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

SYSTEM_PROMPT = """You are a Lead UI Component Designer for premium SaaS and ThemeForest top sellers.

TYPOGRAPHY — ABSOLUTE HARD CONSTRAINT:
- NEVER: Times New Roman, Georgia, serif, or any serif typeface
- ALWAYS base: font-family="Inter, system-ui, sans-serif"
- Headlines: font-family="Plus Jakarta Sans, Inter, sans-serif" font-weight="700"
- Code/mono: font-family="Roboto Mono, monospace"

DESIGN STANDARDS:
- BORDER-RADIUS (rx/ry): MUST be a SINGLE numeric value (eg. rx="8"). NEVER array syntax (eg. rx="0 0 8 8"). MAX rx="10" globally.
- Buttons: gradient fill OR solid accent. rx="6" or rx="10". Bold white label.
- Cards: white #ffffff, drop-shadow <filter><feDropShadow dx="0" dy="4" stdDeviation="8" flood-opacity="0.08"/></filter>
- Accents: #1258ca (blue), #f05e23 (orange), #ffd548 (golden), #97ea90 (green)
- Backgrounds: #ffffff or #151515 or #f8f7f4. NEVER flat #cccccc gray.
- Labels: 10px uppercase letter-spacing="1.5" for metadata
- Density: HIGH — every pixel purposeful

OUTPUT: <svg>...</svg> block ONLY. No markdown fences."""

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
            extra_body={"thinking": {"type": "disabled"}},
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

    model = "kimi-k2.5"
    client = OpenAI(base_url="https://api.moonshot.ai/v1", api_key=api_key)

    print(f"⚙️  Atom factory — {len(all_comps)} components, 4 concurrent workers")
    results = []

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {
            pool.submit(generate_atom, client, comp, model, atoms_dir, comp.get("_organ_w"), comp.get("_organ_h")): comp["id"]
            for comp in all_comps
        }
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            icon = "✅" if result["status"] == "ok" else "❌"
            msg = f"  {icon} {result['id']}"
            if result["status"] == "ok":
                msg += f" ({result['vw']}×{result['vh']})"
            elif "error" in result:
                msg += f" — {result['error'][:60]}"
            print(msg)
            time.sleep(0.2)  # light throttle

    ok = sum(1 for r in results if r["status"] == "ok")
    print(f"\n✅ {ok}/{len(results)} atoms generated → {atoms_dir}")

    # Save atom manifest
    manifest = {r["id"]: r for r in results}
    (pipeline_dir / "atoms_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
