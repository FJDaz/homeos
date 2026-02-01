"""Generate single-file HTML from design structure + frontend structure (page vierge + webographie)."""
from pathlib import Path
from typing import Dict, Optional
import json
import re
from loguru import logger


def _load_webography(path: Optional[Path] = None) -> str:
    """
    Load webography from file.

    Args:
        path: Path to webography file. Defaults to docs/02-sullivan/Références webdesign de Sullivan.md at repo root.

    Returns:
        Webography text or empty string if file is not found.
    """
    if path is None:
        # Repo root: Backend/Prod/sullivan/generator -> parents[4] = AETHERFLOW
        root = Path(__file__).resolve().parents[4]
        path = root / "docs" / "02-sullivan" / "Références webdesign de Sullivan.md"
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning(f"Webography file not found: {path}")
        return ""


def _extract_html(raw: str) -> str:
    """Extract HTML from model output (strip ```html ... ``` if present)."""
    s = raw.strip()
    m = re.search(r"```(?:html)?\s*([\s\S]*?)\s*```", s)
    if m:
        return m.group(1).strip()
    return s


async def generate_html_from_design(
    design_structure: Dict,
    frontend_structure: Dict,
    image_path: Optional[Path],
    webography_text: str,
    output_path: Path,
) -> str:
    """
    Generate HTML from design and frontend structures (page vierge, webographie, single-file brutalist).

    Args:
        design_structure: Design structure (from DesignAnalyzer).
        frontend_structure: Frontend structure (Miroir).
        image_path: Optional image path for context.
        webography_text: Webography content (Références webdesign de Sullivan.md).
        output_path: Where to write the HTML file.

    Returns:
        Generated HTML string.
    """
    from ...models.gemini_client import GeminiClient

    prompt = (
        "Page vierge. Contexte: "
        + json.dumps({"design_structure": design_structure, "frontend_structure": frontend_structure})
        + ". Webographie: "
        + webography_text
        + ". Instruction: Générez un document HTML/CSS/JS complet single-file brutalist."
    )
    if len(prompt) > 12000:
        prompt = prompt[:12000]

    client = GeminiClient(execution_mode="BUILD")
    result = await client.generate(
        prompt,
        context=None,
        output_constraint="Code only",
        max_tokens=16384,
    )

    if not result.success or not result.code:
        raise RuntimeError(result.error or "Gemini generation failed")

    html = _extract_html(result.code)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    logger.info(f"HTML written: {output_path}")
    return html

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