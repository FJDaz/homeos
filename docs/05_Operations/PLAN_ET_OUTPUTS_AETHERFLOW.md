# Plan exact et fichiers générés — AETHERFLOW -q / -f

**Date** : 2026-02-01

---

## 1. Plan utilisé quand on lance -q ou -f

Le plan n’est **pas fixé** dans le CLI : il est passé en argument avec **`--plan <fichier.json>`**.

**Exemples de commandes :**

```bash
# IR (inventaire) — 5 sections fusionnées en un seul fichier
./run_aetherflow.sh -f --plan Backend/Notebooks/benchmark_tasks/plan_phase3a_etape1_chunked.json

# Patch test (1 step, insert fragment)
./run_aetherflow.sh -f --plan Backend/Notebooks/benchmark_tasks/plan_studio_patch_test.json

# Sans --output : répertoire de base = settings.OUTPUT_DIR (défaut: output)
./run_aetherflow.sh -q --plan Backend/Notebooks/benchmark_tasks/plan_phase3a_etape1_chunked.json
```

**Plan utilisé pour l’IR (inventaire)** :  
`Backend/Notebooks/benchmark_tasks/plan_phase3a_etape1_chunked.json`

- **task_id** : `phase3a-etape1-ir-chunked`
- **steps** : 5 (step_1 … step_5), chacun produit une section Markdown du rapport IR
- **metadata.output_merge** :
  - **file** : `output/studio/ir_inventaire.md`
  - **steps** : `["step_1", "step_2", "step_3", "step_4", "step_5"]`

Après exécution, le workflow concatène les sorties de ces 5 steps (dans l’ordre) et écrit le résultat dans `output/studio/ir_inventaire.md`.

---

## 2. Où sont les fichiers générés

**Répertoire de base** : `args.output` ou `settings.output_dir` (défaut : **`output`**).

### En **-q** (PROTO)

| Élément | Chemin |
|--------|--------|
| Sorties des steps | **`output/fast/step_outputs/`** |
| Fichier par step | `step_1.txt`, `step_1_code.txt`, `step_2.txt`, … |
| Apply | Utilise le contenu de **`output/fast/step_outputs/`** |
| Merge (si output_merge dans le plan) | Écrit dans le chemin indiqué dans le plan (ex. `output/studio/ir_inventaire.md`) en lisant les steps depuis `output/fast/` |
| Métriques | `output/fast/metrics_<task_id>.json`, `.csv` |
| Validation | `output/validation/` |

### En **-f** (PROD)

| Élément | Chemin |
|--------|--------|
| Brouillon FAST | **`output/fast_draft/step_outputs/`** (step_1.txt, step_1_code.txt, …) |
| Sorties BUILD (utilisées pour l’apply) | **`output/build_refactored/step_outputs/`** |
| Fichier par step | `step_1.txt`, `step_1_code.txt`, `step_2.txt`, … |
| Apply | Utilise le contenu de **`output/build_refactored/step_outputs/`** |
| Merge (si output_merge) | Lit les steps depuis **`output/build_refactored/`**, écrit dans le fichier du plan (ex. `output/studio/ir_inventaire.md`) |
| Métriques | `output/build_refactored/metrics_<task_id>.json`, `.csv` |
| Validation | `output/validation/` |

**Lecture des step outputs** (`get_step_output`) :  
On utilise en priorité **`step_X_code.txt`** (contenu “code” sans structure), sinon **`step_X.txt`** (sortie brute du step).

---

## 3. Exemple concret (plan IR en -f)

**Plan** : `plan_phase3a_etape1_chunked.json`  
**Commande** : `./run_aetherflow.sh -f --plan Backend/Notebooks/benchmark_tasks/plan_phase3a_etape1_chunked.json`

**Fichiers générés :**

1. **`output/fast_draft/step_outputs/`**  
   step_1.txt, step_1_code.txt, step_2.txt, step_2_code.txt, … step_5.txt, step_5_code.txt (brouillon FAST).

2. **`output/build_refactored/step_outputs/`**  
   step_1.txt, step_1_code.txt, … step_5.txt, step_5_code.txt (version BUILD utilisée pour l’apply et le merge).

3. **`output/studio/ir_inventaire.md`**  
   Fichier final produit par **merge** : concaténation des 5 step outputs (depuis `output/build_refactored/`) dans l’ordre, avec séparateur `\n\n---\n\n`, écrit dans le chemin indiqué par `metadata.output_merge.file`.

**Exemple de contenu d’un step** (premières lignes de `output/build_refactored/step_outputs/step_1_code.txt`) :

```markdown
# Inventaire IR — Phase 3 A Étape 1

Ce document sert de base pour l'arbitrage Sullivan (étape 2) et les décisions Garder / Réserve / Obsolète.

Source genome : `output/studio/homeos_genome.json`
Source intentions : `docs/04-homeos/PRD_HOMEOS.md`

## 1. Inventaire Genome (Implémentation actuelle)

### 1.1 Métadonnées
...
```

---

## 4. Résumé

| Mode | Répertoire des step outputs | Fichier merge (ex. IR) |
|------|-----------------------------|-------------------------|
| **-q** | `output/fast/step_outputs/` | `output/studio/ir_inventaire.md` (si output_merge dans le plan) |
| **-f** | `output/build_refactored/step_outputs/` | `output/studio/ir_inventaire.md` (idem) |

Le **plan exact** est toujours celui passé en **`--plan <fichier.json>`**. Pour l’IR, c’est `Backend/Notebooks/benchmark_tasks/plan_phase3a_etape1_chunked.json`.
