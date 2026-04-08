# MISSION CONTROL : AETHERFLOW ROADMAP

> Missions complètes archivées dans [ROADMAP_ACHIEVED.md](./ROADMAP_ACHIEVED.md).

---

## 🧠 BOOTSTRAP GEMINI — À inclure dans TOUTE mission frontend

```
CONTEXTE TECHNIQUE OBLIGATOIRE — lis avant de coder :

1. DIAGNOSTIC DOM AVANT LISTENER
   Avant d'ajouter un event listener, remonte la chaîne du DOM :
   - Quel élément est réellement cliqué ? (e.target)
   - Y a-t-il un élément enfant `absolute inset-0` qui intercepte les clics avant le parent ?
   - Si oui → ajouter `pointer-events-none` sur l'intercepteur, puis le listener sur le parent.
   - Tester avec : `element.addEventListener('click', e => console.log(e.target))` avant tout patch.

2. OVERLAYS & Z-INDEX
   Un overlay `hidden` sur un parent = ses enfants sont invisibles même si LEUR hidden est retiré.
   Toujours vérifier : `getComputedStyle(el).display` et `el.offsetHeight` avant de déboguer le JS.

3. RÈGLE DE LIVRAISON
   Ne pas marquer TERMINÉ avant d'avoir testé manuellement le comportement dans le browser.

4. SCOPE STRICT
   Ne pas refactoriser les fichiers existants stables sans instruction explicite.

5. STYLE HOMÉOS
   Pas de majuscules dans les labels UI. Pas d'emojis. Border-radius max `rounded-[20px]`.
   Vert HoméOS (#8cc63f) uniquement en nudge — jamais en fond large.
```

---

## Phase Active (2026-04-07)

### Thème 0 — Hotfixes
> M121 ✅, M116 ✅, M122–127 ✅ — archivées ROADMAP_ACHIEVED.md

---

### Thème 7 — Wire → Cadrage

> M147 ✅, M181 ✅, M183 ✅, M185 ✅, M186 absorbée M187, M187 ✅, M184 ✅, M188 (dashboard) ✅ — archivées

### Mission 188 — Wire : Aperçu fonctionnel post-forge
**STATUS: 🟠 PRÊTE**
**DATE: 2026-04-06 | ACTOR: GEMINI**

Bouton "tester" dans l'overlay Wire post-forge → `window.open('/api/frd/file?name={name}&raw=1&wire=1')`.
- `server_v3.py` : si `wire=1`, retourner HTML brut sans tracker
- `WsWire.js` : bouton cliquable après `_executeForge` succès

---

### Mission 182-A — Wire : organes du manifest dans le tableau
**STATUS: 🟠 PRÊTE**
**DATE: 2026-04-06 | ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE

Diagnostic console d'abord :
```js
fetch('/api/projects/active/wire-audit').then(r=>r.json()).then(d=>console.log('audit:', d.audit?.length, d.audit))
```
- `audit.length === 6` → modifier `WsWire.js _renderBilan()`
- `audit.length === 0` → modifier route `wire-audit` dans `server_v3.py`

**Livrable :** tableau Wire affiche 6 lignes d'organes.

---

### Mission 182-B — Wire : bouton "activer le plan"
**STATUS: 🔵 EN ATTENTE 182-A | ACTOR: GEMINI**

Cliquer `#ws-wire-apply-plan` → champ chat se remplit → Sullivan répond. Inspecter `WsWire.js` autour de `btnApplyPlan.onclick`.

---

### Mission 180 — Rebranchement WiRE dans cadrage_alt
**STATUS: 🔴 PRIORITÉ**
**DATE: 2026-04-05 | ACTOR: GEMINI**

- [ ] Shell `#ws-wire-overlay` dans `cadrage_alt.html`
- [ ] Chargement `WsWire.js` + `WsInspect.js`
- [ ] Déclenchement diagnostic z-index au clic `.wire`

---

### Mission 149 — Canvas N0 : États de sélection + toolbar
**STATUS: 🟠 PRÊTE | DATE: 2026-04-02**
- [ ] États CSS (hover, selected, dragging)
- [ ] WsCanvas.js : notifyToolbar, cursor

---

### Mission 150 — Retour Cadrage : session pré-alimentée
**STATUS: 🟠 PRÊTE | DATE: 2026-04-02**
- [ ] Route `POST /api/cadrage/init-context`
- [ ] Badge "contexte wire chargé" dans Cadrage UI

---

### Mission 153 — Undo Sullivan
**STATUS: 🔵 EN COURS — GEMINI | DATE: 2026-04-03**
- [ ] WsCanvas.js : snapshot avant update
- [ ] Bouton Undo dans le header workspace

---

### Mission 155 — Bouton Stop Sullivan
**STATUS: 🟠 PRÊTE | DATE: 2026-04-03**
- [ ] WsChat.js : AbortController + bouton Stop UI

---

### Thème 8 — Système Miroir
> M158 ✅, M159 ✅, M160 ✅, M161 ✅ — archivées

**Dette technique post-M158 :**
1. `Canvas.feature.js` (53KB) : Découplage moteur SVG / Zoom-Pan
2. `sullivan_renderer.js` (33KB) : Migration DOM Factory → composants DESIGN.md
3. `semantic_bridge.js` (19KB) : Simplification routage Sullivan → FEE

---

### Thème 9 — Multi-Projet
> M162 ✅, M163 ✅, M164 ✅, M165 ✅ — archivées

---

### Thème 10 — Design System

### Mission 167 — DESIGN.md HoméOS
**STATUS: ✅ LIVRÉ | ACTOR: FJD + CLAUDE**
`Frontend/1. CONSTITUTION/DESIGN.md` — Colors, Typography, Shape, Effects, Spacing, Tone, Forbidden.

---

### Mission 170 — BEHAVIOR_SULLIVAN.md
**STATUS: 🟠 PRÊTE**
**DATE: 2026-04-06 | ACTOR: FJD + CLAUDE**
**Dépendance : M167**

- [ ] `Frontend/1. CONSTITUTION/BEHAVIOR_SULLIVAN.md` : Identité, Modes, Manifest, Règles, Format, Interdits
- [ ] Brancher dans `server_v3.py` → injecté dans `base_system` de chaque mode

---

### Thème 14 — Backend IDE
> M208 ✅ — archivée (`WsBackend.js`, War Room 3 colonnes, Quick-Switcher)

---

### Thème 15 — FEE Lab
> M209 ✅ — archivée (`WsFEE.js`, layout Studio, Sullivan FEE)

### Mission 221 — FEE Studio : overlay "Camera RAW" 4 zones au clic "front dev"
**STATUS: ✅ LIVRÉ | DATE: 2026-04-07 | ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE
> Vision complète : `docs/09_Frontend/FEE_POPOVER_VISION.md`

**CONTEXTE CRITIQUE : cette mission se passe entièrement dans `/workspace` (`workspace.html`).
Ne pas créer de nouvelle page, ni de route `/fee`. L'overlay est injecté dans le DOM du workspace au clic sur le bouton `[data-mode="front-dev"]` déjà présent dans `workspace.html`. Il flotte au-dessus du layout workspace existant (`position: fixed; inset: 0; z-index: 9000`). Le workspace reste monté en dessous.**

**Concept :** le mode FEE est un outil d'étalonnage de l'interactivité, pas de construction. L'étudiant est DA, Sullivan traduit l'émotion en timeline GSAP.

```
┌──────────────────────────────────────────────────────────────┐
│  GAUCHE (~240px)    │   CENTRE (flex-1)     │  DROITE (~320px) │
│  Explorateur        │   Iframe "pristine"   │  Sullivan FEE    │
│  data-af-id tree    │   Hot-Reload temporel │  Vibe-to-Code    │
│  LEDs GSAP          │   Play/Pause/Rewind   │  logic.js AST    │
│  State selector     │   Slow-Mo             │  chat + input    │
│─────────────────────┴───────────────────────┴─────────────────│
│  BAS (~100px) — Pellicule : Entrées | Sorties | Parallaxe | Distorsions | Hover │
└──────────────────────────────────────────────────────────────┘
```

**Gauche — Explorateur de Triggers :**
- Appel `postMessage` à l'iframe → récupère tous les `[data-af-id]`
- Afficher arborescence : nom de l'élément + `data-af-id`
- LED verte si l'élément possède déjà une timeline GSAP dans `logic.js`
- Sélecteur State : `initial` / `hover` / `click` / `scroll-trigger` — filtre le contexte envoyé à Sullivan

**Centre — Labo Photo :**
- `<iframe id="fee-preview-iframe">` → URL : `/api/bkd/fee/preview?project_id={id}&path={file}`
- Hot-Reload : injection via `postMessage` du code généré par Sullivan, sans rechargement complet
- Barre de contrôle : Play / Pause / Rewind / ×0.25 Slow-Mo (dispatche des commandes GSAP via postMessage)

**Droite — Sullivan FEE (Vibe-to-Code) :**
- Réutiliser `WsFEE.js` logique chat (historique + input + stream SSE)
- Contexte envoyé à Sullivan = `{ trigger: data-af-id, state, existing_code: extrait logic.js }`
- Code généré isolé dans un bloc `// [FEE-LOGIC-START] ... // [FEE-LOGIC-END]` dans `logic.js`
- Bouton "appliquer" → `POST /api/bkd/fee/apply` → patch chirurgical AST

**Bas — Pellicule d'Effets :**
- Strip horizontale scrollable, vignettes par catégorie : `Entrées` | `Sorties` | `Parallaxe` | `Distorsions P5.js` | `Hover`
- Clic vignette → pré-remplit le chat Sullivan avec le squelette de code correspondant

**Déclenchement :**
- Clic `[data-mode="front-dev"]` → injecte l'overlay dans `body` si absent → `classList.remove('hidden')`
- Bouton × → `classList.add('hidden')` + reset mode toggle
- Ne pas toucher au GSAP drawer existant (`ws-fee-effects-drawer`) — ce nouvel overlay le remplace

**Fichiers à lire :**
- `Frontend/3. STENCILER/static/templates/workspace.html` — bouton `front-dev`, structure body
- `Frontend/3. STENCILER/static/js/workspace/WsFEE.js` — logique Sullivan FEE existante
- `Frontend/3. STENCILER/static/templates/bkd_frd.html` — référence layout tripartite Mission 208
- `docs/09_Frontend/FEE_POPOVER_VISION.md` — vision complète

**Fichiers à créer/modifier :**
- `Frontend/3. STENCILER/static/js/workspace/WsFEEStudio.js` — **créer** : classe `WsFEEStudio`, injecte et orchestre les 4 zones
- `Frontend/3. STENCILER/static/templates/workspace.html` — charger `WsFEEStudio.js`, brancher sur `[data-mode="front-dev"]`

**Style :** `#f7f6f2` bg, `#3d3d3c` text, `#8cc63f` accent, `border: 1px solid #e5e5e5`, `font-family: Geist`, `border-radius: 0` (Hard-Edge). Pas d'emojis. Pas de majuscules labels.

**Livrable :**
1. Clic "front dev" → overlay 4 zones s'ouvre plein écran
2. Explorateur gauche liste les `data-af-id` de l'iframe
3. Sullivan traduit l'intention en timeline GSAP → code injecté dans `logic.js`
4. Hot-reload visible dans l'iframe sans rechargement
5. Pellicule bas cliquable → pré-remplit Sullivan

**CR post-livraison (Qwen) :**
- `POST /api/bkd/fee/apply` manquante → ajoutée (injecte code avec markers FEE dans logic.js)
- Bouton `[data-mode="front-dev"]` non branché → auto-init ajouté dans WsFEEStudio.js
- Bloc try/except de `fee/chat` cassé → réparé
- Presets étendus : 5 → **20** dans 5 catégories (entrées ×7, sorties ×3, parallaxe ×3, hover ×5, continu ×2)

---

### Thème 16 — EdTech DNMADE
> M210 ✅, M214 ✅, M215 ✅, M216 ✅, M217 ✅, M218 ✅, M219 ✅, M220 ✅ — archivées

---

## Thème 17 — Rattrapage EdTech (Vendredi)

> Bugs identifiés 2026-04-07. Traiter dans l'ordre.

### R0 — Sullivan patch_element : _apply_tailwind_diff manquant → blobs Tailwind
**STATUS: ✅ LIVRÉ**

**Fix appliqué dans `frd_router.py` :**
- `_apply_tailwind_diff(source_html, diff)` — patch chirurgical de classes Tailwind via BeautifulSoup (fallback data-wire inclus)
- `_strip_tailwind_blobs(html)` — supprime les `<style>` > 5000 chars avant sauvegarde
- `save_frd_file()` appelle `_strip_tailwind_blobs()` avant `write_text`
- `sullivan_router.py` importe maintenant la fonction existante → plus d'exception silencieuse

**Validé :**
```bash
# patch_element : add/remove classes OK
# strip blob >5000 : ✅ supprimé
# preserve small <style> : ✅ conservé
# data-wire fallback : ✅ OK
```

### R1 — `/teacher` : formulaire "créer une classe" ne soumet pas
**STATUS: ✅ LIVRÉ**

**Fix appliqué :**
- `createClass()` : error handling complet (validation HTTP status, feedback UI rouge/vert, console.log debug)
- Ajout `PUT /api/classes/{id}` — modifier une classe (backend + modal frontend)
- Ajout `DELETE /api/classes/{id}` — supprimer une classe + cascade étudiants
- Boutons "modifier" et "supprimer" visibles quand une classe est sélectionnée
- Tableau de sujets ajouté au dashboard — `GET /api/classes/{id}/subjects` appelé au chargement
- Affiche sujet/description/competences ou "aucun sujet" si vide

```bash
# Testé et validé :
curl -X POST http://localhost:9998/api/classes -H "Content-Type: application/json" -d '{"name":"DNMADE 2026","subject":"Design Web"}'
curl -X PUT http://localhost:9998/api/classes/dnmade-2026 -H "Content-Type: application/json" -d '{"name":"DNMADE 2026 v2","subject":"Design Web"}'
curl -X DELETE http://localhost:9998/api/classes/dnmade-2026
```

---

### R2 — Cadrage mode prof : `class_id` pas transmis à Sullivan
**STATUS: ✅ LIVRÉ**

**Diagnostic :** Le frontend passait déjà `class_id` dans l'URL SSE. Le router l'acceptait déjà. `_load_class_meta()`, `_load_dnmade_referentiel()`, `_build_prof_system()` existaient déjà dans `brainstorm_logic.py`.

**Le seul bug :** chemin DB incorrect dans `_load_class_meta()`
- Avait : `... / "Frontend/3. STENCILER" / "db" / "projects.db"` (n'existait pas)
- Corrigé : `... / "db" / "projects.db"` (racine AETHERFLOW)

**Résultat :** Sullivan reçoit maintenant le contexte DNMADE complet — nom de classe, sujet actif, et référentiel 4 domaines / 10 compétences.

**Fichier modifié :** `Backend/Prod/retro_genome/brainstorm_logic.py` — ligne DB path corrigée

---

### R9 — bootstrap.js:814 TypeError : refreshNav undefined
**STATUS: ✅ LIVRÉ**

**Fix :** ajout guard `if (!window.HOMEOS) window.HOMEOS = {};` avant assignation de `refreshNav` et `boot`.
**Fichier :** `Frontend/3. STENCILER/static/js/bootstrap.js` ligne 814.

### R3 — Onglet "Dashboard" absent du nav en mode prof
**STATUS: ✅ VALIDÉ**

Bootstrap.js injecte le nav dynamique avec l'onglet Dashboard pour `role === 'prof'` (ligne `TABS.unshift({ id: 'dashboard', label: 'Dashboard', ... path: '/teacher' })`).

---

### R4 — cadrage_alt.html : Univers LT Std Light + max-width
**STATUS: ✅ LIVRÉ (CODE DIRECT)**

- Streams + inputs → `font-family: 'Univers LT Std'; font-weight: 300; font-size: 14px`
- `@font-face` → `/static/fonts/univers-lt-std/univers-lt-std-300.woff2`
- Contenu centré `max-width: 48rem`
- Panneau compétences prof → `top: 120px` (hors zone "+ capture")

---

### R8 — Cadrage mode prof : UX simplifiée (sans arbitrage, sans PRD)
**STATUS: ✅ LIVRÉ**

**Modifications appliquées :**
- Masquage auto des outils d'arbitrage/PRD et du panneau Sullivan en mode prof.
- Amorce silencieuse auto-générée à l'ouverture pour guider le professeur.
- Carte de confirmation visuelle (verte) injectée lors de la détection du sujet structuré.
- Logique de redirection vers `/teacher` après création du sujet.

**Livrable :**
1. `/cadrage?mode=prof&class_id=dnmade-2026` → accueil Sullivan automatique, pas de boutons arbitrage/PRD
2. Discussion → compétences dans panneau droit
3. `<!-- SUJET: -->` détecté → carte verte + bouton "créer le sujet →" actif
4. Clic → retour `/teacher`

---

### R5 — Sujets créés → visibles dans `/teacher`
**STATUS: ✅ VÉRIFIÉ**

`teacher_dashboard.html` appelle `GET /api/classes/{id}/subjects` via `loadSubjects()` au chargement d'une classe. Tableau affiché avec titre, description, compétences.

---

### R6-A — Login élève : résolution classe + student_id
**STATUS: ✅ LIVRÉ**

- `auth_register()` cherche l'élève dans `students` par `display` (case-insensitive)
- Retourne `student_id`, `class_id`, `project_id` dans la réponse
- `login.html` : si élève reconnu et `project_id` null → appelle `/start` pour créer le projet → redirige `/workspace?project_id=X`
- Session stocke `student_id`, `class_id`, `project_id` pour les composants downstream
- Flow admin/prof inchangé (class_id null = redirect `/teacher`)

---

### R6 — Workspace étudiant : isolation projet dans Stitch
**STATUS: ✅ LIVRÉ**

- `/workspace?project_id={id}` → active le projet via `POST /api/projects/activate` avant chargement (XHR synchrone dans `<head>`)
- Stitch pointe sur `projects/{uuid}/imports/` (active_id mis à jour)
- Export → sauvegardé dans `projects/{uuid}/exports/`
- Dashboard prof → bouton "ouvrir" active le projet puis ouvre `/workspace` dans nouvel onglet

---

### M222 — Stitch : reconnaissance et sync automatique par project_id HoméOS
**STATUS: ✅ LIVRÉ**

- Backend : `GET /api/stitch/project-info` → retourne `stitch_project_id` + titre du manifest du projet actif
- Frontend : `WsStitch._syncProjectId()` auto-remplit le champ `project_id` au `show()`
- Flow : `show()` → `updateStatus()` → `_syncProjectId()` → `loadSession()`

**Fichiers à modifier :**
- `stitch_router.py` — ajouter `GET /api/stitch/project-info`
- `WsStitch.js` — ajouter `_syncProjectId()`, l'appeler dans `show()`

**Règle :** ne pas toucher à `loadSession()` ni à `_patch_manifest_stitch_project_id`. Scope strict.

**Livrable :**
1. Workspace ouvert avec `?project_id=dnmade-2026-blart-samuel`
2. Panel Stitch ouvert → `stitch_project_id` auto-rempli depuis manifest
3. `loadSession()` peut opérer sans saisie manuelle

---

### R7 — CI/CD élèves : déploiement des rendus
**STATUS: ✅ LIVRÉ**

**Pipeline GitHub Actions :** `.github/workflows/deploy-student.yml`
- Trigger : `workflow_dispatch` (manual avec `project_id`) ou push sur `student-deploy/*`
- Étapes : resolve project → check exports → prepare bundle → deploy HF Spaces → update milestone N5
- Cible : HF Space `FJDaz/homeos-students` (ou fallback `FJDaz/homeos`)

**Backend :** `POST /api/classes/{class_id}/students/{student_id}/deploy`
- Vérifie exports exists + HTML files
- Trigger GitHub Actions via repository_dispatch
- Update milestone à N5 (Déployé)
- Retourne URL de déploiement

**Utilisation :**
```bash
# Via API
curl -X POST http://localhost:9998/api/classes/dnmade1-2026/students/blart-samuel/deploy

# Via GitHub Actions (manuel)
# Actions → deploy student render → Run workflow → project_id=dnmade1-2026-blart-samuel
```

---

---

## Thème 18 — Désintoxication bootstrap.js

> Diagnostic 2026-04-07. `bootstrap.js` (829L) injecte ~350L de CSS inline à chaque page, plus du code workspace-spécifique (GSAP). Pas de bug actif (R9 réglé, static nav supprimé), mais c'est une bombe à retardement pour les agents et le cache browser.

### B1 — Extraire le CSS de bootstrap.js → homeos-nav.css
**STATUS: ✅ LIVRÉ**
**DATE: 2026-04-07 | ACTOR: QWEN**

**Contexte :**
`bootstrap.js` injecte ~350L de CSS via `style.textContent = \`...\`` dans `injectStyles()`.
Ce CSS ne change jamais → il devrait être un fichier statique, cacheable.

**Fichiers à lire :**
- `Frontend/3. STENCILER/static/js/bootstrap.js` (829L)

**Fichiers à créer/modifier :**
- `Frontend/3. STENCILER/static/css/homeos-nav.css` — **créer** avec tout le contenu de `injectStyles()`
- `Frontend/3. STENCILER/static/js/bootstrap.js` — remplacer `injectStyles()` par injection d'un `<link>` vers `/static/css/homeos-nav.css`

**Livrable :**
```js
// bootstrap.js — injectStyles() remplacée par :
function injectStyles() {
    if (document.getElementById('homeos-bootstrap-css')) return;
    const link = document.createElement('link');
    link.id = 'homeos-bootstrap-css';
    link.rel = 'stylesheet';
    link.href = '/static/css/homeos-nav.css';
    document.head.appendChild(link);
}
```

**Règle :** ne pas toucher à autre chose dans bootstrap.js. Scope strict.

---

### B2 — Sortir le code GSAP/workspace de bootstrap.js
**STATUS: ✅ LIVRÉ**

- Code workspace (`ws-mode-btn`, `effects-drawer`, `GsapCheatSheet`) extrait de `bootstrap.js`
- Déplacé dans nouveau fichier `WsBootstrap.js`
- `workspace.html` charge `WsBootstrap.js`
- `bootstrap.js` est maintenant propre : ne fait que nav + styles globaux

---

---

## Thème 19 — Auth & Login redesign

### M224 — Login : prof par mot de passe, élève par classe + prénom
**STATUS: ✅ LIVRÉ**

**Backend (`auth_router.py`) :**
- Migration DB : colonne `password_hash` ajoutée à `users`
- `POST /api/auth/register-prof` — inscription prof (nom + mot de passe hashé SHA-256)
- `POST /api/auth/login-prof` — login prof par nom + mot de passe
- `POST /api/auth/login-student` — login élève sans mot de passe (class_id + student_id)
- `GET /api/classes/{class_id}/students-list` — liste publique des élèves (sans auth)

**Testé :**
- ✅ Inscription prof → token + role='prof'
- ✅ Login prof correct → token retourné
- ✅ Mauvais mot de passe → 401 "Mot de passe incorrect"
- ✅ Students list → retourne id + display + project_id

**Note :** Frontend UI login (deux branches prof/élève) à implémenter par Gemini.

---

---

## Thème 21 — ProjectContext RAG

### M226 — ProjectContext : contexte projet canonique injecté dans tous les LLM
**STATUS: ✅ LIVRÉ | DATE: 2026-04-07 | ACTOR: QWEN**

> Absorbe M225. Remplace toutes les injections de contexte ad hoc.

**Principe :**
Un seul objet `ProjectContext` chargé une fois par session → injecté dans **tout** appel LLM (cadrage, brainstorm, Sullivan FEE, pre-eval). Le LLM est instruit de respecter impérativement ce contexte avant de répondre.

**Sources à agréger (par ordre de priorité) :**
```
projects/{project_id}/
  ├── manifest.json          → écrans, atoms, stitch_project_id
  ├── genome.json            → structure narrative
  ├── exports/PRD_*.md       → dernier PRD validé (le plus récent)
  └── design.md              → design system projet (si présent)

Frontend/1. CONSTITUTION/
  └── DESIGN.md              → design system HoméOS global (fallback)

classes/{class_id}/subjects/ → sujet DNMADE lié (si class_id en session)
dnmade_referentiel.json      → compétences (si mode éducation)
```

**Backend — créer `Backend/Prod/retro_genome/project_context.py` (ACTOR: QWEN) :**

```python
class ProjectContext:
    def __init__(self, project_id: str = None, class_id: str = None):
        self.project_id = project_id
        self.class_id = class_id
        self._cache = None

    def load(self) -> str:
        """Charge et formate toutes les sources en un bloc texte pour le prompt."""
        if self._cache:
            return self._cache
        sections = []

        # 1. Manifest
        manifest = self._read_json(PROJECTS_DIR / self.project_id / "manifest.json")
        if manifest:
            sections.append(self._format_manifest(manifest))

        # 2. Genome
        genome = self._read_json(PROJECTS_DIR / self.project_id / "genome.json")
        if genome:
            sections.append(f"GÉNOME PROJET:\n{json.dumps(genome, ensure_ascii=False, indent=2)[:2000]}")

        # 3. Dernier PRD
        prd = self._latest_prd()
        if prd:
            sections.append(f"PRD VALIDÉ:\n{prd[:3000]}")

        # 4. Design system projet ou HoméOS global
        design = self._read_file(PROJECTS_DIR / self.project_id / "design.md") \
                 or self._read_file(CONSTITUTION_DIR / "DESIGN.md")
        if design:
            sections.append(f"DESIGN SYSTEM:\n{design[:1500]}")

        # 5. Sujet DNMADE si class_id
        if self.class_id:
            sujet = self._latest_subject()
            if sujet:
                sections.append(f"SUJET DNMADE:\n{sujet}")
            ref = _load_dnmade_referentiel()
            if ref:
                sections.append(f"RÉFÉRENTIEL DNMADE:\n{ref}")

        self._cache = "\n\n---\n\n".join(sections)
        return self._cache

    def as_system_prefix(self) -> str:
        ctx = self.load()
        if not ctx:
            return ""
        return (
            "CONTEXTE PROJET — respecte ces règles IMPÉRATIVEMENT avant de répondre.\n"
            "Ne propose rien qui contredise le manifest, le design system ou le PRD validé.\n\n"
            + ctx + "\n\n---\n\n"
        )
```

**Intégration dans `brainstorm_logic.py` :**

Modifier `sse_chat_generator()` — remplacer toute la logique d'injection contextuelle par :
```python
from .project_context import ProjectContext

ctx = ProjectContext(project_id=project_id, class_id=class_id)
system_prompt = ctx.as_system_prefix() + (BRS_CHAT_SYSTEM if not class_id else "")
```

Supprimer les helpers devenus redondants : `_load_class_meta`, `_load_dnmade_referentiel`, `_build_prof_system` → absorbés dans `ProjectContext`.

**Routes à mettre à jour :**
- `cadrage_router.py` → ajouter `project_id: str = Query(None)` au SSE endpoint → passer à `sse_chat_generator`
- `cadrage_alt.html` → lire `session.project_id` depuis localStorage → ajouter `&project_id=` à l'URL SSE

**Fichiers à lire :**
- `Backend/Prod/retro_genome/brainstorm_logic.py` — L247-370 (sse_chat_generator + helpers M220)
- `Frontend/3. STENCILER/routers/cadrage_router.py`
- `Frontend/3. STENCILER/static/templates/cadrage_alt.html` — `startStreaming()`

**Fichiers à créer/modifier :**
- `Backend/Prod/retro_genome/project_context.py` — **créer**
- `Backend/Prod/retro_genome/brainstorm_logic.py` — remplacer helpers par `ProjectContext`
- `Frontend/3. STENCILER/routers/cadrage_router.py` — ajouter `project_id` param

**Règle fallback (CRITIQUE) :**
- Si `project_id` absent → utiliser `default` comme project_id (projet HoméOS de référence)
- Si `role === 'prof'` → jamais bloqué, toujours un contexte disponible
- Le prof visitant une classe (`class_id` présent) reçoit le sujet de la classe en contexte, même sans project_id personnel

**Livrable :**
1. Tout appel Sullivan reçoit le manifest + genome + PRD + design en contexte
2. Mode prof : sujet DNMADE + référentiel inclus automatiquement, fallback `default` si pas de projet actif
3. Mode élève : idem + manifest Stitch de son projet
4. Un seul endroit à maintenir pour enrichir le contexte de tous les LLM
5. Plus jamais de "veuillez activer un projet" pour le prof

---

### M225 — Cadrage : panneau "contexte projet" visible dans l'UI
**STATUS: 🟠 PRÊTE | DATE: 2026-04-07 | ACTOR: GEMINI**

> Dépend de M226 (backend). Frontend uniquement.

> BOOTSTRAP OBLIGATOIRE

Panneau rétractable dans `cadrage_alt.html` affichant ce que Sullivan voit :
- Titre du projet, ID Stitch, nb écrans, dernier PRD (lien), design system actif
- Bouton "recharger" → re-fetch `GET /api/projects/active` + manifest
- Collapsed par défaut, expand au clic sur "contexte projet ▸"
- Position : colonne de droite sous le panneau compétences (mode prof) ou en haut à droite (mode élève)

**Fichiers à lire :**
- `Frontend/3. STENCILER/static/templates/cadrage_alt.html`
- `Frontend/3. STENCILER/routers/cadrage_router.py`

**Contexte :**
Un élève arrive en Cadrage avec un projet déjà structuré (manifest Stitch : écrans, atoms, intentions).
Sullivan ne voit rien de tout ça — il répond dans le vide.
Il faut : (1) passer `project_id` au SSE, (2) lire le manifest et l'injecter dans le system prompt, (3) l'afficher dans l'UI.

**Backend — `cadrage_router.py` + `brainstorm_logic.py` (ACTOR: QWEN) :**

1. `cadrage_router.py` — ajouter `project_id` au SSE endpoint :
```python
@router.get("/api/cadrage/chat/{provider}")
async def cadrage_chat_sse(provider: str, session_id: str = Query(...), message: str = Query(...), class_id: str = Query(None), project_id: str = Query(None)):
    async def generate():
        async for chunk in cadrage_logic.sse_chat_generator(session_id, provider, message, class_id=class_id, project_id=project_id):
            yield chunk
```

2. `brainstorm_logic.py` — ajouter helper `_load_project_manifest(project_id)` :
```python
def _load_project_manifest(project_id: str) -> str:
    """Lit projects/{project_id}/manifest.json → retourne texte formaté pour le prompt."""
    try:
        projects_dir = Path(__file__).parent.parent.parent.parent / "projects"
        manifest_path = projects_dir / project_id / "manifest.json"
        if not manifest_path.exists():
            return ""
        data = json.loads(manifest_path.read_text(encoding='utf-8'))
        # Résumer : titre, écrans, atoms clés
        lines = []
        if data.get("name"): lines.append(f"Projet : {data['name']}")
        if data.get("stitch_project_id"): lines.append(f"Stitch ID : {data['stitch_project_id']}")
        screens = data.get("screens", [])
        if screens: lines.append(f"Écrans : {', '.join(s.get('name','?') for s in screens)}")
        return "\n".join(lines)
    except Exception as e:
        logger.warning(f"_load_project_manifest error: {e}")
        return ""
```

3. Dans `sse_chat_generator()` — si `project_id` présent, enrichir `system_prompt` :
```python
if project_id:
    manifest_ctx = _load_project_manifest(project_id)
    if manifest_ctx:
        system_prompt += f"\n\nCONTEXTE PROJET ÉLÈVE :\n{manifest_ctx}"
```

**Frontend — `cadrage_alt.html` (ACTOR: GEMINI) :**

> BOOTSTRAP OBLIGATOIRE

1. Au chargement, lire `localStorage.homeos_session.project_id`
2. Si présent → `GET /api/projects/{project_id}/manifest` (ou lire depuis `/api/projects/active`) → afficher dans un panneau rétractable à droite intitulé "contexte projet" :
   - Titre du projet, liste des écrans Stitch, compétences DNMADE si présentes
   - Bouton "recharger" → re-fetch le manifest (utile si l'élève a importé de nouveaux écrans)
   - Panneau collapsed par défaut, expand au clic
3. Ajouter `&project_id={project_id}` à l'URL SSE dans `startStreaming()`

**Fichiers à lire :**
- `Frontend/3. STENCILER/routers/cadrage_router.py`
- `Backend/Prod/retro_genome/brainstorm_logic.py` — `sse_chat_generator()`, helpers M220
- `Frontend/3. STENCILER/static/templates/cadrage_alt.html` — `startStreaming()`, panneau Sullivan

**Livrable :**
1. Élève ouvre `/cadrage` avec `project_id` en session → Sullivan voit le manifest dans son contexte
2. Panneau "contexte projet" visible et rétractable dans l'UI
3. Bouton "recharger" met à jour sans rechargement de page

---

## Thème 25 — Stitch UX

### S1 — Panel Stitch : overflow coupé + formulaire toujours caché
**STATUS: ✅ CODE DIRECT | DATE: 2026-04-08 | ACTOR: CLAUDE**

- `WsStitch.js` : branches `!res.ok` et `!data.linked` appellent maintenant `showManualForm()` — le formulaire ID est visible dès l'ouverture si pas de session liée
- `workspace.html` : `#panel-stitch` → `max-height: calc(100vh - 96px); flex-direction: column` / `#stitch-content` → `overflow-y: auto; flex: 1` (plus de `max-h-[60vh]`)

---

### M227 — Isolation projet par session utilisateur (critique)
**STATUS: ✅ LIVRÉ**

- `bkd_service.get_active_project_id(token)` : si token élève → résout `students.project_id` depuis DB, sinon fallback `active_project.json`
- `bkd_service.set_active_project_id(pid, token)` : si token élève → met à jour DB `students.project_id`
- `projects_router.activate_project` : lit `X-User-Token` → passe au setter
- `bootstrap.js` : project switcher masqué pour `role === 'student'`
- `workspace.html` : activation XHR inclut `X-User-Token`

**Résultat :** Chaque élève voit TOUJOURS son propre projet, même si le prof navigue en même temps sur un autre.
- `Frontend/3. STENCILER/static/templates/workspace.html` — XHR activation L43-55
- `Frontend/3. STENCILER/static/js/bootstrap.js` — `injectNav()`, project switcher

**Livrable :**
1. Hugo ouvre le workspace → son projet, même si le prof a switché entre-temps
2. Hugo ne voit pas le project switcher dans la nav
3. Le prof garde l'accès à tous les projets

---

### S3 — Stitch MCP : utiliser la clé API de FJD pour tous les élèves
**STATUS: ✅ LIVRÉ**

- `_get_stitch_key()` dans `stitch_router.py` : lit d'abord `STITCH_API_KEY` depuis l'env, puis fallback sur `user_keys` (admin/prof)
- Toutes les routes stitch utilisent `_get_stitch_key()` au lieu de `STITCH_API_KEY`
- Tous les `StitchClient()` reçoivent `api_key=_get_stitch_key()`
- `GET /api/stitch/status` retourne `connected: true` si la clé est dans `user_keys` (même sans `.env`)

---

### M232 — Refonte layout workspace : dashboard projet + nettoyage toolbar
**STATUS: 🟠 MISSION GEMINI | DATE: 2026-04-08 | ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE

**Fichiers à lire en entier :**
- `Frontend/3. STENCILER/static/templates/workspace.html` — structure complète panels gauche + toolbar droite
- `Frontend/3. STENCILER/static/js/workspace/ws_main.js` — `fetchWorkspaceImports()`
- `Frontend/3. STENCILER/static/css/workspace.css`

**Garder tous les IDs existants des éléments fonctionnels. Ne pas toucher à Sullivan chat ni au canvas.**

---

**A. Supprimer le panel Audit UX**

Dans `workspace.html`, supprimer entièrement :
- `<div id="section-audit">` et son contenu
- `<button id="badge-audit">` et son contenu
- Tout CSS lié à `.panel-audit`, `#panel-audit`, `#badge-audit` dans `workspace.css`

---

**B. Remplacer `#panel-screens` par un dashboard projet**

Nouveau contenu de `#ws-import-list` (rendu par `fetchWorkspaceImports()`) :

```
┌─────────────────────────────────┐
│  ▸ mon projet                   │  ← collapse (ouvert par défaut)
│    [nom du projet depuis manifest]
│    ┌ Stitch ──────────────────┐  │  ← sous-collapse fermé par défaut
│    │ ID Stitch : [___________] │  │
│    │ [lier →]                  │  │
│    └───────────────────────────┘  │
│                                   │
│    mes écrans                     │
│    ┌───────────────────────────┐  │
│    │ nom-écran.html        [S] [↻] [×] │
│    │ nom-écran-2.html      [S] [↻] [×] │
│    │ ...                       │  │
│    └───────────────────────────┘  │
│    (message si vide)              │
└─────────────────────────────────┘
```

**Comportement :**
- Clic sur le nom d'écran → `window.wsCanvas?.addScreen({...})`
- Bouton `[S]` (logo Stitch SVG, alt "ouvrir dans Stitch") → `fetch('/api/stitch/open/{screen_id}').then(d => window.open(d.url))`
- Bouton `[↻]` → `POST /api/stitch/sync` puis recharger la liste
- Bouton `[×]` → confirmation puis suppression de l'import local

**Sous-collapse Stitch ID :**
- Input texte + bouton "lier" → `POST /api/stitch/pull` avec le project_id saisi → mémorise dans manifest
- Affiché seulement si `stitch_project_id` absent du manifest

---

**C. Nettoyage toolbar droite**

Dans `workspace.html`, toolbar `<nav class="absolute top-1/2 right-8...">`, garder uniquement :

| Outil | Action | Garder |
|-------|--------|--------|
| Select (V) | sélection canvas | ✅ |
| Drag (H) | pan canvas | ✅ |
| Typographie (T) | `#btn-ws-typo` | ✅ |
| Couleur (C) | `#ws-color-panel` — conditionné DESIGN.md | ✅ |
| Stitch (S) | logo Stitch → ouvre panel Stitch | ✅ NOUVEAU |
| Place Image (I) | stitch fait mieux | ❌ supprimer |
| Frame (F) | non fonctionnel | ❌ supprimer |
| Effets (E) | FEE Studio remplace | ❌ supprimer |

Bouton Stitch dans toolbar : icône logo Stitch (ou "S" en attendant) → `window.wsStitch?.toggle()`.

---

**D. Corrections de scope (notes de clarification FJD 2026-04-08)**

- **Sullivan** : panneau en bas du workspace, pas à droite — il demeure
- **Wire** : demeure dans le workspace comme outil/mode
- **Disparaissent** : bouton KIMI (stratégie différente à venir), boutons hover/scroll/click/liste (pris en charge par FEE)
- **Export** : aperçu localhost uniquement pour l'instant — pas de bouton forge/export dans ce scope
- **DESIGN.md** : n'est PAS un document HoméOS exclusif. C'est le design du projet de l'élève = tokens Stitch + règles nécessaires à HoméOS pour jouer sa partie. Stitch = source de vérité design. À chaque pull Design DNA → **toujours mettre à jour** `DESIGN.md` sections `Colors`, `Typography`, `Spacing`. Ne jamais écraser les sections spécifiques HoméOS (ex: `## Wire Rules`, `## Interaction Tokens`) — merge sectionnel.

**D. Règle DESIGN.md merge (backend — dans `stitch_router.py` au pull)**

Structure DESIGN.md d'un projet élève :
```markdown
# DESIGN.md — {project_name}
> Source: Stitch Design DNA + règles HoméOS

## Colors          ← Stitch écrit ici (màj à chaque pull)
## Typography      ← Stitch écrit ici
## Spacing         ← Stitch écrit ici
## Wire Rules      ← HoméOS écrit ici (ne pas écraser)
## Interaction     ← FEE écrit ici (ne pas écraser)
```

Merge : parser les sections `##`, remplacer Stitch (Colors/Typography/Spacing), préserver le reste.

**Livrable :**
1. Panel audit UX supprimé
2. Panel gauche = dashboard projet avec collapse + sous-collapse Stitch ID + liste écrans (3 actions par écran)
3. Toolbar droite = 5 outils max (select, drag, typo, couleur, Stitch)
4. Sullivan panneau bas et Wire préservés — KIMI et boutons interaction supprimés
5. Aucune régression canvas

---

### M231 — Pipeline d'import multi-source : PNG / SVG / Illustrator / Figma plugin / Stitch
**STATUS: 🟠 PRÊTE | DATE: 2026-04-08**

**Contexte :**
Un élève arrive avec ses maquettes depuis différentes sources. Toutes convergent vers `projects/{id}/imports/`. Le reste du workflow (Wire → Forge → Sullivan) est identique quelle que soit la source.

**Sources à supporter :**

| Source | Format | Mécanisme |
|--------|--------|-----------|
| PNG / JPG | image | Upload direct → stocké dans `imports/` comme asset visuel |
| SVG | vecteur | Upload direct → utilisable dans le canvas SVG natif |
| Illustrator | SVG (export) | L'élève exporte en SVG depuis Illustrator → même pipeline que SVG |
| Figma plugin HoméOS | JSON + PNG | Le plugin pousse vers `POST /api/import/figma` → normalisation → `imports/` |
| Stitch | HTML | `POST /api/stitch/pull` → déjà opérationnel ✅ |

**Ce qu'il faut :**

**Backend — `import_router.py` (ACTOR: QWEN) :**

Route `POST /api/import/upload` — upload générique :
```python
@router.post("/import/upload")
async def import_upload(file: UploadFile, request: Request):
    # Accepte : .png, .jpg, .svg, .ai (SVG exporté)
    # Sauvegarde dans projects/{active_id}/imports/{filename}
    # Enregistre dans exports/index.json (même pipeline que Stitch)
    # Retourne { "filename": "...", "type": "png|svg", "path": "..." }
```

Route `POST /api/import/figma` — payload plugin Figma HoméOS :
```python
@router.post("/import/figma")
async def import_figma(request: Request):
    # Body: { "screen_name": str, "png_base64": str, "metadata": {} }
    # Décode le PNG → sauvegarde dans imports/figma_{screen_name}.png
    # Sauvegarde metadata dans imports/figma_{screen_name}.json
    # Retourne { "filename": "...", "imported": true }
```

**Frontend — zone d'import dans le workspace (ACTOR: GEMINI) :**

Dans le panel gauche du workspace (section écrans/imports), ajouter une zone "importer" :
```
┌─────────────────────────────┐
│  importer des maquettes     │
│                             │
│  [↑ PNG / SVG]  [Figma]     │
│  [Stitch →]                 │
│                             │
│  ou glisser-déposer ici     │
└─────────────────────────────┘
```

- Bouton "PNG / SVG" → `<input type="file" accept=".png,.jpg,.svg">` → `POST /api/import/upload`
- Bouton "Figma" → instructions pour le plugin (lien doc)
- Bouton "Stitch →" → ouvre le panel Stitch existant
- Drag & drop → même route

**Livrable :**
1. Un élève peut uploader un PNG ou SVG → apparaît dans `imports/` + liste du workspace
2. Le plugin Figma peut envoyer un écran → même résultat
3. Stitch reste la voie principale pour les aller-retours live

---

### M230 — Workflow Stitch complet : push/pull/sync élève
**STATUS: ✅ LIVRÉ (backend Qwen) — Frontend à faire par Gemini**

**Backend livré :**
- `run_stitch_push_task()` extrait `project_id` depuis `screen_name` → `_patch_manifest_stitch_project_id()`
- `POST /api/stitch/sync` — compare écrans Stitch vs imports locaux → pull les nouveaux
- `GET /api/stitch/open/{screen_id}` — retourne URL Stitch `https://stitch.google.com/p/{pid}/s/{sid}`
- Premier push → `stitch_project_id` mémorisé dans manifest → `stitch_url` retourné au frontend

**Workflow cible :**
```
1. PREMIER PUSH
   Élève clique "modifier dans Stitch" sur un écran HoméOS
   → POST /api/stitch/push (Sullivan + genome + DESIGN.md)
   → generate_screen_from_text → Stitch crée l'écran → retourne screen_name
   → Extraire project_id depuis screen_name ("projects/{pid}/screens/{sid}")
   → Sauvegarder manifest.json : stitch_project_id = pid
   → Ouvrir https://stitch.google.com/p/{pid}/s/{sid} dans nouvel onglet

2. PUSHES SUIVANTS
   → Même stitch_project_id (lu depuis manifest)
   → edit_screen si écran existant, generate_screen_from_text si nouveau

3. PULL / SYNC (Stitch → HoméOS)
   → window.onfocus : retour depuis Stitch → déclenche sync auto
   → Polling toutes les 5min (si Stitch lié)
   → Bouton "synchroniser" manuel
   → Logique : diff écrans Stitch vs imports locaux → pull des nouveaux/modifiés

4. TOOLBAR CANVAS
   → Bouton "modifier dans Stitch" → push Sullivan → ouvre Stitch
   → Bouton "importer de Stitch" → pull forcé

5. PANEL STITCH — liste des écrans
   Pour chaque écran :
   [œil] ouvrir dans HoméOS  [S] ouvrir dans Stitch  [↻] pull cet écran
   En-tête : titre projet (collapsible) + [↻ synchroniser tout]
```

**ACTOR QWEN — Backend :**

A. Dans `run_stitch_push_task()` après succès : extraire `project_id` depuis `screen_name` → `_patch_manifest_stitch_project_id(pid)`.

B. Route `POST /api/stitch/sync` :
```python
@router.post("/sync")
async def stitch_sync(request: Request):
    # Lit stitch_project_id depuis manifest
    # Appelle stitch_session() pour avoir la liste live
    # Pour chaque écran non local → pull (réutilise la logique de /pull)
    # Retourne { "pulled": [...], "already_local": [...] }
```

C. Route `GET /api/stitch/open/{screen_id}` :
```python
@router.get("/open/{screen_id}")
async def stitch_open_url(screen_id: str):
    # Retourne { "url": "https://stitch.google.com/p/{pid}/s/{screen_id}" }
```

Fichiers : `stitch_router.py`, `stitch_client.py`

---

**ACTOR GEMINI — Frontend (absorbe M228) :**

> BOOTSTRAP OBLIGATOIRE

Fichiers à lire : `workspace.html` panel `#panel-stitch`, `WsStitch.js`

**Panel Stitch — réorganiser `#stitch-content` :**
```
[titre projet]          [↻ synchroniser tout]
─────────────────────────────────────────────
liste écrans :
  Nom écran
  [👁 HoméOS]  [S Stitch]  [↻ pull]
─────────────────────────────────────────────
[modifier dans Stitch →]   ← push Sullivan
```
ID projet : lecture seule si lié, éditable si non lié.

**`WsStitch.js` — polling + focus :**
```js
// Dans show() après loadSession()
if (this.isLinked) {
    this._pollTimer = setInterval(() => this.sync(), 5 * 60 * 1000);
    window.addEventListener('focus', () => { if (this.isOpen) this.sync(); });
}

sync() { fetch('/api/stitch/sync', { method: 'POST' }).then(() => this.loadSession()); }
```

**Toolbar canvas — bouton "modifier dans Stitch"** dans `workspace.html` (barre d'outils droite).

Garder tous les IDs existants.

**Livrable :**
1. Premier push → `stitch_project_id` mémorisé → onglet Stitch ouvert
2. Panel : liste écrans avec 3 actions chacun
3. Sync auto focus + polling 5min + bouton
4. Bouton toolbar "modifier dans Stitch"

---

### M228 — Stitch : UX élève intelligible
**STATUS: ✅ ABSORBÉE PAR M230 | DATE: 2026-04-08**

---

> BOOTSTRAP OBLIGATOIRE

**Contexte :** Stitch est l'outil central pour les élèves DNMADE — ils collent l'ID de leur projet Figma/Stitch, importent leurs écrans, et c'est leur matière première pour la Forge. L'UX actuelle est illisible.

**Fichiers à lire :**
- `Frontend/3. STENCILER/static/templates/workspace.html` — `id="panel-stitch"` et `id="ws-stitch-manual-form"`
- `Frontend/3. STENCILER/static/js/workspace/WsStitch.js`

**Réorganiser le contenu de `#stitch-content` en 3 sections lisibles :**

```
┌─────────────────────────┐
│  stitch            [×]  │
│  statut : ● connecté    │
├─────────────────────────┤
│  1. coller l'id stitch  │
│  [_________________]    │
│  [valider →]            │
├─────────────────────────┤
│  2. mes écrans          │
│  (liste auto après pull)│
│  [importer les écrans →]│
├─────────────────────────┤
│  3. générer via texte   │
│  [__intention_________] │
│  [générer →]            │
└─────────────────────────┘
```

**Règles :**
- Garder TOUS les `id` existants (`ws-stitch-project-id`, `ws-stitch-btn-list`, `ws-stitch-btn-pull`, `ws-stitch-screens-list`, `ws-stitch-intent`, `ws-stitch-btn-push`)
- Supprimer `display:none` sur `#ws-stitch-manual-form` — toujours visible
- Labels : minuscules, français, sans jargon
- Tokens HoméOS. Pas d'emojis.

---

> BOOTSTRAP OBLIGATOIRE

**Symptômes :**
1. Le bas du panel Stitch est coupé — `max-h-[60vh]` trop restrictif quand le panel est positionné
2. L'interface est incompréhensible pour un élève

**Fichiers à lire :**
- `Frontend/3. STENCILER/static/templates/workspace.html` — `id="panel-stitch"` (L253-315)
- `Frontend/3. STENCILER/static/js/workspace/WsStitch.js`
- `Frontend/3. STENCILER/static/css/workspace.css` — `.stitch-expanded`

**Fix 1 — Overflow**
Dans `workspace.html`, `id="stitch-content"` :
- Remplacer `max-h-[60vh]` par `overflow-y-auto` sans max-height fixe
- Le panel `#panel-stitch` doit avoir `max-height: calc(100vh - 96px); overflow-y: auto;` en inline style ou via workspace.css

**Fix 2 — UX simplifiée (scope strict)**
Réorganiser le contenu de `#stitch-content` en 3 blocs clairs, dans cet ordre :

```
┌─────────────────────────────┐
│  STITCH                [×]  │
├─────────────────────────────┤
│  statut : connecté / off    │
│  projet : [titre]           │
├─────────────────────────────┤
│  mes écrans                 │  ← liste des screens importés
│  [+ importer un écran]      │  ← bouton ouvre le formulaire manuel (replié par défaut)
├─────────────────────────────┤
│  générer via intention      │  ← textarea + bouton "générer"
└─────────────────────────────┘
```

- Formulaire manuel (`#ws-stitch-manual-form`) : replié par défaut, s'ouvre au clic sur "+ importer un écran"
- Labels en français, minuscules, sans jargon
- Supprimer le bouton "Lister les écrans" (remplacé par le chargement auto à l'ouverture)
- Garder les IDs existants des éléments (WsStitch.js s'y accroche)

**Style :** tokens HoméOS. Pas d'emojis. Pas de majuscules labels.

**Livrable :**
1. Panel scrollable — le bas est visible
2. Un élève comprend en 3 secondes ce qu'il peut faire

---

## Thème 24 — Fix activation projet élève (Hugo)

### P1 — Student project : activation end-to-end cassée
**STATUS: ✅ LIVRÉ (Qwen) | DATE: 2026-04-07 | ACTOR: QWEN**

**Symptôme :** Hugo se connecte → workspace affiche le projet `default` (templates) au lieu de son espace vide.

**Diagnostic à faire :**
L'élève Hugo (`student_id: dumont-hugo`, `class_id: dnamde3`) a un projet existant sur disque.
Tracer le flow complet et trouver où ça casse :

1. `POST /api/auth/login-student` body `{ "class_id": "dnamde3", "student_id": "dumont-hugo" }`
   - Retourne-t-il un `project_id` non-null ?
   - Écrit-il bien `active_project.json` ?

2. `POST /api/projects/activate` body `{ "id": "<project_id>" }`
   - Le projet est-il dans la table `projects` de la DB ?
   - Si non → le code doit l'auto-enregistrer (fix déjà dans `projects_router.py`) et continuer.
   - Retourne-t-il 200 ou 404 ?

3. `bkd_service.get_active_project_id()` — lit depuis la variable globale `_ACTIVE_PROJECT_ID` OU depuis `active_project.json` ?
   - Si la variable globale n'est pas mise à jour (ex: deux imports différents du module), `get_active_project_path()` retourne le mauvais projet.

**Fichiers à lire :**
- `Frontend/3. STENCILER/bkd_service.py` — `get_active_project_id()`, `set_active_project_id()`, `get_active_project_path()`
- `Frontend/3. STENCILER/routers/projects_router.py` — `activate_project()`, `set_active_project_id()`
- `Frontend/3. STENCILER/server_v3.py` — comment `set_active_project_id` est importé/exposé
- `Frontend/3. STENCILER/routers/auth_router.py` — `auth_login_student()` L363-408

**Problème probable :**
`projects_router.py` importe `set_active_project_id` depuis `bkd_service` et met à jour la variable globale dans ce module.
Mais `bkd_service.get_active_project_id()` lit `_ACTIVE_PROJECT_ID` depuis son propre module.
Si `server_v3.py` réexporte `set_active_project_id` sous un autre alias, ou si les routers importent depuis des modules différents → la variable globale est dans un namespace différent → la mise à jour ne se propage pas.

**Fix attendu :**
- S'assurer que `set_active_project_id` dans `projects_router.py` modifie bien la variable globale de `bkd_service` (pas une copie locale).
- OU : rendre `get_active_project_id()` dans `bkd_service` lire depuis `active_project.json` au lieu de la variable globale (plus robuste — pas de problème de namespace).
- ET : s'assurer que `projects/activate` auto-enregistre le projet si absent de la DB (code déjà ajouté — vérifier qu'il est correct).

**Livrable :**
Hugo se connecte → workspace vide (son projet propre, sans templates).

---

## Thème 23 — Typo globale

### M229 — Audit et suppression de "Source Code Pro" sur les boutons
**STATUS: 🟠 MISSION QWEN | DATE: 2026-04-07 | ACTOR: QWEN**

**Symptôme :** Les boutons dans les pages `cadrage_alt.html` et `workspace.html` (et potentiellement d'autres) s'affichent en police monospace Source Code Pro au lieu de la police sans-serif attendue.

**Mission :**

1. Chercher dans tous les fichiers HTML et CSS du dossier `Frontend/3. STENCILER/static/` toutes les occurrences de :
   - `Source Code Pro`
   - `font-mono` (classe Tailwind → mappe vers monospace)
   - `font-family.*mono`
   - `'monospace'` ou `"monospace"` utilisé hors contexte de pre/code/kbd

2. Pour chaque occurrence :
   - Si c'est sur un élément **`<button>`**, `<input>`, `<select>`, `<label>`, `<span>` de contenu textuel UI → **remplacer par `font-family: inherit`** (ou supprimer la règle font si le parent l'hérite déjà)
   - Si c'est sur `<pre>`, `<code>`, `<kbd>`, `.terminal-log`, `.sd-input` (champ clé API) → **laisser tel quel** (monospace légitime)
   - Si c'est dans la config Tailwind (`mono: ['"Source Code Pro"'...]`) dans `cadrage_alt.html` → **remplacer `'Source Code Pro'` par `'Geist Mono', ui-monospace, monospace`**

3. Dans `cadrage_alt.html` — vérifier que les boutons "Envoyer", "Sullivan Arbitrage", "Générer PRD" ont bien `font-family` hérité de la `body` (`'Source Sans 3'`). Si un bouton a explicitement `font-mono` → retirer la classe.

4. Dans `workspace.html` — idem. Vérifier que les spans `font-mono` sont uniquement sur des éléments de code/tag display (`#ws-popover-tag`, `#ws-wire-import-label`) et PAS sur des boutons.

**Fichiers à auditer :**
- `Frontend/3. STENCILER/static/templates/cadrage_alt.html`
- `Frontend/3. STENCILER/static/templates/workspace.html`
- `Frontend/3. STENCILER/static/css/homeos-nav.css`
- `Frontend/3. STENCILER/static/css/stenciler.css`
- `Frontend/3. STENCILER/static/css/workspace.css`

**Règle :** ne pas toucher aux `.sd-input`, `.terminal-log`, `pre`, `code`, `kbd`. Ne changer que les éléments UI (boutons, labels, spans de texte courant).

**Livrable :** liste des occurrences trouvées + modifications appliquées.

---

## Thème 22 — Fixes login & workspace élève

### F1 — Login : activation projet élève au login + logout visible
**STATUS: ✅ LIVRÉ | DATE: 2026-04-07 | ACTOR: QWEN (backend) + GEMINI (frontend)**

---

### F2 — Projet élève : création automatique depuis le sujet actif de la classe
**STATUS: 🟠 PRÊTE | DATE: 2026-04-07 | ACTOR: QWEN**

**Contexte :**
Hugo se connecte → son projet `dnamde3-dumont-hugo` existe dans `PROJECTS_DIR` et `students.project_id` est renseigné, MAIS il n'est pas enregistré dans la table `projects` → `get_active_project_path()` cherche dans `projects` → ne trouve rien → fallback `default` → workspace plein de templates.

**Règle métier :**
Si l'élève n'a pas de projet OU si son projet n'est pas dans la table `projects` :
1. Charger le dernier sujet de la classe (`classes/{class_id}/subjects/*.json` → le plus récent)
2. Nommer le projet d'après le titre du sujet (slugifié) : `contraintes-peruquiennes`
3. Créer le dossier `projects/{class_id}-{student_id}-{sujet_slug}/`
4. Écrire `manifest.json` avec `name: titre_sujet`, `class_id`, `student_id`, `subject_id`
5. **Enregistrer dans la table `projects`** : `INSERT OR IGNORE INTO projects (id, name, path, user_id)`
6. Mettre à jour `students.project_id`
7. Écrire `active_project.json`

**Modifier `create_student_project()` dans `class_router.py` :**
```python
def create_student_project(student, class_id) -> str:
    # Chercher le sujet actif
    subject_dir = CLASSES_DIR / class_id / "subjects"
    subject_title = None
    subject_slug = None
    if subject_dir.exists():
        subjects = sorted(subject_dir.glob("*.json"))
        if subjects:
            data = json.loads(subjects[-1].read_text(encoding='utf-8'))
            subject_title = data.get("title", "")
            subject_slug = slugify(subject_title) if subject_title else None

    project_id = f"{class_id}-{student['id']}" + (f"-{subject_slug}" if subject_slug else "")
    project_path = PROJECTS_DIR / project_id
    project_path.mkdir(parents=True, exist_ok=True)

    manifest = {
        "name": subject_title or f"Projet {student['display']}",
        ...
    }
    # Enregistrer dans table projects
    with bkd_db_con() as con:
        con.execute(
            "INSERT OR IGNORE INTO projects (id, name, path) VALUES (?, ?, ?)",
            (project_id, manifest["name"], str(project_path))
        )
```

**Aussi : route `POST /api/classes/{class_id}/students/{student_id}/start`** — appeler `create_student_project` + activer + retourner `project_id`. Cette route est appelée depuis `login.html` quand `project_id` est null.

**Fichiers à lire :**
- `Frontend/3. STENCILER/routers/class_router.py` — `create_student_project()`, L127-152
- `Frontend/3. STENCILER/bkd_service.py` — `bkd_db_con`, schéma table `projects`

**Livrable :**
1. Hugo se connecte → projet créé/enregistré → workspace vide (son espace propre)
2. Nom du projet = titre du sujet actif de la classe
3. Plus jamais de fallback sur `default` pour un élève

---

### F3 — Éditeur sujet : frontend manquant (M223 backend ✅, UI absente)
**STATUS: ✅ LIVRÉ | DATE: 2026-04-07 | ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE

```
CONTEXTE TECHNIQUE OBLIGATOIRE — lis avant de coder :

1. DIAGNOSTIC DOM AVANT LISTENER
   Avant d'ajouter un event listener, remonte la chaîne du DOM.

2. RÈGLE DE LIVRAISON
   Ne pas marquer TERMINÉ avant d'avoir testé manuellement dans le browser.

3. SCOPE STRICT
   Ne modifier que teacher_dashboard.html. Ne pas toucher aux autres fichiers.

4. STYLE HOMÉOS
   Même CSS que le dashboard existant. Pas de majuscules. Pas d'emojis.
   Tokens : bg #f7f6f2, text #3d3d3c, accent #8cc63f, border #e5e5e5.
   border-radius: 4px max. Font: Geist, -apple-system.
   Hard-edge : pas de border-radius sur le formulaire principal (0px).
```

**Fichier à lire en ENTIER :**
`Frontend/3. STENCILER/static/templates/teacher_dashboard.html`

**Routes backend disponibles (déjà implémentées) :**
- `GET /api/classes/{class_id}/subjects` — liste des sujets
- `GET /api/classes/{class_id}/subjects/{subject_id}` — sujet complet
- `POST /api/classes/{class_id}/subjects` — créer sujet
- `PUT /api/classes/{class_id}/subjects/{subject_id}` — modifier sujet

**Structure JSON d'un sujet (référence pour les formulaires) :**
```json
{
  "id": "contraintes-peruquiennes",
  "title": "Contraintes Péruquiennes",
  "problematique": "Comment...",
  "contexte": "Dans le cadre de...",
  "parties": [
    { "id": "p1", "titre": "Recherche", "description": "...", "duree": "2 semaines" }
  ],
  "livrables": ["Maquette Figma", "Export HTML"],
  "evaluation": {
    "modalite": "Soutenance orale",
    "criteres": [
      { "competence": "A1", "libelle": "Analyse du contexte", "poids": 30 }
    ]
  },
  "competences": ["A1", "A2", "B1"]
}
```

**Ce qu'il faut implémenter dans `teacher_dashboard.html` :**

**1. Bouton "modifier" dans chaque ligne de la table sujets**

Dans `renderSubjects()`, chaque ligne doit avoir un bouton "modifier" :
```js
'<td><button class="btn-action" onclick="editSubject(\'' + s.id + '\')">modifier</button></td>'
```
Ajouter une 5e colonne `<th></th>` dans le thead.

**2. Drawer de formulaire (panel latéral ou modal)**

Un `<div id="subject-form-panel">` positionné en `position: fixed; right: 0; top: 48px; bottom: 0; width: 420px` (drawer droite, s'ouvre par-dessus le contenu).
Style : `background: #f7f6f2; border-left: 1px solid #e5e5e5; overflow-y: auto; padding: 24px; z-index: 500;`
Caché par défaut : `transform: translateX(100%); transition: transform 0.25s ease`.
Ouvert : `transform: translateX(0)`.

**3. Formulaire en 5 sections dans le drawer**

Section 1 — En-tête :
```html
<div class="sf-section">
  <div class="sf-section-label">en-tête</div>
  <label>titre</label>
  <input type="text" id="sf-title" placeholder="Contraintes Péruquiennes">
  <label>problématique</label>
  <textarea id="sf-problematique" rows="2"></textarea>
  <label>contexte</label>
  <textarea id="sf-contexte" rows="3"></textarea>
</div>
```

Section 2 — Parties (liste dynamique) :
- Bouton "+ partie" → append une ligne `{ titre | description | durée | × }`
- Bouton × → remove la ligne
- IDs générés dynamiquement `sf-party-N`

Section 3 — Livrables (liste dynamique) :
- Bouton "+ livrable" → append `<input type="text">` + bouton ×

Section 4 — Évaluation :
- `<input id="sf-modalite" placeholder="Soutenance orale">`
- Tableau critères : colonnes `compétence DNMADE | libellé | poids %`
- Bouton "+ critère" → append ligne avec `<select>` des compétences DNMADE (A1, A2, A3, B1, B2, C1, C2, C3, D1, D2) + input libellé + input number poids
- Ligne total : `Σ poids = X%` (recalculé à chaque changement)

Section 5 — Compétences DNMADE :
- Checkboxes : A1, A2, A3 / B1, B2 / C1, C2, C3 / D1, D2
- Groupées par domaine avec label discret

Bouton "enregistrer" (`.btn-create`) en bas du drawer.
Bouton "annuler" (`.btn-action`) → ferme le drawer.

**4. Fonctions JS à implémenter**

```js
var subjectFormMode = null; // 'create' ou 'edit'
var editingSubjectId = null;

function openSubjectForm(mode, subjectData) {
    subjectFormMode = mode;
    editingSubjectId = subjectData ? subjectData.id : null;
    // Remplir le formulaire si subjectData présent, sinon vider
    fillSubjectForm(subjectData || {});
    document.getElementById('subject-form-panel').style.transform = 'translateX(0)';
}

function closeSubjectForm() {
    document.getElementById('subject-form-panel').style.transform = 'translateX(100%)';
}

function editSubject(subjectId) {
    fetch(API + '/' + currentClassId + '/subjects/' + subjectId)
        .then(function(r) { return r.json(); })
        .then(function(data) { openSubjectForm('edit', data); });
}

function saveSubjectForm() {
    var payload = collectFormData(); // lit tous les champs
    var url = API + '/' + currentClassId + '/subjects' + (subjectFormMode === 'edit' ? '/' + editingSubjectId : '');
    var method = subjectFormMode === 'edit' ? 'PUT' : 'POST';
    fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(function(r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
    .then(function() { closeSubjectForm(); loadSubjects(currentClassId); })
    .catch(function(e) { alert('erreur: ' + e.message); });
}
```

**5. Modifier `createSubject()`**

Remplacer la redirection vers `/cadrage` par :
```js
function createSubject() {
    if (!currentClassId) return;
    openSubjectForm('create', null);
}
```

**Livrable attendu :**
1. Clic "+ sujet" → drawer s'ouvre à droite, formulaire vide
2. Clic "modifier" sur un sujet → drawer s'ouvre pré-rempli avec les données
3. "enregistrer" → POST ou PUT selon le mode → tableau sujets rafraîchi
4. "annuler" → drawer se ferme
5. Pas d'erreur console

**Bugs constatés :**
1. Élève connecté (ex: Hugo) → workspace affiche le projet `default` (templates) au lieu de son projet isolé — `active_project.json` n'est pas mis à jour au login
2. Pas de bouton logout visible — seul le drawer settings (icône engrenage) permet de se déconnecter, trop caché pour une classe

**Fix 1 — Backend : route `POST /api/auth/login-student` doit activer le projet**

Dans `auth_router.py`, après avoir résolu `project_id` :
```python
# Activer le projet de l'élève immédiatement
if project_id:
    active_file = ROOT_DIR / "active_project.json"
    active_file.write_text(json.dumps({"active_id": project_id}), encoding='utf-8')
```

Fichier : `Frontend/3. STENCILER/routers/auth_router.py` — route `POST /api/auth/login-student`

**Fix 2 — Frontend login.html : forcer activation avant redirect**

Dans `loginStudent()`, après `saveSession(data)` :
```js
// Toujours activer le projet avant de rediriger
if (projectId) {
    await fetch('/api/projects/activate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: projectId })
    });
    window.location.href = `/workspace?project_id=${projectId}`;
}
```
Fichier : `Frontend/3. STENCILER/static/templates/login.html`

**Fix 3 — Logout visible dans le nav**

Dans `bootstrap.js`, dans `injectNav()`, ajouter un bouton logout discret dans `hn-actions` à côté du user pill :
```js
const logoutBtn = document.createElement('button');
logoutBtn.className = 'hn-logout';
logoutBtn.textContent = 'quitter';
logoutBtn.onclick = () => {
    localStorage.removeItem('homeos_session');
    window.location.href = '/login';
};
actions.appendChild(logoutBtn);
```
CSS dans `homeos-nav.css` :
```css
#homeos-global-nav .hn-logout {
    font-size: 9px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.08em; color: #ccc; background: none; border: none;
    cursor: pointer; padding: 2px 6px; transition: color 0.15s;
}
#homeos-global-nav .hn-logout:hover { color: #ef4444; }
```

**Fichiers à lire :**
- `Frontend/3. STENCILER/routers/auth_router.py` — `login-student`
- `Frontend/3. STENCILER/static/templates/login.html` — `loginStudent()`
- `Frontend/3. STENCILER/static/js/bootstrap.js` — `injectNav()`
- `Frontend/3. STENCILER/static/css/homeos-nav.css`

**Livrable :**
1. Hugo se connecte → workspace vide (son projet isolé, pas default)
2. Bouton "quitter" visible dans le nav sur toutes les pages
3. Clic → `localStorage` vidé → `/login`

---

## Thème 20 — Sujet DNMADE structuré

### M223 — Éditeur de sujet : format structuré + parties + livrables + évaluation
**STATUS: ✅ LIVRÉ (backend)**

**Backend (`class_router.py`) :**
- `SubjectCreateRequest` enrichi : `problematique`, `contexte`, `parties[]`, `livrables[]`, `evaluation{modalite, criteres[]}`, `competences[]`
- `POST /{class_id}/subjects` — création format structuré complet
- `GET /{class_id}/subjects/{subject_id}` — lecture d'un sujet par ID
- `PUT /{class_id}/subjects/{subject_id}` — mise à jour complète (préserve id + created_at)

**Frontend (`teacher_dashboard.html`) :**
- Tableau sujets : colonne "details" ajoutée (nb parties + nb livrables)
- Affichage `problematique` si `description` vide (rétrocompatibilité)

**Format JSON produit :**
```json
{
  "id": "design-sonore-et-interface",
  "class_id": "dnmade1-2026",
  "title": "Design Sonore et Interface",
  "problematique": "Comment le son peut-il enrichir une interface numérique ?",
  "contexte": "Dans le cadre du studio DNMADE 2ème année...",
  "parties": [{"id": "p1", "titre": "...", "description": "...", "duree": "..."}],
  "livrables": ["Dossier PDF", "Prototype", "Présentation"],
  "evaluation": {"modalite": "Jury DNMADE", "criteres": [{"competence": "A1", "libelle": "...", "poids": 30}]},
  "competences": ["A1", "C2", "C3"]
}
```

**Note :** Frontend UI d'édition modale (formulaire structuré 5 sections) à implémenter par Gemini.

---

## Backlog
 
### Mission 140 — DPL : Instancier le repo GitHub dans HoméOS
**STATUS: 🔵 BACKLOG**
- [ ] Création/Liaison automatique d'un repo GitHub par projet pour le déploiement continu.


### Mission 110 — Templates FRD : liste vide
**STATUS: 🔴 HOTFIX | DATE: 2026-03-31**
- [ ] Diagnostic `#template-select` vide après manifest minimal

### Mission 115 — Bouton "éditer" global
**STATUS: 🔴 HOTFIX**

### Mission 111-A/B — Multi-project isolation + UI
**STATUS: 🔵 BACKLOG**

### Mission 112 — Sullivan Welcome Screen
**STATUS: 🔵 BACKLOG**

### Mission 113 — Sullivan Tips + Smart Nudges
**STATUS: 🔵 BACKLOG**

### Mission 114 — FRD Canvas v2 : snap + zoom + resize
**STATUS: 🔵 BACKLOG**

### Mission 118 — Pont SVG Illustrator → Tailwind
**STATUS: 🔵 BACKLOG**

### Mission 120 — Plugin Figma → FRD Editor
**STATUS: 🔵 BACKLOG**

### Mission 135-139 — Auth, Multi-tenancy, BYOK, Upload, Wire v2
**STATUS: 🔵 BACKLOG**

---

## 🏛️ Doctrine Architecturale (Aether Core)

**Principe du Miroir :** Host (WsCanvas) gère l'UI AetherFlow. Guest (Iframe) = Agents de Terrain légers, aucun scope partagé.

**AetherCore :** point d'entrée unique `ws_iframe_core.js`, lazy-load des sous-trackers (`tracker_fee.js`, `tracker_construct.js`).

**DESIGN.md comme source de vérité :** l'interface Host lit ce fichier et configure les outils disponibles. Sullivan = "Intendant du Magasin".

**Mode FEE :** GSAP + Lenis. Visual Wiring Trigger→Target. Sullivan reçoit la paire de sélecteurs, génère une timeline `gsap.to()`.
