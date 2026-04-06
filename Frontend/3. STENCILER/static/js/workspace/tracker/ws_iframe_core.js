/**
 * ws_iframe_core.js — Phase 1 de l'Aether Core Architecture
 * Tracker injecté au cœur de l'iFrame pour observer le DOM, manipuler la maquette et communiquer avec WsInspect (Host).
 */
(function() {
    // Piège 2 : Garde anti-double injection (si document.write recrée le doc)
    if (window.__aetherTrackerLoaded) return;
    window.__aetherTrackerLoaded = true;

    let lastHover = null;
    let selectedEl = null;
    let lastSelectedEl = null;
    let activeMode = 'select';
    let isDragging = false;
    let isDrawing = false;
    let startX, startY;
    let initialTransformX = 0, initialTransformY = 0;
    let ghostFrame = null;

    function scanAtomicOrgans() {
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_COMMENT, null, false);
        let node;
        while(node = walker.nextNode()) {
            const comment = node.nodeValue.trim();
            if (comment.length > 5 && !comment.includes('-->')) {
                let nextEl = node.nextElementSibling;
                while (nextEl && ['SCRIPT', 'STYLE'].includes(nextEl.tagName)) nextEl = nextEl.nextElementSibling;
                if (nextEl) nextEl.setAttribute('data-atomic-organ', comment);
            }
        }
    }
    scanAtomicOrgans();

    const editBtn = document.createElement('button');
    editBtn.id = 'ws-in-preview-edit-btn';
    editBtn.innerHTML = '<svg style="width:12px;height:12px;margin-right:6px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/></svg> Edit code';
    editBtn.style.cssText = 'position: fixed; display: none; z-index: 999999; background: #fff; color: #64748b; border: 1px solid #e2e8f0; padding: 6px 12px; font-size: 11px; font-family: "Source Sans 3", sans-serif; font-weight: 600; border-radius: 6px; cursor: pointer; align-items: center; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); transform: translateY(-100%); transition: opacity 0.2s;';
    document.body.appendChild(editBtn);

    // Fix: Stop propagation to prevent body.onmousedown from hiding the button before the click
    editBtn.onmousedown = (e) => {
        e.stopPropagation();
        if (selectedEl) {
            const rect = selectedEl.getBoundingClientRect();
            sendClickMessage(selectedEl, rect);
        }
    };

    window.addEventListener('message', (e) => {
        // Piège 3: Les listeners restent inchangés pour correspondre à ceux du WsInspect (Host)
        if (e.data.type === 'inspect-tool-change') {
            activeMode = e.data.mode;
            
            // Clean up old classes
            document.body.classList.remove('mode-audit', 'mode-front-dev', 'mode-construct');
            
            if (activeMode === 'audit') document.body.classList.add('mode-audit');
            if (activeMode === 'front-dev') document.body.classList.add('mode-front-dev');
            if (activeMode === 'construct') document.body.classList.add('mode-construct');
            
            document.body.style.cursor = 
                (activeMode === 'text') ? 'text' :
                (activeMode === 'frame') ? 'crosshair' :
                (activeMode === 'drag') ? 'grab' :
                (activeMode === 'audit') ? 'crosshair' :
                (activeMode === 'front-dev') ? 'alias' :
                (activeMode === 'colors') ? 'copy' :
                (activeMode === 'place-img') ? 'copy' : 'default';
        }
        if (e.data.type === 'inspect-clear-selection') clearSelection();
        if (e.data.type === 'inspect-undo') {
            document.body.innerHTML = e.data.snapshot;
            scanAtomicOrgans(); document.body.appendChild(editBtn);
        }
        if (e.data.type === 'inspect-apply-color') { 
            const _ct = selectedEl || lastSelectedEl; 
            if (_ct) _ct.style.backgroundColor = e.data.color; 
        }
        if (e.data.type === 'inspect-apply-typo') {
            const target = selectedEl || lastSelectedEl;
            if (target) {
                target.style.fontFamily = e.data.font;
                target.style.fontSize = e.data.size + 'px';
                target.style.fontWeight = e.data.weight;
            }
        }
        if (e.data.type === 'inspect-ready-to-place-image') {
            takeSnapshot();
            const img = document.createElement('img');
            img.src = e.data.src; img.style.position = 'absolute';
            img.style.left = (window.lastClickX || 100) + 'px'; img.style.top = (window.lastClickY || 100) + 'px';
            img.style.maxWidth = '200px'; document.body.appendChild(img);
        }
        if (e.data.type === 'inspect-update-dom') {
             if (e.origin !== window.location.origin) return;
             takeSnapshot();
             const target = document.querySelector(e.data.selector);
             if (target) {
                 const parser = new DOMParser();
                 const doc = parser.parseFromString(e.data.html, 'text/html');
                 const newEl = doc.body.firstChild;
                 if (newEl) target.replaceWith(newEl);
             }
        }
        if (e.data.type === 'inspect-apply-effects') {
            const target = selectedEl || lastSelectedEl;
            if (target) {
                // Mapping Shadows (Tailwind to CSS)
                const shadows = {
                    'none': 'none',
                    'shadow-sm': '0 1px 2px 0 rgb(0 0 0 / 0.05)',
                    'shadow-md': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
                    'shadow-lg': '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
                    'shadow-xl': '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
                    'shadow-2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)'
                };
                target.style.boxShadow = shadows[e.data.shadow] || 'none';
                target.style.borderRadius = e.data.radius;
                target.style.borderStyle = e.data.border;
                if (e.data.border !== 'none' && !target.style.borderWidth) {
                    target.style.borderWidth = '1px';
                    target.style.borderColor = 'rgba(0,0,0,0.1)';
                }
            }
        }
        if (e.data.type === 'highlight-intent') {
            const { id, selector, text, tag } = e.data;
            let el = id ? document.getElementById(id) : null;
            if (!el && selector) el = document.querySelector(selector);
            if (!el && text && tag) {
                const candidates = Array.from(document.getElementsByTagName(tag));
                el = candidates.find(c => c.textContent.includes(text));
            }
            if (el) {
                document.querySelectorAll('.intent-highlight').forEach(o => o.classList.remove('intent-highlight'));
                el.classList.add('intent-highlight');
                el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
        if (e.data.type === 'clear-highlights') {
            document.querySelectorAll('.intent-highlight').forEach(o => o.classList.remove('intent-highlight'));
        }
        if (e.data.type === 'ws-inject-nudges') {
            _renderNudges(e.data.nudges || []);
        }
        if (e.data.type === 'ws-clear-nudges') {
            document.querySelectorAll('.ws-nudge').forEach(n => n.remove());
        }
    });

    function _renderNudges(nudges) {
        document.querySelectorAll('.ws-nudge').forEach(n => n.remove());
        nudges.forEach(nudge => {
            const { selector, id, text, tag, status } = nudge;
            let el = id ? document.getElementById(id) : null;
            if (!el && selector) el = document.querySelector(selector);
            if (!el && text && tag) {
                const candidates = Array.from(document.getElementsByTagName(tag));
                el = candidates.find(c => c.textContent.includes(text));
            }
            if (!el) return;

            const rect = el.getBoundingClientRect();
            const dot = document.createElement('div');
            dot.className = 'ws-nudge ' + (status === 'ok' ? 'status-ok' : 'status-pending');
            dot.style.top = (window.scrollY + rect.top) + 'px';
            dot.style.left = (window.scrollX + rect.left) + 'px';
            dot.onclick = (e) => {
                e.stopPropagation();
                window.parent.postMessage({ type: 'ws-nudge-clicked', selector, id, intent: nudge.intent || nudge.inferred_intent }, '*');
            };
            document.body.appendChild(dot);
        });
    }

    function takeSnapshot() { window.parent.postMessage({ type: 'inspect-snapshot', html: document.body.innerHTML }, '*'); }

    function clearSelection() {
        if (selectedEl) selectedEl.classList.remove('organ-selected');
        selectedEl = null; editBtn.style.display = 'none';
        window.parent.postMessage({ type: 'inspect-selection-cleared' }, '*');
    }

    document.body.onmouseover = (e) => {
        if (activeMode !== 'select' && activeMode !== 'audit') return;
        const organ = e.target.closest('[data-atomic-organ]') || e.target;
        if (lastHover && lastHover !== selectedEl) lastHover.classList.remove('inspect-hover');
        if (organ && organ !== document.body && organ !== document.documentElement) { 
            organ.classList.add('inspect-hover'); 
            lastHover = organ; 
        } else {
            lastHover = null;
        }
    };

    document.body.onmousedown = (e) => {
        // All tools behavior
        if (activeMode === 'select' || activeMode === 'text' || activeMode === 'colors') {
            const organ = e.target.closest('[data-atomic-organ]');
            if (organ) {
                if (selectedEl) selectedEl.classList.remove('organ-selected');
                selectedEl = organ; lastSelectedEl = organ; selectedEl.classList.add('organ-selected');
                const rect = selectedEl.getBoundingClientRect();
                
                // Show "Edit Code" in Select/Construct/Front-Dev mode
                if (activeMode === 'select' || activeMode === 'construct' || activeMode === 'front-dev') {
                    editBtn.style.display = 'flex';
                    editBtn.style.top = rect.top + 'px';
                    editBtn.style.left = (rect.left + rect.width - 100) + 'px';
                } else {
                    editBtn.style.display = 'none';
                }
                
                isDragging = (activeMode === 'drag' || activeMode === 'select');
                startX = e.clientX; startY = e.clientY;
                const transform = getComputedStyle(selectedEl).transform;
                if (transform !== 'none') {
                    const matrix = transform.match(/matrix\(([^)]+)\)/)[1].split(', ');
                    initialTransformX = parseFloat(matrix[4] || 0); initialTransformY = parseFloat(matrix[5] || 0);
                } else { initialTransformX = initialTransformY = 0; }
                
                // Parent notification (Mode selectivity handled in parent)
                window.parent.postMessage({ type: 'inspect-organ-selected', tagName: selectedEl.tagName.toLowerCase(), selector: getSelector(selectedEl), rect: rect }, '*');
            } else if (activeMode === 'text') {
                // Nouveau texte si clic sur vide en mode T
                takeSnapshot();
                const span = document.createElement('span');
                span.innerText = 'Nouveau texte';
                span.contentEditable = 'true';
                span.style.position = 'absolute';
                span.style.left = e.clientX + 'px'; span.style.top = e.clientY + 'px';
                span.style.fontFamily = getComputedStyle(document.body).fontFamily;
                span.setAttribute('data-atomic-organ', 'Text Element');
                document.body.appendChild(span);
                span.focus();
            } else { clearSelection(); }
        }

        if (activeMode === 'frame') {
            takeSnapshot(); isDrawing = true;
            drawStartX = e.clientX; drawStartY = e.clientY;
            ghostFrame = document.createElement('div');
            ghostFrame.style.cssText = 'position: fixed; border: 2px dashed #A3CD54; background: rgba(163, 205, 84, 0.1); pointer-events: none; z-index: 9999;';
            ghostFrame.style.left = drawStartX + 'px'; ghostFrame.style.top = drawStartY + 'px';
            document.body.appendChild(ghostFrame);
        }

        if (activeMode === 'place-img') {
            window.lastClickX = e.clientX; window.lastClickY = e.clientY;
            window.parent.postMessage({ type: 'inspect-request-image-file' }, '*');
        }

        if (activeMode === 'audit') {
            const organ = e.target.closest('[data-atomic-organ]') || e.target;
            const rect = organ.getBoundingClientRect();
            window.parent.postMessage({ 
                type: 'inspect-wire-picked', 
                selector: getSelector(organ), 
                organName: organ.getAttribute('data-atomic-organ') || organ.tagName.toLowerCase(),
                rect: { top: rect.top, left: rect.left, width: rect.width, height: rect.height },
                html: organ.outerHTML
            }, '*');
            e.preventDefault();
            e.stopPropagation();
        }
    };

    document.body.onmousemove = (e) => {
        if (isDragging && selectedEl) {
            if (document.body.style.cursor !== 'grabbing') document.body.style.cursor = 'grabbing';
            const dx = e.clientX - startX; const dy = e.clientY - startY;
            // Backtick issue handled carefully
            selectedEl.style.transform = `translate(${initialTransformX + dx}px, ${initialTransformY + dy}px)`;
            const rect = selectedEl.getBoundingClientRect();
            if (editBtn.style.display !== 'none') {
                editBtn.style.top = rect.top + 'px'; editBtn.style.left = (rect.left + rect.width - 100) + 'px';
            }
        }
        if (isDrawing && ghostFrame) {
            const dx = e.clientX - drawStartX; const dy = e.clientY - drawStartY;
            ghostFrame.style.width = Math.abs(dx) + 'px'; ghostFrame.style.height = Math.abs(dy) + 'px';
            ghostFrame.style.left = (dx < 0 ? e.clientX : drawStartX) + 'px'; ghostFrame.style.top = (dy < 0 ? e.clientY : drawStartY) + 'px';
        }
    };

    document.body.onmouseup = () => {
        if (isDragging) {
            takeSnapshot();
            if (activeMode === 'select' || activeMode === 'drag') document.body.style.cursor = 'grab';
        }
        isDragging = false;
        if (isDrawing && ghostFrame) {
            const newDiv = document.createElement('div');
            newDiv.style.cssText = ghostFrame.style.cssText.replace('dashed', 'solid').replace('fixed', 'absolute');
            newDiv.style.pointerEvents = 'auto'; newDiv.setAttribute('data-atomic-organ', 'New Frame');
            document.body.appendChild(newDiv);
            document.body.removeChild(ghostFrame); ghostFrame = null; isDrawing = false;
            takeSnapshot();
        }
    };

    function sendClickMessage(el, rect) {
        window.parent.postMessage({
            type: 'inspect-click', selector: getSelector(el), tagName: el.tagName.toLowerCase(),
            organName: el.getAttribute('data-atomic-organ'), html: el.outerHTML,
            rect: { top: rect.top, left: rect.left, width: rect.width, height: rect.height }
        }, '*');
    }

    function getSelector(el) {
        if (el.id) return '#' + el.id;
        let path = []; while (el && el.parentElement) {
            let siblingIndex = 1; let sibling = el.previousElementSibling;
            while (sibling) { if (sibling.tagName === el.tagName) siblingIndex++; sibling = sibling.previousElementSibling; }
            path.unshift(el.tagName.toLowerCase() + ':nth-of-type(' + siblingIndex + ')'); el = el.parentElement;
        }
        return path.join(' > ');
    }

    const style = document.createElement('style');
    style.innerHTML = `
        .inspect-hover { outline: 2px dashed rgba(163, 205, 84, 0.4) !important; outline-offset: -2px; }
        .organ-selected { outline: 3px solid #A3CD54 !important; outline-offset: -3px; }
        .intent-highlight { outline: 4px solid #8cc63f !important; outline-offset: 2px; transition: outline 0.3s ease; animation: intent-pulse 1.5s infinite; }
        @keyframes intent-pulse { 0% { outline-color: #8cc63f; } 50% { outline-color: rgba(140, 198, 63, 0.3); } 100% { outline-color: #8cc63f; } }
        [contenteditable="true"]:focus { outline: none !important; }

        .ws-nudge {
            position: absolute; width: 12px; height: 12px; border-radius: 50%; z-index: 2147483647;
            cursor: pointer; pointer-events: auto; transform: translate(-50%, -50%);
            border: 2px solid #fff; box-shadow: 0 0 10px rgba(0,0,0,0.2);
            animation: nudge-pulse 1.5s infinite; transition: all 0.2s;
        }
        .ws-nudge.status-ok { background: #8cc63f; }
        .ws-nudge.status-pending { background: #fbbf24; }
        .ws-nudge:hover { transform: translate(-50%, -50%) scale(1.5); }
        @keyframes nudge-pulse {
            0% { box-shadow: 0 0 0 0 rgba(140, 198, 63, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(140, 198, 63, 0); }
            100% { box-shadow: 0 0 0 0 rgba(140, 198, 63, 0); }
        }

        /* Mode Wire Protection - Empêche la sélection de texte et force le curseur */
        body.mode-wire * {
            user-select: none !important;
            -webkit-user-select: none !important;
            cursor: crosshair !important;
        }
    `;
    document.head.appendChild(style);

})();
