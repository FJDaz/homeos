import asyncio
from Backend.Prod.models.agent_router import AgentRouter
from Backend.Prod.models.plan_reader import Step
from pathlib import Path
import json

async def main():
    router = AgentRouter()
    
    # Load proto.py content
    proto_path = Path("/Users/francois-jeandazin/AETHERFLOW/Backend/Prod/workflows/proto.py")
    if proto_path.exists():
        proto_content = proto_path.read_text()
    else:
        proto_content = "def dummy(): pass"
        
    step_data = {
        "id": "step_01",
        "type": "refactoring",
        "description": "Refactor proto.py",
        "estimated_tokens": 10000,
        "complexity": 5.0,
        "context": {
            "files": ["Backend/Prod/workflows/proto.py"]
        }
    }
    step = Step(step_data)
    
    context = f"Existing code files:\n```python\n{proto_content}\n```"
    
    prompt = router._build_prompt(step, context, surgical_mode=True)
    print("=== PROMPT START ===")
    print(prompt[:1000])
    print("... [TRUNCATED] ...")
    print(prompt[-1500:])
    print("=== PROMPT END ===")
    
    # Let's see what happens when we try to send this to deepseek
    from Backend.Prod.models.deepseek_client import DeepSeekClient
    client = DeepSeekClient()
    print("Testing DeepSeek generation...")
    res = await client.generate(prompt=prompt, context=context, output_constraint="json_surgical")
    print(f"Success: {res.success}, Error: {res.error}, Output: {res.code[:100] if res.code else 'None'}...")

    import httpx
    # Directly test the raw payloads for gemini and codestral to see if they reject it immediately
    
if __name__ == "__main__":
    asyncio.run(main())
