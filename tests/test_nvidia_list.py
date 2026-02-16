"""Liste les modèles disponibles avec la clé NVIDIA."""
import asyncio
import httpx
from pathlib import Path
from dotenv import load_dotenv
import os

# Charger .env
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

NVIDIA_KEY = os.getenv("NVIDIA_API_KEY")

async def list_models():
    print(f"🔑 NVIDIA_API_KEY: {NVIDIA_KEY[:20]}..." if NVIDIA_KEY else "❌ Clé manquante")
    print()

    if not NVIDIA_KEY:
        print("❌ Pas de NVIDIA_API_KEY dans .env")
        return

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # Essayer l'endpoint de liste des modèles
            response = await client.get(
                "https://integrate.api.nvidia.com/v1/models",
                headers={
                    "Authorization": f"Bearer {NVIDIA_KEY}",
                }
            )

            print(f"📊 Status: {response.status_code}")
            print(f"📄 Response:\n{response.text[:2000]}")

    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(list_models())
