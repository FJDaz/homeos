/**
 * SULLIVAN RENDERER - Version 1.1
 * Rôle : Génération dynamique de l'interface du Genome Viewer
 * Conformité : Article 5 de la Constitution Aetherflow
 */

class SullivanRenderer {
    constructor() {
        this.methodColors = {
            "GET": "#7aca6a",
            "POST": "#5a9ac6",
            "PUT": "#e4bb5a",
            "DELETE": "#d56363"
        };
    }

    getMethodColor(method) {
        return this.methodColors[method] || "#64748b";
    }

    generateWireframeCorps(visualHint, color = "#7aca6a") {
        if (visualHint === "brainstorm") {
            return `<div style="background:linear-gradient(135deg,#fef3c7 0%,#fde68a 100%);padding:8px;border-radius:8px;height:70px;display:flex;flex-direction:column;gap:4px;justify-content:center;align-items:center;">
                <div style="display:flex;gap:6px;align-items:center;">
                    <span style="font-size:20px;">💡</span>
                    <div style="width:40px;height:3px;background:#fbbf24;border-radius:2px;"></div>
                    <span style="font-size:16px;">📝</span>
                    <div style="width:40px;height:3px;background:#cbd5e1;border-radius:2px;"></div>
                    <span style="font-size:16px;opacity:0.5;">✓</span>
                </div>
                <div style="font-size:10px;color:#92400e;font-weight:600;">Phase créative</div>
            </div>`;
        } else if (visualHint === "backend") {
            return `<div style="background:linear-gradient(135deg,#e0e7ff 0%,#c7d2fe 100%);padding:8px;border-radius:8px;height:70px;display:flex;flex-direction:column;gap:4px;">
                <div style="font-size:10px;color:#3730a3;font-weight:600;">⚙️ Moteur & Données</div>
                <div style="display:flex;gap:4px;align-items:flex-end;flex:1;padding:4px 0;">
                    <div style="flex:1;height:40%;background:#6366f1;border-radius:2px 2px 0 0;"></div>
                    <div style="flex:1;height:70%;background:#6366f1;border-radius:2px 2px 0 0;"></div>
                    <div style="flex:1;height:55%;background:#818cf8;border-radius:2px 2px 0 0;"></div>
                    <div style="flex:1;height:85%;background:#6366f1;border-radius:2px 2px 0 0;"></div>
                </div>
            </div>`;
        } else if (visualHint === "frontend") {
            return `<div style="background:linear-gradient(135deg,#fce7f3 0%,#fbcfe8 100%);padding:8px;border-radius:8px;height:70px;display:flex;flex-direction:column;gap:4px;">
                <div style="font-size:10px;color:#9d174d;font-weight:600;">Design & Interface</div>
                <div style="display:flex;gap:4px;justify-content:center;align-items:center;flex:1;">
                    <div style="width:30%;height:45px;background:rgba(59,130,246,0.3);border:1px dashed #3b82f6;border-radius:4px;"></div>
                    <div style="width:35%;height:45px;background:rgba(16,185,129,0.3);border:1px dashed #10b981;border-radius:4px;"></div>
                    <div style="width:25%;height:45px;background:rgba(236,72,153,0.3);border:1px dashed #ec4899;border-radius:4px;"></div>
                </div>
            </div>`;
        } else if (visualHint === "deploy") {
            return `<div style="background:linear-gradient(135deg,#d1fae5 0%,#a7f3d0 100%);padding:8px;border-radius:8px;height:70px;display:flex;flex-direction:column;gap:4px;justify-content:center;align-items:center;">
                <div style="padding:8px 20px;background:linear-gradient(145deg,#10b981 0%,#059669 100%);border-radius:16px;color:white;font-size:11px;font-weight:700;display:flex;align-items:center;gap:6px;">
                    <span>🚀</span> Publier
                </div>
                <div style="font-size:9px;color:#065f46;">Mise en ligne</div>
            </div>`;
        }
        return this.generateWireframeGeneral(visualHint, color);
    }

    generateWireframeOrganes(visualHint, color = "#7aca6a") {
        if (visualHint === "analyse") {
            return `<div style="background:#f8fafc;padding:6px;border-radius:6px;height:65px;display:flex;flex-direction:column;gap:3px;">
                <div style="display:flex;gap:3px;align-items:center;">
                    <span style="font-size:12px;">🔍</span>
                    <div style="flex:1;height:6px;background:#e2e8f0;border-radius:1px;"></div>
                </div>
                <div style="display:flex;gap:3px;"><div style="flex:2;height:5px;background:#cbd5e1;border-radius:1px;"></div><div style="flex:1;height:5px;background:#7aca6a;border-radius:1px;"></div></div>
                <div style="display:flex;gap:3px;"><div style="flex:2;height:5px;background:#cbd5e1;border-radius:1px;"></div><div style="flex:1;height:5px;background:#cbd5e1;border-radius:1px;"></div></div>
                <div style="display:flex;gap:3px;"><div style="flex:2;height:5px;background:#cbd5e1;border-radius:1px;"></div><div style="flex:1;height:5px;background:#fbbf24;border-radius:1px;"></div></div>
            </div>`;
        } else if (visualHint === "choix") {
            return `<div style="background:#f8fafc;padding:6px;border-radius:6px;height:65px;display:gap:6px;justify-content:center;align-items:center;">
                <div style="width:40%;height:45px;background:white;border:2px solid #7aca6a;border-radius:6px;display:flex;align-items:center;justify-content:center;"><span style="color:#7aca6a;font-size:16px;font-weight:bold;">✓</span></div>
                <div style="width:40%;height:45px;background:#f1f5f9;border:1px solid #cbd5e1;border-radius:6px;display:flex;align-items:center;justify-content:center;"><span style="color:#94a3b8;font-size:16px;">○</span></div>
            </div>`;
        } else if (visualHint === "sauvegarde") {
            return `<div style="background:#f8fafc;padding:6px;border-radius:6px;height:65px;display:flex;flex-direction:column;gap:4px;justify-content:center;align-items:center;">
                <div style="display:flex;gap:8px;align-items:center;">
                    <div style="width:14px;height:14px;background:#7aca6a;border-radius:50%;box-shadow:0 0 8px #7aca6a;"></div>
                    <div style="width:14px;height:14px;background:#7aca6a;border-radius:50%;box-shadow:0 0 8px #7aca6a;"></div>
                    <div style="width:14px;height:14px;background:#7aca6a;border-radius:50%;box-shadow:0 0 8px #7aca6a;"></div>
                    <div style="width:14px;height:14px;background:#e2e8f0;border-radius:50%;"></div>
                </div>
                <div style="font-size:9px;color:#64748b;">3/4 sauvegardé</div>
            </div>`;
        }
        return this.generateWireframeGeneral(visualHint, color);
    }

    generateWireframeGeneral(visualHint, color = "#7aca6a") {
        if (visualHint === "table") {
            return `<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:3px;justify-content:center;">
                <div style="display:flex;gap:3px;"><div style="flex:2;height:5px;background:#e2e8f0;border-radius:1px;"></div><div style="flex:1;height:5px;background:#e2e8f0;border-radius:1px;"></div></div>
                <div style="display:flex;gap:3px;"><div style="flex:2;height:5px;background:#e2e8f0;border-radius:1px;"></div><div style="flex:1;height:5px;background:#7aca6a;border-radius:1px;"></div></div>
                <div style="display:flex;gap:3px;"><div style="flex:2;height:5px;background:#e2e8f0;border-radius:1px;"></div><div style="flex:1;height:5px;background:#e2e8f0;border-radius:1px;"></div></div>
            </div>`;
        }
        return `<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:3px;justify-content:center;">
                <div style="height:6px;background:${color};border-radius:2px;width:30%;"></div>
                <div style="height:4px;background:#e2e8f0;border-radius:1px;"></div>
            </div>`;
    }

    generateComponentCard(comp, level) {
        const name = comp.name || 'Sans nom';
        const hint = comp.visual_hint || 'general';
        const method = comp.method || 'GET';
        const color = this.getMethodColor(method);
        const id = comp.id || 'rand';
        const cid = `cb-${level}-${id}`;

        let wireframe = "";
        if (level === 'corps') wireframe = this.generateWireframeCorps(hint, color);
        else if (level === 'organes') wireframe = this.generateWireframeOrganes(hint, color);
        else if (level === 'cellules') wireframe = this.generateWireframeOrganes(hint, color);
        else wireframe = this.generateWireframeGeneral(hint, color);

        return `
        <div class="comp-card" data-corps="${comp.corps_id || ''}" data-level="${level}" onclick="toggleCheckbox('${cid}')">
            <div class="comp-wireframe">${wireframe}</div>
            <div class="comp-info">
                <div class="comp-name">${name}</div>
                <div class="comp-endpoint">${id}</div>
            </div>
            <div class="comp-footer">
                <div class="comp-method" style="background:${color}20; color:${color};">${method}</div>
                <input type="checkbox" id="${cid}" class="comp-checkbox" onclick="event.stopPropagation(); window.genomeEngine ? window.genomeEngine.updateSelectedComponents() : updateValidateButton();">
            </div>
        </div>`;
    }

    cleanCollect(genome) {
        const corps = genome.n0_phases || [];
        const organes = [];
        const cellules = [];
        const atomes = [];

        corps.forEach(c => {
            if (c.n1_sections) {
                c.n1_sections.forEach(o => {
                    o.corps_id = c.id;
                    organes.push(o);
                    if (o.n2_features) {
                        o.n2_features.forEach(f => {
                            f.corps_id = c.id;
                            f.organe_id = o.id;
                            cellules.push(f);
                            if (f.n3_components) {
                                f.n3_components.forEach(a => {
                                    a.corps_id = c.id;
                                    a.organe_id = o.id;
                                    a.cellule_id = f.id;
                                    atomes.push(a);
                                });
                            }
                        });
                    }
                });
            }
        });
        return { corps, organes, cellules, atomes };
    }

    async render(containerPrefix = "section-") {
        try {
            console.log("🧬 Sullivan Renderer - Démarrage du rendu...");
            const response = await fetch('/api/genome');
            if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);

            const genome = await response.json();
            const { corps, organes, cellules, atomes } = this.cleanCollect(genome);

            const containers = {
                'corps': document.getElementById(`${containerPrefix}corps`),
                'organes': document.getElementById(`${containerPrefix}organes`),
                'cellules': document.getElementById(`${containerPrefix}cellules`),
                'atomes': document.getElementById(`${containerPrefix}atomes`)
            };

            const updateSection = (key, list, label) => {
                const container = containers[key];
                if (container) {
                    const row = container.querySelector('.row');
                    if (row) {
                        row.innerHTML = list.map(item => this.generateComponentCard(item, key)).join('');
                    }
                    const countEl = document.getElementById(`count_${key}`);
                    if (countEl) countEl.textContent = list.length;
                    console.log(`✅ Section ${label} mise à jour (${list.length})`);
                }
            };

            updateSection('corps', corps, 'Corps');
            updateSection('organes', organes, 'Organes');
            updateSection('cellules', cellules, 'Cellules');
            updateSection('atomes', atomes, 'Atomes');

            // Global stats
            const confidenceEl = document.querySelector('.sidebar-section [style*="font-size: 42px"]');
            if (confidenceEl) {
                const conf = Math.round((genome.metadata?.confidence_global || 0.85) * 100);
                confidenceEl.innerHTML = `${conf}%`;
            }

            const setStat = (id, val) => {
                const el = document.getElementById(id);
                if (el) el.textContent = val;
            };

            setStat('total_corps', corps.length);
            setStat('total_organes', organes.length);
            setStat('total_cellules', cellules.length);
            setStat('total_atomes', atomes.length);

            console.log("✨ Rendu Sullivan terminé avec succès.");

        } catch (error) {
            console.error("❌ Sullivan Renderer - Erreur de rendu:", error);
        }
    }
}

window.sullivanRenderer = new SullivanRenderer();
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => window.sullivanRenderer.render());
} else {
    window.sullivanRenderer.render();
}
