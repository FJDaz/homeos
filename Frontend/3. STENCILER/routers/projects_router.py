"""
Projects Router - Extracted from server_v3.py
Contains all project-related routes, models, and helper functions.
"""

import os
import re
import json
import uuid
import sqlite3
import logging
import shutil
import unicodedata
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any

from bkd_service import bkd_db

from fastapi import APIRouter, HTTPException, Body, UploadFile, File, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel

# --- PATH CONSTANTS ---
CWD = Path(__file__).parent.parent.resolve()
ROOT_DIR = CWD.parent.parent
PROJECTS_DIR = ROOT_DIR / "projects"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
PROJECTS_DB_PATH = ROOT_DIR / "db/projects.db"

# --- LOGGING ---
logger = logging.getLogger("AetherFlowV3")

# --- ROUTER ---
router = APIRouter(prefix="/api", tags=["projects"])

# --- PYDANTIC MODELS ---
class ProjectInfo(BaseModel):
    id: str
    name: str
    path: str
    type: str = "personal"
    subject_id: Optional[str] = None
    created_at: Optional[str] = None
    last_opened: Optional[str] = None
    active: bool = False

class ProjectActivateRequest(BaseModel):
    id: str

class ProjectCreateRequest(BaseModel):
    name: str
    id: Optional[str] = None

class ProjectManifest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    raw_content: Optional[str] = None
    archetype: Optional[str] = None
    design_tokens: Optional[Dict] = None
    screens: Optional[List] = None
    wires: Optional[List] = None
    pending_intents: Optional[List] = None
    intent_pipeline: Optional[Dict] = None
    intent_inference: Optional[Dict] = None

# --- HELPER FUNCTIONS ---
def slugify(text: str, max_len: int = 30) -> str:
    # Mission 187: Priorité à l'intelligibilité
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode()
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[\s_]+', '-', text)
    return text[:max_len].rstrip('-')

def parse_design_md(content: str) -> dict:
    """Mission 128: Parse DESIGN.md according to HoméOS format."""
    tokens = {
        "colors": {"primary": "#8cc63f", "neutral": "#ffffff", "text": "#3d3d3c"},
        "typography": {"body": "Geist Sans", "headline_weight": "600"},
        "shape": {"border_radius": "6px"},
        "source": "default",
        "imported_at": datetime.now().isoformat()
    }

    # 1. Palette de Couleurs
    palette_match = re.search(r'### Palette de Couleurs([\s\S]*?)(?:###|$)', content)
    if palette_match:
        sect = palette_match.group(1)
        # Primary
        p_hex = re.search(r'\*\*Primary[^*]*\*\*.*?(#[0-9a-fA-F]{3,6})', sect, re.I)
        if p_hex: tokens["colors"]["primary"] = p_hex.group(1)
        # Backgrounds (souvent textuel, ex: "Blanc pur" -> fallback #fff)
        if "blanc" in sect.lower(): tokens["colors"]["neutral"] = "#ffffff"
        if "gris ultra-léger" in sect.lower(): tokens["colors"]["neutral"] = "#f9fafb"
        # Texts
        t_hex = re.search(r'\*\*Texts[^*]*\*\*.*?(#[0-9a-fA-F]{3,6})', sect, re.I)
        if t_hex: tokens["colors"]["text"] = t_hex.group(1)
        elif "gris anthracite" in sect.lower(): tokens["colors"]["text"] = "#1a1a1a"

    # 2. Typographie
    typo_match = re.search(r'### Typographie([\s\S]*?)(?:###|$)', content)
    if typo_match:
        sect = typo_match.group(1)
        font_match = re.search(r'Police de caractères\*\*.*?`([^`]+)`', sect)
        if font_match: tokens["typography"]["body"] = font_match.group(1)
        if "Semi-bold" in sect: tokens["typography"]["headline_weight"] = "600"

    return tokens


from bkd_service import get_active_project_id, set_active_project_id, get_active_project_path


def get_project_manifest(project_id: str) -> Dict[str, Any]:
    """Lit le manifest.json d'un projet."""
    manifest_path = PROJECTS_DIR / project_id / "manifest.json"
    if manifest_path.exists():
        try:
            return json.loads(manifest_path.read_text(encoding='utf-8'))
        except:
            return {}
    return {}

def save_project_manifest(project_id: str, manifest: Dict[str, Any]):
    """Sauvegarde le manifest.json d'un projet."""
    manifest_path = PROJECTS_DIR / project_id / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')

# Removed duplicated get_active_project_path proxy


def get_project_exports_dir():
    d = get_active_project_path() / "exports"
    d.mkdir(parents=True, exist_ok=True)
    return d

# --- ROUTES ---

@router.get("/projects/active", response_model=ProjectInfo)
def get_active_project_route(request: Request):
    token = request.headers.get("X-User-Token")
    active_id = get_active_project_id(token)
    if not active_id:
        raise HTTPException(status_code=404, detail="No active project")
    with bkd_db() as conn:
        row = conn.execute("SELECT id, name, path, created_at, last_opened FROM projects WHERE id=?",
                           (active_id,)).fetchone()
        if not row: raise HTTPException(status_code=404, detail="Active project not found")
        return ProjectInfo(id=row[0], name=row[1], path=row[2], created_at=row[3], last_opened=row[4], active=True)

@router.post("/projects/activate")
def activate_project(req: ProjectActivateRequest, request: Request = None):
    token = request.headers.get("X-User-Token") if request else None
    with bkd_db() as conn:
        exists = conn.execute("SELECT id FROM projects WHERE id=?", (req.id,)).fetchone()
        if not exists:
            # Auto-register si le dossier existe sur disque (projets élèves créés avant F2)
            project_path = PROJECTS_DIR / req.id
            if not project_path.exists():
                raise HTTPException(status_code=404, detail="Project not found")
            # Lire le nom depuis le manifest si disponible
            manifest_path = project_path / "manifest.json"
            proj_name = req.id
            if manifest_path.exists():
                try:
                    proj_name = json.loads(manifest_path.read_text(encoding='utf-8')).get("name", req.id)
                except Exception:
                    pass
            conn.execute(
                "INSERT OR IGNORE INTO projects (id, name, path) VALUES (?, ?, ?)",
                (req.id, proj_name, str(project_path))
            )
            logger.info(f"Auto-registered project on activate: {req.id}")
        conn.execute("UPDATE projects SET last_opened=datetime('now') WHERE id=?", (req.id,))

    set_active_project_id(req.id, token)
    # M304 — update students.project_id depuis le pattern project_id quand pas de token (appel prof)
    if not token:
        try:
            with bkd_db() as con:
                con.execute(
                    "UPDATE students SET project_id=? WHERE ? LIKE class_id || '-' || id || '%'",
                    (req.id, req.id)
                )
            logger.info(f"[M304] students.project_id mis à jour pour pattern: {req.id}")
        except Exception as e:
            logger.warning(f"[M304] Student update failed: {e}")
    logger.info(f"Project activated: {get_active_project_id(token)}")
    return {"status": "ok", "active_id": get_active_project_id(token)}

@router.get("/projects/active/manifest")
def get_active_manifest_route(request: Request):
    """M232: Retourne le manifest.json du projet actif (token-aware)."""
    token = request.headers.get("X-User-Token")
    active_id = get_active_project_id(token)
    if not active_id:
        return {}
    manifest_path = PROJECTS_DIR / active_id / "manifest.json"
    if not manifest_path.exists():
        return {}
    try:
        return json.loads(manifest_path.read_text(encoding='utf-8'))
    except Exception:
        return {}

@router.get("/projects/active/logic.js")
def get_active_logic_js(request: Request = None):
    """Mission 161: Sert le fichier logic.js du projet actif (token-aware)."""
    token = request.headers.get("X-User-Token") if request else None
    p_path = get_active_project_path(token)
    f_path = p_path / "logic.js"
    if not f_path.exists():
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content="// logic.js not found", media_type="application/javascript")
    return FileResponse(f_path, media_type="application/javascript")

@router.get("/projects", response_model=List[ProjectInfo])
def list_all_projects_route(request: Request):
    """Mission 190 + M298: Admin voit tout, user voit ses projets + (si étudiant) son sujet assigné."""
    token = request.headers.get("X-User-Token")
    user_id = getattr(request.state, 'user_id', None)
    active_id = get_active_project_id(token)

    logger.info(f"[M298] GET /api/projects — user_id={user_id}, active_id={active_id}")

    with bkd_db() as conn:
        # Check if user is admin
        is_admin = False
        if user_id:
            admin_name = os.getenv("ADMIN_NAME", "FJD")
            row = conn.execute("SELECT name FROM users WHERE id = ?", (user_id,)).fetchone()
            is_admin = row and row[0] == admin_name

        if is_admin:
            rows = conn.execute("SELECT id, name, path, created_at, last_opened, type, subject_id FROM projects ORDER BY last_opened DESC").fetchall()
        elif user_id:
            # M298: UNION — projets perso du user + projet étudiant assigné (via students.user_id)
            rows = conn.execute("""
                SELECT DISTINCT p.id, p.name, p.path, p.created_at, p.last_opened, p.type, p.subject_id
                FROM projects p
                WHERE p.user_id = ?
                   OR p.id = (SELECT s.project_id FROM students s WHERE s.user_id = ? AND s.project_id IS NOT NULL)
                ORDER BY p.last_opened DESC
            """, (user_id, user_id)).fetchall()
            logger.info(f"[M298] user_id={user_id[:8]}... → {len(rows)} projet(s)")
        else:
            # Legacy: no token → show all (backward compat)
            rows = conn.execute("SELECT id, name, path, created_at, last_opened, type, subject_id FROM projects ORDER BY last_opened DESC").fetchall()

        return [ProjectInfo(id=r[0], name=r[1], path=r[2], created_at=r[3], last_opened=r[4], type=r[5], subject_id=r[6], active=(r[0] == active_id)) for r in rows]

@router.post("/projects/create")
def create_project_route(request: Request, req: ProjectCreateRequest):
    """Mission 190: Ajoute user_id au projet créé."""
    user_id = getattr(request.state, 'user_id', None)
    pid = req.id or str(uuid.uuid4())[:8] # Small IDs for slugs
    p_path = PROJECTS_DIR / pid
    p_path.mkdir(parents=True, exist_ok=True)

    # Init subfolders
    (p_path / "imports").mkdir(exist_ok=True)
    (p_path / "exports").mkdir(exist_ok=True)
    (p_path / "assets").mkdir(exist_ok=True)

    # Create manifest.json minimal
    manifest = {
        "name": req.name,
        "archetype": None,
        "screens": [],
        "created_at": datetime.now().isoformat()
    }
    save_project_manifest(pid, manifest)
    
    # Mission 208: Scaffolding HoméOS
    from bkd_service import scaffold_project
    scaffold_project(p_path)

    with bkd_db() as conn:
        try:
            conn.execute("INSERT INTO projects (id, name, path, user_id, type) VALUES (?,?,?,?,?)",
                         (pid, req.name, str(p_path), user_id, "personal"))
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Project ID already exists")

    return {"status": "ok", "id": pid}

@router.delete("/projects/{project_id}")
def delete_project_route(project_id: str):
    """Mission 162: Supprime un projet (dossier + DB entry)."""
    p_path = PROJECTS_DIR / project_id
    if not p_path.exists():
        raise HTTPException(status_code=404, detail="Project folder not found")

    # Supprimer le dossier
    shutil.rmtree(p_path)

    # Supprimer de la DB
    with bkd_db() as conn:
        conn.execute('DELETE FROM projects WHERE id=?', (project_id,))


    logger.info(f"Project deleted: {project_id}")
    return {"status": "ok", "deleted": project_id}

@router.get("/projects/{project_id}/manifest")
def get_project_manifest_route(project_id: str):
    """Retourne le manifest.json d'un projet. Crée un manifest par défaut si absent."""
    manifest = get_project_manifest(project_id)
    if not manifest:
        # Project dir doesn't exist — create it with default manifest
        p_path = PROJECTS_DIR / project_id
        p_path.mkdir(parents=True, exist_ok=True)
        default_manifest = {
            "name": project_id,
            "description": "",
            "archetype": None,
            "design_tokens": None,
            "screens": [],
            "wires": [],
            "pending_intents": []
        }
        (p_path / "manifest.json").write_text(json.dumps(default_manifest, indent=2, ensure_ascii=False), encoding='utf-8')
        logger.info(f"Projects: created default manifest for {project_id}")
        return default_manifest
    return manifest

@router.put("/projects/{project_id}/manifest")
def update_project_manifest_route(project_id: str, manifest: ProjectManifest):
    """Met à jour le manifest.json d'un projet — merge profond pour préserver les champs pipeline."""
    p_path = PROJECTS_DIR / project_id
    if not p_path.exists():
        p_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Projects: created directory for {project_id}")

    # Charger le manifest existant sur disque
    manifest_path = p_path / "manifest.json"
    existing = {}
    if manifest_path.exists():
        try:
            existing = json.loads(manifest_path.read_text(encoding='utf-8'))
        except Exception:
            existing = {}

    # Merger : existing d'abord, puis les champs envoyés par le client (non-None seulement)
    incoming = {k: v for k, v in manifest.model_dump().items() if v is not None}
    merged = {**existing, **incoming}

    save_project_manifest(project_id, merged)
    return {"status": "ok", "manifest": merged}

@router.post("/projects/{project_id}/wires")
def add_project_wire_route(project_id: str, wire: dict = Body(...)):
    """Mission 160: Ajoute un 'wire' (câblage visuel) au projet."""
    manifest = get_project_manifest(project_id)
    if "wires" not in manifest: manifest["wires"] = []

    # Éviter les doublons exacts
    exists = any(w for w in manifest["wires"] if w.get("trigger") == wire.get("trigger") and w.get("target") == wire.get("target"))
    if not exists:
        manifest["wires"].append(wire)
        save_project_manifest(project_id, manifest)

    return {"status": "ok", "wires": manifest["wires"]}

@router.post("/project/import-design-md")
async def import_design_md(file: UploadFile = File(...)):
    """Parse et importe un DESIGN.md pour le projet actif."""
    content = (await file.read()).decode("utf-8")
    tokens = parse_design_md(content)

    # Sauvegarde locale au projet
    token_path = get_project_exports_dir() / "design_tokens.json"
    token_path.write_text(json.dumps(tokens, indent=2), encoding="utf-8")

    logger.info(f"Design tokens imported for project {get_active_project_id()}")
    return {"status": "ok", "tokens": tokens}

@router.get("/project/design-tokens")
def get_design_tokens():
    """Retourne les tokens du projet actif ou les defaults."""
    token_path = get_project_exports_dir() / "design_tokens.json"
    if token_path.exists():
        return json.loads(token_path.read_text())

    # Defaults HoméOS
    return {
        "colors": {"primary": "#8cc63f", "neutral": "#ffffff", "text": "#3d3d3c"},
        "typography": {"body": "Geist Sans", "headline_weight": "600"},
        "shape": {"border_radius": "6px"},
        "source": "homeos_default"
    }


# --- MISSION 189 : HOMEO_GENOME COMPILER ---
@router.post("/projects/{project_id}/genome-compile")
def genome_compile(project_id: str):
    """Compile HOMEO_GENOME.md unifié pour le projet."""
    if project_id == "active":
        project_id = get_active_project_id()
        if not project_id:
            raise HTTPException(status_code=404, detail="No active project")

    project_dir = PROJECTS_DIR / project_id
    if not project_dir.exists():
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")

    try:
        import sys
        backend_prod = ROOT_DIR / "Backend/Prod"
        if str(backend_prod) not in sys.path:
            sys.path.insert(0, str(backend_prod))
        from sullivan.genome_compiler import GenomeCompiler

        compiler = GenomeCompiler(project_dir)
        result = compiler.compile()
        logger.info(f"HOMEO_GENOME.md compiled for {project_id}: {result['size_kb']}Ko")
        return result
    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"GenomeCompiler not available: {e}")
    except Exception as e:
        logger.error(f"Genome compile failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/genome")
def genome_read(project_id: str):
    """Lit le HOMEO_GENOME.md du projet."""
    if project_id == "active":
        project_id = get_active_project_id()
        if not project_id:
            raise HTTPException(status_code=404, detail="No active project")

    genome_path = PROJECTS_DIR / project_id / "HOMEO_GENOME.md"
    if not genome_path.exists():
        raise HTTPException(status_code=404, detail="HOMEO_GENOME.md not found")

    return {"content": genome_path.read_text(encoding='utf-8')}
@router.get("/projects/{project_id}/context")
def get_project_context_route(project_id: str, class_id: Optional[str] = None):
    """Mission 225: Retourne le contexte complet du projet (summary + text)."""
    if project_id == "active":
        active_id = get_active_project_id()
        if not active_id: raise HTTPException(status_code=404, detail="No active project")
        project_id = active_id
    
    # Injection sys.path
    import sys
    backend_prod = ROOT_DIR / "Backend/Prod"
    if str(backend_prod) not in sys.path:
        sys.path.insert(0, str(backend_prod))
    
    from retro_genome.project_context import ProjectContext
    ctx = ProjectContext(project_id=project_id, class_id=class_id)
    return ctx.to_dict()
