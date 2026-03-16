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
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from loguru import logger

from .svg_parser import parse_figma_svg
from .archetype_detector import ArchetypeDetector

router = APIRouter(prefix="/retro-genome", tags=["Retro Genome"])

# Singleton
detector = ArchetypeDetector()

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
    Sauvegarde le SVG brut dans exports/retro_genome/ pour inspection.
    """
    from datetime import datetime
    logger.info(f"[RetroGenome] SVG Upload received for: {data.name}")

    # Sauvegarde SVG brut pour inspection visuelle
    exports_dir = Path(__file__).parent.parent.parent.parent / "exports" / "retro_genome"
    exports_dir.mkdir(parents=True, exist_ok=True)
    safe_name = (data.name or "frame").replace(" ", "_").replace("/", "_")[:40]
    svg_path = exports_dir / f"SVG_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.svg"
    svg_path.write_text(data.svg, encoding="utf-8")
    logger.info(f"[RetroGenome] SVG saved to: {svg_path}")

    try:
        # 1. Parsing sémantique
        analysis = parse_figma_svg(data.svg)

        # 2. Détection d'archétype
        archetype = detector.detect(analysis)

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
async def retro_genome_upload(image: UploadFile = File(...)):
    """
    Upload a PNG mockup and run the full Retro Genome pipeline.

    Steps:
    1. Vision Analysis via GeminiClient.generate_with_image()
    2. Intent Mapping via GeminiClient.generate()
    3. Returns merged JSON

    No dependency on Antigravity, Claude Code or any IDE.
    Requires GOOGLE_API_KEY in AetherFlow .env (or GROQ_API_KEY as fallback).
    """
    logger.info(f"[RetroGenome] Upload received: {image.filename} ({image.content_type})")

    image_data = await image.read()
    b64_image, mime_type = _encode_image(image_data)

    client = _get_gemini_client()

    # --- Step 1: Vision Analysis ---
    logger.info("[RetroGenome] Step 1: Vision Analysis")
    try:
        vision_result = await client.generate_with_image(
            prompt=ANALYZER_PROMPT,
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

    return JSONResponse(content={
        "status": "ok",
        "analysis": analysis,
        "audit": audit,
        "archetype": archetype,
        "provider_used": getattr(vision_result, "provider", "gemini")
    })


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
