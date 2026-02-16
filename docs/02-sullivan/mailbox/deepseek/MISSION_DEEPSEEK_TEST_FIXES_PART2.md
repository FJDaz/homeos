# MISSION DEEPSEEK : Test Fixes Part 2 (Parallèle Gemini)

**Date** : 9 février 2026, 16h30
**Agent** : DeepSeek (via Chat CLI)
**Mode AetherFlow** : DOUBLE-CHECK
**Priorité** : 🔴 P0 (parallèle avec Gemini)

---

## 0. CONTEXTE

**Gemini** travaille sur MISSION_GEMINI_TEST_FIXES.md depuis 1h+ (lent).

**Toi (DeepSeek)** : Prendre en charge la **moitié restante** des tests pour diviser le temps par 2.

**Répartition** :
- **Gemini** : Tests `Backend/Prod/tests/test_*.py` (A-M)
- **DeepSeek** : Tests `Backend/Prod/tests/test_*.py` (N-Z) + `Backend/Prod/tests/sullivan/`

---

## 1. OBJECTIF

**Réduire les échecs de tests de ~90 à <50**

**Stratégie** : Même que Gemini
1. Skip tests avec dépendances manquantes (genome vide, API externes)
2. Fix imports cassés
3. Skip tests obsolètes (fonctionnalité supprimée)
4. Documenter bugs réels dans CR

---

## 2. TESTS À TRAITER

### 2.1 Ton Périmètre (DeepSeek)

**Tests backend N-Z** :
```bash
Backend/Prod/tests/test_orchestrator.py
Backend/Prod/tests/test_plan_reader.py
Backend/Prod/tests/test_registry.py
Backend/Prod/tests/test_semantic_cache.py
Backend/Prod/tests/test_star.py
Backend/Prod/tests/test_ui_evaluator.py
Backend/Prod/tests/test_version_manager.py
```

**Tests Sullivan** :
```bash
Backend/Prod/tests/sullivan/test_*.py
```

**Tests Models** (si Gemini n'a pas fini) :
```bash
Backend/Prod/tests/models/test_*.py
```

---

## 3. MÉTHODOLOGIE

### 3.1 Phase 1 : Diagnostic

```bash
cd /Users/francois-jeandazin/AETHERFLOW
source venv/bin/activate
pytest Backend/Prod/tests/test_[n-z]*.py -v --tb=short > deepseek_tests_output.txt
```

**Analyser** :
- ImportError → Skip ou fix import
- AssertionError → Skip si dépendance externe
- AttributeError → Skip si méthode supprimée
- HTTPError → Skip si API externe

---

### 3.2 Phase 2 : Catégorisation

| Catégorie | Action |
|-----------|--------|
| **Dépendance externe** | `@pytest.mark.skip(reason="...")` |
| **Import cassé** | Fix import si évident, sinon skip |
| **Méthode supprimée** | Skip |
| **Bug réel** | Documenter dans CR, NE PAS FIXER |

---

### 3.3 Phase 3 : Fixes Rapides

**Règles** :
- ✅ Ajouter `@pytest.mark.skip`
- ✅ Fix imports évidents
- ❌ **NE PAS** modifier le code source (orchestrator.py, etc.)
- ❌ **NE PAS** créer de nouvelles fonctionnalités

---

## 4. EXEMPLES DE FIXES

### Exemple 1 : Skip Test avec Dépendance Externe

```python
@pytest.mark.skip(reason="Requires external API (Gemini Vision) not available in test env")
def test_analyze_with_vision():
    ...
```

### Exemple 2 : Fix Import

```python
# AVANT
from your_module import orchestrator

# APRÈS
from Backend.Prod.sullivan.identity import sullivan as orchestrator
```

### Exemple 3 : Skip Méthode Supprimée

```python
@pytest.mark.skip(reason="orchestrator.preview() method removed. Test obsolete.")
def test_preview_component():
    ...
```

---

## 5. COMMANDES UTILES

### Lister Tests Ton Périmètre

```bash
cd /Users/francois-jeandazin/AETHERFLOW
pytest --collect-only Backend/Prod/tests/test_[n-z]*.py Backend/Prod/tests/sullivan/
```

### Lancer Tests Ton Périmètre

```bash
pytest Backend/Prod/tests/test_[n-z]*.py Backend/Prod/tests/sullivan/ -v
```

### Compter Échecs

```bash
pytest Backend/Prod/tests/test_[n-z]*.py Backend/Prod/tests/sullivan/ -v | grep -E "FAILED|PASSED" | wc -l
```

---

## 6. CRITÈRES D'ACCEPTATION

- [ ] Tests ton périmètre : <50% échecs (idéal : <30%)
- [ ] Tous les skips documentés avec raison claire
- [ ] Aucun code source modifié (sauf tests)
- [ ] CR déposé avec liste bugs réels identifiés

---

## 7. COORDINATION AVEC GEMINI

**Communication** : Pas de collision, périmètres distincts

**Si Gemini termine avant toi** :
- Il déposera `CR_TEST_FIXES.md` dans `docs/02-sullivan/mailbox/gemini/`
- Continue ton périmètre, tu déposeras `CR_TEST_FIXES_PART2.md`

**Si tu termines avant Gemini** :
- Dépose ton CR
- Attends que Gemini finisse avant de consolider

---

## 8. LIVRAISON

**CR DeepSeek** : `docs/02-sullivan/mailbox/deepseek/CR_TEST_FIXES_PART2.md`

**Format** :
```markdown
# CR DeepSeek : Test Fixes Part 2

**Date** : 9 février 2026
**Agent** : DeepSeek
**Périmètre** : Tests N-Z + Sullivan

## ✅ Tests Traités

### Avant
- Tests échoués : X

### Après
- Tests échoués : Y
- Réduction : Z%

## 📋 Actions Prises

| Fichier | Test | Action | Raison |
|---------|------|--------|--------|
| test_registry.py | test_foo | Skip | Dépendance externe |
| ... | ... | ... | ... |

## 🐛 Bugs Réels Identifiés

1. **Bug 1** : Description
   - Fichier : `path/to/file.py:line`
   - Sévérité : Critique/Majeure/Mineure
   - Recommandation : ...

## 📊 Statistiques Finales

- Tests traités : X
- Skipped : Y
- Fixed : Z
- Bugs documentés : N

## 🚦 Verdict

GO / NO-GO pour production
```

---

## 9. AIDE SONNET

Si tu bloques :

**Import errors** :
```python
# Pattern commun
from Backend.Prod.sullivan.identity import sullivan
from Backend.Prod.models.gemini_client import GeminiClient
```

**Skip pattern** :
```python
@pytest.mark.skip(reason="Clear reason here")
def test_name():
    ...
```

---

## 10. TEMPS ESTIMÉ

**Sans parallélisation** : 2h (comme Gemini)

**Avec parallélisation** : **1h** (vous finissez en même temps)

**Gain** : **50% de temps économisé** 🎉

---

**Go ! Pendant que Gemini finit sa partie, tu gères la tienne !**

*— Sonnet (Ingénieur en Chef)*
