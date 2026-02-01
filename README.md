# Homeos (AETHERFLOW)

Orchestrateur d'Agents IA pour le Développement Logiciel

**Dépôt GitHub** : https://github.com/FJDaz/homeos

## Architecture

**Homeos** (nom commercial) = **AETHERFLOW** (nom interne du code)

- **Claude Code (Cursor)** = Architecte : Génère les plans et orchestre
- **DeepSeek API** = Exécuteur : Génère le code selon le plan
- **Aucune Claude API** : Tout contrôle/vérification par Claude Code directement

## Workflow

```
Claude Code → Génère plan.json → AETHERFLOW exécute (DeepSeek) → Code livré
```

## Workflows disponibles

- **Quick (`-q`)** : FAST → DOUBLE-CHECK (prototypage rapide)
- **Full (`-f`)** : FAST → BUILD → DOUBLE-CHECK (qualité production). En présence de fichiers Python existants dans le plan, le **mode Surgical Edit** s’active automatiquement : le LLM produit des instructions de modification (JSON) appliquées précisément via l’AST au lieu d’un fichier complet. Voir [docs/guides/Surgical_Edit.md](docs/guides/Surgical_Edit.md).

## Installation

AETHERFLOW peut être installé de plusieurs façons selon vos besoins :

### Méthode 1 : Script d'installation universel (Recommandé)

Le script détecte automatiquement votre OS et configure tout :

```bash
# Télécharger et exécuter le script
curl -O https://raw.githubusercontent.com/FJDaz/homeos/main/scripts/install.sh
chmod +x install.sh
./install.sh
```

Le script :
- ✅ Détecte automatiquement macOS, Linux ou Windows (WSL/Git Bash)
- ✅ Vérifie Python 3.9+ et pip
- ✅ Crée l'environnement virtuel
- ✅ Installe toutes les dépendances
- ✅ Configure `.env` avec assistant interactif

### Méthode 2 : Installation via pip

```bash
# Installation depuis le dépôt
pip install -e .

# Ou depuis PyPI (quand publié)
pip install aetherflow

# Avec dépendances de développement
pip install -e ".[dev]"
```

Après installation, la commande `aetherflow` est disponible globalement.

### Méthode 3 : Docker (Recommandé pour production)

```bash
# Démarrer l'API FastAPI
docker-compose --profile api up -d

# Ou démarrer le CLI
docker-compose --profile cli run --rm aetherflow --help

# Voir tous les profiles disponibles
docker-compose config --services
```

**Profiles disponibles** :
- `cli` : Interface en ligne de commande
- `api` : API FastAPI sur port 8000
- `dev` : Mode développement avec hot-reload
- `prod` : Mode production optimisé

### Méthode 4 : Installation manuelle

```bash
# 1. Cloner le dépôt
git clone https://github.com/FJDaz/homeos.git
cd homeos

# 2. Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# 3. Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env et remplir vos clés API
```

### Configuration des variables d'environnement

Copier `.env.example` vers `.env` et remplir vos clés API :

```bash
cp .env.example .env
```

**Clés API requises** :
- `DEEPSEEK_API_KEY` : **OBLIGATOIRE** - Provider principal pour génération de code

**Clés API optionnelles** :
- `MISTRAL_API_KEY` : Pour Codestral
- `GOOGLE_API_KEY` : Pour Gemini
- `GROQ_API_KEY` : Pour Groq
- `ANTHROPIC_API_KEY` : Pour validation Claude (non utilisé actuellement)

Pour plus de détails, voir [`docs/01-getting-started/INSTALLATION.md`](docs/01-getting-started/INSTALLATION.md).

## Utilisation Rapide

### CLI en ligne de commande

```bash
# Exécuter un plan JSON (workflow quick - prototypage rapide)
aetherflow -q --plan plan.json
# ou
python -m Backend.Prod.cli -q --plan plan.json

# Exécuter un plan JSON (workflow full - qualité production)
aetherflow -f --plan plan.json
# ou
python -m Backend.Prod.cli -f --plan plan.json

# Voir l'aide
aetherflow --help
```

### Genome & Sullivan

```bash
# Générer le Genome (homeos_genome.json) depuis l’API
python -m Backend.Prod.cli genome

# Sullivan lit le Genome et affiche metadata, topology, endpoints
python -m Backend.Prod.cli sullivan read-genome
python -m Backend.Prod.cli sullivan read-genome -g output/studio/homeos_genome.json
```

### API FastAPI

```bash
# Démarrer l'API
./start_api.sh
# ou
python -m Backend.Prod.api
# ou via Docker
docker-compose --profile api up -d

# L'API est accessible sur http://127.0.0.1:8000
# Documentation interactive : http://127.0.0.1:8000/docs
# Vérification détaillée : docs/DOUBLE_CHECK_FASTAPI_INSTALLATION.md
```

### Mode serveur (runs répétés sans recharger le modèle)

Chaque `python -m Backend.Prod.cli -q ...` lance un **nouveau process** → le modèle est rechargé à chaque run. Pour enchaîner N× runs **sans rechargement** :

1. **Démarrer l’API une fois** : `./start_api.sh` ou `python -m Backend.Prod.api`
2. **Lancer N× PROTO ou PROD via HTTP** :

```bash
python scripts/run_via_api.py 11 -q   # 11× PROTO (-q)
python scripts/run_via_api.py 5 -f    # 5× PROD (-f)
python scripts/run_via_api.py 3 -f --plan Backend/Notebooks/benchmark_tasks/mon_plan.json
```

Le modèle reste chargé en mémoire dans le process API ; les runs répétés évitent les rechargements.

### Pour Claude Code (dans Cursor)

```python
from Backend.Prod.claude_helper import execute_plan_cli

result = execute_plan_cli("plan.json", "output/")
```

## Fonctionnalités

### Check de Balance

AETHERFLOW vérifie automatiquement le solde de votre compte API avant chaque requête (si l'API le supporte) :

- **Activation** : `ENABLE_BALANCE_CHECK=true` dans `.env` (activé par défaut)
- **Seuil minimum** : `MIN_BALANCE_THRESHOLD=0.10` (défaut: $0.10)
- Si le solde est insuffisant, la requête échoue avec un message d'erreur clair

## Packaging et Distribution

### Générer un DMG pour macOS

```bash
# Sur macOS uniquement
./scripts/packaging/pyinstaller_mac.sh

# Le DMG sera généré dans dist/
# Exemple: dist/Aetherflow-2.2.0-macos-x86_64.dmg
```

### Tests de portabilité

```bash
# Tester l'installation sur différentes plateformes
./scripts/test_portability.sh

# Génère un rapport JSON et HTML dans le répertoire courant
```

## Documentation

### Guides d'installation et déploiement

- **Installation complète** : [`docs/01-getting-started/INSTALLATION.md`](docs/01-getting-started/INSTALLATION.md) - Guide détaillé avec toutes les méthodes
- **PRD HOMEOS (détaillé)** : [`docs/04-homeos/PRD_HOMEOS.md`](docs/04-homeos/PRD_HOMEOS.md) - Vision, scope, architecture, Sullivan, Genome, Studio, roadmap
- **PRD état actuel** : [`docs/04-homeos/PRD_HOMEOS_ETAT_ACTUEL.md`](docs/04-homeos/PRD_HOMEOS_ETAT_ACTUEL.md) - Détail des composants implémentés

### Documentation technique

- **Contexte complet** : `docs/notes/CONTEXTE.md`
- **Guide de test** : `docs/guides/QUICK_TEST_GUIDE.md`
- **PRD** : `docs/guides/PRD AETHERFLOW.md`
- **Option B (Phase 1)** : `docs/guides/OPTION_B_PHASE1_COMPLETE.md`
- **Benchmark Phase 2** : `docs/guides/BENCHMARK_PHASE2_CODESTRAL.md`

## Structure du Projet

```
AETHERFLOW/
├── Backend/
│   ├── Prod/              # Code de production
│   │   ├── api.py         # API FastAPI
│   │   ├── cli.py         # Interface CLI
│   │   ├── orchestrator.py # Orchestrateur principal
│   │   └── sullivan/      # Sullivan Kernel (génération frontend)
│   └── Notebooks/         # Notebooks Jupyter et plans JSON
├── Frontend/              # Interface web Sullivan
│   ├── index.html         # Chatbox Sullivan
│   ├── css/               # Styles
│   └── js/                # Logique JavaScript
├── docs/                  # Documentation complète
│   ├── INSTALLATION.md    # Guide d'installation
│   └── PRD_HOMEOS_ETAT_ACTUEL.md # PRD actuel
├── scripts/
│   ├── install.sh         # Script d'installation universel
│   ├── packaging/         # Scripts de packaging (DMG, DEB, etc.)
│   └── test_portability.sh # Tests de portabilité
├── docker-compose.yml     # Configuration Docker Compose
├── Backend/Dockerfile     # Dockerfile multi-stage optimisé
├── pyproject.toml         # Configuration package Python
├── requirements.txt       # Dépendances Python
├── .env.example           # Exemple de configuration
└── .cursor/rules/         # Règles Cursor pour Claude Code
```

## Portabilité

AETHERFLOW est conçu pour être portable sur toutes les plateformes :

- ✅ **macOS** : 10.12+ (Sierra), compatible Mac 2016
- ✅ **Linux** : Ubuntu 20.04+, Debian, et autres distributions
- ✅ **Windows** : Windows 10+ (via WSL2 recommandé) ou Git Bash

**Méthodes de déploiement** :
- 🐳 **Docker** : Image optimisée multi-stage (< 500MB)
- 📦 **pip** : Package Python installable (`pip install aetherflow`)
- 💿 **DMG** : Bundle macOS autonome (via PyInstaller)
- 🔧 **Script universel** : Installation automatique multi-OS

## Dépannage

### Erreurs shell dans le terminal intégré Cursor

Si vous voyez `base64: /dev/stdout: Operation not permitted` ou `command not found: dump_zsh_state` après chaque commande, **ce n’est pas AETHERFLOW** mais les hooks shell de Cursor. Le workflow tourne correctement en terminal externe (ex. Terminal.app).

**Solutions** : si Cursor propose une option pour désactiver les hooks (Settings → "hooks" / "shell"), l’utiliser ; sinon ajouter dans `~/.zshrc` : `type dump_zsh_state &>/dev/null || dump_zsh_state() { : }`, ou **lancer AETHERFLOW depuis un terminal externe** (recommandé).

Détails : [docs/TROUBLESHOOTING_CURSOR_SHELL.md](docs/TROUBLESHOOTING_CURSOR_SHELL.md).

---

## Support et Contribution

- **Issues** : [GitHub Issues](https://github.com/FJDaz/homeos/issues)
- **Repository** : [GitHub](https://github.com/FJDaz/homeos)

## Licence

MIT License - Voir le fichier LICENSE pour plus de détails.

---

**Dernière mise à jour** : Janvier 2026  
**Version** : 2.2.0 "Sullivan"
