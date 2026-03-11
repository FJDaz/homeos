"""03_scaffold_generator.py — Direct Data-Driven Scaffold (Multi-Phase Fixed).

Reads layout_plan.json and draws the SVG 'Walls' using phase-prefixed IDs
to avoid collisions between phases (e.g. phase_1_brs__shell_header).
"""
import json
import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
pipeline_dir = project_root / "exports/pipeline"

def generate_rect_svg(plan: dict) -> str:
    current_y_offset = 0
    phase_svgs = []
    
    for phase_id, phase_data in plan.get("phases", {}).items():
        phase_h = phase_data.get("total_height", 920)
        phase_name = phase_data.get("name", phase_id)
        
        organs_svg = []
        organs_svg.append(f'<rect x="0" y="{current_y_offset}" width="1440" height="{phase_h}" fill="#f7f6f2"/>')
        
        for organ in phase_data.get("organs", []):
            ox = organ["x"]
            oy = organ["y"] + current_y_offset
            ow = organ["w"]
            oh = organ["h"]
            oid = organ["id"]
            # UNIQUE ID for scaffold matching: {phase_id}__{oid}
            unique_id = f"{phase_id}__{oid}"
            oname = organ.get("name", oid)
            
            organs_svg.append(f'<!-- Organ: {oid} in {phase_id} -->')
            organs_svg.append(f'<g id="{unique_id}" class="af-organ" data-genome-id="{oid}" data-name="{oname}">')
            organs_svg.append(f'  <rect x="{ox}" y="{oy}" width="{ow}" height="{oh}" fill="#ffffff" stroke="#d5d4d0" stroke-width="1" rx="8"/>')
            organs_svg.append(f'  <text x="{ox+12}" y="{oy+18}" font-size="7" fill="#b5b4b0" font-weight="600">{oname.upper()}</text>')
            organs_svg.append(f'</g>')
            
        phase_svg = f'<!-- Phase: {phase_name} -->\n<g id="{phase_id}" class="af-phase">\n' + "\n".join(organs_svg) + "\n</g>"
        phase_svgs.append(phase_svg)
        current_y_offset += phase_h
    
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- AetherFlow Hardened Scaffold — Data-Driven SLCP -->
<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="{current_y_offset}">
  <defs>
    <style>text {{ font-family: -apple-system, Helvetica, Arial, sans-serif; }}</style>
  </defs>
  {chr(10).join(phase_svgs)}
</svg>"""

def main():
    layout_path = pipeline_dir / "layout_plan.json"
    if not layout_path.exists(): sys.exit(1)

    with open(layout_path, encoding="utf-8") as f:
        plan = json.load(f)

    svg = generate_rect_svg(plan)
    
    latest_path = pipeline_dir / "scaffold_latest.svg"
    latest_path.write_text(svg, encoding="utf-8")
    print(f"✅ Multi-Phase Scaffold generated with prefixed IDs.")

if __name__ == "__main__":
    main()
