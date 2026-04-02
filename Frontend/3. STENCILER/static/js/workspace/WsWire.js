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

        this._manifest = null;
        this.init();
    }

    init() {
        if (this.btnCadrage) {
            this.btnCadrage.onclick = () => this._openCadrage();
        }
        if (this.btnValidate) {
            this.btnValidate.onclick = () => {
                this.hide();
                if (window.exitPreviewMode) window.exitPreviewMode();
            };
        }
    }

    _openCadrage() {
        // Construire le contexte à partir du manifeste courant
        const params = new URLSearchParams();
        if (this._importId) params.set('import_id', this._importId);
        if (this._manifest) {
            const archetype = this._manifest.archetype?.label || '';
            const components = (this._manifest.components || [])
                .slice(0, 10)
                .map(c => `${c.name} (${c.role || '?'})`)
                .join(', ');
            const ctx = [
                archetype ? `Archétype détecté : ${archetype}.` : '',
                components ? `Composants : ${components}.` : '',
                `Import : ${this._importId || '?'}.`
            ].filter(Boolean).join(' ');
            params.set('context', ctx);
        }
        this.hide();
        if (window.exitPreviewMode) window.exitPreviewMode();
        window.open(`/cadrage?${params.toString()}`, '_blank');
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

        this._manifest = manifest;
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
