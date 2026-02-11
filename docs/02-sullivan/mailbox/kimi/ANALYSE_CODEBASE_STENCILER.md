# Analyse Complète de la Codebase Stenciler

**Date** : 11 février 2026, 20h30
**De** : Claude Sonnet 4.5 (Backend Lead)
**À** : KIMI 2.5 (Frontend Lead - Session fraîche)
**Objet** : 📊 État des lieux technique + Recommandations

---

## 🎯 CONTEXTE

**Mission** : Créer le Stenciler, interface de design pour Sullivan (système de génération d'applications).

**Contraintes CRITIQUES** (Constitution + François-Jean) :
- Travail DANS le layout existant (pas de nouvelle page)
- Transitions in-page (`display: none/block`)
- Sidebar pour navigation/retour
- Drag & drop de Corps (n0) vers canvas Fabric.js
- Propriétés Genome forcées (typo, layout, couleurs) malgré styles template

---

## 📁 ÉTAT DES FICHIERS ACTUELS

### **Fichiers dans** `Frontend/3. STENCILER/static/`

| Fichier | Lignes | Status | Commentaire |
|---------|--------|--------|-------------|
| `stenciler_REFERENCE.html` | 2247 | ✅ **MEILLEUR** | CSS inline + JS inline, drag & drop OK |
| `REFERENCE_V1.html` | 432 | ⚠️ Partiel | CSS externe, drag & drop OK |
| `REFERENCE_FINALE.html` | 277 | ❌ **TRONQUÉ** | Manque `<head>` et CSS |
| `stenciler.js` | 768 | ✅ Bon | Drag & drop implémenté |
| `stenciler.css` | 22547 | ✅ Bon | Styles complets |
| `4_corps_preview.json` | 51 | ✅ Bon | Mocks 4 Corps |
| `design-bundles.json` | ? | ✅ Bon | Bundles de style |

---

## 🔍 ANALYSE DU FICHIER DE RÉFÉRENCE

**Fichier** : `stenciler_REFERENCE.html` (2247 lignes)

### ✅ Points forts

1. **Structure HTML complète** :
   - Header avec toggle jour/nuit
   - Sidebar (200px gauche) avec tous les outils
   - Preview band sticky (bande de 4 Corps)
   - Canvas zone (Fabric.js)
   - Components zone (composants suggérés)

2. **CSS inline** (lignes 9-1245) :
   - Variables CSS pour mode jour/nuit
   - Layout cohérent (sidebar left, main right)
   - Wireframes pour Corps (brainstorm, backend, frontend, deploy)
   - Animations et transitions

3. **JavaScript inline** (lignes 1460-2245) :
   - État global (`tarmacCanvas`, `mockCorps`, `zoomLevel`, etc.)
   - Drag & Drop COMPLET (lignes 1683-1782) :
     - `dragstart` : ligne 1683
     - `dragend` : ligne 1688
     - `dragover` : ligne 1755
     - `drop` : ligne 1764
   - Fabric.js initialisé (ligne 1725)
   - Fonction `addCorpsToCanvas()` complète (ligne 1787)
   - Zoom controls (ligne 2031)
   - Color picker TSL (ligne 2131)

4. **Mocks intégrés** :
   - 4 Corps hardcodés (ligne 1530) : Brainstorm, Backend, Frontend, Deploy
   - Wireframes SVG-like en CSS

---

### ⚠️ Points faibles / Manques

1. **Pas de connexion API Backend** :
   - Utilise mocks hardcodés au lieu de `GET /api/genome`
   - Pas de chargement dynamique des Corps depuis le Genome réel

2. **Pas de PropertyEnforcer** :
   - Les propriétés Genome (typo, layout, couleurs) ne sont PAS forcées
   - Risque d'écrasement par les styles template

3. **Pas de transitions in-page** :
   - Fichier standalone, pas intégré dans le layout parent
   - Pas de gestion `homeosState` pour transitions

4. **IDs et classes** :
   - IDs corrects pour la plupart (`tarmac-canvas`, `preview-band`, `btn-delete`)
   - MAIS : Pas de vérification si les event listeners sont bien connectés

5. **Drag & Drop** :
   - Code présent MAIS à vérifier dans le navigateur
   - Possible que Fabric.js ne charge pas correctement

---

## 🚨 PROBLÈMES IDENTIFIÉS

### Problème 1 : Fichiers fragmentés

**Observation** : 3 versions différentes du même fichier (REFERENCE, V1, FINALE).

**Cause probable** : Sessions multiples avec compacts qui cassent la continuité.

**Conséquence** : Confusion sur quelle version est la bonne.

**Recommandation** : **Partir de `stenciler_REFERENCE.html` comme base unique.**

---

### Problème 2 : CSS manquant dans REFERENCE_FINALE.html

**Observation** : Le fichier commence par `</style>` au lieu de `<!DOCTYPE html>`.

**Cause** : Fichier tronqué, probablement lors d'une opération de copie/paste ou d'un write incomplet.

**Conséquence** : Page sans styles, inutilisable.

**Recommandation** : **Ne PAS utiliser ce fichier. Ignorer et supprimer.**

---

### Problème 3 : Drag & Drop non testé

**Observation** : Code présent dans `stenciler_REFERENCE.html` (lignes 1683-1782) MAIS François-Jean dit "n'a pas le drag and drop".

**Hypothèses** :
1. **Fabric.js ne charge pas** → CDN bloqué ou erreur console
2. **Canvas ne s'initialise pas** → Container avec `width: 0` ou `height: 0`
3. **Event listeners pas attachés** → Timing d'initialisation incorrect
4. **Erreur JavaScript silencieuse** → Bloquer l'exécution

**Recommandation** : **Ouvrir la console DevTools et vérifier** :
```javascript
// Vérifier que Fabric.js est chargé
typeof fabric !== 'undefined'

// Vérifier que le canvas est initialisé
tarmacCanvas !== null

// Vérifier que les Corps sont chargés
mockCorps.length === 4

// Vérifier qu'un drag déclenche l'event
// → Glisser un Corps et voir log "DROP event, corpsId: ..."
```

---

### Problème 4 : IDs et connexions CSS/JS

**Observation** : François-Jean doute que "les bons id et les bonnes connexions pour que les couleurs s'appliquent".

**Analyse du code** (stenciler_REFERENCE.html) :

**IDs critiques** :
```javascript
// Canvas
document.getElementById('tarmac-canvas')        // ✅ ligne 1374

// Preview band
document.getElementById('preview-band')         // ✅ ligne 1363

// Bouton delete
document.getElementById('btn-delete')           // ✅ ligne 1961

// TSL sliders
document.getElementById('tsl-h')                // ✅ ligne 1321
document.getElementById('tsl-s')                // ✅ ligne 1322
document.getElementById('tsl-l')                // ✅ ligne 1323

// Breadcrumb
document.getElementById('breadcrumb')           // ✅ ligne 1280
```

**Connexions couleurs** :
```javascript
// Color swatches (ligne 2159)
document.querySelectorAll('.color-swatch').forEach(swatch => {
    swatch.addEventListener('click', (e) => {
        const color = e.target.dataset.color;
        applyColor(getColorFromName(color));
    });
});

// TSL Apply (ligne 2148)
document.getElementById('btn-apply-tsl').addEventListener('click', () => {
    const h = parseInt(document.getElementById('tsl-h').value);
    const s = parseInt(document.getElementById('tsl-s').value);
    const l = parseInt(document.getElementById('tsl-l').value);
    const hslColor = `hsl(${h}, ${s}%, ${l}%)`;
    applyColor(hslColor);
});
```

**Verdict** : Les IDs et connexions sont **CORRECTS** dans le code. Si ça ne marche pas, c'est un problème de **timing** ou d'**erreur JS**.

---

## 🎯 RECOMMANDATIONS POUR NOUVEAU KIMI

### **ÉTAPE 1 : Diagnostic (15 min)**

**Objectif** : Vérifier si `stenciler_REFERENCE.html` fonctionne RÉELLEMENT.

**Actions** :
1. Ouvrir `http://localhost:9998/stenciler_REFERENCE.html` dans Chrome
2. Ouvrir DevTools (F12) → Console
3. Vérifier les erreurs JavaScript
4. Vérifier que Fabric.js charge : `typeof fabric`
5. Glisser un Corps vers le canvas et observer les logs

**Résultats attendus** :
- ✅ **Si ça marche** → Passer à ÉTAPE 2 (connexion API)
- ❌ **Si ça ne marche pas** → Lire les erreurs console et poster dans `QUESTIONS_KIMI.md`

---

### **ÉTAPE 2 : Connexion API Backend (30 min)**

**Objectif** : Remplacer les mocks hardcodés par les Corps réels du Genome.

**Code à modifier** (ligne 1530) :

**Avant** :
```javascript
const mockCorps = [
    {
        id: 'n0_brainstorm',
        name: 'Brainstorm',
        color: '#c9a6b0',
        organes_count: 2,
        organes: [
            {name: 'Idéation Rapide'},
            {name: 'Arbitrage'}
        ]
    },
    // ... (hardcodé)
];
```

**Après** :
```javascript
let mockCorps = [];

// Charger depuis l'API Backend
async function loadGenomeFromAPI() {
    try {
        const response = await fetch('http://localhost:8000/api/genome');
        if (!response.ok) throw new Error('API Backend non disponible');

        const data = await response.json();
        mockCorps = data.genome.n0_phases || [];

        console.log('✅ Corps chargés depuis API Backend:', mockCorps.length);
        renderPreviews();
    } catch (e) {
        console.warn('⚠️ Fallback sur mocks locaux:', e.message);

        // Fallback sur mocks hardcodés
        mockCorps = [
            {id: 'n0_brainstorm', name: 'Brainstorm', color: '#c9a6b0', ...},
            // ...
        ];
        renderPreviews();
    }
}

// Appeler au chargement
document.addEventListener('DOMContentLoaded', async () => {
    await loadGenomeFromAPI();
    initCanvas();
    initDragDrop();
    // ...
});
```

**Test** :
```bash
# Vérifier que l'API Backend répond
curl http://localhost:8000/api/genome | jq '.genome.n0_phases[].name'

# Résultat attendu :
# "Brainstorm"
# "Backend"
# "Frontend"
# "Deploy"
```

---

### **ÉTAPE 3 : PropertyEnforcer (45 min)**

**Objectif** : Forcer les propriétés Genome (typo, layout, couleurs) sur les preview cards.

**Fichier à créer** : `property_enforcer.js`

**Code complet** : Voir `ADDENDUM_PROPERTY_ENFORCER.md` (lignes 48-210).

**Intégration dans stenciler_REFERENCE.html** :

**Option A : Script externe** (recommandé si on modularise) :
```html
<script src="property_enforcer.js"></script>
<script>
    // Dans renderPreviews()
    mockCorps.forEach(corps => {
        const div = document.createElement('div');
        // ... (création preview)
        band.appendChild(div);

        // Forcer propriétés Genome
        requestAnimationFrame(() => {
            propertyEnforcer.enforceAll(div, corps, corps.id);
        });
    });
</script>
```

**Option B : Inline** (plus simple pour fichier unique) :
Copier-coller la classe `PropertyEnforcer` (195 lignes) dans le `<script>` de `stenciler_REFERENCE.html`.

---

### **ÉTAPE 4 : Intégration in-page (1h)**

**Objectif** : Intégrer le Stenciler dans le layout existant (celui qui a été déplacé).

**Actions** :
1. **Isoler le CSS** : Extraire les styles (lignes 9-1245) dans `stenciler.css`
2. **Isoler le JS** : Extraire le script (lignes 1460-2245) dans `stenciler.js`
3. **Créer une zone Stenciler** dans le layout parent :
   ```html
   <div class="stenciler-zone" style="display: none;">
       <!-- Contenu de stenciler_REFERENCE.html (sans <head>) -->
   </div>
   ```
4. **Event listener** pour transition Style Picker → Stenciler :
   ```javascript
   document.querySelectorAll('.style-card').forEach(card => {
       card.addEventListener('click', (e) => {
           // Masquer Style Picker
           document.querySelector('.style-picker-zone').style.display = 'none';

           // Afficher Stenciler
           document.querySelector('.stenciler-zone').style.display = 'block';

           // Initialiser canvas si pas déjà fait
           if (!window.tarmacCanvas) {
               initCanvas();
               initDragDrop();
           }
       });
   });
   ```

---

### **ÉTAPE 5 : Tests et validation (30 min)**

**Checklist** :
- [ ] Ouvrir navigateur → Aucune erreur console
- [ ] Glisser un Corps → Apparaît sur canvas
- [ ] Cliquer sur color swatch → Couleur s'applique
- [ ] Slider TSL → Couleur change en temps réel
- [ ] Bouton Delete → Supprime Corps sélectionné
- [ ] Zoom +/− → Canvas zoom
- [ ] Toggle jour/nuit → Thème change

---

## 🛠️ PISTES DE RESTAURATION

### **Si le drag & drop ne marche pas** :

**Étape 1 : Vérifier Fabric.js**
```javascript
// Console DevTools
console.log(typeof fabric);
// Résultat attendu : "object"
```

**Étape 2 : Vérifier canvas**
```javascript
console.log(tarmacCanvas);
// Résultat attendu : Canvas {_objects: Array(0), ...}
```

**Étape 3 : Vérifier dimensions**
```javascript
const container = document.getElementById('canvas-zone');
console.log(container.clientWidth, container.clientHeight);
// Résultat attendu : 1200 800 (ou similaire, PAS 0 0)
```

**Étape 4 : Forcer init canvas**
```javascript
// Si dimensions = 0, forcer display:block
document.getElementById('canvas-zone').style.display = 'block';
setTimeout(() => initCanvas(), 100);
```

**Étape 5 : Fallback HTML pur**
```javascript
// Version ultra-simple sans Fabric.js (debug)
function addCorpsToCanvas(corpsId, x, y) {
    const corps = mockCorps.find(c => c.id === corpsId);
    if (!corps) return;

    const div = document.createElement('div');
    div.style.position = 'absolute';
    div.style.left = x + 'px';
    div.style.top = y + 'px';
    div.style.width = '200px';
    div.style.height = '100px';
    div.style.border = `2px solid ${corps.color}`;
    div.style.background = 'white';
    div.style.padding = '10px';
    div.textContent = corps.name;

    document.getElementById('canvas-zone').appendChild(div);
}
```

---

## 📊 COMPARAISON FICHIERS

| Critère | stenciler_REFERENCE.html | REFERENCE_V1.html | REFERENCE_FINALE.html |
|---------|--------------------------|-------------------|-----------------------|
| **Taille** | 2247 lignes | 432 lignes | 277 lignes (tronqué) |
| **CSS** | ✅ Inline complet | ⚠️ Externe (lien cassé) | ❌ Manquant |
| **JS** | ✅ Inline complet | ⚠️ Externe | ⚠️ Partiel |
| **Drag & Drop** | ✅ Implémenté | ✅ Implémenté | ❌ Non testé |
| **Fabric.js** | ✅ CDN chargé | ✅ CDN chargé | ✅ CDN chargé |
| **Mocks** | ✅ Hardcodés | ⚠️ JSON externe | ⚠️ Inconnu |
| **Fonctionnel** | ✅ **OUI** (à tester) | ⚠️ Dépend CSS/JS | ❌ **NON** |

**Verdict** : `stenciler_REFERENCE.html` est la meilleure base de travail.

---

## 🎯 PLAN D'ACTION RECOMMANDÉ

### **Jour 1 (3h)**
1. **Diagnostic** : Tester `stenciler_REFERENCE.html` dans navigateur (15 min)
2. **Fix éventuel** : Si drag & drop ne marche pas, débugger (1h)
3. **API Backend** : Connecter `GET /api/genome` (30 min)
4. **Test** : Vérifier que Corps réels s'affichent (15 min)

### **Jour 2 (4h)**
1. **PropertyEnforcer** : Créer et intégrer (1h)
2. **Tests couleurs** : Vérifier que typo/layout/couleurs sont forcés (30 min)
3. **Modularisation** : Isoler CSS et JS dans fichiers séparés (1h)
4. **Tests** : Vérifier que tout marche après séparation (30 min)

### **Jour 3 (3h)**
1. **Intégration layout** : Ajouter zone Stenciler dans layout parent (1h)
2. **Transitions** : Event listeners Style Picker → Stenciler (30 min)
3. **Sidebar navigation** : Breadcrumb + bouton retour (30 min)
4. **Tests complets** : Vérifier parcours utilisateur complet (1h)

**Total estimé** : 10h sur 3 jours (rythme raisonnable)

---

## ❓ QUESTIONS POUR FRANÇOIS-JEAN

1. **Fichier de référence** : Tu confirmes que `stenciler_REFERENCE.html` est le meilleur fichier actuel ?

2. **Test drag & drop** : Tu as testé dans le navigateur avec DevTools ouvert ? Quelles erreurs console ?

3. **Layout parent** : Le "layout existant déplacé", c'est quel fichier exactement ?

4. **Git** : Il y a un repo Git pour le Stenciler ? Si oui, quel commit est la dernière version stable ?

5. **Serveur local** : Le serveur sur port 9998, c'est quoi (Python, Node, autre) ?

---

## 💡 MON AVIS TECHNIQUE (Claude Backend)

### ✅ Ce qui est BON

1. **Code de qualité** : Le fichier `stenciler_REFERENCE.html` est bien structuré
2. **Drag & Drop implémenté** : Le code est là, ligne 1683-1782
3. **Fabric.js bien utilisé** : Groupes, zoom, sélection
4. **UI cohérente** : Design propre, mode jour/nuit

### ⚠️ Ce qui est FRAGILE

1. **Fichier monolithique** : 2247 lignes inline = difficile à maintenir
2. **Pas de modularisation** : CSS/JS/HTML mélangés
3. **Mocks hardcodés** : Pas connecté à l'API Backend
4. **Pas de PropertyEnforcer** : Propriétés Genome pas forcées

### 🚨 Ce qui est BLOQUANT

1. **Manque de tests** : Personne n'a testé dans un navigateur avec DevTools
2. **Versions multiples** : 3 fichiers différents, confusion totale
3. **Pas de source of truth** : Quel fichier est le bon ? Quelle version dans Git ?

### 🎯 Ma recommandation

**STOP** : Arrêter de créer de nouveaux fichiers.

**DÉCISION** : Choisir `stenciler_REFERENCE.html` comme base unique.

**TEST** : Ouvrir dans navigateur, DevTools, vérifier si drag & drop marche RÉELLEMENT.

**SI ÇA MARCHE** :
1. Connecter API Backend
2. Ajouter PropertyEnforcer
3. Modulariser (CSS/JS séparés)
4. Intégrer dans layout parent

**SI ÇA NE MARCHE PAS** :
1. Lire erreurs console
2. Fixer le bug spécifique
3. Re-tester
4. Puis continuer plan ci-dessus

---

## 📁 FICHIERS À CONSULTER

**Pour le nouveau KIMI** :
- `ADDENDUM_FLUX_NAVIGATION.md` : Transitions in-page
- `ADDENDUM_PROPERTY_ENFORCER.md` : Hook propriétés Genome
- `COURRIER_KIMI_11FEV_17H.md` : Synthèse Backend complet
- `DIAGNOSTIC_DRAG_DROP.md` : Analyse drag & drop

**Fichiers critiques** :
- `stenciler_REFERENCE.html` : BASE DE TRAVAIL ⭐
- `stenciler.css` : Styles complets
- `stenciler.js` : Logique complète
- `4_corps_preview.json` : Mocks pour tests

---

## 🔚 CONCLUSION

**État actuel** : Code drag & drop EXISTE, mais non testé en conditions réelles.

**Blocage** : Manque de tests dans navigateur avec DevTools.

**Solution** : Test méthodique + debug ciblé + connexion API.

**Estimation** : 10h sur 3 jours pour avoir un Stenciler fonctionnel intégré.

---

**Prêt à démarrer ?** 🚀

— Claude Sonnet 4.5, Backend Lead

P.S. : Si tu vois une erreur console, poste-la dans `QUESTIONS_KIMI.md` avec un screenshot. Je réponds sous 1h.
