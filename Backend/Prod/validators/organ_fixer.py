#!/usr/bin/env python3
"""
organ_fixer.py — Mission 21D Pass 2
Corrige les organes N1 vides (placeholder [ workspace ]) en demandant à Gemini
le ui_role sémantiquement correct, en s'appuyant sur :
  - le nom et la description de l'organe
  - les description_ui de chaque composant N3 (ce que l'utilisateur voit/fait)
  - les visual_hints et interaction_types
  - le contexte projet (HomeOS/Sullivan)

Usage:
  python organ_fixer.py --organs n1_ir n1_arbitrage --genome genome_enriched.json
  python organ_fixer.py --organs n1_ir --genome genome_enriched.json --dry-run
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


# ── Catalogue ui_roles avec descriptions fonctionnelles ──────────────────────

UI_ROLE_CATALOGUE = {
    'dashboard': (
        "Tableau de bord avec métriques, scores de confiance, listes de statuts avec couleurs "
        "(Accept/Revise/Reject), résumé visuel, cartes informatives, galeries de sélection "
        "(choice-cards, layout previews, grilles de style). "
        "Idéal pour : rapports, inventaires, tableaux de validation, vue d'ensemble, "
        "sélection parmi des options visuelles."
    ),
    'form-panel': (
        "Formulaire avec champs texte/select/radio, boutons submit, validation en temps réel. "
        "Idéal pour : saisie de données, paramétrage, configuration."
    ),
    'upload-zone': (
        "Zone de drag & drop, input fichier, preview du fichier uploadé, barre de progression. "
        "Idéal pour : import d'assets, upload images/fichiers, ingestion de données."
    ),
    'main-canvas': (
        "Surface de travail VIDE où l'utilisateur CRÉE ou ÉDITE visuellement. "
        "Ex: éditeur SVG avec calque d'analyse superposé, canvas de design avec annotations, "
        "zone de rendu avec overlay. "
        "PAS pour : galeries de choix (→ dashboard), formulaires, tableaux de données. "
        "Idéal UNIQUEMENT pour : analyse d'image avec overlay interactif, édition de code visuel, "
        "canvas de prototypage."
    ),
    'chat-overlay': (
        "Interface conversationnelle : bulles de messages (style Messenger), input de saisie, "
        "historique de dialogue, choice-cards intégrés. "
        "Idéal pour : dialogues IA, Q&A guidé, onboarding conversationnel."
    ),
    'onboarding-flow': (
        "Stepper horizontal multi-étapes avec indicateurs de progression, wizard guidé, "
        "navigation ← Précédent / Suivant →. "
        "Idéal pour : workflows séquentiels, phases de setup, tutoriels."
    ),
    'nav-header': (
        "Barre de navigation principale avec onglets actifs/inactifs, breadcrumb de localisation, "
        "titre de section. Idéal pour : orientation dans l'application, navigation entre sections."
    ),
    'left-sidebar': (
        "Panneau latéral avec liste d'éléments, arborescence, filtres, menu secondaire. "
        "Idéal pour : navigation de contenu, liste de fichiers/phases, options contextuelles."
    ),
    'settings-panel': (
        "Panneau de configuration avec toggles, sliders, listes de préférences. "
        "Idéal pour : réglages de session, configuration d'outil, préférences utilisateur."
    ),
    'overlay': (
        "Modal, dialog, popup apparaissant par-dessus le contenu principal. "
        "Idéal pour : confirmations, formulaires secondaires, alertes."
    ),
    'export-action': (
        "Carte/bouton de téléchargement, modal de sélection format d'export, "
        "partage de fichier, bouton 📥 avec métadonnées. "
        "Idéal pour : téléchargement d'archives, export SVG/JSON/ZIP, partage."
    ),
    'status-bar': (
        "Barre de statut en bas de page avec pagination, compteurs, actions secondaires. "
        "Idéal pour : navigation entre pages, état de chargement, actions de bas de page."
    ),
}

UX_SEQUENCE = {
    'nav-header': 1, 'left-sidebar': 2, 'main-canvas': 3,
    'main-content': 4, 'dashboard': 5, 'form-panel': 6,
    'upload-zone': 7, 'chat-overlay': 8, 'onboarding-flow': 9,
    'overlay': 10, 'settings-panel': 11, 'status-bar': 12,
    'export-action': 13, 'unknown': 99,
}


# ── Construction du contexte organe ──────────────────────────────────────────

def _build_organ_prompt(organ: dict, project: str, phase_name: str) -> str:
    """
    Construit un prompt riche à partir des données du génome.
    Utilise : organ name, description, N2 features, N3 description_ui, visual_hints,
              interaction_type, layout_hint.
    """
    organ_id   = organ.get('id', '?')
    organ_name = organ.get('name', '?')
    organ_desc = organ.get('description', '')

    lines = [
        f"# Contexte",
        f"Projet : {project}",
        f"Phase : {phase_name}",
        f"",
        f"# Organe à classifier",
        f"ID : {organ_id}",
        f"Nom : {organ_name}",
    ]
    if organ_desc:
        lines.append(f"Description : {organ_desc}")

    lines += ["", "# Composants fonctionnels (N3) — ce que l'utilisateur voit et fait :"]

    for feat in organ.get('n2_features', []):
        feat_name = feat.get('name', '')
        lines.append(f"\n## Feature : {feat_name}")
        for comp in feat.get('n3_components', []):
            hint  = comp.get('visual_hint', '?')
            name  = comp.get('name', '')
            desc  = comp.get('description_ui', '')
            inter = comp.get('interaction_type', '')
            lay   = comp.get('layout_hint', '')
            ep    = comp.get('endpoint', '')

            entry = f"  [{hint}] {name}"
            if desc:
                entry += f"\n    → {desc}"
            if inter:
                entry += f"\n    interaction: {inter}"
            if lay:
                entry += f"  |  layout: {lay}"
            if ep:
                entry += f"\n    endpoint: {ep}"
            lines.append(entry)

    role_list = '\n'.join(
        f"  • {role}: {desc}"
        for role, desc in UI_ROLE_CATALOGUE.items()
    )

    lines += [
        "",
        "# Ta mission",
        "Cet organe est actuellement rendu comme 'main-content' → canvas vide avec grille.",
        "C'est INCORRECT. Analyse le contenu fonctionnel ci-dessus.",
        "",
        "Choisis le ui_role parmi :",
        role_list,
        "",
        "Réponds UNIQUEMENT avec du JSON strict (sans markdown, sans explication hors JSON) :",
        '{"ui_role":"<role>","confidence":0-100,"reasoning":"une phrase expliquant le choix"}',
    ]

    return '\n'.join(lines)


# ── Appel Gemini ─────────────────────────────────────────────────────────────

def fix_organ_roles(
    empty_organ_ids: list,
    genome_path: str,
    api_key: str,
    dry_run: bool = False,
) -> dict:
    """
    Pour chaque organe vide, interroge Gemini Flash pour le bon ui_role.
    Si dry_run=False, patche genome_enriched.json en place.
    Retourne: { organ_id: new_ui_role }
    """
    if not _GEMINI_OK:
        print("  [FIXER] google.genai non disponible — skip")
        return {}

    genome = json.loads(Path(genome_path).read_text(encoding='utf-8'))
    project = genome.get('project', 'HomeOS/Sullivan')

    # Index organ_id → (organ_dict, phase_name)
    organ_index: dict[str, tuple[dict, str]] = {}
    for phase in genome.get('n0_phases', []):
        phase_name = phase.get('name', phase.get('id', '?'))
        for organ in phase.get('n1_sections', []):
            organ_index[organ['id']] = (organ, phase_name)

    client = google_genai.Client(api_key=api_key)
    fixes: dict[str, str] = {}

    for organ_id in empty_organ_ids:
        if organ_id not in organ_index:
            print(f"  [FIXER] ⚠ Organe {organ_id} introuvable dans le génome — skip")
            continue

        organ, phase_name = organ_index[organ_id]
        prompt = _build_organ_prompt(organ, project, phase_name)

        print(f"  [FIXER] Interrogation Gemini pour {organ_id} ({organ.get('name', '?')})...")

        try:
            resp = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )
            raw = resp.text.strip()
            raw = re.sub(r'^```json\s*|\s*```$', '', raw, flags=re.MULTILINE).strip()
            data = json.loads(raw)

            role = data.get('ui_role', '').strip()
            conf = data.get('confidence', 0)
            reason = data.get('reasoning', '')

            if role not in UI_ROLE_CATALOGUE:
                print(f"  [FIXER] ⚠ {organ_id}: role '{role}' non reconnu — ignoré")
                continue

            fixes[organ_id] = role
            print(f"  [FIXER] ✅ {organ_id} → {role}  (conf={conf}%)  «{reason}»")

        except json.JSONDecodeError as e:
            print(f"  [FIXER] ❌ JSON parse erreur pour {organ_id}: {e}")
            print(f"         Réponse brute : {resp.text[:300]}")
        except Exception as e:
            print(f"  [FIXER] ❌ Gemini erreur pour {organ_id}: {type(e).__name__}: {e}")

    if fixes and not dry_run:
        _apply_fixes(fixes, genome, genome_path)

    return fixes


def _apply_fixes(fixes: dict, genome: dict, genome_path: str) -> None:
    """Patche le génome en mémoire et réécrit le fichier."""
    patched = 0
    for phase in genome.get('n0_phases', []):
        for organ in phase.get('n1_sections', []):
            if organ['id'] in fixes:
                old_role = organ.get('ui_role', '?')
                new_role = fixes[organ['id']]
                organ['ui_role']   = new_role
                organ['ux_step']   = UX_SEQUENCE.get(new_role, 99)
                # Invalider le label auto pour forcer re-render propre
                organ['display_label'] = organ.get('name', organ['id'])
                print(f"  [APPLY] {organ['id']}: {old_role} → {new_role}")
                patched += 1

    Path(genome_path).write_text(
        json.dumps(genome, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
    print(f"  [APPLY] {patched} organe(s) patchés → {genome_path}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Corrige les organes vides via Gemini Flash (contexte génome riche)'
    )
    parser.add_argument('--organs', required=True, nargs='+',
                        help='IDs des organes vides (ex: n1_ir n1_arbitrage)')
    parser.add_argument('--genome', required=True,
                        help='Chemin vers genome_enriched.json (sera patché in-place)')
    parser.add_argument('--api-key', default=None,
                        help='Clé Google Gemini (ou GOOGLE_API_KEY_BACKEND)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Affiche les corrections sans écrire le fichier')
    args = parser.parse_args()

    api_key = (
        args.api_key
        or os.environ.get('GOOGLE_API_KEY_BACKEND')
        or os.environ.get('GOOGLE_API_KEY')
    )

    if not api_key:
        print("❌ Clé API manquante (GOOGLE_API_KEY_BACKEND ou GOOGLE_API_KEY)")
        sys.exit(1)

    if not _GEMINI_OK:
        print("❌ google-genai non installé. Faire : pip install google-genai")
        sys.exit(1)

    print(f"🔧 Correction de {len(args.organs)} organe(s) : {args.organs}")
    if args.dry_run:
        print("   Mode dry-run — aucune écriture")

    fixes = fix_organ_roles(args.organs, args.genome, api_key, dry_run=args.dry_run)

    if fixes:
        print(f"\n✅ {len(fixes)}/{len(args.organs)} organe(s) corrigé(s)")
        for oid, role in fixes.items():
            print(f"   {oid} → {role}")
    else:
        print("\n⚠ Aucune correction appliquée")
        sys.exit(1)


if __name__ == '__main__':
    main()
