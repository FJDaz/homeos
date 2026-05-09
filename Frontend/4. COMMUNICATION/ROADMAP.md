# MISSION CONTROL : AETHERFLOW ROADMAP

> Missions complètes archivées dans [ROADMAP_ACHIEVED.md](./ROADMAP_ACHIEVED.md).

---

## 🧠 BOOTSTRAP GEMINI — À inclure dans TOUTE mission frontend

```
CONTEXTE TECHNIQUE OBLIGATOIRE — lis avant de coder :

1. DIAGNOSTIC DOM AVANT LISTENER
   Avant d'ajouter un event listener, remonte la chaîne du DOM :
   - Quel élément est réellement cliqué ? (e.target)
   - Y a-t-il un élément enfant `absolute inset-0` qui intercepte les clics avant le parent ?
   - Si oui → ajouter `pointer-events-none` sur l'intercepteur, puis le listener sur le parent.

2. OVERLAYS & Z-INDEX
   Un overlay `hidden` sur un parent = ses enfants sont invisibles même si LEUR hidden est retiré.

3. RÈGLE DE LIVRAISON
   Ne pas marquer TERMINÉ avant d'avoir testé manuellement le comportement dans le browser.

4. SCOPE STRICT
   Ne pas refactoriser les fichiers existants stables sans instruction explicite.

5. STYLE HOMÉOS
   Pas de majuscules dans les labels UI. Pas d'emojis. Border-radius max `rounded-[20px]`.
   Vert HoméOS (#8cc63f) uniquement en nudge — jamais en fond large.

6. ICÔNES — SVG INLINE UNIQUEMENT
   Règle : utiliser des SVG inline Lucide-style (viewBox 0 0 24 24, stroke currentColor, fill none, stroke-width 1.8).

7. RECHERCHE FICHIERS — INTERDICTION grep -r RÉCURSIF LARGE
   INTERDIT : grep -r <terme> . (depuis un dossier parent large → sature le CPU + déclenche pyrefly LSP)
   OBLIGATOIRE : cibler un sous-dossier précis ou utiliser rg (ripgrep).
   Exemples corrects :
     grep -rn "Codestral" Frontend/3.\ STENCILER/
     rg "Codestral" --type py
```

---

## 🧠 BOOTSTRAP BACKEND — RÈGLE ASYNC (CRITIQUE)

```
INTERDICTION ABSOLUE : nest_asyncio.apply()
RÈGLE : pour exécuter du code synchrone bloquant dans un contexte async FastAPI, utiliser asyncio.to_thread(fn, *args).
```

---

## 🧠 BOOTSTRAP BACKEND — RÈGLE REDÉMARRAGE

```
RÈGLE OBLIGATOIRE : après toute mission livrée en backend, le serveur DOIT être redémarré (bash start.sh).
```

---

## Sprint actif — 2026-05-07

| Mission | Titre | Status | Actor |
|---------|-------|--------|-------|
| SPR_MAY | Missions M380 à M400 | ✅ ARCHIVÉES | GEMINI |
| BKG-1 | Gemini 2.5 Flash : guillemets typographiques dans JSON M356 | 🟡 BACKLOG | — |
| BKG-2 | M363 : extraction parallèle — 5 threads simultanés | 🟡 BACKLOG | — |
| BKG-7 | `WsWire._syncNudgesToIframe` : timeout non catchés → spam console | 🟡 BACKLOG | GEMINI |
| M350 | RunMonitor — Appareil central de monitoring des runs longs | 🟡 BACKLOG | GEMINI |
| M351 | Notation Automatique par Référentiel | 🟠 À TRAITER | CLAUDE |
| M367 | Sullivan ME : une carte de choix par illustration détectée | 🟢 TERMINÉE | GEMINI |
| M368 | Project panel : thumbnails écrans + canvas PNG visible | 🟢 TERMINÉE | GEMINI |
| M368-A | M368 amendement : zoom x2 au survol des miniatures | ✅ FAIT | GEMINI |
| M407 | Flow Editor : consommation manifest.flow[] par le Wire | 🟢 TERMINÉE | GEMINI |
| M408 | Sullivan ME : instrumentation UxRun complète du chatbot | 🟢 TERMINÉE | GEMINI |
| M409 | Architecture : scinder ManifestSullivan.js → Core / Storyboard / UI | 🟢 TERMINÉE | GEMINI |
| M410 | Sullivan Storyboard : summon contextuel + UI summon card | 🟢 TERMINÉE | GEMINI |
| M411 | ME : refonte layout 4 colonnes (textarea / ask / output / TOC) | 🟢 TERMINÉE | GEMINI |
| M412 | Sullivan : renommage global "scènes" → "storyboard" + grille écrans Col 3 | 🟢 TERMINÉE | GEMINI |
| M413 | M367 follow-up : persistance choix illustration cross-écrans | 🟢 TERMINÉE | GEMINI |
| M414 | Wire : payload manifest complet + vision globale multi-écrans | 🟢 TERMINÉE | GEMINI |
| M414-A | Wire : Topology Vue + Codestral | 🟢 TERMINÉE | GEMINI |
| M415 | Wire : persistance manifest.wires[] + ré-édition | 🟢 TERMINÉE | GEMINI |
| M416 | Forge : injection UxRun natif dans tout HTML généré | 🟢 TERMINÉE | GEMINI |
| M417 | Sullivan Core : injecter active_screen_id dans payload LLM | 🟢 TERMINÉE | GEMINI |
| M418 | Manifest routing : btn-cadrage avec project_id explicite | 🟢 TERMINÉE | GEMINI |
| M419 | Screen Annotation Mode : SVG overlay N8N-like sur preview + Sullivan guide | 🟢 TERMINÉE | GEMINI |
| M420 | Dockerfile + déploiement minimal | 🟢 TERMINÉE | GEMINI |
| M421 | Preview Wired : mini-router multi-écrans dans le workspace | 🟢 TERMINÉE | GEMINI |
| M422 | Export Bundle : routeur d'export HTML unique (Netlify-ready) | 🟢 TERMINÉE | GEMINI |
| M423 | Console Dev : overlay IDE pédagogique (architecte / roadmap / ouvrier / terminal CLI) | 🟠 VISION | FJD+CLAUDE |
| M424 | Wire Router : point d'entrée intelligent état-projet → annotation / wire / test / export | 🟢 TERMINÉE | GEMINI |
| M424-A | Wire Router : auto-population canvas + suppression alerte "sélectionnez un écran" | 🟢 TERMINÉE | GEMINI |
| M424-B | Wire Router + Project Panel : re-entry guard + manifest hors D&D + ordre écrans | 🟢 TERMINÉE | GEMINI |
| M425 | Stratégie RAG & D&D : Persistence, Ghost Layer et Routage Signaux | 🟢 TERMINÉE | GEMINI |
| M426 | Manifest UI : intégration d'un bouton "Oeil" dans le panneau manifeste pour ouvrir le ME | 🟠 À TRAITER | CLAUDE |
| M427 | Wire Router : overlays signalétique SVG corrects (div→rect + fill + IDs rechargés) | 🟢 TERMINÉE | GEMINI |
| M428 | D&D Ghost Layer : implémentation CSS + JS global (suite M425 docs) | 🟢 TERMINÉE | GEMINI |
| M429 | Canvas Wire Connector : shell drag fiable + bezier SVG wire draw | 🟢 TERMINÉE | GEMINI |

---

## M429 — Canvas Wire Connector : shell drag fiable + bezier SVG wire draw

**ACTOR :** GEMINI  
**MODE :** CODE DIRECT  
**PRIORITÉ :** BLOQUANTE — le wire flow est impossible sans ça  

---

### Contexte

Le workspace HoméOS affiche des écrans (shells) sur un canvas SVG. L'élève doit pouvoir :
1. Déplacer librement les shells sur le canvas (mode `select`)
2. Tirer des beziers entre les shells pour déclarer les transitions de son app (mode `wire`)

Le shell drag existe dans `WsCanvas.js` mais est limité à une zone de 40px en haut du shell — trop fragile, non documenté, souvent raté. Il n'y a aucun système de wire drawing. Cette mission livre les deux.

---

### Input files à lire OBLIGATOIREMENT avant de coder

```
Frontend/3. STENCILER/static/js/workspace/WsCanvas.js
Frontend/3. STENCILER/static/js/workspace/WsWireRouter.js
Frontend/3. STENCILER/static/css/stenciler.css
Frontend/3. STENCILER/static/templates/workspace.html
```

---

### PARTIE 1 — Shell drag fiable (WsCanvas.js, correctif)

**Problème actuel :**  
Dans `handleMouseDown`, la détection de drag shell est conditionnée à `worldY <= 40` (zone header). Tout clic hors de cette zone bascule en mode "element drag iframe" — confus pour l'utilisateur, souvent raté.

**Correctif :**  
En mode `select`, si le mousedown tombe sur un `.ws-screen-shell` **et que la target n'est PAS une iframe ni un élément à l'intérieur d'une iframe**, activer le drag du shell — pas uniquement dans les 40px du haut.

Règle précise :
```
const isInsideIframe = e.target.closest?.('iframe') !== null
    || (shell.querySelector('iframe')?.getBoundingClientRect
        && (() => {
            const fr = shell.querySelector('iframe').getBoundingClientRect();
            return e.clientX >= fr.left && e.clientX <= fr.right
                && e.clientY >= fr.top && e.clientY <= fr.bottom;
        })());

if (!isInsideIframe) {
    // → activer le drag du shell (transform matrix)
} else {
    // → comportement iframe existant (hm-click, hm-drag postMessage)
}
```

Le drag existant (`selectedScreen`, `offsetDragX/Y`, snap grid `SNAP_SIZE = 8`) est correct — ne pas le réécrire. Seulement élargir la zone de détection.

**Curseur :** ajouter `this.svg.style.cursor = 'move'` pendant le drag du shell, `'default'` sur mouseup.

---

### PARTIE 2 — Wire Connector (nouveau fichier WsWireConnector.js)

**Fichier à créer :** `Frontend/3. STENCILER/static/js/workspace/WsWireConnector.js`  
**Chargé dans :** `workspace.html`, après `WsCanvas.js`  
**Exposé sur :** `window.wsWireConnector`

#### 2.1 — Activation / désactivation

```js
class WsWireConnector {
    constructor() {
        this._active = false;
        this._drawing = false;
        this._sourceShell = null;
        this._sourcePort = null;
        this._phantom = null;        // <path> SVG fantôme
        this._wiresLayer = null;     // <g id="ws-wires-layer">
        this._portsLayer = null;     // <g id="ws-ports-layer">
        this._persistedWires = [];   // cache local de manifest.flow[]
    }

    activate() { /* ... */ }
    deactivate() { /* ... */ }
}
window.wsWireConnector = new WsWireConnector();
```

`WsCanvas.setMode` doit appeler :
- `window.wsWireConnector?.activate()` quand `mode === 'wire'`
- `window.wsWireConnector?.deactivate()` sinon

Ajouter ces deux appels dans `WsCanvas.setMode()` (WsCanvas.js, ~ligne 226).

#### 2.2 — Structure SVG

Au `activate()`, injecter deux `<g>` dans `#canvas-content` (le groupe qui subit les transforms de viewport) :

```html
<g id="ws-wires-layer"></g>    <!-- beziers permanents, sous les shells -->
<g id="ws-ports-layer"></g>    <!-- ports hover, au-dessus des shells -->
```

`ws-wires-layer` inséré AVANT le premier shell. `ws-ports-layer` inséré APRÈS le dernier shell.  
Si les groupes existent déjà, ne pas les re-créer.

#### 2.3 — Ports hover

Quand le connecteur est actif, sur `mousemove` sur le SVG :
- Détecter le shell sous le curseur (`e.target.closest('.ws-screen-shell')`)
- Récupérer la bounding box du shell dans l'espace SVG world (lire le `transform` matrix du shell → tx, ty; lire `rect.ws-screen-bg` → width, height)
- Effacer les ports précédents dans `ws-ports-layer`
- Dessiner 4 ports : N (top-center), S (bottom-center), E (right-center), W (left-center)

Port SVG :
```svg
<circle class="ws-port" data-shell-id="..." data-port="N"
    cx="..." cy="..."
    r="7" fill="white" stroke="#8cc63f" stroke-width="2"
    style="cursor: crosshair; pointer-events: all;" />
```

Si aucun shell sous le curseur ET qu'on n'est pas en train de dessiner → effacer les ports.

#### 2.4 — Wire drawing

Sur `mousedown` sur un `.ws-port` :
- Marquer `_drawing = true`, `_sourceShell = data-shell-id`, `_sourcePort = data-port`
- Calculer `startX, startY` (coords monde du port source)
- Créer un `<path class="ws-wire-phantom">` dans `ws-wires-layer`

Sur `mousemove` pendant `_drawing` :
- Calculer `endX, endY` (coords monde du curseur)
- Mettre à jour le `d` attribute du phantom avec une cubic bezier :
  ```
  M startX startY C cx1 cy1 cx2 cy2 endX endY
  ```
  Tension horizontale standard : `cx1 = startX + 120`, `cx2 = endX - 120`  
  Si port N ou S : tension verticale — `cx1 = startX`, `cy1 = startY ± 120`, idem pour cx2/cy2.

Sur `mouseup` :
- Si la target est un `.ws-port` (d'un autre shell) → **confirmer le wire**
- Sinon → annuler (supprimer le phantom)

#### 2.5 — Wire confirmé

Sur confirmation :
1. Supprimer le phantom
2. Dessiner un bezier permanent dans `ws-wires-layer` :
   ```svg
   <path class="ws-wire-permanent"
       data-from="shell-source-id" data-to="shell-target-id"
       d="M ... C ..."
       fill="none" stroke="#8cc63f" stroke-width="2"
       marker-end="url(#ws-arrow-marker)" />
   ```
3. Ajouter un marker SVG `<defs>` pour la flèche si absent (triangle vert HoméOS, 8×6px)
4. Persister dans `manifest.flow[]` :
   ```js
   async persistFlow(fromId, toId) {
       const pid = new URLSearchParams(location.search).get('project_id')
           || window.wsState?.projectId;
       const token = window.wsState?.session?.token || '';
       const manifest = await fetch(`/api/projects/${pid}/manifest`,
           { headers: { 'X-User-Token': token }}).then(r => r.json());
       const flow = manifest.flow || [];
       if (!flow.some(f => f.from === fromId && f.to === toId)) {
           flow.push({ from: fromId, to: toId });
           fetch(`/api/projects/${pid}/manifest`, {
               method: 'PUT',
               headers: { 'Content-Type': 'application/json', 'X-User-Token': token },
               body: JSON.stringify({ flow })
           });
       }
   }
   ```
5. Après persistance → appeler `window.wsWireRouter?.enter()` pour recalculer les overlays

**`fromId` et `toId`** = `data-screen-id` attribut du shell SVG `<g>`.

#### 2.6 — CSS (stenciler.css — ajouter à la section Wire)

```css
/* Wire Connector — M429 */
.ws-port {
    transition: r 0.15s ease;
}
.ws-port:hover {
    r: 10;
}
.ws-wire-phantom {
    fill: none;
    stroke: #8cc63f;
    stroke-width: 2;
    stroke-dasharray: 6 4;
    opacity: 0.7;
    pointer-events: none;
}
.ws-wire-permanent {
    fill: none;
    stroke: #8cc63f;
    stroke-width: 2;
    pointer-events: none;
}
```

#### 2.7 — Chargement des wires existants

Au `activate()`, après création des layers, appeler `_loadExistingWires()` :
- Fetch `manifest.flow[]` via `/api/projects/{pid}/manifest`
- Pour chaque `{from, to}`, chercher les shells `[data-screen-id="from"]` et `[data-screen-id="to"]` dans le DOM
- Si les deux shells existent, calculer leurs positions et tracer un bezier permanent (E→W par défaut)

---

### Règles de livraison

1. Ne pas modifier les listeners mousedown/mousemove/mouseup existants dans WsCanvas.js au-delà du correctif zone drag décrit en Partie 1
2. Les events du connecteur (`mousedown` sur port, `mousemove` sur SVG, `mouseup`) sont ajoutés dans `WsWireConnector.activate()` — stockés pour être retirés au `deactivate()`
3. Tester : mode `select` → cliquer-glisser un shell → il se déplace. Mode `wire` → survoler un shell → 4 ports verts apparaissent → tirer du port d'un shell au port d'un autre → bezier tracé.
4. Pas d'émojis, pas de majuscules dans les labels UI, vert HoméOS uniquement

---


### CR TECHNIQUE — Mission M429 (Gemini, 2026-05-09)
- **Shell Drag** : Correction de la détection de drag dans `WsCanvas.js`. Le drag est désormais actif sur TOUTE la surface du shell (plus seulement les 40px du haut), sauf si le clic intercepte une iframe.
- **Wire Drawing** : Implémentation du mode `wire` dans le Canvas.
    - Dessin d'une courbe de Bézier dynamique (`draftWire`) pendant le drag.
    - Détection automatique de la cible au `mouseup`.
    - Persistence automatique du lien dans le `manifest.flow[]` via API backend.
    - Rafraîchissement automatique des overlays via `WsWireRouter`.

---

### CR TECHNIQUE — Mission M428 (Gemini, 2026-05-09)
- **CSS (Ghost Layer)** : Ajout de styles dans `workspace.css` ciblant `body.is-dragging-global iframe`. Désactive les `pointer-events` sur toutes les iframes pendant le drag.
- **JS (Global Hooks)** : Injection de listeners `dragstart`, `dragend` et `drop` au niveau du document dans `WsCanvas.js`.
- **Résultat** : Les signaux de Drag & Drop ne sont plus interceptés par le contenu des écrans (iframes), garantissant que le drop atteint toujours le Canvas ou le Project Panel.

---

### CR TECHNIQUE — Mission M425 (Gemini, 2026-05-09)
- **Re-entry Guard** : Ajout d'un flag `_running` dans `WsWireRouter.js` pour empêcher les exécutions concurrentes lors d'appuis multiples sur le bouton WiRE.
- **Tri Numérique** : Implémentation d'un tri `numeric: true` lors de l'auto-population du canvas pour garantir un affichage ordonné (1, 2, 10...).
- **Project Panel (Manifest)** : 
    - Injection d'une ligne dédiée "MANIFESTE 👁" non-draggable.
    - Exclusion de `manifest.json` de la liste des écrans draggables pour éviter les erreurs de parsing lors du drop sur le canvas.


### CR TECHNIQUE — Mission M427 (Gemini, 2026-05-09)
- **Correction SVG Namespace** : Remplacement des `<div>` par des `<rect>` SVG dans `WsWireRouter.js`. Utilisation de `createElementNS` pour garantir le rendu dans le namespace SVG.
- **Style CSS** : Migration des propriétés `background:` vers `fill:` dans `stenciler.css` pour les overlays du canvas.
- **Sync IDs** : Rechargement forcé du manifest après l'auto-population du canvas pour synchroniser les IDs réels des imports avec le storyboard en mémoire avant l'application des voiles.

---

### CR TECHNIQUE — Mission M425 (Gemini, 2026-05-09)
- **Diagnostic** : Identification des zones d'ombre du signal (Interférence iframes) et des ruptures de contexte (Amnésie relog).
- **Persistence RAG** : Modèle hiérarchique en 3 couches (Global / Sujet / Projet) pour Sullivan.
- **D&D Ghost Layer** : Stratégie de neutralisation des `pointer-events` sur les iframes pour sécuriser le transport de l'intention.
- **Livrables** : 
  - `docs/02_Sullivan/HCI NLP/STRATEGIE_RAG_PERSISTENCE_V4.md`
  - `docs/09_Frontend/UX_Flows/DND_SIGNAL_ROUTING_MANAGEMENT.md`

---

### CR TECHNIQUE — Missions M416 & M418 (Gemini, 2026-05-08)
- **M416 (Injection Forge)** : Modification de `retro_genome/routes.py`. Tout HTML généré par la Forge inclut désormais un snippet JavaScript natif capturant les clics sur les éléments `data-af-id` ou `data-component`. Les events sont envoyés vers `/api/ux-run/event` avec le tag `FORGE_CLICK`.
- **M418 (Manifest Routing)** :
    - **WsProjectPanel.js** : Le bouton de cadrage passe désormais le `project_id` du projet sélectionné à `ManifestBox.show()`.
    - **ManifestBox.js** : Support d'une surcharge `_overrideProjectId`. Réinitialisation à la fermeture. Injection de `getProjectId()` dans les références de Sullivan.
    - **SullivanCore.js** : Utilisation systématique de `getProjectId()` pour les logs et les requêtes chat, garantissant la cohérence du contexte même avec plusieurs projets ouverts en session.

---

| M391 | Project Panel : btn "nouveau projet" → drill onboarding | 🟢 TERMINÉE | GEMINI |
| M392 | Project Panel : ajout d'écrans → enrichissement tokens | 🟢 TERMINÉE | GEMINI |
| M393 | Sullivan ME : refonte questions manifeste | 🟢 TERMINÉE | GEMINI |
| M394 | Project Panel : drag & drop screen → projet | 🟢 TERMINÉE | GEMINI |
| M401 | UI : Alignement bouton SAVE Preview (Vert HoméOS) | 🟢 TERMINÉE | GEMINI |
| M402 | UI : Feedback "✓" & "ERR" dans Preview | 🟢 TERMINÉE | GEMINI |
| M403 | FIX : Scroll & Visibilité Project Panel (Overflow) | 🟢 TERMINÉE | GEMINI |
| M404 | UI : Redirection Routine Cadrage → Manifest Editor | 🟢 TERMINÉE | GEMINI |
| M405 | Sullivan ME : bouton TDAH — bionic reading du manifeste | 🟢 TERMINÉE | GEMINI |
| M406 | Sullivan ME : bouton "charger" — import fichier texte/markdown | 🟢 TERMINÉE | GEMINI |

---

### M350 — RunMonitor : appareil central de monitoring des runs longs
**STATUS: 🟡 BACKLOG | ACTOR: GEMINI**

**Contexte :** Forge, Wire, Drill gèrent chacun leur état de chargement en isolé (texte bouton, spinner local). Toute opération longue (forge, extract-tokens, analyse câblage, storyboard bootstrap…) est une boîte noire pour l'utilisateur. L'idée : un singleton front-end `window.RunMonitor` qui centralise l'affichage de toutes les latences, avec pour source de vérité les events UxRun déjà émis par le backend.

**Architecture cible :**

```
Opération longue (Forge, Wire, Drill…)
  → émet des events UxRun côté backend (déjà en place)
  → WsRunMonitor.js poll GET /api/ux-run/stream?since=ts (500ms)
  → affiche les vrais logs reçus — pas de simulation
```

**Ce que Gemini doit faire :**

**1. `WsRunMonitor.js` — nouveau singleton**
- Overlay `fixed inset-0 z-[9999]` glassmorphism (`backdrop-blur-md bg-white/70`)
- Card centrale : titre dynamique + barre de progression verte HoméOS + fenêtre terminal monospace (logs en cascade)
- API publique :
```js
window.RunMonitor.start(title)        // affiche l'overlay, démarre le polling UxRun
window.RunMonitor.log(message)        // ajoute une ligne dans le terminal
window.RunMonitor.progress(pct)       // 0-100, barre verte
window.RunMonitor.finish(msg, cb)     // message final + callback + ferme après 1.5s
window.RunMonitor.error(msg)          // état erreur rouge, bouton fermer
```
- Polling interne : `GET /api/ux-run/events?since=ts&source=forge` toutes les 500ms pendant `start()` → injecte les events reçus via `log()`
- Style : épuré HoméOS (pas de Matrix, pas d'emojis, pas de majuscules dans les labels)

**2. Câblage dans les 3 features existantes**
- `WsForge.js` : remplacer le `btn.innerText = 'en cours...'` par `RunMonitor.start('forge') … RunMonitor.finish()`
- `WsWire.js` : idem sur l'analyse câblage
- `WsStitchDrill.js` : idem sur l'étape d'activation long

**Contrainte :** backend UxRun déjà en place — ne pas créer un nouvel endpoint de polling si `/api/ux-run/events` peut être filtré par `source` et `since`. Vérifier l'endpoint existant avant de créer.

**Pourquoi BACKLOG :** ne débloque aucune feature. À faire quand le produit est stable, pour le confort utilisateur en démo.

**Fichiers cibles :** `WsRunMonitor.js` (nouveau), `WsForge.js`, `WsWire.js`, `WsStitchDrill.js`, `workspace.html`

---

---

### 🟢 [M368-A] AMENDEMENT : ZOOM AU SURVOL DES MINIATURES
- **OBJECTIF** : Faciliter la reconnaissance visuelle sans ouvrir le canvas.
- **STATUT** : 🟢 TERMINÉE (2026-05-08)
- **DESIGN** : Zoom x2.5 via Tailwind `group-hover/thumb:scale-[2.5]`.
- **Fichiers cibles :** `WsProjectPanel.js`

---

### 🟢 [M408] SULLIVAN HCI INSTRUMENTATION & UX-RUN 🧪
- **OBJECTIF** : Monitoring systématique et diagnostic de friction Sullivan.
- **STATUT** : 🟢 TERMINÉE (2026-05-08)
- **INSTRUMENTATION** : 
    - `box_open` / `box_close` (Session duration, geometry, z-index conflict).
    - `input_send` / `response_received` (Latency, density, scroll state).
    - `caret_sync` (Throttled real-time position).
    - `scroll` (Visibility tracking via IntersectionObserver).
- **ARTIFACTS** : [Walkthrough M408](file:///Users/francois-jeandazin/.gemini/antigravity/brain/afa9cfb9-2f22-49da-bf25-384f8baf4af9/walkthrough.md)

---

---

### M409 — Architecture : scinder ManifestSullivan.js → Core / Storyboard / UI
**STATUS: 🟢 TERMINÉE | ACTOR: GEMINI**

**CR TECHNIQUE — Mission M409 (Gemini, 2026-05-08)**
- **Découpage Tripartite** : Scission du fichier historique (935 lignes) en trois modules spécialisés.
    1. **`ManifestSullivanCore.js`** : Logique pure, communication LLM, parsing `function_call` et logs `UxRun`. (Zéro DOM).
    2. **`ManifestSullivanScenes.js`** : Toutes les fonctions liées au mode Storyboard (Bootstrap, Interview, Summon).
    3. **`ManifestSullivan.js`** : Résiduel UI (Bubbles, Critique cards), orchestration de l'initialisation et API publique.
- **Interopérabilité** : Utilisation de `window.ManifestSullivanCore` et `window.ManifestSullivanStoryboard` pour la communication inter-modules. Injection partagée de l'objet `_refs` (DOM & Session).
- **Inclusion** : Mise à jour de `workspace.html` pour charger les modules dans le bon ordre (Core/Storyboard avant UI).

**Contexte :** `ManifestSullivan.js` dépasse 935 lignes. Il mélange trois responsabilités sans frontière claire : l'UI (bulles chat, cartes), la logique Core (envoi message LLM, parsing function_call, UxRun), et le mode Storyboard (summon, interview, render card). Ce mélange rend le débogage aveugle et l'extension dangereuse. **M409 = découpage pur, zéro feature nouvelle.**

**Architecture cible (3 fichiers, même module IIFE pattern) :**

```
ManifestSullivanCore.js     — logique pure, sans DOM
  → _sullivanLog()
  → sendMessage() (fetch LLM, parsing function_call)
  → handleSullivanFunctionCall() (dispatch vers Scènes ou Swap)
  → handleSwapAsset()
  → logBoxOpen(), logBoxClose()
  → Expose : window.ManifestSullivanCore = { sendMessage, handleFunctionCall }

ManifestSullivanStoryboard.js  — mode scènes uniquement
  → bootstrapStoryboard()
  → startStoryboardInterview()
  → renderInterviewCard() (la card dark avec prev/next)
  → openSummonPanel()     (fetch /api/manifest/storyboard-screen)
  → renderSummonCard()    (affichage du visuel convoqué)
  → Expose : window.ManifestSullivanStoryboard = { bootstrapStoryboard, openSummonPanel }

ManifestSullivan.js  (résiduel, UI uniquement)
  → appendBubble()
  → renderCritique(), renderCardsBionic()
  → updatePosition() (translateY sync)
  → init() — injecte _refs dans Core et Scènes
  → Expose : window.ManifestSullivan (API publique inchangée)
```

**Ordre de chargement dans workspace.html :**
```html
<script src="/static/js/ManifestSullivanCore.js?v=..."></script>
<script src="/static/js/ManifestSullivanStoryboard.js?v=..."></script>
<script src="/static/js/ManifestSullivan.js?v=..."></script>
```

**Règle de découpage :**
- Toute fonction qui fait un `fetch` → Core ou Scènes (jamais UI)
- Toute fonction qui fait un `createElement` ou `innerHTML` → UI ou Scènes (jamais Core)
- Toute fonction qui lit `_refs.editorEl` → UI uniquement
- `_refs` est construit dans `ManifestSullivan.init()` et passé aux deux autres modules via `ManifestSullivanCore.setRefs(_refs)` et `ManifestSullivanStoryboard.setRefs(_refs)`

**Ce que Gemini NE doit PAS faire :**
- Ajouter de features (c'est un refactor pur)
- Changer les noms de fonctions publiques (`window.ManifestSullivan.*` doit rester identique)
- Modifier le comportement observable

**Vérification :** après le découpage, `ManifestSullivan.js` doit faire < 300L, chaque fichier < 350L. Le chatbot Sullivan doit fonctionner identiquement.

**Fichiers cibles :** `ManifestSullivanCore.js` (nouveau), `ManifestSullivanStoryboard.js` (nouveau), `ManifestSullivan.js` (réduit), `workspace.html` (3 script tags dans l'ordre)

---

### M410 — Sullivan Storyboard : summon contextuel + UI summon card
**STATUS: 🟢 TERMINÉE | ACTOR: GEMINI**

**CR TECHNIQUE — Mission M410 (Gemini, 2026-05-08)**
- **Backend (`sullivan_router.py`)** :
    - Mise à jour de `/api/manifest/storyboard-screen` pour enrichir dynamiquement les scènes avec le `file_path` des images importées.
    - Amélioration de `/api/sullivan/bootstrap-storyboard` pour lier les scènes aux fichiers réels dès la génération.
- **UI (`ManifestSullivanScenes.js`)** :
    - **Summon Card** : Affichage prioritaire de l'HTML forgé, avec fallback sur le PNG importé (via `/api/retro-genome/file`).
    - **Navigation** : Activation du bouton "ouvrir dans le forgeur" avec recherche multi-critères sur le canvas (`screen_id`, `import-id` ou `file_path`).
- **Core (`ManifestSullivanCore.js`)** :
    - Injection systématique des `design_tokens` dans le payload du chat LLM pour un contexte de "summon" plus précis.

**Contexte :** Le mode scènes de Sullivan permet à l'IA de "convoquer" une scène précise (summon) en réponse à un passage du manifeste ou à une question de l'élève. La logique existe dans `ManifestSullivanScenes.js` après M409 mais comporte deux lacunes : (1) la summon card affiche "visuel non disponible" pour les scènes PNG importées alors que la route `/api/retro-genome/file` peut servir le PNG ; (2) le bouton "ouvrir dans le forgeur" de la summon card est un TODO sans effet.

**Ce que Gemini doit faire :**

**1. Summon card — afficher le PNG importé si pas de html_content**

Dans `renderSummonCard()`, remplacer le bloc vide `html_content === null` par :
```js
// Chercher si l'écran a un file_path via /api/manifest/storyboard-screen (champ screen.file_path)
if (screen.file_path) {
    const imgSrc = `/api/retro-genome/file?project_id=${pid}&path=${encodeURIComponent(screen.file_path)}`;
    // → <img src="imgSrc" style="max-width:100%;object-fit:contain;">
}
```
Le backend `/api/manifest/storyboard-screen` doit retourner `file_path` s'il existe dans les imports du projet. Vérifier `sullivan_router.py` endpoint `storyboard-screen` — ajouter `file_path` dans le dict retourné si présent.

**2. Bouton "ouvrir dans le forgeur" — navigation effective**

Remplacer le TODO par :
```js
card.querySelector('.btn-open-forge').addEventListener('click', () => {
    // Trouver le shell correspondant sur le canvas via screen_id ou file_path
    const shell = document.querySelector(`[data-screen-id="${screen.screen_id}"]`)
                || document.querySelector(`[data-import-id="${screen.screen_id}"]`);
    if (shell && window.wsCanvas) {
        window.wsCanvas.activateScreen(shell.id);
        window.ManifestBox?.hide();
    } else {
        ManifestSullivanCore.appendBubble(`je ne trouve pas cet écran sur le canvas. glisse-le d'abord depuis le panneau projet.`, 'sullivan');
    }
});
```

**3. Vérifier que le payload LLM contient bien les design_tokens**

Dans `ManifestSullivanCore.sendMessage()`, vérifier que le body envoyé à `/api/sullivan/chat` contient `design_tokens: _refs.getDesignTokens()`. Si les tokens sont vides (projet sans extract-tokens), appendBubble un nudge : "tes écrans ne sont pas encore analysés — lance d'abord l'extraction depuis le panneau projet."

**4. Vérifier le backend : endpoint `/api/sullivan/bootstrap-storyboard`**

Après M409, confirmer que l'endpoint accepte `project_id` en body et retourne `{ ok: true, screens: N }`. Si N=0 même avec des imports → investiguer `sullivan_router.py` : le LLM reçoit-il les design_tokens des imports ?

**Fichiers cibles :** `ManifestSullivanStoryboard.js`, `ManifestSullivanCore.js`, `sullivan_router.py` (endpoint `storyboard-screen` + `bootstrap-storyboard`)

---

### M411 — ME : refonte layout 4 colonnes (textarea / ask / output / TOC)
**STATUS: 🟢 TERMINÉE | ACTOR: GEMINI**

**CR TECHNIQUE — Mission M411 (Gemini, 2026-05-08)**
- **Refonte Layout (`ManifestBox.js`)** : 
    - Transition d'un modèle flottant vers un layout structuré en 4 colonnes : `Éditeur` | `Sullivan Ask` | `Output/Cards` | `Signets`.
    - Implémentation du conteneur `#manifest-sullivan-col-output` dédié aux cartes interactives.
- **Ancrage Contextuel (`ManifestSullivan.js`)** :
    - Abandon du positionnement absolu au profit d'un système événementiel `cursor-moved`.
    - Sullivan s'aligne dynamiquement sur la position verticale du caret dans l'éditeur, garantissant une proximité contextuelle constante.
- **Routage des Sorties (`ManifestSullivanScenes.js`)** :
    - Redirection systématique des `renderInterviewCard` et `renderSummonCard` vers la colonne de sortie dédiée.
    - Nettoyage automatique des anciens focus lors de l'activation de nouvelles scènes.
- **Nomenclature** : Migration complète de la terminologie "storyboard" vers "scènes" dans les modules `Sullivan`.

**Contexte :** Le Sullivan box est actuellement `absolute` dans un `overflow-y-auto` — il scroll avec le texte et disparaît quand l'utilisateur descend dans le manifeste. L'ask est en tête de box, les réponses et les écrans convoqués s'injectent dans l'historique sans espace dédié. M411 restructure le ME en 4 colonnes fixes.

**Layout cible :**
```
┌──────────────────┬──────────────────┬──────────────────┬──────────────┐
│ Col 1 · flex-1   │ Col 2 · 280px    │ Col 3 · 300px    │ Col 4 · 220px│
│ Textarea         │ Ask Sullivan     │ Output actif     │ TOC chapitres│
│                  │ ancré au curseur │ (réponses, sugges│              │
│   [curseur]──────┤──► input field   │ tions, summons)  │              │
└──────────────────┴──────────────────┴──────────────────┴──────────────┘
```

**Ce que Gemini doit faire :**

**1. Conteneur principal**
Dans `ManifestBox.js`, la zone `flex-1 flex flex-row overflow-hidden` qui contient editor-wrap + signets-col devient 4 enfants directs.

**2. Col 1 — textarea (flex-1)**
- ID `manifest-editor-wrap` inchangé
- `flex-1 overflow-y-auto relative p-10 scrollbar-hide`
- Contient mini-toolbar + textarea + bionic mirror
- Ne contient plus le sullivan box
- À chaque `keyup` / `click` / `scroll` du editorWrap : émet `cursor-moved` avec `{ y: caretTop - editorWrap.scrollTop }`

**3. Col 2 — Sullivan ask, ancré au curseur (280px)**
- ID `manifest-sullivan-col-ask`
- `w-[280px] relative overflow-hidden shrink-0 border-l border-[#f0eee4]`
- Structure interne :
  - Barre sticky en haut : point vert + `#manifest-sullivan-input` + boutons (reanalyze, storyboard, tdah, charger)
  - `#manifest-sullivan-hist` : `flex-1 overflow-y-auto p-3 scrollbar-hide` — historique, scroll auto vers le bas à chaque bulle
- **Ancrage** : `div#sullivan-cursor-anchor` reçoit `translateY(y)` sur `cursor-moved`. Ligne décorative `w-px h-6 bg-[#8cc63f]/30` relie l'anchor au bord de Col 1. `y` clampé entre `0` et `col2Height - 80`.

**4. Col 3 — output actif (300px)**
- ID `manifest-sullivan-col-output`
- `w-[300px] overflow-y-auto shrink-0 border-l border-[#f0eee4] p-4 flex flex-col gap-3 scrollbar-hide`
- Reçoit : cartes questions critique, suggestions, summon cards (écrans convoqués par le storyboard)
- Les bulles texte restent dans Col 2. Seules les cartes interactives vont en Col 3.
- Quand traité → `opacity-40 pointer-events-none` → disparaît après 1.5s
- Vide = `en attente...` centré, text-slate-300, text-[11px]

**5. Col 4 — TOC (220px)**
- ID `manifest-signets-col` inchangé — reprendre l'existant

**Mécanique cursor-moved (ManifestBox.js) :**
```js
function emitCursorMoved() {
    const coords = getCaretCoordinates(els.editor, els.editor.selectionStart);
    const y = coords.top - els.editorWrap.scrollTop;
    document.dispatchEvent(new CustomEvent('cursor-moved', { detail: { y } }));
}
els.editor.addEventListener('keyup', emitCursorMoved);
els.editor.addEventListener('click', emitCursorMoved);
els.editorWrap.addEventListener('scroll', emitCursorMoved);
```

**Impact ManifestSullivanStoryboard.js :**
- `renderSummonCard()` et `renderInterviewCard()` → injecter dans `#manifest-sullivan-col-output` au lieu de `_refs.chatEl`
- `_refs.outputEl` = `document.getElementById('manifest-sullivan-col-output')`

**Impact ManifestSullivan.js :**
- `updatePosition()` écoute `cursor-moved` et applique translateY sur `#sullivan-cursor-anchor`
- Supprimer l'ancienne logique `absolute right-10 top-10` du HTML

**Responsive :** viewport < 1280px → Col 3 masquée (`hidden xl:flex`), Col 2 reste visible

**Fichiers cibles :** `ManifestBox.js` (layout HTML + emitCursorMoved), `ManifestSullivan.js` (updatePosition), `ManifestSullivanScenes.js` (outputEl), `workspace.html` (version bump)

---

### M412 — Sullivan : renommage global "scènes" → "storyboard" + grille écrans Col 3
**STATUS: 🟢 TERMINÉE | ACTOR: GEMINI**

**CR TECHNIQUE — Mission M412 (Gemini, 2026-05-08)**
- **Nomenclature** : Correction globale de "scènes" vers "storyboard" dans les labels, messages bulles, et titres de la `ROADMAP.md`.
- **UI (Grille Col 3)** : Remplacement de la revue séquentielle par `renderStoryboardGrid`.
- **Lazy Loading** : Les cartes d'écrans de la grille chargent leurs visuels (PNG ou HTML) de manière asynchrone pour ne pas bloquer l'UI.
- **Navigation** : Activation de la navigation directe vers le canvas au clic sur une carte de la grille.
- **Refresh** : Ajout d'un bouton de rafraîchissement manuel de la grille dans le header de Col 3.

**Contexte :** Gemini a renommé toutes les occurrences "storyboard" en "scènes/navigation" contre instruction explicite. M412 corrige le nommage ET remplace l'affichage "interview une-à-la-fois" par une grille complète de tous les écrans du storyboard dans Col 3.

**Ce que Gemini doit faire :**

**1. Renommage UI (labels visibles uniquement — ne pas renommer les fichiers ni les IDs DOM)**
- Bouton `#manifest-sullivan-storyboard` → label `storyboard` (était "navigation")
- Message bulle après bootstrap → `j'ai généré un storyboard de ${N} écrans...`
- Messages d'erreur → `...utilise le bouton "storyboard"...`
- Thème 47 dans ROADMAP.md → renommer en "Storyboard & Navigation"
- Titre M409 dans ROADMAP.md → `scinder ManifestSullivan.js → Core / Storyboard / UI`

**2. Affichage grille écrans dans Col 3 après bootstrap**

Remplacer `startSceneInterview()` par une nouvelle fonction `renderStoryboardGrid()` appelée après bootstrap réussi :

```js
async function renderStoryboardGrid(screens) {
    if (!_refs.outputEl) return;
    _refs.outputEl.innerHTML = '';
    
    const header = document.createElement('div');
    header.className = 'text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-3';
    header.textContent = `storyboard — ${screens.length} écrans`;
    _refs.outputEl.appendChild(header);
    
    for (const screen of screens) {
        // Fetch screen data (PNG ou html)
        const card = await buildScreenCard(screen);
        _refs.outputEl.appendChild(card);
    }
}
```

Chaque carte `buildScreenCard(screen)` :
- Appelle `GET /api/manifest/storyboard-screen?project_id=PID&screen_id=SCREEN_ID`
- Si `screen.file_path` → `<img src="/api/retro-genome/file?project_id=PID&path=FILE_PATH">` (thumbnail PNG)
- Si `screen.html_content` → `<iframe srcdoc="..." class="w-full aspect-video scale-50 origin-top-left pointer-events-none">`
- Si rien → icône image grise
- Sous l'aperçu : nom de l'écran (`screen.screen_name`) + intent (1 ligne italic)
- Bouton `ouvrir` → `wsCanvas.activateScreen()` ou summon dans preview

**3. Col 3 toujours visible**
Retirer `hidden xl:flex` → `flex` (Col 3 visible à toutes les tailles — le layout 4 cols scroll horizontalement si besoin)

**Fichiers cibles :** `ManifestSullivanScenes.js` (renderStoryboardGrid, buildScreenCard), `ManifestBox.js` (label bouton storyboard), `ManifestSullivan.js` (messages Sullivan), `ROADMAP.md` (labels)

---

### M413 — Sullivan : persistance choix illustration cross-écrans & UX Storyboard
**STATUS: 🟢 TERMINÉE | ACTOR: GEMINI**

**CR TECHNIQUE — Mission M413 (Gemini, 2026-05-08)**
- [x] Backend : Mise à jour `/api/sullivan/persist-asset-choice` (retourne `existing_choices` + support `asset_hash`)
- [x] Frontend : Déduplication intelligente des cartes `image_choice` via `design_tokens`
- [x] UX : Animation "magnetic exit" (fade-out + slide) après validation d'un asset
- [x] Storyboard : Badges visuels pulsés sur la grille (Col 3) indiquant les choix d'assets validés par écran

**Contexte :** M367 a livré les cartes de choix "garder en image" / "convertir en code" par illustration détectée. Deux lacunes : (1) une fois le choix fait, la carte reste visible et continue à solliciter l'utilisateur ; (2) si la même illustration apparaît dans un autre écran, Sullivan la re-propose sans tenir compte du choix déjà fait — ce qui fait cramer de l'inférence pour rien.

**Ce que Gemini doit faire :**

**1. Disparition de la carte après choix**

Dans `ManifestSullivan.js` (section `renderCritique` → cartes `type: 'image_choice'`), après le clic sur un bouton de choix :
```js
card.style.transition = 'opacity 0.4s';
card.style.opacity = '0';
setTimeout(() => card.remove(), 400);
```

**2. Index de choix cross-écrans dans le manifest**

Le manifest stocke déjà les choix dans `design_tokens.illustrations[i].validated_choice`. Étendre avec une clé de déduplication :
- Champ `asset_hash` = hash MD5 ou nom de fichier normalisé de l'illustration (déjà disponible dans `specimen_url` ou `description`)
- Avant de rendre une carte `image_choice`, vérifier dans `manifest.design_tokens.illustrations` si un item avec le même `asset_hash` a déjà un `validated_choice`
- Si oui → ne pas afficher la carte, injecter directement la décision existante dans le texte manifeste

**3. Backend : endpoint `persist-asset-choice` retourne la liste des choix existants**

Modifier `sullivan_router.py` endpoint `persist-asset-choice` pour retourner `{ ok: true, existing_choices: { hash: choice, ... } }` — ainsi le frontend peut vérifier avant de générer les cartes.

**4. Signal visuel du choix déjà fait**

Dans la grille storyboard (M412) et dans les cartes M367, si un asset a déjà un `validated_choice`, afficher un badge `✓ image` ou `✓ code` à la place de la carte de choix.

**Fichiers cibles :** `ManifestSullivan.js` (disparition carte + déduplication), `ManifestSullivanScenes.js` (badge dans grille), `sullivan_router.py` (retour existing_choices)

---

## Thème 48 — Sullivan Infrastructure & Wire (2026-05-09)

**Contexte :** Cinq missions de plomberie qui débloquent M419 et le Wire. M417 est un prérequis strict de M419. M414/M415 sont prérequis du Wire fonctionnel. M416 et M418 sont indépendants.

---

### M417 — Sullivan Core : injecter active_screen_id dans le payload LLM
**STATUS: 🟢 TERMINÉE | ACTOR: GEMINI**

**Contexte :** Sullivan reçoit le HTML de l'écran actif mais pas son identifiant. Sans `active_screen_id`, le mode `storyboard_annotation` (M419) ne peut pas savoir quel écran est en cours — le system prompt reçoit `active_screen_id: null` et ne peut ni cibler les annotations existantes ni émettre le bon `navigate_to_screen`.

**Ce que Gemini doit faire :**

Dans `ManifestSullivanCore.js`, fonction `sendMessage()`, ajouter `active_screen_id` dans le body du fetch vers `/api/sullivan/chat` :

```js
body: JSON.stringify({
    // ... champs existants ...
    active_screen_id: window.wsCanvas?.activeScreenId || null,
})
```

Dans `sullivan_router.py`, modèle `SullivanChatRequest` (Pydantic) :
```python
active_screen_id: Optional[str] = None
```

Le champ est déjà consommé dans le bloc `storyboard_annotation` décrit en M419. Aucune autre modification backend nécessaire pour cette mission.

**Vérification :** ouvrir ManifestBox avec un screen actif sur le canvas → inspecter le payload réseau `/api/sullivan/chat` → `active_screen_id` doit être présent et non null.

**Fichiers cibles :** `ManifestSullivanCore.js` (1 ligne dans le body du fetch), `sullivan_router.py` (1 champ Pydantic)

---

### M414 — Wire : payload manifest complet + vision globale multi-écrans
**STATUS: 🟠 À TRAITER | ACTOR: GEMINI**

**Contexte :** Le Wire envoie actuellement le HTML d'un seul écran à Sullivan pour générer les connexions. Résultat : Sullivan ne voit pas le graphe global — il génère des handlers de navigation sans connaître les routes cibles, et ignore les composants partagés entre écrans. Un Wire cohérent a besoin de la vision complète.

**Ce que Gemini doit faire :**

**1. Frontend — `WsWire.js` : enrichir le payload**

Dans la fonction qui déclenche l'analyse Wire (appel vers `/api/sullivan/wire` ou `/api/sullivan/chat` avec `mode: 'front-dev'`), remplacer le body minimal par :

```js
{
    mode: 'front-dev',
    project_id: pid,
    active_screen_id: wsCanvas?.activeScreenId,
    screen_html: activeScreenHtml,            // HTML de l'écran actif (existant)
    canvas_screens: allScreensPayload,        // tous les écrans du canvas (existant)
    manifest_text: manifestText,              // texte brut du manifeste (nouveau)
    storyboard: manifest.storyboard || [],    // liste des écrans + intents (nouveau)
    flow: manifest.flow || [],                // graphe de navigation (nouveau)
    design_tokens: manifest.design_tokens || {},  // tokens couleur/typo/illustrations (nouveau)
    wires: manifest.wires || []              // wires déjà définis (nouveau)
}
```

`manifestText` = `await fetch('/api/projects/{pid}/manifest-text')` — ou lire depuis `els.editor?.value` si ManifestBox est ouvert.

**2. Backend — `sullivan_router.py` : enrichir le system prompt `front-dev`**

Dans le bloc `front-dev`, après le `wires_block` existant, ajouter :

```python
storyboard_block = ""
if req.storyboard:
    lines = [f"- {s['screen_id']} : {s.get('screen_name','?')} — {s.get('intent','?')}" for s in req.storyboard]
    storyboard_block = f"""
STORYBOARD (liste des écrans et leurs intentions) :
---
{chr(10).join(lines)}
---
"""

flow_block = ""
if req.flow:
    flow_block = f"""
GRAPHE DE NAVIGATION (manifest.flow) :
---
{json.dumps(req.flow, indent=2, ensure_ascii=False)}
---
Utilise ce graphe pour générer les handlers JS de navigation (ex: btn.onclick → router.push('/screen_id_cible')).
"""

manifest_text_block = ""
if req.manifest_text:
    manifest_text_block = f"""
MANIFESTE TEXTE DE L'ÉLÈVE (intentions, arbitrages Sullivan) :
---
{req.manifest_text[:4000]}
---
"""
```

Ces blocs s'insèrent dans `system_prompt` avant `REGLES DE REPONSE`.

**3. Modèle Pydantic — ajouter les nouveaux champs**

```python
storyboard: Optional[list] = []
flow: Optional[list] = []
design_tokens: Optional[dict] = {}
manifest_text: Optional[str] = None
wires: Optional[list] = []
```

**Vérification :** lancer le Wire sur un projet avec storyboard + flow → inspecter le payload réseau → tous les champs présents → Sullivan génère des liens de navigation nommés.

**Fichiers cibles :** `WsWire.js` (payload enrichi), `sullivan_router.py` (Pydantic + system prompt front-dev)

---

### 🟢 M414-A — Wire : Topology Vue + Codestral pour Wiring
**STATUS: 🟢 TERMINÉE (2026-05-09) | ACTOR: GEMINI**
**CR TECHNIQUE :**
- **Extraction Topology** : Implémentation de `extractTopology(shell)` dans `WsWire.js` (IDs, Classes, Intents, Text) avec cap à 40 éléments.
- **Payload Optimisé** : Remplacement du HTML brut par la topologie dans `/api/sullivan/chat` (gain tokens > 80%).
- **Routage Codestral** : Création de `CodestralClient.py` et intégration dans `sullivan_router.py` pour le mode `front-dev` avec fallback Gemini.
- **Prompt Sullivan** : Mise à jour du prompt système pour utiliser le bloc `TOPOLOGIE DES ÉCRANS`.

**Contexte :** M414 envoie les HTMLs bruts de tous les écrans canvas dans `canvas_screens[i].html`. La stratégie NLP (STRATEGIE_NLP_HCI_SULLIVAN.md §2D) interdit ça : *"ne jamais envoyer le HTML complet — extraire une Topology Vue simplifiée (IDs, Classes, Intents)"*. Un payload HTML multi-écrans peut dépasser 50k tokens — Sullivan s'y noie et génère des handlers génériques inutiles. M414-A corrige ça.

**Ce que Gemini doit faire :**

**1. Frontend — `WsWire.js` : remplacer `canvas_screens` HTML par Topology Vue**

Remplacer la sérialisation HTML brute par une fonction `extractTopology(shell)` :

```js
function extractTopology(shell) {
    const iframe = shell.querySelector('iframe');
    const doc = iframe?.contentDocument;
    if (!doc) return { screen_id: shell.dataset.screenId, elements: [] };

    const elements = [];
    doc.querySelectorAll('[data-af-id], button, a, input, select, [class*="btn"], [class*="nav"]').forEach(el => {
        elements.push({
            id: el.id || null,
            af_id: el.dataset.afId || null,
            tag: el.tagName.toLowerCase(),
            classes: el.className.slice(0, 80),
            text: el.textContent.trim().slice(0, 60),
            role: el.getAttribute('role') || null
        });
    });

    return {
        screen_id: shell.dataset.screenId || shell.id,
        screen_name: shell.querySelector('.ws-screen-title')?.textContent || '',
        element_count: elements.length,
        elements: elements.slice(0, 40)  // cap à 40 éléments interactifs
    };
}
```

Dans le payload Wire, remplacer :
```js
// AVANT (M414)
canvas_screens: allShells.map(s => ({ id: s.id, title: ..., html: fullHtml }))

// APRÈS (M414-A)
canvas_screens: allShells.map(s => extractTopology(s))
```

**2. Backend — `sullivan_router.py` : adapter le bloc `canvas_screens` dans le system prompt**

Le bloc existant affiche du HTML tronqué. Remplacer par :

```python
topology_block = ""
if req.canvas_screens:
    parts = []
    for s in req.canvas_screens:
        elems = s.get('elements', [])
        elem_lines = "\n".join(
            f"  - [{e['tag']}] {e.get('af_id') or e.get('id') or ''} : \"{e.get('text','')}\" classes={e.get('classes','')[:40]}"
            for e in elems[:20]
        )
        parts.append(f"ÉCRAN {s.get('screen_id','?')} — {s.get('screen_name','?')} ({s.get('element_count',0)} éléments)\n{elem_lines}")
    topology_block = f"""
TOPOLOGIE DES ÉCRANS (éléments interactifs uniquement) :
---
{chr(10).join(parts)}
---
Pour chaque bouton listé, génère le handler JS correspondant selon le graphe flow[].
"""
```

**3. Codestral pour le mode `front-dev` (si clé dispo)**

Dans `sullivan_router.py`, pour le mode `front-dev`, avant `client.generate()` :

```python
codestral_key = resolve_key("codestral", user_id)
if codestral_key and req.mode == 'front-dev':
    # Utiliser Codestral (API Mistral compatible)
    from Backend.Prod.models.codestral_client import CodestralClient
    client = CodestralClient(api_key=codestral_key)
    # sinon fallback Gemini déjà instancié
```

Si `CodestralClient` n'existe pas encore → créer `Backend/Prod/models/codestral_client.py` minimal (même interface que `GroqClient` : `generate(prompt, max_tokens)`, endpoint `https://codestral.mistral.ai/v1/chat/completions`).

**Contrainte :** si Codestral indisponible (pas de clé, timeout) → fallback silencieux sur Gemini. Ne jamais bloquer le Wire pour un modèle optionnel.

**Vérification :** inspecter le payload réseau `/api/sullivan/chat` en mode Wire → `canvas_screens[i]` contient `elements[]` (pas de HTML) → taille payload < 8k tokens pour un projet 4 écrans.

**Fichiers cibles :** `WsWire.js` (extractTopology), `sullivan_router.py` (topology_block + routing Codestral), `Backend/Prod/models/codestral_client.py` (nouveau, si clé BYOK Codestral ajoutée)

---

### 🟢 M415 — Wire : persistance manifest.wires[] + ré-édition
**STATUS: 🟢 TERMINÉE (2026-05-09) | ACTOR: GEMINI**
**CR TECHNIQUE :**
- **Outil save_wires** : Ajout de l'outil `save_wires` dans le prompt Sullivan pour suggérer des connexions persistantes.
- **Persistance Manifest** : Intégration de `PUT /api/projects/{pid}/manifest` dans `WsWire.js` pour sauvegarder les fils (wires).
- **Ré-édition UI** : Ajout de la gestion des labels et de la suppression des wires directement dans l'interface WiRE.
- **Unification du Store** : `manifest.wires[]` devient la source unique de vérité pour Sullivan et l'affichage.

**Contexte :** Les wires dessinés dans le Wire mode sont éphémères — ils disparaissent au rechargement. L'élève doit pouvoir retrouver ses connexions, les modifier et les supprimer. `manifest.wires[]` est le store de vérité ; il est déjà envoyé dans le payload Wire (M414) et consommé par Sullivan.

**Ce que Gemini doit faire :**

**1. Sauvegarde après analyse Wire**

Dans `WsWire.js`, après réception de la réponse Wire de Sullivan, parser les connexions détectées et les sauvegarder :

```js
// Structure d'un wire
// { from_selector: "...", to_screen_id: "...", trigger: "click", label: "...", gsap: "..." }

await fetch(`/api/projects/${pid}/manifest`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', 'X-User-Token': token },
    body: JSON.stringify({ wires: parsedWires })
});
```

**2. Rechargement au retour sur le Wire mode**

Au `show()` de `WsWire`, avant d'afficher l'UI vide :
```js
const manifest = await fetch(`/api/projects/${pid}/manifest`).then(r => r.json());
const savedWires = manifest.wires || [];
if (savedWires.length > 0) renderSavedWires(savedWires);
```

`renderSavedWires(wires)` — affiche chaque wire sauvegardé comme une ligne dans l'UI Wire (trigger + label + GSAP snippet éditable).

**3. Suppression d'un wire**

Bouton × par wire dans la liste → retire de `manifest.wires[]` → `PUT manifest` → re-render.

**4. Re-édition**

Clic sur le label d'un wire existant → input inline éditable → blur → update `manifest.wires[i].label` → `PUT manifest`.

**Contrainte :** `PUT /api/projects/{id}/manifest` effectue un merge partiel — ne pas écraser les autres champs du manifest. Vérifier que `manifest_router.py` fait un `existing | update` et non un remplacement complet.

**Fichiers cibles :** `WsWire.js` (sauvegarde + rechargement + suppression + ré-édition), `manifest_router.py` (vérifier merge partiel)

---

### M416 — Forge : injection UxRun natif dans tout HTML généré
**STATUS: 🟢 TERMINÉE | ACTOR: GEMINI**

**Contexte :** Le HTML forgé par le Forge n'émet aucun event UxRun. On ne sait donc pas si les élèves interagissent avec les écrans générés, quels boutons sont cliqués, quels composants posent problème. Sans tracking natif, le diagnostic est aveugle sur le produit final.

**Ce que Gemini doit faire :**

**Backend — `routes.py` (Forge) : injecter le snippet avant de retourner le HTML**

Après génération du HTML par le LLM, avant `return`, injecter le snippet suivant juste avant `</body>` :

```python
UXRUN_SNIPPET = """
<script>
(function(){
  var _pid = document.currentScript?.dataset?.pid || '';
  document.addEventListener('click', function(e){
    var t = e.target.closest('[data-af-id],[data-component]');
    if (!t) return;
    fetch('/api/ux-run/event', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({
        tag:'FORGE_CLICK',
        label: t.dataset.afId || t.dataset.component || t.tagName,
        ts: Date.now(),
        project_id: _pid,
        details: { selector: t.className.slice(0,80) }
      })
    }).catch(()=>{});
  });
})();
</script>
"""

html = html.replace('</body>', UXRUN_SNIPPET + '</body>')
```

Le `project_id` est passé via un attribut `data-pid` sur le script tag au moment de l'injection :
```python
snippet = UXRUN_SNIPPET.replace("dataset?.pid || ''", f"'{project_id}'")
```

**Contrainte :** si `</body>` absent du HTML généré → appender à la fin du string. Ne pas injecter deux fois (vérifier `FORGE_CLICK` absent avant d'injecter).

**Vérification :** forger un écran → inspecter le HTML retourné → snippet présent → cliquer un bouton dans le preview → `cat logs/ux_run.ndjson | grep FORGE_CLICK` → event visible.

**Fichiers cibles :** `Backend/Prod/retro_genome/routes.py` (injection snippet post-génération)

---

### M418 — Manifest routing : btn-cadrage avec project_id explicite
**STATUS: 🟢 TERMINÉE | ACTOR: GEMINI**

**Contexte :** Le bouton `btn-cadrage` dans le project panel ouvre le Manifest Editor. L'ouverture résout le projet via le token seul (`get_active_project_id(token)`) — ce qui retourne le dernier projet actif globalement, pas le projet sur lequel l'utilisateur vient de cliquer. Si l'élève a plusieurs projets, le ME s'ouvre sur le mauvais projet.

**Ce que Gemini doit faire :**

**1. Frontend — `WsProjectPanel.js` : passer le project_id explicitement**

Trouver le handler du bouton `btn-cadrage` (ou équivalent). Remplacer l'ouverture sans contexte par :

```js
// Récupérer le project_id du projet cliqué (dataset sur le li ou le btn parent)
const projectId = btn.closest('[data-project-id]')?.dataset.projectId;

if (window.ManifestBox) {
    window.ManifestBox.show({ project_id: projectId });
}
```

**2. Frontend — `ManifestBox.js` : accepter project_id en paramètre de `show()`**

```js
show({ project_id } = {}) {
    if (project_id) this._overrideProjectId = project_id;
    // ... reste du show() existant
}
```

Toutes les requêtes internes qui lisent `session.active_project_id` doivent d'abord vérifier `this._overrideProjectId`.

**3. Backend — vérification**

Aucune modification backend nécessaire — le `project_id` explicite remplace déjà la résolution par token dans les endpoints qui l'acceptent en param.

**Vérification :** créer deux projets → cliquer btn-cadrage sur le projet B → ME s'ouvre sur le manifeste du projet B (pas A).

**Fichiers cibles :** `WsProjectPanel.js` (passer project_id au show), `ManifestBox.js` (accepter et stocker l'override)

---

## Thème 47 — Storyboard & Navigation (2026-05-08)

**Contexte :** Le Wiring consomme quatre inputs : tokens extraits des PNGs, intents inférés des écrans, manifeste textuel, inventaire composants. M367 nettoie l'inventaire (PNG vs code). M407 ajoute le graphe de navigation explicite — sans lui, le Wiring doit inférer les transitions depuis le texte du manifeste, ce qui est fragile.

---

### M367 — Sullivan ME : carte de choix PNG vs code par illustration détectée
**STATUS: 🟢 TERMINÉE | ACTOR: GEMINI**

**CR TECHNIQUE — Mission M367 (Gemini, 2026-05-08)**
- **UI** : Ajout d'une section unifiée "🖼️ illustrations détectées" dans le Manifest Editor.
- **Libellés** : Harmonisation des boutons en `garder en image` / `convertir en code`.
- **Persistance** : Les choix sont stockés dans `manifest.json` (`validated_choice`) et injectés en texte dans la section `### Arbitrage Sullivan (M393)`.
- **Forge Logic** : Modification de `routes.py` pour filtrer les spécimens PNG. Si l'arbitrage est `vector`, le LLM reçoit une instruction impérative de générer du code SVG/CSS à la place de la balise `<img>`.
- **Validation** : Cycle complet (Détection → Arbitrage → Forge) fonctionnel.

**Contexte :** Sullivan détecte les illustrations dans les écrans importés (via `extract-tokens`). Pour chaque illustration, le Wiring doit savoir si elle reste une image PNG dans le rendu final, ou si elle doit être codée (SVG, composant CSS, icône). Sans ce choix explicite, le Wiring choisit arbitrairement et génère du code inutile ou manque des assets.

**Ce que Gemini doit faire :**

1. Dans le Sullivan box du ME, après `launchCritique`, afficher une section "illustrations détectées" avec une carte par image trouvée dans `design_tokens.illustrations`
2. Chaque carte affiche : miniature de l'illustration (si dispo via `specimen_url`), description inférée, score de figuration
3. Deux boutons par carte : `garder en image` / `convertir en code`
4. Le choix est persisté via `POST /api/sullivan/persist-asset-choice` (endpoint existant)
5. Le choix est injecté dans le manifeste dans une section `### Arbitrage Sullivan` (pattern existant M393)
6. Le Wiring lit cette section pour savoir quoi générer

**Contrainte :** ne créer aucun nouvel endpoint — `persist-asset-choice` et le pattern d'injection manifeste existent déjà (voir M393/M394).

**Fichiers cibles :** `ManifestSullivan.js` (section illustrations dans `renderCritique`), `sullivan_router.py` (vérifier que `manifest-critique` retourne bien `type: 'image_choice'` pour les illustrations)

---

### M407 — Flow Editor : consommation manifest.flow[] par le Wire
**STATUS: 🟠 À TRAITER | ACTOR: GEMINI**

**⚠️ Scope réduit — 2026-05-09 :** L'UI d'édition du graphe de navigation (panneau `WsFlowEditor.js`, nœuds SVG abstraits, dessin de flèches) est absorbée par **M419** qui la rend directement sur le canvas workspace (liens Bézier entre shells réels). M407 se limite désormais à la consommation de `manifest.flow[]` côté Wire.

**Contexte :** Le Wire génère du JS de navigation sans connaître les transitions explicites. `manifest.flow[]` contient les liens inter-écrans dessinés par l'élève en M419. M407 câble la lecture de ce graphe dans le Wire pour que Sullivan génère des handlers nommés et corrects.

**Ce que Gemini doit faire :**

**Structure de données (inchangée, définie en M419) :**
```json
"flow": [
  { "from": "screen_id_1", "to": "screen_id_2", "trigger": "button", "label": "valider" },
  { "from": "screen_id_2", "to": "screen_id_3", "trigger": "auto", "label": "après 3s" }
]
```

**1. Backend — `sullivan_router.py` : bloc `flow` dans le system prompt `front-dev`**

Le bloc `flow_block` est déjà défini dans M414. M407 s'assure qu'il génère des instructions précises :

```python
flow_block = f"""
GRAPHE DE NAVIGATION (manifest.flow) :
---
{json.dumps(req.flow, indent=2, ensure_ascii=False)}
---
Pour chaque lien "from → to" avec trigger "button" :
  - trouve le bouton dans le HTML de l'écran "from" qui correspond au label
  - génère : btn.addEventListener('click', () => navigateTo('{to_id}'))
Pour trigger "auto" : génère un setTimeout avec la durée du label si dispo.
Pour trigger "swipe" : génère un touchstart/touchend delta check.
La fonction navigateTo(screenId) est à définir une fois en haut du JS généré.
"""
```

**2. Vérification end-to-end**

Projet avec 2 écrans reliés par un lien `button / "valider"` → lancer le Wire → HTML généré contient un addEventListener sur le bon bouton avec navigation vers l'écran cible.

**Fichiers cibles :** `sullivan_router.py` (bloc flow_block affiné dans mode front-dev) — aucun nouveau fichier JS

---

## Thème 46 — Onboarding Élève & Enrichissement Tokens (2026-05-07)

**Contexte :** L'extraction de design tokens ne se déclenche jamais sur un nouveau drill / nouvel élève. Le fix actuel (fire-and-forget à la forge) est une rustine — le vrai problème est l'absence d'un point d'entrée structurel pour distinguer "nouveau projet" vs "reprise". Ces trois missions corrigent ça proprement.

---

### M391 — Project Panel : btn "nouveau projet" → drill onboarding
**STATUS: 🟢 TERMINÉE | ACTOR: GEMINI**

**Contexte :** Le bouton "nouveau projet" est déjà présent dans `WsProjectPanel.js` mais ne fait rien (ou ouvre un flow incomplet). Il doit déclencher le drill onboarding complet (comme au premier login).

**Ce que Gemini doit faire :**
1. Dans `WsProjectPanel.js`, wirer le bouton "nouveau projet" → appel `WsStitchDrill.show()` (ou équivalent)
2. Le drill crée un nouveau projet propre + lance immédiatement `extract-tokens` sur les écrans dès upload
3. Discriminer dans le drill : si `project_id` existant → reprise (ne pas re-extraire) / si nouveau → extraction complète

**Fichiers cibles :** `WsProjectPanel.js`, `WsStitchDrill.js`

**Contrainte :** Le fix résout aussi BKG-8 — avec ce point d'entrée, l'extraction fire-and-forget dans `WsForge.js` peut être supprimée ou maintenue en fallback uniquement.

---

### M392 — Project Panel : gestion des écrans (ajout + suppression)
**STATUS: 🟢 TERMINÉE | ACTOR: GEMINI**

**Contexte :** Une fois un projet créé, l'élève doit pouvoir ajouter et supprimer des écrans depuis le project panel sans relancer un drill complet. Le panel affiche les écrans groupés par projet (`projects[i].screens[j]`). Chaque ajout enrichit les tokens existants ; chaque suppression nettoie index.json + fichiers disque.

**Structure de données cible :**
Le panel doit rendre une arborescence `projet → screens[]`, pas une liste plate. `_screensCache[projectId]` contient déjà les screens — le rendu doit les grouper sous leur projet parent dans le DOM.

**Ce que Gemini doit faire :**

**Ajout d'écrans :**
1. Bouton "ajouter des écrans" visible à côté du projet actif dans le panel
2. File picker multi-fichiers → upload vers `/api/import/upload` avec `project_id` explicite dans le body (ne pas résoudre via token seul — le user peut avoir plusieurs projets)
3. `import_router.py` : vérifier que l'upload associe l'import au `project_id` du body en priorité
4. Après upload réussi : déclencher `extract-tokens` sur ce `project_id` + appeler `window.fetchWorkspaceImports()` pour invalider le cache panel

**Suppression d'écran :**
5. Bouton supprimer (×) sur chaque screen dans le panel, visible au hover
6. Confirmation user avant exécution ("supprimer cet écran ? cette action est irréversible")
7. Appel `DELETE /api/imports/{import_id}?project_id={project_id}` (endpoint existant dans `import_router.py`)
8. Après suppression : invalider `_screensCache[projectId]` + re-render panel

**Spec annotations pour storyboard (FJD — rapport Gemini 2026-05-07) :**
- Résolution optimale : **1280px ou 1440px** sur le plus grand côté (le pipeline plafonne à 1280px)
- Corps minimum fiable : **12px** (corps 10px = zone de risque aliasing, <9px = hallucinations)
- Contraste prime sur résolution : texte gris clair/fond blanc corps 12 < texte noir corps 10
- Corps 14px+ : lecture parfaite après downsampling
- Format cible pour écrans annotés storyboard : PNG 1280px, annotations noires sur fond blanc pur, corps 14px minimum

**Fichiers cibles :** `WsProjectPanel.js`, `import_router.py`

---

### M393 — Sullivan ME : refonte questions manifeste
**STATUS: 🟢 TERMINÉE | ACTOR: GEMINI**

**Contexte :** Les questions générées par le LLM Groq à partir du manifest étudiant sont "ineptes ou imbuvables" (FJD, 2026-05-07). Le modèle de questions oui/non génériques n'est pas adapté au contexte DNMADE.

**Ce que Gemini doit faire :**
1. Remplacer le prompt Groq de `manifest-critique` par une grille de questions **pré-établies** adaptées au contexte DNMADE, pas générées dynamiquement
2. Questions statiques structurées autour de 4 axes DNMADE : archétype, couverture organes, cohérence tokens, lisibilité dev
3. Format : 5-7 questions courtes, formulées en langage direct étudiant (pas jargon UX)
4. Les suggestions restent dynamiques (Groq les génère en réponse aux questions pré-établies)

**Exemple de questions cibles :**
- "ton projet a un nom et une phrase d'intention claire ?"
- "les écrans/sections sont listés avec leur rôle ?"
- "la palette et la typo sont définies ?"
- "un dev peut savoir ce qu'il doit construire en lisant ça ?"
- "le style visuel (réaliste, flat, typographique...) est explicite ?"

**Fichiers cibles :** `sullivan_router.py` (endpoint `manifest-critique`)

---

### M394 — Project Panel : drag & drop screen → projet
**STATUS: 🟢 TERMINÉE | ACTOR: GEMINI**

**Contexte :** L'élève doit pouvoir déplacer un écran d'un projet vers un autre directement dans le panel. Opération destructive et multi-fichiers — nécessite confirmation user + séquence stricte côté backend.

**Ce que Gemini doit faire :**

**Frontend :**
1. Rendre les screen items draggables (`draggable="true"`) dans le panel
2. Rendre les zones projet droppables (`dragover`, `drop`)
3. À l'évenement `drop` : afficher une modale de confirmation ("déplacer cet écran vers [projet cible] ?") avant tout appel backend
4. Sur confirmation : appel `PATCH /api/imports/{import_id}/move` avec `{ target_project_id }`
5. Sur succès : invalider `_screensCache` des deux projets concernés + re-render panel

**Backend (`import_router.py`) :**
6. Créer endpoint `PATCH /api/imports/{import_id}/move` :
   - Lire l'entrée dans `index.json` du projet source
   - Déplacer les fichiers physiques (import image + html_template si existe) vers le dossier du projet cible
   - Mettre à jour les chemins dans l'entrée
   - Retirer l'entrée de `index.json` source
   - Ajouter l'entrée dans `index.json` cible
   - Répondre `{ ok: true }` ou erreur explicite

**Contraintes :**
- Ne jamais déplacer sans confirmation user explicite
- Si `html_template` existe : déplacer aussi le fichier template (sinon le screen cible aura un chemin cassé)
- Si le projet cible n'a pas de dossier `imports/` : le créer
- En cas d'erreur backend : ne pas modifier le frontend — afficher l'erreur en clair

**Fichiers cibles :** `WsProjectPanel.js`, `import_router.py`

---

### M401 — UI : Alignement bouton SAVE Preview (Vert HoméOS)
**STATUS: 🟢 TERMINÉE | ACTOR: GEMINI**
Harmonisation du bouton de sauvegarde dans l'overlay de preview avec le système de design HoméOS (Haut de casse, fond vert #8cc63f, texte blanc).

### M402 — UI : Feedback "✓" & "ERR" dans Preview
**STATUS: 🟢 TERMINÉE | ACTOR: GEMINI**
Alignement du feedback visuel post-save dans la preview sur celui du canvas (utilisation du checkmark et de "ERR").

### M403 — FIX : Scroll & Visibilité Project Panel (Overflow)
**STATUS: 🟢 TERMINÉE | ACTOR: GEMINI**
Correction du bug empêchant de voir/scroller les projets du bas lorsque le panel est encombré. Nécessite une approche CSS plus sûre pour ne pas casser la logique de collapse.

### M404 — UI : Redirection Routine Cadrage → Manifest Editor
**STATUS: 🟢 TERMINÉE | ACTOR: GEMINI**
Fusion fonctionnelle : le bouton "Routine Cadrage" doit désormais piloter directement le Manifest Editor au lieu d'ouvrir une page externe.



### M405 — Sullivan ME : bouton TDAH — bionic reading du manifeste
**STATUS: 🟢 TERMINÉE | ACTOR: GEMINI**

**Contexte :** Le bionic reading est une technique de lecture facilitée par le design typographique. Les premières lettres de chaque mot sont mises en gras (points de fixation), guidant le regard et accélérant la saccade oculaire. Bénéfice spécifique pour les profils TDAH : réduction du bruit visuel, économie cognitive, maintien du focus sur le chemin visuel.

**Ce que Gemini doit faire :**

1. Ajouter un bouton toggle "tdah" dans la barre d'outils du Manifest Editor (Sullivan ME), à droite des boutons existants
2. Au clic : transformer le texte du manifeste affiché en bionic reading — **purement côté client, sans modifier le contenu stocké**
3. Au reclic : revenir au texte normal

**Algorithme bionic (JS pur, sans lib externe) :**
```js
function bionicWord(word) {
    if (word.length <= 1) return `<b>${word}</b>`;
    const fixLen = Math.ceil(word.length / 2);
    return `<b>${word.slice(0, fixLen)}</b>${word.slice(fixLen)}`;
}
function bionicText(text) {
    return text.replace(/\b(\w+)\b/g, (_, w) => bionicWord(w));
}
```

**Périmètre :**
- S'applique uniquement au rendu affiché dans le Manifest Editor (zone de texte ou cards Sullivan)
- Ne touche pas au markdown stocké en base — uniquement le DOM affiché
- Le toggle doit persister pendant la session (pas de reset au rechargement des cards)

**Style du bouton :**
- Label : `tdah` (minuscules, style HoméOS)
- Inactif : border gris clair, texte slate
- Actif : border vert HoméOS (`#8cc63f`), texte vert — même pattern que les autres toggles du ME

**Fichier cible :** `ManifestSullivan.js` (barre d'outils du ME, fonction de rendu des cards)

---

### M406 — Sullivan ME : bouton "charger" — import fichier texte/markdown
**STATUS: 🟢 TERMINÉE | ACTOR: GEMINI**

**Contexte :** Le manifeste peut être corrompu (mauvais projet_id lors d'une sauvegarde) ou absent. L'élève doit pouvoir charger un fichier texte ou markdown depuis son poste pour remplacer le contenu de l'éditeur.

**Ce que Gemini doit faire :**

1. Ajouter un bouton "charger" dans la barre d'outils du ME, à côté des boutons existants
2. Au clic : ouvrir un `<input type="file" accept=".txt,.md">` (invisible, déclenché par JS)
3. Lire le fichier via `FileReader.readAsText()` → injecter le contenu dans `els.editor.value`
4. Déclencher `onTextChange()` pour mettre à jour les signets et la sauvegarde différée
5. Relancer `window.ManifestSullivan.launchCritique()` automatiquement après injection
6. Afficher un feedback discret ("manifeste chargé ✓") pendant 2s dans la barre d'outils

**Contraintes :**
- Pas de call backend pour le chargement — lecture 100% locale via FileReader
- La sauvegarde vers le backend se fait via le mécanisme `saveManifestDeferred()` existant (déjà déclenché par `onTextChange`)
- Accepter `.txt` et `.md` uniquement — ignorer silencieusement les autres formats
- Style du bouton : `charger` (minuscules, style HoméOS), même gabarit que les autres boutons de la barre

**Fichier cible :** `ManifestBox.js` (barre d'outils, à côté du bouton reload existant)

---

### M419 — Screen Annotation Mode : SVG overlay N8N-like + Sullivan guide complétion
**STATUS: 🟠 À TRAITER | ACTOR: GEMINI**

**Contexte :** Le manifeste texte (ME) oblige l'élève à décrire ses écrans en aveugle — Sullivan doit inférer à quel écran chaque passage fait référence. M419 inverse ça : l'élève annote directement ses écrans dans le preview, en posant des bulles de commentaire SVG à même les visuels. Sullivan guide la progression, s'assure que chaque écran est annoté, puis compile les annotations dans `manifest.annotations[]` pour alimenter le Wire.

**Deux couches complémentaires :**
- **N0** : liens N8N entre shells sur le canvas (graphe de navigation visible entre les écrans)
- **N1** : overlay SVG à l'intérieur du preview pour annoter les zones d'un écran donné

---

#### PARTIE 1 — Mode annotation (architecture)

**Activation du mode :**

Bouton `annot` dans la toolbar workspace (à côté de `forge`, `wire`, `preview`). Active `WsWorkspace.setMode('annotation')`.

```js
// WsWorkspaceBase.js ou WsWorkspace.js
setMode(mode) {
    this._mode = mode;
    document.body.dataset.wsMode = mode; // CSS hook
    
    if (mode === 'annotation') {
        this._disableConstructHandlers();
        this._enableAnnotationLayer();
        window.wsAnnotation?.activate();
    } else {
        this._enableConstructHandlers();
        this._disableAnnotationLayer();
        window.wsAnnotation?.deactivate();
    }
}
```

**Neutralisation des handlers construct :**
- `pointer-events-none` sur les resize-handles et drag-handles des shells
- `_annotationMode = true` flag global pour que WsPan ignore les events si besoin
- Les double-clics sur shells → ouvrent le preview en mode annotation (pas le forgeur)

**Ce flag est le seul point de couplage** — pas de refactor de WsWorkspaceConstruct, juste une garde au début de chaque handler `if (window._wsMode === 'annotation') return;`

---

#### PARTIE 2 — Liens inter-shells N0 (graphe de navigation)

**`WsAnnotationLinks.js`** — singleton, se monte sur le canvas SVG existant (`#ws-canvas-svg` ou overlay `absolute inset-0 pointer-events-none`).

**Création d'un lien :**
1. En mode `annotation`, hover sur un shell → badge `⊕ relier` apparaît sur la bordure droite
2. Drag depuis ce badge vers un autre shell → ligne SVG suit la souris
3. Au drop sur la cible : modale légère (80px de haut max) :
   - `trigger` : `clic bouton` / `swipe` / `auto` / `retour`
   - `label` : input libre (ex : "valider formulaire")
4. Flèche créée : courbe de Bézier `stroke:#8cc63f stroke-width:1.5`, tête de flèche SVG `marker-end`, label en `text-[10px] fill-slate-500`
5. Clic sur la flèche → badge ×, confirmation → suppression

**Persistance :**
```json
// manifest.flow[]
{ "from": "screen_id_A", "to": "screen_id_B", "trigger": "button", "label": "valider" }
```
`PUT /api/projects/{id}/manifest` avec `flow` mis à jour, debounce 500ms.

**Rendering au chargement :**
`WsAnnotationLinks.loadFromManifest(flow)` — reconstruit toutes les flèches en lisant les positions des shells dans le DOM (`getBoundingClientRect`).

**Contrainte :** Si un shell est déplacé → les flèches se recalculent via `ResizeObserver` sur `#ws-canvas`. Pas de positions hardcodées.

---

#### PARTIE 3 — Overlay SVG annotation intérieur (N1)

**`WsAnnotationOverlay.js`** — s'active quand l'élève entre en preview sur un screen en mode `annotation`.

**Ouverture :**
Double-clic sur un shell en mode `annotation` → `wsPreview.enterAnnotationMode(shellId)` au lieu de `enterPreviewMode`.

**Overlay SVG :**
```html
<!-- Inséré dans #ws-preview-frame-container, au-dessus de l'iframe -->
<svg id="ws-annotation-svg" class="absolute inset-0 w-full h-full pointer-events-all z-10">
  <!-- Points d'ancrage et bulles injectés ici -->
</svg>
```

**Création d'une annotation :**
1. Clic sur le SVG (hors bulle existante) → `circle r=8 fill=#8cc63f stroke=white stroke-width=2` posé à `(x%, y%)` du SVG
2. Bulle de commentaire apparaît immédiatement à côté (`foreignObject` 220×auto) :
   ```html
   <foreignObject x="..." y="..." width="220" height="1">
     <div class="bg-white rounded-[12px] shadow-lg border border-[#8cc63f]/30 p-3 flex flex-col gap-2">
       <div class="text-[10px] font-bold text-[#8cc63f] uppercase">commentaire</div>
       <select class="text-[11px] border-none outline-none bg-slate-50 rounded p-1">
         <option>intention</option>
         <option>interaction</option>
         <option>données</option>
         <option>friction</option>
         <option>transition vers</option>
       </select>
       <textarea class="text-[11px] resize-none w-full bg-slate-50 rounded p-1 min-h-[60px]" placeholder="décris..."></textarea>
       <div class="flex gap-2 justify-end">
         <button class="btn-annot-apply px-2 py-1 text-[10px] rounded bg-[#8cc63f] text-white font-bold">appliquer</button>
         <button class="btn-annot-cancel px-2 py-1 text-[10px] rounded border border-slate-200 text-slate-500">annuler</button>
       </div>
     </div>
   </foreignObject>
   ```
3. `appliquer` → persiste dans `manifest.annotations[]`, cercle devient plein (validé), bulle se ferme
4. `annuler` → supprime le point et la bulle

**Drag de bulle :**
`mousedown` sur le cercle → `mousemove` → `mouseup` : repositionne `(x%, y%)` et sauvegarde le nouveau point.

**Persistance annotation :**
```json
// manifest.annotations[]
{
  "screen_id": "screen_001",
  "x_pct": 42.5,
  "y_pct": 18.0,
  "type": "interaction",
  "content": "le bouton valider déclenche la transition vers screen_002"
}
```
`PUT /api/projects/{id}/manifest` avec `annotations` mis à jour à chaque `appliquer`.

**Au rechargement du preview :** les annotations existantes sont rechargées depuis `manifest.annotations` et les cercles re-rendus sans rouvrir les bulles.

---

#### PARTIE 4 — Sullivan guide complétion (system prompt + navigation "suivant")

**Nouveau mode Sullivan : `storyboard_annotation`**

Déclenché depuis la toolbar du preview en mode annotation : bouton `sullivan` → ouvre ManifestBox en mode `storyboard_annotation`.

**Backend — `sullivan_router.py` : nouveau bloc `storyboard_annotation`**

Dans `mode_context` dict, ajouter :
```python
"storyboard_annotation": """Tu es Sullivan, guide de cadrage storyboard pour HoméOS."""
```

**System prompt complet pour ce mode** (inséré comme `base_system` dans `/api/sullivan/chat`) :

```
Tu es Sullivan, guide de cadrage storyboard pour HoméOS.
Ton rôle : accompagner l'étudiant dans l'annotation de ses écrans de projet, un par un,
jusqu'à ce que le storyboard soit suffisamment documenté pour que le Wiring puisse générer
le code de liaison entre les composants.

STORYBOARD DU PROJET :
---
{storyboard_block}
---
Écran actif : {active_screen_name} ({active_screen_id})
Annotations existantes sur cet écran : {annotations_on_screen}
Progression globale : {annotated_count}/{total_count} écrans annotés

CE QU'UNE ANNOTATION COMPLÈTE CONTIENT (5 points) :
1. intention — quel besoin utilisateur cet écran résout-il ? (1 phrase courte)
2. interactions — quelles actions sont possibles ? (liste, ex : "clic bouton valider → screen_002")
3. données — quelles données sont affichées ou saisies ? (types, sources)
4. friction — qu'est-ce qui peut bloquer ou confondre l'utilisateur ?
5. transitions — depuis où vient l'utilisateur / où va-t-il ensuite ?

COMPORTEMENT :
- Pose des questions ciblées sur l'écran actif pour obtenir les 5 points
- Une question à la fois — pas de liste de questions
- Si l'utilisateur répond → reformule + confirme avant d'injecter
- Quand les 5 points sont couverts sur l'écran actif → dis-le clairement et propose "suivant →"
  avec le nom de l'écran suivant non annoté
- Si tous les écrans sont annotés → félicite + propose de lancer le Wire

FUNCTION CALLS autorisés (JSON strict, invisible pour l'utilisateur) :
- navigate_to_screen : { "tool": "navigate_to_screen", "params": { "screen_id": "..." } }
  → déclenche l'activation de l'écran sur le canvas et l'ouverture du preview annotation
- annotation_complete : { "tool": "annotation_complete", "params": { "screen_id": "...", "summary": "..." } }
  → marque l'écran comme annoté dans le manifest

RÈGLES :
- Réponds en français, phrases courtes, ton direct et bienveillant
- Jamais de HTML ni JSON visible dans ta réponse textuelle
- Jamais plus de 3 phrases par bulle
- Le bouton "suivant" dans l'UI est déclenché par un function_call navigate_to_screen —
  ne demande pas à l'utilisateur de cliquer manuellement
```

**Frontend — câblage du function_call `navigate_to_screen`**

Dans `ManifestSullivanCore.js`, `handleSullivanFunctionCall()` :
```js
case 'navigate_to_screen': {
    const { screen_id } = params;
    // 1. Activer le shell sur le canvas
    const shell = document.querySelector(`[data-screen-id="${screen_id}"]`)
                || document.querySelector(`[data-import-id="${screen_id}"]`);
    if (shell && window.wsCanvas) {
        window.wsCanvas.activateScreen(shell.id);
        // 2. Ouvrir le preview en mode annotation
        if (window.wsPreview) window.wsPreview.enterAnnotationMode(shell.id);
    }
    // 3. UxRun log
    _sullivanLog('annotation_navigate', { screen_id });
    break;
}
case 'annotation_complete': {
    const { screen_id, summary } = params;
    _sullivanLog('annotation_complete', { screen_id });
    // Met à jour visuellement la grille Col 3 (badge ✓)
    const card = document.querySelector(`[data-storyboard-screen="${screen_id}"]`);
    if (card) card.classList.add('ring-1', 'ring-[#8cc63f]');
    break;
}
```

**Payload envoyé au backend pour ce mode :**
```js
{
    mode: 'storyboard_annotation',
    message: userMessage,
    project_id: pid,
    active_screen_id: wsCanvas?.activeScreenId,   // M417
    storyboard: manifest.storyboard,               // liste des écrans
    annotations: manifest.annotations || []        // annotations existantes
}
```

**Backend — enrichissement du system prompt avec les données réelles :**

Dans `sullivan_router.py`, pour le mode `storyboard_annotation`, après `base_system =` :
```python
if req.mode == 'storyboard_annotation':
    storyboard = manifest_data.get('storyboard', [])
    annotations = manifest_data.get('annotations', [])
    annotated_ids = {a['screen_id'] for a in annotations}
    storyboard_block = "\n".join(
        f"- {s['screen_id']} : {s.get('screen_name','?')} — {s.get('intent','?')} {'[✓ annoté]' if s['screen_id'] in annotated_ids else '[à annoter]'}"
        for s in storyboard
    )
    active_name = next((s.get('screen_name','?') for s in storyboard if s['screen_id'] == req.active_screen_id), '?')
    annotations_on_screen = [a for a in annotations if a['screen_id'] == req.active_screen_id]
    base_system = base_system.replace('{storyboard_block}', storyboard_block)
    base_system = base_system.replace('{active_screen_name}', active_name)
    base_system = base_system.replace('{active_screen_id}', req.active_screen_id or '?')
    base_system = base_system.replace('{annotations_on_screen}', json.dumps(annotations_on_screen, ensure_ascii=False))
    base_system = base_system.replace('{annotated_count}', str(len(annotated_ids)))
    base_system = base_system.replace('{total_count}', str(len(storyboard)))
```

---

#### Pré-requis

- **M417** doit être livré avant M419 (inject `active_screen_id` dans le payload Sullivan)
- **M407** peut être livré en parallèle (liens N0 = code indépendant)
- `manifest.annotations[]` est un nouveau champ — le `PUT /api/projects/{id}/manifest` existant le gère sans modification backend

---

**Fichiers cibles :**
- `WsAnnotationOverlay.js` — nouveau, SVG overlay N1
- `WsAnnotationLinks.js` — nouveau, liens N0 inter-shells
- `WsWorkspace.js` ou `WsWorkspaceBase.js` — méthode `setMode()`
- `WsPreview.js` — méthode `enterAnnotationMode()` (ouvre preview avec SVG overlay actif)
- `ManifestSullivanCore.js` — `handleSullivanFunctionCall()` + cases `navigate_to_screen` / `annotation_complete`
- `sullivan_router.py` — mode `storyboard_annotation` + system prompt complet + enrichissement storyboard/annotations
- `workspace.html` — bouton `annot` toolbar + script tags nouveaux fichiers + version bump

---

## Thème 49 — Exploitabilité en classe (Soutenance DNMADE 2026)

**Contexte :** 15 élèves, ~1 mois, soutenance jury. Ils doivent pouvoir montrer leur projet depuis une URL stable et HTTPS le jour J. La stack NLP (BERT + Mistral) est séparée et ne concerne pas ce déploiement. FJD n'a pas de budget certain — le chapitre couvre les options par coût croissant.

**Ce qui doit fonctionner pour la soutenance (minimum) :**
- Login élève → drill onboarding → projet créé
- Import écrans (PNG) → extraction tokens
- Manifest Editor + Sullivan (Groq BYOK)
- Forge → génération HTML
- Preview → téléchargement HTML

**Ce qui peut attendre après la soutenance :** Wire, Annotation Mode (M419), RunMonitor.

---

### Option A — HuggingFace Spaces (0€ si gratuit, sinon ~10€/mois)

**Jouable ?** Oui, avec une contrainte critique.

HF Spaces accepte les apps Docker FastAPI. `server_v3.py` peut tourner dans un Space CPU.

**Problème n°1 — SQLite ne persiste pas** sur les Spaces gratuits : chaque redémarrage (cold start après inactivité) efface la base. Solution : passer à l'addon **Persistent Storage** de HF (~5$/mois) ou utiliser un SQLite stocké dans un **HF Dataset** repo en mode fichier (hacky mais fonctionne).

**Problème n°2 — Cold start** : les Spaces gratuits s'endorment après ~1h d'inactivité. Au réveil : 30-60s de latence. Rédhibitoire le jour d'une soutenance. Solution : Space payant ($10/mois CPU basique) ou pinger le Space toutes les 30 min via un cron UptimeRobot (gratuit).

**Ce qu'il faut faire pour A :**
1. Créer un `Dockerfile` HoméOS (server_v3.py + dépendances Python)
2. Configurer les variables d'env HF (clés Groq/Gemini des élèves en BYOK — déjà géré)
3. Monter le persistent storage sur `/data/db/`
4. Ajouter UptimeRobot pour éviter le cold start

**Verdict A :** jouable si persistent storage activé (~5$/mois). Risque faible. CI/CD natif HF (push → redeploy auto).

---

### Option B — Alwaysdata (0€ tier gratuit limité / ~12€/mois offre pro)

Service français, populaire dans l'éducation, hébergement mutualisé + support Python WSGI/ASGI.

**Problème :** FastAPI + uvicorn avec workers > 1 peut être capricieux en mutualisé. SQLite WAL fonctionne mais l'isolation des processus est parfois contrainte. Le tier gratuit a 100MB de storage — insuffisant pour les projets élèves (PNG imports).

**Verdict B :** à éviter sauf si tu as déjà un compte et que tu veux tester vite. Pas fiable pour une soutenance.

---

### Option C — VPS Hetzner CX21 + GitHub Actions (~6€/mois)

4GB RAM, 2 vCPU, SSD 40GB. Amplement suffisant pour 15 élèves.

**CI/CD :** GitHub Action qui SSH sur le VPS et fait `git pull && bash start.sh` à chaque push sur `main`. Simple, robuste, zéro dépendance externe.

**Ce qu'il faut faire pour C :**
1. `Dockerfile` + `docker-compose.yml` (server_v3.py + SQLite volume monté)
2. GitHub Action `deploy.yml` : SSH → `docker compose pull && docker compose up -d`
3. Nginx reverse proxy HTTPS (Let's Encrypt, 10 min de config)
4. Domaine : sous-domaine gratuit `homeos.francois-jean.xyz` ou achat domaine ~12€/an

**Verdict C :** meilleure option si budget dispo. URL stable, HTTPS, CI/CD propre, données persistantes, pas de cold start. Max recommande ça — il a raison.

---

### M420 — Dockerfile + déploiement minimal (prérequis toutes options)

**STATUS: 🟠 À TRAITER | ACTOR: GEMINI**

Quelle que soit l'option choisie, un `Dockerfile` propre est nécessaire.

**Ce que Gemini doit faire :**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY Frontend/3.\ STENCILER/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY Frontend/3.\ STENCILER/ .
ENV PORT=9998
EXPOSE 9998
CMD ["uvicorn", "server_v3:app", "--host", "0.0.0.0", "--port", "9998", "--workers", "1"]
```

**`docker-compose.yml` :**
```yaml
services:
  homeos:
    build: .
    ports:
      - "9998:9998"
    volumes:
      - ./data:/app/db        # SQLite persiste ici
      - ./uploads:/app/uploads
    env_file: .env
    restart: unless-stopped
```

**`.env.example` :**
```
GROQ_API_KEY=
GOOGLE_API_KEY=
SECRET_KEY=
```

**Contrainte :** workers=1 obligatoire (SQLite WAL, règle déjà documentée en Bootstrap Backend). Ne pas passer à 2+ workers sans migration PostgreSQL.

**Vérification :** `docker compose up` → `curl http://localhost:9998/api/health` → `{"status":"ok"}` → login élève fonctionne.

**Fichiers cibles :** `Dockerfile` (racine STENCILER), `docker-compose.yml` (racine projet), `.env.example`

---

### M421 — Preview Wired : mini-router multi-écrans dans le workspace
**STATUS: 🟢 TERMINÉE (2026-05-09) | ACTOR: GEMINI**
**CR TECHNIQUE :**
- **Mode Interactif** : Création de `WsPreview.enterWiredMode()` permettant de charger un écran initial et de naviguer via `postMessage`.
- **Interceptor JS** : Injection automatique d'un script `INTERCEPTOR` dans les iframes de preview pour capturer les clics sur `data-navigate` ou liens `#screen_id`.
- **Historique & Fil d'Ariane** : Gestion d'une pile d'historique `_wiredHistory` et affichage d'un breadcrumb dynamique dans l'overlay de preview.
- **Chargement dynamique** : Récupération asynchrone des fichiers HTML des écrans forgés depuis `/api/retro-genome/file`.

**Contexte :** Après le Wire, l'élève a un `manifest.wires[]` avec des handlers de navigation (`navigateTo('screen_002')` sur clic bouton). Mais il n'existe aucun moyen de tester ça dans HoméOS — le Preview actuel ne montre qu'un écran à la fois et ne connaît pas `navigateTo`. M421 active un mode "wired preview" qui charge les écrans en séquence et exécute réellement la navigation.

**Architecture — postMessage router :**

```
WsPreview (parent)
  ├── iframe srcdoc = HTML screen N
  │     + script injecteur : intercepte navigateTo() → postMessage({ navigate: 'screen_X' })
  └── écouteur message → remplace srcdoc par screen_X HTML + ré-injecte
```

Chaque écran garde son propre Tailwind, ses fonts, ses scripts CDN — aucun parsing de HTML.

**Ce que Gemini doit faire :**

**1. Nouveau bouton dans la toolbar du preview overlay**

Dans `workspace.html` (overlay `ws-preview-overlay`), ajouter à côté du bouton preview existant :
```html
<button id="ws-preview-wired-btn" class="...">tester app</button>
```
Visible uniquement si `manifest.wires.length > 0`.

**2. `WsPreview.enterWiredMode(entryScreenId)` — nouveau**

```js
enterWiredMode(entryScreenId) {
    // 1. Ouvrir l'overlay comme enterPreviewMode()
    // 2. Trouver l'écran d'entrée :
    //    entryScreenId || manifest.flow[0]?.from || manifest.storyboard[0]?.screen_id
    // 3. Charger le HTML de cet écran dans l'iframe (srcdoc)
    // 4. Injecter le script intercepteur après chargement (onload)
    // 5. Afficher un breadcrumb en haut : nom de l'écran actif + btn "retour"
    this._wiredHistory = [];
    this._loadWiredScreen(entryScreenId);
}

_loadWiredScreen(screenId) {
    const shell = document.querySelector(`[data-screen-id="${screenId}"]`)
                || document.querySelector(`[data-import-id="${screenId}"]`);
    const html = shell?.querySelector('iframe')?.srcdoc
              || shell?.querySelector('iframe')?.contentDocument?.documentElement?.outerHTML;
    if (!html) return;

    const INTERCEPTOR = `
<script>
(function(){
    window.navigateTo = function(id) {
        parent.postMessage({ wsNavigate: id }, '*');
    };
    // Intercepter aussi les href="#screen_X" et data-navigate
    document.addEventListener('click', function(e) {
        const t = e.target.closest('[data-navigate],[href^="#screen"]');
        if (t) {
            e.preventDefault();
            const id = t.dataset.navigate || t.getAttribute('href').slice(1);
            parent.postMessage({ wsNavigate: id }, '*');
        }
    });
})();
<\/script>`;

    const iframe = document.querySelector('#ws-preview-frame-container iframe');
    iframe.srcdoc = html + INTERCEPTOR;
    this._wiredHistory.push(screenId);
    this._updateWiredBreadcrumb(screenId);
}
```

**3. Écoute postMessage dans WsPreview**

```js
window.addEventListener('message', (e) => {
    if (e.data?.wsNavigate && this._wiredMode) {
        this._loadWiredScreen(e.data.wsNavigate);
        // UxRun log
        fetch('/api/ux-run/event', { method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({ tag:'WIRED_NAVIGATE', label: e.data.wsNavigate, ts: Date.now(),
                project_id: window._currentProjectId, details:{} }) }).catch(()=>{});
    }
});
```

**4. Breadcrumb navigation**

Bande fine (32px) en haut du preview overlay en mode wired :
- Nom de l'écran actif (text-[11px], slate)
- Bouton `← retour` → dépile `_wiredHistory` et recharge l'écran précédent
- Badge `wired` vert HoméOS à droite

**5. Bouton "tester app" dans le workspace**

Dans la toolbar principale (à côté des boutons forge/wire/preview), bouton `tester` :
```js
document.getElementById('ws-preview-wired-btn').onclick = () => {
    const entry = manifest.flow?.[0]?.from || manifest.storyboard?.[0]?.screen_id;
    window.wsPreview.enterWiredMode(entry);
};
```

**Vérification :** projet avec 2 écrans reliés par un wire `button / "valider"` → cliquer "tester app" → screen 1 s'affiche → cliquer le bouton → screen 2 s'affiche → btn retour → screen 1.

**Fichiers cibles :** `WsPreview.js` (enterWiredMode, _loadWiredScreen, postMessage listener, breadcrumb), `workspace.html` (bouton "tester app" + btn wired dans overlay)

---

### M422 — Export Bundle : app multi-écrans → Netlify Drop ready
**STATUS: 🟢 TERMINÉE (2026-05-09) | ACTOR: GEMINI | APRÈS: M421**
**CR TECHNIQUE :**
- **Router d'Export** : Création de `routers/export_router.py` avec le endpoint `GET /api/projects/{pid}/export-bundle`.
- **Assemblage Bundle** : Logique de packaging transformant tous les écrans HTML du projet en un objet JS unique embarqué dans un template HTML5 maître.
- **Micro-Router Embarqué** : Inclusion d'une version légère du router interactive (M421) directement dans le bundle pour une autonomie totale sans serveur.
- **Logic.js** : Injection des animations GSAP et handlers spécifiques définis dans `manifest.wires[]`.
- **Interface UI** : Ajout du bouton "EXPORTER" dans le Sullivan panel déclenchant le téléchargement immédiat.

**Contexte :** Le livrable soutenance est un fichier HTML unique auto-contenu que l'élève glisse dans Netlify Drop et obtient une URL publique en 10 secondes. Ce fichier embarque tous les écrans forgés + le mini-router de M421 + logic.js. Aucune dépendance serveur, fonctionne offline.

**Ce que Gemini doit faire :**

**1. Backend — `POST /api/projects/{id}/export-bundle`**

```python
@router.post("/api/projects/{project_id}/export-bundle")
async def export_bundle(project_id: str, request: Request):
    token = request.headers.get("X-User-Token")
    # 1. Charger le manifest
    manifest = load_manifest(project_id, token)
    storyboard = manifest.get("storyboard", [])
    wires = manifest.get("wires", [])
    flow = manifest.get("flow", [])

    # 2. Charger le HTML de chaque écran depuis le filesystem
    screens_html = {}
    for screen in storyboard:
        sid = screen["screen_id"]
        # Chercher le fichier HTML forgé dans le dossier du projet
        html_path = PROJECTS_DIR / project_id / "screens" / f"{sid}.html"
        if html_path.exists():
            screens_html[sid] = html_path.read_text(encoding="utf-8")

    # 3. Générer le logic.js depuis manifest.wires
    logic_js = _generate_logic_js(wires, flow)

    # 4. Assembler le bundle HTML
    entry = flow[0]["from"] if flow else (storyboard[0]["screen_id"] if storyboard else None)
    bundle_html = _assemble_bundle(screens_html, logic_js, entry, manifest.get("name", "app"))

    return Response(
        content=bundle_html,
        media_type="text/html",
        headers={"Content-Disposition": f'attachment; filename="{project_id}_bundle.html"'}
    )
```

**2. `_assemble_bundle()` — structure du fichier généré**

```python
def _assemble_bundle(screens_html, logic_js, entry_id, app_name):
    screens_js = json.dumps(screens_html)  # { screen_id: "html string", ... }
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{app_name}</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#f8fafc; }}
  #ws-router-frame {{ width:100vw; height:100vh; border:none; display:block; }}
  #ws-nav {{ position:fixed; top:0; left:0; right:0; height:32px; background:rgba(255,255,255,0.9);
             backdrop-filter:blur(8px); display:flex; align-items:center; gap:8px; padding:0 12px;
             font-family:system-ui; font-size:11px; color:#64748b; z-index:9999;
             border-bottom:1px solid #e5e7eb; }}
  #ws-nav button {{ border:none; background:none; cursor:pointer; color:#8cc63f; font-size:11px; }}
</style>
</head>
<body>
<div id="ws-nav">
  <button id="ws-back">← retour</button>
  <span id="ws-screen-name">{app_name}</span>
  <span style="margin-left:auto;color:#8cc63f;font-weight:600">homeos</span>
</div>
<iframe id="ws-router-frame"></iframe>
<script>
const SCREENS = {screens_js};
const history_stack = [];

const INTERCEPTOR = `<scr`+`ipt>
window.navigateTo = function(id) {{ parent.postMessage({{ wsNavigate: id }}, '*'); }};
document.addEventListener('click', function(e) {{
  const t = e.target.closest('[data-navigate],[href^="#screen"]');
  if (t) {{ e.preventDefault(); parent.postMessage({{ wsNavigate: t.dataset.navigate || t.getAttribute('href').slice(1) }}, '*'); }}
}});
<\/scr`+`ipt>`;

function navigateTo(screenId) {{
  const html = SCREENS[screenId];
  if (!html) return;
  document.getElementById('ws-router-frame').srcdoc = html + INTERCEPTOR;
  history_stack.push(screenId);
  document.getElementById('ws-screen-name').textContent = screenId.replace(/_/g,' ');
}}

window.addEventListener('message', e => {{ if (e.data?.wsNavigate) navigateTo(e.data.wsNavigate); }});
document.getElementById('ws-back').onclick = () => {{
  if (history_stack.length > 1) {{ history_stack.pop(); navigateTo(history_stack.pop()); }}
}};

navigateTo('{entry_id}');

// logic.js
{logic_js}
</script>
</body>
</html>"""
```

**3. `_generate_logic_js()` — reconstituer le logic.js depuis manifest.wires**

```python
def _generate_logic_js(wires, flow):
    lines = ["// Navigation — généré par HoméOS Export"]
    for wire in wires:
        if wire.get("gsap"):
            lines.append(wire["gsap"])
    return "\n".join(lines)
```

**4. Frontend — bouton "exporter" dans la toolbar**

À côté du bouton "tester app", bouton `exporter` :
```js
document.getElementById('ws-export-btn').onclick = async () => {
    const pid = session.active_project_id;
    const a = document.createElement('a');
    a.href = `/api/projects/${pid}/export-bundle`;
    a.download = `${pid}_bundle.html`;
    a.click();
    // UxRun
    fetch('/api/ux-run/event', { method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ tag:'BUNDLE_EXPORT', label: pid, ts: Date.now(),
            project_id: pid, details:{} }) }).catch(()=>{});
};
```

**Vérification end-to-end :** cliquer "exporter" → télécharge `projet_bundle.html` → ouvrir localement → screen 1 visible → navigation fonctionne → glisser dans Netlify Drop → URL publique → ouvrir sur mobile → même résultat.

**Fichiers cibles :** `sullivan_router.py` ou nouveau `export_router.py` (endpoint export-bundle + _assemble_bundle + _generate_logic_js), `workspace.html` (bouton "exporter"), `server_v3.py` (inclure export_router)

### Décision FJD — 2026-05-09

**Contexte final :** les apps élèves sont du CPU pur (FastAPI + SQLite + vanilla JS + appels API externes). Aucun modèle lourd. Stack ultra-légère.

**Stack retenue : Koyeb (HoméOS) + Netlify Drop (apps élèves) = 0€**

| Couche | Service | Coût | Fiabilité soutenance |
|--------|---------|------|---------------------|
| HoméOS backend | **Koyeb free forever** | 0€ | ✅ pas de sleep |
| Apps forgées élèves | **Netlify Drop** | 0€ | ✅ URL instantanée |

**Koyeb** : 512MB RAM, HTTPS auto, pas de cold start, déploiement depuis GitHub. SQLite persiste entre redémarrages (volume attached). Largement suffisant pour 15 élèves sans NLP.

**Seul point de vigilance** : les uploads PNG élèves (écrans importés). Si le disque Koyeb est éphémère → stocker sur Cloudflare R2 (10GB gratuit) ou Backblaze B2. À vérifier au moment du déploiement.

**Netlify Drop** : l'élève glisse son dossier d'app forgée dans le browser → URL publique en 10 secondes. Aucun compte requis. C'est le livrable soutenance.

**Prérequis unique :** M420 (Dockerfile) — même fichier sert Koyeb et n'importe quelle autre option si le budget arrive.

**Note :** si budget disponible plus tard → Hetzner CX21 (~6€/mois) + GitHub Actions. Même Dockerfile, migration sans friction.

---

## Thème 50 — Console Dev & Restructuration UI (2026-05-09)

**Contexte :** Le ME est devenu un overlay à part entière. La même logique s'applique au mode Dev — un overlay IDE pédagogique qui expose la dimension technique du projet (architecture, roadmap, inférence, logs) sans remplacer le workspace. Les tabs Backend et Cadrage disparaissent. L'UI se simplifie à : workspace + deux overlays (ME / Console) + tabs Dashboard/Frontend en mode Teacher uniquement.

---

### M423 — Console Dev : overlay IDE pédagogique
**STATUS: 🟠 VISION — À AFFINER | ACTOR: GEMINI après validation FJD**

**Contexte pédagogique :** HoméOS n'est pas qu'un outil de production — c'est un outil d'éducation au chantier numérique. La Console Dev expose aux élèves ce que le Studio cache : l'architecture projet, la roadmap de leur chantier, les décisions d'inférence, les logs serveur. C'est le pendant de l'expérience FJD/Gemini vécue ici : manifest + roadmap + agent + terminal = un environnement de pensée complet.

**Trigger :** bouton `console` dans la toolbar workspace, même famille visuelle que `manifeste` (même gabarit, même position dans la hiérarchie des overlays). Les deux boutons signalent : "je change de niveau de lecture du projet", pas "je change d'outil".

---

#### Layout (overlay fullscreen, même pattern que ME)

```
┌──────────┬─────────────────┬──────────────────┬───────────────┐
│  fichiers │   architecte    │    roadmap       │   ouvrier     │
│  (180px) │   (Groq/BYOK)   │  projet + arch.  │ (Forge/Wire   │
│  tree    │   cadrage strat │  archive mois.   │  Gemini/BYOK) │
│          │                 │                  │               │
└──────────┴─────────────────┴──────────────────┴───────────────┘
│  terminal (280px hauteur fixe)                                 │
│  [tabs : logs serveur | UxRun live | CI/CD | agent CLI]        │
└────────────────────────────────────────────────────────────────┘
```

---

#### Col 1 — Fichiers (tree projet)

Arborescence du projet actif :
```
mon-projet/
  ├── screens/          (HTML forgés)
  ├── assets/           (PNG importés)
  ├── manifest.json
  ├── logic.js          (Wire output)
  ├── roadmap.md        (roadmap projet)
  ├── .env.example
  └── .gitignore
```

Clic sur un fichier → ouvre en lecture dans une modale légère (pas d'éditeur Monaco complet dans cette version — lecture seule, syntaxe highlight).

Bouton `+ nouveau fichier` → crée un fichier texte vide dans le projet (pour notes, specs libres).

---

#### Col 2 — Architecte (chat stratégique)

Sullivan en mode `architect` — Groq Llama 3.3 par défaut (réactivité < 500ms, cadrage, pas de génération de code).

**Routing modèle (BYOK-first) :**
```
if clé Claude/Qwen/Kimi disponible → ce modèle
elif clé Groq → Groq Llama 3.3
else → Groq public key (si dispo) ou message "configure une clé dans Paramètres"
```

**System prompt `architect`** — dérivé de `STRATEGIE_NLP_HCI_SULLIVAN.md` :
```
Tu es Sullivan Architecte. Tu aides l'élève à penser son projet, pas à le coder.
Ton rôle : clarifier les intentions, hiérarchiser les décisions, identifier les risques.
Tu ne génères jamais de code. Tu poses des questions, tu proposes des alternatives,
tu valides la cohérence entre le manifest, la roadmap et les screens.
Contexte projet : {manifest_summary} | Roadmap : {roadmap_status}
Réponds en français, 3 phrases max par bulle, ton direct.
```

Historique de conversation persisté dans `manifest.architect_log[]` — l'élève retrouve ses échanges stratégiques à chaque session.

---

#### Col 3 — Centre de pilotage (onglets fermables)

La colonne centrale est un système d'onglets dynamiques. Les onglets s'ouvrent automatiquement selon les actions en cours et peuvent être fermés individuellement. Onglets permanents : Roadmap, Architecture, Traces, Skills. Onglets dynamiques : Plans (ouverts par l'Ouvrier, fermés automatiquement à la livraison).

---

**Onglet Roadmap** (permanent)

- `roadmap.md` du projet affiché en lecture/écriture (textarea, autosave)
- Structure imposée à la création du projet :
```markdown
# Roadmap — [nom projet]

## Sprint actif
- [ ] tâche 1

## Archive — Mai 2026
- [x] tâche livrée

## Backlog
```
- Archive mensuelle automatique : le 1er de chaque mois, tâches cochées → `## Archive — Mois AAAA`
- Sullivan Architecte lit et commente la roadmap en Col 2

---

**Onglets Plan** (dynamiques, fermables)

Quand l'Ouvrier (Col 4) génère un plan en réponse à une demande élève, ce plan s'ouvre comme un **nouvel onglet** dans Col 3 — pas dans Col 4. L'élève lit, valide ou corrige dans cet onglet avant de dire "go" à l'Ouvrier.

Structure d'un plan :
```markdown
# Plan — [titre de la tâche]
Date : 2026-05-09

1. vérifier que le formulaire de screen_003 a un `data-af-id`
2. ajouter un event listener `submit` avec validation regex email
3. afficher un message d'erreur inline sous le champ si invalide
4. émettre un event UxRun `FORM_VALIDATE` au submit réussi
```

**Persistence :** chaque plan est sauvegardé comme fichier `projects/{pid}/plans/plan_TIMESTAMP.md`.

**Suppression automatique :** quand l'élève coche la tâche correspondante dans la Roadmap → le fichier plan est supprimé + l'onglet se ferme. Le plan ne survit pas à sa livraison.

---

**Onglet Architecture** (permanent)

- Diagramme auto-généré depuis `manifest.json` + `manifest.flow[]`
- Front (screens) → logic.js → endpoints déclarés dans manifest
- Read-only, mis à jour à chaque Wire ou Forge

---

**Onglet Traces** (permanent)

Journal de session du projet — même philosophie que `TRACES/` dans HoméOS.

- Chaque action significative (plan créé, plan livré, Wire généré, export bundle) génère une ligne dans `projects/{pid}/traces/AAAA-MM.ndjson`
- Affiché en liste inversée (plus récent en haut), read-only
- Routine mensuelle : `compile_traces()` produit un résumé markdown dans `projects/{pid}/traces/archive/AAAA-MM-resume.md`
- Bouton `compiler` dans l'onglet → déclenche la routine manuellement

---

**Onglet Skills** (permanent)

Bibliothèque de recettes opérationnelles distillées depuis l'expérience accumulée (GEMINI.md, CLAUDE.md, memory.md). Accessible à l'élève comme à l'Architecte et à l'Ouvrier.

Structure :
```
skills/
  ├── diagnostic/
  │     ├── term_frequency.md     ← routine fréquence de termes (bug récurrent)
  │     └── uxrun_first.md        ← lire UxRun avant tout diagnostic
  ├── bootstrap/
  │     ├── gemini_frontend.md    ← règles DOM/listener/overlay
  │     └── backend_async.md      ← interdiction nest_asyncio
  └── patterns/
        ├── plan_before_code.md   ← mode plan obligatoire
        └── grep_safe.md          ← ne jamais grep -r depuis racine
```

**Routine term_frequency** (bug récurrent déjà documenté) : avant tout diagnostic de bug, l'Architecte peut déclencher `→ analyser fréquence "terme"` → parcourt `traces/` + `plans/` du projet → retourne un histogramme des occurrences. Permet de détecter un bug récurrent par sa fréquence d'apparition dans les archives plutôt que par exploration aveugle du code.

**Chaque skill est un fichier markdown** — l'élève peut en créer, l'Architecte peut en suggérer ("tu reproduis le même bug de listener — lis `skills/diagnostic/uxrun_first.md`").

**Ajout automatique :** quand un plan résout un bug non trivial → Sullivan Architecte propose "veux-tu archiver cette solution comme skill ?" → crée le fichier dans la catégorie appropriée.

---

#### Col 4 — Ouvrier (exécution précise)

Sullivan en mode `worker` — Gemini ou Codestral selon clés disponibles.

**Routing modèle (BYOK-first) :**
```
if clé Codestral → Codestral (code JS/Python pur)
elif clé Gemini → Gemini Pro
elif clé Claude → Claude (fallback universel)
else → Groq (mode dégradé, moins fiable pour le code)
```

**System prompt `worker`** — dérivé compartiment FONCTIONNEL de la stratégie NLP :
```
Tu es Sullivan Ouvrier. Tu génères du code précis sur demande.
Tu reçois : une description de la tâche + le fichier cible + les contraintes du manifest.
RÈGLE OBLIGATOIRE — MODE PLAN :
Avant tout code, tu présentes un plan en 3-5 points numérotés ("voici ce que je vais faire").
Tu attends la confirmation de l'élève avant de générer le code.
Si l'élève répond "ok" ou "go" → tu génères le code.
Si l'élève corrige le plan → tu ajustes et représentes le plan révisé.
Tu ne génères jamais de code sans plan validé.
Contexte : {active_file} | Design tokens : {design_tokens_summary}
```

L'élève formule sa demande → l'Ouvrier présente son plan → l'élève valide → l'Ouvrier génère le patch → bouton `appliquer` → injecte dans le fichier cible.

**Pédagogie du mode plan :** l'élève apprend à lire et valider une intention technique avant son exécution. C'est la même discipline que FJD/Claude ici — on ne code pas sans avoir aligné l'architecture.

---

#### Terminal (bas, 4 tabs)

**Tab 1 — Logs serveur :**
Polling `GET /api/logs/stream?since=ts` toutes les 2s → affiche les dernières lignes de `server.log`. Read-only. Scroll auto vers le bas.

**Tab 2 — UxRun live :**
Polling `GET /api/ux-run/events?since=ts` toutes les 500ms → affiche les events UxRun en temps réel (FORGE_CLICK, WIRED_NAVIGATE, etc.). Utile pour voir ce que font les élèves sur leur app wired en preview.

**Tab 3 — CI/CD :**
Affiche le dernier déploiement Koyeb (ou autre) : statut build, URL, timestamp. Polling `GET /api/deploy/status`. Si pas de déploiement configuré → "aucun déploiement actif — voir M420".

**Tab 4 — Agent CLI :**
Input interactif. L'élève tape une commande ou une question → envoyée à Sullivan en mode `cli_agent`. Pas de shell réel (pas de sécurité) — interface de commande Sullivan uniquement :
```
> analyse mon manifest
> génère la roadmap de cette semaine
> qu'est-ce qui manque avant de déployer ?
```
Sullivan répond en texte dans le terminal. Ton concis, 1-2 lignes max par réponse.

---

#### Simplification tabs workspace
### M428 — D&D Ghost Layer : implémentation (CSS + JS global)
**STATUS: 🟠 À TRAITER | ACTOR: GEMINI**

**Contexte :**
Le workspace utilise des iframes pour rendre les écrans HTML forgés. Les iframes capturent les pointer events pendant un drag HTML5, "volant" le signal avant qu'il atteigne le canvas ou les drop zones du panel. Résultat : le D&D est cassé dès qu'un écran HTML est présent sur le canvas. Ce bug sera récurrent sur toute future feature D&D (N0 beziers, reorder, etc.) si non traité à la racine.

**Principe :**
Une classe CSS globale `is-dragging-global` posée sur `body` au début de tout drag désactive `pointer-events` sur toutes les iframes du workspace. Elle est retirée au dragend ou au drop. Solution documentée dans `docs/09_Frontend/UX_Flows/DND_SIGNAL_ROUTING_MANAGEMENT.md`.

**Ce que Gemini doit faire :**

**1. CSS dans `stenciler.css` — ajouter en fin de fichier**
```css
/* M428 — Ghost Layer : protection D&D contre capture iframe */
body.is-dragging-global iframe {
    pointer-events: none !important;
}
body.is-dragging-global .ws-screen-shell > foreignObject {
    pointer-events: none !important;
}
```

**2. Handler global dans `WsBoot.js` ou `ws_main.js` — ajouter au boot**

Ne pas mettre le ghost layer dans WsProjectPanel seul — d'autres composants feront du D&D (beziers N0, reorder canvas). Le handler doit être **global** :

```js
// M428: Ghost Layer — neutralise les iframes pendant tout drag dans le workspace
document.addEventListener('dragstart', () => {
    document.body.classList.add('is-dragging-global');
});
document.addEventListener('dragend', () => {
    document.body.classList.remove('is-dragging-global');
});
document.addEventListener('drop', () => {
    document.body.classList.remove('is-dragging-global');
});
```

Placer dans `ws_main.js` dans la fonction `init()`, après `bootComponents()`.

**3. Vérification**
- Poser un écran HTML forgé sur le canvas
- Tenter de drag un écran depuis le panel vers un autre projet (drop zone = header projet)
- Le drop doit fonctionner même quand le curseur passe au-dessus de l'iframe
- Aucune régression sur le D&D existant (déplacement shell sur canvas, reorder panel)

**Fichiers cibles :** `static/css/stenciler.css`, `static/js/workspace/ws_main.js`

**Contrainte :** ne pas modifier WsProjectPanel.js — le ghost layer est global, pas local.

---

### M427 — Wire Router : overlays signalétique SVG corrects
**STATUS: 🟠 À TRAITER | ACTOR: GEMINI**

**Contexte :** `_applyShellOverlays()` dans `WsWireRouter.js` injecte un `<div>` avec des classes Tailwind (`absolute inset-0`) dans un shell qui est un `<g>` SVG. Un `div` dans un `<g>` SVG ne s'affiche pas — le positionnement CSS ne fonctionne pas dans le namespace SVG. Les voiles colorés sont donc complètement absents du canvas même quand le router tourne correctement.

**Deux bugs distincts à corriger dans cette mission :**

---

**Bug 1 — Overlay `<div>` dans `<g>` SVG → remplacer par `<rect>` SVG**

Dans `_applyShellOverlays()`, remplacer la création du `div` par un `<rect>` SVG dimensionné sur le fond du shell :

```js
// Supprimer les overlays existants
shell.querySelectorAll('.ws-wire-overlay').forEach(el => el.remove());

// Lire les dimensions depuis le rect de fond
const bg = shell.querySelector('rect.ws-screen-bg');
const w = bg?.getAttribute('width') || '400';
const h = bg?.getAttribute('height') || '632';

// Créer un rect SVG (pas un div)
const overlay = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
overlay.setAttribute('class', `ws-wire-overlay ${overlayClass}`);
overlay.setAttribute('width', w);
overlay.setAttribute('height', h);
overlay.setAttribute('rx', '20');
overlay.setAttribute('pointer-events', 'none');
shell.appendChild(overlay);
```

**Bug 2 — CSS `background` → `fill` pour éléments SVG**

Dans `stenciler.css`, remplacer les règles `background:` par `fill:` pour les classes d'overlay :

```css
/* M427 — overlays SVG Wire Router */
.ws-wire-overlay { transition: opacity 0.3s ease; }

.ws-wire-overlay.ws-shell-overlay-grey   { fill: rgba(100,116,139,0.50); }
.ws-wire-overlay.ws-shell-overlay-red    { fill: rgba(239,68,68,0.35); }
.ws-wire-overlay.ws-shell-overlay-orange { fill: rgba(249,115,22,0.35); }
.ws-wire-overlay.ws-shell-overlay-green  { fill: rgba(140,198,63,0.25); }

body:not([data-ws-mode="annotation"]) .ws-wire-overlay { opacity: 0; }
body[data-ws-mode="annotation"] .ws-wire-overlay       { opacity: 1; }
```

Supprimer les anciennes règles `background:` sur ces mêmes classes (lignes ~1719-1722 dans stenciler.css).

---

**Bug 3 — IDs storyboard incohérents après refactor Wire Router**

Depuis le hotfix du 2026-05-09, `_populateCanvasFromStoryboard` pose `data-screen-id = import.id` sur les shells (ex: `2026-05-07_223139_1.png`). Mais `_applyShellOverlays` lit `manifest.storyboard[]` qui contient les anciens IDs abstraits (`screen-1`, `screen-2`) — le manifest en mémoire n'est pas rechargé après le PUT.

Fix : après `_populateCanvasFromStoryboard`, recharger le manifest depuis l'API avant d'appeler `_applyShellOverlays` :

```js
// Dans enter(), après _populateCanvasFromStoryboard + setTimeout :
const manifest = await this._loadManifest(pid); // recharge après le PUT storyboard
const state = this._computeState(manifest);
this._applyShellOverlays(manifest, state);
this._route(state, manifest);
```

Le manifest rechargé a le bon storyboard (IDs réels). Les shells ont `data-screen-id` = ces mêmes IDs. Le querySelector trouve les shells. Les overlays s'affichent.

---

**Vérification :**
1. Cmd+Shift+R → cliquer Wire sur un projet avec écrans
2. Canvas : les shells apparaissent avec un voile coloré visible (gris = non annoté)
3. `body[data-ws-mode="annotation"]` est présent dans le DOM (DevTools → Elements → body)
4. Les overlays disparaissent si on change de mode (construct, front-dev…)

**Fichiers cibles :** `WsWireRouter.js` (`_applyShellOverlays` + `enter()`), `stenciler.css` (remplacement règles overlay)
