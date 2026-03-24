// static/js/frd/FrdWire.feature.js

export class FrdWire {
    constructor(main) {
        this.main = main;
    }

    async run() {
        document.getElementById('wire-panel')?.classList.remove('hidden');
        const content = document.getElementById('wire-content');
        if (!content) return;
        content.innerText = "Analyse en cours par Codestral...";

        try {
            const res = await (window.__NativeFetch || fetch)('/api/frd/wire', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ html: this.main.editor.getValue() })
            });
            if (res.ok) {
                const data = await res.json();
                content.innerText = data.diagnostic;

                // Mission 89: Add Apply Button
                let applyBtn = document.getElementById('wire-apply-btn');
                if (!applyBtn) {
                    applyBtn = document.createElement('button');
                    applyBtn.id = 'wire-apply-btn';
                    applyBtn.className = 'mt-3 w-full py-2 bg-[#8cc63f] text-white text-[10px] font-bold uppercase tracking-widest rounded hover:bg-opacity-90 transition-all';
                    applyBtn.innerText = '→ Implémenter le plan';
                    content.parentNode.appendChild(applyBtn);
                }
                applyBtn.onclick = () => {
                    this.main.chat.setMode('construct');
                    const input = document.getElementById('chat-input');
                    if (input) {
                        input.value = "Voici le plan WIRE — implémente le code correspondant :\n\n" + data.diagnostic;
                        input.focus();
                    }
                };
            } else {
                const err = await res.json();
                content.innerText = "Erreur : " + (err.error || res.statusText);
            }
        } catch (e) {
            console.error("Wire failed", e);
            content.innerText = "Erreur de connexion au serveur.";
        }
    }
}
