import os
import requests
import json
from dotenv import load_dotenv

def test_kimi_api():
    # Load .env from Backend/.env
    project_root = "/Users/francois-jeandazin/AETHERFLOW"
    env_path = os.path.join(project_root, "Backend/.env")
    load_dotenv(env_path)
    
    api_key = os.getenv("KIMI_KEY")
    if not api_key:
        print("❌ KIMI_KEY non trouvée dans le fichier .env")
        return

    print(f"Testing KIMI API with key: {api_key[:10]}...")
    
    url = "https://api.moonshot.cn/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "moonshot-v1-8k",
        "messages": [
            {"role": "user", "content": "Bonjour, es-tu opérationnel ? Réponds juste 'OK' si oui."}
        ],
        "temperature": 0.3
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
        if response.status_code == 200:
            print("✅ KIMI API répond correctement !")
            print("Réponse:", response.json()['choices'][0]['message']['content'])
        else:
            print(f"❌ Erreur API KIMI (Status: {response.status_code})")
            print("Détail:", response.text)
    except Exception as e:
        print(f"❌ Erreur lors de l'appel : {str(e)}")

if __name__ == "__main__":
    test_kimi_api()
