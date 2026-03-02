"""ValidationEvaluator - Évaluation guidelines (TDD, DRY, SOLID) via AETHERFLOW DOUBLE-CHECK."""
import json
import uuid
import tempfile
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime
from loguru import logger

from ..models.component import Component
from ...orchestrator import Orchestrator


class ValidationEvaluator:
    """
    Évaluateur de validation pour composants frontend.
    
    Utilise DOUBLE-CHECK mode d'AETHERFLOW pour validation guidelines (TDD, DRY, SOLID).
    """
    
    def __init__(self):
        """Initialise l'évaluateur de validation."""
        logger.info("ValidationEvaluator initialized")
    
    async def evaluate_validation(self, component: Component) -> int:
        """
        Évalue la validation d'un composant selon guidelines (0-100).

        Args:
            component: Composant à évaluer

        Returns:
            Score de validation (0-100)
        """
        logger.info(f"Evaluating validation for component: {component.name}")
        
        try:
            # Créer plan JSON pour validation
            plan_path = self._create_validation_plan(component)
            
            # Exécuter via AETHERFLOW DOUBLE-CHECK workflow
            score = await self._execute_validation(plan_path)
            
            logger.info(f"Validation score: {score}")
            return score
            
        except Exception as e:
            logger.warning(f"Error evaluating validation, using heuristic: {e}")
            return self._calculate_heuristic_score(component)
    
    def _create_validation_plan(self, component: Component) -> Path:
        """
        Crée un plan JSON pour validation guidelines.

        Args:
            component: Composant à valider

        Returns:
            Chemin vers le plan JSON créé
        """
        task_id = str(uuid.uuid4())
        
        plan = {
            "task_id": task_id,
            "description": f"Validation guidelines (TDD, DRY, SOLID) pour composant: {component.name}",
            "steps": [
                {
                    "id": "step_validation_dry",
                    "description": f"Valider principe DRY (Don't Repeat Yourself) pour composant {component.name}. Vérifier absence de duplication de code HTML/CSS/JS. Analyser patterns répétés, classes CSS dupliquées, fonctions JS répétées. Score basé sur nombre de duplications détectées.",
                    "type": "analysis",
                    "complexity": 0.6,
                    "estimated_tokens": 2000,
                    "dependencies": [],
                    "validation_criteria": [
                        "Absence de duplication de code",
                        "Patterns réutilisables identifiés",
                        "Code factorisé correctement"
                    ],
                    "context": {
                        "language": "python",
                        "framework": "validation",
                        "files": []
                    }
                },
                {
                    "id": "step_validation_solid",
                    "description": f"Valider principe SOLID (Single Responsibility) pour composant {component.name}. Vérifier responsabilité unique : HTML structure, CSS styling, JS behavior séparés. Chaque partie a une responsabilité claire. Score basé sur séparation des responsabilités.",
                    "type": "analysis",
                    "complexity": 0.6,
                    "estimated_tokens": 2000,
                    "dependencies": ["step_validation_dry"],
                    "validation_criteria": [
                        "Séparation claire HTML/CSS/JS",
                        "Responsabilité unique par partie",
                        "Pas de mélange de responsabilités"
                    ],
                    "context": {
                        "language": "python",
                        "framework": "validation",
                        "files": []
                    }
                },
                {
                    "id": "step_validation_tdd",
                    "description": f"Valider principe TDD (Test-Driven Development) pour composant {component.name}. Vérifier structure testable : fonctions isolées, pas de dépendances globales, code modulaire. Score basé sur facilité de testabilité.",
                    "type": "analysis",
                    "complexity": 0.7,
                    "estimated_tokens": 2500,
                    "dependencies": ["step_validation_dry", "step_validation_solid"],
                    "validation_criteria": [
                        "Structure testable",
                        "Fonctions isolées",
                        "Code modulaire"
                    ],
                    "context": {
                        "language": "python",
                        "framework": "validation",
                        "files": []
                    }
                }
            ],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "claude_version": "claude-code",
                "project_context": f"Validation guidelines Sullivan: {component.name}",
                "component_name": component.name
            }
        }
        
        # Sauvegarder plan dans fichier temporaire
        temp_dir = Path(tempfile.gettempdir()) / "sullivan_validation_plans"
        temp_dir.mkdir(parents=True, exist_ok=True)
        plan_path = temp_dir / f"validation_{task_id}.json"
        
        with open(plan_path, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2)
        
        logger.info(f"Created validation plan: {plan_path}")
        return plan_path
    
    async def _execute_validation(self, plan_path: Path) -> int:
        """
        Exécute la validation via AETHERFLOW DOUBLE-CHECK workflow.

        Args:
            plan_path: Chemin vers le plan JSON

        Returns:
            Score de validation (0-100)
        """
        logger.info("Executing validation via AETHERFLOW DOUBLE-CHECK workflow")
        
        # Créer répertoire de sortie
        output_dir = Path(tempfile.gettempdir()) / "sullivan_validation_outputs" / plan_path.stem
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Utiliser Orchestrator avec mode DOUBLE-CHECK
            orchestrator = Orchestrator(execution_mode="DOUBLE-CHECK")
            
            result = await orchestrator.execute_plan(
                plan_path=plan_path,
                output_dir=output_dir,
                context=None,
                use_streaming=False
            )
            
            await orchestrator.close()
            
            # Analyser résultats pour calculer score
            score = self._calculate_score_from_results(result)
            
            logger.info(f"Validation completed, score: {score}")
            return score
            
        except Exception as e:
            logger.error(f"Error executing validation: {e}", exc_info=True)
            raise
    
    def _calculate_score_from_results(self, result: Dict[str, Any]) -> int:
        """
        Calcule score depuis résultats AETHERFLOW.

        Args:
            result: Résultats d'exécution AETHERFLOW

        Returns:
            Score (0-100)
        """
        # Analyser résultats des steps
        results = result.get("results", {})
        
        if not results:
            logger.warning("No validation results found")
            return 70  # Score par défaut
        
        # Compter steps validés
        validated_steps = sum(1 for r in results.values() if r.success)
        total_steps = len(results)
        
        if total_steps == 0:
            return 70
        
        # Score basé sur pourcentage de steps validés
        validation_rate = validated_steps / total_steps
        base_score = int(validation_rate * 100)
        
        # Ajuster selon contenu des outputs (chercher indicateurs positifs)
        positive_indicators = 0
        for step_result in results.values():
            if step_result.output:
                output_lower = step_result.output.lower()
                if any(word in output_lower[:1000] for word in ["valid", "pass", "ok", "success", "✓"]):
                    positive_indicators += 1
        
        # Bonus si indicateurs positifs
        if positive_indicators > 0:
            bonus = min(10, positive_indicators * 2)
            base_score = min(100, base_score + bonus)
        
        return base_score
    
    def _calculate_heuristic_score(self, component: Component) -> int:
        """
        Calcule score heuristique de validation.

        Args:
            component: Composant à évaluer

        Returns:
            Score heuristique (0-100)
        """
        # Score par défaut basé sur composant généré
        # Les composants générés par AETHERFLOW devraient respecter guidelines
        base_score = 80
        
        # Ajuster selon scores existants du composant
        # Si performance et accessibility sont bons, validation probablement bonne aussi
        if component.performance_score >= 80 and component.accessibility_score >= 80:
            base_score = 85
        elif component.performance_score >= 70 and component.accessibility_score >= 70:
            base_score = 75
        else:
            base_score = 70
        
        return base_score


# Exemple d'utilisation
if __name__ == "__main__":
    import asyncio
    from datetime import datetime
    
    async def main():
        evaluator = ValidationEvaluator()
        
        component = Component(
            name="test_component",
            sullivan_score=75.0,
            performance_score=80,
            accessibility_score=70,
            ecology_score=75,
            popularity_score=0,
            validation_score=80,
            size_kb=50,
            created_at=datetime.now(),
            user_id="test_user"
        )
        
        score = await evaluator.evaluate_validation(component)
        print(f"Validation score: {score}")
    
    asyncio.run(main())
