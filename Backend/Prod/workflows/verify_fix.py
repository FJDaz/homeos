"""VerifyFix workflow: Vérifier le code puis corriger les erreurs détectées."""
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import uuid
import tempfile
from datetime import datetime
from loguru import logger

from ..orchestrator import Orchestrator
from ..models.plan_reader import PlanReader, Plan
from ..claude_helper import get_step_output, apply_generated_code
from ..core.plan_status import update_plan_status
from .proto import ProtoWorkflow


class VerifyFixWorkflow:
    """
    Workflow Vérifier-et-Corriger : exécute le plan, valide, puis corrige les erreurs.

    Séquence:
    1. Exécution BUILD (génération de qualité)
    2. Application du code généré aux fichiers sources
    3. Validation DOUBLE-CHECK (Gemini) → rapport d'erreurs et suggestions
    4. Si des erreurs sont trouvées : génération d’un plan de correction (suggestions)
    5. Exécution des corrections en BUILD et application
    6. Re-validation (une fois)

    Usage: "Je veux qu’Aetherflow vérifie et corrige les erreurs"
    """

    def __init__(self):
        self.orchestrator = None

    async def execute(
        self,
        plan_path: Path,
        output_dir: Optional[Path] = None,
        context: Optional[str] = None,
        max_fix_rounds: int = 1,
    ) -> Dict[str, Any]:
        """
        Exécute le workflow vérifier-et-corriger.

        Args:
            plan_path: Chemin vers le plan JSON
            output_dir: Répertoire de sortie
            context: Contexte additionnel
            max_fix_rounds: Nombre max de tours de correction (défaut 1)

        Returns:
            Résultat combiné (build, validation, corrections éventuelles)
        """
        logger.info("Starting VerifyFix workflow (BUILD → validate → fix errors if needed)")
        output_dir = Path(output_dir) if output_dir else None
        build_dir = output_dir / "build" if output_dir else None
        validation_dir = output_dir / "validation" if output_dir else None

        plan_reader = PlanReader()
        plan = plan_reader.read(plan_path)
        update_plan_status(
            plan_path=str(plan_path),
            plan_id=getattr(plan, "task_id", None),
            workflow_type="VerifyFix",
            phase="BUILD",
            status="running",
            total_steps=len(plan.steps),
        )
        proto = ProtoWorkflow()

        # Phase 1: Exécution BUILD
        logger.info("Phase 1: Executing plan in BUILD mode")
        self.orchestrator = Orchestrator(execution_mode="BUILD")
        try:
            build_result = await self.orchestrator.execute_plan(
                plan_path=plan_path,
                output_dir=build_dir,
                context=context or "",
                use_streaming=False,
                execution_mode="BUILD",
            )
        finally:
            await self.orchestrator.close()

        # Phase 2: Application du code aux fichiers
        logger.info("Phase 2: Applying generated code to source files")
        apply_result = await proto._apply_generated_code(
            plan=plan,
            fast_result=build_result,
            output_dir=build_dir,
        )
        if not apply_result.get("success", True):
            logger.warning(f"Some files could not be applied: {apply_result.get('failed_files', [])}")

        # Phase 3: Validation DOUBLE-CHECK
        logger.info("Phase 3: Validating with DOUBLE-CHECK (Gemini)")
        update_plan_status(phase="validation")
        self.orchestrator = Orchestrator(execution_mode="DOUBLE-CHECK")
        proto.orchestrator = self.orchestrator  # _validate_results uses proto.orchestrator
        try:
            validation_result = await proto._validate_results(
                build_result,
                validation_dir,
                context or "",
            )
        finally:
            await self.orchestrator.close()

        total_time_ms = (
            build_result["metrics"].total_execution_time_ms
            + validation_result.get("execution_time_ms", 0)
        )
        total_cost_usd = (
            build_result["metrics"].total_cost_usd
            + validation_result.get("cost_usd", 0.0)
        )

        fix_rounds_done = 0
        fix_result = None
        validation_after_fix = None

        # Phase 4–6: Correction si nécessaire (jusqu’à max_fix_rounds)
        invalid_details = [
            d
            for d in validation_result.get("validation_details", [])
            if not d.get("valid", True)
        ]
        if invalid_details and max_fix_rounds > 0:
            fix_plan = self._build_fix_plan(plan, invalid_details)
            if fix_plan and fix_plan.get("steps"):
                fix_rounds_done += 1
                logger.info("Phase 4: Running correction steps (BUILD)")
                fix_dir = output_dir / "fix" if output_dir else None
                self.orchestrator = Orchestrator(execution_mode="BUILD")
                try:
                    with tempfile.NamedTemporaryFile(
                        mode="w", suffix=".json", delete=False
                    ) as f:
                        json.dump(fix_plan, f, indent=2)
                        fix_plan_path = Path(f.name)
                    try:
                        fix_result = await self.orchestrator.execute_plan(
                            plan_path=fix_plan_path,
                            output_dir=fix_dir,
                            context=self._fix_context(invalid_details),
                            use_streaming=False,
                            execution_mode="BUILD",
                        )
                    finally:
                        fix_plan_path.unlink(missing_ok=True)
                finally:
                    await self.orchestrator.close()

                # Phase 5: Application des corrections
                if fix_result and fix_result.get("results"):
                    logger.info("Phase 5: Applying corrections to source files")
                    fix_plan_obj = Plan(fix_plan)
                    apply_fix = await proto._apply_generated_code(
                        plan=fix_plan_obj,
                        fast_result=fix_result,
                        output_dir=fix_dir,
                    )
                    logger.info(
                        f"Applied corrections: {apply_fix.get('files_applied', 0)} file(s)"
                    )

                # Phase 6: Re-validation
                if fix_result:
                    logger.info("Phase 6: Re-validating after corrections")
                    self.orchestrator = Orchestrator(execution_mode="DOUBLE-CHECK")
                    proto.orchestrator = self.orchestrator
                    try:
                        validation_after_fix = await proto._validate_results(
                            fix_result,
                            output_dir / "validation_after_fix" if output_dir else None,
                            context or "",
                        )
                        total_time_ms += (
                            (fix_result.get("metrics").total_execution_time_ms if fix_result.get("metrics") else 0)
                            + validation_after_fix.get("execution_time_ms", 0)
                        )
                        if fix_result.get("metrics") and hasattr(fix_result["metrics"], "total_cost_usd"):
                            total_cost_usd += fix_result["metrics"].total_cost_usd
                        total_cost_usd += validation_after_fix.get("cost_usd", 0.0)
                    finally:
                        await self.orchestrator.close()

        all_valid = validation_result.get("success", False)
        if validation_after_fix is not None:
            all_valid = validation_after_fix.get("success", False)

        update_plan_status(
            status="completed",
            total_time_ms=total_time_ms,
            total_cost_usd=total_cost_usd,
        )
        return {
            "workflow": "VerifyFix",
            "success": all_valid,
            "build": build_result,
            "code_applied": apply_result,
            "validation": validation_result,
            "fix_rounds_done": fix_rounds_done,
            "fix_execution": fix_result,
            "validation_after_fix": validation_after_fix,
            "total_time_ms": total_time_ms,
            "total_cost_usd": total_cost_usd,
            "message": "VerifyFix completed: errors corrected" if fix_rounds_done else (
                "VerifyFix completed: no errors" if all_valid else "VerifyFix completed: validation found issues"
            ),
        }

    def _build_fix_plan(self, plan: Plan, invalid_details: List[Dict]) -> Dict[str, Any]:
        """Construit un plan de correction à partir des violations de la validation."""
        steps = []
        for detail in invalid_details:
            step_id = detail.get("step_id", "")
            plan_step = plan.get_step(step_id)
            if not plan_step:
                continue
            feedback = detail.get("pedagogical_feedback")
            if not feedback or not isinstance(feedback, dict):
                suggestions = [detail.get("output", "Fix the issues reported in validation.")[:500]]
            else:
                violations = feedback.get("violations", [])
                suggestions = [
                    v.get("suggestion") or v.get("issue", "")
                    for v in violations
                    if isinstance(v, dict)
                ]
                if not suggestions:
                    suggestions = [feedback.get("overall_feedback", "Apply validation feedback.")]
            description = (
                "Apply the following corrections (from validation):\n"
                + "\n".join(f"- {s}" for s in suggestions[:10])
                + "\n\nTarget: same files as original step. Preserve behavior; fix only reported issues."
            )
            steps.append({
                "id": f"{step_id}_fix",
                "description": description,
                "type": "refactoring",
                "complexity": 0.5,
                "estimated_tokens": 800,
                "dependencies": [],
                "validation_criteria": ["Corrections applied", "Code passes validation"],
                "context": {**dict(plan_step.context or {}), "files": (plan_step.context or {}).get("files", [])},
            })
        if not steps:
            return {}
        return {
            "task_id": str(uuid.uuid4()),
            "description": "Corrections from VerifyFix validation",
            "steps": steps,
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "project_context": "VerifyFix correction round",
            },
        }

    def _fix_context(self, invalid_details: List[Dict]) -> str:
        """Contexte pour les étapes de correction."""
        parts = ["Validation reported the following issues to fix:\n"]
        for d in invalid_details:
            parts.append(f"- {d.get('step_id', '')}: {d.get('output', '')[:300]}...")
        return "\n".join(parts)
