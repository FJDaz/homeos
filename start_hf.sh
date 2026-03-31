#!/bin/bash
# Startup HoméOS pour HF Spaces
# Le path contient un espace ("3. STENCILER") — quotes obligatoires

set -e

# Créer les répertoires d'état (non versionnés)
mkdir -p /app/db
mkdir -p "/app/Frontend/3. STENCILER/logs"
mkdir -p "/app/Frontend/3. STENCILER/output"
mkdir -p /app/exports

# Lancer le serveur depuis le bon répertoire
# (Path(__file__).parent.resolve() dans server_v3.py dépend de ce cwd)
cd "/app/Frontend/3. STENCILER"

exec uvicorn server_v3:app \
    --host 0.0.0.0 \
    --port 7860 \
    --workers 1 \
    --log-level info
