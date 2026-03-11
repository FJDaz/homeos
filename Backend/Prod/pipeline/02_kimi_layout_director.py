"""Step 2 — KIMI Layout Director.

KIMI reçoit zone_map.json → décide la distribution des organes dans le canvas.
Produit pipeline/layout_plan.json.

KIMI a CARTE BLANCHE sur le layout : asymétrique, colonnes variables, hauteurs libres.
Pas de grille 2-col rigide. KIMI décide.
"""
import json
import os
import sys
import re
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

project_root = Path(__file__).parent.parent.parent.parent
load_dotenv(project_root / "Backend/.env")

SYSTEM_PROMPT = """You are a Structural Layout Contractor. Your job is to furniture a house where the walls are EXACTLY as defined in the 'geometric_contract'.

CRITICAL INSTRUCTIONS:
1. CONTRACT IS LAW: You MUST use the exact 'width_px' and 'x_offset' from the 'geometric_contract' for each organ's assigned zone.
2. ASSIGNMENTS: Check the 'assignments' object in the contract. If organ 'X' is assigned to zone 'Y', then organ 'X' MUST have the 'x' and 'w' of zone 'Y'.
3. NO INNOVATION: Do not "guess" widths. Do not use 240px if the contract says 260px.
4. SPATIAL STABILITY: 'is_shell' organs MUST have the same (x, y, w, h) across all phases.
5. NO OVERLAPS: Ensure valid y-stacking if multiple organs share a zone (though usually they have their own).

OUTPUT: JSON only. No markdown. Schema:
{
  "phases": {
    "<n0_id>": {
      "layout_style": "string",
      "total_height": <int>,
      "organs": [
        {
          "id": "<n1_id>",
          "x": <int>,
          "y": <int>,
          "w": <int>,
          "h": <int>,
          "note": "EXACT zone name used from contract"
        }
      ]
    }
  }
}"""

LAYOUT_PROMPT = """Fulfill the Structural Layout Contract for this genome.

CANVAS: {w}px total width.
GEOMETRIC CONTRACT (THE RULES):
{contract_json}

ORGANS to lay out (grouped by phase):
{organs_json}

INSTRUCTIONS:
- For each organ, find its assigned zone in 'geometric_contract.assignments'.
- Look up that zone's 'width_px' and 'x_offset' in 'geometric_contract.zones'.
- Apply these values EXACTLY to the organ's 'w' and 'x'.
- Use standard heights (e.g., Header: 60px, Main: 800px) unless specified.

Return JSON only."""

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--context_text", type=str, default="", help="Overarching project context")
    args = parser.parse_args()

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not set")
        sys.exit(1)

    pipeline_dir = project_root / "exports/pipeline"
    zone_map_path = pipeline_dir / "zone_map.json"
    if not zone_map_path.exists():
        print("❌ zone_map.json not found — run step 1 first")
        sys.exit(1)

    with open(zone_map_path, encoding="utf-8") as f:
        zone_map = json.load(f)

    canvas = zone_map["canvas"]
    contract = zone_map.get("geometric_contract", {})

    # Group organs by N0
    organs_by_n0: dict[str, list] = {}
    for o in zone_map["organs"]:
        organs_by_n0.setdefault(o["n0"], []).append(o)

    organs_summary = {}
    for n0_id, organs in organs_by_n0.items():
        organs_summary[n0_id] = [
            {
                "id": o["id"],
                "name": o["name"],
                "ui_role": o["ui_role"],
                "is_shell": o.get("is_shell", False),
                "n3_count": o["n3_count"],
                "zone_counts": o["zone_counts"],
            }
            for o in organs
        ]

    prompt = LAYOUT_PROMPT.format(
        w=canvas["w"],
        contract_json=json.dumps(contract, indent=2),
        tabs_json=json.dumps(zone_map["tabs"], indent=2),
        organs_json=json.dumps(organs_summary, indent=2),
    )
    
    system_prompt = SYSTEM_PROMPT
    if args.context_text:
        system_prompt += f"\n\nContext Document Reference:\n{args.context_text}"

    client = OpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=api_key
    )
    print("⚖️  Gemini Layout Director — enforcing geometric contract...")

    response = client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        max_tokens=8192,
        response_format={"type": "json_object"}
    )

    choice = response.choices[0]
    raw = choice.message.content or ""
    finish = choice.finish_reason
    print(f"   finish_reason: {finish} | content length: {len(raw)} chars")

    if not raw.strip():
        print("❌ KIMI returned empty content")
        print(f"   Usage: {response.usage}")
        sys.exit(1)

    raw = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()

    try:
        layout_plan = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"❌ JSON parse error: {e}")
        print("Raw response (first 1000 chars):")
        print(raw[:1000])
        sys.exit(1)

    out_path = pipeline_dir / "layout_plan.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(layout_plan, f, indent=2, ensure_ascii=False)

    print(f"✅ layout_plan.json saved")
    for n0_id, phase_data in layout_plan.get("phases", {}).items():
        organs = phase_data.get("organs", [])
        style = phase_data.get("layout_style", "?")
        print(f"   {n0_id} ({style}): {len(organs)} organs")
        for o in organs:
            print(f"     {o['id']} @ ({o['x']},{o['y']}) {o['w']}×{o['h']}")


if __name__ == "__main__":
    main()
