# 📊 TEMPLATE RAPPORT CODE_REVIEW_AGENT

**Généré automatiquement par CodeReviewAgent après analyse**

---

## 🏠 En-tête du rapport

```markdown
## 📊 CODE REVIEW REPORT

**Plan analysé** : [module_cible]  
**Date de revue** : [DATE_HEURE]  
**Agent** : CodeReviewAgent v1.0  
**Résultat** : [✅ APPROUVÉ / ⚠️ AVEC WARNINGS / ❌ REJETÉ]
**Score** : [XX]/100
```

---

## 📋 SYNTHÈSE EXÉCUTIVE

```
[Phrase résumant le verdict et les points principaux]
[Recommandation claire : Go / Modifications requises / Refus]
```

### Verdict rapide

| Critère | Statut | Détail |
|---------|--------|--------|
| Architecture | [✅/⚠️/❌] | [Court commentaire] |
| Mode AetherFlow | [✅/⚠️/❌] | [Approprié ou non] |
| Risques | [✅/⚠️/❌] | [Gérés ou non] |
| Tests | [✅/⚠️/❌] | [Présents ou manquants] |
| Sullivan Compliance | [✅/⚠️/❌] | [Patterns respectés] |

---

## 🔍 DÉTAIL DES VIOLATIONS

### Erreurs bloquantes (Score : -25 chacune)

#### ❌ Erreur 1 : [Nom de la règle]
```yaml
Sévérité: ERROR
Fichier concerné: [chemin/fichier.py]
Message: [Description détaillée du problème]
Suggestion: [Comment corriger]
Impact: [Conséquence si ignoré]
```

#### ❌ Erreur 2 : [Nom de la règle]
```yaml
Sévérité: ERROR
Fichier concerné: [chemin/fichier.py]
Message: [Description]
Suggestion: [Correction proposée]
Impact: [Conséquence]
```

### Warnings (Score : -10 chacun)

#### ⚠️ Warning 1 : [Nom de la règle]
```yaml
Sévérité: WARNING
Fichier concerné: [chemin/fichier.py]
Message: [Description]
Suggestion: [Amélioration suggérée]
Impact: [Impact mineur]
```

#### ⚠️ Warning 2 : [Nom de la règle]
```yaml
Sévérité: WARNING
...
```

### Informations (Score : -5 chacune)

#### ℹ️ Info 1 : [Nom]
```yaml
Sévérité: INFO
Message: [Point d'attention]
Suggestion: [Optionnel]
```

---

## 📊 ANALYSE PAR CATÉGORIE

### 1. Cohérence Architecture (Règle 1)

#### Module cible
- **Chemin** : `[module_cible]`
- **Existe** : [✅ Oui / ⚠️ Nouveau / ❌ Invalide]
- **Compatibilité** : [Analyse]

#### Outils existants
- **Outils trouvés** : [Liste ou "Aucun pertinent"]
- **Utilisés dans plan** : [✅ Oui / ⚠️ Partiel / ❌ Non]
- **Recommandation** : [Outils suggérés]

#### Patterns HomeOS
- **Singletons** : [✅ Préservés / ⚠️ Risque / ❌ Violation]
- **Z-index** : [✅ Respectés / ⚠️ À vérifier / ❌ Conflit]
- **Mémoire** : [✅ SessionContext utilisé / ⚠️ / ❌]

### 2. Utilisation des Modes (Règle 2)

#### Mode sélectionné
- **Mode** : `[PROTO/PROD/SURGICAL/FRONTEND]`
- **Approprié** : [✅ Oui / ⚠️ Discutable / ❌ Non]

#### Validation
- **Fichiers modifiés** : [Nombre]
- **Mode recommandé** : [PROTO/PROD/SURGICAL]
- **Justification** : [Pourquoi ce mode est (in)adapté]

#### Outils Sullivan
- **Liste prévue** : [Outils du plan]
- **Existence vérifiée** : [✅ Tous existent / ⚠️ Certains inexistants]

### 3. Gestion des Risques (Règle 3)

#### Risques identifiés
| Risque | Gravité | Couvert par plan | Mitigation adéquate |
|--------|---------|------------------|---------------------|
| [Risque 1] | [H/M/L] | [✅/⚠️/❌] | [✅/⚠️/❌] |
| [Risque 2] | [H/M/L] | [✅/⚠️/❌] | [✅/⚠️/❌] |

#### Tests recommandés
- **Tests listés** : [Nombre]
- **Adéquation** : [✅ Suffisants / ⚠️ Manquants critiques / ❌ Aucun]
- **Couverture** : [% estimée]

#### Points d'attention connus
- **STATUS_REPORT vérifié** : [✅ Oui / ❌ Non]
- **Points traités** : [Liste ou "Non mentionnés"]

### 4. Spécifique Sullivan (Règles avancées)

#### Détection singletons
```
Singletons détectés dans description/fichiers :
- [NomSingleton] : [✅ Préservé / ⚠️ Risque / ❌ Violation]
- [NomSingleton] : [...]
```

#### Validation Z-index
```
Couches Z-index mentionnées : [Liste]
Ordre correct : [✅ Oui / ⚠️ Incertain / ❌ Non]
Conflit potentiel : [Description ou "Aucun"]
```

#### Mémoire Sullivan
```
Références mémoire/session : [Détectées oui/non]
Utilisation SessionContext : [✅ Correcte / ⚠️ / ❌]
Nouveau système créé : [✅ Non / ❌ Oui - risque]
```

---

## 💡 SUGGESTIONS D'AMÉLIORATION

### Suggestions critiques (si REJETÉ)
1. **[Suggestion 1]** : [Description détaillée]
   - Priorité : [CRITIQUE]
   - Effort : [Faible/Moyen/Fort]

2. **[Suggestion 2]** : [Description]
   - Priorité : [CRITIQUE]
   - Effort : [Faible/Moyen/Fort]

### Suggestions d'optimisation (si WARNINGS)
1. **[Suggestion 1]** : [Description]
   - Priorité : [RECOMMANDÉ]
   - Bénéfice : [Description]

2. **[Suggestion 2]** : [Description]
   - Priorité : [OPTIONNEL]
   - Bénéfice : [Description]

### Bonnes pratiques (si APPROUVÉ)
1. ✅ [Bonne pratique identifiée]
2. ✅ [Autre point positif]

---

## 🎯 DÉCISION FINALE

### Verdict

```markdown
╔════════════════════════════════════════════════════════╗
║  RÉSULTAT : [APPROUVÉ / WARNINGS / REJETÉ]            ║
║  SCORE    : [XX]/100                                   ║
║  DÉCISION : [GO / MODIFICATIONS REQUISES / STOP]      ║
╚════════════════════════════════════════════════════════╝
```

### Prochaines étapes

#### Si APPROUVÉ (score >= 80, pas d'erreurs)
```
✅ L'implémentation peut commencer immédiatement.
⚠️  Attention aux warnings listés ci-dessus (non bloquants).
📋 Suivre la checklist post-implémentation obligatoire.
```

#### Si WARNINGS (score 50-79, ou warnings présents)
```
⚠️  Modifications recommandées avant implémentation :
   1. [Action 1]
   2. [Action 2]

✅ Après corrections : Re-soumettre pour validation rapide.
```

#### Si REJETÉ (score < 50, ou erreurs critiques)
```
❌ Implémentation NON APPROUVÉE.

🔧 Actions requises avant re-soumission :
   1. [Correction critique 1]
   2. [Correction critique 2]
   3. [Revoir architecture]

💡 Alternative suggérée : [Description approche différente]
```

---

## 📋 MÉTRIQUES DÉTAILLÉES

### Score décomposé

| Catégorie | Score brut | Pénalités | Score final | Poids |
|-----------|------------|-----------|-------------|-------|
| Architecture | [100] | [-XX] | [XX] | [25%] |
| Mode | [100] | [-XX] | [XX] | [25%] |
| Risques | [100] | [-XX] | [XX] | [25%] |
| Sullivan | [100] | [-XX] | [XX] | [25%] |
| **TOTAL** | | | **[XX]/100** | **100%** |

### Distribution violations

```
Erreurs :  [Nombre] (Impact : -25 chacune)
Warnings : [Nombre] (Impact : -10 chacun)
Infos :    [Nombre] (Impact : -5 chacune)
```

### Historique (si révisions multiples)

| Version | Date | Score | Changement |
|---------|------|-------|------------|
| v1 | [Date] | [Score] | Initial |
| v2 | [Date] | [Score] | [Résumé modifs] |

---

## 🔗 RÉFÉRENCES

### Règles appliquées
- [Lien vers SKILL.md]
- [Lien vers règles validation]

### Documentation contexte
- STATUS_REPORT consulté : [Chemin]
- PRD référencé : [Chemin]

### Outils référencés
- [Outil 1] : [Chemin fichier]
- [Outil 2] : [Chemin fichier]

---

## 📝 NOTES DE L'AGENT

```
[Observations de l'agent lors de l'analyse]
[Points d'ambiguïté détectés]
[Recommandations non-bloquantes additionnelles]
```

---

## ✅ VALIDATION UTILISATEUR

```markdown
Réponse de l'utilisateur :

[ ] APPROUVÉ - GO pour implémentation
[ ] MODIFICATIONS - Voir ci-dessous
[ ] REJET - Abandonner cette approche

Commentaires / Actions demandées :
_______________________________________________
_______________________________________________
_______________________________________________

Signature : _______________  Date : _______________
```

---

**Rapport généré par** : CodeReviewAgent  
**Template version** : 1.0  
**Validité** : À utiliser avec ImplementationPlan validé
