/**
 * WsWire.js — AetherFlow Wireframe Management (Mission 147)
 * Handles the mapping overlay and validation UI.
 */
class WsWire {
    constructor() {
        this.overlay = document.getElementById('ws-wire-overlay');
        this.tbody = document.getElementById('ws-wire-table-body');
        this.importLabel = document.getElementById('ws-wire-import-label');
        this.btnCadrage = document.getElementById('ws-wire-btn-cadrage');
        this.btnValidate = document.getElementById('ws-wire-btn-validate');

        this.init();
    }

    init() {
        if (this.btnCadrage) {
            this.btnCadrage.onclick = () => {
                // Retour au "Cadrage" (Masque l'overlay et pourrait changer de tab)
                this.hide();
                if (window.exitPreviewMode) window.exitPreviewMode();
            };
        }
        if (this.btnValidate) {
            this.btnValidate.onclick = () => {
                console.log("✅ [WsWire] Wire validated by user");
                this.hide();
                // On pourrait ici notifier le backend ou changer l'état du screen sur le canvas
            };
        }
    }

    /**
     * Affiche l'overlay avec les données du manifeste.
     * @param {Object} manifest - Le contenu du manifest_{id}.json
     * @param {string} importName - Le nom de l'import pour le label
     */
    show(manifest, importName = "Import") {
        console.log("🔍 [WsWire] Diagnostic en cours pour:", importName);
        console.log("🎬 [WsWire] Displaying mapping overlay for:", importName);
        if (!this.overlay || !this.tbody) return;

        this.importLabel.innerText = importName;
        this.tbody.innerHTML = '';

        // Priorité components (M151 ManifestInferer), fallback screens
        const screens = (manifest.components?.length ? manifest.components : manifest.screens) || [];
        
        if (screens.length === 0) {
            this.tbody.innerHTML = `
                <tr>
                    <td colspan="4" class="px-4 py-8 text-center text-slate-400 italic">
                        Aucun mapping détecté dans le manifeste.
                    </td>
                </tr>
            `;
        } else {
            screens.forEach((s, idx) => {
                const tr = document.createElement('tr');
                tr.className = "hover:bg-slate-50 transition-colors";
                
                tr.innerHTML = `
                    <td class="px-4 py-3 font-semibold text-slate-800">${s.name || 'Sans nom'}</td>
                    <td class="px-4 py-3">
                        <span class="px-2 py-0.5 bg-slate-100 text-slate-500 rounded text-[9px] font-bold uppercase tracking-widest">
                            ${s.role || 'ELEMENT'}
                        </span>
                    </td>
                    <td class="px-4 py-3 font-mono text-slate-400 align-middle">${s.z_index || 0}</td>
                    <td class="px-4 py-3">
                        <div class="flex items-center gap-2">
                            <div class="w-1.5 h-1.5 rounded-full bg-[#A3CD54] animate-pulse"></div>
                            <span class="text-[#A3CD54] font-bold text-[10px] uppercase tracking-tighter">Mapped</span>
                        </div>
                    </td>
                `;
                this.tbody.appendChild(tr);
            });
        }

        this.overlay.classList.remove('hidden');
    }

    hide() {
        if (this.overlay) this.overlay.classList.add('hidden');
    }
}

// Initialisation globale
document.addEventListener('DOMContentLoaded', () => {
    window.wsWire = new WsWire();
});
