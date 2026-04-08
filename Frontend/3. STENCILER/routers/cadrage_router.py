from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse, HTMLResponse
import json
import logging
import asyncio

logger = logging.getLogger("CadrageRouter")

CWD = Path(__file__).parent.parent.resolve()
ROOT_DIR = CWD.parent.parent
STATIC_DIR_PATH = CWD / "static"

from Backend.Prod.retro_genome import brainstorm_logic as cadrage_logic

router = APIRouter()


@router.get("/api/cadrage/chat/{provider}")
async def cadrage_chat_sse(provider: str, session_id: str = Query(...), message: str = Query(...), class_id: str = Query(None), project_id: str = Query(None)):
    """SSE endpoint for multi-model chat in Cadrage. M226: project_id + class_id injection."""
    async def generate():
        try:
            async for chunk in cadrage_logic.sse_chat_generator(session_id, provider, message, class_id=class_id, project_id=project_id):
                yield chunk
        except Exception as e:
            logger.error(f"Cadrage Chat SSE Error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/api/cadrage/capture")
async def cadrage_capture(body: dict):
    try:
        return await asyncio.to_thread(cadrage_logic.handle_capture, body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/cadrage/generate-prd")
async def cadrage_generate_prd(body: dict):
    try:
        return await asyncio.to_thread(cadrage_logic.generate_prd, body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/cadrage/rank")
async def cadrage_rank(body: dict):
    try:
        return await asyncio.to_thread(cadrage_logic.handle_rank, body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cadrage")
async def get_cadrage():
    path = STATIC_DIR_PATH / "templates/cadrage_alt.html"
    if not path.exists():
        raise HTTPException(status_code=404)
    return HTMLResponse(content=path.read_text(encoding="utf-8"))


@router.get("/cadrage-alt")
async def get_cadrage_alt():
    path = STATIC_DIR_PATH / "templates/cadrage_alt.html"
    if not path.exists():
        raise HTTPException(status_code=404)
    return HTMLResponse(content=path.read_text(encoding="utf-8"))
