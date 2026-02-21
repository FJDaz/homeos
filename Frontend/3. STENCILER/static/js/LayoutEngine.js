/**
 * LayoutEngine.js
 * Intelligence de placement spatial pour le Stenciler.
 * Basé sur une classification sémantique par zones (TOP, CENTER, RIGHT, BOTTOM, FLOATING).
 */

export const LayoutEngine = {
    /**
     * Propose un placement spatial pour les sections d'un corps.
     */
    proposeLayout(phaseData, canvasWidth = 1200, canvasHeight = 900) {
        const sections = phaseData?.n1_sections || [];

        if (sections.length === 0) return { positions: [], viewBox: { x: 0, y: 0, w: canvasWidth, h: canvasHeight } };

        // 2. Classifications en zones
        const distribution = { TOP: [], CENTER: [], RIGHT: [], BOTTOM: [], FLOATING: [], UNKNOWN: [] };

        sections.forEach(sec => {
            const searchPool = `${sec.id} ${sec.name || ''} ${sec.visual_hint || ''}`.toLowerCase();

            const mapping = {
                TOP: ['stepper', 'breadcrumb', 'navigation', 'nav', 'zoom'],
                RIGHT: ['dashboard', 'session', 'status', 'accordion', 'validation', 'palette', 'color', 'detail'],
                BOTTOM: ['download', 'export', 'launch', 'button', 'deploy'],
                FLOATING: ['modal', 'confirm']
            };

            let zoneFound = null;
            for (const [zone, keys] of Object.entries(mapping)) {
                if (keys.some(k => searchPool.includes(k))) {
                    zoneFound = zone;
                    break;
                }
            }

            if (zoneFound) {
                distribution[zoneFound].push(sec);
            } else {
                distribution.CENTER.push(sec);
            }
        });

        const positions = [];
        const padding = 20;

        // TOP : Rangée horizontale haute
        const hTop = 60;
        const nTop = distribution.TOP.length;
        const wTopTotal = canvasWidth - (padding * 2);
        const wTopCell = nTop > 0 ? (wTopTotal / nTop) : 0;

        distribution.TOP.forEach((sec, i) => {
            const w = Math.min(200, wTopCell - padding);
            const h = hTop - 20;
            positions.push({
                id: sec.id,
                x: padding + (i * wTopCell),
                y: (hTop - h) / 2,
                w, h,
                zone: 'TOP'
            });
        });

        // RIGHT : Colonne droite - Beaucoup plus compacte
        const wRight = 200;
        const xRight = canvasWidth - wRight - padding;
        distribution.RIGHT.forEach((sec, i) => {
            const h = 100;
            positions.push({
                id: sec.id,
                x: xRight,
                y: hTop + padding + (i * (h + padding)),
                w: wRight,
                h,
                zone: 'RIGHT'
            });
        });

        // CENTER : Grille compacte (4 colonnes, taille fixe 180x120)
        const xCenter = padding;
        const yCenter = hTop + padding;
        const cols = 4; // Plus de colonnes pour la densité
        const wCell = 180;
        const hCell = 110;

        distribution.CENTER.forEach((sec, i) => {
            const row = Math.floor(i / cols);
            const col = i % cols;
            positions.push({
                id: sec.id,
                x: xCenter + (col * (wCell + padding)),
                y: yCenter + (row * (hCell + padding)),
                w: wCell,
                h: hCell,
                zone: 'CENTER'
            });
        });

        // BOTTOM
        const yBottom = canvasHeight - 70 - padding;
        const wBottom = 160;
        const hBottom = 40;
        const nBottom = distribution.BOTTOM.length;

        distribution.BOTTOM.forEach((sec, i) => {
            positions.push({
                id: sec.id,
                x: canvasWidth - padding - ((nBottom - i) * (wBottom + padding)),
                y: yBottom + 10,
                w: wBottom,
                h: hBottom,
                zone: 'BOTTOM'
            });
        });

        // FLOATING
        distribution.FLOATING.forEach((sec) => {
            const w = 400;
            const h = 250;
            positions.push({
                id: sec.id,
                x: (canvasWidth - w) / 2,
                y: (canvasHeight - h) / 2,
                w: w,
                h: h,
                zone: 'FLOATING'
            });
        });

        return {
            positions,
            viewBox: { x: 0, y: 0, w: canvasWidth, h: canvasHeight }
        };
    }
};

export default LayoutEngine;
