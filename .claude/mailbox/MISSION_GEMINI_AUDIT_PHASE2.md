# MISSION GEMINI : Audit Codebase - Phase 2 (Fix Tests)

**Date** : 8 février 2026
**Assigné à** : Gemini (Terminal)
**Statut** : EN ATTENTE
**Prérequis** : Phase 1 ✅ TERMINÉE

---

## 🎯 OBJECTIF

Corriger les erreurs de collection pytest (24 erreurs) pour permettre l'exécution des tests.

---

## 📋 TÂCHES À EXÉCUTER (dans l'ordre)

### 1. Installer pytest-asyncio

```bash
cd /Users/francois-jeandazin/AETHERFLOW && source venv/bin/activate
pip install pytest-asyncio pytest-cov
```

---

### 2. Lister les erreurs d'import exactes

```bash
cd /Users/francois-jeandazin/AETHERFLOW && source venv/bin/activate
pytest Backend/Prod/tests --collect-only 2>&1 | grep -E "(ImportError|ModuleNotFoundError|No module)" | head -30
```

---

### 3. Corriger les imports cassés

Les fichiers suivants ont des imports problématiques :

#### 3.1 Remplacer `from auditor import` par le bon chemin

```bash
# Trouver les fichiers avec l'import cassé
grep -r "from auditor import" Backend/Prod/tests/
grep -r "import auditor" Backend/Prod/tests/
```

**Action** : Remplacer par `from sullivan.auditor import ...` ou le chemin correct.

#### 3.2 Supprimer les imports placeholder `your_module`

```bash
# Trouver les fichiers avec placeholder
grep -r "your_module" Backend/Prod/tests/
```

**Action** : Remplacer `your_module` par le vrai module ou commenter le test.

---

### 4. Configurer pytest.ini pour asyncio

Créer ou modifier `Backend/Prod/pytest.ini` :

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
filterwarnings =
    ignore::DeprecationWarning
```

---

### 5. Relancer pytest

```bash
cd /Users/francois-jeandazin/AETHERFLOW && source venv/bin/activate
pytest Backend/Prod/tests -v --tb=short 2>&1 | tee docs/support/audit/pytest_report.txt | tail -100
```

---

### 6. Si des tests échouent encore, lister les fichiers problématiques

```bash
pytest Backend/Prod/tests --collect-only 2>&1 | grep "ERROR" | head -20
```

---

## 📝 COMPTE-RENDU À FOURNIR

Créer : `/Users/francois-jeandazin/AETHERFLOW/.claude/mailbox/CR_GEMINI_AUDIT_PHASE2.md`

```markdown
# CR GEMINI : Audit Phase 2

**Date** : [date]
**Statut** : ✅ TERMINÉ / ⚠️ PARTIEL / ❌ BLOQUÉ

## Résultats

| Tâche | Statut | Notes |
|-------|--------|-------|
| pytest-asyncio | ✅/❌ | ... |
| Fix imports auditor | ✅/❌ | X fichiers corrigés |
| Fix imports your_module | ✅/❌ | X fichiers corrigés |
| pytest.ini | ✅/❌ | ... |
| pytest run | ✅/❌ | X passed, Y failed, Z errors |

## Imports Corrigés

| Fichier | Avant | Après |
|---------|-------|-------|
| test_xxx.py | `from auditor` | `from sullivan.auditor` |

## Tests Exécutés

- Total : X
- Passed : X
- Failed : X
- Errors : X

## Prochaines Actions Suggérées

[...]
```

---

## ⚠️ ATTENTION

- **NE PAS** supprimer des fichiers de test
- **NE PAS** modifier le code source (seulement les tests)
- Si un import est vraiment cassé, **commenter le test** avec `# TODO: fix import`

---

**Merci Gemini !**
