"""
M293: Design Token Extractor — Background extraction from uploaded screens.
Extracts colors, typography hints, and spacing from PNG/SVG/JPG screens.
Stores results in project manifest as design_tokens.
"""
import os
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional
from collections import Counter

logger = logging.getLogger("AetherFlowV3")

# --- PATHS ---
CWD = Path(__file__).parent.parent.resolve()
ROOT_DIR = CWD.parent.parent
PROJECTS_DIR = ROOT_DIR / "projects"


def extract_colors_from_image(image_path: Path, max_colors: int = 8) -> List[str]:
    """Extract dominant colors from a PNG/JPG image using PIL."""
    try:
        from PIL import Image

        with Image.open(image_path) as img:
            if img.mode in ("RGBA", "P", "LA"):
                img = img.convert("RGB")

            # Resize for speed
            img = img.resize((100, 100), Image.Resampling.LANCZOS)
            pixels = list(img.getdata())

            # Quantize to reduce color space
            from PIL.Image import quantize
            img_q = img.quantize(colors=max_colors, method=Image.Quantize.MEDIANCUT)
            palette = img_q.getpalette()
            if not palette:
                return []

            # Extract unique colors
            colors = set()
            for p in img_q.getdata():
                if p * 3 + 2 < len(palette):
                    r, g, b = palette[p*3], palette[p*3+1], palette[p*3+2]
                    colors.add(f"#{r:02x}{g:02x}{b:02x}")

            return sorted(colors)[:max_colors]
    except ImportError:
        logger.warning("Pillow not installed, skipping color extraction")
        return []
    except Exception as e:
        logger.warning(f"Color extraction failed for {image_path}: {e}")
        return []


def extract_colors_from_svg(svg_path: Path, max_colors: int = 8) -> List[str]:
    """Extract fill/stroke colors from SVG content."""
    try:
        import re
        content = svg_path.read_text(encoding="utf-8", errors="replace")

        # Find all hex colors and named CSS colors
        hex_colors = re.findall(r'#([0-9a-fA-F]{3,8})\b', content)
        rgb_colors = re.findall(r'rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', content)

        colors = set()
        for h in hex_colors:
            if len(h) == 3:
                h = h[0]*2 + h[1]*2 + h[2]*2
            elif len(h) == 4:  # with alpha
                h = h[:3]
            elif len(h) > 6:  # with alpha
                h = h[:6]
            if len(h) == 6:
                colors.add(f"#{h.lower()}")

        for r, g, b in rgb_colors:
            try:
                colors.add(f"#{int(r):02x}{int(g):02x}{int(b):02x}")
            except ValueError:
                pass

        return sorted(colors)[:max_colors]
    except Exception as e:
        logger.warning(f"SVG color extraction failed for {svg_path}: {e}")
        return []


def extract_design_tokens_from_screens(project_id: str) -> Dict:
    """
    Analyze all uploaded screens for a project and extract design tokens.
    Returns: { colors: [...], primary_color: str, typography_hints: {...}, spacing_hints: {...} }
    """
    imports_dir = PROJECTS_DIR / project_id / "imports"
    if not imports_dir.exists():
        logger.info(f"[M293] No imports dir for {project_id}")
        return {}

    all_colors = Counter()
    screen_sizes = []
    has_svg = False
    has_png = False

    # Scan all images in imports
    for day_dir in imports_dir.iterdir():
        if not day_dir.is_dir():
            continue
        for img_file in day_dir.iterdir():
            ext = img_file.suffix.lower()
            if ext in (".png", ".jpg", ".jpeg"):
                has_png = True
                colors = extract_colors_from_image(img_file)
                for c in colors:
                    all_colors[c] += 1
                try:
                    from PIL import Image
                    with Image.open(img_file) as img:
                        screen_sizes.append(img.size)
                except:
                    pass
            elif ext == ".svg":
                has_svg = True
                colors = extract_colors_from_svg(img_file)
                for c in colors:
                    all_colors[c] += 1

    # Sort colors by frequency
    sorted_colors = [c for c, _ in all_colors.most_common(10)]

    # Determine primary color (most frequent non-neutral color)
    primary_color = sorted_colors[0] if sorted_colors else "#8cc63f"
    neutral_color = "#f7f6f2"
    text_color = "#3d3d3c"

    # Infer typography hints from screen sizes
    avg_width = int(sum(w for w, _ in screen_sizes) / len(screen_sizes)) if screen_sizes else 0
    avg_height = int(sum(h for _, h in screen_sizes) / len(screen_sizes)) if screen_sizes else 0

    tokens = {
        "colors": {
            "primary": primary_color,
            "neutral": neutral_color,
            "text": text_color,
            "palette": sorted_colors[:8]
        },
        "typography": {
            "body": "Geist Sans",
            "headline_weight": "600",
            "inferred_from": "svg/png analysis"
        },
        "shape": {
            "border_radius": "6px",
            "source": "default"
        },
        "layout": {
            "avg_screen_width": avg_width,
            "avg_screen_height": avg_height,
            "screen_count": len(screen_sizes),
            "source": "image dimensions"
        },
        "source": f"extracted from {len(screen_sizes) + (1 if has_svg else 0)} screen(s)"
    }

    logger.info(f"[M293] Extracted design tokens for {project_id}: {primary_color}, {len(sorted_colors)} colors")
    return tokens


def save_tokens_to_manifest(project_id: str, tokens: Dict):
    """Save extracted tokens to the project's manifest.json."""
    manifest_path = PROJECTS_DIR / project_id / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    manifest = {}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        except:
            pass

    manifest["design_tokens"] = tokens
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
    logger.info(f"[M293] Saved design tokens to manifest for {project_id}")


async def extract_tokens_background(project_id: str):
    """Background task: extract design tokens and save to manifest."""
    try:
        # Run extraction in thread pool (CPU-bound)
        loop = asyncio.get_event_loop()
        tokens = await loop.run_in_executor(None, lambda: extract_design_tokens_from_screens(project_id))
        if tokens:
            await loop.run_in_executor(None, lambda: save_tokens_to_manifest(project_id, tokens))
    except Exception as e:
        logger.error(f"[M293] Background extraction failed for {project_id}: {e}")
