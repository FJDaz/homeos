# 🔍 AUDIT D'INVENTAIRE ET HYGIÈNE DU DÉPÔT
**Date :** 2026-04-24
**Statut :** Rapport d'Audit Pré-Nettoyage
**Cible :** Racine du projet et répertoires de stockage

---

## 1. DIAGNOSTIC DE "POLLUTION" (Dette de Fichiers)
L'analyse montre une accumulation de fichiers orphelins et de scories de développement qui ralentissent l'indexation et la clarté du projet.

### 🛑 Fichiers Toxiques / Erreurs (À supprimer)
*   **`=1.0.9`, `=4.43.0`** : Reliquats de mauvaises installations de packages.
*   **`ga`, `gr1`, `r1`, `af`, `code`, `chat`** : Fichiers orphelins sans extension à la racine.
*   **`server.log`** : Log racine redondant (les logs sont centralisés dans `/logs`).

### ⚠️ Scripts Dispersés (À archiver/déplacer)
*   **`test_*.py` (x18)** : Une multitude de scripts de test à la racine (`test_kimi_nim.py`, `test_qwen_free.py`, etc.).
*   **`aether-*.py`** : Versions expérimentales des agents (`aether-glm.py`, `aether-r1.py`).
*   **`setup_local_qwen.py`, `qwen_cli.py`, `fix_llama_index.py`** : Scripts d'utilité ponctuelle.

### 📦 Volumes de Stockage Mort (À purger)
*   **`output/`** : Contient ~60 dossiers de phases de build passées (`phase6`, `phase23`, `v3b1`). Poids mort important.
*   **`exports/`** : Des centaines de SVGs générés (`template_20260304_...`). Seuls les fichiers dans `/retro_genome` et les derniers exports valides sont utiles.
*   **`aetherflow.egg-info/`** : Métadonnées de packaging inutiles en développement local.
*   **`__pycache__/`** : Cache bytecode Python à purger.

---

## 2. INVENTAIRE DES ACTIFS "CORE" (À protéger)
Ces répertoires constituent le moteur vivant d'AetherFlow.

### 💎 Source Code & UI
*   **`Frontend/3. STENCILER/`** : L'application Stenciler active, ses templates et son JS.
*   **`Backend/Prod/`** : Le moteur de production (Sullivan, Auditor, Models).
*   **`homeos/`** : La logique métier de HomeOS.

### 🏗️ Infrastructure & Gouvernance
*   **`db/projects.db`** : Base de données active (Critique).
*   **`scripts/`** : Centralisation des outils (doit devenir le seul lieu pour les scripts utilitaires).
*   **`GEMINI.md`, `CLAUDE.md`, `ROADMAP.md`** : Fichiers de pilotage des agents.
*   **`start.sh`, `pyproject.toml`, `.env.example`** : Configuration système.

---

## 3. STRATÉGIE DE REMÉDIATION PROPOSÉE
1.  **Phase 1 (Scripts)** : Déplacer tous les `test_*.py` et `aether-*.py` dans un dossier `archives/scripts_legacy/`.
2.  **Phase 2 (Scories)** : Suppression définitive des fichiers `=` et des orphelins sans extension.
3.  **Phase 3 (Volumes)** : Purge de `output/` (ne garder que les logs récents) et de `exports/` (ne garder que les templates de référence).
4.  **Phase 4 (Indexation)** : Mise à jour du `.gitignore` pour éviter la réapparition de ces fichiers.

---
*Rapport généré par Gemini CLI pour le suivi de maintenance AetherFlow.*
