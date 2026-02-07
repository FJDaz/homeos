#!/bin/bash
# RUN KIMI COMPLET - Genome Inference V3
# Usage: ./RUN_KIMI_COMPLETE.sh

set -e

echo "🚀 PRÉPARATION DU RUN KIMI COMPLET"
echo "=================================="

# Vérifier les bundles
echo "✓ Vérification des bundles..."
if [ ! -f "/tmp/bundle_A_documentation.md" ]; then
    echo "❌ Bundle A (documentation) manquant"
    exit 1
fi

if [ ! -f "/tmp/bundle_B_endpoints.txt" ]; then
    echo "❌ Bundle B (endpoints) manquant"
    exit 1
fi

echo "  - Bundle A: $(wc -l < /tmp/bundle_A_documentation.md) lignes"
echo "  - Bundle B: $(wc -l < /tmp/bundle_B_endpoints.txt) lignes"

# Créer le dossier de sortie
OUTPUT_DIR="output/kimi_run_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"
echo "✓ Dossier de sortie: $OUTPUT_DIR"

# Copier les bundles
cp /tmp/bundle_A_documentation.md "$OUTPUT_DIR/"
cp /tmp/bundle_B_endpoints.txt "$OUTPUT_DIR/"
cp MISSION_KIMI_COMPLETE.md "$OUTPUT_DIR/"

echo ""
echo "📋 POUR LANCER KIMI:"
echo "===================="
echo ""
echo "Option 1 - Ligne de commande:"
echo "  kimi --context $OUTPUT_DIR/bundle_A_documentation.md \\"
echo "       --context $OUTPUT_DIR/bundle_B_endpoints.txt \\"
echo "       --context MISSION_KIMI_COMPLETE.md \\"
echo "       --prompt 'Exécute la mission complète'"
echo ""
echo "Option 2 - Interface web:"
echo "  Copier-coller le contenu de:"
echo "  - MISSION_KIMI_COMPLETE.md (le brief)"
echo "  - bundle_A_documentation.md (la doc)"
echo "  - bundle_B_endpoints.txt (les endpoints)"
echo ""
echo "📁 Fichiers préparés dans: $OUTPUT_DIR"
echo ""
echo "⏱️  Temps estimé pour Kimi: 60-90 minutes"
echo ""
