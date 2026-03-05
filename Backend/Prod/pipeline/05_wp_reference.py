"""Step 5 — WP Reference.

Extrait les tokens design d'un thème ThemeForest de référence.
Produit pipeline/wp_reference.json.

Usage:
  python 05_wp_reference.py --theme most
  python 05_wp_reference.py --theme jackryan

Thèmes disponibles : most, osty, nicex, mokko, jackryan, siberia, emilynolan
"""
import argparse
import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent

# ── Design DNA extraite des 7 thèmes MadSparrow vérifiés ─────────────────────
THEMES = {
    "most": {
        "name": "Most (Creative Agency)",
        "url": "https://madsparkstudio.com/themes/most/?storefront=envato-elements",
        "colors": {
            "primary": "#ff6b35",
            "bg": "#ffffff",
            "dark": "#111111",
            "text": "#333333",
            "muted": "#888888",
            "accent2": "#1a1a2e",
        },
        "typography": {
            "display": {"family": "Plus Jakarta Sans", "weight": 700, "size_hero": 64},
            "body": {"family": "Inter", "weight": 400, "size": 16},
            "label": {"family": "Inter", "weight": 600, "size": 11, "uppercase": True},
        },
        "layout": {
            "style": "masonry_hero",
            "hero_height": 700,
            "card_radius": 12,
            "card_shadow": "0 8px 32px rgba(0,0,0,0.10)",
            "button_style": "pill",
            "button_radius": 9999,
            "section_padding_v": 120,
            "col_gap": 32,
        },
        "vibe": "bold creative agency — high contrast, orange energy, masonry grids",
    },
    "osty": {
        "name": "Osty (Creative Agency)",
        "url": "https://madsparkstudio.com/themes/osty/?storefront=envato-elements",
        "colors": {
            "primary": "#ffd548",
            "bg": "#f5f5f5",
            "dark": "#242424",
            "text": "#242424",
            "muted": "#777777",
        },
        "typography": {
            "display": {"family": "Poppins", "weight": 700, "size_hero": 56},
            "body": {"family": "Inter", "weight": 400, "size": 15},
            "label": {"family": "Inter", "weight": 600, "size": 10, "uppercase": True},
        },
        "layout": {
            "style": "dark_light_split",
            "hero_height": 600,
            "card_radius": 8,
            "card_shadow": "0 4px 20px rgba(0,0,0,0.08)",
            "button_style": "sharp_fill",
            "button_radius": 4,
            "section_padding_v": 100,
            "col_gap": 24,
        },
        "vibe": "golden luxury — dark sidebar, golden accents, clean typography",
    },
    "nicex": {
        "name": "Nicex (Portfolio)",
        "url": "https://madsparkstudio.com/themes/nicex/?storefront=envato-elements",
        "colors": {
            "primary": "#1258ca",
            "danger": "#c70a1a",
            "bg": "#ffffff",
            "dark": "#0D0E13",
            "text": "#2d2d2d",
            "muted": "#888888",
        },
        "typography": {
            "display": {"family": "Plus Jakarta Sans", "weight": 700, "size_hero": 52},
            "body": {"family": "Open Sans", "weight": 400, "size": 15},
            "label": {"family": "Open Sans", "weight": 600, "size": 10, "uppercase": True},
        },
        "layout": {
            "style": "portfolio_centered",
            "hero_height": 550,
            "card_radius": 10,
            "card_shadow": "0 4px 24px rgba(0,0,0,0.08)",
            "button_style": "pill",
            "button_radius": 9999,
            "section_padding_v": 80,
            "col_gap": 28,
        },
        "vibe": "precise blue — corporate portfolio, blue+red accents, clean sections",
    },
    "mokko": {
        "name": "Mokko (Portfolio)",
        "url": "https://madsparkstudio.com/themes/mokko/?storefront=envato-elements",
        "colors": {
            "primary": "#97ea90",
            "bg": "#0a0a0a",
            "light": "#f2f2f2",
            "text": "#e8e8e8",
            "muted": "#666666",
        },
        "typography": {
            "display": {"family": "Neue Montreal", "weight": 700, "size_hero": 60},
            "body": {"family": "Inter", "weight": 300, "size": 15},
            "label": {"family": "Inter", "weight": 500, "size": 10, "uppercase": True},
        },
        "layout": {
            "style": "dark_fullpage_slider",
            "hero_height": 800,
            "card_radius": 6,
            "card_shadow": "0 0 40px rgba(151,234,144,0.15)",
            "button_style": "ghost_green",
            "button_radius": 6,
            "section_padding_v": 140,
            "col_gap": 40,
        },
        "vibe": "dark elegance — full-page slider, green neon accent, dark mode first",
    },
    "jackryan": {
        "name": "Jack Ryan (Portfolio)",
        "url": "https://madsparkstudio.com/themes/jackryan/?storefront=envato-elements",
        "colors": {
            "primary": "#1258ca",
            "bg": "#263654",
            "light": "#ffffff",
            "text": "#ffffff",
            "muted": "#a0aec0",
        },
        "typography": {
            "display": {"family": "Bebas Neue", "weight": 400, "size_hero": 72},
            "body": {"family": "Roboto", "weight": 400, "size": 15},
            "label": {"family": "Roboto Mono", "weight": 400, "size": 10, "uppercase": True},
        },
        "layout": {
            "style": "navy_hero",
            "hero_height": 650,
            "card_radius": 8,
            "card_shadow": "0 8px 32px rgba(0,0,0,0.20)",
            "button_style": "sharp_blue",
            "button_radius": 4,
            "section_padding_v": 100,
            "col_gap": 30,
        },
        "vibe": "military precision — navy blue, Bebas Neue display, Roboto Mono accents",
    },
    "siberia": {
        "name": "Siberia (Portfolio)",
        "url": "https://madsparkstudio.com/themes/siberia/?storefront=envato-elements",
        "colors": {
            "primary": "#2458f3",
            "bg": "#3a3d4f",
            "light": "#ffffff",
            "text": "#e8e9ef",
            "muted": "#9097b1",
        },
        "typography": {
            "display": {"family": "Inter", "weight": 800, "size_hero": 58},
            "body": {"family": "Inter", "weight": 400, "size": 15},
            "label": {"family": "Inter", "weight": 600, "size": 10, "uppercase": True},
        },
        "layout": {
            "style": "slate_card_grid",
            "hero_height": 600,
            "card_radius": 12,
            "card_shadow": "0 8px 40px rgba(36,88,243,0.15)",
            "button_style": "blue_fill",
            "button_radius": 8,
            "section_padding_v": 90,
            "col_gap": 28,
        },
        "vibe": "deep blue slate — electric blue accent, dark card grids, Inter heavy",
    },
    "emilynolan": {
        "name": "EmilyNolan (Photography)",
        "url": "https://madsparkstudio.com/themes/emilynolan/?storefront=envato-elements",
        "colors": {
            "primary": "#df1f29",
            "bg": "#151515",
            "light": "#f5f5f5",
            "text": "#ffffff",
            "muted": "#888888",
        },
        "typography": {
            "display": {"family": "Yantramanav", "weight": 900, "size_hero": 68},
            "body": {"family": "Inter", "weight": 300, "size": 14},
            "label": {"family": "Inter", "weight": 500, "size": 10, "uppercase": True},
        },
        "layout": {
            "style": "photo_dark_fullbleed",
            "hero_height": 900,
            "card_radius": 0,
            "card_shadow": "none",
            "button_style": "red_fill",
            "button_radius": 0,
            "section_padding_v": 120,
            "col_gap": 4,
        },
        "vibe": "raw photography — full-bleed dark, red accent, tight image grid",
    },
}


def main():
    parser = argparse.ArgumentParser(description="WP Reference extractor")
    parser.add_argument("--theme", default="most",
                        choices=list(THEMES.keys()), help="ThemeForest theme to use as reference")
    args = parser.parse_args()

    theme = THEMES[args.theme]

    pipeline_dir = project_root / "exports/pipeline"
    pipeline_dir.mkdir(parents=True, exist_ok=True)

    out_path = pipeline_dir / "wp_reference.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(theme, f, indent=2, ensure_ascii=False)

    print(f"✅ wp_reference.json — theme: {theme['name']}")
    print(f"   Primary: {theme['colors']['primary']}")
    print(f"   Display font: {theme['typography']['display']['family']} {theme['typography']['display']['weight']}")
    print(f"   Layout: {theme['layout']['style']}")
    print(f"   Vibe: {theme['vibe']}")
    print(f"\nAvailable themes: {', '.join(THEMES.keys())}")


if __name__ == "__main__":
    main()
