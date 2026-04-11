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
from datetime import datetime
from typing import Optional, Dict, Any
import requests

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from Backend.Prod.models.gemini_client import GeminiClient
from Backend.Prod.config.settings import settings

logger = logging.getLogger("AetherFlowV3")

# Try Supabase for classes/students, but ALWAYS use sqlite3 for users/auth
_USE_SUPABASE = bool(os.getenv("SUPABASE_KEY", ""))
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
ACTIVE_PROJECT_FILE = ROOT_DIR / "active_project.json"

# --- MODELS ---

# --- SQLite fallback helpers (used when Supabase not available) ---
def _sqlite_get_students(class_id=None, display_name=None, student_id=None):
    """Query students from local sqlite3."""
    conn = sqlite3.connect(str(PROJECTS_DB_PATH))
    cursor = conn.cursor()
    if display_name:
        rows = cursor.execute(
            "SELECT id, class_id, project_id FROM students WHERE lower(display) = lower(?)",
            (display_name,)
        ).fetchall()
    elif student_id and class_id:
        rows = cursor.execute(
            "SELECT id, display, project_id FROM students WHERE id = ? AND class_id = ?",
            (student_id, class_id)
        ).fetchall()
    elif class_id:
        rows = cursor.execute(
            "SELECT id, display, project_id FROM students WHERE class_id = ? ORDER BY display",
            (class_id,)
        ).fetchall()
    else:
        rows = []
    conn.close()
    return rows

def _sqlite_get_user_by_name(name):
    conn = sqlite3.connect(str(PROJECTS_DB_PATH))
    cursor = conn.cursor()
    row = cursor.execute("SELECT id, name, role, token FROM users WHERE name = ?", (name,)).fetchone()
    conn.close()
    return row

def _sqlite_get_user_by_token(token):
    conn = sqlite3.connect(str(PROJECTS_DB_PATH))
    cursor = conn.cursor()
    row = cursor.execute("SELECT id, name, role FROM users WHERE token = ?", (token,)).fetchone()
    conn.close()
    return row

def _sqlite_get_user_by_name_with_password(name):
    conn = sqlite3.connect(str(PROJECTS_DB_PATH))
    cursor = conn.cursor()
    row = cursor.execute("SELECT id, name, role, token, password_hash FROM users WHERE name = ?", (name,)).fetchone()
    conn.close()
    return row

def _sqlite_create_user(user_id, name, role, token):
    conn = sqlite3.connect(str(PROJECTS_DB_PATH))
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (id, name, role, token) VALUES (?, ?, ?, ?)", (user_id, name, role, token))
    conn.commit()
    conn.close()

def _sqlite_update_user_password(user_id, password_hash):
    conn = sqlite3.connect(str(PROJECTS_DB_PATH))
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id))
    conn.commit()
    conn.close()

def _sqlite_get_user_key(user_id, provider):
    conn = sqlite3.connect(str(PROJECTS_DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT api_key FROM user_keys WHERE user_id = ? AND provider = ?", (user_id, provider))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def _sqlite_set_user_key(user_id, provider, api_key):
    conn = sqlite3.connect(str(PROJECTS_DB_PATH))
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_keys (user_id, provider, api_key) VALUES (?, ?, ?) "
        "ON CONFLICT(user_id, provider) DO UPDATE SET api_key = ?, updated_at = datetime('now')",
        (user_id, provider, api_key, api_key)
    )
    conn.commit()
    conn.close()

def _create_workspace(workspace_id: str, name: str, owner_id: str):
    """M283a: Crée un workspace personnel pour un user."""
    conn = sqlite3.connect(str(PROJECTS_DB_PATH))
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO workspaces (id, name, plan, owner_id) VALUES (?, ?, 'FREE', ?)",
        (workspace_id, name, owner_id)
    )
    conn.commit()
    conn.close()

def _get_user_workspace_and_plan(user_id):
    """M283a: Retourne (workspace_id, plan) pour un user."""
    conn = sqlite3.connect(str(PROJECTS_DB_PATH))
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
    conn.close()
    return workspace_id, plan

def _link_user_to_workspace(user_id: str, workspace_id: str, role_in_workspace: str):
    """M283a: Lie un user à un workspace."""
    conn = sqlite3.connect(str(PROJECTS_DB_PATH))
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO workspace_members (user_id, workspace_id, role_in_workspace) VALUES (?, ?, ?)",
        (user_id, workspace_id, role_in_workspace)
    )
    cursor.execute("UPDATE users SET workspace_id = ? WHERE id = ?", (workspace_id, user_id))
    conn.commit()
    conn.close()

def _get_user_workspace_and_plan(user_id):
    """M283a: Récupère le workspace et plan d'un user."""
    conn = sqlite3.connect(str(PROJECTS_DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT workspace_id FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    workspace_id = row[0] if row else None
    
    plan = "FREE"
    if workspace_id:
        cursor.execute("SELECT plan FROM workspaces WHERE id = ?", (workspace_id,))
        ws_row = cursor.fetchone()
        if ws_row: plan = ws_row[0]
    
    conn.close()
    return workspace_id, plan

# --- Wrapper functions that dispatch to Supabase or sqlite3 ---
def _sqlite_delete_user_key(user_id, provider):
    conn = sqlite3.connect(str(PROJECTS_DB_PATH))
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_keys WHERE user_id = ? AND provider = ?", (user_id, provider))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
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

class KeyStatusResponse(BaseModel):
    provider: str
    status: str  # "set" or "not_set"

# --- DB INIT (no-op on Supabase — schema managed via migrations) ---
def init_auth_db():
    """Migre le schéma SQLite local pour supporter M283a (RBAC)."""
    if _USE_SUPABASE: return
    
    conn = sqlite3.connect(str(PROJECTS_DB_PATH))
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
    
    # 2. Migration colonnes users
    cursor.execute("PRAGMA table_info(users)")
    cols = [c[1] for c in cursor.fetchall()]
    if "workspace_id" not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN workspace_id TEXT")
        logger.info("Migration: added workspace_id to users")
    
    conn.commit()
    conn.close()

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
async def auth_register(req: RegisterRequest):
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

    # M277: Update active_project.json so server-side code points to the right project
    if project_id:
        active_file = ACTIVE_PROJECT_FILE
        active_file.parent.mkdir(parents=True, exist_ok=True)
        active_file.write_text(json.dumps({"active_id": project_id}, ensure_ascii=False), encoding='utf-8')
        logger.info(f"Auth: active_project.json → {project_id}")

    logger.info(f"Auth: user '{name}' registered (role={role}, student_id={student_id}, workspace={resp.workspace_id})")
    return resp


@router.get("/auth/me")
async def auth_me(request: Request):
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
    conn = sqlite3.connect(str(PROJECTS_DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT workspace_id FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    workspace_id = row[0] if row else f"ws_{user_id}"
    cursor.execute("SELECT plan FROM workspaces WHERE id = ?", (workspace_id,))
    ws_row = cursor.fetchone()
    ws_plan = ws_row[0] if ws_row else "FREE"
    conn.close()

    entitlements = resolve_entitlements(ws_plan, role)

    return MeResponse(
        user_id=user_id, name=user[1], role=role,
        plan=ws_plan, workspace_id=workspace_id, entitlements=entitlements
    )


@router.post("/me/keys")
async def save_user_key(request: Request, req: KeyRequest):
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
async def list_user_keys(request: Request):
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
async def delete_user_key(provider: str, request: Request):
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
async def auth_register_prof(req: ProfRegisterRequest):
    """M224: Inscription prof avec mot de passe."""
    name = req.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Name required")

    password_hash = _hash_password(req.password)
    existing = _find_user_by_name(name)
    if existing:
        raise HTTPException(status_code=409, detail="Ce nom est déjà pris")

    user_id = str(uuid.uuid4())
    token = str(uuid.uuid4())
    _create_user(user_id, name, "prof", token)
    _update_user_password(user_id, password_hash)

    logger.info(f"Auth: new prof '{name}' registered")
    return RegisterResponse(user_id=user_id, name=name, role="prof", token=token)


@router.post("/auth/login-prof")
async def auth_login_prof(req: ProfLoginRequest):
    """M224: Login prof par nom + mot de passe."""
    name = req.name.strip()
    password_hash = _hash_password(req.password)

    user = _find_user_by_name_with_password(name)
    if not user:
        raise HTTPException(status_code=401, detail="Nom incorrect")

    user_id, db_name, role, token, stored_hash = user
    if role not in ("prof", "admin"):
        raise HTTPException(status_code=401, detail="Nom incorrect")

    # Si pas de hash (ancien compte), on accepte sans mdp pour rétrocompatibilité
    if stored_hash and stored_hash != password_hash:
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")

    return RegisterResponse(user_id=user_id, name=db_name, role=role, token=token)


@router.post("/auth/login-student")
async def auth_login_student(req: StudentLoginRequest):
    """M224: Login élève sans mot de passe — par classe + student_id."""
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

    # F1: Activer le projet de l'élève immédiatement
    if project_id:
        active_file = ROOT_DIR / "active_project.json"
        active_file.parent.mkdir(parents=True, exist_ok=True)
        active_file.write_text(json.dumps({"active_id": project_id}, ensure_ascii=False), encoding='utf-8')

    logger.info(f"Auth: student '{display}' logged in (class={req.class_id})")
    return RegisterResponse(
        user_id=user_id, name=display, role="student", token=token,
        student_id=student_id, class_id=req.class_id, project_id=project_id
    )


@router.get("/classes/{class_id}/students-list")
async def list_students_public(class_id: str):
    """M224: Liste publique des élèves d'une classe (sans auth)."""
    students = _list_students_by_class(class_id)
    return {
        "students": [
            {"id": s["id"], "display": s.get("display", s["id"]), "project_id": s.get("project_id")}
            for s in students
        ]
    }
