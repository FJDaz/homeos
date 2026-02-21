import requests
import time
import os
import sys

# --- CONFIGURATION ---
# Seuil d'inactivité en secondes (ex: 30 minutes = 1800)
IDLE_THRESHOLD = int(os.getenv("IDLE_THRESHOLD", 1800))
# URL à surveiller (Ollama par défaut)
OLLAMA_URL = "http://localhost:11434/api/tags"
# API RunPod (nécessaire pour l'auto-stop)
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
POD_ID = os.getenv("RUNPOD_POD_ID")

def get_last_activity():
    """
    On peut utiliser le temps de modification d'un fichier log 
    ou vérifier si des requêtes passent par un proxy.
    Ici, on va simplement checker si le script est "pingé".
    """
    try:
        # On pourrait checker les logs d'Ollama ici si on voulait être précis
        return time.time()
    except:
        return time.time()

def stop_pod():
    """Appelle l'API RunPod pour stopper le pod actuel."""
    if not RUNPOD_API_KEY or not POD_ID:
        print("Erreur : RUNPOD_API_KEY ou RUNPOD_POD_ID manquant.")
        return False
        
    print(f"Inactivité détectée. Arrêt du pod {POD_ID}...")
    
    # GraphQL mutation pour stopper le pod
    url = f"https://api.runpod.io/graphtext/v1/{RUNPOD_API_KEY}"
    query = f"""
    mutation {{
        stopPod(input: {{
            podId: "{POD_ID}"
        }}) {{
            id
            desiredStatus
        }}
    }}
    """
    
    try:
        response = requests.post(url, json={'query': query})
        if response.status_code == 200:
            print("Commande d'arrêt envoyée avec succès.")
            return True
        else:
            print(f"Erreur API : {response.text}")
            return False
    except Exception as e:
        print(f"Erreur lors de l'appel API : {e}")
        return False

def main():
    print(f"Watchdog démarré. Seuil : {IDLE_THRESHOLD}s")
    last_activity = time.time()
    
    while True:
        # Dans une vraie implémentation, on surveillerait les logs d'accès
        # ou on forcerait l'app master à 'pinger' ce watchdog.
        
        # Pour ce prototype, on simule : si aucun fichier 'pulse' n'est touché
        # dans /tmp/pulse, on considère que c'est idle.
        pulse_file = "/tmp/pod_pulse"
        if os.path.exists(pulse_file):
            last_activity = os.path.getmtime(pulse_file)
            
        idle_duration = time.time() - last_activity
        
        if idle_duration > IDLE_THRESHOLD:
            if stop_pod():
                sys.exit(0)
        
        print(f"Idle depuis : {int(idle_duration)}s...", end="\r")
        time.sleep(30)

if __name__ == "__main__":
    main()
