/**
 * ws_main.js — M255
 * Orchestrateur workspace pur.
 * Plus de logique métier, plus de template HTML — tout est dans les modules.
 *
 * Flux : charge les scripts → boot les composants → wire les handlers → READY
 * Traces console : [ws_main] ...
 */
(function() {
    'use strict';
    var t0 = performance.now();
    console.log('[ws_main] starting workspace...');

    // Guard: DOM pas prêt (très rare avec module deferred)
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        // Étape 1 : Charger les modules
        loadScript('/static/js/workspace/WsState.js', function() {
            console.log('[ws_main] WsState loaded');
        });
        loadScript('/static/js/workspace/WsBoot.js');
        loadScript('/static/js/workspace/wsDom.js');
        loadScript('/static/js/workspace/WsImportList.js');
        loadScript('/static/js/workspace/WsAssetPicker.js');

        // Étape 2 : Boot des composants (après un tick pour que les scripts soient parse)
        setTimeout(function() {
            bootComponents();
            wireToolbar();
            wireModeButtons();
            wireInputs();
            loadCurrentContext();

            var elapsed = Math.round(performance.now() - t0);
            console.log('[ws_main] ✅ WORKSPACE READY (' + elapsed + 'ms)');
        }, 50);
    }

    /**
     * Charge un script classique (non-module) de manière synchrone.
     */
    function loadScript(src, onload) {
        var s = document.createElement('script');
        s.src = src;
        s.async = false; // Ordre garanti
        if (onload) s.onload = onload;
        document.head.appendChild(s);
    }

    /**
     * Boot les composants via WsBoot ou fallback si pas chargé.
     */
    function bootComponents() {
        if (typeof WsBoot === 'function') {
            WsBoot().then(function() {
                // Après boot : charger la liste des imports
                if (window.WsImportList) window.WsImportList.refresh();
            });
        } else {
            console.warn('[ws_main] WsBoot not loaded, using fallback init');
            // Fallback minimal si WsBoot.js n'est pas chargé
            try { window.wsAudit = new WsAudit(); } catch(e) { console.error('[ws_main] WsAudit:', e); }
            try { window.wsForge = new WsForge(); } catch(e) { console.error('[ws_main] WsForge:', e); }
            try { window.wsPreview = new WsPreview(); } catch(e) { console.error('[ws_main] WsPreview:', e); }
            try {
                window.wsCanvas = new WsCanvas('ws-canvas', 'canvas-wrapper');
            } catch(e) { console.error('[ws_main] WsCanvas:', e); }
            try { window.wsWire = new WsWire(); } catch(e) { console.error('[ws_main] WsWire:', e); }
            if (window.WsImportList) window.WsImportList.refresh();
        }
    }

    /**
     * Wire les boutons de la toolbar droite.
     */
    function wireToolbar() {
        var btns = document.querySelectorAll('.ws-tool-btn');
        console.log('[ws_main] toolbar:', btns.length, 'buttons');
        btns.forEach(function(btn) {
            btn.addEventListener('click', function() {
                var mode = btn.getAttribute('data-mode');
                console.log('[ws_main] mode →', mode);
                if (window.wsCanvas) window.wsCanvas.setMode(mode);
                if (window.wsState) window.wsState.setMode(mode);

                // Mode text → toggle font drawer
                if (mode === 'text') {
                    var drawer = document.getElementById('ws-font-drawer');
                    if (drawer) drawer.classList.toggle('hidden');
                }
            });
        });

        // Image picker
        var imgBtn = document.getElementById('ws-btn-image-picker');
        if (imgBtn) {
            imgBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                if (window.WsAssetPicker) window.WsAssetPicker.toggle(e);
            });
        }
    }

    /**
     * Wire les boutons de mode du panel Sullivan.
     */
    function wireModeButtons() {
        var modeBtns = document.querySelectorAll('.ws-mode-btn');
        console.log('[ws_main] mode buttons:', modeBtns.length);
        modeBtns.forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                console.log('[ws_main] mode click:', btn.dataset.mode);
                var activeMode = btn.getAttribute('data-mode');

                // UI toggle
                modeBtns.forEach(function(b) {
                    var isActive = b === btn;
                    b.classList.toggle('active', isActive);
                    if (!isActive) {
                        b.classList.add('text-slate-400');
                        b.classList.remove('bg-white', 'shadow-sm', 'text-slate-600');
                    } else if (activeMode !== 'audit') {
                        b.classList.add('bg-white', 'text-slate-600', 'shadow-sm');
                    }
                });

                // Body classes
                document.body.classList.remove('mode-audit', 'mode-front-dev', 'mode-construct');
                if (activeMode === 'audit') document.body.classList.add('mode-audit');
                if (activeMode === 'front-dev') document.body.classList.add('mode-front-dev');
                if (activeMode === 'construct') document.body.classList.add('mode-construct');
            });
        });
    }

    /**
     * Wire les inputs (upload, etc.)
     */
    function wireInputs() {
        var uploadInput = document.getElementById('ws-direct-upload');
        if (uploadInput) {
            uploadInput.addEventListener('change', handleDirectUpload);
            console.log('[ws_main] upload input wired');
        }
    }

    /**
     * Upload direct de fichiers.
     */
    async function handleDirectUpload(event) {
        var files = event.target.files;
        if (!files || files.length === 0) return;
        console.log('[ws_main] upload:', files.length, 'file(s)');
        for (var i = 0; i < files.length; i++) {
            var file = files[i];
            try {
                var formData = new FormData();
                formData.append('file', file);
                formData.append('filename', file.name);
                var res = await fetch('/api/import/upload', { method: 'POST', body: formData });
                if (!res.ok) throw new Error('upload ' + res.status);
                console.log('[ws_main] uploaded:', file.name);
                if (window.WsImportList) window.WsImportList.refresh();
            } catch(e) {
                console.error('[ws_main] upload failed:', file.name, e);
            }
        }
        event.target.value = '';
    }

    /**
     * Charge le contexte courant depuis l'API.
     */
    async function loadCurrentContext() {
        try {
            var res = await fetch('/api/frd/current');
            var context = await res.json();
            if (context && context.id) {
                console.log('[ws_main] loading context:', context.id);
                if (window.wsCanvas) window.wsCanvas.addScreen(context);
            }
        } catch(e) {
            console.error('[ws_main] context load error:', e);
        }
    }

    // Global exposure pour les handlers inline HTML
    window.enterPreviewMode = function(shellId, mode) {
        console.log('[ws_main] enterPreviewMode:', shellId, mode);
        if (window.wsPreview) window.wsPreview.enterPreviewMode(shellId, mode);
    };
    window.exitPreviewMode = function() {
        console.log('[ws_main] exitPreviewMode');
        if (window.wsPreview) window.wsPreview.exitPreviewMode();
    };
    window.togglePanel = function(id) {
        var panel = document.getElementById(id);
        if (panel) panel.classList.toggle('hidden');
    };
})();
