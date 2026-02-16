#!/usr/bin/env python3
"""
Applique le patch Stenciler en échappant correctement les f-strings
"""

STENCILER_CSS = '''
        /* ========================================
           STENCILER SECTION (extension)
           ======================================== */
        
        #stenciler-section {{
            display: none;
            margin-top: 40px;
            padding-top: 40px;
            border-top: 2px dashed #e2e8f0;
        }}
        
        #stenciler-section.visible {{
            display: block;
        }}
        
        /* Bande de previews */
        .previews-band {{
            display: flex;
            gap: 16px;
            justify-content: center;
            padding: 20px;
            background: #f8fafc;
            border-radius: 12px;
            margin-bottom: 24px;
        }}
        
        .preview-corps {{
            width: 120px;
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            cursor: grab;
            transition: all 0.2s;
        }}
        
        .preview-corps:hover {{
            border-color: #7aca6a;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        
        .preview-corps.dragging {{
            opacity: 0.5;
            cursor: grabbing;
        }}
        
        .preview-header {{
            padding: 8px;
            color: white;
            font-size: 11px;
            font-weight: 700;
            text-align: center;
            border-radius: 6px 6px 0 0;
        }}
        
        .preview-body {{
            padding: 8px;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        
        .preview-organe {{
            padding: 4px 6px;
            background: #f1f5f9;
            border-radius: 4px;
            font-size: 9px;
            color: #64748b;
        }}
        
        /* Layout Sidebar + Canvas */
        .stenciler-layout {{
            display: flex;
            gap: 16px;
            height: 600px;
        }}
        
        .stenciler-sidebar {{
            width: 200px;
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 16px;
            flex-shrink: 0;
        }}
        
        .stenciler-canvas {{
            flex: 1;
            background: white;
            border: 2px dashed #cbd5e1;
            border-radius: 12px;
            position: relative;
            overflow: hidden;
        }}
        
        .stenciler-canvas.drag-over {{
            border-color: #7aca6a;
            background: #f0fdf4;
        }}
        
        #tarmac-canvas {{
            width: 100%;
            height: 100%;
        }}
        
        .sidebar-header {{
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 1px solid #e2e8f0;
        }}
        
        .sidebar-header h3 {{
            font-size: 14px;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 4px;
        }}
        
        #selection-info {{
            font-size: 11px;
            color: #64748b;
        }}
        
        .tool-section {{
            margin-bottom: 20px;
        }}
        
        .tool-label {{
            font-size: 11px;
            font-weight: 600;
            color: #64748b;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .color-swatches {{
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
        }}
        
        .color-swatch {{
            width: 24px;
            height: 24px;
            border-radius: 6px;
            cursor: pointer;
            border: 2px solid transparent;
            transition: all 0.2s;
        }}
        
        .color-swatch:hover,
        .color-swatch.active {{
            border-color: #1f2937;
            transform: scale(1.1);
        }}
        
        .slider-container {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .slider-container input[type="range"] {{
            flex: 1;
            height: 6px;
            border-radius: 3px;
            background: #e2e8f0;
            outline: none;
            -webkit-appearance: none;
        }}
        
        .slider-container input[type="range"]::-webkit-slider-thumb {{
            -webkit-appearance: none;
            appearance: none;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: #3b82f6;
            cursor: pointer;
            border: 2px solid white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .slider-value {{
            font-size: 11px;
            color: #64748b;
            min-width: 35px;
            text-align: right;
        }}
        
        .btn-delete {{
            width: 100%;
            padding: 10px;
            background: #fee2e2;
            color: #dc2626;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s;
        }}
        
        .btn-delete:hover {{
            background: #fecaca;
        }}
'''

STENCILER_HTML = '''
            <!-- STENCILER SECTION (cachée par défaut) -->
            <div id="stenciler-section">
                <div class="section-title">🎨 Stenciler - Composer le layout</div>
                
                <!-- Bande de previews 4 Corps -->
                <div class="previews-band">
                    <div class="preview-corps" data-corps-id="n0_brainstorm" draggable="true" ondragstart="handleDragStart(event, 'n0_brainstorm')" ondragend="handleDragEnd(event)">
                        <div class="preview-header" style="background:#fbbf24;">Brainstorm</div>
                        <div class="preview-body">
                            <div class="preview-organe">IR Report</div>
                            <div class="preview-organe">Arbitrage</div>
                        </div>
                    </div>
                    <div class="preview-corps" data-corps-id="n0_backend" draggable="true" ondragstart="handleDragStart(event, 'n0_backend')" ondragend="handleDragEnd(event)">
                        <div class="preview-header" style="background:#6366f1;">Backend</div>
                        <div class="preview-body">
                            <div class="preview-organe">Session</div>
                            <div class="preview-organe">API</div>
                        </div>
                    </div>
                    <div class="preview-corps" data-corps-id="n0_frontend" draggable="true" ondragstart="handleDragStart(event, 'n0_frontend')" ondragend="handleDragEnd(event)">
                        <div class="preview-header" style="background:#ec4899;">Frontend</div>
                        <div class="preview-body">
                            <div class="preview-organe">Navigation</div>
                            <div class="preview-organe">Layout</div>
                            <div class="preview-organe">Upload</div>
                        </div>
                    </div>
                    <div class="preview-corps" data-corps-id="n0_deploy" draggable="true" ondragstart="handleDragStart(event, 'n0_deploy')" ondragend="handleDragEnd(event)">
                        <div class="preview-header" style="background:#10b981;">Deploy</div>
                        <div class="preview-body">
                            <div class="preview-organe">Export</div>
                        </div>
                    </div>
                </div>
                
                <!-- Layout Sidebar + Canvas -->
                <div class="stenciler-layout">
                    <aside class="stenciler-sidebar">
                        <div class="sidebar-header">
                            <h3>Outils</h3>
                            <p id="selection-info">Aucune sélection</p>
                        </div>
                        
                        <div class="tool-section">
                            <div class="tool-label">Bordure</div>
                            <div class="color-swatches">
                                <div class="color-swatch" style="background:#ef4444;" onclick="setColor('#ef4444')"></div>
                                <div class="color-swatch" style="background:#f97316;" onclick="setColor('#f97316')"></div>
                                <div class="color-swatch" style="background:#eab308;" onclick="setColor('#eab308')"></div>
                                <div class="color-swatch" style="background:#22c55e;" onclick="setColor('#22c55e')"></div>
                                <div class="color-swatch" style="background:#3b82f6;" onclick="setColor('#3b82f6')"></div>
                                <div class="color-swatch" style="background:#8b5cf6;" onclick="setColor('#8b5cf6')"></div>
                                <div class="color-swatch" style="background:#ec4899;" onclick="setColor('#ec4899')"></div>
                                <div class="color-swatch" style="background:#64748b;" onclick="setColor('#64748b')"></div>
                            </div>
                        </div>
                        
                        <div class="tool-section">
                            <div class="tool-label">Épaisseur</div>
                            <div class="slider-container">
                                <input type="range" min="1" max="10" value="3" oninput="setBorderWidth(this.value)">
                                <span class="slider-value" id="border-value">3px</span>
                            </div>
                        </div>
                        
                        <div class="tool-section">
                            <div class="tool-label">Fond</div>
                            <div class="color-swatches">
                                <div class="color-swatch" style="background:#ffffff;border:1px solid #e2e8f0;" onclick="setBackground('#ffffff')"></div>
                                <div class="color-swatch" style="background:#f8fafc;" onclick="setBackground('#f8fafc')"></div>
                                <div class="color-swatch" style="background:#fef3c7;" onclick="setBackground('#fef3c7')"></div>
                                <div class="color-swatch" style="background:#dbeafe;" onclick="setBackground('#dbeafe')"></div>
                                <div class="color-swatch" style="background:#fce7f3;" onclick="setBackground('#fce7f3')"></div>
                                <div class="color-swatch" style="background:#d1fae5;" onclick="setBackground('#d1fae5')"></div>
                            </div>
                        </div>
                        
                        <div class="tool-section">
                            <button class="btn-delete" onclick="deleteSelected()">🗑️ Supprimer</button>
                        </div>
                    </aside>
                    
                    <main class="stenciler-canvas" id="canvas-container">
                        <canvas id="tarmac-canvas"></canvas>
                    </main>
                </div>
            </div>
'''

STENCILER_JS = '''
        // ========================================
        // STENCILER FABRIC.JS
        // ========================================
        
        let tarmacCanvas = null;
        let selectedStyle = 'minimal';
        let droppedCorps = [];
        
        // Fonction d'activation du Stenciler (appelée au clic sur style)
        function activateStenciler(style) {{
            selectedStyle = style || 'minimal';
            
            // Afficher la section
            const section = document.getElementById('stenciler-section');
            section.classList.add('visible');
            
            // Scroll vers la section
            setTimeout(() => {{
                section.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            }}, 100);
            
            // Initialiser le canvas (lazy)
            if (!tarmacCanvas) {{
                initTarmacCanvas();
            }}
        }}
        
        function initTarmacCanvas() {{
            const canvasEl = document.getElementById('tarmac-canvas');
            const container = document.getElementById('canvas-container');
            
            if (!canvasEl || !container) return;
            
            tarmacCanvas = new fabric.Canvas('tarmac-canvas', {{
                width: container.clientWidth,
                height: container.clientHeight,
                backgroundColor: '#fafafa',
                selection: true,
                preserveObjectStacking: true
            }});
            
            // Resize handler
            window.addEventListener('resize', () => {{
                if (tarmacCanvas) {{
                    tarmacCanvas.setWidth(container.clientWidth);
                    tarmacCanvas.setHeight(container.clientHeight);
                    tarmacCanvas.renderAll();
                }}
            }});
            
            // Drop zone
            container.addEventListener('dragover', (e) => {{
                e.preventDefault();
                container.classList.add('drag-over');
            }});
            
            container.addEventListener('dragleave', () => {{
                container.classList.remove('drag-over');
            }});
            
            container.addEventListener('drop', (e) => {{
                e.preventDefault();
                container.classList.remove('drag-over');
                
                const corpsId = e.dataTransfer.getData('corpsId');
                if (corpsId) {{
                    const rect = container.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;
                    addCorpsToCanvas(corpsId, x, y);
                }}
            }});
            
            // Selection events
            tarmacCanvas.on('selection:created', updateSidebarFromSelection);
            tarmacCanvas.on('selection:updated', updateSidebarFromSelection);
            tarmacCanvas.on('selection:cleared', clearSidebarSelection);
            
            // Double-click pour drill-down
            tarmacCanvas.on('mouse:dblclick', (e) => {{
                if (e.target && e.target.corpsData) {{
                    enterCorps(e.target.corpsData);
                }}
            }});
        }}
        
        function handleDragStart(e, corpsId) {{
            e.dataTransfer.setData('corpsId', corpsId);
            e.target.classList.add('dragging');
        }}
        
        function handleDragEnd(e) {{
            e.target.classList.remove('dragging');
        }}
        
        function getCorpsColor(corpsId) {{
            const colors = {{
                'n0_brainstorm': '#fbbf24',
                'n0_backend': '#6366f1',
                'n0_frontend': '#ec4899',
                'n0_deploy': '#10b981'
            }};
            return colors[corpsId] || '#64748b';
        }}
        
        function getCorpsName(corpsId) {{
            const names = {{
                'n0_brainstorm': 'Brainstorm',
                'n0_backend': 'Backend',
                'n0_frontend': 'Frontend',
                'n0_deploy': 'Deploy'
            }};
            return names[corpsId] || corpsId;
        }}
        
        function addCorpsToCanvas(corpsId, x, y) {{
            const color = getCorpsColor(corpsId);
            const name = getCorpsName(corpsId);
            
            // Créer le groupe Fabric.js (taille 33% = 200x150)
            const group = new fabric.Group([], {{
                left: x - 100,
                top: y - 75,
                hasControls: true,
                hasBorders: true,
                lockRotation: true
            }});
            
            // Rectangle principal
            const mainRect = new fabric.Rect({{
                width: 200,
                height: 150,
                fill: 'white',
                stroke: color,
                strokeWidth: 3,
                rx: 8,
                ry: 8
            }});
            
            // Header
            const header = new fabric.Rect({{
                width: 200,
                height: 30,
                fill: color,
                rx: 8,
                ry: 8
            }});
            
            // Titre
            const title = new fabric.Text(name, {{
                left: 10,
                top: 8,
                fontSize: 14,
                fontWeight: 'bold',
                fill: 'white',
                fontFamily: 'Inter, sans-serif'
            }});
            
            // Organes placeholders
            let orgY = 40;
            const organes = ['Organe 1', 'Organe 2', 'Organe 3'];
            organes.forEach((org) => {{
                const orgRect = new fabric.Rect({{
                    left: 10,
                    top: orgY,
                    width: 180,
                    height: 20,
                    fill: '#f1f5f9',
                    rx: 4,
                    ry: 4
                }});
                const orgText = new fabric.Text(org, {{
                    left: 15,
                    top: orgY + 4,
                    fontSize: 10,
                    fill: '#64748b',
                    fontFamily: 'Inter, sans-serif'
                }});
                group.addWithUpdate(orgRect);
                group.addWithUpdate(orgText);
                orgY += 25;
            }});
            
            group.addWithUpdate(mainRect);
            group.addWithUpdate(header);
            group.addWithUpdate(title);
            
            // Stocker les données
            group.corpsData = {{ id: corpsId, name: name, color: color }};
            group.corpsId = corpsId;
            
            tarmacCanvas.add(group);
            tarmacCanvas.setActiveObject(group);
            tarmacCanvas.renderAll();
            
            droppedCorps.push(corpsId);
            
            // Mettre à jour l'info sidebar
            document.getElementById('selection-info').textContent = name;
        }}
        
        function enterCorps(corpsData) {{
            console.log('Entrée dans:', corpsData.name);
            alert('Entrée dans: ' + corpsData.name + '\\n\\nDrill-down à implémenter (Tier 3).');
        }}
        
        function updateSidebarFromSelection(e) {{
            const obj = e.selected ? e.selected[0] : null;
            if (obj && obj.corpsData) {{
                document.getElementById('selection-info').textContent = obj.corpsData.name;
            }}
        }}
        
        function clearSidebarSelection() {{
            document.getElementById('selection-info').textContent = 'Aucune sélection';
        }}
        
        function setColor(color) {{
            const obj = tarmacCanvas ? tarmacCanvas.getActiveObject() : null;
            if (obj) {{
                obj.set('stroke', color);
                // Mettre à jour aussi le header
                if (obj._objects) {{
                    obj._objects.forEach(child => {{
                        if (child.fill && child.fill !== 'white' && child.fill !== '#f1f5f9') {{
                            // C'est probablement le header
                            if (child.width > 100 && child.height < 50) {{
                                child.set('fill', color);
                            }}
                        }}
                    }});
                }}
                tarmacCanvas.renderAll();
            }}
        }}
        
        function setBorderWidth(value) {{
            const obj = tarmacCanvas ? tarmacCanvas.getActiveObject() : null;
            if (obj) {{
                obj.set('strokeWidth', parseInt(value));
                tarmacCanvas.renderAll();
            }}
            document.getElementById('border-value').textContent = value + 'px';
        }}
        
        function setBackground(color) {{
            const obj = tarmacCanvas ? tarmacCanvas.getActiveObject() : null;
            if (obj && obj._objects) {{
                // Trouver le rect principal (le plus grand)
                const mainRect = obj._objects.find(o => 
                    o.type === 'rect' && o.width > 100 && o.height > 100
                );
                if (mainRect) {{
                    mainRect.set('fill', color);
                    tarmacCanvas.renderAll();
                }}
            }}
        }}
        
        function deleteSelected() {{
            const obj = tarmacCanvas ? tarmacCanvas.getActiveObject() : null;
            if (obj) {{
                const idx = droppedCorps.indexOf(obj.corpsId);
                if (idx > -1) droppedCorps.splice(idx, 1);
                tarmacCanvas.remove(obj);
                tarmacCanvas.renderAll();
                clearSidebarSelection();
            }}
        }}
        
        // Hook pour la sélection de style existante
        document.addEventListener('DOMContentLoaded', () => {{
            // Intercepter le clic sur les styles
            document.querySelectorAll('.style-card').forEach(card => {{
                card.addEventListener('click', (e) => {{
                    // Activer le Stenciler après sélection
                    const style = card.dataset.style;
                    setTimeout(() => {{
                        activateStenciler(style);
                    }}, 500);
                }});
            }});
        }});
'''

# Lire le fichier original
with open('server_9998_v2.py', 'r') as f:
    content = f.read()

# 1. Ajouter le CSS avant </style>
content = content.replace('    </style>', STENCILER_CSS + '    </style>')

# 2. Ajouter le HTML avant </body>
content = content.replace('    </body>', STENCILER_HTML + '    </body>')

# 3. Ajouter le JS avant </script>
content = content.replace('    </script>', STENCILER_JS + '    </script>')

# Sauvegarder
with open('server_9998_v2.py', 'w') as f:
    f.write(content)

print("✅ Patch appliqué avec succès!")
print(f"Nouvelle taille: {len(content)} caractères")
print(f"Lignes ajoutées: ~{len(content.split(chr(10))) - 1422}")
