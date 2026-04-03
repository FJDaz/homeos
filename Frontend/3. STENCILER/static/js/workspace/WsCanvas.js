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
            const modeMap = { 'KeyV': 'select', 'KeyH': 'drag', 'KeyI': 'place-img', 'KeyF': 'frame' };
            if (modeMap[e.code]) this.setMode(modeMap[e.code]);
            if (e.code === 'Digit0') this.resetView();
        });
        window.addEventListener('keyup', (e) => { if (e.code === 'Space') this.isSpacePressed = false; });

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
            if (this.activeMode === 'select') {
                const rect = this.svg.getBoundingClientRect();
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
        if (this.selectedScreen) {
            const rect = this.svg.getBoundingClientRect();
            const x = (e.clientX - rect.left - this.viewX) / this.scale - this.offsetDragX;
            const y = (e.clientY - rect.top - this.viewY) / this.scale - this.offsetDragY;
            this.selectedScreen.setAttribute('transform', `matrix(1 0 0 1 ${x} ${y})`);
        }
    }

    handleMouseUp() {
        this.isPanning = false;
        if (this.selectedScreen) {
            this.selectedScreen.classList.remove('ws-dragging');
            this.selectedScreen = null;
        }
        window.wsAudit?.notifyToolbar(null, this.activeMode, this.svg);
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
        return {
            src: iframe.src,
            srcdoc: iframe.srcdoc,
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
        if (document.getElementById(`shell-${item.id}`)) {
            this.selectScreen(document.getElementById(`shell-${item.id}`));
            return;
        }
        if (window.WsScreenShell) {
            const g = await window.WsScreenShell.build(item, this);
            this.content.appendChild(g);
            this.selectScreen(g);
            return g;
        }
    }
}

window.WsCanvas = WsCanvas;
