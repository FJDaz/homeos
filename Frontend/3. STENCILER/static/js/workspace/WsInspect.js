/**
 * WsInspect.js — Mission 134-B
 * Refined Arsenal: Non-spontaneous UI, Fix Edit Code, Font Hierarchy
 */

class WsInspect {
    constructor(workspace) {
        this.workspace = workspace;
        this.isActive = false;
        this.activeMode = 'select';
        this.editor = null;
        this.selectedElement = null;
        this.currentSelector = null;
        this.currentFile = null;

        // Undo History Stack
        this.historyStack = [];
        this.maxHistory = 30;

        // UI Containers
        this.popover = document.getElementById('ws-popover-container');
        this.colorPopover = document.getElementById('ws-color-container');
        this.typoPopover = document.getElementById('ws-typo-container');
        
        // Controls
        this.saveBtn = document.getElementById('ws-popover-save');
        this.closeBtn = document.getElementById('ws-popover-close');
        this.tagLabel = document.getElementById('ws-popover-tag');

        this.colorClose = document.getElementById('ws-color-close');
        this.colorApply = document.getElementById('ws-color-apply');
        this.colorPreview = document.getElementById('ws-color-preview');
        this.sliderH = document.getElementById('ws-tsl-h');
        this.sliderS = document.getElementById('ws-tsl-s');
        this.sliderL = document.getElementById('ws-tsl-l');

        this.typoClose = document.getElementById('ws-typo-close');
        this.typoApply = document.getElementById('ws-typo-apply');
        this.fontSelect = document.getElementById('ws-typo-font');
        this.sizeInput = document.getElementById('ws-typo-size');
        this.weightSelect = document.getElementById('ws-typo-weight');

        this.setupListeners();
        // Local Font Access nécessite un geste utilisateur — chargé au premier clic
        if (this.fontSelect) {
            this.fontSelect.addEventListener('mousedown', () => this.loadLocalFonts(), { once: true });
        }
    }

    setMode(mode) {
        this.activeMode = mode;
        this.hide();
        this.hideColor();
        this.hideTypo();
        if (mode !== 'select' && mode !== 'text' && mode !== 'colors') this.clearSelection();
    }

    async loadLocalFonts() {
        if (!this.fontSelect) return;
        if (this.fontSelect.options.length > 3) return;

        let families = [];

        // Priorité 1 : fontes système via serveur (cross-browser, toutes nav)
        try {
            const res = await fetch('/api/sullivan/system-fonts');
            const data = await res.json();
            families = data.families || [];
        } catch (_) {}

        // Priorité 2 : Local Font Access API (Chrome uniquement, si serveur vide)
        if (families.length === 0 && 'queryLocalFonts' in window) {
            try {
                const fonts = await window.queryLocalFonts();
                families = [...new Set(fonts.map(f => f.family))].sort();
            } catch (_) {}
        }

        families.forEach(f => {
            const opt = document.createElement('option');
            opt.value = f; opt.innerText = f;
            this.fontSelect.appendChild(opt);
        });
    }

    setupListeners() {
        if (this.closeBtn) this.closeBtn.onclick = () => this.hide();
        if (this.saveBtn) this.saveBtn.onclick = () => this.saveGraft();
        
        if (this.colorClose) this.colorClose.onclick = () => this.hideColor();
        if (this.colorApply) this.colorApply.onclick = () => this.applyColor();

        if (this.typoClose) this.typoClose.onclick = () => this.hideTypo();
        if (this.typoApply) this.typoApply.onclick = () => this.applyTypo();

        [this.sliderH, this.sliderS, this.sliderL].forEach(s => {
            if (s) s.oninput = () => this.updateColorPreview();
        });

        window.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') { this.hide(); this.hideColor(); this.hideTypo(); this.clearSelection(); }
        });

        window.addEventListener('message', (e) => {
            if (e.data.type === 'inspect-click') this.show(e.data);
            if (e.data.type === 'inspect-tool-change') this.setMode(e.data.mode);
            if (e.data.type === 'inspect-undo') this.undo();
            if (e.data.type === 'inspect-ready-to-place-image') this.placeImageAt(e.data.x, e.data.y, e.data.src);
        });
    }

    injectTracker(iframe) {
        iframe.onload = () => {
            const trackerScript = `
                (function() {
                    let lastHover = null;
                    let selectedEl = null;
                    let lastSelectedEl = null;
                    let activeMode = 'select';
                    let isDragging = false;
                    let isDrawing = false;
                    let startX, startY;
                    let initialTransformX = 0, initialTransformY = 0;
                    let ghostFrame = null;

                    function scanAtomicOrgans() {
                        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_COMMENT, null, false);
                        let node;
                        while(node = walker.nextNode()) {
                            const comment = node.nodeValue.trim();
                            if (comment.length > 5 && !comment.includes('-->')) {
                                let nextEl = node.nextElementSibling;
                                while (nextEl && ['SCRIPT', 'STYLE'].includes(nextEl.tagName)) nextEl = nextEl.nextElementSibling;
                                if (nextEl) nextEl.setAttribute('data-atomic-organ', comment);
                            }
                        }
                    }
                    scanAtomicOrgans();

                    const editBtn = document.createElement('button');
                    editBtn.id = 'ws-in-preview-edit-btn';
                    editBtn.innerHTML = '<svg style="width:12px;height:12px;margin-right:6px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/></svg> Edit code';
                    editBtn.style.cssText = 'position: fixed; display: none; z-index: 999999; background: #fff; color: #64748b; border: 1px solid #e2e8f0; padding: 6px 12px; font-size: 11px; font-family: "Source Sans 3", sans-serif; font-weight: 600; border-radius: 6px; cursor: pointer; align-items: center; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); transform: translateY(-100%); transition: opacity 0.2s;';
                    document.body.appendChild(editBtn);

                    // Fix: Stop propagation to prevent body.onmousedown from hiding the button before the click
                    editBtn.onmousedown = (e) => {
                        e.stopPropagation();
                        if (selectedEl) {
                            const rect = selectedEl.getBoundingClientRect();
                            sendClickMessage(selectedEl, rect);
                        }
                    };

                    window.addEventListener('message', (e) => {
                        if (e.data.type === 'inspect-tool-change') {
                            activeMode = e.data.mode;
                            document.body.style.cursor = 
                                (activeMode === 'text') ? 'text' :
                                (activeMode === 'frame') ? 'crosshair' :
                                (activeMode === 'drag') ? 'grab' :
                                (activeMode === 'colors') ? 'copy' :
                                (activeMode === 'place-img') ? 'copy' : 'default';
                        }
                        if (e.data.type === 'inspect-clear-selection') clearSelection();
                        if (e.data.type === 'inspect-undo') {
                            document.body.innerHTML = e.data.snapshot;
                            scanAtomicOrgans(); document.body.appendChild(editBtn);
                        }
                        if (e.data.type === 'inspect-apply-color') { const _ct = selectedEl || lastSelectedEl; if (_ct) _ct.style.backgroundColor = e.data.color; }
                        if (e.data.type === 'inspect-apply-typo') {
                            const target = selectedEl || lastSelectedEl;
                            if (target) {
                                target.style.fontFamily = e.data.font;
                                target.style.fontSize = e.data.size + 'px';
                                target.style.fontWeight = e.data.weight;
                            }
                        }
                        if (e.data.type === 'inspect-ready-to-place-image') {
                            takeSnapshot();
                            const img = document.createElement('img');
                            img.src = e.data.src; img.style.position = 'absolute';
                            img.style.left = (window.lastClickX || 100) + 'px'; img.style.top = (window.lastClickY || 100) + 'px';
                            img.style.maxWidth = '200px'; document.body.appendChild(img);
                        }
                        if (e.data.type === 'inspect-update-dom') {
                             takeSnapshot();
                             const target = document.querySelector(e.data.selector);
                             if (target) target.outerHTML = e.data.html;
                        }
                    });

                    function takeSnapshot() { window.parent.postMessage({ type: 'inspect-snapshot', html: document.body.innerHTML }, '*'); }

                    function clearSelection() {
                        if (selectedEl) selectedEl.classList.remove('organ-selected');
                        selectedEl = null; editBtn.style.display = 'none';
                        window.parent.postMessage({ type: 'inspect-selection-cleared' }, '*');
                    }

                    document.body.onmouseover = (e) => {
                        if (activeMode !== 'select') return;
                        const organ = e.target.closest('[data-atomic-organ]');
                        if (lastHover && lastHover !== selectedEl) lastHover.classList.remove('inspect-hover');
                        if (organ) { organ.classList.add('inspect-hover'); lastHover = organ; } else lastHover = null;
                    };

                    document.body.onmousedown = (e) => {
                        // All tools behavior
                        if (activeMode === 'select' || activeMode === 'text' || activeMode === 'colors') {
                            const organ = e.target.closest('[data-atomic-organ]');
                            if (organ) {
                                if (selectedEl) selectedEl.classList.remove('organ-selected');
                                selectedEl = organ; lastSelectedEl = organ; selectedEl.classList.add('organ-selected');
                                const rect = selectedEl.getBoundingClientRect();
                                
                                // Show "Edit Code" only in Select mode
                                if (activeMode === 'select') {
                                    editBtn.style.display = 'flex';
                                    editBtn.style.top = rect.top + 'px';
                                    editBtn.style.left = (rect.left + rect.width - 100) + 'px';
                                } else {
                                    editBtn.style.display = 'none';
                                }
                                
                                isDragging = (activeMode === 'drag' || activeMode === 'select');
                                startX = e.clientX; startY = e.clientY;
                                const transform = getComputedStyle(selectedEl).transform;
                                if (transform !== 'none') {
                                    const matrix = transform.match(/matrix\\(([^)]+)\\)/)[1].split(', ');
                                    initialTransformX = parseFloat(matrix[4] || 0); initialTransformY = parseFloat(matrix[5] || 0);
                                } else { initialTransformX = initialTransformY = 0; }
                                
                                // Parent notification (Mode selectivity handled in parent)
                                window.parent.postMessage({ type: 'inspect-organ-selected', tagName: selectedEl.tagName.toLowerCase(), selector: getSelector(selectedEl), rect: rect }, '*');
                            } else if (activeMode === 'text') {
                                // Nouveau texte si clic sur vide en mode T
                                takeSnapshot();
                                const span = document.createElement('span');
                                span.innerText = 'Nouveau texte';
                                span.contentEditable = 'true';
                                span.style.position = 'absolute';
                                span.style.left = e.clientX + 'px'; span.style.top = e.clientY + 'px';
                                span.style.fontFamily = getComputedStyle(document.body).fontFamily;
                                span.setAttribute('data-atomic-organ', 'Text Element');
                                document.body.appendChild(span);
                                span.focus();
                            } else { clearSelection(); }
                        }

                        if (activeMode === 'frame') {
                            takeSnapshot(); isDrawing = true;
                            drawStartX = e.clientX; drawStartY = e.clientY;
                            ghostFrame = document.createElement('div');
                            ghostFrame.style.cssText = 'position: fixed; border: 2px dashed #A3CD54; background: rgba(163, 205, 84, 0.1); pointer-events: none; z-index: 9999;';
                            ghostFrame.style.left = drawStartX + 'px'; ghostFrame.style.top = drawStartY + 'px';
                            document.body.appendChild(ghostFrame);
                        }

                        if (activeMode === 'place-img') {
                            window.lastClickX = e.clientX; window.lastClickY = e.clientY;
                            window.parent.postMessage({ type: 'inspect-request-image-file' }, '*');
                        }
                    };

                    document.body.onmousemove = (e) => {
                        if (isDragging && selectedEl) {
                            if (document.body.style.cursor !== 'grabbing') document.body.style.cursor = 'grabbing';
                            const dx = e.clientX - startX; const dy = e.clientY - startY;
                            selectedEl.style.transform = \`translate(\${initialTransformX + dx}px, \${initialTransformY + dy}px)\`;
                            const rect = selectedEl.getBoundingClientRect();
                            if (editBtn.style.display !== 'none') {
                                editBtn.style.top = rect.top + 'px'; editBtn.style.left = (rect.left + rect.width - 100) + 'px';
                            }
                        }
                        if (isDrawing && ghostFrame) {
                            const dx = e.clientX - drawStartX; const dy = e.clientY - drawStartY;
                            ghostFrame.style.width = Math.abs(dx) + 'px'; ghostFrame.style.height = Math.abs(dy) + 'px';
                            ghostFrame.style.left = (dx < 0 ? e.clientX : drawStartX) + 'px'; ghostFrame.style.top = (dy < 0 ? e.clientY : drawStartY) + 'px';
                        }
                    };

                    document.body.onmouseup = () => {
                        if (isDragging) {
                            takeSnapshot();
                            if (activeMode === 'select' || activeMode === 'drag') document.body.style.cursor = 'grab';
                        }
                        isDragging = false;
                        if (isDrawing && ghostFrame) {
                            const newDiv = document.createElement('div');
                            newDiv.style.cssText = ghostFrame.style.cssText.replace('dashed', 'solid').replace('fixed', 'absolute');
                            newDiv.style.pointerEvents = 'auto'; newDiv.setAttribute('data-atomic-organ', 'New Frame');
                            document.body.appendChild(newDiv);
                            document.body.removeChild(ghostFrame); ghostFrame = null; isDrawing = false;
                            takeSnapshot();
                        }
                    };

                    function sendClickMessage(el, rect) {
                        window.parent.postMessage({
                            type: 'inspect-click', selector: getSelector(el), tagName: el.tagName.toLowerCase(),
                            organName: el.getAttribute('data-atomic-organ'), html: el.outerHTML,
                            rect: { top: rect.top, left: rect.left, width: rect.width, height: rect.height }
                        }, '*');
                    }

                    function getSelector(el) {
                        if (el.id) return '#' + el.id;
                        let path = []; while (el && el.parentElement) {
                            let siblingIndex = 1; let sibling = el.previousElementSibling;
                            while (sibling) { if (sibling.tagName === el.tagName) siblingIndex++; sibling = sibling.previousElementSibling; }
                            path.unshift(el.tagName.toLowerCase() + ':nth-of-type(' + siblingIndex + ')'); el = el.parentElement;
                        }
                        return path.join(' > ');
                    }

                    const style = document.createElement('style');
                    style.innerHTML = \`
                        .inspect-hover { outline: 2px dashed rgba(163, 205, 84, 0.4) !important; outline-offset: -2px; }
                        .organ-selected { outline: 3px solid #A3CD54 !important; outline-offset: -3px; }
                        [contenteditable="true"]:focus { outline: none !important; }
                    \`;
                    document.head.appendChild(style);
                })();
            `;
            try {
                const scriptEl = iframe.contentDocument.createElement('script');
                scriptEl.textContent = trackerScript;
                iframe.contentDocument.body.appendChild(scriptEl);
            } catch (err) { console.error("WsInspect: Injection failed", err); }
        };
    }

    snapshot(html) {
        this.historyStack.push(html);
        if (this.historyStack.length > this.maxHistory) this.historyStack.shift();
    }

    undo() {
        if (this.historyStack.length === 0) return;
        const prevHTML = this.historyStack.pop();
        const iframe = document.querySelector('#ws-preview-frame-container iframe');
        iframe.contentWindow.postMessage({ type: 'inspect-undo', snapshot: prevHTML }, '*');
    }

    show(data) {
        this.isActive = true; this.currentSelector = data.selector;
        const iframe = document.querySelector('#ws-preview-frame-container iframe');
        let filename = "index.html"; if (iframe && iframe.src) { const url = new URL(iframe.src, window.location.origin); filename = url.searchParams.get('file') || url.pathname.split('/').pop(); }
        this.currentFile = filename; this.tagLabel.innerText = data.organName || data.tagName;
        const iframeRect = iframe.getBoundingClientRect();
        let x = iframeRect.left + data.rect.left + data.rect.width + 15; let y = iframeRect.top + data.rect.top;
        if (x + 350 > window.innerWidth) x = iframeRect.left + data.rect.left - 350 - 15;
        this.popover.style.left = `${x}px`; this.popover.style.top = `${y}px`;
        this.popover.classList.add('show'); this.popover.classList.remove('hidden');
        if (!this.editor) this.initMonaco(data.html); else this.editor.setValue(data.html);
    }

    hide() { this.isActive = false; this.popover.classList.remove('show'); setTimeout(() => { if (!this.isActive) this.popover.classList.add('hidden'); }, 300); }

    showColor(data) {
        if (this.activeMode !== 'colors') return;
        if (this.isActive) this.hide();
        const iframe = document.querySelector('#ws-preview-frame-container iframe');
        const iframeRect = iframe.getBoundingClientRect();
        const x = iframeRect.left + data.rect.left; const y = iframeRect.top + data.rect.top + data.rect.height + 15;
        this.colorPopover.style.left = `${x}px`; this.colorPopover.style.top = `${y}px`;
        this.colorPopover.classList.add('show'); this.colorPopover.classList.remove('hidden');
        this.updateColorPreview();
    }

    hideColor() { this.colorPopover.classList.remove('show'); setTimeout(() => this.colorPopover.classList.add('hidden'), 300); }

    updateColorPreview() {
        const color = `hsl(${this.sliderH.value}, ${this.sliderS.value}%, ${this.sliderL.value}%)`;
        this.colorPreview.style.backgroundColor = color;
        const iframe = document.querySelector('#ws-preview-frame-container iframe');
        iframe.contentWindow.postMessage({ type: 'inspect-apply-color', color: color }, '*');
    }

    applyColor() { this.hideColor(); }

    showTypo(data) {
        if (this.activeMode !== 'text') return;
        const iframe = document.querySelector('#ws-preview-frame-container iframe');
        const iframeRect = iframe.getBoundingClientRect();
        const x = iframeRect.left + data.rect.left + data.rect.width + 15;
        const y = iframeRect.top + data.rect.top;
        this.typoPopover.style.left = `${x}px`; this.typoPopover.style.top = `${y}px`;
        this.typoPopover.classList.add('show'); this.typoPopover.classList.remove('hidden');
    }

    hideTypo() { this.typoPopover.classList.remove('show'); setTimeout(() => this.typoPopover.classList.add('hidden'), 300); }

    async applyTypo() {
        let font = this.fontSelect.value;
        const size = this.sizeInput.value;
        const weight = this.weightSelect.value;
        const iframe = document.querySelector('#ws-preview-frame-container iframe');
        if (!iframe) return;

        const originalText = this.typoApply?.innerText;
        if (this.typoApply) { this.typoApply.innerText = '...'; this.typoApply.disabled = true; }

        // 1. Générer la webfont côté serveur
        try {
            const res = await fetch('/api/sullivan/generate-webfont', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ font_name: font })
            });
            const data = await res.json();

            // 2. Injecter @font-face directement dans iframe.contentDocument (pas via trackerScript)
            if (data.css && iframe.contentDocument) {
                let styleEl = iframe.contentDocument.getElementById('ws-injected-fonts');
                if (!styleEl) {
                    styleEl = iframe.contentDocument.createElement('style');
                    styleEl.id = 'ws-injected-fonts';
                    (iframe.contentDocument.head || iframe.contentDocument.body).appendChild(styleEl);
                }
                styleEl.textContent += data.css + '\n';
                // Utiliser le nom de famille déclaré dans le @font-face
                if (data.css) {
                    const match = data.css.match(/font-family:\s*['"]?([^'";]+)['"]?/);
                    if (match) font = match[1].trim();
                }
            }
        } catch (err) {
            console.warn('M148: webfont bridge failed, applying system font directly', err);
        } finally {
            if (this.typoApply) { this.typoApply.innerText = originalText; this.typoApply.disabled = false; }
        }

        // 3. Appliquer la typo via currentSelector (scope graft) — même pattern que saveGraft
        console.log('[applyTypo] selector:', this.currentSelector, '| font:', font, '| iframe.contentDocument:', !!iframe.contentDocument);
        if (this.currentSelector && iframe.contentDocument) {
            const target = iframe.contentDocument.querySelector(this.currentSelector);
            console.log('[applyTypo] target found:', !!target, target);
            if (target) {
                target.style.setProperty('font-family', font, 'important');
                target.style.setProperty('font-size', size + 'px', 'important');
                target.style.setProperty('font-weight', weight, 'important');
                // Override Tailwind utility classes on descendants
                let overrideEl = iframe.contentDocument.getElementById('ws-typo-override');
                if (!overrideEl) {
                    overrideEl = iframe.contentDocument.createElement('style');
                    overrideEl.id = 'ws-typo-override';
                    (iframe.contentDocument.head || iframe.contentDocument.body).appendChild(overrideEl);
                }
                const esc = this.currentSelector.replace(/"/g, '\\"');
                overrideEl.textContent = `${esc}, ${esc} * { font-family: ${font} !important; font-size: ${size}px !important; font-weight: ${weight} !important; }`;
                return;
            }
        }
        // Fallback postMessage si currentSelector absent
        iframe.contentWindow.postMessage({ type: 'inspect-apply-typo', font, size, weight }, '*');
    }

    async initMonaco(initialValue) {
        return new Promise((resolve) => {
            require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs' }});
            require(['vs/editor/editor.main'], () => {
                const container = document.getElementById('ws-popover-editor');
                this.editor = monaco.editor.create(container, {
                    value: initialValue, language: 'html', theme: 'vs-light', minimap: { enabled: false }, fontSize: 12, lineNumbers: 'off', automaticLayout: true, wordWrap: 'on', padding: { top: 10, bottom: 10 }, scrollbar: { vertical: 'hidden', horizontal: 'hidden' }
                });
                const ro = new ResizeObserver(() => this.editor.layout());
                ro.observe(container); resolve();
            });
        });
    }

    async saveGraft() {
        if (!this.isActive) return;
        const btn = this.saveBtn; const originalText = btn.innerText; btn.innerText = 'SAVING...'; btn.disabled = true;
        const newHtml = this.editor.getValue();
        const match = newHtml.match(/font-family:\\s*['"]?([^'";,]+)['"]?/);
        if (match) {
            const fontName = match[1];
            await fetch('/api/workspace/generate-webfonts', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ font_name: fontName })
            });
        }
        try {
            const resp = await fetch('/api/workspace/graft', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename: this.currentFile, selector: this.currentSelector, html_content: newHtml })
            });
            if ((await resp.json()).status === 'success') {
                const iframe = document.querySelector('#ws-preview-frame-container iframe');
                iframe.contentWindow.postMessage({ type: 'inspect-update-dom', selector: this.currentSelector, html: newHtml }, '*');
                btn.innerText = 'DONE ✓'; setTimeout(() => { btn.innerText = originalText; btn.disabled = false; }, 2000);
            } else throw new Error();
        } catch (err) { btn.innerText = 'ERROR'; setTimeout(() => { btn.innerText = originalText; btn.disabled = false; }, 3000); }
    }
    
    clearSelection() {
        const iframe = document.querySelector('#ws-preview-frame-container iframe');
        if (iframe && iframe.contentWindow) iframe.contentWindow.postMessage({ type: 'inspect-clear-selection' }, '*');
    }
}

// Global Listener
window.addEventListener('message', (e) => {
    if (e.data.type === 'inspect-snapshot') window.wsInspect?.snapshot(e.data.html);
    if (e.data.type === 'inspect-organ-selected') {
        if (window.wsInspect && e.data.selector) window.wsInspect.currentSelector = e.data.selector;
        window.wsInspect?.showColor(e.data);
        window.wsInspect?.showTypo(e.data);
    }
    if (e.data.type === 'inspect-selection-cleared') { window.wsInspect?.hideColor(); window.wsInspect?.hideTypo(); }
    if (e.data.type === 'inspect-request-image-file') document.getElementById('ws-internal-image-loader').click();
});

window.WsInspect = WsInspect;
