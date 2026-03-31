# Rapport d'Adaptation des Guidelines RAG Sezane pour AETHERFLOW

**Date** : 26 janvier 2026  
**Source** : `/Users/francois-jeandazin/RAG Sezane/docs/guides/GUIDELINES.md`  
**Destination** : AETHERFLOW

---

## 📋 Résumé Exécutif

Ce rapport analyse les guidelines du projet RAG Sezane et propose leur adaptation à AETHERFLOW. Les guidelines couvrent principalement le développement frontend (Vanilla JS, Vite) et certaines pratiques générales (TDD, DRY, sécurité) qui peuvent être adaptées à notre contexte d'orchestration d'agents IA.

---

## 1. Flux de Travail (Workflow)

### ✅ Déjà Implémenté

#### Test-Driven Development (TDD)
- **Statut** : ⚠️ **Partiellement**
- **Implémentation actuelle** :
  - Les `validation_criteria` dans les steps permettent de définir des critères de validation
  - Le système de validation existe (`ClaudeCodeValidator`)
  - Les tests peuvent être demandés dans la description de l'étape (ex: step_5 dans `plan_example.json`)

#### Unité d'Itération : User Story
- **Statut** : ✅ **Implémenté**
- **Implémentation actuelle** :
  - Les plans sont organisés par tâche complète (ex: "Créer une API REST avec authentification")
  - Les steps sont organisés en dépendances logiques
  - Le système respecte les dépendances entre étapes

#### Audit de Session
- **Statut** : ✅ **Implémenté**
- **Implémentation actuelle** :
  - `ExecutionMonitor` suit l'exécution en temps réel
  - `MetricsCollector` collecte les métriques (temps, tokens, coût, succès)
  - Les résultats sont exportés en JSON/CSV
  - Le mode DOUBLE-CHECK permet une validation supplémentaire

### ❌ Non Implémenté

#### TDD Automatique
- **Problème** : Les tests ne sont pas générés automatiquement avant le code
- **Impact** : Le code peut être généré sans tests si non explicitement demandé
- **Solution proposée** : Voir section "Recommandations"

---

## 2. Architecture & Maintenabilité

### ✅ Déjà Implémenté

#### DRY (Don't Repeat Yourself)
- **Statut** : ✅ **Implémenté au niveau système**
- **Implémentation actuelle** :
  - Cache sémantique pour éviter les requêtes redondantes
  - Prompt cache pour réutiliser les blocs de prompts
  - Factorisation des clients LLM (BaseLLMClient)
  - Modules partagés (`utils`, `cache`, `models`)

#### Structure Modulaire
- **Statut** : ✅ **Implémenté**
- **Implémentation actuelle** :
  - Architecture modulaire claire (`Backend/Prod/models/`, `Backend/Prod/config/`)
  - Séparation des responsabilités (Orchestrator, AgentRouter, PlanReader)
  - Principes SOLID respectés (Responsabilité Unique)

### ⚠️ Partiellement Implémenté

#### Point de Bascule (Refactoring)
- **Statut** : ⚠️ **Non automatisé**
- **Problème** : Pas de détection automatique de fichiers >300 lignes
- **Impact** : Certains fichiers peuvent devenir trop longs sans alerte
- **Solution proposée** : Ajouter une validation dans le plan reader ou un linter

#### DRY dans le Code Généré
- **Statut** : ⚠️ **Dépend du prompt**
- **Problème** : Le code généré par les LLM peut contenir de la duplication
- **Impact** : Qualité variable du code généré
- **Solution proposée** : Ajouter des instructions DRY dans les prompts

### ❌ Non Implémenté

#### Structure de Composant Vanilla (State/Logic/View)
- **Statut** : ❌ **Non applicable**
- **Raison** : AETHERFLOW génère du code backend (Python/FastAPI), pas du frontend Vanilla JS
- **Adaptation** : Pourrait être adapté pour les composants backend (Models/Services/Controllers)

---

## 3. Sécurité & Robustesse

### ✅ Déjà Implémenté

#### Variables d'Environnement
- **Statut** : ✅ **Implémenté**
- **Implémentation actuelle** :
  - `Backend/Prod/config/settings.py` utilise Pydantic Settings
  - Toutes les clés API sont dans `.env`
  - Validation des variables d'environnement au démarrage

#### Isolation
- **Statut** : ✅ **Implémenté**
- **Implémentation actuelle** :
  - Architecture modulaire isolée
  - Chaque provider est isolé dans son propre client
  - Gestion des erreurs et retries par provider

### ⚠️ Partiellement Implémenté

#### Protection XSS
- **Statut** : ⚠️ **Non applicable directement**
- **Raison** : AETHERFLOW génère du code backend, pas du frontend
- **Adaptation** : Pourrait être ajouté comme guideline pour le code généré (si génération frontend)

### ❌ Non Implémenté

#### Docker
- **Statut** : ❌ **Non implémenté**
- **Impact** : Pas de parité dev/prod garantie
- **Solution proposée** : Ajouter Dockerfile et docker-compose.yml

---

## 4. Outillage Technique

### ✅ Déjà Implémenté

#### Linter
- **Statut** : ✅ **Partiellement**
- **Implémentation actuelle** :
  - Le projet utilise probablement des linters (à vérifier)
  - Pas de pre-commit hook visible dans le code

#### Git Workflow
- **Statut** : ✅ **Pratique recommandée**
- **Implémentation actuelle** :
  - Structure Git standard
  - Pas de hooks automatiques visibles

### ❌ Non Implémenté

#### Bundler (Vite.js)
- **Statut** : ❌ **Non applicable**
- **Raison** : AETHERFLOW est un projet Python backend, pas frontend
- **Adaptation** : Pourrait être remplacé par des outils Python (poetry, pip-tools)

#### Pre-commit Hook
- **Statut** : ❌ **Non implémenté**
- **Impact** : Pas de validation automatique avant commit
- **Solution proposée** : Ajouter pre-commit hooks avec linters et tests

---

## 5. Lexique de Supervision

### ✅ Déjà Implémenté

#### Intent (Intention Utilisateur)
- **Statut** : ✅ **Implémenté**
- **Implémentation actuelle** :
  - Les plans sont définis par intention utilisateur (ex: "Créer une API REST")
  - Les steps sont organisés pour répondre à cette intention
  - Le système RAG enrichit le contexte avec l'intention

### ❌ Non Implémenté

#### Pre-commit Hook Automatique
- **Statut** : ❌ **Non implémenté**
- **Impact** : Pas de validation automatique avant commit
- **Solution proposée** : Voir section "Recommandations"

---

## 📊 Tableau Récapitulatif

| Guideline | Statut | Priorité | Effort |
|-----------|--------|----------|--------|
| **TDD Automatique** | ❌ Non implémenté | 🔴 Haute | Moyen |
| **DRY dans prompts** | ⚠️ Partiel | 🟡 Moyenne | Faible |
| **Détection fichiers >300 lignes** | ❌ Non implémenté | 🟢 Basse | Faible |
| **Protection XSS (code généré)** | ⚠️ N/A | 🟢 Basse | N/A |
| **Docker** | ❌ Non implémenté | 🟡 Moyenne | Moyen |
| **Pre-commit hooks** | ❌ Non implémenté | 🟡 Moyenne | Faible |
| **Structure State/Logic/View** | ⚠️ Adaptable | 🟢 Basse | Moyen |

---

## 🎯 Recommandations d'Implémentation

### 1. TDD Automatique (Priorité Haute)

#### Problème
Les tests ne sont pas générés automatiquement avant le code.

#### Solution Proposée

**Option A : Détection automatique dans les prompts**
```python
# Dans agent_router.py, méthode _build_step_prompt_stripped()
def _build_step_prompt_stripped(self, step: Step, context: Optional[str] = None) -> str:
    # ... code existant ...
    
    # Détecter si des tests sont nécessaires
    needs_tests = (
        step.type == "code_generation" and
        ("test" not in step.description.lower() and
         not any("test" in str(c).lower() for c in (step.validation_criteria or [])))
    )
    
    if needs_tests:
        # Ajouter instruction pour générer des tests
        instruction = "Generate code with unit tests."
    else:
        instruction = type_instructions.get(step.type, "")
    
    if instruction:
        parts.append(instruction)
```

**Option B : Nouveau type de step "test_generation"**
```json
{
  "id": "step_1_tests",
  "type": "test_generation",
  "description": "Generate unit tests for step_1",
  "dependencies": ["step_1"]
}
```

**Option C : Instruction systématique dans les prompts**
```python
if step.type == "code_generation":
    prompt_parts.append("\nGenerate the complete code implementation with comprehensive unit tests.")
```

**Recommandation** : Option C (la plus simple) + Option A (détection intelligente)

#### Fichiers à Modifier
- `Backend/Prod/models/agent_router.py` : Méthode `_build_step_prompt_stripped()`

---

### 2. DRY dans les Prompts (Priorité Moyenne)

#### Problème
Le code généré peut contenir de la duplication.

#### Solution Proposée

Ajouter une instruction DRY dans les prompts :
```python
# Dans _build_step_prompt_stripped()
if step.type == "code_generation":
    parts.append("Generate code. Follow DRY principle: extract repeated logic into reusable functions.")
```

#### Fichiers à Modifier
- `Backend/Prod/models/agent_router.py` : Méthode `_build_step_prompt_stripped()`

---

### 3. Pre-commit Hooks (Priorité Moyenne)

#### Solution Proposée

Créer `.pre-commit-config.yaml` :
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-toml
  
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3
  
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=120']
  
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

#### Fichiers à Créer
- `.pre-commit-config.yaml`
- Script d'installation : `scripts/setup_pre_commit.sh`

---

### 4. Docker (Priorité Moyenne)

#### Solution Proposée

Créer `Dockerfile` :
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run application
CMD ["python", "-m", "Backend.Prod.cli", "--plan", "plan.json"]
```

Créer `docker-compose.yml` :
```yaml
version: '3.8'

services:
  aetherflow:
    build: .
    volumes:
      - ./output:/app/output
      - ./logs:/app/logs
      - ./.env:/app/.env
    environment:
      - PYTHONUNBUFFERED=1
```

#### Fichiers à Créer
- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`

---

### 5. Détection Fichiers >300 Lignes (Priorité Basse)

#### Solution Proposée

Ajouter une validation dans le plan reader ou créer un linter custom :
```python
# Dans plan_reader.py ou nouveau module validators.py
def validate_step_output_size(step: Step, output: str) -> List[str]:
    """Validate that generated code doesn't exceed recommended size."""
    warnings = []
    lines = output.split('\n')
    
    if len(lines) > 300:
        warnings.append(
            f"Step {step.id} generated {len(lines)} lines. "
            f"Consider splitting into smaller modules (recommended: <300 lines)."
        )
    
    return warnings
```

#### Fichiers à Modifier/Créer
- `Backend/Prod/models/plan_reader.py` ou nouveau `Backend/Prod/models/validators.py`

---

### 6. Structure State/Logic/View Adaptée (Priorité Basse)

#### Solution Proposée

Pour le code backend généré, adapter en Models/Services/Controllers :
```python
# Dans les prompts pour code_generation
if step.context.get("framework") == "fastapi":
    parts.append(
        "Structure: Models (data), Services (business logic), Controllers (API endpoints). "
        "Follow separation of concerns."
    )
```

#### Fichiers à Modifier
- `Backend/Prod/models/agent_router.py` : Méthode `_build_step_prompt_stripped()`

---

## 📝 Plan d'Action Priorisé

### Phase 1 : Quick Wins (1-2 jours)
1. ✅ Ajouter instruction TDD dans les prompts (Option C)
2. ✅ Ajouter instruction DRY dans les prompts
3. ✅ Créer `.pre-commit-config.yaml`

### Phase 2 : Améliorations Moyennes (3-5 jours)
4. ✅ Implémenter détection automatique de tests (Option A)
5. ✅ Ajouter Dockerfile et docker-compose.yml
6. ✅ Créer script d'installation pre-commit

### Phase 3 : Optimisations (Optionnel)
7. ⚠️ Ajouter validation taille fichiers générés
8. ⚠️ Adapter structure State/Logic/View pour backend

---

## 🔍 Points d'Attention

### 1. Contexte Différent
- **RAG Sezane** : Frontend Vanilla JS avec Vite
- **AETHERFLOW** : Backend Python avec orchestration d'agents IA
- **Impact** : Certaines guidelines ne sont pas directement applicables

### 2. Génération de Code vs Développement Manuel
- Les guidelines RAG Sezane sont pour le développement manuel avec IA
- AETHERFLOW génère du code automatiquement via des agents
- **Impact** : Les guidelines doivent être adaptées pour être incluses dans les prompts

### 3. Tests Automatiques
- Le TDD manuel (écrire test puis code) n'est pas directement applicable
- **Solution** : Générer tests et code ensemble, ou tests avant code dans le plan

---

## 📚 Références

- Guidelines source : `/Users/francois-jeandazin/RAG Sezane/docs/guides/GUIDELINES.md`
- Code AETHERFLOW : `Backend/Prod/models/agent_router.py`
- Plan example : `docs/references/plan_example.json`

---

## ✅ Conclusion

Les guidelines RAG Sezane sont **largement compatibles** avec AETHERFLOW, mais nécessitent des **adaptations** :

1. **TDD** : À adapter pour génération automatique (tests + code ensemble)
2. **DRY** : À intégrer dans les prompts plutôt que dans le développement manuel
3. **Sécurité** : Déjà bien couverte (variables d'environnement)
4. **Outillage** : À ajouter (pre-commit hooks, Docker)
5. **Architecture** : Déjà bien structurée, peut être améliorée avec guidelines dans prompts

**Priorité** : Implémenter TDD automatique et DRY dans les prompts (impact immédiat sur qualité du code généré).

---

**Document généré le** : 26 janvier 2026
