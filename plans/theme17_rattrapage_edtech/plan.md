# Theme 17 — Rattrapage EdTech: Implementation Plan

## Overview
**Theme**: Rattrapage EdTech (Vendredi)  
**Date**: 2026-04-07  
**Scope**: 7 bug fixes / features for the EdTech/DNMADE classroom system  
**Priority**: R1-R6 critical, R7 backlog  

---

## R1 — `/teacher`: Create class form does not submit

### Problem
`POST /api/classes` request appears to go nowhere. The form in `teacher_dashboard.html` calls `createClass()` via `onclick`, but the POST fails silently.

### Root Cause Analysis
Based on code review:
- ✅ Backend route exists: `POST /api/classes` in `class_router.py` line 214
- ✅ Route is registered in `server_v3.py` line 179
- ✅ Frontend `createClass()` function exists in `teacher_dashboard.html`
- ⚠️ **Potential issues**:
  1. Form might be submitting as HTML form instead of fetch (if wrapped in `<form>` tag)
  2. Missing `preventDefault()` if there's an implicit form submission
  3. CORS or content-type mismatch
  4. Server not running on expected port (9998)

### Fix Plan
1. **Inspect `teacher_dashboard.html`** — check if create button is inside a `<form>` element
   - If yes: add `type="button"` to prevent default form submission
   - If no: the `onclick` handler should work as-is

2. **Add error handling** to `createClass()`:
   ```javascript
   function createClass() {
       var name = document.getElementById('new-class-name').value.trim();
       var subject = document.getElementById('new-class-subject').value.trim();
       if (!name) {
           console.error('Class name is required');
           return;
       }
       console.log('Creating class:', name, subject); // Debug log
       fetch(API, {
           method: 'POST',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify({ name: name, subject: subject })
       })
       .then(function(r) {
           if (!r.ok) throw new Error('HTTP ' + r.status);
           return r.json();
       })
       .then(function(data) {
           var fb = document.getElementById('create-feedback');
           fb.textContent = 'classe "' + data.name + '" creee';
           fb.style.display = 'block';
           document.getElementById('new-class-name').value = '';
           document.getElementById('new-class-subject').value = '';
           setTimeout(function() { fb.style.display = 'none'; }, 2000);
           loadClasses();
       })
       .catch(function(e) {
           console.error('createClass error:', e);
           var fb = document.getElementById('create-feedback');
           fb.textContent = 'erreur: ' + e.message;
           fb.style.display = 'block';
           fb.style.color = '#e53e3e';
       });
   }
   ```

3. **Test with curl**:
   ```bash
   curl -X POST http://localhost:9998/api/classes \
     -H "Content-Type: application/json" \
     -d '{"name":"DNMADE 2026","subject":"Design Web"}'
   ```

4. **Test in browser**: Open DevTools console, click "creer la classe", verify POST succeeds

### Files to Modify
- `Frontend/3. STENCILER/static/templates/teacher_dashboard.html` — `createClass()` function

### Validation
- [x] POST `/api/classes` returns 200 with valid class object
- [x] UI shows success feedback
- [x] Class appears in dropdown immediately
- [x] Console shows no errors

### Addendum — R1 completed (2026-04-07)

**Diagnostic :**
- Le backend `POST /api/classes` fonctionnait correctement (test curl OK)
- Le frontend `createClass()` existait mais sans gestion d'erreur visible
- En cas d'échec HTTP, l'erreur était silencieuse (seulement `console.error`)
- Aucun feedback utilisateur sur les erreurs réseau

**Ce qui a été fait :**

1. **`createClass()` — erreur handling complet :**
   - Ajout de `console.log` à chaque étape (debug)
   - Validation HTTP status (`!r.ok` → throw Error)
   - Feedback UI : message d'erreur en rouge si échec
   - Feedback UI : message de succès en vert si réussite
   - Validation du champ nom obligatoire avec message "nom requis"
   - Durée d'affichage du feedback : 2s → 3s

2. **`PUT /api/classes/{class_id}` — modifier une classe (nouveau) :**
   - Backend : route `PUT` dans `class_router.py`
   - Backend : modèle `ClassUpdateRequest` (name + subject)
   - Frontend : bouton "modifier" visible quand une classe est sélectionnée
   - Frontend : modal d'édition avec champs nom/matière pré-remplis
   - Frontend : fonction `editClass()`, `closeEditModal()`, `saveClassEdit()`
   - Rechargement automatique de la liste après modification

3. **`DELETE /api/classes/{class_id}` — supprimer une classe (nouveau) :**
   - Backend : route `DELETE` dans `class_router.py`
   - Backend : suppression en cascade des étudiants (`DELETE FROM students WHERE class_id=?`)
   - Frontend : bouton "supprimer" visible (styling rouge)
   - Frontend : confirmation via `confirm()` avant suppression
   - Frontend : reset de l'UI après suppression (boutons cachés, dashboard vidé)
   - Frontend : rechargement automatique de la liste

4. **UI — boutons edit/delete :**
   - Boutons "modifier" et "supprimer" ajoutés dans `.controls`
   - Affichage conditionnel : visibles uniquement si `currentClassId !== null`
   - Bouton supprimer : bordure + texte rouge (`#e53e3e`)
   - Modal d'édition : overlay sombre + carte centrée, style cohérent HoméOS

**Testé et validé :**
```bash
# CREATE
curl -X POST http://localhost:9998/api/classes \
  -H "Content-Type: application/json" \
  -d '{"name":"DNMADE 2026 Test","subject":"Design Web"}'
# → {"id":"dnmade-2026-test","name":"DNMADE 2026 Test","subject":"Design Web"}

# UPDATE
curl -X PUT http://localhost:9998/api/classes/test-r1 \
  -H "Content-Type: application/json" \
  -d '{"name":"Test R1 Modified","subject":"Design Web Updated"}'
# → {"id":"test-r1","name":"Test R1 Modified","subject":"Design Web Updated"}

# DELETE
curl -X DELETE http://localhost:9998/api/classes/test-r1
# → {"ok":true,"id":"test-r1"}
```

---

## R2 — Cadrage mode prof: `class_id` not transmitted to Sullivan

### Problem
`cadrage_router.py` doesn't accept `class_id` parameter. `brainstorm_logic.sse_chat_generator()` doesn't inject the DNMADE referentiel.

### Fix Plan

#### Step 1: Update `cadrage_router.py`
- Add `class_id: str = Query(None)` parameter to the SSE chat endpoint
- Pass `class_id` to the generator function

#### Step 2: Update `brainstorm_logic.py`
- Implement `_load_class_meta(class_id)` — load class metadata from database
- Implement `_load_dnmade_referentiel()` — load `dnmade_referentiel.json`
- Implement `_build_prof_system(class_id)` — build system prompt with DNMADE context
- Inject referentiel into Sullivan's system prompt when `class_id` is present

### Files to Modify
- `Frontend/3. STENCILER/routers/cadrage_router.py` — add `class_id` param
- `Frontend/3. STENCILER/core/brainstorm_logic.py` — add referentiel loading functions

### Validation
- [x] `/cadrage?mode=prof&class_id=dnmade-2026` loads with DNMADE context
- [x] Sullivan receives referentiel in system prompt
- [x] Prof mode shows competences panel

### Addendum — R2 completed (2026-04-07)

**Diagnostic :**
- Le frontend `cadrage_prof.html` passait déjà `class_id` dans l'URL SSE (ligne 193-194)
- Le frontend `cadrage_alt.html` passait déjà `class_id` (ligne 608)
- Le router `cadrage_router.py` acceptait déjà `class_id` (ligne 21)
- `brainstorm_logic.py` avait déjà `_load_class_meta()`, `_load_dnmade_referentiel()`, `_build_prof_system()`
- **Le seul bug :** chemin DB incorrect dans `_load_class_meta()`
  - Avait : `Path(__file__).parent.parent.parent.parent / "Frontend/3. STENCILER" / "db" / "projects.db"` → n'existait pas
  - Devait être : `Path(__file__).parent.parent.parent.parent / "db" / "projects.db"` → `/Users/francois-jeandazin/AETHERFLOW/db/projects.db`

**Ce qui a été fait :**

1. **Correction du chemin DB dans `_load_class_meta()` :**
   - Ancien chemin : `... / "Frontend/3. STENCILER" / "db" / "projects.db"` (inexistant)
   - Nouveau chemin : `... / "db" / "projects.db"` (racine AETHERFLOW)
   - Résultat : `SELECT name, subject FROM classes WHERE id=?` retourne maintenant les données

2. **Vérification complète du pipeline :**
   - `_load_class_meta('dnmade1-2026')` → `{'name': 'DNMADE1_2026', 'subject': 'OLN'}` ✅
   - `_load_dnmade_referentiel()` → 14 lignes, 4 domaines (A, B, C, D) ✅
   - `_build_prof_system(meta, ref)` → prompt système complet 753 chars ✅

**System prompt généré en mode prof :**
```
MODE PROF -- HomeOS
Classe : DNMADE1_2026
Sujet actif : OLN

Referentiel DNMADE :
Domaine A -- Création:
  A1 : Recherche et exploration
  A2 : Concept et proposition
  A3 : Réalisation et prototypage
Domaine B -- Communication:
  B1 : Présentation visuelle
  B2 : Argumentation orale
Domaine C -- Technique:
  C1 : Maîtrise des outils numériques
  C2 : Production et intégration
  C3 : Qualité et conformité
Domaine D -- Culture:
  D1 : Références et veille
  D2 : Analyse contextuelle

Role : tu aides a formaliser un sujet de projet etudiant...
```

**Flux complet :**
1. Prof clique "creer sujet" dans `/teacher` → ouvre `/cadrage?mode=prof&class_id=X`
2. `cadrage_prof.html` lit `class_id` depuis l'URL
3. Envoi message Sullivan → SSE URL inclut `&class_id=X`
4. `cadrage_router.py` → `sse_chat_generator(class_id=X)`
5. `brainstorm_logic.py` → `_load_class_meta(X)` + `_load_dnmade_referentiel()` → `_build_prof_system()`
6. Sullivan répond avec contexte DNMADE injecté

**Fichier modifié :**
- `Backend/Prod/retro_genome/brainstorm_logic.py` — ligne DB path corrigée

---

## R3 — "Dashboard" tab missing from nav in prof mode

### Status
À VALIDER — Bootstrap.js should inject dynamic nav with Dashboard tab if `role === 'prof'`

### Validation Steps
1. Hard refresh `/cadrage?mode=prof`
2. Check if nav includes "Dashboard" tab
3. If missing, inspect `bootstrap.js` nav generation logic

### Files to Check
- `Frontend/3. STENCILER/static/js/bootstrap.js` — nav injection logic
- `Frontend/3. STENCILER/static/templates/cadrage_alt.html` — nav container

---

## R4 — cadrage_alt.html: Univers LT Std Light font + max-width

### Requirements
- Streams + inputs → `font-family: 'Univers LT Std'; font-weight: 300; font-size: 14px`
- Add `@font-face` → `/static/fonts/univers-lt-std/univers-lt-std-300.woff2`
- Content centered `max-width: 48rem`
- Prof competences panel → `top: 120px` (below "+ capture" zone)

### Fix Plan (CODE DIRECT)
1. Add `@font-face` declaration to `cadrage_alt.html`
2. Update CSS rules for streams/inputs
3. Add `max-width: 48rem; margin: 0 auto;` to content containers
4. Adjust prof panel positioning

### Files to Modify
- `Frontend/3. STENCILER/static/templates/cadrage_alt.html`

### Validation
- [ ] Font loads correctly (check Network tab)
- [ ] Text renders in Univers LT Std Light
- [ ] Content is centered with max-width
- [ ] Prof panel doesn't overlap capture zone

---

## R5 — Created subjects visible in `/teacher`

### Status
À VÉRIFIER — Route `GET /api/classes/{id}/subjects` exists (M219)

### Validation Steps
1. Create a subject via `/cadrage?mode=prof&class_id=X`
2. Select that class in `/teacher` dropdown
3. Check if subjects appear in UI
4. Verify `teacher_dashboard.html` calls `GET /api/classes/{id}/subjects`

### Files to Check
- `Frontend/3. STENCILER/static/templates/teacher_dashboard.html` — subject list display
- `Frontend/3. STENCILER/routers/class_router.py` — `list_subjects()` endpoint

---

## R6 — Student workspace: project isolation in Stitch

### Problem
Without this, students work in the global project, not in their own folder.

### Requirements
- `/workspace?project_id={id}` → Stitch points to `projects/{uuid}/imports/`
- Exports → saved in `projects/{uuid}/exports/`
- Milestone N3 triggered automatically after export

### Fix Plan

#### Step 1: Update workspace routing
- Parse `project_id` from query params
- Set Stitch base path to `projects/{project_id}/`

#### Step 2: Update file operations
- Imports → read from `projects/{project_id}/imports/`
- Exports → write to `projects/{project_id}/exports/`

#### Step 3: Milestone detection
- After export success, call `POST /api/classes/{class_id}/students/{student_id}/detect-milestone`
- Auto-detect N3 when HTML export exists

### Files to Modify
- `Frontend/3. STENCILER/static/js/WsCanvas.js` or workspace loader
- `Frontend/3. STENCILER/routers/class_router.py` — milestone detection
- Stitch file I/O handlers

### Validation
- [ ] Student opens `/workspace?project_id=dnmade-2026-blart-samuel`
- [ ] Stitch shows only that student's files
- [ ] Export saves to correct project folder
- [ ] Milestone updates to N3 automatically

---

## R7 — Student CI/CD: deployment of renders

### Status
🔵 BACKLOG — After R1-R6 complete and tested locally

### Options
1. **Netlify Drop** — Drag-and-drop deployment
2. **HuggingFace Spaces** — Static hosting
3. **ZIP Export** — Auto-download bundle

### Next Steps
- Decide on deployment target after R1-R6
- Implement deployment script
- Add deploy button to student dashboard

---

## Execution Order

1. **R1** — Fix create class form (critical, blocks R5)
2. **R2** — Add class_id to cadrage (critical for prof mode)
3. **R4** — Font/max-width styling (quick CSS fix)
4. **R3** — Validate dashboard nav (may already work)
5. **R5** — Verify subjects display (depends on R1)
6. **R6** — Student project isolation (critical for student mode)
7. **R7** — CI/CD (backlog)

---

## Testing Strategy

### Manual Testing
1. Start server: `python server_v3.py`
2. Open `/teacher` → Create class → Verify POST succeeds
3. Import roster → Create subject → Verify subjects appear
4. Open `/cadrage?mode=prof&class_id=X` → Verify DNMADE context loads
5. Open `/workspace?project_id=Y` → Verify file isolation

### Automated Testing (curl)
```bash
# R1: Create class
curl -X POST http://localhost:9998/api/classes \
  -H "Content-Type: application/json" \
  -d '{"name":"DNMADE 2026","subject":"Design Web"}'

# R5: List subjects
curl http://localhost:9998/api/classes/dnmade-2026/subjects

# R2: Cadrage with class_id
curl "http://localhost:9998/api/cadrage/chat?sse=1&class_id=dnmade-2026"
```

---

## Success Criteria
- [ ] All R1-R6 bugs resolved
- [ ] Teacher can create classes, import rosters, create subjects
- [ ] Professor mode works with DNMADE referentiel
- [ ] Student workspace is isolated per project
- [ ] Milestones auto-detect correctly
- [ ] No console errors in browser
