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
                console.log('[ws_main] mode →', mode, 'wsCanvas=', !!window.wsCanvas);
                if (window.wsCanvas) {
                    window.wsCanvas.setMode(mode);
                    console.log('[ws_main] WsCanvas.activeMode =', window.wsCanvas.activeMode);
                }
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

        // M277: Stitch toolbar button — generate mega-prompt + copy + open Stitch
        var stitchBtn = document.getElementById('ws-toolbar-stitch-btn');
        if (stitchBtn) {
            stitchBtn.addEventListener('click', async function(e) {
                e.stopPropagation();
                try {
                    var res = await fetch('/api/stitch/create-project', { method: 'POST' });
                    var data = await res.json();

                    if (res.status === 400 && data.detail && data.detail.includes('manifest')) {
                        alert(data.detail);
                        return;
                    }

                    if (!res.ok) {
                        alert('Erreur Stitch: ' + (data.detail || res.statusText));
                        return;
                    }

                    // Copy mega-prompt to clipboard
                    if (data.mega_prompt) {
                        try {
                            await navigator.clipboard.writeText(data.mega_prompt);
                        } catch(clipErr) {
                            // Fallback for older browsers
                            var ta = document.createElement('textarea');
                            ta.value = data.mega_prompt;
                            document.body.appendChild(ta);
                            ta.select();
                            document.execCommand('copy');
                            document.body.removeChild(ta);
                        }

                        var toast = document.createElement('div');
                        toast.style.cssText = 'position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#3d3d3c;color:#fff;padding:12px 24px;border-radius:12px;font-size:12px;z-index:99999;';
                        toast.textContent = 'Mega-prompt copié ! Colle-le dans le chat Stitch.';
                        document.body.appendChild(toast);
                        setTimeout(function() { toast.remove(); }, 3000);
                    }

                    // Open Stitch
                    window.open(data.stitch_url || 'https://stitch.withgoogle.com', '_blank');

                } catch(err) {
                    alert('Erreur Stitch: ' + err.message);
                }
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

        // M272: Manifest button in Sullivan panel
        var manifestBtn = document.getElementById('btn-ws-manifest');
        if (manifestBtn) {
            manifestBtn.addEventListener('click', function() {
                if (window.ManifestBox) window.ManifestBox.toggle();
            });
            console.log('[ws_main] manifest button wired');
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

    // wsSendMessage — transactional handshake avec les iframes (utilisé par WsWire)
    window.wsSendMessage = function(iframe, message, timeout) {
        timeout = timeout || 2000;
        return new Promise(function(resolve, reject) {
            if (!iframe || !iframe.contentWindow) return reject('Iframe non disponible');
            var transactionId = 'tx-' + Math.random().toString(36).substr(2, 9);
            var request = Object.assign({}, message, { transactionId: transactionId });
            var handler = function(e) {
                if (e.data && e.data.transactionId === transactionId && e.data.receipt) {
                    iframe.contentWindow.removeEventListener('message', handler);
                    resolve(e.data);
                }
            };
            iframe.contentWindow.addEventListener('message', handler);
            iframe.contentWindow.postMessage(request, '*');
            setTimeout(function() {
                iframe.contentWindow.removeEventListener('message', handler);
                reject('wsSendMessage timeout: ' + message.type);
            }, timeout);
        });
    };
})();
