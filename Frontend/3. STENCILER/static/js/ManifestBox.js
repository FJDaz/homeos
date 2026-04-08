/**
 * ManifestBox — Drawer manifest persistante cross-tabs (M269)
 * Accessible via bouton [M] dans le nav global (bootstrap.js)
 */
(function() {
    'use strict';
    console.log('[ManifestBox] init');

    let overlay = null;
    let manifestData = null;
    let isOpen = localStorage.getItem('manifest_drawer_open') === 'true';

    async function loadManifest() {
        try {
            const session = JSON.parse(localStorage.getItem('homeos_session') || '{}');
            const projectId = session.active_project_id || session.project_id;
            if (!projectId) {
                manifestData = { error: 'aucun projet actif' };
                return;
            }
            const res = await fetch(`/api/projects/${projectId}/manifest`);
            if (!res.ok) {
                manifestData = { error: `manifest non trouvé (${res.status})` };
                return;
            }
            manifestData = await res.json();
        } catch(e) {
            manifestData = { error: e.message };
        }
    }

    async function saveManifest() {
        const textarea = document.getElementById('manifestbox-editor');
        if (!textarea) return;
        try {
            const parsed = JSON.parse(textarea.value);
            const session = JSON.parse(localStorage.getItem('homeos_session') || '{}');
            const projectId = session.active_project_id || session.project_id;
            const res = await fetch(`/api/projects/${projectId}/manifest`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(parsed)
            });
            if (res.ok) {
                manifestData = parsed;
                render();
            } else {
                alert('Erreur sauvegarde manifest');
            }
        } catch(e) {
            alert('JSON invalide: ' + e.message);
        }
    }

    function render() {
        const body = document.getElementById('manifestbox-body');
        const title = document.getElementById('manifestbox-title');
        if (!body) return;

        if (manifestData && manifestData.error) {
            body.innerHTML = `<div class="p-4 text-[11px] text-red-400">${manifestData.error}</div>`;
            return;
        }

        const screens = manifestData?.screens || manifestData?.components || [];
        const archetype = manifestData?.archetype?.label || manifestData?.archetype || '—';

        let html = `
            <div class="p-3 border-b border-[#e5e5e5] flex items-center justify-between bg-[#f7f6f2]">
                <div>
                    <div class="text-[9px] font-black uppercase tracking-widest text-[#9a9a98]">archétype</div>
                    <div class="text-[11px] font-bold text-[#3d3d3c]">${archetype}</div>
                </div>
                <div class="text-[9px] text-[#9a9a98]">${screens.length} écran(s)</div>
            </div>
            <div class="flex-1 overflow-y-auto p-2 space-y-1 no-scrollbar">
        `;

        screens.forEach((s, i) => {
            const name = s.name || s.id || `screen_${i}`;
            const type = s.type || s.archetype_label || 'html';
            const stitchId = s.stitch_id || s.stitch_screen_id || '';
            html += `
                <div class="p-2 bg-white border border-[#e5e5e5] rounded-[12px] text-[11px]">
                    <div class="font-bold text-[#3d3d3c]">${name}</div>
                    <div class="text-[9px] text-[#9a9a98]">${type}${stitchId ? ' · stitch: ' + stitchId : ''}</div>
                </div>
            `;
        });

        html += `</div>
            <div class="p-3 border-t border-[#e5e5e5] bg-[#f7f6f2] space-y-2">
                <button id="manifestbox-edit-btn" class="w-full py-1.5 border border-[#e5e5e5] bg-white text-[10px] font-bold uppercase tracking-wider text-[#3d3d3c] hover:border-[#8cc63f] transition-all rounded-[20px]">éditer le manifest</button>
                <button id="manifestbox-wire-btn" class="w-full py-1.5 bg-[#8cc63f] text-white text-[10px] font-bold uppercase tracking-wider hover:bg-[#7ab536] transition-all rounded-[20px]">envoyer au wire</button>
            </div>
        `;

        body.innerHTML = html;

        // Edit button
        const editBtn = document.getElementById('manifestbox-edit-btn');
        if (editBtn) {
            editBtn.onclick = showEditor;
        }

        // Wire button
        const wireBtn = document.getElementById('manifestbox-wire-btn');
        if (wireBtn) {
            wireBtn.onclick = () => {
                sessionStorage.setItem('manifest_for_wire', JSON.stringify(manifestData));
                window.location.href = '/workspace?tab=wire';
            };
        }

        title.textContent = `manifest · ${screens.length} écran(s)`;
    }

    function showEditor() {
        const body = document.getElementById('manifestbox-body');
        if (!body) return;
        const json = JSON.stringify(manifestData, null, 2);
        body.innerHTML = `
            <textarea id="manifestbox-editor" class="w-full h-full flex-1 bg-[#1a1a1a] text-[#e1e1e6] text-[10px] font-mono p-3 outline-none resize-none" spellcheck="false">${json.replace(/</g, '&lt;')}</textarea>
            <div class="p-3 border-t border-[#e5e5e5] bg-[#f7f6f2]">
                <button id="manifestbox-save-btn" class="w-full py-1.5 bg-[#8cc63f] text-white text-[10px] font-bold uppercase tracking-wider hover:bg-[#7ab536] transition-all rounded-[20px]">sauvegarder</button>
            </div>
        `;
        document.getElementById('manifestbox-save-btn').onclick = saveManifest;
    }

    function buildOverlay() {
        if (overlay) return;

        overlay = document.createElement('div');
        overlay.id = 'manifestbox-overlay';
        overlay.className = 'fixed inset-0 z-[8000] pointer-events-none';
        overlay.innerHTML = `
            <div id="manifestbox-drawer" class="absolute right-0 top-[48px] bottom-0 w-[360px] bg-white border-l border-[#e5e5e5] shadow-[-4px_0_16px_rgba(0,0,0,0.06)] flex flex-col pointer-events-auto transform transition-transform duration-200 ${isOpen ? 'translate-x-0' : 'translate-x-full'}">
                <!-- Header -->
                <div class="h-[40px] border-b border-[#e5e5e5] flex items-center justify-between px-4 shrink-0">
                    <span id="manifestbox-title" class="text-[10px] font-black tracking-[0.15em] uppercase text-[#8cc63f]">manifest</span>
                    <button id="manifestbox-close" class="text-[#9a9a98] hover:text-[#3d3d3c] transition-colors p-1">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                    </button>
                </div>
                <!-- Body -->
                <div id="manifestbox-body" class="flex-1 overflow-hidden flex flex-col"></div>
            </div>
        `;

        document.body.appendChild(overlay);

        // Close button
        document.getElementById('manifestbox-close').onclick = () => hide();

        // Click outside to close
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) hide();
        });

        // Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && isOpen) hide();
        });

        if (isOpen) loadManifest().then(render);
    }

    async function show() {
        buildOverlay();
        const drawer = document.getElementById('manifestbox-drawer');
        if (drawer) drawer.classList.remove('translate-x-full');
        isOpen = true;
        localStorage.setItem('manifest_drawer_open', 'true');
        await loadManifest();
        render();
    }

    function hide() {
        const drawer = document.getElementById('manifestbox-drawer');
        if (drawer) drawer.classList.add('translate-x-full');
        isOpen = false;
        localStorage.setItem('manifest_drawer_open', 'false');
        setTimeout(() => {
            if (overlay) { overlay.remove(); overlay = null; }
        }, 200);
    }

    function toggle() {
        if (isOpen) hide(); else show();
    }

    window.ManifestBox = { show, hide, toggle };
    console.log('[ManifestBox] ✅ OK');
})();
