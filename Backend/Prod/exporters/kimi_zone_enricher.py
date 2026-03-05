"""KIMI Zone Enricher — enrichit le scaffold genome_zones SVG organe par organe.

Stratégie :
1. Parse genome_zones_*.svg → extrait chaque zone N1 (x, y, w, h)
2. Pour chaque organe : KIMI génère du contenu premium pour la zone exacte
3. Injecte le contenu KIMI dans le <g id="n1_xxx"> correspondant
4. Sauvegarde genome_zones_kimi.svg — 1 fichier complet ouvrable dans Illustrator/Figma

Pass optionnel "layout judge" : KIMI suggère une redistribution des organes entre N0.

CONTRAINTE TYPO ABSOLUE : zéro Times / serif. Inter + Plus Jakarta Sans uniquement.
"""
import os
import sys
import json
import time
import re
from pathlib import Path
from xml.etree import ElementTree as ET
from dotenv import load_dotenv
from openai import OpenAI

project_root = Path(__file__).parent.parent.parent.parent
load_dotenv(project_root / "Backend/.env")

# ── Namespaces SVG ──────────────────────────────────────────────────────────
ET.register_namespace("", "http://www.w3.org/2000/svg")
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")

# ── System prompt ──────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a Lead UI Designer for premium SaaS platforms and ThemeForest top sellers (Divi, Avada, Porto, Flatsome).

TYPOGRAPHY — HARD CONSTRAINT — ABSOLUTE:
- NEVER: Times New Roman, Georgia, serif, or any serif font whatsoever
- ALWAYS: font-family="Inter, system-ui, sans-serif" as base
- Headlines: font-family="Plus Jakarta Sans, Inter, sans-serif" font-weight="700"
- Monospace: font-family="Roboto Mono, monospace"
- EMBED fonts via <defs><style>@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Plus+Jakarta+Sans:wght@600;700&display=swap');</style></defs>

DESIGN STANDARDS (ThemeForest premium):
- Buttons: sharp corners with gradient fill OR subtle pill (rx="6"). Bold text 13-14px. Never plain gray.
- Cards: white #ffffff surface, subtle drop-shadow via <filter><feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="#000" flood-opacity="0.08"/></filter>
- Colors: vibrant accent — use ONE of: blue #1258ca, orange #f05e23, golden #ffd548, green #97ea90
- Backgrounds: white #ffffff OR dark #151515 OR cream #f8f7f4 — NEVER #cccccc or flat gray
- Borders: 1px #e5e7eb or 1px accent — thin, purposeful
- Labels: 10-11px uppercase letter-spacing="1" for metadata/categories
- Density: HIGH — every pixel serves a purpose

OUTPUT: ONLY the content SVG elements (NO outer <svg> wrapper tag, NO markdown fences).
The content will be placed inside an existing <g transform="translate(x,y)"> wrapper."""

# ── Role-specific style ────────────────────────────────────────────────────
ROLE_STYLE = {
    "main-content": (
        "Premium workspace panel. White card, 16px radius, generous internal padding. "
        "Section title 18px Plus Jakarta Sans bold. Content in clean grid. "
        "Accent: blue #1258ca. Shadow filter on card."
    ),
    "form-panel": (
        "Premium form surface. White card, 12px radius. "
        "Input fields with 1px #e5e7eb border, 8px radius. Labels 11px uppercase. "
        "Submit: gradient button full-width, accent fill, white bold text. "
        "Subtle dividers between field groups."
    ),
    "dashboard": (
        "SaaS dashboard (Vercel/Linear/ThemeForest Tecnologia inspired). "
        "Top row: KPI metric cards — number 24px bold, label 11px uppercase. "
        "Below: chart placeholder + activity feed. "
        "Accent: blue #1258ca or #2458f3."
    ),
    "main-canvas": (
        "Content canvas / image workspace. Dark bg #151515 or light #f8f7f4. "
        "Central preview area with subtle grid or placeholder. "
        "Toolbar at top or left: icon buttons, separator lines. "
        "Accent color for active tool/selection."
    ),
    "upload-zone": (
        "File upload area. Large dashed-border drop zone (accent color, 6px dashes). "
        "Center: upload icon 40px + headline Plus Jakarta Sans 20px bold + subtext 13px. "
        "Below: format chips (PNG, JPG, SVG) as rounded badges. "
        "Dark or light variant both acceptable."
    ),
    "chat-overlay": (
        "Chat interface. Dark bg #1a1a2e or #242424, golden accent #ffd548. "
        "Header: avatar circle + name + online indicator. "
        "Message bubbles: user right (accent fill), assistant left (dark surface). "
        "Input bar bottom: rounded input + send button. Inter 13px."
    ),
    "onboarding-flow": (
        "Onboarding/navigation steps. "
        "Progress bar top (accent fill for completed steps). "
        "Large step indicator + headline 24px + description 14px. "
        "Primary CTA button (accent gradient) + secondary (ghost/outline). "
        "Step dots bottom center."
    ),
    "export-action": (
        "Export/action panel. White card, left accent border 3px. "
        "Format chips row (PDF, PNG, SVG, JSON) — selected = accent fill. "
        "Large export button full-width, gradient, pill. "
        "Icon 28px + title 18px bold."
    ),
}

# ── Prompt template ────────────────────────────────────────────────────────
PROMPT_TEMPLATE = """Design premium SVG content for this application zone:

ORGAN: {organ_name}
UI ROLE: {ui_role}
STYLE DIRECTIVE: {style}
CANVAS SIZE: {w}px wide × {h}px tall (start at 0,0)

COMPONENTS to represent visually:
{components_json}

HARD RULES:
- Fill the FULL {w}×{h} canvas — no empty space
- Inter or Plus Jakarta Sans fonts ONLY — NEVER Times New Roman or serif
- Every component in the list above must appear as a real visual element
- Use <defs> for gradients, filters (drop-shadow), and clipPaths
- Accent color: {accent}
- Output SVG elements ONLY — no outer <svg> tag, no markdown"""


def parse_organ_zones(svg_path: Path) -> list[dict]:
    """Parse SVG and extract N1 organ zones with their bounding boxes."""
    tree = ET.parse(svg_path)
    root = tree.getroot()
    ns = {"svg": "http://www.w3.org/2000/svg"}
    organs = []

    # Walk all <g> elements looking for id="n1_*"
    for g in root.iter("{http://www.w3.org/2000/svg}g"):
        gid = g.get("id", "")
        if not gid.startswith("n1_"):
            continue
        name = g.get("data-name", gid)
        ui_role = g.get("data-ui-role", "")

        # First <rect> child = bounding box
        first_rect = g.find("{http://www.w3.org/2000/svg}rect")
        if first_rect is None:
            # Try non-namespaced
            first_rect = g.find("rect")
        if first_rect is None:
            continue

        organs.append({
            "id": gid,
            "name": name,
            "ui_role": ui_role,
            "x": int(float(first_rect.get("x", 0))),
            "y": int(float(first_rect.get("y", 0))),
            "w": int(float(first_rect.get("width", 560))),
            "h": int(float(first_rect.get("height", 240))),
        })

    return organs


def get_components_for_organ(genome: dict, organ_id: str) -> list[dict]:
    """Fetch all N3 components for a given N1 organ."""
    for n0 in genome.get("n0_phases", []):
        for n1 in n0.get("n1_sections", []):
            if n1["id"] == organ_id:
                comps = []
                for n2 in n1.get("n2_features", []):
                    comps.extend(n2.get("n3_components", []))
                return comps
    return []


ACCENTS = ["#1258ca", "#f05e23", "#ffd548", "#97ea90", "#2458f3"]


def pick_accent(organ_id: str) -> str:
    return ACCENTS[hash(organ_id) % len(ACCENTS)]


def generate_zone_content(client, organ: dict, components: list, model: str) -> str | None:
    """Ask KIMI to generate SVG content for one organ zone."""
    ui_role = organ["ui_role"]
    style = ROLE_STYLE.get(ui_role, f"Premium SaaS component. White card, accent blue #1258ca, Inter font.")

    prompt = PROMPT_TEMPLATE.format(
        organ_name=organ["name"],
        ui_role=ui_role,
        style=style,
        w=organ["w"],
        h=organ["h"],
        components_json=json.dumps(
            [{"name": c["name"], "type": c.get("visual_hint"), "action": c.get("description_ui", "")}
             for c in components],
            indent=2, ensure_ascii=False
        ),
        accent=pick_accent(organ["id"]),
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

    # Strip markdown fences if any
    content = re.sub(r"```(?:svg|xml)?", "", content).replace("```", "").strip()

    # Strip any accidental outer <svg> wrapper
    if content.startswith("<svg"):
        # Extract inner content
        inner = re.sub(r"^<svg[^>]*>", "", content)
        inner = re.sub(r"</svg>\s*$", "", inner).strip()
        return inner

    return content if content else None


def inject_zone_content(svg_text: str, organ_id: str, x: int, y: int, kimi_content: str) -> str:
    """Replace the content of <g id="n1_xxx"> with KIMI content, positioned at (x, y)."""
    # Find the opening tag of the organ group
    open_pattern = re.compile(
        r'(<g\s[^>]*id="' + re.escape(organ_id) + r'"[^>]*>)',
        re.DOTALL
    )
    close_tag = '</g>'

    match = open_pattern.search(svg_text)
    if not match:
        print(f"  ⚠️  Could not find <g id='{organ_id}'> in SVG")
        return svg_text

    start = match.start()
    open_end = match.end()

    # Find the matching closing </g> — simple depth counter
    depth = 1
    pos = open_end
    while pos < len(svg_text) and depth > 0:
        next_open = svg_text.find('<g', pos)
        next_close = svg_text.find('</g>', pos)
        if next_close == -1:
            break
        if next_open != -1 and next_open < next_close:
            depth += 1
            pos = next_open + 2
        else:
            depth -= 1
            pos = next_close + 4

    end = pos  # position after closing </g>

    new_group = (
        f'{match.group(1)}\n'
        f'  <g transform="translate({x},{y})">\n'
        f'    {kimi_content}\n'
        f'  </g>\n'
        f'</g>'
    )

    return svg_text[:start] + new_group + svg_text[end:]


def layout_judge_pass(client, genome: dict, model: str) -> str:
    """KIMI as layout judge — suggests organ redistribution across N0 phases."""
    structure = []
    for n0 in genome.get("n0_phases", []):
        organs = [{"id": n1["id"], "name": n1["name"], "ui_role": n1.get("ui_role", "")}
                  for n1 in n0.get("n1_sections", [])]
        structure.append({"phase": n0["name"], "organs": organs})

    prompt = f"""You are a UX Information Architect reviewing a SaaS application structure.

Current organ distribution across phases:
{json.dumps(structure, indent=2, ensure_ascii=False)}

Evaluate:
1. Is the organ distribution logical from a UX flow perspective?
2. Are there organs in the wrong phase?
3. Suggest any redistribution that would improve the user journey.

Respond in structured format: current issues + recommended moves (organ_id → target_phase).
Be concise — max 300 words."""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a senior UX architect. Respond concisely and practically."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=4000,
    )
    return response.choices[0].message.content or ""


def main():
    api_key = os.getenv("KIMI_KEY")
    if not api_key:
        print("❌ KIMI_KEY not set in environment")
        sys.exit(1)

    model = "kimi-k2.5"
    client = OpenAI(base_url="https://api.moonshot.ai/v1", api_key=api_key)

    # Find scaffold SVG
    exports_dir = project_root / "exports"
    scaffold_candidates = sorted(exports_dir.glob("genome_zones_*.svg"), reverse=True)
    if not scaffold_candidates:
        print(f"❌ No genome_zones_*.svg in {exports_dir}")
        sys.exit(1)

    scaffold_path = scaffold_candidates[0]
    print(f"📄 Scaffold: {scaffold_path.name}")

    # Load genome for component data
    genome_path = project_root / "Frontend/2. GENOME/genome_enriched.json"
    with open(genome_path, encoding="utf-8") as f:
        genome = json.load(f)

    # Parse organ zones from SVG
    organ_zones = parse_organ_zones(scaffold_path)
    print(f"🗺️  Found {len(organ_zones)} organ zones: {[o['id'] for o in organ_zones]}")

    # Layout judge pass first
    print("\n⚖️  Layout Judge pass...")
    try:
        judge_verdict = layout_judge_pass(client, genome, model)
        verdict_path = exports_dir / "layout_judge_verdict.txt"
        verdict_path.write_text(judge_verdict, encoding="utf-8")
        print(f"  ✅ Verdict saved → {verdict_path.name}")
        print(f"  Preview: {judge_verdict[:200]}...")
    except Exception as e:
        print(f"  ⚠️  Layout judge failed: {e}")
    time.sleep(1)

    # Load scaffold SVG text for string manipulation
    svg_text = scaffold_path.read_text(encoding="utf-8")

    results = []
    for idx, organ in enumerate(organ_zones, 1):
        organ_id = organ["id"]
        ui_role = organ["ui_role"]
        print(f"\n[{idx:02d}/{len(organ_zones)}] {organ_id} ({ui_role}) — {organ['w']}×{organ['h']} @ ({organ['x']},{organ['y']})...")

        components = get_components_for_organ(genome, organ_id)
        if not components:
            print("  ⚠️  No components found in genome — skipping")
            results.append({"id": organ_id, "status": "skipped"})
            continue

        try:
            kimi_content = generate_zone_content(client, organ, components, model)
            if kimi_content:
                # Save individual zone SVG for FJD review
                zone_svg = (
                    f'<svg xmlns="http://www.w3.org/2000/svg" '
                    f'viewBox="0 0 {organ["w"]} {organ["h"]}" '
                    f'width="{organ["w"]}" height="{organ["h"]}">\n'
                    f'{kimi_content}\n</svg>'
                )
                zone_path = exports_dir / f"{organ_id}_kimi_zone.svg"
                zone_path.write_text(zone_svg, encoding="utf-8")

                # Inject into full SVG
                svg_text = inject_zone_content(svg_text, organ_id, organ["x"], organ["y"], kimi_content)
                results.append({"id": organ_id, "status": "ok"})
                print(f"  ✅ Zone enriched ({len(kimi_content)} chars) → {zone_path.name}")
            else:
                results.append({"id": organ_id, "status": "empty"})
                print("  ❌ Empty response")
        except Exception as e:
            results.append({"id": organ_id, "status": "error", "error": str(e)})
            print(f"  ❌ {e}")

        time.sleep(1)

    # Save final enriched SVG
    from datetime import datetime
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = exports_dir / f"genome_kimi_{ts}.svg"
    out_path.write_text(svg_text, encoding="utf-8")

    ok = sum(1 for r in results if r["status"] == "ok")
    print(f"\n{'='*60}")
    print(f"📊 {ok}/{len(results)} zones enriched")
    print(f"💾 Final template → {out_path.name}")
    print(f"📁 Individual zones → exports/<organ_id>_kimi_zone.svg")

    if any(r["status"] not in ("ok", "skipped") for r in results):
        print("\nFailed:")
        for r in results:
            if r["status"] not in ("ok", "skipped"):
                print(f"  ❌ {r['id']} — {r.get('error', r['status'])}")


if __name__ == "__main__":
    main()
