import StencilerFeature from './base.feature.js';

// PreviewBand.feature.js
class PreviewBandFeature extends StencilerFeature {
    constructor(id = 'preview-band', options = {}) {
        super(id, options);
        this.corps = [];
        this.currentLevel = 0;
        this.currentEntity = null;
        this.el = null;
        this.genome = null;
    }

    mount(parentSelector) {
        this.el = document.querySelector(parentSelector);
        if (!this.el) return;

        // Ajoute la classe de conteneur au slot
        this.el.classList.add('preview-band');

        if (this.genome) {
            this.renderCorps();
        }
    }

    init(genome) {
        this.genome = genome;
        if (this.el) {
            this.renderCorps();
        }
    }

    renderCorps() {
        if (!this.el || !this.genome) return;

        const phases = this.genome.n0_phases || [];
        this.currentLevel = 0;

        this.el.innerHTML = `
            ${phases.map(corps => this.renderCorpsCard(corps)).join('')}
        `;

        // Ajouter les écouteurs
        this.el.querySelectorAll('.preview-card').forEach(card => {
            const corpsId = card.dataset.id;

            // Drag
            card.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('application/json', JSON.stringify({
                    type: 'corps',
                    id: corpsId,
                    label: card.querySelector('.name')?.textContent
                }));
                card.classList.add('dragging');
            });

            card.addEventListener('dragend', () => {
                card.classList.remove('dragging');
            });

            // Double-clic pour drill-down
            card.addEventListener('dblclick', () => {
                this.drillToCorps(corpsId);
            });
        });
    }

    renderCorpsCard(corps) {
        const corpType = corps.id.replace('n0_', '');
        return `
            <div class="preview-card ${corpType}" draggable="true" data-id="${corps.id}">
                <div class="corps-wireframe wf-${corpType}">
                    <div class="wf-indicator"></div>
                </div>
                <span class="name">${corps.name}</span>
                <span class="count">${corps.n1_sections?.length || 0} organes</span>
            </div>
        `;
    }

    drillToCorps(corpsId) {
        const corps = this.genome.n0_phases.find(c => c.id === corpsId);
        if (!corps || !this.el) return;

        this.currentLevel = 1;
        this.currentEntity = corps;

        const organes = corps.n1_sections || [];

        this.el.innerHTML = `
            <button class="btn-back">← Retour</button>
            ${organes.map(organe => `
                <div class="preview-card organe" data-id="${organe.id}">
                    <div class="corps-wireframe wf-generic">
                        <div class="wf-icon">⚙️</div>
                    </div>
                    <span class="name">${organe.name}</span>
                    <span class="count">${organe.n2_features?.length || 0} cellules</span>
                </div>
            `).join('')}
        `;

        // Bouton retour
        this.el.querySelector('.btn-back')?.addEventListener('click', () => {
            this.renderCorps();
        });

        // Drill-down sur organes
        this.el.querySelectorAll('.preview-card').forEach(card => {
            card.addEventListener('dblclick', () => {
                console.log('Drill to organe:', card.dataset.id);
            });
        });

        // Mettre à jour breadcrumb via l'app
        if (window.stencilerApp) {
            window.stencilerApp.updateBreadcrumb?.([corps.name]);
        }
    }
}

export default PreviewBandFeature;
