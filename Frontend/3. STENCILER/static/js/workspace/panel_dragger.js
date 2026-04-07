/**
 * static/js/workspace/panel_dragger.js
 * Mission 209 — Panels Draggables : Repositionnement libre dans le Workspace
 *
 * Module vanilla JS pour rendre les panels du workspace draggables
 * avec persistance localStorage.
 */

class PanelDragger {
    constructor(panelEl) {
        this.el = panelEl;
        this.isDragging = false;
        this.offset = { x: 0, y: 0 };
        this._init();
    }

    _init() {
        // Handle de drag : header du panel ou panel entier si pas de handle
        const handle = this.el.querySelector('[data-drag-handle]') || this.el;
        handle.style.cursor = 'grab';

        handle.addEventListener('mousedown', (e) => this._onDown(e));
        document.addEventListener('mousemove', (e) => this._onMove(e));
        document.addEventListener('mouseup', () => this._onUp());

        // Touch support
        handle.addEventListener('touchstart', (e) => this._onTouchDown(e), { passive: false });
        document.addEventListener('touchmove', (e) => this._onTouchMove(e), { passive: false });
        document.addEventListener('touchend', () => this._onTouchUp());

        // Restaurer position sauvegardée
        this._restorePosition();
    }

    _onDown(e) {
        // Ignorer si clic sur bouton, input, etc.
        if (e.target.closest('button, input, select, textarea, a, [onclick]')) return;

        this.isDragging = true;
        this.el.style.cursor = 'grabbing';
        this.el.style.zIndex = '9999';
        this.el.style.transition = 'none'; // Désactiver transition pendant le drag

        const rect = this.el.getBoundingClientRect();
        this.offset.x = e.clientX - rect.left;
        this.offset.y = e.clientY - rect.top;
        e.preventDefault();
    }

    _onMove(e) {
        if (!this.isDragging) return;
        this._setPosition(e.clientX, e.clientY);
    }

    _onUp() {
        if (!this.isDragging) return;
        this.isDragging = false;
        this.el.style.cursor = 'grab';
        this.el.style.zIndex = '';
        this.el.style.transition = ''; // Réactiver transition
        this._savePosition();
    }

    // Touch events
    _onTouchDown(e) {
        if (e.target.closest('button, input, select, textarea, a, [onclick]')) return;

        this.isDragging = true;
        this.el.style.zIndex = '9999';
        this.el.style.transition = 'none';

        const touch = e.touches[0];
        const rect = this.el.getBoundingClientRect();
        this.offset.x = touch.clientX - rect.left;
        this.offset.y = touch.clientY - rect.top;
        e.preventDefault();
    }

    _onTouchMove(e) {
        if (!this.isDragging) return;
        const touch = e.touches[0];
        this._setPosition(touch.clientX, touch.clientY);
        e.preventDefault();
    }

    _onTouchUp() {
        if (!this.isDragging) return;
        this.isDragging = false;
        this.el.style.zIndex = '';
        this.el.style.transition = '';
        this._savePosition();
    }

    _setPosition(clientX, clientY) {
        let x = clientX - this.offset.x;
        let y = clientY - this.offset.y;

        // Clamp dans le viewport
        const rect = this.el.getBoundingClientRect();
        const maxX = window.innerWidth - rect.width;
        const maxY = window.innerHeight - rect.height;
        x = Math.max(0, Math.min(x, maxX));
        y = Math.max(0, Math.min(y, maxY));

        this.el.style.position = 'fixed';
        this.el.style.left = `${x}px`;
        this.el.style.top = `${y}px`;
        this.el.style.margin = '0';
    }

    _savePosition() {
        const rect = this.el.getBoundingClientRect();
        const positions = JSON.parse(localStorage.getItem('ws_panel_positions') || '{}');
        positions[this.el.id] = { x: rect.left, y: rect.top };
        localStorage.setItem('ws_panel_positions', JSON.stringify(positions));
    }

    _restorePosition() {
        const positions = JSON.parse(localStorage.getItem('ws_panel_positions') || '{}');
        const pos = positions[this.el.id];
        if (pos) {
            this.el.style.position = 'fixed';
            this.el.style.left = `${pos.x}px`;
            this.el.style.top = `${pos.y}px`;
            this.el.style.margin = '0';
        }
    }

    static resetAll() {
        localStorage.removeItem('ws_panel_positions');
        window.location.reload();
    }
}

// Exposer globalement
window.PanelDragger = PanelDragger;
