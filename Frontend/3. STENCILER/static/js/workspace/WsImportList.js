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
     * Stockage des imports pour consultation externe (M260)
     */
    let _items = [];

    async function refresh() {
        console.log('[WsImportList] fetching...');
        try {
            const res = await fetch('/api/retro-genome/imports');
            if (!res.ok) {
                console.warn('[WsImportList] fetch failed, status', res.status);
                return;
            }
            const data = await res.json();
            _items = data.imports || [];
            console.log('[WsImportList]', _items.length, 'imports');
            render(_items);
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

        // M276: Stitch sync button at top
        const syncHeader = document.createElement('div');
        syncHeader.className = 'flex items-center justify-between p-2 border-b border-slate-100 mb-2';
        syncHeader.innerHTML =
            '<button id="ws-stitch-sync-btn" class="flex items-center gap-1.5 text-[9px] font-bold uppercase tracking-wider text-slate-400 hover:text-homeos-green transition-all">' +
                '<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>' +
                'actualiser depuis stitch' +
            '</button>' +
            '<span id="ws-stitch-sync-status" class="text-[8px] text-slate-300"></span>';
        container.appendChild(syncHeader);

        document.getElementById('ws-stitch-sync-btn').onclick = async () => {
            const statusEl = document.getElementById('ws-stitch-sync-status');
            statusEl.textContent = 'sync...';
            statusEl.style.color = '#8cc63f';
            try {
                const res = await fetch('/api/stitch/sync', { method: 'POST' });
                const data = await res.json();
                if (data.synced > 0) {
                    statusEl.textContent = `+${data.synced} écran(s)`;
                    statusEl.style.color = '#8cc63f';
                } else {
                    statusEl.textContent = 'à jour';
                    statusEl.style.color = '#9a9a98';
                }
                setTimeout(() => { statusEl.textContent = ''; refresh(); }, 2000);
            } catch(e) {
                statusEl.textContent = 'erreur';
                statusEl.style.color = '#ddb0b0';
                console.error('Stitch sync failed:', e);
            }
        };

        if (imports.length === 0) {
            container.innerHTML = '<div class="p-4 text-[10px] text-slate-400 italic">aucun import</div>';
            return;
        }

        imports.forEach(function(item) {
            const el = document.createElement('div');
            el.className = 'group flex items-center justify-between p-2 rounded-lg border border-slate-100 bg-white hover:border-homeos-green/30 transition-all cursor-pointer';

            el.innerHTML =
                '<span class="text-[10px] font-medium text-slate-600 truncate flex-1">' + item.name + '</span>' +
                '<div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">' +
                    '<button class="p-1.5 hover:bg-slate-50 text-slate-400 hover:text-homeos-green rounded transition-all" title="Aperçu">' +
                        '<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M24 12s-4.5-8-12-8S0 12 0 12s4.5 8 12 8 12-8 12-8z"/></svg>' +
                    '</button>' +
                    '<button class="btn-s-stitch p-1.5 hover:bg-slate-50 text-slate-400 hover:text-indigo-500 rounded transition-all" title="Ouvrir dans Stitch">' +
                        '<span class="text-[9px] font-black font-sans">S</span></button>' +
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

            // [S] Stitch — générer mega-prompt + ouvrir Stitch
            var btnStitch = el.querySelector('.btn-s-stitch');
            if (btnStitch) {
                btnStitch.addEventListener('click', async function(e) {
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

                        if (data.mega_prompt) {
                            try {
                                await navigator.clipboard.writeText(data.mega_prompt);
                            } catch(err) {
                                var ta = document.createElement('textarea');
                                ta.value = data.mega_prompt;
                                document.body.appendChild(ta);
                                ta.select();
                                document.execCommand('copy');
                                document.body.removeChild(ta);
                            }
                            var toast = document.createElement('div');
                            toast.style.cssText = 'position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#3d3d3c;color:#fff;padding:12px 24px;border-radius:12px;font-size:12px;z-index:99999;';
                            toast.textContent = 'Mega-prompt copié ! Colle-le dans Stitch.';
                            document.body.appendChild(toast);
                            setTimeout(function() { toast.remove(); }, 3000);
                        }
                        window.open(data.stitch_url || 'https://stitch.withgoogle.com', '_blank');
                    } catch(err) {
                        alert('Erreur Stitch: ' + err.message);
                    }
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
        render: render,
        get _items() { return _items; }
    };

    console.log('[WsImportList] ✅ OK');
})();
