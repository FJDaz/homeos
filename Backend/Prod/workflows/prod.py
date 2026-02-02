"""PROD workflow: Quality-first with FAST draft then BUILD refactoring."""
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

from ..orchestrator import Orchestrator
from ..core.plan_status import update_plan_status

# #region agent log
_DEBUG_LOG = "/Users/francois-jeandazin/AETHERFLOW/.cursor/debug.log"
def _dbg(hy: str, loc: str, msg: str, data: Optional[Dict] = None):
    with open(_DEBUG_LOG, "a") as f:
        f.write(json.dumps({"timestamp": int(time.time() * 1000), "hypothesisId": hy, "location": loc, "message": msg, "data": data or {}, "sessionId": "debug-session"}) + "\n")
# #endregion
from ..models.plan_reader import PlanReader, Plan, Step


class ProdWorkflow:
    """
    Workflow PROD: Qualité maximale avec refactoring.
    
    Séquence:
    1. Plan + Guidelines
    2. FAST (draft brut) → génère brouillon
    3. BUILD (refactor avec guidelines) → génère code propre
    4. DOUBLE-CHECK (validation finale)
    
    Usage: "Je veux commiter ce code"
    """
    
    def __init__(self):
        """Initialize PROD workflow."""
        self.orchestrator = None
    
    async def execute(
        self,
        plan_path: Path,
        output_dir: Optional[Path] = None,
        context: Optional[str] = None,
        guidelines_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Execute PROD workflow.
        
        Args:
            plan_path: Path to plan JSON file
            output_dir: Output directory for results
            context: Additional context
            guidelines_path: Path to guidelines file (optional, uses default if None)
            
        Returns:
            Dictionary with execution results
        """
        logger.info("Starting PROD workflow (FAST draft → BUILD refactor → DOUBLE-CHECK)")
        # #region agent log
        _dbg("A", "prod.py:execute", "PROD workflow start", {"plan_path": str(plan_path)})
        # #endregion
        # Load plan
        plan_reader = PlanReader()
        plan = plan_reader.read(plan_path)
        update_plan_status(
            plan_path=str(plan_path),
            plan_id=getattr(plan, "task_id", None),
            workflow_type="PROD",
            phase="FAST",
            status="running",
            total_steps=len(plan.steps),
        )
        # Phase 1: FAST execution (draft)
        logger.info("Phase 1: Generating draft with FAST mode (Groq)")
        # #region agent log
        t1 = time.time(); _dbg("A", "prod.py:Phase1", "Phase 1 FAST start", {})
        # #endregion
        self.orchestrator = Orchestrator(execution_mode="FAST")
        
        try:
            fast_result = await self.orchestrator.execute_plan(
                plan_path=plan_path,
                output_dir=output_dir / "fast_draft" if output_dir else None,
                context=context,
                use_streaming=False,
                execution_mode="FAST"
            )
            
            # Check if Phase 1 had critical failures (all steps failed)
            successful_steps = sum(1 for r in fast_result.get("results", {}).values() if r.success)
            total_steps = len(fast_result.get("results", {}))
            
            if successful_steps == 0 and total_steps > 0:
                logger.warning(
                    f"Phase 1 FAST: All {total_steps} steps failed. "
                    f"This may be due to rate limits. Continuing to Phase 2 BUILD anyway."
                )
            elif successful_steps < total_steps:
                logger.warning(
                    f"Phase 1 FAST: {successful_steps}/{total_steps} steps succeeded. "
                    f"Some steps may have failed due to rate limits."
                )
            
            logger.info(f"FAST draft completed: {fast_result['metrics'].total_execution_time_ms/1000:.2f}s")
            # #region agent log
            _dbg("A", "prod.py:Phase1", "Phase 1 FAST end", {"duration_s": round(time.time() - t1, 2)})
            # #endregion
            # Phase 2: BUILD refactoring (with FAST results as context)
            logger.info("Phase 2: Refactoring with BUILD mode (DeepSeek + Guidelines)")
            update_plan_status(phase="BUILD")
            # #region agent log
            t2 = time.time(); _dbg("B", "prod.py:Phase2", "Phase 2 BUILD start", {})
            # #endregion
            await self.orchestrator.close()
            
            self.orchestrator = Orchestrator(execution_mode="BUILD")
            
            # Build context from FAST results for BUILD phase
            # #region agent log
            t_ctx = time.time(); _dbg("E", "prod.py:_build_refactoring_context", "build_context start", {})
            # #endregion
            build_context = self._build_refactoring_context(fast_result, context)
            # #region agent log
            _dbg("E", "prod.py:_build_refactoring_context", "build_context end", {"duration_s": round(time.time() - t_ctx, 2), "context_len": len(build_context)})
            # #endregion
            
            build_result = await self.orchestrator.execute_plan(
                plan_path=plan_path,
                output_dir=output_dir / "build_refactored" if output_dir else None,
                context=build_context,
                use_streaming=False,
                execution_mode="BUILD"
            )
            
            logger.info(f"BUILD refactoring completed: {build_result['metrics'].total_execution_time_ms/1000:.2f}s")
            # #region agent log
            _dbg("B", "prod.py:Phase2", "Phase 2 BUILD end", {"duration_s": round(time.time() - t2, 2)})
            # #endregion
            # Phase 2.5: Apply refactored code to source files
            logger.info("Phase 2.5: Applying refactored code to source files")
            update_plan_status(phase="apply")
            # #region agent log
            t25 = time.time(); _dbg("B", "prod.py:Phase2.5", "Phase 2.5 apply start", {})
            # #endregion
            apply_result = await self._apply_refactored_code(
                plan=plan,
                build_result=build_result,
                output_dir=output_dir / "build_refactored" if output_dir else None
            )
            logger.info(f"Applied code to {apply_result['files_applied']} file(s)")
            # Merge chunked step outputs into one file if plan declares output_merge
            output_merge = plan.metadata.get("output_merge") if isinstance(getattr(plan, "metadata", None), dict) else None
            if output_merge and output_dir:
                merge_file = output_merge.get("file")
                merge_steps = output_merge.get("steps", [])
                if merge_file and merge_steps:
                    from ..claude_helper import merge_step_outputs_to_file
                    project_root = Path(__file__).parent.parent.parent.parent
                    merge_path = project_root / merge_file
                    merge_step_outputs_to_file(merge_steps, str(output_dir / "build_refactored"), merge_path)
            # Error survey: log apply failures
            for file_path in apply_result.get("failed_files", []):
                try:
                    from ..core.error_survey import log_aetherflow_error
                    log_aetherflow_error(
                        title=f"Apply failed (PROD): {Path(file_path).name}",
                        nature="apply_failed",
                        proposed_solution="Vérifier le step output et le mapping bloc→fichier (claude_helper).",
                        raw_error=f"Failed to apply code to {file_path}",
                        file_path=file_path,
                        plan_path=str(plan_path),
                        workflow="PROD",
                    )
                except Exception as survey_err:
                    logger.debug(f"Error survey log failed: {survey_err}")
            # #region agent log
            _dbg("B", "prod.py:Phase2.5", "Phase 2.5 apply end", {"duration_s": round(time.time() - t25, 2), "files_applied": apply_result["files_applied"]})
            # #endregion
            # Phase 3: DOUBLE-CHECK validation
            logger.info("Phase 3: Final validation with DOUBLE-CHECK mode (Gemini)")
            update_plan_status(phase="validation")
            # #region agent log
            t3 = time.time(); _dbg("C", "prod.py:Phase3", "Phase 3 validation start", {})
            # #endregion
            await self.orchestrator.close()
            
            self.orchestrator = Orchestrator(execution_mode="DOUBLE-CHECK")
            
            validation_result = await self._validate_results(
                build_result,
                output_dir / "validation" if output_dir else None,
                build_context
            )
            
            # #region agent log
            _dbg("C", "prod.py:Phase3", "Phase 3 validation end", {"duration_s": round(time.time() - t3, 2)})
            # #endregion
            # Combine results
            combined_result = {
                "workflow": "PROD",
                "fast_draft": fast_result,
                "build_refactored": build_result,
                "code_applied": apply_result,
                "validation": validation_result,
                "success": build_result["success"] and apply_result.get("success", True) and validation_result.get("success", True),
                "total_time_ms": (
                    fast_result["metrics"].total_execution_time_ms +
                    build_result["metrics"].total_execution_time_ms +
                    validation_result.get("execution_time_ms", 0)
                ),
                "total_cost_usd": (
                    fast_result["metrics"].total_cost_usd +
                    build_result["metrics"].total_cost_usd +
                    validation_result.get("cost_usd", 0.0)
                )
            }
            
            # Error survey: log validation failures
            for d in validation_result.get("validation_details", []):
                if not d.get("valid", True):
                    try:
                        from ..core.error_survey import log_aetherflow_error
                        log_aetherflow_error(
                            title=f"Validation failed (PROD): {d.get('step_id', '?')}",
                            nature="validation_failed",
                            proposed_solution="Corriger le code selon le feedback pédagogique ou relancer avec -vfx.",
                            raw_error=d.get("output", ""),
                            step_id=d.get("step_id"),
                            plan_path=str(plan_path),
                            workflow="PROD",
                        )
                    except Exception as survey_err:
                        logger.debug(f"Error survey log failed: {survey_err}")
            logger.info(
                f"PROD workflow completed: {combined_result['total_time_ms']/1000:.2f}s, "
                f"${combined_result['total_cost_usd']:.4f}"
            )
            update_plan_status(
                status="completed",
                total_time_ms=combined_result["total_time_ms"],
                total_cost_usd=combined_result["total_cost_usd"],
            )
            return combined_result
            
        except Exception as e:
            logger.error(f"PROD workflow failed: {e}")
            update_plan_status(status="failed", error=str(e))
            raise
        finally:
            if self.orchestrator:
                await self.orchestrator.close()
    
    def _build_refactoring_context(
        self,
        fast_result: Dict[str, Any],
        original_context: Optional[str]
    ) -> str:
        """
        Build context for BUILD refactoring phase from FAST results.
        
        Args:
            fast_result: Results from FAST execution
            original_context: Original context
            
        Returns:
            Enhanced context with FAST draft code
        """
        context_parts = []
        
        if original_context:
            context_parts.append(original_context)
        
        context_parts.append("\n--- Draft Code from FAST Mode (to refactor) ---\n")
        
        # Add FAST results as draft code to refactor
        for step_id, result in fast_result.get("results", {}).items():
            if result.success and result.output:
                context_parts.append(f"\nStep {step_id} (draft):\n{result.output}\n")
        
        context_parts.append(
            "\n--- Refactoring Instructions ---\n"
            "Refactor the draft code above following these guidelines:\n"
            "- TDD: Add comprehensive unit tests\n"
            "- DRY: Extract repeated logic into reusable functions\n"
            "- SOLID: Ensure single responsibility per function/class\n"
            "- Structure: Separate Models/Services/Controllers\n"
            "- Type hints: Add Python type hints\n"
            "- Docstrings: Document all public functions\n"
        )
        
        return "\n".join(context_parts)
    
    async def _apply_refactored_code(
        self,
        plan: Plan,
        build_result: Dict[str, Any],
        output_dir: Optional[Path]
    ) -> Dict[str, Any]:
        """
        Apply refactored code from BUILD phase to source files.
        
        Args:
            plan: Plan object with step definitions
            build_result: Results from BUILD execution
            output_dir: Output directory where step outputs are stored
            
        Returns:
            Dictionary with application results
        """
        from ..claude_helper import get_step_output, apply_generated_code
        
        files_applied = []
        files_failed = []
        
        if not output_dir:
            logger.warning("No output directory provided, cannot apply refactored code")
            return {
                "success": False,
                "files_applied": 0,
                "files_failed": 0,
                "error": "No output directory"
            }
        
        # For each step in the plan
        for step in plan.steps:
            # Get step output from BUILD phase
            step_output = get_step_output(step.id, str(output_dir))
            
            if not step_output:
                logger.debug(f"No output found for step {step.id}, skipping")
                continue
            
            # Get target files from step context
            target_files = step.context.get("files", []) if step.context else []
            
            if not target_files:
                logger.debug(f"No target files specified for step {step.id}, skipping")
                continue
            
            # Apply code to each target file
            for file_path_str in target_files:
                try:
                    # Resolve file path (relative to project root)
                    file_path = Path(file_path_str)
                    if not file_path.is_absolute():
                        # Try to resolve relative to project root
                        # Assuming we're in Backend/Prod, go up to project root
                        project_root = Path(__file__).parent.parent.parent.parent
                        file_path = project_root / file_path
                    
                    # Convert step to dict for apply_generated_code
                    step_dict = {
                        "id": step.id,
                        "type": step.type,
                        "context": step.context or {}
                    }
                    
                    # Apply the code
                    success = apply_generated_code(
                        step_output=step_output,
                        target_file=file_path,
                        plan_step=step_dict
                    )
                    
                    if success:
                        files_applied.append(str(file_path))
                        logger.info(f"✓ Applied code from {step.id} to {file_path}")
                    else:
                        files_failed.append(str(file_path))
                        logger.warning(f"✗ Failed to apply code from {step.id} to {file_path}")
                        
                except Exception as e:
                    logger.error(f"Error applying code from {step.id} to {file_path_str}: {e}")
                    files_failed.append(file_path_str)
        
        return {
            "success": len(files_failed) == 0,
            "files_applied": len(files_applied),
            "files_failed": len(files_failed),
            "applied_files": files_applied,
            "failed_files": files_failed
        }
    
    async def _validate_results(
        self,
        build_result: Dict[str, Any],
        output_dir: Optional[Path],
        context: Optional[str]
    ) -> Dict[str, Any]:
        """
        Validate BUILD results using DOUBLE-CHECK mode with Gemini.
        
        Creates a comprehensive validation plan and executes it with Gemini to check:
        - Code compiles/runs correctly
        - No security vulnerabilities
        - Logic correctness
        - Respect of guidelines (TDD, DRY, SOLID, Structure)
        - Test coverage and quality
        
        Args:
            build_result: Results from BUILD execution
            output_dir: Output directory
            context: Additional context
            
        Returns:
            Validation results with metrics
        """
        from datetime import datetime
        import json
        import uuid
        
        start_time = datetime.now()
        
        # Extract step outputs for validation
        step_outputs = []
        validation_steps = []
        
        for step_id, result in build_result.get("results", {}).items():
            if result.success and result.output:
                step_outputs.append(f"Step {step_id}:\n{result.output}")
                
                # Create comprehensive validation step
                # Extract step number from step_id (e.g., "step_1" -> "1")
                step_num = step_id.replace("step_", "") if step_id.startswith("step_") else str(len(validation_steps) + 1)
                validation_steps.append({
                    "id": f"step_{step_num}",
                    "description": f"Comprehensive validation of {step_id}: Check compilation, security, logic, and guidelines compliance (TDD, DRY, SOLID)",
                    "type": "analysis",
                    "complexity": 0.5,
                    "estimated_tokens": 800,
                    "dependencies": [],
                    "validation_criteria": [
                        "Code syntax is valid and compiles",
                        "No security vulnerabilities (SQL injection, XSS, unsafe operations)",
                        "Logic is correct and handles edge cases",
                        "Follows TDD: includes comprehensive unit tests",
                        "Follows DRY: no repeated code blocks",
                        "Follows SOLID: single responsibility per function/class",
                        "Structure: Models/Services/Controllers separation (if applicable)",
                        "Type hints present for all functions",
                        "Docstrings present for public functions"
                    ],
                    "context": {
                        "language": "python",
                        "code_to_validate": result.output[:3000],  # More context for BUILD validation
                        "guidelines_applied": True
                    }
                })
        
        if not validation_steps:
            logger.warning("No successful steps to validate")
            return {
                "success": True,
                "execution_time_ms": 0.0,
                "cost_usd": 0.0,
                "validated_steps": 0,
                "validation_details": [],
                "note": "No steps to validate"
            }
        
        # Create validation plan
        validation_plan = {
            "task_id": str(uuid.uuid4()),
            "description": f"Comprehensive validation of BUILD mode execution - {len(validation_steps)} steps with guidelines compliance",
            "steps": validation_steps,
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "claude_version": "claude-code",
                "project_context": "DOUBLE-CHECK validation of BUILD mode execution with guidelines compliance (TDD, DRY, SOLID)"
            }
        }
        
        # Save validation plan temporarily
        temp_plan_path = None
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            temp_plan_path = output_dir / "validation_plan.json"
            with open(temp_plan_path, 'w') as f:
                json.dump(validation_plan, f, indent=2)
        else:
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
            temp_file.write(json.dumps(validation_plan, indent=2))
            temp_file.close()
            temp_plan_path = Path(temp_file.name)
        
        try:
            # Build comprehensive validation context with PEDAGOGICAL feedback format
            validation_context = f"""
Code generated in BUILD mode (after refactoring with guidelines) to validate:

{chr(10).join(step_outputs[:5])}  # Limit to first 5 steps

PEDAGOGICAL VALIDATION MODE - Provide constructive feedback:

For each guideline violation, provide:
1. **Rule violated**: TDD, DRY, SOLID, Structure, Type Hints, or Docstrings
2. **Location**: Specific line numbers or code sections
3. **Issue**: What exactly is wrong
4. **Explanation**: Why this violates the rule
5. **Suggestion**: How to fix it

Format your feedback as:
## Validation Results

### ✅ Passed Checks
- **[Rule Name]**: [Location]
  - Brief confirmation of compliance

### ❌ Failed Checks
- **[Rule Name]**: [Location]
  - **Issue**: [What's wrong]
  - **Why**: [Explanation of violation]
  - **Fix**: [How to correct it]
  - **Code Reference**: [Line numbers or code snippet]

Guidelines to check:
- **TDD**: Comprehensive unit tests present and cover main functionality
- **DRY**: No code duplication, repeated logic extracted
- **SOLID**: Single responsibility principle (one function/class = one task)
- **Structure**: Models/Services/Controllers separation (if applicable)
- **Type Hints**: Python type hints present for all functions
- **Docstrings**: Docstrings present for all public functions
- **Security**: No vulnerabilities (SQL injection, XSS, unsafe eval, etc.)
- **Code Quality**: Proper error handling, naming conventions
"""
            
            # Execute validation plan with DOUBLE-CHECK mode
            logger.info(f"Executing comprehensive validation plan with {len(validation_steps)} validation steps")
            validation_execution = await self.orchestrator.execute_plan(
                plan_path=temp_plan_path,
                output_dir=output_dir,
                context=validation_context,
                use_streaming=False,
                execution_mode="DOUBLE-CHECK"
            )
            
            # Extract validation details
            validation_details = []
            all_valid = True
            
            for step_id, result in validation_execution.get("results", {}).items():
                # Parse validation result more carefully
                output_lower = result.output.lower() if result.output else ""
                # Check for explicit failures first
                has_error = (
                    "error" in output_lower[:500] or 
                    "fail" in output_lower[:500] or
                    "invalid" in output_lower[:500] or
                    "rejected" in output_lower[:500]
                )
                # Check for explicit success indicators
                has_success_indicator = (
                    "valid" in output_lower[:1000] or 
                    "pass" in output_lower[:1000] or 
                    "ok" in output_lower[:1000] or
                    "completed" in output_lower[:1000] or
                    "success" in output_lower[:1000] or
                    "✓" in result.output[:500] if result.output else False
                )
                
                # Consider valid if: step succeeded AND (has success indicator OR no explicit error)
                is_valid = result.success and (has_success_indicator or not has_error)
                
                if not is_valid:
                    all_valid = False
                
                # Parse pedagogical feedback if available
                pedagogical_feedback = None
                if result.output:
                    try:
                        from ..models.feedback_parser import FeedbackParser
                        parser = FeedbackParser()
                        pedagogical_feedback = parser.parse_feedback(result.output)
                    except Exception as e:
                        logger.warning(f"Failed to parse pedagogical feedback for {step_id}: {e}")
                        pedagogical_feedback = None
                
                validation_details.append({
                    "step_id": step_id,
                    "valid": is_valid,
                    "output": result.output[:800] if result.output else "No output",
                    "pedagogical_feedback": pedagogical_feedback.to_dict() if pedagogical_feedback else None,
                    "tokens": result.tokens_used,
                    "cost": result.cost_usd
                })
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Get metrics from validation execution
            metrics = validation_execution.get("metrics")
            if metrics and hasattr(metrics, "total_cost_usd"):
                cost_usd = metrics.total_cost_usd
            elif metrics and hasattr(metrics, "total_cost"):
                cost_usd = metrics.total_cost
            else:
                cost_usd = sum(d.get("cost", 0.0) for d in validation_details)
            
            validation_result = {
                "success": all_valid and validation_execution.get("success", False),
                "execution_time_ms": execution_time,
                "cost_usd": cost_usd,
                "validated_steps": len(validation_details),
                "validation_details": validation_details,
                "metrics": metrics,
                "note": f"DOUBLE-CHECK validation completed: {len([d for d in validation_details if d['valid']])}/{len(validation_details)} steps valid"
            }
            
            logger.info(f"Comprehensive validation completed: {validation_result['note']}")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            return {
                "success": False,
                "execution_time_ms": execution_time,
                "cost_usd": 0.0,
                "validated_steps": 0,
                "validation_details": [],
                "error": str(e),
                "note": f"Validation failed: {e}"
            }
        finally:
            # Cleanup temp file if created
            if temp_plan_path and not (output_dir and temp_plan_path.parent == output_dir):
                try:
                    temp_plan_path.unlink()
                except Exception:
                    pass


