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
        <div class="sidebar-section-header" style="cursor: pointer; display: flex; align-items: center; justify-content: space-between;">
          <h3 style="margin: 0;">genome (${phases.length})</h3>
          <span class="section-chevron">▾</span>
        </div>
        <div class="section-content phases-list" style="display: block;">
          ${phases.map(phase => `
            <div class="phase-item ${this.selectedCorps.has(phase.id) ? 'selected' : ''}" data-id="${phase.id}">
              <span class="phase-name">${phase.name}</span>
              <span class="phase-confidence">${Math.round((phase.confidence || 0.5) * 100)}%</span>
            </div>
          `).join('')}
        </div>
    `;

    const header = this.el.querySelector('.sidebar-section-header');
    const content = this.el.querySelector('.section-content');
    const chevron = this.el.querySelector('.section-chevron');

    header.addEventListener('click', () => {
      const isHidden = content.style.display === 'none';
      content.style.display = isHidden ? 'block' : 'none';
      chevron.textContent = isHidden ? '▾' : '▸';
    });

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
