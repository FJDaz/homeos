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
        { id: 'cadrage',    label: 'Cadrage',    title: "L'Intention (Humain)", path: '/cadrage' },
        { id: 'backend',    label: 'Backend',    title: "La Logique (Machine)", path: '/bkd-frd' },
        { id: 'frontend',   label: 'Frontend',   title: "Le Visuel (Workspace)", path: '/workspace' },
        { id: 'deploy',     label: 'Déploiement', title: "La Sortie", path: '/deploy', disabled: true },
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
            #homeos-global-nav .hn-actions {
                display: flex;
                align-items: center;
                gap: 16px;
                margin-left: auto;
            }
            #homeos-global-nav .hn-project {
                font-size: 10px;
                text-transform: lowercase;
                font-weight: 700;
                color: #8cc63f;
                background: #fff;
                padding: 2px 8px;
                border-radius: 12px;
                border: 1px solid #e5e5e5;
                letter-spacing: 0.05em;
                cursor: pointer;
                transition: all 0.2s;
            }
            #homeos-global-nav .hn-project:hover {
                border-color: #8cc63f;
                box-shadow: 0 2px 4px rgba(140, 198, 63, 0.1);
            }

            /* --- PROJECT SWITCHER (Mission 163) --- */
            #homeos-project-switcher {
                position: fixed;
                top: 54px;
                right: 24px;
                width: 280px;
                background: #fff;
                border: 1px solid #e5e5e5;
                border-radius: 12px;
                box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1);
                z-index: 2000;
                display: flex;
                flex-direction: column;
                overflow: hidden;
                font-family: inherit;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
                opacity: 0;
                transform: translateY(-10px);
                pointer-events: none;
            }
            #homeos-project-switcher.active {
                opacity: 1;
                transform: translateY(0);
                pointer-events: auto;
            }
            .ps-header {
                padding: 12px 16px;
                border-bottom: 1px solid #f0f0f0;
                background: #fafaf9;
            }
            .ps-title {
                font-size: 11px;
                font-weight: 700;
                color: #3d3d3c;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            .ps-search {
                padding: 8px 12px;
            }
            .ps-search input {
                width: 100%;
                border: 1px solid #e5e5e5;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
                outline: none;
                transition: border-color 0.2s;
            }
            .ps-search input:focus {
                border-color: #8cc63f;
            }
            .ps-list {
                max-height: 240px;
                overflow-y: auto;
                padding: 4px 0;
            }
            .ps-item {
                padding: 8px 16px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                cursor: pointer;
                transition: background 0.2s;
                font-size: 12px;
                color: #555;
            }
            .ps-item:hover {
                background: #f7f6f2;
            }
            .ps-item.active {
                background: #f0fdf4;
                color: #166534;
                font-weight: 600;
            }
            .ps-item .ps-name {
                flex: 1;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .ps-delete-btn {
                opacity: 0;
                color: #fca5a5;
                padding: 4px;
                border-radius: 4px;
                transition: all 0.2s;
            }
            .ps-item:hover .ps-delete-btn {
                opacity: 1;
            }
            .ps-delete-btn:hover {
                background: #fee2e2;
                color: #ef4444;
            }
            .ps-footer {
                padding: 12px;
                border-top: 1px solid #f0f0f0;
                display: flex;
                gap: 8px;
            }
            .ps-new-input {
                flex: 1;
                border: 1px solid #e5e5e5;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
                outline: none;
            }
            .ps-new-btn {
                background: #8cc63f;
                color: #fff;
                border: none;
                border-radius: 6px;
                padding: 0 10px;
                font-size: 16px;
                font-weight: 700;
                cursor: pointer;
                transition: opacity 0.2s;
            }
            .ps-new-btn:hover {
                opacity: 0.9;
            }
            .ps-empty {
                padding: 20px;
                text-align: center;
                font-size: 11px;
                color: #aaa;
                font-style: italic;
            }
        `;
        document.head.appendChild(style);
    }

    // ── Détection tab actif ─────────────────────────────────────────────────
    function isActive(path) {
        const p = window.location.pathname.replace(/\/$/, '');
        const target = path.replace(/\/$/, '');
        if (p === target) return true;
        // Aliases pour Cadrage
        if (target === '/cadrage' && (p === '/landing' || p === '')) return true;
        // Aliases pour Backend
        if (target === '/bkd-frd' && p === '/intent-viewer') return true;
        // Aliases pour Frontend
        if (target === '/workspace' && (p === '/frd-editor' || p === '/stenciler')) return true;
        return false;
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
            if (t.title) a.title = t.title;
            tabs.appendChild(a);
        });
        nav.appendChild(tabs);

        const actions = document.createElement('div');
        actions.className = 'hn-actions';
        
        const projectLabel = document.createElement('div');
        projectLabel.id = 'hn-active-project';
        projectLabel.className = 'hn-project';
        projectLabel.textContent = 'chargement...';
        actions.appendChild(projectLabel);
        
        nav.appendChild(actions);

        // Fetch active project
        fetch('/api/projects/active')
            .then(r => r.json())
            .then(data => {
                projectLabel.textContent = data.name || 'sans projet';
            })
            .catch(() => {
                projectLabel.textContent = 'erreur projet';
            });

        document.body.insertBefore(nav, document.body.firstChild);
        document.body.style.paddingTop = '48px';

        // ── PROJECT SWITCHER (Mission 163) ──────────────────────────────────
        injectSwitcher();
    }

    function injectSwitcher() {
        if (document.getElementById('homeos-project-switcher')) return;

        const switcher = document.createElement('div');
        switcher.id = 'homeos-project-switcher';
        switcher.innerHTML = `
            <div class="ps-header">
                <div class="ps-title">Mes Projets</div>
            </div>
            <div class="ps-search">
                <input type="text" placeholder="Rechercher..." id="ps-search-input">
            </div>
            <div id="ps-project-list" class="ps-list">
                <div class="ps-empty">Chargement...</div>
            </div>
            <div class="ps-footer">
                <input type="text" placeholder="Nouveau projet..." id="ps-new-name" class="ps-new-input">
                <button id="ps-create-btn" class="ps-new-btn">+</button>
            </div>
        `;
        document.body.appendChild(switcher);

        const projectBadge = document.getElementById('hn-active-project');
        if (projectBadge) {
            projectBadge.addEventListener('click', (e) => {
                e.stopPropagation();
                toggleSwitcher();
            });
        }

        document.addEventListener('click', (e) => {
            if (!switcher.contains(e.target) && !e.target.closest('.hn-project')) {
                switcher.classList.remove('active');
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') switcher.classList.remove('active');
        });

        // Create logic
        const createBtn = document.getElementById('ps-create-btn');
        const newInp = document.getElementById('ps-new-name');
        
        const handleCreate = () => {
            const name = newInp.value.trim();
            if (!name) return;
            fetch('/api/projects/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: name })
            }).then(r => r.json()).then(data => {
                if (data.id) activateProject(data.id);
            });
        };

        createBtn.onclick = handleCreate;
        newInp.onkeydown = (e) => { if (e.key === 'Enter') handleCreate(); };

        // Search logic
        const searchInput = document.getElementById('ps-search-input');
        searchInput.oninput = (e) => renderProjects(window._homeos_projects, e.target.value);
    }

    function toggleSwitcher() {
        const switcher = document.getElementById('homeos-project-switcher');
        if (!switcher) return;
        
        const isOpen = switcher.classList.toggle('active');
        if (isOpen) {
            fetch('/api/projects')
                .then(r => r.json())
                .then(projects => {
                    window._homeos_projects = projects;
                    renderProjects(projects);
                });
        }
    }

    function renderProjects(projects, filter = "") {
        const list = document.getElementById('ps-project-list');
        if (!list) return;

        const filtered = projects.filter(p => p.name.toLowerCase().includes(filter.toLowerCase()));
        
        if (filtered.length === 0) {
            list.innerHTML = `<div class="ps-empty">Aucun projet trouvé</div>`;
            return;
        }

        list.innerHTML = '';
        filtered.forEach(p => {
            const el = document.createElement('div');
            el.className = 'ps-item' + (p.active ? ' active' : '');
            
            const name = document.createElement('span');
            name.className = 'ps-name';
            name.textContent = p.name;
            name.onclick = () => activateProject(p.id);
            el.appendChild(name);

            // Delete BTN
            const del = document.createElement('span');
            del.className = 'ps-delete-btn';
            del.innerHTML = '×';
            del.title = 'Supprimer le projet';
            del.onclick = (e) => {
                e.stopPropagation();
                if (confirm(`Supprimer le projet "${p.name}" ?`)) deleteProject(p.id);
            };
            el.appendChild(del);

            list.appendChild(el);
        });
    }

    function activateProject(id) {
        fetch('/api/projects/activate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: id })
        }).then(() => {
            window.location.href = '/landing'; // Redirection demandée par l'user
        });
    }

    function deleteProject(id) {
        fetch(`/api/projects/${id}`, { method: 'DELETE' })
            .then(() => toggleSwitcher()); // Refresh via toggle
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

    window.HOMEOS.boot = function () {
        // no-op — nav is injected automatically on DOMContentLoaded
    };
})();
