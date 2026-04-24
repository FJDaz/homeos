/**
 * WsForgeMonitor — Panneau de monitoring en temps réel de la forge.
 * M266 : Trace pas-à-pas visible dans le workspace.
 */
class WsForgeMonitor {
    constructor() {
        this.activeJobId = null;
        this.pollInterval = null;
        this.overlay = null;
    }

    /** Affiche le panneau de monitoring pour un job */
    show(jobId) {
        this.activeJobId = jobId;
        this.injectOverlay();
        this.startPolling();
    }

    hide() {
        this.stopPolling();
        if (this.overlay) {
            this.overlay.classList.add('hidden');
        }
    }

    injectOverlay() {
        if (this.overlay) return;

        this.overlay = document.createElement('div');
        this.overlay.id = 'ws-forge-monitor';
        this.overlay.className = 'hidden fixed inset-0 z-[9999] bg-black/40 flex items-center justify-center font-mono text-[11px]';
        this.overlay.innerHTML = `
            <div class="bg-[#1a1a1a] text-[#e1e1e6] rounded-2xl shadow-2xl w-[640px] max-h-[80vh] flex flex-col overflow-hidden border border-[#333]">
                <!-- Header -->
                <div class="h-[40px] border-b border-[#333] flex items-center justify-between px-4 shrink-0">
                    <span class="text-[12px] font-bold tracking-[0.15em] uppercase text-[#8cc63f]">forge trace</span>
                    <div class="flex items-center gap-3">
                        <span id="forge-status" class="text-[12px] text-[#999] lowercase">running</span>
                        <button id="forge-monitor-close" class="text-[#999] hover:text-white transition-colors p-1">
                            <svg class="w-[18px] h-[18px]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                        </button>
                    </div>
                </div>

                <div id="forge-summary" class="h-[32px] border-b border-[#333] bg-[#222] flex items-center gap-4 px-4 text-[12px] text-[#999] shrink-0">
                    <span class="flex items-center gap-1.5"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg> <span id="forge-duration">—</span></span>
                    <span class="flex items-center gap-1.5"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg> <span id="forge-tokens">—</span></span>
                    <span class="flex items-center gap-1.5"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" x2="12" y1="2" y2="22"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg> <span id="forge-cost">—</span></span>
                    <span class="flex items-center gap-1.5"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14.5 2 14.5 7.5 20 7.5"/></svg> <span id="forge-template">—</span></span>
                </div>

                <!-- Steps list -->
                <div id="forge-steps" class="flex-1 overflow-y-auto p-4 space-y-2 no-scrollbar">
                    <div class="text-[#666] text-center py-8">En attente du démarrage...</div>
                </div>

                <!-- Footer -->
                <div class="h-[36px] border-t border-[#333] flex items-center justify-between px-4 shrink-0 bg-[#151515]">
                    <span id="forge-job-id" class="text-[11px] text-[#555]">job_—</span>
                    <span id="forge-polling" class="text-[11px] text-[#8cc63f]">polling 1s</span>
                </div>
            </div>
        `;

        document.body.appendChild(this.overlay);

        // Close button
        this.overlay.querySelector('#forge-monitor-close').onclick = () => this.hide();

        // Click outside to close
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) this.hide();
        });
    }

    startPolling() {
        this.stopPolling();
        this.poll();
        this.pollInterval = setInterval(() => this.poll(), 1000);
    }

    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }

    async poll() {
        if (!this.activeJobId) return;

        try {
            const res = await fetch(`/api/retro-genome/svg-job/${this.activeJobId}`);
            if (!res.ok) return;
            const job = await res.json();
            this.render(job);

            if (job.status === 'done' || job.status === 'failed') {
                this.stopPolling();
                if (job.status === 'done') {
                    // Refresh project panel
                    if (window.WsProjectPanel) window.WsProjectPanel.refresh();
                }
            }
        } catch (e) {
            console.warn('[ForgeMonitor] poll error:', e.message);
        }
    }

    render(job) {
        if (!this.overlay || this.overlay.classList.contains('hidden')) return;

        const statusEl = document.getElementById('forge-status');
        const durationEl = document.getElementById('forge-duration');
        const tokensEl = document.getElementById('forge-tokens');
        const costEl = document.getElementById('forge-cost');
        const templateEl = document.getElementById('forge-template');
        const stepsEl = document.getElementById('forge-steps');
        const jobIdEl = document.getElementById('forge-job-id');

        if (statusEl) statusEl.textContent = job.status;
        if (jobIdEl) jobIdEl.textContent = this.activeJobId;

        const summary = job.trace_summary;
        if (summary) {
            if (durationEl) durationEl.textContent = `${summary.total_duration_s}s`;
            if (tokensEl) tokensEl.textContent = summary.total_tokens ? `${summary.total_tokens} tok` : '—';
            if (costEl) costEl.textContent = summary.total_cost_usd ? `$${summary.total_cost_usd}` : '—';
            if (templateEl) templateEl.textContent = summary.template_name || '—';

            if (stepsEl && summary.steps) {
                stepsEl.innerHTML = summary.steps.map(s => {
                    const icon = s.status === 'ok' ? `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>` : 
                                 s.status === 'error' ? `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>` : 
                                 `<svg class="animate-spin" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/></svg>`;
                    const color = s.status === 'ok' ? 'text-[#8cc63f]' : s.status === 'error' ? 'text-red-400' : 'text-[#999]';
                    const detail = s.detail ? `<span class="text-[#666] ml-2">${s.detail}</span>` : '';
                    const model = s.model ? `<span class="text-[#8cc63f] ml-2">${s.model}</span>` : '';
                    const err = s.error ? `<div class="text-red-400 mt-1">${s.error}</div>` : '';
                    const meta = [s.model ? '' : '', s.duration_s ? `<span class="text-[#666]">${s.duration_s}s</span>` : ''].filter(Boolean).join(' ');
                    return `
                        <div class="flex items-center gap-2 py-1.5 px-2 rounded ${s.status === 'error' ? 'bg-red-500/5' : ''}">
                            <span class="${color}">${icon}</span>
                            <span class="text-[#e1e1e6] font-bold">${s.name}</span>
                            ${meta ? `<span class="text-[12px]">${meta}</span>` : ''}
                            ${detail}
                            ${model}
                        </div>
                        ${err}
                    `;
                }).join('');
            }
        }
    }
}

window.WsForgeMonitor = window.WsForgeMonitor || new WsForgeMonitor();
