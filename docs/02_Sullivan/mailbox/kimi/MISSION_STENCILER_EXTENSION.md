# Mission KIMI : Extension du Viewer 9998 avec Stenciler

**Date** : 11 février 2026
**De** : François-Jean (Boss) via Claude (Backend Lead)
**À** : KIMI (Chef Frontend)
**Sujet** : EXTENSION du server_9998_v2.py - NE PAS FUSIONNER, AJOUTER EN DESSOUS

---

## 📋 PROCÉDURE ÉTAPE PAR ÉTAPE

### ÉTAPE 0 : LIRE ET COMPRENDRE

Avant d'écrire une seule ligne de code :
1. Ouvre `server_9998_v2.py` (1422 lignes)
2. Repère la ligne 1422 (fin du fichier actuel)
3. Comprends que tu vas **ajouter après**, pas modifier

### ÉTAPE 1 : VÉRIFIER LE FICHIER EXISTANT

```bash
wc -l server_9998_v2.py
# Attendu : 1422 lignes
```

Si ce n'est pas 1422 lignes, **STOP** - le fichier a été modifié. Restaure avec :
```bash
git checkout server_9998_v2.py
```

### ÉTAPE 2 : CRÉER UN BACKUP

```bash
cp server_9998_v2.py server_9998_v2.backup.py
```

### ÉTAPE 3 : AJOUTER LE CODE

Ouvre `server_9998_v2.py` et **va à la fin du fichier** (après la dernière ligne).
Ajoute le code détaillé dans cette mission (CSS, HTML, JS).

### ÉTAPE 4 : TESTER

```bash
python server_9998_v2.py
# Ouvre http://localhost:9998
```

Vérifie que :
- ✅ Le Viewer existant fonctionne toujours
- ✅ La section Stenciler est cachée au démarrage
- ✅ Au clic sur un style, ça scroll vers le Stenciler
- ✅ Les previews sont draggables vers le canvas

### ÉTAPE 5 : SI ÇA NE MARCHE PAS

```bash
# Restaurer le backup
cp server_9998_v2.backup.py server_9998_v2.py
```

Puis recommence en lisant attentivement les erreurs.

---

## ⚠️ CE QUI A FOIRÉ (pour ne pas refaire la même erreur)

| Tentative | Problème |
|-----------|----------|
| Fusion viewer + stenciler | Fichier cassé, logiques incompatibles |
| server_9999_v3.py | Duplication inutile |
| server_9998_stenciler.py | Fichier séparé, pas intégré |
| server_9997_stenciler.py | Port différent, workflow cassé |

**L'erreur** : Tu as essayé de FUSIONNER deux logiques incompatibles (HTML collapse ≠ Canvas Fabric.js).

---

## ✅ LA BONNE APPROCHE : EXTENSION VERTICALE

```
┌──────────────────────────────────────────────────────┐
│                                                      │
│     VIEWER EXISTANT (lignes 1-1422 INCHANGÉES)      │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │ [▼] Brainstorm (2 organes)                     │ │
│  │ [▼] Backend (1 organe)                         │ │
│  │ [▼] Frontend (7 organes)                       │ │
│  │ [▼] Deploy (1 organe)                          │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │ 🎨 Choisir le style (8 cards) + 📁 Upload     │ │ ← Section existante
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  ═══════════════════════════════════════════════════│
│                    ↓ SCROLL ↓                        │
│  ═══════════════════════════════════════════════════│
│                                                      │
│     STENCILER (NOUVELLE SECTION - lignes 1423+)     │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │ BANDE DE PREVIEWS (4 Corps à 20%)             │ │
│  │ ┌────┐ ┌────┐ ┌────┐ ┌────┐                   │ │
│  │ │ B  │ │ Ba │ │ Fr │ │ De │  ← draggables     │ │
│  │ └────┘ └────┘ └────┘ └────┘                   │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  ┌──────────┬─────────────────────────────────────┐ │
│  │ SIDEBAR  │         CANVAS TARMAC               │ │
│  │          │         (Fabric.js)                 │ │
│  │ 🎨 Color │                                     │ │
│  │ 📏 Border│      [Corps droppés ici]           │ │
│  │ 🖌️ BG    │                                     │ │
│  │          │                                     │ │
│  └──────────┴─────────────────────────────────────┘ │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## 🎯 CE QUE TU DOIS FAIRE

### **Règle absolue : NE TOUCHE PAS aux lignes 1-1422**

Le Viewer actuel fonctionne. Tu ne modifies RIEN dans cette partie.

### **Tu ajoutes APRÈS la ligne 1422 :**

1. **Une section "Stenciler"** (cachée par défaut, révélée au trigger)
2. **Une bande de previews** (4 Corps à 20% taille, horizontaux, draggables)
3. **Un layout sidebar + canvas** (Fabric.js)
4. **Le JS Fabric.js** pour le canvas

---

## 🔧 STRUCTURE TECHNIQUE

### **1. Bande de Previews (au-dessus du canvas)**

```html
<div id="stenciler-section" style="display:none;">

  <!-- Bande de previews 4 Corps -->
  <div class="previews-band">
    <div class="preview-corps" data-corps-id="n0_brainstorm" draggable="true">
      <div class="preview-header" style="background:#fbbf24;">Brainstorm</div>
      <div class="preview-body">
        <!-- Organes en blocks colorés simplifiés -->
        <div class="preview-organe">IR</div>
        <div class="preview-organe">Arbitrage</div>
      </div>
    </div>
    <!-- ... 3 autres Corps -->
  </div>

  <!-- Layout Sidebar + Canvas -->
  <div class="stenciler-layout">
    <aside class="stenciler-sidebar">...</aside>
    <main class="stenciler-canvas">
      <canvas id="tarmac-canvas"></canvas>
    </main>
  </div>

</div>
```

### **2. Triggers d'activation**

Le Stenciler s'active quand :
- **Clic sur un des 8 styles** (minimal, corporate, creative, etc.)
- **Upload + analyse d'un template** (feature future, juste prévoir le hook)

```javascript
// Au clic sur un style
function selectStyle(styleId) {
  // 1. Afficher la section Stenciler
  document.getElementById('stenciler-section').style.display = 'block';

  // 2. Stocker le style sélectionné
  window.selectedStyle = styleId;

  // 3. Scroll vers le Stenciler
  document.getElementById('stenciler-section').scrollIntoView({ behavior: 'smooth' });

  // 4. Initialiser le canvas Fabric.js (lazy init)
  if (!window.tarmacCanvas) {
    initTarmacCanvas();
  }
}

// Hook pour l'upload (feature future)
function onTemplateAnalyzed(templateData) {
  // Sera implémenté plus tard
  // Pour l'instant, juste activer le Stenciler
  document.getElementById('stenciler-section').style.display = 'block';
  document.getElementById('stenciler-section').scrollIntoView({ behavior: 'smooth' });
}
```

### **3. Affichage Hybride des Corps (Tier 1/2/3)**

Selon la stratégie hybride de prégénération :

**Preview à 20% (Tier 1 - 0ms)** :
```javascript
// Structure simplifiée pré-générée
const previewCorps = {
  id: "n0_frontend",
  name: "Frontend",
  color: "#ec4899",
  organes_count: 7,
  preview_organes: ["Navigation", "Layout", "Upload", "..."] // Juste les noms
};
```

**Corps sur Tarmac à 33% (Tier 2 - <100ms)** :
```javascript
// Au drop sur le canvas, charger un peu plus de détails
async function loadCorpsDetails(corpsId) {
  // Requête légère : organes avec features_count
  const data = await fetch(`/studio/stencils/corps/${corpsId}`);
  return data.json();
}
```

**Drill-down Organe (Tier 3 - 1-5s)** :
```javascript
// Au double-clic sur un organe dans le canvas
async function loadOrganeDetails(organeId) {
  // Requête complète : composants + mapping Elite
  const data = await fetch(`/studio/stencils/organe/${organeId}/components`);
  return data.json();
}
```

---

## 📐 CSS À AJOUTER

```css
/* ========================================
   STENCILER SECTION (après le viewer)
   ======================================== */

#stenciler-section {
  margin-top: 40px;
  padding-top: 40px;
  border-top: 2px dashed #e2e8f0;
}

/* Bande de previews */
.previews-band {
  display: flex;
  gap: 16px;
  justify-content: center;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
  margin-bottom: 24px;
}

.preview-corps {
  width: 120px;
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  cursor: grab;
  transition: all 0.2s;
}

.preview-corps:hover {
  border-color: #7aca6a;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.preview-corps.dragging {
  opacity: 0.5;
  cursor: grabbing;
}

.preview-header {
  padding: 8px;
  color: white;
  font-size: 11px;
  font-weight: 700;
  text-align: center;
  border-radius: 6px 6px 0 0;
}

.preview-body {
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.preview-organe {
  padding: 4px 6px;
  background: #f1f5f9;
  border-radius: 4px;
  font-size: 9px;
  color: #64748b;
}

/* Layout Sidebar + Canvas */
.stenciler-layout {
  display: flex;
  gap: 16px;
  height: 600px;
}

.stenciler-sidebar {
  width: 200px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px;
  flex-shrink: 0;
}

.stenciler-canvas {
  flex: 1;
  background: white;
  border: 2px dashed #cbd5e1;
  border-radius: 12px;
  position: relative;
  overflow: hidden;
}

#tarmac-canvas {
  width: 100%;
  height: 100%;
}

/* Sidebar tools */
.tool-section {
  margin-bottom: 20px;
}

.tool-label {
  font-size: 11px;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 8px;
  text-transform: uppercase;
}

.color-swatches {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.color-swatch {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
}

.color-swatch:hover,
.color-swatch.active {
  border-color: #1e293b;
  transform: scale(1.1);
}

.slider-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.slider-container input[type="range"] {
  flex: 1;
}

.slider-value {
  font-size: 11px;
  color: #64748b;
  min-width: 35px;
}
```

---

## 🔌 JS FABRIC.JS À AJOUTER

```javascript
/* ========================================
   STENCILER CANVAS (Fabric.js)
   ======================================== */

let tarmacCanvas = null;
let selectedStyle = 'minimal';
let droppedCorps = [];

function initTarmacCanvas() {
  const canvasEl = document.getElementById('tarmac-canvas');
  const container = canvasEl.parentElement;

  tarmacCanvas = new fabric.Canvas('tarmac-canvas', {
    width: container.clientWidth,
    height: container.clientHeight,
    backgroundColor: '#fafafa',
    selection: true
  });

  // Resize handler
  window.addEventListener('resize', () => {
    tarmacCanvas.setWidth(container.clientWidth);
    tarmacCanvas.setHeight(container.clientHeight);
    tarmacCanvas.renderAll();
  });

  // Drop zone
  container.addEventListener('dragover', (e) => {
    e.preventDefault();
    container.style.borderColor = '#7aca6a';
    container.style.background = '#f0fdf4';
  });

  container.addEventListener('dragleave', () => {
    container.style.borderColor = '#cbd5e1';
    container.style.background = 'white';
  });

  container.addEventListener('drop', (e) => {
    e.preventDefault();
    container.style.borderColor = '#cbd5e1';
    container.style.background = 'white';

    const corpsId = e.dataTransfer.getData('corpsId');
    if (corpsId) {
      const rect = container.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      addCorpsToCanvas(corpsId, x, y);
    }
  });

  // Selection events
  tarmacCanvas.on('selection:created', updateSidebarFromSelection);
  tarmacCanvas.on('selection:updated', updateSidebarFromSelection);
  tarmacCanvas.on('selection:cleared', clearSidebarSelection);

  // Double-click pour drill-down
  tarmacCanvas.on('mouse:dblclick', (e) => {
    if (e.target && e.target.corpsData) {
      enterCorps(e.target.corpsData);
    }
  });
}

function handleDragStart(e, corpsId) {
  e.dataTransfer.setData('corpsId', corpsId);
  e.target.classList.add('dragging');
}

function handleDragEnd(e) {
  e.target.classList.remove('dragging');
}

async function addCorpsToCanvas(corpsId, x, y) {
  // Tier 2 : Charger les détails du corps
  const corpsData = await loadCorpsDetails(corpsId);

  const color = getCorpsColor(corpsId);
  const name = corpsData.name || corpsId.replace('n0_', '');

  // Créer le groupe Fabric.js (taille 33%)
  const group = new fabric.Group([], {
    left: x - 100,
    top: y - 75,
    hasControls: true,
    hasBorders: true,
    lockRotation: true
  });

  // Rectangle principal
  const mainRect = new fabric.Rect({
    width: 200,
    height: 150,
    fill: 'white',
    stroke: color,
    strokeWidth: 3,
    rx: 8,
    ry: 8
  });

  // Header
  const header = new fabric.Rect({
    width: 200,
    height: 30,
    fill: color,
    rx: 8,
    ry: 8
  });

  // Titre
  const title = new fabric.Text(name, {
    left: 10,
    top: 8,
    fontSize: 14,
    fontWeight: 'bold',
    fill: 'white'
  });

  // Organes (blocs colorés simplifiés)
  let orgY = 40;
  const organes = corpsData.organes || [];
  organes.slice(0, 4).forEach((org) => {
    const orgRect = new fabric.Rect({
      left: 10,
      top: orgY,
      width: 180,
      height: 20,
      fill: '#f1f5f9',
      rx: 4,
      ry: 4
    });
    const orgText = new fabric.Text(org.name.substring(0, 20), {
      left: 15,
      top: orgY + 4,
      fontSize: 10,
      fill: '#64748b'
    });
    group.addWithUpdate(orgRect);
    group.addWithUpdate(orgText);
    orgY += 25;
  });

  group.addWithUpdate(mainRect);
  group.addWithUpdate(header);
  group.addWithUpdate(title);

  // Stocker les données du corps
  group.corpsData = corpsData;
  group.corpsId = corpsId;

  tarmacCanvas.add(group);
  tarmacCanvas.setActiveObject(group);
  tarmacCanvas.renderAll();

  droppedCorps.push(corpsId);
}

async function loadCorpsDetails(corpsId) {
  // Pour l'instant, données statiques depuis le genome
  // Plus tard : requête API
  const genome = window.genomeData || {};
  const phases = genome.n0_phases || [];
  return phases.find(p => p.id === corpsId) || { name: corpsId, organes: [] };
}

function getCorpsColor(corpsId) {
  const colors = {
    'n0_brainstorm': '#fbbf24',
    'n0_backend': '#6366f1',
    'n0_frontend': '#ec4899',
    'n0_deploy': '#10b981'
  };
  return colors[corpsId] || '#64748b';
}

function enterCorps(corpsData) {
  console.log('Double-clic: Entrée dans', corpsData.name);
  // TODO: Drill-down niveau 2 (afficher organes détaillés)
  alert('Entrée dans: ' + corpsData.name + '\n\nDrill-down à implémenter.');
}

function updateSidebarFromSelection(e) {
  const obj = e.selected ? e.selected[0] : null;
  if (obj) {
    // Mettre à jour les valeurs de la sidebar
    document.getElementById('selection-info').textContent = obj.corpsData?.name || 'Sélection';
  }
}

function clearSidebarSelection() {
  document.getElementById('selection-info').textContent = 'Aucune sélection';
}

// Sidebar tools
function setColor(color) {
  const obj = tarmacCanvas.getActiveObject();
  if (obj) {
    obj.set('stroke', color);
    tarmacCanvas.renderAll();
  }
}

function setBorderWidth(value) {
  const obj = tarmacCanvas.getActiveObject();
  if (obj) {
    obj.set('strokeWidth', parseInt(value));
    tarmacCanvas.renderAll();
  }
  document.getElementById('border-value').textContent = value + 'px';
}

function setBackground(color) {
  const obj = tarmacCanvas.getActiveObject();
  if (obj && obj._objects) {
    // Trouver le rect principal et changer son fill
    const mainRect = obj._objects.find(o => o.type === 'rect' && o.width > 100);
    if (mainRect) {
      mainRect.set('fill', color);
      tarmacCanvas.renderAll();
    }
  }
}

function deleteSelected() {
  const obj = tarmacCanvas.getActiveObject();
  if (obj) {
    const idx = droppedCorps.indexOf(obj.corpsId);
    if (idx > -1) droppedCorps.splice(idx, 1);
    tarmacCanvas.remove(obj);
    tarmacCanvas.renderAll();
  }
}
```

---

## 📦 HTML DE LA SIDEBAR

```html
<aside class="stenciler-sidebar">
  <div class="sidebar-header">
    <h3>Outils</h3>
    <p id="selection-info" style="font-size:11px;color:#64748b;">Aucune sélection</p>
  </div>

  <div class="tool-section">
    <div class="tool-label">Bordure</div>
    <div class="color-swatches">
      <div class="color-swatch" style="background:#ef4444;" onclick="setColor('#ef4444')"></div>
      <div class="color-swatch" style="background:#f97316;" onclick="setColor('#f97316')"></div>
      <div class="color-swatch" style="background:#eab308;" onclick="setColor('#eab308')"></div>
      <div class="color-swatch" style="background:#22c55e;" onclick="setColor('#22c55e')"></div>
      <div class="color-swatch" style="background:#3b82f6;" onclick="setColor('#3b82f6')"></div>
      <div class="color-swatch" style="background:#8b5cf6;" onclick="setColor('#8b5cf6')"></div>
      <div class="color-swatch" style="background:#ec4899;" onclick="setColor('#ec4899')"></div>
      <div class="color-swatch" style="background:#64748b;" onclick="setColor('#64748b')"></div>
    </div>
  </div>

  <div class="tool-section">
    <div class="tool-label">Épaisseur</div>
    <div class="slider-container">
      <input type="range" min="1" max="10" value="3" oninput="setBorderWidth(this.value)">
      <span class="slider-value" id="border-value">3px</span>
    </div>
  </div>

  <div class="tool-section">
    <div class="tool-label">Fond</div>
    <div class="color-swatches">
      <div class="color-swatch" style="background:#ffffff;border:1px solid #e2e8f0;" onclick="setBackground('#ffffff')"></div>
      <div class="color-swatch" style="background:#f8fafc;" onclick="setBackground('#f8fafc')"></div>
      <div class="color-swatch" style="background:#fef3c7;" onclick="setBackground('#fef3c7')"></div>
      <div class="color-swatch" style="background:#dbeafe;" onclick="setBackground('#dbeafe')"></div>
      <div class="color-swatch" style="background:#fce7f3;" onclick="setBackground('#fce7f3')"></div>
      <div class="color-swatch" style="background:#d1fae5;" onclick="setBackground('#d1fae5')"></div>
    </div>
  </div>

  <div class="tool-section">
    <button onclick="deleteSelected()" style="width:100%;padding:10px;background:#fee2e2;color:#dc2626;border:none;border-radius:6px;cursor:pointer;font-weight:600;">
      🗑️ Supprimer
    </button>
  </div>
</aside>
```

---

## 🔗 HOOK POUR UPLOAD FUTURE

```javascript
// Dans la section style existante, ajouter un listener sur l'upload
document.getElementById('upload-zone')?.addEventListener('analysisComplete', (e) => {
  // Feature future : après analyse Gemini Vision du template
  onTemplateAnalyzed(e.detail);
});

function onTemplateAnalyzed(templateData) {
  // 1. Stocker les données extraites
  window.templateData = templateData;

  // 2. Activer le Stenciler
  document.getElementById('stenciler-section').style.display = 'block';
  document.getElementById('stenciler-section').scrollIntoView({ behavior: 'smooth' });

  // 3. Appliquer le style extrait (si disponible)
  if (templateData.style) {
    selectedStyle = templateData.style;
  }

  // 4. Initialiser le canvas
  if (!tarmacCanvas) {
    initTarmacCanvas();
  }
}
```

---

## ✅ RÉCAPITULATIF

**Ce que tu fais :**
1. Tu **ajoutes** ~400 lignes à la fin de `server_9998_v2.py` (après ligne 1422)
2. Tu **ne touches pas** aux 1422 lignes existantes du Viewer
3. La section Stenciler est **cachée par défaut** (`display:none`)
4. Elle s'active au **clic sur un style** OU **après upload+analyse** (hook prévu)
5. Le canvas Fabric.js est **lazy-init** (seulement quand visible)
6. Les Corps sont **draggables** depuis la bande de previews vers le canvas
7. Affichage **hybride** : preview 20% → canvas 33% → drill-down (Tier 1/2/3)

**Ce que tu ne fais pas :**
- ❌ Créer un nouveau fichier
- ❌ Modifier le Viewer existant
- ❌ Fusionner des logiques incompatibles
- ❌ Dupliquer du code

---

---

## 📝 CHECKLIST FINALE

Avant de soumettre ton code, vérifie :

- [ ] Le fichier `server_9998_v2.py` a plus de 1422 lignes (pas moins)
- [ ] Les lignes 1-1422 sont **identiques** à l'original
- [ ] La section `#stenciler-section` existe avec `display:none`
- [ ] Le CDN Fabric.js est chargé : `<script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.1/fabric.min.js"></script>`
- [ ] La fonction `selectStyle()` existe et appelle `scrollIntoView`
- [ ] La fonction `initTarmacCanvas()` existe et crée un `fabric.Canvas`
- [ ] La bande de previews a 4 Corps avec `draggable="true"`
- [ ] La sidebar a les swatches de couleur et le slider border
- [ ] Le hook `onTemplateAnalyzed()` existe (même vide, pour la feature future)

---

## 🚨 SI TU BLOQUES

1. **Erreur JS** : Vérifie que Fabric.js est chargé avant ton code
2. **Canvas invisible** : Vérifie les dimensions du conteneur parent
3. **Drag & drop ne marche pas** : Vérifie `e.dataTransfer.setData` et `getData`
4. **Section ne s'affiche pas** : Vérifie que `selectStyle()` est bien appelée

---

**Ton move, KIMI. Extension, pas fusion. Une étape à la fois.**

---

François-Jean Dazin
Boss @ Sullivan
