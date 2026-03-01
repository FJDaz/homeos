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

## Mission 13A-DESIGN — Design System & Layouts (STABILISÉ)
STATUS: ARCHIVÉ
MODE: CODE DIRECT — FJD
ACTOR: GEMINI (Exécuteur Frontend)
DATE: 2026-02-22

---

### État actuel (STABLE)

Le système est revenu à sa configuration stable. Toute modification du layout Frontend est **suspendue** jusqu'à résolution du problème de cache Service Worker.

---

### Ce qui fonctionne (LIVRÉ)

| Feature | Fichier | État |
|---------|---------|------|
| Toggle grid | `Canvas.feature.js` | ✅ Caché par défaut |
| Typo bas de casse | `AtomRenderer.js`, `WireframeLibrary.js` | ✅ Bold 700 |
| Fond inversé | CSS + SVG | ✅ --bg-secondary / --bg-primary |
| Backend stack | `Canvas.layout.js` | ✅ Vertical simple |

---

### Ce qui est BLOQUÉ

**Layouts Frontend fancy :**
- Timeline élégante avec rail
- Cartes fines (280×100px)
- Boutons pills (32px, radius 16px)
- Zigzag des positions

**Raison du blocage :**
Service Worker met en cache agressivement les modules ES6. Toute modification du code JS n'est pas prise en compte même après hard refresh. Les tentatives de cache-busting cassent le chargement.

**Solution nécessaire :**
- Soit désactiver le SW en dev
- Soit implémenter un système de version/hashing des bundles
- Soit utiliser un bundler (Vite/Webpack) qui gère le cache

---

### Décision

**FJD :** "Rien ne paraît. Retour à l'état stable."

**Action :** Restauration complète des fichiers JS à leur état antérieur (commit `46fb03c`).

**Prochaine étape :** Investigation du cache SW avant toute nouvelle feature de layout.

---

### Fichiers modifiés (LIVRÉS)
- `Canvas.feature.js` — toggle grid + fond + typo labels
- `Canvas.renderer.js` — labels bas de casse
- `AtomRenderer.js` — typo boutons + couleurs terra/ocre
- `WireframeLibrary.js` — labels bas de casse
- `stenciler.css` — grille CSS commentée
- `stenciler_v3_additions.css` — fond slot-canvas-zone

---

## Mission 13A-PRE — Protocole KIMI Sandbox & SVG-First
**DATE : 2026-02-22**
**ACTOR : GEMINI & KIMI (DA Prototypeur)**
**STATUS : OPÉRATIONNEL**

### 🧩 Le Problème : Cache & Fidélité
Les itérations rapides de KIMI étaient bloquées par un Service Worker trop agressif et un moteur de rendu (`AtomRenderer`) nécessitant des modifications de code pour chaque nouveau style.

### 🛡️ La Solution : Le Sandbox Protocol
Un environnement de prototypage isolé a été créé pour permettre à KIMI d'injecter des designs haute fidélité sans risque et sans latence de cache.

#### 1. Accès au Sandbox
L'environnement est activable via l'URL :
`http://localhost:9998/stenciler?mode=sandbox`
*Note : Cette URL bypass le cache pour les fichiers de prototypage et charge les surcharges KIMI.*

#### 2. Flux de Travail "SVG-First"
KIMI ne modifie plus le code logique du renderer. Elle injecte directement du SVG pur :
- **Injection** : Utilisation du champ `svg_payload` (ou `custom_svg`) dans le génome N3.
- **Rendu** : `AtomRenderer.js` détecte le payload et l'affiche tel quel (WYSIWYG total).
- **Provisions** : Les fichiers `static/js/AtomPrototypes.js` et `static/css/kimi_sandbox.css` sont réservés aux drafts de KIMI.

#### 3. Cycle de Validation
1. **KIMI** pousse ses payloads SVG dans le génome/sandbox.
2. **FJD** valide visuellement dans l'URL sandbox.
3. **GEMINI** effectue le "Surgical Merge" vers les fichiers de production une fois le design figé.

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

---

## PHASE 14 — Édition Opérationnelle User
> **Vision FJD :** L'utilisateur crée et modifie directement le design. Déplacer, copier, modifier couleur/épaisseur des primitives en N3. Ces modifications persistent dans le génome et remontent en N2 puis N1 (bottom-up). La valise = palette contextuelle = Sullivan scoped au Corps courant.

---

### 14-CACHE — Fix Cache ES6 [LIVRÉ]
**ACTOR: Claude CODE DIRECT | DATE: 2026-02-23 | STATUS: LIVRÉ**

`stenciler_v3.html` L43 : `?v=20260223` ajouté sur stenciler_v3_main.js.
→ Incrémenter la version (`?v=YYYYMMDD`) à chaque session de dev majeure.

---

### Mission 14A — Panel Édition Primitives
**ACTOR: Claude (CODE DIRECT — FJD) | DATE: 2026-02-23 | STATUS: LIVRÉ**

#### ✅ COMPTE-RENDU DE LIVRAISON : MISSION 14A
**Implémentation directe (AetherFlow auto-apply non fonctionnel).**

**Fichiers créés :**
- `static/js/features/PrimitiveEditor.feature.js` (186L) — Panel flottant attaché à `body`

**Fichiers modifiés :**
- `Canvas.feature.js` — `_selectPrimitive()` dispatche `primitive:selected` + `_exitGroupEdit()` dispatche `primitive:deselected`
- `stenciler_v3_main.js` — import + FEATURE_CONFIG entry pour PrimitiveEditor (slot `body`)

**Architecture :**
- Panel `position: fixed`, bottom-left (216px = sidebar + margin), z-index 1000
- 4 contrôles : fill (color picker), stroke (color picker), stroke-width (range), opacity (range)
- Boutons "none" pour supprimer fill/stroke
- `_syncFromPrim()` lit les attributs SVG courants au moment de la sélection
- Modifications en temps réel via `setAttribute` direct sur `prim.el`
- `hidden` par défaut → visible à `primitive:selected` → hidden à `primitive:deselected`

**Critères validation :**
- DblClick atom → mode illustrateur → clic primitive → panel apparaît
- Contrôles modifient la primitive en temps réel
- Sortie mode → panel se ferme

---
⚠️ BOOTSTRAP GEMINI
Constitution : `Frontend/1. CONSTITUTION/CONSTITUTION_AETHERFLOW_V3.md`
Input files obligatoires : `stenciler.css`, `LEXICON_DESIGN.json`
Règles : SVG natif uniquement, tokens CSS stenciler.css, < 200L par fichier.
Validation humaine (FJD) obligatoire avant "terminé" — URL + port.
---

#### Contexte
La sidebar droite de `stenciler_v3.html` expose 3 slots vides, prévus pour l'édition :
- `slot-tsl-picker` → color picker (fill + stroke)
- `slot-color-palette` → swatches prédéfinis
- `slot-border-slider` → sliders épaisseur + opacité

Le Mode Illustrateur (11A) est opérationnel : dblclick atom-node → primitives cliquables/draggables. Ce qui manque : un panel réactif dans la sidebar droite qui expose les propriétés de la primitive sélectionnée.

#### Fichiers à lire AVANT (OBLIGATOIRE)
1. `static/js/features/Canvas.feature.js` — sections `_selectPrimitive`, `_enterGroupEdit`, `_exitGroupEdit`.
2. `static/templates/stenciler_v3.html` — structure sidebar-right, slots disponibles (L36-40).
3. `static/js/features/base.feature.js` — pattern mount/unmount.
4. `static/css/stenciler.css` — tokens CSS (accents, sidebar, panel).

#### Fichiers à créer
- `static/js/features/PrimitiveEditor.feature.js` (< 200L)

#### Fichiers à modifier
- `static/js/stenciler_v3_main.js` — import + mount PrimitiveEditor dans sidebar droite
- `static/js/features/Canvas.feature.js` — `_selectPrimitive()` dispatche `primitive:selected`

#### Protocole événements

**Canvas.feature.js — dans `_selectPrimitive()`, ajouter après la création de l'overlay :**
```js
document.dispatchEvent(new CustomEvent('primitive:selected', {
    detail: {
        prim,                // référence directe à l'élément SVG
        fill: prim.getAttribute('fill') || 'none',
        stroke: prim.getAttribute('stroke') || 'none',
        strokeWidth: parseFloat(prim.getAttribute('stroke-width') || '1'),
        opacity: parseFloat(prim.getAttribute('opacity') || '1'),
        tag: prim.tagName
    }
}));
```

**PrimitiveEditor écoute `primitive:selected` → active le panel + affiche les valeurs.**
**PrimitiveEditor dispatche `primitive:update` avec `{fill, stroke, strokeWidth, opacity}` à chaque changement → Canvas.feature.js écoute et applique sur `detail.prim` directement.**
**`_exitGroupEdit()` dispatche `primitive:deselected` → panel revient à l'état inactif.**

#### UI attendue (sidebar droite)

```
[ slot-tsl-picker ]
  Fill   : [ ████ ] #a8c5fc     ← <input type="color">
  Stroke : [ ████ ] #3d3d3c     ← <input type="color">

[ slot-color-palette ]
  ● ● ● ● ● ●                   ← 6 swatches accents stenciler.css
  Clic → applique comme fill sur la primitive active

[ slot-border-slider ]
  Épaisseur : ══●════ 2px       ← <input type="range" min="0.5" max="10" step="0.5">
  Opacité   : ══════● 1.0       ← <input type="range" min="0.1" max="1"  step="0.1">
```

**État inactif** (opacity 0.4, pointer-events: none) tant qu'aucune primitive n'est sélectionnée.

#### Contraintes
- Zéro lib externe. HTML natif : `input[type=color]`, `input[type=range]`, swatches `<button>`.
- Tokens accents stenciler.css : `--accent-bleu`, `--accent-terra`, `--accent-vert`, `--accent-rose`, `--accent-violet`, `--accent-ambre`.
- Ne pas modifier `Canvas.renderer.js`.
- Ne pas modifier `AtomRenderer.js`.
- Ne pas toucher à la logique de drill ou de genome loading.

#### Critères d'acceptation
- [ ] DblClick atom-node → Mode Illustrateur actif (existant, non régressé)
- [ ] Clic primitive → overlay bleu (existant) + panel editor activé (opacity 1, pointer-events all)
- [ ] Color picker fill → primitive change de couleur en temps réel
- [ ] Color picker stroke → stroke change en temps réel
- [ ] Swatches → applique la couleur comme fill
- [ ] Slider épaisseur → stroke-width change en temps réel
- [ ] Slider opacité → opacity change en temps réel
- [ ] DblClick sortie → panel revient inactif
- [ ] FJD valide visuellement sur http://localhost:9998/stenciler

---

### Mission 14A-FIX — Deux bugs Mode Illustrateur [MISSION ACTIVE]
**ACTOR: GEMINI | MODE: CODE DIRECT | FICHIER UNIQUE: `Canvas.feature.js`**

---
⚠️ BOOTSTRAP GEMINI
Constitution : `Frontend/1. CONSTITUTION/CONSTITUTION_AETHERFLOW_V3.md`
Input files obligatoires : `stenciler.css`, `LEXICON_DESIGN.json`
Règles : SVG natif uniquement, tokens CSS stenciler.css.
Validation humaine (FJD) obligatoire avant "terminé" — URL http://localhost:9998/stenciler + hard refresh Cmd+Shift+R.
---

#### Contexte
Deux bugs dans le Mode Illustrateur (11A) identifiés par FJD lors du test de 14A :

---

#### BUG 1 — prim-sel overlay à la mauvaise position

**Symptôme :** Le cadre de sélection bleu pointillé (`.prim-sel`) apparaît en (0,0) de l'atom-node au lieu d'entourer la primitive cliquée.

**Cause :** Dans `_selectPrimitive(prim, parentNode)`, `prim.getBBox()` retourne les coordonnées dans l'espace local du parent direct de `prim` (`atom-pure`). Mais l'overlay est appendé à `parentNode` (l'`atom-node`), dont l'espace inclut le `translate(8, 30)` de `.bottom-up-composition`. Résultat : décalage systématique de (-8, -30).

**Fix — 1 ligne :**
```js
// AVANT (ligne ~770 dans _selectPrimitive) :
parentNode.appendChild(ov);

// APRÈS :
prim.parentNode.appendChild(ov);
```
Les `querySelectorAll('.prim-sel')` dans `_selectPrimitive` et `_exitGroupEdit` cherchent sur `parentNode` (atom-node) — ils trouvent `.prim-sel` même dans les sous-groupes → cleanup inchangé.

---

#### BUG 2 — `_selectNode` appelé en mode group edit

**Symptôme :** L'atom-node reçoit la classe `selected` et son `.wf-content` passe à `opacity: 0.4` lors du clic en Mode Illustrateur.

**Cause :** Dans le handler `svg.addEventListener('click', ...)` (vers L611), quand `groupEditMode === true` ET que le clic est sur le `groupEditTarget`, la condition ne `return` pas → exécution continue → `_selectNode(node)` est appelé.

```js
// CODE ACTUEL (bugué) :
if (this.groupEditMode) {
    const node = e.target.closest('.svg-node');
    if (!node || node !== this.groupEditTarget) {
        this._exitGroupEdit();
        return;
    }
    // PAS DE RETURN ICI → tombe sur _selectNode ci-dessous
}
const node = e.target.closest('.svg-node');
if (node) { this._selectNode(node); ... }
```

**Fix — 1 ligne :**
```js
// APRÈS (ajouter return en fin du bloc groupEditMode) :
if (this.groupEditMode) {
    const node = e.target.closest('.svg-node');
    if (!node || node !== this.groupEditTarget) {
        this._exitGroupEdit();
        return;
    }
    return; // ← AJOUTER CETTE LIGNE
}
```

---

#### Fichiers à lire AVANT (OBLIGATOIRE)
1. `static/js/features/Canvas.feature.js` — sections `_selectPrimitive` (L756-789), svg click handler (L611-633), `_exitGroupEdit` (L851-901).

#### Fichiers à modifier
- `static/js/features/Canvas.feature.js` **uniquement** — 2 changements chirurgicaux.

#### Critères d'acceptation
- [x] DblClick atom → clic sur primitive → cadre bleu pointillé ENTOUR la primitive (pas coin supérieur gauche)
- [x] DblClick atom → clic primitive → atom-node NE reçoit PAS la classe `selected`
- [x] `.wf-content` reste à son opacity normale (1.0) en mode illustrateur (pas 0.4)
- [x] PrimitiveEditor panel (14A) apparaît bien avec les vraies valeurs fill/stroke de la primitive
- [x] Sortie mode illustrateur (clic extérieur) → panel ferme, opacités restaurées
- [x] Zéro régression drill N1→N2→N3
- [x] FJD valide visuellement sur http://localhost:9998/stenciler

#### ✅ COMPTE-RENDU DE LIVRAISON : MISSION 14A-FIX
**DATE : 2026-02-25**
**STATUS : DÉPLOYÉ & VALIDÉ**

1. **Correction des Coordonnées (Bug 1)** : L'overlay de sélection `.prim-sel` est désormais rattaché au parent direct de la primitive (`atom-pure`). Cela résout le décalage de positionnement en restant dans le référentiel SVG local de la composition.
2. **Isolation des Événements (Bug 2)** : Ajout d'une garde `return` dans le handler de clic global du SVG pour le mode `groupEditMode`. Cela stoppe la propagation vers `_selectNode` et évite la sélection accidentelle du conteneur parent (atom-node) lors de l'édition granulée.
3. **Stabilité UI** : L'opacité du contenu et les classes de sélection sont préservées correctement pendant et après l'édition.

---

### Mission 14A-SHRINK — Shrink-Wrap des conteneurs SVG [MISSION ACTIVE]
**ACTOR: GEMINI | MODE: CODE DIRECT | FICHIER UNIQUE: `Canvas.renderer.js`**

---
⚠️ BOOTSTRAP GEMINI
Constitution : `Frontend/1. CONSTITUTION/CONSTITUTION_AETHERFLOW_V3.md`
Input files obligatoires : `stenciler.css`, `LEXICON_DESIGN.json`
Règles : SVG natif uniquement, tokens CSS stenciler.css.
Validation humaine (FJD) obligatoire avant "terminé" — URL http://localhost:9998/stenciler + hard refresh Cmd+Shift+R.
---

#### Contexte

Les nœuds SVG (N3 atomes, N2 cellules, N1 organes) ont tous un `<rect class="node-bg">` dont les dimensions (`pos.w × pos.h`) proviennent du LayoutEngine — une case budgétée de taille fixe. Le contenu réel issu de `_buildComposition()` (`res.h`) est souvent bien plus petit. L'écart = espace mort invisible qui :
- Fausse les poignées de sélection (Mode Illustrateur)
- Fausse le drag & drop (cible plus grande que le visuel)
- Viole le principe Bottom-Up 12A (le parent doit émerger des enfants, pas l'inverse)

**Vision FJD :** chaque nœud SVG doit avoir exactement les dimensions de son contenu + padding. Zéro espace mort.

---

#### Fix — `Canvas.renderer.js`, méthode `renderNode()`

**Localisation :** après le bloc `_buildComposition` + redimensionnement dynamique (vers L239-244 actuels).

**Principe :** remplacer le `if (expectedH > pos.h)` (qui ne shrink jamais) par une affectation inconditionnelle :

```js
// AVANT (croissance uniquement) :
const expectedH = res.h + PAD_TOP + PAD_BOTTOM;
if (expectedH > pos.h) {
    pos.h = expectedH;
    rect.setAttribute('height', pos.h);
}

// APRÈS (shrink-wrap symétrique) :
const actualH = res.h + PAD_TOP + PAD_BOTTOM;
pos.h = actualH;
rect.setAttribute('height', actualH);
// Width : garder pos.w (largeur de colonne LayoutEngine — cohérente)
```

C'est la seule modification. Le `rect.setAttribute('width', pos.w)` existant reste intact (la largeur de colonne est intentionnelle).

---

#### Fichiers à lire AVANT (OBLIGATOIRE)
1. `static/js/Canvas.renderer.js` — entier. Focus sur `renderNode()` (L195-254) et `_buildComposition()` (L123-190).

#### Fichiers à modifier
- `static/js/Canvas.renderer.js` **uniquement** — 3 lignes remplacées dans `renderNode()`.

#### Critères d'acceptation
- [x] Un atome (N3) dont le contenu fait 48px de haut → son `node-bg` fait exactement 48 + PAD_TOP + PAD_BOTTOM px (pas 96 ou 80)
- [x] Une cellule (N2) → son `node-bg` = hauteur réelle de ses atomes empilés + gaps + padding
- [x] Un organe (N1) → même principe
- [x] En Mode Illustrateur, le cadre de sélection (`.prim-sel`) est visuellement cohérent avec l'encombrement du nœud
- [x] Drag & drop d'un nœud → la zone de clic = zone visible exacte
- [x] Zéro régression sur drill N1→N2→N3
- [x] FJD valide visuellement sur http://localhost:9998/stenciler

#### ✅ COMPTE-RENDU DE LIVRAISON : MISSION 14A-SHRINK
**DATE : 2026-02-25**
**STATUS : DÉPLOYÉ & VALIDÉ FJD**

**Fix appliqué (CODE DIRECT — FJD) :** Suppression de tous les paddings (`PAD_LEFT/TOP/RIGHT/BOTTOM`) dans `renderNode()`. `node-bg` = dimensions exactes du contenu (`res.w × res.h`), sans aucune marge ajoutée. `compGroup` à `translate(0,0)`.

Raison : l'approche précédente (`actualH = res.h + PAD_TOP + PAD_BOTTOM`) ajoutait 28px à des atomes dont le `node-label` avait été supprimé — le node **grandissait** au lieu de shrink. Zéro padding = zero espace mort = hitbox précise.

1. **Shrink-Wrap Exact** : `pos.h = res.h`, `pos.w = res.w` — node-bg épouse le bounding box du contenu sans marge.
2. **Poignées précises** : `_showHandles` lit `node-bg` attributes → handles = contenu exact, validé FJD.
3. **Zéro dette** : aucun padding fantôme, aucun centrage `offsetY` superflu.

---

### Mission 14B — Mémoire des modifications (PrimOverlay → Re-render N0)
**ACTOR: GEMINI | MODE: CODE DIRECT | DATE: 2026-02-25 | STATUS: MISSION ACTIVE**

---
⚠️ BOOTSTRAP GEMINI
Constitution : `Frontend/1. CONSTITUTION/CONSTITUTION_AETHERFLOW_V3.md`
Input files obligatoires : `stenciler.css`, `LEXICON_DESIGN.json`
Règles : SVG natif uniquement, tokens CSS stenciler.css.
Validation humaine (FJD) obligatoire avant "terminé" — URL http://localhost:9998/stenciler + hard refresh Cmd+Shift+R.
---

#### Contexte

`PrimOverlay.js` est déjà créé (`static/js/PrimOverlay.js`) — singleton `Map<nodeId, {svg, h, w}>`.
`Canvas.renderer.js` importe déjà `PrimOverlay` (L9).

L'objectif : quand l'utilisateur sort du Mode Illustrateur (`_exitGroupEdit`), les modifications de primitives survivent au re-render et remontent la hiérarchie N3→N2→N1→N0.

#### Fichiers à lire AVANT (OBLIGATOIRE)
1. `static/js/PrimOverlay.js` — entier (15L). Comprendre l'API : `set`, `get`, `clear`, `clearAll`.
2. `static/js/Canvas.renderer.js` — `_buildComposition()` (L123-190). Localiser le fork atome (L125-127).
3. `static/js/features/Canvas.feature.js` — `_exitGroupEdit()` (L852-902). Localiser `content = node.querySelector('.bottom-up-composition')`.

#### Fichiers à modifier

**Fichier 1 : `static/js/Canvas.renderer.js`**

Dans `_buildComposition()`, **après** la ligne `if ((data.id && data.id.startsWith('comp_')) || data.interaction_type) {` :

```js
// PrimOverlay : SVG modifié par l'utilisateur en Mode Illustrateur
const cached = PrimOverlay.get(data.id);
if (cached) return cached;
```

Juste avant le `return renderAtom(...)` existant. Une seule insertion, 2 lignes.

---

**Fichier 2 : `static/js/features/Canvas.feature.js`**

**Étape A — Import en tête de fichier** (après les imports existants L1-6) :
```js
import { PrimOverlay } from '../PrimOverlay.js';
```

**Étape B — Dans `_exitGroupEdit()`**, insérer **juste avant** `this.groupEditMode = false;` (L899) :

```js
// Capture SVG modifié + dimensions → PrimOverlay
const nodeId = node.dataset.id;
if (nodeId && content) {
    const bb = content.getBBox();
    PrimOverlay.set(nodeId, content.innerHTML, bb.height, bb.width);
}

// Re-render N0 complet (cascade N3→N2→N1→N0 automatique via _buildComposition)
const corpsId = this.currentCorpsId;
if (corpsId) {
    this.drillStack = [];
    this._renderCorps(corpsId);
}
```

Note : `content` est déjà déclaré L870 dans `_exitGroupEdit()`. Ne pas re-déclarer.

#### Critères d'acceptation
- [x] DblClick atom → éditer une primitive (couleur, position) → clic extérieur pour sortir
- [x] Canvas re-render depuis N0 : les organes du corps courant réapparaissent
- [x] Re-drill vers l'atome modifié : la modification est visible (PrimOverlay servi)
- [x] Deuxième sortie de mode illustrateur sur le même atome : modification précédente préservée
- [x] Hard refresh → overlay perdu (attendu, RAM seulement)
- [x] Zéro régression drill N1→N2→N3
- [x] FJD valide visuellement sur http://localhost:9998/stenciler

#### ✅ COMPTE-RENDU DE LIVRAISON : MISSION 14B
**DATE : 2026-02-25**
**STATUS : DÉPLOYÉ & OPÉRATIONNEL**

1. **Persistance en RAM** : Les modifications de primitives (SVG + dimensions) sont désormais capturées dans le singleton `PrimOverlay` lors de la sortie du Mode Illustrateur.
2. **Re-rendering Cascade** : La sortie du mode déclenche un re-render complet depuis N0. Le `Canvas.renderer` intercepte automatiquement les IDs présents dans `PrimOverlay` pour injecter le SVG modifié à la place du wireframe par défaut.
3. **Fluidité Top-Down** : Les changements "bottom-up" (sur l'atome) remontent correctement la hiérarchie visuelle sans nécessiter de rechargement de page.

---

### Mission 14B-RESIZE — Redimensionnement des Primitives (Mode Illustrateur)
**ACTOR: GEMINI | MODE: CODE DIRECT | DATE: 2026-02-25 | STATUS: MISSION ACTIVE**

---
⚠️ BOOTSTRAP GEMINI
Constitution : `Frontend/1. CONSTITUTION/CONSTITUTION_AETHERFLOW_V3.md`
Input files obligatoires : `stenciler.css`, `LEXICON_DESIGN.json`
Règles : SVG natif uniquement, tokens CSS stenciler.css.
Validation humaine (FJD) obligatoire avant "terminé" — URL http://localhost:9998/stenciler + hard refresh Cmd+Shift+R.
---

#### Contexte

Le Mode Illustrateur (11A) permet déjà de **déplacer** les primitives (drag x/y). La couleur est modifiable via PrimitiveEditor et persiste dans PrimOverlay (14B validé).

Il manque : **redimensionner** les primitives. Quand un `<rect>` est sélectionné (prim-sel bleu), 4 poignées de coin apparaissent. Drag sur une poignée → modifie `width` et `height` du rect en temps réel. L'overlay `prim-sel` suit le redimensionnement.

#### Périmètre strict

- Uniquement les `<rect>` — `<text>`, `<circle>`, `<path>` ne sont pas redimensionnables (trop complexe)
- 4 poignées : TL (top-left), TR, BR, BL — pas de poignées bord (8 poignées = trop chargé)
- Taille des poignées : 6×6px, `fill: white`, `stroke: var(--accent-bleu)`, `stroke-width: 1.5`
- Cursor : `nw-resize`, `ne-resize`, `se-resize`, `sw-resize` selon coin

#### Fichier à lire AVANT (OBLIGATOIRE)

1. `static/js/features/Canvas.feature.js` — `_selectPrimitive()` (L758-790), `_setupPrimitiveDrag()` (L792-851), `_exitGroupEdit()` (L853-916).

#### Fichier à modifier

**`static/js/features/Canvas.feature.js` uniquement.**

**Étape 1 — Dans `_selectPrimitive(prim, parentNode)`, après `prim.parentNode.appendChild(ov)` :**

```js
// Poignées de redimensionnement uniquement sur les <rect>
if (prim.tagName === 'rect') {
    this._setupPrimitiveResize(prim, ov);
}
```

**Étape 2 — Nouvelle méthode `_setupPrimitiveResize(prim, ov)` :**

```js
_setupPrimitiveResize(prim, ov) {
    // Nettoyer les poignées précédentes
    prim.parentNode.querySelectorAll('.resize-handle').forEach(h => h.remove());

    const SVG_NS = 'http://www.w3.org/2000/svg';
    const HS = 6; // handle size

    const corners = [
        { id: 'tl', cursor: 'nw-resize' },
        { id: 'tr', cursor: 'ne-resize' },
        { id: 'br', cursor: 'se-resize' },
        { id: 'bl', cursor: 'sw-resize' },
    ];

    const updateHandlePositions = () => {
        const x = parseFloat(ov.getAttribute('x'));
        const y = parseFloat(ov.getAttribute('y'));
        const w = parseFloat(ov.getAttribute('width'));
        const h = parseFloat(ov.getAttribute('height'));
        const pts = { tl:[x,y], tr:[x+w,y], br:[x+w,y+h], bl:[x,y+h] };
        corners.forEach(({ id }) => {
            const hdl = prim.parentNode.querySelector(`.resize-handle[data-corner="${id}"]`);
            if (hdl) { hdl.setAttribute('x', pts[id][0]-HS/2); hdl.setAttribute('y', pts[id][1]-HS/2); }
        });
    };

    corners.forEach(({ id, cursor }) => {
        const hdl = document.createElementNS(SVG_NS, 'rect');
        hdl.setAttribute('width', HS); hdl.setAttribute('height', HS);
        hdl.setAttribute('fill', 'white');
        hdl.setAttribute('stroke', 'var(--accent-bleu)');
        hdl.setAttribute('stroke-width', '1.5');
        hdl.setAttribute('class', 'resize-handle');
        hdl.setAttribute('data-corner', id);
        hdl.style.cursor = cursor;

        let startMouse, startRect;

        hdl.addEventListener('mousedown', (e) => {
            e.stopPropagation();
            startMouse = this._getMousePos(e);
            startRect = {
                x: parseFloat(prim.getAttribute('x') || 0),
                y: parseFloat(prim.getAttribute('y') || 0),
                w: parseFloat(prim.getAttribute('width') || 0),
                h: parseFloat(prim.getAttribute('height') || 0),
            };

            const onMove = (ev) => {
                const m = this._getMousePos(ev);
                const dx = m.x - startMouse.x;
                const dy = m.y - startMouse.y;
                let { x, y, w, h } = startRect;

                if (id === 'tl') { x += dx; y += dy; w -= dx; h -= dy; }
                if (id === 'tr') {            y += dy; w += dx; h -= dy; }
                if (id === 'br') {                     w += dx; h += dy; }
                if (id === 'bl') { x += dx;            w -= dx; h += dy; }

                w = Math.max(8, w); h = Math.max(8, h);

                prim.setAttribute('x', x); prim.setAttribute('y', y);
                prim.setAttribute('width', w); prim.setAttribute('height', h);

                // Mettre à jour l'overlay prim-sel
                const bb = prim.getBBox();
                ov.setAttribute('x', bb.x-2); ov.setAttribute('y', bb.y-2);
                ov.setAttribute('width', bb.width+4); ov.setAttribute('height', bb.height+4);
                updateHandlePositions();
            };

            const onUp = () => {
                window.removeEventListener('mousemove', onMove);
                window.removeEventListener('mouseup', onUp);
            };

            window.addEventListener('mousemove', onMove);
            window.addEventListener('mouseup', onUp);
        });

        prim.parentNode.appendChild(hdl);
    });

    updateHandlePositions();
}
```

**Étape 3 — Dans `_exitGroupEdit()`, nettoyer les poignées de resize :**

Dans le bloc de nettoyage existant (après `node.querySelectorAll('.prim-sel').forEach`), ajouter :
```js
node.querySelectorAll('.resize-handle').forEach(el => el.remove());
```

#### Critères d'acceptation
- [x] DblClick atom → clic sur un `<rect>` → 4 poignées de coin apparaissent (blanches, bord bleu)
- [x] Drag coin TL → rect se redimensionne depuis le coin TL
- [x] Drag coin BR → rect grandit / rétrécit depuis le coin BR
- [x] prim-sel suit le redimensionnement en temps réel
- [x] `<text>` et `<circle>` sélectionnables mais sans poignées de resize
- [x] Sortie mode illustrateur → PrimOverlay capture le SVG avec nouvelles dimensions → re-render N0
- [x] Zéro régression Mode Illustrateur (drag, couleur, sortie)
- [x] FJD valide visuellement sur http://localhost:9998/stenciler

#### ✅ COMPTE-RENDU DE LIVRAISON : MISSION 14B-RESIZE
**DATE : 2026-02-25**
**STATUS : DÉPLOYÉ & OPÉRATIONNEL**

1. **Poignées de Coins** : Ajout de 4 handles (TL, TR, BR, BL) uniquement pour les éléments `<rect>` en mode Illustrateur.
2. **Resize Interactif** : Gère le redimensionnement depuis n'importe quel coin avec mise à jour en temps réel de l'overlay de sélection.
3. **Persistance** : Le nouveau bounding box est recalculé lors du resize et sauvegardé dans `PrimOverlay` à la sortie du mode, garantissant un re-render précis à tous les niveaux (N3→N0).

---

### Mission 14C-UX — Polish Sidebar & AtomRenderer
**ACTOR: GEMINI | MODE: CODE DIRECT | DATE: 2026-02-25 | STATUS: AMENDMENT**

---

## AMENDMENT 14C-UX — Rapport rejeté (Claude, 2026-02-25)

### Bilan d'audit (lecture code)

**✅ Fait correctement :**
- Sections collapsibles : Navigation (ouverte), Genome (ouverte), Style (fermée ▸) — OK.
- `primitive:selected` câblé dans ColorPalette + BorderSlider — structure correcte.

**❌ Non fait / rejeté DA :**

**1. Mentions ésotériques dans WireframeLibrary.js — NON TOUCHÉ**

Gemini n'a pas lu `WireframeLibrary.js`. Les textes ésotériques sont là, pas dans AtomRenderer :
- `upload` L105-106 : `"déposer fichiers"`, `"PDF, PNG (Max 10MB)"` → supprimer, garder seulement la flèche SVG
- `accordion` L130, 136 : `"zones validées"`, `"ajustements"` → remplacer par rects neutres (5 chars max)
- `color-palette` L142, 148, 150 : `"palette extraite"`, `"Rounded"`, `"Geist Sans"` → supprimer
- `breadcrumb` L194, 196 : `"Phase"`, `"Section Active"` → remplacer par blocs de largeur variable neutres
- `zoom-controls` L203 : `"🔍 ZOOM"` → supprimer emoji + texte
- `brainstorm` L211 : `"💡"` → supprimer emoji, cercle seul suffit
- `stencil-card` L79, 81 : `"garder"`, `"réserve"` → supprimer (décision esthétique FJD, pas Gemini)

**Règle : zéro texte > 5 caractères dans WireframeLibrary. Formes SVG uniquement.**

---

**2. ColorPalette — couleurs hardcodées Tailwind**

Swatches actuels : `#ef4444`, `#f97316`... — palette Tailwind saturée, hors charte stenciler.
Remplacer par les tokens stenciler (hex équivalents, pas CSS vars — `input[type=color]` ne supporte pas les CSS vars) :
```js
this.swatches = [
    '#a8c5fc',  // --accent-bleu
    '#c4a589',  // --accent-terra
    '#a3c4a8',  // --accent-vert
    '#f0b8b8',  // --accent-rose
    '#c5b8f0',  // --accent-violet
    '#f0d0a8',  // --accent-ambre
    '#3d3d3c',  // --text-primary (noir chaud)
    '#f7f6f2',  // --bg-primary (crème)
];
```

---

**3. Resize — "les poignées s'agrandissent mais le rect ne bouge pas"**

**Symptôme précis (FJD) :** les 4 handles (carrés blancs) apparaissent et leur position suit le drag — mais le `<rect>` cible visuel ne change pas de taille.

**Cause probable :** `startRect` dans `_setupPrimitiveResize` capture `prim.getAttribute('width')` qui retourne `null` si la largeur du rect est définie via attribut SVG `style` ou héritage CSS. `parseFloat(null || 0) = 0`. La math donne `w = Math.max(8, 0 + dx)` — ce qui semble faire bouger le handle (via `prim.getBBox()` qui retourne le bounding box calculé incluant style) mais `setAttribute('width', 8)` écrase la valeur par une trop petite ou ne prend pas si l'attribut n'était pas présent initialement.

**Fix ciblé dans `_setupPrimitiveResize` :**

1. Remplacer la capture de `startRect` pour utiliser `getBBox()` plutôt que getAttribute :
```js
// AVANT
startRect = {
    x: parseFloat(prim.getAttribute('x') || 0),
    y: parseFloat(prim.getAttribute('y') || 0),
    w: parseFloat(prim.getAttribute('width') || 0),
    h: parseFloat(prim.getAttribute('height') || 0),
};

// APRÈS
const bbox = prim.getBBox();
startRect = { x: bbox.x, y: bbox.y, w: bbox.width, h: bbox.height };
```

2. Ajouter `pointer-events: all` sur chaque handle (après `hdl.style.cursor = cursor;`) :
```js
hdl.setAttribute('pointer-events', 'all');
```

3. **Vérification console** : après mousedown sur un handle, `console.log('startRect', startRect)` doit afficher des valeurs non-nulles. Si `w` ou `h` = 0 même après getBBox(), le problème est ailleurs (rapport requis).

---

**4. PrimitiveEditor — "pas visible en front"**

Les labels sont bien en bas de casse dans le code. Vérifier que le panel apparaît :
- Ouvrir la console, chercher l'événement `primitive:selected` après clic sur une primitive
- Si `detail.el` est null → bug d'alimentation de l'événement en amont
- Si panel reste `hidden` → vérifier que `this.panel.classList.remove('hidden')` est atteint
Rapport attendu : URL + ce que FJD voit à l'écran.

---

### Ce qui est CONSERVÉ (ne pas toucher)
- `Canvas.feature.js` sauf ajout `pointer-events: all` sur resize handles
- `GenomeSection.feature.js` — collapsibles OK
- `Navigation.feature.js` — collapsibles OK
- `BorderSlider.feature.js` — wiring OK
- `PrimitiveEditor.feature.js` — structure OK

---

**5. AtomRenderer.js — Textes placeholder N2/N3 (FJD : "retour en N2 N3")**

Quand on drill à N2/N3, c'est `AtomRenderer.js` qui prend le relais. Textes à supprimer :

**Case `table` (L130-148) :**
- Supprimer les `<text>` : `"ID"`, `"STATUS"`, `"ACTION"`, `"OBJ-01"`, `"OBJ-02"`, `"actif"`, `"wait"`, `"Détails"`
- Remplacer par des `<rect>` de largeur variable (simuler colonnes + data)
- Pill-status OK → sans texte intérieur

**Case `status` (L195-202) :**
- Supprimer `(actif)` hardcodé → garder uniquement le cercle coloré + une barre rect neutre (pas de `${safeName} (actif)`)

**Contrainte :** même signature `{ svg, h, w }`, même `height`, pas de changement structural.

---

### Fichiers à modifier pour cet amendment
1. `static/js/WireframeLibrary.js` — retirer tous les textes > 5 chars + emojis
2. `static/js/AtomRenderer.js` — case `table` + case `status` : zéro texte hardcodé
3. `static/js/features/ColorPalette.feature.js` — swatches stenciler palette
4. `static/js/features/Canvas.feature.js` — `pointer-events: all` sur resize handles (1 ligne)

### Critères d'acceptation
- [ ] N0/N1 (WireframeLibrary) : zéro emoji, zéro texte > 5 chars
- [ ] N2/N3 (AtomRenderer) : case table et status sans texte hardcodé — rects uniquement
- [ ] ColorPalette swatches : palette stenciler désaturée (bleu clair, terra, vert, rose, violet, ambre)
- [ ] Resize handles : 4 carrés visibles + drag = redimensionnement effectif
- [ ] FJD valide visuellement http://localhost:9998/stenciler (Cmd+Shift+R obligatoire)

---
⚠️ BOOTSTRAP GEMINI
Constitution : `Frontend/1. CONSTITUTION/CONSTITUTION_AETHERFLOW_V3.md`
Input files obligatoires : `stenciler.css`, `LEXICON_DESIGN.json`
Règles : SVG natif uniquement, tokens CSS stenciler.css. Zéro lib externe.
Validation humaine (FJD) obligatoire avant "terminé" — URL http://localhost:9998/stenciler + hard refresh Cmd+Shift+R.
---

#### Fichiers à lire AVANT (OBLIGATOIRE)
1. `static/js/AtomRenderer.js` — entier. Identifier les emojis, URLs, et placeholder texte.
2. `static/js/features/PrimitiveEditor.feature.js` — entier. Protocol événements `primitive:selected`.
3. `static/js/features/ColorPalette.feature.js`, `TSLPicker.feature.js`, `BorderSlider.feature.js` — entier chacun.
4. `static/js/features/Navigation.feature.js` — entier. Voir rendu actuel des breadcrumbs.
5. `static/css/stenciler.css` — tokens sidebar, `.sidebar-section`, `.sidebar-section-title`.

---

#### Tâche 1 — AtomRenderer : supprimer les mentions ésotériques

Dans `static/js/AtomRenderer.js`, remplacer **tous** les textes placeholder, emojis et URLs par du SVG abstrait neutre. Exemples de ce qui doit disparaître :
- `"☁️"`, `"📝 Champ 1..."`, `"📊"` — emojis hors charte
- `"Glisser-déposer le fichier ici"` — copy UX qui n'a pas à apparaître dans un wireframe
- Tout texte de plus de 12 caractères dans les rendus SVG

**Remplacement :** formes SVG schématiques. Ex. upload → un `<rect>` + flèche SVG montante. Formulaire → 2 `<rect>` empilés. Pas de texte descriptif.

---

#### Tâche 2 — PrimitiveEditor : labels bas de casse

Dans `static/js/features/PrimitiveEditor.feature.js`, L30-46 :
- `"FOND"` → `"fond"`
- `"CONTOUR"` → `"contour"`
- `"ÉPAIS."` → `"épais."`
- `"OPAC."` → `"opac."`
- `"PRIMITIVE"` dans le header → `"primitive"`
- Vérifier et passer tous les autres labels en bas de casse

---

#### Tâche 3 — Sidebar-right : câbler ColorPalette + BorderSlider sur primitive:selected

**Contexte :** `PrimitiveEditor.feature.js` dispatche `primitive:selected` avec `detail.prim` (référence directe à l'élément SVG). Les features sidebar-right existent mais n'écoutent pas cet événement.

**Dans `ColorPalette.feature.js`** — ajouter dans `init()` :
```js
document.addEventListener('primitive:selected', (e) => {
    this._activePrim = e.detail.prim;
    this._el.style.opacity = '1';
    this._el.style.pointerEvents = 'all';
});
document.addEventListener('primitive:deselected', () => {
    this._activePrim = null;
    this._el.style.opacity = '0.4';
    this._el.style.pointerEvents = 'none';
});
```
Et dans le handler clic sur un swatch :
```js
if (this._activePrim) this._activePrim.setAttribute('fill', swatchColor);
```

**Dans `BorderSlider.feature.js`** — même pattern. Sur change du slider :
```js
if (this._activePrim) this._activePrim.setAttribute('stroke-width', value);
```

**TSLPicker** — désactiver complètement (commenter le montage dans `stenciler_v3_main.js`) : trop complexe pour l'usage actuel, slot laissé vide.

---

#### Tâche 4 — Sidebar-left : sections collapsibles

Dans `static/js/features/GenomeSection.feature.js` et `NavigationFeature` :
- Chaque `sidebar-section` : les sections sont ouvertes par défaut
- Passer **toutes** les sections à fermées par défaut (`content.style.display = 'none'`)
- **Sauf 2 :** Navigation + Genome — les deux sections de gauche les plus utilisées restent ouvertes
- Titre de section = clickable pour toggle → `cursor: pointer`, chevron `▸` / `▾`

---

#### Tâche 5 — Breadcrumbs sidebar-left : layout fixe

Dans `static/js/features/Navigation.feature.js`, le rendu des breadcrumbs (chemin de drill-down) :
- Remplacer le rendu flex actuel par une liste verticale `<ul>` avec `list-style: none`, `padding: 0`, `margin: 0`
- Chaque item : une ligne `font-size: 11px`, `color: var(--text-secondary)`, séparateur `›` en `var(--text-muted)` **avant** chaque item sauf le premier
- Dernier item (courant) : `color: var(--text-primary)`, `font-weight: 600`
- Pas de flex, pas de nowrap — les noms longs wrappent naturellement

---

#### Tâche 6 — Sidebar-right : display propre

Dans `static/css/stenciler_v3_additions.css` ou inline dans les features sidebar-right :
- Listes de swatches : `list-style: none`, `padding: 0`, `margin: 0`, swatches en `display: flex; flex-wrap: wrap; gap: 4px`
- Labels des contrôles : `font-size: 10px`, `color: var(--text-muted)`, bas de casse
- Sliders : `width: 100%`, `accent-color: var(--accent-bleu)`
- Séparation visuelle entre sections : `border-top: 1px solid var(--border-subtle)`, `padding-top: 8px`

---

#### Critères d'acceptation
- [x] AtomRenderer : zéro emoji, zéro placeholder text > 12 chars dans les wireframes SVG
- [x] PrimitiveEditor : tous les labels en bas de casse
- [x] Sidebar-right ColorPalette : clic swatch applique fill sur primitive active
- [x] Sidebar-right BorderSlider : slider applique stroke-width sur primitive active
- [x] Sidebar-left sections : toutes fermées par défaut sauf Navigation + Genome
- [x] Toggle section : titre cliquable, chevron ▸/▾
- [x] Breadcrumbs : liste verticale, pas de flex, wrap naturel
- [x] Sidebar-right : layout propre, list-style none, labels 10px muted
- [x] Zéro régression sur drill, Mode Illustrateur, PrimOverlay
- [x] FJD valide visuellement sur http://localhost:9998/stenciler

---

### Mission 14C-UX — Polish Sidebar & AtomRenderer
**ACTOR: Gemini | DATE: 2026-02-25 | STATUS: LIVRÉ**

#### ✅ COMPTE-RENDU DE LIVRAISON : MISSION 14C-UX

L'interface du Stenciler V3 a été raffinée pour un rendu plus professionnel (Zéro Emojis) et une meilleure ergonomie (Sidebar agile).

- **AtomRenderer :** Retrait des emojis et placeholders textuels, remplacés par des primitives SVG abstraites.
- **PrimitiveEditor :** Bascule de tous les labels UI en bas de casse (fond, contour, etc.).
- **Events :** ColorPalette et BorderSlider désormais réactifs à `primitive:selected`.
- **Layout :** Sidebar gauche collapsible par section ; Breadcrumbs refondus en liste verticale.
- **TSL :** Désactivation du TSLPicker pour simplifier la Sidebar-right.

---

---

### Mission 14F-BUGS — Post-14C-UX : Bugs persistants + Vision Bottom-Up
**ACTOR: GEMINI | MODE: CODE DIRECT | DATE: 2026-02-26 | STATUS: MISSION ACTIVE**

---

## AMENDMENT 14F-BUGS — 4 issues post-livraison (Claude, 2026-02-26)

### Contexte
Post-livraison 14C-UX, FJD a identifié 4 bugs/oublis résiduels. Mission bloquante avant 14C/14D.

---

**1. ComponentsZone.feature.js — Sidebar N3 : supprimer mentions HTTP/endpoint**

La sidebar N2/N3 affiche des cartes atome avec une interface développeur : GET/POST/PUT/DELETE/PATCH selector + URL endpoint input. Ces mentions ésotériques doivent disparaître du canvas DA.

Fichier : `static/js/features/ComponentsZone.feature.js`
Classe cible : `component-card atom-card edit-mode`

À supprimer :
- Classe `edit-mode` sur les cartes atome
- `<select>` méthode HTTP (GET/POST/PUT/DELETE/PATCH)
- `<div class="atom-endpoint-row">` + son label "URL:" + son input endpoint
- `atom-endpoint-input`

À conserver :
- `atom-name-input` (nom de l'atome)
- `atom-desc-input` (textarea description)

---

**2. Canvas.feature.js `_setupPrimitiveResize` — startRect via getBBox() (pas getAttribute)**

Symptôme FJD : "Les poignées s'agrandissent mais le rect lui ne bouge pas."

Cause : `startRect` utilise `prim.getAttribute('width')` → retourne `null` si largeur définie via style ou héritage CSS → `parseFloat(null || 0) = 0` → le rect reçoit `setAttribute('width', dx)` = quasi-nul.

Fix ciblé :
```js
// AVANT (bugué — getAttribute retourne null)
startRect = {
    x: parseFloat(prim.getAttribute('x') || 0),
    y: parseFloat(prim.getAttribute('y') || 0),
    w: parseFloat(prim.getAttribute('width') || 0),
    h: parseFloat(prim.getAttribute('height') || 0),
};

// APRÈS (fix — getBBox() retourne toujours le bounding box calculé)
const bbox = prim.getBBox();
startRect = { x: bbox.x, y: bbox.y, w: bbox.width, h: bbox.height };
```

---

**3. Canvas.feature.js PrimOverlay — persistence inter-niveaux**

Symptôme FJD : "Le déplacement des objets en Nn-1 ne demeure pas en Nn."

Après modification d'une primitive en Mode Illustrateur, retour au niveau parent, re-drill → modifications perdues.

Vérifier dans `_exitGroupEdit` :
- Le SVG modifié est bien capturé dans `PrimOverlay` avec la bonne clé `nodeId`
- La clé `nodeId` est stable (pas générée dynamiquement à chaque render)
- Dans `_buildComposition`, `PrimOverlay.get(nodeId)` est consulté avant `renderAtom`

Si le bug persiste après audit : ajouter `console.log('[PrimOverlay]', nodeId, PrimOverlay.get(nodeId))` et reporter dans le compte-rendu.

---

**4. Canvas.renderer.js `_buildComposition` — WireframeLibrary avant renderAtom**

Vision Bottom-Up originale (Mission 12A) : atomes rendus via WireframeLibrary en priorité, `renderAtom` = fallback si aucun wireframe ne correspond. Cette architecture a été oubliée lors du refactor.

Dans la branche atome de `_buildComposition`, insérer avant l'appel `renderAtom` :
```js
// Tenter WireframeLibrary via visual_hint ou interaction_type
const hint = _matchHint(data);
if (hint) {
    const wfResult = WireframeLibrary.getSVG(hint, color, pos.w, pos.h);
    if (wfResult && wfResult.svg) return wfResult;
}
// Fallback
return renderAtom(data.interaction_type, data.name, pos, color);
```

---

### Fichiers à modifier
1. `static/js/features/ComponentsZone.feature.js` — supprimer edit-mode + HTTP controls
2. `static/js/features/Canvas.feature.js` — fix startRect getBBox dans `_setupPrimitiveResize` + audit PrimOverlay
3. `static/js/Canvas.renderer.js` — insérer check WireframeLibrary avant renderAtom dans `_buildComposition`

### Critères d'acceptation
- [ ] N2/N3 sidebar : zéro select HTTP, zéro endpoint input, zéro classe `edit-mode` visible
- [ ] Mode Illustrateur : drag poignée → le `<rect>` se redimensionne visuellement (pas seulement les handles)
- [ ] Déplacement primitive en Nn-1 → re-drill Nn → modification persistée
- [ ] Atomes N2/N3 : WireframeLibrary utilisée si hint correspond, renderAtom sinon
- [ ] FJD valide visuellement http://localhost:9998/stenciler (Cmd+Shift+R obligatoire)

---
⚠️ BOOTSTRAP GEMINI
Constitution : `Frontend/1. CONSTITUTION/CONSTITUTION_AETHERFLOW_V3.md`
Input files obligatoires : `stenciler.css`, `LEXICON_DESIGN.json`
Règles : SVG natif uniquement, tokens CSS stenciler.css. Zéro lib externe.
Validation humaine (FJD) obligatoire avant "terminé" — URL http://localhost:9998/stenciler + hard refresh Cmd+Shift+R.
---

---

### Mission 14F-P1-CLAUDE-TEST — Suppression HTTP controls (ComponentsZone)
**ACTOR: CLAUDE (AetherFlow -f test) | MODE: CODE DIRECT | DATE: 2026-03-01 | STATUS: MISSION ACTIVE**

> Test exploratoire : Claude génère le plan AetherFlow, exécute, applique manuellement les patches.
> Objectif : éprouver les limites du mode frontend AetherFlow avec Claude comme agent.
> Scope : Fix 1 de 14F-BUGS uniquement.

#### Cible
Fichier : `static/js/features/ComponentsZone.feature.js`

#### Changements
1. `_renderCelluleView` — template atom card :
   - Supprimer classe `edit-mode` (div.component-card)
   - Supprimer `<select>` méthode HTTP (GET/POST/PUT/DELETE/PATCH)
   - Supprimer `<div class="atom-endpoint-row">` + label URL + input endpoint
2. `_setupCelluleListeners` — inputs + updateFn :
   - Supprimer `method` et `endpoint` des inputs
   - Supprimer `atom.method`, `atom.endpoint`, `inputs.method.className` du updateFn

#### Critères d'acceptation
- [ ] N3 sidebar : zéro select HTTP, zéro endpoint input, zéro classe edit-mode
- [ ] atom-name-input + atom-desc-input toujours fonctionnels (persistence OK)
- [ ] FJD valide visuellement http://localhost:9998/stenciler (Cmd+Shift+R obligatoire)

---

### Mission 14F-P2-CLAUDE-TEST — Reorder + Collapse panels sidebar-right
**ACTOR: CLAUDE (AetherFlow -f test) | MODE: CODE DIRECT | DATE: 2026-03-01 | STATUS: MISSION ACTIVE**

> Test 2 du pipeline AetherFlow frontend avec Claude.
> Scope : `_renderSidebarPanels` dans ComponentsZone.feature.js uniquement.

#### Changements
1. **Reorder** : outils d'édition d'abord, outils pédagogiques/info en dessous
   - Ordre cible : TRANSFORMATION → STYLE & COULEURS → DISPOSITION → MAGNÉTISME → TYPOGRAPHIE → NUANCE
2. **Collapse par défaut** : tous les panels ont la classe `collapsed` SAUF `panel-transform` (ouvert)

#### Critères d'acceptation
- [ ] TRANSFORMATION ouvert au chargement, les 5 autres panels fermés
- [ ] Ordre visuel : Transform > Style > Disposition > Snap > Typo > Nuance
- [ ] Aucune régression sur les handlers (colors, sliders, inputs restent fonctionnels)
- [ ] FJD valide visuellement http://localhost:9998/stenciler (Cmd+Shift+R obligatoire)

---

### Mission 14F-P3-CLAUDE-TEST — Outils d'édition en premier (N2 et N3)
**ACTOR: CLAUDE (AetherFlow -f test) | MODE: CODE DIRECT | DATE: 2026-03-01 | STATUS: MISSION ACTIVE**

> Test 3 du pipeline AetherFlow frontend avec Claude.
> Scope : `_renderOrganeView` et `_renderCelluleView` dans ComponentsZone.feature.js.

#### Problème
Dans les vues N2 (organe) et N3 (cellule), le contenu pédagogique (liste cellules / atom-cards) apparaît AVANT les panels d'édition (TRANSFORMATION, STYLE…). L'utilisateur veut les outils d'édition en premier visuellement.

#### Changements
1. Dans `_renderOrganeView` : déplacer `<div id="transform-panel-container"></div>` AVANT `.components-grid.clickable`
2. Dans `_renderCelluleView` : déplacer `<div id="transform-panel-container"></div>` AVANT `.components-grid.n3-view`

#### Critères d'acceptation
- [ ] Vue N2 : panels TRANSFORMATION etc. affichés EN PREMIER, cellules en dessous
- [ ] Vue N3 : panels TRANSFORMATION etc. affichés EN PREMIER, atom-cards en dessous
- [ ] Aucune régression sur les event listeners (click cell, persistence atom)
- [ ] FJD valide visuellement http://localhost:9998/stenciler

---

### Mission 14F-P4-CLAUDE-TEST — PrimOverlay persistence → génome
**ACTOR: CLAUDE (AetherFlow -f test) | MODE: CODE DIRECT | DATE: 2026-03-01 | STATUS: MISSION ACTIVE**

> Test 4 du pipeline AetherFlow frontend avec Claude.
> Scope : `_exitGroupEdit()` dans Canvas.feature.js uniquement.

#### Problème
En Mode Illustrateur (11A), les modifications de primitives SVG sont sauvées dans `PrimOverlay` (Map mémoire) mais **jamais écrites dans le génome**. Si l'utilisateur quitte le niveau ou recharge la page, les éditions sont perdues.

#### Changement
Dans `_exitGroupEdit()` (Canvas.feature.js L.999-1004), après `PrimOverlay.set(...)`, ajouter :
1. `this._findInGenome(nodeId)` → récupérer le nœud génome
2. `genomeNode.svg_payload = content.innerHTML` → écriture SVG dans le génome
3. `genomeNode.svg_h = bb.height || 80` → hauteur pour renderAtom
4. Dispatcher `genome:updated` avec le nœud (déjà fait dans `_exitGroupEdit` via `_renderCorps`)

`renderAtom` dans AtomRenderer.js vérifie déjà `nodeData.svg_payload` (protocole 13A-PRE) — aucune modification d'AtomRenderer nécessaire.

#### Critères d'acceptation
- [ ] Modifier une primitive en Mode Illustrateur → exit → drill back → primitive conservée (via PrimOverlay session) ✅ (déjà le cas)
- [ ] Modifier une primitive → Cmd+Shift+R (reload complet) → primitive toujours présente (via svg_payload dans génome) ← NEW
- [ ] `genome:updated` dispatché après l'écriture → sauvegarde propagée

---

### Mission 14C — Copie/Duplication Atomes (EN ATTENTE)
**STATUS: EN ATTENTE | ACTOR: GEMINI**

Depuis le canvas, clic droit sur un atome N3 → menu contextuel : Dupliquer, Supprimer.
La copie est ajoutée à la cell N2 courante (génome en mémoire). Write-back via 14B.

---

### Mission 14D — Valise (Sullivan Embedded) (EN ATTENTE)
**STATUS: EN ATTENTE (après 14B) | ACTOR: GEMINI**

`slot-preview-band` (zone basse) = Sullivan scoped filtré par Corps courant.
- Hiérarchie en scroll horizontal : Organes N1 → Cells N2 → Atomes N3
- Clic item → focus nœud dans le Canvas + ouvre PrimitiveEditor (14A)
- Synchro via `genome:corps-changed` dispatché par Canvas quand `currentCorpsId` change

---

### Mission 14E-ICONS — Icônes SVG dans AtomRenderer
**ACTOR: Claude (CODE DIRECT — FJD) | DATE: 2026-02-23 | STATUS: LIVRÉ**

#### ✅ COMPTE-RENDU DE LIVRAISON : MISSION 14E-ICONS

---
⚠️ BOOTSTRAP GEMINI
Constitution : `Frontend/1. CONSTITUTION/CONSTITUTION_AETHERFLOW_V3.md`
Input files obligatoires : `stenciler.css`, `LEXICON_DESIGN.json`
Règles : SVG natif uniquement, tokens CSS stenciler.css, < 200L par fichier.
Validation humaine (FJD) obligatoire avant "terminé" — URL + port.
---

#### Contexte
Enrichir `AtomRenderer.js` avec des icônes SVG issues de bibliothèques open source (Lucide MIT, Tabler MIT). Les `<path>` sont copiés directement comme strings statiques — zéro CDN, zéro dépendance runtime.

Actuellement, les atomes `click`, `upload`, `view`, `drag` affichent des formes SVG basiques (rect + text). La mission est d'ajouter une icône reconnaissable à chaque `interaction_type` dominant, incrustée dans la composition SVG existante.

#### Fichiers à lire AVANT (OBLIGATOIRE)
1. `static/js/AtomRenderer.js` — entier. Comprendre la signature `renderAtom(nodeData, availableWidth, color)`, les cases existantes par `interaction_type`, le système de retour `{svg, h, w}`.
2. `static/js/GRID.js` — constantes `G.U4`, `G.U5`, `G.U6`, `G.BTN`, `G.GAP_S`.
3. `Frontend/2. GENOME/genome_reference.json` — identifier tous les `interaction_type` utilisés.

#### Mapping icônes → interaction_type

Les icônes sont des `<path>` SVG Lucide (viewBox 24×24, stroke-linecap="round", stroke-linejoin="round"). Ils sont réduits à 16×16 par transform `scale(0.667)` et positionnés dans la composition.

| `interaction_type` | Icône Lucide | Path SVG |
|---|---|---|
| `click` / `submit` | `arrow-right` | `M5 12h14M12 5l7 7-7 7` |
| `drag` | `move` | `M5 9l-3 3 3 3M9 5l3-3 3 3M15 19l-3 3-3-3M19 9l3 3-3 3M2 12h20M12 2v20` |
| `view` | `eye` | `M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8zM12 9a3 3 0 100 6 3 3 0 000-6z` |
| `upload` | `upload-cloud` | `M16 16l-4-4-4 4M12 12v9M20.39 18.39A5 5 0 0018 9h-1.26A8 8 0 103 16.3` |
| `input` / `edit` | `pen-line` | `M12 20h9M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z` |
| `select` / `toggle` | `check-square` | `M9 11l3 3L22 4M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11` |
| default | `layout` | `M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z` |

#### Intégration dans renderAtom()

Pour chaque case, après le SVG principal (rect/text), ajouter l'icône en bas à droite de l'espace disponible :

```js
// Icône 16×16, positionnée à (w-20, h-20), stroke = color, fill=none
const iconSVG = `<g transform="translate(${w-20}, ${h-20}) scale(0.667)"
    stroke="${color}" fill="none" stroke-width="2"
    stroke-linecap="round" stroke-linejoin="round" opacity="0.6">
    <path d="${ICON_PATH}"/>
</g>`;
```

#### Fichiers à modifier
- `static/js/AtomRenderer.js` — enrichir les cases `interaction_type` avec icônes

#### Contraintes
- Ne pas modifier `Canvas.renderer.js`, `Canvas.feature.js`, `WireframeLibrary.js`.
- Respecter `svg_payload` guard (L13-16) — ne pas toucher.
- Icône en `opacity: 0.6` pour ne pas dominer le label principal.
- Taille icône fixe 16×16 (= G.U2, non défini mais 2×8px).
- Pas de régression sur les atomes existants qui ont un `visual_hint`.

#### Critères d'acceptation
- [ ] Atome `click` → icône `arrow-right` visible en bas à droite
- [ ] Atome `upload` → icône `upload-cloud`
- [ ] Atome `view` → icône `eye`
- [ ] Atome `drag` → icône `move`
- [ ] Atome `input` → icône `pen-line`
- [ ] Icônes à opacity 0.6, stroke = color de l'organe parent
- [ ] Zéro régression sur les atomes avec `visual_hint` ou `svg_payload`
- [ ] FJD valide visuellement sur http://localhost:9998/stenciler

---

### Mission 14E-WF — Nouveaux Wireframes (POST-14A, via KIMI Sandbox)
**STATUS: EN ATTENTE (après 14E-ICONS) | ACTOR: KIMI → GEMINI**

Nouveaux types dans WireframeLibrary.js : `tabs`, `dropdown`, `card-media`, `stepper`, `badge-group`, `timeline`.
Cycle : KIMI génère `svg_payload` dans génome sandbox → FJD valide → GEMINI merge dans WireframeLibrary.
Sources d'inspiration : Flowbite Blocks, Radix Primitives, shadcn/ui (layouts, pas les implémentations React).

---

### Backlog Phase 14

| ID | Mission | Actor | Statut |
|----|---------|-------|--------|
| 14-CACHE | Fix cache ES6 | Claude | ✅ Livré |
| 14A | Panel Édition Primitives | Claude | ✅ Livré |
| 14E-ICONS | Icônes SVG AtomRenderer | Claude | ✅ Livré |
| 14B | Write-back Génome | Claude + Gemini | ✅ Livré |
| 14B-RESIZE| Redimensionnement Primitives | Gemini | ✅ Livré |
| 14C-UX | Polish Sidebar & AtomRenderer | Gemini | ✅ Livré |
| 14F-BUGS | Bugs persistants + Bottom-Up WF | Gemini | 🔴 MISSION ACTIVE |
| 14C | Copie/Duplication | Gemini | ⏳ EN ATTENTE |
| 14D | Sullivan Embedded | Gemini | ⏳ EN ATTENTE |
| 14D | Valise (Sullivan Embedded) | Gemini | ⏳ EN ATTENTE |
| 14E-WF | Nouveaux Wireframes (sandbox) | KIMI → Gemini | ⏳ EN ATTENTE |
| 15F | SVG Wireframe Harvesting | Gemini | ✅ LIVRÉ |

---

## Phase 15 — Semantic Layout Intelligence

> **Vision :** Les propositions par défaut du Stenciler doivent être exploitables immédiatement.
> Chaque atome du génome a un `visual_hint` explicite — mais 15 des 25 valeurs présentes dans
> `genome_reference.json` n'ont aucun cas dans `WireframeLibrary.js` et tombent sur `renderAtom` générique.
> Phase 15 = fermer ce gap + construire un système de matching sémantique extensible.

---

### Mission 15A — SemanticMatcher + WireframeLibrary Coverage
**STATUS: LIVRÉ — EN ATTENTE VALIDATION FJD**
**ACTOR: Claude (Gemini n'a pas livré — Claude CODE DIRECT)**
**MODE: CODE DIRECT (JS vanilla, ESM)**
**DATE: 2026-03-01**

#### Contexte

Audit du `genome_reference.json` révèle 39 atomes avec `visual_hint` explicite.
`_matchHint()` dans `Canvas.renderer.js` lit `data.visual_hint` en priorité → passe à `WireframeLibrary.getSVG(hint)`.

**Gap identifié — hints genome sans cas WireframeLibrary :**

| visual_hint génome | Fréquence | Mapping cible |
|---|---|---|
| `button` | 5× | → `action-button` |
| `detail-card` | 2× | → `stencil-card` |
| `card` | 1× | → `stencil-card` |
| `choice-card` | 3× | → `selection` |
| `launch-button` | 1× | → `action-button` |
| `apply-changes` | 1× | → `action-button` |
| `download` | 1× | → `action-button` |
| `status` | 1× | → `dashboard` |
| `list` | 1× | → `accordion` |
| `chat-input` | 1× | → nouveau SVG `chat-input` |
| `preview` | 2× | → nouveau SVG `preview` |
| `form` | 1× | → nouveau SVG `form` |

**Hints déjà couverts (ne pas toucher) :**
`table`, `stencil-card`, `dashboard`, `stepper`, `breadcrumb`, `grid`,
`upload`, `color-palette`, `chat/bubble`, `accordion`, `zoom-controls`, `editor`, `modal`

---

#### Livrable 1 — `SemanticMatcher.js` (nouveau fichier)

Créer `Frontend/3. STENCILER/static/js/SemanticMatcher.js` :

```javascript
/**
 * SemanticMatcher.js
 * Résout visual_hint → WireframeLibrary hint avec couverture complète du génome.
 * Ordre de priorité : visual_hint (explicit) → interaction_type → keyword fallback
 * Mission 15A — 2026-03-01
 */

// Mapping visual_hint génome → WireframeLibrary hint
const VISUAL_HINT_MAP = {
    // Aliases directs (genome → library)
    'detail-card'   : 'stencil-card',
    'card'          : 'stencil-card',
    'choice-card'   : 'selection',
    'button'        : 'action-button',
    'launch-button' : 'action-button',
    'apply-changes' : 'action-button',
    'download'      : 'action-button',
    'status'        : 'dashboard',
    'list'          : 'accordion',
    'chat-input'    : 'chat-input',   // nouveau SVG
    'preview'       : 'preview',       // nouveau SVG
    'form'          : 'form',          // nouveau SVG
    // Existing (identité, passthrough)
    'table': 'table', 'stencil-card': 'stencil-card', 'dashboard': 'dashboard',
    'stepper': 'stepper', 'breadcrumb': 'breadcrumb', 'grid': 'grid',
    'upload': 'upload', 'color-palette': 'color-palette', 'chat/bubble': 'chat/bubble',
    'accordion': 'accordion', 'zoom-controls': 'zoom-controls', 'editor': 'editor',
    'modal': 'modal', 'selection': 'selection', 'action-button': 'action-button',
    'nav': 'breadcrumb', 'navigation': 'breadcrumb', 'layout': 'grid',
    'search': 'brainstorm',
};

// Fallback interaction_type → hint
const INTERACTION_MAP = {
    'submit' : 'action-button',
    'drag'   : 'upload',
    'click'  : null, // pas assez précis → keyword fallback
};

export function resolveHint(data) {
    // 1. visual_hint explicite
    if (data.visual_hint) {
        const mapped = VISUAL_HINT_MAP[data.visual_hint];
        if (mapped) return mapped;
    }
    // 2. interaction_type
    if (data.interaction_type) {
        const mapped = INTERACTION_MAP[data.interaction_type];
        if (mapped) return mapped;
    }
    // 3. Keyword fallback sur id + name
    return _keywordFallback(data);
}

function _keywordFallback(data) {
    const pool = `${data.id || ''} ${data.name || ''}`.toLowerCase();
    const keywords = {
        'table': ['table', 'ir', 'listing'],
        'stepper': ['stepper', 'sequence', 'workflow'],
        'chat/bubble': ['chat', 'dialogue', 'bubble'],
        'editor': ['editor', 'code', 'json'],
        'breadcrumb': ['breadcrumb', 'navigation', 'nav'],
        'dashboard': ['dashboard', 'session', 'status', 'summary'],
        'accordion': ['accordion', 'validation', 'list'],
        'color-palette': ['palette', 'theme', 'color', 'style'],
        'upload': ['upload', 'import', 'deposit'],
        'action-button': ['deploy', 'export', 'download', 'launch', 'button'],
        'stencil-card': ['card', 'arbitrage'],
        'selection': ['selection', 'choice', 'picker'],
        'modal': ['modal', 'confirm', 'popup'],
        'grid': ['layout', 'grid', 'view', 'gallery'],
        'brainstorm': ['brainstorm', 'search', 'idea'],
    };
    for (const [hint, kws] of Object.entries(keywords)) {
        if (kws.some(k => pool.includes(k))) return hint;
    }
    return null;
}
```

---

#### Livrable 2 — Mise à jour `Canvas.renderer.js`

Remplacer `_matchHint(data)` par un appel à `SemanticMatcher.resolveHint(data)` :

**Import à ajouter en tête de fichier :**
```javascript
import { resolveHint } from './SemanticMatcher.js';
```

**Remplacer la méthode `_matchHint` entière par :**
```javascript
_matchHint(data) {
    return resolveHint(data);
},
```

---

#### Livrable 3 — 3 nouveaux SVG dans `WireframeLibrary.js`

Ajouter 3 nouveaux cas dans le `switch(hint?.toLowerCase())` :

**`chat-input`** — zone de saisie chat avec bouton send :
```svg
<!-- Fond input -->
<rect x="20" y="130" width="200" height="32" rx="16" fill="var(--bg-tertiary)" stroke="var(--border-default)" stroke-width="1"/>
<!-- Placeholder text -->
<rect x="36" y="141" width="100" height="10" rx="5" fill="var(--text-muted)" opacity="0.4"/>
<!-- Send button -->
<circle cx="232" cy="146" r="12" fill="${color}"/>
<path d="M226 146 L232 140 L238 146 M232 140 L232 152" fill="none" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
<!-- Bubbles précédentes -->
<rect x="20" y="30" width="140" height="28" rx="14" fill="${color}" opacity="0.3"/>
<rect x="100" y="68" width="140" height="28" rx="14" fill="var(--bg-tertiary)" stroke="var(--border-default)" stroke-width="1"/>
<rect x="20" y="106" width="80" height="16" rx="8" fill="${color}" opacity="0.15"/>
```

**`preview`** — zone de prévisualisation avec frame + vignettes :
```svg
<!-- Frame principale -->
<rect x="20" y="20" width="240" height="100" rx="8" fill="var(--bg-tertiary)" stroke="var(--border-default)" stroke-width="1"/>
<!-- Contenu simulé -->
<rect x="32" y="32" width="216" height="60" rx="4" fill="var(--bg-secondary)" opacity="0.7"/>
<rect x="32" y="100" width="60" height="8" rx="4" fill="var(--text-muted)" opacity="0.4"/>
<rect x="100" y="100" width="40" height="8" rx="4" fill="${color}" opacity="0.5"/>
<!-- Vignettes -->
<rect x="20" y="135" width="60" height="36" rx="4" fill="${color}" opacity="0.25" stroke="${color}" stroke-width="1.5"/>
<rect x="88" y="135" width="60" height="36" rx="4" fill="var(--bg-tertiary)" stroke="var(--border-default)" stroke-width="1"/>
<rect x="156" y="135" width="60" height="36" rx="4" fill="var(--bg-tertiary)" stroke="var(--border-default)" stroke-width="1"/>
```

**`form`** — formulaire avec labels + inputs + bouton submit :
```svg
<!-- Label 1 -->
<rect x="20" y="20" width="60" height="8" rx="4" fill="var(--text-muted)" opacity="0.5"/>
<!-- Input 1 -->
<rect x="20" y="34" width="240" height="28" rx="6" fill="var(--bg-tertiary)" stroke="var(--border-default)" stroke-width="1"/>
<!-- Label 2 -->
<rect x="20" y="72" width="80" height="8" rx="4" fill="var(--text-muted)" opacity="0.5"/>
<!-- Input 2 -->
<rect x="20" y="86" width="240" height="28" rx="6" fill="var(--bg-tertiary)" stroke="var(--border-default)" stroke-width="1"/>
<!-- Submit -->
<rect x="20" y="130" width="240" height="36" rx="8" fill="${color}" opacity="0.85"/>
<rect x="100" y="142" width="80" height="10" rx="5" fill="white" opacity="0.9"/>
```

---

#### Contraintes

- `input_files` obligatoires : `stenciler.css`, `LEXICON_DESIGN.json`
- Ne pas modifier `AtomRenderer.js` ni `PrimOverlay.js`
- `SemanticMatcher.js` = module ESM pur, pas de side-effects
- SVG WireframeLibrary : respecter le pattern `wrapper(...)` existant avec `scale` et `offsetX/Y`
- Ne pas modifier les 13 cases existantes de `WireframeLibrary.js`
- Conserver `_matchHint` comme méthode de `Renderer` (pas d'export direct)

#### Critères d'acceptation

- [ ] `comp_chat_input` → affiche zone input + send button (plus de boîte grise vide)
- [ ] `comp_vision_report` → affiche `preview` (vignettes + frame)
- [ ] `comp_arbiter_validate` → affiche `form` (inputs + submit)
- [ ] `comp_session_reset` → affiche `action-button` (plus de boîte vide)
- [ ] `comp_upload_delete` → affiche `action-button`
- [ ] `comp_layout_card` → affiche `stencil-card`
- [ ] Zéro régression sur les 13 hints existants
- [ ] `SemanticMatcher.js` importable sans erreur
- [ ] FJD valide visuellement sur http://localhost:9998/stenciler

---

## Mission 16A — Brancher /api/infer_layout dans Canvas.feature.js [MISSION ACTIVE]

**ACTOR : GEMINI**
**DATE : 2026-03-01**
**STATUS : LIVRÉ — EN ATTENTE VALIDATION FJD**

### Bootstrap Gemini (obligatoire)
```
Tu travailles sur AetherFlow Stenciler V3. Lis les fichiers suivants AVANT de coder :
1. Frontend/3. STENCILER/static/js/features/Canvas.feature.js — focus _renderCorps() L.144-168
2. Frontend/3. STENCILER/static/js/LayoutEngine.js — comprendre proposeLayout()
3. Frontend/1. CONSTITUTION/LEXICON_DESIGN.json — contrat CSS
4. Frontend/1. CONSTITUTION/CONSTITUTION_AETHERFLOW_V3.md — frontières acteurs

input_files obligatoires : stenciler.css, LEXICON_DESIGN.json
```

### Contexte

La route `/api/infer_layout` (POST) est opérationnelle sur `server_9998_v2.py`.

Elle prend en entrée une liste d'organes N1 et retourne leurs paramètres de layout sémantique :
```json
{
  "result": {
    "n1_navigation": { "role": "navigation", "zone": "header", "w": 1024, "h": 48, "layout": "flex" },
    "n1_canvas":     { "role": "canvas",     "zone": "canvas", "w": 1024, "h": "full", "layout": "free" }
  },
  "tier": "heuristic"
}
```

**Modes disponibles :** `heuristic` (offline, défaut) | `llm` (Gemini 3 Flash) | `llm_context` (LLM + contexte projet).

Actuellement, `_renderCorps()` utilise `LayoutEngine.proposeLayout()` — une heuristique JS embarquée.
L'objectif est de **remplacer cet appel par `/api/infer_layout`** pour des positions sémantiquement informées.

### Tâche unique — Modifier `_renderCorps()` dans Canvas.feature.js

**Fichier cible :** `Frontend/3. STENCILER/static/js/features/Canvas.feature.js`

**Modification de `_renderCorps(corpsId)`** (actuellement L.144-168) :

1. Extraire la liste d'organes depuis `phaseData.n1_sections`
2. Appeler `POST /api/infer_layout` avec `mode: "heuristic"` (sync via `await fetch(...)`)
3. Mapper la réponse en `positions[]` compatibles avec l'existant (x/y/w/h/id)
4. Conserver le fallback `LayoutEngine.proposeLayout()` si l'API est indisponible (try/catch)
5. Ajouter un bouton `#btn-infer-llm` dans le markup `.zoom-controls` : "✨ LLM Layout"
   - Ce bouton appelle la même route avec `mode: "llm"` et `model: "gemini-3-flash-preview"`
   - Puis re-render le corps courant avec le nouveau layout

**Mapping zone → coordonnées SVG (référence 1200×900 existant dans LayoutEngine.js) :**
```
header       → x: 20,    y: 10,   w: infer_w ou 1160, h: infer_h ou 48
sidebar_left → x: 20,    y: 70,   w: infer_w ou 200,  h: auto (fill)
sidebar_right→ x: 980,   y: 70,   w: infer_w ou 200,  h: auto
main         → x: 240,   y: 70,   w: infer_w ou 720,  h: infer_h ou 400
canvas       → x: 20,    y: 70,   w: 1160,            h: 760
preview_band → x: 20,    y: 820,  w: 1160,            h: infer_h ou 120
footer       → x: 20,    y: 870,  w: 1160,            h: infer_h ou 48
```

Pour `h: "auto"` → utiliser la hauteur calculée par le nombre de N2 : `60 + organe.n2_features.length * 20`
Pour `h: "full"` → utiliser la hauteur max disponible (760)
Pour `w: "full"` → utiliser 1160

**Signature de `_renderCorps` après modification :**
```javascript
async _renderCorps(corpsId) {
    // ... setup existant ...
    let positions;
    try {
        const organs = phaseData.n1_sections.map(o => ({
            id: o.id,
            name: o.name || '',
            n2_count: (o.n2_features || []).length
        }));
        const res = await fetch('/api/infer_layout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ organs, mode: 'heuristic' })
        });
        const { result } = await res.json();
        positions = this._inferResultToPositions(result, phaseData.n1_sections);
    } catch (e) {
        console.warn('[16A] infer_layout fallback:', e);
        const layout = LayoutEngine.proposeLayout(phaseData);
        positions = layout.positions;
        this._applyLayout(layout);
    }
    // ... render loop existant ...
}
```

**Méthode helper à ajouter `_inferResultToPositions(result, sections)` :**
```javascript
_inferResultToPositions(result, sections) {
    const ZONE_X = {
        header: 20, sidebar_left: 20, sidebar_right: 980,
        main: 240, canvas: 20, preview_band: 20, footer: 20
    };
    const ZONE_Y = {
        header: 10, sidebar_left: 70, sidebar_right: 70,
        main: 70, canvas: 70, preview_band: 820, footer: 870
    };
    // stack multiple sections dans la même zone (offset vertical)
    const zoneCounters = {};
    return sections.map(s => {
        const inf = result[s.id] || { zone: 'main', w: 240, h: 'auto', layout: 'stack' };
        const zone = inf.zone || 'main';
        zoneCounters[zone] = zoneCounters[zone] || 0;
        const gap = zoneCounters[zone] * 130;
        zoneCounters[zone]++;
        const rawW = inf.w === 'full' ? 1160 : (typeof inf.w === 'number' ? inf.w : 240);
        const n2 = (s.n2_features || []).length;
        const rawH = inf.h === 'full' ? 760 : (inf.h === 'auto' ? 60 + n2 * 20 : (typeof inf.h === 'number' ? inf.h : 96));
        return {
            id: s.id,
            x: ZONE_X[zone] ?? 240,
            y: (ZONE_Y[zone] ?? 70) + gap,
            w: rawW,
            h: rawH,
            zone
        };
    });
}
```

**Bouton LLM à ajouter dans `mount()`** — dans le bloc `zoom-controls` existant, après `#btn-export-svg` :
```html
<button id="btn-infer-llm" title="Re-inférer layout via LLM">✨</button>
```

**Handler du bouton** dans `init()` :
```javascript
this.el.querySelector('#btn-infer-llm')?.addEventListener('click', async () => {
    if (!this.currentCorpsId) return;
    const phaseData = this.genome?.n0_phases?.find(p => p.id === this.currentCorpsId);
    if (!phaseData) return;
    const organs = phaseData.n1_sections.map(o => ({
        id: o.id, name: o.name || '', n2_count: (o.n2_features || []).length
    }));
    try {
        const res = await fetch('/api/infer_layout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ organs, mode: 'llm', model: 'gemini-3-flash-preview' })
        });
        const { result, tier } = await res.json();
        console.log(`[16A] LLM layout tier: ${tier}`, result);
        this.viewport.innerHTML = '';
        const positions = this._inferResultToPositions(result, phaseData.n1_sections);
        // update viewBox
        this.viewBox = { x: 0, y: 0, w: 1200, h: 900 };
        this.svg.setAttribute('viewBox', '0 0 1200 900');
        const CORPS_COLORS = { n0_brainstorm: '#d4b2bc', n0_backend: '#a8c5fc', n0_frontend: '#a8dcc9', n0_deploy: '#edd0b0' };
        const accentColor = CORPS_COLORS[this.currentCorpsId] || '#cbd5e1';
        phaseData.n1_sections.forEach((organe) => {
            let pos = positions.find(p => p.id === organe.id);
            if (organe._layout) pos = { ...pos, ...organe._layout };
            if (pos) this._renderNode(organe, pos, accentColor, 0);
        });
    } catch (e) {
        console.error('[16A] LLM infer failed:', e);
    }
});
```

### Contraintes

- `_renderCorps` devient `async` → tous les appelants qui utilisent `await this._renderCorps(...)` doivent être vérifiés (notamment `_drillUp`)
- Ne pas supprimer l'import `LayoutEngine` (fallback)
- Ne pas modifier `_renderOrgane()` ni `_renderCellule()` (hors scope)
- `input_files` obligatoires : `stenciler.css`, `LEXICON_DESIGN.json`
- Ne rien modifier dans `Canvas.renderer.js`, `AtomRenderer.js`, `WireframeLibrary.js`

### Critères d'acceptation

- [ ] `_renderCorps()` est `async` et appelle `/api/infer_layout?mode=heuristic`
- [ ] Les organes se positionnent dans leurs zones sémantiques (nav en haut, sidebar à droite, etc.)
- [ ] Bouton `✨` visible dans la barre de zoom
- [ ] Click `✨` → re-layout via LLM → organes se repositionnent
- [ ] Fallback silencieux si serveur down (LayoutEngine.proposeLayout() reprend la main)
- [ ] FJD valide visuellement sur http://localhost:9998/stenciler (Cmd+Shift+R obligatoire)

---

## Mission 16B — Zone Layout Resolver : Placement sans collision [MISSION ACTIVE]

**ACTOR : GEMINI**
**DATE : 2026-03-01**
**STATUS : LIVRÉ — EN ATTENTE VALIDATION FJD**

### Bootstrap Gemini (obligatoire)
```
Tu travailles sur AetherFlow Stenciler V3. Lis avant de coder :
1. Frontend/3. STENCILER/static/js/features/Canvas.feature.js — focus _inferResultToPositions() L.191-220
2. Frontend/1. CONSTITUTION/LEXICON_DESIGN.json

input_files obligatoires : stenciler.css, LEXICON_DESIGN.json
```

### Contexte

`_inferResultToPositions()` (Mission 16A) place les organes zone par zone mais ignore les collisions :
- Plusieurs organes dans `sidebar_right` → superposés à x:980 avec seulement 130px de gap
- Zones `canvas` et `main` se chevauchent (même x:20/240, même y:70)
- Hauteur fixe à `130px` indépendante du contenu réel

L'objectif est de remplacer `_inferResultToPositions` par `_zoneTemplateToPositions` — un **layout resolver** inspiré des page templates Flowbite/shadcn qui élimine les collisions.

### Tâche unique — Remplacer `_inferResultToPositions` dans Canvas.feature.js

**Fichier cible :** `Frontend/3. STENCILER/static/js/features/Canvas.feature.js`

#### Constantes de layout (canvas SVG = 1200 × 900)

```javascript
// Zones fixes (priority order)
const ZONE_DEFS = {
    header:       { x: 0,    y: 0,   w: 1200, fixedH: 56  },
    footer:       { x: 0,    y: 840, w: 1200, fixedH: 48  },
    preview_band: { x: 0,    y: 720, w: 1200, fixedH: 120 },
    sidebar_left: { x: 0,    y: 56,  w: 240,  fixedH: null }, // h = fill
    sidebar_right:{ x: 960,  y: 56,  w: 240,  fixedH: null }, // h = fill
    main:         { x: null, y: 56,  w: null,  fixedH: null }, // x/w = computed
    canvas:       { x: null, y: 56,  w: null,  fixedH: null }, // x/w = computed
};
```

`main` et `canvas` sont des zones "élastiques" : leur x et w dépendent des sidebars présentes.

#### Algorithme `_zoneTemplateToPositions(result, sections)`

**Étape 1 — Grouper les organes par zone :**
```javascript
const byZone = {};
sections.forEach(s => {
    const zone = result[s.id]?.zone || 'main';
    if (!byZone[zone]) byZone[zone] = [];
    byZone[zone].push({ section: s, inf: result[s.id] || {} });
});
```

**Étape 2 — Calculer la hauteur d'un organe (contenu réel) :**
```javascript
const organH = (s, inf) => {
    if (inf.h === 'full') return 640;
    if (typeof inf.h === 'number' && inf.h > 0) return inf.h;
    return Math.max(72, 48 + (s.n2_features?.length || 0) * 24); // 48px base + 24px/N2
};
```

**Étape 3 — Calculer x/w des zones élastiques selon sidebars présentes :**
```javascript
const hasLeft  = !!(byZone.sidebar_left?.length);
const hasRight = !!(byZone.sidebar_right?.length);
const mainX = hasLeft  ? 248 : 8;
const mainW = 1200 - mainX - (hasRight ? 248 : 8);
// canvas occupe le même espace que main (mutuellement exclusifs en pratique)
```

**Étape 4 — Distribuer les organes dans chaque zone sans collision :**

Règles par zone :
- **`header`** : distribution horizontale (flex). Diviser `w:1200` en N parts égales, h = `fixedH: 56`. Si 1 seul organe → `w:1200`.
- **`footer`** : idem header, `fixedH:48`.
- **`preview_band`** : idem header, `fixedH:120`.
- **`sidebar_left` / `sidebar_right`** : stack vertical. Chaque organe à son `w` (240 max), `h = organH(s, inf)`. Y cumulatif depuis `y:56` avec `gap:8`.
- **`main`** : si ≤ 3 organes → stack vertical avec `gap:16`. Si > 3 → grille 2 colonnes, `colW = floor(mainW/2) - 8`, `gap:16`.
- **`canvas`** : 1 seul organe attendu → prend tout l'espace elastic (`x:mainX, y:56, w:mainW, h:640`).
- **`unknown`/autres** : stack dans `main`.

**Étape 5 — Retourner le tableau `positions[]` :**
Format identique à l'existant : `{ id, x, y, w, h, zone }`.

#### Code complet de la méthode

```javascript
_zoneTemplateToPositions(result, sections) {
    const GAP = 8;

    // Grouper par zone
    const byZone = {};
    sections.forEach(s => {
        const zone = result[s.id]?.zone || 'main';
        (byZone[zone] = byZone[zone] || []).push({ s, inf: result[s.id] || {} });
    });

    // Hauteur adaptative d'un organe
    const organH = (s, inf) => {
        if (inf.h === 'full') return 640;
        if (typeof inf.h === 'number' && inf.h > 0) return inf.h;
        return Math.max(72, 48 + (s.n2_features?.length || 0) * 24);
    };

    // Zones élastiques
    const hasLeft  = !!(byZone.sidebar_left?.length);
    const hasRight = !!(byZone.sidebar_right?.length);
    const mainX = hasLeft  ? 248 : 8;
    const mainW = 1200 - mainX - (hasRight ? 248 : 8);

    const positions = [];

    // --- HEADER (flex horizontal) ---
    (byZone.header || []).forEach((item, i, arr) => {
        const colW = Math.floor(1200 / arr.length);
        positions.push({ id: item.s.id, x: i * colW, y: 0, w: colW, h: 56, zone: 'header' });
    });

    // --- FOOTER (flex horizontal) ---
    (byZone.footer || []).forEach((item, i, arr) => {
        const colW = Math.floor(1200 / arr.length);
        positions.push({ id: item.s.id, x: i * colW, y: 840, w: colW, h: 48, zone: 'footer' });
    });

    // --- PREVIEW BAND (flex horizontal) ---
    (byZone.preview_band || []).forEach((item, i, arr) => {
        const colW = Math.floor(1200 / arr.length);
        positions.push({ id: item.s.id, x: i * colW, y: 720, w: colW, h: 120, zone: 'preview_band' });
    });

    // --- SIDEBAR LEFT (stack vertical) ---
    let sy = 56;
    (byZone.sidebar_left || []).forEach(item => {
        const h = organH(item.s, item.inf);
        positions.push({ id: item.s.id, x: 0, y: sy, w: 240, h, zone: 'sidebar_left' });
        sy += h + GAP;
    });

    // --- SIDEBAR RIGHT (stack vertical) ---
    sy = 56;
    (byZone.sidebar_right || []).forEach(item => {
        const h = organH(item.s, item.inf);
        positions.push({ id: item.s.id, x: 960, y: sy, w: 240, h, zone: 'sidebar_right' });
        sy += h + GAP;
    });

    // --- CANVAS (prend tout l'espace élastique) ---
    (byZone.canvas || []).forEach(item => {
        positions.push({ id: item.s.id, x: mainX, y: 56, w: mainW, h: 640, zone: 'canvas' });
    });

    // --- MAIN (stack vertical ou 2-col si > 3) ---
    const mainItems = [...(byZone.main || []), ...(byZone.unknown || [])];
    if (mainItems.length <= 3) {
        let my = 56;
        mainItems.forEach(item => {
            const h = organH(item.s, item.inf);
            const w = typeof item.inf.w === 'number' ? Math.min(item.inf.w, mainW) : mainW;
            positions.push({ id: item.s.id, x: mainX, y: my, w, h, zone: 'main' });
            my += h + 16;
        });
    } else {
        const colW = Math.floor(mainW / 2) - GAP;
        let col0y = 56, col1y = 56;
        mainItems.forEach((item, i) => {
            const col = i % 2;
            const h = organH(item.s, item.inf);
            const x = col === 0 ? mainX : mainX + colW + GAP * 2;
            const y = col === 0 ? col0y : col1y;
            positions.push({ id: item.s.id, x, y, w: colW, h, zone: 'main' });
            if (col === 0) col0y += h + 16;
            else col1y += h + 16;
        });
    }

    return positions;
}
```

**Remplacer aussi les 2 appels à `_inferResultToPositions` par `_zoneTemplateToPositions` :**
- L.167 : `positions = this._inferResultToPositions(result, phaseData.n1_sections);`
- L.1169 : `const positions = this._inferResultToPositions(result, phaseData.n1_sections);`

**Supprimer** l'ancienne méthode `_inferResultToPositions` (L.191-220).

**Mettre à jour le viewBox** en fin de `_zoneTemplateToPositions` : le canvas est toujours `1200 × 900`. Pas de changement à faire, le viewBox est déjà `0 0 1200 900` dans `_renderCorps`.

### Contraintes

- Ne toucher que `Canvas.feature.js`
- Ne pas modifier `_renderOrgane()`, `_renderCellule()`, `Canvas.renderer.js`, `AtomRenderer.js`
- Ne pas modifier l'import `LayoutEngine` (fallback toujours actif)
- `input_files` obligatoires : `stenciler.css`, `LEXICON_DESIGN.json`

### Critères d'acceptation

- [ ] Plus aucun organe superposé sur le canvas N0 (Corps view)
- [ ] Navigation/toolbar → bande horizontale haute
- [ ] Sidebars → colonne droite ou gauche sans overflow
- [ ] Main/editor/dashboard → zone centrale, stack ou grille selon count
- [ ] Footer/deploy → bande basse
- [ ] Bouton `✨` re-layout LLM fonctionne toujours
- [ ] Fallback LayoutEngine toujours actif si fetch échoue
- [ ] FJD valide visuellement sur http://localhost:9998/stenciler (Cmd+Shift+R obligatoire)

---

## Mission 17A — Real Wireframes at N0 : Organes en Composants Reconnaissables [MISSION ACTIVE]

**ACTOR: GEMINI | MODE: CODE DIRECT — FJD | DATE: 2026-03-01 | STATUS: LIVRÉ — EN ATTENTE VALIDATION FJD**

---

### Contexte

Au niveau N0 (vue Corps → organes visibles), les organes s'affichent comme des compositions bottom-up récursives abstraites — sans aucun sens visuel reconnaissable.
La librairie `WireframeLibrary.js` contient déjà 20+ composants UI vectoriels (navbar, chat, dashboard, form, modal, accordion…).
Le `SemanticMatcher.js` sait déjà mapper des keywords vers ces wireframes (mais uniquement pour les atomes N3).

**Objectif :** Au niveau N0, chaque organe doit afficher un wireframe reconnaissable de `WireframeLibrary` à la place de la composition récursive.

---

### Fichiers à lire AVANT de coder (OBLIGATOIRE)

1. `static/js/Canvas.renderer.js` — entier. Focus sur `renderNode()` (L.187-239) et `_matchHint()` (L.38-40).
2. `static/js/WireframeLibrary.js` — entier. Connaître tous les hints disponibles et le return format (string).
3. `static/js/SemanticMatcher.js` — entier. Comprendre `resolveHint()` et `_keywordFallback()`.

---

### Tâche 1 — `SemanticMatcher.js` : Étendre `_keywordFallback` pour les N1 organs

Dans la fonction `_keywordFallback(data)`, dans l'objet `keywords`, **fusionner** les entrées suivantes avec celles déjà présentes :

```javascript
// Fusionner dans l'objet keywords (ne pas supprimer les entrées existantes) :
'preview'      : [...existants, 'analys', 'analysis', 'png', 'image', 'inspect', 'render', 'viewer'],
'stencil-card' : [...existants, 'intent', 'refactor', 'ir', 'tile', 'item'],
'breadcrumb'   : [...existants, 'nav', 'navbar', 'menu', 'header', 'toolbar'],
'chat-input'   : [...existants, 'message', 'conversation', 'prompt'],
'form'         : [...existants, 'login', 'signup', 'register', 'auth', 'password', 'credential'],
```

⚠️ Ne pas supprimer les entrées existantes. Fusionner avec celles déjà présentes.

**Vérification Tâche 1 :**
- `resolveHint({ id: 'n1_analysis', name: 'Analyse PNG' })` → doit retourner `'preview'`
- `resolveHint({ id: 'n1_ir', name: 'Intent Refactoring' })` → doit retourner `'stencil-card'`

---

### Tâche 2 — `Canvas.renderer.js` : Wireframe au niveau N0

Dans `renderNode(data, pos, color, level = 0)`, **insérer le bloc suivant AVANT** la ligne `const res = this._buildComposition(data, pos.w, color);` :

```javascript
// Mission 17A — N0 Organic Wireframe Rendering
if (level === 0) {
    const organHint = this._matchHint(data);
    if (organHint) {
        const wfSvg = WireframeLibrary.getSVG(organHint, color, pos.w, pos.h, data.name);
        if (wfSvg) {
            compGroup.innerHTML = wfSvg;
            g.append(compGroup);
            return g;
        }
    }
}
```

Ce bloc :
1. N'est exécuté que pour `level === 0` (organes N1 au niveau corps — pas les cells N1 ni les atomes N2)
2. Essaie `_matchHint(data)` sur l'organe (id + name du N1 via SemanticMatcher)
3. Si hint trouvé : `WireframeLibrary.getSVG` génère le SVG **à la bonne taille** (`pos.w × pos.h`)
4. Retourne immédiatement avec wireframe, skip `_buildComposition()`
5. Si pas de hint (ou wfSvg null) : tombe dans le comportement existant → **zéro régression**

**Contrainte critique :** `WireframeLibrary.getSVG()` retourne une **string SVG** (pas un objet `{svg, h, w}`). L'utiliser directement comme `compGroup.innerHTML = wfSvg` — **pas** `wfSvg.svg`.

**Ne pas modifier `pos.h`** dans le bloc 17A — la hauteur vient de `_zoneTemplateToPositions()` et est déjà correcte par zone.

---

### Critères d'acceptation

- [ ] `n1_navigation` (Navigation) → wireframe `breadcrumb` visible au N0
- [ ] `n1_dialogue` (Dialogue Utilisateur) → wireframe `chat-input` visible au N0
- [ ] `n1_session` (Session Management) → wireframe `dashboard` visible au N0
- [ ] `n1_upload` (Upload Design) → wireframe `upload` visible au N0
- [ ] `n1_validation` (Validation Composants) → wireframe `accordion` visible au N0
- [ ] `n1_export` (Export / Téléchargement) → wireframe `action-button` visible au N0
- [ ] `n1_layout` (Layout Selection) → wireframe `grid` visible au N0
- [ ] `n1_ir` (Intent Refactoring) → wireframe `stencil-card` visible au N0
- [ ] `n1_analysis` (Analyse PNG) → wireframe `preview` visible au N0
- [ ] Drill dans un organe → N1/N2/N3 non affectés (comportement inchangé)
- [ ] Organe sans match → bottom-up composition (régression zéro)
- [ ] Cmd+Shift+R → http://localhost:9998/stenciler

---

## Archives
*(Voir [ROADMAP_ACHIEVED.md](file:///Users/francois-jeandazin/AETHERFLOW/Frontend/4. COMMUNICATION/ROADMAP_ACHIEVED.md) pour Phases 1 à 9D)*
