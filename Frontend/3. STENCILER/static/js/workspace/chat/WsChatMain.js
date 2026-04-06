/* WsChatMain.js — Global Workspace Chat (Mission 127 V2 + Refactor) */

class WsChatMain extends WsChatBase {
    constructor(mountId) {
        super(mountId, 'ws-chat-history', 'ws-chat-input', 'btn-ws-send');
        this.modeBtns = document.querySelectorAll('.ws-mode-btn');
        this.currentMode = 'construct';
        this.init();
    }

    init() {
        this.initBase();
        
        this.modeBtns.forEach(btn => {
            btn.onclick = () => {
                this.modeBtns.forEach(b => b.classList.remove('active', 'bg-homeos-green', 'text-white'));
                btn.classList.add('active', 'bg-homeos-green', 'text-white');
                this.currentMode = btn.dataset.mode;
                console.log("🚀 WsChatMain: mode switched to", this.currentMode);

                // Mission 147: Wire mode → enter preview + show overlay
                if (this.currentMode === 'wire') {
                    const activeId = window.wsCanvas?.activeScreenId;
                    if (!activeId) { alert('Sélectionnez un screen sur le canvas d\'abord.'); return; }
                    if (window.enterPreviewMode) window.enterPreviewMode(activeId);
                    
                    const shell = document.getElementById(activeId);
                    const manifest = shell?.dataset?.manifest ? JSON.parse(shell.dataset.manifest) : { screens: [], components: [] };
                    window.wsWire?.show(manifest, shell?.querySelector('.ws-screen-title')?.textContent || activeId);
                }
            };
        });

        // Initialize default mode
        const constructBtn = document.querySelector('[data-mode="construct"]');
        if (constructBtn) constructBtn.click();
        
        // Typo button toggle (Mission 129)
        const typoBtn = document.getElementById('btn-ws-typo');
        if (typoBtn) {
            typoBtn.onclick = () => {
                const drawer = document.getElementById('ws-font-drawer');
                drawer.classList.toggle('hidden');
                typoBtn.classList.toggle('text-homeos-green');
            };
        }
    }

    async sendMessage() {
        const msg = this.inputEl.value.trim();
        if (!msg) return;

        this.appendBubble(msg, 'user');
        this.inputEl.value = '';
        
        const payload = await this._gatherContext(msg);
        const pending = this._appendTransient("Je traite votre demande en mode " + this.currentMode + "...");

        try {
            const data = await this.callSullivanAPI(payload);
            if (pending) pending.remove();
            if (data.explanation) this.appendBubble(data.explanation, 'sullivan');
            if (data.html && window.wsPreview) {
                window.wsPreview.updateActiveScreenHtml(data.html);
            }
        } catch (e) {
            console.error("WsChatMain: send failed", e);
            if (pending) pending.remove();
            this.appendBubble("Désolé, une erreur technique est survenue.", 'sullivan');
        }

        this._checkHistoryVisibility();
    }

    async _gatherContext(msg) {
        let screen_html = null;
        const canvas_screens = [];

        const _getIframeHtml = async (iframe) => {
            if (!iframe) return null;
            if (iframe._lastSullivanHtml) return iframe._lastSullivanHtml;
            if (iframe.srcdoc) return iframe.srcdoc;
            if (iframe.src) {
                try { return await (await fetch(iframe.src)).text(); } catch(_) {}
            }
            return null;
        };

        const previewIframe = document.querySelector('#ws-preview-frame-container iframe');
        if (previewIframe) screen_html = await _getIframeHtml(previewIframe);

        if (!screen_html && window.wsCanvas?.activeScreenId) {
            const shell = document.getElementById(window.wsCanvas.activeScreenId);
            screen_html = await _getIframeHtml(shell?.querySelector('iframe'));
        }

        const shells = document.querySelectorAll('.ws-screen-shell');
        for (const shell of shells) {
            const id = shell.getAttribute('id');
            if (id === window.wsCanvas?.activeScreenId) continue;
            const iframe = shell.querySelector('iframe');
            const html = await _getIframeHtml(iframe);
            if (html) canvas_screens.push({ id, html });
        }

        let selected_element = null;
        if (window.wsInspect?.currentSelector) {
            const selector = window.wsInspect.currentSelector;
            const previewDoc = document.querySelector('#ws-preview-frame-container iframe')?.contentDocument;
            const doc = previewDoc || document.querySelector('.ws-screen-shell iframe')?.contentDocument;
            if (doc) {
                try {
                    const el = doc.querySelector(selector);
                    if (el) selected_element = { selector, tag: el.tagName.toLowerCase(), html: el.outerHTML.slice(0, 1000) };
                } catch(_) {}
            }
        }

        const wires = window.wsWire?.getWires() || [];
        // Résoudre le project_id actif
        let project_id = 'active';
        try {
            const pr = await fetch('/api/projects/active');
            const pd = await pr.json();
            if (pd.id) project_id = pd.id;
        } catch(_) {}
        return { message: msg, mode: this.currentMode, screen_html, canvas_screens, selected_element, wires, project_id };
    }
}

window.WsChatMain = WsChatMain;
