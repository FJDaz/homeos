# Guide d'Utilisation - Benchmark Méta Phase 2.1

## Objectif

Tester les performances d'**AETHERFLOW 0.1** (Claude Code + DeepSeek) pour construire **AETHERFLOW 0.2** (implémentation de CodestralClient).

## Fichiers Créés

1. **Plan JSON** : `Backend/Notebooks/benchmark_tasks/task_10_phase2_codestral_implementation.json`
   - 8 étapes pour implémenter CodestralClient
   - Structure similaire à DeepSeekClient
   - Validation criteria pour chaque étape

2. **Script de Benchmark** : `scripts/benchmark_phase2_codestral.py`
   - Exécute le plan via AETHERFLOW
   - Collecte métriques (temps, coûts, tokens)
   - Génère rapport markdown avec analyse méta

## Utilisation

### 1. Exécuter le Benchmark

```bash
# Depuis la racine du projet
python scripts/benchmark_phase2_codestral.py

# Ou avec options personnalisées
python scripts/benchmark_phase2_codestral.py \
  --plan Backend/Notebooks/benchmark_tasks/task_10_phase2_codestral_implementation.json \
  --output output/my_benchmark \
  --report output/my_benchmark/report.md
```

### 2. Ce qui va se passer

1. **AETHERFLOW 0.1** va exécuter le plan JSON
2. **DeepSeek** va générer le code pour chaque étape
3. Le code généré sera sauvegardé dans `output/benchmark_meta_codestral/step_outputs/`
4. Les métriques seront collectées (temps, coûts, tokens)
5. Un rapport markdown sera généré avec analyse complète

### 3. Résultats Attendus

Le benchmark va créer :
- `output/benchmark_meta_codestral/benchmark_report.md` - Rapport détaillé
- `output/benchmark_meta_codestral/benchmark_data.json` - Données brutes JSON
- `output/benchmark_meta_codestral/step_outputs/step_*.txt` - Code généré par étape

### 4. Métriques Mesurées

- **Performance** : Temps d'exécution total, par étape, overhead
- **Coûts** : Coût total DeepSeek, coût par étape
- **Tokens** : Tokens utilisés (input/output)
- **Qualité** : Taux de réussite, complétude implémentation
- **Self-Hosting** : AETHERFLOW peut-il se construire lui-même ?

## Analyse des Résultats

Le rapport markdown contient une section "Analyse pour Claude Code" avec des questions :
1. AETHERFLOW a-t-il réussi à se construire lui-même ?
2. Qualité du code généré ?
3. Performance acceptable ?
4. Coûts raisonnables ?
5. Efficacité pour construire ses propres composants ?
6. Améliorations suggérées ?

## Notes Importantes

- **Prérequis** : `DEEPSEEK_API_KEY` doit être configuré dans `Backend/.env`
- **Temps estimé** : 5-15 minutes selon la complexité
- **Coût estimé** : ~$0.01-0.05 selon les tokens utilisés
- Le code généré devra être **intégré manuellement** dans le projet après validation

## Prochaines Étapes

Après le benchmark :
1. Analyser le rapport markdown
2. Vérifier la qualité du code généré dans `step_outputs/`
3. Intégrer le code validé dans `Backend/Prod/models/codestral_client.py`
4. Tester l'implémentation
5. Mettre à jour `AgentRouter` si nécessaire
