"""Agent router for multi-provider LLM execution."""
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger

from ..core.cost_tracker import record_cost
from .plan_reader import Step
from .deepseek_client import DeepSeekClient, StepResult
from .groq_client import GroqClient
from .gemini_client import GeminiClient
from .codestral_client import CodestralClient
from .execution_router import ExecutionRouter
from ..config.settings import settings


class AgentRouter:
    """
    Routes execution to appropriate LLM provider based on step characteristics.

    Supports multiple providers:
    - DeepSeek: Primary provider for complex code generation
    - Groq: Fast provider for simple tasks (FAST mode)
    - Gemini: Validation and audit (DOUBLE-CHECK mode)
    - Codestral: Small code refactoring tasks

    Uses ExecutionRouter for mode-based provider selection.
    """

    def __init__(
        self,
        prompt_cache: Optional[Any] = None,
        execution_mode: str = "BUILD",
        semantic_cache: Optional[Any] = None
    ):
        """
        Initialize agent router.

        Args:
            prompt_cache: Optional prompt cache instance
            execution_mode: Execution mode (FAST, BUILD, DOUBLE-CHECK)
            semantic_cache: Optional semantic cache for similar prompt matching
        """
        self.prompt_cache = prompt_cache
        self.execution_mode = execution_mode.upper()
        self.semantic_cache = semantic_cache

        # Initialize execution router for mode-based routing
        self.execution_router = ExecutionRouter()

        # Initialize clients lazily
        self._clients: Dict[str, Any] = {}
        self._initialize_clients()

    def _initialize_clients(self) -> None:
        """Initialize available LLM clients based on configured API keys."""
        # DeepSeek (primary)
        if settings.deepseek_api_key:
            try:
                self._clients["deepseek"] = DeepSeekClient()
                logger.debug("DeepSeek client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize DeepSeek client: {e}")

        # Groq (fast)
        if settings.groq_api_key:
            try:
                self._clients["groq"] = GroqClient()
                logger.debug("Groq client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")

        # Gemini (validation)
        if settings.google_api_key:
            try:
                self._clients["gemini"] = GeminiClient(execution_mode=self.execution_mode)
                logger.debug(f"Gemini client initialized (mode: {self.execution_mode})")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}")

        # Codestral (small tasks) — same availability logic as ExecutionRouter
        _codestral_ok = (
            bool(settings.mistral_api_key)
            and settings.mistral_api_key.isascii()
            and not settings.mistral_api_key.startswith("your_")
            and not settings.mistral_api_key.startswith("votre_")
        )
        if _codestral_ok:
            try:
                self._clients["codestral"] = CodestralClient()
                logger.debug("Codestral client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Codestral client: {e}")

        if not self._clients:
            raise ValueError("No LLM clients could be initialized. Check API keys.")

        logger.info(f"Initialized {len(self._clients)} LLM clients: {list(self._clients.keys())}")

    def select_provider_for_step(self, step: Step) -> str:
        """
        Select the best provider for a given step.

        Uses ExecutionRouter for mode-based routing, with fallbacks.

        Args:
            step: Step to execute

        Returns:
            Provider name to use
        """
        # Check for explicit provider override in step context
        if step.context and step.context.get("provider"):
            provider = step.context["provider"]
            if provider in self._clients:
                logger.debug(f"Using explicit provider override: {provider}")
                return provider

        # In DOUBLE-CHECK mode, use audit provider (Gemini) for analysis/validation steps
        if self.execution_mode == "DOUBLE-CHECK" and step.type in ["analysis", "validation", "review"]:
            audit_provider = self.execution_router.get_audit_provider(self.execution_mode)
            if audit_provider and audit_provider in self._clients:
                logger.info(f"DOUBLE-CHECK audit routing: {step.type} -> {audit_provider}")
                return audit_provider

        # Use ExecutionRouter for mode-based routing
        mode_provider = self.execution_router.get_provider_for_step(step, self.execution_mode)
        logger.info(f"Mode-based routing ({self.execution_mode}): {step.type} -> {mode_provider}")

        # Verify provider is available, fallback if not
        if mode_provider in self._clients:
            return mode_provider

        # Fallback to any available provider
        available = list(self._clients.keys())
        if available:
            fallback = available[0]
            logger.warning(f"Provider {mode_provider} not available, falling back to {fallback}")
            return fallback

        raise ValueError("No LLM providers available")

    async def execute_step(
        self,
        step: Step,
        context: Optional[str] = None,
        surgical_mode: bool = False
    ) -> StepResult:
        """
        Execute a step using the appropriate provider.

        The cache namespace is defined per step (step_{step_id}) to isolate each step
        and avoid semantic cache collisions. This ensures that the results of each step
        are stored and retrieved independently, preventing interference between steps
        with similar prompts.

        Args:
            step: Step to execute
            context: Additional context for the step
            surgical_mode: Whether surgical edit mode is enabled (for precise modifications)

        Returns:
            StepResult with execution results
        """
        start_time = datetime.now()

        # Select provider
        provider_name = self.select_provider_for_step(step)
        provider = self._clients[provider_name]

        logger.info(f"Executing step {step.id} with provider: {provider_name}")
        logger.info(f"Step description: {step.description[:60]}...")
        if surgical_mode:
            logger.info(f"Surgical mode enabled for step {step.id}")

        # Build prompt
        prompt = self._build_prompt(step, context, surgical_mode=surgical_mode)

        # Check semantic cache first (if enabled)
        # Use namespace per step to isolate each step and avoid semantic cache collisions
        cache_namespace = f"step_{step.id}" if step else None
        cached_response = None
        if self.semantic_cache:
            cached_response = self.semantic_cache.get(prompt, namespace=cache_namespace)

        if cached_response:
            response_text, similarity = cached_response
            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            logger.info(f"Semantic cache HIT for step {step.id} (similarity: {similarity:.3f})")

            # Record cache hit (zero cost)
            try:
                record_cost(
                    provider="cache",
                    workflow_type=self.execution_mode,
                    step_id=step.id,
                    task_id=step.id.split("_")[0] if "_" in step.id else step.id,
                    cost_usd=0.0,
                    tokens_total=0,
                    tokens_input=0,
                    tokens_output=0,
                    execution_time_ms=execution_time,
                    cached=True
                )
            except Exception as e:
                logger.debug(f"Could not record cache hit: {e}")

            return StepResult(
                step_id=step.id,
                success=True,
                output=response_text,
                tokens_used=0,
                input_tokens=0,
                output_tokens=0,
                execution_time_ms=execution_time,
                cost_usd=0.0
            )

        # Execute with provider, with automatic fallback on rate limit
        result = None
        fallback_provider = None
        
        try:
            result = await provider.generate(
                prompt=prompt,
                context=context,
                max_tokens=step.estimated_tokens * 2 if step.estimated_tokens else 4000
            )
            
            # Check if failed due to rate limit (429) and we have a fallback
            is_rate_limit = (
                not result.success and 
                result.error and 
                ("429" in str(result.error) or 
                 "rate limit" in str(result.error).lower() or 
                 "rate_limit" in str(result.error).lower() or
                 "too many requests" in str(result.error).lower())
            )
            
            if is_rate_limit:
                # Rate limit detected - try fallback provider
                if self.execution_mode == "FAST" and provider_name == "groq":
                    # In FAST mode, fallback to Gemini if Groq is rate limited
                    if "gemini" in self._clients:
                        fallback_provider = "gemini"
                        logger.warning(
                            f"Groq rate limited (429) for step {step.id}, "
                            f"falling back to Gemini"
                        )
                    elif "deepseek" in self._clients:
                        fallback_provider = "deepseek"
                        logger.warning(
                            f"Groq rate limited (429) for step {step.id}, "
                            f"falling back to DeepSeek"
                        )
                
                # Try fallback if available
                if fallback_provider and fallback_provider in self._clients:
                    fallback_client = self._clients[fallback_provider]
                    logger.info(f"Retrying step {step.id} with fallback provider: {fallback_provider}")
                    
                    try:
                        result = await fallback_client.generate(
                            prompt=prompt,
                            context=context,
                            max_tokens=step.estimated_tokens * 2 if step.estimated_tokens else 4000
                        )
                        provider_name = fallback_provider  # Update provider name for logging
                    except Exception as fallback_error:
                        logger.error(f"Fallback provider {fallback_provider} also failed: {fallback_error}")
                        # Keep original error

            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            # Cache the result (if semantic cache enabled)
            if self.semantic_cache and result and result.success:
                self.semantic_cache.put(
                    prompt=prompt,
                    response=result.code,
                    metadata={
                        "step_id": step.id,
                        "provider": provider_name,
                        "tokens": result.tokens_used,
                        "fallback_used": fallback_provider is not None
                    },
                    tokens_saved=0,  # This call didn't save tokens, but future similar calls will
                    cost_saved_usd=0.0,
                    namespace=cache_namespace
                )

            if result and result.success:
                logger.info(
                    f"Generation completed: {result.tokens_used} tokens, "
                    f"${result.cost_usd:.4f}, {execution_time:.0f}ms "
                    f"(provider: {provider_name})"
                )

                # Record cost to persistent tracker
                try:
                    record_cost(
                        provider=provider_name,
                        workflow_type=self.execution_mode,
                        step_id=step.id,
                        task_id=step.id.split("_")[0] if "_" in step.id else step.id,
                        cost_usd=result.cost_usd,
                        tokens_total=result.tokens_used,
                        tokens_input=result.input_tokens,
                        tokens_output=result.output_tokens,
                        execution_time_ms=execution_time,
                        cached=False
                    )
                except Exception as e:
                    logger.debug(f"Could not record cost: {e}")

            if result:
                return StepResult(
                    step_id=step.id,
                    success=result.success,
                    output=result.code,
                    tokens_used=result.tokens_used,
                    input_tokens=result.input_tokens,
                    output_tokens=result.output_tokens,
                    execution_time_ms=execution_time,
                    error=result.error,
                    cost_usd=result.cost_usd
                )
            else:
                # No result and no fallback worked
                raise Exception("Generation failed and no fallback available")

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.error(f"Step execution failed: {e}")

            return StepResult(
                step_id=step.id,
                success=False,
                output="",
                tokens_used=0,
                input_tokens=0,
                output_tokens=0,
                execution_time_ms=execution_time,
                error=str(e),
                cost_usd=0.0
            )

    def _build_prompt(self, step: Step, context: Optional[str] = None, surgical_mode: bool = False) -> str:
        """
        Build prompt for step execution.

        Args:
            step: Step to execute
            context: Additional context (may contain existing file contents)
            surgical_mode: Whether surgical edit mode is enabled

        Returns:
            Formatted prompt string
        """
        parts = []

        # Add language/framework context if available
        if step.context:
            if step.context.get("language"):
                parts.append(f"Language: {step.context['language']}")
            if step.context.get("framework"):
                parts.append(f"Framework: {step.context['framework']}")

        # Process context - check if it contains existing files section
        context_parts = []
        existing_files_section = None
        
        if context:
            # Check if context contains "Existing code files:" marker
            if "Existing code files:" in context:
                # Split context into parts: before files, files section, after files
                context_lines = context.split("\n")
                before_files = []
                files_section_lines = []
                after_files = []
                
                in_files_section = False
                for line in context_lines:
                    if "Existing code files:" in line:
                        in_files_section = True
                        files_section_lines.append(line)
                    elif in_files_section:
                        if line.startswith("===") or line.startswith("Modify the existing") or line.startswith("Add new code"):
                            files_section_lines.append(line)
                        elif line.strip() == "":
                            files_section_lines.append(line)
                        else:
                            # Check if we're still in a file content block
                            if any(f"=== File:" in prev_line for prev_line in files_section_lines[-10:]):
                                files_section_lines.append(line)
                            else:
                                after_files.append(line)
                    else:
                        before_files.append(line)
                
                if before_files:
                    context_parts.append("\n".join(before_files))
                
                if files_section_lines:
                    existing_files_section = "\n".join(files_section_lines)
                    # Format files section more clearly
                    context_parts.append(existing_files_section)
                
                if after_files:
                    context_parts.append("\n".join(after_files))
            else:
                # No existing files section, use context as-is
                context_parts.append(context)

        # Add step description
        parts.append(f"Task: {step.description}")

        # Add validation criteria if available
        if step.validation_criteria:
            criteria_text = "\n".join(f"- {criterion}" for criterion in step.validation_criteria)
            parts.append(f"\nRequirements:\n{criteria_text}")

        # Add context (with existing files if present)
        if context_parts:
            parts.append("\n" + "\n\n".join(context_parts))

        # Add generation instruction based on step type and surgical mode
        if surgical_mode:
            # Surgical mode: instructions are already in context (added by orchestrator)
            # Just add a reminder to use JSON format
            parts.append("\n\nIMPORTANT: Generate ONLY the JSON instructions object, not the complete file.")
            parts.append("The JSON should contain an 'operations' array with precise modification instructions.")
        else:
            # Normal mode
            if step.type == "refactoring":
                parts.append("\nRefactor the existing code according to the requirements above.")
            elif step.type == "code_generation":
                if existing_files_section:
                    parts.append("\nGenerate code that integrates with the existing files above.")
                else:
                    parts.append("\nGenerate the complete code implementation.")
            elif step.type == "analysis":
                parts.append("\nAnalyze and provide insights about the code.")
            else:
                parts.append("\nGenerate code.")

        return "\n".join(parts)

    async def close(self) -> None:
        """Close all provider clients."""
        for name, client in self._clients.items():
            try:
                await client.close()
                logger.debug(f"Closed {name} client")
            except Exception as e:
                logger.warning(f"Error closing {name} client: {e}")

        self._clients.clear()