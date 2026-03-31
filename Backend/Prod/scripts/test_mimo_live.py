import asyncio
import os
import sys
from pathlib import Path

# Fix path
project_root = Path(__file__).resolve().parents[3]
sys.path.append(str(project_root))

from Backend.Prod.models.mimo_client import MimoClient
from Backend.Prod.core.cost_tracker import get_cost_tracker, record_cost

async def main():
    print("🚀 Test Live MiMo Client with Force Save...")
    client = MimoClient()
    
    result = await client.generate("Dis-moi 3 mots inspirants.")
    
    if result.success:
        print(f"✅ Success! Response: {result.code}")
        record_cost(
            provider="mimo",
            workflow_type="TEST",
            step_id="test_mimo_force_save",
            task_id="verification",
            cost_usd=result.cost_usd,
            tokens_total=result.tokens_used,
            tokens_input=result.input_tokens,
            tokens_output=result.output_tokens,
            execution_time_ms=result.execution_time_ms
        )
        # Force save
        tracker = get_cost_tracker()
        tracker.save()
        print(f"💾 Cost recorded and forced save to {tracker.storage_path}")
    else:
        print(f"❌ Error: {result.error}")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
