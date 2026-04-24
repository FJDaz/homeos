"""DeepSeek API client for code generation."""
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import httpx
from loguru import logger

from ..config.settings import settings
from .plan_reader import Step
from .base_client import BaseLLMClient, GenerationResult
from ..rag.pageindex_store import PageIndexRetriever


@dataclass
class StepResult:
    """Result of executing a step."""
    step_id: str
    success: bool
    output: str
    tokens_used: int
    input_tokens: int
    output_tokens: int
    execution_time_ms: float
    error: Optional[str] = None
    cost_usd: float = 0.0


class DeepSeekClient(BaseLLMClient):
    """Async client for DeepSeek API."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None
    ):
        """
        Initialize DeepSeek client.
        
        Args:
            api_key: DeepSeek API key (defaults to settings)
            api_url: API endpoint URL (defaults to settings)
            model: Model name (defaults to settings)
            timeout: Request timeout in seconds (defaults to settings)
            max_retries: Maximum retry attempts (defaults to settings)
        """
        self.api_key = api_key or settings.deepseek_api_key
        self.api_url = api_url or settings.deepseek_api_url
        self.model = model or settings.deepseek_model
        self.timeout = timeout or settings.timeout
        self.max_retries = max_retries or settings.max_retries
        
        if not self.api_key:
            raise ValueError("DeepSeek API key is required")
        
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        self._retriever = None

    async def retrieve_context(self, query: str, top_k: int = 5) -> str:
        """
        Retrieve relevant context from codebase using PageIndexRAG.
        
        Args:
            query: The search query
            top_k: Number of snippets to retrieve
            
        Returns:
            Formatted context string
        """
        if self._retriever is None:
            # Hierarchical root detection
            # models/Prod/Backend (3 levels)
            project_root = Path(__file__).resolve().parents[3]
            self._retriever = PageIndexRetriever(docs_path=str(project_root))
        
        if not self._retriever.enabled:
            return "RAG context retrieval not available."

        results = await self._retriever.retrieve(query, top_k=top_k)
        if not results:
            return "No relevant context found in codebase."

        context_parts = ["### Relevant Codebase Context:"]
        for res in results:
            context_parts.append(f"--- Fichier: {res['file_name']} ({res['reference']}) ---")
            context_parts.append(res['content'])
        
        return "\n\n".join(context_parts)
    
    @property
    def name(self) -> str:
        """Provider name."""
        return "deepseek"
    
    @property
    def specialties(self) -> List[str]:
        """List of specialties for this provider."""
        return [
            "code_generation",
            "complex_code",
            "refactoring",
            "analysis"
        ]
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def check_balance(self) -> Optional[float]:
        """Check account balance (if API supports it)."""
        if not self._should_check_balance():
            return None
        
        try:
            balance_url = self.api_url.replace("/v1/chat/completions", "/v1/account/balance")
            response = await self.client.get(balance_url)
            if response.status_code == 200:
                data = response.json()
                balance = data.get("balance") or data.get("available_balance") or data.get("credits")
                if balance is not None:
                    return float(balance)
        except: pass
        return None
    
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
        """Generate code from a prompt."""
        start_time = datetime.now()
        
        if self._should_check_balance():
            balance = await self.check_balance()
            if balance is not None and balance < settings.min_balance_threshold:
                return GenerationResult(success=False, code="", tokens_used=0, input_tokens=0, output_tokens=0, cost_usd=0.0, execution_time_ms=0.0, error="Insufficient balance", provider=self.name)
        
        full_prompt = self._build_simple_prompt(prompt, context)
        messages = []
        if output_constraint == "json_surgical":
            from ..core.prompts.surgical_protocol import SURGICAL_SYSTEM_PROMPT
            messages.append({"role": "system", "content": SURGICAL_SYSTEM_PROMPT.format(ast_summary="[AST context]")})
        elif system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": full_prompt})

        request_data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": min(max_tokens or settings.deepseek_max_tokens, settings.deepseek_max_tokens),
            "temperature": temperature or settings.temperature
        }

        if output_constraint == "json_surgical":
            request_data["response_format"] = {"type": "json_object"}
        
        for attempt in range(self.max_retries + 1):
            try:
                response = await self.client.post(self.api_url, json=request_data)
                response.raise_for_status()
                result_data = response.json()
                content = result_data["choices"][0]["message"]["content"]
                usage = result_data.get("usage", {})
                it, ot = usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)
                cost = self._calculate_cost(it, ot)
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                return GenerationResult(success=True, code=content, tokens_used=it+ot, input_tokens=it, output_tokens=ot, cost_usd=cost, execution_time_ms=execution_time, provider=self.name)
            except Exception as e:
                if attempt == self.max_retries: break
                await asyncio.sleep(2 ** attempt)
        
        return GenerationResult(success=False, code="", tokens_used=0, input_tokens=0, output_tokens=0, cost_usd=0.0, execution_time_ms=0.0, error="Max retries reached", provider=self.name)
    
    def _build_simple_prompt(self, prompt: str, context: Optional[str] = None, output_constraint: Optional[str] = None) -> str:
        prompt_parts = []
        if context: prompt_parts.append(f"Context: {context}\n\n")
        prompt_parts.append(f"Task: {prompt}\n\n")
        if output_constraint: prompt_parts.append(f"Output constraint: {output_constraint}")
        else: prompt_parts.append("Generate the complete code implementation.")
        return "".join(prompt_parts)
    
    async def execute_step(self, step: Step, context: Optional[str] = None) -> StepResult:
        start_time = datetime.now()
        prompt = self._build_prompt(step, context)
        request_data = {"model": self.model, "messages": [{"role": "user", "content": prompt}], "max_tokens": min(step.estimated_tokens, settings.deepseek_max_tokens), "temperature": settings.temperature}
        
        for attempt in range(self.max_retries + 1):
            try:
                response = await self.client.post(self.api_url, json=request_data)
                response.raise_for_status()
                result_data = response.json()
                content = result_data["choices"][0]["message"]["content"]
                usage = result_data.get("usage", {})
                it, ot = usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)
                cost = self._calculate_cost(it, ot)
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                return StepResult(step_id=step.id, success=True, output=content, tokens_used=it+ot, input_tokens=it, output_tokens=ot, execution_time_ms=execution_time, cost_usd=cost)
            except Exception as e:
                if attempt == self.max_retries: break
                await asyncio.sleep(2 ** attempt)
        
        return StepResult(step_id=step.id, success=False, output="", tokens_used=0, input_tokens=0, output_tokens=0, execution_time_ms=0.0, error="Max retries reached")
    
    def _build_prompt(self, step: Step, context: Optional[str] = None) -> str:
        prompt_parts = [f"Task: {step.description}\n"]
        if step.validation_criteria:
            prompt_parts.append("\nRequirements:\n" + "\n".join(f"- {c}" for c in step.validation_criteria) + "\n")
        if context: prompt_parts.append(f"\nContext: {context}\n")
        return "".join(prompt_parts)
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        return (input_tokens / 1000) * settings.deepseek_input_cost_per_1k + (output_tokens / 1000) * settings.deepseek_output_cost_per_1k
