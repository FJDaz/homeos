"""DesignerMode - Point d'entrée Mode DESIGNER avec workflow upload → analyse → génération 'Miroir'."""
from typing import Dict, Optional, Any, List
from pathlib import Path
import tempfile
import shutil
from loguru import logger

from ..analyzer.design_analyzer import DesignAnalyzer, DesignStructure
from ..analyzer.ui_inference_engine import UIInferenceEngine
from ...models.agent_router import AgentRouter
from ..knowledge.knowledge_base import KnowledgeBase


class DesignerMode:
    """
    Mode DESIGNER de Sullivan - Workflow "Génération Miroir".
    
    Workflow complet :
    1. Upload design (PNG/JPG/SVG, Figma/Sketch en TODO)
    2. Analyser structure avec DesignAnalyzer (modèle vision Gemini 3 Flash)
    3. Vérifier patterns dans KnowledgeBase
    4. Proposer pattern éprouvé si disponible
    5. Générer composants avec génération 'Miroir' (mapper dessins sur structure logique)
       Intention → Corps → Organes → Molécules → Atomes
    """
    
    SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg"}
    # TODO: Support Figma (.fig) et Sketch (.sketch)
    
    def __init__(
        self,
        design_path: Optional[Path] = None,
        output_path: Optional[Path] = None,
        non_interactive: bool = False,
        output_html: bool = False,
        output_html_path: Optional[Path] = None,
        extract_principles: bool = False,
        principles_path: Optional[Path] = None,
    ):
        """
        Initialise DesignerMode.

        Args:
            design_path: Chemin vers le fichier design (optionnel, peut être fourni plus tard)
            output_path: Chemin de sortie pour les composants générés (optionnel)
            non_interactive: Si True, désactive les confirmations interactives
            output_html: Si True, génère un fichier HTML single-file après le Miroir
            output_html_path: Chemin du fichier HTML (défaut: output/studio/studio_index.html)
            extract_principles: Si True, extrait les principes graphiques (couleurs, typo, etc.) après analyse
            principles_path: Chemin de sortie pour design_principles.json (défaut: output/studio/design_principles.json)
        """
        self.design_path = Path(design_path) if design_path else None
        self.output_path = Path(output_path) if output_path else None
        self.non_interactive = non_interactive
        self.output_html = output_html
        self.output_html_path = Path(output_html_path) if output_html_path else None
        self.extract_principles = extract_principles
        self.principles_path = Path(principles_path) if principles_path else None
        
        # Initialiser les composants
        self.agent_router = AgentRouter(execution_mode="BUILD")
        self.knowledge_base = KnowledgeBase()
        self.design_analyzer = DesignAnalyzer(
            agent_router=self.agent_router,
            knowledge_base=self.knowledge_base
        )
        self.ui_inference_engine = UIInferenceEngine(
            agent_router=self.agent_router,
            knowledge_base=self.knowledge_base
        )
        
        logger.info("DesignerMode initialized")
    
    async def run(self, design_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Exécute le workflow complet "Génération Miroir".

        Args:
            design_path: Chemin vers le fichier design (si non fourni dans __init__)

        Returns:
            Résultats du workflow avec structure design, patterns matchés, structure frontend
        """
        logger.info("Starting DesignerMode workflow 'Génération Miroir'")
        
        # Utiliser design_path fourni ou celui de __init__
        design_file = Path(design_path) if design_path else self.design_path
        
        if not design_file or not design_file.exists():
            return {
                "success": False,
                "message": f"Design file not found: {design_file}",
                "design_structure": None,
                "matched_patterns": None,
                "frontend_structure": None
            }
        
        # Vérifier extension supportée
        if design_file.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            return {
                "success": False,
                "message": f"Unsupported file type: {design_file.suffix}. Supported: {self.SUPPORTED_EXTENSIONS}",
                "design_structure": None,
                "matched_patterns": None,
                "frontend_structure": None
            }
        
        try:
            # Étape 1 : Analyser structure avec DesignAnalyzer (version rapide avec cache)
            logger.info("Step 1: Analyzing design structure with DesignAnalyzerFast")
            from ..analyzer.design_analyzer_fast import DesignAnalyzerFast
            
            fast_analyzer = DesignAnalyzerFast(
                design_analyzer=self.design_analyzer,
                timeout_seconds=60,  # Timeout 60s pour analyses complexes
            )
            design_structure = await fast_analyzer.analyze_image(design_file)
            
            # Optionnel : extraire principes graphiques (phase 2 Sullivan)
            principles = None
            if self.extract_principles:
                from ...config.settings import settings
                from ...models.gemini_client import GeminiClient
                from ..analyzer.design_principles_extractor import DesignPrinciplesExtractor
                logger.info("Extracting design principles (Gemini Vision)")
                gemini_client = GeminiClient(execution_mode="BUILD")
                extractor = DesignPrinciplesExtractor(self.agent_router, gemini_client)
                principles = await extractor.extract_principles(design_file, design_structure.to_dict())
                principles_path = self.principles_path or (settings.output_dir / "studio" / "design_principles.json")
                extractor.save_principles(principles, principles_path)
                logger.info(f"Design principles saved: {principles_path}")
            
            # Étape 2 : Extraire composants
            logger.info("Step 2: Extracting components from design structure")
            components = await self.design_analyzer.extract_components(design_structure)
            
            # Étape 3 : Vérifier patterns dans KnowledgeBase
            logger.info("Step 3: Matching patterns in KnowledgeBase")
            matched_patterns = self.design_analyzer.match_patterns(design_structure)
            
            # Étape 4 : Proposer pattern éprouvé si disponible
            proposed_pattern = None
            if matched_patterns:
                # Prendre le pattern avec le meilleur score de similarité
                proposed_pattern = max(matched_patterns, key=lambda p: p.get("similarity_score", 0))
                logger.info(f"Proposed pattern: {proposed_pattern.get('pattern_name')} (similarity: {proposed_pattern.get('similarity_score', 0):.2f})")
            
            # Étape 5 : Génération 'Miroir' - mapper dessins sur structure logique
            logger.info("Step 5: Performing 'Miroir' generation - mapping design to logical structure")
            frontend_structure = await self._mirror_generation(design_structure, components)
            
            # Optionnel : générer HTML single-file (page vierge + webographie)
            if self.output_html:
                from ..generator.design_to_html import _load_webography, generate_html_from_design
                from ...config.settings import settings
                webography_text = _load_webography()
                html_path = self.output_html_path or (settings.output_dir / "studio" / "studio_index.html")
                await generate_html_from_design(
                    design_structure.to_dict(),
                    frontend_structure,
                    design_file,
                    webography_text,
                    html_path,
                )
                logger.info(f"HTML generated: {html_path}")
            
            # Sauvegarder résultats si output_path spécifié
            if self.output_path:
                self.output_path.mkdir(parents=True, exist_ok=True)
                result_file = self.output_path / "sullivan_designer_result.json"
                import json
                with open(result_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "design_structure": design_structure.to_dict(),
                        "matched_patterns": matched_patterns,
                        "proposed_pattern": proposed_pattern,
                        "frontend_structure": frontend_structure
                    }, f, indent=2)
                logger.info(f"Results saved to {result_file}")
            
            return {
                "success": True,
                "design_structure": design_structure.to_dict(),
                "design_principles": principles if self.extract_principles else None,
                "matched_patterns": matched_patterns,
                "proposed_pattern": proposed_pattern,
                "frontend_structure": frontend_structure,
                "message": "DesignerMode workflow 'Génération Miroir' completed successfully"
            }
            
        except Exception as e:
            logger.error(f"DesignerMode workflow failed: {e}", exc_info=True)
            return {
                "success": False,
                "design_structure": None,
                "matched_patterns": None,
                "frontend_structure": None,
                "message": f"Error: {str(e)}"
            }
    
    async def _mirror_generation(
        self,
        design_structure: DesignStructure,
        components: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Génération 'Miroir' : mapper les dessins sur la structure logique.
        
        Intention → Corps → Organes → Molécules → Atomes

        Args:
            design_structure: Structure de design extraite
            components: Composants extraits

        Returns:
            Structure frontend mappée selon hiérarchie logique
        """
        logger.info("Mapping design to logical structure (Intention → Corps → Organes → Molécules → Atomes)")
        
        # Créer une fonction globale simulée depuis la structure de design
        # En production, cela serait inféré depuis le backend analysé
        from ..analyzer.backend_analyzer import GlobalFunction
        
        # Inférer type de produit depuis les sections détectées
        product_type = self._infer_product_type_from_sections(design_structure.sections)
        
        global_function = GlobalFunction(
            product_type=product_type,
            actors=["user"],  # Par défaut
            business_flows=["View", "Interact"],
            use_cases=["Browse", "Interact"]
        )
        
        # Utiliser UIInferenceEngine pour inférer structure logique
        intention_structure = self.ui_inference_engine.propose_intention_structure(global_function)
        
        # Mapper les sections du design sur les Corps (Niveau 1)
        frontend_structure = {}
        confirmed_steps = intention_structure.get("proposed_steps", [])
        
        for step in confirmed_steps:
            # Inférer Corps depuis l'étape
            corps = self.ui_inference_engine.infer_corps_from_step(step, global_function)
            frontend_structure[step] = {}
            
            # Mapper sections du design sur les Corps
            for corps_item in corps:
                corps_type = corps_item.get("type")
                
                # Trouver section correspondante dans le design
                matching_section = self._find_matching_section(corps_type, design_structure.sections)
                
                if matching_section:
                    # Inférer Organes depuis Corps
                    organes = self.ui_inference_engine.infer_organes_from_corps(corps_item)
                    frontend_structure[step][corps_type] = {
                        "design_section": matching_section,
                        "organes": {}
                    }
                    
                    # Inférer Molécules depuis Organes
                    for organe in organes:
                        molecules = self.ui_inference_engine.infer_molecules_from_organe(organe)
                        frontend_structure[step][corps_type]["organes"][organe.get("type")] = {
                            "molecules": {}
                        }
                        
                        # Inférer Atomes depuis Molécules
                        for molecule in molecules:
                            atoms = self.ui_inference_engine.infer_atoms_from_molecule(molecule)
                            frontend_structure[step][corps_type]["organes"][organe.get("type")]["molecules"][molecule.get("type")] = {
                                "atoms": atoms
                            }
        
        logger.info("Miroir generation completed - design mapped to logical structure")
        return frontend_structure
    
    def _infer_product_type_from_sections(self, sections: List[Dict[str, Any]]) -> str:
        """
        Infère le type de produit depuis les sections détectées.

        Args:
            sections: Sections détectées dans le design

        Returns:
            Type de produit (e-commerce, SaaS, dashboard, etc.)
        """
        section_types = [s.get("type", "").lower() for s in sections]
        
        # Heuristiques simples
        if "hero" in section_types and "cta" in section_types:
            return "landing_page"
        elif "dashboard" in section_types or "chart" in section_types:
            return "dashboard"
        elif "product" in section_types or "cart" in section_types:
            return "e-commerce"
        else:
            return "web_app"
    
    def _find_matching_section(
        self,
        corps_type: str,
        design_sections: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Trouve la section du design correspondant au type de Corps.

        Args:
            corps_type: Type de Corps (social_proof, performance_dashboard, etc.)
            design_sections: Sections détectées dans le design

        Returns:
            Section correspondante ou None
        """
        # Mapping heuristique
        type_mapping = {
            "social_proof": ["testimonials", "reviews", "stats"],
            "performance_dashboard": ["dashboard", "metrics", "charts"],
            "cta": ["cta", "call-to-action", "button"],
            "pricing": ["pricing", "plans", "subscription"]
        }
        
        keywords = type_mapping.get(corps_type, [corps_type])
        
        for section in design_sections:
            section_type = section.get("type", "").lower()
            if any(keyword in section_type for keyword in keywords):
                return section
        
        # Retourner première section si aucune correspondance
        return design_sections[0] if design_sections else None