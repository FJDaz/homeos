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

# Libérer le port 9998 si déjà utilisé
if lsof -ti:9998 > /dev/null 2>&1; then
    echo "⚠️  Le port 9998 est déjà utilisé"
    echo "Arrêt des processus sur le port 9998..."
    lsof -ti:9998 | xargs kill -9 2>/dev/null || true
    sleep 2
    if lsof -ti:9998 > /dev/null 2>&1; then
        echo "❌ Impossible de libérer le port 9998. Arrêtez manuellement : lsof -ti:9998 | xargs kill -9"
        exit 1
    fi
fi

# Démarrer l'API (modèle chargé 1×, reste en mémoire)
# host 0.0.0.0 = exposée sur toutes les interfaces (localhost + réseau)
echo "📡 Démarrage API sur http://0.0.0.0:9998 (accessible http://localhost:9998)"
echo ""
echo "💡 Mode serveur : pour N× runs sans recharger le modèle, appelez /execute via HTTP :"
echo "   python scripts/run_via_api.py 11 -q   # 11× PROTO"
echo "   python scripts/run_via_api.py 5 -f    # 5× PROD"
echo ""
# Démarrer l'API avec uvicorn (standard pour FastAPI)
echo "📡 Démarrage'uvicorn' sur http://0.0.0.0:9998"
python3 -m uvicorn Backend.Prod.api:app --host 0.0.0.0 --port 9998

