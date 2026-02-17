import StencilerFeature from './base.feature.js';
import Lexicon from '../Lexicon.js';

class HeaderFeature extends StencilerFeature {
    constructor(id = 'header') {
        super(id);
        this.tabs = ['BRS', 'BKD', 'FRD', 'DPL'];
        this.el = null;
    }

    render() {
        const { components } = Lexicon.classes;
        return `
            <h1>Stenciler</h1>
            <div class="${components.header_actions}">
                ${this.tabs.map(tab =>
            `<button class="${components.tab}" data-section="${tab.toLowerCase()}">${tab}</button>`
        ).join('')}
            </div>
            <button class="${components.theme_toggle}" aria-label="Toggle theme">
                <span class="theme-icon">🌙</span>
            </button>
        `;
    }

    mount(parentSelector) {
        const parent = document.querySelector(parentSelector);
        if (!parent) {
            console.error(`Slot ${parentSelector} non trouvé`);
            return;
        }
        parent.innerHTML = this.render();
        this.el = parent;
    }

    init() {
        if (!this.el) return;
        const { components } = Lexicon.classes;

        // Theme toggle
        const toggle = this.el.querySelector(`.${components.theme_toggle}`);
        if (toggle) {
            toggle.addEventListener('click', () => {
                const isDark = document.documentElement.getAttribute(Lexicon.data.theme) === 'dark';
                document.documentElement.setAttribute(Lexicon.data.theme, isDark ? 'light' : 'dark');
            });
        }

        // Tab navigation
        this.el.querySelectorAll(`.${components.tab}`).forEach(tab => {
            tab.addEventListener('click', (e) => {
                const section = e.target.getAttribute('data-section');
                console.log(`Navigation vers: ${section}`);
            });
        });
    }
}

export default HeaderFeature;