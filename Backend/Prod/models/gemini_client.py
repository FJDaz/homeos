"""Gemini (Google) API client for code generation and analysis."""
import asyncio
import time
from typing import List, Optional, Dict, Any
import httpx
from loguru import logger

from ..config.settings import settings
from .base_client import BaseLLMClient, GenerationResult


class GeminiClient(BaseLLMClient):
    """Async client for Google Gemini API with automatic fallback cascade."""
    
    # Cascade de fallback pour mode FAST (priorité vitesse)
    FALLBACK_MODELS_FAST = [
        # Fastest models first
        "gemini-2.5-flash-lite",         # Fastest and most cost-efficient
        "gemini-2.5-flash",              # Fast, good price-performance
        "gemini-2.0-flash",              # Fast (deprecated March 2026)
        "gemini-2.5-flash-lite-preview-09-2025",
        "gemini-3-flash-preview",        # Latest fast preview
        "gemini-2.5-flash-preview-09-2025",
        # More capable models (fallback)
        "gemini-2.5-pro",                # More capable but slower
        "gemini-3-pro-preview",          # Most capable preview
        # Experimental (last resort)
        "gemini-2.0-flash-exp",          # Experimental
    ]
    
    # Cascade de fallback pour mode BUILD/PROD (priorité vitesse)
    FALLBACK_MODELS_BUILD = [
        # Fastest models first
        "gemini-2.5-flash-lite",         # Fastest and most cost-efficient
        "gemini-2.5-flash",              # Fast, good price-performance
        "gemini-2.0-flash",              # Fast (deprecated March 2026)
        "gemini-3-flash-preview",        # Latest balanced preview
        "gemini-2.5-flash-preview-09-2025",
        "gemini-2.5-flash-lite-preview-09-2025",
        # More capable models (fallback)
        "gemini-2.5-pro",                # Most capable stable
        "gemini-3-pro-preview",          # Most capable preview
        # Experimental (last resort)
        "gemini-2.0-flash-exp",          # Experimental
    ]
    
    # Cascade par défaut (priorité vitesse)
    FALLBACK_MODELS_DEFAULT = [
        # Fastest models first
        "gemini-2.5-flash-lite",         # Fastest and most cost-efficient
        "gemini-2.5-flash",              # Fast, good price-performance
        "gemini-2.0-flash",              # Stable (deprecated March 2026)
        "gemini-2.5-pro",                # Most capable
        # Preview models
        "gemini-3-flash-preview",        # Latest preview
        "gemini-3-pro-preview",          # Latest preview (most capable)
        "gemini-2.5-flash-preview-09-2025",
        "gemini-2.5-flash-lite-preview-09-2025",
        # Experimental models (last resort)
        "gemini-2.0-flash-exp",          # Experimental
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        execution_mode: Optional[str] = None
    ):
        """
        Initialize Gemini client with fallback cascade.

        Args:
            api_key: Google API key (defaults to settings)
            api_url: API endpoint URL (defaults to settings)
            model: Primary model name (defaults to settings, will fallback if unavailable)
            timeout: Request timeout in seconds (defaults to settings)
            max_retries: Maximum retry attempts per model (defaults to settings)
            execution_mode: Execution mode (FAST, BUILD, DOUBLE-CHECK) - affects fallback order
        """
        self.api_key = api_key or settings.google_api_key
        self.base_url = api_url or settings.gemini_api_url
        self.primary_model = model or settings.gemini_model
        self.timeout = timeout or settings.timeout
        self.max_retries = max_retries or settings.max_retries
        self.execution_mode = (execution_mode or "BUILD").upper()

        if not self.api_key:
            raise ValueError("Google API key is required for Gemini")

        # Select fallback cascade based on execution mode
        if self.execution_mode == "FAST":
            fallback_cascade = self.FALLBACK_MODELS_FAST
            logger.debug("Using FAST mode cascade (prioritizing speed)")
        elif self.execution_mode in ["BUILD", "PROD", "FULL"]:
            fallback_cascade = self.FALLBACK_MODELS_BUILD
            logger.debug("Using BUILD/PROD mode cascade (prioritizing capability)")
        else:
            fallback_cascade = self.FALLBACK_MODELS_DEFAULT
            logger.debug("Using default cascade (balanced)")

        # Build fallback model list: primary model first, then fallback cascade
        self.fallback_models = [self.primary_model]
        for fallback_model in fallback_cascade:
            if fallback_model != self.primary_model:
                self.fallback_models.append(fallback_model)

        logger.info(
            f"GeminiClient initialized with primary model: {self.primary_model} "
            f"(mode: {self.execution_mode})"
        )
        logger.debug(f"Fallback cascade ({len(self.fallback_models)} models): {self.fallback_models}")

        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={"Content-Type": "application/json"}
        )

    @property
    def name(self) -> str:
        """Provider name."""
        return "gemini"

    @property
    def specialties(self) -> List[str]:
        """List of specialties for this provider."""
        return [
            "analysis",
            "parsing",
            "explanation",
            "documentation",
            "code_review"
        ]

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def check_balance(self) -> Optional[float]:
        """
        Check account balance (if API supports it).

        Note: Gemini API does not provide a balance endpoint.
        Gemini has a free tier with quota limits.

        Returns:
            None (balance check not applicable for Gemini free tier)
        """
        if not self._should_check_balance():
            return None

        logger.debug("Balance check not applicable for Gemini (free tier with quota)")
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
        Generate code/text from a prompt with automatic fallback cascade.

        Tries models in order: primary model → fallback cascade.
        Falls back to next model on 404 (model not found) or 429 (rate limit).

        Args:
            prompt: The task description
            context: Additional context (framework, language, etc.)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            cache_params: Optional cache control parameters (Gemini supports cached_content)

        Returns:
            GenerationResult with the generated content
        """
        start_time = time.time()

        # Build full prompt
        full_prompt = self._build_prompt(prompt, context, output_constraint)

        # Prepare request for Gemini API format
        request_data = {
            "contents": [
                {
                    "parts": [
                        {"text": full_prompt}
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": max_tokens or settings.max_tokens,
                "temperature": temperature or settings.temperature
            }
        }
        
        # response_mime_type not supported by current Gemini REST API; rely on prompt for JSON

        # Try each model in fallback cascade
        last_error = None
        last_model_used = None

        for model_idx, model_name in enumerate(self.fallback_models):
            # Build API URL for this model
            api_url = f"{self.base_url}/{model_name}:generateContent?key={self.api_key}"
            
            logger.debug(f"Trying Gemini model {model_idx + 1}/{len(self.fallback_models)}: {model_name}")
            
            backoff = 1.0
            model_failed = False

            # Retry logic for this specific model
            for attempt in range(self.max_retries + 1):
                try:
                    response = await self.client.post(
                        api_url,
                        json=request_data
                    )
                    response.raise_for_status()

                    result_data = response.json()

                    # Extract response from Gemini format
                    candidates = result_data.get("candidates", [])
                    if not candidates:
                        raise ValueError("No candidates in Gemini response")

                    content = candidates[0].get("content", {})
                    parts = content.get("parts", [])
                    if not parts:
                        raise ValueError("No parts in Gemini response")

                    text_content = parts[0].get("text", "")

                    # Extract token usage from usageMetadata
                    usage = result_data.get("usageMetadata", {})
                    input_tokens = usage.get("promptTokenCount", 0)
                    output_tokens = usage.get("candidatesTokenCount", 0)
                    total_tokens = usage.get("totalTokenCount", input_tokens + output_tokens)

                    # Calculate cost
                    cost = self._calculate_cost(input_tokens, output_tokens)

                    # Calculate execution time
                    execution_time_ms = (time.time() - start_time) * 1000

                    if model_name != self.primary_model:
                        logger.info(
                            f"Generation succeeded with fallback model '{model_name}' "
                            f"(primary '{self.primary_model}' unavailable): "
                            f"{total_tokens} tokens, ${cost:.4f}, {execution_time_ms:.0f}ms"
                        )
                    else:
                        logger.info(
                            f"Generation completed with primary model: "
                            f"{total_tokens} tokens, ${cost:.4f}, {execution_time_ms:.0f}ms"
                        )

                    return GenerationResult(
                        success=True,
                        code=text_content,
                        tokens_used=total_tokens,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        cost_usd=cost,
                        execution_time_ms=execution_time_ms,
                        provider=f"{self.name}:{model_name}"
                    )

                except httpx.HTTPStatusError as e:
                    error_text = e.response.text
                    status_code = e.response.status_code
                    last_error = f"HTTP {status_code}: {error_text}"
                    
                    # 404 = Model not found → try next model in cascade
                    if status_code == 404:
                        logger.warning(
                            f"Model '{model_name}' not found (404), "
                            f"falling back to next model in cascade"
                        )
                        model_failed = True
                        break  # Exit retry loop, try next model
                    
                    # 429 = Rate limit → try next model (or wait and retry)
                    elif status_code == 429:
                        if attempt < self.max_retries:
                            wait_time = backoff
                            logger.info(
                                f"Rate limited on '{model_name}', "
                                f"waiting {wait_time}s before retry"
                            )
                            await asyncio.sleep(wait_time)
                            backoff = min(backoff * 2, 30.0)
                            continue
                        else:
                            # Max retries reached for rate limit → try next model
                            logger.warning(
                                f"Rate limit exceeded on '{model_name}' after {self.max_retries + 1} attempts, "
                                f"falling back to next model"
                            )
                            model_failed = True
                            break
                    
                    # 500+ = Server error → retry same model
                    elif status_code >= 500:
                        if attempt < self.max_retries:
                            logger.warning(
                                f"Server error on '{model_name}' (attempt {attempt + 1}), retrying..."
                            )
                            await asyncio.sleep(backoff)
                            backoff = min(backoff * 2, 10.0)
                            continue
                        else:
                            # Max retries reached → try next model
                            logger.warning(
                                f"Server error on '{model_name}' after {self.max_retries + 1} attempts, "
                                f"falling back to next model"
                            )
                            model_failed = True
                            break
                    
                    # Other 4xx errors → try next model
                    else:
                        logger.warning(
                            f"Error {status_code} on '{model_name}': {error_text[:200]}, "
                            f"falling back to next model"
                        )
                        model_failed = True
                        break

                except httpx.RequestError as e:
                    err_msg = str(e) or f"{type(e).__name__}"
                    last_error = f"Request error: {err_msg}"
                    logger.warning(
                        f"Request error on '{model_name}' (attempt {attempt + 1}): {last_error}"
                    )

                    if attempt < self.max_retries:
                        await asyncio.sleep(backoff)
                        backoff = min(backoff * 2, 10.0)
                        continue
                    else:
                        # Max retries reached → try next model
                        model_failed = True
                        break

                except Exception as e:
                    last_error = f"Unexpected error: {str(e)}"
                    logger.error(
                        f"Unexpected error on '{model_name}': {last_error}, "
                        f"falling back to next model"
                    )
                    model_failed = True
                    break

            # If model failed and we have more models to try, continue to next
            if model_failed and model_idx < len(self.fallback_models) - 1:
                last_model_used = model_name
                continue
            elif model_failed:
                # Last model failed, exit loop
                break

        # All models in cascade failed
        execution_time_ms = (time.time() - start_time) * 1000

        logger.error(
            f"Generation failed after trying {len(self.fallback_models)} models: {last_error}"
        )

        return GenerationResult(
            success=False,
            code="",
            tokens_used=0,
            input_tokens=0,
            output_tokens=0,
            cost_usd=0.0,
            execution_time_ms=execution_time_ms,
            error=f"All {len(self.fallback_models)} Gemini models failed. Last error: {last_error}",
            provider=self.name
        )

    async def generate_with_image(
        self,
        prompt: str,
        image_base64: str,
        mime_type: str = "image/png",
        output_constraint: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> GenerationResult:
        """
        Generate from prompt + image (multimodal). Uses same cascade and retries as generate().

        Args:
            prompt: Task description (e.g. audit instructions).
            image_base64: Base64-encoded image data.
            mime_type: Image MIME type (default image/png).
            output_constraint: Optional "JSON only" etc.
            max_tokens: Max output tokens.
            temperature: Sampling temperature.

        Returns:
            GenerationResult with model output (e.g. JSON string).
        """
        start_time = time.time()
        request_data: Dict[str, Any] = {
            "contents": [
                {
                    "parts": [
                        {"inlineData": {"mimeType": mime_type, "data": image_base64}},
                        {"text": prompt},
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": max_tokens or settings.max_tokens,
                "temperature": temperature if temperature is not None else settings.temperature,
            },
        }
        # Note: responseMimeType not supported by REST API; use prompt engineering for JSON

        last_error: Optional[str] = None
        last_model_used: Optional[str] = None

        for model_idx, model_name in enumerate(self.fallback_models):
            api_url = f"{self.base_url}/{model_name}:generateContent?key={self.api_key}"
            logger.debug(
                f"Trying Gemini Vision model {model_idx + 1}/{len(self.fallback_models)}: {model_name}"
            )
            backoff = 1.0
            model_failed = False

            for attempt in range(self.max_retries + 1):
                try:
                    response = await self.client.post(api_url, json=request_data)
                    response.raise_for_status()
                    result_data = response.json()

                    candidates = result_data.get("candidates", [])
                    if not candidates:
                        raise ValueError("No candidates in Gemini response")
                    content = candidates[0].get("content", {})
                    parts = content.get("parts", [])
                    if not parts:
                        raise ValueError("No parts in Gemini response")
                    text_content = parts[0].get("text", "")

                    usage = result_data.get("usageMetadata", {})
                    input_tokens = usage.get("promptTokenCount", 0)
                    output_tokens = usage.get("candidatesTokenCount", 0)
                    total_tokens = usage.get("totalTokenCount", input_tokens + output_tokens)
                    cost = self._calculate_cost(input_tokens, output_tokens)
                    execution_time_ms = (time.time() - start_time) * 1000

                    if model_name != self.primary_model:
                        logger.info(
                            f"Vision generation succeeded with fallback '{model_name}': "
                            f"{total_tokens} tokens, ${cost:.4f}, {execution_time_ms:.0f}ms"
                        )
                    else:
                        logger.info(
                            f"Vision generation completed: {total_tokens} tokens, "
                            f"${cost:.4f}, {execution_time_ms:.0f}ms"
                        )

                    return GenerationResult(
                        success=True,
                        code=text_content,
                        tokens_used=total_tokens,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        cost_usd=cost,
                        execution_time_ms=execution_time_ms,
                        provider=f"{self.name}:{model_name}",
                    )
                except httpx.HTTPStatusError as e:
                    error_text = e.response.text
                    status_code = e.response.status_code
                    last_error = f"HTTP {status_code}: {error_text}"
                    if status_code == 404:
                        logger.warning(
                            f"Model '{model_name}' not found (404), falling back to next"
                        )
                        model_failed = True
                        break
                    if status_code == 429:
                        if attempt < self.max_retries:
                            wait_time = backoff
                            logger.info(
                                f"Rate limited on '{model_name}', waiting {wait_time}s"
                            )
                            await asyncio.sleep(wait_time)
                            backoff = min(backoff * 2, 30.0)
                            continue
                        logger.warning(
                            f"Rate limit on '{model_name}' after retries, falling back"
                        )
                        model_failed = True
                        break
                    if status_code >= 500:
                        if attempt < self.max_retries:
                            await asyncio.sleep(backoff)
                            backoff = min(backoff * 2, 10.0)
                            continue
                        model_failed = True
                        break
                    logger.warning(
                        f"Error {status_code} on '{model_name}': {error_text[:200]}, "
                        "falling back"
                    )
                    model_failed = True
                    break
                except httpx.RequestError as e:
                    last_error = str(e)
                    if attempt < self.max_retries:
                        await asyncio.sleep(backoff)
                        backoff = min(backoff * 2, 10.0)
                        continue
                    model_failed = True
                    break
                except Exception as e:
                    last_error = str(e)
                    logger.error(f"Unexpected error on '{model_name}': {last_error}")
                    model_failed = True
                    break

            if model_failed and model_idx < len(self.fallback_models) - 1:
                last_model_used = model_name
                continue
            if model_failed:
                break

        execution_time_ms = (time.time() - start_time) * 1000
        logger.error(
            f"Vision generation failed after {len(self.fallback_models)} models: {last_error}"
        )
        return GenerationResult(
            success=False,
            code="",
            tokens_used=0,
            input_tokens=0,
            output_tokens=0,
            cost_usd=0.0,
            execution_time_ms=execution_time_ms,
            error=f"All Gemini vision models failed. Last: {last_error}",
            provider=self.name,
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
            Cost in USD (0.0 for free tier)
        """
        input_cost = (input_tokens / 1000) * settings.gemini_input_cost_per_1k
        output_cost = (output_tokens / 1000) * settings.gemini_output_cost_per_1k
        return input_cost + output_cost