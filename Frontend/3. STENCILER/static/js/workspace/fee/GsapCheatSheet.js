/* GsapCheatSheet.js — Mission 166-DEBUG: High-Fidelity & Compact GSAP Previews */

class GsapCheatSheet {
    constructor() {
        this.drawer = document.getElementById('ws-fee-effects-drawer');
        this.toggleBtn = document.getElementById('ws-btn-effects-drawer');
        this.grid = document.getElementById('ws-effects-grid');
        this.expandBtn = document.getElementById('ws-effects-btn-expand');
        this.statcherList = document.getElementById('ws-effects-stacher-list');
        this.statcherCount = document.getElementById('ws-effects-statcher-count');
        this.applyAllBtn = document.getElementById('ws-effects-apply-all');
        this.showMoreBtn = document.getElementById('ws-effects-btn-more');
        
        this.selectedEffects = new Set();
        this.isExpanded = false;
        this.isOpen = false;
        
        this.effects = [
            { id: 'stagger', title: 'Stagger', description: 'Apparition séquentielle.', prompt: 'Applique un effet Stagger GSAP (0.1s).' },
            { id: 'magnetic', title: 'Magnetic', description: 'Attraction au survol.', prompt: 'Rends cet élément magnétique.' },
            { id: 'elastic', title: 'Elastic', description: 'Rebond organique.', prompt: 'Ajoute une entrée élastique.' },
            { id: 'splittext', title: 'Splittext', description: 'Lettre par lettre.', prompt: 'Anime ce texte via SplitText.' },
            { id: 'scrub', title: 'Scrub', description: 'Scroll progressif.', prompt: 'Lie l\'animation au scroll (Scrub).' },
            { id: 'pinning', title: 'Pinning', description: 'Épinglage au scroll.', prompt: 'Épingle l\'élément pendant le scroll.' }
        ];

        this.init();
    }

    async init() {
        if (!this.drawer) return;

        this.toggleBtn.onclick = () => this.toggle();
        this.expandBtn.onclick = () => this.toggleExpand();
        this.applyAllBtn.onclick = () => this.launchSullivanMission();
        this.showMoreBtn.onclick = () => this.loadMoreEffects();

        // Inject Design Tokens (Falls back to defaults in CSS)
        await this.injectDesignTokens();

        // Initial render
        this.render();
        this.updateStatcher();
        
        window.addEventListener('ws-mode-change', (e) => {
            if (e.detail.mode === 'front-dev') {
                this.toggleBtn.classList.remove('hidden');
            } else {
                this.toggleBtn.classList.add('hidden');
                if (this.isOpen) this.toggle();
            }
        });
    }

    async injectDesignTokens() {
        try {
            const res = await fetch('/api/workspace/tokens');
            const tokens = await res.json();
            const root = document.documentElement;
            if (tokens.colors) {
                root.style.setProperty('--homeos-primary', tokens.colors.primary);
                root.style.setProperty('--homeos-text', tokens.colors.text);
                root.style.setProperty('--homeos-radius', tokens.shape?.border_radius || '0px');
            }
        } catch (e) {
            console.warn("GsapCheatSheet: Design tokens fallback active.");
        }
    }

    toggle() {
        this.isOpen = !this.isOpen;
        if (this.isOpen) {
            this.drawer.classList.remove('hidden');
            setTimeout(() => {
                this.drawer.style.height = this.isExpanded ? '100%' : '33%';
            }, 10);
            this.toggleBtn.classList.add('bg-indigo-100');
            this.fetchRecommendations();
        } else {
            this.drawer.style.height = '0';
            setTimeout(() => this.drawer.classList.add('hidden'), 500);
            this.toggleBtn.classList.remove('bg-indigo-100');
        }
    }

    toggleExpand() {
        this.isExpanded = !this.isExpanded;
        this.drawer.style.height = this.isExpanded ? '100%' : '28%';
        this.expandBtn.style.transform = this.isExpanded ? 'rotate(180deg)' : 'rotate(0deg)';
    }

    render() {
        this.grid.innerHTML = '';
        this.effects.forEach(effect => {
            const card = document.createElement('div');
            const isSelected = this.selectedEffects.has(effect.id);
            card.className = `ws-effect-card relative bg-white border border-slate-100 p-2 flex flex-col transition-all duration-300 ws-paper-shadow cursor-default group`;

            card.innerHTML = `
                <div class="flex items-center justify-between mb-1.5">
                    <span class="text-[8px] font-bold text-slate-800 uppercase tracking-tight">${effect.title}</span>
                    <button class="ws-effect-add-btn p-1 rounded-full ${isSelected ? 'bg-indigo-500 text-white' : 'bg-slate-50 text-slate-300 hover:text-indigo-500'} transition-all" data-id="${effect.id}">
                        <svg class="w-2 h-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="${isSelected ? 'M5 13l4 4L19 7' : 'M12 4v16m8-8H4'}"/></svg>
                    </button>
                </div>
                <div class="flex-1 bg-slate-50 rounded border border-slate-100 overflow-hidden flex items-center justify-center relative min-h-[50px] mb-1.5 p-1">
                    <div class="preview-container ${this.getAnimClass(effect.id)}">
                        ${this.getPreviewMarkup(effect.id)}
                    </div>
                </div>
                <p class="text-[7px] text-slate-400 leading-none italic truncate">${effect.description}</p>
            `;

            card.querySelector('.ws-effect-add-btn').onclick = (e) => {
                e.stopPropagation();
                this.toggleEffect(effect.id);
            };

            this.grid.appendChild(card);
        });
    }

    getAnimClass(id) {
        switch(id) {
            case 'stagger': return 'anim-stagger flex gap-1';
            case 'elastic': return 'anim-elastic';
            case 'magnetic': return 'anim-magnetic';
            default: return '';
        }
    }

    getPreviewMarkup(id) {
        switch(id) {
            case 'stagger': 
                return `<div class="ws-preview-item"></div><div class="ws-preview-item"></div><div class="ws-preview-item"></div>`;
            case 'magnetic':
            case 'elastic':
                return `<button class="ws-preview-btn">btn</button>`;
            case 'splittext':
                return `<span class="text-[8px] font-bold text-slate-600 uppercase">text</span>`;
            default:
                return `<div class="ws-preview-item w-12 h-8"></div>`;
        }
    }

    toggleEffect(id) {
        if (this.selectedEffects.has(id)) this.selectedEffects.delete(id);
        else this.selectedEffects.add(id);
        this.render();
        this.updateStatcher();
    }

    updateStatcher() {
        const count = this.selectedEffects.size;
        this.statcherCount.textContent = count;
        this.statcherCount.classList.toggle('hidden', count === 0);
        this.applyAllBtn.disabled = count === 0;
        
        this.statcherList.innerHTML = '';
        if (count === 0) {
            this.statcherList.innerHTML = '<span class="text-[8px] text-slate-400 italic">aucun sélectionné</span>';
        } else {
            this.selectedEffects.forEach(id => {
                const effect = this.effects.find(e => e.id === id);
                const tag = document.createElement('div');
                tag.className = 'px-2 py-0.5 bg-white border border-slate-200 text-[8px] font-bold text-slate-600 uppercase flex items-center space-x-1';
                tag.innerHTML = `<span>${effect.title}</span><button class="hover:text-red-500" data-id="${id}">×</button>`;
                tag.querySelector('button').onclick = () => this.toggleEffect(id);
                this.statcherList.appendChild(tag);
            });
        }
    }

    async fetchRecommendations() {
        console.log("GsapCheatSheet: Sullivan layout scan...");
        this.showMoreBtn.classList.remove('hidden');
    }

    loadMoreEffects() {
        console.log("GsapCheatSheet: Loading more...");
    }

    launchSullivanMission() {
        if (this.selectedEffects.size === 0) return;
        const prompts = Array.from(this.selectedEffects).map(id => this.effects.find(e => e.id === id).prompt);
        const finalPrompt = `Mission GSAP : Applique ces effets :\n- ${prompts.join('\n- ')}`;
        if (window.wsChat) {
            window.wsChat.inputEl.value = finalPrompt;
            this.toggle();
            window.wsChat.inputEl.focus();
        }
    }
}

window.GsapCheatSheet = GsapCheatSheet;
