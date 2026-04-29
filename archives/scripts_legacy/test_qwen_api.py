import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Récupération de la clé QWEN_KEY (utilisée pour Bothub)
api_key = os.getenv("QWEN_KEY")

if not api_key:
    print("❌ Erreur : QWEN_KEY non trouvée dans le .env")
    exit(1)

# Configuration Bothub API
# Modèle suggéré : qwen-2.5-72b-instruct (stable) ou qwen-2.5-max (flagship)
model = "qwen-2.5-72b-instruct" 

url = "https://api.bothub.ai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": model,
    "messages": [
        {"role": "user", "content": "Test AetherFlow. Réponds 'QWEN READY'."}
    ],
    "max_tokens": 100
}

print(f"📡 Test de connexion Bothub avec le modèle {model}...")

try:
    response = requests.post(url, headers=headers, data=json.dumps(data), timeout=15)
    if response.status_code == 200:
        result = response.json()
        content = result['choices'][0]['message']['content']
        print(f"✅ Succès ! Réponse : {content}")
    else:
        print(f"❌ Échec (Code {response.status_code}) : {response.text}")
except Exception as e:
    # Si Bothub échoue, on tente une URL standard Alibaba DashScope au cas où
    print(f"⚠️ Échec sur Bothub ({str(e)}). Tentative sur DashScope (Alibaba Cloud direct)...")
    dash_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    try:
        response = requests.post(dash_url, headers=headers, data=json.dumps(data), timeout=15)
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"✅ Succès sur DashScope ! Réponse : {content}")
        else:
            print(f"❌ Échec global (Code {response.status_code}) : {response.text}")
    except Exception as e2:
        print(f"❌ Erreur critique : {str(e2)}")
