# Smart Routing - Documentation

## Overview

Le système de **Smart Routing** pour AetherFlow est une évolution majeure du routage des requêtes LLM. Il remplace le routage simple basé sur le mode d'exécution par un système intelligent qui :

1. **Estime la taille du contexte** avant exécution
2. **Route vers le meilleur provider** en fonction de cette taille
3. **Active le fallback automatique** cross-provider en cas d'échec
4. **Découpe automatiquement** les steps trop lourds
5. **Génère par sections** les fichiers volumineux

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         AgentRouter                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │ SmartContextRouter │  │ FallbackCascade  │  │ StepChunker  │  │
│  └────────┬────────┘  └────────┬─────────┘  └──────┬───────┘  │
│           │                    │                   │          │
│           ▼                    ▼                   ▼          │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    SectionGenerator                     │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Composants

### 1. SmartContextRouter

**Fichier** : `Backend/Prod/models/smart_context_router.py`

Route intelligemment les requêtes selon la taille du contexte :

| Contexte | Provider | Raison |
|----------|----------|--------|
| < 10k tokens | Groq | Rapide, gratuit |
| 10k - 50k tokens | DeepSeek | Bon rapport qualité/coût |
| > 50k tokens | Gemini | 1M+ contexte, pas de timeout |
| Vision/Images | Gemini | Multimodal natif |

**Utilisation** :
```python
from Backend.Prod.models.smart_context_router import SmartContextRouter

router = SmartContextRouter(available_providers=["groq", "deepseek", "gemini"])
decision = router.route_step(step, context="...", execution_mode="BUILD")

print(decision.primary_provider)  # "deepseek"
print(decision.estimated_tokens)  # 25000
print(decision.should_chunk)      # False
```

### 2. ProviderFallbackCascade

**Fichier** : `Backend/Prod/models/provider_fallback_cascade.py`

Cascade de fallback cross-provider avec retry intelligent :

```python
PROVIDER_CASCADE = ["deepseek", "gemini", "codestral"]
```

**Gestion des erreurs** :
- **429 Rate Limit** → Retry avec backoff exponentiel
- **413 Token Limit** → Passe au provider suivant immédiatement
- **5xx Server Error** → Retry puis fallback
- **Timeout** → Retry avec délai augmenté
- **Circuit Breaker** → Ouvre le circuit après 5 échecs

**Utilisation** :
```python
from Backend.Prod.models.provider_fallback_cascade import ProviderFallbackCascade

cascade = ProviderFallbackCascade(clients={"groq": groq_client, ...})

result = await cascade.execute(
    fallback_chain=["groq", "gemini", "deepseek"],
    execute_fn=lambda client: client.generate(prompt),
    context_size=25000
)

if result.success:
    print(f"Success with {result.provider_used}")
    print(f"Fallback used: {result.fallback_used}")
```

### 3. StepChunker

**Fichier** : `Backend/Prod/models/step_chunker.py`

Découpage automatique des steps "lourds" selon les critères :
- `estimated_tokens > 30000`
- `input_files > 3`
- `code_generation` avec > 200 lignes attendues

**Stratégies de découpage** :
- **File-based** : Par fichiers cibles (quand plusieurs fichiers)
- **Section-based** : Par sections de code (imports, classes, etc.)
- **Logic-based** : Par composants logiques
- **Iterative** : Découpe itérative pour les cas complexes

**Utilisation** :
```python
from Backend.Prod.models.step_chunker import StepChunker

chunker = StepChunker()
should_chunk, reason = chunker.analyze_step(step, estimated_tokens=40000)

if should_chunk:
    strategy = chunker.chunk_step(step, estimated_tokens)
    
    for chunk in strategy.chunks:
        # Execute each chunk
        result = await execute_chunk(chunk)
    
    # Merge results
    final_output = chunker.merge_chunk_results(strategy, chunk_results)
```

### 4. SectionGenerator

**Fichier** : `Backend/Prod/models/section_generator.py`

Génération incrémentale par sections pour les fichiers volumineux :

**Ordre des sections** (Python) :
1. IMPORTS
2. CONSTANTS
3. TYPES
4. UTILITIES
5. CLASSES
6. FUNCTIONS
7. MAIN

**Utilisation** :
```python
from Backend.Prod.models.section_generator import SectionGenerator

generator = SectionGenerator()
plan = generator.create_plan(
    description="Create a complex API module",
    language="python"
)

final_code, results = await generator.generate_all_sections(
    plan=plan,
    generate_fn=lambda prompt: client.generate(prompt),
    on_progress=lambda c, t, n: print(f"{c}/{t}: {n}")
)
```

## Intégration avec AgentRouter

Le `AgentRouter` utilise automatiquement ces composants :

```python
from Backend.Prod.models.agent_router import AgentRouter

router = AgentRouter(execution_mode="BUILD")

# Tout est automatique :
# 1. Estimation de la taille
# 2. Sélection du provider
# 3. Fallback si échec
# 4. Chunking si nécessaire
# 5. Génération par sections si applicable

result = await router.execute_step(step, context="...")
```

## Configuration

### Seuils de routing

```python
# SmartContextRouter
THRESHOLD_FAST = 10000      # < 10k: Groq
THRESHOLD_BALANCED = 50000  # 10k-50k: DeepSeek
# > 50k: Gemini

# StepChunker
CHUNK_THRESHOLD = 30000
MAX_FILES_BEFORE_CHUNKING = 3
MAX_EXPECTED_LINES = 200
```

### Configuration Cascade

```python
from Backend.Prod.models.provider_fallback_cascade import CascadeConfig

config = CascadeConfig(
    max_attempts_per_provider=3,
    base_retry_delay=1.0,
    max_retry_delay=30.0,
    exponential_base=2.0,
    enable_circuit_breaker=True,
    circuit_breaker_threshold=5,
    circuit_breaker_timeout=60.0
)
```

## Statistiques et Monitoring

```python
# Récupérer les stats de routing
stats = router.get_routing_stats()

print(stats)
# {
#     "available_providers": ["groq", "deepseek", "gemini"],
#     "execution_mode": "BUILD",
#     "fallback_stats": {
#         "total_attempts": 45,
#         "successful": 42,
#         "failed": 3,
#         "success_rate": 0.93,
#         "by_provider": {...},
#         "by_failure_type": {...}
#     }
# }
```

## Exemple Complet

```python
import asyncio
from Backend.Prod.models.agent_router import AgentRouter
from Backend.Prod.models.plan_reader import Step

async def main():
    # Initialize router
    router = AgentRouter(execution_mode="BUILD")
    
    # Create a large step
    step = Step({
        "id": "large_generation",
        "description": "Create a full web application with models, views, templates, and API endpoints",
        "type": "code_generation",
        "complexity": 0.9,
        "estimated_tokens": 40000,
        "dependencies": [],
        "validation_criteria": [],
        "context": {
            "language": "python",
            "framework": "fastapi",
            "files": ["models.py", "views.py", "api.py", "templates/"]
        }
    })
    
    # Execute with automatic smart routing
    result = await router.execute_step(
        step=step,
        context="Additional context here"
    )
    
    if result.success:
        print(f"✓ Generated {result.tokens_used} tokens")
        print(f"✓ Cost: ${result.cost_usd:.4f}")
        print(f"✓ Time: {result.execution_time_ms:.0f}ms")
    else:
        print(f"✗ Failed: {result.error}")
    
    # Get routing stats
    stats = router.get_routing_stats()
    print(f"\nFallback rate: {stats['fallback_stats']['success_rate']:.1%}")
    
    await router.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Tests

```bash
# Run smart routing tests
python3 Backend/Prod/tests/test_smart_routing.py
```

## Migration depuis l'ancien système

L'ancien système utilisait uniquement `ExecutionRouter` avec des règles fixes. Le nouveau système est **rétrocompatible** :

```python
# Ancien code (fonctionne toujours)
from Backend.Prod.models.execution_router import ExecutionRouter
router = ExecutionRouter()
provider = router.get_provider_for_step(step, "BUILD")

# Nouveau code (recommandé)
from Backend.Prod.models.agent_router import AgentRouter
router = AgentRouter(execution_mode="BUILD")
result = await router.execute_step(step, context)
```

## Troubleshooting

### Provider toujours en fallback

Vérifiez le circuit breaker :
```python
stats = router.get_routing_stats()
print(stats["fallback_stats"]["open_circuits"])
```

### Chunking trop agressif

Ajustez les seuils :
```python
router.context_router.CHUNK_THRESHOLD = 40000  # Augmenter le seuil
```

### Timeouts fréquents

Augmentez le timeout par défaut :
```python
from Backend.Prod.models.provider_fallback_cascade import CascadeConfig

config = CascadeConfig(default_timeout=180.0)
cascade = ProviderFallbackCascade(clients=clients, config=config)
```

## Roadmap Future

- [ ] Adaptive thresholds based on success rates
- [ ] Predictive token estimation using ML
- [ ] Automatic provider discovery and benchmarking
- [ ] Cost optimization with spot/preemptible instances
- [ ] Multi-region fallback for lower latency
