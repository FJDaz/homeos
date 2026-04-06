/* WsChatBase.js — Core Sullivan Chat (Mission 147) */

class WsChatBase {
    constructor(mountId, historyId, inputId, sendBtnId) {
        this.mount = document.getElementById(mountId);
        this.historyEl = document.getElementById(historyId);
        this.inputEl = document.getElementById(inputId);
        this.sendBtn = document.getElementById(sendBtnId);
        this.onMessageSent = null; // Callback
    }

    initBase() {
        if (this.sendBtn) this.sendBtn.onclick = () => this.sendMessage();
        if (this.inputEl) {
            this.inputEl.onkeydown = (e) => { 
                if (e.key === 'Enter' && !e.shiftKey) { 
                    e.preventDefault(); 
                    this.sendMessage(); 
                }
            };
        }
    }

    appendBubble(text, sender = 'user') {
        const b = document.createElement('div');
        b.className = `p-3 rounded-lg text-[12px] max-w-[90%] transition-all ${sender === 'sullivan' ? 'bg-slate-50 border border-slate-100 self-start shadow-sm' : 'bg-slate-900 text-white self-end ml-auto'}`;
        
        if (sender === 'sullivan') {
            b.innerHTML = `
                <div class="flex items-center gap-2 mb-1">
                    <div class="w-1.5 h-1.5 rounded-full bg-homeos-green"></div>
                    <span class="font-bold text-[9px] uppercase tracking-tighter">sullivan arbitrator</span>
                </div>
                <div class="leading-relaxed whitespace-pre-wrap">${text}</div>
            `;
        } else {
            b.innerText = text;
        }

        if (!this.historyEl) { console.warn("WsChat: historyEl missing", b.textContent); return null; }
        this.historyEl.appendChild(b);
        this.historyEl.classList.remove('hidden');
        this.historyEl.scrollTop = this.historyEl.scrollHeight;

        return b;
    }

    _appendTransient(text) {
        const b = this.appendBubble(text, 'sullivan');
        if (b) b.classList.add('opacity-50', 'italic');
        return b;
    }

    _checkHistoryVisibility() {
        if (this.historyEl && !this.historyEl.children.length) {
            this.historyEl.classList.add('hidden');
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
}

window.WsChatBase = WsChatBase;
