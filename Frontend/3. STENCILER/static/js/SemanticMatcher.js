/**
 * SemanticMatcher.js
 * Résout visual_hint → WireframeLibrary hint avec couverture complète du génome.
 * Ordre de priorité : visual_hint (explicit) → interaction_type → keyword fallback
 * Mission 15A — 2026-03-01
 */

// Mapping visual_hint génome → WireframeLibrary hint
const VISUAL_HINT_MAP = {
    // Aliases (genome → library)
    'detail-card'   : 'stencil-card',
    'card'          : 'stencil-card',
    'choice-card'   : 'selection',
    'button'        : 'action-button',
    'launch-button' : 'action-button',
    'apply-changes' : 'action-button',
    'download'      : 'action-button',
    'status'        : 'dashboard',
    'list'          : 'accordion',
    'chat-input'    : 'chat-input',
    'preview'       : 'preview',
    'form'          : 'form',
    // Identité (passthrough — hints déjà couverts)
    'table': 'table', 'stencil-card': 'stencil-card', 'dashboard': 'dashboard',
    'stepper': 'stepper', 'breadcrumb': 'breadcrumb', 'grid': 'grid',
    'upload': 'upload', 'color-palette': 'color-palette', 'chat/bubble': 'chat/bubble',
    'accordion': 'accordion', 'zoom-controls': 'zoom-controls', 'editor': 'editor',
    'modal': 'modal', 'selection': 'selection', 'action-button': 'action-button',
    'nav': 'breadcrumb', 'navigation': 'breadcrumb', 'layout': 'grid',
    'search': 'brainstorm',
};

// Fallback interaction_type → hint
const INTERACTION_MAP = {
    'submit' : 'action-button',
    'drag'   : 'upload',
    'click'  : null, // pas assez précis → keyword fallback
};

export function resolveHint(data) {
    // 1. visual_hint explicite
    if (data.visual_hint) {
        const mapped = VISUAL_HINT_MAP[data.visual_hint];
        if (mapped) return mapped;
    }
    // 2. interaction_type
    if (data.interaction_type) {
        const mapped = INTERACTION_MAP[data.interaction_type];
        if (mapped) return mapped;
    }
    // 3. Keyword fallback sur id + name
    return _keywordFallback(data);
}

function _keywordFallback(data) {
    const pool = `${data.id || ''} ${data.name || ''}`.toLowerCase();
    const keywords = {
        'table': ['table', 'ir', 'listing'],
        'stepper': ['stepper', 'sequence', 'workflow'],
        'chat/bubble': ['chat', 'dialogue', 'bubble'],
        'editor': ['editor', 'code', 'json'],
        'breadcrumb': ['breadcrumb', 'navigation', 'nav'],
        'dashboard': ['dashboard', 'session', 'status', 'summary'],
        'accordion': ['accordion', 'validation', 'list'],
        'color-palette': ['palette', 'theme', 'color', 'style'],
        'upload': ['upload', 'import', 'deposit'],
        'action-button': ['deploy', 'export', 'download', 'launch', 'button'],
        'stencil-card': ['card', 'arbitrage'],
        'selection': ['selection', 'choice', 'picker'],
        'modal': ['modal', 'confirm', 'popup'],
        'grid': ['layout', 'grid', 'view', 'gallery'],
        'brainstorm': ['brainstorm', 'search', 'idea'],
        'zoom-controls': ['zoom', 'ctrl'],
    };
    for (const [hint, kws] of Object.entries(keywords)) {
        if (kws.some(k => pool.includes(k))) return hint;
    }
    return null;
}
