# Stratégie de Benchmark pour Réduction Latence API

**Date** : 26 janvier 2025  
**Contexte** : Plan de réduction de la latence API nécessite une stratégie de benchmark adaptée

---

## 📊 Analyse du Plan de Réduction de Latence

### Techniques Proposées (par ordre de priorité)

1. **Prompt Caching** (Semaine 1-2)
   - Réduction TTFT estimée : **30-60%**
   - Cache hit rate cible : **>60%**
   - Coût : Cache reads = 0.1× prix input

2. **SLM Locaux** (Semaine 2-4)
   - Réduction appels externes : **20-40%**
   - Utilisation : Validation, formatage, linting

3. **Speculative Decoding** (Semaine 3-6)
   - Draft + Verify pattern
   - Mesure : Speculative accept rate

4. **Cache Sémantique Local** (Continu)
   - Redis + Vector DB
   - Déduplication réponses similaires

5. **WebSockets/Connexions Persistantes** (Continu)
   - Réduction overhead réseau

---

## 🎯 Métriques à Benchmarker (Nouvelles)

### Métriques Existantes (Déjà Mesurées)
- ✅ Temps d'exécution total
- ✅ Coût API
- ✅ Tokens utilisés
- ✅ Taux de succès

### Métriques Nouvelles à Ajouter

#### 1. Métriques de Latence Granulaire

| Métrique | Description | Cible | Priorité |
|----------|-------------|-------|----------|
| **TTFT (Time To First Token)** | Temps avant premier token | <2s | 🔴 Critique |
| **TTR (Time To Response)** | Temps total de réponse | <30s | 🔴 Critique |
| **Queue Latency** | Temps d'attente en file | <1s | 🟡 Moyenne |
| **Network Overhead** | Temps DNS + TCP + TLS | <500ms | 🟡 Moyenne |

#### 2. Métriques de Cache

| Métrique | Description | Cible | Priorité |
|----------|-------------|-------|----------|
| **Cache Hit Rate (Prompt)** | % requêtes utilisant cache | >60% | 🔴 Critique |
| **Cache Hit Rate (Sémantique)** | % réponses dédupliquées | >40% | 🟡 Moyenne |
| **Cache Read Cost** | Coût cache vs full generation | 0.1× | 🔴 Critique |
| **Cache TTL Effectiveness** | Durée optimale du cache | 5min-1h | 🟡 Moyenne |

#### 3. Métriques Speculative Decoding

| Métrique | Description | Cible | Priorité |
|----------|-------------|-------|----------|
| **Speculative Accept Rate** | % tokens/branches acceptés | >70% | 🔴 Critique |
| **Draft Model Speed** | Temps génération draft | <5s | 🟡 Moyenne |
| **Verify Model Speed** | Temps vérification | <10s | 🟡 Moyenne |
| **Speedup Factor** | Gain vs génération normale | >1.5× | 🔴 Critique |

#### 4. Métriques SLM Locaux

| Métrique | Description | Cible | Priorité |
|----------|-------------|-------|----------|
| **SLM Call Rate** | % appels routés localement | >30% | 🟡 Moyenne |
| **SLM Latency** | Temps réponse SLM local | <1s | 🟡 Moyenne |
| **Network Calls Saved** | Nombre appels évités | >20% | 🟡 Moyenne |
| **SLM Accuracy** | Taux succès vs cloud | >95% | 🔴 Critique |

---

## 📋 Suite au Plan : Prospective de Tests

### Phase 1 : Baseline (Avant Optimisations)

**Objectif** : Établir les métriques de référence

**Tests à Effectuer** :
1. **Benchmark Baseline** :
   - Exécuter 10 plans représentatifs
   - Mesurer : TTFT, TTR, coût, tokens, succès
   - Documenter : Temps moyen par provider, par type de tâche

2. **Analyse des Goulots d'Étranglement** :
   - Identifier où la latence est la plus élevée
   - Mesurer : Network overhead, queue latency, TTFT par provider
   - Documenter : Distribution des temps (p50, p95, p99)

**Livrables** :
- Rapport baseline avec métriques complètes
- Graphiques : Distribution TTFT, TTR par provider
- Identification des 3 principaux goulots d'étranglement

---

### Phase 2 : Prompt Caching (Semaine 1-2)

**Objectif** : Mesurer l'impact du prompt caching

**Tests à Effectuer** :
1. **Test Cache Hit** :
   - Exécuter 20 plans avec contexte réutilisable
   - Mesurer : TTFT avant/après cache, cache hit rate
   - Comparer : Coût avec/sans cache

2. **Test Cache Breakpoints** :
   - Varier les breakpoints de cache
   - Mesurer : Impact sur TTFT et coût
   - Identifier : Breakpoints optimaux

3. **Test Cache TTL** :
   - Tester TTL 5min vs 1h
   - Mesurer : Cache hit rate, coût, cohérence
   - Identifier : TTL optimal par type de contexte

**Métriques Clés** :
- **TTFT Reduction** : Cible 30-60%
- **Cache Hit Rate** : Cible >60%
- **Cost Reduction** : Cible 40-50% (cache reads = 0.1×)

**Livrables** :
- Rapport comparaison avant/après prompt caching
- Graphiques : TTFT reduction, cache hit rate over time
- Recommandations : Breakpoints et TTL optimaux

---

### Phase 3 : SLM Locaux (Semaine 2-4)

**Objectif** : Mesurer l'impact des SLM locaux

**Tests à Effectuer** :
1. **Test Routage SLM** :
   - Router 30% des appels vers SLM local
   - Mesurer : Latence SLM vs cloud, taux de succès
   - Comparer : Qualité des réponses

2. **Test Types de Tâches** :
   - Identifier quelles tâches peuvent être routées localement
   - Mesurer : Validation, formatage, linting
   - Documenter : Taux de succès par type

3. **Test Charge** :
   - Tester avec charge élevée (10+ requêtes parallèles)
   - Mesurer : Latence SLM sous charge
   - Comparer : SLM vs cloud sous charge

**Métriques Clés** :
- **SLM Call Rate** : Cible >30%
- **Network Calls Saved** : Cible >20%
- **SLM Accuracy** : Cible >95%

**Livrables** :
- Rapport comparaison SLM vs cloud
- Graphiques : Latence SLM, network calls saved
- Recommandations : Types de tâches à router localement

---

### Phase 4 : Speculative Decoding (Semaine 3-6)

**Objectif** : Mesurer l'impact du speculative decoding

**Tests à Effectuer** :
1. **Test Draft + Verify** :
   - Exécuter plans avec speculative decoding
   - Mesurer : Speculative accept rate, speedup factor
   - Comparer : Temps total vs génération normale

2. **Test Modèles Draft** :
   - Tester différents modèles draft (Qwen, Phi-4, Groq)
   - Mesurer : Accept rate, vitesse, coût
   - Identifier : Modèle draft optimal

3. **Test Branches Spéculatives** :
   - Tester 2-3 branches parallèles
   - Mesurer : Temps total, coût, qualité résultat final
   - Comparer : Branches vs génération séquentielle

**Métriques Clés** :
- **Speculative Accept Rate** : Cible >70%
- **Speedup Factor** : Cible >1.5×
- **Cost Efficiency** : Coût total acceptable vs gain temps

**Livrables** :
- Rapport comparaison speculative vs normal
- Graphiques : Accept rate, speedup factor
- Recommandations : Modèles et stratégies optimales

---

### Phase 5 : Cache Sémantique (Continu)

**Objectif** : Mesurer l'impact du cache sémantique

**Tests à Effectuer** :
1. **Test Similarité** :
   - Tester déduplication réponses similaires
   - Mesurer : Cache hit rate sémantique, qualité réponses
   - Comparer : Réponses dédupliquées vs générées

2. **Test Vector DB** :
   - Tester différents Vector DB (Milvus, Pinecone, Weaviate)
   - Mesurer : Latence recherche, précision, coût
   - Identifier : Solution optimale

**Métriques Clés** :
- **Cache Hit Rate (Sémantique)** : Cible >40%
- **Search Latency** : Cible <100ms
- **Similarity Threshold** : Identifier seuil optimal

---

### Phase 6 : WebSockets (Continu)

**Objectif** : Mesurer l'impact des connexions persistantes

**Tests à Effectuer** :
1. **Test Sessions Longues** :
   - Tester sessions avec WebSockets
   - Mesurer : Network overhead, TTFT amélioré
   - Comparer : WebSocket vs HTTP pour sessions longues

**Métriques Clés** :
- **Network Overhead Reduction** : Cible >30%
- **TTFT Improvement** : Cible >20%

---

## 🔧 Améliorations Nécessaires aux Scripts de Benchmark

### 1. Ajouter Métriques Granulaires

**Fichier** : `scripts/benchmark.py`

**Modifications** :
```python
# Ajouter mesure TTFT, TTR, queue latency
metrics = {
    "ttft_ms": [],  # Time to first token
    "ttr_ms": [],   # Time to response
    "queue_latency_ms": [],  # Queue wait time
    "network_overhead_ms": [],  # DNS + TCP + TLS
    "cache_hits": 0,  # Prompt cache hits
    "cache_misses": 0,
    "slm_calls": 0,  # SLM local calls
    "speculative_accept_rate": 0.0,  # Speculative decoding
}
```

### 2. Ajouter Comparaisons Avant/Après

**Fichier** : `scripts/run_benchmark_suite.py`

**Modifications** :
- Comparer métriques avant/après chaque optimisation
- Générer graphiques : TTFT reduction, cache hit rate, speedup factor
- Tableaux comparatifs : Performance par phase d'optimisation

### 3. Ajouter Tests Spécifiques par Optimisation

**Nouveaux Scripts** :
- `scripts/benchmark_prompt_cache.py` : Tests spécifiques prompt caching
- `scripts/benchmark_slm_local.py` : Tests spécifiques SLM locaux
- `scripts/benchmark_speculative.py` : Tests spécifiques speculative decoding
- `scripts/benchmark_semantic_cache.py` : Tests spécifiques cache sémantique

### 4. Ajouter Métriques de Qualité

**Nouvelles Métriques** :
- **Code Quality Score** : Score qualité code généré (linting, tests)
- **First Try Success Rate** : % code fonctionnel du premier coup
- **Correction Rate** : Nombre corrections nécessaires

---

## 📊 Plan de Benchmark Complet

### Structure des Tests

```
Phase 0: Baseline (Semaine 0)
├─ Benchmark 10 plans représentatifs
├─ Mesurer toutes métriques de base
└─ Identifier goulots d'étranglement

Phase 1: Prompt Caching (Semaine 1-2)
├─ Test cache hit rate
├─ Test cache breakpoints
├─ Test cache TTL
└─ Comparaison avant/après

Phase 2: SLM Locaux (Semaine 2-4)
├─ Test routage SLM
├─ Test types de tâches
├─ Test charge
└─ Comparaison SLM vs cloud

Phase 3: Speculative Decoding (Semaine 3-6)
├─ Test draft + verify
├─ Test modèles draft
├─ Test branches spéculatives
└─ Comparaison speculative vs normal

Phase 4: Cache Sémantique (Continu)
├─ Test similarité
├─ Test Vector DB
└─ Comparaison cache sémantique vs génération

Phase 5: WebSockets (Continu)
├─ Test sessions longues
└─ Comparaison WebSocket vs HTTP
```

### Fréquence des Benchmarks

- **Baseline** : 1 fois (avant optimisations)
- **Chaque Optimisation** : Avant/après + suivi continu
- **Rapport Global** : Mensuel avec toutes les métriques

---

## 🎯 Critères de Succès par Phase

### Phase 1 : Prompt Caching
- ✅ TTFT réduit de **30-60%**
- ✅ Cache hit rate **>60%**
- ✅ Coût réduit de **40-50%**

### Phase 2 : SLM Locaux
- ✅ **>30%** appels routés localement
- ✅ **>20%** appels réseau évités
- ✅ **>95%** précision SLM

### Phase 3 : Speculative Decoding
- ✅ Accept rate **>70%**
- ✅ Speedup factor **>1.5×**
- ✅ Coût total acceptable

### Phase 4 : Cache Sémantique
- ✅ Cache hit rate **>40%**
- ✅ Search latency **<100ms**

### Phase 5 : WebSockets
- ✅ Network overhead réduit de **>30%**
- ✅ TTFT amélioré de **>20%**

---

## 📈 Rapports à Générer

### 1. Rapport Baseline
- Métriques complètes avant optimisations
- Identification goulots d'étranglement
- Graphiques distribution temps

### 2. Rapport par Optimisation
- Comparaison avant/après
- Métriques spécifiques (cache hit rate, accept rate, etc.)
- Recommandations

### 3. Rapport Global Mensuel
- Évolution toutes métriques
- Comparaison toutes phases
- ROI calculé (temps gagné / coût)

---

## 🚀 Actions Immédiates

### Court Terme (Semaine 1)
1. **Instrumenter métriques** : TTFT, TTR, queue latency
2. **Créer baseline** : Exécuter 10 plans représentatifs
3. **Identifier goulots** : Analyser où la latence est la plus élevée

### Moyen Terme (Semaine 2-4)
1. **Ajouter tests prompt caching** : Scripts spécifiques
2. **Ajouter tests SLM** : Scripts spécifiques
3. **Générer rapports** : Comparaisons avant/après

### Long Terme (Semaine 3-6)
1. **Ajouter tests speculative** : Scripts spécifiques
2. **Ajouter tests cache sémantique** : Scripts spécifiques
3. **Automatiser** : Benchmarks continus avec rapports automatiques

---

**Dernière mise à jour** : 26 janvier 2025
