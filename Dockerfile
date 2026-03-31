# HoméOS — Dockerfile pour HF Spaces Docker
# Port : 7860 (obligatoire HF)
# User : 1000 (non-root, obligatoire HF)

FROM python:3.11-slim

# Dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dépendances Python (layer cachée si requirements.hf.txt inchangé)
COPY requirements.hf.txt .
RUN pip install --no-cache-dir -r requirements.hf.txt

# Code source
COPY . .

# Répertoires d'état (non versionnés, créés ici avec bonnes permissions)
RUN mkdir -p db exports \
    "Frontend/3. STENCILER/logs" \
    "Frontend/3. STENCILER/output" \
    && chmod +x start_hf.sh \
    && chown -R 1000:1000 /app

EXPOSE 7860

# HF Spaces impose l'utilisateur 1000
USER 1000

CMD ["/app/start_hf.sh"]
