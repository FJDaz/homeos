#!/bin/bash
# Script pour démarrer l'API FastAPI Sullivan

cd "$(dirname "$0")"

echo "🚀 Démarrage API FastAPI Sullivan..."
echo ""

# Activer venv
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "⚠️  Virtualenv non trouvé, utilisation de Python système"
fi

# Libérer le port 8000 si déjà utilisé
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "⚠️  Le port 8000 est déjà utilisé"
    echo "Arrêt des processus sur le port 8000..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 2
    if lsof -ti:8000 > /dev/null 2>&1; then
        echo "❌ Impossible de libérer le port 8000. Arrêtez manuellement : lsof -ti:8000 | xargs kill -9"
        exit 1
    fi
fi

# Démarrer l'API (modèle chargé 1×, reste en mémoire)
# host 0.0.0.0 = exposée sur toutes les interfaces (localhost + réseau)
echo "📡 Démarrage API sur http://0.0.0.0:8000 (accessible http://localhost:8000)"
echo ""
echo "💡 Mode serveur : pour N× runs sans recharger le modèle, appelez /execute via HTTP :"
echo "   python scripts/run_via_api.py 11 -q   # 11× PROTO"
echo "   python scripts/run_via_api.py 5 -f    # 5× PROD"
echo ""
python -c "
import sys
sys.path.insert(0, '.')
from Backend.Prod.api import run_api
run_api(host='0.0.0.0', port=8000)
"
