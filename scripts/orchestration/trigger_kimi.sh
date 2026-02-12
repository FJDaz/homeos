#!/bin/bash

################################################################################
# trigger_kimi.sh — Création mission KIMI dans collaboration_hub.md
#
# Usage:
#   ./trigger_kimi.sh ETAPE_10
#   ./trigger_kimi.sh 10
#
# Conformité: Constitution AETHERFLOW V2.4, Article 10
# Auteur: Claude Sonnet 4.5 (Backend Lead)
# Date: 12 février 2026
################################################################################

set -euo pipefail

# Configuration
readonly HUB_FILE="collaboration_hub.md"
readonly ROADMAP_FILE="docs/02-sullivan/FIGMA-Like/ROADMAP_12FEV_2026.md"
readonly MAILBOX_DIR="docs/02-sullivan/mailbox/kimi"

# Couleurs
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

################################################################################
# Fonctions utilitaires
################################################################################

log_info() {
    echo -e "${BLUE}ℹ️  $*${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $*${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $*${NC}"
}

log_error() {
    echo -e "${RED}❌ $*${NC}"
}

################################################################################
# Normalisation numéro étape
################################################################################

normalize_step() {
    local input="$1"

    # Si déjà au format ETAPE_X, retourner tel quel
    if [[ "$input" =~ ^ETAPE_[0-9]+$ ]]; then
        echo "$input"
        return 0
    fi

    # Si format numérique simple (ex: "10"), convertir
    if [[ "$input" =~ ^[0-9]+$ ]]; then
        echo "ETAPE_$input"
        return 0
    fi

    # Format invalide
    log_error "Format invalide: $input"
    log_info "Formats acceptés: ETAPE_10, 10"
    return 1
}

################################################################################
# Vérification étape existe
################################################################################

check_step_exists() {
    local step="$1"

    if [[ ! -f "$ROADMAP_FILE" ]]; then
        log_error "Roadmap introuvable: $ROADMAP_FILE"
        return 1
    fi

    if ! grep -q "### $step" "$ROADMAP_FILE"; then
        log_error "$step introuvable dans la roadmap"
        log_info "Étapes disponibles:"
        grep -o "### ÉTAPE [0-9]*" "$ROADMAP_FILE" | sed 's/### /  - /'
        return 1
    fi

    return 0
}

################################################################################
# Recherche documentation
################################################################################

find_documentation() {
    local step="$1"

    if [[ ! -d "$MAILBOX_DIR" ]]; then
        log_warning "Répertoire mailbox introuvable: $MAILBOX_DIR"
        echo ""
        return 0
    fi

    # Recherche fichiers correspondants (case insensitive)
    local doc_file
    doc_file=$(find "$MAILBOX_DIR" -iname "*$step*" -o -iname "*${step//_/}*" | head -n 1)

    if [[ -n "$doc_file" ]]; then
        echo "$doc_file"
    else
        log_warning "Documentation KIMI introuvable pour $step"
        echo ""
    fi
}

################################################################################
# Extraction tâches KIMI depuis roadmap
################################################################################

extract_kimi_tasks() {
    local step="$1"

    if [[ ! -f "$ROADMAP_FILE" ]]; then
        return 1
    fi

    # Extraire section étape + section "Tâches KIMI"
    awk "/### $step/,/^###/ {print}" "$ROADMAP_FILE" | \
        awk '/\*\*Tâches KIMI\*\*/,/^$/ {print}' | \
        grep '^\- \[' || echo "- [ ] Voir roadmap pour détails"
}

################################################################################
# Création mission dans hub
################################################################################

create_mission() {
    local step="$1"
    local doc_file="$2"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    local mission_content
    mission_content=$(cat <<EOFMISSION

---

## 🎯 MISSION KIMI : $step

**Date** : $timestamp
**De** : Claude Sonnet 4.5 (Backend Lead)
**À** : KIMI 2.5 (Frontend Lead)
**Status** : 🔴 EN ATTENTE KIMI

### Instructions

EOFMISSION
)

    # Ajouter lien documentation si disponible
    if [[ -n "$doc_file" ]]; then
        mission_content+="Voir documentation complète : \`$doc_file\`

"
    else
        mission_content+="Voir roadmap : \`$ROADMAP_FILE\`

"
    fi

    # Ajouter tâches
    mission_content+="### Tâches à réaliser

"
    mission_content+="$(extract_kimi_tasks "$step")

"

    # Ajouter signal attendu
    mission_content+="### Signal de fin attendu

Une fois terminé, écrire dans \`collaboration_hub.md\` :
\`\`\`
@CLAUDE_VALIDATE
## CR KIMI : $step TERMINÉE
\`\`\`

**URL validation** : http://localhost:9998/stenciler

---
"

    # Écrire dans hub
    if [[ ! -f "$HUB_FILE" ]]; then
        echo "# Collaboration Hub Claude ↔ KIMI" > "$HUB_FILE"
        echo "" >> "$HUB_FILE"
    fi

    echo "$mission_content" >> "$HUB_FILE"
}

################################################################################
# Affichage confirmation
################################################################################

display_confirmation() {
    local step="$1"
    local doc_file="$2"

    echo ""
    log_success "Mission KIMI créée : $step"
    echo ""
    echo -e "${YELLOW}📋 Tâches déléguées :${NC}"
    extract_kimi_tasks "$step" | sed 's/^/  /'
    echo ""

    if [[ -n "$doc_file" ]]; then
        echo -e "${BLUE}📄 Documentation : $doc_file${NC}"
    fi

    echo -e "${BLUE}🔗 Validation : http://localhost:9998/stenciler${NC}"
    echo ""
    echo -e "${YELLOW}⏳ En attente signal @CLAUDE_VALIDATE dans collaboration_hub.md${NC}"
    echo ""
    log_info "François-Jean, KIMI peut commencer sa mission."
}

################################################################################
# Fonction principale
################################################################################

main() {
    if [[ $# -eq 0 ]]; then
        log_error "Usage: $0 <ETAPE_X | X>"
        log_info "Exemples:"
        log_info "  $0 ETAPE_10"
        log_info "  $0 10"
        exit 1
    fi

    local step_input="$1"
    local step

    # Normaliser étape
    step=$(normalize_step "$step_input") || exit 1

    # Vérifier étape existe
    check_step_exists "$step" || exit 1

    # Chercher documentation
    local doc_file
    doc_file=$(find_documentation "$step")

    # Créer mission
    create_mission "$step" "$doc_file"

    # Confirmation
    display_confirmation "$step" "$doc_file"

    log_success "Mission écrite dans $HUB_FILE"
}

################################################################################
# Point d'entrée
################################################################################

main "$@"
