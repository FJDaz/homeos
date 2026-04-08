/**
 * WsAssetPicker — M254
 * Gestion des assets images du projet — extraction de ws_main.js.
 *
 * Usage : window.WsAssetPicker.open(), window.WsAssetPicker.refresh()
 * Traces console : [WsAssetPicker] ...
 */
(function() {
    'use strict';
    console.log('[WsAssetPicker] init');

    /**
     * Ouvre/ferme le popover image picker.
     */
    function toggle(event) {
        if (event) event.stopPropagation();
        var popover = document.getElementById('ws-image-picker');
        if (!popover) {
            console.warn('[WsAssetPicker] #ws-image-picker not found');
            return;
        }
        var isOpen = !popover.classList.contains('hidden');
        if (isOpen) {
            popover.classList.add('hidden');
            console.log('[WsAssetPicker] closed');
        } else {
            // Positionner le popover à côté du bouton
            var btn = document.getElementById('ws-btn-image-picker');
            if (btn) {
                var rect = btn.getBoundingClientRect();
                popover.style.top = rect.top + 'px';
                popover.style.left = (window.innerWidth - rect.left + 12) + 'px';
            }
            popover.classList.remove('hidden');
            console.log('[WsAssetPicker] opened');
            fetchAssets();
        }
    }

    /**
     * Fetch la liste des assets du projet actif et rend le HTML.
     */
    async function fetchAssets() {
        console.log('[WsAssetPicker] fetching...');
        try {
            const res = await fetch('/api/projects/active/assets');
            if (!res.ok) {
                console.warn('[WsAssetPicker] fetch failed, status', res.status);
                return;
            }
            const data = await res.json();
            const files = data.files || [];
            console.log('[WsAssetPicker]', files.length, 'assets');
            renderAssets(files);
        } catch(e) {
            console.error('[WsAssetPicker] fetch error:', e);
        }
    }

    /**
     * Rend la liste des assets dans le popover.
     */
    function renderAssets(files) {
        var container = document.getElementById('ws-asset-list');
        if (!container) {
            console.warn('[WsAssetPicker] #ws-asset-list not found');
            return;
        }

        if (files.length === 0) {
            container.innerHTML = '<div class="p-3 text-[10px] text-slate-400 italic">aucune image</div>';
            return;
        }

        container.innerHTML = files.map(function(f) {
            return '<div class="flex items-center gap-2 p-2 hover:bg-slate-50 rounded">' +
                '<img src="' + f.url + '" class="w-8 h-8 object-cover rounded" alt="' + f.name + '">' +
                '<span class="text-[9px] text-slate-600 flex-1 truncate">' + f.name + '</span>' +
                '<button class="asset-copy-btn text-[8px] text-slate-400 hover:text-homeos-green" title="Copier URL" data-url="' + f.url + '">📋</button>' +
                '<button class="asset-delete-btn text-[8px] text-slate-400 hover:text-red-500" title="Supprimer" data-filename="' + f.filename + '">✕</button>' +
                '</div>';
        }).join('');

        // Handlers
        container.querySelectorAll('.asset-copy-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                var url = btn.dataset.url;
                var fullUrl = window.location.origin + url;
                navigator.clipboard.writeText(fullUrl).then(function() {
                    console.log('[WsAssetPicker] URL copied:', fullUrl);
                });
            });
        });

        container.querySelectorAll('.asset-delete-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                var filename = btn.dataset.filename;
                if (!confirm('Supprimer "' + filename + '" ?')) return;
                console.log('[WsAssetPicker] deleting:', filename);
                fetch('/api/projects/assets/img/' + filename, { method: 'DELETE' })
                    .then(function(r) {
                        if (r.ok) fetchAssets();
                    })
                    .catch(function(e) {
                        console.error('[WsAssetPicker] delete error:', e);
                    });
            });
        });
    }

    // Exposition
    window.WsAssetPicker = {
        toggle: toggle,
        open: function() { toggle(null); },
        refresh: fetchAssets,
        fetchAssets: fetchAssets
    };

    console.log('[WsAssetPicker] ✅ OK');
})();
