# Diag-3 : Parcours Teacher — Audit Réalisé

## Flux d'Authentification

Le parcours commence sur `login.html` ou `teacher_dashboard.html`.
- **Mécanisme** : `/api/auth/login-prof` via `auth_router.py`.
- **Sécurité** : Hachage SHA-256 local. Pas de JWT, utilisation d'un token UUID simple stocké en DB SQLite.
- **Problème Détecté** : Toute la logique d'auth est `async def` mais effectue des connexions SQLite synchrones (`_sqlite_get_user_by_name`). Risque élevé de freeze si de nombreux profs se connectent.

---

## Gestion de la Classe & Dashboard

La récupération des données dashboard (`/{class_id}/dashboard`) est complexe :
1. **Parsing Heuristique** : Le système déduit le niveau d'avancement des élèves (`milestones`) en vérifiant physiquement l'existence de dossiers `/imports` ou `/exports` sur le disque pour chaque élève.
2. **Coût I/O** : Pour une classe de 30 élèves, le backend effectue 30 x N vérifications `os.path.exists` à chaque refresh.
3. **M305 (Fix Auto-refresh)** : Le frontend a été stabilisé pour ne relancer un refresh qu'après la fin du précédent, évitant l'empilement des requêtes.

---

## Activation de Projet (Le "Freeze Point")

> [!CAUTION]
> **RISQUE DE COLLISION & CORRUPTION** (Mission 304)
> L'activation d'un projet par le prof (`/api/projects/activate`) déclenche une mise à jour de la table `students` via un `LIKE` :
> `UPDATE students SET project_id=? WHERE ? LIKE class_id || '-' || id || '%'`

- **Faille 1** : Si un élève a l'ID `blart` et un autre `blart-2`, l'activation du projet de `blart-2` peut écraser celui de `blart` à cause du joker `%`.
- **Faille 2** : Écriture concurrente sur `active_project.json`. Bien que `server_v3.py` semble gérer les accès, la rapidité des clics prof peut mener à un fichier vide si le `write` échoue.

---

## Parcours de Cadrage (Subjects)

- **Modèle M223** : Les sujets sont stockés en JSON dans `classes/{id}/subjects/`.
- **Alignement** : Globalement stable, mais déconnecté de la base `projects.db` (double source de vérité). Si on supprime un sujet sur disque, il peut rester référencé par les métadonnées élèves en DB.

---

## Recommandations V4

1. **[CRITIQUE] Sécurisation du `UPDATE`** : Remplacer le `LIKE` par une égalité stricte sur l'ID projet élève pour éviter les collisions.
2. **[IMPORTANT] Cache des Milestones** : Ne plus scanner le disque à chaque appel dashboard. Stocker le `milestone_level` en DB (table `students`) et ne le mettre à jour que lors d'événements clés (Import, Forge).
3. **[IMPORTANT] Middlewares de Sécurité** : Migrer tous les helpers `_sqlite_*` de `auth_router.py` vers un pool de threads ou les rendre purement synchrones via `def`.
4. **[UX] Feedback d'Activation** : Ajouter un verrou UI sur le dashboard prof pendant qu'une activation est en cours pour éviter les double-clics.
