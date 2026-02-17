
// 🌓 GESTION DU THÈME JOUR/NUIT avec transition fluide
const ThemeManager = {
    init() {
        // Récupérer le thème sauvegardé ou défaut (jour)
        const savedTheme = localStorage.getItem('aetherflow_theme') || 'light';
        this.applyTheme(savedTheme);

        // Écouteur sur le bouton
        const toggleBtn = document.getElementById('theme-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggle());
        }
    },

    toggle() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.applyTheme(newTheme);

        // Feedback visuel
        console.log(`🌓 Thème basculé: ${newTheme === 'dark' ? 'Mode nuit' : 'Mode jour'}`);
    },

    applyTheme(theme) {
        const html = document.documentElement;
        const toggleBtn = document.getElementById('theme-toggle');
        const iconSpan = toggleBtn?.querySelector('.theme-icon');
        const textSpan = toggleBtn?.querySelector('.theme-text');

        if (theme === 'dark') {
            html.setAttribute('data-theme', 'dark');
            if (iconSpan) iconSpan.textContent = '🌙';
            if (textSpan) textSpan.textContent = 'Mode jour';
        } else {
            html.removeAttribute('data-theme');
            if (iconSpan) iconSpan.textContent = '☀️';
            if (textSpan) textSpan.textContent = 'Mode nuit';
        }

        // Sauvegarder la préférence
        localStorage.setItem('aetherflow_theme', theme);
    }
};

// Initialiser le thème dès que le DOM est prêt
document.addEventListener('DOMContentLoaded', () => {
    ThemeManager.init();
});

// 🔽 DRILL-DOWN MANAGER — Navigation hiérarchique N0→N1→N2→N3 (CLIENT-SIDE)
const DrillDownManager = {
    genome: null,
    currentLevel: 0, // 0 = Corps, 1 = Organes, 2 = Cellules, 3 = Atomes
    currentEntity: null, // L'entité actuellement sélectionnée
    breadcrumb: [],
    originalRenderPreviews: null, // Sauvegarde de la fonction originale

    // Initialiser avec le genome
    async init(genome) {
        console.log('🔽 DrillDownManager initialisé (CLIENT-SIDE)');
        this.genome = genome;
        this.currentLevel = 0;
        this.currentEntity = null; // null = niveau racine (tous les corps)
        this.breadcrumb = ['Genome'];

        // Afficher le breadcrumb initial
        this.renderBreadcrumb();

        // Configurer le bouton retour
        this.setupBackButton();

        console.log('✅ DrillDown prêt — Niveau 0 (Corps)');
    },

    // 🔽 DESCENDRE dans un Corps spécifique
    drillToCorps(corpsId, corpsName) {
        console.log(`[DRILL] Descente dans ${corpsName} (${corpsId})`);
        
        // Trouver le corps dans le genome
        const corps = this.genome.n0_phases.find(c => c.id === corpsId);
        if (!corps) {
            console.error('[DRILL] Corps non trouvé:', corpsId);
            return;
        }

        // Mettre à jour l'état
        this.currentLevel = 1;
        this.currentEntity = corps;
        this.breadcrumb.push(corpsName);

        // Afficher les organes de ce corps
        this.renderOrganes(corps);
        this.renderBreadcrumb();
        this.updateBackButtonVisibility();

        console.log(`[DRILL] Niveau 1 - ${corps.n1_sections?.length || 0} organes`);
    },

    // 🔽 DESCENDRE dans un Organe
    drillToOrgane(organeId, organeName) {
        console.log(`[DRILL] Descente dans ${organeName} (${organeId})`);
        
        const organe = this.currentEntity?.n1_sections?.find(o => o.id === organeId);
        if (!organe) {
            console.error('[DRILL] Organe non trouvé:', organeId);
            return;
        }

        this.currentLevel = 2;
        this.currentEntity = organe;
        this.breadcrumb.push(organeName);

        this.renderCellules(organe);
        this.renderBreadcrumb();
        this.updateBackButtonVisibility();

        console.log(`[DRILL] Niveau 2 - ${organe.n2_features?.length || 0} cellules`);
    },

    // 🔽 DESCENDRE dans une Cellule
    drillToCellule(celluleId, celluleName) {
        console.log(`[DRILL] Descente dans ${celluleName} (${celluleId})`);
        
        const cellule = this.currentEntity?.n2_features?.find(c => c.id === celluleId);
        if (!cellule) {
            console.error('[DRILL] Cellule non trouvée:', celluleId);
            return;
        }

        this.currentLevel = 3;
        this.currentEntity = cellule;
        this.breadcrumb.push(celluleName);

        this.renderAtomes(cellule);
        this.renderBreadcrumb();
        this.updateBackButtonVisibility();

        console.log(`[DRILL] Niveau 3 - ${cellule.n3_components?.length || 0} atomes`);
    },

    // ⬆️ REMONTER d'un niveau
    goBack() {
        console.log('[DRILL] Remontée au niveau', this.currentLevel - 1);
        
        if (this.currentLevel <= 1) {
            // Retour au niveau 0 (tous les corps)
            this.currentLevel = 0;
            this.currentEntity = null;
            this.breadcrumb = ['Genome'];
            
            // Restaurer l'affichage original des 4 corps
            if (window.renderPreviews) {
                window.renderPreviews();
            }
        } else if (this.currentLevel === 2) {
            // Retour au niveau 1 (organes du corps parent)
            const corps = this.genome.n0_phases.find(c => 
                c.n1_sections?.some(o => o.id === this.currentEntity.id)
            );
            this.currentLevel = 1;
            this.currentEntity = corps;
            this.breadcrumb.pop();
            this.renderOrganes(corps);
        } else if (this.currentLevel === 3) {
            // Retour au niveau 2 (cellules de l'organe parent)
            const corps = this.genome.n0_phases.find(c => 
                c.n1_sections?.some(o => 
                    o.n2_features?.some(c => c.id === this.currentEntity.id)
                )
            );
            const organe = corps?.n1_sections?.find(o => 
                o.n2_features?.some(c => c.id === this.currentEntity.id)
            );
            this.currentLevel = 2;
            this.currentEntity = organe;
            this.breadcrumb.pop();
            this.renderCellules(organe);
        }

        this.renderBreadcrumb();
        this.updateBackButtonVisibility();
    },

    // Afficher les organes d'un corps
    renderOrganes(corps) {
        const band = document.getElementById('preview-band');
        if (!band) return;

        const organes = corps.n1_sections || [];
        
        band.innerHTML = organes.map(organe => `
            <div class="preview-card organe" data-id="${organe.id}">
                <div class="corps-wireframe wf-generic">
                    <div class="wf-icon">⚙️</div>
                </div>
                <span class="name">${organe.name}</span>
                <span class="count">${organe.n2_features?.length || 0} cellules</span>
            </div>
        `).join('');

        // Ajouter les écouteurs
        band.querySelectorAll('.preview-card').forEach(card => {
            const organeId = card.dataset.id;
            const organe = organes.find(o => o.id === organeId);
            
            card.addEventListener('dblclick', () => {
                this.drillToOrgane(organeId, organe?.name);
            });
        });

        console.log(`[DRILL] ${organes.length} organes affichés`);
    },

    // Afficher les cellules d'un organe
    renderCellules(organe) {
        const band = document.getElementById('preview-band');
        if (!band) return;

        const cellules = organe.n2_features || [];
        
        band.innerHTML = cellules.map(cellule => `
            <div class="preview-card cellule" data-id="${cellule.id}">
                <div class="corps-wireframe wf-generic">
                    <div class="wf-icon">🔧</div>
                </div>
                <span class="name">${cellule.name}</span>
                <span class="count">${cellule.n3_components?.length || 0} atomes</span>
            </div>
        `).join('');

        band.querySelectorAll('.preview-card').forEach(card => {
            const celluleId = card.dataset.id;
            const cellule = cellules.find(c => c.id === celluleId);
            
            card.addEventListener('dblclick', () => {
                this.drillToCellule(celluleId, cellule?.name);
            });
        });

        console.log(`[DRILL] ${cellules.length} cellules affichées`);
    },

    // Afficher les atomes d'une cellule
    renderAtomes(cellule) {
        const band = document.getElementById('preview-band');
        if (!band) return;

        const atomes = cellule.n3_components || [];
        
        band.innerHTML = atomes.map(atome => `
            <div class="preview-card atome" data-id="${atome.id}">
                <div class="corps-wireframe wf-generic">
                    <div class="wf-icon">⚛️</div>
                </div>
                <span class="name">${atome.name}</span>
                <span class="count">${atome.method || 'GET'}</span>
            </div>
        `).join('');

        console.log(`[DRILL] ${atomes.length} atomes affichés`);
    },

    // Trouver le path à partir d'un ID
    findPathFromId(entityId) {
        // Si on est au niveau 0 (Corps), chercher dans n0_phases
        if (this.currentLevel === 0) {
            const index = this.genome.n0_phases.findIndex(c => c.id === entityId);
            if (index !== -1) return `n0[${index}]`;
        }
        // Sinon utiliser le path stocké dans l'objet
        return this.currentPath;
    },

    // Afficher le breadcrumb
    renderBreadcrumb() {
        const container = document.getElementById('breadcrumb');
        if (!container) {
            console.warn('⚠️ Conteneur breadcrumb non trouvé');
            return;
        }

        container.innerHTML = this.breadcrumb.map((name, index) => {
            const isLast = index === this.breadcrumb.length - 1;
            return `<span class="breadcrumb-item ${isLast ? 'active' : ''}">${name}</span>`;
        }).join(' <span class="breadcrumb-separator">></span> ');

        console.log('🍞 Breadcrumb mis à jour:', this.breadcrumb.join(' > '));
    },

    // Configurer le bouton retour
    setupBackButton() {
        const btn = document.getElementById('btn-back');
        if (btn) {
            btn.addEventListener('click', () => this.goBack());
            // Afficher le bouton si on n'est pas au niveau 0
            if (this.currentLevel > 0) {
                btn.classList.remove('hidden');
            }
            console.log('⬅️ Bouton retour configuré');
        }
    },

    // Mettre à jour la visibilité du bouton retour
    updateBackButtonVisibility() {
        const btn = document.getElementById('btn-back');
        if (btn) {
            if (this.currentLevel > 0) {
                btn.classList.remove('hidden');
            } else {
                btn.classList.add('hidden');
            }
        }
    },

    // Afficher les enfants dans le canvas
    renderChildren(children) {
        console.log('🎨 Rendu des enfants:', children);

        // Mettre à jour le preview band avec les nouveaux éléments
        const previewBand = document.getElementById('preview-band');
        if (!previewBand) return;

        // Vider et reconstruire avec les enfants
        previewBand.innerHTML = children.map((child, index) => {
            const color = child.color || '#64748b';
            return `
                <div class="preview-card" data-id="${child.id}" style="border-color: ${color}">
                    <div class="corps-wireframe" style="background: ${color}20">
                        <div class="wf-step active" style="background: ${color}"></div>
                    </div>
                    <span class="name">${child.name}</span>
                    <span class="count">${child.n3_atomsets?.length || child.n2_features?.length || 0} items</span>
                </div>
            `;
        }).join('');

        // Ajouter les écouteurs de double-clic
        previewBand.querySelectorAll('.preview-card').forEach((card, index) => {
            card.addEventListener('dblclick', () => {
                const child = children[index];
                this.handleDoubleClick(child.id, child.name);
            });
        });

        console.log(`✅ ${children.length} enfants affichés avec double-clic activé`);
    }
};

// 🚀 Récupération des données depuis la page Genome
document.addEventListener('DOMContentLoaded', async () => {
    const selectedStyle = localStorage.getItem('aetherflow_selected_style');
    const timestamp = localStorage.getItem('aetherflow_timestamp');

    if (selectedStyle) {
        console.log('🎨 Style récupéré:', selectedStyle);

        // Mettre à jour l'indicateur de style dans le header
        const styleIndicator = document.querySelector('.style-indicator');
        if (styleIndicator) {
            styleIndicator.className = 'style-indicator ' + selectedStyle;
            styleIndicator.querySelector('span:last-child').textContent = selectedStyle;
        }

        // 🧬 Fetch le genome depuis l'API Backend (localhost:8000)
        try {
            const response = await fetch('/api/genome');
            const data = await response.json();
            const genome = data.genome || data;  // Supporte les deux formats
            console.log('🧬 Genome chargé via API Backend:', genome.n0_phases?.length || 0, 'corps');

            // Stocker pour utilisation par stenciler.js
            window.aetherflowState = {
                genome: genome,
                style: selectedStyle,
                timestamp: parseInt(timestamp || '0')
            };

            // 🔽 Initialiser le DrillDownManager
            await DrillDownManager.init(genome);
        } catch (err) {
            console.error('❌ Erreur chargement genome:', err);
        }

        // 🎭 Illusion : scroll vers le bas comme si on continuait la page
        setTimeout(() => {
            window.scrollTo({
                top: document.body.scrollHeight,
                behavior: 'smooth'
            });
            console.log('🎭 Scroll automatique vers le bas (illusion de continuité)');
        }, 500);

    } else {
        console.log('ℹ️ Aucun style sélectionné — mode standalone');
    }
});

// Exporter DrillDownManager globalement pour stenciler.js
window.DrillDownManager = DrillDownManager;
