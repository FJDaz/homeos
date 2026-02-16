/**
 * GENOME ENGINE - Version 2.0
 * Rôle : Gestion de l'état de sélection des composants
 * Conformité : Article 5 - Système de Rendu
 */

class GenomeEngine {
    constructor() {
        this.selectedComponents = new Set();
        this.initialized = false;
        console.log('🧬 Genome Engine initialisé (v2.0)');
    }

    initialize() {
        if (this.initialized) return;

        // Initialiser les écouteurs d'événements
        this.setupEventListeners();
        this.initialized = true;
        console.log('🚀 Genome Engine prêt');
    }

    setupEventListeners() {
        // Écouter les changements de checkboxes via le viewer.js global
        // Note: La plupart des listeners sont déjà dans viewer.js
        // On se concentre sur la validation
        console.log('⚓ Listeners de sélection actifs');
    }

    updateSelectedComponents() {
        this.selectedComponents.clear();
        document.querySelectorAll('.comp-checkbox:checked').forEach(cb => {
            this.selectedComponents.add(cb.id);
        });

        // Mettre à jour le bouton de validation
        const validateBtn = document.getElementById('validate-btn');
        if (validateBtn) {
            const count = this.selectedComponents.size;
            validateBtn.innerHTML = `Valider (${count})`;
            validateBtn.disabled = count === 0;
        }
    }

    getSelectedComponents() {
        return Array.from(this.selectedComponents);
    }

    validateSelection() {
        this.updateSelectedComponents();
        if (this.selectedComponents.size === 0) {
            alert('⚠️ Veuillez sélectionner au moins un composant');
            return false;
        }

        console.log('✅ Validation des composants sélectionnés:', this.getSelectedComponents());
        return true;
    }
}

// Initialiser l'engine global
window.genomeEngine = new GenomeEngine();
document.addEventListener('DOMContentLoaded', () => {
    window.genomeEngine.initialize();
});
