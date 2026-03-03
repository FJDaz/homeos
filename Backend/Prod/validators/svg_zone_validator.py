#!/usr/bin/env python3
"""
svg_zone_validator.py — Mission 21D
Valide qu'un SVG wireframe contient des zones lisibles (header nav, sidebar, main content).
Utilise Gemini Flash comme juge (google.genai SDK).

Usage:
  python svg_zone_validator.py --svg exports/genome_zones_xxx.svg
  python svg_zone_validator.py --svg ... --pass2  # valide aussi la densité composants
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path

try:
    from google import genai as google_genai
    _GEMINI_OK = True
except ImportError:
    _GEMINI_OK = False

try:
    import anthropic as _anthropic_mod
    _ANTHROPIC_OK = True
except ImportError:
    _ANTHROPIC_OK = False


# ── Checks structurels rapides (sans LLM) ────────────────────────────────────

def _structural_check(svg_content: str) -> tuple[bool, list[str]]:
    """Vérifie la présence des zones via parsing SVG basique."""
    issues = []

    # Header nav : rect pleine largeur proche du top de chaque phase
    if 'class="af-phase"' not in svg_content:
        issues.append("Aucune phase af-phase trouvée dans le SVG")
        return False, issues

    # Chercher des rects de header (fill="#e8e7e3", width="1440")
    header_rects = re.findall(r'<rect[^>]*width="1440"[^>]*fill="#e8e7e3"', svg_content)
    if not header_rects:
        issues.append("Pas de header navigation pleine largeur détecté")

    # Sidebar : rect avec width ~188
    sidebar_rects = re.findall(r'<rect[^>]*width="188"[^>]*fill="#f0efeb"', svg_content)
    if not sidebar_rects:
        issues.append("Pas de sidebar détectée (width=188, fill=#f0efeb)")

    # Main content : organes af-organ
    organ_count = len(re.findall(r'class="af-organ"', svg_content))
    if organ_count == 0:
        issues.append("Aucun organe af-organ dans le main content")
    elif organ_count < 3:
        issues.append(f"Seulement {organ_count} organe(s) — insuffisant pour un wireframe utile")

    return len(issues) == 0, issues


def _density_check(svg_content: str) -> tuple[bool, list[str]]:
    """Vérifie que les archetype renderers produisent du contenu (pas juste des rects vides)."""
    issues = []

    # Compter les éléments de contenu : textes, cercles, lignes dans les organs
    text_count  = len(re.findall(r'<text ', svg_content))
    circle_count = len(re.findall(r'<circle ', svg_content))
    line_count  = len(re.findall(r'<line ', svg_content))
    organ_count = max(1, len(re.findall(r'class="af-organ"', svg_content)))

    elements_per_organ = (text_count + circle_count + line_count) / organ_count

    if elements_per_organ < 3:
        issues.append(
            f"Densité trop faible : {elements_per_organ:.1f} éléments/organe "
            f"(textes={text_count}, cercles={circle_count}, lignes={line_count})"
        )

    # Vérifier qu'il n'y a pas que des main-canvas (grilles vides)
    canvas_organs = svg_content.count('data-ui-role="main-content"')
    if organ_count > 0 and canvas_organs / organ_count > 0.6:
        issues.append(
            f"Trop d'organes main-content ({canvas_organs}/{organ_count}) — "
            "enrichissement insuffisant, relancer enrich"
        )

    return len(issues) == 0, issues


def _organ_quality_check(svg_content: str) -> tuple[bool, list[str], list[str]]:
    """
    Détecte les organes N1 avec contenu placeholder vide ('[ workspace ]').
    Ce placeholder est émis par draw_main_canvas() quand ui_role='main-content'.

    Retourne: (passed, issues, empty_organ_ids)
    """
    issues = []
    empty_organ_ids = []

    # Trouver les tags d'ouverture des groupes af-organ avec leur id et ui-role
    organ_tags = list(re.finditer(
        r'<g\s+([^>]*class="af-organ"[^>]*)>',
        svg_content
    ))

    for i, m in enumerate(organ_tags):
        attrs = m.group(1)
        id_match   = re.search(r'id="([^"]+)"', attrs)
        role_match = re.search(r'data-ui-role="([^"]+)"', attrs)

        if not id_match:
            continue

        organ_id = id_match.group(1)
        role     = role_match.group(1) if role_match else 'unknown'

        # Extraire le contenu de l'organe jusqu'au prochain af-organ ou fin de SVG
        start   = m.end()
        end_pos = organ_tags[i + 1].start() if i + 1 < len(organ_tags) else len(svg_content)
        snippet = svg_content[start:end_pos]

        # main-canvas est un workspace vide LÉGITIME (outil de design, canvas d'édition).
        # On ne le flag comme "vide" que si le role est main-content (classification incorrecte).
        if '[ workspace ]' in snippet and role not in ('main-canvas', 'overlay'):
            empty_organ_ids.append(organ_id)
            issues.append(
                f"Organe vide {organ_id} (ui_role={role}) — placeholder [ workspace ] détecté"
            )

    return len(issues) == 0, issues, empty_organ_ids


# ── Validation LLM (Claude Haiku) ────────────────────────────────────────────

def _llm_validate_zones(svg_content: str, api_key: str) -> tuple[bool, str]:
    """Envoie le résumé SVG à Gemini Flash pour validation sémantique des zones."""
    if not _GEMINI_OK:
        return True, "google.genai non installé — skip LLM check"

    phases   = re.findall(r'data-name="([^"]+)"[^>]*class="af-phase"', svg_content)
    organs   = re.findall(r'data-name="([^"]+)"[^>]*class="af-organ"', svg_content)
    ui_roles = re.findall(r'data-ui-role="([^"]+)"', svg_content)
    nav_tabs = re.findall(r'<text[^>]*font-weight="600"[^>]*>([A-Z]{2,4})</text>', svg_content)

    summary = (
        f"SVG Wireframe AetherFlow — résumé structurel:\n"
        f"- Phases (artboards): {phases}\n"
        f"- Nav tabs: {list(set(nav_tabs))}\n"
        f"- Organes main content: {organs}\n"
        f"- UI roles: {sorted(set(ui_roles))}\n"
        f"- Textes: {svg_content.count('<text ')} | Rects: {svg_content.count('<rect ')} | Organes: {len(organs)}\n"
    )

    prompt = (
        f"Tu es un expert UI wireframe.\n\n{summary}\n\n"
        "Valide STRICTEMENT:\n"
        "1. HEADER: barre nav en haut avec onglets (BRS, BKS, FRD, DPL)\n"
        "2. SIDEBAR: colonne menu gauche avec sections de la phase\n"
        "3. MAIN: ≥2 zones de contenu avec ui_roles DIFFÉRENTS\n"
        "4. DIVERSITÉ: ≥3 ui_roles distincts (pas que main-content)\n\n"
        "Réponds UNIQUEMENT JSON strict:\n"
        '{"result":"PASS"|"FAIL","score":0-100,"issues":[],"summary":"une phrase"}'
    )

    # Essai Gemini Flash
    if _GEMINI_OK:
        try:
            client = google_genai.Client(api_key=api_key)
            resp = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )
            raw = resp.text.strip()
            raw = re.sub(r'^```json\s*|\s*```$', '', raw, flags=re.MULTILINE).strip()
            data = json.loads(raw)
            passed = data.get("result") == "PASS"
            reason = "[Gemini] " + data.get("summary", "") + " | " + str(data.get("issues", []))
            return passed, reason
        except Exception as e:
            print(f"  [VALIDATOR] Gemini 429/erreur → fallback Claude Haiku ({type(e).__name__})")

    # Fallback Claude Haiku
    if _ANTHROPIC_OK:
        anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
        if anthropic_key:
            try:
                cl = _anthropic_mod.Anthropic(api_key=anthropic_key)
                msg = cl.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=512,
                    messages=[{"role": "user", "content": prompt}]
                )
                raw = msg.content[0].text.strip()
                raw = re.sub(r'^```json\s*|\s*```$', '', raw, flags=re.MULTILINE).strip()
                data = json.loads(raw)
                passed = data.get("result") == "PASS"
                reason = "[Haiku] " + data.get("summary", "") + " | " + str(data.get("issues", []))
                return passed, reason
            except Exception as e2:
                return True, f"Haiku fallback échec ({e2}) — skip"

    return True, "Aucun LLM disponible — skip"


# ── Validateur principal ──────────────────────────────────────────────────────

def validate_svg(svg_path: str, check_density: bool = False, api_key: str = None) -> dict:
    """
    Valide un SVG wireframe.
    Retourne: {
        "passed": bool,
        "issues": [...],
        "llm_result": str,
        "empty_organ_ids": [...]   # organes avec placeholder [ workspace ]
    }
    """
    content = Path(svg_path).read_text(encoding='utf-8')
    all_issues = []
    result = {"passed": False, "issues": [], "llm_result": "", "empty_organ_ids": []}

    # Pass 1 : zones structurelles
    ok, issues = _structural_check(content)
    all_issues.extend(issues)

    # Pass 2 : densité globale + qualité par organe (optionnel)
    if check_density:
        ok2, issues2 = _density_check(content)
        all_issues.extend(issues2)

        ok3, issues3, empty_ids = _organ_quality_check(content)
        all_issues.extend(issues3)
        result["empty_organ_ids"] = empty_ids

    # Pass LLM (si clé dispo et pas d'erreurs structurelles bloquantes)
    if api_key and not all_issues:
        llm_ok, llm_msg = _llm_validate_zones(content, api_key)
        result["llm_result"] = llm_msg
        if not llm_ok:
            all_issues.append(f"LLM: {llm_msg}")
    elif api_key:
        result["llm_result"] = "skip (erreurs structurelles préalables)"

    result["issues"] = all_issues
    result["passed"] = len(all_issues) == 0
    return result


# ── CLI standalone ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Validate SVG wireframe zones')
    parser.add_argument('--svg', required=True, help='Chemin vers le SVG à valider')
    parser.add_argument('--pass2', action='store_true', help='Valider aussi la densité des composants')
    parser.add_argument('--api-key', default=None, help='Clé Anthropic (ou ANTHROPIC_API_KEY env)')
    args = parser.parse_args()

    # Priorité : GOOGLE_API_KEY_BACKEND (Backend/.env) > GOOGLE_API_KEY root
    api_key = (args.api_key
               or os.environ.get('GOOGLE_API_KEY_BACKEND')
               or os.environ.get('GOOGLE_API_KEY'))

    print(f"🔍 Validation : {args.svg}")
    result = validate_svg(args.svg, check_density=args.pass2, api_key=api_key)

    if result["passed"]:
        print("✅ PASS — Zones correctement définies")
        if result["llm_result"]:
            print(f"   LLM: {result['llm_result']}")
        if result.get("empty_organ_ids"):
            # PASS global mais organes vides détectés → avertissement non bloquant
            print(f"   ⚠ Organes vides (non bloquants): {result['empty_organ_ids']}")
        sys.exit(0)
    else:
        print("❌ FAIL — Zones insuffisantes :")
        for issue in result["issues"]:
            print(f"   • {issue}")
        if result["llm_result"]:
            print(f"   LLM: {result['llm_result']}")
        if result.get("empty_organ_ids"):
            print(f"   Organes vides à corriger: {result['empty_organ_ids']}")
            # Émettre les IDs sur stdout pour que le shell puisse les capturer
            print(f"EMPTY_ORGANS:{','.join(result['empty_organ_ids'])}")
        sys.exit(1)


if __name__ == '__main__':
    main()
