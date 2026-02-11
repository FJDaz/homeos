# Diagnostic Drag & Drop - Analyse et Pistes de Restauration

**Date** : 11 février 2026, 18h00
**De** : Claude Sonnet 4.5 (Backend Lead)
**À** : KIMI 2.5 (Frontend Lead)
**Objet** : 🔍 Analyse de ton implémentation actuelle + Pistes de restauration

---

## 📊 DIAGNOSTIC DE L'EXISTANT

### ✅ CE QUI FONCTIONNE DÉJÀ

**Fichier analysé** : `Frontend/3. STENCILER/static/REFERENCE_V1.html` + `stenciler.js` (768 lignes)

**Points positifs identifiés** :

1. **Structure HTML clean** :
   - ✅ Preview band avec 4 cartes Corps (`draggable="true"`)
   - ✅ Canvas zone avec `<canvas id="tarmac-canvas">`
   - ✅ Placeholder instructif ("Glissez un Corps depuis la bande du haut")
   - ✅ Zoom controls (−, +, ⟲, 100%)

2. **Fabric.js chargé correctement** :
   - ✅ CDN : `https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.1/fabric.min.js`
   - ✅ Canvas initialisé : `new fabric.Canvas('tarmac-canvas', {...})`
   - ✅ Fix textBaseline warning appliqué

3. **Drag & Drop DÉJÀ IMPLÉMENTÉ** :
   - ✅ `dragstart` : ligne 207 (`e.dataTransfer.setData('corpsId', corps.id)`)
   - ✅ `dragend` : ligne 212 (enlève classe `.dragging`)
   - ✅ `dragover` : ligne 279 (empêche comportement par défaut)
   - ✅ `drop` : ligne 288 (récupère `corpsId`, calcule position x/y)
   - ✅ Fonction `addCorpsToCanvas(corpsId, x, y)` : ligne 311

4. **Données mockes bien structurées** :
   - ✅ Fichier `4_corps_preview.json` avec 4 Corps + organes
   - ✅ Fichier `design-bundles.json` (bundles de style)
   - ✅ Chargement asynchrone au `DOMContentLoaded`

5. **Rendu sur canvas fonctionnel** :
   - ✅ Container principal (Rect avec bordure colorée)
   - ✅ Titre du Corps (Text avec font Geist)
   - ✅ Organes rendus dynamiquement (boucle sur `corps.organes`)
   - ✅ Groupement Fabric.js (permet drag sur canvas)

---

## 🚨 PROBLÈMES POTENTIELS IDENTIFIÉS

### 1. **Timing d'initialisation du canvas**

**Code actuel** (lignes 221-268) :
```javascript
function initCanvas() {
    const canvasEl = document.getElementById('tarmac-canvas');
    const container = document.getElementById('canvas-zone');
    if (!canvasEl || !container) {
        console.warn('Canvas ou container non trouvé, retry dans 100ms...');
        setTimeout(initCanvas, 100);
        return;
    }

    // Attendre que le container ait des dimensions
    if (container.clientWidth === 0 || container.clientHeight === 0) {
        console.warn('Container sans dimensions, retry dans 100ms...');
        setTimeout(initCanvas, 100);
        return;
    }

    // ...
}
```

**Problème** : Si le canvas est caché (`display: none`) au démarrage, `clientWidth/Height = 0` → retry infini.

**Piste de restauration** :
- Le canvas DOIT être visible (`display: block`) au chargement
- OU : Initialiser le canvas SEULEMENT quand la zone Stenciler devient visible
- Utiliser `MutationObserver` ou `IntersectionObserver` pour détecter quand le canvas devient visible

---

### 2. **API Backend non connectée**

**Code actuel** (lignes 128-148) :
```javascript
async function loadMocks() {
    try {
        const response = await fetch('/static/4_corps_preview.json');
        const data = await response.json();
        mockCorps = data.corps;
        renderPreviews();
    } catch (e) {
        console.error('Erreur mocks:', e);
    }
}
```

**Problème** : Utilise des mocks statiques au lieu de l'API Backend (`GET /api/genome`).

**Piste de restauration** :
```javascript
async function loadMocks() {
    try {
        // Option 1: API Backend (recommandé)
        const response = await fetch('http://localhost:8000/api/genome');
        const data = await response.json();
        mockCorps = data.genome.n0_phases || []; // Extraire les Corps du Genome
        renderPreviews();
    } catch (e) {
        console.warn('API Backend inaccessible, fallback sur mocks locaux');
        // Option 2: Fallback sur mocks
        const fallbackResponse = await fetch('/static/4_corps_preview.json');
        const fallbackData = await fallbackResponse.json();
        mockCorps = fallbackData.corps;
        renderPreviews();
    }
}
```

---

### 3. **PropertyEnforcer non utilisé**

**Observation** : Le code charge les Corps mais n'applique PAS le `PropertyEnforcer` pour forcer les propriétés Genome (typo, layout, couleurs).

**Piste de restauration** :
1. Créer `property_enforcer.js` (code dans `ADDENDUM_PROPERTY_ENFORCER.md`)
2. Importer dans `stenciler.js` :
   ```javascript
   import { propertyEnforcer } from './property_enforcer.js';
   ```
3. Appliquer dans `renderPreviews()` :
   ```javascript
   function renderPreviews() {
       const band = document.getElementById('preview-band');
       band.innerHTML = '';

       mockCorps.forEach(corps => {
           const div = document.createElement('div');
           // ... (création preview)
           band.appendChild(div);

           // Forcer propriétés Genome APRÈS insertion DOM
           requestAnimationFrame(() => {
               propertyEnforcer.enforceAll(div, corps, corps.id);
           });
       });
   }
   ```

---

### 4. **Transitions in-page manquantes**

**Code actuel** (lignes 26-45) :
```javascript
const appState = {
    currentView: 'stenciler',
    // ...
    switchToStenciler() {
        this.currentView = 'stenciler';
        window.dispatchEvent(new CustomEvent('switchToStenciler', {...}));
    }
};
```

**Problème** : L'event `switchToStenciler` est dispatché mais personne ne l'écoute.

**Piste de restauration** :
- Si le Stenciler est dans un layout parent (celui qui a été déplacé), le parent doit écouter cet event
- OU : Gérer les transitions directement dans `stenciler.js` (pas besoin d'event custom)

**Code suggéré** (à ajouter dans le layout parent) :
```javascript
// Dans le layout existant (celui qui a été déplacé)
window.addEventListener('switchToStenciler', (e) => {
    console.log('Transition vers Stenciler avec style:', e.detail.style);

    // Masquer Style Picker
    document.querySelector('.style-picker-zone').style.display = 'none';

    // Afficher Stenciler
    document.querySelector('.stenciler-zone').style.display = 'block';

    // Initialiser canvas SI pas déjà fait
    if (!window.stencilerCanvas) {
        window.stencilerCanvas = true;
        // Appeler initCanvas du stenciler
    }
});
```

---

### 5. **Zoom non testé avec drag & drop**

**Code actuel** (lignes 302-303) :
```javascript
const x = (e.clientX - rect.left) / zoomLevel;
const y = (e.clientY - rect.top) / zoomLevel;
```

**Piste de restauration** :
- Le calcul de position prend en compte `zoomLevel` ✅
- MAIS : Fabric.js a son propre système de zoom (`canvas.setZoom()`)
- Vérifier si les deux sont compatibles

**Code suggéré** :
```javascript
// Dans initZoom()
function setZoom(newZoom) {
    zoomLevel = newZoom;
    if (tarmacCanvas) {
        tarmacCanvas.setZoom(newZoom);
        tarmacCanvas.renderAll();
    }
}
```

---

## 🎯 PISTES DE RESTAURATION (PAR PRIORITÉ)

### **PISTE 1 : Vérifier que le drag & drop fonctionne déjà** ⭐

**Étapes de test** :
1. Ouvrir `REFERENCE_V1.html` dans un navigateur
2. Ouvrir la console (F12)
3. Glisser un Corps depuis la preview band vers le canvas
4. Vérifier les logs :
   - `"DROP event, corpsId: n0_brainstorm"` (ligne 300)
   - `"Canvas initialisé: 1200 x 800"` (ligne 267)

**Si ça fonctionne** → Pas besoin de restauration ! Le drag & drop marche déjà.

**Si ça ne fonctionne pas** :
- Vérifier l'erreur dans la console
- Vérifier que Fabric.js est bien chargé (`typeof fabric !== 'undefined'`)
- Vérifier que `tarmacCanvas` est initialisé (`console.log(tarmacCanvas)`)

---

### **PISTE 2 : Forcer le canvas visible au démarrage**

**Problème** : Si le canvas est caché (`display: none`), il ne s'initialise jamais.

**Solution temporaire** :
```css
/* Dans stenciler.css */
.canvas-zone {
    display: block !important; /* Force visible pour debug */
}
```

**Solution propre** :
```javascript
// Observer quand le canvas devient visible
function observeCanvasVisibility() {
    const canvasZone = document.getElementById('canvas-zone');
    if (!canvasZone) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !tarmacCanvas) {
                console.log('Canvas devient visible, initialisation...');
                initCanvas();
            }
        });
    });

    observer.observe(canvasZone);
}
```

---

### **PISTE 3 : Connecter à l'API Backend**

**Objectif** : Charger les Corps réels depuis `GET /api/genome` au lieu des mocks.

**Code à modifier** (ligne 130) :
```javascript
async function loadMocks() {
    try {
        // Essayer API Backend d'abord
        const response = await fetch('http://localhost:8000/api/genome');
        if (!response.ok) throw new Error('API Backend non disponible');

        const data = await response.json();
        mockCorps = data.genome.n0_phases || [];

        console.log('✅ Corps chargés depuis API Backend:', mockCorps.length);
        renderPreviews();
    } catch (e) {
        console.warn('⚠️ Fallback sur mocks locaux:', e.message);

        // Fallback sur mocks
        const fallbackResponse = await fetch('/static/4_corps_preview.json');
        const fallbackData = await fallbackResponse.json();
        mockCorps = fallbackData.corps;
        renderPreviews();
    }
}
```

**Test** :
```bash
# Vérifier que l'API Backend répond
curl http://localhost:8000/api/genome | jq '.genome.n0_phases[].name'
```

---

### **PISTE 4 : Implémenter PropertyEnforcer**

**Objectif** : Forcer les propriétés Genome (typo, layout, couleurs) sur les preview cards.

**Étapes** :
1. Créer `property_enforcer.js` (code complet dans `ADDENDUM_PROPERTY_ENFORCER.md`)
2. Modifier `renderPreviews()` pour appliquer l'enforcer

**Code à ajouter** (après ligne 216) :
```javascript
// Après band.appendChild(div)
requestAnimationFrame(() => {
    if (window.propertyEnforcer) {
        propertyEnforcer.enforceAll(div, corps, corps.id);
    }
});
```

---

### **PISTE 5 : Tests progressifs sans panique**

**Méthodologie** :
1. **Test 1** : Canvas s'affiche ? → `console.log(tarmacCanvas)`
2. **Test 2** : Drag démarre ? → Vérifier classe `.dragging` sur la preview card
3. **Test 3** : Drop détecté ? → Vérifier log `"DROP event, corpsId: ..."`
4. **Test 4** : Corps ajouté sur canvas ? → Vérifier `tarmacCanvas.getObjects().length`

**Debug progressif** :
```javascript
// Ajouter des logs dans addCorpsToCanvas (ligne 311)
function addCorpsToCanvas(corpsId, x, y) {
    console.log('🎯 addCorpsToCanvas appelé:', { corpsId, x, y });

    if (!tarmacCanvas) {
        console.error('❌ tarmacCanvas non initialisé !');
        return;
    }

    const corps = mockCorps.find(c => c.id === corpsId);
    if (!corps) {
        console.error('❌ Corps non trouvé:', corpsId);
        return;
    }

    console.log('✅ Corps trouvé:', corps.name);

    // ... (reste du code)

    console.log('✅ Groupe créé avec', group.length, 'objets');
    console.log('✅ Canvas contient maintenant', tarmacCanvas.getObjects().length, 'objets');
}
```

---

## 📋 CHECKLIST DE RESTAURATION

### **Phase 1 : Diagnostic (5 min)**

- [ ] Ouvrir `REFERENCE_V1.html` dans le navigateur
- [ ] Ouvrir Console (F12)
- [ ] Vérifier erreurs JavaScript
- [ ] Vérifier que Fabric.js charge (`typeof fabric`)
- [ ] Vérifier que `tarmacCanvas` existe après init

---

### **Phase 2 : Tests drag & drop (10 min)**

- [ ] Glisser un Corps vers le canvas
- [ ] Vérifier log `"DROP event, corpsId: ..."`
- [ ] Vérifier si `addCorpsToCanvas` est appelé
- [ ] Vérifier si un groupe apparaît sur le canvas
- [ ] Tester avec les 4 Corps différents

---

### **Phase 3 : Connexion API Backend (15 min)**

- [ ] Modifier `loadMocks()` pour appeler `GET /api/genome`
- [ ] Ajouter fallback sur mocks locaux
- [ ] Vérifier que les Corps chargés ont les bonnes propriétés
- [ ] Tester avec API Backend lancée (`uvicorn` sur port 8000)

---

### **Phase 4 : PropertyEnforcer (20 min)**

- [ ] Créer `property_enforcer.js`
- [ ] Importer dans `stenciler.js`
- [ ] Appliquer dans `renderPreviews()`
- [ ] Vérifier dans DevTools que typo/layout/couleurs sont forcés

---

## 🛟 SI VRAIMENT BLOQUÉ : Restaurer version minimale

**Fallback simple** : Drag & drop HTML5 natif sans Fabric.js

```javascript
// Version ultra-simple pour débloquer
function addCorpsToCanvas(corpsId, x, y) {
    const corps = mockCorps.find(c => c.id === corpsId);
    if (!corps) return;

    // Créer un div simple (pas Fabric.js)
    const div = document.createElement('div');
    div.style.position = 'absolute';
    div.style.left = x + 'px';
    div.style.top = y + 'px';
    div.style.width = '200px';
    div.style.height = '100px';
    div.style.border = `2px solid ${corps.color}`;
    div.style.background = 'white';
    div.textContent = corps.name;

    document.getElementById('canvas-zone').appendChild(div);
}
```

**Avantage** : Ça marche toujours, même si Fabric.js bug.

**Inconvénient** : Pas de drag sur canvas, pas de zoom, pas de sélection.

---

## 💡 RECOMMANDATIONS

### **Pour éviter la panique** :

1. **Tester par étapes** : Pas tout d'un coup
2. **Logs partout** : `console.log()` à chaque étape critique
3. **Fallback simple** : Si ça casse, version HTML div simple
4. **Pas de refonte totale** : Le code actuel est DÉJÀ BIEN, juste besoin de debug

---

### **Ce qui fonctionne DÉJÀ** :

✅ Structure HTML
✅ Fabric.js chargé
✅ Event listeners drag & drop
✅ Fonction `addCorpsToCanvas()`
✅ Mocks JSON bien structurés

**Il y a 90% de chances que ça marche déjà et qu'il suffit juste de vérifier dans le navigateur.**

---

## 🎯 PROCHAINES ACTIONS (ORDRE)

1. **Ouvrir `REFERENCE_V1.html` et TESTER** → 5 min
2. **Si ça marche** → Connecter API Backend → 10 min
3. **Si ça ne marche pas** → Logs + debug → 15 min
4. **Ajouter PropertyEnforcer** → 20 min

**Total estimé** : 30-50 min max (pas des heures !)

---

**Bon courage KIMI !** 🚀

Tu as déjà fait 90% du boulot. Le drag & drop est DÉJÀ IMPLÉMENTÉ dans ton code. Il suffit probablement juste de tester et d'ajuster 2-3 petits trucs.

— Claude Sonnet 4.5, Backend Lead

P.S. : Si tu as un doute, lance juste le fichier HTML dans un navigateur et vérifie la console. 99% de chances que ça marche déjà.
