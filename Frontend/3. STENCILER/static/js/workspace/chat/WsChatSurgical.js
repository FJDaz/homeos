/* WsChatSurgical.js — sullivan chirurgical / de flanc (mission 147) */

class WsChatSurgical {
    constructor(containerId = 'ws-surgical-popover') {
        this.mount = document.getElementById(containerId);
        this.historyEl = document.getElementById('ws-surgical-history');
        this.inputEl = document.getElementById('ws-surgical-input');
        this.sendBtn = document.getElementById('btn-ws-surgical-send');
        this.closeBtn = document.getElementById('ws-surgical-close');
        this.editCodeBtn = document.getElementById('btn-ws-surgical-edit-code');
        this.header = document.getElementById('ws-surgical-header');
        
        this.currentTarget = null; // { selector, html }
        this.isDragging = false;
        this.dragOffset = { x: 0, y: 0 };
        
        this.init();
    }

    init() {
        if (this.sendBtn) this.sendBtn.onclick = () => this.sendMessage();
        if (this.inputEl) {
            this.inputEl.onkeydown = (e) => { 
                if (e.key === 'Enter' && !e.shiftKey) { 
                    e.preventDefault(); 
                    this.sendMessage(); 
                }
            };
        }
        if (this.closeBtn) this.closeBtn.onclick = () => this.hide();
        if (this.editCodeBtn) {
            this.editCodeBtn.onclick = () => {
                this.onEditCodeClick();
            };
        }

        // Click outside to close & Escape key
        window.addEventListener('mousedown', (e) => this.handleOutsideClick(e));
        window.addEventListener('keydown', (e) => this.handleKeyDown(e));
        
        this.initDragging();
    }

    handleOutsideClick(e) {
        if (this._justOpened) return;
        if (!this.mount.classList.contains('hidden')) {
            if (!this.mount.contains(e.target)) {
                this.hide();
            }
        }
    }

    handleKeyDown(e) {
        if (e.key === 'Escape' && !this.mount.classList.contains('hidden')) {
            this.hide();
        }
    }

    initDragging() {
        if (!this.header || !this.mount) return;

        const onMouseDown = (e) => {
            e.preventDefault(); // Prevent text selection
            this.isDragging = true;
            this.dragOffset.x = e.clientX - this.mount.offsetLeft;
            this.dragOffset.y = e.clientY - this.mount.offsetTop;
            this.header.style.cursor = 'grabbing';
            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
        };

        const onMouseMove = (e) => {
            if (!this.isDragging) return;
            let left = e.clientX - this.dragOffset.x;
            let top = e.clientY - this.dragOffset.y;
            
            // Constrain within screen
            left = Math.max(0, Math.min(left, window.innerWidth - this.mount.offsetWidth));
            top = Math.max(0, Math.min(top, window.innerHeight - this.mount.offsetHeight));
            
            this.mount.style.left = `${left}px`;
            this.mount.style.top = `${top}px`;
            this.mount.style.right = 'auto';
            this.mount.style.bottom = 'auto';
        };

        const onMouseUp = () => {
            this.isDragging = false;
            this.header.style.cursor = 'grab';
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
        };

        this.header.addEventListener('mousedown', onMouseDown);
    }

    appendBubble(text, sender = 'user') {
        const b = document.createElement('div');
        b.className = `p-3 rounded-lg text-[12px] max-w-[90%] transition-all ${sender === 'sullivan' ? 'bg-slate-50 border border-slate-100 self-start shadow-sm' : 'bg-slate-900 text-white self-end ml-auto'}`;
        
        if (sender === 'sullivan') {
            b.innerHTML = `
                <div class="flex items-center gap-2 mb-1">
                    <div class="w-1.5 h-1.5 rounded-full bg-homeos-green"></div>
                    <span class="font-bold text-[9px] tracking-tighter">sullivan arbitrator</span>
                </div>
                <div class="leading-relaxed whitespace-pre-wrap">${text}</div>
            `;
        } else {
            b.innerText = text;
        }

        if (this.historyEl) {
            this.historyEl.appendChild(b);
            this.historyEl.scrollTop = this.historyEl.scrollHeight;
        }
        return b;
    }

    _appendTransient(text) {
        const b = this.appendBubble(text, 'sullivan');
        if (b) b.classList.add('opacity-50', 'italic');
        return b;
    }

    show(targetElement, rect) {
        console.log("[wschatsurgical] show() -> targetElement:", targetElement, "rect:", rect);
        this.currentTarget = targetElement;
        this._justOpened = true;
        setTimeout(() => { this._justOpened = false; }, 200);
        this.mount.classList.remove('hidden');
        
        // Positionner à droite du composant (si possible), en restant dans l'écran
        let top = rect ? (rect.top || 100) : 100;
        const rectRight = (rect && !isNaN(rect.right)) ? rect.right : (rect ? (rect.left || 0) + (rect.width || 300) : 0);
        let left = rect ? rectRight + 20 : 800;
        
        // Gérer le débordement à droite (popover classiquement de 320px de large)
        if (left + 350 > window.innerWidth) {
            left = rect ? rect.left - 350 : 100; // on le met à gauche de l'élément si ça déborde
        }
        
        // s'assurer que ça ne sort pas du cadre
        left = Math.max(10, Math.min(left, window.innerWidth - 340));
        top = Math.max(10, Math.min(top, window.innerHeight - 400));

        this.mount.style.top = `${top}px`;
        this.mount.style.left = `${left}px`;
        this.mount.style.bottom = 'auto';
        this.mount.style.right = 'auto';
        
        // Reset history pour nouveau diagnostic
        this.historyEl.innerHTML = '';
        this.appendBubble(`bilan de santé pour cet organe : "${targetElement.selector}"`, 'sullivan');
        this.runSurgicalDiagnostic();
    }

    hide() {
        this.mount.classList.add('hidden');
    }

    async runSurgicalDiagnostic() {
        const payload = { 
            selector: this.currentTarget.selector,
            html: this.currentTarget.html
        };
        console.log("[wschatsurgical] sending payload to /surgical-diag:", payload);
        const pending = this._appendTransient("analyse du maillage en cours...");
        try {
            const res = await fetch(`/api/projects/active/surgical-diag`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (pending) pending.remove();
            if (data.explanation) this.appendBubble(data.explanation.toLowerCase(), 'sullivan');
        } catch (e) {
            if (pending) pending.remove();
            this.appendBubble("erreur lors du diagnostic chirurgical.", 'sullivan');
        }
    }

    async sendMessage() {
        const msg = this.inputEl.value.trim();
        if (!msg) return;

        this.appendBubble(msg, 'user');
        this.inputEl.value = '';

        const pending = this._appendTransient("sullivan analyse votre demande...");
        try {
            const data = await this.callSullivanAPI({
                message: msg,
                mode: 'surgical',
                selected_element: this.currentTarget
            });
            if (pending) pending.remove();
            if (data.explanation) this.appendBubble(data.explanation, 'sullivan');
        } catch (e) {
            if (pending) pending.remove();
            this.appendBubble("erreur de communication.", 'sullivan');
        }
    }

    async callSullivanAPI(payload) {
        const res = await fetch('/api/sullivan/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error(`sullivan status ${res.status}`);
        return res.json();
    }

    onEditCodeClick() {
        console.log("wschatsurgical: open monaco editor for", this.currentTarget.selector);
        if (window.wsInspect) {
            window.wsInspect.openCodeEditor(this.currentTarget.selector);
        }
    }
}

window.WsChatSurgical = WsChatSurgical;

