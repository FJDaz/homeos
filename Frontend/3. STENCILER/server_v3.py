#!/usr/bin/env python3
"""
AetherFlow Server V3 — Orchestrator (Mission 184)
Fichier principal < 200L. Tous les routes sont dans routers/*.py
"""

import os, json, sys, re, uuid, sqlite3, asyncio, logging, subprocess, shutil
# nest_asyncio retiré — incompatible avec uvicorn loop_factory (Python 3.14+)

import urllib.request, zipfile, io, unicodedata
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Query, Body, Request, UploadFile, File, BackgroundTasks, Form
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# --- PATHS ---
CWD = Path(__file__).parent.resolve()
ROOT_DIR = CWD.parent.parent
BACKEND_PROD = ROOT_DIR / "Backend/Prod"
PROJECTS_DIR = ROOT_DIR / "projects"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
PROJECTS_DB_PATH = ROOT_DIR / "db/projects.db"
STATIC_DIR_PATH = CWD / "static"

# --- LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AetherFlowV3")

# --- ENV ---
def _load_env():
    env_path = ROOT_DIR / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())
_load_env()

# --- IMPORTS ---
for p in [str(ROOT_DIR), str(BACKEND_PROD)]:
    if p not in sys.path: sys.path.append(p)
if str(CWD) not in sys.path: sys.path.insert(0, str(CWD))

from bkd_service import (
    SULLIVAN_BKD_SYSTEM, MANIFEST_FRD, SULLIVAN_RAG,
    exec_query_knowledge_base, route_request_bkd,
    resolve_bkd_project_root, bkd_safe_path, bkd_build_tree,
    BKD_DB_PATH, bkd_db, PROJECTS_DIR,
    get_active_project_id as _bkd_get_active_id,
    set_active_project_id as _bkd_set_active_id,
    get_active_project_path as _bkd_get_active_path,
)
from sullivan_arbitrator import SullivanArbitrator, SullivanPulse

try:
    from Backend.Prod.retro_genome.manifest_validator import validate_html, format_system_prompt_constraint, load_manifest, get_manifest_path
except ImportError:
    def validate_html(n, c): return True, []
    def format_system_prompt_constraint(n): return ""
    def load_manifest(n): return {}
    def get_manifest_path(n): return None

try:
    from sullivan.context_pruner import prune_genome
    from Backend.Prod.retro_genome.analyzer import RetroGenomeAnalyzer
    from Backend.Prod.retro_genome.intent_mapper import IntentMapper
    from Backend.Prod.retro_genome.html_generator import HtmlGenerator
    from Backend.Prod.retro_genome import brainstorm_logic as cadrage_logic
except ImportError as e:
    logger.warning(f"Legacy modules missing: {e}")

from wire_analyzer import WireAnalyzer
from Backend.Prod.retro_genome.routes import router as retro_genome_router

# --- GLOBAL STATE ---
_ARBITRATOR = SullivanArbitrator()
_PULSE = SullivanPulse()
_CURRENT_FRD_CONTEXT = {}
_NEW_IMPORTS_COUNT = 0
_KIMI_JOBS: Dict[str, Dict[str, Any]] = {}
_KIMI_JOBS_LOCK = asyncio.Lock()
_wire_preview_html = ""
_FONT_PATH_CACHE = {}
GENOME_FILE = ROOT_DIR / "Frontend/2. GENOME/genome_enriched.json"
LAYOUT_FILE = ROOT_DIR / "Frontend/2. GENOME/layout.json"
PIPELINE_DIR = ROOT_DIR / "exports" / "pipeline"
RETRO_DIR = ROOT_DIR / "exports" / "retro_genome"

# --- LIFESPAN ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    _PULSE.start()
    logger.info("Sullivan Pulse started")

    # M275: API URLs refresh — DÉSACTIVÉ (bloque event loop via Gemini grounding au démarrage)
    # logger.info("[API URLs] Background refresh disabled")

    yield
    logger.info("Server shutting down")

# --- APP ---
app = FastAPI(title="AetherFlow Server V3", version="3.0.0", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*", "null"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

# --- MISSION 190 : AUTH MIDDLEWARE ---
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response

class AuthMiddleware(BaseHTTPMiddleware):
    """Lit X-User-Token → résout user_id → injecte request.state.user_id."""
    EXEMPT_PATHS = ["/api/auth/", "/login", "/static", "/docs", "/openapi.json", "/.well-known"]

    @staticmethod
    def _lookup_user(token: str) -> int | None:
        """Résout user_id depuis un token UUID legacy ou un JWT M313."""
        # JWT M313 : commence par eyJ → décoder directement
        if token.startswith("eyJ"):
            try:
                from core.auth_utils import decode_access_token
                payload = decode_access_token(token)
                if payload and payload.get("user_id"):
                    return payload["user_id"]
            except Exception:
                pass
        # Legacy UUID token : chercher en DB
        with bkd_db() as conn:
            row = conn.execute("SELECT id FROM users WHERE token = ?", (token,)).fetchone()
            return row[0] if row else None

    async def dispatch(self, request: StarletteRequest, call_next):
        # Exempt paths
        if any(request.url.path.startswith(p) for p in self.EXEMPT_PATHS):
            request.state.user_id = None
            return await call_next(request)

        token = request.headers.get("X-User-Token")
        request.state.user_id = None

        if token:
            try:
                loop = asyncio.get_event_loop()
                user_id = await loop.run_in_executor(None, self._lookup_user, token)
                if user_id:
                    request.state.user_id = user_id
                else:
                    print(f"[M298-MW] {request.url.path} — token={token[:8]}... → user NOT FOUND")
            except Exception as e:
                print(f"[M298-MW] {request.url.path} — middleware error: {e}")
        else:
            if request.url.path == "/api/projects":
                print(f"[M298-MW] {request.url.path} — NO token in headers → user_id=None → fallback legacy (ALL projects)")

        return await call_next(request)

app.add_middleware(AuthMiddleware)

# --- STATIC ---
app.mount("/static", StaticFiles(directory=str(STATIC_DIR_PATH)), name="static")

# --- MOUNT RETRO GENOME (existing external router) ---
app.include_router(retro_genome_router, prefix="/api")

# --- MOUNT ALL ROUTERS (Mission 184) ---
from routers.wire_router import router as wire_router
from routers.sullivan_router import router as sullivan_router
from routers.projects_router import router as projects_router
from routers.frd_router import router as frd_router
from routers.bkd_router import router as bkd_router
from routers.cadrage_router import router as cadrage_router
from routers.workspace_router import router as workspace_router
from routers.import_router import router as import_router
from routers.manifest_router import router as manifest_router
from routers.preview_router import router as preview_router
from routers.genome_router import router as genome_router
from routers.retro_router import router as retro_router
from routers.class_router import router as class_router
from routers.page_router import router as page_router
from routers.auth_router import router as auth_router
from routers.stitch_router import router as stitch_router
from routers.subject_router import router as subject_router

app.include_router(wire_router)
app.include_router(sullivan_router)
app.include_router(projects_router)
app.include_router(frd_router)
app.include_router(bkd_router)
app.include_router(cadrage_router)
app.include_router(workspace_router)
app.include_router(import_router)
app.include_router(manifest_router)
app.include_router(preview_router)
app.include_router(genome_router)
app.include_router(retro_router)
app.include_router(page_router)
app.include_router(auth_router)
app.include_router(stitch_router)
app.include_router(class_router)
app.include_router(subject_router)

# --- M274: Health/Debug endpoint ---
@app.get("/api/health")
async def health_check():
    """Debug endpoint to check DB state."""
    import sqlite3
    result = {"status": "ok", "seed": None}
    try:
        db_path = PROJECTS_DB_PATH
        result["db_path"] = str(db_path)
        result["db_exists"] = db_path.exists()
        if db_path.exists():
            with bkd_db() as conn:
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
                result["tables"] = [r[0] for r in cur.fetchall()]
                if "classes" in result["tables"]:
                    cur.execute("SELECT COUNT(*) FROM classes")
                    result["class_count"] = cur.fetchone()[0]
                    cur.execute("SELECT id, name, owner_id FROM classes LIMIT 5")
                    result["classes"] = [dict(zip(["id","name","owner_id"], r)) for r in cur.fetchall()]
                if "students" in result["tables"]:
                    cur.execute("SELECT COUNT(*) FROM students")
                    result["student_count"] = cur.fetchone()[0]
        # Check seed log
        seed_log = db_path.parent / "seed.log"
        if seed_log.exists():
            result["seed_log"] = seed_log.read_text()
    except Exception as e:
        result["error"] = str(e)
    return result

from bkd_service import get_active_project_id, set_active_project_id, get_active_project_path

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server_v3:app", host="0.0.0.0", port=9998, workers=1, timeout_keep_alive=5, reload=False)
