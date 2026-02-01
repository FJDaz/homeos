"""Claude API client for planning and review."""
import asyncio
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import httpx
from loguru import logger

from ..config.settings import settings
from .base_client import BaseLLMClient, GenerationResult


@dataclass
class ClaudeGenerationResult:
    """Result of Claude API generation."""
    success: bool
    content: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    execution_time_ms: float
    error: Optional[str] = None


class ClaudeClient(BaseLLMClient):
    """Async client for Claude API (Sonnet 3.5)."""
    
    # Claude API pricing (Sonnet 3.5)
    INPUT_COST_PER_1M = 3.00  # $3.00 per million input tokens
    OUTPUT_COST_PER_1M = 15.00  # $15.00 per million output tokens
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None
    ):
        """
        Initialize Claude client.
        
        Args:
            api_key: Anthropic API key (defaults to settings)
            model: Model name (defaults to claude-3-5-sonnet-20241022)
            timeout: Request timeout in seconds (defaults to settings)
            max_retries: Maximum retry attempts (defaults to settings)
        """
        self.api_key = api_key or settings.anthropic_api_key
        self.model = model or "claude-3-5-sonnet-20241022"
        self.timeout = timeout or settings.timeout
        self.max_retries = max_retries or settings.max_retries
        
        if not self.api_key:
            raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY in .env")
        
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
        )
        
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost_usd = 0.0
    
    @property
    def name(self) -> str:
        """Provider name."""
        return "claude"
    
    @property
    def specialties(self) -> List[str]:
        """List of specialties for this provider."""
        return [
            "planning",
            "review",
            "code_analysis",
            "mentor_feedback"
        ]
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost in USD."""
        input_cost = (input_tokens / 1_000_000) * self.INPUT_COST_PER_1M
        output_cost = (output_tokens / 1_000_000) * self.OUTPUT_COST_PER_1M
        return input_cost + output_cost
    
    async def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None,
        cache_params: Optional[Dict[str, Any]] = None,
        output_constraint: Optional[str] = None
    ) -> GenerationResult:
        """
        Generate content with Claude Sonnet.
        
        Args:
            prompt: The task description
            context: Additional context (framework, language, etc.)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system_prompt: System prompt for Claude
            cache_params: Optional cache control parameters (not used for Claude)
            output_constraint: Optional constraint on output format
            
        Returns:
            GenerationResult with the generated content
        """
        start_time = time.time()
        
        # Build messages
        messages = []
        if context:
            messages.append({
                "role": "user",
                "content": f"Context: {context}\n\nTask: {prompt}"
            })
        else:
            messages.append({
                "role": "user",
                "content": prompt
            })
        
        # Build request payload
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens or settings.max_tokens,
            "temperature": temperature or settings.temperature
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        # Retry logic
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = await self.client.post(self.api_url, json=payload)
                response.raise_for_status()
                
                data = response.json()
                
                # Extract content and tokens
                content = data["content"][0]["text"]
                input_tokens = data["usage"]["input_tokens"]
                output_tokens = data["usage"]["output_tokens"]
                
                # Calculate cost
                cost = self._calculate_cost(input_tokens, output_tokens)
                
                # Update totals
                self.total_input_tokens += input_tokens
                self.total_output_tokens += output_tokens
                self.total_cost_usd += cost
                
                execution_time_ms = (time.time() - start_time) * 1000
                
                logger.info(
                    f"Claude API: {input_tokens} input + {output_tokens} output tokens, "
                    f"cost ${cost:.4f}, time {execution_time_ms:.0f}ms"
                )
                
                return GenerationResult(
                    success=True,
                    code=content,  # Claude returns text, not just code
                    tokens_used=input_tokens + output_tokens,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost_usd=cost,
                    execution_time_ms=execution_time_ms,
                    provider="claude"
                )
                
            except httpx.HTTPStatusError as e:
                last_error = f"HTTP {e.response.status_code}: {e.response.text}"
                if e.response.status_code == 429:  # Rate limit
                    wait_time = 2 ** attempt
                    logger.warning(f"Rate limited, waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
                elif e.response.status_code >= 500:  # Server error
                    wait_time = 2 ** attempt
                    logger.warning(f"Server error, waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
                else:
                    break  # Client error, don't retry
            except Exception as e:
                last_error = str(e)
                logger.error(f"Claude API error: {e}")
                break
        
        execution_time_ms = (time.time() - start_time) * 1000
        
        return GenerationResult(
            success=False,
            code="",
            tokens_used=0,
            input_tokens=0,
            output_tokens=0,
            cost_usd=0.0,
            execution_time_ms=execution_time_ms,
            error=last_error or "Unknown error",
            provider="claude"
        )
    
    async def check_balance(self) -> Optional[float]:
        """
        Check account balance (if API supports it).
        
        Note: Anthropic API doesn't provide a direct balance endpoint.
        This method returns None as balance checking isn't supported.
        
        Returns:
            None (not supported by Anthropic API)
        """
        return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get usage metrics."""
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_cost_usd": self.total_cost_usd,
            "model": self.model
        }
