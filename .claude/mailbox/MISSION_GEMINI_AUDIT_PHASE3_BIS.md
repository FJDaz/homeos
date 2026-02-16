# MISSION GEMINI : Audit Phase 3 BIS (Simplifiée)

**Date** : 9 février 2026
**Statut** : REMPLACE Phase 3
**Problème** : L'outil `replace` ne fonctionne pas pour éditions multiples

---

## 🎯 NOUVELLE APPROCHE

**STOP les éditions de fichiers Python.** On passe à l'essentiel.

---

## 📋 TÂCHES SIMPLIFIÉES

### 1. Relancer mypy et compter les erreurs actuelles

```bash
cd /Users/francois-jeandazin/AETHERFLOW && source venv/bin/activate
mypy Backend/Prod --exclude '.*\.generated\.py$' --explicit-package-bases --ignore-missing-imports 2>&1 | tail -5
```

Note le nombre d'erreurs.

---

### 2. Relancer les tests et compter

```bash
cd /Users/francois-jeandazin/AETHERFLOW && source venv/bin/activate
pytest Backend/Prod/tests -v --tb=no 2>&1 | tail -20
```

Note : X passed, Y failed.

---

### 3. Générer le rapport de couverture HTML

```bash
cd /Users/francois-jeandazin/AETHERFLOW && source venv/bin/activate
pytest Backend/Prod/tests --cov=Backend/Prod --cov-report=html --cov-report=term-missing 2>&1 | tail -30
```

Le rapport HTML sera dans `htmlcov/index.html`.

---

### 4. Mettre à jour le rapport d'audit

Édite le fichier `docs/support/audit/AUDIT_CODEBASE_COMPLET.md` section 4 (Tests) avec les résultats :

```markdown
## 4. Tests (Couverture, Gaps)

### 4.1 Résultats pytest

- **Total** : X tests
- **Passed** : X (X%)
- **Failed** : X (X%)
- **Couverture** : X%

### 4.2 Rapport de couverture

Disponible dans `htmlcov/index.html`
```

---

## 📝 COMPTE-RENDU

Créer : `.claude/mailbox/CR_GEMINI_AUDIT_PHASE3_BIS.md`

```markdown
# CR GEMINI : Audit Phase 3 BIS

**Date** : [date]
**Statut** : ✅ TERMINÉ

## Résultats Finaux

| Métrique | Valeur |
|----------|--------|
| Erreurs mypy | X |
| Tests passed | X |
| Tests failed | X |
| Couverture | X% |

## Fichiers Générés

- `htmlcov/index.html` - Rapport couverture

## État de l'Audit

Score estimé : X/10
```

---

## ⚠️ IMPORTANT

- **NE PAS** essayer d'éditer des fichiers Python
- **JUSTE** exécuter les commandes et noter les résultats
- Si une commande échoue, noter l'erreur et passer à la suivante

---

**Merci Gemini !**
