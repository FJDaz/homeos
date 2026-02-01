# PRD - Homeos (AETHERFLOW) - État Actuel

**Version** : 2.2 "Sullivan"  
**Date** : 28 janvier 2026  
**Statut** : Beta S1 - En développement actif

---

## 📋 Table des Matières

1. [Vision Produit](#vision-produit)
2. [Positionnement](#positionnement)
3. [Architecture Globale](#architecture-globale)
4. [État Actuel - Fonctionnalités Implémentées](#état-actuel---fonctionnalités-implémentées)
5. [Sullivan Kernel - État d'Implémentation](#sullivan-kernel---état-dimplémentation)
6. [Composants Techniques](#composants-techniques)
7. [Workflows Disponibles](#workflows-disponibles)
8. [API et Interfaces](#api-et-interfaces)
9. [Points d'Amélioration Identifiés](#points-damélioration-identifiés)
10. [Roadmap](#roadmap)

---

## 🎯 Vision Produit

**Homeos** est une **agence de design numérique complète** automatisée par IA, qui accompagne les utilisateurs de la conception à la mise en production :

```
Brainstorm → Backend → Frontend → Deploy
```

**AETHERFLOW** (nom interne du code) est l'orchestrateur d'agents IA qui génère du code de haute qualité en maintenant un équilibre homéostatique entre qualité, performance et maintenabilité.

### Valeur Proposée

- **Génération de code automatisée** : Backend Python/APIs et Frontend HTML/CSS/JS
- **Qualité garantie** : Workflows structurés avec validation automatique
- **Économie de coûts** : Utilisation optimale de modèles LLM économiques (DeepSeek, Gemini, Groq)
- **Intelligence contextuelle** : Analyse automatique du backend pour inférer le frontend correspondant

---

## 🏢 Positionnement

### Homeos = Agence de Design Numérique

**Fonctions principales** :
1. **Brainstorm** : Génération d'idées et concepts (à venir)
2. **Backend** : Génération de code backend Python/APIs via AETHERFLOW
3. **Frontend** : Génération de frontend HTML/CSS/JS via Sullivan Kernel
4. **Deploy** : Déploiement automatisé (à venir)

### AETHERFLOW = Orchestrateur d'Agents IA

**Rôle** : Coordonner l'exécution de plans JSON via différents workflows (PROTO/PROD) en utilisant des modèles LLM économiques.

### Sullivan Kernel = Intelligence Frontend

**Rôle** : Analyser un backend existant, comprendre sa fonction globale métier, et générer le frontend correspondant de manière intelligente.

---

## 🏗️ Architecture Globale

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code (Cursor)                     │
│              Architecte & Orchestrateur Principal          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ Génère plan.json
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌───────────────┐              ┌──────────────────┐
│  AETHERFLOW   │              │ Sullivan Kernel   │
│ Orchestrator  │              │                   │
│               │              │ - BackendAnalyzer │
│ - Workflows   │              │ - UIInference     │
│ - AgentRouter │              │ - ComponentGen   │
│ - Metrics     │              │ - Evaluators     │
└───────┬───────┘              └──────────────────┘
        │
        │ Exécute via LLM
        │
┌───────┴───────────────────────────────────────┐
│         Modèles LLM (DeepSeek, Gemini,        │
│              Groq, Codestral)                 │
└───────────────────────────────────────────────┘
```

### Séparation des Responsabilités

- **Claude Code** : Génère les plans, orchestre l'exécution, valide les résultats
- **AETHERFLOW** : Exécute les plans via workflows structurés
- **Sullivan Kernel** : Analyse backend et génère frontend intelligemment
- **LLM Providers** : Génèrent le code selon les instructions

---

## ✅ État Actuel - Fonctionnalités Implémentées

### 1. AETHERFLOW Core ✅ **COMPLET**

#### Orchestrator (`Backend/Prod/orchestrator.py`)
- ✅ Exécution de plans JSON
- ✅ Workflows PROTO (FAST → DOUBLE-CHECK)
- ✅ Workflows PROD (FAST → BUILD → DOUBLE-CHECK)
- ✅ Parallélisation des étapes indépendantes
- ✅ Rate limiting par provider
- ✅ Métriques complètes (temps, coûts, tokens)
- ✅ Support RAG (enrichissement contexte)
- ✅ Cache sémantique et prompt cache

#### AgentRouter (`Backend/Prod/models/agent_router.py`)
- ✅ Routage intelligent vers providers (DeepSeek, Gemini, Groq, Codestral)
- ✅ Sélection automatique "smartest for least money"
- ✅ Gestion cache sémantique et prompt cache
- ✅ Injection guidelines en mode BUILD
- ✅ Fallback cascade pour Gemini (gestion rate limits)

#### Workflows
- ✅ **ProtoWorkflow** (`Backend/Prod/workflows/proto.py`)
  - FAST → DOUBLE-CHECK (prototypage rapide)
- ✅ **ProdWorkflow** (`Backend/Prod/workflows/prod.py`)
  - FAST → BUILD → DOUBLE-CHECK (qualité maximale)

#### Plan Reader (`Backend/Prod/models/plan_reader.py`)
- ✅ Lecture et validation de plans JSON
- ✅ Support schéma Pydantic
- ✅ Gestion dépendances entre étapes

#### Métriques (`Backend/Prod/models/metrics.py`)
- ✅ `StepMetrics` : Métriques par étape
- ✅ `PlanMetrics` : Métriques agrégées du plan
- ✅ Temps, coûts, tokens, cache hits, latence

### 2. API FastAPI ✅ **OPÉRATIONNELLE**

#### Endpoints Principaux (`Backend/Prod/api.py`)
- ✅ `POST /execute` : Exécute un plan JSON
- ✅ `GET /health` : Health check
- ✅ `POST /sullivan/search` : Recherche de composants
- ✅ `GET /sullivan/components` : Liste des composants
- ✅ `POST /sullivan/dev/analyze` : Analyse backend (DevMode)
- ✅ `POST /sullivan/designer/analyze` : Analyse design (DesignerMode)
- ✅ CORS activé pour développement
- ✅ Servir fichiers statiques frontend

### 3. CLI ✅ **FONCTIONNEL**

#### Commandes (`Backend/Prod/cli.py`)
- ✅ `-q` / `--quick` : Workflow PROTO
- ✅ `-f` / `--full` : Workflow PROD
- ✅ `--plan` : Spécifier plan JSON
- ✅ `--output-dir` : Répertoire de sortie
- ✅ `--mentor` : Mode mentor avec feedback pédagogique

### 4. Sullivan Kernel ✅ **PHASE 1-5 COMPLÈTES**

#### Phase 1 : Analyse Backend ✅
- ✅ **BackendAnalyzer** (`Backend/Prod/sullivan/analyzer/backend_analyzer.py`)
  - Analyse structure projet backend
  - Détection routes API (FastAPI/Flask)
  - Analyse modèles de données (Pydantic/SQLAlchemy)
  - Détection intents automatique
  - Inférence fonction globale métier (type produit, acteurs, flux métier)

- ✅ **UIInferenceEngine** (`Backend/Prod/sullivan/analyzer/ui_inference_engine.py`)
  - Inférence besoins UI depuis fonction globale
  - Approche top-down (Intention → Corps → Organes → Molécules → Atomes)
  - Propose structure d'intention (Niveau 0)
  - Infère Corps (zones de contenu)
  - Infère Organes, Molécules, Atomes

- ✅ **DevMode** (`Backend/Prod/sullivan/modes/dev_mode.py`)
  - Workflow "Collaboration Heureuse"
  - Analyse backend → Inférence fonction globale → Génération frontend
  - Dialogue stratégique (proposition étapes)
  - Maillage des Corps
  - Inférence technique (Organes → Molécules → Atomes)
  - HCI Mentor (surveillance charge cognitive)

#### Phase 2 : Analyse Design ✅
- ✅ **DesignAnalyzer** (`Backend/Prod/sullivan/analyzer/design_analyzer.py`)
  - Analyse designs PNG/Figma/Sketch
  - Extraction structure visuelle
  - Mapping sur structure logique

- ✅ **DesignerMode** (`Backend/Prod/sullivan/modes/designer_mode.py`)
  - Workflow "Génération Miroir"
  - Analyse design → Extraction structure → Mapping logique → Génération frontend

#### Phase 3 : Génération Composants ✅
- ✅ **ComponentGenerator** (`Backend/Prod/sullivan/generator/component_generator.py`)
  - Génération réelle de composants HTML/CSS/JS via AETHERFLOW
  - Création plans JSON automatiques
  - Exécution via workflows PROTO/PROD
  - Parsing code généré depuis outputs
  - Structuration composants avec métadonnées

- ✅ **ComponentRegistry** (`Backend/Prod/sullivan/registry.py`)
  - Orchestration LocalCache → EliteLibrary → Génération
  - Recherche intelligente de composants
  - Génération si non trouvé
  - Évaluation automatique après génération

#### Phase 4 : Évaluation et Scoring ✅
- ✅ **PerformanceEvaluator** (`Backend/Prod/sullivan/evaluators/performance_evaluator.py`)
  - Évaluation performance via Lighthouse CI
  - Score Performance (0-100)

- ✅ **AccessibilityEvaluator** (`Backend/Prod/sullivan/evaluators/accessibility_evaluator.py`)
  - Évaluation accessibilité via axe-core/WCAG
  - Score Accessibilité (0-100)

- ✅ **ValidationEvaluator** (`Backend/Prod/sullivan/evaluators/validation_evaluator.py`)
  - Évaluation validation via AETHERFLOW DOUBLE-CHECK
  - Vérification TDD, DRY, SOLID
  - Score Validation (0-100)

- ✅ **SullivanScore** (`Backend/Prod/sullivan/models/sullivan_score.py`)
  - Calcul score composite (Performance 30%, Accessibilité 30%, Écologie 20%, Popularité 10%, Validation 10%)
  - Seuil Elite Library (85)

#### Phase 5 : Fonctionnalités Avancées ✅
- ✅ **Catégorisation** (`Backend/Prod/sullivan/models/categories.py`)
  - Classification composants (core, complex, domain)
  - Basée sur taille (KB)

- ✅ **Elite Library** (`Backend/Prod/sullivan/library/elite_library.py`)
  - Bibliothèque composants validés (score >= 85)
  - Archivage automatique (> 6 mois sans usage)
  - Retrait composants score < 85
  - Tracking `last_used`

- ✅ **SharingTUI** (`Backend/Prod/sullivan/library/sharing_tui.py`)
  - Interface TUI pour confirmation partage
  - Affichage métriques composant
  - Confirmation interactive avant ajout Elite Library

- ✅ **PatternAnalyzer** (`Backend/Prod/sullivan/analyzer/pattern_analyzer.py`)
  - Analyse patterns dans Elite Library
  - Insights automatiques (fréquences, tendances, corrélations)

- ✅ **ContextualRecommender** (`Backend/Prod/sullivan/recommender/contextual_recommender.py`)
  - Recommandations contextuelles basées sur intent
  - Recherche sémantique via KnowledgeBase
  - Filtrage par catégorie
  - Tri par score Sullivan

- ✅ **KnowledgeBase** (`Backend/Prod/sullivan/knowledge/knowledge_base.py`)
  - Base de connaissances patterns HCI
  - Principes Fogg Behavior Model, Norman Affordances
  - Analytics et métriques

#### Cache et Stockage ✅
- ✅ **LocalCache** (`Backend/Prod/sullivan/cache/local_cache.py`)
  - Cache local par utilisateur (`~/.aetherflow/components/{user_id}/`)
  - Recherche par intent
  - Sauvegarde composants

- ✅ **Elite Library** (`Backend/Prod/sullivan/library/elite_library.py`)
  - Stockage composants validés (`components/elite/`)
  - Archivage automatique
  - Gestion expiration

### 5. Frontend Sullivan ✅ **OPÉRATIONNEL**

#### Interface HTML (`Frontend/`)
- ✅ **Chatbox interactive** : Interface web pour communiquer avec Sullivan
- ✅ **Toggle minimisé/overlay** : Barre minimisée en bas, overlay fullscreen
- ✅ **API intégrée** : Communication avec FastAPI backend
- ✅ **Gestion erreurs** : Messages clairs pour problèmes API
- ✅ `index.html`, `css/styles.css`, `js/app.js`
- ✅ Affichage scores et métriques, liste composants (Cache Local / Elite Library)

### 6. Portabilité ✅ **RÉCEMMENT COMPLÉTÉ**

#### Méthodes d'installation
- ✅ **Script universel** (`scripts/install.sh`) : Détection OS automatique
- ✅ **pip** (`pyproject.toml`) : Package Python installable
- ✅ **Docker** (`docker-compose.yml`) : Profils (cli, api, dev, prod)
- ✅ **DMG macOS** (`scripts/packaging/pyinstaller_mac.sh`) : Bundle autonome

#### Documentation
- ✅ **README.md** : Mis à jour avec toutes les méthodes d'installation
- ✅ **docs/01-getting-started/INSTALLATION.md** : Guide complet multi-plateforme
- ✅ **Dockerfile** : Multi-stage optimisé (< 500MB)

---

## 🔧 Composants Techniques

### Modèles de Données

#### Component (`Backend/Prod/sullivan/models/component.py`)
```python
class Component(BaseModel):
    name: str
    sullivan_score: float
    performance_score: int
    accessibility_score: int
    ecology_score: int
    popularity_score: int
    validation_score: int
    size_kb: int
    created_at: datetime
    user_id: str
    category: Optional[str]  # core, complex, domain
    last_used: Optional[datetime]
```

#### GlobalFunction (`Backend/Prod/sullivan/analyzer/backend_analyzer.py`)
```python
class GlobalFunction:
    product_type: str  # e-commerce, SaaS, dashboard, etc.
    actors: List[str]  # admin, client, vendeur, etc.
    business_flows: List[str]  # CRUD, Search, etc.
    use_cases: List[str]
```

### Structure des Outputs

Voir `docs/references/technique/REPERTOIRE_OUTPUTS_SULLIVAN.md` pour détails complets.

**Principaux répertoires** :
- `/tmp/sullivan_outputs/` : Outputs temporaires génération
- `/tmp/sullivan_plans/` : Plans JSON temporaires
- `~/.aetherflow/components/` : Cache local utilisateur
- `components/elite/` : Elite Library
- `output/{path}/sullivan_result.json` : Résultats DevMode
- `output/{path}/sullivan_designer_result.json` : Résultats DesignerMode

---

## 🔄 Workflows Disponibles

### AETHERFLOW Workflows

#### PROTO (`-q` / `--quick`)
```
FAST → DOUBLE-CHECK
```
- **Usage** : Prototypage rapide
- **Durée** : ~2-5 minutes
- **Qualité** : Bonne (validation basique)

#### PROD (`-f` / `--full`)
```
FAST → BUILD → DOUBLE-CHECK
```
- **Usage** : Qualité production
- **Durée** : ~5-15 minutes
- **Qualité** : Excellente (validation complète + guidelines)

### Sullivan Workflows

#### DevMode
```
Analyse Backend → Inférence Fonction Globale → 
Propose Structure Intention → Infère Corps → 
Infère Organes → Infère Molécules → Infère Atomes →
Génération Composants
```

#### DesignerMode
```
Upload Design → Analyse Visuelle → 
Extraction Structure → Mapping Logique →
Génération Composants
```

---

## 🌐 API et Interfaces

### Endpoints API

#### AETHERFLOW
- `POST /execute` : Exécute plan JSON
- `GET /health` : Health check

#### Sullivan Kernel
- `POST /sullivan/search` : Recherche composant par intent
- `GET /sullivan/components` : Liste composants disponibles
- `POST /sullivan/dev/analyze` : Analyse backend (DevMode)
- `POST /sullivan/designer/analyze` : Analyse design (DesignerMode)

### CLI

```bash
# Workflow PROTO
python -m Backend.Prod.cli -q --plan plan.json

# Workflow PROD
python -m Backend.Prod.cli -f --plan plan.json

# Mode mentor
python -m Backend.Prod.cli -f --plan plan.json --mentor
```

### Frontend Web

Chatbox Sullivan dans `Frontend/` : toggle minimisé/overlay, recherche et visualisation de composants, intégration API FastAPI.

---

## ⚠️ Points d'Amélioration Identifiés

### 1. Inférence Top-Down Sullivan ⚠️ **EN COURS**

**Problème** : Les résultats actuels montrent des structures génériques ("generic_organe", "generic_molecule") au lieu d'une inférence réelle depuis le backend.

**Cause** : L'inférence des intents depuis le code n'est pas encore complètement fonctionnelle.

**Impact** : Sullivan ne génère pas encore de frontend vraiment adapté au backend analysé.

**Priorité** : 🔴 **HAUTE**

### 2. Système STAR ❌ **NON IMPLÉMENTÉ**

**Contexte** : Document de référence créé pour la traduction d'intentions utilisateur.

**Besoin** : Implémenter la traduction d'intentions (Système STAR) pour enrichir l'inférence Sullivan.

**Priorité** : 🟡 **MOYENNE**

### 3. Génération Réelle de Composants ⚠️ **PARTIELLEMENT**

**État** : `ComponentGenerator` existe et fonctionne, mais les composants générés ne sont pas encore sauvegardés avec leur code HTML/CSS/JS.

**Besoin** : Sauvegarder les fichiers générés dans un format accessible.

**Priorité** : 🟡 **MOYENNE**

### 4. Frontend Homeos Studio ❌ **BASIQUE**

**État** : Interface HTML basique pour Sullivan existe, mais pas d'interface complète pour AETHERFLOW.

**Besoin** : Interface complète pour :
- Upload plans JSON
- Visualisation workflows
- Affichage code généré
- Métriques détaillées

**Priorité** : 🟡 **MOYENNE**

### 5. Système de Comptes ❌ **MANQUANT**

**Besoin** : Authentification utilisateurs, gestion sessions, quotas.

**Priorité** : 🟢 **BASSE** (pour beta interne)

### 6. Tests Automatisés ⚠️ **LIMITÉS**

**État** : Quelques tests unitaires, pas de suite complète.

**Besoin** : Tests unitaires, tests d'intégration, tests E2E.

**Priorité** : 🟡 **MOYENNE**

---

## 🗺️ Roadmap

### Phase 6 : Amélioration Inférence (EN COURS)

- [ ] Améliorer détection intents depuis code backend
- [ ] Affiner inférence fonction globale
- [ ] Générer structures frontend réellement adaptées (plus de "generic_*")
- [ ] Intégrer système STAR pour traduction intentions utilisateur
- [ ] Tests avec backends réels

### Phase 7 : Génération Complète

- [ ] Sauvegarder fichiers HTML/CSS/JS générés
- [ ] Créer fichiers de prévisualisation
- [ ] Intégration avec frontend web

### Phase 8 : Interface Complète

- [ ] Interface AETHERFLOW complète
- [ ] Upload plans JSON
- [ ] Visualisation workflows temps réel
- [ ] Export fichiers générés

### Phase 9 : Production Ready

- [ ] Système de comptes
- [ ] Gestion quotas
- [ ] Monitoring et analytics
- [ ] Documentation complète

### Phase 10 : Extensions Futures

- [ ] Mode Brainstorm
- [ ] Mode Deploy
- [ ] Intégration CI/CD
- [ ] Marketplace composants

---

## 📊 Métriques de Succès

### AETHERFLOW
- ✅ Taux de succès exécution plans : > 95%
- ✅ Temps moyen génération : < 10 minutes (PROD)
- ✅ Coût moyen par génération : < $0.50

### Sullivan Kernel
- ✅ Score moyen composants générés : > 75
- ✅ Taux composants Elite Library : > 20%
- ✅ Temps moyen génération composant : < 5 minutes

---

## 📝 Notes Techniques

### Stack Technique

- **Backend** : Python 3.9+, FastAPI, Pydantic
- **LLM Providers** : DeepSeek, Gemini, Groq, Codestral
- **Cache** : Cache sémantique, prompt cache
- **Frontend** : HTML/CSS/JS Vanilla (compatibilité Mac 2016)
- **Logging** : loguru
- **TUI** : Rich, Textual

### Dépendances Principales

- `fastapi` : API REST
- `pydantic` : Validation données
- `loguru` : Logging
- `rich` : TUI
- `textual` : TUI avancée
- Clients LLM (DeepSeek, Gemini, Groq, Codestral)

---

## 🔗 Références

- **PRD Sullivan (exclusif)** : `docs/02-sullivan/PRD_SULLIVAN.md`
- **Documentation complète** : `docs/guides/`
- **Résumé contexte** : `docs/01-getting-started/RESUME_CONTEXTE.md`
- **Répertoire outputs** : `docs/references/technique/REPERTOIRE_OUTPUTS_SULLIVAN.md`
- **Décomposition sémantique** : `docs/references/technique/Décomposition Sémantique (Comprendre l'intention)**.md`
- **Plan d'implémentation** : `.cursor/plans/sullivan_kernel_-_implémentation_complète_971ef366.plan.md`
- **Synthèse Sullivan** : `docs/guides/Synthèse Finale - AetherFlow 2.2 "Sullivan"**.md`

---

**Document généré automatiquement**  
**Dernière mise à jour** : 28 janvier 2026  
**Version** : 2.2 "Sullivan"
