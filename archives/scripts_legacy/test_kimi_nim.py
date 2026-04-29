import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("NVIDIA_NIM_API_KEY")

if not api_key:
    print("❌ Erreur : NVIDIA_NIM_API_KEY non trouvée.")
    exit(1)

# Modèle exact trouvé dans votre config
model = "moonshotai/kimi-k2.5" 

url = "https://integrate.api.nvidia.com/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": model,
    "messages": [
        {"role": "user", "content": "Test de connexion AetherFlow. Réponds 'KIMI NIM READY'."}
    ],
    "max_tokens": 100
}

print(f"📡 Test de connexion NVIDIA NIM avec le modèle {model}...")

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
