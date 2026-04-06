"""
AetherFlow FRD Router - Extracted from server_v3.py
Contains all FRD-related routes, models, globals, and helpers.
"""

import os
import re
import json
import uuid
import asyncio
import logging
import urllib.request
import zipfile
import io
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Query, Request, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from bs4 import BeautifulSoup

logger = logging.getLogger("AetherFlowV3")

# --- ROUTER ---
router = APIRouter()

# --- PATHS (resolve relative to this file's parent chain) ---
CWD = Path(__file__).parent.parent.resolve()
ROOT_DIR = CWD.parent.parent
STATIC_DIR_PATH = CWD / "static"

# --- IMPORTS FROM BKD SERVICE ---
from bkd_service import (
    get_active_project_id, get_active_project_path,
    exec_query_knowledge_base, PROJECTS_DIR,
)

# --- IMPORTS FROM MANIFEST VALIDATOR ---
try:
    from Backend.Prod.retro_genome.manifest_validator import validate_html, format_system_prompt_constraint, load_manifest, get_manifest_path
except ImportError:
    logger.warning("Manifest validator not found. FRD validation will be disabled.")
    def validate_html(n, c): return True, []
    def format_system_prompt_constraint(n): return ""
    def load_manifest(n): return {}
    def get_manifest_path(n): return None

# --- IMPORT FROM SULLIVAN ARBITRATOR ---
from sullivan_arbitrator import SullivanArbitrator

# --- GLOBAL STATE ---
_CURRENT_FRD_CONTEXT = {"type": None, "id": None, "name": None, "html_template": None}
_NEW_IMPORTS_COUNT = 0

_KIMI_JOBS: Dict[str, Dict[str, Any]] = {}
_KIMI_JOBS_LOCK = asyncio.Lock()

_ARBITRATOR = SullivanArbitrator()

# --- PYDANTIC MODELS ---
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

class AnnotateRequest(BaseModel):
    intent_id: str
    component_name: str
    description: str

class CurrentFileRequest(BaseModel):
    type: str
    id: Optional[str] = None
    name: Optional[str] = None
    html_template: Optional[str] = None

# --- KIMI JOB WORKER ---
def _run_kimi_job(job_id, instruction, html_context):
    """Executes the KIMI call in the background (Mission 54)."""
    try:
        # 1. Strip <script> blocks (Mission 52 optimization)
        html_stripped = re.sub(r'<script[\s\S]*?</script>', '', html_context, flags=re.IGNORECASE).strip()

        # Load env for API key
        env_path = ROOT_DIR / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if "=" in line and not line.startswith("#"):
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())

        api_key = os.environ.get('OPENROUTER_API_KEY')
        if not api_key or api_key == "votre_cle_ici":
            async def _set_error():
                async with _KIMI_JOBS_LOCK:
                    _KIMI_JOBS[job_id] = { "status": "error", "error": "OPENROUTER_API_KEY non configur\u00e9e", "ts": datetime.now() }
            asyncio.get_event_loop().run_until_complete(_set_error())
            return

        url = "https://openrouter.ai/api/v1/chat/completions"

        prompt = (
            "Tu es KIMI, expert en design UI/UX. Propose UNE refonte visuelle de l'interface HTML/Tailwind fournie.\n"
            "R\u00e9ponds avec un label court (3-5 mots) puis le HTML complet modifi\u00e9.\n"
            "Format strict :\nLABEL: [label]\n---HTML---\n[HTML complet]\n\n"
            f"Instruction : {instruction}\n"
            f"HTML actuel (scripts omis) :\n{html_stripped}"
        )

        payload = {
            "model": "google/gemma-2-9b-it:free",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 8192,
            "temperature": 0.7
        }

        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'),
                                     headers={
                                         'Content-Type': 'application/json',
                                         'Authorization': f'Bearer {api_key}',
                                         'HTTP-Referer': 'https://aetherflow.ai',
                                         'X-Title': 'AetherFlow'
                                     })

        with urllib.request.urlopen(req, timeout=600) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            choices = res_data.get('choices') or []
            raw_text = (choices[0].get('message') or {}).get('content') if choices else None

            if not raw_text:
                finish = (choices[0].get('finish_reason') if choices else 'unknown')
                error_msg = f"KIMI content vide (finish_reason: {finish})"
                async def _set_error2():
                    async with _KIMI_JOBS_LOCK:
                        _KIMI_JOBS[job_id] = { "status": "error", "error": error_msg, "ts": datetime.now() }
                asyncio.get_event_loop().run_until_complete(_set_error2())
                return

            # Parse label + html
            label = "KIMI Design"
            html = raw_text.strip()
            if "LABEL:" in html:
                parts = html.split("---HTML---", 1)
                label = parts[0].replace("LABEL:", "").strip()
                html = parts[1].strip() if len(parts) > 1 else html
            elif "---HTML---" in html:
                html = html.split("---HTML---", 1)[1].strip()

            # Strip markdown code fences if present
            if html.startswith("```html"):
                html = html.split("```html", 1)[1].split("```")[0].strip()
            elif html.startswith("```"):
                html = html.split("```", 1)[1].split("```")[0].strip()

            async def _set_done():
                async with _KIMI_JOBS_LOCK:
                    _KIMI_JOBS[job_id] = { "status": "done", "label": label, "html": html, "ts": datetime.now() }
            asyncio.get_event_loop().run_until_complete(_set_done())

    except Exception as e:
        async def _set_exc():
            async with _KIMI_JOBS_LOCK:
                _KIMI_JOBS[job_id] = { "status": "error", "error": str(e), "ts": datetime.now() }
        asyncio.get_event_loop().run_until_complete(_set_exc())

# --- WIRES ---
def _build_wire_prompt(html_context: str) -> str:
    return (
        "Tu es Sullivan (IA HomeOS), expert en diagnostic et impl\u00e9mentation de code HTML/JS.\n"
        "Analyse le code source fourni.\n\n"
        "PARTIE 1 \u2014 DIAGNOSTIC : Identifie les probl\u00e8mes existants :\n"
        "- S\u00e9lecteurs orphelins (getElementById/querySelector vers IDs absents)\n"
        "- Bindings manquants (addEventListener/onclick vers fonctions non d\u00e9finies)\n"
        "- Fetch vers endpoints non d\u00e9clar\u00e9s\n"
        "- Interactions d\u00e9crites dans le HTML mais sans JS correspondant\n\n"
        "PARTIE 2 \u2014 PLAN D'IMPL\u00c9MENTATION : Liste les actions JS \u00e0 impl\u00e9menter pour que l'UI soit fonctionnelle. "
        "Pour chaque action : indique l'\u00e9l\u00e9ment cible, le comportement attendu, et l'endpoint API si applicable.\n\n"
        "FORMAT (Markdown) :\n"
        "# \ud83d\udd78\ufe0f Diagnostic WIRE\n\n"
        "## \ud83d\udd0d Probl\u00e8mes d\u00e9tect\u00e9s\n- [Liste ou 'Aucun']\n\n"
        "## \ud83d\udccb Plan d'impl\u00e9mentation\n"
        "1. [Action] \u2014 [\u00c9l\u00e9ment] \u2192 [Comportement / Endpoint]\n"
    )

# --- CUSTOM INJECTION ---
def load_custom_injection():
    injection_path = STATIC_DIR_PATH / 'js' / 'custom_injection.js'
    if injection_path.exists():
        return f"<script>{injection_path.read_text(encoding='utf-8')}</script>"
    return ""

# =============================================================================
# FRD ROUTES
# =============================================================================

@router.post("/api/frd/set-current")
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

@router.get("/api/frd/current")
async def get_current_frd_context():
    return _CURRENT_FRD_CONTEXT

@router.get("/api/frd/current")
async def get_frd_current():
    """Retourne l'import/template actuellement charg\u00e9 dans l'\u00e9diteur."""
    from bkd_service import get_active_project_id
    p_path = PROJECTS_DIR / get_active_project_id()
    f = p_path / "current_frd.json"
    if f.exists():
        return json.loads(f.read_text(encoding='utf-8'))
    return {"status": "none"}

@router.get("/api/frd/manifest")
async def get_frd_manifest(import_id: str = Query(...)):
    """
    D\u00e9tection de manifeste pour le routage intelligent (Mission 146).
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

@router.post("/api/frd/validate-wire")
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

@router.post("/api/frd/annotate")
async def frd_annotate(req: AnnotateRequest):
    """
    Mission 102: Lancement de l'annotation (KIMI / AI).
    G\u00e9n\u00e8re un plan d'impl\u00e9mentation pour une intention donn\u00e9e.
    """
    try:
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

@router.get("/api/frd/export-zip")
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
                        arcname = f"fonts/{font_file.relative_to(fonts_dir)}"
                        zip_file.write(font_file, arcname=arcname)

        zip_buffer.seek(0)
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

@router.get("/api/frd/file")
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

@router.post("/api/frd/file")
async def save_frd_file(req: FRDFileRequest):
    if '/' in req.name or '..' in req.name:
        raise HTTPException(status_code=400, detail="Invalid filename")

    # Validation manifeste DOM (Mission 63)
    is_valid, errors = validate_html(req.name, req.content)
    if not is_valid and not req.force:
        return JSONResponse(status_code=422, content={
            "error": "CONTRAT DOM VIOL\u00c9",
            "violations": errors
        })

    path = STATIC_DIR_PATH / "templates" / req.name
    path.write_text(req.content, encoding='utf-8')
    return {"status": "ok", "name": req.name}

@router.get("/api/frd/assets")
async def list_frd_assets():
    assets_dir = STATIC_DIR_PATH / "assets" / "frd"
    assets_dir.mkdir(parents=True, exist_ok=True)
    assets = []
    for f in sorted(assets_dir.iterdir()):
        if f.is_file() and f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'):
            assets.append({"name": f.name, "url": f"/static/assets/frd/{f.name}"})
    return {"assets": assets}

@router.post("/api/frd/upload")
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

@router.post("/api/frd/chat")
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
        "Tu es Sullivan, expert frontend HomeOS. Tu cr\u00e9es ou modifies des fichiers HTML/Tailwind CSS avec JavaScript vanilla inline.\n"
        "R\u00c8GLE JS : Toujours inclure les event listeners, toggles, fetch calls et interactions n\u00e9cessaires en JS vanilla dans des balises <script> dans le m\u00eame fichier HTML. "
        "Si l'UI contient des boutons, formulaires, panels ou onglets interactifs, g\u00e9n\u00e8re OBLIGATOIREMENT le JS correspondant.\n"
        "R\u00c8GLE CRITIQUE : Si la demande d\u00e9crit une page DIFF\u00c9RENTE de l'HTML actuel, IGNORE l'HTML actuel et cr\u00e9e une nouvelle page.\n"
        "Format de r\u00e9ponse : [explication 1-2 phrases]\n---HTML---\n[code HTML complet]\n"
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

@router.post("/api/frd/kimi/start")
async def kimi_start(req: KimiStartRequest, bg_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())[:8]
    async with _KIMI_JOBS_LOCK:
        _KIMI_JOBS[job_id] = {"status": "pending"}
    bg_tasks.add_task(_run_kimi_job, job_id, req.instruction, req.html)
    return {"job_id": job_id}

@router.get("/api/frd/kimi/result/{job_id}", response_model=KimiResultResponse)
async def kimi_result(job_id: str):
    async with _KIMI_JOBS_LOCK:
        job = _KIMI_JOBS.get(job_id)
    if not job:
        return KimiResultResponse(status="not_found")
    return KimiResultResponse(**job)
