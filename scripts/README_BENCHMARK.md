# Scripts de Benchmarking AETHERFLOW

**Date** : 26 janvier 2025

---

## 📊 Scripts Disponibles

### 1. `benchmark.py` - Benchmark de Base

Script de benchmark simple avec métriques de base.

**Usage** :
```bash
python scripts/benchmark.py --plan path/to/plan.json --output output/dir
```

**Génère** :
- `benchmark_report.md` : Rapport markdown
- `benchmark_data.json` : Données JSON

---

### 2. `benchmark_comprehensive.py` - Benchmark Complet ⭐ NOUVEAU

Script de benchmark amélioré avec :
- ✅ Métriques de latence (TTFT, TTR, queue latency, network overhead)
- ✅ Comparaison par provider
- ✅ Comparaison par type de tâche
- ✅ Métriques de cache (si disponibles)
- ✅ Tableaux récapitulatifs dans le terminal

**Usage** :
```bash
python scripts/benchmark_comprehensive.py --plan path/to/plan.json --output output/dir
```

**Génère** :
- `benchmark_report.md` : Rapport markdown complet avec analyses
- `benchmark_data.json` : Données JSON détaillées

**Exemple** :
```bash
python scripts/benchmark_comprehensive.py \
  --plan Backend/Notebooks/benchmark_tasks/task_parallelization.json \
  --output output/benchmark_comprehensive
```

---

### 3. `run_benchmark_suite.py` - Suite de Benchmarks ⭐ NOUVEAU

Script pour exécuter plusieurs benchmarks et comparer les résultats.

**Usage** :
```bash
python scripts/run_benchmark_suite.py \
  --plans plan1.json plan2.json plan3.json \
  --output output/benchmark_suite
```

**Génère** :
- `comparison_report.md` : Rapport de comparaison
- `comparison_data.json` : Données de comparaison JSON
- Un répertoire par plan avec ses résultats individuels

**Exemple** :
```bash
python scripts/run_benchmark_suite.py \
  --plans \
    Backend/Notebooks/benchmark_tasks/task_parallelization.json \
    Backend/Notebooks/benchmark_tasks/task_test_parallelization.json \
  --output output/benchmark_suite
```

---

## 📈 Métriques Collectées

### Métriques de Base
- ✅ Temps d'exécution total
- ✅ Coût total
- ✅ Tokens utilisés (input/output)
- ✅ Taux de succès
- ✅ Détails par étape

### Métriques de Latence (Nouvelles)
- ⏳ **TTFT** (Time To First Token) - Temps avant premier token
- ⏳ **TTR** (Time To Response) - Temps total de réponse
- ⏳ **Queue Latency** - Temps d'attente en file
- ⏳ **Network Overhead** - Overhead réseau (DNS + TCP + TLS)

*Note* : Ces métriques seront disponibles une fois les optimisations de latence implémentées.

### Métriques de Cache (Futures)
- ⏳ **Cache Hit Rate** - Taux de hits du cache prompt
- ⏳ **Cache Read Cost** - Coût des lectures cache

### Métriques de Qualité (Futures)
- ⏳ **Code Quality Score** - Score qualité code généré
- ⏳ **First Try Success Rate** - % code fonctionnel du premier coup

---

## 🔍 Comparaisons Disponibles

### Par Provider
Le script `benchmark_comprehensive.py` compare automatiquement :
- Temps moyen par provider
- Coût moyen par provider
- Tokens moyens par provider
- Taux de succès par provider
- TTFT moyen par provider (si disponible)

### Par Type de Tâche
Comparaison automatique pour :
- `code_generation`
- `refactoring`
- `analysis`

### Avant/Après Optimisations
Utilisez `run_benchmark_suite.py` pour comparer :
- Baseline vs Optimisé
- Avant/après parallélisation
- Avant/après prompt caching
- Avant/après SLM locaux

---

## 📋 Exemples d'Utilisation

### Benchmark Simple
```bash
python scripts/benchmark.py \
  --plan Backend/Notebooks/benchmark_tasks/task_test_parallelization.json \
  --output output/benchmark_simple
```

### Benchmark Complet avec Analyses
```bash
python scripts/benchmark_comprehensive.py \
  --plan Backend/Notebooks/benchmark_tasks/task_test_parallelization.json \
  --output output/benchmark_comprehensive
```

### Suite de Benchmarks
```bash
python scripts/run_benchmark_suite.py \
  --plans \
    Backend/Notebooks/benchmark_tasks/task_parallelization.json \
    Backend/Notebooks/benchmark_tasks/task_test_parallelization.json \
    Backend/Notebooks/benchmark_tasks/task_rag_pageindex.json \
  --output output/benchmark_suite
```

### Comparaison Baseline vs Optimisé
```bash
# Exécuter baseline
python scripts/run_benchmark_suite.py \
  --plans plan1.json plan2.json \
  --output output/baseline \
  --baseline-label baseline

# Exécuter optimisé (après optimisations)
python scripts/run_benchmark_suite.py \
  --plans plan1.json plan2.json \
  --output output/optimized \
  --optimized-label optimized

# Comparer manuellement les rapports générés
```

---

## 📊 Format des Rapports

### Rapport Markdown
Chaque script génère un rapport markdown avec :
- Métriques globales
- Performance (temps)
- Coûts
- Tokens
- Analyse par provider
- Analyse par type
- Détails par étape
- Questions pour Claude Code

### Données JSON
Les données JSON contiennent toutes les métriques détaillées pour :
- Analyse programmatique
- Génération de graphiques
- Comparaisons automatiques

---

## 🚀 Prochaines Étapes

### Court Terme
1. ✅ Scripts de base créés
2. ⏳ Tester avec plans existants
3. ⏳ Valider les métriques collectées

### Moyen Terme
1. ⏳ Ajouter génération de graphiques (matplotlib/plotly)
2. ⏳ Ajouter comparaisons automatiques avant/après
3. ⏳ Intégrer métriques de latence réelles (TTFT, TTR)

### Long Terme
1. ⏳ Scripts spécifiques par optimisation :
   - `benchmark_prompt_cache.py`
   - `benchmark_slm_local.py`
   - `benchmark_speculative.py`
   - `benchmark_semantic_cache.py`

---

## 📚 Références

- `/docs/guides/STRATEGIE_BENCHMARK_LATENCE.md` : Stratégie complète de benchmark
- `/docs/guides/PLAN_GENERAL_ROADMAP.md` : Étape 6 - Améliorer scripts benchmarking
- `/docs/guides/PRD AETHERFLOW.md` : Section métriques et surveillance

---

**Dernière mise à jour** : 26 janvier 2025
