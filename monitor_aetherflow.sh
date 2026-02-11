#!/bin/bash

# Monitor Aetherflow - Affichage temps réel des tasks en cours
# Usage: ./monitor_aetherflow.sh

echo "🔍 AETHERFLOW MONITOR - Temps réel"
echo "=================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Fonction pour afficher une task
show_task() {
    local task_id=$1
    local output_file=$2

    if [ -f "$output_file" ]; then
        local lines=$(wc -l < "$output_file" 2>/dev/null || echo "0")
        local size=$(ls -lh "$output_file" | awk '{print $5}')

        echo -e "${BLUE}Task $task_id${NC}"
        echo "  Output: $output_file"
        echo "  Lines: $lines | Size: $size"
        echo ""
        echo -e "${YELLOW}--- Dernières 20 lignes ---${NC}"
        tail -n 20 "$output_file"
        echo ""
    else
        echo -e "${RED}❌ Fichier non trouvé: $output_file${NC}"
    fi
}

# Récupérer les tasks en cours
TASK_DIR="/private/tmp/claude-501/-Users-francois-jeandazin-AETHERFLOW/tasks"

if [ ! -d "$TASK_DIR" ]; then
    echo -e "${RED}❌ Répertoire tasks non trouvé: $TASK_DIR${NC}"
    exit 1
fi

# Lister les fichiers .output récents (dernières 24h)
echo -e "${GREEN}📊 Tasks en cours (dernières 24h):${NC}"
echo ""

find "$TASK_DIR" -name "*.output" -mtime -1 -type f | while read output_file; do
    task_id=$(basename "$output_file" .output)
    show_task "$task_id" "$output_file"
    echo "=========================================="
    echo ""
done

# Si aucune task trouvée
if [ $(find "$TASK_DIR" -name "*.output" -mtime -1 -type f | wc -l) -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Aucune task en cours dans les dernières 24h${NC}"
fi

echo ""
echo -e "${GREEN}✅ Monitoring terminé${NC}"
echo ""
echo "Pour suivre une task en temps réel:"
echo "  tail -f $TASK_DIR/<task_id>.output"
