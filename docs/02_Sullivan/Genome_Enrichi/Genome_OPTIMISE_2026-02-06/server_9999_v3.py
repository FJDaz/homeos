#!/usr/bin/env python3
"""
Serveur HTTP pour visualisation du Genome - Port 9999
Version 5.0 - Layout Hiérarchique N0-N3 (Design de Référence)
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

PORT = 9999
GENOME_FILE = "genome_inferred_kimi_innocent_v2.json"

def normalize_keys(obj):
    if isinstance(obj, dict):
        return {k.lower(): normalize_keys(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [normalize_keys(item) for item in obj]
    return obj

def load_genome():
    if os.path.exists(GENOME_FILE):
        with open(GENOME_FILE, 'r') as f:
            data = json.load(f)
            data = normalize_keys(data)
            if 'n0_phases' not in data:
                data['n0_phases'] = []
            if 'metadata' not in data:
                data['metadata'] = {'confidence_global': 0.85}
            return data
    return {"n0_phases": [], "metadata": {"confidence_global": 0.0}}


def get_method_color(method):
    colors = {"GET": "#7aca6a", "POST": "#5a9ac6", "PUT": "#e4bb5a", "DELETE": "#d56363"}
    return colors.get(method, "#64748b")


def generate_wireframe(visual_hint, color="#7aca6a"):
    """Generate wireframe based on visual hint"""
    if visual_hint == "table":
        return f'<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:3px;justify-content:center;"><div style="display:flex;gap:3px;"><div style="flex:2;height:5px;background:#e2e8f0;border-radius:1px;"></div><div style="flex:1;height:5px;background:#e2e8f0;border-radius:1px;"></div></div><div style="display:flex;gap:3px;"><div style="flex:2;height:5px;background:#e2e8f0;border-radius:1px;"></div><div style="flex:1;height:5px;background:{color};border-radius:1px;"></div></div></div>'
    elif visual_hint == "detail-card":
        return f'<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:3px;justify-content:center;"><div style="height:6px;background:{color};border-radius:2px;width:30%;"></div><div style="height:4px;background:#e2e8f0;border-radius:1px;"></div><div style="height:4px;background:#e2e8f0;border-radius:1px;width:80%;"></div></div>'
    elif visual_hint == "stencil-card":
        return '<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:3px;justify-content:center;border-left:3px solid #e4bb5a;"><div style="height:6px;background:#e2e8f0;border-radius:1px;width:60%;margin-left:8px;"></div><div style="display:flex;gap:3px;margin-left:8px;"><div style="flex:1;height:16px;background:#7aca6a;border-radius:2px;"></div><div style="flex:1;height:16px;background:#e2e8f0;border-radius:2px;"></div></div></div>'
    elif visual_hint == "form":
        return '<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:4px;justify-content:center;"><div style="height:8px;background:#e2e8f0;border-radius:2px;width:40%;"></div><div style="height:16px;background:white;border:1px solid #e2e8f0;border-radius:2px;"></div></div>'
    elif visual_hint == "status":
        return '<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;gap:8px;justify-content:center;align-items:center;"><div style="width:12px;height:12px;background:#7aca6a;border-radius:50%;"></div><div style="width:12px;height:12px;background:#7aca6a;border-radius:50%;"></div><div style="width:12px;height:12px;background:#7aca6a;border-radius:50%;"></div><div style="width:12px;height:12px;background:#e2e8f0;border-radius:50%;"></div></div>'
    elif visual_hint == "dashboard":
        return '<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;gap:3px;align-items:flex-end;justify-content:center;"><div style="width:12%;height:30%;background:#7aca6a;border-radius:2px 2px 0 0;"></div><div style="width:12%;height:50%;background:#7aca6a;border-radius:2px 2px 0 0;"></div><div style="width:12%;height:35%;background:#5a9ac6;border-radius:2px 2px 0 0;"></div><div style="width:12%;height:60%;background:#7aca6a;border-radius:2px 2px 0 0;"></div></div>'
    elif visual_hint == "list":
        return '<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:4px;justify-content:center;"><div style="display:flex;align-items:center;gap:4px;"><div style="width:4px;height:4px;background:#7aca6a;border-radius:50%;"></div><div style="flex:1;height:5px;background:#e2e8f0;border-radius:1px;"></div></div><div style="display:flex;align-items:center;gap:4px;"><div style="width:4px;height:4px;background:#e2e8f0;border-radius:50%;"></div><div style="flex:1;height:5px;background:#e2e8f0;border-radius:1px;"></div></div></div>'
    elif visual_hint == "stepper":
        return '<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;gap:4px;justify-content:center;align-items:center;"><div style="width:16px;height:16px;background:#7aca6a;border-radius:50%;"></div><div style="flex:1;height:2px;background:#7aca6a;"></div><div style="width:16px;height:16px;background:#7aca6a;border-radius:50%;"></div><div style="flex:1;height:2px;background:#e2e8f0;"></div><div style="width:16px;height:16px;background:#e2e8f0;border-radius:50%;"></div></div>'
    elif visual_hint == "breadcrumb":
        return '<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;align-items:center;justify-content:center;gap:4px;"><span style="color:#7aca6a;font-size:11px;font-weight:600;">A</span><span style="color:#94a3b8;">&gt;</span><span style="color:#64748b;font-size:11px;">B</span></div>'
    elif visual_hint == "grid":
        return '<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:grid;grid-template-columns:repeat(3,1fr);gap:3px;"><div style="background:#d0e6ff;border-radius:3px;"></div><div style="background:#e0f8e0;border-radius:3px;"></div><div style="background:#fff8a0;border-radius:3px;"></div></div>'
    elif visual_hint == "card":
        return f'<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:3px;justify-content:center;border-left:3px solid {color};"><div style="height:6px;background:{color};border-radius:2px;width:30%;margin-left:8px;"></div><div style="height:4px;background:#e2e8f0;border-radius:1px;margin-left:8px;"></div></div>'
    elif visual_hint == "choice-card":
        return '<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;gap:6px;justify-content:center;align-items:center;"><div style="width:32px;height:32px;background:white;border:2px solid #7aca6a;border-radius:6px;"></div><div style="width:32px;height:32px;background:#f1f5f9;border:1px solid #e2e8f0;border-radius:6px;"></div></div>'
    elif visual_hint == "upload":
        return '<div style="background:#f8fafc;border:1px dashed #cbd5e1;border-radius:4px;height:60px;display:flex;align-items:center;justify-content:center;"><span style="font-size:24px;">+</span></div>'
    elif visual_hint == "color-palette":
        return '<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;gap:4px;justify-content:center;align-items:center;"><div style="width:18px;height:18px;background:#5a9ac6;border-radius:4px;"></div><div style="width:18px;height:18px;background:#7aca6a;border-radius:4px;"></div><div style="width:18px;height:18px;background:#e4bb5a;border-radius:4px;"></div><div style="width:18px;height:18px;background:#1e293b;border-radius:4px;"></div></div>'
    elif visual_hint == "preview":
        return '<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;gap:3px;justify-content:center;align-items:center;"><div style="width:25%;height:40px;background:rgba(59,130,246,0.2);border:1px dashed #5a9ac6;border-radius:3px;"></div><div style="width:35%;height:40px;background:rgba(140,198,63,0.2);border:1px dashed #7aca6a;border-radius:3px;"></div><div style="width:20%;height:40px;background:rgba(236,72,153,0.15);border:1px dashed #ec4899;border-radius:3px;"></div></div>'
    elif visual_hint == "chat/bubble":
        return '<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:4px;justify-content:center;"><div style="display:flex;gap:4px;"><div style="width:16px;height:16px;background:#6a8aca;border-radius:50%;"></div><div style="flex:1;height:12px;background:#e2e8f0;border-radius:6px;"></div></div><div style="display:flex;gap:4px;justify-content:flex-end;"><div style="width:50%;height:12px;background:#6a8aca;border-radius:6px;"></div></div></div>'
    elif visual_hint == "chat-input":
        return '<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;align-items:center;gap:4px;"><div style="flex:1;height:28px;background:white;border:1px solid #e2e8f0;border-radius:14px;"></div><div style="width:28px;height:28px;background:#6a8aca;border-radius:50%;"></div></div>'
    elif visual_hint == "accordion":
        return '<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:3px;justify-content:center;"><div style="display:flex;align-items:center;gap:4px;"><span style="color:#64748b;font-size:10px;">V</span><div style="flex:1;height:6px;background:#e2e8f0;border-radius:1px;"></div></div><div style="display:flex;align-items:center;gap:4px;"><span style="color:#64748b;font-size:10px;">&gt;</span><div style="flex:1;height:6px;background:#e2e8f0;border-radius:1px;"></div></div></div>'
    elif visual_hint == "zoom-controls":
        return '<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;gap:4px;align-items:center;justify-content:center;"><span style="padding:4px 8px;background:#e2e8f0;border-radius:3px;font-size:10px;">&lt;</span><span style="padding:4px 8px;background:#5a9ac6;border-radius:3px;font-size:10px;color:white;">N0</span><span style="padding:4px 8px;background:#e2e8f0;border-radius:3px;font-size:10px;">&gt;</span></div>'
    elif visual_hint == "editor":
        return '<div style="background:#1e293b;border-radius:4px;padding:6px;height:60px;display:flex;flex-direction:column;gap:3px;justify-content:center;"><div style="height:4px;background:#334155;border-radius:1px;width:60%;"></div><div style="height:4px;background:#334155;border-radius:1px;width:40%;"></div></div>'
    elif visual_hint == "launch-button":
        return '<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;align-items:center;justify-content:center;"><div style="padding:10px 24px;background:linear-gradient(145deg,#7aca6a 0%,#6aba5a 100%);border-radius:20px;color:white;font-size:12px;font-weight:700;">GO</div></div>'
    elif visual_hint == "apply-changes":
        return '<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;align-items:center;justify-content:center;gap:6px;"><div style="padding:8px 16px;background:#7aca6a;border-radius:4px;color:white;font-size:11px;">OK</div><div style="padding:8px 16px;background:#e2e8f0;border-radius:4px;color:#64748b;font-size:11px;">KO</div></div>'
    elif visual_hint == "download":
        return '<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;align-items:center;justify-content:center;"><span style="font-size:28px;">DL</span></div>'
    elif visual_hint == "modal":
        return '<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:4px;justify-content:center;align-items:center;"><div style="width:70%;height:10px;background:#e2e8f0;border-radius:2px;"></div><div style="display:flex;gap:4px;"><div style="width:40px;height:14px;background:#e2e8f0;border-radius:2px;"></div><div style="width:40px;height:14px;background:#7aca6a;border-radius:2px;"></div></div></div>'
    elif visual_hint == "button":
        return f'<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;align-items:center;justify-content:center;"><div style="padding:8px 20px;background:{color};border-radius:4px;color:white;font-size:12px;font-weight:600;">Btn</div></div>'
    else:
        return f'<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;align-items:center;justify-content:center;"><div style="width:36px;height:36px;background:{color}15;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;color:{color};">#</div></div>'


def generate_component_card(comp):
    """Generate a simple component card"""
    comp_id = comp.get('id', 'unknown')
    name = comp.get('name', 'Sans nom')
    endpoint = comp.get('endpoint', 'N/A')
    method = comp.get('method', 'GET')
    visual_hint = comp.get('visual_hint', 'generic')
    description = comp.get('description_ui', '')[:50] + '...' if comp.get('description_ui') else ''
    
    color = get_method_color(method)
    wireframe = generate_wireframe(visual_hint, color)
    
    return f'''
    <div class="comp-card" onclick="toggleCheckbox('comp-{comp_id}')">
        {wireframe}
        <div class="comp-info">
            <div class="comp-name">{name}</div>
            <div class="comp-endpoint">{endpoint}</div>
        </div>
        <div class="comp-footer">
            <span class="comp-method" style="background:{color}15;color:{color};">{method}</span>
            <input type="checkbox" id="comp-{comp_id}" class="comp-checkbox" value="{comp_id}" onclick="event.stopPropagation();updateValidateButton()">
        </div>
    </div>
    '''


def generate_n3_grid(components):
    """Generate N3 Atomes grid"""
    if not components:
        return '<div style="color:#94a3b8;padding:20px;">Aucun atome</div>'
    
    html = '<div class="n3-grid">'
    for comp in components:
        html += generate_component_card(comp)
    html += '</div>'
    return html


def generate_n2_cellules(cellules, n0_id, n1_id):
    """Generate N2 Cellules row"""
    if not cellules:
        return ''
    
    html = f'<div class="n2-row" id="n2-{n0_id}-{n1_id}">'
    for cell in cellules:
        cell_id = cell.get('id', 'unknown')
        cell_name = cell.get('name', 'Sans nom')
        atomes = cell.get('n3_components', [])
        count = len(atomes)
        
        html += f'''
        <div class="level-card n2-card" onclick="toggleN3('{n0_id}-{n1_id}-{cell_id}')">
            <div class="level-card-header">
                <span class="level-icon">⚙️</span>
                <span class="level-card-title">{cell_name}</span>
                <span class="level-card-count">{count} atome{'s' if count > 1 else ''}</span>
            </div>
            <div class="level-card-content" id="n3-content-{n0_id}-{n1_id}-{cell_id}" onclick="event.stopPropagation();">
                {generate_n3_grid(atomes)}
            </div>
        </div>
        '''
    html += '</div>'
    return html


def generate_n1_organes(organes, n0_id):
    """Generate N1 Organes row"""
    if not organes:
        return ''
    
    html = f'<div class="n1-row" id="n1-{n0_id}">'
    for org in organes:
        org_id = org.get('id', 'unknown')
        org_name = org.get('name', 'Sans nom')
        cellules = org.get('n2_features', [])
        total_atom = sum(len(c.get('n3_components', [])) for c in cellules)
        count_cell = len(cellules)
        
        html += f'''
        <div class="level-card n1-card" onclick="toggleN2('{n0_id}-{org_id}')">
            <div class="level-card-header">
                <span class="level-icon">🔧</span>
                <span class="level-card-title">{org_name}</span>
                <span class="level-card-count">{count_cell} cellule{'s' if count_cell > 1 else ''} · {total_atom} atome{'s' if total_atom > 1 else ''}</span>
            </div>
            <div class="level-card-content" id="n2-content-{n0_id}-{org_id}">
                {generate_n2_cellules(cellules, n0_id, org_id)}
            </div>
        </div>
        '''
    html += '</div>'
    return html


def generate_n0_corps(phases):
    """Generate N0 Corps row"""
    if not phases:
        return '<div style="color:#94a3b8;padding:20px;">Aucun corps</div>'
    
    html = '<div class="n0-row">'
    for phase in phases:
        phase_id = phase.get('id', 'unknown')
        phase_name = phase.get('name', 'Sans nom')
        organes = phase.get('n1_sections', [])
        
        # Count totals
        total_cell = sum(len(s.get('n2_features', [])) for s in organes)
        total_atom = sum(
            len(f.get('n3_components', [])) 
            for s in organes 
            for f in s.get('n2_features', [])
        )
        count_org = len(organes)
        
        html += f'''
        <div class="level-card n0-card" onclick="toggleN1('{phase_id}')">
            <div class="level-card-header">
                <span class="level-icon">📦</span>
                <span class="level-card-title">{phase_name}</span>
            </div>
            <div class="level-card-body">
                <span class="level-card-count">{count_org} organe{'s' if count_org > 1 else ''} · {total_cell} cellule{'s' if total_cell > 1 else ''} · {total_atom} atome{'s' if total_atom > 1 else ''}</span>
            </div>
            <div class="level-card-content" id="n1-content-{phase_id}">
                {generate_n1_organes(organes, phase_id)}
            </div>
        </div>
        '''
    html += '</div>'
    return html


def generate_html(genome):
    # Calculate stats
    total_phases = len(genome.get('n0_phases', []))
    total_components = sum(
        len(f.get('n3_components', []))
        for p in genome.get('n0_phases', [])
        for s in p.get('n1_sections', [])
        for f in s.get('n2_features', [])
    )
    
    n0_html = generate_n0_corps(genome.get('n0_phases', []))
    
    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HoméOS - Genome Viewer N0-N3</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; overflow: hidden; background: #f8fafc; }}
        
        /* Tabs */
        .tabs {{ display: flex; height: 52px; background: #fff; border-bottom: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
        .tab {{ flex: 1; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 14px; color: #64748b; border-right: 1px solid #f1f5f9; transition: all 0.2s; font-weight: 500; }}
        .tab:last-child {{ border-right: none; }}
        .tab:hover {{ background: linear-gradient(180deg, #fff 0%, #f8fafc 100%); color: #334155; }}
        .tab.active {{ background: transparent; color: #1e293b; font-size: 1.2em; font-weight: 900; border-bottom: 3px solid #7aca6a; padding-bottom: 10px; }}
        
        /* Main Layout */
        .main {{ display: flex; height: calc(100vh - 52px); }}
        
        /* Sidebar */
        .sidebar {{ width: 280px; background: linear-gradient(180deg, #fff 0%, #fafafa 100%); border-right: 1px solid #e2e8f0; overflow-y: auto; flex-shrink: 0; }}
        .sidebar-header {{ padding: 20px; border-bottom: 1px solid #e2e8f0; }}
        .sidebar-title {{ font-size: 22px; font-weight: 800; color: #7aca6a; }}
        .sidebar-subtitle {{ font-size: 12px; color: #94a3b8; margin-top: 4px; }}
        .sidebar-section {{ padding: 18px; border-bottom: 1px solid #f1f5f9; }}
        .sidebar-label {{ font-size: 12px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 14px; }}
        
        /* Content */
        .content {{ flex: 1; overflow-y: auto; padding: 24px; background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%); }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        
        h1 {{ font-size: 24px; font-weight: 800; color: #1e293b; margin-bottom: 8px; }}
        .subtitle {{ font-size: 14px; color: #64748b; margin-bottom: 24px; }}
        
        /* Sticky Header */
        .sticky-header {{
            position: sticky; top: -24px;
            background: linear-gradient(180deg, rgba(248,250,252,0.98) 0%, rgba(241,245,249,0.98) 100%);
            padding: 16px 0; margin-bottom: 20px;
            display: flex; justify-content: space-between; align-items: center;
            border-bottom: 1px solid #e2e8f0;
            z-index: 100;
        }}
        .validate-btn {{
            padding: 10px 20px; background: linear-gradient(145deg, #7aca6a 0%, #6aba5a 100%);
            color: white; border: none; border-radius: 8px;
            font-size: 14px; font-weight: 700; cursor: pointer;
            opacity: 0.5;
        }}
        .validate-btn:enabled {{ opacity: 1; }}
        
        /* === N0-N3 HIERARCHY LAYOUT === */
        
        /* N0 - Corps Level */
        .n0-row {{
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
            margin-bottom: 24px;
        }}
        
        /* N1 - Organes Level */
        .n1-row {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 16px;
        }}
        
        /* N2 - Cellules Level */
        .n2-row {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 12px;
        }}
        
        /* N3 - Atomes Grid */
        .n3-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
            gap: 12px;
            margin-top: 12px;
        }}
        
        /* Level Cards */
        .level-card {{
            background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 16px;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .level-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }}
        
        /* N0 Card - Corps (Green) */
        .n0-card {{
            flex: 1;
            min-width: 220px;
            max-width: calc(25% - 12px);
            border-left: 4px solid #7aca6a;
        }}
        .n0-card .level-card-title {{
            color: #7aca6a;
            font-size: 16px;
            font-weight: 700;
        }}
        
        /* N1 Card - Organes (Blue) */
        .n1-card {{
            flex: 1;
            min-width: 200px;
            max-width: calc(50% - 6px);
            border-left: 3px solid #5a9ac6;
        }}
        .n1-card .level-card-title {{
            color: #5a9ac6;
            font-size: 14px;
            font-weight: 600;
        }}
        
        /* N2 Card - Cellules (Yellow) */
        .n2-card {{
            flex: 1;
            min-width: 180px;
            max-width: calc(50% - 6px);
            border-left: 2px solid #e4bb5a;
        }}
        .n2-card .level-card-title {{
            color: #e4bb5a;
            font-size: 13px;
            font-weight: 600;
        }}
        
        /* Card Header */
        .level-card-header {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px;
        }}
        .level-icon {{
            font-size: 14px;
        }}
        .level-card-title {{
            flex: 1;
        }}
        .level-card-count {{
            font-size: 11px;
            color: #64748b;
            background: #f1f5f9;
            padding: 2px 8px;
            border-radius: 10px;
            white-space: nowrap;
        }}
        .level-card-body {{
            margin-top: 8px;
        }}
        
        /* Card Content (Collapsible) */
        .level-card-content {{
            display: none;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px dashed #e2e8f0;
        }}
        .level-card-content.open {{
            display: block;
        }}
        
        /* Component Card */
        .comp-card {{
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            overflow: hidden;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        }}
        .comp-card:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            transform: translateY(-2px);
            border-color: #cbd5e1;
        }}
        .comp-info {{
            padding: 10px 12px;
            border-bottom: 1px solid #f1f5f9;
        }}
        .comp-name {{
            font-size: 12px;
            font-weight: 700;
            color: #1e293b;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-bottom: 2px;
        }}
        .comp-endpoint {{
            font-size: 10px;
            color: #94a3b8;
            font-family: monospace;
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
            font-size: 9px;
            font-weight: 700;
            text-transform: uppercase;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        .comp-checkbox {{
            width: 16px;
            height: 16px;
            accent-color: #7aca6a;
            cursor: pointer;
        }}
        
        /* Responsive */
        @media (max-width: 1200px) {{
            .n0-card {{ max-width: calc(50% - 8px); }}
        }}
        @media (max-width: 768px) {{
            .n0-card {{ max-width: 100%; }}
            .n1-card {{ max-width: 100%; }}
            .n2-card {{ max-width: 100%; }}
            .sidebar {{ display: none; }}
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
                <div class="sidebar-subtitle">Architecture Genome N0-N3</div>
            </div>
            <div class="sidebar-section">
                <div class="sidebar-label">Confiance globale</div>
                <div style="font-size: 42px; font-weight: 800; color: #7aca6a; letter-spacing: -2px;">{int(genome.get('metadata', {}).get('confidence_global', 0) * 100)}%</div>
            </div>
            <div class="sidebar-section">
                <div class="sidebar-label">Statistiques</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                    <div style="text-align: center; padding: 14px; background: linear-gradient(145deg, #fff 0%, #f8fafc 100%); border-radius: 10px; border: 1px solid #e2e8f0;">
                        <div style="font-size: 24px; font-weight: 800; color: #7aca6a;">{total_phases}</div>
                        <div style="font-size: 11px; color: #94a3b8; font-weight: 600; text-transform: uppercase; margin-top: 4px;">Corps (N0)</div>
                    </div>
                    <div style="text-align: center; padding: 14px; background: linear-gradient(145deg, #fff 0%, #f8fafc 100%); border-radius: 10px; border: 1px solid #e2e8f0;">
                        <div style="font-size: 24px; font-weight: 800; color: #5a9ac6;">{total_components}</div>
                        <div style="font-size: 11px; color: #94a3b8; font-weight: 600; text-transform: uppercase; margin-top: 4px;">Atomes (N3)</div>
                    </div>
                </div>
            </div>
            <div class="sidebar-section">
                <div class="sidebar-label">Hiérarchie</div>
                <div style="font-size: 13px; color: #64748b; line-height: 1.8;">
                    <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;"><span style="width:12px;height:12px;background:#7aca6a;border-radius:2px;"></span><span><strong>N0</strong> Corps (Phases)</span></div>
                    <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;"><span style="width:12px;height:12px;background:#5a9ac6;border-radius:2px;"></span><span><strong>N1</strong> Organes (Sections)</span></div>
                    <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;"><span style="width:12px;height:12px;background:#e4bb5a;border-radius:2px;"></span><span><strong>N2</strong> Cellules (Features)</span></div>
                    <div style="display:flex;align-items:center;gap:6px;"><span style="width:12px;height:12px;background:#64748b;border-radius:2px;"></span><span><strong>N3</strong> Atomes (Composants)</span></div>
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
                <p class="subtitle">Corps <span style="color:#94a3b8;">›</span> Organes <span style="color:#94a3b8;">›</span> Cellules <span style="color:#94a3b8;">›</span> Atomes</p>
                
                <div class="hierarchy-container">
                    <div style="font-size: 12px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;">N0 - Corps (Phases)</div>
                    {n0_html}
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function switchTab(element, tab) {{
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            element.classList.add('active');
        }}
        
        function toggleN1(n0Id) {{
            const content = document.getElementById('n1-content-' + n0Id);
            if (content) {{
                content.classList.toggle('open');
            }}
        }}
        
        function toggleN2(n0n1Id) {{
            const content = document.getElementById('n2-content-' + n0n1Id);
            if (content) {{
                content.classList.toggle('open');
            }}
        }}
        
        function toggleN3(n0n1n2Id) {{
            const content = document.getElementById('n3-content-' + n0n1n2Id);
            if (content) {{
                content.classList.toggle('open');
            }}
        }}
        
        function toggleAll(source) {{
            document.querySelectorAll('.comp-checkbox').forEach(cb => cb.checked = source.checked);
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
        pass


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f"🚀 Serveur Genome N0-N3 démarré : http://localhost:{PORT}")
    print(f"   Version: 5.0 - Layout Hiérarchique (Design de Référence)")
    server.serve_forever()
