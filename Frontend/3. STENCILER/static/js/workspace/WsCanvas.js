class WsCanvas {
    constructor(svgId, wrapperId) {
        this.svg = document.getElementById(svgId);
        this.wrapper = document.getElementById(wrapperId);
        this.content = document.getElementById('canvas-content');
        
        // State
        this.scale = 1.0;
        this.viewX = 0;
        this.viewY = 0;
        this.activeMode = 'select'; // 'select', 'drag', 'place-img', 'frame'
        
        // Interaction
        this.isPanning = false;
        this.isSpacePressed = false;
        this.startX = 0;
        this.startY = 0;
        
        // Draggable screens
        this.selectedScreen = null;
        this.activeScreenId = null; // ID for highlighting
        this.offsetDragX = 0;
        this.offsetDragY = 0;

        this.init();
    }

    init() {
        // --- ZOOM (Wheel) ---
        this.wrapper.addEventListener('wheel', (e) => this.handleWheel(e), { passive: false });

        // --- MOUSE EVENTS ---
        this.wrapper.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        this.wrapper.addEventListener('dblclick', (e) => this.handleDoubleClick(e));
        window.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        window.addEventListener('mouseup', () => this.handleMouseUp());

        // --- KEYBOARD SHORTCUTS ---
        window.addEventListener('keydown', (e) => { 
            if (e.code === 'Space') this.isSpacePressed = true; 
            if (document.activeElement.tagName === 'TEXTAREA' || document.activeElement.tagName === 'INPUT') return;
            
            const modeMap = { 'KeyV': 'select', 'KeyH': 'drag', 'KeyI': 'place-img', 'KeyF': 'frame' };
            if (modeMap[e.code]) this.setMode(modeMap[e.code]);
            if (e.code === 'Digit0') this.resetView();
        });
        window.addEventListener('keyup', (e) => { if (e.code === 'Space') this.isSpacePressed = false; });

        // --- TOOLBAR BUTTONS ---
        document.querySelectorAll('.ws-tool-btn').forEach(btn => {
            btn.onclick = () => this.setMode(btn.dataset.mode);
        });

        this.updateTransform();
    }

    setMode(mode) {
        this.activeMode = mode;
        console.log("🛠 WsCanvas: Mode switched to", mode);
        
        // Update UI
        document.querySelectorAll('.ws-tool-btn').forEach(btn => {
            if (btn.dataset.mode === mode) btn.classList.add('active-tool');
            else btn.classList.remove('active-tool');
        });

        // Update cursor
        if (mode === 'drag') this.svg.style.cursor = 'grab';
        else this.svg.style.cursor = 'default';
    }

    updateTransform() {
        this.content.setAttribute('transform', `matrix(${this.scale} 0 0 ${this.scale} ${this.viewX} ${this.viewY})`);
        const zoomText = document.getElementById('zoom-level');
        if (zoomText) zoomText.innerText = Math.round(this.scale * 100) + '%';
    }

    handleWheel(e) {
        // Guard: si on scrolle dans un panneau UI (panels, chat, toolbar…), ne pas zoomer
        if (e.target.closest('#ws-left-panels, #ws-chat-history, .glass-card')) {
            return; // Laisser le scroll natif se faire normalement
        }

        e.preventDefault();
        const zoomFactor = 1.1;
        const oldScale = this.scale;
        
        if (e.deltaY < 0) this.scale *= zoomFactor;
        else this.scale /= zoomFactor;
        
        this.scale = Math.min(Math.max(0.05, this.scale), 8);

        const rect = this.svg.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        const worldX = (mouseX - this.viewX) / oldScale;
        const worldY = (mouseY - this.viewY) / oldScale;

        this.viewX = mouseX - worldX * this.scale;
        this.viewY = mouseY - worldY * this.scale;

        this.updateTransform();
    }

    handleMouseDown(e) {
        // PAN case (Space or specific Tool)
        if (this.isSpacePressed || e.button === 1 || this.activeMode === 'drag') {
            this.isPanning = true;
            this.startX = e.clientX - this.viewX;
            this.startY = e.clientY - this.viewY;
            if (this.activeMode === 'drag') this.svg.style.cursor = 'grabbing';
            return;
        }

        // SELECT case
        const shell = e.target.closest('.ws-screen-shell');

        if (shell) {
            this.selectScreen(shell);

            if (this.activeMode === 'select') {
                const rect = this.svg.getBoundingClientRect();
                const vals = (shell.getAttribute('transform') || 'matrix(1 0 0 1 0 0)')
                    .match(/matrix\(([^)]+)\)/)?.[1].trim().split(/[\s,]+/).map(Number) || [1,0,0,1,0,0];
                // Detect header zone by Y position (top 40px in world coords)
                const worldY = (e.clientY - rect.top - this.viewY) / this.scale - vals[5];
                if (worldY >= 0 && worldY <= 40) {
                    this.selectedScreen = shell;
                    this.offsetDragX = (e.clientX - rect.left - this.viewX) / this.scale - vals[4];
                    this.offsetDragY = (e.clientY - rect.top - this.viewY) / this.scale - vals[5];
                    this.content.appendChild(shell); // Bring to front
                }
            }
        } else {
            // Clicked on background: deselect
            this.deselectAll();
        }
    }

    handleDoubleClick(e) {
        const shell = e.target.closest('.ws-screen-shell');
        if (shell) {
            // Drill down zoom
            const rect = this.svg.getBoundingClientRect();
            const vals = (shell.getAttribute('transform') || 'matrix(1 0 0 1 0 0)')
                .match(/matrix\(([^)]+)\)/)?.[1].trim().split(/[\s,]+/).map(Number) || [1,0,0,1,0,0];
            
            const targetX = vals[4];
            const targetY = vals[5];
            
            // Aim for 1.5 scale
            this.scale = 1.2;
            this.viewX = rect.width/2 - (targetX + 200) * this.scale;
            this.viewY = rect.height/2 - (targetY + 300) * this.scale;
            this.updateTransform();
        }
    }

    handleMouseMove(e) {
        if (this.isPanning) {
            this.viewX = e.clientX - this.startX;
            this.viewY = e.clientY - this.startY;
            this.updateTransform();
            return;
        }

        if (this.selectedScreen) {
            const rect = this.svg.getBoundingClientRect();
            const x = (e.clientX - rect.left - this.viewX) / this.scale - this.offsetDragX;
            const y = (e.clientY - rect.top - this.viewY) / this.scale - this.offsetDragY;
            this.selectedScreen.setAttribute('transform', `matrix(1 0 0 1 ${x} ${y})`);
        }
    }

    handleMouseUp() {
        this.isPanning = false;
        this.selectedScreen = null;
        if (this.activeMode === 'drag') this.svg.style.cursor = 'grab';
    }

    selectScreen(shell) {
        this.deselectAll();
        shell.classList.add('active');
        const bg = shell.querySelector('.ws-screen-bg');
        if (bg) bg.setAttribute('stroke', '#A3CD54');
        if (bg) bg.setAttribute('stroke-width', '2');
        this.activeScreenId = shell.getAttribute('id');
        
        // Update Audit UX panel (mockup trigger)
        const auditContent = document.getElementById('ws-audit-content');
        if (auditContent) {
            const title = shell.querySelector('.ws-screen-title').textContent;
            auditContent.innerHTML = `
                <div class="flex items-center gap-2 mb-4">
                    <span class="text-[10px] font-bold text-homeos-green uppercase">Screen active</span>
                    <span class="text-[11px] text-slate-800 font-bold">${title}</span>
                </div>
                <div class="space-y-3">
                    <div class="p-3 bg-slate-50 border border-slate-100 rounded-lg">
                        <div class="text-[9px] font-bold text-slate-400 uppercase mb-1">Intent detection</div>
                        <div class="text-[11px] text-slate-600">Interface d'édition détectée. Structure sémantique valide.</div>
                    </div>
                </div>
            `;
        }
    }

    deselectAll() {
        document.querySelectorAll('.ws-screen-shell').forEach(s => {
            s.classList.remove('active');
            const bg = s.querySelector('.ws-screen-bg');
            if (bg) bg.setAttribute('stroke', '#f0f0f0');
            if (bg) bg.setAttribute('stroke-width', '1');
        });
        this.activeScreenId = null;
    }

    getActiveScreenHtml() {
        if (!this.activeScreenId) return null;
        const shell = document.getElementById(this.activeScreenId);
        if (!shell) return null;
        
        const iframe = shell.querySelector('iframe');
        if (!iframe) return null;
        
        return {
            src: iframe.src,
            srcdoc: iframe.srcdoc,
            name: shell.querySelector('.ws-screen-title')?.textContent || 'Untitled'
        };
    }

    resetView() {
        this.scale = 1.0;
        this.viewX = 0;
        this.viewY = 0;
        this.updateTransform();
    }

    setZoom(val) {
        this.scale = val;
        this.updateTransform();
    }

    async addScreen(item) {
        const id = `shell-${item.id}`;
        if (document.getElementById(id)) {
            const existing = document.getElementById(id);
            this.selectScreen(existing);
            return;
        }

        const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
        g.setAttribute('id', id);
        g.setAttribute('class', 'ws-screen-shell');
        
        // Dimensions : desktop (HTML direct uploadé) vs mobile (SVG/forged)
        const isHtml = item.type === 'html' || (item.html_template && item.elements_count === 0);
        const SW = isHtml ? 1200 : 400;
        const SH = isHtml ? 800 : 632;

        // Positioning
        const rect = this.svg.getBoundingClientRect();
        const centerX = (rect.width/2 - SW/2 - this.viewX) / this.scale;
        const centerY = (rect.height/2 - SH/2 - this.viewY) / this.scale;
        g.setAttribute('transform', `matrix(1 0 0 1 ${centerX} ${centerY})`);

        // Main Shell Background
        const bg = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        bg.setAttribute('width', String(SW));
        bg.setAttribute('height', String(SH));
        bg.setAttribute('rx', '20');
        bg.setAttribute('fill', '#fff');
        bg.setAttribute('stroke', '#f0f0f0');
        bg.setAttribute('stroke-width', '1');
        bg.setAttribute('class', 'ws-screen-bg');
        
        // Header
        const header = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        header.setAttribute('width', String(SW));
        header.setAttribute('height', '40');
        header.setAttribute('rx', '20');
        header.setAttribute('class', 'ws-screen-header');
        header.setAttribute('fill', 'transparent');
        header.setAttribute('pointer-events', 'all');
        
        // Title
        const title = document.createElementNS("http://www.w3.org/2000/svg", "text");
        title.setAttribute('x', '20');
        title.setAttribute('y', '25');
        title.setAttribute('class', 'ws-screen-title');
        title.textContent = (item.name || 'Sans titre').toLowerCase();

        // Close btn (✕)
        const closeBtn = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        closeBtn.setAttribute('cx', String(SW - 25));
        closeBtn.setAttribute('cy', '20');
        closeBtn.setAttribute('r', '8');
        closeBtn.setAttribute('class', 'ws-btn-close');
        closeBtn.setAttribute('pointer-events', 'all');
        closeBtn.addEventListener('mousedown', (e) => {
            e.stopPropagation();
            g.remove();
        });

        // iFrame Container
        const fo = document.createElementNS("http://www.w3.org/2000/svg", "foreignObject");
        fo.setAttribute('x', '0');
        fo.setAttribute('y', '40');
        fo.setAttribute('width', String(SW));
        fo.setAttribute('height', String(SH - 40));
        fo.setAttribute('pointer-events', 'none');
        
        const iframe = document.createElement('iframe');
        iframe.style.width = '100%';
        iframe.style.height = '100%';
        iframe.style.border = 'none';
        iframe.style.borderRadius = '0 0 20px 20px';
        iframe.style.background = '#fff';
        iframe.style.pointerEvents = 'none'; // Avoid iframe stealing mouse events for drag
        
        if (item.html_template) {
            iframe.src = `/api/frd/file?name=${encodeURIComponent(item.html_template)}&raw=1`;
        }

        fo.appendChild(iframe);

        // Preview btn (Mission 130-B — Moved down to y=50 to avoid drag conflict)
        const previewFo = document.createElementNS("http://www.w3.org/2000/svg", "foreignObject");
        previewFo.setAttribute('x', String(SW - 180));
        previewFo.setAttribute('y', '50');
        previewFo.setAttribute('width', '100');
        previewFo.setAttribute('height', '30');
        previewFo.setAttribute('pointer-events', 'all');
        const previewDiv = document.createElement('div');
        previewDiv.className = "flex items-center space-x-2 text-slate-500 cursor-pointer hover:text-slate-800 transition-colors";
        previewDiv.style.cssText = 'height:100%; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));';
        previewDiv.innerHTML = `
            <span style="font-size:10px; font-weight:500; background:rgba(255,255,255,0.8); padding:2px 4px; border-radius:4px;">Aperçu</span>
            <svg fill="none" height="14" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24" width="14" xmlns="http://www.w3.org/2000/svg">
                <path d="M15 3h6v6"></path><path d="M9 21H3v-6"></path><path d="M21 3l-7 7"></path><path d="M3 21l7-7"></path>
            </svg>
        `;
        previewDiv.addEventListener('mousedown', (e) => {
            console.log("🖱 [WsCanvas] Mousedown on Preview button");
            e.stopPropagation();
        });
        previewDiv.addEventListener('click', (e) => {
            console.log("🖱 [WsCanvas] Click on Preview button");
            e.stopPropagation();
            this.selectScreen(g);
            if (window.enterPreviewMode) window.enterPreviewMode(id);
        });
        previewFo.appendChild(previewDiv);

        // Save btn (Mission 130-B — Moved down to y=52 to avoid drag conflict)
        const saveFo = document.createElementNS("http://www.w3.org/2000/svg", "foreignObject");
        saveFo.setAttribute('x', String(SW - 90));
        saveFo.setAttribute('y', '52');
        saveFo.setAttribute('width', '60');
        saveFo.setAttribute('height', '26');
        saveFo.setAttribute('pointer-events', 'all');
        const saveBtn = document.createElement('button');
        saveBtn.className = "bg-homeos-green text-white px-3 py-1 rounded-custom font-semibold text-[10px] uppercase tracking-wider shadow-md hover:opacity-90 transition-all";
        saveBtn.style.cssText = "width:100%; height:100%; line-height:1;";
        saveBtn.innerText = "SAVE";
        saveBtn.addEventListener('mousedown', (e) => {
            console.log("🖱 [WsCanvas] Mousedown on Save button");
            e.stopPropagation();
        });
        saveBtn.addEventListener('click', async (e) => {
            console.log("🖱 [WsCanvas] Click on Save button");
            e.stopPropagation();
            saveBtn.style.opacity = '0.5';
            try {
                const iframeEl = g.querySelector('iframe');
                const srcUrl = iframeEl ? iframeEl.src : null;
                console.log("💾 [WsCanvas] Saving screen contents for", item.html_template);
                await fetch('/api/frd/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        name: item.html_template || item.name, 
                        url: srcUrl,
                        screenId: item.id 
                    })
                });
                console.log("✅ [WsCanvas] Saved successfully");
            } catch (err) {
                console.error("❌ [WsCanvas] Save failed", err);
            }
            saveBtn.style.opacity = '1';
        });
        saveFo.appendChild(saveBtn);

        g.appendChild(bg);
        g.appendChild(header);
        g.appendChild(title);
        g.appendChild(previewFo);
        g.appendChild(saveFo);
        g.appendChild(closeBtn);
        g.appendChild(fo);

        // Overlay forge — DOM createElement (innerHTML sur foreignObject = non fiable)
        if (!item.html_template) {
            const forgeOverlay = document.createElementNS("http://www.w3.org/2000/svg", "foreignObject");
            forgeOverlay.setAttribute('x', '100');
            forgeOverlay.setAttribute('y', '260');
            forgeOverlay.setAttribute('width', '200');
            forgeOverlay.setAttribute('height', '80');
            forgeOverlay.setAttribute('class', 'ws-forge-overlay');

            const wrap = document.createElement('div');
            wrap.style.cssText = 'text-align:center;font-family:"Source Sans 3",sans-serif;';

            const nameLabel = document.createElement('div');
            nameLabel.style.cssText = 'font-size:10px;color:#94a3b8;margin-bottom:10px;';
            nameLabel.textContent = (item.name || '').toLowerCase();

            const forgeBtn = document.createElement('button');
            forgeBtn.id = `forge-btn-${item.id}`;
            forgeBtn.style.cssText = 'background:#A3CD54;color:#fff;border:none;border-radius:20px;padding:8px 20px;font-size:11px;cursor:pointer;text-transform:lowercase;';
            forgeBtn.textContent = 'forger le rendu';

            const statusEl = document.createElement('div');
            statusEl.id = `forge-status-${item.id}`;
            statusEl.style.cssText = 'font-size:9px;color:#94a3b8;margin-top:6px;';

            wrap.appendChild(nameLabel);
            wrap.appendChild(forgeBtn);
            wrap.appendChild(statusEl);
            forgeOverlay.appendChild(wrap);

            // Listener direct sur le bouton HTML — contourne la frontière SVG/HTML
            forgeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.forgeScreen(item.id, g, forgeOverlay);
            });

            g.appendChild(forgeOverlay);
        }

        this.content.appendChild(g);
        this.selectScreen(g);
    }

    async forgeScreen(importId, shell, overlay) {
        const btn = overlay.querySelector(`#forge-btn-${importId}`);
        const statusEl = overlay.querySelector(`#forge-status-${importId}`);
        if (btn) { btn.disabled = true; btn.textContent = 'forge en cours...'; }
        if (statusEl) statusEl.textContent = 'analyse sémantique...';

        const chat = window.wsChat;
        const say = (msg) => { if (chat) chat.appendBubble(msg, 'sullivan'); };

        say('forge démarrée — analyse sémantique en cours...');

        try {
            const res = await fetch('/api/retro-genome/generate-from-import', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ import_id: importId })
            });
            if (!res.ok) throw new Error(`${res.status}`);
            const { job_id: jobId } = await res.json();

            say('génération tailwind en cours...');
            let pollCount = 0;
            const MESSAGES = ['structuration du layout...', 'composants en cours...', 'presque terminé...'];

            const poll = setInterval(async () => {
                try {
                    const jr = await fetch(`/api/retro-genome/svg-job/${jobId}`);
                    const job = await jr.json();
                    if (job.status === 'done') {
                        clearInterval(poll);
                        overlay.remove();
                        const iframe = shell.querySelector('iframe');
                        if (iframe) iframe.src = `/api/frd/file?name=${encodeURIComponent(job.template_name)}&raw=1`;
                        say('✓ rendu forgé et chargé.');
                        if (statusEl) statusEl.textContent = '';
                    } else if (job.status === 'failed') {
                        clearInterval(poll);
                        if (statusEl) statusEl.textContent = `échec : ${job.error}`;
                        if (btn) { btn.disabled = false; btn.textContent = 'réessayer'; }
                        say(`forge échouée : ${job.error}`);
                    } else {
                        pollCount++;
                        const msg = MESSAGES[Math.min(pollCount - 1, MESSAGES.length - 1)];
                        if (statusEl) statusEl.textContent = msg;
                        if (pollCount <= MESSAGES.length) say(msg);
                    }
                } catch(_) { clearInterval(poll); }
            }, 4000);

        } catch(err) {
            if (btn) { btn.disabled = false; btn.textContent = 'réessayer'; }
            if (statusEl) statusEl.textContent = `erreur : ${err.message}`;
            say(`erreur forge : ${err.message}`);
        }
    }
}
