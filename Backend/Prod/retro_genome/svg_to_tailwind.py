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
        self._default_tokens = {
            "colors": {"primary": "#8cc63f", "neutral": "#f7f6f2", "text": "#3d3d3c"},
            "typography": {"body": "Geist Sans"},
            "shape": {"border_radius": "6px"}
        }

    @property
    def client(self):
        if self._client is None:
            # Importation tardive pour éviter les cycles
            from Backend.Prod.models.gemini_client import GeminiClient
            # On utilise le mode BUILD pour une meilleure qualité de génération
            self._client = GeminiClient(execution_mode="BUILD")
        return self._client

    def _load_project_tokens(self) -> dict:
        """Charge les tokens du projet actif s'ils existent."""
        try:
            from bkd_service import get_active_project_path
            token_path = get_active_project_path() / "exports" / "design_tokens.json"
            if token_path.exists():
                return json.loads(token_path.read_text())
        except Exception as e:
            logger.warning(f"[SvgToTailwind] Failed to load project tokens: {e}")
        return self._default_tokens

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

        # 4. Chargement des tokens dynamiques (Mission 128)
        tokens = self._load_project_tokens()

        # 5. Prompt LLM
        prompt = f"""Tu es un Expert Intégrateur Frontend AetherFlow spécialisé en conversion Design-to-Code.
MISSION : Traduis cette structure SVG (export Illustrator/Figma) en HTML sémantique avec Tailwind CSS.

NOM DE L'IMPORT : {import_name}

STRUCTURE SVG (FILTRÉE) :
{clean_svg[:50000]} 

TOKENS DE DESIGN À RESPECTER (IMPÉRATIF) :
- Background principal : `{tokens['colors']['neutral']}`
- Texte principal : `{tokens['colors']['text']}`
- Couleur d'accent (boutons, liens actifs) : `{tokens['colors']['primary']}`
- Typographie : {tokens['typography']['body']} (via Google Fonts ou CDN)
- Border-radius : {tokens['shape'].get('border_radius', '6px')}
- Style : Fidèle au design system spécifié ci-dessus.

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
            logger.warning("[SvgToTailwind] Gemini failed, trying Mimo fallback...")
            try:
                from Backend.Prod.models.mimo_client import MimoClient
                mimo = MimoClient()
                result = await mimo.generate(prompt=prompt, max_tokens=16000, temperature=0.1)
            except Exception as e:
                logger.error(f"[SvgToTailwind] Mimo fallback also failed: {e}")

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

    async def convert_image(self, image_base64: str, mime_type: str, import_name: str, design_md: str = "") -> str:
        """
        Traduit une capture d'écran PNG/JPG en HTML sémantique Tailwind via Vision.
        """
        logger.info(f"[SvgToTailwind] Converting image '{import_name}'...")

        # Chargement des tokens dynamiques (Mission 128)
        tokens = self._load_project_tokens()

        # M256-C: DESIGN.md du projet (si fourni, override les tokens par défaut)
        design_section = ""
        if design_md:
            design_section = f"""
DESIGN SYSTEM DU PROJET (IMPÉRATIF — respecte fidèlement ce document) :
{design_md[:3000]}
"""
        else:
            design_section = f"""
TOKENS DE DESIGN À RESPECTER (IMPÉRATIF) :
- Background principal : `{tokens['colors']['neutral']}`
- Texte principal : `{tokens['colors']['text']}`
- Couleur d'accent (boutons, liens actifs) : `{tokens['colors']['primary']}`
- Typographie : {tokens['typography']['body']} (via Google Fonts ou CDN)
- Border-radius : {tokens['shape'].get('border_radius', '6px')}
"""

        prompt = f"""Tu es un Expert Intégrateur Frontend AetherFlow spécialisé en Vision-to-Code.
MISSION : Analyse cette capture d'écran et convertis-la en HTML sémantique avec Tailwind CSS.

NOM DE L'IMPORT : {import_name}
{design_section}
CONTRAINTES TECHNIQUES :
- Utilise UNIQUEMENT Tailwind CSS (via CDN).
- INTERDIT : largeurs fixes en px. Utilise Flexbox et Grid (w-full, flex-1, grid-cols-...).
- Sémantique : Utilise <header>, <main>, <nav>, <footer>, <section>.
- Évite le lorem ipsum : lis les textes réels sur l'image et utilise-les.
- Résultat attendu : Un document HTML5 complet et autonome (<!DOCTYPE html>).

Réponds UNIQUEMENT avec le code HTML complet. Pas de prose, pas de markdown.
"""

        result = await self.client.generate_with_image(
            prompt=prompt,
            image_base64=image_base64,
            mime_type=mime_type,
            max_tokens=16000,
            temperature=0.1
        )

        if not result.success:
            logger.warning("[SvgToTailwind] Gemini Vision failed, trying Mimo fallback...")
            try:
                from Backend.Prod.models.mimo_client import MimoClient
                mimo = MimoClient()
                result = await mimo.generate_with_image(
                    prompt=prompt, image_base64=image_base64, 
                    mime_type=mime_type, max_tokens=16000, temperature=0.1
                )
            except Exception as e:
                logger.error(f"[SvgToTailwind] Mimo fallback vision failed: {e}")

        if not result.success:
            logger.error(f"[SvgToTailwind] LLM Vision Error: {result.error}")
            raise RuntimeError(f"Vision conversion failed: {result.error}")

        code = result.code
        if "```html" in code:
            code = code.split("```html")[1].split("```")[0]
        elif "```" in code:
            code = code.split("```")[1].split("```")[0]

        return code.strip()

    async def analyze_image_design(self, image_base64: str, mime_type: str, import_name: str) -> str:
        """
        M256-A: Analyse l'image PNG → extrait les choix de design → retourne DESIGN.md.
        """
        logger.info(f"[SvgToTailwind] Analyzing image design: '{import_name}'...")

        prompt = f"""Tu es un Expert Designer UI/UX et Directeur Artistique.
MISSION : Analyse cette capture d'écran et extrais les choix de design pour générer un fichier DESIGN.md.

NOM DE L'IMPORT : {import_name}

ANALYSE REQUISE :
1. PALETTE DE COULEURS — chaque couleur dominante avec son usage (bg, text, accent, border, etc.)
2. TYPOGRAPHIE — famille apparente, tailles, graisses, hiérarchie
3. ESPACEMENT — padding/margin patterns, gutters, gaps
4. FORMES — border-radius, ombres, bordures
5. LAYOUT — structure générale (sidebar? grid? flex?), zones principales
6. COMPOSANTS — boutons, cards, navbars, inputs — leur style récurrent
7. TONALITÉ — minimaliste? corporate? playful? sombre? clair?

FORMAT DE SORTIE (DESIGN.md) — réponds UNIQUEMENT avec ce contenu, pas de prose :
```markdown
# DESIGN.md — {import_name}

## Colors
- primary: #XXXXXX (boutons, accents)
- neutral: #XXXXXX (backgrounds)
- text: #XXXXXX (typographie)
- border: #XXXXXX (borders)
- muted: #XXXXXX (secondary text)

## Typography
- body: "font-family" (size, weight)
- heading: "font-family" (size, weight)

## Spacing
- unit: 8px (or observed unit)
- padding-sm: Xpx
- padding-md: Ypx
- padding-lg: Zpx

## Shapes
- border-radius: Xpx
- shadow: description

## Layout
- structure: description

## Components
- button: description style
- card: description style
- nav: description style

## Tone
- description de la tonalité visuelle
```
"""
        result = await self.client.generate_with_image(
            prompt=prompt,
            image_base64=image_base64,
            mime_type=mime_type,
            max_tokens=8000,
            temperature=0.3
        )

        if not result.success:
            logger.warning(f"[SvgToTailwind] Design analysis failed: {result.error}")
            return ""

        design_md = result.code
        if "```markdown" in design_md:
            design_md = design_md.split("```markdown")[1].split("```")[0]
        elif "```" in design_md:
            design_md = design_md.split("```")[1].split("```")[0]
        design_md = design_md.strip()

        # Save DESIGN.md (direct path — avoid bkd_service import)
        try:
            active_file = Path("/Users/francois-jeandazin/AETHERFLOW/active_project.json")
            if active_file.exists():
                import json as _json
                active_data = _json.loads(active_file.read_text(encoding='utf-8'))
                project_id = active_data.get("active_id")
                if project_id:
                    project_path = Path("/Users/francois-jeandazin/AETHERFLOW/projects") / project_id
                    design_file = project_path / "DESIGN.md"
                    design_file.write_text(design_md, encoding='utf-8')
                    logger.info(f"[SvgToTailwind] DESIGN.md saved: {design_file}")
        except Exception as e:
            logger.warning(f"[SvgToTailwind] Failed to save DESIGN.md: {e}")

        return design_md
