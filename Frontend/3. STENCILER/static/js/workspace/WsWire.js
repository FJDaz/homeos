/**
 * WsWire.js — AetherFlow Wireframe Management (Mission 147)
 * Handles the mapping overlay and validation UI.
 */
class WsWire {
    constructor() {
        this.overlay = document.getElementById('ws-wire-overlay');
        this.tbody = document.getElementById('ws-wire-table-body');
        this.importLabel = document.getElementById('ws-wire-import-label');
        this.btnCadrage = document.getElementById('ws-wire-btn-cadrage');
        this.btnApplyPlan = document.getElementById('ws-wire-apply-plan');
        this.planContent = document.getElementById('ws-wire-plan-content');
        this.wireCanvas = document.getElementById('ws-wire-canvas');
        this.wireLines = document.getElementById('ws-wire-lines');
        this.wireDraft = document.getElementById('ws-wire-draft');
        this.eventTypeSelect = document.getElementById('ws-wire-event-type');

        this._manifest = null;
        this._triggerData = null; // { selector, rect, organName }
        this._isWiring = false;
        
        this.init();
    }

    init() {
        if (this.btnCadrage) {
            this.btnCadrage.onclick = () => this._openCadrage();
        }
        if (this.btnApplyPlan) {
            this.btnApplyPlan.onclick = async () => {
                if (!window.wsCanvas) return;
                const screen = window.wsCanvas.getActiveScreenHtml();
                if (!screen) {
                    alert("Aucun écran actif détecté pour le maillage.");
                    return;
                }
                
                // Fallback de lecture HTML
                if (!screen.srcdoc && screen.src) {
                    const shell = document.getElementById(window.wsCanvas.activeScreenId);
                    const iframe = shell?.querySelector('iframe');
                    try { screen.srcdoc = iframe?.contentDocument?.documentElement?.outerHTML || ''; } catch(_) {}
                }
                if (!screen.srcdoc) {
                    alert("Impossible de lire le contenu de l'écran.");
                    return;
                }

                this.btnApplyPlan.disabled = true;
                this.btnApplyPlan.innerText = "analyse du cadrage...";
                this.btnApplyPlan.classList.add('animate-pulse');

                try {
                    const projectRes = await fetch('/api/projects/active');
                    const project = await projectRes.json();

                    // --- MISSION 185 : PRE-WIRE CHECK ---
                    const preRes = await fetch(`/api/projects/${project.id}/pre-wire`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ screen_html: screen.srcdoc })
                    });
                    const preData = await preRes.json();

                    if (preData.bijection === 'total') {
                        // Maillage direct si tout est OK
                        this._executeForge(project.id, screen.srcdoc);
                    } else {
                        // Lancement du mode Liminaire
                        this._startLiminaire(project.id, preData.elements);
                    }
                } catch (err) {
                    console.error("[wswire] pre-wire fail", err);
                    this.btnApplyPlan.disabled = false;
                }
            };
        }

        // Clic en dehors du contenu → ferme l'overlay
        if (this.overlay) {
            this.overlay.addEventListener('click', (e) => {
                if (e.target === this.overlay) this.hide();
            });
        }

        // Mouse follow pour le draft wire
        window.addEventListener('mousemove', (e) => {
            if (this._isWiring && this.wireDraft) {
                this._updateDraftLine(e);
            }
        });

        // Écouter les clics de câblage venant de l'iframe
        window.addEventListener('message', (e) => {
            if (e.data.type === 'inspect-wire-picked') {
                this.handleWireClick(e.data);
            }
            if (e.data.type === 'ws-nudge-clicked') {
                this._handleNudgeClick(e.data);
            }
        });

        // Click outside & Escape key
        window.addEventListener('mousedown', (e) => {
            if (this.overlay && !this.overlay.classList.contains('hidden')) {
                // Si on a cliqué sur le background de l'overlay (et pas dans son contenu)
                if (e.target === this.overlay) {
                    this.hide();
                }
            }
        });
        window.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.overlay && !this.overlay.classList.contains('hidden')) {
                this.hide();
            }
        });
    }

    _openCadrage() {
        // Construire le contexte à partir du manifeste courant
        const params = new URLSearchParams();
        if (this._importId) params.set('import_id', this._importId);
        if (this._manifest) {
            const archetype = this._manifest.archetype?.label || '';
            const components = (this._manifest.components || [])
                .slice(0, 10)
                .map(c => `${c.name} (${c.role || '?'})`)
                .join(', ');
            const ctx = [
                archetype ? `Archétype détecté : ${archetype}.` : '',
                components ? `Composants : ${components}.` : '',
                `Import : ${this._importId || '?'}.`
            ].filter(Boolean).join(' ');
            params.set('context', ctx);
        }
        this.hide();
        if (window.exitPreviewMode) window.exitPreviewMode();
        window.open(`/cadrage?${params.toString()}`, '_blank');
    }

    async show(manifest, importName = "import") {
        console.log("[wswire] diagnostic WiRE lancé pour:", importName);
        if (!this.overlay) return;

        this._manifest = manifest;
        this.importLabel.innerText = importName;
        this.overlay.classList.remove('hidden');

        // Vue Diagnostic Initiale (HoméOS style)
        const container = this.overlay.querySelector('.relative.z-10');
        const mainArea = container.querySelector('.flex.gap-6');
        mainArea.innerHTML = `
            <div class="flex-1 flex flex-col items-center justify-center p-12 bg-[#f7f6f2] rounded-2xl border border-[#e5e5e5] h-[600px] animate-in fade-in duration-500">
                <div class="space-y-6 text-center">
                    <div class="flex items-center justify-center">
                        <div class="w-12 h-12 border-4 border-[#8cc63f]/20 border-t-[#8cc63f] rounded-full animate-spin"></div>
                    </div>
                    <div class="space-y-1">
                        <h3 class="text-[#3d3d3c] font-bold text-sm tracking-widest uppercase italic">Diagnostic WiRE</h3>
                        <p class="text-[#3d3d3c]/50 text-[10px] tracking-widest uppercase">Analyse des organes de l'iframe...</p>
                    </div>
                </div>
            </div>
        `;

        // Masquer le footer initial
        const footer = container.querySelector('.flex.items-center.gap-3.justify-end');
        if (footer) footer.classList.add('hidden');

        try {
            const projectRes = await fetch('/api/projects/active');
            const project = await projectRes.json();
            this._projectId = project.id;

            const screen = window.wsCanvas.getActiveScreenHtml();
            const shell = document.getElementById(window.wsCanvas?.activeScreenId);
            const iframe = shell?.querySelector('iframe');
            const screen_html = screen?.srcdoc || iframe?.contentDocument?.documentElement?.outerHTML || '';
            const preRes = await fetch(`/api/projects/${project.id}/pre-wire`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ screen_html })
            });
            const preData = await preRes.json();

            if (preData.elements && preData.elements.length > 0) {
                this._startLiminaire(project.id, preData.elements);
            } else {
                mainArea.innerHTML = `
                    <div class="flex-1 flex flex-col items-center justify-center p-12 bg-[#f7f6f2] rounded-2xl border border-[#e5e5e5] h-[600px]">
                        <p class="text-[#3d3d3c]/50 text-xs italic">Aucun élément interactif détecté sur cet écran.</p>
                        <button onclick="window.wsWire.hide()" class="mt-4 px-6 py-2 border border-[#e5e5e5] rounded-full text-[10px] font-bold uppercase tracking-widest">fermer</button>
                    </div>
                `;
            }
        } catch (err) {
            console.error("[wswire] diagnostic failed", err);
        }
    }

    _startLiminaire(projectId, elements) {
        this._projectId = projectId;
        this._infillingElements = elements;
        this._currentIndex = 0;
        this._validations = elements.map(el => ({ 
            ...el, confirmed: !el.matched, custom_intent: null 
        }));

        this._renderLiminaireUI();
    }

    _renderLiminaireUI() {
        const container = this.overlay.querySelector('.relative.z-10');
        const mainArea = container.querySelector('.flex.gap-6');
        
        const html = `
            <div class="flex-1 flex flex-col bg-[#f7f6f2] rounded-2xl border border-[#e5e5e5] h-[600px] overflow-hidden animate-in slide-in-from-bottom-4 duration-500">
                <div class="px-8 py-6 border-b border-[#e5e5e5] flex items-center justify-between bg-white/50">
                    <div class="space-y-1">
                        <h3 class="text-[#3d3d3c] font-bold text-xs tracking-widest uppercase">Cadrage Séquentiel</h3>
                        <p class="text-[#3d3d3c]/50 text-[9px] tracking-widest uppercase">Validation des intentions du manifeste</p>
                    </div>
                    <div class="flex gap-1.5">
                        ${this._infillingElements.map((_, i) => `
                            <div class="w-1.5 h-1.5 rounded-full transition-colors duration-300 ${i === this._currentIndex ? 'bg-[#8cc63f]' : (i < this._currentIndex ? 'bg-[#8cc63f]/30' : 'bg-[#e5e5e5]')}"></div>
                        `).join('')}
                    </div>
                </div>

                <div class="flex-1 overflow-y-auto p-8 space-y-2 scrollbar-hide" id="liminaire-table">
                    ${this._infillingElements.map((el, i) => this._renderRow(el, i)).join('')}
                </div>

                <div class="p-6 border-t border-[#e5e5e5] bg-white/30 flex items-center justify-between">
                    <p class="text-[10px] font-bold text-[#3d3d3c]/40 uppercase tracking-widest">sullivan attend votre arbitrage</p>
                    <div class="flex gap-3">
                        <button id="lim-btn-prev" class="px-6 py-2.5 text-[10px] font-bold text-[#3d3d3c]/50 hover:text-[#3d3d3c] disabled:opacity-0 transition-all uppercase tracking-widest" ${this._currentIndex === 0 ? 'disabled' : ''}>précédent</button>
                        ${this._currentIndex === this._infillingElements.length - 1 
                            ? `<button id="lim-btn-finish" class="px-8 py-2.5 bg-[#3d3d3c] text-white text-[10px] font-bold rounded-full hover:bg-black shadow-sm transition-all uppercase tracking-widest">forger le maillage</button>`
                            : `<button id="lim-btn-next" class="px-8 py-2.5 bg-[#8cc63f] text-white text-[10px] font-bold rounded-full hover:opacity-90 shadow-lg shadow-[#8cc63f]/10 transition-all uppercase tracking-widest">étape suivante</button>`
                        }
                    </div>
                </div>
            </div>
        `;

        mainArea.innerHTML = html;
        this._setupLiminaireHandlers(mainArea);
        this._highlightInIframe(this._infillingElements[this._currentIndex]);
        
        // Scroll to active row
        const activeRow = mainArea.querySelector(`[data-index="${this._currentIndex}"]`);
        if (activeRow) activeRow.scrollIntoView({ behavior: 'smooth', block: 'center' });

        // MISSION 186 : Sync Nudges
        this._syncNudgesToIframe(this._validations.map((v, i) => ({
            ...v,
            status: i === this._currentIndex ? 'pending' : (v.confirmed ? 'ok' : 'none')
        })));
    }

    _renderRow(el, i) {
        const isActive = i === this._currentIndex;
        const isDone = i < this._currentIndex;
        const val = this._validations[i];
        
        // Extraction de l'ID pour affichage (intelligibilité Mission 187)
        const displayId = el.selector.replace('#', '');

        return `
            <div data-index="${i}" class="group relative flex items-center gap-4 p-4 rounded-xl border transition-all duration-500 ${isActive ? 'bg-white border-[#8cc63f] shadow-md z-10 scale-[1.02]' : 'bg-transparent border-transparent opacity-40'}">
                <div class="w-8 h-8 flex items-center justify-center rounded-lg ${isDone ? 'bg-[#8cc63f]/10 text-[#8cc63f]' : 'bg-slate-100 text-slate-400'} font-mono text-[10px] font-bold">
                    ${isDone ? '✓' : i + 1}
                </div>
                
                <div class="flex-1 min-w-0 space-y-0.5">
                    <div class="flex items-center gap-2">
                        <span class="text-[10px] font-bold text-[#3d3d3c] font-mono truncate">#${displayId}</span>
                        <span class="px-1.5 py-0.5 bg-slate-100 text-slate-400 text-[8px] font-bold rounded uppercase tracking-tighter">${el.tag}</span>
                    </div>
                    <div class="text-[10px] text-[#3d3d3c]/50 italic truncate">"${el.text || 'sans texte'}"</div>
                </div>

                ${isActive ? `
                    <div class="flex items-center gap-2 animate-in fade-in slide-in-from-right-2 duration-300">
                        <div class="flex bg-slate-100 p-1 rounded-lg border border-slate-200">
                            <button class="lim-opt-yes px-3 py-1.5 text-[9px] font-bold uppercase tracking-widest rounded-md transition-all ${val.confirmed && !val.custom_intent ? 'bg-[#8cc63f] text-white' : 'hover:bg-white text-slate-400'}">oui</button>
                            <button class="lim-opt-no px-3 py-1.5 text-[9px] font-bold uppercase tracking-widest rounded-md transition-all ${!val.confirmed ? 'bg-slate-800 text-white' : 'hover:bg-white text-slate-400'}">non</button>
                            <button class="lim-opt-edit px-3 py-1.5 text-[9px] font-bold uppercase tracking-widest rounded-md transition-all ${val.custom_intent ? 'bg-amber-500 text-white' : 'hover:bg-white text-slate-400'}">autre</button>
                        </div>
                    </div>
                ` : `
                    <div class="text-[10px] font-mono text-[#8cc63f] font-bold">${val.confirmed ? (val.custom_intent || val.inferred_intent) : ''}</div>
                `}

                <!-- Barre de Preload Mission 187 -->
                <div class="lim-preload-bar absolute bottom-0 left-0 h-0.5 bg-[#8cc63f] transition-all duration-1000 ease-out" style="width: 0%"></div>
            </div>

            ${isActive && val.custom_intent !== null && val.custom_intent !== undefined ? `
                <div class="px-12 py-2 animate-in grow duration-300">
                    <input type="text" class="lim-custom-input w-full p-2 bg-white border border-amber-200 rounded-lg text-[10px] font-mono focus:ring-amber-500" placeholder="Saisir l'intention (ex: open_cart)..." value="${val.custom_intent || ''}">
                </div>
            ` : ''}
        `;
    }

    _setupLiminaireHandlers(area) {
        const row = area.querySelector(`[data-index="${this._currentIndex}"]`);
        if (!row) return;

        const val = this._validations[this._currentIndex];
        
        const triggerPreload = (callback) => {
            const bar = row.querySelector('.lim-preload-bar');
            bar.style.width = '100%';
            // Animation proportionnelle au "temps de construction"
            setTimeout(callback, 1200); 
        };

        const nextStep = () => {
            if (this._currentIndex < this._infillingElements.length - 1) {
                this._currentIndex++;
                this._renderLiminaireUI();
            } else {
                this._submitLiminaire(); // Dernier élément validé → forge automatique
            }
        };

        row.querySelector('.lim-opt-yes')?.addEventListener('click', () => {
            val.confirmed = true;
            val.custom_intent = null;
            triggerPreload(nextStep);
        });

        row.querySelector('.lim-opt-no')?.addEventListener('click', () => {
            val.confirmed = false;
            nextStep();
        });

        row.querySelector('.lim-opt-edit')?.addEventListener('click', () => {
            val.confirmed = true;
            val.custom_intent = "";
            this._renderLiminaireUI();
        });

        const input = area.querySelector('.lim-custom-input');
        if (input) {
            input.addEventListener('change', (e) => {
                val.custom_intent = e.target.value.toLowerCase().replace(/\s/g, '_');
            });
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') triggerPreload(nextStep);
            });
        }

        area.querySelector('#lim-btn-next')?.addEventListener('click', nextStep);
        area.querySelector('#lim-btn-prev')?.addEventListener('click', () => {
            this._currentIndex--;
            this._renderLiminaireUI();
        });
        area.querySelector('#lim-btn-finish')?.addEventListener('click', () => this._submitLiminaire());
    }

    async _submitLiminaire() {
        // Nettoyage UI Iframe
        const shell = document.getElementById(window.wsCanvas?.activeScreenId);
        const iframe = shell?.querySelector('iframe');
        iframe?.contentWindow.postMessage({ type: 'clear-highlights' }, '*');

        try {
            const res = await fetch(`/api/projects/${this._projectId}/pre-wire/validate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ validations: this._validations })
            });
            const data = await res.json();
            if (data.status === 'success') {
                const screen = window.wsCanvas.getActiveScreenHtml();
                console.log('[Wire] screen_html len:', screen?.srcdoc?.length, 'src:', screen?.src);
                this._executeForge(this._projectId, screen.srcdoc);
            }
        } catch (err) { console.error(err); }
    }

    async _executeForge(projectId, html) {
        // Mission 187 : Forge déterministe (affichage léger)
        const container = this.overlay.querySelector('.relative.z-10');
        const mainArea = container.querySelector('.flex.gap-6');
        mainArea.innerHTML = `
            <div class="flex-1 flex flex-col items-center justify-center p-12 bg-[#f7f6f2] rounded-2xl border border-[#e5e5e5] h-[600px]">
                <div class="space-y-4 text-center">
                    <p class="text-[#3d3d3c] font-bold text-xs tracking-widest uppercase animate-pulse">forge du maillage en cours...</p>
                    <div class="w-48 h-1 bg-slate-200 rounded-full overflow-hidden mx-auto">
                        <div class="h-full bg-[#8cc63f] animate-forge-progress" style="width: 30%"></div>
                    </div>
                </div>
            </div>
            <style>
                @keyframes forge-progress {
                    0% { width: 0%; }
                    100% { width: 100%; }
                }
                .animate-forge-progress { animation: forge-progress 2s infinite ease-in-out; }
            </style>
        `;

        try {
            const res = await fetch(`/api/projects/${projectId}/wire-apply`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    screen_id: window.wsCanvas.activeScreenId,
                    screen_html: html,
                    validations: this._validations
                })
            });
            const data = await res.json();
            if (data.status === 'success') {
                const shell = document.getElementById(window.wsCanvas.activeScreenId);
                const iframe = shell?.querySelector('iframe');
                if (iframe) {
                    iframe.onload = () => {
                        iframe.onload = null;
                        this.hide();
                    };
                    // Injecter base href pour que les paths relatifs du template fonctionnent en srcdoc
                    const originalSrc = iframe.src || '';
                    const baseUrl = originalSrc ? originalSrc.substring(0, originalSrc.lastIndexOf('/') + 1) : window.location.origin + '/';
                    let forgedHtml = data.html;
                    if (!forgedHtml.includes('<base')) {
                        forgedHtml = forgedHtml.replace('<head>', `<head><base href="${baseUrl}" target="_self">`);
                    }
                    iframe.srcdoc = forgedHtml;
                } else {
                    this.hide();
                }
            } else {
                alert("Erreur forge : " + data.message);
                this._renderLiminaireUI();
            }
        } catch (err) { 
            console.error(err); 
            this._renderLiminaireUI();
        }
    }

    handleWireClick(data) {
        if (!this._isWiring) {
            if (window.wsSurgicalChat) {
                const shell = document.getElementById(window.wsCanvas?.activeScreenId);
                const iframe = shell?.querySelector('iframe');
                const iframeRect = iframe?.getBoundingClientRect() || { top: 0, left: 0 };
                const r = data.rect || {};
                const absoluteRect = {
                    top: iframeRect.top + (r.top || 0),
                    left: iframeRect.left + (r.left || 0),
                    right: iframeRect.left + (r.left || 0) + (r.width || 200),
                    bottom: iframeRect.top + (r.top || 0) + (r.height || 40),
                    width: r.width || 200,
                    height: r.height || 40
                };
                window.wsSurgicalChat.show(data, absoluteRect);
            }
        } else {
            if (!this._triggerData) {
                this._triggerData = data;
                if (this.wireDraft) {
                    this.wireDraft.classList.remove('hidden');
                    this._updateDraftLine();
                }
            } else {
                this._saveWire(this._triggerData, data);
                this._resetWiring();
            }
        }
    }

    _updateDraftLine(mouseEvent = null) {
        if (!this._triggerData || !this.wireDraft) return;
        const iframe = document.querySelector('#ws-preview-frame-container iframe');
        if (!iframe) return;
        const iframeRect = iframe.getBoundingClientRect();
        const x1 = iframeRect.left + this._triggerData.rect.left + (this._triggerData.rect.width / 2);
        const y1 = iframeRect.top + this._triggerData.rect.top + (this._triggerData.rect.height / 2);
        this.wireDraft.setAttribute('x1', x1);
        this.wireDraft.setAttribute('y1', y1);
        if (mouseEvent) {
            this.wireDraft.setAttribute('x2', mouseEvent.clientX);
            this.wireDraft.setAttribute('y2', mouseEvent.clientY);
        } else {
            this.wireDraft.setAttribute('x2', x1);
            this.wireDraft.setAttribute('y2', y1);
        }
    }

    async _saveWire(trigger, target) {
        const eventType = this.eventTypeSelect ? this.eventTypeSelect.value : 'click';
        const wire = {
            trigger: trigger.selector,
            trigger_name: trigger.organName,
            target: target.selector,
            target_name: target.organName,
            event: eventType,
            timestamp: new Date().toISOString()
        };
        this._drawPermanentWire(trigger, target);
        try {
            const projectRes = await fetch('/api/projects/active');
            const projectData = await projectRes.json();
            await fetch(`/api/projects/${projectData.id}/wires`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(wire)
            });
        } catch (err) { console.error(err); }
    }

    _drawPermanentWire(trigger, target) {
        if (!this.wireLines) return;
        const iframe = document.querySelector('#ws-preview-frame-container iframe');
        const iframeRect = iframe.getBoundingClientRect();
        const x1 = iframeRect.left + trigger.rect.left + (trigger.rect.width / 2);
        const y1 = iframeRect.top + trigger.rect.top + (trigger.rect.height / 2);
        const x2 = iframeRect.left + target.rect.left + (target.rect.width / 2);
        const y2 = iframeRect.top + target.rect.top + (target.rect.height / 2);
        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute('x1', x1); line.setAttribute('y1', y1);
        line.setAttribute('x2', x2); line.setAttribute('y2', y2);
        line.setAttribute('stroke', '#A3CD54'); line.setAttribute('stroke-width', '2');
        line.setAttribute('marker-end', 'url(#arrowhead)');
        this.wireLines.appendChild(line);
    }

    getWires() {
        return this._manifest?.wires || [];
    }

    _enterSurgicalReview(modifiedSelectors) {
        console.log("[wswire] entering surgical review for:", modifiedSelectors);
        const shell = document.getElementById(window.wsCanvas?.activeScreenId);
        const iframe = shell?.querySelector('iframe');
        const iframeDoc = iframe?.contentDocument;
        if (!iframeDoc) return;
        const nudges = [];
        modifiedSelectors.forEach(rawSelector => {
            const selector = rawSelector.match(/^[#.][^\s(]*/)?.[0] || rawSelector.split(' ')[0];
            if (!selector || !selector.match(/^[#.]/)) return;
            const el = iframeDoc.querySelector(selector);
            if (el) {
                nudges.push({
                    selector,
                    id: el.id,
                    text: el.textContent.trim().substring(0, 20),
                    tag: el.tagName.toLowerCase(),
                    intent: el.getAttribute('data-wire') || 'maillé',
                    status: 'ok'
                });
            }
        });
        if (nudges.length === 0) {
            iframeDoc.querySelectorAll('[data-wire]').forEach(el => {
                nudges.push({
                    selector: `[data-wire="${el.getAttribute('data-wire')}"]`,
                    id: el.id,
                    intent: el.getAttribute('data-wire'),
                    status: 'ok'
                });
            });
        }
        this._syncNudgesToIframe(nudges);
    }

    _handleNudgeClick(data) {
        if (this._infillingElements) {
            const idx = this._infillingElements.findIndex(el => 
                (data.id && el.id === data.id) || (data.selector && el.selector === data.selector)
            );
            if (idx !== -1) {
                this._currentIndex = idx;
                this._renderLiminaireUI();
            }
        }
    }

    _syncNudgesToIframe(nudges, attempt = 0) {
        const shell = document.getElementById(window.wsCanvas?.activeScreenId);
        const iframe = shell?.querySelector('iframe');
        if (!iframe || !iframe.contentWindow) return;
        iframe.contentWindow.postMessage({ type: 'ws-inject-nudges', nudges }, '*');
    }

    _highlightInIframe(el) {
        if (!el) return;
        const shell = document.getElementById(window.wsCanvas?.activeScreenId);
        const iframe = shell?.querySelector('iframe');
        if (iframe) {
            iframe.contentWindow.postMessage({
                type: 'highlight-intent',
                id: el.id,
                selector: el.selector,
                text: el.text,
                tag: el.tag
            }, '*');
        }
    }

    _resetWiring() {
        this._triggerData = null;
        this._isWiring = false;
        if (this.wireDraft) this.wireDraft.classList.add('hidden');
    }

    hide() {
        if (this.overlay) this.overlay.classList.add('hidden');
        this._resetWiring();
        this._syncNudgesToIframe([]);
    }
}

// Initialisation globale
document.addEventListener('DOMContentLoaded', () => {
    window.wsWire = new WsWire();
});
