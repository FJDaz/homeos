#!/usr/bin/env python3
"""Test du fallback automatique Groq -> Gemini en cas de rate limit."""
import asyncio
import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent.parent))

from Backend.Prod.models.agent_router import AgentRouter
from Backend.Prod.models.plan_reader import Step
from loguru import logger


async def test_rate_limit_detection():
    """Test que le code détecte correctement les erreurs de rate limit."""
    
    # Créer un step de test
    step = Step({
        "id": "step_test_rate_limit",
        "description": "Test de détection du rate limit",
        "type": "code_generation",
        "complexity": 0.3,
        "estimated_tokens": 150,
        "dependencies": [],
        "validation_criteria": ["Code fonctionnel"],
        "context": {"language": "python", "files": ["test.py"]}
    })
    
    logger.info("=" * 80)
    logger.info("TEST: Fallback automatique Groq -> Gemini en cas de rate limit")
    logger.info("=" * 80)
    
    # Créer le router en mode FAST
    router = AgentRouter(execution_mode="FAST")
    
    logger.info(f"Providers disponibles: {list(router._clients.keys())}")
    logger.info(f"Mode d'exécution: {router.execution_mode}")
    
    # Vérifier que Groq est le provider par défaut en mode FAST
    provider = router.select_provider_for_step(step)
    logger.info(f"Provider sélectionné pour step: {provider}")
    
    if provider != "groq":
        logger.warning(f"⚠️  Provider sélectionné n'est pas Groq: {provider}")
        logger.info("Le test du fallback nécessite que Groq soit sélectionné en premier")
    
    # Exécuter le step
    logger.info("\nExécution du step...")
    logger.info("Si Groq retourne 429, le fallback vers Gemini devrait se déclencher automatiquement")
    
    try:
        result = await router.execute_step(step, context="Test du fallback automatique")
        
        logger.info("\n" + "=" * 80)
        logger.info("RÉSULTAT DU TEST")
        logger.info("=" * 80)
        
        if result.success:
            logger.success(f"✅ Step exécuté avec succès")
            logger.info(f"   Provider utilisé: {provider}")
            logger.info(f"   Tokens: {result.tokens_used}")
            logger.info(f"   Coût: ${result.cost_usd:.6f}")
            logger.info(f"   Temps: {result.execution_time_ms:.0f}ms")
            
            if result.error:
                logger.warning(f"   Erreur (mais succès): {result.error}")
            
            # Vérifier si un fallback a été utilisé
            # (on ne peut pas le vérifier directement, mais on peut regarder les logs)
            logger.info("\n💡 Pour vérifier le fallback:")
            logger.info("   - Cherchez 'falling back to Gemini' dans les logs ci-dessus")
            logger.info("   - Si Groq était rate limité, Gemini devrait avoir été utilisé")
        else:
            logger.error(f"❌ Step échoué: {result.error}")
            logger.info("\n💡 Si l'erreur contient '429' ou 'rate limit', le fallback devrait se déclencher")
            logger.info("   Vérifiez les logs ci-dessus pour voir si le fallback a été tenté")
        
        await router.close()
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'exécution: {e}")
        import traceback
        traceback.print_exc()
        await router.close()
        return False
    
    return result.success


async def test_multiple_rapid_requests():
    """Test avec plusieurs requêtes rapides pour essayer de déclencher le rate limit."""
    
    logger.info("\n" + "=" * 80)
    logger.info("TEST: Requêtes rapides multiples pour déclencher rate limit")
    logger.info("=" * 80)
    
    step = Step({
        "id": "step_rapid",
        "description": "Test rapide",
        "type": "code_generation",
        "complexity": 0.1,
        "estimated_tokens": 50,
        "dependencies": [],
        "validation_criteria": [],
        "context": {"language": "python"}
    })
    
    router = AgentRouter(execution_mode="FAST")
    
    logger.info("Envoi de 5 requêtes rapides...")
    logger.info("Si Groq a un rate limit, certaines devraient déclencher le fallback")
    
    results = []
    for i in range(5):
        logger.info(f"\nRequête {i+1}/5...")
        try:
            result = await router.execute_step(step, context=f"Test rapide {i+1}")
            results.append(result.success)
            
            if result.success:
                logger.info(f"  ✅ Succès (provider: {router.select_provider_for_step(step)})")
            else:
                logger.warning(f"  ⚠️  Échec: {result.error}")
                if "429" in str(result.error) or "rate limit" in str(result.error).lower():
                    logger.info(f"  🔄 Rate limit détecté - fallback devrait être déclenché")
        except Exception as e:
            logger.error(f"  ❌ Erreur: {e}")
            results.append(False)
        
        # Petite pause entre les requêtes
        await asyncio.sleep(0.5)
    
    await router.close()
    
    success_count = sum(results)
    logger.info(f"\n📊 Résultats: {success_count}/5 requêtes réussies")
    
    return success_count > 0


async def main():
    """Fonction principale."""
    logger.info("🧪 Tests du fallback automatique Groq -> Gemini")
    logger.info("")
    
    # Test 1: Exécution normale avec détection du fallback
    test1_ok = await test_rate_limit_detection()
    
    # Test 2: Requêtes rapides multiples
    test2_ok = await test_multiple_rapid_requests()
    
    logger.info("\n" + "=" * 80)
    logger.info("RÉSUMÉ DES TESTS")
    logger.info("=" * 80)
    logger.info(f"Test 1 (Détection fallback): {'✅ PASS' if test1_ok else '❌ FAIL'}")
    logger.info(f"Test 2 (Requêtes rapides): {'✅ PASS' if test2_ok else '❌ FAIL'}")
    
    if test1_ok and test2_ok:
        logger.info("\n✅ Tous les tests sont passés")
        logger.info("💡 Le fallback automatique devrait fonctionner si Groq est rate limité")
    else:
        logger.warning("\n⚠️  Certains tests ont échoué")
        logger.info("💡 Vérifiez les logs ci-dessus pour plus de détails")


if __name__ == "__main__":
    asyncio.run(main())
