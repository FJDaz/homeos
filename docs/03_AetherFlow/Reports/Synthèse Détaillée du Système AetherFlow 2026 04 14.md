# Synthèse Détaillée du Système AetherFlow

Cette synthèse documente l'architecture actuelle tout en intégrant les causes racines des blocages identifiés.

## 🗄️ Couche Données (DB)
- **Moteur** : SQLite (`db/projects.db`).
- **Tables Clés** :
    - `students` : Stocke le `project_id` actif et la `milestone`.
    - `projects` : Registre des chemins physiques des projets.
    - `users` : Mapping `token` ➔ `user_id`.
- **Diagnostic Associé** :
    > [!CAUTION]
    > **Bug 1 (Connection Leak)** : `bkd_service.py` ne ferme pas ses connexions dans `get_active_project_path()`.
    > **Bug 4 (Rollback Silencieux)** : `class_router.py` manque de `commit()` explicite sur les batchs `executemany`.

## ⚙️ Serveur & Orchestration (Backend)
- **Framework** : FastAPI (`server_v3.py`) sur port 9998.
- **État Global** : `active_project.json` (mémoire tampon pour le projet "en focus").
- **Middleware** : `AuthMiddleware` (Injection de `request.state.user_id` via `X-User-Token`).
- **Diagnostic Associé** :
    > [!WARNING]
    > **Bug 2 (Race Condition)** : Écritures concurrentes sur `active_project.json` sans verrou (`flock`), corrompant le fichier.
    > **Bug 3 (Désynchronisation)** : L'activation d'un projet par le prof (sans token) ne met pas à jour la table `students`, créant un conflit entre le JSON global et la DB élève.

## 🎨 Interface & Dynamique (Frontend)
- **Techno** : Vanilla JS + GSAP (Animations) + HoméOS Design System.
- **Composants Workspace** : `WsCanvas.js`, `WsWire.js`, `WsStitchDrill.js`.
- **Diagnostic Associé** :
    > [!IMPORTANT]
    > **Bug 5 (Refresh Storm)** : Accumulation d'intervalles d'auto-refresh dans le Dashboard Teacher.
    > **Bug 6 (Séquençage Bloquant)** : Absence de timeout sur `isCanvasEmpty()` dans le Drill Stitch.

## 🤖 Agents & Intelligence
- **Groq (Architecte)** : Expert contexte long (128K), routage des missions complexes (ga).
- **Gemini (Ouvrier)** : Artisan UI, exécution rapide des tâches unitaires.
- **Sullivan (Arbitre)** : Pulse de diagnostic et RAG (PageIndex).
- **Intents** : Système de mapping BRS ➔ Code via `IntentMapper`.

## 🔄 Workflows (WF)
1. **Pipeline AetherFlow** : `BRS` (Design Thinking) ➔ `BKD` (Archi) ➔ `FRD` (Code) ➔ `DPL` (Ops).
2. **Loop Stitch** : Cycle de PUSH/PULL entre le genome local et l'interface Stitch via MCP.

---

# Plan de Correction (Prochaine Étape)

| Mission | Acteur | Scope | Objectif |
| :--- | :--- | :--- | :--- |
| **M303** | QWEN | `bkd_service.py` | Fix Connection Leak + `flock` sur JSON. |
| **M304** | QWEN | `projects_router.py` | Synchro `activate` ➔ DB `students`. |
| **M305** | GEMINI | HTML/JS | Guards sur intervals + Timeouts fetch. |

**Validation** : Ces missions doivent être inscrites dans `ROADMAP.md` pour exécution.
