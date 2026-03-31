"""
Memory - Gestion du contexte et de la mémoire de conversation.
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, field, asdict
from loguru import logger


@dataclass
class Message:
    """Un message dans la conversation."""
    role: str  # "user", "assistant", "system", "tool"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
        )


@dataclass  
class SessionContext:
    """Contexte d'une session utilisateur."""
    session_id: str
    user_id: str
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    
    # Contexte métier
    current_project: Optional[str] = None
    current_step: int = 1  # Étape du parcours UX (1-9)
    genome: Optional[Dict[str, Any]] = None
    design_structure: Optional[Dict[str, Any]] = None
    visual_intent_report: Optional[Dict[str, Any]] = None
    
    # Préférences utilisateur
    preferred_style: Optional[str] = None  # minimal, brutalist, etc.
    mode: str = "normal"  # normal vs expert
    theme_preference: Optional[str] = None  # "light", "dark", "system"
    language_preference: Optional[str] = None  # "fr", "en", "es", "de", "it"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionContext":
        # Convertir les timestamps
        for field_name in ["created_at", "last_activity"]:
            if field_name in data and isinstance(data[field_name], str):
                data[field_name] = datetime.fromisoformat(data[field_name])
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class ConversationMemory:
    """
    Mémoire de conversation avec:
    - Historique complet des messages
    - Résumé pour contexte LLM (fenêtre glissante)
    - Stockage persistant par session
    """
    
    def __init__(
        self,
        session_id: str,
        user_id: str = "anonymous",
        max_history: int = 50,
        context_window: int = 10,
        storage_dir: Optional[Path] = None,
    ):
        """
        Args:
            session_id: ID unique de session
            user_id: ID utilisateur
            max_history: Nombre max de messages à garder
            context_window: Nombre de messages pour le contexte LLM
            storage_dir: Répertoire de stockage persistant
        """
        self.session_id = session_id
        self.user_id = user_id
        self.max_history = max_history
        self.context_window = context_window
        
        self.messages: List[Message] = []
        self.session_context = SessionContext(
            session_id=session_id,
            user_id=user_id,
        )
        
        # Stockage persistant
        if storage_dir is None:
            storage_dir = Path.home() / ".aetherflow" / "sessions"
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Charger session existante si présente
        self._load()
        
        logger.info(f"ConversationMemory initialized: {session_id}")
    
    def add_message(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Ajoute un message à l'historique."""
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {},
        )
        self.messages.append(message)
        
        # Garder seulement les N derniers messages
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
        
        # Mettre à jour l'activité
        self.session_context.last_activity = datetime.now()
        
        # Sauvegarder
        self._save()
    
    def get_context_for_llm(self, include_system: bool = True) -> List[Dict[str, str]]:
        """
        Retourne les derniers messages formatés pour un LLM.
        
        Returns:
            Liste de dicts {"role": ..., "content": ...}
        """
        messages = []
        
        # Message système avec contexte
        if include_system:
            system_prompt = self._build_system_prompt()
            messages.append({"role": "system", "content": system_prompt})
        
        # Derniers messages de l'historique
        recent_messages = self.messages[-self.context_window:]
        for msg in recent_messages:
            messages.append({
                "role": msg.role,
                "content": msg.content,
            })
        
        return messages
    
    def _build_system_prompt(self) -> str:
        """Construit le prompt système avec le contexte actuel."""
        from .personalities import get_personality
        
        # Charge la personnalité configurée (default ou weirdo)
        personality = get_personality()
        
        ctx = self.session_context
        
        # Utiliser la classe de personnalité pour générer le prompt
        context_dict = {
            "step": ctx.current_step,
            "mode": ctx.mode,
            "current_project": ctx.current_project,
            "preferred_style": ctx.preferred_style,
            "genome": ctx.genome,
            "theme": ctx.theme_preference or "system",
            "language": ctx.language_preference or "fr",
        }
        
        return personality.get_system_prompt(context_dict)
    
    def update_context(self, **kwargs) -> None:
        """Met à jour le contexte de session."""
        for key, value in kwargs.items():
            if hasattr(self.session_context, key):
                setattr(self.session_context, key, value)
        self.session_context.last_activity = datetime.now()
        self._save()
    
    # === Gestion des préférences utilisateur ===
    
    def set_theme(self, theme: str) -> bool:
        """
        Définit la préférence de thème pour la session.
        
        Args:
            theme: Thème préféré ("light", "dark", "system")
            
        Returns:
            True si le thème a été défini, False si valeur invalide
        """
        valid_themes = ["light", "dark", "system"]
        if theme not in valid_themes:
            logger.warning(f"Invalid theme '{theme}'. Valid: {valid_themes}")
            return False
        
        self.update_context(theme_preference=theme)
        logger.info(f"Theme set to '{theme}' for session {self.session_id}")
        return True
    
    def get_theme(self) -> str:
        """
        Récupère le thème préféré (défaut: system).
        
        Returns:
            Thème préféré ("light", "dark", ou "system")
        """
        return self.session_context.theme_preference or "system"
    
    def set_language(self, language: str) -> bool:
        """
        Définit la préférence de langue pour la session.
        
        Args:
            language: Langue préférée ("fr", "en", "es", "de", "it")
            
        Returns:
            True si la langue a été définie, False si valeur invalide
        """
        valid_languages = ["fr", "en", "es", "de", "it"]
        if language not in valid_languages:
            logger.warning(f"Invalid language '{language}'. Valid: {valid_languages}")
            return False
        
        self.update_context(language_preference=language)
        logger.info(f"Language set to '{language}' for session {self.session_id}")
        return True
    
    def get_language(self) -> str:
        """
        Récupère la langue préférée (défaut: fr).
        
        Returns:
            Code langue ISO 639-1 ("fr", "en", etc.)
        """
        return self.session_context.language_preference or "fr"
    
    def get_preferences(self) -> Dict[str, Any]:
        """
        Récupère toutes les préférences utilisateur de la session.
        
        Returns:
            Dictionnaire des préférences (theme, language, style, mode)
        """
        ctx = self.session_context
        return {
            "theme": ctx.theme_preference or "system",
            "language": ctx.language_preference or "fr",
            "style": ctx.preferred_style,
            "mode": ctx.mode,
        }
    
    def _save(self) -> None:
        """Sauvegarde la session sur disque."""
        try:
            session_file = self.storage_dir / f"{self.session_id}.json"
            data = {
                "session_context": self.session_context.to_dict(),
                "messages": [msg.to_dict() for msg in self.messages],
            }
            session_file.write_text(json.dumps(data, indent=2, default=str))
        except Exception as e:
            logger.warning(f"Failed to save session: {e}")
    
    def _load(self) -> None:
        """Charge une session existante."""
        try:
            session_file = self.storage_dir / f"{self.session_id}.json"
            if session_file.exists():
                data = json.loads(session_file.read_text())
                self.session_context = SessionContext.from_dict(data["session_context"])
                self.messages = [Message.from_dict(m) for m in data.get("messages", [])]
                logger.info(f"Loaded existing session: {self.session_id}")
        except Exception as e:
            logger.warning(f"Failed to load session: {e}")
    
    def clear(self) -> None:
        """Efface l'historique mais garde le contexte."""
        self.messages = []
        self._save()
    
    def export_conversation(self) -> Dict[str, Any]:
        """Exporte la conversation complète."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "session_context": self.session_context.to_dict(),
            "messages": [msg.to_dict() for msg in self.messages],
            "message_count": len(self.messages),
        }


def create_session_id(user_id: str = "anonymous") -> str:
    """Crée un ID de session unique."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_hash = hashlib.blake2b(
        f"{user_id}{timestamp}".encode(),
        digest_size=8
    ).hexdigest()
    return f"{user_id}_{timestamp}_{random_hash[:8]}"


__all__ = [
    "Message",
    "SessionContext",
    "ConversationMemory",
    "create_session_id",
]
