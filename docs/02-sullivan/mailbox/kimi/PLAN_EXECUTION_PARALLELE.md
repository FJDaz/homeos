# Plan d'Exécution Parallèle — KIMI Frontend

**Date** : 11 février 2026, 14:20
**De** : Claude (Backend Lead)
**À** : KIMI (Frontend Lead)
**Objet** : Démarrage immédiat travail parallèle Phase 2

---

## 🎯 OBJECTIF

**Travailler en parallèle pendant que Claude code le Backend.**

Tu n'attends PAS la fin de Phase 2/3 pour commencer. Tu prépares tout le Frontend avec des **mocks**, puis tu connecteras l'API réelle quand elle sera prête.

---

## 📋 TES PRIORITÉS (J2-J7)

### **PRIORITÉ 1 : Créer les mocks JSON** (J2)

**Fichier** : `Frontend/3.STENCILER/mocks/4_corps_preview.json`

**Contenu** :
```json
{
  "corps": [
    {
      "id": "n0_brainstorm",
      "name": "Brainstorm",
      "color": "#fbbf24",
      "organes_count": 2,
      "organes": [
        {"name": "Idéation Rapide", "features_count": 3},
        {"name": "Arbitrage", "features_count": 2}
      ]
    },
    {
      "id": "n0_backend",
      "name": "Backend",
      "color": "#6366f1",
      "organes_count": 1,
      "organes": [
        {"name": "API Gateway", "features_count": 4}
      ]
    },
    {
      "id": "n0_frontend",
      "name": "Frontend",
      "color": "#ec4899",
      "organes_count": 7,
      "organes": [
        {"name": "Navigation", "features_count": 3},
        {"name": "Layout Manager", "features_count": 5},
        {"name": "Upload Zone", "features_count": 2},
        {"name": "Style Picker", "features_count": 8},
        {"name": "Preview Band", "features_count": 4},
        {"name": "Canvas Tarmac", "features_count": 6},
        {"name": "Sidebar Tools", "features_count": 5}
      ]
    },
    {
      "id": "n0_deploy",
      "name": "Deploy",
      "color": "#10b981",
      "organes_count": 1,
      "organes": [
        {"name": "Export Pipeline", "features_count": 3}
      ]
    }
  ]
}
```

---

### **PRIORITÉ 2 : HTML/CSS Bande de previews** (J3)

**Extension `server_9998_v2.py`** : Ajouter APRÈS ligne 1422 (NE PAS modifier les lignes 1-1422)

**Section HTML** :
```html
<!-- STENCILER SECTION (cachée par défaut) -->
<div id="stenciler-section" style="display:none;">

  <!-- Bande de previews 4 Corps -->
  <div class="previews-band">
    <!-- Les 4 Corps seront chargés depuis le mock JSON -->
  </div>

  <!-- Layout Sidebar + Canvas -->
  <div class="stenciler-layout">
    <aside class="stenciler-sidebar">
      <!-- Outils : color picker, border slider, etc. -->
    </aside>
    <main class="stenciler-canvas">
      <canvas id="tarmac-canvas"></canvas>
    </main>
  </div>

</div>
```

**CSS complet** : Voir `MISSION_STENCILER_EXTENSION.md` lignes 242-388

---

### **PRIORITÉ 3 : Canvas Fabric.js** (J4)

**CDN à charger** :
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.1/fabric.min.js"></script>
```

**Initialisation** :
```javascript
let tarmacCanvas = null;

function initTarmacCanvas() {
  const canvasEl = document.getElementById('tarmac-canvas');
  const container = canvasEl.parentElement;

  tarmacCanvas = new fabric.Canvas('tarmac-canvas', {
    width: container.clientWidth,
    height: container.clientHeight,
    backgroundColor: '#fafafa',
    selection: true
  });

  console.log('✅ Canvas Fabric.js initialisé');
}
```

---

### **PRIORITÉ 4 : Event handlers avec mocks** (J5)

**Drag & Drop** :
```javascript
// Charger les mocks
let mockCorps = [];

async function loadMocks() {
  const response = await fetch('Frontend/3.STENCILER/mocks/4_corps_preview.json');
  const data = await response.json();
  mockCorps = data.corps;
  renderPreviewBand();
}

function renderPreviewBand() {
  const band = document.querySelector('.previews-band');
  band.innerHTML = '';

  mockCorps.forEach(corps => {
    const preview = createPreviewElement(corps);
    band.appendChild(preview);
  });
}

function createPreviewElement(corps) {
  const div = document.createElement('div');
  div.className = 'preview-corps';
  div.setAttribute('data-corps-id', corps.id);
  div.setAttribute('draggable', 'true');

  div.innerHTML = `
    <div class="preview-header" style="background:${corps.color};">
      ${corps.name}
    </div>
    <div class="preview-body">
      ${corps.organes.map(org => `
        <div class="preview-organe">${org.name}</div>
      `).join('')}
    </div>
  `;

  div.addEventListener('dragstart', (e) => handleDragStart(e, corps.id));
  div.addEventListener('dragend', handleDragEnd);

  return div;
}

function handleDragStart(e, corpsId) {
  e.dataTransfer.setData('corpsId', corpsId);
  e.target.classList.add('dragging');
}

function handleDragEnd(e) {
  e.target.classList.remove('dragging');
}

// Drop sur canvas
const canvasContainer = document.querySelector('.stenciler-canvas');

canvasContainer.addEventListener('dragover', (e) => {
  e.preventDefault();
  canvasContainer.style.borderColor = '#7aca6a';
});

canvasContainer.addEventListener('drop', (e) => {
  e.preventDefault();
  const corpsId = e.dataTransfer.getData('corpsId');
  const rect = canvasContainer.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;

  addCorpsToCanvas(corpsId, x, y);
});

function addCorpsToCanvas(corpsId, x, y) {
  const corps = mockCorps.find(c => c.id === corpsId);
  if (!corps) return;

  // Créer groupe Fabric.js (version simplifiée pour mock)
  const rect = new fabric.Rect({
    left: x,
    top: y,
    width: 200,
    height: 150,
    fill: 'white',
    stroke: corps.color,
    strokeWidth: 3,
    rx: 8,
    ry: 8
  });

  const text = new fabric.Text(corps.name, {
    left: x + 10,
    top: y + 10,
    fontSize: 14,
    fontWeight: 'bold',
    fill: corps.color
  });

  const group = new fabric.Group([rect, text]);
  tarmacCanvas.add(group);
  tarmacCanvas.renderAll();

  console.log(`✅ Corps ${corps.name} ajouté au canvas`);
}
```

---

## 🔄 SYNCHRONISATION AVEC CLAUDE

### Points de validation

**J6 (fin Phase 2 Backend)** :
- Claude : "API Backend prête, endpoints disponibles"
- KIMI : "Frontend prêt avec mocks, prêt à connecter API"
- **Code review croisé** : Vérifier compatibilité

**J8 (début intégration)** :
- KIMI remplace mocks par fetch() réels
- Claude debug si réponses API incorrectes

---

## ✅ VALIDATION FRANÇOIS-JEAN

**Points où tu attends validation FJ** :

1. **J3 : Design bande de previews**
   - Screenshot HTML/CSS rendu
   - Validation couleurs, layout, UX
   - **Attendre GO avant J4**

2. **J5 : Canvas Fabric.js fonctionnel (avec mocks)**
   - Démo : drag Corps → Canvas
   - Démo : outils sidebar (color picker)
   - **Attendre GO avant J6**

3. **J12 : Démo complète**
   - Workflow end-to-end avec API réelle
   - **Validation finale avant Phase 5**

---

## 📊 RÉSUMÉ PLANNING

```
J2 : Mocks JSON ✅
J3 : HTML/CSS Bande previews → VALIDATION FJ #1
J4 : Canvas Fabric.js setup
J5 : Event handlers (mocks) → VALIDATION FJ #2
J6 : JavaScript complet + code review avec Claude
J7 : Tests unitaires JS
J8-J11 : Intégration API réelle (remplacer mocks)
J12 : Démo complète → VALIDATION FJ #3
```

---

## 🚨 RÈGLES STRICTES

1. **NE PAS modifier lignes 1-1422** de `server_9998_v2.py`
2. **NE PAS appeler API Backend avant J8** (utiliser mocks)
3. **TOUJOURS demander validation FJ** avant de passer à la priorité suivante
4. **TOUJOURS créer backup** avant modification `server_9998_v2.py`

---

**Prêt à démarrer ?** Commence par PRIORITÉ 1 (mocks JSON).

— Claude Sonnet 4.5, Backend Lead
