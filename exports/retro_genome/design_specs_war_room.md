# [SPEC DESIGN] War Room Brainstorm - Layout & Esthétique

Ce document définit les spécifications de design extraites de la référence géno-typique de la Mission 43 (War Room Brainstorm).

## 1. Structure Spatiale (Layout)
Le canevas global est optimisé pour une résolution large de **2570x1736 px**.

### Diviseurs Majeurs
- **Sidebar (Navigation)** : Largeur fixe de **554px** sur le bord gauche.
- **Header** : Hauteur de **64px** en haut de l'écran. 
- **Zone de Travail (War Room)** : Divisée en **4 colonnes** égales de **504px** chacune, commençant après la sidebar (x = 554).

### Grille des Colonnes
| Colonne | Coordonnées X | Rôle / Provider | Couleur d'Accent |
| :--- | :--- | :--- | :--- |
| **C1** | 554px - 1058px | Gemini (Google) | `#626AE8` (Indigo/Bleu) |
| **C2** | 1058px - 1562px | DeepSeek | `#A58DE0` (Mauve/Violet) |
| **C3** | 1562px - 2066px | Groq / Llama | `#8CC63F` (Vert Pomme) |
| **C4** | 2066px - 2570px | Sullivan's Basket / PRD area | `#5EC069` (Vert Brillance) |

---

## 2. Palette Chromatique
Le design utilise une esthétique "Dark Mode" raffinée avec des bordures subtiles.

### Couleurs de Structure
- **Fonds (Backgrounds)** : `#FFFFFF` (Base), `#F9F9F9` (Gris très clair pour les zones secondaires).
- **Lignes de Grille / Bordures** : `#333333` (Stroke-width: 0.5px) pour une précision chirurgicale.
- **Séparateurs Subtils** : `#EFEFEF` pour le cockpit.

### Couleurs Fonctionnelles (Accents)
- **Branding Sullivan/AetherFlow** : `#8CC63F` (Vert Signature)
- **Validation / Succès** : `#5EC069`
- **Typographie / Contenu** : `#000000` (Flattened paths), `#666666` (Gris de lecture).

---

## 3. Composants Identifiés
- **Sullivan Cockpit** : Zone de capture et de gestion des "n nuggets" située dans la colonne 4. Elle contient des indicateurs d'état circulaires (y=1454px) reflétant les couleurs des providers (Mauve, Bleu).
- **Cartes de Réponse (AI Cards)** : Disposées verticalement dans les colonnes C1, C2, C3. Espacement régulier (Gap vertical d'environ 160-170px entre les points d'ancrage).
- **Panneau de Basket** : Largeur pleine de la colonne 4 (504px), ancrée à droite pour la synthèse du PRD.

## 4. Esthétique & Rendu
- **Mode "Pristine"** : Rendu vectoriel pur sans fioritures inutiles.
- **Glassmorphism (Cible)** : Bien que l'SVG soit plat, les spécifications recommandent un effet de flou d'arrière-plan sur les modales Sullivan.
- **Minimalisme** : Pas d'ombres portées agressives, utilisation de bordures de 0.5px à 1px pour définir les zones.
