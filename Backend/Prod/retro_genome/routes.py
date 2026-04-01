"""
Retro Genome — Routes FastAPI natives AetherFlow.

Ce module fournit les endpoints du pipeline Retro Genome directement
dans le stack AetherFlow, sans aucune dépendance à Antigravity,
Claude Code ou tout autre IDE externe.

Utilisateurs HomeOS : configurez votre GOOGLE_API_KEY dans le .env AetherFlow.
Fallback automatique : Gemini → Groq → (RunPod quand disponible).
"""
import base64
import json
import re
import io
import logging
import asyncio
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from loguru import logger

from .svg_parser import parse_figma_svg
from .archetype_detector import ArchetypeDetector
from .svg_to_tailwind import SvgToTailwindConverter

# Mission 111: Project Scoping
try:
    from bkd_service import get_active_project_path
except ImportError:
    # Fallback for standalone tests if needed
    def get_active_project_path(): return Path(__file__).parent.parent.parent.parent / "projects" / "homéos-default"

router = APIRouter(prefix="/retro-genome", tags=["Retro Genome"])

# Singleton
detector = ArchetypeDetector()

# Mission 101: Global tracker for new imports
_NEW_IMPORTS_COUNT = 0

# Mission 118: Generation job status tracker
_SVG_JOBS = {}
_SVG_CONVERTER = None  # Lazy init — instancié à la première requête

def get_svg_converter():
    """Retourne le convertisseur SVG, instancié au premier appel."""
    global _SVG_CONVERTER
    if _SVG_CONVERTER is None:
        _SVG_CONVERTER = SvgToTailwindConverter()
    return _SVG_CONVERTER

# ─── Prompts ─────────────────────────────────────────────────────────────────

ANALYZER_PROMPT = """You are an expert UI/UX Engineer and AetherFlow Architect.
Perform a REVERSE-GENOME analysis on this PNG mockup. Identify structural regions and components.

For EACH component provide:
- id: unique snake_case identifier
- name: descriptive label
- type: button | input | list | chart | nav | shell_element | form | modal
- location: header | sidebar_left | sidebar_right | main | footer
- visual_characteristics: object with colors, icon, text, approximate size
- inferred_intent: what this element does functionally

Output valid JSON only, no prose before or after.

JSON SCHEMA:
{
  "regions": [
    { "name": "string", "role": "string", "coordinates_hint": "string" }
  ],
  "components": [
    {
      "id": "unique_id",
      "name": "string",
      "type": "string",
      "location": "string",
      "visual_characteristics": {},
      "inferred_intent": "string"
    }
  ],
  "design_tokens": {
    "primary_color": "#hex",
    "accent_color": "#hex",
    "typography": "string"
  }
}"""

CANONICAL_INTENTS = {
    "phase_1_brs": ["MultiverseColumns", "SearchCenter", "ArbitrageDashboard", "TraceLogs"],
    "phase_2_bkd": ["FileExplorer", "CodeEditor", "RoadmapTrack", "ButlerChat", "TerminalOutput"],
    "phase_3_frd": ["GenomeExplorer", "IntentFeed", "PedagogyChat", "StyleChoice", "TooltipInfo"],
    "phase_4_dpl": ["SecretsManager", "SullivanOps", "ThirdPartyUI", "CaptureAction"]
}

MAPPING_PROMPT = """You are a Senior Product Manager and UX Auditor for AetherFlow.

Given the detected UI components below, you must:
1. Map each component to a canonical AetherFlow intent.
2. Perform an ergonomic audit (deadends, gaps, suggestions).
3. Propose a genome_structure skeleton.

CANONICAL INTENTS:
{canonical_reference}

DETECTED COMPONENTS:
{detected_components}

REGIONS:
{detected_regions}

Output valid JSON only.

JSON SCHEMA:
{{
  "mappings": [
    {{
      "component_id": "id",
      "canonical_intent": "intent_id",
      "confidence": 0.9,
      "reasoning": "string"
    }}
  ],
  "ergonomic_audit": {{
    "deadends": ["string"],
    "gaps": ["string"],
    "suggestions": ["string"]
  }},
  "genome_structure": {{
    "n0_phases": [
      {{
        "id": "phase_id",
        "organs": [
          {{ "id": "organ_id", "intent": "intent_id", "components": ["comp_id"] }}
        ]
      }}
    ]
  }}
}}"""

PRD_PROMPT = """You are a senior Product Manager. Generate a Product Requirements Document (PRD)
and an execution roadmap from this UI analysis.

ANALYSIS DATA:
{analysis_data}

PROJECT: {project_name}

Output a markdown PRD with:
1. Executive Summary
2. User Stories (one per organ/region detected)
3. Functional Requirements (one per component)
4. Ergonomic Risks (from audit)
5. Execution Roadmap (3 phases max, ordered by priority)
"""

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _normalize_for_detector(vision_analysis: Dict) -> Dict:
    """Adapte le schema Vision (components[]) au format attendu par ArchetypeDetector (elements[])."""
    elements = []
    for comp in vision_analysis.get("components", []):
        elements.append({
            "apparent_role": comp.get("type", ""),
            "description": comp.get("inferred_intent", ""),
            "text_content": comp.get("name", ""),
            "visual_hint": comp.get("type", ""),
        })
    regions = []
    for reg in vision_analysis.get("regions", []):
        regions.append({
            "name": reg.get("name", ""),
            "structural_role": reg.get("role", "content"),
        })
    return {"elements": elements, "regions": regions}


def _get_gemini_client():
    """Instancie le GeminiClient natif AetherFlow."""
    try:
        from ..models.gemini_client import GeminiClient
        return GeminiClient(execution_mode="FAST")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GeminiClient init failed: {e}")


def _parse_json_response(content: str) -> Dict[str, Any]:
    """Extrait et parse un JSON depuis une réponse texte."""
    # Strip markdown code fences if present
    content = re.sub(r'^```json\s*', '', content.strip())
    content = re.sub(r'\s*```$', '', content.strip())
    json_match = re.search(r'(\{.*\})', content, re.DOTALL)
    if json_match:
        content = json_match.group(1)
    return json.loads(content)


def _encode_image(data: bytes, max_bytes: int = 500 * 1024) -> tuple[str, str]:
    """Redimensionne et encode une image en base64 pour l'API Gemini."""
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(data))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        w, h = img.size
        if max(w, h) > 1024:
            ratio = 1024 / max(w, h)
            img = img.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        quality = 75
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        while len(buf.getvalue()) > max_bytes and quality > 40:
            quality -= 10
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=quality, optimize=True)
        return base64.b64encode(buf.getvalue()).decode("utf-8"), "image/jpeg"
    except ImportError:
        # Pillow not available — encode as-is
        logger.warning("Pillow not available, encoding raw bytes")
        return base64.b64encode(data).decode("utf-8"), "image/png"


# ─── Routes ───────────────────────────────────────────────────────────────────

class SVGUpload(BaseModel):
    svg: str
    name: Optional[str] = "unnamed_frame"

@router.post("/upload-svg")
async def retro_genome_upload_svg(data: SVGUpload):
    """
    Ingress SVG (Mission 41).
    Parse le SVG Figma structuré et détecte l'archétype sans passer par la vision.
    Sauvegarde le SVG brut dans {project}/imports/ pour inspection.
    """
    # Sauvegarde SVG brut pour inspection visuelle dans un dossier daté
    p_path = get_active_project_path()
    base_imports_dir = p_path / "imports"
    today_str = datetime.now().strftime('%Y-%m-%d')
    imports_dir = base_imports_dir / today_str
    imports_dir.mkdir(parents=True, exist_ok=True)
    
    safe_name = (data.name or "frame").replace(" ", "_").replace("/", "_")[:40]
    timestamp_str = datetime.now().strftime('%H%M%S')
    filename = f"SVG_{safe_name}_{timestamp_str}.svg"
    svg_path = imports_dir / filename
    svg_path.write_text(data.svg, encoding="utf-8")
    
    # Update index.json (Scoped to Project)
    index_path = base_imports_dir / "index.json"
    try:
        if index_path.exists():
            index_data = json.loads(index_path.read_text(encoding="utf-8"))
        else:
            index_data = {"imports": []}
        
        new_entry = {
            "id": f"{today_str}_{timestamp_str}_{safe_name}",
            "name": data.name,
            "timestamp": datetime.now().isoformat(),
            "svg_path": f"{today_str}/{filename}",
            "date": today_str
        }
        # Keep only last 50 imports
        index_data["imports"].insert(0, new_entry)
        index_data["imports"] = index_data["imports"][:50]
        index_path.write_text(json.dumps(index_data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        logger.error(f"[RetroGenome] Failed to update index.json: {e}")

    logger.info(f"[RetroGenome] SVG saved to: {svg_path}")

    try:
        # 1. Parsing sémantique
        analysis = parse_figma_svg(data.svg)

        # 2. Détection d'archétype
        archetype = detector.detect(analysis)

        # Enrichir l'entrée index.json avec les résultats de l'analyse
        try:
            index_data2 = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else {"imports": []}
            if index_data2["imports"] and index_data2["imports"][0].get("svg_path") == f"{today_str}/{filename}":
                index_data2["imports"][0]["archetype_id"] = archetype.get("archetype_id", "unknown")
                index_data2["imports"][0]["archetype_label"] = archetype.get("label", "—")
                index_data2["imports"][0]["elements_count"] = len(analysis.get("elements", []))
                index_path.write_text(json.dumps(index_data2, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e2:
            logger.warning(f"[RetroGenome] Failed to enrich index entry: {e2}")

        # Mission 101: Increment notification counter
        global _NEW_IMPORTS_COUNT
        _NEW_IMPORTS_COUNT += 1

        return JSONResponse(content={
            "status": "ok",
            "visual_analysis": analysis,
            "archetype": archetype,
            "design_tokens": analysis.get("design_tokens", {}),
            "svg_saved": str(svg_path),
            "source": "figma_svg"
        })
    except Exception as e:
        logger.error(f"[RetroGenome] SVG Processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def retro_genome_upload(
    images: List[UploadFile] = File(...),
    manifesto: str = Form("")
):
    """
    Upload PNG mockups and run the full Retro Genome pipeline.
    Steps:
    1. Save primary image as upload_latest.png
    2. Vision Analysis via GeminiClient.generate_with_image()
    3. Intent Mapping via GeminiClient.generate()
    4. Returns merged JSON
    """
    if not images:
        raise HTTPException(status_code=400, detail="No images uploaded")
    
    primary_image = images[0]
    logger.info(f"[RetroGenome] Upload received: {len(images)} images. Primary: {primary_image.filename}")

    # Project directories
    p_path = get_active_project_path()
    imports_dir = p_path / "imports"
    exports_dir = p_path / "exports"
    imports_dir.mkdir(parents=True, exist_ok=True)
    exports_dir.mkdir(parents=True, exist_ok=True)
    
    # Save as upload_latest.png for reference
    image_data = await primary_image.read()
    (exports_dir / "upload_latest.png").write_bytes(image_data)
    
    # Also save with timestamp for history
    from datetime import datetime
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    (exports_dir / f"upload_{ts}.png").write_bytes(image_data)

    b64_image, mime_type = _encode_image(image_data)

    client = _get_gemini_client()

    # --- Step 1: Vision Analysis ---
    logger.info("[RetroGenome] Step 1: Vision Analysis")
    try:
        # If manifesto is provided, prepend it to the prompt
        prompt = ANALYZER_PROMPT
        if manifesto:
            prompt = f"USER MANIFESTO / CONTEXT:\n{manifesto}\n\n---\n\n{prompt}"

        vision_result = await client.generate_with_image(
            prompt=prompt,
            image_base64=b64_image,
            mime_type=mime_type,
            output_constraint="JSON only",
            max_tokens=2048
        )
        if not vision_result.success:
            raise ValueError(f"Vision failed: {vision_result.error}")
        analysis = _parse_json_response(vision_result.code)
    except Exception as e:
        logger.error(f"[RetroGenome] Vision Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Vision Analysis failed: {e}")

    # --- Step 2: Intent Mapping ---
    logger.info("[RetroGenome] Step 2: Intent Mapping")
    try:
        mapping_prompt = MAPPING_PROMPT.format(
            canonical_reference=json.dumps(CANONICAL_INTENTS, indent=2),
            detected_components=json.dumps(analysis.get("components", []), indent=2),
            detected_regions=json.dumps(analysis.get("regions", []), indent=2)
        )
        mapping_result = await client.generate(
            prompt=mapping_prompt,
            output_constraint="JSON only",
            max_tokens=4096
        )
        if not mapping_result.success:
            raise ValueError(f"Mapping failed: {mapping_result.error}")
        audit = _parse_json_response(mapping_result.code)
    except Exception as e:
        logger.error(f"[RetroGenome] Intent Mapping failed: {e}")
        # Non-blocking: return partial result
        audit = {
            "mappings": [],
            "ergonomic_audit": {"deadends": [], "gaps": [f"Mapping error: {e}"], "suggestions": []},
            "genome_structure": {}
        }

    # --- Step 3: Archetype Detection (Mission 40/41) ---
    logger.info("[RetroGenome] Step 3: Archetype Detection")
    archetype = detector.detect(_normalize_for_detector(analysis))

    await client.close()

    # Save analysis for status endpoint persistence (Mission 102 Backend)
    analysis_data = {
        "status": "ok",
        "analysis": analysis,
        "audit": audit,
        "archetype": archetype,
        "provider_used": getattr(vision_result, "provider", "gemini")
    }
    status_path = exports_dir / "last_analysis.json"
    status_path.write_text(json.dumps(analysis_data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    return JSONResponse(content=analysis_data)


class PRDRequest(BaseModel):
    data: Dict[str, Any]
    project_name: str = "Analyzed Mockup"


@router.post("/generate-prd")
async def retro_genome_prd(request: PRDRequest):
    """Generate a PRD and roadmap from Retro Genome analysis data."""
    logger.info(f"[RetroGenome] PRD Generation for: {request.project_name}")

    client = _get_gemini_client()
    try:
        prd_prompt = PRD_PROMPT.format(
            analysis_data=json.dumps(request.data, indent=2)[:8000],
            project_name=request.project_name
        )
        result = await client.generate(prompt=prd_prompt, max_tokens=4096)
        if not result.success:
            raise ValueError(result.error)

        # Save PRD to exports
        exports_dir = Path(__file__).parent.parent.parent.parent / "exports" / "retro_genome"
        exports_dir.mkdir(parents=True, exist_ok=True)
        from datetime import datetime
        prd_path = exports_dir / f"PRD_{request.project_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        prd_path.write_text(result.code, encoding="utf-8")

        return JSONResponse(content={
            "status": "ok",
            "prd_path": str(prd_path),
            "roadmap_path": result.get('roadmap_path'),
            "prd_content": result.get('prd_content'),
            "project_name": request.project_name
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PRD generation failed: {e}")
    finally:
        await client.close()


@router.get("/viewer", response_class=HTMLResponse)
async def retro_genome_viewer():
    """Serve the Retro Genome Intent Viewer."""
    template_path = Path(__file__).parent.parent / "templates" / "retro_genome.html"
    if template_path.exists():
        return HTMLResponse(content=template_path.read_text(encoding="utf-8"))
    raise HTTPException(status_code=404, detail="Viewer template not found")


@router.post("/validate")
async def retro_genome_validate(data: Dict[str, Any]):
    """Persiste l'analyse validée pour la génération HTML."""
    exports_dir = Path(__file__).parent.parent.parent.parent / "exports" / "retro_genome"
    exports_dir.mkdir(parents=True, exist_ok=True)
    val_path = exports_dir / "validated_analysis.json"
    val_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"[RetroGenome] Validated analysis saved → {val_path}")
    return {"status": "ok"}


@router.post("/generate-html")
async def retro_genome_generate_html():
    """Génère reality.html depuis l'analyse validée."""
    exports_dir = Path(__file__).parent.parent.parent.parent / "exports" / "retro_genome"
    pngs = sorted(exports_dir.glob("upload_*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not pngs:
        raise HTTPException(status_code=400, detail="No PNG found in exports")
    
    val_path = exports_dir / "validated_analysis.json"
    if not val_path.exists():
        raise HTTPException(status_code=400, detail="Run /validate first")
    
    validated = json.loads(val_path.read_text(encoding="utf-8"))
    
    from .html_generator import HtmlGenerator
    gen = HtmlGenerator()
    
    import asyncio
    # We use asyncio.to_thread if gen.generate is synchronous or needs a separate loop
    # or just await it if it's already async.
    # Base on server_v3.py implementation:
    html_content = await asyncio.to_thread(asyncio.run, gen.generate(
        png_path=pngs[0],
        matched_analysis=validated,
        status_callback=None
    ))
    
    return {"status": "ok", "html_path": str(exports_dir / "reality.html")}

@router.get("/notifications")
async def get_notifications():
    """Mission 101: Retourne le nombre d'imports non lus par le viewer."""
    global _NEW_IMPORTS_COUNT
    return {"new_count": _NEW_IMPORTS_COUNT}

@router.get("/imports")
async def get_imports():
    """Mission 101 bis: Retourne la liste des imports depuis index.json du projet actif."""
    import shutil
    from pathlib import Path as _Path
    p_path = get_active_project_path()
    index_path = p_path / "imports" / "index.json"
    if not index_path.exists():
        return {"imports": []}

    data = json.loads(index_path.read_text(encoding="utf-8"))
    updated = False

    # Stenciler static/templates dir (pour servir via /api/frd/file)
    stenciler_root = _Path(__file__).parent.parent.parent.parent / "Frontend" / "3. STENCILER" / "static" / "templates"

    for entry in data.get("imports", []):
        if entry.get("type") == "html" and not entry.get("html_template"):
            file_path = entry.get("file_path") or entry.get("svg_path")
            if file_path:
                src = p_path / "imports" / file_path
                if src.exists():
                    tpl_name = f"import_backfill_{entry['id']}.html"
                    dst = stenciler_root / tpl_name
                    if not dst.exists():
                        shutil.copy2(str(src), str(dst))
                    entry["html_template"] = tpl_name
                    entry["elements_count"] = 0
                    updated = True

    if updated:
        index_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    return JSONResponse(content=data)

@router.get("/import-analysis-svg")
async def get_import_analysis_svg(id: str):
    """Alias rétrocompatibilité pour Mission 122."""
    return await get_import_analysis(id)

@router.get("/import-analysis")
async def get_import_analysis(id: str):
    """
    Route générique d'analyse d'import (Mission 122).
    Supporte SVG, HTML, PNG, ZIP.
    """
    p_path = get_active_project_path()
    imports_dir = p_path / "imports"
    index_path = imports_dir / "index.json"
    
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.json not found")
        
    index_data = json.loads(index_path.read_text(encoding="utf-8"))
    entry = next((i for i in index_data.get("imports", []) if i["id"] == id), None)
    
    if not entry:
        raise HTTPException(status_code=404, detail="Import not found")
    
    rel_path = entry.get("svg_path") or entry.get("file_path")
    if not rel_path:
        raise HTTPException(status_code=404, detail="Import path not found")
    
    import_path = imports_dir / rel_path
    if not import_path.exists():
        raise HTTPException(status_code=404, detail="Import file not found")

    # LOGIQUE D'ANALYSE POLYMORPHE
    components = []
    archetype_result = None
    
    # Cas 1 : SVG (Parsing Figma)
    if import_path.suffix.lower() == ".svg":
        analysis = parse_figma_svg(import_path.read_text(encoding="utf-8"))
        for i, el in enumerate(analysis.get("elements", [])):
            components.append({
                "id": el.get("id", f"elem_{i}"),
                "name": (el.get("text_content") or el.get("description") or f"élément {i}")[:40],
                "type": el.get("visual_hint", "unknown"),
                "inferred_intent": el.get("apparent_role", "à définir"),
            })
        archetype_result = detector.detect(analysis)
    # Cas 2 : Image ou HTML (Analyse brute simplifiée)
    else:
        components.append({
            "id": "root",
            "name": entry["name"],
            "type": "container",
            "inferred_intent": f"implémenter le template {entry.get('type', 'générique')}"
        })

    return {
        "analysis": {
            "components": components,
            "archetype": archetype_result,
            "import_name": entry["name"],
            "timestamp": entry["timestamp"],
            "type": entry.get("type", "unknown")
        }
    }

@router.get("/import-content")
async def get_import_content(path: str):
    """Lit le contenu d'un SVG importé via son path relatif."""
    p_path = get_active_project_path()
    imports_dir = p_path / "imports"
    target_path = imports_dir / path
    if target_path.exists() and target_path.suffix == ".svg":
        return {"svg": target_path.read_text(encoding="utf-8")}
    raise HTTPException(status_code=404, detail="SVG not found")

@router.post("/imports/clear")
async def clear_imports():
    """Vide la liste des imports (index.json → liste vide). Les SVG restent sur disque."""
    p_path = get_active_project_path()
    index_path = p_path / "imports" / "index.json"
    index_path.write_text(json.dumps({"imports": []}, ensure_ascii=False), encoding="utf-8")
    return {"status": "ok"}

@router.get("/notifications/clear")
async def clear_notifications():
    """Mission 101: Reset le compteur après lecture."""
    global _NEW_IMPORTS_COUNT
    _NEW_IMPORTS_COUNT = 0
    return {"status": "ok"}

# --- MISSION 118 / 120 : FORGE UNIVERSELLE ---

class ImportGenRequest(BaseModel):
    import_id: str

@router.post("/generate-from-svg")  # Alias compatibilité M118
@router.post("/generate-from-import")
async def generate_from_import(req: ImportGenRequest):
    """Déclenche la conversion asynchrone de l'import (SVG ou ZIP) en Tailwind."""
    job_id = f"job_{datetime.now().strftime('%H%M%S')}"
    _SVG_JOBS[job_id] = {"status": "running", "template_name": None, "error": None}
    
    # Task asynchrone pour ne pas bloquer l'HTTP
    async def run_conversion():
        try:
            p_path = get_active_project_path()
            imports_dir = p_path / "imports"
            index_path = imports_dir / "index.json"
            
            if not index_path.exists(): 
                raise Exception("index.json missing")
                
            index_data = json.loads(index_path.read_text(encoding="utf-8"))
            
            # Matching robuste : normalisation unicode pour gérer NFC/NFD (macOS)
            import unicodedata
            req_id_nfc = unicodedata.normalize('NFC', req.import_id)
            entry = next(
                (i for i in index_data.get("imports", []) 
                 if unicodedata.normalize('NFC', i["id"]) == req_id_nfc),
                None
            )
            
            if not entry: 
                raise Exception("Import not found")
            
            # Détection du format par extension
            # Support SVG or HTML/Generic file_path (Mission 121)
            rel_path = entry.get("svg_path") or entry.get("file_path")
            if not rel_path:
                raise Exception(f"Import entry {req.import_id} has no path field (svg_path or file_path)")
                
            import_path = imports_dir / rel_path
            logger.info(f"[Mission 122] Raw suffix: '{import_path.suffix}', Normalized: '{import_path.suffix.lower()}'")
            is_zip = import_path.suffix.lower() == ".zip"
            
            if is_zip:
                # ROUTER ZIP (Mission 118-B)
                logger.info(f"[Mission 118-B] Routing ZIP archive: {import_path.name}")
                with zipfile.ZipFile(import_path, 'r') as z:
                    file_list = z.namelist()
                    
                    # Détection React vs HTML simple
                    is_react = any(f.endswith(('.tsx', '.jsx')) for f in file_list)
                    if is_react:
                        raise Exception("Format React/.zip détecté. Nécessite la Mission 119 (react_to_tailwind).")
                    
                    # Recherche du HTML principal
                    html_files = [f for f in file_list if f.endswith(('.html', '.htm')) and not f.startswith('__MACOSX')]
                    if not html_files:
                        raise Exception("Aucun fichier HTML trouvé dans l'archive ZIP.")
                    
                    # On prend le plus probable (index.html ou le premier à la racine)
                    main_html = next((f for f in html_files if 'index.html' in f.lower()), html_files[0])
                    svg_content = z.read(main_html).decode('utf-8', errors='replace')
                    html_code = await get_svg_converter().convert(svg_content, entry["name"])
            else:
                # DETECTION IMAGE (Mission 122 — Vision)
                IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.webp'}
                if import_path.suffix.lower() in IMAGE_EXTS:
                    import base64
                    img_b64 = base64.b64encode(import_path.read_bytes()).decode()
                    mime = "image/png" if import_path.suffix.lower() == ".png" else "image/jpeg"
                    html_code = await get_svg_converter().convert_image(img_b64, mime, entry["name"])
                else:
                    # FORMAT SVG CLASSIQUE
                    svg_content = import_path.read_text(encoding="utf-8")
                    html_code = await get_svg_converter().convert(svg_content, entry["name"])
            
            # Sauvegarde dans static/templates du Stenciler
            stenciler_templates = Path("/Users/francois-jeandazin/AETHERFLOW/Frontend/3. STENCILER/static/templates")
            stenciler_templates.mkdir(parents=True, exist_ok=True)

            safe_name = entry["name"].lower().replace(" ", "_").split(".")[0]
            template_name = f"reality_{safe_name}.html"
            output_path = stenciler_templates / template_name
            
            output_path.write_text(html_code, encoding="utf-8")
            
            # Suivi des jobs de génération (M118 / M119 / M120)
            _SVG_JOBS[job_id] = {"status": "done", "template_name": template_name, "error": None}
            logger.info(f"[Mission 118] Generation complete: {template_name}")
            
        except Exception as e:
            logger.error(f"[Mission 118] Generation failed for {job_id}: {e}")
            _SVG_JOBS[job_id] = {"status": "failed", "error": str(e), "template_name": None}

    # Lancement du background task
    asyncio.create_task(run_conversion())
    
    return {"status": "started", "job_id": job_id}

@router.get("/svg-job/{job_id}")
async def get_svg_job(job_id: str):
    """Polling pour connaître l'état de la génération."""
    job = _SVG_JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job mapping not found")
    return job
