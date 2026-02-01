#!/bin/bash
# Script pour ouvrir le frontend Homeos dans le navigateur

cd "$(dirname "$0")"

FRONTEND_PATH="Frontend/index.html"
API_PORT=8000

echo "🚀 Ouverture du frontend Homeos..."

# Vérifier si l'API est déjà en cours d'exécution
if lsof -ti:$API_PORT > /dev/null 2>&1; then
    echo "✓ API déjà en cours d'exécution sur le port $API_PORT"
else
    echo "⚠️  L'API n'est pas démarrée."
    echo ""
    echo "Pour démarrer l'API, exécutez dans un autre terminal :"
    echo "  cd $(pwd)"
    echo "  source venv/bin/activate"
    echo "  python -m Backend.Prod.api"
    echo ""
    echo "Ou utilisez : python -m Backend.Prod.api &"
    echo ""
    read -p "Voulez-vous démarrer l'API maintenant ? (o/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[OoYy]$ ]]; then
        echo "Démarrage de l'API..."
        source venv/bin/activate 2>/dev/null || echo "⚠️  Virtualenv non trouvé, utilisation de Python système"
        python -m Backend.Prod.api &
        API_PID=$!
        echo "✓ API démarrée (PID: $API_PID)"
        echo "Attente du démarrage de l'API..."
        sleep 3
    fi
fi

# Ouvrir le frontend dans le navigateur par défaut
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "$FRONTEND_PATH"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open "$FRONTEND_PATH" 2>/dev/null || sensible-browser "$FRONTEND_PATH" 2>/dev/null || echo "Ouvrez manuellement: file://$(pwd)/$FRONTEND_PATH"
else
    echo "Système non supporté. Ouvrez manuellement: file://$(pwd)/$FRONTEND_PATH"
fi

echo ""
echo "✓ Frontend ouvert dans le navigateur"
echo ""
echo "📝 Note: Si vous voyez des erreurs CORS, assurez-vous que l'API est démarrée sur http://127.0.0.1:$API_PORT"
echo ""
