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