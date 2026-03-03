# Backend/Prod/exporters/topology_bank.py
#!/usr/bin/env python3
"""
Banque de topologies (Moteur de Layout Dynamique)
20 squelettes spatiaux couvrant 90%+ des interfaces B2B modernes.
Chaque topologie = distribution pure, agnostique du contenu.
Refs = 2 exemples de production canoniques par structure.
"""
from typing import Dict, List, TypedDict, Union, Optional

class RoleLayout(TypedDict):
    w: str
    h: int

class TopologyLayout(TypedDict):
    type: str
    padding: int
    roles: Dict[str, RoleLayout]

class Topology(TypedDict):
    description: str
    refs: List[str]
    layout: TopologyLayout

TOPOLOGIES: Dict[str, Topology] = {
    # ─── 1. DASHBOARD GRID ───────────────────────────────────────────────────
    # Grille dense : métriques en frise haute, graphe principal large,
    # sidebar secondaire. Pattern Vercel/Datadog.
    "dashboard_grid": {
        "description": (
            "Grille dense avec frise de métriques en haut (4×25%), "
            "espace principal asymétrique : graphe large (66%) + liste/détail (33%)."
        ),
        "refs": [
            "https://tailwindui.com/components/application-ui/page-examples/home-screens",
            "https://vercel.com/dashboard"
        ],
        "layout": {
            "type": "grid",
            "padding": 24,
            "roles": {
                "metric":   {"w": "25%", "h": 120},
                "chart":    {"w": "66%", "h": 400},
                "list":     {"w": "33%", "h": 400},
                "default":  {"w": "100%", "h": 200}
            }
        }
    },

    # ─── 2. BENTO GRID ───────────────────────────────────────────────────────
    # Cartes modulaires de tailles variées, hiérarchie visuelle Apple-like.
    # Grandes cartes hero côte à côte, petites cartes en dessous.
    "bento_grid": {
        "description": (
            "Cartes modulaires de tailles variées. "
            "Feature hero 50%, features secondaires 25%, action CTA pleine largeur."
        ),
        "refs": [
            "https://linear.app/features",
            "https://bentogrids.com/"
        ],
        "layout": {
            "type": "masonry",
            "padding": 16,
            "roles": {
                "feature-highlight": {"w": "50%", "h": 400},
                "feature-minor":     {"w": "25%", "h": 200},
                "action":            {"w": "100%", "h": 100},
                "default":           {"w": "50%", "h": 200}
            }
        }
    },

    # ─── 3. SPLIT PANE FORM ──────────────────────────────────────────────────
    # Écran splitté : contexte/info d'un côté, formulaire de l'autre.
    # Pattern Stripe Checkout, authentification.
    "split_pane_form": {
        "description": (
            "Écran splitté : contexte visuel/info (40% gauche) "
            "et formulaire étape par étape (60% droite)."
        ),
        "refs": [
            "https://stripe.com/docs/payments/checkout",
            "https://tailwindui.com/components/application-ui/forms/form-layouts"
        ],
        "layout": {
            "type": "flex-row",
            "padding": 40,
            "roles": {
                "context-panel": {"w": "40%", "h": "100%"},
                "form-panel":    {"w": "60%", "h": "100%"},
                "default":       {"w": "100%", "h": "auto"}
            }
        }
    },

    # ─── 4. SINGLE COLUMN FOCUS ──────────────────────────────────────────────
    # Colonne unique centrée, max 680px. Onboarding immersif, lecture.
    "single_column_focus": {
        "description": (
            "Colonne unique centrale (max 680px) pour lecture ou onboarding immersif. "
            "Zéro distraction, progression linéaire."
        ),
        "refs": [
            "https://tally.so/",
            "https://medium.com/"
        ],
        "layout": {
            "type": "flex-col-centered",
            "max_width": 680,
            "padding": 40,
            "roles": {
                "header-text":   {"w": "100%", "h": 100},
                "content-block": {"w": "100%", "h": "auto"},
                "action-footer": {"w": "100%", "h": 80},
                "default":       {"w": "100%", "h": "auto"}
            }
        }
    },

    # ─── 5. DATA DENSE TABLE ─────────────────────────────────────────────────
    # Tableau pleine largeur avec barre de filtres haute, rows de données,
    # pagination basse. Pattern Airtable, Linear issues.
    "data_dense_table": {
        "description": (
            "Tableau de données dense pleine largeur : barre de filtres/recherche (40px), "
            "en-tête colonnes (36px), rows de données (36px chacune), pagination (44px)."
        ),
        "refs": [
            "https://linear.app/docs/views",
            "https://airtable.com/templates"
        ],
        "layout": {
            "type": "flex-col",
            "padding": 16,
            "roles": {
                "filter-bar":   {"w": "100%", "h": 44},
                "table-header": {"w": "100%", "h": 36},
                "table-row":    {"w": "100%", "h": 36},
                "verdict-badge":{"w": "15%",  "h": 28},
                "pagination":   {"w": "100%", "h": 44},
                "default":      {"w": "100%", "h": 36}
            }
        }
    },

    # ─── 6. CHAT THREAD ──────────────────────────────────────────────────────
    # Fil conversationnel : bulles alternées gauche/droite, input fixe en bas.
    # Pattern Slack, Intercom.
    "chat_thread": {
        "description": (
            "Fil conversationnel avec bulles alternées (user droite, IA gauche), "
            "zone de messages scrollable, input message fixé en bas."
        ),
        "refs": [
            "https://slack.com/features/messaging",
            "https://www.intercom.com/features/inbox"
        ],
        "layout": {
            "type": "flex-col",
            "padding": 16,
            "roles": {
                "message-user": {"w": "65%", "h": 56, "align": "right"},
                "message-ai":   {"w": "65%", "h": 56, "align": "left"},
                "choice-card":  {"w": "100%", "h": 80},
                "input-bar":    {"w": "100%", "h": 56},
                "default":      {"w": "100%", "h": 56}
            }
        }
    },

    # ─── 7. STEPPER WIZARD ───────────────────────────────────────────────────
    # Indicateur d'étapes horizontal en haut (numéros + labels),
    # contenu central de l'étape active, boutons Précédent/Suivant en bas.
    "stepper_wizard": {
        "description": (
            "Wizard multi-étapes : stepper horizontal (48px), "
            "contenu de l'étape active centré, "
            "footer de navigation Précédent/Suivant (64px)."
        ),
        "refs": [
            "https://www.typeform.com/",
            "https://ui.shadcn.com/docs/components/stepper"
        ],
        "layout": {
            "type": "flex-col-centered",
            "max_width": 720,
            "padding": 32,
            "roles": {
                "step-indicator": {"w": "100%", "h": 48},
                "step-content":   {"w": "100%", "h": "auto"},
                "form-input":     {"w": "100%", "h": 52},
                "nav-buttons":    {"w": "100%", "h": 64},
                "default":        {"w": "100%", "h": "auto"}
            }
        }
    },

    # ─── 8. CARD GALLERY ─────────────────────────────────────────────────────
    # Grille de cartes sélectionnables, 3 colonnes égales.
    # Pattern Framer Templates, Notion Gallery.
    "card_gallery": {
        "description": (
            "Galerie de cartes sélectionnables en grille 3 colonnes. "
            "Chaque carte = preview visuel + titre + badge. Hover = mise en avant."
        ),
        "refs": [
            "https://www.framer.com/templates/",
            "https://www.notion.so/templates"
        ],
        "layout": {
            "type": "grid",
            "columns": 3,
            "padding": 20,
            "roles": {
                "card-preview":  {"w": "33%", "h": 220},
                "card-featured": {"w": "66%", "h": 220},
                "filter-row":    {"w": "100%", "h": 48},
                "default":       {"w": "33%", "h": 200}
            }
        }
    },

    # ─── 9. MASTER DETAIL ────────────────────────────────────────────────────
    # Liste maître étroite (32% gauche) + panneau de détail large (68% droite).
    # Pattern Mail.app, Notion sidebar.
    "master_detail": {
        "description": (
            "Vue maître-détail : liste de navigation étroite (32%) à gauche, "
            "panneau de détail/édition large (68%) à droite. "
            "Sélection dans liste = mise à jour du détail."
        ),
        "refs": [
            "https://developer.apple.com/design/human-interface-guidelines/split-views",
            "https://www.notion.so/"
        ],
        "layout": {
            "type": "flex-row",
            "padding": 0,
            "roles": {
                "list-item":     {"w": "32%", "h": 52},
                "list-header":   {"w": "32%", "h": 40},
                "detail-header": {"w": "68%", "h": 56},
                "detail-body":   {"w": "68%", "h": "auto"},
                "detail-action": {"w": "68%", "h": 56},
                "default":       {"w": "68%", "h": "auto"}
            }
        }
    },

    # ─── 10. Z PATTERN LANDING ───────────────────────────────────────────────
    # Alternance texte-image en rangées (pattern Z de lecture).
    # Rangée impaire : texte gauche + image droite.
    # Rangée paire : image gauche + texte droite.
    "z_pattern_landing": {
        "description": (
            "Pattern Z de lecture : rangées alternées texte (50%) / visuel (50%). "
            "Impaire = texte gauche, paire = texte droite. Hero pleine largeur en tête."
        ),
        "refs": [
            "https://stripe.com/",
            "https://pitch.com/"
        ],
        "layout": {
            "type": "z-alternating",
            "padding": 48,
            "roles": {
                "hero":          {"w": "100%", "h": 320},
                "text-block":    {"w": "50%",  "h": 280},
                "visual-block":  {"w": "50%",  "h": 280},
                "cta-banner":    {"w": "100%", "h": 120},
                "default":       {"w": "50%",  "h": 280}
            }
        }
    },

    # ─── 11. SPLIT EDITORIAL ─────────────────────────────────────────────────
    # Deux colonnes fixes : contenu textuel riche (60%) + visuel/media (40%).
    # Pattern Substack article, Ghost blog.
    "split_editorial": {
        "description": (
            "Deux colonnes fixes côte à côte : "
            "contenu textuel riche (60% gauche) et zone visuelle/media (40% droite). "
            "Idéal pour articles, rapports d'analyse."
        ),
        "refs": [
            "https://substack.com/",
            "https://ghost.org/features/"
        ],
        "layout": {
            "type": "flex-row",
            "padding": 32,
            "roles": {
                "text-body":    {"w": "60%", "h": "auto"},
                "media-panel":  {"w": "40%", "h": 360},
                "caption":      {"w": "40%", "h": 48},
                "default":      {"w": "60%", "h": "auto"}
            }
        }
    },

    # ─── 12. UPLOAD DROPZONE ─────────────────────────────────────────────────
    # Grande zone de dépôt centrale, liste de fichiers déposés en dessous,
    # barre de progression + bouton de validation.
    "upload_dropzone": {
        "description": (
            "Zone de drag-and-drop centrale et proéminente (200px min), "
            "liste des fichiers chargés avec statuts, "
            "barre de progression globale et bouton de validation."
        ),
        "refs": [
            "https://www.filepond.io/",
            "https://uploadthing.com/"
        ],
        "layout": {
            "type": "flex-col-centered",
            "max_width": 720,
            "padding": 32,
            "roles": {
                "dropzone":      {"w": "100%", "h": 200},
                "file-item":     {"w": "100%", "h": 48},
                "progress-bar":  {"w": "100%", "h": 28},
                "submit-action": {"w": "100%", "h": 52},
                "default":       {"w": "100%", "h": 48}
            }
        }
    },

    # ─── 13. CANVAS ANNOTATED ─────────────────────────────────────────────────
    # Surface de travail principale (80%) avec panneau d'annotations/propriétés
    # flottant à droite (20%) et toolbar compacte en haut.
    "canvas_annotated": {
        "description": (
            "Surface de travail visuelle large (80%) avec toolbar compacte (40px), "
            "panneau latéral droit d'annotations et propriétés (20%). "
            "Pattern Figma, Miro."
        ),
        "refs": [
            "https://www.figma.com/",
            "https://miro.com/"
        ],
        "layout": {
            "type": "flex-row",
            "padding": 0,
            "roles": {
                "toolbar":       {"w": "100%", "h": 40},
                "canvas-area":   {"w": "80%",  "h": "auto"},
                "overlay-layer": {"w": "80%",  "h": "auto"},
                "property-panel":{"w": "20%",  "h": "auto"},
                "default":       {"w": "80%",  "h": "auto"}
            }
        }
    },

    # ─── 14. SETTINGS LIST ───────────────────────────────────────────────────
    # Tabs de navigation verticale à gauche (25%), panneau de réglages à droite (75%)
    # organisé en sections avec toggles/inputs. Pattern GitHub Settings.
    "settings_list": {
        "description": (
            "Navigation par onglets verticaux (25% gauche) + "
            "contenu de réglages à droite (75%) : sections avec titre, "
            "rows toggle/input, bouton de sauvegarde en bas."
        ),
        "refs": [
            "https://github.com/settings/profile",
            "https://app.linear.app/settings/general"
        ],
        "layout": {
            "type": "flex-row",
            "padding": 0,
            "roles": {
                "settings-nav":    {"w": "25%", "h": "auto"},
                "settings-section":{"w": "75%", "h": "auto"},
                "toggle-row":      {"w": "75%", "h": 52},
                "input-row":       {"w": "75%", "h": 64},
                "save-footer":     {"w": "75%", "h": 56},
                "default":         {"w": "75%", "h": 52}
            }
        }
    },

    # ─── 15. METRICS KPI ROW ─────────────────────────────────────────────────
    # Frise compacte de KPIs (5–6 cartes égales, pleine largeur).
    # En dessous : graphe temps-réel pleine largeur + table détaillée.
    "metrics_kpi_row": {
        "description": (
            "Frise compacte de KPI (5 cartes 20%, hauteur 88px), "
            "suivi d'un graphe temps-réel pleine largeur (280px) "
            "et d'une table de logs/événements."
        ),
        "refs": [
            "https://grafana.com/grafana/dashboards/",
            "https://www.datadoghq.com/product/dashboards/"
        ],
        "layout": {
            "type": "grid",
            "padding": 16,
            "roles": {
                "kpi-card":   {"w": "20%",  "h": 88},
                "sparkline":  {"w": "20%",  "h": 88},
                "graph":      {"w": "100%", "h": 280},
                "log-row":    {"w": "100%", "h": 32},
                "default":    {"w": "20%",  "h": 88}
            }
        }
    },

    # ─── 16. TIMELINE FEED ───────────────────────────────────────────────────
    # Fil d'activité chronologique vertical. Chaque item = timestamp +
    # avatar + contenu variable. Scroll infini.
    "timeline_feed": {
        "description": (
            "Fil d'activité chronologique vertical pleine largeur (max 720px centré) : "
            "chaque événement = timestamp + avatar + contenu variable. "
            "Items groupés par date. Pattern GitHub Activity, Notion changelog."
        ),
        "refs": [
            "https://github.com/",
            "https://www.figma.com/release-notes/"
        ],
        "layout": {
            "type": "flex-col-centered",
            "max_width": 720,
            "padding": 24,
            "roles": {
                "date-separator": {"w": "100%", "h": 32},
                "feed-item":      {"w": "100%", "h": 72},
                "feed-item-rich": {"w": "100%", "h": 120},
                "load-more":      {"w": "100%", "h": 44},
                "default":        {"w": "100%", "h": 72}
            }
        }
    },

    # ─── 17. MODAL DIALOG ────────────────────────────────────────────────────
    # Overlay semi-transparent + dialogue centré avec en-tête, corps scrollable,
    # footer d'actions. Pattern Radix Dialog, Headless UI.
    "modal_dialog": {
        "description": (
            "Overlay semi-transparent avec dialogue centré (max 480px) : "
            "en-tête titre + bouton fermer (56px), corps scrollable, "
            "footer avec boutons Annuler/Confirmer (60px)."
        ),
        "refs": [
            "https://ui.shadcn.com/docs/components/dialog",
            "https://headlessui.com/react/dialog"
        ],
        "layout": {
            "type": "overlay-centered",
            "max_width": 480,
            "padding": 0,
            "roles": {
                "dialog-header": {"w": "100%", "h": 56},
                "dialog-body":   {"w": "100%", "h": "auto"},
                "form-input":    {"w": "100%", "h": 52},
                "dialog-footer": {"w": "100%", "h": 60},
                "default":       {"w": "100%", "h": "auto"}
            }
        }
    },

    # ─── 18. EXPORT DOWNLOAD ─────────────────────────────────────────────────
    # Cartes de formats d'export (2 colonnes), récapitulatif des métadonnées,
    # CTA de téléchargement proéminent en bas.
    "export_download": {
        "description": (
            "Sélection du format d'export en 2 colonnes (SVG/JSON/ZIP/PDF), "
            "récapitulatif des métadonnées, "
            "bouton de téléchargement principal proéminent."
        ),
        "refs": [
            "https://www.figma.com/design/export",
            "https://www.sketch.com/docs/importing-and-exporting/"
        ],
        "layout": {
            "type": "grid",
            "padding": 24,
            "roles": {
                "format-card":   {"w": "50%",  "h": 96},
                "meta-row":      {"w": "100%", "h": 36},
                "option-toggle": {"w": "100%", "h": 44},
                "download-cta":  {"w": "100%", "h": 56},
                "default":       {"w": "50%",  "h": 96}
            }
        }
    },

    # ─── 19. ACCORDION SECTIONS ─────────────────────────────────────────────────
    # Sections empilées verticalement, chacune avec titre cliquable (40px)
    # et corps rétractable. Pattern FAQ, paramètres avancés, docs.
    "accordion_sections": {
        "description": (
            "Sections verticales empilées avec en-têtes cliquables (40px) "
            "et corps rétractables. Séparateurs visuels entre sections. "
            "Pattern FAQ, paramètres avancés, documentation."
        ),
        "refs": [
            "https://ui.shadcn.com/docs/components/accordion",
            "https://www.radix-ui.com/primitives/docs/components/accordion"
        ],
        "layout": {
            "type": "flex-col",
            "padding": 16,
            "roles": {
                "section-header":  {"w": "100%", "h": 48},
                "section-content": {"w": "100%", "h": "auto"},
                "content-block":   {"w": "100%", "h": 120},
                "separator":       {"w": "100%", "h": 1},
                "default":         {"w": "100%", "h": 48}
            }
        }
    },

    # ─── 20. KANBAN COLUMNS ───────────────────────────────────────────────────
    # Board Kanban : 3–4 colonnes de statut de largeur égale, chacune
    # avec en-tête + pile de cartes scrollable. Pattern Trello, Linear Board.
        "kanban_columns": {
        "description": (
            "Board Kanban multi-colonnes (3–4 statuts de largeur égale) : "
            "chaque colonne = en-tête statut (44px) + pile de cartes (80px chacune) + "
            "bouton d'ajout. Scroll vertical par colonne."
        ),
        "refs": [
            "https://trello.com/",
            "https://linear.app/docs/board-view"
        ],
        "layout": {
            "type": "flex-row-columns",
            "columns": 4,
            "padding": 16,
            "roles": {
                "column-header": {"w": "25%", "h": 44},
                "kanban-card":   {"w": "25%", "h": 80},
                "card-compact":  {"w": "25%", "h": 56},
                "add-card":      {"w": "25%", "h": 36},
                "default":       {"w": "25%", "h": 80}
            }
        }
    },
}

ROLE_TO_TOPOLOGY: Dict[str, str] = {
    "dashboard":      "dashboard_grid",
    "main-content":   "bento_grid",
    "form-panel":     "split_pane_form",
    "onboarding-flow":"stepper_wizard",
    "chat-overlay":   "chat_thread",
    "upload-zone":    "upload_dropzone",
    "main-canvas":    "canvas_annotated",
    "settings-panel": "settings_list",
    "export-action":  "export_download",
    "overlay":        "modal_dialog",
    "status-bar":     "metrics_kpi_row",
    "left-sidebar":   "master_detail",
    "nav-header":     "z_pattern_landing",
}

def get_topology(name: str) -> Topology:
    """Retourne la topologie par nom, ou dashboard_grid par défaut."""
    return TOPOLOGIES.get(name, TOPOLOGIES["dashboard_grid"])

def list_topologies() -> List[str]:
    """Retourne les noms de toutes les topologies disponibles."""
    return list(TOPOLOGIES.keys())

if __name__ == '__main__':
    # Unit tests
    assert isinstance(TOPOLOGIES, dict)
    assert len(TOPOLOGIES) == 20
    assert "dashboard_grid" in TOPOLOGIES
    assert isinstance(ROLE_TO_TOPOLOGY, dict)
    assert "dashboard" in ROLE_TO_TOPOLOGY
    assert get_topology("dashboard_grid") == TOPOLOGIES["dashboard_grid"]
    assert get_topology("nonexistent_topology") == TOPOLOGIES["dashboard_grid"]
    assert isinstance(list_topologies(), list)
    assert "dashboard_grid" in list_topologies()
    print("All tests passed!")