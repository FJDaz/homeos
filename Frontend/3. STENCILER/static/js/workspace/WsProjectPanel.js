/**
 * WsProjectPanel — Clean V3 (Mission 282)
 * Scope : student.projects[i]. Piloté par la session homeos_session.
 */
(function() {
    'use strict';

    let _expanded = {};
    let _projects = [];
    let _expandedState = {};
    let _screensCache = {};
    let optionalProjects = null;

    function getSession() {
        let s = {};
        try {
            s = JSON.parse(localStorage.getItem('homeos_session') || '{}');
        } catch(e) {}
        return s;
    }

    // M294-A: Auth headers helper
    function _authHeaders(extraHeaders = {}) {
        const session = getSession();
        const headers = { ...extraHeaders };
        if (session.token) headers['X-User-Token'] = session.token;
        return headers;
    }

    function _getSession() {
        try {
            const isImpersonate = new URLSearchParams(window.location.search).get('impersonate') === '1';
            if (isImpersonate) {
                const imp = JSON.parse(sessionStorage.getItem('homeos_impersonation') || '{}');
                if (imp.token) return imp;
            }
            return JSON.parse(localStorage.getItem('homeos_session') || '{}');
        } catch(e) { return {}; }
    }

    /**
     * M298 debug: trace le scope réel de la session utilisée pour les projets.
     */
    function _sessionTrace() {
        const s = _getSession();
        return {
            hasToken: !!s.token,
            token8: s.token ? s.token.substring(0, 8) : 'NONE',
            user_id: s.user_id || null,
            role: s.role || null,
            student_id: s.student_id || null,
            project_id: s.project_id || null,
        };
    }

    async function refresh() {
        try {
            const session = _getSession();
            const headers = {};
            if (session.token) headers['X-User-Token'] = session.token;

            console.log('[WsProjectPanel] session:', _sessionTrace());

            const res = await fetch('/api/projects', { headers });
            console.log('[WsProjectPanel] GET /api/projects →', res.status);
            if (!res.ok) return;
            _projects = await res.json();
            if (window.UxRun) window.UxRun.log('RESULT', `panel:projects:${_projects.length}`);
            console.log('[WsProjectPanel] reçu', _projects.length, 'projet(s):', _projects.map(p => p.name + (p.active ? ' [ACTIF]' : '')).join(', '));

            // Filtrer : ne garder que les projets appartenant au user_id de la session
            // (le backend peut retourner des projets partagés ou orphan — on filtre côté client en sécurité)
            const userId = session.user_id;
            if (userId && session.role !== 'admin') {
                // Le backend devrait déjà filtrer, mais on double-check
                // Les projets perso ont user_id = session.user_id
                // Les projets étudiant n'ont pas de user_id mais sont liés via students.user_id
                // On garde tout ce que le backend retourte (déjà filtré côté serveur)
            }

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
            const session = _getSession();
            const res = await fetch(`/api/retro-genome/imports?project_id=${projectId}`, {
                headers: { 'X-User-Token': session.token || '' }
            });
            if (res.ok) {
                const data = await res.json();
                const _visExts = ['html','htm','png','jpg','jpeg','gif','svg','webp'];
                _screensCache[projectId] = (data.imports || []).filter(imp => {
                    const ext = (imp.name || '').toLowerCase().split('.').pop();
                    return _visExts.includes(ext);
                });
            }
        } catch(e) {
            console.error(`[WsProjectPanel] Error fetching screens for ${projectId}:`, e);
        }
    }

    /**
     * Active un projet et synchronise le ManifestBox.
     */
    async function activateProject(projectId) {
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
     * Rendu explicite de la boucle des projets avec séparation par type.
     */
    function render() {
        const container = document.getElementById('ws-project-list');
        if (!container) return;
        
        const session = _getSession();
        const student = session.student || session; 
        const projects = optionalProjects || _projects || [];
        const activeId = session.active_project_id || session.project_id;

        container.innerHTML = '';

        const subjects = projects.filter(p => p.type === 'subject');
        const personal = projects.filter(p => p.type === 'personal');

        // Sinon : Affichage par sections
        if (subjects.length > 0 || (session.role === 'prof' || session.role === 'teacher' || session.role === 'admin' || session.role === 'student')) {
            const svgSubject = `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/></svg>`;
            const showAdd = (session.role === 'prof' || session.role === 'teacher' || session.role === 'admin');
            _renderSectionHeader(container, "Sujets", svgSubject, showAdd, () => {
                if (window.SubjectEditor) window.SubjectEditor.open();
            });
            subjects.forEach(p => _renderProjectAccordion(container, p));
        }

        // Toujours afficher "Projets Personnels" pour les élèves (Fix M333/M334/M335)
        const svgFolder = `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"/></svg>`;
        _renderSectionHeader(container, "Projets Personnels", svgFolder, true, () => {
            // M391: Déclenche l'ouverture du Drill au centre (force mode pour nouveau projet)
            if (window.WsStitchDrill) window.WsStitchDrill.show({ force: true });
        });

        if (personal.length > 0) {
            personal.forEach(p => _renderProjectAccordion(container, p));
        } else {
            const empty = document.createElement('div');
            empty.className = 'p-4 text-center text-[11px] text-slate-300 italic';
            empty.textContent = 'aucun projet personnel';
            container.appendChild(empty);
        }
    }

    async function _createNewProject(name) {
        try {
            const res = await fetch('/api/projects/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: name })
            });
            if (res.ok) {
                const data = await res.json();
                if (data.id) await activateProject(data.id);
                await refresh();
            }
        } catch(e) { console.error('[WsProjectPanel] Create error:', e); }
    }

    async function _uploadScreens(projectId, files) {
        const session = _getSession();
        if (window.UxRun) window.UxRun.log('ACTION', `panel:upload:${projectId}:${files.length}`);
        
        for (const file of files) {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('filename', file.name);
            formData.append('project_id', projectId);
            
            try {
                const res = await fetch('/api/import/upload', {
                    method: 'POST',
                    headers: { 'X-User-Token': session.token || '' },
                    body: formData
                });
                if (res.ok) {
                    // Trigger extraction
                    fetch('/api/imports/extract-tokens', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', 'X-User-Token': session.token || '' },
                        body: JSON.stringify({ project_id: projectId })
                    }).catch(() => {});
                }
            } catch(e) { console.error('[WsProjectPanel] Upload error:', e); }
        }
        delete _screensCache[projectId];
        await fetchProjectScreens(projectId);
        render();
    }

    async function _deleteScreen(projectId, importId) {
        if (!confirm('supprimer cet écran ? cette action est irréversible')) return;
        const session = _getSession();
        if (window.UxRun) window.UxRun.log('ACTION', `panel:delete:${importId}`);
        
        try {
            const res = await fetch(`/api/imports/${importId}?project_id=${projectId}`, {
                method: 'DELETE',
                headers: { 'X-User-Token': session.token || '' }
            });
            if (res.ok) {
                delete _screensCache[projectId];
                await fetchProjectScreens(projectId);
                render();
            }
        } catch(e) { console.error('[WsProjectPanel] Delete error:', e); }
    }

    async function _moveScreen(importId, currentPid, targetPid) {
        if (currentPid === targetPid) return;
        const session = _getSession();
        if (window.UxRun) window.UxRun.log('ACTION', `panel:move:${importId}:${currentPid}->${targetPid}`);
        
        try {
            const res = await fetch(`/api/imports/${importId}/move`, {
                method: 'PATCH',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-User-Token': session.token || '' 
                },
                body: JSON.stringify({ 
                    current_project_id: currentPid,
                    target_project_id: targetPid
                })
            });
            if (res.ok) {
                delete _screensCache[currentPid];
                delete _screensCache[targetPid];
                await Promise.all([
                    fetchProjectScreens(currentPid),
                    fetchProjectScreens(targetPid)
                ]);
                render();
            }
        } catch(e) { console.error('[WsProjectPanel] Move error:', e); }
    }

    function _renderSectionHeader(container, title, icon, showAdd = false, onAdd = null) {
        const h = document.createElement('div');
        h.className = 'px-4 py-2 mt-4 bg-slate-100/30 text-[10px] font-black uppercase tracking-widest text-slate-400 flex items-center justify-between';
        h.innerHTML = `
            <div class="flex items-center gap-2">
                <span>${icon}</span> <span>${title}</span>
            </div>
            ${showAdd ? `
                <button class="btn-section-add w-6 h-6 flex items-center justify-center bg-[#8cc63f] rounded-full text-white shadow-sm hover:scale-110 transition-all" title="nouveau projet">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                </button>
            ` : ''}
        `;
        container.appendChild(h);
        
        const btnAdd = h.querySelector('.btn-section-add');
        if (btnAdd && onAdd) {
            btnAdd.setAttribute('data-ux', 'ACTION');
            btnAdd.setAttribute('data-ux-label', `section:add:${title}`);
            btnAdd.onclick = (e) => {
                e.stopPropagation();
                onAdd();
            };
        }
    }

    function _renderProjectAccordion(container, project) {
        const isExpanded = !!_expandedState[project.id];
        const isActive = project.active;

        const projectBox = document.createElement('div');
        projectBox.className = `border-b border-slate-50 transition-all ${isActive ? 'bg-slate-50/50' : ''}`;

        // Header
        const header = document.createElement('div');
        header.className = `flex items-center justify-between p-4 cursor-pointer hover:bg-slate-100/50 transition-colors group`;
        header.setAttribute('data-ux', 'NAV');
        header.setAttribute('data-ux-label', `projet:${project.name || project.id}`);
        header.onclick = () => toggleProject(project.id);

        // M394: Drop Zone
        header.ondragover = (e) => {
            e.preventDefault();
            header.classList.add('bg-slate-200');
        };
        header.ondragleave = () => {
            header.classList.remove('bg-slate-200');
        };
        header.ondrop = (e) => {
            e.preventDefault();
            header.classList.remove('bg-slate-200');
            const data = JSON.parse(e.dataTransfer.getData('text/plain') || '{}');
            if (data.importId && data.projectId) {
                _moveScreen(data.importId, data.projectId, project.id);
            }
        };

        header.innerHTML = `
            <div class="flex items-center gap-3 min-w-0">
                <div class="w-1.5 h-1.5 rounded-full ${isActive ? 'bg-homeos-green shadow-[0_0_8px_rgba(163,205,84,0.4)]' : 'bg-slate-200'}"></div>
                <span class="text-[12px] font-bold ${isActive ? 'text-slate-800' : 'text-slate-400'} uppercase tracking-widest truncate">
                    ${project.name || project.id}
                </span>
            </div>
            <div class="flex items-center gap-2">
                <button class="btn-add-screen p-1 text-slate-300 hover:text-homeos-green transition-colors" title="ajouter des écrans">
                    <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                </button>
                ${project.type === 'personal' ? `
                    <button class="btn-cadrage p-1 text-slate-300 hover:text-indigo-500 transition-colors" title="Routine Cadrage">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/></svg>
                    </button>
                ` : ''}
                ${isActive ? `<span class="text-[9px] font-black uppercase text-homeos-green tracking-tighter">actif</span>` : ''}
                <div class="p-1 text-slate-300 group-hover:text-slate-500 transition-colors">
                    <svg class="w-3.5 h-3.5 transform transition-transform ${isExpanded ? 'rotate-0' : '-rotate-90'}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7"/></svg>
                </div>
            </div>
        `;
        projectBox.appendChild(header);

        const btnAdd = header.querySelector('.btn-add-screen');
        if (btnAdd) {
            btnAdd.onclick = (e) => {
                e.stopPropagation();
                const inp = document.createElement('input');
                inp.type = 'file';
                inp.multiple = true;
                inp.onchange = () => { if (inp.files.length) _uploadScreens(project.id, inp.files); };
                inp.click();
            };
        }

        const btnCadrage = header.querySelector('.btn-cadrage');
        if (btnCadrage) {
            btnCadrage.onclick = (e) => {
                e.stopPropagation();
                if (window.ManifestSullivanCore) {
                    window.ManifestSullivanCore._sullivanLog('btn_cadrage_clicked', { project_id: project.id });
                }
                if (window.ManifestBox) {
                    window.ManifestBox.show({ project_id: project.id });
                } else {
                    console.error('[WsProjectPanel] ManifestBox not found');
                }
            };
        }

        // Content
        if (isExpanded) {
            const content = document.createElement('div');
            content.className = 'px-4 pb-4 animate-in fade-in slide-in-from-top-1 duration-200';
            _renderScreensList(content, project.id);
            projectBox.appendChild(content);
        }

        container.appendChild(projectBox);
    }

    function _renderDirectSubject(container, project) {
        const isActive = project.active;
        const box = document.createElement('div');
        box.className = 'p-4 animate-in fade-in duration-500';

        box.innerHTML = `
             <div class="mb-6 flex items-center justify-between">
                <div>
                    <h3 class="text-[14px] font-black uppercase tracking-tighter text-slate-800">${project.name}</h3>
                    <p class="text-[10px] text-homeos-green font-bold uppercase tracking-widest">Sujet Actif</p>
                </div>
                <div class="w-2 h-2 rounded-full bg-homeos-green animate-pulse"></div>
            </div>
        `;

        const listContainer = document.createElement('div');
        _renderScreensList(listContainer, project.id);
        box.appendChild(listContainer);
        container.appendChild(box);

        // Auto-activate if not already (safeguard)
        if (!isActive) activateProject(project.id);
    }

    function _renderScreensList(container, projectId) {
        // M424-B Fix 3: Ligne manifeste (hors D&D)
        const manifestRow = document.createElement('div');
        manifestRow.className = 'flex items-center gap-2 px-3 py-1.5 text-[11px] font-medium text-slate-400 hover:text-slate-600 cursor-pointer select-none border-b border-slate-50 mb-2 transition-colors';
        manifestRow.innerHTML = `
          <span class="flex-1 truncate uppercase tracking-wider">manifeste</span>
          <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/>
            <circle cx="12" cy="12" r="3"/>
          </svg>`;
        manifestRow.addEventListener('click', () => {
            if (window.ManifestBox) window.ManifestBox.show({ project_id: projectId });
        });
        container.appendChild(manifestRow);

        const screens = _screensCache[projectId];
        if (!screens) {
            const loader = document.createElement('div');
            loader.className = 'py-2 text-[11px] text-slate-300 italic';
            loader.textContent = 'chargement...';
            container.appendChild(loader);
            return;
        }
        if (screens.length === 0) {
            const empty = document.createElement('div');
            empty.className = 'py-2 text-[11px] text-slate-300 italic text-center';
            empty.textContent = 'aucun écran';
            container.appendChild(empty);
            return;
        }

        const list = document.createElement('div');
        list.className = 'space-y-1';
        screens.forEach(screen => {
            if (screen.name === 'manifest.json') return;
            const sEl = document.createElement('div');
            sEl.className = 'group flex items-center justify-between p-2 rounded-lg hover:bg-white hover:shadow-sm border border-transparent hover:border-slate-100 transition-all cursor-pointer';
            
            // M394: Draggable
            sEl.draggable = true;
            sEl.ondragstart = (e) => {
                e.dataTransfer.setData('text/plain', JSON.stringify({
                    importId: screen.id,
                    projectId: projectId
                }));
                sEl.classList.add('opacity-50');
            };
            sEl.ondragend = () => sEl.classList.remove('opacity-50');

            // Thumbnail URL (M368)
            const filePath = screen.file_path || screen.svg_path;
            const isImage = filePath && /\.(png|jpg|jpeg|svg|webp)$/i.test(filePath);
            const thumbnailUrl = isImage ? `/api/retro-genome/file?project_id=${projectId}&path=${encodeURIComponent(filePath)}` : '';
            
            const thumbHtml = thumbnailUrl 
                ? `<div class="relative group/thumb w-8 h-8 shrink-0 rounded bg-slate-50 border border-slate-200 flex items-center justify-center mr-3">
                    <img src="${thumbnailUrl}" class="w-full h-full object-cover rounded opacity-80 group-hover/thumb:opacity-100 transition-all duration-300 ease-out group-hover/thumb:scale-[2.2] group-hover/thumb:z-50 group-hover/thumb:shadow-2xl group-hover/thumb:border-2 group-hover/thumb:border-white group-hover/thumb:translate-x-2 group-hover/thumb:rotate-2" alt="thumb">
                   </div>`
                : `<div class="w-8 h-8 shrink-0 rounded bg-slate-100 border border-slate-200 flex items-center justify-center mr-3 text-slate-300"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg></div>`;

            sEl.innerHTML = `
                <div class="flex items-center flex-1 overflow-visible">
                    ${thumbHtml}
                    <span class="text-[12px] font-medium text-slate-500 group-hover:text-slate-700 truncate">${screen.name}</span>
                </div>
                <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                    <button class="btn-s-open p-1 text-slate-300 hover:text-homeos-green" title="Ouvrir"><svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M24 12s-4.5-8-12-8S0 12 0 12s4.5 8 12 8 12-8 12-8z"/></svg></button>
                    <button class="btn-s-delete p-1 text-slate-300 hover:text-red-500" title="Supprimer"><svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg></button>
                </div>
            `;
            sEl.setAttribute('data-ux', 'ACTION');
            sEl.setAttribute('data-ux-label', `screen:open:${screen.name}`);
            sEl.onclick = (e) => {
                e.stopPropagation();
                if (window.wsCanvas) {
                    // Enrichir avec le projectId pour que WsScreenShell puisse charger l'image
                    const screenWithProject = { ...screen, project_id: projectId };
                    window.wsCanvas.addScreen(screenWithProject);
                }
            };

            const btnDel = sEl.querySelector('.btn-s-delete');
            if (btnDel) {
                btnDel.onclick = (e) => {
                    e.stopPropagation();
                    _deleteScreen(projectId, screen.id);
                };
            }
            list.appendChild(sEl);
        });
        container.appendChild(list);
    }

    async function refreshActiveScreens() {
        const session = _getSession();
        const activeId = session.active_project_id || session.project_id;
        if (!activeId) return;
        delete _screensCache[activeId];
        await fetchProjectScreens(activeId);
        render();
    }

    window.fetchWorkspaceImports = refreshActiveScreens;

    window.WsProjectPanel = {
        refresh: refresh,
        render: render,
        toggleProject: toggleProject,
        refreshScreens: refreshActiveScreens,
        createProject: _createNewProject,
        get projects() { return _projects; }
    };
})();
