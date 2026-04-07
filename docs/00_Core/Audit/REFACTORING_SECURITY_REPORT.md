# Rapport d'Audit & Stratégie de Refactoring : Projet AETHERFLOW

**Date :** 7 Avril 2026  
**Statut :** Pré-Audit Sénior  
**Document :** Vision technique et sécuritaire pour mise en conformité production.

---

## 1. Résumé Exécutif
Le projet AetherFlow présente une innovation architecturale majeure avec le concept de "Genome" (Source de Vérité émanant du code). Cependant, la codebase actuelle souffre d'une **fragmentation importante** et de **vulnérabilités critiques** liées à la gestion des secrets et à l'exposition de fonctions d'édition chirurgicale du code. Une phase de "nettoyage à sec" est impérative avant toute présentation formelle ou mise en ligne.

---

## 2. Vulnérabilités de Sécurité (Priorité Haute)

### 2.1. Gestion des Secrets et Clés API
*   **Constat :** Plusieurs scripts de test (`test_key.py`, `aether-glm.py`, `ds-r1.py`) contiennent des **clés API codées en dur** (ex: NVIDIA NIM, DeepSeek).
*   **Risque :** Fuite de credentials via le contrôle de version (Git) et exposition financière/technique.
*   **Action :** 
    *   Migrer immédiatement TOUTES les clés vers un fichier `.env` unique.
    *   Implémenter une classe `SecurityConfig` centralisée interdisant le lancement si une clé est détectée en dur dans le code.
    *   Utiliser `git-filter-repo` pour nettoyer l'historique si ces clés ont déjà été commis.

### 2.2. Édition Chirurgicale (Surgical Editing)
*   **Constat :** Le module `ApplyEngine` et les fonctions basées sur l'AST permettent de modifier le code source dynamiquement via des instructions IA.
*   **Risque :** Injection de code malveillant (RCE - Remote Code Execution) si les prompts ou les résultats LLM ne sont pas strictement validés.
*   **Action :** 
    *   Isoler l'exécution des modifications dans un sandbox Docker.
    *   Implémenter un "Human-in-the-loop" obligatoire pour toute modification persistante sur le disque.
    *   Vérifier l'intégrité de l'AST après modification via des linters automatisés (flake8/mypy) avant écriture.

---

## 3. Plan de Refactoring Architectural

### 3.1. Unification des Points d'Entrée
*   **Problème :** Prolifération de serveurs (`server_9998.py`, `server_v3.py`, `serve_frontend.py`, `server_9997_stenciler.py`).
*   **Solution :** 
    *   Désigner `Frontend/3. STENCILER/server_v3.py` comme l'**unique orchestrateur officiel**.
    *   Déplacer tous les autres serveurs dans un dossier `archives/legacy_poc/`.
    *   Standardiser le port unique et utiliser des sous-routeurs FastAPI pour les différents modules (BRS, BKD, FRD, DPL).

### 3.2. Nettoyage de la Racine (Root)
*   **Problème :** Le répertoire racine est encombré de scripts POC (`build_trace_poc.py`, `test_qwen_*.py`) et de fichiers temporaires.
*   **Solution :** 
    *   Créer un dossier `/tools/benchmarks` pour regrouper les scripts de test.
    *   Unifier les dépendances : fusionner `requirements.txt`, `requirements_updated.txt` et `requirements.hf.txt` dans un `pyproject.toml` moderne.

### 3.3. Standardisation de l'Observabilité
*   **Problème :** Usage hétérogène de `logging`, `loguru` et de fonctions `_dbg` personnalisées.
*   **Solution :** 
    *   Généraliser `loguru` pour toute la codebase.
    *   Implémenter un middleware de logging de requêtes structuré (JSON) pour faciliter l'audit de sécurité a posteriori.

---

## 4. Dette Technique & Qualité de Code

### 4.1. Typage et Contrats
*   **Suggestion :** Généraliser l'usage de Pydantic pour tous les échanges entre le Backend (Python) et le Frontend (JavaScript). 
*   **Bénéfice :** Validation automatique des inputs à la frontière de l'API, réduisant les vecteurs d'attaque par buffer overflow ou injection de type.

### 4.2. Gestion du "Genome"
*   **Suggestion :** Centraliser le stockage du Genome dans une base de données SQLite (déjà amorcé dans `db/projects.db`) plutôt que dans des fichiers JSON éparpillés (`genome_enriched.json`).

---

## 5. Recommandations pour l'Audit Sénior

1.  **Documenter le "Trust Boundary" :** Expliquer clairement où s'arrête la confiance envers l'IA et où commencent les garde-fous programmatiques.
2.  **Démonstration de Conformité :** Préparer un script `check_security.py` qui scanne la codebase pour les clés API et les imports dangereux avant chaque commit.
3.  **Audit des Dépendances :** Lancer `bandit` et `safety` sur le projet et inclure les rapports dans le dossier `/docs/00_Core/Audit`.

---
*Rapport généré par l'agent AetherFlow — Conformité Vision 2026*
