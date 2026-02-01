"""Run allowed commands for Run-and-Fix workflow (build/deploy correction)."""
import re
import subprocess
from pathlib import Path
from typing import Tuple
from loguru import logger


ALLOWED_COMMAND_PATTERNS = [
    r"^npm\s+run\s+",
    r"^pnpm\s+run\s+",
    r"^yarn\s+",
    r"^cd\s+[\w./\-]+\s+&&\s+(npm|pnpm|yarn)\s+",
    r"^docker\s+build\s+",
    r"^python\s+-m\s+(pytest|build)\s*",
    r"^\./[\w\-]+\.sh\s*",
]


def is_command_allowed(command: str) -> bool:
    """Return True if command matches one of the allowed patterns."""
    cmd = command.strip()
    for pattern in ALLOWED_COMMAND_PATTERNS:
        if re.search(pattern, cmd):
            return True
    return False


def run_allowed_command(
    command: str,
    cwd: Path,
    timeout_sec: int = 120,
    shell: bool = True,
) -> Tuple[int, str, str]:
    """
    Run a command if it is in the allowlist.

    Returns:
        (exit_code, stdout, stderr).

    Raises:
        ValueError: If command is not allowed.
    """
    if not is_command_allowed(command):
        raise ValueError(
            f"Command not in allowlist: {command!r}. "
            "Allowed: npm run *, pnpm run *, yarn *, cd ... && (npm|pnpm|yarn) *, docker build *, python -m pytest/build, ./script.sh"
        )
    cwd = Path(cwd).resolve()
    if not cwd.is_dir():
        raise FileNotFoundError(f"Working directory does not exist: {cwd}")
    logger.info(f"Running allowed command: {command!r} (cwd={cwd}, timeout={timeout_sec}s)")
    try:
        result = subprocess.run(
            command,
            shell=shell,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
        return (result.returncode, result.stdout or "", result.stderr or "")
    except subprocess.TimeoutExpired:
        logger.warning(f"Command timed out after {timeout_sec}s")
        return (-1, "", f"Command timed out after {timeout_sec}s")
    except Exception as e:
        logger.exception("run_allowed_command failed")
        return (-1, "", str(e))
