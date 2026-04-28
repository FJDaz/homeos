/**
 * WsScreenShell.js — SVG Component Factory for Workspace Screens (Mission 156)
 */
class WsScreenShell {
    /**
     * Construit le groupe SVG complet pour un écran.
     */
    static async build(item, canvas) {
        const id = `shell-${item.id}`;
        
        const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
        g.setAttribute('id', id);
        g.setAttribute('class', 'ws-screen-shell');

        // Hover events (Mission 149)
        g.addEventListener('mouseenter', () => {
            if (!g.classList.contains('ws-selected')) g.classList.add('ws-hover');
        });
        g.addEventListener('mouseleave', () => g.classList.remove('ws-hover'));
        
        // Dimensions : desktop (HTML direct uploadé) vs mobile (SVG/forged)
        const isHtml = item.type === 'html' || (item.html_template && item.elements_count === 0);
        const SW = isHtml ? 1200 : 400;
        const SH = isHtml ? 800 : 632;

        // Positioning (Centered on scale 1.0)
        const svgRect = canvas.svg.getBoundingClientRect();
        const centerX = (svgRect.width/2 - SW/2 - canvas.viewX) / canvas.scale;
        const centerY = (svgRect.height/2 - SH/2 - canvas.viewY) / canvas.scale;
        g.setAttribute('transform', `matrix(1 0 0 1 ${centerX} ${centerY})`);

        // 1. Background
        const bg = this._createElement('rect', {
            'width': String(SW), 'height': String(SH), 'rx': '20',
            'fill': '#fff', 'stroke': '#f0f0f0', 'stroke-width': '1', 'class': 'ws-screen-bg'
        });
        g.appendChild(bg);

        // 2. Header
        const header = this._createElement('rect', {
            'width': String(SW), 'height': '40', 'rx': '20',
            'class': 'ws-screen-header', 'fill': 'transparent', 'pointer-events': 'all'
        });
        header.style.cursor = 'move';
        g.appendChild(header);

        // M237: Gripper visuel centré
        const grip = this._createElement('text', {
            x: String(SW / 2), y: '26', 'text-anchor': 'middle',
            fill: '#d1d5db',
            style: 'font-size:13px; letter-spacing:5px; pointer-events:none; user-select:none;'
        });
        grip.textContent = '⋯';
        g.appendChild(grip);

        // 3. Title
        const title = this._createElement('text', {
            'x': '20', 'y': '25', 'class': 'ws-screen-title'
        });
        title.textContent = (item.name || 'Sans titre').toLowerCase();
        g.appendChild(title);

        // 4. Badges (Origin)
        if (item.origin) {
            const badgeFo = this._createForeignObject(String(25 + (item.name || '').length * 7), '12', '300', '20');
            const badgeDiv = document.createElement('div');
            if (item.origin === 'generated') {
                badgeDiv.innerHTML = `<span style="background:#f0fdf4; color:#16a34a; border:1px solid #bbf7d0; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:600; white-space:nowrap;">Tailwind généré — peut différer du rendu exact</span>`;
            } else if (item.origin === 'compiled') {
                badgeDiv.innerHTML = `<span style="background:#f8fafc; color:#64748b; border:1px solid #e2e8f0; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:600; white-space:nowrap;">build compilé</span>`;
            }
            badgeFo.appendChild(badgeDiv);
            g.appendChild(badgeFo);
        }

        // 5. Close Button
        const closeBtn = this._createElement('circle', {
            'cx': String(SW - 20), 'cy': '20', 'r': '8', 'class': 'ws-btn-close', 'pointer-events': 'all'
        });
        closeBtn.addEventListener('mousedown', (e) => { e.stopPropagation(); g.remove(); });
        g.appendChild(closeBtn);

        // 6. Manifest & Cadrage Check (Mission 146/147)
        try {
            const res = await fetch(`/api/frd/manifest?import_id=${item.id}`);
            const data = await res.json();
            if (data.exists) {
                g.dataset.manifest = JSON.stringify(data.manifest);
                g.dataset.hasManifest = "true";
            } else {
                g.dataset.hasManifest = "false";
                const badgeFo = this._createForeignObject('20', String(SH - 35), '180', '30');
                const badgeDiv = document.createElement('div');
                badgeDiv.innerHTML = `<span style="background:#fff7ed; color:#c2410c; border:1px solid #ffedd5; padding:4px 8px; border-radius:6px; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:0.02em; display:flex; align-items:center; gap:6px; width:fit-content;">
                    <span style="width:6px; height:6px; border-radius:50%; background:#f97316;"></span>
                    cadrage requis
                </span>`;
                badgeFo.appendChild(badgeDiv);
                g.appendChild(badgeFo);
            }
        } catch (_) {}

        // 7. iFrame
        const fo = this._createForeignObject('0', '40', String(SW), String(SH - 40), { 'pointer-events': 'none' });
        const iframe = document.createElement('iframe');
        iframe.style.cssText = 'width:100%; height:100%; border:none; border-radius:0 0 20px 20px; background:#fff; pointer-events:none;';
        iframe.addEventListener('load', () => {
            if (window.wsFontManager) window.wsFontManager.injectStyles();
            // M237: Inject hover engine into iframe
            if (window.wsCanvas) window.wsCanvas.injectHoverEngine(iframe);
        });
        // dist compilé : URL statique directe → assets relatifs du bundle résolus correctement
        // sinon : passage par frd/file (éditable Sullivan)
        if (item.dist_url) {
            iframe.src = item.dist_url;
        } else if (item.html_template) {
            iframe.src = `/api/frd/file?name=${encodeURIComponent(item.html_template)}&raw=1`;
        } else if (item.type === 'png' && item.file_path) {
            // M368: Affichage du PNG brut sur le canvas
            const imgUrl = `/api/projects/${item.project_id}/imports/${item.file_path}`;
            iframe.srcdoc = `<html><body style="margin:0;padding:0;overflow:hidden;background:#fff;display:flex;align-items:center;justify-content:center;height:100vh;"><img src="${imgUrl}" style="max-width:100%;max-height:100%;object-fit:contain;display:block;"></body></html>`;
        }
        fo.appendChild(iframe);
        g.appendChild(fo);

        // 10. Resize Handle (Mission 114)
        const resizeHandle = this._createElement('rect', {
            'x': String(SW - 12), 'y': String(SH - 12), 'width': '12', 'height': '12',
            'class': 'ws-resize-handle', 'pointer-events': 'all'
        });
        g.appendChild(resizeHandle);

        // 8. Tool Buttons (Aperçu, Wire, Save, Download)
        this._addToolButtons(g, item, SW);

        // 9. Forge Overlay (si pas d'HTML template)
        if (!item.html_template) {
            this._addForgeOverlay(g, item);
        }

        return g;
    }

    // --- HELPERS ---

    static _createElement(tag, attrs = {}) {
        const el = document.createElementNS("http://www.w3.org/2000/svg", tag);
        for (let k in attrs) el.setAttribute(k, attrs[k]);
        return el;
    }

    static _createForeignObject(x, y, w, h, attrs = {}) {
        const fo = this._createElement('foreignObject', { x, y, width: w, height: h, ...attrs });
        return fo;
    }

    static _addToolButtons(g, item, SW) {
        // Wire
        const wireFo = this._createForeignObject(String(SW - 340), '8', '90', '24', { 
            'pointer-events': 'all', 'data-right-offset': '340', 'class': 'ws-shell-tool'
        });
        wireFo.style.display = g.dataset.hasManifest === "true" ? 'block' : 'none';
        const wireDiv = document.createElement('div');
        wireDiv.style.cssText = 'height:100%;';
        wireDiv.className = "flex items-center space-x-2 text-homeos-green cursor-pointer hover:opacity-80 transition-opacity";
        wireDiv.innerHTML = `<span style="font-size:12px; font-weight:800; border:1px solid #A3CD54; padding:2px 6px; border-radius:4px; text-transform:uppercase; letter-spacing:0.05em;">Wire</span>`;
        wireDiv.addEventListener('mousedown', (e) => e.stopPropagation());
        wireDiv.addEventListener('click', (e) => { e.stopPropagation(); window.wsCanvas.selectScreen(g); window.wsPreview?.enterPreviewMode(g.id, 'wire'); });
        wireFo.appendChild(wireDiv);
        g.appendChild(wireFo);

        // Aperçu
        const previewFo = this._createForeignObject(String(SW - 240), '8', '90', '24', { 
            'pointer-events': 'all', 'data-right-offset': '240', 'class': 'ws-shell-tool'
        });
        const previewDiv = document.createElement('div');
        previewDiv.className = "flex items-center space-x-2 text-slate-500 cursor-pointer hover:text-slate-800 transition-colors";
        previewDiv.style.cssText = 'height:100%;';
        previewDiv.innerHTML = `<span style="font-size:12px; font-weight:600; background:rgba(0,0,0,0.03); padding:2px 6px; border-radius:4px; text-transform:uppercase; letter-spacing:0.02em;">Aperçu</span>`;
        previewDiv.addEventListener('mousedown', (e) => e.stopPropagation());
        previewDiv.addEventListener('click', (e) => { e.stopPropagation(); window.wsCanvas.selectScreen(g); window.wsPreview?.enterPreviewMode(g.id, 'construct'); });
        previewFo.appendChild(previewDiv);
        g.appendChild(previewFo);

        // Save
        const saveFo = this._createForeignObject(String(SW - 140), '8', '55', '24', { 
            'pointer-events': 'all', 'data-right-offset': '140', 'class': 'ws-shell-tool'
        });
        const saveBtn = document.createElement('button');
        saveBtn.style.cssText = "width:100%; height:100%; line-height:1; background:#8cc63f; color:#fff; border:none; border-radius:4px; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; cursor:pointer;";
        saveBtn.innerText = "SAVE";
        saveBtn.addEventListener('mousedown', (e) => e.stopPropagation());
        saveBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            saveBtn.innerText = '...'; saveBtn.style.opacity = '0.6';
            try {
                const iframeEl = g.querySelector('iframe');
                const html = iframeEl?._lastSullivanHtml || iframeEl?.contentDocument?.documentElement?.outerHTML || iframeEl?.srcdoc || '';
                const name = item.html_template || (item.name + '.html');
                await fetch('/api/frd/file', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name, content: html, force: true }) });
                saveBtn.innerText = '✓';
                setTimeout(() => { saveBtn.innerText = 'SAVE'; saveBtn.style.opacity = '1'; }, 1500);
            } catch (_) { saveBtn.innerText = 'ERR'; saveBtn.style.opacity = '1'; }
        });
        saveFo.appendChild(saveBtn);
        g.appendChild(saveFo);

        // Download
        const downloadFo = this._createForeignObject(String(SW - 75), '8', '24', '24', { 
            'pointer-events': 'all', 'data-right-offset': '75', 'class': 'ws-shell-tool'
        });
        const dlBtn = document.createElement('button');
        dlBtn.className = "flex items-center justify-center text-slate-400 hover:text-homeos-green transition-colors";
        dlBtn.style.cssText = "width:100%; height:100%; background:none; border:none; cursor:pointer;";
        dlBtn.innerHTML = `<svg fill="none" height="16" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24" width="16" xmlns="http://www.w3.org/2000/svg"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>`;
        dlBtn.addEventListener('mousedown', (e) => e.stopPropagation());
        dlBtn.addEventListener('click', (e) => { e.stopPropagation(); window.location.href = `/api/frd/export-zip?import_id=${encodeURIComponent(item.id)}`; });
        downloadFo.appendChild(dlBtn);
        g.appendChild(downloadFo);
    }

    static _addForgeOverlay(g, item) {
        const forgeOverlay = this._createForeignObject('100', '260', '200', '100', { 'class': 'ws-forge-overlay' });
        const wrap = document.createElement('div');
        wrap.style.cssText = 'text-align:center; font-family:"Source Sans 3",sans-serif;';
        
        const nameLabel = document.createElement('div');
        nameLabel.style.cssText = 'font-size:12px; color:#94a3b8; margin-bottom:10px;';
        nameLabel.textContent = (item.name || '').toLowerCase();
        
        const forgeBtn = document.createElement('button');
        forgeBtn.id = `forge-btn-${item.id}`;
        forgeBtn.style.cssText = 'background:#A3CD54; color:#fff; border:none; border-radius:20px; padding:8px 20px; font-size:13px; cursor:pointer; text-transform:lowercase;';
        forgeBtn.textContent = 'forger le rendu';
        
        const statusEl = document.createElement('div');
        statusEl.id = `forge-status-${item.id}`;
        statusEl.style.cssText = 'font-size:11px; color:#94a3b8; margin-top:6px;';
        
        wrap.appendChild(nameLabel);
        wrap.appendChild(forgeBtn);
        wrap.appendChild(statusEl);
        forgeOverlay.appendChild(wrap);

        forgeBtn.addEventListener('mousedown', (e) => e.stopPropagation());
        forgeBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            await WsScreenShell._forgeWithImageGate(item, g, forgeOverlay);
        });
        g.appendChild(forgeOverlay);
    }

    static async _forgeWithImageGate(item, shell, overlay) {
        // 1. Résoudre token (impersonation-safe)
        const sess = JSON.parse(sessionStorage.getItem('homeos_impersonation') || '{}').token
            ? JSON.parse(sessionStorage.getItem('homeos_impersonation') || '{}')
            : JSON.parse(localStorage.getItem('homeos_session') || '{}');
        const token = sess.token || '';

        // 2. Lire le manifest frais du projet actif
        let imageAssets = [];
        try {
            const ar = await fetch('/api/projects/active', { headers: { 'X-User-Token': token } });
            const ap = await ar.json();
            if (ap.id) {
                const mr = await fetch(`/api/projects/${ap.id}/manifest`, { headers: { 'X-User-Token': token } });
                const manifest = await mr.json();
                imageAssets = manifest?.design_tokens?.image_assets || [];
            }
        } catch(_) {}

        // 3. Si pas d'assets → forge directe, pas de gate
        if (!imageAssets.length) {
            window.wsForge?.forgeScreen(item.id, shell, overlay);
            return;
        }

        // 4. Afficher la gate modal
        const decisions = {};
        const modal = document.createElement('div');
        modal.id = 'forge-image-gate';
        modal.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:9999;display:flex;align-items:center;justify-content:center;';

        const box = document.createElement('div');
        box.style.cssText = 'background:#fff;border-radius:16px;padding:24px;max-width:480px;width:90%;box-shadow:0 8px 40px rgba(0,0,0,0.18);display:flex;flex-direction:column;gap:16px;max-height:80vh;overflow-y:auto; font-family: "Source Sans 3", sans-serif;';

        const title = document.createElement('div');
        title.style.cssText = 'font-size:14px;font-weight:700;color:#3d3d3c;';
        title.textContent = `${imageAssets.length} illustration${imageAssets.length > 1 ? 's' : ''} détectée${imageAssets.length > 1 ? 's' : ''} — que fait-on ?`;
        box.appendChild(title);

        imageAssets.forEach((asset, i) => {
            const row = document.createElement('div');
            row.style.cssText = 'display:flex;gap:12px;align-items:flex-start;padding:10px;border-radius:10px;background:#f7f6f2;border:1px solid #e5e5e5;';

            const img = document.createElement('img');
            img.src = asset.specimen_url || '';
            img.style.cssText = 'width:64px;height:64px;object-fit:cover;border-radius:6px;border:1px solid #e5e5e5;flex-shrink:0;';
            row.appendChild(img);

            const right = document.createElement('div');
            right.style.cssText = 'display:flex;flex-direction:column;gap:6px;flex:1;';

            const desc = document.createElement('div');
            desc.style.cssText = 'font-size:12px;color:#64748b;font-style:italic;';
            desc.textContent = (asset.description || `illustration ${i + 1}`).toLowerCase();
            right.appendChild(desc);

            const btns = document.createElement('div');
            btns.style.cssText = 'display:flex;gap:6px;';

            ['tenter en vecteur', 'aplatir en image'].forEach(label => {
                const val = label.includes('vecteur') ? 'vector' : 'png';
                const b = document.createElement('button');
                b.style.cssText = 'padding:4px 10px;border-radius:8px;font-size:12px;border:1px solid #e5e5e5;background:#fff;cursor:pointer;transition:all 0.15s; color: #3d3d3c;';
                b.textContent = label;
                b.dataset.val = val;
                b.dataset.idx = String(i);
                b.onclick = () => {
                    decisions[i] = val;
                    btns.querySelectorAll('button').forEach(x => {
                        x.style.background = '#fff';
                        x.style.color = '#3d3d3c';
                        x.style.borderColor = '#e5e5e5';
                        x.style.fontWeight = 'normal';
                    });
                    b.style.background = '#8cc63f';
                    b.style.color = '#fff';
                    b.style.borderColor = '#8cc63f';
                    b.style.fontWeight = '700';
                };
                btns.appendChild(b);
            });
            right.appendChild(btns);
            row.appendChild(right);
            box.appendChild(row);
        });

        const footer = document.createElement('div');
        footer.style.cssText = 'display:flex;gap:8px;justify-content:flex-end;margin-top:4px;';

        const skipBtn = document.createElement('button');
        skipBtn.style.cssText = 'padding:8px 16px;border-radius:10px;font-size:13px;border:1px solid #e5e5e5;background:#fff;cursor:pointer; color: #3d3d3c;';
        skipBtn.textContent = 'ignorer et forger';
        skipBtn.onclick = () => { modal.remove(); window.wsForge?.forgeScreen(item.id, shell, overlay); };

        const goBtn = document.createElement('button');
        goBtn.style.cssText = 'padding:8px 20px;border-radius:10px;font-size:13px;font-weight:700;border:none;background:#3d3d3c;color:#fff;cursor:pointer;';
        goBtn.textContent = 'forger avec ces choix';
        goBtn.onclick = async () => {
            modal.remove();
            // Écrire les décisions dans le manifest (format lisible par la forge)
            try {
                const ar2 = await fetch('/api/projects/active', { headers: { 'X-User-Token': token } });
                const ap2 = await ar2.json();
                if (ap2.id) {
                    const mr2 = await fetch(`/api/projects/${ap2.id}/manifest`, { headers: { 'X-User-Token': token } });
                    const manifest2 = await mr2.json();
                    let text = manifest2.raw_content || manifest2.description || '';
                    imageAssets.forEach((asset, i) => {
                        const val = decisions[i];
                        if (!val) return;
                        const line = val === 'png'
                            ? `${(asset.description || `illustration ${i+1}`).toLowerCase()} : garder png`
                            : `${(asset.description || `illustration ${i+1}`).toLowerCase()} : tenter vecteurs`;
                        if (!text.includes(line)) text = line + '\n' + text;
                    });
                    manifest2.raw_content = text;
                    await fetch(`/api/projects/${ap2.id}/manifest`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json', 'X-User-Token': token },
                        body: JSON.stringify(manifest2)
                    });
                }
            } catch(_) {}
            window.wsForge?.forgeScreen(item.id, shell, overlay);
        };

        footer.appendChild(skipBtn);
        footer.appendChild(goBtn);
        box.appendChild(footer);
        modal.appendChild(box);
        document.body.appendChild(modal);
    }
}

window.WsScreenShell = WsScreenShell;
