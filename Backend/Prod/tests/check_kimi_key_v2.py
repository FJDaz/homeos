import os
import requests
import json
from dotenv import load_dotenv

def test_kimi_api_v2():
    # Load .env from Backend/.env
    project_root = "/Users/francois-jeandazin/AETHERFLOW"
    env_path = os.path.join(project_root, "Backend/.env")
    load_dotenv(env_path)
    
    api_key = os.getenv("KIMI_KEY")
    if not api_key:
        print("❌ KIMI_KEY non trouvée dans le fichier .env")
        return

    # User's suggested URL and Model
    url = "https://api.moonshot.ai/v1/chat/completions"
    model = "kimi-k2-turbo-preview"
    
    print(f"Testing KIMI API with URL: {url}")
    print(f"Model: {model}")
    print(f"Key: {api_key[:10]}...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": "Hello, are you operational? Answer with 'OK' if yes."}
        ],
        "temperature": 0.6
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=15)
        if response.status_code == 200:
            print("✅ KIMI API répond correctement !")
            print("Réponse:", response.json()['choices'][0]['message']['content'])
        else:
            print(f"❌ Erreur API KIMI (Status: {response.status_code})")
            print("Détail:", response.text)
    except Exception as e:
        print(f"❌ Erreur lors de l'appel : {str(e)}")

if __name__ == "__main__":
    test_kimi_api_v2()
