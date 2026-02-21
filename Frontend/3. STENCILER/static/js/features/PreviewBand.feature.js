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
        this.el.classList.add('preview-band');

        // [Mission 5C] Clic simple pour ouvrir un Corps
        this.el.addEventListener('click', (e) => {
            const card = e.target.closest('.preview-card');
            if (card) {
                const corpsId = card.dataset.id;

                // Feedback visuel : marquer comme active, les autres à 50% opacity (via CSS .active)
                this.el.querySelectorAll('.preview-card').forEach(c => c.classList.remove('active'));
                card.classList.add('active');

                console.log('[UI] Preview Card Click:', corpsId);
                document.dispatchEvent(new CustomEvent('corps:open', {
                    detail: { corpsId, genome: this.genome }
                }));
            }
        });


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

        // Rendu simple, les écouteurs sont gérés par délégation dans mount()
        this.el.innerHTML = `
            ${phases.map(corps => this.renderCorpsCard(corps)).join('')}
        `;
    }

    renderCorpsCard(corps) {
        const corpType = corps.id.replace('n0_', '');
        let wireframeContent = '';

        switch (corpType) {
            case 'brainstorm':
                wireframeContent = `
                    <div class="corps-wireframe wf-brainstorm">
                        <div class="wf-step active"></div>
                        <div class="wf-step-line"></div>
                        <div class="wf-step"></div>
                        <div class="wf-step-line dim"></div>
                        <div class="wf-step dim"></div>
                    </div>`;
                break;
            case 'backend':
                wireframeContent = `
                    <div class="corps-wireframe wf-backend">
                        <div class="wf-bar" style="height:40%"></div>
                        <div class="wf-bar" style="height:70%"></div>
                        <div class="wf-bar dim" style="height:55%"></div>
                        <div class="wf-bar" style="height:85%"></div>
                    </div>`;
                break;
            case 'frontend':
                wireframeContent = `
                    <div class="corps-wireframe wf-frontend">
                        <div class="wf-frame"></div>
                        <div class="wf-frame accent"></div>
                        <div class="wf-frame"></div>
                    </div>`;
                break;
            case 'deploy':
                wireframeContent = `
                    <div class="corps-wireframe wf-deploy">
                        <div class="wf-launch-btn"></div>
                        <div class="wf-arrow"></div>
                    </div>`;
                break;
            default:
                wireframeContent = `<div class="corps-wireframe"></div>`;
        }

        return `
            <div class="preview-card ${corpType}" data-id="${corps.id}">
                ${wireframeContent}
                <span class="name">${corps.name}</span>
                <span class="count">${corps.n1_sections?.length || 0} organes</span>
            </div>
        `;
    }
}

export default PreviewBandFeature;
