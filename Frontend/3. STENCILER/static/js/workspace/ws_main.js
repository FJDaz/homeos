/* ws_main.js — AetherFlow Workspace Orchestrator (Mission 127 V2) */

document.addEventListener('DOMContentLoaded', async () => {
    console.log("🚀 ws_main: starting workspace design V2...");

    // 1. Initialiser le Canvas
    const canvas = new WsCanvas('ws-canvas', 'canvas-wrapper');
    window.wsCanvas = canvas;

    // 2. Initialiser le Chat Sullivan
    const chat = new WsChat('ws-chat-mount');
    window.wsChat = chat;

    // 3. Charger le contexte courant (depuis landing.html)
    await loadCurrentContext();

    // 4. Charger la liste des imports (Panel Audit gauche)
    await fetchWorkspaceImports();

    // 4b. Wire upload input (après wsChat initialisé)
    const uploadInput = document.getElementById('ws-direct-upload');
    if (uploadInput) uploadInput.addEventListener('change', (e) => chat.handleDirectUpload(e));

    // 5. Setup UI buttons (Right Toolbar)
    const zIn = document.getElementById('btn-zoom-in');
    const zOut = document.getElementById('btn-zoom-out');
    const zReset = document.getElementById('btn-reset-view');
    if (zIn) zIn.onclick = () => canvas.setZoom(canvas.scale * 1.2);
    if (zOut) zOut.onclick = () => canvas.setZoom(canvas.scale / 1.2);
    if (zReset) zReset.onclick = () => canvas.resetView();

    console.log("✅ ws_main: workspace ready");
});

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
        if (imports.length === 0) {
            list.innerHTML = '<div class="text-[10px] text-zinc-400 italic">aucun import disponible</div>';
            return;
        }

        imports.forEach(item => {
            const el = document.createElement('div');
            el.className = 'import-card-workspace flex flex-col gap-2 group';
            
            const ext = (item.name || 'file').split('.').pop().toUpperCase();
            el.innerHTML = `
                <div class="flex items-center justify-between">
                    <div class="w-6 h-6 bg-slate-50 border border-slate-100 rounded text-[8px] font-bold text-zinc-400 flex items-center justify-center">${ext}</div>
                    <button class="opacity-0 group-hover:opacity-100 p-1 hover:bg-homeos-green hover:text-white rounded text-homeos-green transition-all" title="Ajouter au canvas">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                    </button>
                </div>
                <div class="truncate text-[11px] font-semibold text-slate-700">${item.name}</div>
                <div class="text-[9px] text-slate-400 font-medium">${new Date(item.timestamp).toLocaleString()}</div>
            `;
            
            el.querySelector('button').onclick = (e) => {
                e.stopPropagation();
                window.wsCanvas.addScreen(item);
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

// --- PREVIEW MODE (Mission 130-B) ---
function enterPreviewMode(shellId) {
    console.log("🔍 [ws_main] enterPreviewMode called with:", shellId);
    const id = shellId || window.wsCanvas.activeScreenId;
    
    if (!id) {
        console.warn("⚠️ [ws_main] No ID provided and no active screen found.");
        alert("Sélectionnez un écran pour l'aperçu.");
        return;
    }

    console.log("🔍 [ws_main] Target ID:", id);
    const shell = document.getElementById(id);
    if (!shell) {
        console.error("❌ [ws_main] Shell element not found in DOM:", id);
        return;
    }

    const iframeSource = shell.querySelector('iframe');
    if (!iframeSource) {
        console.error("❌ [ws_main] No <iframe> found inside shell:", id);
        return;
    }

    console.log("🔍 [ws_main] iframe source found:", iframeSource.src || "srcdoc");
    const container = document.getElementById('ws-preview-frame-container');
    if (!container) {
        console.error("❌ [ws_main] #ws-preview-frame-container not found!");
        return;
    }

    container.innerHTML = ''; 
    const iframe = document.createElement('iframe');
    iframe.className = "w-full h-full border-none bg-white";
    if (iframeSource.srcdoc) iframe.srcdoc = iframeSource.srcdoc;
    else iframe.src = iframeSource.src;

    container.appendChild(iframe);
    document.body.classList.add('preview-mode');
    console.log("🎬 [ws_main] Fullscreen Preview SUCCESS for:", id);
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
