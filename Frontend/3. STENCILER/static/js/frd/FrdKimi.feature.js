// static/js/frd/FrdKimi.feature.js

export class FrdKimi {
    constructor(main) {
        this.main = main;
    }

    async send(instruction) {
        if (this.main.state._kimiInProgress) {
            this.main.chat.appendBubble("KIMI est déjà en cours... patience.", 'sullivan');
            return;
        }
        this.main.state._kimiInProgress = true;

        const overlay = document.getElementById('sullivan-overlay');
        if (!overlay) { this.main.state._kimiInProgress = false; return; }
        const loaderText = overlay.querySelector('div:last-child');
        const oldText = loaderText ? loaderText.innerText : 'Sullivan travaille...';
        if (loaderText) loaderText.innerText = "KIMI DESIGN : INITIALISATION...";
        overlay.style.display = 'flex';

        try {
            const res = await fetch('/api/frd/kimi/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ instruction, html: this.main.editor.getValue() })
            });
            const data = await res.json();
            if (res.ok && data.job_id) {
                if (loaderText) loaderText.innerText = "KIMI TRAVAILLE (POLLING)...";
                this.poll(data.job_id, oldText);
            } else {
                this.main.chat.appendBubble("Erreur KIMI : " + (data.error || "Impossible de démarrer le job"), 'sullivan');
                overlay.style.display = 'none';
                if (loaderText) loaderText.innerText = oldText;
                this.main.state._kimiInProgress = false;
            }
        } catch (e) {
            console.error('[KIMI] fetch error:', e);
            this.main.chat.appendBubble("Erreur connexion KIMI.", 'sullivan');
            overlay.style.display = 'none';
            if (loaderText) loaderText.innerText = oldText;
            this.main.state._kimiInProgress = false;
        }
    }

    async poll(job_id, oldText) {
        const overlay = document.getElementById('sullivan-overlay');
        const loaderText = overlay.querySelector('div:last-child');

        try {
            const res = await fetch('/api/frd/kimi/result/' + job_id);
            const data = await res.json();

            if (data.status === 'done') {
                this.appendKimiBubble(data.label || "KIMI Design", data.html);
                overlay.style.display = 'none';
                if (loaderText) loaderText.innerText = oldText;
                this.main.state._kimiInProgress = false;
            } else if (data.status === 'error') {
                this.main.chat.appendBubble("Erreur KIMI : " + (data.error || "Inconnue"), 'sullivan');
                overlay.style.display = 'none';
                if (loaderText) loaderText.innerText = oldText;
                this.main.state._kimiInProgress = false;
            } else if (data.status === 'not_found') {
                this.main.chat.appendBubble("Erreur : Job KIMI introuvable.", 'sullivan');
                overlay.style.display = 'none';
                if (loaderText) loaderText.innerText = oldText;
                this.main.state._kimiInProgress = false;
            } else {
                setTimeout(() => this.poll(job_id, oldText), 5000);
            }
        } catch (e) {
            console.error('[KIMI] poll error:', e);
            setTimeout(() => this.poll(job_id, oldText), 5000);
        }
    }

    appendKimiBubble(label, html) {
        this.main.state._lastKimiHtml = html;
        const history = document.getElementById('chat-history');
        const div = document.createElement('div');
        div.className = 'chat-bubble kimi-bubble mb-4';

        const header = document.createElement('div');
        header.className = 'px-3 py-2 bg-[#0f0f1e] text-[11px] font-bold uppercase tracking-widest border-b border-[#3d3d63]';
        header.textContent = '🎨 KIMI — ' + label;

        const body = document.createElement('div');
        body.className = 'p-3';

        const btn = document.createElement('button');
        btn.className = 'w-full py-2 bg-[#0f0f1e] text-[11px] border border-[#3d3d63] rounded hover:border-[#8cc63f] hover:text-[#8cc63f] transition-all uppercase tracking-widest font-bold';
        btn.textContent = 'Appliquer';
        btn.addEventListener('click', () => this.applyResult());

        body.appendChild(btn);
        div.appendChild(header);
        div.appendChild(body);
        history.appendChild(div);
        history.scrollTop = history.scrollHeight;
    }

    applyResult() {
        if (!this.main.state._lastKimiHtml) return;
        this.main.editor.setValue(this.main.state._lastKimiHtml);
        this.main.preview.update();
        this.main.chat.appendBubble("Design KIMI appliqué.", 'user');
    }
}
