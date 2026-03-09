"""Step 6 — KIMI Composer (Reference Matcher).

KIMI reçoit layout_plan + wp_reference + atoms manifest + feedback FJD optionnel.
KIMI produit un plan raffiné pour coller à la référence WP.
Produit pipeline/refined_plan.json.

Usage:
  python 06_kimi_composer.py
  python 06_kimi_composer.py --feedback "les cards sont trop petites, dashboard besoin de plus d'espace"
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

project_root = Path(__file__).parent.parent.parent.parent
load_dotenv(project_root / "Backend/.env")

SYSTEM_PROMPT = """You are a Senior Art Director aligning a SaaS application template with a premium WordPress theme reference.

Your task:
1. Review the current layout plan
2. Study the WP reference design tokens (colors, typography, layout style)
3. Produce a REFINED layout plan that makes the template look like the WP reference
4. You may resize, reposition, or reorder organs to match the reference vibe

OUTPUT: JSON only. No markdown.
Schema:
{
  "reference_theme": "string",
  "art_direction": "brief note on the visual direction taken",
  "typography_overrides": {
    "display_font": "...",
    "body_font": "...",
    "accent_color": "#...",
    "bg_color": "#..."
  },
  "phases": {
    "<n0_id>": {
      "layout_style": "string",
      "total_height": <int>,
      "organs": [
        {
          "id": "<n1_id>",
          "x": <int>, "y": <int>, "w": <int>, "h": <int>,
          "atom_style_hint": "brief style note for this organ's atoms",
          "regenerate_atoms": ["<comp_id>", ...]  // list atoms that should be regenerated with new style
        }
      ]
    }
  }
}

SEMANTIC & CALIBRATION CONSTRAINTS:
- The final SVG will use 'id' and 'class="kimi-comp"' for interactivity.
- Ensure all organ and component IDs from the genome are preserved in your refined plan.
- DIMENSIONS: You MUST respect the per-organ dimensions (zone_w, zone_h) provided in the layout plan.
- Atomatic components MUST be designed to fit EXACTLY within their organ's viewBox="0 0 {zone_w} {zone_h}".
- NEVER use absolute coordinates that exceed the organ's width or height. Components currently appear 4x too large; you must compensate by ensuring your visual density matches the target pixel dimensions precisely."""

COMPOSE_PROMPT = """Align this SaaS template layout with the WP reference theme.

CALIBRATION INFO:
The main canvas is 1440px wide. 
Safe content area starts at x=260.
Organ dimensions (w, h) are absolute pixel values. 

CURRENT LAYOUT PLAN:
{layout_plan_json}

WP REFERENCE THEME:
{wp_ref_json}

AVAILABLE ATOMS (generated components):
{atoms_json}

{feedback_section}

TASK:
- Adjust organ positions/sizes to match the WP reference's proportions and vibe
- For each organ, provide a 'viewbox_hint' in the 'atom_style_hint' matching its refined width/height
- Update colors/typography to match the reference palette
- LARGE components must be dense and high-fidelity, not low-res sketches
- Respect safe area: content x >= 260

Return JSON refined_plan matching the schema."""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--feedback", default="", help="FJD feedback for this iteration")
    parser.add_argument("--image", default="", help="Path to image reference for style")
    args = parser.parse_args()

    api_key = os.getenv("KIMI_KEY")
    if not api_key:
        print("❌ KIMI_KEY not set")
        sys.exit(1)

    pipeline_dir = project_root / "exports/pipeline"

    for required in ["layout_plan.json", "wp_reference.json"]:
        if not (pipeline_dir / required).exists():
            print(f"❌ {required} not found — run previous steps first")
            sys.exit(1)

    with open(pipeline_dir / "layout_plan.json", encoding="utf-8") as f:
        layout_plan = json.load(f)
    with open(pipeline_dir / "wp_reference.json", encoding="utf-8") as f:
        wp_ref = json.load(f)

    # Load atom manifest if available
    atoms_manifest = {}
    atoms_path = pipeline_dir / "atoms_manifest.json"
    if atoms_path.exists():
        with open(atoms_path, encoding="utf-8") as f:
            atoms_manifest = json.load(f)

    atoms_summary = [
        {"id": aid, "status": a["status"], "vw": a.get("vw"), "vh": a.get("vh")}
        for aid, a in atoms_manifest.items()
        if a["status"] == "ok"
    ]

    feedback_section = ""
    if args.feedback:
        feedback_section = f"\nFJD FEEDBACK (must be addressed):\n{args.feedback}\n"

    prompt = COMPOSE_PROMPT.format(
        layout_plan_json=json.dumps(layout_plan, indent=2),
        wp_ref_json=json.dumps(wp_ref, indent=2),
        atoms_json=json.dumps(atoms_summary, indent=2) if atoms_summary else "(not yet generated)",
        feedback_section=feedback_section,
    )

    client = OpenAI(base_url="https://api.moonshot.ai/v1", api_key=api_key)
    theme_name = wp_ref.get("name", "unknown")
    print(f"🎨 KIMI Composer — aligning to {theme_name}...")
    if args.feedback:
        print(f"   Feedback: {args.feedback}")
    if args.image:
        print(f"   Image reference: {args.image}")

    # Build messages
    user_content = [{"type": "text", "text": prompt}]
    if args.image:
        import base64
        import mimetypes
        img_path = Path(args.image)
        if img_path.exists():
            mime_type, _ = mimetypes.guess_type(args.image)
            img_b64 = base64.b64encode(img_path.read_bytes()).decode("utf-8")
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{img_b64}"}
            })

    response = client.chat.completions.create(
        model="kimi-k2.5",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        max_tokens=16000,
        extra_body={"thinking": {"type": "enabled"}},
    )

    raw = response.choices[0].message.content or ""
    raw = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()

    try:
        refined = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"❌ JSON parse error: {e}")
        print("Raw:", raw[:500])
        sys.exit(1)

    out_path = pipeline_dir / "refined_plan.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(refined, f, indent=2, ensure_ascii=False)

    print(f"✅ refined_plan.json saved")
    print(f"   Art direction: {refined.get('art_direction', '?')}")
    typo = refined.get("typography_overrides", {})
    if typo:
        print(f"   Display font: {typo.get('display_font', '?')}")
        print(f"   Accent: {typo.get('accent_color', '?')}")

    regen_count = sum(
        len(o.get("regenerate_atoms", []))
        for ph in refined.get("phases", {}).values()
        for o in ph.get("organs", [])
    )
    if regen_count:
        print(f"   ⚠️  {regen_count} atoms flagged for regeneration")


if __name__ == "__main__":
    main()
