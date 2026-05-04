import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).parent.parent.resolve()
LOG_FILE = ROOT_DIR / "logs" / "ux_run.ndjson"
JOURNAL_FILE = ROOT_DIR / "logs" / "UX_JOURNAL.md"
ARCHIVE_DIR = ROOT_DIR / "Frontend" / "4. COMMUNICATION" / "ux_runs"

def compile_journal(archive=False):
    if not LOG_FILE.exists():
        print("Aucun log NDJSON trouvé.")
        return

    events = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    if not events:
        print("Aucun événement à compiler.")
        return

    # Tri par timestamp pour être sûr
    events.sort(key=lambda x: x.get("ts", 0))

    now = datetime.now()
    journal_lines = [
        "# 📖 UX Run — Journal de Navigation Compilé",
        f"*Généré le {now.strftime('%Y-%m-%d %H:%M:%S')}*",
        "",
        "## Séquence Narrative",
        ""
    ]

    last_event = None
    duplicate_count = 0

    for idx, e in enumerate(events):
        tag = e.get("tag", "UNKNOWN")
        label = e.get("label", "")
        project = e.get("project_id", "unknown")
        dt = datetime.fromisoformat(e.get("received_at")) if e.get("received_at") else datetime.fromtimestamp(e.get("ts", 0) / 1000 if e.get("ts", 0) > 1e11 else e.get("ts", 0))
        time_str = dt.strftime("%H:%M:%S")

        # Détection de doublons consécutifs (ex: spam clic ou NAV redondant)
        is_duplicate = False
        if last_event and last_event["tag"] == tag and last_event["label"] == label and last_event["project"] == project:
            time_diff = (e.get("ts", 0) - last_event["ts"])
            if time_diff < 10000:  # Si moins de 10s d'écart (en ms), on le considère comme un doublon/spam
                is_duplicate = True

        if is_duplicate:
            duplicate_count += 1
            # On met à jour le dernier event en mémoire mais on n'écrit pas de nouvelle ligne
            last_event["ts"] = e.get("ts", 0)
            continue
        else:
            # Si on sort d'une série de doublons, on ajoute la mention "x N" à la ligne précédente
            if duplicate_count > 0 and len(journal_lines) > 0:
                journal_lines[-1] = journal_lines[-1] + f" *(x{duplicate_count + 1})*"
            duplicate_count = 0

            # Formater la nouvelle ligne
            icon = "🔹"
            if tag == "NAV": icon = "🧭"
            elif tag == "ACTION": icon = "⚡"
            elif tag == "DECISION": icon = "🧠"
            elif tag == "RESULT": icon = "✅"
            elif tag == "FRICTION": icon = "⚠️"
            elif tag == "WAIT": icon = "⏳"

            line = f"- **[{time_str}]** {icon} **{tag}** : `{label}`"
            if project and project != "unknown":
                line += f" *(Projet: {project})*"
                
            journal_lines.append(line)
            
            last_event = {
                "tag": tag,
                "label": label,
                "project": project,
                "ts": e.get("ts", 0)
            }

    # Fin de boucle, vérifier s'il restait des doublons
    if duplicate_count > 0 and len(journal_lines) > 0:
        journal_lines[-1] = journal_lines[-1] + f" *(x{duplicate_count + 1})*"

    content = "\n".join(journal_lines)

    # Écriture du fichier principal (logs/UX_JOURNAL.md)
    with open(JOURNAL_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Journal compilé avec succès dans : {JOURNAL_FILE.relative_to(ROOT_DIR)}")

    # Archivage si demandé
    if archive:
        if not ARCHIVE_DIR.exists():
            ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        
        archive_name = f"UX_RUN_{now.strftime('%Y-%m-%d_%H%M%S')}.md"
        archive_path = ARCHIVE_DIR / archive_name
        
        with open(archive_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"Archive créée : {archive_path.relative_to(ROOT_DIR)}")
        
        # Nettoyage du fichier NDJSON
        LOG_FILE.unlink()
        print(f"Nettoyage : {LOG_FILE.name} supprimé.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compile les logs UX en journal Markdown.")
    parser.add_argument("--archive", action="store_true", help="Archive le journal et vide les logs NDJSON.")
    args = parser.parse_args()
    
    compile_journal(archive=args.archive)

