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
APP_HEADER_H = 48
APP_SIDEBAR_W = 220
APP_MARGIN = 40


def build_zone_map(genome: dict) -> dict:
    phases = genome.get("n0_phases", [])

    tabs = [
        {"id": ph["id"], "label": ph.get("name", ph["id"]), "index": i}
        for i, ph in enumerate(phases)
    ]

    organs = []
    for ph in phases:
        for n1 in ph.get("n1_sections", []):
            n3_all = [
                c for n2 in n1.get("n2_features", [])
                for c in n2.get("n3_components", [])
            ]
            zones = _organize_components(n3_all)
            zone_counts = {k: len(v) for k, v in zones.items()}
            organs.append({
                "id": n1["id"],
                "name": n1.get("name", n1["id"]),
                "n0": ph["id"],
                "ui_role": n1.get("ui_role", ""),
                "layout_strategy": n1.get("layout_strategy", ""),
                "n3_count": len(n3_all),
                "zone_counts": zone_counts,
                "components": [
                    {
                        "id": c["id"],
                        "name": c.get("name", c["id"]),
                        "visual_hint": c.get("visual_hint", ""),
                        "zone": _classify_component(c),
                        "description_ui": c.get("description_ui", ""),
                    }
                    for c in n3_all
                ],
            })

    return {
        "canvas": {
            "w": CANVAS_W,
            "header_h": APP_HEADER_H,
            "sidebar_w": APP_SIDEBAR_W,
            "margin": APP_MARGIN,
            "safe_x": APP_MARGIN + APP_SIDEBAR_W,
            "safe_w": CANVAS_W - APP_MARGIN - APP_SIDEBAR_W - APP_MARGIN,
        },
        "tabs": tabs,
        "organs": organs,
    }


def main():
    genome_path = project_root / "Frontend/2. GENOME/genome_enriched.json"
    with open(genome_path, encoding="utf-8") as f:
        genome = json.load(f)

    zone_map = build_zone_map(genome)

    out_dir = project_root / "exports/pipeline"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "zone_map.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(zone_map, f, indent=2, ensure_ascii=False)

    n_tabs = len(zone_map["tabs"])
    n_organs = len(zone_map["organs"])
    print(f"✅ zone_map.json — {n_tabs} tabs, {n_organs} organs")
    print(f"   Tabs: {[t['label'] for t in zone_map['tabs']]}")
    for o in zone_map["organs"]:
        print(f"   [{o['n0']}] {o['id']} — {o['n3_count']} comps — {o['ui_role']}")


if __name__ == "__main__":
    main()
