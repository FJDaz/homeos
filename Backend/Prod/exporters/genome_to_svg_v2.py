#!/usr/bin/env python3
"""
genome_to_svg_v2.py — Mission 21B Genome Design Bridge avec Layout Zones
Génère un SVG scaffold organisé en zones (Header, Sidebar, Main, Footer, Floating).

Usage CLI:
  python genome_to_svg_v2.py --output exports/genome_scaffold.svg

Nouveautés:
- Analyse intelligente des composants par visual_hint
- Organisation en zones UI réalistes
- Z-index pour overlays/dialogues
"""

import json
import math
import os
import re
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional

try:
    from openai import OpenAI
    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False

import sys
sys.path.insert(0, os.path.dirname(__file__))
try:
    from archetype_renderers import render_organ
except ImportError:
    render_organ = None

# Layout constants (px)
ARTBOARD_W = 1440
ARTBOARD_H = 900
COL_GAP = 32      # espacement entre organes

# App shell constants
APP_MARGIN   = 40
APP_HEADER_H = 48
APP_SIDEBAR_W = 188
APP_SIDEBAR_GAP = 16

# Legacy (gardés pour _render_organ_zones fallback)
COL_W = 420
N_COLS = 3
START_X = 40
START_Y = 60
ZONE_HEADER_H = 50
ZONE_SIDEBAR_W = 100
ZONE_FOOTER_H = 40
ZONE_GAP = 12

# Codes courts des phases AetherFlow / HomeOS
_PHASE_CODES = {
    'n0_brainstorm': 'BRS',
    'n0_backend':    'BKS',
    'n0_frontend':   'FRD',
    'n0_deploy':     'DPL',
}

def _phase_code(phase_id, phase_name):
    return _PHASE_CODES.get(phase_id, phase_name[:3].upper())

# Couleurs
COL_ORGAN_BG    = '#f7f6f2'
COL_ORGAN_STR   = '#d5d4d0'
COL_ZONE_HEADER = '#e8e7e3'
COL_ZONE_SIDEBAR = '#f0efeb'
COL_ZONE_MAIN   = '#ffffff'
COL_ZONE_FOOTER = '#e8e7e3'
COL_FLOATING    = '#ffffff'
COL_FEAT_BG     = '#ffffff'
COL_FEAT_STR    = '#e8e7e3'
COL_COMP_BG     = '#f5f5f5'
COL_COMP_STR    = '#d5d4d0'
COL_TEXT_MAIN   = '#3d3d3c'
COL_TEXT_SUB    = '#9d9c98'
COL_TEXT_HINT   = '#b5b4b0'
COL_ACCENT      = '#a8c5fc'
FONT            = '-apple-system, Helvetica, Arial, sans-serif'

# Classification des composants par zone
ZONE_MAPPINGS = {
    'header': [
        'breadcrumb', 'stepper', 'nav', 'navigation', 'tabs', 'menu', 
        'toolbar', 'header', 'topbar', 'brand', 'logo', 'search-bar',
        'command-palette', 'quick-actions'
    ],
    'sidebar': [
        'sidebar', 'nav-tree', 'file-tree', 'menu-list', 'filter-panel',
        'settings-panel', 'tool-panel', 'layers', 'outline', 'index'
    ],
    'main': [
        'editor', 'code-editor', 'preview', 'viewer', 'canvas', 'workspace',
        'dashboard', 'table', 'list', 'grid', 'cards', 'gallery',
        'form', 'input', 'textarea', 'select', 'upload', 'dropzone',
        'chart', 'graph', 'diagram', 'map', 'timeline', 'calendar'
    ],
    'footer': [
        'footer', 'status-bar', 'info-bar', 'pagination', 'actions-bar',
        'bottom-actions', 'copyright', 'meta-info'
    ],
    'floating': [
        'modal', 'dialog', 'popup', 'tooltip', 'toast', 'notification',
        'snackbar', 'dropdown', 'popover', 'chat', 'chat-bubble',
        'assistant', 'ai-panel', 'help', 'onboarding', 'tour'
    ]
}


def _esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('"', '&quot;')


def _rect(x, y, w, h, fill, stroke, rx=6, stroke_width=1):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" rx="{rx}"/>')


def _text(x, y, content, size=10, fill=COL_TEXT_MAIN, anchor='start', weight='normal'):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}" '
            f'font-family="{FONT}">{_esc(content)}</text>')


def _classify_component(comp: Dict) -> str:
    """Classifie un composant N3 dans une zone selon son visual_hint."""
    hint = comp.get('visual_hint', '').lower()
    name = comp.get('name', '').lower()
    
    # Vérifier chaque zone
    for zone, keywords in ZONE_MAPPINGS.items():
        for kw in keywords:
            if kw in hint or kw in name:
                return zone
    
    # Défaut: main pour la plupart, floating si contient certains mots
    if any(w in hint or w in name for w in ['overlay', 'float', 'hover', 'click']):
        return 'floating'
    return 'main'


def _organize_components(n3_all: List[Dict]) -> Dict[str, List[Dict]]:
    """Organise les composants par zone."""
    zones = {'header': [], 'sidebar': [], 'main': [], 'footer': [], 'floating': []}
    for comp in n3_all:
        zone = _classify_component(comp)
        zones[zone].append(comp)
    return zones


def _load_kimi_key():
    env_path = Path(__file__).parent.parent.parent.parent / '.env'
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith('KIMI_KEY='):
                return line.split('=', 1)[1].strip()
    return os.environ.get('KIMI_KEY')


_STYLE_LIBRARY_PATH = (
    Path(__file__).parent.parent.parent.parent
    / 'docs' / '02_Sullivan' / 'Composants' / 'style_prompts_library.json'
)
_STYLE_LIBRARY = None


def _load_style_library():
    global _STYLE_LIBRARY
    if _STYLE_LIBRARY is None and _STYLE_LIBRARY_PATH.exists():
        _STYLE_LIBRARY = json.loads(_STYLE_LIBRARY_PATH.read_text(encoding='utf-8'))
    return _STYLE_LIBRARY


def _build_zone_prompt(zones: Dict[str, List[Dict]], organ_name: str) -> str:
    """Construit une description des zones pour le prompt KIMI."""
    parts = []
    
    if zones['header']:
        comps = ', '.join(f"{c.get('name')} ({c.get('visual_hint')})" for c in zones['header'])
        parts.append(f"HEADER (top): {comps}")
    
    if zones['sidebar']:
        comps = ', '.join(f"{c.get('name')} ({c.get('visual_hint')})" for c in zones['sidebar'])
        parts.append(f"SIDEBAR (left): {comps}")
    
    if zones['main']:
        comps = ', '.join(f"{c.get('name')} ({c.get('visual_hint')})" for c in zones['main'])
        parts.append(f"MAIN CONTENT (center): {comps}")
    
    if zones['footer']:
        comps = ', '.join(f"{c.get('name')} ({c.get('visual_hint')})" for c in zones['footer'])
        parts.append(f"FOOTER (bottom): {comps}")
    
    if zones['floating']:
        comps = ', '.join(f"{c.get('name')} ({c.get('visual_hint')})" for c in zones['floating'])
        parts.append(f"FLOATING/OVERLAYS (absolute positioned, z-index): {comps}")
    
    return '\n'.join(parts)


def _get_style_prompt(style_id, organ, n3_all, hints):
    """Retourne le prompt KIMI avec organisation en zones."""
    lib = _load_style_library()
    
    # Organiser les composants en zones
    zones = _organize_components(n3_all)
    zones_desc = _build_zone_prompt(zones, organ.get('name', ''))
    
    # Compter les composants par zone
    zone_counts = {k: len(v) for k, v in zones.items() if v}
    density = 'dense' if len(n3_all) >= 6 else 'medium' if len(n3_all) >= 3 else 'light'
    
    if lib:
        style = next((s for s in lib.get('styles', []) if s['id'] == style_id), None)
        if style:
            tpl = style['prompt_template']
            comp_list = ', '.join(
                f"{c.get('name','?')} ({c.get('visual_hint','?')})" for c in n3_all
            )
            
            # Construction du prompt enrichi avec zones
            prompt = f"""Tu es un designer UI expert en SVG natif pour Illustrator.
Génère le layout SVG interne d'une carte organe AetherFlow avec ORGANISATION EN ZONES UI.

Organe : {organ.get('id', '')} — "{organ.get('name', '')}"
Total composants : {len(n3_all)} (densité {density})

📐 STRUCTURE DES ZONES:
{zones_desc}

🎨 Contraintes:
- Largeur disponible : 400px. Hauteur : libre (min 150px).
- ORGANISATION: Header en haut (full width), Sidebar à gauche (si présente), Main au centre, Footer en bas.
- FLOATING: Les overlays/dialogues/chat doivent être en position:absolute avec z-index supérieur (derniers dans le SVG).
- Sidebar width: ~80px, Header height: ~40px, Footer height: ~30px.
- PAS de <style>, <script>, <defs>, <svg> racine.
- Palette : fond=#f7f6f2, header=#e8e7e3, sidebar=#f0efeb, main=#ffffff, footer=#e8e7e3, floating=#ffffff, accent=#a8c5fc.
- rx="6" sur les rects, rx="10" sur la carte entière.
- Font : -apple-system,Helvetica,sans-serif
- Labels courts (max 20 chars), lisibles à 10px.
- Chaque composant a un attribut data-hint="<visual_hint>".
- Composants principaux (éditeurs, canvas) avec fill accent (#a8c5fc).
- CONNECTEURS: lignes fines entre composants liés si pertinent.

🔧 CRITIQUE XML:
- Guillemets doubles UNIQUEMENT pour tous les attributs SVG.
- Jamais d'apostrophes simples dans les attributs.
- Les valeurs texte dans data-* doivent être en anglais.

Répondre UNIQUEMENT avec du JSON valide:
{{"h": <hauteur_totale_int>, "svg": "<g>...SVG interne...</g>"}}"""
            return prompt

    # Fallback prompt générique enrichi
    comp_list = ', '.join(f"{c.get('name','?')} ({c.get('visual_hint','?')})" for c in n3_all)
    return f"""Tu es un designer UI expert en SVG natif pour Illustrator.
Génère le layout SVG interne d'une carte organe AetherFlow.

Organe : {organ.get('id')} — "{organ.get('name')}"
Composants ({len(n3_all)}, densité {density}) : {comp_list}

📐 STRUCTURE EN ZONES:
{zones_desc}

Contraintes : Largeur 400px, hauteur libre (min 150px), coordonnées relatives à (0,0).
ORGANISATION: Header (haut), Sidebar (gauche si présente), Main (centre), Footer (bas), Floating (overlay z-index).
PAS de <style>, <script>, <defs>, <svg> racine.
Palette : fond=#f7f6f2, feature bg=#ffffff, stroke=#d5d4d0, texte=#3d3d3c, accent=#a8c5fc.
rx="6" rects, rx="10" carte. Labels courts anglais. data-hint="<visual_hint>" par composant.
CRITIQUE XML : guillemets doubles UNIQUEMENT. Pas d'apostrophes dans les attributs.
Répondre JSON strict : {{"h": int, "svg": "<g>...</g>"}}"""


def _kimi_organ_svg(organ, style_id='auto'):
    """Appelle KIMI pour obtenir un SVG layout organisé en zones."""
    if not _OPENAI_AVAILABLE:
        return None
    key = _load_kimi_key()
    if not key:
        return None

    if style_id == 'auto':
        style_id = 'minimal'
    
    n2_list = organ.get('n2_features', [])
    n3_all = [c for f in n2_list for c in f.get('n3_components', [])]
    hints = [c.get('visual_hint', '?') for c in n3_all]
    
    # Analyse des zones pour log
    zones = _organize_components(n3_all)
    zone_info = ', '.join(f"{k}:{len(v)}" for k, v in zones.items() if v)
    
    prompt = _get_style_prompt(style_id, organ, n3_all, hints)
    print(f'  [KIMI] {organ.get("id")} style={style_id} zones=[{zone_info}]...')

    try:
        client = OpenAI(api_key=key, base_url='https://api.moonshot.ai/v1')
        resp = client.chat.completions.create(
            model='moonshot-v1-8k',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.4,
            max_tokens=1500,
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r'^```json\s*|\s*```$', '', raw, flags=re.MULTILINE).strip()
        data = json.loads(raw)
        svg = data.get('svg', '')
        svg = re.sub(r"(\w[\w-]*)='([^']*)'", lambda m: f'{m.group(1)}="{m.group(2)}"', svg)
        return svg, max(150, min(800, int(data.get('h', 200))))
    except Exception as e:
        print(f'  [KIMI] {organ.get("id")} échec : {e}')
        return None


def _render_component_zone(comps: List[Dict], x: float, y: float, w: float, 
                           zone_type: str, is_vertical: bool = False) -> Tuple[str, float]:
    """Rend une zone de composants (header, sidebar, main, footer)."""
    if not comps:
        return '', 0
    
    lines = []
    comp_h = 32
    gap = 6
    padding = 8
    
    # Couleur de fond selon la zone
    zone_colors = {
        'header': COL_ZONE_HEADER,
        'sidebar': COL_ZONE_SIDEBAR,
        'main': COL_ZONE_MAIN,
        'footer': COL_ZONE_FOOTER,
        'floating': COL_FLOATING
    }
    bg_color = zone_colors.get(zone_type, COL_FEAT_BG)
    
    # Calculer la hauteur/largeur
    if is_vertical:
        # Sidebar verticale
        total_h = padding * 2 + len(comps) * (comp_h + gap) - gap
        total_w = w
    else:
        # Horizontal (header, footer, main)
        total_h = padding * 2 + comp_h if len(comps) <= 2 else padding * 2 + len(comps) * (comp_h + gap) - gap
        total_w = w
    
    # Zone background
    lines.append(_rect(x, y, total_w, total_h, bg_color, 
                       COL_ORGAN_STR if zone_type != 'floating' else COL_ACCENT,
                       rx=4 if zone_type != 'floating' else 8,
                       stroke_width=2 if zone_type == 'floating' else 1))
    
    # Label de zone
    if zone_type != 'main':
        lines.append(_text(x + padding, y + 12, zone_type.upper(), size=7, 
                          fill=COL_TEXT_SUB, weight='600'))
    
    # Composants
    cx, cy = x + padding, y + padding + (12 if zone_type != 'main' else 0)
    
    for comp in comps:
        gid = _esc(comp.get('id', ''))
        name = comp.get('name', gid)
        hint = comp.get('visual_hint', 'component')
        
        comp_w = total_w - padding * 2
        
        if is_vertical:
            comp_w = total_w - padding * 2
        else:
            # Si plusieurs composants en horizontal, les répartir
            if len(comps) <= 3 and not is_vertical:
                comp_w = (total_w - padding * 2 - gap * (len(comps) - 1)) // max(1, len(comps))
        
        lines.append(f'<g id="{gid}" class="af-component" data-genome-id="{gid}" data-hint="{_esc(hint)}" data-zone="{zone_type}">')
        lines.append(_rect(cx, cy, comp_w, comp_h, COL_COMP_BG, COL_COMP_STR, rx=4))
        lines.append(_text(cx + 6, cy + 12, hint, size=7, fill=COL_TEXT_HINT))
        lines.append(_text(cx + 6, cy + 24, name[:20], size=9, fill=COL_TEXT_MAIN, weight='500'))
        lines.append('</g>')
        
        if is_vertical:
            cy += comp_h + gap
        else:
            if len(comps) <= 3:
                cx += comp_w + gap
            else:
                cy += comp_h + gap
    
    return '\n'.join(lines), total_h


def _render_organ_zones(organ, x, y, w):
    """Rend un organe avec layout en zones."""
    n2_list = organ.get('n2_features', [])
    n3_all = [c for f in n2_list for c in f.get('n3_components', [])]
    
    if not n3_all:
        return _render_organ_fallback(organ, x, y, w)
    
    # Organiser en zones
    zones = _organize_components(n3_all)
    
    gid = _esc(organ.get('id', ''))
    name = organ.get('name', gid)
    
    lines = [f'<g id="{gid}" class="af-organ" data-genome-id="{gid}" data-name="{_esc(name)}">']
    
    # Container principal
    has_sidebar = len(zones['sidebar']) > 0
    sidebar_w = 90 if has_sidebar else 0
    
    # Calculer hauteur estimée
    header_h = 45 if zones['header'] else 0
    footer_h = 35 if zones['footer'] else 0
    main_h = max(100, len(zones['main']) * 38 + 20) if zones['main'] else 60
    total_h = header_h + main_h + footer_h + ZONE_GAP * 2 + 30  # +30 pour padding
    
    # Fond de l'organe
    lines.append(_rect(x, y, w, total_h, COL_ORGAN_BG, COL_ORGAN_STR, rx=10))
    
    label = organ.get('display_label') or f'{gid} / {name}'
    role  = organ.get('ui_role', '')
    
    lines.append(_text(x + 12, y + 18, label, size=11, fill=COL_TEXT_MAIN, weight='600'))
    if role and role != 'unknown':
        lines.append(_text(x + 12, y + 30, f'[{role}]', size=8, fill=COL_TEXT_SUB))
    
    # Zone de contenu
    content_y = y + 30
    content_x = x + 10
    content_w = w - 20
    
    cy = content_y
    
    # HEADER
    if zones['header']:
        svg, h = _render_component_zone(zones['header'], content_x, cy, content_w, 'header')
        lines.append(svg)
        cy += h + ZONE_GAP
    
    # SIDEBAR + MAIN côte à côte
    if has_sidebar:
        # Sidebar à gauche
        svg_side, h_side = _render_component_zone(zones['sidebar'], content_x, cy, sidebar_w, 'sidebar', is_vertical=True)
        lines.append(svg_side)
        
        # Main à droite
        main_w = content_w - sidebar_w - ZONE_GAP
        svg_main, h_main = _render_component_zone(zones['main'], content_x + sidebar_w + ZONE_GAP, cy, main_w, 'main')
        lines.append(svg_main)
        
        cy += max(h_side, h_main) + ZONE_GAP
    else:
        # Main seul
        if zones['main']:
            svg_main, h_main = _render_component_zone(zones['main'], content_x, cy, content_w, 'main')
            lines.append(svg_main)
            cy += h_main + ZONE_GAP
    
    # FOOTER
    if zones['footer']:
        svg, h = _render_component_zone(zones['footer'], content_x, cy, content_w, 'footer')
        lines.append(svg)
        cy += h
    
    # FLOATING (dernier, z-index visuel via ordre SVG)
    if zones['floating']:
        # Position flottante centrée
        float_y = content_y + 30
        float_x = content_x + content_w // 4
        float_w = content_w // 2
        svg, h = _render_component_zone(zones['floating'], float_x, float_y, float_w, 'floating')
        lines.append(svg)
    
    lines.append('</g>')
    return '\n'.join(lines), total_h


def _render_organ_fallback(organ, x, y, w):
    """Fallback si pas de composants."""
    gid = _esc(organ.get('id', ''))
    name = organ.get('name', gid)
    h = 100
    
    lines = [
        f'<g id="{gid}" class="af-organ" data-genome-id="{gid}" data-name="{_esc(name)}">',
        _rect(x, y, w, h, COL_ORGAN_BG, COL_ORGAN_STR, rx=10),
        _text(x + 12, y + 18, f'{gid} / {name}', size=11, fill=COL_TEXT_MAIN, weight='600'),
        _text(x + 12, y + 40, '(no components)', size=10, fill=COL_TEXT_SUB),
        '</g>'
    ]
    return '\n'.join(lines), h


def _render_n1(organ, x, y, use_kimi=False, style_id='auto'):
    """Rend un organe N1 (avec ou sans KIMI)."""
    gid = _esc(organ.get('id', ''))
    name = _esc(organ.get('display_label', organ.get('name', gid)))
    col_span = organ.get('col_span', 1)
    w = COL_W * col_span + COL_GAP * (col_span - 1)
    
    if use_kimi:
        result = _kimi_organ_svg(organ, style_id=style_id)
        if result:
            svg_inner, kimi_h = result
            print(f'  [KIMI] {organ.get("id")} → {kimi_h}px ✓')
            lines = [
                f'<g id="{gid}" class="af-organ" data-genome-id="{gid}" data-name="{name}">',
                _rect(x, y, w, kimi_h, COL_ORGAN_BG, COL_ORGAN_STR, rx=10),
                _text(x + 12, y + 18, name, size=11, fill=COL_TEXT_MAIN, weight='600'),
                f'<g transform="translate({x},{y + 30})">',
                svg_inner,
                '</g>',
                '</g>',
            ]
            return '\n'.join(lines), kimi_h
        print(f'  [KIMI] {organ.get("id")} → fallback statique')
    
    # Utiliser le renderer d'archétype si disponible
    if render_organ:
        return render_organ(organ, x, y, w)
    
    # Fallback layout en zones statique legacy
    return _render_organ_zones(organ, x, y, w)


def _draw_app_shell(offset_y, total_h, active_id, all_phases, phase_name, organs):
    """Dessine le shell complet : artboard bg + header nav + sidebar organ list."""
    lines = []
    C = '#3d3d3c'
    C_SUB = '#9d9c98'
    C_ACCENT = '#a8c5fc'

    # Artboard background
    lines.append(f'<rect x="0" y="{offset_y}" width="{ARTBOARD_W}" height="{total_h}" fill="#f7f6f2"/>')

    # ── HEADER NAV ──────────────────────────────────────────────────────────
    lines.append(f'<rect x="0" y="{offset_y}" width="{ARTBOARD_W}" height="{APP_HEADER_H}" fill="#e8e7e3" stroke="#d5d4d0" stroke-width="1"/>')

    # Logo
    lx = APP_MARGIN
    lines.append(f'<rect x="{lx}" y="{offset_y+10}" width="28" height="28" fill="{C}" rx="4"/>')
    lines.append(_text(lx + 8, offset_y + 29, 'AF', 11, '#ffffff', weight='700'))

    # Phase tabs
    tx = lx + 44
    for ph in all_phases:
        code = _phase_code(ph.get('id', ''), ph.get('name', ''))
        active = ph.get('id') == active_id
        tw = len(code) * 9 + 24
        tf = C if active else 'none'
        tc = '#ffffff' if active else C_SUB
        lines.append(f'<rect x="{tx}" y="{offset_y+13}" width="{tw}" height="22" fill="{tf}" rx="11"/>')
        lines.append(_text(tx + tw // 2, offset_y + 28, code, 9, tc, 'middle', '600'))
        tx += tw + 8

    # Séparateur vertical
    lines.append(f'<line x1="{tx+4}" y1="{offset_y+14}" x2="{tx+4}" y2="{offset_y+34}" stroke="#d5d4d0" stroke-width="1"/>')

    # Avatar user (placeholder)
    ax = ARTBOARD_W - APP_MARGIN - 16
    lines.append(f'<circle cx="{ax}" cy="{offset_y+24}" r="14" fill="#d5d4d0" stroke="#b5b4b0" stroke-width="1"/>')
    lines.append(_text(ax, offset_y + 28, 'FJD', 7, C, 'middle'))

    # ── SIDEBAR ─────────────────────────────────────────────────────────────
    sb_x = APP_MARGIN
    sb_y = offset_y + APP_HEADER_H
    sb_h = total_h - APP_HEADER_H
    lines.append(f'<rect x="{sb_x}" y="{sb_y}" width="{APP_SIDEBAR_W}" height="{sb_h}" fill="#f0efeb" stroke="#d5d4d0" stroke-width="1"/>')

    # Titre section
    lines.append(_text(sb_x + 12, sb_y + 20, phase_name.upper(), 7, C_SUB, weight='600'))

    for i, organ in enumerate(organs):
        oy = sb_y + 34 + i * 36
        is_first = (i == 0)
        if is_first:
            lines.append(f'<rect x="{sb_x+6}" y="{oy-4}" width="{APP_SIDEBAR_W-12}" height="30" fill="{C_ACCENT}" rx="4"/>')
        icon_fill = C if is_first else '#d5d4d0'
        lines.append(f'<rect x="{sb_x+12}" y="{oy+5}" width="14" height="14" fill="{icon_fill}" rx="3"/>')
        label = organ.get('name', organ.get('id', ''))[:18]
        tc = C if is_first else C_SUB
        lines.append(_text(sb_x + 32, oy + 17, label, 9, tc))

    return '\n'.join(lines)


def _render_n0(phase, all_phases=None, offset_y=0, use_kimi=False, style_id='auto'):
    """Génère le SVG d'une phase N0 comme wireframe page complète (shell + main 2-col)."""
    gid    = phase.get('id', '')
    name   = phase.get('name', gid)
    organs = phase.get('n1_sections', [])
    if all_phases is None:
        all_phases = [phase]

    # Dimensions main content area
    MAIN_X  = APP_MARGIN + APP_SIDEBAR_W + APP_SIDEBAR_GAP
    MAIN_W  = ARTBOARD_W - MAIN_X - APP_MARGIN
    COL2_W  = (MAIN_W - COL_GAP) // 2

    # Pré-estimation hauteur : 2 col × 280px/ligne
    n_rows     = math.ceil(len(organs) / 2) if organs else 1
    total_h    = max(ARTBOARD_H, APP_HEADER_H + 24 + n_rows * 280 + 40)

    lines = [
        f'<!-- Phase: {_esc(name)} -->',
        f'<g id="{_esc(gid)}" class="af-phase" data-genome-id="{_esc(gid)}" data-name="{_esc(name)}">',
        _draw_app_shell(offset_y, total_h, gid, all_phases, name, organs),
    ]

    # ── MAIN CONTENT — grille 2-col avec archetype renderers ────────────────
    cy = offset_y + APP_HEADER_H + 24
    row_max_h = 0

    for i, organ in enumerate(organs):
        col = i % 2
        if col == 0 and i > 0:
            cy += row_max_h + COL_GAP
            row_max_h = 0
        cx = MAIN_X + col * (COL2_W + COL_GAP)

        if render_organ:
            svg_organ, organ_h = render_organ(organ, cx, cy, COL2_W)
        else:
            svg_organ, organ_h = _render_organ_zones(organ, cx, cy, COL2_W)

        lines.append(svg_organ)
        row_max_h = max(row_max_h, organ_h)

    lines.append('</g>')
    return '\n'.join(lines), offset_y + total_h


def generate_svg(genome, use_kimi=False, style_id='auto'):
    """Génère un SVG scaffold — 1 artboard complet par phase (header+sidebar+main)."""
    phases  = genome.get('n0_phases', [])

    # Passe 1 : calculer les hauteurs pour le viewBox total
    phase_heights = []
    for ph in phases:
        organs = ph.get('n1_sections', [])
        n_rows = math.ceil(len(organs) / 2) if organs else 1
        phase_heights.append(max(ARTBOARD_H, APP_HEADER_H + 24 + n_rows * 280 + 40))

    total_h = sum(phase_heights)

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!-- AetherFlow Genome Scaffold v3 — App Wireframe (header+sidebar+main) -->',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ARTBOARD_W}" height="{total_h}">',
        f'  <defs><style>text {{ font-family: {FONT}; }}</style></defs>',
    ]

    offset = 0
    for i, phase in enumerate(phases):
        phase_svg, next_offset = _render_n0(
            phase, all_phases=phases, offset_y=offset,
            use_kimi=use_kimi, style_id=style_id
        )
        parts.append(phase_svg)
        offset = next_offset

    parts.append('</svg>')
    return '\n'.join(parts)


def main():
    parser = argparse.ArgumentParser(description='AetherFlow Genome → SVG scaffold (v2 avec zones)')
    parser.add_argument('--genome', default=None, help='Chemin vers genome_reference.json')
    parser.add_argument('--output', default='exports/genome_scaffold_zones.svg', help='Chemin de sortie SVG')
    parser.add_argument('--kimi', action='store_true', help='Utiliser KIMI pour des layouts fancy')
    parser.add_argument('--style', default='auto', help='Style KIMI : minimal, glassmorphism, swiss, dark_mode...')
    args = parser.parse_args()
    
    if args.genome:
        genome_path = Path(args.genome)
    else:
        base = Path(__file__).parent.parent.parent.parent
        genome_path = base / 'Frontend' / '2. GENOME' / 'genome_reference.json'
    
    with open(genome_path, 'r', encoding='utf-8') as f:
        genome = json.load(f)
    
    if args.kimi:
        total_organs = sum(len(p.get('n1_sections', [])) for p in genome.get('n0_phases', []))
        print(f'Mode KIMI activé — {total_organs} organes à générer...')
    
    svg = generate_svg(genome, use_kimi=args.kimi, style_id=args.style)
    
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg, encoding='utf-8')
    
    phases = genome.get('n0_phases', [])
    print(f'SVG généré : {out} ({len(phases)} phases, {len(svg)} chars)')


if __name__ == '__main__':
    main()
