"""Batch SVG generator — KIMI (Moonshot) pour tous les organes N1 du génome.

Design DNA extraite de thèmes MadSparrow réels :
- Most (Creative Agency) : Plus Jakarta Sans, orange accent, hero slider, masonry
- Osty (Creative Agency) : Inter+Poppins, golden #ffd548, dark #242424 / light #f5f5f5
- Nicex (Portfolio) : Assistant+Open Sans, blue #1258ca, red #c70a1a, dark nav #0D0E13
- Mokko (Portfolio) : Neue Montreal, green #97ea90, full-page slider, dark mode
- Jack Ryan (Portfolio) : Roboto+Bebas Neue, blue #1258CA, dark navy #263654
- Siberia (Portfolio) : blue #2458f3, dark slate #3a3d4f, card grids
- EmilyNolan (Photography) : Yantramanav, #151515 bg, red accent #df1f29
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

# ── System prompt global (ThemeForest DNA) ────────────────────────────────────
SYSTEM_PROMPT = """You are a Lead Theme Architect with deep expertise in premium WordPress themes sold on ThemeForest and Envato Elements (Divi, Avada, The7, Porto, Flatsome, Salient).

DESIGN DNA you must apply:
- Typography: Pair a strong display font (Bebas Neue, Neue Montreal, Plus Jakarta Sans, Yantramanav) with a clean body font (Inter, Roboto, Open Sans). Hero text: 42-64px bold. Section titles: 28-36px. Body: 14-16px.
- Colors: Use one vibrant accent (blue #1258ca, orange hsl(12,85%,58%), golden #ffd548, or green #97ea90) against clean backgrounds (#ffffff or dark #151515/#242424). Never use plain gray.
- Buttons: Always pill-shaped (border-radius: 9999px) OR sharp with bold fill. Gradient fills preferred. Padding: 14px 32px.
- Cards: White surface with subtle drop-shadow (0 4px 24px rgba(0,0,0,0.08)), 8-12px radius. Never flat colored boxes.
- Spacing: Generous. Section padding 80-120px vertical. Internal gaps 24-40px.
- Density: HIGH. Every section is packed with purpose — no empty filler rectangles.

OUTPUT: ONLY the <svg>...</svg> block. No markdown, no explanation, no code fences."""

# ── Role-specific style guidance ──────────────────────────────────────────────
ROLE_STYLE = {
    "nav-header": (
        "Style: Jack Ryan / Siberia. "
        "Fixed header 60-80px. Logo left, nav pills right. "
        "Bebas Neue or bold sans for nav items. "
        "Accent underline on active item. Dark bg #0D0E13 or white. "
        "Add a vibrant CTA button (Get Started / Login) far right."
    ),
    "left-sidebar": (
        "Style: Mokko dark sidebar. "
        "Dark bg #1a1a2e or #151515, width 220px. "
        "Neue Montreal or Inter font. "
        "Active item: accent color fill pill. "
        "Section labels in small caps 10px. Icon + label rows."
    ),
    "main-canvas": (
        "Style: Most / Osty hero section. "
        "Full-width canvas area. "
        "Big headline 48px bold top-left. "
        "Masonry or asymmetric grid of cards below. "
        "Each card: image placeholder + title + subtle tag chip. "
        "Accent color for the primary action button."
    ),
    "main-content": (
        "Style: Siberia content area. "
        "Max-width 960px centered. "
        "Section header 36px semibold. "
        "Content in 2-3 column grid with card components. "
        "Card: white bg, 8px radius, shadow, 24px internal padding."
    ),
    "dashboard": (
        "Style: SaaS premium dashboard (Vercel/Linear inspired + ThemeForest Tecnologia). "
        "Top row: 3-4 KPI metric cards (white, shadow, number 28px bold, label 11px). "
        "Below: asymmetric layout — large chart area (66%) + activity feed (34%). "
        "Accent: blue #1258ca or #2458f3. Dark text #263654."
    ),
    "form-panel": (
        "Style: Nicex / clean SaaS form. "
        "White surface, 12px radius, 32px padding. "
        "Each field: label 11px uppercase tracking, input with bottom-border or full border 1px #e5e7eb. "
        "Submit: full-width pill button, accent fill, white bold text. "
        "Subtle illustration or icon at top."
    ),
    "upload-zone": (
        "Style: EmilyNolan / photography upload. "
        "Large dashed-border drop zone (6px dashes, accent color). "
        "Center: upload icon 48px + bold headline + subtext 14px. "
        "Dark bg variant: #151515 with white text and red/accent dashes. "
        "Below: file format chips (PNG, JPG, SVG) as small rounded badges."
    ),
    "chat-overlay": (
        "Style: Osty dark chat — dark bg #242424, golden accent #ffd548. "
        "Header bar with avatar + name + online dot. "
        "Alternating bubbles: user (accent fill, right) / assistant (dark gray, left). "
        "Input bar at bottom: rounded, dark surface, send button accent. "
        "Font: Inter 14px."
    ),
    "overlay": (
        "Style: Premium modal — Siberia/Nicex style. "
        "Semi-transparent backdrop rgba(0,0,0,0.6). "
        "White card 540px wide, 12px radius, 40px padding, shadow. "
        "Title bar: 20px bold + close X top-right. "
        "Body: 2-3 lines of content. "
        "Footer: Cancel (ghost) + Confirm (accent fill) buttons side by side."
    ),
    "settings-panel": (
        "Style: Jack Ryan settings. "
        "White surface, 16px padding rows. "
        "Each setting: label left (Inter 14px semibold) + toggle right (pill 36x20px). "
        "Active toggle: accent blue fill + white circle. "
        "Section dividers: 1px #f0f0f0. "
        "Danger zone section at bottom (red accent)."
    ),
    "onboarding-flow": (
        "Style: SaaS onboarding steps. "
        "Progress bar top (3-4 steps, accent fill for completed). "
        "Large centered illustration placeholder (120px circle). "
        "Headline 32px + subtext 16px. "
        "Two CTA buttons: primary (accent) + secondary (ghost). "
        "Step indicator dots bottom center."
    ),
    "export-action": (
        "Style: Most / Mokko export/action panel. "
        "Clean white card, accent border-left 3px. "
        "Icon 32px + title 18px bold. "
        "Format selection: chips row (PDF, PNG, SVG, JSON) — selected = accent fill. "
        "Large prominent export button full width, pill, gradient accent."
    ),
    "status-bar": (
        "Style: Jack Ryan footer/status bar. "
        "Dark bg #1a1a1a, height 44px. "
        "Left: 3 colored status dots (green/yellow/gray) + labels. "
        "Center: app name or breadcrumb. "
        "Right: 2 ghost action buttons. "
        "Font: Roboto Mono 11px or Inter 11px."
    ),
}

# ── Main prompt template ───────────────────────────────────────────────────────
PROMPT_TEMPLATE = """Generate an SVG UI section for: {organ_name}

STYLE DIRECTIVE:
{style_directive}

LAYOUT STRATEGY: {layout_strategy}

COMPONENTS to represent (map each to a real visual element):
{components_json}

HARD CONSTRAINTS:
- viewBox="0 0 1000 600" — use the FULL canvas
- Every component above must appear as a visible, designed element
- NO empty gray boxes — every shape must serve a purpose
- Gradients, shadows, and proper typography required
- Use defs for reusable gradients/filters"""


def collect_components(organ):
    components = []
    for feature in organ.get("n2_features", []):
        components.extend(feature.get("n3_components", []))
    return components


def get_style_directive(organ):
    ui_role = organ.get("ui_role", "")
    if ui_role in ROLE_STYLE:
        return ROLE_STYLE[ui_role]
    # Fallback: use organ name + layout_strategy
    return (
        f"Style: Premium SaaS/Agency ThemeForest standard. "
        f"White surface card, accent blue #1258ca, Inter font, shadows, pill buttons. "
        f"Section '{organ.get('name', '')}' — dense, purposeful, no filler."
    )


def generate_svg_for_organ(client, organ, model):
    components = collect_components(organ)
    prompt = PROMPT_TEMPLATE.format(
        organ_name=organ.get("name", organ["id"]),
        style_directive=get_style_directive(organ),
        layout_strategy=organ.get("layout_strategy", "responsive_grid"),
        components_json=json.dumps(components, indent=2)
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        max_tokens=16000,
        extra_body={"thinking": {"type": "disabled"}},
    )
    content = response.choices[0].message.content or ""
    if "<svg" in content:
        return content[content.find("<svg"):content.rfind("</svg>") + 6]
    return None


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

    for n0 in genome.get("n0_phases", []):
        for organ in n0.get("n1_sections", []):
            idx += 1
            organ_id = organ["id"]
            ui_role = organ.get("ui_role", "?")
            print(f"\n[{idx}] {organ_id} ({ui_role}) — {organ.get('name', '')}...")

            try:
                svg = generate_svg_for_organ(client, organ, model)
                if svg:
                    out_path = exports_dir / f"{organ_id}_kimi.svg"
                    out_path.write_text(svg, encoding="utf-8")
                    organ["svg_payload"] = svg
                    results.append({"id": organ_id, "status": "ok", "file": out_path.name})
                    print(f"  ✅ → {out_path.name} ({len(svg)} chars)")
                else:
                    results.append({"id": organ_id, "status": "no_svg"})
                    print(f"  ❌ No SVG in response")
                time.sleep(1)  # rate limit
            except Exception as e:
                results.append({"id": organ_id, "status": "error", "error": str(e)})
                print(f"  ❌ {e}")

    # Save enriched genome with svg_payload
    out_genome = project_root / "Frontend/2. GENOME/genome_enriched_kimi.json"
    with open(out_genome, "w", encoding="utf-8") as f:
        json.dump(genome, f, indent=2, ensure_ascii=False)

    ok = sum(1 for r in results if r["status"] == "ok")
    print(f"\n{'='*50}")
    print(f"📊 {ok}/{len(results)} organs generated")
    print(f"💾 genome_enriched_kimi.json saved")
    for r in results:
        icon = "✅" if r["status"] == "ok" else "❌"
        print(f"  {icon} {r['id']}")


if __name__ == "__main__":
    main()
