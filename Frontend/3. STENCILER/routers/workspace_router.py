from pathlib import Path
import sys
import json
import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from bs4 import BeautifulSoup

logger = logging.getLogger("WorkspaceRouter")

CWD = Path(__file__).parent.parent.resolve()
ROOT_DIR = CWD.parent.parent
STATIC_DIR_PATH = CWD / "static"
PROJECTS_DIR = ROOT_DIR / "projects"

router = APIRouter()


def get_active_project_path():
    from bkd_service import get_active_project_path
    return get_active_project_path()


class GraftRequest(BaseModel):
    filename: str
    selector: str
    html_content: str


@router.get("/workspace")
async def get_workspace_editor():
    """Mission 127: Unified Workspace Canvas"""
    path = STATIC_DIR_PATH / "templates/workspace.html"
    return FileResponse(path)


@router.get("/api/workspace/templates")
async def list_workspace_templates():
    """Mission 110: Liste les templates de base pour le workspace."""
    tpl_dir = STATIC_DIR_PATH / "templates"
    if not tpl_dir.exists():
        return {"templates": []}

    # On filtre pour ne garder que les templates "nobles" (pas les imports ou tmp)
    files = []
    for f in tpl_dir.glob("*.html"):
        if f.name.startswith(("import_", "reality_", "_")):
            continue
        files.append({"name": f.name.replace(".html", ""), "tpl": f.name})

    return {"templates": sorted(files, key=lambda x: x["name"])}


@router.get("/api/workspace/tokens")
async def get_workspace_tokens():
    """
    Mission 159 : Design System Intendant.
    Retourne les jetons de design du projet actif (ou HomeOS par defaut).
    """
    try:
        project_path = get_active_project_path()
        tokens_path = project_path / "design_tokens.json"

        if tokens_path.exists():
            with open(tokens_path, "r", encoding="utf-8") as f:
                return json.load(f)

        # Fallback HomeOS Standard
        return {
            "fonts": ["Source Sans 3", "Geist", "Inter", "Roboto"],
            "colors": {
                "palette": ["#A3CD54", "#1a1a1a", "#f5f5f5", "#ffffff", "#64748b"],
                "allowCustomColors": True
            },
            "effects": {
                "allowShadows": True,
                "allowBorders": True,
                "allowRadius": True,
                "defaultRadius": "20px"
            }
        }
    except Exception as e:
        logger.error(f"Error fetching design tokens: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/workspace/graft")
async def workspace_graft(payload: GraftRequest):
    """
    Graft a new HTML snippet into an existing template file based on a CSS selector.
    """
    try:
        # Resolve project path
        project_path = get_active_project_path()
        file_path = project_path / payload.filename

        if not file_path.exists():
            # Fallback to static/templates if not in project
            file_path = STATIC_DIR_PATH / "templates" / payload.filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {payload.filename}")

        # Read content
        content = file_path.read_text(encoding="utf-8")

        # Parse with BS4
        soup = BeautifulSoup(content, "lxml" if "lxml" in sys.modules else "html.parser")

        # Find element
        target = soup.select_one(payload.selector)
        if not target:
            raise HTTPException(status_code=400, detail=f"Target element not found in {payload.filename} for selector: {payload.selector}")

        # Replace element
        new_tag = BeautifulSoup(payload.html_content, "html.parser")
        target.replace_with(new_tag)

        # Save back
        file_path.write_text(str(soup), encoding="utf-8")

        logger.info(f"[Workspace] Grafted snippet into {payload.filename} via {payload.selector}")
        return {"status": "success", "file": payload.filename}

    except Exception as e:
        logger.error(f"[Workspace] Grafting failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
