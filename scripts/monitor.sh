#!/bin/bash
# Sullivan Monitor — Visualisation temps réel des activités
# Usage: ./scripts/monitor.sh

LOG_FILE="logs/sullivan_activity.log"
MAILBOX_DIR=".claude/mailbox"

# Couleurs
RED='\033[31m'
GREEN='\033[32m'
YELLOW='\033[33m'
BLUE='\033[34m'
CYAN='\033[36m'
RESET='\033[0m'

# Notification macOS (optionnel)
notify_macos() {
    if command -v osascript &> /dev/null; then
        osascript -e "display notification \"$1\" with title \"Sullivan Monitor\"" 2>/dev/null
    fi
}

echo -e "${CYAN}🔍 Sullivan Monitor — Ctrl+C pour quitter${RESET}"
echo -e "${CYAN}===========================================${RESET}"
echo ""

# Créer le fichier si n'existe pas
mkdir -p logs
touch $LOG_FILE

# Afficher les 10 dernières lignes puis suivre
echo -e "${BLUE}📜 Dernières activités:${RESET}"
tail -n 10 $LOG_FILE
echo ""
echo -e "${CYAN}👁️ Surveillance en temps réel...${RESET}"
echo ""

# Suivre les nouvelles lignes avec colorisation
tail -f $LOG_FILE | while read line; do
    # Coloriser selon le type
    if [[ $line == *"[ERROR]"* ]]; then
        echo -e "${RED}$line${RESET}"
        notify_macos "$line"
    elif [[ $line == *"[SUCCESS]"* ]]; then
        echo -e "${GREEN}$line${RESET}"
        notify_macos "$line"
    elif [[ $line == *"[ACTION]"* ]]; then
        echo -e "${YELLOW}$line${RESET}"
    elif [[ $line == *"[FILE]"* ]]; then
        echo -e "${BLUE}$line${RESET}"
    elif [[ $line == *"[KIMI]"* ]]; then
        echo -e "${CYAN}$line${RESET}"
    else
        echo "$line"
    fi
done
