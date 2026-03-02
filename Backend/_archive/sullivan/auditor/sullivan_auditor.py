"""Sullivan Visual Auditor – Gemini Vision UX/UI audit (Brutalist, Genome intent)."""
from __future__ import annotations

import base64
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union

from loguru import logger

# Lazy import to avoid loading Gemini when not auditing
def _gemini_client():
    from ...models.gemini_client import GeminiClient
    return GeminiClient(execution_mode="BUILD")


AUDIT_PROMPT = """You are an expert UX/UI reviewer for **Brutalist** web interfaces (raw, efficient, system fonts, no visual clutter).

Analyze the **screenshot** of the rendered HTML. The interface is intended to match a **Genome/Contract** (PaaS Studio: logs, build, gauges, execute, etc.).

Evaluate:
1. **Clarity**: Is the hierarchy clear? Can users quickly find logs, build button, status, etc.?
2. **Feedback**: Are there clear feedback mechanisms (loading states, errors, success)?
3. **Probité (Brutalist adherence)**: System fonts, minimal palette, no unnecessary decoration, Raw style. Atomic Design: Corps → Organes → logical structure.

Respond **only** with valid JSON in this exact shape (no markdown, no extra text):
```json
{
  "visual_score": 0-100,
  "critiques": ["string", "..."],
  "fixes": []
}
```
- `visual_score`: 0–100 (SullivanScore-like). 85+ = ready for production.
- `critiques`: List of concise, actionable issues (e.g. "Le bouton Build est trop petit", "Zone logs illisible").
- `fixes`: Optional. Keep empty for now; later: `[{"selector": "...", "property": "...", "value": "..."}]`.

Be strict but fair. If the UI is minimal, readable, and matches the intent, score 85+."""


@dataclass
class AuditResult:
    """Result of visual audit from Gemini."""
    visual_score: int
    critiques: List[str]
    fixes: List[Dict[str, str]]
    raw_json: Optional[str] = None
    success: bool = True
    error: Optional[str] = None

    def passed(self, threshold: int = 85) -> bool:
        return self.success and self.visual_score >= threshold


def _image_to_base64(
    screenshot_path_or_bytes: Union[str, Path, bytes],
    mime_type: str = "image/png",
) -> tuple[str, str]:
    """Load image from path or bytes, preprocess for Gemini, return (base64_string, mime_type)."""
    try:
        from ...sullivan.upload.image_preprocessor import (
            preprocess_for_gemini,
            preprocess_bytes_for_gemini,
        )
    except ImportError:
        preprocess_for_gemini = None
        preprocess_bytes_for_gemini = None

    if isinstance(screenshot_path_or_bytes, (str, Path)):
        path = Path(screenshot_path_or_bytes)
        if not path.exists():
            raise FileNotFoundError(f"Screenshot not found: {path}")
        if preprocess_for_gemini:
            raw, mime_type = preprocess_for_gemini(path)
        else:
            raw = path.read_bytes()
    elif isinstance(screenshot_path_or_bytes, bytes):
        if preprocess_bytes_for_gemini:
            raw, mime_type = preprocess_bytes_for_gemini(screenshot_path_or_bytes)
        else:
            raw = screenshot_path_or_bytes
    else:
        raise TypeError("screenshot_path_or_bytes must be path (str|Path) or bytes")
    b64 = base64.standard_b64encode(raw).decode("ascii")
    return b64, mime_type


def _parse_audit_json(raw: str) -> AuditResult:
    """Parse Gemini JSON output into AuditResult. Tolerate markdown-wrapped JSON."""
    raw_stripped = raw.strip()
    # Try to extract JSON from ```json ... ``` or ``` ... ```
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_stripped)
    if m:
        raw_stripped = m.group(1).strip()
    try:
        data = json.loads(raw_stripped)
    except json.JSONDecodeError as e:
        logger.warning(f"Audit JSON parse failed: {e}. Raw (first 500 chars): {raw[:500]}")
        return AuditResult(
            visual_score=0,
            critiques=["Failed to parse audit JSON from model."],
            fixes=[],
            raw_json=raw,
            success=False,
            error=str(e),
        )
    vs = int(data.get("visual_score", 0))
    crit = data.get("critiques") or []
    if not isinstance(crit, list):
        crit = [str(crit)]
    fixes = data.get("fixes") or []
    if not isinstance(fixes, list):
        fixes = []
    return AuditResult(
        visual_score=min(100, max(0, vs)),
        critiques=[str(c) for c in crit],
        fixes=[x if isinstance(x, dict) else {} for x in fixes],
        raw_json=raw,
        success=True,
    )


async def audit_visual_output(
    html_content: str,
    screenshot_path_or_bytes: Union[str, Path, bytes],
    genome_context: Optional[str] = None,
    mime_type: str = "image/png",
) -> AuditResult:
    """
    Run visual audit via Gemini Vision. Expert UX/UI Brutalist.

    Args:
        html_content: Full HTML (for potential future use; audit uses image).
        screenshot_path_or_bytes: Path to PNG or PNG bytes.
        genome_context: Optional intent/topology summary (e.g. "PaaS_Studio, Brainstorm|Back|Front|Deploy").
        mime_type: Image MIME type.

    Returns:
        AuditResult with visual_score, critiques, fixes.
    """
    b64, mime = _image_to_base64(screenshot_path_or_bytes, mime_type)
    prompt = AUDIT_PROMPT
    if genome_context:
        prompt = f"Genome/Contract context: {genome_context}\n\n{prompt}"

    client = _gemini_client()
    result = await client.generate_with_image(
        prompt=prompt,
        image_base64=b64,
        mime_type=mime,
        output_constraint="JSON only",
    )
    if not result.success:
        return AuditResult(
            visual_score=0,
            critiques=[],
            fixes=[],
            raw_json=None,
            success=False,
            error=result.error or "Gemini vision request failed",
        )
    return _parse_audit_json(result.code)
