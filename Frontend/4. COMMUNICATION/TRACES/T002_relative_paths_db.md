# trace t002 : chemins relatifs db -> forge cassée

## contexte
- **date** : 2026-04-29
- **mission** : maintenance structurelle
- **symptômes** : la forge retournait des erreurs 404 lors de la lecture des fichiers sources, bien que les fichiers soient présents sur le disque. les logs montraient des chemins du type `projects/id/projects/id/imports/...`.

## diagnostic
incohérence dans la gestion des chemins (paths) entre les différents composants :
- **extraction** : écrivait des chemins relatifs dans le `manifest.json`.
- **db (table projects)** : stockait parfois des chemins absolus, parfois relatifs selon le point d'entrée (prof vs élève).
- **forge** : concaténait `PROJECTS_DIR` avec le chemin stocké sans vérifier si celui-ci était déjà absolu.
**cause racine** : absence de standardisation des URIs de ressources dans la base de données et le manifest, entraînant des duplications de préfixes lors des jointures logiques.

## solution
1. **standardisation** : tous les chemins stockés en base de données et dans le manifest sont désormais forcés en **absolu** lors de l'écriture (via `Path(p).absolute()`).
2. **validation** : ajout d'un utilitaire de résolution de chemin qui vérifie l'existence avant toute opération de forge.
3. **fix db** : migration chirurgicale des entrées corrompues dans la table `projects`.

## prévention
- **règle backend** : toujours utiliser `pathlib.Path` pour manipuler les chemins.
- **principe** : "store absolute, serve relative". les APIs de serving doivent convertir le chemin absolu en URL publique, mais la logique interne ne doit travailler qu'avec des références immuables.
- **test** : un projet créé via l'interface prof et un projet créé via l'auto-inscription élève doivent désormais avoir le même format de `path` en DB.
