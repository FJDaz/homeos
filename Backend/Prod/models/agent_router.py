"""Agent router for multi-provider LLM execution with smart routing.

Routes execution to appropriate LLM provider based on:
- Step characteristics (type, complexity)
- Context size (estimated tokens)
- Provider capabilities and limits
- Execution mode (FAST, BUILD, DOUBLE-CHECK)

Features:
- Smart context-based routing (SmartContextRouter)
- Cross-provider fallback cascade (ProviderFallbackCascade)
- Automatic step chunking (StepChunker)
- Section-based generation for large files (SectionGenerator)
"""
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
from .smart_context_router import SmartContextRouter, RoutingDecision
from .provider_fallback_cascade import ProviderFallbackCascade, CascadeConfig
from .step_chunker import StepChunker, ChunkingStrategy
from .section_generator import SectionGenerator, should_use_section_generation
from ..config.settings import settings


class AgentRouter:
    """
    Routes execution to appropriate LLM provider with advanced features.

    Supports multiple providers with intelligent routing:
    - DeepSeek: Primary provider for complex code generation (10k-50k tokens)
    - Groq: Fast provider for simple tasks (< 10k tokens)
    - Gemini: High-capacity for large contexts (> 50k tokens) and vision
    - Codestral: Small code refactoring tasks
    
    Smart Routing by Context Size:
    - < 10k tokens: Groq (fast, free tier)
    - 10k - 50k tokens: DeepSeek (balanced quality/cost)
    - > 50k tokens: Gemini (1M+ context, no timeout)
    - Vision/Images: Gemini (multimodal native)
    
    Fallback Cascade:
    - Automatic fallback on rate limits (429), token limits (413), timeouts
    - Cross-provider fallback chain: deepseek → gemini → codestral
    - Circuit breaker pattern for failing providers
    
    Automatic Chunking:
    - Steps > 30k tokens are automatically chunked
    - File-based, section-based, or logic-based chunking strategies
    - Results merged automatically
    
    Section-based Generation:
    - Large files generated incrementally by sections
    - Imports → Types → Utilities → Classes → Functions → Main
    - Accumulated output to handle token limits
    """

    def __init__(
        self,
        prompt_cache: Optional[Any] = None,
        execution_mode: str = "BUILD",
        semantic_cache: Optional[Any] = None
    ):
        """
        Initialize agent router with smart routing.

        Args:
            prompt_cache: Optional prompt cache instance
            execution_mode: Execution mode (FAST, BUILD, DOUBLE-CHECK)
            semantic_cache: Optional semantic cache for similar prompt matching
        """
        self.prompt_cache = prompt_cache
        self.execution_mode = execution_mode.upper()
        self.semantic_cache = semantic_cache

        # Initialize execution router for mode-based routing (legacy support)
        self.execution_router = ExecutionRouter()
        
        # Initialize smart context router (new)
        self.context_router: Optional[SmartContextRouter] = None
        
        # Initialize fallback cascade (new)
        self.fallback_cascade: Optional[ProviderFallbackCascade] = None
        
        # Initialize chunker and section generator (new)
        self.step_chunker = StepChunker()
        self.section_generator = SectionGenerator()

        # Initialize clients lazily
        self._clients: Dict[str, Any] = {}
        self._initialize_clients()
        
        # Initialize smart routing components after clients
        self._initialize_smart_routing()

    def _initialize_clients(self) -> None:
        """Initialize available LLM clients based on configured API keys."""
        # DeepSeek (primary for balanced tasks)
        if settings.deepseek_api_key:
            try:
                self._clients["deepseek"] = DeepSeekClient()
                logger.debug("DeepSeek client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize DeepSeek client: {e}")

        # Groq (fast for small tasks)
        if settings.groq_api_key:
            try:
                self._clients["groq"] = GroqClient()
                logger.debug("Groq client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")

        # Gemini (high capacity for large contexts)
        if settings.google_api_key:
            try:
                self._clients["gemini"] = GeminiClient(execution_mode=self.execution_mode)
                logger.debug(f"Gemini client initialized (mode: {self.execution_mode})")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}")

        # Codestral (small tasks)
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
    
    def _initialize_smart_routing(self) -> None:
        """Initialize smart routing components."""
        available = list(self._clients.keys())
        
        # Initialize context router
        self.context_router = SmartContextRouter(available_providers=available)
        
        # Initialize fallback cascade
        cascade_config = CascadeConfig(
            max_attempts_per_provider=3,
            base_retry_delay=1.0,
            enable_circuit_breaker=True
        )
        self.fallback_cascade = ProviderFallbackCascade(
            clients=self._clients,
            config=cascade_config
        )
        
        logger.info("Smart routing initialized with context-based provider selection")

    def select_provider_for_step(self, step: Step) -> str:
        """
        Select the best provider for a given step using smart routing.

        Uses SmartContextRouter for context-based selection, with fallbacks.

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

        # Use SmartContextRouter for intelligent routing
        if self.context_router:
            try:
                decision = self.context_router.route_step(
                    step=step,
                    execution_mode=self.execution_mode
                )
                
                # Validate primary provider is available
                if decision.primary_provider in self._clients:
                    logger.info(
                        f"Smart routing ({self.execution_mode}): "
                        f"{step.type} → {decision.primary_provider} "
                        f"(~{decision.estimated_tokens} tokens, {decision.reason})"
                    )
                    return decision.primary_provider
                else:
                    logger.warning(
                        f"Smart routing selected {decision.primary_provider} "
                        f"but it's not available, using fallback"
                    )
            except Exception as e:
                logger.warning(f"Smart routing failed: {e}, using legacy routing")

        # Fallback to legacy ExecutionRouter
        mode_provider = self.execution_router.get_provider_for_step(step, self.execution_mode)
        logger.info(f"Legacy routing ({self.execution_mode}): {step.type} -> {mode_provider}")

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
    
    def get_routing_decision(self, step: Step, context: Optional[str] = None) -> RoutingDecision:
        """
        Get full routing decision for a step.
        
        Args:
            step: Step to route
            context: Additional context
            
        Returns:
            RoutingDecision with complete routing information
        """
        if self.context_router:
            return self.context_router.route_step(step, context, execution_mode=self.execution_mode)
        
        # Fallback to basic decision
        provider = self.select_provider_for_step(step)
        return RoutingDecision(
            primary_provider=provider,
            fallback_chain=[],
            estimated_tokens=step.estimated_tokens or 5000,
            should_chunk=False,
            chunk_size=None,
            reason="Legacy routing"
        )

    async def execute_step(
        self,
        step: Step,
        context: Optional[str] = None,
        surgical_mode: bool = False,
        loaded_files: Optional[Dict[str, Optional[str]]] = None
    ) -> StepResult:
        """
        Execute a step using the appropriate provider with full smart routing.

        Features:
        - Smart context-based provider selection
        - Automatic fallback cascade
        - Step chunking for large contexts
        - Section-based generation for large files
        - Semantic caching

        Args:
            step: Step to execute
            context: Additional context
            surgical_mode: Whether surgical edit mode is enabled
            loaded_files: Loaded file contents for context estimation

        Returns:
            StepResult with execution results
        """
        start_time = datetime.now()

        # Get routing decision
        routing_decision = self.get_routing_decision(step, context)
        
        # Check if step should be chunked
        if routing_decision.should_chunk and self.step_chunker:
            logger.info(f"Step {step.id} requires chunking: {routing_decision.reason}")
            return await self._execute_chunked_step(
                step, context, routing_decision, surgical_mode
            )
        
        # Check if section-based generation should be used
        if self.context_router:
            estimated = self.context_router.estimate_tokens(step, context, loaded_files)
            if should_use_section_generation(step, estimated):
                logger.info(f"Step {step.id} using section-based generation")
                return await self._execute_section_generation(
                    step, context, routing_decision, surgical_mode
                )

        # Standard execution with fallback cascade
        return await self._execute_with_fallback(
            step, context, routing_decision, surgical_mode, start_time
        )
    
    async def _execute_with_fallback(
        self,
        step: Step,
        context: Optional[str],
        routing_decision: RoutingDecision,
        surgical_mode: bool,
        start_time: datetime
    ) -> StepResult:
        """Execute step with fallback cascade."""
        
        # Check semantic cache first
        cache_namespace = f"step_{step.id}" if step else None
        cached_response = None
        if self.semantic_cache:
            prompt = self._build_prompt(step, context, surgical_mode)
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
        
        # Build prompt
        prompt = self._build_prompt(step, context, surgical_mode)
        
        # Execute with fallback cascade
        if self.fallback_cascade:
            # Build fallback chain
            fallback_chain = [routing_decision.primary_provider] + routing_decision.fallback_chain
            fallback_chain = [p for p in fallback_chain if p in self._clients]
            
            cascade_result = await self.fallback_cascade.execute(
                fallback_chain=fallback_chain,
                execute_fn=lambda client: client.generate(
                    prompt=prompt,
                    context=context,
                    max_tokens=step.estimated_tokens * 2 if step.estimated_tokens else 4000
                ),
                context_size=routing_decision.estimated_tokens
            )
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if cascade_result.success:
                # Cache the result
                if self.semantic_cache:
                    self.semantic_cache.put(
                        prompt=prompt,
                        response=cascade_result.output,
                        metadata={
                            "step_id": step.id,
                            "provider": cascade_result.provider_used,
                            "fallback_used": cascade_result.fallback_used
                        },
                        tokens_saved=0,
                        cost_saved_usd=0.0,
                        namespace=cache_namespace
                    )
                
                # Record cost
                try:
                    record_cost(
                        provider=cascade_result.provider_used,
                        workflow_type=self.execution_mode,
                        step_id=step.id,
                        task_id=step.id.split("_")[0] if "_" in step.id else step.id,
                        cost_usd=cascade_result.total_cost,
                        tokens_total=cascade_result.total_tokens,
                        tokens_input=cascade_result.total_tokens // 2,  # Estimate
                        tokens_output=cascade_result.total_tokens // 2,
                        execution_time_ms=execution_time,
                        cached=False
                    )
                except Exception as e:
                    logger.debug(f"Could not record cost: {e}")
                
                if cascade_result.fallback_used:
                    logger.info(
                        f"Step {step.id} completed with fallback to {cascade_result.provider_used}: "
                        f"{cascade_result.total_tokens} tokens, ${cascade_result.total_cost:.4f}"
                    )
                
                return StepResult(
                    step_id=step.id,
                    success=True,
                    output=cascade_result.output,
                    tokens_used=cascade_result.total_tokens,
                    input_tokens=cascade_result.total_tokens // 2,
                    output_tokens=cascade_result.total_tokens // 2,
                    execution_time_ms=execution_time,
                    cost_usd=cascade_result.total_cost
                )
            else:
                logger.error(f"Step {step.id} failed after all fallback attempts")
                return StepResult(
                    step_id=step.id,
                    success=False,
                    output="",
                    tokens_used=0,
                    input_tokens=0,
                    output_tokens=0,
                    execution_time_ms=execution_time,
                    error=cascade_result.error,
                    cost_usd=0.0
                )
        else:
            # Fallback to simple execution without cascade
            return await self._execute_simple(step, context, surgical_mode, start_time)
    
    async def _execute_chunked_step(
        self,
        step: Step,
        context: Optional[str],
        routing_decision: RoutingDecision,
        surgical_mode: bool
    ) -> StepResult:
        """Execute a step by chunking it into smaller sub-steps."""
        start_time = datetime.now()
        
        # Create chunking strategy
        chunking_strategy = self.step_chunker.chunk_step(
            step=step,
            estimated_tokens=routing_decision.estimated_tokens
        )
        
        logger.info(
            f"Executing chunked step {step.id} with {len(chunking_strategy.chunks)} chunks "
            f"({chunking_strategy.strategy_type.value})"
        )
        
        # Execute chunks
        results = []
        chunk_outputs = []
        
        for chunk in chunking_strategy.chunks:
            # Convert chunk to Step
            chunk_step = Step(chunk.to_step_dict())
            
            # Execute chunk
            chunk_result = await self._execute_with_fallback(
                step=chunk_step,
                context=context,
                routing_decision=routing_decision,
                surgical_mode=surgical_mode,
                start_time=datetime.now()
            )
            
            results.append(chunk_result)
            if chunk_result.success:
                chunk_outputs.append(chunk_result.output)
            else:
                logger.error(f"Chunk {chunk.id} failed: {chunk_result.error}")
        
        # Merge results
        merged_output = self.step_chunker.merge_chunk_results(
            chunking_strategy, chunk_outputs
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        total_tokens = sum(r.tokens_used for r in results)
        total_cost = sum(r.cost_usd for r in results)
        
        success = len(chunk_outputs) == len(chunking_strategy.chunks)
        
        return StepResult(
            step_id=step.id,
            success=success,
            output=merged_output,
            tokens_used=total_tokens,
            input_tokens=total_tokens // 2,
            output_tokens=total_tokens // 2,
            execution_time_ms=execution_time,
            error=None if success else "Some chunks failed",
            cost_usd=total_cost
        )
    
    async def _execute_section_generation(
        self,
        step: Step,
        context: Optional[str],
        routing_decision: RoutingDecision,
        surgical_mode: bool
    ) -> StepResult:
        """Execute step using section-based generation."""
        start_time = datetime.now()
        
        # Detect language from context
        language = "python"
        if step.context and step.context.get("language"):
            language = step.context["language"]
        
        files = []
        if step.context and step.context.get("files"):
            files = step.context["files"]
        file_path = files[0] if files else None
        
        # Create generation plan
        plan = self.section_generator.create_plan(
            description=step.description,
            language=language,
            file_path=file_path
        )
        
        logger.info(
            f"Section generation for {step.id}: {len(plan.sections)} sections, "
            f"~{plan.total_estimated_lines} lines"
        )
        
        # Generate all sections
        def generate_fn(prompt: str):
            provider_name = routing_decision.primary_provider
            provider = self._clients.get(provider_name)
            if not provider:
                provider = list(self._clients.values())[0]
            
            return provider.generate(
                prompt=prompt,
                context=context,
                max_tokens=step.estimated_tokens * 2 if step.estimated_tokens else 4000
            )
        
        final_code, section_results = await self.section_generator.generate_all_sections(
            plan=plan,
            generate_fn=generate_fn,
            context=context,
            on_progress=lambda current, total, section_name: logger.info(
                f"Section progress: {current}/{total} - {section_name}"
            )
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        total_tokens = sum(r.tokens_used for r in section_results)
        
        success = any(r.success for r in section_results)
        
        return StepResult(
            step_id=step.id,
            success=success,
            output=final_code,
            tokens_used=total_tokens,
            input_tokens=total_tokens // 2,
            output_tokens=total_tokens // 2,
            execution_time_ms=execution_time,
            error=None if success else "Section generation failed",
            cost_usd=0.0  # Will be tracked by individual section costs
        )
    
    async def _execute_simple(
        self,
        step: Step,
        context: Optional[str],
        surgical_mode: bool,
        start_time: datetime
    ) -> StepResult:
        """Simple execution without fallback cascade (legacy)."""
        
        # Select provider
        provider_name = self.select_provider_for_step(step)
        provider = self._clients[provider_name]
        
        logger.info(f"Executing step {step.id} with provider: {provider_name}")
        if surgical_mode:
            logger.info(f"Surgical mode enabled for step {step.id}")
        
        # Build prompt
        prompt = self._build_prompt(step, context, surgical_mode)
        
        try:
            result = await provider.generate(
                prompt=prompt,
                context=context,
                max_tokens=step.estimated_tokens * 2 if step.estimated_tokens else 4000
            )
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if result.success:
                logger.info(
                    f"Generation completed: {result.tokens_used} tokens, "
                    f"${result.cost_usd:.4f}, {execution_time:.0f}ms "
                    f"(provider: {provider_name})"
                )
            
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
        """Build prompt for step execution."""
        parts = []

        # Add language/framework context if available
        if step.context:
            if step.context.get("language"):
                parts.append(f"Language: {step.context['language']}")
            if step.context.get("framework"):
                parts.append(f"Framework: {step.context['framework']}")

        # Process context
        context_parts = []
        if context:
            if "Existing code files:" in context:
                context_parts.append(context)
            else:
                context_parts.append(context)

        # Add step description
        parts.append(f"Task: {step.description}")

        # Add validation criteria if available
        if step.validation_criteria:
            criteria_text = "\n".join(f"- {criterion}" for criterion in step.validation_criteria)
            parts.append(f"\nRequirements:\n{criteria_text}")

        # Add context
        if context_parts:
            parts.append("\n" + "\n\n".join(context_parts))

        # Add generation instruction
        if surgical_mode:
            parts.append("\n\nIMPORTANT: Generate ONLY the JSON instructions object, not the complete file.")
            parts.append("The JSON should contain an 'operations' array with precise modification instructions.")
        else:
            if step.type == "refactoring":
                parts.append("\nRefactor the existing code according to the requirements above.")
            elif step.type == "code_generation":
                parts.append("\nGenerate the complete code implementation.")
            elif step.type == "analysis":
                parts.append("\nAnalyze and provide insights about the code.")
            elif step.type == "patch":
                parts.append("\nGenerate ONLY the fragment to insert at the specified marker/line.")
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
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics."""
        stats = {
            "available_providers": list(self._clients.keys()),
            "execution_mode": self.execution_mode
        }
        
        if self.fallback_cascade:
            stats["fallback_stats"] = self.fallback_cascade.get_stats()
        
        return stats
