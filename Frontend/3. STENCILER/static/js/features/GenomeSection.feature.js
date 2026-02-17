import StencilerFeature from './base.feature.js';
import Lexicon from '../Lexicon.js';

class GenomeSectionFeature extends StencilerFeature {
  constructor(id = 'genome', options = {}) {
    super(id, options);
    this.selectedCorps = new Set();
    this.genome = null;
    this.el = null;
  }

  mount(parentSelector) {
    this.el = document.querySelector(parentSelector);
    if (!this.el) return;
    if (this.genome) {
      this.render();
    }
  }

  init(genome) {
    this.genome = genome;
    if (this.el) {
      this.render();
    }
  }

  render() {
    if (!this.genome || !this.el) return;

    const { components } = Lexicon.classes;
    const phases = this.genome.n0_phases || [];

    // On vide avant de render pour éviter les duplications
    this.el.innerHTML = `
        <h3>Genome (${phases.length} phases)</h3>
        <div class="phases-list">
          ${phases.map(phase => `
            <div class="phase-item ${this.selectedCorps.has(phase.id) ? 'selected' : ''}" data-id="${phase.id}">
              <span class="phase-name">${phase.name}</span>
              <span class="phase-confidence">${Math.round((phase.confidence || 0.5) * 100)}%</span>
            </div>
          `).join('')}
        </div>
    `;

    this.el.querySelectorAll('.phase-item').forEach(item => {
      item.addEventListener('click', () => {
        const phaseId = item.dataset.id;
        if (this.selectedCorps.has(phaseId)) {
          this.selectedCorps.delete(phaseId);
          item.classList.remove('selected');
        } else {
          this.selectedCorps.add(phaseId);
          item.classList.add('selected');
        }
      });
    });
  }
}

export default GenomeSectionFeature;
