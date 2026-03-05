"""Step 7 — Composer.

Lit scaffold_latest.svg + atoms/*.svg + refined_plan.json.
Injecte chaque atom dans sa zone placeholder.
Produit exports/template_TIMESTAMP.svg — le fichier final Illustrator/Figma.
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent

sys.path.insert(0, str(Path(__file__).parent.parent / "exporters"))
from genome_to_svg_v2 import _esc

# Grid System (12 columns)
SIDEBAR_W = 220
MARGIN = 40
SAFE_X = SIDEBAR_W + MARGIN  # 260
SAFE_W = 1140
GRID_COLS = 12
COL_UNIT = 95  # 1140 / 12
GUTTER = 20


def get_organ_atoms(zone_map: dict, organ_id: str) -> list[dict]:
    for organ in zone_map["organs"]:
        if organ["id"] == organ_id:
            return organ.get("components", [])
    return []


import hashlib

def inject_atoms_into_placeholder(
    svg_text: str,
    organ_id: str,
    atoms_dir: Path,
    components: list[dict],
    overrides: dict,
    manifest_components: dict,
) -> str:
    """Replace the organ placeholder <g> content with KIMI atoms."""
    # Find the organ group
    open_re = re.compile(
        r'(<g\s[^>]*id="' + re.escape(organ_id) + r'"[^>]*>)',
        re.DOTALL,
    )
    match = open_re.search(svg_text)
    if not match:
        return svg_text

    open_end = match.end()

    # Find matching </g>
    depth = 1
    pos = open_end
    while pos < len(svg_text) and depth > 0:
        nxt_o = svg_text.find("<g", pos)
        nxt_c = svg_text.find("</g>", pos)
        if nxt_c == -1:
            break
        if nxt_o != -1 and nxt_o < nxt_c:
            depth += 1
            pos = nxt_o + 2
        else:
            depth -= 1
            pos = nxt_c + 4

    inner_content = svg_text[open_end:pos-4]

    # Extract x, y, width, height from the first <rect> (the background)
    rect_match = re.search(r'<rect([^>]+)>', inner_content)
    if not rect_match:
        return svg_text # Not a standard v2 organ, skip

    attrs = rect_match.group(1)
    try:
        x = int(float(re.search(r'x="([^"]+)"', attrs).group(1)))
        y = int(float(re.search(r'y="([^"]+)"', attrs).group(1)))
        w = int(float(re.search(r'width="([^"]+)"', attrs).group(1)))
        h = int(float(re.search(r'height="([^"]+)"', attrs).group(1)))
    except:
        return svg_text

    # Organ position overrides
    organ_x, organ_y = x, y
    if organ_id in overrides:
        ov = overrides[organ_id]
        if 'x' in ov: organ_x = ov['x']
        if 'y' in ov: organ_y = ov['y']

    # Extract the organ Title text (first two texts usually)
    texts = re.findall(r'<text[^>]*>.*?</text>', inner_content)
    title_texts = "\n".join(texts[:2]) if texts else ""

    atom_parts = []
    current_y = y + 40 # Padding after the title
    max_y = current_y
    max_atom_w = w - 32  # horizontal padding

    for comp in components:
        comp_id = comp["id"]
        atom_path = atoms_dir / f"{comp_id}.svg"
        if not atom_path.exists():
            continue

        atom_svg = atom_path.read_text(encoding="utf-8")
        if "</svg>" not in atom_svg or "<svg" not in atom_svg:
            print(f"  ⚠️  {comp_id}: malformed SVG — skipped")
            continue
            
        vb_match = re.search(r'viewBox="0 0 (\d+) (\d+)"', atom_svg)
        if vb_match:
            atom_vw, atom_vh = int(vb_match.group(1)), int(vb_match.group(2))
        else:
            w_match = re.search(r'width="([^"]+)"', atom_svg)
            h_match = re.search(r'height="([^"]+)"', atom_svg)
            try:
                atom_vw = int(float(w_match.group(1).replace('px',''))) if w_match else 440
                atom_vh = int(float(h_match.group(1).replace('px',''))) if h_match else 240
            except:
                atom_vw, atom_vh = 440, 240

        scale_to_fit = max_atom_w / atom_vw
        scale = min(1.0, scale_to_fit)
        
        rendered_w = int(atom_vw * scale)
        rendered_h = int(atom_vh * scale)

        # Safety Cap: François requested no rx/ry (border-radius) above 10
        # Also handles KIMI hallucinating array values like "0 0 8 8" by taking the first number
        def cap_radius(match):
            nums = re.findall(r'([0-9.]+)', match.group(2))
            if not nums: return match.group(0)
            val = float(nums[0])
            return f'{match.group(1)}="{int(val) if val <= 10 else 10}"'
        
        atom_svg = re.sub(r'(r[xy])="([^"]+)"', cap_radius, atom_svg)

        inner = re.sub(r"^<svg[^>]*>", "", atom_svg)
        inner = re.sub(r"</svg>\s*$", "", inner).strip()

        comp_x = x + 16
        comp_y = current_y

        # Apply overrides from template_overrides.json (/api/comp-move & /api/comp-resize)
        if comp_id in overrides:
            ov = overrides[comp_id]
            if 'x' in ov: comp_x = ov['x']
            if 'y' in ov: comp_y = ov['y']
            if 's' in ov: scale = float(ov['s'])

        # Store in manifest (relative to entire canvas)
        manifest_components[comp_id] = {
            "x": int(comp_x),
            "y": int(comp_y),
            "w": rendered_w,
            "h": rendered_h,
            "scale": round(scale, 4),
            "organ_id": organ_id,
            "intent": comp.get("intent", ""),
            "name": comp.get("name", comp_id),
            "source": "kimi",
            "svg": atom_svg
        }

        handle_svg = f'<rect class="resize-handle" x="{atom_vw - 12}" y="{atom_vh - 12}" width="24" height="24" fill="transparent" stroke="#f05e23" stroke-width="2" style="cursor:se-resize; pointer-events:all; opacity:0;"/>'

        atom_parts.append(
            f'<g id="{_esc(comp_id)}" class="kimi-comp" transform="translate({comp_x},{comp_y}) scale({scale:.4f})">\n'
            f'  <title>{_esc(comp.get("name", comp_id))}</title>\n'
            f'{inner}\n'
            f'{handle_svg}\n'
            f'</g>'
        )
        current_y += rendered_h + 12
        max_y = max(max_y, current_y)

    # Calculate new required height based on max_y
    new_h = max_y - y + 20 # bottom padding

    # Only keep the original background if no atoms were injected
    if not atom_parts:
        bg = rect_match.group(0)
        new_content = "\n".join([bg, title_texts])
    else:
        bg = rect_match.group(0)
        bg = re.sub(r'height="[^"]+"', f'height="{new_h}"', bg)
        new_content = "\n".join([bg, title_texts] + atom_parts)

    open_tag = match.group(1)
    if organ_id in overrides:
        ov = overrides[organ_id]
        if 'x' in ov and 'y' in ov:
            tag_end = open_tag.rfind('>')
            if tag_end != -1:
                open_tag = re.sub(r'\stransform="[^"]+"', '', open_tag)
                open_tag = f'{open_tag[:tag_end]} transform="translate({ov["x"]},{ov["y"]})"{open_tag[tag_end:]}'

    new_group = f'{open_tag}\n{new_content}\n</g>'

    return svg_text[: match.start()] + new_group + svg_text[pos:]


def main():
    pipeline_dir = project_root / "exports/pipeline"

    scaffold_path = pipeline_dir / "scaffold_latest.svg"
    if not scaffold_path.exists():
        sys.exit(1)

    zone_map_path = pipeline_dir / "zone_map.json"
    if not zone_map_path.exists():
        sys.exit(1)

    refined_path = pipeline_dir / "refined_plan.json"
    layout_path = pipeline_dir / "layout_plan.json"
    
    # Use refined_plan if available
    plan_path = refined_path if refined_path.exists() else layout_path
    with open(plan_path, "rb") as f:
        plan_content = f.read()
        plan = json.loads(plan_content.decode("utf-8"))
        genome_hash = hashlib.md5(plan_content).hexdigest()

    with open(zone_map_path, encoding="utf-8") as f:
        zone_map = json.load(f)

    atoms_dir = pipeline_dir / "atoms"
    svg_text = scaffold_path.read_text(encoding="utf-8")

    overrides_path = pipeline_dir / "template_overrides.json"
    overrides = {}
    if overrides_path.exists():
        with open(overrides_path, encoding="utf-8") as f:
            try: overrides = json.load(f)
            except: pass

    # --- GRID VISUALIZER (Mission 24G) ---
    grid_svg = []
    for i in range(GRID_COLS + 1):
        gx = SAFE_X + i * COL_UNIT
        grid_svg.append(f'<line x1="{gx}" y1="0" x2="{gx}" y2="3000" stroke="#ff6b35" stroke-width="1" stroke-dasharray="8,4" opacity="0.15" />')
    
    grid_overlay = f'\n  <g id="grid-overlay" pointer-events="none">\n    {"    ".join(grid_svg)}\n  </g>\n'
    svg_text = svg_text.replace('</defs>', '</defs>' + grid_overlay)

    manifest_components = {}
    for organ in zone_map["organs"]:
        organ_id = organ["id"]
        svg_text = inject_atoms_into_placeholder(
            svg_text, organ_id, atoms_dir, 
            organ.get("components", []), overrides,
            manifest_components
        )

    latest = project_root / "exports" / "template_latest.svg"
    latest.write_text(svg_text, encoding="utf-8")

    # Write Manifest
    manifest = {
        "version": 1,
        "genome_hash": genome_hash,
        "last_updated": datetime.now().isoformat(),
        "components": manifest_components,
        "figma_extra": [],
        "pending_retro": []
    }
    manifest_path = project_root / "exports" / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"✅ Template composed and manifest.json generated.")

if __name__ == "__main__":
    main()
