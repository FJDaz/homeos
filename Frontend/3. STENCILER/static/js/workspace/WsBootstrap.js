/**
 * WsBootstrap.js — Workspace-specific init
 * Extracted from bootstrap.js (B2). Loaded only on /workspace pages.
 */

(function () {
    'use strict';

    function init() {
        // Mode toggle listener — show/hide GSAP effects drawer
        const modesContainer = document.querySelector('.flex.bg-slate-100.p-1.rounded-custom');
        if (modesContainer) {
            modesContainer.addEventListener('click', (e) => {
                const btn = e.target.closest('.ws-mode-btn');
                if (btn) {
                    const mode = btn.dataset.mode;
                    if (mode === 'front-dev') {
                        if (!window.WsFEEStudio_instance && window.WsFEEStudio) {
                            var wsRef = window.wsBackend || window.wsCanvas || {};
                            window.WsFEEStudio_instance = new window.WsFEEStudio(wsRef);
                        }
                        if (window.WsFEEStudio_instance) window.WsFEEStudio_instance.open();
                    } else {
                        if (window.WsFEEStudio_instance) window.WsFEEStudio_instance.close();
                    }
                    window.dispatchEvent(new CustomEvent('ws-mode-change', { detail: { mode } }));
                }
            });
        }

        // GsapCheatSheet remplacé par WsFEEStudio (M221) — désactivé
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
