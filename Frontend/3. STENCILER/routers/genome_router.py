from pathlib import Path
import json
import sys
import subprocess
import logging
from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Request

logger = logging.getLogger("GenomeRouter")

CWD = Path(__file__).parent.parent.resolve()
ROOT_DIR = CWD.parent.parent
BACKEND_PROD = ROOT_DIR / "Backend/Prod"

# Les fichiers globaux deviennent des fallbacks ou des sources initiales
GLOBAL_GENOME_FILE = ROOT_DIR / "Frontend/2. GENOME/genome_enriched.json"
GLOBAL_LAYOUT_FILE = ROOT_DIR / "Frontend/2. GENOME/layout.json"

router = APIRouter()


def get_project_pipeline_dir(token: str = None):
    from bkd_service import get_active_project_path
    d = get_active_project_path(token) / "exports" / "pipeline"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_genome_path(token: str = None):
    from bkd_service import get_active_project_path
    p = get_active_project_path(token) / "genome_enriched.json"
    if not p.exists() and GLOBAL_GENOME_FILE.exists():
        import shutil
        shutil.copy2(GLOBAL_GENOME_FILE, p)
    return p


def get_layout_path(token: str = None):
    from bkd_service import get_active_project_path
    p = get_active_project_path(token) / "layout.json"
    if not p.exists() and GLOBAL_LAYOUT_FILE.exists():
        import shutil
        shutil.copy2(GLOBAL_LAYOUT_FILE, p)
    return p


def load_genome(token: str = None):
    p = get_genome_path(token)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {"n0_phases": []}
    return {"n0_phases": []}


def save_genome(genome, token: str = None):
    p = get_genome_path(token)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(genome, indent=2, ensure_ascii=False), encoding="utf-8")


def load_layout(token: str = None):
    p = get_layout_path(token)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_layout(data, token: str = None):
    p = get_layout_path(token)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _load_overrides(token: str = None):
    f = get_project_pipeline_dir(token) / "template_overrides.json"
    if f.exists():
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_overrides(data, token: str = None):
    f = get_project_pipeline_dir(token) / "template_overrides.json"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(data, indent=2), encoding="utf-8")


# --- ROUTES : INFER LAYOUT ---
_ROLE_KEYWORDS = {
    "header": ["menu", "nav", "toolbar", "header", "top"],
    "sidebar": ["controls", "layers", "sidebar", "tools", "panel"],
    "main": ["editor", "canvas", "main", "grid", "content"],
    "preview": ["thumbnail", "preview", "assets", "timeline"],
    "footer": ["status", "footer", "bottom", "dock"]
}
_ROLE_LAYOUT = {
    "header": {"zone": "header", "w": 1024, "h": 40, "layout": "flex"},
    "sidebar": {"zone": "sidebar_right", "w": 240, "h": "auto", "layout": "stack"},
    "main": {"zone": "main", "w": 640, "h": "auto", "layout": "stack"},
    "preview": {"zone": "preview_band", "w": 1024, "h": 120, "layout": "flex"},
    "footer": {"zone": "footer", "w": 1024, "h": 48, "layout": "flex"},
}
_LAYOUT_SYSTEM_PROMPT = """Tu es un expert UX/layout. Pour chaque organe N1 d'un genome JSON, tu inferes ses parametres de layout SVG.
Regles : reference_width=1024px, grid_unit=8px (toutes les valeurs en multiples de 8).
Zones : header, sidebar_left, sidebar_right, main, canvas, preview_band, footer.
Layout types : flex, stack, grid, free. h = nombre|"auto"|"full", w = nombre|"full".
Reponds UNIQUEMENT avec un objet JSON valide, sans markdown, sans explication.
Format : { "organ_id": { "role": "...", "zone": "...", "w": ..., "h": ..., "layout": "..." }, ... }"""


def _infer_layout_heuristic(organs):
    result = {}
    for organ in organs:
        oid = organ.get("id", organ.get("name", ""))
        name = (organ.get("name", "") + " " + organ.get("role", "") + " " + organ.get("label", "")).lower()
        best_role, best_score = "main", 0
        for role, keywords in _ROLE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in name)
            if score > best_score:
                best_role, best_score = role, score
        layout_info = _ROLE_LAYOUT[best_role]
        result[oid] = {"role": best_role, **layout_info}
    return result


async def _infer_layout_llm(organs, context=""):
    """LLM-based layout inference (requires Gemini client)."""
    try:
        from Backend.Prod.retro_genome.routes import _get_gemini_client
        client = _get_gemini_client()

        prompt = f"{_LAYOUT_SYSTEM_PROMPT}\n\nORGANES:\n{json.dumps(organs, ensure_ascii=False)}"
        if context:
            prompt += f"\n\nCONTEXTE:\n{context}"

        result = await client.generate(prompt=prompt, max_tokens=2048)
        await client.close()

        if result.success:
            cleaned = result.code.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()
            return json.loads(cleaned), None
        return None, result.error
    except Exception as e:
        return None, str(e)


@router.get("/api/genome")
def get_genome(request: Request):
    token = request.headers.get("X-User-Token")
    return load_genome(token)


@router.post("/api/genome")
def post_genome(genome: Dict[str, Any], request: Request):
    token = request.headers.get("X-User-Token")
    save_genome(genome, token)
    return {"status": "ok"}


@router.post("/api/layout")
def post_layout(body: Dict[str, Any], request: Request):
    token = request.headers.get("X-User-Token")
    layout = load_layout(token)
    layout.update(body)
    save_layout(layout, token)
    return {"ok": True}


@router.post("/api/infer_layout")
async def infer_layout(body: Dict[str, Any]):
    organs = body.get("organs", [])
    mode = body.get("mode", "heuristic")
    if mode == "heuristic":
        return {"result": _infer_layout_heuristic(organs), "tier": "heuristic"}

    result, err = await _infer_layout_llm(organs, body.get("context", ""))
    if err:
        return {"result": _infer_layout_heuristic(organs), "tier": "heuristic_fallback", "error": err}
    return {"result": result, "tier": "llm"}


@router.post("/api/organ-move")
def organ_move(body: Dict[str, Any], request: Request):
    oid = body.get("id")
    if not oid:
        raise HTTPException(status_code=400)
    token = request.headers.get("X-User-Token")
    ovr = _load_overrides(token)
    ovr.setdefault(oid, {}).update({"x": body.get("x"), "y": body.get("y")})
    _save_overrides(ovr, token)
    composer = BACKEND_PROD / "pipeline/07_composer.py"
    # Note: 07_composer.py might need update to be token-aware if run via CLI
    subprocess.run([sys.executable, str(composer)], cwd=str(ROOT_DIR))
    return {"ok": True}


@router.post("/api/comp-move")
def comp_move(body: Dict[str, Any], request: Request):
    cid = body.get("id")
    if not cid:
        raise HTTPException(status_code=400)
    token = request.headers.get("X-User-Token")
    ovr = _load_overrides(token)
    ovr.setdefault(cid, {}).update({"x": body.get("x"), "y": body.get("y"), "s": body.get("s", 1)})
    _save_overrides(ovr, token)
    composer = BACKEND_PROD / "pipeline/07_composer.py"
    subprocess.run([sys.executable, str(composer)], cwd=str(ROOT_DIR))
    return {"ok": True}


@router.post("/api/accept")
def accept_template(request: Request):
    from bkd_service import get_active_project_path
    token = request.headers.get("X-User-Token")
    prj_path = get_active_project_path(token)
    exports_dir = prj_path / "exports"
    src = exports_dir / "template_latest.svg"
    if src.exists():
        from datetime import datetime
        import shutil
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dst = exports_dir / f"FINAL_template_{ts}.svg"
        shutil.copy2(src, dst)
        return {"saved": dst.name}
    return {"error": "No template found"}
