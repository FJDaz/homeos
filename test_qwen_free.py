import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPEN_ROUTER_QWEN_KEY")

# Modèle Qwen GRATUIT sur OpenRouter
model = "qwen/qwen-2-7b-instruct:free" 

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "HTTP-Referer": "https://aetherflow.ai",
    "Content-Type": "application/json"
}

data = {
    "model": model,
    "messages": [
        {"role": "user", "content": "Hello! Réponds 'QWEN FREE READY'."}
    ]
}

print(f"📡 Test de connexion OpenRouter avec le modèle GRATUIT {model}...")

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
