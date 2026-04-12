export class FrdWire {
    constructor(main) {
        this.main = main;
        this.auditData = null;
        this._monacoEditor = null;
    }

    async run() {
        document.getElementById('wire-panel')?.classList.remove('hidden');
        const content = document.getElementById('wire-content');
        if (!content) return;
        content.innerText = "Analyse sémantique par Codestral...";

        try {
            // 1. Analyse IA (Codestral)
            const res = await (window.__NativeFetch || fetch)('/api/frd/wire', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ html: this.main.editor.getValue() })
            });

            if (res.ok) {
                const data = await res.json();
                content.innerText = data.diagnostic;

                // 2. Audit de bijectivité (Backend)
                content.innerText += "\n\nAudit technique des endpoints...";
                await this.audit();

                // 3. Application UX v2 + V5 Overlay
                this.applyUXv2();
                this.showOverlayV5(data);
            } else {
                const err = await res.json();
                content.innerText = "Erreur : " + (err.error || res.statusText);
            }
        } catch (e) {
            console.error("Wire failed", e);
            content.innerText = "Erreur de connexion au serveur.";
        }
    }

    async audit() {
        const template = document.getElementById('template-select').value;
        try {
            const res = await (window.__NativeFetch || fetch)(`/api/frd/wire-audit?name=${template}`);
            if (res.ok) {
                this.auditData = await res.json();
                console.log("[Wire] Audit findings:", this.auditData);
            }
        } catch (e) { console.warn("[Wire] Audit failed", e); }
    }

    applyUXv2() {
        if (!this.auditData) return;
        
        const container = document.getElementById('workspace-container');
        container.classList.add('wire-mode-active');
        
        // Injecter les badges dans l'iframe
        this.injectBadges();
        
        // Activer les contrôles de la table bijective
        this.setupTableControl();
    }

    injectBadges() {
        const iframe = document.getElementById('preview-iframe');
        const doc = iframe?.contentDocument;
        console.log('[Wire] injectBadges — iframe:', iframe, 'doc:', doc, 'body:', doc?.body, 'findings:', this.auditData?.findings?.length);
        if (!doc) { console.warn('[Wire] injectBadges: no contentDocument'); return; }
        if (!doc.body) { console.warn('[Wire] injectBadges: no body'); return; }

        // Cleanup before re-inject
        doc.querySelectorAll('.badge-wire-v3, .wire-skeleton-overlay, .wire-v2-style').forEach(b => b.remove());

        // 1. Nappe de fond wire mode (Veil)
        let veil = doc.getElementById('wire-veil');
        if (!veil) {
            veil = doc.createElement('div');
            veil.id = 'wire-veil';
            Object.assign(veil.style, {
                position: 'fixed', inset: '0', background: 'rgba(241,245,249,0.75)',
                zIndex: '9990', pointerEvents: 'none', transition: 'opacity 0.4s ease'
            });
            doc.body.appendChild(veil);
        }

        // 2. CSS interne pour l'iframe (Skeleton & Badges)
        const style = doc.createElement('style');
        style.className = 'wire-v2-style';
        style.textContent = `
            .wire-skeleton-overlay {
                position: absolute; pointer-events: none; z-index: 9999;
                border-radius: 4px; animation: skeleton-pulse 1.5s ease-in-out infinite;
            }
            .wire-skeleton-overlay.error  { background: rgba(239, 68, 68, 0.15); border: 1.5px solid #ef4444; }
            .wire-skeleton-overlay.warning { background: rgba(251, 191, 36, 0.12); border: 1.5px solid #f59e0b; }
            @keyframes skeleton-pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }

            .badge-wire-v3 {
                position: absolute; padding: 3px 8px; border-radius: 4px;
                font-size: 12px; font-weight: bold; color: white;
                z-index: 10000; pointer-events: auto; cursor: pointer;
                font-family: sans-serif; white-space: nowrap;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            }
            .badge-wire-v3.ok { background: #22c55e; }
            .badge-wire-v3.error { background: #ef4444; }
            .badge-wire-v3.warning { background: #f59e0b; }
        `;
        doc.head.appendChild(style);

        if (!this.auditData) return;

        this.auditData.findings.forEach(finding => {
            if (!finding.selector) { console.log('[Wire] no selector for', finding.intent_id); return; }
            const el = doc.querySelector(finding.selector);
            console.log('[Wire] selector', finding.selector, '→', el);
            if (!el) return;

            const rect = el.getBoundingClientRect();
            const win = iframe.contentWindow;
            const top = rect.top + win.scrollY;
            const left = rect.left + win.scrollX;

            // Skeleton pour error/warning
            if (finding.status !== 'ok') {
                const sk = doc.createElement('div');
                sk.className = `wire-skeleton-overlay ${finding.status}`;
                sk.style.top = top + 'px';
                sk.style.left = left + 'px';
                sk.style.width = rect.width + 'px';
                sk.style.height = rect.height + 'px';
                doc.body.appendChild(sk);
            }

            // Badge
            const badge = doc.createElement('div');
            badge.className = `badge-wire-v3 ${finding.status}`;
            badge.style.top = top + 'px';
            badge.style.left = left + 'px';
            badge.title = finding.message;

            if (finding.status === 'ok') {
                badge.innerText = '✓ ' + (finding.intent_id || finding.target);
            } else {
                badge.innerText = '✖ ' + (finding.intent_id || 'Unknown');
            }

            badge.onclick = (e) => {
                e.stopPropagation();
                const rect = badge.getBoundingClientRect();
                this.openCodePopover(finding, rect);
            };

            doc.body.appendChild(badge);
        });
    }

    cleanup() {
        const container = document.getElementById('workspace-container');
        container?.classList.remove('wire-mode-active');
        
        const iframe = document.getElementById('preview-iframe');
        const doc = iframe?.contentDocument;
        if (doc) {
            doc.getElementById('wire-veil')?.remove();
            doc.querySelectorAll('.badge-wire-v3, .wire-skeleton-overlay, .wire-v2-style').forEach(b => b.remove());
        }
        
        this.closeCodePopover();
        document.getElementById('bijective-overlay')?.classList.remove('active');
    }

    setupTableControl() {
        const btn = document.getElementById('btn-wire-table');
        if (btn) {
            btn.classList.remove('hidden');
            btn.onclick = (e) => { e.stopPropagation(); this.showOverlayV5(); };
        }
        
        const close = document.getElementById('close-bijective');
        if (close) close.onclick = () => document.getElementById('bijective-overlay').classList.remove('active');
    }

    showOverlayV5(codestralData = null) {
        const overlay = document.getElementById('bijective-overlay');
        const bilanCont = document.getElementById('bijection-bilan');
        const planCont = document.getElementById('bijection-plan');
        const implementBtn = document.getElementById('btn-wire-implement-all');
        
        if (!overlay || !bilanCont || !planCont || !this.auditData) return;

        bilanCont.innerHTML = '';
        planCont.innerHTML = '';

        // 1. Remplissage BILAN & PLAN (Bijection point par point)
        this.auditData.intentions.forEach((intent, idx) => {
            const status = this.auditData.statuts[idx];
            const planText = this.auditData.plan[idx];
            const finding = this.auditData.findings[idx];

            // Item BILAN
            const bilanItem = document.createElement('div');
            bilanItem.className = 'px-6 py-4 flex items-center gap-4 hover:bg-slate-50 transition-colors cursor-pointer';
            bilanItem.innerHTML = `
                <div class="w-[26px] h-[26px] rounded-full flex items-center justify-center shrink-0 ${status === 'ok' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}">
                    <span class="text-[16px] font-wingdings-3">${status === 'ok' ? '&#252;' : '&#251;'}</span>
                </div>
                <div class="flex-1 min-width-0">
                    <div class="text-[14px] font-bold text-slate-900 truncate">${intent}</div>
                    <div class="text-[10px] text-slate-500 font-mono truncate">${finding?.target || 'no-route'}</div>
                </div>
            `;
            bilanItem.onclick = () => {
                if (status === 'error') this.openBackendWorkflow(finding);
                else alert("Endpoint opérationnel.");
            };
            bilanCont.appendChild(bilanItem);

            // Item PLAN
            const planItem = document.createElement('div');
            planItem.className = 'px-6 py-4 hover:bg-slate-50 transition-colors';
            planItem.innerHTML = `
                <div class="text-[13px] leading-relaxed ${status === 'error' ? 'text-slate-700' : 'text-slate-400 italic'}">
                    ${planText}
                </div>
            `;
            planCont.appendChild(planItem);
        });

        // 2. Gestion du bouton d'implémentation globale
        if (implementBtn) {
            implementBtn.onclick = () => {
                overlay.classList.remove('active');
                this.main.chat.setMode('construct');
                const diag = codestralData?.diagnostic || "Plan de bijection validé. Procède à l'implémentation.";
                const input = document.getElementById('chat-input');
                if (input) {
                    input.value = "Voici le plan HoméOS — implémente les correctifs de bijection :\n\n" + diag;
                    input.focus();
                    this.main.chat.send();
                }
            };
        }

        overlay.classList.add('active');
    }

    showTable() {
        // Obsolete but kept for safety if called elsewhere
        this.showOverlayV5();
    }

    openBackendWorkflow(finding) {
        const modal = document.getElementById('backend-modal');
        const arch = document.getElementById('architect-advice');
        const ouv = document.getElementById('ouvrier-mission');
        const startBtn = document.getElementById('btn-start-backend-mission');

        if (!modal || !arch || !ouv) return;

        arch.innerText = finding.advice?.architect || "Analyse indisponible.";
        ouv.innerText = finding.advice?.ouvrier || "Mission indisponible.";
        modal.classList.remove('hidden');

        startBtn.onclick = () => {
            startBtn.innerText = "MISSION LANCÉE...";
            startBtn.disabled = true;
            setTimeout(() => {
                modal.classList.add('hidden');
                startBtn.innerText = "Rédiger & Exécuter la Mission";
                startBtn.disabled = false;
                alert(`Mission lancée pour ${finding.target} ! L'ouvrier Gemini s'en occupe.`);
            }, 1500);
        };
    }

    async openCodePopover(finding, badgeRect) {
        const popover = document.getElementById('wire-code-popover');
        const mount = document.getElementById('wire-monaco-mount');
        const title = document.getElementById('wire-popover-title');
        const status = document.getElementById('wire-popover-status');
        const closeBtn = document.getElementById('wire-popover-close');

        if (!popover || !mount) { console.warn('[Wire] popover or mount not found in DOM'); return; }

        // Positionnement immédiat (avant fetch)
        const iframe = document.getElementById('preview-iframe');
        const iframeRect = iframe.getBoundingClientRect();
        let top  = iframeRect.top  + badgeRect.top;
        let left = iframeRect.left + badgeRect.left + 20;
        top  = Math.max(60, Math.min(top,  window.innerHeight - 350));
        left = Math.max(10, Math.min(left, window.innerWidth  - 440));

        popover.style.top = top + 'px';
        popover.style.left = left + 'px';

        if (title) { title.innerText = `Handler: ${finding.target}`; }
        if (status) { status.innerText = finding.status.toUpperCase(); status.className = `wire-popover-badge ${finding.status}`; }
        if (closeBtn) { closeBtn.onclick = () => this.closeCodePopover(); }

        mount.innerText = 'Chargement...';
        popover.classList.remove('hidden');

        // Fetch source + Monaco
        try {
            const res = await (window.__NativeFetch || fetch)(`/api/frd/wire-source?endpoint=${encodeURIComponent(finding.target)}`);
            const data = await res.json();
            mount.innerText = '';

            if (this._monacoEditor) { this._monacoEditor.dispose(); this._monacoEditor = null; }

            if (window.monaco) {
                this._monacoEditor = monaco.editor.create(mount, {
                    value: data.source || '# source indisponible',
                    language: 'python',
                    theme: 'vs-dark',
                    readOnly: true,
                    fontSize: 11,
                    minimap: { enabled: false },
                    scrollBeyondLastLine: false,
                    automaticLayout: true
                });
            } else {
                mount.innerText = data.source || '# source indisponible';
                mount.style.color = '#ccc';
                mount.style.padding = '8px';
                mount.style.fontFamily = 'monospace';
                mount.style.fontSize = '11px';
                mount.style.whiteSpace = 'pre';
                mount.style.overflowY = 'auto';
            }
        } catch (e) {
            console.error("[Wire] Failed to load source", e);
            mount.innerText = `# Erreur: ${e.message}`;
        }
    }

    closeCodePopover() {
        const popover = document.getElementById('wire-code-popover');
        if (this._monacoEditor) {
            this._monacoEditor.dispose();
            this._monacoEditor = null;
        }
        popover?.classList.add('hidden');
    }

    updateApplyButton(data) {
        let applyBtn = document.getElementById('wire-apply-btn');
        if (!applyBtn) {
            applyBtn = document.createElement('button');
            applyBtn.id = 'wire-apply-btn';
            applyBtn.className = 'mt-3 w-full py-2 bg-[#8cc63f] text-white text-[12px] font-bold uppercase tracking-widest rounded hover:bg-opacity-90 transition-all';
            applyBtn.innerText = '→ Implémenter le plan';
            const content = document.getElementById('wire-content');
            content.parentNode.appendChild(applyBtn);
        }
        applyBtn.onclick = () => {
            this.main.chat.setMode('construct');
            const input = document.getElementById('chat-input');
            if (input) {
                input.value = "Voici le plan WIRE — implémente le code correspondant :\n\n" + data.diagnostic;
                input.focus();
                this.main.chat.send();
            }
        };
    }
}
