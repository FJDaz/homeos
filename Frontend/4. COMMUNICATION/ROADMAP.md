# ROADMAP AetherFlow — Phase Active

> Missions complètes archivées dans [ROADMAP_ACHIEVED.md](./ROADMAP_ACHIEVED.md).

---

## Phase 21 — Genome Design Bridge (Figma / Illustrator)

**Vision :** Genome AetherFlow → SVG balisé → Figma/Illustrator → Styles → HTML stylisé

**Pipeline :**
```
genome_reference.json
  → [enrich]  genome_enricher.py   → genome_enriched.json
  → [render]  genome_to_svg_v2.py  → exports/genome_zones_*.svg
  → [figma]   figma-plugin/        → styles.json
```

**CLI :**
```bash
./sullivan enrich          # Pass 1+2+3 : classification, ux_step, col_span
./sullivan zones           # Render SVG (utilise genome_enriched.json si présent)
./sullivan fancy-zones     # Render SVG + KIMI style
```

**Livré :**
- ✅ 21A — genome_to_svg.py + GET /api/export/svg
- ✅ 21B — genome_enricher.py (Pass 1 : ui_role, dominant_zone, display_label)
- ✅ sullivan CLI (build / enrich / zones / fancy / fancy-zones)
- ✅ genome_to_svg_v2.py (zone renderer + display_label + [ui_role])

---

**STATUS: COMPLETED**

### Contexte

Pass 1 livré (21B) : chaque N1 a `ui_role`, `dominant_zone`, `display_label`.
Problème : le renderer SVG ignore ces métadonnées — tous les organes ont le même rendu générique (rectangles gris empilés).

Cette mission implémente les 3 passes restantes + les renderers archétypes visuellement reconnaissables.

### Fichiers à lire AVANT de coder (OBLIGATOIRE)

1. `Backend/Prod/enrichers/genome_enricher.py` — `enrich_genome()` L.73-122. Comprendre les champs existants (`ui_role`, `dominant_zone`, `display_label`). Les Passes 2+3 s'ajoutent à cette fonction.
2. `Backend/Prod/exporters/genome_to_svg_v2.py` — `_render_n1()` L.468-491 et `_render_n0()` L.494-529. C'est là qu'on branche les archetype renderers.
3. `Frontend/2. GENOME/genome_enriched.json` — lire les `ui_role` réels présents pour calibrer les renderers.

### Fichiers à créer / modifier

---

#### MODIFIER : `Backend/Prod/enrichers/genome_enricher.py`

Ajouter après `enrich_genome()`, deux nouvelles fonctions, et les appeler dans `main()` :

```python
UX_SEQUENCE = {
    'nav-header': 1, 'left-sidebar': 2, 'main-canvas': 3,
    'main-content': 4, 'dashboard': 5, 'form-panel': 6,
    'upload-zone': 7, 'chat-overlay': 8, 'onboarding-flow': 9,
    'overlay': 10, 'settings-panel': 11, 'status-bar': 12,
    'export-action': 13, 'unknown': 99,
}

def enrich_pass2_ux(genome):
    """Ajoute ux_step à chaque N1. Trie les organes dans chaque phase par ux_step."""
    for phase in genome.get('n0_phases', []):
        organs = phase.get('n1_sections', [])
        for organ in organs:
            organ['ux_step'] = UX_SEQUENCE.get(organ.get('ui_role', 'unknown'), 99)
            print(f"  [PASS2] {organ.get('id')} → ux_step={organ['ux_step']}")
        organs.sort(key=lambda o: o.get('ux_step', 99))
    return genome

def enrich_pass3_density(genome):
    """Ajoute layout_type et col_span selon le nb de composants N3."""
    for phase in genome.get('n0_phases', []):
        for organ in phase.get('n1_sections', []):
            n3_count = sum(
                len(f.get('n3_components', []))
                for f in organ.get('n2_features', [])
            )
            if n3_count < 3:
                organ['layout_type'] = 'compact'
                organ['col_span'] = 1
            elif n3_count <= 6:
                organ['layout_type'] = 'standard'
                organ['col_span'] = 1
            else:
                organ['layout_type'] = 'wide'
                organ['col_span'] = 2
            print(f"  [PASS3] {organ.get('id')} → {organ['layout_type']} (N3={n3_count})")
    return genome
```

Dans `main()`, remplacer `enriched = enrich_genome(genome)` par :
```python
enriched = enrich_genome(genome)
enriched = enrich_pass2_ux(enriched)
enriched = enrich_pass3_density(enriched)
```

---

#### CRÉER : `Backend/Prod/exporters/archetype_renderers.py`

Palette commune (copier en haut du fichier) :
```python
C_BG      = '#f7f6f2'
C_SURFACE = '#ffffff'
C_BORDER  = '#d5d4d0'
C_TEXT    = '#3d3d3c'
C_SUB     = '#9d9c98'
C_HINT    = '#b5b4b0'
C_ACCENT  = '#a8c5fc'
C_HEADER  = '#e8e7e3'
C_SIDEBAR = '#f0efeb'
C_ACTIVE  = '#3d3d3c'
FONT      = '-apple-system,Helvetica,Arial,sans-serif'
```

Helpers partagés :
```python
def _r(x, y, w, h, fill, stroke=C_BORDER, rx=4, sw=1, dash=''):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" rx="{rx}"{d}/>')

def _t(x, y, txt, size=9, fill=C_TEXT, anchor='start', weight='normal', clip=0):
    s = str(txt)[:clip] if clip else str(txt)
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}" '
            f'font-family="{FONT}">{s}</text>')

def _c(cx, cy, r, fill=C_BORDER, stroke='none', sw=1):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'

def _line(x1, y1, x2, y2, stroke=C_BORDER, sw=1, dash=''):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"{d}/>'
```

**Spécifications visuelles — une fonction par archétype :**

**`draw_nav_header(organ, x, y, w, components)` → `(svg, 56)`**
```
[A] [Home] [Explore] [Studio] [Export]          [🔍]
```
- Fond : `_r(x, y, w, 56, C_HEADER, C_BORDER, rx=8)`
- Logo : `_r(x+12, y+12, 32, 32, C_ACTIVE, rx=4)` + `_t(x+20, y+33, "A", 14, "#ffffff", weight="700")`
- Pills nav (boucle sur components[:5], px = x+56+i*76) :
  - `_r(px, y+16, 68, 24, C_ACTIVE if i==0 else C_SURFACE, C_BORDER, rx=12)`
  - `_t(px+34, y+32, comp['name'][:8], 9, "#ffffff" if i==0 else C_TEXT, "middle")`
- Search : `_c(x+w-28, y+28, 11, "none", C_SUB, 1.5)` + `_line(x+w-20, y+36, x+w-16, y+40, C_SUB, 1.5)`

**`draw_left_sidebar(organ, x, y, w, components)` → `(svg, h)`**
h = 48 + len(components)*40 + 16 ; w_draw = 88 (fixe)
```
MENU
[■] Home     ← fond accent
[■] Projects
[■] Settings
```
- Fond : `_r(x, y, 88, h, C_SIDEBAR, C_BORDER, rx=8)`
- Header : `_t(x+10, y+22, "MENU", 7, C_SUB, weight="600")`
- Rows ry = y+36+i*40 :
  - Active (i==0) : `_r(x+4, ry+2, 80, 32, C_ACCENT, C_ACCENT, rx=4)`
  - Icône : `_r(x+10, ry+8, 16, 16, C_ACTIVE if i==0 else C_BORDER, rx=3)`
  - Label : `_t(x+34, ry+20, comp['name'][:14], 9, C_ACTIVE if i==0 else C_TEXT)`

**`draw_main_canvas(organ, x, y, w, components)` → `(svg, h)`**
h = max(240, 48 + len(components)*32 + 24)
- Fond : `_r(x, y, w, h, C_SURFACE, C_BORDER, rx=8)`
- Grille : lignes horizontales step 24 : `_line(x+1, gy, x+w-1, gy, "#f0efeb")`
- Label : `_t(x+12, y+20, "CANVAS / EDITOR", 7, C_HINT, weight="600")`
- Zone éditeur : `_r(x+16, y+32, w-32, h-48, C_BG, C_SUB, rx=4, dash="4 4")`
- Texte centré : `_t(x+w//2, y+h//2, "[ workspace ]", 9, C_HINT, "middle")`

**`draw_form_panel(organ, x, y, w, components)` → `(svg, h)`**
h = 44 + len(components)*52 + 48
- Fond : `_r(x, y, w, h, C_SURFACE, C_BORDER, rx=8)`
- Header : `_t(x+12, y+22, "FORMULAIRE", 7, C_HINT, weight="600")`
- Fields fy = y+38+i*52 :
  - Label : `_t(x+16, fy+12, comp['name'][:22], 8, C_SUB)`
  - Input : `_r(x+16, fy+16, w-32, 28, C_BG, C_BORDER, rx=4)`
  - Curseur : `_line(x+24, fy+22, x+24, fy+38, C_ACCENT, 1.5)`
  - Hint text : `_t(x+30, fy+34, comp.get('visual_hint','')[:18], 8, C_HINT)`
- Submit : `_r(x+16, y+h-40, w-32, 28, C_ACTIVE, rx=6)` + `_t(x+w//2, y+h-20, "Submit", 10, "#ffffff", "middle", "600")`

**`draw_dashboard(organ, x, y, w, components)` → `(svg, 236)`**
- Fond : `_r(x, y, w, 236, C_BG, C_BORDER, rx=8)`
- Header : `_t(x+12, y+22, "DASHBOARD", 7, C_HINT, weight="600")`
- 3 metric cards (cw=(w-32-16)//3, cx_i=x+12+i*(cw+8), cy=y+36) :
  - `_r(cx_i, y+36, cw, 64, C_SURFACE, C_BORDER, rx=6)`
  - Valeur : `_t(cx_i+cw//2, y+72, ["42","87%","↑12"][i], 18, C_TEXT, "middle", "700")`
  - Label : `_t(cx_i+cw//2, y+90, comp['name'][:10], 7, C_SUB, "middle")`
- Chart zone zy=y+112 : `_r(x+12, zy, w-24, 72, C_SURFACE, C_BORDER, rx=4, dash="4 4")`
- 6 barres (bw=18, hauteurs=[28,44,36,52,40,56]) : `_r(bx, zy+72-bh, bw, bh, C_ACCENT)`
- Label : `_t(x+w-30, zy+68, "GRAPH", 7, C_HINT)`

**`draw_chat_overlay(organ, x, y, w, components)` → `(svg, h)`**
h = 52 + len(components)*44 + 44
- Fond+border accent : `_r(x, y, w, h, C_SURFACE, C_ACCENT, rx=8, sw=2)`
- Header bar : `_r(x, y, w, 38, C_HEADER, C_BORDER, rx=8)` + `_t(x+12, y+24, "ASSISTANT", 8, C_TEXT, weight="600")`
- Bulles by=y+50+i*44 :
  - Pair : droite `_r(x+w-136, by, 120, 30, C_ACCENT, rx=12)` + texte milieu
  - Impair : gauche `_r(x+12, by, 120, 30, C_HEADER, C_BORDER, rx=12)` + texte milieu
- Input : `_r(x+12, y+h-36, w-52, 28, C_BG, C_BORDER, rx=14)` + `_c(x+w-20, y+h-22, 12, C_ACCENT)`

**`draw_upload_zone(organ, x, y, w, components)` → `(svg, 160)`**
- Fond : `_r(x, y, w, 160, C_SURFACE, C_BORDER, rx=8)`
- Zone pointillée : `_r(x+20, y+16, w-40, 128, C_BG, C_SUB, rx=6, dash="6 4")`
- Icône : `_c(x+w//2, y+68, 22, C_HEADER, C_BORDER, 1.5)` + `_t(x+w//2, y+58, "↑", 14, C_SUB, "middle")`
- Texte : `_t(x+w//2, y+100, "Drag & drop", 11, C_TEXT, "middle", "500")` + `_t(x+w//2, y+116, "or click to browse", 8, C_HINT, "middle")`

**`draw_overlay(organ, x, y, w, components)` → `(svg, 224)`**
- Backdrop (fill-opacity inline) : `<rect x="{x}" y="{y}" width="{w}" height="224" fill="#3d3d3c" fill-opacity="0.12" rx="8"/>`
- Ombre : `<rect x="{x+28}" y="{y+28}" width="{w-48}" height="172" fill="#000000" fill-opacity="0.06" rx="8"/>`
- Card : `_r(x+24, y+24, w-48, 172, C_SURFACE, C_BORDER, rx=8)`
- Title bar : `_r(x+24, y+24, w-48, 36, C_HEADER, "none", rx=8)`
- Titre : `_t(x+40, y+48, organ.get('name','Modal')[:22], 11, C_TEXT, weight="600")`
- Close : `_c(x+w-36, y+42, 9, C_BORDER)` + `_t(x+w-36, y+46, "×", 10, C_TEXT, "middle")`
- Corps (2 lignes) : `_r(x+36, y+72, w-80, 8, C_BORDER, rx=2)` + `_r(x+36, y+88, (w-80)*2//3, 8, C_BORDER, rx=2)`
- Boutons : annuler (stroke) + valider (C_ACTIVE fond blanc)

**`draw_settings_panel(organ, x, y, w, components)` → `(svg, h)`**
h = 44 + len(components)*44 + 12
- Fond : `_r(x, y, w, h, C_SURFACE, C_BORDER, rx=8)`
- Header : `_t(x+12, y+22, "PARAMÈTRES", 7, C_HINT, weight="600")`
- Rows ry=y+36+i*44 :
  - Séparateur : `_line(x+12, ry, x+w-12, ry, C_HEADER)`
  - Label : `_t(x+16, ry+20, comp['name'][:24], 10, C_TEXT)`
  - Toggle fond : `_r(x+w-52, ry+6, 36, 20, C_ACCENT if i==0 else C_BORDER, rx=10)`
  - Bille : `_c(x+w-20 if i==0 else x+w-38, ry+16, 8, C_SURFACE)`

**`draw_status_bar(organ, x, y, w, components)` → `(svg, 44)`**
- Fond : `_r(x, y, w, 44, C_HEADER, C_BORDER, rx=8)`
- Dots statut (colors=['#4ade80','#facc15','#94a3b8'], boucle min(3,len)) :
  - `_c(x+16+i*80, y+22, 5, colors[i])` + `_t(x+26+i*80, y+26, comp['name'][:8], 8, C_SUB)`
- Boutons : `_r(x+w-136, y+10, 60, 24, C_SURFACE, C_BORDER, rx=4)` + `_r(x+w-68, y+10, 60, 24, C_SURFACE, C_BORDER, rx=4)`

**`draw_content_module(organ, x, y, w, components)` → `(svg, h)` (fallback)**
h = 44 + len(components)*36 + 12
- Fond : `_r(x, y, w, h, C_SURFACE, C_BORDER, rx=8)`
- Header : `_t(x+12, y+22, organ.get('display_label', organ.get('name','Module'))[:28], 9, C_TEXT, weight="600")`
- Rows ry=y+36+i*36 : `_r(x+12, ry+4, w-24, 24, C_BG, C_BORDER, rx=4)` + `_t(x+20, ry+20, comp['name'][:24], 8, C_TEXT)`

**Dispatcher :**
```python
ROLE_RENDERERS = {
    'nav-header': draw_nav_header,
    'left-sidebar': draw_left_sidebar,
    'main-canvas': draw_main_canvas,
    'main-content': draw_main_canvas,
    'form-panel': draw_form_panel,
    'dashboard': draw_dashboard,
    'chat-overlay': draw_chat_overlay,
    'upload-zone': draw_upload_zone,
    'overlay': draw_overlay,
    'settings-panel': draw_settings_panel,
    'status-bar': draw_status_bar,
    'onboarding-flow': draw_form_panel,
    'export-action': draw_upload_zone,
}

def render_organ(organ, x, y, w):
    role = organ.get('ui_role', 'unknown')
    components = [c for f in organ.get('n2_features', []) for c in f.get('n3_components', [])]
    renderer = ROLE_RENDERERS.get(role, draw_content_module)
    svg_body, organ_h = renderer(organ, x, y, w, components)
    gid  = organ.get('id', '')
    name = organ.get('display_label', organ.get('name', gid))
    role_str = role if role and role != 'unknown' else ''
    header = (
        f'<g id="{gid}" class="af-organ" data-genome-id="{gid}" '
        f'data-name="{name}" data-ui-role="{role_str}" data-ux-step="{organ.get("ux_step","")}">'
    )
    return f'{header}\n{svg_body}\n</g>', organ_h
```

---

#### MODIFIER : `Backend/Prod/exporters/genome_to_svg_v2.py`

**Import à ajouter après les imports existants :**
```python
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from archetype_renderers import render_organ
```

**Remplacer `_render_n1()` entier :**
```python
def _render_n1(organ, x, y, use_kimi=False, style_id='auto'):
    col_span = organ.get('col_span', 1)
    w = COL_W * col_span + COL_GAP * (col_span - 1)

    if use_kimi:
        result = _kimi_organ_svg(organ, style_id=style_id)
        if result:
            svg_inner, kimi_h = result
            gid  = _esc(organ.get('id', ''))
            name = _esc(organ.get('display_label', organ.get('name', gid)))
            lines = [
                f'<g id="{gid}" class="af-organ" data-genome-id="{gid}" data-name="{name}">',
                _rect(x, y, w, kimi_h, COL_ORGAN_BG, COL_ORGAN_STR, rx=10),
                _text(x+12, y+18, name, size=11, fill=COL_TEXT_MAIN, weight='600'),
                f'<g transform="translate({x},{y+30})">',
                svg_inner,
                '</g></g>',
            ]
            return '\n'.join(lines), kimi_h
        print(f'  [KIMI] {organ.get("id")} → fallback archetype')

    return render_organ(organ, x, y, w)
```

**Remplacer la boucle `for i, organ in enumerate(organs)` dans `_render_n0()` :**
```python
col_cursor = 0
row = 0
row_y = [offset_y + START_Y]

for organ in organs:
    col_span = organ.get('col_span', 1)
    col = col_cursor % N_COLS

    if col + col_span > N_COLS:
        row += 1
        col_cursor = 0
        col = 0
        if len(row_y) <= row:
            row_y.append(row_y[-1] + 260 + COL_GAP)

    x = START_X + col * (COL_W + COL_GAP)
    y_org = row_y[row]
    svg_organ, organ_h = _render_n1(organ, x, y_org, use_kimi=use_kimi, style_id=style_id)
    lines.append(svg_organ)
    col_cursor += col_span

    if col_cursor >= N_COLS:
        row += 1
        col_cursor = 0
        if len(row_y) <= row:
            row_y.append(row_y[-1] + organ_h + COL_GAP)
```

---

### Critères d'acceptation

- [ ] `./sullivan enrich` → terminal affiche `[PASS2]` et `[PASS3]` pour chaque organe
- [ ] `genome_enriched.json` contient `ux_step`, `layout_type`, `col_span` sur chaque N1
- [ ] `./sullivan zones` → SVG généré sans erreur Python
- [ ] Un organe `nav-header` affiche une barre horizontale avec pills nav
- [ ] Un organe `form-panel` affiche des champs label + input
- [ ] Un organe `dashboard` affiche 3 metric cards + barres chart
- [ ] Un organe `col_span=2` est deux fois plus large dans la grille
- [ ] Aucun appel KIMI/API dans les archetype renderers (tout statique)
- [ ] FJD valide visuellement le SVG généré

### Bootstrap Gemini OBLIGATOIRE

```
Tu es Gemini, agent frontend AetherFlow.
Mission 21D — Archetype Renderers + Passes 2+3.

AVANT DE CODER :
1. Lire Backend/Prod/enrichers/genome_enricher.py
2. Lire Backend/Prod/exporters/genome_to_svg_v2.py
3. Lire Frontend/2. GENOME/genome_enriched.json

RÈGLES ABSOLUES :
- Guillemets doubles UNIQUEMENT dans toutes les strings SVG/XML
- Chaque draw_* retourne (svg_string: str, h: int) — h entier
- archetype_renderers.py dans Backend/Prod/exporters/ (même dossier que genome_to_svg_v2.py)
- Import : from archetype_renderers import render_organ
- Ne pas supprimer --kimi dans genome_to_svg_v2.py
- Ne pas toucher genome_enricher.py au-delà des Passes 2+3

Livrer le code complet de chaque fichier entre triple backticks, chemin en commentaire L1.
```

---

## Mission 21C — Figma Bridge : Plugin & Sync [PENDING — après 21D validé]

**ACTOR: GEMINI**
**MODE: CODE DIRECT / Plugin Figma**
**DATE: 2026-03-03**
**STATUS: PENDING**

### Objectif
Pont Figma ↔ AetherFlow : plugin dédié pour importer le genome enrichi et synchroniser les styles design vers le backend.

### F1 — Plugin Figma (Scaffold)
- Fichiers : `figma-plugin/manifest.json`, `figma-plugin/ui.html`, `figma-plugin/code.js`
- UI : boutons "Importer Genome", "Sync Styles", "Check Changes"
- Les frames Figma importées utilisent `display_label` comme nom (pas l'ID ésotérique)

### F2 — Import : Genome → Figma
- `GET /api/genome` → Frames nommées par `display_label` N1, groupées par N0
- Stocker `genome_id` dans `pluginData` de chaque node

### F3 — Sync : Figma → AetherFlow
- Extraire fills/strokes/radius depuis nodes tagués → `POST /api/styles/sync`
- AetherFlow stocke dans `styles.json` + génère variables CSS

### Critères d'acceptation
- [ ] Plugin installable en mode dev Figma
- [ ] "Importer" → frames avec `display_label` comme nom
- [ ] "Sync" → backend reçoit styles, écrit `styles.json`
- [ ] Variables CSS générées depuis l'export Figma
