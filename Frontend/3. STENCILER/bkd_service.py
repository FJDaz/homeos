"""
bkd_service.py — Sullivan BKD : prompts, RAG, DB helpers, router.
Partagé par server_9998_v2.py et server_v3.py.
Ne doit dépendre d'aucun des deux serveurs.
"""

import os
import sys
import json
import sqlite3
import urllib.request
from pathlib import Path

# --- Paths ---
_SERVICE_DIR = Path(__file__).parent.resolve()
ROOT_DIR = (_SERVICE_DIR / "../..").resolve()
BACKEND_PROD = ROOT_DIR / "Backend" / "Prod"

for _p in [str(ROOT_DIR), str(BACKEND_PROD)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)


def _load_env():
    env_path = ROOT_DIR / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())


_load_env()

# --- Manifest FRD ---
def _load_manifest_frd() -> str:
    path = ROOT_DIR / "docs/02_Sullivan/Retro_Genome/MANIFEST_FRD.md"
    if path.exists():
        try:
            return path.read_text(encoding="utf-8")
        except Exception:
            return ""
    return ""


MANIFEST_FRD: str = _load_manifest_frd()

# --- Sullivan BKD System Prompt ---
SULLIVAN_BKD_SYSTEM = (
    "Tu es Sullivan BKD, architecte backend et DevOps du projet AetherFlow.\n"
    "Tu assistes le développeur dans la gestion du code backend Python, des API REST, des workflows AetherFlow, et du déploiement.\n\n"
    "CONTEXTE TECHNIQUE :\n"
    "- Stack : Python 3.11+, FastAPI/http.server, LlamaIndex, SQLite, Docker\n"
    "- Agents : Gemini (frontend), Groq (routing), Codestral (code gen), MiMo (wire/diag)\n"
    "- Pipeline AetherFlow : BRS → BKD → FRD → DPL\n"
    "- Éditeur : surgical_editor.py (AST Python), surgical_editor_js.py (acorn Range-Based)\n\n"
    "RÈGLES :\n"
    "1. Tu génères des patches précis (pas de rewrites complets si patch suffisant)\n"
    "2. Tu cites toujours le fichier + la fonction à modifier\n"
    "3. Pour les modifications multi-fichiers, tu listes les fichiers dans l'ordre d'application\n"
    "4. Tu n'inventes pas d'API — tu utilises uniquement les routes documentées\n"
    "5. Tu utilises query_knowledge_base() pour toute question sur l'archi AetherFlow\n\n"
    "FORMAT réponse code : ```python\n# fichier: <path>\n# fonction: <name>\n<code>\n```\n\n"
    "Tu ne génères JAMAIS de HTML/CSS/Tailwind. Si la tâche est frontend, tu le signales."
)

# --- Sullivan Docs (RAG) ---
SULLIVAN_DOCS = [
    str(ROOT_DIR / "docs/02_Sullivan"),
    str(ROOT_DIR / "docs/02-sullivan"),
    str(ROOT_DIR / "docs/04_HomeOS"),
    str(ROOT_DIR / "docs/04-homeos"),
    str(ROOT_DIR / "docs/03_AetherFlow"),
    str(ROOT_DIR / "Frontend/4. COMMUNICATION/ROADMAP.md"),
    str(ROOT_DIR / "Frontend/4. COMMUNICATION/ROADMAP_ACHIEVED.md"),
]


def _init_sullivan_rag():
    try:
        _saved = sys.path.copy()
        sys.path = [p for p in sys.path if not p.endswith("Backend/Prod") and not p.endswith("Backend/_archive")]
        try:
            from Backend.Prod.rag.pageindex_store import PageIndexRetriever
        finally:
            sys.path = _saved
        docs = []
        for p in SULLIVAN_DOCS:
            pp = Path(p)
            if pp.is_dir():
                docs += list(pp.rglob("*.md"))
            elif pp.exists():
                docs.append(pp)
        rag = PageIndexRetriever(document_paths=[str(d) for d in docs])
        if not getattr(rag, "enabled", True):
            print("[RAG] LlamaIndex non disponible — RAG désactivé")
            return None
        print(f"[RAG] Index Sullivan : {len(docs)} documents ✅")
        return rag
    except Exception as e:
        print(f"[RAG] Désactivé : {e}")
        return None


SULLIVAN_RAG = _init_sullivan_rag()


def exec_query_knowledge_base(query: str) -> str:
    if SULLIVAN_RAG is None:
        return "RAG non disponible."
    try:
        import asyncio
        nodes = asyncio.run(SULLIVAN_RAG.retrieve(query))
        if not nodes:
            return "Aucun résultat trouvé dans la base de connaissance."
        chunks = []
        for n in nodes[:4]:
            src = n.get("file_name", "?") if isinstance(n, dict) else getattr(getattr(n, "node", n), "metadata", {}).get("file_name", "?")
            content = n.get("content", "") if isinstance(n, dict) else n.node.get_content()
            chunks.append(f"[{src}]\n{content[:600]}")
        return "\n\n---\n\n".join(chunks)
    except Exception as e:
        return f"Erreur RAG : {e}"


# --- BKD Projects DB ---
BKD_DB_PATH = ROOT_DIR / "db" / "projects.db"
PROJECTS_DIR = ROOT_DIR / "projects"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

def init_bkd_db():
    import sqlite3
    BKD_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(BKD_DB_PATH))
    con.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            path TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            last_opened TEXT DEFAULT (datetime('now'))
        )
    """)
    default_path = str(PROJECTS_DIR / "homéos-default")
    (PROJECTS_DIR / "homéos-default").mkdir(parents=True, exist_ok=True)
    con.execute("INSERT OR IGNORE INTO projects (id, name, path) VALUES (?, ?, ?)",
                ("homéos-default", "homéos default", default_path))
    con.commit()
    con.close()


init_bkd_db()


def bkd_db_con():
    import sqlite3
    return sqlite3.connect(str(BKD_DB_PATH), check_same_thread=False)


# Global State for Active Project
_ACTIVE_PROJECT_ID = "homéos-default"

def get_active_project_id():
    return _ACTIVE_PROJECT_ID

def set_active_project_id(pid: str):
    global _ACTIVE_PROJECT_ID
    _ACTIVE_PROJECT_ID = pid

def get_active_project_path() -> Path:
    id = get_active_project_id()
    con = bkd_db_con()
    row = con.execute("SELECT path FROM projects WHERE id=?", (id,)).fetchone()
    con.close()
    if row: return Path(row[0])
    # Fallback/Auto-init default
    p = PROJECTS_DIR / id
    p.mkdir(parents=True, exist_ok=True)
    return p

def resolve_bkd_project_root(project_id: str):
    con = bkd_db_con()
    row = con.execute("SELECT path FROM projects WHERE id=?", (project_id,)).fetchone()
    con.close()
    return Path(row[0]) if row else None


def bkd_safe_path(project_root: Path, rel_path: str):
    resolved = (project_root / rel_path).resolve()
    try:
        resolved.relative_to(project_root.resolve())
    except ValueError:
        return None
    if resolved.suffix not in BKD_ALLOWED_EXTENSIONS:
        return None
    return resolved


def bkd_build_tree(root, rel="", depth=2, current=0):
    result = []
    try:
        for entry in sorted(Path(root).iterdir(), key=lambda e: (e.is_file(), e.name)):
            if entry.name.startswith(".") and entry.name not in (".env.example",):
                continue
            if entry.name in BKD_EXCLUDE_DIRS:
                continue
            rel_entry = f"{rel}/{entry.name}" if rel else entry.name
            if entry.is_dir():
                node = {"name": entry.name, "path": rel_entry, "type": "dir", "children": []}
                if current < depth:
                    node["children"] = bkd_build_tree(entry, rel_entry, depth, current + 1)
                result.append(node)
            elif entry.is_file() and entry.suffix in BKD_ALLOWED_EXTENSIONS:
                result.append({"name": entry.name, "path": rel_entry, "type": "file", "size": entry.stat().st_size})
    except PermissionError:
        pass
    return result


# --- BKD Router (Groq classifier) ---
def route_request_bkd(message: str, history=None, arbitrator=None) -> dict:
    """Route BKD via Groq. arbitrator requis pour pick() dynamique."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key or arbitrator is None:
        return {"type": "quick", "model": "gemini-2.5-flash", "provider": "gemini"}

    last_model_turn = ""
    if history:
        last_model_turn = next((t.get("text", "") for t in reversed(history) if t.get("role") == "model"), "")

    system = (
        "Tu es un routeur pour Sullivan BKD (assistant backend/devops AetherFlow).\n"
        "Réponds UNIQUEMENT avec un JSON : {\"type\": \"...\", \"reason\": \"...\"}\n\n"
        "Types disponibles :\n"
        "- quick         : question courte, explication archi, doc lookup, conversation\n"
        "- code-simple   : génération ou patch < 100 lignes, fichier unique\n"
        "- code-complex  : multi-fichiers, nouvelle feature, refactoring > 100L\n"
        "- wire          : analyse statique codebase, routes API, diagnostic dépendances\n"
        "- diagnostic    : débogage, stacktrace, investigation erreur\n\n"
        "RÈGLE : si le message est une confirmation d'exécution (\"go\", \"procède\", \"lance\") "
        "ET que le dernier tour contient un plan technique → même type que le plan.\n\n"
        f"DERNIER TOUR SULLIVAN :\n{last_model_turn[:800]}"
    )

    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Message BKD : {message}"},
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
    }
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}", "User-Agent": "AetherFlow-Agent/1.0"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            route_type = json.loads(data["choices"][0]["message"]["content"]).get("type", "quick")
            config = arbitrator.pick(route_type)
            print(f"[BKD] Route: {route_type} → {config['provider']} ({config['model']})")
            return {"type": route_type, "model": config["model"], "provider": config["provider"]}
    except Exception as e:
        print(f"[BKD_ROUTER_ERROR] {e}")
        return {"type": "quick", "model": "gemini-2.5-flash", "provider": "gemini"}
