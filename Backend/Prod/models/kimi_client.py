"""KIMI (Moonshot) client — OpenAI-compatible SDK."""
import asyncio
import json
from typing import Optional
from loguru import logger

from ..config.settings import settings


class KimiClient:
    """Client KIMI via OpenAI SDK. base_url = https://api.moonshot.ai/v1"""

    def __init__(self):
        self.api_key = settings.kimi_api_key
        self.base_url = settings.kimi_api_url  # https://api.moonshot.ai/v1
        self.model = settings.kimi_model       # kimi-k2-turbo-preview
        if not self.api_key:
            logger.warning("KIMI API key not configured")

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def _get_client(self):
        """Return an OpenAI client pointed at Moonshot API."""
        from openai import OpenAI
        return OpenAI(base_url=self.base_url, api_key=self.api_key)

    async def generate_svg(
        self,
        prompt: str,
        system_prompt: str = "You are a professional SVG UI designer specializing in high-fidelity wireframes."
    ) -> Optional[str]:
        """Generate an SVG string from a prompt. Returns raw SVG string or None."""
        if not self.available:
            return None
        try:
            client = self._get_client()
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=16000,
                extra_body={"thinking": {"type": "disabled"}},
            )
            content = response.choices[0].message.content or ""
            if "<svg" in content:
                return content[content.find("<svg"):content.rfind("</svg>") + 6]
            return None
        except Exception as e:
            logger.error(f"KIMI generate_svg error: {e}")
            return None

    async def validate_output(
        self,
        output: str,
        expected_language: str = "python",
        step_type: str = "code_generation"
    ) -> dict:
        """Gate-keeper validation. Returns {valid, reason, detected_issue}."""
        if not self.available:
            return {"valid": True, "reason": "KIMI not available", "detected_issue": None}

        quick = self._quick_heuristic_check(output, expected_language)
        if not quick["valid"]:
            return quick

        try:
            client = self._get_client()
            prompt = self._build_validation_prompt(output, expected_language, step_type)
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code validation assistant. Respond with JSON only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                extra_body={"thinking": {"type": "disabled"}},
            )
            content = response.choices[0].message.content or ""
            return self._parse_validation_response(content)
        except Exception as e:
            logger.warning(f"KIMI validation error: {e}")
            return {"valid": True, "reason": f"KIMI error: {e}", "detected_issue": None}

    def _quick_heuristic_check(self, output: str, expected_language: str) -> dict:
        stripped = output.strip()
        toxic = ['{"operations":', '{"files":', '{"changes":', '"operation":', '"file_path":']
        for p in toxic:
            if p in stripped[:500]:
                return {
                    "valid": False,
                    "reason": f"JSON wrapper instead of {expected_language}",
                    "detected_issue": "json_wrapper"
                }
        if not stripped:
            return {"valid": False, "reason": "Empty output", "detected_issue": "empty_output"}
        return {"valid": True, "reason": "Heuristic passed", "detected_issue": None}

    def _build_validation_prompt(self, output: str, expected_language: str, step_type: str) -> str:
        truncated = output[:2000]
        return (
            f"Validate this LLM output before applying to a file.\n"
            f"Expected: {expected_language} code for step type \"{step_type}\"\n"
            f"Output:\n```\n{truncated}\n```\n"
            f"Check: is this actual code or a JSON wrapper? Any harmful patterns?\n"
            f'Respond JSON only: {{"valid": true/false, "reason": "...", "detected_issue": null}}'
        )

    def _parse_validation_response(self, content: str) -> dict:
        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            result = json.loads(content.strip())
            return {
                "valid": result.get("valid", True),
                "reason": result.get("reason", ""),
                "detected_issue": result.get("detected_issue")
            }
        except Exception:
            return {"valid": True, "reason": "Parse error, allowing through", "detected_issue": None}

    async def execute_step(
        self,
        step,
        context: Optional[str] = None,
        system_context: Optional[str] = None
    ):
        """Execute an AetherFlow step using KIMI."""
        from .deepseek_client import StepResult
        import time

        if not self.available:
            return StepResult(
                step_id=step.id, success=False, output="",
                tokens_used=0, input_tokens=0, output_tokens=0,
                execution_time_ms=0, error="KIMI API key not configured", cost_usd=0.0
            )

        start = time.time()
        try:
            client = self._get_client()
            messages = []
            if system_context:
                messages.append({"role": "system", "content": system_context})
            else:
                messages.append({
                    "role": "system",
                    "content": "You are an expert software engineer. Generate clean, well-structured code."
                })
            user_content = (context + "\n\n" if context else "") + f"Task: {step.description}\nType: {step.type}"
            messages.append({"role": "user", "content": user_content})

            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=self.model,
                messages=messages,
                max_tokens=16384,
                extra_body={"thinking": {"type": "disabled"}},
            )
            elapsed = (time.time() - start) * 1000
            output = response.choices[0].message.content or ""
            usage = response.usage
            in_tok = usage.prompt_tokens if usage else 0
            out_tok = usage.completion_tokens if usage else 0
            total = usage.total_tokens if usage else 0
            cost = (total / 1_000_000) * 0.015

            logger.info(f"KIMI step {step.id} completed: {total} tokens, ${cost:.4f}")
            return StepResult(
                step_id=step.id, success=True, output=output,
                tokens_used=total, input_tokens=in_tok, output_tokens=out_tok,
                execution_time_ms=elapsed, error=None, cost_usd=cost
            )
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return StepResult(
                step_id=step.id, success=False, output="",
                tokens_used=0, input_tokens=0, output_tokens=0,
                execution_time_ms=elapsed, error=str(e), cost_usd=0.0
            )
