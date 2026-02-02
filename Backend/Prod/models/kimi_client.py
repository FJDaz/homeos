"""KIMI (Moonshot) client for gate-keeper validation."""
import httpx
from typing import Optional
from loguru import logger

from ..config.settings import settings


class KimiClient:
    """
    Client for KIMI (Moonshot) API.

    Used as gate-keeper to validate LLM output before apply.
    Fast and cheap validation layer.
    """

    def __init__(self):
        """Initialize KIMI client."""
        self.api_key = settings.kimi_api_key
        self.api_url = settings.kimi_api_url
        self.model = settings.kimi_model
        self.timeout = 30  # Short timeout for validation

        if not self.api_key:
            logger.warning("KIMI API key not configured")

    @property
    def available(self) -> bool:
        """Check if KIMI client is available."""
        return bool(self.api_key)

    async def validate_output(
        self,
        output: str,
        expected_language: str = "python",
        step_type: str = "code_generation"
    ) -> dict:
        """
        Validate LLM output before apply.

        Args:
            output: The LLM output to validate
            expected_language: Expected code language (python, html, javascript, etc.)
            step_type: Type of step (code_generation, patch, refactoring, analysis)

        Returns:
            dict with:
                - valid: bool - True if output looks safe to apply
                - reason: str - Explanation if invalid
                - detected_issue: str|None - Type of issue detected
        """
        if not self.available:
            return {"valid": True, "reason": "KIMI not available, skipping validation", "detected_issue": None}

        # Quick heuristic check first (no API call needed for obvious issues)
        quick_check = self._quick_heuristic_check(output, expected_language)
        if not quick_check["valid"]:
            return quick_check

        # If heuristic passed, use KIMI for deeper validation
        try:
            prompt = self._build_validation_prompt(output, expected_language, step_type)

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are a code validation assistant. Respond with JSON only."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.1,
                        "max_tokens": 200
                    }
                )

                if response.status_code != 200:
                    logger.warning(f"KIMI validation failed: {response.status_code}")
                    return {"valid": True, "reason": "KIMI API error, allowing through", "detected_issue": None}

                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

                return self._parse_validation_response(content)

        except Exception as e:
            logger.warning(f"KIMI validation error: {e}")
            return {"valid": True, "reason": f"KIMI error: {e}, allowing through", "detected_issue": None}

    def _quick_heuristic_check(self, output: str, expected_language: str) -> dict:
        """
        Quick heuristic check without API call.
        Catches obvious issues like JSON wrapper instead of code.
        """
        stripped = output.strip()

        # Check for JSON "operations" wrapper (common LLM mistake)
        toxic_patterns = [
            '{"operations":',
            '{"files":',
            '{"changes":',
            '"operation":',
            '"file_path":',
            '{"type": "',
        ]

        for pattern in toxic_patterns:
            if pattern in stripped[:500]:  # Check first 500 chars
                return {
                    "valid": False,
                    "reason": f"Output looks like JSON wrapper instead of {expected_language} code",
                    "detected_issue": "json_wrapper"
                }

        # Check if output starts with JSON when expecting code
        if expected_language in ["python", "html", "javascript", "typescript"]:
            if stripped.startswith("{") and '"' in stripped[:50]:
                # Could be JSON instead of code
                return {
                    "valid": False,
                    "reason": f"Output starts with JSON but expected {expected_language}",
                    "detected_issue": "json_instead_of_code"
                }

        # Check for empty or whitespace-only output
        if not stripped:
            return {
                "valid": False,
                "reason": "Output is empty",
                "detected_issue": "empty_output"
            }

        return {"valid": True, "reason": "Heuristic check passed", "detected_issue": None}

    def _build_validation_prompt(self, output: str, expected_language: str, step_type: str) -> str:
        """Build the validation prompt for KIMI."""
        # Truncate output if too long (KIMI is for quick validation)
        truncated = output[:2000] if len(output) > 2000 else output

        return f"""Validate this LLM output before applying it to a file.

Expected: {expected_language} code for step type "{step_type}"

Output to validate:
```
{truncated}
```

Check for these issues:
1. Is this actual {expected_language} code, or a JSON wrapper/metadata?
2. Does it contain harmful patterns (infinite loops, rm -rf, etc.)?
3. Is it syntactically reasonable for {expected_language}?

Respond with JSON only:
{{"valid": true/false, "reason": "brief explanation", "detected_issue": null or "issue_type"}}"""

    def _parse_validation_response(self, content: str) -> dict:
        """Parse KIMI's validation response."""
        import json

        try:
            # Try to parse as JSON
            # Handle markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            result = json.loads(content.strip())
            return {
                "valid": result.get("valid", True),
                "reason": result.get("reason", "Unknown"),
                "detected_issue": result.get("detected_issue")
            }
        except json.JSONDecodeError:
            # If KIMI didn't return valid JSON, be permissive
            logger.debug(f"KIMI returned non-JSON: {content[:100]}")
            return {"valid": True, "reason": "Could not parse KIMI response, allowing through", "detected_issue": None}
