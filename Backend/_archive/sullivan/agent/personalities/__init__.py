"""
Sullivan Personality System

Charge dynamiquement la personnalité selon la configuration.

Usage:
    from . import get_personality
    
    personality = get_personality()
    prompt = personality.get_system_prompt(context)

Configuration:
    1. Variable d'environnement: SULLIVAN_PERSONALITY=weirdo
    2. Fichier config: ~/.aetherflow/config.json -> {"personality": "weirdo"}
    3. Défaut: sullivan_default (professionnel)
"""

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Type

# Import base class
from .base import PersonalityBase

# Import personalities
from .sullivan_default import SullivanDefault
from .sullivan_weirdo import SullivanWeirdo

# Registry of available personalities
PERSONALITIES: dict[str, Type[PersonalityBase]] = {
    "default": SullivanDefault,
    "weirdo": SullivanWeirdo,
    # Ajoute tes personnalités ici !
}


def get_personality_name() -> str:
    """
    Détermine quelle personnalité utiliser.
    
    Ordre de priorité:
    1. Variable d'environnement SULLIVAN_PERSONALITY
    2. Fichier ~/.aetherflow/config.json -> personality
    3. Défaut: "default"
    """
    # 1. Variable d'environnement
    env_personality = os.getenv("SULLIVAN_PERSONALITY")
    if env_personality:
        return env_personality.lower()
    
    # 2. Fichier de config utilisateur
    config_path = Path.home() / ".aetherflow" / "config.json"
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text())
            personality = config.get("personality")
            if personality:
                return personality.lower()
        except (json.JSONDecodeError, IOError):
            pass
    
    # 3. Défaut
    return "default"


def get_personality(name: str | None = None) -> PersonalityBase:
    """
    Renvoie la classe de personnalité demandée.
    
    Args:
        name: Nom de la personnalité (None = auto-detect)
        
    Returns:
        Classe de personnalité (hérite de PersonalityBase)
        
    Example:
        >>> personality = get_personality()
        >>> print(personality.NAME)
        'Sullivan'
    """
    personality_name = name.lower() if name else get_personality_name()
    
    if personality_name not in PERSONALITIES:
        print(f"⚠️  Personnalité '{personality_name}' inconnue. Utilisation de 'default'.")
        print(f"   Disponibles: {', '.join(PERSONALITIES.keys())}")
        personality_name = "default"
    
    return PERSONALITIES[personality_name]


def list_personalities() -> list[str]:
    """Liste les personnalités disponibles."""
    return list(PERSONALITIES.keys())


def add_personality(name: str, personality_class: Type[PersonalityBase]) -> None:
    """
    Enregistre une nouvelle personnalité dynamiquement.
    
    Args:
        name: Nom de la personnalité
        personality_class: Classe héritant de PersonalityBase
        
    Example:
        >>> from .mon_custom import MonSullivan
        >>> add_personality("custom", MonSullivan)
    """
    PERSONALITIES[name.lower()] = personality_class


# Export pour import facile
__all__ = [
    "PersonalityBase",
    "SullivanDefault", 
    "SullivanWeirdo",
    "get_personality",
    "get_personality_name",
    "list_personalities",
    "add_personality",
    "PERSONALITIES",
]
