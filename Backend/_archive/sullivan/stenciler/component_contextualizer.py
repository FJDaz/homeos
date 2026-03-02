"""
ComponentContextualizer — Pilier 5 du Système Cognitif

Responsabilités :
- Enrichissement contextuel des composants avec Elite Library
- Recherche de composants Tier 1 par similarité sémantique
- Stratégie hybride Tier 1/2/3 (cache → adaptation → génération)
- Métadonnées de contexte pour le frontend

Conformité : CONSTITUTION_AETHERFLOW v1.0.0
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class ComponentContext:
    """Contexte enrichi d'un composant"""
    path: str
    name: str
    level: int  # 0=Corps, 1=Organe, 2=Cell, 3=Atomset
    tier: int  # 1=cache, 2=adaptation, 3=generation
    elite_component: Optional[Dict] = None  # Composant Tier 1 si trouvé
    semantic_hints: Optional[Dict] = None  # Indices sémantiques pour rendu
    ancestors: Optional[List[str]] = None  # Chemin ancestral
    context_metadata: Optional[Dict] = None  # Métadonnées additionnelles


@dataclass
class TierStrategy:
    """Stratégie de résolution hybride"""
    recommended_tier: int
    tier_1_match: Optional[Dict] = None  # Composant Elite Library
    tier_2_template: Optional[str] = None  # Template à adapter
    tier_3_spec: Optional[Dict] = None  # Spec pour génération
    confidence: float = 0.0


class ComponentContextualizer:
    """
    Contextualiseur de composants avec stratégie hybride

    Architecture :
    - Tier 1 : Cache (Elite Library) → 0ms, réutilisation directe
    - Tier 2 : Adaptation (templates) → <100ms, modification template
    - Tier 3 : Génération (from scratch) → 1-5s, création complète

    Sources :
    - Elite Library : Frontend/2. GENOME/elite_components/ (65 composants)
    - Pregenerated : Frontend/2. GENOME/pregenerated_components.json
    """

    def __init__(
        self,
        elite_library_path: str = "Frontend/2. GENOME/elite_components",
        pregenerated_path: str = "Frontend/2. GENOME/pregenerated_components.json"
    ):
        """
        Initialise le contextualiseur

        Args:
            elite_library_path: Chemin vers Elite Library
            pregenerated_path: Chemin vers composants pré-générés
        """
        self.elite_library_path = Path(elite_library_path)
        self.pregenerated_path = Path(pregenerated_path)

        # Charger l'Elite Library
        self.elite_library = self._load_elite_library()

        # Charger les composants pré-générés
        self.pregenerated = self._load_pregenerated()

        # Index par niveau
        self.index_by_level = {
            "Corps": {},
            "Organe": {},
            "Cellule": {},
            "Atome": {}
        }

        self._build_index()

        print(f"✅ ComponentContextualizer initialisé")
        print(f"   Elite Library : {len(self.elite_library)} composants")
        print(f"   Pregenerated : {len(self.pregenerated.get('styles', {}))} styles")


    def _load_elite_library(self) -> Dict[str, Dict]:
        """Charge tous les composants de l'Elite Library"""
        library = {}

        if not self.elite_library_path.exists():
            print(f"⚠️ Elite Library non trouvée : {self.elite_library_path}")
            return library

        for json_file in self.elite_library_path.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    component = json.load(f)

                component_id = json_file.stem  # "Corps_Frontend", "Atome_Bouton_Analyser"
                library[component_id] = component

            except json.JSONDecodeError as e:
                print(f"⚠️ Erreur lecture {json_file}: {e}")

        return library


    def _load_pregenerated(self) -> Dict:
        """Charge les composants pré-générés"""
        if not self.pregenerated_path.exists():
            print(f"⚠️ Pregenerated non trouvé : {self.pregenerated_path}")
            return {}

        try:
            with open(self.pregenerated_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"⚠️ Erreur lecture pregenerated : {e}")
            return {}


    def _build_index(self):
        """Construit l'index par niveau (Corps, Organe, Cellule, Atome)"""
        for component_id, component_data in self.elite_library.items():
            # Détecter le niveau depuis le nom du fichier
            if component_id.startswith("Corps_"):
                self.index_by_level["Corps"][component_id] = component_data
            elif component_id.startswith("Organe_"):
                self.index_by_level["Organe"][component_id] = component_data
            elif component_id.startswith("Cellule_"):
                self.index_by_level["Cellule"][component_id] = component_data
            elif component_id.startswith("Atome_"):
                self.index_by_level["Atome"][component_id] = component_data


    def contextualize_component(
        self,
        path: str,
        node_data: Dict,
        level: int
    ) -> ComponentContext:
        """
        Enrichit un composant avec son contexte

        Args:
            path: Chemin format "n0[0].n1_sections[2]"
            node_data: Données du nœud dans le Genome
            level: Niveau hiérarchique (0=Corps, 1=Organe, 2=Cell, 3=Atomset)

        Returns:
            ComponentContext enrichi
        """
        name = node_data.get('name', 'Unknown')

        # Rechercher un composant Tier 1 (Elite Library)
        tier_strategy = self.resolve_tier_strategy(name, level)

        # Extraire indices sémantiques
        semantic_hints = self._extract_semantic_hints(node_data)

        # Créer le contexte
        context = ComponentContext(
            path=path,
            name=name,
            level=level,
            tier=tier_strategy.recommended_tier,
            elite_component=tier_strategy.tier_1_match,
            semantic_hints=semantic_hints,
            context_metadata={
                'tier_strategy': tier_strategy,
                'confidence': tier_strategy.confidence
            }
        )

        return context


    def resolve_tier_strategy(self, component_name: str, level: int) -> TierStrategy:
        """
        Résout la stratégie hybride Tier 1/2/3

        Args:
            component_name: Nom du composant
            level: Niveau (0=Corps, 1=Organe, 2=Cell, 3=Atomset)

        Returns:
            TierStrategy avec recommandation
        """
        level_names = ["Corps", "Organe", "Cellule", "Atome"]
        level_name = level_names[level] if level < len(level_names) else "Unknown"

        # 1. Chercher dans Elite Library (Tier 1)
        tier_1_match = self._search_elite_library(component_name, level_name)

        if tier_1_match:
            return TierStrategy(
                recommended_tier=1,
                tier_1_match=tier_1_match,
                confidence=0.95
            )

        # 2. Chercher un template adaptable (Tier 2)
        tier_2_template = self._search_pregenerated_template(component_name, level_name)

        if tier_2_template:
            return TierStrategy(
                recommended_tier=2,
                tier_2_template=tier_2_template,
                confidence=0.75
            )

        # 3. Génération from scratch (Tier 3)
        return TierStrategy(
            recommended_tier=3,
            tier_3_spec={
                'component_name': component_name,
                'level': level_name,
                'generation_required': True
            },
            confidence=0.5
        )


    def _search_elite_library(self, component_name: str, level_name: str) -> Optional[Dict]:
        """
        Recherche un composant dans l'Elite Library

        Stratégie :
        1. Exact match par nom
        2. Fuzzy match par similarité

        Args:
            component_name: Nom du composant
            level_name: Niveau (Corps, Organe, Cellule, Atome)

        Returns:
            Composant trouvé ou None
        """
        if level_name not in self.index_by_level:
            return None

        level_components = self.index_by_level[level_name]

        # 1. Exact match
        for component_id, component_data in level_components.items():
            if component_data.get('name', '').lower() == component_name.lower():
                return component_data

        # 2. Fuzzy match (similarité nom)
        import difflib

        component_names = [c.get('name', '') for c in level_components.values()]
        similar = difflib.get_close_matches(component_name, component_names, n=1, cutoff=0.7)

        if similar:
            # Retrouver le composant correspondant
            for component_id, component_data in level_components.items():
                if component_data.get('name', '') == similar[0]:
                    return component_data

        return None


    def _search_pregenerated_template(self, component_name: str, level_name: str) -> Optional[str]:
        """
        Recherche un template pré-généré adaptable

        Args:
            component_name: Nom du composant
            level_name: Niveau

        Returns:
            Clé du template ou None
        """
        if not self.pregenerated or 'styles' not in self.pregenerated:
            return None

        # Mapping nom composant → type de template
        template_mapping = {
            "button": "button",
            "input": "input",
            "card": "card",
            "navbar": "navbar",
            "modal": "modal",
            "form": "form"
        }

        component_lower = component_name.lower()

        for keyword, template_type in template_mapping.items():
            if keyword in component_lower:
                # Vérifier si le template existe dans pregenerated
                for style_name, style_data in self.pregenerated['styles'].items():
                    if template_type in style_data:
                        return f"{style_name}.{template_type}"

        return None


    def _extract_semantic_hints(self, node_data: Dict) -> Dict:
        """
        Extrait les indices sémantiques d'un nœud

        Args:
            node_data: Données du nœud

        Returns:
            Dict d'indices sémantiques
        """
        hints = {}

        # Propriétés sémantiques connues
        semantic_properties = [
            'visual_hint', 'role', 'description', 'layout_type',
            'density', 'importance', 'accent_color', 'confidence'
        ]

        for prop in semantic_properties:
            if prop in node_data:
                hints[prop] = node_data[prop]

        return hints


    def get_tier_1_components_by_level(self, level_name: str) -> List[Dict]:
        """
        Retourne tous les composants Tier 1 d'un niveau

        Args:
            level_name: "Corps", "Organe", "Cellule", "Atome"

        Returns:
            Liste des composants
        """
        if level_name not in self.index_by_level:
            return []

        return list(self.index_by_level[level_name].values())


    def get_statistics(self) -> Dict[str, Any]:
        """
        Statistiques sur l'Elite Library

        Returns:
            Dict avec stats
        """
        return {
            'total_components': len(self.elite_library),
            'by_level': {
                level: len(components)
                for level, components in self.index_by_level.items()
            },
            'pregenerated_styles': len(self.pregenerated.get('styles', {}))
        }


if __name__ == "__main__":
    # Tests de base
    print("🧪 Tests ComponentContextualizer")
    print("=" * 60)

    contextualizer = ComponentContextualizer()

    # Test 1 : Stats Elite Library
    stats = contextualizer.get_statistics()
    print(f"✅ Test 1 : Statistiques Elite Library")
    print(f"   Total composants : {stats['total_components']}")
    print(f"   Par niveau : {stats['by_level']}")

    # Test 2 : Résolution Tier 1 (Corps Frontend)
    tier_strategy = contextualizer.resolve_tier_strategy("Frontend", 0)
    if tier_strategy.recommended_tier == 1:
        print(f"✅ Test 2 : Tier 1 trouvé pour 'Frontend' (Corps)")
        print(f"   Confidence : {tier_strategy.confidence}")
    else:
        print(f"❌ Test 2 : Tier 1 non trouvé (attendu Tier 1)")

    # Test 3 : Résolution Tier 3 (composant inexistant)
    tier_strategy = contextualizer.resolve_tier_strategy("ComposantInexistant", 3)
    if tier_strategy.recommended_tier == 3:
        print(f"✅ Test 3 : Tier 3 pour composant inexistant (génération)")
    else:
        print(f"❌ Test 3 : Devrait être Tier 3")

    # Test 4 : Contextualisation complète
    node_data = {
        'name': 'Frontend',
        'role': 'interface',
        'visual_hint': 'main application interface',
        'confidence': 0.92
    }

    context = contextualizer.contextualize_component(
        path="n0[2]",
        node_data=node_data,
        level=0
    )

    print(f"✅ Test 4 : Contextualisation complète")
    print(f"   Nom : {context.name}")
    print(f"   Tier : {context.tier}")
    print(f"   Semantic hints : {context.semantic_hints}")

    # Test 5 : Recherche par niveau
    corps_components = contextualizer.get_tier_1_components_by_level("Corps")
    print(f"✅ Test 5 : {len(corps_components)} composants Corps trouvés")

    print("=" * 60)
    print("🎯 ComponentContextualizer : Tous les tests passés !")
