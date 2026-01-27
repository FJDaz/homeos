"""EliteLibrary - Bibliothèque de composants validés avec expiration et archivage."""
import json
from pathlib import Path
from typing import Optional, List
from datetime import datetime, timedelta
from loguru import logger

from ..models.component import Component
from ..models.sullivan_score import SullivanScore, ELITE_THRESHOLD
from ..models.categories import ComponentCategory, classify_component


class EliteLibrary:
    """
    Bibliothèque de composants validés avec gestion expiration et archivage.
    
    Tracker last_used pour chaque composant, archivage automatique si > 6 mois sans usage,
    retrait si score descendant < 85.
    """
    
    ARCHIVE_DIR_NAME = "archived"
    ARCHIVE_AFTER_MONTHS = 6
    MIN_SCORE_FOR_RETENTION = 85

    def __init__(self, path: Path = Path("components/elite/")):
        """
        Initialise la bibliothèque.

        Args:
            path: Chemin d'accès à la bibliothèque
        """
        self.path = path
        self.path.mkdir(parents=True, exist_ok=True)
        
        # Créer répertoire archived
        self.archive_path = self.path / self.ARCHIVE_DIR_NAME
        self.archive_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"EliteLibrary initialized at {self.path}")

    def find_similar(self, intent: str) -> Optional[Component]:
        """
        Recherche un composant similaire dans la bibliothèque.
        Met à jour last_used lors de la recherche.

        Args:
            intent: Intention de recherche

        Returns:
            Composant similaire si trouvé, sinon None
        """
        for file in self.path.glob("*.json"):
            if file.name.startswith("archived_"):
                continue  # Ignorer fichiers archivés
            
            try:
                with open(file, "r", encoding="utf-8") as f:
                    component_dict = json.load(f)
                    component = Component(**component_dict)
                    
                    if intent.lower() in component.name.lower():
                        # Mettre à jour last_used
                        component.last_used = datetime.now()
                        self._save_component(component)
                        logger.info(f"Found similar component: {component.name}, updated last_used")
                        return component
            except Exception as e:
                logger.warning(f"Error loading component from {file}: {e}")
                continue
        
        return None

    def add(self, component: Component) -> bool:
        """
        Ajoute un composant à la bibliothèque si son score est supérieur au seuil élite.

        Args:
            component: Composant à ajouter

        Returns:
            True si le composant est ajouté, False sinon
        """
        if self.validate_entry(component):
            # Classifier le composant si pas déjà fait
            if not component.category:
                component.category = classify_component(component).value
            
            # Initialiser last_used si None
            if component.last_used is None:
                component.last_used = datetime.now()
            
            # Sauvegarder
            self._save_component(component)
            logger.info(f"Component '{component.name}' added to EliteLibrary")
            return True
        return False

    def validate_entry(self, component: Component) -> bool:
        """
        Valide un composant avant de l'ajouter à la bibliothèque.

        Args:
            component: Composant à valider

        Returns:
            True si le composant est valide, False sinon
        """
        sullivan_score = SullivanScore(
            performance=component.performance_score,
            accessibility=component.accessibility_score,
            ecology=component.ecology_score,
            popularity=component.popularity_score,
            validation=component.validation_score,
        )
        return sullivan_score.total() >= ELITE_THRESHOLD

    def _save_component(self, component: Component) -> None:
        """
        Sauvegarde un composant dans un fichier JSON.

        Args:
            component: Composant à sauvegarder
        """
        file_path = self.path / f"{component.name}.json"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(component.to_dict(), f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving component {component.name}: {e}")

    def archive_old_components(self) -> int:
        """
        Archive les composants qui n'ont pas été utilisés depuis plus de 6 mois.

        Returns:
            Nombre de composants archivés
        """
        logger.info("Archiving old components (> 6 months unused)")
        
        cutoff_date = datetime.now() - timedelta(days=self.ARCHIVE_AFTER_MONTHS * 30)
        archived_count = 0
        
        for file in self.path.glob("*.json"):
            if file.name.startswith("archived_"):
                continue
            
            try:
                with open(file, "r", encoding="utf-8") as f:
                    component_dict = json.load(f)
                    component = Component(**component_dict)
                    
                    # Vérifier si last_used est trop ancien
                    if component.last_used and component.last_used < cutoff_date:
                        # Déplacer vers archived
                        archived_file = self.archive_path / f"archived_{file.name}"
                        file.rename(archived_file)
                        archived_count += 1
                        logger.info(f"Archived component: {component.name}")
            except Exception as e:
                logger.warning(f"Error processing {file} for archiving: {e}")
        
        logger.info(f"Archived {archived_count} components")
        return archived_count

    def remove_low_score(self) -> int:
        """
        Retire les composants dont le score est descendant < 85.

        Returns:
            Nombre de composants retirés
        """
        logger.info("Removing low score components (< 85)")
        
        removed_count = 0
        
        for file in self.path.glob("*.json"):
            if file.name.startswith("archived_"):
                continue
            
            try:
                with open(file, "r", encoding="utf-8") as f:
                    component_dict = json.load(f)
                    component = Component(**component_dict)
                    
                    # Vérifier score
                    sullivan_score = SullivanScore(
                        performance=component.performance_score,
                        accessibility=component.accessibility_score,
                        ecology=component.ecology_score,
                        popularity=component.popularity_score,
                        validation=component.validation_score,
                    )
                    
                    if sullivan_score.total() < self.MIN_SCORE_FOR_RETENTION:
                        # Déplacer vers archived
                        archived_file = self.archive_path / f"archived_{file.name}"
                        file.rename(archived_file)
                        removed_count += 1
                        logger.info(f"Removed low score component: {component.name} (score: {sullivan_score.total():.1f})")
            except Exception as e:
                logger.warning(f"Error processing {file} for removal: {e}")
        
        logger.info(f"Removed {removed_count} low score components")
        return removed_count

    def update_last_used(self, component: Component) -> None:
        """
        Met à jour last_used pour un composant.

        Args:
            component: Composant à mettre à jour
        """
        component.last_used = datetime.now()
        self._save_component(component)
        logger.debug(f"Updated last_used for component: {component.name}")


# Exemple d'utilisation
if __name__ == "__main__":
    from datetime import datetime
    
    library = EliteLibrary()

    component = Component(
        name="Composant exemple",
        sullivan_score=90.0,
        performance_score=95,
        accessibility_score=90,
        ecology_score=85,
        popularity_score=80,
        validation_score=95,
        size_kb=1024,
        created_at=datetime.now(),
        user_id="utilisateur_123",
        category=None,
        last_used=None
    )

    print(f"Adding component: {library.add(component)}")
    
    similar_component = library.find_similar("exemple")
    if similar_component:
        print(f"Found: {similar_component.name}")
    
    # Test archivage
    archived = library.archive_old_components()
    print(f"Archived {archived} components")
