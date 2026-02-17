// STENCILER JS - Complet avec zoom et formes améliorées

(function() {
    'use strict';
    
    console.log('Stenciler v2.0 - API Ready');
    
    // État
    let tarmacCanvas = null;
    let mockCorps = [];
    let designBundles = null;
    let isLight = true; // Mode jour par défaut
    let zoomLevel = 1;
    let colorMode = 'border'; // 'border' ou 'fill'
    let currentTSL = { h: 0, s: 70, l: 50 }; // Hue, Saturation, Lightness
    
    // API Configuration
    const API_BASE = '/api'; // Claude's endpoints
    const API = {
        genome: `${API_BASE}/genome`,
        styles: `${API_BASE}/styles`,
        components: `${API_BASE}/components/elite`
    };
    
    // App State (pour transitions)
    const appState = {
        currentView: 'stenciler', // brainstorm | style_picker | upload | stenciler
        genome: null,
        styleSelected: null,
        templateData: null,
        
        // Transitions
        onStyleClicked(styleId) {
            this.styleSelected = styleId;
            this.switchToStenciler();
        },
        
        switchToStenciler() {
            this.currentView = 'stenciler';
            // Trigger event pour le layout parent
            window.dispatchEvent(new CustomEvent('switchToStenciler', { 
                detail: { style: this.styleSelected }
            }));
        }
    };
    
    // Initialisation avec séquence sécurisée
    document.addEventListener('DOMContentLoaded', async function() {
        // Étape 1: Charger données
        await Promise.all([
            loadMocks(),
            loadDesignBundles()
        ]);
        
        // Étape 2: DOM prêt - init UI
        initThemeToggle();
        initColorMode();
        initTSL();
        initColorSwatches();
        initBorderSlider();
        initDeleteButton();
        initPreviewBandToggle();
        initAPI();
        initNavigation();
        
        // Étape 3: Attendre layout stable puis init canvas
        requestAnimationFrame(() => {
            initCanvas();
            initDragDrop();
            initZoom();
        });
        
        // Étape 4: Observer les changements de visibilité du canvas
        observeCanvasVisibility();
    });
    
    // Observer quand le canvas devient visible (après transition)
    function observeCanvasVisibility() {
        const canvasZone = document.getElementById('canvas-zone');
        if (!canvasZone) return;
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && tarmacCanvas) {
                    // Forcer re-render quand visible
                    requestAnimationFrame(() => {
                        tarmacCanvas.renderAll();
                        console.log('Canvas rendu (devenu visible)');
                    });
                }
            });
        }, { threshold: 0.1 });
        
        observer.observe(canvasZone);
    }
    
    // Preview band collapse toggle
    function initPreviewBandToggle() {
        const toggle = document.getElementById('preview-band-toggle');
        const wrapper = document.getElementById('preview-band-wrapper');
        if (!toggle || !wrapper) return;
        
        toggle.addEventListener('click', () => {
            togglePreviewBand(wrapper, toggle);
        });
    }
    
    function togglePreviewBand(wrapper, toggle) {
        wrapper.classList.toggle('collapsed');
        toggle.textContent = wrapper.classList.contains('collapsed') ? '▲' : '▼';
    }
    
    function collapsePreviewBand() {
        console.log('collapsePreviewBand called');
        const wrapper = document.getElementById('preview-band-wrapper');
        const toggle = document.getElementById('preview-band-toggle');
        console.log('wrapper:', wrapper, 'toggle:', toggle);
        if (wrapper && !wrapper.classList.contains('collapsed')) {
            wrapper.classList.add('collapsed');
            if (toggle) toggle.textContent = '▲';
            console.log('Preview band collapsed');
        } else {
            console.log('Cannot collapse: wrapper missing or already collapsed');
        }
    }
    
    // Chargement mocks
    async function loadMocks() {
        try {
            const response = await fetch('/static/4_corps_preview.json');
            const data = await response.json();
            mockCorps = data.corps;
            renderPreviews();
        } catch (e) {
            console.error('Erreur mocks:', e);
        }
    }
    
    // Chargement design bundles
    async function loadDesignBundles() {
        try {
            const response = await fetch('/static/design-bundles.json');
            const data = await response.json();
            designBundles = data.bundles;
        } catch (e) {
            console.warn('Pas de design bundles, utilisation fallback');
        }
    }
    
    // Rendu previews avec wireframes
    function renderPreviews() {
        const band = document.getElementById('preview-band');
        if (!band) return;
        
        band.innerHTML = '';
        mockCorps.forEach(corps => {
            const div = document.createElement('div');
            const corpType = corps.id.replace('n0_', '');
            div.className = `preview-card ${corpType}`;
            div.draggable = true;
            
            // Wireframe selon le type
            let wireframeHtml = '';
            switch(corpType) {
                case 'brainstorm':
                    wireframeHtml = `
                        <div class="corps-wireframe wf-brainstorm">
                            <div class="wf-step active"></div>
                            <div class="wf-step-line"></div>
                            <div class="wf-step"></div>
                            <div class="wf-step-line dim"></div>
                            <div class="wf-step dim"></div>
                        </div>`;
                    break;
                case 'backend':
                    wireframeHtml = `
                        <div class="corps-wireframe wf-backend">
                            <div class="wf-bar" style="height:40%"></div>
                            <div class="wf-bar" style="height:70%"></div>
                            <div class="wf-bar dim" style="height:55%"></div>
                            <div class="wf-bar" style="height:85%"></div>
                        </div>`;
                    break;
                case 'frontend':
                    wireframeHtml = `
                        <div class="corps-wireframe wf-frontend">
                            <div class="wf-frame"></div>
                            <div class="wf-frame accent"></div>
                            <div class="wf-frame"></div>
                        </div>`;
                    break;
                case 'deploy':
                    wireframeHtml = `
                        <div class="corps-wireframe wf-deploy">
                            <div class="wf-launch-btn"></div>
                            <div class="wf-arrow"></div>
                        </div>`;
                    break;
            }
            
            div.innerHTML = `
                ${wireframeHtml}
                <span class="name">${corps.name}</span>
                <span class="count">${corps.organes_count} organes</span>
            `;
            
            div.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('corpsId', corps.id);
                div.classList.add('dragging');
            });
            
            div.addEventListener('dragend', () => {
                div.classList.remove('dragging');
            });
            
            // 🔽 DRILL-DOWN : Double-clic pour descendre dans le Corps
            div.addEventListener('dblclick', () => {
                console.log(`[DRILL] Double-clic sur ${corps.name}`);
                if (window.DrillDownManager) {
                    window.DrillDownManager.drillToCorps(corps.id, corps.name);
                } else {
                    console.error('[DRILL] DrillDownManager non disponible');
                }
            });
            
            band.appendChild(div);
        });
        
        // Exporter globalement pour le DrillDownManager
        window.renderPreviews = renderPreviews;
    }
    
    // Canvas avec retry pour timing
    function initCanvas() {
        const canvasEl = document.getElementById('tarmac-canvas');
        const container = document.getElementById('canvas-zone');
        if (!canvasEl || !container) {
            console.warn('Canvas ou container non trouvé, retry dans 100ms...');
            setTimeout(initCanvas, 100);
            return;
        }
        
        // Attendre que le container ait des dimensions
        if (container.clientWidth === 0 || container.clientHeight === 0) {
            console.warn('Container sans dimensions, retry dans 100ms...');
            setTimeout(initCanvas, 100);
            return;
        }
        
        // Détruire l'ancienne instance si existe
        if (tarmacCanvas) {
            tarmacCanvas.dispose();
        }
        
        tarmacCanvas = new fabric.Canvas('tarmac-canvas', {
            width: container.clientWidth,
            height: container.clientHeight,
            backgroundColor: 'transparent',
            selection: true
        });
        
        // Fix Fabric.js textBaseline warning
        fabric.Text.prototype.set({
            textBaseline: 'alphabetic'
        });
        
        // Resize handler avec debounce
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                if (tarmacCanvas && container) {
                    tarmacCanvas.setWidth(container.clientWidth);
                    tarmacCanvas.setHeight(container.clientHeight);
                    tarmacCanvas.renderAll();
                }
            }, 100);
        });
        
        console.log('Canvas initialisé:', container.clientWidth, 'x', container.clientHeight);
    }
    
    // Drag & Drop avec vérification canvas
    function initDragDrop() {
        const zone = document.getElementById('canvas-zone');
        if (!zone) {
            console.warn('Canvas zone non trouvée pour DnD, retry...');
            setTimeout(initDragDrop, 100);
            return;
        }
        
        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.classList.add('drag-over');
        });
        
        zone.addEventListener('dragleave', () => {
            zone.classList.remove('drag-over');
        });
        
        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            zone.classList.remove('drag-over');
            
            // S'assurer que le canvas est prêt
            if (!tarmacCanvas) {
                console.warn('Canvas non prêt, tentative de réinitialisation...');
                initCanvas();
                if (!tarmacCanvas) return;
            }
            
            const corpsId = e.dataTransfer.getData('corpsId');
            console.log('DROP event, corpsId:', corpsId);
            const rect = zone.getBoundingClientRect();
            const x = (e.clientX - rect.left) / zoomLevel;
            const y = (e.clientY - rect.top) / zoomLevel;
            
            addCorpsToCanvas(corpsId, x, y);
            collapsePreviewBand(); // Auto-collapse on drop
        });
    }
    
    // Ajouter corps avec forme complète (style simple Vercel)
    function addCorpsToCanvas(corpsId, x, y) {
        if (!tarmacCanvas) return;
        
        const corps = mockCorps.find(c => c.id === corpsId);
        if (!corps) return;
        
        const bundle = designBundles?.['vercel-like']?.corps || {
            width: 320, height: 240, padding: 20,
            organeHeight: 40, organeGap: 12
        };
        
        const group = [];
        
        // Container principal
        const container = new fabric.Rect({
            left: 0, top: 0,
            width: bundle.width,
            height: bundle.height,
            fill: isLight ? '#f0efeb' : bundle.background,
            stroke: corps.color,
            strokeWidth: 2,
            rx: bundle.borderRadius || 12
        });
        group.push(container);
        
        // Titre
        const title = new fabric.Text(corps.name, {
            left: bundle.padding,
            top: bundle.padding,
            fontSize: 16,
            fontWeight: '600',
            fill: isLight ? '#3d3d3c' : '#e5e5e5'
        });
        group.push(title);
        
        // Organes
        if (corps.organes) {
            let orgY = bundle.padding + 30;
            corps.organes.forEach((organe, i) => {
                const orgRect = new fabric.Rect({
                    left: bundle.padding,
                    top: orgY,
                    width: bundle.width - bundle.padding * 2,
                    height: bundle.organeHeight,
                    fill: isLight ? '#fafafa' : bundle.organeStyle?.background,
                    stroke: isLight ? '#e0dfdb' : bundle.organeStyle?.borderColor,
                    strokeWidth: 1,
                    rx: bundle.organeStyle?.borderRadius || 8
                });
                group.push(orgRect);
                
                const orgText = new fabric.Text(organe.name, {
                    left: bundle.padding + 12,
                    top: orgY + 12,
                    fontSize: 11,
                    fill: isLight ? '#6f6f6e' : '#888888'
                });
                group.push(orgText);
                
                orgY += bundle.organeHeight + bundle.organeGap;
            });
        }
        
        // Groupe Fabric
        const fabricGroup = new fabric.Group(group, {
            left: x - bundle.width / 2,
            top: y - 40,
            selectable: true,
            hasControls: true,
            hasBorders: true,
            cornerSize: 8,
            transparentCorners: false,
            cornerColor: corps.color
        });
        
        tarmacCanvas.add(fabricGroup);
        tarmacCanvas.setActiveObject(fabricGroup);
        tarmacCanvas.renderAll();
        
        // Cacher placeholder
        const placeholder = document.getElementById('canvas-placeholder');
        if (placeholder) placeholder.style.display = 'none';
        
        // Afficher bandeau
        showDroppedBar(corps);
    }
    
    // Zoom
    function initZoom() {
        const zoomIn = document.getElementById('zoom-in');
        const zoomOut = document.getElementById('zoom-out');
        const zoomReset = document.getElementById('zoom-reset');
        const zoomDisplay = document.getElementById('zoom-level');
        
        function updateZoom() {
            if (tarmacCanvas) {
                tarmacCanvas.setZoom(zoomLevel);
                tarmacCanvas.renderAll();
            }
            if (zoomDisplay) zoomDisplay.textContent = Math.round(zoomLevel * 100) + '%';
        }
        
        if (zoomIn) zoomIn.addEventListener('click', () => { zoomLevel = Math.min(zoomLevel * 1.2, 3); updateZoom(); });
        if (zoomOut) zoomOut.addEventListener('click', () => { zoomLevel = Math.max(zoomLevel / 1.2, 0.3); updateZoom(); });
        if (zoomReset) zoomReset.addEventListener('click', () => { zoomLevel = 1; updateZoom(); });
        
        // Zoom molette
        const canvasZone = document.getElementById('canvas-zone');
        if (canvasZone) {
            canvasZone.addEventListener('wheel', (e) => {
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    const delta = e.deltaY > 0 ? 0.9 : 1.1;
                    zoomLevel = Math.max(0.3, Math.min(3, zoomLevel * delta));
                    updateZoom();
                }
            });
        }
    }
    
    // Bandeau déposé
    function showDroppedBar(corps) {
        const bar = document.getElementById('dropped-bar');
        const title = document.getElementById('dropped-title');
        const badge = document.getElementById('dropped-badge');
        
        if (bar) {
            bar.classList.remove('hidden');
            if (title) title.textContent = corps.name;
            if (badge) badge.textContent = `${corps.organes_count || 0} organes`;
        }
    }
    
    // Theme toggle - Mode jour par défaut
    function initThemeToggle() {
        const toggle = document.getElementById('theme-toggle');
        if (!toggle) return;
        
        // Init mode jour (pas d'attribut data-theme = mode jour par défaut)
        document.body.removeAttribute('data-theme');
        toggle.textContent = 'Mode nuit';
        
        toggle.addEventListener('click', () => {
            isLight = !isLight;
            document.body.setAttribute('data-theme', isLight ? '' : 'dark');
            toggle.textContent = isLight ? 'Mode nuit' : 'Mode jour';
            if (tarmacCanvas) tarmacCanvas.renderAll();
        });
    }
    
    // Color Mode Toggle (Border vs Fill)
    function initColorMode() {
        const buttons = document.querySelectorAll('.mode-btn');
        if (!buttons.length) return;
        
        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                buttons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                colorMode = btn.dataset.mode;
                console.log('Color mode switched to:', colorMode);
            });
        });
    }
    
    // TSL Color Picker
    function initTSL() {
        const hSlider = document.getElementById('tsl-h');
        const sSlider = document.getElementById('tsl-s');
        const lSlider = document.getElementById('tsl-l');
        const hVal = document.getElementById('tsl-h-val');
        const sVal = document.getElementById('tsl-s-val');
        const lVal = document.getElementById('tsl-l-val');
        const preview = document.getElementById('tsl-preview');
        const applyBtn = document.getElementById('btn-apply-tsl');
        
        if (!hSlider || !sSlider || !lSlider) return;
        
        function updatePreview() {
            const h = parseInt(hSlider.value);
            const s = parseInt(sSlider.value);
            const l = parseInt(lSlider.value);
            
            currentTSL = { h, s, l };
            
            const color = `hsl(${h}, ${s}%, ${l}%)`;
            if (preview) preview.style.background = color;
            
            if (hVal) hVal.textContent = h + '°';
            if (sVal) sVal.textContent = s + '%';
            if (lVal) lVal.textContent = l + '%';
            
            // Update slider backgrounds
            sSlider.style.background = `linear-gradient(to right, hsl(${h},0%,${l}%), hsl(${h},100%,${l}%))`;
            lSlider.style.background = `linear-gradient(to right, hsl(${h},${s}%,0%), hsl(${h},${s}%,50%), hsl(${h},${s}%,100%))`;
        }
        
        hSlider.addEventListener('input', updatePreview);
        sSlider.addEventListener('input', updatePreview);
        lSlider.addEventListener('input', updatePreview);
        
        applyBtn?.addEventListener('click', () => {
            const color = `hsl(${currentTSL.h}, ${currentTSL.s}%, ${currentTSL.l}%)`;
            const active = tarmacCanvas?.getActiveObject();
            
            if (active?.type === 'group') {
                const rect = active.item(0);
                if (colorMode === 'border') {
                    rect.set('stroke', color);
                } else {
                    rect.set('fill', color);
                }
                tarmacCanvas.renderAll();
            }
        });
        
        // Init
        updatePreview();
    }
    
    // Color swatches - applique selon le mode (border ou fill)
    function initColorSwatches() {
        document.querySelectorAll('.color-swatch').forEach(swatch => {
            swatch.addEventListener('click', function() {
                document.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('selected'));
                this.classList.add('selected');
                
                const active = tarmacCanvas?.getActiveObject();
                if (active?.type === 'group') {
                    const rect = active.item(0);
                    // Utiliser getComputedStyle pour récupérer la couleur calculée
                    const computedStyle = getComputedStyle(this);
                    const color = computedStyle.backgroundColor;
                    
                    if (colorMode === 'border') {
                        rect.set('stroke', color);
                    } else {
                        rect.set('fill', color);
                    }
                    tarmacCanvas.renderAll();
                }
            });
        });
    }
    
    // API Integration - Endpoints Claude
    function initAPI() {
        const statusEl = document.getElementById('api-status');
        const btnGenome = document.getElementById('btn-fetch-genome');
        const btnStyles = document.getElementById('btn-fetch-styles');
        
        // Check API status
        checkAPIStatus();
        
        // Fetch Genome
        btnGenome?.addEventListener('click', async () => {
            try {
                updateAPIStatus('loading');
                const response = await fetch(API.genome);
                if (!response.ok) throw new Error('HTTP ' + response.status);
                const genome = await response.json();
                appState.genome = genome;
                console.log('Genome loaded:', genome);
                loadGenomeIntoStenciler(genome);
                updateAPIStatus('online');
            } catch (e) {
                console.error('Failed to fetch genome:', e);
                updateAPIStatus('offline');
                // Fallback: use mocks
                loadGenomeIntoStenciler({ n0_phases: mockCorps });
            }
        });
        
        // Fetch Styles
        btnStyles?.addEventListener('click', async () => {
            try {
                updateAPIStatus('loading');
                const response = await fetch(API.styles);
                if (!response.ok) throw new Error('HTTP ' + response.status);
                const styles = await response.json();
                console.log('Styles loaded:', styles);
                updateAPIStatus('online');
            } catch (e) {
                console.error('Failed to fetch styles:', e);
                updateAPIStatus('offline');
            }
        });
    }
    
    function checkAPIStatus() {
        // Ping API
        fetch(API.genome, { method: 'HEAD' })
            .then(() => updateAPIStatus('online'))
            .catch(() => updateAPIStatus('offline'));
    }
    
    function updateAPIStatus(status) {
        const statusEl = document.getElementById('api-status');
        if (!statusEl) return;
        
        const dot = statusEl.querySelector('.status-dot');
        const text = statusEl.querySelector('.status-text');
        
        if (status === 'online') {
            dot?.classList.add('online');
            dot?.classList.remove('offline');
            if (text) text.textContent = 'Connecté';
        } else if (status === 'offline') {
            dot?.classList.remove('online');
            dot?.classList.add('offline');
            if (text) text.textContent = 'Hors ligne';
        } else if (status === 'loading') {
            if (text) text.textContent = 'Chargement...';
        }
    }
    
    function loadGenomeIntoStenciler(genome) {
        const corps = genome.n0_phases || genome.corps || [];
        if (corps.length) {
            mockCorps = corps;
            renderPreviews();
            console.log('Genome loaded into Stenciler:', corps.length, 'corps');
        }
    }
    
    // Border slider
    function initBorderSlider() {
        const slider = document.querySelector('.border-slider');
        const display = document.querySelector('.border-value');
        
        if (slider) {
            slider.addEventListener('input', function() {
                if (display) display.textContent = this.value + 'px';
                
                const active = tarmacCanvas?.getActiveObject();
                if (active?.type === 'group') {
                    const rect = active.item(0);
                    rect.set('strokeWidth', parseInt(this.value));
                    tarmacCanvas.renderAll();
                }
            });
        }
    }
    
    // Delete - bouton et touches clavier
    function initDeleteButton() {
        // Clic sur bouton
        document.querySelector('.btn-delete')?.addEventListener('click', deleteSelectedObject);
        
        // Touches clavier Delete / Backspace
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Delete' || e.key === 'Backspace') {
                // Vérifier qu'on n'est pas dans un input/texte editable
                const activeElement = document.activeElement;
                const isEditing = activeElement && (
                    activeElement.tagName === 'INPUT' ||
                    activeElement.tagName === 'TEXTAREA' ||
                    activeElement.contentEditable === 'true'
                );
                
                if (!isEditing) {
                    e.preventDefault();
                    deleteSelectedObject();
                }
            }
        });
    }
    
    function deleteSelectedObject() {
        const active = tarmacCanvas?.getActiveObject();
        if (active) {
            tarmacCanvas.remove(active);
            tarmacCanvas.renderAll();
            console.log('Objet supprimé');
        }
    }
    
    // Navigation - Breadcrumb et bouton retour
    function initNavigation() {
        const breadcrumb = document.getElementById('breadcrumb');
        const backBtn = document.getElementById('btn-back');
        
        if (!breadcrumb) return;
        
        // Écouter les changements de vue
        window.addEventListener('switchToStenciler', (e) => {
            updateBreadcrumb('stenciler');
        });
        
        // Bouton retour
        backBtn?.addEventListener('click', () => {
            // Dispatcher event pour le layout parent
            window.dispatchEvent(new CustomEvent('navigateBack'));
        });
        
        // Mettre à jour selon la vue initiale
        updateBreadcrumb(appState.currentView);
    }
    
    function updateBreadcrumb(view) {
        const breadcrumb = document.getElementById('breadcrumb');
        const backBtn = document.getElementById('btn-back');
        
        const crumbs = {
            brainstorm: 'Brainstorm',
            style_picker: 'Brainstorm › Style',
            upload: 'Brainstorm › Upload',
            stenciler: 'Brainstorm › Style › Stenciler'
        };
        
        if (breadcrumb) {
            breadcrumb.textContent = crumbs[view] || view;
        }
        
        // Afficher bouton retour si pas sur Brainstorm
        if (backBtn) {
            backBtn.classList.toggle('hidden', view === 'brainstorm');
        }
    }
    
    // Expose appState pour le layout parent
    window.stencilerApp = appState;
    window.updateBreadcrumb = updateBreadcrumb;
    
    // API publique pour timing/extérieur
    window.stencilerAPI = {
        // Forcer re-init canvas (après transition de vue)
        reinitCanvas: () => {
            requestAnimationFrame(() => {
                initCanvas();
            });
        },
        
        // Forcer render
        render: () => {
            if (tarmacCanvas) tarmacCanvas.renderAll();
        },
        
        // Charger genome depuis API
        loadGenome: (genomeData) => {
            appState.genome = genomeData;
            loadGenomeIntoStenciler(genomeData);
        },
        
        // Obtenir référence canvas
        getCanvas: () => tarmacCanvas,
        
        // État actuel
        getState: () => ({
            isLight,
            zoomLevel,
            colorMode,
            currentTSL,
            corpsCount: mockCorps.length
        })
    };
    
})();
