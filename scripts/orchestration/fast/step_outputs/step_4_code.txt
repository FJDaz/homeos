{
  "operations": [
    {
      "type": "modify_method",
      "target": "display_report",
      "position": "before",
      "code": "
        # Charger l\'état
        local state_json
        state_json=$(load_state)
        COMPACT_COUNT=$(echo \"$state_json\" | grep -o '\"compact_count\": [0-9]*' | cut -d' ' -f2 || echo 0)

        # Déterminer ICC_PERCENT (à partir du rapport)
        local icc_percent=0
        if [[ -n \"$ICC_PERCENT\" ]]; then
          icc_percent=$ICC_PERCENT
        else
          # Extraire ICC du rapport si disponible
          local icc_line
          icc_line=$(extract_kimi_report | grep -i \"icc\" | head -1)
          if [[ -n \"$icc_line\" ]]; then
            icc_percent=$(echo \"$icc_line\" | grep -o '[0-9]*\\.\\?[0-9]*' | head -1)
          fi
        fi

        # Obtenir statut
        local status_icon
        status_icon=$(get_status_icon \"$icc_percent\" \"$COMPACT_COUNT\")

        # Afficher section Métriques Git LLM
        echo \"\"
        echo \"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\"
        echo -e \"${YELLOW}📊 MÉTRIQUES GIT LLM:${NC}\"
        echo -e \"  Tokens CR (approx.): ${TOKENS_CR}\"
        echo -e \"  ICC%: $icc_percent%\"
        echo -e \"  Compact#: $COMPACT_COUNT\"
        echo -e \"  Statut: $status_icon\"

        # Formatage coloré selon statut
        case \"$status_icon\" in
          \"🔴 ROUGE\")
            echo -e \"${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\"
            ;;
          \"🟣 MAGENTA\")
            echo -e \"${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\"
            ;;
          \"🟠 ORANGE\")
            echo -e \"${ORANGE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\"
            ;;
          \"🟢 VERT\")
            echo -e \"${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\"
            ;;
        esac
      "
    }
  ]
}