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
                0% { transform: scale(1); opacity: 0.8; }
                100% { transform: scale(1.6); opacity: 0; }
            }
            @keyframes success-pop {
                0% { transform: scale(0.9); opacity: 0; }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); opacity: 1; }
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
                animation: pulse-low-cpu 2.5s infinite cubic-bezier(0.4, 0, 0.2, 1);
                pointer-events: none;
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
                                            <button class="drill-save-btn px-2 py-1.5 text-[13px] font-bold bg-[#8cc63f] text-white rounded-[8px] hover:bg-[#7ab536] transition-all whitespace-nowrap" data-provider="${p.id}">OK</button>
                                        </div>
                                        <div class="drill-helper-text mt-1 text-[13px] text-[#8cc63f] hidden" id="drill-helper-${p.id}"></div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                        <div class="text-[12px] text-[#9a9a98] mb-3"><span id="drill-key-count">${getActiveKeyCount()}</span> clé(s) configurée(s) — <span class="text-[#8cc63f]">💡 aussi dispo via ⚙</span></div>
                        <button id="drill-continue-keys" class="px-8 py-2.5 bg-[#8cc63f] text-white text-[13px] font-bold rounded-[12px] hover:bg-[#7ab536] transition-all">Continuer →</button>
                    </div>
                `
            },
            // Step 3: Manifest
            {
                html: `
                    <div class="text-center max-w-md">
                        <div class="text-[20px] font-bold text-[#3d3d3c] mb-2">Étape 3 — Manifeste</div>
                        <div class="text-[13px] text-[#9a9a98] mb-4">Le manifeste définit l'ADN de ton projet.</div>
                        <div id="drill-manifest-section">
                            <div class="text-[13px] text-[#9a9a98]">Chargement...</div>
                        </div>
                    </div>
                `
            },
            // Step 4: Forged screens
            {
                html: `
                    <div class="text-center max-w-md">
                        <div class="text-[20px] font-bold text-[#3d3d3c] mb-2">Étape 4 — Écrans forgés</div>
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
            loadManifestStep();
        }
        else if (stepIndex === 4) {
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
            await fetch('/api/imports/extract-tokens', { method: 'POST' });
        } catch(e) {
            console.warn('[WsStitchDrill] Token extraction failed:', e);
        }
    }

    async function loadManifestStep() {
        const section = document.getElementById('drill-manifest-section');
        if (!section) return;

        try {
            const session = getSession();
            const projectId = session.active_project_id || session.project_id;

            if (!projectId) {
                showManifestUpload(section, 'projet non trouvé dans la session');
                return;
            }

            const res = await fetch(`/api/projects/${projectId}/manifest`);

            if (res.ok) {
                const m = await res.json();
                const hasContent = m.raw_content || m.description || m.archetype || (m.screens && m.screens.length > 0);

                if (!hasContent) {
                    showManifestUpload(section);
                } else {
                    // Fetch design tokens too
                    let tokensHtml = '';
                    try {
                        const tokenRes = await fetch('/api/imports/design-tokens');
                        const tokenData = await tokenRes.json();
                        const tokens = tokenData.tokens || {};
                        const palette = tokens.colors?.palette || [];
                        if (palette.length > 0) {
                            tokensHtml = `
                                <div class="mt-3 pt-3 border-t border-[#e5e5e5]">
                                    <div class="text-[9px] font-bold text-[#9a9a98] uppercase tracking-wider mb-2">tokens extraits des écrans</div>
                                    <div class="flex gap-1 flex-wrap">
                                        ${palette.map(c => `<div class="w-6 h-6 rounded-[4px] border border-[#e5e5e5] cursor-pointer" style="background:${c}" title="${c}"></div>`).join('')}
                                    </div>
                                </div>
                            `;
                        }
                    } catch(e) {}

                    const name = m.name || 'Sans titre';
                    const desc = m.description || m.raw_content || '';
                    const archetype = m.archetype?.label || m.archetype || 'Studio HoméOS';
                    const finalScreenCount = Math.max((m.screens || []).length, screenCount);

                    section.innerHTML = `
                        <div class="success-badge bg-white border-2 border-[#8cc63f] rounded-[16px] p-5 mb-5 text-left text-[13px] text-[#3d3d3c] relative shadow-md">
                            <div class="absolute -top-3 -right-3 w-8 h-8 bg-[#8cc63f] rounded-full flex items-center justify-center text-white shadow-lg">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                            </div>
                            <div class="text-[10px] font-bold text-[#8cc63f] uppercase tracking-widest mb-1">Manifeste Validé</div>
                            <div class="font-bold text-[15px] mb-1">${name}</div>
                            ${desc ? '<div class="text-[#9a9a98] mb-3 text-[12px] leading-relaxed">' + desc.substring(0, 150) + '...</div>' : ''}
                            <div class="flex gap-4 text-[11px] text-[#9a9a98] font-medium">
                                <span class="bg-[#f7f6f2] px-2 py-0.5 rounded-full">Projet: ${archetype}</span>
                                <span class="bg-[#f7f6f2] px-2 py-0.5 rounded-full">Écrans: ${finalScreenCount}</span>
                            </div>
                            ${tokensHtml}
                        </div>
                    `;
                    _finishButton(section);
                }
            } else {
                showManifestUpload(section);
            }
        } catch(e) {
            showManifestUpload(section, 'Erreur: ' + e.message);
        }
    }

    function showManifestUpload(section, errorMsg) {
        section.innerHTML = `
            <div class="p-6 border-2 border-dashed border-[#e5e5e5] rounded-[20px] hover:border-[#8cc63f] transition-all cursor-pointer" id="drill-manifest-upload-zone">
                <div class="text-[26px] mb-2">↑</div>
                <div class="text-[14px] font-bold text-[#3d3d3c]">Glisser ton manifeste ici</div>
                <div class="text-[12px] text-[#9a9a98]">ou cliquer pour parcourir (.json, .md, .txt)</div>
                <input type="file" id="drill-manifest-input" class="hidden" accept=".json,.md,.txt">
            </div>
            <div id="drill-manifest-status" class="mt-3 text-[12px] text-[#9a9a98]"></div>
            ${errorMsg ? '<div class="mt-2 text-[12px] text-[#d44]">' + errorMsg + '</div>' : ''}
        `;

        const zone = document.getElementById('drill-manifest-upload-zone');
        const input = document.getElementById('drill-manifest-input');
        const status = document.getElementById('drill-manifest-status');

        zone.onclick = () => input.click();
        zone.ondragover = (e) => { e.preventDefault(); zone.style.borderColor = '#8cc63f'; };
        zone.ondragleave = () => { zone.style.borderColor = '#e5e5e5'; };
        zone.ondrop = (e) => { e.preventDefault(); zone.style.borderColor = '#e5e5e5'; if (e.dataTransfer.files.length) uploadManifest(e.dataTransfer.files[0], status); };
        input.onchange = () => { if (input.files.length) uploadManifest(input.files[0], status); };
        _finishButton(section);
    }

    async function uploadManifest(file, statusEl) {
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
            const res = await fetch(`/api/projects/${projectId}/manifest`, {
                method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
            });
            if (!res.ok) { statusEl.textContent = 'Erreur (' + res.status + ')'; statusEl.style.color = '#d44'; return; }
            statusEl.innerHTML = `
                <div class="success-badge flex items-center justify-center gap-2 text-[#8cc63f] font-bold py-2">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    <span>ADN du projet sauvegardé !</span>
                </div>
            `;
            loadManifestStep(); // Pour afficher le bloc validé
        } catch(e) { statusEl.textContent = 'Erreur: ' + e.message; statusEl.style.color = '#d44'; }
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

    function show() {
        const session = getSession();
        const role = session.role || 'student';
        if (role !== 'student') { console.log('[WsStitchDrill] Skipping for role:', role); return; }
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
