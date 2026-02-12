/**
 * PropertyEnforcer — Force les propriétés Genome sur le template CSS
 * 
 * Rôle : Récupérer le CSS généré par le Backend et l'injecter dans le DOM
 * avec !important pour écraser les styles du template.
 */

const PropertyEnforcer = {
    // Configuration
    API_BASE_URL: 'http://localhost:8000',
    STYLE_ID: 'genome-enforced',
    
    /**
     * Initialise l'enforcer et charge le CSS
     * @param {string} genomeId - ID du genome (default: 'default')
     */
    async init(genomeId = 'default') {
        console.log('🔧 PropertyEnforcer initialisé');
        
        try {
            // 1. Fetch le CSS depuis le Backend
            const css = await this.fetchCSS(genomeId);
            
            // 2. Injecter dans le DOM
            this.injectCSS(css);
            
            console.log('✅ Propriétés Genome appliquées avec succès');
            return true;
            
        } catch (error) {
            console.error('❌ PropertyEnforcer erreur:', error);
            return false;
        }
    },
    
    /**
     * Récupère le CSS depuis l'API Backend
     * @param {string} genomeId 
     * @returns {string} CSS avec !important
     */
    async fetchCSS(genomeId) {
        const url = `${this.API_BASE_URL}/api/genome/${genomeId}/css`;
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Le Backend retourne {css: "..."}
        return data.css || '';
    },
    
    /**
     * Injecte le CSS dans le DOM
     * @param {string} css 
     */
    injectCSS(css) {
        // Supprimer l'ancien style s'il existe
        this.cleanup();
        
        // Créer le nouveau style
        const styleEl = document.createElement('style');
        styleEl.id = this.STYLE_ID;
        styleEl.textContent = css;
        
        // Injecter dans le head
        document.head.appendChild(styleEl);
        
        console.log('🎨 CSS Genome injecté dans le DOM');
    },
    
    /**
     * Supprime le style injecté précédemment
     */
    cleanup() {
        const existing = document.getElementById(this.STYLE_ID);
        if (existing) {
            existing.remove();
            console.log('🧹 Ancien CSS Genome supprimé');
        }
    },
    
    /**
     * Rafraîchit le CSS (utile après modification du Genome)
     * @param {string} genomeId 
     */
    async refresh(genomeId = 'default') {
        console.log('🔄 Rafraîchissement des propriétés Genome...');
        return await this.init(genomeId);
    }
};

// Export pour utilisation dans d'autres modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PropertyEnforcer;
}

// Auto-init si DOM prêt
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 PropertyEnforcer auto-init...');
    PropertyEnforcer.init('default');
});
