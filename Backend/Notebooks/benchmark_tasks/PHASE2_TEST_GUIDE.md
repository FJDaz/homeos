# Guide de Test Phase 2 - Validation Claude

## Objectif

Tester le système de validation conditionnelle par Claude sur une tâche complexe en situation réelle de construction.

## Prérequis

1. Clés API configurées dans `Backend/.env` :
   - `DEEPSEEK_API_KEY` (obligatoire)
   - `ANTHROPIC_API_KEY` (obligatoire pour validation)

2. Installation des dépendances :
```bash
pip install -r requirements.txt
```

## Tâche de Test

**Fichier** : `task_09_phase2_validation_test.json`

**Description** : Tâche complexe avec 4 étapes interdépendantes :
1. Génération d'une classe DataProcessor complexe (complexity: 0.8)
2. Création de tests unitaires (complexity: 0.7)
3. Création d'API FastAPI (complexity: 0.75)
4. Analyse de qualité (complexity: 0.6, type: analysis)

## Exécution

### Mode 1 : Test avec validation activée (recommandé)

```bash
python -m Backend.Prod.cli \
  --plan Backend/Notebooks/benchmark_tasks/task_09_phase2_validation_test.json \
  --output output/phase2_test \
  --verbose
```

### Mode 2 : Test sans validation (pour comparaison)

```bash
# Désactiver la validation dans .env
ENABLE_CLAUDE_VALIDATION=false

python -m Backend.Prod.cli \
  --plan Backend/Notebooks/benchmark_tasks/task_09_phase2_validation_test.json \
  --output output/phase2_test_no_validation
```

## Ce qui sera testé

1. **Détection automatique** : Le système détecte automatiquement quelles étapes nécessitent la validation Claude
   - `step_1` : complexity 0.8 > 0.7 → ✅ Validation
   - `step_2` : complexity 0.7 = 0.7 → ✅ Validation
   - `step_3` : complexity 0.75 > 0.7 → ✅ Validation
   - `step_4` : type "analysis" → ✅ Validation

2. **Validation par Claude** : Pour chaque étape validée, Claude :
   - Évalue la qualité du code généré
   - Vérifie les critères de validation
   - Donne un score (0.0-1.0)
   - Fournit des feedbacks détaillés

3. **Correction automatique** : Si validation échoue (score < 0.7) :
   - Le système demande une correction à DeepSeek
   - DeepSeek génère une version corrigée
   - Le résultat corrigé remplace l'original

## Métriques à observer

Dans le rapport généré (`output/phase2_test/metrics_*.json`) :

- **Coûts** :
  - Coût DeepSeek (génération)
  - Coût Claude (validation)
  - Coût total
  - Comparaison avec/sans validation

- **Qualité** :
  - Score de validation par étape
  - Nombre de corrections demandées
  - Taux de réussite après validation

- **Performance** :
  - Temps d'exécution total
  - Temps de validation
  - Temps de correction

## Résultats attendus

1. **Validation déclenchée** pour les étapes complexes
2. **Feedback détaillé** de Claude sur chaque étape
3. **Corrections automatiques** si nécessaire
4. **Métriques complètes** dans les rapports

## Analyse des résultats

Après exécution, comparer :

1. **Qualité du code** : Les fichiers générés dans `output/phase2_test/step_outputs/`
2. **Métriques** : `output/phase2_test/metrics_*.json` et `metrics_*.csv`
3. **Logs** : `logs/aetherflow.log` pour les détails de validation

## Questions à se poser

- La validation améliore-t-elle la qualité du code généré ?
- Le coût supplémentaire de Claude est-il justifié ?
- Les corrections automatiques sont-elles efficaces ?
- Le système détecte-t-il correctement les étapes à valider ?
