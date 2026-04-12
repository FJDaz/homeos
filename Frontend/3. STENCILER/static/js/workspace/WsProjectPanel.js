/**
 * WsProjectPanel — Clean V3 (Mission 282)
 * Scope : student.projects[i]. Piloté par la session homeos_session.
 */
(function() {
    'use strict';
    
    let _expanded = {};

    function getSession() {
        let s = {};
        try {
            s = JSON.parse(localStorage.getItem('homeos_session') || '{}');
        } catch(e) {}
        return s;
    }

    async function refresh() {
        // En mode onboarding, le Drill injecte souvent via l'API avant de rafraîchir le panel
        // On peut faire un fetch optionnel ici si la session est vide
        const session = getSession();
        if (!session.projects && !session.student?.projects) {
            try {
                const res = await fetch('/api/projects');
                const projects = await res.json();
                // On ne touche pas à la session ici pour ne pas corrompre le drill, 
                // mais on peut utiliser les données pour le rendu immédiat.
                render(projects);
                return;
            } catch(e) {}
        }
        render();
    }

    async function activateAndShow(projectId) {
        console.log('[WsProjectPanel] Selecting project:', projectId);
        try {
            // 1. Activation Backend (établit le contexte serveur)
            await fetch('/api/projects/activate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: projectId })
            });

            // 2. Mise à jour session locale (synchro client)
            const session = getSession();
            session.active_project_id = projectId;
            localStorage.setItem('homeos_session', JSON.stringify(session));

            // 3. Trigger ManifestBox (Ouvre l'éditeur directement comme demandé)
            if (window.ManifestBox) window.ManifestBox.showForProject(projectId);
            
            render();
        } catch(e) {
            console.error('[WsProjectPanel] Selection error:', e);
        }
    }

    function render(optionalProjects = null) {
        const container = document.getElementById('ws-project-list');
        if (!container) return;
        
        const session = getSession();
        const student = session.student || session; 
        const projects = optionalProjects || student.projects || [];
        const activeId = session.active_project_id || session.project_id;

        container.innerHTML = '';

        if (projects.length === 0) {
            container.innerHTML = '<div class="p-6 text-center text-[11px] text-slate-300 italic uppercase tracking-widest">Aucun projet actif</div>';
            return;
        }

        // BOUCLE EXPLICITE : for (i=0; i < Total; i++)
        for (let i = 0; i < projects.length; i++) {
            const p = projects[i];
            const isExpanded = _expanded[p.id] !== undefined ? _expanded[p.id] : (p.id === activeId);
            const isActive = (p.id === activeId);

            const item = document.createElement('div');
            item.className = `border-b border-white transition-all ${isActive ? 'bg-[#fcfaf7]' : ''}`;
            
            item.innerHTML = `
                <div class="flex items-center justify-between p-4 cursor-pointer hover:bg-white transition-all group" id="p-header-${p.id}">
                    <div class="flex items-center gap-3">
                        <div class="w-1.5 h-1.5 rounded-full ${isActive ? 'bg-homeos-green shadow-[0_0_8px_rgba(140,198,63,0.4)]' : 'bg-slate-100'}"></div>
                        <span class="text-[12px] font-bold uppercase tracking-widest ${isActive ? 'text-slate-800' : 'text-slate-400 group-hover:text-slate-500'}">${p.name || p.id}</span>
                    </div>
                    <svg class="w-3.5 h-3.5 text-slate-200 group-hover:text-slate-400 transform transition-transform ${isExpanded ? '' : '-rotate-90'}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M19 9l-7 7-7-7" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </div>
                <div id="p-content-${p.id}" class="${isExpanded ? 'block' : 'hidden'} px-8 pb-5 animate-in fade-in duration-300">
                    <div class="flex flex-col gap-2">
                         <div class="text-[11px] text-slate-400 leading-relaxed">Projet prêt. Toutes les ressources sont synchronisées avec Stitch.</div>
                         <button class="text-left text-[10px] font-bold uppercase tracking-widest text-homeos-green hover:underline" onclick="event.stopPropagation(); window.ManifestBox.showForProject('${p.id}')">Editer le manifeste</button>
                    </div>
                </div>
            `;
            
            container.appendChild(item);

            // Handlers
            const header = document.getElementById(`p-header-${p.id}`);
            header.onclick = () => {
                const wasExpanded = !!_expanded[p.id];
                _expanded[p.id] = !wasExpanded;
                if (!wasExpanded) {
                    activateAndShow(p.id);
                } else {
                    render(optionalProjects);
                }
            };
        }
    }

    window.WsProjectPanel = { refresh, render };
    console.log('[WsProjectPanel] ✅ Clean Session Scope OK');
})();
