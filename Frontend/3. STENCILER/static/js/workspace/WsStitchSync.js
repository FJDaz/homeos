/**
 * WsStitchSync — M281
 * Polling Stitch toutes les 2 min → détecte nouveaux écrans → pull auto HTML
 * Toast notification quand un nouveau screen est détecté
 */
(function() {
    'use strict';
    console.log('[WsStitchSync] init');

    let pollTimer = null;
    let knownScreenCount = 0;
    let maxPolls = 8;  // 8 polls × 2min = 16 min max par session
    let pollCount = 0;

    function startPolling() {
        if (pollTimer) return;
        console.log('[WsStitchSync] Polling démarré (2min, max ' + maxPolls + ' polls)');

        // Premier poll immédiat pour établir la baseline
        doPoll();

        pollTimer = setInterval(() => {
            if (pollCount >= maxPolls) {
                console.log('[WsStitchSync] Max polls atteint, arrêt');
                stopPolling();
                return;
            }
            doPoll();
        }, 120000); // 2 minutes
    }

    function stopPolling() {
        if (pollTimer) {
            clearInterval(pollTimer);
            pollTimer = null;
        }
    }

    async function doPoll() {
        pollCount++;
        try {
            const res = await fetch('/api/stitch/sync', { method: 'POST' });
            if (!res.ok) {
                console.warn('[WsStitchSync] Sync failed, status', res.status);
                if (res.status === 400 || res.status === 404) {
                    console.log('[WsStitchSync] No Stitch project linked, stopping polling');
                    stopPolling();
                }
                return;
            }
            const data = await res.json();

            // Handle clean no-project responses
            if (data.total_stitch === 0) {
                console.log('[WsStitchSync] No Stitch screens yet');
                return;
            }

            if (knownScreenCount === 0) {
                // Premier poll — establish baseline
                knownScreenCount = data.total_stitch || 0;
                console.log('[WsStitchSync] Baseline:', knownScreenCount, 'screens Stitch');
                return;
            }

            if (data.total_stitch > knownScreenCount) {
                // Nouveau(x) screen(s) détecté(s)
                const newCount = data.total_stitch - knownScreenCount;
                showToast(newCount);
                knownScreenCount = data.total_stitch;

                // Refresh la liste des imports
                if (window.WsProjectPanel) window.WsProjectPanel.refresh();
            }
        } catch(e) {
            console.error('[WsStitchSync] Poll error:', e);
        }
    }

    function showToast(count) {
        const toast = document.createElement('div');
        toast.style.cssText = 'position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#3d3d3c;color:#fff;padding:12px 24px;border-radius:12px;font-size:14px;z-index:99999;animation:slideDown 0.3s ease;';
        toast.className = 'flex items-center gap-2';
        toast.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="13.5" cy="6.5" r=".5"/><circle cx="17.5" cy="10.5" r=".5"/><circle cx="8.5" cy="7.5" r=".5"/><circle cx="6.5" cy="12.5" r=".5"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.688-1.688h1.906c3.106 0 5.632-2.526 5.632-5.632 0-4.945-4.485-8.742-10-8.742z"/></svg> <span>${count} nouveau(x) screen(s) Stitch détecté(s)</span>`;
        document.body.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transition = 'opacity 0.3s';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }

    // Public API
    window.WsStitchSync = { startPolling, stopPolling, doPoll };
    console.log('[WsStitchSync] ✅ OK');
})();