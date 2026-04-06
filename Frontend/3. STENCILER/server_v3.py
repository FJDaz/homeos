#!/usr/bin/env python3
"""
AetherFlow Server V3 - FastAPI Foundation
Mission 85: BKD Routes & Sullivan Pulse
Mission 118: Forge Tailwind AI (Updated 2026-03-31)
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
import zipfile
import io
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Query, Body, Request, UploadFile, File, BackgroundTasks, Form
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from bs4 import BeautifulSoup
import lxml

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
for p in [str(ROOT_DIR), str(BACKEND_PROD), str(CWD)]:
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
    from Backend.Prod.retro_genome import brainstorm_logic as cadrage_logic
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

def get_manifest_context(project_id: str):
    """Mission 181: Protocole Sullivan : Manifeste-Driven Identity."""
    try:
        if project_id == "active":
            project_id = get_active_project_id()
        manifest_path = PROJECTS_DIR / project_id / "manifest.json"
        if not manifest_path.exists():
            return "ALERTE : manifeste absent. anatomie non déclarée. rejoignez le mode CADRAGE pour initialiser cet organe."
        
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
            
        return f"""
MANIFESTE DU PROJET (SOURCE DE VÉRITÉ) :
---
ARCHETYPE : {manifest.get('archetype', 'non défini')}
ANATOMIE : {', '.join(manifest.get('anatomy', []))}
DESIGN TOKENS : {json.dumps(manifest.get('design_tokens', {}))}
WIRES (CÂBLAGE) : {len(manifest.get('wires', []))} actifs
---
"""
    except Exception as e:
        logger.error(f"Failed to load manifest context: {e}")
        return "ALERTE : Échec du chargement du manifeste."

# --- PYDANTIC MODELS ---
# --- MISSION 187 : ID ENGINE ---
import re, unicodedata

def slugify(text: str, max_len: int = 30) -> str:
    # Mission 187: Priorité à l'intelligibilité
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode()
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[\s_]+', '-', text)
    return text[:max_len].rstrip('-')

TAG_PREFIXES = {
    'button': 'btn', 'a': 'lnk', 'input': 'inp', 'form': 'frm',
    'select': 'sel', 'summary': 'tog', 'textarea': 'inp',
    'header': 'hdr', 'footer': 'ftr', 'nav': 'nav', 'section': 'sec'
}

def ensure_ids(html: str) -> str:
    """Mission 187: Injecte ou renomme les IDs pour qu'ils soient exploitables."""
    soup = BeautifulSoup(html, 'html.parser')
    counters = {}
    
    # Sélecteurs interactifs et structurants
    targets = soup.find_all(['button', 'a', 'input', 'form', 'select', 'summary', 'textarea', 'header', 'footer', 'nav', 'section', 'h1', 'h2', 'h3'])
    
    for el in targets:
        current_id = el.get('id', '')
        # Si l'ID est générique ou absent, on le remplace/génère
        is_generic = not current_id or re.match(r'^(el|div|section|block|id|tmp|gen)-\d+$', current_id) or len(current_id) < 3
        
        if is_generic:
            prefix = TAG_PREFIXES.get(el.name, 'el')
            # Extraire du texte, placeholder ou aria-label
            raw_text = el.get_text(strip=True)[:40] or el.get('placeholder', '') or el.get('aria-label', '') or el.get('name', '')
            
            if raw_text:
                slug = slugify(raw_text)
                new_id = f"{prefix}-{slug}" if slug else f"{prefix}-{counters.get(prefix, 0)+1}"
            else:
                counters[prefix] = counters.get(prefix, 0) + 1
                new_id = f"{prefix}-{counters[prefix]}"
            
            # Gestion des doublons
            base_id = new_id
            c = 1
            while soup.find(id=new_id):
                new_id = f"{base_id}-{c}"
                c += 1
            
            el['id'] = new_id
            logger.info(f"Ensured ID: {current_id} -> {new_id}")
            
    return str(soup)

class ProjectInfo(BaseModel):
    id: str
    name: str
    path: str
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
    archetype: Optional[str] = None
    design_tokens: Optional[Dict] = None
    screens: Optional[List] = None
    wires: Optional[List] = None
    pending_intents: Optional[List] = None

class BKDFileListItem(BaseModel):
    name: str
    path: str
    size: Optional[int] = None
    modified: Optional[str] = None

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

# --- MISSION 116 : CURRENT FRD CONTEXT ---
_CURRENT_FRD_CONTEXT = {"type": None, "id": None, "name": None, "html_template": None}
_NEW_IMPORTS_COUNT = 0

class CurrentFileRequest(BaseModel):
    type: str
    id: Optional[str] = None
    name: Optional[str] = None
    html_template: Optional[str] = None

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
        elif "Bold" in sect: tokens["typography"]["headline_weight"] = "700"

    # 3. Formes & Structure
    shape_match = re.search(r'### Formes & Structure([\s\S]*?)(?:###|$)', content)
    if shape_match:
        sect = shape_match.group(1)
        br_match = re.search(r'Border Radius\*\*.*?`([^`]+)`', sect)
        if br_match: tokens["shape"]["border_radius"] = br_match.group(1)

    tokens["source"] = "homeos_design_md"
    return tokens

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

# --- MISSION 116 : CURRENT FRD CONTEXT ROUTES ---
@app.post("/api/frd/set-current")
async def set_current_frd_context(req: CurrentFileRequest):
    global _CURRENT_FRD_CONTEXT
    _CURRENT_FRD_CONTEXT = {
        "type": req.type,
        "id": req.id,
        "name": req.name,
        "html_template": req.html_template
    }
    logger.info(f"Current FRD context set: {_CURRENT_FRD_CONTEXT}")
    return {"status": "ok", "context": _CURRENT_FRD_CONTEXT}

@app.get("/api/frd/current")
async def get_current_frd_context():
    return _CURRENT_FRD_CONTEXT

@app.get("/api/frd/manifest")
async def get_frd_manifest(import_id: str = Query(...)):
    """
    Détection de manifeste pour le routage intelligent (Mission 146).
    Recherche manifest_{import_id}.json dans le dossier manifests du projet actif.
    """
    manifest_dir = get_active_project_path() / "manifests"
    manifest_path = manifest_dir / f"manifest_{import_id}.json"
    
    if manifest_path.exists():
        try:
            content = json.loads(manifest_path.read_text(encoding='utf-8'))
            return {"exists": True, "manifest": content}
        except Exception as e:
            logger.error(f"Erreur lecture manifeste {import_id} : {e}")
            return {"exists": False, "error": f"Format invalide : {e}"}
    
    return {"exists": False}

@app.post("/api/frd/validate-wire")
async def validate_wire(request: Request):
    body = await request.json()
    import_id = body.get("import_id", "")
    manifest_dir = get_active_project_path() / "manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    path = manifest_dir / f"manifest_{import_id}.json"
    existing = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    existing["validated"] = True
    path.write_text(json.dumps(existing, ensure_ascii=False, indent=2))
    return {"status": "ok"}

@app.get("/api/frd/current")
async def get_frd_current():
    """Retourne l'import/template actuellement chargé dans l'éditeur."""
    from bkd_service import get_active_project_id
    p_path = PROJECTS_DIR / get_active_project_id()
    f = p_path / "current_frd.json"
    if f.exists():
        return json.loads(f.read_text(encoding='utf-8'))
    return {"status": "none"}

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
async def get_stenciler_redirect():
    """Mission 168: Redirect ancien /stenciler → /workspace (architecture hexagonale M156)."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/workspace", status_code=301)

@app.get("/stenciler_v3")
async def get_stenciler_v3_redirect():
    """Mission 168: Redirect ancien /stenciler_v3 → /workspace."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/workspace", status_code=301)

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

@app.get("/workspace")
async def get_workspace_editor():
    """Mission 127: Unified Workspace Canvas"""
    path = STATIC_DIR_PATH / "templates/workspace.html"
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

# --- CACHE DES FONTES SYSTÈME (Optimisation M148) ---
_FONT_PATH_CACHE = {}

def _warm_up_font_cache():
    """Scanne les dossiers système une seule fois au démarrage."""
    font_dirs = [Path("/System/Library/Fonts"), Path("/Library/Fonts"), Path.home() / "Library/Fonts"]
    ext = {'.ttf', '.otf', '.ttc'}
    for d in font_dirs:
        if not d.exists(): continue
        for f in d.rglob('*'):
            if f.suffix.lower() in ext:
                _FONT_PATH_CACHE[f.stem.lower()] = f

_warm_up_font_cache()

@app.get("/api/sullivan/fonts")
async def sullivan_list_fonts():
    """Liste les fontes uploadées dans /static/fonts/."""
    from Backend.Prod.sullivan.font_webgen import FontWebGen
    webgen = FontWebGen()
    fonts = webgen.list_fonts()
    return {"fonts": fonts}

@app.get("/api/sullivan/system-fonts")
async def sullivan_system_fonts():
    """Liste les familles de fontes installées sur le poste via le cache."""
    return {"families": sorted(_FONT_PATH_CACHE.keys())}

@app.post("/api/sullivan/generate-webfont")
async def sullivan_generate_webfont(body: Dict[str, Any]):
    """Génère une webfont depuis les fontes système Mac à la volée (Mission 148)."""
    font_name = body.get('font_name')
    if not font_name:
        raise HTTPException(status_code=400, detail="font_name is required")
    
    from Backend.Prod.sullivan.font_webgen import FontWebGen
    webgen = FontWebGen()
    
    # 1. Vérifier si déjà généré (basé sur le slug)
    slug = re.sub(r'[^\w\s-]', '', font_name.lower())
    slug = re.sub(r'[\s_]+', '-', slug).strip('-')
    meta_path = Path(webgen.output_dir) / slug / "metadata.json"
    
    if meta_path.exists():
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass

    # 2. Chercher le fichier via le cache optimisé
    found_path = _FONT_PATH_CACHE.get(font_name.lower())
    
    # Recherche partielle si exact échoue dans le cache
    if not found_path:
        for name, path in _FONT_PATH_CACHE.items():
            if font_name.lower() in name:
                found_path = path
                break

    if not found_path:
        return {"status": "not_found", "message": f"Source pour '{font_name}' introuvable."}

    # 3. Générer via FontWebGen, avec fallback conversion directe si subsetting échoue
    def _convert_font(path, name, out_dir):
        from fontTools.ttLib import TTFont as _TTFont
        _slug = re.sub(r'[^\w\s-]', '', name.lower())
        _slug = re.sub(r'[\s_]+', '-', _slug).strip('-')
        font_out = out_dir / _slug
        font_out.mkdir(parents=True, exist_ok=True)
        woff2_path = font_out / f"{_slug}.woff2"
        font = _TTFont(str(path))
        font.flavor = "woff2"
        font.save(str(woff2_path))
        css = f"@font-face {{ font-family: '{name}'; src: url('/static/fonts/{_slug}/{_slug}.woff2') format('woff2'); font-display: swap; }}"
        return {"status": "ok", "css": css, "slug": _slug}

    try:
        result = await asyncio.to_thread(webgen.generate, str(found_path), {"family_name": font_name})
        result["status"] = "ok"
        return result
    except Exception as e:
        logger.warning(f"FontWebGen failed ({e}), falling back to direct conversion")
        try:
            out_dir = Path(webgen.output_dir)
            result = await asyncio.to_thread(_convert_font, found_path, font_name, out_dir)
            return result
        except Exception as e2:
            logger.error(f"Direct font conversion failed: {e2}")
            return {"status": "error", "message": str(e2)}

@app.delete("/api/sullivan/fonts/{slug}")
async def sullivan_delete_font(slug: str):
    """Supprime une fonte et son répertoire."""
    from Backend.Prod.sullivan.font_webgen import FontWebGen
    webgen = FontWebGen()
    success = webgen.delete_font(slug)
    if success:
        return {"status": "ok", "deleted": slug}
    raise HTTPException(status_code=404, detail=f"Font '{slug}' not found")


class SullivanChatRequest(BaseModel):
    message: str
    project_id: Optional[str] = "active"
    mode: str = "construct"
    screen_html: Optional[str] = None
    canvas_screens: Optional[list] = None  # [{ id, title, html }]
    selected_element: Optional[dict] = None  # { selector, tag, html } — M154
    wires: Optional[List[Dict]] = None  # [{ trigger, target, event }] — M161


@app.post("/api/sullivan/chat")
async def sullivan_chat(req: SullivanChatRequest):
    """
    Chat Sullivan — répond à un message utilisateur selon le mode courant.
    Mission 142 + 152 : Support multi-screens et Design System (DESIGN.md).
    """
    try:
        from Backend.Prod.retro_genome.routes import _get_gemini_client
        client = _get_gemini_client()
    except Exception as e:
        logger.error(f"GeminiClient init failed: {e}")
        raise HTTPException(status_code=500, detail="LLM unavailable")

    mode_context = {
        "construct": "Tu es Sullivan, un assistant de design UI/UX et AetherFlow Architect. Aide l'utilisateur à concevoir et forger ses écrans.",
        "inspect": "Tu es Sullivan, inspecteur UI/UX. Analyse le design courant pour identifier des problèmes ergonomiques ou d'accessibilité.",
        "preview": "Tu es Sullivan, critique design. Commente le rendu final de l'interface.",
        "front-dev": "Tu es Sullivan, Front-End Engineer & Expert GSAP. Ton rôle est de transformer les intentions de design et les connexions (Wires) en animations fluides et professionnelles utilisant la bibliothèque GSAP.",
    }
    
    base_system = mode_context.get(req.mode, mode_context["construct"])
    
    # --- MISSION 181 : PROTOCOLE SULLIVAN (MANIFESTE) ---
    project_id = req.project_id or "active"
    manifest_context = get_manifest_context(project_id)
    
    base_system += f"\n\n{manifest_context}"
    
    if "CADRAGE" in manifest_context:
        # Fallback : Inviter au cadrage si manifest absent
        base_system += "\nTu ne peux pas effectuer de modifications majeures. Invite poliment l'utilisateur à initialiser son projet via le mode CADRAGE."

    # --- MISSION 152 : DESIGN SYSTEM (DESIGN.md) ---
    design_md_block = ""
    try:
        design_path = get_active_project_path() / "DESIGN.md"
        if not design_path.exists():
            design_path = STATIC_DIR_PATH / "templates" / "DESIGN.md"
        if design_path.exists():
            design_md_block = f"""
DESIGN SYSTEM DU PROJET (RÉFÉRENCE) :
---
{design_path.read_text(encoding='utf-8')[:4000]}
---
Utilise ces tokens et ces règles pour garantir la cohérence visuelle si l'utilisateur demande une modification.
"""
    except Exception: pass

    # --- MISSION 181 : MANIFEST PROJET (IDENTITÉ & ORGANES) ---
    manifest_block = ""
    try:
        manifest_path = PROJECTS_DIR / project_id / "manifest.json"
        if manifest_path.exists():
            manifest_data = json.loads(manifest_path.read_text(encoding='utf-8'))
            manifest_block = f"""
MANIFEST DU PROJET (SOURCE DE VÉRITÉ) :
---
Nom : {manifest_data.get('name', '?')}
Description : {manifest_data.get('description', '?')}
Archétype : {manifest_data.get('archetype', '?')}
Règles design : {json.dumps(manifest_data.get('design_tokens', {}), ensure_ascii=False)}
Organes déclarés : {json.dumps([o for s in manifest_data.get('screens', []) for c in s.get('corps', []) for o in c.get('organes', [])], ensure_ascii=False)[:2000]}
---
Respecte strictement ces règles de design. Chaque organe déclaré doit avoir un équivalent dans le HTML.
"""
    except Exception: pass

    # --- MISSION 142 : ÉCRAN ACTIF (MODIFIABLE) ---
    context_html_block = ""
    if req.screen_html:
        context_html_block = f"""
CODE SOURCE HTML DE L'ÉCRAN ACTIF (MODIFIABLE) :
---
{req.screen_html}
---
Si l'utilisateur demande une modification visuelle, une correction ou un ajout :
1. Analyse son intention.
2. Modifie le code source HTML ci-dessus pour appliquer le changement.
3. Retourne TOUT le document HTML5 mis à jour dans le champ "---HTML---" de ta réponse.
4. Explique ce que tu as fait dans le bloc "---EXPLANATION---".
"""

    # --- MISSION 154 : ÉLÉMENT SÉLECTIONNÉ (FOCUS) ---
    selected_block = ""
    if req.selected_element:
        sel = req.selected_element
        selected_block = f"""
ÉLÉMENT ACTUELLEMENT SÉLECTIONNÉ PAR L'UTILISATEUR (selector: {sel.get('selector','?')}) :
---
{sel.get('html','')[:2000]}
---
L'utilisateur parle probablement de cet élément spécifiquement. Si tu modifies le screen, cible en priorité cet élément et ses descendants directs.
"""

    # --- MISSION 142 : AUTRES ÉCRANS ---
    other_screens_block = ""
    if req.canvas_screens:
        parts = []
        for s in req.canvas_screens:
            parts.append(f"SCREEN [{s.get('id','?')}] TITLE: {s.get('title','Sans Titre')}\nHTML:\n{s.get('html','')[:1000]}")
        parts_joined = "\n\n---\n\n".join(parts)
        other_screens_block = f"""
AUTRES ÉCRANS PRÉSENTS SUR LE CANVAS (LECTURE SEULE - RÉFÉRENCE) :
---
{parts_joined}
---
Ces écrans sont fournis pour comparaison et contexte. Tu ne peux pas les modifier directement, mais tu dois t'en inspirer pour la cohérence.
"""

    # --- MISSION 161 : WIRES & GSAP ---
    wires_block = ""
    if req.wires:
        wires_json = json.dumps(req.wires, indent=2)
        wires_block = f"""
CONNEXIONS VISUELLES (WIRES) DÉTECTÉES :
---
{wires_json}
---
Utilise ces paires Trigger/Target pour générer des animations GSAP intelligentes.
Par exemple, si Trigger='button' et Target='menu', anime le menu lors de l'interaction sur le bouton.
"""

    system_prompt = f"""
{base_system}

{manifest_block}

{design_md_block}

{selected_block}

{context_html_block}

{other_screens_block}

{wires_block}

RÈGLES DE RÉPONSE :
Réponds avec ce format exact (trois blocs séparés par des délimiteurs) :

---EXPLANATION---
Ton explication courte ici (1-3 phrases).
---HTML---
<!DOCTYPE html>... (le HTML complet de l'ÉCRAN ACTIF uniquement, avec injection automatique de <script type="module" src="/api/projects/active/logic.js"></script> si besoin)
---LOGIC---
// Ton code GSAP ici. Utilise des imports ESM pour GSAP (ex: import gsap from "https://esm.sh/gsap").
---END---

Pas de prose, pas de markdown, pas de JSON.
"""

    try:
        result = await client.generate(
            prompt=f"{system_prompt}\n\nMessage utilisateur : {req.message}",
            max_tokens=16384
        )

        if not result.success:
            return {"explanation": "Désolé, je rencontre une difficulté technique.", "html": None}

        raw_text = result.code.strip()

        # Parsing par délimiteurs (Mission 161: Support ---LOGIC---)
        explanation = None
        html = None
        logic_js = None
        
        if "---EXPLANATION---" in raw_text:
            try:
                explanation = raw_text.split("---EXPLANATION---")[1].split("---")[0].strip()
                
                if "---HTML---" in raw_text:
                    html_part = raw_text.split("---HTML---")[1].split("---")[0].strip()
                    html = None if html_part.upper() == "NULL" or not html_part.startswith("<") else html_part
                
                if "---LOGIC---" in raw_text:
                    logic_part = raw_text.split("---LOGIC---")[1].split("---")[0].strip()
                    logic_js = None if logic_part.upper() == "NULL" else logic_part
                    
            except Exception as e:
                logger.error(f"Sullivan parsing error: {e}")
                explanation = raw_text
        else:
            explanation = raw_text

        # Sauvegarde de la logique dans logic.js (Mission 161)
        if logic_js:
            try:
                p_path = get_active_project_path()
                if p_path:
                    (p_path / "logic.js").write_text(logic_js, encoding='utf-8')
                    logger.info(f"Sullivan: GSAP logic saved to {p_path}/logic.js")
            except Exception as e:
                logger.error(f"Failed to save logic.js: {e}")
        
        return {"explanation": explanation, "html": html, "logic_js": logic_js}

    except Exception as e:
        logger.error(f"Sullivan chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- MISSION 128 : DESIGN SYSTEM BRIDGE ---
@app.post("/api/project/import-design-md")
async def import_design_md(file: UploadFile = File(...)):
    """Parse et importe un DESIGN.md pour le projet actif."""
    content = (await file.read()).decode("utf-8")
    tokens = parse_design_md(content)
    
    # Sauvegarde locale au projet
    token_path = get_project_exports_dir() / "design_tokens.json"
    token_path.write_text(json.dumps(tokens, indent=2), encoding="utf-8")
    
    logger.info(f"Design tokens imported for project {get_active_project_id()}")
    return {"status": "ok", "tokens": tokens}

@app.get("/api/project/design-tokens")
async def get_design_tokens():
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

# --- ROUTES : PROJECTS (Mission 111 + 162) ---

ACTIVE_PROJECT_FILE = ROOT_DIR / "active_project.json"

def get_active_project_id() -> Optional[str]:
    """Retourne l'ID du projet actif depuis le fichier active_project.json."""
    if ACTIVE_PROJECT_FILE.exists():
        try:
            data = json.loads(ACTIVE_PROJECT_FILE.read_text(encoding='utf-8'))
            return data.get("active_id")
        except:
            return None
    return None

def set_active_project_id(project_id: str):
    """Sauvegarde l'ID du projet actif dans active_project.json."""
    ACTIVE_PROJECT_FILE.write_text(json.dumps({"active_id": project_id}, ensure_ascii=False), encoding='utf-8')

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

@app.get("/api/projects/active", response_model=ProjectInfo)
async def get_active_project_route():
    active_id = get_active_project_id()
    if not active_id:
        raise HTTPException(status_code=404, detail="No active project")
    with sqlite3.connect(str(PROJECTS_DB_PATH)) as conn:
        row = conn.execute("SELECT id, name, path, created_at, last_opened FROM projects WHERE id=?",
                           (active_id,)).fetchone()
        if not row: raise HTTPException(status_code=404, detail="Active project not found")
        return ProjectInfo(id=row[0], name=row[1], path=row[2], created_at=row[3], last_opened=row[4], active=True)

@app.post("/api/projects/activate")
async def activate_project(req: ProjectActivateRequest):
    with sqlite3.connect(str(PROJECTS_DB_PATH)) as conn:
        exists = conn.execute("SELECT id FROM projects WHERE id=?", (req.id,)).fetchone()
        if not exists: raise HTTPException(status_code=404, detail="Project not found")
        conn.execute("UPDATE projects SET last_opened=datetime('now') WHERE id=?", (req.id,))

    set_active_project_id(req.id)
    logger.info(f"Project activated: {get_active_project_id()}")
    return {"status": "ok", "active_id": get_active_project_id()}

@app.get("/api/projects/active/logic.js")
async def get_active_logic_js():
    """Mission 161: Sert le fichier logic.js du projet actif."""
    p_path = get_active_project_path()
    f_path = p_path / "logic.js"
    if not f_path.exists():
        return HTMLResponse(content="// logic.js not found", media_type="application/javascript")
    return FileResponse(f_path, media_type="application/javascript")

@app.get("/api/projects", response_model=List[ProjectInfo])
async def list_all_projects_route():
    active_id = get_active_project_id()
    with sqlite3.connect(str(PROJECTS_DB_PATH)) as conn:
        rows = conn.execute("SELECT id, name, path, created_at, last_opened FROM projects ORDER BY last_opened DESC").fetchall()
        return [ProjectInfo(id=r[0], name=r[1], path=r[2], created_at=r[3], last_opened=r[4], active=(r[0] == active_id)) for r in rows]

@app.post("/api/projects/create")
async def create_project_route(req: ProjectCreateRequest):
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

    with sqlite3.connect(str(PROJECTS_DB_PATH)) as conn:
        try:
            conn.execute("INSERT INTO projects (id, name, path) VALUES (?,?,?)",
                         (pid, req.name, str(p_path)))
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Project ID already exists")

    return {"status": "ok", "id": pid}

@app.delete("/api/projects/{project_id}")
async def delete_project_route(project_id: str):
    """Mission 162: Supprime un projet (dossier + DB entry)."""
    p_path = PROJECTS_DIR / project_id
    if not p_path.exists():
        raise HTTPException(status_code=404, detail="Project folder not found")

    # Supprimer le dossier
    shutil.rmtree(p_path)

    # Supprimer de la DB
    with sqlite3.connect(str(PROJECTS_DB_PATH)) as conn:
        conn.execute('DELETE FROM projects WHERE id=?', (project_id,))

    # Si c'était le projet actif, reset
    if get_active_project_id() == project_id:
        ACTIVE_PROJECT_FILE.unlink(missing_ok=True)

    logger.info(f"Project deleted: {project_id}")
    return {"status": "ok", "deleted": project_id}

@app.get("/api/projects/{project_id}/manifest")
async def get_project_manifest_route(project_id: str):
    """Retourne le manifest.json d'un projet."""
    manifest = get_project_manifest(project_id)
    if not manifest:
        raise HTTPException(status_code=404, detail="Manifest not found")
    return manifest

@app.put("/api/projects/{project_id}/manifest")
async def update_project_manifest_route(project_id: str, manifest: ProjectManifest):
    """Met à jour le manifest.json d'un projet."""
    p_path = PROJECTS_DIR / project_id
    if not p_path.exists():
        raise HTTPException(status_code=404, detail="Project not found")

    manifest_data = manifest.model_dump()
    save_project_manifest(project_id, manifest_data)
    return {"status": "ok", "manifest": manifest_data}

@app.post("/api/projects/{project_id}/wires")
async def add_project_wire_route(project_id: str, wire: dict = Body(...)):
    """Mission 160: Ajoute un 'wire' (câblage visuel) au projet."""
    manifest = get_project_manifest(project_id)
    if "wires" not in manifest: manifest["wires"] = []
    
    # Éviter les doublons exacts
    exists = any(w for w in manifest["wires"] if w.get("trigger") == wire.get("trigger") and w.get("target") == wire.get("target"))
    if not exists:
        manifest["wires"].append(wire)
        save_project_manifest(project_id, manifest)
    
    return {"status": "ok", "wires_count": len(manifest["wires"])}

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
@app.get("/api/frd/export-zip")
async def export_zip(import_id: str):
    """
    Export a screen as a ZIP containing HTML + fonts.
    Mission 144
    """
    try:
        p_path = get_active_project_path()
        imports_dir = p_path / "imports"
        index_path = imports_dir / "index.json"
        
        if not index_path.exists():
            raise HTTPException(status_code=404, detail="index.json not found")
            
        index_data = json.loads(index_path.read_text(encoding="utf-8"))
        entry = next((i for i in index_data.get("imports", []) if i["id"] == import_id), None)
        
        if not entry:
            raise HTTPException(status_code=404, detail=f"Import {import_id} not found")
            
        html_template = entry.get("html_template")
        if not html_template:
            raise HTTPException(status_code=400, detail="Import has no forged template yet.")
            
        # 1. Read HTML
        templates_dir = STATIC_DIR_PATH / "templates"
        html_path = templates_dir / html_template
        if not html_path.exists():
             raise HTTPException(status_code=404, detail=f"Template {html_template} not found")
        
        # 2. Prepare ZIP in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            # Write HTML as index.html for portability
            zip_file.writestr("index.html", html_path.read_text(encoding="utf-8"))
            
            # Write Fonts from /static/fonts/
            fonts_dir = STATIC_DIR_PATH / "fonts"
            if fonts_dir.exists():
                for font_file in fonts_dir.rglob("*"):
                    if font_file.is_file():
                        # We want the fonts to be in a /fonts folder in the ZIP
                        arcname = f"fonts/{font_file.relative_to(fonts_dir)}"
                        zip_file.write(font_file, arcname=arcname)
                        
        zip_buffer.seek(0)
        # Clean filename for attachment
        safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', entry["name"].split('.')[0])
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename=export_{safe_name}.zip"}
        )
        
    except Exception as e:
        logger.error(f"ZIP Export failed: {e}")
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/frd/file")
async def get_frd_file(name: str = Query(...), raw: int = Query(0)):
    if '/' in name or '..' in name:
        raise HTTPException(status_code=400, detail="Invalid filename")
    path = STATIC_DIR_PATH / "templates" / name
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    if raw:
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=path.read_text(encoding='utf-8'))
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
@app.get("/api/workspace/templates")
async def list_workspace_templates():
    """Mission 110: Liste les templates de base pour le workspace."""
    tpl_dir = STATIC_DIR_PATH / "templates"
    if not tpl_dir.exists(): return {"templates": []}
    
    # On filtre pour ne garder que les templates "nobles" (pas les imports ou tmp)
    files = []
    for f in tpl_dir.glob("*.html"):
        if f.name.startswith(("import_", "reality_", "_")): continue
        files.append({"name": f.name.replace(".html", ""), "tpl": f.name})
    
    return {"templates": sorted(files, key=lambda x: x["name"])}

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

# --- ROUTES : CADRAGE (EX-BRS) ---
@app.get("/api/cadrage/chat/{provider}")
async def cadrage_chat_sse(provider: str, session_id: str = Query(...), message: str = Query(...)):
    """SSE endpoint for multi-model chat in Cadrage."""
    from fastapi.responses import StreamingResponse
    async def generate():
        try:
            async for chunk in cadrage_logic.sse_chat_generator(session_id, provider, message):
                yield chunk
        except Exception as e:
            logger.error(f"Cadrage Chat SSE Error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/api/cadrage/capture")
async def cadrage_capture(body: Dict[str, Any]):
    try:
        return await asyncio.to_thread(cadrage_logic.handle_capture, body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cadrage/generate-prd")
async def cadrage_generate_prd(body: Dict[str, Any]):
    try:
        return await asyncio.to_thread(cadrage_logic.generate_prd, body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cadrage/rank")
async def cadrage_rank(body: Dict[str, Any]):
    try:
        return await asyncio.to_thread(cadrage_logic.handle_rank, body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cadrage")
async def get_cadrage():
    path = STATIC_DIR_PATH / "templates/cadrage_alt.html"
    if not path.exists(): raise HTTPException(status_code=404)
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=path.read_text(encoding='utf-8'))

@app.get("/cadrage-alt")
async def get_cadrage_alt():
    path = STATIC_DIR_PATH / "templates/cadrage_alt.html"
    if not path.exists(): raise HTTPException(status_code=404)
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=path.read_text(encoding='utf-8'))

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

        # Chercher le handler dans# server_v3.py — Force reload M118
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
    safe_name = (filename or file.filename or "upload").replace(" ", "_").replace("/", "_")[:128]
    timestamp_str = datetime.now().strftime('%H%M%S')
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    ext = Path(file.filename).suffix.lower() if file.filename else ''
    stored_filename = f"IMPORT_{safe_name}_{timestamp_str}{ext}"
    
    today_dir = exports_dir / today_str
    today_dir.mkdir(parents=True, exist_ok=True)
    file_path = today_dir / stored_filename
    
    content = await file.read()
    
    # MISSION 187 : Nettoyage & IDs sémantiques à l'import
    if ext == '.html':
        try:
            html_content = content.decode('utf-8')
            html_content = ensure_ids(html_content)
            content = html_content.encode('utf-8')
        except Exception as e:
            logger.error(f"Failed to ensure IDs during import: {e}")

    file_path.write_bytes(content)
    
    # Update index.json
    index_path = exports_dir / "index.json"
    try:
        if index_path.exists():
            index_data = json.loads(index_path.read_text(encoding="utf-8"))
        else:
            index_data = {"imports": []}
        
        # Pour les HTML uploadés : copier directement dans templates/ et setter html_template
        html_template_name = None
        if ext == '.html':
            templates_dir = STATIC_DIR_PATH / "templates"
            templates_dir.mkdir(parents=True, exist_ok=True)
            tpl_filename = f"import_{today_str}_{timestamp_str}_{safe_name}.html"
            tpl_path = templates_dir / tpl_filename
            tpl_path.write_bytes(content)
            html_template_name = tpl_filename

            # Mission 151: Auto-generated Wire Manifest (Static DOM parsing)
            try:
                from Backend.Prod.retro_genome.archetype_detector import ArchetypeDetector
                
                # Inférence statique (No browser)
                soup = BeautifulSoup(content, 'lxml') or BeautifulSoup(content, 'html.parser')
                
                # Extraction des éléments structurants
                elements = []
                items = soup.find_all(['section', 'nav', 'header', 'footer', 'div', 'button', 'h1', 'h2', 'h3', 'p', 'input'])
                
                for idx, el in enumerate(items[:35]): # Limite 35
                    el_id = el.get('id') or el.get('data-id') or f"el_{idx}"
                    text = el.get_text(strip=True)[:50]
                    role = el.get('data-role') or (el.get('data-af-region') if el.has_attr('data-af-region') else el.name)
                    
                    elements.append({
                        "id": el_id,
                        "name": el.name.upper(),
                        "role": role,
                        "text": text,
                        "visual_hint": el.get('class', [""])[0] if el.get('class') else ""
                    })

                # Archetype Detection
                detector = ArchetypeDetector()
                archetype = detector.detect({"elements": elements})
                
                # Mapping Components (WsWire.js compatible)
                components = []
                for idx, el in enumerate(elements):
                    components.append({
                        "id": el["id"],
                        "name": el["name"],
                        "role": el["role"],
                        "z_index": idx + 1,
                        "text": el["text"]
                    })
                
                final_manifest = {
                    "import_id": f"{today_str}_{timestamp_str}_{safe_name}",
                    "archetype": archetype,
                    "components": components,
                    "screens": [{"id": "main", "name": "Main Screen", "components": components}],
                    "generated_at": datetime.now().isoformat(),
                    "source": "M151 Static Inference"
                }

                # Sauvegarde project-specific
                from bkd_service import get_active_project_path
                prj_path = get_active_project_path()
                if prj_path:
                    m_dir = prj_path / "manifests"
                    m_dir.mkdir(parents=True, exist_ok=True)
                    m_file = m_dir / f"manifest_{today_str}_{timestamp_str}_{safe_name}.json"
                    m_file.write_text(json.dumps(final_manifest, indent=2, ensure_ascii=False))
                    logger.info(f"✅ M151: Manifest generated statically for {tpl_filename}")
            except Exception as e:
                logger.error(f"❌ M151: Static inference failed: {e}")

        new_entry = {
            "id": f"{today_str}_{timestamp_str}_{safe_name}",
            "name": Path(safe_name).stem + ext,
            "timestamp": datetime.now().isoformat(),
            "file_path": f"{today_str}/{stored_filename}",
            "date": today_str,
            "type": ext.lstrip('.') if ext else 'unknown',
            "archetype_id": "multi_format_import",
            "archetype_label": "import multi-format",
            "html_template": html_template_name,
            "elements_count": 0
        }
        index_data["imports"].insert(0, new_entry)
        index_data["imports"] = index_data["imports"][:50]
        index_path.write_text(json.dumps(index_data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        logger.error(f"[Import] Failed to update index.json: {e}")

    logger.info(f"[Import] File saved: {file_path}")

    global _NEW_IMPORTS_COUNT
    _NEW_IMPORTS_COUNT += 1

    return {"status": "ok", "import": new_entry}

@app.delete("/api/imports/{import_id}")
async def import_delete(import_id: str):
    """
    Mission 125: Suppression d'un import.
    Supprime l'entrée de index.json et les fichiers sur disque.
    """
    import unicodedata

    exports_dir = get_project_imports_dir()
    index_path = exports_dir / "index.json"
    
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Index not found")
        
    try:
        index_data = json.loads(index_path.read_text(encoding="utf-8"))
        imports = index_data.get("imports", [])
        
        # Support NFC normalization for IDs
        req_id_nfc = unicodedata.normalize('NFC', import_id)
        
        target_index = -1
        target_entry = None
        
        for i, entry in enumerate(imports):
            if unicodedata.normalize('NFC', entry.get("id", "")) == req_id_nfc:
                target_index = i
                target_entry = entry
                break
        
        if target_index == -1:
            raise HTTPException(status_code=404, detail=f"Import {import_id} not found")
            
        # Suppression des fichiers physiques
        paths_to_check = [target_entry.get("svg_path"), target_entry.get("file_path")]
        for rel_p in paths_to_check:
            if rel_p:
                abs_p = exports_dir / rel_p
                if abs_p.exists():
                    try:
                        abs_p.unlink()
                        logger.info(f"[Import] Deleted physical file: {abs_p}")
                    except Exception as e:
                        logger.warning(f"[Import] Failed to unlink {abs_p}: {e}")
        
        # Retrait de l'index
        imports.pop(target_index)
        index_data["imports"] = imports
        index_path.write_text(json.dumps(index_data, indent=2, ensure_ascii=False), encoding="utf-8")
        
        logger.info(f"[Import] Successfully deleted import entry: {import_id}")
        return {"status": "deleted", "id": import_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Import] Deletion crash: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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

class GraftRequest(BaseModel):
    filename: str
    selector: str
    html_content: str

@app.get("/api/workspace/tokens")
async def get_workspace_tokens():
    """
    Mission 159 : Design System Intendant.
    Retourne les jetons de design du projet actif (ou HoméOS par défaut).
    """
    try:
        project_path = get_active_project_path()
        tokens_path = project_path / "design_tokens.json"
        
        if tokens_path.exists():
            with open(tokens_path, "r", encoding="utf-8") as f:
                return json.load(f)
        
        # Fallback HoméOS Standard
        return {
          "fonts": ["Source Sans 3", "Geist", "Inter", "Roboto"],
          "colors": {
            "palette": ["#A3CD54", "#1a1a1a", "#f5f5f5", "#ffffff", "#64748b"],
            "allowCustomColors": True
          },
          "effects": {
            "allowShadows": True,
            "allowBorders": True,
            "allowRadius": True,
            "defaultRadius": "20px"
          }
        }
    except Exception as e:
        logger.error(f"Error fetching design tokens: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workspace/graft")
async def workspace_graft(payload: GraftRequest):
    """
    Graft a new HTML snippet into an existing template file based on a CSS selector.
    """
    try:
        # Resolve project path
        project_path = get_active_project_path()
        file_path = project_path / payload.filename
        
        if not file_path.exists():
            # Fallback to static/templates if not in project
            file_path = STATIC_DIR_PATH / "templates" / payload.filename
            
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {payload.filename}")
            
        # Read content
        content = file_path.read_text(encoding='utf-8')
        
        # Parse with BS4
        soup = BeautifulSoup(content, 'lxml' if 'lxml' in sys.modules else 'html.parser')
        
        # Find element
        target = soup.select_one(payload.selector)
        if not target:
            # Try a fuzzy match if selector fails (selector might be slightly different due to nth-child)
            # Logic: If selector is simple (like #id or .class), we might find it.
            # For now, strict match or error.
            raise HTTPException(status_code=400, detail=f"Target element not found in {payload.filename} for selector: {payload.selector}")
            
        # Replace element
        new_tag = BeautifulSoup(payload.html_content, 'html.parser')
        target.replace_with(new_tag)
        
        # Save back
        file_path.write_text(str(soup), encoding='utf-8')
        
        logger.info(f"✅ [Workspace] Grafted snippet into {payload.filename} via {payload.selector}")
        return {"status": "success", "file": payload.filename}
        
    except Exception as e:
        logger.error(f"❌ [Workspace] Grafting failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
    return RedirectResponse(url="/workspace")

@app.get("/landing")
async def get_landing():
    path = STATIC_DIR_PATH / "templates/landing.html"
    if not path.exists(): raise HTTPException(status_code=404)
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=path.read_text(encoding='utf-8'))

# --- MISSION 147 : WIRE AUDIT & SURGICAL (CLEA UX) ---

class SurgicalDiagRequest(BaseModel):
    selector: str
    html: str

class PreWireRequest(BaseModel):
    screen_html: str

class PreWireValidation(BaseModel):
    selector: str
    tag: str
    text: str
    inferred_intent: str
    confirmed: bool
    custom_intent: Optional[str] = None

class PreWireValidateRequest(BaseModel):
    validations: List[PreWireValidation]

@app.get("/api/projects/{project_id}/wire-audit")
async def wire_audit(project_id: str):
    """Bilan de santé du maillage selon le Corpus CLEA."""
    if project_id == "active":
        project_id = get_active_project_id()
    project_path = PROJECTS_DIR / project_id
    manifest_path = project_path / "manifest.json"
    if not manifest_path.exists():
        manifest_path = ROOT_DIR / "exports" / "manifest.json"
    
    manifest = {}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        except: manifest = {}
    
    analyzer = WireAnalyzer(ROOT_DIR)
    registered_routes = []
    for route in app.routes:
        if hasattr(route, "path"):
            registered_routes.append(route.path)
    
    audit = []
    # Aplatir la structure screens[].corps[].organes[] en liste de composants
    raw_components = manifest.get("components", [])
    if not raw_components:
        for screen in manifest.get("screens", []):
            for corps in screen.get("corps", []):
                for organe in corps.get("organes", []):
                    raw_components.append(organe)
    components = raw_components
    backend_map = analyzer._get_backend_mapping()

    for comp in components:
        name = comp.get("name") or comp.get("label") or comp.get("id")
        intent = comp.get("role") or comp.get("intent") or comp.get("label") or "action"
        endpoint = backend_map.get(name) or backend_map.get(intent)
        
        status = "todo"
        if endpoint:
            match = any(r.rstrip('/') == endpoint.rstrip('/') for r in registered_routes)
            status = "ok" if match else "error"
        
        audit.append({
            "organ": name,
            "intent": intent,
            "endpoint": endpoint or "non défini",
            "status": status
        })
    
    plan = "# Plan d'Action (Revue Bionique)\n\n"
    gaps = [a for a in audit if a["status"] != "ok"]
    if not gaps:
        plan += "Votre projet est sain. Tous les organes sont correctement maillés au corps de l'application."
    else:
        for item in gaps:
            # Remplacement de la prose 'poétique' par du 'DNMADE-friendly' (Direct & Valeur)
            action = f"Relier l'organe '{item['organ']}' à sa fonction '{item['intent']}'"
            plan += f"- [ ] **Action** : {action}\n"
    
    return {"audit": audit, "plan": plan}

@app.post("/api/projects/{project_id}/pre-wire")
async def pre_wire(project_id: str, req: PreWireRequest):
    """Mission 185 : Sullivan extrait les intentions du template (Infilling)."""
    if project_id == "active":
        project_id = get_active_project_id()
    
    processed_html = ensure_ids(req.screen_html)
    soup = BeautifulSoup(processed_html, 'html.parser')
    interactives = []

    # Sélecteurs d'éléments interactifs
    tags = soup.find_all(['button', 'a', 'summary'])
    inputs = soup.find_all('input', type=['submit', 'button', 'reset'])
    onclicks = soup.find_all(lambda t: t.has_attr('onclick') and t.name not in ['button', 'a'])
    
    for i, el in enumerate(tags + inputs + onclicks):
        # Générer un sélecteur simple (id ou tag + index)
        selector = f"#{el['id']}" if el.has_attr('id') else f"{el.name}:nth-of-type({i+1})"
        text = el.get_text(strip=True)[:50] or el.get('value', '') or el.get('placeholder', '') or "Sans label"
        
        interactives.append({
            "selector": selector,
            "tag": el.name,
            "text": text,
            "id": el.get('id', ''),
            "class": " ".join(el.get('class', []))
        })

    if not interactives:
        return {"elements": [], "bijection": "null", "manifest_exists": False}

    # Appel Sullivan pour inférence d'intents
    project_path = PROJECTS_DIR / project_id
    manifest_path = project_path / "manifest.json"
    manifest_exists = manifest_path.exists()
    manifest_data = {}
    if manifest_exists:
        try: manifest_data = json.loads(manifest_path.read_text(encoding='utf-8'))
        except: manifest_exists = False

    prompt = f"""Tu es Sullivan, l'Expert BRS HoméOS. 
Voici des éléments d'interface. Pour chacun, devine son label (nom humain) et son intent (code_action).
RÉPONDS UNIQUEMENT EN JSON : [{{ "selector": "...", "label": "...", "intent": "..." }}, ...]

ÉLÉMENTS :
{json.dumps(interactives[:20], ensure_ascii=False)}
"""
    config = _ARBITRATOR.pick("quick")
    res = await asyncio.to_thread(_ARBITRATOR.dispatch, config, [{"role":"user", "content": prompt}])
    inferred = []
    try:
        # Nettoyage JSON si le LLM met des markdowns
        cleaned_json = res.get("text", "[]").strip()
        if "```json" in cleaned_json:
            cleaned_json = cleaned_json.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned_json:
            cleaned_json = cleaned_json.split("```")[1].split("```")[0].strip()
        inferred = json.loads(cleaned_json)
    except Exception as e:
        logger.error(f"Failed to parse Sullivan inference: {e}")

    # Calcul de la bijection
    existing_intents = []
    for s in manifest_data.get("screens", []):
        for c in s.get("corps", []):
            for o in c.get("organes", []):
                existing_intents.append(o.get("id") or o.get("role"))

    final_elements = []
    matches = 0
    for inf in inferred:
        matched = inf.get("intent") in existing_intents
        if matched: matches += 1
        
        # Retrouver les infos d'origine (tag, text)
        orig = next((x for x in interactives if x['selector'] == inf.get('selector')), {})
        
        final_elements.append({
            "selector": inf.get("selector"),
            "id": orig.get("id", ""),
            "tag": orig.get("tag", "div"),
            "text": orig.get("text", "Sans texte"),
            "inferred_intent": inf.get("intent"),
            "endpoint": inf.get("endpoint", ""),
            "matched": matched
        })

    bijection = "total" if matches == len(final_elements) else "incomplete"
    if matches == 0: bijection = "null"

    return {
        "elements": final_elements,
        "bijection": bijection,
        "manifest_exists": manifest_exists,
        "enriched_html": str(soup)  # HTML avec IDs injectés par ensure_ids()
    }

@app.post("/api/projects/{project_id}/pre-wire/validate")
async def pre_wire_validate(project_id: str, req: PreWireValidateRequest):
    """Mission 185 : Sullivan met à jour le manifeste après validation humaine."""
    if project_id == "active":
        project_id = get_active_project_id()
    
    project_path = PROJECTS_DIR / project_id
    manifest_path = project_path / "manifest.json"
    
    manifest = {"name": project_id, "screens": [{"id": "workspace", "corps": [{"id": "main", "organes": []}]}]}
    if manifest_path.exists():
        try: manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        except: pass

    # Extraction des organes actuels pour éviter les doublons
    if "screens" not in manifest or not manifest["screens"]:
        manifest["screens"] = [{"id": "workspace", "corps": [{"id": "main", "organes": []}]}]
    
    organs = manifest["screens"][0]["corps"][0]["organes"]
    pending = manifest.get("pending_intents", [])
    
    count = 0
    for val in req.validations:
        if not val.confirmed:
            # MISSION 187 : Stockage en attente si non confirmé (les "autre")
            pending.append({
                "selector": val.selector,
                "text": val.text,
                "tag": val.tag,
                "note": val.custom_intent or "utilisateur à défini 'autre'"
            })
            continue
        
        intent = val.custom_intent or val.inferred_intent
        # Chercher si l'organe existe déjà par son intent
        existing = next((o for o in organs if o.get("id") == intent or o.get("role") == intent), None)
        
        if existing:
            existing["name"] = val.text
            existing["selector"] = val.selector
        else:
            organs.append({
                "id": intent,
                "name": val.text,
                "role": intent,
                "selector": val.selector
            })
        count += 1

    manifest["pending_intents"] = pending
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
    logger.info(f"✅ [WiRE] Manifeste mis à jour ({count} organes validés, {len(pending)} en attente) pour {project_id}")
    
    return {"status": "success", "organs_count": count, "pending_count": len(pending)}

@app.post("/api/projects/{project_id}/wire-apply")
async def wire_apply_plan(project_id: str, req: Dict[str, Any]):
    """Mission 187 : Forge déterministe (Plus de LLM). Applique les validations confirmées."""
    if project_id == "active": project_id = get_active_project_id()
    
    screen_html = req.get("screen_html")
    validations = req.get("validations", [])
    if not screen_html: return {"status": "error", "message": "screen_html manquant"}

    try:
        from bs4 import BeautifulSoup as BS
        soup = BS(screen_html, 'html.parser')
        modified_elements = []

        for v in validations:
            el_id = v.get('id')
            intent = v.get('intent') or v.get('inferred_intent')
            endpoint = v.get('endpoint')
            if not el_id or not intent: continue
                
            el = soup.find(id=el_id)
            if el:
                el['data-wire'] = intent
                if endpoint: el['data-endpoint'] = endpoint
                modified_elements.append(f"#{el_id}")

        new_html = str(soup)

        # Sauvegarder dans le template d'origine si fourni
        template_name = req.get("template_name")
        import shutil
        if template_name and '/' not in template_name and '..' not in template_name:
            template_file = STATIC_DIR_PATH / "templates" / template_name
            if template_file.exists():
                shutil.copy2(template_file, template_file.with_suffix('.html.bak'))
                template_file.write_text(new_html, encoding='utf-8')
                logger.info(f"Forge saved to {template_file}")

        # Injecter le runtime Wire dans le HTML forgé
        wire_runtime = """<script>
(function(){
    const WIRE_BASE = window.parent?.location?.origin || window.location.origin;
    function showToast(msg, ok){
        let t = document.getElementById('_wire_toast');
        if(!t){ t = document.createElement('div'); t.id='_wire_toast';
            t.style.cssText='position:fixed;bottom:24px;right:24px;z-index:99999;padding:12px 20px;border-radius:10px;font-size:13px;font-family:system-ui,sans-serif;max-width:320px;box-shadow:0 4px 16px rgba(0,0,0,.15);transition:opacity .3s';
            document.body.appendChild(t); }
        t.style.background = ok ? '#f0fce8' : '#fff3cd';
        t.style.color = ok ? '#2d5a0e' : '#856404';
        t.style.border = ok ? '1px solid #8cc63f' : '1px solid #ffc107';
        t.textContent = msg; t.style.opacity='1';
        clearTimeout(t._hide); t._hide = setTimeout(()=>{ t.style.opacity='0'; }, 5000);
    }
    async function execute(wire, userInput, endpoint){
        showToast('⏳ ' + wire + '…', true);
        try {
            const base = window.parent?.location?.origin || 'http://localhost:9998';
            const res = await fetch(base + '/api/wire-execute', {
                method:'POST', headers:{'Content-Type':'application/json'},
                body: JSON.stringify({ wire, user_input: userInput, endpoint })
            });
            const data = await res.json();
            showToast(data.response || data.message || '✓ action exécutée', true);
        } catch(e) { showToast('❌ erreur wire : ' + e.message, false); }
    }
    document.addEventListener('DOMContentLoaded', ()=>{
        document.querySelectorAll('[data-wire]').forEach(el => {
            const wire = el.getAttribute('data-wire');
            const endpoint = el.getAttribute('data-endpoint') || '';
            el.addEventListener('click', e => {
                // Chercher un input texte associé (dans le même form ou parent proche)
                const container = el.closest('form') || el.parentElement;
                const input = container?.querySelector('textarea,input[type=text],input:not([type])');
                const userInput = input?.value || '';
                if(el.tagName === 'A') e.preventDefault();
                execute(wire, userInput, endpoint);
            });
        });
    });
})();
</script>"""
        if '</head>' in new_html:
            new_html = new_html.replace('</head>', wire_runtime + '\n</head>')
        else:
            new_html = wire_runtime + new_html

        return {"status": "success", "html": new_html, "modified_elements": modified_elements or []}
    except Exception as e:
        logger.error(f"❌ [WiRE] Échec de la Forge Déterministe : {e}")
        return {"status": "error", "message": str(e)}


_wire_preview_html: str = ""

@app.post("/wire-preview")
async def set_wire_preview(req: Dict[str, Any]):
    global _wire_preview_html
    _wire_preview_html = req.get("html", "")
    return {"status": "ok"}

@app.get("/wire-preview")
async def get_wire_preview():
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=_wire_preview_html or "<p>aucun preview</p>")

@app.post("/api/wire-execute")
async def wire_execute(req: Dict[str, Any]):
    """Runtime Wire : intercepte une action et appelle Groq."""
    wire = req.get("wire", "")
    user_input = req.get("user_input", "")
    endpoint = req.get("endpoint", "")

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return {"response": f"[wire:{wire}] GROQ_API_KEY manquant"}

    system = (
        f"Tu es un assistant IA branché sur l'interface HoméOS.\n"
        f"L'utilisateur a déclenché l'action : '{wire}'.\n"
        f"Réponds de manière courte et utile (1-3 phrases max)."
    )
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_input or f"action: {wire}"},
        ],
        "temperature": 0.7,
        "max_tokens": 200,
    }
    try:
        import urllib.request as urlreq
        r = urlreq.Request(url, data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}", "User-Agent": "AetherFlow/1.0"})
        with urlreq.urlopen(r, timeout=15) as resp:
            data = json.loads(resp.read())
        response = data["choices"][0]["message"]["content"].strip()
        return {"response": response}
    except Exception as e:
        logger.error(f"[wire-execute] erreur Groq : {e}")
        return {"response": f"erreur groq : {e}"}

@app.post("/api/projects/{project_id}/wire-catchup")
async def wire_catchup(project_id: str):
    """Mission 187 : Sullivan suggère des intentions/endpoints pour les 'autre' mis en attente."""
    if project_id == "active": project_id = get_active_project_id()
    
    project_path = PROJECTS_DIR / project_id
    manifest_path = project_path / "manifest.json"
    if not manifest_path.exists(): return {"status": "error", "message": "Manifeste introuvable"}
    
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    pending = manifest.get("pending_intents", [])
    if not pending: return {"status": "success", "suggestions": []}

    prompt = f"""Tu es Sullivan, l'Expert de Maillage AetherFlow (Corpus CLEA).
MISSION : Suggère des intentions (intent) et des endpoints (METHOD /path) pour ces éléments mis en attente.

ÉLÉMENTS EN ATTENTE :
{json.dumps(pending, ensure_ascii=False)}

RÈGLES DE NOMMAGE (CLEA) :
- intent : snake_case (ex: valider_commande, voir_profil)
- endpoint : METHODE /chemin (ex: POST /api/cart/validate, GET /api/user/profile)

Réponds UNIQUEMENT avec un JSON pur sous ce format :
[
  {{"id": "id-de-l-element", "intent": "suggestion_intent", "endpoint": "METHOD /suggestion/path"}},
  ...
]
"""
    try:
        config = _ARBITRATOR.pick("construction")
        res = await asyncio.to_thread(_ARBITRATOR.dispatch, config, [{"role":"user", "content": prompt}])
        text = res.get("text", "[]")
        
        # Nettoyage JSON
        if "```json" in text: text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text: text = text.split("```")[1].split("```")[0].strip()
        
        suggestions = json.loads(text)
        return {"status": "success", "suggestions": suggestions}
    except Exception as e:
        logger.error(f"Error in wire-catchup: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/api/projects/{project_id}/surgical-diag")
async def surgical_diag(project_id: str, req: SurgicalDiagRequest):
    """Diagnostic chirurgical ciblé (CLEA UX)."""
    if project_id == "active":
        project_id = get_active_project_id()
        
    manifest_context = get_manifest_context(project_id)

    prompt = f"""Tu es Sullivan, l'Arbitre de Maillage HoméOS (Corpus CLEA).
{manifest_context}
CONTEXTE : L'utilisateur inspecte un organe spécifique qui semble présenter un défaut de câblage.
ORGANE (Sélecteur) : {req.selector}
EXTRAIT HTML : {req.html[:1000]}

MISSION : Produis un diagnostic "Bilan de Santé" court et sémantique (style CLEA).
- Utilise le "Fil d'Ariane émotionnel" : rassurer l'utilisateur.
- Utilise "L'erreur qui guide" : explique comment réparer le pont serveur.
- Jargon technique INTERDIT (pas de 'endpoint', '404', 'api'). Utilise 'Pont Serveur', 'Flux', 'Maillage', 'Organe'.

Réponds en 3-4 lignes maximum. Pas de prose, pas de markdown complexe.
"""
    config = _ARBITRATOR.pick("quick")
    res = await asyncio.to_thread(_ARBITRATOR.dispatch, config, [{"role":"user", "content": prompt}])
    return {"explanation": res.get("text", "Diagnostic indisponible.")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server_v3:app", host="0.0.0.0", port=9998, reload=True)
