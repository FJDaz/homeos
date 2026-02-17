# ROADMAP_ACHIEVED — Archive des Phases Terminées
**Append-only. Ne jamais modifier une entrée existante.**

---
<!-- Les phases validées sont archivées ici par Claude après validation de François-Jean -->

---

## PHASE 1 — Wireframes Sullivan Renderer
STATUS: ARCHIVÉ
DATE: 2026-02-15
COMMIT: 94488da

### Ce qui a été fait
- Réécriture des 3 méthodes wireframe dans `sullivan_renderer.js` (231L → enrichis)
  - `generateWireframeCorps` : 4 hints (brainstorm/backend/frontend/deploy) avec gradients et icônes
  - `generateWireframeOrganes` : 3 hints (analyse/choix/sauvegarde) avec composants expressifs
  - `generateWireframeGeneral` : hint table + fallback coloré
- Bug CSS corrigé dans `choix` : `display:gap:6px` → `display:flex;gap:6px`
- Commit 94488da (+cleanup repo : archive_svelte -40MB, .backup_*, .generated.py, artifacts pip)

### Ce qui reste ouvert (transmis Phase 2)
- Visual_hint absent des données genome → la plupart des composants tombent sur le fallback générique
- Drill-down non implémenté (viewer = 4 sections linéaires sans interactivité N→N+1)
- Validation visuelle par François-Jean non obtenue (serveur non relancé lors de la session)

---

## PHASE 2 — Mission A : sullivan_renderer.js Fix wireframes + descriptions
STATUS: ARCHIVÉ
DATE: 2026-02-16
ACTOR: KIMI

### Ce qui a été fait
- Fix 1 : Inférence `visual_hint` depuis `comp.name` pour les Corps (L143-150)
  - brainstorm / backend+api / frontend+interface / deploy+livraison
- Fix 2 : 3 nouveaux wireframes dans `generateWireframeGeneral()` (L100-133)
  - `detail-card` : header coloré + 3 lignes label:valeur
  - `stencil-card` : titre + description + 2 boutons Garder/Réserve
  - `form` : 2 champs gris empilés + bouton submit vert
- Fix 3 : `description_ui` affiché sur 2 lignes dans `.comp-info` (L163+L171, `-webkit-line-clamp:2`)

### Ce qui reste (Phase 2 en cours)
- Mission B : breadcrumb DOM dans viewer.html + drilldownState dans genome_engine.js
- Mission C : brancher `drillInto()` sur les clics Corps dans sullivan_renderer.js

---

## PHASE 2 — Missions B+C : Drill-down Genome Viewer
STATUS: ARCHIVÉ
DATE: 2026-02-16
ACTOR: KIMI

### Ce qui a été fait

**Mission B — viewer.html + genome_engine.js**
- Breadcrumb DOM ajouté dans `viewer.html` (avant `.container`) :
  - `#breadcrumb-bar` (display:none par défaut)
  - `#breadcrumb-text` : affiche "Tout › [NomCorps]"
  - `#breadcrumb-back` + `#breadcrumb-reset` : boutons de navigation
- `genome_engine.js` — 5 méthodes de drill-down ajoutées :
  - `drilldownState` : objet d'état `{active, corpsId, corpsName, organeId, organeName}`
  - `applyDrillFilter()` : masque/affiche les `.comp-card` selon le corps actif
  - `updateBreadcrumb()` : affiche/masque la barre breadcrumb selon l'état
  - `drillInto(corpsId, corpsName)` : active le filtrage sur un corps
  - `resetDrill()` : désactive le filtrage, tout redevient visible
  - Listeners breadcrumb dans `setupEventListeners()`

**Mission C — sullivan_renderer.js**
- `generateComponentCard()` : `onclick` conditionnel sur les cartes Corps
  - Corps → `drillInto(id, name)` + `toggleCheckbox(cid)`
  - Autres niveaux → `toggleCheckbox(cid)` seul
- Sélection checkbox préservée pendant le drill

### Ce qui reste ouvert (transmis Phase 3)
- Bug canvas `'alphabetical'` → `'alphabetic'` (stenciler.js:~313) — hors scope viewer, sera traité Phase 3
- Faux positifs semantic_bridge.js (58 violations HTML dans description_ui) — non bloquant
- `stenciler_v2.html` : monolithe 1540L, source de difficultés agents → Phase 3 Factory

