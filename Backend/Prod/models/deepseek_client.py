"""DeepSeek API client for code generation."""
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import httpx
from loguru import logger

from ..config.settings import settings
from .plan_reader import Step
from .base_client import BaseLLMClient, GenerationResult


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
        """
        Check account balance (if API supports it).
        
        Note: DeepSeek API may not provide a direct balance endpoint.
        This method attempts to check balance via account/billing endpoints.
        
        Returns:
            Balance in USD if available, None if not supported or check failed
        """
        if not self._should_check_balance():
            return None
        
        try:
            # Try to check balance via account endpoint (if available)
            # Note: DeepSeek API structure may vary - adjust endpoint as needed
            balance_url = self.api_url.replace("/v1/chat/completions", "/v1/account/balance")
            
            try:
                response = await self.client.get(balance_url)
                if response.status_code == 200:
                    data = response.json()
                    # Adjust based on actual API response structure
                    balance = data.get("balance") or data.get("available_balance") or data.get("credits")
                    if balance is not None:
                        logger.info(f"Account balance: ${balance:.2f}")
                        return float(balance)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    # Endpoint not available - balance check not supported
                    logger.debug("Balance check endpoint not available for DeepSeek API")
                else:
                    logger.warning(f"Failed to check balance: HTTP {e.response.status_code}")
            except Exception as e:
                logger.debug(f"Balance check not supported: {e}")
                
        except Exception as e:
            logger.debug(f"Balance check failed: {e}")
        
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
        start_time = datetime.now()
        
        # Check balance before request (if enabled and supported)
        if self._should_check_balance():
            balance = await self.check_balance()
            if balance is not None:
                min_balance = settings.min_balance_threshold
                if balance < min_balance:
                    error_msg = f"Insufficient balance: ${balance:.2f} (minimum: ${min_balance:.2f})"
                    logger.error(error_msg)
                    return GenerationResult(
                        success=False,
                        code="",
                        tokens_used=0,
                        input_tokens=0,
                        output_tokens=0,
                        cost_usd=0.0,
                        execution_time_ms=0.0,
                        error=error_msg,
                        provider=self.name
                    )
                logger.info(f"Balance check passed: ${balance:.2f}")
        
        # Build full prompt (context may be cacheable block)
        full_prompt = self._build_simple_prompt(prompt, context)
        
        # Prepare request
        request_data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            "max_tokens": max_tokens or settings.max_tokens,
            "temperature": temperature or settings.temperature
        }
        
        # Add cache control if provided (DeepSeek API support)
        if cache_params:
            # DeepSeek may support cache_id or cache_control
            if "cache_id" in cache_params:
                request_data["cache_id"] = cache_params["cache_id"]
            if "cache_control" in cache_params:
                # If DeepSeek supports cache_control, add it
                # Note: Check DeepSeek API docs for exact format
                pass
        
        # Execute with retries
        last_error = None
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
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                
                logger.info(
                    f"Generation completed: {total_tokens} tokens, "
                    f"${cost:.4f}, {execution_time:.0f}ms"
                )
                
                return GenerationResult(
                    success=True,
                    code=content,
                    tokens_used=total_tokens,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost_usd=cost,
                    execution_time_ms=execution_time,
                    provider=self.name
                )
                
            except httpx.HTTPStatusError as e:
                last_error = f"HTTP {e.response.status_code}: {e.response.text}"
                logger.warning(f"Generation attempt {attempt + 1} failed: {last_error}")
                
                if e.response.status_code == 429:  # Rate limit
                    wait_time = 2 ** attempt
                    logger.info(f"Rate limited, waiting {wait_time}s before retry")
                    await asyncio.sleep(wait_time)
                elif e.response.status_code >= 500:  # Server error
                    if attempt < self.max_retries:
                        wait_time = 2 ** attempt
                        await asyncio.sleep(wait_time)
                        continue
                else:
                    break
                    
            except httpx.RequestError as e:
                last_error = f"Request error: {str(e)}"
                logger.warning(f"Generation attempt {attempt + 1} failed: {last_error}")
                
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    break
            
            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
                logger.error(f"Generation failed with unexpected error: {last_error}")
                break
        
        # All retries failed
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        logger.error(f"Generation failed after {self.max_retries + 1} attempts: {last_error}")
        
        return GenerationResult(
            success=False,
            code="",
            tokens_used=0,
            input_tokens=0,
            output_tokens=0,
            cost_usd=0.0,
            execution_time_ms=execution_time,
            error=last_error,
            provider=self.name
        )
    
    def _build_simple_prompt(self, prompt: str, context: Optional[str] = None, output_constraint: Optional[str] = None) -> str:
        """
        Build a simple prompt from task and context.
        
        Args:
            prompt: Task description
            context: Additional context
            output_constraint: Optional constraint on output format
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = []
        
        # Add context if provided
        if context:
            prompt_parts.append(f"Context: {context}\n\n")
        
        # Add task description
        prompt_parts.append(f"Task: {prompt}\n\n")
        
        # Add output constraint if specified
        if output_constraint:
            if output_constraint == "Code only":
                prompt_parts.append("Generate only code, no explanations or prose.")
            elif output_constraint == "JSON only":
                prompt_parts.append("Generate only valid JSON, no explanations.")
            elif output_constraint == "No prose":
                prompt_parts.append("Generate output without prose or explanations.")
            else:
                prompt_parts.append(f"Output constraint: {output_constraint}")
        else:
            prompt_parts.append("Generate the complete code implementation.")
        
        return "".join(prompt_parts)
    
    async def execute_step(
        self,
        step: Step,
        context: Optional[str] = None
    ) -> StepResult:
        """
        Execute a step using DeepSeek API.
        
        Args:
            step: Step to execute
            context: Additional context for the step
            
        Returns:
            StepResult with execution results
        """
        start_time = datetime.now()
        step_id = step.id
        
        logger.info(f"Executing step {step_id}: {step.description[:50]}...")
        
        # Build prompt
        prompt = self._build_prompt(step, context)
        
        # Prepare request
        request_data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": min(step.estimated_tokens, settings.max_tokens),
            "temperature": settings.temperature
        }
        
        # Execute with retries
        last_error = None
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
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                
                logger.info(
                    f"Step {step_id} completed: {total_tokens} tokens, "
                    f"${cost:.4f}, {execution_time:.0f}ms"
                )
                
                return StepResult(
                    step_id=step_id,
                    success=True,
                    output=content,
                    tokens_used=total_tokens,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    execution_time_ms=execution_time,
                    cost_usd=cost
                )
                
            except httpx.HTTPStatusError as e:
                last_error = f"HTTP {e.response.status_code}: {e.response.text}"
                logger.warning(f"Step {step_id} attempt {attempt + 1} failed: {last_error}")
                
                if e.response.status_code == 429:  # Rate limit
                    # Wait before retry
                    wait_time = 2 ** attempt
                    logger.info(f"Rate limited, waiting {wait_time}s before retry")
                    await asyncio.sleep(wait_time)
                elif e.response.status_code >= 500:  # Server error
                    # Retry on server errors
                    if attempt < self.max_retries:
                        wait_time = 2 ** attempt
                        await asyncio.sleep(wait_time)
                        continue
                else:
                    # Client error, don't retry
                    break
                    
            except httpx.RequestError as e:
                last_error = f"Request error: {str(e)}"
                logger.warning(f"Step {step_id} attempt {attempt + 1} failed: {last_error}")
                
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    break
            
            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
                logger.error(f"Step {step_id} failed with unexpected error: {last_error}")
                break
        
        # All retries failed
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        logger.error(f"Step {step_id} failed after {self.max_retries + 1} attempts: {last_error}")
        
        return StepResult(
            step_id=step_id,
            success=False,
            output="",
            tokens_used=0,
            input_tokens=0,
            output_tokens=0,
            execution_time_ms=execution_time,
            error=last_error,
            cost_usd=0.0
        )
    
    def _build_prompt(self, step: Step, context: Optional[str] = None) -> str:
        """
        Build the prompt for a step.
        
        Args:
            step: Step to build prompt for
            context: Additional context (may contain existing file contents)
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = []
        
        # Add step context if available
        if step.context and isinstance(step.context, dict):
            if step.context.get("language"):
                prompt_parts.append(f"Language: {step.context['language']}\n")
            if step.context.get("framework"):
                prompt_parts.append(f"Framework: {step.context['framework']}\n")
            if step.context.get("files"):
                files = ", ".join(step.context["files"])
                prompt_parts.append(f"Target files: {files}\n")
        
        # Add task description
        prompt_parts.append(f"Task: {step.description}\n")
        
        # Add validation criteria if available
        if step.validation_criteria:
            criteria = "\n".join(f"- {criterion}" for criterion in step.validation_criteria)
            prompt_parts.append(f"\nRequirements:\n{criteria}\n")
        
        # Add context if provided (may contain existing file contents)
        if context:
            # Check if context contains existing files section
            if "Existing code files:" in context:
                # Format existing files section clearly
                prompt_parts.append(f"\n{context}\n")
            else:
                # Regular context
                prompt_parts.append(f"\nContext: {context}\n")
        
        # Add instruction based on type
        if step.type == "code_generation":
            if context and "Existing code files:" in context:
                prompt_parts.append("\nGenerate code that integrates with the existing files above.")
            else:
                prompt_parts.append("\nGenerate the complete code implementation.")
        elif step.type == "refactoring":
            prompt_parts.append("\nRefactor the existing code according to the requirements above.")
        elif step.type == "analysis":
            prompt_parts.append("\nAnalyze and provide insights about the code.")
        elif step.type == "patch":
            prompt_parts.append("\nGenerate ONLY the fragment to insert at the specified marker/line (patch mode). Do not output the complete file.")
        
        return "".join(prompt_parts)
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate cost based on token usage.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Cost in USD
        """
        input_cost = (input_tokens / 1000) * settings.deepseek_input_cost_per_1k
        output_cost = (output_tokens / 1000) * settings.deepseek_output_cost_per_1k
        return input_cost + output_cost
