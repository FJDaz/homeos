"""Step 3 — Scaffold Generator (Hybrid Scaffold Integration).

Uses genome_to_svg_v2.py to generate a complete App Shell (Header, Sidebar, 
rigid 2-column grid organs). This ensures mathematical stability for N0.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(Path(__file__).parent.parent / "exporters"))

from genome_to_svg_v2 import generate_svg

def main():
    pipeline_dir = project_root / "exports/pipeline"
    genome_path = project_root / "Frontend/2. GENOME/genome_enriched.json"
    
    if not genome_path.exists():
        print(f"❌ {genome_path} not found")
        sys.exit(1)

    with open(genome_path, encoding="utf-8") as f:
        genome = json.load(f)

    # 1. Generate the rigid App Shell Scaffold
    svg = generate_svg(genome, use_kimi=False, style_id='auto')

    # 2. Write to files
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = pipeline_dir / f"scaffold_{ts}.svg"
    out_path.write_text(svg, encoding="utf-8")

    latest_path = pipeline_dir / "scaffold_latest.svg"
    latest_path.write_text(svg, encoding="utf-8")

    print(f"✅ Hybrid Scaffold generated (App Shell N0)")
    print(f"   → {out_path.name} ({len(svg):,} chars)")
    print(f"   → scaffold_latest.svg")

if __name__ == "__main__":
    main()
