# GENOME PEDAGOGY RAG INDEX

Ce document décrit fonctionnellement les N2 (Cellules / Features) générées par l'agent Sullivan et rendues par KIMI. 
Dans l'architecture AetherFlow, le N0 représente la Phase, le N1 l'Organe (zone d'écran), le N2 la Cellule (Feature / logique interactive), et le N3 l'Atome (composant unitaire visuel). 
Ce fichier sert de référence RAG pour l'explicabilité de la structure générée.

---

## 💊 CELLS (N2) - Features & Logique Interactive

### [n2_ir_report]
- **Sens Humain / Doc UX** : Le tableau de bord central de l'Architecture Visuelle à 3 Panels (Intentions, Implémentation, Actions). Son objectif est de "rendre visible l'invisible" en cartographiant les écarts entre les intentions du manifeste et le code généré.
- **Intent Code / Utilité** : Composant névralgique du workflow Sullivan. Il agrège les états interactifs à travers les 7 phases du refactoring (ex: *Phase 1 Inventory*, *Phase 2 Mapping*, *Phase 3 Ambiguity Scanner*). Il manipule les états d'acceptation (Core, Support, Réserve, Deprecated) via le `irState.store.js` et bloque l'exportation du génome (Phase 7: Gel) tant que 100% des intentions ne sont pas couvertes ou explicitement gérées.

### [n2_stencils]
- **Sens Humain / Doc UX** : Interface de découverte (ComponentDiscovery) des atomes et molécules générés. Présente la bibliothèque organisée (ComponentLibrary) pour choisir visuellement les briques d'interface.
- **Intent Code / Utilité** : Consommateur de l'endpoint `GET /components` et `POST /sullivan/search`. Gère l'affichage en grille (ResultsGrid), le filtrage dynamique (FilterSidebar) et l'injection du composant (drag & drop) embarquant son payload spécifique.

### [n2_session_mgmt]
- **Sens Humain / Doc UX** : Contrôle du cycle de vie du "Intent Refactoring", garantissant qu'aucune donnée ou décision de l'utilisateur n'est perdue (Undo/Redo, Timeline de décisions).
- **Intent Code / Utilité** : Pilote le State Manager (sauvegarde, reset). Implémente le pattern "État Persistant" (ex: `ir_session` progress, last_saved) décrit dans l'architecture IR pour permettre le rechargement de session.

### [n2_stepper]
- **Sens Humain / Doc UX** : Indicateur d'avancement linéaire pour guider le Workflow Sullivan étape par étape, réduisant la complexité perçue.
- **Intent Code / Utilité** : Mécanisme de routing visuel ou de changement d'état conditionné par la validation de l'étape précédente.

### [n2_layouts]
- **Sens Humain / Doc UX** : Sélection et disposition des conteneurs spatiaux de la page (les "Blueprints" ou templates).
- **Intent Code / Utilité** : Logique de grille, Flexbox ou outil de disposition permettant à l'Orchestrateur (CanvasFeature) d'injecter des éléments de manière harmonieuse.

### [n2_vision_analysis]
- **Sens Humain / Doc UX** : Retour visuel (Feedback) de l'analyse multimodale de l'IA sur une image fournie (Rapport Vision).
- **Intent Code / Utilité** : Affichage des régions d'intérêts (ROI) et du rendu de la pipeline `vision_analysis.py`.

### [n2_upload]
- **Sens Humain / Doc UX** : Point d'ingestion des assets de l'utilisateur (Drag & Drop de design).
- **Intent Code / Utilité** : Input file parser pour charger les ressources (PNG/Figma) et amorcer le pipeline d'extraction.

### [n2_chat]
- **Sens Humain / Doc UX** : Interface conversationnelle (Chatbot Sullivan) permettant l'arbitrage direct ou l'affinage des choix d'interface.
- **Intent Code / Utilité** : Widget LLM asynchrone pour échanger des payloads sémantiques avec Gemini via l'API, avec historique de conversation.

### [n2_validation]
- **Sens Humain / Doc UX** : L'étape de "Souveraineté humaine". C'est le Gating final (Decision Time) où l'utilisateur valide le consensus établi avec l'IA (Sullivan Arbiter) avant le gel du génome.
- **Intent Code / Utilité** : Validation conditionnelle (exécution de `POST /execute` ou validation de cluster `Core/Réserve`). Gère l'interface de décision (DecisionPanel, Kanban interactif) et bloque le flux si des actions orphelines (ex: Extra-Genome) sont détectées.

### [n2_zoom]
- **Sens Humain / Doc UX** : Macro/Micro navigation (Zoom in/out). Permet d'isoler un atome ou d'observer l'ensemble des Corps (Vue Top-Bottom).
- **Intent Code / Utilité** : Manipulation du ViewBox SVG (Canvas Matrix Transform) pour explorer la hiérarchie.

### [n2_export]
- **Sens Humain / Doc UX** : Déploiement et concrétisation. Traduit l'approbation humaine en fichiers réels après le "Gel du Génome".
- **Intent Code / Utilité** : Composant de terminaison (relié conceptuellement au module *Deploy*). Il wrap le `genome_hash` et génère le `manifest.json` pour la consommation par l'UI/Figma Bridge et la génération SVG finale.
