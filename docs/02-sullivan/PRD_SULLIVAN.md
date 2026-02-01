# PRD - Sullivan Kernel

**Version** : 2.2 "Sullivan"  
**Date** : 28 janvier 2026  
**Statut** : Beta S1 - En développement actif  
**Périmètre** : Ce PRD couvre **exclusivement** le Sullivan Kernel. AETHERFLOW (orchestrateur, workflows PROTO/PROD, CLI), Homeos et la production sont hors scope.

---

## 📋 Table des Matières

1. [Vision et Rôle](#vision-et-rôle)
2. [Architecture Sullivan](#architecture-sullivan)
3. [État Actuel - Phases 1 à 5](#état-actuel---phases-1-à-5)
4. [Workflows Sullivan](#workflows-sullivan)
5. [Composants Techniques](#composants-techniques)
6. [API et Frontend](#api-et-frontend)
7. [Points d'Amélioration](#points-damélioration)
8. [Roadmap Sullivan](#roadmap-sullivan)
9. [Métriques et Concepts](#métriques-et-concepts)
10. [Références](#références)

---

## 🎯 Vision et Rôle

**Sullivan** est l’**intelligence frontend** qui analyse un backend existant, en infère la fonction globale métier, et génère le frontend correspondant (HTML/CSS/JS) de manière structurée et évaluée.

### Valeur proposée

- **Analyse backend** : Routes API, modèles de données, intents → fonction globale (type produit, acteurs, flux).
- **Inférence top-down** : Intention → Corps → Organes → Molécules → Atomes (Atomic Design).
- **Génération de composants** : HTML/CSS/JS via plans JSON exécutés par l’orchestrateur (AETHERFLOW).
- **Qualité mesurée** : SullivanScore (Performance, Accessibilité, Écologie, Popularité, Validation), Elite Library.

### Dépendance externe

Sullivan s’appuie sur **AETHERFLOW** pour la génération de code (exécution de plans, appel LLM). Il n’orchestre pas lui‑même les workflows PROTO/PROD ; il les utilise via `ComponentGenerator` et `ValidationEvaluator`.

---

## 🏗️ Architecture Sullivan

```
                    Backend (cible)
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                     Sullivan Kernel                               │
├──────────────────────────────────────────────────────────────────┤
│  analyzer/          BackendAnalyzer, DesignAnalyzer,              │
│                     UIInferenceEngine, PatternAnalyzer            │
│  modes/             DevMode, DesignerMode                         │
│  generator/         ComponentGenerator                            │
│  registry           ComponentRegistry (LocalCache → Elite → Gen)  │
│  evaluators/        Performance, Accessibility, Validation        │
│  models/            Component, SullivanScore, categories          │
│  library/           Elite Library, SharingTUI                     │
│  knowledge/         KnowledgeBase                                 │
│  recommender/       ContextualRecommender                         │
└──────────────────────────────────────────────────────────────────┘
                           │
                           ▼
              Composants HTML/CSS/JS / Elite Library
```

**Flux principaux** : Analyse → Inférence → Génération → Évaluation → Stockage (LocalCache / Elite Library).

---

## ✅ État Actuel - Phases 1 à 5

### Phase 1 : Analyse Backend ✅

| Composant | Fichier | Description |
|-----------|---------|-------------|
| **BackendAnalyzer** | `sullivan/analyzer/backend_analyzer.py` | Structure projet, routes API (FastAPI/Flask), modèles (Pydantic/SQLAlchemy), intents, fonction globale (type produit, acteurs, flux) |
| **UIInferenceEngine** | `sullivan/analyzer/ui_inference_engine.py` | Inférence UI top-down : Intention → Corps → Organes → Molécules → Atomes |
| **DevMode** | `sullivan/modes/dev_mode.py` | Workflow « Collaboration Heureuse » : analyse → inférence → génération ; dialogue stratégique, HCI Mentor |

### Phase 2 : Analyse Design ✅

| Composant | Fichier | Description |
|-----------|---------|-------------|
| **DesignAnalyzer** | `sullivan/analyzer/design_analyzer.py` | Designs PNG/Figma/Sketch → structure visuelle → mapping logique |
| **DesignerMode** | `sullivan/modes/designer_mode.py` | Workflow « Génération Miroir » : design → structure → génération frontend |

### Phase 3 : Génération Composants ✅

| Composant | Fichier | Description |
|-----------|---------|-------------|
| **ComponentGenerator** | `sullivan/generator/component_generator.py` | Génération HTML/CSS/JS via AETHERFLOW (plans JSON, PROTO/PROD), parsing outputs, métadonnées |
| **ComponentRegistry** | `sullivan/registry.py` | LocalCache → Elite Library → Génération ; recherche par intent, génération si absent, évaluation après génération |

### Phase 4 : Évaluation et Scoring ✅

| Composant | Fichier | Description |
|-----------|---------|-------------|
| **PerformanceEvaluator** | `sullivan/evaluators/performance_evaluator.py` | Lighthouse CI → score Performance (0–100) |
| **AccessibilityEvaluator** | `sullivan/evaluators/accessibility_evaluator.py` | axe-core / WCAG → score Accessibilité (0–100) |
| **ValidationEvaluator** | `sullivan/evaluators/validation_evaluator.py` | AETHERFLOW DOUBLE-CHECK (TDD, DRY, SOLID) → score Validation (0–100) |
| **SullivanScore** | `sullivan/models/sullivan_score.py` | Composite : Performance 30%, Accessibilité 30%, Écologie 20%, Popularité 10%, Validation 10% ; seuil Elite = 85 |

### Phase 5 : Fonctionnalités avancées ✅

| Composant | Fichier | Description |
|-----------|---------|-------------|
| **Catégorisation** | `sullivan/models/categories.py` | core / complex / domain (taille KB) |
| **Elite Library** | `sullivan/library/elite_library.py` | Composants score ≥ 85 ; archivage > 6 mois ; retrait si &lt; 85 ; `last_used` |
| **SharingTUI** | `sullivan/library/sharing_tui.py` | TUI confirmation partage, métriques, ajout Elite |
| **PatternAnalyzer** | `sullivan/analyzer/pattern_analyzer.py` | Patterns Elite Library, insights (fréquences, tendances) |
| **ContextualRecommender** | `sullivan/recommender/contextual_recommender.py` | Recommandations par intent, KnowledgeBase, catégorie, score |
| **KnowledgeBase** | `sullivan/knowledge/knowledge_base.py` | Patterns HCI (Fogg, Norman, etc.), analytics |

#### Cache et stockage ✅

- **LocalCache** : `~/.aetherflow/components/{user_id}/` — recherche par intent, sauvegarde.
- **Elite Library** : `components/elite/` — archivage, expiration.

---

## 🔄 Workflows Sullivan

### DevMode — « Collaboration Heureuse »

```
Analyse Backend → Inférence Fonction Globale →
Structure Intention → Corps → Organes → Molécules → Atomes →
Génération Composants
```

### DesignerMode — « Génération Miroir »

```
Upload Design → Analyse Visuelle →
Extraction Structure → Mapping Logique →
Génération Composants
```

---

## 🔧 Composants Techniques

### Modèles

**Component** (`sullivan/models/component.py`)  
`name`, `sullivan_score`, `performance_score`, `accessibility_score`, `ecology_score`, `popularity_score`, `validation_score`, `size_kb`, `created_at`, `user_id`, `category`, `last_used`.

**GlobalFunction** (`backend_analyzer`)  
`product_type`, `actors`, `business_flows`, `use_cases`.

### Structure des outputs

Voir `docs/references/technique/REPERTOIRE_OUTPUTS_SULLIVAN.md`.

| Répertoire / Fichier | Usage |
|----------------------|--------|
| `/tmp/sullivan_outputs/` | Outputs temporaires génération |
| `/tmp/sullivan_plans/` | Plans JSON temporaires |
| `~/.aetherflow/components/` | Cache local utilisateur |
| `components/elite/` | Elite Library |
| `output/{path}/sullivan_result.json` | Résultats DevMode |
| `output/{path}/sullivan_designer_result.json` | Résultats DesignerMode |

---

## 🌐 API et Frontend

### Endpoints (Sullivan uniquement)

- `POST /sullivan/search` — Recherche composant par intent  
- `GET /sullivan/components` — Liste composants  
- `POST /sullivan/dev/analyze` — Analyse backend (DevMode)  
- `POST /sullivan/designer/analyze` — Analyse design (DesignerMode)  

Exposés via l’API FastAPI du projet ; CORS et fichiers statiques pour le frontend.

### Frontend Sullivan ✅ OPÉRATIONNEL

- **Chatbox** : interface web pour interagir avec Sullivan  
- **Toggle minimisé / overlay** : barre en bas, overlay fullscreen  
- **API** : communication FastAPI  
- **Erreurs** : messages explicites  
- Fichiers : `Frontend/index.html`, `css/`, `js/` — scores, métriques, liste composants (Cache Local / Elite).

---

## ⚠️ Points d'Amélioration

### 1. Inférence top-down ⚠️ EN COURS — Priorité 🔴 HAUTE

**Problème** : Structures génériques (« generic_organe », « generic_molecule ») au lieu d’une inférence réelle depuis le backend.

**Impact** : Frontend généré peu adapté au backend analysé.

### 2. Système STAR ❌ NON IMPLÉMENTÉ — Priorité 🟡 MOYENNE

**Contexte** : Doc de référence pour la traduction d’intentions utilisateur.  
**Besoin** : Implémenter la traduction d’intentions (STAR) pour enrichir l’inférence.

### 3. Sauvegarde des composants générés ⚠️ PARTIEL — Priorité 🟡 MOYENNE

**État** : Génération OK, fichiers souvent en temporaire.  
**Besoin** : Sauvegarder HTML/CSS/JS dans un format exploitable (ex. Elite Library, exports).

---

## 🗺️ Roadmap Sullivan

### Phase 6 : Amélioration inférence (en cours)

- [ ] Détection intents depuis le code backend
- [ ] Inférence fonction globale affinée
- [ ] Structures frontend réelles (fin des « generic_* »)
- [ ] Intégration système STAR (traduction intentions)
- [ ] Tests sur backends réels

### Phase 7 : Génération complète

- [ ] Sauvegarde systématique HTML/CSS/JS générés
- [ ] Prévisualisation des composants
- [ ] Intégration Elite Library / frontend web

### Orientations ultérieures (hors scope PRD actuel)

- Interface enrichie (Studio), visualisation workflows, export — à traiter dans un PRD « produit » dédié.

---

## 📊 Métriques et Concepts

### Métriques Sullivan

- Score moyen composants générés **> 75**
- Taux composants Elite Library **> 20 %**
- Temps moyen génération composant **< 5 min**

### Atomic Design (top-down)

```
Intention (Niveau 0) → Corps → Organes → Molécules → Atomes
```

### SullivanScore

- **Performance** 30 % (Lighthouse)  
- **Accessibilité** 30 % (WCAG)  
- **Écologie** 20 %  
- **Popularité** 10 %  
- **Validation** 10 % (TDD, DRY, SOLID)  

---

## 🔗 Références

- **Répertoire outputs** : `docs/references/technique/REPERTOIRE_OUTPUTS_SULLIVAN.md`
- **Décomposition sémantique** : `docs/references/technique/Décomposition Sémantique (Comprendre l'intention)**.md`
- **Résumé contexte** : `docs/01-getting-started/RESUME_CONTEXTE.md`
- **PRD produit (Homeos)** : `docs/04-homeos/PRD_HOMEOS.md`, `docs/04-homeos/PRD_HOMEOS_ETAT_ACTUEL.md`
- **Synthèse Sullivan** : `docs/guides/Synthèse Finale - AetherFlow 2.2 "Sullivan"**.md`
- **Addendum PRD Sullivan (ajouts récents)** : `docs/02-sullivan/PRD_SULLIVAN_ADDENDUM.md` — pipeline « template → écrans câblés », Genome, Studio, Chatbot, CLI/API, sorties Studio, corrections.

---

**Dernière mise à jour** : 28 janvier 2026  
**Version** : 2.2 "Sullivan"
