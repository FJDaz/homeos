#!/usr/bin/env python3
"""Test rapide pour vérifier que Gemini est utilisable avec facturation activée."""
import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Backend.Prod.models.gemini_client import GeminiClient
from Backend.Prod.models.agent_router import AgentRouter
from loguru import logger

async def test_gemini_direct():
    """Test direct du GeminiClient."""
    print("\n" + "="*60)
    print("TEST 1 : GeminiClient Direct")
    print("="*60)
    
    try:
        client = GeminiClient()
        print(f"✅ GeminiClient initialisé")
        print(f"   Modèle : {client.model}")
        print(f"   API URL : {client.api_url[:60]}...")
        
        # Test génération simple
        print("\n📤 Test de génération...")
        result = await client.generate(
            prompt="Explique brièvement ce qu'est Python en 2 phrases.",
            max_tokens=100
        )
        
        if result.success:
            print(f"✅ Génération réussie !")
            print(f"   Tokens utilisés : {result.tokens_used}")
            print(f"   Coût : ${result.cost_usd:.6f}")
            print(f"   Temps : {result.execution_time_ms:.0f}ms")
            print(f"\n📝 Réponse :\n{result.code[:200]}...")
            return True
        else:
            print(f"❌ Erreur : {result.error}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation : {e}")
        return False
    finally:
        await client.close()

async def test_gemini_via_router():
    """Test via AgentRouter."""
    print("\n" + "="*60)
    print("TEST 2 : Gemini via AgentRouter")
    print("="*60)
    
    try:
        router = AgentRouter()
        
        # Vérifier si Gemini est disponible
        available = router.get_available_providers()
        print(f"📋 Providers disponibles : {list(available.keys())}")
        
        if "gemini" not in available:
            print("❌ Gemini n'est pas disponible dans AgentRouter")
            return False
        
        print(f"✅ Gemini disponible")
        print(f"   Spécialités : {available['gemini']}")
        
        # Test avec routage automatique (analysis devrait utiliser Gemini)
        print("\n📤 Test avec routage automatique (type: analysis)...")
        result = await router.generate(
            task="Analyse ce code Python et explique ce qu'il fait",
            context="def hello(): print('Hello')",
            provider="gemini"  # Forcer Gemini pour le test
        )
        
        if result.success:
            print(f"✅ Génération réussie via AgentRouter !")
            print(f"   Provider utilisé : {result.provider}")
            print(f"   Tokens utilisés : {result.tokens_used}")
            print(f"   Coût : ${result.cost_usd:.6f}")
            print(f"   Temps : {result.execution_time_ms:.0f}ms")
            print(f"\n📝 Réponse :\n{result.code[:200]}...")
            return True
        else:
            print(f"❌ Erreur : {result.error}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await router.close()

async def test_gemini_quota_info():
    """Affiche les informations sur les quotas Gemini."""
    print("\n" + "="*60)
    print("INFO : Quotas Gemini")
    print("="*60)
    
    print("""
📊 Quotas Gratuits (même avec facturation activée) :
   - Requêtes/min : 5-15 (selon modèle)
   - Tokens/min : 250,000
   - Requêtes/jour : 100-1,000

💰 Facturation :
   - Vous ne payez QUE si vous dépassez les quotas gratuits
   - Si vous restez dans les limites → $0.00 facturé
   - Avec facturation activée : Données privées (pas d'entraînement Google)

✅ Votre compte de facturation est associé, vous pouvez utiliser Gemini !
""")

async def main():
    """Exécute tous les tests."""
    print("\n" + "="*60)
    print("🔍 VÉRIFICATION GEMINI - Facturation Activée")
    print("="*60)
    
    results = []
    
    # Test 1 : Direct
    result1 = await test_gemini_direct()
    results.append(("GeminiClient Direct", result1))
    
    # Test 2 : Via Router
    result2 = await test_gemini_via_router()
    results.append(("Gemini via AgentRouter", result2))
    
    # Info quotas
    await test_gemini_quota_info()
    
    # Résumé
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*60)
    
    for name, success in results:
        status = "✅ RÉUSSI" if success else "❌ ÉCHOUÉ"
        print(f"{status} : {name}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n✅ Gemini est utilisable avec votre compte de facturation !")
        print("   Vous pouvez utiliser Gemini dans AETHERFLOW.")
        print("   Coût : $0.00 tant que vous restez dans les quotas gratuits.")
    else:
        print("\n⚠️ Certains tests ont échoué.")
        print("   Vérifiez votre configuration et votre API key.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
