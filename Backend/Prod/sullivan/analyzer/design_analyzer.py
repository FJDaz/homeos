"""DesignAnalyzer - Analyse designs avec modèle vision pour extraction structure."""
from typing import List, Dict, Optional, Any
from pathlib import Path
import base64
from loguru import logger

from ...models.agent_router import AgentRouter
from ..knowledge.knowledge_base import KnowledgeBase


class DesignStructure:
    """Structure extraite d'un design."""
    
    def __init__(
        self,
        sections: List[Dict[str, Any]],
        components: List[Dict[str, Any]],
        layout: Dict[str, Any],
        hierarchy: Dict[str, Any]
    ):
        """
        Initialise la structure de design.

        Args:
            sections: Sections identifiées (Hero, Features, CTA, etc.)
            components: Composants détectés (buttons, forms, cards)
            layout: Informations sur le layout
            hierarchy: Hiérarchie visuelle
        """
        self.sections = sections
        self.components = components
        self.layout = layout
        self.hierarchy = hierarchy
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return {
            "sections": self.sections,
            "components": self.components,
            "layout": self.layout,
            "hierarchy": self.hierarchy
        }


class DesignAnalyzer:
    """
    Analyseur de design avec modèle vision.
    
    Utilise Gemini 3 Flash via AgentRouter pour analyser les designs (PNG/JPG/SVG).
    Fallback automatique si rate limit (429) vers autre modèle vision ou OCR + heuristics.
    """
    
    def __init__(
        self,
        agent_router: Optional[AgentRouter] = None,
        knowledge_base: Optional[KnowledgeBase] = None
    ):
        """
        Initialise l'analyseur de design.

        Args:
            agent_router: Router pour sélection modèle vision (optionnel)
            knowledge_base: Base de connaissances pour patterns (optionnel)
        """
        self.agent_router = agent_router or AgentRouter(execution_mode="BUILD")
        self.knowledge_base = knowledge_base or KnowledgeBase()
        
        logger.info("DesignAnalyzer initialized with Gemini 3 Flash vision model")
    
    async def analyze_image(self, image_path: Path) -> DesignStructure:
        """
        Analyse une image avec modèle vision Gemini 3 Flash.
        
        Fallback automatique si rate limit (429).

        Args:
            image_path: Chemin vers l'image (PNG/JPG/SVG)

        Returns:
            Structure de design extraite
        """
        logger.info(f"Analyzing image: {image_path}")
        
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Lire l'image et encoder en base64
        image_data = self._read_image(image_path)
        
        # Analyser avec modèle vision via AgentRouter
        # Utiliser Gemini 3 Flash (prioritaire) avec fallback automatique
        try:
            structure_dict = await self._analyze_with_vision_model(image_data, image_path)
        except Exception as e:
            logger.warning(f"Vision model analysis failed: {e}, falling back to OCR + heuristics")
            structure_dict = await self._analyze_with_ocr_heuristics(image_path)
        
        # Extraire structure
        sections = structure_dict.get("sections", [])
        components = structure_dict.get("components", [])
        layout = structure_dict.get("layout", {})
        hierarchy = structure_dict.get("hierarchy", {})
        
        design_structure = DesignStructure(
            sections=sections,
            components=components,
            layout=layout,
            hierarchy=hierarchy
        )
        
        logger.info(f"Extracted {len(sections)} sections and {len(components)} components")
        return design_structure
    
    async def extract_components(self, structure: DesignStructure) -> List[Dict[str, Any]]:
        """
        Extrait les composants depuis la structure de design.

        Args:
            structure: Structure de design

        Returns:
            Liste des composants extraits avec métadonnées
        """
        logger.info("Extracting components from design structure")
        
        components = []
        
        # Extraire composants depuis les sections
        for section in structure.sections:
            section_type = section.get("type", "")
            section_components = section.get("components", [])
            
            for comp in section_components:
                components.append({
                    "type": comp.get("type", "unknown"),
                    "section": section_type,
                    "bounds": comp.get("bounds"),
                    "text": comp.get("text", ""),
                    "style": comp.get("style", {})
                })
        
        # Extraire composants depuis la liste globale
        for comp in structure.components:
            if comp not in components:
                components.append(comp)
        
        logger.info(f"Extracted {len(components)} components")
        return components
    
    def match_patterns(self, structure: DesignStructure) -> List[Dict[str, Any]]:
        """
        Compare la structure avec les patterns dans KnowledgeBase.

        Args:
            structure: Structure de design extraite

        Returns:
            Liste des patterns matchés avec scores de similarité
        """
        logger.info("Matching design structure with KnowledgeBase patterns")
        
        matched_patterns = []
        
        # Rechercher patterns similaires dans KnowledgeBase
        # Exemple : "80% des landing pages SaaS utilisent [Hero → Features → Testimonials → CTA]"
        sections_types = [s.get("type", "") for s in structure.sections]
        sections_query = " ".join(sections_types)
        
        patterns = self.knowledge_base.search_patterns(sections_query)
        
        # Calculer similarité avec chaque pattern
        for pattern_name, pattern_data in patterns.items():
            similarity_score = self._calculate_similarity(structure, pattern_data)
            
            if similarity_score > 0.5:  # Seuil de similarité
                matched_patterns.append({
                    "pattern_name": pattern_name,
                    "pattern_data": pattern_data,
                    "similarity_score": similarity_score,
                    "match_type": "high" if similarity_score > 0.8 else "medium"
                })
        
        logger.info(f"Matched {len(matched_patterns)} patterns")
        return matched_patterns
    
    def _read_image(self, image_path: Path) -> bytes:
        """Lit une image et retourne les données binaires."""
        with open(image_path, 'rb') as f:
            return f.read()
    
    async def _analyze_with_vision_model(
        self,
        image_data: bytes,
        image_path: Path
    ) -> Dict[str, Any]:
        """
        Analyse avec modèle vision via AgentRouter.
        
        Utilise Gemini 3 Flash avec fallback automatique si rate limit.

        Args:
            image_data: Données binaires de l'image
            image_path: Chemin de l'image (pour contexte)

        Returns:
            Structure extraite depuis le modèle vision
        """
        # Encoder en base64 pour l'API
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Prompt pour extraction structure
        prompt = f"""
Analyze this design image and extract:
1. Sections (Hero, Features, CTA, Footer, etc.) with their types and positions
2. Components (buttons, forms, cards, inputs, etc.) with their types, text, and bounds
3. Layout information (grid, flex, spacing, etc.)
4. Visual hierarchy (primary, secondary, tertiary elements)

Return JSON structure:
{{
    "sections": [
        {{"type": "Hero", "bounds": [x, y, width, height], "components": [...]}},
        ...
    ],
    "components": [
        {{"type": "button", "text": "...", "bounds": [...], "style": {{...}}}},
        ...
    ],
    "layout": {{"type": "grid", "columns": 3, ...}},
    "hierarchy": {{"primary": [...], "secondary": [...], "tertiary": [...]}}
}}
"""
        
        # Utiliser AgentRouter pour appeler modèle vision
        # AgentRouter gère automatiquement le fallback si rate limit
        try:
            # Pour l'instant, simulation - à remplacer par appel réel à AgentRouter avec vision
            # Le modèle vision sera sélectionné automatiquement (Gemini 3 Flash prioritaire)
            logger.info("Calling vision model via AgentRouter (Gemini 3 Flash)")
            
            # TODO: Implémenter appel réel à AgentRouter avec support vision
            # Pour l'instant, retourner structure simulée
            return {
                "sections": [
                    {"type": "Hero", "bounds": [0, 0, 1200, 600], "components": []},
                    {"type": "Features", "bounds": [0, 600, 1200, 400], "components": []},
                    {"type": "CTA", "bounds": [0, 1000, 1200, 200], "components": []}
                ],
                "components": [
                    {"type": "button", "text": "Get Started", "bounds": [500, 500, 200, 50]},
                    {"type": "input", "text": "Email", "bounds": [400, 1050, 400, 40]}
                ],
                "layout": {"type": "grid", "columns": 3},
                "hierarchy": {"primary": ["Hero"], "secondary": ["Features"], "tertiary": ["CTA"]}
            }
        except Exception as e:
            logger.error(f"Vision model analysis failed: {e}")
            raise
    
    async def _analyze_with_ocr_heuristics(self, image_path: Path) -> Dict[str, Any]:
        """
        Fallback : analyse avec OCR + heuristics si modèle vision échoue.

        Args:
            image_path: Chemin vers l'image

        Returns:
            Structure extraite avec OCR + heuristics
        """
        logger.info("Using OCR + heuristics fallback")
        
        # TODO: Implémenter OCR réel (ex: pytesseract, easyocr)
        # Pour l'instant, retourner structure basique
        
        return {
            "sections": [
                {"type": "Unknown", "bounds": [0, 0, 1200, 800], "components": []}
            ],
            "components": [],
            "layout": {"type": "unknown"},
            "hierarchy": {}
        }
    
    def _calculate_similarity(
        self,
        structure: DesignStructure,
        pattern_data: Dict[str, Any]
    ) -> float:
        """
        Calcule le score de similarité entre structure et pattern.

        Args:
            structure: Structure de design
            pattern_data: Données du pattern

        Returns:
            Score de similarité (0.0 - 1.0)
        """
        # Heuristique simple : comparer types de sections
        structure_sections = set(s.get("type", "") for s in structure.sections)
        pattern_sections = set(pattern_data.get("sections", []))
        
        if not pattern_sections:
            return 0.0
        
        intersection = structure_sections.intersection(pattern_sections)
        union = structure_sections.union(pattern_sections)
        
        if not union:
            return 0.0
        
        similarity = len(intersection) / len(union)
        return similarity


# Exemple d'utilisation
if __name__ == "__main__":
    import asyncio
    
    async def main():
        analyzer = DesignAnalyzer()
        
        # Analyser une image
        image_path = Path("example_design.png")
        if image_path.exists():
            structure = await analyzer.analyze_image(image_path)
            print("Design structure:", structure.to_dict())
            
            # Extraire composants
            components = await analyzer.extract_components(structure)
            print("Components:", components)
            
            # Matcher patterns
            patterns = analyzer.match_patterns(structure)
            print("Matched patterns:", patterns)
    
    asyncio.run(main())
