#!/usr/bin/env python3
"""
Serveur ARBITER - Port 9999
Layout EXTRAIT_JS.md + genome_inferred_complete.json
"""

import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

PORT = 9999
BASE_DIR = Path("/Users/francois-jeandazin/AETHERFLOW")
GENOME_PATH = BASE_DIR / "genome_inferred_complete.json"

def load_genome():
    """Charge le genome inféré par Kimi innocent"""
    with open(GENOME_PATH) as f:
        return json.load(f)

def generate_component_wireframe(component):
    """Génère un wireframe visuel pour le composant (occurrence pas libellé)"""
    visual_hint = component.get("visual_hint", "generic")
    method = component.get("method", "GET")
    
    # Couleurs méthode HTTP
    method_colors = {
        "GET": "#7cb342",
        "POST": "#3b82f6", 
        "PUT": "#f59e0b",
        "PATCH": "#f59e0b",
        "DELETE": "#ef4444"
    }
    color = method_colors.get(method, "#888")
    
    # Wireframe selon visual_hint
    if visual_hint == "table":
        wireframe = f'''
        <div style="background:#1e1e1e;border:1px solid #3a3a3a;border-radius:4px;padding:12px;width:100%;">
            <div style="display:flex;gap:8px;margin-bottom:8px;">
                <div style="width:24px;height:24px;background:{color};border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:10px;color:white;font-weight:bold;">{method[:1]}</div>
                <div style="flex:1;">
                    <div style="width:70%;height:5px;background:#555;border-radius:2px;margin-bottom:3px;"></div>
                    <div style="width:50%;height:3px;background:#444;border-radius:1px;"></div>
                </div>
            </div>
            <div style="display:flex;gap:4px;">
                <div style="flex:1;height:8px;background:#2a2a2a;border-radius:1px;"></div>
                <div style="flex:1;height:8px;background:#2a2a2a;border-radius:1px;"></div>
                <div style="flex:1;height:8px;background:#2a2a2a;border-radius:1px;"></div>
            </div>
        </div>'''
    elif visual_hint == "card":
        wireframe = f'''
        <div style="background:#1e1e1e;border:1px solid #3a3a3a;border-radius:4px;padding:12px;width:100%;">
            <div style="display:flex;gap:8px;margin-bottom:8px;">
                <div style="width:24px;height:24px;background:{color};border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:10px;color:white;font-weight:bold;">{method[:1]}</div>
                <div style="flex:1;">
                    <div style="width:60%;height:6px;background:#555;border-radius:2px;margin-bottom:4px;"></div>
                    <div style="width:40%;height:3px;background:#444;border-radius:1px;"></div>
                </div>
            </div>
            <div style="height:20px;background:#2a2a2a;border-radius:2px;border:1px solid #3a3a3a;"></div>
        </div>'''
    elif visual_hint == "form":
        wireframe = f'''
        <div style="background:#1e1e1e;border:1px solid #3a3a3a;border-radius:4px;padding:10px;width:100%;">
            <div style="display:flex;gap:8px;margin-bottom:8px;align-items:center;">
                <div style="width:20px;height:20px;background:{color};border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:9px;color:white;font-weight:bold;">{method[:1]}</div>
                <span style="font-size:9px;color:#888;">form</span>
            </div>
            <div style="margin-bottom:6px;">
                <div style="width:40%;height:4px;background:{color};border-radius:1px;margin-bottom:3px;"></div>
                <div style="width:100%;height:12px;background:#2a2a2a;border:1px solid #3a3a3a;border-radius:2px;"></div>
            </div>
            <div>
                <div style="width:30%;height:4px;background:{color};border-radius:1px;margin-bottom:3px;"></div>
                <div style="width:100%;height:12px;background:#2a2a2a;border:1px solid #3a3a3a;border-radius:2px;"></div>
            </div>
        </div>'''
    elif visual_hint == "button":
        wireframe = f'''
        <div style="background:#1e1e1e;border:1px solid #3a3a3a;border-radius:4px;padding:12px;width:100%;display:flex;justify-content:center;">
            <div style="padding:6px 16px;background:{color};border-radius:4px;font-size:10px;color:white;font-weight:600;">{method}</div>
        </div>'''
    else:
        wireframe = f'''
        <div style="background:#1e1e1e;border:1px solid #3a3a3a;border-radius:4px;padding:12px;width:100%;">
            <div style="display:flex;gap:8px;align-items:center;">
                <div style="width:24px;height:24px;background:{color};border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:10px;color:white;font-weight:bold;">{method[:1]}</div>
                <div style="flex:1;height:4px;background:#555;border-radius:2px;"></div>
            </div>
        </div>'''
    
    return wireframe

def generate_genome_tree(genome_data):
    """Génère l'arbre du genome N0-N3 pour le panneau droit"""
    html = '<div class="genome-tree-level" data-level="0">'
    html += '<div class="genome-tree-item expanded"><span class="tree-toggle">▼</span><span class="tree-icon">🧬</span><span class="tree-label">Genome Root</span></div>'
    html += '<div class="genome-tree-children">'
    
    for phase in genome_data.get("n0_phases", []):
        phase_id = phase.get("id", "")
        phase_name = phase.get("name", "")
        confidence = phase.get("confidence", 0)
        
        html += f'<div class="genome-tree-item" data-level="1">'
        html += f'<span class="tree-toggle">▶</span><span class="tree-icon">📦</span><span class="tree-label">{phase_name}</span>'
        html += f'<span style="margin-left:auto;font-size:9px;color:#7cb342;">{int(confidence*100)}%</span>'
        html += '</div>'
        html += '<div class="genome-tree-children" style="display:none;">'
        
        for section in phase.get("n1_sections", []):
            section_name = section.get("name", "")
            html += f'<div class="genome-tree-item" data-level="2">'
            html += f'<span class="tree-toggle">▶</span><span class="tree-icon">📁</span><span class="tree-label">{section_name}</span>'
            html += '</div>'
            html += '<div class="genome-tree-children" style="display:none;">'
            
            for feature in section.get("n2_features", []):
                feature_name = feature.get("name", "")
                html += f'<div class="genome-tree-item" data-level="3">'
                html += f'<span class="tree-icon">⚙️</span><span class="tree-label">{feature_name}</span>'
                html += '</div>'
                
                # Composants N3
                for comp in feature.get("n3_components", []):
                    comp_name = comp.get("name", "")
                    method = comp.get("method", "GET")
                    visual = comp.get("visual_hint", "")
                    html += f'<div class="genome-tree-item" data-level="4" style="padding-left:64px;">'
                    html += f'<span style="font-size:9px;padding:2px 4px;background:#333;border-radius:2px;margin-right:4px;color:#aaa;">{method}</span>'
                    html += f'<span style="font-size:10px;color:#888;">{comp_name}</span>'
                    html += f'<span style="margin-left:auto;font-size:8px;color:#666;font-style:italic;">{visual}</span>'
                    html += '</div>'
            
            html += '</div>'  # /feature
        
        html += '</div>'  # /section
    
    html += '</div></div>'  # /children /root
    return html

def generate_components_panel(genome_data):
    """Génère le panneau gauche avec les composants (occurrences visuelles)"""
    components = []
    
    # Extraire tous les composants N3
    for phase in genome_data.get("n0_phases", []):
        for section in phase.get("n1_sections", []):
            for feature in section.get("n2_features", []):
                for comp in feature.get("n3_components", []):
                    components.append({
                        "phase": phase.get("name", ""),
                        **comp
                    })
    
    html = '<div class="components-grid">'
    
    for comp in components[:16]:  # Limiter à 16 pour la lisibilité
        wireframe = generate_component_wireframe(comp)
        phase = comp.get("phase", "")
        name = comp.get("name", "")
        endpoint = comp.get("endpoint", "")
        
        html += f'''
        <div class="arbiter-component-item">
            <label class="flex items-start gap-3 cursor-pointer" style="display:flex;align-items:flex-start;gap:12px;">
                <input type="checkbox" class="component-checkbox" checked style="margin-top:4px;accent-color:#7cb342;">
                <div style="flex:1;min-width:0;">
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                        <span style="font-size:16px;">📦</span>
                        <span style="font-size:11px;color:#7cb342;font-weight:600;text-transform:uppercase;">{phase[:15]}</span>
                    </div>
                    {wireframe}
                    <p style="font-size:10px;color:#888;margin:8px 0 0 0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{endpoint}</p>
                </div>
            </label>
        </div>
        '''
    
    if len(components) > 16:
        html += f'<div style="grid-column:1/-1;text-align:center;padding:10px;color:#888;font-size:12px;">... et {len(components)-16} autres composants</div>'
    
    html += '</div>'
    return html, len(components)

def generate_html():
    """Génère la page HTML complète"""
    genome = load_genome()
    genome_tree = generate_genome_tree(genome)
    components_panel, comp_count = generate_components_panel(genome)
    
    html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HoméOS ARBITER - Genome Inferred</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; overflow: hidden; }}
        
        /* Tabs */
        .tabs-container {{ display: flex; height: 50px; background: #fff; border-bottom: 1px solid #e0e0e0; }}
        .tab {{ flex: 1; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 14px; color: #666; border-right: 1px solid #e0e0e0; transition: all 0.2s; }}
        .tab:last-child {{ border-right: none; }}
        .tab:hover {{ background: #f9f9f9; }}
        .tab.active {{ background: #A6CE39; color: #333; font-weight: 500; }}
        
        /* Main layout */
        .main-container {{ display: flex; height: calc(100vh - 50px); }}
        
        /* Sidebar */
        .sidebar {{ width: 280px; background: #f8f8f8; border-right: 1px solid #e0e0e0; display: flex; flex-direction: column; overflow-y: auto; }}
        .logo {{ padding: 16px; border-bottom: 1px solid #e0e0e0; background: #fff; }}
        .logo-title {{ font-size: 20px; font-weight: 700; color: #8cc63f; letter-spacing: -0.5px; }}
        .logo-subtitle {{ font-size: 12px; color: #888; margin-top: 2px; }}
        .sidebar-section {{ padding: 12px; border-bottom: 1px solid #e0e0e0; }}
        .sidebar-section-title {{ font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }}
        
        /* ARBITER Container */
        .arbiter-container {{ display: flex; height: 100%; min-height: calc(100vh - 50px); }}
        
        /* Panneau Gauche (Clair) - Intent Revue */
        .panel-left {{ width: 55%; background: #f0f0e8; padding: 24px 32px; overflow-y: auto; border-right: 1px solid #d0d0c8; }}
        .panel-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid #d0d0c8; }}
        .panel-title {{ font-size: 14px; font-weight: 600; color: #5a5a52; letter-spacing: 0.5px; }}
        .arbiter-badge {{ background: #7cb342; color: white; padding: 6px 14px; border-radius: 4px; font-size: 12px; font-weight: 600; }}
        
        /* Panneau Droite (Sombre) - Genome */
        .panel-right {{ width: 45%; background: #252525; min-height: 100%; padding: 24px 32px; color: #fff; overflow-y: auto; }}
        .genome-header {{ text-align: center; margin-bottom: 32px; }}
        .genome-title {{ font-size: 14px; font-weight: 600; color: #fff; letter-spacing: 0.5px; }}
        .genome-section {{ margin-bottom: 28px; }}
        .genome-section-title {{ font-size: 12px; font-weight: 600; color: #fff; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 1px solid #3a3a3a; }}
        
        /* Genome Tree */
        .genome-tree-container {{ font-size: 12px; }}
        .genome-tree-item {{ display: flex; align-items: center; gap: 6px; padding: 6px 0; cursor: pointer; border-radius: 4px; transition: background 0.15s; }}
        .genome-tree-item:hover {{ background: #333; }}
        .genome-tree-item[data-level="1"] {{ padding-left: 16px; }}
        .genome-tree-item[data-level="2"] {{ padding-left: 32px; }}
        .genome-tree-item[data-level="3"] {{ padding-left: 48px; }}
        .genome-tree-item[data-level="4"] {{ padding-left: 64px; }}
        .tree-toggle {{ font-size: 10px; color: #888; width: 12px; }}
        .tree-icon {{ font-size: 12px; }}
        .tree-label {{ color: #ccc; }}
        .genome-tree-children {{ display: block; }}
        
        /* Components Grid */
        .components-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; }}
        .arbiter-component-item {{ background: #fff; border: 1px solid #d0d0c8; border-radius: 8px; padding: 14px; transition: all 0.2s; }}
        .arbiter-component-item:hover {{ border-color: #7cb342; box-shadow: 0 2px 8px rgba(124,179,66,0.15); }}
        .component-checkbox {{ accent-color: #7cb342; }}
        
        /* Arbiter Component Grid in dark panel */
        .arbiter-component-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-top: 12px; }}
        .arbiter-component-item-dark {{ background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 4px; padding: 10px; font-size: 10px; color: #aaa; cursor: pointer; transition: all 0.2s; }}
        .arbiter-component-item-dark:hover {{ border-color: #7cb342; background: #2a2a2a; }}
        
        /* Expandable sections */
        .expandable-section {{ margin-top: 24px; border-top: 1px solid #d0d0c8; padding-top: 16px; }}
        .expandable-header {{ display: flex; align-items: center; gap: 8px; cursor: pointer; }}
        .expand-icon {{ color: #7cb342; font-size: 12px; }}
        .expandable-title {{ font-size: 11px; font-weight: 600; color: #7cb342; }}
        
        /* Dark dropdowns */
        .dark-dropdowns {{ background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 4px; padding: 8px; }}
        .dark-dropdown-item {{ font-size: 10px; color: #888; padding: 4px 0; border-bottom: 1px solid #2a2a2a; }}
        .dark-dropdown-item:last-child {{ border-bottom: none; }}
        
        /* Stats */
        .inference-stats {{ display: flex; gap: 24px; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid #d0d0c8; }}
        .stat-item {{ text-align: center; }}
        .stat-value {{ display: block; font-size: 24px; font-weight: 700; color: #7cb342; }}
        .stat-label {{ font-size: 11px; color: #888; text-transform: uppercase; }}
    </style>
</head>
<body>
    <!-- Tabs -->
    <div class="tabs-container">
        <div class="tab" data-tab="brainstorm">Brainstorm</div>
        <div class="tab" data-tab="backend">Backend</div>
        <div class="tab active" data-tab="frontend">Frontend</div>
        <div class="tab" data-tab="deploy">Deploy</div>
    </div>

    <!-- Main -->
    <div class="main-container">
        <!-- Sidebar -->
        <aside class="sidebar">
            <div class="logo">
                <div class="logo-title">HoméOS</div>
                <div class="logo-subtitle">ARBITER - Genome Inferred</div>
            </div>
            
            <div class="sidebar-section">
                <h3 class="sidebar-section-title">🧬 Genome Drilldown</h3>
                <div class="genome-tree-container">
                    {genome_tree}
                </div>
            </div>
            
            <div class="sidebar-section">
                <h3 class="sidebar-section-title">📊 Stats</h3>
                <div style="display:flex;gap:12px;">
                    <div style="text-align:center;flex:1;">
                        <div style="font-size:20px;font-weight:700;color:#7cb342;">{len(genome.get('n0_phases', []))}</div>
                        <div style="font-size:10px;color:#888;">Phases</div>
                    </div>
                    <div style="text-align:center;flex:1;">
                        <div style="font-size:20px;font-weight:700;color:#7cb342;">{comp_count}</div>
                        <div style="font-size:10px;color:#888;">Composants</div>
                    </div>
                </div>
            </div>
            
            <div class="sidebar-section">
                <h3 class="sidebar-section-title">🎯 Confidence</h3>
                <div style="font-size:24px;font-weight:700;color:#7cb342;text-align:center;">
                    {int(genome.get('metadata', {}).get('confidence_global', 0) * 100)}%
                </div>
            </div>
        </aside>

        <!-- Content Area -->
        <main class="content-area" style="flex:1;display:flex;flex-direction:column;background:#fff;overflow:hidden;">
            <!-- ARBITER Layout -->
            <div class="arbiter-container">
                <!-- Panneau Gauche (Clair) - Intent Revue -->
                <div class="panel-left">
                    <div class="panel-header">
                        <span class="panel-title">Intent Revue - Composants Inférés</span>
                        <span class="arbiter-badge">ARBITER</span>
                    </div>
                    
                    <div class="inference-stats">
                        <div class="stat-item">
                            <span class="stat-value">{comp_count}</span>
                            <span class="stat-label">Composants</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">{len(genome.get('n0_phases', []))}</span>
                            <span class="stat-label">Phases</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">{int(genome.get('metadata', {}).get('confidence_global', 0) * 100)}%</span>
                            <span class="stat-label">Confiance</span>
                        </div>
                    </div>
                    
                    <div class="expandable-section">
                        <div class="expandable-header">
                            <span class="expand-icon">↕</span>
                            <span class="expandable-title">§1.5 Composants suggérés (Occurrences)</span>
                        </div>
                        <div style="margin-top:12px;">
                            {components_panel}
                        </div>
                    </div>
                </div>

                <!-- Panneau Droite (Sombre) - Genome -->
                <div class="panel-right">
                    <div class="genome-header" style="display:flex;justify-content:space-between;align-items:center;">
                        <span class="genome-title">Génome Inferred (Kimi Innocent)</span>
                        <span style="font-size:10px;color:#7cb342;padding:4px 8px;background:#2a3a1e;border-radius:4px;">v3.0-confronted</span>
                    </div>

                    <!-- Corps (Phases) -->
                    <div class="genome-section">
                        <div class="genome-section-title">Phases N0 (Corps)</div>
                        <div class="dark-dropdowns">
                            {''.join([f'<div class="dark-dropdown-item" style="display:flex;justify-content:space-between;"><span>{p.get("name", "")}</span><span style="color:#7cb342;">{int(p.get("confidence", 0)*100)}%</span></div>' for p in genome.get('n0_phases', [])])}
                        </div>
                    </div>

                    <!-- Organes (Sections) -->
                    <div class="genome-section">
                        <div class="genome-section-title">Sections N1 (Organes)</div>
                        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:8px;">
                            {''.join([f'<div style="padding:8px;background:#1e1e1e;border:1px solid #3a3a3a;border-radius:4px;text-align:center;font-size:9px;color:#aaa;"><div style="font-size:16px;margin-bottom:4px;">📁</div>{s.get("name", "")[:12]}</div>' for p in genome.get('n0_phases', []) for s in p.get('n1_sections', [])][:9])}
                        </div>
                    </div>

                    <!-- Cellules (Features) -->
                    <div class="genome-section">
                        <div class="genome-section-title">Features N2 (Cellules)</div>
                        <div class="dark-dropdowns">
                            {''.join([f'<div class="dark-dropdown-item">⚙️ {f.get("name", "")}</div>' for p in genome.get('n0_phases', []) for s in p.get('n1_sections', []) for f in s.get('n2_features', [])][:6])}
                        </div>
                        <div style="margin-top:8px;font-size:9px;color:#666;text-align:center;">... et plus</div>
                    </div>
                    
                    <!-- Metadata -->
                    <div class="genome-section" style="border-top:2px solid #7cb342;padding-top:16px;margin-top:24px;">
                        <div class="genome-section-title">Métadonnées</div>
                        <div style="font-size:10px;color:#888;line-height:1.6;">
                            <div><strong style="color:#7cb342;">Méthode:</strong> {genome.get('inference_method', '')}</div>
                            <div><strong style="color:#7cb342;">Sources:</strong> {', '.join(genome.get('metadata', {}).get('sources_used', []))}</div>
                            <div><strong style="color:#7cb342;">Conflits:</strong> {len(genome.get('metadata', {}).get('unresolved_conflicts', []))} non résolus</div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <script>
        // Tab switching
        document.querySelectorAll('.tab').forEach(tab => {{
            tab.addEventListener('click', function() {{
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                this.classList.add('active');
            }});
        }});
        
        // Tree expand/collapse
        document.querySelectorAll('.genome-tree-item').forEach(item => {{
            item.addEventListener('click', function(e) {{
                e.stopPropagation();
                const toggle = this.querySelector('.tree-toggle');
                const children = this.nextElementSibling;
                if (children && children.classList.contains('genome-tree-children')) {{
                    const isExpanded = toggle.textContent === '▼';
                    toggle.textContent = isExpanded ? '▶' : '▼';
                    children.style.display = isExpanded ? 'none' : 'block';
                }}
            }});
        }});
        
        // Checkbox toggle card
        document.querySelectorAll('.component-checkbox').forEach(chk => {{
            chk.addEventListener('change', function() {{
                const card = this.closest('.arbiter-component-item');
                if (card) {{
                    card.style.opacity = this.checked ? '1' : '0.5';
                }}
            }});
        }});
    </script>
</body>
</html>'''
    
    return html

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ['/studio', '/studio?step=4', '/', '/studio/']:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(generate_html().encode('utf-8'))
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "ok",
                "port": PORT,
                "genome_version": "3.0-confronted"
            }).encode())
        else:
            super().do_GET()
    
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    print(f"🚀 ARBITER Server démarré sur http://localhost:{PORT}")
    print(f"   URL: http://localhost:{PORT}/studio?step=4")
    print(f"   Genome: {GENOME_PATH.name}")
    print(f"   Layout: ARBITER (55% clair / 45% sombre)")
    with HTTPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()
