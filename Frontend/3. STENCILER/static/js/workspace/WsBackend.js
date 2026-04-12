/* WsBackend.js — Orchestration de la War Room Studio (M208 Rectifiée) */

class WsBackend {
    constructor() {
        this.projectId = null;
        this.currentFilePath = null;
        this.archConvId = localStorage.getItem('ws_arch_conv_id');
        this.workConvId = localStorage.getItem('ws_work_conv_id');
        this.sidebarCollapsed = localStorage.getItem('ws_sidebar_collapsed') === 'true';
        this.pendingPlan = { architect: false, worker: false };
        
        // Eléments UI
        this.els = {
            projectTitle: document.getElementById('project-switcher'),
            workspaceContainer: document.getElementById('ws-content-area'), // Conteneur des vues
            tabRow: document.getElementById('ws-tab-row'),
            renderArea: document.getElementById('render-area'),
            editorArea: document.getElementById('editor-area'),
            currentFilename: document.getElementById('current-filename'),
            chatArch: document.getElementById('chat-arch-history'),
            chatWork: document.getElementById('chat-work-history'),
            inputArch: document.getElementById('input-arch'),
            inputWork: document.getElementById('input-work'),
            logArch: document.getElementById('log-arch'),
            logWork: document.getElementById('log-work'),
            historyArch: document.getElementById('select-history-arch'),
            historyWork: document.getElementById('select-history-work'),
            btnRecompile: document.getElementById('btn-recompile'),
            btnRefreshFiles: document.getElementById('btn-refresh-files'),
            explorerGrid: document.getElementById('explorer-grid'),
            toggleSidebar: document.getElementById('toggle-sidebar'),
            sidebarLeft: document.getElementById('sidebar-left')
        };
        
        this.init();
    }

    async init() {
        console.log("🚀 WsBackend: Initialisation Studio...");
        
        // État Sidebar
        if (this.sidebarCollapsed) {
            this.els.sidebarLeft.classList.add('collapsed');
        }

        await this.loadActiveProject();
        this.addLog('architect', '— war room initialisée —');
        this.addLog('worker', '— en attente d\'instructions —');
        this.setupEventListeners();
        this.loadRoadmap();
        this.refreshHistory('architect');
        this.refreshHistory('worker');
        
        if (this.archConvId) this.loadConversation(this.archConvId, 'architect');
        if (this.workConvId) this.loadConversation(this.workConvId, 'worker');
    }

    async loadActiveProject() {
        try {
            const res = await fetch('/api/bkd/projects');
            const data = await res.json();
            const projects = data.projects || [];

            // Alimenter le <select>
            const sel = this.els.projectTitle;
            sel.innerHTML = '';
            projects.forEach(p => {
                const opt = document.createElement('option');
                opt.value = p.id;
                opt.textContent = p.name;
                opt.selected = p.active;
                sel.appendChild(opt);
            });

            // Projet initial = actif ou premier
            const active = projects.find(p => p.active) || projects[0];
            if (active) {
                this.projectId = active.id;
                sel.value = active.id;
                this.loadExplorer();
            }

            // Switch projet
            sel.onchange = () => {
                this.projectId = sel.value;
                this.loadExplorer();
                this.loadRoadmap();
                this.refreshHistory('architect');
                this.refreshHistory('worker');
                this.archConvId = null;
                this.workConvId = null;
                localStorage.removeItem('ws_arch_conv_id');
                localStorage.removeItem('ws_work_conv_id');
                document.getElementById('chat-arch-history').innerHTML = '';
                document.getElementById('chat-work-history').innerHTML = '';
            };
        } catch (e) {
            console.error("WsBackend: Erreur chargement projet", e);
        }
    }

    setupEventListeners() {
        // Toggle Sidebar
        this.els.toggleSidebar.onclick = () => {
            this.sidebarCollapsed = !this.sidebarCollapsed;
            this.els.sidebarLeft.classList.toggle('collapsed', this.sidebarCollapsed);
            localStorage.setItem('ws_sidebar_collapsed', this.sidebarCollapsed);
        };

        // Raccourci clavier Alt+B pour la sidebar
        window.addEventListener('keydown', (e) => {
            if (e.altKey && e.key === 'b') {
                this.els.toggleSidebar.click();
            }
        });

        // Chat Architecte (Main-Left)
        this.els.inputArch.onkeydown = (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                if (this.pendingPlan.architect) {
                    this.addLog('architect', "validation du plan requise");
                    return;
                }
                e.preventDefault();
                this.sendMessage('architect');
            }
        };

        // Chat Ouvrier (Aside-Right)
        this.els.inputWork.onkeydown = (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                if (this.pendingPlan.worker) {
                    this.addLog('worker', "validation du plan requise");
                    return;
                }
                e.preventDefault();
                this.sendMessage('worker');
            }
        };

        // History Selects
        this.els.historyArch.onchange = (e) => {
            if (e.target.value) this.loadConversation(e.target.value, 'architect');
            else this.startNewConversation('architect');
        };
        
        this.els.historyWork.onchange = (e) => {
            if (e.target.value) this.loadConversation(e.target.value, 'worker');
            else this.startNewConversation('worker');
        };

        // Refresh Files
        this.els.btnRefreshFiles.onclick = () => this.loadExplorer();

        // Initial Tabs
        document.querySelectorAll('[data-tab]').forEach(tab => {
            tab.onclick = () => this.switchTab(tab.getAttribute('data-tab'));
        });

        // Recompile
        this.els.btnRecompile.onclick = async () => {
            this.addLog('architect', 'recompilation du génome...');
            try {
                const res = await fetch('/api/projects/active/genome-compile', { method: 'POST' });
                this.addLog('architect', res.ok ? 'génome recompilé' : 'échec recompilation');
                this.loadRoadmap();
            } catch (e) { this.addLog('architect', 'erreur api compile'); }
        };
    }

    switchTab(targetId) {
        // Update Buttons
        const btns = this.els.tabRow.querySelectorAll('button');
        btns.forEach(btn => {
            const id = btn.getAttribute('data-tab');
            btn.classList.toggle('tab-active', id === targetId);
            btn.classList.toggle('text-homeos-muted', id !== targetId);
        });

        // Update Areas
        const container = this.els.workspaceContainer;
        for (let child of container.children) {
            const areaId = child.id.replace('-area', '');
            child.classList.toggle('hidden', areaId !== targetId);
        }
    }

    // --- Dynamic Tabs ---
    createTab(id, label, contentHtml, isPlan = false) {
        const tabId = `${id}`;
        let btn = this.els.tabRow.querySelector(`[data-tab="${tabId}"]`);
        
        if (!btn) {
            btn = document.createElement('button');
            btn.setAttribute('data-tab', tabId);
            btn.className = 'h-full text-[12px] uppercase font-bold tracking-widest text-homeos-textMuted hover:text-homeos-text flex items-center gap-2';
            btn.innerHTML = `${label} <span class="text-[10px] opacity-30 hover:opacity-100 close-tab">×</span>`;
            
            // Insert before the spacers/filename
            this.els.tabRow.insertBefore(btn, this.els.tabRow.querySelector('.flex-1'));
            
            btn.onclick = (e) => {
                if (e.target.classList.contains('close-tab')) {
                    this.closeTab(tabId);
                    return;
                }
                this.switchTab(tabId);
            };
        }

        let area = document.getElementById(`${tabId}-area`);
        if (!area) {
            area = document.createElement('div');
            area.id = `${tabId}-area`;
            area.className = 'hidden h-full overflow-auto p-8 no-scrollbar bg-white';
            this.els.workspaceContainer.appendChild(area);
        }
        area.innerHTML = contentHtml;
        this.switchTab(tabId);
    }

    closeTab(id) {
        const btn = this.els.tabRow.querySelector(`[data-tab="${id}"]`);
        const area = document.getElementById(`${id}-area`);
        if (btn) btn.remove();
        if (area) area.remove();
        this.switchTab('roadmap');
    }

    // --- EXPLORER LOGIC ---
    async loadExplorer() {
        if (!this.projectId) return;
        try {
            const res = await fetch(`/api/bkd/files?project_id=${this.projectId}`);
            const data = await res.json();
            this.els.explorerGrid.innerHTML = '';
            if (data.files && data.files.length > 0) {
                const tree = this.buildTree(data.files);
                this.els.explorerGrid.appendChild(this.renderTree(tree));
            }
        } catch (e) {
            console.error("WsBackend: Erreur explorer", e);
        }
    }

    buildTree(files) {
        const tree = {};
        files.forEach(file => {
            const parts = file.path.split('/');
            let current = tree;
            parts.forEach((part, index) => {
                if (!current[part]) {
                    current[part] = { 
                        _isFile: index === parts.length - 1, 
                        _path: file.path,
                        _children: {}
                    };
                }
                current = current[part]._children;
            });
        });
        return tree;
    }

    renderTree(node, depth = 0) {
        const container = document.createElement('div');
        container.className = depth > 0 ? 'folder-children' : '';
        
        Object.keys(node).sort().forEach(key => {
            const item = node[key];
            const div = document.createElement('div');
            div.className = `py-1 hover:bg-homeos-panel cursor-pointer truncate flex items-center group`;
            
            if (item._isFile) {
                div.innerHTML = `<span class="mr-2 opacity-40">📄</span>${key}`;
                div.onclick = () => this.loadFile(item._path);
            } else {
                div.innerHTML = `<span class="mr-2 opacity-40">📁</span><span class="font-bold">${key}</span>`;
                const children = this.renderTree(item._children, depth + 1);
                children.classList.add('hidden');
                div.onclick = (e) => {
                    e.stopPropagation();
                    children.classList.toggle('hidden');
                    div.querySelector('span:first-child').innerHTML = children.classList.contains('hidden') ? '📁' : '📂';
                };
                container.appendChild(div);
                container.appendChild(children);
                return;
            }
            container.appendChild(div);
        });
        return container;
    }

    async loadFile(path) {
        this.currentFilePath = path;
        this.els.currentFilename.textContent = path;
        try {
            const res = await fetch(`/api/bkd/file?project_id=${this.projectId}&path=${encodeURIComponent(path)}`);
            const data = await res.json();
            
            if (path.endsWith('.md')) {
                this.createTab('editor', path, `<div class="roadmap-content">${marked.parse(data.content)}</div>`);
            } else {
                this.createTab('editor', path, `<textarea id="txt-edit-${path}" class="w-full h-full p-4 font-mono text-[11px] outline-none bg-homeos-panel/10" spellcheck="false">${data.content}</textarea>`);
            }
            this.addLog('architect', `Fichier ouvert : ${path}`);
        } catch (e) {
            this.addLog('architect', `Erreur chargement : ${path}`);
        }
    }

    // --- ROADMAP & CHAT ---
    async loadRoadmap() {
        if (!this.projectId) return;
        const candidates = [
            '2. COMMUNICATION/ROADMAP.md',
            'ROADMAP.md',
            'Frontend/4. COMMUNICATION/ROADMAP.md',
            'HOMEO_GENOME.md',
        ];
        try {
            for (const path of candidates) {
                const res = await fetch(`/api/bkd/file?project_id=${encodeURIComponent(this.projectId)}&path=${encodeURIComponent(path)}`);
                if (res.ok) {
                    const data = await res.json();
                    this.els.renderArea.innerHTML = marked.parse(data.content);
                    document.getElementById('current-filename').textContent = path.split('/').pop();
                    return;
                }
            }
            this.els.renderArea.innerHTML = '<p style="color:#9a9a98;font-size:13px;padding:16px">Aucune roadmap trouvée pour ce projet.</p>';
        } catch (e) {}
    }

    async sendMessage(role) {
        const input = role === 'architect' ? this.els.inputArch : this.els.inputWork;
        const msg = input.value.trim();
        if (!msg) return;

        // Si le message est "go", lever le blocage
        if (msg.toLowerCase() === 'go' && this.pendingPlan[role]) {
            this.pendingPlan[role] = false;
            this.closeTab(`plan-${role}`);
            this.addLog(role, "Plan validé. Exécution lancée.");
            // On continue pour envoyer le "go" à Sullivan
        }

        const convId = role === 'architect' ? this.archConvId : this.workConvId;
        this.appendBubble(role, msg, 'user');
        input.value = '';
        this.addLog(role, `> ${msg.slice(0, 40)}...`);

        try {
            const res = await fetch('/api/bkd/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: msg, project_id: this.projectId, role, conversation_id: convId })
            });
            const data = await res.json();
            this.appendBubble(role, data.explanation, 'assistant');
            
            // Détection de plan
            if (data.explanation.includes('## plan')) {
                this.createPlanTab(role, data.explanation);
            }

            if (!convId) {
                const newId = data.conversation_id;
                if (role === 'architect') { this.archConvId = newId; localStorage.setItem('ws_arch_conv_id', newId); }
                else { this.workConvId = newId; localStorage.setItem('ws_work_conv_id', newId); }
                this.refreshHistory(role);
            }
        } catch (e) { this.addLog(role, 'Erreur de communication.'); }
    }

    createPlanTab(role, content) {
        this.pendingPlan[role] = true;
        const label = `plan — ${role}`;
        const tabId = `plan-${role}`;
        
        const html = `
            <div class="roadmap-content p-4 bg-homeos-panel/20 border-l-4 border-homeos-green h-full flex flex-col">
                <div class="flex-1">${marked.parse(content)}</div>
                <div class="p-6 border-t border-homeos-border flex justify-center sticky bottom-0 bg-white shadow-xl">
                    <button id="btn-go-${role}" class="px-12 py-3 bg-homeos-green text-white font-bold tracking-widest text-[14px] hover:opacity-90 shadow-lg">GO</button>
                </div>
            </div>
        `;
        
        this.createTab(tabId, label, html, true);
        
        // Go button listener
        setTimeout(() => {
            const btn = document.getElementById(`btn-go-${role}`);
            if (btn) {
                btn.onclick = () => {
                    const input = role === 'architect' ? this.els.inputArch : this.els.inputWork;
                    input.value = 'go';
                    this.sendMessage(role);
                };
            }
        }, 100);
        
        this.addLog(role, "Plan de mission détecté. Validation requise.");
    }

    appendBubble(role, text, sender) {
        const container = role === 'architect' ? this.els.chatArch : this.els.chatWork;
        const b = document.createElement('div');
        b.className = `p-3 text-[13px] leading-relaxed mb-4 ${sender === 'user' ? 'bg-white border border-homeos-border' : 'bg-white border-l-2 border-homeos-green shadow-sm'}`;
        b.innerHTML = sender === 'assistant' ? `<div class="text-[11px] font-bold uppercase mb-1 opacity-40">${role}</div><div class="whitespace-pre-wrap">${text}</div>` : text;
        container.appendChild(b);
        container.scrollTop = container.scrollHeight;
    }

    addLog(role, text) {
        const log = role === 'architect' ? this.els.logArch : this.els.logWork;
        const line = document.createElement('div');
        line.innerHTML = `<span class="opacity-30 mr-2">${new Date().toLocaleTimeString()}</span> ${text}`;
        log.appendChild(line);
        log.scrollTop = log.scrollHeight;
    }

    async refreshHistory(role) {
        if (!this.projectId) return;
        const res = await fetch(`/api/bkd/conversations?project_id=${this.projectId}&role=${role}`);
        const list = await res.json();
        const select = role === 'architect' ? this.els.historyArch : this.els.historyWork;
        select.innerHTML = '<option value="">Nouv. Session</option>';
        list.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c.id;
            opt.textContent = c.title || c.id.slice(0, 8);
            select.appendChild(opt);
        });
        select.value = role === 'architect' ? this.archConvId : this.workConvId;
    }

    async loadConversation(id, role) {
        const res = await fetch(`/api/bkd/conversations/${id}`);
        const data = await res.json();
        const history = JSON.parse(data.content_json);
        const container = role === 'architect' ? this.els.chatArch : this.els.chatWork;
        container.innerHTML = '';
        history.forEach(turn => this.appendBubble(role, turn.content, turn.role));
        if (role === 'architect') this.archConvId = id; else this.workConvId = id;
        localStorage.setItem(`ws_${role}_conv_id`, id);
    }

    startNewConversation(role) {
        if (role === 'architect') this.archConvId = null; else this.workConvId = null;
        localStorage.removeItem(`ws_${role}_conv_id`);
        (role === 'architect' ? this.els.chatArch : this.els.chatWork).innerHTML = '';
    }
}
