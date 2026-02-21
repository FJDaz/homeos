# Guide de Test Rapide - AETHERFLOW

## Étape 1 : Préparer l'environnement

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Configurer les clés API dans Backend/.env
DEEPSEEK_API_KEY=votre_clé
ANTHROPIC_API_KEY=votre_clé  # Pour validation automatique
```

## Étape 2 : Test Simple (Validation du workflow)

```bash
# Tester avec une tâche simple
python scripts/benchmark.py \
  --plan Backend/Notebooks/benchmark_tasks/task_01_simple_api.json \
  --output output/test_simple
```

**Résultat attendu** :
- Code généré dans `output/test_simple/step_outputs/`
- Rapport dans `output/test_simple/benchmark_report.md`
- Métriques dans `output/test_simple/benchmark_data.json`

## Étape 3 : Demander à Claude Code de créer le plan Phase 2

**Demande à faire à Claude Code** :
"Peux-tu créer un plan complet pour implémenter la Phase 2 d'AETHERFLOW : système multi-agents avec router intelligent. Sauvegarde-le dans `Backend/Notebooks/benchmark_tasks/phase2_complete.json`"

## Étape 4 : Segmenter la Phase 2

**Demande à faire à Claude Code** :
"En utilisant le plan phase2_complete.json, crée un plan segmenté pour la Partie 1 : Router de base. Sauvegarde-le dans `Backend/Notebooks/benchmark_tasks/phase2_part1_router.json`"

Voir `docs/guides/SEGMENTATION_PHASE2.md` pour les détails de segmentation.

## Étape 5 : Tester la Partie 1 avec Benchmark

```bash
python scripts/benchmark.py \
  --plan Backend/Notebooks/benchmark_tasks/phase2_part1_router.json \
  --output output/phase2_part1
```

## Étape 6 : Claude Code analyse les résultats

Claude Code lit `output/phase2_part1/benchmark_report.md` et :
- Vérifie la qualité du code généré
- Analyse les métriques (coûts, temps)
- Décide si on peut passer à la Partie 2 ou si corrections nécessaires

## Workflow Complet

```
Vous → "Implémente Phase 2 Partie 1"
  ↓
Claude Code → Génère plan phase2_part1_router.json
  ↓
Vous → Lance benchmark.py
  ↓
AETHERFLOW → Exécute plan (DeepSeek génère code)
  ↓
Benchmark → Génère rapport markdown
  ↓
Claude Code → Analyse rapport et décide suite
```

## Surveillance pendant l'exécution

Le script affiche en temps réel :
- Progression des étapes
- Métriques (coûts, temps, tokens)
- Résultats de validation Claude
- Corrections automatiques si nécessaire

## Fichiers Générés

Après chaque benchmark :
- `output/[nom_test]/step_outputs/` : Code généré par étape
- `output/[nom_test]/benchmark_report.md` : Rapport pour Claude Code
- `output/[nom_test]/benchmark_data.json` : Données brutes JSON
- `output/[nom_test]/metrics_*.json` : Métriques détaillées
