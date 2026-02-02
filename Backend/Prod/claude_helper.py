"""Helper functions for Claude Code to interact with AetherFlow."""
import subprocess
import json
import re
import ast
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from loguru import logger


def _validate_output_sync(
    output: str,
    target_file: Optional[str] = None,
    step_type: str = "code_generation"
) -> Tuple[bool, str, Optional[str]]:
    """
    Synchronous wrapper for gate-keeper validation.

    Calls the async gate-keeper from sync code using asyncio.run().

    Returns:
        Tuple of (is_valid, reason, fallback_path)
    """
    try:
        from .core.output_gatekeeper import validate_before_apply

        # Run async validation in event loop
        try:
            loop = asyncio.get_running_loop()
            # If there's already a running loop, we can't use asyncio.run
            # Fall back to quick heuristic check only
            return _quick_heuristic_check(output, target_file)
        except RuntimeError:
            # No running loop, safe to use asyncio.run
            return asyncio.run(validate_before_apply(output, target_file, step_type))
    except ImportError as e:
        logger.debug(f"Gate-keeper not available: {e}")
        return True, "Gate-keeper not available", None
    except Exception as e:
        logger.warning(f"Gate-keeper validation error: {e}")
        return True, f"Validation error: {e}", None


def _quick_heuristic_check(
    output: str,
    target_file: Optional[str] = None
) -> Tuple[bool, str, Optional[str]]:
    """
    Quick heuristic check for obvious issues (no async/API call).
    Used when async validation is not possible.
    """
    stripped = output.strip()

    # Check for JSON "operations" wrapper (common LLM mistake)
    toxic_patterns = [
        '{"operations":',
        '{"files":',
        '{"changes":',
        '"operation":',
    ]

    for pattern in toxic_patterns:
        if pattern in stripped[:500]:
            fallback = None
            if target_file:
                p = Path(target_file)
                fallback = str(p.parent / f"{p.stem}.generated{p.suffix}")
            return False, f"Output looks like JSON wrapper instead of code", fallback

    return True, "Heuristic check passed", None


def detect_planner_choice(user_message: str) -> Optional[str]:
    """
    Detect planner choice in user message.
    
    Supports BYOK (Bring Your Own Key) and BYOC (Bring Your Own Cursor/Claude) patterns.
    
    Options are parallel (not mutually exclusive):
    - BYOK: Claude API key (pay-per-use)
    - BYOC Cursor: Cursor Pro subscription
    - BYOC Claude: Claude Pro/MAX subscription
    
    Returns:
    - "claude_code" if Cursor Pro subscription (BYOC Cursor)
    - "claude_api" if Claude API key (BYOK) or Claude Pro/MAX subscription (BYOC Claude)
    - "gemini" if Gemini
    - "deepseek" if DeepSeek
    - None if no explicit choice
    """
    message_lower = user_message.lower()
    
    # Patterns for Claude Code (Cursor Pro subscription / BYOC Cursor)
    if any(phrase in message_lower for phrase in [
        "formule actuelle", "cursor", "claude code", 
        "utilise cursor", "avec cursor", "byoc cursor",
        "mon abonnement cursor", "mon cursor", "cursor pro"
    ]):
        return "claude_code"
    
    # Patterns for Claude API (BYOK - key) or Claude Pro/MAX (BYOC Claude - subscription)
    # Note: Both use claude_api, distinction is commercial (key vs subscription)
    if any(phrase in message_lower for phrase in [
        "claude api", "claude sonnet", "utilise claude api",
        "avec claude api", "claude standalone", "byok",
        "ma clé claude", "ma clé anthropic",
        # Claude Pro/MAX subscription patterns
        "claude pro", "claude max", "mon abonnement claude",
        "mon claude.ai", "byoc claude", "claude.ai"
    ]):
        return "claude_api"
    
    # Patterns for Gemini
    if any(phrase in message_lower for phrase in [
        "gemini", "utilise gemini", "avec gemini"
    ]):
        return "gemini"
    
    # Patterns for DeepSeek
    if any(phrase in message_lower for phrase in [
        "deepseek", "utilise deepseek", "avec deepseek"
    ]):
        return "deepseek"
    
    return None


def execute_plan_cli(
    plan_path: str, 
    output_dir: Optional[str] = None,
    planner: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute a plan using AetherFlow CLI.
    
    Claude Code can call this function to execute a plan.
    
    Args:
        plan_path: Path to plan.json file
        output_dir: Optional output directory
        planner: Optional planner choice (claude_code|claude_api|gemini|deepseek|auto)
        
    Returns:
        Dictionary with execution results
    """
    cmd = ["python", "-m", "Backend.Prod.cli", "--plan", plan_path]
    if output_dir:
        cmd.extend(["--output", output_dir])
    if planner:
        cmd.extend(["--planner", planner])
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent.parent
    )
    
    if result.returncode != 0:
        return {
            "success": False,
            "error": result.stderr,
            "output": result.stdout
        }
    
    # Try to find metrics file
    plan_file = Path(plan_path)
    task_id = None
    if plan_file.exists():
        with open(plan_file) as f:
            plan_data = json.load(f)
            task_id = plan_data.get("task_id")
    
    output_path = Path(output_dir) if output_dir else Path("output")
    metrics_file = output_path / f"metrics_{task_id}.json" if task_id else None
    
    results = {
        "success": True,
        "output": result.stdout,
        "metrics_file": str(metrics_file) if metrics_file and metrics_file.exists() else None
    }
    
    if metrics_file and metrics_file.exists():
        with open(metrics_file) as f:
            results["metrics"] = json.load(f)
    
    return results


def split_structure_and_code(raw_output: str) -> Tuple[str, str]:
    """
    Split raw LLM output into structure part (file tree / arborescence) and code part.
    The structure part is never applied to code files; only code_part is used by apply.

    Detects:
    - Explicit blocks ```file_tree ... ``` or ```structure ... ```
    - Consecutive lines that look like a directory tree (├──, │, └──).

    Returns:
        (structure_part, code_part). If no structure detected, structure_part is "", code_part is raw_output.
    """
    if not raw_output or not raw_output.strip():
        return ("", raw_output)

    text = raw_output

    # 1. Explicit block ```file_tree ... ``` or ```structure ... ```
    for block_name in ("file_tree", "structure"):
        pattern = rf"```\s*{block_name}\s*\n(.*?)```"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            structure_part = match.group(1).strip()
            code_part = (text[: match.start()] + text[match.end() :]).strip()
            return (structure_part, code_part)

    # 2. Consecutive lines that look like a directory tree (├──, │, └──)
    tree_prefix = re.compile(r"^\s*[├│└]\s*")
    lines = text.split("\n")
    structure_lines: List[int] = []
    i = 0
    while i < len(lines):
        if tree_prefix.search(lines[i]):
            start = i
            while i < len(lines) and tree_prefix.search(lines[i]):
                structure_lines.append(i)
                i += 1
            # Require at least 2 consecutive tree lines to consider it a structure block
            if len(structure_lines) >= 2:
                structure_part = "\n".join(lines[j] for j in structure_lines)
                code_lines = [lines[j] for j in range(len(lines)) if j not in structure_lines]
                code_part = "\n".join(code_lines).strip()
                return (structure_part, code_part)
            structure_lines.clear()
        else:
            i += 1

    return ("", raw_output)


def get_step_output(step_id: str, output_dir: str = "output") -> Optional[str]:
    """
    Get the output of a specific step (code part only, for apply).
    Prefers step_X_code.txt when present (structure-free content); otherwise step_X.txt for backward compat.
    """
    outputs_dir = Path(output_dir) / "step_outputs"
    code_file = outputs_dir / f"{step_id}_code.txt"
    if code_file.exists():
        return code_file.read_text(encoding="utf-8")
    full_file = outputs_dir / f"{step_id}.txt"
    if full_file.exists():
        return full_file.read_text(encoding="utf-8")
    return None


def _strip_markdown_fence(content: str) -> str:
    """Strip one level of outer markdown code fence (```markdown ... ``` or ``` ... ```)."""
    if not content or not content.strip():
        return content
    lines = content.strip().split("\n")
    if not lines or not lines[0].strip().startswith("```"):
        return content.strip()
    start = 1
    end = len(lines)
    if len(lines) >= 2 and lines[-1].strip() == "```":
        end = len(lines) - 1
    return "\n".join(lines[start:end]).strip()


def merge_step_outputs_to_file(
    step_ids: List[str],
    output_dir: str,
    merge_file_path: Path,
    separator: str = "\n\n---\n\n",
) -> bool:
    """
    Concatenate step outputs (in order) and write to a single file.
    Used for chunked report plans: each step produces one section, we merge on our side.
    Strips outer markdown fence from each part. Creates parent dirs.
    """
    parts = []
    for step_id in step_ids:
        out = get_step_output(step_id, output_dir)
        if out and out.strip():
            parts.append(_strip_markdown_fence(out))
    if not parts:
        logger.warning(f"No step outputs to merge for {merge_file_path}")
        return False
    content = separator.join(parts)
    merge_file_path = Path(merge_file_path)
    merge_file_path.parent.mkdir(parents=True, exist_ok=True)
    merge_file_path.write_text(content, encoding="utf-8")
    logger.info(f"Merged {len(parts)} step outputs to {merge_file_path} ({len(content)} chars)")
    return True


def _extract_code_blocks(step_output: str) -> List[Tuple[str, str]]:
    """
    Extract code blocks from step output.
    
    Supports:
    - Markdown code blocks (```python, ```javascript, etc.)
    - Plain code blocks (```)
    - Inline code blocks
    
    Args:
        step_output: Raw step output text
        
    Returns:
        List of tuples (language, code_content)
    """
    code_blocks = []
    
    # Pattern for markdown code blocks: ```language\ncode\n```
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.finditer(pattern, step_output, re.DOTALL)
    
    for match in matches:
        language = match.group(1) or "python"  # Default to Python
        code_content = match.group(2).strip()
        if code_content:
            code_blocks.append((language.lower(), code_content))
    
    # If no code blocks found, try to extract code after "```python" or similar markers
    if not code_blocks:
        # Look for code after language markers
        lang_patterns = {
            "python": r'(?:```python|```py|python:)\s*\n(.*?)(?:```|$)',
            "javascript": r'(?:```javascript|```js|javascript:)\s*\n(.*?)(?:```|$)',
            "typescript": r'(?:```typescript|```ts|typescript:)\s*\n(.*?)(?:```|$)',
        }
        
        for lang, pattern in lang_patterns.items():
            matches = re.finditer(pattern, step_output, re.DOTALL)
            for match in matches:
                code_content = match.group(1).strip()
                if code_content and len(code_content) > 50:  # Minimum reasonable code size
                    code_blocks.append((lang, code_content))
                    break
    
    return code_blocks


def _apply_patch_fragment(
    existing_content: str,
    fragment: str,
    patch_config: Dict[str, Any],
) -> Optional[str]:
    """
    Apply a fragment to existing file content at marker/line (patch mode).
    Spec: docs/references/technique/PLAN_STEP_TYPE_PATCH_SPEC.md

    Args:
        existing_content: Full file content.
        fragment: Code fragment to insert or use as replacement.
        patch_config: Must have "position" (after|before|replace) and either
            "marker", or "line" (1-based), or "marker_start"+"marker_end" for replace.

    Returns:
        New file content, or None if marker/line not found or config invalid.
    """
    position = patch_config.get("position")
    if position not in ("after", "before", "replace"):
        logger.warning(f"PATCH: invalid position '{position}'")
        return None

    lines = existing_content.splitlines(keepends=True)
    if not lines:
        return None

    def find_line_number(needle: str) -> Optional[int]:
        for i, line in enumerate(lines):
            if needle in line:
                return i + 1  # 1-based
        return None

    target_line: Optional[int] = None
    target_line_end: Optional[int] = None  # for replace (inclusive)

    if "line" in patch_config:
        ln = int(patch_config["line"])
        if 1 <= ln <= len(lines):
            target_line = ln
        else:
            logger.warning(f"PATCH: line {ln} out of range (1..{len(lines)})")
            return None
    elif position == "replace" and "marker_start" in patch_config and "marker_end" in patch_config:
        start = find_line_number(patch_config["marker_start"])
        end = find_line_number(patch_config["marker_end"])
        if start is None:
            logger.warning(f"PATCH: marker_start not found")
            return None
        if end is None:
            logger.warning(f"PATCH: marker_end not found")
            return None
        if end < start:
            logger.warning(f"PATCH: marker_end before marker_start")
            return None
        target_line = start
        target_line_end = end
    elif "marker" in patch_config:
        target_line = find_line_number(patch_config["marker"])
        if target_line is None:
            logger.warning(f"PATCH: marker not found")
            return None
        if position == "replace":
            target_line_end = target_line  # replace single line
    else:
        logger.warning("PATCH: need marker, line, or marker_start+marker_end")
        return None

    # Normalize fragment: ensure trailing newline if multi-line
    fragment_stripped = fragment.rstrip()
    if "\n" in fragment_stripped:
        fragment_content = fragment_stripped + "\n"
    else:
        fragment_content = fragment_stripped + "\n"

    # Build new content
    # Convert to 0-based indices
    idx = target_line - 1
    if target_line_end is not None:
        idx_end = target_line_end - 1
    else:
        idx_end = idx

    if position == "after":
        # Insert fragment after line target_line (after index idx)
        new_lines = lines[: idx + 1] + [fragment_content] + lines[idx + 1 :]
    elif position == "before":
        # Insert fragment before line target_line (before index idx)
        new_lines = lines[:idx] + [fragment_content] + lines[idx:]
    else:
        # replace: replace lines [idx .. idx_end] (inclusive) with fragment
        new_lines = lines[:idx] + [fragment_content] + lines[idx_end + 1 :]

    return "".join(new_lines)


def _determine_file_extension(language: str) -> str:
    """
    Determine file extension from language name.
    
    Args:
        language: Language name (python, javascript, etc.)
        
    Returns:
        File extension (e.g., ".py", ".js")
    """
    extension_map = {
        "python": ".py",
        "py": ".py",
        "javascript": ".js",
        "js": ".js",
        "typescript": ".ts",
        "ts": ".ts",
        "html": ".html",
        "css": ".css",
        "json": ".json",
        "markdown": ".md",
        "md": ".md",
    }
    return extension_map.get(language.lower(), ".py")


def apply_generated_code(
    step_output: str,
    target_file: Path,
    plan_step: Dict[str, Any]
) -> bool:
    """
    Apply generated code from step output to target file.

    This function parses the step output, extracts code blocks, and applies
    them to the target file. For refactoring tasks, it modifies existing code.
    For code_generation tasks, it creates or replaces files.
    For patch tasks, it inserts or replaces a fragment at marker/line (see PLAN_STEP_TYPE_PATCH_SPEC.md).

    For target files with extension .md or .markdown, the entire step_output
    is written as-is (no code block extraction), so that document/markdown
    content is not mistaken for code or lost when no ``` blocks are present.

    Args:
        step_output: Raw output from step execution
        target_file: Path to target file to modify
        plan_step: Step dictionary from plan (contains context, type, etc.)

    Returns:
        True if application successful, False otherwise
    """
    try:
        # For .md / .markdown targets: write full step_output as document content
        ext = target_file.suffix.lower()
        if ext in (".md", ".markdown"):
            if not step_output or not step_output.strip():
                logger.warning(f"Empty step output for markdown target {target_file}")
                return False
            content = step_output.strip()
            # Strip one level of outer markdown code fence if present (LLM often wraps in ```markdown ... ```)
            lines = content.split("\n")
            if lines and lines[0].strip().startswith("```"):
                start = 1
                end = len(lines)
                if len(lines) >= 2 and lines[-1].strip() == "```":
                    end = len(lines) - 1
                content = "\n".join(lines[start:end]).strip()
                logger.debug(f"Stripped outer markdown code fence for {target_file}")
            target_file.parent.mkdir(parents=True, exist_ok=True)
            target_file.write_text(content, encoding="utf-8")
            logger.info(f"Wrote document content to {target_file} ({len(content)} chars)")
            return True

        # Extract code blocks from output for non-markdown targets
        code_blocks = _extract_code_blocks(step_output)

        if not code_blocks:
            logger.warning(f"No code blocks found in step output for {target_file}")
            return False

        # Get step type to determine application strategy
        step_type = plan_step.get("type", "code_generation")

        # Gate-keeper validation: check output before apply
        # Prevents catastrophic overwrites from malformed LLM responses
        language, code_content = code_blocks[0]
        is_valid, reason, fallback_path = _validate_output_sync(
            output=code_content,
            target_file=str(target_file),
            step_type=step_type
        )
        if not is_valid:
            logger.warning(f"GATE-KEEPER REJECTED: {reason}")
            if fallback_path:
                # Write to .generated file instead of target
                Path(fallback_path).parent.mkdir(parents=True, exist_ok=True)
                Path(fallback_path).write_text(code_content, encoding="utf-8")
                logger.warning(f"Output saved to {fallback_path} for manual review")
            return False
        
        # Determine language from first code block or file extension
        language, code_content = code_blocks[0]
        if not language:
            # Infer from file extension
            ext = target_file.suffix
            if ext == ".py":
                language = "python"
            elif ext in [".js", ".jsx"]:
                language = "javascript"
            elif ext in [".ts", ".tsx"]:
                language = "typescript"
            else:
                language = "python"  # Default
        
        # Ensure target file directory exists
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Apply code based on step type
        if step_type == "refactoring":
            # For refactoring, DO NOT overwrite existing files
            # This prevents destructive overwrites of production code
            if target_file.exists():
                # Save generated code to a separate file for manual review/merge
                generated_file = target_file.with_suffix(f".generated{target_file.suffix}")
                generated_file.write_text(code_content, encoding="utf-8")
                logger.warning(
                    f"REFACTORING: Generated code saved to {generated_file} "
                    f"(manual merge required with {target_file})"
                )
                # Return True because generation succeeded, even if not auto-applied
                return True
            else:
                # File doesn't exist, safe to create it
                target_file.write_text(code_content, encoding="utf-8")
                logger.info(f"Created {target_file} (refactoring)")
        elif step_type == "patch":
            # Patch: insert or replace fragment at marker/line in existing file
            context = plan_step.get("context") or {}
            patch_config = context.get("patch")
            if not patch_config or not isinstance(patch_config, dict):
                logger.warning("PATCH: context.patch missing or invalid for step type patch")
                return False
            if not target_file.exists():
                logger.warning(f"PATCH: target file does not exist: {target_file}")
                return False
            existing_content = target_file.read_text(encoding="utf-8")
            # Idempotent: skip if fragment already present (first significant line as signature)
            if patch_config.get("idempotent"):
                sig_line = next(
                    (ln.strip() for ln in code_content.strip().split("\n") if ln.strip()),
                    "",
                )
                if sig_line and sig_line in existing_content:
                    logger.info(f"PATCH: fragment already present (idempotent), skipping {target_file}")
                    return True
            new_content = _apply_patch_fragment(existing_content, code_content, patch_config)
            if new_content is None:
                return False
            target_file.write_text(new_content, encoding="utf-8")
            logger.info(f"Patched {target_file} (position={patch_config.get('position')})")
        else:
            # For code_generation, REPLACE file content (not append)
            # Appending caused corruption (duplicate content, mixed files)
            if target_file.exists():
                existing_code = target_file.read_text(encoding="utf-8")
                # Only write if content is different
                if code_content.strip() != existing_code.strip():
                    target_file.write_text(code_content, encoding="utf-8")
                    logger.info(f"Replaced {target_file}")
                else:
                    logger.info(f"Content unchanged in {target_file}, skipping")
            else:
                # Create new file
                target_file.write_text(code_content, encoding="utf-8")
                logger.info(f"Created {target_file}")

        # POST-APPLY VALIDATION: syntax check + targeted tests + auto-rollback
        # Game changer: test what you implement, immediately
        try:
            from .core.post_apply_validator import validate_after_apply

            # Determine project root from target file
            project_root = target_file.parent
            while project_root != project_root.parent:
                if (project_root / ".git").exists() or (project_root / "pyproject.toml").exists():
                    break
                project_root = project_root.parent

            # Run validation (syntax + tests + auto-rollback on failure)
            run_tests = plan_step.get("context", {}).get("run_tests", True)
            auto_rollback = plan_step.get("context", {}).get("auto_rollback", True)

            success, message, test_output = validate_after_apply(
                file_path=target_file,
                run_tests=run_tests,
                auto_rollback=auto_rollback,
                project_root=project_root
            )

            if not success:
                logger.error(f"POST-APPLY VALIDATION FAILED: {message}")
                if test_output:
                    logger.debug(f"Test output:\n{test_output[:1000]}")
                return False
            else:
                logger.info(f"POST-APPLY VALIDATION OK: {message}")

        except ImportError:
            logger.debug("Post-apply validator not available, skipping")
        except Exception as e:
            logger.warning(f"Post-apply validation error (non-fatal): {e}")

        return True
        
    except Exception as e:
        logger.error(f"Failed to apply generated code to {target_file}: {e}")
        logger.exception("Error details")
        return False


async def generate_plan_with_planner(
    description: str,
    context: Optional[str] = None,
    planner: Optional[str] = None,
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a plan using the specified planner.
    
    Claude Code can call this function to generate a plan with a specific planner.
    
    Args:
        description: Task description
        context: Optional additional context
        planner: Planner choice (claude_code|claude_api|gemini|deepseek|auto)
        output_path: Optional path to save the plan
        
    Returns:
        Dictionary with plan data and metadata
    """
    import asyncio
    from .planners import PlannerManager
    
    planner_manager = PlannerManager(planner_mode=planner or "auto")
    
    try:
        plan = await planner_manager.generate_plan(
            description=description,
            context=context,
            output_path=Path(output_path) if output_path else None,
            force_planner=planner
        )
        
        # If plan is None, it means Claude Code should handle it
        if plan is None:
            return {
                "success": True,
                "planner": "claude_code",
                "message": "Using Claude Code (Cursor) for plan generation"
            }
        
        return {
            "success": True,
            "plan": plan,
            "planner": plan.get("metadata", {}).get("planner_used", "unknown"),
            "output_path": output_path
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "planner": planner or "auto"
        }
