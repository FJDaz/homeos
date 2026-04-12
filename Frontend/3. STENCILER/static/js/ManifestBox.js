/**
 * ManifestBox — M292: Manifest Editor + Sullivan (Contextual) + Signets
 * Remplace l'ancien panneau par un éditeur complet avec layout 3 colonnes.
 */
(function() {
    'use strict';
    
    let panel = null;
    let manifestData = null;
    let isSignetsOpen = true;
    let saveTimeout = null;
    
    // UI Refs
    let els = {};

    // --- UTILS ---
    function getSession() {
        return JSON.parse(localStorage.getItem('homeos_session') || '{}');
    }

    /**
     * Calcule la position relative (X, Y) du curseur dans un textarea.
     * Utilise un div miroir invisible pour calculer la hauteur du texte.
     */
    function getCaretCoordinates(element, position) {
        const div = document.createElement('div');
        const style = window.getComputedStyle(element);
        
        const properties = [
            'direction', 'boxSizing', 'width', 'height', 'overflowX', 'overflowY',
            'borderTopWidth', 'borderRightWidth', 'borderBottomWidth', 'borderLeftWidth',
            'paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft',
            'fontStyle', 'fontVariant', 'fontWeight', 'fontStretch', 'fontSize',
            'lineHeight', 'fontFamily', 'textAlign', 'textTransform', 'textIndent',
            'textDecoration', 'letterSpacing', 'wordSpacing', 'tabSize', 'whiteSpace',
            'wordBreak', 'wordWrap'
        ];
        properties.forEach(prop => div.style[prop] = style[prop]);
        
        div.style.position = 'absolute';
        div.style.top = '-9999px';
        div.style.left = '-9999px';
        // Important pour conserver les espaces et retours à la ligne
        div.style.whiteSpace = 'pre-wrap';
        
        const textUpToCaret = element.value.substring(0, position);
        div.textContent = textUpToCaret;
        
        const span = document.createElement('span');
        span.textContent = element.value.substring(position) || '.';
        div.appendChild(span);
        
        document.body.appendChild(div);
        const coords = { top: span.offsetTop, left: span.offsetLeft, height: span.offsetHeight };
        document.body.removeChild(div);
        
        return coords;
    }

    // --- API ---
    /**
     * Charge le manifest d'un projet spécifié ou du projet actif.
     */
    async function loadManifest(targetProjectId = null) {
        try {
            const session = getSession();
            const projectId = targetProjectId || session.active_project_id || session.project_id;
            if (!projectId) return;

            const res = await fetch(`/api/projects/${projectId}/manifest`);
            if (res.ok) {
                manifestData = await res.json();
                
                // Si pas de raw_content : utiliser description si dispo, sinon générer depuis les écrans
                if (!manifestData.raw_content) {
                    if (manifestData.description) {
                        manifestData.raw_content = manifestData.description;
                    } else if (manifestData.screens && manifestData.screens.length > 0) {
                        let md = `# Manifeste : ${manifestData.name || 'Projet'}\n\n`;
                        manifestData.screens.forEach(s => {
                            md += `## ${s.name || 'Écran'}\n- Type: ${s.type || s.archetype_label}\n\n`;
                        });
                        manifestData.raw_content = md;
                    }
                }
            } else {
                // Initialise un nouveau manifest vide
                manifestData = {
                    name: 'Nouveau Projet',
                    raw_content: '# Mon Manifeste\n\nDécrivez votre intention ici...'
                };
            }
        } catch(e) {
            console.error('Erreur chargement manifest', e);
        }
    }

    async function saveManifestDeferred() {
        const text = els.editor.value;
        const session = getSession();
        const projectId = session.active_project_id || session.project_id;
        if (!projectId) return;

        const payload = manifestData || {};
        payload.raw_content = text;
        // Mettre à jour le nom si on a un # Titre principal
        const matchTitle = text.match(/^#\s+(.+)$/m);
        if (matchTitle) payload.name = matchTitle[1];

        try {
            await fetch(`/api/projects/${projectId}/manifest`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json', 'X-User-Token': session.token || '' },
                body: JSON.stringify(payload)
            });
            console.log('[WsManifestEditor] saved');
            updateSideSummary(text);
        } catch(e) {
            console.error('Erreur save', e);
        }
    }

    /**
     * Met à jour le résumé dans le panneau latéral persistant.
     */
    function updateSideSummary(text) {
        const el = document.getElementById('manifest-summary-content');
        if (!el) return;

        if (!text || text.trim() === '') {
            el.innerHTML = '<span class="italic opacity-50">Manifeste vide...</span>';
            return;
        }

        // Nettoyer un peu le texte (virer les gros titres MD pour le résumé)
        let summary = text
            .replace(/^#+\s+/gm, '') // Enlever les #
            .split('\n')
            .filter(line => line.trim().length > 0)
            .slice(0, 3) // 3 premières lignes non vides
            .join(' / ');

        if (summary.length > 120) summary = summary.substring(0, 117) + '...';
        el.innerText = summary;
    }

    function onTextChange() {
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(saveManifestDeferred, 1000);
        updateSignets();
        updateSullivanPosition();
    }

    // --- SULLIVAN (Contextual floating chat) ---
    async function sendSullivanMessage() {
        const msg = els.sullivanInput.value.trim();
        if (!msg) return;

        // Context line
        const caretPos = els.editor.selectionStart;
        const textBefore = els.editor.value.substring(0, caretPos);
        const currentLine = textBefore.split('\n').pop() || '';

        appendBubble(msg, 'user');
        els.sullivanInput.value = '';

        const pending = appendBubble('analyse...', 'sullivan');
        pending.classList.add('opacity-50', 'italic');

        try {
            const res = await fetch('/api/sullivan/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: msg,
                    mode: 'manifest_assist',
                    context: `L'utilisateur travaille sur le manifest. Ligne actuelle : "${currentLine}"\nTout le texte:\n${els.editor.value}`
                })
            });
            const data = await res.json();
            pending.remove();
            if (data.explanation) appendBubble(data.explanation, 'sullivan');
        } catch(e) {
            pending.remove();
            appendBubble('Erreur de communication.', 'sullivan');
        }
    }

    function appendBubble(text, sender) {
        const b = document.createElement('div');
        b.className = `p-2 rounded-lg text-[12px] max-w-[90%] ${sender === 'sullivan' ? 'bg-[#f7f6f2] self-start border border-[#e5e5e5]' : 'bg-slate-900 text-white self-end ml-auto'}`;
        if (sender === 'sullivan') {
            b.innerHTML = `<span class="font-bold text-[#8cc63f] mr-1">S.</span>${text}`;
        } else {
            b.innerText = text;
        }
        els.sullivanHist.appendChild(b);
        els.sullivanHist.scrollTop = els.sullivanHist.scrollHeight;
        return b;
    }

    function updateSullivanPosition() {
        if (!els.editor || !els.sullivanBox) return;
        
        const pos = els.editor.selectionStart;
        const coords = getCaretCoordinates(els.editor, pos);
        
        // Calculer l'offset Y en retranchant le scroll de la zone parente de l'editeur
        let targetY = coords.top - els.editorWrap.scrollTop;
        
        // Contraindre Sullivan pour ne pas sortir de l'ecran (padding 40px en haut, bottom constraint)
        const maxY = els.editorWrap.clientHeight - els.sullivanBox.offsetHeight - 20;
        targetY = Math.max(0, Math.min(targetY, maxY));
        
        // Animation fluide
        els.sullivanBox.style.transform = `translateY(${targetY}px)`;
    }

    // --- SIGNETS (TOC) ---
    function updateSignets() {
        const text = els.editor.value;
        const lines = text.split('\n');
        
        els.signetsList.innerHTML = '';
        
        let positionInStr = 0;
        let count = 0;

        lines.forEach(line => {
            const len = line.length + 1; // +1 for newline
            const match = line.match(/^(#{1,3})\s+(.*)$/);
            if (match) {
                const level = match[1].length;
                const title = match[2];
                const pos = positionInStr;
                
                const btn = document.createElement('button');
                btn.className = `text-left w-full truncate py-1 hover:text-homeos-green transition-colors ${level === 1 ? 'font-bold text-[#3d3d3c] text-[13px] mt-2' : level === 2 ? 'text-[12px] text-slate-500 pl-2' : 'text-[11px] text-slate-400 pl-4'}`;
                btn.innerText = title;
                btn.onclick = () => {
                    els.editor.focus();
                    els.editor.setSelectionRange(pos, pos);
                    
                    // Scroll to position
                    const coords = getCaretCoordinates(els.editor, pos);
                    els.editorWrap.scrollTo({ top: coords.top - 40, behavior: 'smooth' });
                    
                    updateSullivanPosition();
                };
                els.signetsList.appendChild(btn);
                count++;
            }
            positionInStr += len;
        });

        if (count === 0) {
            els.signetsList.innerHTML = '<span class="text-slate-300 italic">Aucun chapitre (#, ##)...</span>';
        }
    }

    function toggleSignets() {
        isSignetsOpen = !isSignetsOpen;
        if (isSignetsOpen) {
            els.signetsCol.style.width = '250px';
            els.signetsTitle.style.display = 'block';
            els.signetsList.style.display = 'flex';
            els.signetsToggle.innerHTML = `
                <svg class="w-[18px] h-[18px]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
            `;
        } else {
            els.signetsCol.style.width = '40px';
            els.signetsTitle.style.display = 'none';
            els.signetsList.style.display = 'none';
            els.signetsToggle.innerHTML = `
                <svg class="w-[18px] h-[18px]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
            `;
        }
    }

    // --- UI BUILD ---
    function buildPanel() {
        if (panel) return;

        panel = document.createElement('div');
        panel.id = 'manifestbox-panel';
        panel.style.cssText = `
            position: fixed;
            top: 5vh;
            left: 5vw;
            width: 90vw;
            height: 90vh;
            z-index: 2000;
            background: #fdfdfc;
            border: 1px solid #e5e5e5;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
            display: none;
            flex-direction: column;
            overflow: hidden;
            font-family: 'Inter', sans-serif;
        `;

        panel.innerHTML = `
            <div id="manifestbox-handle" class="h-[40px] bg-white border-b border-[#e5e5e5] px-4 flex items-center justify-between cursor-grab select-none">
                <span class="text-[12px] font-black uppercase tracking-[0.15em] text-[#8cc63f]">manifest editor</span>
                <div class="flex items-center gap-3">
                    <button id="manifestbox-reload" class="p-1 px-2 text-slate-400 hover:text-[#8cc63f] transition-all flex items-center gap-1" title="Recharger depuis le serveur">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h5M20 20v-5h-5M4 13a8.1 8.1 0 0015.4 3M20 11a8.1 8.1 0 00-15.4-3"/></svg>
                        <span class="text-[9px] font-bold uppercase tracking-widest hidden sm:inline">Recharger</span>
                    </button>
                    <button id="manifestbox-validate" class="px-3 py-1 bg-[#8cc63f] text-white text-[11px] font-bold rounded-full uppercase tracking-widest hover:bg-[#7ab536] transition-all">
                        Valider le manifeste
                    </button>
                    <button id="manifestbox-close" class="text-slate-400 hover:text-red-500 transition-colors">
                        <svg class="w-[18px] h-[18px]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                    </button>
                </div>
            </div>
            
            <div class="flex-1 flex flex-row overflow-hidden relative">
                
                <!-- EDITOR COL -->
                <div id="manifest-editor-wrap" class="flex-1 relative p-10 overflow-y-auto scrollbar-hide" style="scroll-behavior: smooth;">
                    <!-- SULLIVAN PAPER FLOAT -->
                    <div id="manifest-sullivan-box" class="absolute right-10 top-10 w-[320px] bg-white rounded-xl border border-slate-100 shadow-[0_20px_40px_-15px_rgba(0,0,0,0.1)] flex flex-col z-20" style="transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1); max-height:400px;">

                        <!-- TOP INPUT (M292 spec) -->
                        <div class="p-3 bg-white border-b border-slate-50 flex items-center gap-2 rounded-t-xl z-10 sticky top-0 shadow-sm">
                            <div class="w-[10px] h-[10px] rounded-full bg-homeos-green animate-pulse shrink-0"></div>
                            <input type="text" id="manifest-sullivan-input" placeholder="Sullivan, une remarque sur ce passage ?"
                                   class="flex-1 border-none bg-transparent text-[13px] font-medium text-slate-700 outline-none placeholder:text-slate-300">
                        </div>

                        <!-- HISTORY -->
                        <div id="manifest-sullivan-hist" class="flex-1 overflow-y-auto p-3 flex flex-col gap-2 max-h-[300px] scrollbar-hide bg-slate-50/30">
                            <!-- bulles injectées -->
                            <div class="p-2 rounded-lg text-[12px] bg-[#f7f6f2] self-start border border-[#e5e5e5] max-w-[90%]">
                                <span class="font-bold text-[#8cc63f] mr-1">S.</span>Je lis par-dessus votre épaule. Saisissez du texte par ici.
                            </div>
                        </div>

                    </div>

                    <!-- MINI TOOLBAR (M282) -->
                    <div class="flex items-center gap-1 mb-3 px-1">
                        <button class="manifest-toolbar-btn" data-md="# " title="Titre 1"><span class="text-[12px] font-bold text-[#3d3d3c]">H1</span></button>
                        <button class="manifest-toolbar-btn" data-md="## " title="Titre 2"><span class="text-[11px] font-bold text-[#3d3d3c]">H2</span></button>
                        <button class="manifest-toolbar-btn" data-md="### " title="Titre 3"><span class="text-[10px] font-bold text-[#3d3d3c]">H3</span></button>
                        <span class="text-[#e5e5e5] mx-1">|</span>
                        <button class="manifest-toolbar-btn" data-md="- " title="Liste à puces"><span class="text-[12px] text-[#9a9a98]">•</span></button>
                        <button class="manifest-toolbar-btn" data-md="1. " title="Liste numérotée"><span class="text-[10px] text-[#9a9a98]">1.</span></button>
                        <span class="text-[#e5e5e5] mx-1">|</span>
                        <button class="manifest-toolbar-btn" data-md="**" title="Gras"><span class="text-[12px] font-bold text-[#3d3d3c]">B</span></button>
                        <button class="manifest-toolbar-btn" data-md="*" title="Italique"><span class="text-[12px] italic text-[#3d3d3c]">I</span></button>
                    </div>

                    <textarea id="manifest-editor-textarea" spellcheck="false"
                              placeholder="# Votre Manifeste..."
                              class="w-[calc(100%-360px)] min-h-[150%] max-w-[800px] bg-transparent border-none outline-none text-[#3d3d3c] focus:ring-0 resize-none font-mono text-[13px] leading-relaxed tracking-tight"
                              style="font-family: 'JetBrains Mono', 'Monaco', monospace; margin-bottom:50vh;"></textarea>
                </div>

                <!-- SIGNETS COL -->
                <div id="manifest-signets-col" class="w-[250px] bg-[#fcfaf7] border-left border-white shadow-[-5px_0_15px_rgba(0,0,0,0.02)] flex flex-col transition-all duration-300 shrink-0 z-30 relative">
                    <div class="h-[40px] px-3 flex items-center justify-between border-b border-[#f0eee4] bg-[#fcfaf7]">
                        <span id="manifest-signets-title" class="text-[11px] font-bold uppercase tracking-widest text-slate-400">chapitres (toc)</span>
                        <button id="manifest-signets-toggle" class="p-1 rounded-md text-slate-400 hover:bg-slate-100 transition-colors">
                            <svg class="w-[18px] h-[18px]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                        </button>
                    </div>
                    <div id="manifest-signets-list" class="flex-1 overflow-y-auto p-4 flex flex-col gap-1.5 scrollbar-hide">
                        <!-- signets -->
                    </div>
                    <!-- DESIGN TOKENS SWATCHES (M293) -->
                    <div id="manifest-tokens-section" class="border-t border-[#f0eee4] bg-[#fcfaf7] p-3 hidden">
                        <div class="text-[9px] font-bold uppercase tracking-widest text-slate-400 mb-2">tokens extraits</div>
                        <div id="manifest-tokens-palette" class="flex gap-1.5 flex-wrap"></div>
                        <div id="manifest-tokens-info" class="text-[9px] text-slate-400 mt-1.5"></div>
                    </div>
                </div>

            </div>
        `;

        document.body.appendChild(panel);

        // Bind Refs
        els.editorWrap = document.getElementById('manifest-editor-wrap');
        els.editor = document.getElementById('manifest-editor-textarea');
        els.sullivanBox = document.getElementById('manifest-sullivan-box');
        els.sullivanInput = document.getElementById('manifest-sullivan-input');
        els.sullivanHist = document.getElementById('manifest-sullivan-hist');
        els.signetsCol = document.getElementById('manifest-signets-col');
        els.signetsList = document.getElementById('manifest-signets-list');
        els.signetsTitle = document.getElementById('manifest-signets-title');
        els.signetsToggle = document.getElementById('manifest-signets-toggle');

        // Listeners
        document.getElementById('manifestbox-close').onclick = hide;
        document.getElementById('manifestbox-validate').onclick = () => {
            saveManifestDeferred().then(() => hide());
        };
        
        const reloadBtn = document.getElementById('manifestbox-reload');
        if (reloadBtn) {
            reloadBtn.onclick = async () => {
                reloadBtn.classList.add('animate-spin');
                reloadBtn.style.pointerEvents = 'none';
                await loadManifest();
                if (manifestData && manifestData.raw_content) {
                    els.editor.value = manifestData.raw_content;
                    updateSignets();
                    updateSullivanPosition();
                    updateSideSummary(manifestData.raw_content);
                }
                setTimeout(() => {
                    reloadBtn.classList.remove('animate-spin');
                    reloadBtn.style.pointerEvents = 'auto';
                }, 600);
            };
        }

        els.signetsToggle.onclick = toggleSignets;
        
        els.editor.addEventListener('input', onTextChange);
        els.editor.addEventListener('click', updateSullivanPosition);
        els.editor.addEventListener('keyup', (e) => {
            if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Enter'].includes(e.key)) {
                updateSullivanPosition();
            }
        });

        els.editorWrap.addEventListener('scroll', updateSullivanPosition);

        els.sullivanInput.onkeydown = (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendSullivanMessage();
            }
        };

        // Drag Header
        const handle = document.getElementById('manifestbox-handle');
        if (handle) {
            let dragging = false, ox = 0, oy = 0;
            handle.addEventListener('mousedown', (e) => {
                dragging = true;
                ox = e.clientX - panel.getBoundingClientRect().left;
                oy = e.clientY - panel.getBoundingClientRect().top;
                handle.style.cursor = 'grabbing';
            });
            document.addEventListener('mousemove', (e) => {
                if (!dragging) return;
                panel.style.left = (e.clientX - ox) + 'px';
                panel.style.top = (e.clientY - oy) + 'px';
            });
            document.addEventListener('mouseup', () => {
                dragging = false;
                handle.style.cursor = 'grab';
            });
        }

        // M282: Toolbar buttons — insert markdown at cursor
        document.querySelectorAll('.manifest-toolbar-btn').forEach(btn => {
            btn.onclick = (e) => {
                e.preventDefault();
                const md = btn.dataset.md;
                if (!md || !els.editor) return;
                const ta = els.editor;
                const start = ta.selectionStart;
                const end = ta.selectionEnd;
                const selected = ta.value.substring(start, end);

                if (md === '**' || md === '*') {
                    // Wrap selection or insert at cursor
                    ta.value = ta.value.substring(0, start) + md + selected + md + ta.value.substring(end);
                    ta.selectionStart = ta.selectionEnd = start + md.length + selected.length;
                } else {
                    // Insert at start of line
                    const lineStart = ta.value.lastIndexOf('\n', start - 1) + 1;
                    ta.value = ta.value.substring(0, lineStart) + md + ta.value.substring(lineStart);
                    ta.selectionStart = ta.selectionEnd = start + md.length;
                }
                ta.focus();
                onTextChange();
            };
        });
    }

    async function show() {
        buildPanel();
        panel.style.display = 'flex';
        await loadManifest();
        if (manifestData) {
            els.editor.value = manifestData.raw_content || manifestData.description || '';
        }
        updateSignets();
        
        // Timeout pour s'assurer que le composant est bien affiché avant de calculer les coords
        setTimeout(updateSullivanPosition, 100);
        
        // Focus sur l'éditeur
        els.editor.focus();
    }

    /**
     * Charge et affiche le manifeste pour un projet spécifique (Mission 282 V2).
     */
    async function showForProject(projectId) {
        console.log('[ManifestBox] Remote activating project:', projectId);
        if (!panel) buildPanel();
        panel.style.display = 'flex';
        await loadManifest(projectId);
        if (manifestData) {
            els.editor.value = manifestData.raw_content || manifestData.description || '';
            updateSideSummary(manifestData.raw_content);
        } else {
            els.editor.value = '';
        }
        updateSignets();
        setTimeout(updateSullivanPosition, 100);
        els.editor.focus();
    }

    // API Publique
    window.ManifestBox = { show, hide, toggle, showForProject };
    
    // Initialisation automatique du résumé latéral (M292B)
    document.addEventListener('DOMContentLoaded', async () => {
        const session = getSession();
        const projectId = session.active_project_id || session.project_id;
        if (projectId) {
            await loadManifest();
            if (manifestData) updateSideSummary(manifestData.raw_content);
        }
    });

    console.log('[WsManifestEditor] ✅ Override OK');
})();