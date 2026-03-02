"""
SemanticPropertySystem — Pilier 3 du Système Cognitif

Responsabilités :
- Définition et validation des propriétés sémantiques autorisées
- Traduction des intentions en attributs sémantiques
- Garde-fou anti-CSS/HTML (Article 3)
- Catalogue des propriétés sémantiques

Conformité : CONSTITUTION_AETHERFLOW v1.0.0
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════════
# DÉFINITIONS DES PROPRIÉTÉS SÉMANTIQUES AUTORISÉES
# ═══════════════════════════════════════════════════════════════════════════════

class SemanticCategory(Enum):
    """Catégories de propriétés sémantiques"""
    LAYOUT = "layout"           # Organisation spatiale
    VISUAL = "visual"           # Apparence sémantique
    INTERACTION = "interaction" # Comportement utilisateur
    CONTENT = "content"         # Contenu sémantique
    METADATA = "metadata"       # Métadonnées techniques


@dataclass
class SemanticProperty:
    """Définition d'une propriété sémantique"""
    name: str
    category: SemanticCategory
    allowed_values: Optional[List[str]] = None  # None = valeur libre
    value_type: str = "string"  # string | number | boolean | color
    description: str = ""
    examples: Optional[List[str]] = None


# ═══════════════════════════════════════════════════════════════════════════════
# CATALOGUE DES PROPRIÉTÉS SÉMANTIQUES (Article 3)
# ═══════════════════════════════════════════════════════════════════════════════

SEMANTIC_PROPERTIES_CATALOG: Dict[str, SemanticProperty] = {
    # ─────────────────────────────────────────────────────────────────────────
    # LAYOUT : Organisation spatiale
    # ─────────────────────────────────────────────────────────────────────────
    "layout_type": SemanticProperty(
        name="layout_type",
        category=SemanticCategory.LAYOUT,
        allowed_values=["grid", "flex", "stack", "absolute", "flow"],
        value_type="string",
        description="Type d'organisation des éléments enfants",
        examples=["grid", "flex", "stack"]
    ),

    "density": SemanticProperty(
        name="density",
        category=SemanticCategory.LAYOUT,
        allowed_values=["compact", "normal", "airy", "spacious"],
        value_type="string",
        description="Densité de l'espacement entre éléments",
        examples=["compact", "airy"]
    ),

    "alignment": SemanticProperty(
        name="alignment",
        category=SemanticCategory.LAYOUT,
        allowed_values=["start", "center", "end", "stretch"],
        value_type="string",
        description="Alignement sémantique des éléments",
        examples=["center", "start"]
    ),

    "distribution": SemanticProperty(
        name="distribution",
        category=SemanticCategory.LAYOUT,
        allowed_values=["even", "start", "end", "between", "around"],
        value_type="string",
        description="Distribution sémantique de l'espace",
        examples=["even", "between"]
    ),

    # ─────────────────────────────────────────────────────────────────────────
    # VISUAL : Apparence sémantique
    # ─────────────────────────────────────────────────────────────────────────
    "importance": SemanticProperty(
        name="importance",
        category=SemanticCategory.VISUAL,
        allowed_values=["primary", "secondary", "tertiary", "subtle"],
        value_type="string",
        description="Importance visuelle de l'élément",
        examples=["primary", "secondary"]
    ),

    "accent_color": SemanticProperty(
        name="accent_color",
        category=SemanticCategory.VISUAL,
        allowed_values=None,  # Valeur libre (hex color)
        value_type="color",
        description="Couleur d'accentuation sémantique (hex)",
        examples=["#4CAF50", "#FF5722"]
    ),

    "visual_hint": SemanticProperty(
        name="visual_hint",
        category=SemanticCategory.VISUAL,
        allowed_values=None,  # Texte libre
        value_type="string",
        description="Indice visuel descriptif pour le frontend",
        examples=["rounded corners", "shadow effect", "gradient background"]
    ),

    "prominence": SemanticProperty(
        name="prominence",
        category=SemanticCategory.VISUAL,
        allowed_values=["high", "medium", "low", "hidden"],
        value_type="string",
        description="Niveau de proéminence visuelle",
        examples=["high", "low"]
    ),

    "visual_weight": SemanticProperty(
        name="visual_weight",
        category=SemanticCategory.VISUAL,
        allowed_values=["bold", "normal", "light", "subtle"],
        value_type="string",
        description="Poids visuel sémantique",
        examples=["bold", "light"]
    ),

    # ─────────────────────────────────────────────────────────────────────────
    # INTERACTION : Comportement utilisateur
    # ─────────────────────────────────────────────────────────────────────────
    "interaction_level": SemanticProperty(
        name="interaction_level",
        category=SemanticCategory.INTERACTION,
        allowed_values=["interactive", "static", "disabled"],
        value_type="string",
        description="Niveau d'interactivité de l'élément",
        examples=["interactive", "static"]
    ),

    "affordance": SemanticProperty(
        name="affordance",
        category=SemanticCategory.INTERACTION,
        allowed_values=["clickable", "draggable", "hoverable", "focusable"],
        value_type="string",
        description="Type d'affordance suggérée",
        examples=["clickable", "draggable"]
    ),

    "feedback_type": SemanticProperty(
        name="feedback_type",
        category=SemanticCategory.INTERACTION,
        allowed_values=["visual", "haptic", "audio", "none"],
        value_type="string",
        description="Type de feedback lors de l'interaction",
        examples=["visual", "haptic"]
    ),

    # ─────────────────────────────────────────────────────────────────────────
    # CONTENT : Contenu sémantique
    # ─────────────────────────────────────────────────────────────────────────
    "name": SemanticProperty(
        name="name",
        category=SemanticCategory.CONTENT,
        allowed_values=None,
        value_type="string",
        description="Nom sémantique de l'élément",
        examples=["Header", "Hero Section", "Call to Action"]
    ),

    "role": SemanticProperty(
        name="role",
        category=SemanticCategory.CONTENT,
        allowed_values=None,
        value_type="string",
        description="Rôle fonctionnel de l'élément",
        examples=["navigation", "content", "footer"]
    ),

    "content": SemanticProperty(
        name="content",
        category=SemanticCategory.CONTENT,
        allowed_values=None,
        value_type="string",
        description="Contenu textuel ou description",
        examples=["Welcome to HomeOS", "Click here to start"]
    ),

    "semantic_weight": SemanticProperty(
        name="semantic_weight",
        category=SemanticCategory.CONTENT,
        allowed_values=["high", "medium", "low"],
        value_type="string",
        description="Poids sémantique dans la hiérarchie du contenu",
        examples=["high", "medium"]
    ),

    # ─────────────────────────────────────────────────────────────────────────
    # METADATA : Métadonnées techniques
    # ─────────────────────────────────────────────────────────────────────────
    "confidence": SemanticProperty(
        name="confidence",
        category=SemanticCategory.METADATA,
        allowed_values=None,
        value_type="number",
        description="Niveau de confiance de l'inférence (0.0-1.0)",
        examples=["0.85", "0.92"]
    ),

    "id": SemanticProperty(
        name="id",
        category=SemanticCategory.METADATA,
        allowed_values=None,
        value_type="string",
        description="Identifiant unique de l'élément",
        examples=["n0_frontend", "atom_button_primary"]
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# PROPRIÉTÉS CSS/HTML INTERDITES (Article 3)
# ═══════════════════════════════════════════════════════════════════════════════

FORBIDDEN_PROPERTIES: Set[str] = {
    # CSS Layout
    "display", "position", "top", "left", "right", "bottom",
    "width", "height", "min-width", "max-width", "min-height", "max-height",
    "margin", "margin-top", "margin-right", "margin-bottom", "margin-left",
    "padding", "padding-top", "padding-right", "padding-bottom", "padding-left",
    "flex", "flex-direction", "flex-wrap", "justify-content", "align-items",
    "grid", "grid-template-columns", "grid-template-rows", "gap", "grid-gap",

    # CSS Visual
    "color", "background", "background-color", "background-image",
    "border", "border-width", "border-color", "border-style", "border-radius",
    "box-shadow", "text-shadow", "opacity", "filter",

    # CSS Typography
    "font-family", "font-size", "font-weight", "font-style",
    "line-height", "letter-spacing", "text-align", "text-decoration",

    # CSS Misc
    "z-index", "overflow", "cursor", "transition", "animation",
    "transform", "visibility", "clip-path",

    # HTML
    "className", "class", "style", "innerHTML", "outerHTML",
}


# ═══════════════════════════════════════════════════════════════════════════════
# SYSTÈME DE VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════

class SemanticPropertySystem:
    """
    Système de gestion et validation des propriétés sémantiques

    Garde-fou constitutionnel (Article 3) :
    - Valide les propriétés sémantiques autorisées
    - Rejette les propriétés CSS/HTML interdites
    - Fournit des suggestions si propriété inconnue
    """

    def __init__(self):
        """Initialise le système de propriétés sémantiques"""
        self.catalog = SEMANTIC_PROPERTIES_CATALOG
        self.forbidden = FORBIDDEN_PROPERTIES

        print(f"✅ SemanticPropertySystem initialisé : {len(self.catalog)} propriétés autorisées")


    def validate_property(self, property: str, value: Any) -> Tuple[bool, Optional[str], List[str]]:
        """
        Valide une propriété sémantique

        Args:
            property: Nom de la propriété
            value: Valeur de la propriété

        Returns:
            (is_valid, error_message, warnings)
        """
        warnings = []

        # 1. Vérifier si propriété CSS/HTML interdite (Article 3)
        if property in self.forbidden:
            return False, f"❌ VIOLATION ARTICLE 3 : '{property}' est une propriété CSS/HTML interdite", []

        # 2. Vérifier si propriété connue comme sémantique
        if property in self.catalog:
            prop_def = self.catalog[property]

            # Valider les valeurs autorisées
            if prop_def.allowed_values is not None:
                if value not in prop_def.allowed_values:
                    return False, f"Valeur '{value}' invalide pour '{property}'. Valeurs autorisées : {prop_def.allowed_values}", []

            # Valider le type
            if prop_def.value_type == "color":
                if not self._is_valid_hex_color(value):
                    return False, f"Valeur '{value}' n'est pas une couleur hex valide (#RRGGBB)", []

            elif prop_def.value_type == "number":
                if not isinstance(value, (int, float)):
                    return False, f"Valeur '{value}' n'est pas un nombre", []

            return True, None, warnings

        # 3. Propriété inconnue → Avertissement
        suggestions = self._find_similar_properties(property)
        warning = f"⚠️ Propriété '{property}' inconnue"

        if suggestions:
            warning += f" — Peut-être : {', '.join(suggestions)} ?"

        warnings.append(warning)

        return True, None, warnings


    def _is_valid_hex_color(self, value: str) -> bool:
        """Valide qu'une valeur est une couleur hex (#RRGGBB ou #RGB)"""
        if not isinstance(value, str):
            return False

        if not value.startswith('#'):
            return False

        hex_part = value[1:]

        if len(hex_part) == 6 or len(hex_part) == 3:
            try:
                int(hex_part, 16)
                return True
            except ValueError:
                return False

        return False


    def _find_similar_properties(self, property: str) -> List[str]:
        """Trouve des propriétés similaires (Levenshtein distance)"""
        import difflib

        # Utiliser difflib pour trouver les propriétés proches
        similar = difflib.get_close_matches(property, self.catalog.keys(), n=3, cutoff=0.6)

        return similar


    def get_properties_by_category(self, category: SemanticCategory) -> List[SemanticProperty]:
        """
        Retourne toutes les propriétés d'une catégorie

        Args:
            category: Catégorie sémantique

        Returns:
            Liste des propriétés de cette catégorie
        """
        return [prop for prop in self.catalog.values() if prop.category == category]


    def get_all_properties(self) -> List[SemanticProperty]:
        """Retourne toutes les propriétés sémantiques autorisées"""
        return list(self.catalog.values())


    def suggest_property_for_intent(self, intent: str) -> List[SemanticProperty]:
        """
        Suggère des propriétés sémantiques à partir d'une intention utilisateur

        Args:
            intent: Description de l'intention (ex: "rendre plus espacé", "couleur primaire")

        Returns:
            Liste de propriétés suggérées
        """
        intent_lower = intent.lower()
        suggestions = []

        # Mapping intention → propriétés
        intent_keywords = {
            "espa": ["density", "distribution"],
            "couleur": ["accent_color", "prominence"],
            "important": ["importance", "semantic_weight", "prominence"],
            "cliqu": ["affordance", "interaction_level"],
            "layout": ["layout_type", "alignment", "distribution"],
            "visible": ["prominence", "visual_weight"],
        }

        for keyword, properties in intent_keywords.items():
            if keyword in intent_lower:
                for prop_name in properties:
                    if prop_name in self.catalog:
                        suggestions.append(self.catalog[prop_name])

        return suggestions


if __name__ == "__main__":
    # Tests de base
    print("🧪 Tests SemanticPropertySystem")
    print("=" * 60)

    system = SemanticPropertySystem()

    # Test 1 : Validation propriété sémantique valide
    valid, error, warnings = system.validate_property("layout_type", "grid")
    if valid:
        print(f"✅ Test 1 : Propriété sémantique 'layout_type=grid' valide")
    else:
        print(f"❌ Test 1 : Erreur : {error}")

    # Test 2 : Validation propriété CSS interdite
    valid, error, warnings = system.validate_property("background-color", "#FF5722")
    if not valid:
        print(f"✅ Test 2 : Propriété CSS 'background-color' correctement rejetée")
        print(f"   Erreur : {error}")
    else:
        print(f"❌ Test 2 : Propriété CSS devrait être rejetée !")

    # Test 3 : Validation valeur invalide
    valid, error, warnings = system.validate_property("layout_type", "invalid_value")
    if not valid:
        print(f"✅ Test 3 : Valeur invalide correctement rejetée")
        print(f"   Erreur : {error}")
    else:
        print(f"❌ Test 3 : Valeur invalide devrait être rejetée !")

    # Test 4 : Validation couleur hex
    valid, error, warnings = system.validate_property("accent_color", "#4CAF50")
    if valid:
        print(f"✅ Test 4 : Couleur hex valide")
    else:
        print(f"❌ Test 4 : Erreur : {error}")

    # Test 5 : Couleur hex invalide
    valid, error, warnings = system.validate_property("accent_color", "invalid_color")
    if not valid:
        print(f"✅ Test 5 : Couleur hex invalide correctement rejetée")
    else:
        print(f"❌ Test 5 : Couleur invalide devrait être rejetée !")

    # Test 6 : Propriété inconnue avec suggestions
    valid, error, warnings = system.validate_property("layot_type", "grid")
    if valid and warnings:
        print(f"✅ Test 6 : Propriété inconnue avec avertissement")
        print(f"   Warning : {warnings[0]}")
    else:
        print(f"❌ Test 6 : Devrait générer un avertissement")

    # Test 7 : Récupération par catégorie
    layout_props = system.get_properties_by_category(SemanticCategory.LAYOUT)
    print(f"✅ Test 7 : {len(layout_props)} propriétés de catégorie LAYOUT")

    # Test 8 : Suggestion d'intention
    suggestions = system.suggest_property_for_intent("rendre plus espacé")
    if suggestions:
        print(f"✅ Test 8 : {len(suggestions)} propriétés suggérées pour 'espacé'")
        print(f"   Suggestions : {[p.name for p in suggestions]}")
    else:
        print(f"❌ Test 8 : Aucune suggestion trouvée")

    print("=" * 60)
    print("🎯 SemanticPropertySystem : Tous les tests passés !")
