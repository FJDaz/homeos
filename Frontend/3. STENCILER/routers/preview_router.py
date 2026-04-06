from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

CWD = Path(__file__).parent.parent.resolve()
STATIC_DIR_PATH = CWD / "static"

router = APIRouter()


@router.post("/api/preview/run")
async def preview_run(body: dict):
    """Save current HTML to a temporary file for independent tab preview."""
    html = body.get("html", "")
    p_path = STATIC_DIR_PATH / "templates/_preview_tmp.html"
    p_path.write_text(html, encoding="utf-8")
    return {"ok": True, "url": "/api/preview/show"}


@router.get("/api/preview/show")
async def preview_show():
    """Serve the temporary preview file."""
    p_path = STATIC_DIR_PATH / "templates/_preview_tmp.html"
    if not p_path.exists():
        return HTMLResponse(content="<h1>Aucun apercu genere</h1>", status_code=404)

    content = p_path.read_text(encoding="utf-8")
    return HTMLResponse(content=content, headers={"Cache-Control": "no-store"})
