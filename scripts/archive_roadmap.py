import os
import re
from pathlib import Path
from datetime import datetime

# Chemins
COMM_DIR = Path("Frontend/4. COMMUNICATION")
SOURCE_FILE = COMM_DIR / "ROADMAP_ACHIEVED.md"
INDEX_FILE = SOURCE_FILE

def archive_roadmap():
    if not SOURCE_FILE.exists():
        print(f"Erreur : {SOURCE_FILE} introuvable.")
        return

    content = SOURCE_FILE.read_text(encoding='utf-8')
    
    # Séparation du header (jusqu'à la première mission)
    parts = re.split(r'(?=\n### )', content, maxsplit=1)
    header = parts[0] if len(parts) > 1 else content
    body = parts[1] if len(parts) > 1 else ""

    # Découpage par mission/thème
    # On cherche les blocs commençant par ###
    missions = re.split(r'(?=\n### )', body)
    
    archives = {} # month_str -> [mission_content]
    
    current_year_month = datetime.now().strftime("%Y-%m")
    
    for mission in missions:
        if not mission.strip(): continue
        
        # Extraction de la date (DATE: 2026-04-15)
        date_match = re.search(r'DATE: (\d{4}-\d{2})', mission)
        if date_match:
            month = date_match.group(1)
        else:
            # Fallback sur le mois en cours si pas de date trouvée
            month = current_year_month
            
        if month not in archives:
            archives[month] = []
        archives[month].append(mission.strip())

    # Génération des fichiers mensuels
    monthly_links = []
    for month in sorted(archives.keys(), reverse=True):
        year, m = month.split('-')
        month_name = datetime(int(year), int(m), 1).strftime("%B %Y")
        filename = f"ROADMAP_ACHIEVED_{year}_{m}.md"
        file_path = COMM_DIR / filename
        
        # On garde le header original pour chaque archive
        archive_content = f"# ROADMAP_ACHIEVED — Archive {month_name}\n\n" + "\n\n---\n\n".join(archives[month])
        file_path.write_text(archive_content, encoding='utf-8')
        print(f"✓ Archive créée : {filename}")
        
        monthly_links.append(f"- [{month_name}](./{filename})")

    # Mise à jour de l'index
    new_index = f"""# ROADMAP_ACHIEVED — Archives Mensuelles
**Append-only. Ne jamais modifier une entrée existante.**

Ce fichier sert d'index aux missions archivées par mois pour optimiser les performances.

## 📁 Archives par mois
{chr(10).join(monthly_links)}

---
*Dernière mensualisation effectuée le {datetime.now().strftime("%d/%m/%Y à %H:%M")}*
"""
    INDEX_FILE.write_text(new_index, encoding='utf-8')
    print(f"✓ Index mis à jour : {INDEX_FILE}")

if __name__ == "__main__":
    archive_roadmap()
