/**
 * WsPreview.js — Fullscreen Preview & Static DOM Rendering (Mission 156 + M273 Zoom)
 */
class WsPreview {
    constructor() {
        this._updatingHtml = false;
        // M273: Zoom state
        this.previewScale = 1.0;
        this.previewMinScale = 0.2;
        this.previewMaxScale = 3.0;
        this._zoomListenerBound = false;
    }

    // M273: Zoom logic
    setZoom(scale) {
        this.previewScale = Math.max(this.previewMinScale, Math.min(this.previewMaxScale, scale));
        const container = document.getElementById('ws-preview-frame-container');
        const levelEl = document.getElementById('ws-preview-zoom-level');
        if (container) {
            container.style.transform = `scale(${this.previewScale})`;
            container.style.transformOrigin = 'center center';
            container.style.width = `${100 / this.previewScale}%`;
            container.style.height = `${100 / this.previewScale}%`;
        }
        if (levelEl) levelEl.textContent = `${Math.round(this.previewScale * 100)}%`;
    }

    _bindZoomControls() {
        if (this._zoomListenerBound) return;
        this._zoomListenerBound = true;

        // Buttons
        const btnIn = document.getElementById('ws-preview-zoom-in');
        const btnOut = document.getElementById('ws-preview-zoom-out');
        const btnClose = document.getElementById('ws-preview-close-btn');
        const btnDownload = document.getElementById('ws-preview-download');

        if (btnIn) btnIn.onclick = () => this.setZoom(this.previewScale + 0.25);
        if (btnOut) btnOut.onclick = () => this.setZoom(this.previewScale - 0.25);
        if (btnClose) btnClose.onclick = () => this.exitPreviewMode();

        // M273: Download
        if (btnDownload) btnDownload.onclick = () => this.downloadPreview();

        // Wheel zoom (Ctrl/Cmd + wheel)
        const scrollArea = document.getElementById('ws-preview-scroll-area');
        if (scrollArea) {
            scrollArea.addEventListener('wheel', (e) => {
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    const delta = e.deltaY > 0 ? -0.1 : 0.1;
                    this.setZoom(this.previewScale + delta);
                }
            }, { passive: false });
        }
    }

    // M273: Download current preview as HTML
    downloadPreview() {
        try {
            const iframe = document.querySelector('#ws-preview-frame-container iframe');
            const html = iframe?.contentDocument?.documentElement?.outerHTML;
            if (!html) {
                alert("Aucun contenu à télécharger.");
                return;
            }
            const blob = new Blob([html], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `preview_${Date.now()}.html`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch(e) {
            alert("Erreur téléchargement: " + e.message);
        }
    }

    /**
     * Mise à jour dynamique du HTML (Sullivan / Inspect).
     * Utilise document.write sans scripts pour éviter les boucles infinies de rechargement.
     */
    updateActiveScreenHtml(html) {
        if (this._updatingHtml) return;
        this._updatingHtml = true;
        
        // Anti-bounce guard (Monkey-patch fetch prevention)
        setTimeout(() => { this._updatingHtml = false; }, 500);
        
        const previewIframe = document.querySelector('#ws-preview-frame-container iframe');
        const activeId = window.wsCanvas?.activeScreenId;
        const canvasIframe = activeId ? document.getElementById(activeId)?.querySelector('iframe') : null;

        // --- SULLIVAN UNDO (Mission 153/156) ---
        if (window.wsInspect) {
            // Lecture prioritaire du dernier HTML hacké (sans scripts) ou du srcdoc original
            const currentHtml = previewIframe?._lastSullivanHtml
                || canvasIframe?.srcdoc
                || canvasIframe?.contentDocument?.documentElement?.outerHTML;
            
            if (currentHtml) window.wsInspect.snapshot(currentHtml);
        }

        // 1. Sync Canvas Iframe (Toujours modifiable pour le SAVE)
        if (canvasIframe) {
            canvasIframe.srcdoc = html;
        }

        // 2. Sync Preview Iframe (Rendu statique via doc.write)
        if (previewIframe) {
            // Persister l'HTML complet (avec scripts) pour les lectures futures via _getIframeHtml
            previewIframe._lastSullivanHtml = html;

            try {
                // Strip uniquement les scripts locaux/inline (pas les CDN comme Tailwind).
                // Les scripts app réinitialisent le state serveur et écrasent Sullivan.
                // Les scripts CDN (https://) sont préservés pour que Tailwind/Alpine restent actifs.
                const htmlStatic = html.replace(
                    /<script(?![^>]*src\s*=\s*["'](https?:\/\/|\/api\/))[^>]*>[\s\S]*?<\/script>/gi, ''
                );
                
                previewIframe.srcdoc = htmlStatic;

                // Re-injecter le tracker d'inspection après la mise à jour
                if (window.wsInspect) window.wsInspect.injectTracker(previewIframe);

            } catch(err) {
                console.warn("WsPreview: srcdoc update failed", err);
                previewIframe.srcdoc = html;
            }
        }
    }

    /**
     * Entre en mode aperçu (Plein écran ou Wire).
     */
    enterPreviewMode(shellId, mode = 'construct') {
        const id = shellId || window.wsCanvas?.activeScreenId;
        if (!id) {
            alert("Sélectionnez un écran pour l'aperçu.");
            return;
        }

        const overlay = document.getElementById('ws-preview-overlay');
        const shell = document.getElementById(id);
        if (!shell || !overlay) return;

        // Orchestration Z-Index (Mission 150)
        overlay.classList.remove('hidden');
        if (mode === 'wire') {
            overlay.classList.remove('z-[35]', 'bg-transparent');
            overlay.classList.add('z-[100]', 'bg-white/10', 'backdrop-blur-sm');
        } else {
            overlay.classList.remove('z-[100]', 'bg-white/10', 'backdrop-blur-sm');
            overlay.classList.add('z-[35]', 'bg-transparent');
        }

        const iframeSource = shell.querySelector('iframe');
        if (!iframeSource) return;

        const container = document.getElementById('ws-preview-frame-container');
        if (!container) return;

        container.innerHTML = '';
        const iframe = document.createElement('iframe');
        iframe.className = "w-full h-full border-none bg-white shadow-2xl rounded-xl";

        // Priorité à l'HTML prospecté par Sullivan
        if (iframeSource.srcdoc) iframe.srcdoc = iframeSource.srcdoc;
        else iframe.src = iframeSource.src;

        container.appendChild(iframe);

        // M273: Reset zoom and bind controls
        this.previewScale = 1.0;
        this.setZoom(1.0);
        this._bindZoomControls();
        
        // Mission 147 / 150 : Wire Overlay Orchestration
        if (mode === 'wire' && window.wsWire) {
            try {
                const manifest = JSON.parse(shell.dataset.manifest || '{}');
                const title = shell.querySelector('.ws-screen-title')?.textContent || 'Sans titre';
                window.wsWire.show(manifest, title);
            } catch(e) {
                console.error("WsPreview: Manifest parsing failed", e);
            }
        } else if (window.wsWire) {
            window.wsWire.hide();
        }

        // Injecter l'inspecteur
        if (window.wsInspect) {
            window.wsInspect.injectTracker(iframe);
        }

        document.body.classList.add('preview-mode');
    }

    /**
     * Quitte le mode aperçu.
     */
    exitPreviewMode() {
        document.body.classList.remove('preview-mode');
        document.getElementById('ws-preview-overlay').classList.add('hidden');
        document.getElementById('ws-preview-frame-container').innerHTML = '';
        if (window.wsWire) window.wsWire.hide();
    }
}

window.WsPreview = WsPreview;

// M273: Escape key to close preview
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && document.body.classList.contains('preview-mode')) {
        if (window.wsPreview) window.wsPreview.exitPreviewMode();
    }
});
