**Absolument !** Docker d'emblée, c'est LA bonne décision. Ça évite l'enfer des dépendances et rend le projet partageable instantanément. Voici une stack complète prête à démarrer :

## 🐳 Structure Projet Dockerisée

```
aetherflow/
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── .dockerignore
├── requirements.txt
├── pyproject.toml
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── orchestrator.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── claude.py
│   │   └── deepseek.py
│   ├── tui/
│   │   ├── __init__.py
│   │   └── app.py
│   └── utils/
│       ├── __init__.py
│       ├── config.py
│       └── logger.py
├── data/
│   └── .gitkeep
├── logs/
│   └── .gitkeep
└── tests/
    └── __init__.py
```

## 📦 Fichiers Docker

### `Dockerfile`

```dockerfile
# Utilise Python 3.11 slim pour garder l'image légère
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="votre@email.com"
LABEL description="AetherFlow - Orchestrateur d'agents IA"

# Variables d'environnement Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Crée un utilisateur non-root pour la sécurité
RUN useradd -m -u 1000 aetherflow && \
    mkdir -p /app /app/data /app/logs && \
    chown -R aetherflow:aetherflow /app

# Définit le répertoire de travail
WORKDIR /app

# Copie les fichiers de dépendances
COPY --chown=aetherflow:aetherflow requirements.txt pyproject.toml ./

# Installe les dépendances système nécessaires pour Textual
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installe les dépendances Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copie le code source
COPY --chown=aetherflow:aetherflow src/ ./src/

# Bascule vers l'utilisateur non-root
USER aetherflow

# Expose le port si vous ajoutez une API plus tard
EXPOSE 8000

# Point d'entrée
ENTRYPOINT ["python", "-m", "src.main"]
```

### `docker-compose.yml`

```yaml
version: '3.8'

services:
  aetherflow:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: aetherflow
    
    # Active le mode interactif pour la TUI
    stdin_open: true
    tty: true
    
    # Variables d'environnement depuis .env
    env_file:
      - .env
    
    # Volumes pour persistance
    volumes:
      # Code source en dev (hot reload)
      - ./src:/app/src:ro
      # Données persistantes
      - ./data:/app/data
      # Logs persistants
      - ./logs:/app/logs
      # Config utilisateur
      - ./config:/app/config
    
    # Réseau
    networks:
      - aetherflow-network
    
    # Limites de ressources
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 512M
    
    # Redémarrage automatique
    restart: unless-stopped
    
    # Healthcheck
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Service RAG (ChromaDB) - optionnel pour Phase 2
  chromadb:
    image: chromadb/chroma:latest
    container_name: aetherflow-chromadb
    profiles:
      - rag  # Activé seulement avec: docker-compose --profile rag up
    ports:
      - "8001:8000"
    volumes:
      - ./data/chroma:/chroma/chroma
    environment:
      - IS_PERSISTENT=TRUE
    networks:
      - aetherflow-network

  # Monitoring optionnel
  portainer:
    image: portainer/portainer-ce:latest
    container_name: aetherflow-portainer
    profiles:
      - monitoring
    ports:
      - "9000:9000"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - portainer_data:/data
    restart: unless-stopped

networks:
  aetherflow-network:
    driver: bridge

volumes:
  portainer_data:
```

### `requirements.txt`

```txt
# Core
anthropic==0.40.0
requests==2.31.0
httpx==0.27.0

# TUI
textual==0.86.0
rich==13.9.4

# Utils
python-dotenv==1.0.0
pydantic==2.10.3
pydantic-settings==2.6.1

# Async
asyncio==3.4.3
aiohttp==3.11.10

# Logging
loguru==0.7.2

# JSON/YAML
pyyaml==6.0.2
jsonschema==4.23.0

# RAG (Phase 2)
# chromadb==0.4.22
# sentence-transformers==2.3.1

# Testing
pytest==8.3.4
pytest-asyncio==0.25.2
pytest-cov==6.0.0
```

### `.env.example`

```bash
# Copier vers .env et remplir avec vos clés

# API Keys
ANTHROPIC_API_KEY=sk-ant-xxxxx
DEEPSEEK_API_KEY=sk-xxxxx
GROQ_API_KEY=gsk_xxxxx
MISTRAL_API_KEY=xxxxx
GOOGLE_API_KEY=xxxxx

# Configuration
AETHERFLOW_ENV=development
LOG_LEVEL=INFO
MAX_PARALLEL_TASKS=3

# Coûts et limites
DAILY_BUDGET_USD=10.00
MAX_TOKENS_PER_REQUEST=4000

# Cache
ENABLE_RESPONSE_CACHE=true
CACHE_TTL_SECONDS=3600

# RAG (optionnel)
RAG_ENABLED=false
CHROMA_HOST=chromadb
CHROMA_PORT=8000

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=8080
```

### `.dockerignore`

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Git
.git/
.gitignore

# Env
.env
.env.local

# Data
data/*
!data/.gitkeep
logs/*
!logs/.gitkeep

# Tests
.pytest_cache/
.coverage
htmlcov/

# Docker
Dockerfile
docker-compose.yml
.dockerignore

# Docs
README.md
docs/
*.md
```

## 🚀 Code Source Minimal

### `src/main.py`

```python
#!/usr/bin/env python3
"""
AetherFlow - Point d'entrée principal
"""
import asyncio
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from .utils.config import settings
from .utils.logger import setup_logger
from .tui.app import AetherFlowTUI

console = Console()
logger = setup_logger()


def check_environment():
    """Vérifie que l'environnement est correctement configuré"""
    missing_keys = []
    
    if not settings.anthropic_api_key:
        missing_keys.append("ANTHROPIC_API_KEY")
    if not settings.deepseek_api_key:
        missing_keys.append("DEEPSEEK_API_KEY")
    
    if missing_keys:
        console.print(
            Panel(
                f"[red]❌ Clés API manquantes:[/]\n" + 
                "\n".join(f"  • {key}" for key in missing_keys) +
                "\n\n[yellow]Copiez .env.example vers .env et remplissez vos clés[/]",
                title="Configuration Incomplète",
                border_style="red"
            )
        )
        return False
    
    return True


def main():
    """Point d'entrée principal"""
    console.print(
        Panel.fit(
            "[bold cyan]AetherFlow[/] v0.1.0\n"
            "[dim]Orchestrateur d'agents IA pour makers[/]",
            border_style="cyan"
        )
    )
    
    # Vérification environnement
    if not check_environment():
        sys.exit(1)
    
    logger.info("Démarrage d'AetherFlow")
    
    try:
        # Mode TUI par défaut
        if len(sys.argv) == 1:
            app = AetherFlowTUI()
            app.run()
        
        # Mode CLI avec argument
        else:
            task = " ".join(sys.argv[1:])
            from .orchestrator import Orchestrator
            
            orchestrator = Orchestrator()
            result = asyncio.run(orchestrator.process(task))
            
            console.print(Panel(
                result,
                title="[green]✅ Résultat[/]",
                border_style="green"
            ))
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Interruption par l'utilisateur[/]")
        sys.exit(0)
    except Exception as e:
        logger.exception("Erreur fatale")
        console.print(f"[red]❌ Erreur: {e}[/]")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### `src/utils/config.py`

```python
"""Configuration centralisée avec Pydantic"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Configuration de l'application"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # API Keys
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    deepseek_api_key: str = Field(default="", alias="DEEPSEEK_API_KEY")
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    mistral_api_key: str = Field(default="", alias="MISTRAL_API_KEY")
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    
    # Configuration générale
    environment: str = Field(default="development", alias="AETHERFLOW_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    max_parallel_tasks: int = Field(default=3, alias="MAX_PARALLEL_TASKS")
    
    # Limites
    daily_budget_usd: float = Field(default=10.0, alias="DAILY_BUDGET_USD")
    max_tokens_per_request: int = Field(default=4000, alias="MAX_TOKENS_PER_REQUEST")
    
    # Cache
    enable_cache: bool = Field(default=True, alias="ENABLE_RESPONSE_CACHE")
    cache_ttl: int = Field(default=3600, alias="CACHE_TTL_SECONDS")
    
    # RAG
    rag_enabled: bool = Field(default=False, alias="RAG_ENABLED")
    chroma_host: str = Field(default="localhost", alias="CHROMA_HOST")
    chroma_port: int = Field(default=8001, alias="CHROMA_PORT")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, alias="ENABLE_METRICS")
    metrics_port: int = Field(default=8080, alias="METRICS_PORT")


settings = Settings()
```

### `src/utils/logger.py`

```python
"""Configuration du logger avec Loguru"""
import sys
from pathlib import Path
from loguru import logger

from .config import settings


def setup_logger():
    """Configure le logger"""
    
    # Supprime le logger par défaut
    logger.remove()
    
    # Logger console
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True
    )
    
    # Logger fichier
    log_dir = Path("/app/logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        log_dir / "aetherflow_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="7 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}"
    )
    
    return logger
```

### `src/orchestrator.py`

```python
"""Orchestrateur principal - logique Claude → DeepSeek"""
import asyncio
from typing import List, Dict, Any

from anthropic import Anthropic
import requests

from .utils.config import settings
from .utils.logger import setup_logger

logger = setup_logger()


class Orchestrator:
    """Orchestrateur qui route les tâches entre agents"""
    
    def __init__(self):
        self.claude = Anthropic(api_key=settings.anthropic_api_key)
        self.deepseek_url = "https://api.deepseek.com/v1/chat/completions"
        self.total_cost = 0.0
    
    async def process(self, task: str) -> str:
        """Traite une tâche de bout en bout"""
        logger.info(f"Traitement de la tâche: {task}")
        
        # 1. Claude planifie
        plan = await self._claude_plan(task)
        logger.info(f"Plan créé avec {len(plan['steps'])} étapes")
        
        # 2. Exécution des étapes
        results = []
        for i, step in enumerate(plan['steps'], 1):
            logger.info(f"Étape {i}/{len(plan['steps'])}: {step['description']}")
            
            if step['complexity'] < 0.7:
                result = await self._deepseek_execute(step)
                cost = 0.002  # Estimation
            else:
                result = await self._claude_execute(step)
                cost = 0.018  # Estimation
            
            results.append(result)
            self.total_cost += cost
        
        # 3. Synthèse
        final_result = "\n\n".join(results)
        logger.info(f"Tâche terminée. Coût total: ${self.total_cost:.4f}")
        
        return final_result
    
    async def _claude_plan(self, task: str) -> Dict[str, Any]:
        """Claude analyse et crée un plan"""
        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": f"""Analyse cette tâche et crée un plan d'exécution JSON:

Tâche: {task}

Réponds UNIQUEMENT avec un objet JSON (pas de texte avant/après):
{{
    "steps": [
        {{
            "description": "description courte",
            "type": "code_generation|refactoring|analysis",
            "complexity": 0.5,
            "estimated_tokens": 500
        }}
    ]
}}"""
            }]
        )
        
        # Parse la réponse
        import json
        import re
        
        text = response.content[0].text
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        else:
            raise ValueError("Impossible de parser le plan JSON")
    
    async def _deepseek_execute(self, step: Dict) -> str:
        """DeepSeek exécute une étape simple"""
        response = requests.post(
            self.deepseek_url,
            headers={
                "Authorization": f"Bearer {settings.deepseek_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-coder",
                "messages": [
                    {
                        "role": "user",
                        "content": f"Génère le code pour: {step['description']}"
                    }
                ],
                "max_tokens": step.get('estimated_tokens', 1000)
            },