"""
Auth Router — Mission 190
Users table + session token + isolation projets.
"""

import os
import json
import uuid
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from Backend.Prod.models.gemini_client import GeminiClient
from Backend.Prod.config.settings import settings
from routers.auth_supabase import (
    find_student_by_display, find_user_by_name, create_user,
    find_user_by_token, list_classes, list_students_by_class,
    update_student, delete_class, create_class,
    find_user_by_id, get_user_key, set_user_key,
    find_student_by_id_and_class, update_user_password,
    find_user_by_name_with_password,
)

logger = logging.getLogger("AetherFlowV3")

router = APIRouter(prefix="/api")

# --- PATHS ---
CWD = Path(__file__).parent.parent.resolve()
ROOT_DIR = CWD.parent.parent
PROJECTS_DIR = ROOT_DIR / "projects"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

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

# --- DB INIT (no-op on Supabase — schema managed via migrations) ---
def init_auth_db():
    """Supabase tables are managed via migrations. No local init needed."""
    pass

# --- SEED ADMIN ---
def seed_admin():
    """Seed le user admin si absent (ADMIN_NAME depuis .env, défaut: FJD)."""
    admin_name = os.getenv("ADMIN_NAME", "FJD")
    existing = find_user_by_name(admin_name)
    if not existing:
        admin_id = str(uuid.uuid4())
        admin_token = str(uuid.uuid4())
        create_user(admin_id, admin_name, "admin", admin_token)
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
    student_info = find_student_by_display(name)
    student_id = student_info[0] if student_info else None
    class_id = student_info[1] if student_info else None
    project_id = student_info[2] if student_info else None

    # Chercher user existant
    existing = find_user_by_name(name)
    if existing:
        return RegisterResponse(
            user_id=existing[0], name=existing[1], role=existing[2], token=existing[3],
            student_id=student_id, class_id=class_id, project_id=project_id
        )

    # Créer nouveau
    user_id = str(uuid.uuid4())
    token = str(uuid.uuid4())
    create_user(user_id, name, role, token)

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

    user = find_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    return MeResponse(user_id=user[0], name=user[1], role=user[2])


@router.post("/me/keys")
async def save_user_key(request: Request, req: KeyRequest):
    """Sauvegarde une clé API utilisateur (BYOK)."""
    token = request.headers.get("X-User-Token")
    if not token:
        raise HTTPException(status_code=401, detail="X-User-Token header required")

    user = find_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = user[0]
    set_user_key(user_id, req.provider, req.api_key)

    logger.info(f"Auth: user {user_id[:8]}... saved key for {req.provider}")
    return {"status": "ok", "provider": req.provider}


@router.get("/me/keys")
async def list_user_keys(request: Request):
    """Retourne le statut des clés API (jamais la clé elle-même)."""
    token = request.headers.get("X-User-Token")
    if not token:
        raise HTTPException(status_code=401, detail="X-User-Token header required")

    user = find_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = user[0]
    all_providers = ["gemini", "groq", "openai", "kimi", "mimo", "deepseek", "qwen", "watson"]
    result = {p: get_user_key(user_id, p) is not None and "set" or "not_set" for p in all_providers}
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
        
        raw_code = result.code.strip()
        if raw_code.startswith("```json"):
            raw_code = raw_code[7:]
        elif raw_code.startswith("```"):
            raw_code = raw_code[3:]
        if raw_code.endswith("```"):
            raw_code = raw_code[:-3]
        raw_code = raw_code.strip()
        
        return json.loads(raw_code)
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
    existing = find_user_by_name(name)
    if existing:
        raise HTTPException(status_code=409, detail="Ce nom est déjà pris")

    user_id = str(uuid.uuid4())
    token = str(uuid.uuid4())
    create_user(user_id, name, "prof", token)
    update_user_password(user_id, password_hash)

    logger.info(f"Auth: new prof '{name}' registered")
    return RegisterResponse(user_id=user_id, name=name, role="prof", token=token)


@router.post("/auth/login-prof")
async def auth_login_prof(req: ProfLoginRequest):
    """M224: Login prof par nom + mot de passe."""
    name = req.name.strip()
    password_hash = _hash_password(req.password)

    user = find_user_by_name_with_password(name)
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
    student = find_student_by_id_and_class(req.student_id, req.class_id)
    if not student:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé dans cette classe")

    student_id, display, project_id, _ = student

    # Créer ou récupérer user
    user = find_user_by_name(display)
    if user:
        user_id, _, _, token = user
    else:
        user_id = str(uuid.uuid4())
        token = str(uuid.uuid4())
        create_user(user_id, display, "student", token)

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
    students = list_students_by_class(class_id)
    return {
        "students": [
            {"id": s["id"], "display": s.get("display", s["id"]), "project_id": s.get("project_id")}
            for s in students
        ]
    }
