/**
 * ManifestBox — Panneau manifest flottant cross-tabs (M269)
 * Accessible via bouton [M] dans le nav global (bootstrap.js)
 * Flotte par-dessus le contenu, positionné sous le nav, à gauche.
 * Upload exclusif depuis le panneau.
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
            if (res.status === 404) {
                manifestData = { error: `aucun manifest — upload un fichier .json ci-dessous` };
                return;
            }
            if (!res.ok) {
                manifestData = { error: `erreur serveur (${res.status})` };
                return;
            }
            manifestData = await res.json();
        } catch(e) {
            manifestData = { error: e.message };
        }
    }

    async function handleManifestUpload(file) {
        if (!file) return;
        try {
            const text = await file.text();
            const parsed = JSON.parse(text);
            const session = JSON.parse(localStorage.getItem('homeos_session') || '{}');
            const projectId = session.active_project_id || session.project_id;
            const res = await fetch(`/api/projects/${projectId}/manifest`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(parsed)
            });
            if (!res.ok) {
                alert('Erreur sauvegarde manifest: ' + res.status);
                return;
            }
            manifestData = parsed;
            render();
            const toast = document.createElement('div');
            toast.style.cssText = 'position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#3d3d3c;color:#fff;padding:12px 24px;border-radius:12px;font-size:12px;z-index:99999;';
            toast.textContent = '✓ Manifest mis à jour';
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 2000);
        } catch(e) {
            alert('Erreur: fichier JSON invalide — ' + e.message);
        }
    }

    function triggerUpload() {
        const fi = document.createElement('input');
        fi.type = 'file';
        fi.accept = '.json';
        fi.onchange = () => handleManifestUpload(fi.files[0]);
        fi.click();
    }

    function render() {
        const body = document.getElementById('manifestbox-body');
        const title = document.getElementById('manifestbox-title');
        if (!body) return;

        if (manifestData && manifestData.error) {
            // No manifest state: show upload button + error
            body.innerHTML = `
                <div class="flex-1 flex flex-col items-center justify-center p-6 text-center">
                    <div class="text-[11px] text-red-400 mb-4">${manifestData.error}</div>
                    <button id="manifestbox-upload-btn" class="px-4 py-2 bg-white border border-[#e5e5e5] rounded-[12px] text-[10px] font-bold text-[#3d3d3c] hover:border-[#8cc63f] hover:text-[#8cc63f] transition-all cursor-pointer">
                        ↑ Charger un manifest (.json)
                    </button>
                    <div class="text-[9px] text-[#9a9a98] mt-2">Requis pour Stitch</div>
                </div>
            `;
            document.getElementById('manifestbox-upload-btn').onclick = triggerUpload;
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
                <button id="manifestbox-upload-btn" class="text-[8px] text-slate-400 hover:text-[#8cc63f] transition-all cursor-pointer" title="Remplacer">↑ remplacer</button>
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

        html += `</div>`;
        body.innerHTML = html;
        document.getElementById('manifestbox-upload-btn').onclick = triggerUpload;

        if (title) title.textContent = `manifest · ${screens.length}`;
    }

    function buildPanel() {
        if (panel) return;

        panel = document.createElement('div');
        panel.id = 'manifestbox-panel';
        panel.style.cssText = `
            position: fixed;
            top: 60px;
            left: 340px;
            width: 300px;
            max-height: 480px;
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
        panel.querySelector('#manifestbox-close').onclick = hide;

        // Draggable
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

    window.ManifestBox = { show, hide, toggle, upload: triggerUpload };
    console.log('[ManifestBox] ✅ OK');
})();