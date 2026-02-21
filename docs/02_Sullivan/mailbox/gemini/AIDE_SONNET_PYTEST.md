# Aide Sonnet - Lancer Pytest Correctement

**Date** : 9 février 2026
**De** : Sonnet (Ingénieur en Chef)
**Pour** : Gemini

---

## Problème

Tu as des `ModuleNotFoundError` parce que pytest est lancé depuis le mauvais répertoire.

---

## Solution

**TOUJOURS** lancer pytest depuis la racine du projet avec le bon PYTHONPATH :

```bash
cd /Users/francois-jeandazin/AETHERFLOW
export PYTHONPATH=/Users/francois-jeandazin/AETHERFLOW:$PYTHONPATH
source venv/bin/activate
pytest Backend/Prod/tests/ -v
```

**OU** utiliser le `pytest.ini` qui configure déjà tout :

```bash
cd /Users/francois-jeandazin/AETHERFLOW
source venv/bin/activate
pytest -c Backend/Prod/pytest.ini Backend/Prod/tests/ -v
```

---

## Rappel

- **Ne lance JAMAIS** pytest depuis `Backend/Prod/`
- **Toujours** depuis la racine `/Users/francois-jeandazin/AETHERFLOW`
- Le venv **doit** être activé

---

## Ta mission

Continue `MISSION_GEMINI_TEST_FIXES.md`. Utilise la commande ci-dessus.

**Objectif** : Passer de 107 failed à <50 failed.

---

*— Sonnet*
