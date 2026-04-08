/**
 * static/js/workspace/panel_dragger.js
 * Panels Draggables : Repositionnement libre dans le Workspace
 *
 * Architecture : un seul listener global document par type.
 * Suppression du click parasite après un drag (onclick du handle).
 */

(function() {
    'use strict';

    var activeDragger = null;

    // --- Global document listeners (single instance) ---
    document.addEventListener('mousemove', function(e) {
        if (!activeDragger) return;
        activeDragger._setPosition(e.clientX, e.clientY);
    });

    document.addEventListener('mouseup', function() {
        if (!activeDragger) return;
        activeDragger._finish();
    });

    document.addEventListener('touchmove', function(e) {
        if (!activeDragger || !e.touches[0]) return;
        e.preventDefault();
        activeDragger._setPosition(e.touches[0].clientX, e.touches[0].clientY);
    }, { passive: false });

    document.addEventListener('touchend', function() {
        if (!activeDragger) return;
        activeDragger._finish();
    });

    class PanelDragger {
        constructor(panelEl) {
            this.el = panelEl;
            this.isDragging = false;
            this.didDrag = false;
            this.offset = { x: 0, y: 0 };
            this._init();
        }

        _init() {
            var self = this;
            var handle = this.el.querySelector('[data-drag-handle]') || this.el;
            handle.style.cursor = 'grab';

            handle.addEventListener('mousedown', function(e) { self._start(e); });
            handle.addEventListener('touchstart', function(e) { self._startTouch(e); }, { passive: false });

            // Kill the onclick/click that fires after a drag (toggle collapse)
            handle.addEventListener('click', function(e) {
                if (self.didDrag) {
                    e.stopImmediatePropagation();
                    e.preventDefault();
                    self.didDrag = false;
                }
            }, true); // capture phase

            this._restorePosition();
        }

        _start(e) {
            // Don't drag on interactive elements inside handle
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' ||
                e.target.tagName === 'SELECT' ||
                (e.target.tagName === 'A' && e.target.href) ||
                (e.target.tagName === 'BUTTON' && !e.target.hasAttribute('data-drag-handle'))) {
                return;
            }
            if (activeDragger && activeDragger !== this) activeDragger._forceFinish();

            this.isDragging = true;
            this.didDrag = false;
            activeDragger = this;

            var rect = this.el.getBoundingClientRect();
            this.offset.x = e.clientX - rect.left;
            this.offset.y = e.clientY - rect.top;

            this.el.style.cursor = 'grabbing';
            this.el.style.zIndex = '9999';
            this.el.style.transition = 'none';
            e.preventDefault();
            e.stopPropagation();
        }

        _startTouch(e) {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' ||
                e.target.tagName === 'SELECT' ||
                (e.target.tagName === 'A' && e.target.href) ||
                (e.target.tagName === 'BUTTON' && !e.target.hasAttribute('data-drag-handle'))) {
                return;
            }
            if (activeDragger && activeDragger !== this) activeDragger._forceFinish();

            this.isDragging = true;
            this.didDrag = true; // touch always counts as drag
            activeDragger = this;

            var touch = e.touches[0];
            var rect = this.el.getBoundingClientRect();
            this.offset.x = touch.clientX - rect.left;
            this.offset.y = touch.clientY - rect.top;

            this.el.style.zIndex = '9999';
            this.el.style.transition = 'none';
            e.preventDefault();
        }

        _setPosition(clientX, clientY) {
            var x = clientX - this.offset.x;
            var y = clientY - this.offset.y;

            // Only consider it a drag if moved > 4px
            if (Math.abs(clientX - this.offset.x - parseFloat(this.el.style.left || 0)) > 4 ||
                Math.abs(clientY - this.offset.y - parseFloat(this.el.style.top || 0)) > 4) {
                this.didDrag = true;
            }

            // Clamp within viewport
            var maxX = window.innerWidth - this.el.offsetWidth;
            var maxY = window.innerHeight - this.el.offsetHeight;
            x = Math.max(0, Math.min(x, maxX));
            y = Math.max(0, Math.min(y, maxY));

            this.el.style.position = 'fixed';
            this.el.style.left = x + 'px';
            this.el.style.top = y + 'px';
            this.el.style.margin = '0';
            this.el.style.right = 'auto';
            this.el.style.bottom = 'auto';
        }

        _finish() {
            if (!this.isDragging) return;
            this.isDragging = false;
            if (activeDragger === this) activeDragger = null;

            this.el.style.cursor = 'grab';
            this.el.style.zIndex = '';
            this.el.style.transition = '';
            this._savePosition();
        }

        _forceFinish() {
            this.isDragging = false;
            this.el.style.cursor = 'grab';
            this.el.style.zIndex = '';
            this.el.style.transition = '';
        }

        _savePosition() {
            var rect = this.el.getBoundingClientRect();
            var positions = JSON.parse(localStorage.getItem('ws_panel_positions') || '{}');
            positions[this.el.id] = { x: rect.left, y: rect.top };
            localStorage.setItem('ws_panel_positions', JSON.stringify(positions));
        }

        _restorePosition() {
            var positions = JSON.parse(localStorage.getItem('ws_panel_positions') || '{}');
            var pos = positions[this.el.id];
            if (pos) {
                this.el.style.position = 'fixed';
                this.el.style.left = pos.x + 'px';
                this.el.style.top = pos.y + 'px';
                this.el.style.margin = '0';
                this.el.style.right = 'auto';
                this.el.style.bottom = 'auto';
            }
        }

        static resetAll() {
            localStorage.removeItem('ws_panel_positions');
            window.location.reload();
        }
    }

    window.PanelDragger = PanelDragger;
})();
