"""Xiaomi MiMo LLM client — OpenAI-compatible SDK."""
import asyncio
import time
import json
from typing import List, Optional, Dict, Any
import httpx
from loguru import logger

from ..config.settings import settings
from .base_client import BaseLLMClient, GenerationResult

class MimoClient(BaseLLMClient):
    """
    Async client for Xiaomi MiMo AI (OpenAI-compatible).
    Base URL: https://api.xiaomimimo.com/v1
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None
    ):
        """Initialize MiMo client."""
        self.api_key = api_key or settings.mimo_api_key
        self.api_url = api_url or settings.mimo_api_url
        if not self.api_url.endswith("/chat/completions"):
            self.api_url = f"{self.api_url.rstrip('/')}/chat/completions"
            
        self.model = model or settings.mimo_model
        self.timeout = timeout or settings.timeout
        self.max_retries = max_retries or settings.max_retries

        if not self.api_key:
            logger.warning("Xiaomi MiMo API key (MIMO_KEY) not configured")

        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )

    @property
    def name(self) -> str:
        return "mimo"

    @property
    def specialties(self) -> List[str]:
        return ["high_fidelity_ui", "vision_aware", "low_cost", "chinese_optimized"]

    async def close(self) -> None:
        await self.client.aclose()

    async def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        cache_params: Optional[Dict[str, Any]] = None,
        output_constraint: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> GenerationResult:
        """Generate content from a prompt."""
        start_time = time.time()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        user_content = (context + "\n\n" if context else "") + prompt
        messages.append({"role": "user", "content": user_content})
        
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
                
                # Local cost calculation
                cost = (input_tokens * settings.mimo_input_cost_per_1k / 1000) + \
                       (output_tokens * settings.mimo_output_cost_per_1k / 1000)
                
                execution_time_ms = (time.time() - start_time) * 1000
                
                logger.info(f"MiMo prompt tokens: {input_tokens}, completion: {output_tokens}, cost: ${cost:.6f}")
                
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
            except Exception as e:
                last_error = str(e)
                logger.warning(f"[MiMo] Attempt {attempt+1} failed: {e}")
                if attempt < self.max_retries:
                    await asyncio.sleep(1)

        return GenerationResult(
            success=False, code="", tokens_used=0, input_tokens=0, output_tokens=0,
            cost_usd=0.0, execution_time_ms=(time.time()-start_time)*1000,
            error=last_error, provider=self.name
        )

    async def generate_with_image(
        self,
        prompt: str,
        image_base64: str,
        mime_type: str = "image/png",
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        output_constraint: Optional[str] = None,
    ) -> GenerationResult:
        """Vision multimodal via OpenAI-compatible content array."""
        start_time = time.time()
        
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{image_base64}"}
                },
                {"type": "text", "text": prompt}
            ]
        }]
        
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
                
                cost = (input_tokens * settings.mimo_input_cost_per_1k / 1000) + \
                       (output_tokens * settings.mimo_output_cost_per_1k / 1000)
                
                execution_time_ms = (time.time() - start_time) * 1000
                
                logger.info(f"MiMo Vision prompt tokens: {input_tokens}, completion: {output_tokens}, cost: ${cost:.6f}")
                
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
            except Exception as e:
                last_error = str(e)
                logger.warning(f"[MiMo Vision] Attempt {attempt+1} failed: {e}")
                if attempt < self.max_retries:
                    await asyncio.sleep(1)

        return GenerationResult(
            success=False, code="", tokens_used=0, input_tokens=0, output_tokens=0,
            cost_usd=0.0, execution_time_ms=(time.time()-start_time)*1000,
            error=last_error, provider=self.name
        )

if __name__ == "__main__":
    # Small test block
    async def test():
        client = MimoClient()
        res = await client.generate("Dis bonjour en français")
        print(f"Result: {res.code}")
        await client.close()
    
    if settings.mimo_api_key:
        asyncio.run(test())
