# Diag-2 : Backend & Routes — Audit Réalisé

## Architecture Globale

Le serveur AetherFlow V3 (`server_v3.py`) repose sur **FastAPI** avec un montage granulaire de plus de 15 routeurs spécialisés (Mission 184).

**Points de passage critiques :**
1. `orchestrator.py` : Entrée principale du moteur de génération.
2. `bkd_service.py` : Coeur métier (Prompts, RAG, Accès disques).
3. `routers/` : Exposition API (Stitch, Class, BKD, Workspace, etc.).

---

## État des Handlers (Async vs Sync)

> [!WARNING]
> **BLOQUAGES DE L'EVENT LOOP**
> Malgré la mission M306, plusieurs routeurs centraux utilisent toujours des patterns `async def` pour effectuer des appels SQLite synchrones et bloquants.

- **`bkd_router.py`** : Les routes `/projects` (L146) et `/conversations` (L234) sont `async` mais ouvrent des connexions SQLite bloquantes sans `executor`.
- **`class_router.py`** : Correctement migré en `def` (sync) ou protégé par des garde-fous, mais le fallback DB (L45) est redondant avec `bkd_service`.
- **`server_v3.py`** : L'AuthMiddleware (L122) utilise `run_in_executor` (Correct), mais le HealthCheck (`/api/health`) est bloquant.

---

## Alignement avec les Contrats API

1. **Incohérence des Intents** : Le rapport `API_ARCHETYPAL_INFERENCE.md` propose une détection automatique des APIs (FS List, FS Save) basées sur l'UI, mais le code actuel utilise encore des endpoints "verbeux" et manuels (`/api/bkd/file`, `/api/bkd/projects`).
2. **Double Emploi** : `/api/health` dans `server_v3.py` et `/api/evaluation` dans `class_router.py` lisent tous deux la base `classes` avec des logiques de parsing légèrement différentes.

---

## Dette Technique & Code Mort

1. **Mission de Cleanup Avortée** : La mission `V3A` (Backend Cleanup) a échoué à supprimer `apply_generated_code()` car ce bloc reste importé par les workflows `proto.py` et `frd.py`. Ces workflows de "transition" polluent la structure V3.
2. **Fallbacks Multiples** : Il existe au moins 3 implémentations de connexion à `projects.db` dispersées dans :
   - `bkd_service.py` (`bkd_db_con`)
   - `class_router.py` (`supabase_db_con` fallback)
   - `server_v3.py` (Inline local connect)

---

## Recommandations V4

1. **[CRITIQUE] Standardisation des Handlers** : Appliquer systématiquement le pattern `def` (sans async) pour tous les handlers touchant à SQLite, confiant la gestion du thread pool à FastAPI (Worker Threads).
2. **[IMPORTANT] Centralisation du DB Manager** : Supprimer toutes les ouvertures de connexion redondantes et n'utiliser **QUE** le context manager de `bkd_service.py`.
3. **[STRATÉGIQUE] Migration des Intents** : Implémenter le "Functional Signature Recognition" pour que le backend expose des routes génériques d'archétypes (FS, DB, Auth) au lieu d'APIs ad-hoc.
4. **[CLEANUP] Purge des Workflows V2** : Migrer les dépendances de `proto.py` et `frd.py` vers `ApplyEngine` pour enfin supprimer les 5000+ lignes de code mort identifiées dans `V3A`.
