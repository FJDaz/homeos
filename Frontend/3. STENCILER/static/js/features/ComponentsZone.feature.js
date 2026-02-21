import StencilerFeature from './base.feature.js';
import { NuanceUI } from './Nuance.feature.js';

/**
 * ComponentsZoneFeature (Mission 5B)
 * Sidebar contextuelle qui affiche le détail d'un Corps sélectionné au canvas.
 */
class ComponentsZoneFeature extends StencilerFeature {
  constructor(id = 'slot-sidebar-right', options = {}) {
    super(id, options);
    this.genome = null;
    this.currentCorps = null;
    this.currentOrgane = null;
    this.currentCellule = null;
    this.el = null;
    this.currentStyleTarget = 'fill'; // 'fill' or 'stroke'
  }

  mount(parentSelector) {
    this.el = document.querySelector(parentSelector);
    if (!this.el) return;

    this.el.innerHTML = `
            <div class="components-zone-empty">
                <div class="empty-icon">📂</div>
                <div class="empty-text">Cliquez sur un Organe dans le Canvas pour voir ses détails</div>
            </div>
        `;
  }

  init(genome) {
    this.genome = genome;

    // Écouter l'ouverture d'un corps (N0)
    document.addEventListener('corps:open', (e) => {
      const { corpsId } = e.detail;
      this.onCorpsOpen(corpsId);
    });

    // Écouter la sélection d'un organe (N1)
    document.addEventListener('organe:selected', (e) => {
      const { organeId } = e.detail;
      this.onOrganeSelected(organeId);
    });

    // Sync avec drill Canvas (6C)
    document.addEventListener('cellule:selected', (e) => {
      const { celluleId } = e.detail;
      this.onCelluleSelected(celluleId);
    });

    document.addEventListener('corps:drill-back', (e) => {
      const { corpsId } = e.detail;
      this.onCorpsOpen(corpsId);
    });

    // --- Mission 8D-BIS : Real-time Transform Update ---
    document.addEventListener('node:moved', (e) => {
      const { id, x, y } = e.detail;
      this._updateTransformInputs(id, x, y);
    });

    document.addEventListener('snap:config-changed', (e) => {
      const { snapSize } = e.detail;
      this._updateTransformSteps(snapSize);
    });

    // --- Mission 9C : Selection-driven Sidebar Updates ---
    document.addEventListener('canvas:node:selected', (e) => {
      const { nodeData } = e.detail;
      console.log(`[ComponentsZone] Node selected for Nuance: ${nodeData.id}`);
      // If we are already in the right view, we can just re-render panels
      // but it's safer to ensure we have the right context.
      this.render(); // This will call _renderSidebarPanels which now includes Nuance
    });

    console.log('Components Zone initialized (Canvas-Centric)');
  }

  onCorpsOpen(corpsId) {
    if (!this.genome) return;
    const corps = this.genome.n0_phases?.find(p => p.id === corpsId);
    if (!corps) return;

    this.currentCorps = corps;
    this.currentOrgane = null;
    this.currentCellule = null;
    this.render();
  }

  onOrganeSelected(organeId) {
    if (!this.genome) return;

    const organe = this.genome.n0_phases
      ?.flatMap(p => p.n1_sections)
      ?.find(s => s.id === organeId);

    if (!organe) return;

    if (!this.currentCorps || !this.currentCorps.n1_sections.some(s => s.id === organeId)) {
      this.currentCorps = this.genome.n0_phases.find(p => p.n1_sections.some(s => s.id === organeId));
    }

    this.currentOrgane = organe;
    this.currentCellule = null;
    this.render();
  }

  onCelluleSelected(celluleId) {
    if (!this.currentOrgane) return;
    const cellule = this.currentOrgane.n2_features?.find(c => c.id === celluleId);
    if (!cellule) return;

    this.currentCellule = cellule;
    this.render();
  }

  render() {
    if (!this.el || (!this.currentCorps && !this.currentOrgane)) return;

    if (this.currentCellule) {
      this._renderCelluleView();
    } else if (this.currentOrgane) {
      this._renderOrganeView();
    } else {
      this._renderCorpsView();
    }
  }

  _renderCorpsView() {
    const organes = this.currentCorps.n1_sections || [];
    this.el.innerHTML = `
        <div class="components-zone-header cz-corps-header">
            <h3>${this.currentCorps.name.toUpperCase()}</h3>
            <span class="count">${organes.length} organes (N1)</span>
        </div>
        <div class="components-zone-empty">
            <div class="empty-text cz-invite">
                Sélectionnez un organe dans le canvas pour voir ses détails
            </div>
        </div>
    `;
  }

  _renderOrganeView() {
    const cells = this.currentOrgane.n2_features || [];
    const corpsName = this.currentCorps?.name.toUpperCase() || 'GENOME';

    this.el.innerHTML = `
        <div class="components-zone-header">
            <div class="cz-breadcrumb">
                <span class="cz-back" id="cz-back-to-corps">← ${corpsName}</span>
                <span class="cz-separator">›</span>
            </div>
            <h3>${this.currentOrgane.name.toUpperCase()}</h3>
            <span class="count">${cells.length} cellules (N2)</span>
        </div>
        <div class="components-grid clickable">
            <div class="component-card">
                <div class="cells-list">
                    ${cells.map(cell => `
                        <div class="cell-item selectable" data-id="${cell.id}" title="${cell.description || ''}">
                            <span class="cell-dot"></span>
                            <div class="cell-content">
                                <span class="cell-name">${cell.name}</span>
                                ${cell.description ? `<p class="cell-desc">${cell.description}</p>` : ''}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
        <div id="transform-panel-container"></div>
    `;

    this._renderSidebarPanels(this.currentOrgane);

    this.el.querySelector('#cz-back-to-corps')?.addEventListener('click', () => {
      this.currentOrgane = null;
      this.render();
    });

    this.el.querySelectorAll('.cell-item.selectable').forEach(item => {
      item.addEventListener('click', () => this.onCelluleSelected(item.dataset.id));
    });
  }

  _renderCelluleView() {
    const atoms = this.currentCellule.n3_components || [];
    const corpsName = this.currentCorps?.name.toUpperCase() || 'GENOME';
    const organeName = this.currentOrgane?.name.toUpperCase() || 'ORGANE';

    this.el.innerHTML = `
        <div class="components-zone-header">
            <div class="cz-breadcrumb">
                <span class="cz-back" id="cz-back-to-organe">← ${organeName}</span>
                <span class="cz-separator">›</span>
            </div>
            <div class="header-title-row">
                <h3>${this.currentCellule.name.toUpperCase()}</h3>
                <div class="cz-led idle" id="persistence-led" title="Sauvegarde automatique active"></div>
            </div>
        </div>
        <div class="components-grid n3-view">
            ${atoms.length ? atoms.map(atom => `
                <div class="component-card atom-card edit-mode" data-id="${atom.id}">
                    <div class="atom-header">
                        <select class="atom-method-select ${atom.method ? atom.method.toLowerCase() : 'get'}">
                            ${['GET', 'POST', 'PUT', 'DELETE', 'PATCH'].map(m => `
                                <option value="${m}" ${atom.method === m ? 'selected' : ''}>${m}</option>
                            `).join('')}
                        </select>
                        <input type="text" class="atom-name-input" value="${atom.name}" spellcheck="false" placeholder="Nom de l'atome">
                    </div>
                    <div class="atom-endpoint-row">
                        <span class="endpoint-label">URL:</span>
                        <input type="text" class="atom-endpoint-input" value="${atom.endpoint || ''}" placeholder="/api/endpoint" spellcheck="false">
                    </div>
                    <textarea class="atom-desc-input" placeholder="Description UI...">${atom.description_ui || ''}</textarea>
                </div>
            `).join('') : '<div class="empty-text">Aucun atome (N3) défini</div>'}
        </div>
        <div id="transform-panel-container"></div>
    `;

    this._renderSidebarPanels(this.currentCellule);
    this._setupCelluleListeners();
  }

  _setupCelluleListeners() {
    this.el.querySelector('#cz-back-to-organe')?.addEventListener('click', () => {
      this.currentCellule = null;
      this.render();
    });

    const led = this.el.querySelector('#persistence-led');

    this.el.querySelectorAll('.atom-card').forEach(card => {
      const atomId = card.dataset.id;
      const atom = this.currentCellule.n3_components.find(a => a.id === atomId);
      if (!atom) return;

      const inputs = {
        method: card.querySelector('.atom-method-select'),
        name: card.querySelector('.atom-name-input'),
        endpoint: card.querySelector('.atom-endpoint-input'),
        desc: card.querySelector('.atom-desc-input')
      };

      const updateFn = () => {
        atom.method = inputs.method.value;
        atom.name = inputs.name.value;
        atom.endpoint = inputs.endpoint.value;
        atom.description_ui = inputs.desc.value;

        // Visual feedback
        inputs.method.className = `atom-method-select ${atom.method.toLowerCase()}`;
        if (led) {
          led.className = 'cz-led saving';
          setTimeout(() => { if (led) led.className = 'cz-led idle'; }, 2000);
        }

        console.log(`[Persistence] Updated atom ${atomId}`);
        document.dispatchEvent(new CustomEvent('genome:updated', {
          detail: { type: 'n3', id: atomId, genome: this.genome }
        }));
      };

      Object.values(inputs).forEach(input => {
        input.addEventListener('change', updateFn);
        if (input.tagName === 'TEXTAREA') {
          const autoResize = () => {
            input.style.height = 'auto';
            input.style.height = input.scrollHeight + 'px';
          };
          input.addEventListener('input', autoResize);
          autoResize();
        }
      });
    });
  }

  _renderSidebarPanels(obj) {
    const container = this.el.querySelector('#transform-panel-container');
    if (!container || !obj) return;

    const x = Math.round(obj._layout?.x || 0);
    const y = Math.round(obj._layout?.y || 0);
    const w = Math.round(obj._layout?.w || 280);
    const h = Math.round(obj._layout?.h || 60);
    const step = window.stencilerApp?.canvas?.snapSize || 20;

    const fonts = ['Geist', 'Inter', 'monospace', 'serif', 'system-ui'];
    const currentFont = obj._style?.font || 'Geist';
    const strokeWidth = obj._style?.strokeWidth || 1.5;
    const paddingValue = obj._style?.padding || 0;
    const marginValue = obj._style?.margin || 0;

    container.innerHTML = `
        <!-- Panel Transformation -->
        <div class="cz-panel" id="panel-transform">
            <div class="panel-header">
                <span>TRANSFORMATION</span>
                <span class="chevron">▼</span>
            </div>
            <div class="panel-content">
                <div class="transform-grid">
                    <div class="input-group">
                        <label>X</label>
                        <input type="number" id="tr-x" value="${x}" step="${step}">
                    </div>
                    <div class="input-group">
                        <label>Y</label>
                        <input type="number" id="tr-y" value="${y}" step="${step}">
                    </div>
                    
                    <div class="input-group">
                        <label>LARGEUR (L)</label>
                        <div class="inc-dec-group">
                            <button class="inc-btn" data-prop="w" data-val="-20">-</button>
                            <input type="number" id="tr-w" value="${w}" step="${step}" class="small-input">
                            <button class="inc-btn" data-prop="w" data-val="20">+</button>
                        </div>
                    </div>

                    <div class="input-group">
                        <label>HAUTEUR (H)</label>
                        <div class="inc-dec-group">
                            <button class="inc-btn" data-prop="h" data-val="-20">-</button>
                            <input type="number" id="tr-h" value="${h}" step="${step}" class="small-input">
                            <button class="inc-btn" data-prop="h" data-val="20">+</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Panel Disposition (Mission 8G) -->
        <div class="cz-panel" id="panel-disposition">
            <div class="panel-header">
                <span>DISPOSITION</span>
                <span class="chevron">▼</span>
            </div>
            <div class="panel-content">
                <div class="input-group">
                    <label>MARGE INTÉRIEURE (PADDING)</label>
                    <div class="inc-dec-group">
                        <button class="inc-btn" data-prop="padding" data-val="-2">-</button>
                        <input type="number" id="st-padding" value="${paddingValue}" class="small-input">
                        <button class="inc-btn" data-prop="padding" data-val="2">+</button>
                    </div>
                </div>

                <div class="input-group">
                    <label>MARGE EXTÉRIEURE (MARGIN)</label>
                    <div class="inc-dec-group">
                        <button class="inc-btn" data-prop="margin" data-val="-2">-</button>
                        <input type="number" id="st-margin" value="${marginValue}" class="small-input">
                        <button class="inc-btn" data-prop="margin" data-val="2">+</button>
                    </div>
                </div>

                <div class="input-group" style="margin-top: 10px; border-top: 1px solid var(--border-subtle); padding-top: 10px;">
                    <button id="st-apply-all" class="btn-secondary" style="width: 100%; font-size: 10px;">APPLIQUER À TOUT LE CORPS</button>
                </div>
            </div>
        </div>

        <!-- Panel Nuance (Mission 9C) -->
        ${NuanceUI.render(obj)}

        <!-- Panel Snapping -->
        <div class="cz-panel" id="panel-snapping">
            <div class="panel-header">
                <span>MAGNÉTISME (SNAP)</span>
                <span class="chevron">▼</span>
            </div>
            <div class="panel-content">
                <div class="style-grid">
                    <div class="input-group">
                        <label>GRILLE (PX)</label>
                        <select id="sn-size" class="font-select">
                            <option value="5" ${step === 5 ? 'selected' : ''}>5 px</option>
                            <option value="8" ${step === 8 ? 'selected' : ''}>8 px</option>
                            <option value="10" ${step === 10 ? 'selected' : ''}>10 px</option>
                            <option value="20" ${step === 20 ? 'selected' : ''}>20 px (Défaut)</option>
                            <option value="40" ${step === 40 ? 'selected' : ''}>40 px</option>
                        </select>
                    </div>
                </div>
            </div>
        </div>

        <!-- Panel Style -->
        <div class="cz-panel" id="panel-style">
            <div class="panel-header">
                <span>STYLE & COULEURS</span>
                <span class="chevron">▼</span>
            </div>
            <div class="panel-content">
                <div class="style-grid">
                    <div class="fill-stroke-switch">
                        <button class="fs-btn ${this.currentStyleTarget === 'fill' ? 'active' : ''}" data-target="fill">FOND</button>
                        <button class="fs-btn ${this.currentStyleTarget === 'stroke' ? 'active' : ''}" data-target="stroke">CONTOUR</button>
                    </div>
                    
                    <div class="color-nuancier">
                        ${['#ffffff', '#101115', '#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#6366f1', '#14b8a6'].map(c => `
                            <div class="color-chip" style="background:${c}" data-color="${c}"></div>
                        `).join('')}
                    </div>

                    <div class="input-group">
                        <label>SUR MESURE (TSL/HEX)</label>
                        <input type="color" id="st-color-picker" value="${this.currentStyleTarget === 'fill' ? (obj._style?.fill || '#ffffff') : (obj._style?.stroke || '#000000')}">
                    </div>

                    <div class="input-group">
                        <label>ÉPAISSEUR</label>
                        <input type="range" id="st-width" min="0" max="10" step="0.5" value="${strokeWidth}">
                    </div>
                </div>
            </div>
        </div>

        <!-- Panel Typography -->
        <div class="cz-panel" id="panel-typography">
            <div class="panel-header">
                <span>TYPOGRAPHIE</span>
                <span class="chevron">▼</span>
            </div>
            <div class="panel-content">
                <select class="font-select" id="ty-font">
                    ${fonts.map(f => `<option value="${f}" ${currentFont === f ? 'selected' : ''}>${f}</option>`).join('')}
                </select>
            </div>
        </div>
    `;

    this._setupPanelHandlers(obj);
  }

  _setupPanelHandlers(obj) {
    const container = this.el.querySelector('#transform-panel-container');

    // Mission 9C : Nuance Handlers
    NuanceUI.setupHandlers(container, obj, () => {
      document.dispatchEvent(new CustomEvent('genome:updated'));
    });

    // Collapsible logic
    this.el.querySelectorAll('.panel-header').forEach(header => {
      header.addEventListener('click', () => {
        header.parentElement.classList.toggle('collapsed');
      });
    });

    // Transformation
    const trInputs = {
      x: this.el.querySelector('#tr-x'),
      y: this.el.querySelector('#tr-y'),
      w: this.el.querySelector('#tr-w'),
      h: this.el.querySelector('#tr-h')
    };

    const updateLayout = () => {
      if (!obj._layout) obj._layout = {};
      obj._layout.x = parseInt(trInputs.x.value);
      obj._layout.y = parseInt(trInputs.y.value);
      obj._layout.w = parseInt(trInputs.w.value);
      obj._layout.h = parseInt(trInputs.h.value);
      this._persist(obj);
      document.dispatchEvent(new CustomEvent('node:layout-changed', { detail: { id: obj.id, layout: obj._layout } }));
    };
    Object.values(trInputs).forEach(i => i.addEventListener('change', updateLayout));

    // Style - Fill/Stroke
    this.el.querySelectorAll('.fs-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        this.currentStyleTarget = btn.dataset.target;
        this.render(); // Re-render focus
      });
    });

    // Colors
    this.el.querySelectorAll('.color-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        if (!obj._style) obj._style = {};
        if (this.currentStyleTarget === 'fill') obj._style.fill = chip.dataset.color;
        else obj._style.stroke = chip.dataset.color;
        this._persist(obj);
        this._broadcastStyle(obj);
      });
    });

    // Custom Color Picker
    this.el.querySelector('#st-color-picker')?.addEventListener('input', (e) => {
      if (!obj._style) obj._style = {};
      if (this.currentStyleTarget === 'fill') obj._style.fill = e.target.value;
      else obj._style.stroke = e.target.value;
      this._persist(obj);
      this._broadcastStyle(obj);
    });

    // Stroke Width
    this.el.querySelector('#st-width')?.addEventListener('input', (e) => {
      if (!obj._style) obj._style = {};
      obj._style.strokeWidth = parseFloat(e.target.value);
      this._persist(obj);
      this._broadcastStyle(obj);
    });

    // Font
    this.el.querySelector('#ty-font')?.addEventListener('change', (e) => {
      if (!obj._style) obj._style = {};
      obj._style.font = e.target.value;
      this._persist(obj);
      this._broadcastStyle(obj);
    });

    // Snapping
    this.el.querySelector('#sn-size')?.addEventListener('change', (e) => {
      const newSize = parseInt(e.target.value);
      if (window.stencilerApp?.canvas) {
        window.stencilerApp.canvas.snapSize = newSize;
        window.stencilerApp.canvas._updateGridPattern();
        this._updateTransformSteps(newSize);
      }
    });

    // Disposition (Padding / Margin)
    const updateDisposition = (prop, val) => {
      if (!obj._style) obj._style = {};
      obj._style[prop] = Math.max(0, parseInt(val));
      this._persist(obj);
      if (prop === 'padding' && window.stencilerApp?.renderer) {
        const node = document.querySelector(`[data-id="${obj.id}"]`);
        if (node) window.stencilerApp.renderer.updateNode(node, obj._layout.w, obj._layout.h);
      }
    };

    this.el.querySelector('#st-padding')?.addEventListener('change', (e) => updateDisposition('padding', e.target.value));
    this.el.querySelector('#st-margin')?.addEventListener('change', (e) => updateDisposition('margin', e.target.value));

    this.el.querySelectorAll('.inc-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const prop = btn.dataset.prop;
        const diff = parseInt(btn.dataset.val);

        if (prop === 'padding' || prop === 'margin') {
          const input = this.el.querySelector(`#st-${prop}`);
          if (input) {
            const newVal = Math.max(0, parseInt(input.value) + diff);
            input.value = newVal;
            updateDisposition(prop, newVal);
          }
        } else if (prop === 'w' || prop === 'h') {
          const input = this.el.querySelector(`#tr-${prop}`);
          if (input) {
            const newVal = Math.max(10, parseInt(input.value) + diff);
            input.value = newVal;
            // Update transform panel logic
            if (!obj._layout) obj._layout = {};
            obj._layout[prop] = newVal;
            this._persist(obj);
            document.dispatchEvent(new CustomEvent('node:layout-changed', { detail: { id: obj.id, layout: obj._layout } }));
          }
        }
      });
    });

    this.el.querySelector('#st-apply-all')?.addEventListener('click', () => {
      const p = parseInt(this.el.querySelector('#st-padding').value);
      const m = parseInt(this.el.querySelector('#st-margin').value);
      this._applyStyleToCorps(p, m);
    });
  }

  _applyStyleToCorps(padding, margin) {
    if (!this.currentCorps) return;
    const applyRec = (list) => {
      list.forEach(item => {
        item._style = item._style || {};
        item._style.padding = padding;
        item._style.margin = margin;
        if (item.n1_sections) applyRec(item.n1_sections);
        if (item.n2_features) applyRec(item.n2_features);
        if (item.n3_components) applyRec(item.n3_components);
      });
    };
    applyRec([this.currentCorps]);
    document.dispatchEvent(new CustomEvent('genome:updated'));
  }

  _persist(obj) {
    document.dispatchEvent(new CustomEvent('genome:updated'));
  }

  _broadcastStyle(obj) {
    document.dispatchEvent(new CustomEvent('node:style-changed', {
      detail: { id: obj.id, style: obj._style }
    }));
  }

  _updateTransformInputs(id, x, y) {
    const current = this.currentCellule || this.currentOrgane;
    if (current && current.id === id) {
      const inputX = this.el.querySelector('#tr-x');
      const inputY = this.el.querySelector('#tr-y');
      if (inputX) inputX.value = Math.round(x);
      if (inputY) inputY.value = Math.round(y);
    }
  }

  _updateTransformSteps(snapSize) {
    this.el.querySelectorAll('.transform-grid input').forEach(input => {
      input.setAttribute('step', snapSize);
    });
  }
}

export default ComponentsZoneFeature;
