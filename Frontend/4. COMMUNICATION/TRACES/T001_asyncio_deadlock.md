# trace t001 : deadlock asyncio (pipeline extraction)

## contexte
- **date** : 2026-04-29
- **mission** : m376 (stabilisation multi-images)
- **symptômes** : le pipeline d'extraction s'arrêtait indéfiniment après la détection des tokens, juste avant l'inférence de l'intention initiale (seed intent). aucun log d'erreur, simple freeze du thread de fond.

## diagnostic
le pipeline utilisait `asyncio.to_thread()` pour ne pas bloquer le serveur fastapi. à l'intérieur de ce thread, la fonction `infer_seed_intent` tentait de lancer son propre client asynchrone (`httpx.AsyncClient`) ou d'utiliser `asyncio.run()`.
**cause racine** : imbrication de boucles d'événements (nested event loops). tenter de démarrer une boucle `asyncio` dans un thread lui-même piloté par une boucle parente (fastapi) provoque des conflits de ressources ou des deadlocks sur le sélecteur i/o.

## solution
le code a été refactorisé pour supprimer toute asynchronicité à l'intérieur du thread de fond pour cette tâche spécifique :
1. création de `_run_seed_intent_sync()` : une version purement synchrone utilisant la bibliothèque `requests`.
2. appel via `asyncio.to_thread(self._run_seed_intent_sync, ...)` depuis le router.
3. ajout d'un `_save_manifest()` systématique après l'appel, garantissant que même en cas d'échec de l'ia, l'état d'avancement est persisté.

## prévention
- **règle bootstrap backend** : interdiction de `nest_asyncio.apply()`.
- **stratégie** : privilégier le code synchrone (`requests`) pour les appels api dans les workers de fond (`to_thread`).
- **monitoring** : toujours ajouter un signal `window.UxRun.log('RESULT', ...)` après une étape critique pour confirmer sa complétion côté frontend.
