from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

CWD = Path(__file__).parent.parent.resolve()
STATIC_DIR_PATH = CWD / "static"

router = APIRouter()


@router.get("/stenciler")
async def get_stenciler_redirect():
    """Mission 168: Redirect ancien /stenciler -> /workspace (architecture hexagonale M156)."""
    return RedirectResponse(url="/workspace", status_code=301)


@router.get("/stenciler_v3")
async def get_stenciler_v3_redirect():
    """Mission 168: Redirect ancien /stenciler_v3 -> /workspace."""
    return RedirectResponse(url="/workspace", status_code=301)


@router.get("/bkd")
async def get_bkd_editor():
    path = STATIC_DIR_PATH / "templates/bkd_editor.html"
    if not path.exists():
        raise HTTPException(status_code=404, detail="bkd_editor.html not yet generated")
    return FileResponse(path)


@router.get("/frd-editor")
async def get_frd_editor():
    path = STATIC_DIR_PATH / "templates/frd_editor.html"
    return FileResponse(path)


@router.get("/bkd-frd")
async def get_bkd_frd():
    path = STATIC_DIR_PATH / "templates/bkd_frd.html"
    if not path.exists():
        raise HTTPException(status_code=404)
    return HTMLResponse(content=path.read_text(encoding="utf-8"))


@router.get("/brainstorm")
async def get_brainstorm():
    path = STATIC_DIR_PATH / "templates/brainstorm_war_room_tw.html"
    if not path.exists():
        raise HTTPException(status_code=404)
    return HTMLResponse(content=path.read_text(encoding="utf-8"))


@router.get("/brainstorm-alt")
async def get_brainstorm_alt():
    path = STATIC_DIR_PATH / "templates/brainstorm_alt.html"
    if not path.exists():
        raise HTTPException(status_code=404)
    return HTMLResponse(content=path.read_text(encoding="utf-8"))


@router.get("/intent-viewer")
async def get_intent_viewer():
    path = STATIC_DIR_PATH / "templates/intent_viewer.html"
    if not path.exists():
        raise HTTPException(status_code=404)
    return HTMLResponse(content=path.read_text(encoding="utf-8"))


@router.get("/")
async def get_root():
    return RedirectResponse(url="/workspace")


@router.get("/landing")
async def get_landing():
    path = STATIC_DIR_PATH / "templates/landing.html"
    if not path.exists():
        raise HTTPException(status_code=404)
    return HTMLResponse(content=path.read_text(encoding="utf-8"))
