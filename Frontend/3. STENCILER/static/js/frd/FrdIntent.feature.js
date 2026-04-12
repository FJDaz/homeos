/**
 * FrdIntent.feature.js — Mission 117
 * Intégration du Registre des Intentions (Analyse SVG) dans l'Editeur FRD.
 * Gère le Protocole Spécial SVG AI pour les exports Illustrator.
 */

const FrdIntent = {
    importId: null,
    analysis: null,
    svgContent: null,
    stylesMap: {}, // Mapping .stX -> style rules

    async init(id) {
        if (!id) return;
        this.importId = id;
        console.log("🎨 FrdIntent: initializing analysis for", id);
        
        try {
            // 1. Récupérer l'analyse backend (Claude)
            const res = await fetch(`/api/retro-genome/import-analysis?id=${id}`);
            const data = await res.json();
            this.analysis = data.analysis;

            // 2. Récupérer le contenu SVG brut pour le décodage Illustrator
            await this.fetchRawSvg();

            // 3. Appliquer le Protocole SVG AI Rule #1 (Styles)
            this.decodeIllustratorStyles();

            // 4. Afficher le panneau
            this.showPanel();
            this.renderTable();

            // 5. Sullivan Action (Livrable D)
            if (window.frdApp && window.frdApp.chat) {
                window.frdApp.chat.appendBubble("j'ai analysé votre import illustrator. le registre des intentions est prêt à gauche. voulez-vous que je génère le code tailwind ?", 'sullivan');
            }

            // 6. Wiring bouton génération
            const genBtn = document.getElementById('btn-generate-tailwind');
            if (genBtn) {
                genBtn.onclick = () => this.generateTailwind();
            }

        } catch (err) {
            console.error("❌ FrdIntent: failed to load analysis", err);
        }
    },

    async generateTailwind() {
        if (!this.importId) return;
        console.log("🚀 FrdIntent: triggering specialized SVG-to-Tailwind generation for", this.importId);
        
        // Mission 123: Preload bar
        document.querySelector('.global-pipeline-header')?.classList.add('is-loading');

        const chat = window.frdApp && window.frdApp.chat;
        if (chat) {
            chat.appendBubble("déclenchement de la forge tailwind (protocole svg ai v1.0)...", 'sullivan');
        }

        try {
            // 1. Déclencher le job
            const res = await fetch('/api/retro-genome/generate-from-svg', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ import_id: this.importId })
            });

            if (!res.ok) throw new Error(`Erreur serveur: ${res.status}`);
            const data = await res.json();
            const jobId = data.job_id;

            if (chat) chat.appendBubble("analyse sémantique en cours... l'architecte sullivan traite votre illustrator.", 'sullivan');

            // 2. Polling du status
            const poll = setInterval(async () => {
                try {
                    const statusRes = await fetch(`/api/retro-genome/svg-job/${jobId}`);
                    const job = await statusRes.json();

                    if (job.status === 'done') {
                        clearInterval(poll);
                        document.querySelector('.global-pipeline-header')?.classList.remove('is-loading');
                        if (chat) chat.appendBubble(`forge terminée ! chargement du template : ${job.template_name}`, 'sullivan');
                        
                        // Charger le nouveau fichier dans l'éditeur
                        await window.frdApp.editor.loadFile(job.template_name);
                        
                        // Fermer le panneau d'analyse
                        const closeBtn = document.getElementById('btn-close-intent');
                        if (closeBtn) closeBtn.click();
                    } else if (job.status === 'failed') {
                        clearInterval(poll);
                        document.querySelector('.global-pipeline-header')?.classList.remove('is-loading');
                        if (chat) chat.appendBubble(`échec de la forge : ${job.error}`, 'sullivan');
                    }
                } catch (e) {
                    clearInterval(poll);
                    document.querySelector('.global-pipeline-header')?.classList.remove('is-loading');
                    console.error("Polling failed", e);
                }
            }, 2000);

        } catch (err) {
            document.querySelector('.global-pipeline-header')?.classList.remove('is-loading');
            console.error("❌ FrdIntent: generation failed", err);
            if (chat) chat.appendBubble("désolé, la forge a rencontré un obstacle technique.", 'sullivan');
        }
    },

    async fetchRawSvg() {
        // On récupère d'abord le path via la liste des imports
        const listRes = await fetch('/api/retro-genome/imports');
        const listData = await listRes.json();
        const entry = (listData.imports || []).find(i => i.id === this.importId);
        
        if (entry && entry.svg_path) {
            const svgRes = await fetch(`/api/retro-genome/import-content?path=${entry.svg_path}`);
            const svgData = await svgRes.json();
            this.svgContent = svgData.svg;
        }
    },

    decodeIllustratorStyles() {
        if (!this.svgContent) return;
        
        // Rule #1: Crack Style Block
        const styleMatch = this.svgContent.match(/<style type="text\/css">([\s\S]*?)<\/style>/);
        if (styleMatch) {
            const styleContent = styleMatch[1];
            const rules = styleContent.match(/\.(st\d+)\{([^}]+)\}/g);
            if (rules) {
                rules.forEach(rule => {
                    const m = rule.match(/\.(st\d+)\{([^}]+)\}/);
                    if (m) this.stylesMap[m[1]] = m[2];
                });
            }
        }
        console.log("🎨 FrdIntent: decoded", Object.keys(this.stylesMap).length, "Illustrator styles.");
    },

    showPanel() {
        const panel = document.getElementById('intent-panel');
        if (panel) {
            panel.classList.remove('hidden');
            setTimeout(() => panel.classList.add('active'), 10);
        }
    },

    renderTable() {
        const list = document.getElementById('intent-list');
        if (!list || !this.analysis) return;
        
        list.innerHTML = "";
        
        this.analysis.components.forEach(comp => {
            const row = document.createElement('tr');
            row.className = "intent-row border-b border-gray-100 hover:bg-[#fdfdfb] transition-colors";
            
            // On enrichit l'affichage avec le mapping couleur si possible
            let typeBadge = comp.type;
            if (comp.type === 'unknown' && this.stylesMap[comp.id]) {
                typeBadge = "shape";
            }

            row.innerHTML = `
                <td class="intent-cell intent-cell-id font-mono text-[10px] text-[#8cc63f]">${comp.id}</td>
                <td class="intent-cell">
                    <span class="intent-cell-type px-1.5 py-0.5 rounded bg-gray-100 text-[11px] uppercase font-bold text-gray-500">
                        ${typeBadge}
                    </span>
                </td>
                <td class="intent-cell">
                    <div class="text-[13px] text-[#3d3d3c] font-medium leading-tight">${comp.name}</div>
                    <div class="text-[12px] text-gray-400 italic">${comp.inferred_intent}</div>
                </td>
                <td class="intent-cell text-right">
                    <button class="btn-intent-action" title="Annoter">
                        <svg class="w-[14px] h-[14px]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                    </button>
                </td>
            `;
            list.appendChild(row);
        });
    }
};

window.FrdIntent = FrdIntent;
export default FrdIntent;
