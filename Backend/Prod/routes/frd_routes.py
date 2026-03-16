#!/usr/bin/env python3
"""
frd_routes.py — Mission 45
Routes FastAPI pour la gestion des templates (FRD).
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any
from .retro_genome import frd_logic as logic

router = APIRouter(prefix="/api/frd", tags=["FRD - Editor"])

class TemplateSave(BaseModel):
    name: str
    content: str

@router.get("/file")
async def get_template(name: str = Query(..., description="Nom du template (ex: brainstorm_war_room.html)")):
    """ Récupère le contenu d'un template. """
    try:
        content = logic.read_template(name)
        return {"status": "ok", "name": name, "content": content}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/file")
async def save_template(data: TemplateSave):
    """ Sauvegarde le contenu d'un template. """
    try:
        logic.write_template(data.name, data.content)
        return {"status": "ok", "message": "Sauvegardé ✓"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
