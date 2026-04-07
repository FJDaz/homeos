/**
 * ws_iframe_core.js — Phase 1 de l'Aether Core Architecture
 * Tracker injecté au cœur de l'iFrame pour observer le DOM, manipuler la maquette et communiquer avec WsInspect (Host).
 * Mission 200A : ID Engine — data-af-id sur tout élément significatif.
 * Mission 200B : Transactional Handshake — receipts pour chaque commande.
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

    // --- MISSION 200A : ID ENGINE ---
    // Hash court et stable pour un élément (tag + texte + position)
    function _hashElement(el) {
        const tag = el.tagName.toLowerCase();
        const text = (el.textContent || '').trim().slice(0, 30);
        const id = el.id || '';
        const cls = (el.className || '').toString().slice(0, 30);
        let raw = tag + id + cls + text;
        let hash = 0;
        for (let i = 0; i < raw.length; i++) {
            hash = ((hash << 5) - hash) + raw.charCodeAt(i);
            hash |= 0;
        }
        return 'af-' + Math.abs(hash).toString(36).slice(0, 8);
    }

    /**
     * Injecte data-af-id sur tous les éléments significatifs du DOM.
     - Skip: script, style, head, meta, link, noscript
     - Skip: éléments déjà avec data-af-id ou id HTML
     - Cible: éléments avec texte, classes, ou enfants visibles
     */
    function injectAfIds() {
        const SKIP_TAGS = new Set(['SCRIPT', 'STYLE', 'HEAD', 'META', 'LINK', 'NOSCRIPT', 'BR', 'HR']);
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT, null, false);
        let node;
        let count = 0;
        while (node = walker.nextNode()) {
            if (SKIP_TAGS.has(node.tagName)) continue;
            if (node.dataset && node.dataset.afId) continue; // déjà fait
            if (node.id) continue; // a déjà un id HTML

            // Élément significatif s'il a du texte direct, des classes, ou des enfants
            const hasText = node.childNodes && Array.from(node.childNodes).some(c => c.nodeType === Node.TEXT_NODE && c.textContent.trim().length > 0);
            const hasClasses = node.className && node.className.toString().trim().length > 0;
            const hasChildren = node.children && node.children.length > 0;

            if (hasText || hasClasses || hasChildren) {
                node.setAttribute('data-af-id', _hashElement(node));
                count++;
            }
        }
        return count;
    }

    // Injecter au chargement
    const idsInjected = injectAfIds();
    if (idsInjected > 0) console.log('[AetherTracker]', idsInjected, 'data-af-id injectés');

    function scanAtomicOrgans() {
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_COMMENT, null, false);
        let node;
        while(node = walker.nextNode()) {
            const comment = node.nodeValue.trim();
            if (comment.length > 5 && !comment.includes('-->')) {
                let nextEl = node.nextElementSibling;
                while (nextEl && ['SCRIPT', 'STYLE'].includes(nextEl.tagName)) nextEl = nextEl.nextElementSibling;
                if (nextEl) {
                    nextEl.setAttribute('data-atomic-organ', comment);
                    // M200A: aussi injecter data-af-id si absent
                    if (!nextEl.dataset.afId) nextEl.setAttribute('data-af-id', _hashElement(nextEl));
                }
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

    // --- MISSION 200B : TRANSACTIONAL HANDSHAKE ---
    // Envoie un receipt pour CHAQUE commande reçue du Host
    function _sendReceipt(transactionId, status, detail) {
        window.parent.postMessage({
            type: 'AF_RECEIPT',
            transactionId: transactionId,
            status: status,  // 'success' | 'error'
            detail: detail || null,
            ts: Date.now()
        }, '*');
    }

    // Vérifie si un élément est visible/cliquable (pas overlay)
    function _isElementVisible(el) {
        if (!el) return false;
        const rect = el.getBoundingClientRect();
        if (rect.width === 0 && rect.height === 0) return false;
        const style = getComputedStyle(el);
        if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') return false;
        // Check overlay
        const topEl = document.elementFromPoint(rect.left + rect.width / 2, rect.top + rect.height / 2);
        if (topEl && topEl !== el && !el.contains(topEl)) {
            return { visible: false, overlapped_by: topEl.tagName + (topEl.className ? '.' + topEl.className.toString().split(' ')[0] : '') };
        }
        return { visible: true };
    }

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

            // M200B: Receipt pour tool change
            if (e.data.transactionId) _sendReceipt(e.data.transactionId, 'success', { mode: activeMode });
        }
        if (e.data.type === 'inspect-clear-selection') {
            clearSelection();
            if (e.data.transactionId) _sendReceipt(e.data.transactionId, 'success');
        }
        if (e.data.type === 'inspect-undo') {
            try {
                document.body.innerHTML = e.data.snapshot;
                scanAtomicOrgans();
                document.body.appendChild(editBtn);
                injectAfIds(); // M200A: ré-injecter après undo
                if (e.data.transactionId) _sendReceipt(e.data.transactionId, 'success');
            } catch (err) {
                if (e.data.transactionId) _sendReceipt(e.data.transactionId, 'error', 'undo_failed: ' + err.message);
            }
        }
        if (e.data.type === 'inspect-apply-color') {
            const _ct = selectedEl || lastSelectedEl;
            if (_ct) {
                _ct.style.backgroundColor = e.data.color;
                if (e.data.transactionId) _sendReceipt(e.data.transactionId, 'success');
            } else {
                if (e.data.transactionId) _sendReceipt(e.data.transactionId, 'error', 'no_element_selected');
            }
        }
        if (e.data.type === 'inspect-apply-typo') {
            const target = selectedEl || lastSelectedEl;
            if (target) {
                target.style.fontFamily = e.data.font;
                target.style.fontSize = e.data.size + 'px';
                target.style.fontWeight = e.data.weight;
                if (e.data.transactionId) _sendReceipt(e.data.transactionId, 'success');
            } else {
                if (e.data.transactionId) _sendReceipt(e.data.transactionId, 'error', 'no_element_selected');
            }
        }
        if (e.data.type === 'inspect-ready-to-place-image') {
            takeSnapshot();
            const img = document.createElement('img');
            img.src = e.data.src; img.style.position = 'absolute';
            img.style.left = (window.lastClickX || 100) + 'px'; img.style.top = (window.lastClickY || 100) + 'px';
            img.style.maxWidth = '200px'; document.body.appendChild(img);
            if (e.data.transactionId) _sendReceipt(e.data.transactionId, 'success');
        }
        if (e.data.type === 'inspect-update-dom') {
             if (e.origin !== window.location.origin) return;
             try {
                 takeSnapshot();
                 const target = document.querySelector(e.data.selector);
                 if (target) {
                     const parser = new DOMParser();
                     const doc = parser.parseFromString(e.data.html, 'text/html');
                     const newEl = doc.body.firstChild;
                     if (newEl) {
                         target.replaceWith(newEl);
                         // M200A: injecter data-af-id sur le nouvel élément
                         if (newEl.nodeType === Node.ELEMENT_NODE && !newEl.dataset.afId) {
                             newEl.setAttribute('data-af-id', _hashElement(newEl));
                         }
                         if (e.data.transactionId) _sendReceipt(e.data.transactionId, 'success');
                     } else {
                         if (e.data.transactionId) _sendReceipt(e.data.transactionId, 'error', 'empty_html');
                     }
                 } else {
                     if (e.data.transactionId) _sendReceipt(e.data.transactionId, 'error', 'element_not_found: ' + e.data.selector);
                 }
             } catch (err) {
                 if (e.data.transactionId) _sendReceipt(e.data.transactionId, 'error', 'dom_update_failed: ' + err.message);
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
                if (e.data.transactionId) _sendReceipt(e.data.transactionId, 'success');
            } else {
                if (e.data.transactionId) _sendReceipt(e.data.transactionId, 'error', 'no_element_selected');
            }
        }
        if (e.data.type === 'highlight-intent') {
            const { id, selector, text, tag } = e.data;
            let el = id ? document.getElementById(id) : null;
            if (!el && selector) el = document.querySelector(selector);
            // M200A: aussi chercher par data-af-id
            if (!el && selector && selector.includes('data-af-id')) el = document.querySelector(selector);
            if (!el && text && tag) {
                const candidates = Array.from(document.getElementsByTagName(tag));
                el = candidates.find(c => c.textContent.includes(text));
            }
            if (el) {
                document.querySelectorAll('.intent-highlight').forEach(o => o.classList.remove('intent-highlight'));
                el.classList.add('intent-highlight');
                el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                if (e.data.transactionId) _sendReceipt(e.data.transactionId, 'success');
            } else {
                if (e.data.transactionId) _sendReceipt(e.data.transactionId, 'error', 'element_not_found');
            }
        }
        if (e.data.type === 'clear-highlights') {
            document.querySelectorAll('.intent-highlight').forEach(o => o.classList.remove('intent-highlight'));
            if (e.data.transactionId) _sendReceipt(e.data.transactionId, 'success');
        }
        if (e.data.type === 'ws-clear-nudges') {
            document.querySelectorAll('.ws-nudge').forEach(n => n.remove());
            if (e.data.transactionId) _sendReceipt(e.data.transactionId, 'success');
        }

        // M200B: Generic command handler — toute commande avec transactionId reçoit un receipt
        if (e.data.type === 'AF_CMD') {
            const txId = e.data.transactionId || e.data.id;
            try {
                const action = e.data.action;
                const selector = e.data.selector;
                const value = e.data.value;

                let el = null;
                if (selector) {
                    el = document.querySelector(selector);
                    // M200A: fallback par data-af-id
                    if (!el && selector.includes('data-af-id')) el = document.querySelector(selector);
                }

                if (!el) {
                    _sendReceipt(txId, 'error', 'element_not_found: ' + (selector || 'N/A'));
                    return;
                }

                // Visibility check
                const visibility = _isElementVisible(el);
                if (visibility && !visibility.visible) {
                    _sendReceipt(txId, 'error', 'element_not_visible', { overlapped_by: visibility.overlapped_by });
                    return;
                }

                // Execute action
                switch (action) {
                    case 'apply-color':
                        el.style.backgroundColor = value;
                        break;
                    case 'apply-class':
                        value.split(' ').forEach(c => {
                            if (c.startsWith('-')) el.classList.remove(c.slice(1));
                            else el.classList.add(c);
                        });
                        break;
                    case 'set-text':
                        el.textContent = value;
                        break;
                    default:
                        _sendReceipt(txId, 'error', 'unknown_action: ' + action);
                        return;
                }

                _sendReceipt(txId, 'success', { action, selector });
            } catch (err) {
                _sendReceipt(e.data.transactionId || e.data.id, 'error', 'command_failed: ' + err.message);
            }
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

            // M200B: Visibility Report sur hover
            const visibility = _isElementVisible(organ);
            const afId = organ.dataset.afId || organ.id || null;
            window.parent.postMessage({
                type: 'AF_VISIBILITY',
                data_af_id: afId,
                selector: getSelector(organ),
                clickable: visibility === true || visibility.visible,
                overlapped_by: (visibility && visibility.overlapped_by) || null,
                z_index: +getComputedStyle(organ).zIndex || 0,
                opacity: +getComputedStyle(organ).opacity,
                in_viewport: true // simplifié
            }, '*');
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
        if (el.dataset && el.dataset.afId) return '[data-af-id="' + el.dataset.afId + '"]';
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
