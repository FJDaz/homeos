# Analyse & Proposition : Réintégration Stenciler dans le FRD Editor

Cette analyse évalue les actifs du projet **Stenciler** (v2.0) pour identifier les fonctionnalités à haute valeur ajoutée capables de transformer le **FRD Editor** actuel d'un outil de diagnostic technique en un véritable studio de conception-réalisation.

---

## 🏗️ Analyse des Actifs Stenciler (Fabric.js Era)

Le Stenciler a validé plusieurs patterns ergonomiques qui manquent aujourd'hui au FRD Editor, lequel reste très orienté "code-after-design".

### 1. Fonctionnalités Validées & Réutilisables
*   **Fond Snapable (Grid/Layout) :** La capacité d'aligner des éléments sur une grille invisible. Indispensable pour maintenir l'harmonie sans passer par le CSS Auto-layout de Figma.
*   **Appliquer Couleur / Style :** Le sélecteur TSL (Teinte, Saturation, Luminosité) et les swatches rapides permettent une itération visuelle instantanée.
*   **Drill Down (Double-Clic) :** La capacité de descendre "dans" un composant pour en éditer les sous-éléments (organes). C'est le cœur de l'approche sémantique d'AetherFlow.
*   **Drag & Drop d'Éléments :** Pouvoir piocher dans une bibliothèque d'archétypes et les poser sur le "tarmac".

### 2. Ce qui "marche vraiment"
L'aspect **Direct Manipulation** de Fabric.js. Le fait de cliquer sur un objet et d'avoir des poignées de redimensionnement/couleur crée un sentiment de contrôle immédiat que l'inspection de l'iframe (actuelle) ne procure pas encore.

---

## 🧐 Analyse Comparative : Google Stitch

*   **Leur Force :** L'approche **Prompt-to-UI** et le format `design.md`. C'est extrêmement rapide pour générer une structure de base.
*   **Leur Faiblesse (D'après l'usage) :** L'inefficacité sur le temps long. Stitch est brillant pour le "0 à 1", mais devient frustrant pour le "1 à 100". Le manque de contrôle granulaire (pixel-perfection) et la difficulté à "câbler" réellement le backend sans passer par des abstractions complexes limitent son usage sérieux.
*   **Notre Opportunité :** HoméOS doit être le pont. **Stitch fait le croquis, HoméOS fait le plan d'architecte.**

---

## 🚀 Proposition : Le FRD Editor à "Deux Mondes"

Au lieu d'avoir un éditeur monolithique, nous proposons deux modes de travail distincts dans le même écran, switchables via le header.

### Mode A : ÉDITION (WYSIWYG / Lore Stenciler)
> **Objectif :** Modifier le look & feel sans peur du code.
*   **Interface :** Sullivan active une couche Fabric.js *au-dessus* de l'iframe ou injecte des outils de manipulation directe (GUI) dans le DOM de l'iframe.
*   **Features :**
    *   Sélection d'élément → Bulle contextuelle avec Sélecteur de couleur (Lore Stenciler).
    *   Input texte direct (on-click edit).
    *   Drag des éléments pour réordonner (Flexbox reordering automatique via Sullivan).
    *   **Nice to have :** Le fond snapable pour le layout global.

### Mode B : WIRING (Technique / Lore FRD)
> **Objectif :** Câbler l'intelligence et la bijection API.
*   **Interface :** L'interface actuelle (Wire mode, Bijection panels, Monaco Editor).
*   **Features :**
    *   Diagnostic géographique de l'IA.
    *   Assignation des routes Python aux intentions UI.
    *   Validation des promesses (Tests/CI).

---

## 🗺️ Roadmap de Convergence

| Feature | Provenance | Priorité | État |
|---|---|---|---|
| **Color Picker TSL** | Stenciler | **P1** | À migrer vers Drawer Sullivan |
| **Direct Text Edit** | Concept | **P1** | Sullivan Command |
| **Drill Down View** | Stenciler | **P2** | Navigation sémantique |
| **Snap-to-Grid** | Stenciler | **P3** | Layout Engine |

---
*Document d'analyse stratégique — HoméOS v3*
