/**
 * WsFEEStudio - Labo Photo (FEE Studio) pour l'étalonnage GSAP
 * Mission 221 — HoméOS 2026
 */
class WsFEEStudio {
    constructor(wsBackend) {
        this.ws = wsBackend;
        this.isOpen = false;
        this.activeScreen = null;
        this.isGenerating = false;
        this.feeHistory = [];
        this.selectedTrigger = null;
        this.selectedState = 'initial'; // initial | hover | click | scroll-trigger
        this.previewScale = 1.0;
        this.previewMinScale = 0.2;
        this.previewMaxScale = 3.0;

        this.init();
    }

    init() {
        // L'UI est injectée dynamiquement au premier open()
    }

    injectUI() {
        if (document.getElementById('fee-studio-overlay')) return;

        const overlay = document.createElement('div');
        overlay.id = 'fee-studio-overlay';
        overlay.className = 'hidden fixed inset-6 z-[9000] bg-[#f7f6f2] flex flex-col font-sans text-[#3d3d3c] rounded-[20px] shadow-[0_4px_16px_rgba(0,0,0,0.06)] overflow-hidden border border-[#e5e5e5]';
        overlay.style.fontFamily = "'Univers LT Std', 'Geist', -apple-system, sans-serif";

        overlay.innerHTML = `
            <!-- HEADER -->
            <header class="h-[48px] border-b border-[#e5e5e5] px-6 flex items-center justify-between bg-white shrink-0">
                <div class="flex items-center gap-4">
                    <span class="text-[10px] font-black tracking-[0.2em] uppercase text-[#3d3d3c]">fee studio <span class="text-[#8cc63f]">camera raw</span></span>
                    <div class="h-4 w-px bg-[#e5e5e5]"></div>
                    <span id="fee-studio-project-label" class="text-[10px] font-bold text-[#9a9a98] lowercase italic">Projet: ...</span>
                </div>
                <button id="fee-studio-btn-close" class="p-2 text-[#9a9a98] hover:text-[#3d3d3c] transition-colors rounded-[20px]">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
            </header>

            <!-- MAIN CONTENT -->
            <div class="flex-1 flex divide-x divide-[#e5e5e5] overflow-hidden">
                
                <!-- GAUCHE: EXPLOREUR -->
                <aside class="w-[240px] flex flex-col bg-white shrink-0">
                    <div class="p-3 border-b border-[#e5e5e5] bg-[#f7f6f2]/50">
                        <span class="text-[9px] font-black uppercase tracking-widest text-[#9a9a98]">explorateur triggers</span>
                    </div>
                    <!-- State Selector -->
                    <div class="p-3 border-b border-[#e5e5e5] flex gap-1">
                        <select id="fee-studio-state" class="w-full text-[10px] font-bold border border-[#e5e5e5] bg-white px-2 py-1 outline-none text-lowercase rounded-[20px]">
                            <option value="initial">état: initial</option>
                            <option value="hover">état: hover</option>
                            <option value="click">état: click</option>
                            <option value="scroll-trigger">état: scroll</option>
                        </select>
                    </div>
                    <div id="fee-studio-triggers" class="flex-1 overflow-y-auto p-2 space-y-1 no-scrollbar">
                        <!-- data-af-id items -->
                    </div>
                </aside>

                <!-- CENTRE: LABO PHOTO (IFRAME) -->
                <main class="flex-1 flex flex-col bg-white overflow-hidden relative">
                    <!-- Iframe Container (scrollable pour zoom > 1) -->
                    <div id="fee-studio-preview-wrapper" class="flex-1 bg-[#efefeb] overflow-auto flex items-center justify-center p-8">
                        <div id="fee-studio-preview-container" class="bg-white shadow-2xl relative border border-[#e5e5e5] rounded-[20px] overflow-hidden" style="width:100%;height:100%;">
                             <iframe id="fee-studio-iframe" class="w-full h-full border-none" style="transform-origin:center center;transition:transform 0.15s ease;"></iframe>
                        </div>
                    </div>

                    <!-- Controls Bar -->
                    <div class="h-[48px] border-t border-[#e5e5e5] bg-white flex items-center justify-between px-4 shrink-0">
                        <!-- Zoom Controls -->
                        <div class="flex items-center gap-2">
                            <button id="fee-studio-btn-zoom-out" class="w-7 h-7 rounded-full border border-[#e5e5e5] flex items-center justify-center text-[#9a9a98] hover:border-[#8cc63f] hover:text-[#8cc63f] transition-all" title="Zoom Out">
                                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"/></svg>
                            </button>
                            <span id="fee-studio-zoom-level" class="text-[10px] font-bold text-[#9a9a98] w-10 text-center tabular-nums">100%</span>
                            <button id="fee-studio-btn-zoom-in" class="w-7 h-7 rounded-full border border-[#e5e5e5] flex items-center justify-center text-[#9a9a98] hover:border-[#8cc63f] hover:text-[#8cc63f] transition-all" title="Zoom In">
                                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                            </button>
                        </div>
                        <!-- Playback Controls -->
                        <div class="flex items-center gap-4">
                            <button id="fee-studio-btn-rewind" class="p-2 text-[#9a9a98] hover:text-[#8cc63f] transition-all rounded-[20px]" title="Rewind">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0019 16V8a1 1 0 00-1.6-.8l-5.334 4zM4.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0011 16V8a1 1 0 00-1.6-.8l-5.334 4z"/></svg>
                            </button>
                            <button id="fee-studio-btn-play" class="w-10 h-10 rounded-full bg-[#3d3d3c] text-white flex items-center justify-center hover:bg-black transition-all shadow-lg active:scale-95">
                                <svg class="w-4 h-4 fill-current ml-0.5" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                            </button>
                            <button id="fee-studio-btn-slow" class="px-3 py-1 border border-[#e5e5e5] text-[9px] font-black uppercase tracking-widest text-[#9a9a98] hover:border-[#8cc63f] hover:text-[#8cc63f] transition-all rounded-[20px]" title="Slow Motion x0.25">
                                ×0.25
                            </button>
                        </div>
                        <!-- Download -->
                        <button id="fee-studio-btn-download" class="px-3 py-1.5 border border-[#e5e5e5] text-[9px] font-bold uppercase tracking-wider text-[#9a9a98] hover:border-[#8cc63f] hover:text-[#8cc63f] transition-all rounded-[20px]" title="Télécharger le projet">
                            <svg class="w-3.5 h-3.5 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
                            télécharger
                        </button>
                    </div>
                </main>

                <!-- DROITE: SULLIVAN FEE -->
                <aside class="w-[320px] flex flex-col bg-[#f7f6f2] shrink-0">
                    <div class="p-3 border-b border-[#e5e5e5] flex items-center justify-between bg-white">
                        <span class="text-[9px] font-black uppercase tracking-widest">sullivan fee <span class="text-[#8cc63f]">worker</span></span>
                        <div id="fee-studio-status" class="w-2 h-2 rounded-full bg-[#ccc]"></div>
                    </div>
                    <!-- Chat History -->
                    <div id="fee-studio-chat" class="flex-1 overflow-y-auto p-4 space-y-4 no-scrollbar text-[11px] leading-relaxed">
                        <div class="p-3 bg-white border border-[#e5e5e5] font-serif italic text-[#9a9a98] rounded-[20px]">
                            Bonjour. Je suis prêt à étalonner l'interactivité. Sélectionnez un trigger à gauche pour commencer.
                        </div>
                    </div>
                    <!-- Input Area -->
                    <div class="p-3 border-t border-[#e5e5e5] bg-white">
                        <textarea id="fee-studio-input" placeholder="Décrivez l'émotion visuelle..." class="w-full bg-[#f7f6f2] border border-[#e5e5e5] p-3 text-[12px] outline-none focus:border-[#8cc63f] h-20 resize-none rounded-[20px]"></textarea>
                        <div class="flex items-center justify-between mt-2">
                             <button id="fee-studio-btn-apply" class="px-3 py-1.5 bg-[#8cc63f] text-white text-[9px] font-black uppercase tracking-widest hidden rounded-[20px]">appliquer le code</button>
                             <button id="fee-studio-btn-send" class="ml-auto w-8 h-8 bg-[#3d3d3c] text-white flex items-center justify-center hover:bg-black transition-all rounded-[20px]">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                             </button>
                        </div>
                    </div>
                </aside>
            </div>

            <!-- BAS: PELLICULE D'EFFETS -->
            <footer class="h-[100px] border-t border-[#e5e5e5] bg-[#f7f6f2] overflow-hidden flex items-center shrink-0">
                <div class="px-4 border-r border-[#e5e5e5] h-full flex flex-col justify-center gap-1 shrink-0">
                    <span class="text-[8px] font-black uppercase tracking-tighter text-[#9a9a98]">pellicule</span>
                    <span class="text-[10px] font-bold">effets gsap</span>
                </div>
                <div id="fee-studio-presets" class="flex-1 flex gap-4 overflow-x-auto p-4 no-scrollbar items-center">
                    <!-- Preset cards -->
                </div>
            </footer>
        `;

        document.body.appendChild(overlay);
        this.setupEventListeners();
    }

    setupEventListeners() {
        const btnClose = document.getElementById('fee-studio-btn-close');
        btnClose.onclick = () => this.close();

        const btnSend = document.getElementById('fee-studio-btn-send');
        btnSend.onclick = () => this.sendToSullivan();

        const input = document.getElementById('fee-studio-input');
        input.onkeydown = (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendToSullivan();
            }
        };

        const btnSlow = document.getElementById('fee-studio-btn-slow');
        btnSlow.onclick = () => this.setSlowMo();

        const btnPlay = document.getElementById('fee-studio-btn-play');
        btnPlay.onclick = () => this.controlPlay();

        const btnRewind = document.getElementById('fee-studio-btn-rewind');
        btnRewind.onclick = () => this.controlRewind();

        const stateSelect = document.getElementById('fee-studio-state');
        stateSelect.onchange = (e) => { this.selectedState = e.target.value; };

        const btnApply = document.getElementById('fee-studio-btn-apply');
        btnApply.onclick = () => this.applyCode();

        // M273: Zoom controls
        const btnZoomIn = document.getElementById('fee-studio-btn-zoom-in');
        const btnZoomOut = document.getElementById('fee-studio-btn-zoom-out');
        if (btnZoomIn) btnZoomIn.onclick = () => this.setZoom(this.previewScale + 0.25);
        if (btnZoomOut) btnZoomOut.onclick = () => this.setZoom(this.previewScale - 0.25);

        // Wheel zoom (Ctrl/Cmd + wheel)
        const wrapper = document.getElementById('fee-studio-preview-wrapper');
        if (wrapper) {
            wrapper.addEventListener('wheel', (e) => {
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    const delta = e.deltaY > 0 ? -0.1 : 0.1;
                    this.setZoom(this.previewScale + delta);
                }
            }, { passive: false });
        }

        // M273: Download button
        const btnDownload = document.getElementById('fee-studio-btn-download');
        if (btnDownload) btnDownload.onclick = () => this.downloadProject();
    }

    // M273: Zoom logic
    setZoom(scale) {
        this.previewScale = Math.max(this.previewMinScale, Math.min(this.previewMaxScale, scale));
        const iframe = document.getElementById('fee-studio-iframe');
        const container = document.getElementById('fee-studio-preview-container');
        const levelEl = document.getElementById('fee-studio-zoom-level');
        if (iframe) iframe.style.transform = `scale(${this.previewScale})`;
        if (container) {
            container.style.width = `${100 / this.previewScale}%`;
            container.style.height = `${100 / this.previewScale}%`;
        }
        if (levelEl) levelEl.textContent = `${Math.round(this.previewScale * 100)}%`;
    }

    async open() {
        this.injectUI();

        // M240: Resolve projectId from session, not wsBackend
        const session = JSON.parse(localStorage.getItem('homeos_session') || '{}');
        this.projectId = session.active_project_id || session.project_id || null;

        // M260: Resolve activeScreen from canvas-selected shell
        const activeShellId = window.wsCanvas?.activeScreenId;
        let resolvedScreen = 'landing.html';
        if (activeShellId && activeShellId.startsWith('shell-')) {
            const importId = activeShellId.slice(6); // strip 'shell-'
            const items = window.WsImportList?._items || [];
            const activeItem = items.find(i => i.id === importId);
            resolvedScreen = activeItem?.html_template || activeItem?.file_path || 'landing.html';
        }
        this.activeScreen = resolvedScreen;

        if (!this.projectId) {
            console.warn('[FEEStudio] Aucun projet actif dans la session');
            alert("veuillez activer un projet");
            return;
        }

        if (this.activeScreen === 'landing.html') {
            console.warn('[FEEStudio] Aucun écran sélection sur le canvas');
        }

        document.getElementById('fee-studio-project-label').innerText = `projet: ${this.projectId}`;
        document.getElementById('fee-studio-overlay').classList.remove('hidden');
        this.isOpen = true;

        const iframe = document.getElementById('fee-studio-iframe');
        iframe.src = `/api/bkd/fee/preview?project_id=${this.projectId}&path=${this.activeScreen}`;
        
        iframe.onload = () => {
             this.scanTriggers();
        };

        this.loadPresets();
    }

    close() {
        document.getElementById('fee-studio-overlay').classList.add('hidden');
        this.isOpen = false;
        // Reset toggle mode UI if present
        const modesContainer = document.querySelector('.flex.bg-slate-100.p-1.rounded-custom');
        if (modesContainer) {
            const constructBtn = modesContainer.querySelector('[data-mode="construct"]');
            if (constructBtn) constructBtn.click();
        }
    }

    async scanTriggers() {
        const iframe = document.getElementById('fee-studio-iframe');
        try {
            const doc = iframe.contentDocument || iframe.contentWindow.document;
            const elements = doc.querySelectorAll('[data-af-id]');
            const container = document.getElementById('fee-studio-triggers');
            container.innerHTML = '';

            // Fetch coverage (logic.js content)
            let coverage = "";
            try {
                const res = await fetch(`/api/bkd/fee/logic?project_id=${this.projectId}&screen=${this.activeScreen}`);
                const data = await res.json();
                coverage = data.code || "";
            } catch(e) { console.warn("Coverage fetch failed", e); }

            elements.forEach(el => {
                const id = el.getAttribute('data-af-id');
                const tag = el.tagName.toLowerCase();
                const hasAnimation = coverage.includes(`[data-af-id="${id}"]`) || coverage.includes(`data-af-id="${id}"`);
                
                const item = document.createElement('button');
                item.className = "w-full text-left p-2 border border-[#e5e5e5] bg-white hover:border-[#8cc63f] transition-all flex items-center justify-between group rounded-[20px]";
                item.innerHTML = `
                    <div class="flex items-center gap-2">
                        <div class="w-1.5 h-1.5 rounded-full ${hasAnimation ? 'bg-[#8cc63f] shadow-[0_0_8px_rgba(140,198,63,0.6)]' : 'bg-[#efefef]'}" data-led-id="${id}"></div>
                        <span class="text-[11px] font-bold">${id}</span>
                    </div>
                    <span class="text-[8px] opacity-30 uppercase font-black">${tag}</span>
                `;
                item.onclick = () => this.selectTrigger(id);
                container.appendChild(item);
            });
        } catch (e) { console.error("Scan triggers failed", e); }
    }

    selectTrigger(id) {
        this.selectedTrigger = id;
        document.querySelectorAll('#fee-studio-triggers button').forEach(b => b.classList.remove('border-[#8cc63f]'));
        const btn = Array.from(document.querySelectorAll('#fee-studio-triggers button')).find(b => b.innerText.includes(id));
        if (btn) btn.classList.add('border-[#8cc63f]');
        
        const input = document.getElementById('fee-studio-input');
        input.value = `Anime l'élement [${id}] pour que... `;
        input.focus();
    }

    async loadPresets() {
        try {
            const res = await fetch('/api/bkd/fee/presets');
            const data = await res.json();
            const container = document.getElementById('fee-studio-presets');
            container.innerHTML = '';

            data.presets.forEach(p => {
                const card = document.createElement('button');
                card.className = "shrink-0 w-24 h-full border border-[#e5e5e5] bg-white flex flex-col p-2 hover:border-[#8cc63f] transition-all group rounded-[20px] overflow-hidden";
                card.innerHTML = `
                    <div class="flex-1 bg-[#f7f6f2] flex items-center justify-center mb-1 group-hover:bg-[#8cc63f]/10 rounded-[12px]">
                        <svg class="w-6 h-6 text-[#ccc] group-hover:text-[#8cc63f]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                    </div>
                    <span class="text-[8px] font-black uppercase text-center truncate">${p.name}</span>
                `;
                card.onclick = () => {
                    document.getElementById('fee-studio-input').value = p.prompt;
                    this.sendToSullivan(p.prompt);
                };
                container.appendChild(card);
            });
        } catch (e) { console.error("Presets failed", e); }
    }

    async sendToSullivan(customMsg = null) {
        if (this.isGenerating) return;
        const msg = customMsg || document.getElementById('fee-studio-input').value.trim();
        if (!msg) return;

        if (!customMsg) document.getElementById('fee-studio-input').value = '';
        
        this.addChatMessage('user', msg);
        this.isGenerating = true;
        document.getElementById('fee-studio-status').classList.remove('bg-[#ccc]');
        document.getElementById('fee-studio-status').classList.add('bg-[#8cc63f]', 'animate-pulse');

        try {
            const res = await fetch('/api/bkd/fee/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    message: msg,
                    trigger: this.selectedTrigger,
                    state: this.selectedState,
                    history: this.feeHistory,
                    project_id: this.projectId,
                    screen: this.activeScreen
                })
            });
            const data = await res.json();
            this.addChatMessage('assistant', data.explanation);
            
            // Extract code and hot-reload
            const match = data.explanation.match(/```(?:javascript|js)?([\s\S]*?)```/);
            if (match && match[1]) {
                this.lastGeneratedCode = match[1].trim();
                this.previewCode(this.lastGeneratedCode);
                document.getElementById('fee-studio-btn-apply').classList.remove('hidden');
            }
        } catch (e) {
            this.addChatMessage('assistant', "Erreur de communication avec le studio.");
        } finally {
            this.isGenerating = false;
            document.getElementById('fee-studio-status').classList.remove('animate-pulse');
        }
    }

    addChatMessage(role, text) {
        const chat = document.getElementById('fee-studio-chat');
        const div = document.createElement('div');
        div.className = `p-3 border ${role === 'user' ? 'bg-white border-[#e5e5e5] ml-4' : 'bg-[#efefeb] border-[#e5e5e5] mr-4'} rounded-[20px]`;
        div.innerHTML = `<div class="text-[11px]">${text}</div>`;
        chat.appendChild(div);
        chat.scrollTop = chat.scrollHeight;
        this.feeHistory.push({role, text});
    }

    previewCode(code) {
        const iframe = document.getElementById('fee-studio-iframe');
        iframe.contentWindow.postMessage({
            type: 'FEE_INJECT_GSAP',
            code: code,
            screen: this.activeScreen
        }, '*');
    }

    setSlowMo() {
        const iframe = document.getElementById('fee-studio-iframe');
        iframe.contentWindow.postMessage({ type: 'FEE_GSAP_CONTROL', action: 'timeScale', value: 0.25 }, '*');
    }

    controlPlay() {
        const iframe = document.getElementById('fee-studio-iframe');
        iframe.contentWindow.postMessage({ type: 'FEE_GSAP_CONTROL', action: 'play' }, '*');
    }

    controlRewind() {
        const iframe = document.getElementById('fee-studio-iframe');
        iframe.contentWindow.postMessage({ type: 'FEE_GSAP_CONTROL', action: 'restart' }, '*');
    }

    // M273: Download project as ZIP
    async downloadProject() {
        try {
            const iframe = document.getElementById('fee-studio-iframe');
            const html = iframe.contentDocument?.documentElement?.outerHTML;
            if (!html) {
                alert("Aucun contenu à télécharger — chargez d'abord un écran.");
                return;
            }

            // Create blob and download
            const blob = new Blob([html], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${this.activeScreen || 'fee-screen'}.html`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch(e) {
            alert("Erreur téléchargement: " + e.message);
        }
    }

    async applyCode() {
        if (!this.lastGeneratedCode) return;
        try {
            await fetch('/api/bkd/fee/apply', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    project_id: this.projectId,
                    screen: this.activeScreen,
                    code: this.lastGeneratedCode,
                    trigger: this.selectedTrigger
                })
            });
            alert("Code appliqué dans logic.js");
            document.getElementById('fee-studio-btn-apply').classList.add('hidden');
        } catch (e) { alert("Erreur d'application."); }
    }
}

window.WsFEEStudio = WsFEEStudio;
