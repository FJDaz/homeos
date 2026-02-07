// HomeOS Canvas - Figma Like
// Canvas interactif avec outils de dessin

class CanvasFigma {
    constructor() {
        this.canvas = document.getElementById('main-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.wrapper = document.getElementById('canvas-wrapper');
        this.selectionBox = document.getElementById('selection-box');
        
        // Configuration
        this.canvasWidth = 1920;
        this.canvasHeight = 1080;
        this.scale = 1;
        this.minScale = 0.1;
        this.maxScale = 5;
        
        // État
        this.currentTool = 'select';
        this.isDrawing = false;
        this.isPanning = false;
        this.isMoving = false;
        this.startX = 0;
        this.startY = 0;
        this.lastX = 0;
        this.lastY = 0;
        this.panX = 0;
        this.panY = 0;
        
        // Éléments
        this.elements = [];
        this.selectedElement = null;
        this.nextId = 1;
        
        // Grille
        this.showGrid = true;
        this.snapToGrid = true;
        this.gridSize = 20;
        
        // Historique
        this.history = [];
        this.historyIndex = -1;
        
        this.init();
    }
    
    init() {
        this.setupCanvas();
        this.setupEventListeners();
        this.setupTools();
        this.setupProperties();
        this.render();
        this.saveState();
    }
    
    setupCanvas() {
        this.canvas.width = this.canvasWidth;
        this.canvas.height = this.canvasHeight;
        this.updateCanvasTransform();
    }
    
    setupEventListeners() {
        // Mouse events
        this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('mouseup', (e) => this.handleMouseUp(e));
        this.canvas.addEventListener('wheel', (e) => this.handleWheel(e));
        this.canvas.addEventListener('contextmenu', (e) => this.handleContextMenu(e));
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
        
        // Window resize
        window.addEventListener('resize', () => this.render());
        
        // Context menu
        document.getElementById('context-menu').addEventListener('click', (e) => {
            if (e.target.classList.contains('context-item')) {
                this.handleContextAction(e.target.dataset.action);
            }
        });
        
        // Click outside to close context menu
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.context-menu')) {
                document.getElementById('context-menu').classList.remove('active');
            }
        });
    }
    
    setupTools() {
        const toolButtons = document.querySelectorAll('.tool-btn');
        toolButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                toolButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentTool = btn.dataset.tool;
                this.updateCursor();
            });
        });
        
        // Zoom controls
        document.getElementById('zoom-in').addEventListener('click', () => this.zoom(0.1));
        document.getElementById('zoom-out').addEventListener('click', () => this.zoom(-0.1));
        document.getElementById('reset-view').addEventListener('click', () => this.resetView());
        
        // Grid toggles
        document.getElementById('show-grid').addEventListener('change', (e) => {
            this.showGrid = e.target.checked;
            this.render();
        });
        
        document.getElementById('snap-grid').addEventListener('change', (e) => {
            this.snapToGrid = e.target.checked;
        });
    }
    
    setupProperties() {
        // Propriétés
        const props = ['x', 'y', 'w', 'h'];
        props.forEach(prop => {
            document.getElementById(`prop-${prop}`).addEventListener('change', (e) => {
                if (this.selectedElement) {
                    this.selectedElement[prop] = parseInt(e.target.value) || 0;
                    this.render();
                    this.saveState();
                }
            });
        });
        
        // Fill
        document.getElementById('fill-color').addEventListener('input', (e) => {
            if (this.selectedElement) {
                this.selectedElement.fillColor = e.target.value;
                this.render();
                this.saveState();
            }
        });
        
        document.getElementById('fill-opacity').addEventListener('input', (e) => {
            if (this.selectedElement) {
                this.selectedElement.fillOpacity = e.target.value / 100;
                this.render();
            }
        });
        
        // Stroke
        document.getElementById('stroke-color').addEventListener('input', (e) => {
            if (this.selectedElement) {
                this.selectedElement.strokeColor = e.target.value;
                this.render();
                this.saveState();
            }
        });
        
        document.getElementById('stroke-width').addEventListener('change', (e) => {
            if (this.selectedElement) {
                this.selectedElement.strokeWidth = parseInt(e.target.value) || 0;
                this.render();
                this.saveState();
            }
        });
        
        // Corner radius
        document.getElementById('corner-radius').addEventListener('input', (e) => {
            if (this.selectedElement) {
                this.selectedElement.cornerRadius = parseInt(e.target.value) || 0;
                this.render();
            }
        });
        
        // Opacity
        document.getElementById('opacity').addEventListener('input', (e) => {
            if (this.selectedElement) {
                this.selectedElement.opacity = e.target.value / 100;
                this.render();
            }
        });
    }
    
    // Coordonnées
    getMousePos(e) {
        const rect = this.canvas.getBoundingClientRect();
        return {
            x: (e.clientX - rect.left - this.panX) / this.scale,
            y: (e.clientY - rect.top - this.panY) / this.scale
        };
    }
    
    snapToGridValue(value) {
        if (!this.snapToGrid) return value;
        return Math.round(value / this.gridSize) * this.gridSize;
    }
    
    // Event Handlers
    handleMouseDown(e) {
        if (e.button === 1 || (e.button === 0 && e.spaceKey)) {
            // Pan
            this.isPanning = true;
            this.lastX = e.clientX;
            this.lastY = e.clientY;
            this.wrapper.classList.add('panning');
            return;
        }
        
        if (e.button !== 0) return;
        
        const pos = this.getMousePos(e);
        this.startX = this.snapToGridValue(pos.x);
        this.startY = this.snapToGridValue(pos.y);
        
        if (this.currentTool === 'select') {
            // Check if clicking on an element
            const clicked = this.getElementAt(pos.x, pos.y);
            if (clicked) {
                this.selectElement(clicked);
                this.isMoving = true;
            } else {
                this.selectElement(null);
                this.isDrawing = true;
                this.selectionBox.style.left = e.clientX + 'px';
                this.selectionBox.style.top = e.clientY + 'px';
                this.selectionBox.style.width = '0px';
                this.selectionBox.style.height = '0px';
                this.selectionBox.classList.add('active');
            }
        } else {
            this.isDrawing = true;
        }
    }
    
    handleMouseMove(e) {
        const pos = this.getMousePos(e);
        const x = this.snapToGridValue(pos.x);
        const y = this.snapToGridValue(pos.y);
        
        // Update status bar
        document.getElementById('mouse-pos').textContent = `${Math.round(x)}, ${Math.round(y)}`;
        
        if (this.isPanning) {
            const dx = e.clientX - this.lastX;
            const dy = e.clientY - this.lastY;
            this.panX += dx;
            this.panY += dy;
            this.lastX = e.clientX;
            this.lastY = e.clientY;
            this.updateCanvasTransform();
            return;
        }
        
        if (!this.isDrawing && !this.isMoving) return;
        
        if (this.currentTool === 'select') {
            if (this.isMoving && this.selectedElement) {
                const dx = x - this.startX;
                const dy = y - this.startY;
                this.selectedElement.x += dx;
                this.selectedElement.y += dy;
                this.startX = x;
                this.startY = y;
                this.updateProperties();
                this.render();
            } else if (this.isDrawing) {
                // Selection box
                const rect = this.canvas.getBoundingClientRect();
                const boxX = Math.min(e.clientX, rect.left + this.startX * this.scale + this.panX);
                const boxY = Math.min(e.clientY, rect.top + this.startY * this.scale + this.panY);
                const boxW = Math.abs(e.clientX - (rect.left + this.startX * this.scale + this.panX));
                const boxH = Math.abs(e.clientY - (rect.top + this.startY * this.scale + this.panY));
                
                this.selectionBox.style.left = boxX + 'px';
                this.selectionBox.style.top = boxY + 'px';
                this.selectionBox.style.width = boxW + 'px';
                this.selectionBox.style.height = boxH + 'px';
            }
        } else {
            // Preview shape
            this.render();
            this.drawPreview(x, y);
        }
    }
    
    handleMouseUp(e) {
        if (this.isPanning) {
            this.isPanning = false;
            this.wrapper.classList.remove('panning');
            return;
        }
        
        if (!this.isDrawing && !this.isMoving) return;
        
        const pos = this.getMousePos(e);
        const x = this.snapToGridValue(pos.x);
        const y = this.snapToGridValue(pos.y);
        
        if (this.currentTool === 'select') {
            if (this.isDrawing) {
                this.selectionBox.classList.remove('active');
            }
        } else if (this.isDrawing) {
            this.createElement(this.startX, this.startY, x, y);
        }
        
        this.isDrawing = false;
        this.isMoving = false;
        this.render();
        this.saveState();
    }
    
    handleWheel(e) {
        if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            const delta = e.deltaY > 0 ? -0.1 : 0.1;
            this.zoom(delta);
        }
    }
    
    handleContextMenu(e) {
        e.preventDefault();
        const menu = document.getElementById('context-menu');
        menu.style.left = e.pageX + 'px';
        menu.style.top = e.pageY + 'px';
        menu.classList.add('active');
    }
    
    handleContextAction(action) {
        document.getElementById('context-menu').classList.remove('active');
        
        switch(action) {
            case 'duplicate':
                this.duplicateSelected();
                break;
            case 'delete':
                this.deleteSelected();
                break;
            case 'bring-front':
                this.bringToFront();
                break;
            case 'send-back':
                this.sendToBack();
                break;
        }
    }
    
    handleKeyDown(e) {
        // Tool shortcuts
        switch(e.key.toLowerCase()) {
            case 'v':
                this.setTool('select');
                break;
            case 'r':
                this.setTool('rectangle');
                break;
            case 'o':
                this.setTool('circle');
                break;
            case 't':
                this.setTool('text');
                break;
            case 'l':
                this.setTool('line');
                break;
            case 'delete':
            case 'backspace':
                if (this.selectedElement) {
                    this.deleteSelected();
                }
                break;
            case 'd':
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    this.duplicateSelected();
                }
                break;
            case 'z':
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    if (e.shiftKey) {
                        this.redo();
                    } else {
                        this.undo();
                    }
                }
                break;
        }
    }
    
    // Tools
    setTool(tool) {
        this.currentTool = tool;
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.tool === tool) {
                btn.classList.add('active');
            }
        });
        this.updateCursor();
    }
    
    updateCursor() {
        const cursors = {
            select: 'default',
            rectangle: 'crosshair',
            circle: 'crosshair',
            text: 'text',
            line: 'crosshair'
        };
        this.canvas.style.cursor = cursors[this.currentTool] || 'default';
    }
    
    // Elements
    createElement(x1, y1, x2, y2) {
        const element = {
            id: this.nextId++,
            type: this.currentTool,
            x: Math.min(x1, x2),
            y: Math.min(y1, y2),
            w: Math.abs(x2 - x1) || 1,
            h: Math.abs(y2 - y1) || 1,
            fillColor: document.getElementById('fill-color').value,
            fillOpacity: 1,
            strokeColor: document.getElementById('stroke-color').value,
            strokeWidth: parseInt(document.getElementById('stroke-width').value) || 0,
            cornerRadius: parseInt(document.getElementById('corner-radius').value) || 0,
            opacity: 1
        };
        
        if (this.currentTool === 'line') {
            element.x2 = x2;
            element.y2 = y2;
        }
        
        this.elements.push(element);
        this.addLayerItem(element);
        this.selectElement(element);
    }
    
    getElementAt(x, y) {
        for (let i = this.elements.length - 1; i >= 0; i--) {
            const el = this.elements[i];
            if (x >= el.x && x <= el.x + el.w && y >= el.y && y <= el.y + el.h) {
                return el;
            }
        }
        return null;
    }
    
    selectElement(element) {
        this.selectedElement = element;
        
        // Update layer selection
        document.querySelectorAll('.layer-item').forEach(item => {
            item.classList.remove('selected');
            if (element && parseInt(item.dataset.id) === element.id) {
                item.classList.add('selected');
            }
        });
        
        this.updateProperties();
        this.render();
    }
    
    deleteSelected() {
        if (!this.selectedElement) return;
        
        const index = this.elements.findIndex(e => e.id === this.selectedElement.id);
        if (index > -1) {
            this.elements.splice(index, 1);
            this.removeLayerItem(this.selectedElement.id);
            this.selectedElement = null;
            this.updateProperties();
            this.render();
            this.saveState();
        }
    }
    
    duplicateSelected() {
        if (!this.selectedElement) return;
        
        const copy = {
            ...this.selectedElement,
            id: this.nextId++,
            x: this.selectedElement.x + 20,
            y: this.selectedElement.y + 20
        };
        
        this.elements.push(copy);
        this.addLayerItem(copy);
        this.selectElement(copy);
        this.saveState();
    }
    
    bringToFront() {
        if (!this.selectedElement) return;
        const index = this.elements.indexOf(this.selectedElement);
        if (index > -1) {
            this.elements.splice(index, 1);
            this.elements.push(this.selectedElement);
            this.render();
            this.saveState();
        }
    }
    
    sendToBack() {
        if (!this.selectedElement) return;
        const index = this.elements.indexOf(this.selectedElement);
        if (index > -1) {
            this.elements.splice(index, 1);
            this.elements.unshift(this.selectedElement);
            this.render();
            this.saveState();
        }
    }
    
    // Layers
    addLayerItem(element) {
        const list = document.getElementById('layers-list');
        const li = document.createElement('li');
        li.className = 'layer-item';
        li.dataset.id = element.id;
        li.innerHTML = `
            <span class="layer-icon">${this.getLayerIcon(element.type)}</span>
            <span class="layer-name">${element.type} ${element.id}</span>
        `;
        li.addEventListener('click', () => this.selectElement(element));
        list.insertBefore(li, list.firstChild);
    }
    
    removeLayerItem(id) {
        const item = document.querySelector(`.layer-item[data-id="${id}"]`);
        if (item) item.remove();
    }
    
    getLayerIcon(type) {
        const icons = {
            rectangle: '▭',
            circle: '○',
            text: 'T',
            line: '/'
        };
        return icons[type] || '◆';
    }
    
    // Properties
    updateProperties() {
        const el = this.selectedElement;
        if (el) {
            document.getElementById('prop-x').value = Math.round(el.x);
            document.getElementById('prop-y').value = Math.round(el.y);
            document.getElementById('prop-w').value = Math.round(el.w);
            document.getElementById('prop-h').value = Math.round(el.h);
            document.getElementById('fill-color').value = el.fillColor;
            document.getElementById('stroke-color').value = el.strokeColor;
            document.getElementById('stroke-width').value = el.strokeWidth;
            document.getElementById('corner-radius').value = el.cornerRadius;
        } else {
            ['x', 'y', 'w', 'h'].forEach(p => document.getElementById(`prop-${p}`).value = 0);
        }
    }
    
    // Zoom & Pan
    zoom(delta) {
        const newScale = Math.max(this.minScale, Math.min(this.maxScale, this.scale + delta));
        this.scale = newScale;
        this.updateCanvasTransform();
        document.getElementById('zoom-level').textContent = Math.round(this.scale * 100) + '%';
    }
    
    resetView() {
        this.scale = 1;
        this.panX = 0;
        this.panY = 0;
        this.updateCanvasTransform();
        document.getElementById('zoom-level').textContent = '100%';
    }
    
    updateCanvasTransform() {
        this.canvas.style.transform = `translate(-50%, -50%) translate(${this.panX}px, ${this.panY}px) scale(${this.scale})`;
    }
    
    // History
    saveState() {
        this.history = this.history.slice(0, this.historyIndex + 1);
        this.history.push(JSON.stringify(this.elements));
        this.historyIndex++;
    }
    
    undo() {
        if (this.historyIndex > 0) {
            this.historyIndex--;
            this.elements = JSON.parse(this.history[this.historyIndex]);
            this.render();
            this.rebuildLayers();
        }
    }
    
    redo() {
        if (this.historyIndex < this.history.length - 1) {
            this.historyIndex++;
            this.elements = JSON.parse(this.history[this.historyIndex]);
            this.render();
            this.rebuildLayers();
        }
    }
    
    rebuildLayers() {
        document.getElementById('layers-list').innerHTML = '';
        this.elements.forEach(el => this.addLayerItem(el));
    }
    
    // Rendering
    render() {
        // Clear
        this.ctx.clearRect(0, 0, this.canvasWidth, this.canvasHeight);
        
        // Draw grid
        if (this.showGrid) {
            this.drawGrid();
        }
        
        // Draw elements
        this.elements.forEach(el => this.drawElement(el));
        
        // Draw selection
        if (this.selectedElement) {
            this.drawSelection();
        }
    }
    
    drawGrid() {
        this.ctx.strokeStyle = '#e5e5e5';
        this.ctx.lineWidth = 1;
        
        for (let x = 0; x <= this.canvasWidth; x += this.gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvasHeight);
            this.ctx.stroke();
        }
        
        for (let y = 0; y <= this.canvasHeight; y += this.gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvasWidth, y);
            this.ctx.stroke();
        }
    }
    
    drawElement(el) {
        this.ctx.save();
        this.ctx.globalAlpha = el.opacity;
        
        // Fill
        if (el.fillOpacity > 0) {
            this.ctx.fillStyle = el.fillColor;
            this.ctx.globalAlpha = el.opacity * el.fillOpacity;
            
            if (el.type === 'rectangle') {
                this.roundRect(el.x, el.y, el.w, el.h, el.cornerRadius);
                this.ctx.fill();
            } else if (el.type === 'circle') {
                this.ctx.beginPath();
                this.ctx.ellipse(el.x + el.w/2, el.y + el.h/2, el.w/2, el.h/2, 0, 0, Math.PI * 2);
                this.ctx.fill();
            }
        }
        
        // Stroke
        if (el.strokeWidth > 0) {
            this.ctx.strokeStyle = el.strokeColor;
            this.ctx.lineWidth = el.strokeWidth;
            this.ctx.globalAlpha = el.opacity;
            
            if (el.type === 'rectangle') {
                this.roundRect(el.x, el.y, el.w, el.h, el.cornerRadius);
                this.ctx.stroke();
            } else if (el.type === 'circle') {
                this.ctx.beginPath();
                this.ctx.ellipse(el.x + el.w/2, el.y + el.h/2, el.w/2, el.h/2, 0, 0, Math.PI * 2);
                this.ctx.stroke();
            } else if (el.type === 'line') {
                this.ctx.beginPath();
                this.ctx.moveTo(el.x, el.y);
                this.ctx.lineTo(el.x2, el.y2);
                this.ctx.stroke();
            }
        }
        
        // Text
        if (el.type === 'text') {
            this.ctx.fillStyle = el.fillColor;
            this.ctx.font = '16px sans-serif';
            this.ctx.fillText('Text', el.x, el.y + 16);
        }
        
        this.ctx.restore();
    }
    
    drawPreview(x, y) {
        this.ctx.save();
        this.ctx.strokeStyle = '#0d99ff';
        this.ctx.lineWidth = 1;
        this.ctx.setLineDash([5, 5]);
        
        const w = x - this.startX;
        const h = y - this.startY;
        
        if (this.currentTool === 'rectangle') {
            this.ctx.strokeRect(this.startX, this.startY, w, h);
        } else if (this.currentTool === 'circle') {
            this.ctx.beginPath();
            this.ctx.ellipse(
                this.startX + w/2,
                this.startY + h/2,
                Math.abs(w/2),
                Math.abs(h/2),
                0, 0, Math.PI * 2
            );
            this.ctx.stroke();
        } else if (this.currentTool === 'line') {
            this.ctx.beginPath();
            this.ctx.moveTo(this.startX, this.startY);
            this.ctx.lineTo(x, y);
            this.ctx.stroke();
        }
        
        this.ctx.restore();
    }
    
    drawSelection() {
        if (!this.selectedElement) return;
        
        const el = this.selectedElement;
        this.ctx.save();
        this.ctx.strokeStyle = '#0d99ff';
        this.ctx.lineWidth = 2;
        this.ctx.setLineDash([4, 4]);
        
        if (el.type === 'line') {
            // Line selection
        } else {
            this.ctx.strokeRect(el.x - 2, el.y - 2, el.w + 4, el.h + 4);
        }
        
        this.ctx.restore();
    }
    
    roundRect(x, y, w, h, r) {
        const radius = Math.min(r, w/2, h/2);
        this.ctx.beginPath();
        this.ctx.moveTo(x + radius, y);
        this.ctx.lineTo(x + w - radius, y);
        this.ctx.quadraticCurveTo(x + w, y, x + w, y + radius);
        this.ctx.lineTo(x + w, y + h - radius);
        this.ctx.quadraticCurveTo(x + w, y + h, x + w - radius, y + h);
        this.ctx.lineTo(x + radius, y + h);
        this.ctx.quadraticCurveTo(x, y + h, x, y + h - radius);
        this.ctx.lineTo(x, y + radius);
        this.ctx.quadraticCurveTo(x, y, x + radius, y);
        this.ctx.closePath();
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    new CanvasFigma();
});
