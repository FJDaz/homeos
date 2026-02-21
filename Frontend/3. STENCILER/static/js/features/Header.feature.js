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
            <div class="header-exports">
                <button class="btn-export secondary" id="btn-export-json" title="Export Machine (JSON)">JSON</button>
                <button class="btn-export primary" id="btn-export-html" title="Export Humain (HTML)">HTML</button>
            </div>
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

        // Export logic
        this.el.querySelector('#btn-export-json')?.addEventListener('click', () => this.exportJSON());
        this.el.querySelector('#btn-export-html')?.addEventListener('click', () => this.exportHTML());
    }

    exportJSON() {
        const genome = window.stencilerApp?.genome;
        if (!genome) return;
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(genome, null, 2));
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", `genome_${new Date().getTime()}.json`);
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
        console.log('📤 Genome exported as JSON');
    }

    exportHTML() {
        const canvasFeature = window.stencilerApp?.features?.get('canvas');
        const svgElement = canvasFeature?.getSVG();
        if (!svgElement) {
            alert("Erreur: Canvas introuvable pour l'export.");
            return;
        }

        const svgData = new XMLSerializer().serializeToString(svgElement);
        const title = document.querySelector('title')?.innerText || 'Stenciler Export';

        const standaloneHTML = `
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>${title} - Export</title>
    <style>
        body { margin: 0; padding: 20px; background: #f7f6f2; display: flex; justify-content: center; align-items: center; min-height: 100vh; font-family: sans-serif; }
        .export-container { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; }
        svg { max-width: 100%; height: auto; display: block; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.05)); }
        .export-footer { margin-top: 20px; text-align: center; font-size: 12px; color: #94a3b8; }
    </style>
</head>
<body>
    <div class="export-container">
        ${svgData}
        <div class="export-footer">Généré par AetherFlow Stenciler V3 — Sullivan Architecture</div>
    </div>
</body>
</html>`;

        const blob = new Blob([standaloneHTML], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `stenciler_presentation_${new Date().getTime()}.html`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        console.log('📤 Standalone HTML Presentation exported');
    }
}

export default HeaderFeature;