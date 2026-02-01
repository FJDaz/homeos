# ============================================
# BUILD STAGE - Pour la compilation et l'installation
# ============================================
FROM python:3.11-slim-bookworm AS builder

# Variables d'environnement pour optimiser pip
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installation des dépendances système pour build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copie séparée des requirements pour optimiser le cache Docker
COPY requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt

# ============================================
# RUNTIME STAGE - Image finale légère
# ============================================
FROM python:3.11-slim-bookworm AS runtime

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.local/bin:$PATH" \
    PYTHONPATH="/app"

# Installation des dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Création de l'utilisateur non-root
RUN groupadd -r aetherflow && useradd -r -g aetherflow aetherflow

# Copie des packages Python installés
COPY --from=builder /root/.local /home/aetherflow/.local

# Copie du code source
WORKDIR /app
COPY Backend/ ./Backend/
COPY docs/ ./docs/
COPY requirements.txt ./

# Changement de propriétaire
RUN chown -R aetherflow:aetherflow /app && \
    mkdir -p /app/data /app/logs /app/output && \
    chown -R aetherflow:aetherflow /app/data /app/logs /app/output

USER aetherflow

# Exposition du port
EXPOSE 8000

# Healthcheck amélioré avec gestion de différents endpoints
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD sh -c 'curl -f http://localhost:8000/health 2>/dev/null || curl -f http://localhost:8000/ 2>/dev/null || exit 1'

# Commande d'exécution par défaut
CMD ["python", "-m", "Backend.Prod.cli", "--help"]
