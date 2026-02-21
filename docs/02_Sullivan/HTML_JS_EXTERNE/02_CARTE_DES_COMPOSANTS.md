# 02 - Carte des Composants (Le Lego Aetherflow)

L'externalisation consiste à briser le monolithe `server_9998_v2.py` pour créer une bibliothèque de composants autonomes.

## 🧱 Architecture par Ensembles

### A. Le GENOME VIEWER (Analyse)
*Modules pour visualiser la statue sémantique N0-N3.*
- `viewer_layout.html` : Squelette global.
- `wireframe_lib.js` : Bibliothèque des rendus 2D (SVG).
- `atome_card.html` : Template de base des composants atomiques.

### B. LE STYLE PICKER (Pivot)
*La passerelle entre le fonctionnel et l'esthétique.*
- `style_grid.html` : La sélection des 8 univers visuels.
- `style_registry.js` : Le dictionnaire des thèmes (Elegant, Tech, etc.).
- `upload_handler.js` : Gestionnaire d'importation de maquettes.

### C. LE STENCILER (Atelier)
*L'espace de manipulation directe.*
- `canvas_core.js` : Initialisation Fabric.js et gestion du Tarmac.
- `sidebar_tools.html` : Panneau de réglages contextuels.
- `previews_band.html` : La glissière des Corps (N0) à insérer.

---

## ⚡ L'ENGINE "OUVERT" (Hooks System)
*La couche d'articulation permettant l'extensibilité infinie.*

- **`hook_manager.js`** : Permet de "brancher" des actions sur des événements.
    - Ex: `hook.onSelection('Affiche_Outils_N2')`.
- **`context_mediator.js`** : Calcule ce que l'utilisateur doit voir selon où il se trouve dans le Genome.
- **`drill_down_logic.js`** : Gère la navigation sémantique (Plongée N0 -> N3).

---

## 💡 Impact sur le Contexte IA
En travaillant sur des fichiers séparés, nous réduisons le "bruit" pour l'agent (KIMI/Claude) par un facteur **10 à 20**. L'IA n'ouvre que la brique dont elle a besoin, éliminant ainsi les régressions "amnésiques" constatées sur le monolithe.
