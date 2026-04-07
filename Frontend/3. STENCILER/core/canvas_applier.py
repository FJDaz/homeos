import os
import re
import json
from pathlib import Path
from typing import Dict, Any, Optional

# --- CONFIG ---
CWD = Path(__file__).parent.parent.resolve()
TEMPLATES_DIR = CWD / "core" / "canvas_templates"
DEFAULT_DESIGN_PATH = CWD.parent.parent / "Frontend/1. CONSTITUTION/DESIGN.md"
PROJECTS_DIR = CWD.parent.parent / "projects"

class CanvasApplier:
    def __init__(self):
        self.templates = {}
        self._load_templates()

    def _load_templates(self):
        if not TEMPLATES_DIR.exists():
            return
        for f in TEMPLATES_DIR.glob("*.html"):
            self.templates[f.stem] = f.read_text(encoding='utf-8')

    def _parse_design_md(self, design_content: str) -> Dict[str, str]:
        """
        Extrait les tokens du DESIGN.md (format tableau Markdown).
        """
        tokens = {}
        # Chercher les lignes de tableau | --token | valeur | ... |
        # On utilise regex pour capturer le token et la valeur
        pattern = r"\|\s*(`--[^`]+`|--[^\s|]+)\s*\|\s*`?([^`|\s]+)`?\s*\|"
        matches = re.finditer(pattern, design_content)
        for m in matches:
            token = m.group(1).replace("`", "").strip()
            value = m.group(2).strip()
            tokens[token] = value
        return tokens

    def _get_project_design_tokens(self, project_id: str) -> Dict[str, str]:
        """
        Charge le DESIGN.md du projet ou le fallback constitutionnel.
        """
        tokens = {}
        design_path = PROJECTS_DIR / project_id / "DESIGN.md"
        if not design_path.exists():
            design_path = DEFAULT_DESIGN_PATH
            
        if design_path.exists():
            try:
                content = design_path.read_text(encoding='utf-8')
                tokens = self._parse_design_md(content)
            except Exception as e:
                print(f"Error parsing DESIGN.md: {e}")
        
        return tokens

    def _apply_design_system(self, html: str, tokens: Dict[str, str]) -> str:
        """
        Remplace les classes sémantiques af-* par leurs valeurs concrètes.
        """
        # --- Mapping des classes af-* vers les tokens DESIGN.md ---
        mapping = {
            "af-bg-primary": "--bg-primary",
            "af-bg-secondary": "--bg-secondary",
            "af-text-primary": "--text-primary",
            "af-text-muted": "--text-muted",
            "af-border-primary": "--separator",
            "af-nudge-bg": "--homeos-green",
            "af-nudge-text": "--homeos-green",
            "af-radius-sm": "--radius-sm",
            "af-radius": "--radius",
            "af-radius-md": "--radius-md",
            "af-radius-lg": "--radius-lg",
            "af-radius-max": "--radius-max"
        }

        # Sort by length descending to avoid partial matches (e.g. af-radius matching inside af-radius-md)
        sorted_classes = sorted(mapping.keys(), key=len, reverse=True)

        for af_class in sorted_classes:
            token = mapping[af_class]
            value = tokens.get(token)
            if value:
                # Si c'est une couleur (hex)
                if value.startswith("#"):
                    # On convertit af-bg-* en bg-[#...]
                    if "-bg" in af_class:
                        html = html.replace(af_class, f"bg-[{value}]")
                    # On convertit af-text-* en text-[#...]
                    elif "-text" in af_class:
                        html = html.replace(af_class, f"text-[{value}]")
                    # On convertit af-border-* en border-[{value}]
                    elif "-border" in af_class:
                        html = html.replace(af_class, f"border-[{value}]")
                # Si c'est un radius (px)
                elif "radius" in token:
                    html = html.replace(af_class, f"rounded-[{value}]")
            else:
                # Fallbacks neutres si token non défini
                fallbacks = {
                    "af-bg-primary": "bg-[#f7f6f2]",
                    "af-bg-secondary": "bg-[#efefeb]",
                    "af-text-primary": "text-[#3d3d3c]",
                    "af-text-muted": "text-[#9a9a98]",
                    "af-border-primary": "border-[#e5e5e5]",
                    "af-nudge-bg": "bg-[#8cc63f]",
                    "af-nudge-text": "text-[#8cc63f]",
                    "af-radius": "rounded-[4px]",
                    "af-radius-sm": "rounded-[2px]",
                    "af-radius-md": "rounded-[6px]",
                    "af-radius-lg": "rounded-[12px]",
                    "af-radius-max": "rounded-[20px]"
                }
                if af_class in fallbacks:
                    html = html.replace(af_class, fallbacks[af_class])

        return html

    def instanciate(self, canvas_name: str, props: Dict[str, Any], project_id: str = "active") -> str:
        """
        Instancie un canevas avec ses props et le design du projet.
        """
        if project_id == "active":
            from bkd_service import get_active_project_path
            p_path = get_active_project_path()
            project_id = p_path.name if p_path else "default"

        template = self.templates.get(canvas_name)
        if not template:
            return f"<!-- Error: Canvas '{canvas_name}' not found -->"

        # 1. Gestion des blocs conditionnels [[if prop]] ... [[endif]]
        # (Supporte uniquement les booleens simples pour l'instant)
        def _handle_ifs(match):
            prop_name = match.group(1).strip()
            content = match.group(2)
            if props.get(prop_name, False):
                return content
            return ""
        
        template = re.sub(r"\[\[if\s+([^\]]+)\]\](.*?)\[\[endif\]\]", _handle_ifs, template, flags=re.DOTALL)

        # 2. Remplacements de base {{prop}}
        # Ajout automatique de slug pour les labels si besoin
        if "label" in props:
            props["label_slug"] = re.sub(r'[^\w\s-]', '', str(props["label"]).lower()).replace(" ", "-")
        
        # Ajout d'un ID unique si absent
        if "id" not in props:
            import random
            props["id"] = f"{int(random.random()*1000)}"

        # Derived class mapping (props → Tailwind classes)
        if canvas_name == "button":
            size_map = {"sm": "px-2 py-1 text-[10px]", "md": "px-4 py-2 text-xs", "lg": "px-6 py-3 text-sm"}
            variant_map = {
                "primary": "af-nudge-bg border-transparent",
                "secondary": "bg-[#efefeb] af-border-primary",
                "ghost": "bg-transparent border-current"
            }
            props["size_class"] = size_map.get(props.get("size", "md"), size_map["md"])
            props["variant_class"] = variant_map.get(props.get("variant", "primary"), variant_map["primary"])

        # Remplacements
        for key, value in props.items():
            template = template.replace(f"{{{{{key}}}}}", str(value))

        # 3. Application du Design System
        tokens = self._get_project_design_tokens(project_id)
        final_html = self._apply_design_system(template, tokens)

        return final_html

# Singleton
applier = CanvasApplier()
