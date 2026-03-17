# MISSION CONTROL : AETHERFLOW ROADMAP

> Missions complètes archivées dans [ROADMAP_ACHIEVED.md](./ROADMAP_ACHIEVED.md).

---

## Mission 54 — FRD Editor : KIMI Job Queue + Polling (Fix inject.js timeout)

**STATUS: 🔴 À FAIRE**
**DATE: 2026-03-17**
**ACTOR: GEMINI + CLAUDE (backend)**
**MODE: CODE DIRECT — FJD**
**FICHIERS :**
- `Frontend/3. STENCILER/server_9998_v2.py` — routes KIMI job queue
- `Frontend/3. STENCILER/static/templates/frd_editor.html` — client polling

---

### Diagnostic Root Cause

inject.js (extension Chrome AetherFlow) monkey-patch `window.fetch` avec un timeout interne ~30-60s.
Sullivan (`/api/frd/chat`) répond en <10s → passe.
KIMI (`/api/frd/kimi`) prend 4-8 min → inject.js abandonne la promesse fetch avant réponse serveur.
Le serveur répond bien 200, mais le code client ne voit jamais la réponse.
XHR confirmé idem : inject.js intercepte aussi `XMLHttpRequest`.

### Solution : Job Queue + Polling

Remplacer le fetch long-running par un pattern en deux étapes :
1. `POST /api/frd/kimi/start` → lance KIMI en background thread, retourne immédiatement `{ job_id }`
2. `GET /api/frd/kimi/result/{job_id}` → retourne `{ status: "pending" }` ou `{ status: "done", label, html }` ou `{ status: "error", error }`
3. Client poll toutes les 5s — chaque fetch dure < 1s, inject.js ne peut pas timeout

### Backend — `server_9998_v2.py`

#### Données partagées (thread-safe)
```python
import threading, uuid

_kimi_jobs = {}          # { job_id: { status, label, html, error } }
_kimi_jobs_lock = threading.Lock()
```

#### Route `POST /api/frd/kimi/start`
```python
# Lire { instruction, html }
# Générer job_id = str(uuid.uuid4())[:8]
# Enregistrer _kimi_jobs[job_id] = { "status": "pending" }
# Lancer threading.Thread(target=_run_kimi_job, args=(job_id, instruction, html), daemon=True).start()
# Retourner immédiatement : { "job_id": job_id }
```

#### Fonction `_run_kimi_job(job_id, instruction, html)`
Contient le code KIMI actuel (strip scripts, appel NVIDIA, parse label+html).
À la fin :
```python
with _kimi_jobs_lock:
    _kimi_jobs[job_id] = { "status": "done", "label": label, "html": html }
# En cas d'erreur :
    _kimi_jobs[job_id] = { "status": "error", "error": str(e) }
```
Cleanup : supprimer les jobs > 30 min du dict.

#### Route `GET /api/frd/kimi/result/{job_id}`
```python
# path: /api/frd/kimi/result/JOBID
# Extraire job_id depuis self.path
# Retourner _kimi_jobs.get(job_id, { "status": "not_found" })
```

### Frontend — `frd_editor.html`

#### `sendKimi(instruction)`
```js
// POST /api/frd/kimi/start → { job_id }
// Lancer _pollKimi(job_id)
```

#### `_pollKimi(job_id)` — polling toutes les 5s
```js
async function _pollKimi(job_id) {
    const res = await fetch('/api/frd/kimi/result/' + job_id);
    const data = await res.json();
    if (data.status === 'done') {
        appendKimiBubble(data.label, data.html);
        // cleanup overlay, _kimiInProgress = false
    } else if (data.status === 'error') {
        appendBubble('Erreur KIMI : ' + data.error, 'sullivan');
        // cleanup
    } else {
        // pending → re-poll dans 5s
        setTimeout(() => _pollKimi(job_id), 5000);
    }
}
```

#### Panel de diagnostic (optionnel, collapsible dans Sullivan pane)
Petite barre de statut sous le header Sullivan :
- `● IDLE` / `⟳ KIMI job_id en cours (Xs)` / `✓ KIMI done` / `✗ KIMI error`
- Mis à jour à chaque poll

### Critères de sortie
- [ ] `POST /api/frd/kimi/start` retourne `{ job_id }` en < 1s
- [ ] Background thread démarre KIMI sans bloquer le serveur
- [ ] Client poll toutes les 5s → bulle KIMI apparaît ~5s après fin traitement
- [ ] Barre de statut visible dans Sullivan pane pendant le traitement
- [ ] Sullivan (Gemini) non perturbé
- [ ] Aucun fetch ne dure > 5s → inject.js ne peut pas timeout

### Bootstrap Gemini
Fournir en input :
- `frd_editor.html` complet (client actuel)
- `server_9998_v2.py` section route KIMI (~L661-760)
Gemini implémente : `_pollKimi`, status bar, `sendKimi` modifié.
Claude implémente : routes backend `start` + `result` + `_run_kimi_job`.

---

## Mission 53 — FRD Editor : Fix KIMI Pipeline (Debug & Stabilisation)

**STATUS: ✅ TERMINÉ**
**DATE: 2026-03-17**
**ACTOR: CLAUDE (CODE DIRECT — FJD)**

---

### Contexte

KIMI est intégré via NVIDIA NIM (`moonshotai/kimi-k2.5`, `https://integrate.api.nvidia.com/v1/chat/completions`).
La clef NVIDIA est dans `.env` : `NVIDIA_NIM_API_KEY` (ou `NVIDIA_API_KEY` en fallback).
Le trigger actuel : mode DESIGN actif (toggle UI) OU message préfixé `/design`.
La commande `/design` seule bascule le mode persistant. `/construct` le remet en CONSTRUCT.

**État actuel cassé** — KIMI ne répond pas / ne produit pas de variante utilisable. Causes probables identifiées :

#### Bug 1 — `applyKimiVariant` : index corrompu
`variantId = 'variant-${Date.now()}-0'` → `split('-').pop()` retourne `'0'` (string).
`window._lastKimiVariants['0']` fonctionne en JS (accès objet) mais devient silencieusement `undefined` si `_lastKimiVariants` est réinitialisé entre deux appels KIMI (plusieurs bulles dans le chat). Le lookup est sur le DERNIER appel uniquement — cliquer sur une ancienne bulle plante sans message.

**Fix :** stocker les variants dans un `Map` indexé par `Date.now()` (l'identifiant de batch) et chercher par batch + index, pas juste par index.

#### Bug 2 — Régression `updatePreview()` (résolue mais à vérifier)
Un patch récent a temporairement stripé les `<script>` dans `updatePreview()`. Revert effectué. Vérifier que `updatePreview()` reçoit bien `editorHTML.getValue()` sans transformation.

#### Bug 3 — `setMode` : boutons toggle manquants ou inconsistants
La fonction `setMode()` existe mais les boutons `#toggle-construct` / `#toggle-design` peuvent manquer du DOM si un précédent revert a perturbé le HTML. Vérifier que les deux boutons sont dans la section `<!-- Input area -->` et que `setMode('construct')` est appelé à l'init pour l'état visuel par défaut.

#### Bug 4 — Parsing réponse KIMI : format non respecté
KIMI k2.5 est créatif dans ses réponses. Le parser actuel cherche `---VARIANT \d---` mais KIMI peut répondre avec des variantes numérotées différemment ou ajouter du texte avant le premier marqueur. Si `variants` est vide, le frontend affiche "KIMI n'a pas pu générer de variantes valides" sans détail.

**Fix :** ajouter logging serveur du `raw_text` reçu (50 premiers chars) pour diagnostic, et rendre le parser plus tolérant (fallback : si aucun `---VARIANT` trouvé mais qu'il y a un `---HTML---`, considérer comme 1 variant anonyme).

#### Bug 5 — Timeout réel vs annoncé
Avec `max_tokens: 4096` et 1 variante, le timeout devrait être ~30-60s. Mais le overlay dit "patience (~60s)" et la variable `_kimiInProgress` bloque les appels suivants pendant 180s si KIMI timeout côté serveur (Python lève `urllib.error.URLError: timed out`). Le frontend ne reçoit rien pendant 180s puis un 500 KIMI error.

**Fix :** réduire timeout Python à 90s (suffisant pour 4096 tokens), et dans le frontend afficher un message de timeout distinct si l'erreur est "timed out".

---

### Tâches

#### Backend `server_9998_v2.py`

- [ ] **T1** : Log `raw_text[:200]` reçu de KIMI (print serveur) pour diagnostic
- [ ] **T2** : Parser plus tolérant — fallback si pas de `---VARIANT \d---` mais présence `---HTML---`
- [ ] **T3** : Timeout Python : `90` (pas 180)
- [ ] **T4** : Retourner dans la réponse JSON un champ `debug_raw` (50 chars) en mode dev pour affichage côté frontend en cas d'échec parsing

#### Frontend `frd_editor.html`

- [ ] **T5** : `applyKimiVariant` — remplacer `window._lastKimiVariants` par `window._kimiVariantMap` (Map) :
  ```js
  // À la création de la bulle :
  const batchId = Date.now();
  window._kimiVariantMap = window._kimiVariantMap || new Map();
  window._kimiVariantMap.set(batchId, variants);
  // variantId = `variant-${batchId}-${i}`

  // Dans applyKimiVariant(variantId) :
  const parts = variantId.split('-');
  const idx = parseInt(parts.pop());
  const batchId = parseInt(parts.slice(1).join('-'));
  const variants = window._kimiVariantMap.get(batchId);
  const variant = variants ? variants[idx] : null;
  ```
- [ ] **T6** : Vérifier présence `#toggle-construct` + `#toggle-design` dans le HTML, ajouter si manquants
- [ ] **T7** : Appeler `setMode('construct')` à l'init (après Monaco load) pour état visuel cohérent
- [ ] **T8** : En cas d'erreur KIMI incluant "timed out", afficher "KIMI timeout — réessaie avec une instruction plus courte." au lieu de "Erreur de connexion à KIMI."
- [ ] **T9** : Si `data.variants.length === 0` ET `data.debug_raw`, afficher dans la bulle KIMI : "Parsing échoué. Réponse brute : [debug_raw]"

---

### Critères de sortie
- Mode DESIGN activé → message envoyé → overlay KIMI → bulle avec 1 variante apparaît
- Click "Appliquer le design" → Monaco se met à jour, preview se rafraîchit
- Click sur une ancienne bulle KIMI (session multi-appels) → applique la bonne variante (pas de silent fail)
- Timeout KIMI → message explicite dans le chat, `_kimiInProgress` remis à `false`
- `/design` + `/construct` dans le chat → basculent le mode + confirment dans le chat

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

## Mission 50 — FRD Editor UX Improvements

**STATUS: ✅ TERMINE**
**DATE: 2026-03-16**
**ACTOR: ANTIGRAVITY**

### Réalisations
- **Sullivan Loader** : Overlay de chargement et bulle d'attente "Sullivan travaille...".
- **Resizable Monaco** : Ajout d'une poignée de redimensionnement entre l'éditeur et la preview.
- **Toggle Workspace** : Bouton [≡] pour replier/déplier l'éditeur (340px ↔ 0).
- **Selection Highlight** : Clic sur un élément HTML dans Monaco → focus et contour vert fluo dans la preview.

---

## Mission 51 — Asset Upload (Drag & Drop → Sullivan Context)

**STATUS: ✅ TERMINE**
**DATE: 2026-03-16**
**ACTOR: ANTIGRAVITY**

### Objectif
Permettre l'upload direct d'images dans le panel Sullivan pour enrichir le contexte Gemini.

### Réalisations
- **Assets Zone** : Zone de drop dédiée dans le panel Sullivan.
- **Backend Robuste** : Upload multipart compatible Python 3.14 (sans module `cgi`).
- **Context Injection** : Sullivan reçoit la liste des URLs des assets uploadés dans son prompt système pour pouvoir les référencer dans le HTML.
- **Thumbnails UX** : Visualisation immédiate, suppression d'un clic, copie URL au presse-papier.

![Success Verification Asset Upload](file:///Users/francois-jeandazin/.gemini/antigravity/brain/27df21fb-7905-436d-b9ad-ee1498340997/mission_51_final_verification_success_1773684542495.webp)

---

## Mission 52 — FRD Editor : Commande `/design` → KIMI Design Critic

**STATUS: ✅ TERMINÉ** *(voir M53 pour stabilisation)*
**DATE: 2026-03-16**
**ACTOR: ANTIGRAVITY**

### Objectif
Intégrer KIMI (via NVIDIA NIM) comme expert design capable de proposer des variantes de layout via la commande `/design`.

### Réalisations
- **Design Mode** : Détection du préfixe `/design` dans le chat Sullivan.
- **KIMI Integration** : Route `/api/frd/kimi` interfaçant l'API NVIDIA (Kimi 2.5).
- **Variant Bubble** : Affichage de 3 propositions sous forme de tuiles foncées (style premium).
- **One-Click Apply** : Injection immédiate du variant dans Monaco + rafraîchissement preview.
- **Fallback & Robustesse** : Chargement automatique du `.env` et gestion des timeouts.

### Critères de sortie
- [x] `/design` seul dans le chat → bulle KIMI avec 3 tuiles preview apparaît
- [x] `/design réduis la densité` → KIMI reçoit l'instruction + le HTML courant
- [x] Click [Appliquer] sur une tuile → Monaco se met à jour + preview se rafraîchit
- [x] `NVIDIA_API_KEY` absente → message d'erreur dans la bulle, pas de crash
- [x] Sullivan normal (sans `/design`) non perturbé

#### Backend — `server_9998_v2.py`

**Route : `POST /api/frd/kimi`**

```python
# Lire body : { instruction: str, html: str }
# Construire prompt KIMI (voir format ci-dessus)
# Appel NVIDIA API :
#   url = "https://integrate.api.nvidia.com/v1/chat/completions"
#   headers = { "Authorization": f"Bearer {os.environ.get('NVIDIA_API_KEY')}", "Content-Type": "application/json" }
#   payload = { "model": "nvidia/llama-3.1-nemotron-ultra-253b-v1", "messages": [...], "max_tokens": 8192 }
# Parser la réponse → extraire 3 blocs ---VARIANT N--- / LABEL / ---HTML---
# Retourner { "variants": [{ "label": "...", "html": "..." }, ...] }
# Si NVIDIA_API_KEY absent → { "error": "NVIDIA_API_KEY non configurée" }
```

> Note : Le modèle exact peut varier selon la disponibilité NVIDIA. Paramètre configurable en tête de route. Fallback acceptable : 1 seul variant si le parsing échoue.

#### Frontend — `frd_editor.html`

**Détection commande dans `sendChat()` :**
```js
async function sendChat() {
  const message = chatInput.value.trim();
  if (!message) return;

  if (message.startsWith('/design')) {
    const instruction = message.slice(7).trim(); // texte après /design
    await sendKimi(instruction);
    return;
  }
  // ... flow Sullivan habituel
}
```

**Fonction `sendKimi(instruction)` :**
```js
async function sendKimi(instruction) {
  appendMessage('user', instruction ? `/design ${instruction}` : '/design');
  showOverlay('KIMI analyse le layout...');
  try {
    const res = await fetch('/api/frd/kimi', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ instruction, html: editorHTML.getValue() })
    });
    const data = await res.json();
    if (data.error) { appendMessage('error', data.error); return; }
    appendKimiVariants(data.variants);
  } catch (e) {
    appendMessage('error', e.message);
  } finally {
    hideOverlay();
  }
  chatInput.value = '';
}
```

**Rendu bulle KIMI `appendKimiVariants(variants)` :**
```js
function appendKimiVariants(variants) {
  const div = document.createElement('div');
  div.className = 'kimi-bubble'; // styles ci-dessous
  div.innerHTML = `
    <div class="kimi-header">🎨 KIMI — ${variants.length} proposition${variants.length > 1 ? 's' : ''}</div>
    <div class="kimi-tiles">
      ${variants.map((v, i) => `
        <div class="kimi-tile">
          <iframe srcdoc="${escapeHtml(v.html)}" class="kimi-preview" scrolling="no"></iframe>
          <div class="kimi-label">${v.label}</div>
          <button class="kimi-apply" onclick="applyKimiVariant(${i})">Appliquer</button>
        </div>
      `).join('')}
    </div>
  `;
  div._variants = variants; // stocker pour applyKimiVariant
  document.getElementById('chat-history').appendChild(div);
  div.scrollIntoView({ behavior: 'smooth' });
  window._lastKimiVariants = variants; // accès global pour applyKimiVariant
}

function applyKimiVariant(index) {
  const v = window._lastKimiVariants[index];
  if (!v) return;
  editorHTML.setValue(v.html);
  updatePreview();
}
```

**CSS bulle KIMI** (ajouter dans `<style>`) :
```css
.kimi-bubble {
  background: #1a1a2e;
  border-radius: 6px;
  padding: 10px;
  margin: 8px 0;
}
.kimi-header {
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 8px;
}
.kimi-tiles {
  display: flex;
  gap: 8px;
}
.kimi-tile {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.kimi-preview {
  width: 100%;
  height: 80px;
  border: 1px solid #333;
  transform-origin: top left;
  pointer-events: none;
}
.kimi-label {
  color: #ccc;
  font-size: 9px;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.kimi-apply {
  background: #8cc63f;
  color: #fff;
  border: none;
  padding: 3px 6px;
  font-size: 9px;
  cursor: pointer;
  border-radius: 3px;
  width: 100%;
}
.kimi-apply:hover { background: #7ab535; }
```

### Versioning — Snapshot avant application

Avant tout `[Appliquer]`, auto-sauvegarder le HTML courant dans un historique local. L'utilisateur n'a pas à penser à sauvegarder.

```js
let _kimiHistory = []; // stack LIFO, max 10 entrées

function applyKimiVariant(index) {
  const v = window._lastKimiVariants[index];
  if (!v) return;
  // Snapshot avant écrasement
  _kimiHistory.push(editorHTML.getValue());
  if (_kimiHistory.length > 10) _kimiHistory.shift();
  // Afficher bouton Annuler si caché
  document.getElementById('kimi-undo-btn').style.display = 'flex';
  editorHTML.setValue(v.html);
  updatePreview();
}

function undoKimi() {
  if (!_kimiHistory.length) return;
  editorHTML.setValue(_kimiHistory.pop());
  updatePreview();
  if (!_kimiHistory.length) document.getElementById('kimi-undo-btn').style.display = 'none';
}
```

**Bouton Annuler** — pastille flottante en bas du panel Sullivan, visible uniquement après un [Appliquer] :
```html
<div id="kimi-undo-btn"
     style="display:none; position:sticky; bottom:8px; left:0; right:0;
            margin:4px 8px; background:#1a1a2e; color:#ccc;
            font-size:9px; padding:4px 8px; border-radius:4px;
            cursor:pointer; align-items:center; gap:6px; justify-content:center;"
     onclick="undoKimi()">
  ↩ Revenir au layout précédent
</div>
```

Comportement :
- Apparaît après le premier `[Appliquer]`
- Disparaît quand l'historique est vide (après N annulations)
- Multiple annulations possibles (max 10 niveaux)
- N'interfère pas avec le Save — le Save reste une action explicite FJD

### Contraintes
- `NVIDIA_API_KEY` lue depuis `os.environ` — pas hardcodée
- Parsing robuste : si un variant ne parse pas, l'ignorer silencieusement (pas de crash)
- `escapeHtml()` sur les HTML avant injection dans `srcdoc` pour éviter les XSS
- Les iframes KIMI sont `pointer-events: none` (preview read-only)
- La commande `/design` fonctionne avec ou sans instruction : `/design` seul = "propose 3 directions" ; `/design réduis la densité` = contrainte passée à KIMI

### Bootstrap Gemini
Fournir `frd_editor.html` complet en input.
Gemini implémente : `sendKimi()`, `appendKimiVariants()`, CSS `.kimi-*`, détection `/design` dans `sendChat()`.
Claude implémente : route `POST /api/frd/kimi` dans `server_9998_v2.py`.

### Critères de sortie
- [ ] `/design` seul dans le chat → bulle KIMI avec 3 tuiles preview apparaît
- [ ] `/design réduis la densité` → KIMI reçoit l'instruction + le HTML courant
- [ ] Click [Appliquer] sur une tuile → Monaco se met à jour + preview se rafraîchit
- [ ] Bouton "↩ Revenir" apparaît après [Appliquer] → annulation vers le layout précédent
- [ ] Multi-niveaux d'annulation (≤ 10) fonctionnels
- [ ] `NVIDIA_API_KEY` absente → message d'erreur dans la bulle, pas de crash
- [ ] Sullivan normal (sans `/design`) non perturbé

---

## BACKLOG

- [ ] **MISSION 41B** : SVG BACKPLANE GENERATOR — `svg_backplane.py` : manifest enrichi → SVG annoté af-metadata, exportable Figma
- [ ] **MISSION 41C** : ROUTINE SVG ILLUSTRATOR — `_parse_illustrator_svg()` dans `svg_parser.py`.
  Stratégie "extract-first, Vision-last" : extraire mécaniquement `fill`/`stroke`/`rect`/`<g>`, Vision uniquement pour labelliser `name`/`inferred_intent`/`apparent_role`. Vision ne remplace jamais les valeurs déjà extraites. Déclenchement Vision : `source == 'illustrator'` ET `len(regions) < 2`.
- [ ] **MISSION 42** : MIGRATION FASTAPI — Remplacer `server_9998_v2.py` (~1200L, ~40 routes) par FastAPI/Uvicorn pour déployabilité (Railway, Docker). `retro_genome/routes.py` déjà en FastAPI → `app.include_router()`. Mission lourde — découper par domaine (genome, retro-genome, statics, exports).
- [ ] **MISSION 27** : CHATBOT PÉDAGOGIQUE (GEMINI API)
- [ ] **MISSION 26** : RAG ENGINE SYSTEM
- [ ] **MISSION 29** : CONTRÔLEUR HOMEOS NATIVE (EMBED FIGMA + GUI RETRO-GENOME)
