# 🗺️ PLAN DE RESTRUCTURATION ET SANITISATION (MAINTENANCE SENIOR)

**Objectif** : Zéro scorie à la racine, alignement sur la logique de journalisation mensuelle, et structure "Handoff-Ready" pour Max.

---

## 1. ARCHITECTURE DES ARCHIVES (Logique Mensuelle)
Tout ce qui est caduc sera déplacé dans `/archives` en suivant la même structure que la `ROADMAP_ACHIEVED`.

### `/archives/scripts/`
Déplacement des tests orphelins et versions d'agents obsolètes :
*   `test_*.py` (provenant de la racine)
*   `aether-*.py`
*   `super_diag.py`, `setup_local_qwen.py`

### `/archives/generation/`
Compression et archivage des dossiers de sortie massifs :
*   `output/` (Ne garder que les 3 derniers builds)
*   `exports/` (Purger les templates intermédiaires, garder uniquement `retro_genome`)

---

## 2. RANGEMENT DE RANG 1 (Racine "Cœur")
La racine ne doit contenir QUE des répertoires structurels ou des fichiers de gouvernance critiques.

### 📂 Répertoires de Rang 1 (Conservés)
*   `/Backend` (Production)
*   `/Frontend` (Production)
*   `/docs` (Documentation)
*   `/scripts` (Outils actifs)
*   `/db` (Données)
*   `/logs` (Traçabilité)
*   `/archives` (Historique)

### 🧹 Action "Racine Propre" (Cleanup)
*   **Scripts utilitaires** : Déplacer `serve_frontend.py`, `run_aetherflow.sh`, `start.sh`, `start_api.sh`, etc., vers `/scripts/launcher/` (ou les garder si critiques, mais avec un préfixe clair).
*   **Suppression des Toxiques** : `rm =1.0.9 =4.43.0 ga af r1 code chat gr1`.
*   **Fichiers MD** : Regrouper `DEEPSEEK.md`, `LLAMA.md`, `QWEN.md` dans `/docs/00_Core/Agents/`.

---

## 3. LOGIQUE DE RANGEMENT PAR PERTINENCE

### Les "Outils de Travail" (`/bin` local)
Les raccourcis comme `af`, `chat`, `code` ne seront plus des fichiers à la racine mais des **alias** ou des scripts dans `/scripts/cli/`.

### Les "Classes & Projets"
*   Regrouper `/classes` et `/projects` sous un répertoire parent `/workspace_data/` pour dégager le rang 1.

---

## 4. TABLEAU DE RÉÉDITION DES DOSSIERS

| Dossier Actuel | Destination Cible | Statut |
| :--- | :--- | :--- |
| `aetherflow-chat` | `/archives/legacy_agents/` | Archivé |
| `sandbox_payloads` | `/docs/06_Design_Assets/Payloads/` | Classé |
| `trouver-son-representant` | `/archives/standalone_apps/` | Archivé |
| `gemini_workspace` | `/docs/05_Operations/Agent_Contexts/` | Classé |
| `free-claude-code` | `/tools/external/` | Classé |

---

## 5. VALIDATION & EXÉCUTION
1.  **Script de Migration** : Créer `scripts/maintenance/sanitize_repo.py` pour automatiser ces déplacements sans casser les liens relatifs (vérification des imports).
2.  **Mise à jour REPO_MAP** : Générer une nouvelle carte du dépôt après nettoyage.

---
*Ce plan suit la directive de "Zéro scorie" et la logique d'archivage mensuel instaurée pour la Roadmap.*
