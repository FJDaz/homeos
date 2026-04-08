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

SULLIVAN_FEE_SYSTEM = (
    "Tu es Sullivan FEE, expert en animation GSAP, smooth-scroll Lenis et créativité interactive P5.js.\n"
    "Ton rôle est d'étalonner l'expérience utilisateur d'AetherFlow en traduisant des intentions émotionnelles en code.\n\n"
    "CONTEXTE TECHNIQUE :\n"
    "- Sélecteurs : utilise uniquement les [data-af-id=\"...\"] fournis.\n"
    "- Bibliothèque : GSAP 3.x (incluant ScrollTrigger).\n"
    "- Isolation : Ton code sera placé dans un bloc // [FEE-LOGIC] dédié.\n\n"
    "RÈGLES :\n"
    "1. Génère UNIQUEMENT du JavaScript pur.\n"
    "2. Pas de balises <script>, pas d'explicatif long.\n"
    "3. Format de sortie : // [FEE-LOGIC] — {data-af-id} — {state}\n"
    "4. Priorité à la fluidité et à la vibe AetherFlow (Geist, 0px radius, sleek, ALT Casing).\n"
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


# --- BKD Constants ---
BKD_ALLOWED_EXTENSIONS = {
    '.py', '.js', '.ts', '.html', '.css', '.json', '.yaml', '.yml',
    '.toml', '.md', '.txt', '.sh', '.env.example', '.sql', '.jsx', '.tsx'
}
BKD_EXCLUDE_DIRS = {
    '__pycache__', 'node_modules', '.git', '.venv', 'venv', 'env',
    'dist', 'build', '.idea', '.vscode', '__snapshots__'
}

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
    con.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            subject TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            class_id TEXT NOT NULL,
            display TEXT NOT NULL,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            project_id TEXT,
            milestone INTEGER DEFAULT 0,
            FOREIGN KEY (class_id) REFERENCES classes(id)
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'architect',
            title TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            content_json TEXT DEFAULT '[]',
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)
    default_path = str(PROJECTS_DIR / "homéos-default")
    (PROJECTS_DIR / "homéos-default").mkdir(parents=True, exist_ok=True)
    con.execute("INSERT OR IGNORE INTO projects (id, name, path) VALUES (?, ?, ?)",
                ("homéos-default", "homéos default", default_path))
    con.commit()
    con.close()
    
    # Scaffold default project if empty
    scaffold_project(Path(default_path))


def scaffold_project(project_path: Path):
    """Crée l'arborescence HoméOS standard pour un nouveau projet BKD."""
    structure = [
        "1. CONSTITUTION",
        "2. COMMUNICATION",
        "3. BACKEND",
        "4. FRONTEND"
    ]
    for folder in structure:
        (project_path / folder).mkdir(parents=True, exist_ok=True)
    
    # Fichiers de base
    roadmap_content = (
        "# MISSION CONTROL : ROADMAP\n\n"
        "## Thème 1 — Initialisation\n\n"
        "### Mission 1 — Décollage\n"
        "**STATUS: 🟠 PRÊTE**\n"
        "**DATE: " + Path().cwd().name + "**\n\n"
        "Objectif : Configurer l'environnement et valider le premier 'ping' AetherFlow.\n"
    )
    roadmap_path = project_path / "2. COMMUNICATION" / "ROADMAP.md"
    if not roadmap_path.exists():
        roadmap_path.write_text(roadmap_content, encoding="utf-8")
        
    const_content = (
        "# CONSTITUTION DU PROJET\n\n"
        "## Rôles\n"
        "- **Sullivan** : Architecte Backend\n"
        "- **Kimi** : Designer Frontend\n"
        "- **Assistant** : Orchestrateur\n\n"
        "## Règles\n"
        "1. Respect strict du DESIGN.md\n"
        "2. Pas de code non documenté\n"
    )
    const_path = project_path / "1. CONSTITUTION" / "CONSTITUTION.md"
    if not const_path.exists():
        const_path.write_text(const_content, encoding="utf-8")

    # Copie du DESIGN.md global si possible
    global_design = ROOT_DIR / "Frontend/1. CONSTITUTION/DESIGN.md"
    target_design = project_path / "1. CONSTITUTION" / "DESIGN.md"
    if global_design.exists() and not target_design.exists():
        target_design.write_text(global_design.read_text(encoding="utf-8"), encoding="utf-8")


init_bkd_db()


def conv_auto_title(message: str, project_path: Path) -> str:
    """Détecte un ID de mission (M123) ou tronque à 60 chars."""
    import re
    # 1. Recherche pattern Mission (M123, Mission 123)
    match = re.search(r'(M\d+|Mission\s+\d+)', message, re.IGNORECASE)
    if match:
        tag = match.group(0).upper()
        # On essaie de trouver le titre dans la Roadmap
        roadmap_path = project_path / "Frontend/4. COMMUNICATION/ROADMAP.md"
        if not roadmap_path.exists():
            roadmap_path = project_path / "ROADMAP.md"
        if not roadmap_path.exists():
            roadmap_path = Path(str(project_path).replace("/projects/", "/Frontend/2. GENOME/")) / "HOMEO_GENOME.md"

        if roadmap_path.exists():
            try:
                content = roadmap_path.read_text(encoding='utf-8')
                # On cherche la ligne commençant par ### Mission XYZ
                mid = tag.replace("MISSION ", "").replace("M", "")
                rm_match = re.search(fr'### Mission {mid}.*[:—]\s*(.*)', content, re.IGNORECASE)
                if rm_match:
                    return f"M{mid} — {rm_match.group(1).strip()[:50]}"
            except:
                pass
        return tag

    # 2. Fallback: premiers 60 chars
    return message[:60].strip() + ("..." if len(message) > 60 else "")


def bkd_db_con():
    import sqlite3
    return sqlite3.connect(str(BKD_DB_PATH), check_same_thread=False)


# Global State for Active Project — M227: token-aware
_ACTIVE_PROJECT_ID = "homéos-default"

def get_active_project_id(token: str = None):
    """M227: Resolve active project. If token is a student token, return their project_id from DB."""
    if token:
        try:
            with bkd_db_con() as con:
                row = con.execute(
                    "SELECT s.project_id FROM students s "
                    "JOIN users u ON u.name = s.display "
                    "WHERE u.token = ? AND s.project_id IS NOT NULL",
                    (token,)
                ).fetchone()
                if row and row[0]:
                    return row[0]
        except Exception:
            pass
    # Fallback to active_project.json (prof/admin shared state)
    try:
        active_file = ROOT_DIR / "active_project.json"
        if active_file.exists():
            data = json.loads(active_file.read_text(encoding='utf-8'))
            pid = data.get("active_id")
            if pid:
                return pid
    except Exception:
        pass
    return _ACTIVE_PROJECT_ID

def set_active_project_id(pid: str, token: str = None):
    global _ACTIVE_PROJECT_ID
    _ACTIVE_PROJECT_ID = pid
    # If token is a student, update their project_id in DB
    if token:
        try:
            with bkd_db_con() as con:
                con.execute(
                    "UPDATE students SET project_id=? WHERE display = ("
                    "SELECT name FROM users WHERE token=?)",
                    (pid, token)
                )
        except Exception:
            pass
    # Also persist to active_project.json for prof/admin
    try:
        active_file = ROOT_DIR / "active_project.json"
        active_file.parent.mkdir(parents=True, exist_ok=True)
        active_file.write_text(json.dumps({"active_id": pid}, ensure_ascii=False), encoding='utf-8')
    except Exception as e:
        logger.warning(f"set_active_project_id: failed to persist: {e}")

def get_active_project_path(token: str = None) -> Path:
    id = get_active_project_id(token)
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


# --- Conversation History Helpers ---

def conv_create(project_id: str, role: str = "architect", title: str = None) -> str:
    import uuid as _uuid
    cid = str(_uuid.uuid4())
    with bkd_db_con() as con:
        con.execute(
            "INSERT INTO conversations (id, project_id, role, title, content_json) VALUES (?, ?, ?, ?, ?)",
            (cid, project_id, role, title, "[]")
        )
    return cid


def conv_append(conv_id: str, role: str, text: str):
    """Ajoute un turn à la conversation. role = 'user' | 'assistant'."""
    with bkd_db_con() as con:
        row = con.execute("SELECT content_json FROM conversations WHERE id=?", (conv_id,)).fetchone()
        if not row:
            return
        turns = json.loads(row[0])
        turns.append({"role": role, "text": text})
        con.execute(
            "UPDATE conversations SET content_json=?, updated_at=datetime('now') WHERE id=?",
            (json.dumps(turns, ensure_ascii=False), conv_id)
        )


def conv_get(conv_id: str) -> dict | None:
    with bkd_db_con() as con:
        row = con.execute(
            "SELECT id, project_id, role, title, created_at, updated_at, content_json FROM conversations WHERE id=?",
            (conv_id,)
        ).fetchone()
    if not row:
        return None
    return {"id": row[0], "project_id": row[1], "role": row[2], "title": row[3],
            "created_at": row[4], "updated_at": row[5], "turns": json.loads(row[6])}


def get_fee_logic(project_id: str, screen_name: str) -> str:
    """Récupère le contenu de logic/{screen}.js pour le FEE Lab."""
    from bkd_service import resolve_bkd_project_root
    root = resolve_bkd_project_root(project_id)
    if not root: return ""
    
    logic_dir = root / "logic"
    logic_dir.mkdir(exist_ok=True)
    
    file_path = logic_dir / f"{screen_name.replace('.html', '')}.js"
    if file_path.exists():
        return file_path.read_text(encoding="utf-8")
    return "// [FEE-LOGIC] Vide pour " + screen_name


def save_fee_logic(project_id: str, screen_name: str, content: str):
    """Sauvegarde ou patche le bloc // [FEE-LOGIC] dans le fichier écran correspondante."""
    from bkd_service import resolve_bkd_project_root
    root = resolve_bkd_project_root(project_id)
    if not root: return
    
    logic_dir = root / "logic"
    logic_dir.mkdir(exist_ok=True)
    
    file_path = logic_dir / f"{screen_name.replace('.html', '')}.js"
    file_path.write_text(content, encoding="utf-8")


def conv_list(project_id: str, limit: int = 5) -> list:
    with bkd_db_con() as con:
        rows = con.execute(
            "SELECT id, role, title, updated_at FROM conversations WHERE project_id=? ORDER BY updated_at DESC LIMIT ?",
            (project_id, limit)
        ).fetchall()
    return [{"id": r[0], "role": r[1], "title": r[2], "updated_at": r[3]} for r in rows]


def conv_auto_title(conv_id: str):
    """Tente de déduire un titre depuis les premiers turns ou la roadmap (regex M\\d+)."""
    import re
    conv = conv_get(conv_id)
    if not conv or conv.get("title"):
        return
    # 1. Cherche référence mission dans les turns
    all_text = " ".join(t.get("text", "") for t in conv.get("turns", []))
    match = re.search(r'M(\d{3,})', all_text)
    if match:
        title = f"Mission {match.group(1)}"
    elif conv.get("turns"):
        # Fallback : premiers 60 chars du premier message user
        first_user = next((t["text"] for t in conv["turns"] if t.get("role") == "user"), "")
        title = first_user[:60].strip() or "Sans titre"
    else:
        return
    with bkd_db_con() as con:
        con.execute("UPDATE conversations SET title=? WHERE id=?", (title, conv_id))


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
