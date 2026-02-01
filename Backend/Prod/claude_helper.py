"""Helper functions for Claude Code to interact with AetherFlow."""
import subprocess
import json
import re
import ast
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from loguru import logger


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
    For code_generation tasks, it creates or appends to files.
    
    Args:
        step_output: Raw output from step execution
        target_file: Path to target file to modify
        plan_step: Step dictionary from plan (contains context, type, etc.)
        
    Returns:
        True if application successful, False otherwise
    """
    try:
        # Extract code blocks from output
        code_blocks = _extract_code_blocks(step_output)
        
        if not code_blocks:
            logger.warning(f"No code blocks found in step output for {target_file}")
            return False
        
        # Get step type to determine application strategy
        step_type = plan_step.get("type", "code_generation")
        
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
        else:
            # For code_generation, create new file or append
            if target_file.exists():
                # Check if code already exists (avoid duplicates)
                existing_code = target_file.read_text(encoding="utf-8")
                if code_content.strip() not in existing_code:
                    # Append new code
                    new_content = existing_code + "\n\n" + code_content
                    target_file.write_text(new_content, encoding="utf-8")
                    logger.info(f"Appended to {target_file}")
                else:
                    logger.info(f"Code already exists in {target_file}, skipping")
            else:
                # Create new file
                target_file.write_text(code_content, encoding="utf-8")
                logger.info(f"Created {target_file}")
        
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


# Backend/Prod/sullivan/generator/component_generator.py

import json
import asyncio
from typing import Dict, Tuple
from fastapi import Depends
from pydantic import BaseModel
