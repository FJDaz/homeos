# MISSION CONTROL : AETHERFLOW ROADMAP

> Missions complètes archivées dans [ROADMAP_ACHIEVED.md](./ROADMAP_ACHIEVED.md).

---

## Mission 85 — FastAPI Foundation : squelette server_v3.py + routes BKD

**STATUS: ✅ LIVRÉ — Amendment appliqué (Claude)**
**DATE: 2026-03-24**
**ACTOR: GEMINI + CLAUDE**
**MODE: aetherflow -f + CODE DIRECT**

### Contexte

`server_9998_v2.py` = monolithe ~2830 lignes `BaseHTTPRequestHandler`. Exceptions avalées, routing illisible, imports dynamiques cachant les bugs. Migration FastAPI en shadow mode — `server_v3.py` tourne sur port **9999** pendant la transition.

### Bootstrap Gemini

```
Tu es un expert Python backend. Tu génères server_v3.py dans Frontend/3. STENCILER/.
Lire server_9998_v2.py pour comprendre la structure existante.
Lire sullivan_arbitrator.py pour le wiring Arbitrator.
Lire .env (via _load_env pattern) pour les clés API.
```

### Livrables attendus

- `server_v3.py` : FastAPI + uvicorn, port 9999
- Lifespan : `_load_env()`, init `SullivanArbitrator`, init DB Sullivan, init RAG
- `SullivanArbitrator` = dépendance FastAPI (`Depends`)
- Routes portées : toutes les `/api/bkd/*` + `/api/sullivan/pulse`
- Exceptions = `HTTPException` (pas de catch silencieux)
- Pydantic models pour les body BKD

### Critères de sortie

- [ ] `python3 server_v3.py` → port 9999, pas d'erreur
- [ ] `POST /api/bkd/chat` → Sullivan répond ✅
- [ ] `GET /api/bkd/projects` ✅
- [ ] `GET /api/sullivan/pulse` ✅
- [ ] `/docs` Swagger accessible ✅

### Correction : MIMO

Si Gemini produit du code cassé : MiMo (`mimo-v2-flash`) patch les erreurs de syntaxe / imports manquants.

### Validation finale : CLAUDE

Claude relit, teste avec curl, valide ou écrit AMENDMENT.

---

## Mission 86 — FastAPI FRD : `/api/frd/*` + fix bug 500

**STATUS: ✅ LIVRÉ — Amendment appliqué (Claude)**
**DATE: 2026-03-24**
**ACTOR: GEMINI + CLAUDE**
**MODE: aetherflow -f + CODE DIRECT**

### Contexte

Routes FRD ont un bug 500 silencieux sur `/api/frd/chat` (mode `construct` + fichier nommé). FastAPI exposera la vraie stacktrace et permettra de corriger proprement.

### Bootstrap Gemini

```
Lire server_v3.py (sortie M85) pour la structure FastAPI existante.
Lire server_9998_v2.py lignes 1283→1575 (handlers FRD actuels).
Lire static/templates/frd_editor.html lignes 910→930 (payload envoyé).
```

### Livrables attendus

- Porter dans `server_v3.py` : `/api/frd/chat`, `/api/frd/wire`, `/api/frd/files`, `/api/frd/file`, `/api/frd/assets`
- Fichiers statiques et templates HTML (`/static/*`, `/stenciler`, `/frd-editor`)
- Porter `/api/infer_layout`
- Corriger le bug mode `construct` (import `load_manifest` ou logique cassée)

### Critères de sortie

- [ ] `POST /api/frd/chat` → 200, Sullivan répond ✅
- [ ] `POST /api/frd/wire` → patch HTML ✅
- [ ] `/stenciler` et `/frd-editor` servis ✅

### Correction : MIMO — Validation : CLAUDE

---

## Mission 87-A — FastAPI : Genome + Layout + fichiers statiques

**STATUS: ✅ LIVRÉ — Hotfix port 9999 (Claude)**
**DATE: 2026-03-24**
**ACTOR: GEMINI + CLAUDE**
**MODE: aetherflow -f + CODE DIRECT**

### Bootstrap Gemini

```
Lire server_v3.py (état M86) pour la structure FastAPI existante.
Lire server_9998_v2.py — cibler uniquement les routes ci-dessous.
Ne pas toucher aux routes BKD/FRD déjà portées.
```

### Livrables attendus

Porter dans `server_v3.py` :
- Fichiers statiques : `/`, `/sw.js`, `/preview`, `/template`, `/brainstorm`, `/brainstorm-tw`, `/stenciler_v3`, `/genome_canvas`, `/intent-viewer`
- Genome API : `GET/POST /api/genome`, `GET /api/layout`, `POST /api/manifest`, `POST /api/manifest/patch`, `GET /api/lexicon`
- Organ/Comp : `POST /api/organ-move`, `POST /api/comp-move`, `POST /api/comp-resize`
- `POST /api/pedagogy/gaps`

### Critères de sortie

- [ ] `GET /` → viewer.html ✅
- [ ] `GET /api/genome` → JSON génome ✅
- [ ] `POST /api/manifest` → 200 ✅

### Correction : MIMO — Validation : CLAUDE

---

## Mission 87-B — FastAPI : BRS (Brain-Reasoning System)

**STATUS: ✅ LIVRÉ (Gemini)**
**DATE: 2026-03-24**
**ACTOR: GEMINI**
**MODE: aetherflow -f**

### Bootstrap Gemini

```
Lire server_v3.py (état M87-A).
Lire server_9998_v2.py — cibler uniquement /api/brs/*.
```

### Livrables attendus

Porter dans `server_v3.py` :
- `POST /api/brs/capture`
- `POST /api/brs/dispatch`
- `POST /api/brs/rank`
- `POST /api/brs/generate-prd`
- `GET/POST /api/brs/buffer-questions`

### Critères de sortie

- [ ] `POST /api/brs/capture` → 200 ✅
- [ ] `POST /api/brs/dispatch` → réponse LLM ✅

### Correction : MIMO — Validation : CLAUDE

---

## Mission 87-C — FastAPI : Retro-Genome (le plus lourd)

**STATUS: ✅ LIVRÉ partiel (Gemini) — routes critiques présentes, validate/reality/generate-prd manquantes**
**DATE: 2026-03-24**
**ACTOR: GEMINI**
**MODE: aetherflow -f**

### Bootstrap Gemini

```
Lire server_v3.py (état M87-B).
Lire server_9998_v2.py — cibler uniquement /api/retro-genome/*.
Attention : uploads multipart (upload, upload-svg), exports ZIP (export-zip).
```

### Livrables attendus

Porter dans `server_v3.py` :
- `GET/POST /api/retro-genome/manifest`
- `POST /api/retro-genome/chat`
- `POST /api/retro-genome/validate`
- `POST /api/retro-genome/approve`
- `POST /api/retro-genome/reality`
- `POST /api/retro-genome/upload` (multipart)
- `POST /api/retro-genome/upload-svg`
- `POST /api/retro-genome/generate-html`
- `POST /api/retro-genome/generate-prd`
- `POST /api/retro-genome/export-manifest`
- `POST /api/retro-genome/export-schema`
- `POST /api/retro-genome/export-zip`

### Critères de sortie

- [ ] `POST /api/retro-genome/chat` → 200 ✅
- [ ] `POST /api/retro-genome/upload` → fichier sauvegardé ✅
- [ ] `POST /api/retro-genome/export-zip` → ZIP téléchargeable ✅

### Correction : MIMO — Validation : CLAUDE

---

## Mission 87-D — Bascule port 9998 + archivage

**STATUS: ✅ LIVRÉ (Claude)**
**DATE: 2026-03-24**
**ACTOR: CLAUDE**
**MODE: CODE DIRECT — FJD**

### Livrables attendus

- `server_v3.py` : changer port 9999 → 9998
- Killer `server_9998_v2.py` (processus)
- Déplacer `server_9998_v2.py` → `static/_archive/server_9998_v2.py`
- Mettre à jour `API_CONTRACT.md` avec toutes les nouvelles routes FastAPI

### Critères de sortie

- [ ] `localhost:9998` → server_v3.py répond ✅
- [ ] `server_9998_v2.py` archivé ✅
- [ ] `API_CONTRACT.md` à jour ✅
- [ ] FRD editor + BKD chat fonctionnels sur port 9998 ✅

---

## Mission 90 — BKD : route `/api/bkd/files` + explorateur réel dans bkd_frd.html

**STATUS: 🟡 PRÊT**
**DATE: 2026-03-24**
**ACTOR: CLAUDE (route backend) + GEMINI (frontend)**
**MODE: CODE DIRECT — FJD**

### Contexte

`bkd_frd.html` charge les projets via `/api/bkd/projects` mais l'explorateur est hardcodé avec des fichiers fictifs (`Main.ts`, `Components/`, `Styles/`). Il manque une route `/api/bkd/files?project_id=xxx` pour lister les vrais fichiers du répertoire du projet. `GET /api/bkd/file` et `POST /api/bkd/file` existent déjà dans `server_v3.py`.

### Livrable CLAUDE — `server_v3.py`

Ajouter la route :
```
GET /api/bkd/files?project_id={id}
→ Retourne la liste des fichiers du projet (récursif, extensions autorisées BKD_ALLOWED_EXTENSIONS)
→ Format : { "files": [ { "path": "src/main.py", "name": "main.py", "ext": ".py" }, ... ] }
→ Exclure BKD_EXCLUDE_DIRS
→ 404 si project_id inconnu
```

### Livrable GEMINI — `bkd_frd.html`

Remplacer le chargement hardcodé par un appel réel :
- Au démarrage : `GET /api/bkd/projects` → prend `projects[0].id` → `GET /api/bkd/files?project_id={id}` → populate l'explorateur avec les vrais fichiers
- Clic sur un fichier dans l'explorateur : `GET /api/bkd/file?project_id={id}&path={path}` → affiche dans `#editor-content`
- Bootstrap : lire `static/templates/bkd_frd.html` (état actuel) + `Frontend/1. CONSTITUTION/API_CONTRACT.md`

### Critères de sortie

- [ ] `GET /api/bkd/files?project_id=4c29163f-...` → liste les fichiers d'AetherFlow ✅
- [ ] Explorateur dans le browser affiche les vrais fichiers du projet ✅
- [ ] Clic sur un fichier → contenu affiché dans l'éditeur ✅

### Validation : CLAUDE (curl) + FJD (visuel)

---

## Mission 75-A — BKD Frontend : bkd_editor.html

**STATUS: 🟡 PRÊT**
**DATE: 2026-03-24**
**ACTOR: MIMO (wire audit) + GEMINI (frontend) + CLAUDE (hotfix route)**
**MODE: aetherflow -vfx (Gemini) + CODE DIRECT (Claude)**

### Contexte

Architecture validée (Décision 2026-03-23) :
- `code-server` dans un `<iframe>` → éditeur VS Code complet (port 8080)
- Sidebar droite Sullivan BKD → chat via `POST /api/bkd/chat` (port 9998)
- Accessible via `GET /bkd` (route à ajouter en hotfix Claude)

### Audit Wire (MiMo — à exécuter en premier)

MiMo analyse le codebase en mode wire avant que Gemini génère le HTML :

```
Lire server_v3.py lignes 213-235 (pattern de service des templates HTML).
Lire bkd_service.py lignes 48-65 (SULLIVAN_BKD_SYSTEM — capacités de Sullivan BKD).
Lire static/templates/frd_editor.html (structure de référence : layout 3 colonnes, chat JS).
Produire : liste des dépendances JS/CSS à linker, structure DOM recommandée, payload POST /api/bkd/chat exact.
```

### Bootstrap Gemini

```
Lire static/templates/frd_editor.html — pattern layout + chat JS vanilla à réutiliser.
Lire static/css/stenciler.css — SEULE source de vérité design (tokens V1, warm neutrals, Geist 12px).
Lire Frontend/1. CONSTITUTION/LEXICON_DESIGN.json — classes atomiques et data attributes.
Lire Frontend/1. CONSTITUTION/API_CONTRACT.md — section Domaine BKD pour payload exact.
NE PAS linker viewer.css (incompatible).
NE PAS générer de Python/backend.
```

### Livrables

**Claude (hotfix)** — `server_v3.py` : ajouter route `GET /bkd` → sert `bkd_editor.html`

**Gemini** — `static/templates/bkd_editor.html` :
- Layout 2 colonnes : iframe code-server (flex: 1) + sidebar Sullivan (280px)
- Header : titre "BKD — La Forge" + indicateur pulse Sullivan
- Iframe : `src="http://localhost:8080"`, `allow="clipboard-read;clipboard-write"`
- Sidebar : chat history scrollable + input `Enter` → `POST /api/bkd/chat` → affiche `data.text`
- Tokens CSS : `var(--bg-primary)`, `var(--sidebar-width)`, `var(--header-height)`, etc.
- JS vanilla uniquement, pas de framework

### Critères de sortie

- [ ] `GET http://localhost:9998/bkd` → `bkd_editor.html` servi ✅
- [ ] Iframe code-server visible (même si port 8080 vide → about:blank acceptable en test) ✅
- [ ] Chat Sullivan : `POST /api/bkd/chat` → réponse affichée dans la sidebar ✅
- [ ] Tokens stenciler.css respectés (pas de couleurs hardcodées) ✅

### Correction : MIMO — Validation : CLAUDE + FJD (visuel)

---

## Mission 88 — Refactorisation frd_editor.html V3 modulaire

**STATUS: 🟡 PRÊT**
**DATE: 2026-03-24**
**ACTOR: CLAUDE**
**MODE: CODE DIRECT — FJD**

### Contexte

`frd_editor.html` = 1348 lignes monolithiques (CSS inline + HTML + JS). Impossible à déboguer, à auditer par un agent, et en contradiction avec la règle V3 (< 300L par fichier). Toute la logique Sullivan/KIMI/Wire/Monaco/Assets/Preview est emmêlée dans un seul bloc `<script>`.

Objectif : découper sans changer aucune logique. Comportement identique avant/après. Aucune régression.

### Architecture cible

```
Frontend/3. STENCILER/
├── static/
│   ├── css/
│   │   └── frd_editor.css              (styles extraits du <style> inline)
│   └── js/
│       └── frd/
│           ├── frd_main.js             (init + wiring, ~80L)
│           ├── FrdEditor.feature.js    (Monaco + locks + template selector, ~250L)
│           ├── FrdChat.feature.js      (Sullivan chat + mode toggle + audit, ~250L)
│           ├── FrdKimi.feature.js      (KIMI design workflow, ~120L)
│           ├── FrdWire.feature.js      (Wire/Codestral diagnostic, ~80L)
│           ├── FrdAssets.feature.js    (assets + drag/drop + ZIP, ~200L)
│           └── FrdPreview.feature.js   (live preview + inspect hover, ~150L)
└── templates/
    └── frd_editor.html                 (~80L — template pur + imports)
```

### Règles de découpe

- **Zéro régression logique** — copier/extraire uniquement, pas réécrire
- **Bypass `__NativeFetch`** — conserver dans `frd_editor.html` en premier `<script>` (avant tout import)
- **ES6 modules** — chaque feature exporte ses fonctions publiques, `frd_main.js` les importe et les wire aux événements DOM
- **State partagé** — `_chatMode`, `_chatHistory`, `_htmlHistory`, `_zipMode`, `editorHTML` → exposés via `frd_main.js` ou passés en paramètre
- **`frd_editor.css`** — extraire tel quel le bloc `<style>` actuel, linker via `<link>`
- **Aucun changement CSS, HTML, ou logique** — FJD valide visuellement

### Livrables

- [ ] `frd_editor.css` créé ✅
- [ ] 6 features créées, chacune < 300L ✅
- [ ] `frd_main.js` orchestre l'init ✅
- [ ] `frd_editor.html` réduit à ~80L (template + `<link>` + `<script type="module">`) ✅
- [ ] `GET /frd-editor` → rendu identique visuellement ✅
- [ ] Sullivan chat répond (mode `construct` et `conseil`) ✅
- [ ] Wire fonctionne ✅
- [ ] KIMI flow intact ✅

### Validation : FJD (visuel) + curl Sullivan

---

## Mission 89 — Sullivan FRD : simplification UI + Wire→Construct pipeline

**STATUS: 🟡 PRÊT**
**DATE: 2026-03-24**
**ACTOR: GEMINI**
**MODE: CODE DIRECT — FJD**

### Contexte

L'UI Sullivan FRD a 4 boutons de mode dont 2 (DESIGN, COUNCIL) n'ont jamais fonctionné. Des modifications partielles cassées ont été appliquées et doivent être consolidées. Le mode Wire doit produire un diagnostic + plan d'implémentation, et permettre de transférer ce plan à Construct d'un clic.

### Bootstrap Gemini

```
Lire static/js/frd/FrdChat.feature.js — état actuel à corriger.
Lire static/js/frd/FrdWire.feature.js — état actuel à enrichir.
Lire static/templates/frd_editor.html — état actuel UI.
Lire Frontend/1. CONSTITUTION/SULLIVAN_INTERACTIONS.md — patterns JS vanilla toggles/panels.
```

### Livrables

**`frd_editor.html`** :
- Garder uniquement 2 boutons : `#toggle-construct` (CONSTRUCT) et `#toggle-wire` (WIRE)
- Supprimer `#toggle-design` et `#toggle-conseil`
- Vérifier que `#chat-input`, `#btn-send`, `#chat-history` sont présents et intacts

**`FrdChat.feature.js`** :
- `setMode(mode)` : gérer uniquement `'construct'` et `'wire'`
- En mode `construct` : activer le bouton CONSTRUCT, désactiver WIRE, placer placeholder correct
- En mode `wire` : activer le bouton WIRE, désactiver CONSTRUCT, afficher `#wire-panel`
- Ne PAS masquer `#wire-panel` quand on bascule vers construct (conserver le plan visible)
- Conserver `triggerSilentAudit()` intact (appelé par FrdEditor)
- Conserver `updateAuditPanel()` intact
- Dans `send()` : supprimer les branches `/design` et `/conseil`
- Dans `send()` : convertir `role: 'model'` → `role: 'assistant'` dans l'historique

**`FrdWire.feature.js`** :
- Après affichage du diagnostic dans `#wire-content`, injecter sous ce div un bouton `#wire-apply-btn` : "→ Implémenter le plan"
- Click sur ce bouton : `this.main.chat.setMode('construct')` + pré-remplir `#chat-input` avec `"Voici le plan Wire — implémente le JS correspondant :\n" + data.diagnostic` + focus sur `#chat-input`
- Conserver `(window.__NativeFetch || fetch)` sur le fetch wire

### Critères de sortie

- [ ] Interface : 2 boutons seulement (CONSTRUCT / WIRE), textarea et Envoyer présents ✅
- [ ] `triggerSilentAudit()` ne lève pas d'erreur JS ✅
- [ ] Wire affiche diagnostic + plan, panel reste visible en mode Construct ✅
- [ ] Bouton "→ Implémenter le plan" → bascule Construct + pré-remplit input ✅
- [ ] Chat Construct répond sans 500 sur 2e requête ✅

### Validation : FJD (visuel) + Cmd+Shift+R

---

## Mission 91 — API Generator Engine : retro-genome → FastAPI routes

**STATUS: ✅ LIVRÉ (Claude, 2026-03-25) — archivé dans ROADMAP_ACHIEVED.md**
**DATE: 2026-03-25**
**ACTOR: CLAUDE**
**MODE: aetherflow -f**

### Contexte

Aujourd'hui toutes les routes de `server_v3.py` sont écrites à la main. Or le retro-genome dispose déjà de la chaîne complète :

```
interface (HTML/SVG/Figma)
  → manifest_inferer.py      # détecte les entités, intents, régions
  → archetype_detector.py    # identifie l'archetype (ide_like, chatbot_pro, dashboard…)
  → functional_archetypes.json  # chaque archetype a suggested_endpoints[]
```

Il manque le dernier maillon : **`api_generator.py`** — un moteur qui prend un manifest + son archetype et génère le code Python FastAPI correspondant.

**Objectif** : MVP prouvable en 1 run. Un CLI qui, à partir d'un manifest.json, produit un `router_{name}.py` importable dans `server_v3.py`.

### Architecture cible

```
Backend/Prod/retro_genome/
└── api_generator.py          # nouveau — moteur de génération
```

**Entrées** :
- `manifest.json` (depuis `exports/retro_genome/` ou path CLI)
- `functional_archetypes.json` (lookup archetype → suggested_endpoints)
- `af_metadata_schema.json` (types d'entités → paramètres Pydantic)

**Sortie** : fichier Python `router_{project_slug}.py` contenant :
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/{slug}", tags=["{slug}"])

# Généré depuis archetype: ide_like
@router.get("/fs/tree")
async def get_fs_tree():
    """[auto] Liste l'arborescence de fichiers — archetype ide_like"""
    raise HTTPException(status_code=501, detail="Not implemented")

@router.post("/fs/save")
async def post_fs_save(body: FsSaveRequest):
    """[auto] Sauvegarde un fichier — archetype ide_like"""
    raise HTTPException(status_code=501, detail="Not implemented")
...
```

### Logique de génération

```python
def generate(manifest_path: str, output_path: str):
    manifest = load_json(manifest_path)
    archetype_id = manifest.get("archetype_id") or detect_archetype(manifest)
    archetype = lookup_archetype(archetype_id)            # functional_archetypes.json
    endpoints = archetype["suggested_endpoints"]           # ex: ["GET /api/fs/tree", ...]
    entities  = extract_entities(manifest)                 # depuis data-af-intent + data-af-id

    routes = []
    for endpoint in endpoints:
        method, path = endpoint.split(" ", 1)
        handler_name = path_to_handler(method, path)      # "GET /api/fs/tree" → "get_fs_tree"
        body_model   = infer_body_model(method, path, entities)  # POST → Pydantic model
        routes.append(RouteSpec(method, path, handler_name, body_model))

    write_router_file(routes, archetype, output_path)
```

### Critères de sortie (preuve obligatoire)

**Test A — pipeline complet sur `bkd_frd.html`** :
```bash
# 1. Inférer le manifest depuis bkd_frd.html
python -m retro_genome.manifest_inferer \
  --input Frontend/3.\ STENCILER/static/templates/bkd_frd.html \
  --output /tmp/manifest_bkd.json

# 2. Générer les routes
python -m retro_genome.api_generator \
  --manifest /tmp/manifest_bkd.json \
  --output /tmp/router_bkd.py

# 3. Vérifier le contenu
cat /tmp/router_bkd.py
```

**Attendu** : routes générées incluent au minimum les équivalents de :
- `GET /api/bkd/files` (file explorer → archetype ide_like)
- `POST /api/bkd/chat` (chat Sullivan → archetype chatbot_pro)

**Test B — importabilité** :
```bash
python -c "import ast; ast.parse(open('/tmp/router_bkd.py').read()); print('✅ Syntaxe Python valide')"
```

**Test C — cohérence avec server_v3.py** :
Extraire les routes générées, comparer avec les routes existantes dans server_v3.py. Le rapport doit identifier :
- Routes générées présentes dans server_v3 ✅ (validation)
- Routes générées absentes → candidats à implémenter 🔵
- Routes server_v3 non couvertes → hors archetype (normal) ℹ️

### Bootstrap Claude (aetherflow -f)

```
Lire Backend/Prod/retro_genome/functional_archetypes.json — source des suggested_endpoints.
Lire Backend/Prod/retro_genome/af_metadata_schema.json — attributs data-af-* pour inférer les Pydantic models.
Lire Backend/Prod/retro_genome/archetype_detector.py — comprendre comment l'archetype est détecté.
Lire Backend/Prod/retro_genome/manifest_inferer.py — format du manifest en sortie.
Lire Frontend/3. STENCILER/server_v3.py lignes 1-50 — pattern FastAPI APIRouter de référence.
```

### Livrables

- [ ] `Backend/Prod/retro_genome/api_generator.py` — moteur CLI fonctionnel ✅
- [ ] Test A passe → `/tmp/router_bkd.py` généré ✅
- [ ] Test B passe → syntaxe Python valide ✅
- [ ] Test C rapport affiché dans le terminal ✅

### Validation : CLAUDE (run CLI) + FJD (lecture rapport)

---

## Mission 75-B — Extension VS Code `aetherflow-bkd`

**STATUS: 🔵 BACKLOG**
**DATE: 2026-03-23**
**ACTOR: CLAUDE**
**MODE: CODE DIRECT — FJD**

### Livrables
- WebviewPanel Majordome (chat Sullivan dans VS Code)
- WebviewPanel Roadmap viewer (ROADMAP.md rendu)
- Message passing : fichier actif dans VS Code → Sullivan BKD context

---

## Mission 75-C — Dockerfile code-server

**STATUS: 🔵 BACKLOG**
**DATE: 2026-03-23**
**ACTOR: CLAUDE**
**MODE: CODE DIRECT — FJD**

### Livrables
- Dockerfile basé sur `codercom/code-server:latest`
- Extensions pré-installées : Roo Code, GitLens, aetherflow-bkd
- Docker image fonctionnelle en local (`docker run -p 8080:8080`)
