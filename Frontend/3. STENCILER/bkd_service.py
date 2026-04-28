"""
bkd_service.py — Sullivan BKD : prompts, RAG, DB helpers, router.
Partagé par server_9998_v2.py et server_v3.py.
Ne doit dépendre d'aucun des deux serveurs.
"""

import os
import sys
import json
import sqlite3, asyncio, logging, subprocess, shutil, contextlib, fcntl, urllib.request
from datetime import datetime
from pathlib import Path

# --- Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BKD")

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
        from Backend.Prod.core.async_utils import safe_run
        nodes = safe_run(SULLIVAN_RAG.retrieve(query))
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

@contextlib.contextmanager
def bkd_db(db_path: Path = None):
    target_db = db_path or BKD_DB_PATH
    con = sqlite3.connect(str(target_db), check_same_thread=False)
    try:
        with con: # Mission 303: Transaction (commit/rollback)
            yield con
    finally:
        con.close()

def init_bkd_db():
    BKD_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with bkd_db() as con:
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=NORMAL")
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
                user_id TEXT,
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
        # --- M307: Centralized auth & infra tables ---
        con.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                role TEXT DEFAULT 'student',
                token TEXT NOT NULL UNIQUE,
                password_hash TEXT,
                workspace_id TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                code TEXT NOT NULL UNIQUE,
                creator_id TEXT NOT NULL,
                title TEXT,
                expires_at TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (creator_id) REFERENCES users(id)
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS session_participants (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT,
                joined_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)
        
        # Mission 313: Migration colonnes users
        cursor = con.cursor()
        cursor.execute("PRAGMA table_info(users)")
        cols = [c[1] for c in cursor.fetchall()]
        if "email" not in cols:
            con.execute("ALTER TABLE users ADD COLUMN email TEXT")
        if "password_hash_bcrypt" not in cols:
            con.execute("ALTER TABLE users ADD COLUMN password_hash_bcrypt TEXT")
        if "active_project_id" not in cols:
            con.execute("ALTER TABLE users ADD COLUMN active_project_id TEXT")

        con.execute("""
            CREATE TABLE IF NOT EXISTS user_keys (
                user_id TEXT NOT NULL,
                provider TEXT NOT NULL,
                api_key TEXT NOT NULL,
                updated_at TEXT DEFAULT (datetime('now')),
                PRIMARY KEY (user_id, provider)
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS workspaces (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                plan TEXT DEFAULT 'FREE',
                owner_id TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS workspace_members (
                user_id TEXT,
                workspace_id TEXT,
                role_in_workspace TEXT,
                PRIMARY KEY (user_id, workspace_id)
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                referential_json TEXT DEFAULT '[]',
                criteria_json TEXT DEFAULT '[]',
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)

        # Mission 316: Migration DB pour séparation projects.type + subject_id
        cursor = con.cursor()
        
        # 1. Projects cols
        cursor.execute("PRAGMA table_info(projects)")
        p_cols = [c[1] for c in cursor.fetchall()]
        if "type" not in p_cols:
            con.execute("ALTER TABLE projects ADD COLUMN type TEXT DEFAULT 'personal'")
        if "subject_id" not in p_cols:
            con.execute("ALTER TABLE projects ADD COLUMN subject_id TEXT")
        
        # 2. Subjects cols
        cursor.execute("PRAGMA table_info(subjects)")
        sb_cols = [c[1] for c in cursor.fetchall()]
        if "class_id" not in sb_cols:
            con.execute("ALTER TABLE subjects ADD COLUMN class_id TEXT")
        
        # 3. Students cols
        cursor.execute("PRAGMA table_info(students)")
        st_cols = [c[1] for c in cursor.fetchall()]
        if "subject_id" not in st_cols:
            con.execute("ALTER TABLE students ADD COLUMN subject_id TEXT")
        
        # Mission 326: Migration classes.owner_id
        cursor.execute("PRAGMA table_info(classes)")
        cl_cols = [c[1] for c in cursor.fetchall()]
        if "owner_id" not in cl_cols:
            con.execute("ALTER TABLE classes ADD COLUMN owner_id TEXT")
            # Backfill initial aux classes sans propriétaire
            admin_name = os.getenv("ADMIN_NAME", "FJD")
            con.execute("""
                UPDATE classes SET owner_id = (SELECT id FROM users WHERE name = ?)
                WHERE owner_id IS NULL
            """, (admin_name,))
            logger.info(f"BKD Migration M326: 'owner_id' added to classes and backfilled to {admin_name}")
        
        # 4. Migration des données existantes (élèves -> subject)
        con.execute("""
            UPDATE projects SET type = 'subject'
            WHERE id IN (SELECT project_id FROM students WHERE project_id IS NOT NULL)
        """)
        logger.info("BKD Migration M316: DB structured and student projects migrated to 'subject' type.")

        default_path = str(PROJECTS_DIR / "homéos-default")
        (PROJECTS_DIR / "homéos-default").mkdir(parents=True, exist_ok=True)
        con.execute("INSERT OR IGNORE INTO projects (id, name, path, type) VALUES (?, ?, ?, 'personal')",
                    ("homéos-default", "homéos default", default_path))
    
    # Scaffold default project if empty
    scaffold_project(Path(default_path))

def get_user_role(user_id: str) -> str | None:
    """Lit le rôle d'un utilisateur par son ID (utilisé pour les permissions)."""
    with bkd_db() as con:
        row = con.execute("SELECT role FROM users WHERE id = ?", (user_id,)).fetchone()
    return row[0] if row else None


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


# --- End DB Helpers ---


def _write_json_locked(file_path: Path, data: dict):
    """Writes JSON with explicit file locking (Mission 303)."""
    with open(file_path, 'w', encoding='utf-8') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        json.dump(data, f, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
        fcntl.flock(f, fcntl.LOCK_UN)


# Global State for Active Project — M309: Pure DB persistence

def get_active_project_id(token: str = None):
    """M309/M337: Resolve active project with Role Isolation and JWT support."""
    if token:
        try:
            with bkd_db() as con:
                # 1. Tentative lookup DB (tokens UUID legacy)
                row = con.execute(
                    "SELECT s.project_id, u.role, u.active_project_id FROM users u "
                    "LEFT JOIN students s ON s.display = u.name "
                    "WHERE u.token = ?",
                    (token,)
                ).fetchone()
                
                if row:
                    stud_pid, role, user_pid = row
                    if role == 'student' and stud_pid:
                        return stud_pid
                    if role in ('teacher', 'admin', 'prof') and user_pid:
                        return user_pid
        except Exception as e:
            logger.error(f"get_active_project_id: DB error: {e}")

        # 2. Fallback JWT — token non stocké en DB (impersonation)
        if token.startswith('eyJ'):
            try:
                from core.auth_utils import decode_access_token
                payload = decode_access_token(token)
                if payload:
                    user_id = payload.get('user_id', '')
                    role = payload.get('role', '')
                    with bkd_db() as con:
                        if role == 'student':
                            # user_id peut être "student_<slug>" ou un vrai UUID
                            row = con.execute(
                                "SELECT project_id FROM students WHERE user_id = ?",
                                (user_id,)
                            ).fetchone()
                            if row and row[0]:
                                return row[0]
                            # Fallback: user_id = "student_<id>" — lookup by students.id
                            if user_id.startswith('student_'):
                                s_id = user_id[len('student_'):]
                                row = con.execute(
                                    "SELECT project_id FROM students WHERE id = ?",
                                    (s_id,)
                                ).fetchone()
                                if row and row[0]:
                                    return row[0]
                        
                        # Si prof JWT — chercher active_project_id dans users
                        row = con.execute(
                            "SELECT active_project_id FROM users WHERE id = ?",
                            (user_id,)
                        ).fetchone()
                        if row and row[0]:
                            return row[0]
            except Exception as e:
                logger.error(f"get_active_project_id: JWT decode error: {e}")

    return "homéos-default"

def set_active_project_id(pid: str, token: str = None):
    """M309: Persist active project with Role Isolation.
    Students: update only their private project_id in DB.
    Teachers: update their active_project_id in DB.
    """
    if token:
        try:
            with bkd_db() as con:
                # 1. Check role
                row = con.execute("SELECT role, name FROM users WHERE token=?", (token,)).fetchone()
                if not row: return
                role, name = row

                # 2. Update based on role
                if role == 'student':
                    con.execute("UPDATE students SET project_id=? WHERE display=?", (pid, name))
                    logger.info(f"set_active_project_id: Student {name} project updated to {pid}")
                else:
                    con.execute("UPDATE users SET active_project_id=? WHERE token=?", (pid, token))
                    logger.info(f"set_active_project_id: User {name} ({role}) active project updated to {pid}")
        except Exception as e:
            logger.error(f"set_active_project_id: DB error: {e}")

def get_active_project_path(token: str = None) -> Path:
    id = get_active_project_id(token)
    with bkd_db() as con:
        row = con.execute("SELECT path FROM projects WHERE id=?", (id,)).fetchone()
    if row: return Path(row[0])
    # Fallback/Auto-init default
    p = PROJECTS_DIR / id
    p.mkdir(parents=True, exist_ok=True)
    return p

def resolve_bkd_project_root(project_id: str, token: str = None):
    """M309: Resolve project root. If project_id == 'active', use token-aware active project."""
    if project_id == "active":
        project_id = get_active_project_id(token)
    
    with bkd_db() as con:
        row = con.execute("SELECT path FROM projects WHERE id=?", (project_id,)).fetchone()
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


# --- Subjects Helpers (M322) ---

def list_subjects(class_id: str = None) -> list:
    with bkd_db() as con:
        if class_id:
            rows = con.execute("SELECT id, name, description, created_at FROM subjects WHERE class_id=?", (class_id,)).fetchall()
        else:
            rows = con.execute("SELECT id, name, description, created_at FROM subjects").fetchall()
    return [{"id": r[0], "name": r[1], "description": r[2], "created_at": r[3]} for r in rows]

def get_subject(subject_id: str) -> dict | None:
    with bkd_db() as con:
        row = con.execute("SELECT id, name, description, referential_json, criteria_json, class_id FROM subjects WHERE id=?", (subject_id,)).fetchone()
    if not row: return None
    return {
        "id": row[0],
        "name": row[1],
        "description": row[2],
        "referential": json.loads(row[3]),
        "criteria": json.loads(row[4]),
        "class_id": row[5]
    }

def save_subject(data: dict) -> str:
    sid = data.get("id") or f"sj_{int(datetime.now().timestamp())}"
    referential = json.dumps(data.get("referential", []), ensure_ascii=False)
    criteria = json.dumps(data.get("criteria", []), ensure_ascii=False)
    with bkd_db() as con:
        con.execute("""
            INSERT OR REPLACE INTO subjects (id, name, description, referential_json, criteria_json, class_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (sid, data["name"], data.get("description", ""), referential, criteria, data.get("class_id")))
    return sid

def delete_subject(subject_id: str):
    with bkd_db() as con:
        con.execute("DELETE FROM subjects WHERE id=?", (subject_id,))

# --- Conversation History Helpers ---

def conv_create(project_id: str, role: str = "architect", title: str = None) -> str:
    import uuid as _uuid
    cid = str(_uuid.uuid4())
    with bkd_db() as con:
        con.execute(
            "INSERT INTO conversations (id, project_id, role, title, content_json) VALUES (?, ?, ?, ?, ?)",
            (cid, project_id, role, title, "[]")
        )
    return cid


def conv_append(conv_id: str, role: str, text: str):
    """Ajoute un turn à la conversation. role = 'user' | 'assistant'."""
    with bkd_db() as con:
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
    with bkd_db() as con:
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
    root = resolve_bkd_project_root(project_id)
    if not root: return
    
    logic_dir = root / "logic"
    logic_dir.mkdir(exist_ok=True)
    
    file_path = logic_dir / f"{screen_name.replace('.html', '')}.js"
    file_path.write_text(content, encoding="utf-8")


def conv_list(project_id: str, limit: int = 5) -> list:
    with bkd_db() as con:
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
    with bkd_db() as con:
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
