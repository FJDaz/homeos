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
        g.appendChild(header);

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
                badgeDiv.innerHTML = `<span style="background:#f0fdf4; color:#16a34a; border:1px solid #bbf7d0; padding:2px 6px; border-radius:4px; font-size:9px; font-weight:600; white-space:nowrap;">Tailwind généré — peut différer du rendu exact</span>`;
            } else if (item.origin === 'compiled') {
                badgeDiv.innerHTML = `<span style="background:#f8fafc; color:#64748b; border:1px solid #e2e8f0; padding:2px 6px; border-radius:4px; font-size:9px; font-weight:600; white-space:nowrap;">build compilé</span>`;
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
                badgeDiv.innerHTML = `<span style="background:#fff7ed; color:#c2410c; border:1px solid #ffedd5; padding:4px 8px; border-radius:6px; font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:0.02em; display:flex; align-items:center; gap:6px; width:fit-content;">
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
        iframe.addEventListener('load', () => { if (window.wsFontManager) window.wsFontManager.injectStyles(); });
        if (item.html_template) iframe.src = `/api/frd/file?name=${encodeURIComponent(item.html_template)}&raw=1`;
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
        wireDiv.innerHTML = `<span style="font-size:10px; font-weight:800; border:1px solid #A3CD54; padding:2px 6px; border-radius:4px; text-transform:uppercase; letter-spacing:0.05em;">Wire</span>`;
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
        previewDiv.innerHTML = `<span style="font-size:10px; font-weight:600; background:rgba(0,0,0,0.03); padding:2px 6px; border-radius:4px; text-transform:uppercase; letter-spacing:0.02em;">Aperçu</span>`;
        previewDiv.addEventListener('mousedown', (e) => e.stopPropagation());
        previewDiv.addEventListener('click', (e) => { e.stopPropagation(); window.wsCanvas.selectScreen(g); window.wsPreview?.enterPreviewMode(g.id, 'construct'); });
        previewFo.appendChild(previewDiv);
        g.appendChild(previewFo);

        // Save
        const saveFo = this._createForeignObject(String(SW - 140), '8', '55', '24', { 
            'pointer-events': 'all', 'data-right-offset': '140', 'class': 'ws-shell-tool'
        });
        const saveBtn = document.createElement('button');
        saveBtn.style.cssText = "width:100%; height:100%; line-height:1; background:#8cc63f; color:#fff; border:none; border-radius:4px; font-size:9px; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; cursor:pointer;";
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
        nameLabel.style.cssText = 'font-size:10px; color:#94a3b8; margin-bottom:10px;';
        nameLabel.textContent = (item.name || '').toLowerCase();
        
        const forgeBtn = document.createElement('button');
        forgeBtn.id = `forge-btn-${item.id}`;
        forgeBtn.style.cssText = 'background:#A3CD54; color:#fff; border:none; border-radius:20px; padding:8px 20px; font-size:11px; cursor:pointer; text-transform:lowercase;';
        forgeBtn.textContent = 'forger le rendu';
        
        const statusEl = document.createElement('div');
        statusEl.id = `forge-status-${item.id}`;
        statusEl.style.cssText = 'font-size:9px; color:#94a3b8; margin-top:6px;';
        
        wrap.appendChild(nameLabel);
        wrap.appendChild(forgeBtn);
        wrap.appendChild(statusEl);
        forgeOverlay.appendChild(wrap);

        forgeBtn.addEventListener('mousedown', (e) => e.stopPropagation());
        forgeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            window.wsForge?.forgeScreen(item.id, g, forgeOverlay);
        });
        g.appendChild(forgeOverlay);
    }
}

window.WsScreenShell = WsScreenShell;
