# MISSION CONTROL : AETHERFLOW ROADMAP

> Missions complètes archivées dans [ROADMAP_ACHIEVED.md](./ROADMAP_ACHIEVED.md).

---

## Thème 0 — Hotfixes

> M121 ✅, M116 ✅, M122 ✅, M123 ✅, M124 ✅, M125 ✅, M126 ✅, M127 ✅ — archivées dans ROADMAP_ACHIEVED.md (2026-04-01)

### Mission 125 — DELETE /api/imports/{id}
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---

### Mission 126 — Cascade LLM : gemini-3.1-flash-lite en queue
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---

## Thème 6 — Refonte FRD : Canvas Workspace Unifié

### Mission 128 — Bridge DESIGN.md → tokens projet dynamiques

**STATUS: 🔵 BACKLOG**
**DATE: 2026-04-01**
**ACTOR: CLAUDE (CODE DIRECT — server_v3.py + svg_to_tailwind.py) + GEMINI (landing.html)**
**DÉPENDANCE: aucune (indépendant de M127)**

**Contexte :** HoméOS a son propre format `DESIGN.md` (défini dans `docs/06_Design_Assets/assets/sullivan_editor_base_accurate/DESIGN.md`). Ce fichier documente le design system d'un projet (palette, typo, formes). En l'uploadant dans HoméOS, tous les appels LLM suivants (génération SVG→HTML, vision PNG) utilisent les tokens du projet au lieu des tokens HoméOS par défaut. Ce bridge positionne HoméOS en **continuité de Stitch** : même design system, même vocabulaire.

#### Format DESIGN.md HoméOS (référence : sullivan_editor_base_accurate/DESIGN.md)

Sections parsées :

```markdown
### Palette de Couleurs
- **Primary (...)** : `#A3CD54`   → colors.primary
- **Backgrounds** : blanc pur     → colors.neutral (fallback #ffffff)
- **Texts** : gris anthracite     → colors.text (fallback #1a1a1a)

### Typographie
- **Police de caractères** : `Source Sans 3`  → typography.body
- **Display/Headlines** : Semi-bold           → typography.headline_weight

### Formes & Structure (Shape)
- **Border Radius** : `20px`       → shape.border_radius
```

Parser : regex `\*\*[^*]+\*\*\s*:\s*` + extraction hex `#[0-9a-fA-F]{3,6}` + backtick values.

#### Livrable A — Routes backend (server_v3.py) — Claude

```
POST /api/project/import-design-md
Body: multipart (file)

→ Parse le DESIGN.md selon le format HoméOS
→ Produit exports/design_tokens.json :
  {
    "colors": { "primary": "#A3CD54", "neutral": "#ffffff", "text": "#1a1a1a" },
    "typography": { "body": "Source Sans 3", "headline_weight": "600" },
    "shape": { "border_radius": "20px" },
    "source": "homeos_design_md",
    "imported_at": "2026-04-01T..."
  }
→ Retourne { "status": "ok", "tokens": {...} }

GET /api/project/design-tokens
→ Retourne design_tokens.json si présent
→ Sinon retourne defaults HoméOS :
  { "colors": { "primary": "#8cc63f", "neutral": "#f7f6f2", "text": "#3d3d3c" },
    "typography": { "body": "Geist" }, "shape": { "border_radius": "6px" } }
```

#### Livrable B — Injection tokens dans les prompts LLM (svg_to_tailwind.py) — Claude

Ajouter `load_project_tokens()` (lit `design_tokens.json` ou retourne defaults) et l'appeler dans `convert()` + `convert_image()` :

```python
async def load_project_tokens() -> dict:
    path = ROOT_DIR / "exports" / "design_tokens.json"
    if path.exists():
        return json.loads(path.read_text())
    return DEFAULT_TOKENS  # HoméOS defaults

# Dans les prompts, remplacer les valeurs hardcodées :
t = await load_project_tokens()
f"- Accent / Primary : `{t['colors']['primary']}`"
f"- Background : `{t['colors']['neutral']}`"
f"- Texte : `{t['colors']['text']}`"
f"- Typographie : {t['typography']['body']}"
f"- Border-radius : {t['shape']['border_radius']}"
```

#### Livrable C — Upload depuis la landing (Gemini)

Bouton discret "design system" dans le header landing :
- Clic → `<input type="file" accept=".md">` → `POST /api/project/import-design-md`
- Au chargement : `GET /api/project/design-tokens` → si `source == "homeos_design_md"` → pastille couleur `primary` + label "design actif"

**Bootstrap Gemini :**
```
Lire static/templates/landing.html — header existant.
Ajouter UNIQUEMENT : bouton "design system" discret (texte 11px, ghost) dans le header.
Au clic → file input .md → POST /api/project/import-design-md.
Au chargement → GET /api/project/design-tokens → si source présent → pastille ronde couleur primary (16px).
Lire static/css/stenciler.css — tokens V1. Pas d'uppercase. Geist 12px.
```

**Fichiers :**
- `Frontend/3. STENCILER/server_v3.py` — Livrable A
- `Backend/Prod/retro_genome/svg_to_tailwind.py` — Livrable B
- `static/templates/landing.html` — Livrable C (Gemini)

**Critères de sortie :**
- [ ] Upload `DESIGN.md` HoméOS → `design_tokens.json` créé avec primary + neutral + typo parsés
- [ ] `GET /api/project/design-tokens` → tokens parsés ou defaults HoméOS
- [ ] Génération SVG/PNG suivante → prompt LLM utilise les tokens du projet (pas hardcodés)
- [ ] Landing : pastille seed color visible si design importé
- [ ] Pas de régression si aucun DESIGN.md (defaults HoméOS inchangés)

---

### Mission 127 — Workspace V1 (Shell + Canvas Engine)

**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md
**DATE: 2026-04-01 | ACTOR: GEMINI + CLAUDE**

---

### Mission 129 — Workspace : features layer 2

**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md
**DATE: 2026-04-01 | ACTOR: GEMINI + CLAUDE**

---

### Mission 130-A — Header Minimal + Mode Aperçu Plein Écran

**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md
**DATE: 2026-04-01 | ACTOR: CLAUDE**

---

### Mission 130-B — Boutons Aperçu & Save par Screen

**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md
**DATE: 2026-04-01 | ACTOR: CLAUDE**

---

### Mission 130-C — Fix Robuste Panneaux Latéraux

**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md
**DATE: 2026-04-01 | ACTOR: CLAUDE**

---

### Mission 130 — Mode Inspect In-Preview & Monaco Popover

**STATUS: 🔵 BACKLOG**
**DATE: 2026-04-01**
**ACTOR: CLAUDE + GEMINI**
**DÉPENDANCE: M130-A/M130-B ✅ (Mise en place de l'aperçu)**

**Contexte :** Le tiroir latéral de code massif est abandonné au profit d'une expérience d'édition ultra-ciblée. Une fois entré dans le **Mode Aperçu (Plein Écran)** d'un screeen, le `Mode Inspect` (tel qu'il a été implémenté historiquement dans le FRD Editor via `FrdPreview.feature.js`) s'active **par défaut**. Au clic sur un élément dans l'aperçu, un éditeur Monaco flottant ("popover" ou bulle) apparaît au flanc immédiat de l'élément cliqué. Il ne contient **que** le code HTML (extrait) correspondant au composant inspecté.

**Livrables :**
1. **Activation Inspecteur (In-Preview) :** Au déclenchement du Preview, injection de la logique `Inspect Mode` avec highlight visuel au survol des éléments de l'iframe.
2. **Popover Monaco Contextuel :** Cible sélectionnée → apparition d'un conteneur flottant à proximité directe (via Popper.js ou calcul de bounding client rect).
3. **Édition d'Extrait (Grafting) :** Ce Monaco ne parse que l'outerHTML du nœud cible. À la sauvegarde (`Cmd+S` ou bouton check), l'extrait modifié remplace proprement le nœud dans le DOM distant (Server-side ou via postMessage direct) et le composant se met à jour localement.
4. **Cohérence Ergonomique :** Design de la bulle Monaco discret et raccord au design système HoméOS.

---

---

### Mission 131 — Exclusivité des Outils en Mode Aperçu & Nettoyage

**STATUS: 🔵 BACKLOG**
**DATE: 2026-04-01**
**ACTOR: GEMINI + CLAUDE**
**DÉPENDANCE: M130 🔵**

**Contexte :** Les outils de la barre d'outils ne doivent être accessibles et opérables qu'**une fois en mode aperçu**. Toute notion d'aperçu global dans la toolbar doit définitivement disparaître car cela créerait des conflits avec le mode Aperçu par écran nouvellement implémenté (130-A/B).

**Livrables :**
1. **Verrouillage de la Toolbar :** Rendre la barre d'outils droite invisible ou désactivée sur le canvas principal, pour ne l'activer que lorsque `enterPreviewMode` a été déclenché.
2. **Nettoyage UI :** Suppression radicale de toute icône ou bouton "Aperçu" redondant dans la toolbar ou le header principal.

---

### Mission 132 — Outils de Manipulation (Drag, Déplacer, Cadre, Place Image)

**STATUS: 🔵 BACKLOG**
**DATE: 2026-04-01**
**ACTOR: CLAUDE**
**DÉPENDANCE: M131 🔵**

**Contexte :** Donner vie aux outils présents dans la toolbar pour manipuler le DOM du screen actuellement en mode aperçu.

**Livrables :**
1. **Flèche de sélection :** Sélection d'éléments spécifiques dans le screen (DOM) et autorisation du "drag" de ces éléments de manière ciblée.
2. **Outil Déplacer (Hand) :** Permet de "pan" directement dans la vue si l'écran dépasse.
3. **Outil Cadre :** Tracé d'un block DIV ou conteneur HTML structurant directement via clic-glissé.
4. **Outil Place Image :** Input file ouvrant et insertion d'une balise `<img src="...">` avec l'asset à l'endroit cliqué.

---

### Mission 133 — Undo & Mode "Couleur TSL" local homéOS

**STATUS: 🔵 BACKLOG**
**DATE: 2026-04-01**
**ACTOR: CLAUDE**
**DÉPENDANCE: M132 🔵**

**Contexte :** Implémenter l'annulation des actions lors de l'édition ainsi que la colorisation sémantique cohérente avec HoméOS.

**Livrables :**
1. **Pile d'historique (Undo) :** Mémoriser les modifications DOM (positions, ajout cadre, source images) pour rollback (Cmd Z).
2. **Outil Color Apply (TSL) :** Interface pour appliquer des couleurs TSL (Teinte, Saturation, Luminosité). Ce color picker devra se baser rigoureusement sur les palettes / échelles stipulées dans `design.md` HoméOS.

---

### Mission 134 — Arsenal Typo (System Fonts & Webfont Generator)

**STATUS: 🔵 BACKLOG**
**DATE: 2026-04-01**
**ACTOR: CLAUDE + GEMINI**
**DÉPENDANCE: M133 🔵**

**Contexte :** Gérer l'ajout de cadres de texte et la sélection de la typographie de manière ultra-locale, avec génération finale des fonts au moment du `save`.

**Livrables :**
1. **Outil Texte :** Création de zones de texte directement dans l'aperçu.
2. **Sélecteur de System Fonts :** Interface lisant et proposant la sélection directe des polices installées sur la machine de l'utilisateur (via Local Font Access API).
3. **Hook de Sauvegarde (Webfont Generator) :** Lors du `save` du screen, extraire les polices système choisies et déclencher l'API Backend `Webfont Generator` (via `font_webgen.py` de la M109B) pour packager, subsetter et générer les `@font-face` CSS finaux.

---

### Mission 124 — Fallback Mimo après quota Gemini épuisé
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---

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

**STATUS: ✅ LIVRÉ**
**DATE: 2026-03-31**

> Archivée dans ROADMAP_ACHIEVED.md

---

## Thème 2 — Architecture User / Project

**Contexte :** HoméOS est actuellement mono-projet global. En cours pédagogique, chaque étudiant travaille sur un projet distinct. Sans scoping, imports, manifests et templates se mélangent.

**Stratégie de découpage :** deux passes pour limiter le risque de régression. M111-A = backend pur (sans toucher les URLs). M111-B = UI sur base stable.

**Structure cible :**
```
ROOT_DIR/
  projects/
    {uuid}/
      manifest.json
      imports/
      exports/
      metadata.json     ← { id, name, created_at }
  static/fonts/         ← global (partagé entre projets)
```

---

### Mission 111-A — Multi-project : backend isolation

**STATUS: 🔵 BACKLOG**
**DATE: 2026-03-31**
**ACTOR: CLAUDE (CODE DIRECT)**

**Périmètre strict :** `server_v3.py` uniquement. Pas de changement d'URL. Le `project_id` transite par **session FastAPI** (cookie côté serveur), pas en query param.

#### Modèle de données

```python
# projects/{uuid}/metadata.json
{
  "id": "uuid4",
  "name": "Projet Cléa",
  "created_at": "2026-03-31T14:00:00",
}
# Session FastAPI : request.session["active_project_id"] = uuid
```

#### Helper de résolution de chemin

```python
def get_project_dir(project_id: str) -> Path:
    return ROOT_DIR / "projects" / project_id

def get_manifest_path(project_id: str) -> Path:
    return get_project_dir(project_id) / "manifest.json"

def get_imports_dir(project_id: str) -> Path:
    return get_project_dir(project_id) / "imports"
```

#### Migration douce au démarrage

```python
# lifespan() : si ROOT_DIR/exports/manifest.json existe → créer projet "default"
# et y copier manifest + imports/ (sans supprimer les originaux)
# → session["active_project_id"] = "default"
```

#### Routes à ajouter

```
GET    /api/projects              → liste { id, name, created_at }[]
POST   /api/projects              → { name } → créer dossier + metadata.json
POST   /api/projects/{id}/activate → session["active_project_id"] = id
DELETE /api/projects/{id}         → supprime dossier (sécurité : pas le projet actif)
GET    /api/projects/active       → { id, name } du projet en session
```

#### Endpoints existants à scoper (session-based, sans changer leur signature)

```
GET  /api/manifest/get            → lit get_manifest_path(session[active_project_id])
POST /api/manifest/save           → écrit idem
POST /api/import/upload           → sauvegarde dans get_imports_dir(session[...])
GET  /api/retro-genome/imports    → liste depuis get_imports_dir(session[...])
POST /api/preview/run             → isolée par projet (sous-dossier exports/)
```

**Ne pas toucher :**
- URLs existantes (aucun `?p=` en query param)
- `frd/files` (templates FRD = globaux, pas scopés au projet)
- `static/fonts/` (global)
- `bkd_service.py` (hors périmètre M111-A)
- Toute logique JS frontend

**Critères de sortie :**
- [ ] `POST /api/projects` → crée `projects/{uuid}/` + `metadata.json` + `imports/`
- [ ] `POST /api/projects/{id}/activate` → session mise à jour
- [ ] `GET /api/manifest/get` → lit dans le bon dossier projet
- [ ] Migration douce : si manifest racine existe → projet "default" créé au boot
- [ ] Test manuel : deux sessions browser → projets distincts, pas de collision

---

### Mission 111-B — Multi-project : UI landing + header

**STATUS: 🔵 BACKLOG**
**DÉPENDANCE: M111-A ✅**
**ACTOR: GEMINI (landing.html + bootstrap.js)**

#### UI landing.html

- Section `#project-switcher` en tête (avant `#import-section`) :
  - Liste des projets (`GET /api/projects`) → cartes cliquables
  - Bouton "nouveau projet" → prompt nom → `POST /api/projects` + activate
  - Projet actif surligné (bordure `#8cc63f`)
- Import scoping : `handleFiles` passe le projet actif (via état JS, pas URL)

#### UI bootstrap.js / header global

- Afficher le nom du projet actif à droite des tabs (petit texte 11px, couleur `#8cc63f`)
- Fetch `GET /api/projects/active` au chargement

**Bootstrap Gemini :**
```
Lire static/templates/landing.html — NE PAS toucher drop zone ni import-section.
Lire static/js/bootstrap.js — ajouter nom projet actif dans .pipeline-actions (droite).
Lire static/css/stenciler.css — tokens V1.
Lire Frontend/1. CONSTITUTION/LEXICON_DESIGN.json.
Pas d'uppercase. Pas d'emojis. Geist 12px. #8cc63f accents.
NE PAS ajouter ?p= dans les URLs.
```

**Critères de sortie :**
- [ ] Deux projets distincts → imports et manifests isolés sans collision
- [ ] Switching projet depuis la landing → pipeline rebascule

- [ ] Nom du projet actif visible dans le header global
- [ ] Nouveau projet → landing vierge (aucun import résiduel du projet précédent)

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

## Thème 5 — Pipeline landing → FRD : fluidité de base

### Mission 115 — Bouton "éditer" global + template courant dans FRD

**STATUS: 🔴 HOTFIX**
**DATE: 2026-03-31**
**ACTOR: GEMINI (landing.html + frd_editor.html)**

**Contexte :** Deux frictions bloquantes sur le pipeline de base :
1. La landing affiche des boutons "éditer" par intention — ce découpage par intent n'a pas de sens à ce stade. Il faut un seul bouton "ouvrir dans le FRD editor" par import.
2. Quand on arrive dans le FRD editor, le template en cours de travail n'est pas retrouvé automatiquement — le `#template-select` est vide ou désynchronisé.

#### Livrable A — landing.html : bouton "éditer" global par import (Gemini)

Remplacer les boutons par-intent par un seul bouton par carte d'import :
```
[ ouvrir dans frd editor ]  →  /frd-editor (+ marque le fichier comme courant)
```
- Un clic → `POST /api/frd/set-current { name: filename }` puis `window.location = '/frd-editor'`
- Pas d'édition inline par intent sur la landing

#### Livrable B — server_v3.py : route `set-current` (Claude CODE DIRECT)

```
POST /api/frd/set-current   { name: str }  →  stocke en mémoire _CURRENT_FRD_FILE
GET  /api/frd/current       →  { name: str | null }
```

#### Livrable C — frd_editor.html : auto-charger le fichier courant (Gemini)

Au chargement de `frd_editor.html` :
```javascript
// init() → GET /api/frd/current → si name → loadFile(name) + select dans #template-select
```

**Critères de sortie :**
- [ ] Clic "ouvrir dans frd editor" sur une carte import → arrive dans FRD avec le bon fichier chargé
- [ ] `#template-select` pointe sur le fichier courant
- [ ] Pas de régression sur le chargement manuel depuis `#template-select`

---

### Mission 116 — Fix pipeline intent_viewer → FRD editor
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---

### Mission 117 — Fusion Intent → FRD : Analyse Intégrée

**STATUS: ✅ LIVRÉ**
**DATE: 2026-03-31**
**ACTOR: GEMINI (frontend) + CLAUDE (backend updates)**
**DÉPENDANCE: M116 (pipeline landing → FRD corrigé)**

**Contexte :** L'écran séparé `intent_viewer.html` crée une rupture dans le flux créatif. L'objectif est de fusionner ses fonctionnalités dans l'Éditeur FRD. Lorsqu'un utilisateur ouvre un **Import de référence**, il ne doit pas être envoyé vers un visualiseur passif, mais vers l'Éditeur qui se configure en mode "Analyse".

#### Livrable A — frd_editor.html : Panneau d'Analyse (Gemini)

- Ajout d'un panneau latéral `#intent-panel` (drawer à gauche ou à droite, stylisé HoméOS).
- Intégration du tableau interactif des intentions (Intention / Archetype / Target / Action).
- Badge de statut de l'analyse (Validé / À réviser).

#### Livrable B — FrdIntent.feature.js : Module d'Analyse (Gemini)

- Nouveau module portable encapsulant la logique de `intent_viewer.html` :
  - `fetchIntents(importId)` → récupère `index.json` + `analysis.json` via `/api/retro-genome/import-analysis-svg`.
  - `renderIntents()` → peuple le tableau dans `#intent-panel`.
  - `annotateIntent(id, annotation)` → persiste les modifications via `/api/retro-genome/validate`.

#### Livrable C — frd_main.js : Orchestration (Gemini)

- Au chargement (`init`) : si `ctx.type === 'import'`, activer automatiquement le module `intent` et ouvrir le panneau.
- **Sullivan Autostart** : Sullivan détecte l'import et propose proactivement : *"bonjour. je vois votre import figma. voici les intentions détectées. voulez-vous que je génère la structure tailwind correspondante ?"*

#### Livrable D — server_v3.py : Helper de génération (Claude CODE DIRECT)

- Endpoint `POST /api/frd/generate-initial` :
  - Prend `import_id` en entrée.
  - Exécute `HtmlGenerator.generate()` (Mission 35) pour produire le premier jet `reality.html`.
  - Sauvegarde le fichier dans `static/templates/` et bascule le contexte courant sur ce nouveau template.

**Critères de sortie :**
- [x] Landing -> Ouvrir import SVG -> Arrive dans FRD -> Panneau d'analyse ouvert automatiquement.
- [x] Mockup SVG visible dans le canvas de droite (Mode Référence).
- [x] Sullivan propose la génération Tailwind dans le chat.
- [x] Validation des intentions persiste entre les sessions.
- [x] Pas de régression sur l'édition de templates HTML existants.

**COMPTE RENDU (CR) DE MISSION :**
- Fusion réussie : L'Intent Viewer est maintenant un élément natif de l'Éditeur FRD sous forme de slider animé.
- Introduction du **Protocole SVG AI**, une couche cruciale de dé-obfuscation pour traiter les exports vectoriels d'Adobe Illustrator sans surcharger le contexte LLM.
- **Sullivan** est proactif : branché au bouton de génération dans le panneau d'analyse, il déclenche directement `/api/retro-genome/generate-html` et bascule l'éditeur en code (`.html`) dès que la réponse est prête.
- Le cycle Architecte -> Intégrateur -> DA est préservé, mais l'expérience UI est unifiée.

---

### Mission 118 — Pont SVG Illustrator → Tailwind Direct

**STATUS: ⚠️ PARTIEL — M118-B requis**
**DATE: 2026-03-31**
**ACTOR: CLAUDE (CODE DIRECT — backend uniquement)**
**DÉPENDANCE: M117 (panneau d'analyse FRD)**

**Contexte :** Le pipeline de génération existant (`/api/retro-genome/generate-html`) est conçu pour des PNGs uploadés via Retro Genome, pas pour des SVG Illustrator. Il nécessite Playwright, un cycle QA en plusieurs passes, et sauvegarde dans `/exports/retro_genome/` (hors de `static/templates/`). L'objectif de cette mission est de créer un **pont direct** SVG→Tailwind, plus simple et adapté au workflow landing → FRD Editor.

#### Livrable A — Nouveau module `svg_to_tailwind.py` (Claude)

Fichier : `Backend/Prod/retro_genome/svg_to_tailwind.py`

```python
async def convert(svg_content: str, import_name: str) -> str:
    """
    Protocole SVG AI (v1.0) + appel LLM direct.
    1. Filtrage du bruit : strip <font>, <glyph>, <image> base64
    2. Décodage .stX : mapper les classes CSS vers les tokens HoméOS
    3. Extraction des <text> et <rect>/<path> structurants (viewBox zones)
    4. Prompt LLM : "Traduis cette structure SVG annotée en HTML sémantique Tailwind"
    5. Retourne le HTML complet
    """
```

Contraintes du prompt LLM :
- Stack : HTML5 + Tailwind CDN
- Tokens HoméOS : `#f7f6f2` bg, `#3d3d3c` texte, `#8cc63f` accent
- Pas de largeurs fixes en px, Flexbox/Grid obligatoire
- Résultat : document HTML complet autonome (`<!DOCTYPE html>`)

#### Livrable B — Nouvelle route dans `routes.py` (Claude)

```python
POST /api/retro-genome/generate-from-svg
Body: { "import_id": str }

→ Lit le SVG via index.json + svg_path
→ Appelle svg_to_tailwind.convert()
→ Sauvegarde le résultat dans static/templates/{safe_name}.html
→ Retourne { "template_name": str, "status": "ok" }
```

**Important :** Le fichier généré doit être sauvegardé dans `static/templates/` (pas dans `/exports/`) pour être lisible par `GET /api/frd/file?name=...`.

#### Livrable C — Feedback temps réel : SSE ou polling (Claude)

La génération dure plusieurs secondes (appel LLM long). Implémenter l'une des deux options :
- **Option A (préférée)** : L'endpoint retourne immédiatement un `job_id`, puis `GET /api/retro-genome/svg-job/{job_id}` retourne `{ status: "pending"|"done", template_name? }`.
- **Option B (simple)** : L'endpoint est synchrone mais retourne immédiatement `{ status: "started" }` et le frontend poll `/api/frd/current` jusqu'à ce que `html_template` soit renseigné.

#### Ce que GEMINI fera ensuite (M119)

Une fois la route opérationnelle, connecter `FrdIntent.generateTailwind()` sur `/api/retro-genome/generate-from-svg` et ajouter l'indicateur de chargement dans Sullivan Chat.

**Fichiers à créer/modifier :**
- `Backend/Prod/retro_genome/svg_to_tailwind.py` **[NEW]**
- `Backend/Prod/retro_genome/routes.py` — ajout route `generate-from-svg` **[MODIFY]**

**Critères de sortie :**
- [ ] `POST /api/retro-genome/generate-from-svg` avec `import_id` valide → retourne `{ template_name: "...", status: "ok" }`
- [ ] Le fichier `.html` généré est présent dans `static/templates/`
- [ ] `GET /api/frd/file?name={template_name}` → 200 avec le contenu HTML Tailwind
- [ ] Le HTML généré contient des tokens HoméOS (couleurs, Geist, lowercase)
- [ ] Pas de modification de la route `/generate-html` existante

---

### Mission 118-B — Routeur de formats d'import + prompts adaptatifs

**STATUS: 🔵 BACKLOG**
**DATE: 2026-03-31**
**ACTOR: CLAUDE (CODE DIRECT — `svg_to_tailwind.py` + `routes.py`)**
**DÉPENDANCE: M118 (module `svg_to_tailwind.py` existant)**

**Contexte :** Le pipeline actuel est aveugle au format source. Il traite tous les SVG de la même façon et dit au LLM "lis les `<text>`" même quand il n'y en a pas (SVG vectorisé). Résultat : lorem ipsum systématique sur les exports Illustrator.

**5 formats à router, 5 stratégies distinctes :**

| Format | Signal de détection | Stratégie |
|---|---|---|
| **Illustrator SVG vectorisé** | `<text>=0` + classes `.stX` | Inférence structurelle par couleurs |
| **Figma SVG** | `<text>` présents + `id="node-/frame-"` | Lecture directe texte + hiérarchie |
| **HTML/CSS ZIP** | `.zip` + `.html` dedans, pas de `.tsx` | Extraction HTML principal + inline CSS |
| **React/ZIP** | `.zip` + `.tsx/.jsx` dedans | M119 (transpilation JSX→HTML) |
| **PNG/JPG** | extension image | Pipeline Playwright existant (hors scope) |

#### Livrable A — `detect_import_format(content, filename)` dans `svg_to_tailwind.py`

```python
def detect_svg_type(svg_content: str) -> str:
    has_text  = bool(re.search(r'<text', svg_content))
    has_stx   = bool(re.search(r'\.(st\d+)', svg_content))
    has_figma = bool(re.search(r'id="node-|id="frame-', svg_content))
    if not has_text and has_stx: return "illustrator_vectorized"
    if has_figma:                return "figma"
    if has_text:                 return "structured_svg"
    return "unknown"
```

#### Livrable B — Prompt adaptatif selon le type dans `convert()`

**illustrator_vectorized** : extraire palette couleurs + rects + viewBox → décrire la structure au LLM sans lui envoyer le SVG brut :
```python
color_freq = Counter(re.findall(r'fill="(#[0-9a-fA-F]{3,6}|white)"', svg_content))
rects = re.findall(r'<rect[^/]*/>', svg_content)
viewbox = re.search(r'viewBox="([^"]+)"', svg_content)
# Prompt : "Ce SVG est vectorisé. Palette : ... Rects : ... Interface de type [nom_fichier]. Génère le HTML."
```

**figma / structured_svg** : prompt actuel (déjà bon, il y a du `<text>` à lire).

#### Livrable C — Route `generate-from-svg` dans `routes.py` : router ZIP

Actuellement la route ne gère que les SVG depuis `index.json`. Ajouter :
- Si `entry["name"]` se termine en `.zip` → extraire l'archive en mémoire → détecter React vs HTML/CSS → appeler le bon convertisseur

**Fichiers :**
- `Backend/Prod/retro_genome/svg_to_tailwind.py` — A + B
- `Backend/Prod/retro_genome/routes.py` — C

**Critères de sortie :**
- [ ] SVG Illustrator vectorisé → layout reconnaissable (palette HoméOS, pas de lorem ipsum)
- [ ] SVG Figma → comportement inchangé (textes lus directement)
- [ ] ZIP HTML/CSS → HTML principal extrait et servi comme template
- [ ] ZIP React → message clair "format React détecté, M119 requis" (pas de crash)

---

### Mission 120 — Rebranchement Plugin Figma → FRD Editor

**STATUS: 🔵 BACKLOG**
**DATE: 2026-03-31**
**ACTOR: CLAUDE (backend) + GEMINI (frontend)**
**DÉPENDANCE: M38 (plugin Figma existant), M116 (pipeline set-current)**

**Contexte :** Le plugin Figma (M38) est le chemin le plus précis pour la conversion design → HTML. Il envoie la structure Figma native (frames nommés, textes, composants) directement à l'API locale. Il était branché sur l'ancien viewer (`/api/retro-genome/reality`). Il faut le rebrancher sur le nouveau pipeline FRD Editor.

**Localisation du plugin :** chercher dans le repo un dossier `figma-plugin/` ou `plugin/` contenant `manifest.json`, `code.js`, `ui.html`.

#### Livrable A — server_v3.py : nouvelle route Figma (Claude)

```
POST /api/figma/import
Body: { frames: [...], project_name: str }
→ Stocke les données Figma dans projects/{active}/imports/figma_{timestamp}.json
→ Déclenche generate-from-svg (adapté Figma) ou appelle directement HtmlGenerator
→ Retourne { import_id, status: "started", job_id }
```

#### Livrable B — Plugin Figma code.js : changer la cible (Claude)

Remplacer l'endpoint cible :
```javascript
// Avant (M38)
fetch('http://localhost:9998/api/retro-genome/reality', ...)
// Après (M120)
fetch('http://localhost:9998/api/figma/import', ...)
```

#### Livrable C — landing.html : afficher les imports Figma (Gemini)

Les imports Figma apparaissent dans la liste avec un badge `figma` distinct des SVG.

**Fichiers :**
- `Frontend/3. STENCILER/server_v3.py` — route `/api/figma/import`
- Plugin Figma `code.js` — changer URL cible
- `static/templates/landing.html` — badge figma (Gemini)

**Critères de sortie :**
- [ ] Plugin Figma → bouton "Envoyer à HoméOS" → import visible dans la landing
- [ ] Import Figma → "ouvrir dans frd editor" → template HTML généré et chargé
- [ ] Pas de régression sur les imports SVG existants

---

### Mission 122 — Pipeline import unifié : tous formats → FRD editor
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---

### Mission 119 — Pont React/ZIP → Tailwind Direct

**STATUS: 🔵 BACKLOG**
**DATE: 2026-03-31**
**ACTOR: CLAUDE (CODE DIRECT — backend uniquement)**
**DÉPENDANCE: M118 (pont SVG→Tailwind opérationnel, module `svg_to_tailwind.py` comme modèle)**

**Contexte :** Une codebase React/Next.js (`.zip`) contient une richesse sémantique exploitable : composants nommés, props typées, hiérarchie de pages. L'objectif est de convertir ce bundle en un template HTML + Tailwind vanilla exploitable dans le FRD Editor. Ce n'est pas une transpilation — c'est une **traduction d'intention** : on garde la hiérarchie et le design system, on efface le framework.

#### Livrable A — Nouveau module `react_to_tailwind.py` (Claude)

Fichier : `Backend/Prod/retro_genome/react_to_tailwind.py`

Algorithme :
```
1. Dé-zipper le bundle en mémoire (zipfile)
2. Identifier les fichiers de "surface" prioritaires :
   - App.tsx / App.jsx / page.tsx (Next.js)
   - Index entry points
   - Les composants référencés dans App (1 niveau)
3. Extraction & nettoyage JSX :
   - Retirer les imports React, hooks, useState, useEffect
   - Retirer les annotations TypeScript (:string, <T>, interface...)
   - Garder l'arbre JSX et les classes Tailwind existantes
4. Prompt LLM :
   "Convertis ce JSX nettoyé en HTML5 sémantique vanilla.
    Garde les classes Tailwind telles quelles.
    Transforme les composants en leur équivalent HTML.
    Résultat : document HTML complet autonome."
5. Sauvegarder dans static/templates/{safe_name}.html
```

Contraintes :
- Si le ZIP contient déjà des classes Tailwind → les conserver (pas de réécriture)
- Si le ZIP utilise CSS Modules / styled-components → extraire les styles en `<style>` inline
- Taille max par appel LLM : tronquer à 6000 tokens si nécessaire (prendre App + 2 composants max)

#### Livrable B — Nouvelle route dans `routes.py` (Claude)

```python
POST /api/retro-genome/generate-from-zip
Body: { "import_id": str }

→ Lit le ZIP depuis index.json + file_path (créé par /api/import/upload)
→ Appelle react_to_tailwind.convert()
→ Sauvegarde dans static/templates/{safe_name}.html
→ Retourne { "template_name": str, "status": "ok" }
```

#### Livrable C — Feedback (même pattern que M118)

Réutiliser le mécanisme de polling/job_id développé en M118. Pas de duplication — extraire en helper partagé si besoin.

#### Ce que GEMINI fera ensuite (M120)

Connecter `FrdIntent.generateTailwind()` pour détecter le type de l'import (`svg` vs `zip`/`jsx`) et appeler la bonne route. Unifier l'indicateur de chargement Sullivan.

**Fichiers à créer/modifier :**
- `Backend/Prod/retro_genome/react_to_tailwind.py` **[NEW]**
- `Backend/Prod/retro_genome/routes.py` — ajout route `generate-from-zip` **[MODIFY]**

**Note d'architecture :** Les deux modules M118 (`svg_to_tailwind.py`) et M119 (`react_to_tailwind.py`) partagent le même pattern :
```
Source brute → Extraction sémantique → LLM → static/templates/ → FRD Editor
```
À terme ils pourraient être unifiés dans un `converter_factory.py`.

**Critères de sortie :**
- [ ] `POST /api/retro-genome/generate-from-zip` avec `import_id` d'un ZIP React → retourne `{ template_name, status }`
- [ ] Le fichier `.html` généré est dans `static/templates/` et chargeable par `GET /api/frd/file?name=...`
- [ ] Les classes Tailwind du React source sont **préservées** (pas réécrites)
- [ ] Les imports React / TypeScript sont **absents** du HTML généré
- [ ] Fonctionne sur un ZIP Next.js standard (App Router ou Pages Router)

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
