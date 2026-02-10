# MISSION GEMINI : Audit Codebase - Phase 3 (Fix Mypy Critiques)

**Date** : 8 février 2026
**Assigné à** : Gemini (Terminal)
**Statut** : EN ATTENTE
**Prérequis** : Phase 1 ✅, Phase 2 ✅

---

## 🎯 OBJECTIF

Corriger les erreurs mypy les plus critiques (`[no-redef]`, `[union-attr]`) pour améliorer la stabilité du code.

**Cible** : Réduire de 305 → <200 erreurs mypy

---

## 📋 TÂCHES À EXÉCUTER (dans l'ordre)

### 1. Relancer mypy pour avoir l'état actuel

```bash
cd /Users/francois-jeandazin/AETHERFLOW && source venv/bin/activate
mypy Backend/Prod --exclude '.*\.generated\.py$' --explicit-package-bases --ignore-missing-imports 2>&1 | tee docs/support/audit/mypy_report_v6.txt | tail -50
```

---

### 2. Corriger les `[no-redef]` dans api.py (lignes 35-43)

Le fichier `Backend/Prod/api.py` a des imports dupliqués aux lignes 35-43.

**Action** : Examiner les imports et supprimer les doublons.

```bash
head -50 Backend/Prod/api.py
```

Les imports dupliqués ressemblent à :
```python
# Ligne ~35-43 : imports redéfinis
from ... import settings  # déjà importé avant
from ... import Plan, PlanReader  # déjà importé
```

**Solution** : Supprimer les lignes d'import redondantes.

---

### 3. Corriger les `[no-redef]` dans code_review_agent.py (ligne 27)

```bash
head -40 Backend/Prod/sullivan/agent/code_review_agent.py
```

**Action** : La ligne 27 redéfinit plusieurs noms. Nettoyer les imports.

---

### 4. Corriger les `[union-attr]` dans surgical_editor.py

Les erreurs `[union-attr]` indiquent des accès à `.body` sur un objet potentiellement `None`.

```bash
grep -n "\.body" Backend/Prod/core/surgical_editor.py | head -20
```

**Solution type** : Ajouter une vérification `if module is not None:` avant d'accéder à `.body`

Exemple de correction :
```python
# AVANT
for node in ast.walk(self.tree):
    ...

# APRÈS
if self.tree is not None:
    for node in ast.walk(self.tree):
        ...
```

---

### 5. Corriger les `[union-attr]` dans orchestrator.py

Mêmes problèmes d'accès sur objets potentiellement `None`.

```bash
grep -n "record_step_result\|complete_step\|start_step" Backend/Prod/orchestrator.py
```

**Solution** : Ajouter des guards `if self.metrics is not None:`

---

### 6. Relancer mypy après corrections

```bash
mypy Backend/Prod --exclude '.*\.generated\.py$' --explicit-package-bases --ignore-missing-imports 2>&1 | tee docs/support/audit/mypy_report_v7.txt
echo "Erreurs restantes:" && tail -5 docs/support/audit/mypy_report_v7.txt
```

---

## 📝 COMPTE-RENDU À FOURNIR

Créer : `/Users/francois-jeandazin/AETHERFLOW/.claude/mailbox/CR_GEMINI_AUDIT_PHASE3.md`

```markdown
# CR GEMINI : Audit Phase 3

**Date** : [date]
**Statut** : ✅ TERMINÉ / ⚠️ PARTIEL / ❌ BLOQUÉ

## Résultats Mypy

| Métrique | Avant | Après |
|----------|-------|-------|
| Erreurs totales | 305 | X |
| Fichiers avec erreurs | 56 | X |
| `[no-redef]` | ~20 | X |
| `[union-attr]` | ~15 | X |

## Fichiers Corrigés

| Fichier | Corrections |
|---------|-------------|
| api.py | Imports dupliqués supprimés |
| code_review_agent.py | ... |
| surgical_editor.py | Guards None ajoutés |
| orchestrator.py | ... |

## Problèmes Non Résolus

[Liste des erreurs restantes importantes]

## Prochaines Actions Suggérées

[...]
```

---

## ⚠️ ATTENTION

- **NE PAS** changer la logique du code, seulement ajouter des guards/types
- **NE PAS** supprimer du code fonctionnel
- Si un fix est complexe, **le noter** dans le CR et passer au suivant
- Priorité : `[no-redef]` d'abord (plus simple), puis `[union-attr]`

---

**Merci Gemini !**
