import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    print("❌ Erreur : OPENROUTER_API_KEY non trouvée dans le .env")
    exit(1)

# Modèle Kimi sur OpenRouter (communément moonshotai/kimi-k2.5 ou moonshotai/kimi-k2-thinking)
model = "moonshotai/kimi-k2.5" 

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "HTTP-Referer": "https://aetherflow.ai", # Optionnel
    "X-Title": "AetherFlow Diagnostic",
    "Content-Type": "application/json"
}

data = {
    "model": model,
    "messages": [
        {"role": "user", "content": "Test de connexion AetherFlow. Réponds brièvement 'KIMI READY'."}
    ]
}

print(f"📡 Test de connexion OpenRouter avec le modèle {model}...")

try:
    response = requests.post(url, headers=headers, data=json.dumps(data), timeout=15)
    if response.status_code == 200:
        result = response.json()
        content = result['choices'][0]['message']['content']
        print(f"✅ Succès ! Réponse : {content}")
    else:
        print(f"❌ Échec (Code {response.status_code}) : {response.text}")
except Exception as e:
    print(f"❌ Erreur lors de l'appel : {str(e)}")
