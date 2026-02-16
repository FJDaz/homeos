# Feuille de Route - Correction Aetherflow

**Date** : 11 février 2026
**Auteur** : Claude Opus 4.5
**Priorité** : HAUTE (bloque les runs aetherflow)

---

## Diagnostic

### Problèmes identifiés

| # | Problème | Cause racine | Impact |
|---|----------|--------------|--------|
| 1 | `surgical_editor.py` corrompu | JSON non-appliqué écrit dans le fichier | ✅ **FIXÉ** |
| 2 | LLM génère opérations non-supportées | Prompt ne contraint pas assez le LLM | Échec runs API |
| 3 | Exécution parallèle sature rate limits | 6 steps simultanés → Groq/Deepseek timeout | Runs incomplets |
| 4 | Création fichiers utilise surgical mode | `surgical_mode=True` par défaut | Fichiers JSON au lieu de Python |

---

## Plan de correction

### PHASE A : Corrections immédiates (J1)

#### A.1 Ajouter fallback quand surgical échoue
**Fichier** : `Backend/Prod/orchestrator.py` (lignes 737-794)

**Modification** :
```python
# Quand surgical_mode échoue, écrire le code brut au lieu du JSON
if not success:
    # Fallback: extraire le code des opérations et l'écrire
    code_content = extract_code_from_operations(result.output)
    if code_content:
        file_path.write_text(code_content, encoding='utf-8')
        logger.warning(f"Surgical failed, wrote raw code to {file_path}")
```

**Effort** : 30 min

---

#### A.2 Désactiver surgical mode pour nouveaux fichiers
**Fichier** : `Backend/Prod/orchestrator.py` (ligne 667)

**Avant** :
```python
surgical_mode = step.context.get('surgical_mode', True) or (...)
```

**Après** :
```python
# Surgical mode uniquement si le fichier EXISTE et contient du code
has_existing_code = any(content is not None and len(content.strip()) > 0
                        for content in existing_files.values())
surgical_mode = has_existing_code and (
    step.context.get('surgical_mode', True) or (
        self.execution_mode in ["BUILD", "DOUBLE-CHECK"] and
        has_python_files and
        step.type in ['refactoring', 'code_generation']
    )
)
```

**Effort** : 15 min

---

### PHASE B : Améliorer le prompt surgical (J2)

#### B.1 Contraindre les opérations supportées dans le prompt
**Fichier** : `Backend/Prod/orchestrator.py` (ligne 716-717)

**Avant** :
```python
files_section += "\n\nSURGICAL MODE: Instead of generating the complete file, generate structured JSON instructions..."
files_section += '{\n  "operations": [\n    {\n      "type": "add_method|modify_method|..."'
```

**Après** :
```python
files_section += """

SURGICAL MODE INSTRUCTIONS:
Generate ONLY these operation types (no others):
- add_import: Add an import statement
- add_function: Add a standalone function (NOT a route decorator)
- add_class: Add a new class
- add_method: Add a method to an existing class
- modify_method: Modify an existing method
- replace_import: Replace one import with another

FORBIDDEN (will cause errors):
- add_route ❌
- add_to_router ❌
- add_endpoint ❌

For FastAPI routes, use add_function with the full decorated function:
{
  "type": "add_function",
  "code": "@router.get('/endpoint')\\nasync def my_endpoint(): ..."
}
"""
```

**Effort** : 20 min

---

### PHASE C : Séquentialiser l'exécution (J2-J3)

#### C.1 Ajouter option `--sequential` au CLI
**Fichier** : `Backend/Prod/cli.py`

**Ajout** :
```python
parser.add_argument('--sequential', '-seq', action='store_true',
                    help='Execute plan steps one at a time (avoids rate limiting)')
```

**Effort** : 10 min

---

#### C.2 Implémenter exécution séquentielle dans l'orchestrator
**Fichier** : `Backend/Prod/orchestrator.py`

**Logique** :
```python
if self.sequential_mode:
    for step in plan.steps:
        result = await self._execute_step(step, context)
        if not result.success:
            break
        await asyncio.sleep(2)  # Pause entre steps pour rate limits
else:
    # Exécution parallèle actuelle
    results = await asyncio.gather(*[...])
```

**Effort** : 45 min

---

### PHASE D : Tests et validation (J3)

#### D.1 Test unitaire surgical fallback
```python
def test_surgical_fallback_writes_code():
    """When surgical fails, raw code should be written."""
    ...
```

#### D.2 Test intégration séquentiel
```bash
./aetherflow -f --plan plan_test.json --sequential
```

#### D.3 Test avec plan API complet
```bash
./aetherflow -f --plan plan_phase3_api_rest.json --sequential
```

**Effort** : 1h

---

## Planning

| Jour | Phase | Livrables | Validation |
|------|-------|-----------|------------|
| **J1** (aujourd'hui) | A | Fallback + désactivation surgical nouveaux fichiers | `python -c "import ast; ..."` |
| **J2** | B + C.1 | Prompt amélioré + option CLI | `./aetherflow --help` |
| **J3** | C.2 + D | Exécution séquentielle + tests | Run complet plan_phase3 |

---

## Effort total estimé

| Phase | Effort |
|-------|--------|
| A | 45 min |
| B | 20 min |
| C | 55 min |
| D | 1h |
| **Total** | ~3h |

---

## Risques

| Risque | Mitigation |
|--------|------------|
| Fallback écrit du code invalide | Validation AST avant écriture |
| Exécution séquentielle trop lente | Option parallèle reste dispo |
| LLM ignore les instructions | Double-check avec regex |

---

## Validation finale

**Critère de succès** :
```bash
# Ce run doit compléter 6/6 steps sans erreur
./aetherflow -f --plan plan_phase3_api_rest.json --sequential
```

---

**Prêt à commencer Phase A ?**
