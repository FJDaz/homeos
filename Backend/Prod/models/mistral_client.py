"""Mistral API client via OpenRouter for brainstorming."""
import asyncio
import time
import json
from typing import List, Optional, Dict, Any
import httpx
from loguru import logger

from ..config.settings import settings
from .base_client import BaseLLMClient, GenerationResult

class MistralClient(BaseLLMClient):
    """Async client for Mistral AI via OpenRouter (OpenAI-compatible)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None
    ):
        """
        Initialize Mistral client.
        """
        self.api_key = api_key or settings.mistral_chat_key
        # Direct Mistral API (MISTRAL_CHAT_KEY = La Plateforme chat key)
        self.api_url = api_url or "https://api.mistral.ai/v1/chat/completions"
        self.model = model or "open-mistral-nemo"
        self.timeout = timeout or settings.timeout
        self.max_retries = max_retries or settings.max_retries

        if not self.api_key:
            import os
            self.api_key = os.getenv("MISTRAL_CHAT_KEY")

        if not self.api_key:
            raise ValueError("MISTRAL_CHAT_KEY requis dans .env")

        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )

    @property
    def name(self) -> str:
        return "mistral"

    @property
    def specialties(self) -> List[str]:
        return ["french_native", "editorial", "creative_writing"]

    async def close(self) -> None:
        await self.client.aclose()

    async def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        cache_params: Optional[Dict[str, Any]] = None,
        output_constraint: Optional[str] = None
    ) -> GenerationResult:
        """Generate content from a prompt."""
        start_time = time.time()
        
        messages = [{"role": "user", "content": prompt}]
        
        request_data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens or settings.max_tokens,
            "temperature": temperature or settings.temperature
        }

        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                response = await self.client.post(self.api_url, json=request_data)
                response.raise_for_status()
                
                result_data = response.json()
                content = result_data["choices"][0]["message"]["content"]
                usage = result_data.get("usage", {})
                
                input_tokens = usage.get("prompt_tokens", 0)
                output_tokens = usage.get("completion_tokens", 0)
                total_tokens = usage.get("total_tokens", input_tokens + output_tokens)
                
                execution_time_ms = (time.time() - start_time) * 1000
                
                return GenerationResult(
                    success=True,
                    code=content,
                    tokens_used=total_tokens,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost_usd=0.0, # OpenRouter costs vary
                    execution_time_ms=execution_time_ms,
                    provider=self.name
                )
            except Exception as e:
                last_error = str(e)
                logger.warning(f"[Mistral] Attempt {attempt+1} failed: {e}")
                await asyncio.sleep(1)

        return GenerationResult(
            success=False, code="", tokens_used=0, input_tokens=0, output_tokens=0,
            cost_usd=0.0, execution_time_ms=(time.time()-start_time)*1000,
            error=last_error, provider=self.name
        )
