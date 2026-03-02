"""
DesignAnalyzerFast - Version optimisée latence du DesignAnalyzer

Optimisations:
1. Cache LRU pour éviter les appels répétés
2. Timeout agressif (5-10s max)
3. Préprocessing ultra-aggressif des images
4. Fallback vers résultat partiel si timeout
"""

import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

from .design_analyzer import DesignAnalyzer, DesignStructure
from .vision_cache import get_vision_cache
from ...models.gemini_client import GeminiClient


class DesignAnalyzerFast:
    """
    Wrapper rapide pour DesignAnalyzer avec cache et timeout.
    """

    # Timeout augmenté à 60s pour laisser Gemini Vision analyser des images complexes
    # (l'analyse de structure prend ~30-45s sur des designs UI détaillés)
    DEFAULT_TIMEOUT_SECONDS = 60
    
    def __init__(
        self,
        design_analyzer: DesignAnalyzer,
        gemini_client: Optional[GeminiClient] = None,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ):
        """
        Args:
            design_analyzer: Instance de DesignAnalyzer à wrapper
            gemini_client: Client Gemini (optionnel, pour timeout personnalisé)
            timeout_seconds: Timeout maximum pour l'analyse
        """
        self.design_analyzer = design_analyzer
        self.gemini_client = gemini_client
        self.timeout_seconds = timeout_seconds
        self.cache = get_vision_cache()
        
        logger.info(f"DesignAnalyzerFast initialized (timeout: {timeout_seconds}s)")
    
    async def analyze_image(self, image_path: Path) -> DesignStructure:
        """
        Analyse une image avec cache et timeout.
        
        Args:
            image_path: Chemin vers l'image
            
        Returns:
            DesignStructure analysée
            
        Raises:
            TimeoutError: Si l'analyse dépasse le timeout
            Exception: Si l'analyse échoue
        """
        image_path = Path(image_path)
        
        # 1. Vérifier le cache
        image_bytes = image_path.read_bytes()
        cached_result = self.cache.get(image_bytes)
        
        if cached_result is not None:
            logger.info(f"[Fast] Cache hit for {image_path.name}")
            return DesignStructure.from_dict(cached_result)
        
        # 2. Analyse avec timeout
        logger.info(f"[Fast] Analyzing {image_path.name} (timeout: {self.timeout_seconds}s)")
        
        try:
            # Lancer l'analyse avec timeout
            result = await asyncio.wait_for(
                self.design_analyzer.analyze_image(image_path),
                timeout=self.timeout_seconds
            )
            
            # Cacher le résultat
            self.cache.set(image_bytes, result.to_dict())
            logger.info(f"[Fast] Analysis completed for {image_path.name}")
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"[Fast] TIMEOUT after {self.timeout_seconds}s for {image_path.name}")
            
            # Retourner une structure minimale en cas de timeout
            return self._fallback_structure(image_path, "timeout")
            
        except Exception as e:
            logger.error(f"[Fast] Analysis failed: {e}")
            raise
    
    def _fallback_structure(self, image_path: Path, reason: str) -> DesignStructure:
        """
        Crée une structure minimale en cas d'échec/timeout.
        
        Args:
            image_path: Chemin de l'image
            reason: Raison du fallback
            
        Returns:
            DesignStructure minimale
        """
        logger.warning(f"[Fast] Using fallback structure for {image_path.name} ({reason})")
        
        return DesignStructure(
            sections=[{
                "type": "main_content",
                "bounds": [0, 0, 100, 100],
                "description": f"Auto-generated (fallback: {reason})"
            }],
            layout={"type": "single_column", "columns": 1},
            components=[],
            hierarchy={"root": "main_content", "children": []}
        )


# Fonction utilitaire pour créer une instance rapide
async def analyze_image_fast(
    image_path: Path,
    agent_router=None,
    knowledge_base=None,
    timeout_seconds: int = 10,
) -> DesignStructure:
    """
    Analyse rapide d'une image avec timeout et cache.
    
    Args:
        image_path: Chemin vers l'image
        agent_router: AgentRouter (optionnel)
        knowledge_base: KnowledgeBase (optionnel)
        timeout_seconds: Timeout en secondes
        
    Returns:
        DesignStructure analysée
    """
    from ...models.agent_router import AgentRouter
    from ..knowledge.knowledge_base import KnowledgeBase
    
    agent_router = agent_router or AgentRouter(execution_mode="BUILD")
    knowledge_base = knowledge_base or KnowledgeBase()
    
    design_analyzer = DesignAnalyzer(
        agent_router=agent_router,
        knowledge_base=knowledge_base
    )
    
    fast_analyzer = DesignAnalyzerFast(
        design_analyzer=design_analyzer,
        timeout_seconds=timeout_seconds
    )
    
    return await fast_analyzer.analyze_image(image_path)


__all__ = ["DesignAnalyzerFast", "analyze_image_fast"]
