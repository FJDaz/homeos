# PRD AETHERFLOW — À jour (v2.3)

**Product Requirements Document** : AETHERFLOW — Orchestrateur d’agents IA pour le développement logiciel.  
**Version** : 2.3.0  
**Dernière mise à jour** : Mars 2026  

---

## 1. Vue d’ensemble

### 1.1 Nom et positionnement

- **Nom produit** : AETHERFLOW (nom interne) / Homeos (nom commercial).
- **Rôle** : Orchestrateur d’exécution de plans de développement. Évolue vers un moteur **Standalone BKD** (Backend Development) pour la construction de code robuste et "Pristine".

### 1.2 Principe d’orchestration (Deep Flow)

- **Deep Flow Architecture** :
    - **Raisonnement (DeepSeek-R1)** : Analyse stratégique et architecturale initiale.
    - **Écriture (Fast Models)** : Génération itérative du code via Codestral, Groq ou DeepSeek-V3.
- **Claude Code (dans Cursor)** = architecte : produit les plans (`plan.json`).
- **AETHERFLOW** = exécuteur : lit le plan, gère le cycle de vie, le "Self-Healing" et la persistance.
- **Aucune Claude API** dans le cœur : la validation et le contrôle sont faits par Claude Code ou par des modes DOUBLE-CHECK (ex. Gemini) dans AETHERFLOW.

### 1.3 Objectifs clés

- **Exécution fiable** : exécuter des plans multi-steps avec dépendances, fallback provider (ex. rate limit), et application du code généré.
- **Coût / performance** : utiliser des providers économiques (DeepSeek, Groq, Gemini) avec cache sémantique et prompt cache quand disponible.
- **Qualité** : modes FAST (prototype) vs BUILD (qualité), Surgical Edit (modifications ciblées via AST), validation (VerifyFix, Run-and-Fix).
- **Extensibilité** : ajout de workflows (Run-and-Fix) et, à terme, d’un mode agentique (outils pendant l’exécution d’un step).

---

## 2. Spécifications fonctionnelles

### 2.1 Entrées

- **Plan JSON** (`plan.json`) : `task_id`, `description`, `steps[]` (id, description, type, complexity, estimated_tokens, dependencies, validation_criteria, context avec `files`, `language`, `framework`). Schéma : `docs/references/plan_schema.json`.
- **Contexte optionnel** : chaîne passée à tous les steps (ex. guidelines, stack).
- **Workflow** : choix du parcours (PROTO, PROD, VerifyFix, Run-and-Fix).

### 2.2 Workflows

| Workflow | Raccourci | Description |
|----------|-----------|-------------|
| **PROTO** (quick) | `-q` | FAST → application du code → validation DOUBLE-CHECK (Gemini). Prototypage rapide. |
| **PROD** (full) | `-f` | FAST (brouillon) → BUILD (refactor qualité) → application → validation DOUBLE-CHECK. Qualité production. |
| **VerifyFix** | `-vfx` | BUILD → application → validation DOUBLE-CHECK → si erreurs, plan de correction → exécution des corrections → re-validation. |
| **Run-and-Fix** | `-rfx` | Lance une **commande réelle** (ex. `npm run build`) ; en cas d’échec, envoie stderr/stdout + contexte au LLM, applique les corrections, relance la commande (max N tours). Pas de plan JSON requis, `--command` obligatoire. |
| **Run-and-Fix après PROD** | `-f --run-and-fix "cmd"` | Après exécution PROD, enchaîne avec Run-and-Fix sur la commande donnée. |

### 2.3 Modes d’exécution par step

- **FAST** : modèle rapide (ex. Groq), sortie directe.
- **BUILD** : modèle qualité (ex. DeepSeek), consignes qualité.
- **DOUBLE-CHECK** : audit / validation (ex. Gemini), retour structuré (ex. pedagogical feedback).
- **Surgical Edit** : si BUILD/DOUBLE-CHECK et fichiers Python dans le step, le LLM produit des instructions JSON (add_method, modify_method, etc.) appliquées via AST au lieu d’écraser le fichier.

### 2.4 Providers et routage

- **Providers supportés** : DeepSeek, Groq, Gemini, Codestral (selon clés API).
- **Routage** : selon le mode (FAST → Groq prioritaire, BUILD → DeepSeek, etc.) avec fallback en cas de rate limit (ex. 429).
- **Cache** : cache sémantique par step (namespace `step_{id}`), prompt cache si le provider le supporte.

### 2.5 RAG

- Enrichissement du contexte plan avec RAG (PageIndex) quand activé : récupération de passages pertinents pour la description du plan / contexte.

### 2.6 Sorties

- **Répertoire de sortie** : `step_outputs/` (fichiers `step_X.txt`, `step_X_code.txt`, `step_X_structure.md` selon split structure/code).
- **Métriques** : temps, tokens, coût par step et global, succès/échec.
- **Application** : fait par le `ApplyEngine` (fusionnant surgical, overwrite et fallback) piloté par l'Orchestrateur.

### 2.7 Asymétrie FAST/BUILD (Apply Logic)

- **FAST Mode** : Le code généré est considéré comme un brouillon (draft). Il est sauvegardé dans `step_outputs/` mais n'est **jamais** appliqué chirurgicalement aux fichiers source originaux pour éviter toute corruption accidentelle lors de la phase d'exploration. L'application se fait par écrasement si explicitement demandé ou via Claude Code.
- **BUILD Mode** : Le code est optimisé pour la production. Le mode **Surgical Edit** est activé par défaut pour les fichiers Python, permettant des modifications précises via AST. En cas d'échec surgical, un fallback vers l'extraction de blocs de code (Smart Overwrite) est tenté avant de recourir à la création de fichiers `.generated` pour revue manuelle.

---

## 3. Run-and-Fix (détail)

- **Objectif** : corriger en boucle à partir des **vraies** erreurs de build ou de déploiement (stdout/stderr).
- **Entrées** : `--command` (obligatoire), `--run-and-fix-workdir`, `--run-and-fix-max-rounds` (défaut 5).
- **Boucle** : exécution de la commande (liste blanche : `npm run *`, `pnpm run *`, `yarn *`, `cd ... && (npm|pnpm|yarn) *`, `docker build *`, `python -m pytest/build`, `./*.sh`) → si exit ≠ 0, constitution d’un prompt (commande + stderr + contexte fichiers), appel LLM, parsing des blocs `FILE: path` + contenu, écriture des fichiers → relance.
- **Sécurité** : timeout par run (défaut 120 s), répertoire de travail fixé, pas de commandes arbitraires.
- **Référence** : `docs/05-operations/CORRECTION_BUILD_DEPLOY.md`.

---

## 4. Intégrations

### 4.1 CLI

- **Point d’entrée** : `aetherflow` ou `python -m Backend.Prod.cli`.
- **Options principales** : `--plan`, `--workflow`, `-q` / `-f` / `-vfx` / `-rfx`, `--command` (run-and-fix), `--output`, `--context`, `--mentor` (feedback pédagogique), `--stats` (cache), `--costs`, `--status` (monitoring plan).
- **Sous-commandes** : `genome`, `studio`, `sullivan` (designer, build, dev, read-genome, plan-screens).

### 4.2 API FastAPI

- **Démarrage** : `python -m Backend.Prod.api` ou `./start_api.sh` ou Docker profile `api`.
- **Usage** : exécution de workflows / plans via HTTP, mode serveur pour enchaîner des runs sans recharger le modèle. Doc interactive : `/docs`.

### 4.3 Claude Code (Cursor)

- **Helper** : `Backend.Prod.claude_helper` — `execute_plan_cli()`, `get_step_output()`, `apply_generated_code()`, `generate_plan_with_planner()`.
- **Règle** : AETHERFLOW utilisé pour l’**implémentation** (génération de code) ; vérification / review / refactoring manuel par Claude Code directement.

### 4.4 Sullivan & Genome (Stenciler V3)

- **Genome** : Source de vérité unique (metadata, topology, endpoints). Représentation "Pristine" du produit.
- **Stenciler V3** : Module Illustrator-like pour la manipulation directe de l'UI.
    - **Illustrator Mode** : Édition interactive des primitives SVG au clic.
    - **Bottom-Up Rendering** : Priorité aux wireframes métiers (`WireframeLibrary`) sur le rendu générique.
    - **Persistance** : Synchronisation temps réel entre modifications graphiques (SVG) et données Genome.
- **Sullivan** : Build à partir du genome, dev mode analyse backend. Intégré au Stenciler pour la prévisualisation contextualisée.

---

## 5. Composants techniques (résumé)

- **Orchestrator** : lecture du plan, ordre d’exécution (dépendances), chargement des fichiers existants, appel AgentRouter par step, application Surgical si besoin, sauvegarde des sorties.
- **AgentRouter** : sélection du provider (mode + fallback), construction du prompt, cache sémantique, appel au client LLM, agrégation des métriques.
- **Clients LLM** : DeepSeek, Groq, Gemini, Codestral (interface commune `generate(prompt, context, max_tokens)`).
- **Workflows** : ProtoWorkflow, ProdWorkflow, VerifyFixWorkflow, RunAndFixWorkflow.
- **Core** : run_command (liste blanche, `run_allowed_command`), surgical_editor (AST, instructions JSON), plan_status, cost_tracker, RAG (PageIndex).
- **Modèles** : Plan, Step, StepResult, GenerationResult, feedback parser, etc.

---

## 6. Non-fonctionnel

- **Sécurité** : pas d’exécution de commandes arbitraires hors Run-and-Fix (liste blanche) ; chemins limités au workspace pour l’application du code.
- **Portabilité** : Python 3.9+, macOS / Linux / Windows (WSL ou Git Bash), Docker, pip, script d’install.
- **Config** : `.env` (clés API, timeouts, chemins). Voir `docs/notes/ENV_KEYS_CHECK.md`.

---

## 7. Roadmap (résumé)

- **Actuel (v2.3)** : Phase 14 (Stenciler V3), Write-back génome, Illustrator Mode, Palette Stenciler, Deep Flow (R1).
- **Court terme** : 
    - Mission 14C (Copie/Duplication).
    - Mission 14D (Sullivan Embedded - La Valise).
    - Nettoyage des interfaces (suppression mentions HTTP/Dev).
- **Moyen terme** : Mode **agentique** via LangGraph (Self-Healing autonome).
- **Long terme** : Tool calling natif, intégration CI/CD, multi-projets.

---

## 8. Références

- **Installation** : `docs/01-getting-started/INSTALLATION.md`
- **Workflow Cursor** : `.cursor/rules/aetherflow-workflow.mdc`
- **Run-and-Fix** : `docs/05-operations/CORRECTION_BUILD_DEPLOY.md`
- **Pouvoir agent** : `docs/05-operations/AETHERFLOW_AGENT_POWER.md`
- **Agentification** : `docs/05-operations/AGENTIFICATION_AETHERFLOW.md`
- **Schéma plan** : `docs/references/plan_schema.json` (si présent)
- **PRD Homeos** : `docs/04-homeos/PRD_HOMEOS.md` (vision produit élargie, Studio, Sullivan)

---

*Statut : PRD à jour reflétant l’état de AETHERFLOW v2.3 (mars 2026).*
