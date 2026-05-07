/**
 * ManifestSullivan — M357: Sullivan logic for Manifest Editor
 * Externalized with strict refs injection.
 */
(function() {
    'use strict';
    
    let _refs = {};
    let _critiqueAnswers = {};
    let _currentSuggestions = [];

    /**
     * Mission M399/M400: Log un événement UX Sullivan vers le serveur
     */
    function _sullivanLog(event, data = {}) {
        const sess = _refs.getSession?.() || {};
        const pid = new URLSearchParams(window.location.search).get('project_id')
            || sess.active_project_id || sess.project_id;
        if (!pid) return;
        
        // M400: Injection systématique du contexte de positionnement
        const posData = {};
        if (_refs.editorEl) {
            const text = _refs.getManifestText();
            const caretPos = _refs.editorEl.selectionStart;
            const lines = text.substring(0, caretPos).split('\n');
            posData.line_idx = lines.length;
            posData.caret_offset = caretPos;
        }
        if (_refs.sullivanBoxEl) {
            const transform = _refs.sullivanBoxEl.style.transform;
            const m = transform.match(/translateY\((\d+)px\)/);
            posData.box_y = m ? parseInt(m[1]) : 0;
        }
        
        fetch('/api/ux-run/event', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-User-Token': sess.token || '' },
            body: JSON.stringify({ source: 'sullivan', event, project_id: pid, ...posData, ...data })
        }).catch(() => {}); // Fire-and-forget
    }

    /**
     * Mission 201 : Initialisation de Sullivan
     */
    function init(refs) {
        _refs = refs;
        _critiqueAnswers = {};
        _currentSuggestions = [];
        
        // M400: Activer le magnétisme fluide via CSS
        if (_refs.sullivanBoxEl) {
            _refs.sullivanBoxEl.style.transition = 'transform 0.5s cubic-bezier(0.16, 1, 0.3, 1)';
        }
    }

    /**
     * Append a chat bubble to history
     * M400: Ajout du mode 'typing' pour l'effet de frappe progressive
     */
    async function appendBubble(text, sender, useTyping = false) {
        if (!_refs.chatEl) return;
        const b = document.createElement('div');
        b.className = `p-2 rounded-lg text-[14px] max-w-[90%] ${sender === 'sullivan' ? 'bg-[#f7f6f2] self-start border border-[#e5e5e5]' : 'bg-slate-900 text-white self-end ml-auto'}`;
        
        if (sender === 'sullivan') {
            b.innerHTML = `<span class="font-bold text-[#8cc63f] mr-1">s.</span><span class="bubble-content"></span>`;
            const contentEl = b.querySelector('.bubble-content');
            
            if (useTyping && text.length > 20) {
                // Effet Smart Typing (M400)
                const chars = text.split('');
                let current = '';
                for (const char of chars) {
                    current += char;
                    contentEl.innerText = current;
                    await new Promise(r => setTimeout(r, Math.random() * 15 + 5));
                    _refs.chatEl.scrollTop = _refs.chatEl.scrollHeight;
                }
            } else {
                contentEl.innerHTML = text;
            }
        } else {
            b.innerText = text;
        }
        
        _refs.chatEl.appendChild(b);
        _refs.chatEl.scrollTop = _refs.chatEl.scrollHeight;
        return b;
    }

    /**
     * Send a manual message to Sullivan
     */
    async function sendSullivanMessage() {
        if (!_refs.inputEl) return;
        const msg = _refs.inputEl.value.trim();
        if (!msg) return;

        _sullivanLog('chat_sent', { mode: 'manifest_assist', message_len: msg.length });

        // Contextual caret position
        const caretPos = _refs.editorEl ? _refs.editorEl.selectionStart : 0;
        const fullText = _refs.getManifestText();
        const textBefore = fullText.substring(0, caretPos);
        const currentLine = textBefore.split('\n').pop() || '';

        appendBubble(msg, 'user');
        _refs.inputEl.value = '';

        const pending = await appendBubble('analyse...', 'sullivan');
        pending.classList.add('opacity-50', 'italic');

        try {
            const session = _refs.getSession();
            const res = await fetch('/api/sullivan/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-User-Token': session.token || ''
                },
                body: JSON.stringify({
                    message: msg,
                    mode: 'manifest_assist',
                    project_id: session.active_project_id || session.project_id || null,
                    context: `l'utilisateur travaille sur le manifest. ligne actuelle : "${currentLine}"\nmanifest complet :\n${fullText}`
                })
            });
            const data = await res.json();
            pending.remove();
            
            if (!res.ok) {
                _sullivanLog('chat_error', { mode: 'manifest_assist', error: data.detail || 'res.ok false' });
                appendBubble(`erreur serveur (${res.status}) : ${data.detail || JSON.stringify(data)}`, 'sullivan');
            } else {
                _sullivanLog('chat_ok', { mode: 'manifest_assist', response_type: data.function_call ? 'function_call' : 'text' });
                if (data.explanation || data.reply) {
                    appendBubble(data.explanation || data.reply, 'sullivan');
                }
                // M398: Gestion des function calls
                if (data.function_call) {
                    handleSullivanFunctionCall(data.function_call);
                }
            }
        } catch(e) {
            _sullivanLog('chat_error', { mode: 'manifest_assist', error: 'exception' });
            pending.remove();
            appendBubble('erreur de communication.', 'sullivan');
        }
    }

    /**
     * Launch automatic critique
     */
    async function launchCritique() {
        if (!_refs.chatEl) return;
        
        const session = _refs.getSession();
        const text = _refs.getManifestText().trim();
        if (!text || text.length < 10) return;

        // Reset
        _refs.chatEl.innerHTML = '';
        _critiqueAnswers = {};
        _currentSuggestions = [];
        
        const loading = await appendBubble('analyse de ton manifeste...', 'sullivan');
        loading.classList.add('opacity-50', 'italic');

        // M367: fix cache stale — résolution via /api/projects/active (token-based, impersonation-safe)
        let design_tokens = _refs.getDesignTokens() || {};
        try {
            const activeRes = await fetch('/api/projects/active', {
                headers: { 'X-User-Token': session.token || '' }
            });
            const activeProject = await activeRes.json();
            if (activeProject.id) {
                const freshRes = await fetch(`/api/projects/${activeProject.id}/manifest`, {
                    headers: { 'X-User-Token': session.token || '' }
                });
                const freshManifest = await freshRes.json();
                if (freshManifest.design_tokens) design_tokens = freshManifest.design_tokens;
            }
        } catch(e) {
            console.warn('[M367] Stale fallback:', e);
        }

        _sullivanLog('critique_launched');
        
        try {
            const res = await fetch('/api/sullivan/manifest-critique', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-User-Token': session.token || ''
                },
                body: JSON.stringify({
                    manifest_text: text,
                    design_tokens: design_tokens,
                    project_id: session.active_project_id || session.project_id || null
                })
            });
            const data = await res.json();
            loading.remove();

            if (data.questions && data.questions.length > 0) {
                _currentSuggestions = data.suggestions || [];
                // M394: On garde les assets validés en mémoire pour le chat/HCI
                _refs.validatedAssets = data.validated_assets || [];
                renderCritique(data.questions, _currentSuggestions);
            } else {
                appendBubble("ton manifeste semble solide, je n'ai pas de critique majeure pour le moment.", "sullivan");
            }
        } catch(e) {
            loading.remove();
            appendBubble("je n'ai pas réussi à analyser ton manifeste (erreur réseau).", "sullivan");
        }
    }

    /**
     * Render the Yes/No critique apparatus
     */
    function renderCritique(questions, suggestions) {
        appendBubble("j'ai lu tes intentions. pour t'aider à préciser ton design, réponds à ces quelques questions :", "sullivan");
        
        const wrap = document.createElement('div');
        wrap.className = 'flex flex-col gap-2 mt-2';
        
        // --- MISSION M385: Grouping logic ---
        const triggerQs = questions.filter(q => q.type === 'image_trigger');
        const assetQs = questions.filter(q => q.type === 'image_choice');
        const standardQs = questions.filter(q => q.type !== 'image_choice' && q.type !== 'image_trigger');

        const highFig = assetQs.filter(q => (q.figuration_score || 0) > 0.5);
        const lowFig = assetQs.filter(q => (q.figuration_score || 0) <= 0.5);

        const renderCard = (q) => {
            const card = document.createElement('div');
            card.className = 'critique-question flex flex-col gap-1 p-2 rounded-[12px] bg-[#f7f6f2] border border-[#e5e5e5] transition-all';
            
            if (q.type === 'image_trigger') {
                card.innerHTML = `
                    <span class="text-[14px] text-slate-500 italic">${q.text || ''}</span>
                    <button class="btn-img-trigger mt-1 px-3 py-1 rounded-[8px] text-[13px] border border-[#e5e5e5] hover:bg-[#8cc63f]/10 hover:border-[#8cc63f] transition-all self-start">analyser les illustrations</button>
                `;
                card.querySelector('.btn-img-trigger').onclick = async () => {
                    const sess = _refs.getSession();
                    const btn = card.querySelector('.btn-img-trigger');
                    const project_id = new URLSearchParams(window.location.search).get('project_id')
                        || sess.active_project_id || sess.project_id;
                    btn.textContent = 'analyse en cours...';
                    btn.disabled = true;
                    if (window.UxRun) window.UxRun.log('ACTION', 'img_trigger_clicked', { project_id });
                    try {
                        const res = await fetch('/api/imports/extract-tokens', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json', 'X-User-Token': sess.token || '' },
                            body: JSON.stringify({ project_id })
                        });
                        if (window.UxRun) window.UxRun.log('RESULT', `img_trigger:${res.ok ? 'ok' : 'fail'}:${res.status}`, { project_id });
                        if (!res.ok) throw new Error(`extract-tokens ${res.status}`);
                        await new Promise(r => setTimeout(r, 15000));
                        launchCritique();
                    } catch (e) {
                        if (window.UxRun) window.UxRun.log('FRICTION', `img_trigger_error:${e.message}`, { project_id });
                        btn.textContent = 'échec — réessayer';
                        btn.disabled = false;
                    }
                };
            } else if (q.type === 'image_choice') {
                const isHigh = (q.figuration_score || 0) > 0.5;
                const rec = isHigh ? 'png' : 'vector';
                
                card.innerHTML = `
                    <div class="flex justify-between items-center px-1">
                        <span class="text-[13px] text-slate-500 italic">${q.text.toLowerCase()}</span>
                        <span class="text-[10px] font-bold opacity-30 uppercase tracking-tighter">score: ${Math.round((q.figuration_score||0.5)*100)}%</span>
                    </div>
                    <div class="flex gap-3 items-center">
                        <img src="${q.specimen ? q.specimen.specimen_url : ''}" class="w-20 h-20 rounded-[8px] object-cover border border-[#e5e5e5] bg-white shrink-0" onerror="this.style.display='none'">
                        <div class="flex flex-col gap-1.5 grow">
                            <button class="btn-img-choice w-full text-left px-3 py-1.5 rounded-[8px] text-[13px] border border-[#e5e5e5] transition-all ${rec==='png'?'bg-white border-[#8cc63f] border-2 shadow-sm':''}" data-val="png">
                                <span class="block font-medium">garder en image (png)</span>
                                <span class="text-[10px] opacity-60">recommandé pour figuratif</span>
                            </button>
                            <button class="btn-img-choice w-full text-left px-3 py-1.5 rounded-[8px] text-[13px] border border-[#e5e5e5] transition-all ${rec==='vector'?'bg-white border-[#8cc63f] border-2 shadow-sm':''}" data-val="vector">
                                <span class="block font-medium">tenter en vecteur (code)</span>
                                <span class="text-[10px] opacity-60">recommandé pour ui/icons</span>
                            </button>
                        </div>
                    </div>
                `;

                const btns = card.querySelectorAll('.btn-img-choice');
                btns.forEach(btn => {
                    btn.onclick = () => {
                        const val = btn.dataset.val;
                        _sullivanLog('asset_choice', { asset: q.text, choice: val });
                        _critiqueAnswers[q.id] = val;
                        
                        btns.forEach(b => b.className = 'btn-img-choice w-full text-left px-3 py-1.5 rounded-[8px] text-[13px] border border-[#e5e5e5] bg-white transition-all');
                        btn.className = 'btn-img-choice w-full text-left px-3 py-1.5 rounded-[8px] text-[13px] font-bold bg-[#8cc63f] text-white border-[#8cc63f] transition-all';
                        
                        const choiceStr = val === 'png' ? `${q.text} : garder png` : `${q.text} : tenter vecteurs`;
                        const manifestText = _refs.getManifestText();
                        let newText = manifestText;
                        const sectionTitle = "### Arbitrage Sullivan (M393)";
                        const regex = new RegExp(`${q.text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\s*:\\s*[^\\n]+`);
                        
                        // Si l'élément est déjà présent (peu importe où), on le met à jour
                        if (newText.match(regex)) {
                            newText = newText.replace(regex, choiceStr);
                        } else {
                            // Sinon, on l'ajoute à la fin dans la section dédiée
                            if (!newText.includes(sectionTitle)) {
                                newText = newText.trim() + "\n\n" + sectionTitle + "\n" + choiceStr;
                            } else {
                                // On l'ajoute à la fin de la section existante
                                newText = newText.trim() + "\n" + choiceStr;
                            }
                        }
                        
                        if (_refs.applyManifest) _refs.applyManifest(newText);
                        
                        // M393: Persistance du choix pour mémorisation Sullivan
                        const sess = _refs.getSession?.() || {};
                        fetch('/api/sullivan/persist-asset-choice', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json', 'X-User-Token': sess.token || '' },
                            body: JSON.stringify({ 
                                project_id: sess.active_project_id || sess.project_id, 
                                asset_description: q.text, 
                                choice: val 
                            })
                        }).catch(e => console.warn('[M393] Persist failed:', e));

                        if (Object.keys(_critiqueAnswers).length === questions.length) {
                            showSuggestions(suggestions, _critiqueAnswers);
                        }
                    };
                });
            } else {
                card.innerHTML = `
                    <span class="text-[14px] text-slate-600">${q.id}. ${(q.text || '').toLowerCase()}</span>
                    <div class="flex gap-2">
                        <button class="btn-oui px-3 py-1 rounded-[8px] text-[14px] border border-[#e5e5e5] hover:bg-[#8cc63f]/10 hover:border-[#8cc63f] transition-all">oui</button>
                        <button class="btn-non px-3 py-1 rounded-[8px] text-[14px] border border-[#e5e5e5] hover:bg-slate-100 transition-all">non</button>
                    </div>
                `;
                const btnOui = card.querySelector('.btn-oui');
                const btnNon = card.querySelector('.btn-non');
                const handleAnswer = (val) => {
                    _sullivanLog('critique_answer', { question_id: q.id, answer: val });
                    _critiqueAnswers[q.id] = val;
                    if (val === 'oui') {
                        btnOui.className = 'btn-oui px-3 py-1 rounded-[8px] text-[14px] font-bold bg-[#8cc63f] text-white border-[#8cc63f] transition-all';
                        btnNon.className = 'btn-non px-3 py-1 rounded-[8px] text-[14px] border border-[#e5e5e5] bg-white transition-all';
                    } else {
                        btnNon.className = 'btn-non px-3 py-1 rounded-[8px] text-[14px] font-bold bg-slate-800 text-white border-slate-800 transition-all';
                        btnOui.className = 'btn-oui px-3 py-1 rounded-[8px] text-[14px] border border-[#e5e5e5] bg-white transition-all';
                    }
                    if (Object.keys(_critiqueAnswers).length === questions.length) showSuggestions(suggestions, _critiqueAnswers);
                };
                btnOui.onclick = () => handleAnswer('oui');
                btnNon.onclick = () => handleAnswer('non');
            }
            return card;
        };

        // Render sections
        if (triggerQs.length > 0) triggerQs.forEach(q => wrap.appendChild(renderCard(q)));

        if (highFig.length > 0) {
            const h = document.createElement('div');
            h.className = 'text-[11px] font-bold text-slate-400 uppercase tracking-widest mt-2 px-1 mb-1';
            h.innerText = '🖼️ Contenu Illustratif (PNG)';
            wrap.appendChild(h);
            highFig.forEach(q => wrap.appendChild(renderCard(q)));
        }

        if (lowFig.length > 0) {
            const h = document.createElement('div');
            h.className = 'text-[11px] font-bold text-slate-400 uppercase tracking-widest mt-2 px-1 mb-1';
            h.innerText = '✨ Éléments Graphiques (Code)';
            wrap.appendChild(h);
            lowFig.forEach(q => wrap.appendChild(renderCard(q)));
        }

        if (standardQs.length > 0) {
            const h = document.createElement('div');
            h.className = 'text-[11px] font-bold text-slate-400 uppercase tracking-widest mt-2 px-1 mb-1';
            h.innerText = '🧭 Cadrage Technique';
            wrap.appendChild(h);
            standardQs.forEach(q => wrap.appendChild(renderCard(q)));
        }

        if (_refs.chatEl) {
            _refs.chatEl.appendChild(wrap);
            _refs.chatEl.scrollTop = _refs.chatEl.scrollHeight;
        }
    }

    /**
     * Show suggestions based on user answers
     */
    function showSuggestions(suggestions, answers) {
        _sullivanLog('suggestions_shown', { count: suggestions.length });
        const old = document.getElementById('sullivan-critique-suggestions');
        if (old) old.remove();

        const wrap = document.createElement('div');
        wrap.id = 'sullivan-critique-suggestions';
        wrap.className = 'mt-3 flex flex-col gap-2';
        wrap.innerHTML = `<span class="text-[13px] text-slate-400 uppercase tracking-wide">suggestions</span>`;

        suggestions.forEach(s => {
            const answer = answers[s.id] || 'non';
            const item = document.createElement('div');
            item.className = `suggestion-item text-[14px] p-2 rounded-[10px] transition-all ${
                answer === 'oui' 
                ? 'bg-[#8cc63f]/10 border border-[#8cc63f]/30 text-slate-700 font-medium' 
                : 'bg-white border border-[#e5e5e5] text-slate-700'
            }`;
            
            item.innerHTML = `
                <div class="flex justify-between items-start gap-4">
                    <span><span class="font-medium text-[13px] opacity-60 mr-1">${s.id}.</span> ${s.text.toLowerCase()}</span>
                    <button class="btn-apply-suggestion shrink-0 text-[13px] px-2 py-0.5 rounded-[6px] border border-slate-200 hover:border-[#8cc63f] hover:bg-[#8cc63f]/10 hover:text-[#8cc63f] transition-all" data-id="${s.id}">appliquer</button>
                </div>
            `;
            
            const applyBtn = item.querySelector('.btn-apply-suggestion');
            applyBtn.onclick = () => {
                _sullivanLog('apply_suggestion', { id: s.id });
                applySuggestion(applyBtn, s.text, s.id);
            };

            wrap.appendChild(item);
        });

        if (_refs.chatEl) {
            _refs.chatEl.appendChild(wrap);
            _refs.chatEl.scrollTop = _refs.chatEl.scrollHeight;
        }
    }

    /**
     * Apply a suggestion by rewriting the manifest via LLM
     */
    async function applySuggestion(btn, text, id) {
        if (btn.disabled) return;
        
        const originalText = btn.innerText;
        btn.disabled = true;
        btn.innerText = 'en cours...';
        btn.classList.add('opacity-50');

        try {
            const manifestText = _refs.getManifestText();
            const session = _refs.getSession();
            
            const res = await fetch('/api/sullivan/manifest-apply', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-User-Token': session.token || ''
                },
                body: JSON.stringify({
                    manifest_text: manifestText,
                    suggestion: text,
                    suggestion_id: id
                })
            });
            const data = await res.json();

            if (data.proposed_manifest) {
                if (_refs.applyManifest) {
                    _refs.applyManifest(data.proposed_manifest);
                    btn.innerText = 'appliqué ✓';
                    btn.className = 'btn-apply-suggestion shrink-0 text-[13px] px-2 py-0.5 rounded-[6px] border border-[#8cc63f] transition-all opacity-50 bg-[#8cc63f]/10 text-[#8cc63f]';
                    btn.disabled = true;
                }
            } else {
                btn.innerText = 'erreur';
                console.error('[Sullivan] Apply failed:', data.error);
                setTimeout(() => {
                    btn.disabled = false;
                    btn.innerText = originalText;
                    btn.classList.remove('opacity-50');
                }, 2000);
            }
        } catch(e) {
            btn.innerText = 'erreur réseau';
            console.error('[Sullivan] Network error:', e);
            setTimeout(() => {
                btn.disabled = false;
                btn.innerText = originalText;
                btn.classList.remove('opacity-50');
            }, 2000);
        }
    }

    /**
     * Update Sullivan position relative to editor caret
     */
    function updatePosition() {
        if (!_refs.editorEl || !_refs.sullivanBoxEl) return;
        
        const pos = _refs.editorEl.selectionStart;
        if (!window.ManifestBox || typeof window.ManifestBox.getCaretCoordinates !== 'function') return;

        const coords = window.ManifestBox.getCaretCoordinates(_refs.editorEl, pos);
        let targetY = coords.top - _refs.editorWrapEl.scrollTop;
        const maxY = _refs.editorWrapEl.clientHeight - _refs.sullivanBoxEl.offsetHeight - 20;
        targetY = Math.max(0, Math.min(targetY, maxY));
        
        _refs.sullivanBoxEl.style.transform = `translateY(${targetY}px)`;
    }

    /**
     * Bootstrap the storyboard (M395)
     */
    async function bootstrapStoryboard(btn) {
        if (!btn) return;
        const sess = _refs.getSession?.() || {};
        const originalText = btn.textContent;
        
        btn.disabled = true;
        btn.textContent = '...';
        
        _sullivanLog('storyboard_bootstrap_started');
        
        try {
            const res = await fetch('/api/sullivan/bootstrap-storyboard', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-User-Token': sess.token || ''
                },
                body: JSON.stringify({ project_id: sess.active_project_id || sess.project_id })
            });
            const data = await res.json();
            
            if (data.ok) {
                btn.textContent = `storyboard (${data.screens} écrans)`;
                btn.classList.add('text-[#8cc63f]', 'border-[#8cc63f]');
                appendBubble(`j'ai généré un storyboard de ${data.screens} écrans à partir de tes intentions. tu peux maintenant naviguer entre les écrans.`, 'sullivan');
                
                // M396: Rafraîchir le storyboard du canvas pour synchroniser la navigation
                if (window.wsCanvas) {
                    window.wsCanvas.loadStoryboard();
                }
            } else {
                btn.textContent = 'erreur';
                btn.disabled = false;
                setTimeout(() => { btn.textContent = originalText; }, 2000);
            }
        } catch(e) {
            btn.textContent = 'erreur réseau';
            btn.disabled = false;
            setTimeout(() => { btn.textContent = originalText; }, 2000);
        }
    }

    /**
     * Handle Gemini Function Calls (M398)
     */
    async function handleSullivanFunctionCall(fc) {
        if (!fc || !fc.name) return;
        const { name, args } = fc;
        console.log('[M398] Handling Sullivan function call:', name, args);
        
        _sullivanLog('function_call_received', { name, args });

        if (name === 'summon_screen') {
            openSummonPanel(args.screen_id, args.focus);
        } else if (name === 'swap_asset') {
            handleSwapAsset(args.asset_description, args.new_choice);
        } else if (name === 'storyboard_interview') {
            startStoryboardInterview(args.start_screen_id);
        }
    }

    /**
     * Start the Storyboard Interview (M397)
     */
    async function startStoryboardInterview(startId = null) {
        const sess = _refs.getSession?.() || {};
        const loading = await appendBubble(`préparation de l'interview storyboard...`, 'sullivan');
        loading.classList.add('opacity-50', 'italic');
        
        try {
            const res = await fetch(`/api/projects/${sess.active_project_id || sess.project_id}/manifest`, {
                headers: { 'X-User-Token': sess.token || '' }
            });
            const manifest = await res.json();
            loading.remove();
            
            const storyboard = manifest.storyboard || [];
            if (storyboard.length === 0) {
                appendBubble(`ton storyboard est vide. utilise le bouton "storyboard" pour le générer d'abord.`, 'sullivan');
                return;
            }
            
            _refs.interviewStoryboard = storyboard;
            _refs.interviewIdx = startId ? storyboard.findIndex(s => s.screen_id === startId) : 0;
            if (_refs.interviewIdx === -1) _refs.interviewIdx = 0;
            
            renderInterviewCard();
            
        } catch(e) {
            loading.remove();
            appendBubble(`erreur lors du lancement de l'interview.`, 'sullivan');
        }
    }

    /**
     * Render the interactive interview card (M397)
     */
    function renderInterviewCard() {
        const screen = _refs.interviewStoryboard[_refs.interviewIdx];
        if (!screen) return;
        
        const old = document.getElementById('storyboard-interview-card');
        if (old) old.remove();
        
        const card = document.createElement('div');
        card.id = 'storyboard-interview-card';
        card.className = 'mt-3 p-4 rounded-[20px] bg-slate-900 text-white shadow-2xl flex flex-col gap-4 animate-in slide-in-from-right-4 duration-300';
        
        card.innerHTML = `
            <div class="flex items-center justify-between opacity-60">
                <span class="text-[10px] font-bold uppercase tracking-widest">storyboard interview</span>
                <span class="text-[10px]">${_refs.interviewIdx + 1} / ${_refs.interviewStoryboard.length}</span>
            </div>
            
            <div class="flex flex-col gap-1">
                <h4 class="text-[16px] font-bold text-[#8cc63f]">${screen.screen_name || screen.screen_id}</h4>
                <p class="text-[13px] text-slate-300 italic opacity-80 leading-relaxed">"${screen.intent || 'pas d\'intention précisée'}"</p>
            </div>
            
            <div class="flex gap-2">
                <button id="int-btn-summon" class="flex-1 py-2 rounded-[10px] bg-white/10 hover:bg-white/20 text-[12px] font-bold transition-all">voir l'écran</button>
                <button id="int-btn-next" class="px-4 py-2 rounded-[10px] bg-[#8cc63f] text-slate-900 text-[12px] font-bold hover:bg-[#a3cd54] transition-all">suivant →</button>
            </div>
            
            <div class="pt-2 border-t border-white/10 flex items-center justify-between">
                <button id="int-btn-prev" class="text-[11px] opacity-40 hover:opacity-100 transition-opacity" ${_refs.interviewIdx === 0 ? 'disabled' : ''}>← précédent</button>
                <button id="int-btn-close" class="text-[11px] text-red-400 opacity-60 hover:opacity-100 transition-opacity">quitter</button>
            </div>
        `;
        
        card.querySelector('#int-btn-summon').onclick = () => openSummonPanel(screen.screen_id);
        card.querySelector('#int-btn-next').onclick = () => {
            if (_refs.interviewIdx < _refs.interviewStoryboard.length - 1) {
                _refs.interviewIdx++;
                renderInterviewCard();
                openSummonPanel(_refs.interviewStoryboard[_refs.interviewIdx].screen_id);
            } else {
                appendBubble(`interview terminée. tous les écrans ont été passés en revue.`, 'sullivan');
                card.remove();
            }
        };
        card.querySelector('#int-btn-prev').onclick = () => {
            if (_refs.interviewIdx > 0) {
                _refs.interviewIdx--;
                renderInterviewCard();
                openSummonPanel(_refs.interviewStoryboard[_refs.interviewIdx].screen_id);
            }
        };
        card.querySelector('#int-btn-close').onclick = () => card.remove();
        
        _refs.chatEl.appendChild(card);
        _refs.chatEl.scrollTop = _refs.chatEl.scrollHeight;
        
        // Auto-summon the first time
        openSummonPanel(screen.screen_id);
    }

    /**
     * Open a floating summon panel (M398)
     */
    async function openSummonPanel(screenId, focus) {
        const sess = _refs.getSession?.() || {};
        const loading = await appendBubble(`récupération de l'écran ${screenId}...`, 'sullivan');
        loading.classList.add('opacity-50', 'italic');
        
        try {
            const res = await fetch(`/api/manifest/storyboard-screen?project_id=${sess.active_project_id || sess.project_id}&screen_id=${screenId}`, {
                headers: { 'X-User-Token': sess.token || '' }
            });
            const data = await res.json();
            loading.remove();
            
            if (data.screen_id) {
                _sullivanLog('summon_ok', { screen_id: screenId });
                renderSummonCard(data, focus);
            } else {
                _sullivanLog('summon_error', { screen_id: screenId, error: 'not_found' });
                appendBubble(`désolé, je ne trouve pas l'écran ${screenId}.`, 'sullivan');
            }
        } catch(e) {
            loading.remove();
            _sullivanLog('summon_error', { screen_id: screenId, error: 'network' });
            appendBubble(`erreur lors de la récupération de l'écran.`, 'sullivan');
        }
    }

    /**
     * Render a visual card for the summoned screen
     */
    function renderSummonCard(screen, focus) {
        const card = document.createElement('div');
        card.className = 'summon-card mt-2 p-3 rounded-[16px] bg-white border border-[#8cc63f]/30 shadow-xl flex flex-col gap-2 overflow-hidden animate-in fade-in zoom-in duration-300';
        
        const title = screen.screen_name || screen.screen_id;
        card.innerHTML = `
            <div class="flex items-center justify-between border-b border-slate-50 pb-2 mb-1">
                <span class="text-[12px] font-bold uppercase tracking-widest text-[#8cc63f]">summon: ${title}</span>
                <span class="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-500">${screen.forged ? 'forgé' : 'storyboard'}</span>
            </div>
            <div class="preview-area w-full aspect-video rounded-[8px] bg-slate-50 border border-slate-100 overflow-hidden relative group">
                ${screen.html_content ? 
                    `<iframe class="w-[200%] h-[200%] scale-50 origin-top-left pointer-events-none" srcdoc="${screen.html_content.replace(/"/g, '&quot;')}"></iframe>` :
                    `<div class="flex flex-col items-center justify-center h-full text-slate-300 gap-2">
                        <svg class="w-8 h-8 opacity-20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                        <span class="text-[11px] font-medium opacity-50 uppercase tracking-tighter">visuel non disponible (storyboard)</span>
                     </div>`
                }
                <div class="absolute inset-0 bg-gradient-to-t from-white/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-2">
                    <button class="w-full py-1.5 rounded-[8px] bg-slate-900 text-white text-[12px] font-bold shadow-lg transform translate-y-2 group-hover:translate-y-0 transition-transform">ouvrir dans le forgeur</button>
                </div>
            </div>
            ${focus ? `<div class="text-[12px] text-slate-500 bg-slate-50 p-2 rounded-[8px] border-l-2 border-[#8cc63f]"><strong>focus:</strong> ${focus}</div>` : ''}
        `;
        
        card.querySelector('button')?.addEventListener('click', () => {
            // TODO: M396 Navigation vers cet écran
            appendBubble(`je t'emmène sur l'écran ${title}...`, 'sullivan');
        });
        
        _refs.chatEl.appendChild(card);
        _refs.chatEl.scrollTop = _refs.chatEl.scrollHeight;
    }

    /**
     * Handle Asset Swap (M398)
     */
    async function handleSwapAsset(desc, choice) {
        const sess = _refs.getSession?.() || {};
        appendBubble(`compris, je passe <strong>${desc}</strong> en mode <strong>${choice.toUpperCase()}</strong>.`, 'sullivan');
        
        try {
            // 1. Reset (M394)
            await fetch('/api/sullivan/reset-asset-choice', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-User-Token': sess.token || '' },
                body: JSON.stringify({ project_id: sess.active_project_id || sess.project_id, asset_description: desc })
            });
            
            // 2. Persist (M393)
            await fetch('/api/sullivan/persist-asset-choice', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-User-Token': sess.token || '' },
                body: JSON.stringify({ project_id: sess.active_project_id || sess.project_id, asset_description: desc, choice: choice })
            });
            
            appendBubble(`c'est fait. tu peux relancer la forge pour voir le changement.`, 'sullivan');
            
            // Mettre à jour le manifest visuellement si possible
            if (_refs.applyManifest) {
                 const manifestText = _refs.getManifestText();
                 const choiceStr = choice === 'png' ? `${desc} : garder png` : `${desc} : tenter vecteurs`;
                 const regex = new RegExp(`${desc.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\s*:\\s*[^\\n]+`);
                 const newText = manifestText.replace(regex, choiceStr);
                 _refs.applyManifest(newText);
            }
            
        } catch(e) {
            appendBubble(`désolé, je n'ai pas pu effectuer le swap d'asset.`, 'sullivan');
        }
    }

    // Export API
    window.ManifestSullivan = {
        init,
        launchCritique,
        sendSullivanMessage,
        appendBubble,
        updatePosition,
        bootstrapStoryboard
    };

})();
