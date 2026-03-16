#!/usr/bin/env python3
"""
svg_parser.py — Mission 41B
Parser sémantique pour les exports SVG de Figma.
Extrait les fonts, les couleurs et la structure des groupes sans LLM.
"""

import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Set

def parse_figma_svg(svg_string: str) -> Dict:
    """
    Extrait les signaux sémantiques d'un SVG Figma export.
    Retourne un dict compatible avec le format visual_analysis de analyzer.py.
    """
    # Nettoyage namespace pour faciliter le parsing
    svg_string = re.sub(' xmlns="[^"]+"', '', svg_string, count=1)
    
    try:
        root = ET.fromstring(svg_string)
    except Exception as e:
        return {"error": f"Invalid SVG: {str(e)}", "elements": [], "regions": []}

    fonts: Set[str] = set()
    colors: Set[str] = set()
    elements: List[Dict] = []
    regions: List[Dict] = []

    # 1. Extraction récursive
    def walk(node, current_region_id=None):
        tag = node.tag.split('}')[-1]
        node_id = node.get('id', '')
        
        # Gestion des régions (groupes avec ID)
        if tag == 'g' and node_id:
            region_name = node_id
            # Inférence du rôle structurel
            role = "content"
            name_lower = region_name.lower()
            if "header" in name_lower: role = "header"
            elif "footer" in name_lower: role = "footer"
            elif "sidebar" in name_lower: role = "sidebar"
            elif "nav" in name_lower: role = "header"
            
            region_data = {
                "id": region_name,
                "name": region_name,
                "elements_contained": [],
                "structural_role": role
            }
            regions.append(region_data)
            current_region_id = region_name

        # Extraction des styles (fill, stroke, fonts)
        style = node.get('style', '')

        # Fonts — style inline ET attribut direct
        font_match = re.search(r'font-family:\s*([^;]+)', style)
        if font_match:
            f = font_match.group(1).strip().strip("'").strip('"')
            fonts.add(f)
        direct_font = node.get('font-family')
        if direct_font:
            fonts.add(direct_font.strip().strip("'").strip('"'))

        # Couleurs — attributs directs ET style inline
        for attr in ['fill', 'stroke']:
            val = node.get(attr)
            if val and val.startswith('#'):
                colors.add(val.upper())
        for prop in ['fill', 'stroke']:
            m = re.search(rf'{prop}:\s*(#[0-9a-fA-F]{{3,6}})', style)
            if m:
                colors.add(m.group(1).upper())

        # Éléments terminaux
        if tag in ('text', 'rect', 'circle', 'path', 'ellipse'):
            el_id = node_id or f"{tag}_{len(elements)}"
            
            # Apparent role & hint inference
            role = tag
            hint = f"{tag} shape"
            text_content = None
            
            if tag == 'text':
                role = "text"
                hint = "text label"
                text_content = node.text or "".join(node.itertext())
            elif tag == 'rect':
                role = "box"
                hint = "container"
            
            el_data = {
                "id": el_id,
                "apparent_role": role,
                "visual_hint": hint,
                "text_content": text_content,
                "color_hex": node.get('fill') if node.get('fill', '').startswith('#') else None,
                "description": f"SVG {tag} element extracted from Figma"
            }
            elements.append(el_data)
            
            if current_region_id:
                for r in regions:
                    if r['id'] == current_region_id:
                        r['elements_contained'].append(el_id)
                        break

        for child in node:
            walk(child, current_region_id)

    walk(root)

    # 2. Post-processing Design Tokens
    google_fonts_url = ""
    if fonts:
        families = [f.replace(' ', '+') for f in fonts]
        google_fonts_url = f"https://fonts.googleapis.com/css2?family={'&family='.join(families)}&display=swap"

    sorted_colors = sorted(list(colors))
    return {
        "elements": elements,
        "regions": regions,
        "design_tokens": {
            "fonts": sorted(list(fonts)),
            "google_fonts_import": f"@import url('{google_fonts_url}');" if google_fonts_url else None,
            "colors": sorted_colors,
            "primary_color": sorted_colors[0] if sorted_colors else "#3D3D3C",
            "accent_color": sorted_colors[1] if len(sorted_colors) > 1 else None,
        },
        "source": "figma_svg"
    }

if __name__ == "__main__":
    # Test basique
    sample_svg = """<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
        <g id="Header_Section">
            <rect id="bg" fill="#F0F0F0" x="0" y="0" width="100" height="20" />
            <text style="font-family: 'Playfair Display'; fill: #333333">Hello World</text>
        </g>
    </svg>"""
    result = parse_figma_svg(sample_svg)
    import json
    print(json.dumps(result, indent=2))
