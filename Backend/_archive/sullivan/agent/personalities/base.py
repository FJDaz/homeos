"""
Base class for Sullivan personalities.

All personality implementations must inherit from this class
and implement the required methods.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class PersonalityBase(ABC):
    """Abstract base class for Sullivan personality implementations."""
    
    # Identity
    NAME: str = "Sullivan"
    ROLE: str = "Assistant"
    AVATAR: str = "🎨"
    
    # Personality traits (1-10 scale)
    TRAITS: Dict[str, int] = {}
    
    # Response style
    MAX_SENTENCES: int = 4
    USE_EMOJIS: bool = True
    FORMALITY_LEVEL: int = 5  # 1=casual, 10=formal
    
    @classmethod
    @abstractmethod
    def get_system_prompt(cls, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate the system prompt for this personality.
        
        Args:
            context: Session context (step, mode, genome, etc.)
            
        Returns:
            Complete system prompt string
        """
        pass
    
    @classmethod
    def get_identity(cls) -> Dict[str, Any]:
        """Return identity info for UI display."""
        return {
            "name": cls.NAME,
            "role": cls.ROLE,
            "avatar": cls.AVATAR,
            "traits": cls.TRAITS,
        }
    
    @classmethod
    def format_response(cls, content: str) -> str:
        """
        Optional post-processing for responses.
        Override to add personality-specific formatting.
        """
        return content
    
    @classmethod
    def get_welcome_message(cls, step: int = 1) -> str:
        """
        Generate welcome message for a given journey step.
        Override for custom welcome messages.
        """
        return cls._default_welcome(step)
    
    @classmethod
    def _default_welcome(cls, step: int) -> str:
        """Default welcome message template."""
        messages = {
            1: f"{cls.AVATAR} Salut ! Je suis {cls.NAME}, prêt à t'aider avec ton projet. Commençons par le nom ?",
            2: f"Parfait ! Parlons un peu du contexte de ce projet maintenant.",
            3: f"Super ! On va définir l'identité visuelle maintenant.",
            4: f"Excellent ! Passons aux couleurs maintenant.",
            5: f"Génial ! Quelle typographie imagines-tu ?",
            6: f"Top ! Parlons structure et éléments UI maintenant.",
            7: f"Parfait ! Voyons comment tout s'organise.",
            8: f"Génial ! Voyons le résultat de notre travail.",
            9: f"🎉 Félicitations ! Ton projet est prêt. Que veux-tu faire maintenant ?",
        }
        return messages.get(step, f"{cls.AVATAR} Comment puis-je t'aider ?")
