"""FRD (Fast Render Design) workflows: KIMI-powered workflows for large contexts."""
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

from ..orchestrator import Orchestrator
from ..models.plan_reader import PlanReader, Plan
from ..core.plan_status import update_plan_status


class FrdWorkflow:
    """
    FRD Workflow: KIMI-powered workflows for handling large contexts.

    Three variants:
    1. FRD-QUICK: Fast prototyping with KIMI only (FRD-FAST mode)
    2. FRD-FULL: Complete workflow KIMI → DeepSeek → Gemini (FRD-FAST → TEST → REVIEW)
    3. FRD-VFX: Full cycle with verification and fixes (FRD-FAST → TEST → VERIFY → FIX)

    FRD-FAST mode uses KIMI (128K context) for:
    - Tier 1 component library generation
    - Large file refactoring
    - Context > 15K tokens
    """

    def __init__(self, variant: str = "quick"):
        """
        Initialize FRD workflow.

        Args:
            variant: Workflow variant ('quick', 'full', or 'vfx')
        """
        self.variant = variant.lower()
        self.orchestrator = None

    async def execute(
        self,
        plan_path: Path,
        output_dir: Optional[Path] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute FRD workflow based on variant.

        Args:
            plan_path: Path to plan JSON file
            output_dir: Output directory for results
            context: Additional context

        Returns:
            Dictionary with execution results
        """
        if self.variant == "quick":
            return await self._execute_quick(plan_path, output_dir, context)
        elif self.variant == "full":
            return await self._execute_full(plan_path, output_dir, context)
        elif self.variant == "vfx":
            return await self._execute_vfx(plan_path, output_dir, context)
        else:
            raise ValueError(f"Unknown FRD variant: {self.variant}")

    async def _execute_quick(
        self,
        plan_path: Path,
        output_dir: Optional[Path] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute FRD-QUICK: Fast prototyping with KIMI only.

        Sequence:
        1. Execute with FRD-FAST mode (KIMI for large contexts)
        2. Apply generated code

        Args:
            plan_path: Path to plan JSON file
            output_dir: Output directory for results
            context: Additional context

        Returns:
            Dictionary with execution results
        """
        logger.info("Starting FRD-QUICK workflow (FRD-FAST with KIMI)")

        plan_reader = PlanReader()
        plan = plan_reader.read(plan_path)

        update_plan_status(
            plan_path=str(plan_path),
            plan_id=getattr(plan, "task_id", None),
            workflow_type="FRD-QUICK",
            phase="FRD-FAST",
            status="running",
            total_steps=len(plan.steps),
        )

        # Phase 1: Execute with FRD-FAST mode (uses KIMI for large contexts)
        logger.info("Phase 1: Executing with FRD-FAST mode (KIMI for >15K tokens)")
        self.orchestrator = Orchestrator(execution_mode="FRD-FAST")

        try:
            frd_result = await self.orchestrator.execute_plan(
                plan_path=plan_path,
                output_dir=output_dir / "frd-fast" if output_dir else None,
                context=context,
                use_streaming=False,
                execution_mode="FRD-FAST"
            )

            logger.info(f"FRD-FAST execution completed: {frd_result['metrics'].total_execution_time_ms/1000:.2f}s")

            # Phase 1.5: Apply generated code to source files
            logger.info("Phase 1.5: Applying generated code to source files")
            update_plan_status(phase="apply")
            apply_result = await self._apply_generated_code(
                plan=plan,
                fast_result=frd_result,
                output_dir=output_dir / "frd-fast" if output_dir else None
            )
            logger.info(f"Applied code to {apply_result['files_applied']} file(s)")

            # Merge chunked step outputs if needed
            output_merge = plan.metadata.get("output_merge") if isinstance(getattr(plan, "metadata", None), dict) else None
            if output_merge and output_dir:
                merge_file = output_merge.get("file")
                merge_steps = output_merge.get("steps", [])
                if merge_file and merge_steps:
                    from ..claude_helper import merge_step_outputs_to_file
                    project_root = Path(__file__).parent.parent.parent.parent
                    merge_path = project_root / merge_file
                    merge_step_outputs_to_file(merge_steps, str(output_dir / "frd-fast"), merge_path)

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
                        workflow="FRD-QUICK",
                    )
                except Exception as survey_err:
                    logger.debug(f"Error survey log failed: {survey_err}")

            combined_result = {
                "workflow": "FRD-QUICK",
                "frd_fast_execution": frd_result,
                "code_applied": apply_result,
                "success": frd_result["success"] and apply_result.get("success", True),
                "total_time_ms": frd_result["metrics"].total_execution_time_ms,
                "total_cost_usd": frd_result["metrics"].total_cost_usd
            }

            logger.info(f"FRD-QUICK workflow completed: {combined_result['total_time_ms']/1000:.2f}s, ${combined_result['total_cost_usd']:.4f}")
            update_plan_status(
                status="completed",
                total_time_ms=combined_result["total_time_ms"],
                total_cost_usd=combined_result["total_cost_usd"],
            )

            return combined_result

        except Exception as e:
            logger.error(f"FRD-QUICK workflow failed: {e}")
            update_plan_status(status="failed", error_message=str(e))
            raise
        finally:
            if self.orchestrator:
                await self.orchestrator.close()

    async def _execute_full(
        self,
        plan_path: Path,
        output_dir: Optional[Path] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute FRD-FULL: Complete workflow with KIMI → DeepSeek → Gemini.

        Sequence:
        1. FRD-FAST (KIMI for large contexts)
        2. Apply code
        3. TEST (DeepSeek for quality)
        4. REVIEW (Gemini for validation)

        Args:
            plan_path: Path to plan JSON file
            output_dir: Output directory for results
            context: Additional context

        Returns:
            Dictionary with execution results
        """
        logger.info("Starting FRD-FULL workflow (FRD-FAST → TEST → REVIEW)")

        plan_reader = PlanReader()
        plan = plan_reader.read(plan_path)

        update_plan_status(
            plan_path=str(plan_path),
            plan_id=getattr(plan, "task_id", None),
            workflow_type="FRD-FULL",
            phase="FRD-FAST",
            status="running",
            total_steps=len(plan.steps),
        )

        # Phase 1: FRD-FAST with KIMI
        logger.info("Phase 1: FRD-FAST (KIMI)")
        self.orchestrator = Orchestrator(execution_mode="FRD-FAST")

        try:
            frd_result = await self.orchestrator.execute_plan(
                plan_path=plan_path,
                output_dir=output_dir / "frd-fast" if output_dir else None,
                context=context,
                execution_mode="FRD-FAST"
            )

            logger.info(f"FRD-FAST completed: {frd_result['metrics'].total_execution_time_ms/1000:.2f}s")

            # Apply code
            update_plan_status(phase="apply")
            apply_result = await self._apply_generated_code(
                plan=plan,
                fast_result=frd_result,
                output_dir=output_dir / "frd-fast" if output_dir else None
            )

            # Phase 2: TEST with DeepSeek
            logger.info("Phase 2: TEST (DeepSeek)")
            update_plan_status(phase="FRD-TEST")
            await self.orchestrator.close()

            self.orchestrator = Orchestrator(execution_mode="BUILD")
            test_result = await self.orchestrator.execute_plan(
                plan_path=plan_path,
                output_dir=output_dir / "test" if output_dir else None,
                context=context,
                execution_mode="BUILD"
            )

            logger.info(f"TEST completed: {test_result['metrics'].total_execution_time_ms/1000:.2f}s")

            # Phase 3: REVIEW with Gemini
            logger.info("Phase 3: REVIEW (Gemini)")
            update_plan_status(phase="FRD-REVIEW")
            await self.orchestrator.close()

            self.orchestrator = Orchestrator(execution_mode="DOUBLE-CHECK")
            review_result = await self._validate_results(
                test_result,
                output_dir / "review" if output_dir else None,
                context
            )

            combined_result = {
                "workflow": "FRD-FULL",
                "frd_fast_execution": frd_result,
                "code_applied": apply_result,
                "test_execution": test_result,
                "review": review_result,
                "success": all([
                    frd_result["success"],
                    apply_result.get("success", True),
                    test_result["success"],
                    review_result.get("success", True)
                ]),
                "total_time_ms": (
                    frd_result["metrics"].total_execution_time_ms +
                    test_result["metrics"].total_execution_time_ms +
                    review_result.get("execution_time_ms", 0)
                ),
                "total_cost_usd": (
                    frd_result["metrics"].total_cost_usd +
                    test_result["metrics"].total_cost_usd +
                    review_result.get("cost_usd", 0.0)
                )
            }

            logger.info(f"FRD-FULL workflow completed: {combined_result['total_time_ms']/1000:.2f}s, ${combined_result['total_cost_usd']:.4f}")
            update_plan_status(
                status="completed",
                total_time_ms=combined_result["total_time_ms"],
                total_cost_usd=combined_result["total_cost_usd"],
            )

            return combined_result

        except Exception as e:
            logger.error(f"FRD-FULL workflow failed: {e}")
            update_plan_status(status="failed", error_message=str(e))
            raise
        finally:
            if self.orchestrator:
                await self.orchestrator.close()

    async def _execute_vfx(
        self,
        plan_path: Path,
        output_dir: Optional[Path] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute FRD-VFX: Full cycle with verification and fixes.

        Sequence:
        1. FRD-FAST (KIMI)
        2. Apply code
        3. TEST (DeepSeek)
        4. VERIFY (Gemini validation)
        5. FIX (if issues found, re-run with corrections)

        Args:
            plan_path: Path to plan JSON file
            output_dir: Output directory for results
            context: Additional context

        Returns:
            Dictionary with execution results
        """
        logger.info("Starting FRD-VFX workflow (FRD-FAST → TEST → VERIFY → FIX)")

        plan_reader = PlanReader()
        plan = plan_reader.read(plan_path)

        update_plan_status(
            plan_path=str(plan_path),
            plan_id=getattr(plan, "task_id", None),
            workflow_type="FRD-VFX",
            phase="FRD-FAST",
            status="running",
            total_steps=len(plan.steps),
        )

        # Use VerifyFixWorkflow but with FRD-FAST for initial execution
        from .verify_fix import VerifyFixWorkflow

        # Override initial execution mode to FRD-FAST
        vfx_workflow = VerifyFixWorkflow()
        vfx_workflow.initial_mode = "FRD-FAST"

        result = await vfx_workflow.execute(plan_path, output_dir, context)

        # Update workflow type in result
        result["workflow"] = "FRD-VFX"

        return result

    async def _apply_generated_code(
        self,
        plan: Plan,
        fast_result: Dict[str, Any],
        output_dir: Optional[Path]
    ) -> Dict[str, Any]:
        """
        Apply generated code to source files.

        NOTE: Application is disabled for now - code is generated but not applied.
        Manual application via CLI will be required.

        Args:
            plan: The plan being executed
            fast_result: Results from FAST execution
            output_dir: Output directory containing step outputs

        Returns:
            Dictionary with application results
        """
        logger.info("Code application skipped - outputs available in {}", output_dir)

        # Return success without actually applying
        # User can manually apply code from output directory
        return {
            "success": True,
            "files_applied": 0,
            "failed_files": [],
            "applied_files": [],
            "note": f"Code generated in {output_dir}, manual application required"
        }

    async def _validate_results(
        self,
        execution_result: Dict[str, Any],
        output_dir: Optional[Path],
        context: Optional[str]
    ) -> Dict[str, Any]:
        """
        Validate execution results using Gemini.

        Args:
            execution_result: Results from previous execution
            output_dir: Output directory for validation results
            context: Additional context

        Returns:
            Dictionary with validation results
        """
        from ..models.claude_validator import ClaudeCodeValidator

        validator = ClaudeCodeValidator()

        validation_details = []
        total_time = 0
        total_cost = 0.0
        all_valid = True

        for step_id, step_result in execution_result.get("results", {}).items():
            if not step_result.success:
                continue

            try:
                # Validate using Gemini (via Claude validator for now)
                validation = await validator.validate_step_output(
                    step_result.output,
                    step_id=step_id
                )

                validation_details.append({
                    "step_id": step_id,
                    "valid": validation.get("valid", True),
                    "output": validation.get("feedback", "")
                })

                if not validation.get("valid", True):
                    all_valid = False

            except Exception as e:
                logger.warning(f"Validation failed for step {step_id}: {e}")
                validation_details.append({
                    "step_id": step_id,
                    "valid": False,
                    "output": f"Validation error: {e}"
                })
                all_valid = False

        return {
            "success": all_valid,
            "validation_details": validation_details,
            "execution_time_ms": total_time,
            "cost_usd": total_cost
        }


# Convenience functions for CLI
async def execute_frd_quick(plan_path: Path, output_dir: Optional[Path] = None, context: Optional[str] = None):
    """Execute FRD-QUICK workflow."""
    workflow = FrdWorkflow(variant="quick")
    return await workflow.execute(plan_path, output_dir, context)


async def execute_frd_full(plan_path: Path, output_dir: Optional[Path] = None, context: Optional[str] = None):
    """Execute FRD-FULL workflow."""
    workflow = FrdWorkflow(variant="full")
    return await workflow.execute(plan_path, output_dir, context)


async def execute_frd_vfx(plan_path: Path, output_dir: Optional[Path] = None, context: Optional[str] = None):
    """Execute FRD-VFX workflow."""
    workflow = FrdWorkflow(variant="vfx")
    return await workflow.execute(plan_path, output_dir, context)
