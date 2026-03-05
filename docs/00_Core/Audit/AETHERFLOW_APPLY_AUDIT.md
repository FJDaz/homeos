# AetherFlow "Apply" — Audit Complet & Plan de Remédiation

> **Date :** 2026-03-02
> **Auditeur :** Claude (Sonnet 4.6) — vérification croisée code source
> **Scope :** Pipeline d'application de code (Apply) — tous modes (PROD, PROTO, FRD)
> **Statut :** AUDIT VÉRIFIÉ — 9 issues identifiées (3 critiques, 3 hautes, 2 moyennes, 1 erreur factuelle)

---

## Table des matières

1. [Résumé exécutif](#1-résumé-exécutif)
2. [Issues confirmées (audit initial)](#2-issues-confirmées-audit-initial)
3. [Issues supplémentaires découvertes](#3-issues-supplémentaires-découvertes)
4. [Erreur factuelle dans l'audit initial](#4-erreur-factuelle-dans-laudit-initial)
5. [Cartographie des flux d'apply](#5-cartographie-des-flux-dapply)
6. [Solutions proposées (amendées)](#6-solutions-proposées-amendées)
7. [Checklist d'implémentation](#7-checklist-dimplémentation)
8. [Annexe — Références fichiers](#8-annexe--références-fichiers)

---

## 1. Résumé exécutif

Le pipeline "Apply" d'AetherFlow — responsable d'écrire le code généré par les LLMs sur le disque — souffre de **défauts architecturaux systémiques** qui expliquent la majorité des échecs d'auto-apply observés en production.

### Diagnostic en une phrase

> Il existe **3 chemins d'apply concurrents** (Orchestrator inline, Phase 2.5 ProdWorkflow, claude_helper), aucun ne fonctionne correctement seul, et leur interaction produit des résultats imprévisibles.

### Tableau de synthèse

| # | Issue | Sévérité | Fichier source | Ligne(s) |
|---|-------|----------|----------------|----------|
| A | Refactoring crée `.generated` au lieu d'overwrite | **HAUTE** | `claude_helper.py` | 293-305 |
| B | VETO surgical sans fallback full-file (fichiers existants) | **HAUTE** | `orchestrator.py` | 1115-1141 |
| C | Double chemin d'apply (Orchestrator + Phase 2.5) | **HAUTE** | `prod.py` + `orchestrator.py` | 137 / 1045 |
| D | Dépendance `astunparse` fragile | Moyenne | `surgical_editor.py` | 14-18 |
| E | `auto_apply` existe déjà — audit initial propose de le recréer | Erreur factuelle | `prod.py` | 330 |
| F | Asymétrie FAST/BUILD non documentée | Basse | `orchestrator.py` | 928-935 |
| **G** | **`get_step_output()` lit output pollué (pas `_code.txt`)** | **HAUTE** | `claude_helper.py` | 140 |
| **H** | **`PostApplyValidator` = dead code (jamais appelé)** | **Moyenne** | `post_apply_validator.py` | entier |
| **I** | **`merge_step_outputs_to_file` = ImportError latente** | **CRITIQUE** | 3 workflows | — |

---

## 2. Issues confirmées (audit initial)

### A. Stratégie "Refactoring" conservative — `claude_helper.py:293-305`

**Statut :** ✅ CONFIRMÉ par lecture du code source.

**Code incriminé :**

```python
# claude_helper.py — apply_generated_code()
if step_type == "refactoring":
    if target_file.exists():
        generated_file = target_file.with_suffix(f".generated{target_file.suffix}")
        generated_file.write_text(code_content, encoding="utf-8")
        logger.warning(
            f"REFACTORING: Generated code saved to {generated_file} "
            f"(manual merge required with {target_file})"
        )
        return True  # ← PROBLÈME : retourne True même sans modification
```

**Analyse :**

- Quand un step est `type: "refactoring"` et que le fichier cible existe déjà, AetherFlow **refuse l'overwrite** et crée un fichier sibling `.generated.py` (ou `.generated.js`, `.generated.css`, etc.).
- La fonction retourne `True`, ce qui masque l'échec vis-à-vis de l'appelant (`_apply_refactored_code()` dans `prod.py`). Le pipeline croit que l'apply a réussi alors que le fichier cible n'a **pas été modifié**.
- Ce comportement affecte **tous les types de fichiers**, pas seulement Python. L'audit initial ne mentionnait que `.py`.

**Impact :** Tout step de refactoring sur un fichier existant produit un fichier fantôme que personne ne merge jamais. Les `.generated.*` s'accumulent dans le workspace (preuve : 20+ fichiers `.generated.py` trouvés dans `Backend/Prod/sullivan/`).

**Preuve filesystem :**
```
Backend/Prod/sullivan/studio_routes.generated.py
Backend/Prod/sullivan/identity.generated.py
Backend/Prod/sullivan/registry.generated.py
Backend/Prod/sullivan/intent_translator.generated.py
Backend/Prod/sullivan/modes/designer_mode.generated.py
Backend/Prod/sullivan/library/elite_library.generated.py
... (20+ fichiers)
```

---

### B. VETO Surgical Mode — `orchestrator.py:1115-1141`

**Statut :** ✅ CONFIRMÉ avec nuances.

**Code incriminé :**

```python
# orchestrator.py — _execute_step()
elif not success:
    # VETO: Stop the append fallback and alert the user
    error_msg = f"Surgical modification failed for {file_path}: {modified_code}"
    logger.error(f"❌ {error_msg}")

    alert_banner = "\n" + "!" * 80 + "\n"
    alert_banner += "⚠️  ALERT: MODIFICATION REJECTED\n"
    alert_banner += f"The surgical edit for {file_path} failed or produced invalid code.\n"
    alert_banner += "THE FILE HAS BEEN PRESERVED IN ITS ORIGINAL STATE TO PREVENT CORRUPTION.\n"
    alert_banner += "!" * 80 + "\n"

    logger.critical(alert_banner)
    application_errors.append(f"{file_path}: {modified_code}")
```

**Analyse :**

Le VETO est intentionnel — il empêche la corruption de fichiers en cas d'output LLM mal formaté. Mais il est **trop brutal** pour les fichiers existants :

1. **Asymétrie création/modification :** Pour les **nouveaux fichiers**, un fallback existe (lignes 1073-1092) qui extrait le code des opérations JSON et écrit directement. Pour les **fichiers existants**, aucun fallback — VETO total.

2. **Protection `_`-préfixés :** `SurgicalApplier._validate_operation()` (surgical_editor.py:480-488) bloque tout patch LLM ciblant une méthode `_xxx` (préfixe underscore). Légitime pour protéger les metadata système, mais source de VETO silencieux pour du code privé valide :

```python
# surgical_editor.py — _validate_operation()
if op.op_type in ('modify_method', 'add_method') and op.target:
    target_name = op.target.split('.', 1)[-1]
    if target_name.startswith('_'):
        return (f"Protected target '{op.target}': LLM patches may not target "
                f"'_'-prefixed members (system metadata). Use CODE DIRECT instead.")
```

3. **Chaîne de fallback incomplète :** Le mode surgical utilise d'abord le range-based replacement (preserving comments), puis `astunparse` si le range échoue. Mais si les deux échouent → VETO sans tentative de full-file overwrite.

**Impact :** Tout refactoring chirurgical qui échoue (JSON mal formaté, cible `_`-préfixée, AST invalide) résulte en **zéro modification** même si le LLM a produit du code valide dans le même output.

---

### C. Double chemin d'apply — `orchestrator.py:1045` vs `prod.py:137-148`

**Statut :** ✅ CONFIRMÉ — plus grave que décrit dans l'audit initial.

**Flux de données observé :**

```
ProdWorkflow.execute()
│
├── Phase 1: FAST (Orchestrator mode FAST)
│   └── Pas de surgical → steps code_generation écrasent directement
│
├── Phase 2: BUILD (Orchestrator mode BUILD)
│   └── surgical_mode = True pour refactoring steps
│       ├── Surgical réussit → fichier modifié inline ✅
│       └── Surgical échoue → VETO, fichier intact ❌
│
├── Phase 2.5: _apply_refactored_code() ← REDONDANT
│   └── Appelle claude_helper.apply_generated_code()
│       └── step_type == "refactoring" → crée .generated.py (même si surgical a déjà réussi)
│
└── Phase 3: DOUBLE-CHECK (validation)
```

**Scénario de double-application confirmé :**

1. Orchestrator BUILD exécute un step `refactoring` → surgical réussit → fichier modifié ✅
2. Phase 2.5 re-lit le même step output → appelle `apply_generated_code()` → type = `refactoring` + fichier existe → crée `.generated.py` en doublon ❌

**Scénario de double-échec :**

1. Orchestrator BUILD → surgical échoue → VETO → fichier intact
2. Phase 2.5 → lit output pollué (voir Issue G) → `_extract_code_blocks()` peut échouer → `.generated.py` avec contenu incorrect ou pas de code

---

## 3. Issues supplémentaires découvertes

### G. `get_step_output()` lit l'output pollué — `claude_helper.py:140`

**Sévérité : HAUTE**

**Le problème :**

L'Orchestrator sauvegarde **2 fichiers** par step (`orchestrator.py:1225-1249`) :

| Fichier | Contenu | Utilisé par |
|---------|---------|-------------|
| `step_1_code.txt` | Code seul (extrait via `split_structure_and_code()`) | **RIEN** |
| `step_1.txt` | Output complet avec headers metadata | `get_step_output()` |

Mais `get_step_output()` ne lit **que** le fichier `.txt` complet :

```python
# claude_helper.py:140
def get_step_output(step_id: str, output_dir: str = "output") -> Optional[str]:
    output_file = Path(output_dir) / "step_outputs" / f"{step_id}.txt"
    if output_file.exists():
        return output_file.read_text(encoding="utf-8")
    return None
```

Le fichier `step_1.txt` contient des headers metadata :

```
Step: step_1
Description: Implement user authentication
Type: refactoring
Success: True
Tokens: 2847
Cost: $0.0142
Time: 3200ms

============================================================

[... le vrai code commence ici ...]
```

**Phase 2.5 passe donc ces headers metadata à `_extract_code_blocks()`**, qui cherche des blocs markdown dans un output pollué.

**Test qui confirme le bug :** `test_apply_phase.py:95-101` attend la préférence `_code.txt` :

```python
def test_get_step_output_prefers_code_txt(tmp_path):
    """get_step_output préfère step_X_code.txt quand il existe."""
    out = tmp_path / "step_outputs"
    out.mkdir()
    (out / "step_1.txt").write_text("full output with header\nand tree\n├── x")
    (out / "step_1_code.txt").write_text("code only content")
    assert get_step_output("step_1", str(tmp_path)) == "code only content"
    # ^^^ CE TEST ÉCHOUE — l'implémentation ne lit que .txt
```

**Impact :** `_extract_code_blocks()` peut extraire du code incorrect ou échouer silencieusement à cause des headers. Cela explique une partie des `.generated.py` vides ou avec du contenu tronqué observés en production.

---

### H. `PostApplyValidator` = dead code — `core/post_apply_validator.py`

**Sévérité : Moyenne (opportunité manquée)**

**Le module existe** (359 lignes) avec des fonctionnalités complètes :

- Validation syntaxique multi-langage (Python via `ast.parse`, JSON, YAML, HTML, JS/TS via `node --check`)
- Découverte automatique de tests associés (`foo.py` → `test_foo.py`, `foo_test.py`, `tests/test_foo.py`)
- Exécution pytest/jest ciblée (pas la suite complète)
- Auto-rollback via `git checkout` en cas d'échec

**Mais il n'est JAMAIS importé ni appelé** depuis le pipeline d'apply :

```
Recherche "PostApplyValidator" / "validate_after_apply" dans :
- orchestrator.py : 0 résultats
- workflows/prod.py : 0 résultats
- workflows/proto.py : 0 résultats
- workflows/frd.py : 0 résultats
```

Seule référence : `tests/test_new_file_creation.py:73` (un test unitaire isolé).

**Impact :** AetherFlow écrit du code sur le disque sans jamais valider la syntaxe ni lancer les tests associés. Le `PostApplyValidator` résoudrait une partie des Issues A et B s'il était branché dans le pipeline.

---

### I. `merge_step_outputs_to_file` = ImportError latente — 3 workflows

**Sévérité : CRITIQUE**

**Le problème :** Trois workflows importent une fonction qui **n'existe nulle part** dans le codebase :

```python
# prod.py:155
from ..claude_helper import merge_step_outputs_to_file

# frd.py:128
from ..claude_helper import merge_step_outputs_to_file

# proto.py:85
from ..claude_helper import merge_step_outputs_to_file
```

**Recherche exhaustive :**

```
grep -r "def merge_step_outputs" Backend/Prod/ → 0 résultats
grep -r "def merge_step_outputs" . → 0 résultats (codebase entier)
```

La fonction est protégée par un guard conditionnel (`if output_merge and output_dir:`) dans `prod.py:150-158`, ce qui explique pourquoi le crash n'est pas systématique — il ne se produit que quand un plan JSON contient `metadata.output_merge`.

**Impact :** Tout plan avec `output_merge` provoque un `ImportError` à runtime. C'est une bombe à retardement pour les plans multi-steps qui fusionnent leurs outputs en un seul fichier.

---

## 4. Erreur factuelle dans l'audit initial

### E. Solution 2 propose de créer `auto_apply` — il existe déjà

L'audit initial propose :

> *"Introduce a global or step-level configuration `auto_apply: true`."*

**Ce flag existe déjà** dans `prod.py:330` :

```python
# prod.py — _apply_refactored_code()
# GUARD: respect explicit opt-out via context flag
if step.context and not step.context.get("auto_apply", True):
    logger.debug(f"Auto-apply disabled for step {step.id} (auto_apply=false in context)")
    continue
```

Le défaut est `True` (auto-apply activé sauf opt-out explicite). Le problème n'est pas l'absence du flag — c'est que `apply_generated_code()` dans `claude_helper.py` **ignore complètement ce flag** et crée `.generated.*` pour tout step `refactoring` sur fichier existant, indépendamment de `auto_apply`.

---

## 5. Cartographie des flux d'apply

### Flux actuel (dysfonctionnel)

```
LLM Output
    │
    ├─── [MODE FAST] ──────────────────────────────────────────┐
    │    Orchestrator (surgical_mode=False)                     │
    │    └── step.type == "code_generation" → overwrite direct  │ ✅ OK
    │                                                           │
    ├─── [MODE BUILD] ─────────────────────────────────────────┤
    │    Orchestrator (surgical_mode=True si refactoring+.py)   │
    │    ├── Surgical réussit → modifie fichier inline          │ ✅ OK
    │    └── Surgical échoue → VETO total                       │ ❌ Issue B
    │                                                           │
    ├─── [Phase 2.5 ProdWorkflow] ─────────────────────────────┤
    │    _apply_refactored_code()                               │
    │    ├── get_step_output() → lit output pollué              │ ❌ Issue G
    │    ├── _extract_code_blocks() → extraction fragile        │
    │    └── apply_generated_code()                             │
    │        └── refactoring + exists → .generated.*            │ ❌ Issue A
    │                                                           │
    └─── [PostApplyValidator] ─────────────────────────────────┤
         Jamais appelé                                          │ ❌ Issue H
```

### Flux cible (proposé)

```
LLM Output
    │
    └─── ApplyEngine (unifié) ──────────────────────────────────┐
         │                                                       │
         ├── 1. Surgical Edit (si JSON valide + AST match)       │
         │   └── Succès → écriture + validation                  │
         │                                                       │
         ├── 2. Smart Overwrite (fallback si surgical échoue)    │
         │   └── Extraire code blocks → .bak → overwrite         │
         │                                                       │
         ├── 3. Review Fallback (si aucun code extractible)      │
         │   └── .generated.* + alerte utilisateur               │
         │                                                       │
         └── 4. PostApplyValidator (systématique)                │
             ├── ast.parse() / node --check                      │
             ├── Tests associés (pytest/jest)                     │
             └── Auto-rollback si échec                          │
```

---

## 6. Solutions proposées (amendées)

### Solution 1 : Unified `ApplyEngine` (priorité 1)

Créer une classe unique `ApplyEngine` qui remplace les 3 chemins actuels :

```
Backend/Prod/core/apply_engine.py
```

Hiérarchie d'application best-effort :

1. **Surgical Edit** — Si output contient du JSON surgical valide ET que l'AST du fichier cible est parsable. Utilise le range-based replacement en priorité (préserve comments/formatting).

2. **Smart Overwrite** — Si le surgical échoue OU si le step n'est pas `refactoring`, extraire les code blocks de l'output et overwrite le fichier cible. Créer un `.bak` avant overwrite pour rollback.

3. **Review Fallback** — Uniquement si aucun code extractible n'est trouvé dans l'output. Crée `.generated.*` et log un warning explicite. **Ce mode ne retourne PAS `True`** — il retourne un état `"review_needed"`.

### Solution 2 : Brancher `PostApplyValidator` (priorité 1)

Intégrer `PostApplyValidator` dans `ApplyEngine` :

- Après chaque écriture : `validate_and_test(file_path, run_tests=True, auto_rollback=True)`
- En mode `auto_rollback=True` : si la syntaxe est invalide ou les tests échouent, `git checkout -- file` automatique
- Cela remplace le VETO brutal par un filet de sécurité intelligent

### Solution 3 : Fix `get_step_output()` (priorité 1)

Implémenter la préférence `_code.txt` déjà prévue par les tests :

```python
def get_step_output(step_id: str, output_dir: str = "output") -> Optional[str]:
    outputs_dir = Path(output_dir) / "step_outputs"
    # Préférer le fichier code-only (sans headers metadata)
    code_file = outputs_dir / f"{step_id}_code.txt"
    if code_file.exists():
        return code_file.read_text(encoding="utf-8")
    # Fallback sur le fichier complet
    full_file = outputs_dir / f"{step_id}.txt"
    if full_file.exists():
        return full_file.read_text(encoding="utf-8")
    return None
```

### Solution 4 : Supprimer Phase 2.5 de ProdWorkflow (priorité 2)

Une fois `ApplyEngine` en place dans l'Orchestrator :

- Supprimer `_apply_refactored_code()` de `prod.py`
- L'Orchestrator est le seul responsable de l'apply
- `ProdWorkflow` se concentre sur l'orchestration des phases (FAST → BUILD → DOUBLE-CHECK)

### Solution 5 : Implémenter `merge_step_outputs_to_file` (priorité 2)

Créer la fonction manquante dans `claude_helper.py` :

```python
def merge_step_outputs_to_file(
    step_ids: List[str],
    output_dir: str,
    target_path: Path
) -> bool:
    """Merge multiple step outputs into a single file."""
    parts = []
    for step_id in step_ids:
        content = get_step_output(step_id, output_dir)
        if content:
            parts.append(content)
    if parts:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text("\n\n".join(parts), encoding="utf-8")
        return True
    return False
```

### Solution 6 : Fuzzy Surgical Parser (priorité 3)

Améliorer `SurgicalInstructionParser.parse_instructions()` pour tolérer :

- JSON avec trailing commas
- Code fourni en raw text en dehors du champ `"code"` du JSON
- Blocs markdown mal fermés
- Indentation mixte tabs/spaces dans le champ `"code"`

---

## 7. Checklist d'implémentation

### Phase 1 — Fixes critiques (stop-the-bleeding)

- [ ] **I.** Implémenter `merge_step_outputs_to_file` dans `claude_helper.py` (éviter l'ImportError)
- [ ] **G.** Fix `get_step_output()` pour préférer `_code.txt` (le test existe déjà)
- [ ] **B.** Ajouter fallback full-file dans l'Orchestrator après VETO surgical sur fichiers existants

### Phase 2 — Refactoring apply pipeline

- [ ] **A+C.** Créer `ApplyEngine` unifié dans `Backend/Prod/core/apply_engine.py`
- [ ] **H.** Brancher `PostApplyValidator` dans `ApplyEngine` (validation + auto-rollback)
- [ ] **C.** Supprimer `_apply_refactored_code()` de `prod.py` (et l'appel Phase 2.5)
- [ ] **E.** Faire respecter le flag `auto_apply` dans `ApplyEngine` (pas dans `claude_helper.py`)
- [ ] **A.** Nettoyer les 20+ fichiers `.generated.*` orphelins dans `Backend/Prod/sullivan/`

### Phase 3 — Hardening

- [ ] **D.** Ajouter `astunparse` au `requirements.txt` comme dépendance hard (pas optional)
- [ ] **F.** Documenter l'asymétrie FAST/BUILD pour le mode surgical dans les guidelines plan JSON
- [ ] Solution 6 : Fuzzy Surgical Parser (tolérance JSON malformé)
- [ ] Tests d'intégration end-to-end du pipeline apply (plan → execute → verify file on disk)

---

## 8. Annexe — Références fichiers

### Fichiers du pipeline Apply

| Fichier | Rôle | Lignes clés |
|---------|------|-------------|
| `Backend/Prod/claude_helper.py` | Extraction code blocks + apply | L140 (get_step_output), L244-322 (apply_generated_code) |
| `Backend/Prod/orchestrator.py` | Orchestration steps + surgical apply inline | L904-936 (surgical mode activation), L1045-1149 (apply inline), L1210-1249 (save outputs) |
| `Backend/Prod/workflows/prod.py` | Workflow PROD (FAST→BUILD→DOUBLE-CHECK) | L137-148 (Phase 2.5), L291-390 (_apply_refactored_code) |
| `Backend/Prod/core/surgical_editor.py` | Édition AST chirurgicale | L265-353 (parser), L446-674 (applier), L914-1054 (SurgicalEditor) |
| `Backend/Prod/core/post_apply_validator.py` | Validation post-apply (DEAD CODE) | L19-358 (entier) |

### Fichiers `.generated.*` orphelins (à nettoyer)

```
Backend/Prod/sullivan/planner/__init__.generated.py
Backend/Prod/sullivan/analyzer/design_analyzer.generated.py
Backend/Prod/sullivan/modes/__init__.generated.py
Backend/Prod/sullivan/generator/design_to_html.generated.py
Backend/Prod/sullivan/studio_routes.generated.py
Backend/Prod/sullivan/identity.generated.py
Backend/Prod/sullivan/registry.generated.py
Backend/Prod/sullivan/intent_translator.generated.py
Backend/Prod/sullivan/modes/designer_mode.generated.py
Backend/Prod/sullivan/library/elite_library.generated.py
Backend/Prod/sullivan/recommender/contextual_recommender.generated.py
Backend/Prod/sullivan/builder/corps_generator.generated.py
Backend/Prod/sullivan/analyzer/design_principles_extractor.generated.py
Backend/Prod/sullivan/analyzer/ui_inference_engine.generated.py
Backend/Prod/sullivan/analyzer/pattern_analyzer.generated.py
```

---

*Rapport généré par Claude (Sonnet 4.6) — vérification croisée sur code source le 2026-03-02.*
*Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>*
