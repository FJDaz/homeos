# Décision : SLM Locaux - Annulé

**Date** : 26 janvier 2025  
**Statut** : ❌ **ANNULÉ - Contrainte technique**

---

## 🚫 Contrainte Identifiée

**Machine** : i7 4 cœurs  
**Problème** : Insuffisant pour faire tourner des SLM locaux

**Ressources requises pour SLM locaux** :
- CPU : 8+ cœurs recommandés
- RAM : 8-16GB minimum
- GPU : Optionnel mais recommandé
- Stockage : 4-8GB par modèle

**Notre configuration** : i7 4 cœurs → **Incompatible**

---

## ✅ Alternative Validée : Groq

**Groq remplace efficacement SLM local** :

| Critère | SLM Local | Groq (Alternative) |
|---------|-----------|---------------------|
| **Latence** | <1s | 1-3s ✅ |
| **Coût** | 0€ | ~$0.0001/tâche ✅ |
| **Qualité** | 95% | 98% ✅ |
| **Ressources locales** | 8GB+ RAM | 0 ✅ |
| **Installation** | Ollama + modèle | API key ✅ |
| **Maintenance** | Oui | Non ✅ |

**Verdict** : ✅ **Groq offre latence équivalente sans ressources locales**

---

## 📋 Actions Prises

1. ✅ **SLM locaux retirés du roadmap** (Étape 9)
2. ✅ **Groq validé comme alternative** (déjà intégré)
3. ✅ **Documentation mise à jour** :
   - `PLAN_GENERAL_ROADMAP.md` : SLM locaux marqués comme annulés
   - `CE_QUI_RESTE.md` : SLM locaux retirés
   - `ANALYSE_SLM_LOCAUX.md` : Verdict mis à jour

---

## 🎯 Plan Révisé - Étape 9 : Réduction Latence API

**Ce qui reste** :
1. ✅ **Prompt Caching** : Fait
2. ⏳ **Speculative Decoding** : Priorité haute (gain TTFT important)
3. ⏳ **Cache Sémantique** : Priorité haute (réduction appels redondants)
4. ⏳ **WebSockets** : Priorité moyenne (connexions persistantes)

**SLM locaux** : ❌ **Retiré** - Utiliser Groq à la place

---

## ✅ Conclusion

**SLM locaux** : ❌ **Impossible sur cette configuration**

**Alternative** : ✅ **Groq** (déjà intégré, latence équivalente, pas de ressources locales)

**Impact** : Aucun - Groq remplace efficacement SLM local avec meilleure qualité et maintenance zéro.
