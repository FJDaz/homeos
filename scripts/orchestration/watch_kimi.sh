#!/bin/bash

################################################################################
# watch_kimi.sh — Surveillance du signal @CLAUDE_VALIDATE dans collaboration_hub.md
#
# Usage:
#   ./watch_kimi.sh
#   ./watch_kimi.sh &  (en arrière-plan)
#
# Conformité: Constitution AETHERFLOW V2.4, Article 10
# Auteur: Claude Sonnet 4.5 (Backend Lead)
# Date: 12 février 2026
################################################################################

set -euo pipefail

# Configuration
readonly HUB_FILE="collaboration_hub.md"
readonly CHECK_INTERVAL=10  # secondes
readonly MARKER="@CLAUDE_VALIDATE"

# Couleurs
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# État
LAST_CHECK_HASH=""

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
# Vérifications initiales
################################################################################

check_prerequisites() {
    if [[ ! -f "$HUB_FILE" ]]; then
        log_error "Fichier $HUB_FILE introuvable"
        log_info "Création du fichier..."
        touch "$HUB_FILE"
        echo "# Collaboration Hub Claude ↔ KIMI" > "$HUB_FILE"
        echo "" >> "$HUB_FILE"
        echo "Ce fichier sert de point de communication entre Claude (Backend Lead) et KIMI (Frontend Lead)." >> "$HUB_FILE"
        log_success "Fichier créé"
    fi
}

################################################################################
# Notification macOS
################################################################################

send_notification() {
    local title="$1"
    local message="$2"

    if command -v osascript &> /dev/null; then
        osascript -e "display notification \"$message\" with title \"$title\" sound name \"Glass\""
    else
        log_warning "osascript non disponible (notification macOS impossible)"
    fi
}

################################################################################
# Extraction du CR KIMI
################################################################################

extract_kimi_report() {
    if [[ ! -f "$HUB_FILE" ]]; then
        log_error "Fichier $HUB_FILE introuvable"
        return 1
    fi

    # Extraire depuis @CLAUDE_VALIDATE jusqu'à la prochaine section ou fin de fichier
    awk "/$MARKER/,/^---$|^## [^C]|EOF/" "$HUB_FILE"
}

################################################################################
# Git LLM Oriented - Constitution V2.4 Articles 8-10
################################################################################

# Calcul approximatif tokens (Article 8)
estimate_tokens() {
    local text="$1"
    local word_count
    word_count=$(echo "$text" | wc -w | tr -d ' ')

    # Approximation : 1 mot ≈ 1.3 token
    TOKENS_CR=$((word_count * 13 / 10))

    # ICC : contexte KIMI = 128k tokens
    ICC_PERCENT=$(awk "BEGIN {printf \"%.1f\", ($TOKENS_CR / 128000.0) * 100}")
}

# Création snapshot Git LLM (Article 9)
create_snapshot() {
    local timestamp
    local hash
    local filename

    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    hash=$(md5 -q "$HUB_FILE" 2>/dev/null || md5sum "$HUB_FILE" 2>/dev/null | awk '{print $1}' | cut -c1-8)

    mkdir -p snapshots

    filename="snapshots/KIMI_${timestamp}_${hash}.txt"

    {
        echo "Timestamp: $timestamp"
        echo "Model: KIMI"
        echo "ICC: ${ICC_PERCENT}%"
        echo "Tokens CR: ${TOKENS_CR}"
        echo "Compact #: ${COMPACT_COUNT}"
        echo "Hash: $(md5 -q "$HUB_FILE" 2>/dev/null || md5sum "$HUB_FILE" 2>/dev/null | awk '{print $1}')"
        echo ""
        echo "=== Artefact (CR KIMI) ==="
        extract_kimi_report
    } > "$filename"

    log_success "Snapshot Git LLM créé : $filename"
}

# Gestion compteur Compacts (Article 10)
load_compact_count() {
    local state_file=".watcher_state"
    if [[ -f "$state_file" ]]; then
        cat "$state_file" 2>/dev/null || echo "0"
    else
        echo "0"
    fi
}

save_compact_count() {
    echo "$COMPACT_COUNT" > ".watcher_state"
}

increment_compact_count() {
    COMPACT_COUNT=$((COMPACT_COUNT + 1))
    save_compact_count
    log_info "Compact #${COMPACT_COUNT} enregistré"
}

# Statut visuel (Article 10)
get_status_icon() {
    local icc="$1"
    local compacts="$2"

    # Comparaison ICC >= 80
    local icc_high=0
    if (( $(awk "BEGIN {print ($icc >= 80.0)}") )); then
        icc_high=1
    fi

    if [[ $compacts -ge 4 ]]; then
        echo "🔴 ROUGE (CRISE)"
    elif [[ $compacts -eq 3 && $icc_high -eq 1 ]]; then
        echo "🟣 MAGENTA (PRÉ-ALERTE)"
    elif [[ $icc_high -eq 1 ]]; then
        echo "🟠 ORANGE (ATTENTION)"
    else
        echo "🟢 VERT (OPTIMAL)"
    fi
}

################################################################################
# Affichage formaté du CR
################################################################################

display_report() {
    # Charger compteur Compacts
    COMPACT_COUNT=$(load_compact_count)

    # Calcul tokens/ICC
    local cr_text
    cr_text=$(extract_kimi_report)
    estimate_tokens "$cr_text"

    # Statut visuel
    local status
    status=$(get_status_icon "$ICC_PERCENT" "$COMPACT_COUNT")

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}MISSION KIMI TERMINÉE${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "$cr_text"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${YELLOW}📊 MÉTRIQUES GIT LLM (Constitution V2.4)${NC}"
    echo "  Tokens CR   : ${TOKENS_CR}"
    echo "  ICC         : ${ICC_PERCENT}%"
    echo "  Compacts    : ${COMPACT_COUNT}"
    echo "  Statut      : ${status}"
    echo ""

    # Créer snapshot si ICC >= 80%
    if (( $(awk "BEGIN {print ($ICC_PERCENT >= 80.0)}") )); then
        create_snapshot
        increment_compact_count
    fi

    # Alerte CRISE si >= 4 compacts
    if [[ $COMPACT_COUNT -ge 4 ]]; then
        echo ""
        echo -e "${RED}╔════════════════════════════════════════════════╗${NC}"
        echo -e "${RED}║  🚨 CRISE CONTEXTUELLE (Constitution §10.2)   ║${NC}"
        echo -e "${RED}╠════════════════════════════════════════════════╣${NC}"
        echo -e "${RED}║  Compacts: ${COMPACT_COUNT}/4 (LIMITE ATTEINTE)              ║${NC}"
        echo -e "${RED}║  Action requise: Relancer nouvelle session    ║${NC}"
        echo -e "${RED}║  Fiabilité KIMI compromise                     ║${NC}"
        echo -e "${RED}╚════════════════════════════════════════════════╝${NC}"
        echo ""
    fi

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${YELLOW}📋 Actions requises :${NC}"
    echo "  1. Ouvrir http://localhost:9998/stenciler"
    echo "  2. Valider visuellement (Article 10 Constitution)"
    echo "  3. Feedback : 'GO ÉTAPE suivante' ou 'KO, corriger X'"
    echo ""
}

################################################################################
# Proposition relance Claude Code
################################################################################

propose_relaunch() {
    echo -n -e "${YELLOW}🤖 Relancer Claude Code automatiquement ? (y/n) ${NC}"
    read -r response

    case "$response" in
        y|Y|yes|YES)
            log_info "Relance Claude Code..."
            echo "Valider travail KIMI" | claude-code || {
                log_error "Échec relance Claude Code"
                log_info "Relancez manuellement si nécessaire"
            }
            ;;
        *)
            log_info "Relance annulée. Relancez Claude Code manuellement."
            ;;
    esac
}

################################################################################
# Détection du signal
################################################################################

check_signal() {
    if [[ ! -f "$HUB_FILE" ]]; then
        return 1
    fi

    # Calculer hash du fichier
    local current_hash
    current_hash=$(md5 -q "$HUB_FILE" 2>/dev/null || md5sum "$HUB_FILE" 2>/dev/null | awk '{print $1}')

    # Si fichier n'a pas changé, skip
    if [[ "$current_hash" == "$LAST_CHECK_HASH" ]]; then
        return 1
    fi

    LAST_CHECK_HASH="$current_hash"

    # Vérifier présence du marqueur
    if grep -q "$MARKER" "$HUB_FILE"; then
        return 0
    fi

    return 1
}

################################################################################
# Boucle principale
################################################################################

main() {
    log_info "Démarrage surveillance collaboration_hub.md"
    log_info "Intervalle: ${CHECK_INTERVAL}s"
    log_info "Signal attendu: $MARKER"
    log_info "Appuyez sur Ctrl+C pour arrêter"
    echo ""

    check_prerequisites

    # Hash initial
    LAST_CHECK_HASH=$(md5 -q "$HUB_FILE" 2>/dev/null || md5sum "$HUB_FILE" 2>/dev/null | awk '{print $1}')

    while true; do
        if check_signal; then
            # Signal détecté !
            send_notification "Aetherflow" "KIMI a terminé sa mission. Validation requise."
            display_report
            propose_relaunch

            # Arrêter la surveillance après détection
            log_success "Surveillance terminée"
            exit 0
        fi

        # Attendre avant prochain check
        sleep "$CHECK_INTERVAL"
    done
}

################################################################################
# Gestion des signaux
################################################################################

cleanup() {
    echo ""
    log_warning "Arrêt surveillance (Ctrl+C détecté)"
    exit 0
}

trap cleanup SIGINT SIGTERM

################################################################################
# Point d'entrée
################################################################################

main "$@"
