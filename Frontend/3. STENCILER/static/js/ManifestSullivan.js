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
     * Initialize Sullivan with shared refs
     * @param {Object} refs - { chatEl, inputEl, editorEl, sullivanBoxEl, editorWrapEl, getSession, getManifestText, getDesignTokens }
     */
    function init(refs) {
        _refs = refs;
        _critiqueAnswers = {};
        _currentSuggestions = [];
    }

    /**
     * Append a chat bubble to history
     */
    function appendBubble(text, sender) {
        if (!_refs.chatEl) return;
        const b = document.createElement('div');
        b.className = `p-2 rounded-lg text-[14px] max-w-[90%] ${sender === 'sullivan' ? 'bg-[#f7f6f2] self-start border border-[#e5e5e5]' : 'bg-slate-900 text-white self-end ml-auto'}`;
        
        if (sender === 'sullivan') {
            b.innerHTML = `<span class="font-bold text-[#8cc63f] mr-1">s.</span>${text}`;
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

        // Contextual caret position
        const caretPos = _refs.editorEl ? _refs.editorEl.selectionStart : 0;
        const fullText = _refs.getManifestText();
        const textBefore = fullText.substring(0, caretPos);
        const currentLine = textBefore.split('\n').pop() || '';

        appendBubble(msg, 'user');
        _refs.inputEl.value = '';

        const pending = appendBubble('analyse...', 'sullivan');
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
                appendBubble(`erreur serveur (${res.status}) : ${data.detail || JSON.stringify(data)}`, 'sullivan');
            } else if (data.explanation) {
                appendBubble(data.explanation, 'sullivan');
            } else if (data.reply) {
                appendBubble(data.reply, 'sullivan');
            } else {
                appendBubble(`réponse inattendue : ${JSON.stringify(data)}`, 'sullivan');
            }
        } catch(e) {
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
        
        const loading = appendBubble('analyse de ton manifeste...', 'sullivan');
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

        try {
            const res = await fetch('/api/sullivan/manifest-critique', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-User-Token': session.token || ''
                },
                body: JSON.stringify({
                    manifest_text: text,
                    design_tokens: design_tokens
                })
            });
            const data = await res.json();
            loading.remove();

            if (data.questions && data.questions.length > 0) {
                _currentSuggestions = data.suggestions || [];
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
        
        questions.forEach(q => {
            try {
            const card = document.createElement('div');
            card.className = 'critique-question flex flex-col gap-1 p-2 rounded-[12px] bg-[#f7f6f2] border border-[#e5e5e5] transition-all';

            if (q.type === 'image_trigger') {
                card.innerHTML = `
                    <span class="text-[14px] text-slate-500 italic">${q.text || ''}</span>
                    <button class="btn-img-trigger mt-1 px-3 py-1 rounded-[8px] text-[13px] border border-[#e5e5e5] hover:bg-[#8cc63f]/10 hover:border-[#8cc63f] transition-all self-start">analyser les illustrations</button>
                `;
                card.querySelector('.btn-img-trigger').onclick = async () => {
                    const sess = _refs.getSession ? _refs.getSession() : (JSON.parse(sessionStorage.getItem('homeos_impersonation')||'{}').token ? JSON.parse(sessionStorage.getItem('homeos_impersonation')||'{}') : JSON.parse(localStorage.getItem('homeos_session')||'{}'));
                    card.querySelector('.btn-img-trigger').textContent = 'analyse en cours...';
                    await fetch('/api/imports/extract-tokens', { method: 'POST', headers: { 'X-User-Token': sess.token || '' } });
                    await new Promise(r => setTimeout(r, 15000));
                    launchCritique();
                };
            } else if (q.type === 'image_choice') {
                // M367: Rendu par carte individuelle pour chaque asset
                if (q.specimen) {
                    card.innerHTML = `
                        <span class="text-[14px] text-slate-500 italic">${q.text.toLowerCase()}</span>
                        <img src="${q.specimen.specimen_url}" class="w-24 h-24 rounded-[8px] object-cover border border-[#e5e5e5] self-start mt-1">
                        <div class="flex gap-2 mt-1">
                            <button class="btn-img-choice px-3 py-1 rounded-[8px] text-[13px] border border-[#e5e5e5] hover:bg-[#8cc63f]/10 hover:border-[#8cc63f] transition-all" data-val="png">aplatir en image</button>
                            <button class="btn-img-choice px-3 py-1 rounded-[8px] text-[13px] border border-[#e5e5e5] hover:bg-[#8cc63f]/10 hover:border-[#8cc63f] transition-all" data-val="vector">tenter en vecteur</button>
                        </div>
                    `;
                }

                const btns = card.querySelectorAll('.btn-img-choice');
                btns.forEach(btn => {
                    btn.onclick = () => {
                        const val = btn.dataset.val;
                        _critiqueAnswers[q.id] = val;
                        
                        // Style toggle
                        btns.forEach(b => b.className = 'btn-img-choice px-3 py-1 rounded-[8px] text-[13px] border border-[#e5e5e5] bg-white transition-all');
                        btn.className = 'btn-img-choice px-3 py-1 rounded-[8px] text-[13px] font-bold bg-[#8cc63f] text-white border-[#8cc63f] transition-all';
                        
                        // Application au manifest (M367: injection ligne par ligne)
                        const manifestText = _refs.getManifestText();
                        let newText = manifestText;
                        const choiceStr = val === 'png' ? `${q.text} : garder png` : `${q.text} : tenter vecteurs`;
                        
                        // Injection intelligente juste après le titre ou au début
                        const regex = new RegExp(`${q.text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\s*:\\s*[^\\n]+`);
                        if (!newText.match(regex)) {
                            if (newText.startsWith('#')) {
                                const lines = newText.split('\n');
                                lines.splice(1, 0, choiceStr);
                                newText = lines.join('\n');
                            } else {
                                newText = choiceStr + '\n' + newText;
                            }
                        } else {
                            newText = newText.replace(regex, choiceStr);
                        }
                        
                        if (_refs.applyManifest) _refs.applyManifest(newText);
                        
                        if (Object.keys(_critiqueAnswers).length === questions.length) {
                            showSuggestions(suggestions, _critiqueAnswers);
                        }
                    };
                });
            } else {
                // Rendu standard Oui/Non
                card.innerHTML = `
                    <span class="text-[14px] text-slate-600">${q.id}. ${(q.text || '').toLowerCase()}</span>
                    <div class="flex gap-2">
                        <button class="btn-oui px-3 py-1 rounded-[8px] text-[14px] border border-[#e5e5e5] hover:bg-[#8cc63f]/10 hover:border-[#8cc63f] transition-all" data-id="${q.id}">oui</button>
                        <button class="btn-non px-3 py-1 rounded-[8px] text-[14px] border border-[#e5e5e5] hover:bg-slate-100 transition-all" data-id="${q.id}">non</button>
                    </div>
                `;

                const btnOui = card.querySelector('.btn-oui');
                const btnNon = card.querySelector('.btn-non');

                const handleAnswer = (val) => {
                    _critiqueAnswers[q.id] = val;
                    
                    if (val === 'oui') {
                        btnOui.className = 'btn-oui px-3 py-1 rounded-[8px] text-[14px] font-bold bg-[#8cc63f] text-white border-[#8cc63f] transition-all';
                        btnNon.className = 'btn-non px-3 py-1 rounded-[8px] text-[14px] border border-[#e5e5e5] bg-white transition-all';
                    } else {
                        btnNon.className = 'btn-non px-3 py-1 rounded-[8px] text-[14px] font-bold bg-slate-800 text-white border-slate-800 transition-all';
                        btnOui.className = 'btn-oui px-3 py-1 rounded-[8px] text-[14px] border border-[#e5e5e5] bg-white transition-all';
                    }

                    if (Object.keys(_critiqueAnswers).length === questions.length) {
                        showSuggestions(suggestions, _critiqueAnswers);
                    }
                };

                btnOui.onclick = () => handleAnswer('oui');
                btnNon.onclick = () => handleAnswer('non');
            }

            wrap.appendChild(card);
            } catch(err) { console.error('[renderCritique] question error:', q, err); }
        });

        if (_refs.chatEl) {
            _refs.chatEl.appendChild(wrap);
            _refs.chatEl.scrollTop = _refs.chatEl.scrollHeight;
        }
    }

    /**
     * Show suggestions based on user answers
     */
    function showSuggestions(suggestions, answers) {
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
            applyBtn.onclick = () => applySuggestion(applyBtn, s.text, s.id);

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

    // Export API
    window.ManifestSullivan = {
        init,
        launchCritique,
        sendSullivanMessage,
        appendBubble,
        updatePosition
    };

})();
