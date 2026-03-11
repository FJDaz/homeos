"""Step 1 — Zone Planner.

Lit genome_enriched.json → produit pipeline/zone_map.json.
Tab count = len(n0_phases) TOUJOURS. Jamais hardcodé.
Réutilise la logique de classification de genome_to_svg_v2.py.
"""
import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(Path(__file__).parent.parent / "exporters"))

from genome_to_svg_v2 import _classify_component, _organize_components

CANVAS_W = 1440
APP_MARGIN = 20


import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(project_root / "Backend/.env")

GEOMETRIC_PROMPT = """You are a Master Structural Architect. Your mission is to extract the EXACT geometric layout from a project MANIFEST and map provided GENOME ORGANS to specific zones.

MANIFEST:
{manifest_text}

GENOME ORGANS to assign:
{organs_summary}

RULES:
1. CANVAS: 1440px wide. Margin: 20px. Default Sidebar width: 260px.
2. PHASES: Create a contract for EACH Phase ID found in the GENOME.
3. GRID TYPE: Identify the grid (e.g., "triptych-multiverse", "dual-column-roadmap", "pentagrid-ide").
4. ZONES: Define the named zones (e.g., "left_sidebar", "main_col_1", "main_col_2", "right_sidebar", "footer").
5. ASSIGNMENTS: Map EVERY organ to one of your defined zones based on its name and role.
6. HIERARCHY:
   - Sidebar Left -> width: 260px
   - Main Area -> remaining width (1440 - 260 - right_sidebar - gaps)
   - If "Multiverse" with 3 cols -> split Main Area width by 3.
   - If "Dual Col" (Col 1, Col 2) -> split Main Area width by 2.

Output a single JSON object.

JSON SCHEMA:
{{
  "phases": {{
    "<phase_id>": {{
      "grid_type": "string",
      "zones": [
        {{ "name": "string", "width_px": <int>, "x_offset": <int>, "note": "why this width" }}
      ],
      "assignments": {{
        "<organ_id>": "zone_name"
      }}
    }}
  }}
}}"""

def extract_geometric_patterns(manifest_text: str, organs_summary: list) -> dict:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️  GOOGLE_API_KEY not set, skipping geometric extraction")
        return {}
    
    client = OpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=api_key
    )
    
    print(f"🧠 Gemini Architectural Analysis — extracting zones from manifest ({len(manifest_text)} chars)...")
    
    summary = [{"id": o["id"], "name": o["name"], "ui_role": o["ui_role"], "n0": o["n0"]} for o in organs_summary]
    
    response = client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=[
            {"role": "system", "content": "You are a Master Structural Architect. You MUST return valid JSON ONLY. No preamble, no conversational text."},
            {"role": "user", "content": GEOMETRIC_PROMPT.format(manifest_text=manifest_text, organs_summary=json.dumps(summary, indent=2))}
        ],
        max_tokens=8192,
        response_format={"type": "json_object"}
    )
    
    res_text = response.choices[0].message.content
    print(f"   Gemini Response length: {len(res_text)} chars")
    
    # Robust JSON extraction
    import re
    json_match = re.search(r'(\{.*\})', res_text, re.DOTALL)
    if json_match:
        res_text = json_match.group(1)
    
    try:
        return json.loads(res_text)
    except Exception as e:
        print(f"❌ Failed to parse Gemini JSON: {e}")
        # Save raw for inspection
        with open("exports/pipeline/step1_error_raw.txt", "w") as f:
            f.write(res_text)
        return {}

def build_zone_map(genome: dict, manifest_text: str = "") -> dict:
    phases = genome.get("n0_phases", [])
    tabs = [{"id": ph["id"], "label": ph.get("name", ph["id"]), "index": i} for i, ph in enumerate(phases)]

    organs = []
    # -- Parse App Shell --
    app_shell = genome.get("n0_app_shell", {})
    if app_shell:
        for n1 in app_shell.get("n1_sections", []):
            n3_all = [c for n2 in n1.get("n2_features", []) for c in n2.get("n3_components", [])]
            zones = _organize_components(n3_all)
            organs.append({
                "id": n1["id"], "name": n1.get("name", n1["id"]), "n0": "app_shell",
                "ui_role": n1.get("ui_role", ""), "is_shell": True,
                "n3_count": len(n3_all), "zone_counts": {k: len(v) for k, v in zones.items()},
                "components": [{"id": c["id"], "name": c.get("name", c["id"]), "visual_hint": c.get("visual_hint", ""), "zone": _classify_component(c), "description_ui": c.get("description_ui", "")} for c in n3_all],
            })

    # -- Parse Standard Phases --
    for ph in phases:
        for n1 in ph.get("n1_sections", []):
            n3_all = [c for n2 in n1.get("n2_features", []) for c in n2.get("n3_components", [])]
            zones = _organize_components(n3_all)
            organs.append({
                "id": n1["id"], "name": n1.get("name", n1["id"]), "n0": ph["id"],
                "ui_role": n1.get("ui_role", ""), "n3_count": len(n3_all),
                "zone_counts": {k: len(v) for k, v in zones.items()},
                "components": [{"id": c["id"], "name": c.get("name", c["id"]), "visual_hint": c.get("visual_hint", ""), "zone": _classify_component(c), "description_ui": c.get("description_ui", "")} for c in n3_all],
            })

    geometric_contract = {}
    if manifest_text:
        geometric_contract = extract_geometric_patterns(manifest_text, organs)

    return {
        "canvas": {"w": CANVAS_W, "header_h": 0, "sidebar_w": 0, "margin": APP_MARGIN, "safe_x": APP_MARGIN, "safe_w": CANVAS_W - 2 * APP_MARGIN},
        "tabs": tabs,
        "organs": organs,
        "geometric_contract": geometric_contract
    }

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", type=str, default="", help="Path to manifest file")
    args = parser.parse_args()

    genome_path = project_root / "Frontend/2. GENOME/genome_enriched.json"
    with open(genome_path, encoding="utf-8") as f:
        genome = json.load(f)

    manifest_text = ""
    if args.context:
        m_path = project_root / args.context
        print(f"DEBUG: Context path: {m_path}")
        if m_path.exists():
            with open(m_path, encoding="utf-8") as f:
                manifest_text = f.read()
            print(f"DEBUG: Manifest loaded, {len(manifest_text)} chars")
        else:
            print(f"DEBUG: Manifest path NOT FOUND: {m_path}")

    zone_map = build_zone_map(genome, manifest_text)

    out_dir = project_root / "exports/pipeline"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "zone_map.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(zone_map, f, indent=2, ensure_ascii=False)

    print(f"✅ zone_map.json — {len(zone_map['tabs'])} tabs, {len(zone_map['organs'])} organs")
    if zone_map.get("geometric_contract"):
        print("   📐 Geometric Contract extracted from Manifest")


if __name__ == "__main__":
    main()
