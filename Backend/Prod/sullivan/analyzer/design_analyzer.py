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


import asyncio
import json
from typing import Dict, Optional
from pathlib import Path
import logging

class DesignPrinciplesExtractor:
    """
    A class used to extract design principles from an image.

    Attributes:
    ----------
    agent_router : AgentRouter
        The agent router used to select the agent.
    gemini_client : GeminiClient
        The Gemini client used to generate design principles.

    Methods:
    -------
    extract_principles(image_path: Path, design_structure: Optional[Dict] = None) -> Dict:
        Extracts design principles from an image.
    save_principles(principles: Dict, output_path: Path) -> None:
        Saves the design principles to a JSON file.
    """

    def __init__(self, agent_router: 'AgentRouter', gemini_client: 'GeminiClient'):
        """
        Initializes the DesignPrinciplesExtractor.

        Args:
        ----
        agent_router : AgentRouter
            The agent router used to select the agent.
        gemini_client : GeminiClient
            The Gemini client used to generate design principles.
        """
        self.agent_router = agent_router
        self.gemini_client = gemini_client

    async def extract_principles(self, image_path: Path, design_structure: Optional[Dict] = None) -> Dict:
        """
        Extracts design principles from an image.

        Args:
        ----
        image_path : Path
            The path to the image.
        design_structure : Optional[Dict]
            The design structure. Defaults to None.

        Returns:
        -------
        Dict
            A dictionary containing the design principles.
        """
        try:
            # Generate the prompt
            prompt = f"À partir de cette maquette (et optionnellement de la structure design fournie), liste les principes graphiques réutilisables."
            if design_structure:
                prompt += f" Structure design: {json.dumps(design_structure)}"

            # Generate the design principles using Gemini Vision
            response = await self.gemini_client.generate_with_image(image_path, prompt)

            # Parse the response to extract the JSON
            json_response = self._parse_json_response(response)

            return json_response

        except Exception as e:
            logging.error(f"Error extracting design principles: {e}")
            raise

    def _parse_json_response(self, response: str) -> Dict:
        """
        Parses the response to extract the JSON.

        Args:
        ----
        response : str
            The response from Gemini Vision.

        Returns:
        -------
        Dict
            A dictionary containing the design principles.
        """
        try:
            # Remove markdown code block if present
            response = response.strip("

from fastapi import UploadFile, File
from typing import Optional
from PIL import Image
import io
import logging
from agent_router import AgentRouter
from task import Task
from knowledge_base import KnowledgeBase
from vision_model import VisionModel

class DesignAnalyzer:
    """
    Analyzes designs (PNG/JPG/SVG) using the Gemini 3 Flash vision model via AgentRouter.
    """
    
    def __init__(self, agent_router: AgentRouter, knowledge_base: KnowledgeBase):
        """
        Initializes the DesignAnalyzer with an AgentRouter and a KnowledgeBase.
        
        Args:
        - agent_router (AgentRouter): The AgentRouter instance for selecting the vision model.
        - knowledge_base (KnowledgeBase): The KnowledgeBase instance for comparing patterns.
        """
        self.agent_router = agent_router
        self.knowledge_base = knowledge_base

    async def analyze_image(self, image_file: UploadFile = File(...)) -> dict:
        """
        Analyzes the provided image file using the Gemini 3 Flash vision model.
        
        Args:
        - image_file (UploadFile): The image file to analyze.
        
        Returns:
        - dict: A dictionary containing the extracted structure and matched patterns.
        """
        try:
            # Read the image file
            image = Image.open(io.BytesIO(image_file.file.read()))
            
            # Create a Task instance for the AgentRouter
            task = Task(type="image_analysis", complexity=0.5, size_in_tokens=1000)
            
            # Select the vision model using the AgentRouter
            agent = self.agent_router.select_agent(task)
            
            # Use the selected vision model to analyze the image
            vision_model = VisionModel(agent)
            structure = vision_model.analyze_image(image)
            
            # Extract components from the structure
            components = self.extract_components(structure)
            
            # Match patterns with the KnowledgeBase
            matched_patterns = self.match_patterns(structure)
            
            return {
                "structure": structure,
                "components": components,
                "matched_patterns": matched_patterns
            }
        
        except Exception as e:
            logging.error(f"Error analyzing image: {e}")
            return {"error": str(e)}

    def extract_components(self, structure: dict) -> dict:
        """
        Extracts components (sections, buttons, forms, cards) from the structure.
        
        Args:
        - structure (dict): The structure dictionary containing the visual elements.
        
        Returns:
        - dict: A dictionary containing the extracted components.
        """
        components = {
            "sections": [],
            "buttons": [],
            "forms": [],
            "cards": []
        }
        
        # Iterate through the structure and extract components
        for element in structure["elements"]:
            if element["type"] == "section":
                components["sections"].append(element)
            elif element["type"] == "button":
                components["buttons"].append(element)
            elif element["type"] == "form":
                components["forms"].append(element)
            elif element["type"] == "card":
                components["cards"].append(element)
        
        return components

    def match_patterns(self, structure: dict) -> list:
        """
        Matches the structure with patterns in the KnowledgeBase.
        
        Args:
        - structure (dict): The structure dictionary containing the visual elements.
        
        Returns:
        - list: A list of matched patterns.
        """
        matched_patterns = []
        
        # Iterate through the KnowledgeBase patterns and match with the structure
        for pattern in self.knowledge_base.patterns:
            if self.knowledge_base.match_pattern(structure, pattern):
                matched_patterns.append(pattern)
        
        return matched_patterns

    async def fallback_analyze_image(self, image_file: UploadFile = File(...)) -> dict:
        """
        Fallback analysis using OCR and heuristics if the primary vision model fails.
        
        Args:
        - image_file (UploadFile): The image file to analyze.
        
        Returns:
        - dict: A dictionary containing the extracted structure and matched patterns.
        """
        try:
            # Read the image file
            image = Image.open(io.BytesIO(image_file.file.read()))
            
            # Perform OCR on the image
            ocr_text = self.perform_ocr(image)
            
            # Extract structure using heuristics
            structure = self.extract_structure_using_heuristics(ocr_text)
            
            # Extract components from the structure
            components = self.extract_components(structure)
            
            # Match patterns with the KnowledgeBase
            matched_patterns = self.match_patterns(structure)
            
            return {
                "structure": structure,
                "components": components,
                "matched_patterns": matched_patterns
            }
        
        except Exception as e:
            logging.error(f"Error analyzing image (fallback): {e}")
            return {"error": str(e)}

    def perform_ocr(self, image: Image) -> str:
        """
        Performs OCR on the provided image.
        
        Args:
        - image (Image): The image to perform OCR on.
        
        Returns:
        - str: The extracted text from the image.
        """
        # Implement OCR logic here
        pass

    def extract_structure_using_heuristics(self, ocr_text: str) -> dict:
        """
        Extracts structure using heuristics from the OCR text.
        
        Args:
        - ocr_text (str): The OCR text to extract structure from.
        
        Returns:
        - dict: A dictionary containing the extracted structure.
        """
        # Implement heuristics logic here
        pass

from fastapi import UploadFile, File
from typing import Optional
from PIL import Image
import io
import logging
from design_analyzer import DesignAnalyzer
from knowledge_base import KnowledgeBase
from ui_inference_engine import UIInferenceEngine
from typing import Dict, List

class DesignerMode:
    """
    DesignerMode class for designing and analyzing user interfaces.
    """
    
    def __init__(self, design_analyzer: DesignAnalyzer, knowledge_base: KnowledgeBase, ui_inference_engine: UIInferenceEngine):
        """
        Initializes the DesignerMode with a DesignAnalyzer, KnowledgeBase, and UIInferenceEngine.
        
        Args:
        - design_analyzer (DesignAnalyzer): The DesignAnalyzer instance for analyzing designs.
        - knowledge_base (KnowledgeBase): The KnowledgeBase instance for matching patterns.
        - ui_inference_engine (UIInferenceEngine): The UIInferenceEngine instance for mapping structures.
        """
        self.design_analyzer = design_analyzer
        self.knowledge_base = knowledge_base
        self.ui_inference_engine = ui_inference_engine

    async def upload_and_analyze_design(self, design_file: UploadFile = File(...)) -> Dict:
        """
        Uploads and analyzes a design file using the DesignAnalyzer.
        
        Args:
        - design_file (UploadFile): The design file to upload and analyze.
        
        Returns:
        - Dict: A dictionary containing the analysis results.
        """
        try:
            # Analyze the design file using the DesignAnalyzer
            analysis_results = await self.design_analyzer.analyze_image(design_file)
            
            # Match patterns with the KnowledgeBase
            matched_patterns = self.knowledge_base.match_patterns(analysis_results["structure"])
            
            # Map the structure using the UIInferenceEngine
            mapped_structure = self.ui_inference_engine.map_structure(analysis_results["structure"])
            
            return {
                "analysis_results": analysis_results,
                "matched_patterns": matched_patterns,
                "mapped_structure": mapped_structure
            }
        
        except Exception as e:
            logging.error(f"Error uploading and analyzing design: {e}")
            return {"error": str(e)}

    def propose_pattern(self, matched_patterns: List[Dict]) -> Optional[Dict]:
        """
        Proposes a pattern from the matched patterns.
        
        Args:
        - matched_patterns (List[Dict]): The list of matched patterns.
        
        Returns:
        - Optional[Dict]: The proposed pattern or None if no patterns are matched.
        """
        if matched_patterns:
            return matched_patterns[0]
        else:
            return None

    def generate_components(self, mapped_structure: Dict) -> Dict:
        """
        Generates components from the mapped structure using the 'Miroir' approach.
        
        Args:
        - mapped_structure (Dict): The mapped structure to generate components from.
        
        Returns:
        - Dict: A dictionary containing the generated components.
        """
        components = {
            "sections": [],
            "buttons": [],
            "forms": [],
            "cards": []
        }
        
        # Iterate through the mapped structure and generate components
        for element in mapped_structure["elements"]:
            if element["type"] == "section":
                components["sections"].append(element)
            elif element["type"] == "button":
                components["buttons"].append(element)
            elif element["type"] == "form":
                components["forms"].append(element)
            elif element["type"] == "card":
                components["cards"].append(element)
        
        return components

# Example usage
design_analyzer = DesignAnalyzer(AgentRouter(), KnowledgeBase())
knowledge_base = KnowledgeBase()
ui_inference_engine = UIInferenceEngine()
designer_mode = DesignerMode(design_analyzer, knowledge_base, ui_inference_engine)

# Upload and analyze a design file
design_file = UploadFile(filename="design.png", file=io.BytesIO(open("design.png", "rb").read()))
analysis_results = designer_mode.upload_and_analyze_design(design_file)

# Propose a pattern
matched_patterns = analysis_results["matched_patterns"]
proposed_pattern = designer_mode.propose_pattern(matched_patterns)

# Generate components
mapped_structure = analysis_results["mapped_structure"]
components = designer_mode.generate_components(mapped_structure)

print("Analysis Results:", analysis_results)
print("Proposed Pattern:", proposed_pattern)
print("Generated Components:", components)