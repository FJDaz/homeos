"""Test Local Orchestrator Switch logic."""
import asyncio
import sys
from pathlib import Path

# Ajout du path pour import Backend
sys.path.append(str(Path(__file__).parent.parent))

from Backend.Prod.core.local_orchestrator import LocalOrchestrator

async def test_orchestrator():
    orchestrator = LocalOrchestrator()
    
    print("--- Test 1: Syntax Task (3B) ---")
    res1 = await orchestrator.execute("Check the syntax of: print('hello')", task_type="syntax")
    print(f"Model used: {res1.get('model')}")
    print(f"Content: {res1.get('content')[:100]}...")
    
    print("\n--- Test 2: Logic Task (7B) - Should trigger RAM Cleanup ---")
    res2 = await orchestrator.execute("Explain the concept of Spinozist substance.", task_type="logic")
    print(f"Model used: {res2.get('model')}")
    print(f"Content: {res2.get('content')[:100]}...")
    
    await orchestrator.cleanup()
    print("\nTest completed.")

if __name__ == "__main__":
    asyncio.run(test_orchestrator())
