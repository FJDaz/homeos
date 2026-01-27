"""ComponentRegistry - Orchestrateur principal pour Sullivan Kernel."""
import asyncio
from typing import Optional
from loguru import logger

from .cache.local_cache import LocalCache
from .library.elite_library import EliteLibrary
from .knowledge.knowledge_base import KnowledgeBase
from .models.component import Component
from .models.sullivan_score import ELITE_THRESHOLD


class ComponentRegistry:
    """
    Orchestrateur principal qui coordonne LocalCache, EliteLibrary et KnowledgeBase.
    
    Cette classe implémente la logique de recherche et génération de composants
    en suivant une hiérarchie : LocalCache → EliteLibrary → Génération.
    """
    
    def __init__(self):
        """
        Initialise le ComponentRegistry avec les 3 niveaux de stockage.
        """
        self.local_cache = LocalCache()
        self.elite_library = EliteLibrary()
        self.knowledge_base = KnowledgeBase()
        
        logger.info("ComponentRegistry initialized with LocalCache, EliteLibrary, and KnowledgeBase")
    
    async def get_or_generate(
        self,
        intent: str,
        user_id: str
    ) -> Component:
        """
        Récupère un composant existant ou génère un nouveau composant.
        
        Logique d'exécution :
        1. Cherche dans LocalCache (si score > 70, retourne)
        2. Cherche dans EliteLibrary (si trouvé, retourne)
        3. Génère nouveau composant (placeholder pour l'instant)
        4. Si score >= 85, suggère le partage
        
        Args:
            intent: Description de l'intention du composant recherché
            user_id: Identifiant de l'utilisateur
            
        Returns:
            Component: Le composant trouvé ou généré
        """
        logger.info(f"Searching component for intent: '{intent}' (user: {user_id})")
        
        # Étape 1: Chercher dans LocalCache
        local_component = self.local_cache.find_similar(intent, user_id)
        if local_component:
            if local_component.sullivan_score > 70:
                logger.info(f"Found component in LocalCache with score {local_component.sullivan_score:.1f}")
                return local_component
            else:
                logger.debug(f"LocalCache component score {local_component.sullivan_score:.1f} <= 70, continuing search")
        
        # Étape 2: Chercher dans EliteLibrary
        elite_component = self.elite_library.find_similar(intent)
        if elite_component:
            logger.info(f"Found component in EliteLibrary: {elite_component.name}")
            # Mettre à jour last_used
            self.elite_library.update_last_used(elite_component)
            # Sauvegarder dans LocalCache pour usage futur
            self.local_cache.save(elite_component, user_id)
            return elite_component
        
        # Étape 2.5: Recommandations contextuelles avant génération
        from .recommender import ContextualRecommender
        recommender = ContextualRecommender(library=self.elite_library, knowledge_base=self.knowledge_base)
        recommendations = recommender.recommend(intent, f"Context for {intent}", user_id, limit=3)
        if recommendations:
            logger.info(f"Found {len(recommendations)} contextual recommendations")
            # Utiliser la première recommandation si score élevé
            if recommendations[0].sullivan_score >= 80:
                logger.info(f"Using recommended component: {recommendations[0].name}")
                self.elite_library.update_last_used(recommendations[0])
                self.local_cache.save(recommendations[0], user_id)
                return recommendations[0]
        
        # Étape 3: Générer nouveau composant
        logger.info(f"No component found, generating new component for intent: '{intent}'")
        new_component = await self._generate_component(intent, user_id)
        
        # Étape 4: Si score >= 85, utiliser SharingTUI pour confirmation partage
        if new_component.sullivan_score >= ELITE_THRESHOLD:
            await self._suggest_sharing(new_component, user_id)
        
        # Mettre à jour last_used pour le composant généré
        if new_component.last_used is None:
            from datetime import datetime
            new_component.last_used = datetime.now()
        
        # Sauvegarder dans LocalCache
        self.local_cache.save(new_component, user_id)
        
        return new_component
    
    async def _generate_component(
        self,
        intent: str,
        user_id: str
    ) -> Component:
        """
        Génère un nouveau composant via ComponentGenerator (AETHERFLOW).
        
        Args:
            intent: Description de l'intention
            user_id: Identifiant de l'utilisateur
            
        Returns:
            Component: Nouveau composant généré
        """
        from .generator.component_generator import ComponentGenerator
        
        logger.info(f"Generating component via ComponentGenerator for intent: '{intent}'")
        
        # Enrichir contexte depuis KnowledgeBase
        context = f"Générer composant frontend pour: {intent}"
        
        # Créer ComponentGenerator avec workflow PROTO (rapidité)
        # TODO: Permettre choix workflow (PROTO vs PROD) selon contexte
        generator = ComponentGenerator(
            agent_router=None,  # Utilisera AgentRouter par défaut
            knowledge_base=self.knowledge_base,
            workflow="PROTO"  # PROTO pour rapidité, PROD pour qualité
        )
        
        try:
            # Générer composant via AETHERFLOW
            component = await generator.generate_component(
                intent=intent,
                context=context,
                user_id=user_id
            )
            
            logger.info(f"Generated component via AETHERFLOW: {component.name} ({component.size_kb} KB)")
            
            # Évaluer le composant avec tous les évaluateurs
            component = await self._evaluate_component(component)
            
            return component
            
        except Exception as e:
            logger.error(f"Error generating component via ComponentGenerator: {e}", exc_info=True)
            # Fallback: créer composant placeholder en cas d'erreur
            from datetime import datetime
            
            logger.warning("Falling back to placeholder component due to generation error")
            placeholder_component = Component(
                name=f"component_{intent[:20].replace(' ', '_')}",
                sullivan_score=50.0,  # Score réduit pour placeholder
                performance_score=60,
                accessibility_score=60,
                ecology_score=60,
                popularity_score=0,
                validation_score=60,
                size_kb=5,
                created_at=datetime.now(),
                user_id=user_id
            )
            return placeholder_component
    
    async def _evaluate_component(self, component: Component) -> Component:
        """
        Évalue un composant avec tous les évaluateurs et met à jour les scores.

        Args:
            component: Composant à évaluer

        Returns:
            Component avec scores mis à jour
        """
        from .evaluators import PerformanceEvaluator, AccessibilityEvaluator, ValidationEvaluator
        
        logger.info(f"Evaluating component: {component.name}")
        
        try:
            # Évaluer performance
            performance_evaluator = PerformanceEvaluator()
            performance_score = await performance_evaluator.evaluate_performance(component)
            
            # Calculer score écologie depuis taille
            ecology_score = performance_evaluator.calculate_ecology_score(component.size_kb)
            
            # Évaluer accessibilité
            accessibility_evaluator = AccessibilityEvaluator()
            accessibility_score = await accessibility_evaluator.evaluate_accessibility(component)
            
            # Évaluer validation (guidelines TDD, DRY, SOLID)
            validation_evaluator = ValidationEvaluator()
            validation_score = await validation_evaluator.evaluate_validation(component)
            
            # Calculer score composite Sullivan
            from .models.sullivan_score import SullivanScore
            sullivan_score_obj = SullivanScore(
                performance=performance_score,
                accessibility=accessibility_score,
                ecology=ecology_score,
                popularity=component.popularity_score,  # Conservé depuis composant
                validation=validation_score
            )
            sullivan_score = sullivan_score_obj.total()
            
            # Mettre à jour composant avec scores réels
            component.performance_score = performance_score
            component.accessibility_score = accessibility_score
            component.ecology_score = ecology_score
            component.validation_score = validation_score
            component.sullivan_score = sullivan_score
            
            # Classifier le composant
            from ..models.categories import classify_component
            component.category = classify_component(component).value
            
            # Initialiser last_used
            from datetime import datetime
            if component.last_used is None:
                component.last_used = datetime.now()
            
            logger.info(
                f"Component evaluated - Performance: {performance_score}, "
                f"Accessibility: {accessibility_score}, Ecology: {ecology_score}, "
                f"Validation: {validation_score}, Sullivan: {sullivan_score:.1f}, "
                f"Category: {component.category}"
            )
            
            return component
            
        except Exception as e:
            logger.error(f"Error evaluating component: {e}", exc_info=True)
            # En cas d'erreur, retourner composant avec scores par défaut
            return component
    
    async def _suggest_sharing(
        self,
        component: Component,
        user_id: str
    ) -> None:
        """
        Suggère à l'utilisateur de partager le composant dans EliteLibrary via SharingTUI.
        
        Args:
            component: Le composant à suggérer pour partage
            user_id: Identifiant de l'utilisateur
        """
        logger.info(
            f"Component '{component.name}' has score {component.sullivan_score:.1f} >= {ELITE_THRESHOLD}. "
            f"Showing sharing confirmation TUI for user {user_id}"
        )
        
        # Utiliser SharingTUI pour confirmation
        from .library.sharing_tui import SharingTUI
        
        try:
            sharing_tui = SharingTUI()
            shared_component = sharing_tui.confirm_sharing(self.elite_library, component)
            
            if shared_component:
                logger.info(f"Component '{component.name}' shared successfully via TUI")
            else:
                logger.info(f"Sharing cancelled by user for component '{component.name}'")
        except Exception as e:
            logger.error(f"Error in sharing TUI: {e}", exc_info=True)
            # Fallback: ajout automatique si TUI échoue
            success = self.elite_library.add(component)
            if success:
                logger.info(f"Component '{component.name}' added to EliteLibrary (fallback)")
