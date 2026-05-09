/**
 * WsWireRouter.js — Point d'entrée intelligent état-projet (M424)
 * Orchestre le passage entre annotation, génération de câblage et preview.
 */
class WsWireRouter {
    constructor() {
        this._active = false;
        this._running = false;
        this.config = {
            threshold: 3 // Seuil minimum d'annotations par écran
        };
        
        // M424-A: Reset active flag when changing mode manually
        window.addEventListener('message', (e) => {
            if (e.data?.type === 'ws-mode-changed') {
                if (!['wire', 'annotation', 'wired'].includes(e.data.mode)) {
                    this._active = false;
                }
            }
        });
    }

    async enter() {
        if (this._running) return;
        this._running = true;
        this._active = true;
        const pid = this._getProjectId();
        if (!pid) {
            console.error("[WsWireRouter] Aucun project_id trouvé");
            this._running = false;
            return;
        }

        try {
            console.log("[WsWireRouter] starting...");
            const manifest = await this._loadManifest(pid);
            
            // M424-A: Auto-population si canvas vide
            const existingShells = document.querySelectorAll('[data-screen-id], .ws-screen-shell');
            if (existingShells.length === 0 && manifest.storyboard?.length > 0) {
                console.log("[WsWireRouter] Canvas vide, auto-population...");
                await this._populateCanvasFromStoryboard(pid);
                // Attendre que les shells soient rendus
                await new Promise(r => setTimeout(r, 600));
                // M427: Recharger le manifest pour avoir les IDs réels après population
                const updatedManifest = await this._loadManifest(pid);
                const updatedState = this._computeState(updatedManifest);
                this._applyShellOverlays(updatedManifest, updatedState);
                this._route(updatedState, updatedManifest);
                return; // On arrête là car on a déjà routé
            }

            const state = this._computeState(manifest);
            
            // Appliquer les voiles visuels sur le canvas
            this._applyShellOverlays(manifest, state);
            
            // Router vers l'action appropriée
            this._route(state, manifest);
        } catch (err) {
            console.error("[WsWireRouter] Erreur enter:", err);
        } finally {
            this._running = false;
        }
    }

    _computeState(manifest) {
        // Use actual DOM shells as source of truth — storyboard IDs may be stale/abstract
        const shellIds = [...document.querySelectorAll('[data-screen-id]')]
            .map(s => s.getAttribute('data-screen-id')).filter(Boolean);

        if (shellIds.length === 0) return 'no_screens';

        const flow = manifest.flow || [];
        const annotations = manifest.annotations || [];
        const wires = manifest.wires || [];
        const linkedIds = new Set([...flow.map(f => f.from), ...flow.map(f => f.to)]);
        const threshold = manifest.wire_threshold || this.config.threshold;

        const allLinked = shellIds.every(id => linkedIds.has(id));
        const allAnnotated = shellIds.every(id =>
            annotations.filter(a => a.screen_id === id).length >= threshold
        );

        if (!allLinked || !allAnnotated) return 'annotation_incomplete';
        if (wires.length === 0) return 'ready_to_wire';
        return 'wired';
    }

    _applyShellOverlays(manifest, state) {
        const flow = manifest.flow || [];
        const annotations = manifest.annotations || [];
        const threshold = manifest.wire_threshold || this.config.threshold;

        // Iterate on actual canvas shells — storyboard IDs may be stale/abstract (M427+)
        document.querySelectorAll('[data-screen-id]').forEach(shell => {
            const screenId = shell.getAttribute('data-screen-id');
            const isLinked = flow.some(f => f.from === screenId || f.to === screenId);
            const annotationCount = annotations.filter(a => a.screen_id === screenId).length;

            let overlayClass = 'ws-shell-overlay-grey';
            if (isLinked && annotationCount === 0)
                overlayClass = 'ws-shell-overlay-red';
            else if (isLinked && annotationCount < threshold)
                overlayClass = 'ws-shell-overlay-orange';
            else if (isLinked && annotationCount >= threshold)
                overlayClass = 'ws-shell-overlay-green';

            shell.querySelectorAll('.ws-wire-overlay').forEach(el => el.remove());

            const bg = shell.querySelector('rect.ws-screen-bg');
            const w = bg?.getAttribute('width') || '400';
            const h = bg?.getAttribute('height') || '632';

            const overlay = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            overlay.setAttribute('class', `ws-wire-overlay ${overlayClass}`);
            overlay.setAttribute('width', w);
            overlay.setAttribute('height', h);
            overlay.setAttribute('rx', '20');
            overlay.setAttribute('pointer-events', 'none');
            shell.appendChild(overlay);
        });
    }

    _route(state, manifest) {
        const pid = this._getProjectId();

        switch (state) {
            case 'no_screens':
                window.ManifestSullivan?.appendBubble(
                    "importe d'abord des écrans dans ton projet pour commencer le câblage.", 'sullivan');
                break;

            case 'annotation_incomplete':
                // Rester en mode wire — ne pas écraser le mode utilisateur
                
                // Sullivan résume la situation
                const missing = this._getMissingScreens(manifest);
                let msg = "";
                if (missing.unlinked > 0) msg += `${missing.unlinked} écran(s) sans lien. `;
                if (missing.unannotated > 0) msg += `${missing.unannotated} écran(s) sans annotation complète. `;
                msg += `clique sur un écran rouge ou orange pour commencer.`;
                
                window.ManifestSullivan?.appendBubble(msg, 'sullivan');
                
                // UxRun
                this._log('wire_router', 'annotation_incomplete', missing);
                break;

            case 'ready_to_wire':
                // Tout annoté → lancer la génération Wire
                window.ManifestSullivan?.appendBubble(
                    "tous tes écrans sont prêts. je génère le câblage...", 'sullivan');
                if (window.wsWire) {
                    window.wsWire.show(manifest);
                }
                this._log('wire_router', 'wire_generation_started', {});
                break;

            case 'wired':
                // Wire existe → ouvrir Preview Wired
                window.ManifestSullivan?.appendBubble(
                    "ton app est déjà câblée. tu veux la tester ?", 'sullivan');
                const entry = manifest.flow?.[0]?.from || manifest.storyboard?.[0]?.screen_id;
                if (window.wsPreview) {
                    window.wsPreview.enterWiredMode(entry);
                }
                this._log('wire_router', 'preview_wired_opened', { entry });
                break;
        }
    }

    _getMissingScreens(manifest) {
        const storyboard = manifest.storyboard || [];
        const flow = manifest.flow || [];
        const annotations = manifest.annotations || [];
        const linkedIds = new Set([...flow.map(f => f.from), ...flow.map(f => f.to)]);
        const threshold = manifest.wire_threshold || this.config.threshold;

        return {
            unlinked: storyboard.filter(s => !linkedIds.has(s.screen_id)).length,
            unannotated: storyboard.filter(s =>
                annotations.filter(a => a.screen_id === s.screen_id).length < threshold
            ).length
        };
    }

    _log(tag, label, details) {
        const pid = this._getProjectId();
        fetch('/api/ux-run/event', { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                tag: tag.toUpperCase(), 
                label, 
                ts: Date.now(),
                project_id: pid, 
                details 
            })
        }).catch(() => {});
    }

    /**
     * Peupler le canvas depuis les imports réels + recaler le manifest.storyboard
     */
    async _populateCanvasFromStoryboard(pid) {
        try {
            const token = window.wsState?.session?.token || '';
            const res = await fetch(`/api/retro-genome/imports?project_id=${pid}`, {
                headers: { 'X-User-Token': token }
            });
            if (!res.ok) return;
            const data = await res.json();

            // Source de vérité = imports visuels, pas le storyboard Sullivan
            const _screenExts = ['html', 'htm', 'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'];
            const imports = (data.imports || []).filter(imp => {
                const ext = (imp.name || '').toLowerCase().split('.').pop();
                return _screenExts.includes(ext);
            }).sort((a, b) => (a.name || '').localeCompare(b.name || '', undefined, { numeric: true, sensitivity: 'base' }));

            if (imports.length === 0) return;

            const columns = 3;
            const newStoryboard = [];

            for (let i = 0; i < imports.length; i++) {
                const imp = imports[i];
                const screenWithProject = { ...imp, project_id: pid };
                const shell = await window.wsCanvas.addScreen(screenWithProject);

                if (shell) {
                    // screen_id = import.id → cohérence totale storyboard ↔ canvas ↔ overlays
                    shell.setAttribute('data-screen-id', imp.id);
                    const col = i % columns;
                    const row = Math.floor(i / columns);
                    const x = 50 + col * (imp.type === 'html' ? 1300 : 500);
                    const y = 50 + row * 900;
                    shell.setAttribute('transform', `matrix(1 0 0 1 ${x} ${y})`);

                    newStoryboard.push({ screen_id: imp.id, screen_name: imp.name });
                }
            }

            // Recaler manifest.storyboard avec les vrais IDs d'import
            if (newStoryboard.length > 0) {
                await fetch(`/api/projects/${pid}/manifest`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json', 'X-User-Token': token },
                    body: JSON.stringify({ storyboard: newStoryboard })
                }).catch(() => {});
            }
            
            // Reset view pour voir tout le monde
            if (window.wsCanvas) window.wsCanvas.resetView();
            
        } catch (e) {
            console.error("[WsWireRouter] Auto-population failed:", e);
        }
    }

    _getProjectId() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('project_id') || window.wsState?.projectId;
    }

    async _loadManifest(pid) {
        const token = window.wsState?.session?.token || '';
        const res = await fetch(`/api/projects/${pid}/manifest`, {
            headers: { 'X-User-Token': token }
        });
        if (!res.ok) throw new Error("Erreur chargement manifeste");
        return await res.json();
    }
}

window.wsWireRouter = new WsWireRouter();
