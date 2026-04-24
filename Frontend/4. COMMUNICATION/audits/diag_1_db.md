# Diag-1 : Fondations DB — Audit Réalisé

## Inventaire DB

### 1. `projects.db` (Principal)
Fichier local : `/Users/francois-jeandazin/AETHERFLOW/db/projects.db`

**Schéma Réel (Observé) :**
- **users** : `id (PK)`, `email`, `password`, `role`, `token`, `created_at`
- **classes** : `id (PK)`, `name`, `teacher`, `created_at`
- **students** : `id`, `class_id`, `display`, `nom`, `prenom` (PK: id, class_id)
- **projects** : `id (PK)`, `name`, `student_id`, `class_id`, `created_at`
- **subjects** : `id (PK)`, `class_id`, `title`, `content`, `created_at`
- **conversations** : `id (PK)`, `user_id`, `messages`, `created_at`

### 2. `metrics.db`
Fichier local : `/Users/francois-jeandazin/AETHERFLOW/db/metrics.db`
- **ai_calls** : Journalisation des appels LLM (provider, model, latency, success).

---

## Migrations vs Réalité

> [!CAUTION]
> **DIVERGENCE MAJEURE DÉTECTÉE**
> Le code de `bkd_service.py` (Sullivan BKD) définit un schéma (`init_bkd_db`) qui n'est **PAS** appliqué sur le fichier `projects.db` actuel.

| Entité | Attendu (code bkd_service) | Réel (disque) | Statut |
| :--- | :--- | :--- | :--- |
| **students** | `project_id`, `milestone` | **ABSENTS** | 🔴 Critique |
| **projects** | `path` | **ABSENT** | 🔴 Critique |
| **conversations** | `project_id`, `role`, `title` | `user_id`, `messages` | 🔴 Incohérent |
| **classes** | `subject` | `teacher` | 🟠 Décalage |

**Constat** : Le système tourne sur un schéma "Legacy" (probablement issu de la V2 ou d'une branche pré-Stenciler V3) alors que la logique métier Python attend des colonnes de suivi (milestones, project_id) qui n'existent pas en base.

---

## Orphelins et Incohérences

1. **Désynchronisation Physique/Logique** :
   - Des dossiers projets existent dans `/projects/` mais n'ont aucune entrée dans la table `projects` :
     - `dnmade1-2026-blart-samuel/`
     - `dnamde3-serre-lilou-.../`
     - `51172791/`
   - Ces projets sont "invisibles" pour le dashboard professeur.

2. **Désynchronisation Students/Active** :
   - La table `students` ne possédant pas de colonne `project_id`, le lien entre un élève et son projet repose entièrement sur la table associative `projects` (via `student_id`).
   - Cependant, le `student_id` dans la table `projects` est souvent vide ou incohérent avec les imports récents.

---

## Sources de Vérité Conflictuelles

1. **Projet Actif** : Stocké dans `active_project.json` (`active_id`). Lu par `bkd_service.py`. La DB `projects.db` n'a aucune notion de "global active project".
2. **Auth / User ID** : Géré par `AuthMiddleware` dans `server_v3.py` via la table `users`. Mais la logique métier (`class_router.py`) utilise souvent des identifiants `student_id` qui ne sont pas mappés formellement aux `users.id` dans toutes les routes.

---

## Recommandations V4

1. **[CRITIQUE] Unification du Schéma** : Aligner la DB sur les besoins de `bkd_service.py` (ajouter `project_id`, `milestone` à `students` et `path` à `projects`).
2. **[IMPORTANT] Migration Formelle** : Créer un script de migration qui répare les colonnes manquantes sans perdre les données `users` existantes.
3. **[IMPORTANT] Nettoyage Physique** : Script de réconciliation pour recréer les entrées DB manquantes pour les dossiers présents dans `/projects/`.
4. **[COSMÉTIQUE] Suppression Legacy** : Supprimer les tables orphelines (ex: `subjects` si géré par JSON des classes).
