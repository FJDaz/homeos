#!/usr/bin/env python3
"""
genome_enricher.py — Mission 21B
Enrichit le genome avec des métadonnées sémantiques (ui_role, dominant_zone, display_label).
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict

# Réutilisation de la logique de classification de genome_to_svg_v2
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

UI_ROLE_MAP = {
    'header':   {'ui_role': 'nav-header',      'label': 'Navigation'},
    'sidebar':  {'ui_role': 'left-sidebar',    'label': 'Panel'},
    'main':     {'ui_role': 'main-content',    'label': 'Workspace'},
    'footer':   {'ui_role': 'status-bar',      'label': 'Actions'},
    'floating': {'ui_role': 'overlay',         'label': 'Overlay'},
}

HINT_ROLE_OVERRIDES = {
    'form':         'form-panel',
    'input':        'form-panel',
    'upload':       'upload-zone',
    'download':     'export-action',
    'export':       'export-action',
    'editor':       'main-canvas',
    'canvas':       'main-canvas',
    'preview':      'main-canvas',
    'dashboard':    'dashboard',
    'chart':        'dashboard',
    'graph':        'dashboard',
    'accordion':    'dashboard',
    'choice-card':  'dashboard',   # galerie de sélection visuelle (layout, style)
    'table':        'dashboard',   # tableaux de données avec verdicts
    'detail-card':  'dashboard',   # fiche technique / vue détail
    'chat':         'chat-overlay',
    'modal':        'overlay',
    'dialog':       'overlay',
    'settings':     'settings-panel',
    'stepper':      'onboarding-flow',
    'breadcrumb':   'nav-header',
}

def classify_hint(hint: str, name: str) -> str:
    hint = hint.lower()
    name = name.lower()
    for zone, keywords in ZONE_MAPPINGS.items():
        for kw in keywords:
            if kw in hint or kw in name:
                return zone
    if any(w in hint or w in name for w in ['overlay', 'float', 'hover', 'click']):
        return 'floating'
    return 'main'

def enrich_genome(genome: Dict) -> Dict:
    for phase in genome.get('n0_phases', []):
        for organ in phase.get('n1_sections', []):
            hints = []
            all_n3 = []
            for feature in organ.get('n2_features', []):
                for comp in feature.get('n3_components', []):
                    all_n3.append(comp)
                    hints.append(comp.get('visual_hint', '').lower())
            
            if not hints:
                organ['ui_role'] = 'unknown'
                organ['dominant_zone'] = 'main'
                organ['display_label'] = organ.get('name', organ.get('id'))
                continue

            # Compter par zone
            zone_counts = {'header': 0, 'sidebar': 0, 'main': 0, 'footer': 0, 'floating': 0}
            hint_counts = {}
            
            for comp in all_n3:
                h = comp.get('visual_hint', '').lower()
                n = comp.get('name', '').lower()
                zone = classify_hint(h, n)
                zone_counts[zone] += 1
                hint_counts[h] = hint_counts.get(h, 0) + 1
            
            # Zone dominante
            dominant_zone = max(zone_counts, key=zone_counts.get)
            
            # UI Role
            ui_role = UI_ROLE_MAP[dominant_zone]['ui_role']
            
            # Overrides par hint — substring matching, du plus fréquent au moins fréquent
            ui_role_override = None
            for hint in sorted(hint_counts.keys(), key=lambda h: hint_counts[h], reverse=True):
                matched = next((role for key, role in HINT_ROLE_OVERRIDES.items() if key in hint), None)
                if matched:
                    ui_role_override = matched
                    break
            if ui_role_override:
                ui_role = ui_role_override
            
            # Label
            role_label = next((v['label'] for k, v in UI_ROLE_MAP.items() if v['ui_role'] == ui_role), 'Module')
            # Si on a un override, on peut chercher son label ou utiliser une table étendue
            # Pour faire simple, on utilise le label de la zone ou "Module"
            
            organ['ui_role'] = ui_role
            organ['dominant_zone'] = dominant_zone
            organ['display_label'] = f"{role_label} / {organ.get('name', organ.get('id'))}"
            
            print(f"  [ENRICH] {organ.get('id')} -> {ui_role} ({dominant_zone})")
            
    return genome

UX_SEQUENCE = {
    'nav-header': 1, 'left-sidebar': 2, 'main-canvas': 3,
    'main-content': 4, 'dashboard': 5, 'form-panel': 6,
    'upload-zone': 7, 'chat-overlay': 8, 'onboarding-flow': 9,
    'overlay': 10, 'settings-panel': 11, 'status-bar': 12,
    'export-action': 13, 'unknown': 99,
}

def enrich_pass2_ux(genome):
    """Ajoute ux_step à chaque N1. Trie les organes dans chaque phase par ux_step."""
    for phase in genome.get('n0_phases', []):
        organs = phase.get('n1_sections', [])
        for organ in organs:
            organ['ux_step'] = UX_SEQUENCE.get(organ.get('ui_role', 'unknown'), 99)
            print(f"  [PASS2] {organ.get('id')} → ux_step={organ['ux_step']}")
        organs.sort(key=lambda o: o.get('ux_step', 99))
    return genome

def enrich_pass3_density(genome):
    """Ajoute layout_type et col_span selon le nb de composants N3."""
    for phase in genome.get('n0_phases', []):
        for organ in phase.get('n1_sections', []):
            n3_count = sum(
                len(f.get('n3_components', []))
                for f in organ.get('n2_features', [])
            )
            if n3_count < 3:
                organ['layout_type'] = 'compact'
                organ['col_span'] = 1
            elif n3_count <= 6:
                organ['layout_type'] = 'standard'
                organ['col_span'] = 1
            else:
                organ['layout_type'] = 'wide'
                organ['col_span'] = 2
            print(f"  [PASS3] {organ.get('id')} → {organ['layout_type']} (N3={n3_count})")
    return genome

import asyncio
from typing import Optional

def _get_api_key_for_gemini() -> Optional[str]:
    import os
    return (os.environ.get('GOOGLE_API_KEY_BACKEND') or 
            os.environ.get('GOOGLE_API_KEY'))

def enrich_pass4_architecture(genome):
    """
    Pass 4: Utilise Gemini Architect pour générer un layout premium WP-inspired.
    Si Gemini n'est pas dispo, garde la stratégie standard.
    """
    api_key = _get_api_key_for_gemini()
    if not api_key:
        print("  [PASS4] Skipped (No Google API Key)")
        return genome
        
    try:
        import sys
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
            
        from Backend.Prod.planners.gemini_planner import GeminiPlanner
        from Backend.Prod.models.gemini_client import GeminiClient
        from Backend.Prod.exporters.topology_bank import TOPOLOGIES
        
        # Format topology bank context
        topo_context = []
        for name, spec in TOPOLOGIES.items():
            topo_context.append(f"- {name}: {spec['description']}")
        topo_str = "\n".join(topo_context)
        
        client = GeminiClient(api_key=api_key)
        planner = GeminiPlanner(gemini_client=client)
        
        # Create an event loop explicitly for sync context
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        for phase in genome.get('n0_phases', []):
            for organ in phase.get('n1_sections', []):
                # Request layout from Gemini
                print(f"  [PASS4] Consulting Theme Architect for {organ.get('id')}...")
                result = loop.run_until_complete(
                    planner.generate_ui_architecture(organ, topo_str)
                )
                
                # Apply the layout strategy
                organ['layout_strategy'] = result.get('layout_strategy', 'standard')
                organ['layout_justification'] = result.get('justification', '')
                
                # Optional: Handle explicit zone assignments if returned
                assignments = result.get('zone_assignment', {})
                if assignments:
                    # Enrich N2 features with zone info where possible
                    for uizone, item_list in assignments.items():
                        for item in item_list:
                            # Simplistic match to append zone info to description or a new field
                            for feat in organ.get('n2_features', []):
                                for comp in feat.get('n3_components', []):
                                    if comp.get('name', '').lower() in item.lower():
                                        comp['zone_assignment'] = uizone
                                        break
                                        
                print(f"  [PASS4] ↳ Selected: {organ['layout_strategy']}")
                
    except ImportError as e:
        print(f"  [PASS4] Skipped (Missing dependencies: {e})")
    except Exception as e:
        print(f"  [PASS4] Failed: {e}")
        
    return genome

def main():
    parser = argparse.ArgumentParser(description='AetherFlow Genome Enricher')
    parser.add_argument('--genome', required=True, help='Path to genome_reference.json')
    parser.add_argument('--output', required=True, help='Path to genome_enriched.json')
    parser.add_argument('--dry-run', action='store_true', help='Do not write file')
    args = parser.parse_args()
    
    with open(args.genome, 'r', encoding='utf-8') as f:
        genome = json.load(f)
    
    enriched = enrich_genome(genome)
    enriched = enrich_pass2_ux(enriched)
    enriched = enrich_pass3_density(enriched)
    enriched = enrich_pass4_architecture(enriched)
    
    if not args.dry_run:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(enriched, f, indent=2, ensure_ascii=False)
        print(f"Genome enrichi sauvegardé dans : {args.output}")
    else:
        print("Dry-run : aucune écriture.")

if __name__ == '__main__':
    main()

