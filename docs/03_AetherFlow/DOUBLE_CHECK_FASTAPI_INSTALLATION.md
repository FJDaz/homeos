# DOUBLE-CHECK FastAPI Installation & Mode Serveur

Vérification de l’installation FastAPI, des scripts de démarrage, du mode serveur et de `run_via_api`.

---

## 1. Ce qui a été vérifié

### 1.1 Stack FastAPI

- **FastAPI** : `requirements.txt` → `fastapi==0.115.0`
- **Uvicorn** : `requirements.txt` → `uvicorn==0.30.6`
- **App** : `Backend/Prod/api.py` → `app = FastAPI(...)`, CORS, routes.

### 1.2 Endpoints

| Endpoint | Statut | Usage |
|----------|--------|--------|
| `GET /health` | OK | Docker healthcheck, curl |
| `POST /execute` | OK | plan_path / plan_json, workflow PROTO \| PROD |
| `GET /` | OK | Conditionnel (frontend) |
| `POST /sullivan/search`, `GET /sullivan/components`, etc. | OK | Sullivan |

### 1.3 Démarrer l’API

- **Recommandé** : `./start_api.sh`  
  - Active le venv, vérifie le port 8000, tue un éventuel process existant, lance l’API via  
    `python -c "from Backend.Prod.api import run_api; run_api(host='127.0.0.1', port=8000)"`.
- **Alternatives** :  
  - `python -m Backend.Prod.api` (depuis la racine du projet, avec `PYTHONPATH` adapté).  
  - Docker : `docker-compose --profile api up -d` →  
    `command: ["python", "-m", "Backend.Prod.api"]`.

### 1.4 `run_api` et `__main__`

- `run_api(host, port)` dans `api.py` appelle `uvicorn.run(app, host=host, port=port)`.
- `if __name__ == "__main__": run_api()` permet d’exécuter l’API avec  
  `python -m Backend.Prod.api` (sous réserve de résolution module vs package, voir §3).

### 1.5 Mode serveur et `run_via_api`

- **Script** : `scripts/run_via_api.py`
- **Usage** :  
  - `python scripts/run_via_api.py N -q` → N× PROTO  
  - `python scripts/run_via_api.py N -f` → N× PROD  
  - `--plan`, `--base-url` optionnels.
- **Comportement** : boucle de `POST /execute` avec `plan_path` et `workflow` ;  
  timeout `httpx.Timeout(600.0, connect=10.0)` ; gestion `ConnectError` / `ConnectTimeout` / `HTTPStatusError`.  
  En cas d’erreur de connexion, la boucle s’arrête au premier échec (évite N messages « API non joignable »).
- ** Prérequis** : API déjà démarrée (ex. `./start_api.sh`).

### 1.6 Configuration

- **output_dir** : `settings.output_dir` (défaut `output`). Création dans `Settings.__init__` via `mkdir(parents=True, exist_ok=True)`.
- **Fichiers temporaires (plan_json)** : créés sous `settings.output_dir` puis supprimés après exécution.

### 1.7 Docker

- **Service** : `docker-compose` → `api`, build `Backend/Dockerfile`, port 8000.
- **Healthcheck** : `curl -f http://localhost:8000/health`.
- **Volumes** : `./Backend/Prod`, `./output`, `./logs`.  
  Plans dans l’image : `Backend/Notebooks/...` (copiés au build, non exclus par `.dockerignore`).

---

## 2. Incohérences ou points d’attention

### 2.1 `python -m Backend.Prod.api` vs package `api/`

- Il existe à la fois le **module** `Backend/Prod/api.py` et le **package** `Backend/Prod/api/` (avec `.gitkeep` uniquement).
- `python -m Backend.Prod.api` peut cibler le **package** selon l’environnement ;  
  le package n’a pas de `__main__` ni de `run_api` / `app`.
- **Recommandation** : utiliser `./start_api.sh` en priorité (invocation explicite de `run_api` via le module).  
  Si vous utilisez `-m`, vérifier que c’est bien le module `api.py` qui est exécuté.

### 2.2 `run_via_api` contre l’API en Docker

- `run_via_api` envoie un `plan_path` **relatif** au dépôt (ex.  
  `Backend/Notebooks/benchmark_tasks/test_workflow_prod.json`).
- L’API résout ce chemin par rapport à son **cwd** (process local = racine du dépôt ; Docker = `/app`).
- En Docker, les plans sont ceux **dans l’image** (ou montés). Les fichiers uniquement sur l’hôte ne sont pas vus.  
  Pour utiliser des plans hôte avec l’API Docker, monter par ex.  
  `./Backend/Notebooks:/app/Backend/Notebooks` (ou un répertoire dédié).

### 2.3 `start_api.sh` et `pkill`

- `pkill -f "Backend.Prod.api\|uvicorn.*api"` peut arrêter d’autres processus contenant ces chaînes.  
  En environnement partagé, préférer arrêter explicitement le process qui écoute sur 8000 (ex. via `lsof -ti:8000` puis `kill`).

---

## 3. Checklist rapide

- [x] `fastapi` et `uvicorn` dans `requirements.txt`
- [x] `GET /health` implémenté et utilisé par le healthcheck Docker
- [x] `POST /execute` avec `plan_path` ou `plan_json`, `workflow` PROTO/PROD
- [x] `run_api()` et `if __name__ == "__main__"` dans `api.py`
- [x] `./start_api.sh` démarre l’API (venv, port, `run_api`)
- [x] `scripts/run_via_api.py` pour N× runs via HTTP
- [x] README : API FastAPI + mode serveur documentés
- [x] Docker : service `api`, healthcheck `/health`, `python -m Backend.Prod.api`

---

## 4. Références

- `Backend/Prod/api.py` : app FastAPI, `run_api`, routes.
- `start_api.sh` : démarrage API.
- `scripts/run_via_api.py` : runs répétés via `/execute`.
- `README.md` : section « API FastAPI » et « Mode serveur ».
- `docker-compose.yml` : service `api`.
