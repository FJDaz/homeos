# Diag-7 : Moteur AetherFlow — Audit Réalisé

## Orchestration & Heartbeat

- **Cœur du système** : `bkd_service.py` et `server_v3.py`.
- **Mécanisme Pulsé** : `SullivanPulse` assure la vitalité des agents en arrière-plan.
- **RAG (Retrieval Augmented Generation)** : Sullivan utilise un index LlamaIndex (`docs/02_Sullivan`) pour rester aligné sur la doctrine AetherFlow.

---

## Intégrité de la Logique Métier

- **Surgical Editor** : Utilisation de parseurs AST (Python) et Acorn (JS) pour modifier le code sans tout réécrire. C'est la force du moteur V3.
- **Gouvernance des Projets** : Le système de mapping `Token -> Student -> ProjectPath` est ingénieux mais fragile car dispersé entre `bkd_service` et les overrides de `server_v3`.

---

## Défaillances Systémiques (The "V3 Wall")

> [!IMPORTANT]
> **Désynchronisation de la "Source de Vérité"**
> Il existe deux versions de `get_active_project_id`. L'une consulte la DB, l'autre (`server_v3.py` L237) force la lecture d'un fichier JSON global.
- **Risque** : Un élève pourrait accidentellement écrire dans le projet d'un autre si le serveur utilise l'override JSON au mauvais moment.

> [!CAUTION]
> **Crashes RAG & Event Loop**
> La fonction `exec_query_knowledge_base` utilise `asyncio.run()`. Dans un environnement FastAPI `async`, cela déclenche une erreur fatale immédiate si appelé depuis un thread principal.

---

## Vision pour la Refonte V4

Le diagnostic complet des 7 phases pointe vers une conclusion unique : **AetherFlow a atteint les limites de l'architecture "Single-File + SQLite Sync"**.

### Les piliers de la V4 :
1. **[BASE] Unification Strict** : Un seul `ServiceManager` gérant les accès DB et Fichiers avec des verrous (Locks) globaux.
2. **[PERF] Full Async / No Blocking** : Conversion intégrale des 16+ routers en handlers synchrones (`def`) gérés par le thread pool de FastAPI, ou asynchrones purs (`async def`) avec un driver SQLite asynchrone (ex: `aiosqlite`).
3. **[RESILIENCE] Multi-Workers Ready** : Élimination des états globaux en mémoire (`_ACTIVE_PROJECT_ID`) au profit d'une persistence session/stateless.
4. **[AI] Streaming & Feedback** : Généralisation du streaming SSE (Server-Sent Events) pour toutes les interactions IA (Sullivan, Kimi, FEE).

---

## Conclusion du Diagnostic
Le système est **bienséant mais instable**. Les fondations (DB, Projets) sont saines mais le câblage (Backend Handlers, Sync I/O) est défaillant. La V4 devra être une mission de **Surgical Refactoring** focalisée sur la stabilité de l'Event Loop.
