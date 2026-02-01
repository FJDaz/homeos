"""Run-and-Fix workflow: run a command (build/deploy), on failure fix from stderr and retry."""
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from loguru import logger

from ..orchestrator import Orchestrator
from ..models.plan_reader import Step
from ..core.run_command import run_allowed_command, is_command_allowed


MAX_CONTEXT_CHARS = 120_000
MAX_FILES = 25
RUN_AND_FIX_TIMEOUT_SEC = 120


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent.parent


def _gather_file_context(workdir: Path, extensions: Tuple[str, ...] = (".svelte", ".ts", ".js", ".tsx", ".jsx")) -> str:
    """Gather content of relevant source files under workdir for LLM context."""
    parts: List[str] = []
    total = 0
    count = 0
    for ext in extensions:
        for f in workdir.rglob(f"*{ext}"):
            if count >= MAX_FILES or total >= MAX_CONTEXT_CHARS:
                break
            try:
                if "node_modules" in str(f) or ".svelte-kit" in str(f) or "dist" in str(f):
                    continue
                content = f.read_text(encoding="utf-8", errors="replace")
                rel = f.relative_to(workdir)
                chunk = f"\n=== {rel} ===\n{content}\n"
                if total + len(chunk) > MAX_CONTEXT_CHARS:
                    chunk = chunk[: MAX_CONTEXT_CHARS - total] + "\n... (truncated)"
                parts.append(chunk)
                total += len(chunk)
                count += 1
            except Exception as e:
                logger.debug(f"Skip {f}: {e}")
        if count >= MAX_FILES or total >= MAX_CONTEXT_CHARS:
            break
    return "\n".join(parts) if parts else "(no source files found)"


def _parse_file_blocks(llm_output: str) -> List[Tuple[str, str]]:
    """Parse LLM output for FILE: path blocks. Returns list of (relative_path, content)."""
    out: List[Tuple[str, str]] = []
    pattern = re.compile(
        r"FILE:\s*([^\n]+?)\s*\n```[\w]*\n(.*?)```",
        re.DOTALL,
    )
    for m in pattern.finditer(llm_output):
        path = m.group(1).strip().strip('"\'')
        content = m.group(2).strip()
        if path and content:
            out.append((path, content))
    if not out:
        single = re.search(r"```[\w]*\n(.*?)```", llm_output, re.DOTALL)
        if single:
            content = single.group(1).strip()
            if len(content) > 50:
                out.append(("fix.patch", content))
    return out


def _apply_fix_blocks(blocks: List[Tuple[str, str]], workdir: Path, base_dir: Path) -> int:
    """Write parsed (path, content) to workdir or base_dir. Returns number of files written."""
    written = 0
    workdir_res = workdir.resolve()
    base_res = base_dir.resolve()
    for rel_path, content in blocks:
        rel = Path(rel_path).as_posix().lstrip("/")
        if ".." in rel:
            continue
        for base in (workdir_res, base_res):
            target = (base / rel).resolve()
            try:
                if not str(target).startswith(str(base)):
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
                written += 1
                logger.info(f"Applied fix to {target}")
                break
            except Exception as e:
                logger.warning(f"Could not write {target}: {e}")
    return written


class RunAndFixWorkflow:
    """
    Run-and-Fix: run a command (e.g. build/deploy); on failure, send error + context
    to LLM, apply fixes, and retry until success or max_rounds.
    """

    def __init__(self):
        self.orchestrator: Optional[Orchestrator] = None

    async def execute(
        self,
        command: str,
        workdir: Optional[Path] = None,
        max_rounds: int = 5,
        output_dir: Optional[Path] = None,
        timeout_sec: int = RUN_AND_FIX_TIMEOUT_SEC,
    ) -> Dict[str, Any]:
        """
        Execute run-and-fix loop.

        Args:
            command: Command to run (must match allowlist in run_command).
            workdir: Working directory (default: project root).
            max_rounds: Max fix rounds after first failure.
            output_dir: Optional directory for logs.
            timeout_sec: Timeout per command run.

        Returns:
            Dict with success, rounds_done, total_time_ms, total_cost_usd, message, last_stdout, last_stderr.
        """
        if not is_command_allowed(command):
            return {
                "success": False,
                "rounds_done": 0,
                "total_time_ms": 0,
                "total_cost_usd": 0.0,
                "message": f"Command not in allowlist: {command!r}",
                "last_stdout": "",
                "last_stderr": "",
            }
        base_dir = _project_root()
        workdir = Path(workdir) if workdir else base_dir
        workdir = workdir.resolve()
        if not workdir.is_dir():
            workdir = base_dir

        total_time_ms = 0.0
        total_cost_usd = 0.0
        rounds_done = 0
        last_stdout, last_stderr = "", ""

        self.orchestrator = Orchestrator(execution_mode="BUILD")
        try:
            for round_num in range(max_rounds + 1):
                exit_code, stdout, stderr = run_allowed_command(command, workdir, timeout_sec=timeout_sec)
                last_stdout, last_stderr = stdout, stderr

                if exit_code == 0:
                    return {
                        "success": True,
                        "rounds_done": rounds_done,
                        "total_time_ms": total_time_ms,
                        "total_cost_usd": total_cost_usd,
                        "message": "Command succeeded" + (f" after {rounds_done} fix(es)" if rounds_done else ""),
                        "last_stdout": last_stdout,
                        "last_stderr": last_stderr,
                    }

                if round_num >= max_rounds:
                    break

                logger.info(f"Run-and-Fix round {round_num + 1}: command failed (exit {exit_code}), asking LLM for fixes")
                file_context = _gather_file_context(workdir)
                prompt = (
                    "The following command failed. Propose code fixes so that the next run succeeds.\n\n"
                    f"Command: {command}\n\n"
                    f"Stdout:\n{stdout[:8000]}\n\n"
                    f"Stderr:\n{stderr[:8000]}\n\n"
                    "Relevant files (edit only what is necessary; output each change as FILE: path then a code block):\n"
                    f"{file_context[:60000]}\n\n"
                    "Output format: for each file to modify, write:\nFILE: path/to/file\n```lang\nfull file content or minimal patch\n```"
                )
                step_data = {
                    "id": f"fix_round_{round_num + 1}",
                    "description": prompt,
                    "type": "code_generation",
                    "complexity": 0.5,
                    "estimated_tokens": 4000,
                    "dependencies": [],
                    "validation_criteria": [],
                    "context": {"files": []},
                }
                step = Step(step_data)
                result = await self.orchestrator.agent_router.execute_step(step, prompt, surgical_mode=False)
                total_time_ms += getattr(result, "execution_time_ms", 0) or 0
                total_cost_usd += getattr(result, "cost_usd", 0) or 0
                if not result.success or not result.output:
                    logger.warning("LLM did not return fixes; stopping run-and-fix")
                    break
                blocks = _parse_file_blocks(result.output)
                if not blocks:
                    logger.warning("No FILE: blocks parsed from LLM output; stopping")
                    break
                n = _apply_fix_blocks(blocks, workdir, base_dir)
                logger.info(f"Applied {n} file(s) from LLM output")
                rounds_done += 1
        finally:
            if self.orchestrator:
                await self.orchestrator.close()

        return {
            "success": False,
            "rounds_done": rounds_done,
            "total_time_ms": total_time_ms,
            "total_cost_usd": total_cost_usd,
            "message": f"Command still failing after {rounds_done} fix(es)",
            "last_stdout": last_stdout,
            "last_stderr": last_stderr,
        }
