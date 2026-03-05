# ROADMAP V3 — BACKLOG

> Phases futures, non encore planifiées en détail.
> Entrée en ROADMAP.md quand la phase précédente est terminée.

---

## V3-C — Docker + Distribution

**Dépend de : V3-B (UnifiedExecutor)**

- `Dockerfile` : Python 3.11-slim, COPY Backend/, EXPOSE 8000, CMD uvicorn
- `docker-compose.yml` : service homeos + volume SQLite persistant
- `.dockerignore` : Frontend/, _archive/, *.bak, *.generated.*
- Test local : `docker build && docker run -p 8000:8000`
- Image publique : `docker push aetherflow/homeos:v3`
- Mode : `aetherflow -q` (FAST, génération directe)

---

## V3-D — Interfaces LLM propres (Architecture Hexagonale)

**Dépend de : V3-C**

```
Backend/Prod/interfaces/
  llm_provider.py    → ABC LLMProvider
Backend/Prod/adapters/
  groq_adapter.py
  deepseek_adapter.py
  gemini_adapter.py
  llm_router.py      → fallback chain + rate limiting
```

- Découpler l'orchestrateur des providers concrets
- Rate limiter Gemini (60 req/min)
- Timeout DeepSeek géré proprement
- Mode : `aetherflow -f` (BUILD, multi-fichiers)

---

## V3-E — SQLite Storage

**Dépend de : V3-D**

```
Backend/Prod/interfaces/
  storage.py         → ABC Storage
Backend/Prod/adapters/
  sqlite_storage.py  → SQLiteStorage
```

- Persistance Génome (état projet) en SQLite local
- Remplacement des outputs fichiers texte actuels
- `homeos.db` dans le volume Docker
- Migration des données existantes (si pertinent)
- Mode : `aetherflow -f`

---

## V3-F — IDE 4 Panneaux

**Dépend de : V3-E**

Interface web servie par FastAPI. Zéro framework JS lourd.

```
┌──────────────┬──────────────────┬──────────┬──────────────────┐
│  Explorateur │  CodeMirror 6    │ xterm.js │  Assistant CLI   │
│  (arbre HTML │  éditeur code    │ terminal │  chat AetherFlow │
│  vanilla JS) │  CDN             │ CDN      │  /api/chat       │
└──────────────┴──────────────────┴──────────┴──────────────────┘
```

- Panel 1 : arbre fichiers via `/api/files` + fetch
- Panel 2 : CodeMirror 6 (CDN) — syntax highlighting, lecture/écriture fichier
- Panel 3 : xterm.js (CDN) — output terminal, logs AetherFlow en temps réel (WebSocket)
- Panel 4 : chat simple → POST `/api/orchestrate` → retour streamed
- Cible : 1 fichier HTML + 1 fichier JS + CSS inline. Pas de build step.

---

## V3-G — Traces BRS

**Dépend de : V3-F**

Intégrer le système existant `/Users/francois-jeandazin/TRACES/` dans HomeOS V3.

**Ce qui existe déjà :**
- Extension Chrome (6 fichiers) — capture LLM interactions ✅
- `trace_brain.py` — FastAPI + SQLite, `/ingest` + `/ask` ✅
- `trace_memory.db` — peuplée ✅
- `trace_dashboard.html` — UI simple ✅

**Ce qui reste à faire :**
- Migrer `trace_brain.py` → `Backend/Prod/traces/`
- Aligner schéma `trace_memory.db` avec SQLite V3-E
- Raccorder extension Chrome à l'API HomeOS (endpoint `/api/traces`)
- ⚠️ Clé API Gemini hardcodée dans `trace_brain.py` L7 → variable d'environnement AVANT tout déploiement
- Interface `/traces` intégrée dans IDE V3-F (panel 4 ou onglet dédié)

---

## Backlog Libre

| Idée | Priorité | Notes |
|------|----------|-------|
| CLI `homeos run fast "..."` | Haute | Simplifie l'onboarding étudiants |
| Export ZIP projet | Moyenne | PRD V3 section 3.3.3 |
| FallbackLocalProvider | Basse | Peu utile en pratique — templates statiques |
| UIGenerator/FRD (UXPilot...) | Non | Hors scope V3 — Sullivan bis |
| Extension Chrome BRS autonome | Moyenne | Déjà 80% fait dans /TRACES |
| Monaco Editor | Non | CodeMirror 6 suffit |
| Glassmorphism Stenciler | Hors scope V3 | Frontend = roadmap séparée |
