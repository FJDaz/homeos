"""Sullivan refinement loop: build → screenshot → audit → revise until score > 85."""
from __future__ import annotations

import asyncio
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from loguru import logger

# Lazy imports
def _gemini():
    from ..models.gemini_client import GeminiClient
    return GeminiClient(execution_mode="BUILD")


def _build_html(genome: Union[str, Path, Dict], base_url: str) -> str:
    from .builder.sullivan_builder import build_html
    return build_html(genome, base_url=base_url)


async def _capture(html: str) -> bytes:
    from .auditor.screenshot_util import capture_html_screenshot
    return await capture_html_screenshot(html, full_page=True)


async def _audit(html: str, screenshot: Union[str, Path, bytes], genome_context: Optional[str] = None):
    from .auditor.sullivan_auditor import audit_visual_output
    return await audit_visual_output(html, screenshot, genome_context=genome_context)


REVISE_PROMPT = """You are an expert Brutalist UI designer. Revise the HTML below based on these critiques.

Critiques:
{critiques}

Rules:
- Keep Brutalist style: system fonts, minimal palette, no external libs, raw.
- Preserve structure: sidebar (topology) + main (organes), data-path/data-method on organes, inline fetch JS.
- Fix only what the critiques mention (e.g. button size, contrast, hierarchy).
- Return the **complete** revised HTML document only. No markdown, no explanation."""


def _extract_html(raw: str) -> str:
    """Extract HTML from model output (strip ```html ... ``` if present)."""
    s = raw.strip()
    m = re.search(r"```(?:html)?\s*([\s\S]*?)\s*```", s)
    if m:
        return m.group(1).strip()
    return s


async def _revise_html(html: str, critiques: List[str]) -> str:
    """Ask Gemini to revise HTML given critiques; return revised HTML."""
    if not critiques:
        return html
    prompt = REVISE_PROMPT.format(critiques="\n".join(f"- {c}" for c in critiques))
    client = _gemini()
    # Révision HTML = document complet ; 4000 tokens par défaut peut tronquer → 16384
    result = await client.generate(
        prompt,
        context=f"Current HTML (first 12_000 chars):\n{html[:12000]}",
        output_constraint="Code only",
        max_tokens=16384,
    )
    if not result.success or not result.code:
        logger.warning("Gemini revise failed, keeping original HTML")
        return html
    return _extract_html(result.code)


async def run_refinement(
    genome: Union[str, Path, Dict[str, Any]],
    output_path: Optional[Union[str, Path]] = None,
    base_url: str = "http://localhost:8000",
    max_iterations: int = 5,
    score_threshold: int = 85,
) -> Tuple[Path, str, Optional[Any]]:
    """
    Build → screenshot → audit → revise until visual_score >= score_threshold or max iterations.

    Returns:
        (path_to_html, final_html, last_audit_result or None)
    """
    genome_path = Path(genome) if isinstance(genome, (str, Path)) and Path(genome).exists() else None
    if output_path is None:
        output_path = Path("output/studio/studio_index.html")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    genome_context: Optional[str] = None
    if isinstance(genome, dict):
        meta = genome.get("metadata") or {}
        topo = genome.get("topology") or []
        genome_context = f"{meta.get('intent', 'PaaS_Studio')}, topology: {', '.join(topo)}"
    elif genome_path:
        import json
        try:
            g = json.loads(genome_path.read_text(encoding="utf-8"))
            meta = g.get("metadata") or {}
            topo = g.get("topology") or []
            genome_context = f"{meta.get('intent', 'PaaS_Studio')}, topology: {', '.join(topo)}"
        except Exception:
            pass

    html = _build_html(genome, base_url)
    last_audit = None

    for it in range(max_iterations):
        logger.info(f"Refinement iteration {it + 1}/{max_iterations}")
        screenshot = await _capture(html)
        last_audit = await _audit(html, screenshot, genome_context=genome_context)
        logger.info(f"  visual_score={last_audit.visual_score}, critiques={len(last_audit.critiques)}")

        if last_audit.passed(score_threshold):
            logger.info(f"Audit passed (score >= {score_threshold})")
            break
        if it + 1 >= max_iterations:
            logger.warning(f"Max iterations {max_iterations} reached, score={last_audit.visual_score}")
            break

        html = await _revise_html(html, last_audit.critiques)

    output_path.write_text(html, encoding="utf-8")
    logger.info(f"Wrote {output_path}")
    return output_path, html, last_audit

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from typing import Dict, Optional
from pathlib import Path
import json
import logging
from gemini_client import GeminiClient

app = FastAPI()

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Generator:
    def _load_webography(self, path: Optional[Path] = None) -> str:
        """
        Load webography from file.

        Args:
        path (Optional[Path]): Path to webography file. Defaults to None.

        Returns:
        str: Webography text or empty string if file is not found.
        """
        if path is None:
            path = Path(__file__).resolve().parents[3] / 'docs' / '02-sullivan' / 'Références webdesign de Sullivan.md'
        
        try:
            with open(path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            return ""

    async def generate_html_from_design(self, design_structure: Dict, frontend_structure: Dict, image_path: Optional[Path], webography_text: str, output_path: Path) -> str:
        """
        Generate HTML from design and frontend structures.

        Args:
        design_structure (Dict): Design structure.
        frontend_structure (Dict): Frontend structure.
        image_path (Optional[Path]): Image path.
        webography_text (str): Webography text.
        output_path (Path): Output path.

        Returns:
        str: Generated HTML.
        """
        # Build prompt
        prompt = f"Page vierge. Contexte: {json.dumps({'design_structure': design_structure, 'frontend_structure': frontend_structure})}. Webographie: {webography_text}. Instruction: Générez un document HTML/CSS/JS complet single-file brutalist."
        
        # Truncate context if too large
        if len(prompt) > 12000:
            prompt = prompt[:12000]
        
        # Call Gemini API
        gemini_client = GeminiClient(execution_mode='BUILD')
        response = await gemini_client.generate(prompt, context={}, output_constraint='Code only', max_tokens=16384)
        
        # Extract HTML from response
        html = self._extract_html(response)
        
        # Write HTML to output path
        with open(output_path, 'w') as file:
            file.write(html)
        
        return html

    def _extract_html(self, response: str) -> str:
        """
        Extract HTML from response.

        Args:
        response (str): Response from Gemini API.

        Returns:
        str: Extracted HTML.
        """
        # Find