import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("QWEN_KEY")

# Configuration SiliconFlow (Très populaire pour Qwen)
model = "qwen/qwen-2.5-72b-instruct" 

url = "https://api.siliconflow.cn/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": model,
    "messages": [
        {"role": "user", "content": "Test SiliconFlow. Réponds 'QWEN SILICON READY'."}
    ],
    "max_tokens": 100
}

print(f"📡 Test de connexion SiliconFlow avec le modèle {model}...")

try:
    response = requests.post(url, headers=headers, data=json.dumps(data), timeout=15)
    if response.status_code == 200:
        result = response.json()
        content = result['choices'][0]['message']['content']
        print(f"✅ Succès SiliconFlow ! Réponse : {content}")
    else:
        print(f"❌ Échec (Code {response.status_code}) : {response.text}")
except Exception as e:
    print(f"❌ Erreur lors de l'appel : {str(e)}")
