
import asyncio
from pathlib import Path
import sys
import os

# Ajouter le répertoire racine au path pour les imports
sys.path.append(os.getcwd())

from Backend.Prod.workflows.prod import ProdWorkflow

async def main():
    plan_path = Path("maiathon_bridge_plan.json")
    output_dir = Path("output/maiathon_integration")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    workflow = ProdWorkflow()
    print(f"Lancement du workflow PROD pour le plan: {plan_path}")
    
    try:
        result = await workflow.execute(
            plan_path=plan_path,
            output_dir=output_dir,
            context="Intégration Maïathon Bridge"
        )
        print("\nWorkflow terminé avec succès!")
        print(f"Temps total: {result['total_time_ms']/1000:.2f}s")
        print(f"Coût total: ${result['total_cost_usd']:.4f}")
    except Exception as e:
        print(f"\nErreur lors de l'exécution du workflow: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
