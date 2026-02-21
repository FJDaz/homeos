/**
 * AtomRenderer.js
 * Rendu compact des Atomes (N3) — icônes inline, sans WireframeLibrary.
 * CODE DIRECT — FJD 2026-02-21
 */

export function renderAtom(interaction_type, name, pos, color) {
    const cx = pos.w / 2;
    const cy = pos.h / 2;
    const safeName = (name || '').substring(0, 18).toUpperCase();

    switch (interaction_type) {
        case 'click':
        case 'submit': {
            const bw = Math.min(pos.w - 24, 128);
            const bh = 28;
            const bx = cx - bw / 2;
            const by = cy - bh / 2;
            return `
                <rect x="${bx}" y="${by}" width="${bw}" height="${bh}" rx="14"
                      fill="${color}" opacity="0.85"/>
                <text x="${cx}" y="${cy + 1}" font-size="9" fill="white"
                      text-anchor="middle" dominant-baseline="middle"
                      font-family="Geist, sans-serif" font-weight="700">${safeName}</text>
            `;
        }
        case 'view': {
            const rowW = pos.w - 24;
            const startY = cy - 18;
            return `
                <rect x="12" y="${startY}"      width="${rowW}" height="7" rx="2" fill="var(--border-subtle)" />
                <rect x="12" y="${startY + 11}" width="${rowW * 0.75}" height="7" rx="2" fill="${color}" opacity="0.4"/>
                <rect x="12" y="${startY + 22}" width="${rowW}" height="7" rx="2" fill="var(--border-subtle)" />
                <rect x="12" y="${startY + 33}" width="${rowW * 0.6}" height="7" rx="2" fill="var(--border-subtle)" />
            `;
        }
        case 'drag': {
            const dots = [];
            for (let r = 0; r < 2; r++) {
                for (let c = 0; c < 3; c++) {
                    dots.push(`<circle cx="${cx - 16 + c * 16}" cy="${cy - 6 + r * 12}" r="3.5" fill="${color}" opacity="0.55"/>`);
                }
            }
            return dots.join('');
        }
        default: {
            const type = interaction_type || 'component';
            return `
                <text x="${cx}" y="${cy - 6}" font-size="22" text-anchor="middle"
                      dominant-baseline="middle" fill="${color}" opacity="0.35"
                      font-family="sans-serif">⬡</text>
                <text x="${cx}" y="${cy + 16}" font-size="8" text-anchor="middle"
                      fill="var(--text-muted)" font-family="Geist, sans-serif">${type}</text>
            `;
        }
    }
}
