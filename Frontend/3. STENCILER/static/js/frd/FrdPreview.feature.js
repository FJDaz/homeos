// static/js/frd/FrdPreview.feature.js

export class FrdPreview {
    constructor(main) {
        this.main = main;
    }

    update() {
        if (this.main.state._zipMode) return;
        const iframe = document.getElementById('preview-iframe');
        let content = this.main.editor.getValue();
        const marker = '<!-- __FRD:' + this.main.state.inspectActive + ':' + this.main.state._lockActive + ' -->';
        content = content.includes('</body>')
            ? content.replace('</body>', marker + '</body>')
            : content + marker;
        iframe.srcdoc = content;
    }

    injectScripts() {
        const iframe = document.getElementById('preview-iframe');
        try {
            const doc = iframe.contentDocument;
            if (!doc || !doc.body) return;
            
            const s1 = doc.createElement('script');
            s1.textContent = [
                "window.addEventListener('message', function(e) {",
                "    if (e.data.type !== 'highlight') return;",
                "    var el = document.querySelector(e.data.selector);",
                "    if (!el) return;",
                "    document.querySelectorAll('[data-hl]').forEach(function(h){ h.style.outline=''; h.removeAttribute('data-hl'); });",
                "    el.style.outline = '4px solid #8cc63f';",
                "    el.setAttribute('data-hl', '1');",
                "    el.scrollIntoView({ behavior: 'smooth', block: 'center' });",
                "    setTimeout(function(){ el.style.outline = '2px solid #8cc63f'; }, 200);",
                "});"
            ].join('\n');
            doc.body.appendChild(s1);

            if (this.main.state.inspectActive) {
                const s2 = doc.createElement('script');
                s2.textContent = [
                    "var __li = null;",
                    "document.addEventListener('mouseover', function(e) {",
                    "    var el = e.target;",
                    "    if (el === document.documentElement || el === document.body) return;",
                    "    if (el === __li) return;",
                    "    if (__li) __li.style.outline = '';",
                    "    __li = el;",
                    "    el.style.outline = '2px solid #8cc63f';",
                    "    window.parent.postMessage({ type: 'inspect-hover', id: el.id||null, tag: el.tagName.toLowerCase(), cls: el.getAttribute('class')||'' }, '*');",
                    "});",
                    "document.addEventListener('mouseleave', function() { if (__li) { __li.style.outline=''; __li=null; } });",
                    "document.addEventListener('click', function(e) {",
                    "    e.preventDefault(); e.stopPropagation();",
                    "    var el = e.target;",
                    "    window.parent.postMessage({ type: 'inspect-click', id: el.id||null, tag: el.tagName.toLowerCase(), cls: el.getAttribute('class')||'' }, '*');",
                    "}, true);"
                ].join('\n');
                doc.body.appendChild(s2);
            }

            if (this.main.state._lockActive) {
                const sLock = doc.createElement('script');
                sLock.textContent = [
                    "var __lh = null;",
                    "document.addEventListener('mouseover', function(e) {",
                    "    var el = e.target;",
                    "    if (el === document.documentElement || el === document.body) return;",
                    "    if (el === __lh) return;",
                    "    if (__lh) { __lh.style.outline = ''; }",
                    "    __lh = el;",
                    "    if (!el.hasAttribute('data-frd-lock')) el.style.outline = '2px dashed #f97316';",
                    "    var path = [];",
                    "    var cur = el;",
                    "    while (cur && cur !== document.body) { ",
                    "        path.unshift((cur.tagName.toLowerCase()) + (cur.id ? '#'+cur.id : cur.className ? '.'+cur.className.trim().split(' ')[0] : '')); ",
                    "        cur = cur.parentElement; ",
                    "    }",
                    "    window.parent.postMessage({ type: 'lock-hover', path: path.join(' › ') }, '*');",
                    "});",
                    "document.addEventListener('mouseleave', function() { ",
                    "    if (__lh) { __lh.style.outline=''; __lh=null; } ",
                    "    window.parent.postMessage({ type: 'lock-hover', path: '' }, '*');",
                    "});",
                    "document.addEventListener('click', function(e) {",
                    "    e.preventDefault(); e.stopPropagation();",
                    "    var el = e.target;",
                    "    window.parent.postMessage({ type: 'lock-click', id: el.id||null, tag: el.tagName.toLowerCase(), cls: el.getAttribute('class')||'' }, '*');",
                    "}, true);",
                    "document.querySelectorAll('[data-frd-lock]').forEach(function(el){ el.style.backgroundColor = 'rgba(249, 115, 22, 0.5)'; el.style.outline = '2px solid #f97316'; });"
                ].join('\n');
                doc.body.appendChild(sLock);
            }
        } catch (e) { console.warn('[FRD] inject scripts failed:', e); }
    }

    highlightInMonaco({ id, tag, cls }, select) {
        const content = this.main.editor.getValue();
        const lines = content.split('\n');
        const searchId = id ? `id="${id}"` : null;
        const searchCls = cls ? cls.trim().split(' ')[0] : null;
        let lineIdx = -1;

        if (searchId) {
            for (let i = 0; i < lines.length; i++) {
                if (lines[i].includes(searchId)) { lineIdx = i; break; }
            }
        }
        if (lineIdx === -1 && searchCls) {
            for (let i = 0; i < lines.length; i++) {
                if (lines[i].includes('<' + tag) && lines[i].includes(searchCls)) { lineIdx = i; break; }
            }
        }
        if (lineIdx === -1) {
            for (let i = 0; i < lines.length; i++) {
                if (lines[i].includes('<' + tag)) { lineIdx = i; break; }
            }
        }

        if (lineIdx === -1) return;
        const lineNum = lineIdx + 1;
        this.main.editor.editor.revealLineInCenter(lineNum);

        if (select) {
            this.main.editor.editor.setSelection(new monaco.Selection(lineNum, 1, lineNum, lines[lineIdx].length + 1));
        } else {
            clearTimeout(this.main.state._inspectDecTimer);
            this.main.state._inspectDecorations = this.main.editor.editor.deltaDecorations(this.main.state._inspectDecorations, [{
                range: new monaco.Range(lineNum, 1, lineNum, 1),
                options: { isWholeLine: true, className: 'monaco-inspect-highlight' }
            }]);
            this.main.state._inspectDecTimer = setTimeout(() => {
                this.main.state._inspectDecorations = this.main.editor.editor.deltaDecorations(this.main.state._inspectDecorations, []);
            }, 1500);
        }
    }
}
