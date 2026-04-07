# ROADMAP — Genome Design Bridge
## AetherFlow ↔ Illustrator ↔ Figma ↔ Web

**Projet :** Figma Bridge
**Référence plan :** `PLAN_GENOME_DESIGN_BRIDGE.md`
**Date :** 2026-03-02

---

## Frontières hermétiques

| Acteur | Périmètre |
|---|---|
| **Claude + AetherFlow** | Backend Python : exporters, endpoints, style engine |
| **Gemini Bot** | JS plugin Figma : UI, logique document Figma, alertes |
| **FJD** | DA + validation SVG dans Illustrator + validation plugin dans Figma |

Aucun chevauchement. AetherFlow ne touche pas au JS Figma. Gemini ne touche pas au Python.

---

## Mission 21A — Genome → SVG exporter
**ACTOR: AETHERFLOW | MODE: -f (PROD) | STATUS: PENDING**
**Plan :** `plans/plan_21a_genome_svg.json`

### Périmètre
- `Backend/Prod/exporters/genome_to_svg.py` — script Python
- `Frontend/3. STENCILER/server_9998_v2.py` — ajouter `GET /api/export/svg`

### Critères d'acceptation
- [ ] `GET /api/export/svg` → télécharge `genome_scaffold.svg`
- [ ] SVG structuré : `<g id="n0_*">` → `<g id="n1_*">` → `<g id="n2_*">` → `<g id="n3_*">`
- [ ] Attributs genome : `data-genome-id`, `data-hint`, `data-name` sur chaque groupe
- [ ] Artboards 1440×900px par phase N0
- [ ] Layout automatique : organes N1 en grille, features N2 en colonnes
- [ ] Placeholders N3 : rectangles étiquetés avec `visual_hint`
- [ ] FJD ouvre dans Illustrator → calques nommés par IDs genome ✓

---

## Mission 21B — Figma Plugin : scaffold + UI
**ACTOR: GEMINI BOT | MODE: CODE DIRECT | STATUS: PENDING**

### Périmètre
```
figma-plugin/
  manifest.json   ← config plugin Figma (name, permissions, entrypoints)
  ui.html         ← panel plugin (3 boutons : Importer / Lire SVG / Sync)
  code.js         ← scaffold : lit genome → crée frames Figma taguées
```

### Ce que Gemini doit lire avant de coder
- `PLAN_GENOME_DESIGN_BRIDGE.md` (Phase 2A)
- La doc Figma Plugin API : `figma.createFrame()`, `node.setPluginData()`, `figma.root.children`

### Critères d'acceptation
- [ ] `manifest.json` valide (Figma Plugin API v1, permissions : `currentuser`)
- [ ] `ui.html` : panel avec 3 boutons (Importer genome / Lire layers SVG / Sync styles)
- [ ] `code.js` — fonction `importGenome()` :
  - fetch `http://localhost:9998/api/genome`
  - Pour chaque N1 → `figma.createFrame()` nommé `organ.id`
  - `frame.setPluginData('genomeId', organ.id)` + `setPluginData('genomeName', organ.name)`
  - Frames organisées en grille sur la page courante
- [ ] `code.js` — fonction `readSvgLayers()` :
  - Parcourt tous les nodes de la page courante
  - Pour chaque node dont le nom matche `n1_*` ou `n2_*` ou `n3_*` → `setPluginData('genomeId', node.name)`
  - Retourne un résumé dans le panel UI
- [ ] Plugin chargeable dans Figma Desktop (Plugins > Development > Import plugin from manifest)

### Non-périmètre (Mission 21D)
- Alerte hors-genome → Mission 21D
- Export styles → Mission 21D

---

## Mission 21C — Backend styles sync
**ACTOR: AETHERFLOW | MODE: -f (PROD) | STATUS: PENDING**
**Plan :** `plans/plan_21c_styles_engine.json`

### Périmètre
- `server_9998_v2.py` — ajouter `POST /api/styles/sync` + `POST /api/genome/request-feature`
- `Backend/Prod/core/style_engine.py` — convertit Figma fills/strokes → CSS

### Critères d'acceptation
- [ ] `POST /api/styles/sync` body: `{ "n1_ir": { fills, strokes, cornerRadius, fontName, opacity } }`
  - Convertit Figma color objects → hex CSS
  - Sauvegarde dans `Frontend/2. GENOME/styles.json` (merge, pas écrase)
  - Retourne `{ status: "ok", updated: N }`
- [ ] `GET /api/styles/{genome_id}` → retourne CSS tokens pour ce nœud
- [ ] `POST /api/genome/request-feature` body: `{ name, visual_hint, description }`
  - Ajoute un nœud `pending` dans le genome (section `_pending` de `genome_reference.json`)
  - Retourne l'ID généré
- [ ] `style_engine.py` : `figma_color_to_css(fills)` → `"#rrggbb"` (ou `rgba`)
- [ ] Tests : `test_style_engine.py` — 3 cas (solid fill, gradient, transparent)

---

## Mission 21D — Figma Plugin : alertes + export
**ACTOR: GEMINI BOT | MODE: CODE DIRECT | STATUS: PENDING**
**Dépend de :** Mission 21B livré + validé, Mission 21C livré + validé

### Périmètre
Compléter `figma-plugin/code.js` (ne pas réécrire — PATCH uniquement) :

### Ce que Gemini doit ajouter
1. **Alerte hors-genome** (listener `figma.on('documentchange')`) :
   - Si node créé sans `pluginData.genomeId` → `figma.notify(...)` avec bouton "Envoyer à AetherFlow"
   - Clic bouton → `POST /api/genome/request-feature` avec `name`, `visual_hint` deviné

2. **Export styles** (fonction `syncStylesToAetherFlow()`) :
   - Parcourt tous les nodes taguués `genomeId`
   - Collecte `fills`, `strokes`, `cornerRadius`, `fontName`, `opacity`
   - `POST /api/styles/sync` avec le styleMap

3. **Guess hint** (fonction `guessHint(node)`) :
   - Rectangle plein → `'card'`
   - Rectangle avec texte "btn" ou petit → `'button'`
   - Node avec beaucoup d'enfants → `'form'`
   - Fallback → `'component'`

### Critères d'acceptation
- [ ] Créer un element dans Figma sans tag → notification apparaît dans Figma
- [ ] Clic "Oui" → élément tagué `pending_*` + `POST /api/genome/request-feature` confirmé
- [ ] Bouton "Sync styles" panel → `POST /api/styles/sync` → `styles.json` mis à jour
- [ ] Pas de régression sur Mission 21B (import genome + readSvgLayers)

---

## Mission 21E — Intégration finale : HTML stylisé
**ACTOR: AETHERFLOW | MODE: -f (PROD) | STATUS: PENDING**
**Dépend de :** Missions 21A + 21C livrés

### Périmètre
- `Frontend/3. STENCILER/genome_preview.py` — injecter `styles.json` dans le rendu HTML

### Critères d'acceptation
- [ ] `GET /preview` : si `styles.json` contient l'ID d'un nœud → applique les styles CSS inline
- [ ] Fallback gracieux si pas de styles pour un nœud (styles par défaut inchangés)
- [ ] `GET /api/render/{genome_id}` → retourne le HTML complet d'un organe avec ses styles

---

## Ordre d'exécution

```
21A (AetherFlow)  →  FJD valide SVG dans Illustrator
        ↓
21B (Gemini)      →  FJD valide plugin dans Figma
        ↓
21C (AetherFlow)  →  tests endpoints styles
        ↓
21D (Gemini)      →  FJD valide alertes + sync dans Figma
        ↓
21E (AetherFlow)  →  FJD valide rendu stylisé dans browser
```

Chaque étape validée par FJD avant la suivante. Pas de mission lancée en parallèle.

---

## Plans AetherFlow

| Mission | Plan JSON | Commande |
|---|---|---|
| 21A | `plans/plan_21a_genome_svg.json` | `aetherflow --plan plans/plan_21a_genome_svg.json --output output/` |
| 21C | `plans/plan_21c_styles_engine.json` | `aetherflow --plan plans/plan_21c_styles_engine.json --output output/` |
| 21E | `plans/plan_21e_html_render.json` | `aetherflow --plan plans/plan_21e_html_render.json --output output/` |

Plans Gemini : missions 21B et 21D sont CODE DIRECT (pas de plan JSON AetherFlow).

---

## Rollback

Chaque mission est indépendante. En cas d'échec :
- AetherFlow : le fichier `.generated` n'est pas appliqué, rollback automatique
- Gemini : `figma-plugin/` est un dossier isolé, ne touche pas au stenciler ou au server
- `styles.json` : fichier additionnel, sa suppression = retour état précédent sans impact
