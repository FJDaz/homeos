# 🌌 VISION : FEE POPOVER (MODE "CAMERA RAW" UI)

> Ce document définit l'architecture et la vision du mode **Front End Experience (FEE)** en tant que surcouche immersive du Workspace HoméOS.

---

## 1. Le Concept : L'UI en Post-Production
Inspiré par le filtre **Camera RAW** d'Adobe Photoshop, le mode FEE n'est pas un outil de construction, mais un outil d'**étalonnage de l'interactivité**. 
Il s'ouvre en **popover plein écran** au-dessus du layout standard pour permettre un focus total sur la "sensibilité" du mouvement (GSAP, Shaders, Shaders P5.js, Interactivité haptique).

## 2. Architecture du Layout (Modèle BKD FRD / Mission 208)

Le layout reprend la structure tripartite robuste stabilisée lors de la Mission 208 du Backend FRD :

### ⬅️ GAUCHE : L'Explorateur de Structure (Triggers)
*   **Rôle** : Identifier les cibles de l'animation.
*   **Contenu** : 
    *   Arborescence filtrée des éléments porteurs de `data-af-id`.
    *   Indicateurs visuels (LEDs) pour les éléments possédant déjà une timeline GSAP.
    *   Sélecteur de "State" (Initial, Hover, Click, Scroll-Trigger).

### 🖥️ CENTRE : Le Labo Photo (Iframe Preview)
*   **Rôle** : Rendu "Pristine" en temps réel.
*   **Contenu** : 
    *   Iframe isolée avec injection dynamique de code (`postMessage`).
    *   **Hot-Reload Temporel** : Modification des paramètres de courbe (easing) sans rafraîchissement complet de la page.
    *   Contrôleurs de lecture (Play/Pause/Rewind/Slow-Mo) pour déboguer les micro-interactions.

### ➡️ DROITE : L'Ouvrier (Sullivan AI Agent)
*   **Rôle** : Assistant de script dédié aux effets.
*   **Contenu** : 
    *   Chatbox Sullivan spécialisée dans le "Vibe-to-Code".
    *   Capacité à traduire des intentions abstraites (" Sullivan, fais que ce bouton respire quand on ne le clique pas ") en timelines GSAP précises.
    *   Accès au `logic.js` du projet pour une édition chirurgicale (AST).

### 🎞️ BAS : La Pellicule d'Effets (API GSAP Presets)
*   **Rôle** : Catalogue d'intentions visuelles.
*   **Contenu** : 
    *   Barre horizontale de vignettes (Thumbnails) montrant des aperçus d'effets.
    *   Catégories : `Entrées (Entrance)`, `Sorties (Exit)`, `Parallaxe`, `Distorsions (P5.js)`, `Hover-States`.
    *   Le clic sur une vignette génère instantanément le squelette de code dans Sullivan.

---

## 3. Fondations Techniques & Doctrine

*   **Pristine Logic** : Le code généré est stocké dans un bloc isolé `// [FEE-LOGIC]` pour ne pas polluer la structure HTML/CSS de base.
*   **Communication Bridge** : Utilisation du protocole de message stabilisé en Mission 208 pour une communication fluide entre le Host (Parent) et le Guest (Iframe).
*   **HoméOS Compliance** : Respect strict du design system (0px radius, beige #f7f6f2) même dans les interfaces d'édition les plus complexes.

## 4. Objectifs Pédagogiques
L'étudiant n'est plus un développeur qui lutte avec la syntaxe GSAP, mais un **Directeur Artistique** qui ajuste les curseurs d'une expérience déjà vivante. Sullivan devient le pont entre l'émotion visuelle et la rigueur du code.

---
*Vision FEE Popover — HoméOS 2026*
