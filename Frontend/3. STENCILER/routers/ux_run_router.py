import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Request, Query, Body
from pydantic import BaseModel

logger = logging.getLogger("AetherFlowV3.UXRun")

router = APIRouter()

# --- PATHS ---
ROOT_DIR = Path(__file__).parent.parent.parent.parent.resolve()
LOG_FILE = ROOT_DIR / "logs" / "ux_run.ndjson"

class UXEvent(BaseModel):
    tag: str
    label: str
    ts: float
    path: Optional[str] = None
    project_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

@router.post("/api/ux-run/event")
async def ux_run_event(event: UXEvent):
    """
    Mission M375 : Enregistre un événement UX dans le log NDJSON.
    """
    try:
        # Création du dossier logs si absent (sécurité)
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Préparation de la ligne NDJSON
        data = event.dict()
        data["received_at"] = datetime.now().isoformat()
        
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
            
        # Log serveur classique pour monitoring temps réel
        logger.info(f"[UX-SIGNAL] {event.tag} | {event.label} | project={event.project_id}")
        
        return {"ok": True}
    except Exception as e:
        logger.error(f"Failed to log UX event: {e}")
        return {"ok": False, "error": str(e)}

@router.get("/api/ux-run/session")
async def ux_run_get_session(last: int = Query(50)):
    """
    Mission M375 : Retourne les N derniers événements enregistrés.
    """
    if not LOG_FILE.exists():
        return {"events": []}
        
    try:
        events = []
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            # On lit tout pour pouvoir trier/filtrer facilement
            # (Fichier éphémère, donc pas de souci de perfs ici)
            lines = f.readlines()
            
        for line in lines[-last:]:
            if line.strip():
                events.append(json.loads(line))
                
        return {"events": events}
    except Exception as e:
        logger.error(f"Failed to read UX session: {e}")
        return {"events": [], "error": str(e)}
