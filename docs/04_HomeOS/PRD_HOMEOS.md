# PRD — HOMEOS (AETHERFLOW)

**Product Requirements Document — Plateforme d’homéostasie du code**

| Attribut | Valeur |
|----------|--------|
| **Version** | 2.2 "Sullivan" |
| **Date** | 30 janvier 2026 |
| **Statut** | Beta S1 — Développement actif |
| **Nom commercial** | Homeos |
| **Nom technique** | AETHERFLOW |

---

## Table des matières

1. [Aperçu et vision](#1-aperçu-et-vision)
2. [Problème et solution](#2-problème-et-solution)
3. [Public cible et objectifs](#3-public-cible-et-objectifs)
4. [Architecture globale](#4-architecture-globale)
5. [Périmètre fonctionnel (scope)](#5-périmètre-fonctionnel-scope)
6. [Sullivan Kernel et workflow idéal](#6-sullivan-kernel-et-workflow-idéal)
7. [Genome et Studio](#7-genome-et-studio)
8. [API, CLI et interfaces](#8-api-cli-et-interfaces)
9. [Modèles de données et sorties](#9-modèles-de-données-et-sorties)
10. [Exigences non fonctionnelles](#10-exigences-non-fonctionnelles)
11. [Roadmap et priorités](#11-roadmap-et-priorités)
12. [Glossaire et références](#12-glossaire-et-références)

---

## 1. Aperçu et vision

### 1.1 Vision produit

**Homeos** est une **agence de design numérique automatisée par IA** qui accompagne les utilisateurs de la conception à la mise en production :

```
Brainstorm → Backend → Frontend → Deploy
```

**AETHERFLOW** (nom interne du code) est l’orchestrateur d’agents IA qui génère du code de qualité en maintenant un équilibre **homéostatique** entre qualité, performance et maintenabilité.

### 1.2 Proposition de valeur

- **Génération de code automatisée** : Backend (Python/APIs) et frontend (HTML/CSS/JS) à partir de plans, de designs ou du genome.
- **Qualité structurée** : Workflows PROTO/PROD avec validation (DOUBLE-CHECK) et guidelines (TDD, DRY, SOLID).
- **Coûts maîtrisés** : Utilisation de LLM économiques (DeepSeek, Gemini, Groq, Codestral) ; pas de dépendance à Claude API pour l’exécution.
- **Intelligence contextuelle** : Analyse du backend (Genome), du design (template), inférence UI (Intention → Corps → Organes → Molécules → Atomes).

### 1.3 Rôles des briques

| Brique | Rôle |
|--------|------|
| **Claude Code (Cursor)** | Architecte : génère les plans, orchestre, valide les résultats. |
| **AETHERFLOW** | Exécuteur : exécute les plans JSON via workflows (PROTO/PROD/VerifyFix). |
| **Sullivan Kernel** | Intelligence frontend : analyse backend/design, genome, plan d’écrans, génération de corps et dialogue (chatbot). |
| **LLM (DeepSeek, Gemini, Groq, Codestral)** | Génération de code et d’analyses selon le routage AETHERFLOW. |

---

## 2. Problème et solution

### 2.1 Problème utilisateur

- Code généré par IA souvent peu maintenable, peu optimisé, peu accessible.
- Temps passé à corriger/ajuster le code généré.
- Manque d’outils pédagogiques pour enseigner les bonnes pratiques (performance, accessibilité, sobriété).

### 2.2 Problème technique / business

- Dépendance à Cursor Pro et Claude API pour une exécution complète.
- Coûts et risque géopolitique d’une dépendance exclusive à des LLM US.

### 2.3 Solution HOMEOS

1. **Orchestration portable** : Plans JSON exécutés par AETHERFLOW avec des LLM multiples (DeepSeek, Gemini, Groq, Codestral) — pas d’exécution dépendante de Claude API.
2. **Sullivan Kernel** : Analyse backend (Genome), design (template), plan d’écrans (screen_plan), génération de corps (écrans) et chatbot pour l’affinage.
3. **Studio & API** : Interface (Studio) et API FastAPI pour exposer genome, plans, exécution et endpoints Sullivan.

---

## 3. Public cible et objectifs

### 3.1 Public cible

- **Enseignants** (DNMADE, NSI, BUT MMI) : formation aux bonnes pratiques.
- **Étudiants** : apprentissage et prototypage rapide.
- **Développeurs indépendants** : gain de temps sur le frontend.
- **Établissements** : outil éthique et performant en environnement contrôlé.

### 3.2 Objectifs

- **Court terme** : Atteindre 100 utilisateurs payants en 6 mois ; stabiliser le workflow Sullivan (template → écrans câblés).
- **Moyen terme** : Devenir une référence pour l’enseignement du front-end en France.
- **Long terme** : Extension internationale et à d’autres domaines (back-end, mobile, Deploy).

---

## 4. Architecture globale

### 4.1 Schéma

```
┌─────────────────────────────────────────────────────────────────┐
│                    Claude Code (Cursor)                          │
│              Architecte & Orchestrateur principal                │
└────────────────────────────┬────────────────────────────────────┘
                              │ plan.json, commandes CLI
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AETHERFLOW (Backend)                        │
├─────────────────────────────────────────────────────────────────┤
│  Orchestrator │ AgentRouter │ Workflows (PROTO/PROD/VerifyFix)   │
│  Plan Reader  │ RAG / Cache sémantique / Prompt cache            │
└────────────────────────────┬────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ Genome       │    │ Sullivan Kernel  │    │ API FastAPI       │
│ Generator    │    │                  │    │                   │
│ (OpenAPI →   │    │ • BackendAnalyzer│    │ /execute, /health │
│  genome JSON)│    │ • DesignAnalyzer │    │ /studio/genome    │
└──────────────┘    │ • DesignerMode    │    │ /sullivan/*       │
                    │ • ScreenPlanner  │    │ / (Studio HTML)   │
                    │ • CorpsGenerator │    └──────────────────┘
                    │ • Sullivan       │
                    │   Chatbot        │
                    └──────────────────┘
                              │
                              ▼
                    LLM (DeepSeek, Gemini, Groq, Codestral)
```

### 4.2 Séparation des responsabilités

- **Claude Code** : Génère les plans, orchestre l’exécution, valide les résultats ; pas d’exécution LLM directe pour le code Sullivan.
- **AETHERFLOW** : Exécute les plans via workflows ; routage LLM ; métriques et cache.
- **Sullivan Kernel** : Lecture genome, analyse design, plan d’écrans, génération de corps, chatbot ; toute inférence layout/code passe par AETHERFLOW (plans + workflows).
- **API** : Exposition du genome, exécution de plans, endpoints Sullivan (search, components, dev/designer analyze, corps/organes, chatbot).

---

## 5. Périmètre fonctionnel (scope)

### 5.1 In scope (v2.2)

- Exécution de plans JSON (workflows PROTO, PROD, VerifyFix).
- Génération du **Genome** à partir de l’OpenAPI de l’API (`homeos_genome.json`).
- **Sullivan** : analyse backend (DevMode), analyse design (DesignerMode), extraction de principes graphiques, template → HTML (Phase 1), plan d’écrans (genome → screen_plan.json), génération de corps (screen_plan + principes → HTML), chatbot (organes par corps, affinage).
- **Studio** : page d’accueil servie à `/` (studio_index.html), organes (Execute Plan, Health, Get Studio Genome, Search Component, etc.), appels API.
- API FastAPI : `/execute`, `/health`, `/studio/genome`, `/sullivan/*` (search, components, dev/designer analyze, corps/organes, chatbot).
- CLI : `aetherflow -q/-f/-vfx --plan`, `sullivan read-genome`, `sullivan plan-screens`, `sullivan build`, `sullivan designer`, etc.
- Cache sémantique, prompt cache, RAG pour enrichissement de contexte.
- Portabilité : script d’installation, pip, Docker, DMG macOS.

### 5.2 Out of scope (v2.2)

- Mode **Brainstorm** (génération d’idées) — prévu roadmap.
- Mode **Deploy** (déploiement automatisé) — prévu roadmap.
- Système de comptes / authentification / quotas — prévu roadmap.
- Interface complète AETHERFLOW (upload de plans, visualisation workflows temps réel) — partiellement couvert par le Studio actuel.

---

## 6. Sullivan Kernel et workflow idéal

### 6.1 Workflow cible (template → écrans câblés)

1. **Image (template)** → analyse designer → **génération HTML** à partir du design (single-file).
2. **Principes graphiques** : extraction depuis le template (couleurs, typo, espacements) → `design_principles.json`.
3. **Câblage backend** : Genome (OpenAPI) → `homeos_genome.json`.
4. **Plan d’écrans** : Genome → **ScreenPlanner** → `screen_plan.json` (liste de corps avec organes, endpoints).
5. **Génération des corps** : screen_plan + design_principles → squelette HTML par corps (sections ancrées, single-page).
6. **Corps 1 (écran 1)** : proposition des **organes** depuis le plan ; **chatbot Sullivan** (z-index 10) pour affinage des cellules (molécules).
7. **Boucle** : addendum graphique → questions Sullivan → affinage → passage au corps suivant, etc.

### 6.2 Phases Sullivan implémentées

| Phase | Objectif | Composant / sortie | État |
|-------|----------|--------------------|------|
| **Phase 1** | Template → HTML (design seul) | DesignerMode + design_to_html → `studio_index.html` | Implémenté |
| **Phase 2** | Principes graphiques depuis template | DesignPrinciplesExtractor → `design_principles.json` | Implémenté |
| **Phase 3** | Genome → plan d’écrans | ScreenPlanner → `screen_plan.json` | Implémenté |
| **Phase 4** | Plan + principes → corps (HTML) | CorpsGenerator → `studio_corps.html` | Implémenté |
| **Phase 5** | Corps 1 + organes + chatbot | Sullivan Chatbot, GET `/sullivan/corps/{id}/organes`, page chatbot | Implémenté |

### 6.3 Modes Sullivan

- **DevMode** : Analyse backend → inférence fonction globale → proposition structure (Intention → Corps → Organes → Molécules → Atomes) → génération.
- **DesignerMode** : Upload design (image) → analyse visuelle → extraction structure + optionnel principes + optionnel HTML (Phase 1).
- **ScreenPlanner** : Genome → liste de corps (écrans) avec organes et endpoints.
- **CorpsGenerator** : screen_plan + design_principles → HTML des corps.
- **Chatbot** : dialogue pour affinage par écran (organes, cellules) ; appels Gemini via backend.

### 6.4 Références webdesign Sullivan

Les tendances utilisées pour interpréter les templates sont décrites dans `docs/02-sullivan/Références webdesign de Sullivan.md` (Gumroad, Linear, Tally, Vercel, iA.net, Family, Stripe, Berkshire Hathaway).

---

## 7. Genome et Studio

### 7.1 Genome

- **Définition** : Représentation structurée de l’API (metadata, topology, endpoints, schémas) dérivée de l’OpenAPI.
- **Génération** : `Backend/Prod/core/genome_generator.py` ; entrée = OpenAPI de l’API.
- **Sortie** : `output/studio/homeos_genome.json` (ou chemin configurable).
- **Exposition** : `GET /studio/genome` ; si le fichier n’existe pas, l’API peut le générer à la volée.

### 7.2 Studio

- **Page d’accueil** : Servie à `GET /` depuis `output/studio/studio_index.html` (ou fallback Svelte/Frontend).
- **Contenu** : Sidebar (Pipeline : Brainstorm, Back, Front, Deploy), organes dynamiques (Execute Plan, Health, Get Studio Genome, Search Component, List Components, Sullivan Dev/Designer Analyze, Preview, etc.) avec boutons Fetch/Execute et zones d’affichage.
- **Base URL** : `http://localhost:8000` (ou `0.0.0.0:8000` pour exposition réseau).
- **Fichiers clés** : `output/studio/studio_index.html`, `homeos_genome.json`, `screen_plan.json`, `design_principles.json`, `studio_corps.html`, `studio_corps1_chatbot.html`.

### 7.3 Règle d’or

- **Inférence** (layout à partir du genome, génération de code) : **AETHERFLOW** (plans + workflows).
- **Amendement / dialogue** : **Chatbot** (frontend) → API Sullivan.
- **Review / correction manuelle** : Utilisateur ou Claude en direct dans l’IDE — pas d’inférence “sauvage” hors AETHERFLOW.

---

## 8. API, CLI et interfaces

### 8.1 API FastAPI

- **Démarrage** : `./start_api.sh` ou `python -m Backend.Prod.api` ; host `0.0.0.0`, port `8000`.
- **Endpoints principaux** :
  - `POST /execute` : Exécution d’un plan JSON.
  - `GET /health` : Health check.
  - `GET /` : Page d’accueil Studio (studio_index.html ou fallbacks).
  - `GET /studio/genome` : Genome JSON.
  - `POST /sullivan/search` : Recherche de composants.
  - `GET /sullivan/components` : Liste des composants.
  - `POST /sullivan/dev/analyze` : Analyse backend (DevMode).
  - `POST /sullivan/designer/analyze` : Analyse design (DesignerMode).
  - `POST /sullivan/designer/upload` : Upload fichier design.
  - `GET /sullivan/corps/{corps_id}/organes` : Organes pour un corps (depuis screen_plan).
  - `POST /sullivan/chatbot` : Message vers le chatbot Sullivan.
  - `GET /sullivan/preview`, `GET /sullivan/preview/{component_id}`, etc. : Prévisualisation composants.

### 8.2 CLI

- **Workflows** :
  - `./run_aetherflow.sh -q --plan <plan.json>` : PROTO (rapide).
  - `./run_aetherflow.sh -f --plan <plan.json>` : PROD (qualité).
  - `./run_aetherflow.sh -vfx --plan <plan.json>` : VerifyFix (exécution + validation + corrections).
- **Genome** : `aetherflow genome` (ou équivalent) → génération `homeos_genome.json`.
- **Sullivan** :
  - `aetherflow sullivan read-genome` : Lecture et affichage du genome.
  - `aetherflow sullivan plan-screens --genome output/studio/homeos_genome.json --output output/studio/screen_plan.json` : Plan d’écrans.
  - `aetherflow sullivan build` : Build genome → studio_index.html.
  - `aetherflow sullivan designer --design <image>` : DesignerMode (analyse + optionnel principes + optionnel HTML).

### 8.3 Frontend

- **Studio** : Single-page dans `output/studio/studio_index.html`, organes câblés sur l’API.
- **Frontend legacy** : `Frontend/` (index.html, studio.html, css/, js/) pour chatbox et studio genome.
- **Svelte** : `frontend-svelte/` (build possible) ; servi si présent et si studio_index n’existe pas.

---

## 9. Modèles de données et sorties

### 9.1 Genome (`homeos_genome.json`)

- Metadata, topology, liste d’endpoints (path, method, x_ui_hint, etc.), schema_definitions.

### 9.2 Screen plan (`screen_plan.json`)

- Liste de corps (écrans) : `id`, `label`, `organes`, `endpoints`, etc.

### 9.3 Design principles (`design_principles.json`)

- Design tokens : couleurs, typo, espacements, border_radius, etc.

### 9.4 Composants Sullivan

- **Component** : name, sullivan_score, performance/accessibility/ecology/popularity/validation scores, size_kb, user_id, category, etc.
- **LocalCache** : `~/.aetherflow/components/{user_id}/`.
- **Elite Library** : composants avec score ≥ 85.

### 9.5 Répertoires de sortie

- `output/studio/` : genome, screen_plan, design_principles, studio_index.html, studio_corps.html, studio_corps1_chatbot.html, static/.
- `output/build/`, `output/validation/` : step_outputs, métriques (JSON/CSV).
- Voir `docs/references/technique/REPERTOIRE_OUTPUTS_SULLIVAN.md` pour l’inventaire détaillé.

---

## 10. Exigences non fonctionnelles

### 10.1 Performance

- Exécution PROTO : ordre de grandeur 2–5 min selon plan.
- Exécution PROD : 5–15 min.
- VerifyFix : exécution + validation ; objectif succès sans erreur lorsque le plan et le code sont cohérents.

### 10.2 Coûts

- Objectif : coût par exécution plan < 0,50 USD (usage LLM économiques).
- Check de balance optionnel (ENABLE_BALANCE_CHECK, MIN_BALANCE_THRESHOLD).

### 10.3 Portabilité

- macOS, Linux, Windows (WSL/Git Bash).
- Installation : script universel, pip, Docker, DMG macOS.

### 10.4 Sécurité

- Clés API dans `.env` (non versionné).
- CORS configuré pour le développement ; à restreindre en production.

### 10.5 Observabilité

- Métriques par étape et par plan (temps, tokens, coûts, cache hits).
- Export JSON/CSV des métriques.
- Logs (loguru).

---

## 11. Roadmap et priorités

### 11.1 Fait (v2.2)

- AETHERFLOW Core (Orchestrator, AgentRouter, PROTO/PROD/VerifyFix).
- Genome Generator, API exposant genome et Sullivan.
- Sullivan Phases 1–5 : Template→HTML, principes graphiques, ScreenPlanner, CorpsGenerator, Chatbot + organes par corps.
- Studio (page `/`, organes, appels API).
- CLI (workflows, genome, sullivan read-genome, plan-screens, build, designer).
- Route `/` robuste (plusieurs fallbacks pour éviter 404).
- API exposée sur `0.0.0.0:8000`.

### 11.2 En cours / à consolider

- Stabilité de la route `/` et du chargement du Studio selon environnement.
- Inférence top-down Sullivan (réduction des structures génériques).
- Sauvegarde et prévisualisation systématiques des composants générés.

### 11.3 Prévu

- Interface AETHERFLOW complète (upload plans, visualisation workflows).
- Mode Brainstorm.
- Mode Deploy.
- Système de comptes / quotas (beta puis production).
- Tests automatisés (unitaires, intégration, E2E).
- Documentation utilisateur et runbooks.

---

## 12. Glossaire et références

### 12.1 Glossaire

- **AETHERFLOW** : Orchestrateur d’agents IA (nom technique).
- **Homeos** : Nom commercial de la plateforme.
- **Genome** : Représentation structurée de l’API (OpenAPI → JSON).
- **Studio** : Interface principale servie à `/` (organes, genome, Sullivan).
- **Sullivan** : Kernel d’intelligence frontend (analyse, plan d’écrans, corps, chatbot).
- **Corps** : Écran / section de page dans le plan d’écrans.
- **Organe** : Bloc fonctionnel à l’intérieur d’un corps (mapping endpoints, x_ui_hint).
- **PROTO** : Workflow rapide (FAST → DOUBLE-CHECK).
- **PROD** : Workflow qualité (FAST → BUILD → DOUBLE-CHECK).
- **VerifyFix** : Workflow exécution + validation + corrections si besoin.

### 12.2 Références

- **PRD Sullivan** : `docs/02-sullivan/PRD_SULLIVAN.md`
- **Workflow idéal Sullivan** : `docs/02-sullivan/SULLIVAN_WORKFLOW_IDEAL.md`
- **Mode d’emploi Genome / Chatbot** : `docs/02-sullivan/MODE_EMPLOI_SULLIVAN_GENOME.md`
- **Références webdesign** : `docs/02-sullivan/Références webdesign de Sullivan.md`
- **Installation** : `docs/01-getting-started/INSTALLATION.md`
- **Guide rapide AETHERFLOW** : `docs/01-getting-started/GUIDE_RAPIDE_AETHERFLOW.md`
- **Répertoire outputs Sullivan** : `docs/references/technique/REPERTOIRE_OUTPUTS_SULLIVAN.md`
- **README projet** : `README.md`

---

**Document** : PRD HOMEOS (entier et à jour)  
**Dernière mise à jour** : 30 janvier 2026  
**Version** : 2.2 "Sullivan"
