/* WsChat.js — Sullivan Workspace Chat (Mission 127 V2) */

class WsChat {
    constructor(mountId) {
        this.mount = document.getElementById(mountId);
        this.historyEl = document.getElementById('ws-chat-history');
        this.inputEl = document.getElementById('ws-chat-input');
        this.sendBtn = document.getElementById('btn-ws-send');
        this.modeBtns = document.querySelectorAll('.ws-mode-btn');
        
        this.currentMode = 'construct';
        this.init();
    }

    init() {
        if (this.sendBtn) this.sendBtn.onclick = () => this.sendMessage();
        this.inputEl.onkeydown = (e) => { 
            if (e.key === 'Enter' && !e.shiftKey) { 
                e.preventDefault(); 
                this.sendMessage(); 
            }
        };
        
        this.modeBtns.forEach(btn => {
            btn.onclick = () => {
                this.modeBtns.forEach(b => b.classList.remove('active', 'bg-homeos-green', 'text-white'));
                btn.classList.add('active', 'bg-homeos-green', 'text-white');
                this.currentMode = btn.dataset.mode;
                console.log("🚀 WsChat: mode switched to", this.currentMode);

                // Mission 147: Wire mode → enter preview + show overlay
                if (this.currentMode === 'wire') {
                    const activeId = window.wsCanvas?.activeScreenId;
                    if (!activeId) { alert('Sélectionnez un screen sur le canvas d\'abord.'); return; }
                    if (window.enterPreviewMode) window.enterPreviewMode(activeId);
                    // Show wire overlay even without manifest
                    const shell = document.getElementById(activeId);
                    const manifest = shell?.dataset?.manifest ? JSON.parse(shell.dataset.manifest) : { screens: [], components: [] };
                    window.wsWire?.show(manifest, shell?.querySelector('.ws-screen-title')?.textContent || activeId);
                }
            };
        });

        // Current mode default
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

    async handleDirectUpload(event) {
        const files = event.target.files;
        if (!files || files.length === 0) return;

        // Bulle temporaire "en cours" — supprimée après succès
        const pendingBubble = this._appendTransient(`upload en cours...`);

        for (let file of files) {
            try {
                await this._uploadRaw(file);

                if (window.fetchWorkspaceImports) await window.fetchWorkspaceImports();

                const res = await fetch('/api/retro-genome/imports');
                const list = await res.json();
                const imports = list.imports || [];
                const item = imports[0]; // On prend le plus récent

                if (item && window.wsCanvas) {
                    window.wsCanvas.addScreen(item);
                }
            } catch (e) {
                console.error("WsChat: upload failed", e);
                this.appendBubble(`erreur upload ${file.name} : ${e.message}`, 'sullivan');
            }
        }

        // Retire la bulle transitoire
        if (pendingBubble) pendingBubble.remove();
        this._checkHistoryVisibility();

        // Reset input
        event.target.value = '';
    }

    _appendTransient(text) {
        const b = this.appendBubble(text, 'sullivan');
        if (b) b.classList.add('opacity-50', 'italic'); // Style visuel pour le "en cours"
        return b;
    }

    _checkHistoryVisibility() {
        if (this.historyEl && !this.historyEl.children.length) {
            this.historyEl.classList.add('hidden');
        }
    }

    async _uploadRaw(file) {
        const ext = file.name.split('.').pop().toLowerCase();
        if (ext === 'svg') {
            const svgContent = await file.text();
            const res = await fetch('/api/retro-genome/upload-svg', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ svg: svgContent, name: file.name })
            });
            if (!res.ok) throw new Error(`svg upload ${res.status}`);
            return res.json();
        } else {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('filename', file.name);
            const res = await fetch('/api/import/upload', { method: 'POST', body: formData });
            if (!res.ok) throw new Error(`upload ${res.status}`);
            return res.json();
        }
    }

    async uploadFile(file) {
        // ... (keep as is or remove if redundant, handleDirectUpload uses _uploadRaw)
        return this._uploadRaw(file);
    }

    appendBubble(text, sender = 'user') {
        const b = document.createElement('div');
        b.className = `p-3 rounded-lg text-[12px] max-w-[90%] transition-all ${sender === 'sullivan' ? 'bg-slate-50 border border-slate-100 self-start shadow-sm' : 'bg-slate-900 text-white self-end ml-auto'}`;
        
        if (sender === 'sullivan') {
            b.innerHTML = `
                <div class="flex items-center gap-2 mb-1">
                    <div class="w-1.5 h-1.5 rounded-full bg-homeos-green"></div>
                    <span class="font-bold text-[9px] uppercase tracking-tighter">sullivan arbitrator</span>
                </div>
                <div class="leading-relaxed whitespace-pre-wrap">${text}</div>
            `;
        } else {
            b.innerText = text;
        }

        if (!this.historyEl) { console.warn("WsChat: historyEl missing", b.textContent); return null; }
        this.historyEl.appendChild(b);
        this.historyEl.classList.remove('hidden');
        this.historyEl.scrollTop = this.historyEl.scrollHeight;

        return b;
    }

    async sendMessage() {
        const msg = this.inputEl.value.trim();
        if (!msg) return;

        this.appendBubble(msg, 'user');
        this.inputEl.value = '';
        
        // --- SULLIVAN API (Mission 142 + 152: Full Canvas Context) ---
        let screen_html = null;
        const canvas_screens = [];

        const _getIframeHtml = async (iframe) => {
            if (!iframe) return null;
            if (iframe._lastSullivanHtml) return iframe._lastSullivanHtml; // Sullivan a déjà édité
            if (iframe.srcdoc) return iframe.srcdoc;
            if (iframe.src) {
                try { return await (await fetch(iframe.src)).text(); } catch(_) {}
            }
            return null;
        };

        // 1. Écran Actif (Priorité 1: preview, Priorité 2: canvas)
        const previewIframe = document.querySelector('#ws-preview-frame-container iframe');
        if (previewIframe) {
            screen_html = await _getIframeHtml(previewIframe);
        }
        if (!screen_html && window.wsCanvas?.activeScreenId) {
            const shell = document.getElementById(window.wsCanvas.activeScreenId);
            screen_html = await _getIframeHtml(shell?.querySelector('iframe'));
        }

        // 2. Autres Écrans du Canvas (Mission 152)
        const shells = document.querySelectorAll('.ws-screen-shell');
        for (const shell of shells) {
            const id = shell.getAttribute('id');
            if (id === window.wsCanvas?.activeScreenId) continue; // Déjà dans screen_html
            
            const title = shell.querySelector('.ws-screen-title')?.textContent || id;
            const iframe = shell.querySelector('iframe');
            const html = await _getIframeHtml(iframe);
            if (html) canvas_screens.push({ id, title, html });
        }

        // 3. Élément sélectionné (M154) — focus précis sur l'organe courant
        let selected_element = null;
        if (window.wsInspect?.currentSelector) {
            const selector = window.wsInspect.currentSelector;
            const previewDoc = document.querySelector('#ws-preview-frame-container iframe')?.contentDocument;
            const canvasDoc = window.wsCanvas?.activeScreenId
                ? document.getElementById(window.wsCanvas.activeScreenId)?.querySelector('iframe')?.contentDocument
                : null;
            const doc = previewDoc || canvasDoc;
            if (doc) {
                try {
                    const el = doc.querySelector(selector);
                    if (el) {
                        selected_element = {
                            selector,
                            tag: el.tagName.toLowerCase(),
                            html: el.outerHTML.slice(0, 2000)
                        };
                    }
                } catch(_) {}
            }
        }

        // 4. Wires (M161)
        const wires = window.wsWire?.getWires() || [];
        
        const pending = this._appendTransient("Je traite votre demande en mode " + this.currentMode + "...");

        try {
            const res = await fetch('/api/sullivan/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: msg,
                    mode: this.currentMode,
                    screen_html: screen_html,
                    canvas_screens: canvas_screens,
                    selected_element: selected_element,
                    wires: wires
                })
            });
            const data = await res.json();
            
            // Nettoyage de la bulle d'attente avant d'afficher la réponse
            if (pending) pending.remove();

            if (data.explanation) {
                this.appendBubble(data.explanation, 'sullivan');
            }

            // Mission 142: Apply HTML modification if returned
            console.log('[WsChat] response html len:', data.html?.length, '| activeScreenId:', window.wsCanvas?.activeScreenId);
            if (data.html && window.wsPreview) {
                window.wsPreview.updateActiveScreenHtml(data.html);
            }
        } catch (e) {
            console.error("WsChat: send failed", e);
            if (pending) pending.remove();
            this.appendBubble("Désolé, une erreur technique est survenue.", 'sullivan');
        }

        this._checkHistoryVisibility();
    }
}
