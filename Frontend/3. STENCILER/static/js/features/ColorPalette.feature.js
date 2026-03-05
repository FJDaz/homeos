import StencilerFeature from './base.feature.js';
import Lexicon from '../Lexicon.js';

class ColorPaletteFeature extends StencilerFeature {
  constructor(id = 'color-palette', options = {}) {
    super(id, options);
    this.swatches = [
      '#a8c5fc', // --accent-bleu
      '#c4a589', // --accent-terra
      '#a3c4a8', // --accent-vert
      '#f0b8b8', // --accent-rose
      '#c5b8f0', // --accent-violet
      '#f0d0a8', // --accent-ambre
      '#3d3d3c', // --text-primary (noir chaud)
      '#f7f6f2'  // --bg-primary (crème)
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

  init() {
    document.addEventListener('primitive:selected', (e) => {
      this._activePrim = e.detail.el;
      if (this.el) {
        this.el.style.opacity = '1';
        this.el.style.pointerEvents = 'all';
      }
    });

    document.addEventListener('primitive:deselected', () => {
      this._activePrim = null;
      if (this.el) {
        this.el.style.opacity = '0.4';
        this.el.style.pointerEvents = 'none';
      }
    });
  }

  mount(parentSelector) {
    this.el = document.querySelector(parentSelector);
    if (!this.el) return;

    // Ajoute la classe de conteneur au slot
    const { components } = Lexicon.classes;
    this.el.classList.add('color-palette');

    this.el.innerHTML = this.render();

    this.init();

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
    if (this._activePrim) {
      this._activePrim.setAttribute('fill', this.selectedColor);
      return;
    }
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
