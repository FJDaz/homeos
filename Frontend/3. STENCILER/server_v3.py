#!/usr/bin/env python3
"""
AetherFlow Server V3 - FastAPI Foundation
Mission 85: BKD Routes & Sullivan Pulse
"""

import os
import json
import sys
import re
import uuid
import sqlite3
import asyncio
import logging
import subprocess
import shutil
import urllib.request
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Query, Body, Request, UploadFile, File, BackgroundTasks, Form
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# --- CONFIGURATION & PATHS ---
CWD = Path(__file__).parent.resolve()
ROOT_DIR = CWD.parent.parent
BACKEND_PROD = ROOT_DIR / "Backend/Prod"
PROJECTS_DIR = ROOT_DIR / "projects"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
PROJECTS_DB_PATH = ROOT_DIR / "db/projects.db"

# --- LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AetherFlowV3")

# --- ENVIRONMENT ---
def _load_env():
    env_path = ROOT_DIR / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())
        logger.info("Environment variables loaded from .env")

_load_env()

# --- SULLIVAN IMPORTS ---
import sys
for p in [str(ROOT_DIR), str(BACKEND_PROD)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from bkd_service import (
    SULLIVAN_BKD_SYSTEM, MANIFEST_FRD, SULLIVAN_RAG,
    exec_query_knowledge_base, route_request_bkd,
    resolve_bkd_project_root, bkd_safe_path, bkd_build_tree,
    BKD_DB_PATH, bkd_db_con, PROJECTS_DIR,
    get_active_project_id, set_active_project_id, get_active_project_path,
)

from sullivan_arbitrator import SullivanArbitrator, SullivanPulse

try:
    from Backend.Prod.retro_genome.manifest_validator import validate_html, format_system_prompt_constraint, load_manifest, get_manifest_path
except ImportError:
    logger.warning("Manifest validator not found. FRD validation will be disabled.")
    def validate_html(n, c): return True, []
    def format_system_prompt_constraint(n): return ""
    def load_manifest(n): return {}
    def get_manifest_path(n): return None

# --- MISSION 87 : LEGACY IMPORTS ---
try:
    from sullivan.context_pruner import prune_genome
    from Backend.Prod.retro_genome.analyzer import RetroGenomeAnalyzer
    from Backend.Prod.retro_genome.intent_mapper import IntentMapper
    from Backend.Prod.retro_genome.html_generator import HtmlGenerator
    from Backend.Prod.retro_genome import brainstorm_logic as brs_logic
except ImportError as e:
    logger.warning(f"Legacy modules missing: {e}. Some routes will fail.")

from wire_analyzer import WireAnalyzer

from Backend.Prod.retro_genome.routes import router as retro_genome_router

# --- LEGACY CONSTANTS (Scoped if possible) ---
# Note: We keep these for non-scoped core files
GENOME_FILE = ROOT_DIR / "Frontend/2. GENOME/genome_enriched.json"
LAYOUT_FILE = ROOT_DIR / "Frontend/2. GENOME/layout.json"

# --- DATABASE INIT ---
def init_db():
    PROJECTS_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(PROJECTS_DB_PATH)) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                last_opened TEXT DEFAULT (datetime('now'))
            )
        """)
        
        # Ensure default project exists
        existing = conn.execute("SELECT id FROM projects WHERE id='homéos-default'").fetchone()
        if not existing:
            default_path = PROJECTS_DIR / "homéos-default"
            default_path.mkdir(parents=True, exist_ok=True)
            (default_path / "imports").mkdir(exist_ok=True)
            (default_path / "exports").mkdir(exist_ok=True)
            (default_path / "assets").mkdir(exist_ok=True)
            conn.execute("INSERT INTO projects (id, name, path) VALUES (?,?,?)",
                         ("homéos-default", "homéos default", str(default_path)))
            logger.info("Created Default Project: homéos-default")

            # Migration douce : copier manifest + imports existants s'ils existent à la racine
            old_manifest = ROOT_DIR / "exports" / "manifest.json"
            new_manifest = default_path / "manifest.json"
            if old_manifest.exists() and not new_manifest.exists():
                import shutil
                shutil.copy2(str(old_manifest), str(new_manifest))
                logger.info(f"Migration douce : manifest.json copié vers {new_manifest}")

            old_imports = ROOT_DIR / "exports" / "retro_genome"
            new_imports = default_path / "imports"
            if old_imports.exists():
                for f in old_imports.iterdir():
                    dest = new_imports / f.name
                    if not dest.exists():
                        shutil.copy2(str(f), str(dest))
                logger.info(f"Migration douce : imports copiés vers {new_imports}")
            
    logger.info(f"Projects database initialized at {PROJECTS_DB_PATH}")

def get_active_project_id():
    from bkd_service import get_active_project_id
    return get_active_project_id()

def get_active_project_path():
    from bkd_service import get_active_project_path
    return get_active_project_path()

# --- PROJECT PATH HELPERS (Mission 111) ---
def get_project_manifest_path():
    return get_active_project_path() / "manifest.json"

def get_project_imports_dir():
    d = get_active_project_path() / "imports"
    d.mkdir(parents=True, exist_ok=True)
    return d

def get_project_exports_dir():
    d = get_active_project_path() / "exports"
    d.mkdir(parents=True, exist_ok=True)
    return d

def get_project_pipeline_dir():
    d = get_project_exports_dir() / "pipeline"
    d.mkdir(parents=True, exist_ok=True)
    return d

# --- PYDANTIC MODELS ---
class ProjectCreateRequest(BaseModel):
    name: str
    id: Optional[str] = None

class ProjectActivateRequest(BaseModel):
    id: str

class ProjectInfo(BaseModel):
    id: str
    name: str
    path: str
    created_at: str
    last_opened: str

class BKDFileListItem(BaseModel):
    path: str
    name: str
    ext: str

class BKDFileListingResponse(BaseModel):
    files: List[BKDFileListItem]

class FileReadInfo(BaseModel):
    project_id: str
    path: str


class FileResponse(BaseModel):
    content: str
    language: str
    path: str
    size: int

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []
    project_id: Optional[str] = None

class ChatResponse(BaseModel):
    explanation: str
    html: Optional[str] = None
    model: str
    route: str
    provider: str

class FileWriteRequest(BaseModel):
    project_id: str
    path: str
    content: str

class FRDFileRequest(BaseModel):
    name: str
    content: str
    force: Optional[bool] = False

class KimiStartRequest(BaseModel):
    instruction: str
    html: str

class KimiResultResponse(BaseModel):
    status: str
    html: Optional[str] = None
    label: Optional[str] = None
    error: Optional[str] = None

class WireRequest(BaseModel):
    html: str

# --- GLOBAL STATE (SULLIVAN) ---
_ARBITRATOR = SullivanArbitrator()
_PULSE = SullivanPulse()

# --- KIMI JOBS STATE ---
_KIMI_JOBS: Dict[str, Dict[str, Any]] = {}
_KIMI_JOBS_LOCK = asyncio.Lock()

# --- CONSTANTS: LAYOUT INFERENCE ---
_ROLE_KEYWORDS = {
    "header":   ["menu", "nav", "toolbar", "header", "top"],
    "sidebar":  ["controls", "layers", "sidebar", "tools", "panel"],
    "main":     ["editor", "canvas", "main", "grid", "content"],
    "preview":  ["thumbnail", "preview", "assets", "timeline"],
    "footer":   ["status", "footer", "bottom", "dock"]
}
_ROLE_LAYOUT = {
    "header":   {"zone": "header",        "w": 1024, "h": 40,    "layout": "flex"},
    "sidebar":  {"zone": "sidebar_right", "w": 240,  "h": "auto","layout": "stack"},
    "main":     {"zone": "main",          "w": 640,  "h": "auto","layout": "stack"},
    "preview":  {"zone": "preview_band",  "w": 1024, "h": 120,   "layout": "flex"},
    "footer":   {"zone": "footer",        "w": 1024, "h": 48,    "layout": "flex"},
}
_LAYOUT_SYSTEM_PROMPT = """Tu es un expert UX/layout. Pour chaque organe N1 d'un genome JSON, tu inféres ses paramètres de layout SVG.
Règles : reference_width=1024px, grid_unit=8px (toutes les valeurs en multiples de 8).
Zones : header, sidebar_left, sidebar_right, main, canvas, preview_band, footer.
Layout types : flex, stack, grid, free. h = nombre|"auto"|"full", w = nombre|"full".
Réponds UNIQUEMENT avec un objet JSON valide, sans markdown, sans explication.
Format : { "organ_id": { "role": "...", "zone": "...", "w": ..., "h": ..., "layout": "..." }, ... }"""

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    _load_env()
    init_db()
    _PULSE.start()
    logger.info("Sullivan Pulse started")
    
    # RAG Initialisation (if needed, simplified for now)
    # _SULLIVAN_RAG = init_sullivan_rag()
    
    yield
    # Shutdown
    logger.info("Server shutting down")

app = FastAPI(
    title="AetherFlow Server V3",
    description="FastAPI implementation for AetherFlow BKD/FRD",
    version="3.0.0",
    lifespan=lifespan
)

# CORS — inclut "null" pour les iframes sandboxées (plugin Figma)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "null"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(retro_genome_router, prefix="/api")

# Exception handler global — ajoute CORS sur les 500 non catchés
@app.exception_handler(Exception)
async def _global_exception_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
        headers={"Access-Control-Allow-Origin": "*"},
    )

# --- STATIC FILES ---
# On monte /static sur le dossier static/
STATIC_DIR_PATH = CWD / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR_PATH)), name="static")

@app.get("/stenciler")
async def get_stenciler():
    path = STATIC_DIR_PATH / "templates/stenciler.html"
    from fastapi.responses import FileResponse
    return FileResponse(path)

@app.get("/bkd")
async def get_bkd_editor():
    path = STATIC_DIR_PATH / "templates/bkd_editor.html"
    if not path.exists(): raise HTTPException(status_code=404, detail="bkd_editor.html not yet generated")
    from fastapi.responses import FileResponse
    return FileResponse(path)

@app.get("/frd-editor")
async def get_frd_editor():
    path = STATIC_DIR_PATH / "templates/frd_editor.html"
    from fastapi.responses import FileResponse
    return FileResponse(path)

# --- UTILS (BKD) ---
ALLOWED_EXTENSIONS = {'.py', '.js', '.ts', '.html', '.css', '.md', '.json', '.txt', '.yaml', '.yml', '.toml', '.sh', '.env.example'}
EXCLUDE_DIRS = {'__pycache__', '.git', 'node_modules', '.venv', 'venv', 'dist', 'build', '.mypy_cache'}

# Aliases vers bkd_service (pas de duplication)
get_db_conn = bkd_db_con
resolve_project_root = resolve_bkd_project_root
build_tree = bkd_build_tree
safe_path = bkd_safe_path

# --- ROUTES : SULLIVAN ---
@app.get("/api/sullivan/pulse")
async def get_sullivan_pulse():
    return _PULSE.get_status()

# --- ROUTES : SULLIVAN TYPOGRAPHY ENGINE (Mission 109 Phase B) ---
@app.post("/api/sullivan/font-upload")
async def sullivan_font_upload(file: UploadFile = File(...)):
    """
    Mission 109 Phase B: Upload TTF/OTF/WOFF/WOFF2 → classification + webfont + @font-face.
    """
    from Backend.Prod.sullivan.font_classifier import FontClassifier
    from Backend.Prod.sullivan.font_webgen import FontWebGen
    
    # Sauvegarde temporaire
    exports_dir = ROOT_DIR / "exports" / "fonts"
    exports_dir.mkdir(parents=True, exist_ok=True)
    
    temp_path = exports_dir / f"temp_{file.filename}"
    content = await file.read()
    temp_path.write_bytes(content)
    
    try:
        # 1. Classification
        classifier = FontClassifier()
        classification = classifier.classify(str(temp_path))
        
        # 2. Génération webfont
        webgen = FontWebGen()
        webfont_result = webgen.generate(str(temp_path), classification)
        
        # 3. Nettoyage
        temp_path.unlink()
        
        return {
            "status": "ok",
            "classification": classification,
            "webfont": webfont_result
        }
    except Exception as e:
        logger.error(f"Font upload failed: {e}")
        if temp_path.exists():
            temp_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sullivan/fonts")
async def sullivan_list_fonts():
    """Liste toutes les fontes dans /static/fonts/."""
    from Backend.Prod.sullivan.font_webgen import FontWebGen
    webgen = FontWebGen()
    fonts = webgen.list_fonts()
    return {"fonts": fonts}

@app.delete("/api/sullivan/fonts/{slug}")
async def sullivan_delete_font(slug: str):
    """Supprime une fonte et son répertoire."""
    from Backend.Prod.sullivan.font_webgen import FontWebGen
    webgen = FontWebGen()
    success = webgen.delete_font(slug)
    if success:
        return {"status": "ok", "deleted": slug}
    raise HTTPException(status_code=404, detail=f"Font '{slug}' not found")

# --- ROUTES : PROJECTS (Mission 111) ---

@app.get("/api/projects/active", response_model=ProjectInfo)
async def get_active_project_route():
    with sqlite3.connect(str(PROJECTS_DB_PATH)) as conn:
        row = conn.execute("SELECT id, name, path, created_at, last_opened FROM projects WHERE id=?", 
                           (get_active_project_id(),)).fetchone()
        if not row: raise HTTPException(status_code=404, detail="Active project not found")
        return ProjectInfo(id=row[0], name=row[1], path=row[2], created_at=row[3], last_opened=row[4])

@app.post("/api/projects/activate")
async def activate_project(req: ProjectActivateRequest):
    with sqlite3.connect(str(PROJECTS_DB_PATH)) as conn:
        exists = conn.execute("SELECT id FROM projects WHERE id=?", (req.id,)).fetchone()
        if not exists: raise HTTPException(status_code=404, detail="Project not found")
        conn.execute("UPDATE projects SET last_opened=datetime('now') WHERE id=?", (req.id,))
    
    set_active_project_id(req.id)
    logger.info(f"Project activated: {get_active_project_id()}")
    return {"status": "ok", "active_id": get_active_project_id()}

@app.get("/api/projects", response_model=List[ProjectInfo])
async def list_all_projects_route():
    with sqlite3.connect(str(PROJECTS_DB_PATH)) as conn:
        rows = conn.execute("SELECT id, name, path, created_at, last_opened FROM projects ORDER BY last_opened DESC").fetchall()
        return [ProjectInfo(id=r[0], name=r[1], path=r[2], created_at=r[3], last_opened=r[4]) for r in rows]

@app.post("/api/projects/create")
async def create_project_route(req: ProjectCreateRequest):
    pid = req.id or str(uuid.uuid4())[:8] # Small IDs for slugs
    p_path = PROJECTS_DIR / pid
    p_path.mkdir(parents=True, exist_ok=True)
    
    # Init subfolders
    (p_path / "imports").mkdir(exist_ok=True)
    (p_path / "exports").mkdir(exist_ok=True)
    (p_path / "assets").mkdir(exist_ok=True)
    
    with sqlite3.connect(str(PROJECTS_DB_PATH)) as conn:
        try:
            conn.execute("INSERT INTO projects (id, name, path) VALUES (?,?,?)", 
                         (pid, req.name, str(p_path)))
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Project ID already exists")
            
    return {"status": "ok", "id": pid}

@app.get("/api/bkd/projects", response_model=Dict[str, List[ProjectInfo]])
async def list_bkd_projects():
    # Legacy link for BKD
    projects = await list_all_projects_route()
    return {"projects": projects}

@app.get("/api/bkd/files")
async def list_bkd_files(project_id: str = Query(...)):
    root = resolve_project_root(project_id)
    if not root:
        raise HTTPException(status_code=404, detail="Project not found")
    files = []
    for p in Path(root).rglob("*"):
        if p.is_file() and p.suffix in BKD_ALLOWED_EXTENSIONS:
            if not any(part in BKD_EXCLUDE_DIRS for part in p.parts):
                rel = str(p.relative_to(root))
                files.append({"path": rel, "name": p.name, "ext": p.suffix})
    files.sort(key=lambda f: f["path"])
    return {"files": files}

@app.delete("/api/bkd/projects/{project_id}")
async def delete_project(project_id: str):
    with get_db_conn() as conn:
        conn.execute('DELETE FROM projects WHERE id=?', (project_id,))
    return {"ok": True, "deleted": project_id}

# --- ROUTES : BKD FILES ---
@app.get("/api/bkd/files", response_model=BKDFileListingResponse)
async def bkd_list_files(project_id: str = Query(...)):
    root = resolve_bkd_project_root(project_id)
    if not root:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Recursive build tree from bkd_service
    tree = bkd_build_tree(root, rel="", depth=10)
    
    # Flatten the tree as requested by Mission 90
    flat_files = []
    def flatten(nodes):
        for node in nodes:
            if node['type'] == 'file':
                flat_files.append(BKDFileListItem(
                    path=node['path'],
                    name=node['name'],
                    ext=Path(node['name']).suffix
                ))
            elif node['type'] == 'dir':
                flatten(node.get('children', []))
    
    flatten(tree)
    return BKDFileListingResponse(files=flat_files)

@app.get("/api/bkd/file", response_model=FileResponse)
async def get_file(project_id: str = Query(...), path: str = Query(...)):
    root = resolve_bkd_project_root(project_id)
    if not root:
        raise HTTPException(status_code=404, detail="Project not found")
    
    file_path = bkd_safe_path(root, path)
    if not file_path or not file_path.exists():
        raise HTTPException(status_code=403, detail="Path not allowed or file not found")
    
    content = file_path.read_text(encoding='utf-8')
    ext_map = {'.py':'python','.js':'javascript','.ts':'typescript','.html':'html','.css':'css','.md':'markdown','.json':'json','.yaml':'yaml','.yml':'yaml','.toml':'toml','.sh':'bash'}
    
    return FileResponse(
        content=content,
        language=ext_map.get(file_path.suffix, 'text'),
        path=path,
        size=len(content)
    )

@app.post("/api/bkd/file")
async def write_file(req: FileWriteRequest):
    root = resolve_project_root(req.project_id)
    if not root:
        raise HTTPException(status_code=404, detail="Project not found")
    
    file_path = safe_path(root, req.path)
    if not file_path:
        raise HTTPException(status_code=403, detail="Path not allowed")
    
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(req.content, encoding='utf-8')
    return {"ok": True, "path": req.path, "size": len(req.content)}

# --- UTILS : GENOME & LAYOUT ---
def load_genome():
    if GENOME_FILE.exists():
        try: return json.loads(GENOME_FILE.read_text(encoding='utf-8'))
        except: return {"n0_phases": []}
    return {"n0_phases": []}

def save_genome(genome):
    GENOME_FILE.parent.mkdir(parents=True, exist_ok=True)
    GENOME_FILE.write_text(json.dumps(genome, indent=2, ensure_ascii=False), encoding='utf-8')

def load_layout():
    if LAYOUT_FILE.exists():
        try: return json.loads(LAYOUT_FILE.read_text(encoding='utf-8'))
        except: return {}
    return {}

def save_layout(data):
    LAYOUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    LAYOUT_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

def _load_overrides():
    f = get_project_pipeline_dir() / "template_overrides.json"
    if f.exists():
        try: return json.loads(f.read_text(encoding="utf-8"))
        except: return {}
    return {}

def save_template_overrides(data: Dict[str, Any]):
    p_dir = get_project_pipeline_dir()
    (p_dir / "template_overrides.json").write_text(json.dumps(data, indent=2), encoding="utf-8")

def _write_retro_status(step, message):
    get_project_imports_dir().mkdir(parents=True, exist_ok=True)
    (get_project_imports_dir() / "upload_status.json").write_text(json.dumps({"step": step, "message": message, "ts": datetime.now().isoformat()}))

@app.get("/api/retro-genome/status")
async def retro_genome_status():
    status_file = get_project_imports_dir() / "upload_status.json"
    analysis_file = get_project_imports_dir() / "last_analysis.json"
    
    # Base status from upload_status.json if active
    res = {"step": "idle", "message": ""}
    if status_file.exists():
        res = json.loads(status_file.read_text(encoding="utf-8"))
    
    # Attach persistent analysis data if available (Mission 102 Backend)
    if analysis_file.exists():
        try:
            analysis_data = json.loads(analysis_file.read_text(encoding="utf-8"))
            res["analysis"] = analysis_data.get("analysis")
            res["audit"] = analysis_data.get("audit")
            res["archetype"] = analysis_data.get("archetype")
        except: pass
    
    return res

class AnnotateRequest(BaseModel):
    intent_id: str
    component_name: str
    description: str

@app.post("/api/frd/annotate")
async def frd_annotate(req: AnnotateRequest):
    """
    Mission 102: Lancement de l'annotation (KIMI / AI).
    Génère un plan d'implémentation pour une intention donnée.
    """
    try:
        # Import dynamic context from retro_genome
        from Backend.Prod.retro_genome.routes import _get_gemini_client
        client = _get_gemini_client()
        
        prompt = f"""You are an AetherFlow Architect. 
Provide a high-precision implementation plan for the following UI intent:
- Intent ID: {req.intent_id}
- Component: {req.component_name}
- Functional Goal: {req.description}

Format: Short technical markdown. Focus on:
1. Expected Frontend Interaction (JS).
2. Backend Endpoint convention (FastAPI).
3. Data Contract (JSON).

Output valid Markdown only, no prose."""

        result = await client.generate(prompt=prompt, max_tokens=1024)
        await client.close()
        
        if result.success:
            return {"status": "ok", "annotation": result.code}
        else:
            return {"status": "error", "message": result.error}
    except Exception as e:
        logger.error(f"Annotation failed: {e}")
        return {"status": "error", "message": str(e)}

def load_custom_injection():
    injection_path = STATIC_DIR_PATH / 'js' / 'custom_injection.js'
    if injection_path.exists():
        return f"<script>{injection_path.read_text(encoding='utf-8')}</script>"
    return ""

# --- ROUTES : FRD FILES ---
@app.get("/api/frd/file")
async def get_frd_file(name: str = Query(...)):
    if '/' in name or '..' in name:
        raise HTTPException(status_code=400, detail="Invalid filename")
    path = STATIC_DIR_PATH / "templates" / name
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return {"content": path.read_text(encoding='utf-8'), "name": name}

@app.post("/api/frd/file")
async def save_frd_file(req: FRDFileRequest):
    if '/' in req.name or '..' in req.name:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Validation manifeste DOM (Mission 63)
    is_valid, errors = validate_html(req.name, req.content)
    if not is_valid and not req.force:
        return JSONResponse(status_code=422, content={
            "error": "CONTRAT DOM VIOLÉ",
            "violations": errors
        })
    
    path = STATIC_DIR_PATH / "templates" / req.name
    path.write_text(req.content, encoding='utf-8')
    return {"status": "ok", "name": req.name}

# --- ROUTES : FRD FILES LIST ---
@app.get("/api/frd/files")
async def list_frd_files():
    files = sorted([f.name for f in (STATIC_DIR_PATH / "templates").glob("*.html")])
    return {"files": files}

# --- ROUTES : FRD ASSETS ---
@app.get("/api/frd/assets")
async def list_frd_assets():
    assets_dir = STATIC_DIR_PATH / "assets" / "frd"
    assets_dir.mkdir(parents=True, exist_ok=True)
    assets = []
    for f in sorted(assets_dir.iterdir()):
        if f.is_file() and f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'):
            assets.append({"name": f.name, "url": f"/static/assets/frd/{f.name}"})
    return {"assets": assets}

@app.post("/api/frd/upload")
async def upload_frd_asset(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'):
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    assets_dir = STATIC_DIR_PATH / "assets" / "frd"
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    dest_path = assets_dir / file.filename
    with open(dest_path, "wb") as f:
        f.write(await file.read())
    
    return {"url": f"/static/assets/frd/{file.filename}"}

# --- ROUTES : FRD WIRE ---
def _build_wire_prompt(html_context: str) -> str:
    return (
        "Tu es Sullivan (IA HomeOS), expert en diagnostic et implémentation de code HTML/JS.\n"
        "Analyse le code source fourni.\n\n"
        "PARTIE 1 — DIAGNOSTIC : Identifie les problèmes existants :\n"
        "- Sélecteurs orphelins (getElementById/querySelector vers IDs absents)\n"
        "- Bindings manquants (addEventListener/onclick vers fonctions non définies)\n"
        "- Fetch vers endpoints non déclarés\n"
        "- Interactions décrites dans le HTML mais sans JS correspondant\n\n"
        "PARTIE 2 — PLAN D'IMPLÉMENTATION : Liste les actions JS à implémenter pour que l'UI soit fonctionnelle. "
        "Pour chaque action : indique l'élément cible, le comportement attendu, et l'endpoint API si applicable.\n\n"
        "FORMAT (Markdown) :\n"
        "# 🕸️ Diagnostic WIRE\n\n"
        "## 🔍 Problèmes détectés\n- [Liste ou 'Aucun']\n\n"
        "## 📋 Plan d'implémentation\n"
        "1. [Action] — [Élément] → [Comportement / Endpoint]\n"
        "2. ...\n\n"
        "SOIS FACTUEL ET CONCIS. Si le fichier est un shell sans JS, liste quand même tout ce qui devrait être branché."
        f"\n\nCODE SOURCE :\n{html_context}"
    )

@app.post("/api/frd/wire")
async def frd_wire(req: WireRequest):
    prompt = _build_wire_prompt(req.html)
    config = _ARBITRATOR.pick("wire")

    def _call():
        r = urllib.request.Request(
            config["base_url"],
            data=json.dumps({
                "model": config["model"],
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0
            }).encode('utf-8'),
            headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {config["api_key"]}'}
        )
        with urllib.request.urlopen(r, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data['choices'][0]['message']['content']

    try:
        diagnostic = await asyncio.to_thread(_call)
        return {"diagnostic": diagnostic, "provider": config["provider"], "model": config["model"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- ROUTES : BKD CHAT ---
@app.post("/api/bkd/chat", response_model=ChatResponse)
async def bkd_chat(req: ChatRequest):
    try:
        # 1. Routing via Groq + SullivanArbitrator
        route_info = route_request_bkd(req.message, req.history, _ARBITRATOR)
        route_type = route_info.get('type', 'quick')
        config = _ARBITRATOR.pick(route_type)

        project_ctx = ''
        if req.project_id:
            root = resolve_bkd_project_root(req.project_id)
            if root:
                tree = bkd_build_tree(root, depth=1)
                tree_names = ', '.join(n['name'] for n in tree[:20])
                project_ctx = f'\nPROJET ACTIF : {root}\nFICHIERS RACINE : {tree_names}\n'

        system_instruction = SULLIVAN_BKD_SYSTEM + project_ctx + '\n\nMANIFEST PROJET :\n' + MANIFEST_FRD
        
        # Tools wiring (Gemini style as used in dispatch)
        tools = [{
            'functionDeclarations': [
                {
                    'name': 'query_knowledge_base',
                    'description': 'Interroge la base de connaissance AetherFlow.',
                    'parameters': {'type': 'OBJECT', 'properties': {'query': {'type': 'STRING'}}, 'required': ['query']}
                },
                {
                    'name': 'read_bkd_file',
                    'description': 'Lit le contenu d\'un fichier du projet backend.',
                    'parameters': {'type': 'OBJECT', 'properties': {'path': {'type': 'STRING'}}, 'required': ['path']}
                }
            ]
        }]
        
        # Simplification of the loop for M85 (porting existing logic)
        messages = [{"role": turn.get('role', 'user'), "content": turn.get('text', '')} for turn in req.history[-12:]]
        messages.append({"role": "user", "content": req.message})
        
        final_text = ""
        for _ in range(4):
            res = _ARBITRATOR.dispatch(config, messages, system=system_instruction, tools=tools)
            if not res.get("success"):
                raise HTTPException(status_code=500, detail=res.get("error", "Dispatch error"))
            
            fc = res.get("function_call")
            if fc and fc.get('name') == 'query_knowledge_base':
                q = fc['args'].get('query', '')
                result = exec_query_knowledge_base(q)
                messages.append({'role': 'assistant', 'content': f'Appel outil knowledge base: {q}'})
                messages.append({'role': 'user', 'content': f'RESULTAT: {result}'})
            elif fc and fc.get('name') == 'read_bkd_file' and req.project_id:
                rel = fc['args'].get('path', '')
                root = resolve_project_root(req.project_id)
                file_content = ''
                if root:
                    safe = safe_path(root, rel)
                    if safe:
                        try:
                            file_content = safe.read_text(encoding='utf-8')[:6000]
                        except:
                            file_content = f'Impossible de lire {rel}'
                    else:
                        file_content = f'Accès refusé : {rel}'
                messages.append({'role': 'assistant', 'content': f'Appel outil read file: {rel}'})
                messages.append({'role': 'user', 'content': f'CONTENU: {file_content}'})
            else:
                final_text = res.get("text", "")
                break

        return ChatResponse(
            explanation=final_text,
            model=config['model'],
            route=route_type,
            provider=config['provider']
        )
    except Exception as e:
        logger.error(f"BKD Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- ROUTES : FRD CHAT ---
@app.post("/api/frd/chat")
async def frd_chat(body: Dict[str, Any]):
    # Fix silent 500 by validating inputs early
    message = body.get('message', '')
    html_context = body.get('html', '')
    file_name = body.get('name', '')
    history = body.get('history', [])
    mode = body.get('mode', 'construct')
    
    project_manifest = load_manifest(file_name) if file_name else {}
    manifest_block = f"\n\nCONTEXTE PROJET :\n{json.dumps(project_manifest)}\n" if project_manifest else ""
    
    # Common system prompt
    api_contract = ROOT_DIR / "Frontend/1. CONSTITUTION/API_CONTRACT.md"
    contract_text = api_contract.read_text(encoding='utf-8') if api_contract.exists() else "No contract"
    
    dom_constraint = format_system_prompt_constraint(file_name) if file_name else ""
    
    system_instruction = (
        "Tu es Sullivan, expert frontend HomeOS. Tu crées ou modifies des fichiers HTML/Tailwind CSS avec JavaScript vanilla inline.\n"
        "RÈGLE JS : Toujours inclure les event listeners, toggles, fetch calls et interactions nécessaires en JS vanilla dans des balises <script> dans le même fichier HTML. "
        "Si l'UI contient des boutons, formulaires, panels ou onglets interactifs, génère OBLIGATOIREMENT le JS correspondant.\n"
        "RÈGLE CRITIQUE : Si la demande décrit une page DIFFÉRENTE de l'HTML actuel, IGNORE l'HTML actuel et crée une nouvelle page.\n"
        "Format de réponse : [explication 1-2 phrases]\n---HTML---\n[code HTML complet]\n"
        + dom_constraint + manifest_block +
        "\nAPI CONTRACT :\n" + contract_text
    )

    config = _ARBITRATOR.pick("code-simple")
    
    messages = [{"role": "assistant" if t.get('role') == 'model' else t.get('role', 'user'), "content": t.get('content') or t.get('text', '')} for t in history[-12:]]
    messages.append({"role": "user", "content": f"{message}\n\nHTML ACTUEL:\n{html_context}"})
    
    tools = [{
        "functionDeclarations": [
            {"name": "read_reference", "parameters": {"type": "OBJECT", "properties": {"path": {"type": "STRING"}}, "required": ["path"]}},
            {"name": "query_knowledge_base", "parameters": {"type": "OBJECT", "properties": {"query": {"type": "STRING"}}, "required": ["query"]}}
        ]
    }]

    try:
        final_text = ""
        for _ in range(4):
            res = await asyncio.to_thread(_ARBITRATOR.dispatch, config, messages, system=system_instruction, tools=tools)
            if not res.get("success"): raise HTTPException(status_code=500, detail=res.get("error"))
            
            fc = res.get("function_call")
            if fc and fc['name'] == 'read_reference':
                messages.append({"role": "assistant", "content": f"outil: {fc['name']}"})
                messages.append({"role": "user", "content": _exec_read_reference(fc['args'].get('path'))})
            elif fc and fc['name'] == 'query_knowledge_base':
                messages.append({"role": "assistant", "content": f"outil: {fc['name']}"})
                messages.append({"role": "user", "content": await exec_query_knowledge_base(fc['args'].get('query'))})
            else:
                final_text = res.get("text", "")
                break

        explanation = final_text
        new_html = html_context
        if "---HTML---" in final_text:
            explanation, new_html = final_text.split("---HTML---", 1)
        
        return {
            "explanation": explanation.strip(),
            "html": new_html.strip(),
            "model": config["model"],
            "provider": config["provider"]
        }
    except Exception as e:
        logger.error(f"FRD Chat Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- ROUTES : KIMI JOBS ---
@app.post("/api/frd/kimi/start")
async def kimi_start(req: KimiStartRequest, bg_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())[:8]
    async with _KIMI_JOBS_LOCK:
        _KIMI_JOBS[job_id] = {"status": "pending"}
    bg_tasks.add_task(_run_kimi_job, job_id, req.instruction, req.html)
    return {"job_id": job_id}

@app.get("/api/frd/kimi/result/{job_id}", response_model=KimiResultResponse)
async def kimi_result(job_id: str):
    async with _KIMI_JOBS_LOCK:
        job = _KIMI_JOBS.get(job_id)
    if not job:
        return KimiResultResponse(status="not_found")
    return KimiResultResponse(**job)

# --- ROUTES : INFER LAYOUT ---
@app.post("/api/infer_layout")
async def infer_layout(body: Dict[str, Any]):
    organs = body.get('organs', [])
    mode = body.get('mode', 'heuristic')
    if mode == 'heuristic':
        return {"result": _infer_layout_heuristic(organs), "tier": "heuristic"}
    
    result, err = await _infer_layout_llm(organs, body.get('context', ''))
    if err:
        return {"result": _infer_layout_heuristic(organs), "tier": "heuristic_fallback", "error": err}
    return {"result": result, "tier": "llm"}

# --- ROUTES : ROOT & VIEWER ---

@app.get("/studio")
@app.get("/studio")
async def get_viewer():
    path = STATIC_DIR_PATH / "templates/viewer.html"
    if not path.exists(): raise HTTPException(status_code=404)
    content = path.read_text(encoding='utf-8')
    content = content.replace("{{custom_injection}}", load_custom_injection())
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content)

# --- ROUTES : GENOME ---
@app.get("/api/genome")
async def get_genome():
    return load_genome()

@app.post("/api/genome")
async def post_genome(genome: Dict[str, Any] = Body(...)):
    save_genome(genome)
    return {"status": "ok"}

# --- ROUTES : LAYOUT ENHANCED ---
@app.post("/api/layout")
async def post_layout(body: Dict[str, Any]):
    layout = load_layout()
    layout.update(body)
    save_layout(layout)
    return {"ok": True}

@app.post("/api/organ-move")
async def organ_move(body: Dict[str, Any]):
    oid = body.get('id')
    if not oid: raise HTTPException(status_code=400)
    ovr = _load_overrides()
    ovr.setdefault(oid, {}).update({"x": body.get('x'), "y": body.get('y')})
    _save_overrides(ovr)
    composer = BACKEND_PROD / "pipeline/07_composer.py"
    subprocess.run([sys.executable, str(composer)], cwd=str(ROOT_DIR))
    return {"ok": True}

@app.post("/api/comp-move")
async def comp_move(body: Dict[str, Any]):
    cid = body.get('id')
    if not cid: raise HTTPException(status_code=400)
    ovr = _load_overrides()
    ovr.setdefault(cid, {}).update({"x": body.get('x'), "y": body.get('y'), "s": body.get('s', 1)})
    _save_overrides(ovr)
    composer = BACKEND_PROD / "pipeline/07_composer.py"
    subprocess.run([sys.executable, str(composer)], cwd=str(ROOT_DIR))
    return {"ok": True}

@app.post("/api/accept")
async def accept_template():
    exports_dir = ROOT_DIR / 'exports'
    src = exports_dir / 'template_latest.svg'
    if src.exists():
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        dst = exports_dir / f'FINAL_template_{ts}.svg'
        shutil.copy2(src, dst)
        return {"saved": dst.name}
    return {"error": "No template found"}

# --- ROUTES : RETRO-GENOME (Mountés via router) ---

@app.post("/api/retro-genome/chat")
async def retro_chat(body: Dict[str, Any]):
    # Implémentation via SullivanArbitrator (Mission 87 simplifiée)
    # Dans le monolithe c'était du pur routing, ici on délégue à l'Arbitre
    config = _ARBITRATOR.pick("quick")
    res = await asyncio.to_thread(_ARBITRATOR.dispatch, config, [{"role":"user", "content":body.get('message','') or 'Analyze'}])
    return {"explanation": res.get("text", "")}

# --- ROUTES : BRS (BRAINSTORM) ---
@app.get("/api/brs/chat/{provider}")
async def brs_chat_sse(provider: str, session_id: str = Query(...), message: str = Query(...)):
    async def event_generator():
        async for chunk in brs_logic.sse_chat_generator(session_id, provider, message):
            yield chunk
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/brs/capture")
async def brs_capture(body: Dict[str, Any]):
    try:
        return await asyncio.to_thread(brs_logic.handle_capture, body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/brs/generate-prd")
async def brs_generate_prd(body: Dict[str, Any]):
    try:
        return await asyncio.to_thread(brs_logic.generate_prd, body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/brs/rank")
async def brs_rank(body: Dict[str, Any]):
    try:
        return await asyncio.to_thread(brs_logic.handle_rank, body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- ROUTES : RETRO-GENOME ENHANCED ---
@app.post("/api/retro-genome/approve")
async def retro_approve():
    _write_retro_status("done", "Rendu validé par le Directeur. Prêt pour export.")
    return {"status": "ok"}

@app.post("/api/retro-genome/export-zip")
async def retro_export_zip():
    from Backend.Prod.retro_genome.exporter_vanilla import export_as_zip
    html_path = get_project_exports_dir() / "reality.html"
    if not html_path.exists(): raise HTTPException(status_code=404, detail="reality.html not found")
    zip_path = await asyncio.to_thread(export_as_zip, "AetherFlow_Reality", html_path.read_text(encoding='utf-8'), get_project_exports_dir())
    return {"status": "ok", "zip_path": str(zip_path)}

@app.post("/api/retro-genome/export-manifest")
async def retro_export_manifest():
    from Backend.Prod.retro_genome.manifest_inferer import ManifestInferer
    html_path = get_project_exports_dir() / "reality.html"
    if not html_path.exists(): raise HTTPException(status_code=404, detail="reality.html not found")
    manifest = await asyncio.to_thread(asyncio.run, ManifestInferer.infer_from_html(html_path))
    out = get_project_manifest_path()
    ManifestInferer.save_manifest(manifest, out)
    return {"status": "ok", "manifest_path": str(out)}

@app.get("/api/frd/wire-audit")
async def wire_audit(request: Request, name: str = Query(...)):
    """Audit technique intent <-> endpoint pour le mode Wire v2."""
    analyzer = WireAnalyzer(ROOT_DIR)
    return analyzer.analyze_template(name, request.app.routes)

@app.get("/api/frd/wire-source")
async def get_wire_source(endpoint: str = Query(...)):
    """
    Parser AST Python pour extraire le handler correspondant à la route dans server_v3.py.
    """
    import ast
    try:
        source_path = Path(__file__)
        tree = ast.parse(source_path.read_text(encoding='utf-8'))
        
        handler_source = "# Handler non trouvé pour cet endpoint"
        lines_range = [0, 0]

        # Chercher le handler dans server_v3.py
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef) or isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    # On cherche @app.get("/path") ou @app.post("/path")
                    if isinstance(decorator, ast.Call) and \
                       isinstance(decorator.func, ast.Attribute) and \
                       decorator.func.attr in ("get", "post", "put", "delete", "patch") and \
                       len(decorator.args) > 0 and \
                       isinstance(decorator.args[0], ast.Constant) and \
                       decorator.args[0].value == endpoint:
                        
                        handler_source = ast.get_source_segment(source_path.read_text(encoding='utf-8'), node)
                        lines_range = [node.lineno, node.end_lineno]
                        return {"source": handler_source, "endpoint": endpoint, "lines": lines_range}

        # Si non trouvé dans app direct, peut-être dans un router? (Simplifié: on cherche juste dans server_v3.py)
        return {"source": handler_source, "endpoint": endpoint, "lines": lines_range}
    except Exception as e:
        logger.error(f"Error in wire-source: {e}")
        return {"source": f"# Erreur lors du parsing : {str(e)}", "endpoint": endpoint, "lines": [0,0]}


# --- ROUTES : MANIFEST MANAGEMENT (Mission 100-bis) ---
@app.post("/api/import/upload")
async def import_upload(file: UploadFile = File(...), filename: str = Form("")):
    """
    Mission 100-bis: Generic upload endpoint for multi-format imports.
    Supports: ZIP (Stitch), TSX/TS (React), HTML/CSS/JS files.
    """
    from datetime import datetime

    exports_dir = get_project_imports_dir()
    exports_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    safe_name = (filename or file.filename or "upload").replace(" ", "_").replace("/", "_")[:40]
    timestamp_str = datetime.now().strftime('%H%M%S')
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    ext = Path(file.filename).suffix.lower() if file.filename else ''
    stored_filename = f"IMPORT_{safe_name}_{timestamp_str}{ext}"
    
    file_path = exports_dir / stored_filename
    content = await file.read()
    file_path.write_bytes(content)
    
    # Update index.json
    index_path = exports_dir / "index.json"
    try:
        if index_path.exists():
            index_data = json.loads(index_path.read_text(encoding="utf-8"))
        else:
            index_data = {"imports": []}
        
        new_entry = {
            "id": f"{today_str}_{timestamp_str}_{safe_name}",
            "name": safe_name + ext,
            "timestamp": datetime.now().isoformat(),
            "file_path": f"{today_str}/{stored_filename}",
            "date": today_str,
            "type": ext.lstrip('.') if ext else 'unknown',
            "archetype_id": "multi_format_import",
            "archetype_label": "import multi-format"
        }
        index_data["imports"].insert(0, new_entry)
        index_data["imports"] = index_data["imports"][:50]
        index_path.write_text(json.dumps(index_data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        logger.error(f"[Import] Failed to update index.json: {e}")
    
    logger.info(f"[Import] File saved: {file_path}")
    
    global _NEW_IMPORTS_COUNT
    _NEW_IMPORTS_COUNT += 1
    
    return {"status": "ok", "file_saved": str(file_path)}

@app.get("/api/manifest/check")
async def manifest_check():
    """Check if manifest.json and design.md exist."""
    m_path = ROOT_DIR / 'manifest.json'
    d_path = ROOT_DIR / 'design.md'
    b_path = ROOT_DIR / 'backend.md'
    return {
        "exists": m_path.exists(),
        "stitch_ready": d_path.exists(),
        "backend_ready": b_path.exists()
    }

@app.get("/api/manifest/backend")
async def manifest_backend_get():
    """Get backend.md content."""
    b_path = get_active_project_path() / 'backend.md'
    if not b_path.exists():
        return {"content": "# HoméOS Backend Manifest\n\n*Not initialized*"}
    return {"content": b_path.read_text(encoding='utf-8')}

@app.put("/api/manifest/backend")
async def manifest_backend_put(data: Dict[str, str]):
    """Update backend.md content."""
    b_path = get_active_project_path() / 'backend.md'
    content = data.get('content', '')
    b_path.write_text(content, encoding='utf-8')
    return {"ok": True}

@app.post("/api/manifest/import-stitch")
async def manifest_import_stitch():
    """Parse design.md and sync with backend.md."""
    d_path = get_active_project_path() / 'design.md'
    b_path = get_active_project_path() / 'backend.md'
    if not d_path.exists():
        raise HTTPException(status_code=404, detail="design.md not found in project")
    
    design_content = d_path.read_text(encoding='utf-8')
    
    # Simple Heuristic Parser for Stitch design.md
    components = []
    # Identify: ### Component[intent] or # intent: POST /api/...
    comp_matches = re.finditer(r'###\s+([\w\-]+)\[([\w\-]+)\]', design_content)
    intent_matches = re.finditer(r'-\s+Intent:\s+(GET|POST|PUT|DELETE)\s+([^\n\r]+)', design_content)
    
    findings = []
    for m in comp_matches:
        name, action = m.group(1), m.group(2)
        route = f"POST /api/{name.lower()}/{action.lower()}"
        findings.append(f"| {name}[{action}] | {route} | 🔴 Backlog |")
    
    for m in intent_matches:
        method, path = m.group(1), m.group(2).strip()
        findings.append(f"| Stitch Direct | {method} {path} | 🔴 Backlog |")

    # Generate Markdown Table
    table_content = "\n".join(findings)
    new_backend_md = f"""# HoméOS Backend Manifest

## 🗺️ Intent Map (Synchronisé depuis Stitch)
| Composant | Route API | Statut |
| :--- | :--- | :--- |
{table_content}

## 🧪 Tests & Qualité
- [ ] Vérifier la bijection sémantique avec Wire V5
- [ ] Valider les schémas JSON (Pydantic)
- [ ] Tester les timeouts Sullivan
"""
    
    # Merge strategy: If file exists, we'll try to keep manual notes (not implemented for complexity, but plan says override for now)
    b_path.write_text(new_backend_md, encoding='utf-8')
    
    return {"ok": True, "count": len(findings), "manifest": new_backend_md}

@app.get("/api/manifest/get")
async def manifest_get():
    """Get the current manifest.json content."""
    m_path = get_project_manifest_path()
    if not m_path.exists():
        raise HTTPException(status_code=404, detail="manifest.json not found in project")
    with open(m_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    return manifest

@app.post("/api/manifest/create")
async def manifest_create(data: Dict[str, Any]):
    """Create a new manifest.json with project metadata."""
    m_path = get_project_manifest_path()
    if m_path.exists():
        return {"ok": False, "error": "manifest.json already exists in project"}
    
    name = data.get('name', 'unnamed-project')
    author = data.get('author', 'unknown')
    description = data.get('description', '')
    
    manifest = {
        "name": name,
        "author": author,
        "description": description,
        "created_at": datetime.now().isoformat(),
        "version": "0.1.0",
        "elements": [],
        "intents": []
    }
    
    with open(m_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    logger.info(f"manifest.json created: {name} by {author}")
    return {"ok": True, "manifest": manifest}

@app.post("/api/manifest/patch")
async def manifest_patch(patch: Dict[str, Any]):
    m_path = get_project_manifest_path()
    if not m_path.exists(): raise HTTPException(status_code=404)
    with open(m_path, 'r', encoding='utf-8') as f: manifest = json.load(f)
    if 'elements' in patch:
        for p_el in patch['elements']:
            for el in manifest.get('elements', []):
                if el.get('id') == p_el.get('id'): el.update(p_el); break
    with open(m_path, 'w', encoding='utf-8') as f: json.dump(manifest, f, indent=2, ensure_ascii=False)
    return {"ok": True}

@app.get("/bkd-frd")
async def get_bkd_frd():
    path = STATIC_DIR_PATH / "templates/bkd_frd.html"
    if not path.exists(): raise HTTPException(status_code=404)
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=path.read_text(encoding='utf-8'))

@app.get("/brainstorm")
async def get_brainstorm():
    path = STATIC_DIR_PATH / "templates/brainstorm_war_room_tw.html"
    if not path.exists(): raise HTTPException(status_code=404)
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=path.read_text(encoding='utf-8'))

@app.get("/brainstorm-alt")
async def get_brainstorm_alt():
    path = STATIC_DIR_PATH / "templates/brainstorm_alt.html"
    if not path.exists(): raise HTTPException(status_code=404)
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=path.read_text(encoding='utf-8'))

@app.get("/intent-viewer")
async def get_intent_viewer():
    path = STATIC_DIR_PATH / "templates/intent_viewer.html"
    if not path.exists(): raise HTTPException(status_code=404)
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=path.read_text(encoding='utf-8'))

@app.post("/api/preview/run")
async def preview_run(body: Dict[str, str]):
    """Save current HTML to a temporary file for independent tab preview."""
    html = body.get('html', '')
    p_path = STATIC_DIR_PATH / "templates/_preview_tmp.html"
    p_path.write_text(html, encoding='utf-8')
    return {"ok": True, "url": "/api/preview/show"}

@app.get("/api/preview/show")
async def preview_show():
    """Serve the temporary preview file."""
    p_path = STATIC_DIR_PATH / "templates/_preview_tmp.html"
    if not p_path.exists():
        return HTMLResponse(content="<h1>Aucun aperçu généré</h1>", status_code=404)
    
    content = p_path.read_text(encoding='utf-8')
    return HTMLResponse(content=content, headers={"Cache-Control": "no-store"})

@app.get("/")
async def get_root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/landing")

@app.get("/landing")
async def get_landing():
    path = STATIC_DIR_PATH / "templates/landing.html"
    if not path.exists(): raise HTTPException(status_code=404)
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=path.read_text(encoding='utf-8'))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9998)
