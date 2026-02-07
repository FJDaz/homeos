"""Visual inference: endpoint → visual hint + DaisyUI component."""
from __future__ import annotations

import re
from typing import Dict, Any, Optional, Tuple
from loguru import logger


# Mapping heuristique: (method, path_patterns) → visual metadata
ENDPOINT_TO_VISUAL: Dict[Tuple[str, Tuple[str, ...]], Dict[str, str]] = {
    # GET + liste → table
    ("GET", ("list", "all", "users", "items", "products", "orders", "records", "entities")): {
        "visual_hint": "table",
        "visual_category": "data_display",
        "inferred_daisy_component": "daisy_table",
        "wireframe_sketch": "Header row with columns + scrollable data rows + pagination footer"
    },
    # POST + create → form
    ("POST", ("create", "new", "add", "register", "signup", "submit")): {
        "visual_hint": "form",
        "visual_category": "data_input",
        "inferred_daisy_component": "daisy_fieldset",
        "wireframe_sketch": "Grouped input fields with labels + submit button + validation messages"
    },
    # GET + detail/id → card
    ("GET", ("detail", "profile", "info", "view", "show", "get", "{id}")): {
        "visual_hint": "card",
        "visual_category": "data_display",
        "inferred_daisy_component": "daisy_card",
        "wireframe_sketch": "Header with title + avatar/icon + body content + action buttons footer"
    },
    # DELETE → modal confirmation
    ("DELETE", ("delete", "remove", "destroy", "purge")): {
        "visual_hint": "modal",
        "visual_category": "actions",
        "inferred_daisy_component": "daisy_modal",
        "wireframe_sketch": "Overlay backdrop + centered dialog box + warning icon + confirm/cancel buttons"
    },
    # GET + status/health → stat
    ("GET", ("health", "status", "metrics", "stats", "analytics", "dashboard")): {
        "visual_hint": "stat",
        "visual_category": "data_display",
        "inferred_daisy_component": "daisy_stat",
        "wireframe_sketch": "Grid of stat cards with large numbers + trend indicators + sparklines"
    },
    # PUT/PATCH → form (edition)
    ("PUT", ("update", "edit", "modify", "change")): {
        "visual_hint": "form",
        "visual_category": "data_input",
        "inferred_daisy_component": "daisy_fieldset",
        "wireframe_sketch": "Pre-filled input fields + save/cancel buttons + inline validation"
    },
    ("PATCH", ("update", "edit", "modify", "change", "partial")): {
        "visual_hint": "form",
        "visual_category": "data_input",
        "inferred_daisy_component": "daisy_fieldset",
        "wireframe_sketch": "Pre-filled input fields + save/cancel buttons + inline validation"
    },
    # Search/filter → filter component
    ("GET", ("search", "filter", "query", "find", "lookup")): {
        "visual_hint": "filter",
        "visual_category": "data_input",
        "inferred_daisy_component": "daisy_filter",
        "wireframe_sketch": "Search input + filter chips + sort dropdown + result count badge"
    },
    # Upload files → file input
    ("POST", ("upload", "import", "bulk", "batch")): {
        "visual_hint": "upload",
        "visual_category": "data_input",
        "inferred_daisy_component": "daisy_file_input",
        "wireframe_sketch": "Drop zone with icon + file list + progress bars + upload button"
    },
    # Auth/login → form compact
    ("POST", ("login", "auth", "authenticate", "token", "oauth")): {
        "visual_hint": "form",
        "visual_category": "data_input",
        "inferred_daisy_component": "daisy_input",
        "wireframe_sketch": "Email/password inputs + remember checkbox + submit button + forgot link"
    },
    # Logout → button
    ("POST", ("logout", "signout")): {
        "visual_hint": "button",
        "visual_category": "actions",
        "inferred_daisy_component": "daisy_button",
        "wireframe_sketch": "Destructive action button with confirmation tooltip"
    },
    # Settings/preferences → form with tabs
    ("GET", ("settings", "config", "preferences", "options")): {
        "visual_hint": "tabs",
        "visual_category": "navigation",
        "inferred_daisy_component": "daisy_tab",
        "wireframe_sketch": "Horizontal tab bar + content panels with form fields per section"
    },
    ("PUT", ("settings", "config", "preferences", "options")): {
        "visual_hint": "tabs",
        "visual_category": "navigation",
        "inferred_daisy_component": "daisy_tab",
        "wireframe_sketch": "Horizontal tab bar + content panels with form fields per section"
    },
}


def _match_patterns(path: str, method: str, patterns: Tuple[str, ...]) -> bool:
    """
    Vérifie si le path/method match les patterns donnés.
    
    Args:
        path: API path (ex: /api/users/123)
        method: HTTP method (ex: GET)
        patterns: Tuple de patterns à matcher
        
    Returns:
        True si au moins un pattern match
    """
    path_lower = path.lower()
    method_upper = method.upper()
    
    for pattern in patterns:
        # Pattern {id} → recherche de paramètre dynamique
        if pattern == "{id}":
            if re.search(r'\{[^}]+\}', path) or re.search(r'/\d+(/|$)', path):
                return True
        # Pattern standard
        elif pattern in path_lower:
            return True
    
    return False


def infer_visual_hint(method: str, path: str, summary: str = "") -> Dict[str, str]:
    """
    Infère les métadonnées visuelles depuis un endpoint.
    
    Args:
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        path: API path
        summary: Endpoint summary/description (optionnel)
        
    Returns:
        Dict avec visual_hint, visual_category, inferred_daisy_component, wireframe_sketch
    """
    method_upper = method.upper()
    path_lower = path.lower()
    summary_lower = summary.lower() if summary else ""
    
    # 1. Chercher match exact dans ENDPOINT_TO_VISUAL
    for (m, patterns), metadata in ENDPOINT_TO_VISUAL.items():
        if m == method_upper and _match_patterns(path, method, patterns):
            logger.debug(f"Visual inference (exact): {method} {path} → {metadata['visual_hint']}")
            return metadata.copy()
    
    # 2. Heuristiques secondaires basées sur méthode seule
    if method_upper == "GET":
        # GET sur collection (sans ID) → liste/table
        if "{" not in path and not any(ext in path_lower for ext in [".json", ".xml", ".csv"]):
            return {
                "visual_hint": "list",
                "visual_category": "data_display",
                "inferred_daisy_component": "daisy_list",
                "wireframe_sketch": "Vertical list with item titles + descriptions + action icons"
            }
        # GET avec ID ou paramètre → detail/card
        else:
            return {
                "visual_hint": "detail",
                "visual_category": "data_display",
                "inferred_daisy_component": "daisy_card",
                "wireframe_sketch": "Header with title + avatar/icon + body content + action buttons"
            }
    
    elif method_upper == "POST":
        # POST par défaut → form
        return {
            "visual_hint": "form",
            "visual_category": "data_input",
            "inferred_daisy_component": "daisy_fieldset",
            "wireframe_sketch": "Grouped input fields with labels + submit button + validation messages"
        }
    
    elif method_upper in ("PUT", "PATCH"):
        # PUT/PATCH par défaut → form (edition)
        return {
            "visual_hint": "form",
            "visual_category": "data_input",
            "inferred_daisy_component": "daisy_fieldset",
            "wireframe_sketch": "Pre-filled input fields + save/cancel buttons + inline validation"
        }
    
    elif method_upper == "DELETE":
        # DELETE par défaut → modal
        return {
            "visual_hint": "modal",
            "visual_category": "actions",
            "inferred_daisy_component": "daisy_modal",
            "wireframe_sketch": "Overlay backdrop + centered dialog + warning message + confirm/cancel buttons"
        }
    
    # 3. Fallback générique
    return {
        "visual_hint": "generic",
        "visual_category": "general",
        "inferred_daisy_component": "daisy_card",  # Card est le plus versatile
        "wireframe_sketch": "Container with header, body content, and optional footer actions"
    }


def enrich_endpoint_with_visual(endpoint: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrichit un endpoint avec les métadonnées visuelles.
    
    Args:
        endpoint: Dict avec method, path, summary, ...
        
    Returns:
        Endpoint enrichi avec visual_hint, visual_category, inferred_daisy_component, wireframe_sketch
    """
    method = endpoint.get("method", "GET")
    path = endpoint.get("path", "")
    summary = endpoint.get("summary", "")
    
    visual_meta = infer_visual_hint(method, path, summary)
    
    return {
        **endpoint,
        **visual_meta
    }


def get_daisy_component_list() -> list[str]:
    """
    Retourne la liste des composants DaisyUI disponibles (pour validation).
    
    Returns:
        Liste des IDs de composants daisy_*
    """
    return [
        "daisy_button", "daisy_dropdown", "daisy_modal", "daisy_swap",
        "daisy_theme_controller", "daisy_accordion", "daisy_avatar",
        "daisy_badge", "daisy_card", "daisy_carousel", "daisy_chat_bubble",
        "daisy_collapse", "daisy_kbd", "daisy_list", "daisy_stat",
        "daisy_status", "daisy_table", "daisy_timeline", "daisy_breadcrumbs",
        "daisy_menu", "daisy_navbar", "daisy_pagination", "daisy_steps",
        "daisy_tab", "daisy_alert", "daisy_loading", "daisy_progress",
        "daisy_radial_progress", "daisy_skeleton", "daisy_toast",
        "daisy_tooltip", "daisy_checkbox", "daisy_fieldset", "daisy_file_input",
        "daisy_filter", "daisy_label", "daisy_radio", "daisy_range",
        "daisy_rating", "daisy_select", "daisy_input", "daisy_textarea",
        "daisy_toggle", "daisy_validator", "daisy_divider", "daisy_drawer",
        "daisy_footer", "daisy_hero", "daisy_indicator", "daisy_join",
        "daisy_mask", "daisy_stack", "daisy_fab", "daisy_countdown",
        "daisy_diff", "daisy_dock", "daisy_link"
    ]


def validate_inferred_component(component_id: str) -> bool:
    """
    Valide qu'un composant inféré existe dans la librairie.
    
    Args:
        component_id: ID du composant (ex: daisy_table)
        
    Returns:
        True si le composant existe
    """
    available = get_daisy_component_list()
    return component_id in available
