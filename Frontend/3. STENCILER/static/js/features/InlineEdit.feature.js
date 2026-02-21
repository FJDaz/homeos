/**
 * InlineEdit.feature.js
 * Gère l'édition directe de texte sur le Canvas pour les Atomes (N3).
 * Conformité Art 7 §7.1 (Règle des 300 lignes)
 */

export const InlineEditUI = {
    activeInput: null,
    activeContext: null,

    /**
     * Monte un champ de saisie au-dessus d'un élément SVG.
     * @param {SVGElement} targetEl - L'élément SVG cliqué (text).
     * @param {Object} nodeData - Les données du node dans le génome.
     * @param {string} property - La propriété à modifier (name, method, endpoint).
     * @param {Function} onCommit - Callback lors de la validation.
     */
    mount(targetEl, nodeData, property, onCommit) {
        if (this.activeInput) this.close();

        const canvasContainer = document.querySelector('#slot-canvas-zone');
        if (!canvasContainer) return;

        // Calcul de la position absolue par rapport au container du canvas
        const bbox = targetEl.getBoundingClientRect();
        const containerBbox = canvasContainer.getBoundingClientRect();

        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'inline-edit-input';
        input.value = nodeData[property] || '';
        input.spellcheck = false;

        // Style hérité et positionnement
        const fontSize = window.getComputedStyle(targetEl).fontSize;
        const fontWeight = window.getComputedStyle(targetEl).fontWeight;

        Object.assign(input.style, {
            position: 'absolute',
            left: `${bbox.left - containerBbox.left}px`,
            top: `${bbox.top - containerBbox.top}px`,
            width: `${bbox.width + 20}px`,
            height: `${bbox.height + 4}px`,
            fontSize: fontSize,
            fontWeight: fontWeight,
            fontFamily: 'Geist, sans-serif',
            background: 'var(--bg-primary)',
            color: 'var(--text-primary)',
            border: '1px solid var(--accent-bleu)',
            borderRadius: '2px',
            padding: '0 4px',
            zIndex: '1000',
            outline: 'none',
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
        });

        canvasContainer.appendChild(input);
        input.focus();
        if (property === 'name') input.select();

        this.activeInput = input;
        this.activeContext = { nodeData, property, onCommit };

        // Handlers
        input.onkeydown = (e) => {
            if (e.key === 'Enter') {
                this.commit();
            } else if (e.key === 'Escape') {
                this.close();
            }
        };

        input.onblur = () => {
            this.commit();
        };
    },

    commit() {
        if (!this.activeInput || !this.activeContext) return;

        const { nodeData, property, onCommit } = this.activeContext;
        const newValue = this.activeInput.value.trim();

        if (newValue !== nodeData[property]) {
            nodeData[property] = newValue;
            console.log(`[InlineEdit] Committed ${property} -> ${newValue}`);
            if (onCommit) onCommit(nodeData, property, newValue);
        }

        this.close();
    },

    close() {
        if (this.activeInput) {
            const el = this.activeInput;
            this.activeInput = null;   // null avant remove() pour bloquer le blur→commit
            this.activeContext = null;
            el.remove();
        }
    }
};
