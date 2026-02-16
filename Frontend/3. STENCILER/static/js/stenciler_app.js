
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

// 🔽 DRILL-DOWN MANAGER — Navigation hiérarchique N0→N1→N2→N3
const DrillDownManager = {
    API_BASE_URL: 'http://localhost:8000',
    currentPath: null,
    currentLevel: 0,
    breadcrumb: [],
    breadcrumbPaths: [],

    // Initialiser avec le genome
    async init(genome) {
        console.log('🔽 DrillDownManager initialisé');
        this.genome = genome;
        this.currentPath = 'n0[0]'; // Commencer au premier Corps
        this.currentLevel = 0;
        this.breadcrumb = [genome.n0_phases[0]?.name || 'Brainstorm'];
        this.breadcrumbPaths = ['n0[0]'];

        // Afficher le breadcrumb initial
        this.renderBreadcrumb();

        // Configurer le bouton retour
        this.setupBackButton();

        console.log('✅ DrillDown prêt — Niveau 0 (Corps)');
    },

    // Double-clic sur un composant
    async handleDoubleClick(entityId, entityName) {
        console.log(`🔍 Double-clic sur: ${entityName} (${entityId})`);

        // Trouver le path à partir de l'ID
        const path = this.findPathFromId(entityId);
        if (!path) {
            console.warn('❌ Path non trouvé pour:', entityId);
            return;
        }

        console.log('📍 Path trouvé:', path);

        // Vérifier si on peut descendre
        if (this.currentLevel >= 3) {
            console.log('⛔ Niveau maximum atteint (N3)');
            return;
        }

        // Appeler l'API drill-down
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/drilldown/enter`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path: path, child_index: 0 })
            });

            if (!response.ok) {
                const error = await response.json();
                console.warn('⚠️ Pas d\'enfant:', error.detail);
                return;
            }

            const data = await response.json();
            console.log('⬇️ Drill-down réussi:', data);

            // Mettre à jour l'état
            this.currentPath = data.new_path || path;
            this.currentLevel = data.current_level;
            this.breadcrumb = data.breadcrumb;
            this.breadcrumbPaths = data.breadcrumb_paths;

            // Rafraîchir l'affichage
            this.renderBreadcrumb();
            this.renderChildren(data.children);
            this.updateBackButtonVisibility();

        } catch (err) {
            console.error('❌ Erreur drill-down:', err);
        }
    },

    // Remonter d'un niveau
    async goBack() {
        if (this.currentLevel <= 0) {
            console.log('⛔ Déjà au niveau racine');
            return;
        }

        console.log('⬆️ Remontée au niveau précédent');

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/drilldown/exit`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path: this.currentPath })
            });

            if (!response.ok) {
                console.error('❌ Erreur exit:', await response.text());
                return;
            }

            const data = await response.json();
            console.log('⬆️ Drill-up réussi:', data);

            // Mettre à jour l'état
            this.currentPath = data.parent_path;
            this.currentLevel = data.current_level;
            this.breadcrumb = data.breadcrumb;
            this.breadcrumbPaths = data.breadcrumb_paths;

            // Rafraîchir l'affichage
            this.renderBreadcrumb();
            this.renderChildren(data.children);
            this.updateBackButtonVisibility();

        } catch (err) {
            console.error('❌ Erreur drill-up:', err);
        }
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
