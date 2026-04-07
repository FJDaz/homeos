"""
Canvas Library — Catalogue des canevas autorisés pour Sullivan.
Définit les schémas de propriétés pour chaque composant du catalogue.
"""

from typing import Dict, Any, List

CANVAS_LIBRARY = {
    "button": {
        "description": "Un bouton d'action simple.",
        "props": {
            "label": {"type": "string", "default": "cliquer ici"},
            "variant": {"type": "string", "options": ["primary", "secondary", "ghost"], "default": "primary"},
            "size": {"type": "string", "options": ["sm", "md", "lg"], "default": "md"},
            "hasIcon": {"type": "boolean", "default": False},
            "iconName": {"type": "string", "default": "arrow-right"}
        }
    },
    "card": {
        "description": "Un conteneur de contenu avec image et texte.",
        "props": {
            "title": {"type": "string", "default": "titre de la card"},
            "description": {"type": "string", "default": "description de la card..."},
            "hasImage": {"type": "boolean", "default": True},
            "imagePosition": {"type": "string", "options": ["top", "left", "background"], "default": "top"},
            "hasBadge": {"type": "boolean", "default": False},
            "badgeText": {"type": "string", "default": "nouveau"},
            "hasCTA": {"type": "boolean", "default": True},
            "ctaLabel": {"type": "string", "default": "voir plus"},
            "columns": {"type": "integer", "options": [1, 2, 3], "default": 1}
        }
    },
    "hero": {
        "description": "Une section d'introduction impactante.",
        "props": {
            "title": {"type": "string", "default": "titre hero"},
            "subtitle": {"type": "string", "default": "sous-titre hero..."},
            "layout": {"type": "string", "options": ["centered", "split", "fullscreen"], "default": "centered"},
            "hasVideo": {"type": "boolean", "default": False},
            "hasCTA": {"type": "boolean", "default": True},
            "ctaLabel": {"type": "string", "default": "découvrir"},
            "hasSubtitle": {"type": "boolean", "default": True}
        }
    },
    "nav": {
        "description": "Une barre de navigation.",
        "props": {
            "layout": {"type": "string", "options": ["horizontal", "sidebar"], "default": "horizontal"},
            "hasLogo": {"type": "boolean", "default": True},
            "hasAuth": {"type": "boolean", "default": False},
            "linksCount": {"type": "integer", "default": 4}
        }
    },
    "form-field": {
        "description": "Un champ de formulaire (input, textarea, etc.).",
        "props": {
            "label": {"type": "string", "default": "nom"},
            "type": {"type": "string", "options": ["text", "email", "password", "textarea", "select"], "default": "text"},
            "placeholder": {"type": "string", "default": "saisissez votre texte..."},
            "hasLabel": {"type": "boolean", "default": True},
            "hasHelper": {"type": "boolean", "default": False},
            "helperText": {"type": "string", "default": "info complémentaire"}
        }
    },
    "modal": {
        "description": "Une fenêtre de dialogue surgissante.",
        "props": {
            "title": {"type": "string", "default": "titre modal"},
            "size": {"type": "string", "options": ["sm", "md", "lg", "fullscreen"], "default": "md"},
            "hasHeader": {"type": "boolean", "default": True},
            "hasFooter": {"type": "boolean", "default": True},
            "ctaLabel": {"type": "string", "default": "valider"}
        }
    },
    "badge": {
        "description": "Un petit indicateur d'état.",
        "props": {
            "label": {"type": "string", "default": "actif"},
            "variant": {"type": "string", "options": ["default", "success", "warning", "error"], "default": "default"},
            "hasIcon": {"type": "boolean", "default": False}
        }
    },
    "toast": {
        "description": "Une notification éphémère.",
        "props": {
            "message": {"type": "string", "default": "opération réussie"},
            "variant": {"type": "string", "options": ["info", "success", "warning", "error"], "default": "info"},
            "position": {"type": "string", "options": ["top", "bottom"], "default": "bottom"}
        }
    },
    "tabs": {
        "description": "Un système d'onglets pour naviguer entre contenus.",
        "props": {
            "layout": {"type": "string", "options": ["horizontal", "vertical"], "default": "horizontal"},
            "count": {"type": "integer", "options": [2, 3, 4, 5], "default": 3}
        }
    },
    "table": {
        "description": "Un tableau de données.",
        "props": {
            "title": {"type": "string", "default": "données"},
            "rows": {"type": "integer", "default": 5},
            "hasPagination": {"type": "boolean", "default": True},
            "hasSearch": {"type": "boolean", "default": False},
            "hasSort": {"type": "boolean", "default": False}
        }
    },
    "avatar": {
        "description": "Représentation visuelle d'un utilisateur.",
        "props": {
            "size": {"type": "string", "options": ["sm", "md", "lg"], "default": "md"},
            "hasStatus": {"type": "boolean", "default": False},
            "hasFallback": {"type": "boolean", "default": True}
        }
    },
    "timeline": {
        "description": "Une suite logique d'événements.",
        "props": {
            "layout": {"type": "string", "options": ["vertical", "horizontal"], "default": "vertical"},
            "count": {"type": "integer", "options": [3, 4, 5], "default": 3}
        }
    },
    "pricing-card": {
        "description": "Une card présentant un tarif.",
        "props": {
            "planName": {"type": "string", "default": "premium"},
            "price": {"type": "string", "default": "29€"},
            "hasHighlight": {"type": "boolean", "default": False},
            "hasBadge": {"type": "boolean", "default": False},
            "featuresCount": {"type": "integer", "options": [3, 4, 5, 6], "default": 4}
        }
    },
    "drawer": {
        "description": "Un panneau latéral coulissant.",
        "props": {
            "title": {"type": "string", "default": "menu"},
            "position": {"type": "string", "options": ["left", "right", "bottom"], "default": "right"},
            "hasOverlay": {"type": "boolean", "default": True}
        }
    },
    "stat-block": {
        "description": "Un bloc affichant des statistiques.",
        "props": {
            "label": {"type": "string", "default": "visiteurs"},
            "value": {"type": "string", "default": "12.4k"},
            "columns": {"type": "integer", "options": [2, 3, 4], "default": 3},
            "hasIcon": {"type": "boolean", "default": True},
            "hasTrend": {"type": "boolean", "default": True}
        }
    }
}
