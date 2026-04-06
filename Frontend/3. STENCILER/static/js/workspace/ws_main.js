/* ws_main.js — AetherFlow Workspace Orchestrator (Mission 127 V2) */

document.addEventListener('DOMContentLoaded', async () => {
    console.log("🚀 ws_main: starting workspace design V2 (Hexagonal Architecture)...");

    // 1. Initialiser l'Architecture Hexagonale (Mission 156)
    window.wsAudit = new WsAudit();
    window.wsForge = new WsForge();
    window.wsPreview = new WsPreview();
    
    const canvas = new WsCanvas('ws-canvas', 'canvas-wrapper');
    window.wsCanvas = canvas;

    // 2. Initialiser le Chat Sullivan (Main + Surgical)
    const chat = new WsChatMain('ws-chat-mount');
    window.wsChat = chat;
    window.wsSurgicalChat = new WsChatSurgical('ws-surgical-popover');
    window.wsWire = new WsWire();

    // 2b. Initialiser l'Inspecteur (Mission 130)
    const inspect = new WsInspect(window);
    window.wsInspect = inspect;

    // 2c. Charger les Design Tokens (Mission 159)
    try {
        const tokenRes = await fetch('/api/workspace/tokens');
        const tokens = await tokenRes.json();
        inspect.applyDesignTokens(tokens);
    } catch (err) {
        console.error("❌ ws_main: failed to load design tokens", err);
    }

    // 3. Charger le contexte courant (depuis landing.html)
    await loadCurrentContext();

    // 4. Charger la liste des imports (Panel Audit gauche)
    await fetchWorkspaceImports();

    // 4b. Wire upload input (après wsChat initialisé)
    const uploadInput = document.getElementById('ws-direct-upload');
    if (uploadInput) uploadInput.addEventListener('change', (e) => chat.handleDirectUpload(e));

    // 5. Setup UI buttons (Right Toolbar)
    document.querySelectorAll('.ws-tool-btn').forEach(btn => {
        btn.onclick = () => {
            const mode = btn.getAttribute('data-mode');
            window.wsCanvas?.setMode(mode);
            
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

async function fetchWorkspaceImports() {
    const list = document.getElementById('ws-import-list');
    try {
        const res = await fetch('/api/retro-genome/imports');
        const data = await res.json();
        const imports = data.imports || [];
        
        list.innerHTML = '';

        // Screens système figés (BRS + Workspace actuel)
        const systemScreens = [
            { id: '_sys_cadrage_alt',name: 'Cadrage Alt',    tpl: 'cadrage_alt.html' },
        ];
        list.insertAdjacentHTML('beforeend', '<div style="font-size:8px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#94a3b8;padding:4px 0 2px;">système</div>');
        systemScreens.forEach(s => {
            const el = document.createElement('div');
            el.className = 'import-card-workspace flex flex-col gap-1 group border-b border-slate-100 pb-2 mb-1';
            el.innerHTML = `
                <div class="flex items-center gap-2">
                    <div class="w-6 h-6 bg-slate-50 border border-slate-100 rounded text-[8px] font-bold text-zinc-400 flex items-center justify-center">SYS</div>
                    <span class="text-[10px] font-bold text-slate-500 truncate">${s.name}</span>
                </div>`;
            el.style.cursor = 'pointer';
            el.onclick = () => {
                // Charger comme screen canvas — Sullivan peut l'éditer
                window.wsCanvas?.addScreen({
                    id: s.id, name: s.name, type: 'html',
                    html_template: s.tpl, elements_count: 0
                });
            };
            list.appendChild(el);
        });

        // Templates "DÉPARTS" (Mission 110 Hotfix)
        try {
            const tplRes = await fetch('/api/workspace/templates');
            const tplData = await tplRes.json();
            const tpls = tplData.templates || [];
            
            if (tpls.length > 0) {
                list.insertAdjacentHTML('beforeend', '<div style="font-size:8px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#94a3b8;padding:4px 0 2px;">départs</div>');
                tpls.forEach(t => {
                    const el = document.createElement('div');
                    el.className = 'import-card-workspace flex flex-col gap-1 group border-b border-slate-100 pb-2 mb-1';
                    el.innerHTML = `
                        <div class="flex items-center gap-2">
                            <div class="w-6 h-6 bg-slate-50 border border-slate-100 rounded text-[8px] font-bold text-homeos-green flex items-center justify-center">TPL</div>
                            <span class="text-[10px] font-bold text-slate-500 truncate">${t.name}</span>
                        </div>`;
                    el.style.cursor = 'pointer';
                    el.onclick = () => {
                        window.wsCanvas?.addScreen({
                            id: 'tpl-' + t.name, name: t.name, type: 'html',
                            html_template: t.tpl, elements_count: 0
                        });
                    };
                    list.appendChild(el);
                });
            }
        } catch(err) { console.error("❌ Mission 110: templates load failed", err); }

        list.insertAdjacentHTML('beforeend', '<div style="font-size:8px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#94a3b8;padding:6px 0 2px;">imports</div>');
        if (imports.length === 0) {
            list.insertAdjacentHTML('beforeend', '<div class="text-[10px] text-zinc-400 italic">aucun import disponible</div>');
            return;
        }

        imports.forEach(item => {
            const el = document.createElement('div');
            el.className = 'import-card-workspace flex flex-col gap-2 group';
            
            const ext = (item.name || 'file').split('.').pop().toUpperCase();
            el.innerHTML = `
                <div class="flex items-center justify-between">
                    <div class="w-6 h-6 bg-slate-50 border border-slate-100 rounded text-[8px] font-bold text-zinc-400 flex items-center justify-center">${ext}</div>
                    <div class="flex gap-1">
                        <button class="ws-del-import-btn opacity-0 group-hover:opacity-100 p-1 hover:bg-red-500 hover:text-white rounded text-red-400 transition-all" title="Supprimer l'import">
                            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                        </button>
                        <button class="ws-add-to-canvas-btn opacity-0 group-hover:opacity-100 p-1 hover:bg-homeos-green hover:text-white rounded text-homeos-green transition-all" title="Ajouter au canvas">
                            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                        </button>
                    </div>
                </div>
                <div class="truncate text-[11px] font-semibold text-slate-700">${item.name}</div>
                <div class="text-[9px] text-slate-400 font-medium">${new Date(item.timestamp).toLocaleString()}</div>
            `;
            
            el.style.cursor = 'pointer';
            
            // Clic simple -> ajoute au canvas
            el.onclick = (e) => {
                e.stopPropagation();
                window.wsCanvas.addScreen(item);
            };
            
            // Double clic -> ajoute au canvas ET entre en aperçu (ou entre juste en aperçu si déjà présent)
            el.ondblclick = (e) => {
                e.stopPropagation();
                e.preventDefault();
                // Vérifier si le shell existe déjà sur le canvas
                let shell = document.getElementById(`shell-${item.id}`);
                if (!shell) {
                    shell = window.wsCanvas.addScreen(item);
                }
                // Petit délai pour laisser le DOM SVG se mettre à jour
                setTimeout(() => {
                    if (window.enterPreviewMode) window.enterPreviewMode(`shell-${item.id}`);
                }, 100);
            };

            el.querySelector('.ws-add-to-canvas-btn').onclick = (e) => {
                e.stopPropagation();
                window.wsCanvas.addScreen(item);
            };

            el.querySelector('.ws-del-import-btn').onclick = async (e) => {
                e.stopPropagation();
                // Suppression immédiate — Mission 141
                try {
                    const res = await fetch(`/api/imports/${encodeURIComponent(item.id)}`, { method: 'DELETE' });
                    if (res.ok) {
                        el.remove();
                        const shell = document.getElementById(`shell-${item.id}`);
                        if (shell) shell.remove();
                    } else {
                        console.error("❌ Failed to delete import", res.status);
                    }
                } catch (err) {
                    console.error("❌ Error deleting import", err);
                }
            };

            list.appendChild(el);
        });

    } catch (e) {
        console.error("ws_main: failed to fetch imports", e);
        list.innerHTML = '<div class="text-[10px] text-red-400">erreur chargement</div>';
    }
}

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

// Global exposure
window.fetchWorkspaceImports = fetchWorkspaceImports;
window.togglePanel = togglePanel;
window.enterPreviewMode = enterPreviewMode;
window.exitPreviewMode = exitPreviewMode;
window.saveProject = saveProject;
