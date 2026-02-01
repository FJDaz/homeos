# Speculative Decoding - Guide Technique

**Date** : 26 janvier 2025  
**Statut** : ✅ **IMPLÉMENTÉ**  
**Référence** : Voir `ETAPE_9_REDUCTION_LATENCE.md` pour vue d'ensemble

---

## 🎯 Objectif

Réduire le TTFT (Time To First Token) en utilisant un modèle draft rapide (Groq/Gemini Flash) pour générer des tokens, puis vérifier ces tokens en parallèle avec un modèle de qualité (DeepSeek/Gemini).

**Gain cible** : >70% speculative accept rate, >1.5x speedup factor

---

## 📋 Architecture

### **Draft + Verify Pattern**

1. **Draft Model** (rapide, économique) :
   - Groq ou Gemini Flash
   - Génère des tokens rapidement
   - Latence : 1-3s

2. **Verify Model** (qualité) :
   - DeepSeek ou Gemini
   - Vérifie/valide les tokens du draft
   - Qualité : 98%+

3. **Accept/Reject** :
   - Tokens acceptés → utilisés directement
   - Tokens rejetés → régénérés par verify model

---

## 🔧 Implémentation

### **Module** : `Backend/Prod/speculative/decoder.py`

**Classe principale** : `SpeculativeDecoder`

```python
from Backend.Prod.speculative import SpeculativeDecoder

decoder = SpeculativeDecoder(
    draft_client=groq_client,      # Fast model
    verify_client=deepseek_client, # Quality model
    draft_provider="groq",
    verify_provider="deepseek"
)

result = await decoder.decode(
    prompt="Generate a REST API...",
    max_tokens=2000
)
```

**Résultat** : `SpeculativeResult` avec :
- `result` : GenerationResult final
- `speculative_accept_rate` : % de tokens acceptés
- `speedup_factor` : Facteur d'accélération
- `draft_time_ms` : Temps draft
- `verify_time_ms` : Temps vérification

---

## 🔌 Intégration dans AgentRouter

**Activation automatique** pour :
- Tâches longues (>1000 tokens)
- Tâches complexes (>0.7 complexity)
- Type : `code_generation`

**Activation manuelle** :
```python
result = await router.execute_step(
    step=step,
    use_speculative=True  # Force speculative
)
```

---

## 📊 Métriques

### **StepMetrics étendues** :

- `speculative_enabled` : Booléen
- `speculative_accept_rate` : % (cible >70%)
- `speculative_speedup_factor` : Facteur (cible >1.5x)
- `draft_provider` : Provider draft
- `verify_provider` : Provider verify

### **Enregistrement** :

```python
metrics.record_step_result(
    step=step,
    result=result,
    speculative_accept_rate=spec_result.speculative_accept_rate,
    speculative_speedup=spec_result.speedup_factor,
    draft_provider=spec_result.draft_provider,
    verify_provider=spec_result.verify_provider
)
```

---

## 🧪 Tests

### **Script de benchmark** : `scripts/benchmark_speculative.py`

**Usage** :
```bash
python scripts/benchmark_speculative.py
```

**Mesure** :
- Temps d'exécution (speculative vs normal)
- Speedup factor
- Accept rate
- Coût comparatif

**Résultats** : Sauvegardés dans `output/benchmark_speculative.json`

---

## ⚙️ Configuration

**Activation/Désactivation** :

```python
# Dans AgentRouter
router = AgentRouter(enable_speculative=True)  # Par défaut: True
```

**Critères d'activation automatique** :
- `step_type == "code_generation"`
- `estimated_tokens > 1000` OU `complexity > 0.7`

---

## 📈 Gains Attendus

| Métrique | Cible | Description |
|----------|-------|-------------|
| **Accept Rate** | >70% | % de tokens draft acceptés |
| **Speedup** | >1.5x | Accélération vs normal |
| **TTFT Reduction** | -30-50% | Réduction temps premier token |
| **Coût** | +10-20% | Légère augmentation (draft + verify) |

---

## 🔍 Détails Techniques

### **Algorithme** :

1. Générer draft avec modèle rapide (Groq/Gemini Flash)
2. Vérifier draft avec modèle qualité (DeepSeek/Gemini)
3. Comparer tokens draft vs verify (premiers 50 tokens)
4. Calculer accept rate basé sur overlap
5. Utiliser résultat verify (meilleure qualité)

### **Fallback** :

Si draft échoue → Fallback sur verify model uniquement

---

## ✅ Statut

- ✅ Module `SpeculativeDecoder` créé
- ✅ Intégration dans `AgentRouter`
- ✅ Métriques ajoutées à `StepMetrics`
- ✅ Script de benchmark créé
- ⏳ Tests en production (à faire)

---

## 📝 Notes

- **Accept Rate** : Calcul approximatif basé sur comparaison token-level (premiers 50 tokens)
- **Speedup** : Estimation basée sur temps total vs temps théorique sans speculative
- **Qualité** : Toujours utiliser résultat verify (meilleure qualité que draft)

---

## 🔗 Références

- Plan de réduction latence : `/docs/guides/Plan de rédcution de la latence API.md`
- Roadmap : `/docs/guides/PLAN_GENERAL_ROADMAP.md` (Étape 9)
