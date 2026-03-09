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

SYSTEM_PROMPT = """You are a Senior Information Architect and Layout Designer for premium SaaS applications.
You receive a genome structure (tabs, organs, components) and produce an optimal layout plan.

PRINCIPLES:
- NEVER use rigid 2-column grids — vary column widths, use asymmetric layouts
- High-density organs get more height; simple organs get less
- Dashboard organs: full-width or 70/30 split
- Form/upload organs: right panel, 400-500px wide
- Chat/overlay organs: floating card positioning
- Canvas/analysis organs: large, 66%+ width

OUTPUT: JSON only. No markdown. Schema:
{
  "phases": {
    "<n0_id>": {
      "layout_style": "string (e.g. split_70_30, asymmetric, full_width, nested)",
      "total_height": <int>,
      "organs": [
        {
          "id": "<n1_id>",
          "x": <int>,   // absolute from left edge (safe_x = 260)
          "y": <int>,   // relative to phase start (0 = top of phase)
          "w": <int>,
          "h": <int>,
          "note": "why this size/position"
        }
      ]
    }
  }
}"""

LAYOUT_PROMPT = """Design the layout for this SaaS application genome.

CANVAS: {w}px total width. Safe content area starts at x={safe_x} (header+sidebar reserved).
Safe area width: {safe_w}px. Phase gap: 40px between phases.

TABS (N0 phases, one artboard per tab):
{tabs_json}

ORGANS to lay out (per phase):
{organs_json}

For each phase: decide x/y/w/h for each organ.
- x must be >= {safe_x} (content area start)
- y = 0 means top of phase content (below app shell header ~72px)
- w + x must not exceed {w} - 40 (right margin)
- Vary layouts: asymmetric, nested, full-width — avoid uniform 2-col grid
- Minimum organ height: 200px. Maximum: 600px.
- Interesting layouts matter: dashboard = wide, form = narrow, canvas = hero-sized

Return JSON only."""


def main():
    api_key = os.getenv("KIMI_KEY")
    if not api_key:
        print("❌ KIMI_KEY not set")
        sys.exit(1)

    pipeline_dir = project_root / "exports/pipeline"
    zone_map_path = pipeline_dir / "zone_map.json"
    if not zone_map_path.exists():
        print("❌ zone_map.json not found — run step 1 first")
        sys.exit(1)

    with open(zone_map_path, encoding="utf-8") as f:
        zone_map = json.load(f)

    canvas = zone_map["canvas"]
    tabs_by_id = {t["id"]: t for t in zone_map["tabs"]}

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
                "n3_count": o["n3_count"],
                "zone_counts": o["zone_counts"],
            }
            for o in organs
        ]

    prompt = LAYOUT_PROMPT.format(
        w=canvas["w"],
        safe_x=canvas["safe_x"],
        safe_w=canvas["safe_w"],
        tabs_json=json.dumps(zone_map["tabs"], indent=2),
        organs_json=json.dumps(organs_summary, indent=2),
    )

    client = OpenAI(base_url="https://api.moonshot.ai/v1", api_key=api_key)
    print("⚖️  KIMI Layout Director — designing layout...")

    response = client.chat.completions.create(
        model="kimi-k2.5",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_tokens=16000,
        extra_body={"thinking": {"type": "enabled"}},
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
