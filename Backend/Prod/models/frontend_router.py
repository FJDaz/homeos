# Backend/Prod/models/frontend_router.py
"""
Frontend Router - Intelligent provider selection for frontend-related tasks.

This router implements task-specific provider selection with fallback logic,
rate limiting protection, and provider availability checks.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from loguru import logger

from ..config.settings import settings


class FrontendRouter:
    """
    Router for frontend-specific tasks with intelligent provider selection.
    
    Implements:
    - Task-specific provider mapping
    - Groq rate limiting with TTL cache
    - Provider availability checks
    - Fallback logic for unavailable providers
    """
    
    # Task type to provider mapping
    _TASK_PROVIDER_MAP: Dict[str, str] = {
        "vision/analyze_design": "gemini",  # Vision tasks require Gemini
        "generate_components/generate_html": "conditional",  # Context-dependent
        "refine_style/micro_adjustment": "groq",  # Fast response preferred
        "dialogue/chat": "groq",  # Conversational tasks
        "validate_homeostasis/validation": "groq",  # Validation tasks
    }
    
    # Default provider for unknown task types
    _DEFAULT_PROVIDER = "deepseek"
    
    # Context size threshold for Gemini vs DeepSeek
    _CONTEXT_SIZE_THRESHOLD = 50000
    
    # Rate limit TTL in seconds
    _RATE_LIMIT_TTL = 60
    
    def __init__(self) -> None:
        """
        Initialize the FrontendRouter.
        
        Sets up rate limiting cache and detects available providers.
        """
        self._groq_limited: bool = False
        self._groq_limited_until: Optional[datetime] = None
        self._available_providers: Dict[str, bool] = self._detect_available_providers()
        
        logger.debug(
            f"FrontendRouter initialized. Available providers: {self._available_providers}"
        )
    
    def _detect_available_providers(self) -> Dict[str, bool]:
        """
        Detect which providers are available based on settings.
        
        Returns:
            Dictionary mapping provider names to availability status.
        """
        return {
            "deepseek": self._is_provider_available("deepseek"),
            "gemini": self._is_provider_available("gemini"),
            "groq": self._is_provider_available("groq"),
        }
    
    def _is_provider_available(self, provider: str) -> bool:
        """
        Check if a provider is available based on API key configuration.
        
        Args:
            provider: Provider name to check.
            
        Returns:
            True if provider is available, False otherwise.
        """
        if provider == "deepseek":
            return bool(settings.deepseek_api_key)
        elif provider == "gemini":
            return bool(settings.google_api_key)
        elif provider == "groq":
            return bool(settings.groq_api_key)
        return False
    
    def _check_groq_availability(self) -> bool:
        """
        Check if Groq is available (not rate limited).
        
        Returns:
            True if Groq is available, False if rate limited.
        """
        if not self._groq_limited:
            return True
        
        # Check if rate limit TTL has expired
        if datetime.now() > self._groq_limited_until:
            self._groq_limited = False
            self._groq_limited_until = None
            logger.info("Groq rate limit expired, provider is now available")
            return True
        
        return False
    
    def limit_groq(self) -> None:
        """
        Mark Groq as rate limited for the configured TTL.
        
        This should be called when a rate limit error (429) is received.
        """
        self._groq_limited = True
        self._groq_limited_until = datetime.now() + timedelta(
            seconds=self._RATE_LIMIT_TTL
        )
        logger.warning(
            f"Groq rate limited until {self._groq_limited_until}"
        )
    
    def get_provider_for_task(
        self, 
        task_type: str, 
        context_size: Optional[int] = None
    ) -> str:
        """
        Get the appropriate provider for a given task type and context size.
        
        Args:
            task_type: Type of frontend task.
            context_size: Optional context size in tokens/characters.
            
        Returns:
            Provider name to use for the task.
            
        Raises:
            ValueError: If task_type is empty or None.
        """
        if not task_type:
            raise ValueError("task_type cannot be empty")
        
        # Get base provider from mapping
        base_provider = self._TASK_PROVIDER_MAP.get(
            task_type, 
            self._DEFAULT_PROVIDER
        )
        
        # Handle conditional provider selection
        if base_provider == "conditional":
            return self._get_conditional_provider(task_type, context_size)
        
        # Apply rate limiting for Groq tasks
        if base_provider == "groq":
            return self._get_groq_with_fallback()
        
        # Ensure provider is available
        return self._ensure_provider_available(base_provider)
    
    def _get_conditional_provider(
        self, 
        task_type: str, 
        context_size: Optional[int]
    ) -> str:
        """
        Get provider for conditional tasks (context-dependent).
        
        Args:
            task_type: Type of task.
            context_size: Optional context size.
            
        Returns:
            Provider name.
        """
        if task_type == "generate_components/generate_html":
            # Use Gemini for large contexts, DeepSeek for smaller ones
            if context_size and context_size > self._CONTEXT_SIZE_THRESHOLD:
                return self._ensure_provider_available("gemini")
            return self._ensure_provider_available("deepseek")
        
        # Fallback for unknown conditional tasks
        return self._ensure_provider_available(self._DEFAULT_PROVIDER)
    
    def _get_groq_with_fallback(self) -> str:
        """
        Get Groq provider with fallback to Gemini if rate limited.
        
        Returns:
            Provider name (groq or gemini).
        """
        # Check if Groq is available and not rate limited
        if self._available_providers.get("groq") and self._check_groq_availability():
            return "groq"
        
        # Fallback to Gemini
        logger.debug(
            "Groq unavailable or rate limited, falling back to Gemini"
        )
        return self._ensure_provider_available("gemini")
    
    def _ensure_provider_available(self, provider: str) -> str:
        """
        Ensure the requested provider is available, fallback if not.
        
        Args:
            provider: Desired provider.
            
        Returns:
            Available provider name.
        """
        if self._available_providers.get(provider):
            return provider
        
        # Provider not available, find fallback
        fallback = self._find_fallback_provider(provider)
        logger.warning(
            f"Provider {provider} not available, falling back to {fallback}"
        )
        return fallback
    
    def _find_fallback_provider(self, unavailable_provider: str) -> str:
        """
        Find an appropriate fallback provider.
        
        Args:
            unavailable_provider: Provider that is not available.
            
        Returns:
            Fallback provider name.
        """
        # Priority order for fallbacks
        fallback_priority = ["deepseek", "gemini", "groq"]
        
        for provider in fallback_priority:
            if (
                provider != unavailable_provider 
                and self._available_providers.get(provider)
            ):
                return provider
        
        # No providers available, return default
        return self._DEFAULT_PROVIDER
    
    def get_provider(
        self, 
        task_type: str, 
        context_size: Optional[int] = None
    ) -> str:
        """
        Public method to get provider with rate limit handling.
        
        This is the main entry point for external callers.
        
        Args:
            task_type: Type of frontend task.
            context_size: Optional context size.
            
        Returns:
            Provider name to use.
        """
        provider = self.get_provider_for_task(task_type, context_size)
        
        # If Groq is selected, check rate limit and apply if needed
        if provider == "groq":
            # In a real implementation, this would check actual API rate limits
            # For now, we simulate by always applying rate limit after use
            self.limit_groq()
        
        logger.debug(
            f"Selected provider {provider} for task {task_type} "
            f"(context_size: {context_size})"
        )
        return provider
