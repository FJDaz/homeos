/**
 * Canvas.renderer.js
 * Moteur de rendu vectoriel pour le Stenciler.
 * Responsabilités : Construction des éléments SVG, injection des wireframes.
 */

import { G } from './GRID.js';
import { renderAtom } from './AtomRenderer.js';
import { PrimOverlay } from './PrimOverlay.js';
import { WireframeLibrary } from './WireframeLibrary.js';
import { resolveHint } from './SemanticMatcher.js';

console.log('📦 [Debug] WireframeLibrary imported:', !!WireframeLibrary);

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
        return resolveHint(data);
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
            // PrimOverlay : SVG modifié par l'utilisateur en Mode Illustrateur (14B)
            const cached = PrimOverlay.get(data.id);
            if (cached) return cached;

            // 14F-BUGS : Tenter WireframeLibrary avant renderAtom (Bottom-Up)
            const hint = this._matchHint(data);
            if (hint) {
                const wfResult = WireframeLibrary.getSVG(hint, color, availableWidth, 180, data.name);
                if (wfResult && wfResult.svg) {
                    return { svg: wfResult.svg, h: wfResult.h || 180, w: availableWidth };
                }
            }

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
        let maxPositionedY = 0;
        const CANVAS_REF_W = 1024; // Largeur de référence du canvas N2

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

            // Mémoire bottom-up : cellules (N2) uniquement — pas les atomes (N3).
            // Les coords N3 canvas ne sont pas compatibles avec les coords locales.
            const isAtomChild = child.id?.startsWith('comp_') || !!child.interaction_type;
            let tx = currentX;
            let ty = currentY;
            if (!isAtomChild && child._layout?.x !== undefined && child._layout?.y !== undefined) {
                tx = Math.round((child._layout.x / CANVAS_REF_W) * availableWidth);
                ty = child._layout.y;
                maxPositionedY = Math.max(maxPositionedY, ty + res.h);
            }

            childHTML += `<g class="composition-wrapper" transform="translate(${tx}, ${ty})">${res.svg}</g>`;

            // Avancement des curseurs Layout (auto-layout, toujours calculé pour totalH)
            if (layoutType === 'flex' || layoutType === 'grid') {
                currentX += childAvailWidth + gap;
                rowHeight = Math.max(rowHeight, res.h);
            } else {
                currentY += res.h + gap;
            }
        });

        // Calcul hauteur finale (max entre auto-stack et enfants positionnés librement)
        let totalH = currentY;
        if (layoutType === 'flex' || layoutType === 'grid') {
            totalH = currentY + rowHeight;
        } else if (currentY > 0) {
            totalH = currentY - gap; // Retrait du dernier gap en mode stack
        }

        totalH = Math.max(totalH, maxPositionedY);

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
        // Zéro padding — node-bg = dimensions exactes du contenu (CODE DIRECT FJD 2026-02-25)
        const compGroup = this._el('g', {
            class: 'wf-content bottom-up-composition',
            'pointer-events': 'none'
        });

        // Mission 17A — N0 Organic Wireframe Rendering
        if (level === 0) {
            const organHint = this._matchHint(data);
            if (organHint) {
                const wfSvg = WireframeLibrary.getSVG(organHint, color, pos.w, pos.h, data.name);
                if (wfSvg) {
                    compGroup.innerHTML = wfSvg;
                    g.append(compGroup);
                    return g;
                }
            }
        }

        const res = this._buildComposition(data, pos.w, color);

        // Shrink-wrap : W = availableWidth (preservé depuis _layout.w si défini)
        // H suit le contenu SAUF si l'utilisateur a défini une H explicite via _layout
        const userH = data._layout?.h;
        pos.h = userH || res.h;
        pos.w = res.w;
        rect.setAttribute('height', pos.h);
        rect.setAttribute('width', pos.w);

        compGroup.innerHTML = res.svg;
        g.append(compGroup);

        return g;
    },

    /**
     * Met à jour le contenu d'un nœud lors d'un redimensionnement.
     */
    updateNode(g, w, h) {
        const rect = g.querySelector('.node-bg');
        const wfContent = g.querySelector('.wf-content');

        if (rect) {
            rect.setAttribute('width', w);
            rect.setAttribute('height', h);
        }

        // --- Bottom-up : re-render content at new width, scale to new height ---
        if (wfContent) {
            const nodeData = this._findDataById(g.dataset.id);
            if (nodeData) {
                const res = this._buildComposition(nodeData, w, 'var(--accent-bleu)');
                wfContent.innerHTML = res.svg;
                if (res.h > 0 && h > 0 && Math.abs(h - res.h) > 1) {
                    wfContent.setAttribute('transform', `scale(1, ${h / res.h})`);
                } else {
                    wfContent.removeAttribute('transform');
                }
            }
        }
    }
};

export default Renderer;
