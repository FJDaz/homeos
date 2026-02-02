"""PROTO workflow: Fast prototyping with minimal quality checks."""
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

from ..orchestrator import Orchestrator
from ..models.plan_reader import PlanReader, Plan
from ..core.plan_status import update_plan_status


class ProtoWorkflow:
    """
    Workflow PROTO: Vitesse maximale pour prototypage.
    
    Séquence:
    1. Plan (si nécessaire)
    2. Exécution FAST (Groq)
    3. Validation DOUBLE-CHECK (Gemini)
    
    Usage: "Je veux voir si ça marche"
    """
    
    def __init__(self):
        """Initialize PROTO workflow."""
        self.orchestrator = None
    
    async def execute(
        self,
        plan_path: Path,
        output_dir: Optional[Path] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute PROTO workflow.
        
        Args:
            plan_path: Path to plan JSON file
            output_dir: Output directory for results
            context: Additional context
            
        Returns:
            Dictionary with execution results
        """
        logger.info("Starting PROTO workflow (FAST → DOUBLE-CHECK)")
        plan_reader = PlanReader()
        plan = plan_reader.read(plan_path)
        update_plan_status(
            plan_path=str(plan_path),
            plan_id=getattr(plan, "task_id", None),
            workflow_type="PROTO",
            phase="FAST",
            status="running",
            total_steps=len(plan.steps),
        )
        # Phase 1: Execute with FAST mode
        logger.info("Phase 1: Executing with FAST mode (Groq)")
        self.orchestrator = Orchestrator(execution_mode="FAST")
        
        try:
            fast_result = await self.orchestrator.execute_plan(
                plan_path=plan_path,
                output_dir=output_dir / "fast" if output_dir else None,
                context=context,
                use_streaming=False,
                execution_mode="FAST"
            )
            
            logger.info(f"FAST execution completed: {fast_result['metrics'].total_execution_time_ms/1000:.2f}s")
            
            # Phase 1.5: Apply generated code to source files
            logger.info("Phase 1.5: Applying generated code to source files")
            update_plan_status(phase="apply")
            apply_result = await self._apply_generated_code(
                plan=plan,
                fast_result=fast_result,
                output_dir=output_dir / "fast" if output_dir else None
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
                    merge_step_outputs_to_file(merge_steps, str(output_dir / "fast"), merge_path)
            # Error survey: log apply failures
            for file_path in apply_result.get("failed_files", []):
                try:
                    from ..core.error_survey import log_aetherflow_error
                    log_aetherflow_error(
                        title=f"Apply failed: {Path(file_path).name}",
                        nature="apply_failed",
                        proposed_solution="Vérifier le step output et le mapping bloc→fichier (claude_helper).",
                        raw_error=f"Failed to apply code to {file_path}",
                        file_path=file_path,
                        plan_path=str(plan_path),
                        workflow="PROTO",
                    )
                except Exception as survey_err:
                    logger.debug(f"Error survey log failed: {survey_err}")
            
            # Phase 2: Double-check validation
            logger.info("Phase 2: Validating with DOUBLE-CHECK mode (Gemini)")
            update_plan_status(phase="validation")
            await self.orchestrator.close()
            
            self.orchestrator = Orchestrator(execution_mode="DOUBLE-CHECK")
            
            # Create a validation plan from FAST results
            validation_result = await self._validate_results(
                fast_result,
                output_dir / "validation" if output_dir else None,
                context
            )
            
            # Combine results
            combined_result = {
                "workflow": "PROTO",
                "fast_execution": fast_result,
                "code_applied": apply_result,
                "validation": validation_result,
                "success": fast_result["success"] and apply_result.get("success", True) and validation_result.get("success", True),
                "total_time_ms": fast_result["metrics"].total_execution_time_ms + validation_result.get("execution_time_ms", 0),
                "total_cost_usd": fast_result["metrics"].total_cost_usd + validation_result.get("cost_usd", 0.0)
            }
            
            # Error survey: log validation failures
            for d in validation_result.get("validation_details", []):
                if not d.get("valid", True):
                    try:
                        from ..core.error_survey import log_aetherflow_error
                        log_aetherflow_error(
                            title=f"Validation failed: {d.get('step_id', '?')}",
                            nature="validation_failed",
                            proposed_solution="Corriger le code selon le feedback pédagogique ou relancer avec -vfx.",
                            raw_error=d.get("output", ""),
                            step_id=d.get("step_id"),
                            plan_path=str(plan_path),
                            workflow="PROTO",
                        )
                    except Exception as survey_err:
                        logger.debug(f"Error survey log failed: {survey_err}")
            
            logger.info(f"PROTO workflow completed: {combined_result['total_time_ms']/1000:.2f}s, ${combined_result['total_cost_usd']:.4f}")
            update_plan_status(
                status="completed",
                total_time_ms=combined_result["total_time_ms"],
                total_cost_usd=combined_result["total_cost_usd"],
            )
            return combined_result
            
        except Exception as e:
            logger.error(f"PROTO workflow failed: {e}")
            update_plan_status(status="failed", error=str(e))
            raise
        finally:
            if self.orchestrator:
                await self.orchestrator.close()
    
    async def _apply_generated_code(
        self,
        plan: Plan,
        fast_result: Dict[str, Any],
        output_dir: Optional[Path]
    ) -> Dict[str, Any]:
        """
        Apply generated code from FAST phase to source files.
        
        Args:
            plan: Plan object with step definitions
            fast_result: Results from FAST execution
            output_dir: Output directory where step outputs are stored
            
        Returns:
            Dictionary with application results
        """
        from ..claude_helper import get_step_output, apply_generated_code
        
        files_applied = []
        files_failed = []
        
        if not output_dir:
            logger.warning("No output directory provided, cannot apply generated code")
            return {
                "success": False,
                "files_applied": 0,
                "files_failed": 0,
                "error": "No output directory"
            }
        
        # For each step in the plan
        for step in plan.steps:
            # Get step output from FAST phase
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
        fast_result: Dict[str, Any],
        output_dir: Optional[Path],
        context: Optional[str]
    ) -> Dict[str, Any]:
        """
        Validate FAST results using DOUBLE-CHECK mode with Gemini.
        
        Creates a validation plan and executes it with Gemini to check:
        - Code compiles/runs correctly
        - No obvious security issues
        - Logic is sound
        - Basic code quality
        
        Args:
            fast_result: Results from FAST execution
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
        
        for step_id, result in fast_result.get("results", {}).items():
            if result.success and result.output:
                step_outputs.append(f"Step {step_id}:\n{result.output}")
                
                # Create validation step for each successful step
                # Extract step number from step_id (e.g., "step_1" -> "1")
                step_num = step_id.replace("step_", "") if step_id.startswith("step_") else str(len(validation_steps) + 1)
                validation_steps.append({
                    "id": f"step_{step_num}",
                    "description": f"Validate code from {step_id}: Check compilation, security, and logic correctness",
                    "type": "analysis",
                    "complexity": 0.3,
                    "estimated_tokens": 500,
                    "dependencies": [],
                    "validation_criteria": [
                        "Code syntax is valid",
                        "No obvious security vulnerabilities",
                        "Logic is sound and correct",
                        "Code follows basic best practices"
                    ],
                    "context": {
                        "language": "python",
                        "code_to_validate": result.output[:2000]  # Limit size
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
            "description": f"Validate FAST mode execution results - {len(validation_steps)} steps",
            "steps": validation_steps,
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "claude_version": "claude-code",
                "project_context": "DOUBLE-CHECK validation of FAST mode execution"
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
            # Build validation context with PEDAGOGICAL feedback format (adapted for PROTO - less strict)
            validation_context = f"""
Code generated in FAST mode to validate:

{chr(10).join(step_outputs[:5])}  # Limit to first 5 steps to avoid token overflow

PEDAGOGICAL VALIDATION MODE (PROTO - Focus on syntax and security):

For each issue found, provide:
1. **Rule violated**: Syntax, Security, Logic, or Code Quality
2. **Location**: Specific line numbers or code sections
3. **Issue**: What exactly is wrong
4. **Explanation**: Why this is a problem
5. **Suggestion**: How to fix it

Format your feedback as:
## Validation Results

### ✅ Passed Checks
- **[Rule Name]**: [Location]
  - Brief confirmation

### ❌ Failed Checks
- **[Rule Name]**: [Location]
  - **Issue**: [What's wrong]
  - **Why**: [Explanation]
  - **Fix**: [How to correct it]
  - **Code Reference**: [Line numbers or code snippet]

Validation requirements (PROTO - basic checks):
- **Syntax**: Code compiles/runs correctly (syntax errors, import issues)
- **Security**: No obvious security issues (SQL injection, XSS, unsafe eval, etc.)
- **Logic**: Logic correctness (off-by-one errors, null pointer issues, etc.)
- **Code Quality**: Basic code quality (naming, structure)
"""
            
            # Execute validation plan with DOUBLE-CHECK mode
            logger.info(f"Executing validation plan with {len(validation_steps)} validation steps")
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
                # Check for explicit failures
                output_lower = result.output.lower() if result.output else ""
                has_error = (
                    "error" in output_lower[:500] or 
                    "fail" in output_lower[:500] or
                    "invalid" in output_lower[:500]
                )
                # Check for success indicators
                has_success = (
                    "valid" in output_lower[:1000] or 
                    "pass" in output_lower[:1000] or 
                    "ok" in output_lower[:1000] or
                    "completed" in output_lower[:1000] or
                    "✓" in result.output[:500] if result.output else False
                )
                
                # Consider valid if: step succeeded AND (has success indicator OR no explicit error)
                is_valid = result.success and (has_success or not has_error)
                
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
                    "output": result.output[:500] if result.output else "No output",
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
            
            logger.info(f"Validation completed: {validation_result['note']}")
            
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
