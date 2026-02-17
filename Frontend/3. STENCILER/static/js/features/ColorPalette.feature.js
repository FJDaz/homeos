import StencilerFeature from './base.feature.js';
import Lexicon from '../Lexicon.js';

class ColorPaletteFeature extends StencilerFeature {
  constructor(id = 'color-palette', options = {}) {
    super(id, options);
    this.swatches = [
      '#ef4444', '#f97316', '#f59e0b', '#84cc16',
      '#22c55e', '#10b981', '#06b6d4', '#0ea5e9',
      '#3b82f6', '#6366f1', '#8b5cf6', '#d946ef'
    ];
    this.selectedColor = this.swatches[0];
    this.canvas = options.canvas;
    this.el = null;
  }

  render() {
    return `
        ${this.swatches.map(color => `
          <div class="color-swatch ${color === this.selectedColor ? 'active' : ''}" 
               style="background-color: ${color}" 
               data-color="${color}"></div>
        `).join('')}
    `;
  }

  mount(parentSelector) {
    this.el = document.querySelector(parentSelector);
    if (!this.el) return;

    // Ajoute la classe de conteneur au slot
    const { components } = Lexicon.classes;
    this.el.classList.add('color-palette');

    this.el.innerHTML = this.render();

    this.el.querySelectorAll('.color-swatch').forEach(swatch => {
      swatch.addEventListener('click', () => {
        this.selectedColor = swatch.dataset.color;
        this.el.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('active'));
        swatch.classList.add('active');
        this.applyColor();
      });
    });
  }

  applyColor() {
    if (!this.canvas?.getActiveObject()) return;
    const obj = this.canvas.getActiveObject();
    if (window.colorMode === 'stroke') {
      obj.set('stroke', this.selectedColor);
    } else {
      obj.set('fill', this.selectedColor);
    }
    this.canvas.requestRenderAll();
  }
}

export default ColorPaletteFeature;
