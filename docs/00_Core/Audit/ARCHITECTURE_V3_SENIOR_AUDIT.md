# 📚 AetherFlow V3 — Architecture Technique & Flux de Données

Ce document détaille la mécanique interne d'AetherFlow, de l'UI JavaScript au Middleware Python, en passant par la gestion des sessions et l'Event Loop asynchrone.

---

## 1. Gestion des Utilisateurs & Sessions
L'authentification et l'identification des entités (Classes, Users, Projets) reposent sur un **système de jetons (Tokens)**.

### Côté Frontend (JS)
*   **Source de Vérité** : `localStorage.getItem('homeos_session')`.
    *   C'est un objet JSON contenant : `token`, `user_id`, `role`, `student_id`, `class_id`, et `active_project_id`.
*   **Transport** : Tout appel API doit inclure le Header :
    ```javascript
    headers: { 'X-User-Token': session.token }
    ```
*   **Fichiers Clés** :
    *   `WsBackend.js` : Gère le passage du token lors des chats avec Sullivan.
    *   `WsProjectPanel.js` : Gère le scope des projets (`student.projects`) selon le token.
    *   `WsStitchDrill.js` : Gère l'onboarding et l'injection du token pour l'extraction de tokens design.

### Côté Backend (Python/FastAPI)
*   **Récupération** : Les routes utilisent un utilitaire (souvent dans `auth_router` ou via une dépendance FastAPI) pour extraire le `user_id` du header.
*   **Hiérarchie des IDs** :
    1.  **Token** → Identité UNIQUE du user.
    2.  **User** → Possède N projets ou appartient à une **Classe**.
    3.  **Projet** → Un dossier physique dans `/projects/{project_id}`.
*   **Fichier Clé** : `routers/import_router.py` (utilise `get_active_project_id(token)`).

---

## 2. Le Middleware & l'Event Loop
AetherFlow utilise **FastAPI** motorisé par **Uvicorn**. La force du système réside dans son asynchronisme.

### Qu'est-ce que l'Event Loop ?
L'Event Loop est le chef d'orchestre. Au lieu d'attendre (bloquer) qu'une tâche soit finie (ex: un appel à Gemini ou une lecture disque), Python "suspend" la fonction et passe à la suivante.

*   **`async def`** : Déclare une fonction qui peut être suspendue.
*   **`await`** : Indique le point de suspension volontaire (I/O, API).

### Pourquoi est-ce crucial dans le Drill ?
Lorsqu'un étudiant uploade 10 écrans :
1.  Le backend reçoit 10 fichiers.
2.  Il doit extraire les couleurs (long).
3.  Il doit appeler Gemini Vision (très long).

Si nous n'avions pas d'Event Loop, le serveur serait "gelé" pendant 30 secondes pour TOUS les utilisateurs. Grâce à `asyncio.create_task`, nous lançons ces processus en arrière-plan sans bloquer les requêtes entrantes.

### Tâches de Fond (Background Tasks)
Dans `import_router.py`, nous utilisons :
```python
asyncio.create_task(run_extraction_with_lock(active_id))
```
Cela dit au serveur : "Lance ça en parallèle, réponds immédiatement à l'utilisateur que c'est 'Started', et préviens-moi quand c'est fini."

---

## 3. Flux de Données Types

### Scénario : Changement de Projet (WsProjectPanel)
1.  **Frontend** : L'utilisateur clique sur un projet. `activateProject(id)` est appelé.
2.  **JS** : Un `POST /api/projects/activate` est envoyé.
3.  **Backend** : Met à jour le flag `active: true` dans le `manifest.json` du projet.
4.  **Backend** : Retourne OK.
5.  **JS** : `ManifestBox.showForProject(id)` est déclenché. Il recharge instantanément le manifeste du nouveau dossier projet.

### Scénario : Onboarding (WsStitchDrill)
1.  **JS** : `uploadScreen(file)`.
2.  **Backend** : Sauvegarde dans `projects/{id}/imports/`.
3.  **Backend** (`create_task`) : Déclenche `extract_tokens_background`.
4.  **Inférence** : Sullivan (Gemini Vision) analyse les pixels → crée `manifest["intent_inference"]`.
5.  **JS** (Polling) : L'étape 5 du drill interroge `/api/projects/{id}/manifest`. Dès que `intent_inference` apparaît, l'UI se débloque.

---

## 4. Maintenance & Debug
Si l'interface semble "bloquée" :
1.  **Vérifiez le LocalStorage** : Est-ce que `homeos_session` a bien un token ?
2.  **Vérifiez l'Event Loop** : Un processus lourd (`run_in_executor`) peut saturer les threads si trop d'extractions (`PIL`) tournent en même temps. (C'est pourquoi nous avons ajouté le verrou `_ACTIVE_EXTRACTIONS`).
3.  **Vérifiez le PID** : Si le backend a crashé, relancez `./start.sh` pour réinitialiser Uvicorn sur le port 9998.

---

## 5. Audit de Vulnérabilité : Points de Rupture & Freeze

L'architecture AetherFlow V3, bien que performante, présente des points sensibles où une incohérence peut "geler" l'expérience utilisateur ou saturer le serveur.

### 🔴 Risque 1 : Blocage de l'Event Loop (CPU-Bound)
*   **Cause** : Utilisation de fonctions synchrones lourdes (ex: PIL pour traiter des images, parsing de gros fichiers JSON) directement dans une route `async def`.
*   **Effet** : Le serveur ne répond plus à **aucune requête**. Même une simple page HTML ne charge plus tant que le CPU n'a pas fini son calcul.
*   **Mitigation** : Toujours déléguer les tâches synchrones à un thread pool via `run_in_executor` ou utiliser l'asynchronisme natif pour les appels API (Gemini).

### 🔴 Risque 2 : Boucles de Polling Infinies (Frontend)
*   **Cause** : Dans le Drill, nous utilisons `setTimeout(() => renderInferenceStep(), 3000)`. Si le backend répond par une erreur 500 persistante ou un JSON malformé sans gestion de "Max Retries", le navigateur boucle à l'infini.
*   **Effet** : Saturation réseau, ralentissement du navigateur, et impression de "freeze" sur l'étape de chargement.
*   **Signale Diagnostic** : Actuellement, le Drill boucle sans limite de temps. Il faudrait un "Timeout Sullivan" (ex: après 2 minutes, proposer un bouton de re-tentative).

### 🔴 Risque 3 : Incohérence de Scope (Session vs Filesystem)
*   **Cause** : La `homeos_session` côté Front peut avoir un `active_project_id` désynchronisé avec le backend (si l'utilisateur a changé de projet dans un autre onglet).
*   **Effet** : Sullivan écrit le code généré dans le Projet B alors que l'utilisateur regarde le Projet A.
*   **Incohérence Archi** : Le middleware se base sur le Header `X-User-Token` pour déduire le projet actif. Si le Front envoie un token périmé ou un mauvais ID en paramètre d'URL, la cascade d'erreurs commence.

### 🔴 Risque 4 : Ghost Processes (Processus Fantômes)
*   **Cause** : Lancer des tâches de fond (`create_task`) sans vérifier si une tâche identique tourne déjà pour le même projet.
*   **Effet** : Multiplier les appels à Gemini pour la même image, saturant le quota API et le CPU local.
*   **Status** : Corrigé partiellement via le verrou `_ACTIVE_EXTRACTIONS`, mais reste vulnérable si le serveur redémarre pendant une tâche.

### 🔴 Risque 5 : Désynchronisation Manifeste / Canvas
*   **Cause** : Le `ManifestBox` (Editor) et le `WsCanvas` (Visualisation) lisent le même `manifest.json`. Si l'un écrit sans que l'autre ne "pull" les changements, user-input peut être écrasé par Sullivan (Race Condition).
*   **Mitigation** : Implémenter un système de "Last-Modified" ou de WebSockets (Broadcast) pour prévenir le Front qu'une modif backend a eu lieu.

---

## 6. Synthèse des Diagnostics (Antigravity)

1.  **Drill Onboard** : Le point le plus critique est l'étape de chargement Sullivan. Sans garde-fou temporel, c'est une source majeure de frustration.
2.  **FastAPI Workers** : Si le serveur est lancé avec 1 seul worker (par défaut dans bcp de scripts `start.sh`), n'importe quel blocage synchrone est fatal.
3.  **JSON Parsing** : Les retours de Gemini (Sullivan) sont parfois pollués par du markdown. Un échec de `json.loads` dans le middleware peut interrompre une tâche de fond sans log visible côté Front.

---

## 7. 🧐 L'Œil du Senior : Vulnérabilités Systémiques Profondes

Si l'implémentation répond au besoin immédiat, un regard architectural "Senior" révèle des failles structurelles profondes sur le long terme :

### A. Le Mythe du Verrou Asynchrone (Multi-Worker Concurrency)
*   **La Faille** : Nous avons implémenté un `_ACTIVE_EXTRACTIONS = set()` en mémoire pour éviter les tâches en double. **C'est une illusion de sécurité** si l'application passe en production avec plusieurs "Workers" (ex: Gunicorn avec 4 workers). Chaque worker aura son propre `set()` en mémoire isolée.
*   **Risque** : `Filesystem as a Database` (utiliser des fichiers .json comme base de données) est la pire architecture pour la concurrence. Si deux workers tentent d'écrire dans `manifest.json` au même moment (race condition I/O), le fichier sera tronqué ou corrompu (JSON invalide).
*   **Remède Senior** : Il faut implémenter un verrou système distribué (ex: Redis Lock) ou utiliser une base de données ACID (PostgreSQL / SQLite) plutôt que le système de fichiers pour les états critiques (comme le manifest).

### B. Le "Split-Brain" Multi-onglet (Frontend JS)
*   **La Faille** : La "Single Source of Truth" de l'identité est le `localStorage` (`homeos_session`). Contrairement au `sessionStorage`, il est partagé entre tous les onglets.
*   **Risque** : L'utilisateur ouvre le Projet A dans l'onglet 1. Puis ouvre le Projet B dans l'onglet 2. L'onglet 2 modifie le `localStorage`. Si l'utilisateur retourne sur l'onglet 1 et clique sur "Sauvegarder", l'UI de l'onglet 1 va envoyer les données du Projet A dans le fichier du Projet B (car il lit le nouveau token/ID du `localStorage` à la volée dans `getSession()`).
*   **Remède Senior** : La session doit injecter l'ID actif dans un context mémoire JS à l'initialisation de l'onglet, et écouter l'événement `storage` pour alerter l'utilisateur ("Session modifiée ailleurs, veuillez rafraîchir").

### C. Le Vide Asynchrone (Silent Background Failures)
*   **La Faille** : Le paradigme "Fire-and-Forget" (ex: `asyncio.create_task` dans le Drill).
*   **Risque** : Si l'API Gemini répond avec une erreur 429 (Quota exceeded) ou un timeout, la fonction `extract_tokens_background` log l'erreur serveur puis **s'arrête silencieusement**. Elle n'écrira jamais `intent_inference` dans le manifeste. Côté Frontend, la boucle de polling `renderInferenceStep()` via `setTimeout` attendra indéfiniment. C'est un freeze fonctionnel insidieux.
*   **Remède Senior** : Il FAUT modéliser l'échec. Un background job doit écrire son état dans une base ou un fichier tampon : `{"status": "processing" | "completed" | "failed", "error": "..."}`. Le front doit d'abord lire cet état global avant d'espérer la donnée finale.

### D. La Confiance Aveugle dans le Disque (Missing Schema Validation)
*   **La Faille** : On manipule `manifest.json` avec de simples `json.loads` et `json.dumps`. 
*   **Risque** : AetherFlow est destiné aux étudiants. Si l'étudiant édite manuellement son manifest et introduit une erreur de syntaxe, ou supprime la clé `screens`, le backend va charger un dict Python corrompu et enchaîner les `KeyError` ou les `AttributeError` dans tout le middleware, provoquant des 500 inattendues.
*   **Remède Senior** : Même si les données viennent d'un fichier local, elles doivent passer à travers un "bouclier" Pydantic (ex: `ManifestModel.parse_file(...)`) avant de toucher la logique métier. En cas d'erreur de parsing, on log proprement et on instancie un modèle de fallback vide ou on alerte le frontend.

---

## 8. Remarques Claude — Bugs Actifs & Corrections (27 Avril 2026)

### Fix 1 : `manifest_analyze` — Route async → def (CRITIQUE)
**Symptôme** : Le serveur ne répond plus à aucune requête (y compris `/api/health`) pendant l'exécution de `/api/manifest/analyze`.

**Cause racine** : La route était `async def` mais appelait `GeminiClient.generate()` via un cascade 4 modèles × 4 tentatives × timeout=120s. Même si httpx est async, la corroutine tenait l'event loop en "attente active" en cas de modèles indisponibles (backoff + retry). En Python, une seule coroutine qui ne cède pas (`await asyncio.sleep`) peut saturer l'event loop sur worker unique.

**Fix appliqué** : Route transformée en `def` (thread pool FastAPI). L'IA tourne dans `asyncio.run()` isolé dans un thread — le serveur reste réactif.

**Fichier** : `routers/import_router.py` — `manifest_analyze()`

---

### Fix 2 : `GeminiClient` non fermé dans `_call_ai` (fuite httpx)
**Symptôme** : Chaque appel à `/api/manifest/analyze` créait un `httpx.AsyncClient` (pool de connexions TCP vers googleapis) qui n'était jamais fermé → accumulation silencieuse de descripteurs de fichiers et connexions TCP.

**Cause** : `client = GeminiClient()` dans `_call_ai` sans `finally: await client.close()`.

**Fix appliqué** : Ajout du `try/finally` + `await client.close()`. Mode `FAST` forcé pour réduire le timeout du cascade.

**Fichier** : `routers/manifest_analyzer.py` — `_call_ai()`

---

### Fix 3 : `WsProjectPanel.js` — Variables IIFE non déclarées
**Symptôme** : `ReferenceError: _projects is not defined` à chaque appel à `refresh()` — le panel projets ne se charge jamais.

**Cause** : Gemini a réécrit le fichier en retirant les déclarations de module : `_projects`, `_expandedState`, `_screensCache`, `optionalProjects` utilisées partout sans être déclarées dans le scope de l'IIFE.

**Fix appliqué** : Ajout des 4 déclarations `let` au début de l'IIFE.

**Fichier** : `static/js/workspace/WsProjectPanel.js`

---

### Fix 4 : `_call_groq` — urlopen sync dans async (partiel)
**Symptôme** : Groq appelait `urllib.request.urlopen(timeout=15)` directement dans une `async def` — blocage event loop de 15s.

**Fix appliqué** : Wrappé dans `asyncio.to_thread(_do_request)`. Contournement suffisant pour Groq seul, mais insuffisant si la cascade Gemini prend le relais (voir Fix 1).

**Fichier** : `routers/manifest_analyzer.py` — `_call_groq()`

---

### Diagnostic permanent : infer-intent 404 après redémarrage tardif
**Cause** : La route `/api/imports/infer-intent` (M353) a été ajoutée en cours de session. Le serveur en cours d'exécution au moment de l'ajout n'a pas été redémarré immédiatement → route absente du registre FastAPI pendant toute la session.

**Règle à documenter** : Après tout ajout de route Python → redémarrage obligatoire. Les pyc stales ne sont pas le seul risque — c'est le module chargé en mémoire qui compte.

---

### Observations systémiques (non régressées, à surveiller)

1.  **Cascade GeminiClient sans budget temps** : `max_retries=3` × 4 modèles × `timeout=120s` = **1920s worst case**. Pour des routes de type "manifest analyze" (non critiques), recommander un client dédié avec timeout court (15-20s) et 0 retry — accepter l'échec, pas la latence.

2.  **`asyncio.to_thread` vs `def` route** : La règle générale est plus simple que prévu : si une route fait du blocking I/O (réseau urllib, PIL, sqlite3 lourd), la déclarer `def`. FastAPI gère le thread pool. L'`async def` est réservée aux routes qui utilisent uniquement des libs vraiment async (httpx, asyncpg, aiofiles).

3.  **`_ACTIVE_EXTRACTIONS` set() en mémoire** : Verrou valide pour single-worker. En production multi-worker (Gunicorn), utiliser un fichier lock ou une table SQLite `extractions_in_progress` pour le même effet sans dépendance Redis.

4.  **Sullivan muet en impersonation** : Cause identifiée — 3 fetches dans `WsStitchDrill` manquent le header `X-User-Token` : `POST /api/imports/extract-tokens` (~l.419), `GET /api/projects/${projectId}/manifest` (~l.438), `GET /api/imports/design-tokens` (~l.450). Planifié en M354.

_Document complété par Claude Sonnet 4.6 — 27 Avril 2026._
