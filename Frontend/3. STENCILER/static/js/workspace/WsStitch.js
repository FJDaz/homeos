/**
 * WsStitch.js — HoméOS
 * Mission 203 : Stitch Panel (UX de connexion et test end-to-end)
 * 
 * Gère l'interface de connexion et d'importation depuis Stitch (MCP).
 */

class WsStitch {
    constructor() {
        this.drawer = null;
        this.statusBadge = null;
        this.screensList = null;
        this.feedback = null;
        this.projectIdInput = null;
        this.screenNameInput = null;
        this.intentInput = null;
        this.btnPush = null;
        
        this.isOpen = false;
        this.isConnected = false;
        
        this._init();
    }

    _init() {
        // L'injection HTML est faite dans workspace.html, on récupère les refs
        this.drawer = document.getElementById('panel-stitch');
        if (!this.drawer) {
            console.warn("⚠️ [WsStitch] Panel element not found in DOM.");
            return;
        }

        this.statusBadge = document.getElementById('ws-stitch-status');
        this.screensList = document.getElementById('ws-stitch-screens-list');
        this.feedback = document.getElementById('ws-stitch-feedback');
        this.projectIdInput = document.getElementById('ws-stitch-project-id');
        this.screenNameInput = document.getElementById('ws-stitch-screen-name');

        // Event Listeners
        const btnList = document.getElementById('ws-stitch-btn-list');
        if (btnList) btnList.onclick = () => this.listScreens();

        const btnPull = document.getElementById('ws-stitch-btn-pull');
        if (btnPull) btnPull.onclick = () => this.pull();

        this.intentInput = document.getElementById('ws-stitch-intent');
        this.btnPush = document.getElementById('ws-stitch-btn-push');
        if (this.btnPush) this.btnPush.onclick = () => this.push();

        const badgeTrigger = document.getElementById('badge-stitch');
        if (badgeTrigger) badgeTrigger.onclick = () => this.toggle();
        
        const closeBtn = document.getElementById('ws-stitch-close');
        if (closeBtn) closeBtn.onclick = () => this.hide();

        console.log("✅ [WsStitch] Initialized.");
    }

    async toggle() {
        if (this.isOpen) this.hide();
        else await this.show();
    }

    async show() {
        if (!this.drawer) return;
        this.drawer.classList.remove('collapsed');
        this.isOpen = true;

        // Appliquer l'expansion au layout global
        const leftPanels = document.getElementById('ws-left-panels');
        if (leftPanels) leftPanels.classList.add('stitch-expanded');

        // Masquer le badge
        const badgeStitch = document.getElementById('badge-stitch');
        if (badgeStitch) badgeStitch.classList.add('badge-hidden');

        // Masquer le bouton FRD Editor (via body class pour sécurité)
        document.body.classList.add('stitch-open');

        await this.updateStatus();
        await this.loadSession();
    }

    hide() {
        if (!this.drawer) return;
        this.drawer.classList.add('collapsed');
        this.isOpen = false;
        
        const leftPanels = document.getElementById('ws-left-panels');
        if (leftPanels) leftPanels.classList.remove('stitch-expanded');

        const badgeStitch = document.getElementById('badge-stitch');
        if (badgeStitch) badgeStitch.classList.remove('badge-hidden');

        document.body.classList.remove('stitch-open');
    }

    async updateStatus() {
        if (!this.statusBadge) return;

        try {
            const res = await fetch('/api/stitch/status');
            const data = await res.json();

            this.isConnected = data.connected;
            this.statusBadge.textContent = data.connected ? 'connecté' : (data.api_key_set ? 'clé présente' : 'non configuré');
            this.statusBadge.style.color = data.connected ? '#8cc63f' : '#9a9a98';
            this.statusBadge.style.borderColor = data.connected ? '#8cc63f' : '#e5e5e5';
        } catch (err) {
            this.statusBadge.textContent = 'erreur status';
            this.statusBadge.style.color = '#ddb0b0';
        }
    }

    async loadSession() {
        const projectTitleEl = document.getElementById('ws-stitch-project-title');
        const screensContainer = document.getElementById('ws-stitch-screens-list');

        try {
            const res = await fetch('/api/stitch/session');
            if (!res.ok) {
                // Session non liée ou erreur
                if (projectTitleEl) projectTitleEl.textContent = 'Projet non lié';
                if (screensContainer) {
                    screensContainer.innerHTML = `
                        <div class="text-[10px] text-slate-400 italic mb-2">
                            Aucun projet Stitch connecté.
                        </div>
                        <div class="text-[10px] text-slate-400">
                            Importez un écran via le formulaire ci-dessous pour lier un projet.
                        </div>
                    `;
                }
                return;
            }

            const data = await res.json();

            if (!data.linked) {
                if (projectTitleEl) projectTitleEl.textContent = 'Projet non lié';
                if (screensContainer) {
                    screensContainer.innerHTML = '<div class="text-[10px] text-slate-400 italic">Aucun projet Stitch lié. Importez un écran pour commencer.</div>';
                }
                return;
            }

            // Afficher le titre du projet
            if (projectTitleEl) {
                projectTitleEl.textContent = data.project_title || data.project_id;
                // Lien "changer" discret
                const changeLink = document.createElement('a');
                changeLink.href = '#';
                changeLink.className = 'text-[9px] text-slate-400 underline ml-2';
                changeLink.textContent = 'changer';
                changeLink.onclick = (e) => {
                    e.preventDefault();
                    this.showManualForm();
                };
                projectTitleEl.appendChild(changeLink);
            }

            // Auto-fill project_id
            this.projectIdInput.value = data.project_id;

            // Afficher les écrans
            if (screensContainer) {
                screensContainer.innerHTML = '';
                const screens = data.screens || [];

                if (screens.length === 0) {
                    screensContainer.innerHTML = '<div class="text-[10px] text-slate-400 italic">Aucun écran dans ce projet Stitch.</div>';
                } else {
                    screens.forEach(screen => {
                        const el = document.createElement('div');
                        el.className = 'text-[11px] py-1 border-b border-[#e5e5e5] flex items-center justify-between';

                        const isLocal = screen.local;
                        const dotColor = isLocal ? '#8cc63f' : '#9a9a98';
                        const dotLabel = isLocal ? 'importé' : 'Stitch';
                        const actionLabel = isLocal ? '→ ouvrir dans Wire' : '→ importer';

                        el.innerHTML = `
                            <div class="flex items-center gap-2">
                                <span style="color: ${dotColor};">●</span>
                                <span style="color: ${isLocal ? '#3d3d3c' : '#9a9a98'};">${screen.title}</span>
                            </div>
                            <span class="text-[9px] cursor-pointer underline" style="color: ${isLocal ? '#8cc63f' : '#9a9a98'};" data-action="${isLocal ? 'open' : 'import'}" data-stitch-id="${screen.stitch_id}" data-local-file="${screen.local_file || ''}">${actionLabel}</span>
                        `;

                        // Event listeners sur les actions
                        const actionBtn = el.querySelector('[data-action]');
                        actionBtn.onclick = () => {
                            const action = actionBtn.dataset.action;
                            if (action === 'import') {
                                this.importScreen(screen.stitch_id);
                            } else if (action === 'open') {
                                this.openInWire(actionBtn.dataset.localFile);
                            }
                        };

                        screensContainer.appendChild(el);
                    });
                }

                if (data.offline) {
                    const offlineBadge = document.createElement('div');
                    offlineBadge.className = 'text-[9px] text-slate-400 italic mt-2';
                    offlineBadge.textContent = '⚠ hors-ligne — données en cache';
                    screensContainer.appendChild(offlineBadge);
                }
            }

        } catch (err) {
            console.error("[WsStitch] loadSession fail:", err);
            if (projectTitleEl) projectTitleEl.textContent = 'erreur session';
            if (screensContainer) screensContainer.innerHTML = '<div class="text-[10px] italic" style="color: #ddb0b0;">Erreur lors du chargement de la session.</div>';
        }
    }

    async importScreen(stitchId) {
        const projectId = this.projectIdInput.value.trim();
        if (!projectId || !stitchId) {
            this.showFeedback("Project ID ou Screen ID manquant.", "error");
            return;
        }

        this.showFeedback("Importation en cours...");

        try {
            const res = await fetch('/api/stitch/pull', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ project_id: projectId, screen_name: stitchId })
            });

            if (!res.ok) throw new Error(await res.text());

            const data = await res.json();
            this.showFeedback(`✓ ${data.imported}`, "success");

            // Rafraîchir la session
            await this.loadSession();

            // Rafraîchir la liste des imports dans le workspace
            if (window.fetchWorkspaceImports) window.fetchWorkspaceImports();

        } catch (err) {
            console.error("[WsStitch] importScreen fail:", err);
            this.showFeedback("Erreur lors de l'importation.", "error");
        }
    }

    openInWire(localFile) {
        if (!localFile) {
            this.showFeedback("Fichier local introuvable.", "error");
            return;
        }
        // Naviguer vers l'écran dans le workspace
        if (window.loadImport) {
            window.loadImport(localFile);
        } else {
            this.showFeedback(`Ouverture de ${localFile} dans Wire...`, "info");
        }
    }

    showManualForm() {
        // Afficher le formulaire manuel pour saisir project_id
        const manualSection = document.getElementById('ws-stitch-manual-form');
        if (manualSection) {
            manualSection.style.display = 'block';
            this.projectIdInput.focus();
        }
    }

    async listScreens() {
        const projectId = this.projectIdInput.value.trim();
        if (!projectId) {
            this.showFeedback("Veuillez saisir un Project ID.", "error");
            return;
        }

        this.showFeedback("Récupération des écrans...");
        this.screensList.innerHTML = '<div class="text-[10px] text-slate-400 italic">Chargement...</div>';

        try {
            const res = await fetch(`/api/stitch/screens?project_id=${projectId}`);
            if (!res.ok) throw new Error(await res.text());
            
            const data = await res.json();
            const screens = data.screens || [];
            
            this.screensList.innerHTML = '';
            if (screens.length === 0) {
                this.screensList.innerHTML = '<div class="text-[10px] text-slate-400 italic">Aucun écran trouvé.</div>';
            } else {
                screens.forEach(screen => {
                    const name = screen.name || screen.id;
                    const el = document.createElement('div');
                    el.className = 'text-[11px] cursor-pointer py-1 border-b border-[#e5e5e5] transition-colors';
                    el.style.color = '#3d3d3c';
                    el.onmouseenter = () => { el.style.color = '#8cc63f'; };
                    el.onmouseleave = () => { el.style.color = '#3d3d3c'; };
                    el.textContent = name;
                    el.onclick = () => {
                        this.screenNameInput.value = name;
                    };
                    this.screensList.appendChild(el);
                });
            }
            this.showFeedback(`${screens.length} écrans trouvés.`);
        } catch (err) {
            console.error("[WsStitch] listScreens fail:", err);
            this.screensList.innerHTML = '';
            this.showFeedback("Erreur lors de la récupération.", "error");
        }
    }

    async pull() {
        // Utilise maintenant importScreen qui est session-aware
        const projectId = this.projectIdInput.value.trim();
        const screenName = this.screenNameInput.value.trim();

        if (!projectId || !screenName) {
            this.showFeedback("Project ID et Screen Name requis.", "error");
            return;
        }

        await this.importScreen(screenName);
    }

    showFeedback(text, type = "info") {
        if (!this.feedback) return;
        this.feedback.textContent = text;
        this.feedback.style.color = type === "error" ? "#ddb0b0" : (type === "success" ? "#8cc63f" : "#9a9a98");
    }

    _autoFillProjectId() {
        // Tentative de lecture du manifest du screen actif
        const activeId = window.wsCanvas?.activeScreenId;
        if (activeId) {
            const shell = document.getElementById(activeId);
            if (shell && shell.dataset.manifest) {
                try {
                    const manifest = JSON.parse(shell.dataset.manifest);
                    if (manifest.stitch_project_id) {
                        this.projectIdInput.value = manifest.stitch_project_id;
                    }
                } catch(e) {}
            }
        }
    }

    async push() {
        const projectId = this.projectIdInput.value.trim();
        const intent = this.intentInput.value.trim();

        if (!projectId || !intent) {
            this.showFeedback("Project ID et Intention requis.", "error");
            return;
        }

        this.btnPush.disabled = true;
        this.btnPush.style.opacity = '0.5';
        this.showFeedback(" Sullivan initie la boucle Stitch...");

        try {
            const res = await fetch('/api/stitch/push', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    project_id: projectId, 
                    screen_intent: intent 
                })
            });

            if (!res.ok) throw new Error(await res.text());
            const { task_id } = await res.json();
            
            this.pollTask(task_id);
        } catch (err) {
            console.error("[WsStitch] push fail:", err);
            this.showFeedback("Échec de l'envoi.", "error");
            this.btnPush.disabled = false;
            this.btnPush.style.opacity = '1';
        }
    }

    async pollTask(taskId) {
        const interval = setInterval(async () => {
            try {
                const res = await fetch(`/api/stitch/task/${taskId}`);
                const status = await res.json();

                if (status.success === true) {
                    clearInterval(interval);
                    this.showFeedback("✓ Génération terminée !", "success");
                    this.btnPush.disabled = false;
                    this.btnPush.style.opacity = '1';
                    
                    if (status.data && status.data.previewUrl) {
                        this.feedback.innerHTML += ` <a href="${status.data.previewUrl}" target="_blank" class="underline text-violet-500">Ouvrir dans Stitch</a>`;
                    }
                } else if (status.success === false) {
                    clearInterval(interval);
                    this.showFeedback(`Erreur: ${status.error}`, "error");
                    this.btnPush.disabled = false;
                    this.btnPush.style.opacity = '1';
                } else {
                    // Update current step comment
                    this.showFeedback(status.comment || "Génération en cours...");
                }
            } catch (err) {
                clearInterval(interval);
                this.showFeedback("Erreur de polling.", "error");
                this.btnPush.disabled = false;
                this.btnPush.style.opacity = '1';
            }
        }, 1500);
    }
}

// Exposer pour ws_main
window.WsStitch = WsStitch;
