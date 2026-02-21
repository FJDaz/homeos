# PRD - Homeos (AETHERFLOW) - État Actuel

**Version** : 2.3 "Genome"  
**Date** : 11 février 2026  
**Statut** : Beta S2 - Genome Viewer + Stenciler en développement

---

## 📋 Table des Matières

1. [Vision Produit](#vision-produit)
2. [Positionnement](#positionnement)
3. [Architecture Genome N0-N3](#architecture-genome-n0-n3)
4. [État Actuel - Fonctionnalités Implémentées](#état-actuel---fonctionnalités-implémentées)
5. [Sullivan Kernel - État d'Implémentation](#sullivan-kernel---état-dimplémentation)
6. [Composants Elite & Stratégie Hybride](#composants-elite--stratégie-hybride)
7. [Workflows Disponibles](#workflows-disponibles)
8. [Séparation des Rôles KIMI/Backend](#séparation-des-rôles-kimibackend)
9. [Points d'Amélioration Identifiés](#points-damélioration-identifiés)
10. [Roadmap](#roadmap)

---

## 🎯 Vision Produit

**Homeos** est une **agence de design numérique complète** automatisée par IA, structurée selon l'architecture biologique Genome (N0-N3) :

```
N0 Corps (Phases) → N1 Organes (Sections) → N2 Cellules (Features) → N3 Atomes (Composants)
     Brainstorm    →    Backend/Frontend   →    Upload/Layout      →    Button/Card/Form
```

**AETHERFLOW** est l'orchestrateur d'agents IA qui maintient l'homéostasie entre qualité, performance et maintenabilité.

### Valeur Proposée

- **Génération de code automatisée** : Backend Python/APIs et Frontend HTML/CSS/JS
- **Architecture Genome** : Structure hiérarchique biologique (Corps > Organes > Cellules > Atomes)
- **Qualité garantie** : Workflows structurés avec validation automatique et scoring Sullivan
- **Stratégie hybride** : Cache Elite (Tier 1/2/3) pour 0ms à <5s selon complexité
- **Intelligence contextuelle** : Analyse backend pour inférer frontend via UIInferenceEngine

---

## 🏢 Positionnement

### Homeos = Agence de Design Numérique

**Fonctions principales (4 Corps)** :
1. **Brainstorm** (N0) : Intent Refactoring, Arbitrage, Génome
2. **Backend** (N1) : Session Management, API, Distillation
3. **Frontend** (N1) : Navigation, Layout, Upload, Analyse, Dialogue, Validation, Adaptation
4. **Deploy** (N1) : Export, Finalisation

### AETHERFLOW = Orchestrateur d'Agents IA

**Rôle** : Coordonner l'exécution via workflows PROTO/PROD avec modèles LLM économiques.

### Sullivan Kernel = Intelligence Frontend

**Rôle** : Analyser backend, comprendre fonction globale métier, générer frontend adapté.

### KIMI = Chef Frontend

**Rôle** : 100% du rendu visuel (CSS, HTML, animations). Reçoit données du backend, ne reçoit jamais d'instructions de layout.

---

## 🧬 Architecture Genome N0-N3

```
┌─────────────────────────────────────────────────────────────┐
│                         N0 - CORPS                          │
│                    (4 Phases/Template)                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐ │
│  │ Brainstorm  │ │   Backend   │ │  Frontend   │ │ Deploy │ │
│  │   🟡 N0     │ │   🔵 N0     │ │   🟣 N0     │ │  🟢 N0 │ │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └───┬────┘ │
│         │               │               │            │      │
├─────────┴───────────────┴───────────────┴────────────┤      │
│                      N1 - ORGANES                        │      │
│                   (Sections Fonctionnelles)               │      │
├─────────────────────────────────────────────────────────┤      │
│  Brainstorm:          Backend:        Frontend:         │      │
│  - IR (N1)            - Session (N1)  - Navigation (N1) │      │
│  - Arbitrage (N1)     - Génome (N1)   - Layout (N1)     │      │
│                                       - Upload (N1)     │      │
│                                       - Analyse (N1)    │      │
│                                       - Dialogue (N1)   │      │
│                                       - Validation (N1) │      │
│                                       - Adaptation (N1) │      │
├─────────────────────────────────────────────────────────┤      │
│                      N2 - CELLULES                        │      │
│                      (Features/Modules)                   │      │
├─────────────────────────────────────────────────────────┤      │
│  Ex: Navigation → Stepper (N2), Breadcrumb (N2)         │      │
│  Ex: Layout → Grid (N2), Cards (N2)                     │      │
├─────────────────────────────────────────────────────────┤      │
│                      N3 - ATOMES                          │      │
│                   (Composants UI Primitifs)               │      │
├─────────────────────────────────────────────────────────┤      │
│  Button, Input, Card, Badge, Modal, Table, Form...      │      │
└─────────────────────────────────────────────────────────┘      │
```

### Genome Viewer (Port 9998)

- **Visualisation** : 4 Corps alignés avec collapses N0-N3
- **Wireframes** : Par niveau avec emojis et Wingdings3
- **Interactions** : Clic pour expand/collapse, checkboxes
- **Technos** : Python HTTP server, HTML/CSS vanilla, Fabric.js

### Stenciler (Intégration en cours)

- **Canvas Figma-like** : Drag & drop Corps, grille magnétique
- **Sidebar minimale** : Outils couleur/bordure/fond/supprimer
- **Lazy loading** : Tier 1/2/3 selon profondeur
- **Scroll automatique** : Au clic sur style/upload

---

## ✅ État Actuel - Fonctionnalités Implémentées

### 1. AETHERFLOW Core ✅ **COMPLET**

#### Orchestrator (`Backend/Prod/orchestrator.py`)
- ✅ Exécution plans JSON avec workflows PROTO/PROD
- ✅ Parallélisation étapes indépendantes
- ✅ Rate limiting par provider
- ✅ Métriques (temps, coûts, tokens)
- ✅ Cache sémantique et prompt cache

#### AgentRouter (`Backend/Prod/models/agent_router.py`)
- ✅ Routage intelligent (DeepSeek, Gemini, Groq, Codestral)
- ✅ "Smartest for least money"
- ✅ Fallback cascade Gemini

#### Workflows
- ✅ **ProtoWorkflow** : FAST → DOUBLE-CHECK
- ✅ **ProdWorkflow** : FAST → BUILD → DOUBLE-CHECK

### 2. API FastAPI ✅ **OPÉRATIONNELLE**

#### Endpoints Principaux (`Backend/Prod/api.py`)
- ✅ `POST /execute` : Exécute plan JSON
- ✅ `GET /health` : Health check
- ✅ `POST /sullivan/dev/analyze` : DevMode
- ✅ `POST /sullivan/designer/analyze` : DesignerMode
- ✅ `GET /sullivan/components` : Liste composants
- ✅ CORS activé, fichiers statiques

### 3. CLI ✅ **FONCTIONNEL**

```bash
python -m Backend.Prod.cli -q --plan plan.json    # PROTO
python -m Backend.Prod.cli -f --plan plan.json    # PROD
python -m Backend.Prod.cli -f --plan plan.json --mentor
```

### 4. Sullivan Kernel ✅ **PHASES 1-5 COMPLÈTES**

#### Phase 1 : Analyse Backend ✅
- ✅ **BackendAnalyzer** : Analyse structure, routes, modèles
- ✅ **UIInferenceEngine** : Inférence top-down (Intention → Corps → Organes → Molécules → Atomes)
- ✅ **DevMode** : Workflow "Collaboration Heureuse"

#### Phase 2 : Analyse Design ✅
- ✅ **DesignAnalyzer** : Analyse PNG/Figma
- ✅ **DesignerMode** : Workflow "Génération Miroir"

#### Phase 3 : Génération Composants ✅
- ✅ **ComponentGenerator** : Génération HTML/CSS/JS
- ✅ **ComponentRegistry** : Orchestration LocalCache → EliteLibrary

#### Phase 4 : Évaluation et Scoring ✅
- ✅ **SullivanScore** : Composite (Perf 30%, Access 30%, Éco 20%, Pop 10%, Val 10%)
- ✅ Seuil Elite Library : 85

#### Phase 5 : Fonctionnalités Avancées ✅
- ✅ **Elite Library** : Composants validés (score ≥ 85)
- ✅ **PatternAnalyzer** : Analyse patterns
- ✅ **ContextualRecommender** : Recommandations contextuelles
- ✅ **KnowledgeBase** : Patterns HCI (Fogg, Norman)

### 5. Genome & Composants ✅ **NOUVEAU**

#### Genome Viewer (`server_9998_v2.py`)
- ✅ Structure N0-N3 inférée
- ✅ 4 Corps avec wireframes par niveau
- ✅ Wingdings3 + emojis
- ✅ Collapses interactifs
- ✅ Sidebar avec stats

#### Stenciler (En développement)
- ✅ Architecture classes définie (voir `ARCHITECTURE_CLASSES_STENCILER.md`)
- ✅ Canvas Fabric.js
- ✅ Drag & drop Corps
- ✅ Sidebar outils (couleur, bordure, fond)
- ✅ Grille magnétique

### 6. Elite Components ✅ **66 COMPOSANTS**

Bibliothèque pré-générée dans `Backend/Prod/sullivan/library/elite_components/` :
- Atome_Carte_Layout.json
- Atome_Galerie_Layouts.json
- Atome_Resume_Genome.json
- ... (66 composants au total)

Scores : 85-95 (Sullivan Score)

---

## 🏆 Composants Elite & Stratégie Hybride

### Tier 1 : CORE LIBRARY (0ms)
```
[Atomes + Molécules de base] → Pré-générés, testés, optimisés
Usage : 60% des composants
Latence : 0ms (cache)
Qualité : ✅✅✅✅✅ (Elite Library)
```

### Tier 2 : PATTERN LIBRARY (< 100ms)
```
[Organismes courants] → Pré-générés, légèrement adaptables
Usage : 30% des composants
Latence : < 100ms (adaptation)
Qualité : ✅✅✅✅ (Score > 85)
```

### Tier 3 : CUSTOM GENERATION (1-5s)
```
[Composants uniques] → Générés à la volée
Usage : 10% des composants
Latence : 1-5s (génération complète)
Qualité : ✅✅✅ (Dépend du contexte)
```

### Fichier Genome
- **Source** : `docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/genome_inferred_kimi_innocent_v2.json`
- **Structure** : 4 N0 Phases → 10 N1 Sections → 14 N2 Features → 32 N3 Components
- **Confiance globale** : 85%

---

## 🔄 Workflows Disponibles

### AETHERFLOW

#### PROTO (`-q` / `--quick`)
```
FAST → DOUBLE-CHECK
Durée : ~2-5 minutes
Qualité : Bonne
```

#### PROD (`-f` / `--full`)
```
FAST → BUILD → DOUBLE-CHECK
Durée : ~5-15 minutes
Qualité : Excellente
```

### Sullivan

#### DevMode
```
Analyse Backend → Inférence Fonction Globale → 
Propose Structure → Infère Corps → Infère Organes → 
Infère Molécules → Infère Atomes → Génération
```

#### DesignerMode
```
Upload Design → Analyse Visuelle → 
Extraction Structure → Mapping Logique → Génération
```

---

## 👥 Séparation des Rôles KIMI/Backend

### Territoire KIMI (SANCTUAIRE)
- ✅ HTML sémantique
- ✅ CSS / Tailwind / Variables
- ✅ Layout (flex, grid, position)
- ✅ Animations et transitions
- ✅ Responsive et breakpoints
- ✅ Typographie (polices, tailles)

### Territoire Backend (Python)
- ✅ Logique métier (Corps/Organe/Cellule/Atome)
- ✅ Données JSON pures
- ✅ Suggestions de composants (IDs)
- ✅ Attributs sémantiques (`layout_type: "grid"`)
- ✅ Actions possibles (`can_be_colored: true`)
- ✅ Cache et persistance

### Interface Contract
```python
# Backend fournit
data = {
    "id": "n0_frontend",
    "name": "Frontend",
    "color": "#ec4899",  # Thématique, pas CSS
    "organes": [...],
    "tier": 1
}

# KIMI traduit en CSS
.style-frontend {
    border-left: 4px solid #ec4899;
}
```

---

## ⚠️ Points d'Amélioration Identifiés

### 1. Intégration Stenciler 🔴 **HAUTE PRIORITÉ**
**État** : Architecture définie, implémentation en cours  
**Besoin** : Fusionner Genome Viewer + Stenciler sur même page  
**Approche** : Extension verticale (pas fusion)

### 2. Classes Abstraction Métier 🟡 **EN COURS**
**Document** : `docs/02-sullivan/Analyses/ARCHITECTURE_CLASSES_STENCILER.md`  
**Classes** : CorpsEntity, ModificationLog, ComponentContextEngine, DrillDownManager, PNGSemanticAnalyzer, ToolRegistry  
**Status** : En attente implémentation Python

### 3. Persistance Modifications 🟡 **À IMPLÉMENTER**
**Besoin** : JSON Modifs, localStorage, éventuellement SQLite  
**Format** : Event sourcing light (journal des changements)

### 4. Analyse PNG Sémantique 🟡 **À IMPLÉMENTER**
**Besoin** : Gemini Vision → Attributs sémantiques (pas CSS)  
**Output** : `{layout_type: "grid", dominant_colors: [...], zones: [...]}`

### 5. Système de Comptes 🟢 **BASSE**
**Besoin** : Auth, sessions, quotas  
**Priorité** : Post-beta interne

---

## 🗺️ Roadmap

### Phase 6 : Stenciler & Classes (EN COURS - Février 2026)
- [x] Architecture classes définie
- [ ] Implémentation CorpsEntity + ModificationLog
- [ ] Implémentation ComponentContextEngine
- [ ] Intégration Stenciler dans Viewer 9998
- [ ] Tests drag & drop Canvas

### Phase 7 : Analyse & Contexte (Mars 2026)
- [ ] PNGSemanticAnalyzer (Gemini Vision)
- [ ] Traduction PNG → Attributs sémantiques
- [ ] KIMI : Traduction attributs → CSS
- [ ] Tests workflows upload + analyse

### Phase 8 : Persistance & Export (Avril 2026)
- [ ] JSON Modifs temps réel
- [ ] LocalStorage / SQLite
- [ ] Export final (zip, git)
- [ ] Intégration Deploy

### Phase 9 : Production (Mai-Juin 2026)
- [ ] Système de comptes
- [ ] Monitoring et analytics
- [ ] Documentation complète
- [ ] Marketplace composants

---

## 📊 Métriques de Succès

### AETHERFLOW
- ✅ Taux de succès exécution plans : > 95%
- ✅ Temps moyen génération PROD : < 10 minutes
- ✅ Coût moyen par génération : < $0.50

### Sullivan Kernel
- ✅ Score moyen composants : > 75
- ✅ Taux Elite Library : > 20%
- ✅ Temps génération composant : < 5 minutes

### Genome/Stenciler
- 🎯 Latence Tier 1 : 0ms
- 🎯 Latence Tier 2 : < 100ms
- 🎯 Latence Tier 3 : < 5s

---

## 📝 Notes Techniques

### Stack
- **Backend** : Python 3.9+, FastAPI, Pydantic
- **LLM** : DeepSeek, Gemini, Groq, Codestral
- **Frontend** : HTML/CSS Vanilla, Fabric.js, HTMX
- **Cache** : Cache sémantique, prompt cache

### Fichiers Clés
- **Genome** : `docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/genome_inferred_kimi_innocent_v2.json`
- **Viewer** : `server_9998_v2.py` (port 9998)
- **Architecture** : `docs/02-sullivan/Analyses/ARCHITECTURE_CLASSES_STENCILER.md`
- **Mission** : `docs/02-sullivan/mailbox/kimi/MISSION_STENCILER_EXTENSION.md`

---

## 🔗 Références

- **Architecture Classes** : `docs/02-sullivan/Analyses/ARCHITECTURE_CLASSES_STENCILER.md`
- **Mission Stenciler** : `docs/02-sullivan/mailbox/kimi/MISSION_STENCILER_EXTENSION.md`
- **Genome** : `docs/02-sullivan/Genome_Enrichi/`
- **Stratégie Hybride** : `docs/02-sullivan/Composants/STRATEGIE HYBRIDES DE PREGENRATION DES COMPOSANTS.md`
- **PRD Sullivan** : `docs/02-sullivan/PRD_SULLIVAN.md`

---

**Document mis à jour** : 11 février 2026  
**Version** : 2.3 "Genome"  
**Prochaine milestone** : Intégration Stenciler + Classes Abstraction
