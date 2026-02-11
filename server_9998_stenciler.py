#!/usr/bin/env python3
"""
Serveur HTTP pour Stenciler Sullivan - Port 9998
Version 7.1 - Single Page Scrollable + Sidebar Minimale
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

PORT = 9998
GENOME_FILE = "docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/genome_inferred_kimi_innocent_v2.json"
FONTS_DIR = "Frontend/fonts"

def load_genome():
    """Charge le genome depuis le fichier JSON"""
    filepath = GENOME_FILE
    if not os.path.exists(filepath):
        cwd = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(cwd, GENOME_FILE)
    
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return {"n0_phases": [], "metadata": {"confidence_global": 0.85}}


def get_corps_color(corps_id):
    """Couleur distinctive pour chaque corps"""
    colors = {
        "n0_brainstorm": "#fbbf24",  # Jaune
        "n0_backend": "#6366f1",      # Indigo
        "n0_frontend": "#ec4899",     # Rose
        "n0_deploy": "#10b981"        # Vert
    }
    return colors.get(corps_id, "#64748b")


def generate_preview_corps(corps):
    """Génère une prévisualisation simplifiée d'un corps à 20%"""
    corps_id = corps.get('id', 'unknown')
    corps_name = corps.get('name', 'Sans nom')
    organes = corps.get('n1_sections', [])[:3]
    color = get_corps_color(corps_id)
    
    organes_html = ""
    for org in organes:
        org_name = org.get('name', '')[:12]
        organes_html += f'<div class="preview-organe">{org_name}</div>'
    
    if len(corps.get('n1_sections', [])) > 3:
        organes_html += f'<div style="text-align:center;font-size:10px;color:#6b7280;margin-top:4px;">+{len(corps.get("n1_sections", [])) - 3}</div>'
    
    return f'''
    <div class="corps-preview" data-corps-id="{corps_id}" draggable="true" ondragstart="handleDragStart(event, '{corps_id}')">
        <div class="corps-preview-header" style="background: {color};">
            <div class="corps-dot" style="background: white;"></div>
            <span class="corps-name">{corps_name}</span>
        </div>
        <div class="corps-preview-body">
            {organes_html}
        </div>
        <div class="corps-preview-footer">
            <span>→ Glisser dans le tarmac</span>
        </div>
    </div>
    '''


def generate_html(genome):
    phases = genome.get('n0_phases', [])
    confidence = genome.get('metadata', {}).get('confidence_global', 0.85)
    
    previews_html = ""
    for phase in phases[:4]:
        previews_html += generate_preview_corps(phase)
    
    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HoméOS - Stenciler Sullivan (Port 9998)</title>
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.1/fabric.min.js"></script>
    
    <style>
        :root {{
            --font-main: 'Inter', system-ui, -apple-system, sans-serif;
            --color-bg: #f8fafc;
            --color-sidebar: #ffffff;
            --color-border: #e2e8f0;
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{ 
            font-family: var(--font-main); 
            background: var(--color-bg);
            overflow-x: hidden;
        }}
        
        /* Layout horizontal: Sidebar | Content */
        .app-container {{ 
            display: flex; 
            min-height: 100vh;
        }}
        
        /* SIDEBAR MINIMALE */
        .sidebar {{ 
            width: 60px;
            background: var(--color-sidebar);
            border-right: 1px solid var(--color-border);
            position: fixed;
            left: 0;
            top: 0;
            bottom: 0;
            z-index: 1000;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 16px 0;
            gap: 8px;
        }}
        
        .sidebar.expanded {{
            width: 220px;
            align-items: flex-start;
            padding: 16px;
        }}
        
        .sidebar-toggle {{
            width: 36px;
            height: 36px;
            border: none;
            background: #f1f5f9;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            margin-bottom: 16px;
        }}
        
        .sidebar-toggle:hover {{
            background: #e2e8f0;
        }}
        
        .tool-btn {{
            width: 44px;
            height: 44px;
            border: none;
            background: transparent;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            position: relative;
            transition: all 0.2s;
        }}
        
        .tool-btn:hover, .tool-btn.active {{
            background: #f1f5f9;
        }}
        
        .tool-btn.active::before {{
            content: '';
            position: absolute;
            left: -16px;
            top: 50%;
            transform: translateY(-50%);
            width: 3px;
            height: 24px;
            background: #3b82f6;
            border-radius: 0 2px 2px 0;
        }}
        
        /* Section outils (visible quand expanded) */
        .tool-section {{
            width: 100%;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid var(--color-border);
            display: none;
        }}
        
        .sidebar.expanded .tool-section {{
            display: block;
        }}
        
        .tool-label {{
            font-size: 11px;
            font-weight: 600;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
        }}
        
        .color-picker {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-bottom: 16px;
        }}
        
        .color-swatch {{
            width: 28px;
            height: 28px;
            border-radius: 6px;
            cursor: pointer;
            border: 2px solid transparent;
            transition: all 0.2s;
        }}
        
        .color-swatch:hover {{
            transform: scale(1.1);
        }}
        
        .color-swatch.active {{
            border-color: #1f2937;
            box-shadow: 0 0 0 2px white, 0 0 0 4px #1f2937;
        }}
        
        .slider-control {{
            margin-bottom: 16px;
        }}
        
        .slider-label {{
            font-size: 12px;
            color: #64748b;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
        }}
        
        .slider {{
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: #e2e8f0;
            outline: none;
            -webkit-appearance: none;
        }}
        
        .slider::-webkit-slider-thumb {{
            -webkit-appearance: none;
            appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #3b82f6;
            cursor: pointer;
            border: 2px solid white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        /* CONTENT AREA (scrollable) */
        .content {{
            flex: 1;
            margin-left: 60px;
            min-height: 100vh;
        }}
        
        /* HEADER - 4 Corps */
        .header-section {{
            background: linear-gradient(180deg, #ffffff 0%, #f1f5f9 100%);
            padding: 32px;
            border-bottom: 1px solid var(--color-border);
        }}
        
        .section-title {{
            font-size: 14px;
            font-weight: 700;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .section-title::after {{
            content: '';
            flex: 1;
            height: 1px;
            background: linear-gradient(90deg, #e2e8f0 0%, transparent 100%);
        }}
        
        .corps-container {{
            display: flex;
            gap: 24px;
            justify-content: center;
            flex-wrap: wrap;
        }}
        
        .corps-preview {{
            width: 200px;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            cursor: grab;
            transition: all 0.3s ease;
        }}
        
        .corps-preview:hover {{
            transform: translateY(-4px);
            box-shadow: 0 12px 24px rgba(0,0,0,0.1);
        }}
        
        .corps-preview.dragging {{
            opacity: 0.5;
            cursor: grabbing;
        }}
        
        .corps-preview-header {{
            padding: 12px 16px;
            display: flex;
            align-items: center;
            gap: 10px;
            color: white;
        }}
        
        .corps-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }}
        
        .corps-name {{
            font-weight: 700;
            font-size: 14px;
        }}
        
        .corps-preview-body {{
            padding: 12px;
            min-height: 100px;
        }}
        
        .preview-organe {{
            padding: 6px 10px;
            background: #f8fafc;
            border-radius: 6px;
            margin-bottom: 6px;
            font-size: 12px;
            color: #374151;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        
        .corps-preview-footer {{
            padding: 10px 12px;
            background: #f8fafc;
            font-size: 11px;
            color: #6b7280;
            text-align: center;
        }}
        
        /* TARMAC SECTION */
        .tarmac-section {{
            padding: 32px;
            min-height: 800px;
            position: relative;
        }}
        
        .tarmac-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
        }}
        
        .tarmac-canvas-container {{
            background: white;
            border-radius: 16px;
            border: 2px dashed #e2e8f0;
            min-height: 600px;
            position: relative;
            overflow: hidden;
        }}
        
        .tarmac-canvas-container.drag-over {{
            border-color: #7aca6a;
            background: rgba(124, 179, 66, 0.02);
        }}
        
        #tarmac-canvas {{
            width: 100%;
            height: 600px;
        }}
        
        .drop-hint {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            color: #94a3b8;
            pointer-events: none;
        }}
        
        .drop-hint-icon {{
            font-size: 48px;
            margin-bottom: 16px;
            opacity: 0.5;
        }}
        
        .drop-hint-text {{
            font-size: 16px;
            font-weight: 500;
        }}
        
        /* VALIDATE SECTION */
        .validate-section {{
            padding: 32px;
            text-align: center;
            border-top: 1px solid var(--color-border);
        }}
        
        .btn-validate {{
            padding: 16px 48px;
            background: linear-gradient(145deg, #7aca6a 0%, #6aba5a 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(124, 179, 66, 0.3);
            transition: all 0.2s;
        }}
        
        .btn-validate:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(124, 179, 66, 0.4);
        }}
        
        .btn-validate:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }}
        
        /* Grille magnétique */
        .canvas-container {{
            background-image: radial-gradient(circle, #e2e8f0 1px, transparent 1px);
            background-size: 20px 20px;
        }}
        
        /* Responsive desktop first - pas de mobile ici */
        @media (max-width: 1200px) {{
            .corps-container {{
                gap: 16px;
            }}
            .corps-preview {{
                width: 180px;
            }}
        }}
    </style>
</head>
<body>
    <div class="app-container">
        <!-- SIDEBAR MINIMALE -->
        <aside class="sidebar" id="sidebar">
            <button class="sidebar-toggle" onclick="toggleSidebar()" title="Outils">⚙️</button>
            
            <button class="tool-btn active" title="Sélection" onclick="setTool('select')">↖️</button>
            <button class="tool-btn" title="Couleur" onclick="setTool('color')">🎨</button>
            <button class="tool-btn" title="Bordure" onclick="setTool('border')">⬜</button>
            <button class="tool-btn" title="Supprimer" onclick="setTool('delete')">🗑️</button>
            
            <div class="tool-section">
                <div class="tool-label">Couleurs</div>
                <div class="color-picker">
                    <div class="color-swatch active" style="background: #3b82f6;" onclick="setColor('#3b82f6')"></div>
                    <div class="color-swatch" style="background: #7aca6a;" onclick="setColor('#7aca6a')"></div>
                    <div class="color-swatch" style="background: #fbbf24;" onclick="setColor('#fbbf24')"></div>
                    <div class="color-swatch" style="background: #ec4899;" onclick="setColor('#ec4899')"></div>
                    <div class="color-swatch" style="background: #6366f1;" onclick="setColor('#6366f1')"></div>
                    <div class="color-swatch" style="background: #1f2937;" onclick="setColor('#1f2937')"></div>
                </div>
                
                <div class="tool-label">Bordure</div>
                <div class="slider-control">
                    <div class="slider-label">
                        <span>Épaisseur</span>
                        <span id="border-value">2px</span>
                    </div>
                    <input type="range" class="slider" min="0" max="10" value="2" onchange="updateBorder(this.value)">
                </div>
                
                <div class="tool-label">Fond</div>
                <div class="slider-control">
                    <div class="slider-label">
                        <span>Opacité</span>
                        <span id="opacity-value">20%</span>
                    </div>
                    <input type="range" class="slider" min="0" max="100" value="20" onchange="updateOpacity(this.value)">
                </div>
            </div>
        </aside>

        <!-- CONTENT (Scrollable) -->
        <main class="content">
            <!-- SECTION 1: Corps Preview -->
            <section class="header-section">
                <div class="section-title">📦 1. Sélectionner un Corps du Génome</div>
                <div class="corps-container">
                    {previews_html}
                </div>
            </section>
            
            <!-- SECTION 2: Tarmac Canvas -->
            <section class="tarmac-section">
                <div class="tarmac-header">
                    <div class="section-title">🎨 2. Composer sur le Tarmac</div>
                    <div style="font-size: 13px; color: #64748b;">
                        Double-clic pour entrer dans un corps
                    </div>
                </div>
                
                <div class="tarmac-canvas-container" id="tarmac-container">
                    <canvas id="tarmac-canvas"></canvas>
                    <div class="drop-hint" id="drop-hint">
                        <div class="drop-hint-icon">📥</div>
                        <div class="drop-hint-text">Glissez un Corps ici pour commencer</div>
                    </div>
                </div>
            </section>
            
            <!-- SECTION 3: Validation -->
            <section class="validate-section">
                <div class="section-title" style="justify-content: center; margin-bottom: 24px;">✓ 3. Valider la sélection</div>
                <button class="btn-validate" id="btn-validate" disabled onclick="validateSelection()">
                    Valider et continuer →
                </button>
            </section>
        </main>
    </div>
    
    <script>
        let canvas;
        let currentTool = 'select';
        let currentColor = '#3b82f6';
        let currentBorderWidth = 2;
        let currentOpacity = 20;
        let droppedCorps = [];
        
        document.addEventListener('DOMContentLoaded', function() {{
            initCanvas();
            setupDragAndDrop();
        }});
        
        function initCanvas() {{
            const container = document.getElementById('tarmac-container');
            canvas = new fabric.Canvas('tarmac-canvas', {{
                width: container.clientWidth - 4,
                height: 600,
                backgroundColor: 'transparent',
                preserveObjectStacking: true,
                selection: true,
                uniScaleTransform: true
            }});
            
            // Grille magnétique
            drawGrid();
            
            canvas.on('object:moving', function(e) {{
                snapToGrid(e.target);
            }});
            
            canvas.on('mouse:dblclick', function(e) {{
                if (e.target && e.target.corpsData) {{
                    enterCorps(e.target.corpsData);
                }}
            }});
            
            canvas.on('selection:created', updateSelection);
            canvas.on('selection:updated', updateSelection);
            canvas.on('selection:cleared', clearSelection);
        }}
        
        function drawGrid() {{
            // Grille gérée par CSS background
        }}
        
        function snapToGrid(target) {{
            const gridSize = 20;
            target.set({{
                left: Math.round(target.left / gridSize) * gridSize,
                top: Math.round(target.top / gridSize) * gridSize
            }});
        }}
        
        function setupDragAndDrop() {{
            const container = document.getElementById('tarmac-container');
            const hint = document.getElementById('drop-hint');
            
            container.addEventListener('dragover', function(e) {{
                e.preventDefault();
                container.classList.add('drag-over');
            }});
            
            container.addEventListener('dragleave', function(e) {{
                container.classList.remove('drag-over');
            }});
            
            container.addEventListener('drop', function(e) {{
                e.preventDefault();
                container.classList.remove('drag-over');
                
                const corpsId = e.dataTransfer.getData('corps-id');
                if (corpsId) {{
                    const rect = container.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;
                    dropCorpsOnTarmac(corpsId, x, y);
                }}
            }});
        }}
        
        function handleDragStart(e, corpsId) {{
            e.dataTransfer.setData('corps-id', corpsId);
            e.target.classList.add('dragging');
            setTimeout(() => e.target.classList.remove('dragging'), 0);
        }}
        
        function dropCorpsOnTarmac(corpsId, x, y) {{
            const corpsData = {{
                id: corpsId,
                name: getCorpsName(corpsId),
                color: getCorpsColor(corpsId)
            }};
            
            droppedCorps.push(corpsData);
            document.getElementById('drop-hint').style.display = 'none';
            document.getElementById('btn-validate').disabled = false;
            
            // Créer l'objet sur le canvas (taille desktop 100%)
            const group = new fabric.Group([], {{
                left: x - 150,
                top: y - 100,
                selectable: true,
                hasControls: true,
                hasBorders: true,
                borderColor: corpsData.color,
                cornerColor: corpsData.color,
                cornerSize: 8
            }});
            
            // Corps rectangle (taille desktop)
            const mainRect = new fabric.Rect({{
                width: 300,
                height: 400,
                fill: corpsData.color + '20',
                stroke: corpsData.color,
                strokeWidth: 2,
                rx: 12
            }});
            
            const header = new fabric.Rect({{
                width: 300,
                height: 50,
                fill: corpsData.color,
                rx: 12
            }});
            
            const title = new fabric.Text(corpsData.name, {{
                left: 20,
                top: 15,
                fontSize: 18,
                fontWeight: 'bold',
                fill: '#ffffff',
                fontFamily: 'Inter, sans-serif'
            }});
            
            // Organes placeholders
            for (let i = 0; i < 3; i++) {{
                const orgY = 70 + i * 90;
                const orgRect = new fabric.Rect({{
                    left: 20,
                    top: orgY,
                    width: 260,
                    height: 80,
                    fill: 'rgba(255,255,255,0.9)',
                    stroke: '#e2e8f0',
                    rx: 6
                }});
                group.addWithUpdate(orgRect);
            }}
            
            const hint = new fabric.Text('Double-clic pour entrer', {{
                left: 80,
                top: 370,
                fontSize: 11,
                fill: '#64748b'
            }});
            
            group.addWithUpdate(mainRect);
            group.addWithUpdate(header);
            group.addWithUpdate(title);
            group.addWithUpdate(hint);
            
            group.corpsData = corpsData;
            canvas.add(group);
            canvas.setActiveObject(group);
            canvas.renderAll();
            
            // Smooth scroll vers le tarmac
            document.querySelector('.tarmac-section').scrollIntoView({{ behavior: 'smooth' }});
        }}
        
        function getCorpsName(id) {{
            const names = {{
                'n0_brainstorm': 'Brainstorm',
                'n0_backend': 'Backend',
                'n0_frontend': 'Frontend',
                'n0_deploy': 'Deploy'
            }};
            return names[id] || id.replace('n0_', '');
        }}
        
        function getCorpsColor(id) {{
            const colors = {{
                'n0_brainstorm': '#fbbf24',
                'n0_backend': '#6366f1',
                'n0_frontend': '#ec4899',
                'n0_deploy': '#10b981'
            }};
            return colors[id] || '#64748b';
        }}
        
        function enterCorps(corpsData) {{
            console.log('Entrée dans:', corpsData.name);
            alert('Entrée dans: ' + corpsData.name + '\\n\\nLes organes seront chargés avec lazy loading.');
        }}
        
        // Sidebar tools
        function toggleSidebar() {{
            document.getElementById('sidebar').classList.toggle('expanded');
        }}
        
        function setTool(tool) {{
            currentTool = tool;
            document.querySelectorAll('.tool-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            if (tool === 'delete' && canvas.getActiveObject()) {{
                canvas.remove(canvas.getActiveObject());
                canvas.renderAll();
            }}
        }}
        
        function setColor(color) {{
            currentColor = color;
            document.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('active'));
            event.target.classList.add('active');
            
            const active = canvas.getActiveObject();
            if (active) {{
                active.set('stroke', color);
                active.set('borderColor', color);
                canvas.renderAll();
            }}
        }}
        
        function updateBorder(value) {{
            currentBorderWidth = parseInt(value);
            document.getElementById('border-value').textContent = value + 'px';
            
            const active = canvas.getActiveObject();
            if (active) {{
                active.set('strokeWidth', currentBorderWidth);
                canvas.renderAll();
            }}
        }}
        
        function updateOpacity(value) {{
            currentOpacity = parseInt(value);
            document.getElementById('opacity-value').textContent = value + '%';
        }}
        
        function updateSelection() {{
            // Met à jour la sidebar selon la sélection
        }}
        
        function clearSelection() {{
            // Réinitialise la sidebar
        }}
        
        function validateSelection() {{
            if (droppedCorps.length === 0) return;
            alert('✅ Sélection validée !\\n\\nProchaine étape : Upload ou Style par défaut');
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
        elif self.path.startswith('/fonts/'):
            font_path = os.path.join(FONTS_DIR, os.path.basename(self.path))
            if os.path.exists(font_path):
                self.send_response(200)
                if self.path.endswith('.woff2'):
                    self.send_header('Content-type', 'font/woff2')
                elif self.path.endswith('.woff'):
                    self.send_header('Content-type', 'font/woff')
                self.end_headers()
                with open(font_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f"🚀 Stenciler Sullivan v7.1 démarré : http://localhost:{PORT}")
    print(f"   Single page scrollable | Sidebar minimale | Desktop first")
    server.serve_forever()
