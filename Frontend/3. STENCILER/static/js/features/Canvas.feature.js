import StencilerFeature from './base.feature.js';
import { PrimOverlay } from '../PrimOverlay.js';
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

        // --- Toggle Grid ---
        this.gridVisible = true;

        // --- Mission 19A : Persistence Layout N0 ---
        this.layout_store = {};
    }

    mount(parentSelector) {
        this.el = document.querySelector(parentSelector);
        if (!this.el) return;

        this.el.classList.add('canvas-container', 'svg-mode');

        this.el.innerHTML = `
            <svg id="stenciler-svg" width="100%" height="100%" viewBox="${this.viewBox.x} ${this.viewBox.y} ${this.viewBox.w} ${this.viewBox.h}" preserveAspectRatio="xMidYMid meet">
                <defs>
                    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                        <path d="M 20 0 L 0 0 0 20" fill="none" stroke="var(--border-subtle, #d5d4d0)" stroke-width="1"/>
                    </pattern>
                </defs>
                <rect id="svg-bg" width="100%" height="100%" fill="var(--bg-secondary, #f0efeb)" pointer-events="none"/>
                <rect id="svg-grid" width="100%" height="100%" fill="url(#grid)" pointer-events="none" class="grid-layer"/>
                <text id="svg-level-indicator" x="20" y="30" font-size="11" fill="var(--text-muted)" font-family="Geist, sans-serif" pointer-events="none"></text>
                <g id="svg-viewport"></g>
                <text id="svg-placeholder" x="500" y="400" text-anchor="middle" font-size="18" fill="var(--text-muted, #94a3b8)" font-family="Inter, sans-serif" pointer-events="none">
                    Déposez des Corps ici (Moteur SVG)
                </text>
            </svg>
            <div class="zoom-controls">
                <button id="btn-grid-toggle" title="Toggle Grid">⊞</button>
                <button id="btn-zoom-out">-</button>
                <span id="zoom-level">100%</span>
                <button id="btn-zoom-in">+</button>
                <button id="btn-zoom-reset">Reset</button>
                <button id="btn-export-svg" title="Export SVG">📥</button>
                <button id="btn-infer-llm" title="Re-inférer layout via LLM">✨</button>
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

        // --- Mission 19A : Load N0 Layout ---
        fetch('/api/layout')
            .then(res => res.json())
            .then(data => { this.layout_store = data; })
            .catch(e => console.warn('[19A] Layout load failed:', e));

        document.addEventListener('corps:open', async (e) => {
            const { corpsId } = e.detail;
            this.drillStack = [];
            await this._renderCorps(corpsId);
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

    async _renderCorps(corpsId) {
        if (!this.viewport) return;
        this.currentCorpsId = corpsId;
        this.viewport.innerHTML = '';
        const phaseData = this.genome?.n0_phases?.find(p => p.id === corpsId);
        if (!phaseData) return;

        const CORPS_COLORS = { n0_brainstorm: '#d4b2bc', n0_backend: '#a8c5fc', n0_frontend: '#a8dcc9', n0_deploy: '#edd0b0' };
        const accentColor = CORPS_COLORS[corpsId] || '#cbd5e1';

        let positions;
        try {
            const organs = phaseData.n1_sections.map(o => ({
                id: o.id,
                name: o.name || '',
                n2_count: (o.n2_features || []).length
            }));
            const res = await fetch('/api/infer_layout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ organs, mode: 'heuristic' })
            });
            const { result } = await res.json();
            positions = this._zoneTemplateToPositions(result, phaseData.n1_sections);
            // On s'assure que le viewBox suit le layout
            this.viewBox = { x: 0, y: 0, w: 1200, h: 900 };
            this.svg.setAttribute('viewBox', '0 0 1200 900');
        } catch (e) {
            console.warn('[16A] infer_layout fallback:', e);
            const layout = LayoutEngine.proposeLayout(phaseData);
            positions = layout.positions;
            this._applyLayout(layout);
        }

        phaseData.n1_sections.forEach((organe) => {
            let pos = positions.find(p => p.id === organe.id);
            // --- Surcharge Mission 19A : persistence du Layout N0 ---
            const saved = this.layout_store[organe.id];
            if (saved) {
                pos = { ...pos, ...saved };
            } else if (organe._layout) {
                // Fallback legacy (si le genome contient encore des positions)
                pos = { ...pos, ...organe._layout };
            }
            if (pos) this._renderNode(organe, pos, accentColor, 0);
        });

        this._updateIndicator(phaseData.name.toUpperCase());
        this._hidePlaceholder();
    }

    _zoneTemplateToPositions(result, sections) {
        const GAP = 8;

        // Grouper par zone
        const byZone = {};
        sections.forEach(s => {
            const zone = result[s.id]?.zone || 'main';
            (byZone[zone] = byZone[zone] || []).push({ s, inf: result[s.id] || {} });
        });

        // Hauteur adaptative d'un organe
        // Base généreuse : _buildComposition() est tall par nature (bottom-up SVG)
        const organH = (s, inf) => {
            if (inf.h === 'full') return 640;
            if (typeof inf.h === 'number' && inf.h > 0) return inf.h;
            return Math.max(160, 80 + (s.n2_features?.length || 0) * 40);
        };

        // Zones élastiques
        const hasLeft = !!(byZone.sidebar_left?.length);
        const hasRight = !!(byZone.sidebar_right?.length);
        const mainX = hasLeft ? 248 : 8;
        const mainW = 1200 - mainX - (hasRight ? 248 : 8);

        const positions = [];

        // --- HEADER (flex horizontal) ---
        (byZone.header || []).forEach((item, i, arr) => {
            const colW = Math.floor(1200 / arr.length);
            positions.push({ id: item.s.id, x: i * colW, y: 0, w: colW, h: 56, zone: 'header' });
        });

        // --- FOOTER (flex horizontal) ---
        (byZone.footer || []).forEach((item, i, arr) => {
            const colW = Math.floor(1200 / arr.length);
            positions.push({ id: item.s.id, x: i * colW, y: 840, w: colW, h: 48, zone: 'footer' });
        });

        // --- PREVIEW BAND (flex horizontal) ---
        (byZone.preview_band || []).forEach((item, i, arr) => {
            const colW = Math.floor(1200 / arr.length);
            positions.push({ id: item.s.id, x: i * colW, y: 720, w: colW, h: 120, zone: 'preview_band' });
        });

        // --- SIDEBAR LEFT (stack vertical) ---
        let sy = 56;
        (byZone.sidebar_left || []).forEach(item => {
            const h = organH(item.s, item.inf);
            positions.push({ id: item.s.id, x: 0, y: sy, w: 240, h, zone: 'sidebar_left' });
            sy += h + GAP;
        });

        // --- SIDEBAR RIGHT (stack vertical) ---
        sy = 56;
        (byZone.sidebar_right || []).forEach(item => {
            const h = organH(item.s, item.inf);
            positions.push({ id: item.s.id, x: 960, y: sy, w: 240, h, zone: 'sidebar_right' });
            sy += h + GAP;
        });

        // --- CANVAS (prend tout l'espace élastique) ---
        (byZone.canvas || []).forEach(item => {
            positions.push({ id: item.s.id, x: mainX, y: 56, w: mainW, h: 640, zone: 'canvas' });
        });

        // --- MAIN (stack vertical ou 2-col si > 3) ---
        const mainItems = [...(byZone.main || []), ...(byZone.unknown || [])];
        if (mainItems.length <= 3) {
            let my = 56;
            mainItems.forEach(item => {
                const h = organH(item.s, item.inf);
                const w = typeof item.inf.w === 'number' ? Math.min(item.inf.w, mainW) : mainW;
                positions.push({ id: item.s.id, x: mainX, y: my, w, h, zone: 'main' });
                my += h + 16;
            });
        } else {
            const colW = Math.floor(mainW / 2) - GAP;
            let col0y = 56, col1y = 56;
            mainItems.forEach((item, i) => {
                const col = i % 2;
                const h = organH(item.s, item.inf);
                const x = col === 0 ? mainX : mainX + colW + GAP * 2;
                const y = col === 0 ? col0y : col1y;
                positions.push({ id: item.s.id, x, y, w: colW, h, zone: 'main' });
                if (col === 0) col0y += h + 16;
                else col1y += h + 16;
            });
        }

        return positions;
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

                // Shift = homothétie (aspect ratio constant)
                if (e.shiftKey && this.resizeStart.ratio > 0) {
                    const ratio = this.resizeStart.ratio;
                    const isCorner = id.length === 2; // 'tl','tr','bl','br'
                    const isH = id === 'l' || id === 'r';
                    if (isCorner || isH) nh = nw / ratio;
                    else nw = nh * ratio;
                }

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
                    w: w, h: h,
                    ratio: h > 0 ? w / h : 1
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

            // --- Mission 19A : Sync layout.json pour N0 ---
            const currentLevel = this.drillStack.length; // 0 = Corps (Organes visible)
            if (currentLevel === 0) {
                this.layout_store[id] = { x, y, w, h };
                fetch('/api/layout', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ [id]: { x, y, w, h } })
                }).catch(e => console.error('[19A] POST layout failed:', e));
            }
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
                return;
            }

            const node = e.target.closest('.svg-node');
            if (node) {
                e.stopPropagation(); // BUG E: Stop propagation to prevent multiple triggers
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
                    // Mode Illustrateur : intercept le dblclick pour entrer dans le groupe
                    this.groupEditMode ? this._exitGroupEdit() : this._enterGroupEdit(node);
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
        prim.parentNode.appendChild(ov);

        // Poignées de redimensionnement uniquement sur les <rect> (14B-RESIZE)
        if (prim.tagName === 'rect') {
            this._setupPrimitiveResize(prim, ov);
        }

        // 14A : Notifier PrimitiveEditor
        document.dispatchEvent(new CustomEvent('primitive:selected', {
            detail: {
                el: prim,
                fill: prim.getAttribute('fill') || 'none',
                stroke: prim.getAttribute('stroke') || 'none',
                strokeWidth: parseFloat(prim.getAttribute('stroke-width') || 1.5),
                tag: prim.tagName
            }
        }));

        // 14A : Setup drag avec update de l'overlay s'il ne l'est pas déjà
        if (prim._dragHandlers) {
            // Remplacer l'ancien handler avec l'overlay (si on le voulait)
            // Mais pour l'instant, le drag setup dans _enterGroupEdit suffit
            // On évite le double appel qui causait les leaks (BUG 14A-FIX)
        }
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

        const onMouseMove = (e) => {
            if (!dragging) return;
            const currentMouse = this._getMousePos(e);
            const dx = currentMouse.x - startMouse.x;
            const dy = currentMouse.y - startMouse.y;

            setXY(startPos.x + dx, startPos.y + dy);

            // Mettre à jour l'overlay s'il existe
            if (overlay) {
                const bb = prim.getBBox();
                overlay.setAttribute('x', bb.x - 2);
                overlay.setAttribute('y', bb.y - 2);
                overlay.setAttribute('width', bb.width + 4);
                overlay.setAttribute('height', bb.height + 4);
            }
        };

        const onMouseUp = () => {
            dragging = false;
            window.removeEventListener('mousemove', onMouseMove);
            window.removeEventListener('mouseup', onMouseUp);
        };

        const onMouseDown = (e) => {
            dragging = true;
            startMouse = this._getMousePos(e);
            startPos = getXY();
            e.stopPropagation();

            // Attacher les events window uniquement pendant le drag
            window.addEventListener('mousemove', onMouseMove);
            window.addEventListener('mouseup', onMouseUp);
        };

        prim.addEventListener('mousedown', onMouseDown);

        // Stocker les références pour le nettoyage
        prim._dragHandlers = { down: onMouseDown, move: onMouseMove, up: onMouseUp };
    }

    _setupPrimitiveResize(prim, ov) {
        // Nettoyer les poignées précédentes
        prim.parentNode.querySelectorAll('.resize-handle').forEach(h => h.remove());

        const SVG_NS = 'http://www.w3.org/2000/svg';
        const HS = 6; // handle size

        const corners = [
            { id: 'tl', cursor: 'nw-resize' },
            { id: 'tr', cursor: 'ne-resize' },
            { id: 'br', cursor: 'se-resize' },
            { id: 'bl', cursor: 'sw-resize' },
        ];

        const updateHandlePositions = () => {
            const x = parseFloat(ov.getAttribute('x'));
            const y = parseFloat(ov.getAttribute('y'));
            const w = parseFloat(ov.getAttribute('width'));
            const h = parseFloat(ov.getAttribute('height'));
            const pts = { tl: [x, y], tr: [x + w, y], br: [x + w, y + h], bl: [x, y + h] };
            corners.forEach(({ id }) => {
                const hdl = prim.parentNode.querySelector(`.resize-handle[data-corner="${id}"]`);
                if (hdl) {
                    hdl.setAttribute('x', pts[id][0] - HS / 2);
                    hdl.setAttribute('y', pts[id][1] - HS / 2);
                }
            });
        };

        corners.forEach(({ id, cursor }) => {
            const hdl = document.createElementNS(SVG_NS, 'rect');
            hdl.setAttribute('width', HS);
            hdl.setAttribute('height', HS);
            hdl.setAttribute('fill', 'white');
            hdl.setAttribute('stroke', 'var(--accent-bleu)');
            hdl.setAttribute('stroke-width', '1.5');
            hdl.setAttribute('class', 'resize-handle');
            hdl.setAttribute('data-corner', id);
            hdl.setAttribute('pointer-events', 'all');
            hdl.style.cursor = cursor;

            let startMouse, startRect;

            hdl.addEventListener('mousedown', (e) => {
                e.stopPropagation();
                startMouse = this._getMousePos(e);
                const bbox = prim.getBBox();
                startRect = { x: bbox.x, y: bbox.y, w: bbox.width, h: bbox.height };
                console.log('📐 [14B-RESIZE] Start Resize:', startRect);

                const onMove = (ev) => {
                    const m = this._getMousePos(ev);
                    const dx = m.x - startMouse.x;
                    const dy = m.y - startMouse.y;
                    let { x, y, w, h } = startRect;

                    if (id === 'tl') { x += dx; y += dy; w -= dx; h -= dy; }
                    if (id === 'tr') { y += dy; w += dx; h -= dy; }
                    if (id === 'br') { w += dx; h += dy; }
                    if (id === 'bl') { x += dx; w -= dx; h += dy; }

                    w = Math.max(8, w);
                    h = Math.max(8, h);

                    prim.setAttribute('x', x);
                    prim.setAttribute('y', y);
                    prim.setAttribute('width', w);
                    prim.setAttribute('height', h);

                    // Mettre à jour l'overlay prim-sel
                    const bb = prim.getBBox();
                    ov.setAttribute('x', bb.x - 2);
                    ov.setAttribute('y', bb.y - 2);
                    ov.setAttribute('width', bb.width + 4);
                    ov.setAttribute('height', bb.height + 4);
                    updateHandlePositions();
                };

                const onUp = () => {
                    window.removeEventListener('mousemove', onMove);
                    window.removeEventListener('mouseup', onUp);
                };

                window.addEventListener('mousemove', onMove);
                window.addEventListener('mouseup', onUp);
            });

            prim.parentNode.appendChild(hdl);
        });

        updateHandlePositions();
    }

    async _exitGroupEdit() {
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
                // Nettoyage click
                if (prim._gc) {
                    prim.removeEventListener('click', prim._gc);
                    delete prim._gc;
                }

                // Nettoyage drag (BUG 14A-FIX)
                if (prim._dragHandlers) {
                    prim.removeEventListener('mousedown', prim._dragHandlers.down);
                    window.removeEventListener('mousemove', prim._dragHandlers.move);
                    window.removeEventListener('mouseup', prim._dragHandlers.up);
                    delete prim._dragHandlers;
                }

                prim.setAttribute('pointer-events', 'none');
                prim.style.cursor = '';
            });
        }

        // Supprimer la sélection
        node.querySelectorAll('.prim-sel').forEach(el => el.remove());
        node.querySelectorAll('.resize-handle').forEach(el => el.remove());

        // 14A : Fermer PrimitiveEditor
        document.dispatchEvent(new CustomEvent('primitive:deselected'));

        // Capture SVG modifié + dimensions → PrimOverlay (14B) + génome (14F-P4)
        const nodeId = node.dataset.id;
        if (nodeId && content) {
            const bb = content.getBBox();
            PrimOverlay.set(nodeId, content.innerHTML, bb.height, bb.width);
            console.log('💾 [PrimOverlay] Saved:', nodeId, PrimOverlay.get(nodeId));
            const genomeNode = this._findInGenome(nodeId);
            if (genomeNode) {
                genomeNode.svg_payload = content.innerHTML;
                genomeNode.svg_h = Math.round(bb.height) || 80;
            }
        }

        // Re-render N0 complet (cascade N3→N2→N1→N0 automatique via _buildComposition)
        const corpsId = this.currentCorpsId;
        if (corpsId) {
            this.drillStack = [];
            await this._renderCorps(corpsId);
        }

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

        // Toggle Grid
        this.el.querySelector('#btn-grid-toggle')?.addEventListener('click', () => {
            this.gridVisible = !this.gridVisible;
            const gridRect = this.svg.querySelector('#svg-grid');
            const btn = this.el.querySelector('#btn-grid-toggle');
            if (gridRect) {
                gridRect.style.display = this.gridVisible ? 'block' : 'none';
            }
            if (btn) {
                btn.style.opacity = this.gridVisible ? '1' : '0.4';
            }
        });

        // Handler LLM Layout (Mission 16A)
        this.el.querySelector('#btn-infer-llm')?.addEventListener('click', async () => {
            if (!this.currentCorpsId) return;
            const phaseData = this.genome?.n0_phases?.find(p => p.id === this.currentCorpsId);
            if (!phaseData) return;
            const organs = phaseData.n1_sections.map(o => ({
                id: o.id, name: o.name || '', n2_count: (o.n2_features || []).length
            }));

            // Show loading state
            const btn = this.el.querySelector('#btn-infer-llm');
            if (btn) btn.textContent = '⏳';

            try {
                const res = await fetch('/api/infer_layout', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        organs,
                        mode: 'llm',
                        model: 'gemini-3-flash-preview'
                    })
                });
                const { result, tier } = await res.json();
                console.log(`[16A] LLM layout tier: ${tier}`, result);

                this.viewport.innerHTML = '';
                const positions = this._zoneTemplateToPositions(result, phaseData.n1_sections);

                // update viewBox
                this.viewBox = { x: 0, y: 0, w: 1200, h: 900 };
                this.svg.setAttribute('viewBox', '0 0 1200 900');

                const CORPS_COLORS = { n0_brainstorm: '#d4b2bc', n0_backend: '#a8c5fc', n0_frontend: '#a8dcc9', n0_deploy: '#edd0b0' };
                const accentColor = CORPS_COLORS[this.currentCorpsId] || '#cbd5e1';

                phaseData.n1_sections.forEach((organe) => {
                    let pos = positions.find(p => p.id === organe.id);
                    if (organe._layout) pos = { ...pos, ...organe._layout };
                    if (pos) this._renderNode(organe, pos, accentColor, 0);
                });
            } catch (e) {
                console.error('[16A] LLM infer failed:', e);
            } finally {
                if (btn) btn.textContent = '✨';
            }
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
