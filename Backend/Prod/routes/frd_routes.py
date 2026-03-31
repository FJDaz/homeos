#!/usr/bin/env python3
"""
frd_routes.py — Mission 45 + Manifeste DOM
Routes FastAPI pour la gestion des templates (FRD).

Validation manifeste (contrôle en sortie) :
  POST /api/frd/file → valide le HTML contre <name>_manifest.json avant écriture.
  Violation = HTTP 422 avec liste précise des violations. Aucune exception.

Routes manifeste :
  GET /api/frd/manifest/{name} → retourne le manifeste JSON du template.
  GET /api/frd/manifest/{name}/prompt → retourne le bloc système prompt à injecter.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any
from ..retro_genome import frd_logic as logic
from ..retro_genome.manifest_validator import validate_html, load_manifest, format_system_prompt_constraint

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
    """
    Sauvegarde le contenu d'un template.

    Si un manifeste existe pour ce template, le HTML est validé AVANT écriture.
    Toute violation → HTTP 422 avec la liste précise des violations.
    Aucune écriture partielle, aucune heuristique, aucune exception.
    """
    is_valid, errors = validate_html(data.name, data.content)
    if not is_valid:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "CONTRAT DOM VIOLÉ",
                "file": data.name,
                "violations_count": len(errors),
                "violations": errors,
                "message": (
                    f"Le HTML contient {len(errors)} violation(s) du manifeste. "
                    "Aucune écriture effectuée. Corrigez toutes les violations avant de sauvegarder."
                )
            }
        )
    try:
        logic.write_template(data.name, data.content)
        return {"status": "ok", "message": "Sauvegardé ✓"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/manifest/{name}")
async def get_manifest(name: str):
    """
    Retourne le manifeste JSON du template.
    Usage : injection dans les prompts agents avant toute modification HTML.
    """
    manifest = load_manifest(name)
    if manifest is None:
        raise HTTPException(status_code=404, detail=f"Aucun manifeste pour '{name}'.")
    return manifest

@router.get("/manifest/{name}/prompt")
async def get_manifest_prompt(name: str):
    """
    Retourne le bloc de contrainte système à injecter dans tout prompt agent
    qui va modifier ce template. Format texte brut (pas JSON).
    """
    prompt = format_system_prompt_constraint(name)
    if not prompt:
        raise HTTPException(status_code=404, detail=f"Aucun manifeste pour '{name}'.")
    return {"constraint_prompt": prompt}
