# 📝 TEMPLATE IMPLEMENTATIONPLAN

**Copier ce template et compléter les sections `[...]`**

---

## 🏠 En-tête obligatoire

```markdown
## 🏠 HOMEOS/SULLIVAN CONTEXT CHECK

### 📊 Statut
- Date : [DATE]
- Auteur : Kimi
- Module cible : [NOM_DU_MODULE]

### 📋 Checklist pré-action
- [x] 1. STATUS_REPORT consulté : [CHEMIN/NOM_FICHIER]
- [x] 2. Mode AetherFlow : [PROTO/PROD/SURGICAL/FRONTEND/DESIGNER]
- [x] 3. Outils existants vérifiés : [LISTE_OU_AUCUN]
- [x] 4. Plan généré (ce document)
- [ ] 5. CodeReviewAgent : [EN_ATTENTE/APPROUVÉ]
- [ ] 6. Approbation GO : [EN_ATTENTE]
```

---

## 📋 IMPLEMENTATIONPLAN (JSON)

```json
{
  "module_cible": "[ex: sullivan/agent]",
  "mode_aetherflow": "[proto|prod|surgical]",
  "fichiers_crees": [
    "[chemin/fichier1.py]",
    "[chemin/fichier2.py]"
  ],
  "fichiers_modifies": [
    "[chemin/fichier_existant.py]"
  ],
  "fichiers_supprimes": [
    "[chemin/fichier_obsolete.py]"
  ],
  "outils_sullivan_utilises": [
    "[ex: ConversationMemory]",
    "[ex: SessionContext]"
  ],
  "z_index_layers": [
    "[si UI: content|overlay|modal|...]"
  ],
  "risques_identifies": [
    "[Risque 1]",
    "[Risque 2]"
  ],
  "tests_recommandes": [
    "[test_1]",
    "[test_2]"
  ],
  "known_attention_points": [
    "[Point attention STATUS_REPORT]"
  ],
  "description": "[Description détaillée de l'implémentation]"
}
```

---

## 🎯 Description détaillée

### Objectif
```
[Description claire de ce que va faire l'implémentation]
[Contexte métier/fonctionnel]
```

### Contexte actuel
```
[État actuel du système concerné]
[Pourquoi cette modification est nécessaire]
```

### Solution proposée
```
[Description technique de la solution]
[Architecture/Design patterns utilisés]
```

---

## 🔍 Analyse détaillée

### Architecture
```
[Diagramme ou description de l'architecture]
[Interactions avec modules existants]
```

### Dépendances
```
[Dépendances externes (packages, APIs)]
[Dépendances internes (autres modules)]
```

### Impact sur code existant
```
[Fichiers touchés et pourquoi]
[Risques de régression]
```

---

## ⚠️ Analyse des risques

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| [Risque 1] | [Faible/Moyen/Fort] | [Mineur/Majeur/Critique] | [Solution] |
| [Risque 2] | [Faible/Moyen/Fort] | [Mineur/Majeur/Critique] | [Solution] |

### Points d'attention spécifiques
- [ ] [Point 1 lié à STATUS_REPORT]
- [ ] [Point 2 lié à architecture]

---

## 🧪 Stratégie de tests

### Tests unitaires
```python
# Exemple de tests à implémenter
def test_[fonctionnalité]():
    """Test [description]"""
    # Arrange
    [setup]
    # Act
    [action]
    # Assert
    [vérification]
```

### Tests d'intégration
```
[Scénarios de test end-to-end]
[Données de test nécessaires]
```

### Validation manuelle
```
[Étapes de validation manuelle]
[Critères d'acceptation]
```

---

## 📅 Planning d'implémentation

### Étapes détaillées

1. **Étape 1** : [Description]
   - Fichier(s) : `[chemin]`
   - Durée estimée : [X minutes]
   - Validation : [Critère]

2. **Étape 2** : [Description]
   - Fichier(s) : `[chemin]`
   - Durée estimée : [X minutes]
   - Validation : [Critère]

3. **Étape 3** : [Description]
   - ...

---

## 🔧 Validation technique

### Checklist pré-implémentation
- [ ] Architecture alignée avec HomeOS
- [ ] Singletons préservés (si applicable)
- [ ] Z-index respectés (si UI)
- [ ] Pas de duplication code existant
- [ ] Imports valides vérifiés

### Checklist post-implémentation
- [ ] Tests unitaires passent
- [ ] Pas de régression détectée
- [ ] Documentation à jour
- [ ] CodeReviewAgent validé (si applicable)

---

## 💰 Estimation ressources

### Coût inference (si appels LLM)
| Étape | Modèle | Tokens IN | Tokens OUT | Coût estimé |
|-------|--------|-----------|------------|-------------|
| [Étape 1] | [DeepSeek/Gemini] | [~X] | [~Y] | [$Z] |
| [Étape 2] | [DeepSeek/Gemini] | [~X] | [~Y] | [$Z] |
| **TOTAL** | | | | **[~$Z]** |

### Temps estimé
- Analyse : [X] minutes
- Implémentation : [Y] minutes
- Tests : [Z] minutes
- **Total** : [X+Y+Z] minutes

---

## 🔄 Alternative(s) considérée(s)

### Option A (retenue) : [Description]
- Avantages : [Liste]
- Inconvénients : [Liste]

### Option B (écartée) : [Description]
- Pourquoi écartée : [Justification]

### Option C (écartée) : [Description]
- Pourquoi écartée : [Justification]

---

## ❓ Questions ouvertes

1. **[Question 1]** : [Description]
   - Options : [A/B/C]
   - Recommandation : [Option]

2. **[Question 2]** : [Description]
   - ...

---

## ✅ VALIDATION REQUISE

### Pour l'utilisateur

```markdown
Merci de répondre par :
- **GO** : Approuvé pour implémentation
- **MODIFICATIONS** : Voir commentaires ci-dessous
- **REJET** : Annuler cette approche

Commentaires / Modifications demandées :
_______________________________________________
_______________________________________________
```

---

## 📝 NOTES DE TRAVAIL (internes Kimi)

```
[Notes pendant l'analyse]
[Découverts pendant l'exploration]
[Points à vérifier]
```

---

**Template version** : 1.0  
**À utiliser avec** : `SKILL.md` et `CHECKLIST.md`  
**Mise à jour** : Remplacer tous les `[...]` par valeurs réelles
