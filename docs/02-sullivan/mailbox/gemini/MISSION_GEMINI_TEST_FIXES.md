# MISSION GEMINI : Fixer les Tests Échoués

**Date** : 9 février 2026
**Agent** : Gemini (QA)
**Mode AetherFlow** : DOUBLE-CHECK
**Priorité** : 🟠 P1

---

## 1. CONTEXTE

L'audit du 8 février a révélé :
- **140 tests passed** (56.7%)
- **107 tests failed** (43.3%)

Ta mission : réduire le nombre de tests échoués.

---

## 2. OBJECTIF

Passer de **107 failed** à **< 50 failed** (objectif : 80% pass rate).

---

## 3. CONTRAINTES IMPORTANTES

⚠️ **NE PAS modifier le code source** (`Backend/Prod/`) sauf les fichiers de tests.

Si un test échoue à cause d'un bug dans le code source :
1. Documente le bug dans ton CR
2. Commente le test avec `# TODO: Bug in source - [description]`
3. Passe au test suivant

---

## 4. WORKFLOW

### 4.1 Diagnostic

```bash
cd /Users/francois-jeandazin/AETHERFLOW
source venv/bin/activate
pytest Backend/Prod/tests/ --tb=short -q 2>&1 | head -100
```

### 4.2 Catégoriser les échecs

| Catégorie | Action |
|-----------|--------|
| **ImportError** | Fixer les imports dans le test |
| **AssertionError** | Vérifier si le test est correct |
| **TypeError** | Adapter les signatures d'appel |
| **Missing fixture** | Ajouter la fixture manquante |
| **Async issue** | Ajouter `@pytest.mark.asyncio` |
| **Bug source** | Documenter + skip |

### 4.3 Prioriser

1. Tests de collection (imports)
2. Tests Sullivan (`tests/sullivan/`)
3. Tests Core (`tests/core/`)
4. Tests Models (`tests/models/`)

---

## 5. SKILLS À CHARGER

Utilise tes skills dans `gemini_workspace/skills/` :
- `TestFixer.md` - Guide de correction tests
- `AuditAssistant.md` - Méthodologie audit

---

## 6. LIVRABLES

### 6.1 Compte-rendu

**Fichier** : `docs/02-sullivan/mailbox/gemini/CR_TEST_FIXES.md`

Contenu :
```markdown
# CR Test Fixes - 9 février 2026

## Résultats
- Avant : 140 passed / 107 failed
- Après : X passed / Y failed

## Tests corrigés
| Fichier | Test | Problème | Fix |
|---------|------|----------|-----|
| ... | ... | ... | ... |

## Bugs source identifiés
| Fichier source | Bug | Test concerné |
|----------------|-----|---------------|
| ... | ... | ... |

## Tests skippés (à revoir)
- ...
```

### 6.2 Pas de PR

Ne crée pas de PR. Juste les corrections locales.

---

## 7. CRITÈRES D'ACCEPTATION

- [ ] Pass rate > 80% (ou justification)
- [ ] Aucune modification du code source (hors tests)
- [ ] Bugs source documentés
- [ ] CR déposé dans mailbox

---

**Bonne mission !**
