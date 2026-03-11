"""Step 4 — KIMI Atom Factory.

Pour chaque composant N3 : KIMI génère un SVG premium isolé.
4 workers concurrent pour paralléliser les appels API.
Sauve pipeline/atoms/<comp_id>.svg

CONTRAINTE TYPO ABSOLUE : Inter / Plus Jakarta Sans / Bebas Neue uniquement.
JAMAIS Times New Roman, Georgia, ou tout font serif.
"""
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

project_root = Path(__file__).parent.parent.parent.parent
load_dotenv(project_root / "Backend/.env")

SYSTEM_PROMPT = """You are a Lead UI Component Designer at the 'Elite' level, following the PRISTINE design system.
Your mission is to produce highly refined, professional-grade SVG components for a state-of-the-art SaaS application.

TYPOGRAPHY — THE LAW:
- NEVER use serif fonts (Times New Roman, Georgia, etc.). Violation = failure.
- BASE: font-family="Inter, system-ui, sans-serif"
- HEADLINES: font-family="Plus Jakarta Sans, Inter, sans-serif" font-weight="700"
- DATA/MONO: font-family="Roboto Mono, monospace" (size 10-11px)

GEOMETRY & STYLE:
- BORDER-RADIUS (rx/ry): MUST be a SINGLE numeric value (eg. rx="8"). 
- MAX radius is 12px. Optimal is 6px to 10px.
- NEVER use array syntax for radius (eg. rx="0 0 8 8").
- SHADOWS: Use <filter> with <feDropShadow dx="0" dy="4" stdDeviation="8" flood-opacity="0.08"/>.
- BORDERS: 1px or 1.5px using #d5d4d0 (light) or #c5c4c0 (warm).

PALETTE — PRISTINE ACCENTS:
- BLUE: #1258ca | ORANGE: #f05e23 | GOLD: #ffd548 | GREEN: #97ea90 | MODERN BLUE: #2458f3
- Use subtle gradients in <defs> for buttons and active states.

SVG STRUCTURE:
- Keep the SVG tree clean and semantic.
- Use <g id="component_root"> to wrap the entire content.
- Every visual element must be functional (no placeholders).

OUTPUT: Return the <svg> block ONLY. No markdown, no commentary."""

VIEWBOX = {
    "button": (360, 80), "form": (400, 300), "table": (560, 340),
    "dashboard": (560, 300), "list": (400, 260), "stencil-card": (360, 200),
    "detail-card": (480, 300), "status": (400, 80), "card": (360, 180),
    "search": (400, 72), "upload": (400, 220), "slider": (480, 120),
    "default": (440, 240),
}

ZONE_STYLE = {
    "header": "Header component. Dark #0D0E13 or white with border. Compact 60-80px. Logo/title left, actions right. Plus Jakarta Sans bold.",
    "sidebar": "Sidebar nav. Dark #1a1a2e or #f8f7f4. Compact rows icon+label. Active: accent fill pill. Inter 12px.",
    "main": "Main content card. White surface, shadow, generous padding. Section title 18-20px Plus Jakarta Sans bold. Inter body.",
    "footer": "Status/footer bar. Dark #1a1a1a, 44px height. Status dots left, info center, actions right. Roboto Mono 11px.",
    "floating": "Modal/overlay. Semi-transparent backdrop. White card 540px wide, 12px radius, 40px padding. Title + actions.",
}

ACCENTS = ["#1258ca", "#f05e23", "#ffd548", "#97ea90", "#2458f3"]


def get_vb(hint: str, organ_w: int = None, organ_h: int = None) -> tuple[int, int]:
    # If we have real organ dimensions, use them as base
    if organ_w and organ_h:
        # If it's a list or similar multi-item component, we might want a smaller base
        # but for now, let's use the organ width as the primary constraint
        return (organ_w, organ_h)
        
    for k, v in VIEWBOX.items():
        if k in hint:
            return v
    return VIEWBOX["default"]


def pick_accent(comp_id: str) -> str:
    return ACCENTS[hash(comp_id) % len(ACCENTS)]


PROMPT = """Design a premium SVG UI component:

NAME: {name}
TYPE: {visual_hint}
ZONE: {zone}
ZONE STYLE: {zone_style}
WHAT IT DOES: {description_ui}
CANVAS: viewBox="0 0 {vw} {vh}" — fill the FULL canvas

HARD RULES:
- Inter or Plus Jakarta Sans ONLY — NEVER Times New Roman or serif
- Every visual element must be a real UI element (no gray placeholder boxes)
- Use <defs> for gradients, shadows (<filter><feDropShadow.../></filter>)
- Accent color: {accent}
- Output ONLY the <svg>...</svg> block"""


def generate_atom(client, comp: dict, model: str, out_dir: Path, organ_w: int = None, organ_h: int = None) -> dict:
    comp_id = comp["id"]
    api_key = os.getenv("GOOGLE_API_KEY")
    client = OpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=api_key
    )
    visual_hint = comp.get("visual_hint", "default")
    zone = comp.get("zone", "main")
    vw, vh = get_vb(visual_hint, organ_w, organ_h)

    prompt = PROMPT.format(
        name=comp.get("name", comp_id),
        visual_hint=visual_hint,
        zone=zone,
        zone_style=ZONE_STYLE.get(zone, ZONE_STYLE["main"]),
        description_ui=comp.get("description_ui", ""),
        vw=vw, vh=vh,
        accent=pick_accent(comp_id),
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=8000,
            extra_body={"thinking": {"type": "enabled"}},
        )
        content = response.choices[0].message.content or ""
        if "<svg" in content:
            svg = content[content.find("<svg"):content.rfind("</svg>") + 6]
            (out_dir / f"{comp_id}.svg").write_text(svg, encoding="utf-8")
            return {"id": comp_id, "status": "ok", "vw": vw, "vh": vh}
        return {"id": comp_id, "status": "no_svg"}
    except Exception as e:
        return {"id": comp_id, "status": "error", "error": str(e)}


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--context_text", type=str, default="", help="Overarching project context")
    args = parser.parse_args()

    api_key = os.getenv("KIMI_KEY")

    pipeline_dir = project_root / "exports/pipeline"
    zone_map_path = pipeline_dir / "zone_map.json"
    if not zone_map_path.exists():
        print("❌ zone_map.json not found — run step 1 first")
        sys.exit(1)

    with open(zone_map_path, encoding="utf-8") as f:
        zone_map = json.load(f)

    atoms_dir = pipeline_dir / "atoms"
    atoms_dir.mkdir(parents=True, exist_ok=True)

    # Load layout_plan if available to get organ dimensions
    layout_plan = {}
    layout_path = pipeline_dir / "layout_plan.json"
    if layout_path.exists():
        with open(layout_path, encoding="utf-8") as f:
            layout_plan = json.load(f)

    # Collect all N3 components with organ dimensions
    all_comps = []
    for organ in zone_map["organs"]:
        oid = organ["id"]
        n0_id = organ["n0"]
        
        # Get dimensions from layout_plan
        organ_w, organ_h = None, None
        phase_data = layout_plan.get("phases", {}).get(n0_id, {})
        for o in phase_data.get("organs", []):
            if o["id"] == oid:
                organ_w = o.get("w")
                organ_h = o.get("h")
                break

        for comp in organ.get("components", []):
            all_comps.append({**comp, "_organ_id": oid, "_organ_w": organ_w, "_organ_h": organ_h})

    model = "gemini-2.0-flash"
    client = OpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=api_key
    )

    global SYSTEM_PROMPT
    if args.context_text:
        SYSTEM_PROMPT += f"\n\nHere is the overarching vision of the product you are designing today:\n{args.context_text}"

    print(f"⚙️  Atom factory — {len(all_comps)} components, 4 concurrent workers")
    results = []

    with ThreadPoolExecutor(max_workers=1) as pool:
        futures = {
            pool.submit(generate_atom, client, comp, model, atoms_dir, comp.get("_organ_w"), comp.get("_organ_h")): comp["id"]
            for comp in all_comps
            if not (atoms_dir / f"{comp['id']}.svg").exists() # Skip existing
        }
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
                icon = "✅" if result["status"] == "ok" else "❌"
                msg = f"  {icon} {result['id']}"
                if result["status"] == "ok":
                    msg += f" ({result['vw']}×{result['vh']})"
                elif "error" in result:
                    msg += f" — {result['error'][:60]}"
                print(msg)
            except Exception as e:
                print(f"  ❌ Error in worker: {e}")
            time.sleep(1.0)  # Throttling to 1 req/sec

    ok = sum(1 for r in results if r["status"] == "ok")
    print(f"\n✅ {ok}/{len(results)} atoms generated → {atoms_dir}")

    # Save atom manifest
    manifest = {r["id"]: r for r in results}
    (pipeline_dir / "atoms_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
