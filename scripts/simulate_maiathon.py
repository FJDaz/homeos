
import asyncio
import httpx
import json
import sys

async def simulate_maiathon_call(message, context=None):
    url = "http://localhost:8000/v1/cto/chat"
    payload = {
        "message": message,
        "context": context or {"project": "Maïathon", "persona": "Spinoza"}
    }
    
    print(f"--- Simulation Maïathon Bridge ---")
    print(f"Message envoyé: {message}")
    print(f"Appel de l'API CTO Aetherflow à {url}...")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                print("\n[RÉPONSE D'AETHERFLOW]")
                print(f"Statut: Succès")
                print(f"Modèle utilisé: {result.get('model')}")
                print(f"Contenu:\n{result.get('content')}")
                print(f"\nMétriques: {result.get('metadata')}")
            else:
                print(f"\nErreur API ({response.status_code}): {response.text}")
        except Exception as e:
            print(f"\nErreur de connexion: {e}")
            print("Note: Assurez-vous que l'API Aetherflow est lancée (npm run dev ou python -m Backend.Prod.api)")

if __name__ == "__main__":
    message = "Explique-moi l'essence des affects selon mon éthique, en tant que Maïeute."
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
    
    asyncio.run(simulate_maiathon_call(message))

{
  "operations": [
    {
      "type": "add_function",
      "target": "scripts/simulate_maiathon.py",
      "position": "end",
      "code": """
async def test_simulate_maiathon_call():
    message = "Test message"
    await simulate_maiathon_call(message)

if __name__ == "__main__":
    asyncio.run(test_simulate_maiathon_call())
"""
    }
  ]
}