#!/usr/bin/env python3
"""
Script d'instructions pour Claude - Suite de Benchmarks AETHERFLOW

Claude doit :
1. Lire ce script
2. Exécuter chaque opération listée ci-dessous
3. Lancer le script de benchmarking pour évaluer les résultats
"""

# ============================================================================
# LISTE DES OPÉRATIONS À EXÉCUTER
# ============================================================================

# Suite Minimale Recommandée (Quick Test)
OPERATIONS = [
    {
        "id": "bench-001",
        "name": "API REST Simple",
        "plan": "Backend/Notebooks/benchmark_tasks/task_01_simple_api.json",
        "description": "Créer une API REST simple avec un endpoint GET /hello",
        "type": "simple",
        "expected_time": "30-60s",
        "expected_cost": "$0.001-0.002"
    },
    {
        "id": "bench-004",
        "name": "Système d'Authentification",
        "plan": "Backend/Notebooks/benchmark_tasks/task_04_authentication.json",
        "description": "Créer un système d'authentification avec hashage de mots de passe",
        "type": "multi_steps",
        "expected_time": "2-3min",
        "expected_cost": "$0.005-0.010"
    },
    {
        "id": "bench-007",
        "name": "Tâche Complexe avec Validation",
        "plan": "Backend/Notebooks/benchmark_tasks/task_09_phase2_validation_test.json",
        "description": "Tâche complexe avec plusieurs étapes interdépendantes",
        "type": "complex",
        "expected_time": "3-5min",
        "expected_cost": "$0.010-0.020"
    },
    {
        "id": "bench-010",
        "name": "Refactoring",
        "plan": "Backend/Notebooks/benchmark_tasks/task_06_refactoring.json",
        "description": "Refactoring de code existant",
        "type": "refactoring",
        "expected_time": "2-3min",
        "expected_cost": "$0.005-0.010"
    },
    {
        "id": "bench-016",
        "name": "Calculatrice avec Tests",
        "plan": "Backend/Notebooks/benchmark_tasks/task_02_calculator.json",
        "description": "Créer une calculatrice avec tests unitaires",
        "type": "tests",
        "expected_time": "2-3min",
        "expected_cost": "$0.005-0.010"
    }
]

# ============================================================================
# INSTRUCTIONS POUR CLAUDE
# ============================================================================

"""
CLAUDE, voici ce que tu dois faire :

1. POUR CHAQUE OPÉRATION dans la liste OPERATIONS ci-dessus :
   
   a) Exécute le plan JSON avec AETHERFLOW :
      python -m Backend.Prod.cli --plan {plan} --output output/benchmark_suite/{id}
   
   b) Vérifie que l'exécution a réussi
   
   c) Note les métriques (temps, coûts, tokens)

2. APRÈS avoir exécuté toutes les opérations :
   
   Lance le script de benchmarking pour générer le rapport d'évaluation :
      python scripts/run_benchmark_suite.py --suite minimal
   
   OU si tu veux une suite personnalisée :
      python scripts/run_benchmark_suite.py --custom {plan1} {plan2} {plan3} ...

3. ANALYSE le rapport généré dans :
      output/benchmark_suite/minimal/evaluation_report.md

4. PRÉSENTE les résultats à l'utilisateur avec :
   - Taux de réussite global
   - Temps total d'exécution
   - Coût total
   - Points forts/faibles identifiés
   - Recommandations d'amélioration
"""

# ============================================================================
# COMMANDES À EXÉCUTER (pour référence)
# ============================================================================

COMMANDS = [
    # Exécuter chaque benchmark
    "python -m Backend.Prod.cli --plan Backend/Notebooks/benchmark_tasks/task_01_simple_api.json --output output/benchmark_suite/bench-001",
    "python -m Backend.Prod.cli --plan Backend/Notebooks/benchmark_tasks/task_04_authentication.json --output output/benchmark_suite/bench-004",
    "python -m Backend.Prod.cli --plan Backend/Notebooks/benchmark_tasks/task_09_phase2_validation_test.json --output output/benchmark_suite/bench-007",
    "python -m Backend.Prod.cli --plan Backend/Notebooks/benchmark_tasks/task_06_refactoring.json --output output/benchmark_suite/bench-010",
    "python -m Backend.Prod.cli --plan Backend/Notebooks/benchmark_tasks/task_02_calculator.json --output output/benchmark_suite/bench-016",
    
    # Générer le rapport d'évaluation
    "python scripts/run_benchmark_suite.py --suite minimal"
]

# ============================================================================
# MÉTRIQUES ATTENDUES
# ============================================================================

EXPECTED_METRICS = {
    "total_benchmarks": 5,
    "min_success_rate": 0.8,  # 80% minimum
    "max_total_time_minutes": 15,
    "max_total_cost_usd": 0.05,
    "min_successful_steps_rate": 0.9  # 90% des étapes doivent réussir
}

# ============================================================================
# POINTS D'ATTENTION
# ============================================================================

ATTENTION_POINTS = [
    "Vérifier que chaque plan JSON existe avant de l'exécuter",
    "Surveiller les erreurs d'exécution et les noter",
    "Comparer les métriques réelles avec les métriques attendues",
    "Identifier les benchmarks qui échouent et comprendre pourquoi",
    "Analyser les patterns dans les échecs (complexité, type, etc.)"
]

if __name__ == "__main__":
    """
    Ce script est un fichier d'instructions pour Claude.
    Ne pas exécuter directement - Claude doit lire ce fichier et suivre les instructions.
    """
    print("=" * 70)
    print("SCRIPT D'INSTRUCTIONS POUR CLAUDE - SUITE DE BENCHMARKS")
    print("=" * 70)
    print(f"\nNombre d'opérations à exécuter : {len(OPERATIONS)}")
    print("\nOpérations :")
    for op in OPERATIONS:
        print(f"  - {op['id']}: {op['name']} ({op['type']})")
    print("\n" + "=" * 70)
    print("Claude doit lire ce script et exécuter les opérations listées.")
    print("=" * 70)
