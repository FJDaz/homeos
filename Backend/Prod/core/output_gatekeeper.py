"""Output Gate-keeper: validates LLM output before apply.

Pipeline:
1. Quick heuristic check (no API call)
2. KIMI validation (fast, cheap)
3. Claude API fallback (if KIMI fails or detects issues)

If validation fails, output goes to .generated instead of overwriting target file.
"""
import asyncio
from typing import Optional, Tuple
from pathlib import Path
from loguru import logger

from ..models.kimi_client import KimiClient
from ..config.settings import settings


class OutputGatekeeper:
    """
    Validates LLM output before applying to target files.

    Prevents catastrophic overwrites from malformed LLM responses
    (e.g., JSON "operations" wrapper instead of actual code).
    """

    def __init__(self):
        """Initialize gate-keeper with KIMI client."""
        self.kimi = KimiClient()
        self._claude_client = None  # Lazy init

    @property
    def claude_client(self):
        """Lazy initialize Claude client for fallback."""
        if self._claude_client is None and settings.anthropic_api_key:
            try:
                from ..models.claude_client import ClaudeClient
                self._claude_client = ClaudeClient()
            except Exception as e:
                logger.warning(f"Could not initialize Claude client for fallback: {e}")
        return self._claude_client

    async def validate(
        self,
        output: str,
        target_file: Optional[str] = None,
        step_type: str = "code_generation",
        expected_language: Optional[str] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Validate LLM output before apply.

        Args:
            output: The LLM output to validate
            target_file: Target file path (used to infer language)
            step_type: Type of step (code_generation, patch, refactoring, analysis)
            expected_language: Override language detection

        Returns:
            Tuple of (is_valid, reason, safe_fallback_path)
            - is_valid: True if safe to apply
            - reason: Explanation
            - safe_fallback_path: If invalid, path to write .generated file (or None)
        """
        # Infer language from target file if not provided
        if not expected_language and target_file:
            expected_language = self._infer_language(target_file)
        expected_language = expected_language or "python"

        # Step 1: KIMI validation (includes quick heuristic check)
        kimi_result = await self.kimi.validate_output(
            output=output,
            expected_language=expected_language,
            step_type=step_type
        )

        if kimi_result["valid"]:
            logger.debug(f"Gate-keeper: KIMI approved output ({kimi_result['reason']})")
            return True, kimi_result["reason"], None

        # Step 2: KIMI detected an issue - try Claude fallback for second opinion
        logger.warning(f"Gate-keeper: KIMI rejected output - {kimi_result['reason']}")

        if self.claude_client:
            claude_result = await self._claude_fallback_validation(
                output=output,
                kimi_reason=kimi_result["reason"],
                expected_language=expected_language,
                step_type=step_type
            )

            if claude_result["valid"]:
                logger.info(f"Gate-keeper: Claude overrode KIMI rejection ({claude_result['reason']})")
                return True, claude_result["reason"], None
            else:
                logger.warning(f"Gate-keeper: Claude confirmed rejection ({claude_result['reason']})")

        # Validation failed - compute fallback path
        fallback_path = None
        if target_file:
            target = Path(target_file)
            fallback_path = str(target.parent / f"{target.stem}.generated{target.suffix}")

        return False, kimi_result["reason"], fallback_path

    async def _claude_fallback_validation(
        self,
        output: str,
        kimi_reason: str,
        expected_language: str,
        step_type: str
    ) -> dict:
        """
        Use Claude API for second opinion when KIMI rejects output.
        Claude is smarter but more expensive, so only used as fallback.
        """
        if not self.claude_client:
            return {"valid": False, "reason": "Claude fallback not available"}

        try:
            import anthropic

            # Build a concise validation prompt
            truncated = output[:1500] if len(output) > 1500 else output

            prompt = f"""KIMI validation rejected this LLM output with reason: "{kimi_reason}"

Please give a second opinion. Is this valid {expected_language} code for a {step_type} operation?

Output:
```
{truncated}
```

Respond with JSON only: {{"valid": true/false, "reason": "brief explanation"}}"""

            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            response = client.messages.create(
                model="claude-3-haiku-20240307",  # Use Haiku for speed/cost
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text if response.content else ""
            return self._parse_validation_response(content)

        except Exception as e:
            logger.warning(f"Claude fallback validation error: {e}")
            return {"valid": False, "reason": f"Claude error: {e}"}

    def _parse_validation_response(self, content: str) -> dict:
        """Parse validation response from Claude."""
        import json

        try:
            # Handle markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            result = json.loads(content.strip())
            return {
                "valid": result.get("valid", False),
                "reason": result.get("reason", "Unknown")
            }
        except json.JSONDecodeError:
            # If can't parse, assume invalid (be conservative)
            logger.debug(f"Could not parse Claude response: {content[:100]}")
            return {"valid": False, "reason": "Could not parse validation response"}

    def _infer_language(self, file_path: str) -> str:
        """Infer programming language from file extension."""
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".jsx": "javascript",
            ".html": "html",
            ".htm": "html",
            ".css": "css",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".md": "markdown",
            ".sql": "sql",
            ".sh": "bash",
            ".bash": "bash",
            ".rs": "rust",
            ".go": "go",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".h": "c",
            ".hpp": "cpp",
        }

        ext = Path(file_path).suffix.lower()
        return ext_map.get(ext, "text")


# Global instance for easy access
_gatekeeper: Optional[OutputGatekeeper] = None


def get_gatekeeper() -> OutputGatekeeper:
    """Get or create the global gate-keeper instance."""
    global _gatekeeper
    if _gatekeeper is None:
        _gatekeeper = OutputGatekeeper()
    return _gatekeeper


async def validate_before_apply(
    output: str,
    target_file: Optional[str] = None,
    step_type: str = "code_generation"
) -> Tuple[bool, str, Optional[str]]:
    """
    Convenience function to validate output before apply.

    Returns:
        Tuple of (is_valid, reason, fallback_path)
    """
    gatekeeper = get_gatekeeper()
    return await gatekeeper.validate(output, target_file, step_type)
