/**
 * WsFEE - Orchestrateur du FEE Lab (Front-End Engineering)
 * Gère l'étalonnage GSAP et l'interaction avec Sullivan FEE.
 */
class WsFEE {
    constructor(wsBackend) {
        this.ws = wsBackend;
        this.isOpen = false;
        this.activeScreen = null;
        
        // Configuration Sullivan
        this.feeHistory = [];
        this.isGenerating = false;

        this.els = {
            overlay: document.getElementById('fee-lab-overlay'),
            btnClose: document.getElementById('btn-close-fee'),
            btnOpen: document.getElementById('btn-fee-lab'),
            previewIframe: document.getElementById('fee-preview-iframe'),
            triggersList: document.getElementById('fee-triggers-list'),
            presetsStrip: document.getElementById('fee-presets-strip'),
            chatHistory: document.getElementById('chat-fee-history'),
            chatInput: document.getElementById('input-fee'),
            activeScreenLabel: document.getElementById('fee-active-screen')
        };

        this.init();
    }

    init() {
        if (!this.els.btnOpen) return;

        this.els.btnOpen.addEventListener('click', () => this.open());
        this.els.btnClose.addEventListener('click', () => this.close());
        
        this.els.chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendToSullivan();
            }
        });

        // Charger les presets
        this.loadPresets();
    }

    async open() {
        const projectId = this.ws.activeProject;
        // On récupère l'écran actif depuis WsBackend ou on prend l'import sélectionné
        this.activeScreen = this.ws.currentFile || 'landing.html';
        
        if (!projectId) {
            alert("veuillez sélectionner un projet d'abord");
            return;
        }

        this.els.activeScreenLabel.innerText = `screen: ${this.activeScreen}`;
        this.els.overlay.classList.remove('hidden');
        this.isOpen = true;

        // Charger la preview
        const previewUrl = `/api/bkd/fee/preview?project_id=${projectId}&path=${this.activeScreen}`;
        this.els.previewIframe.src = previewUrl;

        // Scanner les triggers une fois l'iframe chargée
        this.els.previewIframe.onload = () => this.scanTriggers();
    }

    close() {
        this.els.overlay.classList.add('hidden');
        this.isOpen = false;
        this.els.previewIframe.src = 'about:blank';
    }

    scanTriggers() {
        try {
            const iframe = this.els.previewIframe;
            const doc = iframe.contentDocument || iframe.contentWindow.document;
            const elements = doc.querySelectorAll('[data-af-id]');
            
            this.els.triggersList.innerHTML = '';
            
            if (elements.length === 0) {
                this.els.triggersList.innerHTML = '<div class="text-[10px] text-homeos-muted italic">aucun [data-af-id] trouvé</div>';
                return;
            }

            elements.forEach(el => {
                const id = el.getAttribute('data-af-id');
                const tag = el.tagName.toLowerCase();
                const btn = document.createElement('button');
                btn.className = "w-full text-left p-2 text-[11px] border border-homeos-border bg-homeos-panel/20 hover:border-homeos-green hover:bg-homeos-green/5 transition-all flex items-center justify-between group";
                btn.innerHTML = `
                    <span class="font-mono text-homeos-muted group-hover:text-homeos-text">${id}</span>
                    <span class="text-[9px] opacity-30">${tag}</span>
                `;
                btn.onclick = () => this.selectTrigger(id);
                this.els.triggersList.appendChild(btn);
            });
        } catch (e) {
            console.error("Erreur scan triggers:", e);
        }
    }

    selectTrigger(id) {
        this.els.chatInput.value = `anime l'élément [data-af-id="${id}"] pour qu'il... `;
        this.els.chatInput.focus();
    }

    async loadPresets() {
        try {
            const res = await fetch('/api/bkd/fee/presets');
            const data = await res.json();
            
            this.els.presetsStrip.innerHTML = '';
            data.presets.forEach(preset => {
                const btn = document.createElement('button');
                btn.className = "shrink-0 px-4 py-2 border border-homeos-border text-[10px] font-medium hover:border-homeos-green bg-white shadow-sm transition-all";
                btn.innerText = preset.name.toLowerCase();
                btn.onclick = () => this.applyPreset(preset);
                this.els.presetsStrip.appendChild(btn);
            });
        } catch (e) {
            console.error("Erreur presets:", e);
        }
    }

    applyPreset(preset) {
        this.addChatMessage('user', `applique le preset : ${preset.name.toLowerCase()}`);
        this.sendToSullivan(preset.prompt);
    }

    addChatMessage(role, text) {
        const div = document.createElement('div');
        div.className = `p-3 ${role === 'user' ? 'bg-homeos-panel/30 ml-4' : 'bg-homeos-architect/10 mr-4'} border border-homeos-border`;
        div.innerHTML = `<div class="text-[11px] leading-relaxed text-homeos-text">${marked.parse(text)}</div>`;
        this.els.chatHistory.appendChild(div);
        this.els.chatHistory.scrollTop = this.els.chatHistory.scrollHeight;
        this.feeHistory.push({role, text});
    }

    async sendToSullivan(customMsg = null) {
        if (this.isGenerating) return;
        
        const msg = customMsg || this.els.chatInput.value.trim();
        if (!msg) return;

        if (!customMsg) {
            this.addChatMessage('user', msg);
            this.els.chatInput.value = '';
        }

        this.isGenerating = true;
        
        try {
            const res = await fetch('/api/bkd/fee/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    message: msg,
                    history: this.feeHistory,
                    project_id: this.ws.activeProject,
                    screen: this.activeScreen
                })
            });

            const data = await res.json();
            if (data.explanation) {
                this.addChatMessage('assistant', data.explanation);
                this.extractAndPreviewCode(data.explanation);
            }
        } catch (e) {
            this.addChatMessage('assistant', "erreur de communication avec sullivan fee");
        } finally {
            this.isGenerating = false;
        }
    }

    extractAndPreviewCode(text) {
        // Recherche du bloc de code JS
        const match = text.match(/```(?:javascript|js)?([\s\S]*?)```/);
        if (match && match[1]) {
            const code = match[1].trim();
            this.injectToPreview(code);
        }
    }

    injectToPreview(code) {
        // Envoi du code à l'iframe via postMessage
        // L'iframe doit avoir un listener pour injecter dynamiquement le script GSAP
        const message = {
            type: 'FEE_INJECT_GSAP',
            code: code,
            screen: this.activeScreen
        };
        this.els.previewIframe.contentWindow.postMessage(message, '*');
    }
}
