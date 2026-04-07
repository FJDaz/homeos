# Rapport Stratégique : Intégration de Google Stitch via MCP (Model Context Protocol)

**Emplacement** : /docs/02_Sullivan/Analyses  
**Date** : 3 avril 2026  
**Auteur** : Gemini CLI (AetherFlow Orchestrator)

---

## 1. Introduction au Protocole MCP de Google Stitch
Stitch est l'outil de design AI-native de Google. Son intégration avec le **Model Context Protocol (MCP)** permet à un agent IA (comme Sullivan) d'interagir directement avec le canevas de design, les tokens et le code généré sans passer par des exports de fichiers manuels.

---

## 2. Capacités Exposées par le Serveur MCP Stitch

L'implémentation actuelle (notamment via `@_davideast/stitch-mcp`) expose des outils et ressources critiques pour l'écosystème AetherFlow :

### A. Outils d'Action (Tools)
- **`get_screen_code`** : Extraction directe du code HTML/Tailwind/CSS d'un écran spécifique.
- **`generate_screen_from_text`** : Création d'un nouvel écran à partir d'un prompt sémantique.
- **`edit_screen`** : Modification d'un écran existant via des instructions textuelles.
- **`get_project_data`** : Lecture de l'arborescence du projet (écrans, composants, hiérarchie).

### B. Ressources de Contexte (Resources)
- **Design DNA** : Accès programmatique aux palettes de couleurs, échelles typographiques et tokens sémantiques.
- **Assets** : Récupération des URL des ressources visuelles utilisées dans la maquette.

---

## 3. Opportunités d'Intégration pour AetherFlow / HomeOS

L'adoption du protocole MCP transformerait radicalement le pipeline actuel de la codebase :

### A. Suppression du "Goulot d'étranglement" de l'Import
Sullivan peut désormais **"aspirer"** le code directement depuis le cloud Google sans fichiers intermédiaires.

### B. Synchronisation Temps-Réel du Design System
Sullivan interroge le **Design DNA** de Stitch pour garantir que chaque "Graft" respecte les tokens exacts définis visuellement.

### C. Mode Front-End Engineer (FEE) Augmenté
Utilisation des métadonnées d'intentions de Stitch pour générer des animations **GSAP** précises et automatiser le câblage (Routes/Navigation).

---

## 4. Workflow Bidirectionnel : Le "Loop" sémantique

Il est possible d'envisager un flux aller-retour où Stitch sert de **"GPU Graphique"** déporté :

1.  **BRS (Brainstorm)** : L'intention humaine est définie.
2.  **PUSH (DESIGN.md)** : Sullivan envoie le contenu du `DESIGN.md` à Stitch via `generate_screen_from_text`. Stitch "cristallise" visuellement les intentions.
3.  **VISUAL DESIGN** : Le design est affiné dans l'interface native de Stitch (cloud).
4.  **PULL (Code)** : Sullivan récupère le squelette HTML/Tailwind via `get_screen_code`.
5.  **FORGE (AetherFlow)** : L'implémentation finale (logique complexe, API, Surgical Edit) est réalisée dans le Workspace AetherFlow.

**Bénéfice** : On profite de la puissance d'imagination graphique de Stitch tout en gardant la maîtrise technique et chirurgicale d'AetherFlow.

---

## 5. Stratégie d'Implémentation Recommandée

| Étape | Action Technique | Bénéfice |
| :--- | :--- | :--- |
| **1. Bridge MCP** | Configurer le proxy `@_davideast/stitch-mcp` avec API Key. | Accès bidirectionnel aux outils. |
| **2. Module `stitch_loop.py`** | Créer un orchestrateur pour envoyer le `DESIGN.md` comme contrainte de prompt. | Cohérence sémantique forcée. |
| **3. Sullivan FEE** | Apprendre à Sullivan à choisir entre "Coder" ou "Demander un Design" à Stitch. | Optimisation du coût cognitif. |

---

## 6. Conclusion
L'intégration de Stitch via MCP fait d'AetherFlow le **moteur d'exécution** d'un système de design cloud. Stitch devient l'imaginaire graphique, et AetherFlow la réalité technique.

---
*Document mis à jour pour inclure les protocoles d'envoi et de bouclage (Loop).*
