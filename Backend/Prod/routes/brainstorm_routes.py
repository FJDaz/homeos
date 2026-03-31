#!/usr/bin/env python3
"""
brainstorm_routes.py — Mission 43 Task A
Routes FastAPI pour la Phase Brainstorm (BRS) de HomeOS.
"""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel

from ..retro_genome import brainstorm_logic as logic
from ..retro_genome.brs_storage import storage

router = APIRouter(prefix="/api/brs", tags=["Brainstorm"])

# --- Modèles Pydantic ---

class DispatchRequest(BaseModel):
    session_id: str
    prompt: str
    buffer_answers: Optional[Dict[str, str]] = None

class CaptureRequest(BaseModel):
    session_id: str
    text: str
    provider: str
    source_index: Optional[int] = 0

class PRDRequest(BaseModel):
    session_id: str
    project_name: str

# --- Routes ---

@router.get("/buffer-questions")
async def get_buffer_questions():
    return logic.get_buffer_questions()

@router.post("/dispatch")
async def dispatch_brainstorm(data: DispatchRequest):
    result = await logic.dispatch_brainstorm(data.session_id, data.prompt, data.buffer_answers)
    return result

@router.get("/stream/{session_id}/{provider}")
async def stream_brainstorm(session_id: str, provider: str):
    return StreamingResponse(
        logic.sse_generator(session_id, provider),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.post("/capture")
async def capture_nugget(data: CaptureRequest):
    nugget = logic.capture_nugget(data.session_id, data.text, data.provider)
    return {"status": "ok", "nugget_id": nugget["id"]}

@router.get("/basket/{session_id}")
async def get_basket(session_id: str):
    return {"session_id": session_id, "basket": storage.get_basket(session_id)}

@router.post("/generate-prd")
async def generate_prd(data: PRDRequest):
    try:
        result = await logic.generate_prd_from_basket(data.session_id, data.project_name)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_brainstorm(q: str):
    """Recherche plein texte dans les messages BRS."""
    results = storage.search(q)
    return {"status": "ok", "query": q, "results": results}

@router.get("/arbitrate/{session_id}")
async def arbitrate_session(session_id: str):
    """Route SSE d'arbitrage Sullivan."""
    return StreamingResponse(
        logic.arbitrate_session(session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


class RankRequest(BaseModel):
    session_id: str

@router.post("/rank")
async def rank_council(body: RankRequest):
    """Mission 58 — Classement arbitré des 3 réponses COUNCIL."""
    result = await logic.rank_council(body.session_id)
    return result
