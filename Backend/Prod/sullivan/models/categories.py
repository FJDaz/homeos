"""ComponentCategory - Système de catégorisation des composants."""
from enum import Enum
from typing import Optional
from loguru import logger

from .component import Component


class ComponentCategory(str, Enum):
    """
    Enum pour la catégorisation des composants.
    
    - core: Composants simples réutilisables (< 50 KB, pas de dépendances)
    - complex: Composants avancés (50-200 KB, dépendances modérées)
    - domain: Composants spécialisés métier (> 200 KB, dépendances complexes)
    """
    core = "core"
    complex = "complex"
    domain = "domain"


def classify_component(component: Component) -> ComponentCategory:
    """
    Classifie un composant en fonction de sa taille et de sa complexité.

    Args:
        component: Composant à classer

    Returns:
        ComponentCategory: Catégorie du composant
    """
    size_kb = component.size_kb
    
    # Core: composants simples réutilisables (< 50 KB)
    if size_kb < 50:
        return ComponentCategory.core
    
    # Complex: composants avancés (50-200 KB)
    elif size_kb <= 200:
        return ComponentCategory.complex
    
    # Domain: composants spécialisés métier (> 200 KB)
    else:
        return ComponentCategory.domain


# Exemple d'utilisation
if __name__ == "__main__":
    from datetime import datetime
    
    component1 = Component(
        name="Core Utility",
        sullivan_score=85.0,
        performance_score=90,
        accessibility_score=85,
        ecology_score=90,
        popularity_score=80,
        validation_score=85,
        size_kb=20,
        created_at=datetime.now(),
        user_id="test_user"
    )
    print(f"{component1.name}: {classify_component(component1)}")  # core
    
    component2 = Component(
        name="Complex Handler",
        sullivan_score=80.0,
        performance_score=85,
        accessibility_score=80,
        ecology_score=75,
        popularity_score=70,
        validation_score=80,
        size_kb=100,
        created_at=datetime.now(),
        user_id="test_user"
    )
    print(f"{component2.name}: {classify_component(component2)}")  # complex
    
    component3 = Component(
        name="Domain Service",
        sullivan_score=75.0,
        performance_score=80,
        accessibility_score=75,
        ecology_score=70,
        popularity_score=60,
        validation_score=75,
        size_kb=500,
        created_at=datetime.now(),
        user_id="test_user"
    )
    print(f"{component3.name}: {classify_component(component3)}")  # domain
