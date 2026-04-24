# Handoff Dev Senior — AetherFlow / HoméOS
> Document à jour au 2026-04-24. Maintenu par FJD.

---

## Stack

- **Python 3.14** + FastAPI + uvicorn — port `9998`, `workers=1` obligatoire
- **SQLite WAL** — `db/projects.db` (chemin absolu : `/Users/francois-jeandazin/AETHERFLOW/db/projects.db`)
- **Vanilla JS** — pas de framework, templates dans `Frontend/3. STENCILER/static/templates/`
- **Auth** — header `X-User-Token` : UUID legacy ou JWT (`eyJ…`) — voir `AuthMiddleware` dans `server_v3.py`
- **Routers** — tous dans `Frontend/3. STENCILER/routers/` — montés dans `server_v3.py`

---

## Démarrage local

```bash
cd /Users/francois-jeandazin/AETHERFLOW
bash start.sh

# Vérification :
curl http://localhost:9998/api/health
```

---

## Règle critique — redémarrage

Toute modification d'un fichier dans `routers/` ou `bkd_service.py` nécessite un redémarrage complet du serveur. Une route ajoutée sans redémarrage retourne 404 même si le code est correct. Vérifier via `/openapi.json` que la route est bien enregistrée avant de tester depuis le navigateur.

---

## DB Schema (actuel)

```
users                (id UUID, name, role, token, password_hash_bcrypt, active)
students             (id slug, display, class_id, project_id, user_id FK→users)
classes              (id slug, name, subject, owner_id FK→users)
projects             (id UUID, user_id FK→users, name, type 'personal'|'subject', subject_id nullable)
subjects             (id UUID, class_id FK→classes, title, dnmade_competence, instructions)
sessions             (id, class_id, title, created_at)
session_participants (session_id, user_id, joined_at)
```

---

## Pitfalls connus

| Symptôme | Cause | Fix |
|----------|-------|-----|
| Page blanche sans erreur console | `nest_asyncio.apply()` dans un fichier importé | Supprimer nest_asyncio — interdit définitivement |
| Route retourne 404 après livraison | Serveur non redémarré | `bash start.sh` puis vérifier `/openapi.json` |
| Dashboard prof ne charge pas | Fetch sans header `X-User-Token` | Ajouter `authHeaders()` à chaque fetch |
| Freeze sur toutes les requêtes | `sqlite3.connect()` dans un contexte async | Utiliser `loop.run_in_executor(None, fn)` |
| Impersonation 404 | Route ajoutée mais serveur pas redémarré | Même cause — redémarrer |

---

## Architecture des routers

```
server_v3.py (port 9998)
├── AuthMiddleware          — résout X-User-Token → request.state.user_id
├── /static                — fichiers statiques (CSS, JS, templates)
├── routers/
│   ├── auth_router.py     — login, register, impersonate, magic-link
│   ├── class_router.py    — CRUD classes (scoping owner_id pour les profs)
│   ├── subject_router.py  — CRUD sujets pédagogiques
│   ├── bkd_router.py      — backend knowledge base
│   ├── admin_router.py    — gestion users (admin only)
│   ├── projects_router.py — CRUD projets
│   ├── workspace_router.py
│   └── ...
└── bkd_service.py         — couche DB partagée (bkd_db context manager)
```

---

## Auth — pattern standard

```js
// Frontend : toujours envoyer le token dans les headers
const session = JSON.parse(localStorage.getItem('homeos_session') || '{}');
fetch('/api/...', {
    headers: { 'X-User-Token': session.token, 'Content-Type': 'application/json' }
});
```

```python
# Backend : récupérer user_id depuis le middleware
@router.get("/api/something")
def endpoint(request: Request):
    user_id = request.state.user_id  # None si pas de token valide
    if not user_id:
        raise HTTPException(status_code=401)
```

---

## Missions en attente

| Mission | Description | Fichiers | Priorité |
|---------|-------------|----------|----------|
| M329 | Icône SVG impersonation — remplacer emoji 👁 | `teacher_dashboard.html` | 🟡 |
| M350 | Live Watch — polling status drill étudiants | nouveau fichier | 🟡 |
| M351 | Notation automatique par référentiel DNMADE | `subject_router.py` | 🟡 |

---

## Ce que FJD garde (ne pas déléguer)

- Validation visuelle de toute livraison frontend (Article 16 Constitution)
- Architecture et décisions de modèle de données
- Tout ce qui concerne NLP/HCI (BERT, Bayesian, Sullivan RL)
- Autorité esthétique DA — aucune décision visuelle sans validation FJD
