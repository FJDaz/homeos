import json
from pathlib import Path
from datetime import datetime

genome = {
    "metadata": {
        "intent": "PaaS_Studio_MANIFEST_FRD",
        "version": "3.0-manifest",
        "generated_at": datetime.now().isoformat(),
        "confidence_global": 0.95,
        "composants_count": 15
    },
    "topology": ["Brainstorm", "Back", "Front", "Deploy"],
    "endpoints": [],
    "schema_definitions": {},
    "n0_phases": [
        {
            "id": "phase_1_brs",
            "name": "Phase 1 - BRS (Brain-Reasoning-Service)",
            "n1_sections": [
                {
                    "id": "brs_main",
                    "name": "Main Area (Multiverse)",
                    "ui_role": "main-canvas",
                    "dominant_zone": "main",
                    "n2_features": [
                        {
                            "id": "feat_brs_multiverse",
                            "name": "LLM Confrontation",
                            "n3_components": [
                                {
                                    "id": "comp_brs_iframes",
                                    "name": "Multiverse Columns",
                                    "endpoint": "/brs/multiverse",
                                    "method": "GET",
                                    "visual_hint": "grid",
                                    "layout_hint": "grid",
                                    "interaction_type": "view",
                                    "description_ui": "Alignement de 2 ou 3 colonnes d'iframes hébergeant les bots."
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "brs_sidebar_left",
                    "name": "Sidebar Left (Moteur Sullivan)",
                    "ui_role": "left-sidebar",
                    "dominant_zone": "sidebar",
                    "n2_features": [
                        {
                            "id": "feat_brs_search",
                            "name": "Recherche",
                            "n3_components": [
                                {
                                    "id": "comp_brs_search",
                                    "name": "Centre de Recherche",
                                    "endpoint": "/brs/search",
                                    "method": "POST",
                                    "visual_hint": "form",
                                    "layout_hint": "stack",
                                    "interaction_type": "submit",
                                    "description_ui": "Centre de recherche simple avec placeholder explicite et facettes."
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "brs_sidebar_right",
                    "name": "Sidebar Right (Arbitrage Sullivan)",
                    "ui_role": "settings-panel",
                    "dominant_zone": "sidebar",
                    "n2_features": [
                        {
                            "id": "feat_brs_arbitrage",
                            "name": "Arbitrage",
                            "n3_components": [
                                {
                                    "id": "comp_brs_arbitrage",
                                    "name": "Arbitrage Dashboard",
                                    "endpoint": "/brs/arbitrage",
                                    "method": "GET",
                                    "visual_hint": "dashboard",
                                    "layout_hint": "stack",
                                    "interaction_type": "view",
                                    "description_ui": "Sullivan récolte les données pour rendre un arbitrage."
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "brs_footer",
                    "name": "Footer Collapsible (La Trace)",
                    "ui_role": "status-bar",
                    "dominant_zone": "footer",
                    "n2_features": [
                        {
                            "id": "feat_brs_trace",
                            "name": "Trace",
                            "n3_components": [
                                {
                                    "id": "comp_brs_trace",
                                    "name": "Trace Logs",
                                    "endpoint": "/brs/trace",
                                    "method": "GET",
                                    "visual_hint": "table",
                                    "layout_hint": "grid",
                                    "interaction_type": "click",
                                    "description_ui": "Divisé en colonnes reprenant la zone principale. Clic pour recharger."
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "id": "phase_2_bkd",
            "name": "Phase 2 - BKD (La Forge)",
            "n1_sections": [
                {
                    "id": "bkd_sidebar_left",
                    "name": "Sidebar Left (Workspace)",
                    "ui_role": "left-sidebar",
                    "dominant_zone": "sidebar",
                    "n2_features": [
                        {
                            "id": "feat_bkd_files",
                            "name": "Explorateur",
                            "n3_components": [
                                {
                                    "id": "comp_bkd_files",
                                    "name": "File Explorer",
                                    "endpoint": "/bkd/files",
                                    "method": "GET",
                                    "visual_hint": "list",
                                    "layout_hint": "stack",
                                    "interaction_type": "click",
                                    "description_ui": "Explorateur de fichiers local et cloud."
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "bkd_main",
                    "name": "Main Area (Edition & Roadmap)",
                    "ui_role": "main-canvas",
                    "dominant_zone": "main",
                    "n2_features": [
                        {
                            "id": "feat_bkd_editor",
                            "name": "Code Editor",
                            "n3_components": [
                                {
                                    "id": "comp_bkd_editor",
                                    "name": "Éditeur de Code",
                                    "endpoint": "/bkd/edit",
                                    "method": "PUT",
                                    "visual_hint": "editor",
                                    "layout_hint": "stack",
                                    "interaction_type": "edit",
                                    "description_ui": "Éditeur simplifié splittable."
                                },
                                {
                                    "id": "comp_bkd_roadmap",
                                    "name": "Roadmap Track",
                                    "endpoint": "/bkd/roadmap",
                                    "method": "GET",
                                    "visual_hint": "dashboard",
                                    "layout_hint": "stack",
                                    "interaction_type": "view",
                                    "description_ui": "Suivi temps réel des fichiers ROADMAP."
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "bkd_sidebar_right",
                    "name": "Sidebar Right (Majordome Sullivan)",
                    "ui_role": "settings-panel",
                    "dominant_zone": "sidebar",
                    "n2_features": [
                        {
                            "id": "feat_bkd_agent",
                            "name": "Agent Assist",
                            "n3_components": [
                                {
                                    "id": "comp_bkd_agent",
                                    "name": "Chat Majordome",
                                    "endpoint": "/bkd/agent",
                                    "method": "POST",
                                    "visual_hint": "chat-input",
                                    "layout_hint": "stack",
                                    "interaction_type": "submit",
                                    "description_ui": "Pilotage par Gemini pour les actions courantes."
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "bkd_footer",
                    "name": "Footer (Terminal & Audit)",
                    "ui_role": "status-bar",
                    "dominant_zone": "footer",
                    "n2_features": [
                        {
                            "id": "feat_bkd_term",
                            "name": "Terminal",
                            "n3_components": [
                                {
                                    "id": "comp_bkd_term",
                                    "name": "Terminal Output",
                                    "endpoint": "/bkd/terminal",
                                    "method": "GET",
                                    "visual_hint": "status",
                                    "layout_hint": "stack",
                                    "interaction_type": "view",
                                    "description_ui": "Terminal de commande et suivi audit."
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "id": "phase_3_frd",
            "name": "Phase 3 - FRD (Le Tisseur)",
            "n1_sections": [
                {
                    "id": "frd_main",
                    "name": "Main Area (Genome Viewer)",
                    "ui_role": "main-canvas",
                    "dominant_zone": "main",
                    "n2_features": [
                        {
                            "id": "feat_frd_viewer",
                            "name": "Genome Render",
                            "n3_components": [
                                {
                                    "id": "comp_frd_viewer",
                                    "name": "Genome Explorer",
                                    "endpoint": "/frd/genome",
                                    "method": "GET",
                                    "visual_hint": "preview",
                                    "layout_hint": "canvas",
                                    "interaction_type": "click",
                                    "description_ui": "Visualisation explosive des organes."
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "frd_sidebar_left",
                    "name": "Sidebar Left (Le Pourquoi)",
                    "ui_role": "left-sidebar",
                    "dominant_zone": "sidebar",
                    "n2_features": [
                        {
                            "id": "feat_frd_history",
                            "name": "History Intents",
                            "n3_components": [
                                {
                                    "id": "comp_frd_history",
                                    "name": "Intent Feed",
                                    "endpoint": "/frd/history",
                                    "method": "GET",
                                    "visual_hint": "list",
                                    "layout_hint": "stack",
                                    "interaction_type": "view",
                                    "description_ui": "Historique des intentions ayant motivé les générations."
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "frd_sidebar_right",
                    "name": "Sidebar Right (Pédagogie)",
                    "ui_role": "settings-panel",
                    "dominant_zone": "sidebar",
                    "n2_features": [
                        {
                            "id": "feat_frd_pedagogie",
                            "name": "Structure HCl",
                            "n3_components": [
                                {
                                    "id": "comp_frd_pedagogie",
                                    "name": "Pedagogy Chat",
                                    "endpoint": "/frd/ask",
                                    "method": "POST",
                                    "visual_hint": "chat-input",
                                    "layout_hint": "stack",
                                    "interaction_type": "submit",
                                    "description_ui": "Sullivan répond sur la structure technique."
                                },
                                {
                                    "id": "comp_frd_style",
                                    "name": "Style Choice",
                                    "endpoint": "/frd/style",
                                    "method": "PUT",
                                    "visual_hint": "choice-card",
                                    "layout_hint": "grid",
                                    "interaction_type": "click",
                                    "description_ui": "Choix entre 8 styles ou upload."
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "frd_footer",
                    "name": "Footer Contextuel",
                    "ui_role": "status-bar",
                    "dominant_zone": "footer",
                    "n2_features": [
                        {
                            "id": "feat_frd_context",
                            "name": "Hover Context",
                            "n3_components": [
                                {
                                    "id": "comp_frd_context",
                                    "name": "Tooltip Info",
                                    "endpoint": "/frd/hover",
                                    "method": "GET",
                                    "visual_hint": "status",
                                    "layout_hint": "stack",
                                    "interaction_type": "view",
                                    "description_ui": "Explication de l'usage et Intent au survol."
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "id": "phase_4_dpl",
            "name": "Phase 4 - DPL (Le Propulseur)",
            "n1_sections": [
                {
                    "id": "dpl_sidebar_left",
                    "name": "Sidebar Left (Configurations)",
                    "ui_role": "left-sidebar",
                    "dominant_zone": "sidebar",
                    "n2_features": [
                        {
                            "id": "feat_dpl_configs",
                            "name": "Deploy Configs",
                            "n3_components": [
                                {
                                    "id": "comp_dpl_secrets",
                                    "name": "Secrets Manager",
                                    "endpoint": "/dpl/secrets",
                                    "method": "PUT",
                                    "visual_hint": "form",
                                    "layout_hint": "stack",
                                    "interaction_type": "edit",
                                    "description_ui": "Gestion des secrets, clés API."
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "dpl_main",
                    "name": "Main Area (Dual Col)",
                    "ui_role": "main-canvas",
                    "dominant_zone": "main",
                    "n2_features": [
                        {
                            "id": "feat_dpl_ops",
                            "name": "Operations",
                            "n3_components": [
                                {
                                    "id": "comp_dpl_chat",
                                    "name": "Sullivan Ops",
                                    "endpoint": "/dpl/ops",
                                    "method": "POST",
                                    "visual_hint": "chat-input",
                                    "layout_hint": "stack",
                                    "interaction_type": "submit",
                                    "description_ui": "Instructions et chat de pilotage."
                                },
                                {
                                    "id": "comp_dpl_iframe",
                                    "name": "Third-Party UI",
                                    "endpoint": "/dpl/service",
                                    "method": "GET",
                                    "visual_hint": "preview",
                                    "layout_hint": "stack",
                                    "interaction_type": "view",
                                    "description_ui": "UI native du service de déploiement."
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "dpl_sidebar_right",
                    "name": "Sidebar Right (Guide Sullivan)",
                    "ui_role": "settings-panel",
                    "dominant_zone": "sidebar",
                    "n2_features": [
                        {
                            "id": "feat_dpl_guide",
                            "name": "Capture Guide",
                            "n3_components": [
                                {
                                    "id": "comp_dpl_capture",
                                    "name": "Capture Action",
                                    "endpoint": "/dpl/capture",
                                    "method": "POST",
                                    "visual_hint": "launch-button",
                                    "layout_hint": "stack",
                                    "interaction_type": "click",
                                    "description_ui": "Bouton Capture pour analyse Gemini Vision."
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}

out_path = Path("Frontend/2. GENOME/genome_manifest.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(genome, f, indent=2, ensure_ascii=False)
print("✅ N0_phases generated in", str(out_path))
