"""DevMode - Point d'entrée Mode DEV avec workflow 'Collaboration Heureuse'."""
from typing import Dict, Optional, Any, List
from pathlib import Path
import json
from loguru import logger

from ..analyzer.backend_analyzer import BackendAnalyzer, GlobalFunction
from ..analyzer.ui_inference_engine import UIInferenceEngine
from ...models.agent_router import AgentRouter
from ..knowledge.knowledge_base import KnowledgeBase


class DevMode:
    """
    Mode DEV de Sullivan - Workflow "Collaboration Heureuse".
    
    Workflow complet :
    1. Dialogue Stratégique : accord sur N étapes parcours (inférence IA basée JTBD)
    2. Maillage des Corps : définition zones contenu pour chaque étape
    3. Inférence Technique : AETHERFLOW déroule cascade Organes → Molécules → Atomes
    4. HCI Mentor : surveillance charge cognitive, propose ventilation vers étape N+1 si saturation
    5. Génération 'Miroir' optionnelle : si design PNG fourni, mapper dessins sur structure logique
    """
    
    def __init__(
        self,
        backend_path: Path,
        output_path: Optional[Path] = None,
        analyze_only: bool = False,
        non_interactive: bool = False
    ):
        """
        Initialise DevMode.

        Args:
            backend_path: Chemin vers le backend à analyser
            output_path: Chemin de sortie pour le frontend généré (optionnel)
            analyze_only: Si True, affiche seulement le rapport de fonction globale
            non_interactive: Si True, désactive les confirmations interactives
        """
        self.backend_path = Path(backend_path)
        self.output_path = Path(output_path) if output_path else None
        self.analyze_only = analyze_only
        self.non_interactive = non_interactive
        
        # Initialiser les composants
        self.agent_router = AgentRouter(execution_mode="BUILD")
        self.knowledge_base = KnowledgeBase()
        self.backend_analyzer = BackendAnalyzer(self.backend_path)
        self.ui_inference_engine = UIInferenceEngine(
            agent_router=self.agent_router,
            knowledge_base=self.knowledge_base
        )
        
        logger.info(f"DevMode initialized for backend: {self.backend_path}")
    
    async def run(self) -> Dict[str, Any]:
        """
        Exécute le workflow complet "Collaboration Heureuse".

        Returns:
            Résultats du workflow avec global_function, ui_intent, frontend_structure
        """
        logger.info("Starting DevMode workflow 'Collaboration Heureuse'")
        
        try:
            # Étape 1 : Analyser le backend
            logger.info("Step 1: Analyzing backend structure")
            global_function = self.backend_analyzer.analyze_project_structure()
            
            if self.analyze_only:
                return {
                    "success": True,
                    "global_function": global_function.to_dict(),
                    "ui_intent": None,
                    "frontend_structure": None,
                    "message": "Analysis completed (analyze-only mode)"
                }
            
            # Étape 2 : Dialogue Stratégique (Niveau 0 - Intention Suprême)
            logger.info("Step 2: Strategic dialogue - proposing intention structure")
            intention_structure = self.ui_inference_engine.propose_intention_structure(global_function)
            
            if not self.non_interactive:
                # Demander confirmation (simulé pour l'instant)
                logger.info(f"Proposed steps: {intention_structure.get('proposed_steps', [])}")
                logger.info("(In interactive mode, user would confirm here)")
            
            # Étape 3 : Maillage des Corps (Niveau 1)
            logger.info("Step 3: Content area mapping (Corps)")
            confirmed_steps = intention_structure.get("proposed_steps", [])
            corps_mapping = {}
            
            for step in confirmed_steps:
                corps = self.ui_inference_engine.infer_corps_from_step(step, global_function)
                corps_mapping[step] = corps
                
                # Vérifier charge cognitive
                if self.ui_inference_engine.check_cognitive_load(step):
                    logger.warning(f"Cognitive load high for step '{step}', suggesting ventilation")
            
            # Étape 4 : Inférence Technique (Niveau 2-3)
            logger.info("Step 4: Technical inference (Organes → Molécules → Atomes)")
            frontend_structure = {}
            
            for step, corps_list in corps_mapping.items():
                frontend_structure[step] = {}
                for corps in corps_list:
                    organes = self.ui_inference_engine.infer_organes_from_corps(corps)
                    frontend_structure[step][corps.get("type")] = {}
                    
                    for organe in organes:
                        molecules = self.ui_inference_engine.infer_molecules_from_organe(organe)
                        frontend_structure[step][corps.get("type")][organe.get("type")] = {}
                        
                        for molecule in molecules:
                            atoms = self.ui_inference_engine.infer_atoms_from_molecule(molecule)
                            frontend_structure[step][corps.get("type")][organe.get("type")][molecule.get("type")] = atoms
            
            # Étape 5 : HCI Mentor (surveillance charge cognitive)
            logger.info("Step 5: HCI Mentor - monitoring cognitive load")
            cognitive_load_ok = True
            for step in confirmed_steps:
                if self.ui_inference_engine.check_cognitive_load(step):
                    cognitive_load_ok = False
                    logger.warning(f"HCI Mentor: High cognitive load detected for '{step}'")
            
            # Étape 6 : Génération 'Miroir' (optionnelle, si design fourni)
            # TODO: Implémenter avec Gemini 3 Flash + fallback
            
            # Sauvegarder résultats si output_path spécifié
            if self.output_path:
                self.output_path.mkdir(parents=True, exist_ok=True)
                result_file = self.output_path / "sullivan_result.json"
                with open(result_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "global_function": global_function.to_dict(),
                        "intention_structure": intention_structure,
                        "frontend_structure": frontend_structure
                    }, f, indent=2)
                logger.info(f"Results saved to {result_file}")
            
            return {
                "success": True,
                "global_function": global_function.to_dict(),
                "ui_intent": intention_structure,
                "frontend_structure": frontend_structure,
                "message": "Workflow 'Collaboration Heureuse' completed successfully"
            }
            
        except Exception as e:
            logger.error(f"DevMode workflow failed: {e}", exc_info=True)
            return {
                "success": False,
                "global_function": None,
                "ui_intent": None,
                "frontend_structure": None,
                "message": f"Error: {str(e)}"
            }