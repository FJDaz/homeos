// static/js/frd/FrdChat.feature.js

export class FrdChat {
    constructor(main) {
        this.main = main;
    }

    setMode(mode) {
        this.main.state._chatMode = mode;
        const cBtn = document.getElementById('toggle-construct');
        const wiBtn = document.getElementById('toggle-wire');

        if (mode === 'construct') {
            this.main.wire.cleanup(); // Nettoyage Mission 98
            if (cBtn) { cBtn.classList.add('bg-slate-800', 'text-white'); cBtn.classList.remove('text-gray-400'); }
            if (wiBtn) { wiBtn.classList.remove('bg-slate-300', 'text-slate-900'); wiBtn.classList.add('text-gray-400'); }
            document.getElementById('chat-input').placeholder = "Instruction Sullivan (ex: 'Change la couleur en bleu')";
        } else if (mode === 'wire') {
            if (wiBtn) { wiBtn.classList.add('bg-slate-300', 'text-slate-900'); wiBtn.classList.remove('text-gray-400'); }
            if (cBtn) { cBtn.classList.remove('bg-slate-800', 'text-white'); cBtn.classList.add('text-gray-400'); }
            document.getElementById('chat-input').placeholder = "Mode WIRE — Diagnostic automatique en cours...";
            document.getElementById('wire-panel')?.classList.remove('hidden');
            this.main.wire.run(); 
        }
    }

    async send() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        if (!message) return;

        if (message === '/construct') { this.setMode('construct'); this.appendBubble("Mode CONSTRUCT activé.", 'sullivan'); input.value = ''; return; }
        if (message === '/wire') { this.setMode('wire'); this.main.wire.run(); input.value = ''; return; }

        this.appendBubble(message, 'user');
        input.value = '';

        if (this.main.state._chatMode === 'wire') {
            this.main.wire.run();
            return;
        }

        const overlay = document.getElementById('sullivan-overlay');
        overlay.style.display = 'flex';
        const pendingId = 'pending-' + Date.now();
        this.appendBubble("Sullivan analyse votre demande...", 'sullivan', pendingId);

        const btn = document.getElementById('btn-send');
        btn.disabled = true;

        try {
            const res = await (window.__NativeFetch || fetch)('/api/frd/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    mode: this.main.state._chatMode,
                    message,
                    name: document.getElementById('template-select').value,
                    html: this.main.editor.getValue(),
                    assets: this.main.state.uploadedAssets,
                    history: this.main.state._chatHistory
                })
            });

            const pendingBubble = document.getElementById(pendingId);
            if (!res.ok) {
                if (pendingBubble) pendingBubble.innerText = `⚠️ Erreur serveur (${res.status}) — Sullivan indisponible.`;
            } else {
                const data = await res.json();
                if (pendingBubble) pendingBubble.innerText = data.explanation;

                if (data.html) {
                    this.main.state._htmlHistory.push(this.main.editor.getValue());
                    if (this.main.state._htmlHistory.length > 10) this.main.state._htmlHistory.shift();
                    document.getElementById('btn-undo').classList.remove('hidden');

                    this.main.state._chatHistory.push({ role: 'user', content: message });
                    this.main.state._chatHistory.push({ role: 'assistant', content: data.explanation || '' });
                    if (this.main.state._chatHistory.length > 12) this.main.state._chatHistory = this.main.state._chatHistory.slice(-12);

                    this.main.state._zipMode = false;
                    this.main.editor.setValue(data.html);

                    const templateSelect = document.getElementById('template-select');
                    const currentName = templateSelect.value;
                    if (!templateSelect.querySelector(`option[value="${currentName}"]`) || currentName.endsWith('.zip')) {
                        const saveName = currentName.replace('.zip', '') + '_tailwind.html';
                        let opt = templateSelect.querySelector(`option[value="${saveName}"]`);
                        if (!opt) { opt = document.createElement('option'); opt.value = saveName; opt.textContent = saveName; templateSelect.appendChild(opt); }
                        templateSelect.value = saveName;
                    }
                }
            }
        } catch (e) { console.error("Chat failed", e); }
        finally {
            overlay.style.display = 'none';
            btn.disabled = false;
        }
    }

    appendBubble(text, role, id = null) {
        const history = document.getElementById('chat-history');
        const div = document.createElement('div');
        div.className = `chat-bubble ${role}-bubble`;
        if (id) div.id = id;
        div.innerText = text;
        history.appendChild(div);
        history.scrollTop = history.scrollHeight;
    }

    async triggerSilentAudit() {
        try {
            const res = await (window.__NativeFetch || fetch)('/api/frd/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    mode: 'conseil',
                    message: "Audit automatique de routine.",
                    name: document.getElementById('template-select').value,
                    html: this.main.editor.getValue()
                })
            });
            if (res.ok) {
                const data = await res.json();
                this.updateAuditPanel(data.explanation);
            }
        } catch (e) { console.error("Silent audit failed", e); }
    }

    updateAuditPanel(markdown) {
        const panel = document.getElementById('audit-content');
        const stats = document.getElementById('audit-stats');
        if (!panel) return;

        let html = markdown
            .replace(/🔴/g, '<div class="flex gap-2 my-1"><span class="flex-shrink-0">🔴</span><span>')
            .replace(/🟡/g, '<div class="flex gap-2 my-1"><span class="flex-shrink-0">🟡</span><span>')
            .replace(/🟢/g, '<div class="flex gap-2 my-1"><span class="flex-shrink-0">🟢</span><span>')
            .split('\n').map(line => line.includes('<span>') ? line + '</span></div>' : `<p>${line}</p>`).join('');

        panel.innerHTML = html;

        const reds = (markdown.match(/🔴/g) || []).length;
        const yellows = (markdown.match(/🟡/g) || []).length;
        stats.innerText = `(🔴 ${reds} · 🟡 ${yellows})`;

        if (reds > 0) document.getElementById('ux-audit-panel').open = true;
    }
}
