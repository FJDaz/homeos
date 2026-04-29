#!/usr/bin/env python3
"""
Script pour diagnostiquer et corriger l'installation de llama-index.
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd):
    """Exécute une commande shell et retourne le résultat."""
    print(f"Exécution: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(f"Sortie: {result.stdout}")
    if result.stderr:
        print(f"Erreur: {result.stderr}")
    return result.returncode == 0

def main():
    print("=== Diagnostic de l'installation llama-index ===")
    
    # 1. Vérifier si Python peut importer llama_index
    print("\n1. Test d'importation de llama_index...")
    try:
        import llama_index
        print(f"✓ llama_index version: {llama_index.__version__}")
    except ImportError as e:
        print(f"✗ ImportError: {e}")
    
    try:
        import llama_index.core
        print("✓ llama_index.core importé avec succès")
    except ImportError as e:
        print(f"✗ ImportError pour core: {e}")
    
    # 2. Vérifier les packages installés
    print("\n2. Packages installés dans l'environnement virtuel...")
    venv_path = Path("venv")
    if venv_path.exists():
        print(f"Environnement virtuel trouvé: {venv_path}")
        
        # Vérifier si pip est dans venv
        pip_path = venv_path / "bin" / "pip"
        if pip_path.exists():
            print(f"Pip trouvé: {pip_path}")
            
            # Lister les packages liés à llama
            success = run_command(f"{pip_path} list | grep -i llama")
            if not success:
                print("Aucun package llama trouvé")
        else:
            print("Pip non trouvé dans venv")
    else:
        print("Aucun environnement virtuel trouvé")
    
    # 3. Options de correction
    print("\n3. Options de correction:")
    print("   a. Installer llama-index depuis requirements.txt")
    print("   b. Installer directement avec pip")
    print("   c. Désactiver RAG dans pageindex_store.py")
    
    choice = input("\nChoisissez une option (a/b/c) ou 'q' pour quitter: ").lower()
    
    if choice == 'a':
        # Installer depuis requirements.txt
        if venv_path.exists() and (venv_path / "bin" / "pip").exists():
            pip_cmd = str(venv_path / "bin" / "pip")
            run_command(f"{pip_cmd} install -r requirements.txt")
        else:
            print("Utilisation de pip système...")
            run_command("pip install -r requirements.txt")
    
    elif choice == 'b':
        # Installer directement
        packages = "llama-index llama-index-core"
        if venv_path.exists() and (venv_path / "bin" / "pip").exists():
            pip_cmd = str(venv_path / "bin" / "pip")
            run_command(f"{pip_cmd} install {packages}")
        else:
            run_command(f"pip install {packages}")
    
    elif choice == 'c':
        # Désactiver RAG
        print("\nDésactivation de RAG dans pageindex_store.py...")
        rag_file = Path("Backend/Prod/rag/pageindex_store.py")
        if rag_file.exists():
            content = rag_file.read_text()
            # Remplacer le warning par un message plus doux
            new_content = content.replace(
                "logger.warning(f\"LlamaIndex not available: {e}. Install with: pip install llama-index llama-index-core\")",
                "logger.info(f\"LlamaIndex not available: {e}. RAG functionality will be disabled.\")"
            )
            rag_file.write_text(new_content)
            print("✓ RAG désactivé silencieusement")
        else:
            print("✗ Fichier pageindex_store.py non trouvé")
    
    elif choice == 'q':
        print("Au revoir!")
        return
    
    # 4. Vérification finale
    print("\n4. Vérification finale...")
    try:
        import llama_index
        print(f"✓ llama_index version: {llama_index.__version__}")
        print("✓ Installation réussie!")
    except ImportError as e:
        print(f"✗ ImportError persistant: {e}")
        print("Le RAG restera désactivé jusqu'à l'installation de llama-index.")

if __name__ == "__main__":
    main()