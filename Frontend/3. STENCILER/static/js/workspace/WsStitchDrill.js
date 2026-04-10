/**
 * WsStitchDrill — M280
 * Landing canvas + drill paramétrage Stitch (manifest → API keys → Stitch)
 */
(function() {
    'use strict';
    console.log('[WsStitchDrill] init');

    let overlay = null;
    let currentStep = 0;

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

    function createOverlay() {
        if (overlay) return;

        overlay = document.createElement('div');
        overlay.id = 'ws-stitch-drill-overlay';
        overlay.style.cssText = `
            position: fixed; inset: 0; z-index: 5000;
            background: rgba(247,246,242,0.95);
            display: flex; align-items: center; justify-content: center;
            flex-direction: column;
        `;

        document.body.appendChild(overlay);
        renderStep();
    }

    function renderStep() {
        if (!overlay) return;

        const steps = [
            // Step 0: Landing button
            {
                html: `
                    <button id="drill-start-btn" class="w-32 h-32 rounded-full bg-gradient-to-br from-[#8cc63f] to-[#6a9a2f] text-white font-bold text-[14px] uppercase tracking-widest shadow-lg hover:shadow-xl transition-all animate-pulse cursor-pointer"
                            style="animation: pulse 2s ease-in-out infinite; background: linear-gradient(135deg, #a3d960 0%, #8cc63f 30%, #7ab536 70%, #5a8a26 100%);">
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
            // Step 2: API Keys
            {
                html: `
                    <div class="text-center max-w-md">
                        <div class="text-[18px] font-bold text-[#3d3d3c] mb-2">Étape 2 — Clés API</div>
                        <div class="text-[11px] text-[#9a9a98] mb-4">Plus de clés = plus de chance de réussite. HomeOS utilise un fallback en cascade.</div>
                        <div class="bg-white border border-[#e5e5e5] rounded-[16px] p-4 mb-4 text-left">
                            <div class="text-[10px] font-bold text-[#3d3d3c] mb-2">Cascade active :</div>
                            <div class="text-[9px] text-[#9a9a98] space-y-1">
                                <div>1. Gemini → 2. Groq → 3. OpenAI → 4. DeepSeek</div>
                            </div>
                        </div>
                        <button id="drill-open-settings" class="px-6 py-2 bg-[#8cc63f] text-white text-[11px] font-bold rounded-[12px] hover:bg-[#7ab536] transition-all">
                            Ouvrir les paramètres (⚙)
                        </button>
                        <div class="mt-3 text-[10px] text-[#9a9a98]">Clique sur Continuer quand tu es prêt</div>
                        <button id="drill-continue-keys" class="mt-2 px-6 py-2 text-[11px] text-[#8cc63f] font-bold underline">Continuer →</button>
                    </div>
                `
            },
            // Step 3: Launch Stitch
            {
                html: `
                    <div class="text-center max-w-md">
                        <div class="text-[18px] font-bold text-[#3d3d3c] mb-2">Étape 3 — Lancer Stitch</div>
                        <div class="text-[11px] text-[#9a9a98] mb-6">HomeOS va créer ton projet Stitch et charger tes écrans. Laisse la page ouverte.</div>
                        <button id="drill-launch-stitch" class="px-8 py-3 bg-gradient-to-r from-[#8cc63f] to-[#6a9a2f] text-white text-[12px] font-bold uppercase tracking-wider rounded-[16px] hover:shadow-lg transition-all">
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
            document.getElementById('drill-open-settings').onclick = () => {
                // Open settings drawer
                const settingsToggle = document.getElementById('hn-settings-toggle');
                if (settingsToggle) settingsToggle.click();
            };
            document.getElementById('drill-continue-keys').onclick = () => {
                currentStep = 3;
                renderStep();
            };
        }
        else if (stepIndex === 3) {
            document.getElementById('drill-launch-stitch').onclick = launchStitchProject;
        }
    }

    async function handleManifestUpload(file, statusEl) {
        try {
            const text = await file.text();
            const session = JSON.parse(localStorage.getItem('homeos_session') || '{}');
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

            // Advance to next step after brief delay
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
            // Create Stitch project
            const res = await fetch('/api/stitch/create-project', { method: 'POST' });
            const data = await res.json();

            if (!res.ok) {
                text.textContent = 'Erreur: ' + (data.detail || 'inconnue');
                return;
            }

            bar.style.width = '50%';
            text.textContent = 'Projet créé — ouverture de Stitch...';

            // Open Stitch
            window.open(data.stitch_url || 'https://stitch.withgoogle.com', '_blank');

            bar.style.width = '80%';
            text.textContent = 'Stitch ouvert — charge tes écrans manuellement.';

            // Close drill overlay after delay
            setTimeout(() => {
                bar.style.width = '100%';
                text.textContent = '✓ Prêt ! Utilise ↻ dans la liste des écrans pour synchroniser.';
                setTimeout(() => {
                    if (overlay) {
                        overlay.style.display = 'none';
                        overlay = null;
                    }
                    // Refresh imports list
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
    console.log('[WsStitchDrill] ✅ OK');
})();