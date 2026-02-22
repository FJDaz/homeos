/**
 * CanvasLayout (SVG Layout Engine)
 * Responsabilité : Calculer les positions (x, y) des organes en fonction du type de Corps.
 */
const CanvasLayout = {
    /**
     * Calcule le layout et retourne un objet contenant les éléments et la viewBox
     */
    calculate(corpsId, sectionData, customConfig = {}) {
        const config = { width: 1024, padding: 32, ...customConfig }; // Multiples de 16
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
        const cardW = 640; // 40 * 16
        const x = (width - cardW) / 2;

        const positions = organs.map(org => {
            const pos = { x, y: currentY, w: cardW, h: 80 + (org.n2_features?.length * 16 || 0) }; // multiple de 16
            currentY += pos.h + 32; // gap de 32
            return pos;
        });

        return { positions, viewBox: { x: 0, y: 0, w: width, h: currentY + padding } };
    },

    /**
     * Layout "Architecture" : Blocs compacts empilés (Vertical Stack).
     */
    _layoutArchitecture(organs, { width, padding, cardW = 320, cardH = 64 }) { // 20*16, 4*16
        let currentY = padding;
        const x = (width - cardW) / 2;

        const positions = organs.map(org => {
            const pos = { x, y: currentY, w: cardW, h: cardH };
            currentY += pos.h + 24; // Proportionate gap multiple of 8 (24px)
            return pos;
        });

        return { positions, viewBox: { x: 0, y: 0, w: width, h: currentY + padding } };
    },

    /**
     * Layout "Composition" : Grille 2 colonnes (Page Builder).
     */
    _layoutComposition(organs, { width, padding }) {
        const cardW = 384; // 24 * 16
        const gap = 32; // 2 * 16
        const startX = (width - (cardW * 2 + gap)) / 2;
        let maxY = 0;

        const positions = organs.map((org, i) => {
            const col = i % 2;
            const row = Math.floor(i / 2);
            const x = startX + (col * (cardW + gap));
            const y = padding + (row * 160); // 10 * 16
            const pos = { x, y, w: cardW, h: 144 }; // 9 * 16
            maxY = Math.max(maxY, y + pos.h);
            return pos;
        });

        return { positions, viewBox: { x: 0, y: 0, w: width, h: maxY + padding } };
    },

    /**
     * Layout "Pipeline" : Flux horizontal (Séquence).
     */
    _layoutPipeline(organs, { width, padding }) {
        const cardW = 192; // 12 * 16
        const gap = 32; // 2 * 16
        const totalW = (organs.length * (cardW + gap)) - gap;
        const startX = padding;
        const y = 192; // 12 * 16

        const positions = organs.map((org, i) => ({
            x: startX + (i * (cardW + gap)),
            y: y,
            w: cardW,
            h: 128 // 8 * 16
        }));

        return { positions, viewBox: { x: 0, y: 0, w: Math.max(width, totalW + padding * 2), h: 640 } };
    }
};

export default CanvasLayout;
