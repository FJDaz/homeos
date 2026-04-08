/**
 * WsBoot — M251
 * Séquence d'initialisation ordonnée, try/catch par composant.
 * Remplace le bloc async DOMContentLoaded de ws_main.js.
 *
 * Usage : WsBoot().then(() => { /* workspace ready * / })
 * Traces console : [WsBoot] ...
 */
function WsBoot() {
    'use strict';

    var t0 = performance.now();
    console.log('[WsBoot] === START ===');

    // Helper : boot un composant en isolant les erreurs
    function bootSafe(name, fn) {
        var t1 = performance.now();
        try {
            fn();
            console.log('[WsBoot] ✅ ' + name + ' OK (' + Math.round(performance.now() - t1) + 'ms)');
            return true;
        } catch(e) {
            console.error('[WsBoot] ❌ ' + name + ' CRASH:', e.message);
            return false;
        }
    }

    // Helper : boot async avec isolation
    function bootSafeAsync(name, fn) {
        var t1 = performance.now();
        return fn().then(function() {
            console.log('[WsBoot] ✅ ' + name + ' OK (' + Math.round(performance.now() - t1) + 'ms)');
            return true;
        }).catch(function(e) {
            console.error('[WsBoot] ❌ ' + name + ' CRASH:', e.message);
            return false;
        });
    }

    return Promise.resolve()
        .then(function() {
            // Étape 0 : État global (doit être prêt en premier)
            return bootSafe('WsState', function() {
                if (!window.wsState) {
                    console.warn('[WsBoot] WsState not loaded, including script...');
                }
            });
        })
        .then(function() {
            // Étape 1 : Composments de base (pas de dépendances DOM)
            bootSafe('WsAudit', function() { window.wsAudit = new WsAudit(); });
            bootSafe('WsForge', function() { window.wsForge = new WsForge(); });
            bootSafe('WsPreview', function() { window.wsPreview = new WsPreview(); });
        })
        .then(function() {
            // Étape 2 : Canvas (nécessite SVG dans le DOM)
            bootSafe('WsCanvas', function() {
                var canvas = new WsCanvas('ws-canvas', 'canvas-wrapper');
                window.wsCanvas = canvas;
            });
        })
        .then(function() {
            // Étape 3 : Chat Sullivan (nécessite mount points)
            bootSafe('WsChatMain', function() {
                var chat = new WsChatMain('ws-chat-mount');
                window.wsChat = chat;
            });
            bootSafe('WsChatSurgical', function() {
                window.wsSurgicalChat = new WsChatSurgical('ws-surgical-popover');
            });
        })
        .then(function() {
            // Étape 4 : Wire + FEE Studio
            bootSafe('WsWire', function() { window.wsWire = new WsWire(); });
            bootSafe('WsFEEStudio', function() {
                window.wsFEEStudio = new WsFEEStudio(null);
            });
        })
        .then(function() {
            // Étape 5 : Inspecteur
            bootSafe('WsInspect', function() {
                window.wsInspect = new WsInspect(window);
            });
        })
        .then(function() {
            // Étape 6 : Design Tokens (async)
            return bootSafeAsync('DesignTokens', function() {
                return fetch('/api/workspace/tokens')
                    .then(function(r) { return r.json(); })
                    .then(function(tokens) {
                        if (window.wsInspect) window.wsInspect.applyDesignTokens(tokens);
                    });
            });
        })
        .then(function() {
            var elapsed = Math.round(performance.now() - t0);
            console.log('[WsBoot] === WORKSPACE READY (' + elapsed + 'ms) ===');
        })
        .catch(function(e) {
            console.error('[WsBoot] UNEXPECTED CRASH:', e);
        });
}
