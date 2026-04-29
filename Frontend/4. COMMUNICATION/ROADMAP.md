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

2. OVERLAYS & Z-INDEX
   Un overlay `hidden` sur un parent = ses enfants sont invisibles même si LEUR hidden est retiré.

3. RÈGLE DE LIVRAISON
   Ne pas marquer TERMINÉ avant d'avoir testé manuellement le comportement dans le browser.

4. SCOPE STRICT
   Ne pas refactoriser les fichiers existants stables sans instruction explicite.

5. STYLE HOMÉOS
   Pas de majuscules dans les labels UI. Pas d'emojis. Border-radius max `rounded-[20px]`.
   Vert HoméOS (#8cc63f) uniquement en nudge — jamais en fond large.

6. ICÔNES — SVG INLINE UNIQUEMENT
   Règle : utiliser des SVG inline Lucide-style (viewBox 0 0 24 24, stroke currentColor, fill none, stroke-width 1.8).
```

---

## 🧠 BOOTSTRAP BACKEND — RÈGLE ASYNC (CRITIQUE)

```
INTERDICTION ABSOLUE : nest_asyncio.apply()
RÈGLE : pour exécuter du code synchrone bloquant dans un contexte async FastAPI, utiliser asyncio.to_thread(fn, *args).
```

---

## 🧠 BOOTSTRAP BACKEND — RÈGLE REDÉMARRAGE

```
RÈGLE OBLIGATOIRE : après toute mission livrée en backend, le serveur DOIT être redémarré (bash start.sh).
```

---

## Sprint actif — 2026-04-27

| Mission | Titre | Status | Actor |
|---------|-------|--------|-------|
| SPR_APR | Missions M327 à M362 | ✅ ARCHIVÉES | GEMINI |
| M363 | M356 enrichi : détection illustrative + spécimens | ✅ TERMINÉE | GEMINI |
| M364 | Sullivan ME : questionnaire images + forge différenciée | ✅ TERMINÉE | GEMINI |
| BKG-1 | Gemini 2.5 Flash : guillemets typographiques dans JSON M356 | 🟡 BACKLOG | — |
| BKG-2 | M363 : extraction parallèle — 5 threads simultanés (1 par fichier uploadé) | 🟡 BACKLOG | — |
| BKG-3 | M363 : `design_tokens: null` dans manifest → crash `NoneType not subscriptable` | ✅ HOTFIX | CLAUDE |
| BKG-4 | `google-genai` SDK absent du venv → `generate_with_image` silencieusement vide | ✅ HOTFIX | CLAUDE |
| BKG-5 | Sullivan `image_trigger` : bouton "analyser" lance extraction + attend 15s flat | 🟡 BACKLOG | GEMINI |
| BKG-6 | `wire_router.py` : `pending_intents: null` → crash 500 sur `/pre-wire/validate` | ✅ HOTFIX | CLAUDE |
| BKG-7 | `WsWire._syncNudgesToIframe` : timeout non catchés → spam console (cosmétique) | 🟡 BACKLOG | GEMINI |
| M365 | Wiring : rebrancher X-User-Token dans WsWire.js | ✅ TERMINÉE | GEMINI |
| M366 | Wire overlay : bouton "Cadrage LLM" → "retour manifeste" | ✅ TERMINÉE | GEMINI |
| M367 | Sullivan ME : une carte de choix par illustration détectée | 🟠 À TRAITER | GEMINI |
| M368 | Project panel : thumbnails écrans + canvas PNG visible | 🟠 À TRAITER | GEMINI |
| M369 | Gate pré-forge : décision image par asset avant forge | 🟠 À TRAITER | GEMINI |
| M350 | Vue "Live Watch" (Drill Status Polling) | 🟠 À TRAITER | GEMINI |
| M351 | Notation Automatique par Référentiel | 🟠 À TRAITER | CLAUDE |


---

## Thème 43 — Forge Intelligence Illustrative

### M363 — design_token_extractor.py : détection illustrative + spécimens
**STATUS: ✅ CODE LIVRÉ — ⚠️ NON VALIDÉ EN PROD | ACTOR: GEMINI**

### CR — Mission M363 (Intelligence Illustrative)
- **Prompt Vision** : Enrichissement pour détecter les régions illustratives (portraits, icons, photos) avec `count` et `bbox`.
- **Pipeline PIL** : Implémentation de `_process_specimens` (async via threads) qui crop, thumbnail (200px) et sauvegarde les miniatures dans `projects/{id}/assets/img/`.
- **Persistance** : Les assets sont injectés dans `manifest.json["design_tokens"]["image_assets"]`.

### CR — Débuggage M363 (2026-04-27, Claude)

**Bugs corrigés :**
1. `google-genai` SDK absent du venv → `generate_with_image` échouait silencieusement sur tous les modèles preview (3.x). Fix : `pip install google-genai` dans le venv AetherFlow. Confirmé fonctionnel : Gemini Vision retourne bien `image_assets: 1` dans les logs après fix.
2. `design_tokens: null` dans manifest existant → `.get("design_tokens", default)` retourne `None` (pas le default), crash `'NoneType' object is not subscriptable` à la ligne de merge. Fix : remplacé par `manifest.get("design_tokens") or {default}`.
3. Race condition extraction : 5 threads simultanés (un par fichier uploadé) passaient tous le guard `_ACTIVE_EXTRACTIONS` avant qu'aucun n'ait appelé `.add()`. Fix : `_ACTIVE_EXTRACTIONS.add(active_id)` déplacé avant le spawn du thread.

**État au 2026-04-27 :**
- Gemini Vision détecte bien les `image_assets` (confirmé en logs : `image_assets: 1` sur ecran test Blart Samuel).
- `_process_specimens` : statut inconnu — le pipeline crashait avant d'y arriver (bug 2). Après fix, non retesté faute de temps.
- Sullivan ME affiche maintenant un `image_trigger` visible même sans assets (bouton "analyser les illustrations").
- Le bouton attend 15s flat puis relance la critique — temporisation non adaptative (BKG-5).
- Résultat final côté étudiant : rien de visible. Cause probable : timing (extraction pas terminée quand la critique est appelée) ou `_process_specimens` échoue encore silencieusement.

**Pour reprendre :**
- Tester `_process_specimens` isolément sur un projet avec `image_assets` détectés.
- Vérifier que `specimen_url` est bien écrit dans `manifest.json["design_tokens"]["image_assets"]` après extraction.
- Vérifier que `ManifestSullivan.js` reçoit bien les specimens via `getDesignTokens()` → `manifestData.design_tokens.image_assets`.
- Si specimens OK → le rendu `image_choice` fonctionne (validé via test curl).

---

---

## Thème 35 — Dashboard Prof : Suivi & Analytics

### M367 — Sullivan ME : une carte de choix par illustration détectée
**STATUS: 🟠 À TRAITER | ACTOR: GEMINI**

**Contexte :**
M364 a livré une seule question globale (`image_choice`) avec tous les spécimens en carousel et un unique choix binaire pour le lot entier. La cible est : **une carte par illustration détectée**, chacune affichant son spécimen + deux boutons radio ("tenter en vecteur" / "aplatir en image"). Le choix est enregistré individuellement dans le manifest par asset.

**État actuel (à modifier) :**
- `sullivan_router.py` ligne ~826 : génère UNE question `image_choice` avec `specimens: image_assets[:4]`
- `ManifestSullivan.js` lignes 164-213 : rend UN bloc avec carousel + deux boutons globaux

**Fichiers à modifier :**
1. `Frontend/3. STENCILER/static/js/ManifestSullivan.js`
2. `Frontend/3. STENCILER/routers/sullivan_router.py`
3. `Frontend/3. STENCILER/static/js/ManifestBox.js` (fix cache stale — PRIORITAIRE)

---

**Changement 0 — `ManifestBox.js` (BLOQUANT — fix cache stale)**

`manifestData` est chargé une fois à l'ouverture du ManifestBox. Si l'extraction tourne après, `design_tokens` dans le cache reste `null` et Sullivan ne voit jamais les assets.

Dans `ManifestSullivan.js`, la fonction `launchCritique()` (ligne ~109) envoie `design_tokens: _refs.getDesignTokens() || {}`. Remplacer par un fetch frais du manifest avant d'appeler Sullivan :

```js
// AVANT (ligne ~121)
design_tokens: _refs.getDesignTokens() || {}

// APRÈS : récupérer les design_tokens frais depuis le manifest API
const sess2 = _refs.getSession();
let fresh_dt = _refs.getDesignTokens() || {};
try {
    const freshRes = await fetch(`/api/projects/${sess2.projectId || window.__WsState?.projectId}/manifest`,
        { headers: { 'X-User-Token': sess2.token || '' } });
    const freshManifest = await freshRes.json();
    if (freshManifest.design_tokens) fresh_dt = freshManifest.design_tokens;
} catch(_) {}
// puis utiliser fresh_dt à la place de _refs.getDesignTokens()
```

---

**Changement 1 — `sullivan_router.py`**

Remplacer la génération d'une seule question par une question par asset. Le prompt Groq reste mais devient une description courte par asset plutôt qu'une question Groq (trop lent pour N assets — remplacer par un label descriptif direct).

```python
# AVANT : une question globale
special_q = {
    "id": "img_q",
    "type": "image_choice",
    "text": q_res.code.strip(),
    "specimens": image_assets[:4]
}
questions.insert(0, special_q)

# APRÈS : une question par asset (max 4)
for i, asset in enumerate(image_assets[:4]):
    questions.insert(i, {
        "id": f"img_q_{i}",
        "type": "image_choice",
        "text": asset.get("description", f"illustration {i+1}"),
        "specimen": asset  # UN seul specimen, pas une liste
    })
```

Supprimer l'appel Groq pour la question — le label vient directement de `asset["description"]` (déjà en français, produit par Gemini Vision).

**Changement 2 — `ManifestSullivan.js`**

Pour `q.type === 'image_choice'`, remplacer le rendu carousel par une carte par question :
- Image du spécimen : `q.specimen.specimen_url` (singular, pas `q.specimens`)
- Taille : `w-24 h-24` (96px) en object-cover, avec `q.specimen.description` en caption
- Deux boutons sous l'image : "tenter en vecteur" / "aplatir en image"
- Au clic : injecter dans le manifest `${q.text} : tenter vecteurs` ou `${q.text} : garder png`
- Style toggle : bouton sélectionné → bg-[#8cc63f] text-white, autres → reset

```html
<!-- Rendu cible par carte image_choice -->
<div class="flex flex-col gap-2 p-2 rounded-[12px] bg-[#f7f6f2] border border-[#e5e5e5]">
  <span class="text-[13px] text-slate-500 italic">[q.text]</span>
  <img src="[q.specimen.specimen_url]" class="w-24 h-24 rounded-[8px] object-cover border border-[#e5e5e5] self-start">
  <div class="flex gap-2">
    <button data-val="vector">tenter en vecteur</button>
    <button data-val="png">aplatir en image</button>
  </div>
</div>
```

**Injection manifest au clic :**
```js
const line = val === 'png'
  ? `${q.text} : garder png`
  : `${q.text} : tenter vecteurs`;
// Injecter en tête du manifest (même logique que l'existant)
```

**Règles :**
- Ne pas toucher `image_trigger` (bouton "analyser les illustrations") — inchangé
- Pas de majuscule dans les labels boutons
- Le bootstrap Gemini s'applique (section BOOTSTRAP GEMINI en tête de ROADMAP)
- Redémarrer le serveur après modification de `sullivan_router.py`

**Test de vérification :**
1. Projet avec `design_tokens.image_assets` non vide (ex: dnmade1-2026-blart-samuel après extraction)
2. Ouvrir Sullivan ME → cliquer "affiner le manifeste"
3. Voir autant de cartes que d'illustrations détectées, chacune avec son image et ses deux boutons
4. Cliquer "tenter en vecteur" sur la première → le manifeste contient la ligne correspondante

---

### M366 — Wire overlay : bouton "Cadrage LLM" → "retour manifeste"
**STATUS: ✅ TERMINÉE | ACTOR: GEMINI**

### CR — Mission M366 (Redirection Wire → Manifeste)
- **Fluidité UX** : Lorsqu'un étudiant a besoin d'enrichir le diagnostic liminaire, le bouton du Header Wire ne force plus l'ouverture d'un nouvel onglet `/cadrage`.
- **Remplacement `WsWire.js`** : Remplacement de l'appel `window.wsWire._openCadrage()` par l'exécution combinée de `window.wsWire.hide()` et `window.ManifestBox?.show()`.
- **Intitulé** : Changement du texte "Cadrage LLM" en "retour manifeste", en respectant le token de style typographique HoméOS.

---

### M365 — Wiring : rebrancher X-User-Token dans WsWire.js
**STATUS: ✅ TERMINÉE | ACTOR: GEMINI**

### CR — Mission M365 (Wiring Token Reconnect)
- **Session Isolation** : Ajout de la méthode `_getSession()` supportant l'impersonation mode.
- **Injection Header** : Injection systématique de `X-User-Token` dans tous les fetch vers `/api/projects/*`.
- **Impact** : Le pré-câblage (Pre-Wire) et l'application de la forge (`wire-apply`) ciblent désormais le projet actif de l'étudiant, même si celui-ci n'est pas sur la session par défaut.
- **Résultat** : Sullivan analyse maintenant les bons écrans en mode Wire, évitant le retour à `"homéos-default"`.

---

### M364 — Sullivan Manifest Editor : questionnaire images + flag forge
**STATUS: ✅ CODE LIVRÉ — ⚠️ NON VALIDÉ EN PROD | ACTOR: GEMINI**

### CR — Mission M364 (Questionnaire Images)
- **Backend Injection** : Dans `sullivan_router.py`, injection d'un type de question `image_choice` si des assets sont présents. Utilisation de Groq pour générer une question naturelle basée sur les descriptions.
- **Frontend Rendu** : Mise à jour de `renderCritique()` dans `ManifestSullivan.js` : carousel de spécimens + boutons "Aplatir en image" / "Tenter en vecteur".
- **Interaction Manifeste** : Le choix est injecté en haut du manifeste (`images : garder en png` ou `images : tenter vecteurs`).
- **Validé via curl** : Le endpoint `/api/sullivan/manifest-critique` retourne bien `image_choice` avec specimens quand `design_tokens.image_assets` est fourni. Le rendu frontend `renderCritique()` gère le type `image_choice` correctement.
- **Non validé** : le chemin complet upload → extraction → manifest → Sullivan en conditions réelles étudiant.

---

## Thème 37 — NLP / HCI (Réservé FJD)

> **Ces travaux sont exclusivement menés par FJD. Ne pas déléguer.**

### Vision architecture BERT + Bayesian + MinB/MaxB

**Pipeline cible :**
```
Contexte large (RAG passages) + message user (500 tokens)
  → BERT all-MiniLM-L6-v2 (cosine sim → intent vector 384d)
  → Bayesian update : prior = sliding window 3 derniers intents
  → Routing MinB / MaxB
```

**État actuel dans `maiathon/Spinoza_Secours_HF/Backend/app_runpod.py` :**
- ✅ BERT `all-MiniLM-L6-v2` chargé
- ✅ 4 intent anchors (accord / confusion / resistance / neutre)
- ✅ Cosine similarity → intent label
- ❌ Score de confiance non retourné
- ❌ Aucun routing MinB/MaxB

---

## Thème 35 — Dashboard Prof : Suivi & Analytics

### M368 — Project panel : thumbnails écrans + canvas PNG visible
**STATUS: 🟠 À TRAITER | ACTOR: GEMINI**

**Contexte :**
Quand un étudiant charge ses écrans PNG dans le workspace, le project panel affiche uniquement les noms de fichiers (texte), et le canvas affiche un bloc blanc vide lorsqu'on clique sur un écran. L'objectif est d'afficher les PNG directement — un aperçu 48px dans le panel, et l'image pleine taille sur le canvas.

**Diagnostic technique (Claude, 2026-04-28) :**

Endpoint actuel des imports : `GET /api/retro-genome/imports?project_id=xxx`
Chaque objet import retourné : `{ id, name, timestamp, file_path, date, type, archetype_id, html_template, elements_count }`
**Pas de champ `url`** — il manque un endpoint pour servir les fichiers PNG bruts.

Fichiers PNG stockés dans : `AETHERFLOW/projects/{project_id}/imports/{date}/{filename}`
`file_path` dans l'objet = `"2026-04-28/IMPORT_interface1.png_125831.png"` (chemin relatif au dossier imports)

**Changement 0 — `import_router.py` : nouveau endpoint de serving**

Ajouter après le endpoint `asset_serve` existant :

```python
@router.get("/api/projects/{project_id}/imports/{date}/{filename}")
def serve_import_file(project_id: str, date: str, filename: str):
    from fastapi.responses import FileResponse
    file_path = PROJECTS_DIR / project_id / "imports" / date / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Import non trouvé")
    return FileResponse(str(file_path))
```

Aucun header X-User-Token requis — les `<img>` browser ne transmettent pas de headers custom. L'endpoint est read-only, pas de données sensibles.

URL cible générée côté JS : `/api/projects/${projectId}/imports/${item.file_path.replace('/', '/')}`
(où `item.file_path` = `"2026-04-28/IMPORT_interface1.png_125831.png"`)

**Changement 1 — `WsProjectPanel.js` : thumbnail 48px avant le nom**

Dans la fonction qui construit les items (lignes ~342-357), remplacer :
```js
sEl.innerHTML = `
    <span class="text-[12px] font-medium text-slate-500 ...truncate">${screen.name}</span>
    ...
`;
```
par :
```js
const thumbUrl = screen.file_path
    ? `/api/projects/${projectId}/imports/${screen.file_path}`
    : null;
sEl.innerHTML = `
    <div class="flex items-center gap-2 min-w-0">
        ${thumbUrl ? `<img src="${thumbUrl}" class="w-[48px] h-[36px] rounded-[4px] object-cover shrink-0 border border-[#f0eee4]" loading="lazy">` : '<div class="w-[48px] h-[36px] rounded-[4px] bg-slate-100 shrink-0"></div>'}
        <span class="text-[12px] font-medium text-slate-500 group-hover:text-slate-700 truncate">${screen.name}</span>
    </div>
    <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
        ...boutons existants...
    </div>
`;
```

`projectId` est disponible dans le scope de la fonction (paramètre de `renderScreens` ou de la closure).

**Changement 2 — `WsScreenShell.js` : afficher le PNG sur le canvas**

Dans `WsScreenShell.build()`, après la condition `if (item.dist_url)` et `else if (item.html_template)`, ajouter :
```js
} else if (item.type === 'png' && item.file_path) {
    const imgUrl = `/api/projects/${item.project_id || projectId}/imports/${item.file_path}`;
    iframe.srcdoc = `<html><body style="margin:0;padding:0;overflow:hidden;background:#fff;"><img src="${imgUrl}" style="width:100%;height:100%;object-fit:contain;display:block;"></body></html>`;
}
```

**Problème** : l'item retourné par `addScreen(screen)` ne contient pas `project_id`. Il faut le passer depuis `WsProjectPanel.js` lors du clic :
```js
// WsProjectPanel.js ligne ~354 (onclick)
if (window.wsCanvas) window.wsCanvas.addScreen({ ...screen, project_id: projectId });
```

`projectId` est l'ID du projet courant dans le scope du click handler.

**Redémarrage serveur obligatoire** après modification de `import_router.py`.

**Test de vérification :**
1. Ouvrir le workspace d'un étudiant avec des écrans PNG uploadés
2. Project panel → chaque écran affiche un thumbnail 48×36px + le nom
3. Cliquer sur un écran → canvas affiche le PNG à pleine taille (pas un bloc blanc)
4. Vérifier que l'endpoint `/api/projects/dnamde3-hiver-lyse/imports/2026-04-28/IMPORT_interface1.png_125831.png` retourne HTTP 200

**Règles :**
- Bootstrap Gemini obligatoire (voir en tête de ROADMAP)
- Pas de majuscules dans les labels UI
- Redémarrer le serveur après `import_router.py`
- Ne pas toucher aux autres fonctions du canvas ou du project panel

---

### M369 — Gate pré-forge : décision image par asset avant forge
**STATUS: 🟠 À TRAITER | ACTOR: GEMINI**

**Contexte :**
Quand un étudiant clique "forger le rendu", si le projet contient des `image_assets` dans `design_tokens`, la forge doit d'abord savoir quoi faire de chaque illustration (la vectoriser ou la conserver en PNG aplati). Cette décision se prend une seule fois, avant la forge. Elle est écrite dans le manifest — que la forge lit déjà — donc aucun changement au pipeline forge n'est requis.

**Principe de non-régression (CRITIQUE) :**
- Ne pas modifier `WsForge.js` (ni ses méthodes, ni ses routes)
- Ne pas modifier le backend forge (`/api/retro-genome/generate-from-import`)
- Ne pas modifier `WsForge.forgeScreen()` — l'appeler inchangé après la gate
- Toucher uniquement : `WsScreenShell._addForgeOverlay()` (un seul bloc click handler) + ajouter une méthode statique dans `WsScreenShell`

**Point d'entrée (fichier : `WsScreenShell.js`, lignes 247-249) :**

```js
// AVANT
forgeBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    window.wsForge?.forgeScreen(item.id, g, forgeOverlay);
});

// APRÈS
forgeBtn.addEventListener('click', async (e) => {
    e.stopPropagation();
    await WsScreenShell._forgeWithImageGate(item, g, forgeOverlay);
});
```

**Nouvelle méthode statique `WsScreenShell._forgeWithImageGate(item, shell, overlay)` :**

```js
static async _forgeWithImageGate(item, shell, overlay) {
    // 1. Résoudre token (impersonation-safe)
    const sess = JSON.parse(sessionStorage.getItem('homeos_impersonation') || '{}').token
        ? JSON.parse(sessionStorage.getItem('homeos_impersonation') || '{}')
        : JSON.parse(localStorage.getItem('homeos_session') || '{}');
    const token = sess.token || '';

    // 2. Lire le manifest frais du projet actif
    let imageAssets = [];
    try {
        const ar = await fetch('/api/projects/active', { headers: { 'X-User-Token': token } });
        const ap = await ar.json();
        if (ap.id) {
            const mr = await fetch(`/api/projects/${ap.id}/manifest`, { headers: { 'X-User-Token': token } });
            const manifest = await mr.json();
            imageAssets = manifest?.design_tokens?.image_assets || [];
        }
    } catch(_) {}

    // 3. Si pas d'assets → forge directe, pas de gate
    if (!imageAssets.length) {
        window.wsForge?.forgeScreen(item.id, shell, overlay);
        return;
    }

    // 4. Afficher la gate modal
    const decisions = {};
    const modal = document.createElement('div');
    modal.id = 'forge-image-gate';
    modal.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:9999;display:flex;align-items:center;justify-content:center;';

    const box = document.createElement('div');
    box.style.cssText = 'background:#fff;border-radius:16px;padding:24px;max-width:480px;width:90%;box-shadow:0 8px 40px rgba(0,0,0,0.18);display:flex;flex-direction:column;gap:16px;max-height:80vh;overflow-y:auto;';

    const title = document.createElement('div');
    title.style.cssText = 'font-size:14px;font-weight:700;color:#3d3d3c;';
    title.textContent = `${imageAssets.length} illustration${imageAssets.length > 1 ? 's' : ''} détectée${imageAssets.length > 1 ? 's' : ''} — que fait-on ?`;
    box.appendChild(title);

    imageAssets.forEach((asset, i) => {
        const row = document.createElement('div');
        row.style.cssText = 'display:flex;gap:12px;align-items:flex-start;padding:10px;border-radius:10px;background:#f7f6f2;border:1px solid #e5e5e5;';

        const img = document.createElement('img');
        img.src = asset.specimen_url || '';
        img.style.cssText = 'width:64px;height:64px;object-fit:cover;border-radius:6px;border:1px solid #e5e5e5;flex-shrink:0;';
        row.appendChild(img);

        const right = document.createElement('div');
        right.style.cssText = 'display:flex;flex-direction:column;gap:6px;flex:1;';

        const desc = document.createElement('div');
        desc.style.cssText = 'font-size:12px;color:#64748b;font-style:italic;';
        desc.textContent = (asset.description || `illustration ${i + 1}`).toLowerCase();
        right.appendChild(desc);

        const btns = document.createElement('div');
        btns.style.cssText = 'display:flex;gap:6px;';

        ['tenter en vecteur', 'aplatir en image'].forEach(label => {
            const val = label.includes('vecteur') ? 'vector' : 'png';
            const b = document.createElement('button');
            b.style.cssText = 'padding:4px 10px;border-radius:8px;font-size:12px;border:1px solid #e5e5e5;background:#fff;cursor:pointer;transition:all 0.15s;';
            b.textContent = label;
            b.dataset.val = val;
            b.dataset.idx = String(i);
            b.onclick = () => {
                decisions[i] = val;
                btns.querySelectorAll('button').forEach(x => {
                    x.style.background = '#fff';
                    x.style.color = '#3d3d3c';
                    x.style.borderColor = '#e5e5e5';
                    x.style.fontWeight = 'normal';
                });
                b.style.background = '#8cc63f';
                b.style.color = '#fff';
                b.style.borderColor = '#8cc63f';
                b.style.fontWeight = '700';
            };
            btns.appendChild(b);
        });
        right.appendChild(btns);
        row.appendChild(right);
        box.appendChild(row);
    });

    const footer = document.createElement('div');
    footer.style.cssText = 'display:flex;gap:8px;justify-content:flex-end;margin-top:4px;';

    const skipBtn = document.createElement('button');
    skipBtn.style.cssText = 'padding:8px 16px;border-radius:10px;font-size:13px;border:1px solid #e5e5e5;background:#fff;cursor:pointer;';
    skipBtn.textContent = 'ignorer et forger';
    skipBtn.onclick = () => { modal.remove(); window.wsForge?.forgeScreen(item.id, shell, overlay); };

    const goBtn = document.createElement('button');
    goBtn.style.cssText = 'padding:8px 20px;border-radius:10px;font-size:13px;font-weight:700;border:none;background:#3d3d3c;color:#fff;cursor:pointer;';
    goBtn.textContent = 'forger avec ces choix';
    goBtn.onclick = async () => {
        modal.remove();
        // Écrire les décisions dans le manifest (format lisible par la forge)
        try {
            const ar2 = await fetch('/api/projects/active', { headers: { 'X-User-Token': token } });
            const ap2 = await ar2.json();
            if (ap2.id) {
                const mr2 = await fetch(`/api/projects/${ap2.id}/manifest`, { headers: { 'X-User-Token': token } });
                const manifest2 = await mr2.json();
                let text = manifest2.raw_content || manifest2.description || '';
                imageAssets.forEach((asset, i) => {
                    const val = decisions[i];
                    if (!val) return;
                    const line = val === 'png'
                        ? `${(asset.description || `illustration ${i+1}`).toLowerCase()} : garder png`
                        : `${(asset.description || `illustration ${i+1}`).toLowerCase()} : tenter vecteurs`;
                    if (!text.includes(line)) text = line + '\n' + text;
                });
                manifest2.raw_content = text;
                await fetch(`/api/projects/${ap2.id}/manifest`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json', 'X-User-Token': token },
                    body: JSON.stringify(manifest2)
                });
            }
        } catch(_) {}
        window.wsForge?.forgeScreen(item.id, shell, overlay);
    };

    footer.appendChild(skipBtn);
    footer.appendChild(goBtn);
    box.appendChild(footer);
    modal.appendChild(box);
    document.body.appendChild(modal);
}
```

**Règles :**
- Bootstrap Gemini obligatoire (voir en tête de ROADMAP)
- Pas de majuscules dans les labels (sauf le titre de la gate : première lettre ok)
- Vert HoméOS (`#8cc63f`) uniquement sur le bouton sélectionné (toggle)
- `border-radius` max `16px` (box) / `10px` (boutons)
- Pas de redémarrage serveur nécessaire (JS statique uniquement)
- Bumper le `?v=` de `WsScreenShell.js` dans `workspace.html`

**Test de vérification :**
1. Projet avec `design_tokens.image_assets` non vide
2. Cliquer "forger le rendu" sur un écran → la gate s'affiche avec les thumbnails
3. Choisir "tenter en vecteur" sur une illustration → bouton vert
4. Cliquer "forger avec ces choix" → gate disparaît, forge démarre normalement
5. Vérifier dans le manifest que la ligne `portrait nancy : tenter vecteurs` a été injectée
6. Projet sans `image_assets` → clic "forger" → forge directe sans gate

---

> Ce thème concerne la visibilité en temps réel de l'avancement des étudiants et la gestion granulaire des sujets.

### M370 — V4 Clean : suppression du code mort, branche propre pour handoff
**STATUS: ✅ TERMINÉE | ACTOR: GEMINI**

### CR — Mission M370 (V4 Clean)
- **Root Cleanup** : Suppression de ~20 scripts legacy et fichiers de test à la racine.
- **Routers Cleanup** : Suppression des 6 routers inactifs. Inlining des constantes RBAC (PLAN_LIMITS) dans `auth_router.py` pour maintenir la stabilité.
- **Docs Cleanup** : Suppression des dossiers `docs/` legacy (archives).
- **Templates Cleanup** : Conservation stricte des 10 templates HTML listés. `brainstorm_war_room.html` renommé en `brainstorm_war_room_tw.html` pour cohérence code.
- **Architecture Cleanup** : Suppression du dossier `homeos/` (V3).
- **Validation** : Serveur redémarré, `/api/health` OK, `/api/auth/me` (RBAC) testé OK.

**Contexte**  
Le repo AETHERFLOW contient environ 1500 fichiers pour ~80 actifs. L'objectif est une branche `v4-clean` git-propre, sans toucher aux imports Python ni à la structure des dossiers actifs. Phase 1 uniquement : supprimer, pas restructurer.

**Ce que Gemini doit faire**

**Étape 0 — Créer la branche**
```bash
cd /Users/francois-jeandazin/AETHERFLOW
git checkout main
git checkout -b v4-clean
```

**Étape 1 — Supprimer les fichiers morts à la racine** (`git rm` uniquement les fichiers trackés)
```bash
git rm -f groq-r1.py ds-r1.py serve_frontend.py super_diag.py test_extract.py 2>/dev/null || true
git rm -f active_project.json manifest.json design.md build_trace_poc.py 2>/dev/null || true
git rm -f "=1.0.9" "=4.43.0" 2>/dev/null || true
git rm -rf outputs/ 2>/dev/null || true
# Scripts test Qwen/Kimi :
git rm -f test_key.py test_kimi_nim.py test_kimi_openrouter.py 2>/dev/null || true
git rm -f test_qwen3_free.py test_qwen3_next_free.py test_qwen_api.py test_qwen_api_v2.py 2>/dev/null || true
git rm -f test_qwen_free.py test_qwen_openrouter.py test_qwen_silicon.py 2>/dev/null || true
git rm -f qwen_cli.py setup_local_qwen.py aether-glm.py aether-r1.py 2>/dev/null || true
```

**Étape 2 — Supprimer les routers morts** (non montés dans server_v3.py)
```bash
git rm -f "Frontend/3. STENCILER/routers/api_key_urls.py" 2>/dev/null || true
git rm -f "Frontend/3. STENCILER/routers/auth_supabase.py" 2>/dev/null || true
git rm -f "Frontend/3. STENCILER/routers/manifest_analyzer.py" 2>/dev/null || true
git rm -f "Frontend/3. STENCILER/routers/model_health.py" 2>/dev/null || true
git rm -f "Frontend/3. STENCILER/routers/rbac_middleware.py" 2>/dev/null || true
git rm -f "Frontend/3. STENCILER/routers/supabase_client.py" 2>/dev/null || true
git rm -f "Frontend/3. STENCILER/routers/supabase_client.py" 2>/dev/null || true
```

**Étape 3 — Supprimer les anciens docs trackés** (dossiers docs/ racine déjà archivés)
```bash
git rm -rf docs/02_Sullivan/ docs/03_AetherFlow/ docs/04_Archives/ 2>/dev/null || true
git rm -rf docs/04_HomeOS/ docs/05_Operations/ docs/06_Design_Assets/ 2>/dev/null || true
git rm -rf docs/07_Guides/ docs/08_Research/ docs/09_Frontend/ 2>/dev/null || true
git rm -rf docs/00_Core/technique/ 2>/dev/null || true
```

**Étape 4 — Supprimer les templates HTML legacy** (non routés)
Les templates actifs (à conserver) sont exactement :
`login.html`, `workspace.html`, `student_login.html`, `teacher_dashboard.html`,
`bkd_frd.html`, `cadrage_alt.html`, `cadrage_prof.html`, `frd_editor.html`,
`brainstorm_war_room_tw.html`, `intent_viewer.html`

Supprimer tout le reste dans `Frontend/3. STENCILER/static/templates/` :
```bash
cd "Frontend/3. STENCILER/static/templates/"
# Lister tous les html, exclure les 10 actifs, git rm le reste
git ls-files "*.html" | grep -vE "^(login|workspace|student_login|teacher_dashboard|bkd_frd|cadrage_alt|cadrage_prof|frd_editor|brainstorm_war_room_tw|intent_viewer)\.html$" | xargs git rm -f
cd /Users/francois-jeandazin/AETHERFLOW
```

**Étape 5 — Supprimer le dossier homeos/ (architecture morte)**
```bash
git rm -rf homeos/ 2>/dev/null || true
```

**Étape 6 — Vérification serveur** (obligatoire avant commit)
```bash
cd /Users/francois-jeandazin/AETHERFLOW
python3 -c "import ast, sys
import subprocess
result = subprocess.run(['python3', '-m', 'py_compile', 'Frontend/3. STENCILER/server_v3.py'], capture_output=True)
print('server_v3 syntax:', 'OK' if result.returncode == 0 else result.stderr.decode())
"
curl -s http://localhost:9998/api/health | python3 -c "import sys,json; print('health:', json.load(sys.stdin).get('status'))"
```

**Étape 7 — Commit et push**
```bash
git add -A
git commit -m "chore(v4-clean): suppression code mort — routers inactifs, docs archivés, templates legacy, homeos/"
git push -u origin v4-clean
```

**Règles**
- Ne toucher à aucun fichier `.py` actif (pas de refactor d'imports)
- Ne toucher à aucun fichier dans `Frontend/3. STENCILER/routers/` sauf les 6 routers morts listés
- Ne pas supprimer `Backend/` (trop de dépendances imbriquées à auditer séparément)
- Si un `git rm` échoue (fichier non tracké) → `|| true`, continuer
- Le serveur doit répondre `{"status":"ok"}` sur `/api/health` après le commit

**Test de vérification**
1. `git status` sur `v4-clean` → 0 modified, 0 untracked utiles
2. `curl http://localhost:9998/api/health` → `status: ok`
3. Login teacher FJD → dashboard classes visible
4. Login student Lyse → workspace charge, drill fonctionne
5. `git log --oneline -3` → commit propre visible

---

### M350 — Vue "Live Watch" (Drill Status Polling) 
**STATUS: 🟠 À TRAITER | ACTOR: GEMINI**

### M351 — Notation Automatique par Référentiel
**STATUS: 🟠 À TRAITER | ACTOR: CLAUDE**
