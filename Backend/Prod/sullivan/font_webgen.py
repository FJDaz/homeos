"""
Sullivan Typography Engine — Phase B
Web Font Generator: Subset + WOFF2 + @font-face CSS

Workflow:
    Upload TTF/OTF/WOFF/WOFF2
        ↓ fonttools: normalisation
        ↓ Subsetting: Latin Extended (U+0020–U+024F) + ponctuation typo
        ↓ Export WOFF2 (Brotli) + WOFF fallback
        ↓ Storage: /static/fonts/{slug}/{slug}-{weight}{style}.woff2
        ↓ Génération @font-face CSS
"""

import os
import re
import shutil
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter


# --- Configuration ---

# Subset cible: latin professionnel + ponctuation typographique
LATIN_SUBSET_RANGES = [
    # Basic Latin
    (0x0020, 0x007E),
    # Latin-1 Supplement
    (0x00A0, 0x00FF),
    # Latin Extended-A
    (0x0100, 0x017E),
    # Latin Extended-B (partial)
    (0x0180, 0x024F),
]

# Ponctuation typographique
TYPO_PUNCTUATION = [
    0x2013,  # en-dash
    0x2014,  # em-dash
    0x2018,  # left single quotation mark
    0x2019,  # right single quotation mark
    0x201C,  # left double quotation mark
    0x201D,  # right double quotation mark
    0x00AB,  # guillemet gauche
    0x00BB,  # guillemet droit
    0x2026,  # horizontal ellipsis
    0x00B7,  # middle dot
    0x2010,  # hyphen
    0x2011,  # non-breaking hyphen
    0x2012,  # figure dash
    0x202F,  # narrow no-break space
    0x2009,  # thin space
    0x200A,  # hair space
    0x200B,  # zero-width space
]

# Fontes commerciales connues (alerte licensing)
COMMERCIAL_FONTS = frozenset({
    "söhne", "graphik", "canela", "financier", "tiempos",
    "gt walsheim", "neue haas grotesk", "acumin", "freight",
    "aktiv grotesk", "whitney", "gotham", "proxima nova",
    "museo", "klavika", "futura pt", "din next", "aachen"
})


class FontWebGen:
    """Générateur de webfonts: subset, WOFF2, @font-face CSS."""

    def __init__(self, output_dir: str = None):
        """
        Args:
            output_dir: Répertoire de sortie (défaut: /static/fonts)
        """
        self.output_dir = Path(output_dir) if output_dir else None
        if self.output_dir is None:
            # Default to project static/fonts
            self.output_dir = Path(__file__).parent.parent.parent.parent / "Frontend/3. STENCILER/static/fonts"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, font_path: str, classification: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Génère les webfonts optimisées depuis une fonte source.

        Args:
            font_path: Chemin vers le fichier TTF/OTF/WOFF/WOFF2
            classification: Résultat de FontClassifier.classify() (optionnel)

        Returns:
            {
                "slug": "cormorant",
                "font_family": "Cormorant",
                "css": "@font-face { ... }",
                "files": [...],
                "total_size": 12345,
                "licensing_warning": "Cormorant est une fonte commerciale..."
            }
        """
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"Font file not found: {font_path}")

        font = TTFont(font_path)

        # Slugify family name
        family_name = classification.get("family_name", "Unknown") if classification else "Unknown"
        slug = self._slugify(family_name)

        # Créer répertoire spécifique à la fonte
        font_dir = self.output_dir / slug
        font_dir.mkdir(parents=True, exist_ok=True)

        # Extraire poids et style
        weight = self._extract_weight(font, classification)
        style = self._extract_style(font, classification)
        is_variable = classification.get("is_variable", False) if classification else False

        # Subset + conversion
        files_generated = []
        css_rules = []

        if is_variable:
            # Variable font: un seul fichier avec axe weight
            woff2_path = font_dir / f"{slug}-variable.woff2"
            woff_path = font_dir / f"{slug}-variable.woff"

            # Subset variable font (préserver les axes)
            subsetter = Subsetter()
            subsetter.populate(glyphs=self._get_subset_glyphs(font))
            subsetter.subset(font)

            # Export WOFF2
            font.flavor = "woff2"
            font.save(woff2_path)
            files_generated.append({
                "path": str(woff2_path.relative_to(self.output_dir.parent)),
                "format": "woff2-variations",
                "weight": "100 900",
                "style": style
            })

            # Export WOFF fallback (optionnel, pour vieux browsers)
            # Note: WOFF2 est largement supporté, WOFF peut être omis
            # font.flavor = "WOFF"
            # font.save(woff_path)

            # CSS Variable Font
            css_rules.append(self._generate_variable_css(
                family=family_name,
                woff2_path=f"/static/fonts/{slug}/{woff2_path.name}",
                weight_range="100 900",
                style=style
            ))
        else:
            # Static fonts: WOFF2 + WOFF
            suffix = f"-{weight}{style}" if style != "normal" else f"-{weight}"

            # Subset
            subsetter = Subsetter()
            subsetter.populate(glyphs=self._get_subset_glyphs(font))
            subsetter.subset(font)

            # Export WOFF2
            woff2_name = f"{slug}{suffix}.woff2"
            woff2_path = font_dir / woff2_name
            font.flavor = "woff2"
            font.save(woff2_path)
            files_generated.append({
                "path": str(woff2_path.relative_to(self.output_dir.parent)),
                "format": "woff2",
                "weight": str(weight),
                "style": style
            })

            # Export WOFF fallback (optionnel, pour vieux browsers)
            # Note: WOFF2 est largement supporté (>95%), WOFF peut être omis
            # Si besoin, générer avec fonttools.woff2 ou outil externe

            # CSS @font-face
            css_rules.append(self._generate_static_css(
                family=family_name,
                woff2_path=f"/static/fonts/{slug}/{woff2_name}",
                woff_path="",  # WOFF fallback optionnel
                weight=weight,
                style=style
            ))

        # Calculer taille totale
        total_size = sum(f.stat().st_size for f in font_dir.glob("*") if f.is_file())

        # Alerte licensing
        licensing_warning = None
        if family_name.lower() in COMMERCIAL_FONTS:
            licensing_warning = f"{family_name} est une fonte commerciale. Vérifiez votre licence avant usage web."

        # Données de métadonnées pour persistence (Mission 109-C)
        meta = {
            "slug": slug,
            "font_family": family_name,
            "classification": classification,
            "css": "\n\n".join(css_rules),
            "files": files_generated,
            "total_size": total_size,
            "licensing_warning": licensing_warning,
            "created_at": datetime.now().isoformat() if "datetime" in globals() else None
        }

        # Sauvegarde persistante
        meta_path = font_dir / "metadata.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

        return meta

    def _slugify(self, text: str) -> str:
        """Normalise un nom de fonte pour usage filesystem/URL."""
        # Remplacer caractères spéciaux
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s_]+', '-', text)
        text = re.sub(r'-+', '-', text)
        return text.strip('-')

    def _extract_weight(self, font: TTFont, classification: Dict = None) -> int:
        """Extrait le poids numérique (100-900)."""
        if classification and classification.get("weights_available"):
            weights = classification["weights_available"]
            return weights[0] if len(weights) == 1 else 400

        if "OS/2" in font:
            return font["OS/2"].usWeightClass
        return 400

    def _extract_style(self, font: TTFont, classification: Dict = None) -> str:
        """Extrait le style (normal/italic/oblique)."""
        if classification:
            style = classification.get("style", "Regular").lower()
            if "italic" in style:
                return "italic"
            if "oblique" in style:
                return "oblique"
            return "normal"

        if "name" in font:
            style_name = font["name"].getDebugName(2) or ""
            if "italic" in style_name.lower():
                return "italic"
        return "normal"

    def _get_subset_glyphs(self, font: TTFont) -> set:
        """Retourne l'ensemble des glyphes à conserver."""
        glyphs = set()

        # Unicode ranges
        for start, end in LATIN_SUBSET_RANGES:
            for codepoint in range(start, end + 1):
                if codepoint in font.getBestCmap():
                    glyphs.add(font.getBestCmap()[codepoint])

        # Ponctuation typo
        for codepoint in TYPO_PUNCTUATION:
            if codepoint in font.getBestCmap():
                glyphs.add(font.getBestCmap()[codepoint])

        # Glyphes essentiels
        essential = [".notdef", ".null", "space", "uni00A0"]
        glyphs.update(essential)

        # Si la fonte a un glyphe .notdef, le garder
        if ".notdef" in font.getGlyphOrder():
            glyphs.add(".notdef")

        return glyphs

    def _generate_static_css(self, family: str, woff2_path: str, woff_path: str,
                             weight: int, style: str) -> str:
        """Génère @font-face pour fonte statique."""
        # WOFF2 only (WOFF fallback optionnel)
        return f"""@font-face {{
  font-family: '{family}';
  src: url('{woff2_path}') format('woff2');
  font-weight: {weight};
  font-style: {style};
  font-display: swap;
  unicode-range: U+0020-00FF, U+0100-017E, U+2013-2014, U+2018-2019, U+201C-201D, U+00AB-00BB;
}}"""

    def _generate_variable_css(self, family: str, woff2_path: str,
                               weight_range: str, style: str) -> str:
        """Génère @font-face pour fonte variable."""
        return f"""@font-face {{
  font-family: '{family}';
  src: url('{woff2_path}') format('woff2-variations');
  font-weight: {weight_range};
  font-style: {style};
  font-display: swap;
  unicode-range: U+0020-00FF, U+0100-017E, U+2013-2014, U+2018-2019, U+201C-201D, U+00AB-00BB;
}}"""

    def list_fonts(self) -> List[Dict[str, Any]]:
        """Liste toutes les fontes dans le répertoire output."""
        fonts = []
        if not self.output_dir.exists():
            return fonts

        for font_dir in self.output_dir.iterdir():
            if not font_dir.is_dir():
                continue

            slug = font_dir.name
            meta_path = font_dir / "metadata.json"
            
            if meta_path.exists():
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                        fonts.append(meta)
                        continue
                except Exception:
                    pass

            # Fallback if no metadata (Legacy/Manual folders)
            files = list(font_dir.glob("*.woff2")) + list(font_dir.glob("*.woff"))
            if files:
                family = slug.replace('-', ' ').title()
                is_variable = any("variable" in f.name for f in files)
                weights = set()
                for f in files:
                    match = re.search(r'-(\d{3})', f.stem)
                    if match: weights.add(int(match.group(1)))
                    elif "variable" in f.name: weights.add("variable")

                fonts.append({
                    "slug": slug,
                    "font_family": family,
                    "is_variable": is_variable,
                    "weights": sorted(list(weights)) if not any(isinstance(w, str) for w in weights) else ["variable"],
                    "files": [str(f.relative_to(self.output_dir)) for f in files],
                    "total_size": sum(f.stat().st_size for f in files)
                })

        return sorted(fonts, key=lambda x: x.get("font_family", x.get("family", "")))

    def delete_font(self, slug: str) -> bool:
        """Supprime une fonte et son répertoire."""
        font_dir = self.output_dir / slug
        if font_dir.exists() and font_dir.is_dir():
            shutil.rmtree(font_dir)
            return True
        return False


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python font_webgen.py <font.ttf> [output_dir]")
        sys.exit(1)

    font_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    gen = FontWebGen(output_dir)
    result = gen.generate(font_path)
    print(json.dumps(result, indent=2, ensure_ascii=False))
