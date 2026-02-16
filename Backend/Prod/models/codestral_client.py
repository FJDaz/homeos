"""Codestral (Mistral) API client for code generation."""
import asyncio
import time
from typing import List, Optional, Dict, Any
import httpx
from loguru import logger

from ..config.settings import settings
from .base_client import BaseLLMClient, GenerationResult


class CodestralClient(BaseLLMClient):
    """Async client for Codestral (Mistral) API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None
    ):
        """
        Initialize Codestral client.

        Args:
            api_key: Mistral API key (defaults to settings)
            api_url: API endpoint URL (defaults to settings)
            model: Model name (defaults to settings)
            timeout: Request timeout in seconds (defaults to settings)
            max_retries: Maximum retry attempts (defaults to settings)
        """
        self.api_key = api_key or settings.mistral_api_key
        self.api_url = api_url or settings.mistral_api_url
        self.model = model or settings.codestral_model
        self.timeout = timeout or settings.timeout
        self.max_retries = max_retries or settings.max_retries

        if not self.api_key:
            raise ValueError("Mistral API key is required")

        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )

    @property
    def name(self) -> str:
        """Provider name."""
        return "codestral"

    @property
    def specialties(self) -> List[str]:
        """List of specialties for this provider."""
        return [
            "fim",
            "code_completion",
            "refactoring",
            "local_edit"
        ]

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def check_balance(self) -> Optional[float]:
        """
        Check account balance (if API supports it).

        Note: Mistral API does not currently provide a balance endpoint.
        This method returns None to indicate balance check is not supported.

        Returns:
            None (balance check not supported for Mistral)
        """
        if not self._should_check_balance():
            return None

        # Mistral API does not provide a balance endpoint
        logger.debug("Balance check not supported for Mistral/Codestral API")
        return None

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
        Generate code from a prompt (BaseLLMClient interface).

        Args:
            prompt: The task description
            context: Additional context (framework, language, etc.)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            GenerationResult with the generated code
        """
        start_time = time.time()

        # Build full prompt
        full_prompt = self._build_prompt(prompt, context, output_constraint)

        # Prepare messages; inject surgical system prompt if needed
        messages = []
        if output_constraint == "json_surgical":
            from ..core.prompts.surgical_protocol import SURGICAL_SYSTEM_PROMPT
            messages.append({
                "role": "system",
                "content": SURGICAL_SYSTEM_PROMPT.format(ast_summary="[AST context provided in task prompt]")
            })
        messages.append({"role": "user", "content": full_prompt})

        # Prepare request
        request_data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens or settings.max_tokens,
            "temperature": temperature or settings.temperature
        }

        # Execute with retries
        last_error = None
        backoff = 1.0

        for attempt in range(self.max_retries + 1):
            try:
                response = await self.client.post(
                    self.api_url,
                    json=request_data
                )
                response.raise_for_status()

                result_data = response.json()

                # Extract response
                content = result_data["choices"][0]["message"]["content"]
                usage = result_data.get("usage", {})
                input_tokens = usage.get("prompt_tokens", 0)
                output_tokens = usage.get("completion_tokens", 0)
                total_tokens = usage.get("total_tokens", input_tokens + output_tokens)

                # Calculate cost
                cost = self._calculate_cost(input_tokens, output_tokens)

                # Calculate execution time
                execution_time_ms = (time.time() - start_time) * 1000

                logger.info(
                    f"Generation completed: {total_tokens} tokens, "
                    f"${cost:.4f}, {execution_time_ms:.0f}ms"
                )

                return GenerationResult(
                    success=True,
                    code=content,
                    tokens_used=total_tokens,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost_usd=cost,
                    execution_time_ms=execution_time_ms,
                    provider=self.name
                )

            except httpx.HTTPStatusError as e:
                last_error = f"HTTP {e.response.status_code}: {e.response.text}"
                logger.warning(f"Generation attempt {attempt + 1} failed: {last_error}")

                if e.response.status_code == 429:  # Rate limit
                    wait_time = backoff
                    logger.info(f"Rate limited, waiting {wait_time}s before retry")
                    await asyncio.sleep(wait_time)
                    backoff = min(backoff * 2, 10.0)
                elif e.response.status_code >= 500:  # Server error
                    if attempt < self.max_retries:
                        await asyncio.sleep(backoff)
                        backoff = min(backoff * 2, 10.0)
                        continue
                else:
                    break

            except httpx.RequestError as e:
                last_error = f"Request error: {str(e)}"
                logger.warning(f"Generation attempt {attempt + 1} failed: {last_error}")

                if attempt < self.max_retries:
                    await asyncio.sleep(backoff)
                    backoff = min(backoff * 2, 10.0)
                    continue
                else:
                    break

            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
                logger.error(f"Generation failed with unexpected error: {last_error}")
                break

        # All retries failed
        execution_time_ms = (time.time() - start_time) * 1000

        logger.error(f"Generation failed after {self.max_retries + 1} attempts: {last_error}")

        return GenerationResult(
            success=False,
            code="",
            tokens_used=0,
            input_tokens=0,
            output_tokens=0,
            cost_usd=0.0,
            execution_time_ms=execution_time_ms,
            error=last_error,
            provider=self.name
        )

    def _build_prompt(self, prompt: str, context: Optional[str] = None, output_constraint: Optional[str] = None) -> str:
        """
        Build prompt from task and context.

        Args:
            prompt: Task description
            context: Additional context
            output_constraint: Optional constraint on output format

        Returns:
            Formatted prompt string
        """
        base_prompt = f"Task: {prompt}\n\n"
        
        if output_constraint:
            if output_constraint == "Code only":
                base_prompt += "Generate only code, no explanations or prose."
            elif output_constraint == "JSON only":
                base_prompt += "Generate only valid JSON, no explanations."
            elif output_constraint == "No prose":
                base_prompt += "Generate output without prose or explanations."
            else:
                base_prompt += f"Output constraint: {output_constraint}"
        else:
            base_prompt += "Generate the complete code implementation."
        
        if context:
            return f"Context: {context}\n\n{base_prompt}"
        return base_prompt

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate cost based on token usage.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost in USD
        """
        input_cost = (input_tokens / 1000) * settings.mistral_input_cost_per_1k
        output_cost = (output_tokens / 1000) * settings.mistral_output_cost_per_1k
        return input_cost + output_cost
