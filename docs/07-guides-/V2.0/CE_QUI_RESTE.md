# Ce Qui Reste à Faire - État Actuel

**Date** : 26 janvier 2025  
**Dernière mise à jour** : Après Étape 9 (Réduction Latence API)

---

## ✅ Ce Qui Vient d'Être Fait (Cette Session)

1. ✅ **Cache PageIndex avec hash invalidation** : 57x speedup mesuré (0.57s → 0.01s)
2. ✅ **Gemini 2.5 Flash** : Modèle mis à jour dans settings
3. ✅ **Prompt Caching infrastructure** : Module créé et intégré

---

## 📋 Ce Qui Reste à Faire

### 🔴 **Priorité Haute** (À faire maintenant)

#### 1. **Étape 6 : Améliorer Scripts de Benchmarking** 🟡 EN COURS

**Statut** : Partiellement fait, reste à compléter

**Ce qui est fait** :
- ✅ `benchmark_comprehensive.py` créé avec métriques étendues
- ✅ `run_benchmark_suite.py` créé pour comparaisons
- ✅ `README_BENCHMARK.md` documentation créée
- ✅ Métriques de latence (TTFT, TTR) ajoutées à `StepMetrics`

**Ce qui reste** :
- ⏳ Scripts spécifiques pour chaque optimisation :
  - ⏳ `scripts/benchmark_prompt_cache.py` : Tests spécifiques prompt caching
  - ⏳ `scripts/benchmark_slm_local.py` : Tests spécifiques SLM locaux
  - ⏳ `scripts/benchmark_speculative.py` : Tests spécifiques speculative decoding
  - ⏳ `scripts/benchmark_semantic_cache.py` : Tests spécifiques cache sémantique
- ⏳ Métriques de qualité : taux de code fonctionnel du premier coup
- ⏳ Graphiques : TTFT reduction, cache hit rate, speedup factor
- ⏳ Graphiques : Temps par provider, Coût par provider

**Impact** : Nécessaire pour mesurer les gains réels des optimisations

---

#### 2. **Étape 9 : Réduction Latence API** (Phase 3) ⏳ PARTIELLEMENT FAIT

**Ce qui est fait** :
- ✅ **Prompt Caching** : Infrastructure complète (module + intégration)
  - Module `PromptCache` créé
  - Intégré dans `AgentRouter` et tous les clients
  - Support DeepSeek, Gemini, Groq, Codestral
  - Stats trackées automatiquement

**Ce qui reste** :
- ❌ **SLM Locaux** : **ANNULÉ - Contrainte technique**
  - **Raison** : Machine i7 4 cœurs (insuffisant pour SLM locaux)
  - **Alternative** : ✅ **Groq déjà intégré** (latence 1-3s, équivalent SLM local)
  - **Note** : Groq remplace efficacement SLM local sans ressources système
  
- ⏳ **Speculative Decoding** (Semaine 3-6) :
  - Implémentation avec un modèle draft (Gemini Flash)
  - Mesure speculative accept rate
  - Optimisation pour réduire TTFT
  
- ⏳ **Cache Sémantique** (Continu) :
  - Cache des réponses similaires (embedding-based)
  - Réduction appels API redondants
  - Mesure cache hit rate sémantique
  
- ⏳ **WebSockets / Persistent Connections** (Continu) :
  - Connexions persistantes pour réduire overhead réseau
  - Pool de connexions réutilisables
  - Mesure réduction latence réseau

**Impact** : -70% latence totale estimée (selon proposition)

---

### 🟡 **Priorité Moyenne** (Optionnel, peut être ajouté plus tard)

#### 3. **BM25 Pre-filter pour RAG** ⏳ OPTIONNEL

**Description** : Utiliser BM25 avant PageIndex pour filtrer top-5 candidats

**Ce qui reste** :
- ⏳ Installer `rank-bm25` : `pip install rank-bm25`
- ⏳ Ajouter pre-filter dans `PageIndexRetriever._retrieve()`
- ⏳ Tester précision (ne doit pas dégrader les résultats)

**Gain estimé** : -40% latence sur retrieval (en plus du cache déjà fait)

**Impact** : Modéré (cache tree déjà fait -75% latence)

---

#### 4. **Étape 10 : Modes d'Exécution** (Phase 4 - Évolutions Futures) 🔮

**Description** : Routage dynamique avec modes explicites (FAST, BUILD, DOUBLE-CHECK)

**Prérequis** :
- ✅ RAG PageIndex (fait)
- ⏳ Vérification robuste (à améliorer)

**Ce qui reste** :
- ⏳ Implémenter modes dans `AgentRouter`
- ⏳ Logique de routage par mode
- ⏳ Tests et benchmarks par mode

**Impact** : Amélioration UX et contrôle utilisateur

**Note** : Peut être différé (architecture actuelle suffisante)

---

## 📊 Récapitulatif par Priorité

### 🔴 **À Faire Maintenant**

1. **Compléter Étape 6** : Scripts benchmarking spécifiques + graphiques
2. **Continuer Étape 9** : Speculative Decoding, Cache Sémantique, WebSockets
   - ❌ SLM locaux retirés (contrainte technique - utiliser Groq à la place)

### 🟡 **Optionnel / Plus Tard**

3. **BM25 Pre-filter** : Si besoin de réduire encore la latence RAG
4. **Modes d'Exécution** : Phase 4, peut être différé

---

## 🎯 Prochaine Étape Recommandée

**Option 1 : Compléter Benchmarking (Étape 6)**
- Créer les scripts spécifiques pour chaque optimisation
- Ajouter graphiques et métriques de qualité
- Permet de mesurer les gains réels

**Option 2 : Continuer Latence API (Étape 9)**
- Implémenter SLM locaux (gain immédiat pour tâches simples)
- Puis Speculative Decoding (gain TTFT)
- Puis Cache Sémantique (réduction appels API)

**Option 3 : BM25 Pre-filter**
- Quick win si besoin de réduire encore latence RAG
- ~1-2h d'implémentation

---

## ✅ Ce Qui Est Déjà Fait (Rappel)

- ✅ Phase 1 & 2 : Architecture complète (6/9 étapes)
- ✅ Étape 7 : Parallélisation
- ✅ Étape 8 : RAG PageIndex (avec cache)
- ✅ Prompt Caching : Infrastructure complète
- ✅ Cache PageIndex : 57x speedup
- ✅ Gemini 2.5 Flash : Modèle mis à jour

---

## 📈 Progression Globale

**Phase 1 & 2** : ✅ **100% terminée** (6/6 étapes)  
**Phase 3** : ⏳ **~30% terminée** (Prompt Caching fait, reste Speculative/Semantic/WebSockets - SLM locaux annulés)  
**Phase 4** : 🔮 **0% terminée** (Modes d'Exécution - futur)

**Total** : **~70% du roadmap principal terminé**
