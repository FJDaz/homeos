"""
API REST pour Sullivan Stenciler - Phase 3

Expose les 5 piliers Backend via endpoints FastAPI :
1. État : GET /api/genome, GET /api/state, GET /api/schema
2. Modifications : POST /api/modifications, GET /api/modifications/history, POST /api/snapshot
3. Navigation : POST /api/drilldown/enter, POST /api/drilldown/exit, GET /api/breadcrumb
4. Composants : GET /api/components/contextual, GET /api/components/{id}, GET /api/components/elite
5. Outils : GET /api/tools, POST /api/tools/{tool_id}/apply

Conformité : CONSTITUTION_AETHERFLOW v1.0.0
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, status, Body
from pydantic import BaseModel, Field
from datetime import datetime
from pathlib import Path

from sullivan.stenciler.genome_state_manager import GenomeStateManager
from sullivan.stenciler.modification_log import ModificationLog
from sullivan.stenciler.drilldown_manager import DrillDownManager
from sullivan.stenciler.component_contextualizer import ComponentContextualizer
from sullivan.stenciler.semantic_property_system import SemanticPropertySystem


router = APIRouter(prefix="/api", tags=["stenciler"])

# Instances globales (à remplacer par injection de dépendances en prod)
# Utiliser chemin absolu pour compatibilité tests
_genome_path = Path(__file__).parent.parent / "genome_v2.json"
genome_manager = GenomeStateManager(genome_path=str(_genome_path))
modification_log = ModificationLog()
drilldown_manager = DrillDownManager(genome=genome_manager.get_modified_genome())
component_ctx = ComponentContextualizer()
semantic_system = SemanticPropertySystem()


# ============================================================================
# PILIER 1 : ÉTAT
# ============================================================================

class GenomeResponse(BaseModel):
    genome: Dict[str, Any]
    metadata: Dict[str, Any]


class StateResponse(BaseModel):
    current_state: Dict[str, Any]
    modification_count: int
    last_snapshot_id: str
    last_modified: str


@router.get("/genome", response_model=GenomeResponse)
async def get_genome():
    """Récupère le Genome complet"""
    try:
        genome = genome_manager.get_modified_genome()
        return GenomeResponse(
            genome=genome,
            metadata={
                "version": genome.get("version", "2.0.0"),
                "modification_count": len(modification_log.get_events_since(datetime.min)),
                "last_modified": datetime.now().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération Genome: {str(e)}"
        )


@router.get("/state", response_model=StateResponse)
async def get_state():
    """Récupère l'état actuel du Genome"""
    try:
        genome = genome_manager.get_modified_genome()
        return StateResponse(
            current_state=genome,
            modification_count=len(modification_log.get_events_since(datetime.min)),
            last_snapshot_id=None,
            last_modified=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération état: {str(e)}"
        )


@router.get("/schema")
async def get_schema():
    """Récupère le schéma JSON du Genome"""
    try:
        return {
            "levels": ["n0_phases", "n1_sections", "n2_features", "n3_atomsets"],
            "semantic_properties": semantic_system.get_all_properties(),
            "forbidden_properties": list(semantic_system.FORBIDDEN_PROPERTIES)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération schéma: {str(e)}"
        )


# ============================================================================
# PILIER 2 : MODIFICATIONS
# ============================================================================

class ModificationRequest(BaseModel):
    path: str = Field(..., description="Chemin vers l'élément (format n0[0].n1[2])")
    property: str = Field(..., description="Propriété sémantique à modifier")
    value: Any = Field(..., description="Nouvelle valeur")


class ModificationResponse(BaseModel):
    success: bool
    snapshot_id: Optional[str] = None
    error: Optional[str] = None
    validation_errors: Optional[List[str]] = None


@router.post("/modifications", response_model=ModificationResponse)
async def apply_modification(request: ModificationRequest):
    """Applique une modification au Genome"""
    try:
        result = genome_manager.apply_modification(
            path=request.path,
            property=request.property,
            value=request.value
        )

        return ModificationResponse(
            success=result.success,
            snapshot_id=result.snapshot_id,
            error=result.error,
            validation_errors=result.validation_errors
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur application modification: {str(e)}"
        )


@router.get("/modifications/history")
async def get_modification_history(since: Optional[str] = None, limit: int = 50):
    """Récupère l'historique des modifications"""
    try:
        events = modification_log.get_events_since(since) if since else modification_log.get_all_events()

        return {
            "events": [
                {
                    "id": e.id,
                    "timestamp": e.timestamp.isoformat(),
                    "path": e.path,
                    "property": e.property,
                    "old_value": e.old_value,
                    "new_value": e.new_value,
                    "semantic_attributes": e.semantic_attributes
                }
                for e in events[:limit]
            ],
            "total": len(events),
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération historique: {str(e)}"
        )


@router.post("/snapshot")
async def create_snapshot():
    """Crée un snapshot de l'état actuel"""
    try:
        snapshot_id = genome_manager.create_snapshot()
        return {"snapshot_id": snapshot_id, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur création snapshot: {str(e)}"
        )


# ============================================================================
# PILIER 3 : NAVIGATION
# ============================================================================

class DrillDownRequest(BaseModel):
    path: str = Field(..., description="Chemin vers l'élément à explorer")


@router.post("/drilldown/enter")
async def drilldown_enter(request: DrillDownRequest):
    """Descend d'un niveau dans la hiérarchie"""
    try:
        result = drilldown_manager.drill_down(request.path)
        return {
            "success": True,
            "current_level": result["level"],
            "children": result.get("children", []),
            "breadcrumb": drilldown_manager.get_breadcrumb()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur drilldown: {str(e)}"
        )


@router.post("/drilldown/exit")
async def drilldown_exit():
    """Remonte d'un niveau dans la hiérarchie"""
    try:
        result = drilldown_manager.drill_up()
        return {
            "success": True,
            "current_level": result["level"],
            "breadcrumb": drilldown_manager.get_breadcrumb()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur drill-up: {str(e)}"
        )


@router.get("/breadcrumb")
async def get_breadcrumb():
    """Récupère le fil d'Ariane de navigation"""
    try:
        return {
            "breadcrumb": drilldown_manager.get_breadcrumb(),
            "current_level": drilldown_manager.current_level
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération breadcrumb: {str(e)}"
        )


# ============================================================================
# PILIER 4 : COMPOSANTS
# ============================================================================

@router.get("/components/contextual")
async def get_contextual_components(level: str, context: Optional[Dict[str, Any]] = None):
    """Récupère les composants pertinents pour le contexte actuel"""
    try:
        components = component_ctx.get_contextual_components(level, context or {})
        return {
            "components": components,
            "level": level,
            "count": len(components)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération composants contextuels: {str(e)}"
        )


@router.get("/components/{component_id}")
async def get_component(component_id: str):
    """Récupère un composant par son ID"""
    try:
        component = component_ctx.get_component_by_id(component_id)
        if not component:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Composant {component_id} non trouvé"
            )
        return component
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération composant: {str(e)}"
        )


@router.get("/components/elite")
async def get_elite_library():
    """Récupère la bibliothèque Elite complète (65 composants)"""
    try:
        return {
            "components": component_ctx.elite_library,
            "total": len(component_ctx.elite_library),
            "by_level": component_ctx.get_components_by_level()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération Elite Library: {str(e)}"
        )


# ============================================================================
# PILIER 5 : OUTILS (SEMANTIC PROPERTIES)
# ============================================================================

@router.get("/tools")
async def get_tools():
    """Récupère la liste des outils (propriétés sémantiques)"""
    try:
        properties = semantic_system.get_all_properties()
        return {
            "tools": [
                {
                    "id": prop.name,
                    "name": prop.name,
                    "description": prop.description,
                    "category": prop.category,
                    "type": prop.type,
                    "constraints": prop.constraints
                }
                for prop in properties
            ],
            "total": len(properties)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération outils: {str(e)}"
        )


class ToolApplicationRequest(BaseModel):
    property: str = Field(..., description="Nom de la propriété sémantique")
    value: Any = Field(..., description="Valeur à valider/appliquer")
    context: Optional[Dict[str, Any]] = None


@router.post("/tools/{tool_id}/apply")
async def apply_tool(tool_id: str, request: ToolApplicationRequest):
    """Applique/valide une propriété sémantique"""
    try:
        # Validation
        validation = semantic_system.validate_property(request.property, request.value)

        if not validation["valid"]:
            return {
                "success": False,
                "validation_errors": validation["errors"],
                "property": request.property
            }

        return {
            "success": True,
            "property": request.property,
            "validated_value": request.value,
            "suggestions": semantic_system.get_property_suggestions(request.property, request.context or {})
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur application outil: {str(e)}"
        )
