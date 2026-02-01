# Guide rapide – Lancer AETHERFLOW

## Commandes disponibles

### Mode QUICK (PROTO) – Brouillon rapide

```bash
./aetherflow -q --plan <plan.json>
```

### Mode FULL (PROD) – Production avec validation

```bash
./aetherflow -f --plan <plan.json>
```

### Voir les coûts

```bash
./aetherflow --costs
```

### Voir les stats cache

```bash
./aetherflow --stats
```

---

## Exemples concrets

```bash
# Test simple
./aetherflow -q --plan Backend/Notebooks/benchmark_tasks/test_workflow_proto.json

# Correction existante
./aetherflow -f --plan Backend/Notebooks/benchmark_tasks/correction_patch_pattern_analyzer.json --output output/test
```

---

## Si problème (exit code 136, base64, dump_zsh_state) dans Cursor

Le terminal intégré Cursor peut interférer. Solutions :

1. **Lancer dans un terminal externe** (Terminal.app, iTerm) – recommandé.
2. **Contournement shell** : `SHELL=/bin/bash ./aetherflow -q --plan <plan.json>`
3. **Appel direct Python** (depuis la racine du projet) :  
   `python3 -m Backend.Prod.cli -q --plan <plan.json>`

Détails : [TROUBLESHOOTING_CURSOR_SHELL.md](TROUBLESHOOTING_CURSOR_SHELL.md).
