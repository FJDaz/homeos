"""Test rapide de l'API Moonshot KIMI."""
import asyncio
import httpx
from pathlib import Path
from dotenv import load_dotenv
import os

# Charger .env
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Test avec KIMI_KEY directe (Moonshot platform)
KIMI_KEY = os.getenv("KIMI_KEY")
# Essayer les deux URLs possibles
URLS_TO_TEST = [
    ("Moonshot CN", "https://api.moonshot.cn/v1/chat/completions", "moonshot-v1-8k"),
    ("Moonshot AI", "https://api.moonshot.ai/v1/chat/completions", "moonshot-v1-8k"),
]

async def test_kimi():
    print(f"🔑 KIMI_KEY: {KIMI_KEY[:20]}..." if KIMI_KEY else "❌ KIMI_KEY manquante")
    print()

    if not KIMI_KEY:
        print("❌ Pas de KIMI_KEY dans .env")
        return

    # Tester les deux URLs
    for name, url, model in URLS_TO_TEST:
        print(f"\n🧪 Test {name}")
        print(f"🌐 URL: {url}")
        print(f"🤖 Modèle: {model}")

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {KIMI_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [
                            {"role": "user", "content": "Hello, respond with just 'OK'"}
                        ],
                        "temperature": 0.1,
                        "max_tokens": 10
                    }
                )

                print(f"📊 Status: {response.status_code}")

                if response.status_code == 200:
                    result = response.json()
                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    print(f"✅ API fonctionne !")
                    print(f"💬 Réponse: {content}")
                    return  # Succès, on arrête
                else:
                    print(f"❌ Erreur {response.status_code}")
                    print(f"📄 Response: {response.text[:200]}")

        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_kimi())
