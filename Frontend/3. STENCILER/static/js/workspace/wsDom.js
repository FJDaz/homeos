/**
 * wsDom — M252
 * Utilitaires DOM sécurisés avec traces console.
 * Élimine les crash sur éléments absents et les handlers silencieux.
 *
 * Usage : safeEl('my-id'), safeClick('.btn', handler)
 * Traces console : [wsDom] ...
 */
(function() {
    'use strict';
    console.log('[wsDom] init');

    /**
     * Récupère un élément par ID. Warning console si absent.
     * @param {string} id
     * @param {boolean} warn - afficher un warning si absent (défaut: true)
     * @returns {Element|null}
     */
    function safeEl(id, warn) {
        var el = document.getElementById(id);
        if (!el && warn !== false) {
            console.warn('[wsDom] ⚠ #' + id + ' not found in DOM');
        }
        return el;
    }

    /**
     * Ajoute un event listener click sur un sélecteur. Silencieux si absent.
     * @param {string} selector
     * @param {Function} handler
     * @returns {boolean} true si élément trouvé
     */
    function safeClick(selector, handler) {
        var el = document.querySelector(selector);
        if (!el) {
            console.warn('[wsDom] ⚠ ' + selector + ' not found, click handler skipped');
            return false;
        }
        el.addEventListener('click', handler);
        console.log('[wsDom] ✓ click on ' + selector);
        return true;
    }

    /**
     * Délégation d'événement : écoute sur parent, filtre par selector enfant.
     * @param {string} parentSelector
     * @param {string} childSelector
     * @param {string} eventType - 'click', 'mousedown', etc.
     * @param {Function} handler
     */
    function safeOn(parentSelector, childSelector, eventType, handler) {
        var parent = document.querySelector(parentSelector);
        if (!parent) {
            console.warn('[wsDom] ⚠ parent ' + parentSelector + ' not found');
            return;
        }
        parent.addEventListener(eventType, function(e) {
            var target = e.target.closest ? e.target.closest(childSelector) : null;
            if (target) {
                handler(e, target);
            }
        });
        console.log('[wsDom] ✓ delegate ' + eventType + ' on ' + parentSelector + ' → ' + childSelector);
    }

    /**
     * QuerySelectorAll safe — retourne [] si aucun résultat.
     * @param {string} selector
     * @returns {NodeList|Array}
     */
    function safeAll(selector) {
        var els = document.querySelectorAll(selector);
        return els || [];
    }

    // Exposition globale
    window.wsDom = {
        el: safeEl,
        click: safeClick,
        on: safeOn,
        all: safeAll
    };

    console.log('[wsDom] ✅ OK (4 utils)');
})();
