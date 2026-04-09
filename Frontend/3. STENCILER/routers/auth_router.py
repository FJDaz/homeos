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
from typing import Optional

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
    # Not implemented in sqlite3 fallback — returns None (treated as "not_set")
    return None

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

# --- Wrapper functions that dispatch to Supabase or sqlite3 ---
def _find_student_by_display(name):
    if _USE_SUPABASE:
        return find_student_by_display(name)
    rows = _sqlite_get_students(display_name=name)
    return rows[0] if rows else None

def _find_user_by_name(name):
    if _USE_SUPABASE:
        return find_user_by_name(name)
    return _sqlite_get_user_by_name(name)

def _create_user(user_id, name, role, token):
    if _USE_SUPABASE:
        return create_user(user_id, name, role, token)
    return _sqlite_create_user(user_id, name, role, token)

def _find_user_by_token(token):
    if _USE_SUPABASE:
        return find_user_by_token(token)
    return _sqlite_get_user_by_token(token)

def _find_user_by_name_with_password(name):
    if _USE_SUPABASE:
        return find_user_by_name_with_password(name)
    return _sqlite_get_user_by_name_with_password(name)

def _update_user_password(user_id, password_hash):
    if _USE_SUPABASE:
        return update_user_password(user_id, password_hash)
    return _sqlite_update_user_password(user_id, password_hash)

def _find_student_by_id_and_class(student_id, class_id):
    if _USE_SUPABASE:
        return find_student_by_id_and_class(student_id, class_id)
    rows = _sqlite_get_students(student_id=student_id, class_id=class_id)
    return rows[0] if rows else None

def _get_user_key(user_id, provider):
    if _USE_SUPABASE:
        return get_user_key(user_id, provider)
    return _sqlite_get_user_key(user_id, provider)

def _set_user_key(user_id, provider, api_key):
    if _USE_SUPABASE:
        return set_user_key(user_id, provider, api_key)
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

class MeResponse(BaseModel):
    user_id: str
    name: str
    role: str

class KeyRequest(BaseModel):
    provider: str
    api_key: str

class KeyStatusResponse(BaseModel):
    provider: str
    status: str  # "set" or "not_set"

# --- DB INIT (no-op on Supabase — schema managed via migrations) ---
def init_auth_db():
    """Supabase tables are managed via migrations. No local init needed."""
    pass

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
        return RegisterResponse(
            user_id=existing[0], name=existing[1], role=existing[2], token=existing[3],
            student_id=student_id, class_id=class_id, project_id=project_id
        )

    # Créer nouveau
    user_id = str(uuid.uuid4())
    token = str(uuid.uuid4())
    _create_user(user_id, name, role, token)

    logger.info(f"Auth: new user '{name}' registered (role={role}, student_id={student_id})")
    return RegisterResponse(
        user_id=user_id, name=name, role=role, token=token,
        student_id=student_id, class_id=class_id, project_id=project_id
    )


@router.get("/auth/me")
async def auth_me(request: Request):
    """Retourne les infos de l'utilisateur authentifié."""
    token = request.headers.get("X-User-Token")
    if not token:
        raise HTTPException(status_code=401, detail="X-User-Token header required")

    user = _find_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    return MeResponse(user_id=user[0], name=user[1], role=user[2])


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
