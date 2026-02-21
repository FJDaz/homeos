/**
 * CanvasLayout (SVG Layout Engine)
 * Responsabilité : Calculer les positions (x, y) des organes en fonction du type de Corps.
 */
const CanvasLayout = {
    /**
     * Calcule le layout et retourne un objet contenant les éléments et la viewBox
     */
    calculate(corpsId, sectionData, customConfig = {}) {
        const config = { width: 1000, padding: 40, ...customConfig };
        const type = corpsId.replace('n0_', '');
        const organs = sectionData || [];

        switch (type) {
            case 'brainstorm': return this._layoutExploration(organs, config);
            case 'backend': return this._layoutArchitecture(organs, config);
            case 'frontend': return this._layoutComposition(organs, config);
            case 'deploy': return this._layoutPipeline(organs, config);
            default: return this._layoutArchitecture(organs, config);
        }
    },

    /**
     * Layout "Exploration" : Colonne centrée large, propice à l'idéation.
     */
    _layoutExploration(organs, { width, padding }) {
        let currentY = padding;
        const cardW = 600;
        const x = (width - cardW) / 2;

        const positions = organs.map(org => {
            const pos = { x, y: currentY, w: cardW, h: 80 + (org.n2_features?.length * 15 || 0) };
            currentY += pos.h + 30;
            return pos;
        });

        return { positions, viewBox: { x: 0, y: 0, w: width, h: currentY + padding } };
    },

    /**
     * Layout "Architecture" : Blocs compacts empilés (Vertical Stack).
     */
    _layoutArchitecture(organs, { width, padding, cardW = 300, cardH = 50 }) {
        let currentY = padding;
        const x = (width - cardW) / 2;

        const positions = organs.map(org => {
            const pos = { x, y: currentY, w: cardW, h: cardH };
            currentY += pos.h + (cardH * 0.3); // Proportionate gap
            return pos;
        });

        return { positions, viewBox: { x: 0, y: 0, w: width, h: currentY + padding } };
    },

    /**
     * Layout "Composition" : Grille 2 colonnes (Page Builder).
     */
    _layoutComposition(organs, { width, padding }) {
        const cardW = 400;
        const gap = 40;
        const startX = (width - (cardW * 2 + gap)) / 2;
        let maxY = 0;

        const positions = organs.map((org, i) => {
            const col = i % 2;
            const row = Math.floor(i / 2);
            const x = startX + (col * (cardW + gap));
            const y = padding + (row * 160);
            const pos = { x, y, w: cardW, h: 140 };
            maxY = Math.max(maxY, y + pos.h);
            return pos;
        });

        return { positions, viewBox: { x: 0, y: 0, w: width, h: maxY + padding } };
    },

    /**
     * Layout "Pipeline" : Flux horizontal (Séquence).
     */
    _layoutPipeline(organs, { width, padding }) {
        const cardW = 180;
        const gap = 60;
        const totalW = (organs.length * (cardW + gap)) - gap;
        const startX = padding;
        const y = 200;

        const positions = organs.map((org, i) => ({
            x: startX + (i * (cardW + gap)),
            y: y,
            w: cardW,
            h: 120
        }));

        return { positions, viewBox: { x: 0, y: 0, w: Math.max(width, totalW + padding * 2), h: 600 } };
    }
};

export default CanvasLayout;
