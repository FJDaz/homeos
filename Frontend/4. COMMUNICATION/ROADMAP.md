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
