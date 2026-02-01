#!/bin/bash
# Tester le Studio (API + navigateur) puis lancer AETHERFLOW -q.
# À exécuter dans un terminal EXTERNE (Terminal.app, iTerm) depuis la racine du projet.
# Prérequis : venv avec Python 3.12 ou 3.13 et deps installées (pip install -r requirements.txt)

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Utiliser venv si présent
if [ -x "$ROOT/venv/bin/python" ]; then
  PYTHON="$ROOT/venv/bin/python"
  PIP="$ROOT/venv/bin/pip"
else
  PYTHON=python3
  PIP=pip3
fi

echo "=== 1. Vérification venv / deps ==="
if ! "$PYTHON" -c "import loguru, fastapi" 2>/dev/null; then
  echo "Dépendances manquantes. Création venv avec Python 3.12 ou 3.13 puis: pip install -r requirements.txt"
  echo "Exemple: python3.13 -m venv venv && ./venv/bin/pip install -r requirements.txt"
  exit 1
fi

echo ""
echo "=== 2. Démarrage API (port 8000) en arrière-plan ==="
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
"$PYTHON" -m uvicorn Backend.Prod.api:app --host 127.0.0.1 --port 8000 &
API_PID=$!
sleep 3
if ! curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health | grep -q 200; then
  echo "API n'a pas répondu sur /health. Vérifiez les logs."
  kill $API_PID 2>/dev/null || true
  exit 1
fi
echo "API OK: http://127.0.0.1:8000"
echo "  - Chatbox: http://127.0.0.1:8000/"
echo "  - Studio:  http://127.0.0.1:8000/studio.html"
echo "Ouvrez ces URLs dans votre navigateur pour tester le Studio."
echo ""

echo "=== 3. AETHERFLOW -q ==="
./run_aetherflow.sh -q --plan Backend/Notebooks/benchmark_tasks/plan_studio_genome_frontend.json

echo ""
echo "=== Terminé. L'API tourne toujours (PID $API_PID). Pour arrêter: kill $API_PID ==="
