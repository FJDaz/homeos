# ROADMAP_ACHIEVED — Archive March 2026

### 70-C — MANIFEST_FRD Injection
- [x] `_load_manifest_frd()` au démarrage serveur → `_MANIFEST_FRD` constante module
- [x] Injecté dans `system_instruction` Sullivan à chaque appel construct
- [x] Sullivan connaît la vision S-T-A-R, les phases BRS/BKD/FRD/DPL, les rôles

---

## Mission 71 — Sullivan Tool Use : read_reference()
**STATUS: ✅ LIVRÉ**
**ACTOR: MIMO (plan) + CLAUDE (corrections spec Gemini)**
**DATE: 2026-03-23**
**FICHIERS :** `server_9998_v2.py`
- [x] `REFERENCE_WHITELIST` dict (manifest_frd, sullivan_interactions, api_contract, constitution, lexicon_design)
- [x] `_exec_read_reference(path_or_key)` — sécurité path traversal, lecture max 8000 chars
- [x] `tools: [{functionDeclarations: [...]}]` injecté dans payload Gemini (mode construct uniquement)
- [x] Boucle tool calling max 4 itérations — détecte `functionCall`, exécute, renvoie `functionResponse`
- [x] Log `[TOOL USE] read_reference('...')` dans les logs serveur
- [x] Format corrigé : `tools` = liste (pas dict), `role: "user"` pour functionResponse (spec Gemini)
- [x] MiMo note : 6.5/10 — structure correcte, bugs de spec API mineurs

---

## Mission 72 — FRD Editor : Qualité de vie (templates + save-as)
**STATUS: ✅ LIVRÉ**
**ACTOR: CLAUDE (CODE DIRECT)**
**DATE: 2026-03-23**
**FICHIERS :** `frd_editor.html`, `server_9998_v2.py`
- [x] Route `GET /api/frd/files` → liste tous les `.html` du dossier templates (triés alphabétiquement)
- [x] Select templates peuplé dynamiquement au chargement (zéro hardcode)
- [x] Champ texte `save-name` à gauche du bouton Save — permet renommer avant sauvegarde
- [x] Save : utilise `save-name` en priorité, fallback sur select
- [x] Load : utilise `save-name` en priorité, fallback sur select
- [x] Après Save avec nom custom : option ajoutée au select + select positionné dessus
- [x] Load pré-remplit le champ `save-name` avec le nom du fichier chargé
- [x] Force-save : 422 DOM manifest → dialog confirm → re-POST avec `force: true`

---

## Mission 73 — Sullivan Router : route text-only + Gemini conversationnel
**STATUS: ✅ LIVRÉ**
**ACTOR: CLAUDE (CODE DIRECT)**
**DATE: 2026-03-23**
**FICHIERS :** `server_9998_v2.py`
- [x] Groq router : ajout type `"text-only"` avec règles de détection explicites (question, analyse, rapport, lecture, conversation, "procède", "as-tu chargé", etc.)
- [x] Champ `"response"` dans le JSON Groq pour les réponses text-only
- [x] Handler text-only : Gemini appelé en mode texte pur (manifest + history en contexte, sans tools, sans HTML)
- [x] Gemini répond en markdown — Sullivan sait ce que contient le manifest, peut répondre aux questions projet
- [x] Groq = routing uniquement, Gemini = intelligence conversationnelle + génération code
- [x] Log `[MISSION 64] Route: text-only` visible dans les logs serveur

---

## Mission 74 — Sullivan : "Procède" → exécution du plan discuté
**STATUS: ✅ LIVRÉ**
**ACTOR: CLAUDE (CODE DIRECT)**
**DATE: 2026-03-24**
**FICHIERS :** `server_9998_v2.py`
- [x] `_route_request(message, html_context, history=None)` — history passé depuis `/api/frd/chat`
- [x] `last_model_turn` extrait de `history` (dernier tour `role: model`)
- [x] Groq system prompt : règle explicite "execution command + dernier tour contient plan → html-only/both"
- [x] "procède au plan" retiré des exemples text-only
- [x] Block `DERNIER TOUR SULLIVAN : {last_model_turn[:1000]}` injecté dans le message Groq
- [x] Quand exec command détecté + last_model_turn non vide → `message = f"SPEC À IMPLÉMENTER:\n{last_model_turn[:3000]}"`
- [x] Gemini reçoit la spec du plan dans le message, l'exécute sans se baser sur le html_context

---

## Mission 77 — Sullivan Knowledge Base : RAG AetherFlow
**STATUS: ✅ LIVRÉ**
**ACTOR: CLAUDE (CODE DIRECT)**
**DATE: 2026-03-24**
**FICHIERS :** `server_9998_v2.py`, `Backend/Prod/rag/pageindex_store.py`
- [x] Import PageIndexRetriever depuis `Backend.Prod.rag.pageindex_store` (sys.path.insert)
- [x] `_SULLIVAN_DOCS` : 02_Sullivan, 04_HomeOS, 03_AetherFlow, ROADMAP.md, ROADMAP_ACHIEVED.md
- [x] `_init_sullivan_rag()` : collecte récursive *.md + *.py, PageIndexRetriever avec persist_dir
- [x] `_SULLIVAN_RAG = _init_sullivan_rag()` au démarrage — index chargé une fois
- [x] `_exec_query_knowledge_base(query)` : asyncio.run(retrieve()), dict {content, file_name, score}
- [x] `query_knowledge_base` déclaré dans `functionDeclarations` Gemini
- [x] Handler dans boucle tool calling : elif fn_name == 'query_knowledge_base'
- [x] Log `[RAG] query='...' → N chars` visible dans les logs
- [x] 445 documents indexés — cache disk (rag_index/)
- [x] Serveur lancé via `.venv/bin/python3` (LlamaIndex uniquement dans venv)
- [x] **Correctifs appliqués** : suppression build_index() (auto-init), asyncio.run() pour retrieve() async, accesseurs dict {content, file_name} (pas NodeWithScore)

---

## Décision architecture BKD — 2026-03-23
**TYPE: Décision technique (non-mission)**
- BKD Forge UI = **code-server** (VS Code dans le browser, self-hosted Docker) — pas Monaco seul
- 1 extension VS Code custom `aetherflow-bkd` (TypeScript) pour Majordome + Roadmap panels
- Stack : `codercom/code-server:latest` + WebviewPanel API + fetch `/api/frd/chat`
- Ports : 8080 (code-server), 9998 (AetherFlow backend)
- Documenté dans `docs/02_Sullivan/Retro_Genome/MANIFEST_FRD.md` section Phase 2 BKD

---

## Mission 44 — Pipeline Figma REST → HTML Pixel-Fidèle (via Gemini)
**STATUS: ✅ LIVRÉ** *(via Mission 48 Tailwind — CSS custom path abandonné)*
**ACTOR: GEMINI**
**DATE: 2026-03-16**
- [x] Pipeline systématisable : Figma REST API → spec JSON → Gemini → HTML
- [x] Artifacts HomeOS 1 : `figma_homeos1_spec.json` (6025L) + `figma_homeos1_render.png`
- [x] 3 tentatives CSS custom échouées → pivot Tailwind arbitrary values (M48) validé FJD
- [x] Palette `--figma-*` documentée, mapping typo Figma→web établi (Inter/Geist/system-ui)
- [x] `brainstorm_war_room_tw.html` = implémentation validée (M48 ✅)

---

## Mission 52+53 — FRD Editor : Intégration KIMI Design Critic
**STATUS: ✅ LIVRÉ**
**ACTOR: GEMINI (M52 initial) + CLAUDE (M53 debug/stabilisation)**
**DATE: 2026-03-17**
- [x] Route `POST /api/frd/kimi` → NVIDIA NIM `moonshotai/kimi-k2.5`, timeout 300s
- [x] Script-stripping avant envoi (économie tokens ~50%)
- [x] Parsing réponse : label + HTML, tolérant aux variations de format KIMI
- [x] 1 seule proposition par appel (simplifié depuis 3 variantes)
- [x] XHR (bypass inject.js monkey-patch fetch) → `appendKimiBubble` DOM-only (addEventListener)
- [x] `applyKimiResult()` → `editorHTML.setValue()` + `updatePreview()`
- [x] Mode toggle CONSTRUCT/DESIGN + commandes `/design` et `/construct`
- [x] Bug assets `cwd` manquant → corrigé
- [x] Null-check sur KIMI content vide

---

## Mission 51 — FRD Editor : Asset Upload (Drag & Drop → Sullivan Context)
**STATUS: ✅ LIVRÉ**
**ACTOR: GEMINI (frontend) + CLAUDE (backend)**
**DATE: 2026-03-16**
- [x] Zone Assets dans Sullivan pane : drop-zone dashed, thumbnails 40×40, bouton [×] supprimer
- [x] Drag & drop → `POST /api/frd/upload` (multipart stdlib, extensions whitelistées)
- [x] `GET /api/frd/assets` → liste les fichiers `static/assets/frd/`
- [x] `sendChat()` injecte `assets: uploadedAssets` → system prompt Sullivan
- [x] `loadAssets()` au démarrage pour persister entre sessions

---

## Mission 50 — FRD Editor UX : Loader Sullivan + Monaco Resizable + Inspect
**STATUS: ✅ LIVRÉ**
**ACTOR: GEMINI**
**DATE: 2026-03-16**
- [x] Overlay `Sullivan travaille...` (position:fixed, z-index:9999, spinner CSS)
- [x] Drag handle 4px entre Monaco et Preview (clamp 180px→50vw, `editor.layout()` en continu)
- [x] Toggle `[≡]` mémorise la largeur avant collapse
- [x] `onDidChangeCursorSelection` → regex `id="..."` → `postMessage` → outline vert `#8cc63f` sur l'élément preview

---

## Mission 49 — FRD Editor : Monaco + Preview + Sullivan Chat
**STATUS: ✅ LIVRÉ**
**ACTOR: GEMINI + FJD**
**DATE: 2026-03-16**
- [x] Éditeur 3 panes : Monaco (resizable) | Preview iframe srcdoc | Sullivan chat 320px
- [x] Routes `/frd-editor`, `/api/frd/chat` (Gemini Flash-Lite), `/api/frd/save`
- [x] Hotfix `cwd` scope Python → `_cwd = os.path.dirname(os.path.abspath(__file__))`
- [x] Sullivan : system prompt + parse `---HTML---` → `{ explanation, html }`

---

## Mission 48 — EXPÉRIMENTATION Tailwind : Figma JSON → HTML Tailwind
**STATUS: ✅ LIVRÉ**
**ACTOR: GEMINI**
**DATE: 2026-03-16**
- [x] `brainstorm_war_room_tw.html` : layout Tailwind arbitrary values depuis coords Figma
- [x] Grid `grid-cols-[554px_504px_504px_504px_504px]`, palette `--figma-*` CSS vars
- [x] Tailwind validé comme standard FRD → remplace approche CSS custom Mission 44
- [x] Route `/brainstorm-tw` ajoutée dans `server_9998_v2.py`

---

## Mission 47 — Sullivan Arbitre + Search FTS5
**STATUS: ✅ LIVRÉ**
**ACTOR: CLAUDE + hotfixes**
**DATE: 2026-03-14**
- [x] `arbitrate_session()` dans `brainstorm_logic.py` → GeminiClient + system prompt arbitre
- [x] `GET /api/brs/arbitrate/{session_id}` → SSE StreamingResponse
- [x] `search(query)` FTS5 dans `brs_storage.py` → `snippet()` + score
- [x] `GET /api/brs/search?q=` → JSON + UI câblée dans `brainstorm_war_room.html`
- [x] Bouton Sullivan → stream arbitrage dans panel Sullivan, style italic accent mauve

---

## Mission 46 — BRS Persistance SQLite + MistralClient
**STATUS: ✅ LIVRÉ**
**ACTOR: CLAUDE**
**DATE: 2026-03-14**
- [x] `brs_storage.py` : BRSStorage SQLite (sessions, messages, nuggets, documents) + FTS5
- [x] `mistral_client.py` : OpenRouter free tier, `mistralai/mistral-nemo`
- [x] `brainstorm_logic.py` : migration in-memory → SQLite, provider groq → Mistral Nemo
- [x] Colonne 3 = Mistral (éditorial French-native) au lieu de Groq

---

## Mission 45 — Éditeur Monaco HTML/CSS (FRD sub-phase)
**STATUS: ✅ LIVRÉ**
**ACTOR: GEMINI + CLAUDE**
**DATE: 2026-03-14**
- [x] `monaco_editor.html` : split 50/50, tabs HTML/CSS, LOAD/SAVE
- [x] CSS-only injection sans rechargement iframe (injection dans `#monaco-injected-style`)
- [x] Routes `GET /monaco`, `GET /api/frd/file`, `POST /api/frd/file`
- [x] Debounce 300ms, toast "Sauvegardé ✓"

---

## Mission 39 — Intent Viewer : Stabilisation Analyse PNG
**STATUS: ✅ LIVRÉ**
**ACTOR: CLAUDE (CODE DIRECT) + GEMINI (Tâche C+D prompt)**
**DATE: 2026-03-13**
- [x] Tâche A : PNG natif lossless (`format="PNG"`, `mime_type="image/png"`), `MAX_DIMENSION=1280`, suppression JPEG/dégradation qualité.
- [x] Tâche B : `temperature=0` + retry ×3 avec `asyncio.sleep(1)` dans `analyze_png()`. Logger du numéro de tentative.
- [x] Tâche C+D (Gemini) : `color_hex` obligatoire, sidebar détection, `visual_hint` par élément, `coords` géométriques, `computed-intersection` + `parents` pour chevauchements.

---

## Mission 40 — SVG Backplane + Archetypal API Inference
**STATUS: ✅ LIVRÉ**
**ACTOR: CLAUDE (A+C CODE DIRECT) + GEMINI (B+D)**
**DATE: 2026-03-13**
- [x] Tâche A : `af_metadata_schema.json` — 9 attributs, 2 couches (fonctionnelle + géométrique). Schéma de référence pour le SVG Backplane.
- [x] Tâche B (Gemini) : `functional_archetypes.json` — 20 archétypes (ide_like, venn_diagram, sudoku_grid, weather_app...) avec `artifact_type`, `visual_triggers`, `required_components`, `suggested_endpoints`.
- [x] Tâche C : `archetype_detector.py` — matching déterministe keyword-scoring, génère `dev_brief` pédagogique, confidence < 0.5 → `unknown`. Tests : venn_diagram ✅ admin_dashboard ✅ unknown ✅.
- [x] Tâche D (Gemini) : `VISUAL_DECOMPOSER_PROMPT` enrichi — `visual_hint` obligatoire, `coords` géométriques (`row/col` ou `cx/cy/r`), `computed-intersection` + `parents` pour zones calculées.

---

## Mission 38 — Figma Bridge Plugin : Debug & Stabilisation
**STATUS: ✅ LIVRÉ**
**ACTOR: CLAUDE (CODE DIRECT)**
**DATE: 2026-03-13**
- [x] Fix crash au démarrage : `"allowedDomains": ["none"]` était valide mais `optional chaining ?.` cassait le sandbox Figma — retiré.
- [x] Fix loop silencieuse : `figma.loadFontAsync` appelé avec Inter Medium alors que le TextNode utilise Regular par défaut → crash catchée silencieusement.
- [x] Refactor code.js : font chargée une fois avant la boucle, frame parent container, zoom auto, opacité minimum 15% pour les fonds transparents, try/catch global.
- [x] Manifest validé : `allowedDomains: ["none"]` + `devAllowedDomains: ["http://localhost:9998"]`.
- [x] Blueprint import ✅ | Reality import ✅ (17 éléments dans container parent).

---

## Mission 36 — Sullivan Cockpit : Conversational Refinement (Chat)
**STATUS: ✅ LIVRÉ**
**ACTOR: ANTIGRAVITY**
**DATE: 2026-03-11**
- [x] API Endpoint `/api/retro-genome/chat` créé.
- [x] Sullivan Refine implémenté dans `HtmlGenerator`.
- [x] UI Sync (bouton Envoyer, animations) branchée.
- [x] System Prompt intégré.

## Mission 35 — Retro-Genome Reality View Engine (Multi-pass)
**STATUS: ✅ LIVRÉ**
**ACTOR: ANTIGRAVITY**
**DATE: 2026-03-11**
- [x] Génération Multi-pass HTML → CSS → Review DA.
- [x] Exigence Design : Flexbox/Grid/Gap/Clamp.
- [x] Monitoring Sullivan dans l'UI.
- [x] Routage Dual-Viewer (Blueprint vs Reality).

## Mission 34C — Workflow Validation : Intent → Reality
**STATUS: ✅ LIVRÉ**
**ACTOR: GEMINI**
**DATE: 2026-03-11**
- [x] Persistance via `validated_analysis.json`.
- [x] Polling du statut frontend.

## Mission 34B — Dual Viewer : Routage & Endpoints Backend ✅ 2026-03-11
- [x] Routage serveur implémenté dans `server_9998_v2.py`.
- [x] Endpoint `/api/pedagogy/gaps` fonctionnel.

## Mission 34A — Dual Viewer : Templates & Cockpit Frontend ✅ 2026-03-11
- [x] `viewer_blueprint.html` extrait et nettoyé.
- [x] `viewer_reality.html` créé (canvas HTML/CSS + Cockpit Sullivan).
- [x] Routage serveur dual-viewer implémenté.
- [x] Endpoint `/api/pedagogy/gaps` ajouté au front.

## Mission 32 — Retro Genome (PNG → Intent → PRD) ✅ 2026-03-10
- [x] **Vision Backend** : `analyzer.py` via Gemini 2.0 Flash/Vision.
- [x] **Semantic Mapping** : `intent_mapper.py` (mapping Intents AetherFlow).
- [x] **Automation PRD** : `prd_generator.py` (synthèse doc + roadmap).
- [x] **Intent Viewer V1** : Interface `/intent-viewer` validation interactive.

## Mission 31B — SLCP Hardening (Gemini 2.0 & Data-Driven) ✅ 2026-03-10
- [x] Migration Gemini 2.0 pour tous les steps du pipeline.
- [x] Scaffold Data-Driven via `03_scaffold_generator.py`.
- [x] Précision Millimétrique (Sidebars, colonnes).

## Mission 31 — Dynamic App Shell Inference ✅ 2026-03-09
- [x] Support Genome : Intégration de `n0_app_shell`.
- [x] SVG Cleanup : Suppression des fonctions statiques.
- [x] Zone Planning : Libération des marges `header_h`.

## Mission 30 — Context Injection & SVG Bound Fix ✅ 2026-03-09
- [x] Flag `--context` : Injection dynamique du Manifeste.
- [x] Ghost Rect Cleanup : Suppression du `<rect>` background.
- [x] Activer le mode `thinking` sur les étapes 2 (Layout Director) et 6 (Composer).
- [x] Implémenter le script de validation post-génération `validate_atoms.py` (anti-serif, rx <= 10).
- [x] Modifier l'export SVG vers le Manifeste JSON pour aplatir les groupes (`<g>`) de positionnement.

---

## Mission 25B — Figma Bridge & JSON Manifest ✅ 2026-03-04
- [x] Génération du `manifest.json` dans `exports/` par le `07_composer.py`.
- [x] Calcul des coordonnées absolues (x, y) et dimensions (w, h) pour Figma.
- [x] Inclusion du `genome_hash` pour tracking de version.
- [x] API `GET /api/manifest` pour servir les données au plugin.
- [x] API `POST /api/manifest/patch` pour synchronisation bidirectionnelle.
- [x] Scaffolding du plugin Figma (`manifest.json`, `ui.html`, `code.js`).

## Mission 24G — Design Cleanup (rx <= 10) ✅ 2026-03-04
- [x] Contrainte stricte `rx <= 10` imposée dans `04_kimi_atom_factory.py` (prompt).
- [x] Sécurité RegEx ajoutée dans `07_composer.py` pour raboter tout `rx/ry > 10` à l'injection.
- [x] Cleanup des restes `rx="11"` dans le builder statique `genome_to_svg_v2.py`.

## Mission 24E — Recalibration échelle KIMI ✅ 2026-03-04
- [x] Calcul du scale factor forcé : `target_w / atom_viewbox_w`.
- [x] Injection des dimensions pixel cibles (`zone_w`, `zone_h`) dans le prompt de Step 6.
- [x] Lecture de `layout_plan.json` dès la génération des atomes.

## Mission 24D — Drag au niveau Organe ✅ 2026-03-03
- [x] Drag sur `.af-organ` déplace fond + tous ses composants enfants ensemble.
- [x] `POST /api/organ-move` persiste dans `template_overrides.json`.

## Mission 24C — Template Viewer Interactif (Drag + Resize) ✅ 2026-03-03
- [x] Drag d'un composant SVG sans libs tierces.
- [x] Resize d'un composant SVG.
- [x] Overrides persistés et restaurés.

## Mission 24B — KIMI : IDs sémantiques dans le SVG rendu ✅ 2026-03-03
- [x] Chaque zone/composant rendu dans `<g id="{comp_id}" class="kimi-comp">`.
- [x] `<title>{label}</title>` ajouté en premier enfant.

## Mission 24A — Template Viewer Chat UI ✅ 2026-03-03
- [x] Chat UI intégré (panneau droit 340px).
- [x] Route `POST /api/feedback` pour itération continue.
- [x] Zéro fetch(), tout en XHR.

---

## PHASE 1 — Wireframes Sullivan Renderer
STATUS: ARCHIVÉ
DATE: 2026-02-15
COMMIT: 94488da

---

### Leçons
- Le serveur avait un service worker agressif (cache-first) → require hard refresh
- Grille CSS + SVG grid = conflit visuel → une seule source de vérité
- Tokens CSS variables garantissent cohérence jour/nuit

---

---

## Mission 17A — Real Wireframes at N0
STATUS: ARCHIVÉ
DATE: 2026-03-01
ACTOR: CLAUDE (CODE DIRECT — FJD)
VALIDATION: FJD (commit git, branche idx-setup)

---

### Fichiers modifiés
- `static/js/SemanticMatcher.js`
- `static/js/Canvas.renderer.js`

---

## Mission 18A — Genome HTML Preview (Flowbite)
STATUS: ARCHIVÉ
DATE: 2026-03-02
ACTOR: CLAUDE (CODE DIRECT — FJD)
VALIDATION: Serveur 200 — validation visuelle FJD en attente

---

### Prochaine étape envisagée
Mission 18B — Inline editing : `contenteditable` + drag-and-drop + PATCH `/api/genome/node/<id>` → édition directe sans LLM dans la boucle.

---

## Mission V3-A — Backend Dead Code Cleanup
STATUS: ARCHIVÉ (PARTIEL)
DATE: 2026-03-02
ACTOR: AETHERFLOW (auto-exécuté) + CLAUDE (audit)
VALIDATION: 21/21 tests PASS

---

### Prochaine étape V3
V3-B : Supprimer `workflows/frd.py` et `workflows/verify_fix.py` (dead code confirmé) → débloque la suppression de `apply_generated_code()`.


---

## Mission 18B — Preview Inline Editor
STATUS: ARCHIVÉ
DATE: 2026-03-02
ACTOR: GEMINI (JS) + CLAUDE (endpoints Python)
VALIDATION: FJD ✅

---

### Résultat
Édition directe dans `/preview` sans LLM dans la boucle. Persistance dans `genome_reference.json`.

---

## Mission 19A — Canvas Layout Persistence
STATUS: ARCHIVÉ
DATE: 2026-03-02
ACTOR: GEMINI (auto-exécuté)
VALIDATION: Critères cochés par Gemini

---

### Ce qui a été fait
- `GET /api/layout` + `POST /api/layout` dans `server_9998_v2.py`
- `load_layout()` / `save_layout()` → `Frontend/2. GENOME/layout.json` (séparé du genome)
- `_renderCorps()` dans `Canvas.feature.js` : charge layout au démarrage, applique positions
- `_updateLayoutInGenome()` : fire-and-forget POST après chaque drag/resize

---

## Mission 19B — SurgicalEditorJS (AetherFlow JS Apply)
STATUS: ARCHIVÉ
DATE: 2026-03-02
ACTOR: GEMINI (auto-exécuté)
VALIDATION: test_surgical_js.py 1 PASSED ✅

---

### Impact
AetherFlow peut désormais éditer chirurgicalement les fichiers JS frontend.
CODE DIRECT pour JS n'est plus obligatoire — AetherFlow mode -f supporte les patches JS.

---

## Mission Proto-20A — Genome Canvas HTML (Prototype)
STATUS: ARCHIVÉ
DATE: 2026-03-02
ACTOR: AETHERFLOW (Gemini) + CLAUDE (hotfixes)
VALIDATION: FJD — drag fonctionnel, tabs OK

---

### Décision architecture
Canvas HTML pur validé comme remplacement du canvas SVG cassé.
→ Mission 20A : focus mode + resize + layout complet.

---

## Mission 20A — Canvas Features : Focus Mode + Resize + Layout w
STATUS: ARCHIVÉ
DATE: 2026-03-02
ACTOR: AETHERFLOW (Gemini) + CLAUDE (hotfixes resize)
VALIDATION: FJD ✅ "Cool"

---

### Mission 14F-P1-CLAUDE-TEST — Suppression HTTP controls (ComponentsZone)
**ACTOR: CLAUDE (AetherFlow -f test) | MODE: CODE DIRECT | DATE: 2026-03-01 | STATUS: MISSION ACTIVE**

> Test exploratoire : Claude génère le plan AetherFlow, exécute, applique manuellement les patches.
> Objectif : éprouver les limites du mode frontend AetherFlow avec Claude comme agent.
> Scope : Fix 1 de 14F-BUGS uniquement.

#### Cible
Fichier : `static/js/features/ComponentsZone.feature.js`

#### Changements
1. `_renderCelluleView` — template atom card :
   - Supprimer classe `edit-mode` (div.component-card)
   - Supprimer `<select>` méthode HTTP (GET/POST/PUT/DELETE/PATCH)
   - Supprimer `<div class="atom-endpoint-row">` + label URL + input endpoint
2. `_setupCelluleListeners` — inputs + updateFn :
   - Supprimer `method` et `endpoint` des inputs
   - Supprimer `atom.method`, `atom.endpoint`, `inputs.method.className` du updateFn

#### Critères d'acceptation
- [ ] N3 sidebar : zéro select HTTP, zéro endpoint input, zéro classe edit-mode
- [ ] atom-name-input + atom-desc-input toujours fonctionnels (persistence OK)
- [ ] FJD valide visuellement http://localhost:9998/stenciler (Cmd+Shift+R obligatoire)

---

---

### Mission 14F-P2-CLAUDE-TEST — Reorder + Collapse panels sidebar-right
**ACTOR: CLAUDE (AetherFlow -f test) | MODE: CODE DIRECT | DATE: 2026-03-01 | STATUS: MISSION ACTIVE**

> Test 2 du pipeline AetherFlow frontend avec Claude.
> Scope : `_renderSidebarPanels` dans ComponentsZone.feature.js uniquement.

#### Changements
1. **Reorder** : outils d'édition d'abord, outils pédagogiques/info en dessous
   - Ordre cible : TRANSFORMATION → STYLE & COULEURS → DISPOSITION → MAGNÉTISME → TYPOGRAPHIE → NUANCE
2. **Collapse par défaut** : tous les panels ont la classe `collapsed` SAUF `panel-transform` (ouvert)

#### Critères d'acceptation
- [ ] TRANSFORMATION ouvert au chargement, les 5 autres panels fermés
- [ ] Ordre visuel : Transform > Style > Disposition > Snap > Typo > Nuance
- [ ] Aucune régression sur les handlers (colors, sliders, inputs restent fonctionnels)
- [ ] FJD valide visuellement http://localhost:9998/stenciler (Cmd+Shift+R obligatoire)

---

---

### Mission 14F-P3-CLAUDE-TEST — Outils d'édition en premier (N2 et N3)
**ACTOR: CLAUDE (AetherFlow -f test) | MODE: CODE DIRECT | DATE: 2026-03-01 | STATUS: MISSION ACTIVE**

> Test 3 du pipeline AetherFlow frontend avec Claude.
> Scope : `_renderOrganeView` et `_renderCelluleView` dans ComponentsZone.feature.js.

#### Problème
Dans les vues N2 (organe) et N3 (cellule), le contenu pédagogique (liste cellules / atom-cards) apparaît AVANT les panels d'édition (TRANSFORMATION, STYLE…). L'utilisateur veut les outils d'édition en premier visuellement.

#### Changements
1. Dans `_renderOrganeView` : déplacer `<div id="transform-panel-container"></div>` AVANT `.components-grid.clickable`
2. Dans `_renderCelluleView` : déplacer `<div id="transform-panel-container"></div>` AVANT `.components-grid.n3-view`

#### Critères d'acceptation
- [ ] Vue N2 : panels TRANSFORMATION etc. affichés EN PREMIER, cellules en dessous
- [ ] Vue N3 : panels TRANSFORMATION etc. affichés EN PREMIER, atom-cards en dessous
- [ ] Aucune régression sur les event listeners (click cell, persistence atom)
- [ ] FJD valide visuellement http://localhost:9998/stenciler

---

---

### Mission 14F-P4-CLAUDE-TEST — PrimOverlay persistence → génome
**ACTOR: CLAUDE (AetherFlow -f test) | MODE: CODE DIRECT | DATE: 2026-03-01 | STATUS: MISSION ACTIVE**

> Test 4 du pipeline AetherFlow frontend avec Claude.
> Scope : `_exitGroupEdit()` dans Canvas.feature.js uniquement.

#### Problème
En Mode Illustrateur (11A), les modifications de primitives SVG sont sauvées dans `PrimOverlay` (Map mémoire) mais **jamais écrites dans le génome**. Si l'utilisateur quitte le niveau ou recharge la page, les éditions sont perdues.

#### Changement
Dans `_exitGroupEdit()` (Canvas.feature.js L.999-1004), après `PrimOverlay.set(...)`, ajouter :
1. `this._findInGenome(nodeId)` → récupérer le nœud génome
2. `genomeNode.svg_payload = content.innerHTML` → écriture SVG dans le génome
3. `genomeNode.svg_h = bb.height || 80` → hauteur pour renderAtom
4. Dispatcher `genome:updated` avec le nœud (déjà fait dans `_exitGroupEdit` via `_renderCorps`)

`renderAtom` dans AtomRenderer.js vérifie déjà `nodeData.svg_payload` (protocole 13A-PRE) — aucune modification d'AtomRenderer nécessaire.

#### Critères d'acceptation
- [ ] Modifier une primitive en Mode Illustrateur → exit → drill back → primitive conservée (via PrimOverlay session) ✅ (déjà le cas)
- [ ] Modifier une primitive → Cmd+Shift+R (reload complet) → primitive toujours présente (via svg_payload dans génome) ← NEW
- [ ] `genome:updated` dispatché après l'écriture → sauvegarde propagée

---

---

### Mission 15A — SemanticMatcher + WireframeLibrary Coverage
**STATUS: LIVRÉ — EN ATTENTE VALIDATION FJD**
**ACTOR: Claude (Gemini n'a pas livré — Claude CODE DIRECT)**
**MODE: CODE DIRECT (JS vanilla, ESM)**
**DATE: 2026-03-01**

#### Contexte

Audit du `genome_reference.json` révèle 39 atomes avec `visual_hint` explicite.
`_matchHint()` dans `Canvas.renderer.js` lit `data.visual_hint` en priorité → passe à `WireframeLibrary.getSVG(hint)`.

**Gap identifié — hints genome sans cas WireframeLibrary :**

| visual_hint génome | Fréquence | Mapping cible |
|---|---|---|
| `button` | 5× | → `action-button` |
| `detail-card` | 2× | → `stencil-card` |
| `card` | 1× | → `stencil-card` |
| `choice-card` | 3× | → `selection` |
| `launch-button` | 1× | → `action-button` |
| `apply-changes` | 1× | → `action-button` |
| `download` | 1× | → `action-button` |
| `status` | 1× | → `dashboard` |
| `list` | 1× | → `accordion` |
| `chat-input` | 1× | → nouveau SVG `chat-input` |
| `preview` | 2× | → nouveau SVG `preview` |
| `form` | 1× | → nouveau SVG `form` |

**Hints déjà couverts (ne pas toucher) :**
`table`, `stencil-card`, `dashboard`, `stepper`, `breadcrumb`, `grid`,
`upload`, `color-palette`, `chat/bubble`, `accordion`, `zoom-controls`, `editor`, `modal`

---

#### Livrable 1 — `SemanticMatcher.js` (nouveau fichier)

Créer `Frontend/3. STENCILER/static/js/SemanticMatcher.js` :

```javascript
/**
 * SemanticMatcher.js
 * Résout visual_hint → WireframeLibrary hint avec couverture complète du génome.
 * Ordre de priorité : visual_hint (explicit) → interaction_type → keyword fallback
 * Mission 15A — 2026-03-01
 */

// Mapping visual_hint génome → WireframeLibrary hint
const VISUAL_HINT_MAP = {
    // Aliases directs (genome → library)
    'detail-card'   : 'stencil-card',
    'card'          : 'stencil-card',
    'choice-card'   : 'selection',
    'button'        : 'action-button',
    'launch-button' : 'action-button',
    'apply-changes' : 'action-button',
    'download'      : 'action-button',
    'status'        : 'dashboard',
    'list'          : 'accordion',
    'chat-input'    : 'chat-input',   // nouveau SVG
    'preview'       : 'preview',       // nouveau SVG
    'form'          : 'form',          // nouveau SVG
    // Existing (identité, passthrough)
    'table': 'table', 'stencil-card': 'stencil-card', 'dashboard': 'dashboard',
    'stepper': 'stepper', 'breadcrumb': 'breadcrumb', 'grid': 'grid',
    'upload': 'upload', 'color-palette': 'color-palette', 'chat/bubble': 'chat/bubble',
    'accordion': 'accordion', 'zoom-controls': 'zoom-controls', 'editor': 'editor',
    'modal': 'modal', 'selection': 'selection', 'action-button': 'action-button',
    'nav': 'breadcrumb', 'navigation': 'breadcrumb', 'layout': 'grid',
    'search': 'brainstorm',
};

// Fallback interaction_type → hint
const INTERACTION_MAP = {
    'submit' : 'action-button',
    'drag'   : 'upload',
    'click'  : null, // pas assez précis → keyword fallback
};

export function resolveHint(data) {
    // 1. visual_hint explicite
    if (data.visual_hint) {
        const mapped = VISUAL_HINT_MAP[data.visual_hint];
        if (mapped) return mapped;
    }
    // 2. interaction_type
    if (data.interaction_type) {
        const mapped = INTERACTION_MAP[data.interaction_type];
        if (mapped) return mapped;
    }
    // 3. Keyword fallback sur id + name
    return _keywordFallback(data);
}

function _keywordFallback(data) {
    const pool = `${data.id || ''} ${data.name || ''}`.toLowerCase();
    const keywords = {
        'table': ['table', 'ir', 'listing'],
        'stepper': ['stepper', 'sequence', 'workflow'],
        'chat/bubble': ['chat', 'dialogue', 'bubble'],
        'editor': ['editor', 'code', 'json'],
        'breadcrumb': ['breadcrumb', 'navigation', 'nav'],
        'dashboard': ['dashboard', 'session', 'status', 'summary'],
        'accordion': ['accordion', 'validation', 'list'],
        'color-palette': ['palette', 'theme', 'color', 'style'],
        'upload': ['upload', 'import', 'deposit'],
        'action-button': ['deploy', 'export', 'download', 'launch', 'button'],
        'stencil-card': ['card', 'arbitrage'],
        'selection': ['selection', 'choice', 'picker'],
        'modal': ['modal', 'confirm', 'popup'],
        'grid': ['layout', 'grid', 'view', 'gallery'],
        'brainstorm': ['brainstorm', 'search', 'idea'],
    };
    for (const [hint, kws] of Object.entries(keywords)) {
        if (kws.some(k => pool.includes(k))) return hint;
    }
    return null;
}
```

---

#### Livrable 2 — Mise à jour `Canvas.renderer.js`

Remplacer `_matchHint(data)` par un appel à `SemanticMatcher.resolveHint(data)` :

**Import à ajouter en tête de fichier :**
```javascript
import { resolveHint } from './SemanticMatcher.js';
```

**Remplacer la méthode `_matchHint` entière par :**
```javascript
_matchHint(data) {
    return resolveHint(data);
},
```

---

#### Livrable 3 — 3 nouveaux SVG dans `WireframeLibrary.js`

Ajouter 3 nouveaux cas dans le `switch(hint?.toLowerCase())` :

**`chat-input`** — zone de saisie chat avec bouton send :
```svg
<!-- Fond input -->
<rect x="20" y="130" width="200" height="32" rx="16" fill="var(--bg-tertiary)" stroke="var(--border-default)" stroke-width="1"/>
<!-- Placeholder text -->
<rect x="36" y="141" width="100" height="10" rx="5" fill="var(--text-muted)" opacity="0.4"/>
<!-- Send button -->
<circle cx="232" cy="146" r="12" fill="${color}"/>
<path d="M226 146 L232 140 L238 146 M232 140 L232 152" fill="none" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
<!-- Bubbles précédentes -->
<rect x="20" y="30" width="140" height="28" rx="14" fill="${color}" opacity="0.3"/>
<rect x="100" y="68" width="140" height="28" rx="14" fill="var(--bg-tertiary)" stroke="var(--border-default)" stroke-width="1"/>
<rect x="20" y="106" width="80" height="16" rx="8" fill="${color}" opacity="0.15"/>
```

**`preview`** — zone de prévisualisation avec frame + vignettes :
```svg
<!-- Frame principale -->
<rect x="20" y="20" width="240" height="100" rx="8" fill="var(--bg-tertiary)" stroke="var(--border-default)" stroke-width="1"/>
<!-- Contenu simulé -->
<rect x="32" y="32" width="216" height="60" rx="4" fill="var(--bg-secondary)" opacity="0.7"/>
<rect x="32" y="100" width="60" height="8" rx="4" fill="var(--text-muted)" opacity="0.4"/>
<rect x="100" y="100" width="40" height="8" rx="4" fill="${color}" opacity="0.5"/>
<!-- Vignettes -->
<rect x="20" y="135" width="60" height="36" rx="4" fill="${color}" opacity="0.25" stroke="${color}" stroke-width="1.5"/>
<rect x="88" y="135" width="60" height="36" rx="4" fill="var(--bg-tertiary)" stroke="var(--border-default)" stroke-width="1"/>
<rect x="156" y="135" width="60" height="36" rx="4" fill="var(--bg-tertiary)" stroke="var(--border-default)" stroke-width="1"/>
```

**`form`** — formulaire avec labels + inputs + bouton submit :
```svg
<!-- Label 1 -->
<rect x="20" y="20" width="60" height="8" rx="4" fill="var(--text-muted)" opacity="0.5"/>
<!-- Input 1 -->
<rect x="20" y="34" width="240" height="28" rx="6" fill="var(--bg-tertiary)" stroke="var(--border-default)" stroke-width="1"/>
<!-- Label 2 -->
<rect x="20" y="72" width="80" height="8" rx="4" fill="var(--text-muted)" opacity="0.5"/>
<!-- Input 2 -->
<rect x="20" y="86" width="240" height="28" rx="6" fill="var(--bg-tertiary)" stroke="var(--border-default)" stroke-width="1"/>
<!-- Submit -->
<rect x="20" y="130" width="240" height="36" rx="8" fill="${color}" opacity="0.85"/>
<rect x="100" y="142" width="80" height="10" rx="5" fill="white" opacity="0.9"/>
```

---

#### Contraintes

- `input_files` obligatoires : `stenciler.css`, `LEXICON_DESIGN.json`
- Ne pas modifier `AtomRenderer.js` ni `PrimOverlay.js`
- `SemanticMatcher.js` = module ESM pur, pas de side-effects
- SVG WireframeLibrary : respecter le pattern `wrapper(...)` existant avec `scale` et `offsetX/Y`
- Ne pas modifier les 13 cases existantes de `WireframeLibrary.js`
- Conserver `_matchHint` comme méthode de `Renderer` (pas d'export direct)

#### Critères d'acceptation

- [ ] `comp_chat_input` → affiche zone input + send button (plus de boîte grise vide)
- [ ] `comp_vision_report` → affiche `preview` (vignettes + frame)
- [ ] `comp_arbiter_validate` → affiche `form` (inputs + submit)
- [ ] `comp_session_reset` → affiche `action-button` (plus de boîte vide)
- [ ] `comp_upload_delete` → affiche `action-button`
- [ ] `comp_layout_card` → affiche `stencil-card`
- [ ] Zéro régression sur les 13 hints existants
- [ ] `SemanticMatcher.js` importable sans erreur
- [ ] FJD valide visuellement sur http://localhost:9998/stenciler

---

## Mission 16A — Brancher /api/infer_layout dans Canvas.feature.js [MISSION ACTIVE]

**ACTOR : GEMINI**
**DATE : 2026-03-01**
**STATUS : LIVRÉ — EN ATTENTE VALIDATION FJD**

---

### Blocages connus
- **V3-A Tâche 2** : `apply_generated_code()` non supprimable tant que `frd.py` / `verify_fix.py` existent.
- **Preview inline editing** : OPÉRATIONNEL. Renommage, hint swap et reorder persistent dans le JSON.

---

## Mission 18B — Preview Inline Editor ✅ ARCHIVÉ
**ACTOR: GEMINI | MODE: CODE DIRECT — FJD | DATE: 2026-03-02 | STATUS: COMPLETED**

---

---

### Mission 14F-P4-CLAUDE-TEST — PrimOverlay persistence → génome ✅ LIVRÉ

---


## Mission 19A — Canvas Layout : Drag & Resize des Organes N0 ✅ ARCHIVÉ
**ACTOR: GEMINI | MODE: CODE DIRECT — FJD | DATE: 2026-03-02 | STATUS: COMPLETED**

---

### Critères d'acceptation
- [x] Drag organe N0 → se déplace librement
- [x] Reload → position restaurée depuis `layout.json`
- [x] Drag poignée coin → organe redimensionné
- [x] Reload → dimensions restaurées
- [x] Drill dans organe → layout N1/N2/N3 non affecté
- [x] `layout.json` absent → fallback `_zoneTemplateToPositions()` (zéro régression)

---

## Mission 20C — Genome Canvas : Resize Hauteur + Inline Rename
**ACTOR: GEMINI | MODE: CODE DIRECT | DATE: 2026-03-02 | STATUS: MISSION ACTIVE**

---
⚠️ BOOTSTRAP GEMINI (obligatoire)
Tu es Gemini, agent frontend AetherFlow.
FJD = DA — seule autorité esthétique. Aucune décision visuelle non demandée.
Lis le fichier cible ENTIÈREMENT avant de coder.
Valide mentalement chaque feature avant de livrer.
---

---

### Critères d'acceptation
- [x] Clic sur carte → ouvre la sidebar avec les palettes. Le changement change la couleur.
- [x] Le layout SVG n'est plus concerné, tout se fait en HTML pur via les IDs du DOM.
- [x] Double clic carte → mode Pénétrant (Drill down zoomé).
- [x] Dans le mode zoom, modification d'un composant de base → le genome RAM est MAJ, le composant est re-rendu instantanément.

---

## Mission 21B — Genome Enricher : Pass 1 Classification Sémantique

**ACTOR: GEMINI**
**MODE: aetherflow -f**
**DATE: 2026-03-03**
**STATUS: COMPLETED**

---

### Bootstrap Gemini OBLIGATOIRE

```
Tu es Gemini, agent frontend AetherFlow.
Tu reçois une mission Python backend exceptionnelle (enrichissement de données, pas d'UI).
Lis impérativement les fichiers listés avant de coder.
Respecte la structure genome : n0_phases → n1_sections → n2_features → n3_components[].visual_hint
Ne crée pas de nouveaux fichiers au-delà de ceux listés.
Guillemets doubles uniquement dans les strings Python destinées à XML/SVG.
Réponds avec le code complet de chaque fichier entre triple backticks avec le chemin en commentaire L1.
```
- [x] Le `server_9998_v2.py` accepte et consolide correctement ces modifications dans son fichier physique.

---

## PHASE 21E — Mission Topology Bank + Renderer Topologique
STATUS: ARCHIVÉ
DATE: 2026-03-03
COMMIT: fc3dec8
BRANCH: experience_front_gemini

---

### Décision
→ Abandon du renderer Python statique comme solution principale. Passer à KIMI comme générateur SVG IA.

---

## PHASE 22 — Prop 3A + 2B : Latence AetherFlow
STATUS: ARCHIVÉ
DATE: 2026-03-03
COMMIT: 0a97804
BRANCH: experience_front_gemini

---

### Méthode
- Plan AetherFlow lancé (780s, 648K tokens) → .generated non auto-appliqués (Codestral fragmented output)
- Apply final : CODE DIRECT sur les 4 fichiers

---


## Mission 35/36 V2 — Agency Loop : Visual QA & HCI Stabilization

**STATUS: ✅ ACHEVÉ**
**ACTOR: ANTIGRAVITY**
**DATE: 2026-03-11**

---

### Réalisations
- **The Lens (Playwright)** : Moteur de rendu Headless pour capturer les screenshots des essais.
- **M2M Loop (Junior vs DA)** : Boucle fermée entre intégrateur (Flash) et DA (Vision) pour corriger les dérives stylistiques.
- **Monitoring Sullivan** : Affichage en direct de la "Critique du DA" dans le cockpit Sullivan.
- **HCI Director Approval** : Validation humaine obligatoire (Bouton Approve/Reject) avant livraison.

---

## Mission 41 — SVG Ingress : Figma → Pipeline (Plugin Bridge + svg_parser)

**STATUS: ✅ ACHEVÉ (Tâches A/B/C/D)**
**ACTOR: GEMINI (implémentation) + CLAUDE (review)**
**DATE: 2026-03-13**

---

### Validé FJD : ✅

---

## Mission 74 — Sullivan : "Procède" → exécution du plan discuté
**STATUS: ✅ LIVRÉ**
**DATE: 2026-03-23**
**ACTOR: CLAUDE**
**MODE: CODE DIRECT**
**FICHIERS :** `Frontend/3. STENCILER/server_9998_v2.py`

- [x] `_route_request()` enrichi avec le dernier tour model de l'historique
- [x] Groq route "procède/go/implémente" vers `html-only` ou `both` quand le tour précédent contient un plan
- [x] `history` passé à `_route_request` depuis `/api/frd/chat`
- [x] Log `[MISSION 64] Route: html-only` sur les confirmations d'exécution

---

### Validé FJD : ✅

---

## Mission 77 — Sullivan Knowledge Base : RAG AetherFlow branché sur /api/frd/chat
**STATUS: ✅ LIVRÉ**
**DATE: 2026-03-24**
**ACTOR: CLAUDE**
**MODE: CODE DIRECT**
**FICHIERS :** `Frontend/3. STENCILER/server_9998_v2.py`

- [x] `_SULLIVAN_DOCS` : corpus 7 sources (docs/02_Sullivan, 04_HomeOS, 03_AetherFlow, ROADMAP, ROADMAP_ACHIEVED)
- [x] `_init_sullivan_rag()` → `PageIndexRetriever` LlamaIndex CPU-only, log `[RAG] Index Sullivan : N documents`
- [x] `_exec_query_knowledge_base(query)` → top-4 chunks avec source metadata
- [x] Tool `query_knowledge_base` déclaré dans `/api/frd/chat` functionDeclarations (type OBJECT majuscules)
- [x] Handler `elif fc.get('name') == 'query_knowledge_base'` dans la boucle tool calling
- [x] Log `[RAG] query='...' → N chars`

---

### Validé FJD : ✅

---

## Mission 81 — Sullivan BKD : system_instruction Python/backend
**STATUS: ✅ LIVRÉ**
**DATE: 2026-03-24**
**ACTOR: CLAUDE**
**MODE: CODE DIRECT**
**FICHIERS :** `Frontend/3. STENCILER/server_9998_v2.py`

- [x] `_SULLIVAN_BKD_SYSTEM` définie après `_MANIFEST_FRD = _load_manifest_frd()` (ligne ~124)
- [x] Persona : architecte backend Python/DevOps, jamais HTML/Tailwind
- [x] Stack : Python 3.11+, http.server, LlamaIndex, SQLite, Docker
- [x] 5 règles : patches précis, citer fichier+fonction, ordre multi-fichiers, pas d'API inventée, RAG obligatoire

---

### Validé FJD : ✅

---

## Mission 79 — User DB BKD : project_id → project_path (SQLite)
**STATUS: ✅ LIVRÉ**
**DATE: 2026-03-24**
**ACTOR: CLAUDE (MiMo direct)**
**MODE: CODE DIRECT**
**FICHIERS :** `Frontend/3. STENCILER/server_9998_v2.py`, `db/projects.db`

- [x] `import sqlite3` ajouté
- [x] `_BKD_DB_PATH = Path('.../db/projects.db')`, `_init_bkd_db()`, `_bkd_db_con()` (check_same_thread=False)
- [x] Table `projects` : id, name, path, created_at, last_opened
- [x] `GET /api/bkd/projects` → liste triée par last_opened
- [x] `GET /api/bkd/projects/{id}` → détail projet
- [x] `POST /api/bkd/projects` → upsert (si path existant, màj last_opened ; sinon UUID4)
- [x] `POST /api/bkd/projects/{id}` + `X-HTTP-Method-Override: DELETE` → suppression
- [x] Tests curl : création, liste, arbre → OK

---

### Validé FJD : ✅

---

## Mission 80 — /api/bkd/file + /api/bkd/tree : lecture/écriture fichiers projet
**STATUS: ✅ LIVRÉ**
**DATE: 2026-03-24**
**ACTOR: CLAUDE (MiMo direct)**
**MODE: CODE DIRECT**
**FICHIERS :** `Frontend/3. STENCILER/server_9998_v2.py`

- [x] `_BKD_ALLOWED_EXTENSIONS` (13 types), `_BKD_EXCLUDE_DIRS` (8 exclusions)
- [x] `_resolve_bkd_project_root(project_id)` → Path depuis SQLite
- [x] `_bkd_safe_path(root, rel)` → anti path-traversal (resolved.relative_to())
- [x] `_bkd_build_tree(root, depth)` → arbre récursif, dirs avant fichiers
- [x] `GET /api/bkd/file?project_id=&path=` → {content, language, path, size}
- [x] `GET /api/bkd/tree?project_id=&depth=` → {tree, root}
- [x] `POST /api/bkd/file` → écriture avec mkdir -p
- [x] Test : lecture `orchestrator.py` (68KB) → OK

---

### Validé FJD : ✅

---

## Mission 78 — Sullivan BKD : Groq router + /api/bkd/chat (Gemini cascade)
**STATUS: ✅ LIVRÉ**
**DATE: 2026-03-24**
**ACTOR: CLAUDE (MiMo direct)**
**MODE: CODE DIRECT**
**FICHIERS :** `Frontend/3. STENCILER/server_9998_v2.py`

- [x] `_BKD_MODEL_MAP` : quick→flash-lite, code-simple→flash, code-complex/wire/diagnostic→2.0-flash
- [x] `_route_request_bkd(message, history)` → Groq llama-3.3-70b, fallback propre si GROQ_API_KEY absent
- [x] `POST /api/bkd/chat` : Groq route → dispatch Gemini, history 12 tours, project_ctx si project_id
- [x] Tool use loop (max 4 iter) : `query_knowledge_base` (RAG) + `read_bkd_file` (lecture projet)
- [x] Réponse `{explanation, model, route}`
- [x] Test curl : route=quick → gemini-2.0-flash-lite, réponse BKD en < 5s

---

### Validé FJD : ✅

---

## Mission 82 — RM : Correctif model map BKD + FRD (vrais modèles Gemini)
**STATUS: ✅ LIVRÉ**
**DATE: 2026-03-24**
**ACTOR: CLAUDE (CODE DIRECT)**
**MODE: CODE DIRECT**
**FICHIERS :** `Frontend/3. STENCILER/server_9998_v2.py`

- [x] `_BKD_MODEL_MAP` ne référence plus `gemini-3.1-flash` (modèle fantôme → HTTP 404)
- [x] Alignement sur modèles réels confirmés : quick→flash-lite, code-simple→2.0-flash, code-complex/wire/diagnostic→2.5-pro
- [x] `python3 -m py_compile server_9998_v2.py` → OK

---

### Validé FJD : ✅

---

## Mission 84 — RM : Fix `system_prompt` kwarg dans GroqClient + CodestralClient
**STATUS: ✅ LIVRÉ**
**DATE: 2026-03-24**
**ACTOR: CLAUDE (CODE DIRECT)**
**MODE: CODE DIRECT**
**FICHIERS :** `Backend/Prod/models/groq_client.py`, `Backend/Prod/models/codestral_client.py`

- [x] `GroqClient.generate()` accepte `system_prompt: Optional[str] = None`
- [x] Injecté en `{"role": "system", "content": system_prompt}` avant la logique json_surgical
- [x] `CodestralClient.generate()` idem
- [x] Le fallback cascade `agent_router.py` ne lève plus de `TypeError`

---

### Validé FJD : ✅

---

## Mission 83 — SullivanArbitrator : sentinelle dynamique + cascade Qwen/MiMo
**STATUS: ✅ LIVRÉ**
**DATE: 2026-03-24**
**ACTOR: GEMINI (module) + CLAUDE (wiring)**
**MODE: CODE DIRECT**
**FICHIERS :** `Frontend/3. STENCILER/sullivan_arbitrator.py` (NEW), `Frontend/3. STENCILER/server_9998_v2.py`

- [x] `sullivan_arbitrator.py` : SullivanSentinel (SQLite `db/metrics.db`), SullivanPulse (probe daemon 120s), SullivanArbitrator.pick()
- [x] TIER_MAP : quick/code-simple/code-complex → Gemini primaire | wire/diagnostic → MiMo primaire
- [x] Fallback Qwen SiliconFlow (QWEN_KEY) ou OpenRouter (OPEN_ROUTER_QWEN_KEY)
- [x] Clients inline urllib (0 dépendance externe)
- [x] `db_path` absolu via `Path(__file__).parent.resolve()`
- [x] First-boot : pas de métriques pulse → primary par défaut (pas de fallback intempestif)
- [x] Wiring `server_9998_v2.py` : import + `_ARBITRATOR` + `_PULSE.start()` au boot
- [x] `GET /api/sullivan/pulse` → `_PULSE.get_status()` ✅ testé
- [x] `/api/bkd/chat` utilise `_ARBITRATOR.pick(route_type)` + `_ARBITRATOR.dispatch()` ✅
- [x] MiMo répond sur route `diagnostic` : "Bonjour ! Je suis Sullivan." ✅
- [x] `python3 -m py_compile server_9998_v2.py` → OK

---

### Validé FJD : ✅

---

## Mission 91 + 91-A — API Generator Engine
**STATUS: ✅ LIVRÉ**
**DATE: 2026-03-25**
**ACTOR: CLAUDE**
**FICHIERS :** `Backend/Prod/retro_genome/api_generator.py` (NEW), `Backend/Prod/retro_genome/functional_archetypes.json`

- [x] `api_generator.py` : CLI `--manifest → --output router_{slug}.py`
- [x] Pipeline complet prouvé : `bkd_frd.html` → manifest_inferer → api_generator → router Python valide
- [x] M91-A : détection top-2 archetypes composites (score2 >= 50% score1)
- [x] M91-A : résolution `aetherflow_conventions` dans `functional_archetypes.json`
- [x] `functional_archetypes.json` : conventions ajoutées à `ide_like` + `chatbot_pro`
- [x] Résultat sur `bkd_frd.html` : `ide_like (6) + chatbot_pro (3)` → 5 routes, 3/5 matchent exactement `server_v3.py` ✅
- [x] Test B : syntaxe Python valide (ast.parse) ✅
- [x] Pushé sur main (94c8d13)

---

### Validé FJD : ✅

---

## Mission 92 — Archetypes HoméOS natifs
**STATUS: ✅ LIVRÉ**
**DATE: 2026-03-25**
**ACTOR: CLAUDE**
**FICHIERS :** `Backend/Prod/retro_genome/functional_archetypes.json`

- [x] `aetherflow_brs` : War Room multi-LLM (dispatch/stream/capture/prd/arbitrate)
- [x] `genome_canvas` : Stenciler SVG (genome/manifest/infer-layout/organ-move/comp-*)
- [x] `retro_genome_studio` : Studio analyse (upload/validate/approve/reality/generate/export)
- [x] Fix: `pascal_node` duplicate `math_role` → `layout_role`
- [x] Test: `brainstorm_war_room_tw.html` → `aetherflow_brs` détecté (score direct) ✅
- [x] Test: `bkd_frd.html` → `ide_like + chatbot_pro` composite ✅
- [x] Pushé sur main (9981a34)

---

### Validé FJD : ✅

---

## Mission 85 — FastAPI Foundation : server_v3.py + routes BKD
**DATE: 2026-03-24 | ACTOR: GEMINI + CLAUDE | STATUS: ✅ LIVRÉ**
- `server_v3.py` FastAPI + uvicorn port 9999 → basculé port 9998
- Routes `/api/bkd/*` portées depuis server_9998_v2.py
- Pydantic models body BKD, exceptions HTTPException

## Mission 86 — FastAPI FRD : `/api/frd/*` + fix bug 500
**DATE: 2026-03-24 | ACTOR: GEMINI + CLAUDE | STATUS: ✅ LIVRÉ**
- Routes `/api/frd/*` portées (file, files, assets, wire-audit, wire-source, kimi)
- Fix bug 500 import manquant

## Mission 87-A — FastAPI : Genome + Layout + fichiers statiques
**DATE: 2026-03-24 | ACTOR: GEMINI | STATUS: ✅ LIVRÉ**
- Routes genome, layout, fichiers statiques montés sur server_v3.py

## Mission 87-B — FastAPI : BRS (Brain-Reasoning System)
**DATE: 2026-03-24 | ACTOR: GEMINI | STATUS: ✅ LIVRÉ**
- Router BRS monté : dispatch, stream, capture, prd, arbitrate

## Mission 87-C — FastAPI : Retro-Genome
**DATE: 2026-03-24 | ACTOR: GEMINI | STATUS: ✅ LIVRÉ (partiel)**
- Router retro_genome monté : upload, validate, reality, generate-prd
- Routes critiques présentes, quelques endpoints secondaires ajoutés en M91

## Mission 87-D — Bascule port 9998 + archivage server_9998_v2.py
**DATE: 2026-03-24 | ACTOR: CLAUDE | STATUS: ✅ LIVRÉ**
- server_v3.py basculé port 9998 (remplace définitivement server_9998_v2.py)
- server_9998_v2.py archivé

---

## Mission 97 — Wire UX v2 : table bijective + diagnostic géographique
**DATE: 2026-03-25 | ACTOR: CLAUDE + GEMINI | STATUS: ✅ LIVRÉ**
- `wire_analyzer.py` : extraction intentions, matching INTENT_MAP, badges ok/error
- `frd_editor.html` : table bijective Wire, diagnostic géographique (position bbox)
- Route `GET /api/frd/wire-audit` opérationnelle

## Mission 98 — Wire UX v3 : skeleton mode
**DATE: 2026-03-26 | ACTOR: GEMINI | STATUS: ✅ LIVRÉ**
- Skeleton mode overlay dans frd_editor.html
- Peel-out CSS sur iframe en mode Wire

## Mission 99 — Wire UX v4 : peel-out CSS + pop-in Monaco + route wire-source
**DATE: 2026-03-27 | ACTOR: CLAUDE | STATUS: ✅ LIVRÉ (CODE DIRECT)**
- Route `GET /api/frd/wire-source?func=handler_name` → retourne code Python du handler
- `FrdWire.feature.js` : pop-in Monaco affichée AVANT le fetch (fallback sans Monaco)
- Badge wire positionné sur l'élément (corrigé de top-18px → top)
- `UI_ONLY_FUNCTIONS` blacklist dans wire_analyzer.py (filtre setMode, togglePanel…)

---

## Mission 101-bis — Bridge Plugin ui.html — conformité design HoméOS
**DATE: 2026-03-30 | ACTOR: CLAUDE | STATUS: ✅ LIVRÉ (CODE DIRECT)**
- `--primary: #8cc63f` (vert HoméOS officiel, remplace #ff6b35)
- `text-transform: uppercase` supprimé de `.subtitle`
- Emojis boutons et statuts supprimés (📐, 🎨, ⚠️, ✓)
- 4 `figma.notify()` nettoyés dans code.js
- Feedback export enrichi : archétype + nb composants + lien intent viewer

## Mission 100 — Landing Import unifiée
**DATE: 2026-03-30 | ACTOR: GEMINI + CLAUDE | STATUS: ✅ LIVRÉ**
- `/landing` → `landing.html` — grille imports Figma Bridge
- Polling 10s, badge notification, bouton rafraîchir + vider
- Route `POST /api/retro-genome/imports/clear` (CODE DIRECT Claude)
- Lien stenciler supprimé → remplacé par frd-editor

## Mission 102 — Intent Viewer : auto-load + endpoint import-analysis
**DATE: 2026-03-30 | ACTOR: CLAUDE | STATUS: ✅ LIVRÉ (CODE DIRECT)**
- Route `GET /api/retro-genome/import-analysis?id=...` : re-parse SVG → components[]
- Mapping schema svg_parser : apparent_role, visual_hint, text_content
- `fetchIntents()` redirigé depuis /status (vide) vers /imports + /import-analysis
- Tous les liens stenciler/editor → /frd-editor dans intent_viewer.html
- `autoLoadLatestImport()` : affiche résumé dernier import dans sidebar

## Mission 106 — CI/CD HF Spaces Docker
**DATE: 2026-03-30 | ACTOR: CLAUDE | STATUS: ✅ LIVRÉ (CODE DIRECT)**
- `Dockerfile` : FROM python:3.11-slim, port 7860, USER 1000, start_hf.sh
- `start_hf.sh` : cd "Frontend/3. STENCILER" && uvicorn server_v3:app --port 7860
- `requirements.hf.txt` : dépendances allégées (sans playwright, llama-index)
- `.github/workflows/deploy-hf.yml` : push main → git push hf-space main --force
- `README.md` : metadata YAML HF Spaces (sdk: docker, app_port: 7860)
- Compte HF : FJDaz | Repo GitHub : https://github.com/FJDaz/homeos

## Session 2026-03-30/31 — Missions livrées
**DATE: 2026-03-30 → hotfix 2026-03-31**

| Mission | Notes |
|---|---|
| M97 | Wire UX v2 — table bijective + diagnostic géographique |
| M98 | Wire UX v3 — skeleton mode |
| M99 | Wire UX v4 — peel-out CSS + pop-in Monaco + route wire-source |
| M100 | Landing Import — hub Figma SVG + rafraîchir/vider |
| M100-bis | Hub universel — drop multi-format + manifest check + sélection écrans |
| M101-bis | Bridge Plugin — conformité design HoméOS |
| M102 | Intent Viewer — auto-load + endpoint import-analysis + liens frd-editor |
| M103 | Wire v5 — auto-launch + overlay bijectif bilan/plan |
| M104 | Stitch Integration — backend.md + intent_map + Monaco drawer |
| M105 | Aperçu local — rendu 1:1 dans un onglet indépendant |
| M106 | CI/CD HF Spaces — Dockerfile, start_hf.sh, deploy-hf.yml |
| M107 | Navigation globale — bootstrap.js auto-contenu, tabs HoméOS |
| M109A | Font Classifier — Vox-ATypI via Panose + Bézier stress/contraste |
| M109B | Font WebGen — Subset Latin + WOFF2 + @font-face CSS |

## CR Mission 107 — Navigation globale cohérente
**DATE: 2026-03-30 → hotfix 2026-03-31 | ACTOR: GEMINI + CLAUDE | STATUS: ✅ LIVRÉ**
- `bootstrap.js` auto-contenu : CSS embarqué, 4 tabs (brainstorm/backend/frontend/deploy), brand homéOS
- Tab actif via pathname, `window.HOMEOS.refreshNav()` exposé
- `frd_editor.css` : `.global-pipeline-header { position: fixed }` pour layout `h-screen`
- Hotfix Claude : version Gemini initiale sans CSS → rendu texte brut + emojis non conformes

## CR Mission 109A — Font Classifier
**DATE: 2026-03-31 | ACTOR: CLAUDE (CODE DIRECT) | STATUS: ✅ LIVRÉ**
- `font_classifier.py` : Panose → SERIF_TO_VOX (ids lowercase conformes typography_db.json)
- Analyse Bézier contours `o` : outer+inner → stress_angle_deg, contrast_ratio
- sub_family Linéales séparé de vox_atypi (grotesque/geometrique/humaniste)
- Fallback post.italicAngle + heuristique panose[1]

## CR Mission 109B — Font WebGen
**DATE: 2026-03-31 | ACTOR: CLAUDE (CODE DIRECT) | STATUS: ✅ LIVRÉ**
- `font_webgen.py` : subset Latin + WOFF2 + @font-face CSS
- Fix Subsetter API : `populate(glyphs=...)` (pas `.glyphs =`)
- Fix WOFF2 flavor : `font.flavor = "woff2"` avant save
- Routes `server_v3.py` : POST /api/sullivan/font-upload, GET /api/sullivan/fonts, DELETE /api/sullivan/fonts/{slug}

## CR Mission 100-bis — Landing : hub universel d'import
**DATE: 2026-03-30 | ACTOR: GEMINI + CLAUDE | STATUS: ✅ LIVRÉ**
- Drop multi-format SVG/ZIP/TSX/HTML/CSS/JS, manifest creation, sélection écrans
- Routes : POST /api/import/upload, GET+POST /api/manifest/check|create|get

## CR Mission 103 — Wire mode v5
**DATE: 2026-03-30 | ACTOR: GEMINI + CLAUDE | STATUS: ✅ LIVRÉ**
- Auto-trigger wire mode, overlay biface Bilan↔Plan, bouton IMPLÉMENTER LE PLAN

## CR Mission 104 — Stitch Integration
**DATE: 2026-03-30 | ACTOR: CLAUDE + GEMINI | STATUS: ✅ LIVRÉ**
- backend.md Source of Truth, import design.md→backend.md, Monaco drawer landing


## CR Mission 127 — Workspace V1 (Shell + Canvas Engine)
**DATE: 2026-04-01 | ACTOR: GEMINI (HTML/CSS) + CLAUDE (JS) | STATUS: ✅ LIVRÉ**
- Shell `workspace.html` + `workspace.css` fidèle à `screen.png` Stitch
- Canvas SVG infini : zoom molette centré curseur, pan space+drag
- `WsCanvas.js` : `addScreen()` (iframe + drag), `removeScreen()` (DELETE API)
- `WsChat.js` : toggle CONSTRUCT/WIRE, upload `+` → `POST /api/import/upload` → `addScreen()`
- Route `GET /workspace` dans `server_v3.py`
- Landing : bouton "ouvrir dans workspace" via `POST /api/frd/set-current`

## CR Mission 129 — Workspace Features Layer 2
**DATE: 2026-04-01 | ACTOR: GEMINI + CLAUDE | STATUS: ✅ LIVRÉ (partiels M130-B/C)**
- Panel Screens flottant gauche : liste + collapse → badge, re-clic → rouvre
- Panel Audit UX : collapse → badge "AUDIT UX", transition
- Toolbar verticale droite : 4 outils (select, drag, image, frame), état actif #A3CD54
- Screens affichent le contenu HTML réel via `iframe src=/api/frd/file?name=`
- Fix conflit scroll/zoom : `handleWheel` guard `e.target.closest()`

## CR Mission 130-A — Header Minimal + Mode Aperçu Plein Écran
**DATE: 2026-04-01 | ACTOR: CLAUDE | STATUS: ✅ LIVRÉ**
- Retrait des boutons Aperçu/Save du header global
- `#ws-preview-overlay` : inset 0, z-index 35, sans border ni shadow
- `enterPreviewMode()` + `exitPreviewMode()` dans `ws_main.js`
- Classe `body.preview-mode` : masque panels et bouton FRD editor
- Sullivan et toolbar maintenus au-dessus (z-index supérieur)

## CR Mission 130-B — Boutons Aperçu & Save par Screen
**DATE: 2026-04-01 | ACTOR: CLAUDE | STATUS: ✅ LIVRÉ**
- Bouton "Aperçu" (texte + icône 4 flèches) dans le bandeau de chaque screen (y=50, hors zone drag)
- Bouton "SAVE" pilule verte HoméOS dans le bandeau (y=52)
- `enterPreviewMode(screenId)` : iframe brute plein écran, zéro padding/shadow
- `POST /api/frd/save` avec feedback visuel opacité
- `e.stopPropagation()` sur mousedown et click pour éviter le drag conflict
- Fix critique : rétablissement de `fo.appendChild(iframe)` supprimé par inadvertance

## CR Mission 130-C — Fix Robuste Panneaux Latéraux
**DATE: 2026-04-01 | ACTOR: CLAUDE | STATUS: ✅ LIVRÉ**
- `togglePanel()` simplifié : `classList.toggle('collapsed')` uniquement, CSS gère tout
- Transition `max-height` (0→800px) + opacity pour les panneaux
- Transition `max-height` (0→50px) + opacity pour les badges
- Wrappers stables `#section-screens` et `#section-audit` pour isoler les flux de layout
- Délai 50ms sur apparition du badge pour permettre au panneau de libérer l'espace d'abord
- Headers panels cliquables sur toute leur surface (`onclick` sur la div entière)
- Libellés badges repassés à l'horizontale (suppression de `vertical-text`)


## CR Mission 144 — Export projet + @font-face dans les screens
**DATE: 2026-04-02 | ACTOR: CLAUDE (CODE DIRECT) | STATUS: ✅ LIVRÉ**
- Route `GET /api/frd/export-zip?import_id=` : génère ZIP avec HTML + fontes WOFF2 injectées
- Bouton téléchargement (↓) dans le bandeau de chaque screen canvas
- WsFontManager.js : injection des `@font-face` dans les iframes à l'ouverture

## CR Mission 145 — Renommage UI : BRS → Cadrage + tabs renommés
**DATE: 2026-04-02 | ACTOR: CLAUDE (CODE DIRECT) | STATUS: ✅ LIVRÉ**
- Renommage complet BRS → Cadrage dans bootstrap.js + workspace.html
- Pipeline 4 onglets : Cadrage / Backend / Frontend / Déploiement
- Aucune occurrence "BRS" ou "Brainstorm" visible dans l'UI

## CR Mission 146 — Détection manifeste → routage Wire ou Cadrage
**DATE: 2026-04-02 | ACTOR: CLAUDE (CODE DIRECT) | STATUS: ✅ LIVRÉ**
- Route `GET /api/frd/manifest?import_id=` : détecte `projects/{active}/manifests/manifest_{id}.json`
- Retourne `{ exists: true, manifest: {...} }` ou `{ exists: false }`
- WsCanvas.js : badge "cadrage requis" si pas de manifeste, bouton Wire si manifeste présent

## CR Mission 148 — Bridge @font-face : fontes système → iframes screens
**DATE: 2026-04-02 | ACTOR: CLAUDE (CODE DIRECT) | STATUS: ✅ LIVRÉ**
- Route `POST /api/sullivan/generate-webfont { font_name }` : scan macOS Fonts + génère WOFF2
- Cache d'indexation système pour supprimer latence de scan
- applyTypo() : `setProperty('font-family', font, 'important')` via currentSelector (scope graft)
- Injection `@font-face` directe dans `iframe.contentDocument` (pas via postMessage)
- Override Tailwind descendants via `<style id="ws-typo-override">` avec `selector, selector * { !important }`

## CR Mission 151 — Auto-génération manifeste à l'import HTML
**DATE: 2026-04-02 | ACTOR: CLAUDE (CODE DIRECT) | STATUS: ✅ LIVRÉ**
- `import_upload()` : appel ManifestInferer + ArchetypeDetector après écriture HTML
- Génère `projects/{active}/manifests/manifest_{id}.json` avec `components[]` + `archetype`
- Try/except silencieux : un échec Playwright ne bloque jamais l'upload
- Wire overlay lit `manifest.components` (pas `manifest.screens`)

## CR Mission 152 — Sullivan context complet : tous les screens canvas + DESIGN.md
**DATE: 2026-04-02 | ACTOR: CLAUDE (CODE DIRECT) | STATUS: ✅ LIVRÉ**
- WsChat.js : collecte `canvas_screens[]` depuis tous les `.ws-screen-shell` sauf l'actif
- server_v3.py : `max_tokens=16384` (fix blank screen War Room 23KB)
- Injection DESIGN.md (scan `get_active_project_path()/DESIGN.md`, 4000 chars max)
- Sullivan reçoit : screen actif (complet) + autres screens (6000 chars chacun, max 3) + DESIGN.md

## CR Mission 154 — Sullivan : focus élément sélectionné dans le prompt
**DATE: 2026-04-03 | ACTOR: CLAUDE (CODE DIRECT) | STATUS: ✅ LIVRÉ**
- WsChat.js : capture `wsInspect.currentSelector` → lit `el.outerHTML` depuis `iframe.contentDocument`
- Envoie `selected_element: { selector, tag, html }` dans la requête `/api/sullivan/chat`
- server_v3.py : `SullivanChatRequest.selected_element` + bloc `selected_block` injecté avant `context_html_block`
- Sans sélection → `selected_block` vide, comportement inchangé

## CR Mission 130 — Mode Inspect In-Preview & Monaco Popover
**DATE: 2026-04-01 | ACTOR: GEMINI | STATUS: ✅ LIVRÉ**
- Injection inspecteur dans l'iframe preview (highlight survol, clic → sélection)
- Popover Monaco flottant au flanc de l'élément cliqué (bounding client rect)
- Grafting : outerHTML modifié → remplacement propre du nœud DOM
- Design bulle Monaco aligné HoméOS

## CR Mission 131 — Exclusivité des Outils en Mode Aperçu & Nettoyage
**DATE: 2026-04-01 | ACTOR: GEMINI | STATUS: ✅ LIVRÉ**
- Toolbar droite activée uniquement en mode aperçu (`enterPreviewMode`)
- Suppression des boutons "Aperçu" redondants dans header principal

## CR Mission 140 — Boutons Aperçu & Save dans le header de chaque screen canvas
**DATE: 2026-04-01 | ACTOR: CLAUDE (CODE DIRECT) | STATUS: ✅ LIVRÉ**
- Bouton "Aperçu" + bouton "SAVE" dans le bandeau SVG de chaque screen
- `enterPreviewMode(screenId)` depuis le bouton + `e.stopPropagation()` anti-drag
- `POST /api/frd/save` avec feedback visuel opacité

## CR Mission 141 — Suppression d'imports depuis le panel Screens
**DATE: 2026-04-01 | ACTOR: CLAUDE (CODE DIRECT) | STATUS: ✅ LIVRÉ**
- Bouton ✕ sur chaque import card (ws-main.js)
- `DELETE /api/imports/{id}` en backend (server_v3.py)
- Suppression immédiate du card + du shell canvas correspondant

## CR Mission 143 — Sullivan UI Compact : 2 bulles visibles
**DATE: 2026-04-02 | ACTOR: GEMINI | STATUS: ✅ LIVRÉ**
- `#ws-chat-history` : max-h réduit, overflow hidden — 2 bulles max visibles
- WsChat.js : trim des bulles > 2 après chaque appendBubble()
- Panel Sullivan ≤ 160px de hauteur totale

## CR Mission 142 — Sullivan Actions : édition directe du screen actif
**DATE: 2026-04-02 | ACTOR: CLAUDE (CODE DIRECT) | STATUS: ✅ LIVRÉ**
- WsChat.js : capture screen_html (iframe srcdoc ou fetch src) → envoi à Sullivan
- `POST /api/sullivan/chat` : Gemini reçoit HTML + génère version modifiée
- Parsing `---EXPLANATION--- / ---HTML--- / ---END---` dans la réponse
- WsCanvas.updateActiveScreenHtml() : applique HTML retourné sur l'iframe active

## CR Mission 132 — Outils de Manipulation (Drag, Déplacer, Cadre, Place Image)
**DATE: 2026-04-01 | ACTOR: GEMINI | STATUS: ✅ LIVRÉ**
- Flèche de sélection : Drag d'éléments DOM dans l'iframe preview.
- Outil Hand : Panning dans la vue.
- Outil Cadre : Insertion de `<div>` par clic-glissé.
- Outil Place Image : Insertion d'images via file picker.

## CR Mission 133 — Undo & Color Picker Libre
**DATE: 2026-04-01 | ACTOR: GEMINI | STATUS: ✅ LIVRÉ**
- Pile d'historique (Undo) : Cmd+Z pour annuler les modifications DOM.
- Outil Color Apply : Color picker TSL sémantique basé sur DESIGN.md.

## CR Mission 134 — Arsenal Typo (System Fonts & Webfont Generator)
**DATE: 2026-04-01 | ACTOR: GEMINI | STATUS: ✅ LIVRÉ**
- Outil Texte : Création de zones de texte dans l'aperçu.
- Sélecteur System Fonts : Accès aux polices locales (Font Access API).
- Hook Sauvegarde : Génération automatique de @font-face via Backend.

## CR Mission 156 — Refactor WsCanvas : découpe hexagonale en 5 modules
**DATE: 2026-04-03 | ACTOR: GEMINI | STATUS: ✅ LIVRÉ**
- Découpe de WsCanvas.js (683L → 198L).
- Création de WsAudit.js, WsForge.js, WsPreview.js, WsScreenShell.js.
- Fix HCI (Boucle infinie) : document.write statique sans scripts dans WsPreview.
- Persistance Sullivan : fallback sur _lastSullivanHtml dans WsChat.

---

## Mission 117 — Fusion Intent → FRD : Analyse Intégrée
**STATUS: ✅ LIVRÉ**
**DATE: 2026-03-31 | ACTOR: GEMINI (frontend) + CLAUDE (backend updates)**
- Analyse intégrée dans l'éditeur FRD.
- Branchement des intentions sur les composants détectés.

## Mission 119 — Pont React/ZIP → Tailwind Direct
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-01 | ACTOR: GEMINI (react_to_tailwind.py) + CLAUDE (routes.py)**
- Conversion directe de composants React/ZIP vers Tailwind.
- Support du pattern `svg_to_tailwind.py`.

## Mission 127 — Workspace V1 (Shell + Canvas Engine)
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-01 | ACTOR: GEMINI**
- Moteur de canvas SVG de base.
- Système de shell pour les écrans.

## Mission 129 — Workspace : features layer 2
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-01 | ACTOR: GEMINI**
- Améliorations UX du canvas.
- Layer 2 des fonctionnalités de manipulation.

## Mission 130 — Mode Aperçu, Panneaux & Monaco Popover
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-01 | ACTOR: GEMINI**
- Mission 130-A : Header Minimal + Mode Aperçu Plein Écran.
- Mission 130-B : Boutons Aperçu & Save par Screen.
- Mission 130-C : Fix Robuste Panneaux Latéraux.
- Mission 130 : Mode Inspect In-Preview & Monaco Popover.

## Mission 131 — Exclusivité des Outils en Mode Aperçu & Nettoyage
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-01 | ACTOR: GEMINI**

## M298 — Double contexte student / user : pont FK + project panel filtré
**STATUS: ✅ LIVRÉ | DATE: 2026-04-13 | ACTOR: QWEN (Back) + CLAUDE (Front fixes)**

**Backend :**
- Migration 006 : `students.user_id` FK → `users(id)` + index (applied SQLite)
- `auth_router.py` : `_get_student_user_id` / `_set_student_user_id` helpers (write-once FK)
- `auth_login_student` : écrit `students.user_id` au login (backfill idempotent)
- `auth_register` : idem pour la branche student
- `projects_router.py` : requête UNION — projets perso (`user_id = ?`) + sujet assigné (`students.project_id` via subquery)
- Suppression de `OR user_id IS NULL` — retournait TOUS les projets legacy
- `class_router.py` : forcé SQLite (Supabase schema désynchronisé)

**Frontend :**
- `WsProjectPanel.js` : envoie `X-User-Token` header, trace de session
- `WsStitchDrill.js` : bouton step 4 wired, `hide()` supprime overlay du DOM, déduplication bouton upload
- `ManifestBox.js` : `hide()` + `toggle()` ajoutés (ReferenceError fix), `loadDesignTokens` orphelin retiré
- `_finishButton(container)` — helper unique pour le bouton "Commencer à travailler" (4 occurrences → 1)
- Nettoyage des outils et focus sur le mode aperçu.

## Mission 299 — RM : Résolution conflit merge WsStitchDrill.js
**STATUS: ✅ LIVRÉ | DATE: 2026-04-13 | ACTOR: GEMINI**

- Résolution mécanique des 3 conflits de merge identifiés.
- Respect strict de la règle "HEAD gagne" sur les blocs ,  et .
- Restauration de la validité syntaxique du fichier JS.
- Vérification par `grep` : zéro marqueur de conflit restant.

## Mission 302 — Groq wrapper : injection de fichiers dans le contexte
**STATUS: ✅ LIVRÉ | DATE: 2026-04-13 | ACTOR: GEMINI**

- Identification du wrapper `code` (bash) comme source du script temporaire `groq-versatile.py`.
- Mise à jour du template `cat <<EOF` dans le script `code`.
- Ajout de la boucle `sys.argv[1:]` pour lire les fichiers passés en arguments.
- Injection automatique du contenu des fichiers dans le contexte `user` de Groq avant le REPL.
- Validation avec `./code code` : injection fonctionnelle et confirmée par message de succès.

## Mission 303 — Diagnostic Système : DB Leak + Race Condition JSON
**STATUS: ✅ LIVRÉ | DATE: 2026-04-14 | ACTOR: QWEN (GEMINI-AUX)**

- Context manager `bkd_db()` : fermeture systématique des connexions SQLite.
- `_write_json_locked()` avec `fcntl.flock` : élimination des race conditions sur `active_project.json`.
- Migration de tous les appels internes vers `bkd_db()` (bkd_service.py, routers concernés).

## Mission 304 — DB comme seule source de vérité pour le projet actif
**STATUS: ✅ LIVRÉ | DATE: 2026-04-14 | ACTOR: Claude CODE DIRECT**

- WAL mode SQLite (`PRAGMA journal_mode=WAL` + `PRAGMA synchronous=NORMAL`) : lectures concurrentes sans bloquer les écritures.
- `get_active_project_id(token)` : résolution token-aware — `students.project_id` en DB si token présent, fallback `active_project.json` sinon.
- `activate_project` : met à jour `students.project_id` via pattern matching `WHERE ? LIKE class_id || '-' || id || '%'` même sans token enseignant.
- `bkd_router.py` + `stitch_router.py` : import migré vers `bkd_db` (context manager).

## Mission 305 — Frontend Resilience : Guards & Timeouts
**STATUS: ✅ LIVRÉ | DATE: 2026-04-14 | ACTOR: GEMINI**

- `teacher_dashboard.html` : `setInterval` → `setTimeout` récursif (refresh storm impossible) + verrou `_loadDashboardPending`.
- `WsStitchDrill.js` : `AbortController` 5000ms sur `isCanvasEmpty()` — le drill ne peut plus freezer indéfiniment si le backend est sous charge RAG.

## Mission 306 — Débloquer l'event loop : async def → def sur les handlers SQLite-only
**STATUS: ✅ LIVRÉ | DATE: 2026-04-14 | ACTOR: Claude CODE DIRECT**

Cause racine du freeze serveur : handlers `async def` avec SQLite synchrone bloquaient l'event loop uvicorn entier.

- `routers/class_router.py` : 16 conversions `async def` → `def` (list_classes, class_dashboard, list_students, import_roster, start_student_project, update_milestone, detect_student_milestone, student_pre_eval, create_class, update_class, delete_class, create_subject, get_subject, update_subject, deploy_student_render, list_subjects).
- `routers/projects_router.py` : 14 conversions (get_active_project_route, activate_project, get_active_manifest_route, get_active_logic_js, list_all_projects_route, create_project_route, delete_project_route, get_project_manifest_route, update_project_manifest_route, add_project_wire_route, get_design_tokens, genome_compile, genome_read, get_project_context_route).

**Validation :** 5 requêtes parallèles `/api/classes` → 5×200, zéro timeout.


---

**Fichier 1 : `routers/class_router.py`**

Identifier tous les handlers `async def` dans ce fichier. Pour chacun :
- S'il contient un `await` → laisser `async def`
- S'il ne contient que du SQLite / file I/O / logique pure → changer en `def`

Handlers à convertir (vérifier `await` absent) :
`list_classes`, `get_class`, `create_class`, `list_students`, `add_student`, `delete_student`,
`get_dashboard`, `create_student_project_route`, `list_subjects`, `add_subject`, `delete_subject`

**Fichier 2 : `routers/projects_router.py`**

Même règle. Handlers à inspecter :
`list_all_projects_route`, `get_project`, `delete_project`, `get_project_manifest`,
`update_project_manifest`, `get_project_genome`, `get_project_context`

**ATTENTION — ne pas convertir :**
- Tout handler qui fait `await` (appels LLM, streaming, websocket)
- `get_active_project_route` — vient d'être modifié en M304, laisser `async def`
- `activate_project` — idem

---

**Contraintes :**
- Ne modifier QUE la signature (`async def` → `def`). Ne pas toucher le corps des fonctions.
- Si un handler a `async def` + `await` → laisser intact, ne pas toucher.
- Ne pas modifier `server_v3.py`, `bkd_service.py`, ni les autres routers.

**Test de validation :**
```bash
# Après restart, simuler 5 requêtes dashboard en parallèle
for i in {1..5}; do curl -s -o /dev/null -w "%{http_code}\n" http://localhost:9998/api/classes/dnamde3/dashboard & done; wait
# Attendu : cinq 200, pas de timeout
```

**Livraison :** les deux fichiers modifiés + résultat du test parallèle.

---

**Diagnostic à effectuer :**

1. Lancer le serveur et ouvrir `/teacher`.
2. Charger une classe → noter si la première requête `/api/classes/{class_id}/dashboard` répond.
3. Changer de classe immédiatement → observer si la deuxième requête répond ou timeout.
4. Inspecter la console browser (Network tab) : est-ce un 504 / timeout / réponse vide ?
5. Côté serveur : chercher des `print` ou logs d'erreur sur chaque requête dashboard.

**Hypothèses à valider :**

- A. `detect_milestone()` itère sur `imports_dir.iterdir()` et `exports_dir.iterdir()` — si un dossier contient beaucoup de fichiers, ça peut être lent pour N étudiants en séquence. Vérifier avec un timer.
- B. Connexion SQLite `bkd_db_con` — verrou si deux requêtes concurrentes touchent la même base. FastAPI async + SQLite synchrone = risque de lock.
- C. La boucle `for s in students` fait un `UPDATE students SET milestone=?` par étudiant si le milestone a changé → N writes séquentiels en contexte async. Regrouper en une seule transaction.

---

**Fix 2 — Clés API : stockage Fernet (AES-128 symétrique)**

Fichier : `Frontend/3. STENCILER/core/key_resolver.py` (lire avant de toucher — il existe déjà).

Créer un helper `crypto_keys.py` dans `Frontend/3. STENCILER/core/` :
```python
from cryptography.fernet import Fernet
import os

def _get_fernet() -> Fernet:
    key = os.getenv("FERNET_KEY")
    if not key:
        raise RuntimeError("FERNET_KEY manquante dans .env — générer avec: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"")
    return Fernet(key.encode())

def encrypt_key(plain: str) -> str:
    return _get_fernet().encrypt(plain.encode()).decode()

def decrypt_key(token: str) -> str:
    return _get_fernet().decrypt(token.encode()).decode()
```

Modifier `stitch_router.py` — `_get_stitch_key()` : déchiffrer à la lecture.
Modifier toute route qui fait `INSERT INTO user_keys` : chiffrer à l'écriture.

**Migration DB :** les clés en clair existantes sont invalides avec Fernet. Ajouter une colonne `encrypted BOOLEAN DEFAULT 0` dans `user_keys`. À la lecture : si `encrypted=0` → retourner en clair + re-chiffrer + mettre `encrypted=1`. Migration transparente sans downtime.

---

---

### Mission 110 — Templates FRD : liste vide
**STATUS: 🔴 HOTFIX | DATE: 2026-03-31**
- [ ] Diagnostic `#template-select` vide après manifest minimal