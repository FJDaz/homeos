# MISSION CONTROL : AETHERFLOW ROADMAP

> Missions complètes archivées dans [ROADMAP_ACHIEVED.md](./ROADMAP_ACHIEVED.md).

---

## Mission 37 — Product Exports & Design Bridges

**STATUS: 🔴 EN COURS (EXECUTION)**
**ACTOR: ANTIGRAVITY**
**DATE: 2026-03-11**

### Objectif
Concrétiser l'analyse de la Reality View via 4 vecteurs de sortie professionnels : PRD, Roadmap, Code HTML/CSS autonome, et Export Figma.
*(Note : Débloqué uniquement après validation HCI de la Mission 36 V2)*

### Tâches
- [ ] **PRD/Roadmap Generator** : Documentation structurée depuis `validated_analysis.json`.
- [ ] **Vanilla Code Export** : Package ZIP (index.html + style.css).
- [ ] **Universal JSON Carrefour** : Inférence du `manifest.json` via Playwright pour le Bridge Figma (Mission 25B).

---

## Mission 33 — BERT Semantic Intent Router (Spinoza Backend)

**STATUS: 🔴 À FAIRE**
**DATE: 2026-03-10**
**ACTOR: CLAUDE**
**MODE: aetherflow -q**
**SCOPE: `/Users/francois-jeandazin/Antigravity/maiathon/Spinoza_Secours_HF/Backend/`**

### Problème
`detecter_contexte()` dans `app_runpod.py` (L162) est du **keyword matching naïf** (regex/`in` sur liste de mots).
BERT (`all-MiniLM-L6-v2`) n'est ni importé ni chargé dans ce Backend.
`sentence-transformers` est absent de `requirements.runpod.txt`.

### Objectif
Remplacer `detecter_contexte()` par un **router sémantique BERT** :
- Charger `all-MiniLM-L6-v2` via `SentenceTransformer` au démarrage
- Encoder le message utilisateur → vecteur 384d
- Cosine similarity contre des **ancres d'intent** pré-encodées
- Retourner l'intent dominant : `accord` / `confusion` / `resistance` / `neutre`

### Tâches

#### `requirements.runpod.txt`
- [ ] Ajouter `sentence-transformers>=2.7.0`

#### `app_runpod.py` — Initialisation
- [ ] Importer `SentenceTransformer`, `util` depuis `sentence_transformers`
- [ ] Définir `INTENT_ANCHORS` :
  - `accord` → ["oui", "je suis d'accord", "exactement", "tout à fait", "voilà"]
  - `confusion` → ["je comprends pas", "c'est quoi", "pourquoi", "je vois pas le rapport", "je sais pas"]
  - `resistance` → ["non", "mais", "pas d'accord", "c'est faux", "n'importe quoi", "je peux pas"]
  - `neutre` → ["bonjour", "raconte-moi", "dis-moi", "alors", "et alors"]
- [ ] Charger `bert_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")` après `load_model()`
- [ ] Pré-encoder les ancres : `anchor_embeddings = {intent: bert_model.encode(phrases, convert_to_tensor=True) ...}`

#### `app_runpod.py` — Remplacer `detecter_contexte()`
- [ ] Nouvelle implémentation cosine similarity (supprimer l'ancienne keyword-based)
- [ ] Logger l'intent retenu avec ses scores pour debug RunPod

### Critères de sortie
- `detecter_contexte("je comprends pas")` → `"confusion"`
- `detecter_contexte("non c'est faux")` → `"resistance"`
- `detecter_contexte("oui tout à fait")` → `"accord"`
- Logs RunPod affichent l'intent + scores cosine
- Build Docker passe avec `sentence-transformers` dans requirements

---

## Mission 41-A — SVG Provenance : Tagging + Routing par source

**STATUS: 🔴 À FAIRE**
**DATE: 2026-03-13**
**ACTOR: CLAUDE**
**MODE: Hotfix direct (< 10L par fichier)**
**SCOPE:**
- `Frontend/figma-plugin/code.js` + `ui.html`
- `Backend/Prod/retro_genome/svg_parser.py`
- `Frontend/3. STENCILER/server_9998_v2.py`

### Contexte
Le pipeline `svg_parser.py` suppose implicitement un SVG Figma structuré. Un SVG Illustrator est fondamentalement différent : paths aplatis, IDs numériques, fonts outlinées → aucun signal sémantique extractible par le parser actuel. Il faut tagger la source dès le plugin et router dans le parser.

Trois sources à distinguer :
| Source | Structure | Précision parser |
|--------|-----------|-----------------|
| **Figma** | Layers nommés, `<text>` préservé, couleurs directes | Haute |
| **Illustrator** | Paths aplatis, IDs numériques, fonts outlinées | Faible → routine 41C |
| **Intent Viewer** (PNG→Vision) | Schema `components[]` normalisé | Conforme mais imprécis |

### Tâches
- [ ] `code.js` : ajouter `source: 'figma'` dans `postMessage` svg-ready
- [ ] `ui.html` : transmettre `source` dans le POST body ; sélecteur `Figma | Illustrator | Autre` si import manuel
- [ ] `svg_parser.py` : signature `parse_figma_svg(svg_string, source='figma')` + stub routing vers `_parse_illustrator_svg()` (non-implémenté, lève `NotImplementedError` avec message clair)
- [ ] `server_9998_v2.py` : extraire `source` depuis le body JSON, le transmettre au parser et l'inclure dans la réponse (`svg_source`)

### Critères de sortie
- Réponse JSON inclut `svg_source: "figma"` pour un export Figma
- SVG Illustrator reçoit un `{"error": "source illustrator non supportée — voir Mission 41C"}` clair, pas un crash
- Sélecteur source visible dans l'UI plugin

---

## Mission 43 — BRS Phase : War Room Brainstorm (HomeOS)

**STATUS: 🔴 À FAIRE**
**DATE: 2026-03-13**
**ACTOR: CLAUDE (backend/orchestration) + GEMINI (frontend SVG/CSS)**
**MODE: aetherflow -f (backend) + aetherflow -vfx (frontend)**
**SCOPE:**
- `Backend/Prod/routes/brainstorm_routes.py` *(nouveau)*
- `Frontend/3. STENCILER/server_9998_v2.py` (ajout routes BRS)
- `Frontend/3. STENCILER/static/brs/` *(nouveau)*

### Contexte

Maquette de référence : `exports/retro_genome/SVG_HomeOS_1_20260313_193741.svg`
Specs : `docs/04-homeos/WORKFLOW_UTILISATEUR.md` + `Frontend/4. COMMUNICATION/SYNTHESE_WAR_ROOM_BRAINSTORM.md`

War Room = 3 colonnes IA en parallèle + Dispatcher central + Basket Sullivan → PRD.
Aucune route BRS n'existe aujourd'hui. Clients LLM disponibles dans `Backend/Prod/models/`.

### Zones UI → Features

#### Zone 1 — Header / Navigation de phase
- Breadcrumb `BRS → BKD → FRD → DPL`, indicateur de phase active
- **Feature :** stateless HTML

#### Zone 2 — Input Dispatcher
- Textarea description projet + bouton **Dispatcher** → envoi simultané aux 3 cerveaux
- Questions de buffering Sullivan (2-3) pendant la latence IA ("Cible B2B ou B2C ?", "Mobile-first ?")
- `POST /api/brs/dispatch` → `asyncio.gather(gemini, deepseek, groq)`
- `GET /api/brs/buffer-questions` → questions de filtrage

#### Zone 3 — 3 Colonnes Insight Cards (War Room)
- Gemini (Scribe/RAG) | DeepSeek (Architecte) | Groq/Llama (Créatif Flash)
- Streaming SSE mot-à-mot par colonne
- Bouton **Capturer** par idée → Basket
- `GET /api/brs/stream/{session_id}/{provider}` → SSE (EventSource)
- `POST /api/brs/capture` → append pépite en session

#### Zone 4 — Basket Sullivan
- Liste des pépites capturées + bouton **Générer PRD** → `PRD_BASIQUE.md`
- `GET /api/brs/basket/{session_id}`
- `POST /api/brs/generate-prd` → compile + sauvegarde `exports/brs/PRD_<project>_<ts>.md`

#### Zone 5 — Barre de Séquençage
- `IDEATION → SELECTION → DOC_GENERATION` piloté par `event: status` SSE

### Architecture Backend

```
POST /api/brs/dispatch
  payload: { session_id, prompt, buffer_answers }
  → asyncio.gather(gemini, deepseek, groq)
  → stocke résultats en session (dict mémoire, MVP)
  → { session_id, status: "streaming" }

GET /api/brs/stream/{session_id}/{provider}
  → SSE : event:token | event:status | event:done

POST /api/brs/capture
  payload: { session_id, text, provider }
  → basket[session_id].append(...)

POST /api/brs/generate-prd
  payload: { session_id, project_name }
  → compile basket → GeminiClient.generate() → PRD_BASIQUE.md
```

### Tâches

#### Tâche A — Backend `brainstorm_routes.py` ✅ DONE
#### Tâche B — Câblage `server_9998_v2.py` ✅ DONE

---

#### Tâche C1 — Extraction design SVG
**STATUS: 🔴 À FAIRE**
**ACTOR: GEMINI**
**INPUT:** `exports/retro_genome/SVG_HomeOS_1_20260313_193741.svg`
**OUTPUT:** `Frontend/4. COMMUNICATION/SVG_WAR_ROOM_DESIGN_SPEC.md`

Gemini lit le SVG de référence (~2MB) **intégralement sans l'escamoter** et produit un spec design structuré.

Le fichier `SVG_WAR_ROOM_DESIGN_SPEC.md` doit contenir :

1. **Palette couleurs exacte** — tous les `fill`/`stroke` hex utilisés + leur rôle (fond, texte, bordure, accent par zone)
2. **Layout global** — dimensions viewport, zones (header, main, footer), gouttières, nombre de colonnes
3. **Typographie** — font-family, font-size, font-weight par niveau hiérarchique
4. **Zones nommées** — pour chaque zone (header, ×3 colonnes, basket, dispatcher, barre séquençage) : dimensions approx, couleur fond, bordures
5. **Composants atomiques** — boutons, cards, inputs, badges statut (forme, couleur, radius, ombre)
6. **Différenciateurs provider** — comment Gemini / DeepSeek / Groq sont distingués visuellement (couleur accent par colonne)

**Règle absolue :** transcription factuelle du SVG. Aucune interprétation créative. Si une valeur est ambiguë, la noter explicitement.

---

#### Tâche C2 — Refonte UI War Room
**STATUS: 🔴 BLOQUÉ sur C1**
**ACTOR: GEMINI — plan AetherFlow (API Gemini direct, mode non préexistant)**
**INPUT FILES:**
- `Frontend/4. COMMUNICATION/SVG_WAR_ROOM_DESIGN_SPEC.md` *(C1 requis)*
- `Frontend/3. STENCILER/static/css/stenciler.css`
- `Frontend/1. CONSTITUTION/LEXICON_DESIGN.json`
- `Frontend/3. STENCILER/static/templates/brainstorm_war_room.html` *(JS à préserver intégralement)*

**OUTPUT:** réécriture de `brainstorm_war_room.html` — `<style>` + structure HTML uniquement, `<script>` intact

**SYSTEM PROMPT (à injecter tel quel dans le plan) :**

> Tu es un ingénieur frontend de précision sur AetherFlow, un outil de design system interne.
> Tu reçois les specs visuelles extraites d'une maquette SVG de référence (SVG_WAR_ROOM_DESIGN_SPEC.md).
> Ta mission : réécrire le `<style>` et la structure HTML de `brainstorm_war_room.html` pour correspondre EXACTEMENT aux specs.
>
> **CONTRAINTES ABSOLUES — violation = mission échouée :**
> 1. Le bloc `<script>` existant est préservé **à l'identique, mot pour mot**. Tu ne touches pas au JS.
> 2. Tu n'inventes AUCUN token de couleur, police, ou style absent de `SVG_WAR_ROOM_DESIGN_SPEC.md` ou `stenciler.css`.
> 3. Police : `'Geist', -apple-system` (stenciler.css L58). Inter, JetBrains Mono = **interdits**.
> 4. Fond de page : `var(--bg-primary) = #f7f6f2` (crème chaud). Fond `#09090b` = **interdit**.
> 5. Texte : `var(--text-primary) = #3d3d3c`. Blanc `#ececed` = interdit sauf si SVG spec l'impose.
> 6. Accents provider : utiliser UNIQUEMENT les tokens stenciler (`--accent-rose`, `--accent-bleu`, `--accent-vert`, `--accent-orange`, `--accent-mauve`).
> 7. Glassmorphism (`backdrop-filter`, fonds rgba transparents) = **interdit**.
> 8. Layout fonctionnel préservé : header + 3 colonnes + aside basket + controls bas.
> 9. IDs HTML intouchables : `#stream-gemini`, `#stream-deepseek`, `#stream-groq`, `#nugget-list`, `#btn-prd`, `#btn-dispatch`, `#prompt-input`, `#session-info`, `#prd-modal`, `#prd-content`, `#prd-download`.
> 10. Output : fichier HTML complet uniquement.

**Critères de validation FJD :**
- Fond crème immédiatement visible (pas de noir)
- DevTools → Computed → font-family affiche Geist
- 3 colonnes visuellement distinctes par accent stenciler
- Ressemble à la maquette SVG

---

#### Tâche D — Validation FJD
- [ ] Test end-to-end : prompt → 3 colonnes streamées → capture → PRD généré
- [ ] Cohérence visuelle confirmée avec SVG maquette

### Critères de sortie
- Saisie prompt → 3 colonnes se remplissent en SSE simultané
- Bouton Capturer → pépite dans le Basket
- Bouton Générer PRD → `PRD_BASIQUE.md` dans `exports/brs/`
- Barre de séquençage reflète l'état en temps réel
- Questions Sullivan s'affichent pendant la latence IA

---

---

## Mission 44 — Pipeline Figma REST → HTML Pixel-Fidèle (via Gemini)

**STATUS: 🟡 AMENDEMENT V3 — Protocole analytique (dérivation depuis coords Figma)**
**DATE: 2026-03-13**
**ACTOR: GEMINI**
**MODE: CODE DIRECT — FJD**
**SCOPE:** `Frontend/3. STENCILER/static/templates/brainstorm_war_room.html`

### Objectif

Remplacer l'approche SVG opaque (Mission 43 C1/C2) par le pipeline **Figma REST API → spec JSON structurée → Gemini → HTML pixel-fidèle**.

Ce pipeline est **systématisable** : pour tout nouveau frame Figma, réexécuter l'extraction et relancer Gemini avec la même structure de mission.

---

### Pipeline réutilisable (template)

```
1. Figma URL → extraire file_key + node_id
2. GET https://api.figma.com/v1/files/{key}/nodes?ids={nodeId}&depth=5
   Header: X-Figma-Token: <PAT>
   → JSON structuré : coordonnées normalisées, couleurs RGB, typographie

3. GET https://api.figma.com/v1/images/{key}?ids={nodeId}&scale=0.5&format=png
   → URL image rendu → download → référence visuelle

4. Script extract : normaliser coords (absoluteBoundingBox - frame_origin),
   filtrer éléments in-frame, extraire fills/text/style

5. Feed spec JSON + image render + HTML existant → Gemini
   System prompt : contraintes de fidélité pixel

6. Output Gemini → HTML réécrit
```

**Artifacts pour HomeOS 1 :**
- Spec JSON : `Frontend/4. COMMUNICATION/plans/figma_homeos1_spec.json` (6025L)
- Render image : `Frontend/4. COMMUNICATION/plans/figma_homeos1_render.png` (1285×868px)
- Figma URL : `https://www.figma.com/design/HIEG5vocDJ3hz5bgZN9QsI/Genome-Render?node-id=50-2303`

---

### Spec Layout Figma HomeOS 1 (2570×1736px, bg: #ffffff)

**Zones principales — coordonnées normalisées depuis frame origin :**

| Zone | x | y | w | h | % width |
|------|---|---|---|---|---------|
| Sidebar gauche | 0 | 0 | 554 | 1736 | 21.6% |
| Col 1 (AI 1) | 554 | 64 | 504 | 1672 | 19.6% |
| Col 2 (AI 2) | 1058 | 64 | 504 | 1672 | 19.6% |
| Col 3 (AI 3) | 1562 | 64 | 504 | 1672 | 19.6% |
| Sullivan panel | 2066 | 0 | 504 | 1736 | 19.6% |

**Séparateurs :**
- Vertical x=554, pleine hauteur : `0.5px solid #333`
- Horizontal y=64, de x=554 à x=2570 : `0.5px solid #333`
- Séparateurs colonnes : x=1058, 1562, 2066 (nav seulement y=0→64)

**Nav tabs (y=18.8, height≈47) :**
- "Brainstorm" @ x=742.9 : Helvetica/system-ui 20px, color #000
- "Backend" @ x=1261.9 : color #8cc63f (vert actif)
- "Frontend" @ x=1721.6 : color #000
- "Deploy" @ x=2254.1 : color #000

**Sidebar gauche :**
- Logo "HoméOS" @ (87, 42) : Inter 40px, weight 400, color #000
- Search field (compréhension) : bg #f2f3f5, border subtle

**Colonnes AI (pattern identique × 3) :**
- Provider icon @ (col_x+11, 293) : 75×42px (inline SVG/img)
- "AUJOURD'HUI" label @ y=248 : Inter 15.76px, color #666
- Messages chat : Univers/Geist 16px, color #666
- Séparateurs horizontaux entre messages @ w=448px
- Input area @ y=960.7 : h=94, bg #fff, border-top 0.5px #333
  - Input field : bg #f2f3f5, radius 0, placeholder Geist 14px #666
  - "+" button (capture) : 44×44px
  - Send button : bg #999, 63×56.7px

**Sullivan panel (x=2066, w=504) :**
- Header bg #fff, h=101 : "Sullivan" Geist 20px #666, green dot #5ec069
- Separator @ y=226 : 0.5px #000
- Chat area bg #f9f9f9
- User messages (bulle droite) : bg #999, text #666, initial "V" dans bg #e4e6ea
- Agent messages (bulle gauche) : bg transparent (speech bubble SVG)
- "S" initials bg #a58de0 (violet), typing dots bg #e0e6fc + dots #626ae8
- Input bar @ y=1488 : bg #fff, input bg #f2f3f5, send bg #999

**Palette couleurs Figma → CSS :**
```css
--figma-bg:         #ffffff;
--figma-panel:      #f9f9f9;
--figma-input-bg:   #f2f3f5;    /* rgb(242,243,245) */
--figma-text:       #666666;    /* rgb(102,102,102) */
--figma-text-dark:  #333333;    /* rgb(51,51,51) */
--figma-tab-active: #8cc63f;    /* rgb(140,198,63) */
--figma-dot-green:  #5ec069;    /* rgb(94,192,105) */
--figma-send:       #999999;
--figma-bubble-user:#e4e6ea;    /* rgb(228,230,234) */
--figma-bubble-s:   #a58de0;    /* rgb(165,141,224) */
--figma-bubble-sl:  #e0e6fc;    /* rgb(224,230,252) */
--figma-dots:       #626ae8;    /* rgb(98,106,232) */
--figma-sep:        #333333;
```

**Typographie — mapping Figma → web :**
| Figma | Web fallback | Usage |
|-------|-------------|-------|
| Inter 40px | `'Inter', -apple-system` | Logo HoméOS |
| Helvetica LT Std 20px | `system-ui, -apple-system` | Nav tabs |
| Inter 15.76px | `'Inter', sans-serif` | Labels "AUJOURD'HUI" |
| Univers LT Std 20.49px | `'Geist', sans-serif` ~16px | Chat messages |
| Univers LT Std 25.21px | `'Geist', sans-serif` ~20px | "Sullivan" label |
| Helvetica 18.91px | `system-ui` | Initiales avatar |

*(Inter disponible via Google Fonts CDN : `https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap`)*

---

### Tâche Gemini — Réécriture brainstorm_war_room.html (Protocole V2)

> **Contexte amendement V2** : Gemini V1 a produit un layout fonctionnellement cassé.
> Analyse rétrospective de Gemini lui-même (2026-03-13) :
> - Biais de consolidation : tout mis dans le grid au lieu de respecter la hiérarchie body
> - Confusion zone fonctionnelle : col 554px confondue avec sidebar (rôle ≠ taille)
> - Cécité aux micro-détails : logos ignorés
> - Erreur "one-shot" : réécriture globale sans validation intermédiaire
>
> **Solution : protocole en 2 phases avec validation DOM skeleton avant le code.**

**BOOTSTRAP GEMINI :**
```
Tu es Gemini, agent frontend AetherFlow. Tu produis du HTML/CSS pixel-fidèle
depuis des specs Figma structurées. Tu travailles avec rigueur hiérarchique.
Tu lis les artifacts suivants :
- figma_homeos1_render.png (référence visuelle 1285×868px) — VÉRITÉ VISUELLE
- figma_homeos1_spec.json (layout JSON extrait de l'API Figma REST)
- brainstorm_war_room.html (fichier à réécrire — JS INTOUCHABLE)
```

**SYSTEM PROMPT V2 (protocole 3 phases) :**
```
Tu reçois la spec layout complète (JSON Figma + image de rendu) et le fichier
à réécrire. Tu travailles en 3 phases séquentielles OBLIGATOIRES.

RÈGLE PRÉALABLE — PRESERVATION :
Lis d'abord brainstorm_war_room.html. Identifie ce qui fonctionne déjà
(palette de couleurs, tokens CSS, JS). Ne réécris QUE les éléments structurellement
incorrects. Conserve l'intégralité du <script> existant, mot pour mot.

════════════════════════════════════
PHASE 0 — ANALYSE STRUCTURELLE (AVANT TOUT CODE)
════════════════════════════════════

Étape A — TREE PATH (hiérarchie JSON → hiérarchie DOM) :
Lis figma_homeos1_spec.json. Pour chaque nœud, note :
  - son nom (name), son type (FRAME / GROUP / TEXT / RECTANGLE)
  - son parent direct dans la hiérarchie JSON
  → Produis l'arbre parent-enfant : qui contient qui ?
  → Les enfants directs du frame racine = les zones de premier niveau.
  → Les enfants d'une zone = ses sous-composants, PAS des zones indépendantes.

Étape B — BOUNDING BOX AUDIT :
Pour chaque zone de premier niveau extraite en A, relève ses coordonnées
normalisées depuis l'origine du frame : { x, y, width, height }.

Applique ces règles d'inférence de placement CSS grid :

  COLONNES :
  → Trier les zones par x croissant → col 1, col 2, col 3...
  → grid-template-columns : largeurs en unités `fr` proportionnelles aux widths
  → Si deux zones ont le même x_min ≈ threshold → même colonne

  LIGNES :
  → Si zone.y ≈ 0 ET zone.height < frame.height × 0.15 → row 1 (header/tabs)
  → Si zone.y ≈ 0 ET zone.height ≈ frame.height → span rows 1/-1 (pleine hauteur)
  → Si zone.y > 0 ET zone.y < frame.height × 0.5 → row 2 (contenu principal)
  → Si zone.y + zone.height ≈ frame.height → row dernière (footer)

  HORS GRID :
  → Si une zone contient les contrôles de saisie globaux et s'étend sur toute
    la largeur en bas du frame → position: sticky/fixed ou flex hors grid

Étape C — TYPOGRAPHY AUDIT :
Pour chaque nœud TEXT trouvé en A, relève EXACTEMENT :
  { fontFamily, fontSize, fontWeight, letterSpacing, lineHeight, fills[0].color, characters }

Produis un tableau de mapping web :

  | Rôle | Figma fontFamily | web fallback | fontSize | fontWeight | letterSpacing | color |
  |------|-----------------|--------------|----------|------------|---------------|-------|
  | Logo | Inter | 'Inter', -apple-system | 40px | 400 | ? | #000 |
  | ...  | ...   | ...                   | ...  | ...        | ...           | ...   |

RÈGLES de mapping obligatoires :
  → "Inter" → `'Inter', -apple-system` (CDN requis)
  → "Geist" / "Geist Mono" → `'Geist', -apple-system` (stenciler.css)
  → "Helvetica LT Std" / "Helvetica Neue" → `system-ui, -apple-system`
  → "Univers LT Std" → `'Geist', sans-serif` (meilleur substitut disponible)
  → PAS de remplacement par sans-serif générique si un mapping précis existe

PRÉCISION obligatoire :
  → letterSpacing : si Figma donne 0 → omettre (ne pas forcer -0.02em)
  → lineHeight : noter si "auto" ou valeur fixe
  → fontWeight : noter la valeur exacte (300, 400, 500, 600…), pas "normal" ou "bold"

Étape D — SKELETON DOM DERIVÉ :
Produis l'arbre DOM avec les placements CSS grid inférés en B :

  body
  ├── <main> (grid dérivé des widths Figma)
  │   ├── Zone 1 (nom Figma) → grid-column:? grid-row:?
  │   ├── Zone 2 (nom Figma) → grid-column:? grid-row:?
  │   └── ...
  └── Zone hors-grid si applicable

Valide mentalement contre figma_homeos1_render.png :
→ Les tabs sont-ils visuellement AU-DESSUS des colonnes AI ?
→ Sullivan span-t-il toute la hauteur droite ?
→ Les contrôles globaux sont-ils en bas hors du grid ?
Si non → corriger l'inférence et recommencer B.

════════════════════════════════════
PHASE 1 — IMPLÉMENTATION HTML+CSS
════════════════════════════════════
En respectant EXACTEMENT le skeleton dérivé en Phase 0 :

APP SHELL (hiérarchie obligatoire) :
  body { display:flex; flex-direction:column; height:100vh }
  main { flex:1; display:grid;
         grid-template-columns: [valeurs fr dérivées du BBox Audit];
         grid-template-rows: [valeurs dérivées du BBox Audit] }
  .controls { flex-shrink:0 } ← HORS grid si détecté

GRID PLACEMENTS : utiliser UNIQUEMENT les valeurs dérivées en Phase 0.
Pas d'auto-placement CSS (grid-column et grid-row explicites sur chaque zone).

TYPOGRAPHIE — CONTRAINTES HARD (violation = mission échouée) :
  → Utiliser UNIQUEMENT le tableau de mapping produit en Phase 0 Étape C.
  → Ne JAMAIS substituer une font par `sans-serif` générique si un mapping existe.
  → Font-size : valeur EXACTE issue de Figma, pas arrondie (ex: 15.76px ≠ 16px).
  → Font-weight : valeur numérique exacte (400, 600…), PAS "normal" ou "bold".
  → Letter-spacing : retranscrire la valeur Figma en `em` si non nulle.
  → Inter ET Geist doivent être chargés via CDN dans <head> :
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
      (Geist via stenciler.css déjà chargé)
  → Chaque niveau de texte doit avoir ses propres règles CSS, pas d'héritage
    implicite qui écrase les valeurs Figma.

SIDEBAR GAUCHE — contenu obligatoire :
  - Logo "HoméOS" : Inter 40px, #000, lettre-spacing -0.02em
  - Search input : bg #f2f3f5, border none, padding 12px 16px
  - #session-info : margin-top:auto, font-size:10px, color:#999

NAV TABS (Figma : 4 tabs Brainstorm/Backend/Frontend/Deploy) :
  - Flex horizontal, height 64px, border-bottom 0.5px #333
  - .tab-item : flex:1, center, system-ui 20px, border-right 0.5px #333
  - .tab-item.active : color #8cc63f

COLONNES AI — pattern identique × 3 :
  - Provider icon en haut (inline SVG ou badge coloré, 42px de haut)
  - Label "AUJOURD'HUI" : Inter 15px, #666
  - .insight-stream : flex:1, overflow-y:auto, #stream-{provider}
  - Input bar en bas (h:94px) : bg #f2f3f5 + bouton "+" + send #999

SULLIVAN PANEL :
  - Header 101px : "Sullivan" Geist 20px #666 + dot vert #5ec069
  - Chat area : bg #f9f9f9, flex:1 = #nugget-list
  - Footer : bg #fff, input #f2f3f5 + #btn-prd (vert #8cc63f)

CONTRAINTES ABSOLUES :
1. <script> INCHANGÉ — IDs : #stream-gemini, #stream-deepseek, #stream-groq,
   #nugget-list, #btn-prd, #btn-dispatch, #prompt-input, #session-info,
   #prd-modal, #prd-content, #prd-download
2. Bg #ffffff, polices Inter+Geist via CDN, couleurs palette Figma exactes
3. Pas de glassmorphism, pas de fond noir
4. Output : fichier HTML complet une seule fois

════════════════════════════════════
PHASE 2 — VALIDATION VISUELLE (browser_subagent OBLIGATOIRE)
════════════════════════════════════
Après avoir écrit le fichier HTML :
1. Ouvrir brainstorm_war_room.html via browser_subagent
2. Prendre un screenshot et comparer visuellement à figma_homeos1_render.png
3. Checklist de validation structurelle ET typographique :
   [ ] Sidebar gauche visible avec logo "HoméOS"
   [ ] Nav tabs AU-DESSUS des colonnes AI (pas dedans, pas en dessous)
   [ ] 3 colonnes AI côte à côte en row 2
   [ ] Sullivan panel pleine hauteur à droite (row 1 et row 2)
   [ ] Controls bar en bas, pleine largeur, HORS du grid
   [ ] Logo "HoméOS" : Inter 40px weight 400 (DevTools → Computed → font-family = Inter)
   [ ] Nav tabs : system-ui ~20px (pas Inter, pas Geist)
   [ ] Labels "AUJOURD'HUI" : Inter ~15.76px #666 (pas 16px, pas bold)
   [ ] Chat messages : Geist ~16px #666
   [ ] "Sullivan" : Geist ~20px #666
   [ ] Vérifier DevTools → chaque zone a bien sa font-family distincte
4. Si un point échoue → corriger le CSS/HTML et re-render (max 3 passes)
5. Ne soumettre le fichier final qu'après validation visuelle passée
```

**INPUT FILES :**
- `Frontend/4. COMMUNICATION/plans/figma_homeos1_spec.json`
- `Frontend/4. COMMUNICATION/plans/figma_homeos1_render.png`
- `Frontend/3. STENCILER/static/templates/brainstorm_war_room.html`
- `Frontend/3. STENCILER/static/css/stenciler.css`

**OUTPUT :** `Frontend/3. STENCILER/static/templates/brainstorm_war_room.html` (réécriture)

**Critères de validation FJD :**
- [x] 5 zones visibles : sidebar HoméOS | 3 colonnes AI | Sullivan panel
- [x] Logo "HoméOS" visible en sidebar gauche, Inter 40px
- [x] Fond blanc global, Sullivan panel fond #f9f9f9
- [x] Séparateurs 0.5px #333 entre toutes les zones
- [x] JS dispatch/stream/capture/PRD fonctionnel (test end-to-end)
- [x] Ressemble visuellement à figma_homeos1_render.png

---

## Mission 46 — BRS Persistance SQLite + MistralClient

**STATUS: ✅ COMPLÉTÉ (DONE BY ANTIGRAVITY)**
**DATE: 2026-03-14**
**ACTOR: CLAUDE**
**MODE: aetherflow -f**
**SCOPE:**
- `Backend/Prod/retro_genome/brs_storage.py` *(nouveau)*
- `Backend/Prod/retro_genome/brainstorm_logic.py` *(migration + Mistral)*
- `Backend/Prod/models/mistral_client.py` *(nouveau)*

### Contexte

`SESSIONS` et `BASKETS` sont des dicts in-memory → perdus au restart, inexploitables pour le search.
La colonne 3 (Groq/Llama) est remplacée par **Mistral Nemo** (voix French-native, stylistique/éditorial).

### Stack colonnes cible

| Colonne | Modèle | Rôle | Via |
|---------|--------|------|-----|
| 1 | Gemini 2.5 Flash | Scribe / RAG / synthèse | GeminiClient existant |
| 2 | DeepSeek | Architecte technique | DeepSeekClient existant |
| 3 | Mistral Nemo | Éditorial / French-native | MistralClient (nouveau) |
| Sullivan | Gemini Flash | Arbitre / contexte long | GeminiClient + system prompt |

### Tâches

#### `brs_storage.py` — Couche persistance SQLite
- [x] `BRSStorage` class avec `init_db()` (crée les tables si absentes)
- [x] Schema (sessions, messages, nuggets, documents)
- [x] FTS5 virtuelle sur `messages(content)` pour search
- [x] Méthodes : `save_session()`, `save_message()`, `save_nugget()`, `get_basket()`, `save_document()`
- [x] Singleton `storage = BRSStorage("exports/brs/brs_sessions.db")`

#### `mistral_client.py` — Client OpenAI-compatible
- [x] Hérite de `BaseClient`
- [x] `base_url = "https://openrouter.ai/api/v1"` (via OpenRouter free tier)
- [x] `model = "mistralai/mistral-nemo"`
- [x] Header `HTTP-Referer` + `X-Title` requis par OpenRouter
- [x] `MISTRAL_API_KEY` (= clé OpenRouter) depuis `.env`
- [x] Méthode `generate(prompt)` → streaming compatible avec `sse_generator()`

#### `brainstorm_logic.py` — Migration
- [x] Importer `BRSStorage` + `MistralClient`
- [x] Supprimer `SESSIONS` et `BASKETS` dicts → remplacer par appels `storage.*`
- [x] Dans `sse_generator()` : provider `"groq"` → `"mistral"` → `MistralClient()`
- [x] Après chaque token streamé : `storage.save_message(session_id, provider, "assistant", token)`
  *(Note : accumuler les tokens, sauvegarder en fin de stream pour éviter N writes)*
- [x] Dans `generate_prd_from_basket()` : après génération → `storage.save_document(session_id, "prd", path, content)`

### Critères de sortie
- Restart serveur → sessions/nuggets toujours présents
- 3 colonnes streament : Gemini + DeepSeek + Mistral Nemo
- `exports/brs/brs_sessions.db` existe avec les tables peuplées après une session
- `sqlite3 brs_sessions.db "SELECT * FROM messages LIMIT 5"` retourne des résultats

---

## Mission 45 — Éditeur Monaco HTML/CSS (FRD sub-phase)

**STATUS: ✅ COMPLÉTÉ (DONE BY CLAUDE)**
**DATE: 2026-03-14**
**ACTOR: GEMINI (frontend) + CLAUDE (routes backend)**
**MODE: CODE DIRECT — FJD**
**SCOPE:**
- `Frontend/3. STENCILER/static/templates/monaco_editor.html` *(nouveau)*
- `Frontend/3. STENCILER/server_9998_v2.py` *(ajout 3 routes < 10L chacune)*

### Contexte

Sous-phase FRD entre génération HTML (Mission 44) et handoff BKD.
Permet à FJD de corriger le layout/typo HTML généré par Gemini avant de le valider.
Retenu sur Monaco : même moteur VS Code — cohérence future phase BKD.

### Architecture

```
┌────────────────────────────────────────────────────────┐
│  ÉDITEUR MONACO (50%)     │  PREVIEW iframe (50%)      │
│  ┌──────────────────────┐ │  ┌──────────────────────┐  │
│  │ [HTML] [CSS]  [LOAD] │ │  │                      │  │
│  │                      │ │  │   srcdoc live        │  │
│  │  Monaco Editor       │ │  │   preview            │  │
│  │                      │ │  │                      │  │
│  │              [SAVE]  │ │  └──────────────────────┘  │
│  └──────────────────────┘ │                            │
└────────────────────────────────────────────────────────┘
```

**Comportement preview :**
- Tab CSS actif → modification : injecter dans `iframe.contentDocument.querySelector('#monaco-injected-style').textContent` — **sans rechargement**
- Tab HTML actif → modification : rebuild `iframe.srcdoc` complet
- Debounce 300ms sur les deux

**Monaco via CDN :**
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs/loader.min.js"></script>
```
Deux éditeurs instanciés (`html`, `css`), switchés par tabs.

**État interne :**
```js
let htmlContent = '';  // contenu HTML chargé
let cssContent  = '';  // CSS extrait du <style> du fichier HTML
```
Quand un fichier est chargé :
1. Parser `<style>...</style>` → `cssContent` (tab CSS)
2. Tout le reste → `htmlContent` (tab HTML)
Quand SAVE : recombiner `htmlContent` (avec `cssContent` injecté dans `<style>`) → POST

### Tâches

#### Backend — `server_9998_v2.py`

- [ ] Route `GET /monaco` → `templates/monaco_editor.html`
- [ ] Route `GET /api/frd/file?name=<filename>` → lit `static/templates/<filename>`, retourne `{ name, content }`
- [ ] Route `POST /api/frd/file` → reçoit `{ name, content }`, écrit `static/templates/<name>`

#### Frontend — `monaco_editor.html`

- [ ] Layout split 50/50 (flexbox, height 100vh)
- [ ] Header : titre "FRD Monaco Editor" + tabs `[HTML] [CSS]` + boutons `[LOAD] [SAVE]`
- [ ] Monaco instancié en `html` (tab HTML) et `css` (tab CSS), switch sans rechargement Monaco
- [ ] Au LOAD : `GET /api/frd/file?name=brainstorm_war_room.html` par défaut (nom modifiable)
- [ ] Preview iframe srcdoc — CSS-only injection sans rechargement
- [ ] Debounce 300ms : `let timer; clearTimeout(timer); timer = setTimeout(updatePreview, 300)`
- [ ] Bouton SAVE → `POST /api/frd/file` → feedback toast "Sauvegardé ✓"
- [ ] Style : fond blanc, séparateur central 1px #333, header 48px, police Geist 12px

### Critères de sortie
- `/monaco` accessible dans le navigateur
- LOAD charge `brainstorm_war_room.html` dans les deux éditeurs
- Modifier le CSS met à jour le preview sans rechargement iframe
- Modifier le HTML recharge le preview avec le nouveau srcdoc
- SAVE écrit le fichier sur disque, `Cmd+Shift+R` sur `/brainstorm` reflète les changements

---

## Mission 47 — Sullivan Arbitre + Search FTS5

**STATUS: ✅ COMPLÉTÉ (DONE BY ANTIGRAVITY + CLAUDE hotfixes)**
**DATE: 2026-03-14**
**ACTOR: CLAUDE**
**MODE: aetherflow -f**
**SCOPE:**
- `Backend/Prod/retro_genome/brainstorm_logic.py` *(arbitrage Sullivan)*
- `Backend/Prod/routes/brainstorm_routes.py` *(routes search + arbitrage)*
- `Backend/Prod/retro_genome/brs_storage.py` *(méthode search FTS5)*
- `Frontend/3. STENCILER/static/templates/brainstorm_war_room.html` *(UI search + Sullivan trigger)*

### Tâches

#### Sullivan — Arbitre (voix propre)

**System prompt Sullivan :**
```
Tu es Sullivan, arbitre éditorial d'une session de brainstorming multi-modèles HomeOS.
Tu reçois les sorties de 3 cerveaux distincts :
- Gemini (Scribe) : RAG, mémoire, synthèse large
- DeepSeek (Architecte) : rigueur technique, structure
- Mistral (Éditorial) : style, langue, angle créatif

Ton rôle d'arbitre :
1. Identifier les tensions et convergences entre les 3 points de vue
2. Signaler les topics qui méritent d'être approfondis (ex : "→ DeepSeek soulève X, à creuser")
3. Proposer une synthèse en 3-5 points actionnables
4. Articuler avec les sessions passées si pertinent (fournies en contexte)
5. Ne pas réécrire ce qui a été dit — pointer, contraster, articuler

Style : français direct, sans effusions, synthétique. Pas de liste à puces génériques.
```

- [ ] `brainstorm_logic.py` : nouvelle fonction `arbitrate_session(session_id)`
  - Récupère les 3 streams complets depuis `storage.get_messages(session_id)`
  - Récupère les nuggets du basket comme contexte secondaire
  - Génère avec `GeminiClient(execution_mode="BUILD")` + system prompt Sullivan
  - Sauvegarde dans `storage.save_message(session_id, "sullivan", "assistant", content)`
  - Retourne en streaming SSE (même pattern que `sse_generator`)

- [ ] `brainstorm_routes.py` : `GET /api/brs/arbitrate/{session_id}` → SSE StreamingResponse

#### Search FTS5

- [ ] `brs_storage.py` : méthode `search(query: str, user_id: str = None)`
  - `SELECT snippet(messages_fts, ...) FROM messages_fts WHERE content MATCH ?`
  - Retourne `[{ session_id, provider, excerpt, created_at, score }]`
  - `user_id` filter si fourni

- [ ] `brainstorm_routes.py` : `GET /api/brs/search?q={query}` → JSON

#### Frontend — Search UI + Sullivan trigger

- [ ] Search input dans sidebar gauche (déjà présent dans le HTML) câblé sur `GET /api/brs/search?q=`
- [ ] Résultats affichés sous la colonne du provider concerné (badge "SESSION #X")
- [ ] Bouton **Sullivan** dans le panel Sullivan → déclenche `GET /api/brs/arbitrate/{session_id}`
- [ ] Stream arbitrage → `#nugget-list` (zone Sullivan) avec style distinct (italic, couleur accent mauve)

### Critères de sortie
- Recherche "mobile-first" → résultats apparaissent sous Gemini/DeepSeek/Mistral selon qui l'a mentionné
- Bouton Sullivan → synthèse arbitrée streame dans le panel droit
- Sullivan cite explicitement les tensions entre les 3 cerveaux
- Résultats search incluent session_id + provider + extrait surligné

---

## Mission 48 — EXPÉRIMENTATION Tailwind : Figma JSON → HTML Tailwind

**STATUS: ✅ COMPLÉTÉ (DONE BY GEMINI)**
**DATE: 2026-03-16**
**ACTOR: GEMINI**
**MODE: CODE DIRECT — FJD**
**SCOPE:** `Frontend/3. STENCILER/static/templates/brainstorm_war_room_tw.html`

### Contexte

Mission 44 (CSS custom) a échoué 3 fois sur les placements grid. Hypothèse : Tailwind arbitrary values `w-[Xpx]` / `grid-cols-[...]` traduisent mécaniquement les coords Figma sans que Gemini ait à inférer quoi que ce soit.

Ce fichier est un **test isolé**. Si FJD valide le layout visuellement, Tailwind devient le standard du pipeline FRD et remplace l'approche CSS custom de Mission 44.

**Artifacts disponibles (inchangés depuis Mission 44) :**
- Spec JSON : `Frontend/4. COMMUNICATION/plans/figma_homeos1_spec.json`
- Render image : `Frontend/4. COMMUNICATION/plans/figma_homeos1_render.png`
- Source à préserver (JS) : `Frontend/3. STENCILER/static/templates/brainstorm_war_room.html`

---

### BOOTSTRAP GEMINI

```
Tu es Gemini, agent frontend AetherFlow. Tu génères du HTML pixel-fidèle avec Tailwind CSS.
Tu lis :
- figma_homeos1_render.png — VÉRITÉ VISUELLE (1285×868px, référence absolue)
- figma_homeos1_spec.json — coordonnées exactes extraites de l'API Figma REST
- brainstorm_war_room.html — source dont tu dois préserver le <script> intégralement
```

### SYSTEM PROMPT

```
CONTRAINTE ABSOLUE N°1 — TAILWIND UNIQUEMENT :
Pas de <style> custom. Tout le CSS passe par des classes Tailwind.
Exception tolérée : une seule balise <style> pour les variables CSS de couleur Figma
(--figma-bg, --figma-text, etc.) et pour `scrollbar-width: none` si nécessaire.

CONTRAINTE ABSOLUE N°2 — TRADUCTION MÉCANIQUE DES COORDS :
Chaque zone du JSON Figma se traduit directement en Tailwind arbitrary values.
Règle : largeur Figma X → `w-[Xpx]`, hauteur Y → `h-[Ypx]`, etc.
Ne jamais arrondir ou estimer — utiliser les valeurs exactes du JSON.

CONTRAINTE ABSOLUE N°3 — PLAY CDN :
Ajouter dans <head> :
<script src="https://cdn.tailwindcss.com"></script>

CONTRAINTE ABSOLUE N°4 — JS INTACT :
Le bloc <script> existant est copié mot pour mot.
IDs intouchables : #stream-gemini, #stream-deepseek, #stream-groq,
#nugget-list, #btn-prd, #btn-dispatch, #prompt-input, #session-info,
#prd-modal, #prd-content, #prd-download, #search-input, #btn-arbitrate

═══════════════════════════════════
PHASE 0 — LECTURE DU JSON (obligatoire avant tout code)
═══════════════════════════════════

1. Lis figma_homeos1_spec.json. Extrais les 5 zones de premier niveau :
   - leur x, y, width, height absolus
   - leur couleur de fond (fills[0].color)

2. Construis le grid principal :
   Cadre total : 2570×1736px
   → grid-cols-[554px_504px_504px_504px_504px]
   Vérifier que sum = 2570 (554+504×4 = 554+2016 = 2570 ✓)
   → Les 2 lignes : row 1 = tabs (h=64px), row 2 = contenu (h=1672px)
   → Sullivan panel : span rows 1/-1 (pleine hauteur)

3. Pour chaque zone, note les sous-composants critiques avec leurs coords relatives :
   - Provider icons (y relatif, h, w)
   - Labels "AUJOURD'HUI" (fontFamily, fontSize exact, color)
   - Input bars (h, y, bg)
   - Sullivan header (h)

═══════════════════════════════════
PHASE 1 — GÉNÉRATION HTML+TAILWIND
═══════════════════════════════════

SHELL OBLIGATOIRE :
```html
<div class="flex flex-col h-screen overflow-hidden bg-white">
  <!-- tabs row -->
  <div class="grid grid-cols-[554px_504px_504px_504px_504px] h-[64px] border-b border-[#333]">
    ...
  </div>
  <!-- main content -->
  <div class="grid grid-cols-[554px_504px_504px_504px_504px] flex-1 overflow-hidden">
    <!-- sidebar -->         col 1 : w-[554px] h-full
    <!-- col gemini -->      col 2 : w-[504px] flex flex-col border-l border-[#333]
    <!-- col deepseek -->    col 3 : w-[504px] flex flex-col border-l border-[#333]
    <!-- col mistral -->     col 4 : w-[504px] flex flex-col border-l border-[#333]
    <!-- sullivan panel -->  col 5 : w-[504px] flex flex-col border-l border-[#333] bg-[#f9f9f9]
  </div>
</div>
```

TYPOGRAPHIE (arbitrary values obligatoires) :
- Logo "HoméOS" : `font-['Inter'] text-[40px] font-[400] text-[#000]`
- Nav tabs : `font-[system-ui] text-[20px] text-[#000]` → active : `text-[#8cc63f]`
- Labels "AUJOURD'HUI" : `font-['Inter'] text-[15.76px] text-[#666]`
- Chat messages : `font-['Geist'] text-[16px] text-[#666]`
- Sullivan titre : `font-['Geist'] text-[20px] text-[#666]`

COULEURS (classes Tailwind arbitrary) :
- Fond page : `bg-[#ffffff]`
- Panel Sullivan : `bg-[#f9f9f9]`
- Input bg : `bg-[#f2f3f5]`
- Séparateurs : `border-[#333]` épaisseur `border-[0.5px]`
- Onglet actif : `text-[#8cc63f]`
- Dot vert Sullivan : `bg-[#5ec069]`
- Bouton send : `bg-[#999]`

COLONNES AI — pattern × 3 (gemini, deepseek, mistral) :
```html
<section class="w-[504px] flex flex-col border-l border-[#333] overflow-hidden">
  <div class="h-[42px] flex items-center px-3"><!-- provider badge --></div>
  <div class="text-[15.76px] font-['Inter'] text-[#666] px-3 py-2">AUJOURD'HUI</div>
  <div class="flex-1 overflow-y-auto px-3" id="stream-{provider}"></div>
  <div class="h-[94px] border-t border-[#333] flex items-center gap-2 px-3 bg-[#f2f3f5]">
    <input class="flex-1 bg-transparent text-[14px] font-['Geist'] text-[#666] outline-none" placeholder="...">
    <button class="w-[44px] h-[44px] flex items-center justify-center text-[#666]">+</button>
    <button class="w-[63px] h-[56px] bg-[#999] text-white text-xs">→</button>
  </div>
</section>
```

SULLIVAN PANEL :
```html
<section class="w-[504px] flex flex-col border-l border-[#333] bg-[#f9f9f9]">
  <div class="h-[101px] bg-white border-b border-[#333] flex items-center gap-3 px-4">
    <span class="w-2 h-2 rounded-full bg-[#5ec069]"></span>
    <span class="font-['Geist'] text-[20px] text-[#666]">Sullivan</span>
  </div>
  <div class="flex-1 overflow-y-auto p-4" id="nugget-list"></div>
  <div class="p-4 bg-white border-t border-[#333] flex flex-col gap-2">
    <button id="btn-arbitrate" class="w-full h-10 border border-[#333] text-[12px] font-['Geist']">
      SULLIVAN ARBITRAGE
    </button>
    <button id="btn-prd" disabled class="w-full h-10 bg-[#8cc63f] text-white text-[12px] font-['Geist'] disabled:bg-[#ccc]">
      GÉNÉRER PRD
    </button>
  </div>
</section>
```

═══════════════════════════════════
PHASE 2 — VALIDATION VISUELLE
═══════════════════════════════════

Comparer le rendu à figma_homeos1_render.png :
[ ] 5 colonnes visibles avec séparateurs 0.5px #333
[ ] Row tabs sur toute la largeur, h=64px
[ ] Sidebar "HoméOS" Inter 40px à gauche
[ ] Sullivan pleine hauteur (pas tronqué par les tabs)
[ ] 3 colonnes AI avec input bar en bas h=94px
[ ] Fond blanc global, fond #f9f9f9 Sullivan uniquement

Critère de blocage : si une zone déborde ou disparaît → corriger les classes grid avant de soumettre.
```

**OUTPUT :** `Frontend/3. STENCILER/static/templates/brainstorm_war_room_tw.html`

*(Route à ajouter manuellement dans server_9998_v2.py : `GET /brainstorm-tw` → ce fichier)*

### Critères de validation FJD
- [ ] `/brainstorm-tw` accessible et chargeable
- [ ] Fond blanc visible immédiatement (pas de fond sombre)
- [ ] 5 colonnes avec séparateurs nets
- [ ] Logo "HoméOS" Inter 40px en sidebar
- [ ] Layout visuellement proche de `figma_homeos1_render.png`
- [ ] JS dispatch/stream fonctionnel (test end-to-end)

### Décision post-test
- **Layout OK** → Tailwind devient standard FRD. Mission 44 archivée, pipeline mis à jour.
- **Layout KO** → fermer la piste Tailwind. Explorer une approche code-first sans LLM pour le layout (cf. discussion stratégique).

---

## Mission 49 — FRD Editor : Monaco + Preview + Sullivan Chat (Gemini 3.1 Flash-Lite)

**STATUS: ✅ COMPLÉTÉ**
**DATE: 2026-03-16**
**ACTOR: GEMINI + FJD**
**MODE: CO-PILOT — FJD**
**SCOPE:**
- `Frontend/3. STENCILER/static/templates/frd_editor.html`
- `Frontend/3. STENCILER/server_9998_v2.py` (Routes: `/frd-editor`, `/api/frd/chat`, `/api/frd/save`)

### Objectif

Éditeur FRD tout-en-un : Monaco (escamotable) + Preview + Sullivan chatbot (Gemini Flash).
Le dev dicte les modifications en langage naturel → Gemini applique → Monaco + preview se mettent à jour.
Destiné à remplacer la boucle Antigravity → copier-coller → vérifier.
À terme : intégrer dans l'interface HomeOS.

### Architecture

```
┌──────────────────────────────────────────────────────────────┐
│ [≡] frd_editor.html   [HTML][CSS]  [LOAD] [SAVE]  [◀ Sullivan]│
├────────────┬─────────────────────────┬───────────────────────┤
│ Monaco     │  Preview iframe         │  Sullivan Chat        │
│ ESCAMOTABLE│  flex-1                 │  320px fixe           │
│ 340px      │  s'étend quand Monaco   │  Gemini Flash         │
│            │  caché (width:0)        │  bulles chat          │
│ [HTML][CSS]│                         │  ─────────────────    │
│  < code >  │                         │  [input]  [→]         │
└────────────┴─────────────────────────┴───────────────────────┘
     ↑ toggle [≡] : width 340px ↔ 0, overflow hidden, transition 200ms
```

**MONACO ESCAMOTABLE — comportement précis :**
- Panneau Monaco : `width: 340px; overflow: hidden; transition: width 200ms ease`
- Bouton `[≡]` dans le header toggle : `monacoPane.style.width = collapsed ? '340px' : '0'`
- Quand width = 0 : le preview (`flex: 1`) prend toute la place disponible
- Quand width = 340px : preview rétrécit, Monaco visible
- `editorHTML.layout()` appelé après la transition pour que Monaco se redimensionne correctement

### Backend — `POST /api/frd/chat`

Appel sync urllib (pas d'async) à `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent`.

Body reçu : `{ message, html }`
Réponse : `{ explanation, html }` (parsé sur `---HTML---`)

**System prompt Sullivan éditeur :**
```
Tu es Sullivan, assistant de modification d'interface HomeOS.
Tu modifies des fichiers HTML Tailwind CSS selon les instructions du développeur.
Tu réponds TOUJOURS dans ce format exact :
[explication courte en français, 1-2 phrases max]
---HTML---
[fichier HTML complet modifié, rien d'autre]
Règles : ne jamais modifier le <script> • préserver tous les IDs • Tailwind arbitrary values
```

### Livrables & Correction (Post-implémentation)
- **Éditeur Monaco** : Intégré avec toggle `[≡]` escamotable (transition 200ms).
- **IA Sullivan** : Mise à jour vers **Gemini 3.1 Flash-Lite Preview** (via `GOOGLE_API_KEY`).
- **Synchronisation** : `iframe.srcdoc` utilisé pour un rendu instantané du code Monaco.
- **Persistence** : Route `/api/frd/save` fonctionnelle pour écraser les templates existants.
- **Structure Tailwind (Mission 48 Refactor)** : Sidebar 330px full-height, Sullivan panel sous le header, grid AI 3 colonnes avec footer de résultats sémantiques.

---

## Mission 50 — FRD Editor UX : Loader Sullivan + Monaco Resizable + Inspect

**STATUS: ✅ COMPLÉTÉ**
**DATE: 2026-03-16**
**ACTOR: GEMINI**
**MODE: CODE DIRECT — FJD**
**SCOPE:**
- `Frontend/3. STENCILER/static/templates/frd_editor.html`

### Contexte

Suite de Mission 49 (FRD Editor opérationnel). L'API Sullivan fonctionne. Le save est réparé côté serveur (`cwd` hotfix appliqué par Claude). Il reste 3 UX manquantes.

### Tâches

#### 1. Loader Sullivan (overlay pendant traitement IA)
Quand `sendChat()` est appelé :
- Afficher un **overlay semi-transparent** (`position: fixed`, `z-index: 50`, `background: rgba(0,0,0,0.35)`) par-dessus toute l'UI.
- L'overlay contient un spinner minimaliste + texte `Sullivan travaille...` centré, style HomeOS (fond blanc, Geist, couleur `#8cc63f`).
- Simultanément : ajouter une bubble `sullivan-bubble` dans le chat-history avec le message `Sullivan analyse votre demande...` (bubble "pending").
- Quand la réponse arrive : masquer l'overlay, remplacer la bubble pending par la vraie réponse, mettre à jour Monaco.

#### 2. Monaco Pane Resizable (drag handle)
Remplacer la largeur fixe `340px` par un panneau redimensionnable :
- Ajouter un **resize handle** entre `#monaco-pane` et `#preview-pane` : div verticale `4px`, `cursor: col-resize`, `background: #333`, hover `background: #8cc63f`.
- Drag : mousedown sur le handle → mousemove calcule `newWidth = event.clientX`, `clamp(180px, 50vw)` → `monacoPane.style.width = newWidth + 'px'` → `editorHTML.layout()` en continu.
- mouseup / mouseleave document → stopper le drag.
- Le toggle `[≡]` continue de fonctionner (mémorise la dernière largeur avant collapse).

#### 3. Monaco → Preview : Highlight de la sélection
Quand l'utilisateur sélectionne du texte dans Monaco :
- Écouter `editorHTML.onDidChangeCursorSelection`.
- Identifier l'éventuel `id=""` dans le texte sélectionné (regex : `id="([^"]+)"`).
- Injecter un `postMessage` dans l'iframe preview avec `{ type: 'highlight', selector: '#found-id' }`.
- Dans le `srcdoc` du preview (via script injecté dans `updatePreview()`), écouter `window.addEventListener('message', ...)` et toggle `outline: 2px solid #8cc63f` sur l'élément ciblé.
- Si aucun id détecté : ne rien faire.

### Style & Contraintes
- Police Geist, couleurs HomeOS : fond `#ffffff`, accent `#8cc63f`, séparateurs `#333333`
- Spinner : animation CSS pure (rotation `border-t transparent`), pas de lib externe
- Conserver tous les IDs existants et le comportement Load / Save / Toggle

### Bootstrap Gemini
Fournir le fichier complet `frd_editor.html` en input.

### Livrables Mission 50
- **Sullivan Loader** : Overlay semi-transparent `Sullivan travaille...` + bubble "pending" synchronisée avec la réponse finale.
- **Resizable Monaco** : Drag handle vertical entre Monaco et Preview (min 180px, max 50vw) avec rafraîchissement `editor.layout()`.
- **Toggle Memory** : Le bouton `[≡]` mémorise la largeur personnalisée avant de s'effondrer.
- **Smart Highlighting** : La sélection d'un `id=""` dans Monaco déclenche un message vers l'iframe pour entourer l'élément cible d'un outline vert (`#8cc63f`) et le centrer dans la vue.

---

## Mission 51 — FRD Editor : Asset Upload (Drag & Drop → Sullivan Context)

**STATUS: 🔴 À FAIRE**
**DATE: 2026-03-16**
**ACTOR: GEMINI (frontend) + CLAUDE (backend routes)**
**MODE: CODE DIRECT — FJD**
**SCOPE:**
- `Frontend/3. STENCILER/static/templates/frd_editor.html` *(modifier)*
- `Frontend/3. STENCILER/server_9998_v2.py` *(2 routes nouvelles)*

### Contexte

Sullivan peut modifier du HTML/Tailwind mais n'a aucun moyen de référencer des images réelles.
L'objectif : drag & drop d'un fichier image sur la chatbox → upload → URL disponible pour Sullivan → Sullivan peut écrire `<img src="/assets/frd/logo.png">` dans le HTML généré.

### Architecture

```
FRD Editor — Sullivan Pane
├── Zone Assets (au-dessus de la chatbox)
│   ├── Titre "ASSETS" (style header Sullivan, uppercase, tracking)
│   ├── Zone de drop (dashed border #333, bg #f9f9f9, h=80px, texte "Glisser une image ici")
│   │   → dragover : highlight vert #8cc63f
│   │   → drop : upload + thumbnail
│   └── Liste thumbnails : img 40×40px + nom + bouton [×] supprimer
│
Backend
├── POST /api/frd/upload   → multipart, sauvegarde dans static/assets/frd/
│                          → retourne { url: "/assets/frd/<filename>" }
├── GET  /api/frd/assets   → liste les fichiers dans static/assets/frd/
│                          → retourne { assets: [{ name, url }] }
└── static /assets/frd/*  → servir les fichiers (via route GET existante ou nouvelle)

Sullivan chat
└── sendChat() injecte dans le body :
    { message, html, assets: ["/assets/frd/logo.png", ...] }
    → /api/frd/chat transmet assets dans le system prompt Sullivan :
      "Images disponibles pour les <img> : {assets_list}"
```

### Tâches

#### Backend — `server_9998_v2.py`

**Route 1 : `POST /api/frd/upload`**
- Lire `Content-Type: multipart/form-data`
- Parser via `cgi.FieldStorage` ou `email.parser` (stdlib Python uniquement, pas de dépendance)
- Créer `static/assets/frd/` si absent (`os.makedirs(..., exist_ok=True)`)
- Sécurité : whitelist extensions `['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']`
- Sauvegarder sous `static/assets/frd/<filename_sanitisé>`
- Retourner `{ "url": "/assets/frd/<filename>" }`

**Route 2 : `GET /api/frd/assets`**
- Lister les fichiers dans `static/assets/frd/`
- Retourner `{ "assets": [{ "name": "logo.png", "url": "/assets/frd/logo.png" }, ...] }`

**Route 3 : `GET /assets/frd/<filename>`** (si pas déjà couverte par le static handler)
- Servir le fichier avec le bon Content-Type (utiliser `mimetypes.guess_type`)

**Route `/api/frd/chat` — mise à jour**
- Extraire `assets` depuis le body JSON (liste d'URLs, peut être vide/absent)
- Si `assets` non vide : injecter dans le system prompt Sullivan avant le message :
  ```
  Images disponibles (utilise ces URLs dans les balises <img src="..."> si pertinent) :
  {chr(10).join(assets)}
  ```

#### Frontend — `frd_editor.html`

**Zone Assets dans `#sullivan-pane`** (insérer entre le header "Chatbot Sullivan" et `#chat-history`) :

```html
<div id="assets-zone" class="border-b-[0.5px] border-figma-sep bg-white">
  <div class="px-4 py-2 text-[9px] font-bold uppercase tracking-widest text-figma-text">Assets</div>
  <div id="drop-zone" class="mx-4 mb-3 h-[60px] border border-dashed border-[#333]
       flex items-center justify-center text-[10px] text-figma-text cursor-pointer
       transition-colors">
    Glisser une image ici
  </div>
  <div id="asset-thumbnails" class="px-4 pb-3 flex flex-wrap gap-2"></div>
</div>
```

**JS — Drag & Drop :**
```js
const dropZone = document.getElementById('drop-zone');
let uploadedAssets = [];

// Charger la liste existante au démarrage
async function loadAssets() {
  const res = await fetch('/api/frd/assets');
  if (res.ok) {
    const data = await res.json();
    uploadedAssets = data.assets.map(a => a.url);
    data.assets.forEach(a => addThumbnail(a.name, a.url));
  }
}

dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.style.borderColor = '#8cc63f';
  dropZone.style.background = '#f0fae0';
});
dropZone.addEventListener('dragleave', () => {
  dropZone.style.borderColor = '#333';
  dropZone.style.background = '';
});
dropZone.addEventListener('drop', async (e) => {
  e.preventDefault();
  dropZone.style.borderColor = '#333';
  dropZone.style.background = '';
  const files = e.dataTransfer.files;
  for (const file of files) {
    const fd = new FormData();
    fd.append('file', file);
    const res = await fetch('/api/frd/upload', { method: 'POST', body: fd });
    if (res.ok) {
      const data = await res.json();
      uploadedAssets.push(data.url);
      addThumbnail(file.name, data.url);
    }
  }
});

function addThumbnail(name, url) {
  const container = document.getElementById('asset-thumbnails');
  const wrap = document.createElement('div');
  wrap.className = 'relative group';
  wrap.innerHTML = `
    <img src="${url}" title="${name}"
         class="w-10 h-10 object-cover border border-[#333] cursor-pointer"
         onclick="navigator.clipboard.writeText('${url}')">
    <span class="absolute -top-1 -right-1 hidden group-hover:flex w-4 h-4
                 bg-[#333] text-white text-[8px] items-center justify-center
                 cursor-pointer rounded-full"
          onclick="removeAsset('${url}', this.parentElement)">×</span>
  `;
  container.appendChild(wrap);
}

function removeAsset(url, el) {
  uploadedAssets = uploadedAssets.filter(u => u !== url);
  el.remove();
}
```

**JS — Mise à jour `sendChat()` :**
Ajouter `assets: uploadedAssets` dans le body de `/api/frd/chat` :
```js
body: JSON.stringify({ message, html: editorHTML.getValue(), assets: uploadedAssets })
```

**Comportement click sur thumbnail :** copie l'URL dans le clipboard (feedback optionnel : flash vert 200ms).

### Style & Contraintes
- Police Geist, couleurs HomeOS : fond `#ffffff`, accent `#8cc63f`, séparateurs `#333`
- Pas de lib externe (FormData natif, pas de axios)
- Parser multipart côté Python : `cgi.FieldStorage` (stdlib, dépréciée Python 3.11+ mais fonctionnelle) ou implémentation manuelle des boundaries
- Extensions autorisées uniquement : `.png .jpg .jpeg .gif .svg .webp`
- Noms de fichiers sanitisés : `os.path.basename` + strip caractères non-alphanumériques

### Bootstrap Gemini
Fournir `frd_editor.html` complet en input. Gemini implémente la partie frontend uniquement.
Claude implémente les routes backend dans `server_9998_v2.py`.

### Critères de sortie
- [ ] Drag d'un PNG sur la drop zone → thumbnail apparaît dans le panel Assets
- [ ] Click thumbnail → URL copiée dans le clipboard
- [ ] Sullivan reçoit la liste d'assets dans son contexte → "place le logo en haut à gauche" → Monaco contient `<img src="/assets/frd/logo.png">`
- [ ] Preview iframe charge l'image (même serveur, URL relative)
- [ ] Restart serveur → assets toujours là (fichiers sur disque)

---

## BACKLOG

- [ ] **MISSION 41B** : SVG BACKPLANE GENERATOR — `svg_backplane.py` : manifest enrichi → SVG annoté af-metadata, exportable Figma
- [ ] **MISSION 41C** : ROUTINE SVG ILLUSTRATOR — `_parse_illustrator_svg()` dans `svg_parser.py`.
  Stratégie "extract-first, Vision-last" : extraire mécaniquement `fill`/`stroke`/`rect`/`<g>`, Vision uniquement pour labelliser `name`/`inferred_intent`/`apparent_role`. Vision ne remplace jamais les valeurs déjà extraites. Déclenchement Vision : `source == 'illustrator'` ET `len(regions) < 2`.
- [ ] **MISSION 42** : MIGRATION FASTAPI — Remplacer `server_9998_v2.py` (~1200L, ~40 routes) par FastAPI/Uvicorn pour déployabilité (Railway, Docker). `retro_genome/routes.py` déjà en FastAPI → `app.include_router()`. Mission lourde — découper par domaine (genome, retro-genome, statics, exports).
- [ ] **MISSION 27** : CHATBOT PÉDAGOGIQUE (GEMINI API)
- [ ] **MISSION 26** : RAG ENGINE SYSTEM
- [ ] **MISSION 29** : CONTRÔLEUR HOMEOS NATIVE (EMBED FIGMA + GUI RETRO-GENOME)
