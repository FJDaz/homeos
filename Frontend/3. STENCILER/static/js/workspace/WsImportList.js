/**
 * WsImportList — M253
 * Gestion de la liste des imports (screen list) — extraction de ws_main.js.
 *
 * Usage : window.WsImportList.refresh()
 * Traces console : [WsImportList] ...
 */
(function() {
    'use strict';
    console.log('[WsImportList] init');

    /**
     * Récupère la liste des imports et rend le HTML.
     */
    async function refresh() {
        console.log('[WsImportList] fetching...');
        try {
            const res = await fetch('/api/retro-genome/imports');
            if (!res.ok) {
                console.warn('[WsImportList] fetch failed, status', res.status);
                return;
            }
            const data = await res.json();
            const imports = data.imports || [];
            console.log('[WsImportList]', imports.length, 'imports');
            render(imports);
        } catch(e) {
            console.error('[WsImportList] fetch error:', e);
        }
    }

    /**
     * Rend la liste des imports dans le conteneur.
     */
    function render(imports) {
        const container = document.getElementById('ws-import-list');
        if (!container) {
            console.warn('[WsImportList] #ws-import-list not found');
            return;
        }
        container.innerHTML = '';

        if (imports.length === 0) {
            container.innerHTML = '<div class="p-4 text-[10px] text-slate-400 italic">aucun import</div>';
            return;
        }

        imports.forEach(function(item) {
            const el = document.createElement('div');
            el.className = 'group flex items-center justify-between p-2 rounded-lg border border-slate-100 bg-white hover:border-homeos-green/30 transition-all cursor-pointer';

            // Bouton [S] uniquement pour les imports Stitch
            const isStitch = item.archetype_id === 'stitch_import' ||
                             (item.archetype_label && item.archetype_label.toLowerCase().includes('stitch'));

            el.innerHTML =
                '<span class="text-[10px] font-medium text-slate-600 truncate flex-1">' + item.name + '</span>' +
                '<div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">' +
                    '<button class="p-1.5 hover:bg-slate-50 text-slate-400 hover:text-homeos-green rounded transition-all" title="Aperçu">' +
                        '<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M24 12s-4.5-8-12-8S0 12 0 12s4.5 8 12 8 12-8 12-8z"/></svg>' +
                    '</button>' +
                    (isStitch ?
                        '<button class="btn-s-open p-1.5 hover:bg-slate-50 text-slate-400 hover:text-indigo-500 rounded transition-all" title="Stitch">' +
                            '<span class="text-[9px] font-black font-sans">S</span></button>' : '') +
                    '<button class="btn-s-sync p-1.5 hover:bg-slate-50 text-slate-400 hover:text-homeos-green rounded transition-all" title="Sync">' +
                        '<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>' +
                    '</button>' +
                    '<button class="btn-s-delete p-1.5 hover:bg-red-50 text-slate-300 hover:text-red-500 rounded transition-all" title="Supprimer">' +
                        '<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>' +
                    '</button>' +
                '</div>';

            // Clic principal → addScreen
            el.addEventListener('click', function() {
                console.log('[WsImportList] addScreen:', item.id);
                if (window.wsCanvas) window.wsCanvas.addScreen(item);
            });

            // Double-clic → preview
            el.addEventListener('dblclick', function() {
                if (window.wsCanvas) window.wsCanvas.addScreen(item);
                setTimeout(function() {
                    if (window.enterPreviewMode) window.enterPreviewMode('shell-' + item.id, 'construct');
                }, 100);
            });

            // [S] Stitch
            var btnOpen = el.querySelector('.btn-s-open');
            if (btnOpen) {
                btnOpen.addEventListener('click', function(e) {
                    e.stopPropagation();
                    console.log('[WsImportList] [S] clicked for:', item.id);
                    fetch('/api/stitch/open/' + item.id)
                        .then(function(r) {
                            if (!r.ok) {
                                console.warn('[WsImportList] /api/stitch/open returned', r.status, 'for', item.id);
                                return null;
                            }
                            return r.json();
                        })
                        .then(function(d) {
                            if (d && d.url) {
                                console.log('[WsImportList] opening Stitch:', d.url);
                                window.open(d.url);
                            }
                        })
                        .catch(function(e) {
                            console.error('[WsImportList] Stitch open error:', e);
                        });
                });
            }

            // [↻] Sync
            var btnSync = el.querySelector('.btn-s-sync');
            if (btnSync) {
                btnSync.addEventListener('click', function(e) {
                    e.stopPropagation();
                    console.log('[WsImportList] [↻] sync clicked');
                    fetch('/api/stitch/sync', { method: 'POST' })
                        .then(function(r) {
                            if (r.ok) refresh();
                        })
                        .catch(function(e) {
                            console.error('[WsImportList] sync error:', e);
                        });
                });
            }

            // [×] Delete
            var btnDelete = el.querySelector('.btn-s-delete');
            if (btnDelete) {
                btnDelete.addEventListener('click', function(e) {
                    e.stopPropagation();
                    if (!confirm('Supprimer cet import ?')) return;
                    console.log('[WsImportList] [×] delete:', item.id);
                    fetch('/api/imports/' + encodeURIComponent(item.id), { method: 'DELETE' })
                        .then(function(r) {
                            if (r.ok) refresh();
                        })
                        .catch(function(e) {
                            console.error('[WsImportList] delete error:', e);
                        });
                });
            }

            container.appendChild(el);
        });
    }

    // Exposition
    window.WsImportList = {
        refresh: refresh,
        render: render
    };

    console.log('[WsImportList] ✅ OK');
})();
