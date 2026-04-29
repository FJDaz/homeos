#!/bin/bash
# AetherFlow — Stenciler Quick Start
STENCILER_DIR="$(cd "$(dirname "$0")/Frontend/3. STENCILER" && pwd)"
VENV="$(cd "$(dirname "$0")" && pwd)/venv/bin/activate"

echo "Nettoyage du port 9998..."
lsof -ti :9998 | xargs kill -9 2>/dev/null
sleep 1

echo "Activation du venv..."
if [ ! -f "$VENV" ]; then
    echo "ERREUR : venv introuvable à $VENV"
    exit 1
fi
source "$VENV"

echo "Démarrage du serveur..."
cd "$STENCILER_DIR"
nohup python3 server_v3.py > /tmp/server_v3.log 2>&1 &
echo "PID: $!"

echo "Attente (max 60s)..."
for i in {1..60}; do
    if curl -s --max-time 1 http://localhost:9998/api/classes > /dev/null 2>&1; then
        echo "SERVEUR PRET — http://localhost:9998 (${i}s)"
        exit 0
    fi
    sleep 1
done

echo "TIMEOUT — tail /tmp/server_v3.log :"
tail -20 /tmp/server_v3.log
exit 1
