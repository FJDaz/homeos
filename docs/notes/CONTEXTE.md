# AETHERFLOW - Contexte Complet

**Date** : Janvier 2025  
**Version** : POC Phase 1 → AetherFlow 2.1  
**Statut** : ✅ **PRODUCTION READY**

---

## 🎯 Vision du Projet

AETHERFLOW est un orchestrateur d'agents IA pour le développement logiciel où :
- **Claude Code (dans Cursor)** = Architecte : génère les plans et orchestre
- **DeepSeek API** = Exécuteur : génère le code selon le plan
- **Aucune Claude API** : Tout contrôle/vérification par Claude Code directement

---

## 📋 Architecture Actuelle

### Workflow Complet

```
1. Utilisateur demande à Claude Code : "Implémente la phase 2"
   ↓
2. Claude Code génère automatiquement plan.json
   ↓
3. Claude Code appelle AETHERFLOW (via claude_helper.execute_plan_cli())
   ↓
4. AETHERFLOW lit plan.json → DeepSeek/Groq/Gemini exécute chaque étape
   ↓
5. Code généré sauvegardé dans output/step_outputs/
   ↓
6. Claude Code récupère les résultats et présente le code final
   ↓
7. Utilisateur reçoit le code validé
```

### Règle Fondamentale

- ✅ **AETHERFLOW utilisé** : UNIQUEMENT pour IMPLÉMENTATION (génération de code)
- ❌ **AETHERFLOW NON utilisé** : Pour vérification, contrôle, analyse (Claude Code fait directement)

---

## 🏗️ Structure du Projet

```
AETHERFLOW/
├── Backend/
│   ├── Prod/
│   │   ├── config/
│   │   │   └── settings.py          # Configuration Pydantic
│   │   ├── models/
│   │   │   ├── plan_reader.py        # Lecture/validation plans JSON
│   │   │   ├── deepseek_client.py   # Client DeepSeek API
│   │   │   ├── metrics.py           # Collecte métriques
│   │   │   ├── agent_router.py      # Routage intelligent
│   │   │   └── feedback_parser.py   # Parser feedback pédagogique
│   │   ├── workflows/
│   │   │   ├── proto.py             # Workflow PROTO
│   │   │   └── prod.py              # Workflow PROD
│   │   ├── cache/
│   │   │   ├── semantic_cache.py    # Cache sémantique
│   │   │   └── prompt_cache.py      # Cache prompts
│   │   ├── orchestrator.py          # Orchestrateur principal
│   │   ├── cli.py                   # Interface ligne de commande
│   │   └── tui/
│   │       ├── app.py                # Application TUI
│   │       └── widgets/              # Widgets TUI
│   └── Notebooks/
│       └── benchmark_tasks/         # Plans de test
├── docs/
│   ├── guides/
│   │   ├── PRD AETHERFLOW.md        # PRD complet
│   │   ├── GUIDELINES.md            # Guidelines développement
│   │   └── SYNTHESE_AETHERFLOW.md   # Synthèse complète
│   └── references/
│       └── plan_schema.json          # Schéma JSON des plans
├── scripts/
│   └── benchmark.py                 # Script de benchmark
└── aetherflow                       # Script de lancement
```

---

## 🔧 Composants Implémentés

### 1. PlanReader (`Backend/Prod/models/plan_reader.py`)
- Lit et valide les plans JSON selon le schéma
- Gère les dépendances entre étapes
- Calcule l'ordre d'exécution

### 2. AgentRouter (`Backend/Prod/models/agent_router.py`)
- Routage intelligent vers providers (DeepSeek, Gemini, Groq, Codestral)
- Gestion cache sémantique
- Injection guidelines (mode BUILD)
- Gestion namespaces cache

### 3. Workflows (`Backend/Prod/workflows/`)
- **ProtoWorkflow** : Prototypage rapide (FAST → DOUBLE-CHECK)
- **ProdWorkflow** : Production qualité (FAST → BUILD → DOUBLE-CHECK)

### 4. Cache Système (`Backend/Prod/cache/`)
- **SemanticCache** : Cache sémantique avec embeddings
- **PromptCache** : Cache prompts réutilisables
- **EmbeddingModelSingleton** : Singleton pour modèle embedding

### 5. Orchestrator (`Backend/Prod/orchestrator.py`)
- Exécution de plans séquentiellement ou en parallèle
- Respecte les dépendances entre étapes
- Sauvegarde les résultats dans output/
- Génère les métriques

### 6. CLI (`Backend/Prod/cli.py`)
- Interface ligne de commande avec Rich
- Affichage progressif des étapes
- Rapport final avec métriques
- Options `--fast`, `--build`, `--check`, `--stats`, `--tui`, `--mentor`

### 7. TUI (`Backend/Prod/tui/`)
- Interface terminal interactive avec Textual
- Dashboard 3 colonnes (Plan, Console, Métriques)
- Quick Generate : Génération directe depuis le TUI
- Save Code : Sauvegarde automatique du code généré

### 8. Workflow Mentor (`Backend/Prod/models/feedback_parser.py`)
- Feedback pédagogique structuré
- Violations de règles détaillées
- Références de code précises
- Suggestions d'amélioration

---

## 📝 Format Plan JSON

Structure attendue (voir `docs/references/plan_schema.json`) :

```json
{
  "task_id": "uuid-v4",
  "description": "Description de la tâche",
  "steps": [
    {
      "id": "step_1",
      "description": "Description détaillée",
      "type": "code_generation|refactoring|analysis",
      "complexity": 0.0-1.0,
      "estimated_tokens": 100-8000,
      "dependencies": [],
      "validation_criteria": ["critère 1", "critère 2"],
      "context": {
        "language": "python",
        "framework": "fastapi",
        "files": ["file1.py"]
      }
    }
  ],
  "metadata": {
    "created_at": "2025-01-25T10:00:00Z",
    "claude_version": "claude-code"
  }
}
```

---

## 🚀 Utilisation

### Pour Claude Code (dans Cursor)

Quand l'utilisateur demande une implémentation :

```python
from Backend.Prod.claude_helper import execute_plan_cli, get_step_output

# 1. Générer le plan (fait automatiquement par Claude Code)
# 2. Exécuter
result = execute_plan_cli(
    plan_path="Backend/Notebooks/benchmark_tasks/mon_plan.json",
    output_dir="output/mon_projet"
)

# 3. Récupérer les résultats
if result["success"]:
    code_step1 = get_step_output("step_1", "output/mon_projet")
    # Présenter le code à l'utilisateur
```

### Pour l'utilisateur (CLI)

```bash
# Exécuter un plan
python -m Backend.Prod.cli \
  --plan Backend/Notebooks/benchmark_tasks/task_01_simple_api.json \
  --output output/test1 \
  --verbose

# Workflow PROTO (rapide)
python -m Backend.Prod.cli --fast \
  --plan plan.json \
  --output output/proto

# Workflow PROD (qualité)
python -m Backend.Prod.cli --build \
  --plan plan.json \
  --output output/prod

# TUI
./aetherflow  # Lance TUI par défaut
./aetherflow --tui --plan plan.json --mentor
```

---

## 📊 Métriques Trackées

- **Performance** : Temps d'exécution total et par étape
- **Coûts** : Coût total par provider (input + output tokens)
- **Tokens** : Tokens utilisés (input/output séparément)
- **Qualité** : Taux de réussite, nombre d'étapes réussies/échouées
- **Cache** : Hit rate, tokens économisés, coût économisé
- **Fichiers** : Liste des fichiers générés

---

## 🧪 Tests et Benchmark

### Tâches de Test Disponibles

- `task_01_simple_api.json` - API REST simple
- `task_02_calculator.json` - Calculatrice avec tests
- `task_03_data_processing.json` - Traitement CSV
- `task_04_authentication.json` - Système auth
- `task_05_database_crud.json` - CRUD SQLite
- `task_06_refactoring.json` - Refactoring code
- `task_07_analysis.json` - Analyse codebase
- `task_08_microservice.json` - Architecture microservice
- `task_09_phase2_validation_test.json` - Test validation

### Segmentation Phase 2

La Phase 2 a été segmentée en parties testables :
1. **Partie 1** : Router de base ✅
2. **Partie 2** : Intégration Codestral ✅
3. **Partie 3** : Intégration Gemini ✅
4. **Partie 4** : Routage avancé ✅

---

## 🔑 Configuration

### Variables d'Environnement (`Backend/.env`)

```bash
# DeepSeek API (OBLIGATOIRE)
DEEPSEEK_API_KEY=votre_clé

# Configuration DeepSeek
DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions
DEEPSEEK_MODEL=deepseek-coder
MAX_TOKENS=4000
TEMPERATURE=0.7
TIMEOUT=60
MAX_RETRIES=3

# Gemini API (optionnel)
GEMINI_API_KEY=votre_clé

# Groq API (optionnel)
GROQ_API_KEY=votre_clé

# Mistral/Codestral API (optionnel)
MISTRAL_API_KEY=votre_clé

# Chemins
OUTPUT_DIR=output
LOGS_DIR=logs

# Coûts (pour tracking)
DEEPSEEK_INPUT_COST_PER_1K=0.00014
DEEPSEEK_OUTPUT_COST_PER_1K=0.00028
```

**PAS de clé Claude API nécessaire** - Claude Code fonctionne dans Cursor.

---

## 📈 Évolution du Projet

### Phase 1 : POC ✅
- ✅ Lecture et validation du plan.json fonctionnelle
- ✅ Exécution d'au moins 5 tâches de benchmark réussies
- ✅ Tracking coûts/performance opérationnel
- ✅ Rapport benchmark généré automatiquement
- ✅ Documentation de base complète

### Phase 2 : Routage Intelligent ✅
- ✅ Router intelligent multi-agents (Codestral, Gemini, Groq)
- ✅ Logique de routage basée sur type/complexity
- ✅ Parallélisation des étapes indépendantes
- ✅ Monitoring temps réel

### Phase 3 : Optimisations ✅
- ✅ Cache sémantique avec singleton
- ✅ Prompt caching
- ✅ Connection pooling
- ✅ Speculative decoding (testé, désactivé par défaut)

### Phase 4 : Expérience Utilisateur ✅
- ✅ TUI (Terminal User Interface)
- ✅ Workflow Mentor (feedback pédagogique)
- ✅ Quick Generate dans TUI
- ✅ Save Code dans TUI

### Phase 5 : À Venir
- ⏳ Interface Web HTML/CSS
- ⏳ Packaging DMG "One-Click"
- ⏳ Benchmarks officiels (SWE-Bench)

---

## 🎯 Prochaines Étapes

1. **Interface Web** : Dashboard HTML/CSS pour visualisation
2. **Packaging** : DMG pour Mac 2016
3. **Benchmarks** : SWE-Bench Lite (>25% target)
4. **Documentation** : Guides utilisateur détaillés

---

## 📚 Documentation

- **PRD Complet** : `docs/guides/PRD AETHERFLOW.md`
- **Synthèse Complète** : `docs/guides/SYNTHESE_AETHERFLOW.md`
- **Modes d'Exécution** : `docs/guides/MODES_EXECUTION.md`
- **Performance** : `docs/guides/PERFORMANCE_OPTIMISATIONS.md`
- **Cache Système** : `docs/guides/CACHE_SYSTEM.md`
- **Benchmarks** : `docs/notes/BENCHMARKS.md`
- **Guidelines** : `docs/guides/GUIDELINES.md`
- **Règle Cursor** : `.cursor/rules/aetherflow-workflow.mdc`

---

## 🔄 Workflow Complet Automatisé

1. **Utilisateur** : "Implémente la phase 2"
2. **Claude Code** : Génère `plan.json` automatiquement
3. **Claude Code** : Appelle `execute_plan_cli(plan.json)`
4. **AETHERFLOW** : Routage intelligent → Code généré
5. **Claude Code** : Récupère résultats → Présente code final
6. **Utilisateur** : Reçoit le code validé

**Aucune intervention manuelle nécessaire.**

---

**Dernière mise à jour** : Janvier 2025  
**Statut** : ✅ **PRODUCTION READY** (AetherFlow 2.1)
