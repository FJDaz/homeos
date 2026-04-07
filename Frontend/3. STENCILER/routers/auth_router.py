"""
Auth Router — Mission 190
Users table + session token + isolation projets.
"""

import os
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
    """Crée les tables users et user_keys, ajoute user_id à projects si absent."""
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
    """Enregistre un utilisateur par nom. Retourne user_id + token."""
    name = req.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Name required")

    admin_name = os.getenv("ADMIN_NAME", "FJD")
    role = "admin" if name == admin_name else "student"

    conn = sqlite3.connect(str(PROJECTS_DB_PATH))
    cursor = conn.cursor()

    # Chercher par name
    existing = cursor.execute("SELECT id, name, role, token FROM users WHERE name = ?", (name,)).fetchone()
    if existing:
        conn.close()
        return RegisterResponse(user_id=existing[0], name=existing[1], role=existing[2], token=existing[3])

    # Créer nouveau
    user_id = str(uuid.uuid4())
    token = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO users (id, name, role, token) VALUES (?, ?, ?, ?)",
        (user_id, name, role, token)
    )
    conn.commit()
    conn.close()

    logger.info(f"Auth: new user '{name}' registered (role={role})")
    return RegisterResponse(user_id=user_id, name=name, role=role, token=token)


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


# --- INIT ---
init_auth_db()
seed_admin()
