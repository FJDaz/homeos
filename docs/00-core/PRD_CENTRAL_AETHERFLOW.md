# PRD CENTRAL : AETHERFLOW (CLEAN & PRISTINE)

**Version** : 3.0 "Deep Flow"  
**Date** : 16 février 2026  
**Statut** : RÉFÉRENTIEL IMMUABLE (POST-NETTOYAGE)

---

## 🚀 1. Vision : Le Moteur de Construction de Code Robuste

AetherFlow n'est plus seulement un orchestrateur pour HomeOS, c'est une **proposition commerciale autonome** : un bouquet d'APIs optimisées pour garantir une construction de code solide, précise et abordable.

### Le Pilier BKD (Backend Engine)
- **Objectif** : Autonomiser la phase de construction logique.
- **Moteur** : Orchestrateur multi-LLM (DeepSeek, Gemini, Groq) avec gestion AST (Surgical Edit).
- **Valeur** : Un code qui compile, qui respecte l'architecture existante et qui coûte le juste prix.

### Le Pilier FRD (Frontend Pristine)
- **Objectif** : Rendu pur et découplé.
- **Philosophie** : Un "Sanctuaire" de rendu 100% conforme à la **Constitution AetherFlow**.
- **Interopérabilité** : Une API REST JSON comme unique pont ontologique.

---

## 🧬 2. Architecture & Composants

### AetherFlow Engine (BKD)
- **Surgical Edit v2** : Modification précise via AST pour éviter la corruption de fichiers.
- **Smart Routing** : Allocation dynamique (DeepSeek pour le complexe, Groq pour la vitesse, Gemini pour le volume).
- **RAG & Context** : Enrichissement automatique par `PageIndexRetriever`.

### Sullivan Logic (Cognition)
- **Genome N0-N3** : Cartographie sémantique de toutes les interfaces.
- **UI Inference** : Capacité à dériver le frontend depuis le sens backend.

---

## 🛠️ 3. État Actuel (Clean Status)

### Infrastructure
- ✅ **Nettoyage 2026-02-16** : Suppression des bruits de session, archivage des status reports obsolètes.
- ✅ **Docs Core** : Centralisation dans `docs/00-core/`.
- ✅ **Environnement** : Workspaces identifiés et isolés.

### Fonctionnalités
- ✅ **Surgical Mode** : Opérationnel et debuggé.
- ✅ **Multi-Provider** : DeepSeek-V3 et Gemini 1.5 Pro intégrés.
- ✅ **Constitutional Enforcer** : Barrière sémantique active.

---

## 🗺️ 4. Objectifs Stratégiques (Next-Gen)

### Robustesse & Auto-Correction (LangGraph)
- **Transition** : Migration vers une orchestration par graphes pour gérer les boucles de rétroaction (Self-Healing).
- **Objectif** : Zéro erreur de syntaxe en sortie d'API.

### Solidité de Construction : DeepSeek-R1 Pre-Reasoning
L'hybridation "Raisonnement (R1) / Écriture (V3/Codestral)" est le moteur de la proposition de valeur AetherFlow.
- **Mécanisme** : Implémentation de `_reasoning_pre_pass()` dans l'orchestrateur.
- **Flux** : Plan + AST → **DeepSeek-R1** (`deepseek-reasoner`) → Bloc `[REASONING]` → Modèle d'écriture.
- **Activation** : Déclenchée par `pre_reasoning: true` dans le contexte du plan JSON.
- **Valeur** : Zéro code "fantôme", compréhension parfaite des dépendances avant toute modification.

---

## 📜 5. Constitution & Gouvernance
Toute modification doit respecter les **3 Règles d'Or** (Frontière Hermétique, Aucun Empiètement, Source de Vérité Unique).

*Référentiel maintenu par Antigravity sous supervision du CTO François-Jean Dazin.*
