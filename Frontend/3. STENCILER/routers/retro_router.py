from pathlib import Path
import json
import logging
import asyncio
from datetime import datetime
from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Request

logger = logging.getLogger("RetroRouter")

CWD = Path(__file__).parent.parent.resolve()
ROOT_DIR = CWD.parent.parent

RETRO_DIR = ROOT_DIR / "Backend/Prod/retro_genome"

router = APIRouter()


def get_project_imports_dir(token: str = None):
    from bkd_service import get_active_project_path
    d = get_active_project_path(token) / "imports"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_project_exports_dir(token: str = None):
    from bkd_service import get_active_project_path
    d = get_active_project_path(token) / "exports"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_project_manifest_path(token: str = None):
    from bkd_service import get_active_project_path
    return get_active_project_path(token) / "manifest.json"


def _write_retro_status(step, message, token: str = None):
    imports_dir = get_project_imports_dir(token)
    imports_dir.mkdir(parents=True, exist_ok=True)
    (imports_dir / "upload_status.json").write_text(
        json.dumps({"step": step, "message": message, "ts": datetime.now().isoformat()})
    )


@router.get("/api/retro-genome/status")
def retro_genome_status(request: Request):
    token = request.headers.get("X-User-Token")
    imports_dir = get_project_imports_dir(token)
    status_file = imports_dir / "upload_status.json"
    analysis_file = imports_dir / "last_analysis.json"

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
        except Exception:
            pass

    return res


@router.post("/api/retro-genome/chat")
async def retro_chat(body: Dict[str, Any]):
    # Implementation via SullivanArbitrator (Mission 87 simplifiee)
    # Dans le monolithe c'etait du pur routing, ici on delegue a l'Arbitre
    from sullivan_arbitrator import SullivanArbitrator
    _ARBITRATOR = SullivanArbitrator()
    config = _ARBITRATOR.pick("quick")
    res = await asyncio.to_thread(_ARBITRATOR.dispatch, config, [{"role": "user", "content": body.get("message", "") or "Analyze"}])
    return {"explanation": res.get("text", "")}


@router.post("/api/retro-genome/approve")
def retro_approve(request: Request):
    token = request.headers.get("X-User-Token")
    _write_retro_status("done", "Rendu valide par le Directeur. Pret pour export.", token)
    return {"status": "ok"}


@router.post("/api/retro-genome/export-zip")
async def retro_export_zip(request: Request):
    from Backend.Prod.retro_genome.exporter_vanilla import export_as_zip
    token = request.headers.get("X-User-Token")
    exports_dir = get_project_exports_dir(token)
    html_path = exports_dir / "reality.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="reality.html not found")
    zip_path = await asyncio.to_thread(export_as_zip, "AetherFlow_Reality", html_path.read_text(encoding="utf-8"), exports_dir)
    return {"status": "ok", "zip_path": str(zip_path)}


@router.post("/api/retro-genome/export-manifest")
async def retro_export_manifest(request: Request):
    from Backend.Prod.retro_genome.manifest_inferer import ManifestInferer
    token = request.headers.get("X-User-Token")
    exports_dir = get_project_exports_dir(token)
    html_path = exports_dir / "reality.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="reality.html not found")
    manifest = await asyncio.to_thread(asyncio.run, ManifestInferer.infer_from_html(html_path))
    out = get_project_manifest_path(token)
    ManifestInferer.save_manifest(manifest, out)
    return {"status": "ok", "manifest_path": str(out)}
