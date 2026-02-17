/**
 * GENOME ENGINE - Version 2.0
 * Rôle : Gestion de l'état de sélection des composants
 * Conformité : Article 5 - Système de Rendu
 */

class GenomeEngine {
    constructor() {
        this.selectedComponents = new Set();
        this.initialized = false;
        // État du drill-down
        this.drilldownState = { active: false, corpsId: null, corpsName: '', organeId: null, organeName: '' };
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
        
        // Listeners breadcrumb drill-down
        document.getElementById('breadcrumb-back')?.addEventListener('click', () => this.resetDrill());
        document.getElementById('breadcrumb-reset')?.addEventListener('click', () => this.resetDrill());
    }

    // Filtrer les cartes visibles selon l'état drill-down
    applyDrillFilter() {
        const s = this.drilldownState;
        console.log('[DRILL] applyDrillFilter - état:', s);
        let filtered = 0, shown = 0;
        document.querySelectorAll('.comp-card').forEach(card => {
            const cardCorps = card.dataset.corps;
            const level = card.dataset.level;
            // Toujours montrer les Corps (section-corps ne filtre pas)
            if (card.closest('#section-corps')) { card.style.display = ''; shown++; return; }
            // Filtrer par corps actif
            const shouldShow = !s.active || cardCorps === s.corpsId;
            card.style.display = shouldShow ? '' : 'none';
            if (shouldShow) shown++; else filtered++;
            console.log(`[DRILL] ${level} ${card.querySelector('.comp-name')?.textContent} - corpsId: ${cardCorps} vs ${s.corpsId} => ${shouldShow ? 'SHOW' : 'HIDE'}`);
        });
        console.log(`[DRILL] Résultat: ${shown} visibles, ${filtered} masqués`);
        this.updateBreadcrumb();
    }

    updateBreadcrumb() {
        const bar = document.getElementById('breadcrumb-bar');
        const text = document.getElementById('breadcrumb-text');
        if (!bar || !text) return;
        if (!this.drilldownState.active) {
            bar.style.display = 'none';
            return;
        }
        bar.style.display = 'flex';
        text.textContent = 'Tout › ' + this.drilldownState.corpsName;
    }

    drillInto(corpsId, corpsName) {
        console.log('[DRILL] drillInto appelé avec:', corpsId, corpsName);
        this.drilldownState = { active: true, corpsId, corpsName, organeId: null, organeName: '' };
        this.applyDrillFilter();
    }

    resetDrill() {
        this.drilldownState = { active: false, corpsId: null, corpsName: '', organeId: null, organeName: '' };
        this.applyDrillFilter();
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
