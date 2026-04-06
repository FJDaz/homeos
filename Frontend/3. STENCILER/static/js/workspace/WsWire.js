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
            <div class="flex-1 flex flex-col items-center justify-center p-12 bg-[#f7f6f2] border border-[#e5e5e5] h-[600px] animate-in fade-in duration-500" style="border-radius: 0px;">
                <div class="space-y-6 text-center">
                    <div class="flex items-center justify-center">
                        <div class="w-12 h-12 border-4 border-[#8cc63f]/20 border-t-[#8cc63f] animate-spin" style="border-radius: 0px;"></div>
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
        // Sullivan pré-coche ce qu'il a déjà reconnu dans le manifeste
        this._validations = elements.map(el => ({ 
            ...el, confirmed: el.matched === true, custom_intent: null 
        }));

        this._renderLiminaireUI();
    }

    _renderLiminaireUI() {
        const container = this.overlay.querySelector('.relative.z-10');
        const mainArea = container.querySelector('.flex.gap-6');
        
        let previousScrollTop = 0;
        const currentTable = mainArea.querySelector('#liminaire-table');
        if (currentTable) {
            previousScrollTop = currentTable.scrollTop;
        }
        
        const checkedCount = this._validations.filter(v => v.confirmed).length;
        const totalCount = this._validations.length;

        const html = `
            <div class="flex-1 flex flex-col bg-[#f7f6f2] h-[600px] overflow-hidden border border-[#e5e5e5] animate-in slide-in-from-bottom-4 duration-500" style="border-radius: 0px;">
                <!-- Header HoméOS (Hard-Edge) -->
                <div class="px-8 py-6 border-b border-[#e5e5e5] flex items-center justify-between bg-white">
                    <div class="space-y-1">
                        <h3 class="text-[#3d3d3c] font-bold text-xs tracking-widest uppercase italic" style="font-family: 'Source Sans 3', sans-serif;">Cadrage Global</h3>
                        <p class="text-[#3d3d3c]/50 text-[9px] tracking-widest uppercase">${checkedCount} / ${totalCount} Organes Validés par Sullivan</p>
                    </div>
                    <button onclick="window.wsWire._openCadrage()" class="px-4 py-2 border border-[#e5e5e5] text-[#3d3d3c]/50 hover:text-[#3d3d3c] hover:bg-slate-50 text-[9px] font-bold uppercase tracking-widest transition-colors" style="border-radius: 0px;">
                        Cadrage LLM
                    </button>
                </div>

                <!-- Table Executive -->
                <div class="flex-1 overflow-y-auto scrollbar-hide" id="liminaire-table">
                    <table class="w-full text-left border-collapse">
                        <thead class="sticky top-0 bg-[#f7f6f2] z-20">
                            <tr class="border-b border-[#e5e5e5]">
                                <th class="p-4 text-[9px] font-bold text-[#3d3d3c]/40 uppercase tracking-widest w-12 text-center">✓</th>
                                <th class="p-4 text-[9px] font-bold text-[#3d3d3c]/40 uppercase tracking-widest">Organe</th>
                                <th class="p-4 text-[9px] font-bold text-[#3d3d3c]/40 uppercase tracking-widest">Intention</th>
                                <th class="p-4 text-[9px] font-bold text-[#3d3d3c]/40 uppercase tracking-widest text-right">Custom</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-100">
                            ${this._infillingElements.map((el, i) => this._renderRow(el, i)).join('')}
                        </tbody>
                    </table>
                </div>

                <!-- Footer Action Global -->
                <div class="p-6 bg-white flex items-center justify-between border-t border-[#e5e5e5]">
                    <p class="text-[9px] font-bold text-[#3d3d3c]/30 uppercase tracking-widest">raccourcis : [↵ forger] [esp toggle]</p>
                    <button id="lim-btn-global-forge" class="px-10 py-3 bg-[#A3CD54] text-[#1A1A1A] text-[10px] font-bold hover:bg-[#8cc63f] transition-all uppercase tracking-widest shadow-lg shadow-[#A3CD54]/20" style="border-radius: 0px;">
                        Forger le maillage
                    </button>
                </div>
            </div>
        `;

        mainArea.innerHTML = html;
        this._setupLiminaireHandlers(mainArea);
        
        const newTable = mainArea.querySelector('#liminaire-table');
        if (newTable && previousScrollTop > 0) {
            newTable.scrollTop = previousScrollTop;
        }
        
        // Sync Nudges Initial (Tous les validés en dot vert)
        this._syncNudgesToIframe(this._validations.map(v => ({
            ...v,
            status: v.confirmed ? 'ok' : 'none'
        })));
    }

    _renderRow(el, i) {
        const val = this._validations[i];
        const displayId = el.selector.replace('#', '');
        
        return `
            <tr data-index="${i}" class="group hover:bg-white transition-colors cursor-pointer ${val.confirmed ? 'bg-white/40' : ''}">
                <td class="p-4 text-center">
                    <div class="lim-checkbox w-5 h-5 border-2 transition-all flex items-center justify-center mx-auto ${val.confirmed ? 'bg-[#A3CD54] border-[#A3CD54]' : 'border-[#e5e5e5] bg-white'}" style="border-radius: 0px;">
                        ${val.confirmed ? '<svg class="w-3 h-3 text-[#1A1A1A]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="square" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path></svg>' : ''}
                    </div>
                </td>
                <td class="p-4">
                    <div class="flex flex-col">
                        <div class="flex items-center gap-2">
                            <span class="text-[10px] font-bold text-[#3d3d3c] font-mono">#${displayId}</span>
                            <span class="px-1 py-0.5 bg-slate-100 text-slate-400 text-[8px] font-bold uppercase tracking-tighter" style="border-radius: 0px;">${el.tag}</span>
                        </div>
                        <div class="text-[9px] text-[#3d3d3c]/40 italic truncate max-w-[150px]">"${el.text || 'sans texte'}"</div>
                    </div>
                </td>
                <td class="p-4">
                    <code class="text-[10px] text-[#3d3d3c] font-mono ${val.confirmed ? 'text-[#8cc63f]' : 'opacity-50'}">
                        ${val.custom_intent || val.inferred_intent}
                    </code>
                </td>
                <td class="p-4 text-right">
                    <button class="lim-row-edit p-1.5 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-slate-100" style="border-radius: 0px;">
                        <svg class="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="square" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
                    </button>
                    ${val.isEditing ? `
                        <div class="absolute inset-x-0 bottom-0 bg-white border-t border-amber-200 p-2 animate-in slide-in-from-bottom-2 duration-200 z-10 box-shadow">
                            <input type="text" class="lim-inline-input w-full p-2 text-[10px] font-mono border border-amber-200 focus:outline-none focus:ring-1 focus:ring-[#A3CD54]" style="border-radius: 0px;" value="${val.custom_intent || val.inferred_intent}" autofocus>
                        </div>
                    ` : ''}
                </td>
            </tr>
        `;
    }

    _setupLiminaireHandlers(area) {
        const rows = area.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const idx = parseInt(row.dataset.index);
            const val = this._validations[idx];

            // Toggle Checkbox via clic sur ligne (sauf si on clique sur l'édit)
            row.addEventListener('click', (e) => {
                if (e.target.closest('.lim-row-edit') || e.target.closest('.lim-inline-input')) return;
                val.confirmed = !val.confirmed;
                this._renderLiminaireUI();
            });

            // Bouton Edit
            row.querySelector('.lim-row-edit')?.addEventListener('click', (e) => {
                e.stopPropagation();
                val.isEditing = true;
                this._renderLiminaireUI();
            });

            // Input direct
            const input = row.querySelector('.lim-inline-input');
            if (input) {
                input.focus();
                input.addEventListener('input', (e) => {
                    val.custom_intent = e.target.value;
                });
                input.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') {
                        val.isEditing = false;
                        val.confirmed = true;
                        this._renderLiminaireUI();
                    }
                    if (e.key === 'Escape') {
                        val.isEditing = false;
                        this._renderLiminaireUI();
                    }
                });
                input.addEventListener('click', (e) => e.stopPropagation());
            }
        });

        // Bouton Forge Global
        const forgeBtn = area.querySelector('#lim-btn-global-forge');
        if (forgeBtn) {
            forgeBtn.addEventListener('click', () => {
                this._submitLiminaire();
            });
        }

        // Scroll Roulette (Horizontal via Wheel) on liminaire-table
        const table = area.querySelector('#liminaire-table');
        if (table) {
            table.addEventListener('wheel', (e) => {
                if (e.deltaY !== 0) {
                    table.scrollTop += e.deltaY; // Vertical par défaut
                    // Si le contenu dépasse en largeur, on pourrait mapper deltaY -> scrollLeft
                    // Mais ici on assure juste que le scroll interne est prioritaire
                    e.stopPropagation();
                }
            }, { passive: false });
        }

        // Raccourcis clavier
        const handleKeys = (e) => {
            if (this.overlay.classList.contains('hidden')) return;
            if (e.key === 'Enter' && !e.shiftKey) {
                this._submitLiminaire();
            }
        };
        window.removeEventListener('keydown', this._keyHandler);
        this._keyHandler = handleKeys;
        window.addEventListener('keydown', this._keyHandler);
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
                    // Update iframe logic first
                    iframe.onload = () => { iframe.onload = null; };
                    const originalSrc = iframe.src || '';
                    const baseUrl = originalSrc ? originalSrc.substring(0, originalSrc.lastIndexOf('/') + 1) : window.location.origin + '/';
                    let forgedHtml = data.html;
                    if (!forgedHtml.includes('<base')) {
                        forgedHtml = forgedHtml.replace('<head>', `<head><base href="${baseUrl}" target="_self">`);
                    }
                    iframe.srcdoc = forgedHtml;

                    // Écran de succès post-forge (Hard-Edge)
                    const screen = window.wsCanvas.getActiveScreenHtml();
                    const fileName = screen?.src?.split('name=')[1]?.split('&')[0] || 'template.html';
                    const testUrl = `/api/frd/file?name=${fileName}&raw=1`;

                    mainArea.innerHTML = `
                        <div class="flex-1 flex flex-col items-center justify-center p-12 bg-[#f7f6f2] border border-[#e5e5e5] h-[600px] animate-in slide-in-from-bottom-4 duration-500" style="border-radius: 0px;">
                            <div class="space-y-8 text-center max-w-sm">
                                <div class="w-16 h-16 bg-[#A3CD54]/20 border-2 border-[#A3CD54] mx-auto flex items-center justify-center text-[#A3CD54]" style="border-radius: 0px;">
                                    <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="square" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                                </div>
                                <div class="space-y-2">
                                    <h3 class="text-[#3d3d3c] font-bold text-sm tracking-widest uppercase italic">Maillage Forgeré</h3>
                                    <p class="text-[#3d3d3c]/50 text-[10px] tracking-widest uppercase leading-relaxed">Les intentions ont été tissées dans le code source déterministe.</p>
                                </div>
                                <div class="flex flex-col gap-3 pt-4">
                                    <button onclick="window.open('${testUrl}', '_blank')" class="w-full px-6 py-3 bg-[#A3CD54] text-[#1A1A1A] text-[10px] font-bold uppercase tracking-widest hover:bg-[#8cc63f] transition-all shadow-sm" style="border-radius: 0px;">
                                        Tester la Page
                                    </button>
                                    <button onclick="window.wsWire.hide()" class="w-full px-6 py-3 border border-[#e5e5e5] text-[#3d3d3c]/50 hover:text-[#3d3d3c] hover:bg-white text-[10px] font-bold uppercase tracking-widest transition-all" style="border-radius: 0px;">
                                        Fermer l'interface
                                    </button>
                                </div>
                            </div>
                        </div>
                    `;
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
