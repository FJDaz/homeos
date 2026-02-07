#!/usr/bin/env python3
"""
Serveur HTTP pour visualisation du Genome - Port 9999
Version 2.0 avec wireframes explicites et 10 composants FRD V2
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

# Configuration
PORT = 9999
GENOME_FILE = "genome_enrichi.json"

def load_genome():
    """Charge le genome depuis le fichier JSON"""
    if os.path.exists(GENOME_FILE):
        with open(GENOME_FILE, 'r') as f:
            return json.load(f)
    return {"n0_phases": [], "metadata": {"confidence_global": 0.0}}

def generate_component_wireframe(component, phase_name, description=""):
    """Génère le HTML du wireframe pour un composant"""
    visual_hint = component.get("visual_hint", "generic")
    method = component.get("method", "GET")
    endpoint = component.get("endpoint", "N/A")
    name = component.get("name", "Sans nom")
    comp_id = component.get("id", "unknown")
    
    # Couleurs méthode HTTP
    method_colors = {
        "GET": "#22c55e",
        "POST": "#3b82f6", 
        "PUT": "#f59e0b",
        "DELETE": "#ef4444"
    }
    color = method_colors.get(method, "#6b7280")
    
    # Nom clair sans préfixe technique
    nom_clair = name.replace("Comp ", "").replace("Component ", "")
    
    # === WIRE FRAMES ===
    
    # ANCHOR:WIRE_STATUS
    if visual_hint == "status" or visual_hint == "indicator" or visual_hint == "health":
        wireframe = '''<div style="background:white;border:2px solid #e5e7eb;border-radius:8px;padding:12px;">
            <div style="font-size:10px;font-weight:600;color:#374151;margin-bottom:8px;">🏥 Santé du projet</div>
            <div style="display:flex;justify-content:center;gap:12px;margin-bottom:10px;">
                <div style="text-align:center;"><div style="width:14px;height:14px;background:#22c55e;border-radius:50%;margin:0 auto 4px;"></div><span style="font-size:8px;color:#6b7280;">OK</span></div>
                <div style="text-align:center;"><div style="width:14px;height:14px;background:#22c55e;border-radius:50%;margin:0 auto 4px;"></div><span style="font-size:8px;color:#6b7280;">OK</span></div>
                <div style="text-align:center;"><div style="width:14px;height:14px;background:#22c55e;border-radius:50%;margin:0 auto 4px;"></div><span style="font-size:8px;color:#6b7280;">OK</span></div>
                <div style="text-align:center;"><div style="width:14px;height:14px;background:#9ca3af;border-radius:50%;margin:0 auto 4px;"></div><span style="font-size:8px;color:#6b7280;">?</span></div>
            </div>
            <div style="font-size:9px;color:#22c55e;text-align:center;">✅ Fonctions vitales présentes</div>
        </div>'''
    # /ANCHOR:WIRE_STATUS
    
    # ANCHOR:WIRE_ZOOM
    elif visual_hint == "zoom-controls" or visual_hint == "zoom":
        wireframe = '''<div style="background:white;border:2px solid #e5e7eb;border-radius:8px;padding:12px;">
            <div style="font-size:10px;font-weight:600;color:#374151;margin-bottom:8px;">🔭 Navigation</div>
            <div style="display:flex;gap:6px;margin-bottom:10px;">
                <span style="flex:1;padding:8px;background:#f3f4f6;border-radius:4px;text-align:center;font-size:10px;">← Out</span>
                <span style="flex:1;padding:8px;background:#3b82f6;color:white;border-radius:4px;text-align:center;font-size:10px;font-weight:600;">🔍 Corps ▼</span>
                <span style="flex:1;padding:8px;background:#f3f4f6;border-radius:4px;text-align:center;font-size:10px;">In →</span>
            </div>
            <div style="display:flex;align-items:center;justify-content:center;gap:8px;font-size:9px;color:#6b7280;">
                <span style="color:#22c55e;font-weight:bold;">◉ Corps</span><span>></span><span>○ Organe</span><span>></span><span>○ Atome</span>
            </div>
        </div>'''
    # /ANCHOR:WIRE_ZOOM
    
    # ANCHOR:WIRE_DOWNLOAD
    elif visual_hint == "download" or visual_hint == "export":
        wireframe = '''<div style="background:white;border:2px solid #e5e7eb;border-radius:8px;padding:12px;">
            <div style="font-size:10px;font-weight:600;color:#374151;margin-bottom:8px;">📦 Votre projet est prêt !</div>
            <div style="border:1px solid #e5e7eb;border-radius:6px;padding:10px;display:flex;align-items:center;gap:10px;margin-bottom:10px;">
                <span style="font-size:24px;">📄</span>
                <div style="flex:1;">
                    <div style="font-size:11px;font-weight:600;color:#374151;">homeos-project.zip</div>
                    <div style="font-size:9px;color:#9ca3af;">2.4 MB • 12 fichiers</div>
                </div>
            </div>
            <div style="padding:8px;background:#22c55e;border-radius:6px;text-align:center;font-size:11px;color:white;font-weight:600;">📥 Télécharger le ZIP</div>
        </div>'''
    # /ANCHOR:WIRE_DOWNLOAD
    
    # ANCHOR:WIRE_CHAT_INPUT
    elif visual_hint == "chat-input" or visual_hint == "input":
        wireframe = '''<div style="background:white;border:2px solid #e5e7eb;border-radius:8px;padding:12px;">
            <div style="font-size:10px;font-weight:600;color:#374151;margin-bottom:8px;">💬 Votre message</div>
            <div style="border:1px solid #d1d5db;border-radius:6px;padding:10px;height:50px;background:#f9fafb;margin-bottom:8px;">
                <div style="height:6px;background:#d1d5db;border-radius:1px;width:70%;"></div>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="display:flex;gap:8px;"><span style="font-size:14px;">📎</span><span style="font-size:14px;">😊</span></div>
                <span style="padding:6px 12px;background:#3b82f6;border-radius:6px;font-size:10px;color:white;font-weight:600;">➤ Envoyer</span>
            </div>
        </div>'''
    # /ANCHOR:WIRE_CHAT_INPUT
    
    # ANCHOR:WIRE_COLOR_PALETTE
    elif visual_hint == "color-palette" or visual_hint == "palette":
        wireframe = '''<div style="background:white;border:2px solid #e5e7eb;border-radius:8px;padding:12px;">
            <div style="font-size:10px;font-weight:600;color:#374151;margin-bottom:8px;">🎨 Style détecté</div>
            <div style="display:flex;gap:6px;margin-bottom:10px;">
                <div style="flex:1;height:32px;background:#3b82f6;border-radius:4px;"></div>
                <div style="flex:1;height:32px;background:#22c55e;border-radius:4px;"></div>
                <div style="flex:1;height:32px;background:#f59e0b;border-radius:4px;"></div>
                <div style="flex:1;height:32px;background:#1f2937;border-radius:4px;"></div>
            </div>
            <div style="display:flex;gap:6px;flex-wrap:wrap;">
                <span style="padding:4px 8px;background:#f3f4f6;border-radius:12px;font-size:9px;color:#6b7280;">Rounded: 8px</span>
                <span style="padding:4px 8px;background:#f3f4f6;border-radius:12px;font-size:9px;color:#6b7280;font-family:system-ui;">Inter</span>
            </div>
        </div>'''
    # /ANCHOR:WIRE_COLOR_PALETTE
    
    # ANCHOR:WIRE_CHOICE
    elif visual_hint == "choice-card" or visual_hint == "choice":
        wireframe = '''<div style="background:white;border:2px solid #e5e7eb;border-radius:8px;padding:12px;">
            <div style="font-size:10px;font-weight:600;color:#374151;margin-bottom:8px;">🎨 Choisissez votre style</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px;">
                <div style="border:1px solid #e5e7eb;border-radius:6px;padding:8px;text-align:center;"><span style="font-size:10px;color:#6b7280;">○ Minimal</span></div>
                <div style="border:1px solid #e5e7eb;border-radius:6px;padding:8px;text-align:center;"><span style="font-size:10px;color:#6b7280;">○ Brutaliste</span></div>
                <div style="border:1px solid #e5e7eb;border-radius:6px;padding:8px;text-align:center;"><span style="font-size:10px;color:#6b7280;">○ Moderne</span></div>
                <div style="border:1px solid #e5e7eb;border-radius:6px;padding:8px;text-align:center;"><span style="font-size:10px;color:#6b7280;">○ Corporate</span></div>
            </div>
            <div style="text-align:right;"><span style="padding:6px 12px;background:#3b82f6;border-radius:6px;font-size:10px;color:white;font-weight:600;">Continuer →</span></div>
        </div>'''
    # /ANCHOR:WIRE_CHOICE
    
    # ANCHOR:WIRE_STENCIL
    elif visual_hint == "stencil-card" or visual_hint == "stencil":
        wireframe = '''<div style="background:white;border:2px solid #e5e7eb;border-radius:8px;padding:12px;">
            <div style="font-size:12px;font-weight:600;color:#374151;margin-bottom:6px;">💡 Veille du Système</div>
            <div style="font-size:10px;color:#6b7280;margin-bottom:10px;line-height:1.4;">Voir l'état de santé du projet en un coup d'œil</div>
            <div style="display:flex;gap:8px;">
                <span style="flex:1;padding:6px;background:#22c55e;border-radius:4px;text-align:center;font-size:10px;color:white;">🟢 Garder</span>
                <span style="flex:1;padding:6px;background:#f3f4f6;border-radius:4px;text-align:center;font-size:10px;color:#6b7280;">⚪ Réserve</span>
            </div>
        </div>'''
    # /ANCHOR:WIRE_STENCIL
    
    # ANCHOR:WIRE_DETAIL
    elif visual_hint == "detail-card" or visual_hint == "detail":
        wireframe = '''<div style="background:white;border:2px solid #e5e7eb;border-radius:8px;padding:12px;">
            <div style="font-size:11px;font-weight:600;color:#374151;font-family:monospace;margin-bottom:6px;">🔧 /api/health</div>
            <div style="font-size:9px;color:#6b7280;margin-bottom:4px;">Type: GET</div>
            <div style="font-size:9px;color:#6b7280;margin-bottom:8px;">Retour: JSON {status, uptime}</div>
            <div style="display:flex;gap:8px;">
                <span style="flex:1;padding:6px;background:#f3f4f6;border-radius:4px;text-align:center;font-size:10px;color:#6b7280;">📋 Copier</span>
                <span style="flex:1;padding:6px;background:#3b82f6;border-radius:4px;text-align:center;font-size:10px;color:white;">↗️ Tester</span>
            </div>
        </div>'''
    # /ANCHOR:WIRE_DETAIL
    
    # ANCHOR:WIRE_LAUNCH
    elif visual_hint == "launch-button" or visual_hint == "launch":
        wireframe = '''<div style="background:white;border:2px solid #e5e7eb;border-radius:8px;padding:16px;text-align:center;">
            <div style="font-size:11px;font-weight:600;color:#374151;margin-bottom:10px;">🚀 Génération du code</div>
            <div style="padding:10px;background:#22c55e;border-radius:8px;font-size:12px;color:white;font-weight:600;">🚀 Lancer la distillation</div>
        </div>'''
    # /ANCHOR:WIRE_LAUNCH
    
    # ANCHOR:WIRE_APPLY
    elif visual_hint == "apply-changes" or visual_hint == "apply":
        wireframe = '''<div style="background:white;border:2px solid #e5e7eb;border-radius:8px;padding:12px;">
            <div style="font-size:10px;font-weight:600;color:#374151;margin-bottom:10px;">💾 Sauvegarder les changements</div>
            <div style="display:flex;gap:8px;">
                <span style="flex:1;padding:8px;background:#22c55e;border-radius:6px;text-align:center;font-size:11px;color:white;font-weight:600;">💾 Appliquer</span>
                <span style="flex:1;padding:8px;background:#f3f4f6;border-radius:6px;text-align:center;font-size:11px;color:#6b7280;">↩️ Annuler</span>
            </div>
        </div>'''
    # /ANCHOR:WIRE_APPLY
    
    # ANCHOR:WIRE_TABLE
    elif visual_hint == "table":
        wireframe = f'''<div style="background:white;border:2px solid #e5e7eb;border-radius:8px;padding:12px;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
                <div style="width:24px;height:24px;background:{color};border-radius:6px;display:flex;align-items:center;justify-content:center;">
                    <span style="color:white;font-size:12px;font-weight:bold;">{method[:1]}</span>
                </div>
                <div style="flex:1;">
                    <div style="font-size:10px;font-weight:600;color:#374151;">{nom_clair}</div>
                    <div style="font-size:9px;color:#9ca3af;">{endpoint}</div>
                </div>
            </div>
            <div style="border-top:1px solid #e5e7eb;padding-top:8px;">
                <div style="display:flex;gap:4px;margin-bottom:4px;">
                    <div style="flex:1;height:6px;background:#2a2a2a;border-radius:1px;"></div>
                    <div style="flex:1;height:6px;background:#2a2a2a;border-radius:1px;"></div>
                    <div style="width:40px;height:6px;background:{color};border-radius:1px;"></div>
                </div>
                <div style="display:flex;gap:4px;">
                    <div style="flex:1;height:6px;background:#e5e7eb;border-radius:1px;"></div>
                    <div style="flex:1;height:6px;background:#e5e7eb;border-radius:1px;"></div>
                    <div style="width:40px;height:6px;background:#e5e7eb;border-radius:1px;"></div>
                </div>
            </div>
        </div>'''
    # /ANCHOR:WIRE_TABLE
    
    # ANCHOR:WIRE_CARD
    elif visual_hint == "card":
        wireframe = f'''<div style="background:white;border:2px solid #e5e7eb;border-radius:8px;padding:12px;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                <div style="width:32px;height:32px;background:{color};border-radius:8px;display:flex;align-items:center;justify-content:center;">
                    <span style="color:white;font-size:14px;">◆</span>
                </div>
                <div style="flex:1;">
                    <div style="font-size:11px;font-weight:600;color:#374151;">{nom_clair}</div>
                    <div style="font-size:9px;color:#9ca3af;">{method} {endpoint}</div>
                </div>
            </div>
            <div style="height:4px;background:#e5e7eb;border-radius:2px;margin-top:8px;"></div>
        </div>'''
    # /ANCHOR:WIRE_CARD
    
    # ANCHOR:WIRE_FORM
    elif visual_hint == "form":
        wireframe = '''<div style="background:white;border:2px solid #e5e7eb;border-radius:8px;padding:12px;">
            <div style="margin-bottom:8px;">
                <div style="font-size:9px;color:#6b7280;margin-bottom:3px;">Label</div>
                <div style="height:28px;border:1px solid #d1d5db;border-radius:4px;background:#f9fafb;"></div>
            </div>
            <div style="margin-bottom:8px;">
                <div style="font-size:9px;color:#6b7280;margin-bottom:3px;">Label</div>
                <div style="height:28px;border:1px solid #d1d5db;border-radius:4px;background:#f9fafb;"></div>
            </div>
            <div style="display:flex;gap:8px;margin-top:12px;">
                <div style="flex:1;height:32px;background:#22c55e;border-radius:6px;"></div>
                <div style="flex:1;height:32px;background:#f3f4f6;border-radius:6px;"></div>
            </div>
        </div>'''
    # /ANCHOR:WIRE_FORM
    
    # ANCHOR:WIRE_DASHBOARD
    elif visual_hint == "dashboard":
        wireframe = '''<div style="background:white;border:2px solid #e5e7eb;border-radius:8px;padding:12px;">
            <div style="display:flex;gap:8px;margin-bottom:10px;">
                <div style="flex:1;text-align:center;padding:8px;background:#f3f4f6;border-radius:6px;">
                    <div style="font-size:16px;font-weight:700;color:#22c55e;">12</div>
                    <div style="font-size:8px;color:#6b7280;">Items</div>
                </div>
                <div style="flex:1;text-align:center;padding:8px;background:#f3f4f6;border-radius:6px;">
                    <div style="font-size:16px;font-weight:700;color:#3b82f6;">8</div>
                    <div style="font-size:8px;color:#6b7280;">Actifs</div>
                </div>
            </div>
            <div style="height:40px;background:#f3f4f6;border-radius:4px;display:flex;align-items:flex-end;padding:4px;gap:2px;">
                <div style="flex:1;height:60%;background:#22c55e;border-radius:1px;"></div>
                <div style="flex:1;height:80%;background:#22c55e;border-radius:1px;"></div>
                <div style="flex:1;height:40%;background:#3b82f6;border-radius:1px;"></div>
                <div style="flex:1;height:90%;background:#22c55e;border-radius:1px;"></div>
            </div>
        </div>'''
    # /ANCHOR:WIRE_DASHBOARD
    
    # ANCHOR:WIRE_EDITOR
    elif visual_hint == "editor":
        wireframe = '''<div style="background:#1e293b;border-radius:8px;padding:12px;font-family:monospace;">
            <div style="display:flex;gap:6px;margin-bottom:10px;">
                <div style="width:10px;height:10px;background:#ef4444;border-radius:50%;"></div>
                <div style="width:10px;height:10px;background:#f59e0b;border-radius:50%;"></div>
                <div style="width:10px;height:10px;background:#22c55e;border-radius:50%;"></div>
            </div>
            <div style="display:flex;flex-direction:gap:4px;">
                <div style="height:4px;background:#3b82f6;border-radius:1px;width:20%;margin-bottom:4px;"></div>
                <div style="height:4px;background:#22c55e;border-radius:1px;width:40%;margin-bottom:4px;"></div>
                <div style="height:4px;background:#f59e0b;border-radius:1px;width:30%;margin-bottom:4px;"></div>
                <div style="height:4px;background:#64748b;border-radius:1px;width:50%;"></div>
            </div>
        </div>'''
    # /ANCHOR:WIRE_EDITOR
    
    # ANCHOR:WIRE_CHAT
    elif visual_hint == "chat/bubble":
        wireframe = '''<div style="background:white;border:2px solid #e5e7eb;border-radius:8px;padding:12px;">
            <div style="display:flex;gap:8px;margin-bottom:10px;">
                <div style="width:28px;height:28px;background:#4f46e5;border-radius:50%;display:flex;align-items:center;justify-content:center;">
                    <span style="color:white;font-size:12px;font-weight:bold;">S</span>
                </div>
                <div style="flex:1;background:#f3f4f6;border-radius:12px;border-bottom-left-radius:4px;padding:10px;">
                    <div style="height:4px;background:#d1d5db;border-radius:1px;margin-bottom:3px;"></div>
                    <div style="height:4px;background:#d1d5db;border-radius:1px;width:70%;"></div>
                </div>
            </div>
            <div style="display:flex;gap:8px;justify-content:flex-end;">
                <div style="flex:1;background:#4f46e5;border-radius:12px;border-bottom-right-radius:4px;padding:10px;max-width:70%;">
                    <div style="height:4px;background:white;border-radius:1px;opacity:0.4;margin-bottom:3px;"></div>
                    <div style="height:4px;background:white;border-radius:1px;opacity:0.4;width:60%;"></div>
                </div>
            </div>
        </div>'''
    # /ANCHOR:WIRE_CHAT
    
    # ANCHOR:WIRE_PREVIEW
    elif visual_hint == "preview":
        wireframe = '''<div style="background:white;border:2px solid #e5e7eb;border-radius:8px;padding:12px;">
            <div style="position:relative;background:linear-gradient(135deg,#f3f4f6 0%,#e5e7eb 100%);border-radius:6px;height:100px;overflow:hidden;">
                <div style="position:absolute;top:15%;left:10%;width:35%;height:30%;background:#dbeafe;border:2px dashed #3b82f6;border-radius:4px;opacity:0.8;"></div>
                <div style="position:absolute;top:45%;left:55%;width:30%;height:40%;background:#dcfce7;border:2px dashed #22c55e;border-radius:4px;opacity:0.7;"></div>
                <div style="position:absolute;top:20%;left:60%;width:25%;height:25%;background:#fce7f3;border:2px dashed #ec4899;border-radius:4px;opacity:0.6;"></div>
            </div>
        </div>'''
    # /ANCHOR:WIRE_PREVIEW
    
    # ANCHOR:WIRE_UPLOAD
    elif visual_hint == "upload" or visual_hint == "upload/dropzone":
        wireframe = '''<div style="background:#fafafa;border:3px dashed #d1d5db;border-radius:8px;padding:24px;text-align:center;">
            <div style="font-size:48px;margin-bottom:12px;">📁</div>
            <div style="height:10px;background:#d1d5db;border-radius:2px;width:70%;margin:0 auto 8px;"></div>
            <div style="height:6px;background:#e5e7eb;border-radius:1px;width:50%;margin:0 auto;"></div>
        </div>'''
    # /ANCHOR:WIRE_UPLOAD
    
    # ANCHOR:WIRE_GRID
    elif visual_hint == "grid":
        wireframe = '''<div style="background:white;border:2px solid #e5e7eb;border-radius:8px;padding:12px;">
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;">
                <div style="aspect-ratio:1;background:#dbeafe;display:flex;flex-direction:column;align-items:center;justify-content:center;border-radius:4px;">
                    <span style="font-family:serif;font-size:14px;color:#1e40af;">Aa</span>
                    <span style="font-family:sans-serif;font-size:10px;color:#3b82f6;">Serif</span>
                </div>
                <div style="aspect-ratio:1;background:#dcfce7;display:flex;flex-direction:column;align-items:center;justify-content:center;border-radius:4px;">
                    <span style="font-family:sans-serif;font-size:14px;color:#166534;">Aa</span>
                    <span style="font-size:10px;color:#22c55e;">Sans</span>
                </div>
                <div style="aspect-ratio:1;background:#fef3c7;display:flex;flex-direction:column;align-items:center;justify-content:center;border-radius:4px;">
                    <span style="font-family:monospace;font-size:14px;color:#92400e;">Aa</span>
                    <span style="font-size:10px;color:#f59e0b;">Mono</span>
                </div>
            </div>
        </div>'''
    # /ANCHOR:WIRE_GRID
    
    # ANCHOR:WIRE_ACCORDION
    elif visual_hint == "accordion":
        wireframe = '''<div style="background:white;border:2px solid #e5e7eb;border-radius:8px;padding:12px;">
            <div style="border:1px solid #e5e7eb;border-radius:6px;margin-bottom:6px;">
                <div style="padding:8px;background:#f9fafb;display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:10px;font-weight:600;color:#374151;">Section 1</span>
                    <span style="font-size:10px;color:#6b7280;">▼</span>
                </div>
            </div>
            <div style="border:1px solid #e5e7eb;border-radius:6px;margin-bottom:6px;">
                <div style="padding:8px;background:#f9fafb;display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:10px;font-weight:600;color:#374151;">Section 2</span>
                    <span style="font-size:10px;color:#6b7280;">▼</span>
                </div>
            </div>
            <div style="border:1px solid #e5e7eb;border-radius:6px;">
                <div style="padding:8px;background:#f9fafb;display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:10px;font-weight:600;color:#374151;">Section 3</span>
                    <span style="font-size:10px;color:#6b7280;">▼</span>
                </div>
            </div>
        </div>'''
    # /ANCHOR:WIRE_ACCORDION
    
    # ANCHOR:WIRE_MODAL
    elif visual_hint == "modal" or visual_hint == "modal/dialog":
        wireframe = '''<div style="background:white;border:2px solid #e5e7eb;border-radius:8px;padding:12px;position:relative;">
            <div style="position:absolute;top:8px;right:8px;font-size:14px;color:#9ca3af;">×</div>
            <div style="font-size:12px;font-weight:600;color:#374151;margin-bottom:8px;">Titre Modal</div>
            <div style="height:4px;background:#e5e7eb;border-radius:1px;margin-bottom:4px;"></div>
            <div style="height:4px;background:#e5e7eb;border-radius:1px;width:80%;margin-bottom:12px;"></div>
            <div style="display:flex;gap:8px;justify-content:flex-end;">
                <div style="padding:6px 12px;background:#f3f4f6;border-radius:4px;font-size:10px;color:#6b7280;">Annuler</div>
                <div style="padding:6px 12px;background:#22c55e;border-radius:4px;font-size:10px;color:white;">Confirmer</div>
            </div>
        </div>'''
    # /ANCHOR:WIRE_MODAL
    
    # ANCHOR:WIRE_BREADCRUMB
    elif visual_hint == "breadcrumb":
        wireframe = '''<div style="background:white;border:2px solid #e5e7eb;border-radius:8px;padding:12px;">
            <div style="display:flex;align-items:center;gap:6px;font-size:10px;color:#6b7280;">
                <span style="color:#22c55e;font-weight:600;">Accueil</span>
                <span>></span>
                <span style="color:#22c55e;font-weight:600;">Catégorie</span>
                <span>></span>
                <span style="color:#374151;font-weight:600;">Page</span>
            </div>
            <div style="height:4px;background:#e5e7eb;border-radius:1px;margin-top:10px;"></div>
        </div>'''
    # /ANCHOR:WIRE_BREADCRUMB
    
    # ANCHOR:WIRE_LIST
    elif visual_hint == "list":
        wireframe = '''<div style="background:white;border:2px solid #e5e7eb;border-radius:8px;padding:12px;">
            <div style="display:flex;align-items:center;gap:8px;padding:8px;border-bottom:1px solid #f3f4f6;">
                <div style="width:8px;height:8px;background:#22c55e;border-radius:50%;"></div>
                <div style="flex:1;height:4px;background:#e5e7eb;border-radius:1px;"></div>
            </div>
            <div style="display:flex;align-items:center;gap:8px;padding:8px;border-bottom:1px solid #f3f4f6;">
                <div style="width:8px;height:8px;background:#3b82f6;border-radius:50%;"></div>
                <div style="flex:1;height:4px;background:#e5e7eb;border-radius:1px;"></div>
            </div>
            <div style="display:flex;align-items:center;gap:8px;padding:8px;">
                <div style="width:8px;height:8px;background:#f59e0b;border-radius:50%;"></div>
                <div style="flex:1;height:4px;background:#e5e7eb;border-radius:1px;"></div>
            </div>
        </div>'''
    # /ANCHOR:WIRE_LIST
    
    # ANCHOR:WIRE_BUTTON
    elif visual_hint == "button":
        wireframe = f'''<div style="background:white;border:2px solid #e5e7eb;border-radius:8px;padding:12px;text-align:center;">
            <div style="display:inline-flex;align-items:center;gap:8px;padding:10px 20px;background:{color};border-radius:6px;color:white;font-weight:600;">
                <span style="font-size:14px;">▶</span>
                <span style="font-size:12px;">{method}</span>
            </div>
            <div style="height:4px;background:#e5e7eb;border-radius:1px;margin-top:10px;width:60%;margin-left:auto;margin-right:auto;"></div>
        </div>'''
    # /ANCHOR:WIRE_BUTTON
    
    # ANCHOR:WIRE_GENERIC
    else:
        # Générique = simple bloc
        wireframe = f'''<div style="background:white;border:2px solid #e5e7eb;border-radius:8px;padding:12px;">
            <div style="display:flex;align-items:center;gap:8px;">
                <div style="width:24px;height:24px;background:{color};border-radius:6px;display:flex;align-items:center;justify-content:center;">
                    <span style="font-size:12px;">◆</span>
                </div>
                <div style="flex:1;">
                    <div style="font-size:11px;font-weight:600;color:#374151;">{nom_clair}</div>
                    <div style="font-size:9px;color:#9ca3af;">{endpoint}</div>
                </div>
            </div>
            <div style="margin-top:8px;padding:8px;background:#f9fafb;border-radius:4px;">
                <div style="height:4px;background:#e5e7eb;border-radius:1px;margin-bottom:3px;"></div>
                <div style="height:4px;background:#e5e7eb;border-radius:1px;width:70%;"></div>
            </div>
        </div>'''
    # /ANCHOR:WIRE_GENERIC
    
    # ANCHOR:COMP_CARD
    html = f'''<div class="component-card" style="background:white;border:1px solid #e5e7eb;border-radius:12px;padding:16px;cursor:pointer;transition:all 0.2s;position:relative;" onclick="toggleCheckbox('comp-{comp_id}')">
        <div style="position:absolute;top:12px;right:12px;">
            <input type="checkbox" id="comp-{comp_id}" class="comp-checkbox" value="{comp_id}" style="width:18px;height:18px;cursor:pointer;" onclick="event.stopPropagation();updateValidateButton()">
        </div>
        {wireframe}
        <div style="margin-top:12px;padding-top:12px;border-top:1px solid #f3f4f6;">
            <div style="font-size:13px;font-weight:600;color:#111827;margin-bottom:4px;">{nom_clair}</div>
            {f'<div style="font-size:11px;color:#6b7280;line-height:1.4;margin-bottom:6px;">{description}</div>' if description else ''}
            <div style="font-size:10px;color:#9ca3af;font-family:monospace;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{endpoint}</div>
        </div>
    </div>'''
    # /ANCHOR:COMP_CARD
    
    return html


def generate_html(genome):
    """Génère la page HTML complète"""
    
    # Collecter tous les composants
    components = []
    for phase in genome.get('n0_phases', []):
        for section in phase.get('n1_sections', []):
            for feature in section.get('n2_features', []):
                for comp in feature.get('n3_components', []):
                    comp['_phase'] = phase.get('name', 'Unknown')
                    comp['_section'] = section.get('name', 'Unknown')
                    comp['_feature'] = feature.get('name', 'Unknown')
                    components.append(comp)
    
    # Générer les cartes de composants
    components_html = ""
    for comp in components:
        desc = comp.get('description_ui', '')
        components_html += generate_component_wireframe(comp, comp['_phase'], desc)
    
    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HoméOS - Genome Viewer (Port 9999)</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; overflow: hidden; background: #f8fafc; }}
        
        /* Tabs */
        .tabs {{ display: flex; height: 50px; background: #fff; border-bottom: 1px solid #e5e7eb; }}
        .tab {{ flex: 1; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 14px; color: #6b7280; border-right: 1px solid #e5e7eb; transition: all 0.2s; font-weight: 500; }}
        .tab:last-child {{ border-right: none; }}
        .tab:hover {{ background: #f9fafb; }}
        .tab.active {{ background: #22c55e; color: white; font-weight: 600; }}
        
        /* Main */
        .main {{ display: flex; height: calc(100vh - 50px); }}
        
        /* Sidebar */
        .sidebar {{ width: 280px; background: #fff; border-right: 1px solid #e5e7eb; overflow-y: auto; }}
        .sidebar-header {{ padding: 20px; border-bottom: 1px solid #e5e7eb; }}
        .sidebar-title {{ font-size: 20px; font-weight: 700; color: #22c55e; }}
        .sidebar-subtitle {{ font-size: 12px; color: #9ca3af; margin-top: 4px; }}
        .sidebar-section {{ padding: 20px; border-bottom: 1px solid #f3f4f6; }}
        .sidebar-label {{ font-size: 11px; font-weight: 600; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; }}
        
        /* Content */
        .content {{ flex: 1; overflow-y: auto; padding: 24px; background: #f8fafc; }}
        .genome-container {{ max-width: 1400px; margin: 0 auto; }}
        
        /* Sticky Header */
        .sticky-header {{ position: sticky; top: 0; background: #f8fafc; padding: 16px 24px; border-bottom: 1px solid #e5e7eb; z-index: 100; display: flex; justify-content: space-between; align-items: center; }}
        
        /* Stats */
        .stats {{ display: flex; gap: 24px; margin-bottom: 24px; padding: 16px; background: white; border-radius: 12px; border: 1px solid #e5e7eb; }}
        .stat {{ text-align: center; }}
        .stat-value {{ font-size: 28px; font-weight: 800; color: #22c55e; }}
        .stat-label {{ font-size: 11px; color: #6b7280; text-transform: uppercase; font-weight: 600; }}
        
        /* Component Grid */
        .component-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }}
        .component-card:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,0.1); transform: translateY(-2px); }}
        .component-card.selected {{ border-color: #22c55e; box-shadow: 0 0 0 2px rgba(34,197,94,0.2); }}
    </style>
</head>
<body>
    <!-- Tabs -->
    <div class="tabs">
        <div class="tab">Brainstorm</div>
        <div class="tab">Backend</div>
        <div class="tab active">Frontend</div>
        <div class="tab">Deploy</div>
    </div>

    <!-- Main -->
    <div class="main">
        <!-- Sidebar -->
        <aside class="sidebar">
            <div class="sidebar-header">
                <div class="sidebar-title">HoméOS</div>
                <div class="sidebar-subtitle">Genome Viewer v2.0</div>
            </div>
            <div class="sidebar-section">
                <div class="sidebar-label">Confiance globale</div>
                <div style="font-size: 36px; font-weight: 800; color: #22c55e;">{int(genome.get('metadata', {}).get('confidence_global', 0) * 100)}%</div>
            </div>
            <div class="sidebar-section">
                <div class="sidebar-label">Statistiques</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                    <div style="text-align: center; padding: 12px; background: #f9fafb; border-radius: 8px;">
                        <div style="font-size: 20px; font-weight: 700; color: #22c55e;">{len(genome.get('n0_phases', []))}</div>
                        <div style="font-size: 10px; color: #9ca3af;">phases</div>
                    </div>
                    <div style="text-align: center; padding: 12px; background: #f9fafb; border-radius: 8px;">
                        <div style="font-size: 20px; font-weight: 700; color: #3b82f6;">{len(components)}</div>
                        <div style="font-size: 10px; color: #9ca3af;">composants</div>
                    </div>
                </div>
            </div>
            <div class="sidebar-section">
                <div class="sidebar-label">Wireframes FRD V2</div>
                <div style="font-size: 12px; color: #6b7280; line-height: 1.6;">
                    ✓ status<br>
                    ✓ zoom-controls<br>
                    ✓ download<br>
                    ✓ chat-input<br>
                    ✓ color-palette<br>
                    ✓ choice-card<br>
                    ✓ stencil-card<br>
                    ✓ detail-card<br>
                    ✓ launch-button<br>
                    ✓ apply-changes
                </div>
            </div>
        </aside>

        <!-- Content -->
        <div class="content">
            <!-- Sticky Header -->
            <div class="sticky-header">
                <div style="display: flex; gap: 12px; align-items: center;">
                    <input type="checkbox" id="select-all" style="width: 20px; height: 20px; accent-color: #22c55e; cursor: pointer;" onchange="toggleAll(this)">
                    <label for="select-all" style="font-size: 14px; color: #374151; cursor: pointer; font-weight: 500;">Tout sélectionner</label>
                </div>
                <button id="validate-btn" style="padding: 10px 20px; background: #22c55e; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; opacity: 0.5;" disabled>Valider (0)</button>
            </div>
            
            <div class="genome-container">
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">{len([c for c in components if c.get('method') == 'GET'])}</div>
                        <div class="stat-label">📖 Voir</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" style="color: #3b82f6;">{len([c for c in components if c.get('method') == 'POST'])}</div>
                        <div class="stat-label">➕ Ajouter</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" style="color: #f59e0b;">{len([c for c in components if c.get('method') == 'PUT'])}</div>
                        <div class="stat-label">✏️ Modifier</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" style="color: #6b7280;">{len([c for c in components if c.get('method') not in ['GET', 'POST', 'PUT']])}</div>
                        <div class="stat-label">Autres</div>
                    </div>
                </div>
                
                <h2 style="font-size: 18px; font-weight: 700; color: #111827; margin-bottom: 16px;">🧬 le Génome — {len(components)} composants</h2>
                
                <div class="component-grid">
                    {components_html}
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function toggleAll(source) {{
            checkboxes = document.querySelectorAll('.comp-checkbox');
            checkboxes.forEach(cb => cb.checked = source.checked);
            updateValidateButton();
        }}
        
        function updateValidateButton() {{
            count = document.querySelectorAll('.comp-checkbox:checked').length;
            btn = document.getElementById('validate-btn');
            btn.innerHTML = 'Valider (' + count + ')';
            btn.disabled = count === 0;
            btn.style.opacity = count === 0 ? '0.5' : '1';
        }}
        
        function toggleCheckbox(id) {{
            cb = document.getElementById(id);
            cb.checked = !cb.checked;
            updateValidateButton();
        }}
    </script>
</body>
</html>'''


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
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
        pass  # Silence les logs


if __name__ == '__main__':
    genome = load_genome()
    print(f"🚀 Serveur v2 démarré : http://localhost:{PORT}")
    print(f"   Layout : Vue unique 100% (le Génome)")
    print(f"   Wireframes : 10 FRD V2 + classiques")
    print(f"   Composants : {sum(len(section.get('n2_features', [])) for phase in genome.get('n0_phases', []) for section in phase.get('n1_sections', []))}")
    
    with HTTPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()
