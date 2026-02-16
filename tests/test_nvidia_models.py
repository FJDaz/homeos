"""Test des modèles disponibles sur NVIDIA NIM."""
import asyncio
import httpx
from pathlib import Path
from dotenv import load_dotenv
import os

# Charger .env
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

NVIDIA_KEY = os.getenv("NVIDIA_API_KEY")

async def test_nvidia():
    print(f"🔑 NVIDIA_API_KEY: {NVIDIA_KEY[:20]}..." if NVIDIA_KEY else "❌ Clé manquante")
    print()

    if not NVIDIA_KEY:
        print("❌ Pas de NVIDIA_API_KEY dans .env")
        return

    # Liste des modèles KIMI potentiels sur NVIDIA NIM
    models_to_test = [
        "moonshotai/kimi-k2.5",
        "moonshot/kimi-k2.5",
        "kimi-k2.5",
        "meta/llama-3.1-8b-instruct",  # Test avec un modèle connu
    ]

    for model in models_to_test:
        print(f"🧪 Test modèle: {model}")

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    "https://integrate.api.nvidia.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {NVIDIA_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [
                            {"role": "user", "content": "Say OK"}
                        ],
                        "max_tokens": 10
                    }
                )

                print(f"   📊 Status: {response.status_code}")

                if response.status_code == 200:
                    result = response.json()
                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    print(f"   ✅ Fonctionne ! Réponse: {content}")
                    print()
                else:
                    error = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                    print(f"   ❌ Erreur: {error}")
                    print()

        except Exception as e:
            print(f"   ❌ Exception: {e}")
            print()

if __name__ == "__main__":
    asyncio.run(test_nvidia())
