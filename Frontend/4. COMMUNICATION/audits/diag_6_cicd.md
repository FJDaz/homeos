# Diag-6 : CI/CD & Pipeline — Audit Réalisé

## Stratégie de Déploiement

- **Cible** : HuggingFace (HF) Spaces (Docker).
- **Automation** : GitHub Action `deploy-hf.yml`.
- **Mécanisme** : Push direct du dossier racine vers HF Hub via `huggingface_hub`.

---

## Conteneurisation (Dockerfile)

- **Base** : `python:3.11-slim` (Légère et sécurisée).
- **Isolation** : Mode non-root (user 1000) imposé par HF.
- **Graft d'État** : Le script `start_hf.sh` crée les dossiers `db`, `exports`, et `logs` à la volée.

---

## Risques Majeurs Identifiés (Pipeline & Runtime)

> [!CAUTION]
> **LE "SINGLE WORKER" DEADLOCK**
> Le fichier `start_hf.sh` (L23-27) lance Uvicorn avec **un seul worker** (`--workers 1`).

1. **Impact** : Combiné avec les handlers bloquants (Diag-2), cela signifie que si une seule requête LLM ou une requête SQLite lourde est en cours, **l'ensemble du système est inaccessible pour tous les autres utilisateurs**. C'est la cause technique n°1 du "Freeze Permanent" ressenti par les utilisateurs en classe.
2. **Volatilité des Données** : HF Spaces redémarre régulièrement les conteneurs (mise à jour, idle timeout). Sans volume persistant (EFS, S3, ou Supabase Sync), toutes les modifications de la table `students` ou les nouveaux projets créés sur le Space sont **perdus** à chaque déploiement.
3. **Absence de Tests** : La pipeline `deploy-hf.yml` ne contient aucune étape de validation (Pytest, Lint). Elle pousse le code tel quel.

---

## État des Scripts Utilitaires

- **Runner local** : `run_aetherflow.sh` semble être utilisé pour le développement Mac.
- **Monitoring** : `monitor_aetherflow.sh` n'est pas intégré à la boucle de CI. C'est un outil manuel.

---

## Recommandations V4

1. **[CRITIQUE] Multi-Workers / Mode Async** : Augmenter le nombre de workers (si la RAM HF le permet) ET supprimer impérativement les appels bloquants dans le code (Mission déjà initiée sur `class_router.py`).
2. **[IMPORTANT] Persistance Externe** : Centraliser la base de données sur Supabase ou une instance SQLite distante (Cloud Backup) pour éviter la perte de données au restart HF.
3. **[IMPORTANT] Healthchecks CI** : Ajouter une étape de tests unitaires et de "Build Check" dans la GitHub Action avant de déployer.
4. **[OPTIMISATION] Docker Layering** : Optimiser le Dockerfile pour ne pas re-télécharger toutes les dépendances à chaque petit changement de texte (organiser les COPY plus finement).
