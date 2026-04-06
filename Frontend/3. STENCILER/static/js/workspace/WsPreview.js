/**
 * WsPreview.js — Fullscreen Preview & Static DOM Rendering (Mission 156)
 */
class WsPreview {
    constructor() {
        this._updatingHtml = false;
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
