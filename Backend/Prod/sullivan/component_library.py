"""Component Library - Tier 1 cache for pre-generated components."""
import json
from pathlib import Path
from typing import Dict, List, Optional


class ComponentNotFoundError(Exception):
    """Custom exception for component not found."""
    pass


class ComponentLibrary:
    """
    Component library for accessing pre-generated UI components.

    Implements Tier 1 caching strategy: 0ms latency via JSON lookup.
    """

    def __init__(self, components_file: Optional[Path] = None):
        """
        Initialize the component library.

        Args:
            components_file: Path to JSON file. Defaults to pregenerated_components.json
        """
        if components_file is None:
            components_file = Path(__file__).parent / "pregenerated_components.json"

        self.components_file = components_file
        self.cache = self.load_components()

    def load_components(self) -> Dict:
        """
        Load pre-generated components from JSON file.

        Returns:
            Dict: Component cache (extracted from 'styles' key if present)
        """
        try:
            with open(self.components_file, "r") as f:
                data = json.load(f)
                # Handle both formats: {"styles": {...}} or direct {...}
                return data.get("styles", data)
        except FileNotFoundError:
            print(f"⚠️  Component library not found at {self.components_file}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in component library: {e}")
            return {}

    def get_component(self, style_id: str, atom_type: str, variant: str = 'primary') -> Dict:
        """
        Get a component from the cache (Tier 1 lookup).

        Args:
            style_id: Style ID (minimal, corporate, creative, etc.)
            atom_type: Component type (button, input, card, etc.)
            variant: Variant (primary, secondary, danger, etc.)

        Returns:
            Dict: Component definition with html, css_classes, accessibility, props

        Raises:
            ComponentNotFoundError: If component not found in cache
        """
        try:
            return self.cache[style_id][atom_type][variant]
        except KeyError:
            # Detailed error message
            if style_id not in self.cache:
                available = list(self.cache.keys())
                raise ComponentNotFoundError(
                    f"Style '{style_id}' not in cache. Available: {available}"
                )
            elif atom_type not in self.cache[style_id]:
                available = list(self.cache[style_id].keys())
                raise ComponentNotFoundError(
                    f"Atom '{atom_type}' not in style '{style_id}'. Available: {available}"
                )
            else:
                available = list(self.cache[style_id][atom_type].keys())
                raise ComponentNotFoundError(
                    f"Variant '{variant}' not in {style_id}/{atom_type}. Available: {available}"
                )

    def get_all_styles(self) -> List[str]:
        """Get all available style IDs."""
        return list(self.cache.keys())

    def get_all_atoms(self, style_id: str) -> List[str]:
        """Get all atom types for a style."""
        return list(self.cache.get(style_id, {}).keys())

    def get_all_variants(self, style_id: str, atom_type: str) -> List[str]:
        """Get all variants for an atom type in a style."""
        try:
            return list(self.cache[style_id][atom_type].keys())
        except KeyError:
            return []

    def render_component(self, style_id: str, atom_type: str, variant: str, props: Dict) -> str:
        """
        Render a component by injecting props into HTML template.

        Args:
            style_id: Style ID
            atom_type: Component type
            variant: Variant
            props: Props to inject (e.g., {"text": "Click me", "color": "#000"})

        Returns:
            str: Rendered HTML with props injected
        """
        component = self.get_component(style_id, atom_type, variant)
        html = component["html"]

        # Replace {{prop}} placeholders with actual values
        customizable_fields = component.get("props", {}).get("customizable_fields", [])
        for field in customizable_fields:
            if field in props:
                placeholder = f"{{{{{field}}}}}"
                html = html.replace(placeholder, str(props[field]))

        return html

    def get_css_classes(self, style_id: str, atom_type: str, variant: str) -> List[str]:
        """Get CSS classes for a component."""
        component = self.get_component(style_id, atom_type, variant)
        return component.get("css_classes", [])

    def get_accessibility_info(self, style_id: str, atom_type: str, variant: str) -> Dict:
        """Get accessibility information for a component."""
        component = self.get_component(style_id, atom_type, variant)
        return component.get("accessibility", {})

    def get_customizable_fields(self, style_id: str, atom_type: str, variant: str) -> List[str]:
        """Get list of customizable fields for a component."""
        component = self.get_component(style_id, atom_type, variant)
        return component.get("props", {}).get("customizable_fields", [])

    def is_available(self, style_id: str, atom_type: str, variant: str) -> bool:
        """Check if a component is available in the cache."""
        try:
            self.get_component(style_id, atom_type, variant)
            return True
        except ComponentNotFoundError:
            return False

    def get_cache_stats(self) -> Dict:
        """Get statistics about the component cache."""
        stats = {
            "total_styles": len(self.cache),
            "styles": {}
        }

        for style_id in self.cache:
            atoms = self.cache[style_id]
            total_variants = sum(len(variants) for variants in atoms.values())
            stats["styles"][style_id] = {
                "atom_types": len(atoms),
                "total_variants": total_variants
            }

        stats["total_components"] = sum(
            style["total_variants"] for style in stats["styles"].values()
        )

        return stats


# Convenience singleton for default usage
_default_library: Optional[ComponentLibrary] = None


def get_default_library() -> ComponentLibrary:
    """Get the default component library instance (singleton)."""
    global _default_library
    if _default_library is None:
        _default_library = ComponentLibrary()
    return _default_library


# Quick usage example
if __name__ == "__main__":
    library = ComponentLibrary()

    print("📚 Component Library Stats:")
    print(json.dumps(library.get_cache_stats(), indent=2))

    print("\n🎨 Testing component retrieval:")
    try:
        component = library.get_component("minimal", "button", "primary")
        print(f"✅ Found: {component['html'][:50]}...")

        # Test rendering
        html = library.render_component("minimal", "button", "primary", {"text": "Click me!"})
        print(f"✅ Rendered: {html}")
    except ComponentNotFoundError as e:
        print(f"❌ {e}")
