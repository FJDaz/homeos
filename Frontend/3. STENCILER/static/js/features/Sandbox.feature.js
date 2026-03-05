import CanvasFeature from './Canvas.feature.js';

/**
 * 🧪 SandboxFeature - Pure Frontend Layout Experiments
 * 
 * Usage: Activer via console: window.enableSandbox()
 *        Désactiver: window.disableSandbox()
 * 
 * Ce module permet de tester des layouts expérimentaux sans:
 * - Modifier le serveur (Constitution V3.1)
 * - Modifier le genome (Pristine Mode)
 * - Casser la production
 */

class SandboxFeature extends CanvasFeature {
    constructor(id, options) {
        super(id, options);
        this.sandboxMode = false;
        this.experimentalLayouts = new Map();
        console.log('🧪 SandboxFeature loaded - type window.enableSandbox() to activate');
    }

    init(genome) {
        super.init(genome);
        
        // Expose globalement pour activation manuelle
        window.enableSandbox = () => this.enable();
        window.disableSandbox = () => this.disable();
        window.sandboxInject = (svg) => this.injectSVG(svg);
        
        // Auto-enable si ?sandbox=true dans l'URL
        if (location.search.includes('sandbox=true')) {
            this.enable();
        }
    }

    enable() {
        this.sandboxMode = true;
        document.body.classList.add('sandbox-active');
        console.log('🧪 SANDBOX MODE ENABLED');
        console.log('  - window.sandboxInject(svgString) : injecte un SVG');
        console.log('  - window.disableSandbox() : désactive le mode');
        
        // Ajouter le CSS sandbox dynamiquement
        this._injectSandboxStyles();
        
        // Redessiner avec layout sandbox
        if (this.currentCorpsId) {
            this._renderCorps(this.currentCorpsId);
        }
    }

    disable() {
        this.sandboxMode = false;
        document.body.classList.remove('sandbox-active');
        console.log('🧪 Sandbox mode disabled');
        
        // Restaurer le rendu normal
        if (this.currentCorpsId) {
            super._renderCorps(this.currentCorpsId);
        }
    }

    _injectSandboxStyles() {
        if (document.getElementById('sandbox-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'sandbox-styles';
        style.textContent = `
            body.sandbox-active::before {
                content: "🧪 SANDBOX MODE";
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                height: 24px;
                background: linear-gradient(90deg, #a8dcc9, #5A6B7C);
                color: white;
                font: 700 10px/24px 'Geist', sans-serif;
                text-align: center;
                letter-spacing: 1px;
                z-index: 99999;
            }
            body.sandbox-active {
                padding-top: 24px;
            }
            .sandbox-injection {
                animation: sandbox-pulse 2s ease-in-out infinite;
            }
            @keyframes sandbox-pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.8; }
            }
        `;
        document.head.appendChild(style);
    }

    _renderCorps(corpsId) {
        if (!this.sandboxMode || !corpsId?.includes('frontend')) {
            return super._renderCorps(corpsId);
        }
        
        // Rendu sandbox pour Frontend
        this._renderFrontendSandbox(corpsId);
    }

    _renderFrontendSandbox(corpsId) {
        if (!this.viewport) return;
        this.currentCorpsId = corpsId;
        this.viewport.innerHTML = '';
        
        const phaseData = this.genome?.n0_phases?.find(p => p.id === corpsId);
        if (!phaseData) return;

        const CORPS_COLORS = { 
            n0_brainstorm: '#d4b2bc', 
            n0_backend: '#a8c5fc', 
            n0_frontend: '#a8dcc9', 
            n0_deploy: '#edd0b0' 
        };
        const accentColor = CORPS_COLORS[corpsId] || '#cbd5e1';

        // Rail timeline
        this._drawTimelineRail(phaseData.n1_sections, accentColor);
        
        // Cards en vague
        phaseData.n1_sections.forEach((organe, index) => {
            const pos = this._getWavePosition(index, phaseData.n1_sections.length);
            const node = this._renderNode(organe, pos, accentColor, 0);
            node.classList.add('sandbox-injection');
        });

        this._updateIndicator(phaseData.name.toLowerCase() + ' 🧪');
        this._hidePlaceholder();
    }

    _drawTimelineRail(sections, color) {
        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        const width = 1000, startX = 100, endX = 900, y = 50;
        
        // Ligne
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', startX);
        line.setAttribute('y1', y);
        line.setAttribute('x2', endX);
        line.setAttribute('y2', y);
        line.setAttribute('stroke', color);
        line.setAttribute('stroke-width', '2');
        line.setAttribute('opacity', '0.4');
        g.appendChild(line);
        
        // Points
        const step = (endX - startX) / (sections.length - 1 || 1);
        sections.forEach((s, i) => {
            const cx = startX + (i * step);
            const active = i === 0;
            
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('cx', cx);
            circle.setAttribute('cy', y);
            circle.setAttribute('r', active ? '10' : '6');
            circle.setAttribute('fill', active ? color : 'var(--bg-primary)');
            circle.setAttribute('stroke', color);
            circle.setAttribute('stroke-width', '2');
            g.appendChild(circle);
            
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', cx);
            text.setAttribute('y', y + 4);
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('font-size', '10');
            text.setAttribute('font-weight', '700');
            text.setAttribute('fill', active ? '#fff' : color);
            text.textContent = (i + 1).toString();
            g.appendChild(text);
            
            const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            label.setAttribute('x', cx);
            label.setAttribute('y', y + 24);
            label.setAttribute('text-anchor', 'middle');
            label.setAttribute('font-size', '8');
            label.setAttribute('fill', 'var(--text-secondary)');
            label.textContent = (s.name || '').toLowerCase().substring(0, 10);
            g.appendChild(label);
        });
        
        this.viewport.appendChild(g);
    }

    _getWavePosition(index, total) {
        const cardW = 240, cardH = 80, gap = 20;
        const totalW = (total * cardW) + ((total - 1) * gap);
        const startX = (1000 - totalW) / 2;
        const wave = Math.sin(index * 0.6) * 15;
        
        return {
            x: startX + (index * (cardW + gap)),
            y: 100 + wave,
            w: cardW,
            h: cardH
        };
    }

    /**
     * Injection directe d'un SVG pour test
     */
    injectSVG(svgString) {
        if (!this.viewport) {
            console.error('Viewport not ready');
            return;
        }
        
        // Parser le SVG
        const parser = new DOMParser();
        const doc = parser.parseFromString(svgString, 'image/svg+xml');
        const svg = doc.querySelector('svg');
        
        if (svg) {
            // Ajouter au viewport
            const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            g.classList.add('sandbox-injection');
            g.innerHTML = svg.innerHTML;
            this.viewport.appendChild(g);
            console.log('🧪 SVG injected');
        }
    }
}

export default SandboxFeature;
