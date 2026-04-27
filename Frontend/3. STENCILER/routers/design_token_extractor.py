"""
M356: Pipeline Incrémental HCI — Design Tokens → Seed Intent → Reconcile.
Traite les écrans un par un avec persistance immédiate pour une robustesse maximale.
"""
import os
import json
import base64
import asyncio
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from Backend.Prod.models.gemini_client import GeminiClient

logger = logging.getLogger("AetherFlowV3")

# --- PATHS ---
CWD = Path(__file__).parent.parent.resolve()
ROOT_DIR = CWD.parent.parent
PROJECTS_DIR = ROOT_DIR / "projects"

SUPPORTED = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp'}

def _load_manifest(path: Path) -> dict:
    if not path.exists(): return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except:
        return {}

def _save_manifest(path: Path, manifest: dict):
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')

async def extract_tokens_for_screen(image_path: Path) -> dict:
    """Envoie un écran à Gemini Vision, retourne les design tokens visuels bruts."""
    suffix = image_path.suffix.lower()
    mime = SUPPORTED.get(suffix, 'image/png')
    
    try:
        image_b64 = base64.b64encode(image_path.read_bytes()).decode()
        prompt = """Analyse cet écran de design étudiant et extrais les design tokens visuels.
Réponds UNIQUEMENT en JSON valide, sans balise markdown.
Format attendu :
{
  "colors": ["#hex1", "#hex2", ...],
  "typography": ["police ou style détecté", ...],
  "spacing": "serré | équilibré | aéré",
  "mood": ["mot1", "mot2", "mot3"],
  "layout": "colonne | grille | libre | asymétrique"
}"""

        client = GeminiClient(execution_mode="BUILD")
        try:
            result = await client.generate_with_image(
                prompt=prompt,
                image_base64=image_b64,
                mime_type=mime,
                temperature=0.2,
                max_tokens=400
            )
            if result.success:
                text = re.sub(r'^```ja?son\s*|\s*```$', '', result.code.strip(), flags=re.MULTILINE | re.IGNORECASE)
                return json.loads(text)
        finally:
            await client.close()
    except Exception as e:
        logger.error(f"[M356] Vision extraction failed for {image_path}: {e}")
    return {}

async def infer_seed_intent(tokens: dict) -> dict:
    """Transforme les premiers tokens en intention de base (seed)."""
    prompt = f"""Tu es un expert HCI. À partir de ces tokens design, infère l'intention de base du projet.
Tokens : {json.dumps(tokens)}

Réponds UNIQUEMENT en JSON :
{{
  "archetype": "portfolio | app-outil | site-vitrine | editorial | identite-visuelle",
  "description": "une phrase courte",
  "mood": ["mot1", "mot2", "mot3"],
  "suggested_sections": ["section1", "section2", "section3"]
}}"""
    client = GeminiClient(execution_mode="FAST")
    try:
        res = await client.generate(prompt=prompt, temperature=0.3, max_tokens=250)
        if res.success:
            text = re.sub(r'^```ja?son\s*|\s*```$', '', res.code.strip(), flags=re.MULTILINE | re.IGNORECASE)
            return json.loads(text)
        return {}
    except Exception as e:
        logger.error(f"[M356] Seed intent failed: {e}")
        return {}
    finally:
        await client.close()

async def extract_tokens_background(project_id: str):
    """Pipeline incrémental M356 : 1 écran à la fois, avec persistance immédiate."""
    imports_dir = PROJECTS_DIR / project_id / "imports"
    if not imports_dir.exists(): return

    # 1. Collecter les écrans (max 6, triés par date/dossier)
    screens = []
    for day_dir in sorted(imports_dir.iterdir()):
        if day_dir.is_dir():
            for f in sorted(day_dir.iterdir()):
                if f.is_file() and f.suffix.lower() in SUPPORTED:
                    screens.append(f)
    screens = screens[:6]
    if not screens: return

    # 2. Charger l'état
    manifest_path = PROJECTS_DIR / project_id / "manifest.json"
    manifest = _load_manifest(manifest_path)
    pipeline = manifest.setdefault("intent_pipeline", {
        "processed_screens": [],
        "seed_intent": None,
        "accumulated_intents": [],
        "reconciled": False
    })
    processed = set(pipeline["processed_screens"])
    global_tokens = manifest.get("design_tokens", {"colors": [], "typography": [], "mood": [], "spacing": "équilibré", "layout": "libre"})

    # 3. Boucle incrémentale
    for screen in screens:
        screen_rel_path = f"{screen.parent.name}/{screen.name}"
        if screen_rel_path in processed: continue

        logger.info(f"[M356] Processing screen: {screen_rel_path}")
        
        # 3a. Extraction Vision
        tokens = await extract_tokens_for_screen(screen)
        if not tokens: continue

        # 3b. Merge tokens visuels
        for k in ["colors", "typography", "mood"]:
            for item in tokens.get(k, []):
                if item not in global_tokens[k]: global_tokens[k].append(item)
        global_tokens["spacing"] = tokens.get("spacing", global_tokens["spacing"])
        global_tokens["layout"] = tokens.get("layout", global_tokens["layout"])

        # 3c. Seed Intent (si c'est le premier)
        if not pipeline["seed_intent"]:
            seed = await infer_seed_intent(tokens)
            if seed:
                pipeline["seed_intent"] = seed
                manifest["intent_inference"] = seed # Sync immédiat pour le drill UI

        # 3d. Update pipeline state
        pipeline["processed_screens"].append(screen_rel_path)
        pipeline["accumulated_intents"].append({"screen": screen_rel_path, "tokens": tokens})
        
        # 3e. Persistance immédiate (Safety first)
        manifest["design_tokens"] = global_tokens
        _save_manifest(manifest_path, manifest)
        _archive_design_md(project_id, global_tokens)
        
        logger.info(f"[M356] Progress saved for {screen_rel_path}")

    logger.info(f"[M356] Pipeline completed for project {project_id}")

def _archive_design_md(project_id: str, tokens: dict):
    """Archivage markdown des tokens (Mission 352 compliance)."""
    design_md = PROJECTS_DIR / project_id / "homeos_design.md"
    lines = [
        f"# design tokens — {project_id}",
        f"_mis à jour le {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n",
        "## couleurs", *[f"- `{c}`" for c in tokens.get("colors", [])],
        "\n## typographie", *[f"- {t}" for t in tokens.get("typography", [])],
        "\n## ambiance", *[f"- {m}" for m in tokens.get("mood", [])],
        f"\n## espacement : {tokens.get('spacing', 'non détecté')}",
        f"## layout : {tokens.get('layout', 'non détecté')}",
    ]
    design_md.write_text("\n".join(str(l) for l in lines), encoding="utf-8")
