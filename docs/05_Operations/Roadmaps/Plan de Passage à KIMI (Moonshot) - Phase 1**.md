# **Plan de Passage à KIMI (Moonshot) - Phase 1**

Tu as raison, ça s'est noyé. Voici un plan **concret et immédiat** pour intégrer KIMI comme principal provider dans AETHERFLOW.

## 🎯 **Objectif Immédiat**
Remplacer le provider principal par KIMI (Moonshot) en gardant Claude comme expert/validation, avec DeepSeek en fallback.

## 📋 **Étapes Concrètes (2-3 jours max)**

### **Jour 1: Setup & Client KIMI**

#### 1.1. Créer le client KIMI
```
Backend/Prod/clients/kimi_client.py
```

```python
# Backend/Prod/clients/kimi_client.py
import os
from typing import Dict, Any, Optional
import aiohttp
from datetime import datetime

class KimiClient:
    """Client pour l'API Moonshot (KIMI)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("MOONSHOT_API_KEY")
        self.base_url = "https://api.moonshot.cn/v1"
        self.models = {
            "kimi-v1": "moonshot-v1-8k",
            "kimi-v1-32k": "moonshot-v1-32k",
            "kimi-v1-128k": "moonshot-v1-128k",
            "kimi-2.5": "moonshot-v2-128k",  # Le plus récent
        }
        self.session = None
        
    async def initialize(self):
        """Initialisation asynchrone"""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
    
    async def generate(
        self,
        prompt: str,
        model: str = "kimi-2.5",
        temperature: float = 0.3,
        max_tokens: int = 4000,
        **kwargs
    ) -> Dict[str, Any]:
        """Appel à l'API KIMI"""
        
        if not self.session:
            await self.initialize()
        
        actual_model = self.models.get(model, model)
        
        payload = {
            "model": actual_model,
            "messages": [
                {"role": "system", "content": "Tu es un expert en développement logiciel."},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    return {
                        "text": data["choices"][0]["message"]["content"],
                        "usage": data.get("usage", {}),
                        "model": actual_model
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"KIMI API error {response.status}: {error_text}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"KIMI connection error: {e}")
    
    async def close(self):
        """Nettoyage"""
        if self.session:
            await self.session.close()

# Singleton pour usage global
_kimi_client = None

async def get_kimi_client():
    """Factory pour obtenir le client KIMI"""
    global _kimi_client
    if _kimi_client is None:
        _kimi_client = KimiClient()
        await _kimi_client.initialize()
    return _kimi_client
```

#### 1.2. Configurer l'API Key
```bash
# Dans ton .env
MOONSHOT_API_KEY=sk-votre-clé-kimi-ici

# Dans Backend/Prod/config.py
KIMI_CONFIG = {
    "enabled": True,
    "default_model": "kimi-2.5",
    "fallback_model": "kimi-v1-128k",
    "max_retries": 3,
    "timeout": 120
}
```

#### 1.3. Tester le client
```
Backend/Prod/tests/test_kimi_client.py
```

```python
# Test immédiat
async def test_kimi():
    client = KimiClient()
    await client.initialize()
    
    response = await client.generate(
        prompt="Écris une fonction Python qui calcule Fibonacci",
        model="kimi-2.5",
        temperature=0.1
    )
    
    print("✅ KIMI fonctionne!")
    print(response["text"])
    await client.close()
```

### **Jour 2: Intégration dans AgentRouter**

#### 2.1. Modifier AgentRouter
```
Backend/Prod/core/agent_router.py
```

```python
# Ajouter KIMI comme provider principal
class AgentRouter:
    def __init__(self):
        self.providers = {
            "kimi": {
                "client": None,  # Lazy loading
                "priority": 1,
                "models": {
                    "FAST": "kimi-2.5",
                    "BUILD": "kimi-2.5",
                    "DOUBLE-CHECK": "kimi-2.5"
                },
                "cost_per_token": 0.000002,  # ~$2/million tokens
                "rate_limit": 100  # requests/minute
            },
            "claude": {
                "client": ClaudeClient(),
                "priority": 2,
                "role": "expert_validation",
                "cost_per_token": 0.000015  # ~$15/million tokens
            },
            "deepseek": {
                "client": DeepSeekClient(),
                "priority": 3,
                "role": "fallback",
                "cost_per_token": 0.00000014  # ~$0.14/million tokens
            },
            "groq": {
                "client": GroqClient(),
                "priority": 4,
                "role": "ultra_fast",
                "cost_per_token": 0.00000079  # ~$0.79/million tokens
            }
        }
        
        # Nouvelle stratégie: KIMI first
        self.routing_strategy = {
            "FAST": ["kimi", "groq", "deepseek"],
            "BUILD": ["kimi", "claude", "deepseek"],
            "DOUBLE-CHECK": ["claude", "kimi"],  # Claude pour validation rigoureuse
            "SURGICAL_EDIT": ["kimi", "deepseek"]
        }
    
    async def get_provider(self, mode: str, step_complexity: str = "medium"):
        """Retourne le provider optimal pour le mode"""
        strategy = self.routing_strategy.get(mode, ["kimi", "deepseek"])
        
        for provider_name in strategy:
            provider = self.providers[provider_name]
            
            # Initialisation lazy de KIMI
            if provider_name == "kimi" and provider["client"] is None:
                provider["client"] = await get_kimi_client()
            
            # Vérifier rate limits et disponibilité
            if await self.is_provider_available(provider_name):
                return provider
        
        # Fallback ultime
        return self.providers["deepseek"]
    
    async def generate_with_fallback(self, prompt: str, mode: str, **kwargs):
        """Génération avec fallback automatique"""
        providers_tried = []
        
        for provider_name in self.routing_strategy[mode]:
            try:
                provider = await self.get_provider_for_name(provider_name)
                
                print(f"🔄 Utilisation de {provider_name} pour mode {mode}")
                
                response = await provider["client"].generate(
                    prompt=prompt,
                    model=provider["models"].get(mode, provider["default_model"]),
                    **kwargs
                )
                
                # Log de l'usage
                await self.log_usage(provider_name, response.get("usage", {}))
                
                return {
                    **response,
                    "provider": provider_name,
                    "fallback_used": len(providers_tried) > 0
                }
                
            except Exception as e:
                print(f"❌ {provider_name} a échoué: {e}")
                providers_tried.append(provider_name)
                continue
        
        raise Exception(f"Tous les providers ont échoué: {providers_tried}")
```

#### 2.2. Adapter les prompts pour KIMI
```
Backend/Prod/prompts/kimi_prompts.py
```

```python
# Prompts optimisés pour KIMI
KIMI_PROMPTS = {
    "FAST": """Tu es un assistant de code rapide et concis.
Tâche: {task}
Code existant: {context}
Réponds uniquement avec le code nécessaire, sans explications.""",
    
    "BUILD": """Tu es un ingénieur logiciel senior.
Tâche: {task}
Contexte: {context}
Instructions:
1. Écris du code production-ready
2. Inclus les erreurs handling
3. Documente les fonctions importantes
4. Suis les patterns du codebase
5. Optimise la performance""",
    
    "VALIDATION": """Tu es un expert en review de code.
Code à valider: {code}
Critères:
1. Sécurité
2. Performance
3. Maintenabilité
4. Respect des conventions
Retourne: [VALID|INVALID] + explication concise"""
}
```

### **Jour 3: Migration des Workflows**

#### 3.1. Modifier les workflows existants
```
Backend/Prod/workflows/prod_workflow.py
```

```python
class ProdWorkflow(BaseWorkflow):
    async def execute_step(self, step):
        """Exécute un step avec KIMI comme principal"""
        
        # Construction du prompt optimisé pour KIMI
        prompt = self.build_kimi_prompt(step)
        
        try:
            # Essayer KIMI d'abord
            response = await self.agent_router.generate_with_fallback(
                prompt=prompt,
                mode="BUILD",
                temperature=0.2,
                max_tokens=self.calculate_token_budget(step)
            )
            
            step_result = StepResult(
                content=response["text"],
                provider=response["provider"],
                tokens_used=response["usage"].get("total_tokens", 0),
                cost=self.calculate_cost(response),
                fallback_used=response.get("fallback_used", False)
            )
            
            # Si fallback utilisé, logger pour analyse
            if step_result.fallback_used:
                await self.log_fallback_event(step, step_result.provider)
            
            return step_result
            
        except Exception as e:
            print(f"❌ Échec sur le step {step.id}: {e}")
            raise
```

#### 3.2. Mettre à jour la configuration par défaut
```
config/default_config.yaml
```

```yaml
# Configuration par défaut avec KIMI comme principal
default_providers:
  primary: "kimi"
  validation: "claude"
  fallback: "deepseek"
  fast: "groq"

provider_settings:
  kimi:
    enabled: true
    default_model: "kimi-2.5"
    max_tokens_per_request: 8000
    temperature:
      FAST: 0.3
      BUILD: 0.2
      VALIDATION: 0.1
    retry_policy:
      max_retries: 3
      backoff_factor: 2
  
  claude:
    enabled: true
    use_for: ["validation", "complex_reasoning"]
    max_tokens_per_request: 4000
  
  deepseek:
    enabled: true
    use_for: ["fallback", "large_context"]
    max_tokens_per_request: 32000
```

### **Phase de Testing (2 jours)**

#### 4.1. Script de migration
```
scripts/migrate_to_kimi.py
```

```python
#!/usr/bin/env python3
"""
Script de migration vers KIMI - Test progressif
"""

import asyncio
import json
from datetime import datetime

class KimiMigrationTester:
    def __init__(self):
        self.results = []
        self.test_cases = [
            {
                "name": "Simple function",
                "prompt": "Write a Python function to reverse a string",
                "expected": "def reverse_string"
            },
            {
                "name": "Bug fix",
                "prompt": "Fix this bug: [code with bug]",
                "expected": "fixed_code"
            },
            {
                "name": "Refactoring",
                "prompt": "Refactor this code for better performance",
                "expected": "refactored"
            }
        ]
    
    async def run_tests(self):
        """Exécute tous les tests"""
        print("🧪 Début des tests KIMI...")
        
        for test in self.test_cases:
            print(f"\nTest: {test['name']}")
            
            # Test avec KIMI
            kimi_result = await self.test_with_kimi(test["prompt"])
            
            # Test avec ancien provider (pour comparaison)
            old_result = await self.test_with_old_provider(test["prompt"])
            
            # Comparaison
            comparison = self.compare_results(kimi_result, old_result)
            
            self.results.append({
                "test": test["name"],
                "kimi": kimi_result,
                "old": old_result,
                "comparison": comparison,
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"  KIMI: {comparison['verdict']}")
            print(f"  Temps: {comparison['time_diff']:.2f}s")
            print(f"  Coût: ${comparison['cost_diff']:.6f}")
        
        # Générer rapport
        self.generate_report()
        
    async def test_with_kimi(self, prompt):
        """Test avec le nouveau provider KIMI"""
        # Implémentation
        pass
    
    async def test_with_old_provider(self, prompt):
        """Test avec l'ancien provider"""
        # Implémentation
        pass

async def main():
    tester = KimiMigrationTester()
    await tester.run_tests()
    
    print("\n✅ Migration test terminée!")
    print("Vérifiez le rapport: migration_report.json")

if __name__ == "__main__":
    asyncio.run(main())
```

#### 4.2. Dashboard de monitoring
```
Backend/Prod/monitoring/kimi_monitor.py
```

```python
class KimiMonitor:
    """Monitor pour KIMI provider"""
    
    METRICS = [
        "response_time",
        "success_rate", 
        "tokens_per_request",
        "cost_per_day",
        "fallback_rate"
    ]
    
    async def compare_providers_week(self):
        """Compare KIMI vs ancien provider sur une semaine"""
        
        # Données KIMI (nouveau)
        kimi_stats = await self.get_provider_stats("kimi", days=7)
        
        # Données ancien provider
        old_stats = await self.get_provider_stats("previous", days=7)
        
        comparison = {
            "cost_saving": (old_stats["total_cost"] - kimi_stats["total_cost"]) / old_stats["total_cost"] * 100,
            "speed_change": (old_stats["avg_response_time"] - kimi_stats["avg_response_time"]) / old_stats["avg_response_time"] * 100,
            "success_rate_change": kimi_stats["success_rate"] - old_stats["success_rate"],
            "tokens_efficiency": kimi_stats["tokens_per_task"] / old_stats["tokens_per_task"]
        }
        
        return comparison
```

### **Checklist de Migration**

```markdown
## ✅ Checklist Migration KIMI

### Phase 1: Setup (Jour 1)
- [ ] Créer `kimi_client.py`
- [ ] Obtenir clé API Moonshot
- [ ] Tester la connexion
- [ ] Ajouter au .env

### Phase 2: Intégration (Jour 2)
- [ ] Modifier `agent_router.py`
- [ ] Implémenter stratégie KIMI-first
- [ ] Ajouter fallback
- [ ] Configurer les prompts KIMI

### Phase 3: Migration (Jour 3)
- [ ] Modifier `prod_workflow.py`
- [ ] Modifier `proto_workflow.py`
- [ ] Mettre à jour config par défaut
- [ ] Tester les workflows

### Phase 4: Testing (Jour 4-5)
- [ ] Exécuter script de migration
- [ ] Comparer résultats
- [ ] Valider qualité
- [ ] Ajuster température/tokens

### Phase 5: Go Live (Jour 6)
- [ ] Activer KIMI en prod
- [ ] Monitorer 24h
- [ ] Ajuster rate limits
- [ ] Documenter changements
```

### **Commandes CLI pour la Migration**

```bash
# 1. Tester la connexion KIMI
python -m Backend.Prod.clients.test_kimi

# 2. Exécuter les tests de migration
python scripts/migrate_to_kimi.py --full

# 3. Activer KIMI progressivement
aetherflow --enable-kimi 25   # 25% du traffic d'abord
aetherflow --enable-kimi 50   # 50%
aetherflow --enable-kimi 100  # 100%

# 4. Monitorer la migration
aetherflow monitor providers --compare
aetherflow monitor costs --days 7
aetherflow monitor quality --provider kimi
```

### **Fichiers à Modifier/Créer**

```
Backend/Prod/
├── clients/
│   ├── kimi_client.py          # NOUVEAU
│   └── __init__.py             # Ajouter KimiClient
├── core/
│   └── agent_router.py         # MODIFIER (stratégie KIMI)
├── prompts/
│   └── kimi_prompts.py         # NOUVEAU
├── workflows/
│   ├── prod_workflow.py        # MODIFIER
│   └── proto_workflow.py       # MODIFIER
└── config/
    └── default_config.yaml     # MODIFIER

scripts/
├── migrate_to_kimi.py          # NOUVEAU
└── test_kimi_connection.py     # NOUVEAU

tests/
└── test_kimi_integration.py    # NOUVEAU
```

### **Metrics à Surveiller**

```python
# Après migration, surveiller:
METRICS_TO_WATCH = {
    "success_rate": "> 90%",          # Taux de succès
    "avg_response_time": "< 5s",      # Temps de réponse
    "cost_per_task": "< $0.001",      # Coût par tâche
    "fallback_rate": "< 10%",         # Taux de fallback
    "token_efficiency": "> 0.8",      # Tokens utiles/totaux
}
```

## 🎯 **Priorité Absolue**

**Commence par ça** (aujourd'hui même):

1. **Créer `kimi_client.py`** (30 minutes)
2. **Tester la connexion** (15 minutes)
3. **Modifier `agent_router.py`** (1 heure)

En 2 heures, tu auras KIMI qui fonctionne en mode test. Le reste, tu peux l'ajouter progressivement.

**C'est clair maintenant ?** La migration vers KIMI est simple et directe. Tu veux que je détaille une étape spécifique ?