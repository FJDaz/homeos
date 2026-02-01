# Benchmark Tasks

Ce répertoire contient des tâches de test pour benchmarker AetherFlow.

## Utilisation

Exécuter une tâche individuelle :
```bash
python -m Backend.Prod.cli --plan Backend/Notebooks/benchmark_tasks/task_01_simple_api.json
```

Exécuter toutes les tâches (script à créer) :
```bash
python scripts/run_benchmark.py
```

## Tâches disponibles

- `task_01_simple_api.json` - Créer une API REST simple
- `task_02_calculator.json` - Créer une calculatrice avec tests
- `task_03_data_processing.json` - Traitement de données CSV
- `task_04_authentication.json` - Système d'authentification
- `task_05_database_crud.json` - CRUD avec base de données
- `task_06_refactoring.json` - Refactoring de code existant
- `task_07_analysis.json` - Analyse de codebase
- `task_08_microservice.json` - Architecture microservice simple
- `task_09_phase2_validation_test.json` - **Test Phase 2 : Validation Claude sur tâche complexe**
