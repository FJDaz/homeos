/**
 * AtomPrototypes.js
 * Experimental renders for KIMI (Prototypeur DA).
 * This will be merged into AtomRenderer.js once validated.
 */

export const AtomPrototypes = {
    // Exemple d'un bouton avec micro-animation ou style différent
    renderExperimentalButton(nodeData, availableWidth, color) {
        const safeName = (nodeData.name || '').toLowerCase();
        return `
            <rect x="0" y="0" width="${availableWidth}" height="32" rx="16" fill="${color}" opacity="0.1" stroke="${color}" stroke-width="1"/>
            <text x="${availableWidth / 2}" y="20" font-size="11" fill="${color}" text-anchor="middle" font-weight="700" font-family="Geist">${safeName}</text>
        `;
    },

    // Nouveau : Prototype de bouton "Pill" ultra-détaillé en SVG pur
    getPillPrototype(name, width, color) {
        return `
            <rect x="0" y="0" width="${width}" height="32" rx="16" fill="${color}" fill-opacity="0.1" stroke="${color}" stroke-width="1.5"/>
            <circle cx="16" cy="16" r="4" fill="${color}"/>
            <text x="32" y="20" font-size="10" font-weight="800" fill="${color}" font-family="Geist">${name.toLowerCase()}</text>
        `;
    }
};
