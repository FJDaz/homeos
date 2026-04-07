"""
Stitch Router — Mission 201-A
Import direct depuis Stitch via API HTTP.
Remplace l'upload SVG pour les projets Stitch.
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

import asyncio
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel

logger = logging.getLogger("AetherFlowV3")

router = APIRouter(prefix="/api/stitch")

# --- PATHS ---
CWD = Path(__file__).parent.parent.resolve()
ROOT_DIR = CWD.parent.parent
PROJECTS_DIR = ROOT_DIR / "projects"
STITCH_API_KEY = os.getenv("STITCH_API_KEY", "")


# --- MODELS ---
class PullRequest(BaseModel):
    project_id: str
    screen_name: Optional[str] = None

class PushRequest(BaseModel):
    project_id: str
    screen_intent: str  # Intention libre ex: "page d'accueil avec hero et CTA principal"

class PullResponse(BaseModel):
    screens: list = []
    imported: Optional[str] = None
    design_md_written: bool = False

class StatusResponse(BaseModel):
    connected: bool
    api_key_set: bool


class SyncPushRequest(BaseModel):
    stitch_id: str
    instructions: str


# --- ROUTES ---
@router.get("/status")
async def stitch_status():
    """Vérifie que Stitch est configuré et joignable."""
    return StatusResponse(
        connected=bool(STITCH_API_KEY),
        api_key_set=bool(STITCH_API_KEY)
    )


@router.get("/session")
async def stitch_session():
    """Source de vérité live : état du projet Stitch vs imports locaux."""
    if not STITCH_API_KEY:
        raise HTTPException(status_code=501, detail="Stitch non configuré — ajoutez STITCH_API_KEY au .env")

    try:
        # Charger manifest pour récupérer project_id
        active_file = ROOT_DIR / "active_project.json"
        active_id = None
        if active_file.exists():
            active_id = json.loads(active_file.read_text()).get("active_id")

        manifest_path = PROJECTS_DIR / (active_id or "default") / "manifest.json"
        manifest = {}
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))

        project_id = manifest.get("stitch_project_id")
        if not project_id:
            return {"linked": False}

        # Fetch live depuis Stitch via MCP
        from core.stitch_client import StitchClient
        client = StitchClient()
        project_data = client.get_project_data(project_id)
        stitch_screens = project_data.get("screenInstances", [])

        # Imports locaux déjà tirés
        imports_dir = PROJECTS_DIR / (active_id or "default") / "imports"
        local_files = set(f.stem for f in imports_dir.glob("stitch_*.html")) if imports_dir.exists() else set()

        screens = []
        for s in stitch_screens:
            full_name = s.get("name", "")
            short_id = full_name.split("/")[-1]
            title = s.get("title", short_id)
            safe = "stitch_" + "".join(c if c.isalnum() or c in "-_ " else "_" for c in title).strip().replace(" ", "_")[:60]
            screens.append({
                "stitch_id": short_id,
                "title": title,
                "local": safe in local_files,
                "local_file": f"{safe}.html" if safe in local_files else None
            })

        return {
            "linked": True,
            "project_id": project_id,
            "project_title": project_data.get("title", project_id),
            "screens": screens
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stitch session failed: {e}")
        # Fallback : retourner les données du manifest si MCP échoue
        active_file = ROOT_DIR / "active_project.json"
        active_id = None
        if active_file.exists():
            active_id = json.loads(active_file.read_text()).get("active_id")
        manifest_path = PROJECTS_DIR / (active_id or "default") / "manifest.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            project_id = manifest.get("stitch_project_id")
            if project_id:
                return {"linked": True, "project_id": project_id, "project_title": project_id, "screens": [], "offline": True}
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-push")
async def stitch_sync_push(req: SyncPushRequest):
    """
    Pousse une modification vers l'écran Stitch source.
    body: { stitch_id: str, instructions: str }
    → appelle edit_screen({ name: "projects/{pid}/screens/{stitch_id}", instructions })
    """
    if not STITCH_API_KEY:
        raise HTTPException(status_code=501, detail="Stitch non configuré")

    try:
        # Récupérer project_id depuis manifest
        active_file = ROOT_DIR / "active_project.json"
        active_id = None
        if active_file.exists():
            active_id = json.loads(active_file.read_text()).get("active_id")

        manifest_path = PROJECTS_DIR / (active_id or "default") / "manifest.json"
        if not manifest_path.exists():
            raise HTTPException(status_code=404, detail="manifest.json introuvable")

        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        project_id = manifest.get("stitch_project_id")
        if not project_id:
            raise HTTPException(status_code=400, detail="stitch_project_id non configuré dans manifest.json")

        from core.stitch_client import StitchClient
        client = StitchClient()
        result = client.edit_screen(project_id, req.stitch_id, req.instructions)

        logger.info(f"Stitch SYNC-PUSH: edited screen {req.stitch_id} in project {project_id}")
        return {"success": True, "stitch_id": req.stitch_id, "result": result}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stitch sync-push failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/screens")
async def stitch_screens(project_id: str):
    """Liste les écrans disponibles dans le projet Stitch."""
    if not STITCH_API_KEY:
        raise HTTPException(status_code=501, detail="Stitch non configuré — ajoutez STITCH_API_KEY au .env")

    try:
        from core.stitch_client import StitchClient
        client = StitchClient()
        data = client.get_project_data(project_id)
        # Stitch retourne screenInstances (pas screens)
        raw_screens = data.get("screenInstances", data.get("screens", []))
        # Normaliser : extraire le nom court depuis le resource name (ex: "projects/123/screens/home" → "home")
        screens = []
        for s in raw_screens:
            full_name = s.get("name", s.get("id", ""))
            short_name = full_name.split("/")[-1] if "/" in full_name else full_name
            screens.append({"name": short_name, "full_name": full_name, "title": s.get("title", short_name)})
        return {"screens": screens}
    except Exception as e:
        logger.error(f"Stitch screens fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _patch_manifest_stitch_project_id(project_id: str):
    """Stocke stitch_project_id dans manifest.json après un premier pull réussi."""
    try:
        active_file = ROOT_DIR / "active_project.json"
        active_id = None
        if active_file.exists():
            active_id = json.loads(active_file.read_text()).get("active_id")

        manifest_path = PROJECTS_DIR / (active_id or "default") / "manifest.json"
        manifest = {}
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))

        if manifest.get("stitch_project_id") != project_id:
            manifest["stitch_project_id"] = project_id
            manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
            logger.info(f"Manifest patched: stitch_project_id = {project_id}")
    except Exception as e:
        logger.warning(f"Failed to patch manifest with stitch_project_id: {e}")


@router.post("/pull")
async def stitch_pull(request: Request, req: PullRequest):
    """
    Importe un écran Stitch dans le projet actif.
    - Si screen_name absent → retourne la liste des écrans disponibles
    - Si screen_name présent → télécharge le HTML + Design DNA
    - Mémorise stitch_project_id dans manifest.json
    """
    if not STITCH_API_KEY:
        raise HTTPException(status_code=501, detail="Stitch non configuré — ajoutez STITCH_API_KEY au .env")

    try:
        from core.stitch_client import StitchClient
        client = StitchClient()

        if not req.screen_name:
            return {"screens": [], "imported": None, "design_md_written": False}

        # Télécharger directement — pas de validation (le listing a déjà confirmé l'existence)
        # screen_name = segment court (ex: "11b1df51...") issu du resource path Stitch
        screen_data = client.get_screen_code(req.project_id, req.screen_name)
        logger.info(f"Stitch screen_data keys: {list(screen_data.keys())}")
        logger.info(f"Stitch screen_data['screen_data'] keys: {list(screen_data.get('screen_data', {}).keys())}")
        logger.info(f"Stitch screen_data dump: {str(screen_data)[:800]}")
        html = screen_data.get("html", screen_data.get("code", ""))

        if not html:
            raise HTTPException(status_code=500, detail="No HTML returned from Stitch")

        # 4. Sauvegarder dans imports/ du projet actif
        user_id = getattr(request.state, 'user_id', None)
        active_file = ROOT_DIR / "active_project.json"
        active_id = None
        if active_file.exists():
            active_id = json.loads(active_file.read_text()).get("active_id")

        imports_dir = PROJECTS_DIR / (active_id or "default") / "imports"
        imports_dir.mkdir(parents=True, exist_ok=True)

        # Utiliser le titre Stitch comme nom de fichier si disponible
        raw_screen = screen_data.get("screen_data", {})
        title = raw_screen.get("title", raw_screen.get("displayName", req.screen_name))
        safe_title = "".join(c if c.isalnum() or c in "-_ " else "_" for c in title).strip().replace(" ", "_")[:60]
        filename = f"stitch_{safe_title}.html" if safe_title else f"stitch_{req.screen_name[:12]}.html"

        import_path = imports_dir / filename
        import_path.write_text(html, encoding='utf-8')

        # 4b. Enregistrer dans index.json + copier dans static/templates/ (même pipeline que upload manuel)
        try:
            from pathlib import Path as _Path
            static_dir = CWD / "static"
            templates_dir = static_dir / "templates"
            templates_dir.mkdir(parents=True, exist_ok=True)
            tpl_filename = f"stitch_{safe_title}.html"
            (templates_dir / tpl_filename).write_text(html, encoding='utf-8')

            exports_dir = PROJECTS_DIR / (active_id or "default") / "exports"
            exports_dir.mkdir(parents=True, exist_ok=True)
            index_path = exports_dir / "index.json"
            index_data = json.loads(index_path.read_text(encoding='utf-8')) if index_path.exists() else {"imports": []}

            today_str = datetime.now().strftime("%Y%m%d")
            ts_str = datetime.now().strftime("%H%M%S")
            new_entry = {
                "id": f"{today_str}_{ts_str}_{safe_title}",
                "name": filename,
                "timestamp": datetime.now().isoformat(),
                "file_path": filename,
                "date": today_str,
                "type": "html",
                "archetype_id": "stitch_import",
                "archetype_label": f"Stitch — {title}",
                "html_template": tpl_filename,
                "elements_count": 0
            }
            index_data["imports"].insert(0, new_entry)
            index_data["imports"] = index_data["imports"][:50]
            index_path.write_text(json.dumps(index_data, indent=2, ensure_ascii=False), encoding='utf-8')
        except Exception as e:
            logger.warning(f"Stitch index registration failed (non-blocking): {e}")

        # 5. Design DNA → DESIGN.md (uniquement si absent)
        design_md_written = False
        try:
            dna = client.get_design_dna(req.project_id)
            project_dir = PROJECTS_DIR / (active_id or "default")
            design_path = project_dir / "DESIGN.md"
            if not design_path.exists():
                # Convertir DNA en DESIGN.md minimal
                tokens = dna.get("tokens", {})
                content = f"""# DESIGN.md — {req.project_id}

## Colors
{json.dumps(tokens.get('colors', {}), indent=2)}

## Typography
{json.dumps(tokens.get('typography', {}), indent=2)}

## Spacing
{json.dumps(tokens.get('spacing', {}), indent=2)}
"""
                design_path.write_text(content, encoding='utf-8')
                design_md_written = True
        except Exception as e:
            logger.warning(f"Stitch Design DNA fetch failed (non-blocking): {e}")

        logger.info(f"Stitch PULL: imported {filename} → {import_path}")

        # Mémoriser project_id dans manifest.json
        _patch_manifest_stitch_project_id(req.project_id)

        return {
            "screens": [],
            "imported": filename,
            "design_md_written": design_md_written
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stitch pull failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- PUSH & TASK LOGIC ---

async def run_stitch_push_task(task_id: str, project_id: str, screen_intent: str):
    from core.task_manager import TaskManager
    from core.stitch_client import StitchClient
    from core.stitch_prompt_builder import StitchPromptBuilder
    import sys

    status = TaskManager.get_task(task_id)
    if not status: return

    try:
        # Résoudre le projet AetherFlow actif
        active_file = ROOT_DIR / "active_project.json"
        active_id = None
        if active_file.exists():
            active_id = json.loads(active_file.read_text()).get("active_id")

        project_dir = PROJECTS_DIR / (active_id or "default")
        if not project_dir.exists():
            status.update("error", "Projet actif introuvable", success=False)
            return

        # 1. Compiler le brief depuis le genome/manifest
        status.update("compiling_genome", "Sullivan compile le génome de votre projet...")
        builder = StitchPromptBuilder(project_dir)
        prompt = builder.build(screen_intent)

        # 2. Envoyer à Stitch
        status.update("calling_stitch", "Transmission de l'ADN design à l'imaginaire Stitch...")
        client = StitchClient()
        result = client.generate_screen_from_text(prompt, project_id)

        screen_name = result.get("name", result.get("screenId", "generated"))
        preview_url = result.get("previewUrl") or result.get("preview_url")

        # 3. Success
        status.update("success", f"L'écran '{screen_name}' a été généré dans Stitch.",
                      success=True, data={
                          "screen_name": screen_name,
                          "preview_url": preview_url,
                          "prompt_length": len(prompt)
                      })
        logger.info(f"Stitch PUSH Success: {task_id} → {screen_name}")

    except Exception as e:
        logger.error(f"Stitch PUSH Task Failed: {e}")
        status.update("error", f"Erreur lors de la génération : {str(e)}", success=False, error=str(e))


@router.post("/push")
async def stitch_push(req: PushRequest, background_tasks: BackgroundTasks):
    """Lance une génération d'écran Stitch en arrière-plan depuis le genome du projet."""
    if not STITCH_API_KEY:
        raise HTTPException(status_code=501, detail="Stitch non configuré")

    from core.task_manager import TaskManager
    status = TaskManager.create_task()

    background_tasks.add_task(run_stitch_push_task, status.task_id, req.project_id, req.screen_intent)

    return {"task_id": status.task_id}


@router.get("/task/{task_id}")
async def stitch_task_status(task_id: str):
    """Retourne l'état d'avancement d'une tâche Stitch."""
    from core.task_manager import TaskManager
    status = TaskManager.get_task(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return status.to_dict()
