"""
VisualDecomposer (analyzer.py) — Retro-Genome Pipeline (Mission 35)
Analyse libre d'une maquette PNG : description ouverte sans taxonomie imposée.
Gère 1 ou plusieurs images.
"""
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
    # 0. Nettoyage des balises <think> (Gemini 3.1 Pro Preview)
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
    # Cela permet d'ignorer la prose "Voici le JSON :" qui fuitait
    first = text.find('{')
    last = text.rfind('}')
    if first != -1 and last != -1 and last > first:
        try:
            return json.loads(text[first:last+1])
        except Exception:
            pass

    # 3. Ultime recours : essayer le texte brut après strip
    try:
        return json.loads(text.strip())
    except Exception:
        pass

    raise ValueError(f"Impossible d'extraire un JSON valide depuis : {text[:200]}")



project_root = Path(__file__).parent.parent.parent.parent
load_dotenv(project_root / "Backend/.env")

TARGET_MAX_BYTES = 500 * 1024   # 500 KB
MAX_DIMENSION = 1024            # px
JPEG_QUALITY = 75

VISUAL_DECOMPOSER_PROMPT = """Tu es un expert en Analyse Visuelle d'Interfaces.
Ta mission est de décrire LIBREMENT ce que tu observes dans cette maquette d'interface.

NE PROJETTE AUCUNE CATÉGORIE PRÉDÉFINIE.
Décris ce que tu vois réellement, qu'il s'agisse :
- D'une interface classique (formulaire, dashboard, navigation...)
- D'un système expérimental (grille matricielle, formes géométriques, diagramme, carte...)
- D'une annotation, d'un schéma, d'une maquette papier photographiée...

POUR CHAQUE ÉLÉMENT VISIBLE :
1. Donne-lui un identifiant unique (slug court : ex. "top_bar", "cell_3x2", "submit_btn")
2. Décris sa forme, sa couleur dominante, sa position relative dans la page
3. Décris ce qu'il semble faire ou représenter (sans certitude si ambigu)
4. Note les annotations textuelles visibles

ÉGALEMENT IDENTIFIE :
- Les zones/régions structurantes (zones de contenu, zones de navigation, zones périphériques)
- Les couleurs dominantes et la typographie apparente
- Si des annotations manuscrites ou des légendes sont visibles

Réponds UNIQUEMENT avec un objet JSON valide. Pas de markdown, pas de commentaires.

JSON SCHEMA :
{
  "elements": [
    {
      "id": "slug_unique",
      "description": "ce que c'est / ce que ça fait",
      "position": "haut, bas, gauche, droite, centre, etc.",
      "color": "couleur(s) dominante(s)",
      "text_content": "texte visible ou null",
      "apparent_role": "rôle supposé en langage libre"
    }
  ],
  "regions": [
    {
      "id": "slug",
      "name": "nom libre",
      "elements_contained": ["id1", "id2"],
      "structural_role": "rôle structurant observé"
    }
  ],
  "design_tokens": {
    "primary_colors": ["#hex1", "#hex2"],
    "background_color": "#hex",
    "typography_apparent": "description de la typo visible ou null"
  },
  "annotations_visible": ["texte d'annotation 1", "texte d'annotation 2"]
}"""


class ImagePreprocessor:
    def __init__(self, target_max_bytes=TARGET_MAX_BYTES, max_dimension=MAX_DIMENSION):
        self.target_max_bytes = target_max_bytes
        self.max_dimension = max_dimension

    def process(self, image_path: Path) -> Tuple[str, str]:
        try:
            from PIL import Image
        except ImportError:
            raise RuntimeError("Pillow not installed: pip install pillow")

        with Image.open(image_path) as img:
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            w, h = img.size
            if max(w, h) > self.max_dimension:
                ratio = self.max_dimension / max(w, h)
                img = img.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)

            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True)
            data = buffer.getvalue()

            quality = JPEG_QUALITY
            while len(data) > self.target_max_bytes and quality > 40:
                quality -= 10
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=quality, optimize=True)
                data = buffer.getvalue()

        return base64.b64encode(data).decode("utf-8"), "image/jpeg"


from Backend.Prod.models.gemini_client import GeminiClient


class RetroGenomeAnalyzer:
    """VisualDecomposer — Analyse visuelle libre d'une ou plusieurs maquettes PNG."""

    def __init__(self):
        self.client = GeminiClient(execution_mode="FAST")
        self.preprocessor = ImagePreprocessor()

    async def analyze_png(self, image_path: Path) -> Dict:
        """Analyse un seul PNG et retourne un JSON de décomposition visuelle libre."""
        logger.info(f"🔍 VisualDecomposer: Analyzing {image_path.name}...")

        b64_image, mime_type = self.preprocessor.process(image_path)

        try:
            result = await self.client.generate_with_image(
                prompt=VISUAL_DECOMPOSER_PROMPT,
                image_base64=b64_image,
                mime_type=mime_type,
                output_constraint="JSON only",
                max_tokens=4096
            )

            if not result.success:
                raise ValueError(result.error)

            # Utiliser result.text si result.code est vide (réponse non-code)
            raw = result.code if result.code and result.code.strip() else getattr(result, 'text', '') or ''
            if not raw:
                raise ValueError("Réponse vide de Gemini")

            logger.debug(f"[VisualDecomposer] Raw response (first 300): {raw[:300]}")
            return extract_json_robust(raw)
        except Exception as e:
            logger.error(f"[VisualDecomposer] Failed for {image_path.name}: {e}")
            return {"error": str(e), "elements": [], "regions": [], "design_tokens": {}, "annotations_visible": []}
        finally:
            await self.client.close()

    async def analyze_multiple(self, image_paths: List[Path]) -> Dict:
        """
        Analyse plusieurs PNGs séquentiellement et synthétise les résultats.
        Chaque appel recrée le client pour éviter les conflits de session.
        """
        logger.info(f"🔍 VisualDecomposer: Analyzing {len(image_paths)} images...")
        results = []
        for path in image_paths:
            # Recréer le client pour chaque appel (évite les problèmes de session)
            self.client = GeminiClient(execution_mode="FAST")
            res = await self.analyze_png(path)
            results.append({"source": path.name, "analysis": res})

        return {"multi_template_analysis": results}
