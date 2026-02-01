"""Script d'exemple pour Claude Code - Comment utiliser AETHERFLOW."""

# Exemple 1 : Exécution simple
from Backend.Prod.claude_helper import execute_plan_cli, get_step_output

# 1. Générer le plan (fait par Claude Code)
plan_path = "Backend/Notebooks/benchmark_tasks/mon_plan.json"

# 2. Exécuter automatiquement
result = execute_plan_cli(
    plan_path=plan_path,
    output_dir="output/mon_projet"
)

# 3. Vérifier et récupérer les résultats
if result["success"]:
    print("✅ Plan exécuté avec succès !")
    print(f"Coût total: ${result['metrics']['total_cost_usd']:.4f}")
    print(f"Taux de réussite: {result['metrics']['success_rate']:.1%}")
    
    # Récupérer le code de chaque étape
    for step_id in ["step_1", "step_2", "step_3"]:
        code = get_step_output(step_id, "output/mon_projet")
        if code:
            print(f"\n📄 Code de {step_id}:")
            print(code[:500])  # Afficher les 500 premiers caractères
else:
    print(f"❌ Erreur: {result.get('error')}")

# Exemple 2 : Workflow complet dans une fonction Claude Code
def implementer_phase2():
    """
    Fonction que Claude Code peut utiliser pour implémenter la phase 2.
    """
    # 1. Générer le plan
    plan = {
        "task_id": "phase2-001",
        "description": "Implémenter la phase 2",
        "steps": [
            # ... étapes définies par Claude Code
        ],
        "metadata": {
            "created_at": "2025-01-25T12:00:00Z",
            "claude_version": "claude-code"
        }
    }
    
    # Sauvegarder le plan
    import json
    plan_path = "Backend/Notebooks/benchmark_tasks/phase2_plan.json"
    with open(plan_path, "w") as f:
        json.dump(plan, f, indent=2)
    
    # 2. Exécuter
    result = execute_plan_cli(plan_path, "output/phase2")
    
    # 3. Récupérer et présenter les résultats
    if result["success"]:
        all_code = []
        for step_id in [f"step_{i}" for i in range(1, len(plan["steps"]) + 1)]:
            code = get_step_output(step_id, "output/phase2")
            if code:
                all_code.append(f"# {step_id}\n{code}")
        
        return "\n\n".join(all_code)
    else:
        return f"Erreur lors de l'exécution: {result.get('error')}"
