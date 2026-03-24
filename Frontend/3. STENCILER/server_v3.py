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

from fastapi import FastAPI, HTTPException, Depends, Query, Body, Request, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# --- CONFIGURATION & PATHS ---
CWD = Path(__file__).parent.resolve()
ROOT_DIR = CWD.parent.parent
BACKEND_PROD = ROOT_DIR / "Backend/Prod"
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

# --- SULLIVAN IMPORTS ---
import sys
for p in [str(ROOT_DIR), str(BACKEND_PROD)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from bkd_service import (
    SULLIVAN_BKD_SYSTEM, MANIFEST_FRD, SULLIVAN_RAG,
    exec_query_knowledge_base, route_request_bkd,
    resolve_bkd_project_root, bkd_safe_path, bkd_build_tree,
    BKD_DB_PATH, bkd_db_con,
    BKD_ALLOWED_EXTENSIONS, BKD_EXCLUDE_DIRS,
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

# --- CONSTANTS ---
RETRO_DIR = ROOT_DIR / "exports" / "retro_genome"
PIPELINE_DIR = ROOT_DIR / "exports" / "pipeline"
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
    logger.info(f"Projects database initialized at {PROJECTS_DB_PATH}")

# --- PYDANTIC MODELS ---
class ProjectBase(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Mon Projet"})
    path: str = Field(..., json_schema_extra={"example": "/Users/name/projects/my-app"})

class ProjectResponse(BaseModel):
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

# --- ROUTES : BKD PROJECTS ---
@app.get("/api/bkd/projects", response_model=Dict[str, List[ProjectResponse]])
async def list_projects():
    with get_db_conn() as conn:
        rows = conn.execute('SELECT id, name, path, created_at, last_opened FROM projects ORDER BY last_opened DESC').fetchall()
    
    projects = [
        ProjectResponse(id=r[0], name=r[1], path=r[2], created_at=r[3], last_opened=r[4])
        for r in rows
    ]
    return {"projects": projects}

@app.post("/api/bkd/projects")
async def register_project(project: ProjectBase):
    path_obj = Path(project.path)
    if not path_obj.exists() or not path_obj.is_dir():
        raise HTTPException(status_code=400, detail="Project path does not exist or is not a directory")
    
    with get_db_conn() as conn:
        existing = conn.execute('SELECT id FROM projects WHERE path=?', (str(path_obj),)).fetchone()
        if existing:
            conn.execute("UPDATE projects SET last_opened=datetime('now') WHERE id=?", (existing[0],))
            return {"id": existing[0], "created": False}
        
        project_id = str(uuid.uuid4())
        conn.execute('INSERT INTO projects (id, name, path) VALUES (?,?,?)', (project_id, project.name, str(path_obj)))
        return {"id": project_id, "created": True}

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
    f = PIPELINE_DIR / "template_overrides.json"
    if f.exists():
        try: return json.loads(f.read_text(encoding="utf-8"))
        except: return {}
    return {}

def _save_overrides(data):
    PIPELINE_DIR.mkdir(parents=True, exist_ok=True)
    (PIPELINE_DIR / "template_overrides.json").write_text(json.dumps(data, indent=2), encoding="utf-8")

def _write_retro_status(step, message):
    RETRO_DIR.mkdir(parents=True, exist_ok=True)
    (RETRO_DIR / "upload_status.json").write_text(json.dumps({"step": step, "message": message, "ts": datetime.now().isoformat()}))

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
@app.get("/")
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

# --- ROUTES : RETRO-GENOME ---
@app.get("/api/retro-genome/status")
async def retro_status():
    status_path = RETRO_DIR / "upload_status.json"
    if status_path.exists():
        return json.loads(status_path.read_text(encoding='utf-8'))
    return {"step": "idle", "message": ""}

@app.post("/api/retro-genome/upload")
async def retro_upload(request: Request):
    # Simplification du parsing multipart en utilisant FastAPI directement si possible
    # Sinon portage du parsing manuel de server_9998_v2
    # Pour Mission 87, on va supposer que le frontend peut s'adapter ou on utilise UploadFile
    pass # À détailler si besoin d'un portage exact 1:1

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
    html_path = RETRO_DIR / "reality.html"
    if not html_path.exists(): raise HTTPException(status_code=404, detail="reality.html not found")
    zip_path = await asyncio.to_thread(export_as_zip, "AetherFlow_Reality", html_path.read_text(encoding='utf-8'), RETRO_DIR)
    return {"status": "ok", "zip_path": str(zip_path)}

@app.post("/api/retro-genome/export-manifest")
async def retro_export_manifest():
    from Backend.Prod.retro_genome.manifest_inferer import ManifestInferer
    html_path = RETRO_DIR / "reality.html"
    if not html_path.exists(): raise HTTPException(status_code=404, detail="reality.html not found")
    manifest = await asyncio.to_thread(asyncio.run, ManifestInferer.infer_from_html(html_path))
    out = RETRO_DIR / "manifest.json"
    ManifestInferer.save_manifest(manifest, out)
    return {"status": "ok", "manifest_path": str(out)}

@app.post("/api/retro-genome/generate-html")
async def retro_gen_html():
    pngs = sorted(RETRO_DIR.glob("upload_*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not pngs: raise HTTPException(status_code=400, detail="No PNG found")
    val_path = RETRO_DIR / "validated_analysis.json"
    if not val_path.exists(): raise HTTPException(status_code=400, detail="Not validated")
    
    with open(val_path, 'r', encoding='utf-8') as f: validated = json.load(f)
    gen = HtmlGenerator()
    def cb(msg, step="generating"): _write_retro_status(step, msg)
    html = await asyncio.to_thread(asyncio.run, gen.generate(png_path=pngs[0], matched_analysis=validated, status_callback=cb))
    return {"status": "ok", "html_path": str(RETRO_DIR / "reality.html")}

@app.post("/api/retro-genome/upload-svg")
async def retro_upload_svg(body: Dict[str, Any]):
    svg = body.get('svg', '')
    name = body.get('name', 'frame')
    if not svg: raise HTTPException(status_code=400)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    out = RETRO_DIR / f"SVG_{name}_{ts}.svg"
    out.write_text(svg, encoding='utf-8')
    from Backend.Prod.retro_genome.svg_parser import parse_figma_svg
    from Backend.Prod.retro_genome.archetype_detector import ArchetypeDetector
    analysis = parse_figma_svg(svg)
    arch = ArchetypeDetector().detect(analysis)
    return {"status": "ok", "visual_analysis": analysis, "archetype": arch}

@app.post("/api/manifest/patch")
async def manifest_patch(patch: Dict[str, Any]):
    m_path = ROOT_DIR / 'exports' / 'manifest.json'
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9998)
