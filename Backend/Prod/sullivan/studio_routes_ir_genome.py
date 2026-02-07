"""
Extension Studio Routes - IR + Genome View (Mission 2/6)
Layout 50/50 avec affichage IR Visuel et Genome Structure
"""

import re
import json
from pathlib import Path
from typing import Dict, Any, List
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import logging
logger = logging.getLogger(__name__)

# Router extension
router = APIRouter(prefix="/studio", tags=["studio-ir-genome"])

# Templates
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


def get_output_dir() -> Path:
    """Retourne le répertoire de sortie."""
    return Path("output")


def parse_ir_visuel() -> List[Dict[str, Any]]:
    """
    Parse le fichier ir_visuel_edite.md pour extraire les endpoints.
    Retourne une liste de dicts avec method, path, visual_hint, component_ref
    """
    ir_path = get_output_dir() / "studio" / "ir_visuel_edite.md"
    endpoints = []
    
    if not ir_path.exists():
        print("WARNING:")(f"IR Visuel non trouvé: {ir_path}")
        return []
    
    try:
        content = ir_path.read_text(encoding="utf-8")
        lines = content.split('\n')
        
        # Pattern pour matcher les lignes du tableau
        for line in lines:
            # Format: | 🟢 GET | `/path` | hint | 📄 visual | `component` |
            match = re.match(
                r'\|\s*[^|]+\s+(GET|POST|PUT|DELETE|PATCH)\s*\|\s*`([^`]+)`\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*`([^`]+)`',
                line
            )
            if match:
                method, path, ui_hint, visual, component = match.groups()
                
                # Extraire l'emoji du hint visuel (ex: 📄 list → 📄)
                visual_clean = visual.strip()
                visual_emoji = "🔹"
                if visual_clean and visual_clean[0].encode('utf-8')[:1] != visual_clean[0].encode('utf-8'):
                    # C'est probablement un emoji (multibyte)
                    parts = visual_clean.split(maxsplit=1)
                    if parts:
                        visual_emoji = parts[0]
                        visual_hint = parts[1] if len(parts) > 1 else visual_clean
                else:
                    visual_hint = visual_clean
                
                # Extraire wireframe si disponible dans la section détaillée
                wireframe = None
                # Chercher le détail de cet endpoint plus loin dans le fichier
                endpoint_detail_pattern = rf'\*\*{method}\*\*\s+`{re.escape(path)}`.*?\n\- \*\*Wireframe:\*\*\s*(.+?)(?:\n\n|\n\*\*|$)'
                detail_match = re.search(endpoint_detail_pattern, content, re.DOTALL)
                if detail_match:
                    wireframe = detail_match.group(1).strip()
                
                endpoints.append({
                    "method": method.strip(),
                    "path": path.strip(),
                    "ui_hint": ui_hint.strip(),
                    "visual_hint": visual_hint if 'visual_hint' in dir() else visual_clean,
                    "visual_emoji": visual_emoji,
                    "component_ref": component.strip(),
                    "wireframe": wireframe or f"{visual_hint} - Composant {component.strip()}"
                })
        
        print("INFO:")(f"IR Visuel parsé: {len(endpoints)} endpoints")
        
    except Exception as e:
        print("ERROR:")(f"Erreur parsing IR Visuel: {e}")
        return []
    
    return endpoints


def parse_genome_enrichi() -> List[Dict[str, Any]]:
    """
    Parse le fichier genome_enrichi.json pour extraire la structure Corps > Organes > Atomes
    """
    genome_path = get_output_dir() / "studio" / "genome_enrichi.json"
    
    if not genome_path.exists():
        print("WARNING:")(f"Genome enrichi non trouvé: {genome_path}")
        return []
    
    try:
        data = json.loads(genome_path.read_text(encoding="utf-8"))
        corps_list = []
        
        for corps in data.get("genome", {}).get("corps", []):
            organes_list = []
            
            for organe in corps.get("organes", []):
                atomes_list = []
                
                for atome in organe.get("atomes", []):
                    atomes_list.append({
                        "id": atome.get("id"),
                        "name": atome.get("name"),
                        "endpoint": atome.get("endpoint"),
                        "method": atome.get("method"),
                        "component_ref": atome.get("component_ref"),
                        "visual_hint": atome.get("visual_hint"),
                        "wireframe_sketch": atome.get("wireframe_sketch")
                    })
                
                organes_list.append({
                    "id": organe.get("id"),
                    "name": organe.get("name"),
                    "figma_type": organe.get("figma_type"),
                    "atomes": atomes_list
                })
            
            corps_list.append({
                "id": corps.get("id"),
                "name": corps.get("name"),
                "status": corps.get("status"),
                "figma_type": corps.get("figma_type"),
                "organes": organes_list
            })
        
        print("INFO:")(f"Genome parsé: {len(corps_list)} corps")
        return corps_list
        
    except Exception as e:
        print("ERROR:")(f"Erreur parsing Genome: {e}")
        return []


@router.get("/ir/visual", response_class=JSONResponse)
async def get_ir_visual():
    """
    Retourne l'IR Visuel au format JSON.
    """
    endpoints = parse_ir_visuel()
    return {
        "status": "success",
        "count": len(endpoints),
        "endpoints": endpoints
    }


@router.get("/genome/corps/{corps_id}", response_class=JSONResponse)
async def get_corps_detail(corps_id: str):
    """
    Retourne un Corps spécifique du Genome.
    """
    all_corps = parse_genome_enrichi()
    
    for corps in all_corps:
        if corps["id"] == corps_id:
            return {
                "status": "success",
                "corps": corps
            }
    
    return {
        "status": "error",
        "message": f"Corps {corps_id} non trouvé"
    }


@router.get("/step/4", response_class=HTMLResponse)
async def get_step_4_ir_genome_view(request: Request):
    """
    Affiche la vue IR + Genome (Step 4) avec layout 50/50.
    """
    # Parser les données
    ir_endpoints = parse_ir_visuel()
    genome_corps = parse_genome_enrichi()
    
    print("INFO:")(f"Step 4 - IR: {len(ir_endpoints)} endpoints, Genome: {len(genome_corps)} corps")
    
    return templates.TemplateResponse(
        "studio/ir_genome_view.html",
        {
            "request": request,
            "ir_endpoints": ir_endpoints,
            "ir_count": len(ir_endpoints),
            "genome_corps": genome_corps,
            "corps_count": len(genome_corps)
        }
    )


@router.get("/ir-genome-view", response_class=HTMLResponse)
async def get_ir_genome_view_direct(request: Request):
    """
    Route alternative pour accéder directement à la vue IR + Genome.
    """
    return await get_step_4_ir_genome_view(request)
