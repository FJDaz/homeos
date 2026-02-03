"""Smart context-based routing for LLM providers.

Routes steps to appropriate providers based on estimated context size,
with automatic fallback cascade and intelligent chunking support.
"""
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from loguru import logger

from .plan_reader import Step


class ProviderTier(Enum):
    """Provider tiers based on capabilities."""
    FAST = "fast"           # Groq - < 10k tokens, ultra fast
    BALANCED = "balanced"   # DeepSeek - 10k-50k tokens, good quality/cost
    HIGH_CAPACITY = "high"  # Gemini - > 50k tokens, 1M+ context
    VISION = "vision"       # Gemini - multimodal, vision tasks


@dataclass
class ProviderProfile:
    """Profile for a provider with capabilities and limits."""
    name: str
    tier: ProviderTier
    max_tokens: int
    max_input_tokens: int
    typical_speed: str  # "fast", "medium", "slow"
    cost_efficiency: str  # "low", "medium", "high"
    specialties: List[str]
    rate_limit_rpm: int  # Requests per minute limit
    rate_limit_tpm: int  # Tokens per minute limit


# Provider profiles with their capabilities
PROVIDER_PROFILES = {
    "groq": ProviderProfile(
        name="groq",
        tier=ProviderTier.FAST,
        max_tokens=8192,
        max_input_tokens=12000,  # TPM limit for llama-3.3-70b
        typical_speed="fast",
        cost_efficiency="high",
        specialties=["fast_generation", "simple_tasks", "refactoring"],
        rate_limit_rpm=30,
        rate_limit_tpm=12000
    ),
    "deepseek": ProviderProfile(
        name="deepseek",
        tier=ProviderTier.BALANCED,
        max_tokens=8192,
        max_input_tokens=64000,  # 64k context
        typical_speed="medium",
        cost_efficiency="high",
        specialties=["code_generation", "complex_code", "reasoning"],
        rate_limit_rpm=100,
        rate_limit_tpm=100000
    ),
    "gemini": ProviderProfile(
        name="gemini",
        tier=ProviderTier.HIGH_CAPACITY,
        max_tokens=8192,
        max_input_tokens=1000000,  # 1M context
        typical_speed="fast",
        cost_efficiency="high",
        specialties=["large_context", "analysis", "documentation", "vision"],
        rate_limit_rpm=60,
        rate_limit_tpm=1000000
    ),
    "codestral": ProviderProfile(
        name="codestral",
        tier=ProviderTier.FAST,
        max_tokens=8192,
        max_input_tokens=32000,
        typical_speed="fast",
        cost_efficiency="medium",
        specialties=["code_completion", "fim", "small_refactoring"],
        rate_limit_rpm=60,
        rate_limit_tpm=60000
    ),
}


@dataclass
class RoutingDecision:
    """Result of a routing decision."""
    primary_provider: str
    fallback_chain: List[str]
    estimated_tokens: int
    should_chunk: bool
    chunk_size: Optional[int]
    reason: str


class SmartContextRouter:
    """
    Intelligent context-based router for LLM providers.
    
    Routes based on:
    - Estimated context size
    - Step type and complexity
    - Provider capabilities and limits
    - Execution mode (FAST, BUILD, DOUBLE-CHECK)
    
    Thresholds:
    - < 10k tokens: Groq (fast, free tier)
    - 10k - 50k tokens: DeepSeek (balanced quality/cost)
    - > 50k tokens: Gemini (1M+ context, no timeout)
    - Vision tasks: Gemini (multimodal native)
    """
    
    # Token thresholds for provider selection
    THRESHOLD_FAST = 10000      # < 10k: Groq
    THRESHOLD_BALANCED = 50000  # 10k-50k: DeepSeek
    # > 50k: Gemini

    # Chunking threshold - steps above this will be chunked
    # Reduced from 30k to 15k to avoid Gemini timeouts on large plans
    CHUNK_THRESHOLD = 15000
    
    # Max files before considering chunking
    MAX_FILES_BEFORE_CHUNKING = 3
    
    # Expected lines threshold for chunking
    MAX_EXPECTED_LINES = 200
    
    def __init__(self, available_providers: Optional[List[str]] = None):
        """
        Initialize smart context router.
        
        Args:
            available_providers: List of available provider names.
                               If None, uses all configured providers.
        """
        self.available_providers = available_providers or list(PROVIDER_PROFILES.keys())
        self.profiles = {
            name: profile for name, profile in PROVIDER_PROFILES.items()
            if name in self.available_providers
        }
        
        if not self.profiles:
            logger.warning("No providers available, using default cascade")
            self.profiles = PROVIDER_PROFILES
    
    def estimate_tokens(
        self,
        step: Step,
        context: Optional[str] = None,
        loaded_files: Optional[Dict[str, Optional[str]]] = None
    ) -> int:
        """
        Estimate total tokens for a step.
        
        Uses multiple heuristics:
        - step.estimated_tokens if available
        - Context string length
        - Number and size of loaded files
        - Step type and complexity
        
        Args:
            step: Step to estimate
            context: Additional context string
            loaded_files: Dictionary of loaded file contents
            
        Returns:
            Estimated token count
        """
        total_estimate = 0
        
        # Start with step's own estimate if available
        if step.estimated_tokens and step.estimated_tokens > 0:
            total_estimate = max(total_estimate, step.estimated_tokens)
        
        # Add context tokens (roughly 4 chars per token)
        if context:
            context_tokens = len(context) // 4
            total_estimate += context_tokens
        
        # Add file content tokens
        if loaded_files:
            for path, content in loaded_files.items():
                if content:
                    # Rough estimate: 4 chars per token for code
                    file_tokens = len(content) // 4
                    total_estimate += file_tokens
        
        # Adjust based on step type and complexity
        type_multipliers = {
            "code_generation": 1.2,
            "refactoring": 1.0,
            "analysis": 0.8,
            "patch": 0.5,
            "validation": 0.6,
            "review": 0.7,
        }
        multiplier = type_multipliers.get(step.type, 1.0)
        
        # Complexity factor (0.0 - 1.0)
        complexity_factor = 1.0 + (step.complexity * 0.5)
        
        total_estimate = int(total_estimate * multiplier * complexity_factor)
        
        # Add buffer for prompt overhead and response
        total_estimate = int(total_estimate * 1.2) + 500
        
        return max(total_estimate, 1000)  # Minimum 1k tokens
    
    def should_chunk_step(
        self,
        step: Step,
        estimated_tokens: int,
        loaded_files: Optional[Dict[str, Optional[str]]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Determine if a step should be chunked.
        
        Criteria:
        - estimated_tokens > CHUNK_THRESHOLD (30k)
        - Number of input_files > 3
        - code_generation with expected file > 200 lines
        
        Args:
            step: Step to evaluate
            estimated_tokens: Pre-calculated token estimate
            loaded_files: Loaded file contents
            
        Returns:
            Tuple of (should_chunk, reason)
        """
        reasons = []
        
        # Check token threshold
        if estimated_tokens > self.CHUNK_THRESHOLD:
            reasons.append(f"estimated_tokens ({estimated_tokens}) > {self.CHUNK_THRESHOLD}")
        
        # Check number of input files
        if step.context and isinstance(step.context, dict):
            input_files = step.context.get("input_files", [])
            if len(input_files) > self.MAX_FILES_BEFORE_CHUNKING:
                reasons.append(f"input_files ({len(input_files)}) > {self.MAX_FILES_BEFORE_CHUNKING}")
        
        # Check expected file size for code generation
        if step.type == "code_generation":
            # Estimate based on description length and complexity
            desc_words = len(step.description.split())
            estimated_lines = desc_words // 5  # Rough: 5 words per line of code
            
            if estimated_lines > self.MAX_EXPECTED_LINES:
                reasons.append(f"estimated_lines ({estimated_lines}) > {self.MAX_EXPECTED_LINES}")
        
        if reasons:
            return True, "; ".join(reasons)
        
        return False, None
    
    def select_provider_for_tokens(
        self,
        estimated_tokens: int,
        step_type: str = "code_generation",
        requires_vision: bool = False,
        execution_mode: str = "BUILD"
    ) -> RoutingDecision:
        """
        Select provider based on estimated token count.
        
        Args:
            estimated_tokens: Estimated token count
            step_type: Type of step
            requires_vision: Whether step requires vision capabilities
            execution_mode: Execution mode (FAST, BUILD, DOUBLE-CHECK)
            
        Returns:
            RoutingDecision with provider selection and fallback chain
        """
        execution_mode = execution_mode.upper()
        
        # Vision tasks always go to Gemini
        if requires_vision:
            return RoutingDecision(
                primary_provider="gemini",
                fallback_chain=self._get_fallback_chain("gemini", execution_mode),
                estimated_tokens=estimated_tokens,
                should_chunk=estimated_tokens > self.CHUNK_THRESHOLD,
                chunk_size=self._calculate_chunk_size(estimated_tokens) if estimated_tokens > self.CHUNK_THRESHOLD else None,
                reason="Vision/multimodal task requires Gemini"
            )
        
        # FAST mode: prioritize speed
        if execution_mode == "FAST":
            if estimated_tokens < self.THRESHOLD_FAST:
                primary = "groq"
            elif estimated_tokens < self.THRESHOLD_BALANCED:
                primary = "deepseek"
            else:
                primary = "gemini"
        
        # BUILD mode: balanced approach
        elif execution_mode == "BUILD":
            if estimated_tokens < self.THRESHOLD_FAST:
                # Small tasks: Groq or Codestral
                if step_type in ["refactoring", "patch"]:
                    primary = "codestral" if "codestral" in self.available_providers else "groq"
                else:
                    primary = "groq"
            elif estimated_tokens < self.THRESHOLD_BALANCED:
                primary = "deepseek"
            else:
                primary = "gemini"
        
        # DOUBLE-CHECK mode: prioritize quality
        elif execution_mode == "DOUBLE-CHECK":
            if estimated_tokens < self.THRESHOLD_BALANCED:
                primary = "deepseek"
            else:
                primary = "gemini"
        
        # Default to balanced
        else:
            if estimated_tokens < self.THRESHOLD_FAST:
                primary = "groq"
            elif estimated_tokens < self.THRESHOLD_BALANCED:
                primary = "deepseek"
            else:
                primary = "gemini"
        
        # Ensure primary provider is available
        if primary not in self.available_providers:
            primary = self._get_best_available(estimated_tokens)
        
        should_chunk = estimated_tokens > self.CHUNK_THRESHOLD
        chunk_size = self._calculate_chunk_size(estimated_tokens) if should_chunk else None
        
        reason = (
            f"{estimated_tokens} tokens in {execution_mode} mode "
            f"({self._get_size_category(estimated_tokens)})"
        )
        
        return RoutingDecision(
            primary_provider=primary,
            fallback_chain=self._get_fallback_chain(primary, execution_mode),
            estimated_tokens=estimated_tokens,
            should_chunk=should_chunk,
            chunk_size=chunk_size,
            reason=reason
        )
    
    def route_step(
        self,
        step: Step,
        context: Optional[str] = None,
        loaded_files: Optional[Dict[str, Optional[str]]] = None,
        execution_mode: str = "BUILD"
    ) -> RoutingDecision:
        """
        Route a step to appropriate provider with full analysis.
        
        This is the main entry point for routing decisions.
        
        Args:
            step: Step to route
            context: Additional context
            loaded_files: Loaded file contents
            execution_mode: Execution mode
            
        Returns:
            RoutingDecision with complete routing information
        """
        # Estimate tokens
        estimated_tokens = self.estimate_tokens(step, context, loaded_files)
        
        # Check if step requires vision
        requires_vision = self._step_requires_vision(step)
        
        # Get routing decision
        decision = self.select_provider_for_tokens(
            estimated_tokens=estimated_tokens,
            step_type=step.type,
            requires_vision=requires_vision,
            execution_mode=execution_mode
        )
        
        # Check if should chunk
        should_chunk, chunk_reason = self.should_chunk_step(step, estimated_tokens, loaded_files)
        if should_chunk:
            decision.should_chunk = True
            decision.chunk_size = self._calculate_chunk_size(estimated_tokens)
            decision.reason += f"; Chunking: {chunk_reason}"
        
        logger.info(
            f"Smart routing for {step.id}: {decision.primary_provider} "
            f"({decision.estimated_tokens} tokens, {decision.reason})"
        )
        
        return decision
    
    def _get_fallback_chain(
        self,
        primary: str,
        execution_mode: str
    ) -> List[str]:
        """
        Get fallback chain for a primary provider.
        
        Args:
            primary: Primary provider name
            execution_mode: Execution mode
            
        Returns:
            List of fallback provider names in order
        """
        # Default cascade for all modes
        cascade = ["deepseek", "gemini", "codestral"]
        
        # Remove primary from cascade
        if primary in cascade:
            cascade.remove(primary)
        
        # Add primary's alternatives based on tier
        primary_profile = self.profiles.get(primary)
        if primary_profile:
            if primary_profile.tier == ProviderTier.FAST:
                # Fast tier falls back to balanced, then high capacity
                if "deepseek" not in cascade:
                    cascade.insert(0, "deepseek")
            elif primary_profile.tier == ProviderTier.BALANCED:
                # Balanced falls back to high capacity
                if "gemini" not in cascade:
                    cascade.insert(0, "gemini")
        
        # Filter to available providers
        return [p for p in cascade if p in self.available_providers]
    
    def _get_best_available(self, estimated_tokens: int) -> str:
        """Get best available provider for token count."""
        if estimated_tokens < self.THRESHOLD_FAST:
            for provider in ["groq", "codestral", "deepseek", "gemini"]:
                if provider in self.available_providers:
                    return provider
        elif estimated_tokens < self.THRESHOLD_BALANCED:
            for provider in ["deepseek", "gemini", "groq"]:
                if provider in self.available_providers:
                    return provider
        else:
            for provider in ["gemini", "deepseek"]:
                if provider in self.available_providers:
                    return provider
        
        # Fallback to any available
        return self.available_providers[0] if self.available_providers else "gemini"
    
    def _get_size_category(self, tokens: int) -> str:
        """Get size category for token count."""
        if tokens < self.THRESHOLD_FAST:
            return "small"
        elif tokens < self.THRESHOLD_BALANCED:
            return "medium"
        else:
            return "large"
    
    def _step_requires_vision(self, step: Step) -> bool:
        """Check if step requires vision capabilities."""
        if not step.context:
            return False
        
        # Check for vision indicators in context
        vision_indicators = [
            "image", "png", "jpg", "jpeg", "vision", "visual",
            "screenshot", "diagram", "figure", "multimodal"
        ]
        
        context_str = str(step.context).lower()
        step_desc = step.description.lower()
        
        for indicator in vision_indicators:
            if indicator in context_str or indicator in step_desc:
                return True
        
        return False
    
    def _calculate_chunk_size(self, total_tokens: int) -> int:
        """Calculate optimal chunk size for large steps."""
        # Target chunks of ~20k tokens to stay well under limits
        target_chunk = 20000
        
        # Calculate number of chunks needed
        num_chunks = max(2, (total_tokens + target_chunk - 1) // target_chunk)
        
        # Distribute evenly
        return (total_tokens + num_chunks - 1) // num_chunks
    
    def get_provider_limits(self, provider: str) -> Optional[ProviderProfile]:
        """Get limits for a provider."""
        return self.profiles.get(provider)
    
    def validate_routing(
        self,
        decision: RoutingDecision,
        available_providers: List[str]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a routing decision against available providers.
        
        Args:
            decision: RoutingDecision to validate
            available_providers: List of actually available providers
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if decision.primary_provider not in available_providers:
            return False, f"Primary provider {decision.primary_provider} not available"
        
        # Check if fallback chain has any valid providers
        valid_fallbacks = [p for p in decision.fallback_chain if p in available_providers]
        if not valid_fallbacks and len(available_providers) > 1:
            return False, "No valid fallback providers in chain"
        
        return True, None
