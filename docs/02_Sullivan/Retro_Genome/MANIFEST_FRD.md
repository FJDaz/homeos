Voici une version **abstraite et actualisée** du manifeste Homeos (Aetherflow), structurée autour de **rôles fonctionnels** plutôt que de briques techniques figées. Ça rend le système intemporel et adaptable à ton funnel FAST → BUILD. À la fin, une **shortlist 2026** de solutions gratuites/OSS pour implémenter chaque rôle, priorisant VS Code-like, self-hosted et ton profil dev front/AI. [github](https://github.com/jet-admin/jet-bridge)

## 💎 Principes Fondamentaux (S-T-A-R)

**Vision** : Intention → Réalisation via Abstraction « Pristine ». Dualité Raisonnement (modèles lents) + Écriture (modèles rapides), Surgical Edit (AST), Génome local + Rétro-Génome.  
**Phases** : BRS (Trace/Brain-Reasoning) → BKD (Forge/Backend) → FRD (Tisseur/Frontend) → DPL (Propulseur/Deployment).  
**Économie** : Architecte valide les CR de l’Exécutant (Sullivan) avant archivage.

## 🧠 Phase 1 — BRS : Trace (Élaboration Sémantique)

**UI** :  
- Main : Multiverse (2-3 iframes LLM pour confrontation).  
- Sidebar G : Recherche + Facettes.  
- Sidebar D : Arbitrage/Synthèse.  
- Footer : Trace par colonne (clic → conversation).  

**Rôles** : Capture PRD/FRD → Confrontation → Arbitrage.

## 🛠️ Phase 2 — BKD : Forge (Production Pristine)

**UI** :
- Sidebar G : Workspace (fichiers locaux/cloud).
- Col 1 : Éditeur splittable (VS Code-like).
- Col 2 : Roadmap dynamique (ROADMAP.md / ACHIEVED / BACKLOG).
- Sidebar D : Majordome (pilotage).
- Footer : Terminal + Audit.

**Workflow** : Architecte → Mission → Exécutant (Sullivan) → CR → Validation/Repair.

**Implémentation BKD — Décision technique (2026-03-23) :**
L'éditeur BKD = **code-server** (VS Code dans le browser, self-hosted, Docker).
On n'utilise PAS Monaco seul — Monaco est l'éditeur, pas l'IDE. VS Code complet est la bonne granularité.

Architecture retenue :
- `code-server` embarqué dans l'UI BKD via `<iframe src="http://localhost:8080">`
- 1 extension VS Code custom **AetherFlow BKD** qui injecte :
  - WebviewPanel "Majordome" (sidebar D) — chat Sullivan
  - WebviewPanel "Roadmap" (col 2) — lecture ROADMAP.md / ACHIEVED / BACKLOG
- Extensions pré-installées dans l'image Docker : Roo Code, GitLens, Markdown Preview
- Auth : code-server `--auth none` en local, password en prod
- Multi-user (élèves) : 1 instance code-server par user (Docker container isolé)

Stack minimale BKD :
```
Docker : code-server (codercom/code-server:latest)
Extension : aetherflow-bkd (TypeScript, VS Code Extension API)
  → vscode.window.createWebviewPanel() pour Majordome + Roadmap
  → vscode.workspace.fs pour lire ROADMAP.md
  → fetch() vers /api/frd/chat pour Sullivan
Ports : 8080 (code-server), 9998 (AetherFlow backend)
```

Ce que VS Code fournit nativement (ne pas réimplémenter) :
- File explorer (Sidebar G)
- Terminal intégré (Footer)
- Split editor (Col 1)
- Git (GitLens)
- Syntax highlight, IntelliSense, search

## 🎨 Phase 3 — FRD : Tisseur (Génome Visuel)

**UI** :  
- Main : Genome Viewer (explosion organes/composants).  
- Sidebar G : Historique Intentions.  
- Sidebar D : Pédagogie HCI.  
- Footer : Tooltip (usage/source).  

**Workflow** : Style/Arbitrage BRS → Template → Figma Bridge bidirectionnel.

## 🚀 Phase 4 — DPL : Propulseur (Mise en Service)

**UI** :  
- Sidebar G : Secrets/Clés (Netlify/Vercel/Runpod).  
- Col 1 : Instructions/Chat.  
- Col 2 : iFrame service tiers.  
- Sidebar D : Guide (Capture Vision → Analyse).  

## Solutions d’Implémentation (Shortlist 2026)

| Rôle Homeos | Solutions gratuites/OSS prioritaires | Pourquoi ? (Alignement + Setup VS Code-like) |
|-------------|--------------------------------------|---------------------------------------------|
| **Architecte** (Raisonnement lent, validation CR) | 1. DeepSeek V3.1 (BytePlus ModelArk, 500k tokens gratuits)<br>2. Claude 3.5 Sonnet (API gratuite limitée)<br>3. Llama 3.1 405B (via Ollama local)  [docs.byteplus](https://docs.byteplus.com/en/docs/ModelArk/1801298) | Haut niveau raisonnement ; intégrable via Roo Code ou LiteLLM (proxy multi-LLM). Setup : `.env` API key → VS Code terminal. |
| **Exécutant Sullivan** (Écriture rapide, Majordome) | 1. Gemini 2.0 Flash (gratuit)<br>2. Groq LPU (Mixtral/Qwen gratuit)<br>3. DeepSeek Coder V2 (local via Ollama) | Vitesse + multimodal ; piloter via Roo Code modes (Code/Architect/Debug). Setup : Extension Roo Code → API key Gemini.  [github](https://github.com/qpd-v/Roo-Code) |
| **Éditeur VS Code-like** (Forge/Workspace) | 1. Roo Code (qpd-v/Roo-Code, VS Code plugin)<br>2. Cursor IDE (gratuit base)<br>3. VS Code + Continue.dev | Orchestration LLM native ; Surgical Edit via modes. Setup : Marketplace → Modes custom pour S-T-A-R.  [github](https://github.com/qpd-v/Roo-Code) |
| **Gateway/Propulseur** (APIs + Déploiement) | 1. API 200 (Docker self-hosted)<br>2. app.build (Neon agent full-stack)<br>3. tRPC + ts-rest (TypeScript-first)  [github](https://github.com/API-200/api200) | Cache/retries/mocks ; iFrames DPL. Setup : `docker run api200` → Proxy Netlify/Vercel. |
| **Générateur Backend/API** (BKD rapide) | 1. app.build (Fastify/Drizzle/React)<br>2. Jet Bridge (REST from DB)<br>3. Prisma + Fastify  [github](https://github.com/jet-admin/jet-bridge) | Full-stack jetable ; Pristine via Architecte. Setup : Prompt → Déploiement Koyeb auto. |
| **Genome Viewer/FRD** (Composants visuels) | 1. Storybook + React/Vue<br>2. Figma API + Plugin bidirectionnel<br>3. Plasmic (headless CMS UI) | Explosion sémantique ; Token extraction. Setup : VS Code + Tailwind → Figma webhook. |
| **Roadmap/Terminal** (Suivi/Audit) | 1. Obsidian/Markdown Notes (VS Code)<br>2. Git + Conventional Commits<br>3. Terminal VS Code intégré | ROADMAP.md dynamique. Setup : Extension Markdown Preview + GitLens. |
| **Figma Bridge** (Bidirectionnel) | 1. Figma REST API + Webhooks<br>2. Penpot (OSS Figma alt)<br>3. Builder.io (Visual CMS) | Sync Génome ↔ Design. Setup : Node script VS Code → Figma token. |

**Stack minimale gratuite pour MVP** : Roo Code (VS Code) + DeepSeek/Gemini (APIs) + API 200 (Gateway) + app.build (Génération) + Git/Obsidian (Roadmap). Total : 0€, self-hosted prioritaire, aligné front/AI. [github](https://github.com/API-200/api200)