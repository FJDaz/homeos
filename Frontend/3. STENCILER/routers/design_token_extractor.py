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
from PIL import Image
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
Identifie aussi les régions illustratives (portraits, photos, illustrations, icônes, motifs).
Réponds UNIQUEMENT en JSON valide, sans balise markdown.
Format attendu :
{
  "colors": ["#hex1", "#hex2", ...],
  "typography": ["police ou style détecté", ...],
  "spacing": "serré | équilibré | aéré",
  "mood": ["mot1", "mot2", "mot3"],
  "layout": "colonne | grille | libre | asymétrique",
  "image_assets": [
    {
      "type": "portrait | illustration | photo | icone | motif | fond",
      "description": "description courte en français (ex: portrait de personnage cartoon)",
      "count": 1,
      "is_specimen": true,
      "bbox": [y_min, x_min, y_max, x_max]
    }
  ]
}
Note : bbox est en % de 0 à 1000 pour [y_min, x_min, y_max, x_max]. Un seul specimen bbox par TYPE."""

        client = GeminiClient(execution_mode="BUILD")
        try:
            logger.info(f"[M356] Vision: calling Gemini BUILD for {image_path.name}...")
            result = await asyncio.wait_for(client.generate_with_image(
                prompt=prompt,
                image_base64=image_b64,
                mime_type=mime,
                temperature=0.2,
                max_tokens=800
            ), timeout=30.0)
            if result.success:
                text = result.code.strip()
                text = re.sub(r'```[a-z]*', '', text).strip().strip('`')
                s, e = text.find('{'), text.rfind('}')
                if s >= 0 and e >= 0:
                    text = text[s:e+1]
                # Normalise typographic quotes before parsing
                text = text.replace('‘', "'").replace('’', "'")
                text = text.replace('“', '"').replace('”', '"')
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    clean = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
                    try:
                        return json.loads(clean)
                    except json.JSONDecodeError:
                        return {}
        finally:
            try:
                await asyncio.wait_for(client.close(), timeout=1.0)
            except Exception:
                pass
    except asyncio.TimeoutError:
        logger.error(f"[M356] Vision TIMEOUT (>30s) for {image_path.name} — skipping")
    except Exception as e:
        logger.error(f"[M356] Vision extraction failed for {image_path}: {e}")
    return {}

async def _process_specimens(project_id: str, screen_path: Path, assets: List[dict]) -> List[dict]:
    """Recadre et sauvegarde les spécimens d'images détectés via PIL."""
    if not assets: return []
    
    processed = []
    assets_dir = PROJECTS_DIR / project_id / "assets" / "img"
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    def process_sync():
        try:
            with Image.open(screen_path) as img:
                w, h = img.size
                for asset in assets:
                    bbox = asset.get('bbox')
                    if not bbox or len(bbox) != 4: continue
                    
                    # Convert % (0-1000) to pixels
                    y1, x1, y2, x2 = bbox
                    left = (x1 * w) / 1000
                    top = (y1 * h) / 1000
                    right = (x2 * w) / 1000
                    bottom = (y2 * h) / 1000
                    
                    # Crop & Resize
                    crop = img.crop((left, top, right, bottom))
                    crop.thumbnail((200, 200))
                    
                    t = asset['type'].replace(' ', '_')
                    screen_slug = screen_path.stem
                    filename = f"specimen_{t}_{screen_slug}.png"
                    save_path = assets_dir / filename
                    crop.save(save_path, "PNG")
                    
                    asset['specimen_url'] = f"/api/projects/assets/img/{filename}?project_id={project_id}"
                    processed.append(asset)
        except Exception as e:
            logger.error(f"[_process_specimens] PIL error: {e}")

    await asyncio.to_thread(process_sync)
    return processed

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
        logger.info("[M356] infer_seed_intent: calling Gemini FAST...")
        res = await asyncio.wait_for(client.generate(prompt=prompt, temperature=0.3, max_tokens=250), timeout=25.0)
        if res.success:
            text = re.sub(r'^```ja?son\s*|\s*```$', '', res.code.strip(), flags=re.MULTILINE | re.IGNORECASE)
            return json.loads(text)
        return {}
    except asyncio.TimeoutError:
        logger.error("[M356] Seed intent TIMEOUT (>25s) — skipping")
        return {}
    except Exception as e:
        logger.error(f"[M356] Seed intent failed: {e}")
        return {}
    finally:
        try:
            await asyncio.wait_for(client.close(), timeout=1.0)
        except Exception:
            pass

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
    global_tokens = manifest.get("design_tokens") or {"colors": [], "typography": [], "mood": [], "spacing": "équilibré", "layout": "libre"}

    # 3. Boucle incrémentale
    for screen in screens:
        screen_rel_path = f"{screen.parent.name}/{screen.name}"
        if screen_rel_path in processed: continue

        logger.info(f"[M356] Processing screen: {screen_rel_path}")
        
        # 3a. Extraction Vision
        tokens = await extract_tokens_for_screen(screen)
        logger.info(f"[M356] tokens keys: {list(tokens.keys())}, image_assets: {len(tokens.get('image_assets', []))}")
        if not tokens: continue

        # 3b. Merge tokens visuels
        for k in ["colors", "typography", "mood"]:
            for item in tokens.get(k, []):
                if item not in global_tokens[k]: global_tokens[k].append(item)
        global_tokens["spacing"] = tokens.get("spacing", global_tokens["spacing"])
        global_tokens["layout"] = tokens.get("layout", global_tokens["layout"])

        # 3c. Spécimens (M363)
        raw_assets = tokens.get("image_assets", [])
        if raw_assets:
            processed_assets = await _process_specimens(project_id, screen, raw_assets)
            if processed_assets:
                if "image_assets" not in global_tokens: global_tokens["image_assets"] = []
                # On ajoute les nouveaux spécimens détectés
                global_tokens["image_assets"].extend(processed_assets)

        # 3d. Update pipeline state + sauvegarde immédiate AVANT seed intent
        pipeline["processed_screens"].append(screen_rel_path)
        pipeline["accumulated_intents"].append({"screen": screen_rel_path, "tokens": tokens})
        manifest["design_tokens"] = global_tokens
        _save_manifest(manifest_path, manifest)
        logger.info(f"[M356] design_tokens sauvegardés pour {screen_rel_path}")

        # 3e. Seed Intent (si c'est le premier) — non-bloquant, best-effort
        if not pipeline["seed_intent"]:
            try:
                seed = await asyncio.wait_for(infer_seed_intent(tokens), timeout=20.0)
                if seed:
                    pipeline["seed_intent"] = seed
                    manifest["intent_inference"] = seed
            except Exception:
                logger.warning("[M356] Seed intent ignoré (timeout ou erreur)")
        
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
