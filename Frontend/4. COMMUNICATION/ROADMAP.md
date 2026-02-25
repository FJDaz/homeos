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
- [ ] DblClick atom → éditer une primitive (couleur, position) → clic extérieur pour sortir
- [ ] Canvas re-render depuis N0 : les organes du corps courant réapparaissent
- [ ] Re-drill vers l'atome modifié : la modification est visible (PrimOverlay servi)
- [ ] Deuxième sortie de mode illustrateur sur le même atome : modification précédente préservée
- [ ] Hard refresh → overlay perdu (attendu, RAM seulement)
- [ ] Zéro régression drill N1→N2→N3
- [ ] FJD valide visuellement sur http://localhost:9998/stenciler

---

### Mission 14C — Copie/Duplication Atomes (EN ATTENTE)
**STATUS: EN ATTENTE (après 14A) | ACTOR: GEMINI**

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
| 14B | Write-back Génome | Claude + Gemini | ⏳ EN ATTENTE |
| 14C | Copie/Duplication | Gemini | ⏳ EN ATTENTE |
| 14D | Valise (Sullivan Embedded) | Gemini | ⏳ EN ATTENTE |
| 14E-WF | Nouveaux Wireframes (sandbox) | KIMI → Gemini | ⏳ EN ATTENTE |

---

## Archives
*(Voir [ROADMAP_ACHIEVED.md](file:///Users/francois-jeandazin/AETHERFLOW/Frontend/4. COMMUNICATION/ROADMAP_ACHIEVED.md) pour Phases 1 à 9D)*
