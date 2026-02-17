import StencilerFeature from './base.feature.js';

// APIStatus.feature.js
class APIStatusFeature extends StencilerFeature {
  constructor(id = 'api-status', options = {}) {
    super(id, options);
    this.status = 'disconnected';
  }

  render() {
    return `<div class="api-status" data-status="${this.status}">API: ${this.status}</div>`;
  }

  mount(parentSelector) {
    const parent = document.querySelector(parentSelector);
    if (!parent) return;
    parent.innerHTML = this.render();
  }

  setStatus(status) {
    this.status = status;
    const el = document.querySelector('.api-status');
    if (el) {
      el.dataset.status = status;
      el.textContent = `API: ${status}`;
    }
  }
}

export default APIStatusFeature;
