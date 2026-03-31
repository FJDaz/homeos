import os
import subprocess

def setup_local_qwen():
    model_name = "qwen3-local"
    # Chemin vers votre fichier GGUF (à adapter si différent)
    gguf_path = "qwen3-8b-q4_k_m.gguf" 
    
    if not os.path.exists(gguf_path):
        print(f"❌ Erreur : Fichier {gguf_path} non trouvé.")
        print("💡 Téléchargez-le d'abord (ex: sur HuggingFace) et placez-le à la racine d'AetherFlow.")
        return

    modelfile_content = f"""
FROM ./{gguf_path}
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER stop "<|endoftext|>"
PARAMETER stop "<|im_start|>"
PARAMETER stop "<|im_end|>"
SYSTEM \"\"\"
Tu es Qwen3, le cerveau local d'AetherFlow HomeOS. 
Tu es un expert en architecture logicielle, audit UX et code Tailwind.
Réponds de manière concise et technique.
\"\"\"
"""
    
    with open("Modelfile_Qwen3", "w") as f:
        f.write(modelfile_content)
    
    print(f"📦 Création du modèle Ollama '{model_name}'...")
    try:
        subprocess.run(["ollama", "create", model_name, "-f", "Modelfile_Qwen3"], check=True)
        print(f"✅ Modèle {model_name} créé avec succès !")
        print(f"🚀 Testez-le avec : ollama run {model_name}")
    except Exception as e:
        print(f"❌ Erreur lors de la création : {e}")

if __name__ == "__main__":
    setup_local_qwen()
