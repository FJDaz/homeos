# PLAN INTEGRATION FIGMA EDITOR - Genome FRD

**Date** : 2026-02-08  
**Mode AetherFlow** : PROD (-f) avec Surgical Edit  
**Fichier cible** : `server_9999_v2.py` (Genome Viewer existant)  
**Référence UX** : `UX Phase FRD Clarifé.md`  

---

## ARCHITECTURE : Deux vues dans une seule app

```
server_9999_v2.py génère:
├── Vue 1: GENOME BROWSER (actuelle)
│   ├── Liste hiérarchique Corps/Organes/Cellules/Atomes
│   ├── Checkboxes de sélection
│   ├── Stats (Lire/Créer/Modifier)
│   └── Bouton "Valider (n)" → SWITCH TO VUE 2
│
└── Vue 2: FIGMA EDITOR (nouvelle, cachée par défaut)
    ├── Row Corps (haut) - miniatures des items sélectionnés
    ├── Breadcrumb - navigation hiérarchique
    ├── Main Area - Canvas Fabric.js
    ├── Sidebar - hiérarchie accordéon (sans Corps en haut)
    └── Toolbar - zoom/export
```

---

## PHASE 1 : Intégration du switch Vue 1 → Vue 2

**Modification `generate_html()` :**

1.  **Wrapper les vues** dans deux divs distinctes :
    ```html
    <div id="browser-view">...</div>  <!-- Existant -->
    <div id="editor-view" style="display:none">...</div>  <!-- Nouveau -->
    ```

2.  **JavaScript de transition** :
    ```javascript
    function openEditor(selectedIds) {
        document.getElementById('browser-view').style.display = 'none';
        document.getElementById('editor-view').style.display = 'grid';
        initEditor(selectedIds);  // Charge Fabric.js
    }
    ```

3.  **Connecter "Valider"** : Au clic, collecte les IDs cochés, appelle `openEditor()`.

---

## PHASE 2 : Row Corps et Drag & Drop

**Implémentation `UX Phase FRD` §A :**

1.  **Row Corps (top bar)** :
    -   Horizontal scroll
    -   Miniatures des Corps sélectionnés dans Vue 1
    -   États : ⏳ skeleton / ✅ généré / ⚠️ brainstorm needed
    -   **HTML5 Drag & Drop natif**

2.  **Drop Zone** sur le canvas Fabric :
    -   Activation au dragover
    -   Au drop : création d'un objet Fabric `Rect` représentant le Corps
    -   Si `status === 'missing'` → déclenche Brainstorm Modal

---

## PHASE 3 : Navigation hiérarchique

**Implémentation `UX Phase FRD` §B :**

1.  **Double-clic drill-down** :
    -   Sur objet Corps → zoom, affiche ses Organes
    -   Sur Organe → zoom, affiche ses Atomes
    -   Fabric.js viewport zoom + pan

2.  **Breadcrumb** :
    -   `Corps > Organe > Atome`
    -   Clic sur niveau = remontée
    -   Synchro avec viewport Fabric

3.  **Sidebar accordéon** :
    -   **Important** : Corps n'apparaissent PAS ici
    -   Seulement hiérarchie du Corps actif
    -   Corps actif = MAX LUM, autres = MIN LUM

---

## PHASE 4 : Brainstorm et Export

**Implémentation `UX Phase FRD` §C :**

1.  **Brainstorm Modal** :
    -   Popup si Corps déposé sans dimensions
    -   Input : `Largeur × Hauteur`
    -   Pré-remplissage suggéré

2.  **Export JSON** :
    -   Bouton dans toolbar
    -   État Fabric → JSON
    -   Compatible Figma REST API (futur)

---

## CONTRAINTES

- **PAS DE SERVEUR** : Python sert juste fichiers statiques
- **PAS DE BUILD** : Fabric.js via CDN
- **PAS DE FRAMEWORK** : Vanilla JS
- **Surgical Edit** : Modifications minimales à `server_9999_v2.py`

---

## WORKFLOW UTILISATEUR FINAL

1.  Ouvre `localhost:9999` → Vue 1 (liste hiérarchique)
2.  Coche des Corps → Clique "Valider (3)"
3.  **Switch** → Vue 2 (Figma Editor) avec les 3 Corps en top row
4.  Drag un Corps sur le canvas
5.  Double-clic pour naviguer Organes/Atomes
6.  Export JSON
