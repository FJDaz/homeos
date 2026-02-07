# Plan d'exécution : Mode Manager (Homeos)

Décisions d'orientation (validées) :
- **Option A** : Package top-level `homeos/` (core, construction, project, config) qui utilise Backend/Prod. CLI `homeos` pour mode/switch. Les CLI existants (`aetherflow -f`, `-q`, `vfx`) restent inchangés.
- **Ordre 1** : Couche méta (Mode Manager) d'abord, puis deux modes, puis switching, puis Intent Refactoring.
- **Génome v1** : remplace l'actuel (un seul artefact ; ScreenPlanner/CorpsGenerator lisent le genome avec intents, features, compartments).

---

## Étapes d'implémentation (Ordre 1)

### 1. Couche méta — Mode Manager
- Créer le package `homeos/` à la racine : `core`, `construction`, `project`, `config`.
- Implémenter `homeos/core/mode_manager.py` :
  - `HomeosMode` (CONSTRUCTION, PROJECT)
  - `ModeConfiguration` (charge YAML par mode)
  - `ModeManager` (singleton, détection via `.homeos_mode` ou `homeos_construction/`, `switch_mode`, `get_aetherflow()`, `get_sullivan()`)
- Fichiers de config : `homeos/config/construction_config.yaml`, `homeos/config/project_config.yaml` (z_index_layers, frontend_stack, workflow, validation_rules, components).

Référence détaillée : [homeos-core-mode_manager.py.md](homeos-core-mode_manager.py.md)

### 2. Deux modes — Adapters Aetherflow et Sullivan
- `homeos/construction/aetherflow.py` → `ConstructionAetherflow` (wrapper Backend.Prod, config construction).
- `homeos/construction/sullivan.py` → `ConstructionSullivan` (Svelte, overlay, studio).
- `homeos/project/aetherflow.py` → `ProjectAetherflow`.
- `homeos/project/sullivan.py` → `ProjectSullivan` (HTML/CSS/JS vanilla).
- Aucune modification des implémentations dans `Backend/Prod/` ; wrappers qui délèguent.

### 3. CLI Homeos
- Point d'entrée `homeos` (ou `python -m homeos.cli`) : commandes `mode`, `switch --construction` / `--project`.
- Ne pas toucher à `aetherflow` ni à `Backend/Prod/cli.py`.

### 4. Intent Refactoring (après Mode Manager)
- Pipeline IR + Sullivan Arbiter ; genome v1 unique qui remplace l'actuel.

### 5. Construction bottom-up et références
- MANIFESTE_HOMEOS_V0, design tokens, Sullivan Validation UI.

---

## Fichiers à créer (étape 1)

```
homeos/
  __init__.py
  core/
    __init__.py
    mode_manager.py
  construction/
    __init__.py
    aetherflow.py   # étape 2
    sullivan.py     # étape 2
  project/
    __init__.py
    aetherflow.py   # étape 2
    sullivan.py     # étape 2
  config/
    construction_config.yaml
    project_config.yaml
  cli.py            # étape 3
```
