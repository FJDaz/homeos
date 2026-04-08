/* ws_main.js — AetherFlow Workspace Orchestrator (Mission 127 V2) */

document.addEventListener('DOMContentLoaded', async () => {
    console.log("🚀 ws_main: starting workspace design V2 (Hexagonal Architecture)...");

    // 1. Initialiser l'Architecture Hexagonale (Mission 156)
    try { window.wsAudit = new WsAudit(); } catch(e) { console.error('[ws_main] WsAudit crash:', e); }
    try { window.wsForge = new WsForge(); } catch(e) { console.error('[ws_main] WsForge crash:', e); }
    try { window.wsPreview = new WsPreview(); } catch(e) { console.error('[ws_main] WsPreview crash:', e); }

    try {
        const canvas = new WsCanvas('ws-canvas', 'canvas-wrapper');
        window.wsCanvas = canvas;
    } catch(e) { console.error('[ws_main] WsCanvas crash:', e); }

    // 2. Initialiser le Chat Sullivan (Main + Surgical)
    try {
        const chat = new WsChatMain('ws-chat-mount');
        window.wsChat = chat;
    } catch(e) { console.error('[ws_main] WsChatMain crash:', e); }

    try { window.wsSurgicalChat = new WsChatSurgical('ws-surgical-popover'); } catch(e) { console.error('[ws_main] WsChatSurgical crash:', e); }
    try { window.wsWire = new WsWire(); } catch(e) { console.error('[ws_main] WsWire crash:', e); }
    try { window.wsFEEStudio = new WsFEEStudio(window.wsBackend); } catch(e) { console.error('[ws_main] WsFEEStudio crash:', e); }

    // 2b. Initialiser l'Inspecteur (Mission 130)
    try {
        const inspect = new WsInspect(window);
        window.wsInspect = inspect;
    } catch(e) { console.error('[ws_main] WsInspect crash:', e); }

    // 2c. Charger les Design Tokens (Mission 159)
    try {
        const tokenRes = await fetch('/api/workspace/tokens');
        const tokens = await tokenRes.json();
        inspect.applyDesignTokens(tokens);
    } catch (err) {
        console.error("❌ ws_main: failed to load design tokens", err);
    }

    // 2d. Panels Draggables (Mission 209)
    if (window.PanelDragger) {
        const draggablePanels = [
            'panel-screens',
            'ws-monaco-popover', 'ws-surgical-popover',
            'ws-color-popover', 'ws-typo-popover', 'ws-effects-popover'
        ];
        draggablePanels.forEach(id => {
            const el = document.getElementById(id);
            if (el) new window.PanelDragger(el);
        });
        console.log("✅ [M209] PanelDragger initialized for all workspace panels");
    }

    // 3. Charger le contexte courant (depuis landing.html)
    await loadCurrentContext();

    // 4. Charger la liste des imports (Panel Audit gauche)
    await fetchWorkspaceImports();

    // 4b. Wire upload input (après wsChat initialisé)
    const uploadInput = document.getElementById('ws-direct-upload');
    if (uploadInput) uploadInput.addEventListener('change', handleDirectUpload);

    // 5. Setup UI buttons (Right Toolbar)
    document.querySelectorAll('.ws-tool-btn').forEach(btn => {
        btn.onclick = () => {
            const mode = btn.getAttribute('data-mode');
            window.wsCanvas?.setMode(mode);

            // Mission 207 — Ouvrir le drawer typographie quand mode = text
            if (mode === 'text') {
                const drawer = document.getElementById('ws-font-drawer');
                if (drawer) drawer.classList.toggle('hidden');
            }

            // Éventuel postMessage si l'iframe préview existe
            const iframe = document.querySelector('#ws-preview-frame-container iframe');
            if (iframe && iframe.contentWindow) {
                iframe.contentWindow.postMessage({ type: 'inspect-tool-change', mode: mode }, '*');
            }
        };
    });

    // 5b. Setup Mode buttons (Sullivan Panel - Mission 160)
    document.querySelectorAll('.ws-mode-btn').forEach(btn => {
        btn.onclick = (e) => {
            console.log('diag: mode click', e.target);
            const activeMode = btn.getAttribute('data-mode');
            // UI Toggle (3 states)
            document.querySelectorAll('.ws-mode-btn').forEach(b => {
                const isActive = b === btn;
                b.classList.toggle('active', isActive);
                
                // Mission 147: Reset default classes that might conflict with .active CSS
                if (!isActive) {
                    b.classList.add('text-slate-400');
                    b.classList.remove('bg-white', 'shadow-sm', 'text-slate-600');
                } else if (activeMode !== 'audit') {
                    // Default active style for non-audit modes (construct, front-dev)
                    b.classList.add('bg-white', 'text-slate-600', 'shadow-sm');
                }
            });
            
            document.body.classList.remove('mode-audit', 'mode-front-dev', 'mode-construct');
            
            if (activeMode === 'audit') document.body.classList.add('mode-audit');
            if (activeMode === 'front-dev') document.body.classList.add('mode-front-dev');
            if (activeMode === 'construct') document.body.classList.add('mode-construct');
            
            document.body.style.cursor = 
                (activeMode === 'text') ? 'text' :
                (activeMode === 'frame') ? 'crosshair' :
                (activeMode === 'drag') ? 'grab' :
                (activeMode === 'audit') ? 'crosshair' :
                (activeMode === 'front-dev') ? 'alias' :
                (activeMode === 'colors') ? 'copy' :
                (activeMode === 'place-img') ? 'copy' : 'default';
            
            window.wsCanvas?.setMode(activeMode);
            if (activeMode === 'audit' && window.wsWire) {
                const activeId = window.wsCanvas?.activeScreenId;
                const shell = activeId ? document.getElementById(activeId) : null;
                const manifest = shell ? JSON.parse(shell.dataset.manifest || '{}') : {};
                const title = shell?.querySelector('.ws-screen-title')?.textContent || 'Import';
                window.wsWire.show(manifest, title);
            } else if (window.wsWire) {
                window.wsWire.hide();
            }
            
            const iframe = document.querySelector('#ws-preview-frame-container iframe');
            if (iframe && iframe.contentWindow) {
                iframe.contentWindow.postMessage({ type: 'inspect-tool-change', mode: activeMode }, '*');
            }
        };
    });

    // 6. Global Shortcuts (Mission 133 - Undo)
    window.addEventListener('keydown', (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key === 'z') {
            e.preventDefault();
            console.log("🚀 ws_main: Undo Shortcut Detected (Cmd+Z)");
            if (window.wsInspect) window.wsInspect.undo();
        }
    });

    const zReset = document.getElementById('btn-reset-view');
    if (zReset) zReset.onclick = () => canvas.resetView();

    // 7. Image Picker (Mission 235)
    const btnImagePicker = document.getElementById('ws-btn-image-picker');
    if (btnImagePicker) {
        btnImagePicker.onclick = (e) => toggleImagePicker(e);
    }

    console.log("✅ ws_main: workspace ready (hexagonal architecture active)");
});

// --- EXPOSITIONS GLOBALES (Bridging avec WsPreview) ---
window.enterPreviewMode = (shellId, mode) => window.wsPreview?.enterPreviewMode(shellId, mode);
window.exitPreviewMode = () => window.wsPreview?.exitPreviewMode();


async function loadCurrentContext() {
    try {
        const res = await fetch('/api/frd/current');
        const context = await res.json();
        
        if (context && context.id) {
            console.log("🚀 ws_main: auto-loading current context", context.id);
            window.wsCanvas.addScreen(context);
        }
    } catch (e) {
        console.error("ws_main: failed to load context", e);
    }
}

/**
 * window.wsSendMessage (Mission 200B - Transactional Handshake)
 * Envoie un message à l'iframe et attend un 'receipt' avec le même transactionId.
 */
window.wsSendMessage = function(iframe, message, timeout = 2000) {
    return new Promise((resolve, reject) => {
        if (!iframe || !iframe.contentWindow) return reject("Iframe non disponible");
        
        const transactionId = 'tx-' + Math.random().toString(36).substr(2, 9);
        const request = { ...message, transactionId };
        
        const handler = (e) => {
            if (e.data && e.data.type === 'receipt' && e.data.transactionId === transactionId) {
                window.removeEventListener('message', handler);
                clearTimeout(timer);
                resolve(e.data);
            }
        };
        
        window.addEventListener('message', handler);
        const timer = setTimeout(() => {
            window.removeEventListener('message', handler);
            console.warn(`⚠️ Handshake Timeout [${transactionId}] for type: ${message.type}`);
            resolve({ status: 'timeout', transactionId });
        }, timeout);
        
        iframe.contentWindow.postMessage(request, '*');
    });
};

async function fetchWorkspaceImports() {
    const list = document.getElementById('ws-import-list');
    const session = JSON.parse(localStorage.getItem('homeos_session') || '{}');
    const isStudent = session.role === 'student';

    try {
        const res = await fetch('/api/retro-genome/imports');
        const data = await res.json();
        const imports = data.imports || [];
        
        // Mission 232: Dashboard Projet (token-aware pour élèves)
        const manifestHeaders = session.token ? { 'X-User-Token': session.token } : {};
        const manifestRes = await fetch('/api/projects/active/manifest', { headers: manifestHeaders });
        const manifest = manifestRes.ok ? await manifestRes.json() : {};
        const projectName = manifest.name || "Mon Projet HoméOS";
        const stitchId = manifest.stitch_project_id || "";

        list.innerHTML = `
            <div class="ws-dashboard-section mb-6">
                <!-- Header "Mon Projet" -->
                <div class="flex items-center justify-between mb-3 group cursor-pointer" onclick="this.nextElementSibling.classList.toggle('hidden')">
                    <div class="flex items-center gap-2">
                        <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">▸ mon projet</span>
                    </div>
                </div>
                
                <div class="pl-2 space-y-4">
                    <!-- Titre du projet -->
                    <div class="text-[11px] font-bold text-slate-700">${projectName}</div>

                    <!-- Sous-collapse Stitch -->
                    <div class="rounded-lg border border-slate-100 bg-slate-50/50 overflow-hidden">
                        <div class="px-3 py-2 border-b border-slate-100 flex items-center justify-between cursor-pointer hover:bg-slate-100 transition-all" onclick="this.nextElementSibling.classList.toggle('hidden')">
                            <span class="text-[9px] font-bold text-slate-400 uppercase tracking-wider">stitch link</span>
                            <span class="text-[8px] text-slate-300">${stitchId ? 'lié' : 'non lié'}</span>
                        </div>
                        <div class="p-3 space-y-2 ${stitchId ? 'hidden' : ''}">
                            <input id="db-stitch-id" type="text" value="${stitchId}" placeholder="ID Stitch..." 
                                class="w-full bg-white border border-slate-200 px-2 py-1.5 text-[10px] rounded focus:border-homeos-green outline-none">
                            <button onclick="linkStitchProject()" class="w-full py-1.5 bg-slate-800 text-white text-[9px] font-bold uppercase tracking-widest rounded hover:bg-black transition-all">
                                lier →
                            </button>
                        </div>
                    </div>

                    <!-- Liste des écrans -->
                    <div class="space-y-2">
                        <div class="text-[9px] font-bold text-slate-400 uppercase tracking-wider mb-2">mes écrans</div>
                        <div id="db-screens-container" class="space-y-1.5">
                            ${imports.length === 0 ? '<div class="text-[10px] text-slate-300 italic">aucun écran — utilisez stitch</div>' : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Rendu des écrans
        const screensContainer = document.getElementById('db-screens-container');
        imports.forEach(item => {
            const el = document.createElement('div');
            el.className = 'group flex items-center justify-between p-2 rounded-lg border border-slate-100 bg-white hover:border-homeos-green/30 transition-all cursor-pointer';
            el.innerHTML = `
                <span class="text-[10px] font-medium text-slate-600 truncate flex-1">${item.name}</span>
                <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <!-- [👁] HoméOS -->
                    <button class="p-1.5 hover:bg-slate-50 text-slate-400 hover:text-homeos-green rounded transition-all" title="Aperçu HoméOS">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M24 12s-4.5-8-12-8S0 12 0 12s4.5 8 12 8 12-8 12-8z"/></svg>
                    </button>
                    <!-- [S] Stitch -->
                    <button class="btn-s-open p-1.5 hover:bg-slate-50 text-slate-400 hover:text-indigo-500 rounded transition-all" title="Ouvrir dans Stitch">
                        <span class="text-[9px] font-black font-sans">S</span>
                    </button>
                    <!-- [↻] Sync -->
                    <button class="btn-s-sync p-1.5 hover:bg-slate-50 text-slate-400 hover:text-homeos-green rounded transition-all" title="Synchroniser">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                    </button>
                    <!-- [×] Kill -->
                    <button class="btn-s-delete p-1.5 hover:bg-red-50 text-slate-300 hover:text-red-500 rounded transition-all" title="Supprimer">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                    </button>
                </div>
            `;

            el.onclick = () => window.wsCanvas?.addScreen(item);
            el.ondblclick = () => {
                window.wsCanvas?.addScreen(item);
                setTimeout(() => window.enterPreviewMode(`shell-${item.id}`), 100);
            };

            // Actions
            const btnOpen = el.querySelector('.btn-s-open');
            if (btnOpen) btnOpen.onclick = async (e) => {
                e.stopPropagation();
                const res = await fetch(`/api/stitch/open/${item.id}`);
                if (res.ok) {
                    const d = await res.json();
                    if (d.url) window.open(d.url);
                }
            };

            el.querySelector('.btn-s-sync').onclick = async (e) => {
                e.stopPropagation();
                const res = await fetch('/api/stitch/sync', { method: 'POST' });
                if (res.ok) window.fetchWorkspaceImports();
            };

            el.querySelector('.btn-s-delete').onclick = async (e) => {
                e.stopPropagation();
                if (confirm(`Supprimer l'import ${item.name} ?`)) {
                    await fetch(`/api/imports/${encodeURIComponent(item.id)}`, { method: 'DELETE' });
                    window.fetchWorkspaceImports();
                }
            };

            screensContainer.appendChild(el);
        });

    } catch (e) {
        console.error("ws_main: failed to fetch imports", e);
        list.innerHTML = '<div class="text-[10px] text-red-400">erreur chargement dashboard</div>';
    }
}

// Upload direct (PNG, SVG, ZIP, HTML…) — tout passe par /api/import/upload
async function handleDirectUpload(event) {
    const files = event.target.files;
    if (!files || files.length === 0) return;
    for (const file of files) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('filename', file.name);
            const res = await fetch('/api/import/upload', { method: 'POST', body: formData });
            if (!res.ok) throw new Error(`upload ${res.status}`);
            if (window.fetchWorkspaceImports) await window.fetchWorkspaceImports();
        } catch (e) {
            console.error('handleDirectUpload: failed for', file.name, e);
        }
    }
    event.target.value = '';
}

// Helper pour lier le projet Stitch depus le dashboard
window.linkStitchProject = async function() {
    const id = document.getElementById('db-stitch-id').value;
    if (!id) return;
    try {
        const res = await fetch('/api/stitch/pull', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ project_id: id })
        });
        if (res.ok) {
            window.fetchWorkspaceImports();
        }
    } catch(e) { console.error("Link error", e); }
};

// --- PANEL MANAGEMENT (Mission 129) ---
function togglePanel(id) {
    const panel = document.getElementById(id);
    const badgeId = id.replace('panel-', 'badge-');
    const badge = document.getElementById(badgeId);
    
    // Toggle class and let CSS handle the rest
    const isCollapsed = panel.classList.toggle('collapsed');
    
    // Badge visibility with smooth transition
    if (badge) {
        if (isCollapsed) {
            // Un petit délai permet au panel de commencer à se replier 
            // avant que le badge ne demande sa propre hauteur
            setTimeout(() => {
                badge.classList.remove('badge-hidden');
            }, 50);
        } else {
            badge.classList.add('badge-hidden');
        }
    }
}

// --- PREVIEW MODE (Mission 130-B / 150) ---
function enterPreviewMode(shellId, mode = 'construct') {
    console.log(`🔍 [ws_main] enterPreviewMode called [${mode}] for:`, shellId);
    const id = shellId || window.wsCanvas.activeScreenId;
    
    if (!id) {
        console.warn("⚠️ [ws_main] No ID provided and no active screen found.");
        alert("Sélectionnez un écran pour l'aperçu.");
        return;
    }

    const overlay = document.getElementById('ws-preview-overlay');
    const shell = document.getElementById(id);
    if (!shell || !overlay) return;

    // Orchestration Z-Index (Mission 150)
    if (mode === 'audit') {
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
    iframe.className = "w-full h-full border-none bg-white";
    if (iframeSource.srcdoc) iframe.srcdoc = iframeSource.srcdoc;
    else iframe.src = iframeSource.src;

    container.appendChild(iframe);
    
    // Mission 147 / 150 : Audit Overlay Orchestration
    if (mode === 'audit' && window.wsWire) {
        try {
            const manifest = JSON.parse(shell.dataset.manifest || '{}');
            const title = shell.querySelector('.ws-screen-title')?.textContent || 'Sans titre';
            window.wsWire.show(manifest, title);
        } catch(e) {
            console.error("M147: Manifest parsing failed", e);
        }
    } else if (window.wsWire) {
        window.wsWire.hide();
    }

    // Mission 130 : Injecter l'inspecteur
    if (window.wsInspect) {
        window.wsInspect.injectTracker(iframe);
    }

    document.body.classList.add('preview-mode');
    console.log(`🎬 [ws_main] Preview Mode Success [${mode}] for:`, id);
}

function exitPreviewMode() {
    document.body.classList.remove('preview-mode');
    document.getElementById('ws-preview-frame-container').innerHTML = '';
}

function saveProject() {
    // Mockup save logic
    console.log("💾 Saving project state...");
    const btn = document.getElementById('ws-btn-save');
    const originalContent = btn.innerHTML;
    
    btn.innerHTML = '<svg class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>';
    
    setTimeout(() => {
        btn.innerHTML = '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>';
        setTimeout(() => {
            btn.innerHTML = originalContent;
        }, 1500);
    }, 800);
}

// --- ASSETS MANAGEMENT (Mission 235) ---
async function toggleImagePicker(event) {
    const popover = document.getElementById('ws-image-picker');
    if (!popover) return;

    if (!popover.classList.contains('hidden')) {
        popover.classList.add('hidden', 'scale-95', 'opacity-0');
        return;
    }

    // Positionner à gauche de la toolbar
    const btn = event.currentTarget;
    const rect = btn.getBoundingClientRect();
    popover.style.top = `${rect.top}px`;
    popover.style.right = `${window.innerWidth - rect.left + 12}px`;

    popover.classList.remove('hidden');
    // Petit timeout pour l'animation
    setTimeout(() => {
        popover.classList.remove('scale-95', 'opacity-0');
        popover.classList.add('scale-100', 'opacity-100');
    }, 10);

    await fetchProjectAssets();
}

async function fetchProjectAssets() {
    const list = document.getElementById('ws-image-list');
    try {
        const res = await fetch('/api/projects/active/assets');
        const data = await res.json();
        const files = data.files || [];

        if (files.length === 0) {
            list.innerHTML = '<div class="text-[10px] text-slate-300 italic text-center py-4">aucune image trouvée</div>';
            return;
        }

        list.innerHTML = '';
        files.forEach(file => {
            const item = document.createElement('div');
            item.className = 'group flex items-center gap-3 p-2 rounded-lg border border-slate-100 bg-white hover:border-homeos-green/30 transition-all';
            
            const isSvg = file.filename.endsWith('.svg');
            const previewUrl = file.url;

            item.innerHTML = `
                <div class="w-10 h-10 rounded border border-slate-100 bg-slate-50 flex-shrink-0 flex items-center justify-center overflow-hidden">
                    ${isSvg ? `<img src="${previewUrl}" class="w-6 h-6 object-contain">` : `<img src="${previewUrl}" class="w-full h-full object-cover">`}
                </div>
                <div class="flex-1 min-width-0">
                    <div class="text-[10px] font-bold text-slate-700 truncate">${file.name}</div>
                    <div class="text-[8px] text-slate-400 uppercase tracking-tighter">${(file.size / 1024).toFixed(1)} KB</div>
                </div>
                <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button class="p-1.5 hover:bg-slate-50 text-slate-400 hover:text-homeos-green rounded" title="Copier le lien" onclick="copyAssetUrl('${file.url}')">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"/></svg>
                    </button>
                    <button class="p-1.5 hover:bg-red-50 text-slate-300 hover:text-red-500 rounded" title="Supprimer" onclick="deleteAsset('${file.filename}')">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                    </button>
                </div>
            `;
            list.appendChild(item);
        });
    } catch (e) {
        console.error("fetchProjectAssets error", e);
        list.innerHTML = '<div class="text-[10px] text-red-400 italic">erreur chargement assets</div>';
    }
}

window.copyAssetUrl = (url) => {
    const fullUrl = window.location.origin + url;
    navigator.clipboard.writeText(fullUrl).then(() => {
        // Feedback visuel discret ? 
        console.log("URL copiée :", fullUrl);
    });
};

window.deleteAsset = async (filename) => {
    if (!confirm(`Supprimer cette image définitivement ?`)) return;
    try {
        const res = await fetch(`/api/projects/assets/img/${filename}`, { method: 'DELETE' });
        if (res.ok) fetchProjectAssets();
    } catch (e) { console.error("Lelete error", e); }
};

// Global exposure
window.fetchWorkspaceImports = fetchWorkspaceImports;
window.togglePanel = togglePanel;
window.enterPreviewMode = enterPreviewMode;
window.exitPreviewMode = exitPreviewMode;
window.saveProject = saveProject;
window.toggleImagePicker = toggleImagePicker;
