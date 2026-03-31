import math
import os
import json
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from typing import Dict, Any, Optional, List, Tuple


class FontClassifier:
    """
    Sullivan Typography Engine — Phase A
    Classifie les polices via signaux morphologiques (Panose + contours Bézier sur 'o').
    Les valeurs vox_atypi correspondent aux `id` de typography_db.json.
    """

    # panose[1] (SerifStyle) → id Vox-ATypI (clé de typography_db.json)
    SERIF_TO_VOX: Dict[int, str] = {
        2:  "humanes",
        3:  "garaldes",
        4:  "reales",
        5:  "reales",
        6:  "mecanes",
        7:  "didones",
        8:  "didones",
        9:  "didones",
        10: "incises",
        11: "lineales",
        12: "lineales",
        13: "lineales",
        14: "incises",
        15: "lineales",
    }

    # panose[6] (ArmStyle) → sous-famille Linéales
    HUMANISTE_ARMS:  frozenset = frozenset({7, 8, 9, 10, 11, 12, 13, 14})
    GROTESQUE_ARMS:  frozenset = frozenset({2, 3, 4, 5, 6})

    def classify(self, font_path: str) -> Dict[str, Any]:
        """Analyse complète — retourne le schéma Vox-ATypI + signaux."""
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"Font file not found: {font_path}")

        font     = TTFont(font_path)
        panose   = self._extract_panose(font)
        family_t = panose[0]
        serif_s  = panose[1]
        contrast = panose[4]
        arm_s    = panose[6]

        # --- 1. Famille primaire ---
        if   family_t == 5: vox = "symboles"
        elif family_t == 3: vox = "scriptes"
        elif family_t == 4: vox = "fractures"
        else:
            vox = self.SERIF_TO_VOX.get(serif_s, "inconnue")
            # contraste élevé non détecté → forcer Didones
            if contrast >= 8 and vox in ("inconnue", "reales", "humanes"):
                vox = "didones"
            # sans-serif non détecté → Linéales
            if vox == "inconnue" and serif_s >= 11:
                vox = "lineales"

        # --- 2. Sous-famille Linéales ---
        sub_family: Optional[str] = None
        if vox == "lineales":
            sub_family = self._lineale_sub_family(font, arm_s)

        # --- 3. Signaux morphologiques (Bézier sur 'o') ---
        morpho = self._analyze_morphology(font)

        # --- 4. Métadonnées ---
        name        = font["name"]
        family_name = name.getDebugName(1) or "Unnamed"
        style       = name.getDebugName(2) or "Regular"

        is_variable = "fvar" in font
        weights: List = []
        if is_variable:
            for axis in font["fvar"].axes:
                if axis.axisTag == "wght":
                    weights = [axis.minValue, axis.maxValue]
        elif "OS/2" in font:
            weights = [font["OS/2"].usWeightClass]

        return {
            "family_name":      family_name,
            "style":            style,
            "vox_atypi":        vox,
            "sub_family":       sub_family,
            "is_variable":      is_variable,
            "weights_available": weights,
            "signals": {
                "panose_raw":       list(panose),
                "stress_angle_deg": morpho["stress_angle"],
                "contrast_ratio":   morpho["contrast_ratio"],
                "serif_raw":        serif_s,
                "arm_style_raw":    arm_s,
            },
        }

    # ------------------------------------------------------------------
    # Panose
    # ------------------------------------------------------------------

    def _extract_panose(self, font: TTFont) -> list:
        if "OS/2" in font:
            p = font["OS/2"].panose
            return [
                p.bFamilyType, p.bSerifStyle, p.bWeight, p.bProportion,
                p.bContrast, p.bStrokeVariation, p.bArmStyle,
                p.bLetterForm, p.bMidline, p.bXHeight,
            ]
        return [0] * 10

    # ------------------------------------------------------------------
    # Linéales sub-family
    # ------------------------------------------------------------------

    def _lineale_sub_family(self, font: TTFont, arm_style: int) -> str:
        """Grotesque / geometrique / humaniste — mots-clés puis Panose arm style."""
        name   = font["name"]
        label  = ((name.getDebugName(4) or "") + " " + (name.getDebugName(1) or "")).lower()

        if any(k in label for k in ("humanist", "humaniste", "gill", "frutiger",
                                     "myriad", "geist", "inter ", "source sans")):
            return "humaniste"
        if any(k in label for k in ("geometric", "géométrique", "futura", "avenir",
                                     "circular", "montserrat")):
            return "geometrique"
        if any(k in label for k in ("grotesque", "grotesk", "helvetica",
                                     "akzidenz", "gothic", "univers")):
            return "grotesque"

        # Fallback Panose
        if arm_style in self.HUMANISTE_ARMS:  return "humaniste"
        if arm_style in self.GROTESQUE_ARMS:  return "grotesque"
        return "grotesque"

    # ------------------------------------------------------------------
    # Analyse morphologique Bézier
    # ------------------------------------------------------------------

    def _analyze_morphology(self, font: TTFont) -> Dict[str, float]:
        """
        Calcule stress_angle et contrast_ratio depuis les contours du glyphe 'o'.
        Méthode : outer + inner (counter) → distances locales outer→inner.
        - thinnest distance = délié → position angulaire = axe de stress
        - contrast_ratio = thickest / thinnest
        Fallback sur post.italicAngle + heuristique Panose.
        """
        result = {"stress_angle": 0.0, "contrast_ratio": 1.0}
        try:
            cmap = font.getBestCmap()
            if not cmap or ord("o") not in cmap:
                result["stress_angle"] = self._fallback_angle(font)
                return result

            contours = self._extract_contours(font, cmap[ord("o")])
            if len(contours) < 2:
                result["stress_angle"] = self._fallback_angle(font)
                return result

            def bbox_area(pts: list) -> float:
                xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
                return (max(xs) - min(xs)) * (max(ys) - min(ys)) if xs else 0.0

            contours.sort(key=bbox_area, reverse=True)
            outer, inner = contours[0], contours[1]

            # Centre approximatif du glyphe (bbox outer)
            xs = [p[0] for p in outer]; ys = [p[1] for p in outer]
            cx = (min(xs) + max(xs)) / 2
            cy = (min(ys) + max(ys)) / 2

            # Échantillonnage ~40 pts par contour
            def sample(pts: list, n: int = 40) -> list:
                step = max(1, len(pts) // n)
                return pts[::step]

            s_outer = sample(outer)
            s_inner = sample(inner)

            # Pour chaque point outer : distance min vers inner + angle depuis centre
            records: List[Tuple[float, float]] = []  # (distance, angle_deg)
            for po in s_outer:
                d = min(math.hypot(po[0] - pi[0], po[1] - pi[1]) for pi in s_inner)
                ang = math.degrees(math.atan2(po[1] - cy, po[0] - cx)) % 360
                records.append((d, ang))

            if not records:
                result["stress_angle"] = self._fallback_angle(font)
                return result

            thinnest = min(records, key=lambda r: r[0])
            thickest = max(records, key=lambda r: r[0])

            # Angle de stress = direction du délié, normalisé 0–90°
            raw = thinnest[1] % 90
            result["stress_angle"]  = round(raw if raw <= 45 else 90 - raw, 2)
            result["contrast_ratio"] = round(
                thickest[0] / thinnest[0] if thinnest[0] > 0 else 1.0, 3
            )

        except Exception:
            result["stress_angle"] = self._fallback_angle(font)

        return result

    def _extract_contours(self, font: TTFont, glyph_name: str) -> List[List[Tuple]]:
        """Extrait les contours d'un glyphe en liste de points (x, y)."""
        # TTF
        if "glyf" in font:
            g = font["glyf"][glyph_name]
            if not hasattr(g, "numberOfContours") or g.numberOfContours <= 0:
                return []
            coords, _, endPts = g.getCoordinates(font["glyf"])
            out, start = [], 0
            for end in endPts:
                out.append([(int(coords[i][0]), int(coords[i][1]))
                             for i in range(start, end + 1)])
                start = end + 1
            return out

        # CFF / OTF
        if "CFF " in font or "CFF2" in font:
            gs = font.getGlyphSet()
            if glyph_name not in gs:
                return []
            pen = RecordingPen()
            gs[glyph_name].draw(pen)
            out, cur = [], []
            for op, args in pen.value:
                if op == "moveTo":
                    if cur: out.append(cur)
                    cur = [args[0]]
                elif op in ("lineTo", "curveTo", "qCurveTo"):
                    cur.append(args[-1])
                elif op in ("endPath", "closePath"):
                    if cur: out.append(cur)
                    cur = []
            if cur: out.append(cur)
            return out

        return []

    def _fallback_angle(self, font: TTFont) -> float:
        """Fallback stress angle via post.italicAngle, puis heuristique Panose."""
        if "post" in font:
            a = abs(float(getattr(font["post"], "italicAngle", 0.0)))
            if a != 0.0:
                return round(a, 2)
        p = self._extract_panose(font)
        return 15.0 if len(p) > 1 and p[1] in (2, 3) else 0.0


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(json.dumps(FontClassifier().classify(sys.argv[1]),
                         indent=2, ensure_ascii=False))
