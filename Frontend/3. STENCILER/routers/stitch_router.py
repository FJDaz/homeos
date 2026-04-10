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


# --- S3: Resolve Stitch API key from env or DB ---
def _get_stitch_key() -> str:
    key = os.getenv("STITCH_API_KEY", "")
    if key:
        return key
    try:
        from bkd_service import bkd_db_con
        with bkd_db_con() as con:
            row = con.execute(
                "SELECT uk.api_key FROM user_keys uk "
                "JOIN users u ON u.id = uk.user_id "
                "WHERE uk.provider = 'stitch' AND u.role IN ('admin','prof') "
                "ORDER BY u.role DESC LIMIT 1"
            ).fetchone()
            if row:
                return row[0]
    except Exception:
        pass
    return ""


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
    """Vérifie que Stitch est configuré et joignable. S3: key from env or DB."""
    key = _get_stitch_key()
    return StatusResponse(
        connected=bool(key),
        api_key_set=bool(key)
    )


@router.get("/project-info")
async def stitch_project_info():
    """M222: Retourne le stitch_project_id lié au projet HoméOS actif."""
    active_file = ROOT_DIR / "active_project.json"
    if not active_file.exists():
        return {"linked": False}

    try:
        active_data = json.loads(active_file.read_text())
        active_id = active_data.get("active_id")
    except Exception:
        return {"linked": False}

    if not active_id:
        return {"linked": False}

    manifest_path = PROJECTS_DIR / active_id / "manifest.json"
    if not manifest_path.exists():
        return {"linked": False}

    try:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        stitch_id = manifest.get("stitch_project_id")
        if not stitch_id:
            return {"linked": False}

        return {
            "linked": True,
            "stitch_project_id": stitch_id,
            "title": manifest.get("stitch_project_title", stitch_id)
        }
    except Exception as e:
        logger.warning(f"stitch_project_info error: {e}")
        return {"linked": False}


@router.get("/session")
async def stitch_session():
    """Source de vérité live : état du projet Stitch vs imports locaux."""
    if not _get_stitch_key():
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
        client = StitchClient(api_key=_get_stitch_key())
        project_data = client.get_project_data(project_id)
        stitch_screens = project_data.get("screenInstances", [])

        # Imports locaux déjà tirés
        imports_dir = PROJECTS_DIR / (active_id or "default") / "imports"
        local_files = set(f.stem for f in imports_dir.glob("stitch_*.html")) if imports_dir.exists() else set()

        screens = []
        for s in stitch_screens:
            full_name = s.get("name", "")
            short_id = full_name.split("/")[-1]
            # Intelligible name: displayName > title > short_id
            title = s.get("displayName") or s.get("title") or short_id
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
    if not _get_stitch_key():
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
        client = StitchClient(api_key=_get_stitch_key())
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
    if not _get_stitch_key():
        raise HTTPException(status_code=501, detail="Stitch non configuré — ajoutez STITCH_API_KEY au .env")

    try:
        from core.stitch_client import StitchClient
        client = StitchClient(api_key=_get_stitch_key())
        data = client.get_project_data(project_id)
        # Stitch retourne screenInstances (pas screens)
        raw_screens = data.get("screenInstances", data.get("screens", []))
        # Normaliser : extraire le nom court depuis le resource name (ex: "projects/123/screens/home" → "home")
        screens = []
        for s in raw_screens:
            full_name = s.get("name", s.get("id", ""))
            short_name = full_name.split("/")[-1] if "/" in full_name else full_name
            screens.append({"name": short_name, "full_name": full_name, "title": s.get("displayName") or s.get("title") or short_name})
        return {"screens": screens}
    except Exception as e:
        logger.error(f"Stitch screens fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _merge_design_md(project_dir: Path, dna_tokens: dict):
    """M232: Fusionne les tokens Design DNA (Stitch) dans DESIGN.md sans écraser les sections HoméOS."""
    design_path = project_dir / "DESIGN.md"
    project_name = project_dir.name

    # Préparer les nouvelles sections Stitch
    stitch_sections = {
        "Colors": f"## Colors\n{json.dumps(dna_tokens.get('colors', {}), indent=2)}\n",
        "Typography": f"## Typography\n{json.dumps(dna_tokens.get('typography', {}), indent=2)}\n",
        "Spacing": f"## Spacing\n{json.dumps(dna_tokens.get('spacing', {}), indent=2)}\n"
    }

    if not design_path.exists():
        content = f"# DESIGN.md — {project_name}\n> Source: Stitch Design DNA + règles HoméOS\n\n"
        content += stitch_sections["Colors"] + "\n"
        content += stitch_sections["Typography"] + "\n"
        content += stitch_sections["Spacing"] + "\n"
        content += "## Wire Rules\n\n"
        content += "## Interaction\n\n"
        design_path.write_text(content, encoding='utf-8')
        return True

    # Parser le fichier existant par sections "##"
    try:
        lines = design_path.read_text(encoding='utf-8').splitlines()
        existing_sections = {}
        header_lines = []
        current_section = None

        for line in lines:
            if line.startswith("## "):
                current_section = line[3:].strip()
                existing_sections[current_section] = []
            elif current_section is None:
                header_lines.append(line)
            else:
                existing_sections[current_section].append(line)

        # Reconstruire le fichier
        new_content = "\n".join(header_lines).strip() + "\n\n"
        
        # 1. Écrire les sections Stitch (toujours en premier)
        new_content += stitch_sections["Colors"] + "\n"
        new_content += stitch_sections["Typography"] + "\n"
        new_content += stitch_sections["Spacing"] + "\n"

        # 2. Préserver les autres sections (Wire Rules, Interaction, etc.)
        for sec_name, sec_lines in existing_sections.items():
            if sec_name not in ["Colors", "Typography", "Spacing"]:
                new_content += f"## {sec_name}\n" + "\n".join(sec_lines).strip() + "\n\n"

        design_path.write_text(new_content, encoding='utf-8')
        return True
    except Exception as e:
        logger.error(f"Failed to merge DESIGN.md: {e}")
        return False


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
    if not _get_stitch_key():
        raise HTTPException(status_code=501, detail="Stitch non configuré — ajoutez STITCH_API_KEY au .env")

    try:
        from core.stitch_client import StitchClient
        client = StitchClient(api_key=_get_stitch_key())

        if not req.screen_name:
            return {"screens": [], "imported": None, "design_md_written": False}

        # Fetch project data to get intelligible screen names
        project_data = client.get_project_data(req.project_id)
        screen_instances = project_data.get("screenInstances", project_data.get("screens", []))
        screen_name_map = {}
        for s in screen_instances:
            full_name = s.get("name", "")
            short_id = full_name.split("/")[-1]
            screen_name_map[short_id] = s.get("displayName") or s.get("title") or short_id
        logger.info(f"Stitch screen name map: {screen_name_map}")

        # Download screen code
        screen_data = client.get_screen_code(req.project_id, req.screen_name)
        logger.info(f"Stitch screen_data ROOT keys: {list(screen_data.keys())}")
        raw = screen_data.get("screen_data", {})
        logger.info(f"Stitch screen_data['screen_data'] keys: {list(raw.keys())}")
        # DUMP complet pour diagnostic
        logger.info(f"Stitch screen_data DUMP: {json.dumps(raw, indent=2, ensure_ascii=False)[:2000]}")
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

        # Use intelligible screen name from project data
        title = screen_name_map.get(req.screen_name, req.screen_name)
        # Also try raw_screen response for displayName/title
        raw_screen = screen_data.get("screen_data", {})
        if not title or title == req.screen_name:
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

        # 5. Design DNA → DESIGN.md (Merge Mission 232)
        design_md_written = False
        try:
            dna = client.get_design_dna(req.project_id)
            project_dir = PROJECTS_DIR / (active_id or "default")
            design_md_written = _merge_design_md(project_dir, dna.get("tokens", {}))
        except Exception as e:
            logger.warning(f"Stitch Design DNA fetch/merge failed: {e}")

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
        client = StitchClient(api_key=_get_stitch_key())
        result = client.generate_screen_from_text(prompt, project_id)

        screen_name = result.get("name", result.get("screenId", "generated"))
        preview_url = result.get("previewUrl") or result.get("preview_url")

        # M230: Extract Stitch project_id from screen_name and patch manifest
        # screen_name can be "projects/{pid}/screens/{sid}" or just "{sid}"
        extracted_pid = project_id  # Use the one we already have
        if "/" in str(screen_name):
            parts = screen_name.split("/")
            for i, p in enumerate(parts):
                if p == "projects" and i + 1 < len(parts):
                    extracted_pid = parts[i + 1]
                    break
        _patch_manifest_stitch_project_id(extracted_pid)
        logger.info(f"Stitch PUSH: extracted project_id={extracted_pid} from screen_name={screen_name}")

        # 3. Success
        status.update("success", f"L'écran '{screen_name}' a été généré dans Stitch.",
                      success=True, data={
                          "screen_name": screen_name,
                          "preview_url": preview_url,
                          "stitch_project_id": extracted_pid,
                          "stitch_url": f"https://stitch.google.com/p/{extracted_pid}/s/{screen_name.split('/')[-1] if '/' in str(screen_name) else screen_name}",
                          "prompt_length": len(prompt)
                      })
        logger.info(f"Stitch PUSH Success: {task_id} → {screen_name}")

    except Exception as e:
        logger.error(f"Stitch PUSH Task Failed: {e}")
        status.update("error", f"Erreur lors de la génération : {str(e)}", success=False, error=str(e))


@router.post("/push")
async def stitch_push(req: PushRequest, background_tasks: BackgroundTasks):
    """Lance une génération d'écran Stitch en arrière-plan depuis le genome du projet."""
    if not _get_stitch_key():
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


# --- M277: CREATE PROJECT + GENERATE FIRST SCREEN ---

@router.post("/create-project")
async def stitch_create_project(request: Request):
    """
    M277: Crée un projet Stitch pour le projet HomeOS actif + génère le 1er écran avec mega-prompt.
    Stocke stitch_project_id dans le manifest. Retourne l'URL du projet Stitch.
    """
    if not _get_stitch_key():
        raise HTTPException(status_code=501, detail="Stitch non configuré")

    try:
        from core.stitch_client import _mcp_call

        # Get active project
        active_file = ROOT_DIR / "active_project.json"
        active_id = None
        if active_file.exists():
            active_id = json.loads(active_file.read_text(encoding='utf-8')).get("active_id")

        if not active_id:
            raise HTTPException(status_code=400, detail="Aucun projet HomeOS actif")

        manifest_path = PROJECTS_DIR / active_id / "manifest.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        else:
            manifest = {}

        project_title = manifest.get("name", active_id)
        project_id = active_id  # Use as project ID for badge

        # 1. Create Stitch project
        proj_result = _mcp_call("create_project", {"title": project_title}, _get_stitch_key())
        stitch_name = proj_result.get("name", "")
        if not stitch_name:
            raise HTTPException(status_code=500, detail=f"Échec création projet Stitch: {proj_result}")

        stitch_project_id = stitch_name.replace("projects/", "")

        # 2. Generate first screen with mega-prompt including badge
        prompt = f"""Crée une landing page pour le projet étudiant "{project_title}".

DESIGN:
- Style clean, hard-edge, Tailwind CSS
- Palette: #8cc63f (vert primary), #f7f6f2 (background), #3d3d3c (texte)
- Tous les labels en lowercase
- Border-radius max 20px

IDENTIFICATION PROJET (OBLIGATOIRE):
Ajoute un badge visible dans le footer avec le texte exact: "project-id: {project_id}"
Ce badge est nécessaire pour le suivi pédagogique de la plateforme.

LAYOUT:
- Section hero avec titre et description
- Grille de features (3 colonnes)
- Footer avec le badge d'identification du projet"""

        screen_result = _mcp_call("generate_screen_from_text", {
            "projectId": stitch_project_id,
            "prompt": prompt
        }, _get_stitch_key())

        # 3. Store stitch_project_id in manifest
        manifest["stitch_project_id"] = stitch_name
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')

        logger.info(f"Stitch create-project: {project_title} → {stitch_name}")
        return {
            "success": True,
            "stitch_project_id": stitch_name,
            "url": f"https://stitch.withgoogle.com",
            "project_title": project_title
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stitch create-project failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- M230/M276: SYNC & OPEN ---

@router.post("/sync")
async def stitch_sync(request: Request):
    """M230/M276: Synchronise les écrans Stitch vers HoméOS (pull des nouveaux/modifiés)."""
    if not _get_stitch_key():
        raise HTTPException(status_code=501, detail="Stitch non configuré")

    try:
        from core.stitch_client import StitchClient, _mcp_call
        client = StitchClient(api_key=_get_stitch_key())

        # Read stitch_project_id from manifest
        active_file = ROOT_DIR / "active_project.json"
        active_id = None
        if active_file.exists():
            active_id = json.loads(active_file.read_text(encoding='utf-8')).get("active_id")

        manifest_path = PROJECTS_DIR / (active_id or "default") / "manifest.json"
        if not manifest_path.exists():
            raise HTTPException(status_code=404, detail="manifest.json introuvable")

        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        stitch_pid = manifest.get("stitch_project_id")
        if not stitch_pid:
            # Fallback: check if there's any stitch_project_id in imports
            raise HTTPException(status_code=400, detail="Aucun projet Stitch lié au manifest")

        # Extract numeric project ID
        proj_id = stitch_pid.replace("projects/", "") if "/" in stitch_pid else stitch_pid

        # List all screens from Stitch via MCP
        screens_data = _mcp_call("list_screens", {"projectId": proj_id}, _get_stitch_key())
        screens = screens_data.get("screens", [])

        if not screens:
            return {"synced": 0, "message": "Aucun écran dans le projet Stitch"}

        # Prepare imports directory
        from bkd_service import get_active_project_path
        imports_dir = get_active_project_path() / "imports"
        imports_dir.mkdir(parents=True, exist_ok=True)
        today_str = datetime.now().strftime("%Y-%m-%d")
        ts_str = datetime.now().strftime("%H%M%S")

        # Also prepare static/templates directory
        stenciler_templates = Path(__file__).parent.parent / "static" / "templates"
        stenciler_templates.mkdir(parents=True, exist_ok=True)

        # Read index.json
        index_path = imports_dir / "index.json"
        if index_path.exists():
            index_data = json.loads(index_path.read_text(encoding='utf-8'))
        else:
            index_data = {"imports": []}

        existing_ids = {imp.get("stitch_screen_id") for imp in index_data.get("imports", []) if imp.get("stitch_screen_id")}

        synced = []
        for screen in screens:
            # Screen name is like "projects/123/screens/abc123"
            full_name = screen.get("name", screen.get("id", ""))
            screen_id = full_name.split("/")[-1] if "/" in full_name else full_name
            title = screen.get("title", screen.get("displayName", screen_id))

            if screen_id in existing_ids:
                continue  # Already synced

            # Get screen HTML
            screen_details = _mcp_call("get_screen", {
                "projectId": proj_id,
                "screenId": screen_id,
                "name": full_name
            }, _get_stitch_key())

            # Try to get HTML from the response
            html_code = screen_details.get("htmlCode", {})
            download_url = html_code.get("downloadUrl")
            html = ""

            if download_url:
                try:
                    import urllib.request
                    req = urllib.request.Request(download_url)
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        html = resp.read().decode('utf-8')
                except Exception as e:
                    logger.warning(f"Stitch sync: failed to download HTML for {screen_id}: {e}")

            if not html:
                # Try inline content
                html = html_code.get("content", "")

            if not html:
                continue

            # Save to templates
            safe_name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in title).strip()[:60]
            template_name = f"stitch_{safe_name}_{screen_id}.html"
            tpl_path = stenciler_templates / template_name
            tpl_path.write_text(html, encoding='utf-8')

            # Add to index.json
            new_entry = {
                "id": f"stitch_{ts_str}_{safe_name}",
                "name": title,
                "timestamp": datetime.now().isoformat(),
                "file_path": f"{today_str}/{template_name}",
                "html_template": template_name,
                "type": "html",
                "archetype_id": "stitch_import",
                "archetype_label": "import stitch",
                "stitch_screen_id": screen_id,
                "stitch_project_id": stitch_pid,
                "elements_count": 0
            }
            index_data["imports"].insert(0, new_entry)
            synced.append(title)

        index_data["imports"] = index_data["imports"][:50]
        index_path.write_text(json.dumps(index_data, indent=2, ensure_ascii=False), encoding='utf-8')

        logger.info(f"Stitch sync: {len(synced)} new screens synced")
        return {"synced": len(synced), "screen_names": synced, "total_stitch": len(screens)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stitch sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/open/{screen_id}")
async def stitch_open_url(screen_id: str):
    """M230: Retourne l'URL Stitch pour ouvrir un écran dans l'éditeur Stitch."""
    active_file = ROOT_DIR / "active_project.json"
    active_id = None
    if active_file.exists():
        active_id = json.loads(active_file.read_text(encoding='utf-8')).get("active_id")

    manifest_path = PROJECTS_DIR / (active_id or "default") / "manifest.json"
    if not manifest_path.exists():
        raise HTTPException(status_code=404, detail="manifest.json introuvable")

    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    stitch_pid = manifest.get("stitch_project_id")
    if not stitch_pid:
        raise HTTPException(status_code=400, detail="Aucun projet Stitch lié")

    url = f"https://stitch.google.com/p/{stitch_pid}/s/{screen_id}"
    return {"url": url, "project_id": stitch_pid, "screen_id": screen_id}
