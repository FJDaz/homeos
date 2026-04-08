"""
AetherFlow BKD Router - Extracted from server_v3.py
Contains all BKD-related routes, models, and utilities.
"""

import os
import json
import uuid
import sqlite3
import asyncio
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# --- LOGGING ---
logger = logging.getLogger("AetherFlowV3.BKD")

# --- PATHS ---
CWD = Path(__file__).parent.parent.resolve()
ROOT_DIR = CWD.parent.parent
PROJECTS_DIR = ROOT_DIR / "projects"
PROJECTS_DB_PATH = ROOT_DIR / "db/projects.db"

# --- ENVIRONMENT ---
def _load_env():
    env_path = ROOT_DIR / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())

_load_env()

# --- SULLIVAN IMPORTS ---
import sys
for p in [str(ROOT_DIR), str(ROOT_DIR / "Backend/Prod"), str(CWD)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from bkd_service import (
    SULLIVAN_BKD_SYSTEM, MANIFEST_FRD, SULLIVAN_RAG,
    exec_query_knowledge_base, route_request_bkd,
    resolve_bkd_project_root, bkd_safe_path, bkd_build_tree,
    BKD_DB_PATH, bkd_db_con, PROJECTS_DIR as BKD_PROJECTS_DIR,
    get_active_project_id, set_active_project_id, get_active_project_path,
    BKD_ALLOWED_EXTENSIONS, BKD_EXCLUDE_DIRS,
    conv_create, conv_append, conv_get, conv_list, conv_auto_title,
    SULLIVAN_FEE_SYSTEM, get_fee_logic, save_fee_logic,
)

from sullivan_arbitrator import SullivanArbitrator, SullivanPulse

# --- PYDANTIC MODELS ---
class ProjectInfo(BaseModel):
    id: str
    name: str
    path: str
    created_at: Optional[str] = None
    last_opened: Optional[str] = None
    active: bool = False

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
    role: str = "architect"  # architect | worker
    conversation_id: Optional[str] = None

class ConversationInfo(BaseModel):
    id: str
    project_id: str
    role: str
    title: str
    updated_at: str

class ConversationDetail(ConversationInfo):
    content_json: str

class ChatResponse(BaseModel):
    explanation: str
    html: Optional[str] = None
    route: str
    provider: str
    conversation_id: Optional[str] = None

class FileWriteRequest(BaseModel):
    project_id: str
    path: str
    content: str

# --- CONSTANTS ---
ALLOWED_EXTENSIONS = {'.py', '.js', '.ts', '.html', '.css', '.md', '.json', '.txt', '.yaml', '.yml', '.toml', '.sh', '.env.example'}
EXCLUDE_DIRS = {'__pycache__', '.git', 'node_modules', '.venv', 'venv', 'dist', 'build', '.mypy_cache'}

# Aliases vers bkd_service (pas de duplication)
get_db_conn = bkd_db_con
resolve_project_root = resolve_bkd_project_root
build_tree = bkd_build_tree
safe_path = bkd_safe_path

# BKD-specific constants (from bkd_service)
BKD_ALLOWED_EXTENSIONS = ALLOWED_EXTENSIONS
BKD_EXCLUDE_DIRS = EXCLUDE_DIRS

# --- ARBITRATOR ---
_ARBITRATOR = SullivanArbitrator()

# --- ROUTER ---
router = APIRouter(prefix="/api/bkd", tags=["bkd"])

# --- HELPER: list_all_projects_route (needed by BKD projects endpoint) ---
async def list_all_projects_route():
    active_id = get_active_project_id()
    with sqlite3.connect(str(PROJECTS_DB_PATH)) as conn:
        rows = conn.execute("SELECT id, name, path, created_at, last_opened FROM projects ORDER BY last_opened DESC").fetchall()
        return [ProjectInfo(id=r[0], name=r[1], path=r[2], created_at=r[3], last_opened=r[4], active=(r[0] == active_id)) for r in rows]

# --- ROUTES ---

@router.get("/projects", response_model=Dict[str, List[ProjectInfo]])
async def list_bkd_projects():
    # Legacy link for BKD
    projects = await list_all_projects_route()
    return {"projects": projects}

@router.get("/files")
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

@router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    with get_db_conn() as conn:
        conn.execute('DELETE FROM projects WHERE id=?', (project_id,))
    return {"ok": True, "deleted": project_id}

# --- BKD FILES ---
@router.get("/files", response_model=BKDFileListingResponse)
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

@router.get("/file", response_model=FileResponse)
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

@router.post("/file")
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

# --- CONVERSATIONS ---

@router.get("/conversations", response_model=List[ConversationInfo])
async def list_conversations(project_id: str = Query(...), role: Optional[str] = None):
    with get_db_conn() as conn:
        q = "SELECT id, project_id, role, title, updated_at FROM conversations WHERE project_id = ?"
        params = [project_id]
        if role:
            q += " AND role = ?"
            params.append(role)
        q += " ORDER BY updated_at DESC"
        rows = conn.execute(q, params).fetchall()
        return [ConversationInfo(id=r[0], project_id=r[1], role=r[2], title=r[3], updated_at=r[4]) for r in rows]

@router.get("/conversations/{conv_id}", response_model=ConversationDetail)
async def get_conversation(conv_id: str):
    with get_db_conn() as conn:
        row = conn.execute("SELECT id, project_id, role, title, updated_at, content_json FROM conversations WHERE id = ?", (conv_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return ConversationDetail(id=row[0], project_id=row[1], role=row[2], title=row[3], updated_at=row[4], content_json=row[5])

@router.post("/conversations/{conv_id}/append")
async def append_to_conversation(conv_id: str, turn: Dict[str, Any] = Body(...)):
    """Ajoute un tour (role: user|assistant, content: str) à une conversation existante."""
    with get_db_conn() as conn:
        row = conn.execute("SELECT content_json FROM conversations WHERE id = ?", (conv_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        history = json.loads(row[0])
        history.append(turn)
        
        conn.execute("UPDATE conversations SET content_json = ?, updated_at = datetime('now') WHERE id = ?", 
                     (json.dumps(history), conv_id))
        conn.commit()
    return {"ok": True}

# --- BKD CHAT ---
@router.post("/chat", response_model=ChatResponse)
async def bkd_chat_endpoint(req: ChatRequest):
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

        # 3. Dispatch & History Management
        from bkd_service import conv_auto_title
        
        conv_id = req.conversation_id
        if not conv_id:
            conv_id = str(uuid.uuid4())
            # Création initiale
            title = conv_auto_title(req.message, root) if req.project_id else "Nouvelle conversation"
            with get_db_conn() as conn:
                conn.execute(
                    "INSERT INTO conversations (id, project_id, role, title, content_json) VALUES (?, ?, ?, ?, ?)",
                    (conv_id, req.project_id or "homéos-default", req.role, title, json.dumps([]))
                )
                conn.commit()

        # Tools wiring...
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
                        file_content = f'Acces refusé : {rel}'
                messages.append({'role': 'assistant', 'content': f'Appel outil read file: {rel}'})
                messages.append({'role': 'user', 'content': f'CONTENU: {file_content}'})
            else:
                final_text = res.get("text", "")
                break

        # Persister le tour dans la DB
        with get_db_conn() as conn:
            row = conn.execute("SELECT content_json FROM conversations WHERE id = ?", (conv_id,)).fetchone()
            if row:
                hist = json.loads(row[0])
                hist.append({"role": "user", "content": req.message})
                hist.append({"role": "assistant", "content": final_text})
                conn.execute(
                    "UPDATE conversations SET content_json = ?, updated_at = datetime('now') WHERE id = ?", 
                    (json.dumps(hist), conv_id)
                )
                conn.commit()

        return ChatResponse(
            explanation=final_text,
            model=config['model'],
            route=route_type,
            provider=config['provider'],
            conversation_id=conv_id  # Retourner le conv_id pour le frontend
        )
    except Exception as e:
        logger.error(f"BKD Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- CONVERSATION HISTORY ROUTES ---

class ConvCreateRequest(BaseModel):
    project_id: str
    role: str = "architect"
    title: Optional[str] = None

class ConvAppendRequest(BaseModel):
    role: str  # 'user' | 'assistant'
    text: str

@router.post("/conversations")
async def create_conversation(req: ConvCreateRequest):
    cid = conv_create(req.project_id, req.role, req.title)
    return {"id": cid}

@router.get("/conversations")
async def list_conversations(project_id: str = Query(...), limit: int = Query(5)):
    return {"conversations": conv_list(project_id, limit)}

@router.get("/conversations/{conv_id}")
async def get_conversation(conv_id: str):
    conv = conv_get(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv

@router.post("/conversations/{conv_id}/append")
async def append_to_conversation(conv_id: str, req: ConvAppendRequest):
    conv_append(conv_id, req.role, req.text)
    conv_auto_title(conv_id)
    return {"ok": True}

@router.delete("/conversations/{conv_id}")
async def delete_conversation(conv_id: str):
    with bkd_db_con() as con:
        con.execute("DELETE FROM conversations WHERE id=?", (conv_id,))
    return {"ok": True}


# --- FEE LAB ROUTES ---

@router.get("/fee/preview", response_class=HTMLResponse)
async def get_fee_preview(project_id: str = Query(...), path: str = Query(...)):
    """Sert le HTML brut d'un fichier projet pour l'iframe FEE — M260: injecte <base> pour les assets relatifs."""
    root = resolve_bkd_project_root(project_id)
    if not root:
        raise HTTPException(status_code=404, detail="Project not found")
    file_path = bkd_safe_path(root, path)
    if not file_path or not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    html = file_path.read_text(encoding="utf-8")

    # M260-Fix2: Injecter <base> pour que les assets relatifs (css/, images/) résolvent
    # Le HTML est servi via /api/bkd/fee/preview → le browser cherche relatifs ici
    # On injecte une base pointant vers le dossier du fichier HTML
    file_dir = str(file_path.parent)
    if "<base" not in html and "<head>" in html:
        html = html.replace("<head>", f'<head><base href="/projects/{project_id}/" />', 1)

    return HTMLResponse(content=html)


@router.get("/fee/presets")
async def get_fee_presets():
    """Charge le catalogue des presets GSAP."""
    path = CWD / "static/fee_presets.json"
    if not path.exists():
        return {"presets": []}
    return json.loads(path.read_text(encoding="utf-8"))


@router.get("/fee/logic")
async def get_fee_logic_route(project_id: str = Query(...), screen: str = Query(...)):
    """Lit le code logic/{screen}.js."""
    content = get_fee_logic(project_id, screen)
    return {"content": content, "screen": screen}


@router.post("/fee/logic")
async def save_fee_logic_route(req: Dict[str, Any] = Body(...)):
    """Sauvegarde le code logic/{screen}.js."""
    project_id = req.get("project_id")
    screen = req.get("screen")
    content = req.get("content")
    if not project_id or not screen:
        raise HTTPException(status_code=400, detail="Missing project_id or screen")
    save_fee_logic(project_id, screen, content)
    return {"ok": True}


@router.post("/fee/chat")
async def fee_chat_endpoint(req: ChatRequest):
    """Chat spécialisé Sullivan FEE (GSAP Expert)."""
    try:
        # On utilise Sullivan FEE System Prompt
        system = SULLIVAN_FEE_SYSTEM

        # Arbitrage simplifié (Geist/Kimi/Gemini-2.0-Flash recommandé pour le code rapide)
        config = _ARBITRATOR.pick("code-simple")

        # Limiter l'historique pour Sullivan FEE
        messages = [{"role": turn.get('role', 'user'), "content": turn.get('text', '')} for turn in req.history[-6:]]
        messages.append({"role": "user", "content": req.message})

        # Appel Sullivan Arbitrator
        res = _ARBITRATOR.dispatch(config, messages, system=system)

        if not res.get("success"):
            raise HTTPException(status_code=500, detail=res.get("error", "FEE Dispatch error"))

        return ChatResponse(
            explanation=res.get("text", ""),
            model=config['model'],
            route="fee-lab",
            provider=config['provider'],
            conversation_id=req.conversation_id
        )
    except Exception as e:
        logger.error(f"FEE Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fee/apply")
async def fee_apply_code(req: dict):
    """M221: Applique le code GSAP généré dans logic.js du projet."""
    project_id = req.get("project_id")
    screen = req.get("screen", "landing.html")
    code = req.get("code", "")
    trigger = req.get("trigger")

    if not project_id or not code:
        raise HTTPException(status_code=400, detail="project_id et code requis")

    # Lire logic.js existant
    logic_path = PROJECTS_DIR / project_id / "logic" / "logic.js"
    existing = ""
    if logic_path.exists():
        existing = logic_path.read_text(encoding='utf-8')

    # Injecter le code avec markers FEE
    fee_block = f"\n// [FEE-LOGIC-START] trigger={trigger}\n{code}\n// [FEE-LOGIC-END]\n"
    new_content = existing + fee_block

    logic_path.parent.mkdir(parents=True, exist_ok=True)
    logic_path.write_text(new_content, encoding='utf-8')

    return {"status": "ok", "trigger": trigger, "screen": screen}



