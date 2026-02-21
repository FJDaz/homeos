/**
 * Nuance.feature.js
 * Gère les sous-styles (Nuances) du Genome : Grain, Registre, Présence.
 * Conformité Art 7 §7.1 (Règle des 300 lignes)
 */

export const SUBSTYLE_DEFAULTS = {
    grain: 'standard',
    registre: 'body',
    presence: 'neutre'
};

export function resolveSubstyle(node, parentSubstyle = {}) {
    return {
        ...SUBSTYLE_DEFAULTS,
        ...parentSubstyle,
        ...(node._substyle || {})
    };
}

export const NuanceUI = {
    render(node) {
        const substyle = resolveSubstyle(node);

        return `
            <div class="cz-panel" id="panel-nuance">
                <div class="panel-header">
                    <span>NUANCE (SOUS-STYLES)</span>
                    <span class="chevron">▼</span>
                </div>
                <div class="panel-content">
                    <div class="style-grid">
                        <div class="input-group">
                            <label>DENSITÉ (GRAIN)</label>
                            <select class="font-select" data-nuance="grain">
                                ${['compact', 'standard', 'aéré'].map(v => `
                                    <option value="${v}" ${substyle.grain === v ? 'selected' : ''}>${v.toUpperCase()}</option>
                                `).join('')}
                            </select>
                        </div>
                        <div class="input-group">
                            <label>TYPOGRAPHIE (REGISTRE)</label>
                            <select class="font-select" data-nuance="registre">
                                ${['caption', 'body', 'heading'].map(v => `
                                    <option value="${v}" ${substyle.registre === v ? 'selected' : ''}>${v.toUpperCase()}</option>
                                `).join('')}
                            </select>
                        </div>
                        <div class="input-group">
                            <label>ACCENT (PRÉSENCE)</label>
                            <select class="font-select" data-nuance="presence">
                                ${['neutre', 'actif', 'muted'].map(v => `
                                    <option value="${v}" ${substyle.presence === v ? 'selected' : ''}>${v.toUpperCase()}</option>
                                `).join('')}
                            </select>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    setupHandlers(container, node, onUpdate) {
        const panel = container.querySelector('#panel-nuance');
        if (!panel) return;

        // Collapsible
        panel.querySelector('.panel-header').addEventListener('click', () => {
            panel.classList.toggle('collapsed');
        });

        // Selects
        panel.querySelectorAll('select[data-nuance]').forEach(select => {
            select.addEventListener('change', (e) => {
                const prop = e.target.dataset.nuance;
                const val = e.target.value;

                if (!node._substyle) node._substyle = {};
                node._substyle[prop] = val;

                console.log(`[Nuance] Updated ${prop} -> ${val}`);
                if (onUpdate) onUpdate(node);
            });
        });
    }
};
