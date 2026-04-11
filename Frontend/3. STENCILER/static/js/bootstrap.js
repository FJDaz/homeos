/**
 * Bootstrap.js — HoméOS
 * Mission 107 : Navigation globale cohérente
 *
 * Auto-injecte le header global sur toutes les pages.
 * CSS embarqué — aucune dépendance externe.
 */

(function () {
    'use strict';

    // ── Guard: ne pas exécuter dans les iframes ────────────────────────────
    if (window !== window.top) return;

    // ── Tabs Dynamic Logic ───────────────────────────────────────────────
    let TABS = [
        { id: 'cadrage',    label: 'Cadrage',    title: "L'Intention (Humain)", path: '/cadrage' },
        { id: 'backend',    label: 'Backend',    title: "La Logique (Machine)", path: '/bkd-frd' },
        { id: 'frontend',   label: 'Frontend',   title: "Le Visuel (Workspace)", path: '/workspace' },
        { id: 'deploy',     label: 'Déploiement', title: "La Sortie", path: '/deploy', disabled: true },
    ];

    const session = JSON.parse(localStorage.getItem('homeos_session') || '{}');
    if (session.role === 'prof' || session.role === 'admin') {
        TABS.unshift({ id: 'dashboard', label: 'Dashboard', title: 'Tableau de bord enseignant', path: '/teacher' });
    }
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
                if (session.workspace_id) config.headers.set('X-Workspace-Id', session.workspace_id);
            } else {
                config.headers['X-User-Token'] = session.token;
                if (session.workspace_id) config.headers['X-Workspace-Id'] = session.workspace_id;
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
        const link = document.createElement('link');
        link.id = 'homeos-bootstrap-css';
        link.rel = 'stylesheet';
        link.href = '/static/css/homeos-nav.css';
        document.head.appendChild(link);

        // Delete button styles
        const style = document.createElement('style');
        style.textContent = `
            .sd-delete-btn {
                background: none;
                border: none;
                color: #d44;
                font-size: 14px;
                font-weight: bold;
                cursor: pointer;
                padding: 2px 6px;
                border-radius: 50%;
                transition: background 0.15s;
                line-height: 1;
            }
            .sd-delete-btn:hover {
                background: rgba(221,68,68,0.1);
            }
            .rbac-blocked {
                opacity: 0.5 !important;
                filter: grayscale(1) !important;
                cursor: not-allowed !important;
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

        // M269: ManifestBox button [M]
        const manifestBtn = document.createElement('button');
        manifestBtn.id = 'hn-manifest-btn';
        manifestBtn.className = 'hn-manifest-btn';
        manifestBtn.title = 'manifest du projet';
        manifestBtn.textContent = 'M';
        manifestBtn.onclick = function(e) { e.stopPropagation(); window.ManifestBox?.toggle(); };
        actions.appendChild(manifestBtn);

        const projectLabel = document.createElement('div');
        projectLabel.id = 'hn-active-project';
        projectLabel.className = 'hn-project';
        projectLabel.textContent = 'chargement...';

        // M227: Hide project switcher for students
        if (session.role !== 'student') {
            actions.appendChild(projectLabel);
            projectLabel.onclick = function(e) { e.stopPropagation(); toggleSwitcher(); };
        }

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

        // F1: Logout visible button — SVG power icon
        const logoutBtn = document.createElement('button');
        logoutBtn.className = 'hn-logout';
        logoutBtn.title = 'se déconnecter';
        logoutBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18.36 6.64a9 9 0 1 1-12.73 0"/><line x1="12" y1="2" x2="12" y2="12"/></svg>';
        logoutBtn.onclick = function() {
            localStorage.removeItem('homeos_session');
            window.location.href = '/login';
        };
        actions.appendChild(logoutBtn);
        
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
                <span class="sd-label">Compte & Workspace</span>
                <div class="flex flex-col gap-1 mb-3">
                    <div class="flex items-center gap-2">
                        <span class="text-[12px] font-bold text-[#3d3d3c]">${session.name || '?'}</span>
                        <span class="px-1.5 py-0.5 text-[8px] font-black uppercase tracking-widest rounded ${session.plan === 'MAX' ? 'bg-indigo-600 text-white' : session.plan === 'PRO' ? 'bg-indigo-100 text-indigo-700' : 'bg-slate-100 text-slate-500'}">${session.plan || 'FREE'}</span>
                    </div>
                    <span class="text-[9px] text-slate-400 font-mono tracking-tighter uppercase">${session.role || 'student'} / ${session.user_id?.substring(0,8) || '...' }</span>
                </div>
                
                <div class="bg-slate-50 p-2 rounded-lg border border-slate-100">
                    <div class="text-[8px] uppercase tracking-widest text-slate-400 mb-1">Workspace actif</div>
                    <div class="text-[11px] font-bold text-slate-700 truncate">${session.workspace_id || 'Personnel'}</div>
                </div>
            </div>

            <div class="sd-section">
                <span class="sd-label">Clés API (BYOK)</span>
                <div id="sd-keys-list" class="space-y-6">
                    ${[
                        {id:'gemini',   pricing:'gratuit'},
                        {id:'groq',     pricing:'gratuit'},
                        {id:'openai',   pricing:'payant'},
                        {id:'kimi',     pricing:'payant'},
                        {id:'mimo',     pricing:'gratuit'},
                        {id:'deepseek', pricing:'payant'},
                        {id:'qwen',     pricing:'gratuit'},
                        {id:'watson',   pricing:'gratuit'},
                    ].map(p => `
                        <div class="sd-key-group">
                            <div class="sd-key-label">
                                <div class="flex items-center gap-2">
                                    <span class="sd-key-name">${p.id.toUpperCase()}</span>
                                    <span class="px-1.5 py-0.5 text-[8px] font-bold uppercase tracking-wider rounded ${p.pricing === 'gratuit' ? 'bg-[#8cc63f]/20 text-[#6a9a2f]' : 'bg-orange-100 text-orange-600'}">${p.pricing}</span>
                                    <svg class="sd-help-btn" data-provider="${p.id}" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                        <circle cx="11" cy="11" r="8"></circle>
                                        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                                    </svg>
                                </div>
                                <div class="sd-key-status" data-provider="${p.id}"></div>
                            </div>
                            <input type="password" class="sd-input" data-provider="${p.id}" placeholder="Clé ${p.id}...">
                            <div class="sd-helper-text" id="helper-${p.id}"></div>
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

        // BYOK Save — button
        document.getElementById('sd-save-keys-btn').onclick = saveAllKeys;

        // BYOK Save — Enter key on any input
        drawer.querySelectorAll('.sd-input').forEach(input => {
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    saveSingleKey(input);
                }
            });
        });

        async function saveAllKeys() {
            const inputs = drawer.querySelectorAll('.sd-input');
            let success = 0;
            for (const input of inputs) {
                const key = input.value.trim();
                if (!key) continue;
                if (await saveSingleKey(input)) success++;
            }
            if (success > 0) {
                alert(`${success} clé(s) sauvegardée(s).`);
                refreshKeyStatus();
            }
        }

        async function saveSingleKey(input) {
            const key = input.value.trim();
            if (!key) return false;
            try {
                const res = await fetch('/api/me/keys', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ provider: input.dataset.provider, api_key: key })
                });
                if (res.ok) {
                    input.value = '';
                    input.style.borderColor = '#8cc63f';
                    setTimeout(() => { input.style.borderColor = ''; }, 1500);
                    return true;
                }
            } catch(e) { console.error('BYOK Save Fail', e); }
            return false;
        }

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
                        headers: { 'X-User-Token': session.token }
                    });
                    
                    if (!res.ok) throw new Error("API Erreur");
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
                    // Add/delete button when key is set
                    if (value === 'set') {
                        dot.innerHTML = `<button class="sd-delete-btn" data-provider="${provider}" title="Supprimer">×</button>`;
                    } else {
                        dot.innerHTML = '';
                    }
                }
            });
            // Wire delete buttons
            const drawer = document.getElementById('homeos-settings-drawer');
            if (!drawer) return;
            drawer.querySelectorAll('.sd-delete-btn').forEach(btn => {
                btn.onclick = async (e) => {
                    e.stopPropagation();
                    const provider = btn.dataset.provider;
                    if (!confirm(`Supprimer la clé ${provider.toUpperCase()} ?`)) return;
                    const res = await fetch(`/api/me/keys/${provider}`, { method: 'DELETE' });
                    if (res.ok) {
                        refreshKeyStatus();
                    }
                };
            });
        } catch(e) { console.error("Key Status Fail", e); }
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
    if (!window.HOMEOS) window.HOMEOS = {};
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
