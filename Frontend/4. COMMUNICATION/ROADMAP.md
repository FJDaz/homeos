# MISSION CONTROL : AETHERFLOW ROADMAP

> Missions complètes archivées dans [ROADMAP_ACHIEVED.md](./ROADMAP_ACHIEVED.md).
> Plan MVP détaillé : [PLAN_HOMEOS_MVP.md](../../docs/04_HomeOS/Plans/PLAN_HOMEOS_MVP.md)

---

## Session 2026-03-30 — Récapitulatif missions terminées

| Mission | Statut | Notes |
|---|---|---|
| M85–M92 | ✅ archivé | FastAPI foundation, FRD, BRS, retro-genome, archetypes |
| M97 | ✅ LIVRÉ | Wire UX v2 — table bijective + diagnostic géographique |
| M98 | ✅ LIVRÉ | Wire UX v3 — skeleton mode |
| M99 | ✅ LIVRÉ | Wire UX v4 — peel-out CSS + pop-in Monaco + route wire-source |
| M101-bis | ✅ LIVRÉ | Bridge Plugin — conformité design HoméOS (CODE DIRECT Claude) |
| M100 | ✅ LIVRÉ | Landing Import — hub Figma SVG + rafraîchir/vider |
| M100-bis | ✅ LIVRÉ | Hub universel — drop multi-format + manifest check + sélection écrans |
| M102 | ✅ LIVRÉ | Intent Viewer — auto-load + endpoint import-analysis + liens frd-editor |
| M106 | ✅ LIVRÉ | CI/CD HF Spaces — Dockerfile, start_hf.sh, deploy-hf.yml |
| M107 | ✅ LIVRÉ | Navigation globale — header pipeline injecté + tabs auto-actifs |
| M103 | ✅ LIVRÉ | Wire v5 — auto-launch + overlay bijectif bilan/plan |
| M104 | ✅ LIVRÉ | Stitch Integration — backend.md + intent_map + Monaco drawer |
| M105 | ✅ LIVRÉ | Aperçu local — rendu 1:1 dans un onglet indépendant |
| M109A | ✅ LIVRÉ | Font Classifier Ph-A — Vox-ATypI via Panose & Metadata |
| M109B | ✅ LIVRÉ | Font Classifier Ph-B — Analyse Bézier (Stress/Contraste) |
| M104/M108 | ✅ LIVRÉ | Stitch Integration — backend.md + intent_map + Monaco drawer |
| M109A | ✅ LIVRÉ | Font Classifier Ph-A — Vox-ATypI via Panose & Metadata |
| M109B | ✅ LIVRÉ | Font WebGen Ph-B — Subset Latin + WOFF2 + @font-face CSS |

---

## CR Mission 107 — Navigation globale cohérente

**STATUT: ✅ LIVRÉ**
**DATE: 2026-03-30**
**ACTEURS: GEMINI (bootstrap.js + CSS) + CLAUDE (vérification)**

### Livrables

**Frontend (`bootstrap.js`)**
- Fonction `injectGlobalNav()` — injecte header global au DOMContentLoaded
- 4 tabs pipeline : [ import ↓ ] [ analyser ◐ ] [ éditer ✎ ] [ déployer ↑ ]
- Tab actif détecté automatiquement via `window.location.pathname`
- Theme toggle (☀️/🌙) avec persistance localStorage
- Bridge status indicator (dot vert "bridge actif")
- Exposition API : `window.HOMEOS.boot()`, `window.HOMEOS.refreshNav()`

**CSS (`stenciler.css`)**
- `.global-pipeline-header` — header fixe 48px, z-index 1000
- `.pipeline-tab` — styles hover/active/disabled
- `.bridge-status` — indicateur de statut avec dot online/offline
- `.theme-toggle-btn` — bouton thème minimaliste
- Couleurs HoméOS : #7aca6a (vert), Geist 12px, fond #f7f6f2

**Templates mis à jour**
- `landing.html` — header/sidebar supprimés, navigation globale injectée
- `intent_viewer.html` — header/sidebar supprimés, navigation globale injectée
- `frd_editor.html` — navigation Brainstorm/Backend/Frontend supprimée, bootstrap.js ajouté

### Architecture
```
bootstrap.js (injecté sur toutes les pages)
    └─ injectGlobalNav() → header fixe 48px
        ├─ pipeline-brand (homéos v3.1.2)
        ├─ pipeline-tabs (4 tabs pipeline)
        └─ pipeline-actions (bridge status + theme toggle)
```

### Tests effectués
- ✅ `/landing` — bootstrap.js chargé, header injecté
- ✅ `/intent-viewer` — bootstrap.js chargé, header injecté
- ✅ `/frd-editor` — bootstrap.js chargé, navigation supprimée
- ✅ Tab actif détecté automatiquement selon pathname
- ✅ Theme toggle fonctionnel avec persistance

---

## CR Mission 109 Phase B — Web Font Generator

**STATUT: ✅ LIVRÉ**
**DATE: 2026-03-30**
**ACTEUR: CLAUDE (CODE DIRECT)**

### Livrables

**Backend (`font_webgen.py`)**
- Classe `FontWebGen` — génération webfonts depuis TTF/OTF/WOFF/WOFF2
- Subset Latin : U+0020-00FF, U+0100-017E, U+2013-2014, U+2018-2019, U+201C-201D, U+00AB-00BB
- Export WOFF2 (Brotli) — économie 60-80% du poids original
- Génération @font-face CSS standard
- Détection variable font → `format('woff2-variations')` + `font-weight: 100 900`
- Alerte licensing pour fontes commerciales connues

**Routes (`server_v3.py`)**
- `POST /api/sullivan/font-upload` → classification + webfont + CSS
- `GET /api/sullivan/fonts` → liste des fontes dans /static/fonts/
- `DELETE /api/sullivan/fonts/{slug}` → supprime fonte et répertoire

**Storage**
- `/static/fonts/{slug}/{slug}-{weight}{style}.woff2`
- `/exports/fonts/` — uploads temporaires

### Tests effectués
- ✅ Upload SourceCodePro-Semibold.ttf → classification "lineales/grotesque"
- ✅ Subset Latin + export WOFF2 (1220 bytes)
- ✅ @font-face CSS généré correctement
- ✅ Font chargeable depuis `/static/fonts/...`

### Architecture
```
Upload TTF/OTF
    ↓
FontClassifier → {vox_atypi, signals, weights}
    ↓
FontWebGen → subset → WOFF2 → CSS @font-face
    ↓
/static/fonts/{slug}/
```

### Dépendances ajoutées
```
fonttools>=4.43.0
brotli>=1.0.9
```

---

## CR Mission 100-bis — Landing : hub universel d'import

**STATUT: ✅ LIVRÉ**
**DATE: 2026-03-30**
**ACTEURS: GEMINI (landing.html) + CLAUDE (server_v3.py)**

### Livrables

**Frontend (`landing.html`)**
- Zone de drop multi-format : `.svg`, `.zip`, `.tsx`, `.html`, `.css`, `.js`
- Drag-and-drop avec feedback visuel (survol vert HoméOS)
- Formulaire de création de manifest.json (nom, auteur, description)
- Affichage dynamique des imports avec checkboxes de sélection
- Bouton "continuer vers frd editor" avec compteur de sélection
- Empty state et upload progress indicator
- Respect des tokens Stenciler (Geist 12px, #f7f6f2, #7aca6a)

**Backend (`server_v3.py`)**
- `POST /api/import/upload` — Upload générique multi-format
- `GET /api/manifest/check` — Vérification existence manifest
- `GET /api/manifest/get` — Récupération contenu manifest
- `POST /api/manifest/create` — Création manifest avec métadonnées projet
- Tracking des imports dans `exports/retro_genome/index.json`
- Notification counter incrémenté pour le polling

### Tests effectués
- ✅ Endpoint `/api/manifest/check` → retourne `{"exists": false}` si absent
- ✅ Endpoint `/api/manifest/create` → crée manifest.json à la racine
- ✅ Endpoint `/api/import/upload` → sauvegarde fichier + met à jour index.json
- ✅ Landing page `/landing` → affichage correct, drop zone fonctionnelle

### Architecture
```
manifest.json (racine) ← créé si absent
    └─ name, author, description, created_at, version, elements[], intents[]

exports/retro_genome/
    └─ index.json ← tous les imports (SVG + multi-format)
    └─ IMPORT_*.{zip,tsx,html,...} ← fichiers uploadés
```

---

## CR Mission 103 — Wire mode v5 : auto-launch + overlay bijection

**STATUT: ✅ LIVRÉ**
**DATE: 2026-03-30**
**ACTEURS: GEMINI (frontend) + CLAUDE (backend)**

### Livrables

**Backend (`wire_analyzer.py`)**
- Refactorisation de `analyze_template` pour retourner un objet structuré.
- Nouveaux champs : `intentions[]`, `statuts[]`, `plan[]` pour affichage point par point.

**Frontend (`FrdWire.feature.js`, `FrdChat.feature.js`)**
- Auto-trigger : `setMode('wire')` lance immédiatement l'analyse.
- Overlay V5 : Passage d'un tableau plat à un tableau de bord biface (Bilan ↔ Plan).
- Bouton global "IMPLÉMENTER LE PLAN" : ferme l'overlay, repasse en mode Construct et injecte le plan dans le chat.

**UI (`frd_editor.html`)**
- Suppression du bouton "Analyser" (devenu obsolète).
- Redimensionnement de l'overlay (!max-w-[1000px]) pour le dual-column.

---

## CR Mission 104 — Stitch Integration : design.md & backend.md

**STATUT: ✅ LIVRÉ**
**DATE: 2026-03-30**
**ACTEURS: CLAUDE (backend routes) + GEMINI (landing UI)**

### Livrables

**Backend (`server_v3.py`, `wire_analyzer.py`)**
- `backend.md` — Création du fichier "Source of Truth" technique à la racine.
- `POST /api/manifest/import-stitch` — Parseur Markdown pour `design.md` hérité de Stitch.
- `GET/PUT /api/manifest/backend` — Gestion du cycle de vie du manifest technique.
- `WireAnalyzer` — Priorisation du mapping `backend.md` sur le mapping statique pour la bijection.

**Frontend (`landing.html`)**
- **Badge Stitch** : Détection automatique de `design.md` et affichage du badge "Stitch Compatible".
- **Bouton Sync** : Lancement de l'import `design.md` → `backend.md` en un clic.
- **Monaco Drawer** : Remplacement de l'alert manifest par un tiroir latéral avec **Monaco Editor** pour éditer le `backend.md`.

### Architecture
```
design.md (In)  ──>  [Import Logic]  ──>  backend.md (Sync)
                                              │
                                              └─> [Wire Mode] (Priority Map)
```

---

## CR Mission 105 — Aperçu local (Real Tab Preview)

**STATUT: ✅ LIVRÉ**
**DATE: 2026-03-30**
**ACTEURS: CLAUDE (backend) + GEMINI (UI)**

### Livrables

**Backend (`server_v3.py`)**
- `POST /api/preview/run` : Sauvegarde l'état actuel de l'éditeur dans un fichier temporaire (`_preview_tmp.html`).
- `GET /api/preview/show` : Sert le fichier temporaire avec `Cache-Control: no-store` pour garantir la fraîcheur du rendu.

**Frontend (`frd_editor.html`, `FrdEditor.feature.js`)**
- **Bouton "Aperçu ↗"** : Ajouté à la barre d'outils du FRD Editor.
- **Logique de Preview** : Synchronisation entre Monaco et l'onglet distant via `runPreviewTab()`.

### Tests effectués
- ✅ Modification du code dans Monaco -> Clic "Aperçu ↗" -> Nouvel onglet avec les changements exacts.
- ✅ Vérification de l'indépendance (pas d'iframe parent, JS/CSS natif).

---

## Mission 109 — Sullivan Typography Engine

**STATUS: 🔵 BACKLOG**
**DÉPENDANCE: M104/M108 ✅**
**DÉCOUPAGE: 3 phases séquentielles — A ✅ → B ✅ → C (Claude backend + Gemini UI)**

### Vision

Sullivan ne prescrit pas des fontes comme un moteur de templates. Il les **connaît** — leur histoire, leur anatomie, leur contexte culturel. Quand un designer uploade un `.otf` inconnu, Sullivan le positionne dans la classification Vox-ATypI en lisant ses signaux morphologiques (axe de stress, contraste, nature des empattements), puis enrichit la réponse depuis une base de connaissance éditoriale. Il génère ensuite le `@font-face` optimisé web et stocke la fonte dans les assets du projet.

Aucun outil LLM-to-design ne fait ça. Stitch assume Google Fonts. Figma assume le CDN. HoméOS assume la liberté typographique du designer.

---

### Phase A — Classification Vox-ATypI par signaux machine

**ACTOR: CLAUDE (CODE DIRECT)**
**FICHIER: `Backend/Prod/sullivan/font_classifier.py`**

Chaque fonte TrueType/OpenType embarque des tables binaires lisibles sans rendu. La table **panose** (10 octets) encode les signaux morphologiques de la classification Vox-ATypI. Complétée par l'analyse de contours Bézier sur le glyphe `o` (axe de stress, ratio contraste), Sullivan classifie sans IA, sans ambiguïté.

```
pip install fonttools brotli
```

#### Mapping panose[1] (style empattement) → Vox-ATypI

| Valeur | Style | Vox-ATypI |
|---|---|---|
| 2 | Cove (congé arrondi) | Humanes |
| 3 | Obtuse Cove | Garaldes |
| 4–5 | Square Cove | Réales (Transitional) |
| 6 | Square | Mécanes (Slab) |
| 7 | Thin / Hairline | Didones |
| 11–13 | Sans | Linéales |
| 14 | Flared | Incises |

panose[4] (contraste) affine :
- 8–9 = contraste élevé → confirme Didone
- 2–4 = contraste faible + sans → sous-catégorie Grotesque/Géo/Humaniste via analyse `a` et `g`

Calcul axe de stress via contours Bézier sur le glyphe `o` :
```python
def _compute_stress_angle(font: TTFont) -> float:
    """Angle d'inclinaison de l'axe des minima d'épaisseur.
    ~0° = vertical (Didone), ~10-15° = oblique (Garalde/Humane)"""
```

Détection variable font :
```python
is_variable = 'fvar' in font
# Si True → weight_range = (axes[0].minValue, axes[0].maxValue)
```

Schéma retourné par `classify_font()` :
```json
{
  "family_name": "Cormorant",
  "vox_atypi": "Garaldes",
  "vox_atypi_sub": "Aldine",
  "confidence": 0.87,
  "signals": {
    "stress_angle_deg": 12.4,
    "contrast_ratio": 3.1,
    "serif_style": "cove",
    "panose_raw": [2, 3, 6, 3, 5, 4, 4, 2, 2, 4]
  },
  "is_variable": false,
  "weights_available": [300, 400, 500, 600, 700],
  "styles": ["Regular", "Italic"]
}
```

---

### Phase B — Web Font Generator (@font-face + WOFF2)

**ACTOR: CLAUDE (CODE DIRECT)**
**FICHIER: `Backend/Prod/sullivan/font_webgen.py`**

```
Upload TTF/OTF/WOFF/WOFF2
    ↓ fonttools: normalisation
    ↓ Subsetting: Latin Extended (U+0020–U+024F) + ponctuation typo
    ↓   (économie 60–80% du poids)
    ↓ Export WOFF2 (Brotli) + WOFF fallback
    ↓ Storage: /static/fonts/{slug}/{slug}-{weight}{style}.woff2
    ↓ Génération @font-face CSS
```

Subset cible (latin professionnel) :
```
U+0020-007E, U+00A0-00FF, U+0100-017E
U+2018, U+2019, U+201C, U+201D  (guillemets typographiques)
U+2013, U+2014  (tirets)
U+00AB, U+00BB  (guillemets français)
```

CSS standard :
```css
@font-face {
  font-family: 'Cormorant';
  src: url('/static/fonts/cormorant/cormorant-400.woff2') format('woff2'),
       url('/static/fonts/cormorant/cormorant-400.woff') format('woff');
  font-weight: 400;
  font-style: normal;
  font-display: swap;
  unicode-range: U+0020-00FF, U+0100-017E, U+2013-2014, U+2018-2019, U+201C-201D;
}
```

CSS variable font :
```css
@font-face {
  font-family: 'Söhne';
  src: url('/static/fonts/sohne/sohne-variable.woff2') format('woff2-variations');
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
}
```

Alerte licensing (heuristique) :
```python
COMMERCIAL_FONTS = {
    "söhne", "graphik", "canela", "financier", "tiempos",
    "gt walsheim", "neue haas grotesk", "acumin", "freight"
}
# Si match → warning dans la réponse JSON
```

---

### Phase C — Routes + Sullivan Advisor + UI

**ACTOR: CLAUDE (routes + advisor) + GEMINI (UI landing.html)**

Routes `server_v3.py` :
```
POST /api/sullivan/font-upload   → multipart TTF/OTF/WOFF/WOFF2
                                  → classifier + webgen + advisor
                                  → { classification, webfont, sullivan_commentary }

GET  /api/sullivan/fonts         → liste fontes dans /static/fonts/
DELETE /api/sullivan/fonts/{slug} → supprime /static/fonts/{slug}/
```

`sullivan_font_advisor.py` combine classification machine + `typography_db.json` :

> *"Axe oblique à 12°, contraste modéré (ratio 3.1), empattements à congé. Garalde — famille aldine. Proche de Sabon par la modération du contraste. Pour accompagner : privilégie un Grotesque humaniste (Gill Sans, Aktiv) plutôt qu'un Géométrique — l'un dialogue, l'autre concurrence."*

#### `typography_db.json`

**AUTEUR : FJD (sélection éditoriale des 7 références par catégorie) + CLAUDE (structure + complétion technique)**
**CHEMIN : `Backend/Prod/sullivan/typography_db.json`**

8 catégories Vox-ATypI, chacune avec :
- `signals` — critères morphologiques machine (axe, contraste, empattements)
- `references[]` — 7 fontes (nom, année, designer, google_fonts_id, note courte)
- `pairings[]` — avec rationale typographique
- `usages[]` / `anti_usages[]`
- `cultural_refs[]` — Étapes, Eye, Émigré, monographies de référence

Catégories à documenter :
`garaldes` · `didones` · `reales` · `lineales_grotesque` · `lineales_geometrique` · `lineales_humaniste` · `mecanes` · `incises`

**Workflow de construction :** Claude génère le squelette JSON complet avec ses propres références → FJD amende/remplace les 7 références par catégorie selon ses choix éditoriaux → version finale commitée.

#### UI landing.html (Gemini)

Section `#font-manager` — indépendante de la zone d'import SVG :
- Drop zone `.ttf/.otf/.woff/.woff2`
- Carte résultat par fonte : nom + badge Vox-ATypI + preview live (Aa Bb 0123 rendu avec la fonte) + poids disponibles + warning licensing + commentaire Sullivan + snippet `@font-face` Monaco read-only
- Badge "variable font" si détecté
- Bouton "ajouter à stenciler.css" → logge dans `backend.md`

**Bootstrap Gemini :**
```
Lire static/templates/landing.html — structure sections existantes (ne pas toucher).
Lire static/css/stenciler.css — tokens V1.
Lire Frontend/1. CONSTITUTION/LEXICON_DESIGN.json.
Ajouter UNIQUEMENT la section #font-manager après #import-section.
Pas d'uppercase. Pas d'emojis. Geist 12px. #8cc63f pour accents.
```

---

### Fichiers à créer

| Fichier | Auteur | Rôle |
|---|---|---|
| `Backend/Prod/sullivan/font_classifier.py` | CLAUDE | Panose + contours → Vox-ATypI |
| `Backend/Prod/sullivan/font_webgen.py` | CLAUDE | Subset + WOFF2 + @font-face |
| `Backend/Prod/sullivan/sullivan_font_advisor.py` | CLAUDE | Classifier + DB → commentaire Sullivan |
| `Backend/Prod/sullivan/typography_db.json` | FJD + CLAUDE | 8 catégories × 7 références |
| `server_v3.py` + 3 routes | CLAUDE | font-upload, fonts list, delete |
| `static/templates/landing.html` | GEMINI | Section #font-manager |

Dépendances à ajouter : `fonttools>=4.43.0`, `brotli>=1.0.9`

### Critères de sortie

- [ ] Upload `.otf` Garalde → classification "Garaldes", ratio contraste ~3, axe ~12°
- [ ] Upload fonte variable → `is_variable: true`, `font-weight: 100 900` dans CSS
- [ ] `@font-face` généré → chargeable browser depuis `/static/fonts/`
- [ ] Preview landing → fonte rendue live dans la carte
- [ ] Commentaire Sullivan → catégorie + proche référence + suggestion pairing
- [ ] Warning licensing sur fonte connue commerciale
- [ ] `GET /api/sullivan/fonts` → liste les fontes du projet

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
