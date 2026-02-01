# Scripts AETHERFLOW

## benchmark.py

Script de benchmark qui exécute un plan et génère un rapport markdown pour Claude Code analyser.

### Utilisation

```bash
python scripts/benchmark.py \
  --plan Backend/Notebooks/benchmark_tasks/task_01_simple_api.json \
  --output output/benchmark_test1 \
  --report output/benchmark_test1/rapport.md
```

### Ce qu'il fait

1. Exécute le plan via AETHERFLOW
2. Collecte toutes les métriques (coûts, temps, tokens, qualité)
3. Génère un rapport markdown dans `benchmark_report.md`
4. Sauvegarde les données JSON dans `benchmark_data.json`

### Rapport généré

Le rapport markdown contient :
- Métriques globales (succès, temps, coûts)
- Détails par étape
- Liste des fichiers générés
- Section d'analyse pour Claude Code

Claude Code peut ensuite lire ce rapport et analyser les résultats.
