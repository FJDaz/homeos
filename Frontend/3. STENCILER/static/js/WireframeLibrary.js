/**
 * WireframeLibrary.js
 * Bibliothèque des composants SVG natifs pour le Stenciler.
 * Extraite de Mission 7A.
 */

export const WireframeLibrary = {
    /**
     * Retourne le contenu SVG correspondant au hint.
     * @param {string} hint - Identifiant du wireframe (ex: 'table', 'stepper')
     * @param {string} color - Couleur d'accentuation (hex ou var)
     * @param {number} width - Largeur cible
     * @param {number} height - Hauteur cible
     * @param {string} label - Label text to display (optional)
     * @returns {string|null} - Snippet SVG ou null
     */
    getSVG(hint, color = 'var(--accent-bleu)', width = 280, height = 180, label = '') {
        // Ratio de scale proportionnel par rapport à la base 280x180
        const scale = Math.min(width / 280, height / 180);

        // Centrage du wireframe dans la boîte cible
        const offsetX = (width - 280 * scale) / 2;
        const offsetY = (height - 180 * scale) / 2;

        const wrapper = (content) => `<g transform="translate(${offsetX}, ${offsetY}) scale(${scale})">${content}</g>`;

        switch (hint?.toLowerCase()) {
            case 'table':
                return wrapper(`
                    <rect x="20" y="30" width="240" height="120" rx="8" fill="var(--bg-tertiary)" />
                    <rect x="35" y="45" width="140" height="10" rx="2" fill="var(--border-subtle)" />
                    <rect x="185" y="45" width="60" height="10" rx="2" fill="var(--border-subtle)" />
                    <rect x="35" y="65" width="140" height="10" rx="2" fill="var(--border-subtle)" />
                    <rect x="185" y="65" width="60" height="10" rx="2" fill="${color}" />
                    <text x="215" y="73" font-size="7" fill="black" text-anchor="middle" font-family="Geist, sans-serif" font-weight="700">accept</text>
                    <rect x="35" y="85" width="140" height="10" rx="2" fill="var(--border-subtle)" />
                    <rect x="185" y="85" width="60" height="10" rx="2" fill="var(--border-subtle)" />
                    <rect x="35" y="105" width="140" height="10" rx="2" fill="var(--border-subtle)" />
                    <rect x="185" y="105" width="60" height="10" rx="2" fill="var(--border-subtle)" />
                `);

            case 'stepper':
                return wrapper(`
                    <line x1="60" y1="90" x2="220" y2="90" stroke="var(--border-subtle)" stroke-width="2" />
                    <line x1="60" y1="90" x2="140" y2="90" stroke="${color}" stroke-width="2" />
                    <circle cx="60" cy="90" r="10" fill="${color}" />
                    <text x="60" y="93.5" font-size="8" fill="white" text-anchor="middle" font-family="Geist, sans-serif" font-weight="700">✓</text>
                    <circle cx="100" cy="90" r="10" fill="${color}" />
                    <text x="100" y="93.5" font-size="8" fill="white" text-anchor="middle" font-family="Geist, sans-serif" font-weight="700">✓</text>
                    <circle cx="140" cy="90" r="10" fill="${color}" />
                    <text x="140" y="93.5" font-size="8" fill="white" text-anchor="middle" font-family="Geist, sans-serif" font-weight="700">3</text>
                    <circle cx="180" cy="90" r="10" fill="var(--bg-tertiary)" stroke="var(--border-subtle)" />
                    <text x="180" y="93.5" font-size="8" fill="var(--text-muted)" text-anchor="middle" font-family="Geist, sans-serif">4</text>
                    <circle cx="220" cy="90" r="10" fill="var(--bg-tertiary)" stroke="var(--border-subtle)" />
                    <text x="220" y="93.5" font-size="8" fill="var(--text-muted)" text-anchor="middle" font-family="Geist, sans-serif">5</text>
                `);

            case 'chat/bubble':
            case 'chat':
            case 'dialogue':
                return wrapper(`
                    <rect x="30" y="40" width="140" height="30" rx="12" fill="var(--bg-tertiary)" />
                    <path d="M30 70 L30 75 L40 70 Z" fill="var(--bg-tertiary)" />
                    <rect x="45" y="52" width="100" height="6" rx="1" fill="var(--text-muted)" opacity="0.4" />
                    <rect x="110" y="85" width="140" height="30" rx="12" fill="${color}" />
                    <path d="M250 115 L250 120 L240 115 Z" fill="${color}" />
                    <rect x="125" y="97" width="100" height="6" rx="1" fill="white" opacity="0.6" />
                    <rect x="30" y="130" width="100" height="20" rx="10" fill="var(--bg-tertiary)" />
                    <path d="M30 150 L30 155 L40 150 Z" fill="var(--bg-tertiary)" />
                `);

            case 'stencil-card':
                return wrapper(`
                    <rect x="40" y="30" width="200" height="120" rx="6" fill="var(--bg-tertiary)" stroke="var(--border-subtle)" />
                    <rect x="55" y="45" width="100" height="10" rx="2" fill="var(--accent-rose)" />
                    <rect x="55" y="62" width="160" height="6" rx="1" fill="var(--text-muted)" opacity="0.4" />
                    <rect x="55" y="72" width="140" height="6" rx="1" fill="var(--text-muted)" opacity="0.4" />
                    <rect x="55" y="110" width="80" height="24" rx="4" fill="var(--accent-vert)" />
                    <text x="95" y="125" font-size="8" fill="white" text-anchor="middle" font-family="Geist, sans-serif" font-weight="700">garder</text>
                    <rect x="145" y="110" width="80" height="24" rx="4" fill="var(--border-warm)" />
                    <text x="185" y="125" font-size="8" fill="var(--text-secondary)" text-anchor="middle" font-family="Geist, sans-serif" font-weight="700">réserve</text>
                `);

            case 'action-button':
            case 'deploy':
            case 'export':
            case 'download':
            case 'launch-button':
            case 'launch':
                const btnLabel = label || hint || 'ACTION';
                const fontSize = btnLabel.length > 12 ? Math.max(12, 32 - (btnLabel.length - 12) * 1.5) : 32;
                return wrapper(`
                    <!-- Shadow / Volume -->
                    <rect x="0" y="55" width="280" height="80" rx="40" fill="rgba(0,0,0,0.15)" />
                    <rect x="0" y="50" width="280" height="80" rx="40" fill="${color}" />
                    <!-- Inset highlight -->
                    <rect x="5" y="55" width="270" height="70" rx="35" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="2" />
                    <text x="140" y="98" font-size="${fontSize}" fill="white" text-anchor="middle" font-family="Geist, sans-serif" font-weight="700">${btnLabel}</text>
                `);

            case 'upload':
                return wrapper(`
                    <rect x="30" y="30" width="220" height="120" rx="8" fill="none" stroke="var(--border-warm)" stroke-width="1.5" stroke-dasharray="6,4" />
                    <path d="M140 65 C120 65 115 80 115 85 C108 85 105 90 105 97 C105 106 112 112 120 112 L160 112 C168 112 175 106 175 97 C175 90 172 85 165 85 C165 80 160 65 140 65 Z" fill="var(--text-muted)" opacity="0.25" />
                    <text x="140" y="125" font-size="11" fill="var(--text-secondary)" text-anchor="middle" font-family="Geist, sans-serif" font-weight="700">déposer fichiers</text>
                    <text x="140" y="138" font-size="8" fill="var(--text-muted)" text-anchor="middle" font-family="Geist, sans-serif">PDF, PNG (Max 10MB)</text>
                `);

            case 'dashboard':
            case 'session':
                return wrapper(`
                    <rect x="30" y="40" width="105" height="45" rx="4" fill="var(--bg-tertiary)" stroke="var(--border-subtle)" />
                    <rect x="30" y="40" width="105" height="8" rx="4" fill="${color}" />
                    <rect x="40" y="58" width="85" height="4" rx="1" fill="var(--border-subtle)" />
                    <rect x="40" y="68" width="60" height="4" rx="1" fill="var(--border-subtle)" />
                    <rect x="145" y="40" width="105" height="45" rx="4" fill="var(--bg-tertiary)" stroke="var(--border-subtle)" />
                    <rect x="145" y="40" width="105" height="8" rx="4" fill="var(--accent-vert)" />
                    <rect x="155" y="58" width="85" height="4" rx="1" fill="var(--border-subtle)" />
                    <rect x="155" y="68" width="60" height="4" rx="1" fill="var(--border-subtle)" />
                    <rect x="30" y="95" width="105" height="45" rx="4" fill="var(--bg-tertiary)" stroke="var(--border-subtle)" />
                    <rect x="30" y="95" width="105" height="8" rx="4" fill="var(--accent-rose)" />
                    <rect x="145" y="95" width="105" height="45" rx="4" fill="var(--bg-tertiary)" stroke="var(--border-subtle)" />
                    <rect x="145" y="95" width="105" height="8" rx="4" fill="var(--accent-orange)" />
                `);

            case 'accordion':
            case 'validation':
                return wrapper(`
                    <rect x="30" y="30" width="220" height="30" rx="4" fill="${color}" />
                    <text x="45" y="50" font-size="10" fill="white" font-family="Geist, sans-serif" font-weight="700">zones validées</text>
                    <text x="230" y="50" font-size="12" fill="white" font-family="Geist, sans-serif">▼</text>
                    <rect x="30" y="60" width="220" height="40" fill="var(--bg-tertiary)" opacity="0.5" />
                    <rect x="45" y="70" width="190" height="4" rx="1" fill="var(--text-muted)" opacity="0.3" />
                    <rect x="45" y="80" width="150" height="4" rx="1" fill="var(--text-muted)" opacity="0.3" />
                    <rect x="45" y="105" width="220" height="30" rx="4" fill="var(--bg-tertiary)" stroke="var(--border-subtle)" />
                    <text x="45" y="125" font-size="10" fill="var(--text-secondary)" font-family="Geist, sans-serif" font-weight="700">ajustements</text>
                    <text x="230" y="125" font-size="12" fill="var(--text-muted)" font-family="Geist, sans-serif">▶</text>
                `);

            case 'color-palette':
                return wrapper(`
                    <text x="40" y="50" font-size="11" fill="var(--text-primary)" font-family="Geist, sans-serif" font-weight="700">palette extraite</text>
                    <circle cx="60" cy="90" r="20" fill="var(--accent-bleu)" stroke="var(--border-warm)" stroke-width="1" />
                    <circle cx="110" cy="90" r="20" fill="var(--accent-rose)" stroke="var(--border-warm)" stroke-width="1" />
                    <circle cx="160" cy="90" r="20" fill="var(--accent-vert)" stroke="var(--border-warm)" stroke-width="1" />
                    <circle cx="210" cy="90" r="20" fill="var(--accent-orange)" stroke="var(--border-warm)" stroke-width="1" />
                    <rect x="40" y="130" width="60" height="18" rx="9" fill="var(--bg-tertiary)" />
                    <text x="70" y="142" font-size="8" fill="var(--text-secondary)" text-anchor="middle" font-family="Geist, sans-serif">Rounded</text>
                    <rect x="110" y="130" width="60" height="18" rx="9" fill="var(--bg-tertiary)" />
                    <text x="140" y="142" font-size="8" fill="var(--text-secondary)" text-anchor="middle" font-family="Geist, sans-serif">Geist Sans</text>
                `);

            case 'editor':
                return wrapper(`
                    <rect width="280" height="180" rx="8" fill="#1e1e1e" />
                    <path d="M0 8 Q0 0 8 0 L272 0 Q280 0 280 8 L280 180 Q280 180 272 180 L8 180 Q0 180 0 180 Z" fill="#1e1e1e" />
                    <rect x="0" y="0" width="280" height="25" fill="#2d2d2d" />
                    <circle cx="15" cy="12.5" r="3" fill="#ff5f56" />
                    <circle cx="27" cy="12.5" r="3" fill="#ffbd2e" />
                    <circle cx="39" cy="12.5" r="3" fill="#27c93f" />
                    <text x="140" y="16" font-size="8" fill="#888" text-anchor="middle" font-family="Geist Mono, monospace">${label || 'script.js'}</text>
                    <!-- Code Lines -->
                    <g opacity="0.8">
                        <rect x="45" y="45" width="40" height="4" rx="1" fill="#c678dd" />
                        <rect x="90" y="45" width="80" height="4" rx="1" fill="#61afef" />
                        <rect x="45" y="55" width="120" height="4" rx="1" fill="#98c379" />
                        <rect x="45" y="65" width="20" height="4" rx="1" fill="#abb2bf" />
                        <rect x="70" y="65" width="60" height="4" rx="1" fill="#e06c75" />
                        
                        <rect x="45" y="85" width="30" height="4" rx="1" fill="#c678dd" />
                        <rect x="80" y="85" width="100" height="4" rx="1" fill="#61afef" />
                        <rect x="45" y="95" width="60" height="4" rx="1" fill="#abb2bf" />
                        <rect x="110" y="95" width="40" height="4" rx="1" fill="#d19a66" />
                    </g>
                    <rect x="0" y="25" width="35" height="155" fill="#1e1e1e" stroke="#333" stroke-width="0.5" />
                `);

            case 'modal':
                return wrapper(`
                    <rect width="280" height="180" fill="black" opacity="0.3" />
                    <rect x="50" y="40" width="180" height="100" rx="8" fill="var(--bg-primary)" stroke="var(--border-warm)" />
                    <text x="70" y="65" font-size="12" fill="var(--text-primary)" font-family="Geist, sans-serif" font-weight="700">confirmer</text>
                    <rect x="70" y="105" width="65" height="22" rx="4" fill="var(--bg-tertiary)" stroke="var(--border-subtle)" />
                    <text x="102.5" y="119" font-size="8" fill="var(--text-secondary)" text-anchor="middle" font-family="Geist, sans-serif" font-weight="700">annuler</text>
                    <rect x="145" y="105" width="65" height="22" rx="4" fill="${color}" />
                    <text x="177.5" y="119" font-size="8" fill="white" text-anchor="middle" font-family="Geist, sans-serif" font-weight="700">ok</text>
                `);

            case 'breadcrumb':
            case 'navigation':
                return wrapper(`
                    <rect x="0" y="0" width="280" height="180" fill="none" />
                    <rect x="5" y="40" width="270" height="100" rx="6" fill="var(--bg-tertiary)" stroke="var(--border-subtle)" />
                    <text x="20" y="105" font-size="34" fill="${color}" font-family="Geist, sans-serif" font-weight="600">Phase</text>
                    <text x="110" y="105" font-size="34" fill="var(--text-muted)" font-family="Geist, sans-serif">›</text>
                    <text x="140" y="105" font-size="34" fill="var(--text-primary)" font-family="Geist, sans-serif" font-weight="700">Section Active</text>
                `);

            case 'zoom-controls':
                return wrapper(`
                    <rect x="40" y="75" width="200" height="30" rx="15" fill="var(--bg-primary)" stroke="var(--border-warm)" />
                    <text x="60" y="94" font-size="14" fill="var(--text-secondary)" text-anchor="middle" font-family="Geist, sans-serif">←</text>
                    <text x="140" y="94" font-size="10" fill="var(--text-primary)" text-anchor="middle" font-family="Geist, sans-serif" font-weight="600">🔍 ZOOM</text>
                    <text x="220" y="94" font-size="14" fill="var(--text-secondary)" text-anchor="middle" font-family="Geist, sans-serif">→</text>
                `);

            // Brainstorm / Search fallback
            case 'brainstorm':
                return wrapper(`
                    <circle cx="140" cy="90" r="40" fill="none" stroke="${color}" stroke-width="2" stroke-dasharray="4,4" />
                    <text x="140" y="94" font-size="24" text-anchor="middle" dominant-baseline="middle">💡</text>
                `);

            case 'grid':
                return wrapper(`
                    <rect x="20" y="30" width="70" height="50" rx="4" fill="var(--bg-tertiary)" stroke="var(--border-subtle)" />
                    <rect x="105" y="30" width="70" height="50" rx="4" fill="none" stroke="${color}" stroke-dasharray="3,2" />
                    <rect x="190" y="30" width="70" height="50" rx="4" fill="var(--bg-tertiary)" stroke="var(--border-subtle)" />
                    <rect x="20" y="100" width="70" height="50" rx="4" fill="var(--bg-tertiary)" stroke="var(--border-subtle)" />
                    <rect x="105" y="100" width="70" height="50" rx="4" fill="var(--bg-tertiary)" stroke="var(--border-subtle)" />
                    <rect x="190" y="100" width="70" height="50" rx="4" fill="var(--bg-tertiary)" stroke="var(--border-subtle)" />
                `);

            case 'selection':
                return wrapper(`
                    <rect x="20" y="40" width="75" height="100" rx="8" fill="var(--bg-tertiary)" stroke="var(--border-subtle)" />
                    <rect x="102" y="35" width="76" height="110" rx="8" fill="none" stroke="${color}" stroke-width="2" />
                    <rect x="185" y="40" width="75" height="100" rx="8" fill="var(--bg-tertiary)" stroke="var(--border-subtle)" />
                    <circle cx="57.5" cy="75" r="10" fill="var(--text-muted)" opacity="0.2" />
                    <circle cx="140" cy="75" r="12" fill="${color}" opacity="0.3" />
                    <circle cx="222.5" cy="75" r="10" fill="var(--text-muted)" opacity="0.2" />
                `);

            default:
                return null;
        }
    }
};
