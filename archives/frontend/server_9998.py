#!/usr/bin/env python3
"""
Serveur HTTP pour visualisation du Genome - Port 9998
Version 5.0 - Layout SIMPLE: 4 rows de wireframes avec vrais noms
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

PORT = 9998
GENOME_FILE = "docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/genome_inferred_kimi_innocent_v2.json"

def load_genome():
    """Charge le genome depuis le fichier JSON"""
    filepath = GENOME_FILE
    if not os.path.exists(filepath):
        # Essayer chemin relatif depuis le répertoire courant
        cwd = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(cwd, GENOME_FILE)
    
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return {"n0_phases": [], "metadata": {"confidence_global": 0.85}}


def get_method_color(method):
    """Retourne la couleur associée à une méthode HTTP"""
    colors = {"GET": "#7aca6a", "POST": "#5a9ac6", "PUT": "#e4bb5a", "DELETE": "#d56363"}
    return colors.get(method, "#64748b")


def generate_wireframe(visual_hint, color="#7aca6a"):
    """Génère un wireframe miniature selon le visual_hint"""
    
    if visual_hint == "table":
        # Lignes de données grises
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:3px;justify-content:center;">
            <div style="display:flex;gap:3px;"><div style="flex:2;height:5px;background:#e2e8f0;border-radius:1px;"></div><div style="flex:1;height:5px;background:#e2e8f0;border-radius:1px;"></div></div>
            <div style="display:flex;gap:3px;"><div style="flex:2;height:5px;background:#e2e8f0;border-radius:1px;"></div><div style="flex:1;height:5px;background:#7aca6a;border-radius:1px;"></div></div>
            <div style="display:flex;gap:3px;"><div style="flex:2;height:5px;background:#e2e8f0;border-radius:1px;"></div><div style="flex:1;height:5px;background:#e2e8f0;border-radius:1px;"></div></div>
        </div>'''
    
    elif visual_hint == "preview":
        # Rectangles colorés (bleu/vert/rose)
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;gap:3px;justify-content:center;align-items:center;">
            <div style="width:25%;height:40px;background:rgba(59,130,246,0.2);border:1px dashed #5a9ac6;border-radius:3px;"></div>
            <div style="width:35%;height:40px;background:rgba(140,198,63,0.2);border:1px dashed #7aca6a;border-radius:3px;"></div>
            <div style="width:20%;height:40px;background:rgba(236,72,153,0.15);border:1px dashed #ec4899;border-radius:3px;"></div>
        </div>'''
    
    elif visual_hint == "dashboard":
        # Barres verticales (stats)
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;gap:3px;align-items:flex-end;justify-content:center;">
            <div style="width:12%;height:30%;background:#7aca6a;border-radius:2px 2px 0 0;"></div>
            <div style="width:12%;height:50%;background:#7aca6a;border-radius:2px 2px 0 0;"></div>
            <div style="width:12%;height:35%;background:#5a9ac6;border-radius:2px 2px 0 0;"></div>
            <div style="width:12%;height:60%;background:#7aca6a;border-radius:2px 2px 0 0;"></div>
        </div>'''
    
    elif visual_hint == "upload":
        # Zone avec "+"
        return '''<div style="background:#f8fafc;border:1px dashed #cbd5e1;border-radius:4px;height:60px;display:flex;align-items:center;justify-content:center;">
            <span style="font-size:24px;color:#94a3b8;">+</span>
        </div>'''
    
    elif visual_hint == "color-palette":
        # 4 carrés de couleurs
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;gap:4px;justify-content:center;align-items:center;">
            <div style="width:18px;height:18px;background:#5a9ac6;border-radius:4px;"></div>
            <div style="width:18px;height:18px;background:#7aca6a;border-radius:4px;"></div>
            <div style="width:18px;height:18px;background:#e4bb5a;border-radius:4px;"></div>
            <div style="width:18px;height:18px;background:#1e293b;border-radius:4px;"></div>
        </div>'''
    
    elif visual_hint == "chat/bubble":
        # Bulles de dialogue
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:4px;justify-content:center;">
            <div style="display:flex;gap:4px;"><div style="width:16px;height:16px;background:#6a8aca;border-radius:50%;"></div><div style="flex:1;height:12px;background:#e2e8f0;border-radius:6px;"></div></div>
            <div style="display:flex;gap:4px;justify-content:flex-end;"><div style="width:50%;height:12px;background:#6a8aca;border-radius:6px;"></div></div>
        </div>'''
    
    elif visual_hint == "stepper":
        # Cercles reliés par lignes
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;gap:4px;justify-content:center;align-items:center;">
            <div style="width:16px;height:16px;background:#7aca6a;border-radius:50%;"></div>
            <div style="flex:1;height:2px;background:#7aca6a;"></div>
            <div style="width:16px;height:16px;background:#7aca6a;border-radius:50%;"></div>
            <div style="flex:1;height:2px;background:#e2e8f0;"></div>
            <div style="width:16px;height:16px;background:#e2e8f0;border-radius:50%;"></div>
        </div>'''
    
    elif visual_hint == "status":
        # 4 LEDs (vertes/grises)
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;gap:8px;justify-content:center;align-items:center;">
            <div style="width:12px;height:12px;background:#7aca6a;border-radius:50%;"></div>
            <div style="width:12px;height:12px;background:#7aca6a;border-radius:50%;"></div>
            <div style="width:12px;height:12px;background:#7aca6a;border-radius:50%;"></div>
            <div style="width:12px;height:12px;background:#e2e8f0;border-radius:50%;"></div>
        </div>'''
    
    elif visual_hint == "zoom-controls":
        # Boutons < N0 >
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;gap:4px;align-items:center;justify-content:center;">
            <span style="padding:4px 8px;background:#e2e8f0;border-radius:3px;font-size:10px;color:#64748b;">&lt;</span>
            <span style="padding:4px 8px;background:#5a9ac6;border-radius:3px;font-size:10px;color:white;font-weight:600;">N0</span>
            <span style="padding:4px 8px;background:#e2e8f0;border-radius:3px;font-size:10px;color:#64748b;">&gt;</span>
        </div>'''
    
    elif visual_hint == "form":
        # Formulaire
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:4px;justify-content:center;">
            <div style="height:8px;background:#e2e8f0;border-radius:2px;width:40%;"></div>
            <div style="height:16px;background:white;border:1px solid #e2e8f0;border-radius:2px;"></div>
        </div>'''
    
    elif visual_hint == "detail-card":
        # Carte de détail
        return f'''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:3px;justify-content:center;">
            <div style="height:6px;background:{color};border-radius:2px;width:30%;"></div>
            <div style="height:4px;background:#e2e8f0;border-radius:1px;"></div>
            <div style="height:4px;background:#e2e8f0;border-radius:1px;width:80%;"></div>
        </div>'''
    
    elif visual_hint == "choice-card":
        # Carte de choix
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;gap:6px;justify-content:center;align-items:center;">
            <div style="width:32px;height:32px;background:white;border:2px solid #7aca6a;border-radius:6px;"></div>
            <div style="width:32px;height:32px;background:#f1f5f9;border:1px solid #e2e8f0;border-radius:6px;"></div>
        </div>'''
    
    elif visual_hint == "editor":
        # Éditeur de code (fond sombre)
        return '''<div style="background:#1e293b;border-radius:4px;padding:6px;height:60px;display:flex;flex-direction:column;gap:3px;justify-content:center;">
            <div style="height:4px;background:#334155;border-radius:1px;width:60%;"></div>
            <div style="height:4px;background:#334155;border-radius:1px;width:40%;"></div>
            <div style="height:4px;background:#334155;border-radius:1px;width:70%;"></div>
        </div>'''
    
    elif visual_hint == "grid":
        # Grille 3x2
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:grid;grid-template-columns:repeat(3,1fr);gap:3px;">
            <div style="background:#d0e6ff;border-radius:3px;"></div>
            <div style="background:#e0f8e0;border-radius:3px;"></div>
            <div style="background:#fff8a0;border-radius:3px;"></div>
            <div style="background:#ffe0d0;border-radius:3px;"></div>
            <div style="background:#f0d0ff;border-radius:3px;"></div>
            <div style="background:#d0f0ff;border-radius:3px;"></div>
        </div>'''
    
    elif visual_hint == "stencil-card":
        # Carte stencil
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:3px;justify-content:center;border-left:3px solid #e4bb5a;">
            <div style="height:6px;background:#e2e8f0;border-radius:1px;width:60%;"></div>
            <div style="display:flex;gap:3px;">
                <div style="flex:1;height:16px;background:#7aca6a;border-radius:2px;"></div>
                <div style="flex:1;height:16px;background:#e2e8f0;border-radius:2px;"></div>
            </div>
        </div>'''
    
    elif visual_hint == "button":
        # Bouton simple
        return f'''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;align-items:center;justify-content:center;">
            <div style="padding:8px 20px;background:{color};border-radius:4px;color:white;font-size:11px;font-weight:600;">Action</div>
        </div>'''
    
    elif visual_hint == "download":
        # Téléchargement
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;align-items:center;justify-content:center;">
            <span style="font-size:20px;color:#5a9ac6;">⬇</span>
        </div>'''
    
    elif visual_hint == "modal":
        # Modal
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:4px;justify-content:center;align-items:center;">
            <div style="width:70%;height:10px;background:#e2e8f0;border-radius:2px;"></div>
            <div style="display:flex;gap:4px;">
                <div style="width:40px;height:14px;background:#e2e8f0;border-radius:2px;"></div>
                <div style="width:40px;height:14px;background:#7aca6a;border-radius:2px;"></div>
            </div>
        </div>'''
    
    elif visual_hint == "breadcrumb":
        # Fil d'Ariane
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;align-items:center;justify-content:center;gap:4px;">
            <span style="color:#7aca6a;font-size:11px;font-weight:600;">A</span>
            <span style="color:#94a3b8;">/</span>
            <span style="color:#64748b;font-size:11px;">B</span>
        </div>'''
    
    elif visual_hint == "accordion":
        # Accordéon
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:3px;justify-content:center;">
            <div style="display:flex;align-items:center;gap:4px;">
                <span style="color:#7aca6a;font-size:10px;">▼</span>
                <div style="flex:1;height:6px;background:#e2e8f0;border-radius:1px;"></div>
            </div>
            <div style="display:flex;align-items:center;gap:4px;">
                <span style="color:#94a3b8;font-size:10px;">▶</span>
                <div style="flex:1;height:6px;background:#e2e8f0;border-radius:1px;"></div>
            </div>
        </div>'''
    
    elif visual_hint == "launch-button":
        # Bouton fusée
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;align-items:center;justify-content:center;">
            <div style="padding:10px 24px;background:linear-gradient(145deg,#7aca6a 0%,#6aba5a 100%);border-radius:20px;color:white;font-size:11px;font-weight:700;">🚀 GO</div>
        </div>'''
    
    elif visual_hint == "apply-changes":
        # Appliquer changements
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;align-items:center;justify-content:center;gap:6px;">
            <div style="padding:8px 16px;background:#7aca6a;border-radius:4px;color:white;font-size:11px;">✓</div>
            <div style="padding:8px 16px;background:#e2e8f0;border-radius:4px;color:#64748b;font-size:11px;">✕</div>
        </div>'''
    
    elif visual_hint == "chat-input":
        # Input chat
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;align-items:center;gap:4px;">
            <div style="flex:1;height:28px;background:white;border:1px solid #e2e8f0;border-radius:14px;"></div>
            <div style="width:28px;height:28px;background:#6a8aca;border-radius:50%;"></div>
        </div>'''
    
    elif visual_hint == "list":
        # Liste
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:4px;justify-content:center;">
            <div style="display:flex;align-items:center;gap:4px;"><div style="width:4px;height:4px;background:#7aca6a;border-radius:50%;"></div><div style="flex:1;height:5px;background:#e2e8f0;border-radius:1px;"></div></div>
            <div style="display:flex;align-items:center;gap:4px;"><div style="width:4px;height:4px;background:#e2e8f0;border-radius:50%;"></div><div style="flex:1;height:5px;background:#e2e8f0;border-radius:1px;"></div></div>
        </div>'''
    
    elif visual_hint == "card":
        # Carte simple
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:3px;justify-content:center;border:1px solid #e2e8f0;">
            <div style="height:8px;background:#cbd5e1;border-radius:2px;width:50%;"></div>
            <div style="height:4px;background:#e2e8f0;border-radius:1px;"></div>
        </div>'''
    
    else:
        # Générique
        return f'''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;align-items:center;justify-content:center;">
            <div style="width:36px;height:36px;background:{color}20;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;color:{color};">◆</div>
        </div>'''


def generate_component_card(comp):
    """Génère une carte de composant avec son wireframe"""
    comp_id = comp.get('id', 'unknown')
    name = comp.get('name', 'Sans nom')
    endpoint = comp.get('endpoint', 'N/A')
    method = comp.get('method', 'GET')
    visual_hint = comp.get('visual_hint', 'generic')
    description = comp.get('description_ui', '')[:60] + '...' if comp.get('description_ui') else ''
    
    color = get_method_color(method)
    wireframe = generate_wireframe(visual_hint, color)
    
    return f'''
    <div class="comp-card" onclick="toggleCheckbox('comp-{comp_id}')" data-corps="{comp.get('corps', 'all')}">
        {wireframe}
        <div class="comp-info">
            <div class="comp-name" title="{name}">{name}</div>
            <div class="comp-endpoint" title="{endpoint}">{endpoint}</div>
        </div>
        <div class="comp-footer">
            <span class="comp-method" style="background:{color}20;color:{color};">{method}</span>
            <input type="checkbox" id="comp-{comp_id}" class="comp-checkbox" value="{comp_id}" onclick="event.stopPropagation();updateValidateButton()">
        </div>
    </div>
    '''


def collect_components_by_level(genome):
    """Collecte tous les composants par niveau hiérarchique"""
    corps_list = []
    organes_list = []
    cellules_list = []
    atomes_list = []
    
    # Noms explicites des Corps (4)
    corps_names = {
        'n0_brainstorm': 'Brainstorm',
        'n0_backend': 'Backend', 
        'n0_frontend': 'Frontend',
        'n0_deploy': 'Deploy'
    }
    
    # Noms explicites des Organes (10)
    organes_names = {
        'n1_ir': 'Intent Refactoring',
        'n1_arbitrage': 'Arbitrage',
        'n1_session': 'Session Management',
        'n1_navigation': 'Navigation',
        'n1_layout': 'Layout Selection',
        'n1_upload': 'Upload Design',
        'n1_analysis': 'Analyse PNG',
        'n1_dialogue': 'Dialogue Utilisateur',
        'n1_validation': 'Validation Composants',
        'n1_adaptation': 'Adaptation / Zoom Atome',
        'n1_export': 'Export / Téléchargement'
    }
    
    # Noms explicites des Cellules
    cellules_names = {
        'n2_ir_report': 'Rapport IR',
        'n2_stencils': 'Stencils HCI',
        'n2_session_mgmt': 'Gestion Session',
        'n2_stepper': 'Navigation UX',
        'n2_layouts': 'Galerie Layouts',
        'n2_upload': 'Upload et Extraction',
        'n2_vision_analysis': 'Rapport Visuel',
        'n2_chat': 'Interface Chat',
        'n2_validation': 'Récap Global',
        'n2_zoom': 'Navigation Zoom',
        'n2_export': 'Export Projet'
    }
    
    for phase in genome.get('n0_phases', []):
        phase_id = phase.get('id', 'unknown')
        phase_name = corps_names.get(phase_id, phase.get('name', 'Unknown'))
        
        for section in phase.get('n1_sections', []):
            section_id = section.get('id', 'unknown')
            section_name = organes_names.get(section_id, section.get('name', 'Unknown'))
            
            for feature in section.get('n2_features', []):
                feature_id = feature.get('id', 'unknown')
                feature_name = cellules_names.get(feature_id, feature.get('name', 'Unknown'))
                
                for comp in feature.get('n3_components', []):
                    # Enrichir le composant avec les infos hiérarchiques
                    comp['corps'] = phase_id.replace('n0_', '')
                    comp['corps_name'] = phase_name
                    comp['organe_name'] = section_name
                    comp['cellule_name'] = feature_name
                    
                    # Utiliser le vrai nom explicite du composant
                    if 'name' not in comp or comp['name'].startswith('Vue'):
                        comp['name'] = comp.get('name', 'Composant')
                    
                    atomes_list.append(comp)
                    
                    # Créer des pseudo-composants pour les niveaux supérieurs
                    cellule_comp = {
                        'id': feature_id,
                        'name': feature_name,
                        'endpoint': f'/cellule/{feature_id}',
                        'method': 'GET',
                        'visual_hint': 'detail-card',
                        'corps': phase_id.replace('n0_', ''),
                        'description_ui': f'Cellule: {feature_name}'
                    }
                    if cellule_comp['id'] not in [c['id'] for c in cellules_list]:
                        cellules_list.append(cellule_comp)
                
                organe_comp = {
                    'id': section_id,
                    'name': section_name,
                    'endpoint': f'/organe/{section_id}',
                    'method': 'GET',
                    'visual_hint': 'stencil-card',
                    'corps': phase_id.replace('n0_', ''),
                    'description_ui': f'Organe: {section_name}'
                }
                if organe_comp['id'] not in [c['id'] for c in organes_list]:
                    organes_list.append(organe_comp)
        
        corps_comp = {
            'id': phase_id,
            'name': phase_name,
            'endpoint': f'/corps/{phase_id}',
            'method': 'GET',
            'visual_hint': 'dashboard',
            'corps': phase_id.replace('n0_', ''),
            'description_ui': f'Corps: {phase_name}'
        }
        corps_list.append(corps_comp)
    
    return corps_list, organes_list, cellules_list, atomes_list


def generate_html(genome):
    """Génère la page HTML complète"""
    
    corps_list, organes_list, cellules_list, atomes_list = collect_components_by_level(genome)
    
    total = len(atomes_list)
    confidence = int(genome.get('metadata', {}).get('confidence_global', 0.85) * 100)
    
    # Générer les rows
    corps_cards = ''.join(generate_component_card(c) for c in corps_list)
    organes_cards = ''.join(generate_component_card(c) for c in organes_list)
    cellules_cards = ''.join(generate_component_card(c) for c in cellules_list)
    atomes_cards = ''.join(generate_component_card(c) for c in atomes_list)
    
    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HoméOS - Genome Viewer (Port 9998)</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; overflow: hidden; background: #f8fafc; }}
        
        /* Tabs */
        .tabs {{ 
            display: flex; 
            height: 52px; 
            background: #fff; 
            border-bottom: 1px solid #e2e8f0; 
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .tab {{ 
            flex: 1; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            cursor: pointer; 
            font-size: 14px; 
            color: #64748b; 
            border-right: 1px solid #f1f5f9; 
            transition: all 0.2s; 
            font-weight: 500; 
        }}
        .tab:last-child {{ border-right: none; }}
        .tab:hover {{ background: linear-gradient(180deg, #fff 0%, #f8fafc 100%); color: #334155; }}
        .tab.active {{ 
            background: transparent; 
            color: #1e293b; 
            font-weight: 700; 
            border-bottom: 3px solid #7aca6a; 
        }}
        
        /* Main Layout */
        .main {{ display: flex; height: calc(100vh - 52px); }}
        
        /* Sidebar */
        .sidebar {{ 
            width: 280px; 
            background: linear-gradient(180deg, #fff 0%, #fafafa 100%); 
            border-right: 1px solid #e2e8f0; 
            overflow-y: auto; 
            flex-shrink: 0;
        }}
        .sidebar-header {{ padding: 20px; border-bottom: 1px solid #e2e8f0; }}
        .sidebar-title {{ font-size: 22px; font-weight: 800; color: #7aca6a; }}
        .sidebar-subtitle {{ font-size: 12px; color: #94a3b8; margin-top: 4px; }}
        .sidebar-section {{ padding: 18px; border-bottom: 1px solid #f1f5f9; }}
        .sidebar-label {{ 
            font-size: 12px; 
            font-weight: 700; 
            color: #94a3b8; 
            text-transform: uppercase; 
            letter-spacing: 0.8px; 
            margin-bottom: 14px; 
        }}
        
        /* Content */
        .content {{ 
            flex: 1; 
            overflow-y: auto; 
            padding: 24px; 
            background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        
        h1 {{ font-size: 24px; font-weight: 800; color: #1e293b; margin-bottom: 8px; }}
        .subtitle {{ font-size: 14px; color: #64748b; margin-bottom: 24px; }}
        
        .section {{ margin-bottom: 32px; }}
        .section-title {{ 
            font-size: 13px; 
            font-weight: 700; 
            color: #64748b; 
            text-transform: uppercase; 
            letter-spacing: 1px;
            margin-bottom: 16px; 
            padding: 10px 14px;
            background: white;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .section-title::before {{
            content: '';
            width: 4px;
            height: 16px;
            background: #7aca6a;
            border-radius: 2px;
        }}
        
        .row {{ 
            display: flex; 
            gap: 16px; 
            flex-wrap: wrap;
            padding: 4px;
        }}
        
        .comp-card {{
            width: calc(16.666% - 14px);
            min-width: 150px;
            max-width: 200px;
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            overflow: hidden;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .comp-card:hover {{ 
            box-shadow: 0 8px 24px rgba(0,0,0,0.12); 
            transform: translateY(-4px);
            border-color: #7aca6a;
        }}
        .comp-card.selected {{ 
            border-color: #7aca6a; 
            box-shadow: 0 0 0 3px rgba(122,202,106,0.2); 
        }}
        .comp-card.hidden {{ display: none; }}
        
        .comp-info {{ padding: 10px 12px; border-bottom: 1px solid #f1f5f9; }}
        .comp-name {{ 
            font-size: 12px; 
            font-weight: 700; 
            color: #1e293b; 
            white-space: nowrap; 
            overflow: hidden; 
            text-overflow: ellipsis; 
            margin-bottom: 4px; 
        }}
        .comp-endpoint {{ 
            font-size: 10px; 
            color: #94a3b8; 
            font-family: 'SF Mono', Monaco, monospace; 
            white-space: nowrap; 
            overflow: hidden; 
            text-overflow: ellipsis; 
        }}
        
        .comp-footer {{ 
            display: flex; 
            align-items: center; 
            justify-content: space-between;
            padding: 8px 12px; 
            background: #fafafa;
        }}
        .comp-method {{ 
            font-size: 10px; 
            font-weight: 700; 
            text-transform: uppercase;
            padding: 3px 8px; 
            border-radius: 4px;
        }}
        .comp-checkbox {{ 
            width: 18px; 
            height: 18px; 
            accent-color: #7aca6a; 
            cursor: pointer;
        }}
        
        .sticky-header {{
            position: sticky;
            top: -24px;
            background: linear-gradient(180deg, rgba(248,250,252,0.98) 0%, rgba(241,245,249,0.98) 100%);
            padding: 16px 0;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #e2e8f0;
            z-index: 50;
        }}
        .validate-btn {{
            padding: 10px 24px;
            background: linear-gradient(145deg, #7aca6a 0%, #6aba5a 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            opacity: 0.5;
            transition: all 0.2s;
        }}
        .validate-btn:enabled {{ 
            opacity: 1;
        }}
        .validate-btn:enabled:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(122,202,106,0.4);
        }}
        
        .stat-box {{
            text-align: center;
            padding: 14px;
            background: linear-gradient(145deg, #fff 0%, #f8fafc 100%);
            border-radius: 10px;
            border: 1px solid #e2e8f0;
            transition: all 0.2s;
        }}
        .stat-box:hover {{
            border-color: #7aca6a;
            transform: translateY(-2px);
        }}
        .stat-number {{
            font-size: 24px;
            font-weight: 800;
            color: #7aca6a;
        }}
        .stat-label {{
            font-size: 11px;
            color: #94a3b8;
            font-weight: 600;
            text-transform: uppercase;
            margin-top: 4px;
        }}
        
        .type-indicator {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px;
            font-size: 13px;
            color: #64748b;
        }}
        .type-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }}
        
        @media (max-width: 1400px) {{ 
            .comp-card {{ width: calc(20% - 13px); }} 
        }}
        @media (max-width: 1100px) {{ 
            .comp-card {{ width: calc(25% - 12px); }} 
        }}
        @media (max-width: 900px) {{ 
            .comp-card {{ width: calc(33.333% - 11px); }} 
        }}
        @media (max-width: 600px) {{ 
            .comp-card {{ width: calc(50% - 8px); }} 
        }}
    </style>
</head>
<body>
    <div class="tabs">
        <div class="tab active" onclick="switchTab(this, 'all')">Tout</div>
        <div class="tab" onclick="switchTab(this, 'brs')">Brainstorm</div>
        <div class="tab" onclick="switchTab(this, 'bkd')">Backend</div>
        <div class="tab" onclick="switchTab(this, 'frd')">Frontend</div>
        <div class="tab" onclick="switchTab(this, 'dpl')">Deploy</div>
    </div>

    <div class="main">
        <aside class="sidebar">
            <div class="sidebar-header">
                <div class="sidebar-title">HoméOS</div>
                <div class="sidebar-subtitle">Architecture Genome v3.1</div>
            </div>
            <div class="sidebar-section">
                <div class="sidebar-label">Confiance globale</div>
                <div style="font-size: 42px; font-weight: 800; color: #7aca6a; letter-spacing: -2px;">{confidence}%</div>
            </div>
            <div class="sidebar-section">
                <div class="sidebar-label">Statistiques</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                    <div class="stat-box">
                        <div class="stat-number">4</div>
                        <div class="stat-label">phases</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" style="color:#5a9ac6;">{total}</div>
                        <div class="stat-label">composants</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" style="color:#e4bb5a;">{len(organes_list)}</div>
                        <div class="stat-label">organes</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" style="color:#64748b;">{len(cellules_list)}</div>
                        <div class="stat-label">cellules</div>
                    </div>
                </div>
            </div>
            <div class="sidebar-section">
                <div class="sidebar-label">Types de composants</div>
                <div style="font-size: 13px; line-height: 1.8;">
                    <div class="type-indicator"><span class="type-dot" style="background:#7aca6a;"></span><span>Indicateurs & Status</span></div>
                    <div class="type-indicator"><span class="type-dot" style="background:#5a9ac6;"></span><span>Navigation & Stepper</span></div>
                    <div class="type-indicator"><span class="type-dot" style="background:#e4bb5a;"></span><span>Cartes & Stencils</span></div>
                    <div class="type-indicator"><span class="type-dot" style="background:#64748b;"></span><span>Actions & Boutons</span></div>
                </div>
            </div>
        </aside>

        <div class="content">
            <div class="container">
                <div class="sticky-header">
                    <div style="display: flex; gap: 14px; align-items: center;">
                        <input type="checkbox" id="select-all" style="width: 22px; height: 22px; accent-color: #7aca6a; cursor: pointer;" onchange="toggleAll(this)">
                        <label for="select-all" style="font-size: 15px; color: #334155; cursor: pointer; font-weight: 600;">Tout sélectionner</label>
                    </div>
                    <button id="validate-btn" class="validate-btn" disabled>Valider (0)</button>
                </div>
                
                <h1>Architecture Genome</h1>
                <p class="subtitle">Visualisation hiérarchique: Corps → Organes → Cellules → Atomes</p>
                
                <!-- ROW 1: Corps -->
                <div class="section">
                    <div class="section-title">Corps (4 phases)</div>
                    <div class="row" id="row-corps">
                        {corps_cards}
                    </div>
                </div>
                
                <!-- ROW 2: Organes -->
                <div class="section">
                    <div class="section-title">Organes (10 sections fonctionnelles)</div>
                    <div class="row" id="row-organes">
                        {organes_cards}
                    </div>
                </div>
                
                <!-- ROW 3: Cellules -->
                <div class="section">
                    <div class="section-title">Cellules (features)</div>
                    <div class="row" id="row-cellules">
                        {cellules_cards}
                    </div>
                </div>
                
                <!-- ROW 4: Atomes -->
                <div class="section">
                    <div class="section-title">Atomes ({total} composants)</div>
                    <div class="row" id="row-atomes">
                        {atomes_cards}
                    </div>
                </div>
                
                <div style="height: 40px;"></div>
            </div>
        </div>
    </div>
    
    <script>
        // Mapping des tabs vers les corps
        const tabMapping = {{
            'all': 'all',
            'brs': 'brainstorm',
            'bkd': 'backend',
            'frd': 'frontend',
            'dpl': 'deploy'
        }};
        
        function switchTab(element, tab) {{
            // Mettre à jour les tabs
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            element.classList.add('active');
            
            // Filtrer les cartes
            const corpsFilter = tabMapping[tab];
            const cards = document.querySelectorAll('.comp-card');
            
            cards.forEach(card => {{
                if (corpsFilter === 'all' || card.dataset.corps === corpsFilter) {{
                    card.classList.remove('hidden');
                }} else {{
                    card.classList.add('hidden');
                }}
            }});
            
            // Mettre à jour le compteur
            updateValidateButton();
        }}
        
        function toggleAll(source) {{
            const visibleCards = document.querySelectorAll('.comp-card:not(.hidden)');
            visibleCards.forEach(card => {{
                const checkbox = card.querySelector('.comp-checkbox');
                if (checkbox) checkbox.checked = source.checked;
            }});
            updateValidateButton();
        }}
        
        function updateValidateButton() {{
            const count = document.querySelectorAll('.comp-checkbox:checked').length;
            const btn = document.getElementById('validate-btn');
            btn.innerHTML = 'Valider (' + count + ')';
            btn.disabled = count === 0;
        }}
        
        function toggleCheckbox(id) {{
            const cb = document.getElementById(id);
            if (cb) {{
                cb.checked = !cb.checked;
                updateValidateButton();
            }}
        }}
    </script>
</body>
</html>'''


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path.startswith('/studio'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            genome = load_genome()
            html = generate_html(genome)
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Log silencieux
        pass


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f"🧬 Genome Viewer running at http://localhost:{PORT}")
    print(f"📁 Serving genome from: {GENOME_FILE}")
    print("Press Ctrl+C to stop")
    server.serve_forever()
