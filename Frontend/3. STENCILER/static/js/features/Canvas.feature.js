import StencilerFeature from './base.feature.js';

// Canvas.feature.js - inclut ZoomControls + Delete
class CanvasFeature extends StencilerFeature {
    constructor(id = 'canvas-zone', options = {}) {
        super(id, options);
        this.canvas = null;
        this.zoomLevel = 1;
        this.el = null;
    }

    mount(parentSelector) {
        this.el = document.querySelector(parentSelector);
        if (!this.el) return;

        // Ajoute la classe de conteneur au slot
        this.el.classList.add('canvas-container');

        // Créer la structure interne du canvas sans re-wrapper
        this.el.innerHTML = `
            <canvas id="stenciler-canvas"></canvas>
            <div class="zoom-controls">
                <button id="btn-zoom-out">-</button>
                <span id="zoom-level">100%</span>
                <button id="btn-zoom-in">+</button>
                <button id="btn-zoom-reset">Reset</button>
            </div>
            <button id="btn-delete" class="delete-btn">🗑️</button>
        `;
    }

    init() {
        if (!this.el) return;

        const canvasEl = this.el.querySelector('#stenciler-canvas');
        if (!canvasEl) {
            console.error('Canvas element not found in slot');
            return;
        }

        // Initialiser Fabric.js
        this.canvas = new fabric.Canvas(canvasEl, {
            backgroundColor: 'var(--canvas-bg, #f8fafc)',
            selectionColor: 'rgba(100, 150, 255, 0.3)',
            selectionLineWidth: 2,
            width: this.el.clientWidth - 40,
            height: 400
        });

        this._setupGrid();
        this._setupDropHandlers();
        this._setupZoomControls();
        this._setupDeleteHandlers();
        this._setupPlaceholder();

        console.log('Canvas initialized');
    }

    _setupGrid() {
        if (!this.canvas) return;
        const gridSize = 20;
        const width = this.canvas.width;
        const height = this.canvas.height;

        for (let x = 0; x < width; x += gridSize) {
            this.canvas.add(new fabric.Line([x, 0, x, height], {
                stroke: 'var(--grid-line, #e2e8f0)',
                strokeWidth: 0.5,
                selectable: false,
                evented: false
            }));
        }

        for (let y = 0; y < height; y += gridSize) {
            this.canvas.add(new fabric.Line([0, y, width, y], {
                stroke: 'var(--grid-line, #e2e8f0)',
                strokeWidth: 0.5,
                selectable: false,
                evented: false
            }));
        }
    }

    _setupDropHandlers() {
        if (!this.el) return;

        this.el.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.el.classList.add('drag-over');
        });

        this.el.addEventListener('dragleave', () => {
            this.el.classList.remove('drag-over');
        });

        this.el.addEventListener('drop', (e) => {
            e.preventDefault();
            this.el.classList.remove('drag-over');

            const data = e.dataTransfer?.getData('application/json');
            if (!data) return;

            try {
                const { label, color } = JSON.parse(data);
                const rect = new fabric.Rect({
                    width: 120,
                    height: 80,
                    fill: color || '#4A90E2',
                    stroke: '#2C3E50',
                    strokeWidth: 2,
                    rx: 8,
                    ry: 8
                });

                const text = new fabric.Text(label || 'Item', {
                    fontSize: 14,
                    fill: 'white',
                    fontFamily: 'Inter, sans-serif'
                });

                const group = new fabric.Group([rect, text], {
                    left: e.offsetX - 60,
                    top: e.offsetY - 40,
                    hasControls: true,
                    hasBorders: true
                });

                this.canvas.add(group);
                this.canvas.setActiveObject(group);
                this.canvas.renderAll();
            } catch (err) {
                console.error('Error handling drop:', err);
            }
        });
    }

    _setupZoomControls() {
        this.el.querySelector('#btn-zoom-in')?.addEventListener('click', () => {
            this.zoomLevel = Math.min(this.zoomLevel * 1.2, 5);
            this._applyZoom();
        });

        this.el.querySelector('#btn-zoom-out')?.addEventListener('click', () => {
            this.zoomLevel = Math.max(this.zoomLevel / 1.2, 0.2);
            this._applyZoom();
        });

        this.el.querySelector('#btn-zoom-reset')?.addEventListener('click', () => {
            this.zoomLevel = 1;
            this._applyZoom();
        });

        this.canvas.on('mouse:wheel', (opt) => {
            if (opt.e.ctrlKey) {
                opt.e.preventDefault();
                const delta = opt.e.deltaY > 0 ? 0.9 : 1.1;
                this.zoomLevel = Math.max(0.2, Math.min(5, this.zoomLevel * delta));
                this._applyZoom();
            }
        });
    }

    _applyZoom() {
        this.canvas.setZoom(this.zoomLevel);
        const zoomDisplay = this.el.querySelector('#zoom-level');
        if (zoomDisplay) {
            zoomDisplay.textContent = `${Math.round(this.zoomLevel * 100)}%`;
        }
        this.canvas.renderAll();
    }

    _setupDeleteHandlers() {
        this.el.querySelector('#btn-delete')?.addEventListener('click', () => {
            const active = this.canvas.getActiveObject();
            if (active) {
                this.canvas.remove(active);
                this.canvas.discardActiveObject();
                this.canvas.renderAll();
            }
        });

        document.addEventListener('keydown', (e) => {
            if ((e.key === 'Delete' || e.key === 'Backspace') && this.canvas.getActiveObject()) {
                e.preventDefault();
                this.canvas.remove(this.canvas.getActiveObject());
                this.canvas.renderAll();
            }
        });
    }

    _setupPlaceholder() {
        const placeholder = new fabric.Text('Déposez des Corps ici', {
            left: this.canvas.width / 2,
            top: this.canvas.height / 2,
            fontSize: 18,
            fill: 'var(--text-muted, #94a3b8)',
            fontFamily: 'Inter, sans-serif',
            selectable: false,
            evented: false,
            originX: 'center',
            originY: 'center'
        });
        this.canvas.add(placeholder);
    }

    getCanvas() {
        return this.canvas;
    }

}

export default CanvasFeature;
