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
# ROUTER & TEMPLATES
# =============================================================================

router = APIRouter(prefix="/studio", tags=["studio"])

# Templates Jinja2
templates_dir = Path(__file__).parent.parent / "templates"
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


async def get_step_5_choice(request: Request) -> HTMLResponse:
    """Étape 5 : Carrefour créatif (choix PNG vs Layouts)."""
    html = """
    <div id="studio-main-zone" class="p-8 max-w-4xl mx-auto animate-fade-in">
        <div class="text-center mb-10">
            <h2 class="text-2xl font-bold text-slate-800">C'est un peu générique, non ?</h2>
            <p class="text-slate-600 mt-2">Sullivan peut aller plus loin pour rendre ce projet unique.</p>
        </div>

        <div class="grid md:grid-cols-2 gap-8">
            <!-- Option 1 : Upload PNG -->
            <div class="relative border-2 border-dashed border-indigo-200 rounded-2xl p-8 hover:border-indigo-400 transition-colors bg-white group">
                <div id="upload-loader" class="htmx-indicator absolute inset-0 flex flex-col items-center justify-center bg-white/90 rounded-2xl z-10">
                    <div class="animate-spin w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full mb-3"></div>
                    <p class="text-sm font-medium text-slate-600">Analyse en cours…</p>
                    <p class="text-xs text-slate-500 mt-1">Extraction du style et de la structure</p>
                </div>
                <div class="flex flex-col items-center text-center">
                    <div class="w-16 h-16 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                        </svg>
                    </div>
                    <h3 class="text-lg font-semibold">Importez votre layout (PNG)</h3>
                    <p class="text-sm text-slate-500 mt-2 mb-6">Je vais analyser votre image pour en extraire le style et la structure.</p>
                    
                    <form hx-post="/studio/designer/upload" 
                          hx-encoding="multipart/form-data" 
                          hx-target="#studio-main-zone"
                          hx-indicator="#upload-loader">
                        <label class="cursor-pointer bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition-colors">
                            Choisir un fichier
                            <input type="file" name="design_file" accept=".png,.jpg,.jpeg" 
                                   class="hidden" onchange="this.form.requestSubmit()">
                        </label>
                    </form>
                </div>
            </div>

            <!-- Option 2 : Layout proposals -->
            <div class="border-2 border-slate-100 rounded-2xl p-8 hover:border-emerald-400 transition-colors bg-white group">
                <div class="flex flex-col items-center text-center">
                    <div class="w-16 h-16 bg-emerald-50 text-emerald-600 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                  d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"/>
                        </svg>
                    </div>
                    <h3 class="text-lg font-semibold">Proposez-moi des idées</h3>
                    <p class="text-sm text-slate-500 mt-2 mb-6">Je peux générer 8 propositions de styles adaptées à vos fonctions.</p>
                    
                    <button hx-get="/studio/step/5/layouts" 
                            hx-target="#studio-main-zone"
                            class="border border-emerald-600 text-emerald-600 px-6 py-2 rounded-lg hover:bg-emerald-50 transition-colors">
                        Voir les styles
                    </button>
                </div>
            </div>
        </div>
    </div>
    """
    return HTMLResponse(content=html)


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
    # Simule un rapport d'intention pour la démo
    report = studio_session.visual_intent_report
    
    if not report:
        # Crée un rapport de démo
        report = VisualIntentReport(
            metadata={
                "source_png": "upload_user.png",
                "style_global": {
                    "bg_color": "#1a1a1a",
                    "border_radius": "24px",
                    "primary_color": "#6366f1",
                    "font_family": "Geist Sans"
                }
            },
            zones=[
                VisualZone(
                    id="zone_header",
                    coordinates={"x": 0, "y": 0, "w": 1000, "h": 80},
                    hypothesis={
                        "label": "Veille du Système (/health)",
                        "confidence": 0.88,
                        "reasoning": "Zone horizontale haute identifiée comme barre d'état."
                    }
                ),
                VisualZone(
                    id="zone_center",
                    coordinates={"x": 200, "y": 100, "w": 600, "h": 500},
                    hypothesis={
                        "label": "Atelier de Construction (/execute)",
                        "confidence": 0.92,
                        "reasoning": "Large zone centrale pour l'atelier."
                    }
                )
            ]
        )
        studio_session.visual_intent_report = report
    
    zones_html = ""
    for zone in report.zones:
        coords = zone.coordinates
        confidence_pct = int(zone.hypothesis.get("confidence", 0) * 100)
        
        zones_html += f"""
        <g class="group cursor-pointer" onclick="toggleZone('{zone.id}')">
            <rect x="{coords['x']}" y="{coords['y']}" 
                  width="{coords['w']}" height="{coords['h']}"
                  fill="rgba(99, 102, 241, 0.15)" stroke="#6366f1" stroke-width="2" 
                  stroke-dasharray="6 4" class="hover:fill-indigo-300/30 transition-all"/>
            
            <foreignObject x="{coords['x']}" y="{coords['y'] - 30}" width="300" height="40">
                <div class="bg-indigo-600 text-white text-[10px] px-2 py-1 rounded-t-lg font-bold inline-block">
                    {zone.hypothesis.get('label', 'Zone')} ({confidence_pct}%)
                </div>
            </foreignObject>
        </g>
        """
    
    style = report.metadata.get("style_global", {})
    
    html = f"""
    <div class="p-6 max-w-5xl mx-auto">
        <div class="text-center mb-6">
            <h2 class="text-2xl font-bold text-slate-800">Analyse du layout</h2>
            <p class="text-slate-500">J'ai analysé votre image. Voici ce que j'ai détecté :</p>
        </div>
        
        <div class="relative border-4 border-indigo-200 rounded-2xl overflow-hidden bg-slate-100">
            <!-- Placeholder pour l'image uploadée -->
            <div class="w-full h-96 flex items-center justify-center text-slate-400">
                <div class="text-center">
                    <svg class="w-16 h-16 mx-auto mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                    </svg>
                    <p>Votre layout sera affiché ici</p>
                </div>
            </div>
            
            <!-- Calque SVG avec les zones détectées -->
            <svg class="absolute inset-0 w-full h-full" viewBox="0 0 1000 600" preserveAspectRatio="xMidYMid slice">
                {zones_html}
            </svg>
        </div>
        
        <div class="mt-6 bg-white rounded-xl p-6 border border-slate-200">
            <h3 class="font-bold text-slate-800 mb-4">Style détecté</h3>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="p-3 bg-slate-50 rounded-lg">
                    <p class="text-xs text-slate-500">Fond</p>
                    <div class="flex items-center gap-2 mt-1">
                        <div class="w-6 h-6 rounded border" style="background-color: {style.get('bg_color', '#fff')}"></div>
                        <span class="text-sm font-mono">{style.get('bg_color', '#ffffff')}</span>
                    </div>
                </div>
                <div class="p-3 bg-slate-50 rounded-lg">
                    <p class="text-xs text-slate-500">Accent</p>
                    <div class="flex items-center gap-2 mt-1">
                        <div class="w-6 h-6 rounded border" style="background-color: {style.get('primary_color', '#6366f1')}"></div>
                        <span class="text-sm font-mono">{style.get('primary_color', '#6366f1')}</span>
                    </div>
                </div>
                <div class="p-3 bg-slate-50 rounded-lg">
                    <p class="text-xs text-slate-500">Coins</p>
                    <p class="text-sm font-medium mt-1">{style.get('border_radius', '8px')}</p>
                </div>
                <div class="p-3 bg-slate-50 rounded-lg">
                    <p class="text-xs text-slate-500">Typographie</p>
                    <p class="text-sm font-medium mt-1">{style.get('font_family', 'System')}</p>
                </div>
            </div>
        </div>
        
        <div class="mt-6 flex justify-between">
            <button hx-post="/studio/next/5"
                    hx-target="#studio-main-zone"
                    class="text-slate-500 hover:text-slate-700">
                ← Retour
            </button>
            <button hx-post="/studio/next/6"
                    hx-target="#studio-main-zone"
                    class="bg-indigo-600 text-white px-6 py-2 rounded-lg font-bold hover:bg-indigo-700">
                Continuer vers le dialogue →
            </button>
        </div>
    </div>
    """
    
    return HTMLResponse(content=html)


async def get_step_7_dialogue(request: Request) -> HTMLResponse:
    """Étape 7 : Dialogue (post-its, questions Sullivan)."""
    report = studio_session.visual_intent_report
    
    if not report:
        report = VisualIntentReport(
            metadata={"style_global": {"border_radius": "24px"}},
            zones=[
                VisualZone(
                    id="zone_1",
                    coordinates={},
                    hypothesis={"label": "Veille du Système", "confidence": 0.85}
                )
            ]
        )
    
    questions = generate_dialogue_proposals(report)
    
    questions_html = ""
    for q in questions:
        questions_html += f"""
        <div class="bg-yellow-100 p-4 rounded-lg shadow-sm rotate-1 hover:rotate-0 transition-transform">
            <p class="text-sm text-slate-800">{q['text']}</p>
            <div class="mt-3 flex gap-2">
                <button class="text-xs bg-green-500 text-white px-3 py-1 rounded-full hover:bg-green-600">
                    ✓ Oui
                </button>
                <button class="text-xs bg-slate-400 text-white px-3 py-1 rounded-full hover:bg-slate-500">
                    ✗ Non
                </button>
            </div>
        </div>
        """
    
    # Question globale sur le style
    style_q = f"""
    <div class="bg-indigo-100 p-4 rounded-lg shadow-sm -rotate-1 hover:rotate-0 transition-transform">
        <p class="text-sm text-slate-800">
            J'ai relevé un style avec coins très arrondis. On garde cet aspect ?
        </p>
        <div class="mt-3 flex gap-2">
            <button class="text-xs bg-indigo-500 text-white px-3 py-1 rounded-full hover:bg-indigo-600">
                ✓ Parfait
            </button>
            <button class="text-xs bg-slate-400 text-white px-3 py-1 rounded-full hover:bg-slate-500">
                Ajuster...
            </button>
        </div>
    </div>
    """
    
    html = f"""
    <div class="p-6 max-w-4xl mx-auto">
        <div class="text-center mb-8">
            <h2 class="text-2xl font-bold text-slate-800">Un dernier mot...</h2>
            <p class="text-slate-500">Avant de finaliser, quelques questions pour affiner :</p>
        </div>
        
        <div class="grid md:grid-cols-2 gap-6">
            {questions_html}
            {style_q}
        </div>
        
        <div class="mt-8 text-center">
            <button hx-post="/studio/next/7"
                    hx-target="#studio-main-zone"
                    class="bg-indigo-600 text-white px-8 py-3 rounded-xl font-bold hover:bg-indigo-700">
                Valider et continuer →
            </button>
        </div>
    </div>
    """
    
    return HTMLResponse(content=html)


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


# Export pour inclusion dans api.py
__all__ = ["router"]
