"""Intelligence de Veille - HOMEOS V2.
Utilise un modèle BERT pour classifier sémantiquement les alertes du marché.
"""
import subprocess
import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from loguru import logger

class VeilleAgent:
    """
    Agent de Veille Stratégique.
    Gère la classification des flux via un sidecar Python 3.11 (BERT compatible).
    """
    
    def __init__(self, venv_path: str = ".venv_veille"):
        self.venv_path = Path(venv_path)
        # On remonte de Backend/Prod/homeos_v2/vigilance vers la racine du projet
        self.python_bin = Path("/Users/francois-jeandazin/AETHERFLOW") / venv_path / "bin" / "python3"
        
        # Script sidecar localisé dans le même dossier
        self.classifier_script = Path(__file__).parent / "veille_classifier_sidecar.py"
        self._ensure_sidecar_exists()

    def _ensure_sidecar_exists(self):
        """Crée le script sidecar si nécessaire."""
        script_content = """
import sys
import json
from sentence_transformers import SentenceTransformer
import numpy as np

# Modèle très léger pour Mac Intel
model_name = 'all-MiniLM-L6-v2'
model = None

def get_model():
    global model
    if model is None:
        model = SentenceTransformer(model_name)
    return model

def classify(text):
    m = get_model()
    # Classes de référence
    classes = ["PRICE_ALERT", "PERFORMANCE_LEAP", "OPPORTUNITY", "NOISE"]
    # Embedding simple et similarité
    embeddings = m.encode([text] + classes)
    
    text_emb = embeddings[0]
    class_embs = embeddings[1:]
    
    # Cosine similarity
    similarities = [np.dot(text_emb, c_emb) / (np.linalg.norm(text_emb) * np.linalg.norm(c_emb)) for c_emb in class_embs]
    best_idx = np.argmax(similarities)
    
    return {
        "label": classes[best_idx],
        "confidence": float(similarities[best_idx]),
        "model": model_name
    }

if __name__ == "__main__":
    line = sys.stdin.readline()
    if line:
        try:
            data = json.loads(line)
            result = classify(data.get("text", ""))
            print(json.dumps(result))
        except Exception as e:
            print(json.dumps({"error": str(e)}))
"""
        if not self.classifier_script.exists():
            logger.info(f"Creating BERT sidecar at {self.classifier_script}")
            with open(self.classifier_script, 'w') as f:
                f.write(script_content.strip())

    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyse un texte via le sidecar BERT."""
        try:
            if not self.classifier_script.exists():
                return {"label": "ERROR", "error": "Sidecar missing"}

            process = subprocess.Popen(
                [str(self.python_bin), str(self.classifier_script)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=json.dumps({"text": text}), timeout=120)
            
            if process.returncode != 0:
                logger.error(f"Sidecar error: {stderr}")
                return {"label": "ERROR", "confidence": 0, "error": stderr}
                
            return json.loads(stdout)
        except Exception as e:
            logger.error(f"VeilleAgent analysis failed: {e}")
            return {"label": "UNKNOWN", "confidence": 0, "error": str(e)}

    def generate_report(self, items: List[str]) -> Dict[str, Any]:
        """Simulation d'un rapport de veille consolidé."""
        return {
            "summary": f"Analyse de {len(items)} signaux terminée.",
            "alerts": [] 
        }