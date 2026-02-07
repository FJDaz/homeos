# MISSION MONITORING — Système de visibilité

**De** : Claude-Code Senior
**Pour** : KIMI Padawan
**Date** : 3 février 2026
**Priorité** : HAUTE
**Problème** : On ne voit RIEN de ce que tu fais

---

## Le problème

L'utilisateur n'a aucune visibilité sur tes actions :
- Pas de logs en temps réel
- Pas de dashboard
- Pas de notifications
- On découvre après coup ce que tu as fait (ou cassé)

---

## Ce que tu dois créer

### 1. Fichier de log centralisé

**Créer** : `logs/sullivan_activity.log`

Chaque action doit être loguée avec :
```
[2026-02-03 19:45:32] [KIMI] [ACTION] Description de l'action
[2026-02-03 19:45:33] [KIMI] [FILE] Fichier modifié: Backend/Prod/api.py
[2026-02-03 19:45:34] [KIMI] [SUCCESS] Mission X terminée
[2026-02-03 19:45:35] [KIMI] [ERROR] Erreur: description
```

### 2. Script de monitoring temps réel

**Créer** : `scripts/monitor.sh`

```bash
#!/bin/bash
# Monitor Sullivan/KIMI activity in real-time

LOG_FILE="logs/sullivan_activity.log"
MAILBOX_DIR=".claude/mailbox"

echo "🔍 Sullivan Monitor — Ctrl+C pour quitter"
echo "==========================================="

# Créer le fichier si n'existe pas
mkdir -p logs
touch $LOG_FILE

# Afficher les dernières lignes puis suivre
tail -f $LOG_FILE | while read line; do
    # Coloriser selon le type
    if [[ $line == *"[ERROR]"* ]]; then
        echo -e "\033[31m$line\033[0m"  # Rouge
    elif [[ $line == *"[SUCCESS]"* ]]; then
        echo -e "\033[32m$line\033[0m"  # Vert
    elif [[ $line == *"[ACTION]"* ]]; then
        echo -e "\033[33m$line\033[0m"  # Jaune
    else
        echo "$line"
    fi
done
```

### 3. Fonction de log dans ton code

Quand tu modifies du code Python, ajoute cette fonction :

**Fichier** : `Backend/Prod/sullivan/agent/monitor.py`

```python
"""Sullivan Activity Monitor - Logging centralisé."""
import os
from datetime import datetime
from pathlib import Path
from loguru import logger

LOG_FILE = Path(__file__).parent.parent.parent.parent.parent / "logs" / "sullivan_activity.log"

def log_activity(source: str, action_type: str, message: str):
    """Log une activité Sullivan/KIMI.

    Args:
        source: KIMI, SULLIVAN, CLAUDE, USER
        action_type: ACTION, FILE, SUCCESS, ERROR, INFO
        message: Description de l'action
    """
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{source}] [{action_type}] {message}\n"

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line)

    # Aussi dans loguru pour le terminal
    logger.info(f"[{source}] {message}")

def log_file_change(filepath: str, action: str = "MODIFIED"):
    """Log un changement de fichier."""
    log_activity("KIMI", "FILE", f"{action}: {filepath}")

def log_mission_start(mission_name: str):
    """Log le début d'une mission."""
    log_activity("KIMI", "ACTION", f"▶ Mission démarrée: {mission_name}")

def log_mission_end(mission_name: str, success: bool = True):
    """Log la fin d'une mission."""
    status = "SUCCESS" if success else "ERROR"
    emoji = "✓" if success else "✗"
    log_activity("KIMI", status, f"{emoji} Mission terminée: {mission_name}")
```

### 4. Notification macOS (optionnel)

**Ajouter dans** `scripts/monitor.sh` :

```bash
# Notification macOS quand une mission termine
notify_macos() {
    osascript -e "display notification \"$1\" with title \"Sullivan Monitor\""
}

# Dans la boucle tail -f, ajouter:
if [[ $line == *"[SUCCESS]"* ]]; then
    notify_macos "$line"
fi
```

---

## Comment l'utiliser

### Terminal 1 : Lancer le monitor
```bash
chmod +x scripts/monitor.sh
./scripts/monitor.sh
```

### Terminal 2 : Travailler normalement
Les logs apparaîtront en temps réel dans Terminal 1.

---

## IMPORTANT — Tu dois logger tes actions

À partir de maintenant, CHAQUE action que tu fais doit être loguée :

```python
from Backend.Prod.sullivan.agent.monitor import log_activity, log_file_change, log_mission_start, log_mission_end

# Au début d'une mission
log_mission_start("CLEANUP")

# Quand tu modifies un fichier
log_file_change("Backend/Prod/api.py")

# À la fin
log_mission_end("CLEANUP", success=True)
```

---

## Tests

```bash
# 1. Créer les fichiers
# 2. Lancer le monitor
./scripts/monitor.sh

# 3. Dans un autre terminal, tester
python -c "
from Backend.Prod.sullivan.agent.monitor import log_activity
log_activity('TEST', 'INFO', 'Test de monitoring')
"

# 4. Vérifier que le log apparaît dans Terminal 1
```

---

## Quand tu as terminé

Mets à jour `REPORT_FROM_KIMI.md` :
- [ ] `logs/sullivan_activity.log` créé
- [ ] `scripts/monitor.sh` créé et exécutable
- [ ] `Backend/Prod/sullivan/agent/monitor.py` créé
- [ ] Test effectué

---

**Sans monitoring, on travaille à l'aveugle. C'est inacceptable.**

*— Claude-Code Senior*
