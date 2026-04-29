# 🚀 Plan de Présentation : HoméOS V4 & Collaboration Max

**Objectif** : Onboarding de Max (Lead Dev Senior) sur la vision stratégique, l'architecture actuelle et la répartition des pôles d'excellence.

---

## 📅 Introduction : HoméOS V4 — L'Artisanat Augmenté
*   **Vision** : "Atelier de haute-couture numérique". Passage du *Prompt-to-Nothing* au *Design-First Entry*.
*   **Actualité Commerciale** : 
    *   **M2i** : Déjà programmé, déploiement imminent.
    *   **Cegos** : Démarrage en Juin (expérimentation safe en classe).
    *   **Terrain** : Validation en milieu scolaire / épreuves réelles.

## 🔍 Constats & Défis (Le "Pourquoi")
*   **Coût de l'Inférence** : Problèmatique majeure pour le public étudiant (formation massive).
*   **Latence API** : Temps de réponse parfois incompatibles avec le flux créatif.
*   **Réticences Environnementales** : Pression écologique dans l'enseignement (nécessité de modèles frugaux).

## 🛠️ Réponses Techniques : Le Bouquet d'APIs & Mode Manuel
*   **Orchestration** : Bouquet d'APIs hybride (Archi + Ouvrier).
*   **Gouvernance (Constitution AetherFlow)** :
    *   **Architecte (Claude)** : Conception et validation.
    *   **Ouvrier (Gemini/TinyLLMs)** : Exécution et maintenance.
*   **Traçabilité** : Logique `ROADMAP.md` / `ROADMAP_ACHIEVED.md` comme source de vérité.

## 🏗️ Segmentation des Phases (L'Espace de Travail)
1.  **Phase TRACES (Cadrage/BRS)** : Extraction de l'intention et du génome (cf. `/Users/francois-jeandazin/TRACES`).
2.  **Phase Workspace (Frontend Principal)** : L'entrée métier pour l'étudiant/créateur.
3.  **Phase Backend (Mise en scène Mode Manuel)** :
    *   Browser left / Archi / RM / Ouvrier.
    *   Terminaux bas pour les documentalistes.

## 👤 Rôle de Max : Le Gardien de la Structure (Lead FullStack)
Max prend en charge la solidité et la pérennité du système :
*   **Architecture** : Mise en place d'une structure **Hexagonale**, code **Pristine**.
*   **Core Systems** : Base de données, Sécurité, Stabilité.
*   **DPL (Deployment)** : Module de mise à disposition (Mise en œuvre du CI/CD Hugging Face, évolution vers un déploiement dynamique).

## 🧠 Focus FJD : Innovation NLP/UX (Le Lab)
François-Jean se concentre sur l'intelligence et la forme :
*   **NLP / HCI** : Transition **ArchiBERT** (BERT moderne + LLM Tiny) pour compresser le contexte et réduire les coûts.
*   **UX / UI** : Module **FEE** (Frontend Engineering Engine), Système Typo (Univers LT), Sullivan Expert Design.

---

### 🔥 Priorité Immédiate : Éprouver ArchiBERT
*   Validation du pipeline BERT (E5-small) pour la compression du contexte long.
*   Test sur stack local low-end.
