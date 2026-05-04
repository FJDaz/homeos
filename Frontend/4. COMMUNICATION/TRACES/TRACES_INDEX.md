# index des traces techniques (traces)

> ce fichier répertorie les post-mortems techniques et les solutions aux bugs critiques pour éviter les régressions architecturales et optimiser le contexte rag.

| id | titre | date | impact | fichier |
|----|-------|------|--------|---------|
| T001 | deadlock asyncio (pipeline extraction) | 2026-04-29 | critique | [T001_asyncio_deadlock.md](./T001_asyncio_deadlock.md) |
| T002 | chemins relatifs db -> forge cassée | 2026-04-29 | majeur | [T002_relative_paths_db.md](./T002_relative_paths_db.md) |

---

## protocole de rédaction
chaque trace doit contenir :
1. **contexte** : mission d'origine et symptômes.
2. **diagnostic** : cause racine technique identifiée.
3. **solution** : code fix et pourquoi il fonctionne.
4. **prévention** : règle bootstrap ou garde-fou ajouté.
