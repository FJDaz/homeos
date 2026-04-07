# [Mission 207] — Implémentation du Module Backend Multi-Agents

## User Review Required

> [!CAUTION]
> **REFONTE DU LAYOUT** : Le passage à un terminal double et une colonne Architecte dédiée va réduire l'espace du Canvas. Nous devons nous assurer que le mode "Toggle" permet de revenir à la vue Stenciler pure facilement.

> [!IMPORTANT]
> **SYSTÈME DE TITRAGE** : L'auto-titrage basé sur la Roadmap nécessite que Sullivan analyse la RM en début de session pour identifier les missions "actives".

## Proposed Changes

### [UI/UX] Layout Sullivan V3 (Frontend)

#### [MODIFY] [workspace.html](file:///Users/francois-jeandazin/AETHERFLOW/Frontend/3.%20STENCILER/static/templates/workspace.html)
- Créer une structure `grid-cols-[250px_1fr_300px]` pour supporter les trois colonnes (Files | Architect/Editor | Worker).
- Implémenter le `SplitTerminal` en bas avec deux `div` scrollables indépendantes.
- Ajouter un sélecteur de "Rôle" sur chaque bulle de chat pour confirmer quel agent a répondu.

#### [NEW] [WsBackend.js](file:///Users/francois-jeandazin/AETHERFLOW/Frontend/3.%20STENCILER/static/js/workspace/WsBackend.js)
- Gérer l'état de l'explorateur de fichiers.
- Orchestrer les trois flux de chat simultanés.

---

### [Logic] Cascade & History (Backend)

#### [MODIFY] [bkd_service.py](file:///Users/francois-jeandazin/AETHERFLOW/Frontend/3.%20STENCILER/bkd_service.py)
- Étendre `SullivanArbitrator` pour supporter les rôles : `architect`, `architect_second`, `documentalist`, `worker`.
- Implémenter la logique de cascade (Fallback priority list).

#### [MODIFY] [projects.db](file:///Users/francois-jeandazin/AETHERFLOW/db/projects.db)
- Ajouter une table `conversations` : `(id, project_id, role, title, timestamp, content_json)`.

#### [NEW] [HistoryManager.py](file:///Users/francois-jeandazin/AETHERFLOW/Backend/Prod/sullivan/history_manager.py)
- Script dédié au titrage automatique via analyse des patterns Roadmap (regex `M\d+`).

## Open Questions

1. **Combien d'onglets simultanés** pour l'historique ? (Je suggère un "Quick-Switcher" affichant les 5 derniers, avec un bouton "Voir tout").
2. **Priorité de l'Ouvrier** : Souhaitez-vous que l'Ouvrier puisse "voir" la conversation de l'Architecte automatiquement, ou doit-on lui envoyer manuellement les instructions ?

## Verification Plan

- Test de switch entre vue "Visual/Stenciler" et vue "Architect/Backend".
- Simulation d'un échec API pour vérifier la cascade vers le modèle secondaire.
- Vérification que le terminal double colonne ne casse pas le responsive vertical.
