"""
VisualDecomposer (analyzer.py) — Retro-Genome Pipeline (Mission 35)
Analyse libre d'une maquette PNG : description ouverte sans taxonomie imposée.
Gère 1 ou plusieurs images.
"""
import asyncio
import io
import base64
import json
import re
from pathlib import Path
from typing import Tuple, Dict, List
from loguru import logger
from dotenv import load_dotenv


def extract_json_robust(text: str) -> Dict:
    """Extrait un objet JSON depuis une réponse Gemini, même enrobée de markdown ou prose."""
    # 0. Nettoyage des balises <think>
    if '<think>' in text:
        text = re.sub(r'<think>[\s\S]*?</think>', '', text).strip()

    # 1. Chercher un bloc markdown ```json ... ``` ou ``` ... ```
    code_block = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if code_block:
        try:
            return json.loads(code_block.group(1).strip())
        except Exception:
            pass

    # 2. Chercher la structure la plus large entre le premier '{' et le dernier '}'
    first = text.find('{')
    last = text.rfind('}')
    if first != -1 and last != -1 and last > first:
        try:
            return json.loads(text[first:last+1])
        except Exception:
            pass

    # 3. Ultime recours
    try:
        return json.loads(text.strip())
    except Exception:
        pass

    raise ValueError(f"Impossible d'extraire un JSON valide depuis : {text[:200]}")


project_root = Path(__file__).parent.parent.parent.parent
load_dotenv(project_root / "Backend/.env")

MAX_DIMENSION = 1280   # px (was 1024)

VISUAL_DECOMPOSER_PROMPT = """Tu es un expert en Analyse Visuelle d'Interfaces et en Architecture Logicielle.
Ta mission est de décrire LIBREMENT ce que tu observes dans cette maquette d'interface, tout en identifiant sa structure géométrique et son archétype fonctionnel.

NE PROJETTE AUCUNE CATÉGORIE PRÉDÉFINIE, mais sois attentif aux signatures visuelles fortes.

POUR CHAQUE ÉLÉMENT VISIBLE :
1. Donne-lui un identifiant unique (slug court)
2. Décris sa forme, sa couleur, et sa position
3. **visual_hint** (OBLIGATOIRE) : Choisis la valeur la plus proche parmi : `tree-view`, `code-editor`, `data-table`, `circle-overlap`, `grid-matrix`, `pyramid-row`, `node-edge`, `tabs`, `form-input`, `card`, `chart`, `map`, `button`, `status-badge`.
4. **color_hex** (OBLIGATOIRE) : Code hexadécimal exact (ex: #4A90D9).
5. **apparent_role** : Rôle supposé.
6. **coords** (SI GÉOMÉTRIQUE) : 
   - Pour les grilles/matrices : `{ "row": n, "col": m }`
   - Pour les cercles/formes courbes : `{ "cx": x, "cy": y, "r": r }`
7. **parents** (SI CALCULÉ) : Si l'élément est une zone d'intersection entre deux formes, liste leurs IDs : `["id1", "id2"]`. Donne à cet élément le `visual_hint: "computed-intersection"`.

ZONES ET STRUCTURE :
- Identifie les régions structurantes (`regions`). Une **sidebar** (latérale) DOIT être isolée comme région distincte.
- Note les couleurs dominantes dans `design_tokens` au format HEX uniquement.

RÉPONDS UNIQUEMENT AVEC UN OBJET JSON VALIDE.

JSON SCHEMA :
{
  "elements": [
    {
      "id": "slug",
      "description": "string",
      "position": "string",
      "color": "string",
      "color_hex": "#RRGGBB",
      "text_content": "string or null",
      "apparent_role": "string",
      "visual_hint": "slug",
      "coords": { "row": 0, "col": 0 } or { "cx": 0, "cy": 0, "r": 0 } or null,
      "parents": ["id1", "id2"] or null
    }
  ],
  "regions": [
    {
      "id": "slug",
      "name": "string",
      "elements_contained": ["id1"],
      "structural_role": "string"
    }
  ],
  "design_tokens": {
    "primary_colors": ["#hex1", "#hex2"],
    "background_color": "#hex",
    "typography_apparent": "string"
  },
  "annotations_visible": ["string"]
}"""


class ImagePreprocessor:
    def __init__(self, max_dimension=MAX_DIMENSION):
        self.max_dimension = max_dimension

    def process(self, image_path: Path) -> Tuple[str, str]:
        try:
            from PIL import Image
        except ImportError:
            raise RuntimeError("Pillow not installed: pip install pillow")

        with Image.open(image_path) as img:
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")

            w, h = img.size
            if max(w, h) > self.max_dimension:
                ratio = self.max_dimension / max(w, h)
                img = img.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)

            buffer = io.BytesIO()
            img.save(buffer, format="PNG", optimize=True)
            data = buffer.getvalue()

        return base64.b64encode(data).decode("utf-8"), "image/png"


from Backend.Prod.models.gemini_client import GeminiClient


class RetroGenomeAnalyzer:
    """VisualDecomposer — Analyse visuelle libre d'une ou plusieurs maquettes PNG."""

    def __init__(self):
        self.client = GeminiClient(execution_mode="FAST")
        self.preprocessor = ImagePreprocessor()

    async def analyze_png(self, image_path: Path) -> Dict:
        """Analyse un seul PNG et retourne un JSON de décomposition visuelle libre.
        Retry x2 sur réponse vide ou JSON invalide, temperature=0 pour la cohérence.
        """
        logger.info(f"🔍 VisualDecomposer: Analyzing {image_path.name}...")

        b64_image, mime_type = self.preprocessor.process(image_path)

        max_attempts = 3
        last_error = None

        for attempt in range(max_attempts):
            try:
                logger.info(f"[VisualDecomposer] Attempt {attempt + 1}/{max_attempts}")

                result = await self.client.generate_with_image(
                    prompt=VISUAL_DECOMPOSER_PROMPT,
                    image_base64=b64_image,
                    mime_type=mime_type,
                    output_constraint="JSON only",
                    max_tokens=4096,
                    temperature=0
                )

                if not result.success:
                    raise ValueError(result.error)

                raw = result.code if result.code and result.code.strip() else getattr(result, 'text', '') or ''
                if not raw:
                    raise ValueError("Réponse vide de Gemini")

                logger.debug(f"[VisualDecomposer] Raw response (first 300): {raw[:300]}")
                return extract_json_robust(raw)

            except Exception as e:
                last_error = e
                logger.warning(f"[VisualDecomposer] Attempt {attempt + 1} failed: {e}")
                if attempt < max_attempts - 1:
                    await asyncio.sleep(1)

        logger.error(f"[VisualDecomposer] All {max_attempts} attempts failed for {image_path.name}: {last_error}")
        await self.client.close()
        return {"error": str(last_error), "elements": [], "regions": [], "design_tokens": {}, "annotations_visible": []}

    async def analyze_multiple(self, image_paths: List[Path]) -> Dict:
        """
        Analyse plusieurs PNGs séquentiellement et synthétise les résultats.
        Chaque appel recrée le client pour éviter les conflits de session.
        """
        logger.info(f"🔍 VisualDecomposer: Analyzing {len(image_paths)} images...")
        results = []
        for path in image_paths:
            self.client = GeminiClient(execution_mode="FAST")
            res = await self.analyze_png(path)
            results.append({"source": path.name, "analysis": res})

        return {"multi_template_analysis": results}
