// static/js/frd/FrdEditor.feature.js

export class FrdEditor {
    constructor(main) {
        this.main = main;
        this.editor = null;
    }

    async init() {
        return new Promise((resolve) => {
            require.config({ paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs' } });
            require(['vs/editor/editor.main'], () => {
                this.editor = monaco.editor.create(document.getElementById('editor-container'), {
                    value: '<!-- Chargez un fichier pour commencer -->',
                    language: 'html',
                    theme: 'vs-light',
                    automaticLayout: true,
                    minimap: { enabled: false },
                    fontSize: 12,
                    fontFamily: 'Geist Mono, monospace',
                    scrollBeyondLastLine: false,
                    lineNumbers: 'on',
                    wordWrap: 'on'
                });

                this.editor.onDidChangeModelContent(() => {
                    this.main.preview.update();
                });

                // --- Highlight Logic ---
                this.editor.onDidChangeCursorSelection((e) => {
                    const selection = this.editor.getModel().getValueInRange(e.selection);
                    const match = selection.match(/id="([^"]+)"/);
                    if (match) {
                        const id = match[1];
                        const iframe = document.getElementById('preview-iframe');
                        iframe.contentWindow.postMessage({ type: 'highlight', selector: '#' + id }, '*');
                    }
                });

                // Monaco Action: Ctrl+L (Lock Selection)
                this.editor.addAction({
                    id: 'frd-lock-selection',
                    label: '🔒 Locker cet élément',
                    keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyL],
                    contextMenuGroupId: 'frd',
                    contextMenuOrder: 1,
                    run: (ed) => {
                        const selection = ed.getSelection();
                        const selectedText = ed.getModel().getValueInRange(selection);
                        const tagMatch = selectedText.match(/<(\w+)([^>]*)>/);
                        if (!tagMatch) return;
                        const [fullTag, tagName, attrs] = tagMatch;
                        if (attrs.includes('data-frd-lock')) return;
                        const newTag = `<${tagName}${attrs} data-frd-lock="true">`;
                        const newContent = ed.getValue().replace(fullTag, newTag);
                        ed.setValue(newContent);
                        this.refreshLockDecorations();
                        this.main.preview.update();
                    }
                });

                this.main.state.editorHTML = this.editor;
                resolve();
            });
        });
    }

    getValue() { return this.editor ? this.editor.getValue() : ''; }
    setValue(val) { if (this.editor) this.editor.setValue(val); }

    refreshLockDecorations() {
        if (!this.editor) return;
        const lines = this.editor.getValue().split('\n');
        const ranges = [];
        lines.forEach((line, i) => {
            if (line.includes('data-frd-lock="true"')) {
                ranges.push({
                    range: new monaco.Range(i + 1, 1, i + 1, line.length + 1),
                    options: {
                        isWholeLine: true,
                        className: 'monaco-lock-highlight',
                        glyphMarginClassName: 'monaco-lock-glyph'
                    }
                });
            }
        });
        this.main.state._lockDecorations = this.editor.deltaDecorations(this.main.state._lockDecorations, ranges);
    }

    updateClearLocksButton() {
        const hasLocks = this.getValue().includes('data-frd-lock="true"');
        document.getElementById('btn-clear-locks').classList.toggle('hidden', !hasLocks);
    }

    toggleLock({ tag, id, cls }) {
        const content = this.getValue();
        const lines = content.split('\n');

        let pattern = null;
        if (id) {
            pattern = new RegExp(`(<${tag}[^>]*id=["']${id}["'][^>]*)(>)`, 'i');
        } else if (cls) {
            const firstCls = cls.trim().split(/\s+/)[0];
            if (firstCls) pattern = new RegExp(`(<${tag}[^>]*class=["'][^"']*${firstCls.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}[^"']*["'][^>]*)(>)`, 'i');
        }
        if (!pattern) pattern = new RegExp(`(<${tag})(\\s|>)`, 'i');

        let found = false;
        const newLines = lines.map(line => {
            if (found) return line;
            const m = line.match(pattern);
            if (!m) return line;
            found = true;
            if (line.includes('data-frd-lock')) {
                return line.replace(/\s*data-frd-lock="true"/, '');
            } else {
                let newLine = line;
                if (!id && !line.match(/\sid=["'][^"']+["']/i)) {
                    const autoId = `lock-${tag}-${Date.now().toString(36)}`;
                    newLine = newLine.replace(pattern, `$1 id="${autoId}"$2`);
                }
                return newLine.replace(pattern, `$1 data-frd-lock="true"$2`);
            }
        });

        if (found) {
            this.setValue(newLines.join('\n'));
            this.updateClearLocksButton();
            this.refreshLockDecorations();
        }
    }

    async loadList() {
        try {
            const res = await fetch('/api/frd/files');
            if (!res.ok) return;
            const data = await res.json();
            const sel = document.getElementById('template-select');
            sel.innerHTML = '';
            data.files.forEach(f => {
                const opt = document.createElement('option');
                opt.value = f;
                opt.textContent = f.replace('.html', '').replace(/_/g, ' ');
                sel.appendChild(opt);
            });
        } catch (e) { console.warn('Template list unavailable', e); }
    }

    async loadFile(filename) {
        try {
            const res = await fetch(`/api/frd/file?name=${filename}`);
            if (res.ok) {
                const data = await res.json();
                this.setValue(data.content);
                document.getElementById('save-name').value = filename;
                this.main.state._chatHistory = [];
                this.main.state._htmlHistory = [];
                document.getElementById('btn-undo').classList.add('hidden');
                this.refreshLockDecorations();
                this.updateClearLocksButton();
                this.main.chat.triggerSilentAudit();
            }
        } catch (e) { console.error("Load failed", e); }
    }

    async saveFile() {
        const saveInput = document.getElementById('save-name').value.trim();
        const name = saveInput || document.getElementById('template-select').value;
        const content = this.getValue();
        try {
            const res = await fetch('/api/frd/file', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, content })
            });
            if (res.ok) {
                alert("Fichier sauvegardé avec succès !");
                const sel = document.getElementById('template-select');
                if (!sel.querySelector(`option[value="${name}"]`)) {
                    const opt = document.createElement('option');
                    opt.value = name; opt.textContent = name;
                    sel.appendChild(opt);
                }
                sel.value = name;
                this.main.chat.triggerSilentAudit();
            } else {
                const data = await res.json();
                if (res.status === 422) {
                    const msg = "CONTRAT DOM — IDs manquants :\n" + data.violations.join('\n') + "\n\nSauvegarder quand même ?";
                    if (confirm(msg)) {
                        const r2 = await fetch('/api/frd/file', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ name, content, force: true })
                        });
                        if (r2.ok) { alert("Sauvegardé (contrat ignoré)."); this.main.chat.triggerSilentAudit(); }
                        else alert("Erreur : " + r2.statusText);
                    }
                } else {
                    alert("Erreur lors de la sauvegarde : " + (data.error || res.statusText));
                }
            }
        } catch (e) { console.error("Save failed", e); }
    }

    loadHTMLFile(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const content = e.target.result;
            this.setValue(content);
            this.refreshLockDecorations();
            this.updateClearLocksButton();
            const templateSelect = document.getElementById('template-select');
            let opt = templateSelect.querySelector(`option[value="${file.name}"]`);
            if (!opt) {
                opt = document.createElement('option');
                opt.value = file.name;
                opt.textContent = file.name;
                templateSelect.appendChild(opt);
            }
            templateSelect.value = file.name;
            templateSelect.classList.remove('hidden');
            const currentFileSpan = document.getElementById('current-file');
            currentFileSpan.innerText = file.name;
            currentFileSpan.classList.remove('hidden');
            this.main.chat.appendBubble(`Fichier local "${file.name}" chargé. Save → sauvegarde sous ce nom.`, 'sullivan');
            this.main.chat.triggerSilentAudit();
        };
        reader.readAsText(file);
    }

    async loadZIPFile(file) {
        this.main.chat.appendBubble(`📤 Décompression de "${file.name}"...`, 'sullivan');
        const fd = new FormData();
        fd.append('file', file);
        try {
            const res = await fetch('/api/frd/unzip-preview', { method: 'POST', body: fd });
            if (res.ok) {
                const data = await res.json();
                this.main.state._zipMode = true;
                const previewIframe = document.getElementById('preview-iframe');
                previewIframe.removeAttribute('srcdoc');
                previewIframe.src = data.url;
                document.getElementById('btn-exit-zip').classList.remove('hidden');
                const templateSelect = document.getElementById('template-select');
                templateSelect.classList.add('hidden');
                const currentFileSpan = document.getElementById('current-file');
                currentFileSpan.innerText = file.name;
                currentFileSpan.classList.remove('hidden');
                this.main.chat.appendBubble("✨ Aperçu React chargé. Pour reconstruire en HTML/Tailwind, utilise Sullivan en mode CONSTRUCT.", 'sullivan');
                document.getElementById('chat-input').value = "/construct Recrée ce layout React en HTML5 propre avec Tailwind CSS.";
            } else {
                const err = await res.json();
                alert("Erreur d'extraction : " + (err.error || res.statusText));
            }
        } catch (e) {
            console.error("ZIP Load failed", e);
            alert("Erreur de connexion au serveur pour l'extraction ZIP.");
        }
    }
}
