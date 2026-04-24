/**
 * SubjectEditor — M322: Subject & Referential Manager
 * Interface pour créer/éditer des sujets pédagogiques et leurs référentiels.
 */
(function() {
    'use strict';

    let panel = null;
    let currentSubject = {
        id: null,
        name: '',
        description: '',
        referential: [],
        criteria: []
    };

    const els = {};

    function buildUI() {
        if (panel) return;

        panel = document.createElement('div');
        panel.id = 'subject-editor-overlay';
        panel.className = 'fixed inset-0 z-[2100] flex items-center justify-center bg-slate-900/40 backdrop-blur-sm hidden animate-in fade-in duration-300';
        
        panel.innerHTML = `
            <div class="w-[800px] h-[90vh] bg-white rounded-3xl shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-300">
                <!-- Header -->
                <div class="h-16 px-8 border-b border-slate-100 flex items-center justify-between bg-white shrink-0">
                    <div class="flex items-center gap-3">
                        <div class="w-2.5 h-2.5 rounded-full bg-homeos-green shadow-[0_0_12px_rgba(163,205,84,0.6)]"></div>
                        <span class="text-[14px] font-black uppercase tracking-[0.2em] text-slate-800">Éditeur de Sujet</span>
                    </div>
                    <button id="sj-edit-close" class="p-2 text-slate-300 hover:text-red-500 transition-colors">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                    </button>
                </div>

                <!-- Content -->
                <div class="flex-1 overflow-y-auto p-10 space-y-8 scrollbar-hide">
                    <!-- General Info -->
                    <section class="space-y-4">
                        <div class="text-[10px] font-black uppercase tracking-widest text-[#A3CD54]">Informations Générales</div>
                        <div class="space-y-2">
                            <input type="text" id="sj-input-name" placeholder="Titre du sujet (ex: Landing Page E-commerce)" 
                                   class="w-full text-2xl font-bold text-slate-800 border-none focus:ring-0 placeholder:text-slate-200">
                            <textarea id="sj-input-desc" placeholder="Description courte des objectifs pédagogiques..." 
                                     class="w-full text-[14px] text-slate-500 border-none focus:ring-0 resize-none min-h-[80px] placeholder:text-slate-200"></textarea>
                        </div>
                    </section>

                    <hr class="border-slate-50">

                    <!-- Referential -->
                    <section class="space-y-6">
                        <div class="flex items-center justify-between">
                            <div class="text-[10px] font-black uppercase tracking-widest text-[#A3CD54]">Référentiel de Compétences</div>
                            <button id="sj-btn-add-ref" class="px-3 py-1 bg-slate-50 text-slate-400 text-[10px] font-bold uppercase tracking-widest rounded-full hover:bg-slate-100 transition-all flex items-center gap-2">
                                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M12 5v14M5 12h14"/></svg>
                                Ajouter une compétence
                            </button>
                        </div>
                        
                        <div id="sj-ref-container" class="space-y-3">
                            <!-- List of competencies injected here -->
                        </div>
                    </section>
                </div>

                <!-- Footer -->
                <div class="h-20 px-8 border-t border-slate-100 flex items-center justify-between bg-slate-50/30 shrink-0">
                    <button id="sj-btn-delete" class="text-[11px] font-bold uppercase tracking-widest text-slate-300 hover:text-red-500 transition-all">Supprimer le sujet</button>
                    <div class="flex items-center gap-4">
                        <button id="sj-btn-cancel" class="px-6 py-2.5 text-[12px] font-bold uppercase tracking-widest text-slate-400 hover:text-slate-600 transition-all">Annuler</button>
                        <button id="sj-btn-save" class="px-8 py-2.5 bg-homeos-green text-white text-[12px] font-bold uppercase tracking-widest shadow-lg shadow-homeos-green/20 rounded-xl hover:scale-105 active:scale-95 transition-all">Enregistrer</button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(panel);

        // Refs
        els.name = panel.querySelector('#sj-input-name');
        els.desc = panel.querySelector('#sj-input-desc');
        els.refContainer = panel.querySelector('#sj-ref-container');
        els.btnSave = panel.querySelector('#sj-btn-save');
        els.btnCancel = panel.querySelector('#sj-btn-cancel');
        els.btnClose = panel.querySelector('#sj-edit-close');
        els.btnAddRef = panel.querySelector('#sj-btn-add-ref');
        els.btnDelete = panel.querySelector('#sj-btn-delete');

        // Events
        els.btnClose.onclick = hide;
        els.btnCancel.onclick = hide;
        els.btnSave.onclick = save;
        els.btnAddRef.onclick = () => addRefRow();
        els.btnDelete.onclick = deleteSj;
    }

    async function open(subjectId = null) {
        buildUI();
        panel.classList.remove('hidden');
        
        if (subjectId) {
            try {
                const res = await fetch(`/api/subjects/${subjectId}`);
                if (res.ok) {
                    currentSubject = await res.json();
                }
            } catch(e) {
                console.error('[SubjectEditor] Load error:', e);
            }
        } else {
            currentSubject = { id: null, name: '', description: '', referential: [], criteria: [] };
        }

        render();
    }

    function hide() {
        if (panel) panel.classList.add('hidden');
    }

    function render() {
        els.name.value = currentSubject.name || '';
        els.desc.value = currentSubject.description || '';
        els.refContainer.innerHTML = '';
        
        if (currentSubject.referential.length === 0) {
            addRefRow();
        } else {
            currentSubject.referential.forEach(ref => addRefRow(ref));
        }

        els.btnDelete.style.display = currentSubject.id ? 'block' : 'none';
    }

    function addRefRow(ref = { id: Date.now(), label: '', criteria: '' }) {
        const row = document.createElement('div');
        row.className = 'flex gap-4 items-start group animate-in slide-in-from-left-2 duration-200';
        row.innerHTML = `
            <div class="flex-1 space-y-2">
                <input type="text" class="sj-ref-label w-full px-4 py-2.5 bg-slate-50 border border-slate-100 rounded-xl text-[14px] font-bold text-slate-700 focus:bg-white focus:border-homeos-green transition-all outline-none" 
                       placeholder="Nom de la compétence (ex: Architecture Frontend)" value="${ref.label}">
                <textarea class="sj-ref-criteria w-full px-4 py-2 bg-slate-50 border border-slate-100 rounded-xl text-[12px] text-slate-500 focus:bg-white focus:border-homeos-green transition-all outline-none resize-none h-[60px]" 
                       placeholder="Critères d'évaluation détaillés pour Sullivan...">${ref.criteria}</textarea>
            </div>
            <button class="sj-ref-del p-2 mt-1 text-slate-200 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
            </button>
        `;
        
        row.querySelector('.sj-ref-del').onclick = () => row.remove();
        els.refContainer.appendChild(row);
    }

    async function save() {
        const refs = [];
        els.refContainer.querySelectorAll('.flex.gap-4').forEach(row => {
            const label = row.querySelector('.sj-ref-label').value.trim();
            const criteria = row.querySelector('.sj-ref-criteria').value.trim();
            if (label) {
                refs.push({ id: `ref_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`, label, criteria });
            }
        });

        const payload = {
            id: currentSubject.id,
            name: els.name.value.trim(),
            description: els.desc.value.trim(),
            referential: refs,
            criteria: [] // Phase 2: criteria auto-generation
        };

        if (!payload.name) return alert('Le titre est requis');

        els.btnSave.disabled = true;
        els.btnSave.innerText = 'Enregistrement...';

        try {
            const res = await fetch('/api/subjects', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            if (res.ok) {
                hide();
                if (window.WsProjectPanel) window.WsProjectPanel.refresh();
            }
        } catch(e) {
            console.error('[SubjectEditor] Save failed:', e);
        } finally {
            els.btnSave.disabled = false;
            els.btnSave.innerText = 'Enregistrer';
        }
    }

    async function deleteSj() {
        if (!currentSubject.id) return;
        if (!confirm('Supprimer ce sujet ? Cette action est irréversible.')) return;

        try {
            await fetch(`/api/subjects/${currentSubject.id}`, { method: 'DELETE' });
            hide();
            if (window.WsProjectPanel) window.WsProjectPanel.refresh();
        } catch(e) {
            console.error('[SubjectEditor] Delete failed', e);
        }
    }

    window.SubjectEditor = { open, hide };

})();
