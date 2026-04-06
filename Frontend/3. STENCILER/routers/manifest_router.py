from pathlib import Path
import json
import re
import logging
from datetime import datetime
from typing import Any, Dict
from fastapi import APIRouter, HTTPException

logger = logging.getLogger("ManifestRouter")

CWD = Path(__file__).parent.parent.resolve()
ROOT_DIR = CWD.parent.parent

router = APIRouter()


def get_active_project_path():
    from bkd_service import get_active_project_path
    return get_active_project_path()


def get_project_manifest_path():
    return get_active_project_path() / "manifest.json"


@router.get("/api/manifest/check")
async def manifest_check():
    """Check if manifest.json and design.md exist."""
    m_path = ROOT_DIR / "manifest.json"
    d_path = ROOT_DIR / "design.md"
    b_path = ROOT_DIR / "backend.md"
    return {
        "exists": m_path.exists(),
        "stitch_ready": d_path.exists(),
        "backend_ready": b_path.exists()
    }


@router.get("/api/manifest/backend")
async def manifest_backend_get():
    """Get backend.md content."""
    b_path = get_active_project_path() / "backend.md"
    if not b_path.exists():
        return {"content": "# HomeOS Backend Manifest\n\n*Not initialized*"}
    return {"content": b_path.read_text(encoding="utf-8")}


@router.put("/api/manifest/backend")
async def manifest_backend_put(data: Dict[str, str]):
    """Update backend.md content."""
    b_path = get_active_project_path() / "backend.md"
    content = data.get("content", "")
    b_path.write_text(content, encoding="utf-8")
    return {"ok": True}


@router.post("/api/manifest/import-stitch")
async def manifest_import_stitch():
    """Parse design.md and sync with backend.md."""
    d_path = get_active_project_path() / "design.md"
    b_path = get_active_project_path() / "backend.md"
    if not d_path.exists():
        raise HTTPException(status_code=404, detail="design.md not found in project")

    design_content = d_path.read_text(encoding="utf-8")

    # Simple Heuristic Parser for Stitch design.md
    components = []
    # Identify: ### Component[intent] or # intent: POST /api/...
    comp_matches = re.finditer(r"###\s+([\w\-]+)\[([\w\-]+)\]", design_content)
    intent_matches = re.finditer(r"-\s+Intent:\s+(GET|POST|PUT|DELETE)\s+([^\n\r]+)", design_content)

    findings = []
    for m in comp_matches:
        name, action = m.group(1), m.group(2)
        route = f"POST /api/{name.lower()}/{action.lower()}"
        findings.append(f"| {name}[{action}] | {route} | 🔴 Backlog |")

    for m in intent_matches:
        method, path = m.group(1), m.group(2).strip()
        findings.append(f"| Stitch Direct | {method} {path} | 🔴 Backlog |")

    # Generate Markdown Table
    table_content = "\n".join(findings)
    new_backend_md = f"""# HomeOS Backend Manifest

## 🗺️ Intent Map (Synchronise depuis Stitch)
| Composant | Route API | Statut |
| :--- | :--- | :--- |
{table_content}

## 🧪 Tests & Qualite
- [ ] Verifier la bijection semantique avec Wire V5
- [ ] Valider les schemas JSON (Pydantic)
- [ ] Tester les timeouts Sullivan
"""

    # Merge strategy: If file exists, we'll try to keep manual notes (not implemented for complexity, but plan says override for now)
    b_path.write_text(new_backend_md, encoding="utf-8")

    return {"ok": True, "count": len(findings), "manifest": new_backend_md}


@router.get("/api/manifest/get")
async def manifest_get():
    """Get the current manifest.json content."""
    m_path = get_project_manifest_path()
    if not m_path.exists():
        raise HTTPException(status_code=404, detail="manifest.json not found in project")
    with open(m_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    return manifest


@router.post("/api/manifest/create")
async def manifest_create(data: Dict[str, Any]):
    """Create a new manifest.json with project metadata."""
    m_path = get_project_manifest_path()
    if m_path.exists():
        return {"ok": False, "error": "manifest.json already exists in project"}

    name = data.get("name", "unnamed-project")
    author = data.get("author", "unknown")
    description = data.get("description", "")

    manifest = {
        "name": name,
        "author": author,
        "description": description,
        "created_at": datetime.now().isoformat(),
        "version": "0.1.0",
        "elements": [],
        "intents": []
    }

    with open(m_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    logger.info(f"manifest.json created: {name} by {author}")
    return {"ok": True, "manifest": manifest}


@router.post("/api/manifest/patch")
async def manifest_patch(patch: Dict[str, Any]):
    m_path = get_project_manifest_path()
    if not m_path.exists():
        raise HTTPException(status_code=404)
    with open(m_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    if "elements" in patch:
        for p_el in patch["elements"]:
            for el in manifest.get("elements", []):
                if el.get("id") == p_el.get("id"):
                    el.update(p_el)
                    break
    with open(m_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    return {"ok": True}
