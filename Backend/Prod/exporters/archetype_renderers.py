#!/usr/bin/env python3
"""
archetype_renderers.py — Mission 21E
Renderer topologique : chaque organe est dessiné avec ses vrais
composants N3 (noms réels, visual_hints réels) distribués selon
la topologie ROLE_TO_TOPOLOGY[ui_role] de topology_bank.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from topology_bank import TOPOLOGIES, ROLE_TO_TOPOLOGY

# ── Palette ───────────────────────────────────────────────────────────────────
C_BG      = '#f7f6f2'
C_SURFACE = '#ffffff'
C_BORDER  = '#d5d4d0'
C_TEXT    = '#3d3d3c'
C_SUB     = '#9d9c98'
C_HINT    = '#b5b4b0'
C_ACCENT  = '#a8c5fc'
C_HEADER  = '#e8e7e3'
C_SIDEBAR = '#f0efeb'
C_ACTIVE  = '#3d3d3c'
FONT      = '-apple-system,Helvetica,Arial,sans-serif'

# ── Helpers SVG ───────────────────────────────────────────────────────────────
def _esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('"', '&quot;')

def _r(x, y, w, h, fill, stroke=C_BORDER, rx=4, sw=1, dash=''):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" rx="{rx}"{d}/>')

def _t(x, y, txt, size=9, fill=C_TEXT, anchor='start', weight='normal', clip=0):
    s = _esc(str(txt)[:clip] if clip else str(txt))
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}" '
            f'font-family="{FONT}">{s}</text>')

def _c(cx, cy, r, fill=C_BORDER, stroke='none', sw=1):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>')

def _line(x1, y1, x2, y2, stroke=C_BORDER, sw=1, dash=''):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{stroke}" stroke-width="{sw}"{d}/>')

# ── Atome sémantique ──────────────────────────────────────────────────────────
def _draw_semantic_atom(name, hint, x, y, w, h):
    """
    Dessine un atome SVG selon son visual_hint.
    Utilise UNIQUEMENT le vrai `name` du composant N3 — jamais de valeurs fictives.
    """
    lines = []
    x, y, w, h = int(x), int(y), max(int(w), 40), max(int(h), 24)
    mid_x = x + w // 2

    if hint in ('table', 'table-row'):
        # En-tête + rows alternés
        lines.append(_r(x, y, w, 28, C_HEADER, C_BORDER, rx=4))
        lines.append(_t(x+8, y+18, _esc(name[:20]), 8, C_TEXT, weight='600'))
        row_h = max(22, (h - 28) // 3)
        for i in range(min(3, (h - 28) // row_h)):
            ry = y + 28 + i * row_h
            lines.append(_r(x, ry, w, row_h - 1, C_SURFACE if i % 2 == 0 else C_BG, C_BORDER, rx=0))
            # colonnes simulées
            lines.append(_line(x + w * 2 // 5, ry, x + w * 2 // 5, ry + row_h - 1, C_BORDER))
            lines.append(_line(x + w * 4 // 5, ry, x + w * 4 // 5, ry + row_h - 1, C_BORDER))
            # badge accent sur row 0
            if i == 0:
                lines.append(_r(x + w * 4 // 5 + 4, ry + 4, w // 5 - 8, row_h - 8, C_ACCENT, 'none', rx=8))

    elif hint == 'detail-card':
        lines.append(_r(x, y, w, h, C_SURFACE, C_BORDER, rx=6))
        lines.append(_r(x, y, 4, h, C_ACCENT, 'none', rx=2))
        lines.append(_t(x+12, y+18, _esc(name[:22]), 10, C_TEXT, weight='600'))
        for i in range(2):
            lines.append(_r(x+12, y+26+i*14, w-24, 7, C_BORDER, 'none', rx=2))

    elif hint in ('choice-card', 'card', 'stencil-card'):
        border = C_ACCENT if hint == 'stencil-card' else C_BORDER
        lines.append(_r(x, y, w, h, C_SURFACE, border, rx=6))
        preview_h = max(24, h * 3 // 5)
        lines.append(_r(x+6, y+6, w-12, preview_h, C_BG, C_BORDER, rx=4))
        lines.append(_t(mid_x, y + preview_h + 20, _esc(name[:14]), 9, C_TEXT, 'middle'))

    elif hint in ('chart', 'graph', 'dashboard'):
        lines.append(_r(x, y, w, h, C_SURFACE, C_BORDER, rx=6, dash='4 4'))
        bar_hs = [28, 40, 32, 52, 36]
        bw = max(8, (w - 24) // 5)
        for i, bh in enumerate(bar_hs):
            bh = min(bh, h - 20)
            bx = x + 12 + i * (bw + 4)
            lines.append(_r(bx, y + h - 10 - bh, bw, bh, C_ACCENT, 'none', rx=2))
        lines.append(_t(mid_x, y + h - 3, _esc(name[:16]), 7, C_HINT, 'middle'))

    elif hint in ('button', 'launch-button'):
        btn_h = max(28, h)
        lines.append(_r(x, y, w, btn_h, C_ACTIVE, 'none', rx=16))
        lines.append(_t(mid_x, y + btn_h // 2 + 4, _esc(name[:16]), 9, '#ffffff', 'middle', '600'))

    elif hint == 'status':
        lines.append(_r(x, y, w, h, C_BG, C_BORDER, rx=4))
        lines.append(_c(x + 14, y + h // 2, 5, '#4ade80'))
        lines.append(_t(x + 24, y + h // 2 + 4, _esc(name[:18]), 8, C_SUB))

    elif hint == 'list':
        row_h = max(22, h // 3)
        for i in range(min(3, h // row_h)):
            ry = y + i * row_h
            lines.append(_r(x, ry, w, row_h - 2, C_BG, C_BORDER, rx=2))
            lines.append(_t(x + 8, ry + row_h // 2 + 4, _esc(name[:20]), 8, C_TEXT))

    elif hint == 'accordion':
        row_h = max(32, h // 3)
        for i in range(min(3, h // row_h)):
            ry = y + i * row_h
            lines.append(_r(x, ry, w, row_h - 2, C_HEADER, C_BORDER, rx=2))
            lines.append(_t(x + 10, ry + row_h // 2 + 4, _esc(name[:22]), 9, C_TEXT))
            lines.append(_t(x + w - 14, ry + row_h // 2 + 4, '›', 10, C_SUB, 'middle'))

    elif hint == 'zoom-controls':
        btn_w = min(32, w // 2 - 4)
        lines.append(_r(x, y, btn_w, h, C_SURFACE, C_BORDER, rx=4))
        lines.append(_t(x + btn_w // 2, y + h // 2 + 4, '+', 12, C_TEXT, 'middle'))
        lines.append(_r(x + btn_w + 8, y, btn_w, h, C_SURFACE, C_BORDER, rx=4))
        lines.append(_t(x + btn_w + 8 + btn_w // 2, y + h // 2 + 4, '−', 12, C_TEXT, 'middle'))
        lines.append(_t(mid_x, y + h + 10, _esc(name[:14]), 7, C_HINT, 'middle'))

    elif hint == 'editor':
        lines.append(_r(x, y, w, h, '#1e1e1e', 'none', rx=4))
        code_colors = ['#4ade80', '#a8c5fc', '#f7f6f2']
        for i, col in enumerate(code_colors):
            lw = [w * 3 // 4, w // 2, w * 2 // 3][i]
            lines.append(_r(x + 10, y + 10 + i * 14, lw, 7, col, 'none', rx=2))
        lines.append(_t(x + 4, y + 8, _esc(name[:16]), 7, C_HINT))

    elif hint == 'preview':
        lines.append(_r(x, y, w, h, C_BG, C_BORDER, rx=4, dash='6 4'))
        lines.append(_t(mid_x, y + h // 2 - 4, 'IMG', 10, C_HINT, 'middle'))
        lines.append(_t(mid_x, y + h - 8, _esc(name[:16]), 7, C_HINT, 'middle'))

    elif hint in ('color-palette', 'color'):
        palette = ['#a8c5fc', '#f0efeb', '#3d3d3c', '#4ade80', '#facc15']
        r = min(h // 3, 10)
        for i, col in enumerate(palette):
            cx = x + 12 + i * (r * 2 + 4)
            lines.append(_c(cx, y + h // 2, r, col, C_SURFACE, 1))
        lines.append(_t(mid_x, y + h - 4, _esc(name[:16]), 7, C_HINT, 'middle'))

    elif hint == 'upload':
        lines.append(_r(x, y, w, h, C_BG, C_SUB, rx=6, dash='6 4'))
        lines.append(_t(mid_x, y + h // 2 - 4, '↑', 14, C_SUB, 'middle'))
        lines.append(_t(mid_x, y + h // 2 + 14, _esc(name[:16]), 9, C_TEXT, 'middle', '500'))

    elif hint in ('chat/bubble', 'bubble'):
        bh = max(24, (h - 8) // 2)
        lines.append(_r(x + w // 3, y, w * 2 // 3, bh, C_ACCENT, 'none', rx=10))
        lines.append(_t(x + w // 3 + 8, y + bh // 2 + 4, _esc(name[:10]), 8, C_ACTIVE))
        lines.append(_r(x, y + bh + 8, w * 2 // 3, bh, C_HEADER, C_BORDER, rx=10))
        lines.append(_t(x + 8, y + bh + 8 + bh // 2 + 4, _esc(name[:10]), 8, C_TEXT))

    elif hint == 'chat-input':
        lines.append(_r(x, y, w - 28, h, C_BG, C_BORDER, rx=max(h // 2, 12)))
        lines.append(_t(x + 12, y + h // 2 + 4, _esc(name[:18]), 8, C_HINT))
        lines.append(_c(x + w - 14, y + h // 2, 11, C_ACCENT))

    elif hint == 'stepper':
        n = max(3, min(6, w // 40))
        step_w = (w - 24) // n
        for i in range(n):
            cx = x + 12 + i * step_w + step_w // 2
            lines.append(_c(cx, y + h // 2, 10, C_ACTIVE if i == 0 else C_BORDER, C_BORDER, 1.5))
            lines.append(_t(cx, y + h // 2 + 4, str(i + 1), 8,
                            '#ffffff' if i == 0 else C_SUB, 'middle', '600'))
            if i < n - 1:
                lines.append(_line(cx + 10, y + h // 2, cx + step_w - 10, y + h // 2, C_BORDER))
        lines.append(_t(mid_x, y + h - 4, _esc(name[:16]), 7, C_HINT, 'middle'))

    elif hint == 'breadcrumb':
        lines.append(_t(x + 8, y + h // 2 + 4,
                        f'Phase 1 › Phase 2 › {_esc(name[:10])}', 8, C_SUB))

    elif hint == 'download':
        lines.append(_r(x, y, w, h, C_SURFACE, C_BORDER, rx=6))
        lines.append(_t(mid_x, y + h // 2 - 4, '⬇', 14, C_ACCENT, 'middle'))
        lines.append(_t(mid_x, y + h // 2 + 14, _esc(name[:16]), 9, C_TEXT, 'middle'))
        lines.append(_t(mid_x, y + h - 6, '.zip · Export', 7, C_HINT, 'middle'))

    elif hint == 'modal':
        lines.append(_r(x, y, w, h, C_SURFACE, C_ACCENT, rx=8, sw=2))
        lines.append(_r(x, y, w, 32, C_HEADER, 'none', rx=6))
        lines.append(_t(x + 10, y + 21, _esc(name[:18]), 9, C_TEXT, weight='600'))
        lines.append(_r(x + w - 48, y + h - 28, 40, 20, C_ACTIVE, 'none', rx=4))
        lines.append(_t(x + w - 28, y + h - 13, 'OK', 9, '#ffffff', 'middle', '600'))

    elif hint in ('form', 'form-input'):
        lines.append(_t(x + 8, y + 12, _esc(name[:22]), 8, C_SUB))
        lines.append(_r(x, y + 14, w, max(h - 14, 24), C_BG, C_BORDER, rx=4))
        lines.append(_line(x + 8, y + 20, x + 8, y + h - 4, C_ACCENT, 1.5))

    else:
        # Défaut : bloc nommé générique
        lines.append(_r(x, y, w, h, C_BG, C_BORDER, rx=4))
        lines.append(_t(mid_x, y + h // 2 + 4, _esc(name[:20]), 8, C_TEXT, 'middle'))

    return '\n'.join(lines)


# ── Solver de layout ──────────────────────────────────────────────────────────
def _solve_layout(x, y, w, components, topo_name):
    """
    Distribue les composants N3 dans l'espace selon la topologie.
    Retourne [(comp, cx, cy, cw, ch), ...]
    """
    topo = TOPOLOGIES.get(topo_name, TOPOLOGIES['bento_grid'])
    layout = topo.get('layout', {})
    roles = layout.get('roles', {})
    padding = layout.get('padding', 16)
    layout_type = layout.get('type', 'grid')

    result = []
    cursor_x = x + padding
    cursor_y = y
    row_h = 0

    for comp in components:
        hint = comp.get('visual_hint', 'default')
        # Trouver la config de taille pour ce hint
        role_cfg = roles.get(hint, roles.get('default', {'w': '50%', 'h': 120}))

        # Largeur
        w_spec = role_cfg.get('w', '50%')
        if isinstance(w_spec, str) and w_spec.endswith('%'):
            cw = int(w * float(w_spec[:-1]) / 100) - padding
        else:
            cw = int(w_spec) if isinstance(w_spec, int) else w - 2 * padding

        # Hauteur
        h_spec = role_cfg.get('h', 100)
        ch = int(h_spec) if isinstance(h_spec, int) else 100

        # Retour à la ligne si dépassement (modes grid/masonry)
        if layout_type in ('grid', 'masonry', 'flex-row-columns'):
            if cursor_x + cw > x + w - padding and cursor_x > x + padding:
                cursor_x = x + padding
                cursor_y += row_h + padding
                row_h = 0

        result.append((comp, cursor_x, cursor_y, cw, ch))

        if layout_type in ('flex-col', 'flex-col-centered', 'z-alternating'):
            # Empilement vertical
            cursor_y += ch + padding
        elif layout_type in ('grid', 'masonry', 'flex-row', 'flex-row-columns',
                              'overlay-centered'):
            cursor_x += cw + padding
            row_h = max(row_h, ch)

    return result


# ── Renderer dynamique universel ──────────────────────────────────────────────
def draw_dynamic_organ(organ, x, y, w, components):
    """
    Renderer universel piloté par topology_bank.
    Pas de valeurs fictives — uniquement les données du génome.
    Utilise la stratégie WP-inspired (layout_strategy) prioritairement.
    """
    role = organ.get('ui_role', 'main-content')
    gemini_strategy = organ.get('layout_strategy')
    
    # Priorité: 1. Gemini WP Strategy, 2. Static Mapping, 3. bento_grid
    if gemini_strategy and gemini_strategy in TOPOLOGIES:
        topo_name = gemini_strategy
    else:
        topo_name = ROLE_TO_TOPOLOGY.get(role, 'bento_grid')

    # Calculer la hauteur totale : somme des hauteurs planifiées + padding top
    PAD_TOP = 28
    layout = _solve_layout(x, y + PAD_TOP, w, components, topo_name)

    if layout:
        last = layout[-1]
        h_total = (last[2] - y) + last[4] + 20   # cy - y + ch + bottom margin
    else:
        h_total = 120
    h_total = max(h_total, 80)

    lines = []
    lines.append(_r(x, y, w, h_total, C_SURFACE, C_BORDER, rx=8))
    label = organ.get('display_label', organ.get('name', ''))[:30]
    lines.append(_t(x + 12, y + 18, _esc(label), 7, C_HINT, weight='600'))

    for (comp, cx, cy, cw, ch) in layout:
        atom = _draw_semantic_atom(
            comp.get('name', ''),
            comp.get('visual_hint', 'default'),
            cx, cy, cw, ch
        )
        lines.append(atom)

    return '\n'.join(lines), h_total


# ── Renderers structurels (shells fixes, contenu dynamique) ───────────────────

def draw_nav_header(organ, x, y, w, components):
    lines = []
    lines.append(_r(x, y, w, 56, C_HEADER, C_BORDER, rx=8))
    lines.append(_r(x+12, y+12, 32, 32, C_ACTIVE, rx=4))
    lines.append(_t(x+20, y+33, 'A', 14, '#ffffff', weight='700'))
    for i, comp in enumerate(components[:5]):
        px = x + 56 + i * 76
        lines.append(_r(px, y+16, 68, 24,
                        C_ACTIVE if i == 0 else C_SURFACE, C_BORDER, rx=12))
        lines.append(_t(px+34, y+32, _esc(comp.get('name', '')[:8]), 9,
                        '#ffffff' if i == 0 else C_TEXT, 'middle'))
    lines.append(_c(x+w-28, y+28, 11, 'none', C_SUB, 1.5))
    lines.append(_line(x+w-20, y+36, x+w-16, y+40, C_SUB, 1.5))
    return '\n'.join(lines), 56


def draw_left_sidebar(organ, x, y, w, components):
    h = 48 + len(components) * 40 + 16
    lines = []
    lines.append(_r(x, y, 88, h, C_SIDEBAR, C_BORDER, rx=8))
    lines.append(_t(x+10, y+22, 'MENU', 7, C_SUB, weight='600'))
    for i, comp in enumerate(components):
        ry = y + 36 + i * 40
        if i == 0:
            lines.append(_r(x+4, ry+2, 80, 32, C_ACCENT, C_ACCENT, rx=4))
        lines.append(_r(x+10, ry+8, 16, 16,
                        C_ACTIVE if i == 0 else C_BORDER, rx=3))
        lines.append(_t(x+34, ry+20, _esc(comp.get('name', '')[:14]), 9,
                        C_ACTIVE if i == 0 else C_TEXT))
    return '\n'.join(lines), h


def draw_main_canvas(organ, x, y, w, components):
    h = max(240, 48 + len(components) * 32 + 24)
    lines = []
    lines.append(_r(x, y, w, h, C_SURFACE, C_BORDER, rx=8))
    for gy in range(int(y) + 24, int(y + h), 24):
        lines.append(_line(x+1, gy, x+w-1, gy, '#f0efeb'))
    lines.append(_t(x+12, y+20, 'CANVAS / EDITOR', 7, C_HINT, weight='600'))
    lines.append(_r(x+16, y+32, w-32, h-48, C_BG, C_SUB, rx=4, dash='4 4'))
    lines.append(_t(x+w//2, y+h//2, '[ workspace ]', 9, C_HINT, 'middle'))
    return '\n'.join(lines), h


# ── Dispatcher ────────────────────────────────────────────────────────────────
def render_organ(organ, x, y, w):
    role = organ.get('ui_role', 'unknown')
    components = [c for f in organ.get('n2_features', [])
                  for c in f.get('n3_components', [])]

    if role == 'nav-header':
        svg_body, organ_h = draw_nav_header(organ, x, y, w, components)
    elif role == 'left-sidebar':
        svg_body, organ_h = draw_left_sidebar(organ, x, y, w, components)
    elif role in ('main-canvas',):
        svg_body, organ_h = draw_main_canvas(organ, x, y, w, components)
    else:
        svg_body, organ_h = draw_dynamic_organ(organ, x, y, w, components)

    gid  = organ.get('id', '')
    name = organ.get('display_label', organ.get('name', gid))
    role_str = role if role and role != 'unknown' else ''
    header = (
        f'<g id="{gid}" class="af-organ" data-genome-id="{gid}" '
        f'data-name="{_esc(name)}" data-ui-role="{role_str}" '
        f'data-ux-step="{organ.get("ux_step", "")}">'
    )
    return f'{header}\n{svg_body}\n</g>', organ_h
