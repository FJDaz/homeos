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
                    <circle cx="100" cy="90" r="10" fill="${color}" />
                    <circle cx="140" cy="90" r="10" fill="${color}" />
                    <circle cx="180" cy="90" r="10" fill="var(--bg-tertiary)" stroke="var(--border-subtle)" />
                    <circle cx="220" cy="90" r="10" fill="var(--bg-tertiary)" stroke="var(--border-subtle)" />
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
                    <rect x="145" y="110" width="80" height="24" rx="4" fill="var(--border-warm)" />
                `);

            case 'action-button':
            case 'deploy':
            case 'export':
            case 'download':
            case 'launch-button':
            case 'launch':
                const btnLabel = (label || hint || 'ACT').substring(0, 5).toUpperCase();
                return wrapper(`
                    <!-- Shadow / Volume -->
                    <rect x="0" y="55" width="280" height="80" rx="40" fill="rgba(0,0,0,0.15)" />
                    <rect x="0" y="50" width="280" height="80" rx="40" fill="${color}" />
                    <!-- Inset highlight -->
                    <rect x="5" y="55" width="270" height="70" rx="35" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="2" />
                    <text x="140" y="98" font-size="32" fill="white" text-anchor="middle" font-family="Geist, sans-serif" font-weight="700">${btnLabel}</text>
                `);

            case 'upload':
                return wrapper(`
                    <rect x="30" y="30" width="220" height="120" rx="8" fill="none" stroke="var(--border-warm)" stroke-width="1.5" stroke-dasharray="6,4" />
                    <path d="M140 65 C120 65 115 80 115 85 C108 85 105 90 105 97 C105 106 112 112 120 112 L160 112 C168 112 175 106 175 97 C175 90 172 85 165 85 C165 80 160 65 140 65 Z" fill="var(--text-muted)" opacity="0.25" />
                    <path d="M140 75 L140 100 M130 85 L140 75 L150 85" fill="none" stroke="var(--text-muted)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
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
                    <rect x="45" y="42" width="60" height="6" rx="1" fill="white" opacity="0.8" />
                    <text x="230" y="50" font-size="12" fill="white" font-family="Geist, sans-serif">▼</text>
                    <rect x="30" y="60" width="220" height="40" fill="var(--bg-tertiary)" opacity="0.5" />
                    <rect x="45" y="70" width="190" height="4" rx="1" fill="var(--text-muted)" opacity="0.3" />
                    <rect x="45" y="80" width="150" height="4" rx="1" fill="var(--text-muted)" opacity="0.3" />
                    <rect x="45" y="105" width="220" height="30" rx="4" fill="var(--bg-tertiary)" stroke="var(--border-subtle)" />
                    <rect x="60" y="117" width="50" height="6" rx="1" fill="var(--text-secondary)" opacity="0.6" />
                    <text x="230" y="125" font-size="12" fill="var(--text-muted)" font-family="Geist, sans-serif">▶</text>
                `);

            case 'color-palette':
                return wrapper(`
                    <rect x="40" y="40" width="80" height="8" rx="2" fill="var(--text-muted)" opacity="0.3" />
                    <circle cx="60" cy="90" r="20" fill="var(--accent-bleu)" stroke="var(--border-warm)" stroke-width="1" />
                    <circle cx="110" cy="90" r="20" fill="var(--accent-rose)" stroke="var(--border-warm)" stroke-width="1" />
                    <circle cx="160" cy="90" r="20" fill="var(--accent-vert)" stroke="var(--border-warm)" stroke-width="1" />
                    <circle cx="210" cy="90" r="20" fill="var(--accent-orange)" stroke="var(--border-warm)" stroke-width="1" />
                    <rect x="40" y="130" width="60" height="18" rx="9" fill="var(--bg-tertiary)" />
                    <rect x="110" y="130" width="60" height="18" rx="9" fill="var(--bg-tertiary)" />
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
                    <rect x="70" y="55" width="80" height="10" rx="2" fill="var(--text-primary)" opacity="0.8" />
                    <rect x="70" y="105" width="65" height="22" rx="4" fill="var(--bg-tertiary)" stroke="var(--border-subtle)" />
                    <rect x="145" y="105" width="65" height="22" rx="4" fill="${color}" />
                `);

            case 'breadcrumb':
            case 'navigation':
                return wrapper(`
                    <rect x="0" y="0" width="280" height="180" fill="none" />
                    <rect x="5" y="40" width="270" height="100" rx="6" fill="var(--bg-tertiary)" stroke="var(--border-subtle)" />
                    <rect x="25" y="80" width="60" height="20" rx="4" fill="${color}" opacity="0.6" />
                    <text x="110" y="105" font-size="34" fill="var(--text-muted)" font-family="Geist, sans-serif">›</text>
                    <rect x="140" y="80" width="100" height="20" rx="4" fill="var(--text-primary)" opacity="0.8" />
                `);

            case 'zoom-controls':
                return wrapper(`
                    <rect x="40" y="75" width="200" height="30" rx="15" fill="var(--bg-primary)" stroke="var(--border-warm)" />
                    <text x="60" y="94" font-size="14" fill="var(--text-secondary)" text-anchor="middle" font-family="Geist, sans-serif">←</text>
                    <rect x="120" y="86" width="40" height="8" rx="2" fill="var(--text-primary)" opacity="0.3" />
                    <text x="220" y="94" font-size="14" fill="var(--text-secondary)" text-anchor="middle" font-family="Geist, sans-serif">→</text>
                `);

            // Brainstorm / Search fallback
            case 'brainstorm':
                return wrapper(`
                    <circle cx="140" cy="90" r="40" fill="none" stroke="${color}" stroke-width="2" stroke-dasharray="4,4" />
                    <circle cx="140" cy="90" r="15" fill="${color}" opacity="0.4" />
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

            case 'flowbite/accordion':
                return wrapper(`
                    <rect x="30" y="30" width="220" height="120" rx="8" fill="var(--bg-tertiary)" />
                    <rect x="45" y="45" width="100" height="8" rx="2" fill="${color}" />
                    <rect x="45" y="65" width="190" height="4" rx="1" fill="var(--text-muted)" opacity="0.4" />
                    <rect x="45" y="75" width="160" height="4" rx="1" fill="var(--text-muted)" opacity="0.4" />
                    <line x1="45" y1="100" x2="235" y2="100" stroke="var(--border-subtle)" />
                    <rect x="45" y="115" width="80" height="8" rx="2" fill="var(--text-muted)" opacity="0.4" />
                `);

            case 'flowbite/alert':
                return wrapper(`
                    <rect x="40" y="40" width="200" height="100" rx="8" fill="var(--bg-tertiary)" stroke="var(--border-subtle)" />
                    <rect x="55" y="55" width="60" height="8" rx="4" fill="${color}" />
                    <rect x="55" y="75" width="150" height="4" rx="1" fill="var(--text-muted)" opacity="0.4" />
                    <rect x="55" y="85" width="160" height="4" rx="1" fill="var(--text-muted)" opacity="0.4" />
                    <rect x="55" y="110" width="40" height="14" rx="3" fill="${color}" />
                `);

            case 'flowbite/button':
                return wrapper(`
                    <rect x="40" y="70" width="200" height="40" rx="6" fill="${color}" />
                    <rect x="60" y="85" width="160" height="10" rx="2" fill="white" opacity="0.3" />
                `);

            case 'shadcn/card':
                return wrapper(`
                    <rect x="20" y="20" width="240" height="140" rx="8" fill="var(--bg-primary)" stroke="var(--border-subtle)" stroke-width="1"/>
                    <rect x="40" y="40" width="100" height="10" rx="2" fill="var(--text-primary)"/>
                    <rect x="40" y="60" width="180" height="6" rx="1" fill="var(--text-muted)" opacity="0.4"/>
                    <rect x="40" y="70" width="160" height="6" rx="1" fill="var(--text-muted)" opacity="0.4"/>
                    <rect x="40" y="120" width="200" height="1" fill="var(--border-subtle)"/>
                    <rect x="40" y="135" width="60" height="12" rx="4" fill="${color}"/>
                `);

            case 'shadcn/tabs':
                return wrapper(`
                    <rect x="20" y="30" width="240" height="30" rx="6" fill="var(--bg-tertiary)"/>
                    <rect x="25" y="35" width="75" height="20" rx="4" fill="var(--bg-primary)" />
                    <rect x="105" y="42" width="60" height="6" rx="1" fill="var(--text-muted)" opacity="0.4"/>
                    <rect x="180" y="42" width="60" height="6" rx="1" fill="var(--text-muted)" opacity="0.4"/>
                    <rect x="20" y="70" width="240" height="80" rx="8" fill="var(--bg-primary)" stroke="var(--border-subtle)"/>
                `);

            case 'radix/popover':
                return wrapper(`
                    <rect x="110" y="120" width="60" height="25" rx="4" fill="${color}"/>
                    <path d="M140 120 L135 110 L145 110 Z" fill="var(--bg-primary)" stroke="var(--border-subtle)"/>
                    <rect x="60" y="40" width="160" height="70" rx="8" fill="var(--bg-primary)" stroke="var(--border-subtle)" />
                    <rect x="80" y="60" width="100" height="6" rx="1" fill="var(--text-muted)" opacity="0.4"/>
                    <rect x="80" y="75" width="120" height="6" rx="1" fill="var(--text-muted)" opacity="0.4"/>
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

            case 'chat-input':
                return wrapper(`
                    <rect x="20" y="130" width="200" height="32" rx="16" fill="var(--bg-tertiary)" stroke="var(--border-default)" stroke-width="1"/>
                    <rect x="36" y="141" width="100" height="10" rx="5" fill="var(--text-muted)" opacity="0.4"/>
                    <circle cx="232" cy="146" r="12" fill="${color}"/>
                    <path d="M226 146 L232 140 L238 146 M232 140 L232 152" fill="none" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
                    <rect x="20" y="30" width="140" height="28" rx="14" fill="${color}" opacity="0.3"/>
                    <rect x="100" y="68" width="140" height="28" rx="14" fill="var(--bg-tertiary)" stroke="var(--border-default)" stroke-width="1"/>
                    <rect x="20" y="106" width="80" height="16" rx="8" fill="${color}" opacity="0.15"/>
                `);

            case 'preview':
                return wrapper(`
                    <rect x="20" y="20" width="240" height="100" rx="8" fill="var(--bg-tertiary)" stroke="var(--border-default)" stroke-width="1"/>
                    <rect x="32" y="32" width="216" height="60" rx="4" fill="var(--bg-secondary)" opacity="0.7"/>
                    <rect x="32" y="100" width="60" height="8" rx="4" fill="var(--text-muted)" opacity="0.4"/>
                    <rect x="100" y="100" width="40" height="8" rx="4" fill="${color}" opacity="0.5"/>
                    <rect x="20" y="135" width="60" height="36" rx="4" fill="${color}" opacity="0.25" stroke="${color}" stroke-width="1.5"/>
                    <rect x="88" y="135" width="60" height="36" rx="4" fill="var(--bg-tertiary)" stroke="var(--border-default)" stroke-width="1"/>
                    <rect x="156" y="135" width="60" height="36" rx="4" fill="var(--bg-tertiary)" stroke="var(--border-default)" stroke-width="1"/>
                `);

            case 'form':
                return wrapper(`
                    <rect x="20" y="20" width="60" height="8" rx="4" fill="var(--text-muted)" opacity="0.5"/>
                    <rect x="20" y="34" width="240" height="28" rx="6" fill="var(--bg-tertiary)" stroke="var(--border-default)" stroke-width="1"/>
                    <rect x="20" y="72" width="80" height="8" rx="4" fill="var(--text-muted)" opacity="0.5"/>
                    <rect x="20" y="86" width="240" height="28" rx="6" fill="var(--bg-tertiary)" stroke="var(--border-default)" stroke-width="1"/>
                    <rect x="20" y="130" width="240" height="36" rx="8" fill="${color}" opacity="0.85"/>
                    <rect x="100" y="142" width="80" height="10" rx="5" fill="white" opacity="0.9"/>
                `);

            default:
                return null;
        }
    }
};
