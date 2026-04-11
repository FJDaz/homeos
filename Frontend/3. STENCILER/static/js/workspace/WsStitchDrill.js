/**
 * WsStitchDrill — M280/M283/M291
 * Landing canvas + drill paramétrage Stitch (manifest → API keys → Stitch)
 * 
 * CORRECTIONS M283:
 * - Étape 2: champs de saisie des clés DANS le drill (pas dans le drawer)
 * - Vérification des clés configurées avant passage à l'étape 3
 * - Stitch bloqué si plan FREE ou aucune clé
 */
(function() {
    'use strict';
    console.log('[WsStitchDrill] init');

    let overlay = null;
    let currentStep = 0;
    let keyStatus = {}; // { gemini: 'set'|null, groq: 'set'|null, ... }

    const API_PROVIDERS = [
        { id: 'gemini', label: 'Gemini', free: true },
        { id: 'groq', label: 'Groq', free: true },
        { id: 'openai', label: 'OpenAI', free: false },
        { id: 'deepseek', label: 'DeepSeek', free: false },
        { id: 'qwen', label: 'Qwen', free: true },
    ];

    // Check if canvas is empty (no imports)
    async function isCanvasEmpty() {
        try {
            const res = await fetch('/api/retro-genome/imports');
            const data = await res.json();
            return (data.imports || []).length === 0;
        } catch(e) {
            return true;
        }
    }

    // Get session entitlements
    function getSession() {
        try {
            return JSON.parse(localStorage.getItem('homeos_session') || '{}');
        } catch(e) {
            return {};
        }
    }

    // Fetch current key status from backend
    async function fetchKeyStatus() {
        try {
            const session = getSession();
            const res = await fetch('/api/me/keys', {
                headers: { 'X-User-Token': session.token || '' }
            });
            if (res.ok) {
                keyStatus = await res.json();
            }
        } catch(e) {
            console.warn('[WsStitchDrill] Could not fetch key status:', e);
        }
        return keyStatus;
    }

    // Count configured keys
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

        const session = getSession();
        const plan = session.plan || 'FREE';
        const entitlements = session.entitlements || {};
        const canStitch = entitlements.can_use_stitch !== false && keyStatus['gemini'] !== 'set' ? false : true;

        const steps = [
            // Step 0: Landing button
            {
                html: `
                    <button id="drill-start-btn" class="w-32 h-32 rounded-full text-white font-bold text-[14px] uppercase tracking-widest shadow-lg hover:shadow-xl transition-all cursor-pointer"
                            style="background: linear-gradient(135deg, #a3d960 0%, #8cc63f 30%, #7ab536 70%, #5a8a26 100%); animation: pulse 2s ease-in-out infinite;">
                        Créer un<br>projet
                    </button>
                    <style>
                        @keyframes pulse {
                            0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(140,198,63,0.4); }
                            50% { transform: scale(1.05); box-shadow: 0 0 30px 10px rgba(140,198,63,0.2); }
                        }
                    </style>
                `,
                next: null
            },
            // Step 1: Upload manifest
            {
                html: `
                    <div class="text-center max-w-md">
                        <div class="text-[18px] font-bold text-[#3d3d3c] mb-2">Étape 1 — Manifeste</div>
                        <div class="text-[11px] text-[#9a9a98] mb-6">Charge ton manifeste produit (.json, .md ou .txt) pour définir l'ADN du projet.</div>
                        <div class="p-6 border-2 border-dashed border-[#e5e5e5] rounded-[20px] hover:border-[#8cc63f] transition-all cursor-pointer" id="drill-upload-zone">
                            <div class="text-[24px] mb-2">↑</div>
                            <div class="text-[12px] font-bold text-[#3d3d3c]">Glisser un fichier ici</div>
                            <div class="text-[10px] text-[#9a9a98]">ou cliquer pour parcourir</div>
                            <input type="file" id="drill-manifest-input" class="hidden" accept=".json,.md,.txt">
                        </div>
                        <div id="drill-manifest-status" class="mt-3 text-[10px] text-[#9a9a98]"></div>
                        <div class="mt-4 text-[10px] text-[#9a9a98]">Pas de manifeste ? <a href="/cadrage" class="text-[#8cc63f] underline">Va dans Cadrage pour en créer un</a></div>
                    </div>
                `
            },
            // Step 2: API Keys — WITH INPUT FIELDS
            {
                html: `
                    <div class="text-center max-w-md">
                        <div class="text-[18px] font-bold text-[#3d3d3c] mb-2">Étape 2 — Clés API</div>
                        <div class="text-[11px] text-[#9a9a98] mb-4">Au moins une clé est requise. HomeOS utilise un fallback en cascade si la première ne répond pas.</div>
                        <div class="bg-white border border-[#e5e5e5] rounded-[16px] p-4 mb-4 text-left space-y-3">
                            ${API_PROVIDERS.map(p => `
                                <div class="flex items-center gap-2">
                                    <div class="w-2 h-2 rounded-full ${keyStatus[p.id] === 'set' ? 'bg-[#8cc63f]' : 'bg-[#e5e5e5]'}"></div>
                                    <div class="flex-1">
                                        <div class="flex items-center gap-1">
                                            <span class="text-[10px] font-bold text-[#3d3d3c]">${p.label}</span>
                                            ${p.free ? '<span class="text-[8px] px-1 bg-[#8cc63f]/20 text-[#6a9a2f] rounded">gratuit</span>' : ''}
                                        </div>
                                        <input type="password" class="drill-key-input w-full mt-1 px-2 py-1.5 text-[11px] border border-[#e5e5e5] rounded-[8px] outline-none focus:border-[#8cc63f] transition-all" data-provider="${p.id}" placeholder="Clé ${p.label}..." value="">
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                        <div class="text-[10px] text-[#9a9a98] mb-3">
                            <span id="drill-key-count">${getActiveKeyCount()}</span> clé(s) configurée(s)
                            ${plan === 'FREE' ? ' — <span class="text-orange-500">Plan FREE (max 3 projets)</span>' : ''}
                        </div>
                        <button id="drill-continue-keys" class="px-8 py-2.5 bg-[#8cc63f] text-white text-[11px] font-bold rounded-[12px] hover:bg-[#7ab536] transition-all disabled:opacity-40 disabled:cursor-not-allowed" ${getActiveKeyCount() === 0 ? 'disabled' : ''}>
                            Continuer →
                        </button>
                    </div>
                `
            },
            // Step 3: Launch Stitch (with RBAC guard)
            {
                html: `
                    <div class="text-center max-w-md">
                        <div class="text-[18px] font-bold text-[#3d3d3c] mb-2">Étape 3 — Lancer Stitch</div>
                        ${plan === 'FREE' ? `
                            <div class="p-3 bg-orange-50 border border-orange-200 rounded-[12px] mb-4">
                                <div class="text-[11px] text-orange-600 font-bold">⚠ Plan FREE</div>
                                <div class="text-[10px] text-orange-500">Stitch nécessite un plan PRO. Upgrade pour accéder à toutes les fonctionnalités.</div>
                            </div>
                        ` : ''}
                        <div class="text-[11px] text-[#9a9a98] mb-6">HomeOS va créer ton projet Stitch et charger tes écrans. Laisse la page ouverte.</div>
                        <button id="drill-launch-stitch" class="px-8 py-3 bg-gradient-to-r from-[#8cc63f] to-[#6a9a2f] text-white text-[12px] font-bold uppercase tracking-wider rounded-[16px] hover:shadow-lg transition-all ${plan === 'FREE' ? 'opacity-40 cursor-not-allowed' : ''}" ${plan === 'FREE' ? 'disabled' : ''}>
                            Charger sur Stitch →
                        </button>
                        <div id="drill-progress" class="mt-4 hidden">
                            <div class="w-full bg-[#e5e5e5] rounded-full h-2 overflow-hidden">
                                <div id="drill-progress-bar" class="h-full bg-[#8cc63f] transition-all duration-500" style="width: 0%"></div>
                            </div>
                            <div id="drill-progress-text" class="text-[10px] text-[#9a9a98] mt-2">Création du projet Stitch...</div>
                        </div>
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
            document.getElementById('drill-start-btn').onclick = () => {
                currentStep = 1;
                renderStep();
            };
        }
        else if (stepIndex === 1) {
            const zone = document.getElementById('drill-upload-zone');
            const input = document.getElementById('drill-manifest-input');
            const status = document.getElementById('drill-manifest-status');

            zone.onclick = () => input.click();
            zone.ondragover = (e) => { e.preventDefault(); zone.style.borderColor = '#8cc63f'; };
            zone.ondragleave = () => { zone.style.borderColor = '#e5e5e5'; };
            zone.ondrop = (e) => {
                e.preventDefault();
                zone.style.borderColor = '#e5e5e5';
                if (e.dataTransfer.files.length) handleManifestUpload(e.dataTransfer.files[0], status);
            };
            input.onchange = () => { if (input.files.length) handleManifestUpload(input.files[0], status); };
        }
        else if (stepIndex === 2) {
            // Wire key inputs — save on Enter and blur
            document.querySelectorAll('.drill-key-input').forEach(input => {
                const provider = input.dataset.provider;
                
                input.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        saveKey(provider, input.value.trim());
                    }
                });
                
                input.addEventListener('blur', () => {
                    if (input.value.trim()) saveKey(provider, input.value.trim());
                });

                input.addEventListener('input', () => {
                    // Live update key count
                    const count = getActiveKeyCount() + (input.value.trim() ? 1 : 0);
                    const countEl = document.getElementById('drill-key-count');
                    if (countEl) countEl.textContent = count;
                    // Enable/disable continue button
                    const btn = document.getElementById('drill-continue-keys');
                    if (btn) btn.disabled = count === 0;
                });
            });

            document.getElementById('drill-continue-keys').onclick = () => {
                if (getActiveKeyCount() === 0) return;
                currentStep = 3;
                renderStep();
            };
        }
        else if (stepIndex === 3) {
            const launchBtn = document.getElementById('drill-launch-stitch');
            if (launchBtn && !launchBtn.disabled) {
                launchBtn.onclick = launchStitchProject;
            }
        }
    }

    async function saveKey(provider, key) {
        if (!key) return;
        try {
            const session = getSession();
            const res = await fetch('/api/me/keys', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-User-Token': session.token || ''
                },
                body: JSON.stringify({ provider, api_key: key })
            });
            if (res.ok) {
                keyStatus[provider] = 'set';
                // Update the dot
                const input = document.querySelector(`.drill-key-input[data-provider="${provider}"]`);
                if (input) {
                    input.value = '';
                    input.style.borderColor = '#8cc63f';
                    setTimeout(() => { input.style.borderColor = ''; }, 1500);
                    // Update dot
                    const dot = input.closest('.flex').querySelector('.rounded-full');
                    if (dot) dot.classList.remove('bg-[#e5e5e5]');
                    if (dot) dot.classList.add('bg-[#8cc63f]');
                }
                // Update count
                const count = getActiveKeyCount();
                const countEl = document.getElementById('drill-key-count');
                if (countEl) countEl.textContent = count;
                // Enable continue button
                const btn = document.getElementById('drill-continue-keys');
                if (btn && count > 0) btn.disabled = false;
            }
        } catch(e) {
            console.error('[WsStitchDrill] Key save error:', e);
        }
    }

    async function handleManifestUpload(file, statusEl) {
        try {
            const text = await file.text();
            const session = getSession();
            const projectId = session.active_project_id || session.project_id;

            let payload;
            if (file.name.endsWith('.json')) {
                payload = JSON.parse(text);
            } else {
                payload = {
                    name: file.name.replace(/\.(md|txt)$/i, ''),
                    description: text.substring(0, 500),
                    raw_content: text,
                    screens: [],
                    components: []
                };
            }

            const res = await fetch(`/api/projects/${projectId}/manifest`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                statusEl.textContent = 'Erreur sauvegarde (' + res.status + ')';
                statusEl.style.color = '#d44';
                return;
            }

            statusEl.textContent = '✓ Manifest sauvegardé';
            statusEl.style.color = '#8cc63f';

            setTimeout(() => {
                currentStep = 2;
                renderStep();
            }, 800);

        } catch(e) {
            statusEl.textContent = 'Erreur: ' + e.message;
            statusEl.style.color = '#d44';
        }
    }

    async function launchStitchProject() {
        const progress = document.getElementById('drill-progress');
        const bar = document.getElementById('drill-progress-bar');
        const text = document.getElementById('drill-progress-text');

        progress.classList.remove('hidden');
        bar.style.width = '10%';
        text.textContent = 'Création du projet Stitch...';

        try {
            const res = await fetch('/api/stitch/create-project', { method: 'POST' });
            const data = await res.json();

            if (!res.ok) {
                text.textContent = 'Erreur: ' + (data.detail || 'inconnue');
                return;
            }

            bar.style.width = '50%';
            text.textContent = 'Projet créé — ouverture de Stitch...';

            window.open(data.stitch_url || 'https://stitch.withgoogle.com', '_blank');

            bar.style.width = '80%';
            text.textContent = 'Stitch ouvert — charge tes écrans manuellement.';

            if (window.WsStitchSync) window.WsStitchSync.startPolling();

            setTimeout(() => {
                bar.style.width = '100%';
                text.textContent = '✓ Prêt ! Utilise ↻ dans la liste des écrans pour synchroniser.';
                setTimeout(() => {
                    if (overlay) {
                        overlay.style.display = 'none';
                        overlay = null;
                    }
                    if (window.WsImportList) window.WsImportList.refresh();
                }, 2000);
            }, 2000);

        } catch(e) {
            text.textContent = 'Erreur: ' + e.message;
        }
    }

    function show() {
        isCanvasEmpty().then(empty => {
            if (empty) {
                createOverlay();
            }
        });
    }

    function hide() {
        if (overlay) {
            overlay.style.display = 'none';
            overlay = null;
        }
    }

    window.WsStitchDrill = { show, hide };
    console.log('[WsStitchDrill] ✅ OK (with RBAC + key inputs)');
})();