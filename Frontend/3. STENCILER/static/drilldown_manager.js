/**
 * DrillDownManager — Navigation hiérarchique N0→N1→N2→N3
 * 
 * Gère le drill-down double-clic et la navigation dans le Genome.
 */

const DrillDownManager = {
    API_BASE_URL: '',
    currentPath: null,
    currentLevel: 0,
    breadcrumb: [],
    breadcrumbPaths: [],

    async init(genome) {
        console.log('🔽 DrillDownManager initialisé');
        this.genome = genome;
        this.currentPath = 'n0[0]';
        this.currentLevel = 0;
        this.breadcrumb = [genome.n0_phases[0]?.name || 'Brainstorm'];
        this.breadcrumbPaths = ['n0[0]'];

        this.renderBreadcrumb();
        this.setupBackButton();
        this.setupDoubleClick();

        console.log('✅ DrillDown prêt — Niveau 0 (Corps)');
    },

    async handleDoubleClick(entityId, entityName) {
        console.log(`🔍 Double-clic sur: ${entityName} (${entityId})`);

        const path = this.findPathFromId(entityId);
        if (!path) {
            console.warn('❌ Path non trouvé pour:', entityId);
            return;
        }

        console.log('📍 Path trouvé:', path);

        if (this.currentLevel >= 3) {
            console.log('⛔ Niveau maximum atteint (N3)');
            return;
        }

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

            this.currentPath = data.new_path || path;
            this.currentLevel = data.current_level;
            this.breadcrumb = data.breadcrumb;
            this.breadcrumbPaths = data.breadcrumb_paths;

            this.renderBreadcrumb();
            this.renderChildren(data.children);
            this.updateBackButtonVisibility();

        } catch (err) {
            console.error('❌ Erreur drill-down:', err);
        }
    },

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

            this.currentPath = data.parent_path;
            this.currentLevel = data.current_level;
            this.breadcrumb = data.breadcrumb;
            this.breadcrumbPaths = data.breadcrumb_paths;

            this.renderBreadcrumb();
            this.renderChildren(data.children);
            this.updateBackButtonVisibility();

        } catch (err) {
            console.error('❌ Erreur drill-up:', err);
        }
    },

    findPathFromId(entityId) {
        if (this.currentLevel === 0) {
            const index = this.genome.n0_phases.findIndex(c => c.id === entityId);
            if (index !== -1) return `n0[${index}]`;
        }
        return this.currentPath;
    },

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

    setupBackButton() {
        const btn = document.getElementById('btn-back');
        if (btn) {
            btn.addEventListener('click', () => this.goBack());
            if (this.currentLevel > 0) {
                btn.classList.remove('hidden');
            }
            console.log('⬅️ Bouton retour configuré');
        }
    },

    setupDoubleClick() {
        // Le double-clic sera branché par stenciler.js une fois le canvas créé
        console.log('🖱️ Double-clic sera configuré par stenciler.js');
    },

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

    renderChildren(children) {
        console.log('🎨 Rendu des enfants:', children);

        // 🔽 Auto-expand le preview band pour voir les enfants
        if (typeof expandPreviewBand === 'function') {
            expandPreviewBand();
        }

        // 🔽 RENDU SUR LE CANVAS — remplacer l'objet actuel par ses enfants
        if (typeof tarmacCanvas !== 'undefined' && tarmacCanvas) {
            this.renderChildrenOnCanvas(children);
        }

        const previewBand = document.getElementById('preview-band');
        if (!previewBand) return;

        previewBand.innerHTML = children.map((child, index) => {
            const color = child.color || '#64748b';
            // Déterminer le niveau (N0, N1, N2) pour le data attribute
            const niveau = child.n3_atomsets ? 'N2' : (child.n2_features ? 'N1' : 'N0');
            return `
                <div class="preview-card" data-id="${child.id}" data-niveau="${niveau}" draggable="true" style="border-color: ${color}; cursor: grab;">
                    <div class="corps-wireframe" style="background: ${color}20">
                        <div class="wf-step active" style="background: ${color}"></div>
                    </div>
                    <span class="name">${child.name}</span>
                    <span class="count">${child.n3_atomsets?.length || child.n2_features?.length || 0} items</span>
                </div>
            `;
        }).join('');

        previewBand.querySelectorAll('.preview-card').forEach((card, index) => {
            const child = children[index];

            // Double-clic pour drill down
            card.addEventListener('dblclick', () => {
                this.handleDoubleClick(child.id, child.name);
            });

            // 🔽 Drag & Drop (Étape 11)
            card.addEventListener('dragstart', (e) => {
                const niveau = card.dataset.niveau;
                const data = {
                    entity_id: child.id,
                    niveau: niveau,
                    name: child.name,
                    color: child.color || '#64748b'
                };
                e.dataTransfer.setData('application/json', JSON.stringify(data));
                e.dataTransfer.effectAllowed = 'copy';
                card.style.cursor = 'grabbing';
                card.classList.add('dragging');
                console.log('🔽 Drag start preview:', data);
            });

            card.addEventListener('dragend', () => {
                card.style.cursor = 'grab';
                card.classList.remove('dragging');
            });

            // Empêcher sélection texte
            card.style.userSelect = 'none';
            card.style.webkitUserSelect = 'none';
        });

        console.log(`✅ ${children.length} enfants affichés sur canvas et preview band`);
    },

    renderChildrenOnCanvas(children) {
        console.log('🎯 renderChildrenOnCanvas appelé avec', children.length, 'enfants');

        // 🧹 VIDER TOUT LE CANVAS avant de rendre les nouveaux enfants
        // (évite les duplications quand on fait drill up/down)
        const existingObjects = tarmacCanvas.getObjects();
        console.log('🧹 Suppression de', existingObjects.length, 'objets existants');
        existingObjects.forEach(obj => tarmacCanvas.remove(obj));

        // Créer les enfants sur le canvas
        const canvasCenter = { x: tarmacCanvas.width / 2, y: tarmacCanvas.height / 2 };
        const cols = Math.ceil(Math.sqrt(children.length));
        const cellWidth = 280;
        const cellHeight = 180;
        const gap = 40;

        children.forEach((child, index) => {
            const col = index % cols;
            const row = Math.floor(index / cols);
            const x = canvasCenter.x - (cols * (cellWidth + gap)) / 2 + col * (cellWidth + gap) + cellWidth / 2;
            const y = canvasCenter.y - Math.ceil(children.length / cols) * (cellHeight + gap) / 2 + row * (cellHeight + gap) + cellHeight / 2;

            const color = child.color || '#64748b';

            // Rectangle pour l'enfant
            const rect = new fabric.Rect({
                width: cellWidth,
                height: cellHeight,
                fill: color + '20',
                stroke: color,
                strokeWidth: 2,
                rx: 12
            });

            // Texte (bien visible et cliquable)
            const text = new fabric.Text(child.name, {
                fontSize: 14,
                fontWeight: '600',
                fill: '#1f2937',
                top: 15,
                left: cellWidth / 2,
                originX: 'center',
                selectable: true,
                evented: true
            });

            // Groupe
            const group = new fabric.Group([rect, text], {
                left: x - cellWidth / 2,
                top: y - cellHeight / 2,
                selectable: true,
                id: child.id,
                name: child.name
            });

            // Double-clic pour descendre plus loin
            group.on('mousedblclick', () => {
                this.handleDoubleClick(child.id, child.name);
            });

            tarmacCanvas.add(group);
        });

        tarmacCanvas.renderAll();
        console.log(`🎯 ${children.length} enfants rendus sur le canvas`);
        console.log('🎯 Objets sur le canvas:', tarmacCanvas.getObjects().length);
    }
};

// Export pour utilisation
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DrillDownManager;
}
