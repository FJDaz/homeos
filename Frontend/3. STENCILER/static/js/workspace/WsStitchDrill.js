/**
 * WsStitchDrill — M280/M292
 * Landing canvas + drill paramétrage (Écrans → Clés → Manifeste → Écrans forgés)
 *
 * ORDRE:
 * 1. Écrans (1-4) — uploadés en premier pour que la forge les traite dès les clés configurées
 * 2. Clés API — avec explication optimisation moteur AetherFlow
 * 3. Manifeste — upload ou aperçu
 * 4. Écrans forgés — résultat de la forge
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
        try {
            const isImpersonate = new URLSearchParams(window.location.search).get('impersonate') === '1';
            if (isImpersonate) {
                const imp = JSON.parse(sessionStorage.getItem('homeos_impersonation') || '{}');
                if (imp.token) return imp;
            }
            return JSON.parse(localStorage.getItem('homeos_session') || '{}');
        } catch(e) { return {}; }
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
        injectDrillStyles();
        fetchKeyStatus();
        renderStep();
    }

    function injectDrillStyles() {
        if (document.getElementById('ws-drill-styles')) return;
        const s = document.createElement('style');
        s.id = 'ws-drill-styles';
        s.textContent = `
            @keyframes pulse-low-cpu {
                0% { transform: scale(1) translateZ(0); opacity: 0.8; }
                100% { transform: scale(1.4) translateZ(0); opacity: 0; }
            }
            @keyframes success-pop {
                0% { transform: scale(0.9) translateZ(0); opacity: 0; }
                50% { transform: scale(1.05) translateZ(0); }
                100% { transform: scale(1) translateZ(0); opacity: 1; }
            }
            .success-badge {
                animation: success-pop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
            }
            #drill-landing-btn { position: relative; }
            #drill-landing-btn::after {
                content: "";
                position: absolute;
                inset: -6px;
                border: 3px solid #8cc63f;
                border-radius: 50%;
                animation: pulse-low-cpu 3s infinite cubic-bezier(0.4, 0, 0.2, 1);
                pointer-events: none;
                will-change: transform, opacity;
            }
            .drill-card {
                background: white;
                border-radius: 24px;
                padding: 40px;
                box-shadow: 0 10px 30px -5px rgba(0,0,0,0.05), 0 0 1px rgba(0,0,0,0.1);
                border: 1px solid rgba(229,229,225,0.5);
                animation: success-pop 0.5s ease-out;
                position: relative;
            }
            .drill-screen-stack {
                position: relative;
                height: 180px;
                margin-top: 20px;
                margin-bottom: 40px;
                perspective: 1200px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .stacked-screen {
                position: absolute;
                width: 100px;
                height: 160px;
                object-fit: cover;
                border-radius: 12px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.15);
                border: 3px solid white;
                transition: all 0.6s cubic-bezier(0.23, 1, 0.32, 1);
                background: white;
                transform-origin: bottom center;
            }
            .status-reward {
                font-size: 18px !important;
                font-weight: 800;
                color: #1a1a1a;
                letter-spacing: -0.02em;
            }
        `;
        document.head.appendChild(s);
    }

    function renderStep() {
        if (!overlay) return;

        const steps = [
            // Step 0: Landing
            {
                html: `
                    <button id="drill-landing-btn" class="w-36 h-36 rounded-full text-white font-bold text-[18px] uppercase tracking-widest shadow-2xl cursor-pointer hover:scale-105 transition-transform"
                            style="background: linear-gradient(135deg, #a3d960 0%, #8cc63f 30%, #7ab536 70%, #5a8a26 100%);">
                        Créer un<br>projet
                    </button>
                `
            },
            // Step 1: Screens FIRST
            {
                html: `
                    <div class="drill-card text-center max-w-sm">
                        <div class="text-[22px] font-black text-[#1a1a1a] mb-2 tracking-tight">1. Écrans</div>
                        <div class="text-[14px] text-[#94a3b8] mb-8 leading-relaxed">Charge tes ressources architecturales (1-4 fichiers). La forge les traitera dès ton signal.</div>
                        
                        <div id="drill-screen-preview-area" class="hidden drill-screen-stack"></div>

                        <div class="p-10 border-2 border-dashed border-[#f1f5f9] bg-[#f8fafc] rounded-[24px] hover:border-[#8cc63f] hover:bg-white transition-all group cursor-pointer" id="drill-screen-upload-zone">
                            <div class="text-[32px] mb-2 group-hover:scale-110 transition-transform">↑</div>
                            <div class="text-[15px] font-bold text-[#1a1a1a]">Sélectionner les écrans</div>
                            <div class="text-[12px] text-[#94a3b8] mt-1">PNG, JPG ou SVG</div>
                            <input type="file" id="drill-screen-input" class="hidden" accept=".png,.svg,.jpg,.jpeg" multiple>
                        </div>
                        <div id="drill-screen-status" class="mt-4 font-medium min-h-[24px]"></div>
                        <div id="drill-screen-count-container" class="mt-6 flex flex-col items-center gap-2">
                             <div class="text-[12px] text-[#94a3b8] font-mono" id="drill-screen-count">ATTENTE RESSOURCES</div>
                        </div>
                        <button id="drill-continue-screens" class="mt-8 w-full py-4 bg-[#8cc63f] text-[#1a1a1a] text-[14px] font-black rounded-[20px] shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all disabled:opacity-20 disabled:cursor-not-allowed uppercase tracking-widest disabled:translate-y-0" disabled>Continuer →</button>
                    </div>
                `
            },
            // Step 2: Keys
            {
                html: `
                    <div class="text-center max-w-md">
                        <div class="text-[20px] font-bold text-[#3d3d3c] mb-2">Étape 2 — Moteur AetherFlow</div>
                        <div class="bg-[#8cc63f]/10 border border-[#8cc63f]/30 rounded-[16px] p-4 mb-4 text-left">
                            <div class="text-[13px] font-bold text-[#6a9a2f] mb-1">⚡ Optimisation du moteur</div>
                            <div class="text-[12px] text-[#3d3d3c] leading-relaxed">
                                HomeOS utilise un <strong>fallback en cascade</strong> : si un modèle ne répond pas, le suivant prend le relais.
                                <strong>Plus tu renseignes de clés, plus le moteur est fiable et rapide.</strong>
                                C'est gratuit et ça profite à toute la classe.
                            </div>
                        </div>
                        <div class="bg-white border border-[#e5e5e5] rounded-[16px] p-4 mb-4 text-left space-y-3">
                            ${API_PROVIDERS.map(p => `
                                <div class="flex items-start gap-2">
                                    <div class="w-[10px] h-[10px] mt-2.5 rounded-full ${keyStatus[p.id] === 'set' ? 'bg-[#8cc63f]' : 'bg-[#e5e5e5]'}"></div>
                                    <div class="flex-1">
                                        <div class="flex items-center gap-1 mb-1">
                                            <span class="text-[14px] font-bold text-[#3d3d3c]">${p.label}</span>
                                            <span class="text-[13px] text-[#9a9a98]">${p.price}</span>
                                            <button class="drill-help-btn ml-1 text-[#9a9a98] hover:text-[#8cc63f] transition-all" data-provider="${p.id}" title="Trouver l'URL">
                                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                                            </button>
                                        </div>
                                        <div class="flex gap-1">
                                            <input type="password" class="drill-key-input flex-1 px-2 py-1.5 text-[14px] border border-[#e5e5e5] rounded-[8px] outline-none focus:border-[#8cc63f] transition-all" data-provider="${p.id}" placeholder="Clé ${p.label}..." value="">
                                            <button class="drill-save-btn px-2 py-1.5 text-[13px] font-bold bg-[#8cc63f] text-white rounded-[8px] hover:bg-[#7ab536] transition-all whitespace-nowrap" 
                                                data-ux="ACTION" data-ux-label="drill:keys:save"
                                                data-provider="${p.id}">OK</button>
                                        </div>
                                        <div class="drill-helper-text mt-1 text-[13px] text-[#8cc63f] hidden" id="drill-helper-${p.id}"></div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                        <div class="text-[12px] text-[#9a9a98] mb-3"><span id="drill-key-count">${getActiveKeyCount()}</span> clé(s) configurée(s) — <span class="text-[#8cc63f]">💡 aussi dispo via ⚙</span></div>
                        <button id="drill-continue-keys" 
                                data-ux="ACTION" data-ux-label="drill:keys:continue"
                                class="px-8 py-2.5 bg-[#8cc63f] text-white text-[13px] font-bold rounded-[12px] hover:bg-[#7ab536] transition-all">Continuer →</button>
                    </div>
                `
            },
            // Step 3: Choice (M354 Linear Flow)
            {
                html: `
                    <div class="text-center max-w-md">
                        <div class="text-[20px] font-bold text-[#3d3d3c] mb-2">Configuration du projet</div>
                        <div class="text-[13px] text-[#9a9a98] mb-8">Comment souhaites-tu définir l'ADN de ton projet ?</div>
                        <div class="flex flex-col gap-4">
                            <button id="btn-drill-choice-upload" data-ux="DECISION" data-ux-label="Choix: Manifeste existant" class="p-6 border-2 border-[#e5e5e5] rounded-[24px] text-left hover:border-[#8cc63f] hover:bg-[#f8fafc] transition-all group">
                                <div class="font-bold text-[15px] mb-1 group-hover:text-[#8cc63f]">J'ai un manifeste</div>
                                <div class="text-[12px] text-[#9a9a98]">Tu possèdes déjà un fichier .json or .md de ton architecture.</div>
                            </button>
                            <button id="btn-drill-choice-zero" data-ux="DECISION" data-ux-label="Choix: Partir de zéro" class="p-6 border-2 border-[#e5e5e5] rounded-[24px] text-left hover:border-[#8cc63f] hover:bg-[#f8fafc] transition-all group">
                                <div class="font-bold text-[15px] mb-1 group-hover:text-[#8cc63f]">Je pars de zéro</div>
                                <div class="text-[12px] text-[#9a9a98]">Laisse Sullivan analyser tes écrans pour prédire ton intention de design.</div>
                            </button>
                        </div>
                    </div>
                `
            },
            // Step 4: Manifest Upload
            {
                html: `
                    <div class="text-center max-w-md">
                        <div class="text-[20px] font-bold text-[#3d3d3c] mb-2">Import du manifeste</div>
                        <div class="text-[13px] text-[#9a9a98] mb-6">Dépose ton fichier pour synchroniser ton architecture.</div>
                        <div id="drill-manifest-upload-container"></div>
                        <button id="btn-drill-back-choice" class="mt-6 text-[12px] text-[#9a9a98] hover:text-[#3d3d3c]">← retour au choix</button>
                    </div>
                `
            },
            // Step 5: Sullivan Inference View
            {
                html: `
                    <div class="text-center max-w-md">
                        <div class="text-[20px] font-bold text-[#3d3d3c] mb-2">Analyse Sullivan</div>
                        <div id="drill-inference-container" class="mb-6"></div>
                        <div class="flex gap-3">
                            <button id="btn-drill-back-to-choice" data-ux="CORRECTION" data-ux-label="Retour au choix (Inférence)" class="flex-1 py-4 border-2 border-[#e5e5e5] rounded-[16px] text-[#3d3d3c] font-bold text-[13px]">← retour</button>
                            <button id="btn-drill-confirm-inference" data-ux="ACTION" data-ux-label="Validation Inférence Sullivan" class="flex-1 py-4 bg-[#8cc63f] text-white rounded-[16px] font-bold text-[13px]">valider l'intention →</button>
                        </div>
                    </div>
                `
            },
            // Step 6: Forged screens (ancien Step 4)
            {
                html: `
                    <div class="text-center max-w-md">
                        <div class="text-[20px] font-bold text-[#3d3d3c] mb-2">Écrans forgés</div>
                        <div class="text-[13px] text-[#9a9a98] mb-4">Pendant que tu configurais tes clés, la forge a traité tes écrans.</div>
                        <div id="drill-forged-screens" class="bg-white border border-[#e5e5e5] rounded-[16px] p-4 mb-4 text-left max-h-64 overflow-y-auto space-y-2">
                            <div class="text-[13px] text-[#9a9a98] italic">Chargement...</div>
                        </div>
                    </div>
                `
            }
        ];

        const step = steps[currentStep];
        overlay.innerHTML = step.html;
        wireStep(currentStep);
        // M298 debug: post-wire snapshot (after async injection settles)
        setTimeout(() => {
            const btns = overlay.querySelectorAll('button');
            const commenceBtns = Array.from(btns).filter(b => b.textContent.includes('Commencer'));
            console.log('[WsStitchDrill] post-render step', currentStep, '—',
                btns.length, 'btn(s) total,',
                commenceBtns.length, '"Commencer":',
                commenceBtns.map(b => ({id: b.id, parent: b.parentElement?.tagName})));
        }, 800);
    }

    function wireStep(stepIndex) {
        if (stepIndex === 0) {
            document.getElementById('drill-landing-btn').onclick = () => { currentStep = 1; renderStep(); };
        }
        else if (stepIndex === 1) {
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
            // Step 2: Keys + help + save buttons
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
            document.getElementById('btn-drill-choice-upload').onclick = () => { currentStep = 4; renderStep(); };
            document.getElementById('btn-drill-choice-zero').onclick = () => { currentStep = 5; renderStep(); };
        }
        else if (stepIndex === 4) {
             const session = getSession();
             const projectId = session.active_project_id || session.project_id;
             showManifestUpload(document.getElementById('drill-manifest-upload-container'), null);
             document.getElementById('btn-drill-back-choice').onclick = () => { currentStep = 3; renderStep(); };
        }
        else if (stepIndex === 5) {
            renderInferenceStep();
        }
        else if (stepIndex === 6) {
            loadForgedScreens();
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
        statusEl.textContent = 'Capture des fichiers...';
        statusEl.className = 'mt-4 font-medium min-h-[24px] text-[#8cc63f]';

        const previewArea = document.getElementById('drill-screen-preview-area');
        if (previewArea) {
            previewArea.classList.remove('hidden');
        }

        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            if (uploaded + screenCount >= 4) break;
            
            try {
                // Aperçu immédiat (Cléa stack logic - Fan Effect 10° interval)
                if (previewArea) {
                    const img = document.createElement('img');
                    img.src = URL.createObjectURL(file);
                    img.className = 'stacked-screen success-badge';
                    
                    const index = screenCount + uploaded;
                    const angle = index * 10; // 10° par rapport au précédent
                    const xOffset = (index * 20) - 30; // Décalage horizontal pour l'éventail
                    
                    img.style.transform = `translateX(${xOffset}px) rotate(${angle}deg)`;
                    img.style.zIndex = index;
                    previewArea.appendChild(img);
                }

                const formData = new FormData();
                formData.append('file', file);
                formData.append('filename', file.name);
                const res = await fetch('/api/import/upload', { method: 'POST', body: formData });
                if (!res.ok) { statusEl.textContent = 'Erreur (' + res.status + ')'; statusEl.style.color = '#d44'; return; }
                
                // M354: Architecture Extract par écran (fire-and-forget)
                const _s = getSession();
                const _pid = _s.active_project_id || _s.project_id;
                if (_pid) fetch('/api/imports/extract-tokens', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-User-Token': _s.token || '' }, body: JSON.stringify({ project_id: _pid }) })
                    .then(() => fetch('/api/imports/infer-intent', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-User-Token': _s.token || '' }, body: JSON.stringify({ project_id: _pid }) }))
                    .catch(() => {}); // silencieux
                
                uploaded++;
            } catch(e) { statusEl.textContent = 'Erreur: ' + e.message; statusEl.style.color = '#d44'; return; }
        }

        if (uploaded > 0) {
            screenCount += uploaded;
            const countEl = document.getElementById('drill-screen-count');
            const countContainer = document.getElementById('drill-screen-count-container');
            const uploadZone = document.getElementById('drill-screen-upload-zone');
            
            if (countEl) countEl.remove();
            if (uploadZone) uploadZone.style.display = 'none';
            
            const badge = document.createElement('div');
            badge.className = 'success-badge flex items-center gap-2 px-4 py-2 bg-[#8cc63f]/10 border border-[#8cc63f]/30 rounded-full text-[#6a9a2f] text-[13px] font-bold shadow-sm';
            badge.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                <span>${screenCount} ressource(s) architecturale(s) sécurisée(s)</span>
            `;
            countContainer.appendChild(badge);

            statusEl.innerHTML = 'Moteur AetherFlow activé !';
            statusEl.className = 'mt-4 status-reward'; // Passage à 18px via CSS

            if (screenCount >= 1) {
                btn.disabled = false;
                btn.classList.add('success-badge');
            }
            if (window.WsProjectPanel) window.WsProjectPanel.refresh();
            triggerTokenExtraction();
        }
    }

    async function triggerTokenExtraction() {
        try {
            const session = getSession();
            const pid = session.active_project_id || session.project_id;
            if (!pid) return;
            await fetch('/api/imports/extract-tokens', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-User-Token': session.token || '' },
                body: JSON.stringify({ project_id: pid })
            });
        } catch(e) {
            console.warn('[WsStitchDrill] Token extraction failed:', e);
        }
    }

    async function renderInferenceStep() {
        const container = document.getElementById('drill-inference-container');
        if (!container) return;

        try {
            const session = getSession();
            const projectId = session.active_project_id || session.project_id;
            const res = await fetch(`/api/projects/${projectId}/manifest`, {
                headers: { 'X-User-Token': session.token || '' }
            });
            const m = res.ok ? await res.json() : {};
            const intent = m.intent_inference || null;

            if (!intent) {
                 container.innerHTML = `
                    <div class="bg-[#f8fafc] border border-[#e5e5e5] rounded-[16px] p-8 text-center">
                        <div class="w-8 h-8 border-4 border-[#8cc63f] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                        <div class="text-[14px] text-[#3d3d3c] font-bold">Analyse Sullivan en cours...</div>
                        <div class="text-[12px] text-[#9a9a98] mt-1">Extraction des signaux visuels de tes écrans</div>
                    </div>
                 `;
                 setTimeout(() => renderInferenceStep(), 3000);
                 return;
            }

            container.innerHTML = `
                <div class="bg-[#f8fafc] border-2 border-[#8cc63f] rounded-[24px] p-6 text-left animate-in zoom-in duration-500">
                    <div class="text-[11px] font-bold text-[#8cc63f] uppercase tracking-widest mb-3">Intelligence Sullivan</div>
                    <div class="text-[18px] font-black text-[#3d3d3c] mb-1">${intent.archetype}</div>
                    <div class="text-[13px] text-[#3d3d3c] leading-relaxed mb-4">${intent.description}</div>
                    <div class="space-y-2 pt-4 border-t border-[#8cc63f]/20">
                        <div class="text-[12px] text-[#9a9a98]">ambiance : <span class="text-[#3d3d3c] font-bold">${intent.mood.join(', ')}</span></div>
                        <div class="text-[12px] text-[#9a9a98]">sections : <span class="text-[#3d3d3c] font-bold">${intent.suggested_sections.join(', ')}</span></div>
                    </div>
                </div>
            `;

            document.getElementById('btn-drill-back-to-choice').onclick = () => { currentStep = 3; renderStep(); };
            document.getElementById('btn-drill-confirm-inference').onclick = () => createFromZero(intent, session);

        } catch(e) { container.innerHTML = "Erreur de chargement d'inférence."; }
    }

    async function loadManifestStep() {
        // Obsolete dans le flow linéaire, mais gardée pour compatibilité si besoin
    }

    async function createFromZero(intent, session) {
        if (!intent) {
            alert("Sullivan n'a pas encore fini l'analyse. Patiente quelques secondes...");
            return;
        }

        const projectId = session.active_project_id || session.project_id;
        const payload = {
            name: "Nouveau Projet",
            description: intent.description,
            archetype: intent.archetype,
            screens: intent.suggested_sections.map(s => ({ name: s, intent: s })),
            created_at: new Date().toISOString()
        };

        try {
            const res = await fetch(`/api/projects/${projectId}/manifest`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json', 'X-User-Token': session.token || '' },
                body: JSON.stringify(payload)
            });
            if (res.ok) {
                container.innerHTML = `
                    <div class="success-badge bg-[#8cc63f]/10 border-2 border-[#8cc63f] rounded-[24px] p-8 text-center animate-in zoom-in">
                        <div class="w-12 h-12 bg-[#8cc63f] rounded-full flex items-center justify-center text-white mx-auto mb-4 shadow-lg">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                        </div>
                        <div class="text-[18px] font-black text-[#3d3d3c] mb-1">Intention validée !</div>
                        <div class="text-[13px] text-[#9a9a98] mb-6">Sullivan a configuré ton manifest editor.</div>
                        <div id="drill-final-zone-zero"></div>
                    </div>
                `;
                _finishButton(document.getElementById('drill-final-zone-zero'));
            }
        } catch(e) { alert("erreur lors de la création"); }
    }

    function showManifestUpload(section, existingManifest, errorMsg) {
        section.innerHTML = `
            <div class="p-6 border-2 border-dashed border-[#e5e5e5] rounded-[20px] hover:border-[#8cc63f] transition-all cursor-pointer" id="drill-manifest-upload-zone">
                <div class="text-[26px] mb-2">↑</div>
                <div class="text-[14px] font-bold text-[#3d3d3c]">Glisser ton manifeste ici</div>
                <div class="text-[12px] text-[#9a9a98]">ou cliquer pour parcourir (.json, .md, .txt)</div>
                <input type="file" id="drill-manifest-input" class="hidden" accept=".json,.md,.txt">
            </div>
            <div id="drill-manifest-status" class="mt-3 text-[12px] text-[#9a9a98]"></div>
            <div id="drill-merge-zone" class="mt-4 hidden"></div>
            ${errorMsg ? '<div class="mt-2 text-[12px] text-[#d44]">' + errorMsg + '</div>' : ''}
        `;

        const zone = document.getElementById('drill-manifest-upload-zone');
        const input = document.getElementById('drill-manifest-input');
        const status = document.getElementById('drill-manifest-status');

        zone.onclick = () => input.click();
        zone.ondragover = (e) => { e.preventDefault(); zone.style.borderColor = '#8cc63f'; };
        zone.ondragleave = () => { zone.style.borderColor = '#e5e5e5'; };
        zone.ondrop = (e) => { e.preventDefault(); zone.style.borderColor = '#e5e5e5'; if (e.dataTransfer.files.length) uploadManifest(e.dataTransfer.files[0], status, existingManifest); };
        input.onchange = () => { if (input.files.length) uploadManifest(input.files[0], status, existingManifest); };
    }

    async function uploadManifest(file, statusEl, existingManifest) {
        try {
            const text = await file.text();
            const session = getSession();
            const projectId = session.active_project_id || session.project_id;
            let payload;
            if (file.name.endsWith('.json')) {
                payload = JSON.parse(text);
            } else {
                payload = { name: file.name.replace(/\.(md|txt)$/i, ''), description: text.substring(0, 500), raw_content: text, screens: [] };
            }

            // M354: Proposer la fusion si inférence disponible
            const intent = existingManifest ? existingManifest.intent_inference : null;
            if (intent) {
                const mergeZone = document.getElementById('drill-merge-zone');
                if (mergeZone) {
                    mergeZone.classList.remove('hidden');
                    mergeZone.innerHTML = `
                        <div class="p-4 bg-[#8cc63f]/10 border border-[#8cc63f]/30 rounded-[12px] flex items-center justify-between gap-3 animate-in zoom-in">
                            <div class="text-[12px] text-[#6a9a2f]">fusionner avec l'inférence Sullivan ?</div>
                            <button id="btn-drill-merge" class="px-4 py-1.5 bg-[#8cc63f] text-white rounded-[8px] text-[11px] font-bold">fusionner</button>
                        </div>
                    `;
                    document.getElementById('btn-drill-merge').onclick = async () => {
                        // Fusion simple : ajouter les suggested_sections si absentes
                        const currentScreens = (payload.screens || []).map(s => s.intent || s.name);
                        intent.suggested_sections.forEach(sec => {
                            if (!currentScreens.includes(sec)) {
                                payload.screens = payload.screens || [];
                                payload.screens.push({ name: sec, intent: sec });
                            }
                        });
                        payload.archetype = payload.archetype || intent.archetype;
                        payload.description = payload.description || intent.description;
                        await saveAndRefresh(projectId, payload, session, statusEl);
                    };
                }
            }

            await saveAndRefresh(projectId, payload, session, statusEl);

        } catch(e) { statusEl.textContent = 'Erreur: ' + e.message; statusEl.style.color = '#d44'; }
    }

    async function saveAndRefresh(projectId, payload, session, statusEl) {
        const res = await fetch(`/api/projects/${projectId}/manifest`, {
            method: 'PUT', headers: { 'X-User-Token': session.token || '', 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
        });
        if (!res.ok) { statusEl.textContent = 'Erreur (' + res.status + ')'; statusEl.style.color = '#d44'; return; }
        statusEl.innerHTML = `
            <div class="success-badge flex flex-col items-center justify-center gap-4 text-[#8cc63f] font-bold py-6">
                <div class="flex items-center gap-2">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    <span class="text-[16px]">Manifeste synchronisé !</span>
                </div>
                <div id="drill-final-zone-upload"></div>
            </div>
        `;
        _finishButton(document.getElementById('drill-final-zone-upload'));
    }

    async function loadForgedScreens() {
        const container = document.getElementById('drill-forged-screens');
        if (!container) return;
        try {
            const res = await fetch('/api/retro-genome/imports');
            const data = await res.json();
            const imports = data.imports || [];
            if (imports.length === 0) {
                container.innerHTML = '<div class="text-[13px] text-[#9a9a98] italic">Aucun écran forgé pour le moment.</div>';
                return;
            }
            container.innerHTML = imports.map(imp => `
                <div class="flex items-center gap-2 p-2 bg-[#f7f6f2] rounded-[8px]">
                    <div class="w-[34px] h-[34px] bg-[#e5e5e5] rounded-[6px] flex items-center justify-center text-[10px] text-[#9a9a98] font-bold">${imp.type || 'html'}</div>
                    <div class="flex-1 min-w-0">
                        <div class="text-[13px] font-bold text-[#3d3d3c] truncate">${imp.name || imp.id}</div>
                        <div class="text-[11px] text-[#9a9a98]">${imp.archetype_label || imp.archetype || 'import'}</div>
                    </div>
                </div>
            `).join('');
        } catch(e) { container.innerHTML = '<div class="text-[13px] text-[#9a9a98] italic">Erreur chargement.</div>'; }
        _finishButton(container);
    }

    function finishDrill() {
        if (overlay) { overlay.remove(); overlay = null; }
        if (window.WsProjectPanel) window.WsProjectPanel.refresh();
        if (window.ManifestBox) window.ManifestBox.show();
    }

    async function show() {
        const session = getSession();
        const role = session.role || 'student';
        if (role !== 'student') { console.log('[WsStitchDrill] Skipping for role:', role); return; }

        const projectId = session.active_project_id || session.project_id;
        if (projectId) {
            try {
                const res = await fetch(`/api/retro-genome/imports?project_id=${projectId}`, {
                    headers: { 'X-User-Token': session.token || '' }
                });
                if (res.ok) {
                    const data = await res.json();
                    const imports = data.imports || (Array.isArray(data) ? data : []);
                    if (imports.length > 0) {
                        console.log('[WsStitchDrill] Skipping — student has', imports.length, 'screen(s)');
                        return;
                    }
                }
            } catch(e) {
                console.warn('[WsStitchDrill] content check failed, showing drill anyway', e);
            }
        }

        createOverlay();
    }

    function hide() { if (overlay) { overlay.remove(); overlay = null; } }

    /**
     * Bouton "Commencer à travailler" unique — supprime tout existant et en crée un.
     * Appelé par loadManifestStep(), uploadManifest(), loadForgedScreens().
     */
    function _finishButton(container, prepend) {
        // Retirer tout bouton "Commencer" existant dans le container
        container.querySelectorAll('button').forEach(b => {
            if (b.textContent.includes('Commencer')) b.remove();
        });
        const btn = document.createElement('button');
        btn.id = 'drill-finish';
        btn.textContent = 'Commencer à travailler →';
        btn.className = 'success-badge px-10 py-4 bg-gradient-to-br from-[#8cc63f] via-[#7ab536] to-[#5a8a26] text-white text-[14px] font-extrabold uppercase tracking-widest rounded-[20px] shadow-[0_10px_25px_-5px_rgba(140,198,63,0.4)] hover:shadow-[0_15px_30px_-5px_rgba(140,198,63,0.6)] hover:-translate-y-0.5 transition-all cursor-pointer';
        btn.onclick = () => { hide(); if (window.ManifestBox) window.ManifestBox.show(); };
        if (prepend) container.insertBefore(btn, container.firstChild);
        else container.appendChild(btn);
        return btn;
    }

    window.WsStitchDrill = { show, hide };
    console.log('[WsStitchDrill] ✅ OK');
})();
