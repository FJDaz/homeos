// base.feature.js
class StencilerFeature {
  /**
   * Constructor for StencilerFeature
   * @param {string} id - Unique identifier for the feature
   * @param {object} options - Optional parameters for the feature
   */
  constructor(id, options = {}) {
    this.id = id;
    this.options = options;
  }

  /**
   * Render the feature
   * @throws {Error} Not implemented
   */
  render() {
    throw new Error('Not implemented');
  }

  /**
   * Mount the feature to a parent element
   * @param {string} parentSelector - CSS selector for the parent element
   */
  mount(parentSelector) {
    // Default: render HTML into parent
    const parent = document.querySelector(parentSelector);
    if (parent && this.render) {
      parent.innerHTML = this.render();
    }
  }

  /**
   * Initialize the feature
   * @param {object} data - Optional data (e.g., genome)
   */
  init(data) {
    // Default: no-op
    console.log(`[Feature ${this.id}] initialized`);
  }

  /**
   * Destroy the feature
   * @throws {Error} Not implemented
   */
  destroy() {
    throw new Error('Not implemented');
  }
}

export default StencilerFeature;