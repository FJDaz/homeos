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

SYSTEM_PROMPT = """You are a Senior Art Director. Your mission is to define the STYLING for a SaaS application template based on a premium WordPress theme reference.

CRITICAL: The structural layout (coordinates) is FIXED and cannot be changed. You only provide visual direction and component-level style hints.

OUTPUT: JSON only. No markdown.
Schema:
{
  "reference_theme": "string",
  "art_direction": "brief note on visual strategy",
  "typography_overrides": {
    "display_font": "string",
    "accent_color": "hex",
    "bg_color": "hex"
  },
  "phases": {
    "<n0_id>": {
      "organs": {
        "<n1_id>": {
          "atom_style_hint": "detailed style note for atoms in this organ",
          "regenerate_atoms": ["comp_id", ...]
        }
      }
    }
  }
}"""

COMPOSE_PROMPT = """Define the visual style for this SaaS template to match the WP reference.

WP REFERENCE THEME:
{wp_ref_json}

GENOME STRUCTURE (Fixed Layout):
{layout_summary}

INSTRUCTIONS:
- For each organ, provide 'atom_style_hint' detailing colors, borders, shadows, and typography to match the WP theme.
- Focus on making the UI feel "suave", premium, and high-fidelity.
- Do NOT mention coordinates; they are handled by the system.

Return JSON only."""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--feedback", default="", help="FJD feedback for this iteration")
    parser.add_argument("--image", default="", help="Path to image reference for style")
    args = parser.parse_args()

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not set")
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

    layout_summary = {}
    for n0_id, phase_data in layout_plan.get("phases", {}).items():
        layout_summary[n0_id] = [
            {"id": o["id"], "name": o.get("name", o["id"]), "w": o["w"], "h": o["h"]}
            for o in phase_data.get("organs", [])
        ]

    prompt = COMPOSE_PROMPT.format(
        wp_ref_json=json.dumps(wp_ref, indent=2),
        layout_summary=json.dumps(layout_summary, indent=2)
    )

    client = OpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=api_key
    )
    theme_name = wp_ref.get("name", "unknown")
    print(f"🎨 Gemini Composer — aligning style to {theme_name}...")

    # Build messages
    user_content = [{"type": "text", "text": prompt}]
    if args.feedback:
        user_content.append({"type": "text", "text": f"\nFJD FEEDBACK:\n{args.feedback}"})

    response = client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        max_tokens=8192,
        response_format={"type": "json_object"}
    )

    res_text = response.choices[0].message.content or ""
    res_text = re.sub(r"```(?:json)?", "", res_text).replace("```", "").strip()
    
    try:
        style_hints = json.loads(res_text)
    except Exception as e:
        print(f"❌ Failed to parse Composer JSON: {e}")
        sys.exit(1)

    # MERGE HINTS INTO LAYOUT PLAN
    refined = {
        "reference_theme": style_hints.get("reference_theme", theme_name),
        "art_direction": style_hints.get("art_direction", ""),
        "typography_overrides": style_hints.get("typography_overrides", {}),
        "phases": {}
    }

    for n0_id, phase_data in layout_plan.get("phases", {}).items():
        hint_organs = style_hints.get("phases", {}).get(n0_id, {}).get("organs", {})
        refined_organs = []
        for o in phase_data.get("organs", []):
            hint = hint_organs.get(o["id"], {})
            oo = o.copy()
            oo["atom_style_hint"] = hint.get("atom_style_hint", "Maintain consistency with theme.")
            oo["regenerate_atoms"] = hint.get("regenerate_atoms", [])
            refined_organs.append(oo)
        
        refined["phases"][n0_id] = {
            "layout_style": phase_data.get("layout_style", "default"),
            "total_height": phase_data.get("total_height", 800),
            "organs": refined_organs
        }

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
