/**
 * Canvas.renderer.js
 * Moteur de rendu vectoriel pour le Stenciler.
 * Responsabilités : Construction des éléments SVG, injection des wireframes.
 */

import { WireframeLibrary } from './WireframeLibrary.js';

const Renderer = {
    /**
     * Tente de trouver un wireframe correspondant aux données du nœud.
     */
    _matchHint(data) {
        let hint = data.visual_hint;

        // --- Bug n°1 : Aliases pour visual_hint courts ---
        const HINT_ALIASES = {
            'nav': 'breadcrumb',
            'layout': 'grid',
            'search': 'brainstorm',
            'navigation': 'breadcrumb',
            'selection': 'selection' // Fix Bug n°3 : Priorité au wireframe selection
        };

        if (hint) return HINT_ALIASES[hint] || hint;

        const searchPool = `${data.id} ${data.name || ''}`.toLowerCase();
        const mapping = {
            'table': ['table', 'ir', 'listing'],
            'stepper': ['stepper', 'sequence', 'workflow'],
            'chat/bubble': ['chat', 'dialogue', 'bubble', 'user'],
            'editor': ['editor', 'code', 'analyse', 'adaptation', 'json'],
            'breadcrumb': ['breadcrumb', 'navigation', 'nav'],
            'dashboard': ['dashboard', 'session', 'status', 'summary'],
            'accordion': ['accordion', 'validation', 'list'],
            'color-palette': ['palette', 'theme', 'color', 'style'],
            'upload': ['upload', 'import', 'deposit'],
            'action-button': ['deploy', 'export', 'download', 'launch', 'button'],
            'stencil-card': ['card', 'arbitrage'], // Retrait de 'selection' ici
            'selection': ['selection', 'choice', 'picker'],
            'zoom-controls': ['zoom', 'ctrl'],
            'modal': ['modal', 'confirm', 'popup'],
            'grid': ['layout', 'grid', 'view', 'gallery'],
            'brainstorm': ['brainstorm', 'search', 'idea']
        };

        for (const [hint, keywords] of Object.entries(mapping)) {
            if (keywords.some(k => searchPool.includes(k))) return hint;
        }
        return null;
    },

    /**
     * Crée un élément SVG avec namespace.
     */
    _el(tag, attrs = {}, text = '') {
        const el = document.createElementNS('http://www.w3.org/2000/svg', tag);
        Object.entries(attrs).forEach(([k, v]) => el.setAttribute(k, v));
        if (text) el.textContent = text;
        return el;
    },

    /**
     * Rendu d'un nœud (Corps, Organe ou Cellule)
     */
    renderNode(data, pos, color, level = 0) {
        const isCell = level === 1;
        const isAtom = level === 2;

        const g = this._el('g', {
            class: `svg-node ${isAtom ? 'atom-node' : (isCell ? 'cell-node' : 'corps-node')}`,
            transform: `translate(${pos.x}, ${pos.y})`,
            'data-id': data.id
        });

        // Background
        const style = data._style || {};
        const rect = this._el('rect', {
            width: pos.w, height: pos.h, rx: 6,
            fill: style.fill || 'var(--bg-tertiary)',
            stroke: style.stroke || 'var(--border-subtle)',
            'stroke-width': style.strokeWidth || 1.5,
            class: 'interactive-node node-bg'
        });
        rect.style.cssText = 'filter:drop-shadow(0 2px 4px rgba(0,0,0,0.05))';

        // Stripe colorée
        const stripe = this._el('rect', { width: 6, height: pos.h - 16, x: 0, y: 8, fill: color, rx: 2 });

        // Titre - Mission 8D Refinement : Centrage absolu
        const title = this._el('text', {
            x: pos.w / 2, y: pos.h / 2,
            'font-size': isAtom ? 14 : 16, // Légèrement plus grand pour la lisibilité
            fill: 'var(--text-primary)',
            'font-family': style.font || 'Geist, sans-serif',
            'font-weight': '800',
            'pointer-events': 'none',
            'text-anchor': 'middle',
            'dominant-baseline': 'middle',
            class: 'node-label'
        }, data.name.toUpperCase());
        title.style.opacity = '0'; // Masqué par défaut (Mission 8D)
        title.style.transition = 'opacity 0.2s ease';

        g.append(rect, stripe, title);

        // --- SECTION MISSION 8A : Injection Wireframe Library ---
        const hint = this._matchHint(data);
        const pad = style.padding || 0;

        if (hint) {
            const wfSVG = WireframeLibrary.getSVG(hint, color, pos.w - (pad * 2), pos.h - (pad * 2));
            if (wfSVG) {
                const wfGroup = this._el('g', {
                    class: 'wf-content',
                    'pointer-events': 'none',
                    transform: `translate(${pad}, ${pad})`
                });
                wfGroup.innerHTML = wfSVG;
                g.append(wfGroup);

                // --- MISSION 8B-BIS : Déconfinement ---
                // Si wireframe réussi, on masque VISUELLEMENT le fond gris et la stripe, mais on garde le rect pour le hit-test (D&D)
                rect.style.opacity = '0';
                stripe.style.opacity = '0';
                title.style.opacity = '0.35';
                title.setAttribute('font-size', '10');
            }
        } else if (level === 0) {
            // Fallback icônes si pas de wireframe (Précédent Mission 6D)
            const ID_ICONS = {
                'backend': '⚡', 'frontend': '◈', 'brainstorm': '◆', 'deploy': '↗'
            };
            const idKey = data.id.replace(/^n\d+_/, '').toLowerCase();
            const icon = ID_ICONS[idKey] || '◆';
            const iconEl = this._el('text', {
                x: pos.w - 18, y: 20, 'font-size': 18, fill: color,
                'font-family': 'serif', 'text-anchor': 'middle', 'pointer-events': 'none',
                'dominant-baseline': 'middle'
            }, icon);
            g.append(iconEl);
        }

        // Description (si pas de wireframe ou en complément)
        if (!hint && data.description && level < 2) {
            const desc = this._el('text', {
                x: 15, y: 40, 'font-size': 10, fill: 'var(--text-muted)',
                'font-family': 'Inter, sans-serif', 'pointer-events': 'none'
            }, data.description);
            g.append(desc);
        }

        // --- SPECIFIQUE N3 (Atomes) ---
        if (isAtom && data.method) {
            // Fond adaptatif pour l'atome
            const methodLabel = this._el('rect', { x: 15, y: pos.h - 32, width: 35, height: 12, rx: 2, fill: 'var(--bg-hover)', opacity: 0.8 });
            const methodText = this._el('text', { x: 32.5, y: pos.h - 23, 'font-size': 8, 'text-anchor': 'middle', fill: 'var(--text-secondary)', 'font-weight': 'bold' }, data.method);
            const endpoint = this._el('text', { x: 55, y: pos.h - 23, 'font-size': 8, fill: 'var(--text-muted)', 'font-family': 'monospace' }, data.endpoint || '');
            g.append(methodLabel, methodText, endpoint);

            // Si pas de wireframe, ajoutons une micro-icône au centre pour l'atome (N3)
            if (!hint) {
                const atomIcon = this._el('text', {
                    x: pos.w / 2, y: pos.h / 2, 'font-size': 24, fill: color,
                    'text-anchor': 'middle', 'dominant-baseline': 'middle', opacity: 0.2
                }, data.method === 'GET' ? '🔍' : '⚡');
                g.append(atomIcon);
            }
        }

        // Micro-cells preview (N1 -> N2)
        if (level === 0 && !hint) {
            const cells = data.n2_features || [];
            cells.slice(0, 3).forEach((c, i) => {
                const cellY = 55 + (i * 14);
                if (cellY + 12 > pos.h) return;
                const cellText = this._el('text', { x: 15, y: cellY, 'font-size': 9, fill: 'var(--text-secondary)', opacity: 0.8 }, `• ${c.name}`);
                g.append(cellText);
            });
        }

        return g;
    },

    /**
     * Met à jour le contenu d'un nœud lors d'un redimensionnement.
     */
    updateNode(g, w, h) {
        const rect = g.querySelector('.node-bg');
        const stripe = g.querySelector('rect[rx="2"]'); // Stripe colorée
        const label = g.querySelector('.node-label');
        const wfContent = g.querySelector('.wf-content');

        if (rect) {
            rect.setAttribute('width', w);
            rect.setAttribute('height', h);
        }

        if (stripe) {
            stripe.setAttribute('height', Math.max(0, h - 16));
        }

        if (label) {
            label.setAttribute('x', w / 2);
            label.setAttribute('y', h / 2);
        }

        // --- Mise à jour du wireframe ---
        if (wfContent) {
            const dataId = g.dataset.id;
            const genome = window.stencilerApp?.genome;
            let nodeData = null;
            const findNode = (list) => {
                for (const item of list) {
                    if (item.id === dataId) { nodeData = item; return true; }
                    if (item.n1_sections && findNode(item.n1_sections)) return true;
                    if (item.n2_features && findNode(item.n2_features)) return true;
                    if (item.n3_components && findNode(item.n3_components)) return true;
                }
                return false;
            };
            findNode(genome?.n0_phases || []);

            if (nodeData) {
                const hint = this._matchHint(nodeData);
                const color = stripe ? stripe.getAttribute('fill') : 'var(--accent-bleu)';
                const pad = nodeData._style?.padding || 0;

                wfContent.setAttribute('transform', `translate(${pad}, ${pad})`);
                const newSVG = WireframeLibrary.getSVG(hint, color, w - (pad * 2), h - (pad * 2));
                if (newSVG) {
                    wfContent.innerHTML = newSVG;
                }
            }
        }
    }
};

export default Renderer;
