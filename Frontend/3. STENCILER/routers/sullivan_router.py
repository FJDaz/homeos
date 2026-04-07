"""
Sullivan Router - Extracted from server_v3.py
Handles all Sullivan-related routes: pulse, fonts, chat
"""

import os
import re
import json
import asyncio
import logging
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any

# Garantir que le répertoire parent (3. STENCILER) est dans sys.path
_ROOT = Path(__file__).parent.parent.resolve()
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.key_resolver import resolve_key
from core.canvas_library import CANVAS_LIBRARY
from core.canvas_applier import applier

from fastapi import APIRouter, HTTPException, Query, Body, Request, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

logger = logging.getLogger("AetherFlowV3.Sullivan")

router = APIRouter()

# --- PATHS ---
CWD = Path(__file__).parent.parent.resolve()
ROOT_DIR = CWD.parent.parent
BACKEND_PROD = ROOT_DIR / "Backend/Prod"
PROJECTS_DIR = ROOT_DIR / "projects"
STATIC_DIR_PATH = CWD / "static"

# --- SULLIVAN IMPORTS ---
import sys
for p in [str(ROOT_DIR), str(BACKEND_PROD), str(CWD)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from bkd_service import (
    SULLIVAN_BKD_SYSTEM, MANIFEST_FRD,
    route_request_bkd, resolve_bkd_project_root, bkd_safe_path, bkd_build_tree,
    exec_query_knowledge_base,
)

from sullivan_arbitrator import SullivanArbitrator, SullivanPulse

# --- GLOBAL STATE ---
_ARBITRATOR = SullivanArbitrator()
_PULSE = SullivanPulse()

# --- PYDANTIC MODELS ---
class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []
    project_id: Optional[str] = None

class ChatResponse(BaseModel):
    explanation: str
    html: Optional[str] = None
    model: str
    route: str
    provider: str

class SullivanChatRequest(BaseModel):
    message: str
    project_id: Optional[str] = "active"
    mode: str = "construct"
    screen_html: Optional[str] = None
    canvas_screens: Optional[list] = None  # [{ id, title, html }]
    selected_element: Optional[dict] = None  # { selector, tag, html } — M154
    wires: Optional[List[Dict]] = None  # [{ trigger, target, event }] — M161

class ToolCallRequest(BaseModel):
    tool: str
    params: Dict[str, Any]
    project_id: Optional[str] = "active"

class ToolCallResponse(BaseModel):
    status: str
    html: Optional[str] = None
    error: Optional[str] = None

# --- CACHE DES FONTES SYSTEME (Optimisation M148) ---
_FONT_PATH_CACHE = {}

def _warm_up_font_cache():
    """Scanne les dossiers systeme une seule fois au demarrage."""
    font_dirs = [Path("/System/Library/Fonts"), Path("/Library/Fonts"), Path.home() / "Library/Fonts"]
    ext = {'.ttf', '.otf', '.ttc'}
    for d in font_dirs:
        if not d.exists():
            continue
        for f in d.rglob('*'):
            if f.suffix.lower() in ext:
                _FONT_PATH_CACHE[f.stem.lower()] = f

_warm_up_font_cache()

# --- HELPER: get_active_project_path ---
def get_active_project_path():
    from bkd_service import get_active_project_path
    return get_active_project_path()

# --- HELPER: get_manifest_context ---
def get_manifest_context(project_id: str):
    """Mission 181: Protocole Sullivan : Manifeste-Driven Identity."""
    try:
        if project_id == "active":
            project_id = get_active_project_path().name
        manifest_path = PROJECTS_DIR / project_id / "manifest.json"
        if not manifest_path.exists():
            return "ALERTE : manifeste absent. anatomie non declaree. rejoignez le mode CADRAGE pour initialiser cet organe."

        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        return f"""
MANIFESTE DU PROJET (SOURCE DE VERITE) :
---
ARCHETYPE : {manifest.get('archetype', 'non defini')}
ANATOMIE : {', '.join(manifest.get('anatomy', []))}
DESIGN TOKENS : {json.dumps(manifest.get('design_tokens', {}))}
WIRES (CABLAGE) : {len(manifest.get('wires', []))} actifs
---
"""
    except Exception as e:
        logger.error(f"Failed to load manifest context: {e}")
        return "ALERTE : Echec du chargement du manifeste."


# =============================================================================
# SULLIVAN ROUTES
# =============================================================================

@router.get("/api/sullivan/pulse")
async def get_sullivan_pulse():
    return _PULSE.get_status()


@router.post("/api/sullivan/font-upload")
async def sullivan_font_upload(file: UploadFile = File(...)):
    """
    Mission 109 Phase B: Upload TTF/OTF/WOFF/WOFF2 -> classification + webfont + @font-face.
    Mission 207: Logging amélioré pour diagnostic.
    """
    from Backend.Prod.sullivan.font_classifier import FontClassifier
    from Backend.Prod.sullivan.font_webgen import FontWebGen

    if not file.filename:
        raise HTTPException(status_code=400, detail="Nom de fichier requis")

    # Sauvegarde temporaire
    exports_dir = ROOT_DIR / "exports" / "fonts"
    exports_dir.mkdir(parents=True, exist_ok=True)

    temp_path = exports_dir / f"temp_{file.filename}"
    content = await file.read()
    temp_path.write_bytes(content)

    logger.info(f"Font upload: {file.filename} ({len(content)} bytes) saved to {temp_path}")

    try:
        # 1. Classification
        logger.info(f"Font upload: classifying {file.filename}")
        classifier = FontClassifier()
        classification = classifier.classify(str(temp_path))
        logger.info(f"Font upload: classification = {classification.get('vox_atypi', '?')} / {classification.get('family_name', '?')}")

        # 2. Generation webfont
        logger.info(f"Font upload: generating webfont for {classification.get('family_name', '?')}")
        webgen = FontWebGen()
        webfont_result = webgen.generate(str(temp_path), classification)

        # 3. Nettoyage
        temp_path.unlink()

        logger.info(f"Font upload: success — {webfont_result.get('slug', '?')}")
        return {
            "status": "ok",
            "classification": classification,
            "webfont": webfont_result
        }
    except Exception as e:
        logger.error(f"Font upload failed for {file.filename}: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        if temp_path.exists():
            temp_path.unlink()
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")


@router.get("/api/sullivan/fonts")
async def sullivan_list_fonts():
    """Liste les fontes uploadées dans /static/fonts/."""
    from Backend.Prod.sullivan.font_webgen import FontWebGen
    webgen = FontWebGen()
    fonts = webgen.list_fonts()
    return {"fonts": fonts}


@router.get("/api/sullivan/system-fonts")
async def sullivan_system_fonts():
    """Liste les familles de fontes installees sur le poste via le cache."""
    return {"families": sorted(_FONT_PATH_CACHE.keys())}


@router.post("/api/sullivan/tool-call", response_model=ToolCallResponse)
async def sullivan_tool_call(req: ToolCallRequest):
    """
    Mission 204: Execute un tool-call (instrumentation de canevas ou patch).
    """
    try:
        if req.tool == "insert_canvas":
            canvas_name = req.params.get("canvas")
            props = req.params.get("props", {})
            
            if canvas_name not in CANVAS_LIBRARY:
                return {"status": "error", "error": f"Canevas '{canvas_name}' inconnu."}
            
            html = applier.instanciate(canvas_name, props, req.project_id)
            return {"status": "ok", "html": html}
            
        elif req.tool == "patch_element":
            # Mission 204 — patch_element complet via _apply_tailwind_diff
            target = req.params.get("target", "")
            add_classes = req.params.get("add", [])
            remove_classes = req.params.get("remove", [])
            source_html = req.params.get("html", "")

            if not source_html or not target:
                return {"status": "error", "error": "patch_element requires 'html' and 'target'"}

            # Construire le diff au format attendu par _apply_tailwind_diff
            diff = [{
                "id": target,
                "add": " ".join(add_classes) if isinstance(add_classes, list) else add_classes,
                "remove": " ".join(remove_classes) if isinstance(remove_classes, list) else remove_classes
            }]

            try:
                from routers.frd_router import _apply_tailwind_diff
                patched_html = _apply_tailwind_diff(source_html, diff)
                return {"status": "ok", "html": patched_html}
            except Exception as e:
                logger.warning(f"_apply_tailwind_diff failed: {e}, returning source")
                return {"status": "ok", "html": source_html}
            
        return {"status": "error", "error": f"Outil '{req.tool}' non supporte."}
    except Exception as e:
        logger.error(f"Tool call failed: {e}")
        return {"status": "error", "error": str(e)}


@router.post("/api/sullivan/generate-webfont")
async def sullivan_generate_webfont(body: Dict[str, Any]):
    """Genere une webfont depuis les fontes systeme Mac a la volee (Mission 148)."""
    font_name = body.get('font_name')
    if not font_name:
        raise HTTPException(status_code=400, detail="font_name is required")

    from Backend.Prod.sullivan.font_webgen import FontWebGen
    webgen = FontWebGen()

    # 1. Verifier si deja genere (base sur le slug)
    slug = re.sub(r'[^\w\s-]', '', font_name.lower())
    slug = re.sub(r'[\s_]+', '-', slug).strip('-')
    meta_path = Path(webgen.output_dir) / slug / "metadata.json"

    if meta_path.exists():
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass

    # 2. Chercher le fichier via le cache optimise
    found_path = _FONT_PATH_CACHE.get(font_name.lower())

    # Recherche partielle si exact echoue dans le cache
    if not found_path:
        for name, path in _FONT_PATH_CACHE.items():
            if font_name.lower() in name:
                found_path = path
                break

    if not found_path:
        return {"status": "not_found", "message": f"Source pour '{font_name}' introuvable."}

    # 3. Generer via FontWebGen, avec fallback conversion directe si subsetting echoue
    def _convert_font(path, name, out_dir):
        from fontTools.ttLib import TTFont as _TTFont
        _slug = re.sub(r'[^\w\s-]', '', name.lower())
        _slug = re.sub(r'[\s_]+', '-', _slug).strip('-')
        font_out = out_dir / _slug
        font_out.mkdir(parents=True, exist_ok=True)
        woff2_path = font_out / f"{_slug}.woff2"
        font = _TTFont(str(path))
        font.flavor = "woff2"
        font.save(str(woff2_path))
        css = f"@font-face {{ font-family: '{name}'; src: url('/static/fonts/{_slug}/{_slug}.woff2') format('woff2'); font-display: swap; }}"
        return {"status": "ok", "css": css, "slug": _slug}

    try:
        result = await asyncio.to_thread(webgen.generate, str(found_path), {"family_name": font_name})
        result["status"] = "ok"
        return result
    except Exception as e:
        logger.warning(f"FontWebGen failed ({e}), falling back to direct conversion")
        try:
            out_dir = Path(webgen.output_dir)
            result = await asyncio.to_thread(_convert_font, found_path, font_name, out_dir)
            return result
        except Exception as e2:
            logger.error(f"Direct font conversion failed: {e2}")
            return {"status": "error", "message": str(e2)}


@router.delete("/api/sullivan/fonts/{slug}")
async def sullivan_delete_font(slug: str):
    """Supprime une fonte et son repertoire."""
    from Backend.Prod.sullivan.font_webgen import FontWebGen
    webgen = FontWebGen()
    success = webgen.delete_font(slug)
    if success:
        return {"status": "ok", "deleted": slug}
    raise HTTPException(status_code=404, detail=f"Font '{slug}' not found")


@router.post("/api/sullivan/chat")
async def sullivan_chat(request: Request, req: SullivanChatRequest):
    """
    Chat Sullivan - repond a un message utilisateur selon le mode courant.
    Mission 142 + 152 : Support multi-screens et Design System (DESIGN.md).
    Mission 137 : BYOK — injection clé user au runtime.
    """
    from core.key_resolver import resolve_key
    user_id = getattr(request.state, 'user_id', None)

    # Mission 137: Injecter clé BYOK si disponible
    gemini_key = resolve_key("gemini", user_id)
    original_key = os.environ.get("GOOGLE_API_KEY")
    if gemini_key:
        os.environ["GOOGLE_API_KEY"] = gemini_key

    try:
        from Backend.Prod.retro_genome.routes import _get_gemini_client
        client = _get_gemini_client()
    except Exception as e:
        logger.error(f"GeminiClient init failed: {e}")
        raise HTTPException(status_code=500, detail="LLM unavailable")
    finally:
        # Restaurer clé originale
        if gemini_key:
            if original_key:
                os.environ["GOOGLE_API_KEY"] = original_key
            else:
                os.environ.pop("GOOGLE_API_KEY", None)

    mode_context = {
        "construct": "Tu es Sullivan, un assistant de design UI/UX et AetherFlow Architect. Aide l'utilisateur a concevoir et forger ses ecrans.",
        "inspect": "Tu es Sullivan, inspecteur UI/UX. Analyse le design courant pour identifier des problemes ergonomiques ou d'accessibilite.",
        "preview": "Tu es Sullivan, critique design. Commente le rendu final de l'interface.",
        "front-dev": "Tu es Sullivan, Front-End Engineer & Expert GSAP. Ton role est de transformer les intentions de design et les connexions (Wires) en animations fluides et professionnelles utilisant la bibliotheque GSAP.",
    }

    base_system = mode_context.get(req.mode, mode_context["construct"])

    # --- MISSION 181 : PROTOCOLE SULLIVAN (MANIFESTE) ---
    project_id = req.project_id or "active"
    manifest_context = get_manifest_context(project_id)

    base_system += f"\n\n{manifest_context}"

    # --- MISSION 189 : HOMEO_GENOME.md (Source de Vérité Unifiée) ---
    genome_block = ""
    try:
        genome_path = get_active_project_path() / "HOMEO_GENOME.md"
        if genome_path.exists():
            genome_content = genome_path.read_text(encoding='utf-8')
            # Tronquer à 8000 tokens max (~32000 chars)
            if len(genome_content) > 32000:
                genome_content = genome_content[:32000] + "\n\n> ... (tronqué)"
            genome_block = f"""
HOMEO_GENOME.md (SOURCE DE VÉRITÉ DU PROJET) :
---
{genome_content}
---
Ton fichier HOMEO_GENOME.md définit le projet. Ne génère rien qui contrevienne aux tokens §2 ou aux intentions §3/§6.
"""
    except Exception:
        pass

    if "CADRAGE" in manifest_context and not genome_block:
        # Fallback : Inviter au cadrage si manifest absent
        base_system += "\nTu ne peux pas effectuer de modifications majeures. Invite poliment l'utilisateur a initialiser son projet via le mode CADRAGE."

    # --- MISSION 152 : DESIGN SYSTEM (DESIGN.md) ---
    design_md_block = ""
    try:
        design_path = get_active_project_path() / "DESIGN.md"
        if not design_path.exists():
            design_path = STATIC_DIR_PATH / "templates" / "DESIGN.md"
        if design_path.exists():
            design_md_block = f"""
DESIGN SYSTEM DU PROJET (REFERENCE) :
---
{design_path.read_text(encoding='utf-8')[:4000]}
---
Utilise ces tokens et ces regles pour garantir la coherence visuelle si l'utilisateur demande une modification.
"""
    except Exception:
        pass

    # --- MISSION 181 : MANIFEST PROJET (IDENTITE & ORGANES) ---
    manifest_block = ""
    try:
        manifest_path = PROJECTS_DIR / project_id / "manifest.json"
        if manifest_path.exists():
            manifest_data = json.loads(manifest_path.read_text(encoding='utf-8'))
            manifest_block = f"""
MANIFEST DU PROJET (SOURCE DE VERITE) :
---
Nom : {manifest_data.get('name', '?')}
Description : {manifest_data.get('description', '?')}
Archetype : {manifest_data.get('archetype', '?')}
Regles design : {json.dumps(manifest_data.get('design_tokens', {}), ensure_ascii=False)}
Organes declares : {json.dumps([o for s in manifest_data.get('screens', []) for c in s.get('corps', []) for o in c.get('organes', [])], ensure_ascii=False)[:2000]}
---
Respecte strictement ces regles de design. Chaque organe declare doit avoir un equivalent dans le HTML.
"""
    except Exception:
        pass

    # --- MISSION 142 : ECRAN ACTIF (MODIFIABLE) ---
    context_html_block = ""
    if req.screen_html:
        context_html_block = f"""
CODE SOURCE HTML DE L'ECRAN ACTIF (MODIFIABLE) :
---
{req.screen_html}
---
Si l'utilisateur demande une modification visuelle, une correction ou un ajout :
1. Analyse son intention.
2. Modifie le code source HTML ci-dessus pour appliquer le changement.
3. Retourne TOUT le document HTML5 mis a jour dans le champ "---HTML---" de ta reponse.
4. Explique ce que tu as fait dans le bloc "---EXPLANATION---".
"""

    # --- MISSION 154 : ELEMENT SELECTIONNE (FOCUS) ---
    selected_block = ""
    if req.selected_element:
        sel = req.selected_element
        selected_block = f"""
ELEMENT ACTUELLEMENT SELECTIONNE PAR L'UTILISATEUR (selector: {sel.get('selector','?')}) :
---
{sel.get('html','')[:2000]}
---
L'utilisateur parle probablement de cet element specifiquement. Si tu modifies le screen, cible en priorite cet element et ses descendants directs.
"""

    # --- MISSION 142 : AUTRES ECRANS ---
    other_screens_block = ""
    if req.canvas_screens:
        parts = []
        for s in req.canvas_screens:
            parts.append(f"SCREEN [{s.get('id','?')}] TITLE: {s.get('title','Sans Titre')}\nHTML:\n{s.get('html','')[:1000]}")
        parts_joined = "\n\n---\n\n".join(parts)
        other_screens_block = f"""
AUTRES ECRANS PRESENTS SUR LE CANVAS (LECTURE SEULE - REFERENCE) :
---
{parts_joined}
---
Ces ecrans sont fournis pour comparaison et contexte. Tu ne peux pas les modifier directement, mais tu dois t'en inspirer pour la coherence.
"""

    # --- MISSION 161 : WIRES & GSAP ---
    wires_block = ""
    if req.wires:
        wires_json = json.dumps(req.wires, indent=2)
        wires_block = f"""
CONNEXIONS VISUELLES (WIRES) DETECTEES :
---
{wires_json}
---
Utilise ces paires Trigger/Target pour generer des animations GSAP intelligentes.
"""

    # --- MISSION 204 : CATALOGUE DE CANEVAS (TOOL-CALLING) ---
    catalogue_block = f"""
CATALOGUE DE CANEVAS AUTORISES (MISSION 204) :
---
{json.dumps(CANVAS_LIBRARY, indent=2, ensure_ascii=False)}
---
"""

    system_prompt = f"""
{base_system}

{manifest_block}

{design_md_block}

{catalogue_block}

{selected_block}

{context_html_block}

{other_screens_block}

{wires_block}

REGLES DE REPONSE :
Sullivan est un orchestrateur d'outils bornes. Tu as deux modes de reponse :

1. MODE TOOL-CALL (Privilegier pour ajouts/modifications ciblees) :
Reponds avec un JSON strict contenant l'outil et ses parametres.

CASUQUISTIQUE — quand utiliser quel outil :
- L'utilisateur demande d'AJOUTER un composant (bouton, card, hero, nav, formulaire, modal, badge, toast, tabs, table, avatar, timeline, pricing-card, drawer, stat-block) → "insert_canvas" avec le nom du canevas et ses props
- L'utilisateur demande une modification de SURFACE (couleur, taille, espacement, police) sur un element existant → "patch_element" avec target, add/remove classes
- L'utilisateur demande une restructuration MAJEURE, une generation ex-nihilo complete, ou un changement qui touche a la structure globale → reponds en HTML libre avec les delimiteurs ---EXPLANATION---, ---HTML---
- L'utilisateur demande une ANIMATION ou interaction GSAP → reponds avec ---LOGIC---

Outils autorises :
- "insert_canvas" : params: {{ "canvas": "nom", "props": {{...}}, "anchor": {{ "after": "selector" }} }}
- "patch_element" : params: {{ "target": "selector", "add": ["class"], "remove": ["class"], "html": "<html source>" }}

Exemple de reponse JSON insert_canvas :
{{
  "tool": "insert_canvas",
  "params": {{ "canvas": "card", "props": {{ "hasImage": true, "title": "Mon titre" }}, "anchor": {{ "after": "[data-af-id='hero']" }} }}
}}

Exemple de reponse JSON patch_element :
{{
  "tool": "patch_element",
  "params": {{ "target": "[data-af-id='btn-login']", "add": ["font-medium", "tracking-wide"], "remove": ["font-normal"], "html": "<html source>" }}
}}

2. MODE GENERATION LIBRE (Fallback pour restructuration majeure) :
Utilise les delimiteurs ---EXPLANATION---, ---HTML---, ---LOGIC---.

DETERMINISME : Ne genere JAMAIS de HTML libre si un canevas du catalogue peut faire le travail.
"""

    try:
        result = await client.generate(
            prompt=f"{system_prompt}\n\nMessage utilisateur : {req.message}",
            max_tokens=16384
        )

        if not result.success:
            return {"explanation": "Desole, je rencontre une difficulte technique.", "html": None}

        raw_text = result.code.strip()

        # Detection Tool-Call JSON (Mission 204)
        if raw_text.startswith("{") and "tool" in raw_text:
            try:
                tool_data = json.loads(raw_text)
                # On execute le tool call en interne pour retourner le HTML si besoin
                tool_res = await sullivan_tool_call(ToolCallRequest(
                    tool=tool_data["tool"],
                    params=tool_data["params"],
                    project_id=req.project_id
                ))
                if tool_res["status"] == "ok":
                    return {
                        "explanation": f"J'ai utilise l'outil {tool_data['tool']} pour repondre a votre demande.",
                        "html": tool_res["html"],
                        "tool_call": tool_data
                    }
            except Exception as e:
                logger.error(f"Failed to handle inline tool-call: {e}")

        # Parsing par delimiteurs (Mission 161: Support ---LOGIC---)
        explanation = None
        html = None
        logic_js = None

        def _strip_fences(s: str) -> str:
            """Retire les backticks markdown si Sullivan les ajoute autour du code."""
            s = s.strip()
            if s.startswith("```"):
                s = s.split("\n", 1)[-1] if "\n" in s else s[3:]
            if s.endswith("```"):
                s = s.rsplit("```", 1)[0]
            return s.strip()

        if "---EXPLANATION---" in raw_text:
            try:
                explanation = raw_text.split("---EXPLANATION---")[1].split("---")[0].strip()

                if "---HTML---" in raw_text:
                    html_part = _strip_fences(raw_text.split("---HTML---")[1].split("---")[0].strip())
                    html = None if html_part.upper() == "NULL" or not html_part.strip() else html_part

                if "---LOGIC---" in raw_text:
                    logic_part = raw_text.split("---LOGIC---")[1].split("---")[0].strip()
                    logic_js = None if logic_part.upper() == "NULL" else logic_part

            except Exception as e:
                logger.error(f"Sullivan parsing error: {e}")
                explanation = raw_text
        else:
            # Sullivan n'a pas utilisé les délimiteurs — extraire le HTML si présent
            # et ne pas polluer l'explanation avec du code
            if "<!DOCTYPE" in raw_text or "<html" in raw_text:
                try:
                    start = raw_text.find("<!DOCTYPE") if "<!DOCTYPE" in raw_text else raw_text.find("<html")
                    html = raw_text[start:].strip()
                    explanation = raw_text[:start].strip() or "Voici le rendu mis à jour."
                except Exception:
                    explanation = raw_text
            else:
                explanation = raw_text

        # Sauvegarde de la logique dans logic.js (Mission 161)
        if logic_js:
            try:
                p_path = get_active_project_path()
                if p_path:
                    (p_path / "logic.js").write_text(logic_js, encoding='utf-8')
                    logger.info(f"Sullivan: GSAP logic saved to {p_path}/logic.js")
            except Exception as e:
                logger.error(f"Failed to save logic.js: {e}")

        return {"explanation": explanation, "html": html, "logic_js": logic_js}

    except Exception as e:
        logger.error(f"Sullivan chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
