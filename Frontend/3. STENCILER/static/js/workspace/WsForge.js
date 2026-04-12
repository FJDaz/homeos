/**
 * WsForge.js — Sullivan Forge Polling & Job Tracking (Mission 156 + M266 ForgeTrace)
 */
class WsForge {
    constructor() {}

    /**
     * Déclenche la transformation d'un import (SVG/Image/React) en Tailwind HTML.
     */
    async forgeScreen(importId, shell, overlay) {
        const btn = overlay.querySelector(`#forge-btn-${importId}`);
        const statusEl = overlay.querySelector(`#forge-status-${importId}`);
        if (btn) { btn.disabled = true; btn.textContent = 'forge en cours...'; }
        if (statusEl) statusEl.textContent = 'analyse sémantique...';

        const chat = window.wsChat;
        const say = (msg) => { if (chat) chat.appendBubble(msg, 'sullivan'); };

        say('forge démarrée — analyse sémantique en cours...');

        try {
            const res = await fetch('/api/retro-genome/generate-from-import', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ import_id: importId })
            });
            if (!res.ok) throw new Error(`${res.status}`);
            const { job_id: jobId } = await res.json();

            // M266: Ouvrir le ForgeTrace monitor
            if (window.WsForgeMonitor) {
                window.WsForgeMonitor.show(jobId);
            }

            // M267: Persister l'état de forge active
            sessionStorage.setItem('active_forge', JSON.stringify({
                job_id: jobId,
                import_id: importId
            }));

            say('génération tailwind en cours...');
            let pollCount = 0;
            const MESSAGES = ['structuration du layout...', 'composants en cours...', 'presque terminé...'];

            const poll = setInterval(async () => {
                try {
                    const jr = await fetch(`/api/retro-genome/svg-job/${jobId}`);
                    const job = await jr.json();
                    if (job.status === 'done') {
                        clearInterval(poll);
                        // M234: Update index.json with forge result
                        try {
                            await fetch(`/api/imports/${importId}`, {
                                method: 'PATCH',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ html_template: job.template_name, type: 'html', archetype_id: job.archetype || 'stitch_import' })
                            });
                            // Refresh imports list
                            if (window.fetchWorkspaceImports) await window.fetchWorkspaceImports();
                        } catch(e) { console.warn('M234: index update failed', e); }

                        overlay.remove();
                        const iframe = shell.querySelector('iframe');
                        if (iframe) {
                            // dist compilé : URL statique directe (assets relatifs résolus)
                            // sinon : frd/file (éditable Sullivan)
                            iframe.src = job.dist_url
                                ? job.dist_url
                                : `/api/frd/file?name=${encodeURIComponent(job.template_name)}&raw=1`;
                        }
                        say('✓ rendu forgé et chargé.');
                        if (statusEl) statusEl.textContent = '';

                        // M267: Nettoyer l'état de forge active
                        sessionStorage.removeItem('active_forge');

                        // M266: Bouton "discuter dans le cadrage →"
                        const btnCadrage = document.createElement('button');
                        btnCadrage.textContent = 'discuter dans le cadrage →';
                        btnCadrage.className = 'mt-2 px-4 py-2 bg-[#8cc63f] text-white text-[13px] font-bold rounded-[20px] hover:bg-[#7ab536] transition-all cursor-pointer border border-[#8cc63f]';
                        btnCadrage.onclick = () => {
                            sessionStorage.setItem('forge_context', JSON.stringify({
                                import_id: importId,
                                template_name: job.template_name,
                                name: shell.dataset.name || importId
                            }));
                            window.location.href = '/cadrage';
                        };
                        // Insérer après le statusEl ou dans le chat
                        if (statusEl && statusEl.parentNode) {
                            statusEl.parentNode.insertBefore(btnCadrage, statusEl.nextSibling);
                        }
                    } else if (job.status === 'failed') {
                        clearInterval(poll);
                        if (statusEl) statusEl.textContent = `échec : ${job.error}`;
                        if (btn) { btn.disabled = false; btn.textContent = 'réessayer'; }
                        say(`forge échouée : ${job.error}`);
                    } else {
                        pollCount++;
                        const msg = MESSAGES[Math.min(pollCount - 1, MESSAGES.length - 1)];
                        if (statusEl) statusEl.textContent = msg;
                        if (pollCount <= MESSAGES.length) say(msg);
                    }
                } catch(_) { clearInterval(poll); }
            }, 4000);

        } catch(err) {
            if (btn) { btn.disabled = false; btn.textContent = 'réessayer'; }
            if (statusEl) statusEl.textContent = `erreur : ${err.message}`;
            say(`erreur forge : ${err.message}`);
        }
    }
}

window.WsForge = WsForge;

// M267: Reprendre le polling d'une forge active au retour sur l'onglet
(function() {
    'use strict';
    const raw = sessionStorage.getItem('active_forge');
    if (!raw) return;
    try {
        const { job_id: jobId, import_id: importId } = JSON.parse(raw);
        console.log('[WsForge] M267: Resuming forge job', jobId);
        const poll = setInterval(async () => {
            try {
                const jr = await fetch(`/api/retro-genome/svg-job/${jobId}`);
                const job = await jr.json();
                if (job.status === 'done' || job.status === 'failed') {
                    clearInterval(poll);
                    sessionStorage.removeItem('active_forge');
                    if (job.status === 'done' && window.fetchWorkspaceImports) {
                        window.fetchWorkspaceImports();
                    }
                    console.log(`[WsForge] M267: Forge ${job.status}`, job.template_name || job.error);
                }
            } catch(e) { clearInterval(poll); }
        }, 5000);
    } catch(e) { console.warn('[WsForge] M267: resume failed', e); }
})();
