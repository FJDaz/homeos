# État des lieux - HomeOS

## Meta Plan (5 étapes) – Terminé

### 1. Couche Méta
- Architecture de gestion des modes (construction/projet)
- Système de routage intelligent pour la sélection d'agents
- Matrice de décision basée sur la complexité, taille et type de tâche

### 2. Deux Modes
- **Mode Construction** : Génération et validation de code
- **Mode Projet** : Gestion et orchestration de projets
- Système de commutation transparent entre les modes

### 3. CLI (Command Line Interface)
- Interface en ligne de commande unifiée
- Commandes `homeos mode` et `homeos switch`
- Support des flags `--construction` et `--project`

### 4. IR (Intermediate Representation)
- Pipeline de traitement intermédiaire
- Système d'arbitrage pour la validation
- Représentation standardisée des données

### 5. Construction Bottom-Up
- Approche incrémentale de développement
- Génération de code à partir de spécifications
- Validation progressive des composants

## Package homeos/ – Structure

### Core
- `mode_manager/` : Gestionnaire central des modes (ou `core/mode_manager.py`)
- Fichiers de configuration : `construction_config.yaml`, `project_config.yaml`

### Construction
- `construction/` : Mode construction (adapters Aetherflow/Sullivan, etc.)
- `tests/responsive_test.py` : Tests de réactivité (à implémenter en phase B)

### Project
- `project/` : Mode projet (adapters Aetherflow/Sullivan)

### Config
- `config/` : Configuration (construction_config.yaml, project_config.yaml)

### IR (Pipeline + Arbiter)
- `ir/pipeline.py` : Pipeline genome (intents, features, compartments)
- `ir/arbiter.py` : Arbitre Sullivan (validation)

### CLI
- `cli.py` : Point d'entrée principal
- Commandes : `mode`, `switch --construction|--project`

## CLI – Commandes Disponibles

```bash
# Afficher le mode courant
homeos mode

# Basculer entre les modes
homeos switch --construction
homeos switch --project
```

## API – Endpoints

### Studio Genome
- `GET /studio/genome` — Structure du génome (JSON)
- `GET /files/homeos_genome.json` — Fichier genome

### Routes Sullivan
- Routes de validation Sullivan (selon Backend/Prod/api.py)

## Frontend

### Frontend/ (Vanilla)
- `index.html`, `studio.html`, `studio-genome.js` — Chargement genome, rendu organes

### Frontend-svelte (SvelteKit)
- Designer upload (existant)
- Page Studio genome (à faire en phase B)
- Overlay Sullivan Validation UI (à faire en phase B)

## Test Responsive

- `homeos/construction/tests/responsive_test.py` (phase B) : unités relatives, @media, flex/grid

## Références

- **PLAN_MODE_MANAGER** — Plan directeur des 5 étapes
- **MANIFESTE_HOMEOS_V0** — Vision et contraintes HCI
- **design_tokens** — Tokens de design (docs/04-homeos/design_tokens.yaml)
- **SULLIVAN_VALIDATION_UI** — Spécification overlay validation

## État actuel – Après meta plan ; Phase B à venir

- Meta plan (5 étapes) : fait.
- Phase B (Studio concret) : page Studio genome SvelteKit, overlay Validation UI, câblage API, test responsive.
- Phase A (cette doc) : consolidation et documentation.


class AgentRouter:
    def select_agent(self, task: Task) -> Agent:
        decision_matrix = {
            "code_generation_large": {
                "agent": "deepseek_v3",
                "conditions": [
                    task.complexity > 0.7,
                    task.size_in_tokens > 500,
                    task.type in ["module_creation", "code_generation"]
                ]
            },
            "code_generation_small": {
                "agent": "deepseek_v2",
                "conditions": [
                    task.complexity <= 0.7,
                    task.size_in_tokens <= 500,
                    task.type in ["code_generation"]
                ]
            },
            # Add more decision matrix entries as needed
        }

        for task_type, task_config in decision_matrix.items():
            if all(condition for condition in task_config["conditions"]):
                return task_config["agent"]

        # Default agent selection
        return "default_agent"

# Afficher le mode courant
homeos mode

# Basculer entre les modes
homeos switch --construction
homeos switch --project

# Accéder au génome du studio
homeos genome