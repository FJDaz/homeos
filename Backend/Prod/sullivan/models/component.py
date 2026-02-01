from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Component(BaseModel):
    """
    Modèle de composant Sullivan.
    
    Attributes:
    name (str): Nom du composant.
    sullivan_score (float): Score Sullivan (0-100).
    performance_score (int): Score de performance (0-100).
    accessibility_score (int): Score d'accessibilité (0-100).
    ecology_score (int): Score d'écologie (0-100).
    popularity_score (int): Score de popularité (0-100).
    validation_score (int): Score de validation (0-100).
    size_kb (int): Taille du composant en kilo-octets.
    created_at (datetime): Date de création du composant.
    user_id (str): Identifiant de l'utilisateur.
    """

    name: str
    sullivan_score: float  # Score Sullivan (0-100)
    performance_score: int  # Score de performance (0-100)
    accessibility_score: int  # Score d'accessibilité (0-100)
    ecology_score: int  # Score d'écologie (0-100)
    popularity_score: int  # Score de popularité (0-100)
    validation_score: int  # Score de validation (0-100)
    size_kb: int
    created_at: Optional[datetime]
    user_id: str
    category: Optional[str] = None  # Catégorie (core, complex, domain)
    last_used: Optional[datetime] = None  # Date de dernière utilisation

    def to_dict(self) -> dict:
        """
        Convertit le modèle en dictionnaire.
        
        Returns:
        dict: Dictionnaire représentant le modèle.
        """
        return self.dict()

    def __str__(self) -> str:
        """
        Représentation en chaîne de caractères du modèle.
        
        Returns:
        str: Chaîne de caractères représentant le modèle.
        """
        return f"Component(name={self.name}, sullivan_score={self.sullivan_score}, performance_score={self.performance_score}, accessibility_score={self.accessibility_score}, ecology_score={self.ecology_score}, popularity_score={self.popularity_score}, validation_score={self.validation_score}, size_kb={self.size_kb}, created_at={self.created_at}, user_id={self.user_id})"


# Exemple d'utilisation :
if __name__ == "__main__":
    component = Component(
        name="Composant exemple",
        sullivan_score=50.0,
        performance_score=80,
        accessibility_score=90,
        ecology_score=70,
        popularity_score=60,
        validation_score=85,
        size_kb=1024,
        created_at=datetime.now(),
        user_id="utilisateur_123",
    )

    print(component.to_dict())
    print(component)