"""KIMI atom-level SVG designer — bottom-up N3 components.

Génère UN SVG par composant N3 (32 total).
Chaque SVG = un composant isolé, premium, dense.
Injecte svg_payload + svg_h dans le génome → AtomRenderer.js l'affiche.

CONTRAINTE TYPO ABSOLUE : zéro Times New Roman / serif.
Fonts autorisées : Inter, Plus Jakarta Sans, Bebas Neue, Roboto, Neue Montreal.
"""
import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

project_root = Path(__file__).parent.parent.parent.parent
load_dotenv(project_root / "Backend/.env")

# ── System prompt — typo contrainte absolue ────────────────────────────────────
SYSTEM_PROMPT = """You are a Lead UI Component Designer for premium SaaS applications and ThemeForest top sellers.

TYPOGRAPHY — HARD CONSTRAINT — NO EXCEPTIONS:
- NEVER use Times New Roman, Georgia, serif, or any serif font
- ONLY use: Inter, Plus Jakarta Sans, Bebas Neue, Roboto, Neue Montreal
- Default: font-family="Inter, system-ui, sans-serif"
- Headlines: font-family="Plus Jakarta Sans, Inter, sans-serif" weight 700
- Monospace labels: font-family="Roboto Mono, monospace"

DESIGN STANDARDS (ThemeForest premium):
- Buttons: pill-shaped (rx="9999") OR sharp with gradient fill. Padding equivalent: 14px 28px.
- Cards: white fill, subtle shadow via <filter> (feDropShadow dx=0 dy=4 stdDeviation=8 flood-opacity=0.08)
- Colors: use vibrant accents — blue #1258ca, orange #f05e23, golden #ffd548, green #97ea90
- Backgrounds: white #ffffff or dark #151515 or cream #f8f7f4 — NEVER plain gray #cccccc
- Borders: 1px #e5e7eb or colored accent — NEVER thick black outlines
- Labels: 10-11px uppercase tracking-wider for small metadata
- Density: HIGH — every pixel serves a purpose, no empty rectangles

OUTPUT: ONLY the <svg>...</svg> block. No markdown, no explanations, no code fences."""

# ── viewBox dimensions per visual_hint ───────────────────────────────────────
VIEWBOX = {
    "button":       (360, 80),
    "form":         (400, 320),
    "table":        (560, 340),
    "dashboard":    (560, 300),
    "list":         (400, 260),
    "stencil-card": (360, 200),
    "detail-card":  (480, 300),
    "status":       (400, 80),
    "card":         (360, 180),
    "slider":       (480, 120),
    "toggle":       (280, 72),
    "badge":        (200, 60),
    "chart":        (480, 240),
    "timeline":     (480, 200),
    "search":       (400, 72),
    "upload":       (400, 220),
    "default":      (440, 240),
}

# ── Style guidance per zone_assignment ───────────────────────────────────────
ZONE_STYLE = {
    "header": (
        "Header component. Dark bg #0D0E13 or white with bottom border. "
        "Compact height (60-80px). Logo/title left, actions right. "
        "Font: Plus Jakarta Sans bold."
    ),
    "sidebar": (
        "Sidebar component. Dark bg #1a1a2e or light #f8f7f4. "
        "Compact rows with icon + label. Active state: accent fill pill. "
        "Font: Inter 12-13px."
    ),
    "main": (
        "Main content component. White surface, generous padding. "
        "Card style with shadow. Section header 18-22px bold. "
        "Font: Inter or Plus Jakarta Sans."
    ),
    "footer": (
        "Footer/status bar. Dark bg #1a1a1a, compact 44px. "
        "Status indicators left, info center, actions right. "
        "Font: Roboto Mono 11px."
    ),
    "default": (
        "Premium SaaS component. White card, accent #1258ca, Inter font, shadow."
    ),
}

# ── Prompt template ───────────────────────────────────────────────────────────
PROMPT_TEMPLATE = """Generate an SVG UI component for: {comp_name}

COMPONENT TYPE: {visual_hint}
ZONE: {zone}
ZONE STYLE: {zone_style}
USER ACTION: {description_ui}

CANVAS: viewBox="0 0 {vw} {vh}" — use the FULL canvas, no wasted space.

HARD CONSTRAINTS:
- Font: Inter or Plus Jakarta Sans ONLY — NEVER Times New Roman or serif
- No empty gray rectangles — every shape must be a real UI element
- Minimum 2 interactive states visible (default + hover/focus implied by design)
- Drop shadow via <filter><feDropShadow .../></filter> on cards
- Accent color: {accent}
- This is ONE isolated component — NOT a full page layout"""


def get_viewbox(visual_hint: str) -> tuple[int, int]:
    return VIEWBOX.get(visual_hint, VIEWBOX["default"])


def get_zone_style(zone: str) -> str:
    return ZONE_STYLE.get(zone, ZONE_STYLE["default"])


def pick_accent(comp_id: str) -> str:
    """Rotate accents across components for variety."""
    accents = ["#1258ca", "#f05e23", "#ffd548", "#97ea90", "#2458f3", "#df1f29"]
    idx = hash(comp_id) % len(accents)
    return accents[idx]


def generate_svg_for_component(client, comp: dict, model: str) -> str | None:
    visual_hint = comp.get("visual_hint", "default")
    zone = comp.get("zone_assignment", "main")
    vw, vh = get_viewbox(visual_hint)

    prompt = PROMPT_TEMPLATE.format(
        comp_name=comp.get("name", comp["id"]),
        visual_hint=visual_hint,
        zone=zone,
        zone_style=get_zone_style(zone),
        description_ui=comp.get("description_ui", ""),
        vw=vw,
        vh=vh,
        accent=pick_accent(comp["id"]),
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_tokens=16000,
        extra_body={"thinking": {"type": "disabled"}},
    )

    content = response.choices[0].message.content or ""
    if "<svg" in content:
        return content[content.find("<svg"):content.rfind("</svg>") + 6]
    return None


def iter_components(genome: dict):
    """Yield (n0_id, n1_id, n2_id, comp) for all N3 components."""
    for n0 in genome.get("n0_phases", []):
        for n1 in n0.get("n1_sections", []):
            for n2 in n1.get("n2_features", []):
                for comp in n2.get("n3_components", []):
                    yield n0["id"], n1["id"], n2["id"], comp


def main():
    api_key = os.getenv("KIMI_KEY")
    if not api_key:
        print("❌ KIMI_KEY not set in environment")
        sys.exit(1)

    model = "kimi-k2.5"
    client = OpenAI(base_url="https://api.moonshot.ai/v1", api_key=api_key)

    genome_path = project_root / "Frontend/2. GENOME/genome_enriched.json"
    if not genome_path.exists():
        print(f"❌ Genome not found: {genome_path}")
        sys.exit(1)

    with open(genome_path, encoding="utf-8") as f:
        genome = json.load(f)

    exports_dir = project_root / "exports"
    exports_dir.mkdir(exist_ok=True)

    results = []
    idx = 0
    errors = 0

    for n0_id, n1_id, n2_id, comp in iter_components(genome):
        idx += 1
        comp_id = comp["id"]
        visual_hint = comp.get("visual_hint", "?")
        zone = comp.get("zone_assignment", "?")
        vw, vh = get_viewbox(visual_hint)
        print(f"\n[{idx:02d}] {comp_id} ({visual_hint}, {zone}) — {vw}×{vh}...")

        try:
            svg = generate_svg_for_component(client, comp, model)
            if svg:
                # Inject into genome
                comp["svg_payload"] = svg
                comp["svg_h"] = get_viewbox(visual_hint)[1]
                comp["svg_w"] = get_viewbox(visual_hint)[0]

                # Save individual file for FJD review
                out_path = exports_dir / f"{comp_id}_kimi.svg"
                out_path.write_text(svg, encoding="utf-8")
                results.append({"id": comp_id, "status": "ok", "file": out_path.name})
                print(f"  ✅ {out_path.name} ({len(svg)} chars)")
            else:
                results.append({"id": comp_id, "status": "no_svg"})
                print("  ❌ No SVG in response")
                errors += 1
        except Exception as e:
            results.append({"id": comp_id, "status": "error", "error": str(e)})
            print(f"  ❌ {e}")
            errors += 1

        time.sleep(0.8)  # rate limit

    # Save enriched genome with svg_payload on N3 nodes
    out_genome = project_root / "Frontend/2. GENOME/genome_enriched_kimi_atoms.json"
    with open(out_genome, "w", encoding="utf-8") as f:
        json.dump(genome, f, indent=2, ensure_ascii=False)

    ok = sum(1 for r in results if r["status"] == "ok")
    print(f"\n{'='*60}")
    print(f"📊 {ok}/{len(results)} components generated ({errors} errors)")
    print(f"💾 genome_enriched_kimi_atoms.json saved")
    print(f"📁 SVG files in {exports_dir}/")

    if errors:
        print("\nFailed:")
        for r in results:
            if r["status"] != "ok":
                print(f"  ❌ {r['id']} — {r.get('error', r['status'])}")


if __name__ == "__main__":
    main()
