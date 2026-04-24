"""
Subject Router (M322)
Handles CRUD operations for pedagogical subjects.
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Request, Body
from pydantic import BaseModel

from bkd_service import list_subjects, get_subject, save_subject, delete_subject

# --- LOGGING ---
logger = logging.getLogger("AetherFlowV3")

# --- ROUTER ---
router = APIRouter(prefix="/api", tags=["subjects"])

# --- MODELS ---
class SubjectRef(BaseModel):
    id: str
    label: str
    criteria: Optional[str] = ""

class SubjectCriteria(BaseModel):
    id: str
    name: str
    weight: float = 1.0

class SubjectSaveRequest(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = ""
    referential: List[Dict[str, Any]] = []
    criteria: List[Dict[str, Any]] = []
    class_id: Optional[str] = None

class SubjectListItem(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""
    created_at: str

class SubjectDetail(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""
    referential: List[Dict[str, Any]]
    criteria: List[Dict[str, Any]]
    class_id: Optional[str] = None

# --- ROUTES ---

@router.get("/subjects", response_model=List[SubjectListItem])
async def get_subjects_route(class_id: Optional[str] = None):
    try:
        return list_subjects(class_id)
    except Exception as e:
        logger.error(f"Error listing subjects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subjects/{subject_id}", response_model=SubjectDetail)
async def get_subject_route(subject_id: str):
    subject = get_subject(subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject

@router.post("/subjects")
async def save_subject_route(req: SubjectSaveRequest):
    try:
        sid = save_subject(req.dict())
        return {"status": "ok", "id": sid}
    except Exception as e:
        logger.error(f"Error saving subject: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/subjects/{subject_id}")
async def delete_subject_route(subject_id: str):
    try:
        delete_subject(subject_id)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error deleting subject: {e}")
        raise HTTPException(status_code=500, detail=str(e))
