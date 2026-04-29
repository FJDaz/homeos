import requests
import json

# REMPLACEZ PAR VOTRE CLÉ RÉELLE
API_KEY = "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"
MODEL = "z-ai/glm5"
URL = "https://integrate.api.nvidia.com/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": MODEL,
    "messages": [{"role": "user", "content": "Hello, are you GLM-5?"}],
    "temperature": 0.5,
    "top_p": 1,
    "max_tokens": 1024
}

print(f"Test de la clé avec le modèle {MODEL}...")
response = requests.post(URL, headers=headers, json=payload)

if response.status_code == 200:
    print("SUCCÈS !")
    print("Réponse du modèle :")
    print(response.json()['choices'][0]['message']['content'])
else:
    print(f"ERREUR {response.status_code}")
    print(response.text)
