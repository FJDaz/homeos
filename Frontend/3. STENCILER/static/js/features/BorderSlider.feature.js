import StencilerFeature from './base.feature.js';
import Lexicon from '../Lexicon.js';

class BorderSliderFeature extends StencilerFeature {
  constructor(id = 'border-slider', options = {}) {
    super(id, options);
    this.canvas = options.canvas;
    this.value = 0;
    this.el = null;
  }

  render() {
    return `
        <label>Bordure: <span id="border-value">0px</span></label>
        <input type="range" min="0" max="10" value="0" class="border-range">
    `;
  }

  mount(parentSelector) {
    this.el = document.querySelector(parentSelector);
    if (!this.el) return;

    // Ajoute la classe de conteneur au slot
    this.el.classList.add('border-slider');

    this.el.innerHTML = this.render();

    const slider = this.el.querySelector('.border-range');
    const valueDisplay = this.el.querySelector('#border-value');

    if (slider) {
      slider.addEventListener('input', (e) => {
        this.value = parseInt(e.target.value);
        if (valueDisplay) valueDisplay.textContent = `${this.value}px`;
        this.applyBorder();
      });
    }
  }

  applyBorder() {
    if (!this.canvas?.getActiveObject()) return;
    const obj = this.canvas.getActiveObject();
    obj.set('strokeWidth', this.value);
    this.canvas.requestRenderAll();
  }
}

export default BorderSliderFeature;
