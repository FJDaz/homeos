/**
 * ManifestBox — Panneau manifest flottant cross-tabs (M269)
 * Accessible via bouton [M] dans le nav global (bootstrap.js)
 * Flotte par-dessus le contenu, positionné sous le nav, à droite.
 * Draggable depuis le header.
 */
(function() {
    'use strict';
    console.log('[ManifestBox] init');

    let panel = null;
    let manifestData = null;

    function isOpen() {
        return panel && panel.style.display !== 'none';
    }

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
            <div class="p-2 border-b border-[#e5e5e5] flex items-center justify-between bg-[#f7f6f2] shrink-0">
                <div class="flex items-center gap-2">
                    <div>
                        <div class="text-[8px] font-black uppercase tracking-widest text-[#9a9a98]">archétype</div>
                        <div class="text-[10px] font-bold text-[#3d3d3c]">${archetype}</div>
                    </div>
                </div>
                <div class="text-[8px] text-[#9a9a98]">${screens.length} écran(s)</div>
            </div>
            <div id="manifestbox-list" class="flex-1 overflow-y-auto p-2 space-y-1 no-scrollbar">
        `;

        screens.forEach((s, i) => {
            const name = s.name || s.id || `screen_${i}`;
            const type = s.type || s.archetype_label || 'html';
            const stitchId = s.stitch_id || s.stitch_screen_id || '';
            html += `
                <div class="p-2 bg-white border border-[#e5e5e5] rounded-[12px] text-[10px]">
                    <div class="font-bold text-[#3d3d3c]">${name}</div>
                    <div class="text-[8px] text-[#9a9a98]">${type}${stitchId ? ' · stitch: ' + stitchId : ''}</div>
                </div>
            `;
        });

        html += `</div>
            <div class="p-2 border-t border-[#e5e5e5] bg-[#f7f6f2] space-y-1.5 shrink-0">
                <button id="manifestbox-edit-btn" class="w-full py-1 border border-[#e5e5e5] bg-white text-[9px] font-bold uppercase tracking-wider text-[#3d3d3c] hover:border-[#8cc63f] transition-all rounded-[12px]">éditer</button>
                <button id="manifestbox-wire-btn" class="w-full py-1 bg-[#8cc63f] text-white text-[9px] font-bold uppercase tracking-wider hover:bg-[#7ab536] transition-all rounded-[12px]">envoyer au wire</button>
            </div>
        `;

        body.innerHTML = html;

        const editBtn = document.getElementById('manifestbox-edit-btn');
        if (editBtn) editBtn.onclick = showEditor;

        const wireBtn = document.getElementById('manifestbox-wire-btn');
        if (wireBtn) {
            wireBtn.onclick = () => {
                sessionStorage.setItem('manifest_for_wire', JSON.stringify(manifestData));
                window.location.href = '/workspace?tab=wire';
            };
        }

        if (title) title.textContent = `manifest · ${screens.length}`;
    }

    function showEditor() {
        const body = document.getElementById('manifestbox-body');
        if (!body) return;
        const json = JSON.stringify(manifestData, null, 2);
        body.innerHTML = `
            <textarea id="manifestbox-editor" class="w-full h-full bg-[#1a1a1a] text-[#e1e1e6] text-[9px] font-mono p-2 outline-none resize-none" spellcheck="false">${json.replace(/</g, '&lt;')}</textarea>
            <div class="p-2 border-t border-[#e5e5e5] bg-[#f7f6f2] shrink-0">
                <button id="manifestbox-save-btn" class="w-full py-1 bg-[#8cc63f] text-white text-[9px] font-bold uppercase tracking-wider hover:bg-[#7ab536] transition-all rounded-[12px]">sauvegarder</button>
            </div>
        `;
        document.getElementById('manifestbox-save-btn').onclick = saveManifest;
    }

    function buildPanel() {
        if (panel) return;

        panel = document.createElement('div');
        panel.id = 'manifestbox-panel';
        panel.style.cssText = `
            position: fixed;
            top: 56px;
            right: 20px;
            width: 320px;
            height: 480px;
            max-height: calc(100vh - 72px);
            z-index: 1500;
            background: white;
            border: 1px solid #e5e5e5;
            border-radius: 16px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.06);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        `;

        panel.innerHTML = `
            <div class="h-[32px] border-b border-[#e5e5e5] flex items-center justify-between px-3 shrink-0 bg-white" id="manifestbox-handle">
                <span id="manifestbox-title" class="text-[9px] font-black tracking-[0.15em] uppercase text-[#8cc63f]">manifest</span>
                <button id="manifestbox-close" class="text-[#9a9a98] hover:text-[#3d3d3c] transition-colors p-0.5">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
            </div>
            <div id="manifestbox-body" class="flex-1 overflow-hidden flex flex-col bg-white"></div>
        `;

        document.body.appendChild(panel);

        // Close
        panel.querySelector('#manifestbox-close').onclick = () => hide();

        // Drag depuis le header
        const handle = document.getElementById('manifestbox-handle');
        if (handle) {
            handle.style.cursor = 'grab';
            let dragging = false, ox = 0, oy = 0;
            handle.addEventListener('mousedown', (e) => {
                dragging = true;
                ox = e.clientX - panel.getBoundingClientRect().left;
                oy = e.clientY - panel.getBoundingClientRect().top;
                handle.style.cursor = 'grabbing';
                e.preventDefault();
            });
            document.addEventListener('mousemove', (e) => {
                if (!dragging) return;
                panel.style.left = (e.clientX - ox) + 'px';
                panel.style.top = (e.clientY - oy) + 'px';
                panel.style.right = 'auto';
            });
            document.addEventListener('mouseup', () => {
                dragging = false;
                handle.style.cursor = 'grab';
            });
        }
    }

    async function show() {
        buildPanel();
        panel.style.display = 'flex';
        await loadManifest();
        render();
    }

    function hide() {
        if (panel) panel.style.display = 'none';
    }

    function toggle() {
        if (isOpen()) hide(); else show();
    }

    window.ManifestBox = { show, hide, toggle };
    console.log('[ManifestBox] ✅ OK');
})();
