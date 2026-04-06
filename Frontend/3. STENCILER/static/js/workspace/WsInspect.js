/**
 * WsInspect.js — Mission 134-B
 * Refined Arsenal: Non-spontaneous UI, Fix Edit Code, Font Hierarchy
 */

class WsInspect {
    constructor(workspace) {
        this.workspace = workspace;
        this.isActive = false;
        this.activeMode = 'select';
        this.editor = null;
        this.selectedElement = null;
        this.currentSelector = null;
        this.currentFile = null;

        // Undo History Stack
        this.historyStack = [];
        this.maxHistory = 30;

        // UI Containers
        this.popover = document.getElementById('ws-popover-container');
        this.colorPopover = document.getElementById('ws-color-container');
        this.typoPopover = document.getElementById('ws-typo-container');
        this.effectsPopover = document.getElementById('ws-effects-container');
        
        // Design Tokens Store (Mission 159)
        this.designTokens = null;
        
        // Controls
        this.saveBtn = document.getElementById('ws-popover-save');
        this.closeBtn = document.getElementById('ws-popover-close');
        this.tagLabel = document.getElementById('ws-popover-tag');

        this.colorClose = document.getElementById('ws-color-close');
        this.colorApply = document.getElementById('ws-color-apply');
        this.colorPreview = document.getElementById('ws-color-preview');
        this.sliderH = document.getElementById('ws-tsl-h');
        this.sliderS = document.getElementById('ws-tsl-s');
        this.sliderL = document.getElementById('ws-tsl-l');

        this.typoClose = document.getElementById('ws-typo-close');
        this.typoApply = document.getElementById('ws-typo-apply');
        this.fontSelect = document.getElementById('ws-typo-font');
        this.sizeInput = document.getElementById('ws-typo-size');
        this.weightSelect = document.getElementById('ws-typo-weight');

        this.effectsClose = document.getElementById('ws-effects-close');
        this.effectsApply = document.getElementById('ws-effects-apply');
        this.shadowSelect = document.getElementById('ws-effects-shadow');
        this.radiusSlider = document.getElementById('ws-effects-radius');
        this.borderSelect = document.getElementById('ws-effects-border');
        this.radiusVal = document.getElementById('ws-val-radius');

        this.setupListeners();
        // Local Font Access nécessite un geste utilisateur — chargé au premier clic
        if (this.fontSelect) {
            this.fontSelect.addEventListener('mousedown', () => this.loadLocalFonts(), { once: true });
        }
    }

    setMode(mode) {
        this.activeMode = mode;
        this.hide();
        this.hideColor();
        this.hideTypo();
        this.hideEffects();
        if (mode !== 'select' && mode !== 'text' && mode !== 'colors' && mode !== 'effects') this.clearSelection();
    }

    async loadLocalFonts() {
        if (!this.fontSelect) return;
        if (this.fontSelect.options.length > 3) return;

        let families = [];

        // Priorité 1 : fontes système via serveur (cross-browser, toutes nav)
        try {
            const res = await fetch('/api/sullivan/system-fonts');
            const data = await res.json();
            families = data.families || [];
        } catch (_) {}

        // Priorité 2 : Local Font Access API (Chrome uniquement, si serveur vide)
        if (families.length === 0 && 'queryLocalFonts' in window) {
            try {
                const fonts = await window.queryLocalFonts();
                families = [...new Set(fonts.map(f => f.family))].sort();
            } catch (_) {}
        }

        families.forEach(f => {
            const opt = document.createElement('option');
            opt.value = f; opt.innerText = f;
            this.fontSelect.appendChild(opt);
        });
    }

    setupListeners() {
        if (this.closeBtn) this.closeBtn.onclick = () => this.hide();
        if (this.saveBtn) this.saveBtn.onclick = () => this.saveGraft();
        
        if (this.colorClose) this.colorClose.onclick = () => this.hideColor();
        if (this.colorApply) this.colorApply.onclick = () => this.applyColor();

        if (this.typoClose) this.typoClose.onclick = () => this.hideTypo();
        if (this.typoApply) this.typoApply.onclick = () => this.applyTypo();

        if (this.effectsClose) this.effectsClose.onclick = () => this.hideEffects();
        if (this.effectsApply) this.effectsApply.onclick = () => this.applyEffects();
        if (this.radiusSlider) {
            this.radiusSlider.oninput = () => {
                if (this.radiusVal) this.radiusVal.innerText = this.radiusSlider.value + 'px';
            };
        }

        [this.sliderH, this.sliderS, this.sliderL].forEach(s => {
            if (s) s.oninput = () => this.updateColorPreview();
        });

        window.addEventListener('mousedown', (e) => this.handleOutsideClick(e));

        window.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') { 
                this.hide(); 
                this.hideColor(); 
                this.hideTypo(); 
                this.hideEffects(); 
                this.clearSelection(); 
            }
        });

        window.addEventListener('message', (e) => {
            if (e.data.type === 'inspect-click') this.show(e.data);
            if (e.data.type === 'inspect-tool-change') this.setMode(e.data.mode);
            if (e.data.type === 'inspect-undo') this.undo();
            if (e.data.type === 'inspect-ready-to-place-image') this.placeImageAt(e.data.x, e.data.y, e.data.src);
        });
    }

    handleOutsideClick(e) {
        // Liste des popovers à surveiller
        const containers = [this.popover, this.colorPopover, this.typoPopover, this.effectsPopover];
        
        containers.forEach(container => {
            if (container && !container.classList.contains('hidden')) {
                // On vérifie si le clic est en dehors du popover intérieur (toujours le premier enfant)
                const inner = container.querySelector('.glass-card') || container.children[0];
                if (inner && !inner.contains(e.target)) {
                    // Fermer le popover correspondant
                    if (container === this.popover) this.hide();
                    if (container === this.colorPopover) this.hideColor();
                    if (container === this.typoPopover) this.hideTypo();
                    if (container === this.effectsPopover) this.hideEffects();
                }
            }
        });
    }

    async injectTracker(iframe) {
        iframe.onload = async () => {
            try {
                // Fetch le code statique depuis le Host pour éviter les bugs CORS (srcdoc)
                const res = await fetch('/static/js/workspace/tracker/ws_iframe_core.js');
                const trackerContent = await res.text();
                
                const scriptEl = iframe.contentDocument.createElement('script');
                scriptEl.textContent = trackerContent;
                iframe.contentDocument.body.appendChild(scriptEl);
            } catch (err) { console.error("WsInspect: Injection failed", err); }
        };
    }
    snapshot(html) {
        this.historyStack.push(html);
        if (this.historyStack.length > this.maxHistory) this.historyStack.shift();
    }

    undo() {
        if (this.historyStack.length === 0) return;
        const prevHTML = this.historyStack.pop();
        const iframe = document.querySelector('#ws-preview-frame-container iframe');
        iframe.contentWindow.postMessage({ type: 'inspect-undo', snapshot: prevHTML }, '*');
    }

    show(data) {
        this.isActive = true; this.currentSelector = data.selector;
        const iframe = document.querySelector('#ws-preview-frame-container iframe');
        let filename = "index.html"; if (iframe && iframe.src) { const url = new URL(iframe.src, window.location.origin); filename = url.searchParams.get('file') || url.pathname.split('/').pop(); }
        this.currentFile = filename; this.tagLabel.innerText = data.organName || data.tagName;
        const iframeRect = iframe.getBoundingClientRect();
        let x = iframeRect.left + data.rect.left + data.rect.width + 15; let y = iframeRect.top + data.rect.top;
        if (x + 350 > window.innerWidth) x = iframeRect.left + data.rect.left - 350 - 15;
        this.popover.style.left = `${x}px`; this.popover.style.top = `${y}px`;
        this.popover.classList.add('show'); this.popover.classList.remove('hidden');
        if (!this.editor) this.initMonaco(data.html); else this.editor.setValue(data.html);
    }

    /**
     * Ouvre l'éditeur Monaco pour un sélecteur donné en cherchant l'élément dans la preview.
     */
    openCodeEditor(selector) {
        const iframe = document.querySelector('#ws-preview-frame-container iframe');
        if (!iframe || !iframe.contentDocument) return;
        
        const el = iframe.contentDocument.querySelector(selector);
        if (!el) { console.warn("WsInspect: element not found for code editor", selector); return; }
        
        const data = {
            selector: selector,
            rect: el.getBoundingClientRect(),
            tagName: el.tagName.toLowerCase(),
            html: el.outerHTML
        };
        this.show(data);
    }

    hide() { this.isActive = false; this.popover.classList.remove('show'); setTimeout(() => { if (!this.isActive) this.popover.classList.add('hidden'); }, 300); }

    showColor(data) {
        if (this.activeMode !== 'colors') return;
        if (this.isActive) this.hide();
        const iframe = document.querySelector('#ws-preview-frame-container iframe');
        const iframeRect = iframe.getBoundingClientRect();
        const x = iframeRect.left + data.rect.left; const y = iframeRect.top + data.rect.top + data.rect.height + 15;
        this.colorPopover.style.left = `${x}px`; this.colorPopover.style.top = `${y}px`;
        this.colorPopover.classList.add('show'); this.colorPopover.classList.remove('hidden');
        this.updateColorPreview();
    }

    hideColor() { this.colorPopover.classList.remove('show'); setTimeout(() => this.colorPopover.classList.add('hidden'), 300); }

    updateColorPreview() {
        const color = `hsl(${this.sliderH.value}, ${this.sliderS.value}%, ${this.sliderL.value}%)`;
        this.colorPreview.style.backgroundColor = color;
        const iframe = document.querySelector('#ws-preview-frame-container iframe');
        iframe.contentWindow.postMessage({ type: 'inspect-apply-color', color: color }, '*');
    }

    applyColor() { this.hideColor(); }

    showTypo(data) {
        if (this.activeMode !== 'text') return;
        const iframe = document.querySelector('#ws-preview-frame-container iframe');
        const iframeRect = iframe.getBoundingClientRect();
        const x = iframeRect.left + data.rect.left + data.rect.width + 15;
        const y = iframeRect.top + data.rect.top;
        this.typoPopover.style.left = `${x}px`; this.typoPopover.style.top = `${y}px`;
        this.typoPopover.classList.add('show'); this.typoPopover.classList.remove('hidden');
    }

    hideTypo() { this.typoPopover.classList.remove('show'); setTimeout(() => this.typoPopover.classList.add('hidden'), 300); }

    showEffects(data) {
        if (this.activeMode !== 'effects') return;
        if (this.isActive) this.hide();
        const iframe = document.querySelector('#ws-preview-frame-container iframe');
        const iframeRect = iframe.getBoundingClientRect();
        const x = iframeRect.left + data.rect.left + data.rect.width + 15;
        const y = iframeRect.top + data.rect.top;
        this.effectsPopover.style.left = `${x}px`; this.effectsPopover.style.top = `${y}px`;
        this.effectsPopover.classList.add('show'); this.effectsPopover.classList.remove('hidden');
    }

    hideEffects() { if (this.effectsPopover) this.effectsPopover.classList.remove('show'); setTimeout(() => { if (this.effectsPopover) this.effectsPopover.classList.add('hidden'); }, 300); }

    applyEffects() {
        const shadow = this.shadowSelect.value;
        const radius = this.radiusSlider.value + 'px';
        const border = this.borderSelect.value;
        const iframe = document.querySelector('#ws-preview-frame-container iframe');
        if (iframe && iframe.contentWindow) {
            iframe.contentWindow.postMessage({ type: 'inspect-apply-effects', shadow, radius, border }, '*');
        }
    }

    applyDesignTokens(tokens) {
        this.designTokens = tokens;
        console.log('💎 [M159] Design Tokens Applied:', tokens);
        
        // 1. Filtrage des polices
        if (tokens.fonts && this.fontSelect) {
            // Garder uniquement les polices autorisées
            Array.from(this.fontSelect.options).forEach(opt => {
                const isAllowed = tokens.fonts.includes(opt.value) || opt.value === 'Source Sans 3';
                opt.style.display = isAllowed ? 'block' : 'none';
                if (!isAllowed) opt.disabled = true;
            });
        }

        // 2. Inféodation de l'UI (Désactiver les outils interdits)
        if (tokens.colors && tokens.colors.allowCustomColors === false) {
            const colorBtn = document.querySelector('.ws-tool-btn[data-mode="colors"]');
            if (colorBtn) { colorBtn.style.opacity = '0.3'; colorBtn.title = '(Désactivé par le Design System)'; }
        }

        if (tokens.effects) {
            const effectsBtn = document.querySelector('.ws-tool-btn[data-mode="effects"]');
            if (!tokens.effects.allowShadows && !tokens.effects.allowBorders && !tokens.effects.allowRadius) {
                if (effectsBtn) { effectsBtn.style.opacity = '0.3'; effectsBtn.style.pointerEvents = 'none'; }
            }
            // Masquage granulaire dans le popover
            if (this.shadowSelect && !tokens.effects.allowShadows) this.shadowSelect.parentElement.style.display = 'none';
            if (this.radiusSlider && !tokens.effects.allowRadius) this.radiusSlider.parentElement.style.display = 'none';
            if (this.borderSelect && !tokens.effects.allowBorders) this.borderSelect.parentElement.style.display = 'none';
        }
    }

    async applyTypo() {
        let font = this.fontSelect.value;
        const size = this.sizeInput.value;
        const weight = this.weightSelect.value;
        const iframe = document.querySelector('#ws-preview-frame-container iframe');
        if (!iframe) return;

        const originalText = this.typoApply?.innerText;
        if (this.typoApply) { this.typoApply.innerText = '...'; this.typoApply.disabled = true; }

        // 1. Générer la webfont côté serveur
        try {
            const res = await fetch('/api/sullivan/generate-webfont', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ font_name: font })
            });
            const data = await res.json();

            // 2. Injecter @font-face directement dans iframe.contentDocument (pas via trackerScript)
            if (data.css && iframe.contentDocument) {
                let styleEl = iframe.contentDocument.getElementById('ws-injected-fonts');
                if (!styleEl) {
                    styleEl = iframe.contentDocument.createElement('style');
                    styleEl.id = 'ws-injected-fonts';
                    (iframe.contentDocument.head || iframe.contentDocument.body).appendChild(styleEl);
                }
                styleEl.textContent += data.css + '\n';
                // Utiliser le nom de famille déclaré dans le @font-face
                if (data.css) {
                    const match = data.css.match(/font-family:\s*['"]?([^'";]+)['"]?/);
                    if (match) font = match[1].trim();
                }
            }
        } catch (err) {
            console.warn('M148: webfont bridge failed, applying system font directly', err);
        } finally {
            if (this.typoApply) { this.typoApply.innerText = originalText; this.typoApply.disabled = false; }
        }

        // 3. Appliquer la typo via currentSelector (scope graft) — même pattern que saveGraft
        console.log('[applyTypo] selector:', this.currentSelector, '| font:', font, '| iframe.contentDocument:', !!iframe.contentDocument);
        if (this.currentSelector && iframe.contentDocument) {
            const target = iframe.contentDocument.querySelector(this.currentSelector);
            console.log('[applyTypo] target found:', !!target, target);
            if (target) {
                target.style.setProperty('font-family', font, 'important');
                target.style.setProperty('font-size', size + 'px', 'important');
                target.style.setProperty('font-weight', weight, 'important');
                // Override Tailwind utility classes on descendants
                let overrideEl = iframe.contentDocument.getElementById('ws-typo-override');
                if (!overrideEl) {
                    overrideEl = iframe.contentDocument.createElement('style');
                    overrideEl.id = 'ws-typo-override';
                    (iframe.contentDocument.head || iframe.contentDocument.body).appendChild(overrideEl);
                }
                const esc = this.currentSelector.replace(/"/g, '\\"');
                overrideEl.textContent = `${esc}, ${esc} * { font-family: ${font} !important; font-size: ${size}px !important; font-weight: ${weight} !important; }`;
                return;
            }
        }
        // Fallback postMessage si currentSelector absent
        iframe.contentWindow.postMessage({ type: 'inspect-apply-typo', font, size, weight }, '*');
    }

    async initMonaco(initialValue) {
        return new Promise((resolve) => {
            require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs' }});
            require(['vs/editor/editor.main'], () => {
                const container = document.getElementById('ws-popover-editor');
                this.editor = monaco.editor.create(container, {
                    value: initialValue, language: 'html', theme: 'vs-light', minimap: { enabled: false }, fontSize: 12, lineNumbers: 'off', automaticLayout: true, wordWrap: 'on', padding: { top: 10, bottom: 10 }, scrollbar: { vertical: 'hidden', horizontal: 'hidden' }
                });
                const ro = new ResizeObserver(() => this.editor.layout());
                ro.observe(container); resolve();
            });
        });
    }

    async saveGraft() {
        if (!this.isActive) return;
        const btn = this.saveBtn; const originalText = btn.innerText; btn.innerText = 'SAVING...'; btn.disabled = true;
        const newHtml = this.editor.getValue();
        const match = newHtml.match(/font-family:\\s*['"]?([^'";,]+)['"]?/);
        if (match) {
            const fontName = match[1];
            await fetch('/api/workspace/generate-webfonts', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ font_name: fontName })
            });
        }
        try {
            const resp = await fetch('/api/workspace/graft', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename: this.currentFile, selector: this.currentSelector, html_content: newHtml })
            });
            if ((await resp.json()).status === 'success') {
                const iframe = document.querySelector('#ws-preview-frame-container iframe');
                iframe.contentWindow.postMessage({ type: 'inspect-update-dom', selector: this.currentSelector, html: newHtml }, '*');
                btn.innerText = 'DONE ✓'; setTimeout(() => { btn.innerText = originalText; btn.disabled = false; }, 2000);
            } else throw new Error();
        } catch (err) { btn.innerText = 'ERROR'; setTimeout(() => { btn.innerText = originalText; btn.disabled = false; }, 3000); }
    }
    
    clearSelection() {
        const iframe = document.querySelector('#ws-preview-frame-container iframe');
        if (iframe && iframe.contentWindow) iframe.contentWindow.postMessage({ type: 'inspect-clear-selection' }, '*');
    }
}

// Global Listener
window.addEventListener('message', (e) => {
    if (e.data.type === 'inspect-snapshot') window.wsInspect?.snapshot(e.data.html);
    if (e.data.type === 'inspect-organ-selected') {
        if (window.wsInspect && e.data.selector) window.wsInspect.currentSelector = e.data.selector;
        window.wsInspect?.showColor(e.data);
        window.wsInspect?.showTypo(e.data);
        window.wsInspect?.showEffects(e.data);
    }
    if (e.data.type === 'inspect-selection-cleared') { 
        window.wsInspect?.hideColor(); 
        window.wsInspect?.hideTypo(); 
        window.wsInspect?.hideEffects();
    }
    if (e.data.type === 'inspect-request-image-file') document.getElementById('ws-internal-image-loader').click();
});

window.WsInspect = WsInspect;
