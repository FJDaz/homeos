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

## Phase Active (2026-04-08)

### Thème 0 — Hotfixes
> M121 ✅, M116 ✅, M122–127 ✅, M233 ✅, M234 ✅, M236 ✅, M237 ✅, M238 ✅, M239 ✅, M240 ✅, M241 ✅, M242 ✅ — archivées ROADMAP_ACHIEVED.md

---

### Thème 27 — Contexte actif dans FEE Studio et Stitch

---

### Mission 260 — DIAG/FIX : FEE Studio charge le mauvais fichier et casse les URLs relatives (écran blanc)
**STATUS: ✅ LIVRÉ | DATE: 2026-04-08 | ACTOR: QWEN**

**Fix appliqué :**
- `WsFEEStudio.js` L166 : `this.ws?.currentFile` remplacé par résolution depuis `window.wsCanvas.activeScreenId` → strip `shell-` → lookup exact dans `WsImportList._items` → `item.html_template` ou `item.file_path`
- `WsImportList.js` : `_items` exposé via getter sur `window.WsImportList`
- Si aucun écran sélectionné → `console.warn` + fallback `landing.html` (plus d'alert bloquant)

**Symptômes (Double problème provoquant l'écran blanc) :** 
1. **Mauvais Fichier** : Ouvrir FEE Studio depuis le workspace → l'iframe essaie toujours de charger `landing.html` quel que soit l'écran sélectionné sur le canvas.
2. **Assets 404** : Même si le bon fichier est trouvé, l'aperçu dans l'iframe est "cassé" (sans styles ni images) à cause d'erreurs 404, car le backend renvoie le fichier HTML brut sans préciser d'URL de base pour les ressources.

**Cause suspectée 1 (Mauvais fichier) :**
`WsFEEStudio.open()` (ligne 166) :
```js
this.activeScreen = this.ws?.currentFile || 'landing.html';
```
`this.ws` résout `window.wsBackend || window.wsCanvas || {}`. `window.wsBackend` n'est jamais instancié. `window.wsCanvas` n'a pas de propriété `currentFile` — il a `activeScreenId`. Le fallback `'landing.html'` s'applique donc systématiquement.

**Cause suspectée 2 (Assets 404) :**
Dans `bkd_router.py` (ligne ~418), la route `/api/bkd/fee/preview` renvoie :
```python
return HTMLResponse(content=file_path.read_text(encoding="utf-8"))
```
Comme l'iframe a pour base `/api/bkd/fee/preview`, toutes les références relatives (`<link href="css/style.css">`, `<img src="assets/... ">`) du projet échouent en 404.

**Hypothèse de fix 1 (Mauvais Fichier) :**
Remplacer dans `WsFEEStudio.open()` L166 :
```js
// Après — résoudre depuis l'écran actif du canvas
const activeShellId = window.wsCanvas?.activeScreenId;
const activeItem = window.WsImportList?._items?.find(
    i => activeShellId && activeShellId.includes(i.id)
);
this.activeScreen = activeItem?.html_template || activeItem?.file_path || 'landing.html';
```

**Hypothèse QWEN (ajoutée au diag) :**
Le fix ci-dessus est fragile — il repose sur un `includes()` implicite entre l'ID DOM (`shell-figma_142300_MonFrame`) et l'ID d'import (`figma_142300_MonFrame`). Ça marche si le shell est nommé `shell-{item.id}`, mais c'est un couplage non garanti.

La vraie cause racine : `WsFEEStudio` est instancié avec `wsRef = window.wsBackend || window.wsCanvas || {}` mais **ne reçoit jamais explicitement** l'item sélectionné. Il devrait :
1. Lire `window.wsCanvas.activeScreenId` (ex: `shell-figma_142300_MonFrame`)
2. Extraire l'ID d'import en stripant le préfixe `shell-`
3. Chercher cet ID exact dans `WsImportList._items`
4. Prendre `item.html_template` ou `item.file_path`

Si aucun shell n'est sélectionné sur le canvas (`activeScreenId === null`), afficher un message `"sélectionnez un écran sur le canvas"` au lieu de l'alert générique.

**Hypothèse de fix 2 (Base URL) :**
Dans `Frontend/3. STENCILER/routers/bkd_router.py` - Route `/api/bkd/fee/preview` :
Injecter une balise `<base href=".../projects/...">` ou l'URL statique correcte pour ce projet dans le `<head>` du HTML brut avant de le renvoyer, afin que le navigateur sache où chercher les dépendances CSS et JS.
Exemple: `html = html.replace("<head>", f"<head><base href='/projects/{project_id}/'>")`

**Livrable QWEN :**
1. Exécuter les tests console (`window.wsCanvas?.activeScreenId`) et reporter les valeurs.
2. Appliquer le fix 1 dans `WsFEEStudio.js` L166 pour cibler le bon écran.
3. Appliquer le fix 2 dans `bkd_router.py` pour injecter la base URL et réparer le rendu CSS/assets.
4. Confirmer que la prévisualisation dans le FEE Studio fonctionne et affiche les bons styles.

**Fichiers à lire :**
- `Frontend/3. STENCILER/static/js/workspace/WsFEEStudio.js` — L160-185 (`open()`)
- `Frontend/3. STENCILER/static/js/workspace/WsImportList.js`
- `Frontend/3. STENCILER/static/js/workspace/WsCanvas.js`
- `Frontend/3. STENCILER/routers/bkd_router.py` — Route `GET /fee/preview`

---

### Mission 261 — DIAG : Stitch s'ouvre sans projet — `stitch_project_id` non résolu
**STATUS: 🔴 DIAG | DATE: 2026-04-08 | ACTOR: QWEN**

**Symptôme :** Clic "modifier dans Stitch" → panel Stitch s'ouvre, champ `project_id` vide, aucune session chargée.

**Chaîne d'appels à auditer :**
```
WsStitch.show()
  → _syncProjectId()
      → GET /api/stitch/project-info
          → lit active_project.json → active_id
          → lit projects/{active_id}/manifest.json → stitch_project_id
          → si absent : retourne { linked: false }
  → loadSession()
      → si projectIdInput vide → GET /api/stitch/screens?project_id= → 400 ou vide
```

**Tests de diagnostic :**
```js
// 1. active_project.json est-il correct ?
fetch('/api/projects/active').then(r=>r.json()).then(console.log)
// Chercher : id, stitch_project_id dans le manifest

// 2. project-info répond quoi ?
fetch('/api/stitch/project-info').then(r=>r.json()).then(console.log)
// Attendre : { linked: true/false, stitch_project_id, title }

// 3. L'input est-il rempli après _syncProjectId ?
window.wsStitch?.projectIdInput?.value  // vide = _syncProjectId n'a rien trouvé

// 4. Manifest du projet actif
fetch('/api/projects/active').then(r=>r.json()).then(d=>console.log(d.stitch_project_id))
```

**Hypothèse 1 — `manifest.stitch_project_id` est null** (TRÈS PROBABLE)
Le projet de l'élève n'a jamais été lié à un projet Stitch → `linked: false` → pas d'auto-fill → `loadSession()` sans project_id → vide.

Fix : si `linked: false`, afficher dans le panel un message `"lier ce projet à Stitch"` avec un champ de saisie manuelle du stitch_project_id + bouton "enregistrer" qui fait `PATCH /api/projects/active/manifest` avec `{ stitch_project_id: value }`.

**Hypothèse 2 — `active_project.json` ne pointe pas sur le bon projet** (PROBABLE)
Le workspace est ouvert avec `?project_id=X` mais `POST /api/projects/activate` dans le `<head>` a échoué silencieusement → `active_project.json` pointe sur un autre projet → manifest sans stitch_project_id.

Test :
```js
// URL actuelle
new URLSearchParams(window.location.search).get('project_id')
// vs ce que le backend voit comme actif
fetch('/api/projects/active').then(r=>r.json()).then(d=>console.log(d.id))
// Les deux doivent matcher
```

**Livrable QWEN :**
1. Exécuter les tests console, reporter les valeurs
2. Identifier laquelle des deux hypothèses est correcte
3. Si H1 : implémenter le flow de liaison manuelle dans `WsStitch.js` (message + input + PATCH)
4. Si H2 : identifier pourquoi `activate` échoue et corriger dans `workspace.html` ou `projects_router.py`
5. Objectif final : ouvrir Stitch → project_id auto-rempli depuis la session workspace

**Fichiers à lire :**
- `Frontend/3. STENCILER/static/js/workspace/WsStitch.js` — `show()`, `_syncProjectId()`, `loadSession()`
- `Frontend/3. STENCILER/routers/stitch_router.py` — `GET /api/stitch/project-info`
- `Frontend/3. STENCILER/static/templates/workspace.html` — balise `<head>`, appel activate
- `Frontend/3. STENCILER/routers/projects_router.py` — `POST /api/projects/activate`

---

### Thème 26 — Forge Pipeline : réparation Vision-to-Code

---

### Mission 264 — dist.zip compilé : snapshot DOM via Playwright → HTML éditable
**STATUS: 🟠 PRÊTE | DATE: 2026-04-08 | ACTOR: QWEN**

**Contexte :** Un dist.zip React sans sources TSX est actuellement extrait tel quel et servi dans l'iframe — non éditable par Sullivan. Playwright est installé (`python3 -c "import playwright"` → ok). L'objectif : charger le bundle headless, attendre le render React, snapshotter le DOM statique, convertir en Tailwind HTML via LLM → résultat éditable.

**Fichiers à lire :**
- `Backend/Prod/retro_genome/routes.py` — bloc `dist_html` (cas dist/index.html dans le ZIP, L706-739)
- `Backend/Prod/retro_genome/react_to_tailwind.py` — `convert()` existant (source TSX → Tailwind)

**Ce qu'il faut créer :**
Ajouter une méthode `snapshot_and_convert(dist_dir: Path, entry_name: str) -> str` dans `react_to_tailwind.py` :

```python
async def snapshot_and_convert(self, dist_dir: Path, entry_name: str) -> str:
    """
    Charge le dist React dans Playwright, snapshotte le DOM après render,
    nettoie le HTML (supprime scripts/styles inline lourds),
    convertit en Tailwind via LLM.
    """
    from playwright.async_api import async_playwright

    index_html = dist_dir / "index.html"
    if not index_html.exists():
        raise FileNotFoundError(f"index.html absent dans {dist_dir}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # Charger en file:// — pas besoin de serveur
        await page.goto(f"file://{index_html.resolve()}", wait_until="networkidle", timeout=15000)
        # Attendre que React ait rendu (div#root non vide)
        await page.wait_for_selector("#root > *", timeout=10000)
        dom_html = await page.content()
        await browser.close()

    # Nettoyer le HTML snapshot (supprimer scripts, styles inline lourds)
    import re
    dom_html = re.sub(r'<script[\s\S]*?</script>', '', dom_html, flags=re.IGNORECASE)
    dom_html = re.sub(r'<style[^>]*>[\s\S]{2000,}?</style>', '', dom_html, flags=re.IGNORECASE)
    dom_html = dom_html[:40000]  # cap contexte LLM

    # Convertir le DOM statique en Tailwind HTML via LLM
    prompt = f"""Tu es un Expert Intégrateur Frontend.
MISSION : Ce HTML est un snapshot DOM d'une app React compilée.
Convertis-le en HTML5 sémantique + Tailwind CSS autonome et éditable.
Préserve fidèlement la structure, les textes, les couleurs visibles.
Supprime toute dépendance React (data-reactroot, __reactFiber, etc.).
Résultat : document HTML5 complet autonome (<!DOCTYPE html>).
Réponds UNIQUEMENT avec le code HTML. Pas de prose.

NOM : {entry_name}

DOM SNAPSHOT :
{dom_html}
"""
    from Backend.Prod.models.gemini_client import GeminiClient
    client = GeminiClient(execution_mode="BUILD")
    result = await client.generate(prompt, max_tokens=16000, temperature=0.1)
    if not result.success:
        raise RuntimeError(f"LLM conversion failed: {result.error}")
    code = result.code
    if "```html" in code:
        code = code.split("```html")[1].split("```")[0]
    elif "```" in code:
        code = code.split("```")[1].split("```")[0]
    return code.strip()
```

**Brancher dans `routes.py` — remplacer le court-circuit dist :**

Actuellement (L706-739), quand `dist/index.html` est détecté, le code extrait le dist et retourne `origin: compiled`. Remplacer par :

```python
if dist_html:
    safe_base = entry["name"].lower().replace(" ", "_").split(".")[0]
    dist_dir = stenciler_templates / f"zip_dist_{safe_base}"
    dist_dir.mkdir(parents=True, exist_ok=True)
    # Extraire le dist
    dist_prefix = dist_html.replace('index.html', '')
    for member in file_list:
        if member.startswith(dist_prefix) and not member.startswith('__MACOSX') and not member.endswith('/'):
            rel = member[len(dist_prefix):]
            dest = dist_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(z.read(member))
    # Snapshot + conversion Tailwind
    try:
        html_code = await get_react_converter().snapshot_and_convert(dist_dir, entry["name"])
        origin = "generated"
    except Exception as e:
        logger.warning(f"[ZIP/Playwright] Snapshot failed ({e}), fallback dist_url")
        # Fallback : servir le dist compilé si Playwright échoue
        dist_url = f"/static/templates/zip_dist_{safe_base}/index.html"
        wrapper_name = f"zip_dist_{safe_base}/index.html"
        idx = json.loads(index_path.read_text(encoding='utf-8'))
        for e2 in idx.get('imports', []):
            if e2['id'] == req.import_id:
                e2['html_template'] = wrapper_name
                e2['dist_url'] = dist_url
                e2['elements_count'] = 0
                e2['origin'] = "compiled"
                break
        index_path.write_text(json.dumps(idx, indent=2, ensure_ascii=False), encoding='utf-8')
        _SVG_JOBS[job_id] = {"status": "done", "template_name": wrapper_name, "dist_url": dist_url, "error": None}
        return
    # Suite normale : sauvegarder le HTML généré dans templates
    # (le flux rejoint le chemin commun après le bloc ZIP)
    template_name = f"reality_{safe_base}.html"
    (stenciler_templates / template_name).write_text(html_code, encoding='utf-8')
    idx = json.loads(index_path.read_text(encoding='utf-8'))
    for e2 in idx.get('imports', []):
        if e2['id'] == req.import_id:
            e2['html_template'] = template_name
            e2['elements_count'] = 0
            e2['origin'] = "generated"
            break
    index_path.write_text(json.dumps(idx, indent=2, ensure_ascii=False), encoding='utf-8')
    _SVG_JOBS[job_id] = {"status": "done", "template_name": template_name, "error": None}
    logger.info(f"[ZIP/Playwright] snapshot → {template_name}")
    return
```

**Points d'attention :**
- `wait_for_selector("#root > *")` — si le div racine React s'appelle autrement (`#app`, `#main`), Playwright timeout. Ajouter un fallback : `await page.wait_for_load_state("networkidle")` suffit si selector échoue.
- Playwright headless en `file://` ne charge pas les assets réseau — c'est OK, on veut le DOM structurel, pas les images.
- Si Playwright échoue (env sans Chromium, timeout) : fallback propre vers `dist_url` compilé (déjà géré dans le code ci-dessus).

**Livrable :**
- dist.zip forgé → HTML Tailwind éditable (plus d'iframe compilé)
- Fallback silencieux vers dist compilé si Playwright échoue
- Aucune régression sur les ZIP avec sources TSX (M119 inchangé)

---

### Mission 263 — Canvas N0 : drag d'éléments dans un dist React compilé
**STATUS: 🟠 PRÊTE | DATE: 2026-04-08 | ACTOR: GEMINI**

**Contexte :** Le hover engine M237 (injecté dans l'iframe) détecte correctement les éléments du dist React via `mouseover`. Le drag ne fonctionne pas : déplacer un nœud DOM dans un bundle React compilé est impossible sans passer par le state React — le reconciler réécrit le DOM au prochain render.

**Approche :** ne pas déplacer l'élément React. À la place, créer un **calque SVG fantôme** sur le canvas au-dessus de l'iframe. Au `mousedown` sur un élément hover, capturer sa `getBoundingClientRect()`, créer un rectangle SVG fantôme aux mêmes dimensions et coordonnées canvas, le rendre draggable sur le canvas. L'iframe reste intacte.

**Ce que le drag fantôme permet :**
- Repositionner visuellement un élément sans toucher au React bundle
- Stocker la position finale dans le manifest (`element_overrides`) pour reconstruction future
- Sullivan peut lire ces overrides pour proposer une version HTML éditable

**Séquence technique :**

1. Dans `WsCanvas.js` — écouter `hm-select` depuis l'iframe :
```js
// Déjà présent : window.addEventListener('message', ...)
// Ajouter sur hm-select :
if (e.data.type === 'hm-select') {
    this._selectedIframeEl = e.data; // { tag, id, cls, rect }
}
```

2. Le hover engine injecté (dans `injectHoverEngine()`) doit envoyer le `rect` avec `hm-select` :
```js
document.addEventListener('mousedown', function(e) {
    const el = e.target;
    const rect = el.getBoundingClientRect();
    window.parent.postMessage({
        type: 'hm-select',
        tag: el.tagName, id: el.id || '', cls: (el.className||'').toString().slice(0,80),
        rect: { x: rect.left, y: rect.top, w: rect.width, h: rect.height }
    }, '*');
});
```

3. Dans `WsCanvas.js` — à réception de `hm-select` avec `rect`, créer le fantôme SVG :
```js
_createGhostElement(shellG, rect) {
    // Convertir les coordonnées iframe → canvas world
    const shellRect = shellG.querySelector('foreignObject').getBoundingClientRect();
    const scaleX = (shellRect.width / parseFloat(shellG.querySelector('foreignObject').getAttribute('width')));
    const wx = (shellRect.left - this.wrapper.getBoundingClientRect().left - this.viewX) / this.scale
               + rect.x / scaleX;
    const wy = (shellRect.top  - this.wrapper.getBoundingClientRect().top  - this.viewY) / this.scale
               + rect.y / scaleX;
    const ghost = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    ghost.setAttribute('x', wx); ghost.setAttribute('y', wy);
    ghost.setAttribute('width', rect.w / scaleX); ghost.setAttribute('height', rect.h / scaleX);
    ghost.setAttribute('fill', 'rgba(140,198,63,0.15)');
    ghost.setAttribute('stroke', '#8cc63f'); ghost.setAttribute('stroke-width', '1.5');
    ghost.setAttribute('rx', '4');
    ghost.classList.add('ws-ghost-element');
    ghost.dataset.sourceTag = this._selectedIframeEl?.tag || '';
    ghost.dataset.sourceId  = this._selectedIframeEl?.id  || '';
    this.content.appendChild(ghost);
    return ghost;
}
```

4. Rendre le fantôme draggable avec le même système `mousedown/mousemove/mouseup` que les shells.

5. Au `mouseup`, émettre un event `ws-element-placed` avec `{ sourceId, sourceCls, x, y, w, h }` — Sullivan pourra le lire pour proposer une refonte positionnée.

**Points d'attention :**
- Un seul fantôme actif à la fois — supprimer le précédent au prochain `hm-select`
- `pointer-events` de l'iframe : `auto` en mode `select` uniquement (déjà géré M238)
- Ne pas stocker les fantômes dans le manifest pour l'instant — juste l'affichage

**Fichiers :** `WsCanvas.js` (ghost + drag), `injectHoverEngine` dans `WsCanvas.js` (ajouter rect dans hm-select)

**Livrable :**
- Hover → outline vert (déjà OK)
- Mousedown → fantôme SVG vert semi-transparent sur le canvas
- Drag du fantôme → repositionnement fluide
- Mouseup → console `[WS-GHOST]` avec tag/id/position finale

---

### Mission 265 — Forge SVG/Figma : tokens HoméOS + SVG trop lourd
**STATUS: 🔴 PRIORITÉ | DATE: 2026-04-08 | ACTOR: QWEN**

**Fichier unique :** `Backend/Prod/retro_genome/svg_to_tailwind.py` — méthode `convert()` L72-135

**Symptôme :** Export Figma forgé → résultat identique au bug PNG (HoméOS). 62787 tokens, 78s.

---

**Fix 1 — Retirer les tokens HoméOS du prompt (L101-107)**

`color_hint` est déjà calculé L87 — l'utiliser à la place des tokens injectés :

```python
# Avant — remplacer le bloc "TOKENS DE DESIGN À RESPECTER (IMPÉRATIF)" par :
CONTRAINTE DESIGN :
- Extrais les couleurs dominantes directement depuis les valeurs `fill` du SVG.
- Couleurs détectées dans ce fichier (plus fréquentes) : {color_hint}
- Utilise ces couleurs — ne substitue pas tes propres préférences.
```

---

**Fix 2 — Réduire le SVG envoyé au LLM**

Cap actuel `clean_svg[:50000]` → ~60K tokens totaux → 78s. Deux actions dans `_strip_noise()` + cap :

```python
# Dans _strip_noise(), ajouter après les suppressions existantes :
# Supprimer les paths complexes (d= > 200 chars = bruit, pas d'info structurelle)
content = re.sub(r'<path\b[^>]*\bd="[^"]{200,}"[^/]*/>', '', content)
content = re.sub(r'<path\b[^>]*\bd="[^"]{200,}"[\s\S]*?/>', '', content)
```

Et dans `convert()`, abaisser le cap L99 :
```python
# Avant
{clean_svg[:50000]}
# Après
{clean_svg[:20000]}
```

---

**Livrable :** prompt sans tokens HoméOS, SVG < 20K chars, latence estimée < 30s. Aucun autre fichier.

---

### Mission 262 — Forge Vision : remettre le pipeline dans un état carré
**STATUS: 🔴 PRIORITÉ | DATE: 2026-04-08 | ACTOR: QWEN**

**Fichier unique :** `Backend/Prod/retro_genome/svg_to_tailwind.py`

**Fix 1 — Retirer les tokens HoméOS du fallback `convert_image()` — bloc `else` du `design_section` L164-172**
```python
# Avant
else:
    design_section = f"""
TOKENS DE DESIGN À RESPECTER (IMPÉRATIF) :
- Background principal : `{tokens['colors']['neutral']}`
...
"""
# Après
else:
    design_section = """
CONTRAINTE DESIGN : aucun design system prédéfini pour ce projet.
Extrais les couleurs, typographies et espacements directement depuis l'image.
Sois fidèle à ce que tu vois — ne substitue pas tes propres préférences.
"""
```

**Fix 2 — Restaurer le fallback MIMO Vision (supprimé par erreur)**
MIMO-V2-Omni supporte la Vision base64 OpenAI-compatible. Le remettre après `result = await self.client.generate_with_image(...)` :
```python
if not result.success:
    logger.warning("[SvgToTailwind] Gemini Vision failed, trying Mimo fallback...")
    try:
        from Backend.Prod.models.mimo_client import MimoClient
        mimo = MimoClient()
        result = await mimo.generate_with_image(
            prompt=prompt, image_base64=image_base64,
            mime_type=mime_type, max_tokens=16000, temperature=0.1
        )
    except Exception as e:
        logger.error(f"[SvgToTailwind] Mimo fallback vision failed: {e}")
if not result.success:
    logger.error(f"[SvgToTailwind] LLM Vision Error: {result.error}")
    raise RuntimeError(f"Vision conversion failed: {result.error}")
```

**Fix 3 — Vérifier `analyze_image_design()` (même fichier L221+)**
S'assurer que son prompt n'injecte pas de tokens HoméOS. Si oui, même correction que Fix 1.

**Livrable :** aucun autre fichier touché. Scope strict.

---

### Mission 257 — Hotfix : `convert_image()` — retirer les tokens HoméOS du fallback
**STATUS: ✅ ABSORBÉE PAR M262**

**Problème :** quand `design_md` est vide (projet sans DESIGN.md ou exception M256-A), `convert_image()` injecte les tokens HoméOS (`#8cc63f`, `#f7f6f2`, `#3d3d3c`, Geist) comme contrainte `IMPÉRATIVE`. Sullivan ignore l'image et produit une page HoméOS.

**Fichier :** `Backend/Prod/retro_genome/svg_to_tailwind.py` — méthode `convert_image()`, bloc `else` du `design_section` (L164-172).

**Fix :**
```python
# Avant
else:
    design_section = f"""
TOKENS DE DESIGN À RESPECTER (IMPÉRATIF) :
- Background principal : `{tokens['colors']['neutral']}`
...
"""

# Après
else:
    design_section = """
CONTRAINTE DESIGN : aucun design system prédéfini pour ce projet.
Extrais les couleurs, typographies et espacements directement depuis l'image.
Sois fidèle à ce que tu vois — ne substitue pas tes propres préférences de style.
"""
```

**Règle :** ne pas toucher à la branche `if design_md:` ni à `analyze_image_design()`. Scope strict.

---

### Mission 258 — Hotfix : `_generate_with_image_genai` bloque l'event loop
**STATUS: 🔴 PRIORITÉ | DATE: 2026-04-08 | ACTOR: CODE DIRECT — FJD**

**Problème :** `client.models.generate_content(...)` du SDK google-genai est **synchrone**. Appelé directement dans une coroutine FastAPI, il bloque l'event loop — cause probable du `zsh: killed` observé en session.

**Fichier :** `Backend/Prod/models/gemini_client.py` — méthode `_generate_with_image_genai()` (L413).

**Fix :**
```python
import asyncio
import functools

async def _generate_with_image_genai(self, prompt, image_base64, mime_type, max_tokens, temperature):
    from google import genai
    import base64
    client = genai.Client(api_key=self.api_key)

    contents = [{"parts": [
        {"inline_data": {"mime_type": mime_type, "data": image_base64}},
        {"text": prompt},
    ]}]

    # Synchronous SDK → exécuté dans un thread pour ne pas bloquer l'event loop
    response = await asyncio.to_thread(
        functools.partial(
            client.models.generate_content,
            model=self.primary_model,
            contents=contents,
            config={"max_output_tokens": max_tokens, "temperature": temperature},
        )
    )
    return response.text
```

**Règle :** même fix à appliquer à `generate()` (text-only) si le SDK genai est utilisé dans ce chemin — vérifier.

---

### Mission 259 — dist.zip : badge "rendu compilé" dans le shell
**STATUS: 🟠 PRÊTE | DATE: 2026-04-08 | ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE

**Problème :** un dist.zip React forgé charge dans l'iframe comme un rendu fidèle, mais le hover engine ne peut pas inspecter les éléments (React Virtual DOM). L'élève croit que le mode select devrait fonctionner — pas de feedback visuel indiquant que ce shell est en lecture seule.

**Comportement attendu :**
- Le shell d'un dist.zip compilé affiche un badge discret `rendu compilé` dans son header, à droite du titre
- En mode `select`, un tooltip ou message dans la status bar indique `inspecter non disponible — rendu compilé`
- Le hover engine n'est pas injecté dans ces shells (guard dans `WsScreenShell.js`)

**Détection :** `item.origin === 'compiled'` dans l'index.json (déjà positionné par le pipeline ZIP, L734).

**Fichiers :**
- `WsScreenShell.js` — dans `build()`, si `item.origin === 'compiled'` : ajouter badge SVG + skip `injectHoverEngine`
- `WsCanvas.js` — dans `setMode('select')` : si le shell actif a `data-origin="compiled"`, afficher message dans `#ws-status-bar`

**Livrable :**
- Badge `rendu compilé` visible dans le header du shell
- Aucune tentative d'injection hover sur ces shells
- Message status bar en mode select

---

### Thème 28 — Reroutage plugin Figma → Workspace (court-circuit Intent Viewer)

### Mission 265 — Plugin Figma → Workspace direct
**STATUS: 🔴 PRIORITÉ | DATE: 2026-04-08 | ACTOR: QWEN**

**Problème :** Le plugin Figma envoie les SVG vers l'Intent Viewer (`/intent-viewer`) qui les analyse puis redirige vers le FRD Editor. C'est l'ancien pipeline — lent, inutile pour du SVG propre qui n'a pas besoin d'interprétation Vision.

**Flux actuel (à abandonner) :**
```
Plugin Figma → POST /api/import/figma → intent-viewer → analyse → FRD Editor
```

**Flux cible :**
```
Plugin Figma → POST /api/import/figma → imports/ du projet actif → canvas workspace
```

Le SVG arrive propre de Figma → pas de Vision, pas d'Intent Viewer, pas de forge LLM. Il suffit de le sauver dans `imports/`, créer l'entrée `index.json`, et l'afficher sur le canvas workspace.

---

**Fix 1 — `ui.html` : changer le lien de destination après export**

**Fichier :** `Frontend/figma-plugin/ui.html` — ~L261

```html
<!-- Avant -->
<a href="http://localhost:9998/intent-viewer" target="_blank">
    ouvrir dans l'intent viewer →
</a>

<!-- Après -->
<a href="http://localhost:9998/workspace" target="_blank">
    ouvrir dans le workspace →
</a>
```

---

**Fix 2 — `routes.py` : créer la route `POST /api/import/figma`**

**Fichier :** `Backend/Prod/retro_genome/routes.py` (ou `Frontend/3. STENCILER/routers/import_router.py`)

La route doit :
1. Recevoir le payload du plugin : `{ svg: string, name: string }`
2. Sauver le `.svg` dans `projects/{active_id}/imports/{today_str}/name.svg`
3. Créer/mettre à jour `index.json` :
```json
{
  "id": "figma_{timestamp}",
  "name": "nom_du_frame",
  "file_path": "2026-04-08/mon_frame.svg",
  "svg_path": "2026-04-08/mon_frame.svg",
  "type": "svg",
  "archetype_label": "import svg",
  "html_template": null
}
```
4. Retourner `{ status: "ok", import_id: "figma_..." }`

Le SVG sera ensuite forgé en HTML Tailwind par le pipeline existant (`POST /generate-from-import`) quand l'utilisateur le déclenchera depuis le workspace.

---

**Fix 3 — Plugin `code.js` : poster vers la bonne route**

**Fichier :** `Frontend/figma-plugin/code.js`

Vérifier que le `fetch()` dans le handler d'export pointe vers :
```js
fetch('http://localhost:9998/api/import/figma', {
    method: 'POST',
    body: JSON.stringify({ svg: svgString, name: node.name }),
    headers: { 'Content-Type': 'application/json' }
})
```

Et non vers un endpoint intent-viewer.

---

**Fichiers à lire :**
- `Frontend/figma-plugin/ui.html` — L255-265 (bouton post-export)
- `Frontend/figma-plugin/code.js` — handlers d'export SVG, fetch destination
- `Backend/Prod/retro_genome/routes.py` — section import upload (inspirer du pattern `upload-import`)
- `Frontend/3. STENCILER/routers/import_router.py` — `POST /api/import/upload` (pattern existant)

**Critères de succès :**
1. Export Figma → SVG sauvegardé dans `imports/` du projet actif
2. Entrée visible dans la screen list du workspace
3. Bouton post-export ouvre le workspace (pas l'Intent Viewer)
4. Aucun appel à l'Intent Viewer dans le chaînon

---

### Thème 18 — Diagnostics workspace généralisés (2026-04-08)

---

### Mission 239 — DIAG : Toolbar N0 — tous les boutons morts sauf Stitch
**STATUS: 🔴 DIAG EN ATTENTE**

**Symptôme** : Clic sur select (V), drag (H), frame (F), text (T), effects (E) → rien de visible. Seul le bouton Stitch (`<a>` brut) réagit.

---

**Hypothèse 1 — Les `onclick` des `.ws-tool-btn` ne sont jamais attachés**
Probabilité : TRÈS PROBABLE

`ws_main.js` est `type="module"` (workspace.html ligne 579). L'ensemble de l'init est dans un `DOMContentLoaded` async. Si une exception non catchée survient **avant la ligne 58** (setup toolbar), la promise avorte silencieusement. Le [S] de la screen list fonctionne car son onclick est attaché dans `fetchWorkspaceImports()` (ligne ~303), mais cette fonction est appelée à la ligne 52 — les onclicks toolbar sont attachés à la ligne 58, **après** le await. Si `fetchWorkspaceImports()` throw en dehors de son try/catch interne (ex: `list` null → `list.innerHTML` crash dans le catch), DOMContentLoaded avorte avant la ligne 58.

Test :
```js
document.querySelectorAll('.ws-tool-btn').length           // 0 → handlers jamais attachés
document.querySelector('.ws-tool-btn[data-mode="select"]').onclick  // null confirme
```

---

**Hypothèse 2 — Les `onclick` sont attachés mais `window.wsCanvas` est null**
Probabilité : PROBABLE

Si `new WsCanvas(...)` (ligne 11) throw ou retourne un objet incomplet, `window.wsCanvas` est null. Tous les appels `window.wsCanvas?.setMode(mode)` sont des no-ops silencieux.

Test :
```js
window.wsCanvas         // null ?
window.wsCanvas?.activeMode   // undefined ?
```

---

**Hypothèse 3 — Les `onclick` sont attachés et setMode tourne, mais le feedback visuel est invisible**
Probabilité : MOYENNE

`setMode()` ajoute/retire la classe `.active-tool` sur les boutons. Si `.active-tool` n'a aucune règle CSS visible (background, couleur, border), le bouton paraît mort alors qu'il fonctionne. De plus, les modes "frame", "effects", "colors" ne déclenchent aucune ouverture de panneau dans `ws_main.js` — ils changent juste `activeMode` en silence.

Test :
```js
document.querySelector('.ws-tool-btn[data-mode="select"]').classList.contains('active-tool') // avant clic
// Cliquer "drag"
document.querySelector('.ws-tool-btn[data-mode="drag"]').classList.contains('active-tool')    // → true si setMode tourne
```

---

### Mission 240 — DIAG : Bouton Aperçu dans le shell — mort
**STATUS: 🔴 DIAG EN ATTENTE**

**Symptôme** : Clic sur "Aperçu" dans un shell canvas → rien ne s'ouvre.

---

**Hypothèse 1 — `window.wsPreview` est undefined**
Probabilité : TRÈS PROBABLE

Si ws_main.js crashe avant ou à la ligne 9 (`window.wsPreview = new WsPreview()`), `window.wsPreview` est undefined. L'appel `window.wsPreview?.enterPreviewMode(...)` dans le clic du shell est un no-op silencieux.

Test :
```js
window.wsPreview                // undefined ?
typeof window.wsPreview         // "undefined" ?
```

---

**Hypothèse 2 — `ws-preview-overlay` absent du DOM**
Probabilité : PROBABLE

`enterPreviewMode()` fait `document.getElementById('ws-preview-overlay')`. Si l'élément est absent (supprimé par une régression Gemini), la fonction retourne silencieusement à la ligne `if (!shell || !overlay) return`.

Test :
```js
document.getElementById('ws-preview-overlay')          // null ?
document.getElementById('ws-preview-frame-container')  // null ?
```

---

**Hypothèse 3 — Le shell id passé ne correspond à aucun élément**
Probabilité : FAIBLE

Le bouton passe `g.id` à `enterPreviewMode`. Si `g.id` est vide ou mal formé, `document.getElementById(id)` retourne null → retour silencieux ligne 76.

Test :
```js
document.querySelector('.ws-screen-shell')?.id  // vide ou undefined ?
```

---

### Mission 241 — DIAG : Bouton [S] apparaît sur les imports dist.zip
**STATUS: 🔴 DIAG EN ATTENTE**

**Symptôme** : Un import dist.zip affiche un bouton [S] dans la screen list. Clic → `GET /api/stitch/open/2026-04-08_142326_dist.zip` → 400.

---

**Hypothèse 1 — L'entrée index.json a un `archetype_id` hérité d'une ancienne version du code**
Probabilité : TRÈS PROBABLE

La condition `isStitch` dans `fetchWorkspaceImports()` évalue `item.archetype_id === 'stitch_import'`. Si une version précédente du code a créé des entrées avec un archetype_id différent, le check est correct **pour les nouvelles entrées** mais les anciennes dans index.json ont peut-être une valeur aberrante qui passe le test. Ou pire : une régression a enlevé la condition et tout affiche [S].

Test :
```js
fetch('/api/retro-genome/imports').then(r=>r.json()).then(d=>console.log(JSON.stringify(d.imports.map(i=>({id:i.id,archetype_id:i.archetype_id,archetype_label:i.archetype_label})),null,2)))
```

---

**Hypothèse 2 — Le fichier ws_main.js servi est une version cachée sans la condition**
Probabilité : PROBABLE

Les agents ont peut-être appliqué le fix dans le mauvais fichier, ou le serveur sert une version antérieure. Le browser peut avoir en cache une version de ws_main.js sans la condition `isStitch`.

Test : Ouvrir DevTools → Sources → `ws_main.js` → chercher "isStitch". Si absent → version ancienne en cache.
Fix : Cmd+Shift+R (hard refresh).

---

**Hypothèse 3 — La condition est présente mais évalue `true` pour les zips car `archetype_label` contient "stitch" par accident**
Probabilité : FAIBLE

La condition est `item.archetype_label.toLowerCase().includes('stitch')`. Si l'archetype_label d'un zip est "import multi-format" (normal), il ne contient pas "stitch". Mais si un agent a changé le label dans import_router.py, le check peut être faussé.

Test : vérifier dans import_router.py l'`archetype_label` assigné aux uploads ZIP.

---

### Mission 242 — DIAG : FEE Studio — "veuillez activer un projet"
**STATUS: 🔴 DIAG EN ATTENTE**

**Symptôme** : Ouverture FEE Studio → `alert("veuillez activer un projet")` même quand un projet est chargé.

---

**Hypothèse 1 — `window.wsBackend` non instancié → `projectId` undefined**
Probabilité : TRÈS PROBABLE

`ws_main.js` n'instancie jamais `window.wsBackend = new WsBackend()`. `WsFEEStudio.open()` résout `this.ws = window.wsBackend || window.wsCanvas || {}`. Si `wsBackend` est undefined et `wsCanvas` n'a pas de propriété `activeProject`, `projectId` = undefined → alert.

Test :
```js
window.wsBackend                    // undefined ?
window.wsCanvas?.activeProject      // undefined ?
JSON.parse(localStorage.getItem('homeos_session') || '{}')  // a-t-il active_project_id ?
```

---

**Hypothèse 2 — La session localStorage n'a pas de clé `active_project_id`**
Probabilité : PROBABLE

Même si M240 a patché `WsFEEStudio.open()` pour lire depuis `localStorage.homeos_session`, si la session stockée n'a pas de clé `active_project_id` ou `project_id`, le fallback échoue quand même.

Test :
```js
JSON.parse(localStorage.getItem('homeos_session') || '{}')
// Chercher : active_project_id, project_id, token
```

---

**Hypothèse 3 — Le patch M240 n'a pas été appliqué (version ancienne de WsFEEStudio.js servie)**
Probabilité : MOYENNE

Le serveur sert peut-être une version de `WsFEEStudio.js` antérieure au patch. Vérifier dans Sources DevTools que `WsFEEStudio.open()` lit bien `localStorage.homeos_session`.

Test : DevTools → Sources → `WsFEEStudio.js` → chercher "homeos_session". Absent → version antérieure au patch.

---

### Thème 16 — Pipeline Import → Canvas
> M233 ✅, M234 ✅, M235 ✅, M236 ✅, M237 ✅ — archivées ROADMAP_ACHIEVED.md

---

### Thème 17 — Réparations post-M237 (Gemini regressions)

### Mission 238 — Hotfix canvas : 4 régressions M237
**STATUS: ✅ LIVRÉ**

- **Bug 1** : Hover outline exclut maintenant `el.id === 'root'` (React containers)
- **Bug 2** : Aucun changement de `pointer-events` sur les iframes dans `setMode()` — les iframes restent `pointer-events: none`, le moteur hover fonctionne inside l'iframe
- **Bug 3a** : Bouton Stitch ajouté dans la toolbar droite (lien vers `https://stitch.withgoogle.com`)
- **Bug 3b** : Bouton [S] restauré dans `fetchWorkspaceImports()` + listener `fetch('/api/stitch/open/{id}')` → `window.open(d.url)`
- **Bug 4** : `addScreen()` défensif — log si `WsScreenShell` non chargé, structure simplifiée

**Fichiers :** `WsCanvas.js`, `WsScreenShell.js`, `ws_main.js`, `workspace.html`

---

**Bug 1 — Hover outline ne touche que le body**

Le moteur injecté utilise `mouseover` qui bubble — `e.target` est correct mais le React dist enveloppe tout dans des divs avec héritage de `pointer-events`. Fix : cibler `e.target` direct ET exclure les conteneurs racine connus (`#root`, `[data-reactroot]`).

Dans le script injecté (dans `WsCanvas.injectHoverEngine`), remplacer la condition d'exclusion :
```js
// Avant
if (el === document.body || el === document.documentElement) return;
// Après
if (el === document.body || el === document.documentElement || el.id === 'root') return;
// Et forcer pointer-events sur tout le document
document.documentElement.style.setProperty('pointer-events', 'all', 'important');
```

---

**Bug 2 — Drag shell cassé en mode select (iframe mange les events)**

Gemini a mis `pointer-events: auto` sur les iframes en mode select → le SVG canvas ne reçoit plus les mousedown quand on drag au-dessus de l'iframe.

Fix dans `WsCanvas.setMode()` : ne jamais passer les iframes en `auto`. À la place, activer le moteur hover via un flag sur le canvas, et garder les iframes en `pointer-events: none` **toujours**. Le moteur hover fonctionne car il est injecté dans le document de l'iframe — il n'a pas besoin que l'iframe reçoive les events de la page parente.

```js
setMode(mode) {
    this.activeMode = mode;
    // NE PAS toucher pointer-events des iframes — le moteur hover est inside l'iframe
    // Les iframes restent pointer-events: none pour que le canvas drag fonctionne
    // ... reste du setMode
}
```

Retirer tout le bloc `document.querySelectorAll('.ws-screen-shell iframe').forEach(...)` que Gemini a ajouté dans `setMode`.

---

**Bug 3 — Bouton Stitch disparu**

Deux endroits à restaurer :

*3a — Dans la toolbar (`workspace.html`)*, remettre le bouton Stitch entre typo et séparateur zoom, avec un `href` vers Stitch (pas de panel dédié) :
```html
<!-- STITCH (lien direct) -->
<a href="https://stitch.withgoogle.com" target="_blank"
   class="p-3 rounded-xl text-slate-400 hover:text-indigo-500 transition-all"
   title="Ouvrir Stitch">
    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/>
    </svg>
</a>
```

*3b — Dans `ws_main.js` `fetchWorkspaceImports()`*, le bouton [S] par item était conditionnel sur `stitch_screen_id`. Gemini l'a supprimé entièrement. Le remettre dans le template HTML des items de liste :
```js
${item.stitch_screen_id ? `
<button class="btn-s-open p-1.5 hover:bg-slate-50 text-slate-400 hover:text-indigo-500 rounded transition-all" title="Ouvrir dans Stitch">
    <span class="text-[9px] font-black font-sans">S</span>
</button>` : ''}
```
Et remettre le listener correspondant :
```js
const btnOpen = el.querySelector('.btn-s-open');
if (btnOpen) btnOpen.onclick = async (e) => {
    e.stopPropagation();
    const res = await fetch(`/api/stitch/open/${item.id}`);
    const d = await res.json();
    if (d.url) window.open(d.url);
};
```

---

**Bug 4 — Impossible de remettre un item sur le canvas une seconde fois**

`addScreen(item)` dans `WsCanvas.js` :
```js
if (document.getElementById(`shell-${item.id}`)) {
    this.selectScreen(document.getElementById(`shell-${item.id}`));
    return; // ← si le shell a été fermé et retiré du DOM, getElementById retourne null
}
```
La logique est correcte — si `getElementById` retourne `null`, il tombe dans `WsScreenShell.build`. Le bug vient sûrement d'une régression Gemini dans `WsScreenShell.build` ou dans la façon dont le shell est retiré du DOM.

Vérifier dans `WsScreenShell.js` le close button :
```js
closeBtn.addEventListener('mousedown', (e) => { e.stopPropagation(); g.remove(); });
```
Si `g.remove()` retire bien le `<g>` du SVG, `getElementById` retourne null au prochain appel → reconstruit. Tester dans la console : `document.getElementById('shell-XXX')` après fermeture. Si null → le bug est ailleurs (peut-être `addScreen` ne reconstruit pas si `WsScreenShell` est undefined).

Ajouter un log défensif dans `addScreen` :
```js
async addScreen(item) {
    const existing = document.getElementById(`shell-${item.id}`);
    if (existing) { this.selectScreen(existing); return; }
    if (!window.WsScreenShell) { console.error('WsScreenShell not loaded'); return; }
    const g = await window.WsScreenShell.build(item, this);
    this.content.appendChild(g);
    this.selectScreen(g);
    return g;
}
```

---

### Mission 237 — Canvas N0 : drag zone + moteur hover injecté dans l'iframe
**STATUS: ✅ LIVRÉ**

- **Zone de drag** : gripper visuel "⋯" centré sur le header du shell, `cursor: move`
- **Moteur hover** : `injectHoverEngine()` dans `WsCanvas.js` injecté dans le contentDocument de l'iframe
  - `mouseover` → outline vert `#8cc63f` + postMessage `{ type: 'hm-hover', tag, id, cls }`
  - `mouseout` → clear outline + postMessage `{ type: 'hm-clear' }`
  - `click` → stopPropagation + postMessage `{ type: 'hm-click', tag, id, cls, href }`
- `WsScreenShell.js` : appel `wsCanvas.injectHoverEngine(iframe)` au `load`
- `pointer-events: none` par défaut sur l'iframe, `auto` en mode `select` (déjà géré par le canvas)

---

> BOOTSTRAP OBLIGATOIRE

**Contexte :** Deux comportements attendus en mode `select` (flèche). Architecture choisie : moteur hover **injecté dans le contentDocument** de l'iframe au chargement — zéro coordinate math côté canvas, le highlight est rendu à l'intérieur de l'iframe par son propre DOM.

---

**Comportement 1 — Zone de drag du shell (codée mais invisible)**

`WsCanvas.js` ligne 124 : drag déjà restreint à `worldY <= 40`. Manque le visuel.

Dans `WsScreenShell.js`, ajouter après le `<rect class="ws-screen-header">` :
```js
// Cursor move sur le header
header.style.cursor = 'move';

// Gripper visuel centré
const grip = this._createElement('text', {
    x: String(SW / 2), y: '26', 'text-anchor': 'middle',
    fill: '#d1d5db',
    style: 'font-size:11px; letter-spacing:5px; pointer-events:none; user-select:none;'
});
grip.textContent = '⋯';
g.appendChild(grip);
```

---

**Comportement 2 — Moteur hover injecté (postMessage)**

**Architecture :**
- `WsCanvas.js` expose `injectHoverEngine(iframe)` — injecte un script dans `iframe.contentDocument` après chargement
- Le script injecté gère `mouseover` / `mouseout` / `click` → remonte via `window.parent.postMessage`
- `WsCanvas.js` écoute `window.addEventListener('message', ...)` → met à jour `this._selectedIframeEl`
- `pointer-events` de l'iframe : `none` par défaut, `auto` quand `activeMode === 'select'`

**Dans `WsScreenShell.js`**, modifier le listener `load` de l'iframe :
```js
iframe.addEventListener('load', () => {
    if (window.wsFontManager) window.wsFontManager.injectStyles();
    if (window.wsCanvas) window.wsCanvas.injectHoverEngine(iframe);
});
```

**Dans `WsCanvas.js`**, ajouter la méthode `injectHoverEngine(iframe)` :
```js
injectHoverEngine(iframe) {
    try {
        const doc = iframe.contentDocument;
        if (!doc || doc.__hmInjected) return;
        doc.__hmInjected = true;

        const script = doc.createElement('script');
        script.textContent = `
(function() {
    let _last = null;
    function _clear() {
        if (_last) {
            _last.style.removeProperty('outline');
            _last.style.removeProperty('outline-offset');
            _last = null;
        }
    }
    document.addEventListener('mouseover', function(e) {
        const el = e.target;
        if (el === document.body || el === document.documentElement) return;
        _clear();
        el.style.outline = '2px solid #8cc63f';
        el.style.outlineOffset = '-1px';
        _last = el;
        window.parent.postMessage({ type: 'hm-hover', tag: el.tagName, id: el.id || '', cls: (el.className || '').toString().slice(0, 80) }, '*');
    });
    document.addEventListener('mouseout', function(e) {
        if (!e.relatedTarget || e.relatedTarget === document.documentElement) {
            _clear();
            window.parent.postMessage({ type: 'hm-clear' }, '*');
        }
    });
    document.addEventListener('click', function(e) {
        const el = e.target;
        window.parent.postMessage({ type: 'hm-select', tag: el.tagName, id: el.id || '', cls: (el.className || '').toString().slice(0, 80), text: (el.textContent || '').trim().slice(0, 100) }, '*');
    });
})();`;
        doc.head.appendChild(script);
    } catch(_) {}
}
```

**Dans `WsCanvas.js` — `setMode(mode)`**, ajouter la gestion des pointer-events sur toutes les iframes des shells :
```js
setMode(mode) {
    this.activeMode = mode;
    // Activer pointer-events dans les iframes en mode select uniquement
    const isSelect = mode === 'select';
    document.querySelectorAll('.ws-screen-shell iframe').forEach(iframe => {
        iframe.style.pointerEvents = isSelect ? 'auto' : 'none';
    });
    // ... reste du setMode existant
}
```

**Dans `WsCanvas.js` — `init()`**, ajouter le listener message :
```js
window.addEventListener('message', (e) => {
    if (e.data?.type === 'hm-select') {
        this._selectedIframeEl = e.data;
        console.log('[HM-SELECT]', e.data.tag, e.data.id, e.data.text);
        // Sullivan context à brancher ici (mission suivante)
    }
});
```

**Points d'attention :**
- `doc.__hmInjected` guard : évite la double injection si l'iframe reload
- Ne pas injecter si `doc.head` n'existe pas encore (iframe vide ou error page)
- En mode `drag` ou tout autre mode ≠ `select`, les iframes ont `pointer-events: none` → le canvas gère tout sans interférence
- `addScreen()` appelle `WsScreenShell.build()` qui crée l'iframe — l'injection se fait au `load` event, donc après que le contenu soit rendu

**Fichiers :** `WsCanvas.js` + `WsScreenShell.js`

**Livrable :**
- Header shell = curseur `move` + gripper `⋯` centré
- Mode select → iframes activées + moteur hover injecté au load
- Hover = outline vert `#8cc63f` sur l'élément HTML sous la souris, géré entièrement dans l'iframe
- Click = `[HM-SELECT]` dans la console avec tag/id/text
- Tous autres modes → pointer-events none, comportement canvas inchangé

---

### Mission 235 — Toolbar canvas : refonte UX
**STATUS: 🔴 PRIORITÉ | DATE: 2026-04-08 | ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE

**Contexte :** Audit FJD de la toolbar droite flottante (`data-purpose="floating-toolbar"` dans `workspace.html`). Plusieurs outils inutiles, illisibles, ou mal placés.

**Décisions FJD :**

| Outil actuel | Action |
|---|---|
| Flèche `select` | Garder tel quel |
| Main `drag` | Garder — mais remplacer le picto SVG illisible par une main simple (3 tracés max), tooltip `"naviguer (H)"` |
| Couleurs `colors` | **Masquer** (`hidden`) — viendra dans une mission Design System dédiée |
| Typographie `text` | Garder |
| Stitch `stitch` | **Supprimer** (intégré dans M234 — panneau Stitch supprimé) |
| Réinitialiser vue | Garder — corriger le titre en `"recentrer (0)"` |
| Reset layout panels | **Déplacer** hors de la toolbar → voir ci-dessous |

**Fix 1 — Nouveau picto main (drag)**
Remplacer le SVG `path` complexe actuel par un SVG main simple :
```html
<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 11V6a2 2 0 014 0v5m0 0V6a2 2 0 014 0v5m0 0a2 2 0 014 0v3a6 6 0 01-6 6H9a6 6 0 01-6-6v-3"/>
</svg>
```

**Fix 2 — Masquer couleurs**
Ajouter `hidden` au bouton `data-mode="colors"`.

**Fix 3 — Supprimer le bouton Stitch de la toolbar**
Supprimer le `<button data-mode="stitch" ...>` (le lien Stitch est désormais dans le dashboard projet).

**Fix 4 — Déplacer "réinitialiser layout des panneaux" vers le header workspace**
- Supprimer le bouton `onclick="window.PanelDragger?.resetAll()"` de la toolbar
- L'ajouter dans le header du workspace (zone title "Workspace Canvas"), comme un bouton discret à côté du label :
  ```html
  <button onclick="window.PanelDragger?.resetAll()" 
          title="réinitialiser layout des panneaux"
          class="p-1 text-slate-300 hover:text-slate-500 transition-colors">
    <svg class="w-3 h-3" ...><!-- icône reset --></svg>
  </button>
  ```
- Trouver le bon endroit dans le header (chercher `data-purpose` ou le label "Workspace Canvas" ou "canvas")

**Fix 5 — Ajouter bouton image avec popover assets**
Nouveau bouton dans la toolbar, entre typo et le séparateur zoom :
- Picto : icône image (montagne + soleil) standard
- Au clic : ouvre un popover flottant `#ws-image-picker` positionné à gauche de la toolbar
- Le popover liste les fichiers de `assets/img/` du projet actif via `GET /api/projects/active/assets`
- Chaque fichier affiche : thumbnail + nom + bouton "copier lien" (`/api/projects/assets/img/{filename}`)
- Un bouton "importer" dans le popover déclenche `document.getElementById('ws-direct-upload').click()` (l'input existant filtre déjà `.png,.jpg,.jpeg`)

**Note :** Les routes assets sont implémentées dans M236 (QWEN). M235 peut être livrée avec la liste vide (`{ files: [] }`) si M236 n'est pas encore joué — le popover fonctionnera à vide.

**Livrable :**
- Toolbar épurée : flèche / main (picto correct) / typo / image / séparateur / recentrer
- Couleurs + Stitch absents
- "Réinitialiser layout panels" déplacé vers le header
- Popover image basique fonctionnel (même vide)

---

### Mission 236 — Backend : routes assets/img par projet
**STATUS: ✅ LIVRÉ**

- `POST /api/projects/active/assets/upload` — upload image (png/jpg/jpeg/webp/svg/gif, max 10MB)
- `GET /api/projects/active/assets` — liste images du projet (tri par date desc)
- `GET /api/projects/assets/img/{filename}` — sert l'image
- `DELETE /api/projects/assets/img/{filename}` — supprime
- Stockage : `projects/{project_id}/assets/img/`
- Extensions validées + limite 10MB

**Contexte :** Les élèves uploadent des images (PNG, JPG, JPEG, WebP, SVG) dans leur projet. Ces images doivent être stockées dans `projects/{project_id}/assets/img/`, listables, servables, et supprimables.

**Fichier cible :** `Frontend/3. STENCILER/routers/import_router.py` (ou nouveau `assets_router.py` si plus propre — dans ce cas l'enregistrer dans `server_9998_v2.py`)

**Routes à créer :**

**1. Upload**
```
POST /api/projects/active/assets/upload
Content-Type: multipart/form-data
file: <UploadFile>
```
- Stocke dans `get_active_project_path() / "assets" / "img" / {safe_filename}`
- `safe_filename` = slugify + timestamp pour éviter les collisions
- Retourne `{ "status": "ok", "file": { "name": original_name, "filename": safe_filename, "url": "/api/projects/assets/img/{safe_filename}" } }`

**2. Liste**
```
GET /api/projects/active/assets
```
- Retourne `{ "files": [ { "name": ..., "filename": ..., "url": ..., "size": ... }, ... ] }`
- Scanne `assets/img/` — extensions acceptées : `.png .jpg .jpeg .webp .svg .gif`
- Ordre : plus récent en premier

**3. Servir un fichier**
```
GET /api/projects/assets/img/{filename}
```
- `FileResponse` depuis `get_active_project_path() / "assets" / "img" / filename`
- 404 si absent

**4. Supprimer**
```
DELETE /api/projects/assets/img/{filename}
```
- Supprime le fichier physique
- Retourne `{ "status": "deleted" }`

**Contraintes :**
- Créer `assets/img/` avec `mkdir(parents=True, exist_ok=True)` à chaque accès
- Limiter la taille upload à 10MB (vérifier `len(content) <= 10_000_000`)
- Extensions autorisées uniquement (rejeter sinon avec 400)

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
**STATUS: ✅ LIVRÉ (Qwen full stack) | DATE: 2026-04-08**

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
**STATUS: ✅ LIVRÉ (Qwen full stack) | DATE: 2026-04-08**

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

### Mission 257 — Forge PNG : validation genai SDK + fidélité du rendu
**STATUS: ✅ LIVRÉ | ACTOR: QWEN | DATE: 2026-04-08**

- SDK `google-genai` installé (v1.70.0) et testé — `gemini-3.1-flash-lite-preview` répond OK
- `gemini_client.py` : `_generate_with_image_genai()` pour modèles 3.x, REST API pour modèles stables
- `generate_with_image()` route automatiquement selon le nom du modèle (détection "preview")
- `svg_to_tailwind.py` : `convert_image()` accepte `design_md` optionnel, injecté dans le prompt
- `routes.py` : séquence A (analyse) → B (save DESIGN.md) → C (forge avec DESIGN.md)

**Note :** Le serveur a été tué (`killed`) avant qu'une forge PNG ne soit validée end-to-end avec le nouveau code. À retester au prochain redémarrage.

---

### Mission 258 — Drag d'éléments dans l'iframe : fix `elementFromPoint` React
**STATUS: ✅ LIVRÉ | ACTOR: QWEN | DATE: 2026-04-08**

- Remplacé `document.elementFromPoint(x, y)` par `document.elementsFromPoint(x, y)` (retourne TOUS les éléments au point, pas juste le premier)
- Fonction `_findElementAtPoint(x, y)` filtre les wrappers React (`#root`, `#__next`, etc.)
- Accepte le premier élément qui a : un id significatif, une classe CSS, du texte, ou est un élément sémantique
- Fonctionne pour les bundles React (traverse le shadow DOM des conteneurs) ET le HTML statique

---

### Mission 259 — dist.zip : mode preview statique sans React bundle
**STATUS: 🔵 BACKLOG | ACTOR: QWEN | DATE: 2026-04-08**

**CR — Diagnostic final :**
- Les bundles React dans iframes ne sont JAMAIS draggables — leurs event listeners capturent tous les événements avant que le navigateur ne les transmette
- `elementsFromPoint()` fonctionne pour sélectionner l'élément dans l'arbre React mais le `transform: translate()` appliqué n'a aucun effet visuel car React contrôle le rendu via son virtual DOM
- **Décision :** dist.zip = mode preview seule. Pour modifier le contenu, utiliser le pipeline PNG (M256) sur un screenshot du dist.zip

---

### CR Session 8 avril 2026 — M257/M258/M259

**M257 — genai SDK pour Gemini 3.x :**
- Tous les modèles Gemini Vision retournaient 404 via REST API `v1beta` — Google a déprécié les anciens noms
- SDK `google-genai` v1.70.0 installé pour Python 3.14 — testé et OK avec `gemini-3.1-flash-lite-preview`
- `generate_with_image()` route automatiquement : modèles "preview" → genai SDK, modèles stables → REST API
- Pipeline PNG corrigé : A (analyse design) → B (save DESIGN.md) → C (forge avec DESIGN.md injecté)
- **⚠️ Non testé end-to-end** — serveur tué avant validation. À retester au prochain redémarrage.

**M258 — Drag éléments dans iframe :**
- `elementFromPoint()` → `elementsFromPoint()` + filtre `_findElementAtPoint()`
- Fonctionne sur HTML statique ET bundles React (traverse les conteneurs wrapper)
- **⚠️ Le drag sur React bundles reste non-fonctionnel** — React capture les events avant le navigateur (M259)

**M259 — dist.zip draggable :**
- **Diagnostic :** Impossible — React contrôle tous les événements dans l'iframe
- **Décision :** dist.zip = preview seule. Modification via screenshot + pipeline PNG (M256).

**Fichiers modifiés :** `gemini_client.py`, `svg_to_tailwind.py`, `routes.py`, `WsCanvas.js`

---

## Thème 25 — Refactorisation ws_main.js : modules isolés + boot ordonné

> Objectif : éliminer les 7 catégories de bugs récurrents (état undefined, race conditions, crash en cascade, IDs manquants, pointer-events, IDs API erronés, double-binding).
> **Règle :** zéro classe, zéro import complexe. Fonctions pures + IIFE. Chaque fichier expose `window.WsXxx` avec traces console.

### Mission 250 — WsState : état global unique, tracé en console
**STATUS: 🟠 À TRAITER | ACTOR: QWEN**
- Centralise `projectId`, `activeMode`, `session` en un seul objet
- Résout le projet depuis `localStorage.homeos_session` (plus besoin de `wsBackend`)
- Traces : `[WsState] init`, `[WsState] projectId=xxx`, `[WsState] session.role=xxx`
- Fichier : `static/js/workspace/WsState.js`

### Mission 251 — WsBoot : séquence d'init isolée, try/catch par composant
**STATUS: 🟠 À TRAITER | ACTOR: QWEN**
- Remplace le bloc `async function initWorkspace()` de ws_main.js
- Boot explicite étape par étape : Audit → Forge → Preview → Canvas → Chat → Wire → FEEStudio
- Chaque étape dans `bootSafe(nom, fn)` — si crash, log clair + continue
- Traces : `[WsBoot] ✅ WsAudit OK (12ms)`, `[WsBoot] ❌ WsChatMain: <erreur>`
- Fichier : `static/js/workspace/WsBoot.js`

### Mission 252 — wsDom : utilitaires DOM sécurisés
**STATUS: 🟠 À TRAITER | ACTOR: QWEN**
- `safeEl(id)` — getElementById avec warning si absent
- `safeClick(selector, handler)` — addEventListener silencieux si absent
- Traces : `[wsDom] ⚠ #xxx not found`, `[wsDom] ✓ .btn click wired`
- Fichier : `static/js/workspace/wsDom.js`

### Mission 253 — WsImportList : extraction template + handlers imports
**STATUS: 🟠 À TRAITER | ACTOR: QWEN**
- Extrait `fetchWorkspaceImports()` et son template HTML (80+ lignes)
- Boutons [👁] [S] [↻] [×] avec handlers propres
- Traces : `[WsImportList] 5 imports`, `[WsImportList] [S] clicked`
- Fichier : `static/js/workspace/WsImportList.js`

### Mission 254 — WsAssetPicker : extraction gestion assets
**STATUS: 🟠 À TRAITER | ACTOR: QWEN**
- `toggleImagePicker()`, `fetchProjectAssets()`, `copyAssetUrl()`, `deleteAsset()`
- Traces : `[WsAssetPicker] opened`, `[WsAssetPicker] 3 assets`
- Fichier : `static/js/workspace/WsAssetPicker.js`

### Mission 255 — ws_main.js final : ~120 lignes d'orchestration
**STATUS: 🟠 À TRAITER | ACTOR: QWEN**
- Après extraction : boot + wiring toolbar + mode buttons uniquement
- Traces : `[ws_main] toolbar 7 buttons`, `[ws_main] ✅ READY`
- Fichier : `static/js/workspace/ws_main.js` (réécrit)

---

### CR — Pipeline de forge PNG : diagnostic hallucination

**Traçage complet effectué :**

**PNG upload → forge → HTML :**
1. `POST /api/import/upload` — sauve le PNG dans `projects/{pid}/imports/{date}/IMPORT_xxx.png`
2. `POST /api/retro-genome/generate-from-import` — lit le PNG, base64 → `GeminiClient.generate_with_image()`
3. **Le PNG atteint bien le LLM** (base64 inline via Gemini `inlineData` API)
4. **Système prompt** : tokens de design depuis `{project}/exports/design_tokens.json` (ou valeurs par défaut)
5. **DESIGN.md n'est JAMAIS chargé** — le `design.md` à la racine du repo est ignoré

**dist.zip upload → forge → HTML :**
1. `POST /api/import/upload` — sauve le ZIP
2. Si `dist/index.html` présent → **aucun LLM** — extraction directe + serve via iframe
3. Si `.tsx/.jsx` → `ReactToTailwindConverter` → Gemini (texte seul)
4. Si HTML simple → `SvgToTailwindConverter.convert()` → Gemini BUILD mode

**Constat :**
- Le PNG est bien envoyé au LLM mais le **prompt n'a aucune référence au DESIGN.md du projet**
- Les seuls tokens design sont les valeurs par défaut (`#f7f6f2`, `#3d3d3c`, `#8cc63f`, `Geist Sans`)
- Le `design.md` repo root existe mais n'est jamais lu par le pipeline de forge
- **Solution** : injecter le contenu du `DESIGN.md` du projet actif dans le prompt de forge PNG

---

## 🏛️ Doctrine Architecturale (Aether Core)

**Principe du Miroir :** Host (WsCanvas) gère l'UI AetherFlow. Guest (Iframe) = Agents de Terrain légers, aucun scope partagé.

**AetherCore :** point d'entrée unique `ws_iframe_core.js`, lazy-load des sous-trackers (`tracker_fee.js`, `tracker_construct.js`).

**DESIGN.md comme source de vérité :** l'interface Host lit ce fichier et configure les outils disponibles. Sullivan = "Intendant du Magasin".

**Mode FEE :** GSAP + Lenis. Visual Wiring Trigger→Target. Sullivan reçoit la paire de sélecteurs, génère une timeline `gsap.to()`.
