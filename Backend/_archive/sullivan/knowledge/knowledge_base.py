import json
from pathlib import Path


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