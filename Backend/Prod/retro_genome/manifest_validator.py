#!/usr/bin/env python3
"""
manifest_validator.py — Validation d'un template HTML contre son manifeste AetherFlow.

Architecture :
  - Tout template peut avoir un manifeste <name>_manifest.json dans le même dossier.
  - La validation est déclenchée AVANT toute écriture sur disque (POST /api/frd/file).
  - Si le manifeste est absent : pas de contrainte (backward compatible).
  - Si le manifeste est présent : violation = rejet 422 avec liste précise des violations.

Logique de validation :
  1. required_elements  → chaque #id doit exister dans le DOM HTML
  2. required_classes   → chaque classe doit apparaître au moins min_count fois
  3. required_scripts   → chaque src doit être présent (et unique si unique=true)
  4. forbidden          → inline_script_tag détecté = violation

Génération du système prompt :
  format_system_prompt_constraint(file_name) → bloc de texte à injecter
  dans tout prompt système d'un agent qui modifie ce template.
"""

import json
import re
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional
from html.parser import HTMLParser

TEMPLATES_DIR = (
    Path(__file__).parent.parent.parent.parent
    / "Frontend" / "3. STENCILER" / "static" / "templates"
)


# ---------------------------------------------------------------------------
# Analyseur HTML
# ---------------------------------------------------------------------------

class _HTMLAnalyzer(HTMLParser):
    """Extrait les IDs, comptes de classes, et srcs de script d'un document HTML."""

    def __init__(self):
        super().__init__()
        self.ids: set = set()
        self.class_counts: Dict[str, int] = {}
        self.script_srcs: List[str] = []

    def handle_starttag(self, tag: str, attrs_list):
        attrs = dict(attrs_list)

        if "id" in attrs:
            self.ids.add(attrs["id"].strip())

        if "class" in attrs:
            for cls in attrs["class"].split():
                self.class_counts[cls] = self.class_counts.get(cls, 0) + 1

        if tag == "script" and "src" in attrs:
            self.script_srcs.append(attrs["src"].strip())


def _has_inline_scripts(html: str) -> bool:
    """Détecte les <script> inline contenant du code applicatif (hors config Tailwind)."""
    matches = re.findall(
        r'<script(?!\s[^>]*\bsrc\b)[^>]*>(.*?)</script>',
        html, re.IGNORECASE | re.DOTALL
    )
    for content in matches:
        stripped = content.strip()
        # Tailwind config autorisée (déclaratif, pas applicatif)
        if stripped.startswith('tailwind.config'):
            continue
        if stripped:
            return True
    return False


# ---------------------------------------------------------------------------
# Chargement du manifeste
# ---------------------------------------------------------------------------

def get_manifest_path(file_name: str) -> Path:
    stem = Path(file_name).stem  # ex: "brainstorm_war_room_tw"
    return TEMPLATES_DIR / f"{stem}_manifest.json"


def load_manifest(file_name: str) -> Optional[Dict[str, Any]]:
    """Charge le manifeste JSON du template. Retourne None si absent."""
    path = get_manifest_path(file_name)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_html(file_name: str, html: str) -> Tuple[bool, List[str]]:
    """
    Valide le HTML contre le manifeste du template.

    Retourne (is_valid, errors).
    Si pas de manifeste : (True, []) — aucune contrainte.
    Si violations : (False, [liste des erreurs précises]).
    """
    manifest = load_manifest(file_name)
    if manifest is None:
        return True, []

    analyzer = _HTMLAnalyzer()
    analyzer.feed(html)

    errors: List[str] = []

    # 1. IDs requis
    for elem in manifest.get("required_elements", []):
        selector = elem["selector"]
        elem_id = selector.lstrip("#")
        if elem_id not in analyzer.ids:
            errors.append(
                f"ID requis manquant : {selector} — {elem['description']}"
            )

    # 2. Classes requises
    for cls_req in manifest.get("required_classes", []):
        cls = cls_req["class"]
        min_count = cls_req.get("min_count", 1)
        found = analyzer.class_counts.get(cls, 0)
        if found < min_count:
            errors.append(
                f"Classe requise insuffisante : .{cls} "
                f"(attendu ≥{min_count}, trouvé {found}) — {cls_req['description']}"
            )

    # 3. Scripts requis
    for script_req in manifest.get("required_scripts", []):
        src = script_req["src"]
        if src not in analyzer.script_srcs:
            errors.append(
                f"Script obligatoire manquant : {src} — {script_req['description']}"
            )
        elif script_req.get("unique") and analyzer.script_srcs.count(src) > 1:
            errors.append(f"Script dupliqué (doit être unique) : {src}")

    # 4. Interdits
    for rule in manifest.get("forbidden", []):
        if rule["type"] == "inline_script_tag" and _has_inline_scripts(html):
            errors.append(
                f"Script inline interdit : balise <script> sans src détectée. "
                f"— {rule['description']}"
            )

    return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# Génération du bloc système prompt
# ---------------------------------------------------------------------------

def format_system_prompt_constraint(file_name: str) -> str:
    """
    Génère le bloc de contrainte STRICT à injecter dans tout prompt système
    d'un agent (Sullivan, Gemini, Codestral…) qui modifie ce template.

    Retourne une chaîne vide si pas de manifeste (aucune contrainte).
    """
    manifest = load_manifest(file_name)
    if manifest is None:
        return ""

    lines = [
        f"⛔ CONTRAT DOM STRICT — {manifest['file']} (manifeste v{manifest['version']})",
        "Ce fichier est contrôlé par un manifeste machine. Toute modification est validée",
        "automatiquement côté serveur AVANT écriture sur disque.",
        "VIOLATION = REJET TOTAL (HTTP 422). Aucune exception. Aucune heuristique.",
        "",
        "═══════════════════════════════════════════════════",
        "IDs REQUIS — ne jamais renommer, supprimer, ni déplacer :",
        "═══════════════════════════════════════════════════",
    ]

    for elem in manifest.get("required_elements", []):
        lines.append(f"  • {elem['selector']}")
        lines.append(f"      {elem['description']}")

    lines += [
        "",
        "═══════════════════════════════════════════════════",
        "CLASSES REQUISES :",
        "═══════════════════════════════════════════════════",
    ]
    for cls_req in manifest.get("required_classes", []):
        lines.append(
            f"  • .{cls_req['class']} "
            f"(min {cls_req['min_count']} occurrences dans le DOM)"
        )
        lines.append(f"      {cls_req['description']}")

    lines += [
        "",
        "═══════════════════════════════════════════════════",
        "SCRIPT REQUIS (unique, aucun autre script autorisé) :",
        "═══════════════════════════════════════════════════",
    ]
    for s in manifest.get("required_scripts", []):
        lines.append(f"  • {s['src']}")

    lines += [
        "",
        "═══════════════════════════════════════════════════",
        "INTERDIT — violation entraîne rejet immédiat :",
        "═══════════════════════════════════════════════════",
        "  ✗ Renommer ou supprimer un ID requis",
        "  ✗ Ajouter du code JS inline (<script> sans src)",
        "  ✗ Modifier l'attribut src du script contrôleur",
        "  ✗ Dupliquer le script contrôleur",
        "",
        "═══════════════════════════════════════════════════",
        "AUTORISÉ — sans restriction :",
        "═══════════════════════════════════════════════════",
        "  ✓ Classes CSS Tailwind sur n'importe quel élément (apparence uniquement)",
        "  ✓ Texte des labels, placeholders, titres, descriptions",
        "  ✓ Ajout de nouveaux éléments sans ID requis (décoratifs, layout)",
        "  ✓ Attributs style/hidden/data-* sur éléments requis",
        "  ✓ Réorganisation de la mise en page sans toucher les IDs",
        "",
        "═══════════════════════════════════════════════════",
        "PROTOCOLE DE MISE À JOUR DU MANIFESTE :",
        "═══════════════════════════════════════════════════",
        f"  {manifest['update_protocol']}",
    ]

    return "\n".join(lines)
