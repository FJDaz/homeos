from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import json
import os
from pathlib import Path

class Component(BaseModel):
    """
    Modèle de composant avec métadonnées.
    
    Attributes:
    name (str): Nom du composant.
    sullivan_score (float): Score Sullivan du composant.
    performance_score (float): Score de performance du composant.
    accessibility_score (float): Score d'accessibilité du composant.
    size_kb (float): Taille du composant en kilo-octets.
    created_at (datetime): Date de création du composant.
    user_id (int): Identifiant de l'utilisateur qui a créé le composant.
    """
    name: str
    sullivan_score: float
    performance_score: float
    accessibility_score: float
    size_kb: float
    created_at: datetime
    user_id: int

    def calculate_total_score(self) -> float:
        """
        Calcule le score total du composant en additionnant les scores Sullivan, de performance et d'accessibilité.
        
        Returns:
        float: Le score total du composant.
        """
        return self.sullivan_score + self.performance_score + self.accessibility_score

    def calculate_average_score(self) -> float:
        """
        Calcule le score moyen du composant en divisant le score total par 3.
        
        Returns:
        float: Le score moyen du composant.
        """
        return self.calculate_total_score() / 3

    def get_component_info(self) -> dict:
        """
        Renvoie un dictionnaire contenant les informations du composant.
        
        Returns:
        dict: Un dictionnaire contenant les informations du composant.
        """
        return {
            "name": self.name,
            "sullivan_score": self.sullivan_score,
            "performance_score": self.performance_score,
            "accessibility_score": self.accessibility_score,
            "size_kb": self.size_kb,
            "created_at": self.created_at,
            "user_id": self.user_id,
            "total_score": self.calculate_total_score(),
            "average_score": self.calculate_average_score()
        }

class KnowledgeBase:
    """
    Classe KnowledgeBase pour stocker et récupérer des connaissances sur les patterns, les principes HCI et les analytics.
    
    Attributes:
    patterns (dict): Dictionnaire contenant les patterns.
    hci_principles (dict): Dictionnaire contenant les principes HCI.
    analytics (dict): Dictionnaire contenant les analytics.
    """
    def __init__(self):
        self.patterns = self.load_patterns()
        self.hci_principles = self.load_hci_principles()
        self.analytics = self.load_analytics()

    def load_patterns(self) -> dict:
        """
        Charge les patterns à partir des fichiers JSON dans le répertoire knowledge/patterns/.
        
        Returns:
        dict: Dictionnaire contenant les patterns.
        """
        patterns = {}
        for file in Path("knowledge/patterns/").glob("*.json"):
            with open(file, "r") as f:
                pattern_name = file.stem
                patterns[pattern_name] = json.load(f)
        return patterns

    def load_hci_principles(self) -> dict:
        """
        Charge les principes HCI à partir des fichiers JSON dans le répertoire knowledge/hci_principles/.
        
        Returns:
        dict: Dictionnaire contenant les principes HCI.
        """
        hci_principles = {}
        for file in Path("knowledge/hci_principles/").glob("*.json"):
            with open(file, "r") as f:
                principle_name = file.stem
                hci_principles[principle_name] = json.load(f)
        return hci_principles

    def load_analytics(self) -> dict:
        """
        Charge les analytics à partir des fichiers JSON dans le répertoire knowledge/analytics/.
        
        Returns:
        dict: Dictionnaire contenant les analytics.
        """
        analytics = {}
        for file in Path("knowledge/analytics/").glob("*.json"):
            with open(file, "r") as f:
                analytic_name = file.stem
                analytics[analytic_name] = json.load(f)
        return analytics

    def search_patterns(self, query: str) -> dict:
        """
        Recherche des patterns en fonction de la requête.
        
        Args:
        query (str): Requête de recherche.
        
        Returns:
        dict: Dictionnaire contenant les patterns correspondant à la requête.
        """
        results = {}
        for pattern_name, pattern in self.patterns.items():
            if query.lower() in pattern_name.lower() or query.lower() in str(pattern).lower():
                results[pattern_name] = pattern
        return results

    def get_hci_principles(self) -> dict:
        """
        Renvoie les principes HCI.
        
        Returns:
        dict: Dictionnaire contenant les principes HCI.
        """
        return self.hci_principles

    def get_analytics(self) -> dict:
        """
        Renvoie les analytics.
        
        Returns:
        dict: Dictionnaire contenant les analytics.
        """
        return self.analytics

# Exemple d'utilisation
if __name__ == "__main__":
    component = Component(
        name="Composant exemple",
        sullivan_score=8.5,
        performance_score=9.2,
        accessibility_score=8.8,
        size_kb=1024.0,
        created_at=datetime.now(),
        user_id=1
    )

    print(component.get_component_info())

    knowledge_base = KnowledgeBase()
    print(knowledge_base.search_patterns("pricing"))
    print(knowledge_base.get_hci_principles())
    print(knowledge_base.get_analytics())

