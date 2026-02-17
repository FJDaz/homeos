import StencilerFeature from './base.feature.js';

// ComponentsZone.feature.js
class ComponentsZoneFeature extends StencilerFeature {
  constructor(id = 'components-zone') {
    super(id);
  }

  render() {
    return `
      <div class="components-zone">
        <h3>Composants</h3>
        <p>Déposez des éléments ici</p>
      </div>
    `;
  }

  mount(parentSelector) {
    const parent = document.querySelector(parentSelector);
    if (!parent) return;
    // Ne pas écraser le contenu existant, juste ajouter
    const div = document.createElement('div');
    div.innerHTML = this.render();
    parent.appendChild(div);
  }
}

export default ComponentsZoneFeature;
