/**
 * Canvas.renderer.js
 * Moteur de rendu vectoriel pour le Stenciler.
 * Responsabilités : Construction des éléments SVG, injection des wireframes.
 */

import { WireframeLibrary } from './WireframeLibrary.js';
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

        // Dégradé Inset (Refleur)
        const grad = this._el('linearGradient', { id: 'premium-grad', x1: '0', y1: '0', x2: '0', y2: '1' });
        grad.append(this._el('stop', { offset: '0%', 'stop-color': 'white', 'stop-opacity': 0.1 }));
        grad.append(this._el('stop', { offset: '100%', 'stop-color': 'black', 'stop-opacity': 0.05 }));

        defs.append(filter, grad);
        svg.prepend(defs);
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

        // --- Mission 10A-TER : Injection des filtres Premium ---
        const svgElement = document.querySelector('.stenciler-canvas');
        if (svgElement) this._injectDefs(svgElement);

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

        // --- MISSION 10A-FRAME : Restauration Cartouche Atome ---
        // On ne passe plus par _matchHint pour les atomes (keyword matching trop fragile)
        if (isAtom) {
            const PAD_LEFT = 14, PAD_TOP = 24, PAD_RIGHT = 8, PAD_BOTTOM = 8;
            const innerW = pos.w - PAD_LEFT - PAD_RIGHT;
            const innerH = pos.h - PAD_TOP - PAD_BOTTOM;

            if (data.visual_hint) {
                // Priorité au wireframe explicite du génome (ex: 'editor', 'chat')
                const wfSVG = WireframeLibrary.getSVG(data.visual_hint, color, innerW, innerH, data.name);
                if (wfSVG) {
                    const wfGroup = this._el('g', {
                        class: 'wf-content', 'pointer-events': 'none',
                        transform: `translate(${PAD_LEFT}, ${PAD_TOP})`
                    });
                    wfGroup.innerHTML = wfSVG;
                    g.append(wfGroup);
                    // rect et stripe RESTENT VISIBLES
                    title.style.opacity = '0.7';
                    title.setAttribute('y', '16');
                    title.setAttribute('font-size', '9');
                    return g;
                }
            }

            // Fallback ou rendu générique via interaction_type
            const svgStr = renderAtom(data.interaction_type, data.name, { w: innerW, h: innerH }, color);
            if (svgStr) {
                const atomGroup = this._el('g', {
                    class: 'atom-wf-content', 'pointer-events': 'none',
                    transform: `translate(${PAD_LEFT}, ${PAD_TOP})`
                });
                atomGroup.innerHTML = svgStr;
                g.append(atomGroup);
                // rect et stripe RESTENT VISIBLES
                title.style.opacity = '0.7';
                title.setAttribute('y', '16');
                title.setAttribute('font-size', '9');
            }
            return g; // Fin du rendu pour l'Atome
        }

        // --- SECTION MISSION 8A : Injection Wireframe Library (Organes & Cellules) ---
        const hint = this._matchHint(data);
        const pad = style.padding || 0;

        if (hint) {
            const wfSVG = WireframeLibrary.getSVG(hint, color, pos.w - (pad * 2), pos.h - (pad * 2), data.name);
            if (wfSVG) {
                const wfGroup = this._el('g', {
                    class: 'wf-content',
                    'pointer-events': 'none',
                    transform: `translate(${pad}, ${pad})`
                });
                wfGroup.innerHTML = wfSVG;
                g.append(wfGroup);

                // --- MISSION 10A-FRAME : Unification Card-First ---
                // Le wireframe s'insère DANS la carte, il ne la remplace plus.
                // rect.style.opacity = '1'; // Règle par défaut
                // stripe.style.opacity = '1';
                title.style.opacity = '0.7';
                title.setAttribute('y', '16');
                title.setAttribute('font-size', '9');
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
        // Mission 10A-BIS : Retrait des mentions techniques (method/endpoint) demandées par FJD
        // On ne garde que l'id dans le dataset et le comportement interactif

        // Les atomes ne passent plus par ici (forkés en tête de fonction)

        // Micro-previews (Mission 10A : Cascade de détail)
        if (!hint) {
            // N1 -> N2 preview (Organe affiche ses Cellules)
            if (level === 0 && data.n2_features) {
                data.n2_features.slice(0, 3).forEach((c, i) => {
                    const y = 55 + (i * 14);
                    if (y + 12 > pos.h) return;
                    const text = this._el('text', { x: 15, y: y, 'font-size': 9, fill: 'var(--text-secondary)', opacity: 0.8 }, `• ${c.name.substring(0, 24)}`);
                    g.append(text);
                });
            }
            // N2 -> N3 preview (Cellule affiche ses Atomes) - Tâche 2
            if (level === 1 && data.n3_components) {
                data.n3_components.slice(0, 4).forEach((a, i) => {
                    const y = 40 + (i * 12);
                    if (y + 10 > pos.h) return;
                    const label = `${a.interaction_type || 'atome'} : ${a.name}`;
                    const text = this._el('text', { x: 15, y: y, 'font-size': 8, fill: 'var(--text-muted)', opacity: 0.7 }, `› ${label.substring(0, 28)}`);
                    g.append(text);
                });
            }
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
