import asyncio
import base64
import json
import re
from typing import Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DesignPrinciplesExtractor:
    """
    A class used to extract design principles from an image.

    Attributes:
    ----------
    agent_router : AgentRouter
        The agent router used to select the agent.
    gemini_client : GeminiClient
        The Gemini client used to generate design principles.

    Methods:
    -------
    extract_principles(image_path: Path, design_structure: Optional[Dict] = None) -> Dict:
        Extracts design principles from an image.
    save_principles(principles: Dict, output_path: Path) -> None:
        Saves the design principles to a JSON file.
    """

    def __init__(self, agent_router: 'AgentRouter', gemini_client: 'GeminiClient'):
        """
        Initializes the DesignPrinciplesExtractor.

        Args:
        ----
        agent_router : AgentRouter
            The agent router used to select the agent.
        gemini_client : GeminiClient
            The Gemini client used to generate design principles.
        """
        self.agent_router = agent_router
        self.gemini_client = gemini_client

    async def extract_principles(self, image_path: Path, design_structure: Optional[Dict] = None) -> Dict:
        """
        Extracts design principles from an image.

        Args:
        ----
        image_path : Path
            The path to the image.
        design_structure : Optional[Dict]
            The design structure. Defaults to None.

        Returns:
        -------
        Dict
            A dictionary containing the design principles.
        """
        try:
            # Generate the prompt
            prompt = f"À partir de cette maquette (et optionnellement de la structure design fournie), liste les principes graphiques réutilisables."
            if design_structure:
                prompt += f" Structure design: {json.dumps(design_structure)}"

            # Pré-traiter l'image pour Gemini (resize/compress si trop grosse)
            try:
                from ..upload import preprocess_for_gemini
                image_bytes, mime_type = preprocess_for_gemini(image_path)
            except ImportError:
                with open(image_path, "rb") as f:
                    image_bytes = f.read()
                suffix = (image_path.suffix or "").lower()
                mime_type = "image/png" if suffix in (".png",) else "image/jpeg" if suffix in (".jpg", ".jpeg") else "image/png"
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")

            # Generate the design principles using Gemini Vision
            result = await self.gemini_client.generate_with_image(
                prompt, image_base64, mime_type=mime_type
            )
            if not result.success:
                raise RuntimeError(result.error or "Gemini vision call failed")

            # Parse the response to extract the JSON
            json_response = self._parse_json_response(result.code)
            return json_response

        except Exception as e:
            logger.error("Error extracting design principles: %s", e)
            raise

    def _parse_json_response(self, response: str) -> Dict:
        """
        Parses the response to extract the JSON.

        Args:
        ----
        response : str
            The response from Gemini Vision (or GenerationResult.code).

        Returns:
        -------
        Dict
            A dictionary containing the design principles.
        """
        text = (response or "").strip()
        # Remove markdown code block if present
        if "```" in text:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
            if match:
                text = match.group(1).strip()
        # Try to find a JSON object
        start = text.find("{")
        if start != -1:
            depth = 0
            for i in range(start, len(text)):
                if text[i] == "{":
                    depth += 1
                elif text[i] == "}":
                    depth -= 1
                    if depth == 0:
                        text = text[start : i + 1]
                        break
        try:
            return json.loads(text) if text else {}
        except json.JSONDecodeError:
            return {"raw": text, "principles": []}

    def save_principles(self, principles: Dict, output_path: Path) -> None:
        """
        Saves the design principles to a JSON file.

        Args:
        ----
        principles : Dict
            The design principles dictionary.
        output_path : Path
            The path to the output JSON file.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(principles, f, indent=2, ensure_ascii=False)
        logger.info("Design principles saved to %s", output_path)