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
            <h3>Styles</h3>
            <div class="styles-list">
                ${this.styles.map(style => `
                    <div class="${components.style_card} ${style.id === this.selectedStyle ? components.active_tab : ''}" 
                            data-style="${style.id}"
                            style="border-color: ${style.color}">
                        <span class="style-name">${style.name}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }

    mount(parentSelector) {
        this.el = document.querySelector(parentSelector);
        if (!this.el) return;
        this.el.innerHTML = this.render();

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
