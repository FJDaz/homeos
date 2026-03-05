#!/usr/bin/env python3
"""
genome_to_svg.py — Mission 21A Genome Design Bridge
Génère un SVG scaffold balisé depuis le genome AetherFlow.
Chaque <g> porte l'ID genome → calques nommés dans Illustrator.

Usage CLI:
  python genome_to_svg.py --output exports/genome_scaffold.svg

Import:
  from exporters.genome_to_svg import generate_svg
"""

import json
import os
import re
import argparse
from pathlib import Path

try:
    from openai import OpenAI
    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False

# Layout constants (px)
ARTBOARD_W = 1440
ARTBOARD_H = 900
COL_W = 420       # largeur d'un organe N1
COL_GAP = 40      # espacement entre organes
N_COLS = 3        # organes par ligne
START_X = 40
START_Y = 60
FEAT_PAD = 10
COMP_H = 40
COMP_GAP = 8
HEADER_H = 28
FEAT_HEADER_H = 18

# Couleurs
COL_ORGAN_BG    = '#f7f6f2'
COL_ORGAN_STR   = '#d5d4d0'
COL_FEAT_BG     = '#ffffff'
COL_FEAT_STR    = '#e8e7e3'
COL_COMP_BG     = '#f0efeb'
COL_COMP_STR    = '#c5c4c0'
COL_TEXT_MAIN   = '#3d3d3c'
COL_TEXT_SUB    = '#9d9c98'
COL_TEXT_HINT   = '#b5b4b0'
FONT            = '-apple-system, Helvetica, Arial, sans-serif'


def _esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('"', '&quot;')


def _rect(x, y, w, h, fill, stroke, rx=6):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1" rx="{rx}"/>')


def _text(x, y, content, size=10, fill=COL_TEXT_MAIN, anchor='start', weight='normal'):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}" '
            f'font-family="{FONT}">{_esc(content)}</text>')


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


def _get_style_prompt(style_id, organ, n3_all, hints):
    """Retourne le prompt KIMI en utilisant la bibliothèque de styles si disponible."""
    lib = _load_style_library()
    if lib:
        style = next((s for s in lib.get('styles', []) if s['id'] == style_id), None)
        if style:
            tpl = style['prompt_template']
            # Substitutions manuelles (variables non-standard Python)
            comp_list = ', '.join(
                f"{c.get('name','?')} ({c.get('visual_hint','?')})" for c in n3_all
            )
            prompt = (tpl
                .replace('{organ.id}',   organ.get('id', ''))
                .replace('{organ.name}', organ.get('name', ''))
                .replace('{N}',          str(len(n3_all)))
                .replace('[liste]',      comp_list))
            # Append contraintes XML critiques
            prompt += (
                '\nCRITIQUE XML : guillemets doubles UNIQUEMENT pour tous les attributs.'
                ' Pas d\'apostrophes. data-hint en anglais uniquement.'
                '\nRépondre JSON strict : {"h": int, "svg": "<g>...</g>"}'
            )
            return prompt

    # Fallback prompt générique
    density = 'dense' if len(n3_all) >= 5 else 'medium' if len(n3_all) >= 3 else 'light'
    comp_list = ', '.join(f"{c.get('name','?')} ({c.get('visual_hint','?')})" for c in n3_all)
    return f"""Tu es un designer UI expert en SVG natif pour Illustrator.
Génère le layout SVG interne d'une carte organe AetherFlow.
Organe : {organ.get('id')} — "{organ.get('name')}"
Composants ({len(n3_all)}, densité {density}) : {comp_list}
Contraintes : Largeur 400px, hauteur libre (min 120px), coordonnées relatives à (0,0).
Pas de <style>, <script>, <defs>, <svg> racine.
Palette : fond=#f7f6f2, bg=#ffffff, stroke=#d5d4d0, texte=#3d3d3c, accent=#a8c5fc.
rx="6" rects, rx="10" carte. Labels courts anglais. data-hint="<visual_hint>" par composant.
CRITIQUE XML : guillemets doubles UNIQUEMENT. Pas d'apostrophes dans les attributs.
Répondre JSON strict : {{"h": int, "svg": "<g>...</g>"}}"""


def _infer_style(organ):
    """Choisit automatiquement le style KIMI le plus adapté à l'organe
    en fonction de ses visual_hints dominants et de son nom."""
    n2_list = organ.get('n2_features', [])
    hints   = [c.get('visual_hint', '') for f in n2_list for c in f.get('n3_components', [])]
    name    = organ.get('name', '').lower()
    hint_set = set(hints)

    # Règles de mapping hints → style
    if hint_set & {'editor', 'zoom-controls', 'apply-changes'}:
        return 'dark_mode'        # éditeur de code / atome
    if hint_set & {'chat/bubble', 'chat-input'}:
        return 'flat'             # interface conversationnelle
    if hint_set & {'dashboard', 'status', 'table'} and len(hints) >= 3:
        return 'swiss'            # cockpit / données structurées
    if hint_set & {'choice-card', 'card', 'grid'}:
        return 'material'         # sélection / layout
    if hint_set & {'upload', 'preview', 'color-palette'}:
        return 'glassmorphism'    # import / visuel
    if hint_set & {'download', 'modal'}:
        return 'minimal'          # export / confirmation
    if hint_set & {'stepper', 'breadcrumb'}:
        return 'swiss'            # navigation structurée
    if 'analyse' in name or 'arbitrage' in name:
        return 'swiss'
    return 'minimal'              # fallback


def _kimi_organ_svg(organ, style_id='auto'):
    """Appelle KIMI pour obtenir un SVG layout pour un organe N1.
    Retourne (svg_inner: str, h: int) ou None si échec."""
    if not _OPENAI_AVAILABLE:
        return None
    key = _load_kimi_key()
    if not key:
        return None

    if style_id == 'auto':
        style_id = 'minimal'
    n2_list = organ.get('n2_features', [])
    n3_all  = [c for f in n2_list for c in f.get('n3_components', [])]
    hints   = [c.get('visual_hint', '?') for c in n3_all]
    prompt  = _get_style_prompt(style_id, organ, n3_all, hints)
    print(f'  [KIMI] {organ.get("id")} style={style_id}...')

    try:
        client = OpenAI(api_key=key, base_url='https://api.moonshot.ai/v1')
        resp = client.chat.completions.create(
            model='kimi-k2.5',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.4,
            max_tokens=1200,
        )
        raw = resp.choices[0].message.content.strip()
        # Nettoyer éventuel markdown ```json ... ```
        raw = re.sub(r'^```json\s*|\s*```$', '', raw, flags=re.MULTILINE).strip()
        data = json.loads(raw)
        svg  = data.get('svg', '')
        # Safety : convertir les attributs en apostrophes → guillemets doubles
        svg = re.sub(r"(\w[\w-]*)='([^']*)'", lambda m: f'{m.group(1)}="{m.group(2)}"', svg)
        return svg, max(120, min(800, int(data.get('h', 200))))
    except Exception as e:
        print(f'  [KIMI] {organ.get("id")} échec : {e}')
        return None


def _render_n3(comp, x, y, w):
    gid   = _esc(comp.get('id', ''))
    name  = comp.get('name', gid)
    hint  = comp.get('visual_hint', 'component')
    h     = COMP_H
    lines = [
        f'<g id="{gid}" class="af-component" data-genome-id="{gid}" data-hint="{_esc(hint)}">',
        _rect(x, y, w - FEAT_PAD * 2, h, COL_COMP_BG, COL_COMP_STR, rx=4),
        _text(x + 8, y + 13, hint, size=8, fill=COL_TEXT_HINT),
        _text(x + 8, y + 27, name, size=10, fill=COL_TEXT_MAIN, weight='500'),
        '</g>',
    ]
    return '\n'.join(lines), h


def _render_n2(feat, x, y, w):
    gid   = _esc(feat.get('id', ''))
    name  = feat.get('name', gid)
    comps = feat.get('n3_components', [])

    inner_h = FEAT_HEADER_H + FEAT_PAD + (COMP_H + COMP_GAP) * len(comps) + FEAT_PAD
    lines   = [
        f'<g id="{gid}" class="af-feature" data-genome-id="{gid}" data-name="{_esc(name)}">',
        _rect(x, y, w - FEAT_PAD, inner_h, COL_FEAT_BG, COL_FEAT_STR, rx=4),
        _text(x + FEAT_PAD, y + 13, name.upper(), size=8, fill=COL_TEXT_SUB, weight='600'),
    ]
    cy = y + FEAT_HEADER_H + FEAT_PAD
    for comp in comps:
        svg_comp, ch = _render_n3(comp, x + FEAT_PAD, cy, w - FEAT_PAD)
        lines.append(svg_comp)
        cy += ch + COMP_GAP
    lines.append('</g>')
    return '\n'.join(lines), inner_h


def _organ_height(organ):
    """Calcule la hauteur totale d'un organe N1."""
    h = HEADER_H + FEAT_PAD
    for feat in organ.get('n2_features', []):
        n3 = feat.get('n3_components', [])
        h += FEAT_HEADER_H + FEAT_PAD + (COMP_H + COMP_GAP) * len(n3) + FEAT_PAD * 2
    return h + FEAT_PAD


def _render_n1(organ, x, y, use_kimi=False, style_id='auto'):
    gid   = _esc(organ.get('id', ''))
    name  = organ.get('name', gid)
    w     = COL_W

    # Tentative KIMI
    if use_kimi:
        result = _kimi_organ_svg(organ, style_id=style_id)
        if result:
            svg_inner, kimi_h = result
            print(f'  [KIMI] {organ.get("id")} → {kimi_h}px ✓')
            lines = [
                f'<g id="{gid}" class="af-organ" data-genome-id="{gid}" data-name="{_esc(name)}">',
                _rect(x, y, w, kimi_h, COL_ORGAN_BG, COL_ORGAN_STR, rx=10),
                _text(x + 12, y + 18, f'{gid}  /  {name}', size=11, fill=COL_TEXT_MAIN, weight='600'),
                f'<g transform="translate({x},{y + HEADER_H})">',
                svg_inner,
                '</g>',
                '</g>',
            ]
            return '\n'.join(lines), kimi_h

    # Fallback statique
    feats   = organ.get('n2_features', [])
    total_h = _organ_height(organ)
    lines   = [
        f'<g id="{gid}" class="af-organ" data-genome-id="{gid}" data-name="{_esc(name)}">',
        _rect(x, y, w, total_h, COL_ORGAN_BG, COL_ORGAN_STR, rx=8),
        _text(x + 12, y + 18, f'{gid}  /  {name}', size=11, fill=COL_TEXT_MAIN, weight='600'),
    ]
    cy = y + HEADER_H + FEAT_PAD
    for feat in feats:
        svg_feat, fh = _render_n2(feat, x + FEAT_PAD, cy, w - FEAT_PAD)
        lines.append(svg_feat)
        cy += fh + FEAT_PAD
    lines.append('</g>')
    return '\n'.join(lines), total_h


def _render_n0(phase, offset_y=0, use_kimi=False, style_id='auto'):
    """Génère le SVG d'une phase N0 (artboard 1440×900)."""
    gid     = _esc(phase.get('id', ''))
    name    = phase.get('name', gid)
    organs  = phase.get('n1_sections', [])   # ← clé correcte genome

    lines = [
        f'<!-- Phase: {_esc(name)} -->',
        f'<g id="{gid}" class="af-phase" data-genome-id="{gid}" data-name="{_esc(name)}">',
        f'<rect x="0" y="{offset_y}" width="{ARTBOARD_W}" height="{ARTBOARD_H}" fill="#fafaf8"/>',
        _text(20, offset_y + 28, f'Phase : {name}', size=14, fill=COL_TEXT_MAIN, weight='700'),
    ]

    # Rangées dynamiques basées sur la hauteur max par rangée
    row_heights = {}
    for i, organ in enumerate(organs):
        row = i // N_COLS
        h   = _organ_height(organ)
        row_heights[row] = max(row_heights.get(row, 0), h)

    row_y = [offset_y + START_Y]
    for r in range(max(row_heights.keys()) if row_heights else 0):
        row_y.append(row_y[-1] + row_heights.get(r, 0) + COL_GAP)

    for i, organ in enumerate(organs):
        col = i % N_COLS
        row = i // N_COLS
        x   = START_X + col * (COL_W + COL_GAP)
        y   = row_y[row]
        svg_organ, _ = _render_n1(organ, x, y, use_kimi=use_kimi, style_id=style_id)
        lines.append(svg_organ)

    lines.append('</g>')
    return '\n'.join(lines)


def generate_svg(genome, use_kimi=False, style_id='auto'):
    """Génère un SVG scaffold balisé depuis le genome AetherFlow.
    use_kimi=True → appelle KIMI pour chaque organe N1 (plus lent, plus beau).
    Retourne une string SVG."""
    phases  = genome.get('n0_phases', [])
    total_h = ARTBOARD_H * max(len(phases), 1)

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!-- AetherFlow Genome Scaffold — Mission 21A Figma Bridge -->',
        '<!-- Convention: Ne pas renommer les calques af-* dans Illustrator -->',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ARTBOARD_W}" height="{total_h}">',
        f'  <defs><style>text {{ font-family: {FONT}; }}</style></defs>',
    ]
    for i, phase in enumerate(phases):
        parts.append(_render_n0(phase, offset_y=i * ARTBOARD_H, use_kimi=use_kimi, style_id=style_id))
    parts.append('</svg>')
    return '\n'.join(parts)


def main():
    parser = argparse.ArgumentParser(description='AetherFlow Genome → SVG scaffold')
    parser.add_argument('--genome', default=None, help='Chemin vers genome_reference.json')
    parser.add_argument('--output', default='exports/genome_scaffold.svg', help='Chemin de sortie SVG')
    parser.add_argument('--kimi', action='store_true', help='Utiliser KIMI pour des layouts fancy')
    parser.add_argument('--style', default='auto', help='Style KIMI : minimal, brutalist, glassmorphism, swiss, dark_mode, cyberpunk... (voir style_prompts_library.json)')
    args = parser.parse_args()

    if args.genome:
        genome_path = Path(args.genome)
    else:
        base = Path(__file__).parent.parent.parent.parent
        genome_path = base / 'Frontend' / '2. GENOME' / 'genome_reference.json'

    with open(genome_path, 'r', encoding='utf-8') as f:
        genome = json.load(f)

    if args.kimi:
        print(f'Mode KIMI activé — {sum(len(p.get("n1_sections",[])) for p in genome.get("n0_phases",[]))} appels API...')
    svg = generate_svg(genome, use_kimi=args.kimi, style_id=args.style)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg, encoding='utf-8')
    print(f'SVG généré : {out} ({len(phases := genome.get("n0_phases", []))} phases, {len(svg)} chars)')


if __name__ == '__main__':
    main()
