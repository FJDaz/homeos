/**
 * WsCanvas.js — State Machine & Interaction Engine (Mission 156 Hexagonal)
 */
class WsCanvas {
    constructor(svgId, wrapperId) {
        this.svg = document.getElementById(svgId);
        this.wrapper = document.getElementById(wrapperId);
        this.content = document.getElementById('canvas-content');
        
        // State
        this.scale = 1.0;
        this.viewX = 0;
        this.viewY = 0;
        this.activeMode = 'select'; // 'select', 'drag', 'place-img', 'frame'
        
        // Interaction
        this.isPanning = false;
        this.isSpacePressed = false;
        this.startX = 0;
        this.startY = 0;
        
        // Draggable screens
        this.selectedScreen = null;
        this.activeScreenId = null; 
        this.offsetDragX = 0;
        this.offsetDragY = 0;

        // Resize (Mission 114)
        this.isResizing = false;
        this.initialWidth = 0;
        this.initialHeight = 0;
        this.SNAP_SIZE = 8;

        // Element drag inside iframe (N0)
        this.isDraggingElement = false;
        this.dragElementShell = null;
        this.lastDragClientX = 0;
        this.lastDragClientY = 0;

        this.init();
    }

    init() {
        this.wrapper.addEventListener('wheel', (e) => this.handleWheel(e), { passive: false });
        this.wrapper.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        this.wrapper.addEventListener('dblclick', (e) => this.handleDoubleClick(e));
        window.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        window.addEventListener('mouseup', () => this.handleMouseUp());

        window.addEventListener('keydown', (e) => { 
            if (e.code === 'Space') this.isSpacePressed = true; 
            if (['TEXTAREA', 'INPUT'].includes(document.activeElement.tagName)) return;

            // M274: Deletion shortcuts
            if ((e.code === 'Delete' || e.code === 'Backspace') && this.activeScreenId) {
                const shell = document.getElementById(this.activeScreenId);
                if (shell) {
                    shell.remove();
                    this.deselectAll();
                }
                return;
            }

            const modeMap = { 
                'KeyV': 'select', 'KeyH': 'drag', 'KeyI': 'place-img', 
                'KeyF': 'frame', 'KeyC': 'colors', 'KeyT': 'text', 
                'KeyE': 'effects', 'KeyD': 'front-dev'
            };
            if (modeMap[e.code]) this.setMode(modeMap[e.code]);
            if (e.code === 'Digit0') this.resetView();
        });
        window.addEventListener('keyup', (e) => { if (e.code === 'Space') this.isSpacePressed = false; });

        // M237: Listen for hover messages from iframes
        window.addEventListener('message', (e) => {
            if (!e.data || !e.data.type) return;
            if (e.data.type === 'hm-hover') {
                // Update status bar or tooltip
                const info = `${e.data.tag}${e.data.id ? '#' + e.data.id : ''}${e.data.cls ? '.' + e.data.cls.split(/\s+/).slice(0, 2).join('.') : ''}`;
                const statusEl = document.getElementById('ws-status-bar');
                if (statusEl) statusEl.textContent = info;
            } else if (e.data.type === 'hm-clear') {
                const statusEl = document.getElementById('ws-status-bar');
                if (statusEl) statusEl.textContent = '';
            } else if (e.data.type === 'hm-click') {
                // Could open element inspector
                console.log('[M237] iframe click:', e.data);
            }
        });

        this.updateTransform();
    }

    setMode(mode) {
        this.activeMode = mode;
        document.querySelectorAll('.ws-tool-btn').forEach(btn => {
            btn.classList.toggle('active-tool', btn.dataset.mode === mode);
        });
        window.wsAudit?.notifyToolbar(null, mode, this.svg);
    }

    updateTransform() {
        this.content.setAttribute('transform', `matrix(${this.scale} 0 0 ${this.scale} ${this.viewX} ${this.viewY})`);
        const zoomText = document.getElementById('zoom-level');
        if (zoomText) zoomText.innerText = Math.round(this.scale * 100) + '%';
    }

    handleWheel(e) {
        if (e.target.closest('#ws-left-panels, #ws-chat-history, .glass-card')) return;
        e.preventDefault();
        const oldScale = this.scale;
        this.scale = Math.min(Math.max(0.05, (e.deltaY < 0 ? this.scale * 1.1 : this.scale / 1.1)), 8);
        const rect = this.svg.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        const worldX = (mouseX - this.viewX) / oldScale;
        const worldY = (mouseY - this.viewY) / oldScale;
        this.viewX = mouseX - worldX * this.scale;
        this.viewY = mouseY - worldY * this.scale;
        this.updateTransform();
    }

    handleMouseDown(e) {
        if (this.isSpacePressed || e.button === 1 || this.activeMode === 'drag') {
            this.isPanning = true;
            this.startX = e.clientX - this.viewX;
            this.startY = e.clientY - this.viewY;
            if (this.activeMode === 'drag') this.svg.style.cursor = 'grabbing';
            return;
        }

        const shell = e.target.closest('.ws-screen-shell');
        if (shell) {
            this.selectScreen(shell);
            const rect = this.svg.getBoundingClientRect();
            
            // Détection Resize (Mission 114)
            if (e.target.classList.contains('ws-resize-handle')) {
                this.isResizing = true;
                this.selectedScreen = shell;
                this.selectedScreen.classList.add('ws-resizing');
                const bg = shell.querySelector('.ws-screen-bg');
                this.initialWidth = parseFloat(bg.getAttribute('width'));
                this.initialHeight = parseFloat(bg.getAttribute('height'));
                this.startX = e.clientX;
                this.startY = e.clientY;
                return;
            }

            if (this.activeMode === 'select') {
                const transformStr = shell.getAttribute('transform') || '';
                let tx = 0, ty = 0;
                if (transformStr.includes('matrix')) {
                    const vals = transformStr.match(/matrix\(([^)]+)\)/)?.[1].split(/[\s,]+/).map(Number);
                    if (vals && vals.length >= 6) { tx = vals[4]; ty = vals[5]; }
                }
                const worldY = (e.clientY - rect.top - this.viewY) / this.scale - ty;
                if (worldY >= 0 && worldY <= 40) {
                    this.selectedScreen = shell;
                    this.selectedScreen.classList.add('ws-dragging');
                    this.offsetDragX = (e.clientX - rect.left - this.viewX) / this.scale - tx;
                    this.offsetDragY = (e.clientY - rect.top - this.viewY) / this.scale - ty;
                } else {
                    // Element drag inside iframe (N0 level — no snap)
                    const iframe = shell.querySelector('iframe');
                    if (iframe?.contentWindow) {
                        const fr = iframe.getBoundingClientRect();
                        const ix = e.clientX - fr.left;
                        const iy = e.clientY - fr.top;
                        if (ix >= 0 && iy >= 0 && ix <= fr.width && iy <= fr.height) {
                            console.log('[WsCanvas] 🖱️ hm-click x=' + Math.round(ix) + ' y=' + Math.round(iy));
                            iframe.contentWindow.postMessage({ type: 'hm-click', x: ix, y: iy }, '*');
                            this.isDraggingElement = true;
                            this.dragElementShell = shell;
                            this.lastDragClientX = e.clientX;
                            this.lastDragClientY = e.clientY;
                        }
                    }
                }
            }
        } else if (this.svg.contains(e.target)) {
            this.deselectAll();
        }
    }

    handleDoubleClick(e) {
        const shell = e.target.closest('.ws-screen-shell');
        if (shell) {
            e.preventDefault(); e.stopPropagation();
            this.selectScreen(shell);
            window.wsPreview?.enterPreviewMode(shell.id, 'construct');
        }
    }

    handleMouseMove(e) {
        if (this.isPanning) {
            this.viewX = e.clientX - this.startX;
            this.viewY = e.clientY - this.startY;
            this.updateTransform();
            return;
        }
        if (this.isDraggingElement && this.dragElementShell) {
            const iframe = this.dragElementShell.querySelector('iframe');
            if (iframe?.contentWindow) {
                const dx = e.clientX - this.lastDragClientX;
                const dy = e.clientY - this.lastDragClientY;
                if (dx !== 0 || dy !== 0) {
                    console.log('[WsCanvas] 🖐️ hm-drag dx=' + Math.round(dx) + ' dy=' + Math.round(dy));
                    iframe.contentWindow.postMessage({ type: 'hm-drag', dx, dy }, '*');
                    this.lastDragClientX = e.clientX;
                    this.lastDragClientY = e.clientY;
                }
            }
            return;
        }
        if (this.isResizing && this.selectedScreen) {
            const dx = (e.clientX - this.startX) / this.scale;
            const dy = (e.clientY - this.startY) / this.scale;
            
            // Snap Grid (Mission 114)
            const newW = Math.max(200, Math.round((this.initialWidth + dx) / this.SNAP_SIZE) * this.SNAP_SIZE);
            const newH = Math.max(150, Math.round((this.initialHeight + dy) / this.SNAP_SIZE) * this.SNAP_SIZE);
            
            this.updateShellDimensions(this.selectedScreen, newW, newH);
            return;
        }

        if (this.selectedScreen && !this.isResizing) {
            const rect = this.svg.getBoundingClientRect();
            let x = (e.clientX - rect.left - this.viewX) / this.scale - this.offsetDragX;
            let y = (e.clientY - rect.top - this.viewY) / this.scale - this.offsetDragY;
            x = Math.round(x / this.SNAP_SIZE) * this.SNAP_SIZE;
            y = Math.round(y / this.SNAP_SIZE) * this.SNAP_SIZE;
            this.selectedScreen.setAttribute('transform', `matrix(1 0 0 1 ${x} ${y})`);
            return;
        }

        // Hover probe en mode select : envoie coords à l'iframe via postMessage
        if (this.activeMode === 'select' && !this._probeCooldown) {
            const shell = e.target.closest?.('.ws-screen-shell');
            if (shell) {
                const iframe = shell.querySelector('iframe');
                if (iframe?.contentWindow) {
                    const fr = iframe.getBoundingClientRect();
                    const ix = e.clientX - fr.left;
                    const iy = e.clientY - fr.top;
                    if (ix >= 0 && iy >= 0 && ix <= fr.width && iy <= fr.height) {
                        iframe.contentWindow.postMessage({ type: 'hm-probe', x: ix, y: iy }, '*');
                        this._probeCooldown = true;
                        setTimeout(() => { this._probeCooldown = false; }, 50);
                    }
                }
            } else if (this._lastProbeShell) {
                this._lastProbeShell.querySelector('iframe')?.contentWindow?.postMessage({ type: 'hm-clear' }, '*');
                this._lastProbeShell = null;
            }
            if (shell) this._lastProbeShell = shell;
        }
    }

    handleMouseUp() {
        this.isPanning = false;
        this.isResizing = false;
        this.svg.style.cursor = 'grab';
        if (this.selectedScreen) {
            this.selectedScreen.classList.remove('ws-dragging', 'ws-resizing');
            this.selectedScreen = null;
        }
        if (this.isDraggingElement && this.dragElementShell) {
            const iframe = this.dragElementShell.querySelector('iframe');
            iframe?.contentWindow?.postMessage({ type: 'hm-drop' }, '*');
            this.isDraggingElement = false;
            this.dragElementShell = null;
        }
        window.wsAudit?.notifyToolbar(null, this.activeMode, this.svg);
    }

    updateShellDimensions(shell, w, h) {
        // Fond
        const bg = shell.querySelector('.ws-screen-bg');
        bg.setAttribute('width', w);
        bg.setAttribute('height', h);
        
        // Header
        const header = shell.querySelector('.ws-screen-header');
        if (header) header.setAttribute('width', w);
        
        // Iframe ForeignObject
        const fos = shell.querySelectorAll('foreignObject');
        fos.forEach(fo => {
            if (!fo.classList.contains('ws-forge-overlay')) {
                fo.setAttribute('width', w);
                fo.setAttribute('height', h - 40);
            }
        });

        // Close Button & tools (repositionnement)
        const closeBtn = shell.querySelector('.ws-btn-close');
        if (closeBtn) closeBtn.setAttribute('cx', w - 20);
        
        const resizeHandle = shell.querySelector('.ws-resize-handle');
        if (resizeHandle) {
            resizeHandle.setAttribute('x', w - 12);
            resizeHandle.setAttribute('y', h - 12);
        }

        // Tool buttons repositioning (Aperçu, Wire, Save, Download)
        const toolButtons = shell.querySelectorAll('.ws-shell-tool');
        toolButtons.forEach(fo => {
           const offset = parseFloat(fo.getAttribute('data-right-offset'));
           if (!isNaN(offset)) {
               fo.setAttribute('x', w - offset);
           }
        });
    }

    selectScreen(shell) {
        this.deselectAll();
        shell.classList.add('ws-selected');
        this.content.appendChild(shell); // Bring to front
        this.activeScreenId = shell.id;
        window.wsAudit?.updatePanel(shell);
        window.wsAudit?.notifyToolbar('select', this.activeMode, this.svg, shell.id);
    }

    deselectAll() {
        document.querySelectorAll('.ws-screen-shell').forEach(s => {
            s.classList.remove('ws-selected', 'ws-hover', 'ws-dragging');
        });
        this.activeScreenId = null;
        window.wsAudit?.notifyToolbar(null, this.activeMode, this.svg);
    }

    getActiveScreenHtml() {
        if (!this.activeScreenId) return null;
        const shell = document.getElementById(this.activeScreenId);
        const iframe = shell?.querySelector('iframe');
        if (!iframe) return null;
        const srcdoc = iframe.srcdoc
            || iframe.contentDocument?.documentElement?.outerHTML
            || '';
        return {
            src: iframe.src,
            srcdoc,
            name: shell.querySelector('.ws-screen-title')?.textContent || 'Untitled'
        };
    }

    resetView() {
        this.scale = 1.0; this.viewX = 0; this.viewY = 0;
        this.updateTransform();
    }

    setZoom(val) {
        this.scale = val;
        this.updateTransform();
    }

    async addScreen(item) {
        const existing = document.getElementById(`shell-${item.id}`);
        if (existing) { this.selectScreen(existing); return; }
        if (!window.WsScreenShell) { console.error('WsScreenShell not loaded'); return; }
        const g = await window.WsScreenShell.build(item, this);
        this.content.appendChild(g);
        this.selectScreen(g);
        return g;
    }

    // --- M237: Hover Engine Injected into iframe contentDocument ---
    injectHoverEngine(iframe) {
        try {
            const doc = iframe.contentDocument;
            if (!doc || doc.__hmInjected) return;
            doc.__hmInjected = true;

            const script = doc.createElement('script');
            script.textContent = `
(function() {
    let _last = null;
    let _selected = null;
    let _dragAccX = 0, _dragAccY = 0;
    let _origTransform = '';

    // M258: elementsFromPoint au lieu de elementFromPoint — filtre les wrappers React
    function _findElementAtPoint(x, y) {
        var all = document.elementsFromPoint ? document.elementsFromPoint(x, y) : [];
        // Éléments à ignorer (wrappers React, racine, conteneurs vides)
        var skipIds = ['root', '__next', '___gatsby'];
        var skipTags = ['SCRIPT', 'STYLE', 'LINK', 'META', 'HEAD', 'HTML', 'BODY', 'BR', 'HR'];
        for (var i = 0; i < all.length; i++) {
            var el = all[i];
            if (!el || skipTags.indexOf(el.tagName) !== -1) continue;
            if (el.id && skipIds.indexOf(el.id) !== -1) continue;
            // Accepter si : a un id significatif, ou une classe, ou du texte, ou est un élément sémantique
            var hasId = el.id && el.id.length > 2 && skipIds.indexOf(el.id) === -1;
            var hasClass = el.className && typeof el.className === 'string' && el.className.length > 0;
            var hasText = (el.textContent || '').trim().length > 0;
            var isSemantic = ['IMG', 'BUTTON', 'A', 'INPUT', 'H1', 'H2', 'H3', 'H4', 'P', 'SPAN', 'DIV', 'SECTION', 'NAV', 'HEADER', 'FOOTER', 'MAIN', 'ARTICLE'].indexOf(el.tagName) !== -1;
            if (hasId || hasClass || hasText || isSemantic) {
                return el;
            }
        }
        return all.length > 0 ? all[all.length - 1] : null;
    }

    function _clear() {
        if (_last && _last !== _selected) {
            _last.style.removeProperty('outline');
            _last.style.removeProperty('outline-offset');
        }
        _last = null;
    }

    function _clearSelection() {
        if (_selected) {
            _selected.style.removeProperty('outline');
            _selected.style.removeProperty('outline-offset');
            _selected = null;
        }
        _dragAccX = 0; _dragAccY = 0;
    }

    // Reçoit les coordonnées du canvas (iframe pointer-events:none → pas de mouseover natif)
    window.addEventListener('message', function(e) {
        if (!e.data) return;
        if (e.data.type === 'hm-probe') {
            const el = _findElementAtPoint(e.data.x, e.data.y);
            if (!el || el === document.body || el === document.documentElement) { _clear(); return; }
            if (el === _last) return;
            _clear();
            if (el !== _selected) {
                el.style.outline = '2px dashed #8cc63f';
                el.style.outlineOffset = '-1px';
            }
            _last = el;
            window.parent.postMessage({ type: 'hm-hover', tag: el.tagName, id: el.id || '', cls: (el.className || '').toString().slice(0, 80) }, '*');
        } else if (e.data.type === 'hm-clear') {
            _clear();
            window.parent.postMessage({ type: 'hm-clear' }, '*');
        } else if (e.data.type === 'hm-click') {
            console.log('[hm-engine] click x=' + Math.round(e.data.x) + ' y=' + Math.round(e.data.y));
            // Select element for drag
            const el = _findElementAtPoint(e.data.x, e.data.y);
            if (!el || el === document.body || el === document.documentElement) { console.log('[hm-engine] no element at point'); _clearSelection(); return; }
            console.log('[hm-engine] selected:', el.tagName, el.id || el.className || '');
            _clearSelection();
            _selected = el;
            _dragAccX = 0; _dragAccY = 0;
            // Parse existing translate to resume from current position
            const existing = el.style.transform || '';
            const m = existing.match(/translate\\(([\\d.-]+)px,\\s*([\\d.-]+)px\\)/);
            if (m) { _dragAccX = parseFloat(m[1]); _dragAccY = parseFloat(m[2]); }
            _selected.style.outline = '2px solid #8cc63f';
            _selected.style.outlineOffset = '-1px';
            window.parent.postMessage({ type: 'hm-select', tag: el.tagName, id: el.id || '', cls: (el.className || '').toString().slice(0, 80), text: (el.textContent || '').trim().slice(0, 100) }, '*');
        } else if (e.data.type === 'hm-drag') {
            if (!_selected) return;
            _dragAccX += e.data.dx;
            _dragAccY += e.data.dy;
            _selected.style.transform = 'translate(' + _dragAccX + 'px, ' + _dragAccY + 'px)';
            _selected.style.position = _selected.style.position || 'relative';
        } else if (e.data.type === 'hm-drop') {
            console.log('[hm-engine] drop — element moved to', Math.round(_dragAccX), Math.round(_dragAccY));
        }
    });
})();
            `;
            doc.head.appendChild(script);
        } catch (e) {
            // Cross-origin or not loaded yet
        }
    }
}

window.WsCanvas = WsCanvas;
