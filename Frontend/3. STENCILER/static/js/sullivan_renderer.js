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
            return `<div style="background:#f8fafc;padding:6px;border-radius:6px;height:65px;display:flex;gap:6px;justify-content:center;align-items:center;">
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
        // Tableau de données
        if (visualHint === "table") {
            return `<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:3px;justify-content:center;">
                <div style="display:flex;gap:3px;"><div style="flex:2;height:5px;background:#e2e8f0;border-radius:1px;"></div><div style="flex:1;height:5px;background:#e2e8f0;border-radius:1px;"></div></div>
                <div style="display:flex;gap:3px;"><div style="flex:2;height:5px;background:#e2e8f0;border-radius:1px;"></div><div style="flex:1;height:5px;background:#7aca6a;border-radius:1px;"></div></div>
                <div style="display:flex;gap:3px;"><div style="flex:2;height:5px;background:#e2e8f0;border-radius:1px;"></div><div style="flex:1;height:5px;background:#e2e8f0;border-radius:1px;"></div></div>
            </div>`;
        }
        // Fiche technique détaillée
        else if (visualHint === "detail-card") {
            return `<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:3px;">
                <div style="height:8px;background:${color};border-radius:2px;width:40%;"></div>
                <div style="display:flex;gap:8px;margin-top:4px;">
                    <div style="flex:1;height:4px;background:#e2e8f0;border-radius:1px;"></div>
                    <div style="flex:1;height:4px;background:${color};border-radius:1px;"></div>
                </div>
                <div style="display:flex;gap:8px;">
                    <div style="flex:1;height:4px;background:#e2e8f0;border-radius:1px;"></div>
                    <div style="flex:1;height:4px;background:#e2e8f0;border-radius:1px;"></div>
                </div>
            </div>`;
        }
        // Carte pouvoir avec actions
        else if (visualHint === "stencil-card") {
            return `<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:3px;">
                <div style="height:6px;background:${color};border-radius:2px;width:50%;"></div>
                <div style="height:4px;background:#e2e8f0;border-radius:1px;width:80%;"></div>
                <div style="display:flex;gap:6px;margin-top:6px;justify-content:center;">
                    <div style="width:45%;height:14px;background:${color};border-radius:3px;opacity:0.8;"></div>
                    <div style="width:45%;height:14px;background:#cbd5e1;border-radius:3px;"></div>
                </div>
            </div>`;
        }
        // Formulaire
        else if (visualHint === "form") {
            return `<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:4px;">
                <div style="height:12px;background:#f1f5f9;border:1px solid #e2e8f0;border-radius:3px;"></div>
                <div style="height:12px;background:#f1f5f9;border:1px solid #e2e8f0;border-radius:3px;"></div>
                <div style="display:flex;justify-content:flex-end;margin-top:2px;">
                    <div style="width:35%;height:14px;background:#22c55e;border-radius:3px;"></div>
                </div>
            </div>`;
        }
        // Bouton
        else if (visualHint === "button" || visualHint === "launch-button") {
            return `<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:4px;justify-content:center;align-items:center;">
                <div style="padding:6px 24px;background:${color};border-radius:6px;color:white;font-size:11px;font-weight:600;">Action</div>
                <div style="font-size:9px;color:#94a3b8;">Bouton cliquable</div>
            </div>`;
        }
        // Carte de choix
        else if (visualHint === "choice-card" || visualHint === "card") {
            return `<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;gap:8px;align-items:center;">
                <div style="width:40%;height:45px;background:white;border:2px solid ${color};border-radius:6px;display:flex;align-items:center;justify-content:center;"><span style="color:${color};font-size:14px;font-weight:bold;">✓</span></div>
                <div style="width:40%;height:45px;background:#f1f5f9;border:1px solid #cbd5e1;border-radius:6px;display:flex;align-items:center;justify-content:center;"><span style="color:#94a3b8;font-size:14px;">○</span></div>
            </div>`;
        }
        // Grille
        else if (visualHint === "grid") {
            return `<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:4px;justify-content:center;">
                <div style="display:flex;gap:4px;justify-content:center;">
                    <div style="width:28%;height:20px;background:${color};border-radius:3px;opacity:0.6;"></div>
                    <div style="width:28%;height:20px;background:${color};border-radius:3px;opacity:0.6;"></div>
                    <div style="width:28%;height:20px;background:${color};border-radius:3px;opacity:0.6;"></div>
                </div>
                <div style="display:flex;gap:4px;justify-content:center;">
                    <div style="width:28%;height:20px;background:#e2e8f0;border-radius:3px;"></div>
                    <div style="width:28%;height:20px;background:#e2e8f0;border-radius:3px;"></div>
                    <div style="width:28%;height:20px;background:#e2e8f0;border-radius:3px;"></div>
                </div>
            </div>`;
        }
        // Dashboard
        else if (visualHint === "dashboard") {
            return `<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;gap:6px;">
                <div style="flex:1;display:flex;flex-direction:column;gap:3px;">
                    <div style="height:6px;background:${color};border-radius:2px;width:60%;"></div>
                    <div style="flex:1;background:#e2e8f0;border-radius:3px;"></div>
                </div>
                <div style="flex:1;display:flex;flex-direction:column;gap:3px;">
                    <div style="height:6px;background:${color};border-radius:2px;width:60%;"></div>
                    <div style="flex:1;background:#e2e8f0;border-radius:3px;"></div>
                </div>
            </div>`;
        }
        // Upload
        else if (visualHint === "upload") {
            return `<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:4px;justify-content:center;align-items:center;border:2px dashed #cbd5e1;">
                <div style="font-size:16px;color:#94a3b8;">☁️</div>
                <div style="font-size:9px;color:#64748b;">Glisser-déposer</div>
            </div>`;
        }
        // Modal
        else if (visualHint === "modal") {
            return `<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;justify-content:center;align-items:center;">
                <div style="width:70%;height:45px;background:white;border:1px solid #e2e8f0;border-radius:6px;box-shadow:0 2px 8px rgba(0,0,0,0.1);display:flex;flex-direction:column;gap:3px;padding:6px;">
                    <div style="height:4px;background:${color};border-radius:1px;width:40%;"></div>
                    <div style="flex:1;background:#f1f5f9;border-radius:2px;"></div>
                </div>
            </div>`;
        }
        // Liste
        else if (visualHint === "list") {
            return `<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:3px;justify-content:center;">
                <div style="display:flex;gap:4px;align-items:center;"><div style="width:6px;height:6px;background:${color};border-radius:50%;"></div><div style="flex:1;height:4px;background:#e2e8f0;border-radius:1px;"></div></div>
                <div style="display:flex;gap:4px;align-items:center;"><div style="width:6px;height:6px;background:${color};border-radius:50%;"></div><div style="flex:1;height:4px;background:#e2e8f0;border-radius:1px;"></div></div>
                <div style="display:flex;gap:4px;align-items:center;"><div style="width:6px;height:6px;background:${color};border-radius:50%;"></div><div style="flex:1;height:4px;background:#e2e8f0;border-radius:1px;"></div></div>
            </div>`;
        }
        // Éditeur de code
        else if (visualHint === "editor") {
            return `<div style="background:#1e293b;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:3px;font-family:monospace;">
                <div style="height:3px;background:#64748b;border-radius:1px;width:20%;"></div>
                <div style="height:3px;background:#7dd3fc;border-radius:1px;width:60%;"></div>
                <div style="height:3px;background:#86efac;border-radius:1px;width:40%;"></div>
                <div style="height:3px;background:#fca5a5;border-radius:1px;width:50%;"></div>
            </div>`;
        }
        // Chat / Bulles
        else if (visualHint === "chat/bubble") {
            return `<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:4px;justify-content:center;">
                <div style="align-self:flex-start;padding:4px 8px;background:#e2e8f0;border-radius:12px 12px 12px 4px;font-size:8px;color:#64748b;">Message</div>
                <div style="align-self:flex-end;padding:4px 8px;background:${color};border-radius:12px 12px 4px 12px;font-size:8px;color:white;">Réponse</div>
            </div>`;
        }
        // Input chat
        else if (visualHint === "chat-input") {
            return `<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:4px;justify-content:center;">
                <div style="display:flex;gap:4px;">
                    <div style="flex:1;height:14px;background:white;border:1px solid #e2e8f0;border-radius:12px;"></div>
                    <div style="width:14px;height:14px;background:${color};border-radius:50%;"></div>
                </div>
            </div>`;
        }
        // Breadcrumb
        else if (visualHint === "breadcrumb") {
            return `<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;align-items:center;gap:4px;">
                <div style="padding:3px 8px;background:${color};border-radius:4px;font-size:9px;color:white;">Accueil</div>
                <span style="color:#94a3b8;font-size:10px;">›</span>
                <div style="padding:3px 8px;background:#e2e8f0;border-radius:4px;font-size:9px;color:#64748b;">Page</div>
            </div>`;
        }
        // Palette de couleurs
        else if (visualHint === "color-palette") {
            return `<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:4px;justify-content:center;align-items:center;">
                <div style="display:flex;gap:4px;">
                    <div style="width:16px;height:16px;background:#ef4444;border-radius:4px;"></div>
                    <div style="width:16px;height:16px;background:#22c55e;border-radius:4px;"></div>
                    <div style="width:16px;height:16px;background:#3b82f6;border-radius:4px;"></div>
                    <div style="width:16px;height:16px;background:#eab308;border-radius:4px;"></div>
                </div>
                <div style="font-size:9px;color:#64748b;">Palette</div>
            </div>`;
        }
        // Stepper / Étapes
        else if (visualHint === "stepper") {
            return `<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;align-items:center;justify-content:center;gap:8px;">
                <div style="width:18px;height:18px;background:${color};border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:10px;color:white;font-weight:bold;">1</div>
                <div style="width:20px;height:2px;background:${color};"></div>
                <div style="width:18px;height:18px;background:${color};border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:10px;color:white;font-weight:bold;">2</div>
                <div style="width:20px;height:2px;background:#e2e8f0;"></div>
                <div style="width:18px;height:18px;background:#e2e8f0;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:10px;color:#94a3b8;">3</div>
            </div>`;
        }
        // Contrôles zoom
        else if (visualHint === "zoom-controls") {
            return `<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:4px;justify-content:center;align-items:center;">
                <div style="display:flex;gap:4px;align-items:center;">
                    <div style="padding:2px 8px;background:#e2e8f0;border-radius:4px;font-size:12px;color:#64748b;">−</div>
                    <div style="width:60px;height:4px;background:#cbd5e1;border-radius:2px;"></div>
                    <div style="padding:2px 8px;background:#e2e8f0;border-radius:4px;font-size:12px;color:#64748b;">+</div>
                </div>
            </div>`;
        }
        // Accordéon
        else if (visualHint === "accordion") {
            return `<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:3px;">
                <div style="padding:4px 8px;background:${color};border-radius:4px;display:flex;justify-content:space-between;align-items:center;">
                    <div style="width:40%;height:4px;background:white;border-radius:1px;opacity:0.8;"></div>
                    <div style="font-size:10px;color:white;">▼</div>
                </div>
                <div style="padding:4px 8px;background:#e2e8f0;border-radius:4px;display:flex;justify-content:space-between;align-items:center;">
                    <div style="width:40%;height:4px;background:#64748b;border-radius:1px;"></div>
                    <div style="font-size:10px;color:#64748b;">▶</div>
                </div>
            </div>`;
        }
        // Téléchargement
        else if (visualHint === "download") {
            return `<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:4px;justify-content:center;align-items:center;">
                <div style="font-size:16px;color:${color};">⬇️</div>
                <div style="font-size:9px;color:#64748b;">Télécharger</div>
            </div>`;
        }
        // Aperçu / Preview
        else if (visualHint === "preview") {
            return `<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;gap:6px;">
                <div style="flex:1;background:#e2e8f0;border-radius:4px;display:flex;align-items:center;justify-content:center;">
                    <div style="width:60%;height:40%;background:#cbd5e1;border-radius:2px;"></div>
                </div>
                <div style="width:30%;display:flex;flex-direction:column;gap:3px;">
                    <div style="flex:1;background:${color};border-radius:3px;opacity:0.6;"></div>
                    <div style="flex:1;background:#e2e8f0;border-radius:3px;"></div>
                </div>
            </div>`;
        }
        // Status
        else if (visualHint === "status") {
            return `<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:4px;justify-content:center;align-items:center;">
                <div style="display:flex;gap:6px;align-items:center;">
                    <div style="width:10px;height:10px;background:#22c55e;border-radius:50%;box-shadow:0 0 6px #22c55e;"></div>
                    <div style="width:40px;height:4px;background:#e2e8f0;border-radius:1px;"></div>
                </div>
                <div style="font-size:9px;color:#64748b;">En ligne</div>
            </div>`;
        }
        // Appliquer changements
        else if (visualHint === "apply-changes") {
            return `<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:4px;justify-content:center;align-items:center;">
                <div style="padding:5px 16px;background:linear-gradient(135deg,${color} 0%,#22c55e 100%);border-radius:6px;color:white;font-size:10px;font-weight:600;">Appliquer ✓</div>
            </div>`;
        }
        // Fallback générique amélioré
        return `<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:3px;justify-content:center;">
                <div style="height:6px;background:${color};border-radius:2px;width:30%;"></div>
                <div style="height:4px;background:#e2e8f0;border-radius:1px;width:70%;"></div>
                <div style="height:4px;background:#cbd5e1;border-radius:1px;width:50%;"></div>
            </div>`;
    }

    generateComponentCard(comp, level) {
        const name = comp.name || 'Sans nom';
        let hint = comp.visual_hint || 'general';
        const n = (comp.name || '').toLowerCase();
        const id_lower = (comp.id || '').toLowerCase();

        // Fix 1: Inférer hint depuis name pour les Corps
        if (hint === 'general' && level === 'corps') {
            if (n.includes('brainstorm')) hint = 'brainstorm';
            else if (n.includes('backend') || n.includes('api')) hint = 'backend';
            else if (n.includes('frontend') || n.includes('interface')) hint = 'frontend';
            else if (n.includes('deploy') || n.includes('livraison')) hint = 'deploy';
        }
        // Inférer hint pour les Organes (genome HomeOS spécifique)
        else if (hint === 'general' && level === 'organes') {
            if (id_lower.includes('ir') || n.includes('report') || n.includes('rapport')) hint = 'table';
            else if (id_lower.includes('arbitrage') || n.includes('arbitrage')) hint = 'choice-card';
            else if (id_lower.includes('session') || n.includes('session')) hint = 'status';
            else if (id_lower.includes('navigation') || n.includes('navigation')) hint = 'breadcrumb';
            else if (id_lower.includes('layout') || n.includes('layout')) hint = 'grid';
            else if (id_lower.includes('upload') || n.includes('upload')) hint = 'upload';
            else if (id_lower.includes('analysis') || n.includes('analyse')) hint = 'preview';
            else if (id_lower.includes('dialogue') || n.includes('dialogue')) hint = 'chat/bubble';
            else if (id_lower.includes('validation') || n.includes('validation')) hint = 'dashboard';
            else if (id_lower.includes('adaptation') || n.includes('adaptation') || n.includes('zoom')) hint = 'zoom-controls';
            else if (id_lower.includes('export') || n.includes('export') || n.includes('telechargement')) hint = 'download';
        }
        // Inférer hint pour les Cellules (genome HomeOS spécifique)
        else if (hint === 'general' && level === 'cellules') {
            if (id_lower.includes('ir_report') || n.includes('rapport ir')) hint = 'table';
            else if (id_lower.includes('stencils') || n.includes('stencil')) hint = 'choice-card';
            else if (id_lower.includes('session_mgmt') || n.includes('gestion session')) hint = 'status';
            else if (id_lower.includes('stepper') || n.includes('navigation ux')) hint = 'stepper';
            else if (id_lower.includes('layouts') || n.includes('galerie')) hint = 'grid';
            else if (id_lower.includes('upload') || n.includes('upload')) hint = 'upload';
            else if (id_lower.includes('vision') || n.includes('visuel')) hint = 'preview';
            else if (id_lower.includes('chat') || n.includes('chat')) hint = 'chat-input';
            else if (id_lower.includes('validation') || n.includes('recap')) hint = 'dashboard';
            else if (id_lower.includes('zoom') || n.includes('zoom')) hint = 'zoom-controls';
            else if (id_lower.includes('export') || n.includes('export')) hint = 'download';
        }

        const method = comp.method || 'GET';
        const color = this.getMethodColor(method);
        const id = comp.id || 'rand';
        const cid = `cb-${level}-${id}`;

        let wireframe = "";
        if (level === 'corps') wireframe = this.generateWireframeCorps(hint, color);
        else if (level === 'organes') wireframe = this.generateWireframeGeneral(hint, color);
        else if (level === 'cellules') wireframe = this.generateWireframeGeneral(hint, color);
        else wireframe = this.generateWireframeGeneral(hint, color);

        // Fix 3: description_ui affichée sur 2 lignes
        const descriptionText = comp.description_ui || comp.description || '';

        // Mission C: Click handler pour drill-down Corps
        const clickHandler = level === 'corps'
            ? `console.log('[DRILL] Clic sur Corps', '${comp.id}'); if(window.genomeEngine){window.genomeEngine.drillInto('${comp.id}', '${name.replace(/'/g, "\\'")}');}else{console.error('[DRILL] genomeEngine non dispo');} toggleCheckbox('${cid}');`
            : `toggleCheckbox('${cid}')`;

        return `
        <div class="comp-card" data-corps="${comp.corps_id || ''}" data-level="${level}" onclick="${clickHandler}">
            <div class="comp-wireframe">${wireframe}</div>
            <div class="comp-info">
                <div class="comp-name">${name}</div>
                <div class="comp-endpoint">${id}</div>
                <div style="font-size:9px;color:#94a3b8;line-height:1.3;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;">${descriptionText}</div>
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
