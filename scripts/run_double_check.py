#!/usr/bin/env python3
"""Script to run DOUBLE-CHECK validation on Phase 1 Backend API."""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from Backend.Prod.workflows.prod import ProdWorkflow


async def main():
    """Run PROD workflow (includes DOUBLE-CHECK) on validation plan."""
    plan_path = project_root / "Backend" / "Notebooks" / "benchmark_tasks" / "phase1_backend_api_double_check.json"
    output_dir = project_root / "output" / "phase1_double_check"
    
    print(f"Running PROD workflow (FAST → BUILD → DOUBLE-CHECK) on plan: {plan_path}")
    print(f"Output directory: {output_dir}")
    
    workflow = ProdWorkflow()
    try:
        result = await workflow.execute(
            plan_path=plan_path,
            output_dir=output_dir,
            context=None
        )
        
        print("\n" + "="*60)
        print("DOUBLE-CHECK Validation Complete")
        print("="*60)
        print(f"Success: {result.get('success', False)}")
        print(f"Total Time: {result.get('total_time_ms', 0)/1000:.2f}s")
        print(f"Total Cost: ${result.get('total_cost_usd', 0):.4f}")
        
        if "validation" in result:
            validation = result["validation"]
            print(f"\nValidation Details:")
            print(f"  Success: {validation.get('success', False)}")
            if "validation_details" in validation:
                print(f"  Steps Validated: {len(validation['validation_details'])}")
        
        return 0 if result.get("success", False) else 1
        
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
