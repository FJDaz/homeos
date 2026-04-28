# ROADMAP_ACHIEVED — Archive April 2026

### Synthèse + Projection V4 — Mission Claude (après les 7 diagnostics)
**ACTOR: CLAUDE | DÉCLENCHEUR: tous les rapports Diag-1 → Diag-7 livrés**

Claude rédige deux documents à partir des 7 rapports :


## Phase Active (2026-04-15) — DIAGNOSTIC V4

**Décision FJD 2026-04-15 :** Suite à 6 missions de hotfix successifs (M300→M306) sans stabilisation durable, on suspend les patches et on lance un **diagnostic complet** avant toute V4.

**STATUS: ✅ COMPLÉTÉ | DATE: 2026-04-15 | ACTOR: GEMINI**

**Livrable :** 7 rapports détaillés dans `Frontend/4. COMMUNICATION/audits/`.
Synthèse finale : [SYNTHESE_V4.md](../../../.gemini/antigravity/brain/b28d2cde-2615-4f27-8474-ac45da718e20/walkthrough.md).

**Objectif :** rapport exhaustif de l'état réel — DB, backend, frontend, CI/CD — pour fonder une V4 sur des bases saines.

**Exécutant principal :** GEMINI (large contexte). Les rapports sont écrits dans `Frontend/4. COMMUNICATION/audits/`.

**Aucun fix pendant cette phase.** Audit read-only uniquement. Les recommandations seront triées par FJD avant tout chantier.

---

---

### Mission Diag-1 — Fondations DB : schéma, migrations, intégrité référentielle
**STATUS: 🔴 PRIORITÉ | DATE: 2026-04-15 | ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE
> MODE: AUDIT READ-ONLY — ne modifier aucun fichier code, ne pas toucher aux DB.

**Objectif :**
Cartographier l'état réel des bases SQLite, détecter les incohérences, les colonnes ajoutées par patch sans migration, les enregistrements orphelins.

**input_files :**
- `Frontend/3. STENCILER/bkd_service.py` (gestion DB principale)
- `Frontend/3. STENCILER/migrations/` (tous les .sql ou .py)
- `Frontend/3. STENCILER/server_v3.py` (PROJECTS_DB_PATH, BKD_DB_PATH)
- `Frontend/3. STENCILER/routers/auth_router.py`
- `Frontend/3. STENCILER/routers/class_router.py`
- `Frontend/3. STENCILER/routers/projects_router.py`

**Travail à faire :**

1. **Inventaire DB** — pour chaque fichier `.db` détecté :
   - Lister toutes les tables
   - Pour chaque table : colonnes, types, contraintes, index
   - Identifier les FK déclarées vs FK implicites (colonnes nommées `*_id` sans contrainte FK)

2. **Migrations vs réalité** :
   - Lister toutes les migrations dans `migrations/`
   - Comparer le schéma théorique (somme des migrations) vs schéma actuel
   - Détecter les colonnes présentes dans la DB mais absentes des migrations (= ajoutées par patch direct)
   - Détecter les migrations jamais appliquées

3. **Intégrité référentielle** (requêtes SQL read-only) :
   - `students` sans `user_id` (legacy)
   - `students` avec `project_id` pointant vers un projet inexistant
   - `projects` orphelins (`user_id` inexistant)
   - Doublons (mêmes noms d'élèves dans une classe)
   - `students.project_id` vs `active_project.json` : divergences

4. **Sources de vérité conflictuelles** :
   - `active_project.json` vs `students.project_id` vs variable globale `_ACTIVE_PROJECT_ID`
   - Pour chaque entité (projet actif, user_id), lister tous les endroits où l'état est stocké/lu

**Output attendu :** `Frontend/4. COMMUNICATION/audits/diag_1_db.md`

Sections obligatoires :
- ## Inventaire DB (tables + colonnes + index)
- ## Migrations : appliquées vs schéma réel
- ## Orphelins et incohérences (listes avec compteurs)
- ## Sources de vérité conflictuelles
- ## Recommandations V4 (priorisées : critique / important / cosmétique)

---

---

### Mission Diag-2 — Backend : routes, contrats, handlers bloquants
**STATUS: 🟠 PRÊTE | DATE: 2026-04-15 | ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE
> MODE: AUDIT READ-ONLY.

**Objectif :**
Cartographier toutes les routes FastAPI, identifier les handlers qui bloquent l'event loop, comparer avec `API_CONTRACT.md`, détecter les routes mortes ou les endpoints frontend orphelins.

**input_files :**
- `Frontend/3. STENCILER/server_v3.py`
- `Frontend/3. STENCILER/routers/*.py` (24 fichiers)
- `Frontend/1. CONSTITUTION/API_CONTRACT.md`
- `Frontend/3. STENCILER/static/js/**/*.js` (pour grep des `fetch(...)`)

**Travail à faire :**

1. **Inventaire routes** (tableau markdown) :
   | Path | Method | Handler | Fichier:Ligne | async/sync | Bloquant ? |
   - `Bloquant ?` = OUI si `async def` + appel SQLite/file I/O sans `run_in_executor`

2. **Comparaison API_CONTRACT.md** :
   - Routes documentées dans le contrat mais absentes du code
   - Routes implémentées mais absentes du contrat
   - Divergences de signatures (params query, body schema)

3. **Routes appelées vs définies** :
   - Grep de `fetch(`, `await fetch`, `axios.` dans tout le frontend JS
   - Lister chaque endpoint appelé par le frontend
   - Endpoints frontend pointant vers des routes inexistantes (404 garantis)
   - Routes backend jamais appelées par le frontend (= dead code potentiel)

4. **Middlewares & dépendances globales** :
   - Lister middlewares `app.add_middleware(...)` et leur ordre
   - Background tasks (Sullivan Pulse, refresh URLs, etc.)
   - Imports lourds au startup (ML models, RAG)

**Output attendu :** `Frontend/4. COMMUNICATION/audits/diag_2_backend.md`

Sections obligatoires :
- ## Inventaire routes (tableau)
- ## Handlers bloquants détectés (liste avec fichier:ligne)
- ## Divergences API_CONTRACT.md
- ## Endpoints frontend orphelins (404 garantis)
- ## Routes backend dead code
- ## Middlewares & startup overhead
- ## Recommandations V4

---

---

### Mission Diag-3 — Parcours Teacher (login → dashboard → sujets → activation)
**STATUS: 🟠 PRÊTE | DATE: 2026-04-15 | ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE
> MODE: AUDIT READ-ONLY.

**Objectif :**
Tracer le parcours complet enseignant : connexion → vue dashboard de classe → création/import sujet → activation projet pour un élève → vérification que l'élève voit le bon projet.

**input_files :**
- `Frontend/3. STENCILER/static/templates/teacher_dashboard.html`
- `Frontend/3. STENCILER/static/templates/cadrage_prof.html`
- `Frontend/3. STENCILER/static/js/teacher/*.js` (s'il existe)
- `Frontend/3. STENCILER/routers/class_router.py`
- `Frontend/3. STENCILER/routers/projects_router.py`
- `Frontend/3. STENCILER/routers/cadrage_router.py`
- `Frontend/3. STENCILER/routers/auth_router.py`

**Travail à faire :**

1. **Diagramme de séquence** (texte) pour chaque étape :
   - Login prof : quelle route, quel storage du token (cookie/localStorage), quel header sortant
   - Chargement dashboard : routes appelées, polling/refresh, état affiché
   - Création/import sujet : flow complet (upload PDF/texte → cadrage → projet créé)
   - Activation projet pour élève : route `activate_project`, écriture DB + JSON
   - Propagation côté élève : comment l'élève voit-il le projet activé ?

2. **Points de cassure observables** :
   - Race condition sur `active_project.json`
   - Désync `students.project_id` ↔ JSON
   - Cas où le prof active mais l'élève voit un autre projet
   - Erreurs silencieuses (try/except sans log)

3. **État réel des features** :
   - Liste des features visibles dans `teacher_dashboard.html` (boutons, sections)
   - Pour chaque feature : route backend correspondante existe-t-elle ?
   - Features mortes (boutons sans handler)

**Output attendu :** `Frontend/4. COMMUNICATION/audits/diag_3_teacher.md`

Sections obligatoires :
- ## Diagramme de séquence (login → activation)
- ## Cartographie features dashboard
- ## Points de cassure
- ## Features mortes ou incomplètes
- ## Recommandations V4

---

---

### Mission Diag-4 — Parcours Élève (login → workspace → drill → wire → save)
**STATUS: 🟠 PRÊTE | DATE: 2026-04-15 | ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE
> MODE: AUDIT READ-ONLY.

**Objectif :**
Tracer le parcours élève : login sans mot de passe → résolution token → ouverture workspace → onboarding stitch drill → édition wire → sauvegarde.

**input_files :**
- `Frontend/3. STENCILER/static/templates/student_login.html`
- `Frontend/3. STENCILER/static/templates/workspace.html` (ou équivalent)
- `Frontend/3. STENCILER/static/js/workspace/*.js` (WsStitchDrill, WsProjectPanel, ManifestBox, etc.)
- `Frontend/3. STENCILER/routers/auth_router.py`
- `Frontend/3. STENCILER/routers/workspace_router.py`
- `Frontend/3. STENCILER/routers/stitch_router.py`
- `Frontend/3. STENCILER/routers/wire_router.py`
- `Frontend/3. STENCILER/routers/manifest_router.py`

**Travail à faire :**

1. **Diagramme de séquence** :
   - Login élève → token créé/récupéré → redirection workspace
   - Ouverture workspace → quelles routes sont appelées au load (`/api/projects/active`, `/api/projects`, etc.)
   - Onboarding drill (StitchDrill) : étapes, conditions de skip, état persistant
   - Édition wire : sauvegardes auto vs manuelles, conflits de versions
   - Save/load manifest : où c'est stocké, qui le lit

2. **Cas limites** :
   - Élève sans projet activé → que voit-il ?
   - Élève dont le `students.user_id` est `NULL` (legacy avant M298)
   - Token expiré ou invalide
   - Drill interrompu en cours

3. **État UI** :
   - Quels modules JS sont chargés au démarrage du workspace
   - Quels modules sont morts ou inutilisés
   - Boutons sans handler (UI fantôme)

**Output attendu :** `Frontend/4. COMMUNICATION/audits/diag_4_student.md`

Sections obligatoires :
- ## Diagramme de séquence
- ## Modules workspace actifs
- ## Cas limites non gérés
- ## UI fantôme (boutons morts)
- ## Recommandations V4

---

---

### Mission Diag-5 — FEE (Front End Engineer) : GSAP studio + état réel
**STATUS: 🟠 PRÊTE | DATE: 2026-04-15 | ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE
> MODE: AUDIT READ-ONLY.

**Contexte de décision :**
Le Stenciler maison (SVG canvas, atoms, renderers, phases 12A/13A) est **abandonné** (FJD 2026-04-15).
La direction est le **FEE (Front End Engineer)** : un studio basé GSAP pour produire du frontend Awwwards-level.
Les fichiers concernés existent déjà (`WsFEE.js`, `WsFEEStudio.js`, `workspace/fee/`).

**Objectif :**
Évaluer l'état réel du FEE : ce qui est implémenté, ce qui est ébauché, ce qui manque pour en faire un studio opérationnel. Identifier les dépendances GSAP, la cohérence avec le workspace, et les features à construire pour un MVP Awwwards-worthy.

**input_files :**
- `Frontend/3. STENCILER/static/js/workspace/WsFEE.js`
- `Frontend/3. STENCILER/static/js/workspace/WsFEEStudio.js`
- `Frontend/3. STENCILER/static/js/workspace/fee/GsapCheatSheet.js`
- `Frontend/3. STENCILER/static/js/workspace/ws_main.js` (point d'entrée workspace)
- `Frontend/3. STENCILER/static/js/workspace/WsBoot.js`
- `Frontend/3. STENCILER/static/js/workspace/WsBootstrap.js`
- `Frontend/3. STENCILER/static/templates/` (chercher tout template qui importe GSAP ou fait référence au FEE)

**Travail à faire :**

1. **État WsFEE.js** (198L) :
   - Que fait-il exactement ? Lecture complète + résumé fonctionnel
   - Est-il branché au workspace (appelé depuis ws_main.js ou WsBoot) ?
   - Features implémentées vs stubs/TODOs

2. **État WsFEEStudio.js** (489L) :
   - Que fait-il ? Lecture complète + résumé fonctionnel
   - Relations avec WsFEE.js (composition, héritage, indépendance ?)
   - GSAP : importé via CDN, npm, ou local ? Quelles APIs utilisées (gsap.to, ScrollTrigger, etc.) ?

3. **GsapCheatSheet.js** (195L) :
   - Nature exacte : helper, preset library, catalogue d'animations ?
   - Utilisé par WsFEE/WsFEEStudio ou orphelin ?

4. **Intégration workspace** :
   - Le FEE est-il activé dans le workspace élève ? Sur quelle condition ?
   - Quelle route backend sert le contenu FEE ? (chercher dans workspace_router.py, projects_router.py)
   - Conflit ou chevauchement avec le Stenciler encore chargé ?

5. **Périmètre MVP Awwwards** :
   - Lister les features présentes (même partiellement)
   - Lister les features manquantes pour qu'un élève puisse produire un site animé Awwwards-style (éditeur de code, preview live, GSAP timeline UI, asset manager, export HTML/CSS/JS)

**Output attendu :** `Frontend/4. COMMUNICATION/audits/diag_5_fee.md`

Sections obligatoires :
- ## État WsFEE + WsFEEStudio (résumé fonctionnel)
- ## GSAP : intégration actuelle
- ## Branchement workspace (actif ou orphelin ?)
- ## Features présentes vs features manquantes (MVP)
- ## Dette Stenciler : fichiers à supprimer lors du nettoyage V4
- ## Recommandations V4

---

---

### Mission Diag-6 — CI/CD & Pipeline de déploiement
**STATUS: 🟠 PRÊTE | DATE: 2026-04-15 | ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE
> MODE: AUDIT READ-ONLY.

**Objectif :**
Cartographier le pipeline de build/déploiement — du génome élève au rendu Vercel. Identifier les scripts manuels, les dépendances cachées, les points de fragilité.

**input_files :**
- `Frontend/3. STENCILER/routers/preview_router.py`
- `Frontend/3. STENCILER/routers/genome_router.py`
- `Frontend/3. STENCILER/routers/retro_router.py`
- `Frontend/3. STENCILER/routers/class_router.py` (chercher `deploy_student_render`)
- `Frontend/3. STENCILER/server_v3.py` (background tasks, startup hooks)
- `Backend/Prod/` (orchestrator, apply_engine, surgical_editor — si pertinent pour la prod)
- Tout fichier `Dockerfile*`, `vercel.json`, `.github/workflows/*`, `package.json` à la racine
- `start.sh` et tout autre script shell de la racine

**Travail à faire :**

1. **Pipeline build** :
   - Génome SVG → HTML/CSS/JS final : quelle route, quel script
   - Snapshot + conversion (cf `snapshot_and_convert`)
   - Stockage des builds (chemin, format, durée de vie)

2. **Déploiement** :
   - Y a-t-il vraiment un déploiement Vercel automatisé ?
   - Quels secrets sont attendus (env vars) ? Lesquels sont chargés au startup ?
   - Mode dev vs prod : différences réelles dans le code

3. **Background tasks & cron** :
   - Sullivan Pulse : que fait-il exactement, à quelle fréquence ?
   - API URLs refresh (M275) : utile en local ou seulement en prod ?
   - RAG indexing : reconstruit à chaque boot ou caché ?

4. **Robustesse startup** :
   - `start.sh` actuel : ce qu'il fait, ses limites
   - Échecs silencieux au boot (modules absents, env vars manquantes)
   - Health endpoint : que vérifie-t-il vraiment ?

**Output attendu :** `Frontend/4. COMMUNICATION/audits/diag_6_cicd.md`

Sections obligatoires :
- ## Pipeline build (génome → rendu)
- ## Déploiement (réel vs aspirationnel)
- ## Background tasks & overhead
- ## Robustesse startup
- ## Secrets & env vars
- ## Recommandations V4

---

---

### Mission Diag-7 — Moteur AetherFlow : audit + vision refonte Manuel & Auto
**STATUS: 🔴 PRIORITÉ | DATE: 2026-04-15 | ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE
> MODE: AUDIT READ-ONLY + VISION. Deux livrables : état réel (audit) + proposition architecturale (vision refonte).

**Contexte de décision :**
AetherFlow fonctionne actuellement en mode **Manuel assisté** : FJD pilote via ROADMAP.md, Claude rédige les missions, Gemini exécute, Claude vérifie. C'est le workflow HoméOS actif.

FJD veut préparer **deux modes formels** pour la refonte moteur :

**Mode Manuel (formalisé) :**
- ROADMAP centrale + ROADMAP_ACHIEVED (archive append-only) — déjà en place
- Routine d'archivage standardisée (trigger : quand archiver, format, qui décide)
- Hiérarchie d'agents formalisée : **Claude = Architecte en chef** (rédige missions, valide rapports) | **Gemini = Ouvrier** (exécute) | **Second architecte** (Qwen, MIMO ou autre — candidate à définir, rôle : révision critique, missions parallèles simples)
- Gestion des défections : que faire quand un agent rate une mission (retry, amendment, réassignation)

**Mode Auto (LangGraph) :**
- Intégration d'un graph d'exécution (LangGraph ou équivalent) pour orchestrer les agents
- Latences stables : timeout par nœud, SLA par type de mission
- Fallbacks formels : si Claude sature → Gemini en archi / si Gemini rate → retry x2 → GPT → log incident
- Détection de défection automatique : mission marquée TERMINÉ sans livrable → détecteur → alerte
- Pas de hard-polling (pas de sleep loop) — event-driven ou webhooks

**Objectif Diag-7 :**
1. Cartographier ce qui existe déjà dans le moteur (clients, router, cascade, orchestrateur)
2. Identifier ce qui manque pour implémenter les deux modes
3. Proposer une architecture cible V4 du moteur

---

> M260, M266–M276 ✅ — archivées ROADMAP_ACHIEVED.md
> M278, M281, M275 (BYOK) ✅ — archivées ROADMAP_ACHIEVED.md
> M299–M306 ✅ — archivées ROADMAP_ACHIEVED.md

---

---

### Thème 31 — Fondation DB (single source of truth)

---

### Mission 306 — Débloquer l'event loop : async def → def sur les handlers SQLite-only
**STATUS: ✅ LIVRÉ | DATE: 2026-04-14 | ACTOR: Claude CODE DIRECT**

> BOOTSTRAP OBLIGATOIRE

**Contexte architectural :**

FastAPI avec un seul worker uvicorn. Tous les handlers déclarés `async def` tournent **dans l'event loop**. Chaque appel SQLite synchrone (`sqlite3.connect`, `con.execute`) à l'intérieur d'un `async def` **bloque l'event loop entier** — aucune autre requête ne peut être traitée pendant ce temps.

Symptôme observé : sous charge légère (auto-refresh teacher dashboard 30s × 3 classes + ouverture workspaces élèves), le serveur freeze 15-60 secondes. Toutes les requêtes timeout. Le process est vivant mais ne répond plus.

**La règle FastAPI :**
- `async def` = tourne dans l'event loop → jamais de I/O bloquant (pas de sqlite3, pas de file I/O synchrone)
- `def` = tourne dans un threadpool automatiquement → sqlite3, file I/O OK

**Travail à faire : changer `async def` → `def` sur tous les handlers qui n'ont PAS de `await`.**

---

---

### Mission 304 — DB comme seule source de vérité pour le projet actif
**STATUS: ✅ LIVRÉ | DATE: 2026-04-14 | ACTOR: Claude CODE DIRECT**

**Contexte architectural :**

M303 a posé les bases (context managers, flock JSON, fix connection leak). M304 fait la vraie décision : `active_project.json` reste en fallback legacy mais n'est plus la source de vérité. La DB `students.project_id` devient l'état maître. Tout workspace étudiant lit son projet depuis sa propre ligne en DB, pas depuis un fichier partagé.

**4 modifications chirurgicales — fichiers et lignes exactes :**

---

---

### Thème 29 — Stitch & Manifest (en cours)

---

### Mission 302 — Groq wrapper : injection de fichiers dans le contexte
**STATUS: ✅ LIVRÉ | DATE: 2026-04-13 | ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE

**Contexte :**

`groq-versatile.py` est un chat CLI pur (streaming texte). Groq ne peut pas lire de fichiers — il invente des réponses vraisemblables sans jamais toucher la codebase. Pour qu'il exécute des missions réelles, il faut injecter le contenu des fichiers cibles dans le system prompt avant d'envoyer.

**Fichier unique :** `/Users/francois-jeandazin/AETHERFLOW/groq-versatile.py`

**Contenu actuel du fichier (à modifier) :**

```python
import os, json, requests, sys
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
from rich.prompt import Prompt

load_dotenv(dotenv_path=Path("/Users/francois-jeandazin/AETHERFLOW/.env"))
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"
API_KEY = os.getenv("GROQ_API_KEY")
console = Console()

def chat():
    # INJECTION DE L'IDENTITÉ
    role_content = ""
    try:
        role_content = Path("/Users/francois-jeandazin/AETHERFLOW/LLAMA.md").read_text(encoding='utf-8')
    except:
        role_content = "Tu es un ingénieur de production sur le projet AetherFlow."

    console.print("[bold blue]🦙 LLAMA 3.3 VERSATILE ACTIF[/bold blue] (Identité chargée)")
    
    # On initialise l'historique avec le rôle système
    history = [{"role": "system", "content": role_content}]
    
    while True:
        try:
            u = Prompt.ask("\n[bold blue]CODE ❯[/bold blue]")
            if u.lower() in ["exit", "quit"]: break
            history.append({"role": "user", "content": u})
            full = ""
            console.print()
            with Live(console=console, refresh_per_second=10) as live:
                r = requests.post(API_URL, headers={"Authorization": f"Bearer {API_KEY}"}, 
                                 json={"model": MODEL, "messages": history, "stream": True}, stream=True)
                for line in r.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            data_str = line_str[6:].strip()
                            if data_str == "[DONE]": break
                            try:
                                delta = json.loads(data_str)['choices'][0]['delta'].get('content', '')
                                full += delta
                                live.update(Markdown(full))
                            except: continue
            history.append({"role": "assistant", "content": full})
        except KeyboardInterrupt: break
if __name__ == "__main__": chat()
```

---

---

### Mission 301 — Teacher Dashboard : freeze sur chargement répété
**STATUS: ✅ LIVRÉ | DATE: 2026-04-13 | ACTOR: GROQ**

**Contexte :**

Le teacher dashboard (`/teacher`) freeze après avoir chargé un premier étudiant. Les appels suivants (changement de classe, suppression projet, auto-refresh 30s) ne répondent plus. La page reste bloquée en état intermédiaire (loading spinner ou dashboard vide).

La cause probable : le serveur FastAPI répond trop lentement (ou pas du tout) sur l'endpoint `/api/classes/{class_id}/dashboard` quand des requêtes sont enchaînées. À confirmer par inspection des logs serveur.

---

---

### Mission 302 — Groq Context Injection : files context CLI
**STATUS: ✅ LIVRÉ | DATE: 2026-04-13 | ACTOR: ANTIGRAVITY**

**Objectif :** Permettre l'injection de fichiers locaux en contexte via CLI.
- **Résultat** : `python3 groq-versatile.py file1 file2` injecte le contenu complet + assistant acknowledgement.
- **Visuals** : Ajout de l'icône `📂` et du compteur de fichiers.
- **Code** : Script optimisé à 70 lignes.

---

---

### Mission 303 — Diagnostic Système : DB Leak + Race Condition JSON
**STATUS: ✅ LIVRÉ | DATE: 2026-04-14 | ACTOR: QWEN (GEMINI-AUX)**

**Problème :** Freeze permanent causé par des connexions SQLite non fermées et des écritures concurrentes sur `active_project.json`.
- **Fix DB** : Implémentation du context manager `bkd_db()` assurant la fermeture systématique des connexions.
- **Fix JSON** : Ajout de `fcntl.flock` (verrou matériel) pour sécuriser les accès concurrents.
- **Impact** : Stabilité retrouvée sur les runs longs.

---

---

### Mission 305 — Frontend Resilience : Guards & Timeouts
**STATUS: ✅ LIVRÉ | DATE: 2026-04-15 | ACTOR: GEMINI**

**Contexte :**
L'interface présentait des instabilités lors de charges serveurs élevées (ex: pendant l'indexation RAG). Les requêtes du dashboard s'accumulaient et le onboarding drill pouvait bloquer indéfiniment le chargement du workspace.

**Réalisations :**

1.  **Teacher Dashboard (Antidote au Refresh Storm)** :
    - Remplacement du `setInterval` (30s) par un `setTimeout` récursif.
    - **Logique** : Le nouveau délai de 30s ne commence qu'**après** le succès ou l'échec de `loadDashboard()`.
    - Protection supplémentaire via le verrou `_loadDashboardPending` pour interdire tout appel manuel simultané.

2.  **Stitch Drill (Anti-freeze)** :
    - Ajout d'un `AbortController` avec timeout de **5000ms** sur l'appel `isCanvasEmpty()`.
    - Si le backend ne répond pas (RAG lock), le drill rend la main au workspace immédiatement au lieu de rester figé sur l'overlay de chargement.

**Fichiers modifiés :**
- `Frontend/3. STENCILER/static/templates/teacher_dashboard.html`
- `Frontend/3. STENCILER/static/js/workspace/WsStitchDrill.js`

---

---

### Mission 300 — Serveur : stabilisation reload=False + restart propre
**STATUS: ✅ LIVRÉ | DATE: 2026-04-13 | ACTOR: Claude**

**Contexte :**

Le serveur FastAPI (`server_v3.py`) tourne avec `reload=True` (uvicorn StatReload). À chaque modification de fichier, uvicorn tue le process enfant et en recrée un — le port 9998 reste occupé par le parent fantôme, le process enfant ne répond plus. Résultat : serveur zombie, toutes les requêtes timeout.

**Symptôme actuel :** `curl http://localhost:9998/` → timeout (exit 28). `lsof -ti :9998` retourne plusieurs PIDs. Le serveur ne répond plus.

---

---

### Mission 299 — RM : Résolution conflit merge WsStitchDrill.js
**STATUS: ✅ LIVRÉ | DATE: 2026-04-13 | ACTOR: GEMINI → Claude**

> BOOTSTRAP OBLIGATOIRE

**Contexte :**

`WsStitchDrill.js` contient 3 conflits de merge non résolus (marqueurs `<<<<<<<`, `=======`, `>>>>>>>`). Le JS est invalide — le drill est cassé.

La résolution est **mécanique** : HEAD gagne sur les 3 conflits. Aucune logique à inventer.

---

---

### Mission 282 — Refonte panels : Project Panel V3 (Clean Session)
**STATUS: ✅ FAIT | DATE: 2026-04-12 | ACTOR: ANTIGRAVITY**

**Objectif :** Nettoyage complet du panneau projet pour débloquer le drill onboarding et aligner sur le scope `student.projects`.

**CR (Compte-Rendu) :**
- **Nettoyage Drastique** : Le panneau est désormais piloté à 100% par `homeos_session` (localStorage) pour éviter les conflits d'onboarding.
- **Boucle Explicite** : Implémentation de la boucle `for(i=0; i<count; i++)` sur `student.projects`.
- **Zéro Bloqueur** : Synchronisation fluide avec le Drill Stitch ; "Commencer à travailler" ouvre directement le Manifest Editor.
- **Synchro Manifeste** : `window.ManifestBox.showForProject(id)` permet une activation instantanée du contexte projet.

**Fichiers :** `WsProjectPanel.js` (V3), `ManifestBox.js`, `WsStitchDrill.js` (Ciblés).

---

---

### Mission 296 — Project Panel : token auth + scope réel user.projects[i]
**STATUS: ✅ LIVRÉ | DATE: 2026-04-12 | ACTOR: QWEN**

**Fichier unique :** `Frontend/3. STENCILER/static/js/workspace/WsProjectPanel.js`

- `_authHeaders()` helper — injecte `X-User-Token` depuis session
- `refresh()` — fetch `/api/projects` avec token → projets filtrés par user
- `activateAndShow()` — POST avec token → activation correcte côté serveur
- Suppression du fallback non-auth qui retournait tous les projets

---

---

### Mission 283b — Frontend : Session RBAC + UI Workspace
**STATUS: 🟠 PRÊTE | DATE: 2026-04-10 | ACTOR: GEMINI**

**Contexte :** Le backend M283a expose maintenant des sessions enrichies avec `workspace_id`, `plan` et `entitlements`. Le frontend doit adapter la session, le bootstrap et l'UI.

**Livrables :**

1. **Session enrichie** — `bootstrap.js` :
   - `homeos_session` = `{ user_id, name, role, plan, workspace_id, entitlements, token }`
   - Le monkey-patch `fetch` inclut `X-User-Token` (déjà fait)
   - Ajout : `X-Workspace-Id` header optionnel

2. **Guard RBAC frontend** — nouveau `rbac_guard.js` :
   - `canAccess(feature) → bool` — vérifie les entitlements de la session
   - Masque les boutons non autorisés (ex: Stitch si FREE)
   - Affiche un toast "Upgrade to Pro" si quota dépassé
   - Appliqué sur : bouton Stitch, bouton Forge, bouton Cadrage avancé

3. **UI Workspace selector** — dans le drawer Settings :
   - Affiche le workspace actif + plan badge (FREE/PRO/MAX)
   - Si teacher → lien vers "Ma classe" (dashboard)
   - Si student → affiche "Classe : DNMADE3"
   - Si user solo → "Workspace personnel"

4. **Matrice de visibilité UI :**
   | Élément UI | FREE | PRO | MAX |
   |------------|------|-----|-----|
   | Bouton Stitch | ❌ (grisé) | ✅ | ✅ |
   | BYOK panel | ❌ | ✅ | ✅ |
   | Max 4 écrans upload | ✅ (hard limit) | ✅ (20) | ✅ (∞) |
   | Quota indicator | ✅ | ✅ | ❌ (pas de quota) |

5. **Migration login/register** — le login retourne maintenant `plan` + `workspace_id` + `entitlements` → mettre à jour le stockage localStorage

**Fichiers :** `bootstrap.js`, nouveau `rbac_guard.js`, `WsStitchDrill.js` (adapter bouton Stitch si FREE), `ws_main.js` (guard sur forge)

---

### Mission 279 — FEE Studio : resolve écran actif + assets 404
**STATUS: 🟠 PRÊTE | DATE: 2026-04-10 | ACTOR: QWEN**

**Vérifications :**
- `WsFEEStudio.open()` : résout `activeScreen` depuis `wsCanvas.activeScreenId` ✅
- `bkd_router.py` `/fee/preview` : injecte `<base href>` ✅
- Tester sur un écran forgé (PNG → HTML) → l'iframe affiche le rendu avec CSS

**Fichiers :** `WsFEEStudio.js`, `bkd_router.py`, `WsImportList.js`

---

---

### Mission 257 — Hotfix : `convert_image()` — retirer les tokens HoméOS du fallback
**STATUS: ✅ ABSORBÉE PAR M262**

**Problème :** quand `design_md` est vide (projet sans DESIGN.md ou exception M256-A), `convert_image()` injecte les tokens HoméOS (`#8cc63f`, `#f7f6f2`, `#3d3d3c`, Geist) comme contrainte `IMPÉRATIVE`. Sullivan ignore l'image et produit une page HoméOS.

**Fichier :** `Backend/Prod/retro_genome/svg_to_tailwind.py` — méthode `convert_image()`, bloc `else` du `design_section` (L164-172).

**Fix :**
```python
# Avant
else:
    design_section = f"""
TOKENS DE DESIGN À RESPECTER (IMPÉRATIF) :
- Background principal : `{tokens['colors']['neutral']}`
...
"""

# Après
else:
    design_section = """
CONTRAINTE DESIGN : aucun design system prédéfini pour ce projet.
Extrais les couleurs, typographies et espacements directement depuis l'image.
Sois fidèle à ce que tu vois — ne substitue pas tes propres préférences de style.
"""
```

**Règle :** ne pas toucher à la branche `if design_md:` ni à `analyze_image_design()`. Scope strict.

---

---

### Thème 28 — Reroutage plugin Figma → Workspace (court-circuit Intent Viewer)

---

### Mission 265 — Plugin Figma → Workspace direct
**STATUS: ✅ LIVRÉ | DATE: 2026-04-08 | ACTOR: QWEN**

**Fix 1 — `ui.html` :** lien post-export → `/workspace` (plus `/intent-viewer`)
**Fix 2 — `import_router.py` :** nouvelle route `POST /api/import/figma` → sauve SVG dans `imports/`, met à jour `index.json`
**Fix 3 — Plugin `ui.html` :** `fetch()` poste vers `/api/import/figma` (plus `/api/retro-genome/upload-svg`)

Le SVG apparaît dans la screen list du workspace, forgeable via `POST /generate-from-import`.

---

---

### Thème 16 — Pipeline Import → Canvas
> M233 ✅, M234 ✅, M235 ✅, M236 ✅, M237 ✅ — archivées ROADMAP_ACHIEVED.md

---

---

### Thème 17 — Réparations post-M237 (Gemini regressions)

---

### Mission 238 — Hotfix canvas : 4 régressions M237
**STATUS: ✅ LIVRÉ**

- **Bug 1** : Hover outline exclut maintenant `el.id === 'root'` (React containers)
- **Bug 2** : Aucun changement de `pointer-events` sur les iframes dans `setMode()` — les iframes restent `pointer-events: none`, le moteur hover fonctionne inside l'iframe
- **Bug 3a** : Bouton Stitch ajouté dans la toolbar droite (lien vers `https://stitch.withgoogle.com`)
- **Bug 3b** : Bouton [S] restauré dans `fetchWorkspaceImports()` + listener `fetch('/api/stitch/open/{id}')` → `window.open(d.url)`
- **Bug 4** : `addScreen()` défensif — log si `WsScreenShell` non chargé, structure simplifiée

**Fichiers :** `WsCanvas.js`, `WsScreenShell.js`, `ws_main.js`, `workspace.html`

---

---

### Mission 237 — Canvas N0 : drag zone + moteur hover injecté dans l'iframe
**STATUS: ✅ LIVRÉ**

- **Zone de drag** : gripper visuel "⋯" centré sur le header du shell, `cursor: move`
- **Moteur hover** : `injectHoverEngine()` dans `WsCanvas.js` injecté dans le contentDocument de l'iframe
  - `mouseover` → outline vert `#8cc63f` + postMessage `{ type: 'hm-hover', tag, id, cls }`
  - `mouseout` → clear outline + postMessage `{ type: 'hm-clear' }`
  - `click` → stopPropagation + postMessage `{ type: 'hm-click', tag, id, cls, href }`
- `WsScreenShell.js` : appel `wsCanvas.injectHoverEngine(iframe)` au `load`
- `pointer-events: none` par défaut sur l'iframe, `auto` en mode `select` (déjà géré par le canvas)

---

---

### Mission 236 — Backend : routes assets/img par projet
**STATUS: ✅ LIVRÉ**

- `POST /api/projects/active/assets/upload` — upload image (png/jpg/jpeg/webp/svg/gif, max 10MB)
- `GET /api/projects/active/assets` — liste images du projet (tri par date desc)
- `GET /api/projects/assets/img/{filename}` — sert l'image
- `DELETE /api/projects/assets/img/{filename}` — supprime
- Stockage : `projects/{project_id}/assets/img/`
- Extensions validées + limite 10MB

**Contexte :** Les élèves uploadent des images (PNG, JPG, JPEG, WebP, SVG) dans leur projet. Ces images doivent être stockées dans `projects/{project_id}/assets/img/`, listables, servables, et supprimables.

**Fichier cible :** `Frontend/3. STENCILER/routers/import_router.py` (ou nouveau `assets_router.py` si plus propre — dans ce cas l'enregistrer dans `server_9998_v2.py`)

**Routes à créer :**

**1. Upload**
```
POST /api/projects/active/assets/upload
Content-Type: multipart/form-data
file: <UploadFile>
```
- Stocke dans `get_active_project_path() / "assets" / "img" / {safe_filename}`
- `safe_filename` = slugify + timestamp pour éviter les collisions
- Retourne `{ "status": "ok", "file": { "name": original_name, "filename": safe_filename, "url": "/api/projects/assets/img/{safe_filename}" } }`

**2. Liste**
```
GET /api/projects/active/assets
```
- Retourne `{ "files": [ { "name": ..., "filename": ..., "url": ..., "size": ... }, ... ] }`
- Scanne `assets/img/` — extensions acceptées : `.png .jpg .jpeg .webp .svg .gif`
- Ordre : plus récent en premier

**3. Servir un fichier**
```
GET /api/projects/assets/img/{filename}
```
- `FileResponse` depuis `get_active_project_path() / "assets" / "img" / filename`
- 404 si absent

**4. Supprimer**
```
DELETE /api/projects/assets/img/{filename}
```
- Supprime le fichier physique
- Retourne `{ "status": "deleted" }`

**Contraintes :**
- Créer `assets/img/` avec `mkdir(parents=True, exist_ok=True)` à chaque accès
- Limiter la taille upload à 10MB (vérifier `len(content) <= 10_000_000`)
- Extensions autorisées uniquement (rejeter sinon avec 400)

---

---

### Thème 7 — Wire → Cadrage

> M147 ✅, M181 ✅, M183 ✅, M185 ✅, M186 absorbée M187, M187 ✅, M184 ✅, M188 (dashboard) ✅ — archivées

---

### Mission 188 — Wire : Aperçu fonctionnel post-forge
**STATUS: 🟠 PRÊTE**
**DATE: 2026-04-06 | ACTOR: GEMINI**

Bouton "tester" dans l'overlay Wire post-forge → `window.open('/api/frd/file?name={name}&raw=1&wire=1')`.
- `server_v3.py` : si `wire=1`, retourner HTML brut sans tracker
- `WsWire.js` : bouton cliquable après `_executeForge` succès

---

---

### Thème 8 — Système Miroir
> M158 ✅, M159 ✅, M160 ✅, M161 ✅ — archivées

**Dette technique post-M158 :**
1. `Canvas.feature.js` (53KB) : Découplage moteur SVG / Zoom-Pan
2. `sullivan_renderer.js` (33KB) : Migration DOM Factory → composants DESIGN.md
3. `semantic_bridge.js` (19KB) : Simplification routage Sullivan → FEE

---

---

### Thème 9 — Multi-Projet
> M162 ✅, M163 ✅, M164 ✅, M165 ✅ — archivées

---

---

### Thème 10 — Design System

---

### Mission 167 — DESIGN.md HoméOS
**STATUS: ✅ LIVRÉ | ACTOR: FJD + CLAUDE**
`Frontend/1. CONSTITUTION/DESIGN.md` — Colors, Typography, Shape, Effects, Spacing, Tone, Forbidden.

---

---

### Thème 14 — Backend IDE
> M208 ✅ — archivée (`WsBackend.js`, War Room 3 colonnes, Quick-Switcher)

---

---

### Thème 15 — FEE Lab
> M209 ✅ — archivée (`WsFEE.js`, layout Studio, Sullivan FEE)

---

### Mission 221 — FEE Studio : overlay "Camera RAW" 4 zones au clic "front dev"
**STATUS: ✅ LIVRÉ | DATE: 2026-04-07 | ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE
> Vision complète : `docs/09_Frontend/FEE_POPOVER_VISION.md`

**CONTEXTE CRITIQUE : cette mission se passe entièrement dans `/workspace` (`workspace.html`).
Ne pas créer de nouvelle page, ni de route `/fee`. L'overlay est injecté dans le DOM du workspace au clic sur le bouton `[data-mode="front-dev"]` déjà présent dans `workspace.html`. Il flotte au-dessus du layout workspace existant (`position: fixed; inset: 0; z-index: 9000`). Le workspace reste monté en dessous.**

**Concept :** le mode FEE est un outil d'étalonnage de l'interactivité, pas de construction. L'étudiant est DA, Sullivan traduit l'émotion en timeline GSAP.

```
┌──────────────────────────────────────────────────────────────┐
│  GAUCHE (~240px)    │   CENTRE (flex-1)     │  DROITE (~320px) │
│  Explorateur        │   Iframe "pristine"   │  Sullivan FEE    │
│  data-af-id tree    │   Hot-Reload temporel │  Vibe-to-Code    │
│  LEDs GSAP          │   Play/Pause/Rewind   │  logic.js AST    │
│  State selector     │   Slow-Mo             │  chat + input    │
│─────────────────────┴───────────────────────┴─────────────────│
│  BAS (~100px) — Pellicule : Entrées | Sorties | Parallaxe | Distorsions | Hover │
└──────────────────────────────────────────────────────────────┘
```

**Gauche — Explorateur de Triggers :**
- Appel `postMessage` à l'iframe → récupère tous les `[data-af-id]`
- Afficher arborescence : nom de l'élément + `data-af-id`
- LED verte si l'élément possède déjà une timeline GSAP dans `logic.js`
- Sélecteur State : `initial` / `hover` / `click` / `scroll-trigger` — filtre le contexte envoyé à Sullivan

**Centre — Labo Photo :**
- `<iframe id="fee-preview-iframe">` → URL : `/api/bkd/fee/preview?project_id={id}&path={file}`
- Hot-Reload : injection via `postMessage` du code généré par Sullivan, sans rechargement complet
- Barre de contrôle : Play / Pause / Rewind / ×0.25 Slow-Mo (dispatche des commandes GSAP via postMessage)

**Droite — Sullivan FEE (Vibe-to-Code) :**
- Réutiliser `WsFEE.js` logique chat (historique + input + stream SSE)
- Contexte envoyé à Sullivan = `{ trigger: data-af-id, state, existing_code: extrait logic.js }`
- Code généré isolé dans un bloc `// [FEE-LOGIC-START] ... // [FEE-LOGIC-END]` dans `logic.js`
- Bouton "appliquer" → `POST /api/bkd/fee/apply` → patch chirurgical AST

**Bas — Pellicule d'Effets :**
- Strip horizontale scrollable, vignettes par catégorie : `Entrées` | `Sorties` | `Parallaxe` | `Distorsions P5.js` | `Hover`
- Clic vignette → pré-remplit le chat Sullivan avec le squelette de code correspondant

**Déclenchement :**
- Clic `[data-mode="front-dev"]` → injecte l'overlay dans `body` si absent → `classList.remove('hidden')`
- Bouton × → `classList.add('hidden')` + reset mode toggle
- Ne pas toucher au GSAP drawer existant (`ws-fee-effects-drawer`) — ce nouvel overlay le remplace

**Fichiers à lire :**
- `Frontend/3. STENCILER/static/templates/workspace.html` — bouton `front-dev`, structure body
- `Frontend/3. STENCILER/static/js/workspace/WsFEE.js` — logique Sullivan FEE existante
- `Frontend/3. STENCILER/static/templates/bkd_frd.html` — référence layout tripartite Mission 208
- `docs/09_Frontend/FEE_POPOVER_VISION.md` — vision complète

**Fichiers à créer/modifier :**
- `Frontend/3. STENCILER/static/js/workspace/WsFEEStudio.js` — **créer** : classe `WsFEEStudio`, injecte et orchestre les 4 zones
- `Frontend/3. STENCILER/static/templates/workspace.html` — charger `WsFEEStudio.js`, brancher sur `[data-mode="front-dev"]`

**Style :** `#f7f6f2` bg, `#3d3d3c` text, `#8cc63f` accent, `border: 1px solid #e5e5e5`, `font-family: Geist`, `border-radius: 0` (Hard-Edge). Pas d'emojis. Pas de majuscules labels.

**Livrable :**
1. Clic "front dev" → overlay 4 zones s'ouvre plein écran
2. Explorateur gauche liste les `data-af-id` de l'iframe
3. Sullivan traduit l'intention en timeline GSAP → code injecté dans `logic.js`
4. Hot-reload visible dans l'iframe sans rechargement
5. Pellicule bas cliquable → pré-remplit Sullivan

**CR post-livraison (Qwen) :**
- `POST /api/bkd/fee/apply` manquante → ajoutée (injecte code avec markers FEE dans logic.js)
- Bouton `[data-mode="front-dev"]` non branché → auto-init ajouté dans WsFEEStudio.js
- Bloc try/except de `fee/chat` cassé → réparé
- Presets étendus : 5 → **20** dans 5 catégories (entrées ×7, sorties ×3, parallaxe ×3, hover ×5, continu ×2)

---

---

### Thème 16 — EdTech DNMADE
> M210 ✅, M214 ✅, M215 ✅, M216 ✅, M217 ✅, M218 ✅, M219 ✅, M220 ✅ — archivées

## Thème 17 — Rattrapage EdTech (Vendredi)

> Bugs identifiés 2026-04-07. Traiter dans l'ordre.

---

### R0 — Sullivan patch_element : _apply_tailwind_diff manquant → blobs Tailwind
**STATUS: ✅ LIVRÉ**

**Fix appliqué dans `frd_router.py` :**
- `_apply_tailwind_diff(source_html, diff)` — patch chirurgical de classes Tailwind via BeautifulSoup (fallback data-wire inclus)
- `_strip_tailwind_blobs(html)` — supprime les `<style>` > 5000 chars avant sauvegarde
- `save_frd_file()` appelle `_strip_tailwind_blobs()` avant `write_text`
- `sullivan_router.py` importe maintenant la fonction existante → plus d'exception silencieuse

**Validé :**
```bash
# patch_element : add/remove classes OK
# strip blob >5000 : ✅ supprimé
# preserve small <style> : ✅ conservé
# data-wire fallback : ✅ OK
```

---

### R1 — `/teacher` : formulaire "créer une classe" ne soumet pas
**STATUS: ✅ LIVRÉ**

**Fix appliqué :**
- `createClass()` : error handling complet (validation HTTP status, feedback UI rouge/vert, console.log debug)
- Ajout `PUT /api/classes/{id}` — modifier une classe (backend + modal frontend)
- Ajout `DELETE /api/classes/{id}` — supprimer une classe + cascade étudiants
- Boutons "modifier" et "supprimer" visibles quand une classe est sélectionnée
- Tableau de sujets ajouté au dashboard — `GET /api/classes/{id}/subjects` appelé au chargement
- Affiche sujet/description/competences ou "aucun sujet" si vide

```bash
# Testé et validé :
curl -X POST http://localhost:9998/api/classes -H "Content-Type: application/json" -d '{"name":"DNMADE 2026","subject":"Design Web"}'
curl -X PUT http://localhost:9998/api/classes/dnmade-2026 -H "Content-Type: application/json" -d '{"name":"DNMADE 2026 v2","subject":"Design Web"}'
curl -X DELETE http://localhost:9998/api/classes/dnmade-2026
```

---

---

### R2 — Cadrage mode prof : `class_id` pas transmis à Sullivan
**STATUS: ✅ LIVRÉ**

**Diagnostic :** Le frontend passait déjà `class_id` dans l'URL SSE. Le router l'acceptait déjà. `_load_class_meta()`, `_load_dnmade_referentiel()`, `_build_prof_system()` existaient déjà dans `brainstorm_logic.py`.

**Le seul bug :** chemin DB incorrect dans `_load_class_meta()`
- Avait : `... / "Frontend/3. STENCILER" / "db" / "projects.db"` (n'existait pas)
- Corrigé : `... / "db" / "projects.db"` (racine AETHERFLOW)

**Résultat :** Sullivan reçoit maintenant le contexte DNMADE complet — nom de classe, sujet actif, et référentiel 4 domaines / 10 compétences.

**Fichier modifié :** `Backend/Prod/retro_genome/brainstorm_logic.py` — ligne DB path corrigée

---

---

### R9 — bootstrap.js:814 TypeError : refreshNav undefined
**STATUS: ✅ LIVRÉ**

**Fix :** ajout guard `if (!window.HOMEOS) window.HOMEOS = {};` avant assignation de `refreshNav` et `boot`.
**Fichier :** `Frontend/3. STENCILER/static/js/bootstrap.js` ligne 814.

---

### R3 — Onglet "Dashboard" absent du nav en mode prof
**STATUS: ✅ VALIDÉ**

Bootstrap.js injecte le nav dynamique avec l'onglet Dashboard pour `role === 'prof'` (ligne `TABS.unshift({ id: 'dashboard', label: 'Dashboard', ... path: '/teacher' })`).

---

---

### R4 — cadrage_alt.html : Univers LT Std Light + max-width
**STATUS: ✅ LIVRÉ (CODE DIRECT)**

- Streams + inputs → `font-family: 'Univers LT Std'; font-weight: 300; font-size: 14px`
- `@font-face` → `/static/fonts/univers-lt-std/univers-lt-std-300.woff2`
- Contenu centré `max-width: 48rem`
- Panneau compétences prof → `top: 120px` (hors zone "+ capture")

---

---

### R8 — Cadrage mode prof : UX simplifiée (sans arbitrage, sans PRD)
**STATUS: ✅ LIVRÉ**

**Modifications appliquées :**
- Masquage auto des outils d'arbitrage/PRD et du panneau Sullivan en mode prof.
- Amorce silencieuse auto-générée à l'ouverture pour guider le professeur.
- Carte de confirmation visuelle (verte) injectée lors de la détection du sujet structuré.
- Logique de redirection vers `/teacher` après création du sujet.

**Livrable :**
1. `/cadrage?mode=prof&class_id=dnmade-2026` → accueil Sullivan automatique, pas de boutons arbitrage/PRD
2. Discussion → compétences dans panneau droit
3. `<!-- SUJET: -->` détecté → carte verte + bouton "créer le sujet →" actif
4. Clic → retour `/teacher`

---

---

### R5 — Sujets créés → visibles dans `/teacher`
**STATUS: ✅ VÉRIFIÉ**

`teacher_dashboard.html` appelle `GET /api/classes/{id}/subjects` via `loadSubjects()` au chargement d'une classe. Tableau affiché avec titre, description, compétences.

---

---

### R6-A — Login élève : résolution classe + student_id
**STATUS: ✅ LIVRÉ**

- `auth_register()` cherche l'élève dans `students` par `display` (case-insensitive)
- Retourne `student_id`, `class_id`, `project_id` dans la réponse
- `login.html` : si élève reconnu et `project_id` null → appelle `/start` pour créer le projet → redirige `/workspace?project_id=X`
- Session stocke `student_id`, `class_id`, `project_id` pour les composants downstream
- Flow admin/prof inchangé (class_id null = redirect `/teacher`)

---

---

### R6 — Workspace étudiant : isolation projet dans Stitch
**STATUS: ✅ LIVRÉ**

- `/workspace?project_id={id}` → active le projet via `POST /api/projects/activate` avant chargement (XHR synchrone dans `<head>`)
- Stitch pointe sur `projects/{uuid}/imports/` (active_id mis à jour)
- Export → sauvegardé dans `projects/{uuid}/exports/`
- Dashboard prof → bouton "ouvrir" active le projet puis ouvre `/workspace` dans nouvel onglet

---

---

### M222 — Stitch : reconnaissance et sync automatique par project_id HoméOS
**STATUS: ✅ LIVRÉ**

- Backend : `GET /api/stitch/project-info` → retourne `stitch_project_id` + titre du manifest du projet actif
- Frontend : `WsStitch._syncProjectId()` auto-remplit le champ `project_id` au `show()`
- Flow : `show()` → `updateStatus()` → `_syncProjectId()` → `loadSession()`

**Fichiers à modifier :**
- `stitch_router.py` — ajouter `GET /api/stitch/project-info`
- `WsStitch.js` — ajouter `_syncProjectId()`, l'appeler dans `show()`

**Règle :** ne pas toucher à `loadSession()` ni à `_patch_manifest_stitch_project_id`. Scope strict.

**Livrable :**
1. Workspace ouvert avec `?project_id=dnmade-2026-blart-samuel`
2. Panel Stitch ouvert → `stitch_project_id` auto-rempli depuis manifest
3. `loadSession()` peut opérer sans saisie manuelle

---

---

### R7 — CI/CD élèves : déploiement des rendus
**STATUS: ✅ LIVRÉ**

**Pipeline GitHub Actions :** `.github/workflows/deploy-student.yml`
- Trigger : `workflow_dispatch` (manual avec `project_id`) ou push sur `student-deploy/*`
- Étapes : resolve project → check exports → prepare bundle → deploy HF Spaces → update milestone N5
- Cible : HF Space `FJDaz/homeos-students` (ou fallback `FJDaz/homeos`)

**Backend :** `POST /api/classes/{class_id}/students/{student_id}/deploy`
- Vérifie exports exists + HTML files
- Trigger GitHub Actions via repository_dispatch
- Update milestone à N5 (Déployé)
- Retourne URL de déploiement

**Utilisation :**
```bash
# Via API
curl -X POST http://localhost:9998/api/classes/dnmade1-2026/students/blart-samuel/deploy

# Via GitHub Actions (manuel)
# Actions → deploy student render → Run workflow → project_id=dnmade1-2026-blart-samuel
```

## Thème 18 — Désintoxication bootstrap.js

> Diagnostic 2026-04-07. `bootstrap.js` (829L) injecte ~350L de CSS inline à chaque page, plus du code workspace-spécifique (GSAP). Pas de bug actif (R9 réglé, static nav supprimé), mais c'est une bombe à retardement pour les agents et le cache browser.

---

### B1 — Extraire le CSS de bootstrap.js → homeos-nav.css
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-07 | ACTOR: QWEN**

**Contexte :**
`bootstrap.js` injecte ~350L de CSS via `style.textContent = \`...\`` dans `injectStyles()`.
Ce CSS ne change jamais → il devrait être un fichier statique, cacheable.

**Fichiers à lire :**
- `Frontend/3. STENCILER/static/js/bootstrap.js` (829L)

**Fichiers à créer/modifier :**
- `Frontend/3. STENCILER/static/css/homeos-nav.css` — **créer** avec tout le contenu de `injectStyles()`
- `Frontend/3. STENCILER/static/js/bootstrap.js` — remplacer `injectStyles()` par injection d'un `<link>` vers `/static/css/homeos-nav.css`

**Livrable :**
```js
// bootstrap.js — injectStyles() remplacée par :
function injectStyles() {
    if (document.getElementById('homeos-bootstrap-css')) return;
    const link = document.createElement('link');
    link.id = 'homeos-bootstrap-css';
    link.rel = 'stylesheet';
    link.href = '/static/css/homeos-nav.css';
    document.head.appendChild(link);
}
```

**Règle :** ne pas toucher à autre chose dans bootstrap.js. Scope strict.

---

---

### B2 — Sortir le code GSAP/workspace de bootstrap.js
**STATUS: ✅ LIVRÉ**

- Code workspace (`ws-mode-btn`, `effects-drawer`, `GsapCheatSheet`) extrait de `bootstrap.js`
- Déplacé dans nouveau fichier `WsBootstrap.js`
- `workspace.html` charge `WsBootstrap.js`
- `bootstrap.js` est maintenant propre : ne fait que nav + styles globaux

## Thème 19 — Auth & Login redesign

---

### M224 — Login : prof par mot de passe, élève par classe + prénom
**STATUS: ✅ LIVRÉ**

**Backend (`auth_router.py`) :**
- Migration DB : colonne `password_hash` ajoutée à `users`
- `POST /api/auth/register-prof` — inscription prof (nom + mot de passe hashé SHA-256)
- `POST /api/auth/login-prof` — login prof par nom + mot de passe
- `POST /api/auth/login-student` — login élève sans mot de passe (class_id + student_id)
- `GET /api/classes/{class_id}/students-list` — liste publique des élèves (sans auth)

**Testé :**
- ✅ Inscription prof → token + role='prof'
- ✅ Login prof correct → token retourné
- ✅ Mauvais mot de passe → 401 "Mot de passe incorrect"
- ✅ Students list → retourne id + display + project_id

**Note :** Frontend UI login (deux branches prof/élève) à implémenter par Gemini.

## Thème 21 — ProjectContext RAG

---

### M226 — ProjectContext : contexte projet canonique injecté dans tous les LLM
**STATUS: ✅ LIVRÉ | DATE: 2026-04-07 | ACTOR: QWEN**

> Absorbe M225. Remplace toutes les injections de contexte ad hoc.

**Principe :**
Un seul objet `ProjectContext` chargé une fois par session → injecté dans **tout** appel LLM (cadrage, brainstorm, Sullivan FEE, pre-eval). Le LLM est instruit de respecter impérativement ce contexte avant de répondre.

**Sources à agréger (par ordre de priorité) :**
```
projects/{project_id}/
  ├── manifest.json          → écrans, atoms, stitch_project_id
  ├── genome.json            → structure narrative
  ├── exports/PRD_*.md       → dernier PRD validé (le plus récent)
  └── design.md              → design system projet (si présent)

Frontend/1. CONSTITUTION/
  └── DESIGN.md              → design system HoméOS global (fallback)

classes/{class_id}/subjects/ → sujet DNMADE lié (si class_id en session)
dnmade_referentiel.json      → compétences (si mode éducation)
```

**Backend — créer `Backend/Prod/retro_genome/project_context.py` (ACTOR: QWEN) :**

```python
class ProjectContext:
    def __init__(self, project_id: str = None, class_id: str = None):
        self.project_id = project_id
        self.class_id = class_id
        self._cache = None

    def load(self) -> str:
        """Charge et formate toutes les sources en un bloc texte pour le prompt."""
        if self._cache:
            return self._cache
        sections = []

        # 1. Manifest
        manifest = self._read_json(PROJECTS_DIR / self.project_id / "manifest.json")
        if manifest:
            sections.append(self._format_manifest(manifest))

        # 2. Genome
        genome = self._read_json(PROJECTS_DIR / self.project_id / "genome.json")
        if genome:
            sections.append(f"GÉNOME PROJET:\n{json.dumps(genome, ensure_ascii=False, indent=2)[:2000]}")

        # 3. Dernier PRD
        prd = self._latest_prd()
        if prd:
            sections.append(f"PRD VALIDÉ:\n{prd[:3000]}")

        # 4. Design system projet ou HoméOS global
        design = self._read_file(PROJECTS_DIR / self.project_id / "design.md") \
                 or self._read_file(CONSTITUTION_DIR / "DESIGN.md")
        if design:
            sections.append(f"DESIGN SYSTEM:\n{design[:1500]}")

        # 5. Sujet DNMADE si class_id
        if self.class_id:
            sujet = self._latest_subject()
            if sujet:
                sections.append(f"SUJET DNMADE:\n{sujet}")
            ref = _load_dnmade_referentiel()
            if ref:
                sections.append(f"RÉFÉRENTIEL DNMADE:\n{ref}")

        self._cache = "\n\n---\n\n".join(sections)
        return self._cache

    def as_system_prefix(self) -> str:
        ctx = self.load()
        if not ctx:
            return ""
        return (
            "CONTEXTE PROJET — respecte ces règles IMPÉRATIVEMENT avant de répondre.\n"
            "Ne propose rien qui contredise le manifest, le design system ou le PRD validé.\n\n"
            + ctx + "\n\n---\n\n"
        )
```

**Intégration dans `brainstorm_logic.py` :**

Modifier `sse_chat_generator()` — remplacer toute la logique d'injection contextuelle par :
```python
from .project_context import ProjectContext

ctx = ProjectContext(project_id=project_id, class_id=class_id)
system_prompt = ctx.as_system_prefix() + (BRS_CHAT_SYSTEM if not class_id else "")
```

Supprimer les helpers devenus redondants : `_load_class_meta`, `_load_dnmade_referentiel`, `_build_prof_system` → absorbés dans `ProjectContext`.

**Routes à mettre à jour :**
- `cadrage_router.py` → ajouter `project_id: str = Query(None)` au SSE endpoint → passer à `sse_chat_generator`
- `cadrage_alt.html` → lire `session.project_id` depuis localStorage → ajouter `&project_id=` à l'URL SSE

**Fichiers à lire :**
- `Backend/Prod/retro_genome/brainstorm_logic.py` — L247-370 (sse_chat_generator + helpers M220)
- `Frontend/3. STENCILER/routers/cadrage_router.py`
- `Frontend/3. STENCILER/static/templates/cadrage_alt.html` — `startStreaming()`

**Fichiers à créer/modifier :**
- `Backend/Prod/retro_genome/project_context.py` — **créer**
- `Backend/Prod/retro_genome/brainstorm_logic.py` — remplacer helpers par `ProjectContext`
- `Frontend/3. STENCILER/routers/cadrage_router.py` — ajouter `project_id` param

**Règle fallback (CRITIQUE) :**
- Si `project_id` absent → utiliser `default` comme project_id (projet HoméOS de référence)
- Si `role === 'prof'` → jamais bloqué, toujours un contexte disponible
- Le prof visitant une classe (`class_id` présent) reçoit le sujet de la classe en contexte, même sans project_id personnel

**Livrable :**
1. Tout appel Sullivan reçoit le manifest + genome + PRD + design en contexte
2. Mode prof : sujet DNMADE + référentiel inclus automatiquement, fallback `default` si pas de projet actif
3. Mode élève : idem + manifest Stitch de son projet
4. Un seul endroit à maintenir pour enrichir le contexte de tous les LLM
5. Plus jamais de "veuillez activer un projet" pour le prof

## Thème 25 — Stitch UX

---

### S1 — Panel Stitch : overflow coupé + formulaire toujours caché
**STATUS: ✅ CODE DIRECT | DATE: 2026-04-08 | ACTOR: CLAUDE**

- `WsStitch.js` : branches `!res.ok` et `!data.linked` appellent maintenant `showManualForm()` — le formulaire ID est visible dès l'ouverture si pas de session liée
- `workspace.html` : `#panel-stitch` → `max-height: calc(100vh - 96px); flex-direction: column` / `#stitch-content` → `overflow-y: auto; flex: 1` (plus de `max-h-[60vh]`)

---

---

### M227 — Isolation projet par session utilisateur (critique)
**STATUS: ✅ LIVRÉ**

- `bkd_service.get_active_project_id(token)` : si token élève → résout `students.project_id` depuis DB, sinon fallback `active_project.json`
- `bkd_service.set_active_project_id(pid, token)` : si token élève → met à jour DB `students.project_id`
- `projects_router.activate_project` : lit `X-User-Token` → passe au setter
- `bootstrap.js` : project switcher masqué pour `role === 'student'`
- `workspace.html` : activation XHR inclut `X-User-Token`

**Résultat :** Chaque élève voit TOUJOURS son propre projet, même si le prof navigue en même temps sur un autre.
- `Frontend/3. STENCILER/static/templates/workspace.html` — XHR activation L43-55
- `Frontend/3. STENCILER/static/js/bootstrap.js` — `injectNav()`, project switcher

**Livrable :**
1. Hugo ouvre le workspace → son projet, même si le prof a switché entre-temps
2. Hugo ne voit pas le project switcher dans la nav
3. Le prof garde l'accès à tous les projets

---

---

### S3 — Stitch MCP : utiliser la clé API de FJD pour tous les élèves
**STATUS: ✅ LIVRÉ**

- `_get_stitch_key()` dans `stitch_router.py` : lit d'abord `STITCH_API_KEY` depuis l'env, puis fallback sur `user_keys` (admin/prof)
- Toutes les routes stitch utilisent `_get_stitch_key()` au lieu de `STITCH_API_KEY`
- Tous les `StitchClient()` reçoivent `api_key=_get_stitch_key()`
- `GET /api/stitch/status` retourne `connected: true` si la clé est dans `user_keys` (même sans `.env`)

---

---

### M232 — Refonte layout workspace : dashboard projet + nettoyage toolbar
**STATUS: ✅ LIVRÉ (Qwen full stack) | DATE: 2026-04-08**

> BOOTSTRAP OBLIGATOIRE

**Fichiers à lire en entier :**
- `Frontend/3. STENCILER/static/templates/workspace.html` — structure complète panels gauche + toolbar droite
- `Frontend/3. STENCILER/static/js/workspace/ws_main.js` — `fetchWorkspaceImports()`
- `Frontend/3. STENCILER/static/css/workspace.css`

**Garder tous les IDs existants des éléments fonctionnels. Ne pas toucher à Sullivan chat ni au canvas.**

---

**C. Nettoyage toolbar droite**

Dans `workspace.html`, toolbar `<nav class="absolute top-1/2 right-8...">`, garder uniquement :

| Outil | Action | Garder |
|-------|--------|--------|
| Select (V) | sélection canvas | ✅ |
| Drag (H) | pan canvas | ✅ |
| Typographie (T) | `#btn-ws-typo` | ✅ |
| Couleur (C) | `#ws-color-panel` — conditionné DESIGN.md | ✅ |
| Stitch (S) | logo Stitch → ouvre panel Stitch | ✅ NOUVEAU |
| Place Image (I) | stitch fait mieux | ❌ supprimer |
| Frame (F) | non fonctionnel | ❌ supprimer |
| Effets (E) | FEE Studio remplace | ❌ supprimer |

Bouton Stitch dans toolbar : icône logo Stitch (ou "S" en attendant) → `window.wsStitch?.toggle()`.

---

---

### M231 — Pipeline d'import multi-source : PNG / SVG / Illustrator / Figma plugin / Stitch
**STATUS: 🟠 PRÊTE | DATE: 2026-04-08**

**Contexte :**
Un élève arrive avec ses maquettes depuis différentes sources. Toutes convergent vers `projects/{id}/imports/`. Le reste du workflow (Wire → Forge → Sullivan) est identique quelle que soit la source.

**Sources à supporter :**

| Source | Format | Mécanisme |
|--------|--------|-----------|
| PNG / JPG | image | Upload direct → stocké dans `imports/` comme asset visuel |
| SVG | vecteur | Upload direct → utilisable dans le canvas SVG natif |
| Illustrator | SVG (export) | L'élève exporte en SVG depuis Illustrator → même pipeline que SVG |
| Figma plugin HoméOS | JSON + PNG | Le plugin pousse vers `POST /api/import/figma` → normalisation → `imports/` |
| Stitch | HTML | `POST /api/stitch/pull` → déjà opérationnel ✅ |

**Ce qu'il faut :**

**Backend — `import_router.py` (ACTOR: QWEN) :**

Route `POST /api/import/upload` — upload générique :
```python
@router.post("/import/upload")
async def import_upload(file: UploadFile, request: Request):
    # Accepte : .png, .jpg, .svg, .ai (SVG exporté)
    # Sauvegarde dans projects/{active_id}/imports/{filename}
    # Enregistre dans exports/index.json (même pipeline que Stitch)
    # Retourne { "filename": "...", "type": "png|svg", "path": "..." }
```

Route `POST /api/import/figma` — payload plugin Figma HoméOS :
```python
@router.post("/import/figma")
async def import_figma(request: Request):
    # Body: { "screen_name": str, "png_base64": str, "metadata": {} }
    # Décode le PNG → sauvegarde dans imports/figma_{screen_name}.png
    # Sauvegarde metadata dans imports/figma_{screen_name}.json
    # Retourne { "filename": "...", "imported": true }
```

**Frontend — zone d'import dans le workspace (ACTOR: GEMINI) :**

Dans le panel gauche du workspace (section écrans/imports), ajouter une zone "importer" :
```
┌─────────────────────────────┐
│  importer des maquettes     │
│                             │
│  [↑ PNG / SVG]  [Figma]     │
│  [Stitch →]                 │
│                             │
│  ou glisser-déposer ici     │
└─────────────────────────────┘
```

- Bouton "PNG / SVG" → `<input type="file" accept=".png,.jpg,.svg">` → `POST /api/import/upload`
- Bouton "Figma" → instructions pour le plugin (lien doc)
- Bouton "Stitch →" → ouvre le panel Stitch existant
- Drag & drop → même route

**Livrable :**
1. Un élève peut uploader un PNG ou SVG → apparaît dans `imports/` + liste du workspace
2. Le plugin Figma peut envoyer un écran → même résultat
3. Stitch reste la voie principale pour les aller-retours live

---

---

### M230 — Workflow Stitch complet : push/pull/sync élève
**STATUS: ✅ LIVRÉ (Qwen full stack) | DATE: 2026-04-08**

**Backend livré :**
- `run_stitch_push_task()` extrait `project_id` depuis `screen_name` → `_patch_manifest_stitch_project_id()`
- `POST /api/stitch/sync` — compare écrans Stitch vs imports locaux → pull les nouveaux
- `GET /api/stitch/open/{screen_id}` — retourne URL Stitch `https://stitch.google.com/p/{pid}/s/{sid}`
- Premier push → `stitch_project_id` mémorisé dans manifest → `stitch_url` retourné au frontend

**Workflow cible :**
```
1. PREMIER PUSH
   Élève clique "modifier dans Stitch" sur un écran HoméOS
   → POST /api/stitch/push (Sullivan + genome + DESIGN.md)
   → generate_screen_from_text → Stitch crée l'écran → retourne screen_name
   → Extraire project_id depuis screen_name ("projects/{pid}/screens/{sid}")
   → Sauvegarder manifest.json : stitch_project_id = pid
   → Ouvrir https://stitch.google.com/p/{pid}/s/{sid} dans nouvel onglet

2. PUSHES SUIVANTS
   → Même stitch_project_id (lu depuis manifest)
   → edit_screen si écran existant, generate_screen_from_text si nouveau

3. PULL / SYNC (Stitch → HoméOS)
   → window.onfocus : retour depuis Stitch → déclenche sync auto
   → Polling toutes les 5min (si Stitch lié)
   → Bouton "synchroniser" manuel
   → Logique : diff écrans Stitch vs imports locaux → pull des nouveaux/modifiés

4. TOOLBAR CANVAS
   → Bouton "modifier dans Stitch" → push Sullivan → ouvre Stitch
   → Bouton "importer de Stitch" → pull forcé

5. PANEL STITCH — liste des écrans
   Pour chaque écran :
   [œil] ouvrir dans HoméOS  [S] ouvrir dans Stitch  [↻] pull cet écran
   En-tête : titre projet (collapsible) + [↻ synchroniser tout]
```

**ACTOR QWEN — Backend :**

A. Dans `run_stitch_push_task()` après succès : extraire `project_id` depuis `screen_name` → `_patch_manifest_stitch_project_id(pid)`.

B. Route `POST /api/stitch/sync` :
```python
@router.post("/sync")
async def stitch_sync(request: Request):
    # Lit stitch_project_id depuis manifest
    # Appelle stitch_session() pour avoir la liste live
    # Pour chaque écran non local → pull (réutilise la logique de /pull)
    # Retourne { "pulled": [...], "already_local": [...] }
```

C. Route `GET /api/stitch/open/{screen_id}` :
```python
@router.get("/open/{screen_id}")
async def stitch_open_url(screen_id: str):
    # Retourne { "url": "https://stitch.google.com/p/{pid}/s/{screen_id}" }
```

Fichiers : `stitch_router.py`, `stitch_client.py`

---

---

### M228 — Stitch : UX élève intelligible
**STATUS: ✅ ABSORBÉE PAR M230 | DATE: 2026-04-08**

## Thème 24 — Fix activation projet élève (Hugo)

---

### P1 — Student project : activation end-to-end cassée
**STATUS: ✅ LIVRÉ (Qwen) | DATE: 2026-04-07 | ACTOR: QWEN**

**Symptôme :** Hugo se connecte → workspace affiche le projet `default` (templates) au lieu de son espace vide.

**Diagnostic à faire :**
L'élève Hugo (`student_id: dumont-hugo`, `class_id: dnamde3`) a un projet existant sur disque.
Tracer le flow complet et trouver où ça casse :

1. `POST /api/auth/login-student` body `{ "class_id": "dnamde3", "student_id": "dumont-hugo" }`
   - Retourne-t-il un `project_id` non-null ?
   - Écrit-il bien `active_project.json` ?

2. `POST /api/projects/activate` body `{ "id": "<project_id>" }`
   - Le projet est-il dans la table `projects` de la DB ?
   - Si non → le code doit l'auto-enregistrer (fix déjà dans `projects_router.py`) et continuer.
   - Retourne-t-il 200 ou 404 ?

3. `bkd_service.get_active_project_id()` — lit depuis la variable globale `_ACTIVE_PROJECT_ID` OU depuis `active_project.json` ?
   - Si la variable globale n'est pas mise à jour (ex: deux imports différents du module), `get_active_project_path()` retourne le mauvais projet.

**Fichiers à lire :**
- `Frontend/3. STENCILER/bkd_service.py` — `get_active_project_id()`, `set_active_project_id()`, `get_active_project_path()`
- `Frontend/3. STENCILER/routers/projects_router.py` — `activate_project()`, `set_active_project_id()`
- `Frontend/3. STENCILER/server_v3.py` — comment `set_active_project_id` est importé/exposé
- `Frontend/3. STENCILER/routers/auth_router.py` — `auth_login_student()` L363-408

**Problème probable :**
`projects_router.py` importe `set_active_project_id` depuis `bkd_service` et met à jour la variable globale dans ce module.
Mais `bkd_service.get_active_project_id()` lit `_ACTIVE_PROJECT_ID` depuis son propre module.
Si `server_v3.py` réexporte `set_active_project_id` sous un autre alias, ou si les routers importent depuis des modules différents → la variable globale est dans un namespace différent → la mise à jour ne se propage pas.

**Fix attendu :**
- S'assurer que `set_active_project_id` dans `projects_router.py` modifie bien la variable globale de `bkd_service` (pas une copie locale).
- OU : rendre `get_active_project_id()` dans `bkd_service` lire depuis `active_project.json` au lieu de la variable globale (plus robuste — pas de problème de namespace).
- ET : s'assurer que `projects/activate` auto-enregistre le projet si absent de la DB (code déjà ajouté — vérifier qu'il est correct).

**Livrable :**
Hugo se connecte → workspace vide (son projet propre, sans templates).

## Thème 22 — Fixes login & workspace élève

---

### F1 — Login : activation projet élève au login + logout visible
**STATUS: ✅ LIVRÉ | DATE: 2026-04-07 | ACTOR: QWEN (backend) + GEMINI (frontend)**

---

---

### F3 — Éditeur sujet : frontend manquant (M223 backend ✅, UI absente)
**STATUS: ✅ LIVRÉ | DATE: 2026-04-07 | ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE

```
CONTEXTE TECHNIQUE OBLIGATOIRE — lis avant de coder :

1. DIAGNOSTIC DOM AVANT LISTENER
   Avant d'ajouter un event listener, remonte la chaîne du DOM.

2. RÈGLE DE LIVRAISON
   Ne pas marquer TERMINÉ avant d'avoir testé manuellement dans le browser.

3. SCOPE STRICT
   Ne modifier que teacher_dashboard.html. Ne pas toucher aux autres fichiers.

4. STYLE HOMÉOS
   Même CSS que le dashboard existant. Pas de majuscules. Pas d'emojis.
   Tokens : bg #f7f6f2, text #3d3d3c, accent #8cc63f, border #e5e5e5.
   border-radius: 4px max. Font: Geist, -apple-system.
   Hard-edge : pas de border-radius sur le formulaire principal (0px).
```

**Fichier à lire en ENTIER :**
`Frontend/3. STENCILER/static/templates/teacher_dashboard.html`

**Routes backend disponibles (déjà implémentées) :**
- `GET /api/classes/{class_id}/subjects` — liste des sujets
- `GET /api/classes/{class_id}/subjects/{subject_id}` — sujet complet
- `POST /api/classes/{class_id}/subjects` — créer sujet
- `PUT /api/classes/{class_id}/subjects/{subject_id}` — modifier sujet

**Structure JSON d'un sujet (référence pour les formulaires) :**
```json
{
  "id": "contraintes-peruquiennes",
  "title": "Contraintes Péruquiennes",
  "problematique": "Comment...",
  "contexte": "Dans le cadre de...",
  "parties": [
    { "id": "p1", "titre": "Recherche", "description": "...", "duree": "2 semaines" }
  ],
  "livrables": ["Maquette Figma", "Export HTML"],
  "evaluation": {
    "modalite": "Soutenance orale",
    "criteres": [
      { "competence": "A1", "libelle": "Analyse du contexte", "poids": 30 }
    ]
  },
  "competences": ["A1", "A2", "B1"]
}
```

**Ce qu'il faut implémenter dans `teacher_dashboard.html` :**

**1. Bouton "modifier" dans chaque ligne de la table sujets**

Dans `renderSubjects()`, chaque ligne doit avoir un bouton "modifier" :
```js
'<td><button class="btn-action" onclick="editSubject(\'' + s.id + '\')">modifier</button></td>'
```
Ajouter une 5e colonne `<th></th>` dans le thead.

**2. Drawer de formulaire (panel latéral ou modal)**

Un `<div id="subject-form-panel">` positionné en `position: fixed; right: 0; top: 48px; bottom: 0; width: 420px` (drawer droite, s'ouvre par-dessus le contenu).
Style : `background: #f7f6f2; border-left: 1px solid #e5e5e5; overflow-y: auto; padding: 24px; z-index: 500;`
Caché par défaut : `transform: translateX(100%); transition: transform 0.25s ease`.
Ouvert : `transform: translateX(0)`.

**3. Formulaire en 5 sections dans le drawer**

Section 1 — En-tête :
```html
<div class="sf-section">
  <div class="sf-section-label">en-tête</div>
  <label>titre</label>
  <input type="text" id="sf-title" placeholder="Contraintes Péruquiennes">
  <label>problématique</label>
  <textarea id="sf-problematique" rows="2"></textarea>
  <label>contexte</label>
  <textarea id="sf-contexte" rows="3"></textarea>
</div>
```

Section 2 — Parties (liste dynamique) :
- Bouton "+ partie" → append une ligne `{ titre | description | durée | × }`
- Bouton × → remove la ligne
- IDs générés dynamiquement `sf-party-N`

Section 3 — Livrables (liste dynamique) :
- Bouton "+ livrable" → append `<input type="text">` + bouton ×

Section 4 — Évaluation :
- `<input id="sf-modalite" placeholder="Soutenance orale">`
- Tableau critères : colonnes `compétence DNMADE | libellé | poids %`
- Bouton "+ critère" → append ligne avec `<select>` des compétences DNMADE (A1, A2, A3, B1, B2, C1, C2, C3, D1, D2) + input libellé + input number poids
- Ligne total : `Σ poids = X%` (recalculé à chaque changement)

Section 5 — Compétences DNMADE :
- Checkboxes : A1, A2, A3 / B1, B2 / C1, C2, C3 / D1, D2
- Groupées par domaine avec label discret

Bouton "enregistrer" (`.btn-create`) en bas du drawer.
Bouton "annuler" (`.btn-action`) → ferme le drawer.

**4. Fonctions JS à implémenter**

```js
var subjectFormMode = null; // 'create' ou 'edit'
var editingSubjectId = null;

function openSubjectForm(mode, subjectData) {
    subjectFormMode = mode;
    editingSubjectId = subjectData ? subjectData.id : null;
    // Remplir le formulaire si subjectData présent, sinon vider
    fillSubjectForm(subjectData || {});
    document.getElementById('subject-form-panel').style.transform = 'translateX(0)';
}

function closeSubjectForm() {
    document.getElementById('subject-form-panel').style.transform = 'translateX(100%)';
}

function editSubject(subjectId) {
    fetch(API + '/' + currentClassId + '/subjects/' + subjectId)
        .then(function(r) { return r.json(); })
        .then(function(data) { openSubjectForm('edit', data); });
}

function saveSubjectForm() {
    var payload = collectFormData(); // lit tous les champs
    var url = API + '/' + currentClassId + '/subjects' + (subjectFormMode === 'edit' ? '/' + editingSubjectId : '');
    var method = subjectFormMode === 'edit' ? 'PUT' : 'POST';
    fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(function(r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
    .then(function() { closeSubjectForm(); loadSubjects(currentClassId); })
    .catch(function(e) { alert('erreur: ' + e.message); });
}
```

**5. Modifier `createSubject()`**

Remplacer la redirection vers `/cadrage` par :
```js
function createSubject() {
    if (!currentClassId) return;
    openSubjectForm('create', null);
}
```

**Livrable attendu :**
1. Clic "+ sujet" → drawer s'ouvre à droite, formulaire vide
2. Clic "modifier" sur un sujet → drawer s'ouvre pré-rempli avec les données
3. "enregistrer" → POST ou PUT selon le mode → tableau sujets rafraîchi
4. "annuler" → drawer se ferme
5. Pas d'erreur console

**Bugs constatés :**
1. Élève connecté (ex: Hugo) → workspace affiche le projet `default` (templates) au lieu de son projet isolé — `active_project.json` n'est pas mis à jour au login
2. Pas de bouton logout visible — seul le drawer settings (icône engrenage) permet de se déconnecter, trop caché pour une classe

**Fix 1 — Backend : route `POST /api/auth/login-student` doit activer le projet**

Dans `auth_router.py`, après avoir résolu `project_id` :
```python
# Activer le projet de l'élève immédiatement
if project_id:
    active_file = ROOT_DIR / "active_project.json"
    active_file.write_text(json.dumps({"active_id": project_id}), encoding='utf-8')
```

Fichier : `Frontend/3. STENCILER/routers/auth_router.py` — route `POST /api/auth/login-student`

**Fix 2 — Frontend login.html : forcer activation avant redirect**

Dans `loginStudent()`, après `saveSession(data)` :
```js
// Toujours activer le projet avant de rediriger
if (projectId) {
    await fetch('/api/projects/activate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: projectId })
    });
    window.location.href = `/workspace?project_id=${projectId}`;
}
```
Fichier : `Frontend/3. STENCILER/static/templates/login.html`

**Fix 3 — Logout visible dans le nav**

Dans `bootstrap.js`, dans `injectNav()`, ajouter un bouton logout discret dans `hn-actions` à côté du user pill :
```js
const logoutBtn = document.createElement('button');
logoutBtn.className = 'hn-logout';
logoutBtn.textContent = 'quitter';
logoutBtn.onclick = () => {
    localStorage.removeItem('homeos_session');
    window.location.href = '/login';
};
actions.appendChild(logoutBtn);
```
CSS dans `homeos-nav.css` :
```css
#homeos-global-nav .hn-logout {
    font-size: 9px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.08em; color: #ccc; background: none; border: none;
    cursor: pointer; padding: 2px 6px; transition: color 0.15s;
}
#homeos-global-nav .hn-logout:hover { color: #ef4444; }
```

**Fichiers à lire :**
- `Frontend/3. STENCILER/routers/auth_router.py` — `login-student`
- `Frontend/3. STENCILER/static/templates/login.html` — `loginStudent()`
- `Frontend/3. STENCILER/static/js/bootstrap.js` — `injectNav()`
- `Frontend/3. STENCILER/static/css/homeos-nav.css`

**Livrable :**
1. Hugo se connecte → workspace vide (son projet isolé, pas default)
2. Bouton "quitter" visible dans le nav sur toutes les pages
3. Clic → `localStorage` vidé → `/login`

## Thème 20 — Sujet DNMADE structuré

---

### M223 — Éditeur de sujet : format structuré + parties + livrables + évaluation
**STATUS: ✅ LIVRÉ (backend)**

**Backend (`class_router.py`) :**
- `SubjectCreateRequest` enrichi : `problematique`, `contexte`, `parties[]`, `livrables[]`, `evaluation{modalite, criteres[]}`, `competences[]`
- `POST /{class_id}/subjects` — création format structuré complet
- `GET /{class_id}/subjects/{subject_id}` — lecture d'un sujet par ID
- `PUT /{class_id}/subjects/{subject_id}` — mise à jour complète (préserve id + created_at)

**Frontend (`teacher_dashboard.html`) :**
- Tableau sujets : colonne "details" ajoutée (nb parties + nb livrables)
- Affichage `problematique` si `description` vide (rétrocompatibilité)

**Format JSON produit :**
```json
{
  "id": "design-sonore-et-interface",
  "class_id": "dnmade1-2026",
  "title": "Design Sonore et Interface",
  "problematique": "Comment le son peut-il enrichir une interface numérique ?",
  "contexte": "Dans le cadre du studio DNMADE 2ème année...",
  "parties": [{"id": "p1", "titre": "...", "description": "...", "duree": "..."}],
  "livrables": ["Dossier PDF", "Prototype", "Présentation"],
  "evaluation": {"modalite": "Jury DNMADE", "criteres": [{"competence": "A1", "libelle": "...", "poids": 30}]},
  "competences": ["A1", "C2", "C3"]
}
```

**Note :** Frontend UI d'édition modale (formulaire structuré 5 sections) à implémenter par Gemini.

---

---

### Mission 257 — Forge PNG : validation genai SDK + fidélité du rendu
**STATUS: ✅ LIVRÉ | ACTOR: QWEN | DATE: 2026-04-08**

- SDK `google-genai` installé (v1.70.0) et testé — `gemini-3.1-flash-lite-preview` répond OK
- `gemini_client.py` : `_generate_with_image_genai()` pour modèles 3.x, REST API pour modèles stables
- `generate_with_image()` route automatiquement selon le nom du modèle (détection "preview")
- `svg_to_tailwind.py` : `convert_image()` accepte `design_md` optionnel, injecté dans le prompt
- `routes.py` : séquence A (analyse) → B (save DESIGN.md) → C (forge avec DESIGN.md)

**Note :** Le serveur a été tué (`killed`) avant qu'une forge PNG ne soit validée end-to-end avec le nouveau code. À retester au prochain redémarrage.

---

---

### Mission 258 — Drag d'éléments dans l'iframe : fix `elementFromPoint` React
**STATUS: ✅ LIVRÉ | ACTOR: QWEN | DATE: 2026-04-08**

- Remplacé `document.elementFromPoint(x, y)` par `document.elementsFromPoint(x, y)` (retourne TOUS les éléments au point, pas juste le premier)
- Fonction `_findElementAtPoint(x, y)` filtre les wrappers React (`#root`, `#__next`, etc.)
- Accepte le premier élément qui a : un id significatif, une classe CSS, du texte, ou est un élément sémantique
- Fonctionne pour les bundles React (traverse le shadow DOM des conteneurs) ET le HTML statique

## Thème 25 — Refactorisation ws_main.js : modules isolés + boot ordonné

> Objectif : éliminer les 7 catégories de bugs récurrents (état undefined, race conditions, crash en cascade, IDs manquants, pointer-events, IDs API erronés, double-binding).
> **Règle :** zéro classe, zéro import complexe. Fonctions pures + IIFE. Chaque fichier expose `window.WsXxx` avec traces console.

---

### Mission 250 — WsState : état global unique, tracé en console
**STATUS: 🟠 À TRAITER | ACTOR: QWEN**
- Centralise `projectId`, `activeMode`, `session` en un seul objet
- Résout le projet depuis `localStorage.homeos_session` (plus besoin de `wsBackend`)
- Traces : `[WsState] init`, `[WsState] projectId=xxx`, `[WsState] session.role=xxx`
- Fichier : `static/js/workspace/WsState.js`

---

### Mission 251 — WsBoot : séquence d'init isolée, try/catch par composant
**STATUS: 🟠 À TRAITER | ACTOR: QWEN**
- Remplace le bloc `async function initWorkspace()` de ws_main.js
- Boot explicite étape par étape : Audit → Forge → Preview → Canvas → Chat → Wire → FEEStudio
- Chaque étape dans `bootSafe(nom, fn)` — si crash, log clair + continue
- Traces : `[WsBoot] ✅ WsAudit OK (12ms)`, `[WsBoot] ❌ WsChatMain: <erreur>`
- Fichier : `static/js/workspace/WsBoot.js`

---

### Mission 252 — wsDom : utilitaires DOM sécurisés
**STATUS: 🟠 À TRAITER | ACTOR: QWEN**
- `safeEl(id)` — getElementById avec warning si absent
- `safeClick(selector, handler)` — addEventListener silencieux si absent
- Traces : `[wsDom] ⚠ #xxx not found`, `[wsDom] ✓ .btn click wired`
- Fichier : `static/js/workspace/wsDom.js`

---

### Mission 253 — WsImportList : extraction template + handlers imports
**STATUS: 🟠 À TRAITER | ACTOR: QWEN**
- Extrait `fetchWorkspaceImports()` et son template HTML (80+ lignes)
- Boutons [👁] [S] [↻] [×] avec handlers propres
- Traces : `[WsImportList] 5 imports`, `[WsImportList] [S] clicked`
- Fichier : `static/js/workspace/WsImportList.js`

---

### Mission 254 — WsAssetPicker : extraction gestion assets
**STATUS: 🟠 À TRAITER | ACTOR: QWEN**
- `toggleImagePicker()`, `fetchProjectAssets()`, `copyAssetUrl()`, `deleteAsset()`
- Traces : `[WsAssetPicker] opened`, `[WsAssetPicker] 3 assets`
- Fichier : `static/js/workspace/WsAssetPicker.js`

---

### Mission 255 — ws_main.js final : ~120 lignes d'orchestration
**STATUS: 🟠 À TRAITER | ACTOR: QWEN**
- Après extraction : boot + wiring toolbar + mode buttons uniquement
- Traces : `[ws_main] toolbar 7 buttons`, `[ws_main] ✅ READY`
- Fichier : `static/js/workspace/ws_main.js` (réécrit)


<!-- Les phases validées sont archivées ici par Claude après validation de François-Jean -->

---

## M304 — DB comme seule source de vérité pour le projet actif
**STATUS: ✅ LIVRÉ | DATE: 2026-04-14 | ACTOR: Claude CODE DIRECT**

- WAL mode SQLite + `PRAGMA synchronous=NORMAL` (`bkd_service.py` L162) — confirmé `journal_mode: wal`
- `bkd_router.py` L411 + `stitch_router.py` L35 — migrés vers `bkd_db()` (zéro leak restant)
- `GET /api/projects/active` token-aware (`projects_router.py` L143) — chaque élève voit son projet
- `POST /api/projects/activate` met à jour `students.project_id` via pattern LIKE sans token (`projects_router.py` L179) — le dashboard prof écrit directement en DB

## M302 — Groq wrapper : injection de fichiers dans le contexte
**STATUS: ✅ LIVRÉ | DATE: 2026-04-13 | ACTOR: GEMINI**

- `sys.argv[1:]` → lecture fichiers → blocs `=== FICHIER : {path} ===`
- Injection via `history.append` avant la boucle REPL
- 70L (< 80L contrainte respectée)

## M301 — Teacher Dashboard : freeze sur chargement répété
**STATUS: ✅ LIVRÉ | DATE: 2026-04-13 | ACTOR: GROQ**

- Fix A : batch `executemany` pour les UPDATE milestones dans `class_router.py` L457-473
- Fix B : guard `_loadDashboardPending` dans `teacher_dashboard.html` L284/337/340/358

## M300 — Serveur : stabilisation reload=False + restart propre
**STATUS: ✅ LIVRÉ | DATE: 2026-04-13 | ACTOR: Claude**

- `reload=False` était pré-appliqué dans `server_v3.py` L244
- Serveur relancé : `nohup python3 server_v3.py > /tmp/server_v3.log 2>&1 &`
- Vérifié : `GET /api/classes` → JSON valide, port 9998 actif

## M266 — "Envoyer au Cadrage" depuis le workspace
**STATUS: ✅ LIVRÉ | DATE: 2026-04-09 | ACTOR: GEMINI**

- Bouton "discuter dans le cadrage →" dans l'overlay post-forge
- `forge_context` stocké en `sessionStorage` au clic
- `cadrage_alt.html` lit le contexte au load → amorce automatique Sullivan
- `cadrage_router.py` injecte le contexte forge dans le system prompt

## M267 — Persistance d'état cross-tabs
**STATUS: ✅ LIVRÉ | DATE: 2026-04-09 | ACTOR: QWEN**

- Conversation Cadrage persistée en `sessionStorage.cadrage_history`
- Forge active : `{ job_id, import_id }` en sessionStorage → polling repris au retour workspace
- Screen list : re-fetch au montage si liste vide (comportement déjà correct)

## M268 — Sullivan Arbiter : boutons "Générer PRD" et "Générer Manifest"
**STATUS: ✅ LIVRÉ | DATE: 2026-04-09 | ACTOR: GEMINI**

- `POST /api/sullivan/prd` → sauvegarde `PRD_{timestamp}.md` dans exports projet
- `POST /api/sullivan/manifest` → génère/met à jour `manifest.json`
- Bindings câblés dans `ws_main.js` / `WsBootstrap.js`

## M269 — ManifestBox : drawer manifest persistant cross-tabs
**STATUS: ✅ LIVRÉ | DATE: 2026-04-09 | ACTOR: GEMINI**

- `ManifestBox.js` créé — drawer `[M]` dans le nav global (toutes les pages)
- Charge `GET /api/projects/active/manifest` au show()
- JSON éditable + bouton "sauvegarder" → `POST /api/manifest/save`
- Import fichier `.json` externe → sauvegardé + pris en base par Sullivan
- Boutons "envoyer au Wire" et "discuter dans le cadrage" fonctionnels
- État open/closed persisté en `localStorage`

## M270 — Activation projet depuis la session si pas d'URL param
**STATUS: ✅ LIVRÉ | DATE: 2026-04-09 | ACTOR: QWEN**

- `workspace.html` : `pid = params.get('project_id') || session.project_id`
- Même fix appliqué dans `cadrage_alt.html` et `bkd_frd.html`
- Chaque élève voit son propre projet quel que soit l'ordre de connexion

---

## M275 — BYOK : Pricing badges + Enter-to-submit + Delete keys
**STATUS: ✅ LIVRÉ | DATE: 2026-04-10 | ACTOR: QWEN**

- Pricing badges dans settings drawer : vert = gratuit, orange = payant
- 5 gratuits (gemini, groq, mimo, qwen, watson) + 3 payants (openai, kimi, deepseek)
- Toucher Entrée sur un champ clé → sauvegarde instantanée (bordure verte)
- Bouton × rouge sur les clés actives → suppression avec confirmation
- `DELETE /api/me/keys/{provider}` endpoint ajouté
- `api_key_urls.py` : 8/8 URLs validées + cache 24h

## M276 — Stitch sync : bouton actualiser + pull écrans via MCP
**STATUS: ✅ LIVRÉ | DATE: 2026-04-10 | ACTOR: QWEN**

- Bouton ↻ "actualiser depuis stitch" en haut de la screen list
- `POST /api/stitch/sync` → `list_screens` MCP → pull HTML → update `index.json`
- Retourne `+N écran(s) syncés` → auto-refresh

## M277 — Stitch toolbar button + S button sur chaque écran
**STATUS: ✅ LIVRÉ | DATE: 2026-04-10 | ACTOR: QWEN**

- Bouton Stitch dans la toolbar → génère mega-prompt basé sur manifest
- Méga-prompt copié dans le clipboard + toast + Stitch ouvert
- Blocage 400 si aucun manifest — alert "génère d'abord un manifest"
- Bouton [S] sur chaque row de la screen list
- `create-project` appelle MCP `create_project` (~0.8s) → vrai projet Stitch créé
- `stitch_project_id` stocké dans le manifest

## M278 — Cross-platform paths : éliminer les chemins en dur
**STATUS: ✅ LIVRÉ | DATE: 2026-04-10 | ACTOR: QWEN**

- Remplacement de tous les chemins `/Users/francois-jeandazin/AETHERFLOW/...` par des constantes relatives
- `ROOT_DIR`, `TEMPLATES_DIR`, `ACTIVE_PROJECT_FILE`, `PROJECTS_DIR`
- Forge fonctionne sur macOS (local) et Linux (HF container)
- `routes.py` + `svg_to_tailwind.py` fixés

## M281 — Sync Stitch : polling 2min + toast + auto-pull
**STATUS: ✅ LIVRÉ | DATE: 2026-04-10 | ACTOR: QWEN**

- `WsStitchSync.js` : polling `/api/stitch/sync` toutes les 2 min (max 8 polls/session = 16 min)
- Toast "Nouveau screen Stitch détecté" quand le nombre d'écrans augmente
- Arrêt auto si pas de `stitch_project_id` lié (400)
- Refresh auto de la screen list après détection
- Démarrage polling : après drill Stitch OU au workspace ready

## M280 (partiel) — WsStitchDrill : landing canvas + drill 3 étapes
**STATUS: ✅ LIVRÉ | DATE: 2026-04-10 | ACTOR: QWEN**

- Bouton rond vert pulsant "Créer un projet" sur canvas vide (z-index 99999, backdrop blur 3px)
- Étape 1 : Upload manifest (.json/.md/.txt) — bloquant, drag&drop ou click
- Étape 2 : Clés API — cascade fallback expliquée + lien vers paramètres
- Étape 3 : "Charger sur Stitch" → crée projet Stitch via MCP + ouvre Stitch + progress bar
- Démarrage polling auto après drill

---

## M233 — Backend : PATCH /api/imports/{import_id}
**STATUS: ✅ LIVRÉ | DATE: 2026-04-08 | ACTOR: QWEN**

- Route `PATCH /api/imports/{import_id}` dans `import_router.py`
- Merge les champs du body JSON dans l'entrée `index.json` du projet actif
- `from fastapi import Body` ajouté

---

## M234 — Frontend : forge → update liste + suppression panel Stitch
**STATUS: ✅ LIVRÉ | DATE: 2026-04-08 | ACTOR: QWEN + CODE DIRECT**

- `WsForge.js` : après `job.status === 'done'` → `PATCH /api/imports/{importId}` avec `{ html_template, type: 'html' }` → refresh liste
- `ws_main.js` : bouton [S] conditionnel — affiché uniquement si `archetype_id === 'stitch_import'` ou `archetype_label` contient "stitch"
- `workspace.html` : suppression de `#section-stitch` (panel + badge) + script WsStitch
- `ws_main.js` : suppression de l'instanciation WsStitch, retrait de `panel-stitch` du PanelDragger

---

## F2 — Projet élève : création automatique depuis le sujet actif
**STATUS: ✅ LIVRÉ | DATE: 2026-04-07 | ACTOR: CLAUDE (CODE DIRECT)**

- `create_student_project()` charge le dernier sujet de la classe → nomme le projet `{class_id}-{student_id}-{subject_slug}`
- **INSERT OR IGNORE dans la table `projects`** → `get_active_project_path()` trouve le projet (plus de fallback `default`)
- `/start` route : enregistre aussi les projets existants sur disque mais absents de la DB
- Helper `_get_active_subject_title()` ajouté

Fichier : `Frontend/3. STENCILER/routers/class_router.py`

---

## F3 — Éditeur sujet dashboard prof
**STATUS: ✅ LIVRÉ | DATE: 2026-04-07 | ACTOR: GEMINI**

- Drawer fixe droite (`position: fixed; right: 0; top: 48px; width: 420px`) — slide in/out
- Formulaire 5 sections : en-tête, parties (dynamique), livrables (dynamique), évaluation (critères DNMADE + poids), compétences (checkboxes A1-D2)
- `editSubject(id)` → `GET /api/classes/{class_id}/subjects/{id}` → pré-remplit le formulaire
- `createSubject()` → ouvre le drawer vide (plus de redirection vers /cadrage)
- `saveSubjectForm()` → POST (création) ou PUT (modification) selon le mode
- Bouton "modifier" dans chaque ligne du tableau sujets

Fichier : `Frontend/3. STENCILER/static/templates/teacher_dashboard.html`

---

## Mission 208 — Backend FRD : War Room & Architecture Multi-Agents
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-07**
**ACTOR: GEMINI**

---

### Ce qui marche
- **Layout "War Room"** : Grille 3 colonnes `[Architecte | Roadmap | Ouvrier]` avec design industriel `0px border-radius`.
- **Double Terminal** : Footer scindé en deux zones de logs indépendantes (Planning vs Exécution).
- **Architecture Multi-Agents** : Sullivan segmenté en rôles `architect` et `worker` avec contextes étanches.
- **Persistance & Historique** : Sessions sauvegardées en SQLite avec **Quick-Switcher** (5 dernières convs par rôle).
- **Auto-Titrage** : Détection dynamique des IDs de mission (`M208`, `M139`...) dans la Roadmap pour nommer les sessions.
- **WsBackend.js** : Orchestrateur centralisé gérant le dual-chat et le rendu Markdown synchrone.

---

## Mission 210 — Réorganisation Documentaire Frontend
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-07**
**ACTOR: GEMINI**

---

### Ce qui marche
- **Extraction Docs 09** : Création de `docs/09_Frontend/` comme pôle d'autonomie visuelle.
- **FRONTEND_MANIFEST.md** : Clarification des rôles Kimi/Stenciler et doctrine "True HoméOS".
- **ANIMATION_LAWS.md** : Codification des standards GSAP et Splitting.js pour le projet.
- **Migration Chirurgicale** : 7 documents et 2 répertoires d'assets UI déplacés de `02_Sullivan` vers `09_Frontend`.
- **README Global** : Indexation de la nouvelle section Frontend.

---

## Mission 187 — Wire Pipeline End-to-End : Forge + Runtime Groq
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-06**
**ACTOR: Claude (CODE DIRECT — FJD)**

---

### Ce qui marche
- `ensure_ids()` : injecte des IDs lisibles (`btn-envoyer`, `lnk-homeos`…) sur tout élément interactif au moment du pre-wire
- `id` propagé dans `final_elements` (corrigé : champ manquant dans la fusion Sullivan)
- `POST /api/projects/{project_id}/wire-apply` : patch BeautifulSoup déterministe — 20 éléments maillés sur `cadrage_alt.html` ✅
- Wire runtime injecté dans le HTML forgé : écoute les clics sur `[data-wire]`, POST `/api/wire-execute`, affiche toast
- `/api/wire-execute` : appelle Groq (`llama-3.3-70b-versatile`), retourne réponse en JSON
- Fix `StreamingResponse` sur `/api/cadrage/chat/{provider}` (était un async_generator non wrappé → 500)
- `getActiveScreenHtml()` : fallback `contentDocument.outerHTML` pour iframes chargées via `src=`
- `wire-apply` sauvegarde dans `static/templates/{template_name}` (fichier d'origine) + backup `.bak`
- Script console forge-direct : bypass du liminaire pour test rapide

---

### Résultat validé FJD
> "Gloria ! Ah, 'pouet' ! Eh bien, bonjour à toi aussi !" — Groq répond au premier message via le template wiré ✅

---

### Bugs corrigés ce sprint
- Loop liminaire sur dernier élément → `_submitLiminaire()` auto sur last element
- CSS pseudo-sélecteurs → `ensure_ids()` appelé en tête de `/pre-wire`
- `screen_html manquant` à la forge → fallback `contentDocument.outerHTML` dans `_submitLiminaire`
- `modified_elements: ['body']` → id propagé dans final_elements + `enriched_html` retourné par pre-wire

---

## Mission 185 — Pré-Wiring : Manifest émergent du template
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-06**
**ACTOR: GEMINI (2 phases)**

- `POST /api/projects/{project_id}/pre-wire` : BeautifulSoup extrait les éléments interactifs, Sullivan infère les intents, calcule la bijection (`total` / `incomplete` / `null`)
- `POST /api/projects/{project_id}/pre-wire/validate` : écrit `manifest.json` avec les organes validés par le designer
- `WsWire.js` : `btnApplyPlan` appelle `/pre-wire` avant tout. Si `bijection === 'total'` → forge directe. Sinon → `_startLiminaire()`
- `_renderLiminaireUI()` : stepper organe par organe dans l'overlay Wire — tag, texte, intent inféré, oui / éditer / textarea custom
- `_highlightInIframe()` : postMessage `highlight-intent` vers l'iframe pour visualiser l'élément courant
- `_submitLiminaire()` : POST `/pre-wire/validate` → manifest écrit → forge déclenchée
- Fallback `contentDocument.outerHTML` appliqué partout où `screen.srcdoc` peut être vide (iframe chargée via `src=`)

---

## Mission 161 — Sullivan GSAP Bridge
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-03**
**ACTOR: QWEN**

- Mode `front-dev` dans Sullivan : prompt GSAP Expert avec wires injectés en contexte
- Parsing délimiteur `---LOGIC---` → `logic_js` extrait de la réponse LLM
- `logic.js` écrit dans `projects/{uuid}/logic.js` après chaque réponse Sullivan
- Route `GET /api/projects/active/logic.js` → sert le fichier JS au browser (fallback vide si absent)
- Sullivan injecte `<script type="module" src="/api/projects/active/logic.js">` dans le HTML retourné

---

## Mission 165 — DESIGN.md par projet
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-03**
**ACTOR: QWEN**

- `GET /api/workspace/tokens` lit `projects/{uuid}/design_tokens.json` si présent, sinon defaults HoméOS
- Prompt Sullivan (`server_v3.py:653`) : `design_path = get_active_project_path() / "DESIGN.md"` avec fallback template global
- `parse_design_md()` : parser colors, fonts, shape, effects → `design_tokens.json` projet
- `POST /api/projects/{uuid}/design-md` → upload + parse → écrit tokens projet

---

## Mission 163 — Frontend : Switcher Projet UI
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-03**
**ACTOR: GEMINI**

- `bootstrap.js` : `injectSwitcher()` → `#homeos-project-switcher` injecté dans le nav global
- CSS : drawer fixe, `opacity + translateY` transition, `.active` toggle
- Badge `.hn-project` clickable → ouvre/ferme le switcher
- Branché sur `GET /api/projects`, `POST /api/projects/create`, `PUT /api/projects/activate`

---

## Mission 160 — Mode FEE : Visual Wiring (Trigger → Target)
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-03**
**ACTOR: GEMINI**

- `WsWire.js` (232L) — gestion overlay wireframe + tracé de liens visuels
- Sélection en 2 temps : Trigger → Target via `_triggerData` + `_saveWire()`
- Draft line SVG animée pendant le tracé (`ws-wire-canvas`, `ws-wire-lines`, `ws-wire-draft`)
- Persistance via `POST /api/projects/{id}/wires` (livré en M162)
- Intégration workspace : `ws-wire-overlay`, `ws-wire-table-body`, event type select

---

## Mission 162 — Backend : CRUD Projet dynamique
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-03**
**ACTOR: QWEN**

- `GET /api/projects` · `POST /api/projects/create` · `PUT /api/projects/activate` · `DELETE /api/projects/{id}`
- `GET /api/projects/active` · `GET|PUT /api/projects/{id}/manifest`
- DB SQLite (`projects.db`) — isolation complète par projet
- `get_active_project_id()` / `set_active_project_id()` dynamiques via `bkd_service`
- Structure `projects/{uuid}/imports/ exports/ manifests/` opérationnelle
- Bonus M160 : `POST /api/projects/{id}/wires` livré en avance

---

## Mission 164 — Sullivan Apply : Fix document.write → srcdoc
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-03**
**ACTOR: GEMINI (CODE DIRECT)**

- `WsPreview.js:52` : `contentDocument.open/write/close` remplacé par `previewIframe.srcdoc = htmlStatic`
- `_lastSullivanHtml` setté avant le srcdoc — lecture future préservée
- Sullivan Apply opérationnel : shadow-xl + border-radius visibles dans le preview

---

## Mission 159 — Design System Intendant (DESIGN.md)
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-03**
**ACTOR: GEMINI**

- Route `GET /api/workspace/tokens` dans `server_v3.py` — retourne tokens projet actif
- `ws_main.js` : fetch tokens au DOMContentLoaded → `inspect.applyDesignTokens(tokens)`
- `WsInspect.applyDesignTokens()` : filtrage fonts (`fontSelect` options disabled), désactivation outils interdits (`allowCustomColors === false` → btn opacity 0.3), gestion `tokens.effects`
- UI restrictive opérationnelle : les outils non autorisés par le DESIGN.md sont visuellement neutralisés sans être supprimés

---

## Mission 158 — Mirror Core : Extraction chirurgicale du tracker
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-03**
**ACTOR: GEMINI**

- `static/js/workspace/tracker/ws_iframe_core.js` créé — IIFE autonome, guard `window.__aetherTrackerLoaded`
- Tracker extrait de `WsInspect.js` (était inline string ~200L dans `injectTracker`)
- `WsInspect.injectTracker()` → async, `fetch('/static/js/workspace/tracker/ws_iframe_core.js')` + `createElement('script')` + `textContent`
- Tous les `postMessage` types préservés : `inspect-click`, `inspect-tool-change`, `inspect-undo`, `inspect-ready-to-place-image`
- Injection via `textContent` (pas `src=`) → compatible srcdoc + cross-origin localhost

---

## Mission 151 — Auto-génération manifeste à l'import HTML
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-02**
**ACTOR: GEMINI (server_v3.py)**

- Bloc M151 injecté dans `import_upload()` après écriture du template HTML
- `ManifestInferer` (Playwright DOM) → `ArchetypeDetector` → `manifest_{import_id}.json`
- Champs : `archetype`, `components[]` (name, role, z_index, x, y, w, h, text)
- Try/except : upload ne bloque jamais si Playwright échoue
- Idempotent : ne régénère pas si manifest existant

---

## Mission 149 — Canvas N0 : États de sélection + toolbar opérationnelle
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-02**
**ACTOR: GEMINI (WsCanvas.js + workspace.css)**

- États CSS : `.ws-hover`, `.ws-selected`, `.ws-dragging` — suppression `.pulsing`
- `_notifyToolbar()` + `ws-canvas-state` custom event
- Hover sur shell → mouseenter/mouseleave
- Drag → `.ws-dragging` ajouté/retiré au mouseup
- Sélection persistante : clic hors SVG ne déselectionne plus

---

## Mission 148 — Bridge @font-face : fontes système → iframes screens
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-02**
**ACTOR: CLAUDE (CODE DIRECT — server_v3.py + WsInspect.js)**

- Route `POST /api/sullivan/generate-webfont` — scan filesystem + TTF→WOFF2 via fonttools, cache idempotent
- Route `GET /api/sullivan/system-fonts` — 600+ fontes macOS indexées
- `applyTypo()` : inject `@font-face` dans `iframe.contentDocument`, apply via `currentSelector` (scope graft Monaco)
- Override Tailwind utilities via règle CSS `selector, selector * { font-family !important }` injectée dans l'iframe
- `lastSelectedEl` + `selector` dans `inspect-organ-selected` pour persistance de sélection

---

## Mission 146 — Détection manifeste → routage Wire ou Cadrage
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-02**
**ACTOR: GEMINI (server_v3.py)**

- Route `GET /api/frd/manifest?import_id={id}` — détecte `projects/{active}/manifests/manifest_{id}.json`
- Réponse `{ exists: true, manifest: {...} }` ou `{ exists: false }`
- Correction ordre instanciation FastAPI (NameError résolu)

---

## Mission 144 — Export projet + @font-face dans les screens
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-02**
**ACTOR: CLAUDE (CODE DIRECT — server_v3.py + WsCanvas.js + WsFontManager.js)**

- Route `GET /api/frd/export-zip?import_id=` — ZIP HTML + fontes en attachment
- Bouton "↓" dans le header de chaque screen (WsCanvas.js)
- `WsFontManager.injectStyles()` — injection `@font-face` dans les iframes screens

---

## Mission 142 — Sullivan Actions : édition directe du screen actif
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-02**
**ACTOR: CLAUDE (CODE DIRECT — WsChat.js + server_v3.py + WsCanvas.js)**

- `WsChat.js` : capture du HTML de l'iframe active (preview prioritaire, puis shell SVG) via `fetch(iframe.src)` si pas de `srcdoc`
- `server_v3.py` : prompt conditionnel — si `screen_html` présent, demande JSON `{explanation, html}` à Gemini ; parsing robuste avec fallback texte
- `WsCanvas.js` : `updateActiveScreenHtml(html)` — priorité preview iframe, fallback shell SVG ; `mousedown` stopPropagation sur forge button
- Forge button fix : `mousedown` + `stopPropagation` ajouté (canvas interceptait le clic)
- Sullivan agit directement sur le rendu en mode aperçu

---

## Mission 140 — Boutons Aperçu & Save dans le header de chaque screen canvas
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-01**
**ACTOR: GEMINI (WsCanvas.js)**

- `previewFo` et `saveFo` repositionnés à `y=8`, `height=24` dans la bande header (0–40px)
- `previewFo` : `x=SW-260`, `width=110` | `saveFo` : `x=SW-140`, `width=55`
- `mousedown` avec `stopPropagation` sur les deux → drag non bloqué sur le reste du header
- `console.log` debug supprimés

---

## Session 2026-04-01 — Hotfixes Canvas Workspace (hors mission)
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-01**
**ACTOR: CLAUDE (CODE DIRECT)**

- **Upload HTML → canvas direct** : `POST /api/import/upload` retourne `{"import": entry}` + copie dans `static/templates/` + `html_template` setté. Wiring `ws-direct-upload` dans `ws_main.js` (plus d'inline `onchange`).
- **Backfill html_template** : `GET /api/retro-genome/imports` backfille à la volée les imports HTML anciens sans `html_template` (copy→templates + màj index.json).
- **ZIP React avec dist/** : `run_conversion()` détecte `dist/index.html` → extrait le dist, crée un wrapper iframe HTML, sette `html_template` directement — zéro LLM.
- **Drag fix** : détection zone header par position Y (`worldY <= 40`) au lieu de `closest('.ws-screen-header')` (transparent, non hit-testable).
- **Close btn** : suppression directe sans `confirm()`, `pointer-events:all` explicite.
- **foreignObject iframe** : `pointer-events:none` sur le conteneur fo → drag vivant après forge.
- **Sullivan feedback forge** : 4 messages progressifs pendant polling (`forgeScreen` → `window.wsChat.appendBubble`).
- **TIMEOUT 60→180s** : `.env` + `Backend/.env`.
- **`/api/frd/file?raw=1`** : route retourne `HTMLResponse` au lieu de JSON → iframe affiche le HTML rendu.
- **Double init ws_main.js** : suppression du double `<script>` dans workspace.html.
- **Dimensions adaptatives** : 1200×800 pour HTML direct, 400×632 pour SVG/forgé.
- **ws_main.js TypeError** : guards `if (el)` sur btn-zoom-in/out/reset.
- **ws-chat-history** : zone messages ajoutée dans workspace.html + null-safe dans `appendBubble`.
- **beautifulsoup4 + lxml** installés (`--break-system-packages`).

---

## Mission 126 — Cascade LLM : gemini-3.1-flash-lite en queue BUILD
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-01**
**ACTOR: CLAUDE (CODE DIRECT — gemini_client.py)**

- `gemini-3.1-flash-lite` ajouté en fin des 3 cascades (FAST, BUILD, DEFAULT)
- Mimo reste dernier recours dans `svg_to_tailwind.py` (après épuisement total Gemini)

---

## Mission 125 — DELETE /api/imports/{id}
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-01**
**ACTOR: CLAUDE (CODE DIRECT — server_v3.py)**

- `DELETE /api/imports/{import_id}` : retire de index.json + supprime fichier sur disque
- 404 si id inconnu

---

## Mission 124 — Fallback Mimo après quota Gemini épuisé
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-01**
**ACTOR: CLAUDE (CODE DIRECT — mimo_client.py + svg_to_tailwind.py)**

- `generate_with_image()` ajouté à `MimoClient` (format OpenAI multimodal vision, base64 inline)
- `svg_to_tailwind.py` : fallback Mimo après Gemini 429 — `convert()` (text/SVG) + `convert_image()` (vision PNG)
- `MIMO_KEY` depuis `.env` via `settings.mimo_api_key` (déjà configuré)
- Si Mimo échoue aussi → exception levée avec message clair

---

## Mission 123 — Patienteur génération : preload bar header
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-01**
**ACTOR: GEMINI (stenciler.css) + CLAUDE (FrdIntent.feature.js)**

- `stenciler.css` : `.global-pipeline-header::after` + `.is-loading` + `@keyframes homeos-preload` (sweep vert 2.5s)
- `FrdIntent.feature.js` : `classList.add('is-loading')` au démarrage `generateTailwind()` → `remove` sur done/failed/error (4 points de sortie couverts)

---

## Mission 122 — Pipeline import unifié : tous formats → FRD editor
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-01**
**ACTOR: CLAUDE (CODE DIRECT — routes.py + svg_to_tailwind.py + FrdIntent.feature.js)**

- `convert_image(b64, mime, name)` ajouté dans `svg_to_tailwind.py` (Gemini vision PNG/JPG → HTML+Tailwind)
- `GET /api/retro-genome/import-analysis` route générique (SVG, HTML DOM, ZIP, PNG post-gen) — même schéma `{ components }` que SVG
- `GET /api/retro-genome/import-analysis-svg` conservée en alias rétrocompat (appelle `import-analysis` en interne)
- `FrdIntent.init()` → route `/import-analysis` générique + gestion cas vides (PNG auto-trigger, React message, défaut message)
- Cas PNG image dans `run_conversion()` : détection par extension → `convert_image()`

---

## Mission 116 — Fix pipeline intent_viewer → FRD editor
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-01**
**ACTOR: CLAUDE (CODE DIRECT — intent_viewer.html uniquement)**

- `let latestImport = null` ajouté au niveau module dans `intent_viewer.html`
- `fetchIntents()` renseigne `latestImport = imports[0]`
- `openTemplateInFRD()` réécrit : utilise `latestImport` pour appeler `POST /api/frd/set-current` → redirect `/frd-editor`
- Pas de fetch `/api/frd/current` (null sur navigation directe) — fix du bug de navigation depuis tab global

---

## Mission 121 — Hotfix pipeline import : HTML 500 + generate-from-import cassé + bégaie
**STATUS: ✅ LIVRÉ**
**DATE: 2026-03-31**
**ACTOR: CLAUDE (CODE DIRECT — backend uniquement)**

- Bug A : `_NEW_IMPORTS_COUNT = 0` ajouté au module level dans `server_v3.py` (NameError corrigé)
- Bug B : `entry.get("svg_path") or entry.get("file_path")` dans `routes.py` (KeyError sur imports HTML)
- Bug C : fichier HTML sauvegardé dans `imports_dir / today_str /` (cohérence chemin index.json)
- Bug D : `Path(safe_name).stem + ext` (double extension `code.html.html` corrigée)

---

## Mission 109C — Font Advisor + UI Landing (Sullivan Typography Engine)
**STATUS: ✅ LIVRÉ**
**DATE: 2026-03-31**
**ACTOR: CLAUDE (routes + advisor) + GEMINI (UI landing.html)**

- `POST /api/sullivan/font-upload` → classifier + webgen + advisor → `{ classification, webfont, sullivan_commentary }`
- `GET /api/sullivan/fonts` + `DELETE /api/sullivan/fonts/{slug}`
- `sullivan_font_advisor.py` : combine FontClassifier + typography_db.json → commentaire Sullivan (catégorie Vox-ATypI + référence proche + suggestion pairing)
- `landing.html` section `#font-manager` : drop zone, carte par fonte (badge Vox-ATypI, preview live, @font-face snippet Monaco, warning licensing, badge variable font)

---

## Mission 107 — Navigation globale cohérente (bootstrap.js)
**STATUS: ✅ LIVRÉ**
**DATE: 2026-03-30**
**ACTOR: QWEN (bootstrap.js + CSS) + CLAUDE (hotfix tokens + emojis)**
- [x] `bootstrap.js` — `injectGlobalNav()` au DOMContentLoaded
- [x] 4 tabs pipeline : import / analyser / éditer / déployer (disabled)
- [x] Détection pathname automatique pour tab actif
- [x] `window.HOMEOS.boot()` / `refreshNav()` exposés
- [x] CSS `.global-pipeline-header` dans `stenciler.css` — 48px fixe, z-index 1000
- [x] 3 templates mis à jour : landing.html, intent_viewer.html, frd_editor.html
- [x] Hotfix Claude : `#8cc63f` (tokens officiels), emojis → `○`/`●`, CSS dupliqué supprimé

---

## Mission 104/108 — Stitch Integration : backend.md + INTENT_MAP enrichi
**STATUS: ✅ LIVRÉ**
**DATE: 2026-03-30**
**ACTOR: QWEN (routes + landing UI) + CLAUDE (hotfix statut "todo")**
- [x] `POST /api/manifest/import-stitch` — parse `design.md` → génère `backend.md`
- [x] `GET /api/manifest/backend` + `PUT /api/manifest/backend` — CRUD `backend.md`
- [x] Badge "Stitch Compatible" sur landing si `design.md` présent
- [x] Bouton "synchroniser stitch" + drawer Monaco `backend.md` éditable
- [x] `WireAnalyzer._get_backend_mapping()` — lit `backend.md`, priorité sur STATIC_MAP
- [x] Hotfix Claude : statut `"todo"` (≠ "error") pour intents sans mapping connu ; `"warning"` → `"todo"` dans summary

---

## Mission 103 — Wire mode v5 : auto-launch + overlay bijection
**STATUS: ✅ LIVRÉ**
**DATE: 2026-03-30**
**ACTOR: GEMINI (frontend) + CLAUDE (wire_analyzer.py)**
- [x] `wire_analyzer.py` retourne `{intentions[], statuts[], plan[]}` — schéma bijectif
- [x] `FrdChat.feature.js` : `setMode('wire')` → `this.main.wire.run()` auto (pas de bouton Analyser)
- [x] `FrdWire.feature.js` : `showOverlayV5()` — overlay z-index, colonne bilan + colonne plan côte à côte
- [x] `frd_editor.html` : `#bijective-overlay`, bouton IMPLÉMENTER, "BILAN DE BIJECTION" bouton
- [x] Dépréciation de l'audit UI cosmétique absorbé dans le bilan Wire

---

## Mission 69 — FRD Editor : Mode LOCK (zones invariantes)
**STATUS: ✅ LIVRÉ**
**ACTOR: GEMINI (frontend) + CLAUDE (backend + auto-id)**
**DATE: 2026-03-23**
**FICHIERS :** `frd_editor.html`, `server_9998_v2.py`
- [x] Bouton `[LOCK]` dans le header — toggle orange quand actif
- [x] Hover en mode LOCK → outline orange pointillés + breadcrumb DOM
- [x] Clic preview → `data-frd-lock="true"` dans Monaco + décoration fond orange + 🔒 glyph
- [x] Toggle off sur clic d'un élément déjà locké
- [x] Sélection Monaco + `Ctrl+L` → lock sur la balise ouvrante
- [x] LOCK ↔ INSPECT mutuellement exclusifs
- [x] Backend : détection `data-frd-lock` → injection ZONES INVARIANTES dans system_instruction Sullivan
- [x] `[✕ Locks]` → retire tous les locks + efface décorations Monaco
- [x] **Auto-id** : élément sans id → `id="lock-{tag}-{timestamp36}"` généré automatiquement au lock (ancrage précis pour Sullivan)
- [x] `data-frd-lock` survit au Save/Load

---

## Mission 70 — Sullivan Intelligence : Undo + History + Manifest
**STATUS: ✅ LIVRÉ**
**ACTOR: CLAUDE (CODE DIRECT)**
**DATE: 2026-03-23**
**FICHIERS :** `frd_editor.html`, `server_9998_v2.py`

---

### 70-A — Undo Stack
- [x] `_htmlHistory[]` (max 10 états) — push avant chaque setValue Sullivan
- [x] Bouton `⟲ Undo` dans le header — hidden par défaut, visible après 1ère action Sullivan
- [x] Pop + restore + updatePreview au clic
- [x] Reset au Load (nouveau contexte)

---

### 70-B — Conversation History Multi-turn
- [x] `_chatHistory[]` (max 6 échanges = 12 messages) — maintenu côté frontend
- [x] Envoyé dans le body POST `/api/frd/chat` (`history: [...]`)
- [x] Backend reconstruit `contents` Gemini en multi-turn (`role: user/model`)
- [x] `systemInstruction` séparé (format Gemini natif)
- [x] Reset au Load

---

### Ce qui a été fait
- Réécriture des 3 méthodes wireframe dans `sullivan_renderer.js` (231L → enrichis)
  - `generateWireframeCorps` : 4 hints (brainstorm/backend/frontend/deploy) avec gradients et icônes
  - `generateWireframeOrganes` : 3 hints (analyse/choix/sauvegarde) avec composants expressifs
  - `generateWireframeGeneral` : hint table + fallback coloré
- Bug CSS corrigé dans `choix` : `display:gap:6px` → `display:flex;gap:6px`
- Commit 94488da (+cleanup repo : archive_svelte -40MB, .backup_*, .generated.py, artifacts pip)

---

### Ce qui a été fait
- Fix 1 : Inférence `visual_hint` depuis `comp.name` pour les Corps (L143-150)
  - brainstorm / backend+api / frontend+interface / deploy+livraison
- Fix 2 : 3 nouveaux wireframes dans `generateWireframeGeneral()` (L100-133)
  - `detail-card` : header coloré + 3 lignes label:valeur
  - `stencil-card` : titre + description + 2 boutons Garder/Réserve
  - `form` : 2 champs gris empilés + bouton submit vert
- Fix 3 : `description_ui` affiché sur 2 lignes dans `.comp-info` (L163+L171, `-webkit-line-clamp:2`)

---

### Ce qui a été fait

**Mission B — viewer.html + genome_engine.js**
- Breadcrumb DOM ajouté dans `viewer.html` (avant `.container`) :
  - `#breadcrumb-bar` (display:none par défaut)
  - `#breadcrumb-text` : affiche "Tout › [NomCorps]"
  - `#breadcrumb-back` + `#breadcrumb-reset` : boutons de navigation
- `genome_engine.js` — 5 méthodes de drill-down ajoutées :
  - `drilldownState` : objet d'état `{active, corpsId, corpsName, organeId, organeName}`
  - `applyDrillFilter()` : masque/affiche les `.comp-card` selon le corps actif
  - `updateBreadcrumb()` : affiche/masque la barre breadcrumb selon l'état
  - `drillInto(corpsId, corpsName)` : active le filtrage sur un corps
  - `resetDrill()` : désactive le filtrage, tout redevient visible
  - Listeners breadcrumb dans `setupEventListeners()`

**Mission C — sullivan_renderer.js**
- `generateComponentCard()` : `onclick` conditionnel sur les cartes Corps
  - Corps → `drillInto(id, name)` + `toggleCheckbox(cid)`
  - Autres niveaux → `toggleCheckbox(cid)` seul
- Sélection checkbox préservée pendant le drill

---

### Ce qui reste ouvert (transmis Phase 3)
- Bug canvas `'alphabetical'` → `'alphabetic'` (stenciler.js:~313) — hors scope viewer, sera traité Phase 3
- Faux positifs semantic_bridge.js (58 violations HTML dans description_ui) — non bloquant
- `stenciler_v2.html` : monolithe 1540L, source de difficultés agents → Phase 3 Factory

# ROADMAP AetherFlow — Phase Active

---

## PIPELINE V4 — Duo Claude + Gemini

```
Claude (Chief Engineer)    → Cleanup + architecture + review code
Gemini (Frontend Executor) → CSS/SVG generation, inputs: stenciler.css + LEXICON_DESIGN.json
FJD (DA)                   → Validation visuelle — seule autorité esthétique
KIMI                       → VEILLE (hors pipeline actif)
```

**Règle d'or :** Aucun agent ne prend de décision visuelle. Les tokens sont dans `stenciler.css`. Tout écart = retour à FJD.

---

## PHASE 4 — Design Transposition V1→V3 (Test d'efficience)

> **Objectif :** `/stenciler` V3 doit être visuellement identique au design V1 (stenciler.css).
> Si on y arrive → FJD nous fait confiance. Sinon → on recommence avec les leçons.

> **Hypothèse de travail (FJD, 2026-02-19) :** CSS est un langage difficile à "lire" pour les LLMs.
> Ils génèrent du CSS sans voir le rendu. Risque de dérive à chaque itération.
> → Stratégie : Gemini doit d'abord **prouver qu'il comprend** la V1 avant d'écrire quoi que ce soit.

---

---

### ✅ Mission 4A — CLAUDE : Dépollution CSS (CODE DIRECT)
STATUS: TERMINÉ — validé FJD 2026-02-19
ACTOR: CLAUDE

- viewer.css retiré de stenciler_v3.html ✓
- Font Inter → Geist dans Canvas.feature.js ✓
- Fallback color #1e293b → #3d3d3c ✓
- Route /stenciler → stenciler_v3.html ✓

---

---

### ✅ Mission 4B — GEMINI : TEST DE LECTURE (Comprehension Check)
STATUS: TERMINÉ ✅ — validé Claude 2026-02-19
ACTOR: GEMINI (Antigravity)

**Rapport Gemini :** SPEC_LECTURE_V1.md créé (10 zones).
**Validation Claude (4C) :** 10/10 tokens exacts. GO pour 4D.
**2 gaps mineurs notés (non bloquants) :**
- Zone 5 : `.preview-card` dimensions manquantes (width 180px, min-height 90px, radius 6px, padding 10/12px, bg-tertiary)
- Zone 9 : `.color-swatch.selected` state manquant (border var(--text-primary) + box-shadow ring)

---
⚠️ BOOTSTRAP GEMINI — Lire avant toute action
Constitution : Frontend/1. CONSTITUTION/CONSTITUTION_AETHERFLOW_V3.md
Tu es le Système de Rendu. Ici tu es en mode LECTURE uniquement.
Tu ne produis AUCUN CSS à cette étape. Tu produis une SPEC structurée.
FJD est DA — seule autorité visuelle. Claude valide ta lecture avant toute génération.
---

**Contexte :**
Le CSS est un langage difficile à interpréter visuellement pour les LLMs.
Avant de générer quoi que ce soit, tu dois prouver que tu comprends le design V1.

**Input files (lecture seule) :**
- `Frontend/3. STENCILER/static/css/stenciler.css` ← tokens V1 source de vérité
- `Frontend/3. STENCILER/static/STENCILER_REFERENCE_V1.html` ← HTML V1 référence
  ⚠️ Lire UNIQUEMENT le CSS (lignes 9–1219) et le HTML (lignes 1222–1470)
  ⚠️ Ignorer le `<script>` (Fabric.js — obsolète, hors scope)
- `Frontend/1. CONSTITUTION/LEXICON_DESIGN.json` ← contrat CSS partagé

**Output file (écrire ici) :**
`Frontend/4. COMMUNICATION/SPEC_LECTURE_V1.md`

**Mission :**
Lis `stenciler.css` + la section CSS/HTML de `STENCILER_REFERENCE_V1.html`.
Produis une **SPEC DE LECTURE** structurée. PAS de CSS généré.

Pour chaque zone : classe, dimensions (avec token), fond (avec token + hex), typo, layout, états.

**Zones à auditer (10 zones) :**
1. Header (`.stenciler-header`, `.header-actions`, `.style-indicator`)
2. Sidebar gauche (`.sidebar` — dimensions, fond, scroll)
3. Sidebar header (`.sidebar-header`, `.sidebar-brand`, `.sidebar-tagline`)
4. Section sidebar (`.sidebar-section`, `.sidebar-section-title`)
5. Preview band (`.preview-band`, `.preview-card`, variantes `.brainstorm/.backend/.frontend/.deploy`)
6. Canvas zone (`.canvas-zone`, grille `::before`)
7. Components zone (`.components-zone`, `.components-grid`, `.component-card`)
8. Zoom controls (`.zoom-controls`)
9. Palette couleurs (`.color-swatch`, `.color-palette`, `.color-mode-toggle`)
10. Boutons sidebar (`.btn-back`, `.btn-delete`, `.btn-api`)

**Format strict par zone :**
```

---

### Zone : [Nom]
- Classe principale : .nom-classe
- Dimensions : width/height → var(--token) = Xpx (ou "non défini")
- Background : var(--token) = #hexcode
- Font : Geist Xpx / weight NNN / letter-spacing si présent
- Layout : flex row|col | grid X cols | position absolute
- Border : Xpx solid var(--token) = #hexcode (ou "aucune")
- États : hover → [ce qui change] | active → ... | selected → ...
```

Si un token n'existe pas dans stenciler.css → écrire `"non défini dans CSS"`. Pas d'invention.

**Critères de succès 4B :**
- 8 zones documentées
- Chaque token cité avec sa valeur numérique réelle (ex: `var(--sidebar-width) = 200px`)
- Aucune couleur inventée — tout extrait de stenciler.css
- Aucun CSS généré

---

---

### ✅ Mission 4C — CLAUDE : Validation de la Spec
STATUS: TERMINÉ ✅ — 2026-02-19
ACTOR: CLAUDE

Résultat : spec Gemini VALIDÉE. 10/10 tokens exacts. GO Mission 4D.

---

---

### ✅ Mission 4D — GEMINI : Production CSS Fidèle V3
STATUS: RAPPORT
ACTOR: GEMINI (Antigravity)

**Ce qui a été fait :**
- Génération complète de `stenciler_v3_additions.css` couvrant les 10 zones auditées.
- Intégration stricte des tokens `var(--token)` (Fidélité 100% vs `stenciler.css`).
- Résolution des gaps identifiés en 4C :
    - `.preview-card` : Dimensions (180x90px min), padding, radius et bordures-accent activés.
    - `.color-swatch.selected` : État sélectionné conforme (double bague border + shadow).
- Support Dark Mode `[data-theme="dark"]` implémenté pour toutes les nouvelles règles.
- Typographie Geist appliquée partout (font-family, sizes).

**Validation :**
- CSS injecté et prêt pour test sur http://localhost:9998/stenciler.
- Utilisation exclusive des tokens de `stenciler.css` (aucune couleur hardcodée).

**Critères de succès :**
- Les 10 zones ont leur rendu V1.
- Layout 3 colonnes respecté via les slots.
- Transitions `0.12s ease` appliquées.

---

---

### ✅ Mission 4E — CLAUDE : Review Technique
STATUS: TERMINÉ ✅ — 2026-02-19
ACTOR: CLAUDE

CSS Gemini validé. 3 hotfixes CODE DIRECT appliqués :
- border-left preview-cards : 3px → 2px (fidélité V1)
- .color-swatch:hover : ajout border-color var(--border-warm)
- .btn-api : font-size 10px (était groupé à 11px)

---

---

### ✅ Mission 4F — GEMINI : Micro-Wireframes Preview Cards
STATUS: TERMINÉ ✅ — 2026-02-19
ACTOR: GEMINI (Antigravity)

**Rapport Gemini :** Micro-wireframes injectés (Brainstorm, Backend, Frontend, Deploy).
**Validation FJD :** "OK ON EST MIEUX. JE vous fais confiance. C'est le niveau de granularité qui doit présider toujours".

---

---

### Ce qui a été fait
- Branchement du frontend V3 sur `/api/genome` (port 9998, URL relative)
- Support du format imbriqué `{ genome: { n0_phases: [...] } }`
- Genome chargé dans `stenciler_v3_main.js` → `loadGenome()` → distribué à toutes les features via `feature.init(this.genome)`
- Identification des 4 Corps : Brainstorm (2 organes), Backend (1), Frontend (7), Deploy (1)
- Cartographie des 10 Organes identifiés (n1_ir, n1_arbitrage, n1_session, n1_navigation, n1_layout, n1_upload, n1_vision, n1_dialogue, n1_validation, n1_adaptation, n1_export)
- PreviewBand.feature.js : rendu des 4 cards corps avec wireframes typés et drag-and-drop vers canvas

---

### Ce qui a été fait
- **Modèle UX Canvas-Centric** implémenté et validé :
  - `PreviewBand` : N0 permanent. `dblclick` → dispatch `corps:open` (aucun drill in-band)
  - `Canvas` : écoute `corps:open` → rendu hiérarchique centré dans le viewport SVG
  - `ComponentsZone` : écoute `corps:selected` → affiche N1 organes + N2 cells en sidebar droite
- **High-Density Rendering (N2)** : micro-rectangles 2px opacité 0.15 injectés dans les nœuds organes du Canvas
- **Slot alignment** : ComponentsZone montée sur `Lexicon.slots.sidebar_right` (corrigé depuis `slot-main`)
- **Communication découplée** : `CustomEvent` exclusivement (`corps:open`, `corps:selected`) — zéro couplage direct entre features

---

### Fichiers modifiés
- `Canvas.feature.js` (328L — ~28L au-dessus de la limite 300L, à surveiller en 5C)
- `ComponentsZone.feature.js` (78L — réécriture complète)
- `stenciler_v3_main.js` — slot ComponentsZone aligné sur `sidebar_right`
- `PreviewBand.feature.js` — `drillToCorps()` supprimé, event-driven

---

### Preuves
- Screenshots Gemini : canvas_brainstorm_card + right_sidebar_components
- Walkthrough Gemini : `~/.gemini/antigravity/brain/70f1790b.../walkthrough.md.resolved`

---

### Ce qui a été fait

**Gemini (exécution) :**
- `Canvas.layout.js` créé (99L) — 4 layouts sémantiques inférés depuis `corps.id` :
  - Exploration (brainstorm) : colonne 600px centrée
  - Architecture (backend) : stack vertical 300px compact
  - Composition (frontend) : grille 2 colonnes 400px
  - Pipeline (deploy) : flux horizontal
- `Canvas.feature.js` refactorisé à 212L (< 300L ✓) — drag & drop supprimé, layout engine branché
- `PreviewBand.feature.js` — event delegation sur `this.el` dans `mount()`, `click` remplace `dblclick`, classe `.active` + opacité via CSS

**Claude (3 hotfixes CODE DIRECT) :**
- `corps:selected` dispatch ajouté dans `_setupSelectionHandlers` (manquait chez Gemini)
- CSS `.preview-card { opacity: 0.5 }` + `.preview-card.active { opacity: 1 }` dans `stenciler_v3_additions.css`
- `CORPS_COLORS` map ajoutée inline (`phaseData.color` absent du genome réel)

---

### Bug root-cause résolu (5B regression)
Le `dblclick` silencieux de 5B était dû à des listeners individuels attachés après `innerHTML` reset dans `renderCorps()`.
Fix définitif : event delegation sur le parent `this.el` dans `mount()` — robuste contre tout innerHTML reset.

---

### Ce qui a été fait
- `Canvas.feature.js` : `corps:selected` → `organe:selected` avec `{ organeId }` (dispatch précis N1)
- `ComponentsZone.feature.js` refactorisé (82L) :
  - Écoute `organe:selected` (plus `corps:selected`)
  - Recherche de l'organe via `flatMap(n0_phases → n1_sections)` — robuste quel que soit le corps parent
  - Render des N2 cells avec description de l'organe sélectionné
  - État vide : "Cliquez sur un Organe dans le Canvas pour voir ses détails"

---

### Ce qui a été fait
- `ComponentsZone.feature.js` refactorisé (129L) :
  - Écoute `corps:open` → mémorise `currentCorps`, reset `currentOrgane`, affiche vue Corps
  - Vue Corps : nom N0 + nb organes + invite "Sélectionnez un organe"
  - Vue Organe : breadcrumb `[CORPS] › [ORGANE]` + N2 cells (hérité 5D)
  - Fallback `onOrganeSelected` : si `currentCorps` absent, remonte via `find()` dans le genome
- CSS dans `stenciler_v3_additions.css` : `.cz-breadcrumb`, `.cz-separator`, `.cz-corps-header`

---

### Ce qui a été fait
- `ComponentsZone.feature.js` (204L) :
  - `onCelluleSelected(celluleId)` : mémorise la cellule N2 active
  - `_renderCelluleView()` : breadcrumb Corps › Organe › Cellule + liste des `n3_components`
  - Chaque N3 : méthode badge (GET/POST) + endpoint + description_ui
  - Back link breadcrumb → retour vue Organe (`currentCellule = null`)
  - Event delegation sur `.cell-item.selectable` dans `_renderOrganeView`
- CSS dans `stenciler_v3_additions.css` : `.atom-card`, `.atom-method`, `.atom-endpoint`, `.atom-desc`, `.cz-led`

---

### Ce qui a été fait
- `ComponentsZone.feature.js` réduit à 185L (< 200L ✓) :
  - `_updateProperty` + `isSaving` supprimés (dead code 5F)
  - Back nav N1→N0 : `← [NomCorps]` dans `_renderOrganeView` → `currentOrgane = null`
  - Back nav N2→N1 : `← [NomOrgane]` dans `_renderCelluleView` (amélioré vs 5F)
  - Style inline supprimé dans `_renderCorpsView` → classe `.cz-invite`
- `stenciler_v3_additions.css` : `.cz-breadcrumb` 11px + `var(--text-secondary)`, badges méthodes colorés (GET/POST/DELETE), `.cz-invite`, `.atom-desc` clamp 3 lignes

---

### Ce qui a été fait
- `Canvas.feature.js` — `_drillInto(id, level)` :
  - level 1 : dispatche `organe:selected` après `_renderOrgane()`
  - level 2 : dispatche `cellule:selected` après `_renderCellule()`
- `Canvas.feature.js` — `_drillUp()` :
  - stack vide après pop : `_renderCorps()` + dispatche `corps:drill-back`
  - level 1 après pop : `_renderOrgane()` + dispatche `organe:selected`
- `ComponentsZone.feature.js` — `init()` : 2 nouveaux listeners
  - `cellule:selected` → `onCelluleSelected(celluleId)`
  - `corps:drill-back` → `onCorpsOpen(corpsId)`

---

### Incident pipeline
AetherFlow run success_rate 1.0 (Codestral) mais auto-apply n'a pas écrit les fichiers.
Bug identifié dans le code généré : `corps:drill-back` dispatché avant le pop (mauvais moment).
Claude a corrigé et appliqué CODE DIRECT — FJD.

---

### Ce qui a été fait (6D initial)
- `Canvas.feature.js` : stripe latérale 6px (couleur corps), hover states, icônes N1, ombre sélection
- Icons inférés depuis `data.id` (pas de `visual_hint` en N1) via `ID_ICONS` map

---

### Diagnostic 6D-DIAG — Causes root identifiées et fixes
**Problème :** FJD ne constatait aucun changement visuel après Cmd+Shift+R.

**Bug 1 — `level = false` au lieu de `0`** :
- `_renderCorps` passait `false` comme 4ème arg à `_renderNode` → `level === 0` échouait → icônes jamais rendues
- Fix : `_renderNode(organe, pos, color, 0)` (Canvas.feature.js L84)

**Bug 2 — `pointer-events` sur `<g>` SVG** :
- Sans `pointer-events: all` explicite sur les éléments `<g>`, mouseenter/mouseleave non capturés
- Fix : `g.setAttribute('pointer-events', 'all')` + `g.style.cursor = 'pointer'` pour `level < 2`
- Root cause du hover non fonctionnel en 6D.

**Bug 3 — Hauteur N2 trop petite** :
- Nœuds N2 à 60px → micro-cellules commençant à 55px masquées
- Fix : `cardH = 100px` (Canvas.feature.js L100)

---

### Ce qui a été fait
- `Persistence.feature.js` créé : sauvegarde automatique Genome dans `localStorage` (`stenciler_genome_v3`) avec debounce 2s
- Auto-merge au chargement : merge Genome distant + modifications locales
- `ComponentsZone.feature.js` — `_renderCelluleView()` reécrit en mode Authoring :
  - Champs éditables inline : method (select), name (input), endpoint (input), description_ui (textarea auto-resize)
  - `_setupCelluleListeners()` : mutation genome en mémoire + dispatch `genome:updated`
  - LED `.cz-led idle/saving` : feedback visuel sauvegarde (vert → orange pulsé → vert)
- `ComponentsZone.feature.js` : 257L (> 200L limite — surveiller)

---

### Ce qui a été fait
- `Header.feature.js` : ajout `.header-exports` avec boutons `#btn-export-json` + `#btn-export-html`
- `exportJSON()` : téléchargement Genome actuel (incl. modifications localStorage) via data URI
- `exportHTML()` : génération HTML autonome encapsulant le SVG Canvas + styles critiques + footer Sullivan
- `Header.feature.js` : 124L ✓

---

### Ce qui a été fait
- Page de test `static/wireframe_test_7a.html` : 12 wireframes SVG natifs, grille 4 colonnes
- **Groupe A — Traduction (6)** : table, stepper, chat/bubble, stencil-card, upload, dashboard
  - Source : sullivan_renderer.js (HTML inline) → SVG natif + tokens stenciler.css
  - Dark mode réactif (toggleTheme() ajouté par Gemini)
- **Groupe B — Création ex nihilo (6)** : accordion, color-palette, editor, modal, breadcrumb, zoom-controls
  - Seule entrée : description_ui du genome. Aucune référence visuelle.
  - Qualité comparable ou supérieure au Groupe A
- Score final : 12/12 ✅ (A5 upload : polish iconographie post-revue)

---

### Ce qui a été fait
- `Canvas.renderer.js` : `_matchHint()` — resolver intelligent avec HINT_ALIASES + keyword pool
- Guard `if (wfSVG)` → `rect.style.display = 'none'` + `stripe.style.display = 'none'` + `title.opacity = 0.35`
- Fallback intègre : atomes N3 et composants sans wireframe conservent le rendu boîte
- `LayoutEngine.js` : dimensions affinées par zone (TOP 60px, CENTER 220px, RIGHT 180px, BOTTOM 200×50)
- Nouveaux wireframes dans `WireframeLibrary.js` : `action-button`, `grid`, `selection`
- Résultat : canvas = maquette d'application, plus d'organigramme

---

### Ce qui a été fait
- `static/js/GRID.js` créé, 99L — lookup table 8px complète (G.U1→G.U50, constantes sémantiques ICON/BTN/CARD/SIDEBAR/etc., G.snap/cols/rows)
- Import dans `stenciler_v3_main.js` + exposition `window.G` pour debug console
- Audit `LayoutEngine.js` : 4 valeurs déjà alignées, 5 non-alignées documentées (delta ≤ 6px), conservées

---

### Ce qui a été fait
- `Backend/Prod/orchestrator.py` L31-76 : `SUBSTYLE_DEFAULTS` + `SUBSTYLE_RULES` (20 visual_hints) + `inject_substyle()` — lookup pur, coût LLM zéro
- `Backend/Prod/core/surgical_editor.py` L478-486 : guard `_` prefix dans `_validate_operation()` — bloque tout patch LLM ciblant un membre `_*`

---

### Ce qui a été fait
- `static/js/features/Nuance.feature.js` créé, 87L : `resolveSubstyle()` + `NuanceUI.render()` + `NuanceUI.setupHandlers()`
- `static/js/features/ComponentsZone.feature.js` : import NuanceUI, panneau NUANCE injecté dans `_renderSidebarPanels()`, handlers substyle, listener `canvas:node:selected`
- `static/js/features/Canvas.feature.js` : dispatch `canvas:node:selected` + `canvas:selection:cleared` dans `_selectNode()` / `_deselectAll()`
- `stenciler_v3_main.js` : import `resolveSubstyle` + exposition `window.resolveSubstyle`

---

### Ce qui a été fait
- `static/js/features/InlineEdit.feature.js` créé, 100L : `InlineEditUI.mount()` / `commit()` / `close()` — input HTML positionné en absolu sur le container canvas
- `static/js/features/Canvas.feature.js` : dblclick sur `.atom-node` → `InlineEditUI.mount()` sur le champ `name` uniquement

---

### Bugfixes Claude (CODE DIRECT)
- `#canvas-zone` → `#slot-canvas-zone` (container V3 réel — sans ça, zéro input créé)
- `close()` : `activeInput = null` avant `remove()` pour couper le cycle blur→commit sur Escape
- Scope réduit à `name` uniquement : method/endpoint retirés (détail technique, hors scope DA)
- Callback `(data) =>` → `()` (paramètre inutilisé)

---

### Ce qui a été fait

**1. Toggle Grid / No Grid**
- Bouton `⊞` (grid toggle) ajouté dans les zoom-controls
- État `this.gridVisible` dans le constructor de CanvasFeature
- Handler clic : toggle `display: block/none` sur `#svg-grid`
- Feedback visuel : bouton à 40% d'opacité quand grille masquée

**2. Fond SVG plus dense**
- Ajout `<rect id="svg-bg">` sous la grille avec `fill="var(--bg-secondary)"`
- Le fond hérite automatiquement du thème via CSS variables
- Mode jour : `#f0efeb` (dense, moins flottant)
- Mode nuit : `#111111` (encore plus dense, "accident heureux")
- Structure SVG : `#svg-bg` → `#svg-grid` → `#svg-viewport`

---

### Fichiers modifiés
- `Frontend/3. STENCILER/static/js/features/Canvas.feature.js` (+24L)

---

### Résumé des itérations

**Itération 1** — Toggle grid + fond dense
- Toggle bouton `⊞` ajouté
- Fond `--bg-secondary` sous la grille
- Problème : toggle ne masquait que la grille centrale (grille CSS en double)

**Itération 2** — Déduplication
- Grille CSS `::before` commentée dans `stenciler.css` et `additions.css`
- Grille unique = SVG pattern
- Problème : grille trop légère en mode jour

**Itération 3** — Visibilité améliorée
- Stroke-width : 0.5px → 1px
- Couleur : `--grid-line` → `--border-subtle` (#d5d4d0)
- Résultat : grille visible jour et nuit

---

### Fichiers finaux modifiés
- `Canvas.feature.js` — pattern grid + toggle handler
- `stenciler.css` — .canvas-zone::before commenté
- `stenciler_v3_additions.css` — ::before commenté

---

### Résumé
Au niveau N0 du Stenciler (vue Corps → organes), les organes s'affichaient comme des compositions SVG bottom-up abstraites sans sens visuel reconnaissable.

---

### Ce qui a été fait
1. **SemanticMatcher.js** — Extension de `_keywordFallback()` avec mots-clés organ-level :
   - `preview` : analys, analysis, png, image, inspect, render, viewer
   - `stencil-card` : intent, refactor, ir, tile, item
   - `breadcrumb` : nav, navbar, menu, header, toolbar
   - `chat-input` : message, conversation, prompt
   - `form` : login, signup, register, auth, password, credential

2. **Canvas.renderer.js** — Bloc Mission 17A dans `renderNode()` avant `_buildComposition()` :
   - Si `level === 0` : essaie `_matchHint(data)` sur l'organe N1
   - Si hint trouvé : `WireframeLibrary.getSVG()` → `compGroup.innerHTML = wfSvg` → return
   - Sinon : fall-through vers bottom-up composition (zéro régression)

---

### Contexte
Pivot stratégique : abandon de l'inférence SVG comme vue principale. Ajout d'une route `/preview` qui rend le genome en vrais composants Flowbite HTML, garantissant une lecture fidèle et sans ambiguïté du contenu N3.

---

### Ce qui a été fait
1. **`genome_preview.py`** (nouveau fichier) — Mappe N3 `visual_hint` → composants Flowbite HTML.
   - 20+ hints couverts (button, launch-button, stepper, breadcrumb, chat, table, form, upload, accordion, dashboard, grid, modal, download...)
   - N3 `name` = label du composant
   - `data-genome-id` + `data-hint` sur chaque élément (traçabilité genome → HTML)
   - Onglets de navigation entre les 4 phases N0

2. **`server_9998_v2.py`** — 3 patches :
   - Import `render_genome_preview`
   - Route `GET /preview` → phase 1 (Brainstorm) par défaut
   - Route `GET /preview/<phase_id>` → phase ciblée
   - Méthode `_send_html()` helper

---

### Routes disponibles
- `http://localhost:9998/preview` — phase Brainstorm par défaut
- `http://localhost:9998/preview/n0_backend`
- `http://localhost:9998/preview/n0_frontend`
- `http://localhost:9998/preview/n0_deploy`

---

### Ce qui a été fait
1. **Tâche 1 ✅** — 20 fichiers `.generated.py` orphelins supprimés dans `Backend/Prod/sullivan/`
2. **Tâche 2 🚫 BLOQUÉ** — `apply_generated_code()` dans `claude_helper.py` a des appelants actifs :
   - `workflows/proto.py` (L180, L229)
   - `workflows/frd.py` (L115, L228, L354)
   - `workflows/verify_fix.py` (L12, L116, L211)
   - `tests/test_new_file_creation.py` (multiples)
   → Suppression reportée à V3-B (UnifiedExecutor — suppression des workflows zombie)
3. **Tâche 3 ✅** — `astunparse>=1.6.3` déjà présent dans `requirements.txt` (L46)

---

### Note sur le surgical_editor.py
Une régression `\n` (évasion trop agressive) a été détectée et corrigée lors des tests finaux.

---

### Ce qui a été fait
1. **genome_preview.py** — JS d'édition inline injecté :
   - F1 : `dblclick` sur `.genome-label` → `contenteditable` → blur/Enter → `PATCH /api/genome/node/<id>` `{field:'name'}`
   - F2 : bouton ⚙ au hover → `prompt()` hint picker → `PATCH /api/genome/node/<id>` `{field:'visual_hint'}` → `location.reload()`
   - F3 : SortableJS CDN → drag-and-drop composants → `PATCH /api/genome/organ/<id>/reorder`
   - Bonus : clic composant → highlight jaune (sélection visuelle)

2. **server_9998_v2.py** — Endpoints PATCH :
   - `PATCH /api/genome/node/<id>` — met à jour `name` ou `visual_hint` dans le genome JSON
   - `PATCH /api/genome/organ/<id>/reorder` — réordonne les N3 dans un organe
   - `save_genome()`, `_find_n3_by_id()`, `_find_n2_by_organ()` helpers

---

### Ce qui a été fait
- `Backend/Prod/core/js_parser/ast_parser.js` — parseur AST JS via acorn (Node.js)
- `Backend/Prod/core/surgical_editor_js.py` — SurgicalApplierJS range-based sur AST
- `apply_engine.py` — routing automatique `*.js` → SurgicalEditorJS

---

### Ce qui a été fait
- `static/genome_canvas.html` généré par AetherFlow (Gemini, 44s, 100%)
- Canvas div-based avec organes N1 draggables (vrais composants Flowbite)
- Route `GET /genome_canvas` dans server_9998_v2.py (CODE DIRECT)
- Hotfix tabs N0 (Gemini avait hardcodé n0_phases[0])
- Hotfix drag : `e.target.closest()` + listeners sur `document`

---

### Ce qui a été fait
- AetherFlow 20A (76s, 100%) : focus mode CSS + structure
- Hotfixes CODE DIRECT (Gemini avait ignoré le resize) :
  - CSS `.resize-handle` (triangle bas-droit)
  - `renderOrgan()` : append `.resize-handle` div
  - `initDragAndDrop()` : logique resize séparée du drag (flag `resizedOrgan`)
  - Restauration `organ.w` au load depuis `/api/layout`
  - POST `/api/layout` inclut `w` au mouseup drag ET resize

---

### État genome_canvas.html
- Drag libre ✅ (listeners document, e.target.closest)
- Tabs N0 ✅
- Resize largeur ✅ (poignée triangle bas-droit)
- Persistance x/y/w ✅ (layout.json)
- Focus mode : structure CSS présente, interaction à valider

---
# ARCHIVE 2026-03-03 — Phases 10→21B
# Strategic Roadmap Stenciler V3

## Vision 2026 : Le Majordome de Code (Sullivan Architecture)
Garantir une transition fluide du Genome (DNA fonctionnel) vers le Stencil (UI/UX) tout en préservant la fidélité visuelle V1.

---

## ✅ Phases 1→9D COMPLÈTES

Archivées dans [ROADMAP_ACHIEVED.md](file:///Users/francois-jeandazin/AETHERFLOW/Frontend/4. COMMUNICATION/ROADMAP_ACHIEVED.md).

---

## Phase 10 — Detail Cascade : Du Grain Atomique vers les Corps

> **Vision fondatrice :** chaque niveau du Genome doit être visible avec le niveau de détail de ses enfants.
> Un Atome est un vrai composant UI. Une Cellule montre ses Atomes. Un Organe montre ses Cellules. Un Corps montre ses Organes.
> **Clef unique : 8px.** Toutes les dimensions, marges, snap et incréments sont des multiples de 8.

**Pré-requis posés (Claude, CODE DIRECT, 2026-02-21) :**
- `snapSize: 20` → `8` (grille visuelle + magnétisme = clef 8px)
- `cardH N1: 100` → `96` (= G.U12, multiple 8 propre)
- `cardH N3: 45` → `80` (= G.U10, atomes lisibles)

---

---

### Mission 10A — Atom-First Detail : Rendre les Atomes Lisibles [LIVRÉ]

---

### Diagnostic de bug (Claude)

Le rendu actuel des atomes (N3) cache la carte-conteneur grise et laisse le wireframe flotter seul :

```js
// Canvas.renderer.js — L183-185 — COMPORTEMENT ACTUEL (BUGUÉ)
rect.style.opacity = '0';    // ← cache le fond grey
stripe.style.opacity = '0';  // ← cache la stripe colorée
```

**Résultat :** le wireframe apparaît sans cadre. L'utilisateur (FJD) voit un gros bouton ou un composant isolé qui ne ressemble pas aux "cartouches gris" attendus.

**Référence attendue :** `http://localhost:9998/static/wireframe_test_7a.html`
→ Chaque wireframe est dans un `.svg-container` avec fond `var(--bg-secondary)` et `border-radius: 8px`.
→ Le wireframe est **à l'intérieur** du cartouche, pas à la place du cartouche.
→ FJD collera une capture d'écran de comparaison.

---

---

### Fix attendu

**Fichier : `static/js/Canvas.renderer.js`**
Section concernée : le bloc `if (isAtom)` → sous-bloc `renderAtom` (L177-190 environ).

**Principe :**
1. Garder `rect` visible (fond grey = le "cartouche"). Ne pas toucher `rect.style.opacity`.
2. Garder `stripe` visible (bande colorée à gauche). Ne pas toucher `stripe.style.opacity`.
3. Placer le wireframe **à l'intérieur** de la carte avec padding :
   - `PAD_LEFT = 14` (stripe 6px + gap 8px)
   - `PAD_TOP = 24` (espace pour le label en haut)
   - `PAD_RIGHT = 8`
   - `PAD_BOTTOM = 8`
4. Dimensions intérieures passées à `renderAtom` :
   - `innerW = pos.w - PAD_LEFT - PAD_RIGHT`
   - `innerH = pos.h - PAD_TOP - PAD_BOTTOM`
5. `atomGroup` translé à `(PAD_LEFT, PAD_TOP)`.
6. `title` (label du nœud) : garder visible, opacity `0.7`, position y `16`, font-size `9`.

**Même correction pour le sous-bloc `data.visual_hint`** (L163-175) : même logique, garder rect+stripe, wireframe avec padding.

```js
// RÉSULTAT ATTENDU — pseudo-code
if (isAtom) {
    const PAD_LEFT = 14, PAD_TOP = 24, PAD_RIGHT = 8, PAD_BOTTOM = 8;
    const innerW = pos.w - PAD_LEFT - PAD_RIGHT;
    const innerH = pos.h - PAD_TOP - PAD_BOTTOM;

    if (data.visual_hint) {
        const wfSVG = WireframeLibrary.getSVG(data.visual_hint, color, innerW, innerH, data.name);
        if (wfSVG) {
            const wfGroup = this._el('g', { class: 'wf-content', 'pointer-events': 'none',
                transform: `translate(${PAD_LEFT}, ${PAD_TOP})` });
            wfGroup.innerHTML = wfSVG;
            g.append(wfGroup);
            // rect et stripe RESTENT VISIBLES
            title.style.opacity = '0.7';
            title.setAttribute('y', '16');
            title.setAttribute('font-size', '9');
            return g;
        }
    }

    const svgStr = renderAtom(data.interaction_type, data.name, { w: innerW, h: innerH }, color);
    if (svgStr) {
        const atomGroup = this._el('g', { class: 'atom-wf-content', 'pointer-events': 'none',
            transform: `translate(${PAD_LEFT}, ${PAD_TOP})` });
        atomGroup.innerHTML = svgStr;
        g.append(atomGroup);
        // rect et stripe RESTENT VISIBLES
        title.style.opacity = '0.7';
        title.setAttribute('y', '16');
        title.setAttribute('font-size', '9');
    }
    return g;
}
```

---

---

### Contraintes

- **Aucun autre fichier à modifier.** Uniquement `Canvas.renderer.js`, section atome.
- `AtomRenderer.js` n'est **pas** à toucher.
- `Canvas.feature.js` n'est **pas** à toucher (cardH = 160 reste).
- Toutes les dimensions en multiples de 8px.
- Ne pas hardcoder de valeurs absolues hors de `PAD_LEFT/TOP/RIGHT/BOTTOM`.

---

---

### Critères d'acceptation

- [ ] Atome avec `interaction_type: 'click'` → fond grey visible + stripe colorée + wireframe `action-button` à l'intérieur
- [ ] Atome avec `interaction_type: 'view'` → fond grey visible + wireframe `table` à l'intérieur
- [ ] Atome sans `interaction_type` → fond grey visible + wireframe `accordion` à l'intérieur
- [ ] Label du nœud visible en haut de la carte (opacity 0.7, y=16, font-size 9)
- [ ] Résultat visuellement proche de wireframe_test_7a.html (wireframes dans leur conteneur)
- [ ] FJD valide

---

## Backlog Phase 10→11

| ID | Mission | Actor | Statut |
|----|---------|-------|--------|
| 10A | Atom-First Detail | Gemini | ✅ Livré |
| 10A-ARCH| AtomRenderer générique | Gemini | ❌ Rejeté DA |
| 10A-WF  | AtomRenderer WireframeLibrary | Gemini | ✅ Livré |
| 10A-FRAME | Atom Card Frame | Gemini | ✅ Livré |
| 11A | Atom Group Edit — Mode Illustrateur | Gemini | ✅ Livré |
| 11B | Primitive Style Panel (couleur, typo) | Gemini | ✅ Livré |
| 12A | Pivot Bottom-Up SVG (Vrai WYSIWYG) | Gemini | ✅ Livré |
| 13A-PRE | Toggle Grid & Fond Dense SVG | Gemini | ✅ ARCHIVÉ |
| 13A-DESIGN | Proposition Design System (Hype Minimaliste) | Gemini | 🔄 EN COURS |
| 13A | Semantic UI & Design System (Implémentation) | Gemini | ⏳ EN ATTENTE |
| 11C | Export final HTML/CSS | — | ⏳ Backlog |

---

## Phase 11 — Atom Group Edit : Mode Illustrateur

> **Vision FJD :** Double-cliquer sur un atome entre dans le groupe SVG, comme Illustrator.
> Chaque primitive (rect bouton, text label, circle icône) devient sélectionnable et draggable individuellement.
> Clic extérieur → sortie du mode groupe.

---

### Mission 11A — Atom Group Edit

**ACTOR: GEMINI | MODE: CODE DIRECT | FICHIER UNIQUE: `Canvas.feature.js`**

#### Fichiers à lire AVANT (OBLIGATOIRE)
1. `static/js/features/Canvas.feature.js` — entier. Lire `_setupDrillHandlers()`, `_selectNode()`, `_showHandles()`, `_getMousePos()`.
2. `static/js/AtomRenderer.js` — comprendre les primitives SVG générées (rect, text, circle).
3. `static/js/Canvas.renderer.js` — section `if (isAtom)` : structure du `<g>` atome.

#### Structure SVG d'un atome dans le DOM
```
<g class="svg-node atom-node" data-id="...">
  <rect class="node-bg">              ← fond carte
  <rect>                              ← stripe colorée gauche
  <text class="node-label">           ← nom du nœud
  <g class="atom-wf-content" pointer-events="none">
    <rect rx="14">                    ← pill bouton (click/submit)
    <text>                            ← label du bouton
  </g>
</g>
```

#### Implémentation

**1. Constructor — 2 lignes :**
```js
this.groupEditMode = false;
this.groupEditTarget = null;
```

**2. Dans `_setupDrillHandlers()` — intercepter dblclick sur atom-node AVANT le drill :**
```js
if (node.classList.contains('atom-node')) {
    e.stopPropagation();
    this.groupEditMode ? this._exitGroupEdit() : this._enterGroupEdit(node);
    return;
}
```

**3. `_enterGroupEdit(node)` :**
```js
_enterGroupEdit(node) {
    this.groupEditMode = true;
    this.groupEditTarget = node;
    const bg = node.querySelector('.node-bg');
    if (bg) { bg.setAttribute('stroke','var(--accent-bleu)'); bg.setAttribute('stroke-dasharray','5 3'); bg.setAttribute('stroke-width','2'); }
    this.viewport.querySelectorAll('.svg-node').forEach(n => { if (n !== node) n.style.opacity = '0.25'; });
    const content = node.querySelector('.atom-wf-content') || node.querySelector('.wf-content');
    if (!content) return;
    content.setAttribute('pointer-events','all');
    content.querySelectorAll('rect,text,circle,path').forEach(prim => {
        prim.style.cursor = 'move';
        prim.setAttribute('pointer-events','all');
        prim._gc = (e) => { e.stopPropagation(); this._selectPrimitive(prim, node); };
        prim.addEventListener('click', prim._gc);
    });
}
```

**4. `_selectPrimitive(prim, parentNode)` :**
```js
_selectPrimitive(prim, parentNode) {
    parentNode.querySelectorAll('.prim-sel').forEach(el => el.remove());
    const bb = prim.getBBox();
    const ov = document.createElementNS('http://www.w3.org/2000/svg','rect');
    Object.entries({x:bb.x-2,y:bb.y-2,width:bb.width+4,height:bb.height+4,fill:'none',stroke:'var(--accent-bleu)','stroke-width':'1.5','stroke-dasharray':'3 2','pointer-events':'none'}).forEach(([k,v])=>ov.setAttribute(k,v));
    ov.classList.add('prim-sel');
    parentNode.appendChild(ov);
    this._setupPrimitiveDrag(prim, ov);
}
```

**5. `_setupPrimitiveDrag(prim, overlay)` :**
```js
_setupPrimitiveDrag(prim, overlay) {
    const getXY = () => ({x:parseFloat(prim.getAttribute('x')??prim.getAttribute('cx')??0),y:parseFloat(prim.getAttribute('y')??prim.getAttribute('cy')??0)});
    const setXY = (x,y) => { const c=prim.tagName==='circle'; prim.setAttribute(c?'cx':'x',x); prim.setAttribute(c?'cy':'y',y); };
    let drag=false, sm={};
    prim.addEventListener('mousedown',e=>{drag=true;sm=this._getMousePos(e);e.stopPropagation();});
    window.addEventListener('mousemove',e=>{if(!drag)return;const m=this._getMousePos(e);const p=getXY();setXY(p.x+(m.x-sm.x),p.y+(m.y-sm.y));const bb=prim.getBBox();overlay.setAttribute('x',bb.x-2);overlay.setAttribute('y',bb.y-2);overlay.setAttribute('width',bb.width+4);overlay.setAttribute('height',bb.height+4);sm=m;});
    window.addEventListener('mouseup',()=>{drag=false;});
}
```

**6. `_exitGroupEdit()` :**
```js
_exitGroupEdit() {
    const node = this.groupEditTarget;
    if (!node) return;
    const bg = node.querySelector('.node-bg');
    if (bg) { bg.setAttribute('stroke','var(--border-subtle)'); bg.removeAttribute('stroke-dasharray'); bg.setAttribute('stroke-width','1.5'); }
    this.viewport.querySelectorAll('.svg-node').forEach(n=>n.style.opacity='1');
    const content = node.querySelector('.atom-wf-content')||node.querySelector('.wf-content');
    if (content) { content.setAttribute('pointer-events','none'); content.querySelectorAll('rect,text,circle,path').forEach(p=>{p._gc&&p.removeEventListener('click',p._gc);delete p._gc;p.setAttribute('pointer-events','none');p.style.cursor='';}); }
    node.querySelectorAll('.prim-sel').forEach(el=>el.remove());
    this.groupEditMode=false; this.groupEditTarget=null;
}
```

**7. Dans le handler `click` existant — en tête du handler :**
```js
if (this.groupEditMode) {
    const n = e.target.closest('.svg-node');
    if (!n || n !== this.groupEditTarget) { this._exitGroupEdit(); return; }
}
```

#### ✅ COMPTE-RENDU DE LIVRAISON : MISSION 11A
**DATE : 2026-02-21**
**STATUS : DÉPLOYÉ & VALIDÉ**

#### 1. Mode Illustrator (Group Edit)
- **Accès** : Double-clic sur un Atome (N3) pour entrer dans le mode.
- **Feedback visuel** : Bordure bleue discontinue (`stroke-dasharray`) sur le cartouche, estompage (`opacity: 0.25`) des autres éléments du canvas pour focus total.
- **Édition granulaire** : Chaque primitive SVG à l'intérieur du wireframe (rect, text, circle, path) devient sélectionnable et **draggable** individuellement.
- **Sortie** : Clic sur le canvas vide ou double-clic à nouveau sur l'atome pour valider les positions et sortir.

#### 2. Architecture Technique
- **Pointer Events** : Libération des `pointer-events` sur le groupe `atom-wf-content` uniquement pendant l'édition.
- **Overlay de sélection** : Calcul dynamique des `BBox` pour afficher un cadre de sélection bleu autour des primitives.
- **Draggable Primitives** : Système de drag local sans dépendance externe, gérant les coordonnées `x/y` (rect/text) et `cx/cy` (circle).

> [!WARNING]
> **Observation FJD** : Des décalages visuels subsistent entre le rendu "Group Edit" et les wireframes de référence. Une phase de recalage des densités et des coordonnées est nécessaire.

---

---

### Critères d'acceptation
- [x] Dbl-clic atome → bordure pointillée bleue, autres nodes à 25% opacité
- [x] Clic sur primitive → overlay sélection bleu pointillé
- [x] Primitive sélectionnée → draggable dans le groupe
- [x] Dbl-clic à nouveau ou clic hors → sortie propre
- [x] Zéro régression sur drill N1→N2→N3

---

---

---

### Mission 11B — Atom Inspector Panel (Wireframe Pleine Taille)

**ACTOR: GEMINI | MODE: CODE DIRECT | FICHIER: `Canvas.feature.js` uniquement**

#### Contexte

11A a livré le mode groupe (dblclick → primitives sélectionnables dans le cartouche). Mais les atomes générés par AtomRenderer n'ont que 2-3 primitives simples (pill + text). 11B ouvre un **panel HTML flottant** qui affiche le wireframe WireframeLibrary complet à taille native (280×180px), avec toutes ses primitives éditables (5-15 éléments selon le type).

`WireframeLibrary` est déjà importé dans Canvas.feature.js (L2). Ne pas ré-importer.

#### Étapes

**1. Ajouter à la fin de `_enterGroupEdit(node)` :**
```js
this._openAtomInspector(node);
```

**2. `_openAtomInspector(node)` :**
```js
_openAtomInspector(node) {
    this._closeAtomInspector();
    const atomData = this._findInGenome(node.dataset.id);
    if (!atomData) return;

    const WF_MAP = { 'click':'action-button', 'submit':'action-button', 'drag':'selection', 'view':'table' };
    const wfKey = WF_MAP[atomData.interaction_type] || 'accordion';
    const stripe = node.querySelector('rect[fill]:not(.node-bg)');
    const color = stripe ? stripe.getAttribute('fill') : 'var(--accent-bleu)';
    const wfSVG = WireframeLibrary.getSVG(wfKey, color, 280, 180, atomData.name);
    if (!wfSVG) return;

    const panel = document.createElement('div');
    panel.id = 'atom-inspector';
    panel.style.cssText = `position:fixed;right:16px;top:80px;width:312px;background:var(--bg-primary,#f7f6f2);border:1px solid var(--border-warm,#d4cfc8);border-radius:8px;z-index:1000;box-shadow:0 4px 24px rgba(0,0,0,0.12);font-family:Geist,sans-serif;`;
    panel.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-bottom:1px solid var(--border-subtle);">
            <span style="font-size:11px;font-weight:700;color:var(--text-primary);text-transform:uppercase;">${atomData.name}</span>
            <button id="atom-inspector-close" style="background:none;border:none;cursor:pointer;font-size:14px;color:var(--text-muted);">✕</button>
        </div>
        <div style="padding:16px;">
            <svg id="atom-inspector-svg" width="280" height="180" style="border-radius:6px;background:var(--bg-secondary,#eeede8);">${wfSVG}</svg>
        </div>
        <div style="padding:0 16px 12px;font-size:10px;color:var(--text-muted);">Clic sur une primitive pour la sélectionner</div>
    `;
    document.body.appendChild(panel);
    this._inspectorPanel = panel;

    panel.querySelector('#atom-inspector-close').addEventListener('click', () => this._exitGroupEdit());

    const inspSVG = panel.querySelector('#atom-inspector-svg');
    inspSVG.querySelectorAll('rect,text,circle,path,line').forEach(prim => {
        prim.style.cursor = 'move';
        prim.setAttribute('pointer-events', 'all');
        prim._ic = (e) => { e.stopPropagation(); this._selectInspectorPrimitive(prim, inspSVG); };
        prim.addEventListener('click', prim._ic);
        prim.addEventListener('mousedown', (e) => this._startInspectorDrag(prim, e, inspSVG));
    });
}
```

**3. `_selectInspectorPrimitive(prim, svgEl)` :**
```js
_selectInspectorPrimitive(prim, svgEl) {
    svgEl.querySelectorAll('.insp-sel').forEach(el => el.remove());
    const bb = prim.getBBox();
    const ov = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    Object.entries({x:bb.x-2,y:bb.y-2,width:bb.width+4,height:bb.height+4,fill:'none',stroke:'#a8c5fc','stroke-width':'1.5','stroke-dasharray':'3 2','pointer-events':'none'}).forEach(([k,v])=>ov.setAttribute(k,v));
    ov.classList.add('insp-sel');
    svgEl.appendChild(ov);
}
```

**4. `_startInspectorDrag(prim, e, svgEl)` :**
```js
_startInspectorDrag(prim, e, svgEl) {
    e.stopPropagation();
    const CTM = svgEl.getScreenCTM();
    const toSVG = (ev) => ({ x:(ev.clientX-CTM.e)/CTM.a, y:(ev.clientY-CTM.f)/CTM.d });
    const isCirc = prim.tagName === 'circle';
    let sm = toSVG(e);
    let sp = { x:parseFloat(prim.getAttribute(isCirc?'cx':'x')||0), y:parseFloat(prim.getAttribute(isCirc?'cy':'y')||0) };
    const move = (ev) => {
        const m = toSVG(ev);
        prim.setAttribute(isCirc?'cx':'x', sp.x+(m.x-sm.x));
        prim.setAttribute(isCirc?'cy':'y', sp.y+(m.y-sm.y));
        this._selectInspectorPrimitive(prim, svgEl);
    };
    const up = () => { window.removeEventListener('mousemove',move); window.removeEventListener('mouseup',up); };
    window.addEventListener('mousemove', move);
    window.addEventListener('mouseup', up);
}
```

**5. `_closeAtomInspector()` :**
```js
_closeAtomInspector() {
    if (this._inspectorPanel) { this._inspectorPanel.remove(); this._inspectorPanel = null; }
}
```

**6. Dans `_exitGroupEdit()` — ajouter en première ligne :**
```js
this._closeAtomInspector();
```

---

### ✅ COMPTE-RENDU DE LIVRAISON : MISSION 11B
**DATE : 2026-02-21**
**STATUS : DÉPLOYÉ & VALIDÉ (Attente Vérif Humaine)**

#### 1. Atom Inspector Panel
- **Ouverture** : Le double-clic sur un atome ouvre désormais un panneau flottant (`#atom-inspector`) en haut à droite du viewport.
- **Fidélité Totale** : Ce panneau affiche le wireframe natif de l'atome (provenant de la `WireframeLibrary`) à sa taille réelle de conception (280x180), permettant de voir le composant tel qu'il a été pensé avec *toutes* ses primitives sémantiques.
- **Édition Absolue** : Chaque ligne, texte, bouton, ou forme à l'intérieur de ce panneau est individuellement sélectionnable (overlay bleu pointillé) et déplaçable via *drag & drop*.

#### 2. Architecture Technique
- **Cycle de Vie** : La fonction `_openAtomInspector` est greffée dans `_enterGroupEdit`. Réciproquement, `_exitGroupEdit` appelle `_closeAtomInspector` pour garantir la propreté du DOM.
- **Indépendance** : Le système de drag & drop à l'intérieur de l'inspecteur (`_startInspectorDrag`) gère ses propres transformations matricielles SVG (`getScreenCTM`) pour assurer que le curseur suit parfaitement l'élément déplacé, indépendamment du zoom ou pan du Canvas principal.

> [!NOTE]
> Cette mission répond directement à la problématique de cohérence visuelle soulevée, en offrant un accès direct et non-destructif au layout "source" de l'atome, tel qu'imaginé dans le niveau supérieur.

---

---

### Critères d'acceptation
- [x] Dblclick atome → panel flottant à droite avec wireframe WireframeLibrary 280×180
- [x] Clic sur primitive dans le panel → overlay sélection bleu pointillé
- [x] Drag d'une primitive dans le panel → elle se déplace
- [x] Bouton ✕ ou clic extérieur → panel fermé, mode groupe quitté
- [x] Zéro régression sur 11A

---

## PHASE 12A — Pivot Bottom-Up SVG (Le Vrai Mode Illustrateur)
STATUS: MISSION
MODE: aetherflow -f
ACTOR: KIMI

---
⚠️ BOOTSTRAP KIMI
Constitution : Frontend/1. CONSTITUTION/CONSTITUTION_AETHERFLOW_V3.md
Règles absolues :
1. Jamais CSS/HTML dans le backend
2. Jamais GenomeStateManager côté frontend
3. Communication via API REST uniquement
4. Mode aetherflow obligatoire (sauf CODE DIRECT — FJD)
5. Validation humaine obligatoire : URL + port avant "terminé"
---

---

### Mission
L'approche de la Phase 11 (fausse image N1 + cartouches purs N2/N3) est abandonnée car elle casse la cohérence visuelle "WYSIWYG" lors du Drill-Down.
L'objectif est de reconstruire le moteur de rendu (`Canvas.renderer.js` et `AtomRenderer.js`) pour imposer une composition en "Bottom-Up". Le wireframe d'un niveau d'enveloppe ne doit plus être une "image precalculée" provenant d'une librairie abstraite (c.-à-d. la WireframeLibrary) mais la somme réelle de la disposition de ses atomes enfants, orchestrée sémantiquement selon les données du génome.

Étapes de la mission :
1. **AtomRenderer (Sémantique Pure)** : Supprimer le cartouche générique N3. Dessiner des SVG sémantiques purs (Bouton, Tab, Texte) basés UNIQUEMENT sur `interaction_type` et dimensionnés avec les constantes de `GRID.js` (`G.BTN`, etc.).
2. **Layout Sémantique (Tone & Density)** : Utiliser `density` (compact, normal, airy) du génome pour mapper directement vers `G.GAP_S`, `G.GAP`, `G.PAD`, etc.
3. **Canvas.renderer (Compositionnel)** : Dessiner un Organe N1 non plus comme une image `WireframeLibrary`, mais comme un conteneur qui wrap et dispose ses Cellules N2, qui à leur tour wrappent et disposent leurs Atomes N3 avec `GRID.js`.
4. **Vrai Mode Illustrateur** : Au dbl-click sur N1, pas de changement d'apparence. On active simplement les événements (`pointer-events: all`) sur les groupes subordonnés pour éditer chaque primitive.

---

### ✅ COMPTE-RENDU DE LIVRAISON : MISSION 12A (PIVOT)
**DATE : 2026-02-21**
**STATUS : DÉPLOYÉ & VALIDÉ**

#### 1. Révolution Bottom-Up ("Ce qui est au-dessus demeure en-dessous")
- L'architecture de rendu a été complètement retournée. Il n'y a plus de fausse carte ou de "WireframeLibrary" qui dessine des illusions statiques au niveau N1.
- L'image de l'Organe sur le Canvas est désormais **l'assemblage physique et récursif** des éléments SVG purs (Dessinés par l'AtomRenderer), positionnés en fonction du `layout_type` et alignés via la grille 8px mathématique de `GRID.js`.
- Le paradigme WYSIWYG est atteint : au double-clic (Drill-Down), le layout ne bronche pas d'un pixel. Les éléments (textes, boutons, rectangles) se déverrouillent simplement (`pointer-events: all`), offrant un drag & drop immédiat, en contexte.

#### 2. Intégration Sémantique des Marges
- Les niveaux de layout (`_buildComposition` dans `Canvas.renderer`) consomment directement les attributs sémantiques (la constitution `density: compact | normal | airy`) pour appeler les constantes de `GRID.js` (G.GAP_S, G.GAP, G.PAD_L).
- L'espacement n'est plus "magique", il est structurel.

> [!WARNING]
> Les atomes sont nus. Le design généré (couleurs basiques, tailles primitives) est logiquement archaïque à ce stade car l'`AtomRenderer` sémantique vient de naître et manque de CSS/variables de design riches. Le socle est sain, il faut maintenant "habiller" ces atomes (Mission Design System à venir).

---

---

### Critères d'acceptation
- [x] "Ce qui est au-dessus demeure en dessous".

---

## Mission 13A-PRE — Toggle Grid & Fond Dense SVG
STATUS: ARCHIVÉ
MODE: CODE DIRECT — FJD
ACTOR: GEMINI (Exécuteur Frontend)
VALIDATION: FJD — "La grille est top maintenant"

---

---

### Ce qui a été fait

**1. Toggle Grid / No Grid**
- Ajout bouton `⊞` (grid toggle) dans les zoom-controls de `Canvas.feature.js`
- État `this.gridVisible` dans le constructor
- Handler clic : toggle `display: block/none` sur `#svg-grid`
- Feedback visuel : bouton à 40% d'opacité quand grille masquée

**2. Déduplication de la grille**
- Grille CSS `::before` sur `#slot-canvas-zone` commentée dans :
  - `stenciler.css` (L1132-1146)
  - `stenciler_v3_additions.css` (L226-239)
- Grille unique = SVG pattern dans `Canvas.feature.js`
- Toggle fonctionne maintenant sur toute la grille

**3. Grille plus visible**
- Couleur : `var(--border-subtle, #d5d4d0)` (au lieu de `--grid-line`)
- Épaisseur : `1px` (au lieu de `0.5px`)
- Contraste suffisant en mode jour et nuit

**4. Fond SVG plus dense**
- Ajout `<rect id="svg-bg">` sous la grille avec `fill="var(--bg-secondary)"`
- Le fond hérite automatiquement du thème (jour/nuit) via CSS variables
- Mode jour : `#f0efeb` (dense, moins flottant)
- Mode nuit : `#111111` (encore plus dense, "accident heureux")

---

### Fichiers modifiés
- `Frontend/3. STENCILER/static/js/features/Canvas.feature.js` (pattern grid + toggle)
- `Frontend/3. STENCILER/static/css/stenciler.css` (commenté .canvas-zone::before)
- `Frontend/3. STENCILER/static/css/stenciler_v3_additions.css` (commenté ::before)

---

### État actuel (STABLE)

Le système est revenu à sa configuration stable. Toute modification du layout Frontend est **suspendue** jusqu'à résolution du problème de cache Service Worker.

---

---

### Ce qui fonctionne (LIVRÉ)

| Feature | Fichier | État |
|---------|---------|------|
| Toggle grid | `Canvas.feature.js` | ✅ Caché par défaut |
| Typo bas de casse | `AtomRenderer.js`, `WireframeLibrary.js` | ✅ Bold 700 |
| Fond inversé | CSS + SVG | ✅ --bg-secondary / --bg-primary |
| Backend stack | `Canvas.layout.js` | ✅ Vertical simple |

---

---

### Ce qui est BLOQUÉ

**Layouts Frontend fancy :**
- Timeline élégante avec rail
- Cartes fines (280×100px)
- Boutons pills (32px, radius 16px)
- Zigzag des positions

**Raison du blocage :**
Service Worker met en cache agressivement les modules ES6. Toute modification du code JS n'est pas prise en compte même après hard refresh. Les tentatives de cache-busting cassent le chargement.

**Solution nécessaire :**
- Soit désactiver le SW en dev
- Soit implémenter un système de version/hashing des bundles
- Soit utiliser un bundler (Vite/Webpack) qui gère le cache

---

---

### Décision

**FJD :** "Rien ne paraît. Retour à l'état stable."

**Action :** Restauration complète des fichiers JS à leur état antérieur (commit `46fb03c`).

**Prochaine étape :** Investigation du cache SW avant toute nouvelle feature de layout.

---

---

### Fichiers modifiés (LIVRÉS)
- `Canvas.feature.js` — toggle grid + fond + typo labels
- `Canvas.renderer.js` — labels bas de casse
- `AtomRenderer.js` — typo boutons + couleurs terra/ocre
- `WireframeLibrary.js` — labels bas de casse
- `stenciler.css` — grille CSS commentée
- `stenciler_v3_additions.css` — fond slot-canvas-zone

---

## Mission 13A-PRE — Protocole KIMI Sandbox & SVG-First
**DATE : 2026-02-22**
**ACTOR : GEMINI & KIMI (DA Prototypeur)**
**STATUS : OPÉRATIONNEL**

---

### 🧩 Le Problème : Cache & Fidélité
Les itérations rapides de KIMI étaient bloquées par un Service Worker trop agressif et un moteur de rendu (`AtomRenderer`) nécessitant des modifications de code pour chaque nouveau style.

---

### 🛡️ La Solution : Le Sandbox Protocol
Un environnement de prototypage isolé a été créé pour permettre à KIMI d'injecter des designs haute fidélité sans risque et sans latence de cache.

#### 1. Accès au Sandbox
L'environnement est activable via l'URL :
`http://localhost:9998/stenciler?mode=sandbox`
*Note : Cette URL bypass le cache pour les fichiers de prototypage et charge les surcharges KIMI.*

#### 2. Flux de Travail "SVG-First"
KIMI ne modifie plus le code logique du renderer. Elle injecte directement du SVG pur :
- **Injection** : Utilisation du champ `svg_payload` (ou `custom_svg`) dans le génome N3.
- **Rendu** : `AtomRenderer.js` détecte le payload et l'affiche tel quel (WYSIWYG total).
- **Provisions** : Les fichiers `static/js/AtomPrototypes.js` et `static/css/kimi_sandbox.css` sont réservés aux drafts de KIMI.

#### 3. Cycle de Validation
1. **KIMI** pousse ses payloads SVG dans le génome/sandbox.
2. **FJD** valide visuellement dans l'URL sandbox.
3. **GEMINI** effectue le "Surgical Merge" vers les fichiers de production une fois le design figé.

---


## PHASE 13A — Semantic UI & Design System (Suite)
STATUS: MISSION
MODE: aetherflow -f
ACTOR: KIMI
Règles absolues :
1. Jamais CSS/HTML dans le backend
2. Jamais GenomeStateManager côté frontend
3. Communication via API REST uniquement
4. Mode aetherflow obligatoire (sauf CODE DIRECT — FJD)
5. Validation humaine obligatoire : URL + port avant "terminé"
---

---

### Mission
Transformer l'`AtomRenderer` et le système de layout pour traduire formellement les attributs constitutionnels du génome en une interface haute fidélité.
1. Design System : Traduire `importance` (primary, secondary, ghost) pour gérer les ombres, dégradés, et contrastes.
2. Layout Spécialisé : Remplacer l'heuristique de `LayoutEngine.js` par la lecture stricte de `semantic_role` (header -> TOP). Implémenter la répartition interne `layout_type` (stack, flex, grid) dans `Canvas.renderer.js`.

---

### Contexte
- **Fichiers** : `AtomRenderer.js`, `Canvas.renderer.js`, `LayoutEngine.js`.
- Suite logique du Pivot Bottom-Up (12A).

---

## PHASE 14 — Édition Opérationnelle User
> **Vision FJD :** L'utilisateur crée et modifie directement le design. Déplacer, copier, modifier couleur/épaisseur des primitives en N3. Ces modifications persistent dans le génome et remontent en N2 puis N1 (bottom-up). La valise = palette contextuelle = Sullivan scoped au Corps courant.

---

---

### Mission 14A-FIX — Deux bugs Mode Illustrateur [MISSION ACTIVE]
**ACTOR: GEMINI | MODE: CODE DIRECT | FICHIER UNIQUE: `Canvas.feature.js`**

---
⚠️ BOOTSTRAP GEMINI
Constitution : `Frontend/1. CONSTITUTION/CONSTITUTION_AETHERFLOW_V3.md`
Input files obligatoires : `stenciler.css`, `LEXICON_DESIGN.json`
Règles : SVG natif uniquement, tokens CSS stenciler.css.
Validation humaine (FJD) obligatoire avant "terminé" — URL http://localhost:9998/stenciler + hard refresh Cmd+Shift+R.
---

#### Contexte
Deux bugs dans le Mode Illustrateur (11A) identifiés par FJD lors du test de 14A :

---

#### BUG 1 — prim-sel overlay à la mauvaise position

**Symptôme :** Le cadre de sélection bleu pointillé (`.prim-sel`) apparaît en (0,0) de l'atom-node au lieu d'entourer la primitive cliquée.

**Cause :** Dans `_selectPrimitive(prim, parentNode)`, `prim.getBBox()` retourne les coordonnées dans l'espace local du parent direct de `prim` (`atom-pure`). Mais l'overlay est appendé à `parentNode` (l'`atom-node`), dont l'espace inclut le `translate(8, 30)` de `.bottom-up-composition`. Résultat : décalage systématique de (-8, -30).

**Fix — 1 ligne :**
```js
// AVANT (ligne ~770 dans _selectPrimitive) :
parentNode.appendChild(ov);

// APRÈS :
prim.parentNode.appendChild(ov);
```
Les `querySelectorAll('.prim-sel')` dans `_selectPrimitive` et `_exitGroupEdit` cherchent sur `parentNode` (atom-node) — ils trouvent `.prim-sel` même dans les sous-groupes → cleanup inchangé.

---

#### BUG 2 — `_selectNode` appelé en mode group edit

**Symptôme :** L'atom-node reçoit la classe `selected` et son `.wf-content` passe à `opacity: 0.4` lors du clic en Mode Illustrateur.

**Cause :** Dans le handler `svg.addEventListener('click', ...)` (vers L611), quand `groupEditMode === true` ET que le clic est sur le `groupEditTarget`, la condition ne `return` pas → exécution continue → `_selectNode(node)` est appelé.

```js
// CODE ACTUEL (bugué) :
if (this.groupEditMode) {
    const node = e.target.closest('.svg-node');
    if (!node || node !== this.groupEditTarget) {
        this._exitGroupEdit();
        return;
    }
    // PAS DE RETURN ICI → tombe sur _selectNode ci-dessous
}
const node = e.target.closest('.svg-node');
if (node) { this._selectNode(node); ... }
```

**Fix — 1 ligne :**
```js
// APRÈS (ajouter return en fin du bloc groupEditMode) :
if (this.groupEditMode) {
    const node = e.target.closest('.svg-node');
    if (!node || node !== this.groupEditTarget) {
        this._exitGroupEdit();
        return;
    }
    return; // ← AJOUTER CETTE LIGNE
}
```

---

#### Fichiers à lire AVANT (OBLIGATOIRE)
1. `static/js/features/Canvas.feature.js` — sections `_selectPrimitive` (L756-789), svg click handler (L611-633), `_exitGroupEdit` (L851-901).

#### Fichiers à modifier
- `static/js/features/Canvas.feature.js` **uniquement** — 2 changements chirurgicaux.

#### Critères d'acceptation
- [x] DblClick atom → clic sur primitive → cadre bleu pointillé ENTOUR la primitive (pas coin supérieur gauche)
- [x] DblClick atom → clic primitive → atom-node NE reçoit PAS la classe `selected`
- [x] `.wf-content` reste à son opacity normale (1.0) en mode illustrateur (pas 0.4)
- [x] PrimitiveEditor panel (14A) apparaît bien avec les vraies valeurs fill/stroke de la primitive
- [x] Sortie mode illustrateur (clic extérieur) → panel ferme, opacités restaurées
- [x] Zéro régression drill N1→N2→N3
- [x] FJD valide visuellement sur http://localhost:9998/stenciler

#### ✅ COMPTE-RENDU DE LIVRAISON : MISSION 14A-FIX
**DATE : 2026-02-25**
**STATUS : DÉPLOYÉ & VALIDÉ**

1. **Correction des Coordonnées (Bug 1)** : L'overlay de sélection `.prim-sel` est désormais rattaché au parent direct de la primitive (`atom-pure`). Cela résout le décalage de positionnement en restant dans le référentiel SVG local de la composition.
2. **Isolation des Événements (Bug 2)** : Ajout d'une garde `return` dans le handler de clic global du SVG pour le mode `groupEditMode`. Cela stoppe la propagation vers `_selectNode` et évite la sélection accidentelle du conteneur parent (atom-node) lors de l'édition granulée.
3. **Stabilité UI** : L'opacité du contenu et les classes de sélection sont préservées correctement pendant et après l'édition.

---

---

### Mission 14A-SHRINK — Shrink-Wrap des conteneurs SVG [MISSION ACTIVE]
**ACTOR: GEMINI | MODE: CODE DIRECT | FICHIER UNIQUE: `Canvas.renderer.js`**

---
⚠️ BOOTSTRAP GEMINI
Constitution : `Frontend/1. CONSTITUTION/CONSTITUTION_AETHERFLOW_V3.md`
Input files obligatoires : `stenciler.css`, `LEXICON_DESIGN.json`
Règles : SVG natif uniquement, tokens CSS stenciler.css.
Validation humaine (FJD) obligatoire avant "terminé" — URL http://localhost:9998/stenciler + hard refresh Cmd+Shift+R.
---

#### Contexte

Les nœuds SVG (N3 atomes, N2 cellules, N1 organes) ont tous un `<rect class="node-bg">` dont les dimensions (`pos.w × pos.h`) proviennent du LayoutEngine — une case budgétée de taille fixe. Le contenu réel issu de `_buildComposition()` (`res.h`) est souvent bien plus petit. L'écart = espace mort invisible qui :
- Fausse les poignées de sélection (Mode Illustrateur)
- Fausse le drag & drop (cible plus grande que le visuel)
- Viole le principe Bottom-Up 12A (le parent doit émerger des enfants, pas l'inverse)

**Vision FJD :** chaque nœud SVG doit avoir exactement les dimensions de son contenu + padding. Zéro espace mort.

---

#### Fix — `Canvas.renderer.js`, méthode `renderNode()`

**Localisation :** après le bloc `_buildComposition` + redimensionnement dynamique (vers L239-244 actuels).

**Principe :** remplacer le `if (expectedH > pos.h)` (qui ne shrink jamais) par une affectation inconditionnelle :

```js
// AVANT (croissance uniquement) :
const expectedH = res.h + PAD_TOP + PAD_BOTTOM;
if (expectedH > pos.h) {
    pos.h = expectedH;
    rect.setAttribute('height', pos.h);
}

// APRÈS (shrink-wrap symétrique) :
const actualH = res.h + PAD_TOP + PAD_BOTTOM;
pos.h = actualH;
rect.setAttribute('height', actualH);
// Width : garder pos.w (largeur de colonne LayoutEngine — cohérente)
```

C'est la seule modification. Le `rect.setAttribute('width', pos.w)` existant reste intact (la largeur de colonne est intentionnelle).

---

#### Fichiers à lire AVANT (OBLIGATOIRE)
1. `static/js/Canvas.renderer.js` — entier. Focus sur `renderNode()` (L195-254) et `_buildComposition()` (L123-190).

#### Fichiers à modifier
- `static/js/Canvas.renderer.js` **uniquement** — 3 lignes remplacées dans `renderNode()`.

#### Critères d'acceptation
- [x] Un atome (N3) dont le contenu fait 48px de haut → son `node-bg` fait exactement 48 + PAD_TOP + PAD_BOTTOM px (pas 96 ou 80)
- [x] Une cellule (N2) → son `node-bg` = hauteur réelle de ses atomes empilés + gaps + padding
- [x] Un organe (N1) → même principe
- [x] En Mode Illustrateur, le cadre de sélection (`.prim-sel`) est visuellement cohérent avec l'encombrement du nœud
- [x] Drag & drop d'un nœud → la zone de clic = zone visible exacte
- [x] Zéro régression sur drill N1→N2→N3
- [x] FJD valide visuellement sur http://localhost:9998/stenciler

#### ✅ COMPTE-RENDU DE LIVRAISON : MISSION 14A-SHRINK
**DATE : 2026-02-25**
**STATUS : DÉPLOYÉ & VALIDÉ FJD**

**Fix appliqué (CODE DIRECT — FJD) :** Suppression de tous les paddings (`PAD_LEFT/TOP/RIGHT/BOTTOM`) dans `renderNode()`. `node-bg` = dimensions exactes du contenu (`res.w × res.h`), sans aucune marge ajoutée. `compGroup` à `translate(0,0)`.

Raison : l'approche précédente (`actualH = res.h + PAD_TOP + PAD_BOTTOM`) ajoutait 28px à des atomes dont le `node-label` avait été supprimé — le node **grandissait** au lieu de shrink. Zéro padding = zero espace mort = hitbox précise.

1. **Shrink-Wrap Exact** : `pos.h = res.h`, `pos.w = res.w` — node-bg épouse le bounding box du contenu sans marge.
2. **Poignées précises** : `_showHandles` lit `node-bg` attributes → handles = contenu exact, validé FJD.
3. **Zéro dette** : aucun padding fantôme, aucun centrage `offsetY` superflu.

---

---

### Bilan d'audit (lecture code)

**✅ Fait correctement :**
- Sections collapsibles : Navigation (ouverte), Genome (ouverte), Style (fermée ▸) — OK.
- `primitive:selected` câblé dans ColorPalette + BorderSlider — structure correcte.

**❌ Non fait / rejeté DA :**

**1. Mentions ésotériques dans WireframeLibrary.js — NON TOUCHÉ**

Gemini n'a pas lu `WireframeLibrary.js`. Les textes ésotériques sont là, pas dans AtomRenderer :
- `upload` L105-106 : `"déposer fichiers"`, `"PDF, PNG (Max 10MB)"` → supprimer, garder seulement la flèche SVG
- `accordion` L130, 136 : `"zones validées"`, `"ajustements"` → remplacer par rects neutres (5 chars max)
- `color-palette` L142, 148, 150 : `"palette extraite"`, `"Rounded"`, `"Geist Sans"` → supprimer
- `breadcrumb` L194, 196 : `"Phase"`, `"Section Active"` → remplacer par blocs de largeur variable neutres
- `zoom-controls` L203 : `"🔍 ZOOM"` → supprimer emoji + texte
- `brainstorm` L211 : `"💡"` → supprimer emoji, cercle seul suffit
- `stencil-card` L79, 81 : `"garder"`, `"réserve"` → supprimer (décision esthétique FJD, pas Gemini)

**Règle : zéro texte > 5 caractères dans WireframeLibrary. Formes SVG uniquement.**

---

**2. ColorPalette — couleurs hardcodées Tailwind**

Swatches actuels : `#ef4444`, `#f97316`... — palette Tailwind saturée, hors charte stenciler.
Remplacer par les tokens stenciler (hex équivalents, pas CSS vars — `input[type=color]` ne supporte pas les CSS vars) :
```js
this.swatches = [
    '#a8c5fc',  // --accent-bleu
    '#c4a589',  // --accent-terra
    '#a3c4a8',  // --accent-vert
    '#f0b8b8',  // --accent-rose
    '#c5b8f0',  // --accent-violet
    '#f0d0a8',  // --accent-ambre
    '#3d3d3c',  // --text-primary (noir chaud)
    '#f7f6f2',  // --bg-primary (crème)
];
```

---

**3. Resize — "les poignées s'agrandissent mais le rect ne bouge pas"**

**Symptôme précis (FJD) :** les 4 handles (carrés blancs) apparaissent et leur position suit le drag — mais le `<rect>` cible visuel ne change pas de taille.

**Cause probable :** `startRect` dans `_setupPrimitiveResize` capture `prim.getAttribute('width')` qui retourne `null` si la largeur du rect est définie via attribut SVG `style` ou héritage CSS. `parseFloat(null || 0) = 0`. La math donne `w = Math.max(8, 0 + dx)` — ce qui semble faire bouger le handle (via `prim.getBBox()` qui retourne le bounding box calculé incluant style) mais `setAttribute('width', 8)` écrase la valeur par une trop petite ou ne prend pas si l'attribut n'était pas présent initialement.

**Fix ciblé dans `_setupPrimitiveResize` :**

1. Remplacer la capture de `startRect` pour utiliser `getBBox()` plutôt que getAttribute :
```js
// AVANT
startRect = {
    x: parseFloat(prim.getAttribute('x') || 0),
    y: parseFloat(prim.getAttribute('y') || 0),
    w: parseFloat(prim.getAttribute('width') || 0),
    h: parseFloat(prim.getAttribute('height') || 0),
};

// APRÈS
const bbox = prim.getBBox();
startRect = { x: bbox.x, y: bbox.y, w: bbox.width, h: bbox.height };
```

2. Ajouter `pointer-events: all` sur chaque handle (après `hdl.style.cursor = cursor;`) :
```js
hdl.setAttribute('pointer-events', 'all');
```

3. **Vérification console** : après mousedown sur un handle, `console.log('startRect', startRect)` doit afficher des valeurs non-nulles. Si `w` ou `h` = 0 même après getBBox(), le problème est ailleurs (rapport requis).

---

**4. PrimitiveEditor — "pas visible en front"**

Les labels sont bien en bas de casse dans le code. Vérifier que le panel apparaît :
- Ouvrir la console, chercher l'événement `primitive:selected` après clic sur une primitive
- Si `detail.el` est null → bug d'alimentation de l'événement en amont
- Si panel reste `hidden` → vérifier que `this.panel.classList.remove('hidden')` est atteint
Rapport attendu : URL + ce que FJD voit à l'écran.

---

---

### Ce qui est CONSERVÉ (ne pas toucher)
- `Canvas.feature.js` sauf ajout `pointer-events: all` sur resize handles
- `GenomeSection.feature.js` — collapsibles OK
- `Navigation.feature.js` — collapsibles OK
- `BorderSlider.feature.js` — wiring OK
- `PrimitiveEditor.feature.js` — structure OK

---

**5. AtomRenderer.js — Textes placeholder N2/N3 (FJD : "retour en N2 N3")**

Quand on drill à N2/N3, c'est `AtomRenderer.js` qui prend le relais. Textes à supprimer :

**Case `table` (L130-148) :**
- Supprimer les `<text>` : `"ID"`, `"STATUS"`, `"ACTION"`, `"OBJ-01"`, `"OBJ-02"`, `"actif"`, `"wait"`, `"Détails"`
- Remplacer par des `<rect>` de largeur variable (simuler colonnes + data)
- Pill-status OK → sans texte intérieur

**Case `status` (L195-202) :**
- Supprimer `(actif)` hardcodé → garder uniquement le cercle coloré + une barre rect neutre (pas de `${safeName} (actif)`)

**Contrainte :** même signature `{ svg, h, w }`, même `height`, pas de changement structural.

---

---

### Fichiers à modifier pour cet amendment
1. `static/js/WireframeLibrary.js` — retirer tous les textes > 5 chars + emojis
2. `static/js/AtomRenderer.js` — case `table` + case `status` : zéro texte hardcodé
3. `static/js/features/ColorPalette.feature.js` — swatches stenciler palette
4. `static/js/features/Canvas.feature.js` — `pointer-events: all` sur resize handles (1 ligne)

---

### Critères d'acceptation
- [ ] N0/N1 (WireframeLibrary) : zéro emoji, zéro texte > 5 chars
- [ ] N2/N3 (AtomRenderer) : case table et status sans texte hardcodé — rects uniquement
- [ ] ColorPalette swatches : palette stenciler désaturée (bleu clair, terra, vert, rose, violet, ambre)
- [ ] Resize handles : 4 carrés visibles + drag = redimensionnement effectif
- [ ] FJD valide visuellement http://localhost:9998/stenciler (Cmd+Shift+R obligatoire)

---
⚠️ BOOTSTRAP GEMINI
Constitution : `Frontend/1. CONSTITUTION/CONSTITUTION_AETHERFLOW_V3.md`
Input files obligatoires : `stenciler.css`, `LEXICON_DESIGN.json`
Règles : SVG natif uniquement, tokens CSS stenciler.css. Zéro lib externe.
Validation humaine (FJD) obligatoire avant "terminé" — URL http://localhost:9998/stenciler + hard refresh Cmd+Shift+R.
---

#### Fichiers à lire AVANT (OBLIGATOIRE)
1. `static/js/AtomRenderer.js` — entier. Identifier les emojis, URLs, et placeholder texte.
2. `static/js/features/PrimitiveEditor.feature.js` — entier. Protocol événements `primitive:selected`.
3. `static/js/features/ColorPalette.feature.js`, `TSLPicker.feature.js`, `BorderSlider.feature.js` — entier chacun.
4. `static/js/features/Navigation.feature.js` — entier. Voir rendu actuel des breadcrumbs.
5. `static/css/stenciler.css` — tokens sidebar, `.sidebar-section`, `.sidebar-section-title`.

---

#### Tâche 1 — AtomRenderer : supprimer les mentions ésotériques

Dans `static/js/AtomRenderer.js`, remplacer **tous** les textes placeholder, emojis et URLs par du SVG abstrait neutre. Exemples de ce qui doit disparaître :
- `"☁️"`, `"📝 Champ 1..."`, `"📊"` — emojis hors charte
- `"Glisser-déposer le fichier ici"` — copy UX qui n'a pas à apparaître dans un wireframe
- Tout texte de plus de 12 caractères dans les rendus SVG

**Remplacement :** formes SVG schématiques. Ex. upload → un `<rect>` + flèche SVG montante. Formulaire → 2 `<rect>` empilés. Pas de texte descriptif.

---

#### Tâche 2 — PrimitiveEditor : labels bas de casse

Dans `static/js/features/PrimitiveEditor.feature.js`, L30-46 :
- `"FOND"` → `"fond"`
- `"CONTOUR"` → `"contour"`
- `"ÉPAIS."` → `"épais."`
- `"OPAC."` → `"opac."`
- `"PRIMITIVE"` dans le header → `"primitive"`
- Vérifier et passer tous les autres labels en bas de casse

---

#### Tâche 3 — Sidebar-right : câbler ColorPalette + BorderSlider sur primitive:selected

**Contexte :** `PrimitiveEditor.feature.js` dispatche `primitive:selected` avec `detail.prim` (référence directe à l'élément SVG). Les features sidebar-right existent mais n'écoutent pas cet événement.

**Dans `ColorPalette.feature.js`** — ajouter dans `init()` :
```js
document.addEventListener('primitive:selected', (e) => {
    this._activePrim = e.detail.prim;
    this._el.style.opacity = '1';
    this._el.style.pointerEvents = 'all';
});
document.addEventListener('primitive:deselected', () => {
    this._activePrim = null;
    this._el.style.opacity = '0.4';
    this._el.style.pointerEvents = 'none';
});
```
Et dans le handler clic sur un swatch :
```js
if (this._activePrim) this._activePrim.setAttribute('fill', swatchColor);
```

**Dans `BorderSlider.feature.js`** — même pattern. Sur change du slider :
```js
if (this._activePrim) this._activePrim.setAttribute('stroke-width', value);
```

**TSLPicker** — désactiver complètement (commenter le montage dans `stenciler_v3_main.js`) : trop complexe pour l'usage actuel, slot laissé vide.

---

#### Tâche 4 — Sidebar-left : sections collapsibles

Dans `static/js/features/GenomeSection.feature.js` et `NavigationFeature` :
- Chaque `sidebar-section` : les sections sont ouvertes par défaut
- Passer **toutes** les sections à fermées par défaut (`content.style.display = 'none'`)
- **Sauf 2 :** Navigation + Genome — les deux sections de gauche les plus utilisées restent ouvertes
- Titre de section = clickable pour toggle → `cursor: pointer`, chevron `▸` / `▾`

---

#### Tâche 5 — Breadcrumbs sidebar-left : layout fixe

Dans `static/js/features/Navigation.feature.js`, le rendu des breadcrumbs (chemin de drill-down) :
- Remplacer le rendu flex actuel par une liste verticale `<ul>` avec `list-style: none`, `padding: 0`, `margin: 0`
- Chaque item : une ligne `font-size: 11px`, `color: var(--text-secondary)`, séparateur `›` en `var(--text-muted)` **avant** chaque item sauf le premier
- Dernier item (courant) : `color: var(--text-primary)`, `font-weight: 600`
- Pas de flex, pas de nowrap — les noms longs wrappent naturellement

---

#### Tâche 6 — Sidebar-right : display propre

Dans `static/css/stenciler_v3_additions.css` ou inline dans les features sidebar-right :
- Listes de swatches : `list-style: none`, `padding: 0`, `margin: 0`, swatches en `display: flex; flex-wrap: wrap; gap: 4px`
- Labels des contrôles : `font-size: 10px`, `color: var(--text-muted)`, bas de casse
- Sliders : `width: 100%`, `accent-color: var(--accent-bleu)`
- Séparation visuelle entre sections : `border-top: 1px solid var(--border-subtle)`, `padding-top: 8px`

---

#### Critères d'acceptation
- [x] AtomRenderer : zéro emoji, zéro placeholder text > 12 chars dans les wireframes SVG
- [x] PrimitiveEditor : tous les labels en bas de casse
- [x] Sidebar-right ColorPalette : clic swatch applique fill sur primitive active
- [x] Sidebar-right BorderSlider : slider applique stroke-width sur primitive active
- [x] Sidebar-left sections : toutes fermées par défaut sauf Navigation + Genome
- [x] Toggle section : titre cliquable, chevron ▸/▾
- [x] Breadcrumbs : liste verticale, pas de flex, wrap naturel
- [x] Sidebar-right : layout propre, list-style none, labels 10px muted
- [x] Zéro régression sur drill, Mode Illustrateur, PrimOverlay
- [x] FJD valide visuellement sur http://localhost:9998/stenciler

---

---

### Contexte
Post-livraison 14C-UX, FJD a identifié 4 bugs/oublis résiduels. Mission bloquante avant 14C/14D.

---

**1. ComponentsZone.feature.js — Sidebar N3 : supprimer mentions HTTP/endpoint**

La sidebar N2/N3 affiche des cartes atome avec une interface développeur : GET/POST/PUT/DELETE/PATCH selector + URL endpoint input. Ces mentions ésotériques doivent disparaître du canvas DA.

Fichier : `static/js/features/ComponentsZone.feature.js`
Classe cible : `component-card atom-card edit-mode`

À supprimer :
- Classe `edit-mode` sur les cartes atome
- `<select>` méthode HTTP (GET/POST/PUT/DELETE/PATCH)
- `<div class="atom-endpoint-row">` + son label "URL:" + son input endpoint
- `atom-endpoint-input`

À conserver :
- `atom-name-input` (nom de l'atome)
- `atom-desc-input` (textarea description)

---

**2. Canvas.feature.js `_setupPrimitiveResize` — startRect via getBBox() (pas getAttribute)**

Symptôme FJD : "Les poignées s'agrandissent mais le rect lui ne bouge pas."

Cause : `startRect` utilise `prim.getAttribute('width')` → retourne `null` si largeur définie via style ou héritage CSS → `parseFloat(null || 0) = 0` → le rect reçoit `setAttribute('width', dx)` = quasi-nul.

Fix ciblé :
```js
// AVANT (bugué — getAttribute retourne null)
startRect = {
    x: parseFloat(prim.getAttribute('x') || 0),
    y: parseFloat(prim.getAttribute('y') || 0),
    w: parseFloat(prim.getAttribute('width') || 0),
    h: parseFloat(prim.getAttribute('height') || 0),
};

// APRÈS (fix — getBBox() retourne toujours le bounding box calculé)
const bbox = prim.getBBox();
startRect = { x: bbox.x, y: bbox.y, w: bbox.width, h: bbox.height };
```

---

**3. Canvas.feature.js PrimOverlay — persistence inter-niveaux**

Symptôme FJD : "Le déplacement des objets en Nn-1 ne demeure pas en Nn."

Après modification d'une primitive en Mode Illustrateur, retour au niveau parent, re-drill → modifications perdues.

Vérifier dans `_exitGroupEdit` :
- Le SVG modifié est bien capturé dans `PrimOverlay` avec la bonne clé `nodeId`
- La clé `nodeId` est stable (pas générée dynamiquement à chaque render)
- Dans `_buildComposition`, `PrimOverlay.get(nodeId)` est consulté avant `renderAtom`

Si le bug persiste après audit : ajouter `console.log('[PrimOverlay]', nodeId, PrimOverlay.get(nodeId))` et reporter dans le compte-rendu.

---

**4. Canvas.renderer.js `_buildComposition` — WireframeLibrary avant renderAtom**

Vision Bottom-Up originale (Mission 12A) : atomes rendus via WireframeLibrary en priorité, `renderAtom` = fallback si aucun wireframe ne correspond. Cette architecture a été oubliée lors du refactor.

Dans la branche atome de `_buildComposition`, insérer avant l'appel `renderAtom` :
```js
// Tenter WireframeLibrary via visual_hint ou interaction_type
const hint = _matchHint(data);
if (hint) {
    const wfResult = WireframeLibrary.getSVG(hint, color, pos.w, pos.h);
    if (wfResult && wfResult.svg) return wfResult;
}
// Fallback
return renderAtom(data.interaction_type, data.name, pos, color);
```

---

---

### Fichiers à modifier
1. `static/js/features/ComponentsZone.feature.js` — supprimer edit-mode + HTTP controls
2. `static/js/features/Canvas.feature.js` — fix startRect getBBox dans `_setupPrimitiveResize` + audit PrimOverlay
3. `static/js/Canvas.renderer.js` — insérer check WireframeLibrary avant renderAtom dans `_buildComposition`

---

### Critères d'acceptation
- [ ] N2/N3 sidebar : zéro select HTTP, zéro endpoint input, zéro classe `edit-mode` visible
- [ ] Mode Illustrateur : drag poignée → le `<rect>` se redimensionne visuellement (pas seulement les handles)
- [ ] Déplacement primitive en Nn-1 → re-drill Nn → modification persistée
- [ ] Atomes N2/N3 : WireframeLibrary utilisée si hint correspond, renderAtom sinon
- [ ] FJD valide visuellement http://localhost:9998/stenciler (Cmd+Shift+R obligatoire)

---
⚠️ BOOTSTRAP GEMINI
Constitution : `Frontend/1. CONSTITUTION/CONSTITUTION_AETHERFLOW_V3.md`
Input files obligatoires : `stenciler.css`, `LEXICON_DESIGN.json`
Règles : SVG natif uniquement, tokens CSS stenciler.css. Zéro lib externe.
Validation humaine (FJD) obligatoire avant "terminé" — URL http://localhost:9998/stenciler + hard refresh Cmd+Shift+R.
---

---

---

### Mission 14C — Copie/Duplication Atomes (EN ATTENTE)
**STATUS: EN ATTENTE | ACTOR: GEMINI**

Depuis le canvas, clic droit sur un atome N3 → menu contextuel : Dupliquer, Supprimer.
La copie est ajoutée à la cell N2 courante (génome en mémoire). Write-back via 14B.

---

---

### Mission 14D — Valise (Sullivan Embedded) (EN ATTENTE)
**STATUS: EN ATTENTE (après 14B) | ACTOR: GEMINI**

`slot-preview-band` (zone basse) = Sullivan scoped filtré par Corps courant.
- Hiérarchie en scroll horizontal : Organes N1 → Cells N2 → Atomes N3
- Clic item → focus nœud dans le Canvas + ouvre PrimitiveEditor (14A)
- Synchro via `genome:corps-changed` dispatché par Canvas quand `currentCorpsId` change

---

---

### Mission 14E-WF — Nouveaux Wireframes (POST-14A, via KIMI Sandbox)
**STATUS: EN ATTENTE (après 14E-ICONS) | ACTOR: KIMI → GEMINI**

Nouveaux types dans WireframeLibrary.js : `tabs`, `dropdown`, `card-media`, `stepper`, `badge-group`, `timeline`.
Cycle : KIMI génère `svg_payload` dans génome sandbox → FJD valide → GEMINI merge dans WireframeLibrary.
Sources d'inspiration : Flowbite Blocks, Radix Primitives, shadcn/ui (layouts, pas les implémentations React).

---

---

### Backlog Phase 14

| ID | Mission | Actor | Statut |
|----|---------|-------|--------|
| 14-CACHE | Fix cache ES6 | Claude | ✅ Livré |
| 14A | Panel Édition Primitives | Claude | ✅ Livré |
| 14E-ICONS | Icônes SVG AtomRenderer | Claude | ✅ Livré |
| 14B | Write-back Génome | Claude + Gemini | ✅ Livré |
| 14B-RESIZE| Redimensionnement Primitives | Gemini | ✅ Livré |
| 14C-UX | Polish Sidebar & AtomRenderer | Gemini | ✅ Livré |
| 14F-BUGS | Bugs persistants + Bottom-Up WF | Gemini | 🔴 MISSION ACTIVE |
| 14C | Copie/Duplication | Gemini | ⏳ EN ATTENTE |
| 14D | Sullivan Embedded | Gemini | ⏳ EN ATTENTE |
| 14D | Valise (Sullivan Embedded) | Gemini | ⏳ EN ATTENTE |
| 14E-WF | Nouveaux Wireframes (sandbox) | KIMI → Gemini | ⏳ EN ATTENTE |
| 15F | SVG Wireframe Harvesting | Gemini | ✅ LIVRÉ |

---

## Phase 15 — Semantic Layout Intelligence

> **Vision :** Les propositions par défaut du Stenciler doivent être exploitables immédiatement.
> Chaque atome du génome a un `visual_hint` explicite — mais 15 des 25 valeurs présentes dans
> `genome_reference.json` n'ont aucun cas dans `WireframeLibrary.js` et tombent sur `renderAtom` générique.
> Phase 15 = fermer ce gap + construire un système de matching sémantique extensible.

---

---

### Bootstrap Gemini (obligatoire)
```
Tu travailles sur AetherFlow Stenciler V3. Lis les fichiers suivants AVANT de coder :
1. Frontend/3. STENCILER/static/js/features/Canvas.feature.js — focus _renderCorps() L.144-168
2. Frontend/3. STENCILER/static/js/LayoutEngine.js — comprendre proposeLayout()
3. Frontend/1. CONSTITUTION/LEXICON_DESIGN.json — contrat CSS
4. Frontend/1. CONSTITUTION/CONSTITUTION_AETHERFLOW_V3.md — frontières acteurs

input_files obligatoires : stenciler.css, LEXICON_DESIGN.json
```

---

### Contexte

La route `/api/infer_layout` (POST) est opérationnelle sur `server_9998_v2.py`.

Elle prend en entrée une liste d'organes N1 et retourne leurs paramètres de layout sémantique :
```json
{
  "result": {
    "n1_navigation": { "role": "navigation", "zone": "header", "w": 1024, "h": 48, "layout": "flex" },
    "n1_canvas":     { "role": "canvas",     "zone": "canvas", "w": 1024, "h": "full", "layout": "free" }
  },
  "tier": "heuristic"
}
```

**Modes disponibles :** `heuristic` (offline, défaut) | `llm` (Gemini 3 Flash) | `llm_context` (LLM + contexte projet).

Actuellement, `_renderCorps()` utilise `LayoutEngine.proposeLayout()` — une heuristique JS embarquée.
L'objectif est de **remplacer cet appel par `/api/infer_layout`** pour des positions sémantiquement informées.

---

### Tâche unique — Modifier `_renderCorps()` dans Canvas.feature.js

**Fichier cible :** `Frontend/3. STENCILER/static/js/features/Canvas.feature.js`

**Modification de `_renderCorps(corpsId)`** (actuellement L.144-168) :

1. Extraire la liste d'organes depuis `phaseData.n1_sections`
2. Appeler `POST /api/infer_layout` avec `mode: "heuristic"` (sync via `await fetch(...)`)
3. Mapper la réponse en `positions[]` compatibles avec l'existant (x/y/w/h/id)
4. Conserver le fallback `LayoutEngine.proposeLayout()` si l'API est indisponible (try/catch)
5. Ajouter un bouton `#btn-infer-llm` dans le markup `.zoom-controls` : "✨ LLM Layout"
   - Ce bouton appelle la même route avec `mode: "llm"` et `model: "gemini-3-flash-preview"`
   - Puis re-render le corps courant avec le nouveau layout

**Mapping zone → coordonnées SVG (référence 1200×900 existant dans LayoutEngine.js) :**
```
header       → x: 20,    y: 10,   w: infer_w ou 1160, h: infer_h ou 48
sidebar_left → x: 20,    y: 70,   w: infer_w ou 200,  h: auto (fill)
sidebar_right→ x: 980,   y: 70,   w: infer_w ou 200,  h: auto
main         → x: 240,   y: 70,   w: infer_w ou 720,  h: infer_h ou 400
canvas       → x: 20,    y: 70,   w: 1160,            h: 760
preview_band → x: 20,    y: 820,  w: 1160,            h: infer_h ou 120
footer       → x: 20,    y: 870,  w: 1160,            h: infer_h ou 48
```

Pour `h: "auto"` → utiliser la hauteur calculée par le nombre de N2 : `60 + organe.n2_features.length * 20`
Pour `h: "full"` → utiliser la hauteur max disponible (760)
Pour `w: "full"` → utiliser 1160

**Signature de `_renderCorps` après modification :**
```javascript
async _renderCorps(corpsId) {
    // ... setup existant ...
    let positions;
    try {
        const organs = phaseData.n1_sections.map(o => ({
            id: o.id,
            name: o.name || '',
            n2_count: (o.n2_features || []).length
        }));
        const res = await fetch('/api/infer_layout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ organs, mode: 'heuristic' })
        });
        const { result } = await res.json();
        positions = this._inferResultToPositions(result, phaseData.n1_sections);
    } catch (e) {
        console.warn('[16A] infer_layout fallback:', e);
        const layout = LayoutEngine.proposeLayout(phaseData);
        positions = layout.positions;
        this._applyLayout(layout);
    }
    // ... render loop existant ...
}
```

**Méthode helper à ajouter `_inferResultToPositions(result, sections)` :**
```javascript
_inferResultToPositions(result, sections) {
    const ZONE_X = {
        header: 20, sidebar_left: 20, sidebar_right: 980,
        main: 240, canvas: 20, preview_band: 20, footer: 20
    };
    const ZONE_Y = {
        header: 10, sidebar_left: 70, sidebar_right: 70,
        main: 70, canvas: 70, preview_band: 820, footer: 870
    };
    // stack multiple sections dans la même zone (offset vertical)
    const zoneCounters = {};
    return sections.map(s => {
        const inf = result[s.id] || { zone: 'main', w: 240, h: 'auto', layout: 'stack' };
        const zone = inf.zone || 'main';
        zoneCounters[zone] = zoneCounters[zone] || 0;
        const gap = zoneCounters[zone] * 130;
        zoneCounters[zone]++;
        const rawW = inf.w === 'full' ? 1160 : (typeof inf.w === 'number' ? inf.w : 240);
        const n2 = (s.n2_features || []).length;
        const rawH = inf.h === 'full' ? 760 : (inf.h === 'auto' ? 60 + n2 * 20 : (typeof inf.h === 'number' ? inf.h : 96));
        return {
            id: s.id,
            x: ZONE_X[zone] ?? 240,
            y: (ZONE_Y[zone] ?? 70) + gap,
            w: rawW,
            h: rawH,
            zone
        };
    });
}
```

**Bouton LLM à ajouter dans `mount()`** — dans le bloc `zoom-controls` existant, après `#btn-export-svg` :
```html
<button id="btn-infer-llm" title="Re-inférer layout via LLM">✨</button>
```

**Handler du bouton** dans `init()` :
```javascript
this.el.querySelector('#btn-infer-llm')?.addEventListener('click', async () => {
    if (!this.currentCorpsId) return;
    const phaseData = this.genome?.n0_phases?.find(p => p.id === this.currentCorpsId);
    if (!phaseData) return;
    const organs = phaseData.n1_sections.map(o => ({
        id: o.id, name: o.name || '', n2_count: (o.n2_features || []).length
    }));
    try {
        const res = await fetch('/api/infer_layout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ organs, mode: 'llm', model: 'gemini-3-flash-preview' })
        });
        const { result, tier } = await res.json();
        console.log(`[16A] LLM layout tier: ${tier}`, result);
        this.viewport.innerHTML = '';
        const positions = this._inferResultToPositions(result, phaseData.n1_sections);
        // update viewBox
        this.viewBox = { x: 0, y: 0, w: 1200, h: 900 };
        this.svg.setAttribute('viewBox', '0 0 1200 900');
        const CORPS_COLORS = { n0_brainstorm: '#d4b2bc', n0_backend: '#a8c5fc', n0_frontend: '#a8dcc9', n0_deploy: '#edd0b0' };
        const accentColor = CORPS_COLORS[this.currentCorpsId] || '#cbd5e1';
        phaseData.n1_sections.forEach((organe) => {
            let pos = positions.find(p => p.id === organe.id);
            if (organe._layout) pos = { ...pos, ...organe._layout };
            if (pos) this._renderNode(organe, pos, accentColor, 0);
        });
    } catch (e) {
        console.error('[16A] LLM infer failed:', e);
    }
});
```

---

### Contraintes

- `_renderCorps` devient `async` → tous les appelants qui utilisent `await this._renderCorps(...)` doivent être vérifiés (notamment `_drillUp`)
- Ne pas supprimer l'import `LayoutEngine` (fallback)
- Ne pas modifier `_renderOrgane()` ni `_renderCellule()` (hors scope)
- `input_files` obligatoires : `stenciler.css`, `LEXICON_DESIGN.json`
- Ne rien modifier dans `Canvas.renderer.js`, `AtomRenderer.js`, `WireframeLibrary.js`

---

### Critères d'acceptation

- [ ] `_renderCorps()` est `async` et appelle `/api/infer_layout?mode=heuristic`
- [ ] Les organes se positionnent dans leurs zones sémantiques (nav en haut, sidebar à droite, etc.)
- [ ] Bouton `✨` visible dans la barre de zoom
- [ ] Click `✨` → re-layout via LLM → organes se repositionnent
- [ ] Fallback silencieux si serveur down (LayoutEngine.proposeLayout() reprend la main)
- [ ] FJD valide visuellement sur http://localhost:9998/stenciler (Cmd+Shift+R obligatoire)

---

## Mission 16B — Zone Layout Resolver : Placement sans collision [MISSION ACTIVE]

**ACTOR : GEMINI**
**DATE : 2026-03-01**
**STATUS : LIVRÉ — EN ATTENTE VALIDATION FJD**

---

### Bootstrap Gemini (obligatoire)
```
Tu travailles sur AetherFlow Stenciler V3. Lis avant de coder :
1. Frontend/3. STENCILER/static/js/features/Canvas.feature.js — focus _inferResultToPositions() L.191-220
2. Frontend/1. CONSTITUTION/LEXICON_DESIGN.json

input_files obligatoires : stenciler.css, LEXICON_DESIGN.json
```

---

### Contexte

`_inferResultToPositions()` (Mission 16A) place les organes zone par zone mais ignore les collisions :
- Plusieurs organes dans `sidebar_right` → superposés à x:980 avec seulement 130px de gap
- Zones `canvas` et `main` se chevauchent (même x:20/240, même y:70)
- Hauteur fixe à `130px` indépendante du contenu réel

L'objectif est de remplacer `_inferResultToPositions` par `_zoneTemplateToPositions` — un **layout resolver** inspiré des page templates Flowbite/shadcn qui élimine les collisions.

---

### Tâche unique — Remplacer `_inferResultToPositions` dans Canvas.feature.js

**Fichier cible :** `Frontend/3. STENCILER/static/js/features/Canvas.feature.js`

#### Constantes de layout (canvas SVG = 1200 × 900)

```javascript
// Zones fixes (priority order)
const ZONE_DEFS = {
    header:       { x: 0,    y: 0,   w: 1200, fixedH: 56  },
    footer:       { x: 0,    y: 840, w: 1200, fixedH: 48  },
    preview_band: { x: 0,    y: 720, w: 1200, fixedH: 120 },
    sidebar_left: { x: 0,    y: 56,  w: 240,  fixedH: null }, // h = fill
    sidebar_right:{ x: 960,  y: 56,  w: 240,  fixedH: null }, // h = fill
    main:         { x: null, y: 56,  w: null,  fixedH: null }, // x/w = computed
    canvas:       { x: null, y: 56,  w: null,  fixedH: null }, // x/w = computed
};
```

`main` et `canvas` sont des zones "élastiques" : leur x et w dépendent des sidebars présentes.

#### Algorithme `_zoneTemplateToPositions(result, sections)`

**Étape 1 — Grouper les organes par zone :**
```javascript
const byZone = {};
sections.forEach(s => {
    const zone = result[s.id]?.zone || 'main';
    if (!byZone[zone]) byZone[zone] = [];
    byZone[zone].push({ section: s, inf: result[s.id] || {} });
});
```

**Étape 2 — Calculer la hauteur d'un organe (contenu réel) :**
```javascript
const organH = (s, inf) => {
    if (inf.h === 'full') return 640;
    if (typeof inf.h === 'number' && inf.h > 0) return inf.h;
    return Math.max(72, 48 + (s.n2_features?.length || 0) * 24); // 48px base + 24px/N2
};
```

**Étape 3 — Calculer x/w des zones élastiques selon sidebars présentes :**
```javascript
const hasLeft  = !!(byZone.sidebar_left?.length);
const hasRight = !!(byZone.sidebar_right?.length);
const mainX = hasLeft  ? 248 : 8;
const mainW = 1200 - mainX - (hasRight ? 248 : 8);
// canvas occupe le même espace que main (mutuellement exclusifs en pratique)
```

**Étape 4 — Distribuer les organes dans chaque zone sans collision :**

Règles par zone :
- **`header`** : distribution horizontale (flex). Diviser `w:1200` en N parts égales, h = `fixedH: 56`. Si 1 seul organe → `w:1200`.
- **`footer`** : idem header, `fixedH:48`.
- **`preview_band`** : idem header, `fixedH:120`.
- **`sidebar_left` / `sidebar_right`** : stack vertical. Chaque organe à son `w` (240 max), `h = organH(s, inf)`. Y cumulatif depuis `y:56` avec `gap:8`.
- **`main`** : si ≤ 3 organes → stack vertical avec `gap:16`. Si > 3 → grille 2 colonnes, `colW = floor(mainW/2) - 8`, `gap:16`.
- **`canvas`** : 1 seul organe attendu → prend tout l'espace elastic (`x:mainX, y:56, w:mainW, h:640`).
- **`unknown`/autres** : stack dans `main`.

**Étape 5 — Retourner le tableau `positions[]` :**
Format identique à l'existant : `{ id, x, y, w, h, zone }`.

#### Code complet de la méthode

```javascript
_zoneTemplateToPositions(result, sections) {
    const GAP = 8;

    // Grouper par zone
    const byZone = {};
    sections.forEach(s => {
        const zone = result[s.id]?.zone || 'main';
        (byZone[zone] = byZone[zone] || []).push({ s, inf: result[s.id] || {} });
    });

    // Hauteur adaptative d'un organe
    const organH = (s, inf) => {
        if (inf.h === 'full') return 640;
        if (typeof inf.h === 'number' && inf.h > 0) return inf.h;
        return Math.max(72, 48 + (s.n2_features?.length || 0) * 24);
    };

    // Zones élastiques
    const hasLeft  = !!(byZone.sidebar_left?.length);
    const hasRight = !!(byZone.sidebar_right?.length);
    const mainX = hasLeft  ? 248 : 8;
    const mainW = 1200 - mainX - (hasRight ? 248 : 8);

    const positions = [];

    // --- HEADER (flex horizontal) ---
    (byZone.header || []).forEach((item, i, arr) => {
        const colW = Math.floor(1200 / arr.length);
        positions.push({ id: item.s.id, x: i * colW, y: 0, w: colW, h: 56, zone: 'header' });
    });

    // --- FOOTER (flex horizontal) ---
    (byZone.footer || []).forEach((item, i, arr) => {
        const colW = Math.floor(1200 / arr.length);
        positions.push({ id: item.s.id, x: i * colW, y: 840, w: colW, h: 48, zone: 'footer' });
    });

    // --- PREVIEW BAND (flex horizontal) ---
    (byZone.preview_band || []).forEach((item, i, arr) => {
        const colW = Math.floor(1200 / arr.length);
        positions.push({ id: item.s.id, x: i * colW, y: 720, w: colW, h: 120, zone: 'preview_band' });
    });

    // --- SIDEBAR LEFT (stack vertical) ---
    let sy = 56;
    (byZone.sidebar_left || []).forEach(item => {
        const h = organH(item.s, item.inf);
        positions.push({ id: item.s.id, x: 0, y: sy, w: 240, h, zone: 'sidebar_left' });
        sy += h + GAP;
    });

    // --- SIDEBAR RIGHT (stack vertical) ---
    sy = 56;
    (byZone.sidebar_right || []).forEach(item => {
        const h = organH(item.s, item.inf);
        positions.push({ id: item.s.id, x: 960, y: sy, w: 240, h, zone: 'sidebar_right' });
        sy += h + GAP;
    });

    // --- CANVAS (prend tout l'espace élastique) ---
    (byZone.canvas || []).forEach(item => {
        positions.push({ id: item.s.id, x: mainX, y: 56, w: mainW, h: 640, zone: 'canvas' });
    });

    // --- MAIN (stack vertical ou 2-col si > 3) ---
    const mainItems = [...(byZone.main || []), ...(byZone.unknown || [])];
    if (mainItems.length <= 3) {
        let my = 56;
        mainItems.forEach(item => {
            const h = organH(item.s, item.inf);
            const w = typeof item.inf.w === 'number' ? Math.min(item.inf.w, mainW) : mainW;
            positions.push({ id: item.s.id, x: mainX, y: my, w, h, zone: 'main' });
            my += h + 16;
        });
    } else {
        const colW = Math.floor(mainW / 2) - GAP;
        let col0y = 56, col1y = 56;
        mainItems.forEach((item, i) => {
            const col = i % 2;
            const h = organH(item.s, item.inf);
            const x = col === 0 ? mainX : mainX + colW + GAP * 2;
            const y = col === 0 ? col0y : col1y;
            positions.push({ id: item.s.id, x, y, w: colW, h, zone: 'main' });
            if (col === 0) col0y += h + 16;
            else col1y += h + 16;
        });
    }

    return positions;
}
```

**Remplacer aussi les 2 appels à `_inferResultToPositions` par `_zoneTemplateToPositions` :**
- L.167 : `positions = this._inferResultToPositions(result, phaseData.n1_sections);`
- L.1169 : `const positions = this._inferResultToPositions(result, phaseData.n1_sections);`

**Supprimer** l'ancienne méthode `_inferResultToPositions` (L.191-220).

**Mettre à jour le viewBox** en fin de `_zoneTemplateToPositions` : le canvas est toujours `1200 × 900`. Pas de changement à faire, le viewBox est déjà `0 0 1200 900` dans `_renderCorps`.

---

### Contraintes

- Ne toucher que `Canvas.feature.js`
- Ne pas modifier `_renderOrgane()`, `_renderCellule()`, `Canvas.renderer.js`, `AtomRenderer.js`
- Ne pas modifier l'import `LayoutEngine` (fallback toujours actif)
- `input_files` obligatoires : `stenciler.css`, `LEXICON_DESIGN.json`

---

### Critères d'acceptation

- [ ] Plus aucun organe superposé sur le canvas N0 (Corps view)
- [ ] Navigation/toolbar → bande horizontale haute
- [ ] Sidebars → colonne droite ou gauche sans overflow
- [ ] Main/editor/dashboard → zone centrale, stack ou grille selon count
- [ ] Footer/deploy → bande basse
- [ ] Bouton `✨` re-layout LLM fonctionne toujours
- [ ] Fallback LayoutEngine toujours actif si fetch échoue
- [ ] FJD valide visuellement sur http://localhost:9998/stenciler (Cmd+Shift+R obligatoire)

---

## Mission 17A — Real Wireframes at N0 ✅ ARCHIVÉ
> Voir [ROADMAP_ACHIEVED.md](ROADMAP_ACHIEVED.md) — SemanticMatcher + Canvas.renderer.js level===0 block.

---

## Mission 18A — Genome HTML Preview (Flowbite) ✅ ARCHIVÉ
> Voir [ROADMAP_ACHIEVED.md](ROADMAP_ACHIEVED.md) — `/preview` route + genome_preview.py.

---

## Mission V3-A — Backend Dead Code Cleanup ✅ ARCHIVÉ (PARTIEL)
> Voir [ROADMAP_ACHIEVED.md](ROADMAP_ACHIEVED.md) — 20 fichiers .generated.py supprimés. Tâche 2 bloquée (appelants dans workflows zombie).

---

## État Stratégique — 2026-03-02

---

### Acquis
- **Stenciler V3** : drill-down N0→N1→N2→N3 opérationnel. Bottom-up SVG. Mode Illustrateur. Persistence RAM.
- **Genome Preview** : `/preview` rend le genome en vrais composants Flowbite HTML (lecture directe, sans inférence).
- **AetherFlow V3-A** : dead code supprimé, 21/21 tests PASS. Pipeline actif intact.

---

### Contexte

`/preview` est une page HTML read-only générée par `genome_preview.py`.
Les endpoints PATCH sont **déjà implémentés** dans `server_9998_v2.py` (Claude, 2026-03-02) :
- `PATCH /api/genome/node/<id>` — body: `{ "field": "name"|"visual_hint", "value": "..." }`
- `PATCH /api/genome/organ/<organ_id>/reorder` — body: `{ "order": ["n3_id_1", ...] }`

**Ta seule tâche : modifier `genome_preview.py` pour injecter le JS d'édition inline.**

---

---

### Fichiers à lire AVANT de coder (OBLIGATOIRE)

1. `Frontend/3. STENCILER/genome_preview.py` — entier. Comprendre `_comp_html()`, `_render_organ_card()`, `render_genome_preview()`. C'est là que tu injectes le JS.
2. `Frontend/3. STENCILER/server_9998_v2.py` — lire uniquement `do_PATCH`, `_handle_node_patch`, `_handle_organ_reorder`. Contrat API figé, ne pas modifier.

**Input files obligatoires :** `stenciler.css`, `LEXICON_DESIGN.json`

---

---

### Bootstrap Gemini (obligatoire)

```
Tu es Gemini, agent frontend AetherFlow. Tu travailles sur genome_preview.py.
Ton rôle : injecter du JS d'édition inline dans la page HTML générée.
Tu NE modifies PAS server_9998_v2.py. Les endpoints PATCH sont déjà prêts.
FJD = Directeur Artistique. Aucune décision esthétique non demandée.
Utilise Flowbite et Tailwind déjà présents dans la page (CDN déjà chargé).
```

---

---

### Tâche 1 — F1 : Rename inline (contenteditable)

Dans `_comp_html(comp)`, chaque composant a déjà `data-genome-id="{gid}"`.

**Modifier le rendu des labels pour les rendre éditables :**
- Identifier le texte de label dans chaque composant (le `name` du composant)
- L'entourer d'un `<span class="genome-label" data-genome-id="{gid}">` avec `contenteditable="false"`
- Ajouter dans le `<script>` de la page (via `render_genome_preview`) :

```javascript
// F1 — Rename inline
document.querySelectorAll('.genome-label').forEach(span => {
  span.addEventListener('dblclick', () => {
    span.contentEditable = 'true';
    span.focus();
  });
  span.addEventListener('blur', async () => {
    span.contentEditable = 'false';
    const id = span.dataset.genomeId;
    const value = span.textContent.trim();
    await fetch(`/api/genome/node/${id}`, {
      method: 'PATCH',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ field: 'name', value })
    });
  });
});
```

---

---

### Tâche 2 — F2 : Changer le visual_hint (menu contextuel)

**Liste des hints disponibles** (hard-codée, pas de fetch) :
`button`, `launch-button`, `stepper`, `breadcrumb`, `chat/bubble`, `chat-input`,
`choice-card`, `dashboard`, `accordion`, `upload`, `color-palette`, `grid`,
`table`, `stencil-card`, `detail-card`, `preview`, `modal`, `download`,
`zoom-controls`, `form`

**Ajouter un bouton ⚙ sur chaque composant** (dans `_comp_html`) :

```html
<div class="genome-comp-wrapper relative group" data-genome-id="{gid}" data-hint="{vh}">
  <!-- le composant existant ici -->
  <button class="hint-picker absolute top-0 right-0 hidden group-hover:block
                 text-xs bg-gray-700 text-white rounded px-1 py-0.5 z-10"
          data-genome-id="{gid}">⚙</button>
</div>
```

**JS dans la page** :

```javascript
// F2 — Change visual_hint
const HINTS = ['button','launch-button','stepper','breadcrumb','chat/bubble',
  'chat-input','choice-card','dashboard','accordion','upload','color-palette',
  'grid','table','stencil-card','detail-card','preview','modal','download',
  'zoom-controls','form'];

document.querySelectorAll('.hint-picker').forEach(btn => {
  btn.addEventListener('click', async (e) => {
    e.stopPropagation();
    const id = btn.dataset.genomeId;
    const current = btn.closest('[data-hint]').dataset.hint;
    const chosen = prompt(`Visual hint actuel: ${current}\nChoisir:\n${HINTS.join(', ')}`, current);
    if (!chosen || !HINTS.includes(chosen)) return;
    await fetch(`/api/genome/node/${id}`, {
      method: 'PATCH',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ field: 'visual_hint', value: chosen })
    });
    location.reload();
  });
});
```

⚠️ `prompt()` est suffisant pour un outil interne. Pas besoin de modal custom.

---

---

### Tâche 3 — F3 : Drag-and-drop (SortableJS)

**Ajouter SortableJS CDN** dans le `<head>` de `render_genome_preview()` :
```html
<script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.2/Sortable.min.js"></script>
```

**Modifier `_render_organ_card(organ)`** pour ajouter `data-organ-id="{n1_id}"` sur la liste des composants :

```html
<div class="genome-comp-list" data-organ-id="{organ_id}">
  <!-- composants ici -->
</div>
```

**JS dans la page** :

```javascript
// F3 — Drag-and-drop reorder
document.querySelectorAll('.genome-comp-list').forEach(list => {
  Sortable.create(list, {
    animation: 150,
    onEnd: async () => {
      const organId = list.dataset.organId;
      const order = [...list.querySelectorAll('[data-genome-id]')]
        .map(el => el.dataset.genomeId);
      await fetch(`/api/genome/organ/${organId}/reorder`, {
        method: 'PATCH',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ order })
      });
    }
  });
});
```

---

---

### Structure finale de `render_genome_preview()`

Le `<script>` consolidé (F1 + F2 + F3) doit être injecté **juste avant `</body>`** dans le HTML retourné.

---

---

### Ce qu'il NE FAUT PAS toucher

- `server_9998_v2.py` — les endpoints sont figés, ne pas modifier
- Le routing des onglets de phase (déjà fonctionnel)
- Les CDN Flowbite et Tailwind déjà présents

---

---

### Critères d'acceptation

- [x] Double-clic sur un label → `contenteditable` activé, focus
- [x] Blur → `PATCH /api/genome/node/<id>` déclenché, label mis à jour dans le JSON
- [x] Survol d'un composant → bouton ⚙ visible
- [x] Clic ⚙ → `prompt()` avec hint actuel, choix validé → `PATCH` + `location.reload()`
- [x] Drag-and-drop d'un composant dans son organe → `PATCH /api/genome/organ/<id>/reorder` déclenché
- [x] Refresh → ordre persisté dans la page
- [ ] Cmd+Shift+R → http://localhost:9998/preview

---

## Archives
*(Voir [ROADMAP_ACHIEVED.md](ROADMAP_ACHIEVED.md) pour toutes les missions archivées)*

---

### Mission 14F-BUGS — Post-14C-UX : Bugs persistants + Vision Bottom-Up ✅ LIVRÉ
**DATE : 2026-03-02**
**STATUS : DÉPLOYÉ & VALIDÉ**

#### 1. Rétablissement de la Vision "Bottom-Up" (WYSIWYG Intégral)
- **Suppression du raccourci N0** : La `level === 0` shortcut dans `Canvas.renderer.js` a été supprimée. Les Organes ne sont plus des images statiques de la `WireframeLibrary` mais des assemblages dynamiques et réels de leurs enfants. Un changement au niveau Atome (N3) remonte désormais physiquement jusqu'au Corps (N0).
- **Priorité aux Modifs Utilisateur** : `_buildComposition` privilégie désormais systématiquement le `PrimOverlay` (RAM) et le `svg_payload` (Génome) avant de tenter un rendu via `WireframeLibrary`.

#### 2. Persistance & Mémoire de Forme
- **Persistence Inter-niveaux** : Correction de la logique de calcul des coordonnées dans `_buildComposition`. Les atomes déplacés manuellement conservent leur position relative lors du re-render cascade N3→N0.
- **Write-back Génome** : Intégration de l'écriture directe dans le `svg_payload` du génome lors de la sortie du Mode Illustrateur (`_exitGroupEdit`). Les modifications survivent désormais au rechargement de la page (Cmd+R).

#### 3. Stabilité de l'Édition (Mode Illustrateur)
- **Fix Resize** : Remplacement de `getAttribute` par `getBBox()` dans `_setupPrimitiveResize`. Les poignées et le rectangle cible sont désormais parfaitement synchronisés, peu importe le style CSS appliqué.
- **Debug Rails** : Ajout de logs de capture `PrimOverlay` pour un audit transparent des sessions d'édition.

#### 4. Ergonomie Sidebar (FJD Polish)
- **Nettoyage Sémantique** : Suppression définitive des contrôles HTTP (GET/POST, URL endpoint) dans la sidebar N3. Focus pur sur le Design et la Description UI.
- **Accordion de Contrôle** : Réorganisation et fermeture par défaut de tous les panels de la sidebar droite (Style, Nuance, etc.), sauf le panel **TRANSFORMATION**.

---

---

### Mission 14F-P1-CLAUDE-TEST — Suppression HTTP controls (ComponentsZone) ✅ LIVRÉ

---

### Mission 14F-P2-CLAUDE-TEST — Reorder + Collapse panels sidebar-right ✅ LIVRÉ

---

### Mission 14F-P3-CLAUDE-TEST — Outils d'édition en premier (N2 et N3) ✅ LIVRÉ

---

### Objectif
Déplacer et redimensionner les organes N0 sur le canvas SVG du Stenciler.
Positions/dimensions sauvegardées dans `layout.json` séparé du genome.
Au rechargement, le canvas restaure le layout sauvegardé.

---

### Décision architecture — layout.json séparé
- `genome_reference.json` = sémantique (quoi). Ne pas toucher.
- `layout.json` (nouveau) = positions canvas (où).
  Format : `{ "n1_ir": { "x": 120, "y": 80, "w": 320, "h": 200 }, ... }`
- Fichier : `Frontend/2. GENOME/layout.json`

---

### Endpoints serveur (T1 — Claude, CODE DIRECT)
- `GET /api/layout` → retourne `layout.json` (ou `{}` si absent)
- `POST /api/layout` → body: `{ organ_id: { x, y, w, h } }` → merge dans `layout.json`

---

### Drag des organes N0 (T2 — Canvas.feature.js)
- Au niveau N0 : mousedown sur organe → drag libre SVG
- mouseup → `POST /api/layout` avec nouvelle position
- Chargement N0 → `GET /api/layout` → applique positions via `transform`

---

### Resize des organes N0 (T3 — Canvas.feature.js)
- 4 poignées SVG aux coins de chaque organe N0
- Drag poignée → redimensionne l'organe SVG en live
- mouseup → `POST /api/layout` avec nouvelles dimensions

---

### Fichiers à lire AVANT de coder
1. `static/js/features/Canvas.feature.js` — entier. Focus `_renderCorps()`, drag existant.
2. `static/js/Canvas.renderer.js` — entier. Focus `renderNode()` level===0, `_zoneTemplateToPositions()`.

---

### Contexte
`genome_canvas.html` est le nouveau canvas éditeur genome (remplace le canvas SVG cassé).
État actuel validé FJD :
- Drag libre ✅ (listeners sur document, e.target.closest)
- Tabs N0 ✅
- Resize LARGEUR ✅ (poignée triangle bas-droit `.resize-handle`)
- Focus mode ✅ (clic carte → overlay, autres cartes estompées, détail N2/N3)
- Persistance x/y/w dans `/api/layout` ✅

---

### Fichier cible
`Frontend/3. STENCILER/static/genome_canvas.html`

Lire aussi (API disponible) :
- `Frontend/3. STENCILER/server_9998_v2.py` → comprendre POST /api/layout et PATCH /api/genome/node/<id>

---

### F1 — Resize HAUTEUR (poignée bord bas)

**CSS à ajouter** :
```css
.resize-handle-s {
  position: absolute; bottom: 0; left: 50%; transform: translateX(-50%);
  width: 40px; height: 6px; cursor: s-resize;
  background: #d5d4d0; border-radius: 3px; opacity: 0;
  transition: opacity 0.15s;
}
.organ-container:hover .resize-handle-s { opacity: 1; }
```

**Dans `renderOrgan()`** — ajouter après le `.resize-handle` existant :
```javascript
const rhs = document.createElement('div');
rhs.className = 'resize-handle-s';
organContainer.appendChild(rhs);
```

**Dans `initDragAndDrop()`** :
- Ajouter variables : `let resizedHeightOrgan = null, resizeHStartY, resizeHStartH;`
- Dans mousedown : si `e.target.classList.contains('resize-handle-s')` → init resize hauteur (même pattern que resize largeur)
- Dans mousemove : `resizedHeightOrgan.style.height = Math.max(100, resizeHStartH + dy) + 'px'`
- Dans mouseup : POST /api/layout avec `{ x, y, w, h }` (h = offsetHeight)

**Dans `renderOrgan()`** : restaurer `organ.h` → `organContainer.style.height = organ.h + 'px'`
**Dans `renderPhase()`** : `organ.h = saved ? saved.h : null;`

---

### F2 — Inline rename dans le focus mode

Dans `enterFocus()`, le header de la carte en focus affiche le nom de l'organe.
Rendre ce nom éditable au double-clic :

```javascript
// Dans la génération du HTML du focus (enterFocus)
// Remplacer <span>${organ.name}</span> par :
const nameSpan = document.createElement('span');
nameSpan.textContent = organ.name;
nameSpan.style.cssText = 'cursor:text; padding:2px 4px; border-radius:3px;';
nameSpan.addEventListener('dblclick', () => {
  nameSpan.contentEditable = 'true';
  nameSpan.focus();
  nameSpan.style.background = '#f0f9ff';
  nameSpan.style.outline = '1px solid #93c5fd';
});
nameSpan.addEventListener('blur', async () => {
  nameSpan.contentEditable = 'false';
  nameSpan.style.background = '';
  nameSpan.style.outline = '';
  const newName = nameSpan.textContent.trim();
  if (newName && newName !== organ.name) {
    organ.name = newName;
    await fetch(`/api/genome/node/${organ.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ field: 'name', value: newName })
    }).catch(() => {});
  }
});
```

---

### Critères d'acceptation
- [x] Poignée grise apparaît au survol de chaque carte en bas au centre
- [x] Drag poignée bas → hauteur augmente/diminue (min 100px)
- [x] Reload → hauteur restaurée depuis `/api/layout`
- [x] En mode focus : double-clic nom organe → champ éditable
- [x] Blur → PATCH `/api/genome/node/<id>` avec `{field:'name', value}`
- [x] Drag, resize largeur, tabs → aucune régression
- [ ] FJD valide sur http://localhost:9998/genome_canvas (Cmd+Shift+R obligatoire)

---

## Mission 20D — Genome Canvas : Drill Down & Context Panel [COMPLETED]
**ACTOR: Kimi / Gemini**
**MODE: CODE DIRECT**
**DATE: 02/03/2026**
**STATUS: COMPLETED**

---

### Objectif
Apporter la capacité d'inspecter et modifier la charte granulaire des Organes N1 directement depuis l'interface macroscopique (`genome_canvas.html`), sans utiliser le canvas SVG lourd.

---

### F1 — Panneau de Style par Organe (Side Panel)
- **Déclencheur**: Clic simple sur la carte d'un Organe N1 (sélection).
- **Action**: Ouvre un panneau latéral droit (Sidebar HTML) affichant les propriétés de l'organe sélectionné.
- **Fonctionnalités du panneau**:
  - Sélecteur de couleur (Theme CSS) basé sur la palette `UI_UX_PRO_MAX_INTELLIGENCE`.
  - Contrôle de visibilité/affichage.
- **Data Hook**: La sélection envoie un `PATCH /api/genome/node/<id>` pour mettre à jour la propriété `style` ou `theme` du nœud.
- **Réactivité**: La couleur de fond de l'organe change instantanément en local pour le feedback visuel.

---

### F2 — Drill Down (Mode Zoom / N2+N3)
- **Déclencheur**: Double-clic n'importe où sur l'organe (sauf sur le titre qui est déjà géré pour le renommage).
- **Action**: L'organe "s'ouvre" en plein écran / focus modal (position fixed, z-index élevé) avec une transition fluide.
- **Vue Intérieure**:
  - Affiche les colonnes de N2 (Feature Areas).
  - Affiche la liste des N3 (Atomes) à l'intérieur.
- **Édition Bottom-Up**: 
  - Possibilité de cliquer sur un N3 pour accéder à ses propriétés dans la sidebar.
  - La modification d'un N3 entraîne une réécriture dans `_genome` en RAM, et le parent N1 se met à jour visuellement via un re-render complet et instantané ciblé (Single Source of Truth paradigm).
- **Sortie**: Bouton "Fermer" ou clic sur l'arrière-plan semi-transparent pour restaurer la vue globale N0.

---

### F3 — Propagation Top-Down
- Mettre à jour la fonction `_comp_html` pour qu'elle accepte le thème de son parent N1.
- Au lieu de hardcoder des classes Tailwind pour la couleur (`bg-blue-600`), injecter dynamiquement la couleur héritée du parent (ex: `bg-emerald-600`).
- Si la couleur de N1 change (via F1), tous les atomes N3 à l'intérieur se mettent à jour visuellement.

---

### Contexte

Le genome AetherFlow produit des identifiants ésotériques (`n1_validation`, `n1_layout`) illisibles par un humain ou un outil design (Figma, Illustrator). Le `visual_hint` existe sur les composants N3 mais rien ne remonte au niveau N1.

Ce pass enrichit chaque organe N1 avec :
- `ui_role` : type d'écran UI (`form-panel`, `nav-header`, `dashboard`, `chat-overlay`, etc.)
- `dominant_zone` : zone de placement principal (`header`, `sidebar`, `main`, `footer`, `floating`)
- `display_label` : label lisible humain (`"Form / Validation Flow"`) qui remplace l'ID ésotérique

---

### Fichiers à lire AVANT de coder (OBLIGATOIRE)

1. `Backend/Prod/exporters/genome_to_svg_v2.py` — lire `ZONE_MAPPINGS` (L.62-87) et `_classify_component()` (L.105-119). La logique de classification N3 est déjà là, on la remonte au niveau N1.
2. `Frontend/2. GENOME/genome_reference.json` — structure réelle : `n0_phases` → `n1_sections` → `n2_features` → `n3_components[].visual_hint`
3. `Backend/Prod/exporters/genome_to_svg_v2.py` — `_render_organ_zones()` (L.371-449) : voir comment le label N1 est affiché (L.399). C'est ce label qu'on veut enrichir.

---

### Fichiers à créer / modifier

**CRÉER** : `Backend/Prod/enrichers/__init__.py` (vide)

**CRÉER** : `Backend/Prod/enrichers/genome_enricher.py`

```
Logique :
1. Charger genome_reference.json
2. Pour chaque N1 organ :
   a. Collecter tous les visual_hint N3 (à plat, tous features confondus)
   b. Classifier chaque hint dans une zone (réutiliser ZONE_MAPPINGS de genome_to_svg_v2.py)
   c. Compter la distribution par zone
   d. Dominant zone = zone avec le plus de composants
   e. Mapper dominant_zone → ui_role selon UI_ROLE_MAP (voir ci-dessous)
   f. Générer display_label = f"{UI_ROLE_MAP[ui_role]['label']} / {organ['name']}"
3. Ajouter au JSON de chaque N1 : { "ui_role": "...", "dominant_zone": "...", "display_label": "..." }
4. Écrire genome_enriched.json dans le même dossier que genome_reference.json
5. CLI : python genome_enricher.py [--genome <path>] [--output <path>] [--dry-run]
   --dry-run : affiche le résultat sans écrire le fichier
```

**Taxonomie UI_ROLE_MAP** (à inclure dans le code) :
```python
UI_ROLE_MAP = {
    'header':   {'ui_role': 'nav-header',      'label': 'Navigation'},
    'sidebar':  {'ui_role': 'left-sidebar',    'label': 'Panel'},
    'main':     {'ui_role': 'main-content',    'label': 'Workspace'},
    'footer':   {'ui_role': 'status-bar',      'label': 'Actions'},
    'floating': {'ui_role': 'overlay',         'label': 'Overlay'},
}
# Affinage par hint dominant si besoin :
HINT_ROLE_OVERRIDES = {
    'form':        'form-panel',
    'input':       'form-panel',
    'upload':      'upload-zone',
    'editor':      'main-canvas',
    'canvas':      'main-canvas',
    'dashboard':   'dashboard',
    'chart':       'dashboard',
    'chat':        'chat-overlay',
    'modal':       'overlay',
    'settings':    'settings-panel',
    'stepper':     'onboarding-flow',
}
```

**MODIFIER** : `Backend/Prod/exporters/genome_to_svg_v2.py`

Dans `_render_organ_zones()` (L.399), utiliser `display_label` si disponible :
```python
# Avant :
lines.append(_text(x + 12, y + 18, f'{gid} / {name}', ...))
# Après :
label = organ.get('display_label') or f'{gid} / {name}'
role  = organ.get('ui_role', '')
lines.append(_text(x + 12, y + 18, label, ...))
if role:
    lines.append(_text(x + 12, y + 30, f'[{role}]', size=8, fill=COL_TEXT_SUB))
```

**MODIFIER** : `sullivan` (shell script)

Ajouter commande `enrich` avant `zones` :
```bash
enrich)
    $VENV_PYTHON "$SCRIPT_DIR/Backend/Prod/enrichers/genome_enricher.py" \
        --genome "$GENOME_DEFAULT" \
        --output "$SCRIPT_DIR/Frontend/2. GENOME/genome_enriched.json"
    ;;
```

Et dans `build_zones()`, ajouter optionnellement `--genome genome_enriched.json` si le fichier existe.

---

### Critères d'acceptation

- [x] `python genome_enricher.py --dry-run` → affiche pour chaque N1 : `id | ui_role | dominant_zone | display_label`
- [x] `genome_enriched.json` écrit avec les 3 champs ajoutés sur chaque N1 (pas de suppression de champs existants)
- [x] `./sullivan zones` avec genome enrichi → le header SVG de chaque organe affiche `display_label` + `[ui_role]`
- [x] Aucun organe ne reste avec le label par défaut `n1_xxx / undefined`
- [x] FJD valide sur le SVG généré

---

### Ce qui a été fait
- Créé `Backend/Prod/exporters/topology_bank.py` — 20 topologies nommées (bento_grid, split_editorial, masonry, etc.) avec col_span, row_span, densité
- Créé `Backend/Prod/exporters/archetype_renderers.py` — renderers SVG par archétype (nav_header, dashboard, form_panel, chat_overlay, etc.)
- Passes 2+3 dans `genome_enricher.py` : ux_step (tri par séquence UX) + col_span/layout_type (densité N3)
- Renderer `genome_to_svg_v2.py` branché sur `render_organ()` / `_render_n1()`

---

### Résultat visuel
FJD : résultat "gris, des boîtes nulles alignées" — visuellement médiocre. Archétypes Python trop basiques. Le renderer statique ne peut pas concurrencer un LLM pour le design.

---

### Ce qui a été fait

**Prop 3A — ApplyEngine off-thread (`asyncio.to_thread`)**
- `orchestrator.py` : `self.apply_engine.apply(...)` → `await asyncio.to_thread(self.apply_engine.apply, ...)`
- 1 ligne modifiée. Débloque l'event loop pendant les opérations AST/fichiers (sync).

**Prop 2B — Séparation contexte statique/dynamique**
- Extrait `SURGICAL_MODE_INSTRUCTIONS` (~36L) + instructions refactoring/code_gen/patch hors de `step_context` (prompt user)
- Ajouté param `system_context: Optional[str] = None` dans la chaîne : `_execute_step()` → `execute_step()` → `_execute_with_fallback()` / `_execute_simple()`
- `gemini_client.generate()` : `system_prompt` → `request_data["systemInstruction"]` (séparé des `contents`, caching Gemini)
- `deepseek_client.generate()` : `system_prompt` → `{"role": "system", "content": ...}` (prefix caching DeepSeek)
- Les instructions statiques ne boustent plus le prompt dynamique → cache hit > 90% attendu sur instructions fixes

**Fichiers modifiés :**
- `Backend/Prod/orchestrator.py`
- `Backend/Prod/models/agent_router.py`
- `Backend/Prod/models/gemini_client.py`
- `Backend/Prod/models/deepseek_client.py`

---

### Validation
- AST check ✅ sur les 4 fichiers
- Test AetherFlow : 1/1 steps ✅, pipeline sans erreur (129s, $0.01)
- Prop 2B active uniquement sur steps surgical/refactoring/code_gen/patch (pas analysis → system_context=None normal)

---

### Réalisations
- **Tâche A** : Plugin Figma `code.js` + `ui.html` — export SVG chunked (fix RangeError 65534), bouton "Analyser SVG", POST vers `/api/retro-genome/upload-svg`.
- **Tâche B** : `svg_parser.py` — extraction fonts (attributs + style inline), couleurs, régions `<g>`, éléments `<text>`/`<rect>`, `google_fonts_import`, `accent_color`.
- **Tâche C** : Endpoint `/api/retro-genome/upload-svg` dans `server_9998_v2.py` (handler direct, pas FastAPI). SVG sauvegardé dans `exports/retro_genome/SVG_<name>_<ts>.svg`.
- **Tâche D** : `_normalize_for_detector()` adapter Vision (`components[]`) → ArchetypeDetector (`elements[]`). PNG `/upload` inclut maintenant `archetype` dans la réponse.

---

### Bugs corrigés
- RangeError 65534 (Figma sandbox V8) : conversion chunked `svgBytes.subarray(i, i+8192)`
- 404 sur `/api/retro-genome/upload-svg` : route ajoutée à `server_9998_v2.py` (pas à `routes.py` FastAPI)
- Schema mismatch archetype_detector : `_normalize_for_detector()` bridge
- Couleurs inline style manquées : regex `fill:/stroke:` dans style string
- Fonts depuis attribut direct manquées : fallback `node.get('font-family')`
- `msg.error` non vérifié dans `ui.html` : guard ajouté

---

### Pendant
- **Amendment 41-A** (provenance SVG) → Mission 41-A active

---

---

## Mission 55 — BRS : Mode MULTIPLEX (3 chatbots indépendants)
**STATUS: ✅ LIVRÉ — 2026-03-18**
**ACTOR: CLAUDE (backend) + GEMINI (frontend)**
- [x] Route `POST /api/brs/chat/{provider}` — chat individuel persistant par colonne
- [x] `sse_chat_generator()` dans `brainstorm_logic.py` — historique par (session_id, provider)
- [x] UI : 3 inputs indépendants, historique visible, mode MULTIPLEX par défaut
- [x] Sous-header `[MULTIPLEX]` `[COUNCIL]`

---

## Mission 56 — FRD Editor : Mode CONSEIL (Audit UX + Panel collapsible)
**STATUS: ✅ LIVRÉ — 2026-03-18**
**ACTOR: CLAUDE (backend) + GEMINI (frontend)**
- [x] Bouton `[CONSEIL]` dans le toggle mode
- [x] `_build_conseil_prompt()` dans `server_9998_v2.py` — injection CSV ui-ux-pro-max
- [x] Panel `<details id="ux-audit-panel">` sticky Sullivan pane
- [x] `triggerSilentAudit()` auto au loadFile + saveFile
- [x] `updateAuditPanel()` — parse 🔴🟡🟢 + compteurs

---

## Mission 57 — FRD Editor : Mode WIRE frontend (toggle + panel)
**STATUS: ✅ LIVRÉ (frontend) — 2026-03-18 | Backend route 🔴 → M62 bis**
**ACTOR: GEMINI (frontend)**
- [x] Bouton `[WIRE]` dans le toggle mode
- [x] Panel `#wire-panel` avec bouton Analyser
- [x] `runWire()` → `POST /api/frd/wire` (route backend manquante → voir M62 bis)
- [x] `/wire` commande chat → `setMode('wire') + runWire()`
- [ ] Backend `POST /api/frd/wire` → non implémenté

---

## Mission 58 — BRS : Mode COUNCIL complet
**STATUS: ✅ LIVRÉ — 2026-03-18**
**ACTOR: CLAUDE**
- [x] `rank_council()` dans `brainstorm_logic.py` — tableau arbitrage Gemini
- [x] `POST /api/brs/rank` + `GET /api/brs/arbitrate/{session_id}` dans `brainstorm_routes.py`
- [x] `_councilDone` tracker + auto-synthèse Sullivan
- [x] Boutons `Synthétiser maintenant`, `Relancer →`, `Arbitrer`

---

## Mission 59 — BRS : Rendu markdown Sullivan pane
**STATUS: ✅ LIVRÉ — 2026-03-18**
**ACTOR: CLAUDE + GEMINI**
- [x] CDN `marked.min.js` dans `<head>` de `brainstorm_war_room_tw.html`
- [x] `triggerSullivanSynthesis()` → `marked.parse()` au `done`
- [x] `arbitrate()` → `marked.parse(data.ranking)`
- [x] `applyMarkdownStyles(el)` — styles Tailwind table/code/pre/p

---

## Mission 60 — BRS : Externalisation JS (JS Lock)
**STATUS: ✅ LIVRÉ — 2026-03-18**
**ACTOR: CLAUDE**
- [x] Script inline supprimé de `brainstorm_war_room_tw.html` (304 lignes)
- [x] `static/js/brainstorm_war_room.js` — JS complet, protégé de Gemini
- [x] Header `⚠️ CE FICHIER EST GÉRÉ PAR CLAUDE UNIQUEMENT`

---

## Mission 61 — BRS : Rendu markdown colonnes modèles
**STATUS: ✅ LIVRÉ — 2026-03-18**
**ACTOR: GEMINI**
- [x] `startStreaming()` — accumulation tokens + `marked.parse()` au `done`
- [x] `sendToProvider()` — `accumulatedCard` + `marked.parse()` au `done`
- [x] `addCaptureButton()` après rendu markdown dans les deux flows

---

## Mission 43-C1/C2 — War Room SVG Design Spec + Refonte UI
**STATUS: ✅ SUPERSÉDÉ — 2026-03-18**
- Tâches C1 (extraction SVG spec) et C2 (refonte HTML) obsolètes.
- La War Room a été intégralement reconstruite en Tailwind (`brainstorm_war_room_tw.html`) via M44/M48/M55-61.
- Tâche D (validation FJD end-to-end) → intégrée dans les critères des missions BRS successives.


---

## Mission 62 — Infrastructure : Injection API_CONTRACT dans les prompts agents
**STATUS: ✅ LIVRÉ — 2026-03-18**
**ACTOR: CLAUDE (backend)**
- [x] `_load_api_contract()` dans `server_9998_v2.py` — lit `API_CONTRACT.md` depuis disque
- [x] Mode CONSTRUCT : contrat injecté dans le system prompt Sullivan (L834)
- [x] Mode CONSEIL : contrat injecté dans `_build_conseil_prompt()` (L154)
- [x] Sullivan ne peut plus suggérer de routes inventées


---

## Mission 66-FIX — FRD Editor : Correction Mode Inspect
**STATUS: ✅ LIVRÉ — 2026-03-23**
**ACTOR: CLAUDE (hotfix direct)**
**FICHIER:** `Frontend/3. STENCILER/static/templates/frd_editor.html`

---

### Problème initial
Le bouton Inspect (Mission 66) était silencieux : aucun outline dans l'iframe, aucun highlight Monaco. Aucune erreur visible côté utilisateur, mais la console srcdoc révélait :
```
about:srcdoc:184 Uncaught SyntaxError: Unexpected token '<'
```

---

### Diagnostic root cause
**Bug principal (bloquant)** : Injection via template literal + `srcdoc`.
Les scripts étaient injectés en manipulant la string HTML (`</body>` replace) avec des template literals contenant `<\/script>`. En JS, `<\/script>` évalue à `</script>`. Le HTML parser du srcdoc voyait alors deux blocs `<script>...</script>` successifs — mais le premier bloc n'était PAS fermé correctement car le parser HTML du **document parent** (`frd_editor.html`) avait une lecture ambiguë de la séquence. Résultat : les deux blocs de script étaient fusionnés en un seul raw text element. Le V8 engine recevait le contenu des deux blocs comme JavaScript continu, tombait sur `</script>` à la ligne 184, et levait `SyntaxError: Unexpected token '<'`. **Aucun listener n'était enregistré dans l'iframe.**

**Bugs secondaires (UX)** une fois le bug principal résolu :
- `mouseover` trop agressif (bubbling → Monaco scroll en continu)
- `mouseout` efface l'outline trop tôt (parent/child transitions)
- `el.className` → `SVGAnimatedString` sur éléments SVG → crash silencieux
- Race condition sur les décorations Monaco : `setTimeout` cleanup écrasait la décoration suivante

---

### Mesures appliquées

**Fix 1 — Architecture inject (root cause)**
Abandon de l'injection via string HTML. Les scripts sont désormais injectés **via DOM** après le `load` event de l'iframe :
```js
document.getElementById('preview-iframe').addEventListener('load', _injectPreviewScripts);

function _injectPreviewScripts() {
    const doc = iframe.contentDocument;
    const s1 = doc.createElement('script');
    s1.textContent = [...].join('\n');
    doc.body.appendChild(s1);
    if (inspectActive) { /* s2 inspect script */ }
}
```
Avantages : zéro `</script>` dans les template literals, scripts injectés après exécution complète du template, same-origin garanti (srcdoc), try/catch protège le preview.

**Fix 2 — Marker de reload**
`updatePreview()` ajoute un commentaire HTML invisible `<!-- __FRD:true/false -->` pour forcer un vrai reload du srcdoc quand `inspectActive` change (sans modifier Monaco).

**Fix 3 — Tracker `__lastInspected`**
Remplace le `mouseover` agressif + `mouseout` global par un tracker d'élément courant : outline uniquement sur l'élément réellement pointé, `mouseleave` sur document pour cleanup propre.

**Fix 4 — `getAttribute('class')`**
Remplace `el.className` (crash sur SVG) par `el.getAttribute('class') || ''`.

**Fix 5 — Debounce inspect-hover (80ms)**
Le `postMessage` `inspect-hover` est debouncé côté parent : Monaco ne scrolle qu'une fois que la souris se stabilise.

**Fix 6 — Race condition décorations Monaco**
`clearTimeout(_inspectDecTimer)` avant chaque nouvelle décoration : le cleanup ne tue plus la décoration suivante.

---

### Points d'attention résiduels
- Le marker `<!-- __FRD:... -->` est injecté dans le srcdoc mais **pas** dans Monaco (ne pollue pas les fichiers sauvegardés). ✅
- `iframe.contentDocument` est toujours same-origin avec `srcdoc`. ✅
- Si `brainstorm_war_room.js` modifie le DOM de façon async **après** le `load` event, les outlines inspect peuvent apparaître sur des éléments re-rendus. Acceptable pour un outil interne.
- Le search `_highlightInMonaco` par `id=` / première classe Tailwind / tag reste approximatif pour les éléments sans ID. Amélioration possible (Mission future) : search par position XPath ou line hint envoyé depuis l'iframe.

---

## Mission 67 — FRD Editor : Drag & Drop HTML direct dans Monaco

**STATUS: ✅ LIVRÉ — 2026-03-23**
**ACTOR: GEMINI**

---

### Réalisations
- [x] `#drop-overlay` sur `#preview-pane` — overlay vert dashed au dragenter, masqué au drop
- [x] `iframe.style.pointerEvents = 'none'` pendant le drag (essentiel pour recevoir le drop sur l'iframe)
- [x] Bouton `Open` + `<input type="file" accept=".html">` masqué dans le header
- [x] `FileReader.readAsText()` → `editorHTML.setValue()` → `updatePreview()` (drop + Open)
- [x] `#current-file` span dans le header — affiche le nom du fichier chargé
- [x] Style cohérent avec le header (border figma-sep, text-[10px] uppercase tracking-widest)

---

### Note M82 : `gemini-3.1-flash` (code-simple) → corrigé dans M82 (voir ci-dessous)

---

### Mission 266 — Prompt maître Stitch : design brief court depuis DESIGN.md projet
**STATUS: 🟠 PRÊTE — après M265 | DATE: 2026-04-10 | ACTOR: QWEN**

**Contexte :** Le prompt maître envoyé à Stitch ne doit pas décrire l'écran existant (Stitch ne reconstruit pas — il interprète). Il doit être un **design brief court** : intention UX + style + contraintes fortes. L'élève arrive avec un point de départ cohérent, pas une spécification à reproduire.

**Format cible du prompt maître (< 200 tokens) :**
```
Projet : [titre du sujet DNMADE]
Écran : [nom de l'écran — ex: "page d'accueil"]
Objectif : [1 phrase — ce que l'utilisateur fait sur cet écran]
Style : [3 mots depuis DESIGN.md — ex: "minimaliste, tons neutres, typographie claire"]
Couleurs : [primary + neutral + text depuis DESIGN.md]
Contraintes : [2-3 règles fortes — ex: "pas de sidebar, hero pleine largeur, CTA unique"]
```

**Sources à agréger pour construire ce brief :**
1. `projects/{project_id}/DESIGN.md` → style + couleurs
2. `classes/{class_id}/subjects/` → titre du sujet + objectif pédagogique
3. `projects/{project_id}/manifest.json` → nom de l'écran actif

**Backend — créer `stitch_prompt_builder.py` dans `Frontend/3. STENCILER/core/` :**
```python
def build_stitch_brief(project_id: str, screen_name: str, class_id: str = None) -> str:
    """Construit un design brief court pour Stitch depuis les sources projet."""
    # 1. Lire DESIGN.md projet
    # 2. Lire sujet DNMADE si class_id
    # 3. Extraire : titre, style (3 mots), couleurs, contraintes
    # 4. Retourner le brief formaté < 200 tokens
```

**Brancher dans `stitch_router.py`** — endpoint existant `GET /api/stitch/open/{id}` :
- Appeler `build_stitch_brief()` pour construire le prompt
- L'inclure dans la réponse JSON : `{ url: ..., prompt: brief, copy_ready: True }`

**Selon résultat M265 :**
- Si injection URL possible → encoder le brief dans l'URL Stitch
- Si impossible → retourner le brief dans la réponse pour affichage panneau copier-coller côté frontend

**Règle :** ne pas injecter le contenu pédagogique complet (référentiel, compétences) dans le brief Stitch — ça reste dans HoméOS. Le brief est une amorce créative, pas un cahier des charges.

**Fichiers à lire :**
- `Frontend/3. STENCILER/core/stitch_prompt_builder.py` (existe déjà — lire avant de toucher)
- `Frontend/3. STENCILER/routers/stitch_router.py`
- `Backend/Prod/retro_genome/project_context.py` — pour réutiliser la logique de chargement DESIGN.md

---

---

### Mission 264 — dist.zip compilé : snapshot DOM via Playwright → HTML éditable
**STATUS: 🟠 PRÊTE | DATE: 2026-04-08 | ACTOR: QWEN**

**Contexte :** Un dist.zip React sans sources TSX est actuellement extrait tel quel et servi dans l'iframe — non éditable par Sullivan. Playwright est installé (`python3 -c "import playwright"` → ok). L'objectif : charger le bundle headless, attendre le render React, snapshotter le DOM statique, convertir en Tailwind HTML via LLM → résultat éditable.

**Fichiers à lire :**
- `Backend/Prod/retro_genome/routes.py` — bloc `dist_html` (cas dist/index.html dans le ZIP, L706-739)
- `Backend/Prod/retro_genome/react_to_tailwind.py` — `convert()` existant (source TSX → Tailwind)

**Ce qu'il faut créer :**
Ajouter une méthode `snapshot_and_convert(dist_dir: Path, entry_name: str) -> str` dans `react_to_tailwind.py` :

```python
async def snapshot_and_convert(self, dist_dir: Path, entry_name: str) -> str:
    """
    Charge le dist React dans Playwright, snapshotte le DOM après render,
    nettoie le HTML (supprime scripts/styles inline lourds),
    convertit en Tailwind via LLM.
    """
    from playwright.async_api import async_playwright

    index_html = dist_dir / "index.html"
    if not index_html.exists():
        raise FileNotFoundError(f"index.html absent dans {dist_dir}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # Charger en file:// — pas besoin de serveur
        await page.goto(f"file://{index_html.resolve()}", wait_until="networkidle", timeout=15000)
        # Attendre que React ait rendu (div#root non vide)
        await page.wait_for_selector("#root > *", timeout=10000)
        dom_html = await page.content()
        await browser.close()

    # Nettoyer le HTML snapshot (supprimer scripts, styles inline lourds)
    import re
    dom_html = re.sub(r'<script[\s\S]*?</script>', '', dom_html, flags=re.IGNORECASE)
    dom_html = re.sub(r'<style[^>]*>[\s\S]{2000,}?</style>', '', dom_html, flags=re.IGNORECASE)
    dom_html = dom_html[:40000]  # cap contexte LLM

    # Convertir le DOM statique en Tailwind HTML via LLM
    prompt = f"""Tu es un Expert Intégrateur Frontend.
MISSION : Ce HTML est un snapshot DOM d'une app React compilée.
Convertis-le en HTML5 sémantique + Tailwind CSS autonome et éditable.
Préserve fidèlement la structure, les textes, les couleurs visibles.
Supprime toute dépendance React (data-reactroot, __reactFiber, etc.).
Résultat : document HTML5 complet autonome (<!DOCTYPE html>).
Réponds UNIQUEMENT avec le code HTML. Pas de prose.

NOM : {entry_name}

DOM SNAPSHOT :
{dom_html}
"""
    from Backend.Prod.models.gemini_client import GeminiClient
    client = GeminiClient(execution_mode="BUILD")
    result = await client.generate(prompt, max_tokens=16000, temperature=0.1)
    if not result.success:
        raise RuntimeError(f"LLM conversion failed: {result.error}")
    code = result.code
    if "```html" in code:
        code = code.split("```html")[1].split("```")[0]
    elif "```" in code:
        code = code.split("```")[1].split("```")[0]
    return code.strip()
```

**Brancher dans `routes.py` — remplacer le court-circuit dist :**

Actuellement (L706-739), quand `dist/index.html` est détecté, le code extrait le dist et retourne `origin: compiled`. Remplacer par :

```python
if dist_html:
    safe_base = entry["name"].lower().replace(" ", "_").split(".")[0]
    dist_dir = stenciler_templates / f"zip_dist_{safe_base}"
    dist_dir.mkdir(parents=True, exist_ok=True)
    # Extraire le dist
    dist_prefix = dist_html.replace('index.html', '')
    for member in file_list:
        if member.startswith(dist_prefix) and not member.startswith('__MACOSX') and not member.endswith('/'):
            rel = member[len(dist_prefix):]
            dest = dist_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(z.read(member))
    # Snapshot + conversion Tailwind
    try:
        html_code = await get_react_converter().snapshot_and_convert(dist_dir, entry["name"])
        origin = "generated"
    except Exception as e:
        logger.warning(f"[ZIP/Playwright] Snapshot failed ({e}), fallback dist_url")
        # Fallback : servir le dist compilé si Playwright échoue
        dist_url = f"/static/templates/zip_dist_{safe_base}/index.html"
        wrapper_name = f"zip_dist_{safe_base}/index.html"
        idx = json.loads(index_path.read_text(encoding='utf-8'))
        for e2 in idx.get('imports', []):
            if e2['id'] == req.import_id:
                e2['html_template'] = wrapper_name
                e2['dist_url'] = dist_url
                e2['elements_count'] = 0
                e2['origin'] = "compiled"
                break
        index_path.write_text(json.dumps(idx, indent=2, ensure_ascii=False), encoding='utf-8')
        _SVG_JOBS[job_id] = {"status": "done", "template_name": wrapper_name, "dist_url": dist_url, "error": None}
        return
    # Suite normale : sauvegarder le HTML généré dans templates
    # (le flux rejoint le chemin commun après le bloc ZIP)
    template_name = f"reality_{safe_base}.html"
    (stenciler_templates / template_name).write_text(html_code, encoding='utf-8')
    idx = json.loads(index_path.read_text(encoding='utf-8'))
    for e2 in idx.get('imports', []):
        if e2['id'] == req.import_id:
            e2['html_template'] = template_name
            e2['elements_count'] = 0
            e2['origin'] = "generated"
            break
    index_path.write_text(json.dumps(idx, indent=2, ensure_ascii=False), encoding='utf-8')
    _SVG_JOBS[job_id] = {"status": "done", "template_name": template_name, "error": None}
    logger.info(f"[ZIP/Playwright] snapshot → {template_name}")
    return
```

**Points d'attention :**
- `wait_for_selector("#root > *")` — si le div racine React s'appelle autrement (`#app`, `#main`), Playwright timeout. Ajouter un fallback : `await page.wait_for_load_state("networkidle")` suffit si selector échoue.
- Playwright headless en `file://` ne charge pas les assets réseau — c'est OK, on veut le DOM structurel, pas les images.
- Si Playwright échoue (env sans Chromium, timeout) : fallback propre vers `dist_url` compilé (déjà géré dans le code ci-dessus).

**Livrable :**
- dist.zip forgé → HTML Tailwind éditable (plus d'iframe compilé)
- Fallback silencieux vers dist compilé si Playwright échoue
- Aucune régression sur les ZIP avec sources TSX (M119 inchangé)

---

**Hypothèse 2 — `ws-preview-overlay` absent du DOM**
Probabilité : PROBABLE

`enterPreviewMode()` fait `document.getElementById('ws-preview-overlay')`. Si l'élément est absent (supprimé par une régression Gemini), la fonction retourne silencieusement à la ligne `if (!shell || !overlay) return`.

Test :
```js
document.getElementById('ws-preview-overlay')          // null ?
document.getElementById('ws-preview-frame-container')  // null ?
```

---

**Comportement 2 — Moteur hover injecté (postMessage)**

**Architecture :**
- `WsCanvas.js` expose `injectHoverEngine(iframe)` — injecte un script dans `iframe.contentDocument` après chargement
- Le script injecté gère `mouseover` / `mouseout` / `click` → remonte via `window.parent.postMessage`
- `WsCanvas.js` écoute `window.addEventListener('message', ...)` → met à jour `this._selectedIframeEl`
- `pointer-events` de l'iframe : `none` par défaut, `auto` quand `activeMode === 'select'`

**Dans `WsScreenShell.js`**, modifier le listener `load` de l'iframe :
```js
iframe.addEventListener('load', () => {
    if (window.wsFontManager) window.wsFontManager.injectStyles();
    if (window.wsCanvas) window.wsCanvas.injectHoverEngine(iframe);
});
```

**Dans `WsCanvas.js`**, ajouter la méthode `injectHoverEngine(iframe)` :
```js
injectHoverEngine(iframe) {
    try {
        const doc = iframe.contentDocument;
        if (!doc || doc.__hmInjected) return;
        doc.__hmInjected = true;

        const script = doc.createElement('script');
        script.textContent = `
(function() {
    let _last = null;
    function _clear() {
        if (_last) {
            _last.style.removeProperty('outline');
            _last.style.removeProperty('outline-offset');
            _last = null;
        }
    }
    document.addEventListener('mouseover', function(e) {
        const el = e.target;
        if (el === document.body || el === document.documentElement) return;
        _clear();
        el.style.outline = '2px solid #8cc63f';
        el.style.outlineOffset = '-1px';
        _last = el;
        window.parent.postMessage({ type: 'hm-hover', tag: el.tagName, id: el.id || '', cls: (el.className || '').toString().slice(0, 80) }, '*');
    });
    document.addEventListener('mouseout', function(e) {
        if (!e.relatedTarget || e.relatedTarget === document.documentElement) {
            _clear();
            window.parent.postMessage({ type: 'hm-clear' }, '*');
        }
    });
    document.addEventListener('click', function(e) {
        const el = e.target;
        window.parent.postMessage({ type: 'hm-select', tag: el.tagName, id: el.id || '', cls: (el.className || '').toString().slice(0, 80), text: (el.textContent || '').trim().slice(0, 100) }, '*');
    });
})();`;
        doc.head.appendChild(script);
    } catch(_) {}
}
```

**Dans `WsCanvas.js` — `setMode(mode)`**, ajouter la gestion des pointer-events sur toutes les iframes des shells :
```js
setMode(mode) {
    this.activeMode = mode;
    // Activer pointer-events dans les iframes en mode select uniquement
    const isSelect = mode === 'select';
    document.querySelectorAll('.ws-screen-shell iframe').forEach(iframe => {
        iframe.style.pointerEvents = isSelect ? 'auto' : 'none';
    });
    // ... reste du setMode existant
}
```

**Dans `WsCanvas.js` — `init()`**, ajouter le listener message :
```js
window.addEventListener('message', (e) => {
    if (e.data?.type === 'hm-select') {
        this._selectedIframeEl = e.data;
        console.log('[HM-SELECT]', e.data.tag, e.data.id, e.data.text);
        // Sullivan context à brancher ici (mission suivante)
    }
});
```

**Points d'attention :**
- `doc.__hmInjected` guard : évite la double injection si l'iframe reload
- Ne pas injecter si `doc.head` n'existe pas encore (iframe vide ou error page)
- En mode `drag` ou tout autre mode ≠ `select`, les iframes ont `pointer-events: none` → le canvas gère tout sans interférence
- `addScreen()` appelle `WsScreenShell.build()` qui crée l'iframe — l'injection se fait au `load` event, donc après que le contenu soit rendu

**Fichiers :** `WsCanvas.js` + `WsScreenShell.js`

**Livrable :**
- Header shell = curseur `move` + gripper `⋯` centré
- Mode select → iframes activées + moteur hover injecté au load
- Hover = outline vert `#8cc63f` sur l'élément HTML sous la souris, géré entièrement dans l'iframe
- Click = `[HM-SELECT]` dans la console avec tag/id/text
- Tous autres modes → pointer-events none, comportement canvas inchangé

---|
| Flèche `select` | Garder tel quel |
| Main `drag` | Garder — mais remplacer le picto SVG illisible par une main simple (3 tracés max), tooltip `"naviguer (H)"` |
| Couleurs `colors` | **Masquer** (`hidden`) — viendra dans une mission Design System dédiée |
| Typographie `text` | Garder |
| Stitch `stitch` | **Supprimer** (intégré dans M234 — panneau Stitch supprimé) |
| Réinitialiser vue | Garder — corriger le titre en `"recentrer (0)"` |
| Reset layout panels | **Déplacer** hors de la toolbar → voir ci-dessous |

**Fix 1 — Nouveau picto main (drag)**
Remplacer le SVG `path` complexe actuel par un SVG main simple :
```html
<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 11V6a2 2 0 014 0v5m0 0V6a2 2 0 014 0v5m0 0a2 2 0 014 0v3a6 6 0 01-6 6H9a6 6 0 01-6-6v-3"/>
</svg>
```

**Fix 2 — Masquer couleurs**
Ajouter `hidden` au bouton `data-mode="colors"`.

**Fix 3 — Supprimer le bouton Stitch de la toolbar**
Supprimer le `<button data-mode="stitch" ...>` (le lien Stitch est désormais dans le dashboard projet).

**Fix 4 — Déplacer "réinitialiser layout des panneaux" vers le header workspace**
- Supprimer le bouton `onclick="window.PanelDragger?.resetAll()"` de la toolbar
- L'ajouter dans le header du workspace (zone title "Workspace Canvas"), comme un bouton discret à côté du label :
  ```html
  <button onclick="window.PanelDragger?.resetAll()" 
          title="réinitialiser layout des panneaux"
          class="p-1 text-slate-300 hover:text-slate-500 transition-colors">
    <svg class="w-3 h-3" ...><!-- icône reset --></svg>
  </button>
  ```
- Trouver le bon endroit dans le header (chercher `data-purpose` ou le label "Workspace Canvas" ou "canvas")

**Fix 5 — Ajouter bouton image avec popover assets**
Nouveau bouton dans la toolbar, entre typo et le séparateur zoom :
- Picto : icône image (montagne + soleil) standard
- Au clic : ouvre un popover flottant `#ws-image-picker` positionné à gauche de la toolbar
- Le popover liste les fichiers de `assets/img/` du projet actif via `GET /api/projects/active/assets`
- Chaque fichier affiche : thumbnail + nom + bouton "copier lien" (`/api/projects/assets/img/{filename}`)
- Un bouton "importer" dans le popover déclenche `document.getElementById('ws-direct-upload').click()` (l'input existant filtre déjà `.png,.jpg,.jpeg`)

**Note :** Les routes assets sont implémentées dans M236 (QWEN). M235 peut être livrée avec la liste vide (`{ files: [] }`) si M236 n'est pas encore joué — le popover fonctionnera à vide.

**Livrable :**
- Toolbar épurée : flèche / main (picto correct) / typo / image / séparateur / recentrer
- Couleurs + Stitch absents
- "Réinitialiser layout panels" déplacé vers le header
- Popover image basique fonctionnel (même vide)---

**input_files :**
- `Backend/Prod/orchestrator.py` (1463L — moteur principal)
- `Backend/Prod/api.py` (1519L — API exposée)
- `Backend/Prod/models/agent_router.py` (746L — routing agents)
- `Backend/Prod/models/provider_fallback_cascade.py` (484L — cascade de fallback)
- `Backend/Prod/models/execution_router.py` (285L)
- `Backend/Prod/models/` (inventaire de tous les clients : claude, gemini, groq, kimi, mimo, deepseek, mistral, codestral, ollama)
- `Backend/Prod/cli.py` (interface CLI actuelle)
- `Backend/Prod/core/apply_engine.py` (pipeline apply)
- `Backend/Prod/core/surgical_editor.py` + `surgical_editor_js.py`
- `Frontend/4. COMMUNICATION/ROADMAP.md` (workflow Manuel actuel — les 30 premières lignes suffisent)

**Travail à faire :**

**Partie 1 — Audit état réel**

1. **Inventaire agents disponibles** :
   - Pour chaque client (`*_client.py`) : modèle par défaut, capacités (code, vision, long context), état (actif/cassé/déprécié)
   - `agent_router.py` : logique de routing — sur quel critère choisit-il un agent ?
   - `provider_fallback_cascade.py` : la cascade est-elle event-driven ou polling ? Quels triggers ?

2. **Orchestrateur** (`orchestrator.py` 1463L) :
   - Responsabilités actuelles (plan parsing, step execution, retry, reporting)
   - Ce qui est synchrone vs asynchrone
   - Couplages forts (qui appelle qui) — dépendances circulaires ?
   - Dead code identifiable (fonctions jamais appelées)

3. **API** (`api.py` 1519L) :
   - Routes exposées, signatures
   - Rapport avec le CLI (`cli.py`) : le CLI appelle l'API ou directement l'orchestrateur ?
   - Authentification / sécurité

4. **Apply engine** :
   - Flux : plan.json → apply_engine → surgical_editor (py ou js) → fichier patché
   - Ce qui est validé avant/après apply
   - Modes (-f, -vfx, etc.) : lesquels fonctionnent, lesquels sont cassés

5. **Workflow Manuel actuel** :
   - Comment le workflow ROADMAP.md + HoméOS se connecte-t-il (ou ne se connecte pas) au moteur ?
   - Quelles parties du moteur sont bypassées dans le workflow manuel actuel ?

**Partie 2 — Vision architecture V4 Moteur**

Sur la base de l'audit, proposer une architecture cible pour les deux modes. Format : diagrammes texte + listes.

**Mode Manuel V4 :**
- Comment formaliser la ROADMAP comme source de vérité du moteur (pas juste un fichier markdown)
- Routine d'archivage : déclencheur, vérifications, format archive
- Contrat de rôles : interfaces attendues de chaque agent (Claude, Gemini, Second Arch)
- Gestion défection : arbre de décision (mission rate → ?)

**Mode Auto V4 (LangGraph) :**
- Graph proposé : nœuds (Architect, Worker, Reviewer, Fallback), arêtes (transitions), conditions de sortie
- Intégration LangGraph ou équivalent Python natif (StateGraph, nodes, edges)
- Timeout par nœud : valeurs recommandées par type de mission (hotfix < 30s, refactor < 5min, diag < 10min)
- Fallback chain : Claude → Gemini → GPT → log incident (schéma)
- Détection défection : pattern TERMINÉ sans livrable → mécanisme de détection

**Output attendu :** `Frontend/4. COMMUNICATION/audits/diag_7_engine.md`

Sections obligatoires :
- ## Inventaire agents (tableau : client | modèle | capacités | état)
- ## Orchestrateur : responsabilités, couplages, dead code
- ## Apply engine : flux et modes fonctionnels
- ## Workflow Manuel actuel vs moteur (connexions et bypasses)
- ## Vision Mode Manuel V4
- ## Vision Mode Auto V4 (LangGraph)
- ## Recommandations priorisées (critique / important / cosmétique)

---

**Document 1 — `audits/SYNTHESE_V4.md`**
Synthèse cross-cutting :
- Patterns récurrents (ex : SQLite sync dans async def, dual source of truth, monolithes > 500L)
- Ce qui est à refaire vs ce qui peut être conservé
- Architecture V4 cible : DB, backend, moteur, frontend, deploy

---

**Document 2 — `audits/PROJECTION_V4.md`**
**Objectif : la V4 la moins risquée possible, construite en séquence de valeur.**

**Philosophie :** Chaque phase doit être déployable et démontrable de façon autonome avant de passer à la suivante. On ne construit pas la totalité — on construit la prochaine chose qui crée de la valeur prouvable.

**Règle fondamentale :** La Phase 0 est un bloquant strict sur toutes les autres. Pas de schéma au rabais. On ne commence Phase A qu'une fois la DB validée par FJD.

**Séquence :**

**Phase 0 — Fondation DB (bloquant strict)**
Avant tout code applicatif, un schéma canonique, versionné, irréversible dans ses fondations.

Principes non négociables :
- **Un seul moteur** : PostgreSQL (prod) + SQLite WAL (dev local). Pas de fichier JSON comme état partagé.
- **Schéma normalisé** : chaque entité a une table propre, chaque relation une FK explicite avec contrainte.
- **Migrations versionnées** : Alembic ou équivalent. Aucun `ALTER TABLE` manuel, jamais. Chaque migration est idempotente et réversible.
- **Source de vérité unique par entité** : `users`, `students`, `classes`, `projects`, `subjects`, `sessions` — chaque entité a une et une seule table maître. Plus de `active_project.json`, plus de variables globales `_ACTIVE_PROJECT_ID`.
- **Rôles DB** : les permissions sont dans la DB, pas dans le code. Un `user` a un `role` (`admin`, `teacher`, `student`, `user`). Un utilisateur peut avoir plusieurs rôles (un élève est aussi un user).
- **Plans et features flags** : table `plans` + table `feature_flags` dès le départ. Pas hard-codé dans le code applicatif.
- **Audit trail** : toute écriture sensible (activation projet, notation, déploiement) logue dans une table `events`. Pas de perte silencieuse.

**Sécurité d'accès (même bloquant que la DB) :**

- **Login racine** : compte superadmin créé au boot via seed/env — jamais via UI publique. Pas de route `/register` qui crée un admin. Si la table `users` est vide au démarrage : mot de passe aléatoire généré, loggé une seule fois, changement obligatoire à la première connexion.
- **Contrôle d'inscription** : trois modes configurables en DB (`open` / `invite` / `closed`). Défaut scolaire : `invite` ou `closed`. Mode `invite` = lien tokenisé usage unique avec expiration. Jamais configurable dans le code.
- **Vérification d'identité** : email de vérification obligatoire (token TTL 24h), compte en état `pending` sans accès jusqu'à vérification. Flow élève alternatif : code de classe à 6 caractères, vérifié par le teacher.
- **Mots de passe** : bcrypt ou argon2 uniquement. Reset par token usage unique TTL 1h. Minimum 12 caractères. Reset élèves via teacher seulement.
- **Rate limiting sur auth** : 5 tentatives login / IP / 15 min → lockout. 3 créations compte / IP / heure. 3 demandes reset / email / heure.

Critère de sortie Phase 0 : schéma documenté + migrations propres sur DB vierge + seed de test (1 superadmin, 1 teacher, 2 classes, 5 élèves, 3 projets) + login racine fonctionnel + vérification email testée.

**Phase A — Demo Student (priorité absolue)**
Parcours minimal mais complet :
`onboarding élève` → `AHA moment` : Wiring (construction d'une interface) + présence en ligne (CI/CD → URL live)
Critère de succès : un élève sans compte existant arrive, construit quelque chose, a une URL publique en moins de 10 minutes.

**Phase B — Parcours Teacher**
`confection sujet` → `[Phase A déclenché pour un élève]` → `notation auto par référentiel`
Critère de succès : un enseignant crée un sujet, l'assigne, voit les élèves avancer, obtient une notation automatique par rapport à un référentiel (DNMADE ou autre).

**Phase C — Parcours User (non-scolaire)**
`onboarding user` → `AHA moment` identique : Wiring + présence en ligne
Même pipeline que Phase A mais sans contexte classe/sujet. Utilisateur autonome, créateur indépendant.

**Phase D — Cohabitation logique**
Rôles : admin / teacher / élève / user — cohabitent sur le même système.
Règle fondamentale : **un élève peut aussi être un user**. Double identité, accès cumulés.
Permissions, plans, visibilité des projets : chaque rôle accède à son périmètre, sans collision.

**Phase E — Plans tarifaires**
`free / Pro / Total` (contenu des tiers à définir avec FJD).
Architecture ouverte : le système doit anticiper N tiers sans hard-code. Feature flags ou permission matrix extensible.

**Phase F — Ouverture hexagonale**
Chaque feature est conçue comme un hexagone extensible :
- FEE (studio GSAP) → appelé à grossir (nouveaux modules, timeline UI, asset manager)
- Deploy → évolue (preview, staging, custom domain, analytics)
- Wire → évolue (collaboration temps réel, version history)
- Moteur → évolue (agents supplémentaires, LangGraph, auto-orchestration)
Principe : aucun système fermé. Toute feature V4 expose une interface d'extension documentée.

---

**Décision FJD** sur la base des deux documents → lancement V4 phase par phase.

---

**Fix 1 — WAL mode SQLite** (`bkd_service.py` L162)

Activer le Write-Ahead Log pour permettre les lectures concurrentes sans bloquer les écritures (prérequis 10k users).

```python
# AVANT (L162)
con = sqlite3.connect(str(BKD_DB_PATH))

# APRÈS
con = sqlite3.connect(str(BKD_DB_PATH))
con.execute("PRAGMA journal_mode=WAL")
con.execute("PRAGMA synchronous=NORMAL")
```

---

**Fix 2 — Migrer les 2 `bkd_db_con()` restants**

`bkd_router.py` L411 :
```python
# AVANT
with bkd_db_con() as con:
    con.execute("DELETE FROM conversations WHERE id=?", (conv_id,))

# APRÈS
from bkd_service import bkd_db
with bkd_db() as con:
    con.execute("DELETE FROM conversations WHERE id=?", (conv_id,))
```

`stitch_router.py` L34-35 :
```python
# AVANT
from bkd_service import bkd_db_con
with bkd_db_con() as con:

# APRÈS
from bkd_service import bkd_db
with bkd_db() as con:
```

---

**Fix 3 — `GET /api/projects/active` token-aware** (`projects_router.py` L143-145)

```python
# AVANT
@router.get("/projects/active", response_model=ProjectInfo)
async def get_active_project_route():
    active_id = get_active_project_id()

# APRÈS
@router.get("/projects/active", response_model=ProjectInfo)
async def get_active_project_route(request: Request):
    token = request.headers.get("X-User-Token")
    active_id = get_active_project_id(token)
```

---

**Fix 4 — `POST /api/projects/activate` → update `students.project_id` sans token** (`projects_router.py` L179, après `set_active_project_id`)

Quand le prof active un projet élève sans token, déduire l'étudiant depuis le format du project_id (`{class_id}-{student_id}` ou `{class_id}-{student_id}-{subject_slug}`) et mettre à jour `students.project_id` directement.

```python
# AJOUTER après set_active_project_id(req.id, token) (L179) :
if not token:
    try:
        from bkd_service import bkd_db
        with bkd_db() as con:
            con.execute(
                "UPDATE students SET project_id=? WHERE ? LIKE class_id || '-' || id || '%'",
                (req.id, req.id)
            )
            logger.info(f"[M304] Student project_id updated from project_id pattern: {req.id}")
    except Exception as e:
        logger.warning(f"[M304] Student update failed: {e}")
```

---

**Contraintes :**

- Ne pas supprimer `active_project.json` ni son fallback dans `get_active_project_id` — le garder comme filet de sécurité legacy.
- Ne pas modifier les signatures des autres fonctions.
- Ne pas toucher `projects_router.py` au-delà des lignes indiquées.
- Tester : après restart serveur, prof active projet → `GET /api/projects/active` avec header `X-User-Token: {token_etudiant}` retourne le bon projet.

**Livraison :** 4 fichiers modifiés + rapport confirmant que `GET /api/projects/active` retourne le bon projet par token.

---

---

### Thème 30 — Moteur AetherFlow (optimisation par les sessions)

---

### Mission 290 — Contrôle des clés API par session + optimisation cascade
**STATUS: 🟠 PRÊTE | DATE: 2026-04-10 | ACTOR: QWEN**

**Principe :** À chaque nouveau projet d'un user, la stack de clés API est contrôlée. Le résultat met à jour la "meilleure stack du moment" globale. Plus il y a d'utilisateurs, mieux le système marche — effet réseau.

**Mécanisme :**
- Au `POST /api/projects/activate` → contrôle asynchrone de chaque provider configuré (gemini, groq, openai, etc.)
- Résultat stocké dans `db/provider_health.json` : `{ provider, latency_ms, success: bool, last_check, model }`
- Cascade optimisée automatiquement : le provider le plus rapide + fiable passe en #1
- Fallback sur la stack précédente si la nouvelle échoue

**Avantage :**
- Pas de ping permanent — les contrôles sont déclenchés par les sessions réelles
- Les erreurs API (quota, clé expirée, downtime) sont détectées organiquement
- Argument marketing : "plus on est d'utilisateurs, plus AetherFlow est rapide"
- L'expérimentation avec les étudiants = données massives de fiabilité API

**Stack actuelle à tester :**
1. Gemini (vision + design tokens) — fiable mais lent
2. Groq (vision ? ultra rapide) — à tester, si oui → priorité #1
3. OpenAI — payant, bon fallback
4. DeepSeek — bon rapport qualité/prix
5. Qwen — gratuit, fallback
6. Mimo — gratuit via OpenRouter
7. Watson — gratuit IBM Cloud Lite

**Fichiers :** `auth_router.py` (vérif au login), nouveau `engine_optimizer.py`, `api_key_urls.py`

---

### Mission 291 — Drill A : Avec manifest (voie Stitch)
**STATUS: 🟠 PRÊTE | DATE: 2026-04-10 | ACTOR: QWEN**

**Flux :** Upload manifest → Upload écrans (1-4) → Contrôle clés → Lancement Stitch → Sync polling 2min

- Bouton rond pulsant "Créer un projet" sur canvas vide
- Manifest obligatoire (sinon → redirect Cadrage)
- Écrans uploadés (max 4 pour latence)
- Clés vérifiées → ouverture Stitch
- Polling 2min → détection nouveaux screens → pull auto

**Fichiers :** `WsStitchDrill.js` (existant, à adapter), `WsStitchSync.js` (existant), `stitch_router.py`

---

### Mission 292 — Drill B : Sans manifest (voie locale HomeOS)
**STATUS: 🟠 PRÊTE | DATE: 2026-04-10 | ACTOR: QWEN**

**Flux :** Upload écrans (1-4, obligatoire) → Contrôle clés + optimisation cascade → Cadrage (manifest editor + extraction tokens + validation Sullivan) → Forge background → Canvas ready

- Pas de manifest bloquant — les écrans suffisent
- Clés contrôlées → cascade optimisée
- Cadrage transformé : manifest editor inline avec design MD + swatches + "voici ce que j'ai compris"
- Pendant la validation → forge HTML Tailwind en background
- Canvas → écrans prêts, draggables, éditables

**Fichiers :** nouveau `WsLocalDrill.js`, `cadrage_alt.html` → `WsManifestEditor.js`, `forge_router.py` optimisé

---

### Mission 293 — Extraction tokens design dès 1er upload
**STATUS: 🟠 PRÊTE | DATE: 2026-04-10 | ACTOR: QWEN**

**Objectif :** Dès le 1er écran uploadé, extraire les tokens design (couleurs, typo, spacing) via vision LLM.

**Priorité cascade :**
1. **Groq vision** — si disponible, ultra rapide (~1s) → extraction couleurs/typo
2. Gemini vision — fallback (~3-5s)
3. Regex SVG/CSS — dernier recours (couleurs hex, font-family)

**Résultat :** Design MD généré automatiquement → swatches → Sullivan propose "voici ce que j'ai compris, tu valides ?"

**Fichiers :** `svg_to_tailwind.py` (existant), nouveau `design_token_extractor.py`, `cadrage_router.py`

---

**Comportement attendu :**

```bash
# Usage : passer des chemins en arguments
python3 groq-versatile.py path/to/file1.py path/to/file2.js

# Groq voit en contexte système :
# === FICHIER : path/to/file1.py ===
# <contenu complet>
# === FICHIER : path/to/file2.js ===
# <contenu complet>
```

---

**Modification à apporter :**

1. Lire `sys.argv[1:]` — liste de chemins fichiers.
2. Pour chaque chemin : lire le fichier, construire un bloc `=== FICHIER : {path} ===\n{contenu}\n`.
3. Concaténer tous les blocs → `files_context` (str).
4. Dans `history`, ajouter un message `user` **avant** la boucle REPL :
   ```python
   if files_context:
       history.append({"role": "user", "content": f"Voici les fichiers de la codebase :\n\n{files_context}"})
       history.append({"role": "assistant", "content": "Fichiers reçus et analysés. Je suis prêt à travailler."})
   ```
5. Afficher à la console : `[bold green]📂 {N} fichier(s) injectés[/bold green]` si fichiers chargés.
6. Si un chemin n'existe pas → warning console + continuer (ne pas crasher).

---

**Contraintes :**

- Ne pas casser le flow existant (chat loop, streaming, Markdown render) — ajouter seulement avant la boucle.
- Ne pas toucher `LLAMA.md`, `.env`, `groq-r1.py`.
- Le fichier final doit rester < 80 lignes.
- Tester : `python3 groq-versatile.py groq-versatile.py` → Groq doit pouvoir décrire son propre code quand on lui demande.

**Livraison :** `groq-versatile.py` modifié + CR dans ROADMAP.md.

---

**Fichiers cibles :**

- `Frontend/3. STENCILER/routers/class_router.py` — endpoint `GET /{class_id}/dashboard` (L442-474)
- `Frontend/3. STENCILER/static/templates/teacher_dashboard.html` — `loadDashboard()` + `startAutoRefresh()` (L335-760)

---

**Corrections à appliquer (selon diagnostic) :**

**Fix A — Batch UPDATE milestones (class_router.py L457-463) :**

Remplacer la boucle avec `UPDATE` individuel par un batch :

```python
student_list = []
updates = []
for s in students:
    milestone = detect_milestone(s[4]) if s[4] else {"level": 0, "label": "Aucun projet"}
    if milestone["level"] != s[5]:
        updates.append((milestone["level"], s[0]))
    student_list.append({
        "id": s[0], "display": s[1],
        "project_id": s[4], "milestone": milestone,
    })
if updates:
    with supabase_db_con() as con:
        con.executemany("UPDATE students SET milestone=? WHERE id=?", updates)
```

**Fix B — Frontend : debounce loadDashboard (teacher_dashboard.html L335) :**

Ajouter un verrou simple pour éviter les appels simultanés :

```js
var _loadDashboardPending = false;
function loadDashboard() {
    if (_loadDashboardPending) return;
    var classId = document.getElementById('class-select').value;
    if (!classId) return;
    _loadDashboardPending = true;
    currentClassId = classId;
    // ... reste inchangé ...
    fetch(API + '/' + classId + '/dashboard')
        .then(function(r) { return r.json(); })
        .then(function(data) { renderDashboard(data); })
        .catch(function(e) { console.error('loadDashboard error:', e); })
        .finally(function() {
            document.getElementById('loading').hidden = true;
            document.getElementById('dashboard').hidden = false;
            _loadDashboardPending = false;
        });
}
```

---

**Contraintes :**

- Ne pas toucher aux fonctions `renderDashboard`, `renderSubjects`, `loadSubjects` — elles sont stables.
- Ne pas ajouter de `dashboardLoading` guard global (cause de freeze précédemment introduit par QWEN).
- Ne pas modifier le schéma DB ni les routes.
- Tester : charger classe A → classe B → classe A en moins de 2 secondes → pas de freeze.

**Livraison :** rapport avec la cause identifiée + fichiers patchés.

---

---

### Mission 304 — Activate Token-less : Synchronisation DB Students
**STATUS: 🟡 EN COURS | DATE: 2026-04-15 | ACTOR: QWEN**

**Objectif :** L'activation d'un projet par le professeur via le dashboard (sans token) doit synchroniser le `project_id` dans la table `students`.
- **Problème actuel** : Seul `active_project.json` est mis à jour, créant une désynchronisation pour l'élève.
- **Solution** : Déduire l'élève à partir du `project_id` et mettre à jour sa ligne en DB.

---

**Fichier unique :** `Frontend/3. STENCILER/server_v3.py`

**Ligne à modifier :** L244

```python
# AVANT
uvicorn.run("server_v3:app", host="0.0.0.0", port=9998, reload=True)

# APRÈS
uvicorn.run("server_v3:app", host="0.0.0.0", port=9998, reload=False)
```

---

**Procédure de restart propre (à exécuter après le patch) :**

```bash
# 1. Tuer tous les process sur le port
lsof -ti :9998 | xargs kill -9 2>/dev/null; sleep 1

# 2. Lancer le serveur
cd /Users/francois-jeandazin/AETHERFLOW/Frontend/3.\ STENCILER
nohup python3 server_v3.py > /tmp/server_v3.log 2>&1 &

# 3. Attendre 3 secondes puis vérifier
sleep 3 && curl -s http://localhost:9998/api/classes | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK —', len(d.get('classes',[])), 'classes')"
```

---

**Contraintes :**

- Un seul fichier modifié : `server_v3.py` L244.
- Ne pas modifier le host ni le port.
- Rapport : confirmer que `curl /api/classes` retourne JSON valide après restart.

---

**Fichier unique :** `Frontend/3. STENCILER/static/js/workspace/WsStitchDrill.js`

---

**Conflit 1 — L259-270 : wireStep 4**

Garder la version HEAD :
```js
else if (stepIndex === 4) {
    loadForgedScreens();
}
```

Supprimer la version 14b7279 (bloc inline onclick avec debug logs).

---

**Conflit 2 — L438-453 : uploadManifest après save**

Garder la version HEAD :
```js
_finishButton(statusEl.parentNode);
```

Supprimer la version 14b7279 (création inline du bouton avec skipBtn.remove() + startBtn).

---

**Conflit 3 — L508-529 : fonction `_finishButton`**

Garder la version HEAD (la fonction complète) :
```js
function _finishButton(container, prepend) {
    container.querySelectorAll('button').forEach(b => {
        if (b.textContent.includes('Commencer')) b.remove();
    });
    const btn = document.createElement('button');
    btn.id = 'drill-finish';
    btn.textContent = 'Commencer à travailler →';
    btn.className = 'px-8 py-3 bg-gradient-to-r from-[#8cc63f] to-[#6a9a2f] text-white text-[13px] font-bold uppercase tracking-wider rounded-[16px] hover:shadow-lg transition-all cursor-pointer';
    btn.onclick = () => { hide(); if (window.ManifestBox) window.ManifestBox.show(); };
    if (prepend) container.insertBefore(btn, container.firstChild);
    else container.appendChild(btn);
    return btn;
}
```

Supprimer la version 14b7279 (vide — juste `>>>>>>>`).

---

**Vérification :**

Après résolution, le fichier ne doit contenir **aucun** marqueur `<<<<<<<`, `=======`, `>>>>>>>`.
`grep -c "<<<<<<\|=======\|>>>>>>>" WsStitchDrill.js` doit retourner `0`.

**Aucun autre fichier touché.**

---

---

### Mission 281 — Drill step 3 : bouton "ouvrir dans l'éditeur" + fix 404 manifest
**STATUS: 🔴 PRIORITÉ | DATE: 2026-04-12 | ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE

**Contexte :** Le drill `WsStitchDrill.js` a 5 étapes. Step 3 (manifest) s'arrête à l'affichage du manifest ou au formulaire d'upload — **il n'y a aucun bouton pour ouvrir le manifest dans l'éditeur**. `window.ManifestBox.show()` existe (ManifestBox.js L442) mais n'est jamais appelé depuis le drill.

**Fichier unique :** `Frontend/3. STENCILER/static/js/workspace/WsStitchDrill.js`

---

**Fix 1 — Ajouter le bouton "ouvrir l'éditeur" dans `loadManifestStep()`**

Dans la branche `hasContent` (L331-339), remplacer le HTML du step manifest par :

```js
section.innerHTML = `
    <div class="bg-white border border-[#e5e5e5] rounded-[16px] p-4 mb-4 text-left text-[11px] text-[#3d3d3c]">
        <div class="font-bold text-[12px] mb-1">${name}</div>
        ${desc ? '<div class="text-[#9a9a98] mb-2 text-[10px]">' + desc.substring(0, 200) + '</div>' : ''}
        <div class="flex gap-3 text-[9px] text-[#9a9a98] mb-3"><span>archétype: ${archetype}</span><span>écrans: ${(m.screens||[]).length}</span></div>
    </div>
    <div class="flex gap-2">
        <button id="drill-open-editor" class="px-6 py-2.5 border border-[#8cc63f] text-[#8cc63f] text-[11px] font-bold rounded-[12px] hover:bg-[#f0fdf4] transition-all">ouvrir l'éditeur →</button>
        <button id="drill-continue-manifest" class="px-6 py-2.5 bg-[#8cc63f] text-white text-[11px] font-bold rounded-[12px] hover:bg-[#7ab536] transition-all">continuer →</button>
    </div>
`;
document.getElementById('drill-open-editor').onclick = () => {
    if (window.ManifestBox) window.ManifestBox.show();
};
document.getElementById('drill-continue-manifest').onclick = () => { currentStep = 4; renderStep(); };
```

---

**Fix 2 — Ajouter le même bouton après un upload réussi**

Dans `uploadManifest()` (L374), après `statusEl.textContent = '✓ Manifest sauvegardé'`, avant le `setTimeout` :

```js
// Afficher le bouton éditeur sans attendre le step suivant
const editorBtn = document.createElement('button');
editorBtn.textContent = 'ouvrir l\'éditeur →';
editorBtn.className = 'mt-3 px-6 py-2 border border-[#8cc63f] text-[#8cc63f] text-[11px] font-bold rounded-[12px] hover:bg-[#f0fdf4] transition-all block';
editorBtn.onclick = () => { if (window.ManifestBox) window.ManifestBox.show(); };
statusEl.parentNode.insertBefore(editorBtn, statusEl.nextSibling);
```

---

**Fix 3 — Guard projectId null dans `loadManifestStep()`**

L318 : `const projectId = session.active_project_id || session.project_id;`

Si `projectId` est null/undefined → la fetch part sur `/api/projects/undefined/manifest` → 404 silencieux → `showManifestUpload()` alors que le manifest existe.

Ajouter avant le fetch :
```js
if (!projectId) {
    showManifestUpload(section, 'projet non trouvé dans la session');
    return;
}
```

---

**Livrable :**
- Step 3 manifest présent → boutons "ouvrir l'éditeur" ET "continuer"
- Step 3 manifest absent → upload + bouton "ouvrir l'éditeur" après upload réussi
- Guard projectId null → message explicite au lieu de 404 silencieux
- `window.ManifestBox` vérifié avant appel (`if (window.ManifestBox)`)
- Aucun autre fichier touché

---

---

### Mission 298 — Double contexte student / user : pont FK + project panel double tab
**STATUS: 🟠 PRÊTE | DATE: 2026-04-12 | ACTOR: QWEN (Back) + GEMINI (Front) — PARALLÈLE**

**Principe :** Un étudiant a deux vies :
1. **Student** — le drill école : le prof assigne un sujet, l'étudiant travaille dessus. Workflow basique, services institutionnels.
2. **User** — le citoyen moyen : multi-projets perso, BYOK, libre.

Les deux coexistent. Le student n'est pas exclu du user. Le panel projet affiche deux tabs :
- Tab 1 (student) : `sujet assigné → écrans`
- Tab 2 (user) : `mes projets perso → écrans`

**Lien secure :** `students.user_id` (FK nullable → `users.id`). Au login étudiant, si pas de lien → créer user + écrire le lien (write once).

---

#### BACKEND (QWEN) — 3 fichiers

**Fichier 1 — Migration SQL (one-shot)**

`supabase/migrations/006_student_user_link.sql` :
```sql
ALTER TABLE students ADD COLUMN user_id TEXT REFERENCES users(id);
CREATE INDEX IF NOT EXISTS idx_students_user_id ON students(user_id);
```

**Fichier 2 — `auth_router.py`**

Dans `auth_login_student()` (après `user = _find_user_by_name(display)`) :
- Si student a un `user_id` → l'utiliser directement (plus de lookup par nom)
- Si student n'a pas de `user_id` → créer/récupérer user → écrire `students.user_id = user_id`
- Retourner les deux : `student_id` ET `user_id` dans la réponse

Dans `auth_register()` (bloc student) :
- Même logique : après création du user, écrire `students.user_id = user_id`

**Fichier 3 — `projects_router.py`**

Dans `list_all_projects_route()` :
- Student voit : ses projets perso (`user_id = uuid`) + le projet student (`students.project_id`)
- La requête UNION les deux sources

```python
# Student : projets perso + projet student
rows = conn.execute("""
    SELECT DISTINCT p.id, p.name, p.path, p.created_at, p.last_opened
    FROM projects p
    WHERE p.user_id = ?
       OR p.id = (SELECT s.project_id FROM students s WHERE s.id = ? AND s.project_id IS NOT NULL)
    ORDER BY p.last_opened DESC
""", (user_id, student_id)).fetchall()
```

Dans `activate_project_route()` :
- Si le projet activé appartient au student (via `students.project_id`) → écrire dans `students.project_id`
- Sinon → c'est un projet perso du user, juste `last_opened`

---

#### FRONTEND (GEMINI) — 2 fichiers

**Fichier 1 — `bootstrap.js`**

Ne plus cacher le project switcher aux students. Le student a besoin de naviguer entre son sujet et ses projets perso.

**Fichier 2 — `WsProjectPanel.js`**

Deux tabs :
```
┌─────────────────┬──────────────────┐
│ sujet assigné   │ mes projets      │
└─────────────────┴──────────────────┘
```

- **Tab 1 (student)** : affiché si `session.student_id && session.project_id`
  - Header : nom du sujet (via `GET /api/projects/{project_id}/manifest`)
  - Liste des écrans du sujet (via `/api/retro-genome/imports?project_id=...`)
  - Pas de bouton supprimer, pas de bouton créer

- **Tab 2 (user)** : affiché pour tous les users
  - Liste des projets perso (`GET /api/projects` — déjà filtré par user_id côté serveur)
  - Bouton "+ Nouveau projet" (appelle `POST /api/projects/create`)
  - Chaque projet : expand → écrans → activer

**Logique de tab :**
- Par défaut → Tab 1 si student, Tab 2 sinon
- `localStorage` mémorise le dernier tab actif
- Les deux tabs partagent le même mécanisme d'activation (`POST /api/projects/activate`)

**Session :** `homeos_session` stocke maintenant `student_id` ET `user_id` comme champs distincts. Le code existant qui lit `session.project_id` continue de fonctionner.

---

**Fichiers Backend :** `auth_router.py`, `projects_router.py`, `supabase/migrations/006_student_user_link.sql`
**Fichiers Frontend :** `WsProjectPanel.js`, `bootstrap.js`, `login.html`, `student_login.html`

**Critères de succès :**
1. Au login étudiant → `students.user_id` écrit (FK)
2. Panel projet : 2 tabs visibles pour un student
3. Tab 1 = sujet prof, Tab 2 = projets perso
4. Student peut créer un projet perso (Tab 2 → "+ Nouveau projet")
5. Aucun projet existant cassé

---

---

### Mission 280-DIAG — Trois bugs bloquants du drill : manifest 404, stitch sync loop, race condition upload
**STATUS: 🔴 DIAG | DATE: 2026-04-12 | ACTOR: QWEN**

---

**Bug 1 — Manifest 404 persistant pour les étudiants existants**

**Cause identifiée :** `GET /api/projects/{project_id}/manifest` (projects_router.py L290-295) lève 404 si `manifest.json` est absent sur disque. Le dossier projet n'est créé qu'au `register` (nouveaux étudiants). Les sessions existantes n'ont pas de dossier `projects/{project_id}/` → le fichier n'existe pas → 404 systématique.

Le `PUT /api/projects/{project_id}/manifest` crée le dossier (L303) mais le `GET` n'a pas ce filet.

**Fix :** dans `GET /api/projects/{project_id}/manifest`, si manifest absent → créer le dossier + retourner un manifest par défaut plutôt que 404 :
```python
@router.get("/projects/{project_id}/manifest")
async def get_project_manifest_route(project_id: str):
    p_path = PROJECTS_DIR / project_id
    manifest_path = p_path / "manifest.json"
    if not manifest_path.exists():
        # Créer le dossier + manifest minimal plutôt que 404
        p_path.mkdir(parents=True, exist_ok=True)
        default = {"id": project_id, "name": project_id, "screens": [], "stitch_project_id": None}
        manifest_path.write_text(json.dumps(default, indent=2), encoding='utf-8')
        return default
    manifest = get_project_manifest(project_id)
    if not manifest:
        raise HTTPException(status_code=404, detail="Manifest not found")
    return manifest
```

**Fichier :** `Frontend/3. STENCILER/routers/projects_router.py` — L290-296

---

**Bug 2 — Stitch sync 404 en boucle au premier poll**

**Cause identifiée :** `WsStitch._syncProjectId()` appelle `GET /api/stitch/project-info`. Si `stitch_project_id` est null dans le manifest → retourne `{ linked: false }` (HTTP 200, pas 404). Le 404 vient d'ailleurs : `WsStitch.sync()` (L254) appelle `POST /api/stitch/sync` — cette route appelle `_get_stitch_key()` puis tente de récupérer les données Stitch. Si la clé est absente → route lève HTTPException 501, pas 404. 

Le 404 est probablement sur `GET /api/stitch/screens?project_id=` avec `project_id` vide (string vide) → endpoint Stitch retourne 404 car l'ID est invalide.

**Test de diagnostic :**
```js
// Dans la console workspace après ouverture du panel Stitch
fetch('/api/stitch/project-info').then(r=>r.json()).then(console.log)
// Si linked: false → project_id vide → screens?project_id= → 404

// Vérifier la valeur exacte envoyée
window.wsStitch?.projectIdInput?.value  // vide = cause confirmée
```

**Fix :** dans `WsStitch.loadSession()`, si `project_id` est vide ou null → ne pas appeler `GET /api/stitch/screens` → afficher "aucun projet lié" sans requête :
```js
async loadSession() {
    const projectId = this.projectIdInput?.value?.trim();
    if (!projectId) {
        // Afficher état "non lié" sans appel API
        this._renderUnlinked();
        return;
    }
    // ... suite normale
}
```

**Fichier :** `Frontend/3. STENCILER/static/js/workspace/WsStitch.js` — `loadSession()` L159

---

**Bug 3 — Race condition upload manifest dans le drill**

**Cause suspectée :** `WsStitchDrill.js` upload le manifest via `PUT /api/projects/{id}/manifest`, puis immédiatement lit l'état via `GET /api/projects/active/manifest`. Si le `PUT` est async et que le `GET` arrive avant que l'écriture disque soit terminée → le GET retourne l'ancienne version ou 404.

**Test de diagnostic :**
```js
// Dans WsStitchDrill.js, chercher la séquence upload → read
// Y a-t-il un await sur le PUT avant le GET suivant ?
// Si le GET suit sans await → race condition confirmée
```

**Fix probable :** s'assurer que le GET ne part qu'après résolution du PUT :
```js
await fetch('/api/projects/active/manifest', { method: 'PUT', ... });
// Seulement après :
const manifest = await fetch('/api/projects/active/manifest').then(r => r.json());
```

**Fichier :** `Frontend/3. STENCILER/static/js/workspace/WsStitchDrill.js` — séquence upload manifest

---

**Livrable QWEN :**
1. Fix Bug 1 : `GET /api/projects/{id}/manifest` → créer manifest par défaut si absent
2. Confirmer Bug 2 via test console → fix `loadSession()` guard
3. Confirmer Bug 3 via lecture `WsStitchDrill.js` → fix await séquence
4. Reporter les résultats des tests console dans le rapport

---

---

### Mission 280 — Landing Canvas + Drill paramétrage Stitch
**STATUS: 🟠 EN COURS | DATE: 2026-04-10 | ACTOR: QWEN**

**Flux du drill actuel (implémenté) :**
1. **Écrans** (1-4) → upload PNG/SVG/JPG avec drag&drop
2. **Clés API** → 5 champs (Gemini, Groq, OpenAI, DeepSeek, Qwen) avec boutons OK + explication optimisation moteur ("Plus tu renseignes de clés, plus le moteur est fiable et rapide")
3. **Manifeste** → upload si absent, aperçu si présent + lien vers ManifestBox editor
4. **Écrans forgés** → liste les imports forgés pendant la config des clés
5. **Canvas** → "Commencer à travailler"

**Bouton "+ Nouveau projet"** → affiché en bas à droite pour les élèves quand le canvas n'est pas vide (z-index 99999)

**Issues connues :**
- **Manifest 404 persistant** : Même avec le fichier manifest.json sur disque, l'endpoint `/api/projects/{id}/manifest` retourne 404. Le dossier projet n'est pas créé automatiquement au login pour les étudiants existants (seulement pour les nouveaux). Fix partiel : `auth_router.py` crée le dossier + manifest par défaut au register, mais les sessions existantes n'ont pas de dossier projet.
- **Stitch sync 404 en boucle** : Le polling retourne 404 quand aucun `stitch_project_id` n'est lié. Arrêt auto implémenté mais le 404 persiste au premier poll.
- **Manifest upload du drill** : Le upload fonctionne mais le manifest n'est pas toujours persisté correctement (race condition ?)

**Fichiers :** `WsStitchDrill.js`, `auth_router.py`, `projects_router.py`, `WsImportList.js`

---

### Mission 294 — Circuit Breaker + Passive Health Monitoring (Zero-Cost Smart Routing)
**STATUS: 🟠 PRÊTE | DATE: 2026-04-11 | ACTOR: QWEN**

**Principe :** Ne jamais "pinguer" pour tester un provider. Utiliser les **vraies requêtes** comme capteurs de santé. Si DeepSeek plante, toute la classe bascule automatiquement sur Gemini/Groq.

**1. Circuit Breaker (Coupe-circuit) :**
- **Closed** (Normal) : Les requêtes passent vers le provider (ex: DeepSeek)
- **Open** (Sécurité) : Si 3 requêtes échouent (timeout/503) → coupe-circuit saute → bascule auto sur fallback (Groq/Gemini) pendant 5 min
- **Half-Open** (Test) : Après 5 min → 1 seule requête test → si OK → Closed, sinon → Open pour 5 min de plus

**2. Monitoring Passif TTFT (Time To First Token) :**
- Mesurer le temps du premier token de chaque requête
- Si moyenne glissante > 10s → provider marqué "Congested" 🟠
- UI : voyant "DeepSeek encombré — passer sur Gemini ?"

**3. Headers Rate Limit :**
- Lire `X-RateLimit-Remaining` et `X-RateLimit-Reset` sur chaque réponse réussie
- Savoir exactement où on en est sans appel de test

**4. Mutualisation classe (Smart Routing) :**
- Si l'élève A détecte DeepSeek DOWN → info partagée via serveur AetherFlow
- Les 29 autres élèves basculent instantanément sur fallback sans tester
- `provider_health.json` partagé sur le serveur : `{ provider, status, last_check, avg_ttft, failure_count }`

**Implémentation — `ModelHealthManager` :**
```python
class ModelHealthManager:
    def __init__(self):
        self.failure_count = 0
        self.status = "HEALTHY"  # HEALTHY, DEGRADED, DOWN
        self.last_failure_ts = 0

    def record_success(self, latency):
        self.failure_count = 0
        self.status = "DEGRADED" if latency > 15.0 else "HEALTHY"

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_ts = time.time()
        if self.failure_count >= 3:
            self.status = "DOWN"

    def can_attempt(self):
        if self.status == "DOWN":
            return (time.time() - self.last_failure_ts) > 300  # 5 min
        return True
```

**Fichiers :**
- Nouveau `model_health.py` — `ModelHealthManager` par provider (gemini, deepseek, groq, etc.)
- `gemini_client.py` / `deepseek_client.py` — `record_success(latency)`, `record_failure()`
- `rbac_middleware.py` — `check_provider_health(provider)` → fallback si DOWN
- UI — voyant provider dans settings drawer (🟢/🟠/🔴)
- `provider_health.json` — état partagé serveur (mis à jour en mémoire, persisté toutes les 30s)

**Avantage marketing :** "Plus on est d'utilisateurs, plus AetherFlow détecte vite les pannes API et bascule sur des providers sains."

---

### Mission 295 — Sullivan "Micro-Mode" (Global Collapsed State)
**STATUS: 🟠 PRÊTE | DATE: 2026-04-11 | ACTOR: GEMINI**

**Objectif :** Implémenter un mode "réduit" pour Sullivan utilisable partout dans l'application pour minimiser l'encombrement visuel.

**Spécifications :**
- **UI :** Hauteur réduite au strict minimum (input + bouton send).
- **Behavior :** Masquage de l'historique et des boutons secondaires (`edit code`, etc.) dans cet état.
- **Trigger :** Bouton de collapse/expand sur le header.
- **Persistence :** L'état (ouvert/réduit) est mémorisé via localStorage.
- **Global scope :** S'applique au Chat Main et au Surgical Sullivan.

**Fichiers :** `WsChatBase.js`, `WsChatSurgical.js`, `bootstrap.js` (CSS global)

---

---

### Mission 283a — Backend : RBAC middleware + Entitlements + Workspaces DB
**STATUS: 🔴 PRIORITÉ | DATE: 2026-04-10 | ACTOR: QWEN**

**Objectif :** Mettre en place le modèle RBAC + Entitlements côté backend (DB + middleware FastAPI).

**Livrables :**
1. **Migration 005** — `supabase/migrations/005_workspaces_and_entitlements.sql`
   - Table `workspaces` (id, name, plan, owner_id)
   - Table `workspace_members` (user_id, workspace_id, role_in_workspace)
   - Colonne `plan` dans `users` (FREE/PRO/MAX)
   - Seed : workspace personnel par user existant

2. **`rbac_middleware.py`** — Middleware FastAPI + dépendances
   - `get_current_user(token) → User` — résout le token, retourne `{ id, name, role, plan, workspace_id, entitlements }`
   - `@require_role("TEACHER")` — décorateur d'accès par rôle
   - `check_entitlement(user, feature) → bool` — vérifie un droit spécifique
   - `check_quota(user, feature) → bool` — vérifie un quota dynamique

3. **Matrice d'entitlements par plan :**
   ```python
   PLAN_LIMITS = {
       "FREE":  {"max_projects": 3,  "ai_models": ["qwen", "llama"],    "stitch": False, "byok": False, "monthly_tokens": 50_000},
       "PRO":   {"max_projects": 20, "ai_models": ["*"],               "stitch": True,  "byok": True,  "monthly_tokens": 500_000},
       "MAX":   {"max_projects": 999,"ai_models": ["*"],               "stitch": True,  "byok": True,  "monthly_tokens": None},
   }
   ```

4. **Enrichir les endpoints existants :**
   - `POST /api/auth/register` → crée workspace personnel (`ws_{user_id}`)
   - `GET /api/me` → retourne `{ user_id, name, role, plan, workspace_id, entitlements }`
   - `GET /api/me/keys` → protégé par `X-User-Token`

**Fichiers :** `auth_router.py`, `rbac_middleware.py`, `bkd_service.py`, `005_workspaces_and_entitlements.sql`, `server_v3.py`

---

---

### Thème 29 — Sécurité clés API : isolation élève + masquage

---

---

### Mission 268 — Chiffrement : bcrypt pour les mots de passe + Fernet pour les clés API
**STATUS: 🔴 PRIORITÉ | DATE: 2026-04-12 | ACTOR: QWEN**

**Contexte :** deux faiblesses crypto dans la DB SQLite :
- Mots de passe profs : SHA-256 sans sel → vulnérable aux rainbow tables si DB volée
- Clés API (Stitch, HF) : stockées en clair → exploitables directement si DB volée

**Dépendances à ajouter dans `requirements.txt` :**
```
bcrypt>=4.0.0
cryptography>=41.0.0
```

---

**Fix 1 — Mots de passe : SHA-256 → bcrypt**

Fichier : `Frontend/3. STENCILER/routers/auth_router.py` — `_hash_password()` L516-518 et les deux appels.

```python
# Avant
import hashlib
def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Après
import bcrypt
def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def _verify_password(password: str, stored_hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
```

Remplacer la comparaison directe dans le login prof :
```python
# Avant
if password_hash != stored_hash:

# Après
if not _verify_password(req.password, stored_hash):
```

**Migration :** les hashes SHA-256 existants en DB sont incompatibles avec bcrypt. À la première connexion d'un utilisateur avec l'ancien hash, forcer la réinitialisation de mot de passe (retourner 401 avec `detail="reset_required"`). Le frontend affiche "veuillez redéfinir votre mot de passe".

---

**Générer la FERNET_KEY une fois :**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
Ajouter dans `.env` : `FERNET_KEY=<valeur générée>`. Ne jamais la committer.

---

**Livrable QWEN :**
1. `bcrypt` pour hash + verify mots de passe dans `auth_router.py`
2. Logique `reset_required` sur ancien hash SHA-256
3. `core/crypto_keys.py` avec `encrypt_key` / `decrypt_key`
4. `stitch_router.py` : déchiffrement à la lecture des clés
5. Migration transparente (`encrypted` column) dans `user_keys`
6. `requirements.txt` mis à jour

**Fichiers à lire :**
- `Frontend/3. STENCILER/routers/auth_router.py` — L514-570
- `Frontend/3. STENCILER/routers/stitch_router.py` — `_get_stitch_key()`
- `Frontend/3. STENCILER/core/key_resolver.py`

---

---

### Mission 267 — DIAG + FIX : gestion des clés API — isolation élève, masquage, logs
**STATUS: 🔴 PRIORITÉ | DATE: 2026-04-12 | ACTOR: QWEN**

**Contexte :** Audit sécurité sur la gestion des clés API (Stitch, Hugging Face). Trois problèmes identifiés à corriger dans le même fichier principal `stitch_router.py` + `stitch_client.py`.

---

**Problème 1 — Résolution de clé biaisée admin/prof** (CRITIQUE)

Dans `stitch_router.py` — `_get_stitch_key()` L37-39 :
```python
"WHERE uk.provider = 'stitch' AND u.role IN ('admin','prof') "
"ORDER BY u.role DESC LIMIT 1"
```
Un élève qui renseigne son propre token Stitch ne sera jamais trouvé. Pire : le token du prof est utilisé à sa place.

**Fix :** résoudre d'abord par `user_id` de la session courante, puis fallback prof/admin :
```python
def _get_stitch_key(user_id: str = None) -> str:
    key = os.getenv("STITCH_API_KEY", "")
    if key:
        return key
    try:
        conn = get_db_connection()
        # 1. Clé propre à l'utilisateur
        if user_id:
            row = conn.execute(
                "SELECT api_key FROM user_keys WHERE user_id=? AND provider='stitch'",
                (user_id,)
            ).fetchone()
            if row:
                return row[0]
        # 2. Fallback prof/admin
        row = conn.execute(
            "SELECT uk.api_key FROM user_keys uk JOIN users u ON uk.user_id=u.id "
            "WHERE uk.provider='stitch' AND u.role IN ('admin','prof') "
            "ORDER BY u.role DESC LIMIT 1"
        ).fetchone()
        return row[0] if row else ""
    except:
        return ""
```
Passer `user_id` depuis la session dans tous les appels `_get_stitch_key()`.

---

**Problème 2 — Logs bavards qui exposent les clés** (ÉLEVÉ)

Dans `stitch_client.py` — supprimer ou masquer toute ligne loggant des données brutes de l'API :
```python
# Avant (à supprimer)
logger.info(f"Stitch get_screen FULL KEYS: {list(screen_data.keys())} ...")

# Remplacer par
logger.debug(f"Stitch get_screen keys count: {len(screen_data)}")
```
Règle générale : passer tous les logs `INFO` contenant des données de réponse API en `DEBUG`. Ne jamais logger de dict complet depuis une réponse externe.

---

**Problème 3 — Tokens HF stockés en clair + exposés dans les réponses API** (MOYEN)

**3a — Masquage dans les réponses :** créer un helper `mask_key(key: str) -> str` :
```python
def mask_key(key: str) -> str:
    if not key or len(key) < 8:
        return "****"
    return key[:4] + "****" + key[-4:]
# hf_hub_abcdef1234 → hf_h****1234
```
Utiliser dans toutes les routes qui retournent des settings utilisateur.

**3b — Champ password côté frontend :** dans `teacher_dashboard.html` ou la page settings, le champ de saisie du token HF doit être `type="password"`. Mission frontend séparée si Gemini doit intervenir — noter ici comme dette.

---

**Livrable QWEN :**
1. `_get_stitch_key(user_id)` avec résolution user-first dans `stitch_router.py`
2. Logs `stitch_client.py` nettoyés (DEBUG uniquement pour les données API)
3. `mask_key()` helper utilisé dans les routes settings/profil
4. Aucun autre fichier touché sauf `stitch_router.py` et `stitch_client.py`

**Fichiers à lire :**
- `Frontend/3. STENCILER/routers/stitch_router.py` — `_get_stitch_key()` + tous ses appels
- `Frontend/3. STENCILER/core/stitch_client.py` — lignes logger.info avec données API
- `Frontend/3. STENCILER/routers/auth_router.py` — pour comprendre comment `user_id` est résolu depuis la session

---

---

### Thème 28 — Workflow Stitch : prompt maître + tracking

---

---

### Mission 265 — DIAG : prompt maître bloqué — ne remonte pas dans le chatbot Stitch
**STATUS: 🔴 NON RÉSOLU | DATE: 2026-04-10 | ACTOR: QWEN**

**Symptôme :** Le méga-prompt est copié dans le clipboard mais **n'apparaît pas automatiquement dans le chatbox Stitch**. L'élève doit coller manuellement (Cmd+V).

**Contrainte :** Stitch est sur un domaine différent (`stitch.withgoogle.com`) — injection DOM impossible (cross-origin).

**Solutions possibles :**
1. **Background MCP** : `create_project` + `generate_screen_from_text` en arrière-plan → Stitch s'ouvre avec l'écran déjà généré (pas besoin de coller). Prend 2-3 min.
2. **Extension Stitch** : si Google expose une API URL pour pré-remplir le chat (à vérifier).
3. **Accepter le clipboard** : doc user, on considère le copier-coller comme le workflow normal.

---

---

### Thème 27 — Contexte actif dans FEE Studio et Stitch

---

---

### Thème 26 — Forge Pipeline : réparation Vision-to-Code

---

---

### Mission 263 — Canvas N0 : drag d'éléments dans un dist React compilé
**STATUS: 🟠 PRÊTE | DATE: 2026-04-08 | ACTOR: GEMINI**

**Contexte :** Le hover engine M237 (injecté dans l'iframe) détecte correctement les éléments du dist React via `mouseover`. Le drag ne fonctionne pas : déplacer un nœud DOM dans un bundle React compilé est impossible sans passer par le state React — le reconciler réécrit le DOM au prochain render.

**Approche :** ne pas déplacer l'élément React. À la place, créer un **calque SVG fantôme** sur le canvas au-dessus de l'iframe. Au `mousedown` sur un élément hover, capturer sa `getBoundingClientRect()`, créer un rectangle SVG fantôme aux mêmes dimensions et coordonnées canvas, le rendre draggable sur le canvas. L'iframe reste intacte.

**Ce que le drag fantôme permet :**
- Repositionner visuellement un élément sans toucher au React bundle
- Stocker la position finale dans le manifest (`element_overrides`) pour reconstruction future
- Sullivan peut lire ces overrides pour proposer une version HTML éditable

**Séquence technique :**

1. Dans `WsCanvas.js` — écouter `hm-select` depuis l'iframe :
```js
// Déjà présent : window.addEventListener('message', ...)
// Ajouter sur hm-select :
if (e.data.type === 'hm-select') {
    this._selectedIframeEl = e.data; // { tag, id, cls, rect }
}
```

2. Le hover engine injecté (dans `injectHoverEngine()`) doit envoyer le `rect` avec `hm-select` :
```js
document.addEventListener('mousedown', function(e) {
    const el = e.target;
    const rect = el.getBoundingClientRect();
    window.parent.postMessage({
        type: 'hm-select',
        tag: el.tagName, id: el.id || '', cls: (el.className||'').toString().slice(0,80),
        rect: { x: rect.left, y: rect.top, w: rect.width, h: rect.height }
    }, '*');
});
```

3. Dans `WsCanvas.js` — à réception de `hm-select` avec `rect`, créer le fantôme SVG :
```js
_createGhostElement(shellG, rect) {
    // Convertir les coordonnées iframe → canvas world
    const shellRect = shellG.querySelector('foreignObject').getBoundingClientRect();
    const scaleX = (shellRect.width / parseFloat(shellG.querySelector('foreignObject').getAttribute('width')));
    const wx = (shellRect.left - this.wrapper.getBoundingClientRect().left - this.viewX) / this.scale
               + rect.x / scaleX;
    const wy = (shellRect.top  - this.wrapper.getBoundingClientRect().top  - this.viewY) / this.scale
               + rect.y / scaleX;
    const ghost = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    ghost.setAttribute('x', wx); ghost.setAttribute('y', wy);
    ghost.setAttribute('width', rect.w / scaleX); ghost.setAttribute('height', rect.h / scaleX);
    ghost.setAttribute('fill', 'rgba(140,198,63,0.15)');
    ghost.setAttribute('stroke', '#8cc63f'); ghost.setAttribute('stroke-width', '1.5');
    ghost.setAttribute('rx', '4');
    ghost.classList.add('ws-ghost-element');
    ghost.dataset.sourceTag = this._selectedIframeEl?.tag || '';
    ghost.dataset.sourceId  = this._selectedIframeEl?.id  || '';
    this.content.appendChild(ghost);
    return ghost;
}
```

4. Rendre le fantôme draggable avec le même système `mousedown/mousemove/mouseup` que les shells.

5. Au `mouseup`, émettre un event `ws-element-placed` avec `{ sourceId, sourceCls, x, y, w, h }` — Sullivan pourra le lire pour proposer une refonte positionnée.

**Points d'attention :**
- Un seul fantôme actif à la fois — supprimer le précédent au prochain `hm-select`
- `pointer-events` de l'iframe : `auto` en mode `select` uniquement (déjà géré M238)
- Ne pas stocker les fantômes dans le manifest pour l'instant — juste l'affichage

**Fichiers :** `WsCanvas.js` (ghost + drag), `injectHoverEngine` dans `WsCanvas.js` (ajouter rect dans hm-select)

**Livrable :**
- Hover → outline vert (déjà OK)
- Mousedown → fantôme SVG vert semi-transparent sur le canvas
- Drag du fantôme → repositionnement fluide
- Mouseup → console `[WS-GHOST]` avec tag/id/position finale

---

---

### Mission 265 — Forge SVG/Figma : tokens HoméOS + SVG trop lourd
**STATUS: 🔴 PRIORITÉ | DATE: 2026-04-08 | ACTOR: QWEN**

**Fichier unique :** `Backend/Prod/retro_genome/svg_to_tailwind.py` — méthode `convert()` L72-135

**Symptôme :** Export Figma forgé → résultat identique au bug PNG (HoméOS). 62787 tokens, 78s.

---

**Fix 1 — Retirer les tokens HoméOS du prompt (L101-107)**

`color_hint` est déjà calculé L87 — l'utiliser à la place des tokens injectés :

```python
# Avant — remplacer le bloc "TOKENS DE DESIGN À RESPECTER (IMPÉRATIF)" par :
CONTRAINTE DESIGN :
- Extrais les couleurs dominantes directement depuis les valeurs `fill` du SVG.
- Couleurs détectées dans ce fichier (plus fréquentes) : {color_hint}
- Utilise ces couleurs — ne substitue pas tes propres préférences.
```

---

**Fix 2 — Réduire le SVG envoyé au LLM**

Cap actuel `clean_svg[:50000]` → ~60K tokens totaux → 78s. Deux actions dans `_strip_noise()` + cap :

```python
# Dans _strip_noise(), ajouter après les suppressions existantes :
# Supprimer les paths complexes (d= > 200 chars = bruit, pas d'info structurelle)
content = re.sub(r'<path\b[^>]*\bd="[^"]{200,}"[^/]*/>', '', content)
content = re.sub(r'<path\b[^>]*\bd="[^"]{200,}"[\s\S]*?/>', '', content)
```

Et dans `convert()`, abaisser le cap L99 :
```python
# Avant
{clean_svg[:50000]}
# Après
{clean_svg[:20000]}
```

---

**Livrable :** prompt sans tokens HoméOS, SVG < 20K chars, latence estimée < 30s. Aucun autre fichier.

---

---

### Mission 262 — Forge Vision : remettre le pipeline dans un état carré
**STATUS: 🔴 PRIORITÉ | DATE: 2026-04-08 | ACTOR: QWEN**

**Fichier unique :** `Backend/Prod/retro_genome/svg_to_tailwind.py`

**Fix 1 — Retirer les tokens HoméOS du fallback `convert_image()` — bloc `else` du `design_section` L164-172**
```python
# Avant
else:
    design_section = f"""
TOKENS DE DESIGN À RESPECTER (IMPÉRATIF) :
- Background principal : `{tokens['colors']['neutral']}`
...
"""
# Après
else:
    design_section = """
CONTRAINTE DESIGN : aucun design system prédéfini pour ce projet.
Extrais les couleurs, typographies et espacements directement depuis l'image.
Sois fidèle à ce que tu vois — ne substitue pas tes propres préférences.
"""
```

**Fix 2 — Restaurer le fallback MIMO Vision (supprimé par erreur)**
MIMO-V2-Omni supporte la Vision base64 OpenAI-compatible. Le remettre après `result = await self.client.generate_with_image(...)` :
```python
if not result.success:
    logger.warning("[SvgToTailwind] Gemini Vision failed, trying Mimo fallback...")
    try:
        from Backend.Prod.models.mimo_client import MimoClient
        mimo = MimoClient()
        result = await mimo.generate_with_image(
            prompt=prompt, image_base64=image_base64,
            mime_type=mime_type, max_tokens=16000, temperature=0.1
        )
    except Exception as e:
        logger.error(f"[SvgToTailwind] Mimo fallback vision failed: {e}")
if not result.success:
    logger.error(f"[SvgToTailwind] LLM Vision Error: {result.error}")
    raise RuntimeError(f"Vision conversion failed: {result.error}")
```

**Fix 3 — Vérifier `analyze_image_design()` (même fichier L221+)**
S'assurer que son prompt n'injecte pas de tokens HoméOS. Si oui, même correction que Fix 1.

**Livrable :** aucun autre fichier touché. Scope strict.

---

---

### Mission 258 — Hotfix : `_generate_with_image_genai` bloque l'event loop
**STATUS: 🔴 PRIORITÉ | DATE: 2026-04-08 | ACTOR: CODE DIRECT — FJD**

**Problème :** `client.models.generate_content(...)` du SDK google-genai est **synchrone**. Appelé directement dans une coroutine FastAPI, il bloque l'event loop — cause probable du `zsh: killed` observé en session.

**Fichier :** `Backend/Prod/models/gemini_client.py` — méthode `_generate_with_image_genai()` (L413).

**Fix :**
```python
import asyncio
import functools

async def _generate_with_image_genai(self, prompt, image_base64, mime_type, max_tokens, temperature):
    from google import genai
    import base64
    client = genai.Client(api_key=self.api_key)

    contents = [{"parts": [
        {"inline_data": {"mime_type": mime_type, "data": image_base64}},
        {"text": prompt},
    ]}]

    # Synchronous SDK → exécuté dans un thread pour ne pas bloquer l'event loop
    response = await asyncio.to_thread(
        functools.partial(
            client.models.generate_content,
            model=self.primary_model,
            contents=contents,
            config={"max_output_tokens": max_tokens, "temperature": temperature},
        )
    )
    return response.text
```

**Règle :** même fix à appliquer à `generate()` (text-only) si le SDK genai est utilisé dans ce chemin — vérifier.

---

---

### Mission 259 — dist.zip : badge "rendu compilé" dans le shell
**STATUS: 🟠 PRÊTE | DATE: 2026-04-08 | ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE

**Problème :** un dist.zip React forgé charge dans l'iframe comme un rendu fidèle, mais le hover engine ne peut pas inspecter les éléments (React Virtual DOM). L'élève croit que le mode select devrait fonctionner — pas de feedback visuel indiquant que ce shell est en lecture seule.

**Comportement attendu :**
- Le shell d'un dist.zip compilé affiche un badge discret `rendu compilé` dans son header, à droite du titre
- En mode `select`, un tooltip ou message dans la status bar indique `inspecter non disponible — rendu compilé`
- Le hover engine n'est pas injecté dans ces shells (guard dans `WsScreenShell.js`)

**Détection :** `item.origin === 'compiled'` dans l'index.json (déjà positionné par le pipeline ZIP, L734).

**Fichiers :**
- `WsScreenShell.js` — dans `build()`, si `item.origin === 'compiled'` : ajouter badge SVG + skip `injectHoverEngine`
- `WsCanvas.js` — dans `setMode('select')` : si le shell actif a `data-origin="compiled"`, afficher message dans `#ws-status-bar`

**Livrable :**
- Badge `rendu compilé` visible dans le header du shell
- Aucune tentative d'injection hover sur ces shells
- Message status bar en mode select

---

---

### Thème 18 — Diagnostics workspace généralisés (2026-04-08)

---

---

### Mission 239 — DIAG : Toolbar N0 — tous les boutons morts sauf Stitch
**STATUS: 🔴 DIAG EN ATTENTE**

**Symptôme** : Clic sur select (V), drag (H), frame (F), text (T), effects (E) → rien de visible. Seul le bouton Stitch (`<a>` brut) réagit.

---

**Hypothèse 1 — Les `onclick` des `.ws-tool-btn` ne sont jamais attachés**
Probabilité : TRÈS PROBABLE

`ws_main.js` est `type="module"` (workspace.html ligne 579). L'ensemble de l'init est dans un `DOMContentLoaded` async. Si une exception non catchée survient **avant la ligne 58** (setup toolbar), la promise avorte silencieusement. Le [S] de la screen list fonctionne car son onclick est attaché dans `fetchWorkspaceImports()` (ligne ~303), mais cette fonction est appelée à la ligne 52 — les onclicks toolbar sont attachés à la ligne 58, **après** le await. Si `fetchWorkspaceImports()` throw en dehors de son try/catch interne (ex: `list` null → `list.innerHTML` crash dans le catch), DOMContentLoaded avorte avant la ligne 58.

Test :
```js
document.querySelectorAll('.ws-tool-btn').length           // 0 → handlers jamais attachés
document.querySelector('.ws-tool-btn[data-mode="select"]').onclick  // null confirme
```

---

**Hypothèse 2 — Les `onclick` sont attachés mais `window.wsCanvas` est null**
Probabilité : PROBABLE

Si `new WsCanvas(...)` (ligne 11) throw ou retourne un objet incomplet, `window.wsCanvas` est null. Tous les appels `window.wsCanvas?.setMode(mode)` sont des no-ops silencieux.

Test :
```js
window.wsCanvas         // null ?
window.wsCanvas?.activeMode   // undefined ?
```

---

**Hypothèse 3 — Les `onclick` sont attachés et setMode tourne, mais le feedback visuel est invisible**
Probabilité : MOYENNE

`setMode()` ajoute/retire la classe `.active-tool` sur les boutons. Si `.active-tool` n'a aucune règle CSS visible (background, couleur, border), le bouton paraît mort alors qu'il fonctionne. De plus, les modes "frame", "effects", "colors" ne déclenchent aucune ouverture de panneau dans `ws_main.js` — ils changent juste `activeMode` en silence.

Test :
```js
document.querySelector('.ws-tool-btn[data-mode="select"]').classList.contains('active-tool') // avant clic
// Cliquer "drag"
document.querySelector('.ws-tool-btn[data-mode="drag"]').classList.contains('active-tool')    // → true si setMode tourne
```

---

---

### Mission 240 — DIAG : Bouton Aperçu dans le shell — mort
**STATUS: 🔴 DIAG EN ATTENTE**

**Symptôme** : Clic sur "Aperçu" dans un shell canvas → rien ne s'ouvre.

---

**Hypothèse 1 — `window.wsPreview` est undefined**
Probabilité : TRÈS PROBABLE

Si ws_main.js crashe avant ou à la ligne 9 (`window.wsPreview = new WsPreview()`), `window.wsPreview` est undefined. L'appel `window.wsPreview?.enterPreviewMode(...)` dans le clic du shell est un no-op silencieux.

Test :
```js
window.wsPreview                // undefined ?
typeof window.wsPreview         // "undefined" ?
```

---

**Hypothèse 3 — Le shell id passé ne correspond à aucun élément**
Probabilité : FAIBLE

Le bouton passe `g.id` à `enterPreviewMode`. Si `g.id` est vide ou mal formé, `document.getElementById(id)` retourne null → retour silencieux ligne 76.

Test :
```js
document.querySelector('.ws-screen-shell')?.id  // vide ou undefined ?
```

---

---

### Mission 241 — DIAG : Bouton [S] apparaît sur les imports dist.zip
**STATUS: 🔴 DIAG EN ATTENTE**

**Symptôme** : Un import dist.zip affiche un bouton [S] dans la screen list. Clic → `GET /api/stitch/open/2026-04-08_142326_dist.zip` → 400.

---

**Hypothèse 1 — L'entrée index.json a un `archetype_id` hérité d'une ancienne version du code**
Probabilité : TRÈS PROBABLE

La condition `isStitch` dans `fetchWorkspaceImports()` évalue `item.archetype_id === 'stitch_import'`. Si une version précédente du code a créé des entrées avec un archetype_id différent, le check est correct **pour les nouvelles entrées** mais les anciennes dans index.json ont peut-être une valeur aberrante qui passe le test. Ou pire : une régression a enlevé la condition et tout affiche [S].

Test :
```js
fetch('/api/retro-genome/imports').then(r=>r.json()).then(d=>console.log(JSON.stringify(d.imports.map(i=>({id:i.id,archetype_id:i.archetype_id,archetype_label:i.archetype_label})),null,2)))
```

---

**Hypothèse 2 — Le fichier ws_main.js servi est une version cachée sans la condition**
Probabilité : PROBABLE

Les agents ont peut-être appliqué le fix dans le mauvais fichier, ou le serveur sert une version antérieure. Le browser peut avoir en cache une version de ws_main.js sans la condition `isStitch`.

Test : Ouvrir DevTools → Sources → `ws_main.js` → chercher "isStitch". Si absent → version ancienne en cache.
Fix : Cmd+Shift+R (hard refresh).

---

**Hypothèse 3 — La condition est présente mais évalue `true` pour les zips car `archetype_label` contient "stitch" par accident**
Probabilité : FAIBLE

La condition est `item.archetype_label.toLowerCase().includes('stitch')`. Si l'archetype_label d'un zip est "import multi-format" (normal), il ne contient pas "stitch". Mais si un agent a changé le label dans import_router.py, le check peut être faussé.

Test : vérifier dans import_router.py l'`archetype_label` assigné aux uploads ZIP.

---

---

### Mission 242 — DIAG : FEE Studio — "veuillez activer un projet"
**STATUS: 🔴 DIAG EN ATTENTE**

**Symptôme** : Ouverture FEE Studio → `alert("veuillez activer un projet")` même quand un projet est chargé.

---

**Hypothèse 1 — `window.wsBackend` non instancié → `projectId` undefined**
Probabilité : TRÈS PROBABLE

`ws_main.js` n'instancie jamais `window.wsBackend = new WsBackend()`. `WsFEEStudio.open()` résout `this.ws = window.wsBackend || window.wsCanvas || {}`. Si `wsBackend` est undefined et `wsCanvas` n'a pas de propriété `activeProject`, `projectId` = undefined → alert.

Test :
```js
window.wsBackend                    // undefined ?
window.wsCanvas?.activeProject      // undefined ?
JSON.parse(localStorage.getItem('homeos_session') || '{}')  // a-t-il active_project_id ?
```

---

**Hypothèse 2 — La session localStorage n'a pas de clé `active_project_id`**
Probabilité : PROBABLE

Même si M240 a patché `WsFEEStudio.open()` pour lire depuis `localStorage.homeos_session`, si la session stockée n'a pas de clé `active_project_id` ou `project_id`, le fallback échoue quand même.

Test :
```js
JSON.parse(localStorage.getItem('homeos_session') || '{}')
// Chercher : active_project_id, project_id, token
```

---

**Hypothèse 3 — Le patch M240 n'a pas été appliqué (version ancienne de WsFEEStudio.js servie)**
Probabilité : MOYENNE

Le serveur sert peut-être une version de `WsFEEStudio.js` antérieure au patch. Vérifier dans Sources DevTools que `WsFEEStudio.open()` lit bien `localStorage.homeos_session`.

Test : DevTools → Sources → `WsFEEStudio.js` → chercher "homeos_session". Absent → version antérieure au patch.

---

**Bug 1 — Hover outline ne touche que le body**

Le moteur injecté utilise `mouseover` qui bubble — `e.target` est correct mais le React dist enveloppe tout dans des divs avec héritage de `pointer-events`. Fix : cibler `e.target` direct ET exclure les conteneurs racine connus (`#root`, `[data-reactroot]`).

Dans le script injecté (dans `WsCanvas.injectHoverEngine`), remplacer la condition d'exclusion :
```js
// Avant
if (el === document.body || el === document.documentElement) return;
// Après
if (el === document.body || el === document.documentElement || el.id === 'root') return;
// Et forcer pointer-events sur tout le document
document.documentElement.style.setProperty('pointer-events', 'all', 'important');
```

---

**Bug 2 — Drag shell cassé en mode select (iframe mange les events)**

Gemini a mis `pointer-events: auto` sur les iframes en mode select → le SVG canvas ne reçoit plus les mousedown quand on drag au-dessus de l'iframe.

Fix dans `WsCanvas.setMode()` : ne jamais passer les iframes en `auto`. À la place, activer le moteur hover via un flag sur le canvas, et garder les iframes en `pointer-events: none` **toujours**. Le moteur hover fonctionne car il est injecté dans le document de l'iframe — il n'a pas besoin que l'iframe reçoive les events de la page parente.

```js
setMode(mode) {
    this.activeMode = mode;
    // NE PAS toucher pointer-events des iframes — le moteur hover est inside l'iframe
    // Les iframes restent pointer-events: none pour que le canvas drag fonctionne
    // ... reste du setMode
}
```

Retirer tout le bloc `document.querySelectorAll('.ws-screen-shell iframe').forEach(...)` que Gemini a ajouté dans `setMode`.

---

**Bug 3 — Bouton Stitch disparu**

Deux endroits à restaurer :

*3a — Dans la toolbar (`workspace.html`)*, remettre le bouton Stitch entre typo et séparateur zoom, avec un `href` vers Stitch (pas de panel dédié) :
```html
<!-- STITCH (lien direct) -->
<a href="https://stitch.withgoogle.com" target="_blank"
   class="p-3 rounded-xl text-slate-400 hover:text-indigo-500 transition-all"
   title="Ouvrir Stitch">
    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/>
    </svg>
</a>
```

*3b — Dans `ws_main.js` `fetchWorkspaceImports()`*, le bouton [S] par item était conditionnel sur `stitch_screen_id`. Gemini l'a supprimé entièrement. Le remettre dans le template HTML des items de liste :
```js
${item.stitch_screen_id ? `
<button class="btn-s-open p-1.5 hover:bg-slate-50 text-slate-400 hover:text-indigo-500 rounded transition-all" title="Ouvrir dans Stitch">
    <span class="text-[9px] font-black font-sans">S</span>
</button>` : ''}
```
Et remettre le listener correspondant :
```js
const btnOpen = el.querySelector('.btn-s-open');
if (btnOpen) btnOpen.onclick = async (e) => {
    e.stopPropagation();
    const res = await fetch(`/api/stitch/open/${item.id}`);
    const d = await res.json();
    if (d.url) window.open(d.url);
};
```

---

**Bug 4 — Impossible de remettre un item sur le canvas une seconde fois**

`addScreen(item)` dans `WsCanvas.js` :
```js
if (document.getElementById(`shell-${item.id}`)) {
    this.selectScreen(document.getElementById(`shell-${item.id}`));
    return; // ← si le shell a été fermé et retiré du DOM, getElementById retourne null
}
```
La logique est correcte — si `getElementById` retourne `null`, il tombe dans `WsScreenShell.build`. Le bug vient sûrement d'une régression Gemini dans `WsScreenShell.build` ou dans la façon dont le shell est retiré du DOM.

Vérifier dans `WsScreenShell.js` le close button :
```js
closeBtn.addEventListener('mousedown', (e) => { e.stopPropagation(); g.remove(); });
```
Si `g.remove()` retire bien le `<g>` du SVG, `getElementById` retourne null au prochain appel → reconstruit. Tester dans la console : `document.getElementById('shell-XXX')` après fermeture. Si null → le bug est ailleurs (peut-être `addScreen` ne reconstruit pas si `WsScreenShell` est undefined).

Ajouter un log défensif dans `addScreen` :
```js
async addScreen(item) {
    const existing = document.getElementById(`shell-${item.id}`);
    if (existing) { this.selectScreen(existing); return; }
    if (!window.WsScreenShell) { console.error('WsScreenShell not loaded'); return; }
    const g = await window.WsScreenShell.build(item, this);
    this.content.appendChild(g);
    this.selectScreen(g);
    return g;
}
```

---

> BOOTSTRAP OBLIGATOIRE

**Contexte :** Deux comportements attendus en mode `select` (flèche). Architecture choisie : moteur hover **injecté dans le contentDocument** de l'iframe au chargement — zéro coordinate math côté canvas, le highlight est rendu à l'intérieur de l'iframe par son propre DOM.

---

**Comportement 1 — Zone de drag du shell (codée mais invisible)**

`WsCanvas.js` ligne 124 : drag déjà restreint à `worldY <= 40`. Manque le visuel.

Dans `WsScreenShell.js`, ajouter après le `<rect class="ws-screen-header">` :
```js
// Cursor move sur le header
header.style.cursor = 'move';

// Gripper visuel centré
const grip = this._createElement('text', {
    x: String(SW / 2), y: '26', 'text-anchor': 'middle',
    fill: '#d1d5db',
    style: 'font-size:11px; letter-spacing:5px; pointer-events:none; user-select:none;'
});
grip.textContent = '⋯';
g.appendChild(grip);
```

---

---

### Mission 235 — Toolbar canvas : refonte UX
**STATUS: 🔴 PRIORITÉ | DATE: 2026-04-08 | ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE

**Contexte :** Audit FJD de la toolbar droite flottante (`data-purpose="floating-toolbar"` dans `workspace.html`). Plusieurs outils inutiles, illisibles, ou mal placés.

**Décisions FJD :**

| Outil actuel | Action |
|---|---

---

### Mission 182-A — Wire : organes du manifest dans le tableau
**STATUS: 🟠 PRÊTE**
**DATE: 2026-04-06 | ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE

Diagnostic console d'abord :
```js
fetch('/api/projects/active/wire-audit').then(r=>r.json()).then(d=>console.log('audit:', d.audit?.length, d.audit))
```
- `audit.length === 6` → modifier `WsWire.js _renderBilan()`
- `audit.length === 0` → modifier route `wire-audit` dans `server_v3.py`

**Livrable :** tableau Wire affiche 6 lignes d'organes.

---

---

### Mission 182-B — Wire : bouton "activer le plan"
**STATUS: 🔵 EN ATTENTE 182-A | ACTOR: GEMINI**

Cliquer `#ws-wire-apply-plan` → champ chat se remplit → Sullivan répond. Inspecter `WsWire.js` autour de `btnApplyPlan.onclick`.

---

---

### Mission 180 — Rebranchement WiRE dans cadrage_alt
**STATUS: 🔴 PRIORITÉ**
**DATE: 2026-04-05 | ACTOR: GEMINI**

- [ ] Shell `#ws-wire-overlay` dans `cadrage_alt.html`
- [ ] Chargement `WsWire.js` + `WsInspect.js`
- [ ] Déclenchement diagnostic z-index au clic `.wire`

---

---

### Mission 149 — Canvas N0 : États de sélection + toolbar
**STATUS: 🟠 PRÊTE | DATE: 2026-04-02**
- [ ] États CSS (hover, selected, dragging)
- [ ] WsCanvas.js : notifyToolbar, cursor

---

---

### Mission 150 — Retour Cadrage : session pré-alimentée
**STATUS: 🟠 PRÊTE | DATE: 2026-04-02**
- [ ] Route `POST /api/cadrage/init-context`
- [ ] Badge "contexte wire chargé" dans Cadrage UI

---

---

### Mission 153 — Undo Sullivan
**STATUS: 🔵 EN COURS — GEMINI | DATE: 2026-04-03**
- [ ] WsCanvas.js : snapshot avant update
- [ ] Bouton Undo dans le header workspace

---

---

### Mission 155 — Bouton Stop Sullivan
**STATUS: 🟠 PRÊTE | DATE: 2026-04-03**
- [ ] WsChat.js : AbortController + bouton Stop UI

---

---

### Mission 170 — BEHAVIOR_SULLIVAN.md
**STATUS: 🟠 PRÊTE**
**DATE: 2026-04-06 | ACTOR: FJD + CLAUDE**
**Dépendance : M167**

- [ ] `Frontend/1. CONSTITUTION/BEHAVIOR_SULLIVAN.md` : Identité, Modes, Manifest, Règles, Format, Interdits
- [ ] Brancher dans `server_v3.py` → injecté dans `base_system` de chaque mode

---

---

### M225 — Cadrage : panneau "contexte projet" visible dans l'UI
**STATUS: 🟠 PRÊTE | DATE: 2026-04-07 | ACTOR: GEMINI**

> Dépend de M226 (backend). Frontend uniquement.

> BOOTSTRAP OBLIGATOIRE

Panneau rétractable dans `cadrage_alt.html` affichant ce que Sullivan voit :
- Titre du projet, ID Stitch, nb écrans, dernier PRD (lien), design system actif
- Bouton "recharger" → re-fetch `GET /api/projects/active` + manifest
- Collapsed par défaut, expand au clic sur "contexte projet ▸"
- Position : colonne de droite sous le panneau compétences (mode prof) ou en haut à droite (mode élève)

**Fichiers à lire :**
- `Frontend/3. STENCILER/static/templates/cadrage_alt.html`
- `Frontend/3. STENCILER/routers/cadrage_router.py`

**Contexte :**
Un élève arrive en Cadrage avec un projet déjà structuré (manifest Stitch : écrans, atoms, intentions).
Sullivan ne voit rien de tout ça — il répond dans le vide.
Il faut : (1) passer `project_id` au SSE, (2) lire le manifest et l'injecter dans le system prompt, (3) l'afficher dans l'UI.

**Backend — `cadrage_router.py` + `brainstorm_logic.py` (ACTOR: QWEN) :**

1. `cadrage_router.py` — ajouter `project_id` au SSE endpoint :
```python
@router.get("/api/cadrage/chat/{provider}")
async def cadrage_chat_sse(provider: str, session_id: str = Query(...), message: str = Query(...), class_id: str = Query(None), project_id: str = Query(None)):
    async def generate():
        async for chunk in cadrage_logic.sse_chat_generator(session_id, provider, message, class_id=class_id, project_id=project_id):
            yield chunk
```

2. `brainstorm_logic.py` — ajouter helper `_load_project_manifest(project_id)` :
```python
def _load_project_manifest(project_id: str) -> str:
    """Lit projects/{project_id}/manifest.json → retourne texte formaté pour le prompt."""
    try:
        projects_dir = Path(__file__).parent.parent.parent.parent / "projects"
        manifest_path = projects_dir / project_id / "manifest.json"
        if not manifest_path.exists():
            return ""
        data = json.loads(manifest_path.read_text(encoding='utf-8'))
        # Résumer : titre, écrans, atoms clés
        lines = []
        if data.get("name"): lines.append(f"Projet : {data['name']}")
        if data.get("stitch_project_id"): lines.append(f"Stitch ID : {data['stitch_project_id']}")
        screens = data.get("screens", [])
        if screens: lines.append(f"Écrans : {', '.join(s.get('name','?') for s in screens)}")
        return "\n".join(lines)
    except Exception as e:
        logger.warning(f"_load_project_manifest error: {e}")
        return ""
```

3. Dans `sse_chat_generator()` — si `project_id` présent, enrichir `system_prompt` :
```python
if project_id:
    manifest_ctx = _load_project_manifest(project_id)
    if manifest_ctx:
        system_prompt += f"\n\nCONTEXTE PROJET ÉLÈVE :\n{manifest_ctx}"
```

**Frontend — `cadrage_alt.html` (ACTOR: GEMINI) :**

> BOOTSTRAP OBLIGATOIRE

1. Au chargement, lire `localStorage.homeos_session.project_id`
2. Si présent → `GET /api/projects/{project_id}/manifest` (ou lire depuis `/api/projects/active`) → afficher dans un panneau rétractable à droite intitulé "contexte projet" :
   - Titre du projet, liste des écrans Stitch, compétences DNMADE si présentes
   - Bouton "recharger" → re-fetch le manifest (utile si l'élève a importé de nouveaux écrans)
   - Panneau collapsed par défaut, expand au clic
3. Ajouter `&project_id={project_id}` à l'URL SSE dans `startStreaming()`

**Fichiers à lire :**
- `Frontend/3. STENCILER/routers/cadrage_router.py`
- `Backend/Prod/retro_genome/brainstorm_logic.py` — `sse_chat_generator()`, helpers M220
- `Frontend/3. STENCILER/static/templates/cadrage_alt.html` — `startStreaming()`, panneau Sullivan

**Livrable :**
1. Élève ouvre `/cadrage` avec `project_id` en session → Sullivan voit le manifest dans son contexte
2. Panneau "contexte projet" visible et rétractable dans l'UI
3. Bouton "recharger" met à jour sans rechargement de page

---

**A. Supprimer le panel Audit UX**

Dans `workspace.html`, supprimer entièrement :
- `<div id="section-audit">` et son contenu
- `<button id="badge-audit">` et son contenu
- Tout CSS lié à `.panel-audit`, `#panel-audit`, `#badge-audit` dans `workspace.css`

---

**B. Remplacer `#panel-screens` par un dashboard projet**

Nouveau contenu de `#ws-import-list` (rendu par `fetchWorkspaceImports()`) :

```
┌─────────────────────────────────┐
│  ▸ mon projet                   │  ← collapse (ouvert par défaut)
│    [nom du projet depuis manifest]
│    ┌ Stitch ──────────────────┐  │  ← sous-collapse fermé par défaut
│    │ ID Stitch : [___________] │  │
│    │ [lier →]                  │  │
│    └───────────────────────────┘  │
│                                   │
│    mes écrans                     │
│    ┌───────────────────────────┐  │
│    │ nom-écran.html        [S] [↻] [×] │
│    │ nom-écran-2.html      [S] [↻] [×] │
│    │ ...                       │  │
│    └───────────────────────────┘  │
│    (message si vide)              │
└─────────────────────────────────┘
```

**Comportement :**
- Clic sur le nom d'écran → `window.wsCanvas?.addScreen({...})`
- Bouton `[S]` (logo Stitch SVG, alt "ouvrir dans Stitch") → `fetch('/api/stitch/open/{screen_id}').then(d => window.open(d.url))`
- Bouton `[↻]` → `POST /api/stitch/sync` puis recharger la liste
- Bouton `[×]` → confirmation puis suppression de l'import local

**Sous-collapse Stitch ID :**
- Input texte + bouton "lier" → `POST /api/stitch/pull` avec le project_id saisi → mémorise dans manifest
- Affiché seulement si `stitch_project_id` absent du manifest

---

**D. Corrections de scope (notes de clarification FJD 2026-04-08)**

- **Sullivan** : panneau en bas du workspace, pas à droite — il demeure
- **Wire** : demeure dans le workspace comme outil/mode
- **Disparaissent** : bouton KIMI (stratégie différente à venir), boutons hover/scroll/click/liste (pris en charge par FEE)
- **Export** : aperçu localhost uniquement pour l'instant — pas de bouton forge/export dans ce scope
- **DESIGN.md** : n'est PAS un document HoméOS exclusif. C'est le design du projet de l'élève = tokens Stitch + règles nécessaires à HoméOS pour jouer sa partie. Stitch = source de vérité design. À chaque pull Design DNA → **toujours mettre à jour** `DESIGN.md` sections `Colors`, `Typography`, `Spacing`. Ne jamais écraser les sections spécifiques HoméOS (ex: `## Wire Rules`, `## Interaction Tokens`) — merge sectionnel.

**D. Règle DESIGN.md merge (backend — dans `stitch_router.py` au pull)**

Structure DESIGN.md d'un projet élève :
```markdown
# DESIGN.md — {project_name}
> Source: Stitch Design DNA + règles HoméOS

## Colors          ← Stitch écrit ici (màj à chaque pull)
## Typography      ← Stitch écrit ici
## Spacing         ← Stitch écrit ici
## Wire Rules      ← HoméOS écrit ici (ne pas écraser)
## Interaction     ← FEE écrit ici (ne pas écraser)
```

Merge : parser les sections `##`, remplacer Stitch (Colors/Typography/Spacing), préserver le reste.

**Livrable :**
1. Panel audit UX supprimé
2. Panel gauche = dashboard projet avec collapse + sous-collapse Stitch ID + liste écrans (3 actions par écran)
3. Toolbar droite = 5 outils max (select, drag, typo, couleur, Stitch)
4. Sullivan panneau bas et Wire préservés — KIMI et boutons interaction supprimés
5. Aucune régression canvas

---

**ACTOR GEMINI — Frontend (absorbe M228) :**

> BOOTSTRAP OBLIGATOIRE

Fichiers à lire : `workspace.html` panel `#panel-stitch`, `WsStitch.js`

**Panel Stitch — réorganiser `#stitch-content` :**
```
[titre projet]          [↻ synchroniser tout]
─────────────────────────────────────────────
liste écrans :
  Nom écran
  [👁 HoméOS]  [S Stitch]  [↻ pull]
─────────────────────────────────────────────
[modifier dans Stitch →]   ← push Sullivan
```
ID projet : lecture seule si lié, éditable si non lié.

**`WsStitch.js` — polling + focus :**
```js
// Dans show() après loadSession()
if (this.isLinked) {
    this._pollTimer = setInterval(() => this.sync(), 5 * 60 * 1000);
    window.addEventListener('focus', () => { if (this.isOpen) this.sync(); });
}

sync() { fetch('/api/stitch/sync', { method: 'POST' }).then(() => this.loadSession()); }
```

**Toolbar canvas — bouton "modifier dans Stitch"** dans `workspace.html` (barre d'outils droite).

Garder tous les IDs existants.

**Livrable :**
1. Premier push → `stitch_project_id` mémorisé → onglet Stitch ouvert
2. Panel : liste écrans avec 3 actions chacun
3. Sync auto focus + polling 5min + bouton
4. Bouton toolbar "modifier dans Stitch"

---

> BOOTSTRAP OBLIGATOIRE

**Contexte :** Stitch est l'outil central pour les élèves DNMADE — ils collent l'ID de leur projet Figma/Stitch, importent leurs écrans, et c'est leur matière première pour la Forge. L'UX actuelle est illisible.

**Fichiers à lire :**
- `Frontend/3. STENCILER/static/templates/workspace.html` — `id="panel-stitch"` et `id="ws-stitch-manual-form"`
- `Frontend/3. STENCILER/static/js/workspace/WsStitch.js`

**Réorganiser le contenu de `#stitch-content` en 3 sections lisibles :**

```
┌─────────────────────────┐
│  stitch            [×]  │
│  statut : ● connecté    │
├─────────────────────────┤
│  1. coller l'id stitch  │
│  [_________________]    │
│  [valider →]            │
├─────────────────────────┤
│  2. mes écrans          │
│  (liste auto après pull)│
│  [importer les écrans →]│
├─────────────────────────┤
│  3. générer via texte   │
│  [__intention_________] │
│  [générer →]            │
└─────────────────────────┘
```

**Règles :**
- Garder TOUS les `id` existants (`ws-stitch-project-id`, `ws-stitch-btn-list`, `ws-stitch-btn-pull`, `ws-stitch-screens-list`, `ws-stitch-intent`, `ws-stitch-btn-push`)
- Supprimer `display:none` sur `#ws-stitch-manual-form` — toujours visible
- Labels : minuscules, français, sans jargon
- Tokens HoméOS. Pas d'emojis.

---

> BOOTSTRAP OBLIGATOIRE

**Symptômes :**
1. Le bas du panel Stitch est coupé — `max-h-[60vh]` trop restrictif quand le panel est positionné
2. L'interface est incompréhensible pour un élève

**Fichiers à lire :**
- `Frontend/3. STENCILER/static/templates/workspace.html` — `id="panel-stitch"` (L253-315)
- `Frontend/3. STENCILER/static/js/workspace/WsStitch.js`
- `Frontend/3. STENCILER/static/css/workspace.css` — `.stitch-expanded`

**Fix 1 — Overflow**
Dans `workspace.html`, `id="stitch-content"` :
- Remplacer `max-h-[60vh]` par `overflow-y-auto` sans max-height fixe
- Le panel `#panel-stitch` doit avoir `max-height: calc(100vh - 96px); overflow-y: auto;` en inline style ou via workspace.css

**Fix 2 — UX simplifiée (scope strict)**
Réorganiser le contenu de `#stitch-content` en 3 blocs clairs, dans cet ordre :

```
┌─────────────────────────────┐
│  STITCH                [×]  │
├─────────────────────────────┤
│  statut : connecté / off    │
│  projet : [titre]           │
├─────────────────────────────┤
│  mes écrans                 │  ← liste des screens importés
│  [+ importer un écran]      │  ← bouton ouvre le formulaire manuel (replié par défaut)
├─────────────────────────────┤
│  générer via intention      │  ← textarea + bouton "générer"
└─────────────────────────────┘
```

- Formulaire manuel (`#ws-stitch-manual-form`) : replié par défaut, s'ouvre au clic sur "+ importer un écran"
- Labels en français, minuscules, sans jargon
- Supprimer le bouton "Lister les écrans" (remplacé par le chargement auto à l'ouverture)
- Garder les IDs existants des éléments (WsStitch.js s'y accroche)

**Style :** tokens HoméOS. Pas d'emojis. Pas de majuscules labels.

**Livrable :**
1. Panel scrollable — le bas est visible
2. Un élève comprend en 3 secondes ce qu'il peut faire

---

## Thème 23 — Typo globale

---

### M229 — Audit et suppression de "Source Code Pro" sur les boutons
**STATUS: 🟠 MISSION QWEN | DATE: 2026-04-07 | ACTOR: QWEN**

**Symptôme :** Les boutons dans les pages `cadrage_alt.html` et `workspace.html` (et potentiellement d'autres) s'affichent en police monospace Source Code Pro au lieu de la police sans-serif attendue.

**Mission :**

1. Chercher dans tous les fichiers HTML et CSS du dossier `Frontend/3. STENCILER/static/` toutes les occurrences de :
   - `Source Code Pro`
   - `font-mono` (classe Tailwind → mappe vers monospace)
   - `font-family.*mono`
   - `'monospace'` ou `"monospace"` utilisé hors contexte de pre/code/kbd

2. Pour chaque occurrence :
   - Si c'est sur un élément **`<button>`**, `<input>`, `<select>`, `<label>`, `<span>` de contenu textuel UI → **remplacer par `font-family: inherit`** (ou supprimer la règle font si le parent l'hérite déjà)
   - Si c'est sur `<pre>`, `<code>`, `<kbd>`, `.terminal-log`, `.sd-input` (champ clé API) → **laisser tel quel** (monospace légitime)
   - Si c'est dans la config Tailwind (`mono: ['"Source Code Pro"'...]`) dans `cadrage_alt.html` → **remplacer `'Source Code Pro'` par `'Geist Mono', ui-monospace, monospace`**

3. Dans `cadrage_alt.html` — vérifier que les boutons "Envoyer", "Sullivan Arbitrage", "Générer PRD" ont bien `font-family` hérité de la `body` (`'Source Sans 3'`). Si un bouton a explicitement `font-mono` → retirer la classe.

4. Dans `workspace.html` — idem. Vérifier que les spans `font-mono` sont uniquement sur des éléments de code/tag display (`#ws-popover-tag`, `#ws-wire-import-label`) et PAS sur des boutons.

**Fichiers à auditer :**
- `Frontend/3. STENCILER/static/templates/cadrage_alt.html`
- `Frontend/3. STENCILER/static/templates/workspace.html`
- `Frontend/3. STENCILER/static/css/homeos-nav.css`
- `Frontend/3. STENCILER/static/css/stenciler.css`
- `Frontend/3. STENCILER/static/css/workspace.css`

**Règle :** ne pas toucher aux `.sd-input`, `.terminal-log`, `pre`, `code`, `kbd`. Ne changer que les éléments UI (boutons, labels, spans de texte courant).

**Livrable :** liste des occurrences trouvées + modifications appliquées.

---

---

### F2 — Projet élève : création automatique depuis le sujet actif de la classe
**STATUS: 🟠 PRÊTE | DATE: 2026-04-07 | ACTOR: QWEN**

**Contexte :**
Hugo se connecte → son projet `dnamde3-dumont-hugo` existe dans `PROJECTS_DIR` et `students.project_id` est renseigné, MAIS il n'est pas enregistré dans la table `projects` → `get_active_project_path()` cherche dans `projects` → ne trouve rien → fallback `default` → workspace plein de templates.

**Règle métier :**
Si l'élève n'a pas de projet OU si son projet n'est pas dans la table `projects` :
1. Charger le dernier sujet de la classe (`classes/{class_id}/subjects/*.json` → le plus récent)
2. Nommer le projet d'après le titre du sujet (slugifié) : `contraintes-peruquiennes`
3. Créer le dossier `projects/{class_id}-{student_id}-{sujet_slug}/`
4. Écrire `manifest.json` avec `name: titre_sujet`, `class_id`, `student_id`, `subject_id`
5. **Enregistrer dans la table `projects`** : `INSERT OR IGNORE INTO projects (id, name, path, user_id)`
6. Mettre à jour `students.project_id`
7. Écrire `active_project.json`

**Modifier `create_student_project()` dans `class_router.py` :**
```python
def create_student_project(student, class_id) -> str:
    # Chercher le sujet actif
    subject_dir = CLASSES_DIR / class_id / "subjects"
    subject_title = None
    subject_slug = None
    if subject_dir.exists():
        subjects = sorted(subject_dir.glob("*.json"))
        if subjects:
            data = json.loads(subjects[-1].read_text(encoding='utf-8'))
            subject_title = data.get("title", "")
            subject_slug = slugify(subject_title) if subject_title else None

    project_id = f"{class_id}-{student['id']}" + (f"-{subject_slug}" if subject_slug else "")
    project_path = PROJECTS_DIR / project_id
    project_path.mkdir(parents=True, exist_ok=True)

    manifest = {
        "name": subject_title or f"Projet {student['display']}",
        ...
    }
    # Enregistrer dans table projects
    with bkd_db_con() as con:
        con.execute(
            "INSERT OR IGNORE INTO projects (id, name, path) VALUES (?, ?, ?)",
            (project_id, manifest["name"], str(project_path))
        )
```

**Aussi : route `POST /api/classes/{class_id}/students/{student_id}/start`** — appeler `create_student_project` + activer + retourner `project_id`. Cette route est appelée depuis `login.html` quand `project_id` est null.

**Fichiers à lire :**
- `Frontend/3. STENCILER/routers/class_router.py` — `create_student_project()`, L127-152
- `Frontend/3. STENCILER/bkd_service.py` — `bkd_db_con`, schéma table `projects`

**Livrable :**
1. Hugo se connecte → projet créé/enregistré → workspace vide (son espace propre)
2. Nom du projet = titre du sujet actif de la classe
3. Plus jamais de fallback sur `default` pour un élève

---

## Backlog

---

### Mission 140 — DPL : Instancier le repo GitHub dans HoméOS
**STATUS: 🔵 BACKLOG**
- [ ] Création/Liaison automatique d'un repo GitHub par projet pour le déploiement continu.

---

### Mission 115 — Bouton "éditer" global
**STATUS: 🔴 HOTFIX**

---

### Mission 111-A/B — Multi-project isolation + UI
**STATUS: 🔵 BACKLOG**

---

### Mission 112 — Sullivan Welcome Screen
**STATUS: 🔵 BACKLOG**

---

### Mission 113 — Sullivan Tips + Smart Nudges
**STATUS: 🔵 BACKLOG**

---

### Mission 114 — FRD Canvas v2 : snap + zoom + resize
**STATUS: 🔵 BACKLOG**

---

### Mission 118 — Pont SVG Illustrator → Tailwind
**STATUS: 🔵 BACKLOG**

---

### Mission 120 — Plugin Figma → FRD Editor
**STATUS: 🔵 BACKLOG**

---

### Mission 135-139 — Auth, Multi-tenancy, BYOK, Upload, Wire v2
**STATUS: 🔵 BACKLOG**

---

---

### Mission 259 — dist.zip : mode preview statique sans React bundle
**STATUS: 🔵 BACKLOG | ACTOR: QWEN | DATE: 2026-04-08**

**CR — Diagnostic final :**
- Les bundles React dans iframes ne sont JAMAIS draggables — leurs event listeners capturent tous les événements avant que le navigateur ne les transmette
- `elementsFromPoint()` fonctionne pour sélectionner l'élément dans l'arbre React mais le `transform: translate()` appliqué n'a aucun effet visuel car React contrôle le rendu via son virtual DOM
- **Décision :** dist.zip = mode preview seule. Pour modifier le contenu, utiliser le pipeline PNG (M256) sur un screenshot du dist.zip

---

---

### CR Session 8 avril 2026 — M257/M258/M259

**M257 — genai SDK pour Gemini 3.x :**
- Tous les modèles Gemini Vision retournaient 404 via REST API `v1beta` — Google a déprécié les anciens noms
- SDK `google-genai` v1.70.0 installé pour Python 3.14 — testé et OK avec `gemini-3.1-flash-lite-preview`
- `generate_with_image()` route automatiquement : modèles "preview" → genai SDK, modèles stables → REST API
- Pipeline PNG corrigé : A (analyse design) → B (save DESIGN.md) → C (forge avec DESIGN.md injecté)
- **⚠️ Non testé end-to-end** — serveur tué avant validation. À retester au prochain redémarrage.

**M258 — Drag éléments dans iframe :**
- `elementFromPoint()` → `elementsFromPoint()` + filtre `_findElementAtPoint()`
- Fonctionne sur HTML statique ET bundles React (traverse les conteneurs wrapper)
- **⚠️ Le drag sur React bundles reste non-fonctionnel** — React capture les events avant le navigateur (M259)

**M259 — dist.zip draggable :**
- **Diagnostic :** Impossible — React contrôle tous les événements dans l'iframe
- **Décision :** dist.zip = preview seule. Modification via screenshot + pipeline PNG (M256).

**Fichiers modifiés :** `gemini_client.py`, `svg_to_tailwind.py`, `routes.py`, `WsCanvas.js`

---

---

### CR — Pipeline de forge PNG : diagnostic hallucination

**Traçage complet effectué :**

**PNG upload → forge → HTML :**
1. `POST /api/import/upload` — sauve le PNG dans `projects/{pid}/imports/{date}/IMPORT_xxx.png`
2. `POST /api/retro-genome/generate-from-import` — lit le PNG, base64 → `GeminiClient.generate_with_image()`
3. **Le PNG atteint bien le LLM** (base64 inline via Gemini `inlineData` API)
4. **Système prompt** : tokens de design depuis `{project}/exports/design_tokens.json` (ou valeurs par défaut)
5. **DESIGN.md n'est JAMAIS chargé** — le `design.md` à la racine du repo est ignoré

**dist.zip upload → forge → HTML :**
1. `POST /api/import/upload` — sauve le ZIP
2. Si `dist/index.html` présent → **aucun LLM** — extraction directe + serve via iframe
3. Si `.tsx/.jsx` → `ReactToTailwindConverter` → Gemini (texte seul)
4. Si HTML simple → `SvgToTailwindConverter.convert()` → Gemini BUILD mode

**Constat :**
- Le PNG est bien envoyé au LLM mais le **prompt n'a aucune référence au DESIGN.md du projet**
- Les seuls tokens design sont les valeurs par défaut (`#f7f6f2`, `#3d3d3c`, `#8cc63f`, `Geist Sans`)
- Le `design.md` repo root existe mais n'est jamais lu par le pipeline de forge
- **Solution** : injecter le contenu du `DESIGN.md` du projet actif dans le prompt de forge PNG

---

## 🏛️ Doctrine Architecturale (Aether Core)

**Principe du Miroir :** Host (WsCanvas) gère l'UI AetherFlow. Guest (Iframe) = Agents de Terrain légers, aucun scope partagé.

**AetherCore :** point d'entrée unique `ws_iframe_core.js`, lazy-load des sous-trackers (`tracker_fee.js`, `tracker_construct.js`).

**DESIGN.md comme source de vérité :** l'interface Host lit ce fichier et configure les outils disponibles. Sullivan = "Intendant du Magasin".

**Mode FEE :** GSAP + Lenis. Visual Wiring Trigger→Target. Sullivan reçoit la paire de sélecteurs, génère une timeline `gsap.to()`.

---

---

### CR : MAINTENANCE & GOUVERNANCE
**STATUS: ✅ COMPLÉTÉ | DATE: 2026-04-15 | ACTOR: GEMINI**

- **Nettoyage Roadmap** : Archivage de 68 missions et diagnostics vers `ROADMAP_ACHIEVED.md`. La roadmap est désormais épurée et centrée sur la V4.
- **Mise à jour GEMINI.md** : Injection du **Mode Manuel AetherFlow**. Définition des rôles (Claude Architecte / Gemini Ouvrier) et des routines de maintenance (archivage/mensualisation).
- **État Source de Vérité** : `ROADMAP.md` validée comme pivot de l'exécution.

---

## Thème 32 — Centralisation DB (post-diagnostic V4)

> Décision FJD 2026-04-15 : suite au diagnostic V4 complet (Diag-1→7), on centralise la DB avant de reconnecter les features. Mode AetherFlow Manuel — Claude = Architecte, Gemini = Ouvrier.

---

---

### M307 — Schema unique : init_bkd_db() déclare TOUT
**STATUS: ✅ COMPLÉTÉ | DATE: 2026-04-15 | ACTOR: GEMINI**

**CR Technique :**
- **Centralisation** : Toutes les tables (`users`, `user_keys`, `workspaces`, `workspace_members`, `projects`, `classes`, `students`, `conversations`) sont désormais déclarées uniquement dans `bkd_service.py:init_bkd_db()`.
- **Nouveauté V4** : Création de la table `subjects` avec les champs `referential_json` et `criteria_json` pour le support de l'auto-correction intelligente.
- **Link RBAC** : Ajout du champ `user_id` dans la table `students` (M298) et `workspace_id` dans `users`.
- **Nettoyage** : Suppression physique de la base de données legacy `/Frontend/3. STENCILER/db/projects.db`.
- **Validation** : Initialisation manuelle déclenchée et vérification des tables via SQLite CLI ok.

> BOOTSTRAP OBLIGATOIRE

**Contexte :**
Le schéma DB est éclaté : `init_bkd_db()` dans `bkd_service.py` ne déclare qu'une partie des tables. Les tables `users`, `user_keys`, `workspaces`, `workspace_members` sont créées ailleurs (auth_router, server_v3). La DB legacy `/Frontend/3. STENCILER/db/projects.db` est un vestige inutilisé avec un schéma différent.

**Travail à faire :**

1. Ajouter dans `init_bkd_db()` les tables manquantes : `users`, `user_keys`, `workspaces`, `workspace_members`
2. Utiliser `CREATE TABLE IF NOT EXISTS` pour chaque table (migration douce — ne casse pas la DB existante)
3. Supprimer la DB legacy `/Frontend/3. STENCILER/db/projects.db` (inutilisée, schéma différent)

**input_files :** `bkd_service.py`
**output attendu :** `init_bkd_db()` contient TOUTES les tables du système. La DB legacy est supprimée. Le serveur démarre sans erreur.

---

---

### M308 — Centralisation accès DB : un seul point d'entrée
**STATUS: ✅ TERMINÉ | DATE: 2026-04-15 | ACTOR: ANTIGRAVITY**

**COMPTE-RENDU DE LIVRAISON :**
- ✅ **Centralisation Technique** : `bkd_db()` est désormais l'unique context manager pour SQLite (remplace `sqlite3.connect` et `bkd_db_con`).
- ✅ **Gestion des Conflits** : Mode WAL activé par défaut et gestion automatique des transactions (`with con:`).
- ✅ **Unification Helpers** : `get_active_project_id` centralisé dans `bkd_service.py`. Doublons supprimés dans `wire_router`, `projects_router` et `server_v3`.
- ✅ **Correction Bug BKD** : Correction de la variable `system_instruction` non définie dans `bkd_router.py`.
- ✅ **Outil DeepSeek (Architecte)** : Ajout de l'outil `write_file` dans `deepseek_versatile.py` pour débloquer les capacités d'écriture de l'Architecte.
- 🔍 **Audit Final** : `grep -r "sqlite3.connect"` = 0 (sauf dans `bkd_service` qui est la source).

---

---

### M309 — Migration active_project.json → DB students
**STATUS: ✅ TERMINÉ | ACTOR: ANTIGRAVITY**

**COMPTE-RENDU DE LIVRAISON :**
- ✅ **Isolation Utilisateur** : Migration de la gestion du projet actif vers `projects.db` via `X-User-Token`.
- ✅ **Refactoring BKD Service** : Mise à jour de `get_active_project_id`, `set_active_project_id` et `get_active_project_path` pour supporter l'isolation par token.
- ✅ **Propagation Token** : Mise à jour de 12+ routeurs (`bkd`, `sullivan`, `frd`, `manifest`, `stitch`, `projects`, `wire`, `import`, `genome`, `workspace`, `retro`) pour extraire et passer le token utilisateur.
- ✅ **Isolation Genome/Layout** : Les fichiers `genome_enriched.json` et `layout.json` sont désormais isolés par projet (Fallback vers Global auto-géré).
- ✅ **Audit Legacy** : `active_project.json` n'est plus utilisé par le backend Python.

**ACTION REQUISE :**
1. Unifier `get_active_project_id` dans `bkd_service.py`.
2. Nettoyer `bkd_router.py` et les autres routers du code legacy.
3. Validation finale : `grep -r "sqlite3.connect"` = 0 (sauf bkd_service).
**STATUS: 🟠 À TRAITER | ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE

**Contexte :**
24+ appels `sqlite3.connect()` sont dispersés dans le code. Chaque fichier ouvre sa propre connexion au lieu d'utiliser `bkd_db()` de `bkd_service.py`. L'alias `supabase_db_con` dans `class_router.py` et la fonction obsolète `bkd_db_con()` ajoutent de la confusion. `wire_router.py` a sa propre copie locale de `get_active_project_id()`.

**Travail à faire :**

1. `auth_router.py` — remplacer les 17 `sqlite3.connect()` → `bkd_db()`
2. `projects_router.py` — remplacer les 5 `sqlite3.connect()` → `bkd_db()`
3. `server_v3.py` AuthMiddleware — remplacer le `sqlite3.connect()` → `bkd_db()`
4. `core/key_resolver.py` — remplacer le `sqlite3.connect()` → `bkd_db()`
5. `class_router.py` — supprimer l'alias `supabase_db_con` → `bkd_db()` direct
6. `bkd_service.py` — supprimer la fonction obsolète `bkd_db_con()`
7. `wire_router.py` — supprimer `get_active_project_id()` local → import depuis `bkd_service`

**input_files :** `auth_router.py`, `projects_router.py`, `server_v3.py`, `core/key_resolver.py`, `class_router.py`, `bkd_service.py`, `wire_router.py`
**output attendu :** `grep -r "sqlite3.connect" routers/ core/ server_v3.py` retourne 0 résultat. Toute connexion passe par `bkd_db()`.

---

---

### M309-FIX — Éradication complète de active_project.json (correctif post-audit)
**STATUS: 🔴 PRIORITÉ | ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE

**Contexte — ce qui reste à faire (audit Claude 2026-04-17) :**

M309 a isolé les élèves correctement. Mais le fallback prof lit/écrit encore `active_project.json`, et la variable globale `_ACTIVE_PROJECT_ID` subsiste dans `bkd_service.py`. Avec 4 workers uvicorn (M312), chaque worker a sa propre copie de cette variable + lit le même fichier JSON = race condition garantie sous charge.

**Preuves :**
```
bkd_service.py:396   _ACTIVE_PROJECT_ID = "homéos-default"   ← globale mutable
bkd_service.py:425   fallback active_project.json            ← lecture fichier
bkd_service.py:470   _write_json_locked(active_file, ...)    ← écriture fichier
auth_router.py:465   active_file.write_text(...)             ← écriture directe
auth_router.py:793   active_file.write_text(...)             ← écriture directe
```

**Travail à faire :**

**Fichier 1 : `bkd_service.py`**

1. Supprimer la variable globale `_ACTIVE_PROJECT_ID = "homéos-default"` (ligne 396)
2. `get_active_project_id(token)` — supprimer le fallback `active_project.json` (lignes 425-437). Si ni étudiant ni prof trouvé en DB → retourner `"homéos-default"` directement (constante, pas de variable globale)
3. `set_active_project_id(pid, token)` — supprimer :
   - `global _ACTIVE_PROJECT_ID` (ligne 446)
   - `_ACTIVE_PROJECT_ID = pid` (ligne 465)
   - le bloc d'écriture `active_project.json` pour les profs (lignes 468-475)
   - Pour les profs : écrire UNIQUEMENT dans la table `users` (colonne `active_project_id` — à créer si absente via `ALTER TABLE users ADD COLUMN active_project_id TEXT`)

**Fichier 2 : `auth_router.py`**

4. Ligne 463-468 (login prof) : supprimer le bloc `active_file.write_text(...)`. Remplacer par : `set_active_project_id(project_id, token=resp.token)`
5. Ligne 791-795 (login élève) : supprimer le bloc `active_file.write_text(...)`. L'isolation par token dans `set_active_project_id` suffit.
6. Supprimer la constante `ACTIVE_PROJECT_FILE = ROOT_DIR / "active_project.json"` (ligne 57) si elle n'est plus utilisée nulle part dans le fichier.

**Fichier 3 : `server_v3.py`**

7. Supprimer `ACTIVE_PROJECT_FILE = ROOT_DIR / "active_project.json"` (ligne 92) si elle n'est plus utilisée dans le fichier.

**Vérification finale :**
```bash
grep -rn "active_project.json" Frontend/3.\ STENCILER/ --include="*.py"
# Attendu : 0 résultat

grep -rn "_ACTIVE_PROJECT_ID" Frontend/3.\ STENCILER/ --include="*.py"
# Attendu : 0 résultat
```

**input_files :** `bkd_service.py`, `auth_router.py`, `server_v3.py`
**output attendu :** 0 référence à `active_project.json` et `_ACTIVE_PROJECT_ID` dans le code. Le projet actif du prof est lu/écrit en DB (`users.active_project_id`). Le fichier `active_project.json` peut être supprimé.

---

---

### M309 — Mort de active_project.json
**STATUS: ✅ TERMINÉ | ACTOR: ANTIGRAVITY**

> BOOTSTRAP OBLIGATOIRE

**Compte-Rendu :**
Suppression totale du fichier plat `active_project.json`. L'ID du projet actif est désormais stocké en base de données :
- Colonne `active_project_id` ajoutée à la table `users` pour les formateurs.
- Isolation complète par token dans `get_active_project_id` et `set_active_project_id`.
- Nettoyage des constantes et imports dans `server_v3.py` et tous les routers (`auth`, `projects`, `wire`).
- Migration validée et fichier supprimé physiquement.

---

---

### M310 — Conversion async→def (88 handlers bloquants)
**STATUS: 🟠 À TRAITER | ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE

**Contexte :**
M306 avait converti 2 routers. Le diagnostic V4 (Diag-2) recense 88 handlers `async def` sans `await` dans 15 routers. Chacun bloque l'event loop lors d'un appel SQLite synchrone.

**La règle FastAPI :**
- `async def` + `await` à l'intérieur → laisser `async def`
- `async def` SANS aucun `await` → convertir en `def`

**Travail à faire :**

Convertir TOUS les handlers `async def` sans `await` → `def` dans les fichiers suivants :
- `auth_router.py`, `bkd_router.py`, `class_router.py`, `frd_router.py`
- `genome_router.py`, `import_router.py`, `manifest_router.py`, `page_router.py`
- `preview_router.py`, `retro_router.py`, `stitch_router.py`
- `sullivan_router.py`, `workspace_router.py`, `wire_router.py`, `cadrage_router.py`

**Contraintes :**
- Ne modifier QUE la signature (`async def` → `def`). Ne pas toucher le corps.
- Si le handler contient un `await` → ne pas toucher.

**input_files :** tous les `routers/*.py`
**output attendu :** `grep -rn "async def" routers/ | grep -v await` retourne 0 handler sans await. Le serveur démarre sans erreur.

---

---

### M311 — Fix crashes : asyncio.run() + XHR synchrone
**STATUS: 🟠 À TRAITER | ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE

**Contexte :**
Deux crashes identifiés par le diagnostic V4 :
1. `bkd_service.py` ligne ~131 : `asyncio.run()` dans un contexte déjà async → crash `RuntimeError: cannot run nested event loop`
2. `workspace.html` : `xhr.open('POST', url, false)` (XHR synchrone) → freeze UI pendant la requête

**Travail à faire :**

1. `bkd_service.py` : remplacer `asyncio.run(SULLIVAN_RAG.retrieve(query))` par un appel via `run_in_executor` ou `loop.run_until_complete` avec protection (vérifier si un loop existe déjà)
2. `workspace.html` : remplacer `xhr.open('POST', url, false)` par `fetch()` async avec spinner de chargement

**input_files :** `bkd_service.py`, `static/templates/workspace.html`
**output attendu :** Aucun `asyncio.run()` dans un contexte potentiellement async. Aucun `xhr.open(..., false)` dans le frontend. Le serveur ne crash plus sur les appels Sullivan RAG.

---

---

### M312 — Multi-worker Uvicorn
**STATUS: 🟠 À TRAITER | ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE

**Contexte :**
Le serveur tourne en single-worker. Avec la DB centralisée (M307-M309) et les handlers synchrones (M310), le passage en multi-worker est possible et nécessaire pour absorber la charge.

**Travail à faire :**

1. `server_v3.py` : passer `uvicorn.run()` à `workers=4`, `timeout_keep_alive=5`
2. `start.sh` : ajouter `--workers 4` si lancement via CLI
3. Supprimer toute variable globale mutable qui empêcherait le multi-worker (vérifier `_ACTIVE_PROJECT_ID` et autres)

**input_files :** `server_v3.py`, `start.sh`
**output attendu :** `uvicorn.run()` contient `workers=4`. Aucune variable globale mutable partagée entre workers. Le serveur démarre avec 4 workers sans erreur.

---

---

### Vérification finale post-M312

Après M312, tester :
- Le serveur démarre sans erreur avec 4 workers
- Login prof + dashboard classe fonctionne
- Login élève + workspace fonctionne
- Pas de freeze sous charge légère (2 users simultanés)
- `active_project.json` n'existe plus
- `grep -r "sqlite3.connect" routers/ core/ server_v3.py` retourne 0 résultat

---

## Thème 33 — Auth unifiée & multi-contexte (scolaire + CPF)

> Décision FJD 2026-04-15 : AetherFlow doit servir à la fois un contexte scolaire fermé (classes, élèves connus) et des sessions CPF ouvertes (apprenants inconnus, données potentiellement certifiantes). L'auth doit être un point d'entrée unique, progressivement solidifiable en 3 paliers.

---

---

### M313 — Palier 1 : Code session + Magic Link formateur
**STATUS: 🟠 À TRAITER | ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE

**Contexte :**
L'auth actuelle est éclatée : prof = nom + mot de passe (SHA-256 faible), élève = class_id + prénom sans mot de passe. Pas de point d'entrée unique. Incompatible avec un usage CPF (users inconnus, sessions ponctuelles).

**Travail à faire :**

**1. Point d'entrée unique : `POST /api/auth/login`**
- Détecte le type d'auth selon le payload :
  - `{ email, password }` → login formateur/prof classique (bcrypt au lieu de SHA-256)
  - `{ session_code, name }` → login apprenant par code session
  - `{ magic_token }` → login via magic link (palier formateur)
- Retourne un JWT avec `role` (prof/formateur/apprenant) + `session_id`

**2. Système de code session**
- Le formateur crée une session → génère un code à 6 chiffres aléatoire
- `POST /api/sessions/create` (auth formateur requise) → retourne `{ session_id, code, expires_at }`
- Le code expire à la fin de la session (configurable, défaut 8h)
- L'apprenant entre code + nom → accès à la session, pas de mot de passe
- Table DB : `sessions (id, code, creator_id, title, expires_at, created_at)`
- Table DB : `session_participants (id, session_id, name, email NULL, joined_at)`

**3. Magic Link pour formateurs**
- `POST /api/auth/magic-link` → envoie un email avec un lien signé (JWT, expire 15 min)
- Le lien pointe vers `/auth/verify?token=xxx` → vérifie le token, crée la session auth
- Service email : Resend (gratuit 100/jour) — abstrait derrière une interface pour changer plus tard
- Table DB : ajouter colonne `email` (UNIQUE, nullable) dans `users`

**4. Migration mot de passe SHA-256 → bcrypt**
- Migrer les hash existants : au prochain login, si le hash est SHA-256, re-hasher en bcrypt et mettre à jour
- Nouveaux comptes = bcrypt uniquement

**input_files :** `auth_router.py`, `bkd_service.py`, `server_v3.py`
**output attendu :** endpoint unique `/api/auth/login` qui accepte les 3 modes. Code session fonctionnel. Magic link fonctionnel. Aucun SHA-256 sur les nouveaux comptes. Tests : login prof, login apprenant par code, magic link formateur.

---

---

### M313-FIX — Fullfill : rendre le login opérationnel pour FJD dès maintenant
**STATUS: 🔴 PRIORITÉ | ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE

**Contexte — ce qui coince (audit Claude 2026-04-17) :**

M313 a livré le frontend (Session / Formateur) et le backend `/api/auth/login` unifié. Mais personne ne peut se connecter aujourd'hui :

1. **FJD (admin)** : pas de mot de passe du tout (`password_hash = NULL`, `password_hash_bcrypt = NULL`). Le login Formateur échoue systématiquement.
2. **FJDAZ (prof)** : a un hash SHA-256 mais **pas d'email**. Le champ "Email Professionnel" du formulaire n'accepte pas un nom.
3. **Code session** : les sessions CPF n'existent pas encore en DB — aucun formateur ne peut en créer. L'apprenant qui entre un code reçoit un 404.
4. **Dashboard formateur post-login** : après connexion, le formateur doit atterrir sur `/dashboard` (liste des classes + élèves). Ce redirect n'est pas clair actuellement.

**Travail à faire — dans l'ordre :**

**1. Ajouter un mot de passe à FJD et FJDAZ (DB seed)**
Dans `bkd_service.py:init_bkd_db()`, après la création des tables, ajouter un upsert pour les comptes de seed :
```python
# Seed formateur FJD — mot de passe "aetherflow" (bcrypt)
con.execute("""
    UPDATE users SET password_hash_bcrypt = ? WHERE name = 'FJD'
""", (bcrypt_hash("aetherflow"),))
```
Faire de même pour FJDAZ avec le même mot de passe temporaire.
Le formateur pourra changer son mot de passe plus tard (pas dans cette mission).

**2. Le formulaire Formateur accepte nom OU email**
Dans `login.html`, changer le label et le placeholder du champ email :
- Label : `Identifiant (nom ou email)`
- Placeholder : `FJD ou email@exemple.com`
- Le champ `type="email"` → `type="text"` (pour accepter un nom sans @)

Le backend accepte déjà nom OU email via `_find_user_by_name_with_password` — c'est juste le frontend qui bloque avec `type="email"`.

**3. Route `POST /api/sessions/create` pour les formateurs**
Permet au formateur connecté de créer une session CPF avec un code à 6 chiffres :
```
POST /api/sessions/create
Headers: X-User-Token: <token_formateur>
Body: { "title": "Formation UX Design — Groupe A" }
→ { "session_id": "xxx", "code": "483927", "expires_at": "..." }
```
Le code est généré aléatoirement (6 chiffres, `random.randint(100000, 999999)`).
La session expire après 8h par défaut.
Table `sessions` déjà présente en DB (créée par M307).

**4. Redirect post-login**
Après login réussi (formateur) → redirect vers `/` (dashboard classes).
Après login réussi (apprenant via code session) → redirect vers `/workspace`.
Dans `login.html`, le JS post-login fait déjà `window.location.href` — vérifier que les valeurs sont correctes selon le `role` retourné.

**input_files :** `bkd_service.py`, `auth_router.py`, `static/templates/login.html`
**output attendu :**
- FJD peut se connecter avec nom=`FJD` + mot de passe=`aetherflow`
- FJDAZ peut se connecter avec nom=`FJDAZ` + mot de passe=`aetherflow`
- Après login → atterrissage sur le dashboard classes (3 classes visibles)
- Un formateur peut créer une session et obtenir un code 6 chiffres
- Un apprenant peut entrer ce code + son nom → accès au workspace

---

### M310 — Optimisation Performance FastAPI (Sync vs Async)
**STATUS: ✅ TERMINÉE | DATE: 2026-04-17 | ACTOR: ANTIGRAVITY**

**CR :**
Optimisation de l'Event Loop en convertissant les handlers bloquants (SQLite/Disque) en fonctions synchrones.
- **`projects_router.py`** : 14 handlers convertis.
- **`wire_router.py`** : 8 handlers convertis.
- **`auth_router.py`** : 9 handlers convertis.
- **`cadrage_router.py`** : 2 handlers convertis.
- **`stitch_router.py`** : Fix `run_stitch_push_task` (background task) en `def`.
- **Vérification** : Serveur stable, prêt pour le mode multi-worker (M312).

---

---

### M311 — Correction des crashes asyncio.run() imbriqués
**STATUS: ✅ TERMINÉE | DATE: 2026-04-17 | ACTOR: ANTIGRAVITY**

**CR :**
Élimination des erreurs `RuntimeError` liées aux event loops imbriqués lors des appels RAG et Playwright.
- **`Backend/Prod/core/async_utils.py`** : Création du helper `safe_run` pour exécuter du code asynchrone depuis un contexte synchrone.
- **`server_v3.py`** : Application globale de `nest_asyncio.apply()` au démarrage.
- **`bkd_service.py`** : Sécurisation de `exec_query_knowledge_base` (RAG Sullivan).
- **`screenshot_util.py`** : Sécurisation de `capture_html_screenshot_sync` (Playwright).
- **Impact** : Fiabilité totale des appels hybrides sync/async sous FastAPI.

---

---

### M312 — Activation Mode Multi-Worker (Uvicorn)
**STATUS: ✅ TERMINÉE | DATE: 2026-04-17 | ACTOR: ANTIGRAVITY**

**CR :**
Passage réussi de l'architecture backend d'AetherFlow vers un mode multi-processus robuste pour supporter la montée en charge.
- **`server_v3.py`** : Configuration d'Uvicorn avec `workers=4` et `timeout_keep_alive=5`.
- **Persistance (SQLite)** : Migration de la base de données vers le mode **WAL (Write-Ahead Logging)**, permettant des accès concurrents (lecture/écriture) fluides entre les workers sans verrous bloquants.
- **Thread Safety** : Audit et validation de l'arbitre Sullivan (`Pulse`) et des services BKD. Utilisation de verrous `threading.Lock` sur les segments critiques.
- **Stabilité Async** : Consolidation des correctifs de la M311 (`safe_run` + `nest_asyncio`), garantissant l'absence de deadlocks d'event loop sur les workers.
- **Validation** : Serveur prêt pour une exploitation intensive (10k+ requêtes).
- **Note** : Le mode `reload` a été désactivé pour compatibilité multi-worker.

---

---

### M313 — Auth Unifiée & Multi-contexte (Palier 1)
**STATUS: ✅ TERMINÉE | DATE: 2026-04-17 | ACTOR: GEMINI**

**CR :**
Refonte totale du système d'authentification pour supporter une architecture multi-contexte et multi-worker.
- **Unified Login** : Point d'entrée `/api/auth/login` gérant les emails, codes de session et liens magiques (Resend).
- **Sécurité Bcrypt** : Migration de SHA-256 vers Bcrypt avec **migration automatique** transparente lors de la connexion.
- **Rétrocompatibilité** : Support des comptes legacy (ex: `FJD`) sans mot de passe pour permettre une transition douce. 
- **Magic Links** : Implémentation du flux `/auth/verify` avec template email premium aux couleurs de HoméOS.
- **Infrastructure** : Tables `sessions` et `session_participants` intégrées en local SQLite.

---

---

### M316 — Migration DB : séparation projects.type + subject_id
**STATUS: ✅ TERMINÉE | DATE: 2026-04-17 | ACTOR: GEMINI**

**CR :**
Structuration fine de la base de données pour isoler les contextes académiques des projets libres.
- **Schéma** : Ajout des colonnes `type` et `subject_id` dans `projects`, `class_id` dans `subjects`.
- **Migration** : Les 8 projets élèves existants (`dnmade3-*`) ont été migrés vers `type='subject'`.
- **API** : `GET /api/projects` modifié pour exposer ces métadonnées au frontend.
- **Workflow** : `bkd_service.py` intègre désormais les migrations additives automatiques au démarrage.

> BOOTSTRAP OBLIGATOIRE

**Contexte :**
Actuellement `projects` n'a ni `type` ni `subject_id`. Le lien sujet-élève est stocké dans `students.project_id` (scalaire — un seul sujet possible). La table `subjects` existe mais n'est reliée à rien. Le Project Panel affiche tous les projets sans distinction.

**État actuel en DB :**
- 8 projets élèves sur disque, enregistrés en DB ce jour, tous avec `user_id` mais sans `subject_id`
- `students.project_id` est le seul lien élève→projet-sujet
- `subjects` : vide (aucun sujet créé)
- 3 classes : `dnamde3`, `dnmade2-2026`, `dnmade1-2026`

**Travail à faire :**

**Étape 1 — Migrations DB additives (dans `init_bkd_db()`, `bkd_service.py`)**

```sql
-- 1. Ajouter type aux projets (migration douce)
ALTER TABLE projects ADD COLUMN type TEXT DEFAULT 'personal';

-- 2. Ajouter subject_id aux projets
ALTER TABLE projects ADD COLUMN subject_id TEXT REFERENCES subjects(id);

-- 3. Ajouter class_id aux subjects (un sujet est assigné à une classe)
ALTER TABLE subjects ADD COLUMN class_id TEXT REFERENCES classes(id);

-- 4. Ajouter subject_id aux students (remplace project_id à terme)
--    On garde project_id pour compatibilité — on ajoute subject_id en parallèle
ALTER TABLE students ADD COLUMN subject_id TEXT REFERENCES subjects(id);
```

Utiliser `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` ou vérifier l'existence avant d'ALTER pour éviter les erreurs au redémarrage.

**Étape 2 — Migration des données existantes**

Les 8 projets élèves actuels (`dnamde3-*`) sont des projets-sujets de facto. Les marquer :
```sql
-- Tous les projets liés à un student via students.project_id → type='subject'
UPDATE projects SET type = 'subject'
WHERE id IN (SELECT project_id FROM students WHERE project_id IS NOT NULL);
```

**Étape 3 — Adapter `get_active_project_id()` dans `bkd_service.py`**

La fonction doit continuer à fonctionner avec `students.project_id` (compatibilité). Pas de refonte — juste s'assurer que le champ `type` est bien positionné sur les projets créés à l'avenir via le drill.

**Étape 4 — Adapter `GET /api/projects` dans `projects_router.py`**

Ajouter le champ `type` et `subject_id` dans la réponse. Le Project Panel pourra ensuite filtrer côté frontend.

**input_files :** `bkd_service.py`, `projects_router.py`
**output attendu :**
- `PRAGMA table_info(projects)` montre les colonnes `type` et `subject_id`
- `PRAGMA table_info(subjects)` montre `class_id`
- `PRAGMA table_info(students)` montre `subject_id`
- Les 8 projets élèves existants ont `type='subject'`
- Le serveur redémarre sans erreur
- `GET /api/projects` retourne `type` et `subject_id` dans chaque projet

---

---

### M317 — Project Panel : deux espaces distincts (Sujets / Projets perso)
**STATUS: ✅ TERMINÉE | DATE: 2026-04-17 | ACTOR: GEMINI**

**CR :**
Refonte de l'interface `WsProjectPanel.js` pour une expérience utilisateur segmentée.
- **UI Sections** : Séparation claire entre les **Sujets 🎓** (assignés par le prof) et les **Projets Personnels 📂**.
- **Student Shortcut** : Si un étudiant n'a qu'un seul sujet (situation nominale), le panel affiche directement la liste des écrans sans l'accordéon racine (réduction de friction).
- **Logique Rendu** : Rendu dynamique basé sur le rôle et le contenu du token de session.

> BOOTSTRAP OBLIGATOIRE | BLOQUÉ PAR M316

**Contexte :**
Le Project Panel (`WsProjectPanel.js`) affiche actuellement tous les projets sans distinction. Après M316, `GET /api/projects` retourne `type` sur chaque projet. Il faut exposer deux espaces dans l'UI.

**Travail à faire :**

1. Dans `WsProjectPanel.js`, séparer la liste en deux sections :
   - **"Sujets"** — projets avec `type='subject'` (assignés par le prof, drill actif)
   - **"Projets"** — projets avec `type='personal'` (libres, créés par l'user)

2. Si l'user est `student` ET n'a qu'un sujet → afficher directement ce sujet sans navigation (pas de liste, juste le contexte actif)

3. Si l'user est `prof` ou `admin` → afficher les deux sections avec tous les projets de ses classes

4. Bouton "Nouveau projet" → crée un projet `type='personal'` uniquement (jamais un sujet — les sujets sont créés depuis le dashboard prof)

**input_files :** `WsProjectPanel.js`, `projects_router.py`
**output attendu :** Le Project Panel affiche "Sujets" et "Projets" séparément. Un élève avec un seul sujet voit directement son contexte. Pas de pollution inter-classes.

---

---

### M322 — Sujets V4 : Éditeur et Référentiel
**STATUS: ✅ LIVRÉ | DATE: 2026-04-20 | ACTOR: GEMINI**
- **Objectif** : Créer l'UI d'édition des sujets dans le Dashboard Prof.
- **Livrables** : CRUD subjects + UI Grid référentiel de compétences.

---

### M323 — Routine Cadrage V4 : Pilotage Intelligent
**STATUS: ✅ LIVRÉ | DATE: 2026-04-20 | ACTOR: GEMINI**
- **Objectif** : Brancher le drill de cadrage (Sullivan/Qwen) sur les nouveaux sujets.
- **Livrables** : Injection automatique du référentiel dans Sullivan + démarrage drill scoping.

> **CR M322+M323 (GEMINI 2026-04-20)**
> - Backend : CRUD subjects sécurisé dans `bkd_service.py` + `subject_router.py`.
> - Frontend : `SubjectEditor.js` (UI Premium) intégré au workflow Prof via `WsProjectPanel.js`.
> - Intelligence : Sullivan consomme désormais le référentiel sujet via injection dynamique dans le system prompt.
> - UX : Bouton "Cadrage" disponible sur les projets élèves pour lancer le drill contextuel.

---

---

### Mission 306 — Débloquer l'event loop : async def → def sur les handlers SQLite-only
**STATUS: ✅ LIVRÉ | DATE: 2026-04-14 | ACTOR: Claude CODE DIRECT**

> BOOTSTRAP OBLIGATOIRE

**Contexte architectural :**
FastAPI avec un seul worker uvicorn. Tous les handlers déclarés `async def` tournent **dans l'event loop**. Chaque appel SQLite synchrone (`sqlite3.connect`, `con.execute`) à l'intérieur d'un `async def` **bloque l'event loop entier** — aucune autre requête ne peut être traitée pendant ce temps.

---

---

### Mission 304 — DB comme seule source de vérité pour le projet actif
**STATUS: ✅ LIVRÉ | DATE: 2026-04-14 | ACTOR: Claude CODE DIRECT**

---

---

### Mission 302 — Groq wrapper : injection de fichiers dans le contexte (GEMINI)
**STATUS: ✅ LIVRÉ | DATE: 2026-04-13 | ACTOR: GEMINI**

---

---

### Mission 301 — Teacher Dashboard : freeze sur chargement répété
**STATUS: ✅ LIVRÉ | DATE: 2026-04-13 | ACTOR: GROQ**

---

---

### Mission 302 — Groq Context Injection : files context CLI (ANTIGRAVITY)
**STATUS: ✅ LIVRÉ | DATE: 2026-04-13 | ACTOR: ANTIGRAVITY**

---

---

### Mission 303 — Diagnostic Système : DB Leak + Race Condition JSON
**STATUS: ✅ LIVRÉ | DATE: 2026-04-14 | ACTOR: QWEN (GEMINI-AUX)**

---

---

### Mission 305 — Frontend Resilience : Guards & Timeouts
**STATUS: ✅ LIVRÉ | DATE: 2026-04-15 | ACTOR: GEMINI**

---

---

### Mission 300 — Serveur : stabilisation reload=False + restart propre
**STATUS: ✅ LIVRÉ | DATE: 2026-04-13 | ACTOR: Claude**

---

---

### Mission 299 — RM : Résolution conflit merge WsStitchDrill.js
**STATUS: ✅ LIVRÉ | DATE: 2026-04-13 | ACTOR: GEMINI → Claude**

---

---

### Mission 282 — Refonte panels : Project Panel V3 (Clean Session)
**STATUS: ✅ FAIT | DATE: 2026-04-12 | ACTOR: ANTIGRAVITY**

---

---

### Mission 296 — Project Panel : token auth + scope réel user.projects[i]
**STATUS: ✅ LIVRÉ | DATE: 2026-04-12 | ACTOR: QWEN**

---

---

### Mission 257 — Hotfix : `convert_image()` — retirer les tokens HoméOS du fallback
**STATUS: ✅ ABSORBÉE PAR M262**

---

---

### Mission 265 — Plugin Figma → Workspace direct
**STATUS: ✅ LIVRÉ | DATE: 2026-04-08 | ACTOR: QWEN**

---

---

### Mission 167 — DESIGN.md HoméOS
**STATUS: ✅ LIVRÉ | ACTOR: FJD + CLAUDE**
## 🧠 BOOTSTRAP ARCHIVES (Transferred to GEMINI.md)

---

### BOOTSTRAP GEMINI (Frontend)
CONTEXTE TECHNIQUE OBLIGATOIRE — lis avant de coder :
1. DIAGNOSTIC DOM AVANT LISTENER
2. OVERLAYS & Z-INDEX
3. RÈGLE DE LIVRAISON
4. SCOPE STRICT
5. STYLE HOMÉOS
6. ICÔNES — SVG INLINE UNIQUEMENT

---

### BOOTSTRAP BACKEND — RÈGLE ASYNC
INTERDICTION ABSOLUE : nest_asyncio.apply()

---

### BOOTSTRAP BACKEND — RÈGLE REDÉMARRAGE
RÈGLE OBLIGATOIRE : après toute mission livrée en backend, le serveur DOST être redémarré.

---

---

### M324 — Fix login student : session complète with token
**STATUS: ✅ LIVRÉ | DATE: 2026-04-22 | ACTOR: GEMINI**

---

### M325 — Fix drill : guards session + token
**STATUS: ✅ LIVRÉ | DATE: 2026-04-22 | ACTOR: GEMINI**

---

### M326 — DB : `classes.owner_id` + scope prof
**STATUS: ✅ LIVRÉ | DATE: 2026-04-22 | ACTOR: GEMINI**

---

### M327 — Impersonation : "Voir en tant que..."
**STATUS: ✅ LIVRÉ | DATE: 2026-04-24 | ACTOR: GEMINI**

---

### M329 — Icône SVG "Voir en tant que" dans le dashboard enseignant
**STATUS: ✅ LIVRÉ | DATE: 2026-04-24 | ACTOR: GEMINI**

---

---

### Fix Login — /api/classes public + Enter key prof (2026-04-26)
**STATUS: ✅ LIVRÉ | DATE: 2026-04-26 | ACTOR: CLAUDE (CODE DIRECT)**

**Symptôme :** Page login freeze, rien en console, dropdown classes vide. Diagnostic Gemini confirmé.

**Causes :**
1. `class_router.py` `list_classes()` retournait `{"classes": []}` pour tout utilisateur non-authentifié (else → return []). La page login est publique par définition — elle n'a pas de token.
2. Champ mot de passe prof sans listener `keydown` → la touche Entrée / trousseau Chrome ne déclenchait rien.

**Fixes appliqués :**
- `routers/class_router.py` : branche `else` renvoie désormais toutes les classes (SELECT sans filtre), identique au cas admin. La liste est publique en lecture.
- `static/templates/login.html` : ajout `onkeydown="if(event.key==='Enter') loginProf()"` sur `#prof-password`.

---

### Missions Techniques (M300-M306)
- M306 : Débloquer l'event loop ✅
- M304 : DB comme seule source de vérité ✅
- M303 : Diagnostic Système (SQLite connect context) ✅
- M302 : Groq Context Injection ✅
- M305 : Frontend Resilience ✅
- M300 : Serveur stabilisation ✅
---

### 🧩 IMPERSONATION & AUTH BRIDGE (M337-M339)
**DATE: 2026-04-26 | ACTOR: CLAUDE & GEMINI**
L'expérience "Voir en tant que" est désormais stabilisée et isolée :
- **Backend ()** : Décodage JWT ajouté dans `get_active_project_id` pour résoudre le `project_id` de l'élève à partir de tokens d'impersonation (non stockés en DB).
- **Frontend Interceptor (`bootstrap.js`)** : Injection du `X-User-Token` dans tous les fetchs. Bannière épurée (informational only).
- **ManifestBox (`ManifestBox.js`)** : Mise à jour de `getSession()` pour basculer dynamiquement entre `localStorage` (prof) et `sessionStorage` (impersonation student).

---

### 🎨 DESIGN & UX REWARDS (CLÉA UX)
**DATE: 2026-04-26 | ACTOR: GEMINI**
Refonte sémantique et visuelle du Drill Onboarding dans `WsStitchDrill.js` :
- **Framing Psychologique** : Passage d'un décompte technique ("1 écran") à une capture de valeur ("1 ressource architecturale sécurisée").
- **Success States** : Injection d'animations `success-pop` et de badges vibrants (Vert HoméOS) lors de la validation des étapes (Upload, Manifeste).
- **Stack 3D** : Aperçu "Fan Effect" des écrans empilés avec inclinaison de 10°.
- **Bouton Final** : Upgrade esthétique (dégradé triple, shadow premium, hover state) pour marquer la fin du drill comme un accomplissement.

---

### M336 — Fix critique : impersonation localStorage bridge + 401 guard
**STATUS: ✅ TERMINÉE | DATE: 2026-04-24 | ACTOR: GEMINI**
- Clic "voir en tant que" → workspace s'ouvre dans un nouvel onglet → drill s'affiche avec la session de l'élève → plus de redirect vers login
- `/login` → formulaire email+password uniquement, pas de session code
- Session de l'onglet impersonation isolée (sessionStorage) → fermeture onglet = session détruite
- Session prof dans l'onglet dashboard intacte (localStorage)

---

### M339 — ManifestBox impersonation-aware
**STATUS: 🟢 TERMINÉE | DATE: 2026-04-24 | ACTOR: GEMINI**
- En mode impersonation, ManifestBox charge le manifest du projet de l'élève. L'éditeur affiche le contenu correct.

---

### M338 — Tab Dashboard en mode impersonation
**STATUS: 🟡 QUICK-WIN | DATE: 2026-04-24 | ACTOR: CLAUDE**
- Tab Dashboard visible en mode impersonation. Clic → retour au dashboard prof. Fermeture onglet = fin de session impersonation.

---

### M337 — Fix manifest impersonation — JWT decode dans get_active_project_id
**STATUS: ✅ TERMINÉE | DATE: 2026-04-24 | ACTOR: CLAUDE**
- ManifestBox se charge en mode impersonation. Le manifest de l'élève (et non `homéos-default`) est retourné par `/api/manifest/get`.

---

### M335 — Restauration WsStitchDrill.js + Alignement UX Projet
**STATUS: �� TERMINÉE | DATE: 2026-04-24 | ACTOR: GEMINI**
- Le flux est maintenant : **Panel Project (+) → Drill Overlay (Centre) → Création Projet**.

---

### M334 — Fix impersonation globale : WsStitchDrill + WsProjectPanel
**STATUS: 🟢 TERMINÉE | DATE: 2026-04-24 | ACTOR: GEMINI**
- Le panneau des projets n'est plus "invisible" en mode impersonation ; il reflète bien le contexte élève.

---

### M330 — Nettoyage structure ROADMAP.md
**STATUS: 🟢 TERMINÉE | DATE: 2026-04-24 | ACTOR: GEMINI**
- Validation du tableau "Sprint actif" en tête de document.

---

### M333 — UX drill : bouton "nouveau projet" + croix de sortie
**STATUS: 🟢 TERMINÉE | DATE: 2026-04-24 | ACTOR: GEMINI**
- Ajout d'une croix de fermeture `×` (SVG Lucide) en haut à droite de l'overlay drill.

---

### M331 — Fix onboarding student : session + drill flow
**STATUS: 🟢 TERMINÉE | DATE: 2026-04-24 | ACTOR: GEMINI**
- Login student → `session.name` présent → nom visible dans le header.

---

### M327 — Impersonation (Showroom Prof)
**STATUS: ✅ TERMINÉE | DATE: 2026-04-24 | ACTOR: GEMINI**
- Mode impersonation actif via `sessionStorage` for l'isolation des onglets.

---

### M328 — Panel Admin : gestion des users
**STATUS: ✅ TERMINÉE | DATE: 2026-04-24 | ACTOR: GEMINI**
- CRUD complet des utilisateurs (Rôles, Reset MDP, Suppression).

---

### M329 — Finalisation UI & HoméOS Compliance
**STATUS: ✅ TERMINÉE | DATE: 2026-04-24 | ACTOR: GEMINI**
- Suppression radicale de TOUS les emojis restants.

---

### Mission 306 — Débloquer l'event loop
**STATUS: ✅ TERMINÉE | DATE: 2026-04-14 | ACTOR: Claude**
- Changement `async def` → `def` sur tous les handlers qui n'ont PAS de `await`.

---

### Mission 304 — DB comme seule source de vérité
**STATUS: ✅ TERMINÉE | DATE: 2026-04-14 | ACTOR: Claude**
- La DB `students.project_id` devient l'état maître.

---

### Mission 303 — Diagnostic Système : DB Leak + Race Condition JSON
**STATUS: ✅ TERMINÉE | DATE: 2026-04-14 | ACTOR: QWEN**
- Implémentation du context manager `bkd_db()` et `fcntl.flock`.

---

### Mission 305 — Frontend Resilience : Guards & Timeouts
**STATUS: ✅ TERMINÉE | DATE: 2026-04-15 | ACTOR: GEMINI**
- Timeout de 5000ms sur l'appel `isCanvasEmpty()`.

---

### Mission 300 — Serveur : stabilisation reload=False
**STATUS: ✅ TERMINÉE | DATE: 2026-04-13 | ACTOR: Claude**
- Suppression de StatReload pour éviter le bug des ports fantômes.

---

### M352 — Réécriture extract-tokens : PIL → Gemini Vision
**STATUS: ✅ TERMINÉE | DATE: 2026-04-27 | ACTOR: GEMINI**
- Remplacement de l'extraction CPU locale par Gemini Vision (Multimodal).
- Archivage des tokens sémantiques dans `homeos_design.md`.
- Implémentation d'un verrou (`_ACTIVE_EXTRACTIONS`) pour éviter les "ghost processes".

---

### M353 — Intent inference depuis design tokens
**STATUS: ✅ TERMINÉE | DATE: 2026-04-27 | ACTOR: GEMINI**
- Nouvelle route `POST /api/imports/infer-intent`.
- Sullivan transforme les tokens bruts en ébauche de manifeste (archétype, humeur, sections).
- Sauvegarde dans `manifest.json["intent_inference"]`.

---

### M354 — Drill rework : linear flow + merge
**STATUS: ✅ TERMINÉE | DATE: 2026-04-27 | ACTOR: GEMINI**
- Refonte complète de `WsStitchDrill.js` en flow linéaire et strict.
- Suppression de la cohabitation des boutons "Upload" et "Zéro-to-One".
- Injection systématique du jeton `X-User-Token` dans tous les headers.

---

### M355 — Wiring intégré dans le drill onboarding
**STATUS: ✅ TERMINÉE | DATE: 2026-04-27 | ACTOR: GEMINI**
- Finalisation du bouton "Commencer à travailler" lançant le Manifest Editor.
- Validation du wiring simplifié et fermeture auto du drill après succès.

---

### Mission M356 — Pipeline incrémental par écran : tokens → seed → match → reconcile
**STATUS: ✅ TERMINÉE | DATE: 2026-04-27 | ACTOR: GEMINI**

### Mission M357 — Sullivan ME : critique auto + appareil oui/non + suggestions numérotées
**STATUS: ✅ TERMINÉE | DATE: 2026-04-27 | ACTOR: GEMINI**

**Problème résolu :**
Sullivan Manifest Editor répond en bloc de texte indigeste. L'utilisateur ne sait pas quoi répondre, les suggestions arrivent avant l'analyse. Le chat démarre à vide — l'élève ne sait pas qu'il peut interagir avec Sullivan.

**Solution :**
Externalisation de la logique Sullivan dans un module dédié (ManifestSullivan.js) piloté par injection de refs.
Implémentation d'un appareil de critique structuré (Oui/Non) avec suggestions contextuelles dynamiques.
Synchronisation avec le curseur de l'éditeur pour un positionnement flottant contextuel.

**Livrables :**
- Frontend/3. STENCILER/static/js/ManifestSullivan.js
- Frontend/3. STENCILER/static/js/ManifestBox.js (refactoring)
- Frontend/3. STENCILER/static/templates/workspace.html (inclusion script)


---

## Thème 41 — Forge Student Auth

### M361 — WsForge.js : ajouter X-User-Token sur forgeScreen()
**ACTOR: GEMINI | MODE: CODE DIRECT | STATUS: ✅ TERMINÉE**

**CR — Mission M361 (WsForge Multi-Tenant)**
- Ajout du header `X-User-Token` dans l'appel `POST /api/retro-genome/generate-from-import`.
- Récupération sécurisée de la session via `localStorage`.
- Bumper de version `v=361` appliqué dans `workspace.html`.
- **Résultat** : La forge est désormais isolée par étudiant, garantissant que Sullivan travaille sur le bon projet même en environnement mutualisé.

---

## Thème 42 — Student Panel : sémantique Sujet vs Projet

### M362 — WsProjectPanel : sémantique Sujet vs Projet
**ACTOR: GEMINI | MODE: CODE DIRECT | STATUS: ✅ TERMINÉE**

### CR — Mission M362 (Student Panel Semantics)
- Modification de `render()` dans `WsProjectPanel.js` :
    - Si `session.class_id` est présent : tous les projets (`_projects`) sont basculés dans `subjects`.
    - Si `session.class_id` est absent : filtrage classique par `p.type`.
- Bumper de version `v=362` appliqué dans `workspace.html`.
- **Résultat** : Cohérence sémantique pour les élèves en classe — leurs travaux sont des "Sujets", pas des "Projets Personnels".

---

## Thème 40 — Student Flow : Drill Guard + Project Panel

### M359 — WsProjectPanel : session impersonation + projects source
**ACTOR: GEMINI | MODE: CODE DIRECT | STATUS: ✅ TERMINÉE**

### CR — Mission M359 (WsProjectPanel)
- `render()` utilise désormais `_getSession()` (impersonation-aware).
- Source de données basculée sur `_projects` (variable locale peuplée par `refresh()`).
- `fetchProjectScreens` inclut désormais le token `X-User-Token` pour autoriser la lecture des écrans.
- **Résultat** : L'affichage des projets est fluide en mode prof->élève.

### M360 — WsStitchDrill : guard content-aware
**ACTOR: GEMINI | MODE: CODE DIRECT | STATUS: ✅ TERMINÉE**

### CR — Mission M360 (WsStitchDrill)
- `show()` devient `async` et effectue un check via `/api/retro-genome/imports` avant affichage.
- Si le projet actif contient des écrans, le drill est passé (`Skipping — student has X screen(s)`).
- Persistance du drill par clic manuel sur le bouton "+" préservée.
- **Résultat** : Suppression de l'interruption intrusive au chargement du workspace pour les élèves avancés.

---

## Thème 39 — Sullivan Manifest Editor

### M358 — Sullivan ME : droits écriture manifest (apply suggestion)
**ACTOR: GEMINI | MODE: CODE DIRECT | STATUS: ✅ TERMINÉE**

**CR — Mission M358**
*   **Backend API (`sullivan_router.py`)**: Implémentation de `POST /api/sullivan/manifest-apply`.
*   **Frontend Logic (`ManifestSullivan.js`)**: Ajout d'un bouton "appliquer" par carte de suggestion.
*   **Editor Integration (`ManifestBox.js`)**: Injection de la callback `applyManifest` pour mettre à jour l'éditeur en temps réel.
*   **Résultat** : Workflow d'édition bi-directionnel entre la critique AI et le manifest opérationnel.

---

### M352 — CR (Compte-Rendu)
**STATUS: ✅ TERMINÉE | ACTOR: GEMINI**
- **Async Fix** : Passage de `extract_design_tokens` en `async def` dans `import_router.py`. La tâche de fond `extract_tokens_background` est maintenant invoquée proprement via le loop principal de FastAPI, prévenant les blocages d'event loop.
- **Archivage** : Déplacement du fichier legacy `design.md` (racine) vers `docs/04_Archives/design_stitch_legacy.md`. La Constitution (`Frontend/1. CONSTITUTION/DESIGN.md`) est désormais l'unique source de vérité stylistique.

### M353 — CR (Compte-Rendu)
**STATUS: ✅ TERMINÉE | ACTOR: GEMINI**
- **Inférence HCI** : Nouvelle route `POST /api/imports/infer-intent` implémentée.
- **Sullivan Bridge** : Utilisation de `GeminiClient` pour transformer les design tokens bruts (palette hex, typo, spacing) en intention structurée (archétype, humeur, sections suggérées).
- **Persistance Manifeste** : Les résultats sont sauvegardés dans `manifest.json["intent_inference"]`, permettant une pré-configuration intelligente du projet avant même que l'élève ne commence à câbler.
