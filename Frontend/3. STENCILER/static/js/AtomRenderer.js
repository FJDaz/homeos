import { G } from './GRID.js';

/**
 * AtomRenderer.js
 * Moteur de Design System Sémantique (Generative UI).
 * Traduit : semantic_role, interaction_type, importance, et density
 * en de véritables primitives SVG "Premium".
 * 
 * CODE DIRECT — FJD 2026-02-21 — MISSION 13A
 */

export function renderAtom(nodeData, availableWidth, color) {
    // --- SVG-First : Payload direct depuis le génome (KIMI sandbox) ---
    if (nodeData.svg_payload) {
        return { svg: nodeData.svg_payload, h: nodeData.svg_h || G.U6, w: availableWidth };
    }

    let role = nodeData.semantic_role;
    let type = nodeData.interaction_type || 'default';

    // --- Heuristique de transition (Legacy vers V3) ---
    if (!role) {
        if (type === 'submit') role = 'action';
        else if (type === 'click') role = 'action';
        else if (type === 'input' || type === 'select') role = 'data_entry';
        else if (nodeData.visual_hint === 'table' || nodeData.visual_hint === 'list') role = 'data_display';
        else role = 'component';
    }

    let importance = nodeData.importance;
    if (!importance) {
        if (type === 'submit' || type === 'click' || role === 'action') importance = 'primary';
        else importance = 'secondary'; // Par defaut tout le reste est secondary pour etre visible
    }

    const safeName = (nodeData.name || '').substring(0, 24).toLowerCase();
    const density = nodeData.density || 'normal';

    // --- Moteurs de Styling ---

    // 1. Moteur de Tone (Importance) — Palette Hype Minimaliste (désaturée)
    // Pas de vert saturé. Tons ardoise/terra/mauve selon intent du corps parent
    const tones = {
        primary: {
            fill: 'var(--accent-ardoise, #5A6B7C)',  // Bleu ardoise (pas de vert)
            text: '#ffffff',
            stroke: 'none',
            shadow: 'premium-shadow',
            weight: '700'  // Bold
        },
        secondary: {
            fill: 'var(--bg-tertiary, #e8e7e3)',
            text: 'var(--text-primary, #3d3d3c)',
            stroke: 'var(--border-warm, #c5c4c0)',
            shadow: 'subtle-shadow',
            weight: '700'  // Bold même en secondary
        },
        tertiary: {
            fill: 'transparent',
            text: 'var(--text-secondary, #6a6a69)',
            stroke: 'var(--border-subtle, #d5d4d0)',
            shadow: '',
            weight: '600'
        },
        ghost: {
            fill: 'transparent',
            text: 'var(--text-muted, #999998)',
            stroke: 'none',
            shadow: '',
            weight: '500'
        }
    };

    // Fallback gracieux si l'importance n'est pas répertoriée
    const style = tones[importance] || tones.secondary;

    // 2. Moteur de Densité
    // Modifie la taille des composants de base
    const metrics = {
        btnHeight: density === 'compact' ? G.U4 : G.BTN,
        inputHeight: density === 'compact' ? G.U4 : G.INPUT,
        fontSize: density === 'compact' ? 9 : 11,
        smFontSize: density === 'compact' ? 8 : 10,
        radius: density === 'compact' ? 4 : 6
    };

    let svgContent = '';
    let height = G.U5; // Hauteur par défaut

    // --- Matrice de Rendu Sémantique (39 Atomes réels) ---
    const hint = nodeData.visual_hint || 'general';

    // 1. Boutons & Actions Simples
    if (hint === 'button' || hint === 'launch-button' || hint === 'apply-changes' || type === 'submit') {
        height = metrics.btnHeight;
        svgContent = `
            <rect x="0" y="0" width="${availableWidth}" height="${height}" rx="${height / 2}"
                  fill="${style.fill}" 
                  stroke="${style.stroke}" stroke-width="1.5"
                  class="${style.shadow}"/>
            <text x="${availableWidth / 2}" y="${height / 2 + 1}" 
                  font-size="${metrics.fontSize}" fill="${style.text}"
                  text-anchor="middle" dominant-baseline="middle"
                  font-family="Geist, sans-serif" font-weight="${style.weight}">${safeName}</text>
        `;
    }
    // 2. Champs de saisie & Formulaires
    else if (hint === 'form' || type === 'input' || type === 'select') {
        height = metrics.inputHeight * 2 + 10;
        svgContent = `
            <rect x="0" y="0" width="${availableWidth}" height="${metrics.inputHeight}" rx="${metrics.radius}" fill="var(--bg-tertiary)" stroke="var(--border-subtle)"/>
            <text x="12" y="${metrics.inputHeight / 2 + 3}" font-size="${metrics.fontSize}" fill="var(--text-muted)">📝 Champ 1...</text>
            <rect x="0" y="${metrics.inputHeight + 6}" width="${availableWidth}" height="${metrics.inputHeight}" rx="${metrics.radius}" fill="var(--bg-tertiary)" stroke="var(--border-subtle)"/>
            <text x="12" y="${metrics.inputHeight * 1.5 + 9}" font-size="${metrics.fontSize}" fill="var(--text-muted)">📝 Champ 2...</text>
        `;
    }
    // 3. Listes simples
    else if (hint === 'list') {
        height = 60;
        svgContent = `
            <circle cx="8" cy="15" r="3" fill="${color}"/>
            <rect x="16" y="12" width="${availableWidth - 24}" height="6" rx="2" fill="var(--bg-tertiary)"/>
            <circle cx="8" cy="30" r="3" fill="${color}"/>
            <rect x="16" y="27" width="${availableWidth - 32}" height="6" rx="2" fill="var(--bg-tertiary)"/>
            <circle cx="8" cy="45" r="3" fill="${color}"/>
            <rect x="16" y="42" width="${availableWidth - 40}" height="6" rx="2" fill="var(--bg-tertiary)"/>
        `;
    }
    // 4. Tableaux / Grilles de données strictes (IR Reports etc.)
    else if (hint === 'table') {
        height = 80;
        const colW = availableWidth / 3;
        svgContent = `
            <rect x="0" y="0" width="${availableWidth}" height="20" fill="var(--bg-tertiary)" rx="4"/>
            <text x="8" y="14" font-size="9" fill="var(--text-muted)" font-family="monospace">ID</text>
            <text x="${colW}" y="14" font-size="9" fill="var(--text-muted)" font-family="monospace">STATUS</text>
            <text x="${colW * 2}" y="14" font-size="9" fill="var(--text-muted)" font-family="monospace">ACTION</text>
            
            <rect x="0" y="24" width="${availableWidth}" height="1" fill="var(--border-subtle)"/>
            <text x="8" y="40" font-size="10" fill="var(--text-primary)">OBJ-01</text>
            <rect x="${colW}" y="32" width="40" height="12" rx="6" fill="var(--accent-terra, #C4A589)" opacity="0.3"/><text x="${colW + 20}" y="40" font-size="8" fill="var(--accent-terra, #C4A589)" text-anchor="middle" font-weight="700">actif</text>
            <text x="${colW * 2}" y="40" font-size="10" fill="${color}">Détails →</text>

            <rect x="0" y="50" width="${availableWidth}" height="1" fill="var(--border-subtle)"/>
            <text x="8" y="66" font-size="10" fill="var(--text-primary)">OBJ-02</text>
            <rect x="${colW}" y="58" width="40" height="12" rx="6" fill="var(--accent-ocre, #B87B5C)" opacity="0.3"/><text x="${colW + 20}" y="66" font-size="8" fill="var(--accent-ocre, #B87B5C)" text-anchor="middle" font-weight="700">wait</text>
            <text x="${colW * 2}" y="66" font-size="10" fill="${color}">Détails →</text>
        `;
    }
    // 5. Upload Zone
    else if (hint === 'upload') {
        height = 80;
        svgContent = `
            <rect x="0" y="0" width="${availableWidth}" height="${height}" rx="8" fill="var(--bg-tertiary)" stroke="var(--border-strong)" stroke-width="1.5" stroke-dasharray="4 4" class="subtle-shadow"/>
            <text x="${availableWidth / 2}" y="36" font-size="24" fill="var(--text-muted)" text-anchor="middle">☁️</text>
            <text x="${availableWidth / 2}" y="56" font-size="10" fill="var(--text-secondary)" text-anchor="middle" font-family="Geist">Glisser-déposer le fichier ici</text>
        `;
    }
    // 6. Navigation / Breadcrumb
    else if (hint === 'breadcrumb') {
        height = 24;
        svgContent = `
            <rect x="0" y="2" width="50" height="20" rx="4" fill="${color}20"/>
            <text x="25" y="15" font-size="9" fill="${color}" text-anchor="middle" font-weight="600">Accueil</text>
            <text x="62" y="15" font-size="12" fill="var(--text-muted)">›</text>
            <text x="75" y="15" font-size="10" fill="var(--text-secondary)">${safeName.substring(0, 15)}</text>
        `;
    }
    // 7. Accordeon
    else if (hint === 'accordion') {
        height = 36;
        svgContent = `
            <rect x="0" y="0" width="${availableWidth}" height="32" rx="6" fill="var(--bg-primary)" stroke="var(--border-subtle)" class="subtle-shadow"/>
            <text x="12" y="19" font-size="11" fill="var(--text-primary)" font-weight="600">${safeName}</text>
            <path d="M ${availableWidth - 20} 14 L ${availableWidth - 15} 19 L ${availableWidth - 10} 14" fill="none" stroke="var(--text-muted)" stroke-width="2" stroke-linecap="round"/>
        `;
    }
    // 8. Stepper (Progress)
    else if (hint === 'stepper') {
        height = 40;
        const w3 = availableWidth / 3;
        svgContent = `
            <line x1="20" y1="20" x2="${availableWidth - 20}" y2="20" stroke="var(--border-subtle)" stroke-width="2"/>
            <line x1="20" y1="20" x2="${w3}" y2="20" stroke="${color}" stroke-width="2"/>
            
            <circle cx="20" cy="20" r="10" fill="${color}"/>
            <text x="20" y="23" font-size="10" fill="white" text-anchor="middle" font-weight="bold">1</text>
            
            <circle cx="${w3}" cy="20" r="10" fill="${color}"/>
            <text x="${w3}" y="23" font-size="10" fill="white" text-anchor="middle" font-weight="bold">2</text>
            
            <circle cx="${w3 * 2}" cy="20" r="10" fill="var(--bg-primary)" stroke="var(--border-strong)" stroke-width="2"/>
            <text x="${w3 * 2}" y="24" font-size="10" fill="var(--text-muted)" text-anchor="middle" font-weight="bold">3</text>
        `;
    }
    // 9. Statut / Pastilles
    else if (hint === 'status') {
        height = 24;
        svgContent = `
            <rect x="0" y="0" width="${availableWidth}" height="24" rx="12" fill="var(--bg-tertiary)"/>
            <circle cx="12" cy="12" r="4" fill="var(--accent-terra, #C4A589)"/>
            <text x="24" y="16" font-size="10" fill="var(--text-secondary)" font-weight="700">${safeName} (actif)</text>
        `;
    }
    // 10. Dashboard Cards
    else if (hint === 'dashboard' || hint === 'detail-card' || hint === 'stencil-card') {
        height = 88; // Légèrement plus haut pour la marge
        svgContent = `
            <rect x="0" y="0" width="${availableWidth}" height="${height}" rx="8" fill="var(--bg-primary)" stroke="var(--border-subtle)" class="subtle-shadow"/>
            <rect x="12" y="12" width="24" height="24" rx="6" fill="${color}20"/>
            <text x="24" y="28" font-size="14" text-anchor="middle">📊</text>
            <text x="44" y="22" font-size="12" fill="var(--text-primary)" font-weight="700">${safeName}</text>
            <text x="44" y="50" font-size="20" fill="${color}" font-weight="800" letter-spacing="-1">1,234</text>
            <rect x="12" y="68" width="${availableWidth - 24}" height="4" rx="2" fill="var(--bg-tertiary)"/>
            <rect x="12" y="68" width="${(availableWidth - 24) * 0.6}" height="4" rx="2" fill="${color}"/>
        `;
    }
    // 11. Editor (Code)
    else if (hint === 'editor') {
        height = 100;
        svgContent = `
            <rect x="0" y="0" width="${availableWidth}" height="${height}" rx="6" fill="#1e293b"/>
            <circle cx="12" cy="12" r="3" fill="#ef4444"/><circle cx="22" cy="12" r="3" fill="#eab308"/><circle cx="32" cy="12" r="3" fill="#22c55e"/>
            <text x="12" y="32" font-size="10" fill="#7dd3fc" font-family="monospace">function</text>
            <text x="60" y="32" font-size="10" fill="#f8fafc" font-family="monospace">init() {</text>
            <text x="24" y="48" font-size="10" fill="#c4b5fd" font-family="monospace">return</text>
            <text x="64" y="48" font-size="10" fill="#a7f3d0" font-family="monospace">true;</text>
            <text x="12" y="64" font-size="10" fill="#f8fafc" font-family="monospace">}</text>
        `;
    }
    // 12. Chat / Bubbles
    else if (hint === 'chat/bubble') {
        height = 60;
        svgContent = `
            <rect x="0" y="0" width="${availableWidth * 0.7}" height="24" rx="12" fill="var(--bg-tertiary)"/>
            <text x="12" y="15" font-size="10" fill="var(--text-secondary)">Message reçu...</text>
            <rect x="${availableWidth * 0.3}" y="32" width="${availableWidth * 0.7}" height="24" rx="12" fill="${color}"/>
            <text x="${availableWidth - 12}" y="47" font-size="10" fill="white" text-anchor="end">Notre réponse ici</text>
        `;
    }
    // 13. Grille (Layout Gallery)
    else if (hint === 'grid' || hint === 'card' || hint === 'choice-card') {
        height = 100;
        const w2 = (availableWidth - 12) / 2;
        svgContent = `
            <rect x="0" y="0" width="${w2}" height="44" rx="6" fill="var(--bg-primary)" stroke="${color}" stroke-width="2" class="subtle-shadow"/>
            <circle cx="${w2 / 2}" cy="22" r="10" fill="${color}20"/><text x="${w2 / 2}" y="26" font-size="12" fill="${color}" text-anchor="middle">✓</text>
            
            <rect x="${w2 + 12}" y="0" width="${w2}" height="44" rx="6" fill="var(--bg-tertiary)" stroke="var(--border-subtle)"/>
            
            <rect x="0" y="52" width="${w2}" height="44" rx="6" fill="var(--bg-tertiary)" stroke="var(--border-subtle)"/>
            <rect x="${w2 + 12}" y="52" width="${w2}" height="44" rx="6" fill="var(--bg-tertiary)" stroke="var(--border-subtle)"/>
        `;
    }
    // Fallback UI (Texte ou action inconnue)
    else {
        height = G.U6;
        svgContent = `
            <rect class="atom-bg" x="0" y="0" width="${availableWidth}" height="${height}" rx="${metrics.radius}" 
                  fill="${style.fill}" stroke="${style.stroke}" class="${style.shadow}"/>
            <text class="atom-label" x="12" y="${height - 12}" 
                  font-size="${metrics.fontSize}" fill="${style.text}"
                  font-family="Geist, sans-serif" font-weight="700" 
                  dominant-baseline="bottom">${safeName}</text>
        `;
    }

    const ICONS = {
        'click': 'M5 12h14M12 5l7 7-7 7',
        'submit': 'M5 12h14M12 5l7 7-7 7',
        'drag': 'M5 9l-3 3 3 3M9 5l3-3 3 3M15 19l-3 3-3-3M19 9l3 3-3 3M2 12h20M12 2v20',
        'view': 'M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8zM12 9a3 3 0 100 6 3 3 0 000-6z',
        'upload': 'M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12',
        'input': 'M12 20h9M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z',
        'select': 'M9 11l3 3L22 4M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11',
        'edit': 'M12 20h9M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z',
        'default': 'M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z'
    };
    const iconPath = ICONS[type] || ICONS['default'];
    const safeColor = color || 'var(--text-primary, #3d3d3c)';
    const iconSVG = iconPath
        ? `<g transform="translate(${availableWidth - 20}, ${Math.max(2, height - 20)}) scale(0.583)" stroke="${safeColor}" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity="0.5" pointer-events="none"><path d="${iconPath}"/></g>`
        : '';

    // Le wrapper garantit que l'atome est interactif et repérable localement
    // Ajout d'une subtle shadow native SVG pour que les atomes ressortent (vu que N1/N2 n'ont plus de fond)
    return {
        svg: `<g data-id="${nodeData.id}" class="atom-pure" style="opacity: 1; transition: opacity 0.2s; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.08));">${svgContent}${iconSVG}</g>`,
        h: height,
        w: availableWidth
    };
}
