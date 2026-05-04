/**
 * 🎨 UxRunHooks.js — Système de balisage narratif (Mission M375)
 * 
 * Permet de tracker les intentions UX sans polluer le code métier.
 * Typologies : NAV, DECISION, ACTION, WAIT, FRICTION, CORRECTION, ABANDON.
 */

window.UxRun = (function() {
    const API_URL = '/api/ux-run/event';
    const CATEGORIES = ['NAV', 'DECISION', 'ACTION', 'WAIT', 'FRICTION', 'CORRECTION', 'ABANDON'];

    /**
     * Envoie un signal au serveur.
     */
    async function log(category, label, details = {}) {
        if (!CATEGORIES.includes(category)) {
            console.warn(`[UxRun] Catégorie inconnue : ${category}`);
        }

        const projectId = localStorage.getItem('homeos_active_project') || 'unknown';
        const payload = {
            tag: category,
            label: label,
            ts: Date.now() / 1000,
            path: window.location.pathname,
            project_id: projectId,
            details: details
        };

        try {
            await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            console.log(`[UxRun] Signal envoyé : ${category} | ${label}`);
        } catch (e) {
            // Silencieux pour ne pas perturber l'expérience
            console.debug('[UxRun] Echec envoi signal', e);
        }
    }

    /**
     * Initialisation : Ecoute les clics sur [data-ux]
     */
    function init() {
        document.addEventListener('click', (e) => {
            const target = e.target.closest('[data-ux]');
            if (target) {
                const category = target.getAttribute('data-ux');
                const label = target.getAttribute('data-ux-label') || target.innerText.trim() || target.id;
                log(category, label);
            }
        }, true);

        console.log('🚀 UxRunHooks prêt (Typologie: 7 balises active)');
    }

    // Auto-init si on est dans le browser
    if (typeof window !== 'undefined') {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
        } else {
            init();
        }
    }

    return { log };
})();
