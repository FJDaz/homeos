/**
 * static/js/workspace/ws_font_manager.js
 * Sullivan Typography Engine — Workspace Adaptor (Mission 129)
 */

class WsFontManager {
    constructor() {
        this.fonts = [];
        this.previewText = "homéos en minuscules...";
        this.init();
    }

    updatePreviewText(text) {
        this.previewText = text || "homéos...";
        this.render();
    }

    async init() {
        console.log('[WsFontManager] Initializing...');
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
            console.error('[WsFontManager] Load failed:', e);
        }
    }

    async handleUpload(files) {
        if (!files.length) return;
        
        for (let file of files) {
            const formData = new FormData();
            formData.append('file', file);

            try {
                const res = await fetch('/api/sullivan/font-upload', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                console.log('[WsFontManager] Upload success:', data);
                await this.loadFonts(); 
            } catch (e) {
                console.error('[WsFontManager] Upload failed:', e);
            }
        }
    }

    async deleteFont(slug) {
        if (!confirm(`Supprimer la fonte ${slug} ?`)) return;
        try {
            const res = await fetch(`/api/sullivan/fonts/${slug}`, { method: 'DELETE' });
            if (res.ok) await this.loadFonts();
        } catch (e) {
            console.error('[WsFontManager] Delete failed:', e);
        }
    }

    injectStyles() {
        const cssContent = this.fonts.map(f => f.css).filter(Boolean).join('\n\n');
        
        // 1. Inject in main document
        let styleTag = document.getElementById('ws-sullivan-font-styles');
        if (!styleTag) {
            styleTag = document.createElement('style');
            styleTag.id = 'ws-sullivan-font-styles';
            document.head.appendChild(styleTag);
        }
        styleTag.innerHTML = cssContent;

        // 2. Inject in all iframes (Mission 144)
        const iframes = document.querySelectorAll('iframe');
        iframes.forEach(iframe => {
            try {
                const doc = iframe.contentDocument || iframe.contentWindow.document;
                if (!doc || !doc.head) return;
                
                let iframeStyle = doc.getElementById('ws-sullivan-font-styles-iframe');
                if (!iframeStyle) {
                    iframeStyle = doc.createElement('style');
                    iframeStyle.id = 'ws-sullivan-font-styles-iframe';
                    doc.head.appendChild(iframeStyle);
                }
                iframeStyle.innerHTML = cssContent;
            } catch (e) {
                // Same-origin screens are fine, others will be ignored
            }
        });
    }

    render() {
        const container = document.getElementById('ws-font-grid');
        if (!container) return;

        if (this.fonts.length === 0) {
            container.innerHTML = `
                <div class="col-span-full border border-dashed border-[#e5e5e5] p-8 flex flex-col items-center justify-center" style="color: #9a9a98;">
                    <div class="text-[12px] tracking-widest mb-2">aucune fonte active</div>
                    <div class="text-[11px] italic opacity-50">Sullivan attend vos fichiers .ttf...</div>
                </div>
            `;
            return;
        }

        container.innerHTML = this.fonts.map(font => {
            return `
                <div class="p-4 flex flex-col min-w-[200px]" style="background: #f7f6f2; border: 1px solid #e5e5e5; box-shadow: 0 4px 16px rgba(0,0,0,0.06);">
                    <div class="flex items-start justify-between mb-2">
                        <div>
                            <h3 class="text-[13px] lowercase" style="color: #3d3d3c;">${font.font_family}</h3>
                        </div>
                        <button onclick="window.wsFontManager.deleteFont('${font.slug}')" class="transition-all" style="color: #9a9a98;" onmouseover="this.style.color='#ddb0b0'" onmouseout="this.style.color='#9a9a98'">
                            <svg class="w-[14px] h-[14px]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                        </button>
                    </div>
                    <div class="py-4 my-2 overflow-hidden" style="border-top: 1px solid #e5e5e5; border-bottom: 1px solid #e5e5e5;">
                        <p style="font-family: '${font.font_family}'; font-size: 20px; line-height: 1; color: #3d3d3c;" class="whitespace-nowrap lowercase">
                            ${this.previewText}
                        </p>
                    </div>
                </div>
            `;
        }).join('');
    }
}

// Global instance 
window.wsFontManager = new WsFontManager();
