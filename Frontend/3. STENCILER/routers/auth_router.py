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

router = APIRouter(prefix="/api")

# --- PATHS ---
CWD = Path(__file__).parent.parent.resolve()
ROOT_DIR = CWD.parent.parent
PROJECTS_DB_PATH = ROOT_DIR / "db/projects.db"

# --- MODELS ---
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

# --- DB INIT ---
def init_auth_db():
    """Crée les tables users et user_keys, ajoute user_id à projects si absent. M224: ajoute password_hash."""
    conn = sqlite3.connect(str(PROJECTS_DB_PATH))
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            role TEXT DEFAULT 'student',
            token TEXT NOT NULL UNIQUE,
            created_at TEXT DEFAULT (datetime('now'))
        )
    ''')

    # M224: Ajouter password_hash si absent
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN password_hash TEXT')
        logger.info("Auth migration M224: added password_hash to users")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # User keys table (BYOK)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_keys (
            user_id TEXT NOT NULL,
            provider TEXT NOT NULL,
            api_key TEXT NOT NULL,
            updated_at TEXT DEFAULT (datetime('now')),
            PRIMARY KEY (user_id, provider)
        )
    ''')

    # Add user_id column to projects (safe migration)
    try:
        cursor.execute('ALTER TABLE projects ADD COLUMN user_id TEXT REFERENCES users(id)')
        logger.info("Auth migration: added user_id to projects")
    except sqlite3.OperationalError:
        pass  # Column already exists

    conn.commit()
    conn.close()

# --- SEED ADMIN ---
def seed_admin():
    """Seed le user admin si absent (ADMIN_NAME depuis .env, défaut: FJD)."""
    admin_name = os.getenv("ADMIN_NAME", "FJD")
    conn = sqlite3.connect(str(PROJECTS_DB_PATH))
    cursor = conn.cursor()
    existing = cursor.execute("SELECT id FROM users WHERE name = ?", (admin_name,)).fetchone()
    if not existing:
        admin_id = str(uuid.uuid4())
        admin_token = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO users (id, name, role, token) VALUES (?, ?, 'admin', ?)",
            (admin_id, admin_name, admin_token)
        )
        conn.commit()
        logger.info(f"Auth seed: admin user '{admin_name}' created (id={admin_id[:8]}...)")
    conn.close()

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

    conn = sqlite3.connect(str(PROJECTS_DB_PATH))
    cursor = conn.cursor()

    # R6-A: Lookup étudiant dans la table students
    student_row = cursor.execute(
        "SELECT id, class_id, project_id FROM students WHERE lower(display) = lower(?)",
        (name,)
    ).fetchone()

    student_id = student_row[0] if student_row else None
    class_id = student_row[1] if student_row else None
    project_id = student_row[2] if student_row else None

    # Chercher par name dans users
    existing = cursor.execute("SELECT id, name, role, token FROM users WHERE name = ?", (name,)).fetchone()
    if existing:
        conn.close()
        return RegisterResponse(
            user_id=existing[0], name=existing[1], role=existing[2], token=existing[3],
            student_id=student_id, class_id=class_id, project_id=project_id
        )

    # Créer nouveau
    user_id = str(uuid.uuid4())
    token = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO users (id, name, role, token) VALUES (?, ?, ?, ?)",
        (user_id, name, role, token)
    )
    conn.commit()
    conn.close()

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

    conn = sqlite3.connect(str(PROJECTS_DB_PATH))
    cursor = conn.cursor()
    user = cursor.execute("SELECT id, name, role FROM users WHERE token = ?", (token,)).fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    return MeResponse(user_id=user[0], name=user[1], role=user[2])


@router.post("/me/keys")
async def save_user_key(request: Request, req: KeyRequest):
    """Sauvegarde une clé API utilisateur (BYOK)."""
    token = request.headers.get("X-User-Token")
    if not token:
        raise HTTPException(status_code=401, detail="X-User-Token header required")

    conn = sqlite3.connect(str(PROJECTS_DB_PATH))
    cursor = conn.cursor()
    user = cursor.execute("SELECT id FROM users WHERE token = ?", (token,)).fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = user[0]
    cursor.execute(
        "INSERT INTO user_keys (user_id, provider, api_key) VALUES (?, ?, ?) "
        "ON CONFLICT(user_id, provider) DO UPDATE SET api_key = ?, updated_at = datetime('now')",
        (user_id, req.provider, req.api_key, req.api_key)
    )
    conn.commit()
    conn.close()

    logger.info(f"Auth: user {user_id[:8]}... saved key for {req.provider}")
    return {"status": "ok", "provider": req.provider}


@router.get("/me/keys")
async def list_user_keys(request: Request):
    """Retourne le statut des clés API (jamais la clé elle-même)."""
    token = request.headers.get("X-User-Token")
    if not token:
        raise HTTPException(status_code=401, detail="X-User-Token header required")

    conn = sqlite3.connect(str(PROJECTS_DB_PATH))
    cursor = conn.cursor()
    user = cursor.execute("SELECT id FROM users WHERE token = ?", (token,)).fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = user[0]
    keys = cursor.execute(
        "SELECT provider FROM user_keys WHERE user_id = ?", (user_id,)
    ).fetchall()
    conn.close()

    saved_providers = {k[0] for k in keys}
    all_providers = ["gemini", "groq", "openai", "mimo", "qwen"]
    result = {p: ("set" if p in saved_providers else "not_set") for p in all_providers}
    return result


@router.get("/me/keys/helper/{provider}")
async def get_key_helper(provider: str, request: Request):
    """
    Mission 192: Sullivan GPS. 
    Trouve l'URL officielle et les instructions de création via Gemini + Google Search.
    """
    token = request.headers.get("X-User-Token")
    if not token:
        raise HTTPException(status_code=401, detail="X-User-Token header required")

    try:
        gemini = GeminiClient()
        prompt = (
            f"Recherche l'URL officielle et directe du tableau de bord de création de clé API pour le fournisseur '{provider}'.\n"
            "Réponds avec UNIQUEMENT un objet JSON :\n"
            "{\n"
            "  \"url\": \"https://...\",\n"
            "  \"instructions\": \"Courte instruction (max 15 mots), sans prose.\"\n"
            "}"
        )
        
        result = await gemini.generate(
            prompt=prompt,
            output_constraint="JSON only",
            use_search=True # Enable Google Search Grounding
        )
        
        if not result.success:
            logger.error(f"Sullivan GPS result error: {result.error}")
            raise HTTPException(status_code=500, detail=f"Sullivan GPS search failed: {result.error}")
            
        import json
        return json.loads(result.code.strip())
    except Exception as e:
        logger.error(f"Sullivan GPS Exception: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


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
    conn = sqlite3.connect(str(PROJECTS_DB_PATH))
    cursor = conn.cursor()

    # Vérifier si existe déjà
    existing = cursor.execute("SELECT id FROM users WHERE name = ?", (name,)).fetchone()
    if existing:
        conn.close()
        raise HTTPException(status_code=409, detail="Ce nom est déjà pris")

    user_id = str(uuid.uuid4())
    token = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO users (id, name, role, token, password_hash) VALUES (?, ?, 'prof', ?, ?)",
        (user_id, name, token, password_hash)
    )
    conn.commit()
    conn.close()

    logger.info(f"Auth: new prof '{name}' registered")
    return RegisterResponse(user_id=user_id, name=name, role="prof", token=token)


@router.post("/auth/login-prof")
async def auth_login_prof(req: ProfLoginRequest):
    """M224: Login prof par nom + mot de passe."""
    name = req.name.strip()
    password_hash = _hash_password(req.password)

    conn = sqlite3.connect(str(PROJECTS_DB_PATH))
    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT id, name, role, token, password_hash FROM users WHERE name = ? AND role IN ('prof', 'admin')",
        (name,)
    ).fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=401, detail="Nom incorrect")

    user_id, db_name, role, token, stored_hash = row

    # Si pas de hash (ancien compte), on accepte sans mdp pour rétrocompatibilité
    if stored_hash and stored_hash != password_hash:
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")

    return RegisterResponse(user_id=user_id, name=db_name, role=role, token=token)


@router.post("/auth/login-student")
async def auth_login_student(req: StudentLoginRequest):
    """M224: Login élève sans mot de passe — par classe + student_id."""
    conn = sqlite3.connect(str(PROJECTS_DB_PATH))
    cursor = conn.cursor()

    # Vérifier que l'élève existe dans cette classe
    student_row = cursor.execute(
        "SELECT id, display, project_id FROM students WHERE id = ? AND class_id = ?",
        (req.student_id, req.class_id)
    ).fetchone()

    if not student_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Étudiant non trouvé dans cette classe")

    student_id, display, project_id = student_row

    # Créer ou récupérer user
    user_row = cursor.execute("SELECT id, token FROM users WHERE name = ?", (display,)).fetchone()
    if user_row:
        user_id, token = user_row
        # Mettre à jour le rôle si c'était 'student' par défaut
        cursor.execute("UPDATE users SET role = 'student' WHERE id = ?", (user_id,))
    else:
        user_id = str(uuid.uuid4())
        token = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO users (id, name, role, token) VALUES (?, ?, 'student', ?)",
            (user_id, display, token)
        )

    conn.commit()
    conn.close()

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
    conn = sqlite3.connect(str(PROJECTS_DB_PATH))
    cursor = conn.cursor()
    rows = cursor.execute(
        "SELECT id, display, project_id FROM students WHERE class_id = ? ORDER BY display",
        (class_id,)
    ).fetchall()
    conn.close()

    return {
        "students": [
            {"id": r[0], "display": r[1], "project_id": r[2]}
            for r in rows
        ]
    }
