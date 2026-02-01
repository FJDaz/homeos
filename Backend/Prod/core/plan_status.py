"""Plan execution status: write/read current plan progress for monitoring."""
from pathlib import Path
from typing import Any, Dict, Optional
import json
from datetime import datetime, timezone


def _status_path() -> Path:
    """Path to plan_status.json under project .cursor/."""
    # Backend/Prod/core -> Backend/Prod -> Backend -> project root
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    return project_root / ".cursor" / "plan_status.json"


def update_plan_status(
    plan_path: Optional[str] = None,
    plan_id: Optional[str] = None,
    workflow_type: Optional[str] = None,
    phase: Optional[str] = None,
    batch_index: Optional[int] = None,
    current_step_ids: Optional[list] = None,
    completed_steps: Optional[list] = None,
    total_steps: Optional[int] = None,
    total_batches: Optional[int] = None,
    status: Optional[str] = None,
    error: Optional[str] = None,
    total_time_ms: Optional[float] = None,
    total_cost_usd: Optional[float] = None,
    **extra: Any,
) -> None:
    """
    Update plan status (merge with existing). Used by workflows and orchestrator.
    status: "running" | "completed" | "failed"
    """
    path = _status_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    current: Dict[str, Any] = {}
    if path.exists():
        try:
            current = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    now = datetime.now(timezone.utc).isoformat()
    if "started_at" not in current and (plan_path or plan_id or workflow_type):
        current["started_at"] = now
    current["updated_at"] = now
    if plan_path is not None:
        current["plan_path"] = str(plan_path)
    if plan_id is not None:
        current["plan_id"] = plan_id
    if workflow_type is not None:
        current["workflow_type"] = workflow_type
    if phase is not None:
        current["phase"] = phase
    if batch_index is not None:
        current["batch_index"] = batch_index
    if current_step_ids is not None:
        current["current_step_ids"] = current_step_ids
    if completed_steps is not None:
        current["completed_steps"] = list(completed_steps)
    if total_steps is not None:
        current["total_steps"] = total_steps
    if total_batches is not None:
        current["total_batches"] = total_batches
    if status is not None:
        current["status"] = status
    if error is not None:
        current["error"] = error
    if total_time_ms is not None:
        current["total_time_ms"] = total_time_ms
    if total_cost_usd is not None:
        current["total_cost_usd"] = total_cost_usd
    for k, v in extra.items():
        current[k] = v
    path.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")


def get_plan_status() -> Optional[Dict[str, Any]]:
    """Read current plan status from .cursor/plan_status.json."""
    path = _status_path()
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
