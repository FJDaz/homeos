#!/bin/bash

# Configuration pour utiliser le proxy local (GLM-5)
export ANTHROPIC_BASE_URL="http://localhost:8082/v1"
export ANTHROPIC_API_KEY="sk-ant-free-claude-code"
export CLAUDE_CODE_MODEL="claude-3-5-sonnet-20241022"

echo "--- Lancement de Claude Code (Camouflé pour GLM-5) ---"
echo "Note: Le serveur proxy dans 'free-claude-code' doit être actif."
echo "-------------------------------------------"

claude
