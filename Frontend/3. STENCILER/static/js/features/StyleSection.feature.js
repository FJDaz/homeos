import StencilerFeature from './base.feature.js';
import Lexicon from '../Lexicon.js';

class StyleSectionFeature extends StencilerFeature {
    constructor(id = 'style', options = {}) {
        super(id, options);
        this.styles = [
            { id: 'minimal', name: 'Minimal', color: '#64748b' },
            { id: 'corporate', name: 'Corporate', color: '#3b82f6' },
            { id: 'creative', name: 'Créatif', color: '#8b5cf6' },
            { id: 'tech', name: 'Tech', color: '#06b6d4' }
        ];
        this.selectedStyle = null;
        this.el = null;
    }

    render() {
        const { components } = Lexicon.classes;
        return `
            <div class="sidebar-section-header" style="cursor: pointer; display: flex; align-items: center; justify-content: space-between;">
                <h3 style="margin: 0;">styles</h3>
                <span class="section-chevron">▸</span>
            </div>
            <div class="section-content styles-list" style="display: none;">
                ${this.styles.map(style => `
                    <div class="${components.style_card} ${style.id === this.selectedStyle ? components.active_tab : ''}" 
                            data-style="${style.id}"
                            style="border-color: ${style.color}">
                        <span class="style-name">${style.name.toLowerCase()}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }

    mount(parentSelector) {
        this.el = document.querySelector(parentSelector);
        if (!this.el) return;
        this.el.innerHTML = this.render();

        const header = this.el.querySelector('.sidebar-section-header');
        const content = this.el.querySelector('.section-content');
        const chevron = this.el.querySelector('.section-chevron');

        header.addEventListener('click', () => {
            const isHidden = content.style.display === 'none';
            content.style.display = isHidden ? 'block' : 'none';
            chevron.textContent = isHidden ? '▾' : '▸';
        });

        this.el.querySelectorAll(`[${Lexicon.data.style}]`).forEach(item => {
            item.addEventListener('click', () => {
                this.selectedStyle = item.getAttribute(Lexicon.data.style);
                const { components } = Lexicon.classes;
                this.el.querySelectorAll(`.${components.style_card}`).forEach(i => i.classList.remove(components.active_tab));
                item.classList.add(components.active_tab);

                // Sauvegarder
                localStorage.setItem('aetherflow_selected_style', this.selectedStyle);
                console.log('Style sélectionné:', this.selectedStyle);
            });
        });
    }
}

export default StyleSectionFeature;
