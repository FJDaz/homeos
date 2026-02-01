# Documentation d'Installation Aetherflow

## Table des Matières
1. [Prérequis](#prérequis)
2. [Méthodes d'Installation](#méthodes-dinstallation)
3. [Configuration](#configuration)
4. [Exemples d'Utilisation](#exemples-dutilisation)
5. [Dépannage](#dépannage)
6. [FAQ](#faq)

---

## Prérequis

### Systèmes d'exploitation supportés

| Plateforme | Version minimale | Recommandée |
|------------|------------------|-------------|
| **macOS** | 10.15 (Catalina) | 12.0+ (Monterey) |
| **Linux** | Ubuntu 20.04 LTS | Ubuntu 22.04 LTS |
| **Windows** | Windows 10 | Windows 11 / WSL2 |

### Prérequis par plateforme

#### 🍎 **macOS**

**Important** : AETHERFLOW nécessite **Python 3.12 ou 3.13**. Python 3.14 n’est pas supporté (pydantic-core / PyO3 limite à 3.13).

```bash
# 1. Installer Homebrew (si pas déjà installé)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Installer Python 3.12 ou 3.13 (pas 3.14)
brew install python@3.13
# ou: brew install python@3.12

# 3. Créer le venv avec ce Python
cd /chemin/vers/AETHERFLOW
python3.13 -m venv venv
./venv/bin/pip install -r requirements.txt

# 4. Installer Git
brew install git

# 5. Installer Docker Desktop (optionnel)
brew install --cask docker
```

#### 🐧 **Linux (Ubuntu/Debian)**
```bash
# 1. Mettre à jour les paquets
sudo apt update && sudo apt upgrade -y

# 2. Installer Python 3.9+
sudo apt install python3.11 python3.11-venv python3-pip -y

# 3. Installer Git
sudo apt install git -y

# 4. Installer Docker (optionnel)
sudo apt install docker.io docker-compose -y
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

#### 🪟 **Windows**
```bash
# Option 1: WSL2 (Recommandé)
# 1. Installer WSL2
wsl --install

# 2. Installer Ubuntu depuis Microsoft Store
# 3. Suivre les instructions Linux ci-dessus

# Option 2: Native Windows
# 1. Télécharger Python depuis python.org
# 2. Cocher "Add Python to PATH"
# 3. Installer Git pour Windows
```

### Vérification des prérequis
```bash
# Vérifier Python (doit être 3.12 ou 3.13, pas 3.14)
python3 --version  # 3.12.x ou 3.13.x
python3.13 --version  # si installé via brew install python@3.13

# Vérifier pip
pip3 --version

# Vérifier Git
git --version

# Vérifier Docker (optionnel)
docker --version
```

---

## Méthodes d'Installation

### 📦 **Méthode 1: Installation via Docker (Recommandée)**

#### Installation rapide avec Docker Compose
```bash
# 1. Cloner le dépôt
git clone https://github.com/votre-username/aetherflow.git
cd aetherflow

# 2. Copier le fichier d'environnement
cp .env.example .env

# 3. Démarrer les services
docker-compose up -d

# 4. Vérifier l'état
docker-compose ps

# 5. Accéder à l'application
# API: http://localhost:8000
# Documentation: http://localhost:8000/docs
```

#### Configuration Docker avancée
```yaml
# docker-compose.override.yml (pour le développement)
version: '3.8'
services:
  api:
    volumes:
      - ./src:/app/src:rw  # Hot reload
      - ./tests:/app/tests:rw
    environment:
      API_RELOAD: "true"
      APP_DEBUG: "true"
    ports:
      - "8000:8000"
      - "5678:5678"  # Debug port
```

#### Commandes Docker utiles
```bash
# Reconstruire l'image
docker-compose build --no-cache

# Voir les logs
docker-compose logs -f api

# Arrêter les services
docker-compose down

# Supprimer les volumes
docker-compose down -v

# Exécuter des commandes dans le conteneur
docker-compose exec api python manage.py migrate
```

### 🐍 **Méthode 2: Installation native avec Python**

#### Installation via le script universel
```bash
# 1. Télécharger le script d'installation
curl -O https://raw.githubusercontent.com/votre-username/aetherflow/main/scripts/install.sh

# 2. Rendre le script exécutable
chmod +x install.sh

# 3. Exécuter l'installation
./install.sh

# 4. Suivre les instructions à l'écran
```

#### Installation manuelle
```bash
# 1. Cloner le dépôt
git clone https://github.com/votre-username/aetherflow.git
cd aetherflow

# 2. Créer un environnement virtuel (utiliser Python 3.12 ou 3.13, pas 3.14)
python3.13 -m venv venv   # ou python3.12 si installé
# Si vous n'avez que python3 (3.14) : brew install python@3.13 puis python3.13 -m venv venv

# 3. Activer l'environnement
# Sur macOS/Linux:
source venv/bin/activate
# Sur Windows:
venv\Scripts\activate

# 4. Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt

# 5. Installer en mode développement
pip install -e ".[dev]"

# 6. Configurer l'environnement
cp .env.example .env
```

#### Installation avec Poetry
```bash
# 1. Installer Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 2. Installer les dépendances
poetry install

# 3. Activer l'environnement
poetry shell

# 4. Lancer l'application
poetry run python -m aetherflow.cli
```

### 📦 **Méthode 3: Installation depuis PyPI**

```bash
# Installation stable
pip install aetherflow

# Installation avec fonctionnalités avancées
pip install "aetherflow[all]"

# Installation de développement
pip install "aetherflow[dev]"
```

### 🖥️ **Méthode 4: Installation avec gestionnaires de paquets**

#### macOS avec Homebrew
```bash
# Ajouter le tap (quand disponible)
brew tap votre-username/aetherflow

# Installer
brew install aetherflow
```

#### Linux avec Snap
```bash
# (Quand disponible)
sudo snap install aetherflow
```

#### Windows avec Chocolatey
```powershell
# (Quand disponible)
choco install aetherflow
```

---

## Dépannage

### Erreur « Failed building wheel for pydantic-core » / « Python 3.14 is newer than PyO3's maximum (3.13) »

Vous utilisez **Python 3.14** ; pydantic-core (PyO3) ne supporte que jusqu’à 3.13.

**Solution** : créer le venv avec Python 3.12 ou 3.13 :

```bash
# macOS avec Homebrew
brew install python@3.13
cd /chemin/vers/AETHERFLOW
rm -rf venv
python3.13 -m venv venv
./venv/bin/pip install -r requirements.txt
```

Si vous n’installez pas une autre version de Python, vous pouvez tenter (non garanti) :

```bash
PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 pip install -r requirements.txt
```

---

## Configuration

### 🔑 **Configuration des clés API**

#### Fichier `.env`
```bash
# Copier le template
cp .env.example .env

# Éditer le fichier
nano .env
```

#### Variables d'environnement essentielles
```env
# Configuration de base
APP_NAME="Aetherflow"
APP_ENV="development"
APP_SECRET_KEY="votre-clé-secrète-ici"

# Base de données
DATABASE_URL="postgresql://user