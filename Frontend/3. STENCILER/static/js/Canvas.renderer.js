/**
 * Canvas.renderer.js
 * Moteur de rendu vectoriel pour le Stenciler.
 * Responsabilités : Construction des éléments SVG, injection des wireframes.
 */

import { G } from './GRID.js';
import { renderAtom } from './AtomRenderer.js';

const Renderer = {
    /**
     * Recherche de données dans le génome global.
     */
    _findDataById(id) {
        const genome = window.stencilerApp?.genome;
        let found = null;
        const search = (list) => {
            if (found) return;
            for (const item of list) {
                if (item.id === id) { found = item; return; }
                if (item.n1_sections) search(item.n1_sections);
                if (item.n2_features) search(item.n2_features);
                if (item.n3_components) search(item.n3_components);
            }
        };
        search(genome?.n0_phases || []);
        return found;
    },

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
            if (keywords.some(k => searchPool.includes(k))) {
                // Fix Mission 10A-TER: "analyse" matche "editor" trop violemment pour les atomes
                if (hint === 'editor' && data.id.startsWith('comp_') && !searchPool.includes('code')) continue;
                return hint;
            }
        }
        return null;
    },

    /**
     * Crée un élément SVG avec namespace.
     */
    _el(tag, attrs = {}, text = '') {
        const el = document.createElementNS('http://www.w3.org/2000/svg', tag);
        Object.entries(attrs).forEach(([k, v]) => {
            // Sécurité Mission 9D : Évite les valeurs rx invalides (ex: "4 4 0 0")
            if (k === 'rx' && typeof v === 'string' && v.includes(' ')) {
                v = v.split(' ')[0];
            }
            el.setAttribute(k, v);
        });
        if (text) el.textContent = text;
        return el;
    },

    /**
     * Injecte les filtres et dégradés globaux (Premium).
     */
    _injectDefs(svg) {
        if (svg.querySelector('defs')) return;
        const defs = this._el('defs');

        // Filtre Ombre Portée (Premium)
        const filter = this._el('filter', { id: 'premium-shadow', x: '-20%', y: '-20%', width: '140%', height: '140%' });
        filter.append(this._el('feDropShadow', { dx: 0, dy: 3, stdDeviation: 4, 'flood-opacity': 0.15 }));

        // Filtre Ombre Portée (Subtle)
        const filterSubtle = this._el('filter', { id: 'subtle-shadow', x: '-20%', y: '-20%', width: '140%', height: '140%' });
        filterSubtle.append(this._el('feDropShadow', { dx: 0, dy: 1, stdDeviation: 2, 'flood-opacity': 0.05 }));

        // Dégradé Inset (Refleur)
        const grad = this._el('linearGradient', { id: 'premium-grad', x1: '0', y1: '0', x2: '0', y2: '1' });
        grad.append(this._el('stop', { offset: '0%', 'stop-color': 'white', 'stop-opacity': 0.1 }));
        grad.append(this._el('stop', { offset: '100%', 'stop-color': 'black', 'stop-opacity': 0.05 }));

        defs.append(filter, filterSubtle, grad);
        svg.prepend(defs);
    },

    _getSpacing(density) {
        if (density === 'compact') return { gap: G.GAP_S, pad: G.PAD_S };
        if (density === 'airy') return { gap: G.GAP * 1.5, pad: G.PAD_L };
        return { gap: G.GAP, pad: G.PAD };
    },

    _buildComposition(data, availableWidth, color) {
        // Est-ce un Atome (N3) ?
        if ((data.id && data.id.startsWith('comp_')) || data.interaction_type) {
            return renderAtom(data, availableWidth, color);
        }

        // Sinon c'est une Cellule (N2) ou Sous-groupe
        const { gap, pad } = this._getSpacing(data.density);
        const children = data.n2_features || data.n3_components || [];

        let childHTML = '';
        let layoutType = data.layout_type;
        if (!layoutType && data.layout_hint) {
            if (data.layout_hint.includes('row')) layoutType = 'flex';
            else if (data.layout_hint.includes('grid')) layoutType = 'grid';
        }
        layoutType = layoutType || 'stack';

        let currentY = 0;
        let currentX = 0;
        let rowHeight = 0;

        children.forEach((child) => {
            let childAvailWidth = availableWidth;
            let colsCount = 1;

            if (layoutType === 'grid') {
                colsCount = Math.min(children.length, 3); // Max 3 cols par défaut
                if (child.visual_hint === 'color-palette') colsCount = 4;
                childAvailWidth = G.cols(availableWidth, colsCount, gap);
            } else if (layoutType === 'flex') {
                colsCount = children.length;
                childAvailWidth = G.cols(availableWidth, colsCount, gap);
            }

            // --- Wrap Logic (Retour à la ligne) ---
            if ((layoutType === 'flex' || layoutType === 'grid') && (currentX + childAvailWidth > availableWidth + 1)) {
                currentX = 0;
                currentY += rowHeight + gap;
                rowHeight = 0;
            }

            // Génération de l'enfant N3
            const res = this._buildComposition(child, childAvailWidth, color);

            // Wrap dans un <g> positionné
            childHTML += `<g class="composition-wrapper" transform="translate(${currentX}, ${currentY})">${res.svg}</g>`;

            // Avancement des curseurs Layout
            if (layoutType === 'flex' || layoutType === 'grid') {
                currentX += childAvailWidth + gap;
                rowHeight = Math.max(rowHeight, res.h);
            } else {
                currentY += res.h + gap;
            }
        });

        // Calcul hauteur finale
        let totalH = currentY;
        if (layoutType === 'flex' || layoutType === 'grid') {
            totalH = currentY + rowHeight;
        } else if (currentY > 0) {
            totalH = currentY - gap; // Retrait du dernier gap en mode stack
        }

        const svgStr = `<g data-id="${data.id}" class="cell-group">${childHTML}</g>`;
        return { svg: svgStr, h: totalH, w: availableWidth };
    },

    /**
     * Rendu d'un nœud (Corps, Organe ou Cellule) au niveau Canvas.
     */
    renderNode(data, pos, color, level = 0) {
        const isCell = level === 1;
        const isAtom = level === 2;

        const g = this._el('g', {
            class: `svg-node ${isAtom ? 'atom-node' : (isCell ? 'cell-node' : 'corps-node')}`,
            transform: `translate(${pos.x}, ${pos.y})`,
            'data-id': data.id
        });

        // Background (Carte englobante de l'Organe/Cellule sur le canvas)
        const style = data._style || {};
        const rect = this._el('rect', {
            width: pos.w, height: pos.h, rx: 8,
            fill: 'transparent', // Arrêt de mort officiel des boîtes (Alpha 0)
            stroke: 'transparent',
            'stroke-width': 1,
            class: 'interactive-node node-bg'
        });
        rect.style.cssText = ''; // Plus de drop-shadow pour fusionner avec le fond de la page

        const svgElement = document.querySelector('.stenciler-canvas');
        if (svgElement) this._injectDefs(svgElement);

        // Suppression explicite de la barre de couleur verticale demandée par l'utilisateur
        // (stripe retirée)

        // Suppression explicite du title statique (node-label) demandée par l'utilisateur

        g.append(rect);

        // --- PIVOT BOTTOM-UP : Composition dynamique ---
        // Padding réduit à 8px selon demande, sauf PAD_TOP pour le petit titre
        const PAD_LEFT = 8, PAD_TOP = 20, PAD_RIGHT = 8, PAD_BOTTOM = 8;
        const innerW = pos.w - PAD_LEFT - PAD_RIGHT;

        const compGroup = this._el('g', {
            class: 'wf-content bottom-up-composition',
            'pointer-events': 'none',
            transform: `translate(${PAD_LEFT}, ${PAD_TOP})`
        });

        const res = this._buildComposition(data, innerW, color);

        // --- Redimensionnement dynamique ---
        const expectedH = res.h + PAD_TOP + PAD_BOTTOM;
        if (expectedH > pos.h) {
            pos.h = expectedH;
            rect.setAttribute('height', pos.h);
        }

        const innerH = pos.h - PAD_TOP - PAD_BOTTOM;
        const offsetY = Math.max(0, (innerH - res.h) / 2);

        compGroup.setAttribute('transform', `translate(${PAD_LEFT}, ${PAD_TOP + offsetY})`);
        compGroup.innerHTML = res.svg;
        g.append(compGroup);

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
            // Refresh text content if it changed in genome
            const dataId = g.dataset.id;
            const nodeData = this._findDataById(dataId);
            if (nodeData) label.textContent = nodeData.name.toUpperCase();
        }

        // --- Mission 9D & 10A-BIS : Refresh Atom labels ---
        // On ne refresh plus la méthode/endpoint (retirés du rendu)

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
                const newSVG = WireframeLibrary.getSVG(hint, color, w - (pad * 2), h - (pad * 2), nodeData.name);
                if (newSVG) {
                    wfContent.innerHTML = newSVG;
                }
            }
        }
    }
};

export default Renderer;
