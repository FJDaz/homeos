# Tests Étape 9 - Guide de Lancement

**Date** : 26 janvier 2025  
**Statut** : ✅ **Prêt pour tests**  
**Référence** : Voir `ETAPE_9_REDUCTION_LATENCE.md` pour vue d'ensemble

---

## ✅ Implémentations Complétées

1. ✅ **Speculative Decoding** : Module créé et intégré
2. ✅ **Cache Sémantique** : Module créé et intégré  
3. ✅ **Connection Pooling** : Module créé (httpx gère déjà automatiquement)

---

## 🧪 Tests Disponibles

### **1. Test Speculative Decoding**

**Script** : `scripts/benchmark_speculative.py`

**Usage** :
```bash
python scripts/benchmark_speculative.py
```

**Ce qu'il teste** :
- Comparaison speculative vs normal execution
- Mesure accept rate, speedup factor
- Temps d'exécution comparatif
- Coût comparatif

**Résultats** : Sauvegardés dans `output/benchmark_speculative.json`

---

### **2. Test Cache Sémantique**

**Test manuel** :
```python
from Backend.Prod.cache import SemanticCache

cache = SemanticCache()

# Premier appel (cache MISS)
result1 = cache.get("Generate a REST API")
# None (pas de cache)

# Mettre en cache
cache.put("Generate a REST API", "def api(): ...")

# Deuxième appel similaire (cache HIT)
result2 = cache.get("Create a REST API endpoint")
# Retourne réponse cachée si similarité > 0.85

# Stats
stats = cache.get_stats()
print(f"Hit rate: {stats.cache_hit_rate:.1f}%")
```

---

### **3. Test Intégration Complète**

**Via Orchestrator** :
```python
from Backend.Prod.orchestrator import Orchestrator
from Backend.Prod.models.plan_reader import PlanReader

orchestrator = Orchestrator()
plan = PlanReader().read("path/to/plan.json")

# Exécuter plan (utilise automatiquement toutes les optimisations)
result = await orchestrator.execute_plan(plan)

# Vérifier métriques
print(f"Speculative enabled: {result.get('speculative_enabled')}")
print(f"Cache hits: {result.get('cache_hits')}")
```

---

## 📊 Métriques à Vérifier

### **Speculative Decoding** :
- `speculative_accept_rate` : Cible >70%
- `speculative_speedup_factor` : Cible >1.5x
- Temps réduit : -30-50% TTFT

### **Cache Sémantique** :
- `cache_hit_rate` : Cible >40%
- Tokens économisés
- Coût économisé

### **Connection Pooling** :
- `connection_reuse_rate` : Cible >80%
- Overhead réseau réduit : ~350ms par requête réutilisée

---

## ⚠️ Notes Importantes

1. **Premier lancement** : Le modèle d'embedding (`all-MiniLM-L6-v2`) se télécharge la première fois (~80MB)
   - Temps de chargement : ~10-30 secondes
   - Ensuite, chargement instantané depuis cache

2. **NumPy** : Nécessite `numpy<2` (déjà installé)

3. **Dépendances** :
   ```bash
   pip install sentence-transformers "numpy<2"
   ```

---

## 🚀 Lancement Rapide

```bash
# 1. Vérifier dépendances
pip install sentence-transformers "numpy<2"

# 2. Lancer benchmark speculative
python scripts/benchmark_speculative.py

# 3. Vérifier résultats
cat output/benchmark_speculative.json
```

---

## 📝 Résultats Attendus

**Speculative Decoding** :
- Speedup : 1.5x - 2x pour tâches longues
- Accept rate : 60-80% selon tâche
- Latence réduite : -30-50%

**Cache Sémantique** :
- Hit rate : 40-60% pour workflows répétitifs
- Latence cache hit : <10ms vs 2-5s API
- Coût économisé : 100% sur cache hits

---

## 🔗 Documentation

- Speculative Decoding : `/docs/guides/SPECULATIVE_DECODING.md`
- Cache Sémantique : `/docs/guides/CACHE_SEMANTIQUE.md`
- Connection Pooling : `/docs/guides/WEBSOCKETS_CONNECTION_POOL.md`
- Rapport complet : `/docs/guides/RAPPORT_ETAPE_9_COMPLET.md`
