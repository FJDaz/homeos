"""ContextualRecommender - Recommandations contextuelles de composants."""
from typing import List, Optional
from loguru import logger

from ..library.elite_library import EliteLibrary
from ..models.component import Component
from ..models.categories import ComponentCategory
from ..knowledge.knowledge_base import KnowledgeBase


class ContextualRecommender:
    """
    Recommandateur contextuel de composants.
    
    Recommande composants similaires basés sur contexte utilisateur,
    utilise KnowledgeBase pour recherche sémantique.
    """
    
    def __init__(
        self,
        library: Optional[EliteLibrary] = None,
        knowledge_base: Optional[KnowledgeBase] = None
    ):
        """
        Initialise le recommandateur contextuel.

        Args:
            library: Instance EliteLibrary (optionnel)
            knowledge_base: Instance KnowledgeBase (optionnel)
        """
        self.library = library or EliteLibrary()
        # KnowledgeBase peut être instancié sans paramètres (utilise chemins par défaut)
        self.knowledge_base = knowledge_base or KnowledgeBase()
        logger.info("ContextualRecommender initialized")
    
    def recommend(
        self,
        intent: str,
        context: str,
        user_id: str,
        category: Optional[str] = None,
        limit: int = 5
    ) -> List[Component]:
        """
        Recommande des composants similaires basés sur contexte.

        Args:
            intent: Intention du composant recherché
            context: Contexte additionnel
            user_id: Identifiant utilisateur
            category: Catégorie filtrée (optionnel)
            limit: Nombre maximum de recommandations (défaut: 5)

        Returns:
            Liste de composants recommandés (top N, triés par score Sullivan décroissant)
        """
        logger.info(f"Recommending components for intent: '{intent}' (category: {category})")
        
        # Charger tous les composants depuis EliteLibrary
        all_components = self._load_all_components()
        
        if not all_components:
            logger.warning("No components found in EliteLibrary")
            return []
        
        # Filtrer par catégorie si spécifiée
        if category:
            filtered_components = [c for c in all_components if c.category == category]
        else:
            filtered_components = all_components
        
        # Recherche sémantique via KnowledgeBase
        # Utiliser search_patterns pour trouver patterns similaires
        patterns = self.knowledge_base.search_patterns(intent)
        
        # Score de similarité basique (basé sur nom et contexte)
        scored_components = []
        for component in filtered_components:
            score = self._calculate_similarity_score(component, intent, context, patterns)
            scored_components.append((score, component))
        
        # Trier par score décroissant, puis par score Sullivan décroissant
        scored_components.sort(key=lambda x: (x[0], x[1].sullivan_score), reverse=True)
        
        # Retourner top N
        recommendations = [comp for _, comp in scored_components[:limit]]
        
        logger.info(f"Found {len(recommendations)} recommendations")
        return recommendations
    
    def _load_all_components(self) -> List[Component]:
        """
        Charge tous les composants depuis EliteLibrary.

        Returns:
            Liste de composants
        """
        components = []
        
        for file in self.library.path.glob("*.json"):
            if file.name.startswith("archived_"):
                continue
            
            try:
                import json
                with open(file, "r", encoding="utf-8") as f:
                    component_dict = json.load(f)
                    # Gérer conversion datetime
                    from datetime import datetime
                    if "created_at" in component_dict and isinstance(component_dict["created_at"], str):
                        component_dict["created_at"] = datetime.fromisoformat(component_dict["created_at"])
                    if "last_used" in component_dict and isinstance(component_dict["last_used"], str):
                        component_dict["last_used"] = datetime.fromisoformat(component_dict["last_used"])
                    
                    component = Component(**component_dict)
                    components.append(component)
            except Exception as e:
                logger.warning(f"Error loading component from {file}: {e}")
        
        return components
    
    def _calculate_similarity_score(
        self,
        component: Component,
        intent: str,
        context: str,
        patterns: dict
    ) -> float:
        """
        Calcule un score de similarité entre composant et intent/context.

        Args:
            component: Composant à scorer
            intent: Intention recherchée
            context: Contexte additionnel
            patterns: Patterns trouvés dans KnowledgeBase

        Returns:
            Score de similarité (0-1)
        """
        score = 0.0
        
        # Score basé sur nom (mots communs)
        intent_words = set(intent.lower().split())
        component_words = set(component.name.lower().split())
        common_words = intent_words.intersection(component_words)
        if intent_words:
            score += len(common_words) / len(intent_words) * 0.5
        
        # Score basé sur patterns KnowledgeBase
        if patterns:
            score += 0.3
        
        # Bonus pour score Sullivan élevé
        if component.sullivan_score >= 85:
            score += 0.2
        
        return min(1.0, score)


# Exemple d'utilisation
if __name__ == "__main__":
    from datetime import datetime
    
    recommender = ContextualRecommender()
    
    recommendations = recommender.recommend(
        intent="bouton d'appel à l'action",
        context="Landing page SaaS",
        user_id="test_user",
        limit=5
    )
    
    print(f"Found {len(recommendations)} recommendations:")
    for comp in recommendations:
        print(f"  - {comp.name} (score: {comp.sullivan_score:.1f})")
