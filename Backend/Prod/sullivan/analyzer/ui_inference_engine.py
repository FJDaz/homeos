"""UIInferenceEngine - Inférence UI depuis fonction globale avec approche top-down."""
from typing import List, Dict, Optional, Any
from pathlib import Path
from loguru import logger

from ...models.agent_router import AgentRouter
from ..knowledge.knowledge_base import KnowledgeBase
from .backend_analyzer import GlobalFunction


class UIInferenceEngine:
    """
    Moteur d'inférence UI avec approche TOP-DOWN (déduction descendante).
    
    Niveau 0 (Intention Suprême) → propose structure basée sur state-of-the-art et JTBD
    Niveau 1 (Corps/Séquences) → définit zones contenu pour chaque étape confirmée
    Niveau 2 (Organes & Molécules) → déduit Organes depuis Corps, puis Molécules depuis Organes
    Niveau 3 (Atomes) → déduit Atomes depuis Molécules
    
    Mécanisme "Stop du Mentor" pour éviter complexité prématurée.
    HCI Mentor pour surveillance charge cognitive.
    """
    
    def __init__(
        self,
        agent_router: Optional[AgentRouter] = None,
        knowledge_base: Optional[KnowledgeBase] = None,
        intent_translator: Optional[object] = None
    ):
        """
        Initialise le moteur d'inférence UI.

        Args:
            agent_router: Router pour sélection modèle LLM (optionnel, créé si None)
            knowledge_base: Base de connaissances pour patterns (optionnel, créé si None)
            intent_translator: Instance IntentTranslator pour système STAR (optionnel)
        """
        self.agent_router = agent_router or AgentRouter(execution_mode="BUILD")
        # KnowledgeBase peut être créé sans paramètres (utilise chemins par défaut)
        self.knowledge_base = knowledge_base or KnowledgeBase()
        
        # IntentTranslator pour système STAR (optionnel, créé si None)
        if intent_translator is None:
            try:
                from ..intent_translator import IntentTranslator
                self.intent_translator = IntentTranslator()
                logger.info("UIInferenceEngine initialized with STAR (IntentTranslator)")
            except Exception as e:
                logger.warning(f"Failed to initialize IntentTranslator: {e}. STAR features disabled.")
                self.intent_translator = None
        else:
            self.intent_translator = intent_translator
            logger.info("UIInferenceEngine initialized with STAR (IntentTranslator provided)")
        
        if self.intent_translator is None:
            logger.info("UIInferenceEngine initialized with top-down approach")
    
    def propose_intention_structure(
        self,
        global_function: GlobalFunction
    ) -> Dict[str, Any]:
        """
        Niveau 0 : Propose structure d'intention basée sur state-of-the-art et JTBD.
        
        Demande confirmation user avant de continuer.

        Args:
            global_function: Fonction globale identifiée par BackendAnalyzer

        Returns:
            Structure d'intention proposée avec confirmation requise
        """
        logger.info("Proposing intention structure (Niveau 0)")
        
        # Utiliser KnowledgeBase pour suggestions de patterns
        patterns_result = self.knowledge_base.search_patterns(global_function.product_type)
        # Convertir dict en list si nécessaire
        patterns = list(patterns_result.values()) if isinstance(patterns_result, dict) else patterns_result
        
        # Enrichir avec système STAR si IntentTranslator disponible
        star_realisations = []
        if self.intent_translator:
            try:
                # Parser product_type avec IntentTranslator
                parsed_query = self.intent_translator.parse_query(global_function.product_type)
                
                # Rechercher situations similaires avec embeddings
                situations = self.intent_translator.search_situation(global_function.product_type, limit=5)
                
                # Propager STAR pour obtenir réalisations
                for situation in situations:
                    realisation = self.intent_translator.propagate_star(situation)
                    if realisation:
                        star_realisations.append({
                            "pattern_name": situation.pattern_name,
                            "description": realisation.description,
                            "code": realisation.code,
                            "javascript": realisation.javascript,
                            "template": realisation.template
                        })
                        logger.debug(f"STAR realisation found: {realisation.description}")
                
                if star_realisations:
                    logger.info(f"Found {len(star_realisations)} STAR realisations for product_type '{global_function.product_type}'")
            except Exception as e:
                logger.warning(f"Error using IntentTranslator/STAR: {e}. Continuing without STAR enrichment.")
        
        # Proposer structure basée sur JTBD et state-of-the-art
        intention_structure = {
            "product_type": global_function.product_type,
            "actors": global_function.actors,
            "proposed_steps": self._infer_steps_from_global_function(global_function),
            "patterns": patterns,
            "star_realisations": star_realisations,  # Ajouter réalisations STAR
            "requires_confirmation": True
        }
        
        logger.info(f"Proposed {len(intention_structure['proposed_steps'])} steps")
        return intention_structure
    
    def infer_corps_from_step(
        self,
        step: str,
        global_function: GlobalFunction
    ) -> List[Dict[str, Any]]:
        """
        Niveau 1 : Infère les Corps (zones de contenu) depuis une étape confirmée.
        
        Avec mécanisme "Stop du Mentor" pour éviter complexité prématurée.

        Args:
            step: Étape confirmée par l'utilisateur
            global_function: Fonction globale

        Returns:
            Liste des Corps (zones de contenu) pour cette étape
        """
        logger.info(f"Inferring Corps from step: {step}")
        
        # Vérifier charge cognitive avant d'inférer
        if self.check_cognitive_load(step):
            logger.warning("Cognitive load too high, mentor stop triggered")
            return []
        
        # Inférer Corps depuis l'étape et la fonction globale
        corps = []
        
        # Exemple : pour une étape "Rassurer", inférer Corps "Social Proof" ou "Dashboard Performance"
        if "rassurer" in step.lower() or "reassure" in step.lower():
            corps.append({
                "type": "social_proof",
                "description": "Zone de preuves sociales (témoignages, statistiques)"
            })
            corps.append({
                "type": "performance_dashboard",
                "description": "Dashboard de performance et métriques"
            })
        elif "convertir" in step.lower() or "convert" in step.lower():
            corps.append({
                "type": "cta",
                "description": "Zone d'appel à l'action"
            })
            corps.append({
                "type": "pricing",
                "description": "Zone de tarification"
            })
        else:
            # Corps générique
            corps.append({
                "type": "content_zone",
                "description": f"Zone de contenu pour étape: {step}"
            })
        
        logger.info(f"Inferred {len(corps)} Corps from step")
        return corps
    
    def infer_organes_from_corps(
        self,
        corps: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Niveau 2a : Infère les Organes depuis un Corps.
        
        Les Organes sont déduits, pas choisis arbitrairement.

        Args:
            corps: Corps (zone de contenu)

        Returns:
            Liste des Organes nécessaires pour ce Corps
        """
        logger.info(f"Inferring Organes from Corps: {corps.get('type')}")
        
        organes = []
        corps_type = corps.get("type", "")
        
        # Déduire Organes depuis le type de Corps
        if corps_type == "social_proof":
            organes.append({
                "type": "testimonials_section",
                "description": "Section témoignages clients"
            })
            organes.append({
                "type": "stats_section",
                "description": "Section statistiques et chiffres clés"
            })
        elif corps_type == "performance_dashboard":
            organes.append({
                "type": "metrics_header",
                "description": "En-tête avec métriques principales"
            })
            organes.append({
                "type": "chart_section",
                "description": "Section graphiques et visualisations"
            })
        elif corps_type == "cta":
            organes.append({
                "type": "cta_header",
                "description": "En-tête avec message d'appel à l'action"
            })
            organes.append({
                "type": "cta_buttons",
                "description": "Zone de boutons d'action"
            })
        else:
            organes.append({
                "type": "generic_organe",
                "description": f"Organe générique pour {corps_type}"
            })
        
        logger.info(f"Inferred {len(organes)} Organes from Corps")
        return organes
    
    def infer_molecules_from_organe(
        self,
        organe: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Niveau 2b : Infère les Molécules depuis un Organe.
        
        Les Molécules sont déduites, pas choisies arbitrairement.

        Args:
            organe: Organe

        Returns:
            Liste des Molécules nécessaires pour cet Organe
        """
        logger.info(f"Inferring Molecules from Organe: {organe.get('type')}")
        
        molecules = []
        organe_type = organe.get("type", "")
        
        # Déduire Molécules depuis le type d'Organe
        if "testimonials" in organe_type:
            molecules.append({
                "type": "testimonial_card",
                "description": "Carte témoignage (nom + texte + photo)"
            })
        elif "stats" in organe_type:
            molecules.append({
                "type": "stat_card",
                "description": "Carte statistique (label + valeur + icône)"
            })
        elif "chart" in organe_type:
            molecules.append({
                "type": "chart_container",
                "description": "Conteneur graphique (titre + graphique + légende)"
            })
        elif "cta_buttons" in organe_type:
            molecules.append({
                "type": "button_group",
                "description": "Groupe de boutons (bouton primaire + bouton secondaire)"
            })
        else:
            molecules.append({
                "type": "generic_molecule",
                "description": f"Molécule générique pour {organe_type}"
            })
        
        logger.info(f"Inferred {len(molecules)} Molecules from Organe")
        return molecules
    
    def infer_atoms_from_molecule(
        self,
        molecule: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Niveau 3 : Infère les Atomes depuis une Molécule.
        
        Les Atomes sont déduits, pas choisis arbitrairement.

        Args:
            molecule: Molécule

        Returns:
            Liste des Atomes nécessaires pour cette Molécule
        """
        logger.info(f"Inferring Atoms from Molecule: {molecule.get('type')}")
        
        atoms = []
        molecule_type = molecule.get("type", "")
        
        # Déduire Atomes depuis le type de Molécule
        if "card" in molecule_type:
            atoms.append({"type": "label", "description": "Label texte"})
            atoms.append({"type": "value", "description": "Valeur numérique/texte"})
            atoms.append({"type": "icon", "description": "Icône SVG"})
        elif "button" in molecule_type:
            atoms.append({"type": "button", "description": "Bouton cliquable"})
            atoms.append({"type": "text", "description": "Texte du bouton"})
        elif "chart" in molecule_type:
            atoms.append({"type": "svg_canvas", "description": "Canvas SVG pour graphique"})
            atoms.append({"type": "axis_labels", "description": "Labels d'axes"})
        else:
            atoms.append({"type": "generic_atom", "description": f"Atome générique pour {molecule_type}"})
        
        logger.info(f"Inferred {len(atoms)} Atoms from Molecule")
        return atoms
    
    def check_cognitive_load(self, input_data: str) -> bool:
        """
        Vérifie la charge cognitive de l'utilisateur.
        
        Utilise les principes HCI (Fogg Behavior Model, Norman Affordances).

        Args:
            input_data: Données d'entrée à évaluer

        Returns:
            True si charge cognitive trop élevée (nécessite ventilation)
        """
        # Heuristique simple : longueur et complexité
        complexity_score = len(input_data.split()) / 100.0  # Normalisé
        
        # Si trop complexe, proposer ventilation
        if complexity_score > 0.7:
            logger.warning(f"Cognitive load high ({complexity_score:.2f}), suggest ventilation")
            return True
        
        return False
    
    def mentor_stop_check(self, step: str, current_complexity: float) -> bool:
        """
        Mécanisme "Stop du Mentor" : bloque si complexité prématurée.
        
        Empêche l'ajout de fonctionnalités complexes avant d'avoir fini les bases.

        Args:
            step: Étape en cours
            current_complexity: Score de complexité actuel

        Returns:
            True si le mentor doit stopper (complexité prématurée)
        """
        # Si complexité élevée et étape de base non terminée
        if current_complexity > 0.8:
            logger.warning(f"Mentor stop: complexity {current_complexity:.2f} too high for step {step}")
            return True
        
        return False
    
    def _infer_steps_from_global_function(
        self,
        global_function: GlobalFunction
    ) -> List[str]:
        """
        Infère les étapes du parcours depuis la fonction globale.
        
        Basé sur JTBD (Jobs To Be Done) et state-of-the-art.

        Args:
            global_function: Fonction globale

        Returns:
            Liste des étapes proposées
        """
        steps = []
        
        # Patterns selon type de produit
        if global_function.product_type == "e-commerce":
            steps = ["Captation", "Rassurer", "Convertir"]
        elif global_function.product_type == "SaaS":
            steps = ["Découvrir", "Essayer", "Souscrire"]
        elif global_function.product_type == "dashboard":
            steps = ["Vue d'ensemble", "Détails", "Actions"]
        else:
            steps = ["Étape 1", "Étape 2", "Étape 3"]
        
        return steps


# Exemple d'utilisation
if __name__ == "__main__":
    from .backend_analyzer import BackendAnalyzer
    
    # Créer un moteur d'inférence
    engine = UIInferenceEngine()
    
    # Exemple avec fonction globale
    global_func = GlobalFunction(
        product_type="e-commerce",
        actors=["user", "admin"],
        business_flows=["Purchase"],
        use_cases=["Buy product"]
    )
    
    # Proposer structure d'intention
    intention = engine.propose_intention_structure(global_func)
    print("Intention structure:", intention)
    
    # Inférer Corps depuis étape
    corps = engine.infer_corps_from_step("Rassurer", global_func)
    print("Corps:", corps)
    
    # Inférer Organes depuis Corps
    if corps:
        organes = engine.infer_organes_from_corps(corps[0])
        print("Organes:", organes)
        
        # Inférer Molécules depuis Organe
        if organes:
            molecules = engine.infer_molecules_from_organe(organes[0])
            print("Molécules:", molecules)
            
            # Inférer Atomes depuis Molécule
            if molecules:
                atoms = engine.infer_atoms_from_molecule(molecules[0])
                print("Atomes:", atoms)


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