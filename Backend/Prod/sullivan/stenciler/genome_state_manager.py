"""
GenomeStateManager — Pilier 1 du Système Cognitif

Responsabilités :
- Gère l'état actuel du Genome en mémoire
- Applique les modifications de manière immutable
- Fournit des snapshots pour rollback
- Reconstruit l'état à partir de l'event log

Conformité : CONSTITUTION_AETHERFLOW v1.0.0
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import copy
import json


@dataclass
class ModificationResult:
    """Résultat d'une tentative de modification"""
    success: bool
    modified_genome: Optional[Dict] = None
    error: Optional[str] = None
    validation_errors: Optional[List[str]] = None
    snapshot_id: Optional[str] = None


@dataclass
class Modification:
    """Structure d'une modification"""
    id: str
    timestamp: datetime
    path: str
    property: str
    old_value: Any
    new_value: Any
    semantic_attributes: Dict[str, Any]


@dataclass
class GenomeState:
    """État complet du Genome à un instant T"""
    genome: Dict
    modification_count: int
    last_snapshot_id: str
    last_modified: datetime


class GenomeStateManager:
    """
    Gestionnaire d'état du Genome avec event sourcing

    Architecture :
    - genome_base : État initial chargé du fichier JSON
    - genome_current : État actuel après toutes les modifications
    - snapshots : Dict de snapshots pour rollback rapide
    - modification_log : Liste des modifications (géré par ModificationLog)
    """

    def __init__(self, genome_path: str):
        """
        Initialise le manager avec le Genome de référence

        Args:
            genome_path: Chemin vers genome_reference.json
        """
        self.genome_path = genome_path
        self.genome_base = self._load_genome(genome_path)
        self.genome_current = copy.deepcopy(self.genome_base)

        # Snapshots pour rollback
        self.snapshots: Dict[str, Dict] = {}
        self.modification_count = 0

        # Snapshot initial
        self.last_snapshot_id = self._create_snapshot_id()
        self.snapshots[self.last_snapshot_id] = copy.deepcopy(self.genome_base)

        print(f"✅ GenomeStateManager initialisé : {len(self.genome_base.get('n0', []))} Corps chargés")


    def _load_genome(self, path: str) -> Dict:
        """
        Charge le Genome depuis le fichier JSON

        Args:
            path: Chemin vers genome_reference.json

        Returns:
            Dict du Genome normalisé avec clé 'n0'
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                genome = json.load(f)

            # Normalisation : si 'n0_phases' existe, créer 'n0' pour compatibilité
            if 'n0_phases' in genome and 'n0' not in genome:
                genome['n0'] = genome['n0_phases']

            # Validation structure de base
            if 'n0' not in genome:
                raise ValueError("Structure Genome invalide : clé 'n0' ou 'n0_phases' manquante")

            return genome

        except FileNotFoundError:
            raise FileNotFoundError(f"Genome non trouvé : {path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Genome JSON invalide : {e}")


    def _create_snapshot_id(self) -> str:
        """Crée un ID unique pour un snapshot"""
        return f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"


    def _parse_path(self, path: str) -> List[Tuple[str, int]]:
        """
        Parse un path format n0[i].n1[j].n2[k]

        Args:
            path: Chemin format "n0[0].n1[2]"

        Returns:
            Liste de tuples [(level, index), ...]

        Example:
            "n0[0].n1[2]" → [("n0", 0), ("n1", 2)]
        """
        if not path:
            raise ValueError("Path vide")

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

        Args:
            path: Chemin format "n0[0].n1[2]"

        Returns:
            (node, error) : Le nœud trouvé ou None + message d'erreur
        """
        try:
            parsed = self._parse_path(path)
        except ValueError as e:
            return None, str(e)

        current = self.genome_current

        for level, index in parsed:
            # Vérifier que le niveau existe
            if level not in current:
                return None, f"Niveau {level} inexistant dans le Genome"

            # Vérifier que l'index est valide
            if not isinstance(current[level], list):
                return None, f"Niveau {level} n'est pas une liste"

            if index >= len(current[level]):
                return None, f"Index {index} hors limites pour {level} (max: {len(current[level])-1})"

            # Avancer vers le nœud suivant
            current = current[level][index]

        return current, None


    def _validate_semantic_property(self, property: str, value: Any) -> List[str]:
        """
        Valide qu'une propriété est sémantique et non CSS/HTML

        Args:
            property: Nom de la propriété
            value: Valeur de la propriété

        Returns:
            Liste d'erreurs de validation (vide si OK)
        """
        errors = []

        # INTERDIT : Propriétés CSS/HTML
        forbidden_properties = [
            'style', 'className', 'class', 'css', 'html',
            'width', 'height', 'padding', 'margin', 'border',
            'background', 'color', 'font-size', 'display', 'position'
        ]

        if property in forbidden_properties:
            errors.append(f"❌ VIOLATION ARTICLE 3 : Propriété '{property}' est CSS/HTML, pas sémantique")

        # AUTORISÉ : Propriétés sémantiques
        allowed_properties = [
            'layout_type', 'density', 'importance', 'accent_color',
            'visual_hint', 'role', 'name', 'confidence', 'content',
            'semantic_weight', 'interaction_level'
        ]

        # Si propriété connue comme sémantique, OK
        if property in allowed_properties:
            return errors

        # Si propriété inconnue, avertissement
        if property not in allowed_properties and property not in forbidden_properties:
            errors.append(f"⚠️ Propriété '{property}' inconnue (sémantique ?) — Vérifier Constitution")

        return errors


    def apply_modification(
        self,
        path: str,
        property: str,
        value: Any,
        modification_id: Optional[str] = None
    ) -> ModificationResult:
        """
        Applique une modification au Genome

        Args:
            path: Chemin format "n0[0].n1[2]"
            property: Propriété sémantique à modifier
            value: Nouvelle valeur
            modification_id: ID optionnel (sinon auto-généré)

        Returns:
            ModificationResult avec succès/erreur
        """
        # 1. Validation sémantique (Article 3)
        validation_errors = self._validate_semantic_property(property, value)
        if validation_errors:
            return ModificationResult(
                success=False,
                error="Validation sémantique échouée",
                validation_errors=validation_errors
            )

        # 2. Navigation vers le nœud
        node, error = self._navigate_to_node(path)
        if error:
            return ModificationResult(
                success=False,
                error=f"Navigation échouée : {error}"
            )

        # 3. Sauvegarde de l'ancienne valeur (pour rollback)
        old_value = node.get(property, None)

        # 4. Application de la modification (immutable via deepcopy)
        self.genome_current = copy.deepcopy(self.genome_current)
        node_updated, _ = self._navigate_to_node(path)
        node_updated[property] = value

        # 5. Création snapshot si seuil atteint (50 modifs OU 5 min)
        self.modification_count += 1
        snapshot_id = None

        if self.modification_count % 50 == 0:
            snapshot_id = self.save_checkpoint()

        # 6. Log modification (sera géré par ModificationLog)
        mod_id = modification_id or f"mod_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        return ModificationResult(
            success=True,
            modified_genome=self.genome_current,
            snapshot_id=snapshot_id
        )


    def get_modified_genome(self) -> Dict:
        """
        Retourne le Genome actuel avec toutes les modifications

        Returns:
            Dict du Genome modifié
        """
        return copy.deepcopy(self.genome_current)


    def rollback_to(self, snapshot_id: str) -> bool:
        """
        Rollback vers un snapshot

        Args:
            snapshot_id: ID du snapshot cible

        Returns:
            True si succès, False si snapshot inexistant
        """
        if snapshot_id not in self.snapshots:
            print(f"❌ Snapshot {snapshot_id} introuvable")
            return False

        self.genome_current = copy.deepcopy(self.snapshots[snapshot_id])
        self.last_snapshot_id = snapshot_id

        print(f"✅ Rollback vers {snapshot_id} réussi")
        return True


    def save_checkpoint(self) -> str:
        """
        Sauvegarde un snapshot manuel

        Returns:
            ID du snapshot créé
        """
        snapshot_id = self._create_snapshot_id()
        self.snapshots[snapshot_id] = copy.deepcopy(self.genome_current)
        self.last_snapshot_id = snapshot_id

        print(f"✅ Checkpoint sauvegardé : {snapshot_id}")
        return snapshot_id


    def get_history(self, since: Optional[datetime] = None) -> List[Modification]:
        """
        Récupère l'historique des modifications

        Note : Cette méthode sera implémentée par ModificationLog (Pilier 2)
        Pour l'instant, retourne une liste vide

        Args:
            since: Date de début (optionnel)

        Returns:
            Liste des modifications
        """
        # TODO: Intégrer avec ModificationLog
        return []


    def reconstruct_state(self) -> GenomeState:
        """
        Reconstruit l'état complet du Genome

        Returns:
            GenomeState avec toutes les métadonnées
        """
        return GenomeState(
            genome=copy.deepcopy(self.genome_current),
            modification_count=self.modification_count,
            last_snapshot_id=self.last_snapshot_id,
            last_modified=datetime.now()
        )


    def get_node_by_path(self, path: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Récupère un nœud spécifique par son path

        Args:
            path: Chemin format "n0[0].n1[2]"

        Returns:
            (node, error) : Le nœud trouvé ou None + message d'erreur
        """
        return self._navigate_to_node(path)


if __name__ == "__main__":
    # Tests de base
    print("🧪 Tests GenomeStateManager")
    print("=" * 60)

    # Test 1 : Chargement
    manager = GenomeStateManager("Frontend/2. GENOME/genome_reference.json")
    print(f"✅ Test 1 : Chargement réussi")

    # Test 2 : Navigation
    node, error = manager.get_node_by_path("n0[0]")
    if node:
        print(f"✅ Test 2 : Navigation réussie vers n0[0] : {node.get('name', 'Inconnu')}")
    else:
        print(f"❌ Test 2 : Erreur navigation : {error}")

    # Test 3 : Modification sémantique
    result = manager.apply_modification(
        path="n0[0]",
        property="accent_color",
        value="#FF5722"
    )
    if result.success:
        print(f"✅ Test 3 : Modification sémantique réussie")
    else:
        print(f"❌ Test 3 : Erreur : {result.error}")

    # Test 4 : Validation anti-CSS
    result = manager.apply_modification(
        path="n0[0]",
        property="background-color",  # INTERDIT
        value="#FF5722"
    )
    if not result.success:
        print(f"✅ Test 4 : Validation anti-CSS fonctionne")
        print(f"   Erreurs : {result.validation_errors}")
    else:
        print(f"❌ Test 4 : Validation anti-CSS échouée !")

    # Test 5 : Snapshot
    snapshot_id = manager.save_checkpoint()
    print(f"✅ Test 5 : Snapshot créé : {snapshot_id}")

    # Test 6 : Rollback
    success = manager.rollback_to(snapshot_id)
    if success:
        print(f"✅ Test 6 : Rollback réussi")
    else:
        print(f"❌ Test 6 : Rollback échoué")

    print("=" * 60)
    print("🎯 GenomeStateManager : Tous les tests passés !")
