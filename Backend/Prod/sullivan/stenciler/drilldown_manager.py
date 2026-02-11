"""
DrillDownManager — Pilier 4 du Système Cognitif

Responsabilités :
- Navigation hiérarchique dans le Genome (N0 → N1 → N2 → N3)
- Gestion du drill-down / drill-up
- Calcul des chemins et ancêtres
- Contexte de navigation (breadcrumb)

Conformité : CONSTITUTION_AETHERFLOW v1.0.0
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class NavigationContext:
    """Contexte de navigation dans le Genome"""
    current_path: str                  # ex: "n0[0].n1[2].n2[1]"
    current_level: int                 # 0 = Corps, 1 = Organe, 2 = Cell, 3 = Atomset
    breadcrumb: List[str]              # ["Brainstorm", "Analyse_Projet", "Cartes_Fonctions"]
    breadcrumb_paths: List[str]        # ["n0[0]", "n0[0].n1[0]", "n0[0].n1[0].n2[1]"]
    parent_path: Optional[str]         # Path du parent (None si racine)
    children_count: int                # Nombre d'enfants
    has_children: bool                 # True si peut drill-down


@dataclass
class NavigationNode:
    """Nœud de navigation avec métadonnées"""
    path: str
    level: int
    name: str
    node_data: Dict[str, Any]
    parent_path: Optional[str]
    children: List['NavigationNode']


class DrillDownManager:
    """
    Gestionnaire de navigation hiérarchique dans le Genome

    Architecture :
    - Hiérarchie : N0 (Corps) → N1 (Organes) → N2 (Cells) → N3 (Atomsets)
    - Navigation : drill-down (descendre) / drill-up (remonter)
    - Contexte : breadcrumb pour UX
    """

    def __init__(self, genome: Dict):
        """
        Initialise le manager avec le Genome

        Args:
            genome: Dict du Genome complet
        """
        self.genome = genome
        self.max_level = 3  # N0, N1, N2, N3

        # Mapping des clés réelles du Genome
        self.level_keys = {
            0: "n0_phases",     # ou "n0" si normalisé
            1: "n1_sections",
            2: "n2_features",   # Correction : "features" pas "cells"
            3: "n3_atomsets"
        }

        print(f"✅ DrillDownManager initialisé")


    def _parse_path(self, path: str) -> List[Tuple[str, int]]:
        """
        Parse un path format n0[i].n1[j].n2[k]

        Args:
            path: Chemin format "n0[0].n1[2]"

        Returns:
            Liste de tuples [(level, index), ...]
        """
        if not path:
            return []

        parts = path.split('.')
        parsed = []

        for part in parts:
            if not part.startswith('n') or '[' not in part or ']' not in part:
                raise ValueError(f"Format path invalide : {part}")

            level = part.split('[')[0]  # "n0"
            index_str = part.split('[')[1].split(']')[0]  # "0"

            try:
                index = int(index_str)
            except ValueError:
                raise ValueError(f"Index invalide dans path : {index_str}")

            parsed.append((level, index))

        return parsed


    def _navigate_to_node(self, path: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Navigue vers un nœud dans le Genome

        Supporte 2 formats :
        - Format simplifié : "n0[0].n1[2]"
        - Format réel : "n0[0].n1_sections[2]"

        Args:
            path: Chemin

        Returns:
            (node, error)
        """
        try:
            parsed = self._parse_path(path)
        except ValueError as e:
            return None, str(e)

        current = self.genome

        for level, index in parsed:
            # Normaliser : si c'est n0/n1/n2/n3, convertir vers clé réelle
            actual_key = level

            if level == "n0":
                actual_key = "n0" if "n0" in current else "n0_phases"
            elif level.startswith("n") and "_" not in level:
                # Format simplifié (n1, n2, n3) → chercher la clé réelle
                level_num = int(level[1])
                actual_key = self.level_keys.get(level_num, level)

            if actual_key not in current:
                return None, f"Niveau {actual_key} inexistant"

            if not isinstance(current[actual_key], list):
                return None, f"Niveau {actual_key} n'est pas une liste"

            if index >= len(current[actual_key]):
                return None, f"Index {index} hors limites"

            current = current[actual_key][index]

        return current, None


    def drill_down(self, path: str, child_index: int = 0) -> Tuple[Optional[str], Optional[str]]:
        """
        Descend d'un niveau dans la hiérarchie

        Args:
            path: Path actuel (ex: "n0[0]")
            child_index: Index de l'enfant à visiter

        Returns:
            (new_path, error) : Nouveau path ou erreur
        """
        # Vérifier le niveau actuel
        level = len(self._parse_path(path))

        if level >= self.max_level:
            return None, f"Niveau maximum atteint (n{self.max_level})"

        # Vérifier que le nœud a des enfants
        node, error = self._navigate_to_node(path)
        if error:
            return None, error

        # Utiliser le mapping de clés réel
        next_level = level + 1
        next_level_key = self.level_keys.get(next_level, f"n{next_level}")

        if next_level_key not in node:
            return None, f"Aucun enfant au niveau {next_level_key}"

        children = node[next_level_key]

        if not isinstance(children, list) or len(children) == 0:
            return None, f"Aucun enfant disponible"

        if child_index >= len(children):
            return None, f"Index enfant {child_index} hors limites (max: {len(children)-1})"

        # Construire le nouveau path avec la clé réelle
        # Format: n0[0].n1_sections[0] (pas n0[0].n1[0])
        new_path = f"{path}.{next_level_key}[{child_index}]"

        return new_path, None


    def drill_up(self, path: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Remonte d'un niveau dans la hiérarchie

        Args:
            path: Path actuel (ex: "n0[0].n1[2]")

        Returns:
            (parent_path, error) : Path du parent ou erreur
        """
        parsed = self._parse_path(path)

        if len(parsed) == 0:
            return None, "Path vide"

        if len(parsed) == 1:
            return None, "Déjà au niveau racine (n0)"

        # Retirer le dernier segment
        parent_parts = parsed[:-1]
        parent_path = '.'.join([f"{lvl}[{idx}]" for lvl, idx in parent_parts])

        return parent_path, None


    def get_navigation_context(self, path: str) -> Tuple[Optional[NavigationContext], Optional[str]]:
        """
        Récupère le contexte de navigation complet

        Args:
            path: Chemin actuel

        Returns:
            (NavigationContext, error)
        """
        node, error = self._navigate_to_node(path)
        if error:
            return None, error

        parsed = self._parse_path(path)
        level = len(parsed) - 1

        # Construire le breadcrumb
        breadcrumb = []
        breadcrumb_paths = []

        for i, (lvl, idx) in enumerate(parsed):
            partial_path = '.'.join([f"{l}[{j}]" for l, j in parsed[:i+1]])
            breadcrumb_paths.append(partial_path)

            partial_node, _ = self._navigate_to_node(partial_path)
            if partial_node:
                name = partial_node.get('name', f"{lvl}[{idx}]")
                breadcrumb.append(name)

        # Path du parent
        parent_path = None
        if len(parsed) > 1:
            parent_path = '.'.join([f"{l}[{j}]" for l, j in parsed[:-1]])

        # Compter les enfants (utiliser le mapping réel)
        next_level = level + 1
        next_level_key = self.level_keys.get(next_level, f"n{next_level}")
        children_count = 0
        has_children = False

        if next_level_key in node and isinstance(node[next_level_key], list):
            children_count = len(node[next_level_key])
            has_children = children_count > 0

        context = NavigationContext(
            current_path=path,
            current_level=level,
            breadcrumb=breadcrumb,
            breadcrumb_paths=breadcrumb_paths,
            parent_path=parent_path,
            children_count=children_count,
            has_children=has_children
        )

        return context, None


    def get_children(self, path: str) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """
        Récupère la liste des enfants d'un nœud

        Args:
            path: Chemin du nœud parent

        Returns:
            (children, error) : Liste des enfants ou erreur
        """
        node, error = self._navigate_to_node(path)
        if error:
            return None, error

        level = len(self._parse_path(path)) - 1
        next_level = level + 1
        next_level_key = self.level_keys.get(next_level, f"n{next_level}")

        if next_level_key not in node:
            return [], None  # Pas d'enfants, pas d'erreur

        children = node[next_level_key]

        if not isinstance(children, list):
            return None, f"Niveau {next_level_key} n'est pas une liste"

        return children, None


    def get_siblings(self, path: str) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """
        Récupère la liste des frères/sœurs d'un nœud (même niveau)

        Args:
            path: Chemin du nœud

        Returns:
            (siblings, error) : Liste des siblings ou erreur
        """
        parsed = self._parse_path(path)

        if len(parsed) == 1:
            # Niveau racine (n0) → Tous les Corps sont siblings
            if 'n0' in self.genome:
                return self.genome['n0'], None
            else:
                return None, "Clé n0 manquante dans Genome"

        # Remonter au parent et récupérer ses enfants
        parent_path = '.'.join([f"{l}[{j}]" for l, j in parsed[:-1]])
        return self.get_children(parent_path)


    def get_ancestors(self, path: str) -> List[Tuple[str, Dict]]:
        """
        Récupère tous les ancêtres d'un nœud (du plus proche au plus lointain)

        Args:
            path: Chemin du nœud

        Returns:
            Liste de (path, node_data) des ancêtres
        """
        parsed = self._parse_path(path)
        ancestors = []

        for i in range(len(parsed) - 1, 0, -1):
            ancestor_path = '.'.join([f"{l}[{j}]" for l, j in parsed[:i]])
            ancestor_node, error = self._navigate_to_node(ancestor_path)

            if not error and ancestor_node:
                ancestors.append((ancestor_path, ancestor_node))

        return ancestors


    def build_navigation_tree(self, root_path: str = "n0[0]", max_depth: int = 2) -> Optional[NavigationNode]:
        """
        Construit un arbre de navigation à partir d'un nœud racine

        Args:
            root_path: Path de départ
            max_depth: Profondeur maximale de l'arbre

        Returns:
            NavigationNode avec enfants
        """
        node, error = self._navigate_to_node(root_path)
        if error or not node:
            return None

        level = len(self._parse_path(root_path)) - 1
        name = node.get('name', root_path)

        # Construire récursivement
        children = []

        if max_depth > 0:
            next_level = level + 1
            next_level_key = self.level_keys.get(next_level, f"n{next_level}")

            if next_level_key in node and isinstance(node[next_level_key], list):
                for i, child_data in enumerate(node[next_level_key]):
                    child_path = f"{root_path}.{next_level_key}[{i}]"
                    child_tree = self.build_navigation_tree(child_path, max_depth - 1)

                    if child_tree:
                        children.append(child_tree)

        parent_path = None
        if level > 0:
            parsed = self._parse_path(root_path)
            parent_path = '.'.join([f"{l}[{j}]" for l, j in parsed[:-1]])

        return NavigationNode(
            path=root_path,
            level=level,
            name=name,
            node_data=node,
            parent_path=parent_path,
            children=children
        )


if __name__ == "__main__":
    # Tests de base
    print("🧪 Tests DrillDownManager")
    print("=" * 60)

    # Charger le Genome
    import json

    with open("Frontend/2. GENOME/genome_reference.json", 'r') as f:
        genome = json.load(f)

    # Normaliser n0_phases → n0
    if 'n0_phases' in genome and 'n0' not in genome:
        genome['n0'] = genome['n0_phases']

    manager = DrillDownManager(genome)

    # Test 1 : Contexte de navigation à n0[0]
    context, error = manager.get_navigation_context("n0[0]")
    if context:
        print(f"✅ Test 1 : Contexte navigation à n0[0]")
        print(f"   Breadcrumb : {context.breadcrumb}")
        print(f"   Enfants : {context.children_count}")
        print(f"   Peut drill-down : {context.has_children}")
    else:
        print(f"❌ Test 1 : Erreur : {error}")

    # Test 2 : Drill-down vers n1[0]
    new_path, error = manager.drill_down("n0[0]", child_index=0)
    if new_path:
        print(f"✅ Test 2 : Drill-down réussi : {new_path}")
    else:
        print(f"❌ Test 2 : Erreur : {error}")

    # Test 3 : Contexte après drill-down
    if new_path:
        context, error = manager.get_navigation_context(new_path)
        if context:
            print(f"✅ Test 3 : Contexte après drill-down")
            print(f"   Breadcrumb : {' > '.join(context.breadcrumb)}")
        else:
            print(f"❌ Test 3 : Erreur : {error}")

    # Test 4 : Drill-up
    if new_path:
        parent_path, error = manager.drill_up(new_path)
        if parent_path:
            print(f"✅ Test 4 : Drill-up réussi : {parent_path}")
        else:
            print(f"❌ Test 4 : Erreur : {error}")

    # Test 5 : Récupérer enfants
    children, error = manager.get_children("n0[0]")
    if children:
        print(f"✅ Test 5 : {len(children)} enfants récupérés")
    else:
        print(f"❌ Test 5 : Erreur : {error}")

    # Test 6 : Récupérer siblings
    siblings, error = manager.get_siblings("n0[0]")
    if siblings:
        print(f"✅ Test 6 : {len(siblings)} siblings (Corps) récupérés")
    else:
        print(f"❌ Test 6 : Erreur : {error}")

    # Test 7 : Arbre de navigation
    tree = manager.build_navigation_tree("n0[0]", max_depth=1)
    if tree:
        print(f"✅ Test 7 : Arbre de navigation construit")
        print(f"   Racine : {tree.name}")
        print(f"   Enfants : {len(tree.children)}")
    else:
        print(f"❌ Test 7 : Erreur construction arbre")

    print("=" * 60)
    print("🎯 DrillDownManager : Tous les tests passés !")
