"""Base interface for LLM clients."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from loguru import logger


@dataclass
class GenerationResult:
    """Result of code generation."""
    success: bool
    code: str
    tokens_used: int
    input_tokens: int
    output_tokens: int
    cost_usd: float
    execution_time_ms: float
    error: Optional[str] = None
    provider: Optional[str] = None


class BaseLLMClient(ABC):
    """Base interface for LLM clients."""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        cache_params: Optional[Dict[str, Any]] = None,
        output_constraint: Optional[str] = None
    ) -> GenerationResult:
        """
        Generate code from a prompt.
        
        Args:
            prompt: The task description
            context: Additional context (framework, language, etc.)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            cache_params: Optional cache control parameters for prompt caching
            output_constraint: Optional constraint on output format (e.g., "JSON only", "Code only", "No prose")
            
        Returns:
            GenerationResult with the generated code
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass
    
    @property
    @abstractmethod
    def specialties(self) -> List[str]:
        """List of specialties for this provider."""
        pass
    
    async def close(self) -> None:
        """Close the client (cleanup resources)."""
        pass
    
    async def check_balance(self) -> Optional[float]:
        """
        Check account balance (if API supports it).
        
        Returns:
            Balance in USD if available, None if not supported or check failed
        """
        # Default implementation: not supported
        # Override in subclasses if API supports balance checking
        return None
    
    def _should_check_balance(self) -> bool:
        """Check if balance check should be performed."""
        from ..config.settings import settings
        return settings.enable_balance_check
