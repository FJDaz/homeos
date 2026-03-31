// static/js/frd/frd_main.js
import { FrdEditor } from './FrdEditor.feature.js';
import { FrdChat } from './FrdChat.feature.js';
import { FrdKimi } from './FrdKimi.feature.js';
import { FrdWire } from './FrdWire.feature.js';
import { FrdAssets } from './FrdAssets.feature.js';
import { FrdPreview } from './FrdPreview.feature.js';

class FrdMain {
    constructor() {
        this.state = {
            editorHTML: null,
            isCollapsed: false,
            lastHeight: 280,
            inspectActive: false,
            _lockActive: false,
            _lockDecorations: [],
            uploadedAssets: [],
            _chatMode: 'construct',
            _chatHistory: [],
            _htmlHistory: [],
            _zipMode: false,
            _kimiInProgress: false,
            _lastKimiHtml: null,
            _inspectDecorations: [],
            _inspectDecTimer: null,
            _inspectHoverTimer: null
        };

        this.editor = new FrdEditor(this);
        this.chat = new FrdChat(this);
        this.kimi = new FrdKimi(this);
        this.wire = new FrdWire(this);
        this.assets = new FrdAssets(this);
        this.preview = new FrdPreview(this);
    }

    async init() {
        await this.editor.init();
        await this.assets.load();
        await this.editor.loadList();
        this.chat.setMode('construct');
        this.setupEventListeners();

        // Mission 115: Auto-load current file if set
        try {
            const res = await fetch('/api/frd/current');
            const data = await res.json();
            if (data.name) {
                console.log('[FrdMain] Auto-loading current file:', data.name);
                await this.editor.loadFile(data.name);
                const sel = document.getElementById('template-select');
                if (sel) sel.value = data.name;
            }
        } catch (e) {
            console.warn('[FrdMain] Current file fetch failed', e);
        }

        console.log('[FrdMain] Initialized V3 modular');
    }

    setupEventListeners() {
        // UI Layout
        const monacoPane = document.getElementById('monaco-pane');
        const monacoResizeHandle = document.getElementById('monaco-resize-handle');
        
        document.getElementById('btn-toggle-monaco').onclick = (e) => {
            this.state.isCollapsed = !this.state.isCollapsed;
            monacoPane.style.transition = 'height 200ms ease';
            const btn = document.getElementById('btn-toggle-monaco');
            if (this.state.isCollapsed) {
                this.state.lastHeight = monacoPane.offsetHeight;
                monacoPane.style.height = '0px';
                btn.innerText = '▴';
            } else {
                monacoPane.style.height = this.state.lastHeight + 'px';
                btn.innerText = '▾';
            }
            setTimeout(() => { if (this.editor.editor) this.editor.editor.layout(); }, 210);
        };

        // Resizing
        let isResizingMonaco = false;
        monacoResizeHandle.onmousedown = () => {
            isResizingMonaco = true;
            monacoPane.style.transition = 'none';
            document.body.style.cursor = 'row-resize';
        };

        window.onmousemove = (e) => {
            if (!isResizingMonaco) return;
            const mainCol = document.getElementById('main-col');
            const mainColTop = mainCol.getBoundingClientRect().top;
            let newHeight = mainCol.offsetHeight - (e.clientY - mainColTop);
            newHeight = Math.max(100, Math.min(newHeight, mainCol.offsetHeight - 100));
            monacoPane.style.height = newHeight + 'px';
            if (this.editor.editor) this.editor.editor.layout();
        };

        window.onmouseup = () => {
            if (isResizingMonaco) {
                isResizingMonaco = false;
                document.body.style.cursor = 'default';
            }
        };

        // File Operations
        document.getElementById('btn-open').onclick = () => document.getElementById('file-input').click();
        document.getElementById('file-input').onchange = (e) => {
            const file = e.target.files[0];
            if (!file) return;
            if (file.name.endsWith('.html')) this.editor.loadHTMLFile(file);
            else if (file.name.endsWith('.zip')) this.editor.loadZIPFile(file);
        };

        document.getElementById('template-select').onchange = () => {
            const filename = document.getElementById('template-select').value;
            if (!filename) return;
            document.getElementById('save-name').value = filename;
            this.editor.loadFile(filename);
        };

        document.getElementById('btn-save').onclick = () => this.editor.saveFile();
        document.getElementById('btn-preview-tab').onclick = () => this.editor.runPreviewTab();

        document.getElementById('btn-undo').onclick = () => {
            if (this.state._htmlHistory.length === 0) return;
            this.editor.setValue(this.state._htmlHistory.pop());
            this.preview.update();
            if (this.state._htmlHistory.length === 0) document.getElementById('btn-undo').classList.add('hidden');
        };

        document.getElementById('btn-exit-zip').onclick = () => {
            this.state._zipMode = false;
            const previewIframe = document.getElementById('preview-iframe');
            previewIframe.removeAttribute('src');
            document.getElementById('btn-exit-zip').classList.add('hidden');
            this.preview.update();
        };

        // Inspection/Lock Toggles
        document.getElementById('btn-inspect').onclick = () => {
            this.state.inspectActive = !this.state.inspectActive;
            if (this.state.inspectActive && this.state._lockActive) {
                this.state._lockActive = false;
                const lBtn = document.getElementById('btn-lock');
                lBtn.classList.remove('border-orange-400', 'text-orange-500', 'bg-orange-50');
                lBtn.innerText = 'Lock';
            }
            const btn = document.getElementById('btn-inspect');
            if (this.state.inspectActive) {
                btn.classList.add('bg-figma-tabActive', 'text-white', 'font-bold');
                btn.innerText = 'Inspect [ON]';
            } else {
                btn.classList.remove('bg-figma-tabActive', 'text-white', 'font-bold');
                btn.innerText = 'Inspect';
            }
            this.preview.update();
        };

        document.getElementById('btn-lock').onclick = () => {
            this.state._lockActive = !this.state._lockActive;
            if (this.state._lockActive && this.state.inspectActive) {
                this.state.inspectActive = false;
                const iBtn = document.getElementById('btn-inspect');
                iBtn.classList.remove('bg-figma-tabActive', 'text-white', 'font-bold');
                iBtn.innerText = 'Inspect';
            }
            const btn = document.getElementById('btn-lock');
            if (this.state._lockActive) {
                btn.classList.add('border-orange-400', 'text-orange-500', 'bg-orange-50', 'font-bold');
                btn.innerText = 'Lock [ON]';
            } else {
                btn.classList.remove('border-orange-400', 'text-orange-500', 'bg-orange-50', 'font-bold');
                btn.innerText = 'Lock';
                document.getElementById('lock-breadcrumb').classList.add('hidden');
            }
            this.preview.update();
            this.editor.refreshLockDecorations();
        };

        document.getElementById('btn-clear-locks').onclick = () => {
            const cleaned = this.editor.getValue().replace(/\s*data-frd-lock="true"/g, '');
            this.editor.setValue(cleaned);
            this.preview.update();
            this.editor.updateClearLocksButton();
            this.editor.refreshLockDecorations();
        };

        // Chat
        document.getElementById('btn-send').onclick = () => this.chat.send();
        document.getElementById('chat-input').onkeydown = (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.chat.send();
            }
        };

        // Preview Events
        document.getElementById('preview-iframe').addEventListener('load', () => this.preview.injectScripts());

        window.addEventListener('message', e => {
            if (e.data.type === 'inspect-hover' && this.state.inspectActive) {
                clearTimeout(this.state._inspectHoverTimer);
                this.state._inspectHoverTimer = setTimeout(() => this.preview.highlightInMonaco(e.data, false), 80);
            }
            if (e.data.type === 'inspect-click' && this.state.inspectActive) {
                this.preview.highlightInMonaco(e.data, true);
            }
            if (e.data.type === 'lock-click' && this.state._lockActive) {
                this.editor.toggleLock(e.data);
            }
            if (e.data.type === 'lock-hover' && this.state._lockActive) {
                const bc = document.getElementById('lock-breadcrumb');
                bc.textContent = e.data.path;
                bc.classList.toggle('hidden', !e.data.path);
            }
        });

        // Drag & Drop Assets
        const dropZone = document.getElementById('drop-zone');
        if (dropZone) {
            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropZone.style.borderColor = '#8cc63f';
                dropZone.style.background = '#f0fae0';
            });
            dropZone.addEventListener('dragleave', () => {
                dropZone.style.borderColor = '#333';
                dropZone.style.background = '';
            });
            dropZone.addEventListener('drop', async (e) => {
                e.preventDefault();
                dropZone.style.borderColor = '#333';
                dropZone.style.background = '';
                this.assets.handleUpload(e.dataTransfer.files);
            });
        }

        // Global Drag & Drop Files
        const dropOverlay = document.getElementById('drop-overlay');
        let _dragCount = 0;
        window.addEventListener('dragenter', (e) => {
            if (e.dataTransfer && e.dataTransfer.types.includes('Files')) {
                _dragCount++;
                if (dropOverlay) dropOverlay.classList.add('active');
            }
        });
        window.addEventListener('dragleave', (e) => {
            _dragCount--;
            if (_dragCount <= 0) { 
                _dragCount = 0; 
                if (dropOverlay) dropOverlay.classList.remove('active'); 
            }
        });
        window.addEventListener('dragover', (e) => { e.preventDefault(); });
        window.addEventListener('drop', (e) => {
            e.preventDefault();
            _dragCount = 0;
            if (dropOverlay) dropOverlay.classList.remove('active');
            const file = e.dataTransfer.files && e.dataTransfer.files[0];
            if (file) {
                if (file.name.endsWith('.html')) this.editor.loadHTMLFile(file);
                else if (file.name.endsWith('.zip')) this.editor.loadZIPFile(file);
            }
        });
    }
}

window.frdApp = new FrdMain();
document.addEventListener('DOMContentLoaded', () => window.frdApp.init());

// Global entry point for HTML onclick calls
window.setMode = (mode) => window.frdApp.chat.setMode(mode);
window.runWire = () => window.frdApp.wire.run();
