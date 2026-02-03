"""
identity.py - Cerveau HCI de Sullivan

Ce fichier constitue le cœur du réacteur HCI pour Sullivan, intégrant :
- La navigation Top-Bottom
- La médiation pédagogique
- L'audit d'homéostasie
- La traduction Tech -> Humain
"""

import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


# =============================================================================
# BIBLIOTHÈQUES ET DICTIONNAIRES DE RÉFÉRENCE
# =============================================================================

SULLIVAN_HCI_STENCILS = {
    "monitoring": {
        "title": "Indicateur de Vigilance",
        "description": "Un repère visuel pour confirmer que l'IA est connectée et opérationnelle.",
        "stencil_type": "status_dot_pulse",
        "icon": "shield-check",
        "endpoints": ["/health"]
    },
    "orchestrator": {
        "title": "Atelier de Construction",
        "description": "L'espace où les plans JSON deviennent des fichiers Python et HTML.",
        "stencil_type": "progress_stepper",
        "icon": "hammer",
        "endpoints": ["/execute"]
    },
    "gallery": {
        "title": "Bibliothèque de Styles",
        "description": "Une grille pour choisir et prévisualiser vos composants.",
        "stencil_type": "component_grid",
        "icon": "library",
        "endpoints": ["/sullivan/search", "/sullivan/components"]
    },
    "designer": {
        "title": "Miroir Créatif",
        "description": "Analyse votre design PNG pour extraire le style et la structure.",
        "stencil_type": "image_upload",
        "icon": "camera",
        "endpoints": ["/sullivan/designer/upload"]
    },
    "preview": {
        "title": "Bac à Sable",
        "description": "Permet de tester les composants sans tout casser.",
        "stencil_type": "preview_frame",
        "icon": "eye",
        "endpoints": ["/sullivan/preview"]
    }
}

SULLIVAN_DEFAULT_LIBRARY = {
    "status_orb": {
        "html": """<div class="flex items-center gap-2 p-4 bg-gray-50 border rounded-lg" hx-get="/health">
    <div class="relative">
        <div class="w-3 h-3 bg-green-500 rounded-full"></div>
        <div class="absolute inset-0 w-3 h-3 bg-green-500 rounded-full animate-ping opacity-75"></div>
    </div>
    <span class="font-medium text-slate-700">Système Opérationnel</span>
</div>""",
        "description": "Composant de veille standard.",
        "category": "monitoring"
    },
    "action_stepper": {
        "html": """<div class="p-6 bg-slate-900 text-slate-300 rounded-2xl font-mono text-xs">
    <div class="flex items-center gap-2 mb-4 border-b border-slate-700 pb-2">
        <span class="text-emerald-400">></span>
        <span class="text-slate-100 font-bold uppercase tracking-tighter">Workflow Terminal</span>
    </div>
    <div class="space-y-1">
        <p class="text-emerald-500/80">[OK] Initialisation du noyau...</p>
        <p class="animate-pulse">_ En attente d'instruction...</p>
    </div>
</div>""",
        "description": "Interface de suivi d'exécution.",
        "category": "orchestrator"
    },
    "component_card": {
        "html": """<div class="group p-5 border-2 border-slate-100 rounded-2xl bg-white hover:border-indigo-300 hover:shadow-xl transition-all">
    <div class="flex items-start gap-4">
        <div class="p-3 bg-indigo-50 text-indigo-600 rounded-xl">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/></svg>
        </div>
        <div>
            <h4 class="font-bold text-slate-800">Composant</h4>
            <p class="text-sm text-slate-500">Description du composant</p>
        </div>
    </div>
</div>""",
        "description": "Carte de composant pour la galerie.",
        "category": "gallery"
    },
    "upload_zone": {
        "html": """<div class="border-2 border-dashed border-indigo-200 rounded-2xl p-8 hover:border-indigo-400 transition-colors bg-white text-center">
    <div class="w-16 h-16 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
    </div>
    <h3 class="text-lg font-semibold text-slate-800">Importez votre layout</h3>
    <p class="text-sm text-slate-500 mt-2">PNG, JPG ou SVG</p>
</div>""",
        "description": "Zone d'upload pour les designs.",
        "category": "designer"
    }
}

# Les 8 propositions de styles pour l'étape 5 (sans PNG)
SULLIVAN_LAYOUT_PROPOSALS = [
    {
        "id": "minimal",
        "name": "Minimaliste",
        "description": "Clean & Airy - Espaces généreux, typographie légère, pas de superflu.",
        "colors": {"bg": "#ffffff", "primary": "#171717", "accent": "#525252"},
        "preview_class": "bg-white border-slate-200"
    },
    {
        "id": "brutalist",
        "name": "Brutaliste",
        "description": "Raw & Bold - Bords vifs, contrastes forts, typographie système.",
        "colors": {"bg": "#ff00ff", "primary": "#000000", "accent": "#00ffff"},
        "preview_class": "bg-black text-white border-4 border-white"
    },
    {
        "id": "tdah_focus",
        "name": "Focus TDAH",
        "description": "High Contrast & Low Noise - Maximum de contraste, minimum de distractions.",
        "colors": {"bg": "#0a0a0a", "primary": "#00ff00", "accent": "#ff00ff"},
        "preview_class": "bg-black text-green-400 border-2 border-green-400"
    },
    {
        "id": "glassmorphism",
        "name": "Glassmorphism",
        "description": "Translucide & Moderne - Effets de flou, transparence, lumière diffuse.",
        "colors": {"bg": "rgba(255,255,255,0.1)", "primary": "#6366f1", "accent": "#8b5cf6"},
        "preview_class": "bg-gradient-to-br from-indigo-100 to-purple-100"
    },
    {
        "id": "neumorphism",
        "name": "Neumorphism",
        "description": "Soft & Tactile - Ombres douces, effets de relief, surfaces douces.",
        "colors": {"bg": "#e0e5ec", "primary": "#4a5568", "accent": "#718096"},
        "preview_class": "bg-slate-200"
    },
    {
        "id": "cyberpunk",
        "name": "Cyberpunk",
        "description": "Neon & Dark - Fond sombre, néons brillants, futuriste.",
        "colors": {"bg": "#0f0f23", "primary": "#00ffff", "accent": "#ff0080"},
        "preview_class": "bg-slate-900 text-cyan-400 border border-cyan-400"
    },
    {
        "id": "organic",
        "name": "Organique",
        "description": "Nature & Flow - Formes arrondies, couleurs terreuses, douceur.",
        "colors": {"bg": "#faf7f2", "primary": "#8b6914", "accent": "#c4a35a"},
        "preview_class": "bg-amber-50 text-amber-800"
    },
    {
        "id": "corporate",
        "name": "Corporate",
        "description": "Pro & Fiable - Bleu professionnel, grille stricte, hiérarchie claire.",
        "colors": {"bg": "#f8fafc", "primary": "#1e40af", "accent": "#3b82f6"},
        "preview_class": "bg-slate-50 border-blue-200"
    }
]


# =============================================================================
# CLASSES DU KERNEL SULLIVAN
# =============================================================================

@dataclass
class VisualZone:
    """Zone détectée dans une image (étape 6)."""
    id: str
    coordinates: Dict[str, int]  # x, y, w, h
    hypothesis: Dict[str, Any]   # label, confidence, reasoning
    user_validation: Optional[bool] = None


@dataclass
class VisualIntentReport:
    """Rapport d'intention visuelle (étape 6)."""
    metadata: Dict[str, Any]
    zones: List[VisualZone] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "metadata": self.metadata,
            "zones": [
                {
                    "id": z.id,
                    "coordinates": z.coordinates,
                    "hypothesis": z.hypothesis,
                    "user_validation": z.user_validation
                }
                for z in self.zones
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VisualIntentReport":
        zones = [
            VisualZone(
                id=z["id"],
                coordinates=z["coordinates"],
                hypothesis=z["hypothesis"],
                user_validation=z.get("user_validation")
            )
            for z in data.get("zones", [])
        ]
        return cls(metadata=data.get("metadata", {}), zones=zones)


class SullivanKernel:
    """
    Le cerveau HCI de Sullivan.
    Rôles : Médiateur, Designer, Auditeur
    """
    
    def __init__(self, mode: str = "normal"):
        self.mode = mode  # "normal" (HCI/Pédagogique) ou "expert" (Tech/Raw)
        self.journal_narratif: List[str] = []  # ML-Ready journal
    
    def get_intent_translation(self, endpoint: str) -> Dict[str, str]:
        """
        Traduit un endpoint brut en intention pédagogique (Mode Normal).
        
        Args:
            endpoint: Chemin de l'endpoint API
            
        Returns:
            Dictionnaire avec label, icon, desc
        """
        translations = {
            "/health": {
                "label": "Veille du Système",
                "icon": "shield-check",
                "desc": "Assure la santé de l'IA."
            },
            "/execute": {
                "label": "Atelier de Construction",
                "icon": "hammer",
                "desc": "Transforme les plans en code."
            },
            "/sullivan/search": {
                "label": "Web-othèque",
                "icon": "library",
                "desc": "Piochez dans vos composants."
            },
            "/sullivan/components": {
                "label": "Galerie de Composants",
                "icon": "layout-grid",
                "desc": "Parcourez votre bibliothèque."
            },
            "/sullivan/designer/upload": {
                "label": "Miroir Créatif",
                "icon": "camera",
                "desc": "Analyse votre design PNG."
            },
            "/sullivan/preview": {
                "label": "Bac à Sable",
                "icon": "eye",
                "desc": "Testez sans tout casser."
            },
            "/studio/genome": {
                "label": "Génome Technique",
                "icon": "dna",
                "desc": "La topologie de votre application."
            }
        }
        return translations.get(endpoint, {
            "label": endpoint,
            "icon": "cpu",
            "desc": "Fonction technique."
        })
    
    def get_stencil_for_endpoint(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """
        Retourne le stencil HCI associé à un endpoint.
        
        Args:
            endpoint: Chemin de l'endpoint
            
        Returns:
            Stencil correspondant ou None
        """
        for stencil_id, stencil in SULLIVAN_HCI_STENCILS.items():
            if endpoint in stencil.get("endpoints", []):
                return {"id": stencil_id, **stencil}
        return None
    
    def get_all_stencils(self) -> Dict[str, Dict[str, Any]]:
        """Retourne tous les stencils disponibles."""
        return SULLIVAN_HCI_STENCILS
    
    def log_event(self, step: int, event_detail: str) -> None:
        """
        Journalisation narrative pour la valeur pédagogique.
        
        Args:
            step: Numéro de l'étape (1-9)
            event_detail: Description de l'événement
        """
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] Étape {step} : {event_detail}"
        self.journal_narratif.append(log_entry)
        # TODO: Link to ML DB for predictive UX
    
    def get_journal(self) -> List[str]:
        """Retourne le journal narratif."""
        return self.journal_narratif
    
    def clear_journal(self) -> None:
        """Vide le journal narratif."""
        self.journal_narratif = []


class SullivanNavigator:
    """
    Gère la navigation Top-Bottom et l'Arbre d'États.
    Niveaux : Corps > Organe > Atome
    """
    
    def __init__(self):
        self.history: List[Dict[str, Any]] = []  # Pile pour le backtrack
        self.current_level: str = "corps"  # corps, organe, atome
        self.current_id: Optional[str] = None
    
    def zoom_in(self, target_level: str, target_id: str) -> Dict[str, Any]:
        """
        Passe du Corps -> Organe -> Atome.
        
        Args:
            target_level: Niveau cible (organe, atome)
            target_id: Identifiant de la cible
            
        Returns:
            Contexte avec flag 'ghost' pour le mode fantôme
        """
        # Sauvegarde le contexte actuel
        self.history.append({
            "level": self.current_level,
            "id": self.current_id
        })
        
        self.current_level = target_level
        self.current_id = target_id
        
        # Déclenche l'affichage 'Ghost Mode' pour le contexte spatial
        return {
            "context": "ghost",
            "focus": target_id,
            "level": target_level,
            "previous": self.history[-1] if self.history else None
        }
    
    def zoom_out(self) -> Optional[Dict[str, Any]]:
        """
        Remonte la strate (Atome -> Organe -> Corps).
        
        Returns:
            Contexte précédent ou None si déjà au top
        """
        if self.history:
            previous = self.history.pop()
            self.current_level = previous["level"]
            self.current_id = previous["id"]
            return previous
        return None
    
    def jump_to(self, step_id: int) -> Dict[str, Any]:
        """
        Permet de revenir à une étape précédente.
        
        Args:
            step_id: Numéro de l'étape cible
            
        Returns:
            Nouveau contexte
        """
        # Purge les étapes intermédiaires pour recalculer
        self.history = [h for h in self.history if h.get("step", 0) <= step_id]
        return {
            "context": "jump",
            "target_step": step_id,
            "new_history": self.history
        }
    
    def get_current_position(self) -> Dict[str, Any]:
        """Retourne la position actuelle dans l'arbre."""
        return {
            "level": self.current_level,
            "id": self.current_id,
            "depth": len(self.history)
        }
    
    def can_zoom_out(self) -> bool:
        """Vérifie si on peut remonter d'un niveau."""
        return len(self.history) > 0


class SullivanAuditor:
    """
    Garde-fou d'Homéostasie.
    Vérifie que le design respecte les fonctions vitales du Génome.
    """
    
    def check_homeostasis(
        self,
        current_design: Dict[str, Any],
        genome: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Vérifie que le design respecte les fonctions vitales.
        
        Args:
            current_design: Design actuel avec active_functions (liste de paths API)
            genome: Génome de référence
            
        Returns:
            Liste d'alertes si des fonctions vitales manquent
        """
        alerts = []
        required_endpoints = genome.get("endpoints", [])
        active_functions = current_design.get("active_functions", [])
        
        # Parcours layout (step 5) : pas d'arbitrage IR → pas de mapping section→endpoint.
        # On ne génère pas d'alertes pour éviter des faux positifs.
        if not active_functions:
            return []
        
        for ep in required_endpoints:
            path = ep.get("path", "") if isinstance(ep, dict) else ep
            if path not in active_functions:
                kernel = SullivanKernel()
                translation = kernel.get_intent_translation(path)
                
                alerts.append({
                    "type": "missing_function",
                    "endpoint": path,
                    "severity": "warning",
                    "message": f"Attention, l'organe '{translation['label']}' ({path}) est absent !",
                    "suggestion": f"Ajoutez un composant pour {translation['desc']}"
                })
        
        return alerts
    
    def validate_style_consistency(
        self,
        visual_report: VisualIntentReport
    ) -> List[Dict[str, Any]]:
        """
        Valide la cohérence du style extrait.
        
        Args:
            visual_report: Rapport d'intention visuelle
            
        Returns:
            Liste de suggestions
        """
        suggestions = []
        style = visual_report.metadata.get("style_global", {})
        
        # Vérifie le border_radius
        radius = style.get("border_radius", "")
        if radius and "px" in radius:
            try:
                r_val = int(radius.replace("px", ""))
                if r_val > 50:
                    suggestions.append({
                        "type": "style",
                        "message": "Coins très arrondis détectés - style 'bubble' prononcé",
                        "confidence": 0.9
                    })
            except ValueError:
                pass
        
        return suggestions


class Distiller:
    """
    Génération finale par Surgical Edit à l'étape 9.
    Applique le style et le layout validés aux composants.
    """
    
    def apply_adaptation(
        self,
        base_components: Dict[str, str],
        validated_report: VisualIntentReport
    ) -> Dict[str, str]:
        """
        Applique style et layout validés aux composants par défaut.
        
        Args:
            base_components: Composants de base (HTML)
            validated_report: Rapport validé
            
        Returns:
            Composants adaptés
        """
        style = validated_report.metadata.get("style_global", {})
        adapted = {}
        
        for comp_id, html in base_components.items():
            # Injection chirurgicale du style
            adapted_html = self._inject_style(html, style)
            adapted[comp_id] = adapted_html
        
        return adapted
    
    def _inject_style(self, html: str, style: Dict[str, str]) -> str:
        """
        Injecte le style dans le HTML.
        
        Args:
            html: HTML de base
            style: Styles à appliquer
            
        Returns:
            HTML stylisé
        """
        # TODO: Implement surgical HTML string replacement logic
        # Pour l'instant, remplace les classes de border-radius
        if "border_radius" in style:
            # Exemple simple : remplace rounded-lg par valeur spécifique
            radius = style["border_radius"]
            html = html.replace("rounded-lg", f"rounded-[{radius}]")
        
        if "bg_color" in style:
            # Injecte le background si possible
            pass
        
        return html
    
    def generate_component_placement(
        self,
        zones: List[VisualZone],
        components: Dict[str, str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Génère le placement des composants dans les zones.
        
        Args:
            zones: Zones détectées
            components: Composants disponibles
            
        Returns:
            Mapping zone -> composant
        """
        placement = {}
        
        for zone in zones:
            if zone.user_validation:
                label = zone.hypothesis.get("label", "")
                # Trouve le composant correspondant
                for comp_id, comp_html in components.items():
                    if comp_id in label.lower() or label.lower() in comp_html.lower():
                        placement[zone.id] = {
                            "component_id": comp_id,
                            "coordinates": zone.coordinates,
                            "html": comp_html
                        }
                        break
        
        return placement


class LayoutProposals:
    """
    Gère les 8 propositions de layout pour l'étape 5.
    """
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Retourne les 8 propositions de styles."""
        return SULLIVAN_LAYOUT_PROPOSALS
    
    def get_by_id(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        """
        Retourne une proposition par son ID.
        
        Args:
            proposal_id: Identifiant de la proposition
            
        Returns:
            Proposition ou None
        """
        for proposal in SULLIVAN_LAYOUT_PROPOSALS:
            if proposal["id"] == proposal_id:
                return proposal
        return None
    
    def get_preview_html(self, proposal_id: str) -> str:
        """
        Génère le HTML de prévisualisation pour une proposition.
        
        Args:
            proposal_id: ID de la proposition
            
        Returns:
            HTML de prévisualisation
        """
        proposal = self.get_by_id(proposal_id)
        if not proposal:
            return "<div>Proposition non trouvée</div>"
        
        colors = proposal.get("colors", {})
        preview_class = proposal.get("preview_class", "")
        
        return f"""
        <div class="p-6 rounded-xl {preview_class} border-2 transition-all hover:scale-105 cursor-pointer">
            <div class="h-32 flex items-center justify-center rounded-lg mb-4" 
                 style="background-color: {colors.get('bg', '#fff')}; color: {colors.get('primary', '#000')}">
                <span class="text-2xl font-bold">Aa</span>
            </div>
            <h3 class="font-bold text-lg">{proposal['name']}</h3>
            <p class="text-sm opacity-75 mt-1">{proposal['description']}</p>
        </div>
        """


def _normalize_principles_to_style(dp: Dict[str, Any]) -> Dict[str, str]:
    """
    Mappe le format Gemini (colors.primary, primary_color, etc.) vers style_global.
    """
    colors = dp.get("colors", {}) if isinstance(dp.get("colors"), dict) else {}
    primary = dp.get("primary_color") or colors.get("primary") or "#6366f1"
    bg = dp.get("bg_color") or colors.get("bg") or colors.get("main") or "#ffffff"
    radius = dp.get("border_radius") or "8px"
    font = dp.get("font_family") or "system-ui"
    return {
        "primary_color": str(primary),
        "bg_color": str(bg),
        "border_radius": str(radius),
        "font_family": str(font),
    }


def design_structure_to_visual_intent_report(
    design_structure: Dict[str, Any],
    design_principles: Optional[Dict[str, Any]] = None,
) -> VisualIntentReport:
    """
    Mappe design_structure (DesignAnalyzer) vers VisualIntentReport.

    Args:
        design_structure: Dict avec sections, components, layout, hierarchy
        design_principles: Optionnel, pour enrichir style_global

    Returns:
        VisualIntentReport pour l'étape 6
    """
    # metadata.style_global depuis design_principles > layout > components > défaut
    layout = design_structure.get("layout", {})
    components = design_structure.get("components", [])
    style_global = {}
    if design_principles:
        style_global = _normalize_principles_to_style(design_principles)
    else:
        for comp in components[:3]:
            comp_style = comp.get("style", {})
            if comp_style:
                style_global.update(comp_style)
                break
        if not style_global:
            # Fallback layout (primary_color, font_family, etc. si présents)
            for key in ("primary_color", "bg_color", "border_radius", "font_family"):
                if layout.get(key):
                    style_global[key] = layout.get(key)
        if not style_global:
            style_global = {"border_radius": "8px", "primary_color": "#6366f1"}

    metadata = {"style_global": style_global, "source": "design_analyzer"}

    # zones depuis sections
    zones = []
    for i, section in enumerate(design_structure.get("sections", [])):
        section_type = section.get("type", f"zone_{i}")
        bounds = section.get("bounds", [0, 0, 100, 100])
        if isinstance(bounds, list) and len(bounds) >= 4:
            coords = {"x": bounds[0], "y": bounds[1], "w": bounds[2], "h": bounds[3]}
        else:
            coords = {"x": 0, "y": 0, "w": 100, "h": 100}
        zones.append(
            VisualZone(
                id=section_type.lower().replace(" ", "_"),
                coordinates=coords,
                hypothesis={
                    "label": section_type,
                    "confidence": 0.85,
                    "reasoning": section.get("description", f"Section {section_type} détectée"),
                },
                user_validation=None,
            )
        )

    return VisualIntentReport(metadata=metadata, zones=zones)


def generate_dialogue_proposals(
    intention_report: VisualIntentReport
) -> List[Dict[str, Any]]:
    """
    Génère les questions pour le dialogue (étape 7).
    
    Args:
        intention_report: Rapport d'intention visuelle
        
    Returns:
        Liste de questions
    """
    questions = []
    
    for zone in intention_report.zones:
        confidence = zone.hypothesis.get("confidence", 0)
        if confidence < 0.90:
            questions.append({
                "target_zone": zone.id,
                "type": "validation",
                "text": f"J'hésite pour la {zone.id}. J'y verrais bien '{zone.hypothesis.get('label')}', on valide ?",
                "confidence": confidence
            })
    
    # Question sur le style global
    style = intention_report.metadata.get("style_global", {})
    if style.get("border_radius"):
        questions.append({
            "target_zone": "global",
            "type": "style",
            "text": f"J'ai relevé un style avec coins à {style['border_radius']}. On garde cet aspect ?",
            "confidence": 0.85
        })
    
    return questions


# =============================================================================
# INITIALISATION GLOBALE
# =============================================================================

# Instances globales pour le Studio
sullivan = SullivanKernel(mode="normal")
navigator = SullivanNavigator()
auditor = SullivanAuditor()
distiller = Distiller()
layout_proposals = LayoutProposals()


# Export pour compatibilité
__all__ = [
    "SullivanKernel",
    "design_structure_to_visual_intent_report",
    "SullivanNavigator", 
    "SullivanAuditor",
    "Distiller",
    "LayoutProposals",
    "VisualIntentReport",
    "VisualZone",
    "SULLIVAN_HCI_STENCILS",
    "SULLIVAN_DEFAULT_LIBRARY",
    "SULLIVAN_LAYOUT_PROPOSALS",
    "generate_dialogue_proposals",
    # Instances globales
    "sullivan",
    "navigator",
    "auditor",
    "distiller",
    "layout_proposals"
]
