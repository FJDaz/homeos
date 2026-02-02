---
name: aetherflow-quickstart
description: Run AETHERFLOW CLI workflows (quick PROTO, full PROD), show costs and cache stats. Use when the user wants to run aetherflow, execute a plan, run -q/-f, check --costs or --stats, or when AETHERFLOW commands fail with exit 136 in Cursor.
---

# AETHERFLOW Quick Start

## Ordres aetherflow -xxx : prioritaires dans le contexte

Les ordres du type **aetherflow -q**, **aetherflow -f**, **aetherflow -vfx**, etc. sont **prioritaires/propriétaires** dans le contexte : quand l'utilisateur donne un tel ordre (ex. « Phase 1 Aetherflow -q », « aetherflow -q »), l'agent doit interpréter qu'il faut **exécuter le workflow AETHERFLOW via le CLI** (avec le flag indiqué et éventuellement un plan), et non pas faire le travail directement dans l'IDE (éditions de fichiers, commandes manuelles). Si un plan est fourni ou implicite, lancer `./run_aetherflow.sh -q --plan <plan>` (ou -f, -vfx selon le flag). Ne pas substituer par des modifications manuelles sauf si l'utilisateur demande explicitement de faire autrement.

## When to use

- User asks to run AETHERFLOW, build a plan, run quick/full workflow, or check costs/cache.
- User gives an order like "aetherflow -q", "Phase X Aetherflow -f" → treat as priority: run AETHERFLOW CLI, do not do the work directly in the IDE.
- User hits exit code 136 or base64/dump_zsh_state errors when running AETHERFLOW in Cursor.

## Commands (from project root)

| Goal | Command |
|------|---------|
| Quick (PROTO) | `./aetherflow -q --plan <plan.json>` |
| Full (PROD) | `./aetherflow -f --plan <plan.json>` |
| Costs | `./aetherflow --costs` |
| Cache stats | `./aetherflow --stats` |

## Cursor: use the wrapper script first

In Cursor, prefer **run_aetherflow.sh** to avoid shell hooks (base64/dump_zsh_state):

```bash
./run_aetherflow.sh -q --plan Backend/Notebooks/benchmark_tasks/plan_studio_genome_frontend.json
./run_aetherflow.sh -f --plan <plan.json> --output <dir>
./run_aetherflow.sh --costs
./run_aetherflow.sh --stats
```

The script uses `/bin/bash` directly and delegates to `python3 -m Backend.Prod.cli`, bypassing zsh hooks. Ensure the project venv is activated or `python3` has dependencies (`pip install -r requirements.txt`) before running.

## Examples

```bash
./aetherflow -q --plan Backend/Notebooks/benchmark_tasks/test_workflow_proto.json
./run_aetherflow.sh -q --plan Backend/Notebooks/benchmark_tasks/plan_studio_genome_frontend.json
./aetherflow -f --plan Backend/Notebooks/benchmark_tasks/correction_patch_pattern_analyzer.json --output output/test
./aetherflow --costs
```

## If commands still fail in Cursor (exit 136, base64, dump_zsh_state)

Cursor may not expose a "disable hooks" option (no hooks configured). Suggest in order:

1. **Run in an external terminal** (Terminal.app, iTerm) – most reliable when hooks can’t be disabled.
2. **Wrapper script** (in Cursor): `./run_aetherflow.sh -q --plan <plan.json>` – may still hit 136 if Cursor wraps the command.
3. **zshrc workaround**: add to `~/.zshrc`: `type dump_zsh_state &>/dev/null || dump_zsh_state() { : }`, then `source ~/.zshrc`.
4. **Bash / direct Python**: `SHELL=/bin/bash ./aetherflow -q --plan <plan.json>` or `python3 -m Backend.Prod.cli -q --plan <plan.json>` (from project root).

Reference: [TROUBLESHOOTING_CURSOR_SHELL.md](docs/05-operations/TROUBLESHOOTING_CURSOR_SHELL.md), [GUIDE_RAPIDE_AETHERFLOW.md](docs/01-getting-started/GUIDE_RAPIDE_AETHERFLOW.md).

## Markdown avec arborescences (structure vs code)

Si un output ou un document Markdown contient des **arborescences human-friendly** (arborescence de fichiers avec `├──`, `│`, `└──`, ou blocs explicites `file_tree` / `structure`), il faut les **spliter et réinterpréter** : ne pas appliquer l’arborescence comme du code dans les fichiers cibles. L’orchestrateur fait déjà ce split au moment de la sauvegarde des step outputs (`split_structure_and_code` dans `Backend/Prod/claude_helper.py`, écriture de `step_X_structure.md` et `step_X_code.txt`) ; `get_step_output` privilégie `step_X_code.txt` pour l’apply. Si tu reçois ou produis un MD avec de telles arborescences en dehors de ce flux, applique la même règle : extraire la partie structure dans un artefact séparé et n’utiliser que la partie « code » pour l’application aux fichiers.
