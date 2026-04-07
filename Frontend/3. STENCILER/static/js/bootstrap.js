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

    window.HOMEOS = window.HOMEOS || { version: '3.1.2' };
    
    // ── Mission 191: AUTH ORCHESTRATION ────────────────────────────────────
    const session = JSON.parse(localStorage.getItem('homeos_session') || '{}');
    const isLoginPath = window.location.pathname === '/login';

    if (!session.token && !isLoginPath) {
        window.location.href = '/login';
        return;
    }

    // Intercepteur Fetch Global (Monkey-patch)
    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
        let [resource, config] = args;
        if (!config) config = {};
        if (!config.headers) config.headers = {};
        
        // Injecter le token s'il existe
        if (session.token) {
            if (config.headers instanceof Headers) {
                config.headers.set('X-User-Token', session.token);
            } else {
                config.headers['X-User-Token'] = session.token;
            }
        }
        
        const response = await originalFetch(resource, config);
        
        // Gérer le 401 (Session expirée ou invalide)
        if (response.status === 401 && !isLoginPath) {
            console.warn("[AUTH] Session invalid or expired. Redirecting to login.");
            localStorage.removeItem('homeos_session');
            window.location.href = '/login';
        }
        
        return response;
    };

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
            #homeos-global-nav .hn-user-pill {
                display: flex;
                align-items: center;
                gap: 8px;
                padding-left: 16px;
                border-left: 1px solid #e5e5e5;
                margin-left: 16px;
            }
            #homeos-global-nav .hn-user-name {
                font-size: 11px;
                font-weight: 700;
                color: #3d3d3c;
                text-transform: capitalize;
            }
            #homeos-global-nav .hn-settings-btn {
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                color: #888;
                border-radius: 4px;
                transition: all 0.15s;
            }
            #homeos-global-nav .hn-settings-btn:hover {
                background: #fff;
                color: #3d3d3c;
                box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            }

            /* --- SETTINGS DRAWER (Mission 191) --- */
            #homeos-settings-drawer {
                position: fixed;
                top: 48px; bottom: 0; right: 0;
                width: 320px;
                background: #f7f6f2; /* HoméOS Cream */
                border-left: 1px solid #e5e5e5;
                z-index: 2000;
                display: flex;
                flex-direction: column;
                transform: translateX(100%);
                transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                padding: 32px;
                font-family: inherit;
            }
            #homeos-settings-drawer.active {
                transform: translateX(0);
                box-shadow: -10px 0 50px rgba(0,0,0,0.05);
            }
            .sd-section {
                margin-bottom: 40px;
            }
            .sd-label {
                font-size: 10px;
                font-weight: 800;
                color: #aaa;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                margin-bottom: 20px;
                display: block;
            }
            .sd-key-group {
                margin-bottom: 16px;
            }
            .sd-key-label {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 8px;
            }
            .sd-key-name {
                font-size: 11px;
                font-weight: 700;
                color: #3d3d3c;
            }
            .sd-key-status {
                width: 6px;
                height: 6px;
                border-radius: 50%;
                background: #ccc;
            }
            .sd-key-status.active {
                background: #8cc63f;
                box-shadow: 0 0 8px rgba(140, 198, 63, 0.6);
            }
            .sd-input {
                width: 100%;
                background: #fff;
                border: 1px solid #e5e5e5;
                border-radius: 0px; /* Hard-Edge */
                padding: 10px 12px;
                font-size: 11px;
                font-family: 'Source Code Pro', monospace;
                outline: none;
                transition: border-color 0.2s;
            }
            .sd-input:focus {
                border-color: #8cc63f;
            }
            .sd-help-btn {
                width: 14px;
                height: 14px;
                cursor: pointer;
                color: #94a3b8;
                transition: color 0.2s;
            }
            .sd-help-btn:hover {
                color: #8cc63f;
            }
            .sd-helper-text {
                font-size: 9px;
                color: #94a3b8;
                font-style: italic;
                margin-top: 4px;
                display: none;
            }
            .sd-helper-text.active {
                display: block;
            }
            .sd-logout-btn {
                margin-top: auto;
                padding: 12px;
                text-align: center;
                font-size: 10px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                background: #fff;
                border: 1px solid #fee2e2;
                color: #ef4444;
                cursor: pointer;
                transition: all 0.2s;
            }
            .sd-logout-btn:hover {
                background: #ef4444;
                color: #fff;
                border-color: #ef4444;
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

        // Mission 191: User Identity & Settings Button
        const userPill = document.createElement('div');
        userPill.className = 'hn-user-pill';
        userPill.innerHTML = `
            <span class="hn-user-name">${session.name || '?' }</span>
            <div id="hn-settings-toggle" class="hn-settings-btn" title="Paramètres BYOK">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
            </div>
        `;
        actions.appendChild(userPill);
        
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

        // ── SETTINGS DRAWER (Mission 191) ───────────────────────────────────
        injectSettingsDrawer();
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

    // ── Mission 191: SETTINGS DRAWER (BYOK) ────────────────────────────────
    function injectSettingsDrawer() {
        if (document.getElementById('homeos-settings-drawer')) return;

        const drawer = document.createElement('div');
        drawer.id = 'homeos-settings-drawer';
        drawer.innerHTML = `
            <div class="sd-section">
                <span class="sd-label">Identité</span>
                <div class="flex flex-col gap-1">
                    <span class="text-[12px] font-bold text-[#3d3d3c]">${session.name || '?'}</span>
                    <span class="text-[9px] text-slate-400 font-mono tracking-tighter uppercase">${session.role || 'student'} / ${session.user_id?.substring(0,8) || '...' }</span>
                </div>
            </div>

            <div class="sd-section">
                <span class="sd-label">Clés API (BYOK)</span>
                <div id="sd-keys-list" class="space-y-6">
                    ${['gemini', 'groq', 'openai', 'kimi', 'mimo', 'deepseek', 'qwen', 'watson'].map(provider => `
                        <div class="sd-key-group">
                            <div class="sd-key-label">
                                <div class="flex items-center gap-2">
                                    <span class="sd-key-name">${provider.toUpperCase()}</span>
                                    <svg class="sd-help-btn" data-provider="${provider}" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                        <circle cx="11" cy="11" r="8"></circle>
                                        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                                    </svg>
                                </div>
                                <div class="sd-key-status" data-provider="${provider}"></div>
                            </div>
                            <input type="password" class="sd-input" data-provider="${provider}" placeholder="Clé ${provider}...">
                            <div class="sd-helper-text" id="helper-${provider}"></div>
                        </div>
                    `).join('')}
                </div>
                <button id="sd-save-keys-btn" class="mt-8 w-full py-3 bg-[#A3CD54] text-[#1A1A1A] text-[10px] font-bold uppercase tracking-widest hover:opacity-90">
                    Sauvegarder les clés
                </button>
            </div>

            <button class="sd-logout-btn" id="hn-logout-btn">
                Changer d'identité
            </button>
        `;
        document.body.appendChild(drawer);

        const toggle = document.getElementById('hn-settings-toggle');
        if (toggle) {
            toggle.addEventListener('click', (e) => {
                e.stopPropagation();
                const isActive = drawer.classList.toggle('active');
                if (isActive) refreshKeyStatus();
            });
        }

        document.addEventListener('click', (e) => {
            if (!drawer.contains(e.target) && !e.target.closest('.hn-settings-btn')) {
                drawer.classList.remove('active');
            }
        });

        // Logout
        document.getElementById('hn-logout-btn').onclick = () => {
            if (confirm("Se déconnecter et changer d'identité ?")) {
                localStorage.removeItem('homeos_session');
                window.location.href = '/login';
            }
        };

        // BYOK Save
        document.getElementById('sd-save-keys-btn').onclick = async () => {
            const inputs = drawer.querySelectorAll('.sd-input');
            let success = 0;
            for (const input of inputs) {
                const key = input.value.trim();
                if (!key) continue;
                
                try {
                    const res = await fetch('/api/me/keys', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ provider: input.dataset.provider, api_key: key })
                    });
                    if (res.ok) {
                        success++;
                        input.value = ""; // Clear for security
                    }
                } catch(e) { console.error("BYOK Save Fail", e); }
            }
            if (success > 0) {
                alert(`${success} clé(s) sauvegardée(s).`);
                refreshKeyStatus();
            }
        };

        // Mission 192: GPS Help Logic
        drawer.querySelectorAll('.sd-help-btn').forEach(btn => {
            btn.onclick = async (e) => {
                const provider = btn.dataset.provider;
                const helperEl = document.getElementById(`helper-${provider}`);
                if (!helperEl) return;

                helperEl.textContent = "Sullivan cherche...";
                helperEl.classList.add('active');

                try {
                    const res = await fetch(`/api/me/keys/helper/${provider}`, {
                        headers: { 'X-User-Token': session.user_id }
                    });
                    const data = await res.json();
                    if (data.url) {
                        helperEl.innerHTML = `<a href="${data.url}" target="_blank" style="text-decoration:underline;">Cliquez ici</a> : ${data.instructions}`;
                    } else {
                        helperEl.textContent = "Impossible de trouver l'URL.";
                    }
                } catch(err) {
                    helperEl.textContent = "Erreur de recherche.";
                }
            };
        });
    }

    async function refreshKeyStatus() {
        try {
            const res = await fetch('/api/me/keys');
            const status = await res.json();
            Object.entries(status).forEach(([provider, value]) => {
                const dot = document.querySelector(`.sd-key-status[data-provider="${provider}"]`);
                if (dot) {
                    dot.classList.toggle('active', value === 'set');
                }
            });
        } catch(e) { console.error("Key Status Fail", e); }
    }

    // ── Init ────────────────────────────────────────────────────────────────
    function init() {
        injectStyles();
        injectNav();
        
        // Mission 166: Hook into Mode Toggle for Effects Button
        const modesContainer = document.querySelector('.flex.bg-slate-100.p-1.rounded-custom');
        if (modesContainer) {
            modesContainer.addEventListener('click', (e) => {
                const btn = e.target.closest('.ws-mode-btn');
                if (btn) {
                    const mode = btn.dataset.mode;
                    const effectsBtn = document.getElementById('ws-btn-effects-drawer');
                    if (effectsBtn) {
                        if (mode === 'front-dev') {
                            effectsBtn.classList.remove('hidden');
                        } else {
                            effectsBtn.classList.add('hidden');
                            const drawer = document.getElementById('ws-fee-effects-drawer');
                            if (drawer && drawer.style.height !== '0px') {
                                if (window.wsGsapCheatSheet) window.wsGsapCheatSheet.toggle();
                            }
                        }
                    }
                    // Dispatch event for components like GsapCheatSheet
                    window.dispatchEvent(new CustomEvent('ws-mode-change', { detail: { mode } }));
                }
            });
        }

        // Mission 166: Load GsapCheatSheet
        if (window.location.pathname.includes('/workspace')) {
            const script = document.createElement('script');
            script.src = '/static/js/workspace/fee/GsapCheatSheet.js';
            script.onload = () => {
                if (window.GsapCheatSheet) {
                    window.wsGsapCheatSheet = new window.GsapCheatSheet();
                }
            };
            document.body.appendChild(script);
        }
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
