/**
 * static/js/font_manager.js
 * Sullivan Typography Engine — Mission 109-C
 * Management & Advisory for HoméOS Fonts
 */

class FontManager {
    constructor() {
        this.fonts = [];
        this.previewText = "homéos en minuscules...";
        this.init();
    }

    updatePreviewText(text) {
        this.previewText = text || "la petite bête monte...";
        this.render();
    }

    async init() {
        console.log('[FontManager] Initializing Sullivan UI...');
        await this.loadFonts();
    }

    async loadFonts() {
        try {
            const res = await fetch('/api/sullivan/fonts');
            const data = await res.json();
            this.fonts = data.fonts || [];
            this.render();
            this.injectStyles();
        } catch (e) {
            console.error('[FontManager] Load failed:', e);
        }
    }

    async handleUpload(files) {
        if (!files.length) return;
        
        for (let file of files) {
            const formData = new FormData();
            formData.append('file', file);

            try {
                // Show temporary loading state if needed
                const res = await fetch('/api/sullivan/font-upload', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                console.log('[FontManager] Upload success:', data);
                await this.loadFonts(); // Refresh list
            } catch (e) {
                console.error('[FontManager] Upload failed:', e);
            }
        }
    }

    async deleteFont(slug) {
        if (!confirm(`Supprimer la fonte ${slug} ?`)) return;
        try {
            const res = await fetch(`/api/sullivan/fonts/${slug}`, { method: 'DELETE' });
            if (res.ok) await this.loadFonts();
        } catch (e) {
            console.error('[FontManager] Delete failed:', e);
        }
    }

    injectStyles() {
        // Inject @font-face for all managed fonts
        let styleTag = document.getElementById('sullivan-font-styles');
        if (!styleTag) {
            styleTag = document.createElement('style');
            styleTag.id = 'sullivan-font-styles';
            document.head.appendChild(styleTag);
        }

        const cssBlocks = this.fonts.map(f => f.css).filter(Boolean);
        styleTag.innerHTML = cssBlocks.join('\n\n');
    }

    getHomeosScore(font) {
        // Logic for HoméOS aesthetic compliance
        // Humanist Sans / Mixed Geometric lowercase is preferred
        const c = font.classification || {};
        let score = 70; // Base score

        if (c.vox_atypi === 'Humanist') score += 20;
        if (c.vox_atypi === 'Geometric') score += 10;
        if (c.is_variable) score += 5;
        if (c.x_height_ratio > 0.5) score += 5; // Good lowercase legibility

        return Math.min(100, score);
    }

    getPairing(font) {
        const c = font.classification || {};
        if (c.vox_atypi === 'Humanist') return 'Geometric Heading';
        if (c.vox_atypi === 'Geometric') return 'Humanist Body';
        if (c.vox_atypi === 'Serif') return 'Sans-Serif Secondary';
        return 'Sullivan Recommended';
    }

    render() {
        const container = document.getElementById('font-grid');
        if (!container) return;

        if (this.fonts.length === 0) {
            container.innerHTML = `
                <div class="col-span-full border border-dashed border-zinc-200 rounded-xl p-8 flex flex-col items-center justify-center text-zinc-300 min-h-[160px]">
                    <div class="text-[10px] uppercase font-bold tracking-widest mb-2">aucune fonte active</div>
                    <div class="text-[9px] italic opacity-50 font-serif">Sullivan attend vos fichiers .ttf...</div>
                </div>
            `;
            return;
        }

        container.innerHTML = this.fonts.map(font => {
            const score = this.getHomeosScore(font);
            const pairing = this.getPairing(font);
            const c = font.classification || {};
            
            return `
                <div class="group bg-white border border-zinc-100 rounded-xl p-5 shadow-sm hover:shadow-md hover:border-[#8cc63f]/30 transition-all flex flex-col">
                    <div class="flex items-start justify-between mb-4">
                        <div>
                            <h3 class="text-[12px] font-bold text-slate-800 lowercase">${font.font_family}</h3>
                            <p class="text-[9px] text-zinc-400 uppercase tracking-widest mt-0.5">${c.vox_atypi || 'Unknown'} — ${font.is_variable ? 'Variable' : 'Static'}</p>
                        </div>
                        <div class="flex flex-col items-end">
                            <span class="text-[10px] font-black ${score > 80 ? 'text-[#8cc63f]' : 'text-orange-400'}">${score}%</span>
                            <span class="text-[8px] text-zinc-300 uppercase font-bold tracking-tighter">HoméOS Match</span>
                        </div>
                    </div>

                    <!-- PREVIEW -->
                    <div class="py-6 border-y border-zinc-50 my-2 overflow-hidden">
                        <p style="font-family: '${font.font_family}'; font-size: 24px; line-height: 1" class="whitespace-nowrap text-slate-900 lowercase">
                            ${this.previewText}
                        </p>
                        <p style="font-family: '${font.font_family}'; font-size: 11px;" class="mt-2 text-zinc-400 font-serif italic">
                            Sullivan Specimen — ${font.font_family.toLowerCase()}
                        </p>
                    </div>

                    <div class="mt-auto pt-4 flex items-center justify-between">
                        <div class="flex flex-col">
                            <span class="text-[8px] text-zinc-300 uppercase font-black tracking-widest">PAIRING</span>
                            <span class="text-[10px] text-slate-600 font-bold lowercase">${pairing}</span>
                        </div>
                        <button onclick="window.fontManager.deleteFont('${font.slug}')" class="w-8 h-8 rounded-full border border-zinc-100 flex items-center justify-center text-zinc-300 hover:text-red-500 hover:border-red-100 transition-all">
                            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                        </button>
                    </div>

                    ${font.licensing_warning ? `
                        <div class="mt-3 p-2 bg-orange-50 rounded text-[9px] text-orange-600 border border-orange-100 leading-tight">
                            ⚠️ <strong>Licensing:</strong> ${font.licensing_warning}
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');
    }
}

// Global instance
window.addEventListener('DOMContentLoaded', () => {
    window.fontManager = new FontManager();
});
