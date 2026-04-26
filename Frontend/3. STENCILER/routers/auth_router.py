"""
Auth Router — Mission 190
Users table + session token + isolation projets.
"""

import os
import json
import uuid
import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from pydantic import BaseModel

from Backend.Prod.models.gemini_client import GeminiClient
from Backend.Prod.config.settings import settings
from bkd_service import bkd_db
from core.auth_utils import (
    hash_password_bcrypt, verify_password, create_access_token, 
    decode_access_token, send_magic_link_email
)

logger = logging.getLogger("AetherFlowV3")

# Try Supabase for classes/students, but ALWAYS use sqlite3 for users/auth
_USE_SUPABASE = False  # students.user_id n'existe pas sur Supabase — SQLite uniquement
if _USE_SUPABASE:
    try:
        from routers.auth_supabase import (
            find_student_by_display, find_user_by_name, create_user,
            find_user_by_token, list_classes, list_students_by_class,
            update_student, delete_class, create_class,
            find_user_by_id, get_user_key, set_user_key,
            find_student_by_id_and_class, update_user_password,
            find_user_by_name_with_password,
        )
    except Exception as e:
        logger.warning(f"Supabase init failed ({e}), falling back to sqlite3")
        _USE_SUPABASE = False

# For Supabase mode, users/auth ALWAYS stay on sqlite3 (security)
# Only classes/students go through Supabase
_USE_SUPABASE_FOR_USERS = False

router = APIRouter(prefix="/api")

# --- PATHS ---
CWD = Path(__file__).parent.parent.resolve()
ROOT_DIR = CWD.parent.parent
PROJECTS_DB_PATH = ROOT_DIR / "db/projects.db"
PROJECTS_DIR = ROOT_DIR / "projects"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

# --- MODELS ---

# --- SQLite fallback helpers (used when Supabase not available) ---
def _sqlite_get_students(class_id=None, display_name=None, student_id=None):
    """Query students from local sqlite3."""
    with bkd_db() as conn:
        cursor = conn.cursor()
        if display_name:
            rows = cursor.execute(
                "SELECT id, class_id, project_id FROM students WHERE lower(display) = lower(?)",
                (display_name,)
            ).fetchall()
        elif student_id and class_id:
            rows = cursor.execute(
                "SELECT id, display, project_id, class_id FROM students WHERE id = ? AND class_id = ?",
                (student_id, class_id)
            ).fetchall()
        elif class_id:
            rows = cursor.execute(
                "SELECT id, display, project_id FROM students WHERE class_id = ? ORDER BY display",
                (class_id,)
            ).fetchall()
        else:
            rows = []
    return rows

def _sqlite_get_user_by_name(name):
    with bkd_db() as conn:
        cursor = conn.cursor()
        row = cursor.execute("SELECT id, name, role, token FROM users WHERE name = ?", (name,)).fetchone()
    return row

def _sqlite_get_user_by_token(token):
    with bkd_db() as conn:
        cursor = conn.cursor()
        row = cursor.execute("SELECT id, name, role FROM users WHERE token = ?", (token,)).fetchone()
    return row

def _sqlite_get_user_by_name_with_password(name):
    with bkd_db() as conn:
        cursor = conn.cursor()
        row = cursor.execute("SELECT id, name, role, token, password_hash, password_hash_bcrypt FROM users WHERE name = ?", (name,)).fetchone()
    return row

def _sqlite_create_user(user_id, name, role, token):
    with bkd_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (id, name, role, token) VALUES (?, ?, ?, ?)", (user_id, name, role, token))

def _sqlite_update_user_password(user_id, password_hash):
    with bkd_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id))

def _sqlite_update_user_bcrypt(user_id, bcrypt_hash):
    with bkd_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password_hash_bcrypt = ? WHERE id = ?", (bcrypt_hash, user_id))

def _sqlite_get_user_by_email(email):
    with bkd_db() as conn:
        cursor = conn.cursor()
        row = cursor.execute("SELECT id, name, role, token, password_hash, password_hash_bcrypt FROM users WHERE email = ?", (email,)).fetchone()
    return row

def _sqlite_create_session(session_id, code, creator_id, title, expires_at):
    with bkd_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (id, code, creator_id, title, expires_at) VALUES (?, ?, ?, ?, ?)",
            (session_id, code, creator_id, title, expires_at)
        )

def _sqlite_get_session_by_code(code):
    with bkd_db() as conn:
        cursor = conn.cursor()
        row = cursor.execute("SELECT id, creator_id, title, expires_at FROM sessions WHERE code = ?", (code,)).fetchone()
    return row

def _sqlite_add_session_participant(participant_id, session_id, name, email=None):
    with bkd_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO session_participants (id, session_id, name, email) VALUES (?, ?, ?, ?)",
            (participant_id, session_id, name, email)
        )

def _sqlite_get_user_key(user_id, provider):
    with bkd_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT api_key FROM user_keys WHERE user_id = ? AND provider = ?", (user_id, provider))
        row = cursor.fetchone()
    return row[0] if row else None

def _sqlite_set_user_key(user_id, provider, api_key):
    with bkd_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_keys (user_id, provider, api_key) VALUES (?, ?, ?) "
            "ON CONFLICT(user_id, provider) DO UPDATE SET api_key = ?, updated_at = datetime('now')",
            (user_id, provider, api_key, api_key)
        )

def _sqlite_get_student_user_id(student_id, class_id):
    """M298: Lit le user_id d'un étudiant (sqlite3 only)."""
    with bkd_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM students WHERE id = ? AND class_id = ?", (student_id, class_id))
        row = cursor.fetchone()
    return row[0] if row else None

def _sqlite_set_student_user_id(student_id, class_id, user_id):
    """M298: Écrit le lien FK students.user_id = users.id (write once)."""
    with bkd_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET user_id = ? WHERE id = ? AND class_id = ?", (user_id, student_id, class_id))

def _create_workspace(workspace_id: str, name: str, owner_id: str):
    """M283a: Crée un workspace personnel pour un user."""
    with bkd_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO workspaces (id, name, plan, owner_id) VALUES (?, ?, 'FREE', ?)",
            (workspace_id, name, owner_id)
        )

def _get_user_workspace_and_plan(user_id):
    """M283a: Retourne (workspace_id, plan) pour un user."""
    with bkd_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT workspace_id FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        workspace_id = row[0] if row else None
        if not workspace_id:
            workspace_id = f"ws_{user_id}"
            _create_workspace(workspace_id, "Workspace", user_id)
            _link_user_to_workspace(user_id, workspace_id, "owner")
        cursor.execute("SELECT plan FROM workspaces WHERE id = ?", (workspace_id,))
        ws_row = cursor.fetchone()
        plan = ws_row[0] if ws_row else "FREE"
    return workspace_id, plan

def _link_user_to_workspace(user_id: str, workspace_id: str, role_in_workspace: str):
    """M283a: Lie un user à un workspace."""
    with bkd_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO workspace_members (user_id, workspace_id, role_in_workspace) VALUES (?, ?, ?)",
            (user_id, workspace_id, role_in_workspace)
        )
        cursor.execute("UPDATE users SET workspace_id = ? WHERE id = ?", (workspace_id, user_id))

def _get_user_workspace_and_plan(user_id):
    """M283a: Récupère le workspace et plan d'un user."""
    with bkd_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT workspace_id FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        workspace_id = row[0] if row else None
        
        plan = "FREE"
        if workspace_id:
            cursor.execute("SELECT plan FROM workspaces WHERE id = ?", (workspace_id,))
            ws_row = cursor.fetchone()
            if ws_row: plan = ws_row[0]
    
    return workspace_id, plan

# --- Wrapper functions that dispatch to Supabase or sqlite3 ---
def _sqlite_delete_user_key(user_id, provider):
    with bkd_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_keys WHERE user_id = ? AND provider = ?", (user_id, provider))
        deleted = cursor.rowcount > 0
    return deleted
# NOTE: students go through Supabase when available, but users/auth ALWAYS stay on sqlite3

def _find_student_by_display(name):
    if _USE_SUPABASE:
        return find_student_by_display(name)
    rows = _sqlite_get_students(display_name=name)
    return rows[0] if rows else None

def _find_user_by_name(name):
    # Users ALWAYS on sqlite3 — security
    return _sqlite_get_user_by_name(name)

def _create_user(user_id, name, role, token):
    # Users ALWAYS on sqlite3 — security
    return _sqlite_create_user(user_id, name, role, token)

def _find_user_by_token(token):
    # Users ALWAYS on sqlite3 — security
    return _sqlite_get_user_by_token(token)

def _find_user_by_name_with_password(name):
    # Users ALWAYS on sqlite3 — security
    return _sqlite_get_user_by_name_with_password(name)

def _update_user_password(user_id, password_hash):
    # Users ALWAYS on sqlite3 — security
    return _sqlite_update_user_password(user_id, password_hash)

def _find_student_by_id_and_class(student_id, class_id):
    if _USE_SUPABASE:
        return find_student_by_id_and_class(student_id, class_id)
    rows = _sqlite_get_students(student_id=student_id, class_id=class_id)
    return rows[0] if rows else None

def _get_user_key(user_id, provider):
    # Users ALWAYS on sqlite3 — security
    return _sqlite_get_user_key(user_id, provider)

def _set_user_key(user_id, provider, api_key):
    # Users ALWAYS on sqlite3 — security
    return _sqlite_set_user_key(user_id, provider, api_key)

def _list_students_by_class(class_id):
    if _USE_SUPABASE:
        return list_students_by_class(class_id)
    return _sqlite_get_students(class_id=class_id)

def _get_student_user_id(student_id, class_id):
    """M298: Lit le user_id lié à un étudiant (Supabase ou sqlite3)."""
    if _USE_SUPABASE:
        from routers.auth_supabase import _get
        rows = _get("students", select="user_id", filters={"id": student_id, "class_id": class_id})
        if rows and len(rows) > 0:
            return rows[0].get("user_id")
        return None
    return _sqlite_get_student_user_id(student_id, class_id)

def _set_student_user_id(student_id, class_id, user_id):
    """M298: Écrit le lien FK students.user_id = users.id (write once)."""
    if _USE_SUPABASE:
        from routers.auth_supabase import update_student
        update_student(student_id, class_id, {"user_id": user_id})
    else:
        _sqlite_set_student_user_id(student_id, class_id, user_id)
class RegisterRequest(BaseModel):
    name: str

class RegisterResponse(BaseModel):
    user_id: str
    name: str
    role: str
    token: str
    student_id: Optional[str] = None
    class_id: Optional[str] = None
    project_id: Optional[str] = None
    plan: str = "FREE"
    workspace_id: Optional[str] = None
    entitlements: Optional[dict] = None

class MeResponse(BaseModel):
    user_id: str
    name: str
    role: str
    plan: Optional[str] = "FREE"
    workspace_id: Optional[str] = None
    entitlements: Optional[Dict[str, Any]] = None

class KeyRequest(BaseModel):
    provider: str
    api_key: str

class UnifiedLoginRequest(BaseModel):
    # Mode A: Password
    email: Optional[str] = None
    password: Optional[str] = None
    # Mode B: Session Code
    session_code: Optional[str] = None
    name: Optional[str] = None
    # Mode C: Magic Link
    magic_token: Optional[str] = None

class SessionCreateRequest(BaseModel):
    title: str
    duration_hours: int = 8

class MagicLinkRequest(BaseModel):
    email: str

class KeyStatusResponse(BaseModel):
    provider: str
    status: str  # "set" or "not_set"

class ImpersonateRequest(BaseModel):
    student_id: str
    class_id: str

# --- DB INIT (no-op on Supabase — schema managed via migrations) ---
def init_auth_db():
    """Migre le schéma SQLite local pour supporter M283a (RBAC) et M313 (Unified Auth)."""
    if _USE_SUPABASE: return
    
    with bkd_db() as conn:
        cursor = conn.cursor()
        
        # 1. Tables Workspaces
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workspaces (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                plan TEXT DEFAULT 'FREE',
                owner_id TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workspace_members (
                user_id TEXT,
                workspace_id TEXT,
                role_in_workspace TEXT,
                PRIMARY KEY (user_id, workspace_id)
            )
        """)
        
        # 3. Tables Sessions (Mission 313)
        cursor.execute("""
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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_participants (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT,
                joined_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)
        
        # 4. Migration colonnes users (bcrypt, email, active_project)
        cursor.execute("PRAGMA table_info(users)")
        cols = [c[1] for c in cursor.fetchall()]
        if "workspace_id" not in cols:
            cursor.execute("ALTER TABLE users ADD COLUMN workspace_id TEXT")
        if "email" not in cols:
            cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
        if "password_hash_bcrypt" not in cols:
            cursor.execute("ALTER TABLE users ADD COLUMN password_hash_bcrypt TEXT")
        if "active_project_id" not in cols:
            cursor.execute("ALTER TABLE users ADD COLUMN active_project_id TEXT")
        
        logger.info("Auth: local sqlite3 schema ensured.")

# Appeler l'init au chargement
init_auth_db()

# --- SEED ADMIN ---
def seed_admin():
    """Seed le user admin si absent (ADMIN_NAME depuis .env, défaut: FJD)."""
    admin_name = os.getenv("ADMIN_NAME", "FJD")
    existing = _find_user_by_name(admin_name)
    if not existing:
        admin_id = str(uuid.uuid4())
        admin_token = str(uuid.uuid4())
        _create_user(admin_id, admin_name, "admin", admin_token)
        logger.info(f"Auth seed: admin user '{admin_name}' created (id={admin_id[:8]}...)")

# --- ROUTES ---
@router.post("/auth/register")
def auth_register(req: RegisterRequest):
    """Enregistre un utilisateur par nom. Retourne user_id + token + infos étudiant si trouvé."""
    name = req.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Name required")

    admin_name = os.getenv("ADMIN_NAME", "FJD")
    prof_names = [n.strip() for n in os.getenv("PROF_NAMES", "FJD").split(",")]

    if name == admin_name:
        role = "admin"
    elif name in prof_names:
        role = "prof"
    else:
        role = "student"

    # Lookup étudiant via Supabase
    student_info = _find_student_by_display(name)
    student_id = student_info[0] if student_info else None
    class_id = student_info[1] if student_info else None
    project_id = student_info[2] if student_info else None

    # Chercher user existant
    existing = _find_user_by_name(name)
    if existing:
        user_id = existing[0]
        workspace_id, plan = _get_user_workspace_and_plan(user_id)
        resp = RegisterResponse(
            user_id=user_id, name=existing[1], role=existing[2], token=existing[3],
            student_id=student_id, class_id=class_id, project_id=project_id,
            workspace_id=workspace_id, plan=plan
        )
        # M298: Write FK link even for existing users (idempotent backfill)
        if student_id and class_id and resp.role == "student":
            existing_link = _get_student_user_id(student_id, class_id)
            if not existing_link:
                _set_student_user_id(student_id, class_id, user_id)
                logger.info(f"M298: Backfilled student {student_id} → user {user_id}")
    else:
        # Créer nouveau
        user_id = str(uuid.uuid4())
        token = str(uuid.uuid4())
        workspace_id = f"ws_{user_id}"
        
        _create_user(user_id, name, role, token)
        
        # M283a: Create personal workspace
        _create_workspace(workspace_id, f"Workspace {name}", user_id)
        _link_user_to_workspace(user_id, workspace_id, "owner")
        
        resp = RegisterResponse(
            user_id=user_id, name=name, role=role, token=token,
            student_id=student_id, class_id=class_id, project_id=project_id,
            plan="FREE", workspace_id=workspace_id
        )

    # M283a: Resolve entitlements for the response
    from .rbac_middleware import resolve_entitlements
    resp.entitlements = resolve_entitlements(resp.plan, resp.role)

    # M298: Write FK link for students (write once)
    if student_id and class_id and resp.role == "student":
        existing_link = _get_student_user_id(student_id, class_id)
        if not existing_link:
            _set_student_user_id(student_id, class_id, resp.user_id)
            logger.info(f"M298: Linked student {student_id} → user {resp.user_id} (register)")

    # M309: Pure DB project isolation
    if project_id:
        from bkd_service import set_active_project_id
        set_active_project_id(project_id, token=resp.token)
        logger.info(f"Auth: active project set to {project_id} (DB)")

        # M292: Create project directory on disk if missing (for students)
        project_dir = PROJECTS_DIR / project_id
        if not project_dir.exists():
            project_dir.mkdir(parents=True, exist_ok=True)
            # Create default manifest
            default_manifest = {"name": name, "description": "", "archetype": None, "design_tokens": None, "screens": [], "wires": [], "pending_intents": []}
            (project_dir / "manifest.json").write_text(json.dumps(default_manifest, indent=2, ensure_ascii=False), encoding='utf-8')
            logger.info(f"Auth: created project directory for {project_id}")

    logger.info(f"Auth: user '{name}' registered (role={role}, student_id={student_id}, workspace={resp.workspace_id})")
    return resp


@router.post("/auth/login")
def auth_unified_login(req: UnifiedLoginRequest, request: Request):
    """
    Mission 313 : Point d'entrée unique pour l'authentification.
    Supporte : Email/Password (Bcrypt), Code Session, Magic Link.
    """
    # 1. Mode Magic Link
    if req.magic_token:
        payload = decode_access_token(req.magic_token)
        if not payload or payload.get("type") != "magic_link":
            raise HTTPException(status_code=401, detail="Lien magique invalide ou expiré")
        
        email = payload.get("email")
        user = _sqlite_get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
        
        user_id, name, role, token, _, _ = user
        access_token = create_access_token({"user_id": user_id, "role": role})
        return RegisterResponse(user_id=user_id, name=name, role=role, token=access_token)

    # 2. Mode Session Code + Name
    if req.session_code and req.name:
        session = _sqlite_get_session_by_code(req.session_code)
        if not session:
            raise HTTPException(status_code=404, detail="Session non trouvée")
        
        session_id, creator_id, title, expires_at = session
        # Vérif expiration
        if expires_at and datetime.fromisoformat(expires_at) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Session expirée")
        
        participant_id = str(uuid.uuid4())
        _sqlite_add_session_participant(participant_id, session_id, req.name)
        
        access_token = create_access_token({"user_id": participant_id, "role": "apprenant", "session_id": session_id})
        return RegisterResponse(user_id=participant_id, name=req.name, role="apprenant", token=access_token)

    # 3. Mode Email/Password
    if req.email and req.password:
        user = _sqlite_get_user_by_email(req.email)
        if not user:
            # Fallback legacy by name
            user = _find_user_by_name_with_password(req.email)
            if not user:
                raise HTTPException(status_code=401, detail="Identifiants incorrects")
        
        user_id, name, role, token, stored_hash_sha, stored_hash_bcrypt = user[:6]
        
        # Vérification Bcrypt ou SHA-256
        is_valid = False
        if stored_hash_bcrypt:
            is_valid = verify_password(req.password, stored_hash_bcrypt)
        elif stored_hash_sha:
            is_valid = verify_password(req.password, stored_hash_sha)
            # MIGRATION : Si SHA valide, on génère le bcrypt
            if is_valid:
                new_bcrypt_hash = hash_password_bcrypt(req.password)
                _sqlite_update_user_bcrypt(user_id, new_bcrypt_hash)
                logger.info(f"Auth: User {name} migrated to bcrypt successfully.")
        else:
            # Cas Legacy : Pas de mot de passe du tout en base (ex: FJD au début)
            # On autorise la connexion pour permettre de définir le mdp via les paramètres ou simplement accéder
            is_valid = True
            logger.warning(f"Auth: Legacy login without password for user {name}")
        
        if not is_valid:
            raise HTTPException(status_code=401, detail="Identifiants incorrects")
        
        access_token = create_access_token({"user_id": user_id, "role": role})
        return RegisterResponse(user_id=user_id, name=name, role=role, token=access_token)

    raise HTTPException(status_code=400, detail="Mode d'authentification non spécifié ou incomplet")


@router.post("/auth/magic-link")
def auth_request_magic_link(req: MagicLinkRequest, request: Request):
    """Génère un lien magique et l'envoie par email."""
    user = _sqlite_get_user_by_email(req.email)
    if not user:
        # On ne veut pas révéler si l'email existe, mais pour AetherFlow on peut être plus explicite ou discret
        return {"status": "ok", "message": "Si l'adresse existe, un lien a été envoyé."}
    
    magic_token = create_access_token(
        {"email": req.email, "type": "magic_link"}, 
        expires_delta=timedelta(minutes=15)
    )
    
    site_url = str(request.base_url).rstrip("/")
    success = send_magic_link_email(req.email, magic_token, site_url)
    
    if not success:
        return {"status": "error", "message": "Erreur lors de l'envoi de l'email."}
    return {"status": "ok"}


@router.get("/auth/verify")
def auth_verify_magic_token(token: str):
    """
    Handler Magic Link : Valide le token et redirige.
    Mission 137: Sert de point de chute pour les liens envoyés par email.
    """
    payload = decode_access_token(token)
    if not payload or payload.get("type") != "magic_link":
        return HTMLResponse("<h1>Lien invalide ou expiré</h1>", status_code=401)
    
    email = payload.get("email")
    user = _sqlite_get_user_by_email(email)
    if not user:
        return HTMLResponse("<h1>Utilisateur introuvable</h1>", status_code=401)
    
    user_id, name, role, user_token, _, _ = user
    # Redirection vers le frontend avec le token
    target = "/teacher" if role in ("prof", "admin") else "/workspace"
    response = RedirectResponse(url=f"{target}?token={token}") # On passe le token magic link temporaire qui sera converti au me/ login
    return response


@router.post("/sessions/create")
def auth_create_session(req: SessionCreateRequest, request: Request):
    """Crée une nouvelle session de cours (réservé aux formateurs)."""
    token = request.headers.get("X-User-Token")
    if not token:
        raise HTTPException(status_code=401, detail="Token manquant")
    
    user_payload = decode_access_token(token)
    if not user_payload or user_payload.get("role") not in ("prof", "admin"):
        raise HTTPException(status_code=403, detail="Droits insuffisants")
    
    session_id = str(uuid.uuid4())
    # Code aléatoire à 6 chiffres
    import random
    code = f"{random.randint(100000, 999999)}"
    
    expires_at = (datetime.utcnow() + timedelta(hours=req.duration_hours)).isoformat()
    _sqlite_create_session(session_id, code, user_payload["user_id"], req.title, expires_at)
    
    return {"session_id": session_id, "code": code, "expires_at": expires_at}


@router.get("/auth/me")
def auth_me(request: Request):
    """Retourne les infos de l'utilisateur authentifié (M283a : inclut workspace + plan + entitlements)."""
    token = request.headers.get("X-User-Token")
    if not token:
        raise HTTPException(status_code=401, detail="X-User-Token header required")

    user = _find_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    # M283a: Resolve entitlements
    from .rbac_middleware import resolve_entitlements
    user_id = user[0]
    role = user[2]

    # Get workspace info
    with bkd_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT workspace_id FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        workspace_id = row[0] if row else f"ws_{user_id}"
        cursor.execute("SELECT plan FROM workspaces WHERE id = ?", (workspace_id,))
        ws_row = cursor.fetchone()
        ws_plan = ws_row[0] if ws_row else "FREE"

    entitlements = resolve_entitlements(ws_plan, role)

    return MeResponse(
        user_id=user_id, name=user[1], role=role,
        plan=ws_plan, workspace_id=workspace_id, entitlements=entitlements
    )


@router.post("/me/keys")
def save_user_key(request: Request, req: KeyRequest):
    """Sauvegarde une clé API utilisateur (BYOK)."""
    token = request.headers.get("X-User-Token")
    if not token:
        raise HTTPException(status_code=401, detail="X-User-Token header required")

    user = _find_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = user[0]
    _set_user_key(user_id, req.provider, req.api_key)

    logger.info(f"Auth: user {user_id[:8]}... saved key for {req.provider}")
    return {"status": "ok", "provider": req.provider}


@router.get("/me/keys")
def list_user_keys(request: Request):
    """Retourne le statut des clés API (jamais la clé elle-même)."""
    token = request.headers.get("X-User-Token")
    if not token:
        raise HTTPException(status_code=401, detail="X-User-Token header required")

    user = _find_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = user[0]
    all_providers = ["gemini", "groq", "openai", "kimi", "mimo", "deepseek", "qwen", "watson"]
    result = {p: _get_user_key(user_id, p) is not None and "set" or "not_set" for p in all_providers}
    return result


@router.delete("/me/keys/{provider}")
def delete_user_key(provider: str, request: Request):
    """Supprime une clé API pour un provider."""
    token = request.headers.get("X-User-Token")
    if not token:
        raise HTTPException(status_code=401, detail="X-User-Token header required")

    user = _find_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = user[0]
    deleted = _sqlite_delete_user_key(user_id, provider.lower())
    return {"status": "ok", "provider": provider, "deleted": deleted}


@router.get("/me/keys/helper/{provider}")
async def get_key_helper(provider: str):
    """
    Mission 192: Retourne l'URL officielle de création de clé API.
    Utilise le cache actualisé au démarrage du serveur (TTL 24h).
    """
    from routers.api_key_urls import load_cached_urls
    urls = load_cached_urls()
    provider_lower = provider.lower()

    if provider_lower in urls:
        return urls[provider_lower]

    # Fallback: trigger a refresh for this provider
    from routers.api_key_urls import refresh_all_urls
    urls = await refresh_all_urls()
    if provider_lower in urls:
        return urls[provider_lower]
    raise HTTPException(status_code=404, detail=f"Provider '{provider}' URL not found")


# --- M224: PROF PASSWORD + STUDENT LOGIN ---

import hashlib

def _hash_password(password: str) -> str:
    """Hash SHA-256 du mot de passe."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


class ProfRegisterRequest(BaseModel):
    name: str
    password: str

class ProfLoginRequest(BaseModel):
    name: str
    password: str

class StudentLoginRequest(BaseModel):
    class_id: str
    student_id: str


@router.post("/auth/register-prof")
def auth_register_prof(req: ProfRegisterRequest):
    """M224: Inscription prof avec mot de passe (Bcrypt)."""
    name = req.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Name required")

    bcrypt_hash = hash_password_bcrypt(req.password)
    existing = _find_user_by_name(name)
    if existing:
        raise HTTPException(status_code=409, detail="Ce nom est déjà pris")

    user_id = str(uuid.uuid4())
    token = str(uuid.uuid4())
    _create_user(user_id, name, "prof", token)
    _sqlite_update_user_bcrypt(user_id, bcrypt_hash)

    logger.info(f"Auth: new prof '{name}' registered (Bcrypt)")
    return RegisterResponse(user_id=user_id, name=name, role="prof", token=token)

@router.post("/auth/impersonate")
def auth_impersonate(req: ImpersonateRequest, request: Request):
    """M327: Permet à un Admin ou Prof d'obtenir un token étudiant."""
    token = request.headers.get("X-User-Token")
    if not token:
        raise HTTPException(status_code=401, detail="Token manquant")
    
    # 1. Résoudre l'utilisateur demandeur
    user = _find_user_by_token(token)
    if not user:
        # Fallback JWT
        try:
            payload = decode_access_token(token)
            if payload:
                user_id = payload.get("user_id")
                role = payload.get("role")
            else:
                raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
        except:
            raise HTTPException(status_code=401, detail="Token invalide")
    else:
        user_id, _, role = user[:3]

    if role not in ('admin', 'prof'):
        raise HTTPException(status_code=403, detail="Droits insuffisants")

    # 2. Vérification scoping pour les profs
    if role == 'prof':
        with bkd_db() as con:
            row = con.execute("SELECT owner_id FROM classes WHERE id = ?", (req.class_id,)).fetchone()
            if not row or row[0] != user_id:
                raise HTTPException(status_code=403, detail="Vous n'êtes pas le propriétaire de cette classe")

    # 3. Récupérer l'élève
    student = _find_student_by_id_and_class(req.student_id, req.class_id)
    if not student:
        raise HTTPException(status_code=404, detail="Élève non trouvé")
    
    # student = (id, display, project_id, class_id)
    s_id, s_display, s_project_id, s_class_id = student
    
    # 4. Résoudre le user_id de l'élève (pour le token)
    s_user_id = _get_student_user_id(s_id, s_class_id)
    if not s_user_id:
        s_user_id = f"student_{s_id}"

    # 5. Créer le token d'accès
    s_token = create_access_token({"user_id": s_user_id, "role": "student"})
    
    logger.info(f"Auth: Impersonation of student {s_id} by {user_id} ({role})")
    return RegisterResponse(
        user_id=s_user_id,
        name=s_display,
        role="student",
        token=s_token,
        student_id=s_id,
        class_id=s_class_id,
        project_id=s_project_id
    )


@router.post("/auth/login-prof")
def auth_login_prof(req: ProfLoginRequest):
    """M224: Login prof par nom + mot de passe (Bcrypt/Migration)."""
    name = req.name.strip()

    user = _find_user_by_name_with_password(name)
    if not user:
        raise HTTPException(status_code=401, detail="Nom incorrect")

    user_id, db_name, role, token, stored_hash_sha, stored_hash_bcrypt = user[:6]
    if role not in ("prof", "admin"):
        raise HTTPException(status_code=401, detail="Nom incorrect")

    # Vérification avec priorité Bcrypt
    is_valid = False
    if stored_hash_bcrypt:
        is_valid = verify_password(req.password, stored_hash_bcrypt)
    elif stored_hash_sha:
        is_valid = verify_password(req.password, stored_hash_sha)
        if is_valid:
            # Migration auto
            new_bcrypt_hash = hash_password_bcrypt(req.password)
            _sqlite_update_user_bcrypt(user_id, new_bcrypt_hash)
            logger.info(f"Auth: Legacy user {name} migrated to Bcrypt.")
    else:
        # Aucun hash (vieux compte sans mdp) -> on force la création d'un mdp ?
        # Pour l'instant on garde la logique legacy : si pas de hash on laisse passer
        is_valid = True

    if not is_valid:
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")

    return RegisterResponse(user_id=user_id, name=db_name, role=role, token=token)


@router.post("/auth/login-student")
def auth_login_student(req: StudentLoginRequest):
    """M224: Login élève sans mot de passe — par classe + student_id.
    M298: Écrit le lien FK students.user_id (write once)."""
    student = _find_student_by_id_and_class(req.student_id, req.class_id)
    if not student:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé dans cette classe")

    student_id, display, project_id, _ = student

    # Créer ou récupérer user
    user = _find_user_by_name(display)
    if user:
        user_id, _, _, token = user
    else:
        user_id = str(uuid.uuid4())
        token = str(uuid.uuid4())
        _create_user(user_id, display, "student", token)

    # M298: Write FK link if not already set (write once)
    existing_link = _get_student_user_id(student_id, req.class_id)
    if not existing_link:
        _set_student_user_id(student_id, req.class_id, user_id)
        logger.info(f"M298: Linked student {student_id} → user {user_id}")

    # M309: Pure DB project isolation
    if project_id:
        from bkd_service import set_active_project_id
        set_active_project_id(project_id, token=token)

    logger.info(f"Auth: student '{display}' logged in (class={req.class_id}, user_id={user_id[:8]}...)")
    return RegisterResponse(
        user_id=user_id, name=display, role="student", token=token,
        student_id=student_id, class_id=req.class_id, project_id=project_id
    )


@router.get("/classes/{class_id}/students-list")
def list_students_public(class_id: str):
    """M224: Liste publique des élèves d'une classe (sans auth)."""
    students = _list_students_by_class(class_id)
    result = []
    for s in students:
        if isinstance(s, dict):
            result.append({"id": s["id"], "display": s.get("display", s["id"]), "project_id": s.get("project_id")})
        else:
            # tuple: (id, display, project_id)
            result.append({"id": s[0], "display": s[1] if len(s) > 1 else s[0], "project_id": s[2] if len(s) > 2 else None})
    return {"students": result}
