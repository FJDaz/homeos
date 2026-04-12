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
        <div class="sidebar-section-header" style="cursor: pointer; display: flex; align-items: center; justify-content: space-between;">
          <h3 style="margin: 0;">navigation</h3>
          <span class="section-chevron">▾</span>
        </div>
        <div class="section-content" style="display: block;">
          <ul class="breadcrumbs-list" style="list-style: none; padding: 4px 0; margin: 0;">
            ${this.sections.map((id, index) => {
      const name = id.replace('section-', '').toLowerCase();
      return `
                <li style="padding: 2px 0; display: flex; align-items: center; gap: 6px;">
                  ${index > 0 ? '<span style="color: var(--text-muted);">›</span>' : ''}
                  <a href="#${id}" class="${components.tab}" style="text-decoration: none; color: inherit; font-size: 13px;">${name}</a>
                </li>
              `;
    }).join('')}
          </ul>
        </div>
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

    const header = this.el.querySelector('.sidebar-section-header');
    const content = this.el.querySelector('.section-content');
    const chevron = this.el.querySelector('.section-chevron');

    header.addEventListener('click', () => {
      const isHidden = content.style.display === 'none';
      content.style.display = isHidden ? 'block' : 'none';
      chevron.textContent = isHidden ? '▾' : '▸';
    });

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
