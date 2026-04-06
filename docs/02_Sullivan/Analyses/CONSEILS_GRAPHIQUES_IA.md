# Rapport : Conseils Exclusivement Graphiques pour l'UI (Inspiration Outils IA)

**Emplacement** : /docs/02_Sullivan/Analyses  
**Date** : 3 avril 2026  
**Auteur** : Gemini CLI

---

## 🎨 Focus Graphique : Le Regard du "Designer IA Senior"

L'analyse des outils soumis (Thoughtworks, UXPin, theee, DesignCriticGPT) permet d'extraire une liste de critères **purement visuels et esthétiques** pour élever la qualité graphique du Workspace.

### 1. Précision Mathématique & Alignement (Modèle Thoughtworks)
La qualité perçue d'une interface commence par sa rigueur géométrique.
- **Grille Invisible** : Adoption stricte du pas de 8px (ou 4px pour les micro-espacements). Tout élément hors-grille ou ayant des coordonnées sub-pixel (ex: 12.4px) doit être rectifié.
- **Rythme Vertical** : Constance des marges entre les blocs de texte et les composants pour créer un "souffle" visuel harmonieux.

### 2. Hiérarchie & Typographie (Modèle DesignCriticGPT)
L'IA juge la clarté de l'information par son contraste de taille et de graisse.
- **Type Ramp** : Définition d'une échelle typographique claire (H1, H2, H3, Body, Caption). Éviter d'utiliser plus de deux graisses (ex: Regular et Bold uniquement) pour maintenir la pureté.
- **Scannabilité** : Le bouton d'action principal (CTA) doit posséder un poids visuel (couleur, ombre, taille) nettement supérieur aux actions secondaires.

### 3. Théorie des Couleurs & Contrastes (Modèle UXPin)
L'esthétique est indissociable de l'accessibilité chromatique.
- **Harmonie sémantique** : Utilisation d'une palette restreinte (60/30/10). 60% neutre, 30% secondaire, 10% accent (le vert HoméOS #8cc63f).
- **Validation Contrastes** : Vérification systématique des ratios contrastes texte/fond selon les normes WCAG (AA/AAA).

### 4. Affordance & Gestalt (Modèle Design Crit Partner)
Comment l'interface "communique" sa fonction par sa forme.
- **Clarté des Affordances** : Un bouton doit *paraître* cliquable (ombre légère, coin arrondi, contraste de couleur). Un input doit *paraître* éditable.
- **Lois de Proximité** : Regroupement graphique des éléments liés par des conteneurs ou des espacements réduits pour faciliter la compréhension structurelle sans lire le texte.

### 5. Modernité & Signature Visuelle
Les tendances actuelles observées par les IA de critique :
- **Bento Grids** : Organisation des informations dans des cellules aux coins arrondis généreux.
- **Minimal Flat 2.0** : Utilisation de dégradés très subtils et d'ombres diffuses (soft shadows) pour donner de la profondeur sans charger l'interface.

---

## ⚡ Recommandations Actionnables pour Sullivan

| Vecteur | Action Graphique Immédiate |
| :--- | :--- |
| **Bordures** | Généraliser le `border-radius: 12px` ou `20px` pour un look "Soft UI". |
| **Espaces** | Remplacer les espacements arbitraires par des variables T-Shirt (xs: 4px, s: 8px, m: 16px, l: 32px). |
| **Couleurs** | Bannir le noir pur (#000) au profit du gris anthracite (#3d3d3c) pour plus de douceur. |
| **Logic** | Injecter systématiquement `antialiased` et `text-rendering: optimizeLegibility` dans le CSS des screens. |

---
*Ce rapport se concentre sur l'esthétique pure pour garantir un rendu "Pixel Perfect" et moderne.*
