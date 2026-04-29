#!/usr/bin/env python3
import os
from pathlib import Path

def generate_repo_map(root_dir, output_file):
    root = Path(root_dir)
    # Plus sélectif sur les dossiers ignorés
    ignored_dirs = {
        '.git', '__pycache__', 'venv', '.venv', 'node_modules', 
        'rag_index', '.gemini', 'artifacts', 'output', 'logs', 
        'data', 'tmp', 'build', 'dist', '.pytest_cache'
    }
    ignored_extensions = {
        '.pyc', '.pyo', '.exe', '.bin', '.jpg', '.png', '.gif', 
        '.zip', '.tar', '.gz', '.pdf', '.woff', '.woff2', '.ttf', '.eot'
    }

    repo_map = []
    repo_map.append("# 🗺️ AETHERFLOW REPO MAP (Optimized)\n")
    repo_map.append(f"Generated at: {os.popen('date').read().strip()}\n")
    repo_map.append("Ce document permet aux agents IA de comprendre la structure globale.\n")

    for p in sorted(root.rglob('*')):
        # Skip hidden files except identity ones
        if p.name.startswith('.') and p.name not in {'.agent'}:
            continue
            
        if any(part in ignored_dirs for part in p.parts):
            continue
        
        rel_path = p.relative_to(root)
        depth = len(p.parts) - len(root.parts)
        
        # Limiter la profondeur affichée pour les très gros projets
        if depth > 4:
            continue
            
        indent = "  " * (depth - 1)

        if p.is_dir():
            repo_map.append(f"{indent}📁 **{rel_path.name}/**")
        elif p.suffix not in ignored_extensions:
            summary = ""
            # On ne résume que les fichiers à la racine ou profondeur 1 pour gagner de la place
            if depth <= 2:
                if p.suffix == '.py':
                    try:
                        with open(p, 'r', encoding='utf-8') as f:
                            # Juste la première ligne non vide (souvent le docstring ou l'import principal)
                            for line in f:
                                if line.strip() and not line.startswith('#'):
                                    summary = f" — `{line.strip()[:60]}...`"
                                    break
                    except: pass
                elif p.suffix == '.md':
                    try:
                        with open(p, 'r', encoding='utf-8') as f:
                            line = f.readline().strip()
                            if line.startswith('#'):
                                summary = f" — *{line.strip('#').strip()}*"
                    except: pass
            
            repo_map.append(f"{indent}📄 {rel_path.name}{summary}")

    content = "\n".join(repo_map)
    # Check total length
    if len(content) > 100000: # Max 100KB for the map
        repo_map = repo_map[:500] # Truncate if still too big
        repo_map.append("\n... (Arborescence tronquée car trop large)")
        content = "\n".join(repo_map)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    project_root = "/Users/francois-jeandazin/AETHERFLOW"
    output = os.path.join(project_root, "REPO_MAP.md")
    generate_repo_map(project_root, output)
    print(f"✓ REPO_MAP.md optimisée générée dans {output}")
