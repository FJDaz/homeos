# Strategic Roadmap Stenciler V3

## Vision 2026 : Le Majordome de Code (Sullivan Architecture)
Garantir une transition fluide du Genome (DNA fonctionnel) vers le Stencil (UI/UX) tout en préservant la fidélité visuelle V1.

---

## ✅ Phases 1→9D COMPLÈTES

Archivées dans [ROADMAP_ACHIEVED.md](file:///Users/francois-jeandazin/AETHERFLOW/Frontend/4. COMMUNICATION/ROADMAP_ACHIEVED.md).

---

## Phase 10 — Detail Cascade : Du Grain Atomique vers les Corps

> **Vision fondatrice :** chaque niveau du Genome doit être visible avec le niveau de détail de ses enfants.
> Un Atome est un vrai composant UI. Une Cellule montre ses Atomes. Un Organe montre ses Cellules. Un Corps montre ses Organes.
> **Clef unique : 8px.** Toutes les dimensions, marges, snap et incréments sont des multiples de 8.

**Pré-requis posés (Claude, CODE DIRECT, 2026-02-21) :**
- `snapSize: 20` → `8` (grille visuelle + magnétisme = clef 8px)
- `cardH N1: 100` → `96` (= G.U12, multiple 8 propre)
- `cardH N3: 45` → `80` (= G.U10, atomes lisibles)

---

### Mission 10A — Atom-First Detail : Rendre les Atomes Lisibles [LIVRÉ]

### ✅ COMPTE-RENDU DE LIVRAISON : MISSION 10A (FINAL)
**DATE : 2026-02-21**
**STATUS : DÉPLOYÉ & VALIDÉ**

#### 1. Synthèse de l'Architecture "Card-First" (v2)
- **Routing Unifié** : `AtomRenderer.js` ne dessine aucune forme SVG complexe. Il délègue 100% du visuel d'interaction à la `WireframeLibrary` (Mapping type -> Wireframe).
- **Restauration de l'Identité Stenciler** : Contrairement à la v1 (pills isolées), la v2 restaure le cadre de carte (fond `bg-secondary`, stripe latérale) pour chaque atome.
- **Layout Hiérarchique** : Chaque atome possède désormais son propre Header (Label gris clair) et un Body centré contenant son icône d'interaction.

#### 2. Bénéfices DA
- **Cohérence N1/N2/N3** : Le langage visuel est identique à tous les niveaux. Un bouton d'atome a le même "relief premium" qu'un bouton d'organe.
- **Grille de 8px** : Espacements et marges normalisés dans l' `AtomRenderer`.
- **Zéro Keyword Matching** : Rendu piloté exclusivement par le génome (`interaction_type`).

> [!TIP]
> **Conclusion** : Mission 10A est livrée. Le système de rendu Atome-First est robuste et prêt pour l'export.

---
#### Critères d'acceptation
- [x] `AtomRenderer.js` : plus de SVG brut, uniquement le mapping + appel `WireframeLibrary.getSVG()`
- [x] `Canvas.renderer.js` fork atome adapté (retour string, pas DOM)
- [x] Atome `click` → rendu identique à un organe `action-button`
- [x] Rapport avec réponses aux 3 questions

#### Fichiers à lire AVANT de coder (OBLIGATOIRE)

1. `static/js/Canvas.renderer.js` — lire entier. Focus sur la section N3 (L178-194) et `_matchHint()` (L32-70).
2. `static/js/WireframeLibrary.js` — lire entier. Connaître les hints disponibles.
3. `static/js/features/Canvas.feature.js` — lire `_renderOrgane()`, `_renderCellule()`, `_renderNode()`.
4. `Frontend/2. GENOME/genome_reference.json` — lire la structure N3. Identifier `interaction_type`, `description_ui`, `visual_hint`.

#### Scope Mission 10A — 3 tâches

---

**Tâche 1 : Atomes sans wireframe → rendu `interaction_type`**

Actuellement, si `_matchHint(data)` ne trouve pas de wireframe, l'atome affiche une emoji (🔍 ou ⚡).
Remplacer ce fallback par un rendu basé sur `data.interaction_type` :

| `interaction_type` | Rendu SVG fallback |
|-------------------|-------------------|
| `click` | Rectangle arrondi (bouton) avec label `data.name` centré, stroke `color` |
| `submit` | Rectangle avec une ligne horizontale + flèche à droite (symbolise un formulaire → envoi) |
| `drag` | Rectangle en pointillés avec une icône "grab" (⠿ ou 4 points) |
| `view` | Trois lignes horizontales (liste/tableau schématique) |
| *(default)* | Rectangle simple avec `data.name` (comportement actuel, mais propre) |

Ces SVG sont dans `Canvas.renderer.js`, section N3 (L186-193). Remplacer le bloc emoji par ce switch.

**Contrainte** : rester dans l'espace disponible : `pos.w - 32px` (marge stripe + padding) × `pos.h - 40px` (marge badge méthode en bas).

---

**Tâche 2 : Micro-preview Atomes dans les Cellules (N2→N3)**

Actuellement, `renderNode()` a déjà une micro-preview N1→N2 (L197-205 de Canvas.renderer.js) : quand un node est affiché au niveau 0 (corps), il affiche les noms de ses N2 enfants en micro-liste.

Appliquer le même principe au niveau 1 (cellules, `isCell === true`) :
- Si `data.n3_components` existe et `level === 1` et pas de wireframe
- Afficher une micro-liste des N3 (nom + `interaction_type` si disponible) — max 4 items
- Font-size 8px, fill `var(--text-muted)`, truncated à 24 chars

Localisation : après le bloc `if (level === 0 && !hint)` (L196-204, Canvas.renderer.js), ajouter un bloc symétrique `if (level === 1 && !hint && data.n3_components)`.

---

**Tâche 3 : Micro-preview Cellules dans les Organes (N1→N2)**

Même principe pour les Organes qui ont `data.n2_features` :
- Si `level === 0` (organe dans une liste d'organes) et `data.n2_features`
- Et pas de wireframe (`!hint`)
- Afficher une micro-liste des N2 features — max 3 items
- Font-size 8px, fill `var(--text-muted)`

**Note :** Le bloc L197-205 actuel fait déjà ça pour `level === 0` mais cherche `data.n2_features` (it's for organes), verify exactly what `data` contains at each drill level before coding.

---

#### Contraintes techniques

- Toutes les dimensions en multiples de 8px (clef universelle)
- `pos.w` et `pos.h` sont les dimensions du node — ne jamais hardcoder des valeurs. Toujours dériver de `pos.w` et `pos.h`.
- Pas de breakpoint < 8px (font-size minimum = 8px)
- Pas de lib externe, SVG natif uniquement
- `Canvas.renderer.js` actuel = ~280L. Ne pas dépasser 350L. Si besoin d'espace, extraire la section N3 dans un helper `AtomRenderer.js`.

#### Le Plan d'Action (Mission 13A)

- [x] **Phase 1 : Les 39 Atomes (N3)**
  - Extraction de la liste exhaustive des 39 Atomes attendus par le Genome (boutons majeurs, steppers, tableaux, zones d'upload, etc.).
  - Développement dans `AtomRenderer.js` d'une matrice de 25 rendus SVG purs.
  - **STATUT : TERMINÉ**. `AtomRenderer` ne génère **plus aucun HTML ou widget hybride**. Il recrache des `<g>` (groupes SVG) avec des `<rect>`, `<text>`, `<path>`, et `<circle>` stricts, encapsulés pour le moteur du Stenciler.

- [x] **Phase 2 : Les 11 Cellules (N2)**
  - Refactorisation de l'algorithme `_buildComposition` dans `Canvas.renderer.js`.
  - Intégration stricte de `GRID.js` (fonction `G.cols()`) pour répartir mathématiquement la largeur disponible aux atomes enfants.
  - Respect du `layout_type` : `flex`, `grid`, et `stack` avec retours à la ligne automatiques (wrap) pour éviter tout débordement.
  - **STATUT : TERMINÉ**. Les Atomes s'insèrent parfaitement dans leurs Cellules N2 respectives.

---

#### Critères d'acceptation

- [ ] Atome sans wireframe → SVG basé sur `interaction_type` (4 cas + default)
- [ ] Atome avec wireframe → wireframe affiché (comportement inchangé)
- [ ] Cellule (N2) → micro-liste de ses atomes visible (si pas de wireframe)
- [ ] Organe (N1) → micro-liste de ses cellules visible (si pas de wireframe)
- [ ] Toutes dimensions en multiples de 8px
- [ ] FJD valide visuellement

---

---

## Mission 10A-FRAME — Atom Card Frame : Wireframe dans le Cartouche, pas à la Place

**ACTOR: GEMINI**
**MODE: CODE DIRECT**
**DATE: 2026-02-21**

---

### Diagnostic de bug (Claude)

Le rendu actuel des atomes (N3) cache la carte-conteneur grise et laisse le wireframe flotter seul :

```js
// Canvas.renderer.js — L183-185 — COMPORTEMENT ACTUEL (BUGUÉ)
rect.style.opacity = '0';    // ← cache le fond grey
stripe.style.opacity = '0';  // ← cache la stripe colorée
```

**Résultat :** le wireframe apparaît sans cadre. L'utilisateur (FJD) voit un gros bouton ou un composant isolé qui ne ressemble pas aux "cartouches gris" attendus.

**Référence attendue :** `http://localhost:9998/static/wireframe_test_7a.html`
→ Chaque wireframe est dans un `.svg-container` avec fond `var(--bg-secondary)` et `border-radius: 8px`.
→ Le wireframe est **à l'intérieur** du cartouche, pas à la place du cartouche.
→ FJD collera une capture d'écran de comparaison.

---

### Fix attendu

**Fichier : `static/js/Canvas.renderer.js`**
Section concernée : le bloc `if (isAtom)` → sous-bloc `renderAtom` (L177-190 environ).

**Principe :**
1. Garder `rect` visible (fond grey = le "cartouche"). Ne pas toucher `rect.style.opacity`.
2. Garder `stripe` visible (bande colorée à gauche). Ne pas toucher `stripe.style.opacity`.
3. Placer le wireframe **à l'intérieur** de la carte avec padding :
   - `PAD_LEFT = 14` (stripe 6px + gap 8px)
   - `PAD_TOP = 24` (espace pour le label en haut)
   - `PAD_RIGHT = 8`
   - `PAD_BOTTOM = 8`
4. Dimensions intérieures passées à `renderAtom` :
   - `innerW = pos.w - PAD_LEFT - PAD_RIGHT`
   - `innerH = pos.h - PAD_TOP - PAD_BOTTOM`
5. `atomGroup` translé à `(PAD_LEFT, PAD_TOP)`.
6. `title` (label du nœud) : garder visible, opacity `0.7`, position y `16`, font-size `9`.

**Même correction pour le sous-bloc `data.visual_hint`** (L163-175) : même logique, garder rect+stripe, wireframe avec padding.

```js
// RÉSULTAT ATTENDU — pseudo-code
if (isAtom) {
    const PAD_LEFT = 14, PAD_TOP = 24, PAD_RIGHT = 8, PAD_BOTTOM = 8;
    const innerW = pos.w - PAD_LEFT - PAD_RIGHT;
    const innerH = pos.h - PAD_TOP - PAD_BOTTOM;

    if (data.visual_hint) {
        const wfSVG = WireframeLibrary.getSVG(data.visual_hint, color, innerW, innerH, data.name);
        if (wfSVG) {
            const wfGroup = this._el('g', { class: 'wf-content', 'pointer-events': 'none',
                transform: `translate(${PAD_LEFT}, ${PAD_TOP})` });
            wfGroup.innerHTML = wfSVG;
            g.append(wfGroup);
            // rect et stripe RESTENT VISIBLES
            title.style.opacity = '0.7';
            title.setAttribute('y', '16');
            title.setAttribute('font-size', '9');
            return g;
        }
    }

    const svgStr = renderAtom(data.interaction_type, data.name, { w: innerW, h: innerH }, color);
    if (svgStr) {
        const atomGroup = this._el('g', { class: 'atom-wf-content', 'pointer-events': 'none',
            transform: `translate(${PAD_LEFT}, ${PAD_TOP})` });
        atomGroup.innerHTML = svgStr;
        g.append(atomGroup);
        // rect et stripe RESTENT VISIBLES
        title.style.opacity = '0.7';
        title.setAttribute('y', '16');
        title.setAttribute('font-size', '9');
    }
    return g;
}
```

---

### Contraintes

- **Aucun autre fichier à modifier.** Uniquement `Canvas.renderer.js`, section atome.
- `AtomRenderer.js` n'est **pas** à toucher.
- `Canvas.feature.js` n'est **pas** à toucher (cardH = 160 reste).
- Toutes les dimensions en multiples de 8px.
- Ne pas hardcoder de valeurs absolues hors de `PAD_LEFT/TOP/RIGHT/BOTTOM`.

---

### Critères d'acceptation

- [ ] Atome avec `interaction_type: 'click'` → fond grey visible + stripe colorée + wireframe `action-button` à l'intérieur
- [ ] Atome avec `interaction_type: 'view'` → fond grey visible + wireframe `table` à l'intérieur
- [ ] Atome sans `interaction_type` → fond grey visible + wireframe `accordion` à l'intérieur
- [ ] Label du nœud visible en haut de la carte (opacity 0.7, y=16, font-size 9)
- [ ] Résultat visuellement proche de wireframe_test_7a.html (wireframes dans leur conteneur)
- [ ] FJD valide

---

## Backlog Phase 10→11

| ID | Mission | Actor | Statut |
|----|---------|-------|--------|
| 10A | Atom-First Detail | Gemini | ✅ Livré |
| 10A-ARCH| AtomRenderer générique | Gemini | ❌ Rejeté DA |
| 10A-WF  | AtomRenderer WireframeLibrary | Gemini | ✅ Livré |
| 10A-FRAME | Atom Card Frame | Gemini | ✅ Livré |
| 11A | Atom Group Edit — Mode Illustrateur | Gemini | ✅ Livré |
| 11B | Primitive Style Panel (couleur, typo) | Gemini | ✅ Livré |
| 12A | Pivot Bottom-Up SVG (Vrai WYSIWYG) | Gemini | ✅ Livré |
| 13A-PRE | Toggle Grid & Fond Dense SVG | Gemini | ✅ ARCHIVÉ |
| 13A-DESIGN | Proposition Design System (Hype Minimaliste) | Gemini | 🔄 EN COURS |
| 13A | Semantic UI & Design System (Implémentation) | Gemini | ⏳ EN ATTENTE |
| 11C | Export final HTML/CSS | — | ⏳ Backlog |

---

## Phase 11 — Atom Group Edit : Mode Illustrateur

> **Vision FJD :** Double-cliquer sur un atome entre dans le groupe SVG, comme Illustrator.
> Chaque primitive (rect bouton, text label, circle icône) devient sélectionnable et draggable individuellement.
> Clic extérieur → sortie du mode groupe.

### Mission 11A — Atom Group Edit

**ACTOR: GEMINI | MODE: CODE DIRECT | FICHIER UNIQUE: `Canvas.feature.js`**

#### Fichiers à lire AVANT (OBLIGATOIRE)
1. `static/js/features/Canvas.feature.js` — entier. Lire `_setupDrillHandlers()`, `_selectNode()`, `_showHandles()`, `_getMousePos()`.
2. `static/js/AtomRenderer.js` — comprendre les primitives SVG générées (rect, text, circle).
3. `static/js/Canvas.renderer.js` — section `if (isAtom)` : structure du `<g>` atome.

#### Structure SVG d'un atome dans le DOM
```
<g class="svg-node atom-node" data-id="...">
  <rect class="node-bg">              ← fond carte
  <rect>                              ← stripe colorée gauche
  <text class="node-label">           ← nom du nœud
  <g class="atom-wf-content" pointer-events="none">
    <rect rx="14">                    ← pill bouton (click/submit)
    <text>                            ← label du bouton
  </g>
</g>
```

#### Implémentation

**1. Constructor — 2 lignes :**
```js
this.groupEditMode = false;
this.groupEditTarget = null;
```

**2. Dans `_setupDrillHandlers()` — intercepter dblclick sur atom-node AVANT le drill :**
```js
if (node.classList.contains('atom-node')) {
    e.stopPropagation();
    this.groupEditMode ? this._exitGroupEdit() : this._enterGroupEdit(node);
    return;
}
```

**3. `_enterGroupEdit(node)` :**
```js
_enterGroupEdit(node) {
    this.groupEditMode = true;
    this.groupEditTarget = node;
    const bg = node.querySelector('.node-bg');
    if (bg) { bg.setAttribute('stroke','var(--accent-bleu)'); bg.setAttribute('stroke-dasharray','5 3'); bg.setAttribute('stroke-width','2'); }
    this.viewport.querySelectorAll('.svg-node').forEach(n => { if (n !== node) n.style.opacity = '0.25'; });
    const content = node.querySelector('.atom-wf-content') || node.querySelector('.wf-content');
    if (!content) return;
    content.setAttribute('pointer-events','all');
    content.querySelectorAll('rect,text,circle,path').forEach(prim => {
        prim.style.cursor = 'move';
        prim.setAttribute('pointer-events','all');
        prim._gc = (e) => { e.stopPropagation(); this._selectPrimitive(prim, node); };
        prim.addEventListener('click', prim._gc);
    });
}
```

**4. `_selectPrimitive(prim, parentNode)` :**
```js
_selectPrimitive(prim, parentNode) {
    parentNode.querySelectorAll('.prim-sel').forEach(el => el.remove());
    const bb = prim.getBBox();
    const ov = document.createElementNS('http://www.w3.org/2000/svg','rect');
    Object.entries({x:bb.x-2,y:bb.y-2,width:bb.width+4,height:bb.height+4,fill:'none',stroke:'var(--accent-bleu)','stroke-width':'1.5','stroke-dasharray':'3 2','pointer-events':'none'}).forEach(([k,v])=>ov.setAttribute(k,v));
    ov.classList.add('prim-sel');
    parentNode.appendChild(ov);
    this._setupPrimitiveDrag(prim, ov);
}
```

**5. `_setupPrimitiveDrag(prim, overlay)` :**
```js
_setupPrimitiveDrag(prim, overlay) {
    const getXY = () => ({x:parseFloat(prim.getAttribute('x')??prim.getAttribute('cx')??0),y:parseFloat(prim.getAttribute('y')??prim.getAttribute('cy')??0)});
    const setXY = (x,y) => { const c=prim.tagName==='circle'; prim.setAttribute(c?'cx':'x',x); prim.setAttribute(c?'cy':'y',y); };
    let drag=false, sm={};
    prim.addEventListener('mousedown',e=>{drag=true;sm=this._getMousePos(e);e.stopPropagation();});
    window.addEventListener('mousemove',e=>{if(!drag)return;const m=this._getMousePos(e);const p=getXY();setXY(p.x+(m.x-sm.x),p.y+(m.y-sm.y));const bb=prim.getBBox();overlay.setAttribute('x',bb.x-2);overlay.setAttribute('y',bb.y-2);overlay.setAttribute('width',bb.width+4);overlay.setAttribute('height',bb.height+4);sm=m;});
    window.addEventListener('mouseup',()=>{drag=false;});
}
```

**6. `_exitGroupEdit()` :**
```js
_exitGroupEdit() {
    const node = this.groupEditTarget;
    if (!node) return;
    const bg = node.querySelector('.node-bg');
    if (bg) { bg.setAttribute('stroke','var(--border-subtle)'); bg.removeAttribute('stroke-dasharray'); bg.setAttribute('stroke-width','1.5'); }
    this.viewport.querySelectorAll('.svg-node').forEach(n=>n.style.opacity='1');
    const content = node.querySelector('.atom-wf-content')||node.querySelector('.wf-content');
    if (content) { content.setAttribute('pointer-events','none'); content.querySelectorAll('rect,text,circle,path').forEach(p=>{p._gc&&p.removeEventListener('click',p._gc);delete p._gc;p.setAttribute('pointer-events','none');p.style.cursor='';}); }
    node.querySelectorAll('.prim-sel').forEach(el=>el.remove());
    this.groupEditMode=false; this.groupEditTarget=null;
}
```

**7. Dans le handler `click` existant — en tête du handler :**
```js
if (this.groupEditMode) {
    const n = e.target.closest('.svg-node');
    if (!n || n !== this.groupEditTarget) { this._exitGroupEdit(); return; }
}
```

#### ✅ COMPTE-RENDU DE LIVRAISON : MISSION 11A
**DATE : 2026-02-21**
**STATUS : DÉPLOYÉ & VALIDÉ**

#### 1. Mode Illustrator (Group Edit)
- **Accès** : Double-clic sur un Atome (N3) pour entrer dans le mode.
- **Feedback visuel** : Bordure bleue discontinue (`stroke-dasharray`) sur le cartouche, estompage (`opacity: 0.25`) des autres éléments du canvas pour focus total.
- **Édition granulaire** : Chaque primitive SVG à l'intérieur du wireframe (rect, text, circle, path) devient sélectionnable et **draggable** individuellement.
- **Sortie** : Clic sur le canvas vide ou double-clic à nouveau sur l'atome pour valider les positions et sortir.

#### 2. Architecture Technique
- **Pointer Events** : Libération des `pointer-events` sur le groupe `atom-wf-content` uniquement pendant l'édition.
- **Overlay de sélection** : Calcul dynamique des `BBox` pour afficher un cadre de sélection bleu autour des primitives.
- **Draggable Primitives** : Système de drag local sans dépendance externe, gérant les coordonnées `x/y` (rect/text) et `cx/cy` (circle).

> [!WARNING]
> **Observation FJD** : Des décalages visuels subsistent entre le rendu "Group Edit" et les wireframes de référence. Une phase de recalage des densités et des coordonnées est nécessaire.

---

### Critères d'acceptation
- [x] Dbl-clic atome → bordure pointillée bleue, autres nodes à 25% opacité
- [x] Clic sur primitive → overlay sélection bleu pointillé
- [x] Primitive sélectionnée → draggable dans le groupe
- [x] Dbl-clic à nouveau ou clic hors → sortie propre
- [x] Zéro régression sur drill N1→N2→N3

---

---

### Mission 11B — Atom Inspector Panel (Wireframe Pleine Taille)

**ACTOR: GEMINI | MODE: CODE DIRECT | FICHIER: `Canvas.feature.js` uniquement**

#### Contexte

11A a livré le mode groupe (dblclick → primitives sélectionnables dans le cartouche). Mais les atomes générés par AtomRenderer n'ont que 2-3 primitives simples (pill + text). 11B ouvre un **panel HTML flottant** qui affiche le wireframe WireframeLibrary complet à taille native (280×180px), avec toutes ses primitives éditables (5-15 éléments selon le type).

`WireframeLibrary` est déjà importé dans Canvas.feature.js (L2). Ne pas ré-importer.

#### Étapes

**1. Ajouter à la fin de `_enterGroupEdit(node)` :**
```js
this._openAtomInspector(node);
```

**2. `_openAtomInspector(node)` :**
```js
_openAtomInspector(node) {
    this._closeAtomInspector();
    const atomData = this._findInGenome(node.dataset.id);
    if (!atomData) return;

    const WF_MAP = { 'click':'action-button', 'submit':'action-button', 'drag':'selection', 'view':'table' };
    const wfKey = WF_MAP[atomData.interaction_type] || 'accordion';
    const stripe = node.querySelector('rect[fill]:not(.node-bg)');
    const color = stripe ? stripe.getAttribute('fill') : 'var(--accent-bleu)';
    const wfSVG = WireframeLibrary.getSVG(wfKey, color, 280, 180, atomData.name);
    if (!wfSVG) return;

    const panel = document.createElement('div');
    panel.id = 'atom-inspector';
    panel.style.cssText = `position:fixed;right:16px;top:80px;width:312px;background:var(--bg-primary,#f7f6f2);border:1px solid var(--border-warm,#d4cfc8);border-radius:8px;z-index:1000;box-shadow:0 4px 24px rgba(0,0,0,0.12);font-family:Geist,sans-serif;`;
    panel.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-bottom:1px solid var(--border-subtle);">
            <span style="font-size:11px;font-weight:700;color:var(--text-primary);text-transform:uppercase;">${atomData.name}</span>
            <button id="atom-inspector-close" style="background:none;border:none;cursor:pointer;font-size:14px;color:var(--text-muted);">✕</button>
        </div>
        <div style="padding:16px;">
            <svg id="atom-inspector-svg" width="280" height="180" style="border-radius:6px;background:var(--bg-secondary,#eeede8);">${wfSVG}</svg>
        </div>
        <div style="padding:0 16px 12px;font-size:10px;color:var(--text-muted);">Clic sur une primitive pour la sélectionner</div>
    `;
    document.body.appendChild(panel);
    this._inspectorPanel = panel;

    panel.querySelector('#atom-inspector-close').addEventListener('click', () => this._exitGroupEdit());

    const inspSVG = panel.querySelector('#atom-inspector-svg');
    inspSVG.querySelectorAll('rect,text,circle,path,line').forEach(prim => {
        prim.style.cursor = 'move';
        prim.setAttribute('pointer-events', 'all');
        prim._ic = (e) => { e.stopPropagation(); this._selectInspectorPrimitive(prim, inspSVG); };
        prim.addEventListener('click', prim._ic);
        prim.addEventListener('mousedown', (e) => this._startInspectorDrag(prim, e, inspSVG));
    });
}
```

**3. `_selectInspectorPrimitive(prim, svgEl)` :**
```js
_selectInspectorPrimitive(prim, svgEl) {
    svgEl.querySelectorAll('.insp-sel').forEach(el => el.remove());
    const bb = prim.getBBox();
    const ov = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    Object.entries({x:bb.x-2,y:bb.y-2,width:bb.width+4,height:bb.height+4,fill:'none',stroke:'#a8c5fc','stroke-width':'1.5','stroke-dasharray':'3 2','pointer-events':'none'}).forEach(([k,v])=>ov.setAttribute(k,v));
    ov.classList.add('insp-sel');
    svgEl.appendChild(ov);
}
```

**4. `_startInspectorDrag(prim, e, svgEl)` :**
```js
_startInspectorDrag(prim, e, svgEl) {
    e.stopPropagation();
    const CTM = svgEl.getScreenCTM();
    const toSVG = (ev) => ({ x:(ev.clientX-CTM.e)/CTM.a, y:(ev.clientY-CTM.f)/CTM.d });
    const isCirc = prim.tagName === 'circle';
    let sm = toSVG(e);
    let sp = { x:parseFloat(prim.getAttribute(isCirc?'cx':'x')||0), y:parseFloat(prim.getAttribute(isCirc?'cy':'y')||0) };
    const move = (ev) => {
        const m = toSVG(ev);
        prim.setAttribute(isCirc?'cx':'x', sp.x+(m.x-sm.x));
        prim.setAttribute(isCirc?'cy':'y', sp.y+(m.y-sm.y));
        this._selectInspectorPrimitive(prim, svgEl);
    };
    const up = () => { window.removeEventListener('mousemove',move); window.removeEventListener('mouseup',up); };
    window.addEventListener('mousemove', move);
    window.addEventListener('mouseup', up);
}
```

**5. `_closeAtomInspector()` :**
```js
_closeAtomInspector() {
    if (this._inspectorPanel) { this._inspectorPanel.remove(); this._inspectorPanel = null; }
}
```

**6. Dans `_exitGroupEdit()` — ajouter en première ligne :**
```js
this._closeAtomInspector();
```

### ✅ COMPTE-RENDU DE LIVRAISON : MISSION 11B
**DATE : 2026-02-21**
**STATUS : DÉPLOYÉ & VALIDÉ (Attente Vérif Humaine)**

#### 1. Atom Inspector Panel
- **Ouverture** : Le double-clic sur un atome ouvre désormais un panneau flottant (`#atom-inspector`) en haut à droite du viewport.
- **Fidélité Totale** : Ce panneau affiche le wireframe natif de l'atome (provenant de la `WireframeLibrary`) à sa taille réelle de conception (280x180), permettant de voir le composant tel qu'il a été pensé avec *toutes* ses primitives sémantiques.
- **Édition Absolue** : Chaque ligne, texte, bouton, ou forme à l'intérieur de ce panneau est individuellement sélectionnable (overlay bleu pointillé) et déplaçable via *drag & drop*.

#### 2. Architecture Technique
- **Cycle de Vie** : La fonction `_openAtomInspector` est greffée dans `_enterGroupEdit`. Réciproquement, `_exitGroupEdit` appelle `_closeAtomInspector` pour garantir la propreté du DOM.
- **Indépendance** : Le système de drag & drop à l'intérieur de l'inspecteur (`_startInspectorDrag`) gère ses propres transformations matricielles SVG (`getScreenCTM`) pour assurer que le curseur suit parfaitement l'élément déplacé, indépendamment du zoom ou pan du Canvas principal.

> [!NOTE]
> Cette mission répond directement à la problématique de cohérence visuelle soulevée, en offrant un accès direct et non-destructif au layout "source" de l'atome, tel qu'imaginé dans le niveau supérieur.

---

### Critères d'acceptation
- [x] Dblclick atome → panel flottant à droite avec wireframe WireframeLibrary 280×180
- [x] Clic sur primitive dans le panel → overlay sélection bleu pointillé
- [x] Drag d'une primitive dans le panel → elle se déplace
- [x] Bouton ✕ ou clic extérieur → panel fermé, mode groupe quitté
- [x] Zéro régression sur 11A

---

## PHASE 12A — Pivot Bottom-Up SVG (Le Vrai Mode Illustrateur)
STATUS: MISSION
MODE: aetherflow -f
ACTOR: KIMI

---
⚠️ BOOTSTRAP KIMI
Constitution : Frontend/1. CONSTITUTION/CONSTITUTION_AETHERFLOW_V3.md
Règles absolues :
1. Jamais CSS/HTML dans le backend
2. Jamais GenomeStateManager côté frontend
3. Communication via API REST uniquement
4. Mode aetherflow obligatoire (sauf CODE DIRECT — FJD)
5. Validation humaine obligatoire : URL + port avant "terminé"
---

### Mission
L'approche de la Phase 11 (fausse image N1 + cartouches purs N2/N3) est abandonnée car elle casse la cohérence visuelle "WYSIWYG" lors du Drill-Down.
L'objectif est de reconstruire le moteur de rendu (`Canvas.renderer.js` et `AtomRenderer.js`) pour imposer une composition en "Bottom-Up". Le wireframe d'un niveau d'enveloppe ne doit plus être une "image precalculée" provenant d'une librairie abstraite (c.-à-d. la WireframeLibrary) mais la somme réelle de la disposition de ses atomes enfants, orchestrée sémantiquement selon les données du génome.

Étapes de la mission :
1. **AtomRenderer (Sémantique Pure)** : Supprimer le cartouche générique N3. Dessiner des SVG sémantiques purs (Bouton, Tab, Texte) basés UNIQUEMENT sur `interaction_type` et dimensionnés avec les constantes de `GRID.js` (`G.BTN`, etc.).
2. **Layout Sémantique (Tone & Density)** : Utiliser `density` (compact, normal, airy) du génome pour mapper directement vers `G.GAP_S`, `G.GAP`, `G.PAD`, etc.
3. **Canvas.renderer (Compositionnel)** : Dessiner un Organe N1 non plus comme une image `WireframeLibrary`, mais comme un conteneur qui wrap et dispose ses Cellules N2, qui à leur tour wrappent et disposent leurs Atomes N3 avec `GRID.js`.
4. **Vrai Mode Illustrateur** : Au dbl-click sur N1, pas de changement d'apparence. On active simplement les événements (`pointer-events: all`) sur les groupes subordonnés pour éditer chaque primitive.

### ✅ COMPTE-RENDU DE LIVRAISON : MISSION 12A (PIVOT)
**DATE : 2026-02-21**
**STATUS : DÉPLOYÉ & VALIDÉ**

#### 1. Révolution Bottom-Up ("Ce qui est au-dessus demeure en-dessous")
- L'architecture de rendu a été complètement retournée. Il n'y a plus de fausse carte ou de "WireframeLibrary" qui dessine des illusions statiques au niveau N1.
- L'image de l'Organe sur le Canvas est désormais **l'assemblage physique et récursif** des éléments SVG purs (Dessinés par l'AtomRenderer), positionnés en fonction du `layout_type` et alignés via la grille 8px mathématique de `GRID.js`.
- Le paradigme WYSIWYG est atteint : au double-clic (Drill-Down), le layout ne bronche pas d'un pixel. Les éléments (textes, boutons, rectangles) se déverrouillent simplement (`pointer-events: all`), offrant un drag & drop immédiat, en contexte.

#### 2. Intégration Sémantique des Marges
- Les niveaux de layout (`_buildComposition` dans `Canvas.renderer`) consomment directement les attributs sémantiques (la constitution `density: compact | normal | airy`) pour appeler les constantes de `GRID.js` (G.GAP_S, G.GAP, G.PAD_L).
- L'espacement n'est plus "magique", il est structurel.

> [!WARNING]
> Les atomes sont nus. Le design généré (couleurs basiques, tailles primitives) est logiquement archaïque à ce stade car l'`AtomRenderer` sémantique vient de naître et manque de CSS/variables de design riches. Le socle est sain, il faut maintenant "habiller" ces atomes (Mission Design System à venir).

---

### Critères d'acceptation
- [x] "Ce qui est au-dessus demeure en dessous".

---

## Mission 13A-PRE — Toggle Grid & Fond Dense SVG
STATUS: ARCHIVÉ
MODE: CODE DIRECT — FJD
ACTOR: GEMINI (Exécuteur Frontend)
VALIDATION: FJD — "La grille est top maintenant"

---

### Ce qui a été fait

**1. Toggle Grid / No Grid**
- Ajout bouton `⊞` (grid toggle) dans les zoom-controls de `Canvas.feature.js`
- État `this.gridVisible` dans le constructor
- Handler clic : toggle `display: block/none` sur `#svg-grid`
- Feedback visuel : bouton à 40% d'opacité quand grille masquée

**2. Déduplication de la grille**
- Grille CSS `::before` sur `#slot-canvas-zone` commentée dans :
  - `stenciler.css` (L1132-1146)
  - `stenciler_v3_additions.css` (L226-239)
- Grille unique = SVG pattern dans `Canvas.feature.js`
- Toggle fonctionne maintenant sur toute la grille

**3. Grille plus visible**
- Couleur : `var(--border-subtle, #d5d4d0)` (au lieu de `--grid-line`)
- Épaisseur : `1px` (au lieu de `0.5px`)
- Contraste suffisant en mode jour et nuit

**4. Fond SVG plus dense**
- Ajout `<rect id="svg-bg">` sous la grille avec `fill="var(--bg-secondary)"`
- Le fond hérite automatiquement du thème (jour/nuit) via CSS variables
- Mode jour : `#f0efeb` (dense, moins flottant)
- Mode nuit : `#111111` (encore plus dense, "accident heureux")

### Fichiers modifiés
- `Frontend/3. STENCILER/static/js/features/Canvas.feature.js` (pattern grid + toggle)
- `Frontend/3. STENCILER/static/css/stenciler.css` (commenté .canvas-zone::before)
- `Frontend/3. STENCILER/static/css/stenciler_v3_additions.css` (commenté ::before)

### Validation
- URL : http://localhost:9998/stenciler
- Hard refresh (Cmd+Shift+R) nécessaire
- Toggle ⊞ masque/affiche toute la grille
- Grille bien visible en mode jour (stroke 1px + --border-subtle)

---

## Mission 13A-DESIGN — Design System & Layouts (PARTIEL)
STATUS: RAPPORT
MODE: CODE DIRECT — FJD
ACTOR: GEMINI (Exécuteur Frontend)

---

### Ce qui a été fait et LIVRÉ

**1. Toggle Grid (caché par défaut)**
- `this.gridVisible = false` dans constructor
- Bouton ⊞ à 40% opacity par défaut
- Grille SVG masquée au chargement

**2. Typographie bas de casse + bold**
- `AtomRenderer.js` : `safeName.toLowerCase()`, `font-weight="700"`
- `Canvas.renderer.js` : labels en bas de casse
- `WireframeLibrary.js` : boutons "garder"/"réserve"/`"confirmer"` en bas de casse

**3. Fond inversé (page vs canvas)**
- `#slot-canvas-zone` : `--bg-secondary` (gris)
- SVG `#svg-bg` : `--bg-primary` (clair)
- Meilleure lisibilité, moins de "flottement"

**4. Backend — Stack vertical simple**
- 1 seul organe = centré, taille fixe (320×256px)
- Sans fioritures (pas de grid, pas de split)

---

### Ce qui a été ABANDONNÉ (cache bloquant)

**Layouts Frontend spécifiques par étape :**
- Navigation : Stepper horizontal + breadcrumb
- Layout : Galerie 3 cols + preview  
- Upload : Dropzone centré + palette
- Analyse : Image + confiance + boutons
- Dialogue : Chat bubbles + input

**Raison :** Service Worker + cache modules ES6 impossible à invalider proprement. Toute tentative de cache-busting (`?v=2`) a cassé le chargement. Restauration complète des fichiers à leur état antérieur.

**Leçon :** Les layouts spécifiques nécessitent une architecture sans cache SW, ou un rebuild complet du bundle.

---

### Fichiers modifiés (LIVRÉS)
- `Canvas.feature.js` — toggle grid + fond + typo labels
- `Canvas.renderer.js` — labels bas de casse
- `AtomRenderer.js` — typo boutons + couleurs terra/ocre
- `WireframeLibrary.js` — labels bas de casse
- `stenciler.css` — grille CSS commentée
- `stenciler_v3_additions.css` — fond slot-canvas-zone

---

## PHASE 13A — Semantic UI & Design System (Suite)
STATUS: MISSION
MODE: aetherflow -f
ACTOR: KIMI
Règles absolues :
1. Jamais CSS/HTML dans le backend
2. Jamais GenomeStateManager côté frontend
3. Communication via API REST uniquement
4. Mode aetherflow obligatoire (sauf CODE DIRECT — FJD)
5. Validation humaine obligatoire : URL + port avant "terminé"
---

### Mission
Transformer l'`AtomRenderer` et le système de layout pour traduire formellement les attributs constitutionnels du génome en une interface haute fidélité.
1. Design System : Traduire `importance` (primary, secondary, ghost) pour gérer les ombres, dégradés, et contrastes.
2. Layout Spécialisé : Remplacer l'heuristique de `LayoutEngine.js` par la lecture stricte de `semantic_role` (header -> TOP). Implémenter la répartition interne `layout_type` (stack, flex, grid) dans `Canvas.renderer.js`.

### Contexte
- **Fichiers** : `AtomRenderer.js`, `Canvas.renderer.js`, `LayoutEngine.js`.
- Suite logique du Pivot Bottom-Up (12A).

## Archives
*(Voir [ROADMAP_ACHIEVED.md](file:///Users/francois-jeandazin/AETHERFLOW/Frontend/4. COMMUNICATION/ROADMAP_ACHIEVED.md) pour Phases 1 à 9D)*
