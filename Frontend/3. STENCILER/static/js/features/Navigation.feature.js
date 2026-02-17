import StencilerFeature from './base.feature.js';
import Lexicon from '../Lexicon.js';

class NavigationFeature extends StencilerFeature {
  constructor(id = 'navigation', options = {}) {
    super(id, options);
    this.observer = null;
    this.sections = ['section-genome', 'section-style', 'section-stenciler'];
  }

  render() {
    const { components } = Lexicon.classes;
    return `
        ${this.sections.map(id => {
      const name = id.replace('section-', '').charAt(0).toUpperCase() + id.replace('section-', '').slice(1);
      return `<a href="#${id}" class="${components.tab}">${name}</a>`;
    }).join('')}
    `;
  }

  mount(parentSelector) {
    const parent = document.querySelector(parentSelector);
    if (!parent) return;

    // Ajoute la classe de conteneur au slot lui-même
    const { containers } = Lexicon.classes;
    parent.classList.add(containers.navigation);

    parent.innerHTML = this.render();
    this.el = parent;
    this.setupListeners();
  }

  setupListeners() {
    const { components } = Lexicon.classes;
    if (!this.el) return;

    this.el.querySelectorAll(`.${components.tab}`).forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const sectionId = link.getAttribute('href').substring(1);
        this.scrollToSection(sectionId);
      });
    });
  }

  init() {
    this.setupIntersectionObserver();
  }

  scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
      section.scrollIntoView({ behavior: 'smooth' });
      this.updateActiveTab(sectionId);
    }
  }

  updateActiveTab(sectionId) {
    const { components } = Lexicon.classes;
    if (!this.el) return;

    this.el.querySelectorAll(`.${components.tab}`).forEach(tab => {
      const tabSection = tab.getAttribute('href')?.substring(1);
      tab.classList.toggle(components.active_tab, tabSection === sectionId);
    });
  }

  setupIntersectionObserver() {
    this.observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.updateActiveTab(entry.target.id);
        }
      });
    }, { threshold: 0.5 });

    this.sections.forEach(id => {
      const section = document.getElementById(id);
      if (section) this.observer.observe(section);
    });
  }

  destroy() {
    if (this.observer) this.observer.disconnect();
  }
}

export default NavigationFeature;
