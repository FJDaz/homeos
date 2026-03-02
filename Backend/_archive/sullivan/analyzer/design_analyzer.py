"""DesignAnalyzer - Analyse designs avec modèle vision pour extraction structure."""
import json
import re
from typing import List, Dict, Optional, Any, Tuple
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

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DesignStructure":
        """Crée une instance depuis un dictionnaire."""
        return cls(
            sections=data.get("sections", []),
            components=data.get("components", []),
            layout=data.get("layout", {}),
            hierarchy=data.get("hierarchy", {}),
        )


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
        
        # Pré-traiter l'image pour Gemini (resize/compress si trop grosse)
        image_data, mime_type = self._load_image_for_vision(image_path)
        
        # Analyser avec modèle vision via AgentRouter
        # Utiliser Gemini 3 Flash (prioritaire) avec fallback automatique
        try:
            structure_dict = await self._analyze_with_vision_model(
                image_data, image_path, mime_type
            )
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

    def _load_image_for_vision(self, image_path: Path) -> Tuple[bytes, str]:
        """
        Charge et pré-traite l'image pour Gemini Vision.
        Resize/compress si trop grosse (limite inline ~20MB).
        """
        try:
            from ..upload import preprocess_for_gemini
            return preprocess_for_gemini(image_path)
        except ImportError:
            data = self._read_image(image_path)
            mime = "image/png" if image_path.suffix.lower() == ".png" else "image/jpeg"
            return data, mime

    async def _analyze_with_vision_model(
        self,
        image_data: bytes,
        image_path: Path,
        mime_type: str = "image/png",
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
        
        # Prompt optimisé pour JSON valide (Anchor Tagging technique)
        # Limite les sections/composants pour éviter JSON trop long qui se tronque
        prompt = """{
"task": "Analyze this UI design image",
"instructions": [
  "Identify main sections (Header, Sidebar, Content, Footer, etc.)",
  "Detect components (buttons, inputs, cards, tabs, labels)",
  "Extract layout type and visual hierarchy",
  "Output MUST be valid JSON - start with { and end with }",
  "LIMIT: Max 5 sections, max 15 components total"
],
"output_schema": {
  "sections": [{"type": "string", "bounds": [0,0,100,100], "components": []}],
  "components": [{"type": "string", "text": "string", "bounds": [0,0,100,100], "style": {}}],
  "layout": {"type": "string", "columns": 1},
  "hierarchy": {"primary": [], "secondary": [], "tertiary": []}
}
}

CRITICAL: Your response MUST start with { and end with }. No markdown, no explanation, no text outside JSON.
Return the analysis as a single valid JSON object:"""
        
        # Appel réel à Gemini Vision
        gemini = getattr(self.agent_router, "_clients", {}).get("gemini")
        if not gemini:
            from ...models.gemini_client import GeminiClient
            gemini = GeminiClient(execution_mode="BUILD")
        
        logger.info("Calling vision model via Gemini (generate_with_image)")
        result = await gemini.generate_with_image(
            prompt,
            image_base64,
            mime_type=mime_type,
            output_constraint="JSON only",
            max_tokens=8192,
        )
        
        if not result.success:
            raise RuntimeError(result.error or "Gemini vision call failed")
        
        # Parser la réponse JSON (robuste aux erreurs Gemini)
        text = (result.code or "").strip()
        if "```" in text:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
            if match:
                text = match.group(1).strip()
        start = text.find("{")
        if start >= 0:
            text = text[start:]

        # Nettoyer le JSON avant parsing (trailing commas, etc.)
        text = self._clean_json(text)

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            # Log le JSON problématique pour debug
            logger.error(f"JSON parse error: {e}")
            logger.debug(f"Problematic JSON (first 2000 chars): {text[:2000]}")

            # Tentative de réparation plus agressive
            text = self._repair_json_aggressive(text)
            try:
                return json.loads(text)
            except json.JSONDecodeError as e2:
                logger.error(f"JSON repair failed: {e2}")
                raise

    def _clean_json(self, text: str) -> str:
        """Nettoie le JSON malformé retourné par Gemini."""
        # Supprimer les trailing commas avant ] ou }
        text = re.sub(r',\s*([\]}])', r'\1', text)
        # Supprimer les commentaires // ...
        text = re.sub(r'//[^\n]*', '', text)
        # Ajouter virgules manquantes entre } et { (objets adjacents dans array)
        text = re.sub(r'\}\s*\{', '},{', text)
        # Ajouter virgules manquantes entre ] et [ (arrays adjacents)
        text = re.sub(r'\]\s*\[', '],[', text)
        # Ajouter virgules manquantes entre } et " (fin objet, début clé)
        text = re.sub(r'\}\s*"', '},"', text)
        # Ajouter virgules manquantes entre ] et " (fin array, début clé)
        text = re.sub(r'\]\s*"', '],"', text)
        # Ajouter virgules manquantes entre valeur et " (ex: 100 "next_key")
        text = re.sub(r'(\d)\s+"', r'\1,"', text)
        # Ajouter virgules manquantes entre true/false/null et "
        text = re.sub(r'(true|false|null)\s+"', r'\1,"', text)
        # Ajouter virgules manquantes entre " et " (fin string, début clé)
        # Attention: ne pas matcher les strings internes
        text = re.sub(r'"\s*\n\s*"', '",\n"', text)
        # Tronquer au dernier } valide (Gemini peut ajouter du texte après)
        last_brace = text.rfind('}')
        if last_brace >= 0:
            text = text[:last_brace + 1]
        return text

    def _repair_json_aggressive(self, text: str) -> str:
        """
        Réparation agressive du JSON malformé.
        Utilisé en dernier recours si _clean_json échoue.
        """
        # Remplacer les single quotes par double quotes (erreur fréquente)
        # Attention: ne pas remplacer dans les strings
        text = re.sub(r"(?<=[{,\[])\s*'([^']+)'\s*:", r'"\1":', text)
        text = re.sub(r":\s*'([^']*)'(?=[,}\]])", r':"\1"', text)

        # Gérer les clés sans quotes
        text = re.sub(r'(?<=[{,])\s*(\w+)\s*:', r'"\1":', text)

        # Supprimer les virgules en fin de liste/objet (re-check)
        text = re.sub(r',(\s*[}\]])', r'\1', text)

        # Équilibrer les accolades et crochets
        open_braces = text.count('{')
        close_braces = text.count('}')
        open_brackets = text.count('[')
        close_brackets = text.count(']')

        # Ajouter les accolades/crochets manquants à la fin
        text += '}' * (open_braces - close_braces)
        text += ']' * (open_brackets - close_brackets)

        # Supprimer les accolades/crochets en trop à la fin
        while text.endswith('}}') and close_braces > open_braces:
            text = text[:-1]
            close_braces -= 1
        while text.endswith(']]') and close_brackets > open_brackets:
            text = text[:-1]
            close_brackets -= 1

        return text

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
