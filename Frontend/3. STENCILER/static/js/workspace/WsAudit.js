/**
 * WsAudit.js — UX Audit & Toolbar Notifications (Mission 156)
 */
class WsAudit {
    constructor() {}

    /**
     * Met à jour le panneau latéral UX Audit avec les infos de l'écran sélectionné.
     */
    updatePanel(shell) {
        const auditContent = document.getElementById('ws-audit-content');
        if (!auditContent) return;

        const titleEl = shell.querySelector('.ws-screen-title');
        const title = titleEl ? titleEl.textContent : 'Untitled';

        auditContent.innerHTML = `
            <div class="flex items-center gap-2 mb-4">
                <span class="text-[12px] font-bold text-homeos-green uppercase underline decoration-2 underline-offset-4">screen active</span>
                <span class="text-[13px] text-slate-800 font-bold">${title}</span>
            </div>
            <div class="space-y-3">
                <div class="p-3 bg-slate-50 border border-slate-100 rounded-lg">
                    <div class="text-[11px] font-bold text-slate-400 uppercase mb-1">Intent detection</div>
                    <div class="text-[13px] text-slate-600">Interface d'édition détectée. Structure sémantique valide.</div>
                </div>
                <div class="p-3 bg-white border border-slate-100 rounded-lg shadow-sm">
                    <div class="text-[11px] font-bold text-slate-400 uppercase mb-1">Accessibility score</div>
                    <div class="flex items-center gap-2">
                        <div class="h-[6px] flex-1 bg-slate-100 rounded-full overflow-hidden">
                            <div class="h-full bg-homeos-green" style="width: 85%"></div>
                        </div>
                        <span class="text-[12px] font-bold text-slate-600">85%</span>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Notifie la toolbar et met à jour le curseur du canvas.
     */
    notifyToolbar(state, mode, canvasSvg, shellId = null) {
        // 1. Update SVG Cursor
        const cursorMap = { 
            'select': 'default', 
            'drag': 'grab', 
            'frame': 'crosshair', 
            'place-img': 'copy' 
        };
        
        let cursor = cursorMap[mode] || 'default';
        if (mode === 'drag' && window.wsCanvas?.isPanning) cursor = 'grabbing';
        if (mode === 'select' && window.wsCanvas?.selectedScreen) cursor = 'grabbing';
        
        if (canvasSvg) canvasSvg.style.cursor = cursor;

        // 2. Dispatch event for global UI (ws_main hooks)
        const event = new CustomEvent('ws-canvas-state', { 
            detail: { state, shellId, mode } 
        });
        window.dispatchEvent(event);
    }
}

window.WsAudit = WsAudit;
