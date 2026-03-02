from pydantic import BaseModel

class SullivanScore(BaseModel):
    """
    Modèle de score Sullivan.
    
    Attributes:
    performance (int): Score de performance (0-100).
    accessibility (int): Score d'accessibilité (0-100).
    ecology (int): Score d'écologie (0-100).
    popularity (int): Score de popularité (0-100).
    validation (int): Score de validation (0-100).
    """

    performance: int  # Score de performance (0-100)
    accessibility: int  # Score d'accessibilité (0-100)
    ecology: int  # Score d'écologie (0-100)
    popularity: int  # Score de popularité (0-100)
    validation: int  # Score de validation (0-100)

    def total(self) -> float:
        """
        Calcule le score composite.
        
        Returns:
        float: Score composite.
        """
        return (self.performance * 0.3 + 
                self.accessibility * 0.3 + 
                self.ecology * 0.2 + 
                self.popularity * 0.1 + 
                self.validation * 0.1)

ELITE_THRESHOLD = 85  # Seuil pour les élites

# Exemple d'utilisation :
if __name__ == "__main__":
    sullivan_score = SullivanScore(
        performance=80,
        accessibility=90,
        ecology=70,
        popularity=60,
        validation=85,
    )

    print(sullivan_score.dict())
    print(sullivan_score.total())
    print(f"Est-ce que le score est supérieur au seuil élite ? {sullivan_score.total() >= ELITE_THRESHOLD}")