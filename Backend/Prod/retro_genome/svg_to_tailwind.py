"""
SVG to Tailwind Converter — Protocole SVG AI v1.0 (Mission 118)

Convertit les exports SVG (Illustrator, Figma, etc.) en HTML5+Tailwind sémantique.
Implémente le filtrage de bruit et l'inférence structurelle pour LLM.
"""
import re
import json
from typing import Dict, List, Optional
from collections import Counter
from loguru import logger


class SvgToTailwindConverter:
    """
    Protocole SVG AI v1.0 — Pont direct SVG -> Tailwind.
    """

    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            # Importation tardive pour éviter les cycles
            from Backend.Prod.models.gemini_client import GeminiClient
            # On utilise le mode BUILD pour une meilleure qualité de génération
            self._client = GeminiClient(execution_mode="BUILD")
        return self._client

    def _strip_noise(self, svg_content: str) -> str:
        """1. Filtrage du bruit : strip <font>, <glyph>, <image> base64."""
        content = re.sub(r'<font[\s\S]*?</font>', '', svg_content, flags=re.IGNORECASE)
        content = re.sub(r'<glyph[\s\S]*?</glyph>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'<metadata[\s\S]*?</metadata>', '', content, flags=re.IGNORECASE)
        # Supprimer les images base64 qui saturent le contexte
        content = re.sub(r'<image[^>]*/>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'<image[\s\S]*?</image>', '', content, flags=re.IGNORECASE)
        # Supprimer les patterns complexes
        content = re.sub(r'<pattern[\s\S]*?</pattern>', '', content, flags=re.IGNORECASE)
        # Supprimer les commentaires
        content = re.sub(r'<!--[\s\S]*?-->', '', content)
        return content.strip()

    def _decode_stx(self, svg_content: str) -> Dict[str, str]:
        """2. Décodage .stX : mapper les classes CSS vers les tokens HoméOS (simulation)."""
        # Dans Illustrator, les styles sont souvent dans une balise <style>
        styles = {}
        style_match = re.search(r'<style[^>]*>([\s\S]*?)</style>', svg_content)
        if style_match:
            # Extraction basique des classes .st0, .st1...
            for m in re.finditer(r'\.(st\d+)\{([^}]+)\}', style_match[1]):
                styles[m.group(1)] = m.group(2).strip()
        return styles

    async def convert(self, svg_content: str, import_name: str) -> str:
        """
        Traduit la structure SVG en HTML sémantique Tailwind.
        """
        logger.info(f"[SvgToTailwind] Converting '{import_name}'...")
        
        # 1. Nettoyage
        clean_svg = self._strip_noise(svg_content)
        
        # 2. Styles
        styles = self._decode_stx(clean_svg)
        
        # 3. Analyse des couleurs pour le prompt (Inférence)
        colors = re.findall(r'fill="(#[0-9a-fA-F]{3,6})"', clean_svg)
        color_freq = Counter(colors).most_common(5)
        color_hint = ", ".join([f"{c} ({count}x)" for c, count in color_freq])

        # 4. Prompt LLM
        prompt = f"""Tu es un Expert Intégrateur Frontend AetherFlow.
MISSION : Traduis cette structure SVG (export Illustrator/Figma) en HTML sémantique avec Tailwind CSS.

NOM DE L'IMPORT : {import_name}

STRUCTURE SVG (FILTRÉE) :
{clean_svg[:50000]} 

TOKENS DE DESIGN HOMÉOS (OBLIGATOIRE) :
- Background principal : `#f7f6f2`
- Texte principal : `#3d3d3c`
- Couleur d'accent (boutons, liens actifs) : `#8cc63f`
- Typographie : Geist Sans (via Google Fonts ou CDN)
- Style : Minimaliste, précis, lowercase pour les labels secondaires.

CONTRAINTES TECHNIQUES :
- Utilise UNIQUEMENT Tailwind CSS (via CDN).
- INTERDIT : largeurs fixes en px (width: 200px). Utilise Flexbox et Grid (w-full, flex-1, grid-cols-...).
- Sémantique : Utilise <header>, <main>, <nav>, <footer>, <section>.
- Évite le lorem ipsum : si tu vois des textes ou des ID de groupes dans le SVG, utilise-les pour inférer le contenu réel.
- Résultat attendu : Un document HTML5 complet et autonome (<!DOCTYPE html>).

Réponds UNIQUEMENT avec le code HTML complet. Pas de prose, pas de markdown.
"""

        result = await self.client.generate(
            prompt=prompt,
            max_tokens=16000,
            temperature=0.1,
            output_constraint="No prose"
        )

        if not result.success:
            logger.error(f"[SvgToTailwind] LLM Error: {result.error}")
            raise RuntimeError(f"Conversion failed: {result.error}")

        # Nettoyage du bloc de code si le LLM a mis des backticks malgré tout
        code = result.code
        if "```html" in code:
            code = code.split("```html")[1].split("```")[0]
        elif "```" in code:
            code = code.split("```")[1].split("```")[0]
            
        return code.strip()
