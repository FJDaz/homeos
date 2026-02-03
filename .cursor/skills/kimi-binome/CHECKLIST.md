# ✅ CHECKLIST KIMI - EXÉCUTION OBLIGATOIRE

**À copier-coller au début de chaque réponse**

---

## CHECKLIST PRÉ-ACTION

```markdown
## 🏠 HOMEOS/SULLIVAN CONTEXT CHECK

### 📋 Checklist obligatoire

- [ ] 1. **CONTEXTE** : Consulté `STATUS_REPORT_HOMEOS.md` ? 
  - Dernier rapport : `docs/04-homeos/Status reports/`
  - Réponse : _______________

- [ ] 2. **MODE** : Mode AetherFlow identifié ?
  - [ ] PROTO (-q) : Exploration/POC
  - [ ] PROD (-f) : Modification existant ← **DÉFAUT**
  - [ ] SURGICAL : Changement précis < 50 lignes
  - [ ] FRONTEND (-frd) : UI/UX
  - Réponse : _______________

- [ ] 3. **EXISTANT** : Outils Sullivan vérifiés ?
  - Recherche dans `Backend/Prod/sullivan/` : _______________
  - Outil existant trouvé : _______________

- [ ] 4. **PLAN** : ImplementationPlan généré ?
  - Voir section "IMPLEMENTATIONPLAN" ci-dessous

- [ ] 5. **REVUE** : CodeReviewAgent consulté ?
  - [ ] Oui (si disponible)
  - [ ] Non (justification : _______________)
  - Résultat : _______________

- [ ] 6. **APPROBATION** : Attendre "GO" explicite ?
  - Statut : [ ] EN ATTENTE / [ ] REÇU

### ⚠️ Points d'attention identifiés
- Module concerné : _______________
- Risques connus : _______________
- Dépendances : _______________
```

---

## IMPLEMENTATIONPLAN (À COMPLÉTER)

```json
{
  "module_cible": "",
  "mode_aetherflow": "prod",
  "fichiers_crees": [],
  "fichiers_modifies": [],
  "fichiers_supprimes": [],
  "outils_sullivan_utilises": [],
  "z_index_layers": [],
  "risques_identifies": [],
  "tests_recommandes": [],
  "known_attention_points": [],
  "description": ""
}
```

### Champs obligatoires :

| Champ | Description | Exemple |
|-------|-------------|---------|
| `module_cible` | Module principal concerné | `"sullivan/agent"` |
| `mode_aetherflow` | Mode (proto/prod/surgical) | `"prod"` |
| `fichiers_crees` | Nouveaux fichiers | `["code_review_agent.py"]` |
| `fichiers_modifies` | Fichiers modifiés | `["memory.py"]` |
| `fichiers_supprimes` | Fichiers supprimés | `["old_file.py"]` |
| `outils_sullivan_utilises` | Outils existants utilisés | `["ConversationMemory"]` |
| `z_index_layers` | Couches z-index (si UI) | `["content", "overlay"]` |
| `risques_identifies` | Risques connus | `["Singleton violation"]` |
| `tests_recommandes` | Tests à implémenter | `["test_session_context"]` |
| `known_attention_points` | Points STATUS_REPORT | `["ir/pipeline dupliqué"]` |
| `description` | Description détaillée | `"Ajout de..."` |

---

## RAPPORT DE VALIDATION

### Résultat CodeReviewAgent

```
Statut : [ ] APPROUVÉ (score >= 80) 
         [ ] AVEC WARNINGS (score 50-79)
         [ ] REJETÉ (score < 50 ou erreurs critiques)
         [ ] NON CONSULTÉ (justification requise)

Score : ___/100

Violations détectées :
- [ ] _______________
- [ ] _______________

Suggestions :
- _______________

Actions requises avant implémentation :
1. _______________
2. _______________
```

### Approbation utilisateur

```
Décision utilisateur :
[ ] GO - Approuvé pour implémentation
[ ] MODIFICATIONS - Voir commentaires ci-dessous
[ ] REJET - Annuler/Repenser

Commentaires utilisateur :
_______________________________________________
_______________________________________________
```

---

## POST-IMPLÉMENTATION (À COMPLÉTER APRÈS CODE)

### Tests effectués

```markdown
- [ ] Tests unitaires créés
- [ ] Tests passent (commande : _______________)
- [ ] Vérification imports OK
- [ ] Pas de régression détectée
- [ ] Documentation mise à jour
```

### Validation finale

```
✅ Livrable prêt pour commit
[ ] Oui
[ ] Non (blocage : _______________)

Prochaine étape suggérée :
_______________________________________________
```

---

## RACCOURCIS RAPIDES

### Commandes fréquentes

```bash
# Vérifier dernier status report
ls -la docs/04-homeos/Status\ reports/ | tail -5

# Rechercher outil existant
grep -r "class.*Memory" Backend/Prod/sullivan/

# Lancer tests
python -m pytest tests/ -v

# Vérifier singletons
grep -r "_instance" homeos/core/ Backend/Prod/sullivan/
```

### Patterns de réponse standard

**Pattern 1 : Demande simple (question/info)**
```
Réponse directe (pas de checklist requise)
```

**Pattern 2 : Analyse/recherche**
```
## 🏠 HOMEOS/SULLIVAN CONTEXT CHECK

### 📋 Checklist réduite
- [x] CONTEXTE : Consulté (pas de modification)
- [x] MODE : N/A (analyse seule)
[... réponse ...]
```

**Pattern 3 : Implémentation complète**
```
## 🏠 HOMEOS/SULLIVAN CONTEXT CHECK
[Checklist complète 6 points]
## 📝 IMPLEMENTATIONPLAN
[JSON complété]
## 🔍 Plan proposé
[Description détaillée]
❓ GO / MODIFICATIONS / REJET ?
```

---

## CHECKLIST RÉCAPITULATIVE VISUELLE

```
┌─────────────────────────────────────────────────────────┐
│  AVANT TOUTE ACTION                                      │
│  □ 1. STATUS_REPORT consulté ?                          │
│  □ 2. Mode AetherFlow identifié ?                       │
│  □ 3. Outils existants vérifiés ?                       │
│  □ 4. ImplementationPlan généré ?                       │
│  □ 5. CodeReviewAgent consulté ?                        │
│  □ 6. Approbation "GO" reçue ?                          │
└─────────────────────────────────────────────────────────┘
```

---

**Version** : 2.2.1  
**À utiliser avec** : `SKILL.md` (référence complète)  
**Mise à jour** : Copier-coller et remplir les champs vides
