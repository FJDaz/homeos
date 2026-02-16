#!/bin/bash
# QA Quick Check avec DeepSeek Chat CLI
# Usage: ./scripts/qa_quick.sh <fichier_CR>

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ -z "$1" ]; then
    echo "❌ Usage: $0 <fichier_CR>"
    echo ""
    echo "Exemples:"
    echo "  $0 docs/02-sullivan/mailbox/kimi/CR_STEP5_CARREFOUR_CREATIF.md"
    echo "  $0 CR_STEP6.md  (cherche dans mailbox/kimi/)"
    exit 1
fi

CR_FILE="$1"

# Si juste le nom du fichier, chercher dans mailbox/kimi ou gemini
if [[ ! "$CR_FILE" == *"/"* ]]; then
    # Essayer d'abord kimi
    if [ -f "$PROJECT_ROOT/docs/02-sullivan/mailbox/kimi/$CR_FILE" ]; then
        CR_FILE="docs/02-sullivan/mailbox/kimi/$CR_FILE"
    # Sinon essayer gemini
    elif [ -f "$PROJECT_ROOT/docs/02-sullivan/mailbox/gemini/$CR_FILE" ]; then
        CR_FILE="docs/02-sullivan/mailbox/gemini/$CR_FILE"
    else
        CR_FILE="docs/02-sullivan/mailbox/kimi/$CR_FILE"
    fi
fi

# Vérifier que le fichier existe
if [ ! -f "$PROJECT_ROOT/$CR_FILE" ]; then
    echo "❌ Fichier introuvable : $CR_FILE"
    exit 1
fi

cd "$PROJECT_ROOT"

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║   QA Quick Check - DeepSeek Chat CLI       ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "📄 Fichier : $CR_FILE"
echo ""

# Activer venv
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Créer prompt automatique
PROMPT="Analyse ce CR et donne un verdict clair :

1. Verdict (GO/NO-GO) avec raison
2. Tests (combien passent ?)
3. Issues critiques (s'il y en a)
4. Prêt pour étape suivante ? (OUI/NON)

Sois concis et factuel."

# Lancer analyse
echo "$PROMPT" | python scripts/deepseek_chat.py \
    --system "Tu es un expert QA. Donne des verdicts GO/NO-GO clairs et concis." \
    --file "$CR_FILE"

echo ""
echo "✓ Analyse terminée"
