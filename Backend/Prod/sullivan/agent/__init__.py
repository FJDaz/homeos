"""
Sullivan Agent - Capacités de chatbot, partenaire et agent autonome.

Architecture:
- Memory: Contexte de session long terme
- Tools: Capacités d'action (générer, analyser, modifier)
- Personalities: Système de personnalités multiples (default, weirdo)
- Interface: Chat, overlay, ou intégré au Studio

Usage rapide:
    from Backend.Prod.sullivan.agent import create_agent
    
    agent = await create_agent(user_id="user123", step=4)
    response = await agent.chat("Je veux créer une page de login")
    print(response.content)

Personnalités:
    # Pour les users (pro)
    export SULLIVAN_PERSONALITY=default
    
    # Pour toi (drôle d'oiseau edition)
    export SULLIVAN_PERSONALITY=weirdo
    # ou dans ~/.aetherflow/config.json: {"personality": "weirdo"}
"""

from .sullivan_agent import SullivanAgent, AgentResponse, create_agent
from .memory import ConversationMemory, SessionContext, Message, create_session_id
from .tools import ToolRegistry, Tool, ToolResult, tool_registry

# Nouveau système de personnalités
from .personalities import (
    PersonalityBase,
    SullivanDefault,
    SullivanWeirdo,
    get_personality,
    get_personality_name,
    list_personalities,
)

# Pour compatibilité backward, on expose aussi l'ancienne interface
# mais ça pointe vers le nouveau système
default_personality = get_personality()

__all__ = [
    # Agent principal
    "SullivanAgent",
    "AgentResponse",
    "create_agent",
    # Mémoire
    "ConversationMemory",
    "SessionContext",
    "Message",
    "create_session_id",
    # Outils
    "ToolRegistry",
    "Tool",
    "ToolResult",
    "tool_registry",
    # Personnalités (nouveau système)
    "PersonalityBase",
    "SullivanDefault",
    "SullivanWeirdo",
    "get_personality",
    "get_personality_name",
    "list_personalities",
    # Compatibilité
    "default_personality",
]
