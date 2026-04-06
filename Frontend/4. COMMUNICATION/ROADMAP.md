# MISSION CONTROL : AETHERFLOW ROADMAP

> Missions complètes archivées dans [ROADMAP_ACHIEVED.md](./ROADMAP_ACHIEVED.md).

---

## 🧠 BOOTSTRAP GEMINI — À inclure dans TOUTE mission frontend

> Copier-coller ce bloc en tête de chaque mission ACTOR: GEMINI touchant au DOM, aux événements ou aux overlays.

```
CONTEXTE TECHNIQUE OBLIGATOIRE — lis avant de coder :

1. DIAGNOSTIC DOM AVANT LISTENER
   Avant d'ajouter un event listener, remonte la chaîne du DOM :
   - Quel élément est réellement cliqué ? (e.target)
   - Y a-t-il un élément enfant `absolute inset-0` qui intercepte les clics avant le parent ?
   - Si oui → ajouter `pointer-events-none` sur l'intercepteur, puis le listener sur le parent.
   - Tester avec : `element.addEventListener('click', e => console.log(e.target))` avant tout patch.

2. OVERLAYS & Z-INDEX
   Un overlay `hidden` sur un parent = ses enfants sont invisibles même si LEUR hidden est retiré.
   Toujours vérifier : `getComputedStyle(el).display` et `el.offsetHeight` avant de déboguer le JS.
   Un `display:none` sur le parent écrase tout — le z-index n'y change rien.

3. RÈGLE DE LIVRAISON
   Ne pas marquer TERMINÉ avant d'avoir testé manuellement le comportement dans le browser.
   Si tu ne peux pas tester visuellement → décrire précisément le test manuel attendu dans le rapport.

4. SCOPE STRICT
   Ne pas refactoriser les fichiers existants stables (WsChat.js, WsCanvas.js, ws_main.js) sans
   instruction explicite. Créer de nouveaux fichiers plutôt que modifier les fichiers en production.

5. STYLE HOMÉOS
   Pas de majuscules dans les labels UI. Pas d'emojis. Border-radius max `rounded-[20px]`.
   Vert HoméOS (#8cc63f) uniquement en nudge (bordure, point, icône active) — jamais en fond large.
```

---

## Phase Active (2026-04-03)

### Thème 0 — Hotfixes
> M121 ✅, M116 ✅, M122 ✅, M123 ✅, M124 ✅, M125 ✅, M126 ✅, M127 ✅ — archivées dans ROADMAP_ACHIEVED.md (2026-04-01)

---

### Thème 7 — Drill : Manifeste → Wire → Cadrage

### Mission 188 — Wire : Aperçu fonctionnel post-forge
**STATUS: 🟠 PRÊTE**
**DATE: 2026-04-06**
**ACTOR: GEMINI**

**Contexte :** Après forge, le template wiré est sauvegardé dans `static/templates/{name}`. L'iframe se recharge via `iframe.src = iframe.src`. Mais le tracker est ré-injecté et bloque les clics. Il faut un mode "test live" sans tracker.

**Objectif :** Bouton "tester" dans l'overlay Wire post-forge → ouvre `http://localhost:9998/api/frd/file?name={template_name}&raw=1&wire=1` dans un nouvel onglet. Ce paramètre `wire=1` indique au serveur de ne pas injecter le tracker.

**Fichiers à modifier :**
- `server_v3.py` : route `GET /api/frd/file` — si `wire=1`, retourner le HTML brut sans injection tracker (le wire_runtime est déjà dans le HTML forgé)
- `WsWire.js` : après `_executeForge` succès, afficher un bouton "ouvrir aperçu" qui fait `window.open(previewUrl)`

**Contraintes :**
- Le bouton "ouvrir aperçu" n'ouvre pas automatiquement (popup blocker). C'est un bouton cliquable dans l'overlay Wire.
- `window.open` appelé directement depuis un click handler = pas bloqué par le browser.
- Le `template_name` est connu depuis `new URL(iframe.src).searchParams.get('name')`.

**Livrable :** Cliquer "tester" → nouvel onglet → template interactif avec toasts Groq fonctionnels.

### Mission 147 — Wire : Bilan de Santé & Maillage (CLEA UX)
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-05**

> [!IMPORTANT]
> **CR TECHNIQUE (Mission 147)** :
> - **Refactoring WsChat** : Architecture modulaire splitée en `WsChatBase`, `WsChatMain` et `WsChatSurgical`.
> - **Diagnostic Global (Bilan de Santé)** : Overlay WiRE repensé en deux colonnes (Audit Organes vs Plan de Maillage Émotionnel).
> - **Sullivan de Flanc (Chirurgical)** : Popover draggable apparaissant au clic sur un élément dans l'iframe pour un audit ciblé.
> - **Terminologie CLEA** : Intégration totale du lexique (Organe, Fonction, Pont Serveur, Maillage) dans le backend et l'UI.
> - **Édition Directe** : Bouton "ÉDITER LE CODE" (uppercase, vert actif, radius 20px) ouvrant Monaco sur le sélecteur précis.

---

### Mission 149 — Canvas N0 : États de sélection + toolbar opérationnelle
**STATUS: 🟠 PRÊTE**
**DATE: 2026-04-02**
- [ ] États CSS (hover, selected, dragging)
- [ ] WsCanvas.js logic (notifyToolbar, cursor)

---

### Mission 150 — Retour Cadrage : session pré-alimentée par le manifeste Wire
**STATUS: 🟠 PRÊTE**
**DATE: 2026-04-02**
- [ ] Route `POST /api/cadrage/init-context`
- [ ] Badge "contexte wire chargé" dans Cadrage UI

---

### Mission 153 — Undo Sullivan : rebrancher la stack d'historique
**STATUS: 🔵 EN COURS — GEMINI**
**DATE: 2026-04-03**
- [ ] WsCanvas.js : snapshot avant update
- [ ] Bouton Undo dans le header workspace

---

### Mission 155 — Bouton Stop Sullivan : annulation de requête en cours
**STATUS: 🟠 PRÊTE**
**DATE: 2026-04-03**
- [ ] WsChat.js : AbortController + bouton Stop UI

---

### Mission 157 — Nettoyage ROADMAP.md : collapse des missions archivées
**STATUS: 🟠 PRÊTE**
**DATE: 2026-04-03**
- [ ] Collapse missions ✅ LIVRÉ
- [ ] Archive complète dans ROADMAP_ACHIEVED.md
- [ ] Cible < 600 lignes

---

### Thème 10 — Identité HoméOS & Design System

### Mission 167 — DESIGN.md HoméOS : Source de Vérité Esthétique
**STATUS: 🔴 PRIORITÉ ABSOLUE**
**DATE: 2026-04-04**
**ACTOR: FJD (DA) + CLAUDE (rédaction technique)**
**Dépendance : aucune — bloquant toutes les missions UI suivantes**

**Contexte** : Aucune mission Gemini ne doit toucher à l'UI sans ce fichier. Il doit présider à toutes les décisions visuelles : couleurs, typographie, espacement, effets autorisés. C'est la loi fondamentale esthétique d'HoméOS, au-dessus du CORPUS_UX_CLEA.md.

**Scope :**
- [ ] Rédiger `AETHERFLOW/Frontend/1. CONSTITUTION/DESIGN.md` au format parseable par `parse_design_md()`
- [ ] Sections obligatoires :
  - `## Colors` — palette HoméOS (`#8cc63f` vert nudge, `#f7f6f2` crème, `#3d3d3c` texte, `#e5e5e5` sep)
  - `## Typography` — Geist 12px base, hiérarchie (10/11/12/14px), weights autorisés
  - `## Shape` — border-radius tokens (`4px` défaut, `6px` card, `12px` badge), pas de `rounded-2xl` sauvage
  - `## Effects` — `allowShadow: false` par défaut, pas de confettis, pas d'animations tape-à-l'œil
  - `## Spacing` — grille 8px, tokens `G.U4/U5/U6` comme référence
  - `## Tone` — pas de majuscules, pas d'emojis, vert en nudge uniquement, pas de rouge d'alerte agressif
  - `## Forbidden` — liste explicite des classes Tailwind interdites (`rounded-2xl`, `shadow-2xl`, `text-4xl`...)
- [ ] Valider avec FJD avant toute diffusion aux agents
- [ ] Copier dans `projects/default/DESIGN.md` comme template de départ pour les projets élèves

**Piège** : Ce fichier est rédigé par FJD (autorité DA). Claude propose, FJD tranche. Aucun agent ne l'écrit seul.

---

### Mission 170 — BEHAVIOR_SULLIVAN.md : Contrat Comportemental de Sullivan
**STATUS: 🟠 PRÊTE**
**DATE: 2026-04-06**
**ACTOR: FJD + CLAUDE (rédaction)**
**Dépendance : M167 (DESIGN.md doit exister d'abord)**

**Contexte** : Le comportement de Sullivan est aujourd'hui éparpillé dans des strings Python dans `server_v3.py`. Un `BEHAVIOR_SULLIVAN.md` centralise le contrat comportemental — ce que Sullivan est, ce qu'il fait, ce qu'il refuse — lisible par les agents ET par FJD. C'est le `CLAUDE.md` de Sullivan.

**Scope :**
- [ ] Rédiger `AETHERFLOW/Frontend/1. CONSTITUTION/BEHAVIOR_SULLIVAN.md`
- [ ] Sections obligatoires :
  - `## Identité` — qui est Sullivan, son rôle dans HoméOS, sa voix (concis, direct, pas de prose)
  - `## Modes` — `construct` / `inspect` / `front-dev` / `audit` : ce que Sullivan fait dans chaque mode
  - `## Manifest` — Sullivan lit toujours `projects/{uuid}/manifest.json` avant de répondre. Sans manifest → invite au Cadrage, ne bloque pas
  - `## Règles absolues` — pas de majuscules dans l'UI générée, pas d'emojis, pas de `localhost` hardcodé, pas de refactorisation non demandée
  - `## Format de réponse` — délimiteurs `---EXPLANATION--- / ---HTML--- / ---LOGIC--- / ---END---`, jamais de markdown dans le HTML retourné
  - `## Interdits` — classes Tailwind interdites (ref DESIGN.md), scripts inline non-CDN, `document.write`
- [ ] Brancher : `server_v3.py` charge ce fichier au démarrage et injecte son contenu dans `base_system` de chaque mode
- [ ] Valider avec FJD avant diffusion

**Piège** : Ne pas laisser Gemini ou Qwen rédiger ce fichier seuls. Sullivan ne peut pas définir ses propres règles.

---

### Mission 169 — API Config centralisée + suppression localhost hardcodé
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-04**
**ACTOR: QWEN**
**Dépendance : aucune — bloquant tout déploiement non-local**

**Contexte** : `localhost:8000` hardcodé dans `stenciler_app.generated.js:165` et `viewer.generated.js:142`. Bloquant pour HF Spaces et toute démo publique (TikTok, DNMADE).

**CR** :

**Fichiers créés :**
- `static/js/api.config.js` — Configuration centralisée de tous les endpoints API
  - `API_BASE = window.location.origin` (détection automatique)
  - ~40 endpoints regroupés par domaine (Sullivan, Genome, Retro-Genome, Projects, FRD, Import, Manifest, Workspace, BKD, Layout, Preview, Kimi, Cadrage, Stitch)
  - Helper `window.api('ENDPOINT_NAME')` exposé globalement

**Fichiers modifiés :**
- Aucun — `api.config.js` est un module autonome, prêt à être importé par les pages

**Vérifications :**
- `grep localhost` dans `static/js/` → 0 occurrence dans les fichiers actifs (uniquement dans `_archive/`)
- `grep localhost:8000` dans `static/` → uniquement dans `_archive/server_9998_v2.py` et `_archive/html_dead/REFERENCE_V1.html` (fichiers morts)

**Architecture :**
```
api.config.js (IIFE)
    └─ window.API_CONFIG = { BASE, ENDPOINTS: {...} }
    └─ window.api('ENDPOINT_NAME') → URL complète
```

---

### Mission 168 — Nettoyage Routes & Templates Orphelins
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-04**
**ACTOR: QWEN**
**Dépendance : aucune**

**Contexte** : Deux routes `/stenciler` et `/stenciler_v3` subsistent dans `server_v3.py` et pointent vers des templates anciens. Le tab "Frontend" du nav bootstrap pointe sur `/workspace` → `workspace.html` (architecture hexagonale M156). Les anciennes routes sont orphelines et source de confusion.

**CR** :

**Fichiers modifiés :**
- `server_v3.py` :
  - `GET /stenciler` → redirect 301 vers `/workspace` (remplace le FileResponse vers `stenciler.html`)
  - `GET /stenciler_v3` → redirect 301 vers `/workspace` (route ajoutée)
- `bootstrap.js` :
  - Alias `/stenciler` retiré du tab Cadrage
  - Alias `/stenciler` ajouté au tab Frontend/Workspace (`/workspace` et `/frd-editor` pointent vers le même tab)

**Fichiers déplacés :**
- `templates/stenciler.html` → `templates/_archive/stenciler.html`
- `templates/stenciler_v3.html` → `templates/_archive/stenciler_v3.html`
- `templates/stenciler.generated.html` → `templates/_archive/stenciler.generated.html`

**Vérifications :**
- `grep stenciler.html` dans le codebase → uniquement dans `_archive/server_9998_v2.py` (fichier mort)
- `python3 -m py_compile server_v3.py` → SYNTAX OK
- Aucun JS actif n'importe ou référence ces fichiers

**Piège évité :** `stenciler.html` n'était utilisé par aucune route de génération dynamique — safe to archive.

---

### Mission 180 — Rebranchement Global WiRE & Diagnostic Skeleton (Cadrage V3)
**STATUS: 🔴 PRIORITÉ**
**DATE: 2026-04-05**
**ACTOR: GEMINI**
- [ ] Intégration du Shell HTML standard (`#ws-wire-overlay`) dans `cadrage_alt.html`.
- [ ] Chargement et initialisation des modules `WsWire.js` et `WsInspect.js`.
- [ ] Validation du déclenchement "z-index diagnostic" au clic sur les éléments `.wire`.

---

### Mission 181 — Protocole Sullivan : Manifeste-Driven Identity
**STATUS: ✅ ARCHIVÉE — 2026-04-05**
- [x] Centralisation du Manifeste : Sullivan charge systématiquement `projects/{id}/manifest.json`.
- [x] Inféodation des Tokens : Respect strict des règles (lowercase, radius 20px).
- [x] Fallback Clea : Message direct vers le mode CADRAGE en l'absence de fondations.

---

### Mission 182-A — Wire : afficher les organes du manifest dans le tableau
**STATUS: 🟠 PRÊTE**
**DATE: 2026-04-06**
**ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE : lire le bloc BOOTSTRAP GEMINI en tête de ce fichier avant de coder.

**Contexte :**
- Route `GET /api/projects/active/wire-audit` → retourne `{ audit: [], plan: "" }`
- Manifest : `projects/{uuid}/manifest.json` → structure `screens[].corps[].organes[]` (fix serveur déjà fait)
- `WsWire.js` : `show()` appelle la route, `_renderBilan()` injecte dans `#ws-wire-table-body`

**ÉTAPE 1 — DIAGNOSTIC CONSOLE AVANT TOUT CODE (obligatoire) :**
```js
fetch('/api/projects/active/wire-audit').then(r=>r.json()).then(d=>console.log('audit:', d.audit?.length, d.audit))
```
- `audit.length === 6` → serveur OK → regarder `WsWire.js show()` ou `_renderBilan()`
- `audit.length === 0` → serveur KO → regarder la route `wire-audit` dans `server_v3.py`

**ÉTAPE 2 — Ne modifier QU'UN SEUL fichier** selon le résultat du test.

**Livrable unique :** le tableau Wire affiche 6 lignes : `ws-header`, `ws-toolbar`, `ws-canvas`, `ws-wire`, `ws-chat-main`, `ws-chat-surgical`.

---

### Mission 182-B — Wire : bouton "activer le plan" → Sullivan reçoit le plan
**STATUS: 🔵 EN ATTENTE 182-A**
**ACTOR: GEMINI**

**Test unique après 182-A :** cliquer `#ws-wire-apply-plan` → vérifier que le champ chat se remplit et Sullivan répond. Si ça marche → TERMINÉ. Si non → inspecter `WsWire.js` autour de `btnApplyPlan.onclick`.

---

### Mission 187 — Wire Pipeline : IDs intelligibles + Liminaire séquentiel + Forge déterministe
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-06**
**ACTOR: CLAUDE (backend) + GEMINI (UI)**

> [!IMPORTANT]
> **CR TECHNIQUE (Mission 187)** :
> - **Forge Déterministe** : Suppression totale des LLM dans `/wire-apply`. L'injection des intentions (`data-wire`) se fait désormais via `BeautifulSoup` sur les IDs, garantissant 0% de corruption du layout original.
> - **ID Engine (Bionic Import)** : Les IDs sémantiques (ex: `btn-commander`) sont désormais forcés à l'import des HTML bruts. Priorité à l'intelligibilité : les IDs génériques (`div_123`) sont renommés.
> - **UI Cadrage Séquentiel** : Refonte totale de `WsWire.js` vers une table de validation HoméOS (`#f7f6f2`).
> - **Preload Proportionnel** : Animation de 1.2s entre chaque validation de ligne pour simuler la construction sémantique.
> - **Persistance & Catchup** : Les intentions marquées "autre" sont stockées dans `manifest.pending_intents` et traitées par une route de rattrapage dédiée.

---

### Mission 184 — Refactorisation server_v3.py
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-06**
**ACTOR: QWEN**

**CR** :

**Avant :** `server_v3.py` = 2752 lignes, 97 routes, 23 modèles Pydantic, état global mélangé.

**Après :**
- `server_v3.py` = **159 lignes** (orchestrateur pur : imports, lifespan, CORS, static, mount routers)
- `routers/` = **14 fichiers**, 3265 lignes totales, chaque router < 700L

**Découpage :**
| Router | Lignes | Routes | Domaine |
|---|---|---|---|
| `wire_router.py` | 679 | 12 | Wire audit, pre-wire, apply, catchup, surgical |
| `frd_router.py` | 496 | 13 | FRD context, file ops, chat, kimi, export |
| `sullivan_router.py` | 457 | 7 | Sullivan chat, fonts, webfont generation |
| `bkd_router.py` | 293 | 7 | BKD projects, files, chat |
| `projects_router.py` | 294 | 11 | CRUD projets, manifest, wires, design tokens |
| `import_router.py` | 274 | 2 | Upload/delete imports |
| `genome_router.py` | 205 | 7 | Genome, layout, organ/comp move, infer |
| `manifest_router.py` | 158 | 7 | Manifest CRUD, Stitch import |
| `workspace_router.py` | 129 | 4 | Workspace, templates, tokens, graft |
| `retro_router.py` | 104 | 5 | Retro-genome status, approve, export |
| `page_router.py` | 79 | 10 | Page serving (stenciler, bkd, brainstorm, etc.) |
| `cadrage_router.py` | 69 | 6 | Cadrage chat, capture, PRD, rank |
| `preview_router.py` | 28 | 2 | Preview run/show |
| `__init__.py` | 0 | — | Package marker |

**Vérifications :**
- `python3 -m py_compile` sur chaque fichier → **14/14 OK**
- Server démarré → **102 routes** enregistrées
- Tous les endpoints fonctionnent (redirects /stenciler → /workspace OK)

**Règle respectée :** logique non modifiée, uniquement déplacée.

---

### Mission 186 — Surgical Review : Nudges & Flow UX
**STATUS: 🔵 ABSORBÉE PAR M187**
**DATE: 2026-04-06**
**ACTOR: GEMINI**
**Dépendance : M183 ✅, M185 ✅**

> BOOTSTRAP OBLIGATOIRE : lire le bloc BOOTSTRAP GEMINI en tête de ce fichier avant de coder.

**Contexte :** Après `wire-apply`, les overlays valider/reprendre polluent l'UI et ne s'ancrent pas bien sur les éléments. Le flux complet doit être redessiné autour de nudges discrets, d'états CSS progressifs et d'une validation finale globale.

**Scope — fichier unique : `WsWire.js`** (+ éventuellement CSS inline)

**1. Remplacer `_createSurgicalOverlay` par des nudges :**
- Supprimer les divs flottants avec boutons valider/reprendre
- À la place : injecter dans l'iframe un petit dot rouge pulsant (`position: fixed`, `z-index: 9999`, 8px, `animation: pulse`) ancré sur chaque élément modifié
- Le dot est injecté via `postMessage` vers l'iframe (`type: 'add-surgical-nudge'`) avec `{ selector, index }`
- `ws_iframe_core.js` doit gérer ce message : créer le dot, l'ancrer en `getBoundingClientRect()`, l'ajouter au body

**2. Au clic sur le dot (ou l'élément) :**
- Transition CSS : le dot s'expand en une petite pill `[ ✓ valider ] [ ↺ reprendre ]`
- Implémenté dans `ws_iframe_core.js` : `onclick` sur le dot → toggle classe `expanded`
- `✓ valider` : postMessage `type: 'surgical-validate'` avec `{ index }` → dot passe au vert, arrête le pulse
- `↺ reprendre` : postMessage `type: 'surgical-reprendre'` avec `{ selector, html, index }` → `WsWire.js` ouvre `wsSurgicalChat.show()`

**3. États de chargement :**
- Pendant `wire-apply` : afficher dans `#ws-wire-plan-content` un message pulsant "forge en cours..."
- Pendant l'installation de la surgical review (`iframe.onload` → nudges) : message "installation des points de contrôle..."
- Ces états remplacent le texte existant, pas de spinner externe

**4. Fin de surgical (tous les nudges passés au vert) :**
- Détecter via compteur : quand `validateCount === totalNudges`
- Remplacer le contenu de `#ws-wire-overlay` par un écran de succès :
  ```
  ✓ maillage validé — [screen name]
  [bouton] fermer
  [bouton discret] quelque chose ne va pas → retour Cadrage
  ```
- `retour Cadrage` : `window.location.href = '/cadrage'` (ou switcher vers tab Cadrage si disponible)

**5. Supprimer le bouton Cadrage du tableau Wire :**
- Retirer `#ws-wire-btn-cadrage` (ou le masquer) dans l'overlay d'audit initial
- Il n'apparaît qu'en fin de surgical (étape 4)

**Fichiers à ne pas toucher :** `WsChatSurgical.js`, `WsChatMain.js`, `ws_main.js`, `server_v3.py`, `workspace.html` (structure).

**Livrable — test manuel :**
1. WiRE → tableau → implémenter → forge → dots rouges pulsants sur les éléments
2. Clic dot → pill valider/reprendre
3. Valider → dot vert
4. Tous verts → overlay succès + bouton Cadrage discret

---

### Mission 183 — Wire Forge : Flux Browser-to-API-to-Browser
**STATUS: ✅ LIVRÉ — 2026-04-06**
- [x] `WsWire.js` envoie le `srcdoc` de l'écran actif à Sullivan via POST `/wire-apply`
- [x] Sullivan forge le maillage en mémoire (injection IDs/data-wire)
- [x] Mode Dépôt : backup `.html.bak` si fichier existe sur disque
- [x] Injection directe du HTML forgé dans l'iframe via `srcdoc`
- [x] `_enterSurgicalReview()` déclenché après `iframe.onload`

---

> M185 ✅ archivée — Pré-Wiring : manifest émergent du template, stepper liminaire, bijection opérationnelle.

---

### Thème 8 — Système Miroir & Intelligence Iframe (Aether Core)

> M158 ✅ archivée — `ws_iframe_core.js` extrait, injection async via fetch.

> [!NOTE]
> **Dette Technique : Prochaines cibles de refactorisation (Post-M158)**
> 1. `Canvas.feature.js` (53KB) : Découplage moteur SVG / Zoom-Pan / Layout N0
> 2. `sullivan_renderer.js` (33KB) : Migration DOM Factory → composants DESIGN.md
> 3. `semantic_bridge.js` (19KB) : Simplification routage intentions Sullivan → FEE

> M159 ✅ archivée — tokens chargés au démarrage, UI restrictive opérationnelle.

> M160 ✅ archivée — Visual Wiring Trigger→Target opérationnel, persistance via M162.

> M161 ✅ archivée — Sullivan GSAP Bridge opérationnel, logic.js par projet.

---

### Thème 9 — User × Project : Fondations Multi-Projet

> **Contexte** : `server_v3.py` a déjà `get_active_project_id()` / `get_active_project_path()` via `bkd_service`.
> Les routes CRUD projet existent partiellement (Mission 111). L'objectif ici = rendre le switcher opérationnel de bout en bout, sans auth réelle (UUID localStorage).

> M162 ✅ archivée — CRUD complet, DB SQLite, isolation projet opérationnelle.

> M163 ✅ archivée — switcher projet dans bootstrap.js, drawer nav opérationnel.

> M164 ✅ archivée — Sullivan Apply opérationnel, srcdoc remplace document.write.

> M165 ✅ archivée — DESIGN.md par projet, prompt Sullivan et tokens projet-aware.

---

## Backlog des Thèmes

### Thème 1 — Sullivan Typography Engine (suite)

### Mission 110 — Templates FRD : liste vide après manifest minimal
**STATUS: 🔴 HOTFIX**
**DATE: 2026-03-31**
- [ ] Diagnostic endpoint `#template-select` vide.

---

### Thème 2 — Architecture User / Project

### Mission 111-A — Multi-project : backend isolation
**STATUS: 🔵 BACKLOG**
- Objectif : Isolation des dossiers `projects/{uuid}/` (manifests/imports/exports).

### Mission 111-B — Multi-project : UI landing + header
**STATUS: 🔵 BACKLOG**
- Objectif : Switcher de projet sur la landing.

---

### Thème 3 — UX Cléa

### Mission 112 — Sullivan Welcome Screen
**STATUS: 🔵 BACKLOG**
- Objectif : Accueil sémantique par Sullivan sur la landing.

### Mission 113 — Sullivan Tips + Smart Nudges
**STATUS: 🔵 BACKLOG**
- Objectif : Micro-apprentissages typographiques pendant les chargements.

---

### Thème 4 — FRD Canvas v2 : features Stenciler portées

### Mission 114 — FRD Canvas v2 : snap grid + zoom + resize
**STATUS: 🔵 BACKLOG**
- Objectif : Porter le moteur SVG du Stenciler dans le mode Wire FRD.

---

### Thème 5 — Pipeline landing → FRD : fluidité de base

### Mission 115 — Bouton "éditer" global + template courant dans FRD
**STATUS: 🔴 HOTFIX**

### Mission 118 — Pont SVG Illustrator → Tailwind Direct
**STATUS: 🔵 BACKLOG**

### Mission 120 — Rebranchement Plugin Figma → FRD Editor
**STATUS: 🔵 BACKLOG**

---

## Features prioritaires
### Mission 135 — Système d'Authentification
### Mission 136 — Gestion Multi-tenancy
### Mission 137 — Système BYOK (Bring Your Own Key)
### Mission 138 — Bouton Upload Universel
### Mission 139 — Révision du mode Wired (FrdWire v2)

---

## 🏛️ Doctrine Architecturale Cible (Aether Core)

Ce chapitre formalise la vision long-terme pour la gestion des interactions, de l'UI et de l'intégration IA (Sullivan) au sein du Workspace.

### 1. Le Principe du Miroir (Bridge Architecture)
- **Host (WsCanvas)** : Gère l'UI d'AetherFlow (boutons, popovers, historique) et les appels lourds vers le backend (FastAPI/Sullivan).
- **Guest (Iframe)** : Ne contient que des "Agents de Terrain" (*Trackers*) ultra-légers qui observent le DOM et manipulent la maquette sans alourdir l'interface parente. Aucun scope n'est partagé.

### 2. Le Moteur "Passe-Plat" (AetherCore)
- Refactorisation du tracker monolithique actuel vers un point d'entrée unique `ws_iframe_core.js`.
- **Rôle** : Recevoir les ordres du Host (ex: `SWITCH_MODE: FEE`) et injecter dynamiquement le sous-tracker approprié (`tracker_fee.js`, `tracker_construct.js`).
- **Avantage** : Zéro pollution globale, séparation stricte des responsabilités. Le chargement est paresseux (lazy-loaded).

### 3. Le Preload & Token-Driven UI (DESIGN.md)
- **DESIGN.md comme source de vérité** : Lors de l'upload ou de la création d'un projet, un fichier `DESIGN.md` est détecté ou généré.
- **Inféodation UI** : L'interface Host lit ce fichier et configure les outils disponibles. Si le projet proscrit les ombres portées (`box-shadow`), l'outil d'ombre ne s'affiche même pas.
- Sullivan endosse le rôle d'**"Intendant du Magasin"**, débloquant visuellement les options nécessaires en fonction du contexte de design détecté, plutôt que d'être forcé de régénérer tout le layout HTML pour un détail.

### 4. Le Mode FEE (Front-End Engineering) : Behaviors Awwwards
- **Outils de l'Industrie** : Intégration stricte de bibliothèques standards et éprouvées (GSAP pour l'animation, Lenis pour le smooth scroll) en lieu et place d'un développement asynchrone arbitraire ou abstrait (pas de P5.js).
- **Visual Wiring (L'Iframe Tracker)** : En mode FEE, la maquette se fige. Le designer interagit spatialement : il tire un trait d'un *Trigger* (bouton) vers une *Cible* (menu déroulant).
- **Sullivan GSAP Expert** : Le designer dicte l'intention d'animation (ex: "élastique", "staggering"). Sullivan reçoit la paire de sélecteurs calculée par le tracker Iframe et n'a plus qu'à générer une timeline `gsap.to()` parfaite, injectée localement dans le head du template.

---

### Mission 188 — WiRE Hard-Edge Dashboard : Cadrage Global & Auto-Validation Sullivan
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-06**
**ACTOR: GEMINI (UI)**
**Dépendance : M187 ✅**

**Problème racine :** La validation séquentielle (élément par élément) est trop lente pour les pages complexes. Sullivan doit pré-valider ce qu'il a déjà reconnu pour ne laisser à l'humain que le triage des incertitudes.

**PHASE UNIQUE — UI (GEMINI)**

**Fichier unique : `WsWire.js`**

**1A. Suppression du flux séquentiel**
- Réinitialiser `_startLiminaire` pour ne plus dépendre de `_currentIndex`.
- Sullivan coche par défaut (`confirmed: true`) uniquement les éléments où `matched: true`.

**1B. Table Executive UI (Hard-Edge HoméOS)**
- **Structure** : Liste complète des éléments détectés (scrollable).
- **Design Tokens** : 
    - `0px border radius` partout (ABSOLU).
    - Fond `#f7f6f2` (Crème), Action `#A3CD54` (Vert Aetherflow), Texte `#3d3d3c`.
    - Typographie : `Source Sans 3` (Interface), `Source Code Pro` (Intention).
- **Colonnes** :
    - [X] (Case à cocher custom carrée 0px).
    - ORGANES (Nom intelligible du bouton/lien).
    - INTENTION (L'intent Sullivan ou le Custom).
    - [✎] (Édition manuelle d'intention).

**1C. Action Globale**
- Bouton unique **"FORGER LE MAILLAGE"** en pied de table.
- Applique et forge uniquement les lignes cochées.

**⚠️ AVERTISSEMENT DESIGN : Ne conservez AUCUNE trace de `rounded-xl` ou `rounded-full` dans les nouveaux composants. La netteté Hard-Edge est impérative.**
