import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPEN_ROUTER_QWEN_KEY")

if not api_key:
    print("❌ Erreur : OPEN_ROUTER_QWEN_KEY non trouvée.")
    exit(1)

# Modèle exact du snippet
model = "qwen/qwen3-coder:free" 

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "HTTP-Referer": "https://aetherflow.ai",
    "X-Title": "AetherFlow Diagnostic",
    "Content-Type": "application/json"
}

data = {
    "model": model,
    "messages": [
        {"role": "user", "content": "Test Qwen 3 Coder. Réponds 'QWEN3 FREE READY'."}
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
    print(f"❌ Erreur : {str(e)}")
