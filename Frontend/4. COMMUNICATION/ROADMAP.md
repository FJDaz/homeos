# MISSION CONTROL : AETHERFLOW ROADMAP

> Missions complètes archivées dans [ROADMAP_ACHIEVED.md](./ROADMAP_ACHIEVED.md).

---

## Thème 0 — Hotfixes

> M121 ✅, M116 ✅, M122 ✅, M123 ✅, M124 ✅, M125 ✅, M126 ✅, M127 ✅ — archivées dans ROADMAP_ACHIEVED.md (2026-04-01)

### Mission 125 — DELETE /api/imports/{id}
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


### Mission 126 — Cascade LLM : gemini-3.1-flash-lite en queue
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


## Thème 7 — Drill : Manifeste → Wire → Cadrage

> Objectif : à partir d'un import (SVG, HTML, image), HoméOS détecte si un manifeste existe, lance le mode Wire directement si oui, sinon ouvre le Cadrage (ex-BRS). Le Wire doit fonctionner en mode aperçu, validable en un clic.

### Mission 148 — Bridge @font-face : fontes système → iframes screens
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


### Mission 144 — Export projet + @font-face dans les screens
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


### Mission 145 — Renommage UI : BRS → Cadrage + tabs renommés
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


### Mission 146 — Détection manifeste → routage Wire ou Cadrage
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


### Mission 147 — Wire : overlay Z-index + fond blur + validation

**STATUS: 🔵 EN COURS**
**DATE: 2026-04-02**

---

#### MISSION GEMINI — Livrable A : overlay `#ws-wire-overlay` dans workspace.html

**ACTOR: GEMINI**
**MODE: CODE DIRECT**
**FILE: `Frontend/3. STENCILER/static/templates/workspace.html`**

**Bootstrap Gemini :**
```
Tu es un agent frontend expert Tailwind CSS. Tu modifies un seul fichier HTML.
Ne touche à aucun autre fichier. N'invente pas de routes API.
Écris le rapport dans ce fichier quand tu as terminé.
```

**input_files:** `LEXICON_DESIGN.json`, `SULLIVAN_INTERACTIONS.md`

**Contexte DOM existant :**
```html
<!-- PREVIEW OVERLAY — z-[35] -->
<div id="ws-preview-overlay" class="hidden absolute inset-0 bg-white z-[35] flex items-center justify-center overflow-auto">
    <div id="ws-preview-frame-container" class="relative">
        <!-- iframe injectée ici par enterPreviewMode() -->
    </div>
</div>
```

**Ce que tu dois ajouter :**

Insérer `#ws-wire-overlay` comme **frère direct** de `#ws-preview-frame-container`, à l'intérieur de `#ws-preview-overlay`. Il doit se positionner en `absolute inset-0 z-[50]` par-dessus l'iframe. Par défaut `hidden`.

Structure attendue :
```html
<div id="ws-wire-overlay" class="hidden absolute inset-0 z-[50] flex flex-col">
  <!-- Fond blur -->
  <div class="absolute inset-0 backdrop-blur-sm bg-white/80"></div>
  <!-- Contenu -->
  <div class="relative z-10 flex flex-col h-full p-8 gap-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h2 class="text-sm font-semibold text-slate-700 uppercase tracking-widest">wire — mapping composants</h2>
      <span id="ws-wire-import-label" class="text-xs text-slate-400"></span>
    </div>
    <!-- Tableau -->
    <div class="flex-1 overflow-auto rounded-lg border border-slate-200 bg-white shadow-sm">
      <table class="w-full text-xs text-slate-600">
        <thead class="bg-slate-50 border-b border-slate-200">
          <tr>
            <th class="px-4 py-3 text-left font-medium">Composant</th>
            <th class="px-4 py-3 text-left font-medium">Rôle</th>
            <th class="px-4 py-3 text-left font-medium">Z-index</th>
            <th class="px-4 py-3 text-left font-medium">Statut</th>
          </tr>
        </thead>
        <tbody id="ws-wire-table-body" class="divide-y divide-slate-100">
          <!-- Rows injectées par wsWire.show(manifest) -->
        </tbody>
      </table>
    </div>
    <!-- Actions -->
    <div class="flex items-center gap-3 justify-end">
      <button id="ws-wire-btn-cadrage" class="px-4 py-2 text-xs font-medium text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors">
        retour cadrage
      </button>
      <button id="ws-wire-btn-validate" class="px-4 py-2 text-xs font-medium text-white bg-slate-800 rounded-lg hover:bg-slate-700 transition-colors">
        valider le wire
      </button>
    </div>
  </div>
</div>
```

Règles :
- Pas de majuscules dans les labels (convention HoméOS)
- Pas d'emojis
- Tailwind uniquement — aucun style inline
- Ne pas modifier `#ws-preview-overlay` ni `#ws-preview-frame-container`

**Critères de sortie :**
- [ ] `#ws-wire-overlay` présent dans le DOM, `hidden` par défaut
- [ ] `#ws-wire-table-body` vide (rempli par JS)
- [ ] `#ws-wire-btn-validate` et `#ws-wire-btn-cadrage` présents avec leurs ids exacts
- [ ] Aucune autre modification du fichier

---

#### Livrable B — Logic JS + Route Python (CLAUDE — CODE DIRECT)

**À faire après Gemini :**

**1. ws_main.js — `enterPreviewMode()` : détecter manifeste et afficher overlay**

Après injection de l'iframe dans `#ws-preview-frame-container`, appeler :
```javascript
// Détection manifeste
const importId = shell.dataset.importId || shellId;
fetch(`/api/frd/manifest?import_id=${encodeURIComponent(importId)}`)
    .then(r => r.json())
    .then(data => { if (data.exists) window.wsWire?.show(data.manifest, importId); });
```

**2. ws_main.js — objet `wsWire`** (à ajouter en bas du fichier, exposer sur `window`) :
```javascript
window.wsWire = {
    _importId: null,
    show(manifest, importId) {
        this._importId = importId;
        const overlay = document.getElementById('ws-wire-overlay');
        const label = document.getElementById('ws-wire-import-label');
        const tbody = document.getElementById('ws-wire-table-body');
        if (!overlay || !tbody) return;
        if (label) label.textContent = importId;
        const components = manifest.components || manifest.screens || [];
        tbody.innerHTML = components.map(c => `
            <tr>
                <td class="px-4 py-3 font-mono">${c.name || c.id || '—'}</td>
                <td class="px-4 py-3">${c.role || '—'}</td>
                <td class="px-4 py-3">${c.z_index ?? '—'}</td>
                <td class="px-4 py-3"><span class="inline-flex items-center px-2 py-0.5 rounded text-xs bg-amber-50 text-amber-700">en attente</span></td>
            </tr>`).join('');
        overlay.classList.remove('hidden');
        document.getElementById('ws-wire-btn-validate')?.addEventListener('click', () => this.validate(), { once: true });
        document.getElementById('ws-wire-btn-cadrage')?.addEventListener('click', () => this.hide(), { once: true });
    },
    hide() {
        document.getElementById('ws-wire-overlay')?.classList.add('hidden');
    },
    async validate() {
        const res = await fetch('/api/frd/validate-wire', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ import_id: this._importId })
        });
        if ((await res.json()).status === 'ok') this.hide();
    }
};
```

**3. server_v3.py — Route `POST /api/frd/validate-wire`**
```python
@app.post("/api/frd/validate-wire")
async def validate_wire(req: Request):
    body = await req.json()
    import_id = body.get("import_id", "")
    active = _get_active_project()
    manifests_dir = Path(f"projects/{active}/manifests")
    manifests_dir.mkdir(parents=True, exist_ok=True)
    path = manifests_dir / f"manifest_{import_id}.json"
    data = {"validated": True, "import_id": import_id}
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return {"status": "ok"}
```

**Critères de sortie globaux :**
- [ ] Ouvrir un screen sans manifeste → overlay absent
- [ ] Ouvrir un screen avec manifeste → overlay visible avec tableau des composants
- [ ] "Valider le Wire"### Mission 156 — Refactor WsCanvas : découpe hexagonale en 5 modules
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---
anHtml` (déjà en place)

**Critères de sortie :**
- [ ] WsCanvas.js < 200L
- [ ] Sullivan apply fonctionne (doc.write, pas de boucle infinie, changements visibles)
- [ ] Sélection screen / drag / zoom non régressés
- [ ] forge polling toujours fonctionnel

---

### Mission 157 — Nettoyage ROADMAP.md : collapse des missions archivées

**STATUS: 🟠 PRÊTE**
**DATE: 2026-04-03**
**ACTOR: CLAUDE (CODE DIRECT — ROADMAP.md)**

**Contexte :**
ROADMAP.md fait 1787 lignes. De nombreuses missions ✅ LIVRÉ y occupent encore des blocs complets (50–150L chacune) alors qu'elles sont déjà archivées dans `ROADMAP_ACHIEVED.md`. Cela noie les missions actives et ralentit la lecture.

**Objectif :**
Réduire toute mission ayant **STATUS: ✅ LIVRÉ** ET une entrée dans `ROADMAP_ACHIEVED.md` à une ligne de référence unique. Conserver intact tout ce qui est `🔵 EN COURS`, `🟠 PRÊTE`, ou `🔵 BACKLOG`.

**Règle de collapse :**
Remplacer le bloc complet de chaque mission archivée par :
```
### Mission NNN — [titre]
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md
```
Suivi d'un `---` séparateur.

**Missions à vérifier et collapser si archivées :**
Parcourir dans l'ordre du fichier. Pour chaque `### Mission NNN` avec `STATUS: ✅ LIVRÉ` :
1. Vérifier qu'une entrée `Mission NNN` existe dans `ROADMAP_ACHIEVED.md`
2. Si oui → remplacer le bloc par la ligne de référence ci-dessus
3. Si non → laisser intact (ne pas archiver à la volée, signaler en fin de rapport)

**Périmètre :**
- Fichier à modifier : `/Users/francois-jeandazin/AETHERFLOW/Frontend/4. COMMUNICATION/ROADMAP.md`
- Fichier à lire (source de vérité archive) : `/Users/francois-jeandazin/AETHERFLOW/Frontend/4. COMMUNICATION/ROADMAP_ACHIEVED.md`
- Ne pas modifier `ROADMAP_ACHIEVED.md`
- Ne pas toucher aux sections Thème, aux titres de thème, ni aux missions non-✅

**Critères de sortie :**
- [ ] ROADMAP.md < 600 lignes
- [ ] Toutes les missions ✅ LIVRÉ archivées sont collapées à 1 ligne + séparateur
- [ ] Missions EN COURS / PRÊTE / BACKLOG inchangées
- [ ] Rapport : liste des missions collapées + éventuelles missions ✅ non archivées signalées

---

### Mission 155 — Bouton Stop Sullivan : annulation de requête en cours

**STATUS: 🟠 PRÊTE**
**DATE: 2026-04-03**
**ACTOR: CLAUDE (CODE DIRECT — WsChat.js)**

**Contexte :**
Quand Sullivan met trop de temps (erreur réseau, timeout LLM, régénération infinie), l'utilisateur n'a aucun moyen d'annuler. La bulle "en cours..." reste bloquée indéfiniment. Il faut un bouton Stop visible pendant le traitement, qui annule le fetch via `AbortController` et nettoie l'UI.

**Livrable — WsChat.js**

1. Ajouter un `AbortController` dans `sendMessage()` :
```javascript
this._abortController = new AbortController();
const res = await fetch('/api/sullivan/chat', {
    ...
    signal: this._abortController.signal
});
```

2. Afficher un bouton Stop dans la bulle transitoire (remplace le texte simple) :
```javascript
_appendTransient(text) {
    const b = this.appendBubble(`${text} <button id="ws-stop-btn" onclick="window.wsChat?.stopSullivan()" style="margin-left:8px;padding:1px 6px;border:1px solid #cbd5e1;border-radius:4px;font-size:9px;cursor:pointer;background:#fff;color:#64748b;">stop</button>`, 'sullivan');
    ...
}
```

3. Méthode `stopSullivan()` :
```javascript
stopSullivan() {
    this._abortController?.abort();
}
```

4. Dans le `catch`, distinguer abort vs vraie erreur :
```javascript
} catch (e) {
    if (pending) pending.remove();
    if (e.name !== 'AbortError') {
        this.appendBubble("Désolé, une erreur technique est survenue.", 'sullivan');
    }
    // AbortError → silence, l'utilisateur a annulé volontairement
}
```

**Critères de sortie :**
- [ ] Pendant le traitement Sullivan : bouton "stop" visible dans la bulle d'attente
- [ ] Clic stop → fetch annulé, bulle retirée, pas de message d'erreur
- [ ] Erreur réseau réelle → message d'erreur affiché normalement
- [ ] Un seul AbortController actif à la fois (nouveau message → ancien annulé silencieusement)

---

### Mission 154 — Sullivan : focus élément sélectionné dans le prompt
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


### Mission 153 — Undo Sullivan : rebrancher la stack d'historique

**STATUS: 🔵 EN COURS — GEMINI**
**DATE: 2026-04-03**
**ACTOR: GEMINI**

**Contexte :**
`WsInspect` a déjà une `historyStack` complète (`snapshot()` + `undo()`), alimentée par `inspect-snapshot` postMessage depuis l'iframe. Mais Sullivan écrit directement via `updateActiveScreenHtml()` sans pousser de snapshot. Résultat : Cmd+Z ne peut pas défaire une action Sullivan.

**Livrable A — WsCanvas.js : snapshot avant updateActiveScreenHtml**

```javascript
updateActiveScreenHtml(html) {
    // Snapshot pour undo avant modification
    if (window.wsInspect) {
        const previewIframe = document.querySelector('#ws-preview-frame-container iframe');
        const canvasIframe = this.activeScreenId
            ? document.getElementById(this.activeScreenId)?.querySelector('iframe')
            : null;
        const currentHtml = previewIframe?.srcdoc
            || previewIframe?.contentDocument?.documentElement?.outerHTML
            || canvasIframe?.srcdoc || '';
        if (currentHtml) window.wsInspect.snapshot(currentHtml);
    }
    // ... reste inchangé
}
```

**Livrable B — workspace.html : bouton Undo dans le header**

À côté du bouton SAVE existant :
```html
<button onclick="window.wsInspect?.undo()" 
    class="px-3 py-1.5 border border-slate-200 rounded-custom text-[10px] font-bold text-slate-500 uppercase tracking-widest hover:text-slate-800 hover:border-slate-400 transition-all"
    title="Défaire la dernière action Sullivan (Ctrl+Z)">
    undo
</button>
```

Et écouter Ctrl+Z globalement dans `ws_main.js` :
```javascript
window.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'z') {
        e.preventDefault();
        window.wsInspect?.undo();
    }
});
```

**Critères de sortie :**
- [ ] Sullivan modifie un screen → Cmd+Z → screen revient à l'état précédent
- [ ] Bouton "undo" visible dans le header workspace
- [ ] Stack max 10 snapshots (déjà configuré dans WsInspect)

---

### Mission 152 — Sullivan context complet : tous les screens canvas + DESIGN.md
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


### Mission 150 — Retour Cadrage : session pré-alimentée par le manifeste Wire

**STATUS: 🟠 PRÊTE**
**DATE: 2026-04-02**
**ACTOR: CLAUDE (CODE DIRECT — server_v3.py + cadrage_war_room_tw.html)**
**DÉPENDANCE: M151 (manifeste généré), M147 (WsWire._openCadrage)**

**Contexte :**
`WsWire._openCadrage()` ouvre `/cadrage?import_id=...&context=...` avec archétype + composants dans l'URL. `cadrage_war_room_tw.html` lit `?context=` et pré-remplit l'input (déjà implémenté). Mais la session Cadrage démarre vide — les LLM (Gemini, Groq, Codestral) ne reçoivent pas ce contexte. Il faut que le premier message envoyé intègre le contexte Wire comme brief initial.

**Pipeline cible :**
```
Wire overlay → "Retour Cadrage"
  → /cadrage?import_id=X&context=Y&archetype=Z
  → cadrage_war_room_tw.html se charge
  → sessionId généré
  → Contexte Wire injecté comme buffer_answers dans dispatch_brainstorm()
  → Premier SSE : les LLM reçoivent le contexte + produisent un brief
```

**Livrable A — Route POST /api/cadrage/init-context (server_v3.py)**

Nouvelle route pour initialiser une session avec contexte Wire :
```python
@app.post("/api/cadrage/init-context")
async def cadrage_init_context(body: Dict[str, Any]):
    session_id = body.get("session_id")
    import_id = body.get("import_id", "")
    context = body.get("context", "")
    archetype = body.get("archetype", "")
    components = body.get("components", [])

    # Récupérer le manifeste complet si dispo
    manifest_data = {}
    try:
        manifest_dir = get_active_project_path() / "manifests"
        path = manifest_dir / f"manifest_{import_id}.json"
        if path.exists():
            manifest_data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass

    # Construire le buffer_answers pour brainstorm_logic
    buffer_answers = {}
    if archetype:
        buffer_answers["archetype_détecté"] = archetype
    if components:
        buffer_answers["composants_mappés"] = ", ".join(
            f"{c.get('name','?')} ({c.get('role','?')})" for c in components[:15]
        )
    if import_id:
        buffer_answers["import_id"] = import_id
    if context:
        buffer_answers["contexte_wire"] = context

    # Prompt d'ouverture
    prompt = f"""Un screen a été analysé via le mode Wire d'HoméOS.
Archétype détecté : {archetype or 'non spécifié'}.
L'utilisateur souhaite affiner l'intention derrière ce screen et définir ce qu'il doit faire.
Aide-le à cadrer le projet à partir de ce contexte."""

    await cadrage_logic.dispatch_brainstorm(session_id, prompt, buffer_answers)
    return {"status": "ok", "session_id": session_id}
```

**Livrable B — cadrage_war_room_tw.html : appel init-context au démarrage**

Après la génération du `sessionId`, si `?import_id` est présent dans l'URL, appeler `/api/cadrage/init-context` avant le premier message utilisateur :

```javascript
// Après : const sessionId = "CAD-" + ...
if (_wireImportId) {
    const _components = []; // reconstruit depuis ?context= si possible
    fetch('/api/cadrage/init-context', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: sessionId,
            import_id: _wireImportId,
            context: _wireContext || '',
            archetype: _params.get('archetype') || '',
            components: []
        })
    }).then(() => {
        // Afficher un badge de confirmation
        const badge = document.getElementById('ws-wire-context-badge');
        if (badge) badge.classList.remove('hidden');
    });
}
```

Ajouter dans le HTML, visible quand contexte Wire détecté :
```html
<div id="ws-wire-context-badge" class="hidden text-[10px] font-semibold text-homeos-green border border-homeos-green/30 bg-homeos-green/5 px-3 py-1.5 rounded-lg">
    contexte wire chargé — session pré-alimentée
</div>
```

**Livrable C — WsWire._openCadrage() : passer archetype dans l'URL**

Dans `WsWire.js`, enrichir les params :
```javascript
const archetype = this._manifest?.archetype?.label || '';
params.set('archetype', archetype);
```

**Critères de sortie :**
- [ ] Retour Cadrage → badge "contexte wire chargé" visible dans la War Room
- [ ] Premier message envoyé → les LLM reçoivent archétype + composants dans leur prompt
- [ ] Session sans Wire (`/cadrage` direct) → comportement inchangé
- [ ] `dispatch_brainstorm` appelé une seule fois par session

---

### Mission 151 — Auto-génération manifeste à l'import HTML
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


### Mission 149 — Canvas N0 : États de sélection + toolbar opérationnelle

**STATUS: 🟠 PRÊTE**
**DATE: 2026-04-02**
**ACTOR: CLAUDE (CODE DIRECT — WsCanvas.js + workspace.css)**
**DÉPENDANCE: aucune**

**Contexte :**
La toolbar flottante est visible sur le canvas (N0) mais les outils ne produisent aucun feedback visuel distinct. Il n'y a pas de distinction entre :
- `focus-select` — screen sélectionné pour édition (clic dans header)
- `focus-drag` — screen en cours de déplacement (mousedown + move)
- `hover` — survol d'un screen

De plus, `selectScreen()` utilise `.pulsing` (animation verte) comme seul signal visuel — trop subtil, pas scalable. Le canvas a besoin d'un vrai système d'états CSS cohérent pour que la toolbar puisse réagir (ex: afficher les bons outils selon le contexte).

**État actuel du code :**
- `WsCanvas.js:selectScreen()` — ajoute `.active` + `.pulsing` sur le `<rect>` bg, stroke `#A3CD54`
- `WsCanvas.js:deselectAll()` — retire `.active` + `.pulsing`, reset stroke `#f0f0f0`
- `WsCanvas.js:handleMouseDown()` — drag conditionné à `activeMode === 'select'` + `worldY <= 40` (header)
- `workspace.css` — `.ws-screen-shell.active` = seul drop-shadow, `.pulsing` = animation stroke

**Ce qu'il faut implémenter :**

#### Livrable A — Système d'états CSS (workspace.css)

Trois états distincts sur `.ws-screen-shell` :

```css
/* HOVER — survol */
.ws-screen-shell.ws-hover .ws-screen-bg {
    stroke: #d0d0d0;
    stroke-width: 2px;
}

/* SELECTED — sélectionné (clic simple, mode select) */
.ws-screen-shell.ws-selected .ws-screen-bg {
    stroke: #A3CD54;
    stroke-width: 2.5px;
    filter: drop-shadow(0 0 0 3px rgba(163,205,84,0.25));
}
/* Handle de déplacement visible uniquement sur ws-selected */
.ws-screen-shell.ws-selected .ws-screen-header {
    fill: rgba(163,205,84,0.06);
}

/* DRAGGING — en cours de déplacement */
.ws-screen-shell.ws-dragging .ws-screen-bg {
    stroke: #94a3b8;
    stroke-width: 2px;
    opacity: 0.85;
}
.ws-screen-shell.ws-dragging {
    filter: drop-shadow(0 20px 60px rgba(0,0,0,0.25));
}
```

Supprimer `.pulsing` et l'animation `pulse-focus` (remplacés).

#### Livrable B — WsCanvas.js : gestion des états

**Hover** — ajouter mouseenter/mouseleave sur chaque shell `g` à la création :
```javascript
g.addEventListener('mouseenter', () => {
    if (!g.classList.contains('ws-selected')) g.classList.add('ws-hover');
});
g.addEventListener('mouseleave', () => g.classList.remove('ws-hover'));
```

**selectScreen()** — remplacer `.active` + `.pulsing` par `.ws-selected` :
```javascript
selectScreen(shell) {
    this.deselectAll();
    shell.classList.remove('ws-hover');
    shell.classList.add('ws-selected');
    this.content.appendChild(shell); // bring to front
    this.activeScreenId = shell.getAttribute('id');
    this._updateAuditPanel(shell);
    this._notifyToolbar('select', shell);
}
```

**deselectAll()** — nettoyer les trois états :
```javascript
deselectAll() {
    document.querySelectorAll('.ws-screen-shell').forEach(s => {
        s.classList.remove('ws-selected', 'ws-hover', 'ws-dragging');
    });
    this.activeScreenId = null;
    this._notifyToolbar(null, null);
}
```

**Drag** — ajouter/retirer `.ws-dragging` :
```javascript
// Dans handleMouseDown — début drag :
shell.classList.add('ws-dragging');

// Dans handleMouseUp — fin drag :
if (this.selectedScreen) {
    this.selectedScreen.classList.remove('ws-dragging');
    this.selectedScreen = null;
}
```

**`_notifyToolbar(state, shell)`** — dispatcher les états vers la toolbar :
```javascript
_notifyToolbar(state, shell) {
    // Met à jour le cursor du SVG
    const cursorMap = { select: 'default', drag: 'grab', frame: 'crosshair', 'place-img': 'copy' };
    this.svg.style.cursor = cursorMap[this.activeMode] || 'default';
    // Émet un event custom pour que la toolbar puisse réagir
    document.dispatchEvent(new CustomEvent('ws-canvas-state', {
        detail: { state, screenId: shell?.getAttribute('id') || null, mode: this.activeMode }
    }));
}
```

**setMode()** — mettre à jour le cursor SVG immédiatement + badge actif toolbar :
```javascript
setMode(mode) {
    this.activeMode = mode;
    const cursorMap = { select: 'default', drag: 'grab', frame: 'crosshair', 'place-img': 'copy' };
    this.svg.style.cursor = cursorMap[mode] || 'default';
    document.querySelectorAll('.ws-tool-btn').forEach(btn => {
        btn.classList.toggle('active-tool', btn.dataset.mode === mode);
    });
    this._notifyToolbar(null, null);
}
```

#### Livrable C — Toolbar : réaction à `ws-canvas-state`

Dans `ws_main.js`, écouter l'event et afficher un label de contexte dans la toolbar :
```javascript
document.addEventListener('ws-canvas-state', (e) => {
    const { state, screenId, mode } = e.detail;
    const label = document.getElementById('ws-toolbar-context-label');
    if (!label) return;
    label.textContent = screenId
        ? `${mode} — ${screenId.replace('shell-', '').slice(0, 20)}`
        : mode || '';
});
```

Ajouter dans `workspace.html`, sous la toolbar card existante :
```html
<span id="ws-toolbar-context-label" style="font-size:8px; color:#94a3b8; text-align:center; max-width:40px; word-break:break-all; line-height:1.2; padding: 0 4px;"></span>
```

**Critères de sortie :**
- [ ] Hover sur screen → stroke gris doux, pas de sélection
- [ ] Clic sur screen → `.ws-selected` visible (stroke vert, header teinté)
- [ ] Drag → `.ws-dragging` visible (shadow forte, opacité réduite), retiré au mouseup
- [ ] `.pulsing` et `pulse-focus` supprimés
- [ ] Label contexte dans la toolbar : `select — nom-screen`
- [ ] `ws-canvas-state` dispatchable et écouté
- [ ] Sélection persistante : cliquer dans le canvas vide → deselect, clic sur screen → select

---

## Thème 6 — Refonte FRD : Canvas Workspace Unifié

### Mission 128 — Bridge DESIGN.md → tokens projet dynamiques

**STATUS: 🔵 BACKLOG**
**DATE: 2026-04-01**
**ACTOR: CLAUDE (CODE DIRECT — server_v3.py + svg_to_tailwind.py) + GEMINI (landing.html)**
**DÉPENDANCE: aucune (indépendant de M127)**

**Contexte :** HoméOS a son propre format `DESIGN.md` (défini dans `docs/06_Design_Assets/assets/sullivan_editor_base_accurate/DESIGN.md`). Ce fichier documente le design system d'un projet (palette, typo, formes). En l'uploadant dans HoméOS, tous les appels LLM suivants (génération SVG→HTML, vision PNG) utilisent les tokens du projet au lieu des tokens HoméOS par défaut. Ce bridge positionne HoméOS en **continuité de Stitch** : même design system, même vocabulaire.

#### Format DESIGN.md HoméOS (référence : sullivan_editor_base_accurate/DESIGN.md)

Sections parsées :

```markdown
### Palette de Couleurs
- **Primary (...)** : `#A3CD54`   → colors.primary
- **Backgrounds** : blanc pur     → colors.neutral (fallback #ffffff)
- **Texts** : gris anthracite     → colors.text (fallback #1a1a1a)

### Typographie
- **Police de caractères** : `Source Sans 3`  → typography.body
- **Display/Headlines** : Semi-bold           → typography.headline_weight

### Formes & Structure (Shape)
- **Border Radius** : `20px`       → shape.border_radius
```

Parser : regex `\*\*[^*]+\*\*\s*:\s*` + extraction hex `#[0-9a-fA-F]{3,6}` + backtick values.

#### Livrable A — Routes backend (server_v3.py) — Claude

```
POST /api/project/import-design-md
Body: multipart (file)

→ Parse le DESIGN.md selon le format HoméOS
→ Produit exports/design_tokens.json :
  {
    "colors": { "primary": "#A3CD54", "neutral": "#ffffff", "text": "#1a1a1a" },
    "typography": { "body": "Source Sans 3", "headline_weight": "600" },
    "shape": { "border_radius": "20px" },
    "source": "homeos_design_md",
    "imported_at": "2026-04-01T..."
  }
→ Retourne { "status": "ok", "tokens": {...} }

GET /api/project/design-tokens
→ Retourne design_tokens.json si présent
→ Sinon retourne defaults HoméOS :
  { "colors": { "primary": "#8cc63f", "neutral": "#f7f6f2", "text": "#3d3d3c" },
    "typography": { "body": "Geist" }, "shape": { "border_radius": "6px" } }
```

#### Livrable B — Injection tokens dans les prompts LLM (svg_to_tailwind.py) — Claude

Ajouter `load_project_tokens()` (lit `design_tokens.json` ou retourne defaults) et l'appeler dans `convert()` + `convert_image()` :

```python
async def load_project_tokens() -> dict:
    path = ROOT_DIR / "exports" / "design_tokens.json"
    if path.exists():
        return json.loads(path.read_text())
    return DEFAULT_TOKENS  # HoméOS defaults

# Dans les prompts, remplacer les valeurs hardcodées :
t = await load_project_tokens()
f"- Accent / Primary : `{t['colors']['primary']}`"
f"- Background : `{t['colors']['neutral']}`"
f"- Texte : `{t['colors']['text']}`"
f"- Typographie : {t['typography']['body']}"
f"- Border-radius : {t['shape']['border_radius']}"
```

#### Livrable C — Upload depuis la landing (Gemini)

Bouton discret "design system" dans le header landing :
- Clic → `<input type="file" accept=".md">` → `POST /api/project/import-design-md`
- Au chargement : `GET /api/project/design-tokens` → si `source == "homeos_design_md"` → pastille couleur `primary` + label "design actif"

**Bootstrap Gemini :**
```
Lire static/templates/landing.html — header existant.
Ajouter UNIQUEMENT : bouton "design system" discret (texte 11px, ghost) dans le header.
Au clic → file input .md → POST /api/project/import-design-md.
Au chargement → GET /api/project/design-tokens → si source présent → pastille ronde couleur primary (16px).
Lire static/css/stenciler.css — tokens V1. Pas d'uppercase. Geist 12px.
```

**Fichiers :**
- `Frontend/3. STENCILER/server_v3.py` — Livrable A
- `Backend/Prod/retro_genome/svg_to_tailwind.py` — Livrable B
- `static/templates/landing.html` — Livrable C (Gemini)

**Critères de sortie :**
- [ ] Upload `DESIGN.md` HoméOS → `design_tokens.json` créé avec primary + neutral + typo parsés
- [ ] `GET /api/project/design-tokens` → tokens parsés ou defaults HoméOS
- [ ] Génération SVG/PNG suivante → prompt LLM utilise les tokens du projet (pas hardcodés)
- [ ] Landing : pastille seed color visible si design importé
- [ ] Pas de régression si aucun DESIGN.md (defaults HoméOS inchangés)

---

### Mission 127 — Workspace V1 (Shell + Canvas Engine)
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


### Mission 129 — Workspace : features layer 2
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


### Mission 130-A — Header Minimal + Mode Aperçu Plein Écran
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


### Mission 130-B — Boutons Aperçu & Save par Screen
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


### Mission 130-C — Fix Robuste Panneaux Latéraux
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


### Mission 130 — Mode Inspect In-Preview & Monaco Popover
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


---

### Mission 131 — Exclusivité des Outils en Mode Aperçu & Nettoyage
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


### Mission 140 — Boutons Aperçu & Save dans le header de chaque screen canvas
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


### Mission 141 — Suppression d'imports depuis le panel Screens
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


### Mission 143 — Sullivan UI Compact : 2 bulles visibles
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


### Mission 142 — Sullivan Actions : édition directe du screen actif
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


### Mission 132 — Outils de Manipulation (Drag, Déplacer, Cadre, Place Image)
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


### Mission 132-B — Outil Place Image (suite M132)

**STATUS: 🟡 EN COURS**
**DATE: 2026-04-01**
**ACTOR: GEMINI (workspace.html) + CLAUDE (WsCanvas.js)**
**DÉPENDANCE: M132 ✅**

**Contexte :** Gemini a ajouté `<input type="file" id="ws-internal-image-loader" class="hidden" accept="image/*">` dans workspace.html. Il reste à câbler le wiring JS dans WsCanvas.js : clic outil "place-img" → ouvre le file picker → upload → insertion `<img>` à l'endroit cliqué dans le screen actif.

---

### Mission 133 — Undo & Color Picker Libre
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


### Mission 134 — Arsenal Typo (System Fonts & Webfont Generator)
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


### Mission 124 — Fallback Mimo après quota Gemini épuisé
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


### Mission 110 — Templates FRD : liste vide après manifest minimal

**STATUS: 🔴 HOTFIX**
**DATE: 2026-03-31**
**ACTOR: CLAUDE (CODE DIRECT)**

**Symptôme :** après création d'un manifest minimal depuis la landing, le sélecteur de templates dans frd_editor est vide.

**Diagnostic à mener :** vérifier l'endpoint qui alimente `#template-select` dans frd_editor — probablement un scan de répertoire conditionné à l'existence d'un manifest valide, ou un chemin qui change selon le projet actif.

**Critères de sortie :**
- [ ] Templates listés correctement après manifest minimal
- [ ] Pas de régression sur le flux normal (manifest complet)

---

## Thème 1 — Sullivan Typography Engine (suite)

### Mission 109C — Font Advisor + UI Landing
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


## Thème 2 — Architecture User / Project

**Contexte :** HoméOS est actuellement mono-projet global. En cours pédagogique, chaque étudiant travaille sur un projet distinct. Sans scoping, imports, manifests et templates se mélangent.

**Stratégie de découpage :** deux passes pour limiter le risque de régression. M111-A = backend pur (sans toucher les URLs). M111-B = UI sur base stable.

**Structure cible :**
```
ROOT_DIR/
  projects/
    {uuid}/
      manifest.json
      imports/
      exports/
      metadata.json     ← { id, name, created_at }
  static/fonts/         ← global (partagé entre projets)
```

---

### Mission 111-A — Multi-project : backend isolation

**STATUS: 🔵 BACKLOG**
**DATE: 2026-03-31**
**ACTOR: CLAUDE (CODE DIRECT)**

**Périmètre strict :** `server_v3.py` uniquement. Pas de changement d'URL. Le `project_id` transite par **session FastAPI** (cookie côté serveur), pas en query param.

#### Modèle de données

```python
# projects/{uuid}/metadata.json
{
  "id": "uuid4",
  "name": "Projet Cléa",
  "created_at": "2026-03-31T14:00:00",
}
# Session FastAPI : request.session["active_project_id"] = uuid
```

#### Helper de résolution de chemin

```python
def get_project_dir(project_id: str) -> Path:
    return ROOT_DIR / "projects" / project_id

def get_manifest_path(project_id: str) -> Path:
    return get_project_dir(project_id) / "manifest.json"

def get_imports_dir(project_id: str) -> Path:
    return get_project_dir(project_id) / "imports"
```

#### Migration douce au démarrage

```python
# lifespan() : si ROOT_DIR/exports/manifest.json existe → créer projet "default"
# et y copier manifest + imports/ (sans supprimer les originaux)
# → session["active_project_id"] = "default"
```

#### Routes à ajouter

```
GET    /api/projects              → liste { id, name, created_at }[]
POST   /api/projects              → { name } → créer dossier + metadata.json
POST   /api/projects/{id}/activate → session["active_project_id"] = id
DELETE /api/projects/{id}         → supprime dossier (sécurité : pas le projet actif)
GET    /api/projects/active       → { id, name } du projet en session
```

#### Endpoints existants à scoper (session-based, sans changer leur signature)

```
GET  /api/manifest/get            → lit get_manifest_path(session[active_project_id])
POST /api/manifest/save           → écrit idem
POST /api/import/upload           → sauvegarde dans get_imports_dir(session[...])
GET  /api/retro-genome/imports    → liste depuis get_imports_dir(session[...])
POST /api/preview/run             → isolée par projet (sous-dossier exports/)
```

**Ne pas toucher :**
- URLs existantes (aucun `?p=` en query param)
- `frd/files` (templates FRD = globaux, pas scopés au projet)
- `static/fonts/` (global)
- `bkd_service.py` (hors périmètre M111-A)
- Toute logique JS frontend

**Critères de sortie :**
- [ ] `POST /api/projects` → crée `projects/{uuid}/` + `metadata.json` + `imports/`
- [ ] `POST /api/projects/{id}/activate` → session mise à jour
- [ ] `GET /api/manifest/get` → lit dans le bon dossier projet
- [ ] Migration douce : si manifest racine existe → projet "default" créé au boot
- [ ] Test manuel : deux sessions browser → projets distincts, pas de collision

---

### Mission 111-B — Multi-project : UI landing + header

**STATUS: 🔵 BACKLOG**
**DÉPENDANCE: M111-A ✅**
**ACTOR: GEMINI (landing.html + bootstrap.js)**

#### UI landing.html

- Section `#project-switcher` en tête (avant `#import-section`) :
  - Liste des projets (`GET /api/projects`) → cartes cliquables
  - Bouton "nouveau projet" → prompt nom → `POST /api/projects` + activate
  - Projet actif surligné (bordure `#8cc63f`)
- Import scoping : `handleFiles` passe le projet actif (via état JS, pas URL)

#### UI bootstrap.js / header global

- Afficher le nom du projet actif à droite des tabs (petit texte 11px, couleur `#8cc63f`)
- Fetch `GET /api/projects/active` au chargement

**Bootstrap Gemini :**
```
Lire static/templates/landing.html — NE PAS toucher drop zone ni import-section.
Lire static/js/bootstrap.js — ajouter nom projet actif dans .pipeline-actions (droite).
Lire static/css/stenciler.css — tokens V1.
Lire Frontend/1. CONSTITUTION/LEXICON_DESIGN.json.
Pas d'uppercase. Pas d'emojis. Geist 12px. #8cc63f accents.
NE PAS ajouter ?p= dans les URLs.
```

**Critères de sortie :**
- [ ] Deux projets distincts → imports et manifests isolés sans collision
- [ ] Switching projet depuis la landing → pipeline rebascule

- [ ] Nom du projet actif visible dans le header global
- [ ] Nouveau projet → landing vierge (aucun import résiduel du projet précédent)

---

## Thème 3 — UX Cléa

**REF:** `docs/06_Design_Assets/ergonomic_study_clea_ux.md`
**REF:** `docs/06_Design_Assets/CORPUS_UX_CLEA.md`

### Mission 112 — Sullivan Welcome Screen

**STATUS: 🔵 BACKLOG**
**ACTOR: CLAUDE (endpoint) + GEMINI (landing.html)**
**DÉPENDANCE: M111 (scoping projet)**

Remplacer l'austère liste d'imports par un accueil sémantique Sullivan. *Effet de Halo* (Cléa UX P1).

#### Route backend (Claude)

```
GET /api/project/summary
→ {
    "project_name": "Projet Clea",
    "imports_count": 3,
    "last_intent": "formulaire de contact",
    "manifest_status": "ok" | "missing" | "minimal",
    "message": "3 écrans importés. Dernière intention : formulaire de contact."
  }
```

#### UI (Gemini)

- Zone `#sullivan-welcome` en tête de landing : nom projet + message Sullivan contextuel
- Remplacement badge polling par nudge discret orienté action

**Bootstrap Gemini :**
```
Lire static/templates/landing.html.
Lire static/css/stenciler.css.
Lire Frontend/1. CONSTITUTION/LEXICON_DESIGN.json.
Ajouter UNIQUEMENT #sullivan-welcome avant #import-section.
Pas d'uppercase. Pas d'emojis. Geist 12px.
```

**Critères de sortie :**
- [ ] Message Sullivan contextuel au chargement de la landing
- [ ] Mis à jour quand le projet change (M111)
- [ ] Pas de régression sur la drop zone

---

### Mission 113 — Sullivan Tips + Smart Nudges

**STATUS: 🔵 BACKLOG**
**ACTOR: CLAUDE (nudge engine) + GEMINI (UI)**
**DÉPENDANCE: M109A (typography_db.json)**

Utiliser les temps morts pour valoriser. *Intent Context Loading + Smart Nudges* (Cléa UX P3+P4).

#### Route backend (Claude)

```
GET /api/sullivan/tip
→ { "tip": "Les Garaldes portent un axe oblique hérité de la plume...", "source": "garaldes" }
```

Tips tirés de `typography_db.json` : `cultural_refs[]` + `pairings[]` de chaque catégorie (~50 tips disponibles).

Nudges Wire : pendant l'analyse, si route orpheline détectée → nudge non-bloquant.

#### UI (Gemini)

- Loading overlay Intent Viewer : tip Sullivan affiché pendant l'analyse SVG
- FRD header : nudge discret (toast 3s, non-bloquant) sur routes orphelines

**Bootstrap Gemini :**
```
Lire static/templates/intent_viewer.html — ajouter tip dans le loading state existant.
Lire static/css/frd_editor.css — ajouter toast style non-bloquant.
Lire Frontend/1. CONSTITUTION/LEXICON_DESIGN.json.
```

**Critères de sortie :**
- [ ] Tip typographique affiché pendant chaque analyse Intent Viewer
- [ ] Tips variés (pas toujours le même) — rotation aléatoire
- [ ] Nudge route orpheline : toast discret, disparaît seul après 3s
- [ ] Pas de régression sur les loaders existants

---

## Thème 4 — FRD Canvas v2 : features Stenciler portées

### Mission 114 — FRD Canvas v2 : snap grid + zoom + resize

**STATUS: 🔵 BACKLOG**
**DATE: 2026-03-31**
**ACTOR: CLAUDE (FrdWire.feature.js) + GEMINI (UI controls)**
**DÉPENDANCE: M112 + M113 (réfection UX Cléa accomplie)**

**Contexte :** Le Stenciler V3 a développé un moteur canvas SVG solide sur plusieurs missions (8C→14B). Ces features sont portables dans le FRD editor car FrdWire.feature.js est déjà en SVG natif. L'objectif n'est pas de copier le Stenciler mais d'enrichir le wire mode avec les interactions qui font sens pour un éditeur HTML/template.

**Features retenues (validées dans Stenciler)**

| Feature | Source Stenciler | État source | Travail de portage |
|---|---|---|---|
| Snap grid 8px | `_snap()` + `GRID.js` | ✅ solide | Minimal — greffer sur drag FrdWire |
| Zoom / panning | `_setupZoomControls()` + space+drag | ✅ solide | Copier-coller méthodes, adapter viewBox |
| Resize handles (rect) | `_showHandles()` | ✅ solide | Portable, uniquement `<rect>` |
| Drag nodes SVG | `_setupDragHandlers()` | ✅ solide | FrdWire a déjà du drag — unifier |
| Delete node | `_setupDeleteHandlers()` | ✅ trivial | Compléter raccourci clavier |

**Features exclues (trop couplées au genome Stenciler)**
- Drill-down Corps/Organe/Cellule — sémantique incompatible avec FRD (HTML templates, pas genome)
- Apply color broadcast — à concevoir différemment dans un contexte CSS/Tailwind
- Fond gradué — chantier UI complet, pas une feature de portage

**Livrables backend (Claude — CODE DIRECT)**

`FrdWire.feature.js` :
- Intégrer `GRID.js` (import ou copie inline des constantes)
- `_snap(v)` — arrondi 8px, activable via toggle
- `_setupZoom()` — boutons +/−/reset, viewBox scaling sur `#preview-iframe` SVG overlay
- `_setupPan()` — Space+drag sur le canvas wire
- `_setupResizeHandles()` — 4 coins sur `<rect>` sélectionnée, Shift = aspect ratio lock
- Unifier drag existant avec snap

**Livrables UI (Gemini — frd_editor.html + frd_editor.css)**

Barre de contrôles canvas (intégrée dans le header FRD existant) :
- Bouton grid toggle (icône grille, actif = vert HoméOS)
- Bouton snap toggle
- Affichage zoom % (ex: "100%")
- Boutons +/− zoom

**Bootstrap Gemini :**
```
Lire static/templates/frd_editor.html — header existant avec Inspect/Lock/Save.
Lire static/css/frd_editor.css — ne pas casser les styles existants.
Lire Frontend/1. CONSTITUTION/LEXICON_DESIGN.json.
Ajouter UNIQUEMENT les contrôles canvas dans le header FRD (après btn-lock, avant template-select).
Pas d'uppercase. Pas d'emojis. Geist 12px.
```

**Critères de sortie :**
- [ ] Drag wire node → snap automatique sur grille 8px
- [ ] Space+drag → pan du canvas wire
- [ ] Boutons +/− → zoom viewBox du SVG wire
- [ ] Clic `<rect>` → handles sur 4 coins, redimensionnement
- [ ] Grid toggle → grille SVG visible/cachée
- [ ] Pas de régression sur wire mode existant (M97→M103)

---

## Thème 5 — Pipeline landing → FRD : fluidité de base

### Mission 115 — Bouton "éditer" global + template courant dans FRD

**STATUS: 🔴 HOTFIX**
**DATE: 2026-03-31**
**ACTOR: GEMINI (landing.html + frd_editor.html)**

**Contexte :** Deux frictions bloquantes sur le pipeline de base :
1. La landing affiche des boutons "éditer" par intention — ce découpage par intent n'a pas de sens à ce stade. Il faut un seul bouton "ouvrir dans le FRD editor" par import.
2. Quand on arrive dans le FRD editor, le template en cours de travail n'est pas retrouvé automatiquement — le `#template-select` est vide ou désynchronisé.

#### Livrable A — landing.html : bouton "éditer" global par import (Gemini)

Remplacer les boutons par-intent par un seul bouton par carte d'import :
```
[ ouvrir dans frd editor ]  →  /frd-editor (+ marque le fichier comme courant)
```
- Un clic → `POST /api/frd/set-current { name: filename }` puis `window.location = '/frd-editor'`
- Pas d'édition inline par intent sur la landing

#### Livrable B — server_v3.py : route `set-current` (Claude CODE DIRECT)

```
POST /api/frd/set-current   { name: str }  →  stocke en mémoire _CURRENT_FRD_FILE
GET  /api/frd/current       →  { name: str | null }
```

#### Livrable C — frd_editor.html : auto-charger le fichier courant (Gemini)

Au chargement de `frd_editor.html` :
```javascript
// init() → GET /api/frd/current → si name → loadFile(name) + select dans #template-select
```

**Critères de sortie :**
- [ ] Clic "ouvrir dans frd editor" sur une carte import → arrive dans FRD avec le bon fichier chargé
- [ ] `#template-select` pointe sur le fichier courant
- [ ] Pas de régression sur le chargement manuel depuis `#template-select`

---

### Mission 116 — Fix pipeline intent_viewer → FRD editor
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


### Mission 117 — Fusion Intent → FRD : Analyse Intégrée
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


### Mission 118 — Pont SVG Illustrator → Tailwind Direct

**STATUS: ⚠️ PARTIEL — M118-B requis**
**DATE: 2026-03-31**
**ACTOR: CLAUDE (CODE DIRECT — backend uniquement)**
**DÉPENDANCE: M117 (panneau d'analyse FRD)**

**Contexte :** Le pipeline de génération existant (`/api/retro-genome/generate-html`) est conçu pour des PNGs uploadés via Retro Genome, pas pour des SVG Illustrator. Il nécessite Playwright, un cycle QA en plusieurs passes, et sauvegarde dans `/exports/retro_genome/` (hors de `static/templates/`). L'objectif de cette mission est de créer un **pont direct** SVG→Tailwind, plus simple et adapté au workflow landing → FRD Editor.

#### Livrable A — Nouveau module `svg_to_tailwind.py` (Claude)

Fichier : `Backend/Prod/retro_genome/svg_to_tailwind.py`

```python
async def convert(svg_content: str, import_name: str) -> str:
    """
    Protocole SVG AI (v1.0) + appel LLM direct.
    1. Filtrage du bruit : strip <font>, <glyph>, <image> base64
    2. Décodage .stX : mapper les classes CSS vers les tokens HoméOS
    3. Extraction des <text> et <rect>/<path> structurants (viewBox zones)
    4. Prompt LLM : "Traduis cette structure SVG annotée en HTML sémantique Tailwind"
    5. Retourne le HTML complet
    """
```

Contraintes du prompt LLM :
- Stack : HTML5 + Tailwind CDN
- Tokens HoméOS : `#f7f6f2` bg, `#3d3d3c` texte, `#8cc63f` accent
- Pas de largeurs fixes en px, Flexbox/Grid obligatoire
- Résultat : document HTML complet autonome (`<!DOCTYPE html>`)

#### Livrable B — Nouvelle route dans `routes.py` (Claude)

```python
POST /api/retro-genome/generate-from-svg
Body: { "import_id": str }

→ Lit le SVG via index.json + svg_path
→ Appelle svg_to_tailwind.convert()
→ Sauvegarde le résultat dans static/templates/{safe_name}.html
→ Retourne { "template_name": str, "status": "ok" }
```

**Important :** Le fichier généré doit être sauvegardé dans `static/templates/` (pas dans `/exports/`) pour être lisible par `GET /api/frd/file?name=...`.

#### Livrable C — Feedback temps réel : SSE ou polling (Claude)

La génération dure plusieurs secondes (appel LLM long). Implémenter l'une des deux options :
- **Option A (préférée)** : L'endpoint retourne immédiatement un `job_id`, puis `GET /api/retro-genome/svg-job/{job_id}` retourne `{ status: "pending"|"done", template_name? }`.
- **Option B (simple)** : L'endpoint est synchrone mais retourne immédiatement `{ status: "started" }` et le frontend poll `/api/frd/current` jusqu'à ce que `html_template` soit renseigné.

#### Ce que GEMINI fera ensuite (M119)

Une fois la route opérationnelle, connecter `FrdIntent.generateTailwind()` sur `/api/retro-genome/generate-from-svg` et ajouter l'indicateur de chargement dans Sullivan Chat.

**Fichiers à créer/modifier :**
- `Backend/Prod/retro_genome/svg_to_tailwind.py` **[NEW]**
- `Backend/Prod/retro_genome/routes.py` — ajout route `generate-from-svg` **[MODIFY]**

**Critères de sortie :**
- [ ] `POST /api/retro-genome/generate-from-svg` avec `import_id` valide → retourne `{ template_name: "...", status: "ok" }`
- [ ] Le fichier `.html` généré est présent dans `static/templates/`
- [ ] `GET /api/frd/file?name={template_name}` → 200 avec le contenu HTML Tailwind
- [ ] Le HTML généré contient des tokens HoméOS (couleurs, Geist, lowercase)
- [ ] Pas de modification de la route `/generate-html` existante

---

### Mission 118-B — Routeur de formats d'import + prompts adaptatifs

**STATUS: 🔵 BACKLOG**
**DATE: 2026-03-31**
**ACTOR: CLAUDE (CODE DIRECT — `svg_to_tailwind.py` + `routes.py`)**
**DÉPENDANCE: M118 (module `svg_to_tailwind.py` existant)**

**Contexte :** Le pipeline actuel est aveugle au format source. Il traite tous les SVG de la même façon et dit au LLM "lis les `<text>`" même quand il n'y en a pas (SVG vectorisé). Résultat : lorem ipsum systématique sur les exports Illustrator.

**5 formats à router, 5 stratégies distinctes :**

| Format | Signal de détection | Stratégie |
|---|---|---|
| **Illustrator SVG vectorisé** | `<text>=0` + classes `.stX` | Inférence structurelle par couleurs |
| **Figma SVG** | `<text>` présents + `id="node-/frame-"` | Lecture directe texte + hiérarchie |
| **HTML/CSS ZIP** | `.zip` + `.html` dedans, pas de `.tsx` | Extraction HTML principal + inline CSS |
| **React/ZIP** | `.zip` + `.tsx/.jsx` dedans | M119 (transpilation JSX→HTML) |
| **PNG/JPG** | extension image | Pipeline Playwright existant (hors scope) |

#### Livrable A — `detect_import_format(content, filename)` dans `svg_to_tailwind.py`

```python
def detect_svg_type(svg_content: str) -> str:
    has_text  = bool(re.search(r'<text', svg_content))
    has_stx   = bool(re.search(r'\.(st\d+)', svg_content))
    has_figma = bool(re.search(r'id="node-|id="frame-', svg_content))
    if not has_text and has_stx: return "illustrator_vectorized"
    if has_figma:                return "figma"
    if has_text:                 return "structured_svg"
    return "unknown"
```

#### Livrable B — Prompt adaptatif selon le type dans `convert()`

**illustrator_vectorized** : extraire palette couleurs + rects + viewBox → décrire la structure au LLM sans lui envoyer le SVG brut :
```python
color_freq = Counter(re.findall(r'fill="(#[0-9a-fA-F]{3,6}|white)"', svg_content))
rects = re.findall(r'<rect[^/]*/>', svg_content)
viewbox = re.search(r'viewBox="([^"]+)"', svg_content)
# Prompt : "Ce SVG est vectorisé. Palette : ... Rects : ... Interface de type [nom_fichier]. Génère le HTML."
```

**figma / structured_svg** : prompt actuel (déjà bon, il y a du `<text>` à lire).

#### Livrable C — Route `generate-from-svg` dans `routes.py` : router ZIP

Actuellement la route ne gère que les SVG depuis `index.json`. Ajouter :
- Si `entry["name"]` se termine en `.zip` → extraire l'archive en mémoire → détecter React vs HTML/CSS → appeler le bon convertisseur

**Fichiers :**
- `Backend/Prod/retro_genome/svg_to_tailwind.py` — A + B
- `Backend/Prod/retro_genome/routes.py` — C

**Critères de sortie :**
- [ ] SVG Illustrator vectorisé → layout reconnaissable (palette HoméOS, pas de lorem ipsum)
- [ ] SVG Figma → comportement inchangé (textes lus directement)
- [ ] ZIP HTML/CSS → HTML principal extrait et servi comme template
- [ ] ZIP React → message clair "format React détecté, M119 requis" (pas de crash)

---

### Mission 120 — Rebranchement Plugin Figma → FRD Editor

**STATUS: 🔵 BACKLOG**
**DATE: 2026-03-31**
**ACTOR: CLAUDE (backend) + GEMINI (frontend)**
**DÉPENDANCE: M38 (plugin Figma existant), M116 (pipeline set-current)**

**Contexte :** Le plugin Figma (M38) est le chemin le plus précis pour la conversion design → HTML. Il envoie la structure Figma native (frames nommés, textes, composants) directement à l'API locale. Il était branché sur l'ancien viewer (`/api/retro-genome/reality`). Il faut le rebrancher sur le nouveau pipeline FRD Editor.

**Localisation du plugin :** chercher dans le repo un dossier `figma-plugin/` ou `plugin/` contenant `manifest.json`, `code.js`, `ui.html`.

#### Livrable A — server_v3.py : nouvelle route Figma (Claude)

```
POST /api/figma/import
Body: { frames: [...], project_name: str }
→ Stocke les données Figma dans projects/{active}/imports/figma_{timestamp}.json
→ Déclenche generate-from-svg (adapté Figma) ou appelle directement HtmlGenerator
→ Retourne { import_id, status: "started", job_id }
```

#### Livrable B — Plugin Figma code.js : changer la cible (Claude)

Remplacer l'endpoint cible :
```javascript
// Avant (M38)
fetch('http://localhost:9998/api/retro-genome/reality', ...)
// Après (M120)
fetch('http://localhost:9998/api/figma/import', ...)
```

#### Livrable C — landing.html : afficher les imports Figma (Gemini)

Les imports Figma apparaissent dans la liste avec un badge `figma` distinct des SVG.

**Fichiers :**
- `Frontend/3. STENCILER/server_v3.py` — route `/api/figma/import`
- Plugin Figma `code.js` — changer URL cible
- `static/templates/landing.html` — badge figma (Gemini)

**Critères de sortie :**
- [ ] Plugin Figma → bouton "Envoyer à HoméOS" → import visible dans la landing
- [ ] Import Figma → "ouvrir dans frd editor" → template HTML généré et chargé
- [ ] Pas de régression sur les imports SVG existants

---

### Mission 122 — Pipeline import unifié : tous formats → FRD editor
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


### Mission 119 — Pont React/ZIP → Tailwind Direct
**STATUS: ✅ LIVRÉ** — archivée dans ROADMAP_ACHIEVED.md

---


## Features prioritaires

### Mission 135 — Système d'Authentification & Base User
**STATUS: 🔵 BACKLOG**
- [ ] Création de la table `users` (SQLite/PostgreSQL) : `id`, `email`, `password_hash`, `created_at`.
- [ ] Backend logic : Inscription (`/api/auth/register`) et Connexion (`/api/auth/login`) avec JWT ou session sécurisée.
- [ ] Frontend : Pages `register.html` et `login.html` (Design HoméOS, simple, épuré).
- [ ] Middleware : Protection des routes API nécessitant une authentification.

### Mission 136 — Gestion Multi-tenancy : User ID x Project ID
**STATUS: 🔵 BACKLOG**
- [ ] Relation Many-to-Many ou One-to-Many entre `users` et `projects`.
- [ ] Mise à jour du scoper de chemin : `projects/{user_id}/{project_uuid}/`.
- [ ] Migration des projets existants vers l'utilisateur "admin" ou "default" par défaut.
- [ ] UI : Dashboard utilisateur listant uniquement *ses* projets.

### Mission 137 — Système BYOK (Bring Your Own Key)
**STATUS: 🔵 BACKLOG**
- [ ] Backend : Stockage chiffré des clés API (Gemini, DeepSeek, OpenAI) dans le profil utilisateur.
- [ ] Logic : Le `GeminiClient` et les autres adaptateurs vérifient d'abord la clé utilisateur avant d'utiliser la clé système (quota management).
- [ ] UI : Panneau "Paramètres" → "Clés API" avec indicateur de validité.

### Mission 138 — Bouton Upload Universel & Pipeline Assets
**STATUS: 🔵 BACKLOG**
- [ ] Bouton "+" ou "Upload" flottant dans le Workspace.
- [ ] Support Drag & Drop universel (SVG, PNG, JPG, DESIGN.md).
- [ ] Pipeline automatique : détection du type de fichier et routage vers la bonne mission (M118, M128, etc.).

### Mission 139 — Révision du mode Wired (FrdWire v2)
**STATUS: 🔵 BACKLOG**
- [ ] Multi-sélection d'éléments (clic-glissé ou Shift+clic).
- [ ] Raccourcis clavier complets (Duplicate Cmd+D, Group Cmd+G, Alignement).
- [ ] Feedback visuel enrichi : lignes de rappel (Smart Guides) lors du drag.
- [ ] Synchronisation temps-réel bidirectionnelle : modification Code → mise à jour Wire instantanée.
