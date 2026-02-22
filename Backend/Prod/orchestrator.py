"""Orchestrator for executing AetherFlow plans."""
import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from loguru import logger

# #region agent log
_DEBUG_LOG = "/Users/francois-jeandazin/AETHERFLOW/.cursor/debug.log"
def _dbg(hy: str, loc: str, msg: str, data: Optional[Dict] = None):
    with open(_DEBUG_LOG, "a") as f:
        f.write(json.dumps({"timestamp": int(time.time() * 1000), "hypothesisId": hy, "location": loc, "message": msg, "data": data or {}, "sessionId": "debug-session"}) + "\n")
# #endregion

from .models.plan_reader import PlanReader, Plan, Step, PlanValidationError
from .models.deepseek_client import StepResult
from .models.agent_router import AgentRouter
from .models.metrics import MetricsCollector
from .models.claude_validator import ClaudeCodeValidator
from .models.execution_monitor import ExecutionMonitor
from .config.settings import settings
from .rag import PageIndexRetriever
from .core.surgical_editor import SurgicalEditor
from .core.plan_status import update_plan_status
from .claude_helper import split_structure_and_code
from .ui.hybrid_loader import HybridLoader, Phase, StepStatus


# Phase 9B — SUBSTYLE_RULES : injection automatique de sous-styles par visual_hint.
# Coût LLM : zéro. Lookup pur, appliqué avant rendu Stenciler.
# Terminologie : grain (densité) | registre (typographie) | presence (accent)
SUBSTYLE_DEFAULTS = {"grain": "standard", "registre": "body", "presence": "neutre"}

SUBSTYLE_RULES: Dict[str, Dict[str, str]] = {
    "header":       {"grain": "standard", "registre": "heading", "presence": "actif"},
    "nav":          {"grain": "compact",  "registre": "caption", "presence": "neutre"},
    "navigation":   {"grain": "compact",  "registre": "caption", "presence": "neutre"},
    "breadcrumb":   {"grain": "compact",  "registre": "caption", "presence": "neutre"},
    "card":         {"grain": "standard", "registre": "body",    "presence": "neutre"},
    "stencil-card": {"grain": "standard", "registre": "body",    "presence": "neutre"},
    "dashboard":    {"grain": "standard", "registre": "body",    "presence": "neutre"},
    "action":       {"grain": "compact",  "registre": "caption", "presence": "actif"},
    "button":       {"grain": "compact",  "registre": "caption", "presence": "actif"},
    "deploy":       {"grain": "compact",  "registre": "caption", "presence": "actif"},
    "export":       {"grain": "compact",  "registre": "caption", "presence": "actif"},
    "form":         {"grain": "standard", "registre": "body",    "presence": "neutre"},
    "upload":       {"grain": "standard", "registre": "body",    "presence": "neutre"},
    "data-table":   {"grain": "compact",  "registre": "caption", "presence": "neutre"},
    "table":        {"grain": "compact",  "registre": "caption", "presence": "neutre"},
    "modal":        {"grain": "standard", "registre": "body",    "presence": "actif"},
    "confirm":      {"grain": "standard", "registre": "body",    "presence": "actif"},
    "stepper":      {"grain": "compact",  "registre": "caption", "presence": "actif"},
    "editor":       {"grain": "compact",  "registre": "caption", "presence": "neutre"},
    "session":      {"grain": "standard", "registre": "body",    "presence": "neutre"},
}


def inject_substyle(sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Injecte _substyle dans chaque section qui n'en a pas encore, basé sur visual_hint.

    Le champ _substyle est préfixé '_' : métadonnée système, jamais écrasée par patch LLM.
    Fallback sur SUBSTYLE_DEFAULTS si visual_hint inconnu.
    """
    for section in sections:
        if "_substyle" not in section:
            hint = str(section.get("visual_hint", "")).lower()
            # Exact match d'abord, puis match partiel sur les clés connues
            rule = SUBSTYLE_RULES.get(hint)
            if rule is None:
                rule = next((v for k, v in SUBSTYLE_RULES.items() if k in hint), SUBSTYLE_DEFAULTS)
            section["_substyle"] = rule
    return sections


class ExecutionError(Exception):
    """Raised when execution fails."""
    pass


class Orchestrator:
    """Orchestrates plan execution using AgentRouter (multi-provider support)."""

    def __init__(
        self,
        plan_reader: Optional[PlanReader] = None,
        agent_router: Optional[AgentRouter] = None,
        claude_validator: Optional[ClaudeCodeValidator] = None,
        rag_enabled: bool = True,
        execution_mode: str = "BUILD",
        enable_hybrid_loader: bool = True,
        sequential_mode: bool = False
    ):
        """
        Initialize orchestrator.

        Args:
            plan_reader: PlanReader instance (creates new if None)
            agent_router: AgentRouter instance (creates new if None)
            claude_validator: ClaudeValidator instance (creates new if None)
            rag_enabled: Whether to enable RAG for context enrichment (default True)
            execution_mode: Execution mode (FAST, BUILD, DOUBLE-CHECK)
        """
        self.plan_reader = plan_reader or PlanReader()
        self.execution_mode = execution_mode.upper()
        self.sequential_mode = sequential_mode
        # Initialize AgentRouter with prompt cache, semantic cache, and execution mode
        from .cache import PromptCache, SemanticCache
        prompt_cache = PromptCache()
        semantic_cache = SemanticCache()
        self.agent_router = agent_router or AgentRouter(
            prompt_cache=prompt_cache,
            semantic_cache=semantic_cache,
            execution_mode=self.execution_mode
        )
        self.claude_validator = claude_validator or ClaudeCodeValidator()
        self.metrics: Optional[MetricsCollector] = None
        self.monitor: Optional[ExecutionMonitor] = None
        self.enable_hybrid_loader = enable_hybrid_loader
        self.hybrid_loader: Optional[HybridLoader] = None

        # Rate limiting: semaphores per provider to limit concurrent requests
        # Limits: DeepSeek=5, Groq=10, Gemini=10, Codestral=5
        self._provider_semaphores = {
            "deepseek": asyncio.Semaphore(5),
            "groq": asyncio.Semaphore(10),
            "gemini": asyncio.Semaphore(10),
            "codestral": asyncio.Semaphore(5)
        }
        
        # Initialize RAG system
        self.rag_enabled = rag_enabled
        if self.rag_enabled:
            try:
                self.rag = PageIndexRetriever(use_embeddings=False)
                if self.rag.enabled:
                    logger.info("RAG system initialized for context enrichment")
                else:
                    logger.warning("RAG system disabled (LlamaIndex not available)")
                    self.rag_enabled = False
            except Exception as e:
                logger.warning(f"Failed to initialize RAG system: {e}")
                self.rag_enabled = False
                self.rag = None
        else:
            self.rag = None
    
    async def execute_plan(
        self,
        plan_path: Path,
        output_dir: Optional[Path] = None,
        context: Optional[str] = None,
        use_streaming: bool = False,
        execution_mode: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a plan from a JSON file.
        
        Args:
            plan_path: Path to plan JSON file
            output_dir: Directory for output files (defaults to settings)
            context: Additional context for all steps
            use_streaming: If True, use streaming mode to start execution as soon as steps are available
            execution_mode: Execution mode (FAST, BUILD, DOUBLE-CHECK). Overrides instance default.
            
        Returns:
            Dictionary with execution results and metrics
            
        Raises:
            ExecutionError: If execution fails
        """
        # Update execution mode if provided
        if execution_mode:
            self.execution_mode = execution_mode.upper()
            self.agent_router.execution_mode = self.execution_mode
        
        if use_streaming:
            return await self._execute_plan_streaming(plan_path, output_dir, context)
        
        # Read and validate plan
        try:
            plan = self.plan_reader.read(plan_path)
        except PlanValidationError as e:
            raise ExecutionError(f"Plan validation failed: {e}")
        except FileNotFoundError as e:
            raise ExecutionError(f"Plan file not found: {e}")
        
        logger.info(f"Starting execution of plan {plan.task_id}")
        logger.info(f"Plan description: {plan.description}")
        logger.info(f"Total steps: {len(plan.steps)}")
        
        # Initialize RAG references (used in return statement)
        rag_references = []
        
        # Enrich context with RAG if enabled
        enriched_context = context
        if self.rag_enabled and self.rag and self.rag.enabled:
            try:
                rag_query = f"{plan.description}. {context or ''}"
                rag_results = await self.rag.retrieve(rag_query, history=[], top_k=3)
                if rag_results:
                    rag_context_parts = []
                    for result in rag_results:
                        rag_context_parts.append(f"[{result['reference']}]\n{result['content'][:500]}")
                        rag_references.append(result['reference'])
                    rag_context = "\n\n".join(rag_context_parts)
                    enriched_context = f"Contexte projet (RAG):\n{rag_context}\n\n{context or ''}"
                    logger.info(f"Context enriched with RAG: {len(rag_results)} references")
            except Exception as e:
                logger.warning(f"RAG enrichment failed: {e}, using original context")
        
        # Initialize metrics collector
        self.metrics = MetricsCollector(plan)
        
        # Initialize execution monitor
        self.monitor = ExecutionMonitor(plan.description, len(plan.steps))
        for step in plan.steps:
            self.monitor.add_step(step.id, step.description, step.type, step.complexity)
        self.monitor.start_monitoring()
        
        # Get execution order (respecting dependencies)
        execution_order = plan.get_execution_order()
        
        logger.info(f"Execution order: {len(execution_order)} batches")
        
        # Execute steps in order
        results: Dict[str, StepResult] = {}
        
        try:
            for batch_idx, batch in enumerate(execution_order, 1):
                logger.info(f"Executing batch {batch_idx}/{len(execution_order)} ({len(batch)} steps)")
                update_plan_status(
                    batch_index=batch_idx,
                    current_step_ids=[s.id for s in batch],
                    completed_steps=list(results.keys()),
                    total_steps=len(plan.steps),
                    total_batches=len(execution_order),
                )
                # #region agent log
                t_batch = time.time(); _dbg("D", "orchestrator:batch", "batch start", {"batch_idx": batch_idx, "n_batches": len(execution_order), "n_steps": len(batch), "step_ids": [s.id for s in batch]})
                # #endregion
                # Execute steps in batch (parallelized if multiple steps)
                if len(batch) > 1:
                    # Parallel execution for multiple independent steps
                    await self._execute_batch_parallel(batch, enriched_context, results)
                else:
                    # Sequential execution for single step
                    step = batch[0]
                    await self._execute_step_with_monitoring(step, enriched_context, results)
                # #region agent log
                _dbg("D", "orchestrator:batch", "batch end", {"batch_idx": batch_idx, "duration_s": round(time.time() - t_batch, 2)})
                # #endregion
        
        finally:
            # Stop monitoring
            if self.monitor:
                self.monitor.stop_monitoring()
                self.monitor.print_final_summary()
            
            # Finalize metrics
            self.metrics.finalize()
            
            # Export results
            if output_dir:
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # Save RAG references if available
                if rag_references:
                    rag_refs_file = output_dir / "rag_references.txt"
                    with open(rag_refs_file, 'w') as f:
                        f.write("RAG Context References:\n")
                        for ref in rag_references:
                            f.write(f"- {ref}\n")
                
                # Save step outputs
                self._save_step_outputs(output_dir, plan, results)
                
                # Export metrics
                metrics_json = output_dir / f"metrics_{plan.task_id}.json"
                metrics_csv = output_dir / f"metrics_{plan.task_id}.csv"
                self.metrics.export_json(metrics_json)
                self.metrics.export_csv(metrics_csv)
        
        # Print summary
        self.metrics.print_summary()
        
        # Return results
        plan_metrics = self.metrics.get_plan_metrics()
        
        # Get prompt cache stats
        cache_stats = None
        if self.agent_router.prompt_cache:
            cache_stats = self.agent_router.prompt_cache.get_cache_summary()
        
        return {
            "plan": plan,
            "results": results,
            "metrics": plan_metrics,
            "success": plan_metrics.success_rate == 1.0,
            "rag_enabled": self.rag_enabled,
            "rag_references": rag_references if self.rag_enabled else [],
            "prompt_cache_stats": cache_stats
        }
    
    async def _execute_batch_parallel(
            self,
            batch: List[Step],
            context: Optional[str],
            results: Dict[str, StepResult]
        ) -> None:
            """
            Execute multiple independent steps in parallel using asyncio.gather().

            If sequential_mode is enabled, execute steps one by one with a pause between them.
            If file conflicts are detected (same file targeted by multiple steps), force sequential execution.

            Args:
                batch: List of steps to execute in parallel
                context: Additional context for all steps
                results: Dictionary to store step results
            """
            # Check for file conflicts before execution
            file_conflict_detected = False
            conflict_details = []
            original_sequential_mode = None
            
            if len(batch) > 1 and not self.sequential_mode:
                # Collect all target files from each step
                all_target_files = {}
                for step in batch:
                    if step.context and isinstance(step.context, dict):
                        files = step.context.get('files', [])
                        for file_path in files:
                            # Normalize path for comparison
                            normalized_path = str(Path(file_path).resolve())
                            if normalized_path in all_target_files:
                                # Conflict detected: same file targeted by multiple steps
                                file_conflict_detected = True
                                conflict_details.append({
                                    'file': normalized_path,
                                    'step1': all_target_files[normalized_path],
                                    'step2': step.id
                                })
                            else:
                                all_target_files[normalized_path] = step.id
                
                if file_conflict_detected:
                    logger.warning(f"⚠️ File conflict detected in batch of {len(batch)} steps")
                    for conflict in conflict_details:
                        logger.warning(f"  File '{conflict['file']}' targeted by steps: {conflict['step1']}, {conflict['step2']}")
                    logger.warning("🔄 Forcing sequential execution to avoid file corruption")
                    
                    # Temporarily enable sequential mode for this batch
                    original_sequential_mode = self.sequential_mode
                    self.sequential_mode = True
                    
                    try:
                        # Execute steps sequentially
                        step_results = []
                        for i, step in enumerate(batch, 1):
                            logger.info(f"📍 Step {i}/{len(batch)}: {step.id}")
                            try:
                                await self._execute_step_with_monitoring(step, context, results)
                                step_results.append(None)  # Success (result already in dict)
                            except Exception as e:
                                logger.error(f"Step {step.id} failed: {e}")
                                step_results.append(e)

                            # Pause between steps to avoid rate limiting
                            if i < len(batch):
                                logger.info("⏸️  Pausing 2s before next step...")
                                await asyncio.sleep(2)
                        
                        # Process results and handle errors
                        for step, result in zip(batch, step_results):
                            if isinstance(result, Exception):
                                logger.error(f"Unexpected error executing step {step.id}: {result}")
                                # Create failed result
                                failed_result = StepResult(
                                    step_id=step.id,
                                    success=False,
                                    output="",
                                    tokens_used=0,
                                    input_tokens=0,
                                    output_tokens=0,
                                    execution_time_ms=0,
                                    error=str(result)
                                )
                                results[step.id] = failed_result
                                self.metrics.record_step_result(step, failed_result)
                                
                                # Update monitor
                                self.monitor.complete_step(
                                    step.id,
                                    False,
                                    0.0,
                                    0,
                                    0.0,
                                    str(result)
                                )
                            else:
                                # Result is already stored in results dict by _execute_step_with_monitoring
                                if result.success:
                                    logger.info(f"✓ Step {step.id} completed successfully")
                                else:
                                    logger.error(f"✗ Step {step.id} failed: {result.error}")
                        
                        return  # Exit early, batch already handled
                    finally:
                        # Restore original sequential mode
                        if original_sequential_mode is not None:
                            self.sequential_mode = original_sequential_mode
            
            # Continue with normal execution (no conflicts or sequential mode already enabled)
            if self.sequential_mode:
                logger.info(f"🔄 SEQUENTIAL MODE: Executing {len(batch)} steps ONE AT A TIME")
                step_results = []
                for i, step in enumerate(batch, 1):
                    logger.info(f"📍 Step {i}/{len(batch)}: {step.id}")
                    try:
                        await self._execute_step_with_monitoring(step, context, results)
                        step_results.append(None)  # Success (result already in dict)
                    except Exception as e:
                        logger.error(f"Step {step.id} failed: {e}")
                        step_results.append(e)

                    # Pause between steps to avoid rate limiting
                    if i < len(batch):
                        logger.info("⏸️  Pausing 2s before next step...")
                        await asyncio.sleep(2)
            else:
                logger.info(f"Executing {len(batch)} steps in parallel")

                # Create async tasks for each step
                tasks = [
                    self._execute_step_with_monitoring(step, context, results)
                    for step in batch
                ]

                # Execute all steps in parallel with asyncio.gather
                # return_exceptions=True allows other steps to continue if one fails
                step_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Restore original sequential mode if it was temporarily changed
            if original_sequential_mode is not None:
                self.sequential_mode = original_sequential_mode

            # Process results and handle errors
            for step, result in zip(batch, step_results):
                if isinstance(result, Exception):
                    logger.error(f"Unexpected error executing step {step.id}: {result}")
                    # Create failed result
                    failed_result = StepResult(
                        step_id=step.id,
                        success=False,
                        output="",
                        tokens_used=0,
                        input_tokens=0,
                        output_tokens=0,
                        execution_time_ms=0,
                        error=str(result)
                    )
                    results[step.id] = failed_result
                    self.metrics.record_step_result(step, failed_result)
                    
                    # Update monitor
                    self.monitor.complete_step(
                        step.id,
                        False,
                        0.0,
                        0,
                        0.0,
                        str(result)
                    )
                else:
                    # Result is already stored in results dict by _execute_step_with_monitoring
                    if result.success:
                        logger.info(f"✓ Step {step.id} completed successfully")
                    else:
                        logger.error(f"✗ Step {step.id} failed: {result.error}")

    async def _execute_step_with_rate_limit(
        self,
        step: Step,
        context: Optional[str],
        results: Dict[str, StepResult],
        semaphore: asyncio.Semaphore
    ) -> StepResult:
        """
        Execute a step with rate limiting via semaphore.
        
        Args:
            step: Step to execute
            context: Additional context
            results: Dictionary to store results
            semaphore: Semaphore for rate limiting
            
        Returns:
            StepResult
        """
        async with semaphore:
            return await self._execute_step_with_monitoring(step, context, results)
    
    async def _execute_step_with_monitoring(
        self,
        step: Step,
        context: Optional[str],
        results: Dict[str, StepResult]
    ) -> StepResult:
        """
        Execute a single step with monitoring.
        
        This method encapsulates step execution with monitoring to facilitate parallelization.
        
        Args:
            step: Step to execute
            context: Additional context
            results: Dictionary to store step results
            
        Returns:
            StepResult with execution results
        """
        try:
            # Get provider info before execution
            provider_name = self.agent_router.select_provider_for_step(step)
            # #region agent log
            t_step = time.time(); _dbg("A", "orchestrator:step", "step start", {"step_id": step.id, "provider": provider_name})
            # #endregion
            # Start monitoring
            self.monitor.start_step(step.id, provider_name)
            self.monitor.update_step_progress(step.id, f"Executing with {provider_name}...")
            
            # Execute the step
            result = await self._execute_step(step, context, results)
            # #region agent log
            _dbg("A", "orchestrator:step", "step end", {"step_id": step.id, "duration_s": round(time.time() - t_step, 2), "success": result.success})
            # #endregion
            
            # Store result
            results[step.id] = result
            
            # Error survey: log step failure
            if not result.success:
                try:
                    from .core.error_survey import log_aetherflow_error
                    log_aetherflow_error(
                        title=f"Step {step.id} failed",
                        nature="step_failed",
                        proposed_solution="Re-run the step, adjust the plan, or fix the prompt.",
                        raw_error=result.error,
                        step_id=step.id,
                    )
                except Exception as survey_err:
                    logger.debug(f"Error survey log failed: {survey_err}")
            
            # Record metrics with provider info
            self.metrics.record_step_result(step, result, provider=provider_name)
            
            # Update monitor
            self.monitor.complete_step(
                step.id,
                result.success,
                result.execution_time_ms,
                result.tokens_used,
                result.cost_usd,
                result.error
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Unexpected error executing step {step.id}: {e}")
            # Create failed result
            failed_result = StepResult(
                step_id=step.id,
                success=False,
                output="",
                tokens_used=0,
                input_tokens=0,
                output_tokens=0,
                execution_time_ms=0,
                error=str(e)
            )
            results[step.id] = failed_result
            self.metrics.record_step_result(step, failed_result)
            try:
                from .core.error_survey import log_aetherflow_error
                log_aetherflow_error(
                    title=f"Step {step.id} exception",
                    nature="step_exception",
                    proposed_solution="Check logs and fix the cause (prompt, provider, or code).",
                    raw_error=str(e),
                    step_id=step.id,
                )
            except Exception as survey_err:
                logger.debug(f"Error survey log failed: {survey_err}")
            # Update monitor
            self.monitor.complete_step(
                step.id,
                False,
                0.0,
                0,
                0.0,
                str(e)
            )
            return failed_result
    
    def _load_existing_files(self, step: Step) -> Dict[str, Optional[str]]:
        """
        Load existing file contents from step.context.get("files").
        
        Args:
            step: Step with context containing file paths
            
        Returns:
            Dictionary mapping file paths to their contents (or None if file doesn't exist)
        """
        files_content = {}
        
        # Get file paths from step context
        if not step.context or not isinstance(step.context, dict):
            return files_content
        
        file_paths = step.context.get("files", [])
        if not file_paths:
            return files_content
        
        # Limit number of files to avoid token overflow
        MAX_FILES_PER_STEP = 5
        if len(file_paths) > MAX_FILES_PER_STEP:
            logger.warning(
                f"Step {step.id} has {len(file_paths)} files, limiting to {MAX_FILES_PER_STEP} "
                f"(keeping first {MAX_FILES_PER_STEP})"
            )
            file_paths = file_paths[:MAX_FILES_PER_STEP]
        
        # Resolve project root (assuming orchestrator.py is in Backend/Prod/)
        project_root = Path(__file__).parent.parent.parent
        
        # Limit total size to avoid token overflow (~250k tokens ≈ 1MB)
        MAX_TOTAL_SIZE = 1024 * 1024  # 1MB total
        MAX_FILE_SIZE = 200 * 1024  # 200KB per file
        total_size = 0
        
        for file_path_str in file_paths:
            try:
                # Resolve file path (relative or absolute)
                file_path = Path(file_path_str)
                if not file_path.is_absolute():
                    file_path = project_root / file_path
                
                # Normalize path
                file_path = file_path.resolve()
                
                # Check if file exists
                if not file_path.exists():
                    logger.debug(f"File not found (will be created): {file_path}")
                    files_content[file_path_str] = None
                    continue
                
                # Check if it's a file (not a directory)
                if not file_path.is_file():
                    logger.warning(f"Path is not a file: {file_path}")
                    files_content[file_path_str] = None
                    continue
                
                # Check file size
                file_size = file_path.stat().st_size
                if file_size > MAX_FILE_SIZE:
                    logger.warning(
                        f"File {file_path_str} is too large ({file_size} bytes > {MAX_FILE_SIZE} bytes). "
                        f"Will truncate to fit token limits."
                    )
                
                # Check total size limit
                if total_size + file_size > MAX_TOTAL_SIZE:
                    logger.warning(
                        f"Total file size limit reached ({total_size + file_size} bytes > {MAX_TOTAL_SIZE} bytes). "
                        f"Skipping remaining files."
                    )
                    break
                
                # Read file content
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Truncate if necessary (keep beginning and end)
                    if len(content.encode('utf-8')) > MAX_FILE_SIZE:
                        content_bytes = content.encode('utf-8')
                        # Keep first 160KB and last 40KB
                        keep_start = 160 * 1024
                        keep_end = 40 * 1024
                        if len(content_bytes) > keep_start + keep_end:
                            start_part = content_bytes[:keep_start].decode('utf-8', errors='ignore')
                            end_part = content_bytes[-keep_end:].decode('utf-8', errors='ignore')
                            content = f"{start_part}\n\n[... truncated {len(content_bytes) - keep_start - keep_end} bytes ...]\n\n{end_part}"
                            logger.info(f"Truncated file {file_path_str} to fit size limits")
                    
                    files_content[file_path_str] = content
                    total_size += len(content.encode('utf-8'))
                    logger.debug(f"Loaded file {file_path_str} ({len(content)} chars)")
                    
                except UnicodeDecodeError:
                    logger.warning(f"File {file_path_str} is not UTF-8 encoded, skipping")
                    files_content[file_path_str] = None
                except PermissionError:
                    logger.warning(f"Permission denied reading file {file_path_str}")
                    files_content[file_path_str] = None
                except Exception as e:
                    logger.warning(f"Error reading file {file_path_str}: {e}")
                    files_content[file_path_str] = None
                    
            except Exception as e:
                logger.warning(f"Error processing file path {file_path_str}: {e}")
                files_content[file_path_str] = None
        
        logger.info(f"Loaded {sum(1 for v in files_content.values() if v is not None)}/{len(file_paths)} existing files for step {step.id}")
        return files_content
    
    def _load_input_files(self, step: Step) -> Dict[str, Optional[str]]:
        """
        Load read-only file contents from step.context.get("input_files").
        Used for report/inventory tasks: inject genome, PRD, etc. without applying output to them.
        """
        files_content: Dict[str, Optional[str]] = {}
        if not step.context or not isinstance(step.context, dict):
            return files_content
        file_paths = step.context.get("input_files") or []
        if not file_paths:
            return files_content
        MAX_FILES = 5
        if len(file_paths) > MAX_FILES:
            logger.warning(f"Step {step.id} has {len(file_paths)} input_files, limiting to {MAX_FILES}")
            file_paths = file_paths[:MAX_FILES]
        project_root = Path(__file__).parent.parent.parent
        MAX_TOTAL_SIZE = 1024 * 1024  # 1MB
        MAX_FILE_SIZE = 200 * 1024  # 200KB per file
        total_size = 0
        for file_path_str in file_paths:
            try:
                file_path = Path(file_path_str)
                if not file_path.is_absolute():
                    file_path = project_root / file_path
                file_path = file_path.resolve()
                if not file_path.exists() or not file_path.is_file():
                    files_content[file_path_str] = None
                    continue
                file_size = file_path.stat().st_size
                if total_size + file_size > MAX_TOTAL_SIZE:
                    break
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                content_bytes = content.encode('utf-8')
                if len(content_bytes) > MAX_FILE_SIZE:
                    keep_start, keep_end = 160 * 1024, 40 * 1024
                    if len(content_bytes) > keep_start + keep_end:
                        content = content_bytes[:keep_start].decode('utf-8', errors='ignore') + "\n\n[... truncated ...]\n\n" + content_bytes[-keep_end:].decode('utf-8', errors='ignore')
                files_content[file_path_str] = content
                total_size += len(content.encode('utf-8'))
            except Exception as e:
                logger.warning(f"Error reading input_file {file_path_str}: {e}")
                files_content[file_path_str] = None
        if files_content:
            logger.info(f"Loaded {sum(1 for v in files_content.values() if v is not None)} input_files for step {step.id}")
        return files_content

    def _build_reasoning_prompt(
        self,
        step: Step,
        step_context: str,
        ast_contexts: Dict[str, str]
    ) -> str:
        """Build a prompt for the reasoning pre-pass."""
        context_preview = step_context[:1000] + "..." if len(step_context) > 1000 else step_context

        ast_summary = ""
        if ast_contexts:
            ast_summary_parts = ["AST Structure Summary:"]
            for file_path, ast_context in ast_contexts.items():
                ast_summary_parts.append(f"\n=== File: {file_path} ===")
                ast_preview = ast_context[:500] + "..." if len(ast_context) > 500 else ast_context
                ast_summary_parts.append(ast_preview)
            ast_summary = "\n".join(ast_summary_parts)

        return f"""TASK ANALYSIS AND REASONING REQUEST

TASK DESCRIPTION:
{step.description}

CONTEXT (PREVIEW):
{context_preview}

{ast_summary if ast_summary else "No AST structure available."}

REASONING INSTRUCTIONS:
1. Analyze the task requirements and how they relate to the existing code structure
2. Identify which files need modifications and what type of changes are needed
3. Consider dependencies between different parts of the code
4. Think about potential edge cases or conflicts
5. Plan the sequence of operations for surgical editing
6. Consider how to maintain code consistency and follow existing patterns

OUTPUT FORMAT:
Provide a concise, step-by-step reasoning plan. Focus on:
- What needs to be changed
- Where to make changes (specific files/classes/methods)
- How to integrate changes with existing code
- Any potential issues to watch out for

Your reasoning will be used to guide the actual code generation step.
"""

    async def _reasoning_pre_pass(
        self,
        step: Step,
        step_context: str,
        ast_contexts: Dict[str, str]
    ) -> str:
        """
        Perform a reasoning pre-pass using DeepSeek-Reasoner (R1) model.

        Analyzes task + AST structure before the main code generation step.
        Returns reasoning text to inject into step_context, or '' on any failure.
        """
        try:
            from .models.deepseek_client import DeepSeekClient
            reasoner_client = DeepSeekClient(model='deepseek-reasoner')

            reasoning_prompt = self._build_reasoning_prompt(step, step_context, ast_contexts)

            try:
                reasoning_result = await asyncio.wait_for(
                    reasoner_client.generate(
                        prompt=reasoning_prompt,
                        max_tokens=1000,
                        temperature=0.3
                    ),
                    timeout=120.0
                )
            except asyncio.TimeoutError:
                logger.warning(f"Reasoning pre-pass timeout for step {step.id}")
                return ""
            finally:
                await reasoner_client.close()

            if reasoning_result.success and reasoning_result.code:
                reasoning_text = reasoning_result.code
                logger.info(f"Reasoning pre-pass completed for step {step.id} ({len(reasoning_text)} chars)")
                return reasoning_text
            else:
                logger.warning(f"Reasoning pre-pass returned no output for step {step.id}: {reasoning_result.error}")
                return ""

        except Exception as e:
            logger.warning(f"Reasoning pre-pass failed for step {step.id}: {e}")
            return ""

    async def _execute_step(
        self,
        step: Step,
        context: Optional[str],
        previous_results: Dict[str, StepResult]
    ) -> StepResult:
        """
        Execute a single step.
        
        Args:
            step: Step to execute
            context: Additional context
            previous_results: Results from previous steps
            
        Returns:
            StepResult with execution results
        """
        # Build context from previous results if needed
        step_context = context or ""
        
        if step.dependencies:
            # Add outputs from dependent steps to context
            dep_outputs = []
            for dep_id in step.dependencies:
                if dep_id in previous_results:
                    dep_result = previous_results[dep_id]
                    if dep_result.success:
                        dep_outputs.append(f"Previous step {dep_id} output:\n{dep_result.output}")
            
            if dep_outputs:
                step_context = "\n\n".join([step_context] + dep_outputs) if step_context else "\n\n".join(dep_outputs)
        
        # Load input_files (read-only) and inject as reference data
        input_files = self._load_input_files(step)
        if input_files:
            ref_parts = ["\n\nReference data (read-only, do not modify):\n"]
            for path, content in input_files.items():
                if content is not None:
                    ref_parts.append(f"=== File: {path} ===\n{content}\n")
            step_context = "\n\n".join([step_context] + ref_parts) if step_context else "".join(ref_parts)
        
        # Load existing files and inject into context
        existing_files = self._load_existing_files(step)
        surgical_mode = False
        ast_contexts = {}

        if existing_files:
            # Check if surgical mode should be activated
            # Surgical mode: enabled by default for refactoring/code_generation, or explicitly via step.context
            project_root = Path(__file__).parent.parent.parent

            # First, check if we have any Python files that exist AND have content
            has_python_files = False
            has_existing_code = False
            for file_path_str, content in existing_files.items():
                if content is not None and len(content.strip()) > 0:
                    # File exists and has content
                    has_existing_code = True
                    file_path = Path(file_path_str)
                    if not file_path.is_absolute():
                        file_path = project_root / file_path
                    if file_path.suffix == '.py' and file_path.exists():
                        has_python_files = True
                        break

            # Surgical mode: ONLY for refactoring (modifying existing code).
            # code_generation = new file or full rewrite → overwrite direct, no surgical JSON needed.
            surgical_mode = (
                has_existing_code and
                self.execution_mode in ["BUILD", "DOUBLE-CHECK"] and
                has_python_files and
                step.type == 'refactoring' and
                step.context.get('surgical_mode', True)  # Allow disabling via context
            )

            logger.info(f'Surgical mode: {surgical_mode} (execution_mode={self.execution_mode}, step_type={step.type}, has_python_files={has_python_files})')
            
            files_section_parts = ["\n\nExisting code files:\n"]
            
            for file_path_str, content in existing_files.items():
                if content is not None:
                    files_section_parts.append(f"=== File: {file_path_str} ===\n{content}\n")
                    
                    # If surgical mode and Python file, parse AST
                    if surgical_mode:
                        file_path = Path(file_path_str)
                        if not file_path.is_absolute():
                            file_path = project_root / file_path
                        
                        if file_path.suffix == '.py' and file_path.exists():
                            try:
                                editor = SurgicalEditor(file_path)
                                if editor.prepare():
                                    ast_context = editor.get_ast_context()
                                    ast_contexts[file_path_str] = ast_context
                                    logger.info(f"Parsed AST for {file_path_str} (surgical mode)")
                                else:
                                    logger.warning(f"Failed to prepare AST parser for {file_path_str}")
                            except Exception as e:
                                logger.warning(f"Failed to parse AST for {file_path_str}: {e}")
                                # Continue without AST for this file, but keep surgical mode enabled
                                # if at least one file was successfully parsed
            
            if len(files_section_parts) > 1:  # More than just the header
                files_section = "".join(files_section_parts)
                
                # Add AST context if surgical mode and we have parsed ASTs
                if surgical_mode and ast_contexts:
                    ast_section_parts = ["\n\nAST Structure:\n"]
                    for file_path_str, ast_context in ast_contexts.items():
                        ast_section_parts.append(f"=== File: {file_path_str} ===\n{ast_context}\n")
                    files_section += "\n".join(ast_section_parts)
                elif surgical_mode and not ast_contexts:
                    # Surgical mode enabled but no AST parsed - warn but continue
                    logger.warning("Surgical mode enabled but no AST contexts available. LLM will use file content only.")
                
                # Add instructions based on step type and mode
                if surgical_mode:
                    files_section += """

SURGICAL MODE INSTRUCTIONS:
Generate ONLY these operation types (no others will work):
- add_import: Add an import statement
- add_function: Add a standalone function (NOT a route decorator, just the function)
- add_class: Add a new class definition
- add_method: Add a method to an existing class
- modify_method: Modify an existing method
- replace_import: Replace one import with another

CRITICAL - FORBIDDEN OPERATIONS (will cause errors):
❌ add_route (not supported)
❌ add_to_router (not supported)
❌ add_endpoint (not supported)
❌ add_decorator (not supported)

For FastAPI routes, use add_function with the full decorated function:
{
  "type": "add_function",
  "code": "@router.get('/endpoint')\\nasync def my_endpoint():\\n    return {'status': 'ok'}"
}

JSON structure:
{
  "operations": [
    {
      "type": "add_method|modify_method|add_import|replace_import|add_class|add_function",
      "target": "ClassName or ClassName.method_name",
      "position": "after|before|end",
      "after_method": "method_name",
      "code": "def new_method(self): ..."
    }
  ]
}

Focus on precise, minimal changes that integrate seamlessly with existing code.
"""
                else:
                    if step.type == "refactoring":
                        files_section += "\nModify the existing code above according to the requirements. Preserve existing structure, imports, and patterns.\n"
                    elif step.type == "code_generation":
                        files_section += "\nAdd new code to the existing files above. Ensure compatibility with existing imports and structure.\n"
                    elif step.type == "patch":
                        files_section += "\nGenerate ONLY the fragment to insert at the specified marker/line (patch mode). Do not output the complete file.\n"
                
                step_context = "\n\n".join([step_context, files_section]) if step_context else files_section
        
        # Reasoning pre-pass (opt-in via step.context.pre_reasoning: true)
        if step.context and isinstance(step.context, dict) and step.context.get('pre_reasoning', False):
            logger.info(f"Starting reasoning pre-pass for step {step.id}")
            reasoning_text = await self._reasoning_pre_pass(step, step_context, ast_contexts)
            if reasoning_text:
                reasoning_block = f"\n\n[REASONING - DeepSeek R1]\n{reasoning_text}\n[/REASONING]\n\n"
                step_context = step_context + reasoning_block if step_context else reasoning_block
                logger.info(f"Injected reasoning block ({len(reasoning_text)} chars) into step context")
            else:
                logger.warning(f"Reasoning pre-pass returned empty text for step {step.id}")

        # Execute step via AgentRouter (multi-provider)
        # Pass surgical_mode flag to agent_router
        # Pass loaded_files for smart context estimation
        result = await self.agent_router.execute_step(
            step, step_context, surgical_mode=surgical_mode, loaded_files=existing_files
        )

        # Apply surgical instructions if in surgical mode and execution succeeded
        if surgical_mode and result.success and result.output:
            from .core.surgical_editor import SurgicalInstructionParser

            # Check if the output contains surgical instructions
            if SurgicalInstructionParser.is_surgical_output(result.output):
                logger.info(f"Applying surgical instructions for step {step.id}")

                # Apply to each Python file that was parsed
                applied_files = []
                application_errors = []

                for file_path_str in existing_files.keys():
                    file_path = Path(file_path_str)
                    if not file_path.is_absolute():
                        file_path = project_root / file_path

                    if file_path.suffix != '.py':
                        continue

                    if existing_files[file_path_str] is None:
                        # NEW FILE: Create it directly using SurgicalEditor helper
                        try:
                            success, message = SurgicalEditor.create_new_file(file_path, result.output)
                            if success:
                                applied_files.append(f"{file_path} (created)")
                                logger.info(message)
                            else:
                                # FALLBACK: Extract code from surgical JSON and write directly
                                logger.warning(f"Surgical creation failed for {file_path}: {message}")
                                logger.info(f"Attempting fallback: extract code from operations")

                                from .core.surgical_editor import SurgicalInstructionParser
                                operations, parse_error = SurgicalInstructionParser.parse_instructions(result.output)

                                if operations:
                                    # Extract all code from operations
                                    code_parts = []
                                    for op in operations:
                                        if hasattr(op, 'code') and op.code:
                                            code_parts.append(op.code)

                                    if code_parts:
                                        fallback_code = "\n\n".join(code_parts)
                                        file_path.parent.mkdir(parents=True, exist_ok=True)
                                        file_path.write_text(fallback_code, encoding='utf-8')
                                        applied_files.append(f"{file_path} (created via fallback)")
                                        logger.info(f"✅ Fallback successful: wrote {len(fallback_code)} chars to {file_path}")
                                    else:
                                        application_errors.append(f"{file_path}: {message}")
                                        logger.warning(f"Failed to create {file_path}: {message}")
                                else:
                                    application_errors.append(f"{file_path}: {message}")
                                    logger.warning(f"Failed to create {file_path}: {message}")
                        except Exception as e:
                            application_errors.append(f"{file_path}: Failed to create new file: {e}")
                            logger.warning(f"Error creating new file {file_path}: {e}")
                    else:
                        # EXISTING FILE: Apply surgical edits
                        if file_path.exists():
                            try:
                                editor = SurgicalEditor(file_path)
                                if editor.prepare():
                                    success, modified_code, original_code = editor.apply_instructions(result.output)

                                    if success and modified_code:
                                        # Write the modified code back to the file
                                        file_path.write_text(modified_code, encoding='utf-8')
                                        applied_files.append(f"{file_path} (modified)")
                                        logger.info(f"Applied surgical edits to {file_path}")
                                    elif not success:
                                        # VETO: Stop the append fallback and alert the user
                                        error_msg = f"Surgical modification failed for {file_path}: {modified_code}"
                                        logger.error(f"❌ {error_msg}")
                                        
                                        # Strong visual alert in logs and results
                                        alert_banner = "\n" + "!" * 80 + "\n"
                                        alert_banner += "⚠️  ALERT: MODIFICATION REJECTED\n"
                                        alert_banner += f"The surgical edit for {file_path} failed or produced invalid code.\n"
                                        alert_banner += "THE FILE HAS BEEN PRESERVED IN ITS ORIGINAL STATE TO PREVENT CORRUPTION.\n"
                                        alert_banner += "!" * 80 + "\n"
                                        
                                        logger.critical(alert_banner)
                                        application_errors.append(f"{file_path}: {modified_code}")
                                        
                                        # Optional: Save faulty JSON for debugging
                                        try:
                                            debug_path = project_root / ".gemini" / "debug" / f"failed_surgery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                                            debug_path.parent.mkdir(parents=True, exist_ok=True)
                                            debug_path.write_text(result.output, encoding='utf-8')
                                            logger.info(f"Faulty instructions saved to {debug_path}")
                                        except:
                                            pass

                            except Exception as e:
                                application_errors.append(f"{file_path}: {e}")
                                logger.warning(f"Error applying surgical edits to {file_path}: {e}")

                # Update result output with application summary
                if applied_files:
                    result.output = f"Surgical edits applied to: {', '.join(applied_files)}\n\nOriginal instructions:\n{result.output}"
                if application_errors:
                    result.output += f"\n\nApplication errors:\n" + "\n".join(application_errors)

        return result
    
    async def _request_correction(
        self,
        step: Step,
        original_result: StepResult,
        correction_prompt: str,
        context: Optional[str]
    ) -> StepResult:
        """
        Request correction based on Claude's feedback.

        Args:
            step: The step to correct
            original_result: The original result
            correction_prompt: Specific correction instructions from Claude
            context: Additional context

        Returns:
            Corrected StepResult
        """
        # Build correction prompt
        correction_context = f"""
Original task: {step.description}

Original output:
{original_result.output}

Correction needed:
{correction_prompt}

Please provide the corrected version.
"""

        if context:
            correction_context = f"{context}\n\n{correction_context}"

        # Create a temporary step for correction
        correction_step = Step({
            "id": f"{step.id}_correction",
            "description": f"Correction: {correction_prompt}",
            "type": step.type,
            "complexity": step.complexity,
            "estimated_tokens": step.estimated_tokens,
            "dependencies": [],
            "validation_criteria": step.validation_criteria
        })

        # Execute correction via AgentRouter
        correction_result = await self.agent_router.execute_step(
            correction_step,
            correction_context
        )

        return correction_result
    
    def _save_step_outputs(
        self,
        output_dir: Path,
        plan: Plan,
        results: Dict[str, StepResult]
    ) -> None:
        """
        Save step outputs to files.
        
        Args:
            output_dir: Directory to save outputs
            plan: The executed plan
            results: Step execution results
        """
        outputs_dir = output_dir / "step_outputs"
        outputs_dir.mkdir(parents=True, exist_ok=True)
        
        for step in plan.steps:
            if step.id in results:
                result = results[step.id]
                structure_part, code_part = split_structure_and_code(result.output)

                # Save code part for apply (structure-free; apply only reads this when present)
                code_file = outputs_dir / f"{step.id}_code.txt"
                code_file.write_text(code_part, encoding="utf-8")

                # Save structure part separately (never read by apply)
                if structure_part:
                    structure_file = outputs_dir / f"{step.id}_structure.md"
                    structure_file.write_text(structure_part, encoding="utf-8")

                # Save full output for debug / backward compat (get_step_output falls back to this if _code.txt missing)
                output_file = outputs_dir / f"{step.id}.txt"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(f"Step: {step.id}\n")
                    f.write(f"Description: {step.description}\n")
                    f.write(f"Type: {step.type}\n")
                    f.write(f"Success: {result.success}\n")
                    f.write(f"Tokens: {result.tokens_used}\n")
                    f.write(f"Cost: ${result.cost_usd:.4f}\n")
                    f.write(f"Time: {result.execution_time_ms:.0f}ms\n")
                    if result.error:
                        f.write(f"Error: {result.error}\n")
                    f.write("\n" + "=" * 60 + "\n\n")
                    f.write(result.output)

        logger.info(f"Step outputs saved to {outputs_dir}")
    
    async def _execute_plan_streaming(
        self,
        plan_path: Path,
        output_dir: Optional[Path],
        context: Optional[str]
    ) -> Dict[str, Any]:
        """
        Execute a plan using streaming mode - starts execution as soon as steps are available.
        
        This method reads steps from the plan file as they become available and begins
        execution immediately for steps without dependencies, allowing parallel execution
        of plan generation and step execution.
        
        Args:
            plan_path: Path to plan JSON file
            output_dir: Directory for output files
            context: Additional context for all steps
            
        Returns:
            Dictionary with execution results and metrics
        """
        logger.info("Starting streaming execution mode")
        
        # Track steps and their dependencies
        all_steps: Dict[str, Step] = {}
        step_dependencies: Dict[str, List[str]] = {}
        completed_steps: set = set()
        results: Dict[str, StepResult] = {}
        
        # Track plan metadata (will be populated as we read)
        task_id: Optional[str] = None
        plan_description: Optional[str] = None
        
        # Initialize metrics and monitor (will be updated as steps arrive)
        plan_stub = None
        self.metrics = None
        self.monitor = None
        
        # RAG references
        rag_references = []
        enriched_context = context
        
        try:
            # Stream steps as they become available
            async for step in self.plan_reader.read_streaming(plan_path):
                logger.info(f"Received step via streaming: {step.id}")
                
                # Store step
                all_steps[step.id] = step
                step_dependencies[step.id] = step.dependencies.copy()
                
                # Update plan metadata if available
                # Note: We'd need to read metadata separately, for now we'll infer from first step
                if task_id is None:
                    # Try to read full plan to get metadata (one-time read)
                    try:
                        temp_plan = self.plan_reader.read(plan_path)
                        task_id = temp_plan.task_id
                        plan_description = temp_plan.description
                        
                        # Initialize metrics and monitor now that we have plan info
                        self.metrics = MetricsCollector(temp_plan)
                        self.monitor = ExecutionMonitor(plan_description, len(temp_plan.steps))
                        for existing_step in temp_plan.steps:
                            self.monitor.add_step(
                                existing_step.id,
                                existing_step.description,
                                existing_step.type,
                                existing_step.complexity
                            )
                        self.monitor.start_monitoring()
                        
                        # Enrich context with RAG if enabled
                        if self.rag_enabled and self.rag and self.rag.enabled:
                            try:
                                rag_query = f"{plan_description}. {context or ''}"
                                rag_results = await self.rag.retrieve(rag_query, history=[], top_k=3)
                                if rag_results:
                                    rag_context_parts = []
                                    for result in rag_results:
                                        rag_context_parts.append(f"[{result['reference']}]\n{result['content'][:500]}")
                                        rag_references.append(result['reference'])
                                    rag_context = "\n\n".join(rag_context_parts)
                                    enriched_context = f"Contexte projet (RAG):\n{rag_context}\n\n{context or ''}"
                                    logger.info(f"Context enriched with RAG: {len(rag_results)} references")
                            except Exception as e:
                                logger.warning(f"RAG enrichment failed: {e}, using original context")
                    except Exception as e:
                        logger.warning(f"Could not read full plan for metadata: {e}")
                        # Create stub plan for metrics
                        from .models.plan_reader import Plan
                        plan_stub = Plan({
                            "task_id": "streaming_task",
                            "description": "Streaming execution",
                            "steps": [],
                            "metadata": {}
                        })
                        self.metrics = MetricsCollector(plan_stub)
                        self.monitor = ExecutionMonitor("Streaming execution", 0)
                        self.monitor.start_monitoring()
                
                # Check if this step is ready to execute (no dependencies or all dependencies completed)
                ready_to_execute = True
                for dep_id in step.dependencies:
                    if dep_id not in completed_steps:
                        ready_to_execute = False
                        break
                
                if ready_to_execute:
                    # Execute step immediately
                    logger.info(f"Step {step.id} is ready, executing immediately")
                    await self._execute_step_with_monitoring(step, enriched_context, results)
                    completed_steps.add(step.id)
                    
                    # Check if any other steps are now ready
                    await self._check_and_execute_ready_steps(
                        all_steps, completed_steps, enriched_context, results
                    )
                else:
                    logger.debug(f"Step {step.id} waiting for dependencies: {step.dependencies}")
            
            # After streaming is complete, execute any remaining steps
            logger.info("Streaming complete, executing remaining steps")
            await self._check_and_execute_ready_steps(
                all_steps, completed_steps, enriched_context, results
            )
            
            # Verify all steps were executed
            if len(completed_steps) < len(all_steps):
                missing = set(all_steps.keys()) - completed_steps
                logger.warning(f"Some steps were not executed: {missing}")
                # Try to execute remaining steps (may have dependency issues)
                for step_id in missing:
                    step = all_steps[step_id]
                    # Check dependencies again
                    ready = all(dep_id in completed_steps for dep_id in step.dependencies)
                    if ready:
                        await self._execute_step_with_monitoring(step, enriched_context, results)
                        completed_steps.add(step_id)
            
            # Get final plan for return value
            try:
                final_plan = self.plan_reader.read(plan_path)
            except Exception as e:
                logger.warning(f"Could not read final plan: {e}")
                # Create plan from collected steps
                from .models.plan_reader import Plan
                final_plan = Plan({
                    "task_id": task_id or "streaming_task",
                    "description": plan_description or "Streaming execution",
                    "steps": [{
                        "id": step.id,
                        "description": step.description,
                        "type": step.type,
                        "complexity": step.complexity,
                        "estimated_tokens": step.estimated_tokens,
                        "dependencies": step.dependencies,
                        "validation_criteria": step.validation_criteria,
                        "context": step.context
                    } for step in all_steps.values()],
                    "metadata": {}
                })
        
        finally:
            # Stop monitoring
            if self.monitor:
                self.monitor.stop_monitoring()
                self.monitor.print_final_summary()
            
            # Finalize metrics
            if self.metrics:
                self.metrics.finalize()
            
            # Export results
            if output_dir:
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # Save RAG references if available
                if rag_references:
                    rag_refs_file = output_dir / "rag_references.txt"
                    with open(rag_refs_file, 'w') as f:
                        f.write("RAG Context References:\n")
                        for ref in rag_references:
                            f.write(f"- {ref}\n")
                
                # Save step outputs
                if final_plan:
                    self._save_step_outputs(output_dir, final_plan, results)
                    
                    # Export metrics
                    if self.metrics:
                        metrics_json = output_dir / f"metrics_{final_plan.task_id}.json"
                        metrics_csv = output_dir / f"metrics_{final_plan.task_id}.csv"
                        self.metrics.export_json(metrics_json)
                        self.metrics.export_csv(metrics_csv)
        
        # Print summary
        if self.metrics:
            self.metrics.print_summary()
        
        # Return results
        plan_metrics = self.metrics.get_plan_metrics() if self.metrics else None
        
        # Get prompt cache stats
        cache_stats = None
        if self.agent_router.prompt_cache:
            cache_stats = self.agent_router.prompt_cache.get_cache_summary()
        
        return {
            "plan": final_plan,
            "results": results,
            "metrics": plan_metrics,
            "success": plan_metrics.success_rate == 1.0 if plan_metrics else False,
            "rag_enabled": self.rag_enabled,
            "rag_references": rag_references if self.rag_enabled else [],
            "prompt_cache_stats": cache_stats
        }
    
    async def _check_and_execute_ready_steps(
        self,
        all_steps: Dict[str, Step],
        completed_steps: set,
        enriched_context: Optional[str],
        results: Dict[str, StepResult]
    ) -> None:
        """
        Check for steps that are now ready to execute and execute them.
        
        Args:
            all_steps: Dictionary of all steps
            completed_steps: Set of completed step IDs
            enriched_context: Enriched context
            results: Dictionary to store results
        """
        # Find steps that are ready (all dependencies completed)
        ready_steps = []
        for step_id, step in all_steps.items():
            if step_id not in completed_steps:
                if all(dep_id in completed_steps for dep_id in step.dependencies):
                    ready_steps.append(step)
        
        # Execute ready steps in parallel
        if ready_steps:
            logger.info(f"Found {len(ready_steps)} ready steps, executing in parallel")
            await self._execute_batch_parallel(ready_steps, enriched_context, results)
            for step in ready_steps:
                completed_steps.add(step.id)
            
            # Recursively check for more ready steps
            await self._check_and_execute_ready_steps(
                all_steps, completed_steps, enriched_context, results
            )
    
    async def execute_proto_workflow(
        self,
        plan_path: Path,
        output_dir: Optional[Path] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute PROTO workflow: FAST → DOUBLE-CHECK.
        
        Args:
            plan_path: Path to plan JSON file
            output_dir: Output directory for results
            context: Additional context
            
        Returns:
            Dictionary with workflow results
        """
        from .workflows.proto import ProtoWorkflow
        
        workflow = ProtoWorkflow()
        return await workflow.execute(plan_path, output_dir, context)
    
    async def execute_prod_workflow(
        self,
        plan_path: Path,
        output_dir: Optional[Path] = None,
        context: Optional[str] = None,
        guidelines_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Execute PROD workflow: FAST draft → BUILD refactor → DOUBLE-CHECK.
        
        Args:
            plan_path: Path to plan JSON file
            output_dir: Output directory for results
            context: Additional context
            guidelines_path: Path to guidelines file (optional)
            
        Returns:
            Dictionary with workflow results
        """
        from .workflows.prod import ProdWorkflow
        
        workflow = ProdWorkflow()
        return await workflow.execute(plan_path, output_dir, context, guidelines_path)
    
    async def close(self) -> None:
        """Close resources."""
        await self.agent_router.close()
