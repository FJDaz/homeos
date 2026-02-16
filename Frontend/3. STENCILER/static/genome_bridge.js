// GENOME BRIDGE - Connecte le Genome Render au Stenciler
// Ce fichier gère la transition entre les vues

(function() {
    'use strict';
    
    console.log('Genome Bridge initialisé');
    
    // État global de navigation
    const homeosState = {
        currentView: 'brainstorm',     // brainstorm | style_picker | upload | stenciler
        genome: null,                  // Genome validé
        styleSelected: null,           // ID du style choisi
        templateData: null,            // Données template uploadé
        
        // Transition vers Stenciler
        switchToStenciler() {
            console.log('Transition vers Stenciler...');
            this.currentView = 'stenciler';
            
            // Masquer Style Picker/Upload
            const styleZone = document.querySelector('.style-picker-zone');
            const uploadZone = document.querySelector('.upload-zone');
            if (styleZone) styleZone.style.display = 'none';
            if (uploadZone) uploadZone.style.display = 'none';
            
            // Afficher Stenciler
            const stencilerZone = document.querySelector('.stenciler-zone');
            if (stencilerZone) {
                stencilerZone.style.display = 'block';
                
                // Réinitialiser le canvas
                requestAnimationFrame(() => {
                    if (window.stencilerAPI) {
                        window.stencilerAPI.reinitCanvas();
                    }
                });
            }
            
            // Mettre à jour la sidebar
            updateSidebarNavigation('stenciler');
            
            // Charger le genome dans le Stenciler
            if (this.genome && window.stencilerAPI) {
                window.stencilerAPI.loadGenome(this.genome);
            }
            
            // Dispatcher event
            window.dispatchEvent(new CustomEvent('switchedToStenciler', {
                detail: { 
                    view: 'stenciler',
                    style: this.styleSelected,
                    genome: this.genome
                }
            }));
        },
        
        // Clic sur un style
        onStyleClicked(styleId) {
            console.log('Style sélectionné:', styleId);
            this.styleSelected = styleId;
            this.switchToStenciler();
        },
        
        // Upload template
        onTemplateUploaded(templateData) {
            console.log('Template uploadé');
            this.templateData = templateData;
            this.switchToStenciler();
        },
        
        // Retour à la vue précédente
        goBack() {
            if (this.currentView === 'stenciler') {
                this.currentView = 'style_picker';
                
                // Masquer Stenciler
                const stencilerZone = document.querySelector('.stenciler-zone');
                if (stencilerZone) stencilerZone.style.display = 'none';
                
                // Afficher Style Picker
                const styleZone = document.querySelector('.style-picker-zone');
                if (styleZone) styleZone.style.display = 'block';
                
                updateSidebarNavigation('style_picker');
            }
        },
        
        // Charger le genome depuis le render
        loadGenome(genomeData) {
            console.log('Genome chargé:', genomeData);
            this.genome = genomeData;
            
            // Si le Stenciler est déjà visible, charger immédiatement
            if (this.currentView === 'stenciler' && window.stencilerAPI) {
                window.stencilerAPI.loadGenome(genomeData);
            }
        }
    };
    
    // Mettre à jour la navigation sidebar
    function updateSidebarNavigation(view) {
        const breadcrumb = document.getElementById('breadcrumb');
        const backBtn = document.getElementById('btn-back');
        
        const crumbs = {
            brainstorm: 'Brainstorm',
            style_picker: 'Brainstorm › Style',
            upload: 'Brainstorm › Upload',
            stenciler: 'Brainstorm › Style › Stenciler'
        };
        
        if (breadcrumb) {
            breadcrumb.textContent = crumbs[view] || view;
        }
        
        if (backBtn) {
            backBtn.classList.toggle('hidden', view === 'brainstorm');
        }
        
        console.log('Navigation mise à jour:', view);
    }
    
    // Initialiser les event listeners
    function initBridge() {
        // Écouter les clics sur les cartes de style
        document.querySelectorAll('.style-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const styleId = e.currentTarget.dataset.styleId || 
                               e.currentTarget.dataset.style || 
                               'default';
                homeosState.onStyleClicked(styleId);
            });
        });
        
        // Bouton retour
        const backBtn = document.getElementById('btn-back');
        if (backBtn) {
            backBtn.addEventListener('click', () => {
                homeosState.goBack();
            });
        }
        
        // Écouter l'événement genomeValidated depuis le render
        window.addEventListener('genomeValidated', (e) => {
            console.log('Genome validé reçu:', e.detail);
            if (e.detail && e.detail.genome) {
                homeosState.loadGenome(e.detail.genome);
            }
        });
        
        console.log('Bridge initialisé - En attente de interactions');
    }
    
    // Démarrer quand le DOM est prêt
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initBridge);
    } else {
        initBridge();
    }
    
    // Exposer globalement
    window.homeosState = homeosState;
    window.updateSidebarNavigation = updateSidebarNavigation;
    
})();
