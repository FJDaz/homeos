"""PatternAnalyzer - Analyse patterns pour insights automatiques."""
import json
from typing import Dict, Any, List
from collections import defaultdict, Counter
import re
from loguru import logger

from ..library.elite_library import EliteLibrary
from ..models.component import Component
from ..models.categories import ComponentCategory
from ..models.sullivan_score import SullivanScore


class PatternAnalyzer:
    """
    Analyse les patterns dans EliteLibrary pour générer des insights automatiques.
    
    Identifie patterns fréquents, tendances, corrélations scores, structures communes.
    """
    
    def __init__(self, library: EliteLibrary):
        """
        Initialise l'analyseur de patterns.

        Args:
            library: Instance EliteLibrary à analyser
        """
        self.library = library
        logger.info("PatternAnalyzer initialized")
    
    def analyze_patterns(self) -> Dict[str, Any]:
        """
        Analyse les composants de la bibliothèque pour générer des insights.

        Returns:
            Dictionnaire contenant les insights générés
        """
        logger.info("Analyzing patterns in EliteLibrary")
        
        insights: Dict[str, Any] = {
            "summary": {},
            "category_insights": {},
            "naming_patterns": {},
            "score_correlations": {},
            "dependency_trends": {}
        }
        
        # Charger tous les composants depuis les fichiers JSON
        components = self._load_all_components()
        
        if not components:
            insights["summary"] = {"message": "Aucun composant à analyser dans la bibliothèque."}
            logger.warning("No components found in EliteLibrary")
            return insights
        
        total_components = len(components)
        
        # Agrégation des données par catégorie
        scores_by_category: Dict[str, List[float]] = defaultdict(list)
        sizes_by_category: Dict[str, List[int]] = defaultdict(list)
        sullivan_scores_by_category: Dict[str, List[float]] = defaultdict(list)
        component_names: List[str] = []
        
        for comp in components:
            category = comp.category or "unknown"
            scores_by_category[category].append(comp.performance_score)
            sizes_by_category[category].append(comp.size_kb)
            sullivan_scores_by_category[category].append(comp.sullivan_score)
            component_names.append(comp.name)
        
        # Insights généraux
        avg_sullivan = sum(c.sullivan_score for c in components) / total_components
        avg_size = sum(c.size_kb for c in components) / total_components
        
        insights["summary"] = {
            "total_components": total_components,
            "average_sullivan_score": round(avg_sullivan, 2),
            "average_size_kb": round(avg_size, 2)
        }
        
        # Insights par catégorie
        for category in ComponentCategory:
            category_components = [c for c in components if c.category == category.value]
            count = len(category_components)
            
            if count > 0:
                avg_sullivan = sum(sullivan_scores_by_category[category.value]) / count
                avg_size = sum(sizes_by_category[category.value]) / count
                
                insights["category_insights"][category.value] = {
                    "count": count,
                    "average_sullivan_score": round(avg_sullivan, 2),
                    "average_size_kb": round(avg_size, 2),
                    "insight": f"Les composants '{category.value}' ont en moyenne un score Sullivan de {round(avg_sullivan, 2)}"
                }
            else:
                insights["category_insights"][category.value] = {
                    "count": 0,
                    "message": "Aucun composant de cette catégorie."
                }
        
        # Patterns de nommage
        all_name_words = Counter(word.lower() for name in component_names for word in re.findall(r'\b\w+\b', name))
        common_words = [word for word, count in all_name_words.most_common(5) if count > 1]
        
        insights["naming_patterns"]["common_words"] = common_words
        
        # Corrélations scores
        core_components = [c for c in components if c.category == ComponentCategory.core.value]
        if core_components:
            avg_core_score = sum(c.sullivan_score for c in core_components) / len(core_components)
            insights["score_correlations"]["core_average"] = round(avg_core_score, 2)
            if avg_core_score >= 85:
                insights["score_correlations"]["core_insight"] = "Les composants core ont en moyenne un score >= 85, indiquant une bonne qualité."
        
        # Tendances taille
        large_components = [c for c in components if c.size_kb > 200]
        if large_components:
            insights["score_correlations"]["large_components_count"] = len(large_components)
            insights["score_correlations"]["large_components_insight"] = f"{len(large_components)} composants de grande taille (>200 KB) détectés."
        
        logger.info(f"Pattern analysis completed: {total_components} components analyzed")
        return insights
    
    def _load_all_components(self) -> List[Component]:
        """
        Charge tous les composants depuis les fichiers JSON de EliteLibrary.

        Returns:
            Liste de composants
        """
        components = []
        
        for file in self.library.path.glob("*.json"):
            if file.name.startswith("archived_"):
                continue
            
            try:
                with open(file, "r", encoding="utf-8") as f:
                    component_dict = json.load(f)
                    # Gérer conversion datetime si nécessaire
                    if "created_at" in component_dict and isinstance(component_dict["created_at"], str):
                        from datetime import datetime
                        component_dict["created_at"] = datetime.fromisoformat(component_dict["created_at"])
                    if "last_used" in component_dict and isinstance(component_dict["last_used"], str):
                        from datetime import datetime
                        component_dict["last_used"] = datetime.fromisoformat(component_dict["last_used"])
                    
                    component = Component(**component_dict)
                    components.append(component)
            except Exception as e:
                logger.warning(f"Error loading component from {file}: {e}")
        
        return components


# Exemple d'utilisation
if __name__ == "__main__":
    import json
    from datetime import datetime
    
    library = EliteLibrary()
    analyzer = PatternAnalyzer(library)
    
    patterns = analyzer.analyze_patterns()
    print(json.dumps(patterns, indent=2, default=str, ensure_ascii=False))
