# MISSION CONTROL : AETHERFLOW ROADMAP

> Missions complètes archivées dans [ROADMAP_ACHIEVED.md](./ROADMAP_ACHIEVED.md).

---

## Thème 0 — Hotfixes

### Mission 110 — Templates FRD : liste vide après manifest minimal

**STATUS: 🔴 HOTFIX**
**DATE: 2026-03-31**
**ACTOR: CLAUDE (CODE DIRECT)**

**Symptôme :** après création d'un manifest minimal depuis la landing, le sélecteur de templates dans frd_editor est vide.

**Diagnostic à mener :** vérifier l'endpoint qui alimente `#template-select` dans frd_editor — probablement un scan de répertoire conditionné à l'existence d'un manifest valide, ou un chemin qui change selon le projet actif.

**Critères de sortie :**
- [ ] Templates listés correctement après manifest minimal
- [ ] Pas de régression sur le flux normal (manifest complet)

---

## Thème 1 — Sullivan Typography Engine (suite)

### Mission 109C — Font Advisor + UI Landing

**STATUS: 🔵 BACKLOG**
**ACTOR: CLAUDE (routes + advisor) + GEMINI (UI landing.html)**
**DÉPENDANCE: M109A ✅ M109B ✅**

#### Routes `server_v3.py` (Claude)

```
POST /api/sullivan/font-upload   → multipart TTF/OTF/WOFF/WOFF2
                                  → classifier + webgen + advisor
                                  → { classification, webfont, sullivan_commentary }

GET  /api/sullivan/fonts         → liste fontes dans /static/fonts/
DELETE /api/sullivan/fonts/{slug} → supprime /static/fonts/{slug}/
```

#### `sullivan_font_advisor.py` (Claude)

Combine `FontClassifier` + `typography_db.json` → commentaire Sullivan :

> *"Axe oblique à 12°, contraste modéré (ratio 3.1), empattements à congé. Garalde — famille aldine. Proche de Sabon par la modération du contraste. Pour accompagner : privilégie un Grotesque humaniste plutôt qu'un Géométrique — l'un dialogue, l'autre concurrence."*

#### UI `landing.html` — section `#font-manager` (Gemini)

- Drop zone `.ttf/.otf/.woff/.woff2`
- Carte par fonte : badge Vox-ATypI + preview live + poids + warning licensing + commentaire Sullivan + snippet `@font-face` Monaco read-only
- Badge "variable font" si détecté
- Bouton "ajouter à stenciler.css"

**Bootstrap Gemini :**
```
Lire static/templates/landing.html — ne pas toucher les sections existantes.
Lire static/css/stenciler.css — tokens V1.
Lire Frontend/1. CONSTITUTION/LEXICON_DESIGN.json.
Ajouter UNIQUEMENT la section #font-manager après #import-section.
Pas d'uppercase. Pas d'emojis. Geist 12px. #8cc63f pour accents.
```

**Critères de sortie :**
- [ ] Upload `.otf` Garalde → classification "garaldes", axe ~12°, contraste ~3
- [ ] Upload variable font → `is_variable: true`, `font-weight: 100 900`
- [ ] Preview landing → fonte rendue live dans la carte
- [ ] Commentaire Sullivan → catégorie + référence proche + suggestion pairing
- [ ] Warning licensing sur fonte commerciale connue

---

## Thème 2 — Architecture User / Project

### Mission 111 — Multi-project scoping

**STATUS: 🔵 BACKLOG**
**DATE: 2026-03-31**
**ACTOR: CLAUDE (backend) + GEMINI (UI)**

**Contexte :** HoméOS est actuellement mono-projet global. En cours pédagogique, chaque étudiant travaille sur un projet distinct. Sans scoping, les imports, manifests et templates se mélangent.

#### Modèle de données

```python
# Table projects (SQLite ou JSON simple)
{
  "id": "uuid",
  "name": "Projet Clea",
  "user_id": "fjd",          # table users existante
  "created_at": "iso8601",
  "manifest_path": "exports/projects/{id}/manifest.json",
  "imports_dir": "exports/projects/{id}/imports/",
  "active": true             # un seul actif à la fois par user
}
```

#### Routes backend (Claude)

```
GET    /api/projects              → liste projets de l'user courant
POST   /api/projects              → créer projet { name }
POST   /api/projects/{id}/activate → set active, désactive les autres
DELETE /api/projects/{id}         → supprime projet + fichiers
GET    /api/projects/active       → projet actif courant
```

#### Scoping du pipeline

Tous les endpoints existants reçoivent le `project_id` depuis la session :
- `POST /api/import/upload` → sauvegarde dans `imports_dir` du projet actif
- `GET /api/manifest/get` → lit depuis `manifest_path` du projet actif
- `POST /api/preview/run` → preview isolée par projet
- Wire mode, intent analysis → scopés au projet actif

#### UI (Gemini)

- Landing : sélecteur de projet en tête de page + bouton "nouveau projet"
- Header global (bootstrap.js) : nom du projet actif affiché à droite des tabs

**Bootstrap Gemini :**
```
Lire static/templates/landing.html.
Lire static/js/bootstrap.js — ajouter projet actif dans .hn-brand ou pipeline-actions.
Lire Frontend/1. CONSTITUTION/LEXICON_DESIGN.json.
NE PAS modifier le drop zone ni les sections existantes.
```

**Critères de sortie :**
- [ ] Deux projets distincts avec imports, manifests et previews isolés
- [ ] Switching de projet → pipeline complet rebascule sans collision
- [ ] Projet actif visible dans le header global
- [ ] Nouveau projet → landing vierge (pas d'imports résiduels)

---

## Thème 3 — UX Cléa

**REF:** `docs/06_Design_Assets/ergonomic_study_clea_ux.md`
**REF:** `docs/06_Design_Assets/CORPUS_UX_CLEA.md`

### Mission 112 — Sullivan Welcome Screen

**STATUS: 🔵 BACKLOG**
**ACTOR: CLAUDE (endpoint) + GEMINI (landing.html)**
**DÉPENDANCE: M111 (scoping projet)**

Remplacer l'austère liste d'imports par un accueil sémantique Sullivan. *Effet de Halo* (Cléa UX P1).

#### Route backend (Claude)

```
GET /api/project/summary
→ {
    "project_name": "Projet Clea",
    "imports_count": 3,
    "last_intent": "formulaire de contact",
    "manifest_status": "ok" | "missing" | "minimal",
    "message": "3 écrans importés. Dernière intention : formulaire de contact."
  }
```

#### UI (Gemini)

- Zone `#sullivan-welcome` en tête de landing : nom projet + message Sullivan contextuel
- Remplacement badge polling par nudge discret orienté action

**Bootstrap Gemini :**
```
Lire static/templates/landing.html.
Lire static/css/stenciler.css.
Lire Frontend/1. CONSTITUTION/LEXICON_DESIGN.json.
Ajouter UNIQUEMENT #sullivan-welcome avant #import-section.
Pas d'uppercase. Pas d'emojis. Geist 12px.
```

**Critères de sortie :**
- [ ] Message Sullivan contextuel au chargement de la landing
- [ ] Mis à jour quand le projet change (M111)
- [ ] Pas de régression sur la drop zone

---

### Mission 113 — Sullivan Tips + Smart Nudges

**STATUS: 🔵 BACKLOG**
**ACTOR: CLAUDE (nudge engine) + GEMINI (UI)**
**DÉPENDANCE: M109A (typography_db.json)**

Utiliser les temps morts pour valoriser. *Intent Context Loading + Smart Nudges* (Cléa UX P3+P4).

#### Route backend (Claude)

```
GET /api/sullivan/tip
→ { "tip": "Les Garaldes portent un axe oblique hérité de la plume...", "source": "garaldes" }
```

Tips tirés de `typography_db.json` : `cultural_refs[]` + `pairings[]` de chaque catégorie (~50 tips disponibles).

Nudges Wire : pendant l'analyse, si route orpheline détectée → nudge non-bloquant.

#### UI (Gemini)

- Loading overlay Intent Viewer : tip Sullivan affiché pendant l'analyse SVG
- FRD header : nudge discret (toast 3s, non-bloquant) sur routes orphelines

**Bootstrap Gemini :**
```
Lire static/templates/intent_viewer.html — ajouter tip dans le loading state existant.
Lire static/css/frd_editor.css — ajouter toast style non-bloquant.
Lire Frontend/1. CONSTITUTION/LEXICON_DESIGN.json.
```

**Critères de sortie :**
- [ ] Tip typographique affiché pendant chaque analyse Intent Viewer
- [ ] Tips variés (pas toujours le même) — rotation aléatoire
- [ ] Nudge route orpheline : toast discret, disparaît seul après 3s
- [ ] Pas de régression sur les loaders existants

---

## Thème 4 — FRD Canvas v2 : features Stenciler portées

### Mission 114 — FRD Canvas v2 : snap grid + zoom + resize

**STATUS: 🔵 BACKLOG**
**DATE: 2026-03-31**
**ACTOR: CLAUDE (FrdWire.feature.js) + GEMINI (UI controls)**
**DÉPENDANCE: M112 + M113 (réfection UX Cléa accomplie)**

**Contexte :** Le Stenciler V3 a développé un moteur canvas SVG solide sur plusieurs missions (8C→14B). Ces features sont portables dans le FRD editor car FrdWire.feature.js est déjà en SVG natif. L'objectif n'est pas de copier le Stenciler mais d'enrichir le wire mode avec les interactions qui font sens pour un éditeur HTML/template.

**Features retenues (validées dans Stenciler)**

| Feature | Source Stenciler | État source | Travail de portage |
|---|---|---|---|
| Snap grid 8px | `_snap()` + `GRID.js` | ✅ solide | Minimal — greffer sur drag FrdWire |
| Zoom / panning | `_setupZoomControls()` + space+drag | ✅ solide | Copier-coller méthodes, adapter viewBox |
| Resize handles (rect) | `_showHandles()` | ✅ solide | Portable, uniquement `<rect>` |
| Drag nodes SVG | `_setupDragHandlers()` | ✅ solide | FrdWire a déjà du drag — unifier |
| Delete node | `_setupDeleteHandlers()` | ✅ trivial | Compléter raccourci clavier |

**Features exclues (trop couplées au genome Stenciler)**
- Drill-down Corps/Organe/Cellule — sémantique incompatible avec FRD (HTML templates, pas genome)
- Apply color broadcast — à concevoir différemment dans un contexte CSS/Tailwind
- Fond gradué — chantier UI complet, pas une feature de portage

**Livrables backend (Claude — CODE DIRECT)**

`FrdWire.feature.js` :
- Intégrer `GRID.js` (import ou copie inline des constantes)
- `_snap(v)` — arrondi 8px, activable via toggle
- `_setupZoom()` — boutons +/−/reset, viewBox scaling sur `#preview-iframe` SVG overlay
- `_setupPan()` — Space+drag sur le canvas wire
- `_setupResizeHandles()` — 4 coins sur `<rect>` sélectionnée, Shift = aspect ratio lock
- Unifier drag existant avec snap

**Livrables UI (Gemini — frd_editor.html + frd_editor.css)**

Barre de contrôles canvas (intégrée dans le header FRD existant) :
- Bouton grid toggle (icône grille, actif = vert HoméOS)
- Bouton snap toggle
- Affichage zoom % (ex: "100%")
- Boutons +/− zoom

**Bootstrap Gemini :**
```
Lire static/templates/frd_editor.html — header existant avec Inspect/Lock/Save.
Lire static/css/frd_editor.css — ne pas casser les styles existants.
Lire Frontend/1. CONSTITUTION/LEXICON_DESIGN.json.
Ajouter UNIQUEMENT les contrôles canvas dans le header FRD (après btn-lock, avant template-select).
Pas d'uppercase. Pas d'emojis. Geist 12px.
```

**Critères de sortie :**
- [ ] Drag wire node → snap automatique sur grille 8px
- [ ] Space+drag → pan du canvas wire
- [ ] Boutons +/− → zoom viewBox du SVG wire
- [ ] Clic `<rect>` → handles sur 4 coins, redimensionnement
- [ ] Grid toggle → grille SVG visible/cachée
- [ ] Pas de régression sur wire mode existant (M97→M103)

---

## Backlog long terme

| Mission | Description | Dépendances |
|---|---|---|
| M75-A | BKD Frontend : bkd_editor.html complet | — |
| M75-B | Extension VS Code `aetherflow-bkd` | M75-A |
| M75-C | Dockerfile code-server | M75-B |
| M88 | Refactorisation frd_editor.html V3 modulaire | M103 |
| M89 | Sullivan FRD : simplification UI + Wire→Construct | M103 |
| M90 | BKD : route `/api/bkd/files` + explorateur réel | — |
| M95 | Sullivan → api_generator : déploiement auto archetypes | M92 |
