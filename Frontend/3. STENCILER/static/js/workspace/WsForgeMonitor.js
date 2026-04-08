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
                    <span class="text-[10px] font-bold tracking-[0.15em] uppercase text-[#8cc63f]">forge trace</span>
                    <div class="flex items-center gap-3">
                        <span id="forge-status" class="text-[10px] text-[#999] lowercase">running</span>
                        <button id="forge-monitor-close" class="text-[#999] hover:text-white transition-colors p-1">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                        </button>
                    </div>
                </div>

                <!-- Summary bar -->
                <div id="forge-summary" class="h-[32px] border-b border-[#333] bg-[#222] flex items-center gap-4 px-4 text-[10px] text-[#999] shrink-0">
                    <span>⏱ <span id="forge-duration">—</span></span>
                    <span>📦 <span id="forge-tokens">—</span></span>
                    <span>💰 <span id="forge-cost">—</span></span>
                    <span>📝 <span id="forge-template">—</span></span>
                </div>

                <!-- Steps list -->
                <div id="forge-steps" class="flex-1 overflow-y-auto p-4 space-y-2 no-scrollbar">
                    <div class="text-[#666] text-center py-8">En attente du démarrage...</div>
                </div>

                <!-- Footer -->
                <div class="h-[36px] border-t border-[#333] flex items-center justify-between px-4 shrink-0 bg-[#151515]">
                    <span id="forge-job-id" class="text-[9px] text-[#555]">job_—</span>
                    <span id="forge-polling" class="text-[9px] text-[#8cc63f]">polling 1s</span>
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
            const res = await fetch(`/api/svg-job/${this.activeJobId}`);
            if (!res.ok) return;
            const job = await res.json();
            this.render(job);

            if (job.status === 'done' || job.status === 'failed') {
                this.stopPolling();
                if (job.status === 'done') {
                    // Refresh import list
                    if (window.WsImportList) window.WsImportList.refresh();
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
                    const icon = s.status === 'ok' ? '✅' : s.status === 'error' ? '❌' : '⏳';
                    const color = s.status === 'ok' ? 'text-[#8cc63f]' : s.status === 'error' ? 'text-red-400' : 'text-[#999]';
                    const detail = s.detail ? `<span class="text-[#666] ml-2">${s.detail}</span>` : '';
                    const model = s.model ? `<span class="text-[#8cc63f] ml-2">${s.model}</span>` : '';
                    const err = s.error ? `<div class="text-red-400 mt-1">${s.error}</div>` : '';
                    const meta = [s.model ? '' : '', s.duration_s ? `<span class="text-[#666]">${s.duration_s}s</span>` : ''].filter(Boolean).join(' ');
                    return `
                        <div class="flex items-center gap-2 py-1.5 px-2 rounded ${s.status === 'error' ? 'bg-red-500/5' : ''}">
                            <span class="${color}">${icon}</span>
                            <span class="text-[#e1e1e6] font-bold">${s.name}</span>
                            ${meta ? `<span class="text-[10px]">${meta}</span>` : ''}
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
