"""PerformanceEvaluator - Évaluation performance réelle via Lighthouse CI."""
import asyncio
from typing import Optional
from loguru import logger

from ..models.component import Component


class PerformanceEvaluator:
    """
    Évaluateur de performance pour composants frontend.
    
    Utilise Lighthouse CI pour performance réelle, avec fallback heuristique.
    Calcule également la taille du bundle et le score écologie.
    """
    
    def __init__(self, lighthouse_url: Optional[str] = None):
        """
        Initialise l'évaluateur de performance.

        Args:
            lighthouse_url: URL de Lighthouse CI (optionnel, utilise fallback si None)
        """
        self.lighthouse_url = lighthouse_url
        logger.info("PerformanceEvaluator initialized")
    
    async def evaluate_performance(self, component: Component) -> int:
        """
        Évalue la performance d'un composant (0-100).

        Args:
            component: Composant à évaluer

        Returns:
            Score de performance (0-100)
        """
        logger.info(f"Evaluating performance for component: {component.name}")
        
        try:
            # Essayer Lighthouse CI si disponible
            if self.lighthouse_url:
                score = await self._get_lighthouse_score(component)
                logger.info(f"Lighthouse score: {score}")
                return score
            else:
                # Fallback vers calcul heuristique
                score = self._calculate_heuristic_score(component)
                logger.info(f"Heuristic performance score: {score}")
                return score
                
        except Exception as e:
            logger.warning(f"Error evaluating performance, using heuristic: {e}")
            return self._calculate_heuristic_score(component)
    
    def calculate_bundle_size(self, html: str, css: str, js: str) -> int:
        """
        Calcule la taille réelle du bundle en KB.

        Args:
            html: Code HTML
            css: Code CSS
            js: Code JavaScript

        Returns:
            Taille en KB (entier)
        """
        total_bytes = len(html.encode('utf-8')) + len(css.encode('utf-8')) + len(js.encode('utf-8'))
        size_kb = total_bytes / 1024
        return int(size_kb)
    
    def calculate_ecology_score(self, size_kb: int) -> int:
        """
        Calcule le score écologie basé sur la taille (plus petit = meilleur).

        Args:
            size_kb: Taille du bundle en KB

        Returns:
            Score écologie (0-100)
        """
        # Score basé sur taille : < 10 KB = 100, < 50 KB = 90, < 100 KB = 80, etc.
        if size_kb < 10:
            return 100
        elif size_kb < 50:
            return 90
        elif size_kb < 100:
            return 80
        elif size_kb < 200:
            return 70
        elif size_kb < 500:
            return 60
        elif size_kb < 1000:
            return 50
        else:
            # Score décroissant pour grandes tailles
            score = max(0, 100 - (size_kb / 10))
            return int(score)
    
    async def _get_lighthouse_score(self, component: Component) -> int:
        """
        Obtient le score Lighthouse CI (à implémenter avec vraie API).

        Args:
            component: Composant à évaluer

        Returns:
            Score Lighthouse (0-100)
        """
        # TODO: Implémenter appel réel à Lighthouse CI
        # Pour l'instant, utiliser heuristique
        logger.debug("Lighthouse CI not implemented, using heuristic")
        return self._calculate_heuristic_score(component)
    
    def _calculate_heuristic_score(self, component: Component) -> int:
        """
        Calcule un score heuristique basé sur la taille du bundle.

        Args:
            component: Composant à évaluer

        Returns:
            Score heuristique (0-100)
        """
        # Utiliser size_kb du composant si disponible
        size_kb = component.size_kb
        
        # Score basé sur taille : plus petit = meilleur
        if size_kb < 10:
            return 95
        elif size_kb < 50:
            return 85
        elif size_kb < 100:
            return 75
        elif size_kb < 200:
            return 65
        elif size_kb < 500:
            return 55
        else:
            # Score décroissant pour grandes tailles
            score = max(30, 100 - (size_kb / 10))
            return int(score)


# Exemple d'utilisation
if __name__ == "__main__":
    from datetime import datetime
    
    async def main():
        evaluator = PerformanceEvaluator()
        
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
        
        score = await evaluator.evaluate_performance(component)
        print(f"Performance score: {score}")
        
        ecology = evaluator.calculate_ecology_score(component.size_kb)
        print(f"Ecology score: {ecology}")
    
    asyncio.run(main())
