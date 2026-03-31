import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("QWEN_KEY")

if not api_key:
    print("❌ Erreur : QWEN_KEY non trouvée dans le .env")
    exit(1)

# Configuration Bothub API correcte (v2/openai/v1)
# Note : Certains providers changent les noms des modèles (ex: "qwen-2.5-72b" ou "qwen2.5-72b-instruct")
model = "qwen-2.5-72b-instruct" 

url = "https://bothub.chat/api/v2/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": model,
    "messages": [
        {"role": "user", "content": "Test de connexion AetherFlow. Réponds brièvement 'QWEN BOTHUB READY'."}
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
        # Tentative avec un nom de modèle plus générique si 404
        if response.status_code == 404 or "model_not_found" in response.text:
            print("⚠️ Modèle non trouvé. Tentative avec 'gpt-4o' pour vérifier la clé...")
            data["model"] = "gpt-4o"
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=15)
            if response.status_code == 200:
                print("✅ La clé fonctionne ! Mais le modèle Qwen n'est pas reconnu sous ce nom.")
            else:
                print(f"❌ Échec global (Code {response.status_code}) : {response.text}")
except Exception as e:
    print(f"❌ Erreur lors de l'appel : {str(e)}")
