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
        { id: 'gemini', label: 'Gemini', free: true, price: 'Gratuit (15 RPM)' },
        { id: 'groq', label: 'Groq', free: true, price: 'Gratuit (quota limité)' },
        { id: 'openai', label: 'OpenAI', free: false, price: '~$0.005/1K tokens' },
        { id: 'deepseek', label: 'DeepSeek', free: false, price: '~$0.001/1K tokens' },
        { id: 'qwen', label: 'Qwen', free: true, price: 'Gratuit (quota généreux)' },
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
                                <div class="flex items-start gap-2" id="drill-key-row-${p.id}">
                                    <div class="w-2 h-2 mt-2 rounded-full ${keyStatus[p.id] === 'set' ? 'bg-[#8cc63f]' : 'bg-[#e5e5e5]'}"></div>
                                    <div class="flex-1">
                                        <div class="flex items-center gap-1">
                                            <span class="text-[12px] font-bold text-[#3d3d3c]">${p.label}</span>
                                            <span class="text-[11px] text-[#9a9a98] ml-1">${p.price}</span>
                                            <button class="drill-help-btn ml-1 text-[#9a9a98] hover:text-[#8cc63f] transition-all" data-provider="${p.id}" title="Trouver l'URL de la clé">
                                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                                            </button>
                                        </div>
                                        <input type="password" class="drill-key-input w-full mt-1 px-2 py-1.5 text-[12px] border border-[#e5e5e5] rounded-[8px] outline-none focus:border-[#8cc63f] transition-all" data-provider="${p.id}" placeholder="Clé ${p.label}..." value="">
                                        <div class="drill-helper-text mt-1 text-[11px] text-[#8cc63f] hidden" id="drill-helper-${p.id}"></div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                        <div class="text-[10px] text-[#9a9a98] mb-3">
                            <span id="drill-key-count">${getActiveKeyCount()}</span> clé(s) configurée(s)
                            <span class="text-[#8cc63f] ml-2">💡 Tu peux aussi configurer tes clés via le bouton ⚙ dans la barre de navigation</span>
                        </div>
                        <button id="drill-continue-keys" class="px-8 py-2.5 bg-[#8cc63f] text-white text-[11px] font-bold rounded-[12px] hover:bg-[#7ab536] transition-all disabled:opacity-40 disabled:cursor-not-allowed" ${getActiveKeyCount() === 0 ? 'disabled' : ''}>
                            Continuer →
                        </button>
                    </div>
                `
            },
            // Step 3: Screens upload (1-4)
            {
                html: `
                    <div class="text-center max-w-md">
                        <div class="text-[18px] font-bold text-[#3d3d3c] mb-2">Étape 3 — Écrans</div>
                        <div class="text-[11px] text-[#9a9a98] mb-4">Charge 1 à 4 écrans (PNG, SVG, JPG) pour démarrer ton projet.</div>
                        <div class="p-6 border-2 border-dashed border-[#e5e5e5] rounded-[20px] hover:border-[#8cc63f] transition-all cursor-pointer" id="drill-screen-upload-zone">
                            <div class="text-[24px] mb-2">↑</div>
                            <div class="text-[12px] font-bold text-[#3d3d3c]">Glisser tes écrans ici</div>
                            <div class="text-[10px] text-[#9a9a98]">ou cliquer pour parcourir</div>
                            <input type="file" id="drill-screen-input" class="hidden" accept=".png,.svg,.jpg,.jpeg" multiple>
                        </div>
                        <div id="drill-screen-status" class="mt-3 text-[10px] text-[#9a9a98]"></div>
                        <div class="mt-2 text-[10px] text-[#9a9a98]" id="drill-screen-count">0 écran(s) chargé(s) — min. 1 requis</div>
                        <button id="drill-continue-screens" class="mt-4 px-8 py-2.5 bg-[#8cc63f] text-white text-[11px] font-bold rounded-[12px] hover:bg-[#7ab536] transition-all disabled:opacity-40 disabled:cursor-not-allowed" disabled>
                            Continuer →
                        </button>
                    </div>
                `
            },
            // Step 4: Manifest editor (simple — full editor later)
            {
                html: `
                    <div class="text-center max-w-md">
                        <div class="text-[18px] font-bold text-[#3d3d3c] mb-2">Étape 4 — Manifeste</div>
                        <div class="text-[11px] text-[#9a9a98] mb-4">Le manifeste définit l'ADN de ton projet. Tu peux le modifier plus tard.</div>
                        <div id="drill-manifest-preview" class="bg-white border border-[#e5e5e5] rounded-[16px] p-4 mb-4 text-left text-[11px] text-[#3d3d3c] max-h-48 overflow-y-auto">
                            <em class="text-[#9a9a98]">Chargement du manifeste...</em>
                        </div>
                        <button id="drill-finish" class="px-8 py-3 bg-gradient-to-r from-[#8cc63f] to-[#6a9a2f] text-white text-[12px] font-bold uppercase tracking-wider rounded-[16px] hover:shadow-lg transition-all">
                            Commencer à travailler →
                        </button>
                    </div>
                `
            }
        ];

        const step = steps[currentStep];
        overlay.innerHTML = step.html;
        wireStep(currentStep);
    }

    let screenCount = 0;
    let uploadedScreens = [];

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
            // Wire help buttons (?)
            document.querySelectorAll('.drill-help-btn').forEach(btn => {
                btn.onclick = async (e) => {
                    e.stopPropagation();
                    const provider = btn.dataset.provider;
                    const helperEl = document.getElementById(`drill-helper-${provider}`);
                    if (!helperEl) return;

                    helperEl.textContent = 'Recherche de l\'URL...';
                    helperEl.classList.remove('hidden');
                    helperEl.style.color = '#9a9a98';

                    try {
                        const res = await fetch(`/api/me/keys/helper/${provider}`);
                        if (!res.ok) throw new Error('API erreur');
                        const data = await res.json();
                        if (data.url) {
                            helperEl.innerHTML = `<a href="${data.url}" target="_blank" style="text-decoration:underline;color:#8cc63f;" class="font-bold">→ ${data.instructions}</a>`;
                            helperEl.style.color = '#8cc63f';
                        } else {
                            helperEl.textContent = 'URL non trouvée.';
                            helperEl.style.color = '#d44';
                        }
                    } catch(err) {
                        helperEl.textContent = 'Erreur de recherche.';
                        helperEl.style.color = '#d44';
                    }
                };
            });

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
                    const count = getActiveKeyCount() + (input.value.trim() ? 1 : 0);
                    const countEl = document.getElementById('drill-key-count');
                    if (countEl) countEl.textContent = count;
                    const btn = document.getElementById('drill-continue-keys');
                    if (btn) btn.disabled = count === 0;
                });
            });

            document.getElementById('drill-continue-keys').onclick = () => {
                if (getActiveKeyCount() === 0) return;
                currentStep = 3;
                screenCount = 0;
                uploadedScreens = [];
                renderStep();
            };
        }
        else if (stepIndex === 3) {
            // Step 3: Screen upload
            const zone = document.getElementById('drill-screen-upload-zone');
            const input = document.getElementById('drill-screen-input');
            const status = document.getElementById('drill-screen-status');
            const countEl = document.getElementById('drill-screen-count');
            const btn = document.getElementById('drill-continue-screens');

            zone.onclick = () => input.click();
            zone.ondragover = (e) => { e.preventDefault(); zone.style.borderColor = '#8cc63f'; };
            zone.ondragleave = () => { zone.style.borderColor = '#e5e5e5'; };
            zone.ondrop = (e) => {
                e.preventDefault();
                zone.style.borderColor = '#e5e5e5';
                if (e.dataTransfer.files.length) handleScreenUpload(e.dataTransfer.files, status, countEl, btn);
            };
            input.onchange = () => { if (input.files.length) handleScreenUpload(input.files, status, countEl, btn); };
        }
        else if (stepIndex === 4) {
            // Step 4: Manifest preview
            loadManifestPreview();
            document.getElementById('drill-finish').onclick = finishDrill;
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

    async function handleScreenUpload(files, statusEl, countEl, btn) {
        const session = getSession();
        const projectId = session.active_project_id || session.project_id;

        let uploaded = 0;
        statusEl.textContent = 'Upload en cours...';
        statusEl.style.color = '#8cc63f';

        for (const file of files) {
            if (uploaded >= 4) break;
            try {
                const formData = new FormData();
                formData.append('file', file);
                formData.append('filename', file.name);

                const res = await fetch('/api/import/upload', {
                    method: 'POST',
                    body: formData
                });

                if (!res.ok) {
                    statusEl.textContent = 'Erreur upload (' + res.status + ')';
                    statusEl.style.color = '#d44';
                    return;
                }

                uploaded++;

            } catch(e) {
                statusEl.textContent = 'Erreur: ' + e.message;
                statusEl.style.color = '#d44';
                return;
            }
        }

        if (uploaded > 0) {
            screenCount += uploaded;
            countEl.textContent = screenCount + ' écran(s) chargé(s) — min. 1 requis';
            statusEl.textContent = '✓ ' + uploaded + ' écran(s) uploadé(s)';
            statusEl.style.color = '#8cc63f';

            if (screenCount >= 1) btn.disabled = false;

            // Refresh imports list
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
                const manifest = await res.json();
                const name = manifest.name || 'Sans titre';
                const screens = (manifest.screens || []).length;
                const components = (manifest.components || []).length;
                const archetype = manifest.archetype?.label || manifest.archetype || '—';
                const desc = manifest.description || '';

                preview.innerHTML = `
                    <div class="font-bold text-[12px] mb-1">${name}</div>
                    ${desc ? '<div class="text-[#9a9a98] mb-2">' + desc.substring(0, 200) + '</div>' : ''}
                    <div class="flex gap-3 text-[9px] text-[#9a9a98]">
                        <span>Archétype: ${archetype}</span>
                        <span>Écrans: ${screens}</span>
                        <span>Composants: ${components}</span>
                    </div>
                `;
            } else {
                preview.innerHTML = '<em class="text-[#9a9a98]">Aucun manifeste trouvé — tu pourras le créer plus tard depuis le canvas.</em>';
            }
        } catch(e) {
            preview.innerHTML = '<em class="text-[#9a9a98]">Erreur chargement manifeste</em>';
        }
    }

    function finishDrill() {
        if (overlay) {
            overlay.style.display = 'none';
            overlay = null;
        }
        if (window.WsImportList) window.WsImportList.refresh();
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
        const session = getSession();
        const role = session.role || 'student';

        // Teachers and admins skip the drill — they have access to all class projects
        if (role !== 'student') {
            console.log('[WsStitchDrill] Skipping drill for role:', role);
            return;
        }

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