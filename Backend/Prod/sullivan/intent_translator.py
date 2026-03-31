"""IntentTranslator - Traduction d'intentions avec système STAR (Situation, Transformation, Abstraction, Réalisation)."""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from loguru import logger

# Try to import EmbeddingModelSingleton for semantic scoring
try:
    from Backend.Prod.cache.semantic_cache import EmbeddingModelSingleton
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    try:
        from ...cache.semantic_cache import EmbeddingModelSingleton
        EMBEDDINGS_AVAILABLE = True
    except ImportError:
        EMBEDDINGS_AVAILABLE = False
        logger.debug("EmbeddingModelSingleton not available. Semantic scoring will use fallback.")


class Situation:
    """Représente une situation dans la chaîne STAR."""
    
    def __init__(self, id: int, description: str, pattern_name: Optional[str] = None, variants: Optional[List[str]] = None):
        """
        Initialise une Situation.
        
        Args:
            id: Identifiant unique
            description: Description de la situation
            pattern_name: Nom du pattern (optionnel, depuis JSON)
            variants: Variantes du pattern (optionnel, depuis JSON)
        """
        self.id = id
        self.description = description
        self.pattern_name = pattern_name
        self.variants = variants or []


class Transformation:
    """Représente une transformation dans la chaîne STAR."""
    
    def __init__(self, id: int, description: str, user_term: Optional[str] = None, tech_term: Optional[str] = None):
        """
        Initialise une Transformation.
        
        Args:
            id: Identifiant unique
            description: Description de la transformation
            user_term: Terme utilisateur (optionnel, depuis JSON)
            tech_term: Terme technique (optionnel, depuis JSON)
        """
        self.id = id
        self.description = description
        self.user_term = user_term
        self.tech_term = tech_term


class Abstraction:
    """Représente une abstraction dans la chaîne STAR."""
    
    def __init__(self, id: int, description: str, name: Optional[str] = None):
        """
        Initialise une Abstraction.
        
        Args:
            id: Identifiant unique
            description: Description de l'abstraction
            name: Nom de l'abstraction (optionnel, depuis JSON)
        """
        self.id = id
        self.description = description
        self.name = name


class Realisation:
    """Représente une réalisation dans la chaîne STAR."""
    
    def __init__(self, id: int, description: str, code: Optional[str] = None, javascript: Optional[str] = None, template: Optional[str] = None):
        """
        Initialise une Realisation.
        
        Args:
            id: Identifiant unique
            description: Description de la réalisation
            code: Code HTML (optionnel, depuis JSON)
            javascript: Code JavaScript (optionnel, depuis JSON)
            template: Template (optionnel, depuis JSON)
        """
        self.id = id
        self.description = description
        self.code = code
        self.javascript = javascript
        self.template = template


class IntentTranslator:
    """
    Traducteur d'intentions utilisant le système STAR.
    
    Charge les mappings depuis star_mappings.json et permet de rechercher
    des situations, propager la chaîne STAR, et calculer des scores de similarité
    avec embeddings sémantiques.
    """
    
    def __init__(self, mappings_path: Optional[Path] = None):
        """
        Initialise IntentTranslator.
        
        Args:
            mappings_path: Chemin vers star_mappings.json (optionnel, utilise chemin par défaut)
        """
        self.index_situations: List[Situation] = []
        self.index_transformations: List[Transformation] = []
        self.index_abstractions: List[Abstraction] = []
        self.index_realisations: List[Realisation] = []
        self._mappings_by_pattern: Dict[str, Dict] = {}  # Mapping pattern_name -> full mapping dict
        
        # Charger modèle d'embeddings si disponible
        self._embedding_model = None
        if EMBEDDINGS_AVAILABLE:
            try:
                embedding_singleton = EmbeddingModelSingleton()
                self._embedding_model = embedding_singleton.get_model("all-MiniLM-L6-v2")
                if self._embedding_model:
                    logger.info("Embedding model loaded for semantic scoring")
            except Exception as e:
                logger.warning(f"Failed to load embedding model: {e}. Will use fallback scoring.")
        
        # Charger mappings depuis JSON
        if mappings_path is None:
            # Chemin par défaut : depuis le module actuel
            current_dir = Path(__file__).parent
            mappings_path = current_dir / "knowledge" / "star_mappings.json"
        
        self._load_mappings(mappings_path)
    
    def _load_mappings(self, mappings_path: Path) -> None:
        """
        Charge les mappings depuis le fichier JSON.
        
        Args:
            mappings_path: Chemin vers star_mappings.json
        """
        try:
            if not mappings_path.exists():
                logger.warning(f"star_mappings.json not found at {mappings_path}. Indexes will be empty.")
                return
            
            with open(mappings_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'mappings' not in data:
                logger.warning("Invalid JSON structure: 'mappings' key not found")
                return
            
            mappings = data['mappings']
            logger.info(f"Loading {len(mappings)} STAR mappings from {mappings_path}")
            
            for idx, mapping in enumerate(mappings):
                # Validation des clés requises
                required_keys = ['pattern_name', 'variants', 'transformations', 'abstraction', 'realisation']
                if not all(key in mapping for key in required_keys):
                    logger.warning(f"Skipping mapping {idx}: missing required keys")
                    continue
                
                # Créer objets STAR depuis la structure JSON
                pattern_name = mapping['pattern_name']
                variants = mapping.get('variants', [])
                transformations_dict = mapping.get('transformations', {})
                abstraction_dict = mapping.get('abstraction', {})
                realisation_dict = mapping.get('realisation', {})
                
                # Créer Situation depuis pattern_name et variants
                situation_desc = f"{pattern_name}: {', '.join(variants[:2])}" if variants else pattern_name
                situation = Situation(
                    id=idx,
                    description=situation_desc,
                    pattern_name=pattern_name,
                    variants=variants
                )
                
                # Créer Transformation depuis transformations
                user_term = transformations_dict.get('user_term', '')
                tech_term = transformations_dict.get('tech_term', '')
                transformation_desc = f"{user_term} -> {tech_term}" if user_term and tech_term else user_term or tech_term
                transformation = Transformation(
                    id=idx,
                    description=transformation_desc,
                    user_term=user_term,
                    tech_term=tech_term
                )
                
                # Créer Abstraction depuis abstraction
                abstraction_name = abstraction_dict.get('name', '')
                abstraction_desc = abstraction_dict.get('description', '')
                abstraction = Abstraction(
                    id=idx,
                    description=abstraction_desc or abstraction_name,
                    name=abstraction_name
                )
                
                # Créer Realisation depuis realisation
                realisation_code = realisation_dict.get('code', '')
                realisation_js = realisation_dict.get('javascript', '')
                realisation_template = realisation_dict.get('template', 'html')
                realisation_desc = f"{realisation_template} component"
                realisation = Realisation(
                    id=idx,
                    description=realisation_desc,
                    code=realisation_code,
                    javascript=realisation_js,
                    template=realisation_template
                )
                
                # Ajouter aux index
                self.index_situations.append(situation)
                self.index_transformations.append(transformation)
                self.index_abstractions.append(abstraction)
                self.index_realisations.append(realisation)
                
                # Stocker mapping complet pour propagate_star
                self._mappings_by_pattern[pattern_name] = {
                    'situation': situation,
                    'transformation': transformation,
                    'abstraction': abstraction,
                    'realisation': realisation,
                    'mapping': mapping
                }
            
            logger.info(f"Loaded {len(self.index_situations)} STAR mappings successfully")
            
        except FileNotFoundError:
            logger.warning(f"star_mappings.json not found at {mappings_path}. Indexes will be empty.")
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing star_mappings.json: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading mappings: {e}", exc_info=True)
    
    def parse_query(self, query: str) -> Dict[str, List[str]]:
        """
        Extrait les entités (éléments, actions, conditions) de la requête.
        
        Args:
            query: Requête utilisateur
            
        Returns:
            Dictionnaire avec entités extraites
        """
        patterns = {
            "éléments": r"\b(nom|prénom|adresse|téléphone)\b",
            "actions": r"\b(ajouter|supprimer|modifier)\b",
            "conditions": r"\b( si | alors | sinon )\b"
        }
        entites = defaultdict(list)
        for key, pattern in patterns.items():
            matches = re.findall(pattern, query, re.IGNORECASE)
            entites[key] = matches
        return dict(entites)

    def score_mapping(self, query: str, situation: Situation) -> float:
        """
        Calcule le score de similarité entre une requête et une situation.
        
        Utilise embeddings sémantiques (sentence-transformers) si disponible,
        sinon fallback sur comptage de mots.
        
        Args:
            query: Requête utilisateur
            situation: Situation à scorer
            
        Returns:
            Score de similarité entre 0 et 1
        """
        if self._embedding_model is not None:
            try:
                from sentence_transformers import util
                
                # Calculer embeddings
                query_embedding = self._embedding_model.encode([query], convert_to_tensor=True)
                situation_text = situation.description
                situation_embedding = self._embedding_model.encode([situation_text], convert_to_tensor=True)
                
                # Calculer similarité cosinus
                score = util.cos_sim(query_embedding, situation_embedding).item()
                # Normaliser entre 0 et 1 (cos_sim retourne -1 à 1)
                score = max(0.0, min(1.0, (score + 1) / 2))
                return float(score)
            except Exception as e:
                logger.warning(f"Error calculating embeddings: {e}. Falling back to word count.")
        
        # Fallback : comptage de mots
        query_words = set(query.lower().split())
        situation_words = set(situation.description.lower().split())
        common_words = query_words.intersection(situation_words)
        
        if not query_words:
            return 0.0
        
        score = len(common_words) / len(query_words)
        return float(score)
    
    def search_situation(self, query: str, limit: int = 5) -> List[Situation]:
        """
        Recherche des situations similaires à la requête.
        
        Utilise score_mapping() avec embeddings pour scorer chaque situation,
        puis retourne les top N triés par pertinence.
        
        Args:
            query: Requête utilisateur
            limit: Nombre maximum de résultats (défaut: 5)
            
        Returns:
            Liste de Situation triée par score décroissant
        """
        if not self.index_situations:
            logger.warning("No situations in index. Returning empty list.")
            return []
        
        scored_situations: List[Tuple[float, Situation]] = []
        
        for situation in self.index_situations:
            try:
                score = self.score_mapping(query, situation)
                scored_situations.append((score, situation))
            except Exception as e:
                logger.warning(f"Error scoring situation {situation.id}: {e}")
                continue
        
        # Trier par score décroissant
        scored_situations.sort(key=lambda x: x[0], reverse=True)
        
        # Retourner top N
        results = [situation for _, situation in scored_situations[:limit]]
        logger.info(f"Found {len(results)} situations for query '{query}'")
        return results

    def propagate_star(self, situation: Situation) -> Optional[Realisation]:
        """
        Propage la chaîne STAR : Situation → Transformation → Abstraction → Réalisation.
        
        Args:
            situation: Situation de départ
            
        Returns:
            Realisation correspondante ou None si non trouvée
        """
        if not situation.pattern_name:
            logger.warning(f"Situation {situation.id} has no pattern_name. Cannot propagate STAR.")
            return None
        
        # Chercher le mapping complet depuis pattern_name
        mapping_data = self._mappings_by_pattern.get(situation.pattern_name)
        if not mapping_data:
            logger.warning(f"No mapping found for pattern_name '{situation.pattern_name}'")
            return None
        
        realisation = mapping_data['realisation']
        logger.info(f"Propagated STAR for '{situation.pattern_name}': {realisation.description}")
        return realisation