/**
 * PrimitiveEditor.feature.js
 * Panel flottant pour l'édition de primitives SVG en Mode Illustrateur (14A).
 * Monté sur body. Écoute primitive:selected / primitive:deselected.
 * CODE DIRECT — FJD 2026-02-23
 */

import StencilerFeature from './base.feature.js';

class PrimitiveEditorFeature extends StencilerFeature {
    constructor(id = 'primitive-editor') {
        super(id);
        this.panel = null;
        this.currentPrim = null;
    }

    mount() {
        // Panel flottant attaché à body (pas de slot HTML)
        this.panel = document.createElement('div');
        this.panel.id = 'primitive-editor-panel';
        this.panel.className = 'prim-editor-panel hidden';
        this.panel.innerHTML = `
            <div class="prim-editor-header">
                <span class="prim-editor-tag" id="prim-tag">RECT</span>
                <span class="prim-editor-title">PRIMITIVE</span>
                <button class="prim-editor-close" id="prim-close">✕</button>
            </div>
            <div class="prim-editor-body">
                <div class="prim-row">
                    <label>FOND</label>
                    <input type="color" id="prim-fill" value="#e8e7e3">
                    <button class="prim-none-btn" data-prop="fill">none</button>
                </div>
                <div class="prim-row">
                    <label>CONTOUR</label>
                    <input type="color" id="prim-stroke" value="#3d3d3c">
                    <button class="prim-none-btn" data-prop="stroke">none</button>
                </div>
                <div class="prim-row">
                    <label>ÉPAIS.</label>
                    <input type="range" id="prim-sw" min="0" max="8" step="0.5" value="1.5">
                    <span id="prim-sw-val">1.5</span>
                </div>
                <div class="prim-row prim-opacity-row">
                    <label>OPAC.</label>
                    <input type="range" id="prim-opacity" min="0" max="1" step="0.05" value="1">
                    <span id="prim-opacity-val">1</span>
                </div>
            </div>
        `;
        document.body.appendChild(this.panel);
        this._injectStyles();
    }

    init() {
        document.addEventListener('primitive:selected', (e) => {
            this.currentPrim = e.detail.el;
            this._syncFromPrim(e.detail);
            this.panel.classList.remove('hidden');
        });

        document.addEventListener('primitive:deselected', () => {
            this.panel.classList.add('hidden');
            this.currentPrim = null;
        });

        this.panel.querySelector('#prim-close').addEventListener('click', () => {
            this.panel.classList.add('hidden');
            this.currentPrim = null;
            document.dispatchEvent(new CustomEvent('primitive:deselected'));
        });

        // Fill
        this.panel.querySelector('#prim-fill').addEventListener('input', (e) => {
            if (!this.currentPrim) return;
            this.currentPrim.setAttribute('fill', e.target.value);
        });

        // Stroke color
        this.panel.querySelector('#prim-stroke').addEventListener('input', (e) => {
            if (!this.currentPrim) return;
            this.currentPrim.setAttribute('stroke', e.target.value);
        });

        // Stroke width
        const swInput = this.panel.querySelector('#prim-sw');
        const swVal = this.panel.querySelector('#prim-sw-val');
        swInput.addEventListener('input', (e) => {
            if (!this.currentPrim) return;
            this.currentPrim.setAttribute('stroke-width', e.target.value);
            swVal.textContent = e.target.value;
        });

        // Opacity
        const opInput = this.panel.querySelector('#prim-opacity');
        const opVal = this.panel.querySelector('#prim-opacity-val');
        opInput.addEventListener('input', (e) => {
            if (!this.currentPrim) return;
            this.currentPrim.setAttribute('opacity', e.target.value);
            opVal.textContent = parseFloat(e.target.value).toFixed(2);
        });

        // "none" buttons
        this.panel.querySelectorAll('.prim-none-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                if (!this.currentPrim) return;
                this.currentPrim.setAttribute(btn.dataset.prop, 'none');
            });
        });
    }

    _syncFromPrim(detail) {
        const fillInput = this.panel.querySelector('#prim-fill');
        const strokeInput = this.panel.querySelector('#prim-stroke');
        const swInput = this.panel.querySelector('#prim-sw');
        const swVal = this.panel.querySelector('#prim-sw-val');
        const opInput = this.panel.querySelector('#prim-opacity');
        const opVal = this.panel.querySelector('#prim-opacity-val');
        const tagEl = this.panel.querySelector('#prim-tag');

        if (tagEl) tagEl.textContent = (detail.tag || 'EL').toUpperCase();

        // Color picker uniquement pour les couleurs hex valides
        if (detail.fill && detail.fill !== 'none' && /^#[0-9a-f]{3,6}$/i.test(detail.fill)) {
            fillInput.value = detail.fill;
        }
        if (detail.stroke && detail.stroke !== 'none' && /^#[0-9a-f]{3,6}$/i.test(detail.stroke)) {
            strokeInput.value = detail.stroke;
        }

        const sw = parseFloat(detail.strokeWidth) || 1.5;
        swInput.value = sw;
        swVal.textContent = sw;

        const op = parseFloat(detail.el?.getAttribute('opacity') ?? 1);
        opInput.value = op;
        opVal.textContent = op.toFixed(2);
    }

    _injectStyles() {
        const style = document.createElement('style');
        style.id = 'prim-editor-styles';
        style.textContent = `
            .prim-editor-panel {
                position: fixed;
                bottom: 60px;
                left: 216px;
                z-index: 1000;
                background: var(--bg-primary, #f7f6f2);
                border: 1px solid var(--border-subtle, #d5d4d0);
                border-radius: 8px;
                min-width: 210px;
                box-shadow: 0 4px 16px rgba(0,0,0,0.12);
                font-family: Geist, sans-serif;
                font-size: 11px;
            }
            .prim-editor-panel.hidden { display: none; }
            .prim-editor-header {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 7px 10px 6px;
                border-bottom: 1px solid var(--border-subtle, #d5d4d0);
            }
            .prim-editor-tag {
                font-size: 9px;
                font-weight: 700;
                letter-spacing: 0.06em;
                color: white;
                background: var(--accent-ardoise, #5A6B7C);
                padding: 1px 5px;
                border-radius: 3px;
            }
            .prim-editor-title {
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 0.08em;
                color: var(--text-secondary, #6a6a69);
                flex: 1;
            }
            .prim-editor-close {
                background: none;
                border: none;
                cursor: pointer;
                font-size: 11px;
                color: var(--text-muted, #999);
                padding: 2px 4px;
                border-radius: 3px;
                line-height: 1;
            }
            .prim-editor-close:hover { background: var(--bg-tertiary, #e8e7e3); }
            .prim-editor-body {
                padding: 10px 12px;
                display: flex;
                flex-direction: column;
                gap: 8px;
            }
            .prim-row {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .prim-row label {
                font-size: 9px;
                font-weight: 700;
                letter-spacing: 0.06em;
                color: var(--text-muted, #999);
                width: 46px;
                flex-shrink: 0;
            }
            .prim-row input[type="color"] {
                width: 28px;
                height: 20px;
                border: 1px solid var(--border-subtle, #d5d4d0);
                border-radius: 4px;
                cursor: pointer;
                padding: 1px;
                background: none;
            }
            .prim-row input[type="range"] {
                flex: 1;
                height: 3px;
                accent-color: var(--accent-ardoise, #5A6B7C);
            }
            .prim-none-btn {
                font-size: 9px;
                color: var(--text-muted, #999);
                background: none;
                border: 1px solid var(--border-subtle, #d5d4d0);
                border-radius: 4px;
                padding: 2px 6px;
                cursor: pointer;
                white-space: nowrap;
            }
            .prim-none-btn:hover { border-color: var(--text-secondary, #6a6a69); }
            #prim-sw-val, #prim-opacity-val {
                font-size: 10px;
                color: var(--text-secondary, #6a6a69);
                width: 28px;
                text-align: right;
                font-family: monospace;
            }
        `;
        document.head.appendChild(style);
    }

    render() { return ''; }
}

export default PrimitiveEditorFeature;
