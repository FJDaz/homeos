# Coûts AETHERFLOW - Analyse 2026

**Date** : 25 janvier 2025  
**Mise à jour** : Conditions Gemini 2026

---

## 💰 Coûts par Provider (Configuration Actuelle)

| Provider | Input (per 1K tokens) | Output (per 1K tokens) | Statut |
|----------|---------------------|----------------------|--------|
| **DeepSeek** | $0.00014 | $0.00028 | ✅ Payant |
| **Codestral** | $0.0003 | $0.0003 | ✅ Payant |
| **Gemini** | $0.0 (gratuit) | $0.0 (gratuit) | ⚠️ Gratuit jusqu'à quota |
| **Groq** | $0.00059 | $0.00079 | ✅ Payant |

**Note Gemini** : En mode payant (Tier 1), les prix sont :
- Contexte court (≤ 200k tokens) : ~$2.00 / million output
- Contexte long (> 200k tokens) : ~$4.00 / million output

---

## 📊 Coûts Réels Observés (Benchmark Suite)

### Benchmark Récent (5 tâches, 14 étapes)

| Métrique | Valeur |
|----------|--------|
| Tokens totaux | 15,108 (8,108 input / 7,000 output) |
| Provider utilisé | DeepSeek uniquement |
| Coût total | **$0.0031** |
| Coût par étape | **~$0.00022** |
| Coût par 1K tokens | **~$0.00021** |

**Répartition** :
- Input : 8,108 tokens × $0.00014/1K = $0.0011
- Output : 7,000 tokens × $0.00028/1K = $0.0020
- **Total : $0.0031**

---

## 🎯 Scénarios d'Usage avec Routage Intelligent

Avec le routage intelligent activé, AETHERFLOW sélectionne automatiquement le meilleur provider :

### Scénario 1 : Tâche Exemplaire (Module Utilitaire)

**Estimation** : 5 étapes, ~3,050 tokens

| Étape | Type | Provider Sélectionné | Tokens | Coût |
|-------|------|---------------------|--------|------|
| step_1 | analysis | **Gemini** (gratuit) | 400 | **$0.00** |
| step_2 | code_generation | **DeepSeek** | 800 | $0.0003 |
| step_3 | analysis | **Gemini** (gratuit) | 350 | **$0.00** |
| step_4 | refactoring | **Codestral** | 600 | $0.0002 |
| step_5 | code_generation | **DeepSeek** | 900 | $0.0003 |
| **Total** | - | - | 3,050 | **$0.0008** |

**Gain vs DeepSeek seul** : ~74% d'économie grâce à Gemini gratuit pour les analyses

---

### Scénario 2 : Usage Modéré (10 tâches/jour)

**Hypothèse** : 10 tâches similaires à la tâche exemplaire

| Métrique | Valeur |
|----------|--------|
| Tâches/jour | 10 |
| Tokens/jour | ~30,500 |
| Coût/jour (avec routage) | **~$0.008** |
| Coût/mois (30 jours) | **~$0.24** |

**Répartition providers** :
- Gemini (analyses) : ~7,500 tokens → **$0.00** (gratuit)
- DeepSeek (code génération) : ~17,000 tokens → ~$0.005
- Codestral (refactoring) : ~6,000 tokens → ~$0.002

---

### Scénario 3 : Usage Intensif (100 tâches/jour)

**Hypothèse** : 100 tâches similaires

| Métrique | Valeur |
|----------|--------|
| Tâches/jour | 100 |
| Tokens/jour | ~305,000 |
| Coût/jour (avec routage) | **~$0.08** |
| Coût/mois (30 jours) | **~$2.40** |

**Répartition providers** :
- Gemini (analyses) : ~75,000 tokens → **$0.00** (gratuit)
- DeepSeek (code génération) : ~170,000 tokens → ~$0.05
- Codestral (refactoring) : ~60,000 tokens → ~$0.02

---

## ⚠️ Passage au Payant pour Gemini

### Quotas Gratuits Gemini (2026)

| Limite | Valeur Gratuite |
|--------|----------------|
| **Requêtes/min (RPM)** | 5-15 (selon modèle) |
| **Tokens/min (TPM)** | 250,000 |
| **Requêtes/jour (RPD)** | 100-1,000 |

### Quand Passez-Vous au Payant ?

**Déclencheur** : Activation manuelle de la facturation dans Google Cloud

**Scénarios où vous devez activer** :

1. **Erreur 429 (Too Many Requests)**
   - Vous dépassez 15 requêtes/min
   - Vous dépassez 250,000 tokens/min
   - Solution : Activer facturation → Passage Tier 1

2. **Usage Professionnel**
   - Vous intégrez dans une app réelle
   - Vous avez besoin de données privées (pas d'entraînement Google)
   - Solution : Activer facturation immédiatement

3. **Dépassement Quota Quotidien**
   - Vous dépassez 1,000 requêtes/jour
   - Solution : Activer facturation

---

## 💵 Coûts Gemini en Mode Payant (Tier 1)

### Tarification Gemini 3 Pro (2026)

| Contexte | Input (per 1M) | Output (per 1M) |
|----------|---------------|----------------|
| **Court (≤ 200k tokens)** | ~$1.00 | ~$2.00 |
| **Long (> 200k tokens)** | ~$2.00 | ~$4.00 |

**Pour AETHERFLOW** : Contexte généralement court (< 200k tokens)

### Coût Estimé avec Gemini Payant

**Scénario Modéré (10 tâches/jour)** :
- Gemini : ~7,500 tokens/jour × $2.00/1M = **~$0.015/jour**
- Total avec Gemini payant : $0.008 (autres) + $0.015 (Gemini) = **~$0.023/jour**
- **Coût/mois : ~$0.69**

**Scénario Intensif (100 tâches/jour)** :
- Gemini : ~75,000 tokens/jour × $2.00/1M = **~$0.15/jour**
- Total avec Gemini payant : $0.08 (autres) + $0.15 (Gemini) = **~$0.23/jour**
- **Coût/mois : ~$6.90**

---

## 📈 Tableau Comparatif : Gratuit vs Payant Gemini

| Scénario | Tokens Gemini/jour | Mode Gratuit | Mode Payant | Différence |
|----------|------------------|--------------|-------------|------------|
| **Modéré** | 7,500 | $0.00 | $0.015 | +$0.015/jour |
| **Intensif** | 75,000 | $0.00 | $0.15 | +$0.15/jour |
| **Très Intensif** | 250,000+ | ❌ Quota dépassé | $0.50+ | Obligatoire |

---

## 🎯 Recommandations par Niveau d'Usage

### Usage Léger (< 10 tâches/jour)
- ✅ **Restez en gratuit Gemini**
- ✅ Coût total : **~$0.24/mois**
- ✅ Pas besoin d'activer facturation

### Usage Modéré (10-50 tâches/jour)
- ⚠️ **Surveillez les quotas Gemini**
- ✅ Si erreurs 429 → Activez facturation
- ✅ Coût avec Gemini gratuit : **~$0.24-1.20/mois**
- ✅ Coût avec Gemini payant : **~$0.69-3.45/mois**

### Usage Intensif (50-100+ tâches/jour)
- ✅ **Activez facturation Gemini** dès le début
- ✅ Coût total : **~$2.40-6.90/mois**
- ✅ Avantage : Données privées (pas d'entraînement Google)

---

## 💡 Optimisation des Coûts

### Stratégies pour Réduire les Coûts

1. **Maximiser l'usage de Gemini gratuit**
   - Utiliser Gemini pour toutes les analyses (routage automatique)
   - Rester sous les quotas gratuits (15 req/min, 250K tokens/min)

2. **Routage intelligent**
   - AETHERFLOW sélectionne automatiquement le provider le moins cher
   - Gemini pour analyses (gratuit)
   - DeepSeek pour code complexe (moins cher que Codestral)
   - Codestral pour refactoring précis

3. **Batch les requêtes**
   - Grouper les analyses pour maximiser l'usage Gemini gratuit
   - Éviter les pics de requêtes/min

4. **Surveiller les quotas**
   - Activer facturation seulement si nécessaire
   - Utiliser DeepSeek/Groq si quota Gemini dépassé

---

## 📊 Estimation Coûts Mensuels

| Usage | Tâches/jour | Tokens/jour | Gemini Mode | Coût/mois |
|-------|-------------|-------------|-------------|-----------|
| **Léger** | 5 | ~15,000 | Gratuit | **$0.12** |
| **Modéré** | 20 | ~60,000 | Gratuit | **$0.48** |
| **Modéré+** | 20 | ~60,000 | Payant | **$1.38** |
| **Intensif** | 100 | ~305,000 | Payant | **$6.90** |
| **Très Intensif** | 500 | ~1,500,000 | Payant | **$34.50** |

---

## 🚨 Seuils d'Activation Facturation Gemini

### ⚠️ Ajouter un Moyen de Paiement : Sans Risque ?

**Réponse** : **OUI, c'est sans risque** si vous restez dans les quotas gratuits.

**Pourquoi c'est sans risque** :
- ✅ **Pay-As-You-Go** : Vous ne payez QUE si vous dépassez les quotas gratuits
- ✅ **Quotas gratuits conservés** : Même avec facturation activée, vous gardez les quotas gratuits
- ✅ **Pas de frais cachés** : Aucun frais si vous restez dans les limites gratuites
- ✅ **Vérification prépaiement** : Si Google demande une vérification, c'est un crédit (pas une facture)

**Exemple** :
- Quota gratuit : 250,000 tokens/min
- Vous utilisez : 100,000 tokens/min
- **Coût facturé : $0.00** ✅

### Quand Activer la Facturation ?

| Situation | Action | Risque Financier |
|-----------|--------|------------------|
| **Erreurs 429 fréquentes** | ✅ Activer facturation | ⚠️ Payez seulement au-delà des quotas |
| **> 15 requêtes/min** | ✅ Activer facturation | ⚠️ Payez seulement au-delà des quotas |
| **> 250K tokens/min** | ✅ Activer facturation | ⚠️ Payez seulement au-delà des quotas |
| **> 1,000 requêtes/jour** | ✅ Activer facturation | ⚠️ Payez seulement au-delà des quotas |
| **Données sensibles** | ✅ Activer facturation (privacité) | ✅ **$0.00 si vous restez dans quotas** |
| **Usage professionnel** | ✅ Activer facturation | ✅ **$0.00 si vous restez dans quotas** |
| **Précaution** | ✅ Activer dès maintenant | ✅ **$0.00 si vous restez dans quotas** |

### Recommandation

**Vous pouvez activer la facturation sans risque** si :
- ✅ Vous restez dans les quotas gratuits (250K tokens/min, 15 req/min)
- ✅ Vous voulez éviter les erreurs 429 futures
- ✅ Vous voulez la privacité des données (pas d'entraînement Google)
- ✅ Vous voulez des limites plus élevées en cas de besoin

**Vous ne paierez rien** tant que vous restez dans les quotas gratuits.

### Coût Additionnel si Activation

**Scénario Modéré** :
- Sans facturation : **$0.48/mois**
- Avec facturation : **$1.38/mois**
- **Différence : +$0.90/mois** (+187%)

**Scénario Intensif** :
- Sans facturation : ❌ Impossible (quota dépassé)
- Avec facturation : **$6.90/mois**
- **Nécessaire pour continuer**

---

## ✅ Conclusion

### Coûts AETHERFLOW

**En mode gratuit Gemini** :
- Usage léger : **~$0.12-0.24/mois**
- Usage modéré : **~$0.48-1.20/mois**

**En mode payant Gemini** :
- Usage modéré : **~$1.38-3.45/mois**
- Usage intensif : **~$6.90-34.50/mois**

### Avantages AETHERFLOW

1. **Coûts très bas** : ~$0.0002-0.0008 par tâche
2. **Routage intelligent** : Maximise l'usage gratuit Gemini
3. **Scalable** : Coûts restent raisonnables même à grande échelle
4. **Flexible** : Peut fonctionner avec ou sans Gemini payant

### Recommandation

- **Démarrage** : Utilisez Gemini gratuit jusqu'à atteindre les limites
- **Production** : Activez facturation Gemini si vous dépassez les quotas ou avez besoin de privacité
- **Coûts totaux** : Restent très bas même avec Gemini payant (~$1-7/mois pour usage modéré-intensif)

---

**Dernière mise à jour** : 25 janvier 2025
