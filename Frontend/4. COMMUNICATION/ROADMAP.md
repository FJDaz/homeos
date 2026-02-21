# Strategic Roadmap Stenciler V3

## Vision 2026 : Le Majordome de Code (Sullivan Architecture)
Garantir une transition fluide du Genome (DNA fonctionnel) vers le Stencil (UI/UX) tout en préservant la fidélité visuelle V1.

---

## Architecture de Sortie — Décision du 2026-02-20

**Destination confirmée : Humains (deploy, présentation DA) + Interopérabilité externe (Figma futur)**

```
Stenciler
  ├── Couche DATA    → Genome JSON (machine-readable)
  │                    Format d'échange : AetherFlow agents, plugin Figma (futur)
  └── Couche VISUEL  → SVG / HTML autonome (human-readable)
                       Format deploy : présentation client, livraison DA
```

---

## ✅ Phases 1→8B-BIS COMPLÈTES

Archivées dans [ROADMAP_ACHIEVED.md](file:///Users/francois-jeandazin/AETHERFLOW/Frontend/4. COMMUNICATION/ROADMAP_ACHIEVED.md).

**Verdict 8B-BIS (2026-02-21) :** Canvas = maquette d'application fonctionnelle. Wireframes sans cadre parasite, zones TOP/CENTER/RIGHT/BOTTOM distinctes, géométrie adaptive. Validé FJD (lutte mais acquis).

---

## Phase 8 — Intégration Dynamique : SVG Wireframe Library → Canvas

> [!IMPORTANT]
> **CONSTITUTION AETHERFLOW — ARTICLE 1 & 15 :**
> Frontière Hermétique INVIOLABLE. Interdiction absolue pour Gemini d'intervenir sur les fichiers Serveur (.py).
> Communication exclusive par API REST JSON.

---

### Mission 8C — Drag & Drop SVG Natif + Persistence `_layout` [LIVRÉE]

**ACTOR : GEMINI**
**MODE : CODE DIRECT**
**DATE : 2026-02-21**

#### Rapport de Livraison Détaillé

1.  **Moteur d'Interaction Natif :**
    *   **Drag Logic** : Implémentation du cycle complet `mousedown` → `mousemove` → `mouseup` directement dans le contrôleur de domaine `Canvas.feature.js`.
    *   **Précision SVG** : Utilisation de `getScreenCTM().inverse()` pour convertir les coordonnées écran en coordonnées locales SVG, garantissant un déplacement fluide même avec zoom/scroll.
    *   **Guard de Transformation** : Lecture dynamique des attributs `transform="translate(x,y)"` existants pour éviter tout cumul de matrices.

2.  **Alignement & Qualité (Snap-to-Grid) :**
    *   **Magnétisme** : Intégration d'un snap automatique sur une grille de **20px** déclenché au `mouseup`.
    *   **Feedback Visuel** : Changement d'état du curseur (`grabbing`) pendant la manipulation.

3.  **Persistence du Layout :**
    *   **Injection Genome** : Chaque déplacement met à jour la propriété `_layout: {x, y}` dans le génome local.
    *   **Surcharge de Rendu** : Le moteur de rendu (`Canvas.feature.js`) détecte désormais la présence de `_layout` et priorise ces coordonnées sur celles suggérées par le `LayoutEngine`.
    *   **Synchronisation** : Dispatch automatique de `genome:updated` après chaque drop réussi.


**Statut : ✅ TERMINÉ & ARCHIVÉ (Prêt pour Phase 8D)**

---

### Mission 8D — Outils Avancés & Panning [LIVRÉE]

1.  **Hand Tool (Mode Panning)** : `Espace` + `Drag` opérationnel.
2.  **Smart Label System (Hover-Only)** : Labels masqués au repos, apparaissent au survol. Injection intelligente dans le wireframe.
3.  **Transformation Panel** : Edition directe X, Y, W, H dans la sidebar.

---

### Mission 8E — Poignées & Outil Scale [LIVRÉE]

1.  **Handling 8-points** : Bounding box avec 8 poignées interactives.
2.  **Responsive Content** : Redimensionnement automatique des wireframes et labels lors du scale.
3.  **Modular Snap Engine** : Magnétisme flexible (8px, 20px) partagé entre Drag et Resize.

---

### Mission 8G — Layout Compression & Margin Tool [LIVRÉ]

1.  **Vertical & Horizontal Packing** : Optimisation de `LayoutEngine.js` pour une densité maximale (4 colonnes, hauteurs réduites à 120px).
2.  **Margin & Padding System** : Nouveau panneau **DISPOSITION** avec réglage fin (boutons +/-) des marges intérieures et extérieures.
3.  **Global Style Sync** : Bouton "Appliquer à tout le corps" pour une mise en page cohérente en un clic.

---

## ✅ PHASE 8 COMPLÈTE (2026-02-21)
Le Stenciler dispose désormais d'un moteur de design complet, d'un système de redimensionnement intelligent et d'un algorithme de placement spatial haute densité.

---

## Phase 9 — Flows & Connections (En préparation)

#### Objectif
Transformer le canvas en diagramme dynamique avec lignes de connexion et liens logiques.

---

## Archives
*(Voir [ROADMAP_ACHIEVED.md](file:///Users/francois-jeandazin/AETHERFLOW/Frontend/4. COMMUNICATION/ROADMAP_ACHIEVED.md) pour Phases 1 à 8B-BIS)*
