# PLAN INTEGRATION FIGMA EDITOR - Genome FRD

**Date** : 2026-02-08  
**Mode AetherFlow** : PROD (-f) avec Surgical Edit  
**Fichier cible** : `server_9999_v2.py` (Genome Viewer existant)  
**Référence UX** : `UX Phase FRD Clarifé.md`  
**Spécifications POC** : Pré-génération optimale | Desktop 1440×900 | localStorage

---

## ARCHITECTURE : Deux vues dans une seule app

```
server_9999_v2.py génère:
├── Vue 1: GENOME BROWSER (actuelle)
│   ├── Liste hiérarchique Corps/Organes/Cellules/Atomes
│   ├── Checkboxes de sélection
│   ├── Stats (Lire/Créer/Modifier)
│   ├── **Génération background des blueprints** (dès chargement)
│   └── Bouton "Valider (n)" → SWITCH TO VUE 2
│
└── Vue 2: FIGMA EDITOR (nouvelle, cachée par défaut)
    ├── Row Corps (haut) - miniatures avec états ⏳/✅/⚠️
    ├── Breadcrumb - navigation hiérarchique
    ├── Main Area - Canvas Fabric.js
    ├── Sidebar - hiérarchie accordéon (sans Corps en haut)
    └── Toolbar - zoom/export
```

---

## PHASE 0 : Pré-génération des Blueprints (NOUVEAU)

**Objectif** : Générer les esquisses de layouts dès le chargement de la Vue 1 pour une réponse immédiate au switch.

### 0.1 Détection des Corps
```javascript
// Au chargement de la page, identifier tous les Corps du Genome
const corpsList = detectCorpsFromGenome(genomeData);
// Résultat : ['dashboard', 'profile', 'settings', 'reports']
```

### 0.2 Génération asynchrone des blueprints
```javascript
// Pour chaque Corps détecté
function generateBlueprint(corpsId, visualHint) {
  // Tous les Corps en desktop 1440×900 pour ce POC
  const blueprint = {
    id: corpsId,
    width: 1440,
    height: 900,
    viewport: 'desktop',
    structure: inferStructureFromHint(visualHint),
    organes: [], // Positions prédéfinies mais vides
    generated_at: new Date().toISOString(),
    status: 'ready' // ou 'missing' si besoin brainstorm
  };
  
  // Stockage localStorage
  saveToLocalStorage(`blueprint_${corpsId}`, blueprint);
}
```

### 0.3 Structures par type de Corps
```javascript
const structures = {
  'preview': { 
    layout: 'single', 
    zones: [{type: 'preview-area', x: 0, y: 0, w: 1440, h: 900}]
  },
  'table': { 
    layout: 'header-content', 
    zones: [
      {type: 'header', x: 0, y: 0, w: 1440, h: 80},
      {type: 'table', x: 0, y: 80, w: 1440, h: 820}
    ]
  },
  'dashboard': { 
    layout: 'header-grid-footer', 
    zones: [
      {type: 'header', x: 0, y: 0, w: 1440, h: 80},
      {type: 'stats', x: 0, y: 80, w: 1440, h: 200},
      {type: 'content', x: 0, y: 280, w: 1440, h: 620}
    ]
  },
  'grid': { 
    layout: 'masonry', 
    zones: [{type: 'grid', x: 0, y: 0, w: 1440, h: 900}]
  },
  'editor': { 
    layout: 'sidebar-content', 
    zones: [
      {type: 'sidebar', x: 0, y: 0, w: 280, h: 900},
      {type: 'editor', x: 280, y: 0, w: 1160, h: 900}
    ]
  },
  'default': { 
    layout: 'flex', 
    zones: [{type: 'content', x: 0, y: 0, w: 1440, h: 900}]
  }
};
```

### 0.4 Stockage localStorage
```javascript
// Clé : homeos_blueprints
// Valeur : JSON avec tous les blueprints générés
{
  "version": "1.0",
  "generated_at": "2026-02-08T18:30:00Z",
  "blueprints": {
    "dashboard": { /* blueprint */ },
    "profile": { /* blueprint */ },
    "settings": { /* blueprint */ }
  }
}
```

---

## PHASE 1 : Intégration du switch Vue 1 → Vue 2

### 1.1 Wrapper les vues
```html
<div id="browser-view">...</div>
<div id="editor-view" style="display:none">...</div>
```

### 1.2 JavaScript de transition
```javascript
function openEditor(selectedIds) {
  // 1. Récupérer les blueprints depuis localStorage
  const blueprints = selectedIds.map(id => 
    loadFromLocalStorage(`blueprint_${id}`)
  );
  
  // 2. Afficher Row Corps avec états
  renderRowCorps(blueprints);
  
  // 3. Switch de vue
  document.getElementById('browser-view').style.display = 'none';
  document.getElementById('editor-view').style.display = 'grid';
  
  // 4. Initialiser Fabric.js
  initEditor(selectedIds, blueprints);
}
```

### 1.3 Connecter "Valider"
```javascript
document.getElementById('validate-btn').addEventListener('click', () => {
  const selectedIds = getSelectedCorpsIds();
  openEditor(selectedIds);
});
```

---

## PHASE 2 : Row Corps et Drag & Drop

### 2.1 Row Corps avec états
```
[⏳ Dashboard]  [✅ Profile]  [⚠️ Settings]
   skeleton      aperçu       dimensions?
```

**États :**
- **⏳ Skeleton** : Blueprint en cours de génération
- **✅ Généré** : Blueprint disponible dans localStorage
- **⚠️ Brainstorm** : Dimensions manquantes

### 2.2 Drag & Drop HTML5
```javascript
const thumbs = document.querySelectorAll('.corps-thumb');
thumbs.forEach(thumb => {
  thumb.addEventListener('dragstart', (e) => {
    e.dataTransfer.setData('corps-id', thumb.dataset.id);
  });
});

const canvas = document.getElementById('fabric-canvas');
canvas.addEventListener('drop', (e) => {
  const corpsId = e.dataTransfer.getData('corps-id');
  const blueprint = loadFromLocalStorage(`blueprint_${corpsId}`);
  
  if (blueprint.status === 'missing') {
    showBrainstormModal(corpsId);
  } else {
    renderBlueprintOnCanvas(blueprint);
  }
});
```

---

## PHASE 3 : Navigation hiérarchique

### 3.1 Double-clic drill-down
```javascript
canvas.on('mouse:dblclick', (e) => {
  const obj = e.target;
  if (obj.data?.type === 'corps') {
    zoomToOrganeView(obj.data.id);
  } else if (obj.data?.type === 'organe') {
    zoomToAtomeView(obj.data.id);
  }
});
```

### 3.2 Breadcrumb
```
Corps > Dashboard > StatsZone
```

### 3.3 Sidebar accordéon (sans Corps)
```
▼ Dashboard (MAX LUM)
  ├─ Header (MIDDLE LUM)
  ├─ Stats (MIDDLE LUM)
  └─ Footer (MIDDLE LUM)

▶ Profile (MIN LUM)
▶ Settings (MIN LUM)
```

---

## PHASE 4 : Brainstorm et Export

### 4.1 Brainstorm Modal
**Déclenchement** : Si Corps déposé avec `status === 'missing'`

### 4.2 Export JSON
```javascript
function exportToJSON() {
  const exportData = {
    version: '1.0',
    exported_at: new Date().toISOString(),
    canvas_state: canvas.toJSON(),
    blueprints_used: getUsedBlueprints(),
    fabric_objects: canvas.getObjects().map(obj => ({
      type: obj.type,
      position: { x: obj.left, y: obj.top },
      size: { width: obj.width, height: obj.height },
      data: obj.data
    }))
  };
  
  downloadJSON(exportData, `homeos-export-${Date.now()}.json`);
}
```

---

## CONTRAINTES

- **PAS DE SERVEUR** : Python sert fichiers statiques
- **PAS DE BUILD** : Fabric.js via CDN
- **PAS DE FRAMEWORK** : Vanilla JS
- **Surgical Edit** : Modifications minimales
- **Desktop First** : Tous les Corps en 1440×900
- **localStorage** : Stockage client uniquement

---

## WORKFLOW UTILISATEUR

1.  **Ouvre** `localhost:9999` → Vue 1
    └→ *Background* : Génération blueprints dans localStorage

2.  **Coche** des Corps → **Clique** "Valider (3)"
    └→ **Switch** → Vue 2 avec Row Corps (✅)

3.  **Drag** un Corps sur le canvas
    └→ Rendu immédiat du blueprint 1440×900

4.  **Double-clic** → Navigation drill-down

5.  **Export** JSON → Fichier téléchargé

---

## TIMELINE POC (1 mois)

| Semaine | Phase | Livrable |
|---------|-------|----------|
| S1 | 0 + 1 | Blueprints + Switch |
| S2 | 2 | Row Corps + Drag & Drop |
| S3 | 3 | Navigation drill-down |
| S4 | 4 | Brainstorm + Export |
