/**
 * WsProjectPanel — Mission 282 V2
 * Gestion multi-projets avec accordéon explicite et activation automatique.
 * Synchronisé avec ManifestBox.
 */
(function() {
    'use strict';
    console.log('[WsProjectPanel] init V2');

    let _projects = [];
    let _screensCache = {}; // { projectId: [screens] }
    let _expandedState = {}; // { projectId: bool }

    async function refresh() {
        console.log('[WsProjectPanel] fetching all projects...');
        try {
            const res = await fetch('/api/projects');
            if (!res.ok) return;
            _projects = await res.json();
            
            // Initialiser l'état d'expansion : le projet actif est déplié par défaut
            _projects.forEach(p => {
                if (p.active && _expandedState[p.id] === undefined) {
                    _expandedState[p.id] = true;
                }
            });

            // Pré-charger les écrans du projet actif s'il y en a un
            const active = _projects.find(p => p.active);
            if (active && !_screensCache[active.id]) {
                await fetchProjectScreens(active.id);
            }

            render();
        } catch(e) {
            console.error('[WsProjectPanel] refresh error:', e);
        }
    }

    /**
     * Récupère les écrans d'un projet spécifique via le backend mis à jour.
     */
    async function fetchProjectScreens(projectId) {
        try {
            const res = await fetch(`/api/retro-genome/imports?project_id=${projectId}`);
            if (res.ok) {
                const data = await res.json();
                _screensCache[projectId] = data.imports || [];
            }
        } catch(e) {
            console.error(`[WsProjectPanel] Error fetching screens for ${projectId}:`, e);
        }
    }

    /**
     * Active un projet et synchronise le ManifestBox.
     */
    async function activateProject(projectId) {
        console.log('[WsProjectPanel] Activating:', projectId);
        try {
            // 1. Backend activation
            const res = await fetch('/api/projects/activate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: projectId })
            });

            if (res.ok) {
                // 2. State update
                if (window.wsState) window.wsState.setProjectId(projectId);
                
                // 3. Mark in-memory projects
                _projects.forEach(p => p.active = (p.id === projectId));

                // 4. Sync Manifest Editor
                if (window.ManifestBox) {
                    window.ManifestBox.showForProject(projectId);
                }
                
                render();
            }
        } catch(e) {
            console.error('[WsProjectPanel] Activation failed:', e);
        }
    }

    /**
     * Bascule l'accordéon d'un projet.
     */
    async function toggleProject(projectId) {
        const willExpand = !_expandedState[projectId];
        _expandedState[projectId] = willExpand;

        if (willExpand) {
            // Activation auto lors de l'expansion (demande utilisateur)
            await activateProject(projectId);
            
            // Chargement des écrans si besoin
            if (!_screensCache[projectId]) {
                await fetchProjectScreens(projectId);
            }
        }
        render();
    }

    /**
     * Rendu explicite de la boucle des projets.
     */
    function render() {
        const container = document.getElementById('ws-project-list');
        if (!container) return;
        container.innerHTML = '';

        if (_projects.length === 0) {
            container.innerHTML = '<div class="p-6 text-center text-[12px] text-slate-400 italic">Aucun projet.</div>';
            return;
        }

        // BOUCLE EXPLICITE : for (i=0; i < Total; i++)
        for (let i = 0; i < _projects.length; i++) {
            const project = _projects[i];
            const isExpanded = !!_expandedState[project.id];
            const isActive = project.active;

            const projectBox = document.createElement('div');
            projectBox.className = `border-b border-slate-50 transition-all ${isActive ? 'bg-slate-50/50' : ''}`;

            // --- HEADER ---
            const header = document.createElement('div');
            header.className = `flex items-center justify-between p-4 cursor-pointer hover:bg-slate-100/50 transition-colors group`;
            header.onclick = () => toggleProject(project.id);

            header.innerHTML = `
                <div class="flex items-center gap-3 min-w-0">
                    <div class="w-1.5 h-1.5 rounded-full ${isActive ? 'bg-homeos-green shadow-[0_0_8px_rgba(163,205,84,0.4)]' : 'bg-slate-200'}"></div>
                    <span class="text-[12px] font-bold ${isActive ? 'text-slate-800' : 'text-slate-400'} uppercase tracking-widest truncate">
                        ${project.name || project.id}
                    </span>
                </div>
                <div class="flex items-center gap-2">
                    ${isActive ? `<span class="text-[9px] font-black uppercase text-homeos-green tracking-tighter">actif</span>` : ''}
                    <div class="p-1 text-slate-300 group-hover:text-slate-500 transition-colors">
                        <svg class="w-3.5 h-3.5 transform transition-transform ${isExpanded ? 'rotate-0' : '-rotate-90'}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7"/></svg>
                    </div>
                </div>
            `;
            projectBox.appendChild(header);

            // --- CONTENU (Liste écrans) ---
            if (isExpanded) {
                const content = document.createElement('div');
                content.className = 'px-4 pb-4 animate-in fade-in slide-in-from-top-1 duration-200';
                
                const screens = _screensCache[project.id];
                if (!screens) {
                    content.innerHTML = '<div class="py-2 text-[11px] text-slate-300 italic">chargement...</div>';
                } else if (screens.length === 0) {
                    content.innerHTML = '<div class="py-2 text-[11px] text-slate-300 italic text-center">aucun écran</div>';
                } else {
                    const list = document.createElement('div');
                    list.className = 'space-y-1';
                    screens.forEach(screen => {
                        const sEl = document.createElement('div');
                        sEl.className = 'group flex items-center justify-between p-2 rounded-lg hover:bg-white hover:shadow-sm border border-transparent hover:border-slate-100 transition-all cursor-pointer';
                        
                        sEl.innerHTML = `
                            <span class="text-[12px] font-medium text-slate-500 group-hover:text-slate-700 truncate">${screen.name}</span>
                            <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                <button class="btn-s-open p-1 text-slate-300 hover:text-homeos-green"><svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M24 12s-4.5-8-12-8S0 12 0 12s4.5 8 12 8 12-8 12-8z"/></svg></button>
                            </div>
                        `;
                        sEl.onclick = (e) => {
                            e.stopPropagation();
                            if (window.wsCanvas) window.wsCanvas.addScreen(screen);
                        };
                        list.appendChild(sEl);
                    });
                    content.appendChild(list);
                }
                projectBox.appendChild(content);
            }

            container.appendChild(projectBox);
        }
    }

    window.WsProjectPanel = {
        refresh: refresh,
        render: render,
        toggleProject: toggleProject,
        get projects() { return _projects; }
    };

    console.log('[WsProjectPanel] ✅ OK V2');
})();
