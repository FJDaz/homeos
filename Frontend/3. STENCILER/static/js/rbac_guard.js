/**
 * rbac_guard.js — HoméOS
 * Mission 283b : Contrôle des accès (Plan FREE/PRO/MAX)
 */

window.RBAC_GUARD = (function() {
    'use strict';

    function getSession() {
        try {
            return JSON.parse(localStorage.getItem('homeos_session') || '{}');
        } catch(e) {
            return {};
        }
    }

    /**
     * Vérifie si l'utilisateur a accès à une fonctionnalité.
     * @param {string} feature - 'stitch', 'byok', 'forge', etc.
     * @returns {boolean}
     */
    function canAccess(feature) {
        const session = getSession();
        if (!session.entitlements) return true; // Fail-safe: accès par défaut si non renseigné

        const val = session.entitlements[feature];
        
        // Si c'est un booléen, on retourne direct
        if (typeof val === 'boolean') return val;
        
        // Si c'est une liste (ex: ai_models), on vérifie si '*' est présent
        if (Array.isArray(val)) {
            if (val.includes('*')) return true;
        }

        return !!val;
    }

    /**
     * Applique les restrictions visuelles sur le DOM.
     * Cherche les éléments avec data-feature="xxx".
     */
    function applyGuards() {
        const session = getSession();
        const plan = session.plan || 'FREE';
        
        document.querySelectorAll('[data-feature]').forEach(el => {
            const feature = el.dataset.feature;
            if (!canAccess(feature)) {
                el.classList.add('rbac-blocked');
                el.setAttribute('title', `Feature réservée au plan PRO (votre plan: ${plan})`);
                
                // Si c'est un bouton ou lien, on le désactive
                if (el.tagName === 'BUTTON' || el.tagName === 'A') {
                    el.style.opacity = '0.5';
                    el.style.pointerEvents = 'none';
                    el.style.filter = 'grayscale(1)';
                }
            }
        });
    }

    // Export public
    return {
        canAccess: canAccess,
        applyGuards: applyGuards,
        getPlan: () => getSession().plan || 'FREE'
    };
})();

// Auto-init au chargement du DOM
document.addEventListener('DOMContentLoaded', () => {
    window.RBAC_GUARD.applyGuards();
});
