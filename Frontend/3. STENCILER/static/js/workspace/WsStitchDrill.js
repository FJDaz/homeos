/**
 * WsStitchDrill — M280/M292
 * Landing canvas + drill paramétrage (Écrans → Clés → Manifeste)
 * 
 * ORDRE:
 * 1. Écrans (1-4) — uploadés en premier pour que la forge les traite dès les clés configurées
 * 2. Clés API — avec explication optimisation moteur AetherFlow
 * 3. Manifeste aperçu — puis canvas
 */
(function() {
    'use strict';
    console.log('[WsStitchDrill] init');

    let overlay = null;
    let currentStep = 0;
    let keyStatus = {};
    let screenCount = 0;

    const API_PROVIDERS = [
        { id: 'gemini', label: 'Gemini', price: 'Gratuit (15 RPM)' },
        { id: 'groq', label: 'Groq', price: 'Gratuit (quota limité)' },
        { id: 'openai', label: 'OpenAI', price: '~$0.005/1K tokens' },
        { id: 'deepseek', label: 'DeepSeek', price: '~$0.001/1K tokens' },
        { id: 'qwen', label: 'Qwen', price: 'Gratuit (quota généreux)' },
    ];

    function getSession() {
        try { return JSON.parse(localStorage.getItem('homeos_session') || '{}'); } catch(e) { return {}; }
    }

    async function isCanvasEmpty() {
        try {
            const res = await fetch('/api/retro-genome/imports');
            const data = await res.json();
            return (data.imports || []).length === 0;
        } catch(e) { return true; }
    }

    async function fetchKeyStatus() {
        try {
            const session = getSession();
            const res = await fetch('/api/me/keys', { headers: { 'X-User-Token': session.token || '' } });
            if (res.ok) keyStatus = await res.json();
        } catch(e) { console.warn('[WsStitchDrill] Key status error:', e); }
        return keyStatus;
    }

    function getActiveKeyCount() {
        return Object.values(keyStatus).filter(v => v === 'set').length;
    }

    function createOverlay() {
        if (overlay) return;
        overlay = document.createElement('div');
        overlay.id = 'ws-stitch-drill-overlay';
        overlay.style.cssText = `
            position: fixed; inset: 0; z-index: 99999;
            background: rgba(247,246,242,0.5);
            backdrop-filter: blur(3px);
            -webkit-backdrop-filter: blur(3px);
            display: flex; align-items: center; justify-content: center;
            flex-direction: column;
        `;
        document.body.appendChild(overlay);
        fetchKeyStatus();
        renderStep();
    }

    function renderStep() {
        if (!overlay) return;

        const steps = [
            // Step 0: Landing
            {
                html: `
                    <button id="drill-start-btn" class="w-32 h-32 rounded-full text-white font-bold text-[14px] uppercase tracking-widest shadow-lg cursor-pointer"
                            style="background: linear-gradient(135deg, #a3d960 0%, #8cc63f 30%, #7ab536 70%, #5a8a26 100%); animation: pulse 2s ease-in-out infinite;">
                        Créer un<br>projet
                    </button>
                    <style>@keyframes pulse { 0%,100%{transform:scale(1);box-shadow:0 0 0 0 rgba(140,198,63,0.4)} 50%{transform:scale(1.05);box-shadow:0 0 30px 10px rgba(140,198,63,0.2)} }</style>
                `
            },
            // Step 1: Screens FIRST (so forge processes them while keys are configured)
            {
                html: `
                    <div class="text-center max-w-md">
                        <div class="text-[18px] font-bold text-[#3d3d3c] mb-2">Étape 1 — Écrans</div>
                        <div class="text-[11px] text-[#9a9a98] mb-6">Charge 1 à 4 écrans (PNG, SVG, JPG). La forge les traitera dès tes clés configurées.</div>
                        <div class="p-6 border-2 border-dashed border-[#e5e5e5] rounded-[20px] hover:border-[#8cc63f] transition-all cursor-pointer" id="drill-screen-upload-zone">
                            <div class="text-[24px] mb-2">↑</div>
                            <div class="text-[12px] font-bold text-[#3d3d3c]">Glisser tes écrans ici</div>
                            <div class="text-[10px] text-[#9a9a98]">ou cliquer pour parcourir</div>
                            <input type="file" id="drill-screen-input" class="hidden" accept=".png,.svg,.jpg,.jpeg" multiple>
                        </div>
                        <div id="drill-screen-status" class="mt-3 text-[10px] text-[#9a9a98]"></div>
                        <div class="mt-2 text-[10px] text-[#9a9a98]" id="drill-screen-count">0 écran(s) — min. 1 requis</div>
                        <button id="drill-continue-screens" class="mt-4 px-8 py-2.5 bg-[#8cc63f] text-white text-[11px] font-bold rounded-[12px] hover:bg-[#7ab536] transition-all disabled:opacity-40 disabled:cursor-not-allowed" disabled>Continuer →</button>
                    </div>
                `
            },
            // Step 2: Keys + Motor optimization explanation
            {
                html: `
                    <div class="text-center max-w-md">
                        <div class="text-[18px] font-bold text-[#3d3d3c] mb-2">Étape 2 — Moteur AetherFlow</div>
                        <div class="bg-[#8cc63f]/10 border border-[#8cc63f]/30 rounded-[16px] p-4 mb-4 text-left">
                            <div class="text-[11px] font-bold text-[#6a9a2f] mb-1">⚡ Optimisation du moteur</div>
                            <div class="text-[10px] text-[#3d3d3c] leading-relaxed">
                                HomeOS utilise un <strong>fallback en cascade</strong> : si un modèle ne répond pas, le suivant prend le relais.
                                <strong>Plus tu renseignes de clés, plus le moteur est fiable et rapide.</strong>
                                C'est gratuit et ça profite à toute la classe.
                            </div>
                        </div>
                        <div class="bg-white border border-[#e5e5e5] rounded-[16px] p-4 mb-4 text-left space-y-3">
                            ${API_PROVIDERS.map(p => `
                                <div class="flex items-start gap-2">
                                    <div class="w-2 h-2 mt-2.5 rounded-full ${keyStatus[p.id] === 'set' ? 'bg-[#8cc63f]' : 'bg-[#e5e5e5]'}"></div>
                                    <div class="flex-1">
                                        <div class="flex items-center gap-1 mb-1">
                                            <span class="text-[12px] font-bold text-[#3d3d3c]">${p.label}</span>
                                            <span class="text-[11px] text-[#9a9a98]">${p.price}</span>
                                            <button class="drill-help-btn ml-1 text-[#9a9a98] hover:text-[#8cc63f] transition-all" data-provider="${p.id}" title="Trouver l'URL">
                                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                                            </button>
                                        </div>
                                        <div class="flex gap-1">
                                            <input type="password" class="drill-key-input flex-1 px-2 py-1.5 text-[12px] border border-[#e5e5e5] rounded-[8px] outline-none focus:border-[#8cc63f] transition-all" data-provider="${p.id}" placeholder="Clé ${p.label}..." value="">
                                            <button class="drill-save-btn px-2 py-1.5 text-[11px] font-bold bg-[#8cc63f] text-white rounded-[8px] hover:bg-[#7ab536] transition-all whitespace-nowrap" data-provider="${p.id}">OK</button>
                                        </div>
                                        <div class="drill-helper-text mt-1 text-[11px] text-[#8cc63f] hidden" id="drill-helper-${p.id}"></div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                        <div class="text-[10px] text-[#9a9a98] mb-3"><span id="drill-key-count">${getActiveKeyCount()}</span> clé(s) configurée(s) — <span class="text-[#8cc63f]">💡 aussi dispo via ⚙</span></div>
                        <button id="drill-continue-keys" class="px-8 py-2.5 bg-[#8cc63f] text-white text-[11px] font-bold rounded-[12px] hover:bg-[#7ab536] transition-all">Continuer →</button>
                    </div>
                `
            },
            // Step 3: Manifest preview
            {
                html: `
                    <div class="text-center max-w-md">
                        <div class="text-[18px] font-bold text-[#3d3d3c] mb-2">Étape 3 — Manifeste</div>
                        <div class="text-[11px] text-[#9a9a98] mb-4">Le manifeste définit l'ADN de ton projet. Modifiable plus tard.</div>
                        <div id="drill-manifest-preview" class="bg-white border border-[#e5e5e5] rounded-[16px] p-4 mb-4 text-left text-[11px] text-[#3d3d3c] max-h-48 overflow-y-auto">
                            <em class="text-[#9a9a98]">Chargement...</em>
                        </div>
                        <button id="drill-continue-manifest" class="px-8 py-2.5 bg-[#8cc63f] text-white text-[11px] font-bold rounded-[12px] hover:bg-[#7ab536] transition-all">Continuer →</button>
                    </div>
                `
            },
            // Step 4: Forged screens display
            {
                html: `
                    <div class="text-center max-w-md">
                        <div class="text-[18px] font-bold text-[#3d3d3c] mb-2">Étape 4 — Écrans forgés</div>
                        <div class="text-[11px] text-[#9a9a98] mb-4">Pendant que tu configurais tes clés, la forge a traité tes écrans. Voici le résultat :</div>
                        <div id="drill-forged-screens" class="bg-white border border-[#e5e5e5] rounded-[16px] p-4 mb-4 text-left max-h-64 overflow-y-auto space-y-2">
                            <div class="text-[11px] text-[#9a9a98] italic">Chargement des écrans forgés...</div>
                        </div>
                        <button id="drill-finish" class="px-8 py-3 bg-gradient-to-r from-[#8cc63f] to-[#6a9a2f] text-white text-[12px] font-bold uppercase tracking-wider rounded-[16px] hover:shadow-lg transition-all">Commencer à travailler →</button>
                    </div>
                `
            }
        ];

        const step = steps[currentStep];
        overlay.innerHTML = step.html;
        wireStep(currentStep);
    }

    function wireStep(stepIndex) {
        if (stepIndex === 0) {
            document.getElementById('drill-start-btn').onclick = () => { currentStep = 1; renderStep(); };
        }
        else if (stepIndex === 1) {
            // Step 1: Screen upload
            const zone = document.getElementById('drill-screen-upload-zone');
            const input = document.getElementById('drill-screen-input');
            const status = document.getElementById('drill-screen-status');
            const countEl = document.getElementById('drill-screen-count');
            const btn = document.getElementById('drill-continue-screens');

            zone.onclick = () => input.click();
            zone.ondragover = (e) => { e.preventDefault(); zone.style.borderColor = '#8cc63f'; };
            zone.ondragleave = () => { zone.style.borderColor = '#e5e5e5'; };
            zone.ondrop = (e) => { e.preventDefault(); zone.style.borderColor = '#e5e5e5'; if (e.dataTransfer.files.length) handleScreenUpload(e.dataTransfer.files, status, countEl, btn); };
            input.onchange = () => { if (input.files.length) handleScreenUpload(input.files, status, countEl, btn); };

            btn.onclick = () => { if (screenCount >= 1) { currentStep = 2; renderStep(); } };
        }
        else if (stepIndex === 2) {
            // Step 2: Keys + help buttons + save buttons
            document.querySelectorAll('.drill-help-btn').forEach(btn => {
                btn.onclick = async (e) => {
                    e.stopPropagation();
                    const provider = btn.dataset.provider;
                    const helperEl = document.getElementById(`drill-helper-${provider}`);
                    if (!helperEl) return;
                    helperEl.textContent = 'Recherche...';
                    helperEl.classList.remove('hidden');
                    helperEl.style.color = '#9a9a98';
                    try {
                        const res = await fetch(`/api/me/keys/helper/${provider}`);
                        if (!res.ok) throw new Error('API erreur');
                        const data = await res.json();
                        if (data.url) {
                            helperEl.innerHTML = `<a href="${data.url}" target="_blank" style="text-decoration:underline;color:#8cc63f;" class="font-bold">→ ${data.instructions}</a>`;
                            helperEl.style.color = '#8cc63f';
                        } else { helperEl.textContent = 'URL non trouvée.'; helperEl.style.color = '#d44'; }
                    } catch(err) { helperEl.textContent = 'Erreur.'; helperEl.style.color = '#d44'; }
                };
            });

            // Save buttons (OK)
            document.querySelectorAll('.drill-save-btn').forEach(btn => {
                btn.onclick = (e) => {
                    e.stopPropagation();
                    const provider = btn.dataset.provider;
                    const input = document.querySelector(`.drill-key-input[data-provider="${provider}"]`);
                    if (input && input.value.trim()) saveKey(provider, input.value.trim());
                };
            });

            document.querySelectorAll('.drill-key-input').forEach(input => {
                const provider = input.dataset.provider;
                input.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); saveKey(provider, input.value.trim()); } });
                input.addEventListener('input', () => {
                    const count = getActiveKeyCount() + (input.value.trim() ? 1 : 0);
                    const countEl = document.getElementById('drill-key-count');
                    if (countEl) countEl.textContent = count;
                });
            });

            document.getElementById('drill-continue-keys').onclick = () => { currentStep = 3; renderStep(); };
        }
        else if (stepIndex === 3) {
            // Step 3: Manifest preview
            loadManifestPreview();
            document.getElementById('drill-continue-manifest').onclick = () => { currentStep = 4; renderStep(); };
        }
        else if (stepIndex === 4) {
            // Step 4: Forged screens display
            loadForgedScreens();
            document.getElementById('drill-finish').onclick = finishDrill;
        }
    }

    async function saveKey(provider, key) {
        if (!key) return;
        try {
            const session = getSession();
            const res = await fetch('/api/me/keys', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-User-Token': session.token || '' },
                body: JSON.stringify({ provider, api_key: key })
            });
            if (res.ok) {
                keyStatus[provider] = 'set';
                const input = document.querySelector(`.drill-key-input[data-provider="${provider}"]`);
                if (input) {
                    input.style.borderColor = '#8cc63f';
                    input.style.backgroundColor = '#f0fdf4';
                    setTimeout(() => { input.style.borderColor = ''; input.style.backgroundColor = ''; }, 1500);
                    const dot = input.closest('.flex').querySelector('.rounded-full');
                    if (dot) { dot.classList.remove('bg-[#e5e5e5]'); dot.classList.add('bg-[#8cc63f]'); }
                }
                const count = getActiveKeyCount();
                const countEl = document.getElementById('drill-key-count');
                if (countEl) countEl.textContent = count;
            }
        } catch(e) { console.error('[WsStitchDrill] Key save error:', e); }
    }

    async function handleScreenUpload(files, statusEl, countEl, btn) {
        let uploaded = 0;
        statusEl.textContent = 'Upload en cours...';
        statusEl.style.color = '#8cc63f';

        for (const file of files) {
            if (uploaded >= 4) break;
            try {
                const formData = new FormData();
                formData.append('file', file);
                formData.append('filename', file.name);

                const res = await fetch('/api/import/upload', { method: 'POST', body: formData });
                if (!res.ok) { statusEl.textContent = 'Erreur (' + res.status + ')'; statusEl.style.color = '#d44'; return; }
                uploaded++;
            } catch(e) { statusEl.textContent = 'Erreur: ' + e.message; statusEl.style.color = '#d44'; return; }
        }

        if (uploaded > 0) {
            screenCount += uploaded;
            countEl.textContent = screenCount + ' écran(s) chargé(s) — min. 1 requis';
            statusEl.textContent = '✓ ' + uploaded + ' écran(s) uploadé(s)';
            statusEl.style.color = '#8cc63f';
            if (screenCount >= 1) btn.disabled = false;
            if (window.WsImportList) window.WsImportList.refresh();
        }
    }

    async function loadManifestPreview() {
        const preview = document.getElementById('drill-manifest-preview');
        if (!preview) return;
        try {
            const session = getSession();
            const projectId = session.active_project_id || session.project_id;
            const res = await fetch(`/api/projects/${projectId}/manifest`);
            if (res.ok) {
                const m = await res.json();
                const name = m.name || 'Sans titre';
                const screens = (m.screens || []).length;
                const archetype = m.archetype?.label || m.archetype || '—';
                preview.innerHTML = `<div class="font-bold text-[12px] mb-1">${name}</div><div class="flex gap-3 text-[9px] text-[#9a9a98]"><span>Archétype: ${archetype}</span><span>Écrans: ${screens}</span></div>`;
            } else {
                preview.innerHTML = '<em class="text-[#9a9a98]">Aucun manifeste — tu pourras le créer plus tard.</em>';
            }
        } catch(e) { preview.innerHTML = '<em class="text-[#9a9a98]">Erreur chargement</em>'; }
    }

    async function loadForgedScreens() {
        const container = document.getElementById('drill-forged-screens');
        if (!container) return;
        try {
            const res = await fetch('/api/retro-genome/imports');
            const data = await res.json();
            const imports = data.imports || [];

            if (imports.length === 0) {
                container.innerHTML = '<div class="text-[11px] text-[#9a9a98] italic">Aucun écran forgé pour le moment — la forge travaille encore.</div>';
                return;
            }

            container.innerHTML = imports.map(imp => `
                <div class="flex items-center gap-2 p-2 bg-[#f7f6f2] rounded-[8px]">
                    <div class="w-8 h-8 bg-[#e5e5e5] rounded-[6px] flex items-center justify-center text-[8px] text-[#9a9a98] font-bold">${imp.type || 'html'}</div>
                    <div class="flex-1 min-w-0">
                        <div class="text-[11px] font-bold text-[#3d3d3c] truncate">${imp.name || imp.id}</div>
                        <div class="text-[9px] text-[#9a9a98]">${imp.archetype_label || imp.archetype || 'import'} · ${imp.timestamp?.substring(0, 16) || ''}</div>
                    </div>
                </div>
            `).join('');
        } catch(e) {
            container.innerHTML = '<div class="text-[11px] text-[#9a9a98] italic">Erreur chargement des écrans forgés.</div>';
        }
    }

    function finishDrill() {
        if (overlay) { overlay.style.display = 'none'; overlay = null; }
        if (window.WsImportList) window.WsImportList.refresh();
    }

    function show() {
        const session = getSession();
        const role = session.role || 'student';
        if (role !== 'student') { console.log('[WsStitchDrill] Skipping for role:', role); return; }
        
        // Always show for students — check if canvas is empty for full overlay or small button
        isCanvasEmpty().then(empty => {
            if (empty) {
                createOverlay();
            } else {
                // Canvas not empty — show small "Nouveau projet" button in corner
                createSmallButton();
            }
        });
    }

    function createSmallButton() {
        // Remove existing if any
        const existing = document.getElementById('drill-small-btn');
        if (existing) existing.remove();

        const btn = document.createElement('button');
        btn.id = 'drill-small-btn';
        btn.textContent = '+ Nouveau projet';
        btn.style.cssText = `
            position: fixed; bottom: 80px; right: 20px; z-index: 99999;
            background: #8cc63f; color: white; border: none;
            padding: 10px 18px; border-radius: 12px;
            font-size: 12px; font-weight: bold;
            cursor: pointer; box-shadow: 0 2px 12px rgba(0,0,0,0.15);
            transition: all 0.2s;
        `;
        btn.onmouseenter = () => { btn.style.transform = 'scale(1.05)'; };
        btn.onmouseleave = () => { btn.style.transform = 'scale(1)'; };
        btn.onclick = () => { btn.remove(); createOverlay(); };
        document.body.appendChild(btn);
    }

    function hide() { if (overlay) { overlay.style.display = 'none'; overlay = null; } }

    window.WsStitchDrill = { show, hide };
    console.log('[WsStitchDrill] ✅ OK');
})();
