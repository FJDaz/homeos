#!/usr/bin/env python3
import os
import sys
import json
import asyncio
from pathlib import Path

# --- Auto-resolve Virtualenv ---
project_root = Path(__file__).parent.parent
venv_python = project_root / "venv" / "bin" / "python3"
if os.name != "nt" and venv_python.exists() and sys.executable != str(venv_python):
    os.execv(str(venv_python), [str(venv_python)] + sys.argv)

sys.path.insert(0, str(project_root))
from Backend.Prod.models.deepseek_client import DeepSeekClient

import httpx

# --- Global Identity ---
try:
    IDENTITY = Path(project_root / "DEEPSEEK.md").read_text()
except: 
    IDENTITY = "Tu es l'Architecte AetherFlow."

async def stream_response(prompt: str):
    from Backend.Prod.config.settings import settings
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.deepseek_api_key}"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": IDENTITY},
            {"role": "user", "content": prompt}
        ],
        "stream": True
    }
    
    print("\n\033[92m", end="", flush=True)
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            async with client.stream("POST", url, json=payload, headers=headers) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        line = line[5:].strip()
                        if line == "[DONE]": break
                        try:
                            data = json.loads(line)
                            delta = data["choices"][0]["delta"].get("content", "")
                            print(delta, end="", flush=True)
                        except: continue
        except Exception as e:
            print(f"\033[91mErreur: {e}\033[0m")
    print("\033[0m\n")

async def main():
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        print(f"\033[94m[AF] ENVOI: {prompt}\033[0m")
        await stream_response(prompt)
    else:
        print("\033[95m--- AF CLI (Live Architect) ---\033[0m")
        while True:
            try:
                prompt = input("\033[94mUSER ❯ \033[0m")
                if prompt.lower() in ("exit", "quit", "q"): break
                await stream_response(prompt)
            except EOFError: break
            except KeyboardInterrupt: break
            except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
