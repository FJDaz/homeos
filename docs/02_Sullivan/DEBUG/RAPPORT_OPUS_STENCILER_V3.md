# RAPPORT OPUS — Stenciler V3 : Audit Post-Incident
**DATE : 2026-02-23 | AUTEUR : Claude Opus 4.6 | COMPLEMENTE : RAPPORT_HYPOTHESES_DEBUG.md (Gemini)**

---

> Le rapport Gemini couvrait le crash Service Worker (résolu par autodestruction sw.js).
> Ce rapport couvre **tout ce qui reste cassé ou fragile** après la résolution du SW.

---

## I. INFRASTRUCTURE

| Element | Etat |
|---|---|
| Serveur | PID 87787, port 9998, operationnel |
| URL active | `http://localhost:9998/stenciler` -> `stenciler_v3.html` |
| Sandbox | `?mode=sandbox` (bypass SW uniquement, pas le module cache browser) |
| SW | Autodestruction activee (`sw.js`) -- plus de cache agressif |
| Genome | Charge OK (`/api/genome` -> objet JSON) |

---

## II. ARCHITECTURE ACTIVE (FEATURE_CONFIG)

12 features montees dans `stenciler_v3_main.js` :

| # | Feature | Slot | Etat |
|---|---|---|---|
| 1 | HeaderFeature | `#slot-header` | OK |
| 2 | NavigationFeature | `#slot-navigation` | OK |
| 3 | GenomeSectionFeature | `#slot-genome` | OK |
| 4 | StyleSectionFeature | `#slot-style` (hidden) | OK |
| 5 | CanvasFeature | `#slot-canvas-zone` | OK (bugs internes -- voir III) |
| 6 | PreviewBandFeature | `#slot-preview-band` | OK |
| 7 | ComponentsZoneFeature | `#slot-sidebar-right` | OK |
| 8 | APIStatusFeature | `#slot-footer` | OK |
| 9 | PersistenceFeature | `body` | **CRASH** -- voir BUG D |
| 10 | **PrimitiveEditorFeature** | `body` | **BUGGE** -- voir BUG A |
| 11-13 | TSLPicker / ColorPalette / BorderSlider | sidebar-right | Slots vides (non cables) |

> NB : `_openAtomInspector` (mission 11B) **n'existe plus** dans `Canvas.feature.js` -- retire lors du pivot 12A.

---

## III. BUGS ACTIFS

### BUG A -- Panel PrimitiveEditor surgissant [CRITIQUE]

**Fichier** : `Canvas.feature.js` L785-836, L749, L782
**Symptome** : Un panel flottant (fond creme, bottom-left) apparait de facon apparemment aleatoire.

**Cause racine** -- triple defaut dans `_setupPrimitiveDrag()` :

**1) Listeners `window` enregistres immediatement (L834-835) :**
```js
prim.addEventListener('mousedown', onMouseDown);
window.addEventListener('mousemove', onMouseMove); // IMMEDIAT, pas dans onMouseDown
window.addEventListener('mouseup', onMouseUp);     // IMMEDIAT
```
Ils devraient etre dans `onMouseDown` et retires dans `onMouseUp`.
A chaque appel de `_setupPrimitiveDrag`, une nouvelle paire s'accumule sur `window`.

**2) Double appel par primitive :**
- `_enterGroupEdit()` L749 : appelle `_setupPrimitiveDrag(prim, node)` pour chaque primitive
- `_selectPrimitive()` L782 : appelle `_setupPrimitiveDrag(prim, ov)` une deuxieme fois
- -> Doublement systematique des listeners a chaque selection

**3) `mousedown` jamais nettoye :**
`_exitGroupEdit()` L860-865 retire les handlers `click` (via `prim._gc`) mais oublie les `mousedown`.
Apres N entrees/sorties du mode illustrateur, N handlers `mousedown` stale restent sur chaque primitive.
Ces handlers zombies declenchent des interactions parasites -> `_selectPrimitive` -> dispatch `primitive:selected` -> le PrimitiveEditor s'ouvre.

**Fix necessaire** : Mission 14A-FIX
- Stocker les handlers dans `prim._dragHandlers = {down, move, up}`
- Les retirer dans `_exitGroupEdit()`
- Deplacer `window.addEventListener` dans `onMouseDown`
- Supprimer le double appel L782

---

### BUG B -- Icones 14E-ICONS absentes [MINEUR]

**Fichier** : `AtomRenderer.js` L19, L269-278
**Symptome** : Aucune icone visible sur les atomes.

**Cause** :
```js
let type = nodeData.interaction_type || 'default'; // L19 -> 'default' si champ absent
const iconPath = ICONS[type];                       // L279 -> ICONS['default'] = undefined
```

La map `ICONS` couvre `click, submit, drag, view, upload, input, select, edit` mais **pas `'default'`**.
Or le genome actuel n'a probablement pas d'`interaction_type` sur la majorite des noeuds N3 -> `type = 'default'` systematiquement -> pas d'icone.

La ROADMAP 14E-ICONS prevoyait un `default -> layout` :
```
'default': 'M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z'
```

**Fix** : Ajouter cette cle a la map ICONS. Hotfix 1 ligne.

---

### BUG C -- Overlays "consoles" : inventaire exhaustif [POUR INFO]

| Source | Position | Declencheur | Actif en V3 ? |
|---|---|---|---|
| PrimitiveEditor panel | `fixed; bottom:60px; left:216px` | `primitive:selected` event | **OUI -- le coupable** |
| Sullivan Inspector widget | `fixed; bottom:20px; right:20px` | Chargement page | Non -- uniquement `viewer.html` (placeholder `{{custom_injection}}`) |
| Violation Constitutionnelle | `fixed; top:20px; right:20px` | `showViolationAlert()` | Non -- `semantic_bridge.js` non importe en V3 |
| Atom Inspector (11B) | `fixed; right:16px; top:80px` | `_openAtomInspector()` | Non -- methode retiree pivot 12A |

**Conclusion** : En V3 (`/stenciler`), le seul overlay fixed actif = PrimitiveEditor.
Le Sullivan Inspector n'apparait que sur `/` (viewer.html).
Si les deux sont visibles -> deux onglets differents ouverts.

---

### BUG D -- PersistenceFeature crash au mount [MINEUR]

**Decouvert dans** : `Logs.txt` L22-26
```
[DEBUG] Error init persistence: Error: Not implemented
    at PersistenceFeature.render (base.feature.js:18:11)
    at PersistenceFeature.mount (base.feature.js:29:31)
```

`PersistenceFeature` herite de `base.feature.js` sans override de `render()` -> appelle le parent qui throw `Not implemented`.
**Impact** : Aucune persistence locale (localStorage) des modifications du genome.
Le feature est montee en silence d'erreur (catch L56 de `stenciler_v3_main.js`) -- elle ne bloque rien mais ne fait rien non plus.

**Fix** : Soit implementer `render()`, soit retirer de FEATURE_CONFIG si la feature n'est pas prete.

---

### BUG E -- Events `node:selected` repetes en boucle [COSMETIC]

**Decouvert dans** : `Logs.txt` L30-55
```
ComponentsZone.feature.js:71 [ComponentsZone] Node selected for Nuance: n1_adaptation  (x6)
Canvas.feature.js:581 Layout persistent pour n1_adaptation (x3)
```

Le meme noeud est selectionne 6 fois consecutives pour un seul clic.
Cause probable : propagation d'evenements non stoppee dans la chaine `click` -> `_selectNode` -> dispatch `organe:selected` -> ComponentsZone ecoute -> re-dispatch ?
Pas bloquant mais polluant (performance + noise console).

---

## IV. ETAT DES MISSIONS PHASE 14

| Mission | Description | Statut | Notes |
|---|---|---|---|
| 14-CACHE | Fix cache ES6 | Livre | `?v=20260223` sur main.js. **Attention** : `?v=` casse avec server_9998_v2.py (traite query string comme nom de fichier -> 404) |
| 14A | Panel Edition Primitives | Livre / Bugge | PrimitiveEditor cree mais Bug A actif |
| 14E-ICONS | Icones SVG AtomRenderer | Livre / Incomplet | Cle `default` manquante dans ICONS map |
| 14B | Write-back Genome | En attente | Bloque par 14A non stabilise |
| 14C | Copie/Duplication | En attente | Bloque par 14B |
| 14D | Valise (Sullivan Embedded) | En attente | Bloque par 14B |
| 14E-WF | Nouveaux Wireframes (KIMI sandbox) | En attente | Independent |

---

## V. DETTE TECHNIQUE

| Risque | Localisation | Severite |
|---|---|---|
| Handlers `mousedown` zombies | `Canvas.feature.js` `_setupPrimitiveDrag` | **Haute** |
| `_setupPrimitiveDrag` appele 2x par primitive | L749 + L782 | **Haute** |
| PersistenceFeature crash silencieux | `base.feature.js:18` | Moyenne |
| Events selection repetes (x6 par clic) | `Canvas.feature.js` -> `ComponentsZone` | Moyenne |
| 14-CACHE : `?v=` casse server-side | `stenciler_v3.html` L43 | Moyenne |
| `Canvas.feature.js` > 900L (monolithe) | Seuil d'alerte = 500L | Moyenne |
| TSL/ColorPalette/BorderSlider montees mais vides | `stenciler_v3_main.js` | Faible |

---

## VI. PROCHAINES ACTIONS RECOMMANDEES

**Ordre de priorite :**

1. **Immediat** -- Desactiver le PrimitiveEditor (commenter 2 lignes dans `stenciler_v3_main.js` : import L21 + config L35) pour stopper les surgissements.

2. **Hotfix** -- Ajouter `'default': 'M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z'` dans la ICONS map de `AtomRenderer.js` (1 ligne).

3. **Mission 14A-FIX** (GEMINI, CODE DIRECT) -- Reecrire `_setupPrimitiveDrag` :
   - Stocker handlers dans `prim._dragHandlers`
   - Les retirer dans `_exitGroupEdit()`
   - Deplacer `window.addEventListener` dans `onMouseDown`
   - Supprimer le double appel L782

4. **Cleanup** -- Retirer PersistenceFeature de FEATURE_CONFIG (ou implementer `render()`).

5. **Mission 14B** peut demarrer apres 14A-FIX stabilise et valide FJD.

---

*Rapport etabli par Claude Opus 4.6 le 2026-02-23.*
*Complete RAPPORT_HYPOTHESES_DEBUG.md (Gemini, incident SW) et Logs.txt (console browser).*
