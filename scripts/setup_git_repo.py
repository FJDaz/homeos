#!/usr/bin/env python3
"""Script to initialize git repository and prepare for GitHub."""
import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a shell command and return success status."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            print(f"✓ {cmd}")
            if result.stdout.strip():
                print(f"  {result.stdout.strip()}")
            return True
        else:
            print(f"✗ {cmd}")
            if result.stderr.strip():
                print(f"  Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"✗ {cmd}")
        print(f"  Exception: {e}")
        return False

def main():
    """Initialize git repository."""
    project_root = Path(__file__).parent.parent
    
    print("=" * 60)
    print("Initialisation du dépôt Git pour AETHERFLOW")
    print("=" * 60)
    print()
    
    # Check if git is available
    if not run_command("which git", cwd=project_root):
        print("\n❌ Git n'est pas installé. Veuillez installer Git d'abord.")
        return 1
    
    # Initialize git repository
    print("\n1. Initialisation du dépôt Git...")
    if (project_root / ".git").exists():
        print("  ℹ️  Le dépôt Git existe déjà.")
    else:
        if not run_command("git init", cwd=project_root):
            print("\n❌ Échec de l'initialisation du dépôt Git.")
            return 1
        print("  ✓ Dépôt Git initialisé")
    
    # Configure git user (if not already configured)
    print("\n2. Configuration Git...")
    result = subprocess.run(
        "git config user.name",
        shell=True,
        cwd=project_root,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print("  ⚠️  Veuillez configurer votre nom Git:")
        print("     git config user.name \"Votre Nom\"")
    
    result = subprocess.run(
        "git config user.email",
        shell=True,
        cwd=project_root,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print("  ⚠️  Veuillez configurer votre email Git:")
        print("     git config user.email \"votre.email@example.com\"")
    
    # Stage important files
    print("\n3. Ajout des fichiers au dépôt...")
    files_to_add = [
        ".gitignore",
        "README.md",
        "requirements.txt",
        "Backend/",
        "docs/",
        "scripts/",
        ".cursor/rules/",
    ]
    
    for file_path in files_to_add:
        full_path = project_root / file_path
        if full_path.exists():
            run_command(f"git add {file_path}", cwd=project_root)
    
    # Check status
    print("\n4. État du dépôt:")
    run_command("git status --short", cwd=project_root)
    
    print("\n" + "=" * 60)
    print("Prochaines étapes:")
    print("=" * 60)
    print()
    print("1. Créez un dépôt sur GitHub:")
    print("   - Allez sur https://github.com/new")
    print("   - Nom du dépôt: AETHERFLOW (ou Homeos)")
    print("   - Ne cochez PAS 'Initialize with README'")
    print()
    print("2. Connectez votre dépôt local à GitHub:")
    print("   git remote add origin https://github.com/VOTRE_USERNAME/AETHERFLOW.git")
    print()
    print("3. Faites votre premier commit:")
    print("   git commit -m \"Initial commit: AETHERFLOW orchestrator\"")
    print()
    print("4. Poussez vers GitHub:")
    print("   git push -u origin main")
    print()
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
