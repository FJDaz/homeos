"""Cross-provider fallback cascade with intelligent retry logic.

Provides automatic fallback across multiple providers when:
- Rate limits are hit (429)
- Request too large (413)
- Server errors (5xx)
- Request timeouts
- Provider unavailable
"""
import asyncio
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from loguru import logger


class FailureType(Enum):
    """Types of provider failures."""
    RATE_LIMIT = "rate_limit"          # 429
    TOKEN_LIMIT = "token_limit"        # 413, context too large
    SERVER_ERROR = "server_error"      # 5xx
    TIMEOUT = "timeout"                # Request timeout
    REQUEST_ERROR = "request_error"    # Network/connection error
    UNKNOWN = "unknown"                # Other errors


@dataclass
class ProviderAttempt:
    """Record of a provider attempt."""
    provider: str
    timestamp: datetime
    success: bool
    failure_type: Optional[FailureType] = None
    error_message: Optional[str] = None
    tokens_used: int = 0
    execution_time_ms: float = 0.0
    cost_usd: float = 0.0


@dataclass
class CascadeResult:
    """Result of a cascade execution."""
    success: bool
    output: str
    provider_used: str
    attempts: List[ProviderAttempt]
    total_tokens: int
    total_cost: float
    total_time_ms: float
    fallback_used: bool
    error: Optional[str] = None


@dataclass
class CascadeConfig:
    """Configuration for fallback cascade."""
    # Retry configuration
    max_attempts_per_provider: int = 3
    base_retry_delay: float = 1.0
    max_retry_delay: float = 30.0
    exponential_base: float = 2.0
    
    # Token limits for retry decisions
    token_limit_buffer: float = 0.9  # Retry if using >90% of limit
    
    # Timeout configuration
    default_timeout: float = 120.0  # 2 minutes default
    extended_timeout: float = 300.0  # 5 minutes for large contexts
    
    # Failure handling
    retry_on_server_error: bool = True
    max_server_error_retries: int = 2
    
    # Circuit breaker
    enable_circuit_breaker: bool = True
    circuit_breaker_threshold: int = 5  # Failures before opening
    circuit_breaker_timeout: float = 60.0  # Seconds before trying again


class CircuitBreaker:
    """Simple circuit breaker for provider health."""
    
    def __init__(self, threshold: int = 5, timeout: float = 60.0):
        self.threshold = threshold
        self.timeout = timeout
        self.failures: Dict[str, List[datetime]] = {}
        self.open_circuits: Dict[str, datetime] = {}
    
    def record_failure(self, provider: str) -> None:
        """Record a failure for a provider."""
        now = datetime.now()
        
        if provider not in self.failures:
            self.failures[provider] = []
        
        self.failures[provider].append(now)
        
        # Clean old failures outside window
        cutoff = now.timestamp() - self.timeout
        self.failures[provider] = [
            f for f in self.failures[provider]
            if f.timestamp() > cutoff
        ]
        
        # Check if circuit should open
        if len(self.failures[provider]) >= self.threshold:
            self.open_circuits[provider] = now
            logger.warning(f"Circuit breaker OPEN for {provider}")
    
    def record_success(self, provider: str) -> None:
        """Record a success for a provider."""
        if provider in self.failures:
            self.failures[provider].clear()
        
        if provider in self.open_circuits:
            del self.open_circuits[provider]
            logger.info(f"Circuit breaker CLOSED for {provider}")
    
    def is_open(self, provider: str) -> bool:
        """Check if circuit breaker is open for a provider."""
        if provider not in self.open_circuits:
            return False
        
        # Check if circuit should close
        opened_at = self.open_circuits[provider]
        if (datetime.now() - opened_at).total_seconds() > self.timeout:
            del self.open_circuits[provider]
            self.failures[provider] = []
            logger.info(f"Circuit breaker RESET for {provider}")
            return False
        
        return True


class ProviderFallbackCascade:
    """
    Cross-provider fallback cascade with intelligent retry.
    
    Usage:
        cascade = ProviderFallbackCascade(clients={"groq": groq_client, ...})
        result = await cascade.execute(
            fallback_chain=["groq", "gemini", "deepseek"],
            execute_fn=lambda client: client.generate(prompt)
        )
    """
    
    def __init__(
        self,
        clients: Dict[str, Any],
        config: Optional[CascadeConfig] = None
    ):
        """
        Initialize fallback cascade.
        
        Args:
            clients: Dictionary of provider name -> client instance
            config: Cascade configuration (uses defaults if None)
        """
        self.clients = clients
        self.config = config or CascadeConfig()
        self.circuit_breaker = CircuitBreaker(
            threshold=self.config.circuit_breaker_threshold,
            timeout=self.config.circuit_breaker_timeout
        )
        
        # Track attempts for analytics
        self.attempt_history: List[ProviderAttempt] = []
    
    def classify_error(self, error: Exception) -> FailureType:
        """
        Classify an error into a failure type.
        
        Args:
            error: The exception that occurred
            
        Returns:
            FailureType classification
        """
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        # Rate limit indicators
        rate_limit_indicators = [
            "429", "rate limit", "rate_limit", "too many requests",
            "throttled", "quota exceeded"
        ]
        for indicator in rate_limit_indicators:
            if indicator in error_str:
                return FailureType.RATE_LIMIT
        
        # Token limit indicators
        token_limit_indicators = [
            "413", "request too large", "context length", "token limit",
            "maximum context", "too large for model"
        ]
        for indicator in token_limit_indicators:
            if indicator in error_str:
                return FailureType.TOKEN_LIMIT
        
        # Timeout indicators
        timeout_indicators = [
            "timeout", "timed out", "deadline exceeded"
        ]
        for indicator in timeout_indicators:
            if indicator in error_str or "timeout" in error_type:
                return FailureType.TIMEOUT
        
        # Server error indicators
        server_error_indicators = [
            "500", "502", "503", "504", "server error",
            "bad gateway", "service unavailable"
        ]
        for indicator in server_error_indicators:
            if indicator in error_str:
                return FailureType.SERVER_ERROR
        
        # Request error indicators
        request_error_indicators = [
            "connection", "network", "request error", "httpx"
        ]
        for indicator in request_error_indicators:
            if indicator in error_str or indicator in error_type:
                return FailureType.REQUEST_ERROR
        
        return FailureType.UNKNOWN
    
    def should_retry(
        self,
        failure_type: FailureType,
        attempt: int,
        provider: str
    ) -> Tuple[bool, float]:
        """
        Determine if a failed request should be retried.
        
        Args:
            failure_type: Type of failure
            attempt: Current attempt number (0-indexed)
            provider: Provider name
            
        Returns:
            Tuple of (should_retry, delay_seconds)
        """
        # Don't retry token limits - move to next provider
        if failure_type == FailureType.TOKEN_LIMIT:
            return False, 0.0
        
        # Don't retry if max attempts reached
        if attempt >= self.config.max_attempts_per_provider - 1:
            return False, 0.0
        
        # Calculate delay
        delay = min(
            self.config.base_retry_delay * (self.config.exponential_base ** attempt),
            self.config.max_retry_delay
        )
        
        # Retry rate limits with backoff
        if failure_type == FailureType.RATE_LIMIT:
            return True, delay * 2  # Double delay for rate limits
        
        # Retry server errors if configured
        if failure_type == FailureType.SERVER_ERROR:
            if attempt < self.config.max_server_error_retries:
                return True, delay
            return False, 0.0
        
        # Retry timeouts
        if failure_type == FailureType.TIMEOUT:
            return True, delay
        
        # Retry request errors
        if failure_type == FailureType.REQUEST_ERROR:
            return True, delay
        
        # Don't retry unknown errors
        return False, 0.0
    
    async def execute_with_provider(
        self,
        provider: str,
        execute_fn: Callable[[Any], Any],
        timeout: Optional[float] = None
    ) -> Tuple[bool, Any, Optional[Exception]]:
        """
        Execute with a single provider with retries.
        
        Args:
            provider: Provider name
            execute_fn: Function that takes client and returns coroutine
            timeout: Timeout for this execution
            
        Returns:
            Tuple of (success, result_or_none, error_or_none)
        """
        if provider not in self.clients:
            return False, None, Exception(f"Provider {provider} not available")
        
        client = self.clients[provider]
        timeout = timeout or self.config.default_timeout
        
        for attempt in range(self.config.max_attempts_per_provider):
            try:
                # Check circuit breaker
                if self.config.enable_circuit_breaker and self.circuit_breaker.is_open(provider):
                    logger.warning(f"Circuit breaker open for {provider}, skipping")
                    continue
                
                # Execute with timeout
                result = await asyncio.wait_for(
                    execute_fn(client),
                    timeout=timeout
                )
                
                # Record success
                self.circuit_breaker.record_success(provider)
                
                return True, result, None
                
            except asyncio.TimeoutError as e:
                error = Exception(f"Timeout after {timeout}s")
                failure_type = FailureType.TIMEOUT
                
            except Exception as e:
                error = e
                failure_type = self.classify_error(e)
            
            # Record failure
            self.circuit_breaker.record_failure(provider)
            
            # Determine if we should retry
            should_retry, delay = self.should_retry(failure_type, attempt, provider)
            
            if should_retry:
                logger.warning(
                    f"{provider} failed with {failure_type.value}, "
                    f"retrying in {delay:.1f}s (attempt {attempt + 1}/{self.config.max_attempts_per_provider})"
                )
                await asyncio.sleep(delay)
            else:
                logger.warning(
                    f"{provider} failed with {failure_type.value}, "
                    f"not retrying: {error}"
                )
                return False, None, error
        
        # All retries exhausted
        return False, None, error
    
    async def execute(
        self,
        fallback_chain: List[str],
        execute_fn: Callable[[Any], Any],
        timeout: Optional[float] = None,
        context_size: Optional[int] = None
    ) -> CascadeResult:
        """
        Execute with fallback cascade.
        
        Args:
            fallback_chain: Ordered list of providers to try
            execute_fn: Function that takes a client and returns a coroutine
            timeout: Timeout per provider attempt
            context_size: Optional context size for logging
            
        Returns:
            CascadeResult with execution results
        """
        start_time = datetime.now()
        attempts: List[ProviderAttempt] = []
        
        # Adjust timeout for large contexts
        if context_size and context_size > 30000:
            timeout = timeout or self.config.extended_timeout
            logger.info(f"Using extended timeout ({timeout}s) for large context ({context_size} tokens)")
        
        for provider in fallback_chain:
            if provider not in self.clients:
                logger.debug(f"Provider {provider} not in clients, skipping")
                continue
            
            logger.info(f"Trying provider: {provider}")
            
            success, result, error = await self.execute_with_provider(
                provider=provider,
                execute_fn=execute_fn,
                timeout=timeout
            )
            
            # Record attempt
            attempt = ProviderAttempt(
                provider=provider,
                timestamp=datetime.now(),
                success=success,
                failure_type=self.classify_error(error) if error else None,
                error_message=str(error) if error else None,
                tokens_used=getattr(result, 'tokens_used', 0) if success else 0,
                execution_time_ms=getattr(result, 'execution_time_ms', 0) if success else 0,
                cost_usd=getattr(result, 'cost_usd', 0.0) if success else 0.0
            )
            attempts.append(attempt)
            self.attempt_history.append(attempt)
            
            if success:
                total_time = (datetime.now() - start_time).total_seconds() * 1000
                
                logger.info(
                    f"Success with {provider}: "
                    f"{attempt.tokens_used} tokens, ${attempt.cost_usd:.4f}, "
                    f"{attempt.execution_time_ms:.0f}ms"
                )
                
                return CascadeResult(
                    success=True,
                    output=getattr(result, 'code', str(result)),
                    provider_used=provider,
                    attempts=attempts,
                    total_tokens=attempt.tokens_used,
                    total_cost=attempt.cost_usd,
                    total_time_ms=total_time,
                    fallback_used=len(attempts) > 1
                )
            else:
                logger.warning(f"{provider} failed: {attempt.error_message}")
        
        # All providers failed
        total_time = (datetime.now() - start_time).total_seconds() * 1000
        
        logger.error(f"All providers in cascade failed after {len(attempts)} attempts")
        
        return CascadeResult(
            success=False,
            output="",
            provider_used="",
            attempts=attempts,
            total_tokens=0,
            total_cost=0.0,
            total_time_ms=total_time,
            fallback_used=len(attempts) > 1,
            error=f"All providers failed. Last error: {attempts[-1].error_message if attempts else 'Unknown'}"
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cascade statistics."""
        if not self.attempt_history:
            return {"total_attempts": 0}
        
        total = len(self.attempt_history)
        successful = sum(1 for a in self.attempt_history if a.success)
        
        by_provider: Dict[str, Dict[str, int]] = {}
        for attempt in self.attempt_history:
            if attempt.provider not in by_provider:
                by_provider[attempt.provider] = {"success": 0, "failure": 0}
            if attempt.success:
                by_provider[attempt.provider]["success"] += 1
            else:
                by_provider[attempt.provider]["failure"] += 1
        
        by_failure_type: Dict[str, int] = {}
        for attempt in self.attempt_history:
            if attempt.failure_type:
                ft = attempt.failure_type.value
                by_failure_type[ft] = by_failure_type.get(ft, 0) + 1
        
        return {
            "total_attempts": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": successful / total if total > 0 else 0,
            "by_provider": by_provider,
            "by_failure_type": by_failure_type,
            "open_circuits": list(self.circuit_breaker.open_circuits.keys())
        }
    
    def reset_stats(self) -> None:
        """Reset attempt history."""
        self.attempt_history.clear()
