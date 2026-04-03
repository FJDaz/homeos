/**
 * WsForge.js — Sullivan Forge Polling & Job Tracking (Mission 156)
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

            say('génération tailwind en cours...');
            let pollCount = 0;
            const MESSAGES = ['structuration du layout...', 'composants en cours...', 'presque terminé...'];

            const poll = setInterval(async () => {
                try {
                    const jr = await fetch(`/api/retro-genome/svg-job/${jobId}`);
                    const job = await jr.json();
                    if (job.status === 'done') {
                        clearInterval(poll);
                        overlay.remove();
                        const iframe = shell.querySelector('iframe');
                        if (iframe) iframe.src = `/api/frd/file?name=${encodeURIComponent(job.template_name)}&raw=1`;
                        say('✓ rendu forgé et chargé.');
                        if (statusEl) statusEl.textContent = '';
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
