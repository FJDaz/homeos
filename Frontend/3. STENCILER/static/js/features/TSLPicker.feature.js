import StencilerFeature from './base.feature.js';
import Lexicon from '../Lexicon.js';

class TSLPickerFeature extends StencilerFeature {
  constructor(id = 'tsl-picker', options = {}) {
    super(id, options);
    this.hue = 180;
    this.saturation = 50;
    this.lightness = 50;
    this.el = null;
  }

  render() {
    return `
        <label>Teinte: <span id="hue-value">180</span></label>
        <input type="range" min="0" max="360" value="180" class="hue-slider">
        
        <label>Saturation: <span id="sat-value">50</span>%</label>
        <input type="range" min="0" max="100" value="50" class="sat-slider">
        
        <label>Luminosité: <span id="light-value">50</span>%</label>
        <input type="range" min="0" max="100" value="50" class="light-slider">
        
        <div class="color-preview" style="background-color: hsl(180, 50%, 50%)"></div>
    `;
  }

  mount(parentSelector) {
    this.el = document.querySelector(parentSelector);
    if (!this.el) return;
    this.el.innerHTML = this.render();

    const hueSlider = this.el.querySelector('.hue-slider');
    const satSlider = this.el.querySelector('.sat-slider');
    const lightSlider = this.el.querySelector('.light-slider');
    const preview = this.el.querySelector('.color-preview');

    const updateColor = () => {
      this.hue = parseInt(hueSlider?.value || 180);
      this.saturation = parseInt(satSlider?.value || 50);
      this.lightness = parseInt(lightSlider?.value || 50);

      const hueDisplay = this.el.querySelector('#hue-value');
      const satDisplay = this.el.querySelector('#sat-value');
      const lightDisplay = this.el.querySelector('#light-value');

      if (hueDisplay) hueDisplay.textContent = this.hue;
      if (satDisplay) satDisplay.textContent = this.saturation;
      if (lightDisplay) lightDisplay.textContent = this.lightness;

      if (preview) {
        preview.style.backgroundColor = `hsl(${this.hue}, ${this.saturation}%, ${this.lightness}%)`;
      }
    };

    hueSlider?.addEventListener('input', updateColor);
    satSlider?.addEventListener('input', updateColor);
    lightSlider?.addEventListener('input', updateColor);
  }
}

export default TSLPickerFeature;
