"""07_composer.py — Hardened SLCP Composer (Multi-Phase Fixed).

Reads scaffold_latest.svg + atoms/*.svg + refined_plan.json.
Injects each atom into its phase-prefixed zone in the scaffold.
"""
import json
import re
import sys
import hashlib
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
pipeline_dir = project_root / "exports/pipeline"

sys.path.insert(0, str(Path(__file__).parent.parent / "exporters"))
from genome_to_svg_v2 import _esc

def inject_atoms_into_placeholder(
    svg_text: str,
    unique_organ_id: str,
    atoms_dir: Path,
    components: list[dict],
    overrides: dict,
    manifest_components: dict,
) -> str:
    """Replace a unique organ placeholder (e.g. phase_1_brs__shell_header) with scaled atoms."""
    # Find the UNIQUE organ group (prefixed with phase_id)
    open_re = re.compile(
        r'(<g\s[^>]*id="' + re.escape(unique_organ_id) + r'"[^>]*>)',
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
        if nxt_c == -1: break
        if nxt_o != -1 and nxt_o < nxt_c:
            depth += 1
            pos = nxt_o + 2
        else:
            depth -= 1
            pos = nxt_c + 4

    inner_content = svg_text[open_end:pos-4]

    # Extract x, y, width, height from the background <rect>
    rect_match = re.search(r'<rect([^>]+)>', inner_content)
    if not rect_match:
        # If no rect but we are here, something is wrong with the scaffold
        return svg_text

    attrs = rect_match.group(1)
    try:
        x = int(float(re.search(r'x="([^"]+)"', attrs).group(1)))
        y = int(float(re.search(r'y="([^"]+)"', attrs).group(1)))
        w = int(float(re.search(r'width="([^"]+)"', attrs).group(1)))
        h = int(float(re.search(r'height="([^"]+)"', attrs).group(1)))
    except Exception as e:
        print(f"  ⚠️  Error parsing rect for {unique_organ_id}: {e}")
        return svg_text

    # Extract Title text
    texts = re.findall(r'<text[^>]*>.*?</text>', inner_content)
    title_texts = "\n".join(texts[:1]) if texts else ""

    atom_parts = []
    current_y = y + 25
    padding_h = 16
    max_atom_w = w - (padding_h * 2)

    for comp in components:
        comp_id = comp["id"]
        atom_path = atoms_dir / f"{comp_id}.svg"
        if not atom_path.exists(): continue

        atom_svg = atom_path.read_text(encoding="utf-8")
        if "</svg>" not in atom_svg: continue
            
        vb_match = re.search(r'viewBox="0 0 (\d+) (\d+)"', atom_svg)
        if vb_match:
            atom_vw, atom_vh = int(vb_match.group(1)), int(vb_match.group(2))
        else:
            w_match = re.search(r'width="([^"]+)"', atom_svg)
            h_match = re.search(r'height="([^"]+)"', atom_svg)
            try:
                atom_vw = int(float(w_match.group(1).replace('px',''))) if w_match else 400
                atom_vh = int(float(h_match.group(1).replace('px',''))) if h_match else 200
            except: atom_vw, atom_vh = 400, 200

        # Subtraction Logic
        scale = min(1.0, max_atom_w / atom_vw)
        rendered_w = int(atom_vw * scale)
        rendered_h = int(atom_vh * scale)

        def cap_radius(match):
            nums = re.findall(r'([0-9.]+)', match.group(2))
            if not nums: return match.group(0)
            val = float(nums[0])
            return f'{match.group(1)}="{int(val) if val <= 10 else 10}"'
        atom_svg = re.sub(r'(r[xy])="([^"]+)"', cap_radius, atom_svg)

        inner = re.sub(r"^<svg[^>]*>", "", atom_svg)
        inner = re.sub(r"</svg>\s*$", "", inner).strip()

        comp_x = x + padding_h
        comp_y = current_y

        if comp_id in overrides:
            ov = overrides[comp_id]
            if 'x' in ov: comp_x = ov['x']
            if 'y' in ov: comp_y = ov['y']
            if 's' in ov: scale = float(ov['s'])

        manifest_components[comp_id] = {
            "x": int(comp_x), "y": int(comp_y),
            "w": rendered_w, "h": rendered_h,
            "scale": round(scale, 4), "organ_id": unique_organ_id,
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
        current_y += rendered_h + 10

    new_content = "\n".join([title_texts] + atom_parts)
    open_tag = match.group(1)
    new_group = f'{open_tag}\n{new_content}\n</g>'

    return svg_text[: match.start()] + new_group + svg_text[pos:]


def main():
    scaffold_path = pipeline_dir / "scaffold_latest.svg"
    zone_map_path = pipeline_dir / "zone_map.json"
    refined_path = pipeline_dir / "refined_plan.json"
    
    if not scaffold_path.exists() or not zone_map_path.exists(): sys.exit(1)

    # Use refined_plan if available
    with open(refined_path if refined_path.exists() else pipeline_dir / "layout_plan.json", "rb") as f:
        plan_content = f.read()
        plan = json.loads(plan_content.decode("utf-8"))
        genome_hash = hashlib.md5(plan_content).hexdigest()

    with open(zone_map_path, encoding="utf-8") as f:
        zone_map = json.load(f)

    atoms_dir = pipeline_dir / "atoms"
    svg_text = scaffold_path.read_text(encoding="utf-8")

    # Overrides
    overrides_path = pipeline_dir / "template_overrides.json"
    overrides = {}
    if overrides_path.exists():
        with open(overrides_path, encoding="utf-8") as f:
            try: overrides = json.load(f)
            except: pass

    # Grid overlay (SLCP markers)
    grid_lines = []
    if "geometric_contract" in zone_map and "phase_1_brs" in zone_map["geometric_contract"]:
        contract = zone_map["geometric_contract"]["phase_1_brs"]
        for zone in contract.get("zones", []):
            zx, zw = zone["x_offset"], zone["width_px"]
            grid_lines.append(f'<line x1="{zx}" y1="0" x2="{zx}" y2="5000" stroke="#ff6b35" stroke-width="1" stroke-dasharray="2,2" opacity="0.4" />')
            grid_lines.append(f'<line x1="{zx+zw}" y1="0" x2="{zx+zw}" y2="5000" stroke="#ff6b35" stroke-width="1" stroke-dasharray="2,2" opacity="0.4" />')

    grid_overlay = f'\n  <g id="grid-overlay-slcp" pointer-events="none">\n    {"    ".join(grid_lines)}\n  </g>\n'
    svg_text = svg_text.replace('</defs>', '</defs>' + grid_overlay)

    # Multi-phase injection
    manifest_components = {}
    for phase_id, phase_data in plan.get("phases", {}).items():
        for organ_data in phase_data.get("organs", []):
            oid = organ_data["id"]
            # Target the prefixed ID in scaffold
            unique_id = f"{phase_id}__{oid}"
            components = []
            for zm_organ in zone_map.get("organs", []):
                if zm_organ["id"] == oid:
                    components = zm_organ.get("components", [])
                    break
            
            svg_text = inject_atoms_into_placeholder(
                svg_text, unique_id, atoms_dir, 
                components, overrides,
                manifest_components
            )

    latest = project_root / "exports" / "template_latest.svg"
    latest.write_text(svg_text, encoding="utf-8")

    manifest = {
        "version": 1,
        "genome_hash": genome_hash,
        "last_updated": datetime.now().isoformat(),
        "components": manifest_components
    }
    with open(project_root / "exports" / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"✅ SLCP Multi-Phase Composition Complete.")

if __name__ == "__main__":
    main()
