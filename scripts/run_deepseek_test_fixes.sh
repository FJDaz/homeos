#!/bin/bash
# Script pour lancer DeepSeek sur Test Fixes Part 2 (parallèle Gemini)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║   DeepSeek Test Fixes Part 2 (Parallèle)   ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "📋 Mission : MISSION_DEEPSEEK_TEST_FIXES_PART2.md"
echo "🎯 Périmètre : Tests N-Z + Sullivan"
echo "⏱️  Temps estimé : 1h (parallèle avec Gemini)"
echo ""

# Activer venv
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Lancer diagnostic
echo "🔍 Phase 1 : Diagnostic des tests..."
echo ""

pytest Backend/Prod/tests/test_[n-z]*.py Backend/Prod/tests/sullivan/ -v --tb=short > deepseek_tests_output.txt 2>&1

FAILED_COUNT=$(grep -c "FAILED" deepseek_tests_output.txt || echo "0")
PASSED_COUNT=$(grep -c "PASSED" deepseek_tests_output.txt || echo "0")

echo "✅ Tests PASSED : $PASSED_COUNT"
echo "❌ Tests FAILED : $FAILED_COUNT"
echo ""
echo "📄 Output sauvegardé : deepseek_tests_output.txt"
echo ""

# Lancer DeepSeek Chat pour analyse
echo "🤖 Lancement DeepSeek Chat CLI pour analyse..."
echo ""

cat << 'EOF' | python scripts/deepseek_chat.py --system "Tu es un expert QA Python. Analyse les tests échoués et propose des fixes (skip avec raison claire, ou fix import). NE MODIFIE PAS le code source." --file deepseek_tests_output.txt

Analyse ce rapport de tests et identifie :

1. Les tests à skip (dépendances externes, méthodes supprimées)
2. Les imports à fixer
3. Les bugs réels à documenter

Pour chaque test échoué, dis-moi :
- Nom du test
- Raison de l'échec
- Action recommandée (skip/fix import/documenter bug)

Sois concis et actionnable.

EOF

echo ""
echo "✓ Analyse terminée"
echo ""
echo "📝 Prochaines étapes :"
echo "1. Implémenter les fixes recommandés"
echo "2. Relancer pytest pour vérifier"
echo "3. Rédiger CR_TEST_FIXES_PART2.md"
echo ""
