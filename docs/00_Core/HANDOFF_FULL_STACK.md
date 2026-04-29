# HANDOFF FULL STACK : HoméOS V4
**Document exclusivement technique à destination du Lead Fullstack (Max)**
*Pour la vision stratégique et produit, consulter le [PRD_HOMEOS_V4.md](./PRD_HOMEOS_V4.md).*

---

## 1. Stack Technique & Environnement

L'objectif est la robustesse, la sécurité et la maintenabilité d'un socle "Pristine". Pas de frameworks Front-End superflus.

- **Backend Local** : Python 3.14 + FastAPI + Uvicorn (Port `9998`, `workers=1` exigé pour cause d'état mémoire).
- **Base de données (Local vs Cloud)** : 
  - **Local (Workspace/Dev)** : `SQLite` en mode WAL — Fichier : `db/projects.db` (Le moteur tourne en local sans dépendance externe).
  - **Cible Prod (DPL)** : Maintien de l'abstraction pour permettre la bascule vers **Supabase (PostgreSQL)** lors du déploiement cloud des forges.
- **Frontend Core** : Vanilla JS, approche par classes/modules (Pas de React/Vue), templates HTML natifs.
- **Styling** : TailwindCSS v3 (Généré) / Vanilla CSS pour les composants du Workspace (`index.css`).
- **Authentification** : Header `X-User-Token` (Géré via `AuthMiddleware` en backend).

---

## 2. Cartographie du Dépôt (Où trouver quoi)

Le dépôt est l'héritage de plusieurs transitions. Le code actif de la V4 (Le Workspace) est centralisé ici :

### Racine Backend
- `server_v3.py` : Point d'entrée de l'application. Monte les middlewares (Auth) et les routers FastAPI.
- `bkd_service.py` : Couche d'accès DB partagée (Context manager `bkd_db`). Contient les queries SQL critiques (Gestions sessions, projets).

### Architecture des Routers (`Frontend/3. STENCILER/routers/`)
C'est ici que toute la logique API (Le "Bouquet d'APIs") est hardcodée.
- `workspace_router.py` : Entrée principale pour les actions de l'interface Workspace.
- `import_router.py` : Gestion des uploads (PNG/SVG) et serving des assets (`/projects/{id}/imports/`).
- `sullivan_router.py` : Routes IA pour l'analyse du manifeste et la confrontation avec les design tokens.
- `surgical_editor.py` : Le moteur backend qui mutera le code (Forge).
- `auth_router.py`, `class_router.py`, `projects_router.py` : CRUD classique d'état utilisateur.

### Architecture Frontend (`Frontend/3. STENCILER/static/`)
- `templates/` : Fichiers HTML servis par FastAPI (ex: `workspace.html`, `teacher_dashboard.html`).
- `js/workspace/` : Le cœur de l'application client.
  - `WsProjectPanel.js` : Liste des projets, thumbnails.
  - `ManifestBox.js` : Éditeur de manifeste (Intention).
  - `WsScreenShell.js` : SVG Component Factory affichant les écrans/PNG au centre.
  - `WsForge.js` / `WsWire.js` : Logique d'appel API pour la génération et le maillage.
- `css/` : Règles CSS de base.

### Stockage des Projets
Les données générées par les utilisateurs vivent en dehors du versioning Git :
- `projects/` : Dossier contenant un sous-dossier par UID de projet.
  - `manifest.json` : La source de vérité (avec la section `design_tokens`).
  - `imports/` : Fichiers initiaux déposés par l'utilisateur.
  - `dist/` ou `src/` : Le code forgé (HTML/Tailwind).

---

## 3. Rituels & Règles de Développement

### Règle d'Or : Le Redémarrage Backend
Toute modification d’un fichier dans `routers/` ou dans `bkd_service.py` nécessite un **redémarrage complet du serveur** (`bash start.sh`). Une route nouvellement créée retournera une erreur 404 tant que uvicorn n'aura pas redémarré. 
*Tip : Valider la présence de la route via `http://localhost:9998/openapi.json`.*

### Workflow Frontend (Vanilla JS)
- L'interface manipule directement le DOM. Mises à jour isolées via des méthodes `render()`.
- **Cache Stale** : Attention aux headers, un `?v=xxx` est utilisé sur les balises `<script>` HTML pour forcer le refresh client lors de gros changements JS.
- **Requêtes Fetch** : L'injection de l'auth n'est pas magique côté client. Chaque `fetch()` doit inclure `X-User-Token`.

### Accès Concurrence DB
- Ne jamais bloquer l'Event Loop de FastAPI avec des requêtes SQL synchrones lourdes.
- Utilisez `asyncio.to_thread()` ou un executor approprié pour les inférences externes lentes (appels modèle).
- `nest_asyncio.apply()` est **strictement banni** (provoque des pages blanches silencieuses).

---

## 4. Priorités pour le Lead Fullstack (Ton Domaine)

1. **Sécurité et Identité** : Fiabiliser l'AuthMiddleware. Vérifier l'impersonation (Professeur -> Étudiant) qui a souvent eu des fuites de headers.
2. **Maintenabilité du Code "Forge"** : Structurer `surgical_editor.py` et s'assurer que le pipeline Python écrit sans écraser le travail de l'étudiant.
3. **Optimisation DB** : Garantir que SQLite en WAL mode performe bien avec les fetchs de masse du Dashboard enseignant.
4. **CI/CD & Déploiement** : Mettre en place les scripts de packaging automatisant l'envoi d'un bundle exportable "Prêt à l'emploi" ou vers Hugging Face Spaces (DPL module).

---

## 5. Conteneurisation (Docker)

Le projet est "Docker-ready" pour faciliter les déploiements reproductibles.

- **Dockerfile (Racine)** : Image globale pour l'environnement complet de travail.
- **Backend/Dockerfile** : Image optimisée pour le runtime de l'API FastAPI (utilisée par le service `api` dans compose).
- **docker-compose.yml** : Orchestre les services :
  - `api` : Le backend FastAPI sur le port `8000`.
  - `cli` : Environnement prédéfini pour les scripts d'extraction et de forge.
- **Usage recommandé** : 
  ```bash
  docker-compose up api  # Pour lancer le backend en container
  ```

---

## 6. CI/CD & Déploiement

Le déploiement est automatisé via GitHub Actions.

- **Workflow : `.github/workflows/deploy-hf.yml`**
  - Se déclenche sur chaque `push` vers `main`.
  - Effectue un `upload_folder` vers le repository **Hugging Face Spaces** (`FJDaz/homeos`).
  - Nécessite le secret `HF_TOKEN` configuré sur GitHub.
- **Workflow : `.github/workflows/deploy-student.yml`**
  - Gère les déploiements spécifiques aux projets forges des étudiants vers leurs instances respectives.

---
*Document certifié conforme — Avril 2026. Focus Q2 : Robustesse Fullstack & ArchiBert.*
