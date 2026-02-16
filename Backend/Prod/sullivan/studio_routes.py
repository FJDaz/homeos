"""
Studio Routes - Endpoints HTMX pour le Parcours UX Sullivan (9 étapes)

Ce module expose les routes nécessaires pour :
- Phase 1 : Péristaltisme API (IR → Arbitrage → Genome)
- Phase 3 : Machine à états (session + current_step)
- Phase 4-6 : Fragments par étape
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Request, Form, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from loguru import logger

from ..config.settings import settings
from ..core.distillation_to_genome import apply_distillation_to_genome
from .identity import (
    sullivan,
    navigator,
    auditor,
    distiller,
    layout_proposals,
    stenciler,  # Étape 4 : Stenciler (Composants Défaut)
    VisualIntentReport,
    VisualZone,
    SULLIVAN_DEFAULT_LIBRARY,
    SULLIVAN_HCI_STENCILS,
    generate_dialogue_proposals,
    design_structure_to_visual_intent_report,
)


# =============================================================================
# CHARGEMENT DU GENOME (pour Stenciler)
# =============================================================================

GENOME_PATH = Path(__file__).parent.parent.parent / "docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/genome_inferred_kimi_innocent.json"

try:
    with open(GENOME_PATH, encoding='utf-8') as f:
        GENOME_DATA = json.load(f)
    
    # Initialiser Stenciler avec le genome
    stenciler.genome = GENOME_DATA
    
    logger.info(f"✅ Genome chargé : {len(GENOME_DATA.get('n0_phases', []))} Corps détectés")
except FileNotFoundError:
    logger.warning("⚠️ Genome non trouvé, Stenciler vide")
    GENOME_DATA = {}


# =============================================================================
# ROUTER & TEMPLATES
# =============================================================================

router = APIRouter(prefix="/studio", tags=["studio"])

# Templates Jinja2
templates_dir = Path(__file__).parent.parent / "templates"
# Fallback to sullivan/templates if global templates not found
if not templates_dir.exists():
    templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


# =============================================================================
# STOCKAGE EN MÉMOIRE (pour la beta)
# TODO: Remplacer par Redis/DB en production
# =============================================================================

class StudioSession:
    """Session en mémoire pour stocker l'état du parcours UX."""
    
    def __init__(self):
        self.current_step: int = 1
        self.genome: Optional[Dict[str, Any]] = None
        self.distillation_entries: List[Dict[str, Any]] = []
        self.visual_intent_report: Optional[VisualIntentReport] = None
        self.validated_zones: List[str] = []
        self.selected_layout: Optional[str] = None
        self.journal: List[str] = []
        # Step 5 - Carrefour Créatif
        self.uploaded_design_path: Optional[Path] = None
        self.uploaded_design_url: Optional[str] = None
        self.uploaded_filename: Optional[str] = None
    
    def log(self, message: str):
        """Ajoute une entrée au journal."""
        timestamp = datetime.now().isoformat()
        self.journal.append(f"[{timestamp}] {message}")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_step": self.current_step,
            "genome": self.genome,
            "distillation_entries": self.distillation_entries,
            "visual_intent_report": self.visual_intent_report.to_dict() if self.visual_intent_report else None,
            "validated_zones": self.validated_zones,
            "selected_layout": self.selected_layout,
            "journal": self.journal
        }


# Session globale (une seule session pour la beta)
# En production, utiliser session_id depuis cookies
studio_session = StudioSession()


# =============================================================================
# UTILITAIRES
# =============================================================================

def get_output_dir() -> Path:
    """Retourne le répertoire de sortie."""
    return Path(settings.output_dir) if hasattr(settings, "output_dir") else Path("output")


def _save_distillation_entries(entries: List[Dict[str, Any]]) -> Path:
    """
    Sauvegarde les entrées de distillation dans output/studio/distillation_entries.json.
    
    Returns:
        Chemin du fichier écrit
    """
    studio_dir = get_output_dir() / "studio"
    studio_dir.mkdir(parents=True, exist_ok=True)
    entries_path = studio_dir / "distillation_entries.json"
    with open(entries_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
    return entries_path


def load_ir_inventaire() -> Optional[Dict[str, Any]]:
    """Charge le fichier ir_inventaire.json s'il existe."""
    ir_path = get_output_dir() / "studio" / "ir_inventaire.json"
    if ir_path.exists():
        try:
            return json.loads(ir_path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning(f"Failed to load ir_inventaire.json: {e}")
    return None


def load_genome() -> Optional[Dict[str, Any]]:
    """Charge le fichier homeos_genome.json s'il existe."""
    genome_path = get_output_dir() / "studio" / "homeos_genome.json"
    if genome_path.exists():
        try:
            return json.loads(genome_path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning(f"Failed to load homeos_genome.json: {e}")
    return None


def get_endpoints_from_genome(genome: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extrait les endpoints du genome."""
    endpoints = genome.get("endpoints", [])
    result = []
    for ep in endpoints:
        if isinstance(ep, dict):
            result.append(ep)
        else:
            result.append({"path": ep, "method": "GET", "summary": ep})
    return result


# =============================================================================
# ROUTES DE BASE (Phase 1 - Péristaltisme)
# =============================================================================

@router.get("/reports/ir", response_class=HTMLResponse)
async def get_ir_report(request: Request):
    """
    Étape 1 : Affiche le rapport IR (inventaire).
    """
    ir_data = load_ir_inventaire()
    
    if not ir_data:
        return HTMLResponse(
            content="""<div class="p-4 text-amber-600 bg-amber-50 rounded-lg">
                <p class="font-medium">⚠️ Inventaire non disponible</p>
                <p class="text-sm mt-1">Lancez d'abord l'analyse IR.</p>
            </div>"""
        )
    
    # Génère le HTML pour chaque organe
    organes = ir_data.get("organes", [])
    html_parts = ['<div class="space-y-4">']
    
    for organe in organes:
        organe_id = organe.get("id", "")
        title = organe.get("title", "")
        claims = organe.get("claims", [])
        verdict = organe.get("verdict", "Accept")
        
        verdict_color = {
            "Accept": "text-green-600 bg-green-50",
            "Revise": "text-amber-600 bg-amber-50",
            "Reject": "text-red-600 bg-red-50"
        }.get(verdict, "text-gray-600 bg-gray-50")
        
        html_parts.append(f"""
        <div class="border rounded-lg p-3 bg-white" data-section="{organe_id}">
            <div class="flex justify-between items-start mb-2">
                <h4 class="font-semibold text-sm text-slate-800">§{organe_id} {title}</h4>
                <span class="text-xs px-2 py-0.5 rounded {verdict_color}">{verdict}</span>
            </div>
            <div class="space-y-1">
        """)
        
        for claim in claims[:3]:  # Limite à 3 claims pour la lisibilité
            text = claim.get("text", "")
            checked = "✓" if claim.get("checked") else "○"
            html_parts.append(f'<p class="text-xs text-slate-600">{checked} {text}</p>')
        
        if len(claims) > 3:
            html_parts.append(f'<p class="text-xs text-slate-400">+ {len(claims) - 3} autres...</p>')
        
        html_parts.append("</div></div>")
    
    html_parts.append("</div>")
    return HTMLResponse(content="".join(html_parts))


@router.get("/reports/arbitrage", response_class=HTMLResponse)
async def get_arbitrage_report(request: Request):
    """
    Affiche le rapport d'arbitrage (résumé des validations distillation).
    """
    entries = studio_session.distillation_entries
    if not entries:
        return HTMLResponse(
            content="""<div class="p-3 text-slate-500 text-sm italic">
                Aucune validation d'arbitrage pour l'instant. Validez des éléments dans les formulaires ci-dessus.
            </div>"""
        )
    html_parts = ['<div class="space-y-2">']
    for entry in entries:
        verdict = entry.get("verdict", "")
        title = entry.get("section_title", "")
        verdict_class = {
            "Accept": "text-green-600 bg-green-50 border-green-200",
            "Revise": "text-amber-600 bg-amber-50 border-amber-200",
            "Reject": "text-red-600 bg-red-50 border-red-200",
        }.get(verdict, "text-gray-600 bg-gray-50")
        html_parts.append(
            f'<div class="p-2 rounded border-l-4 {verdict_class} text-xs">'
            f'<span class="font-medium">{title}</span> <span class="opacity-75">({verdict})</span>'
            f'</div>'
        )
    html_parts.append("</div>")
    return HTMLResponse(content="".join(html_parts))


@router.get("/arbitrage/forms", response_class=HTMLResponse)
async def get_arbitrage_forms(request: Request):
    """
    Étape 2 : Affiche les formulaires d'arbitrage avec stencils HCI.
    """
    ir_data = load_ir_inventaire()
    
    if not ir_data:
        return HTMLResponse(
            content="""<div class="p-4 text-amber-600 bg-amber-50 rounded-lg">
                <p class="font-medium">⚠️ Données IR manquantes</p>
                <p class="text-sm mt-1">Générez l'inventaire IR d'abord.</p>
            </div>"""
        )
    
    # Enrichit les organes avec les stencils HCI
    organes = ir_data.get("organes", [])
    enriched_organes = []
    
    for organe in organes:
        # Cherche un stencil correspondant
        stencil = None
        title_lower = organe.get("title", "").lower()
        
        for stencil_id, s in SULLIVAN_HCI_STENCILS.items():
            if stencil_id in title_lower or any(
                stencil_id in ep.lower() for ep in s.get("endpoints", [])
            ):
                stencil = s
                break
        
        enriched_organes.append({
            **organe,
            "stencil": stencil,
            "translation": sullivan.get_intent_translation(
                organe.get("claims", [{}])[0].get("text", "") if organe.get("claims") else ""
            )
        })
    
    return templates.TemplateResponse(
        "studio_arbitrage_forms.html",
        {"request": request, "organes": enriched_organes}
    )


@router.post("/validate")
async def post_studio_validate(
    section_id: str = Form(...),
    section_title: str = Form(...),
    items: List[str] = Form(default=[]),
    verdict: str = Form(...)
):
    """
    Valide un élément d'arbitrage et l'ajoute à la distillation.
    """
    entry = {
        "section_id": section_id,
        "section_title": section_title,
        "items": items,
        "verdict": verdict,
        "timestamp": datetime.now().isoformat()
    }
    
    studio_session.distillation_entries.append(entry)
    studio_session.log(f"Validation: {section_id} -> {verdict}")
    
    # Persistance et mise à jour du genome
    try:
        entries_path = _save_distillation_entries(studio_session.distillation_entries)
        genome_path = get_output_dir() / "studio" / "homeos_genome.json"
        if genome_path.exists():
            success = apply_distillation_to_genome(entries_path, genome_path)
            if success:
                logger.info("Genome mis à jour via apply_distillation_to_genome")
            else:
                logger.warning("apply_distillation_to_genome a échoué (réponse 200 inchangée)")
        else:
            logger.debug("Genome non trouvé, skip apply_distillation_to_genome")
    except Exception as e:
        logger.warning(f"Erreur péristaltisme (distillation/genome): {e} — réponse 200 inchangée")
    
    # Retourne le fragment HTML pour le OOB swap
    verdict_icon = {"Accept": "✓", "Revise": "↻", "Reject": "✗"}.get(verdict, "?")
    verdict_class = {
        "Accept": "text-green-600 bg-green-50 border-green-200",
        "Revise": "text-amber-600 bg-amber-50 border-amber-200",
        "Reject": "text-red-600 bg-red-50 border-red-200"
    }.get(verdict, "text-gray-600 bg-gray-50")
    
    html = f"""
    <div class="p-3 border rounded-lg {verdict_class} animate-fade-in">
        <div class="flex items-center gap-2">
            <span class="font-bold">{verdict_icon}</span>
            <div>
                <p class="font-medium text-sm">{section_title}</p>
                <p class="text-xs opacity-75">{len(items)} élément(s) validé(s)</p>
            </div>
        </div>
    </div>
    """
    
    return HTMLResponse(content=html)


@router.get("/distillation/entries", response_class=HTMLResponse)
async def get_distillation_entries(request: Request):
    """Affiche les entrées de distillation validées."""
    entries = studio_session.distillation_entries
    
    if not entries:
        return HTMLResponse(
            content='<p class="text-gray-400 text-sm italic">Aucune validation encore. Validez des éléments dans l\'arbitrage.</p>'
        )
    
    html_parts = ['<div class="space-y-2">']
    
    for entry in entries[-5:]:  # Derniers 5
        verdict = entry.get("verdict", "")
        title = entry.get("section_title", "")
        
        verdict_class = {
            "Accept": "text-green-600 bg-green-50",
            "Revise": "text-amber-600 bg-amber-50",
            "Reject": "text-red-600 bg-red-50"
        }.get(verdict, "text-gray-600")
        
        html_parts.append(f"""
        <div class="p-2 rounded border-l-4 {verdict_class} text-xs">
            <span class="font-medium">{title}</span>
            <span class="opacity-75">({verdict})</span>
        </div>
        """)
    
    html_parts.append("</div>")
    return HTMLResponse(content="".join(html_parts))


@router.get("/genome/summary", response_class=HTMLResponse)
async def get_genome_summary(request: Request):
    """Affiche un résumé du genome."""
    genome = load_genome()
    
    if not genome:
        return HTMLResponse(
            content='<p class="text-gray-400 text-sm">Génome non généré.</p>'
        )
    
    endpoints = genome.get("endpoints", [])
    topology = genome.get("topology", [])
    metadata = genome.get("metadata", {})
    
    html = f"""
    <div class="space-y-3">
        <div class="flex items-center gap-2 text-xs text-slate-500">
            <span class="px-2 py-0.5 bg-slate-100 rounded">v{metadata.get('version', '?')}</span>
            <span>{metadata.get('intent', 'unknown')}</span>
        </div>
        
        <div>
            <p class="text-xs font-medium text-slate-700 mb-1">Topologie ({len(topology)})</p>
            <div class="flex flex-wrap gap-1">
                {''.join(f'<span class="text-[10px] px-1.5 py-0.5 bg-indigo-50 text-indigo-600 rounded">{t}</span>' for t in topology)}
            </div>
        </div>
        
        <div>
            <p class="text-xs font-medium text-slate-700 mb-1">Endpoints ({len(endpoints)})</p>
            <div class="space-y-1 max-h-32 overflow-auto">
                {''.join(f'<p class="text-[10px] text-slate-500 font-mono">{ep.get("method", "GET")} {ep.get("path", ep)}</p>' for ep in endpoints[:5])}
                {f'<p class="text-[10px] text-slate-400">+ {len(endpoints) - 5} plus...</p>' if len(endpoints) > 5 else ''}
            </div>
        </div>
    </div>
    """
    
    return HTMLResponse(content=html)


# =============================================================================
# MACHINE À ÉTATS (Phase 3)
# =============================================================================

@router.post("/next/{current_step}", response_class=HTMLResponse)
async def navigate_next_step(request: Request, current_step: int):
    """
    Passe à l'étape suivante du parcours UX.
    
    Étapes:
    1. IR (Inventaire)
    2. Arbitrage
    3. Genome
    4. Composants Défaut
    5. Carrefour (choix PNG vs Layouts)
    6. Analyse PNG
    7. Dialogue
    8. Validation finale
    9. Adaptation Top-Bottom
    """
    next_step = current_step + 1
    studio_session.current_step = next_step
    
    # Log la transition
    sullivan.log_event(current_step, f"Transition vers étape {next_step}")
    
    # Redirige vers le fragment approprié
    return await get_step_fragment(request, next_step)


@router.get("/step/{step}", response_class=HTMLResponse)
async def get_step_fragment(request: Request, step: int):
    """
    Retourne le fragment HTML pour une étape donnée.
    """
    studio_session.current_step = step
    
    if step == 1:
        # Étape 1 : IR
        return await get_ir_report(request)
    
    elif step == 2:
        # Étape 2 : Arbitrage
        return await get_arbitrage_forms(request)
    
    elif step == 3:
        # Étape 3 : Genome summary
        return await get_step_3_genome(request)
    
    elif step == 4:
        # Étape 4 : Composants Défaut
        return await get_step_4_defaults(request)
    
    elif step == 5:
        # Étape 5 : Carrefour (choix)
        return await get_step_5_choice(request)
    
    elif step == 6:
        # Étape 6 : Analyse PNG
        return await get_step_6_analysis(request)
    
    elif step == 7:
        # Étape 7 : Dialogue
        return await get_step_7_dialogue(request)
    
    elif step == 8:
        # Étape 8 : Validation finale
        return await get_step_8_validation(request)
    
    elif step == 9:
        # Étape 9 : Adaptation Top-Bottom
        return await get_step_9_adaptation(request)
    
    else:
        return HTMLResponse(
            content=f"<div class='p-4 text-red-600'>Éape {step} inconnue</div>"
        )


# =============================================================================
# FRAGMENTS PAR ÉTAPE
# =============================================================================

async def get_step_3_genome(request: Request) -> HTMLResponse:
    """Étape 3 : Genome summary avec lien de validation."""
    genome = load_genome()
    
    if not genome:
        return HTMLResponse(
            content="""<div class="p-4 text-amber-600 bg-amber-50 rounded-lg">
                <p>⚠️ Génome non disponible</p>
            </div>"""
        )
    
    endpoints_count = len(genome.get("endpoints", []))
    topology = genome.get("topology", [])
    
    html = f"""
    <div class="p-6 max-w-2xl mx-auto">
        <div class="text-center mb-6">
            <h2 class="text-2xl font-bold text-slate-800">Génome validé</h2>
            <p class="text-slate-500">La topologie de votre application est fixée.</p>
        </div>
        
        <div class="bg-slate-50 rounded-xl p-6 mb-6">
            <div class="grid grid-cols-3 gap-4 text-center">
                <div>
                    <p class="text-3xl font-bold text-indigo-600">{endpoints_count}</p>
                    <p class="text-xs text-slate-500">Endpoints</p>
                </div>
                <div>
                    <p class="text-3xl font-bold text-indigo-600">{len(topology)}</p>
                    <p class="text-xs text-slate-500">Compartiments</p>
                </div>
                <div>
                    <p class="text-3xl font-bold text-indigo-600">✓</p>
                    <p class="text-xs text-slate-500">Validé</p>
                </div>
            </div>
        </div>
        
        <div class="text-center">
            <button hx-post="/studio/next/3" 
                    hx-target="#studio-main-zone"
                    class="bg-indigo-600 text-white px-8 py-3 rounded-xl font-bold hover:bg-indigo-700 transition-colors">
                Continuer vers les composants →
            </button>
        </div>
    </div>
    """
    
    return HTMLResponse(content=html)


async def get_step_4_defaults(request: Request) -> HTMLResponse:
    """Étape 4 : Galerie de Composants Défaut."""
    library_items = SULLIVAN_DEFAULT_LIBRARY
    
    items_html = ""
    for comp_id, comp_data in library_items.items():
        items_html += f"""
        <div class="group relative p-2 border border-slate-100 rounded-3xl hover:bg-indigo-50/30 transition-all">
            <span class="absolute -top-3 left-6 px-3 py-1 bg-white border text-[10px] font-bold text-indigo-600 rounded-full shadow-sm z-10">
                {comp_data.get('category', 'ORGANE').upper()}
            </span>
            <div class="p-4">
                {comp_data['html']}
            </div>
            <div class="p-4 flex justify-between items-center bg-white/50 rounded-b-2xl">
                <p class="text-xs text-slate-400">{comp_data['description']}</p>
                <span class="text-xs font-mono text-slate-300">{comp_id}</span>
            </div>
        </div>
        """
    
    html = f"""
    <div class="p-8 max-w-5xl mx-auto animate-fade-in">
        <header class="text-center mb-10">
            <h2 class="text-3xl font-black text-slate-900">Vos composants sont prêts.</h2>
            <p class="text-slate-500 mt-2 italic">"Puisque nous avons validé ces capacités, voici les composants standards."</p>
        </header>

        <div class="grid md:grid-cols-2 gap-6">
            {items_html}
        </div>

        <div class="mt-12 p-8 border-2 border-indigo-100 bg-indigo-50/50 rounded-3xl text-center">
            <p class="text-indigo-900 font-medium mb-4">"C'est un peu générique, non ? Vous pouvez importer votre layout ou choisir parmi des idées."</p>
            <div class="flex gap-4 justify-center">
                <button hx-post="/studio/next/4" 
                        hx-target="#studio-main-zone"
                        class="bg-indigo-600 text-white px-8 py-3 rounded-xl font-bold shadow-lg shadow-indigo-200 hover:bg-indigo-700 transition-all">
                    Personnaliser maintenant
                </button>
                <button hx-get="/studio/step/5/layouts" 
                        hx-target="#studio-main-zone"
                        class="bg-white border border-indigo-200 text-indigo-600 px-8 py-3 rounded-xl font-bold hover:bg-white/80">
                    Voir des idées de layouts
                </button>
            </div>
        </div>
    </div>
    """
    
    return HTMLResponse(content=html)


# =============================================================================
# STEP 5 - CARREFOUR CRÉATIF (Upload PNG ou 8 Propositions)
# =============================================================================

async def get_step_5_choice(request: Request) -> HTMLResponse:
    """Étape 5 : Carrefour créatif (choix PNG vs Layouts)."""
    return templates.TemplateResponse(
        "studio_step_5_choice.html",
        {"request": request}
    )


@router.post("/step/5/upload", response_class=HTMLResponse)
async def step_5_upload(
    request: Request,
    design_file: UploadFile = File(...),
):
    """
    Upload PNG depuis l'étape 5.
    Sauvegarde le fichier et retourne le fragment de confirmation.
    """
    import shutil
    
    allowed = {".png", ".jpg", ".jpeg"}
    suffix = Path(design_file.filename or "").suffix.lower()
    
    if suffix not in allowed:
        return HTMLResponse(
            content=f'''<div class="p-4 text-red-600 bg-red-50 rounded-lg">
                <p class="font-medium">❌ Type non supporté</p>
                <p class="text-sm mt-1">Formats acceptés: {", ".join(allowed)}</p>
            </div>''',
            status_code=400,
        )
    
    try:
        # Créer le répertoire de stockage
        uploads_dir = Path.home() / ".aetherflow" / "uploads" / "studio"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # Sauvegarder le fichier avec un nom unique
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{design_file.filename}"
        file_path = uploads_dir / safe_filename
        
        with open(file_path, "wb") as f:
            shutil.copyfileobj(design_file.file, f)
        
        # Mettre à jour la session
        studio_session.uploaded_design_path = file_path
        studio_session.uploaded_filename = design_file.filename
        studio_session.uploaded_design_url = f"/uploads/{safe_filename}"
        
        # Calculer la taille
        file_size_bytes = file_path.stat().st_size
        file_size_mb = round(file_size_bytes / (1024 * 1024), 2)
        
        logger.info(f"✅ Upload réussi: {safe_filename} ({file_size_mb} MB)")
        
        return templates.TemplateResponse(
            "studio_step_5_uploaded.html",
            {
                "request": request,
                "filename": design_file.filename,
                "file_size_mb": file_size_mb,
                "image_url": studio_session.uploaded_design_url,
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Erreur upload: {e}", exc_info=True)
        return HTMLResponse(
            content=f'''<div class="p-4 text-red-600 bg-red-50 rounded-lg">
                <p class="font-medium">❌ Erreur lors de l'upload</p>
                <p class="text-sm mt-1">{str(e)}</p>
            </div>''',
            status_code=500,
        )


@router.delete("/step/5/upload", response_class=HTMLResponse)
async def step_5_delete_upload(request: Request):
    """Supprime le fichier uploadé et retourne au choix."""
    if studio_session.uploaded_design_path and studio_session.uploaded_design_path.exists():
        studio_session.uploaded_design_path.unlink()
    
    studio_session.uploaded_design_path = None
    studio_session.uploaded_filename = None
    studio_session.uploaded_design_url = None
    
    return await get_step_5_choice(request)


@router.get("/step/5/layouts", response_class=HTMLResponse)
async def step_5_layouts(request: Request):
    """Affiche les 8 propositions de styles avec leurs aperçus visuels."""
    from .identity import SULLIVAN_LAYOUT_PROPOSALS
    
    # Enrichir les propositions avec les classes CSS pour les aperçus
    proposals_enriched = []
    preview_styles = {
        "minimalist": {
            "preview_bg": "bg-white",
            "preview_elements": "bg-slate-100",
            "preview_accent": "bg-slate-800",
            "preview_card": "bg-white border border-slate-200",
        },
        "brutalist": {
            "preview_bg": "bg-yellow-50",
            "preview_elements": "bg-black",
            "preview_accent": "bg-black",
            "preview_card": "bg-yellow-400 border-2 border-black",
        },
        "glassmorphism": {
            "preview_bg": "bg-gradient-to-br from-purple-400 to-pink-400",
            "preview_elements": "bg-white/20 backdrop-blur",
            "preview_accent": "bg-white/40",
            "preview_card": "bg-white/30 backdrop-blur border border-white/50",
        },
        "neumorphism": {
            "preview_bg": "bg-slate-200",
            "preview_elements": "bg-slate-200 shadow-[4px_4px_8px_#bebebe,-4px_-4px_8px_#ffffff]",
            "preview_accent": "bg-slate-300",
            "preview_card": "bg-slate-200 shadow-[inset_2px_2px_5px_#bebebe,inset_-2px_-2px_5px_#ffffff] rounded-xl",
        },
        "cyberpunk": {
            "preview_bg": "bg-black",
            "preview_elements": "bg-gradient-to-r from-cyan-500 to-purple-500",
            "preview_accent": "bg-cyan-400",
            "preview_card": "bg-black border border-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.5)]",
        },
        "organic": {
            "preview_bg": "bg-emerald-50",
            "preview_elements": "bg-emerald-200",
            "preview_accent": "bg-emerald-600",
            "preview_card": "bg-white rounded-2xl shadow-lg",
        },
        "aero": {
            "preview_bg": "bg-gradient-to-br from-sky-100 to-blue-200",
            "preview_elements": "bg-white/60 backdrop-blur",
            "preview_accent": "bg-sky-500",
            "preview_card": "bg-white/80 backdrop-blur-xl border border-white/60 shadow-xl rounded-2xl",
        },
        "retro": {
            "preview_bg": "bg-amber-100",
            "preview_elements": "bg-amber-800",
            "preview_accent": "bg-orange-600",
            "preview_card": "bg-amber-50 border-2 border-amber-800 shadow-[4px_4px_0_#92400e]",
        },
    }
    
    for prop in SULLIVAN_LAYOUT_PROPOSALS:
        style = preview_styles.get(prop["id"], preview_styles["minimalist"])
        proposals_enriched.append({**prop, **style})
    
    return templates.TemplateResponse(
        "studio_step_5_layouts.html",
        {
            "request": request,
            "proposals": proposals_enriched,
            "selected_style": studio_session.selected_layout,
        }
    )


@router.post("/step/5/layouts/select", response_class=HTMLResponse)
async def step_5_select_layout(request: Request):
    """Sélectionne un style depuis les propositions."""
    form = await request.form()
    style_id = form.get("style_id")
    
    if style_id:
        studio_session.selected_layout = style_id
        logger.info(f"🎨 Style sélectionné: {style_id}")
    
    # Recharge la page des layouts avec la sélection
    return await step_5_layouts(request)


@router.post("/step/5/validate", response_class=HTMLResponse)
async def step_5_validate_layout(request: Request):
    """Valide le style sélectionné et passe à l'étape 8 (validation finale)."""
    if studio_session.selected_layout:
        from .identity import SULLIVAN_LAYOUT_PROPOSALS
        proposal = next(
            (p for p in SULLIVAN_LAYOUT_PROPOSALS if p["id"] == studio_session.selected_layout),
            None
        )
        if proposal:
            sullivan.log_event(5, f"Layout validé: {proposal['name']}")
            studio_session.current_step = 8
            return await get_step_8_validation(request)
    
    # Si pas de sélection, retourne aux layouts
    return await step_5_layouts(request)


@router.get("/step/5/layouts", response_class=HTMLResponse)
async def get_step_5_layouts(request: Request):
    """Retourne les 8 propositions de styles."""
    proposals = layout_proposals.get_all()
    
    grid_html = ""
    for proposal in proposals:
        colors = proposal.get("colors", {})
        preview_class = proposal.get("preview_class", "")
        
        grid_html += f"""
        <div class="cursor-pointer group"
             hx-post="/studio/step/5/select-layout/{proposal['id']}"
             hx-target="#studio-main-zone">
            <div class="p-4 rounded-xl border-2 border-transparent hover:border-indigo-300 transition-all {preview_class}">
                <div class="h-24 rounded-lg mb-3 flex items-center justify-center"
                     style="background-color: {colors.get('bg', '#fff')}; color: {colors.get('primary', '#000')}">
                    <span class="text-2xl font-bold">Aa</span>
                </div>
                <h4 class="font-bold text-slate-800">{proposal['name']}</h4>
                <p class="text-xs text-slate-500 mt-1">{proposal['description']}</p>
            </div>
        </div>
        """
    
    html = f"""
    <div class="p-8 max-w-5xl mx-auto">
        <div class="text-center mb-8">
            <h2 class="text-2xl font-bold text-slate-800">Choisissez votre style</h2>
            <p class="text-slate-500">8 propositions basées sur les capacités de votre application</p>
        </div>
        
        <div class="grid md:grid-cols-4 gap-4">
            {grid_html}
        </div>
        
        <div class="mt-8 text-center">
            <button hx-post="/studio/next/4"
                    hx-target="#studio-main-zone"
                    class="text-slate-500 hover:text-slate-700 underline">
                ← Retour au carrefour
            </button>
        </div>
    </div>
    """
    
    return HTMLResponse(content=html)


@router.post("/step/5/select-layout/{layout_id}", response_class=HTMLResponse)
async def select_layout(request: Request, layout_id: str):
    """Sélectionne un layout et passe à l'étape 6."""
    studio_session.selected_layout = layout_id
    proposal = layout_proposals.get_by_id(layout_id)
    
    if proposal:
        sullivan.log_event(5, f"Layout sélectionné: {proposal['name']}")
    
    # Passe directement à l'étape 8 (validation) car pas d'analyse PNG
    studio_session.current_step = 8
    return await get_step_8_validation(request)


# =============================================================================
# STEP 6 - ANALYSE VISION (PNG Analysis avec Gemini Vision)
# =============================================================================

@router.post("/step/6/analyze", response_class=HTMLResponse)
async def step_6_analyze(
    request: Request,
    session_id: Optional[str] = None
):
    """
    Déclenche l'analyse Gemini Vision du PNG uploadé.
    Retourne le template HTML avec le rapport visuel.
    """
    from .vision_analyzer import analyze_design_png
    from pathlib import Path
    import time
    
    # Déterminer le chemin du PNG uploadé
    if studio_session.uploaded_design_path and studio_session.uploaded_design_path.exists():
        png_path = studio_session.uploaded_design_path
    else:
        # Fallback: chercher dans ~/.aetherflow/uploads/studio/
        uploads_dir = Path.home() / ".aetherflow" / "uploads" / "studio"
        png_files = list(uploads_dir.glob("*.png")) + list(uploads_dir.glob("*.jpg"))
        if not png_files:
            return HTMLResponse(
                content='''<div class="p-4 text-red-600 bg-red-50 rounded-lg">
                    <p class="font-medium">❌ Aucune image trouvée</p>
                    <p class="text-sm mt-1">Veuillez d\'abord uploader une image à l\'étape 5.</p>
                    <button hx-get="/studio/step/5" hx-target="#studio-main-zone" 
                            class="mt-3 text-indigo-600 hover:underline">← Retour à l\'étape 5</button>
                </div>''',
                status_code=400
            )
        png_path = png_files[0]  # Prend le plus récent
    
    # Générer un session_id si non fourni
    if not session_id:
        session_id = str(int(time.time()))
    
    try:
        # Analyser avec Gemini Vision
        logger.info(f"🔍 Analyse Vision: {png_path.name}")
        visual_report = await analyze_design_png(str(png_path), session_id)
        
        # Stocker le rapport dans la session
        studio_session.visual_intent_report = visual_report
        studio_session.current_step = 6
        
        logger.info(f"✅ Analyse terminée: {len(visual_report.get('layout', {}).get('zones', []))} zones détectées")
        
        # Retourner le template HTML
        return templates.TemplateResponse(
            "studio_step_6_analysis.html",
            {
                "request": request,
                "report": visual_report,
                "png_url": f"/uploads/{png_path.name}",
                "session_id": session_id
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Erreur analyse Vision: {e}", exc_info=True)
        return HTMLResponse(
            content=f'''<div class="p-4 text-red-600 bg-red-50 rounded-lg">
                <p class="font-medium">❌ Erreur lors de l\'analyse</p>
                <p class="text-sm mt-1">{str(e)}</p>
                <button hx-post="/studio/step/6/analyze" hx-target="#studio-main-zone"
                        class="mt-3 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700">
                    🔄 Réessayer
                </button>
            </div>''',
            status_code=500
        )


@router.post("/step/6/regenerate", response_class=HTMLResponse)
async def step_6_regenerate(request: Request):
    """Régénère l'analyse Vision (supprime le cache et relance)."""
    # Supprimer le rapport visuel de la session pour forcer une nouvelle analyse
    studio_session.visual_intent_report = None
    return await step_6_analyze(request)


@router.get("/step/6/analysis", response_class=HTMLResponse)
async def step_6_get_analysis(request: Request):
    """Affiche l'analyse existante (sans la régénérer)."""
    if not studio_session.visual_intent_report:
        # Pas d'analyse en cache, lancer une nouvelle
        return await step_6_analyze(request)
    
    # Utiliser l'analyse en cache
    png_name = studio_session.uploaded_filename or "design.png"
    uploads_dir = Path.home() / ".aetherflow" / "uploads" / "studio"
    png_path = uploads_dir / png_name
    
    return templates.TemplateResponse(
        "studio_step_6_analysis.html",
        {
            "request": request,
            "report": studio_session.visual_intent_report,
            "png_url": f"/uploads/{png_name}",
            "session_id": "cached"
        }
    )


@router.post("/designer/upload", response_class=HTMLResponse)
async def studio_designer_upload(
    request: Request,
    design_file: UploadFile = File(...),
):
    """
    Upload PNG depuis l'étape 5 → DesignerMode → VisualIntentReport → étape 6.
    Retourne le fragment HTML de l'étape 6 (calque d'analyse).
    """
    import tempfile
    from .modes.designer_mode import DesignerMode

    allowed = {".png", ".jpg", ".jpeg", ".svg"}
    suffix = Path(design_file.filename or "").suffix.lower()
    if suffix not in allowed:
        return HTMLResponse(
            content=f'<div class="p-4 text-red-600 bg-red-50 rounded-lg">Type non supporté. Utilisez: {", ".join(allowed)}</div>',
            status_code=400,
        )

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await design_file.read()
            tmp.write(content)
            tmp_path = Path(tmp.name)

        try:
            designer_mode = DesignerMode(
                design_path=tmp_path,
                output_path=None,
                non_interactive=True,
                extract_principles=True,
            )
            result = await designer_mode.run()

            if result.get("success") and result.get("design_structure"):
                report = design_structure_to_visual_intent_report(
                    result["design_structure"],
                    result.get("design_principles"),
                )
                studio_session.visual_intent_report = report
                studio_session.current_step = 6
                sullivan.log_event(5, "Upload PNG analysé, passage à l'étape 6")
                return await get_step_6_analysis(request)
            else:
                return HTMLResponse(
                    content='<div class="p-4 text-amber-600 bg-amber-50 rounded-lg">'
                    f'Analyse échouée: {result.get("message", "Erreur inconnue")}</div>',
                )
        finally:
            tmp_path.unlink(missing_ok=True)
    except Exception as e:
        logger.error(f"Studio designer upload error: {e}", exc_info=True)
        return HTMLResponse(
            content=f'<div class="p-4 text-red-600 bg-red-50 rounded-lg">Erreur: {str(e)}</div>',
            status_code=500,
        )


async def get_step_6_analysis(request: Request) -> HTMLResponse:
    """Étape 6 : Calque d'analyse sur PNG (Rapport d'Intention Visuelle)."""
    # Vérifie si on a un rapport de vision_analyzer.py (format dict) 
    # ou un VisualIntentReport (format classe legacy)
    report_data = studio_session.visual_intent_report
    
    if not report_data:
        # Pas d'analyse disponible, rediriger vers l'analyse
        return await step_6_analyze(request)
    
    # Normaliser le rapport au format attendu par le template
    if isinstance(report_data, dict):
        # Format vision_analyzer.py
        report = report_data
    else:
        # Format VisualIntentReport legacy - convertir en dict
        report = {
            "metadata": {
                "analyzed_at": report_data.metadata.get("analyzed_at", "N/A"),
                "model": report_data.metadata.get("model", "unknown"),
                "source_png": report_data.metadata.get("source_png", "design.png")
            },
            "style": {
                "colors": report_data.metadata.get("style_global", {}),
                "typography": {"family": "sans-serif", "sizes": {}},
                "spacing": {"border_radius": "0px"}
            },
            "layout": {
                "type": "dashboard",
                "zones": [
                    {
                        "id": z.id,
                        "type": "zone",
                        "coordinates": z.coordinates,
                        "components": [],
                        "hypothesis": z.hypothesis
                    }
                    for z in report_data.zones
                ]
            }
        }
    
    # Déterminer l'URL de l'image
    png_url = "/uploads/design.png"
    if studio_session.uploaded_filename:
        png_url = f"/uploads/{studio_session.uploaded_filename}"
    elif studio_session.uploaded_design_url:
        png_url = studio_session.uploaded_design_url
    
    # Retourner le template Jinja2
    return templates.TemplateResponse(
        "studio_step_6_analysis.html",
        {
            "request": request,
            "report": report,
            "png_url": png_url,
            "session_id": "demo"
        }
    )


# =============================================================================
# STEP 7 - DIALOGUE (Chat Sullivan pour affiner l'analyse)
# =============================================================================

@router.get("/step/7/dialogue", response_class=HTMLResponse)
async def step_7_dialogue(request: Request):
    """Affiche l'interface de dialogue Sullivan (Step 7)."""
    # Initialiser l'état du dialogue si nécessaire
    if not hasattr(studio_session, 'dialogue_state'):
        studio_session.dialogue_state = {
            'messages': [],
            'current_question': 0,
            'answers': {},
            'complete': False
        }
    
    # Générer les questions si pas encore fait
    if not studio_session.dialogue_state['messages']:
        await _generate_dialogue_questions()
    
    return await _render_dialogue_template(request)


@router.post("/step/7/answer", response_class=HTMLResponse)
async def step_7_answer(request: Request):
    """Traite une réponse à une question du dialogue."""
    form = await request.form()
    question_id = form.get('question_id')
    answer = form.get('answer')
    
    # Enregistrer la réponse
    if hasattr(studio_session, 'dialogue_state'):
        studio_session.dialogue_state['answers'][question_id] = answer
        
        # Ajouter le message utilisateur
        studio_session.dialogue_state['messages'].append({
            'sender': 'user',
            'text': answer,
            'timestamp': datetime.now().strftime('%H:%M')
        })
        
        # Passer à la question suivante
        studio_session.dialogue_state['current_question'] += 1
        
        # Vérifier si dialogue terminé
        total_questions = len([m for m in studio_session.dialogue_state['messages'] if m['sender'] == 'sullivan'])
        if studio_session.dialogue_state['current_question'] >= total_questions:
            studio_session.dialogue_state['complete'] = True
            sullivan.log_event(7, "Dialogue terminé")
        else:
            # Générer réponse/Question suivante de Sullivan
            await _generate_next_message()
    
    return await _render_dialogue_template(request)


@router.post("/step/7/message", response_class=HTMLResponse)
async def step_7_message(request: Request):
    """Traite un message libre de l'utilisateur."""
    form = await request.form()
    message = form.get('message', '').strip()
    
    if message and hasattr(studio_session, 'dialogue_state'):
        # Ajouter message utilisateur
        studio_session.dialogue_state['messages'].append({
            'sender': 'user',
            'text': message,
            'timestamp': datetime.now().strftime('%H:%M')
        })
        
        # Générer réponse de Sullivan
        await _generate_sullivan_response(message)
    
    return await _render_dialogue_template(request)


@router.post("/step/7/skip", response_class=HTMLResponse)
async def step_7_skip(request: Request):
    """Skip le dialogue et passe directement à la validation."""
    sullivan.log_event(7, "Dialogue skippé")
    studio_session.current_step = 8
    return await get_step_8_validation(request)


async def _generate_dialogue_questions():
    """Génère les questions initiales du dialogue basées sur le rapport visuel."""
    report = studio_session.visual_intent_report or {}
    zones = report.get('layout', {}).get('zones', []) if isinstance(report, dict) else []
    style = report.get('style', {}) if isinstance(report, dict) else {}
    
    messages = []
    
    # Message d'accueil
    messages.append({
        'sender': 'sullivan',
        'text': "J'ai analysé votre design et j'ai quelques questions pour m'assurer que j'ai tout bien compris. Prêt ?",
        'timestamp': datetime.now().strftime('%H:%M'),
        'question_id': 'welcome',
        'options': [
            {'label': 'Oui, commençons !', 'value': 'oui'},
            {'label': 'Passer les questions', 'value': 'skip'}
        ]
    })
    
    # Questions sur les zones
    for i, zone in enumerate(zones[:3]):  # Limite à 3 zones principales
        zone_label = zone.get('hypothesis', {}).get('label', f'Zone {i+1}')
        confidence = zone.get('hypothesis', {}).get('confidence', 0)
        
        if confidence < 0.9:  # Questionner les zones avec faible confiance
            messages.append({
                'sender': 'sullivan',
                'text': f"J'ai détecté une zone '{zone_label}' avec {int(confidence*100)}% de confiance. C'est correct ?",
                'timestamp': datetime.now().strftime('%H:%M'),
                'question_id': f'zone_{zone.get("id", i)}',
                'options': [
                    {'label': 'Oui, c\'est ça', 'value': 'oui'},
                    {'label': 'Non, corriger', 'value': 'non'},
                    {'label': 'Ignorer cette zone', 'value': 'ignore'}
                ]
            })
    
    # Question sur le style
    colors = style.get('colors', {}) if isinstance(style, dict) else {}
    primary_color = colors.get('primary', 'indigo')
    
    messages.append({
        'sender': 'sullivan',
        'text': f"J'ai identifié une couleur principale {primary_color}. Cette palette vous convient ?",
        'timestamp': datetime.now().strftime('%H:%M'),
        'question_id': 'style_color',
        'options': [
            {'label': 'Parfait !', 'value': 'oui'},
            {'label': 'À ajuster', 'value': 'ajuster'},
            {'label': 'Changer complètement', 'value': 'changer'}
        ]
    })
    
    # Question finale
    messages.append({
        'sender': 'sullivan',
        'text': "Merci pour ces précisions ! Je vais maintenant générer le design final basé sur vos réponses. Êtes-vous prêt à valider ?",
        'timestamp': datetime.now().strftime('%H:%M'),
        'question_id': 'final',
        'options': [
            {'label': 'Oui, générer le design', 'value': 'valider'},
            {'label': 'Revoir l\'analyse', 'value': 'revenir'}
        ]
    })
    
    studio_session.dialogue_state['messages'] = messages[:2]  # Commence avec accueil + 1ère question
    studio_session.dialogue_state['total_questions'] = len(messages) - 1


async def _generate_next_message():
    """Génère le prochain message/question de Sullivan."""
    if not hasattr(studio_session, 'dialogue_state'):
        return
    
    current_idx = studio_session.dialogue_state['current_question']
    all_messages = studio_session.dialogue_state.get('all_messages', [])
    
    # Récupérer la question suivante si disponible
    if current_idx < len(all_messages):
        next_msg = all_messages[current_idx]
        studio_session.dialogue_state['messages'].append(next_msg)


async def _generate_sullivan_response(user_message: str):
    """Génère une réponse contextuelle de Sullivan."""
    # Réponses simples basées sur mots-clés
    responses = {
        'couleur': "Je note pour les couleurs. Voulez-vous que je propose des alternatives ?",
        'zone': "Je peux ajuster la détection des zones. Quelle zone souhaitez-vous modifier ?",
        'typo': "La typographie est importante. Préférez-vous un style plus moderne ou classique ?",
        'espacement': "Je peux ajuster les espacements. Plus aéré ou plus compact ?",
    }
    
    response_text = "D'accord, je prends note. Autre chose ?"
    for keyword, resp in responses.items():
        if keyword in user_message.lower():
            response_text = resp
            break
    
    studio_session.dialogue_state['messages'].append({
        'sender': 'sullivan',
        'text': response_text,
        'timestamp': datetime.now().strftime('%H:%M'),
        'question_id': f'response_{len(studio_session.dialogue_state["messages"])}',
        'options': [
            {'label': 'C\'est tout', 'value': 'terminer'},
            {'label': 'Autre chose...', 'value': 'continuer'}
        ]
    })


async def _render_dialogue_template(request: Request) -> HTMLResponse:
    """Rend le template du dialogue avec l'état actuel."""
    state = getattr(studio_session, 'dialogue_state', {
        'messages': [],
        'current_question': 0,
        'answers': {},
        'complete': False
    })
    
    report = studio_session.visual_intent_report or {}
    if isinstance(report, dict):
        zones = report.get('layout', {}).get('zones', [])
        layout_type = report.get('layout', {}).get('type', 'unknown')
    else:
        zones = getattr(report, 'zones', [])
        layout_type = 'unknown'
    
    # Calculer stats
    zones_count = len(zones)
    avg_confidence = 0
    if zones:
        confidences = [z.get('hypothesis', {}).get('confidence', 0) for z in zones] if isinstance(zones[0], dict) else []
        avg_confidence = int(sum(confidences) / len(confidences) * 100) if confidences else 85
    
    total_questions = state.get('total_questions', 3)
    current_q = min(state['current_question'], total_questions)
    progress_percent = int((current_q / total_questions) * 100) if total_questions > 0 else 0
    
    png_url = "/uploads/design.png"
    if studio_session.uploaded_filename:
        png_url = f"/uploads/{studio_session.uploaded_filename}"
    
    return templates.TemplateResponse(
        "studio_step_7_dialogue.html",
        {
            "request": request,
            "messages": state['messages'],
            "zones_count": zones_count,
            "layout_type": layout_type,
            "avg_confidence": avg_confidence,
            "current_question": current_q,
            "total_questions": total_questions,
            "progress_percent": progress_percent,
            "dialogue_complete": state.get('complete', False),
            "allow_free_text": True,  # Permettre messages libres
            "png_url": png_url
        }
    )


async def get_step_8_validation(request: Request) -> HTMLResponse:
    """Étape 8 : Validation finale (accord utilisateur)."""
    # Check d'homéostasie — désactivé si parcours layout (pas d'arbitrage IR)
    genome = load_genome() or {}

    # Parcours layout (step 5 direct) : pas de distillation_entries → pas d'alertes
    # L'auditor vérifie la cohérence entre design actuel et genome, mais sans IR
    # on n'a pas de mapping section→endpoint, donc pas de vérification possible.
    is_layout_path = bool(studio_session.selected_layout) and not studio_session.distillation_entries

    if is_layout_path:
        alerts = []  # Pas d'alertes pour le parcours layout
    else:
        current_design = {
            "active_functions": [
                entry.get("section_id", "")
                for entry in studio_session.distillation_entries
                if entry.get("verdict") == "Accept"
            ]
        }
        alerts = auditor.check_homeostasis(current_design, genome)
    
    alerts_html = ""
    if alerts:
        alerts_html = '<div class="mb-6 space-y-2">'
        for alert in alerts:
            alerts_html += f"""
            <div class="p-3 bg-amber-50 border border-amber-200 rounded-lg">
                <p class="text-sm text-amber-800">⚠️ {alert['message']}</p>
            </div>
            """
        alerts_html += '</div>'
    
    # Résumé des choix
    layout_info = ""
    if studio_session.selected_layout:
        proposal = layout_proposals.get_by_id(studio_session.selected_layout)
        if proposal:
            layout_info = f"<p class='text-sm text-slate-600'>Style sélectionné: <strong>{proposal['name']}</strong></p>"
    
    validations_count = len([e for e in studio_session.distillation_entries if e.get("verdict") == "Accept"])
    
    html = f"""
    <div class="p-8 max-w-2xl mx-auto text-center">
        <h2 class="text-3xl font-black text-slate-800 mb-4">Validation finale</h2>
        <p class="text-slate-500 mb-8">Vérifiez que tout est correct avant la génération.</p>
        
        {alerts_html}
        
        <div class="bg-slate-50 rounded-xl p-6 mb-8 text-left">
            <h3 class="font-bold text-slate-800 mb-4">Résumé de votre configuration</h3>
            
            <div class="space-y-3">
                <div class="flex justify-between items-center py-2 border-b border-slate-200">
                    <span class="text-slate-600">Éléments validés</span>
                    <span class="font-bold text-indigo-600">{validations_count}</span>
                </div>
                <div class="flex justify-between items-center py-2 border-b border-slate-200">
                    <span class="text-slate-600">Endpoints actifs</span>
                    <span class="font-bold text-indigo-600">{len(genome.get('endpoints', []))}</span>
                </div>
                {layout_info}
            </div>
        </div>
        
        <div class="flex gap-4 justify-center">
            <button hx-post="/studio/next/8"
                    hx-target="#studio-main-zone"
                    class="bg-indigo-600 text-white px-8 py-3 rounded-xl font-bold hover:bg-indigo-700 shadow-lg shadow-indigo-200">
                ✓ Générer l'application
            </button>
            <button hx-get="/studio/step/2"
                    hx-target="#studio-main-zone"
                    class="border border-slate-300 text-slate-600 px-6 py-3 rounded-xl hover:bg-slate-50">
                Revenir à l'arbitrage
            </button>
        </div>
    </div>
    """
    
    return HTMLResponse(content=html)


async def get_step_9_adaptation(request: Request) -> HTMLResponse:
    """Étape 9 : Adaptation Top-Bottom (Corps > Organe > Atome)."""
    html = """
    <div class="p-6 max-w-5xl mx-auto">
        <div class="text-center mb-8">
            <h2 class="text-2xl font-bold text-slate-800">Adaptation Top-Bottom</h2>
            <p class="text-slate-500">Navigation granulaire : Corps → Organe → Atome</p>
        </div>

        <!-- Navigation des niveaux -->
        <div class="flex justify-center gap-2 mb-8">
            <button class="px-4 py-2 bg-indigo-600 text-white rounded-lg font-medium">Corps</button>
            <span class="text-slate-400 self-center">→</span>
            <button hx-get="/studio/zoom/organe/header"
                    hx-target="#zoom-view"
                    class="px-4 py-2 bg-slate-200 text-slate-700 rounded-lg hover:bg-slate-300">
                Organe
            </button>
            <span class="text-slate-400 self-center">→</span>
            <button hx-get="/studio/zoom/atome/status"
                    hx-target="#zoom-view"
                    class="px-4 py-2 bg-slate-200 text-slate-700 rounded-lg hover:bg-slate-300">
                Atome
            </button>
        </div>

        <!-- Vue zoomable -->
        <div id="zoom-view" class="border-2 border-slate-200 rounded-2xl p-8 bg-white min-h-96">
            <div class="text-center">
                <h3 class="text-xl font-bold text-slate-800 mb-4">Vue d'ensemble (Corps)</h3>

                <div class="grid md:grid-cols-3 gap-4">
                    <!-- Header -->
                    <div class="col-span-3 p-4 bg-indigo-50 rounded-lg border-2 border-indigo-200 hover:border-indigo-400 cursor-pointer transition-all"
                         hx-get="/studio/zoom/organe/header"
                         hx-target="#zoom-view">
                        <p class="font-medium text-indigo-800">Header</p>
                        <p class="text-xs text-indigo-600">Status orb, navigation</p>
                    </div>

                    <!-- Sidebar -->
                    <div class="p-4 bg-slate-50 rounded-lg border-2 border-slate-200 hover:border-indigo-400 cursor-pointer transition-all h-48"
                         hx-get="/studio/zoom/organe/sidebar"
                         hx-target="#zoom-view">
                        <p class="font-medium text-slate-700">Sidebar</p>
                        <p class="text-xs text-slate-500">Navigation, tools</p>
                    </div>

                    <!-- Main Content -->
                    <div class="col-span-2 p-4 bg-slate-50 rounded-lg border-2 border-slate-200 hover:border-indigo-400 cursor-pointer transition-all h-48"
                         hx-get="/studio/zoom/organe/main"
                         hx-target="#zoom-view">
                        <p class="font-medium text-slate-700">Zone principale</p>
                        <p class="text-xs text-slate-500">Contenu, stepper, output</p>
                    </div>

                    <!-- Footer -->
                    <div class="col-span-3 p-4 bg-slate-50 rounded-lg border-2 border-slate-200 hover:border-indigo-400 cursor-pointer transition-all"
                         hx-get="/studio/zoom/organe/footer"
                         hx-target="#zoom-view">
                        <p class="font-medium text-slate-700">Footer</p>
                        <p class="text-xs text-slate-500">Status, logs</p>
                    </div>
                </div>

                <p class="text-sm text-slate-400 mt-6">Cliquez sur une zone pour zoomer</p>
            </div>
        </div>

        <div class="mt-8 text-center">
            <button hx-post="/studio/finalize"
                    hx-target="#studio-main-zone"
                    class="bg-green-600 text-white px-8 py-3 rounded-xl font-bold hover:bg-green-700">
                ✓ Finaliser la génération
            </button>
        </div>
    </div>
    """

    return HTMLResponse(content=html)


# =============================================================================
# NAVIGATION ZOOM (Phase 6 - Top-Bottom)
# =============================================================================

@router.get("/zoom/{level}/{target_id}", response_class=HTMLResponse)
async def handle_zoom(request: Request, level: str, target_id: str):
    """
    Gère l'exploration granulaire (Corps > Organe > Atome).
    
    Args:
        level: Niveau de zoom (organe, atome)
        target_id: Identifiant de la cible
    """
    context = navigator.zoom_in(level, target_id)
    
    if level == "organe" and target_id == "header":
        html = """
        <div class="animate-fade-in">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-xl font-bold text-slate-800">Header (Organe)</h3>
                <button hx-get="/studio/zoom/out"
                        hx-target="#zoom-view"
                        class="text-sm text-slate-500 hover:text-slate-700">
                    ← Remonter
                </button>
            </div>
            
            <!-- Ghost mode : le reste en filigrane -->
            <div class="relative">
                <!-- Contexte fantôme -->
                <div class="absolute inset-0 opacity-20 pointer-events-none">
                    <div class="grid md:grid-cols-3 gap-4">
                        <div class="col-span-3 p-4 bg-indigo-50 rounded-lg h-20"></div>
                        <div class="p-4 bg-slate-50 rounded-lg h-48"></div>
                        <div class="col-span-2 p-4 bg-slate-50 rounded-lg h-48"></div>
                    </div>
                </div>
                
                <!-- Zone active -->
                <div class="relative z-10 p-6 bg-white rounded-xl border-2 border-indigo-500 shadow-lg">
                    <p class="font-medium text-indigo-800 mb-4">Contenu du Header</p>
                    
                    <div class="space-y-3">
                        <div class="p-3 bg-indigo-50 rounded border border-indigo-200 hover:border-indigo-400 cursor-pointer"
                             hx-get="/studio/zoom/atome/logo"
                             hx-target="#zoom-view">
                            <p class="text-sm font-medium">Logo / Marque</p>
                        </div>
                        <div class="p-3 bg-indigo-50 rounded border border-indigo-200 hover:border-indigo-400 cursor-pointer"
                             hx-get="/studio/zoom/atome/status"
                             hx-target="#zoom-view">
                            <p class="text-sm font-medium">Status Orb (Veille)</p>
                        </div>
                        <div class="p-3 bg-indigo-50 rounded border border-indigo-200 hover:border-indigo-400 cursor-pointer">
                            <p class="text-sm font-medium">Navigation</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        return HTMLResponse(content=html)
    
    elif level == "atome" and target_id == "status":
        html = """
        <div class="animate-fade-in">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-xl font-bold text-slate-800">Status Orb (Atome)</h3>
                <button hx-get="/studio/zoom/organe/header"
                        hx-target="#zoom-view"
                        class="text-sm text-slate-500 hover:text-slate-700">
                    ← Remonter
                </button>
            </div>
            
            <div class="p-6 bg-white rounded-xl border-2 border-indigo-500 shadow-lg">
                <div class="flex items-center gap-4 p-4 bg-slate-50 rounded-lg mb-4">
                    <div class="relative">
                        <div class="w-4 h-4 bg-green-500 rounded-full"></div>
                        <div class="absolute inset-0 w-4 h-4 bg-green-500 rounded-full animate-ping opacity-75"></div>
                    </div>
                    <span class="font-medium text-slate-700">Système Opérationnel</span>
                </div>
                
                <div class="space-y-4">
                    <div>
                        <label class="text-sm text-slate-600">Couleur active</label>
                        <div class="flex gap-2 mt-1">
                            <button class="w-8 h-8 rounded-full bg-green-500 ring-2 ring-offset-2 ring-green-500"></button>
                            <button class="w-8 h-8 rounded-full bg-blue-500"></button>
                            <button class="w-8 h-8 rounded-full bg-amber-500"></button>
                        </div>
                    </div>
                    
                    <div>
                        <label class="text-sm text-slate-600">Animation</label>
                        <select class="mt-1 block w-full rounded border-slate-300 text-sm">
                            <option>Pulse doux</option>
                            <option>Pulse rapide</option>
                            <option>Statique</option>
                        </select>
                    </div>
                </div>
            </div>
        </div>
        """
        return HTMLResponse(content=html)
    
    # Zones génériques (sidebar, main, footer)
    elif level == "organe" and target_id in ("sidebar", "main", "footer"):
        zone_labels = {
            "sidebar": ("Sidebar", "Navigation et outils"),
            "main": ("Zone Principale", "Contenu central, stepper, output"),
            "footer": ("Footer", "Status, logs, actions rapides"),
        }
        label, desc = zone_labels[target_id]
        html = f"""
        <div class="animate-fade-in">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-xl font-bold text-slate-800">{label} (Organe)</h3>
                <button hx-get="/studio/zoom/out"
                        hx-target="#zoom-view"
                        class="text-sm text-slate-500 hover:text-slate-700">
                    ← Remonter
                </button>
            </div>

            <div class="p-6 bg-white rounded-xl border-2 border-indigo-500 shadow-lg">
                <p class="text-slate-600 mb-4">{desc}</p>
                <p class="text-sm text-slate-400">Aucun atome configuré pour cette zone (prototype).</p>
            </div>
        </div>
        """
        return HTMLResponse(content=html)

    return HTMLResponse(content=f"<div class='p-4 text-amber-600 bg-amber-50 rounded-lg'>Niveau {level}/{target_id} non implémenté</div>")


@router.post("/finalize", response_class=HTMLResponse)
async def finalize_generation(request: Request):
    """Finalise la génération et affiche un récapitulatif."""
    studio_session.current_step = 10  # Fin
    sullivan.log_event(9, "Génération finalisée")

    html = """
    <div class="p-8 max-w-2xl mx-auto text-center">
        <div class="w-20 h-20 mx-auto mb-6 bg-green-100 rounded-full flex items-center justify-center">
            <span class="text-4xl">✓</span>
        </div>
        <h2 class="text-3xl font-black text-slate-800 mb-4">Génération terminée !</h2>
        <p class="text-slate-500 mb-8">Votre interface Sullivan est prête.</p>

        <div class="bg-slate-50 rounded-xl p-6 mb-8 text-left">
            <h3 class="font-bold text-slate-800 mb-4">Prochaines étapes</h3>
            <ul class="space-y-2 text-sm text-slate-600">
                <li>• Exporter vers votre projet</li>
                <li>• Intégrer avec votre backend</li>
                <li>• Tester en conditions réelles</li>
            </ul>
        </div>

        <div class="flex gap-4 justify-center">
            <a href="/studio" class="bg-indigo-600 text-white px-6 py-3 rounded-xl font-bold hover:bg-indigo-700">
                ↻ Nouvelle session
            </a>
            <button class="border border-slate-300 text-slate-600 px-6 py-3 rounded-xl hover:bg-slate-50">
                Exporter
            </button>
        </div>
    </div>
    """

    return HTMLResponse(content=html)


@router.get("/zoom/out", response_class=HTMLResponse)
async def handle_zoom_out(request: Request):
    """Remonte d'un niveau dans la navigation Top-Bottom."""
    previous = navigator.zoom_out()
    
    if previous:
        if previous["level"] == "corps":
            return await get_step_9_adaptation(request)
        else:
            return await handle_zoom(request, previous["level"], previous["id"] or "")
    
    return await get_step_9_adaptation(request)


# =============================================================================
# SESSION & DEBUG
# =============================================================================

@router.get("/session", response_class=JSONResponse)
async def get_session():
    """Retourne l'état actuel de la session (debug)."""
    return studio_session.to_dict()


@router.post("/session/reset")
async def reset_session():
    """Réinitialise la session."""
    global studio_session
    studio_session = StudioSession()
    sullivan.clear_journal()
    navigator.history = []
    return {"status": "reset"}


# =============================================================================
# ROUTES STENCILER (Étape 4 - Composants Défaut)
# =============================================================================

@router.get("/stencils", response_class=JSONResponse)
async def get_stencils():
    """
    Retourne la liste des 9 Corps avec leur SVG et les composants.
    
    Returns:
        JSON avec corps[], components et stats
    """
    try:
        corps_list = stenciler.get_corps()
        components_by_corps = {}
        
        for corps in corps_list:
            corps_id = corps["id"]
            # Générer le SVG
            svg = stenciler.generate_stencil_svg(corps_id, width=200, height=120)
            corps["svg"] = svg
            
            # Récupérer les composants avec leur statut
            components = stenciler.get_components_for_corps(corps_id)
            for comp in components:
                comp["status"] = stenciler.get_selection(comp["id"]) or "none"
            
            components_by_corps[corps_id] = components
        
        stats = stenciler.get_stats()
        
        return {
            "corps": corps_list,
            "components_by_corps": components_by_corps,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting stencils: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stencils/select", response_class=JSONResponse)
async def select_component(request: Request):
    """
    Marque un composant comme 'keep' ou 'reserve'.
    
    Request Body:
        {"component_id": "comp_1", "status": "keep"}
    
    Returns:
        {"success": true, "component_id": "...", "status": "..."}
    """
    try:
        data = await request.json()
        component_id = data.get("component_id")
        status = data.get("status")
        
        if not component_id:
            raise HTTPException(status_code=400, detail="component_id requis")
        
        if status not in ("keep", "reserve"):
            raise HTTPException(status_code=400, detail="status doit être 'keep' ou 'reserve'")
        
        stenciler.set_selection(component_id, status)
        
        logger.info(f"Component {component_id} marked as {status}")
        
        return {
            "success": True,
            "component_id": component_id,
            "status": status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error selecting component: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stencils/validated", response_class=JSONResponse)
async def get_validated_genome():
    """
    Retourne le genome filtré (seulement les composants 'keep').
    
    Returns:
        {"genome": {...}, "stats": {...}}
    """
    try:
        validated = stenciler.get_validated_genome()
        stats = stenciler.get_stats()
        
        # Compter les composants gardés
        total_kept = 0
        for phase in validated.get("n0_phases", []):
            for section in phase.get("n1_sections", []):
                for feature in section.get("n2_features", []):
                    total_kept += len(feature.get("n3_components", []))
        
        return {
            "genome": validated,
            "stats": {
                "total_kept": total_kept,
                "total_reserved": stats.get("reserve", 0),
                "total_selected": stats.get("total", 0)
            }
        }
    except Exception as e:
        logger.error(f"Error getting validated genome: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# ROUTES STEP 5 - CARREFOUR CRÉATIF
# =============================================================================

@router.get("/step/5", response_class=HTMLResponse)
async def get_step5_choice(request: Request):
    """
    Affiche le Carrefour Créatif (Step 5) : choix entre Upload PNG ou 8 propositions.
    
    Returns:
        HTML avec les deux options
    """
    return templates.TemplateResponse("studio_step_5_choice.html", {
        "request": request
    })


@router.post("/step/5/upload", response_class=HTMLResponse)
async def upload_design_file(
    request: Request,
    design_file: UploadFile = File(...)
):
    """
    Upload fichier PNG/JPG pour analyse visuelle (Step 6).
    
    Args:
        design_file: Fichier image (PNG, JPG, JPEG)
        
    Returns:
        HTML de confirmation avec preview + bouton "Lancer l'analyse"
    """
    try:
        # Vérifier le type de fichier
        allowed_types = ["image/png", "image/jpeg", "image/jpg"]
        if design_file.content_type not in allowed_types:
            return HTMLResponse(
                content=f"""
                <div class="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                    ❌ Type de fichier non supporté. Veuillez uploader un PNG ou JPG.
                </div>
                """,
                status_code=400
            )
        
        # Créer le répertoire d'upload
        upload_dir = Path.home() / ".aetherflow" / "uploads" / str(studio_session.current_step)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Sauvegarder le fichier
        file_path = upload_dir / design_file.filename
        content = await design_file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Stocker le chemin dans la session
        studio_session.selected_layout = str(file_path)
        studio_session.log(f"Fichier uploadé: {design_file.filename}")
        
        # Retourner HTML avec preview
        return HTMLResponse(content=f"""
        <div class="p-6 bg-white border border-indigo-200 rounded-2xl animate-fade-in">
            <div class="text-center mb-6">
                <div class="text-4xl mb-2">✅</div>
                <h3 class="text-xl font-bold text-slate-800">Fichier reçu !</h3>
                <p class="text-slate-600">{design_file.filename}</p>
            </div>
            
            <div class="mb-6 p-4 bg-slate-50 rounded-xl">
                <img src="/studio/uploads/{design_file.filename}" 
                     alt="Preview" 
                     class="max-h-48 mx-auto rounded-lg shadow-sm">
            </div>
            
            <div class="flex gap-4 justify-center">
                <button hx-post="/studio/step/6/analyze" 
                        hx-target="#studio-main-zone"
                        class="bg-indigo-600 text-white px-6 py-3 rounded-xl font-bold hover:bg-indigo-700 transition-colors">
                    🔍 Lancer l'analyse Gemini
                </button>
                <button hx-get="/studio/step/5" 
                        hx-target="#studio-main-zone"
                        class="bg-slate-200 text-slate-700 px-6 py-3 rounded-xl font-bold hover:bg-slate-300 transition-colors">
                    ↩️ Changer de fichier
                </button>
            </div>
        </div>
        """)
        
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return HTMLResponse(
            content=f"""
            <div class="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                ❌ Erreur lors de l'upload : {str(e)}
            </div>
            """,
            status_code=500
        )


@router.get("/step/5/layouts", response_class=HTMLResponse)
async def get_layout_proposals(request: Request):
    """
    Génère les 8 propositions de styles de layout.
    
    Returns:
        HTML avec grid 2×4 des 8 styles
    """
    try:
        # Récupérer les 8 propositions depuis identity.py
        proposals = layout_proposals.get_all()
        
        # Générer le HTML pour chaque proposition
        proposals_html = ""
        for proposal in proposals:
            colors = proposal.get("colors", {})
            preview_class = proposal.get("preview_class", "")
            
            proposals_html += f"""
            <div class="group cursor-pointer border-2 border-slate-100 rounded-2xl p-4 hover:border-indigo-400 hover:shadow-lg transition-all"
                 onclick="selectLayout('{proposal['id']}')">
                <div class="h-32 rounded-xl mb-4 flex items-center justify-center {preview_class}"
                     style="background-color: {colors.get('bg', '#fff')}; color: {colors.get('primary', '#000')}">
                    <span class="text-3xl font-bold">Aa</span>
                </div>
                <h3 class="font-bold text-slate-800">{proposal['name']}</h3>
                <p class="text-sm text-slate-500 mt-1">{proposal['description']}</p>
                <button class="mt-3 w-full bg-indigo-600 text-white py-2 rounded-lg font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                    Choisir ce style
                </button>
            </div>
            """
        
        return HTMLResponse(content=f"""
        <div class="p-8 max-w-6xl mx-auto animate-fade-in">
            <div class="text-center mb-8">
                <h2 class="text-2xl font-bold text-slate-800">8 Propositions de Styles</h2>
                <p class="text-slate-600 mt-2">Choisissez l'ambiance qui correspond à votre projet</p>
            </div>
            
            <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                {proposals_html}
            </div>
            
            <div class="mt-8 text-center">
                <button hx-get="/studio/step/5" 
                        hx-target="#studio-main-zone"
                        class="bg-slate-200 text-slate-700 px-6 py-3 rounded-xl font-bold hover:bg-slate-300 transition-colors">
                    ↩️ Retour au choix
                </button>
            </div>
            
            <script>
                function selectLayout(layoutId) {{
                    fetch('/studio/step/5/select-layout', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{layout_id: layoutId}})
                    }}).then(() => {{
                        htmx.ajax('GET', '/studio/step/6', '#studio-main-zone');
                    }});
                }}
            </script>
        </div>
        """)
        
    except Exception as e:
        logger.error(f"Error getting layout proposals: {e}")
        return HTMLResponse(
            content=f"""
            <div class="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                ❌ Erreur : {str(e)}
            </div>
            """,
            status_code=500
        )


@router.post("/step/5/select-layout", response_class=JSONResponse)
async def select_layout(request: Request):
    """
    Stocke le layout sélectionné dans la session.
    
    Request Body:
        {"layout_id": "minimal"}
    """
    try:
        data = await request.json()
        layout_id = data.get("layout_id")
        
        if not layout_id:
            raise HTTPException(status_code=400, detail="layout_id requis")
        
        # Vérifier que le layout existe
        proposal = layout_proposals.get_by_id(layout_id)
        if not proposal:
            raise HTTPException(status_code=404, detail="Layout non trouvé")
        
        # Stocker dans la session
        studio_session.selected_layout = layout_id
        studio_session.log(f"Layout sélectionné: {layout_id}")
        
        return {"success": True, "layout_id": layout_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error selecting layout: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Export pour inclusion dans api.py
__all__ = ["router"]
