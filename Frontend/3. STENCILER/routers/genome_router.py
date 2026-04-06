from pathlib import Path
import json
import sys
import subprocess
import logging
from typing import Any, Dict
from fastapi import APIRouter, HTTPException

logger = logging.getLogger("GenomeRouter")

CWD = Path(__file__).parent.parent.resolve()
ROOT_DIR = CWD.parent.parent
BACKEND_PROD = ROOT_DIR / "Backend/Prod"

GENOME_FILE = ROOT_DIR / "Frontend/2. GENOME/genome_enriched.json"
LAYOUT_FILE = ROOT_DIR / "Frontend/2. GENOME/layout.json"
PIPELINE_DIR = ROOT_DIR / "exports" / "pipeline"

router = APIRouter()


def get_project_pipeline_dir():
    from bkd_service import get_active_project_path
    d = get_active_project_path() / "exports" / "pipeline"
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_genome():
    if GENOME_FILE.exists():
        try:
            return json.loads(GENOME_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {"n0_phases": []}
    return {"n0_phases": []}


def save_genome(genome):
    GENOME_FILE.parent.mkdir(parents=True, exist_ok=True)
    GENOME_FILE.write_text(json.dumps(genome, indent=2, ensure_ascii=False), encoding="utf-8")


def load_layout():
    if LAYOUT_FILE.exists():
        try:
            return json.loads(LAYOUT_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_layout(data):
    LAYOUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    LAYOUT_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _load_overrides():
    f = get_project_pipeline_dir() / "template_overrides.json"
    if f.exists():
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_overrides(data):
    f = get_project_pipeline_dir() / "template_overrides.json"
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
async def get_genome():
    return load_genome()


@router.post("/api/genome")
async def post_genome(genome: Dict[str, Any]):
    save_genome(genome)
    return {"status": "ok"}


@router.post("/api/layout")
async def post_layout(body: Dict[str, Any]):
    layout = load_layout()
    layout.update(body)
    save_layout(layout)
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
async def organ_move(body: Dict[str, Any]):
    oid = body.get("id")
    if not oid:
        raise HTTPException(status_code=400)
    ovr = _load_overrides()
    ovr.setdefault(oid, {}).update({"x": body.get("x"), "y": body.get("y")})
    _save_overrides(ovr)
    composer = BACKEND_PROD / "pipeline/07_composer.py"
    subprocess.run([sys.executable, str(composer)], cwd=str(ROOT_DIR))
    return {"ok": True}


@router.post("/api/comp-move")
async def comp_move(body: Dict[str, Any]):
    cid = body.get("id")
    if not cid:
        raise HTTPException(status_code=400)
    ovr = _load_overrides()
    ovr.setdefault(cid, {}).update({"x": body.get("x"), "y": body.get("y"), "s": body.get("s", 1)})
    _save_overrides(ovr)
    composer = BACKEND_PROD / "pipeline/07_composer.py"
    subprocess.run([sys.executable, str(composer)], cwd=str(ROOT_DIR))
    return {"ok": True}


@router.post("/api/accept")
async def accept_template():
    exports_dir = ROOT_DIR / "exports"
    src = exports_dir / "template_latest.svg"
    if src.exists():
        from datetime import datetime
        import shutil
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dst = exports_dir / f"FINAL_template_{ts}.svg"
        shutil.copy2(src, dst)
        return {"saved": dst.name}
    return {"error": "No template found"}
