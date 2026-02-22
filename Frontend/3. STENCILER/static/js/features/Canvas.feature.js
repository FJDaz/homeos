import StencilerFeature from './base.feature.js';
import { WireframeLibrary } from '../WireframeLibrary.js';
import { InlineEditUI } from './InlineEdit.feature.js';
import CanvasLayout from './Canvas.layout.js';
import Renderer from '../Canvas.renderer.js';
import { LayoutEngine } from '../LayoutEngine.js';

/**
 * CanvasFeature (SVG Pivot V3)
 * Remplace Fabric.js par du SVG natif pour une meilleure intégration avec le Genome.
 */
class CanvasFeature extends StencilerFeature {
    constructor(id = 'canvas-zone', options = {}) {
        super(id, options);
        this.svg = null;
        this.zoomLevel = 1;
        this.viewBox = { x: 0, y: 0, w: 1000, h: 800 };
        this.el = null;
        this.selectedObject = null;
        this.drillStack = [];
        this.currentCorpsId = null;

        // --- States Drag & Drop (Mission 8C) ---
        this.isDragging = false;
        this.dragTarget = null;
        this.dragOffset = { x: 0, y: 0 };

        // --- States Selection & Handles (Mission 8E) ---
        this.isResizing = false;
        this.activeHandle = null;
        this.handlesGroup = null;
        this.resizeStart = { x: 0, y: 0, w: 0, h: 0 };

        // --- States Panning (Mission 8D) ---
        this.isSpacePressed = false;
        this.isPanning = false;

        // --- Mission 8D-BIS : Modular Snap Engine ---
        this.snapEnabled = true;
        this.snapSize = 8; // Clef 8px universelle (GRID.js G.U1)

        // --- Mission 11A : Illustrator Mode (Group Edit) ---
        this.groupEditMode = false;
        this.groupEditTarget = null;
    }

    mount(parentSelector) {
        this.el = document.querySelector(parentSelector);
        if (!this.el) return;

        this.el.classList.add('canvas-container', 'svg-mode');

        this.el.innerHTML = `
            <svg id="stenciler-svg" width="100%" height="100%" viewBox="${this.viewBox.x} ${this.viewBox.y} ${this.viewBox.w} ${this.viewBox.h}" preserveAspectRatio="xMidYMid meet">
                <defs>
                    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                        <path d="M 20 0 L 0 0 0 20" fill="none" stroke="var(--grid-line, #e2e8f0)" stroke-width="0.5"/>
                    </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#grid)" pointer-events="none" class="grid-layer"/>
                <text id="svg-level-indicator" x="20" y="30" font-size="11" fill="var(--text-muted)" font-family="Geist, sans-serif" pointer-events="none"></text>
                <g id="svg-viewport"></g>
                <text id="svg-placeholder" x="500" y="400" text-anchor="middle" font-size="18" fill="var(--text-muted, #94a3b8)" font-family="Inter, sans-serif" pointer-events="none">
                    Déposez des Corps ici (Moteur SVG)
                </text>
            </svg>
            <div class="zoom-controls">
                <button id="btn-zoom-out">-</button>
                <span id="zoom-level">100%</span>
                <button id="btn-zoom-in">+</button>
                <button id="btn-zoom-reset">Reset</button>
                <button id="btn-export-svg" title="Export SVG">📥</button>
            </div>
            <button id="btn-delete" class="delete-btn">🗑️</button>
        `;
    }

    init(genome) {
        console.log('🧬 [6D] CanvasFeature Initialized v3.2 - Density Fix');
        this.genome = genome;
        if (!this.el) return;
        this.svg = this.el.querySelector('#stenciler-svg');
        this.viewport = this.el.querySelector('#svg-viewport');
        this.placeholder = this.el.querySelector('#svg-placeholder');

        this._setupZoomControls();
        this._setupDeleteHandlers();
        this._setupSelectionHandlers();
        this._setupDrillHandlers();
        this._setupDragHandlers(); // Mission 8C
        this._setupPanningHandlers(); // Mission 8D
        this._updateGridPattern(); // Mission 8D-BIS

        document.addEventListener('corps:open', (e) => {
            const { corpsId } = e.detail;
            this.drillStack = [];
            this._renderCorps(corpsId);
        });

        // --- Mission 8D : Sync back from Transform Panel ---
        document.addEventListener('node:layout-changed', (e) => {
            const { id, layout } = e.detail;
            const node = this.viewport.querySelector(`[data-id="${id}"]`);
            if (node) {
                node.setAttribute('transform', `translate(${layout.x}, ${layout.y})`);

                // Update background hit-area width/height
                const rect = node.querySelector('.node-bg');
                if (rect) {
                    if (layout.w) rect.setAttribute('width', layout.w);
                    if (layout.h) rect.setAttribute('height', layout.h);
                }

                // Note: Re-injecter le wireframe si on veut un scaling parfait du contenu 
                // mais attention aux performances. Pour l'instant on scale la hitbox.
            }
        });

        document.addEventListener('node:style-changed', (e) => {
            const { id, style } = e.detail;
            const node = this.viewport.querySelector(`[data-id="${id}"]`);
            if (node) {
                const rect = node.querySelector('.node-bg');
                const label = node.querySelector('.node-label');

                if (rect) {
                    if (style.fill) rect.setAttribute('fill', style.fill);
                    if (style.stroke) rect.setAttribute('stroke', style.stroke);
                    if (style.strokeWidth !== undefined) rect.setAttribute('stroke-width', style.strokeWidth);
                }

                if (label && style.font) {
                    label.setAttribute('font-family', style.font);
                }
            }
        });
    }

    _renderCorps(corpsId) {
        if (!this.viewport) return;
        this.currentCorpsId = corpsId;
        this.viewport.innerHTML = '';
        const phaseData = this.genome?.n0_phases?.find(p => p.id === corpsId);
        if (!phaseData) return;

        const CORPS_COLORS = { n0_brainstorm: '#d4b2bc', n0_backend: '#a8c5fc', n0_frontend: '#a8dcc9', n0_deploy: '#edd0b0' };
        const accentColor = CORPS_COLORS[corpsId] || '#cbd5e1';

        const layout = LayoutEngine.proposeLayout(phaseData);
        this._applyLayout(layout);

        phaseData.n1_sections.forEach((organe) => {
            let pos = layout.positions.find(p => p.id === organe.id);
            // --- Surcharge Mission 8C/D : Persistence du Layout & Dimensions ---
            if (organe._layout) {
                pos = { ...pos, ...organe._layout };
            }
            if (pos) this._renderNode(organe, pos, accentColor, 0);
        });

        this._updateIndicator(phaseData.name.toUpperCase());
        this._hidePlaceholder();
    }

    _renderOrgane(organeId) {
        this.viewport.innerHTML = '';
        const organe = this.genome.n0_phases?.flatMap(p => p.n1_sections).find(s => s.id === organeId);
        if (!organe) return;

        const corps = this.genome.n0_phases.find(p => p.n1_sections.some(s => s.id === organeId));
        const CORPS_COLORS = { n0_brainstorm: '#d4b2bc', n0_backend: '#a8c5fc', n0_frontend: '#a8dcc9', n0_deploy: '#edd0b0' };
        const accentColor = CORPS_COLORS[corps?.id] || '#cbd5e1';

        const layout = CanvasLayout.calculate('n0_backend', organe.n2_features, { cardW: 240, cardH: 96 }); // G.U12
        this._applyLayout(layout);

        organe.n2_features.forEach((cell, i) => {
            let pos = layout.positions[i];
            // --- Surcharge Mission 8C/D : Persistence du Layout & Dimensions ---
            if (cell._layout) {
                pos = { ...pos, ...cell._layout };
            }
            this._renderNode(cell, pos, accentColor, 1);
        });

        this._updateIndicator(`${corps.name.toUpperCase()} › ${organe.name.toUpperCase()}`);
    }

    _renderCellule(celluleId) {
        this.viewport.innerHTML = '';
        const genome = window.stencilerApp?.genome;
        let cellule = null;
        let organe = null;
        let corps = null;

        // Trace hierarchy
        genome?.n0_phases?.forEach(p => {
            p.n1_sections?.forEach(s => {
                const found = s.n2_features?.find(f => f.id === celluleId);
                if (found) {
                    cellule = found;
                    organe = s;
                    corps = p;
                }
            });
        });

        if (!cellule) return;

        const CORPS_COLORS = { n0_brainstorm: '#d4b2bc', n0_backend: '#a8c5fc', n0_frontend: '#a8dcc9', n0_deploy: '#edd0b0' };
        const accentColor = CORPS_COLORS[corps?.id] || '#cbd5e1';

        const components = cellule.n3_components || [];
        const layout = CanvasLayout.calculate('n0_backend', components, { cardW: 240, cardH: 96 }); // G.U12 — compact, même hauteur que cellules
        this._applyLayout(layout);

        components.forEach((comp, i) => {
            let pos = layout.positions[i];
            // --- Surcharge Mission 8C/D : Persistence du Layout & Dimensions ---
            if (comp._layout) {
                pos = { ...pos, ...comp._layout };
            }
            this._renderNode(comp, pos, accentColor, 2);
        });

        this._updateIndicator(`${corps.name.toUpperCase()} › ${organe.name.toUpperCase()} › ${cellule.name.toUpperCase()}`);
    }

    _applyLayout(layout) {
        this.viewBox = layout.viewBox;
        this.svg.setAttribute('viewBox', `${this.viewBox.x} ${this.viewBox.y} ${this.viewBox.w} ${this.viewBox.h}`);
    }

    _updateIndicator(text) {
        const indicator = this.el.querySelector('#svg-level-indicator');
        if (indicator) indicator.textContent = text;
    }


    _renderNode(data, pos, color, level = 0) {
        const g = Renderer.renderNode(data, pos, color, level);

        // Hover & Selection logic remains in Feature (Interaction Controller)
        const isInteractive = true; // Mission 8C : Tout est draggable/interactif
        if (isInteractive) {
            const rect = g.querySelector('.node-bg');
            g.setAttribute('pointer-events', 'all');
            g.style.cursor = 'pointer';

            g.addEventListener('mouseenter', () => {
                rect.setAttribute('fill', 'transparent');
                rect.setAttribute('stroke', 'transparent'); // No more stuck blue borders
                rect.style.filter = '';

                const label = g.querySelector('.node-label');
                const content = g.querySelector('.wf-content');
                if (label) label.style.opacity = '1';
                if (content) content.style.opacity = '0.7';

                // Mission 8E : Show selection handles
                this._showHandles(g);
            });
            g.addEventListener('mouseleave', () => {
                const label = g.querySelector('.node-label');
                const content = g.querySelector('.wf-content');
                if (!g.classList.contains('selected')) {
                    rect.setAttribute('fill', 'transparent');
                    rect.setAttribute('stroke', 'transparent');
                    rect.style.filter = '';
                    if (label) label.style.opacity = '0.3';
                    if (content) content.style.opacity = '1';
                }
            });
        }

        this.viewport.appendChild(g);
    }

    _setupDragHandlers() {
        const getMousePos = (e) => {
            const CTM = this.viewport.getScreenCTM();
            return {
                x: (e.clientX - CTM.e) / CTM.a,
                y: (e.clientY - CTM.f) / CTM.d
            };
        };

        this.svg.addEventListener('mousedown', (e) => {
            if (this.isSpacePressed) return; // Priorité au panning
            const node = e.target.closest('.svg-node');
            if (node) {
                this.isDragging = true;
                this.dragTarget = node;

                const mouse = getMousePos(e);
                const transform = node.getAttribute('transform');
                const translateMatch = transform.match(/translate\(([-\d.]+),\s*([-\d.]+)\)/);

                const currentX = translateMatch ? parseFloat(translateMatch[1]) : 0;
                const currentY = translateMatch ? parseFloat(translateMatch[2]) : 0;

                this.dragOffset = {
                    x: mouse.x - currentX,
                    y: mouse.y - currentY
                };

                node.style.cursor = 'grabbing';
                this._selectNode(node);
                e.preventDefault();
            }
        });

        window.addEventListener('mousemove', (e) => {
            if (this.isResizing && this.dragTarget) {
                const mouse = this._getMousePos(e);
                const dx = mouse.x - this.resizeStart.mx;
                const dy = mouse.y - this.resizeStart.my;

                let nx = this.resizeStart.x;
                let ny = this.resizeStart.y;
                let nw = this.resizeStart.w;
                let nh = this.resizeStart.h;

                const id = this.activeHandle;

                if (id.includes('r')) nw += dx;
                if (id.includes('b')) nh += dy;
                if (id.includes('l')) { nx += dx; nw -= dx; }
                if (id.includes('t')) { ny += dy; nh -= dy; }

                // Snap the dimensions
                nw = Math.max(40, this._snap(nw));
                nh = Math.max(20, this._snap(nh));
                nx = this._snap(nx);
                ny = this._snap(ny);

                // Update node visual via Renderer (responsive content)
                Renderer.updateNode(this.dragTarget, nw, nh);
                this.dragTarget.setAttribute('transform', `translate(${nx}, ${ny})`);

                // Update handles group position and redraw handles
                this._showHandles(this.dragTarget);

                // Update transform panel
                document.dispatchEvent(new CustomEvent('node:moved', {
                    detail: { id: this.dragTarget.dataset.id, x: nx, y: ny, w: nw, h: nh }
                }));

                return;
            }

            if (!this.isDragging || !this.dragTarget) return;

            const mouse = this._getMousePos(e);
            let x = mouse.x - this.dragOffset.x;
            let y = mouse.y - this.dragOffset.y;

            // Mission 8D-BIS : Live Snap during drag
            x = this._snap(x);
            y = this._snap(y);

            this.dragTarget.setAttribute('transform', `translate(${x}, ${y})`);

            // --- Mission 8D : Real-time update for Transform Panel ---
            document.dispatchEvent(new CustomEvent('node:moved', {
                detail: { id: this.dragTarget.dataset.id, x, y }
            }));
        });

        window.addEventListener('mouseup', () => {
            if (this.isResizing) {
                this._updateLayoutComplete(this.dragTarget);
                this.isResizing = false;
                this.activeHandle = null;
            }

            if (this.isDragging && this.dragTarget) {
                const transform = this.dragTarget.getAttribute('transform');
                const translateMatch = transform.match(/translate\(([-\d.]+),\s*([-\d.]+)\)/);

                if (translateMatch) {
                    let rx = parseFloat(translateMatch[1]);
                    let ry = parseFloat(translateMatch[2]);

                    rx = this._snap(rx);
                    ry = this._snap(ry);

                    this.dragTarget.setAttribute('transform', `translate(${rx}, ${ry})`);
                    this.dragTarget.style.cursor = 'pointer';

                    this._updateLayoutInGenome(this.dragTarget.dataset.id, rx, ry);
                }
            }
            this.isDragging = false;
            this.dragTarget = null;
        });
    }

    _showHandles(node) {
        if (this.handlesGroup) this.handlesGroup.remove();

        const rect = node.querySelector('.node-bg');
        if (!rect) return;

        const w = parseFloat(rect.getAttribute('width'));
        const h = parseFloat(rect.getAttribute('height'));
        const transform = node.getAttribute('transform');
        const match = transform.match(/translate\(([-\d.]+),\s*([-\d.]+)\)/);
        const x = match ? parseFloat(match[1]) : 0;
        const y = match ? parseFloat(match[2]) : 0;

        this.handlesGroup = Renderer._el('g', { class: 'selection-handles' });
        this.handlesGroup.setAttribute('transform', `translate(${x}, ${y})`);

        // Border
        const border = Renderer._el('rect', {
            width: w, height: h, fill: 'none',
            stroke: 'var(--accent-bleu)', 'stroke-width': 1,
            'stroke-dasharray': '4 2', 'pointer-events': 'none'
        });
        this.handlesGroup.append(border);

        // Handles
        const hs = 8; // handle size
        const positions = [
            { id: 'tl', x: 0, y: 0, cursor: 'nw-resize' },
            { id: 't', x: w / 2, y: 0, cursor: 'n-resize' },
            { id: 'tr', x: w, y: 0, cursor: 'ne-resize' },
            { id: 'r', x: w, y: h / 2, cursor: 'e-resize' },
            { id: 'br', x: w, y: h, cursor: 'se-resize' },
            { id: 'b', x: w / 2, y: h, cursor: 's-resize' },
            { id: 'bl', x: 0, y: h, cursor: 'sw-resize' },
            { id: 'l', x: 0, y: h / 2, cursor: 'w-resize' }
        ];

        positions.forEach(p => {
            const hdl = Renderer._el('rect', {
                x: p.x - hs / 2, y: p.y - hs / 2,
                width: hs, height: hs,
                fill: 'white', stroke: 'var(--accent-bleu)',
                'stroke-width': 1.5,
                class: `handle handle-${p.id}`,
                'data-handle': p.id
            });
            hdl.style.cursor = p.cursor;

            hdl.addEventListener('mousedown', (e) => {
                this.isResizing = true;
                this.activeHandle = p.id;
                this.dragTarget = node;

                const mouse = this._getMousePos(e);
                this.resizeStart = {
                    mx: mouse.x,
                    my: mouse.y,
                    x: x, y: y,
                    w: w, h: h
                };

                e.stopPropagation();
            });

            this.handlesGroup.append(hdl);
        });

        this.viewport.appendChild(this.handlesGroup);
    }

    _getMousePos(e) {
        const CTM = this.viewport.getScreenCTM();
        return {
            x: (e.clientX - CTM.e) / CTM.a,
            y: (e.clientY - CTM.f) / CTM.d
        };
    }

    _updateLayoutComplete(node) {
        const transform = node.getAttribute('transform');
        const match = transform.match(/translate\(([-\d.]+),\s*([-\d.]+)\)/);
        const rx = match ? parseFloat(match[1]) : 0;
        const ry = match ? parseFloat(match[2]) : 0;

        const rect = node.querySelector('.node-bg');
        const rw = rect ? parseFloat(rect.getAttribute('width')) : 0;
        const rh = rect ? parseFloat(rect.getAttribute('height')) : 0;

        this._updateLayoutInGenome(node.dataset.id, rx, ry, rw, rh);
    }

    _snap(value) {
        if (!this.snapEnabled) return value;
        return Math.round(value / this.snapSize) * this.snapSize;
    }

    _updateGridPattern() {
        const pattern = this.svg.querySelector('#grid');
        if (pattern) {
            pattern.setAttribute('width', this.snapSize);
            pattern.setAttribute('height', this.snapSize);
            const path = pattern.querySelector('path');
            if (path) {
                path.setAttribute('d', `M ${this.snapSize} 0 L 0 0 0 ${this.snapSize}`);
            }
        }
    }

    _setupPanningHandlers() {
        window.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && !this.isSpacePressed) {
                if (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA') return;
                this.isSpacePressed = true;
                this.svg.style.cursor = 'grab';
                e.preventDefault();
            }
        });

        window.addEventListener('keyup', (e) => {
            if (e.code === 'Space') {
                this.isSpacePressed = false;
                this.isPanning = false;
                this.svg.style.cursor = 'default';
            }
        });

        let startPoint = { x: 0, y: 0 };

        this.svg.addEventListener('mousedown', (e) => {
            if (this.isSpacePressed) {
                this.isPanning = true;
                this.svg.style.cursor = 'grabbing';
                startPoint = { x: e.clientX, y: e.clientY };
                e.stopImmediatePropagation();
            }
        });

        window.addEventListener('mousemove', (e) => {
            if (this.isPanning) {
                const dx = (e.clientX - startPoint.x) * (this.viewBox.w / this.el.clientWidth);
                const dy = (e.clientY - startPoint.y) * (this.viewBox.h / this.el.clientHeight);

                this.viewBox.x -= dx;
                this.viewBox.y -= dy;

                this.svg.setAttribute('viewBox', `${this.viewBox.x} ${this.viewBox.y} ${this.viewBox.w} ${this.viewBox.h}`);
                startPoint = { x: e.clientX, y: e.clientY };
            }
        });

        window.addEventListener('mouseup', () => {
            if (this.isPanning) {
                this.isPanning = false;
                this.svg.style.cursor = this.isSpacePressed ? 'grab' : 'default';
            }
        });
    }

    _updateLayoutInGenome(id, x, y, w, h) {
        const findAndApply = (list) => {
            for (const item of list) {
                if (item.id === id) {
                    item._layout = item._layout || {};
                    item._layout.x = x;
                    item._layout.y = y;
                    if (w) item._layout.w = w;
                    if (h) item._layout.h = h;
                    return true;
                }
                if (item.n1_sections && findAndApply(item.n1_sections)) return true;
                if (item.n2_features && findAndApply(item.n2_features)) return true;
                if (item.n3_components && findAndApply(item.n3_components)) return true;
            }
            return false;
        };

        if (findAndApply(this.genome.n0_phases)) {
            console.log(`📍 Layout persistent pour ${id} :`, { x, y });
            document.dispatchEvent(new CustomEvent('genome:updated'));
        }
    }

    _setupSelectionHandlers() {
        // Mission 9D : Edition en ligne (N3)
        this.svg.addEventListener('dblclick', (e) => {
            const atomNode = e.target.closest('.atom-node');
            if (!atomNode || e.target.tagName !== 'text') return;

            // On ne veut pas déclencher le drill up/down par erreur
            e.stopPropagation();

            const dataId = atomNode.dataset.id;
            const nodeData = this._findInGenome(dataId);
            if (!nodeData) return;

            // Le wireframe édite uniquement le nom — method/endpoint = détail technique, hors scope DA
            InlineEditUI.mount(e.target, nodeData, 'name', () => {
                // Refresh local rendering
                Renderer.updateNode(atomNode, atomNode._layout?.w || 280, atomNode._layout?.h || 60);

                // Persistence
                document.dispatchEvent(new CustomEvent('genome:updated', {
                    detail: { type: 'n3', id: dataId, genome: this.genome }
                }));
            });
        });

        this.svg.addEventListener('click', (e) => {
            // --- Mission 11A : Sortie Illustrator Mode ---
            if (this.groupEditMode) {
                const node = e.target.closest('.svg-node');
                if (!node || node !== this.groupEditTarget) {
                    this._exitGroupEdit();
                    return;
                }
            }

            const node = e.target.closest('.svg-node');
            if (node) {
                this._selectNode(node);
                if (node.classList.contains('corps-node')) {
                    document.dispatchEvent(new CustomEvent('organe:selected', {
                        detail: { organeId: node.dataset.id, genome: window.stencilerApp?.genome }
                    }));
                }
            } else if (e.target === this.svg || e.target.classList.contains('grid-layer')) {
                this._deselectAll();
            }
        });
    }

    _setupDrillHandlers() {
        this.svg.addEventListener('dblclick', (e) => {
            const node = e.target.closest('.svg-node');
            if (node) {
                e.stopPropagation();

                // --- Restauration du Vrai Drill-Down ---
                // On détecte le niveau actuel et on descend
                const id = node.dataset.id;
                if (node.classList.contains('corps-node')) {
                    this._drillInto(id, 1); // Descend dans l'Organe
                } else if (node.classList.contains('cell-node')) {
                    this._drillInto(id, 2); // Descend dans la Cellule
                } else if (node.classList.contains('atom-node')) {
                    // Les atomes sont le niveau le plus bas, on peut déclencher un event
                    document.dispatchEvent(new CustomEvent('atom:selected', { detail: { atomId: id } }));
                } else {
                    // Repli: on tente de déterminer par l'ID ou on monte d'un niveau générique
                    // Sur les Canvas N0: nodes sont des Organes (donc level 1)
                    this._drillInto(id, 1);
                }
            } else if (e.target === this.svg || e.target.classList.contains('grid-layer')) {
                this._drillUp();
            }
        });
    }

    _drillInto(id, level) {
        if (this.drillStack.some(s => s.id === id)) return;
        this.drillStack.push({ level, id });

        console.log(`[Canvas] Drill down level ${level} -> ${id}`);

        if (level === 1) {
            this._renderOrgane(id);
            document.dispatchEvent(new CustomEvent('organe:selected', {
                detail: { organeId: id, genome: window.stencilerApp?.genome }
            }));
        }
        if (level === 2) {
            this._renderCellule(id);
            document.dispatchEvent(new CustomEvent('cellule:selected', {
                detail: { celluleId: id }
            }));
        }
    }

    _drillUp() {
        if (this.drillStack.length === 0) return;
        this.drillStack.pop();

        console.log(`[Canvas] Drill up. Remaining stack:`, this.drillStack);

        if (this.drillStack.length === 0) {
            if (this.currentCorpsId) {
                this._renderCorps(this.currentCorpsId);
                document.dispatchEvent(new CustomEvent('corps:drill-back', {
                    detail: { corpsId: this.currentCorpsId }
                }));
            }
        } else {
            const prev = this.drillStack[this.drillStack.length - 1];
            if (prev.level === 1) {
                this._renderOrgane(prev.id);
                document.dispatchEvent(new CustomEvent('organe:selected', {
                    detail: { organeId: prev.id, genome: window.stencilerApp?.genome }
                }));
            }
            if (prev.level === 2) {
                this._renderCellule(prev.id);
                document.dispatchEvent(new CustomEvent('cellule:selected', {
                    detail: { celluleId: prev.id }
                }));
            }
        }
    }

    // --- MISSION 11A : Illustrator Mode (Group Edit) ---

    _enterGroupEdit(node) {
        this.groupEditMode = true;
        this.groupEditTarget = node;

        // Feedback visuel sur le conteneur
        const bg = node.querySelector('.node-bg');
        if (bg) {
            bg.setAttribute('stroke', 'var(--accent-bleu)');
            bg.setAttribute('stroke-dasharray', '5 3');
            bg.setAttribute('stroke-width', '2');
        }

        // Estomper les autres nodes
        this.viewport.querySelectorAll('.svg-node').forEach(n => {
            if (n !== node) n.style.opacity = '0.25';
        });

        // --- Mission 11A : Mode Illustrateur ---
        // Activation events internes sur les primitives SVG
        const content = node.querySelector('.bottom-up-composition');
        if (content) {
            content.setAttribute('pointer-events', 'all');
            // On rend toutes les primitives profondes cliquables
            content.querySelectorAll('rect, text, circle, path').forEach(prim => {
                prim.setAttribute('pointer-events', 'all');
                prim.style.cursor = 'move';

                // Mémoriser la callback pour la nettoyer à l'exit
                prim._gc = (e) => {
                    e.stopPropagation();
                    this._selectPrimitive(prim, node);
                };
                prim.addEventListener('click', prim._gc);

                // Setup drag pour chaque primitive
                this._setupPrimitiveDrag(prim, node);
            });
        }

        console.log('🎨 [11A] Illustrator Mode: Entered group edit for', node.dataset.id);
    }

    _selectPrimitive(prim, parentNode) {
        // Nettoyer la sélection précédente
        parentNode.querySelectorAll('.prim-sel').forEach(el => el.remove());

        const bb = prim.getBBox();
        const ov = Renderer._el('rect', {
            x: bb.x - 2, y: bb.y - 2,
            width: bb.width + 4, height: bb.height + 4,
            fill: 'none', stroke: 'var(--accent-bleu)',
            'stroke-width': '1.5', 'stroke-dasharray': '3 2',
            'pointer-events': 'none',
            class: 'prim-sel'
        });
        parentNode.appendChild(ov);

        this._setupPrimitiveDrag(prim, ov);
    }

    _setupPrimitiveDrag(prim, overlay) {
        const getXY = () => {
            const isCircle = prim.tagName === 'circle';
            return {
                x: parseFloat(prim.getAttribute(isCircle ? 'cx' : 'x') || 0),
                y: parseFloat(prim.getAttribute(isCircle ? 'cy' : 'y') || 0)
            };
        };

        const setXY = (x, y) => {
            const isCircle = prim.tagName === 'circle';
            prim.setAttribute(isCircle ? 'cx' : 'x', x);
            prim.setAttribute(isCircle ? 'cy' : 'y', y);
        };

        let dragging = false;
        let startMouse = { x: 0, y: 0 };
        let startPos = { x: 0, y: 0 };

        const onMouseDown = (e) => {
            dragging = true;
            startMouse = this._getMousePos(e);
            startPos = getXY();
            e.stopPropagation();
        };

        const onMouseMove = (e) => {
            if (!dragging) return;
            const currentMouse = this._getMousePos(e);
            const dx = currentMouse.x - startMouse.x;
            const dy = currentMouse.y - startMouse.y;

            setXY(startPos.x + dx, startPos.y + dy);

            // Mettre à jour l'overlay
            const bb = prim.getBBox();
            overlay.setAttribute('x', bb.x - 2);
            overlay.setAttribute('y', bb.y - 2);
            overlay.setAttribute('width', bb.width + 4);
            overlay.setAttribute('height', bb.height + 4);
        };

        const onMouseUp = () => {
            dragging = false;
            window.removeEventListener('mousemove', onMouseMove);
            window.removeEventListener('mouseup', onMouseUp);
        };

        prim.addEventListener('mousedown', onMouseDown);
        window.addEventListener('mousemove', onMouseMove);
        window.addEventListener('mouseup', onMouseUp);
    }

    _exitGroupEdit() {
        const node = this.groupEditTarget;
        if (!node) return;

        // Reset visual feedback
        const bg = node.querySelector('.node-bg');
        if (bg) {
            bg.setAttribute('stroke', 'var(--border-subtle)');
            bg.removeAttribute('stroke-dasharray');
            bg.setAttribute('stroke-width', '1.5');
        }

        // Restore opacity of other elements
        this.viewport.querySelectorAll('.svg-node').forEach(n => {
            n.style.opacity = '1';
        });

        // Désactiver les events sur le contenu
        const content = node.querySelector('.bottom-up-composition');
        if (content) {
            content.setAttribute('pointer-events', 'none');
            content.querySelectorAll('rect, text, circle, path').forEach(prim => {
                if (prim._gc) {
                    prim.removeEventListener('click', prim._gc);
                    delete prim._gc;
                }
                prim.setAttribute('pointer-events', 'none');
                prim.style.cursor = '';
            });
        }

        // Supprimer la sélection
        node.querySelectorAll('.prim-sel').forEach(el => el.remove());

        this.groupEditMode = false;
        this.groupEditTarget = null;
        console.log('🎨 [11A] Illustrator Mode: Exited group edit');
    }



    /**
     * Recherche un node dans le génome local par son ID.
     */
    _findInGenome(id) {
        let found = null;
        const search = (items) => {
            if (found) return;
            for (const item of items) {
                if (item.id === id) { found = item; return; }
                if (item.n1_sections) search(item.n1_sections);
                if (item.n2_features) search(item.n2_features);
                if (item.n3_components) search(item.n3_components);
                if (item.n0_phases) search(item.n0_phases);
            }
        };
        search(this.genome?.n0_phases || []);
        return found;
    }

    _selectNode(node) {
        this._deselectAll();
        this.selectedObject = node;
        node.classList.add('selected');
        const rect = node.querySelector('.node-bg');
        if (rect) {
            rect.setAttribute('stroke', 'transparent'); // Alpha 0 pour selection
            rect.style.filter = '';
        }
        const label = node.querySelector('.node-label');
        const content = node.querySelector('.wf-content');
        if (label) label.style.opacity = '1';
        if (content) content.style.opacity = '0.4';

        // Mission 9C : Dispatch selection event
        document.dispatchEvent(new CustomEvent('canvas:node:selected', {
            detail: { id: node.dataset.id, nodeData: { ...node.dataset } }
        }));

        // Mission 8E : Show selection handles
        this._showHandles(node);
    }

    _deselectAll() {
        this.el.querySelectorAll('.svg-node.selected').forEach(node => {
            node.classList.remove('selected');
            const rect = node.querySelector('.node-bg');
            const label = node.querySelector('.node-label');
            const content = node.querySelector('.wf-content');
            if (rect) {
                rect.setAttribute('stroke', 'var(--border-subtle, #cbd5e1)');
                rect.style.filter = 'drop-shadow(0 2px 4px rgba(0,0,0,0.05))';
            }
            if (label) label.style.opacity = '0';
            if (content) content.style.opacity = '1';
        });
        if (this.handlesGroup) this.handlesGroup.remove();
        this.handlesGroup = null;
        this.selectedObject = null;

        // Mission 9C : Dispatch selection cleared
        document.dispatchEvent(new CustomEvent('canvas:selection:cleared'));
    }

    _setupZoomControls() {
        const updateViewBox = () => {
            this.svg.setAttribute('viewBox', `${this.viewBox.x} ${this.viewBox.y} ${this.viewBox.w} ${this.viewBox.h}`);
            const zoomDisplay = this.el.querySelector('#zoom-level');
            if (zoomDisplay) zoomDisplay.textContent = `${Math.round(1000 / this.viewBox.w * 100)}%`;
        };

        this.el.querySelector('#btn-zoom-in')?.addEventListener('click', () => {
            this.viewBox.w *= 0.8;
            this.viewBox.h *= 0.8;
            updateViewBox();
        });

        this.el.querySelector('#btn-zoom-out')?.addEventListener('click', () => {
            this.viewBox.w *= 1.2;
            this.viewBox.h *= 1.2;
            updateViewBox();
        });

        this.el.querySelector('#btn-zoom-reset')?.addEventListener('click', () => {
            this.viewBox = { x: 0, y: 0, w: 1000, h: 800 };
            updateViewBox();
        });

        this.el.querySelector('#btn-export-svg')?.addEventListener('click', () => {
            const svgData = new XMLSerializer().serializeToString(this.svg);
            const link = document.createElement('a');
            link.href = URL.createObjectURL(new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' }));
            link.download = 'stenciler_export.svg';
            link.click();
        });
    }

    _setupDeleteHandlers() {
        this.el.querySelector('#btn-delete')?.addEventListener('click', () => {
            if (this.selectedObject) {
                this.selectedObject.remove();
                this.selectedObject = null;
            }
        });

        document.addEventListener('keydown', (e) => {
            if ((e.key === 'Delete' || e.key === 'Backspace') && this.selectedObject) {
                if (document.activeElement.tagName !== 'INPUT') {
                    this.selectedObject.remove();
                    this.selectedObject = null;
                }
            }
        });
    }

    _hidePlaceholder() {
        if (this.placeholder) this.placeholder.setAttribute('display', 'none');
    }

    getSVG() {
        return this.svg;
    }
}

export default CanvasFeature;
