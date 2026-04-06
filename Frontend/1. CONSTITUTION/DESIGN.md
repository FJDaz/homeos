# 🏛️ Design System HoméOS — The Rational Playroom

## 1. Overview & Creative North Star

### Creative North Star: "The Rational Playroom"
Ce système est une célébration de la précision mathématique filtrée par une lentille éditoriale ludique et moderne. Il rejette le chaos des layouts web traditionnels en faveur d'une grille rigoureuse et logique. C'est le "Salon Rationnel" : un espace où chaque élément a une coordonnée fixe, mais où l'interaction reste vibrante et cinétique.

Nous brisons le look "template standard" par une typographique à fort impact. En traitant l'UI comme une série de cellules interconnectées plutôt qu'un flux continu, nous créons une expérience intentionnelle et structurée. Nous adoptons une esthétique **"Hard-Edge"** : **0px border radius** sur toute l'interface pour une silhouette architecturale tranchante qui reflète la nature structurée de l'inspiration.

---

## 2. Colors

La stratégie couleur est la **"Vibrance Catégorielle"**. La couleur est un outil cartographique pour définir les états et les catégories.

### Surface Hierarchy & Nesting
Le contraste est obtenu par des décalages tonaux, et non par des bordures.
- **The "No-Line" Rule** : Les bordures solides de 1px sont strictement interdites pour le sectionnement.
- **Logic de Nesting** : Placer une carte `surface_container_lowest` (#ffffff) sur un fond `surface` (#f7f6f2) pour un effet "papier-sur-bureau".

### Primary Semantic Roles (Official Palette)
- **Primary (Vert Aetherflow)** : `#A3CD54` — Succès, Action, Progrès actif.
- **Secondary (Dark)** : `#1A1A1A` — Structure, Fondations, Profondeur.
- **Tertiary (Slate)** : `#64748B` — Neutralité technique, Support.
- **Neutral (Slate Light)** : `#F8FAFC` — Surfaces secondaires.
- **Crème (Background)** : `#F7F6F2` — Fond principal.
- **Texte (Standard)** : `#3D3D3C` — Lisibilité.

---

## 3. Typography

La typographie est la "Voix de la Grille".
- **UI (Navigation, Contrôles)** : `Source Sans 3`.
- **Technique (Code, Inférence)** : `Source Code Pro`.
- **Règle de Casse** : **Sentence case** obligatoire (Majuscule en début de phrase ou d'occurrence, minuscule pour la suite). 
- **Display SCales** : Lettrage serré (-2%) pour un aspect bloc structurel.
- **Label Scales** : Peuvent être en MAJUSCULES pour renforcer l'aspect mathématique (ex: "STEP 01").

---

## 4. Elevation & Depth

La profondeur est une expression de **Superposition Tonale**, pas de hauteur physique.
- **Layering Principle** : Empiler les tokens de surface (ex: Blanc sur Gris très clair).
- **Ambient Shadows** : Uniquement pour les éléments flottants (Modales). Utiliser l'ombre "Cloud Shadow" : `box-shadow: 0 24px 48px rgba(0, 0, 0, 0.06)`. Elle doit être une présence atmosphérique, pas une ombre portée dure.
- **0px border radius** : Une règle absolue. La netteté est notre signature.

---

## 5. Components

### Buttons
- **Primary** : Coins vifs (**0px**), fond `Primary` (#A3CD54), texte `OnPrimary` (Sombre).
- **Secondary** : Fond `Secondary` (#1A1A1A), texte blanc.
- **Tertiary** : Sans fond ; texte `Texte` (#3D3D3C) avec un changement de ton au survol.

### Cards & Magic Squares
- **Structure** : Pas de diviseurs. Utiliser `2.5rem` (10 units) de padding.
- **Grid Unit** : Les cellules individuelles utilisent des changements de tonalité pour créer un effet de damier mathématique.

---

## 6. Do's and Don'ts

### Do
- **Do** utiliser la grille de 8px de manière rigoureuse.
- **Do** utiliser **0px border radius** pour TOUT.
- **Do** utiliser des blocs de couleurs contrastés pour séparer les flux logiques.
- **Do** laisser de "l'oxygène" (espaces vides) pour éviter l'encombrement.

### Don't
- **Don't** utiliser de bordures noires de 1px.
- **Don't** utiliser d'angles arrondis. Jamais.
- **Don't** utiliser d'ombres "Material Design" par défaut.

---
*Fichier de référence technique — DA : FJD.*
