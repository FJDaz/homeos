/**
 * Bootstrap.js — HoméOS
 * Mission 107 : Navigation globale cohérente
 *
 * Auto-injecte le header global sur toutes les pages.
 * CSS embarqué — aucune dépendance externe.
 */

(function () {
    'use strict';

    // ── Tabs ────────────────────────────────────────────────────────────────
    const TABS = [
        { id: 'brainstorm', label: 'brainstorm', path: '/landing' },
        { id: 'backend',    label: 'backend',    path: '/intent-viewer' },
        { id: 'frontend',   label: 'frontend',   path: '/frd-editor' },
        { id: 'deploy',     label: 'deploy',     path: '/deploy', disabled: true },
    ];

    // ── État global ─────────────────────────────────────────────────────────
    window.HOMEOS = window.HOMEOS || { version: '3.1.2' };

    // ── CSS auto-injecté ────────────────────────────────────────────────────
    function injectStyles() {
        if (document.getElementById('homeos-bootstrap-css')) return;
        const style = document.createElement('style');
        style.id = 'homeos-bootstrap-css';
        style.textContent = `
            #homeos-global-nav {
                position: fixed;
                top: 0; left: 0; right: 0;
                height: 48px;
                background: #f7f6f2;
                border-bottom: 1px solid #e5e5e5;
                display: flex;
                align-items: center;
                padding: 0 24px;
                gap: 32px;
                z-index: 1000;
                font-family: 'Geist', -apple-system, sans-serif;
                box-sizing: border-box;
            }
            #homeos-global-nav .hn-brand {
                font-size: 14px;
                font-weight: 700;
                color: #3d3d3c;
                letter-spacing: -0.02em;
                flex-shrink: 0;
                text-decoration: none;
            }
            #homeos-global-nav .hn-brand .hn-accent {
                color: #8cc63f;
            }
            #homeos-global-nav .hn-tabs {
                display: flex;
                align-items: center;
                gap: 4px;
                flex: 1;
            }
            #homeos-global-nav .hn-tab {
                font-size: 12px;
                font-weight: 400;
                color: #888;
                text-decoration: none;
                padding: 4px 10px;
                border-radius: 4px;
                transition: color 0.15s;
                white-space: nowrap;
            }
            #homeos-global-nav .hn-tab:hover:not(.hn-disabled) {
                color: #3d3d3c;
            }
            #homeos-global-nav .hn-tab.hn-active {
                font-weight: 700;
                color: #3d3d3c;
            }
            #homeos-global-nav .hn-tab.hn-disabled {
                color: #ccc;
                cursor: default;
                pointer-events: none;
            }
        `;
        document.head.appendChild(style);
    }

    // ── Détection tab actif ─────────────────────────────────────────────────
    function isActive(path) {
        const p = window.location.pathname.replace(/\/$/, '');
        return p === path.replace(/\/$/, '');
    }

    // ── Injection du header ─────────────────────────────────────────────────
    function injectNav() {
        if (document.getElementById('homeos-global-nav')) return;

        const nav = document.createElement('nav');
        nav.id = 'homeos-global-nav';

        const brand = document.createElement('a');
        brand.href = '/landing';
        brand.className = 'hn-brand';
        brand.innerHTML = 'hom<span class="hn-accent">é</span>OS';
        nav.appendChild(brand);

        const tabs = document.createElement('div');
        tabs.className = 'hn-tabs';
        TABS.forEach(function (t) {
            const a = document.createElement('a');
            a.href = t.disabled ? '#' : t.path;
            a.className = 'hn-tab' +
                (isActive(t.path) ? ' hn-active' : '') +
                (t.disabled ? ' hn-disabled' : '');
            a.textContent = t.label;
            tabs.appendChild(a);
        });
        nav.appendChild(tabs);

        document.body.insertBefore(nav, document.body.firstChild);
        document.body.style.paddingTop = '48px';
    }

    // ── Init ────────────────────────────────────────────────────────────────
    function init() {
        injectStyles();
        injectNav();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // ── API publique ────────────────────────────────────────────────────────
    window.HOMEOS.refreshNav = function () {
        const existing = document.getElementById('homeos-global-nav');
        if (existing) existing.remove();
        document.body.style.paddingTop = '';
        injectNav();
    };
})();
