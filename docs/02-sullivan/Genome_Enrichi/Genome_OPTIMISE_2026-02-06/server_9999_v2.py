#!/usr/bin/env python3
"""
Serveur HTTP pour visualisation du Genome - Port 9999
Version 2.1 - Wireframes enrichis (ombres, gradients, style Figma)
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

PORT = 9999
GENOME_FILE = "genome_inferred_kimi_innocent.json"

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

def generate_component_wireframe(component, phase_name, description=""):
    visual_hint = component.get("visual_hint", "generic")
    method = component.get("method", "GET")
    endpoint = component.get("endpoint", "N/A")
    name = component.get("name", "Sans nom")
    comp_id = component.get("id", "unknown")
    
    method_colors = {
        "GET": "#7aca6a",
        "POST": "#5a9ac6", 
        "PUT": "#e4bb5a",
        "DELETE": "#d56363"
    }
    color = method_colors.get(method, "#64748b")
    nom_clair = name.replace("Comp ", "").replace("Component ", "")
    
    # === WIREFRAMES ENRICHIS ===
    
    # STATUS - LEDs avec ombres et gradients
    if visual_hint == "status":
        wireframe = '''<div style="background:linear-gradient(145deg,#ffffff 0%,#f8fafc 100%);border:1px solid #e2e8f0;border-radius:6px;padding:8px;box-shadow:0 1px 3px rgba(0,0,0,0.05),0 1px 2px rgba(0,0,0,0.03);">
            <div style="display:flex;align-items:center;gap:5px;margin-bottom:12px;">
                <div style="width:8px;height:8px;background:linear-gradient(135deg,#7aca6a 0%,#6aba5a 100%);border-radius:50%;box-shadow:0 0 0 2px rgba(140,198,63,0.2);"></div>
                <span style="font-size:13px;font-weight:600;color:#1e293b;letter-spacing:-0.2px;">🏥 Santé du projet</span>
            </div>
            <div style="display:flex;justify-content:center;gap:6px;margin:16px 0;">
                <div style="text-align:center;">
                    <div style="width:12px;height:12px;background:linear-gradient(135deg,#7aca6a 0%,#6aba5a 100%);border-radius:50%;margin:0 auto 6px;box-shadow:0 2px 4px rgba(140,198,63,0.3),inset 0 -2px 4px rgba(0,0,0,0.1);"></div>
                    <span style="font-size:11px;color:#64748b;font-weight:500;">OK</span>
                </div>
                <div style="text-align:center;">
                    <div style="width:12px;height:12px;background:linear-gradient(135deg,#7aca6a 0%,#6aba5a 100%);border-radius:50%;margin:0 auto 6px;box-shadow:0 2px 4px rgba(140,198,63,0.3),inset 0 -2px 4px rgba(0,0,0,0.1);"></div>
                    <span style="font-size:11px;color:#64748b;font-weight:500;">OK</span>
                </div>
                <div style="text-align:center;">
                    <div style="width:12px;height:12px;background:linear-gradient(135deg,#7aca6a 0%,#6aba5a 100%);border-radius:50%;margin:0 auto 6px;box-shadow:0 2px 4px rgba(140,198,63,0.3),inset 0 -2px 4px rgba(0,0,0,0.1);"></div>
                    <span style="font-size:11px;color:#64748b;font-weight:500;">OK</span>
                </div>
                <div style="text-align:center;">
                    <div style="width:12px;height:12px;background:linear-gradient(135deg,#94a3b8 0%,#64748b 100%);border-radius:50%;margin:0 auto 6px;box-shadow:inset 0 2px 4px rgba(0,0,0,0.1);"></div>
                    <span style="font-size:11px;color:#64748b;font-weight:500;">?</span>
                </div>
            </div>
            <div style="background:linear-gradient(90deg,rgba(140,198,63,0.1) 0%,rgba(140,198,63,0.05) 100%);border-radius:6px;padding:8px;text-align:center;">
                <span style="font-size:12px;color:#7aca6a;font-weight:600;">✅ Fonctions vitales présentes</span>
            </div>
        </div>'''
    
    # ZOOM-CONTROLS - Navigation riche
    elif visual_hint == "zoom-controls":
        wireframe = '''<div style="background:linear-gradient(145deg,#ffffff 0%,#f8fafc 100%);border:1px solid #e2e8f0;border-radius:6px;padding:8px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex;align-items:center;gap:5px;margin-bottom:12px;">
                <span style="font-size:13px;font-weight:600;color:#1e293b;letter-spacing:-0.2px;">🔭 Navigation</span>
                <span style="margin-left:auto;font-size:11px;color:#94a3b8;background:#f1f5f9;padding:2px 6px;border-radius:4px;">N2</span>
            </div>
            <div style="display:flex;gap:5px;margin-bottom:12px;">
                <span style="flex:1;padding:6px;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border:1px solid #cbd5e1;border-radius:6px;text-align:center;font-size:12px;color:#475569;font-weight:500;box-shadow:0 1px 2px rgba(0,0,0,0.05);">← Out</span>
                <span style="flex:1;padding:6px;background:linear-gradient(145deg,#5a9ac6 0%,#4a83b6 100%);border:1px solid #3d72a0;border-radius:6px;text-align:center;font-size:12px;color:white;font-weight:600;box-shadow:0 2px 4px rgba(59,130,246,0.3);">🔍 Corps ▼</span>
                <span style="flex:1;padding:6px;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border:1px solid #cbd5e1;border-radius:6px;text-align:center;font-size:12px;color:#475569;font-weight:500;box-shadow:0 1px 2px rgba(0,0,0,0.05);">In →</span>
            </div>
            <div style="background:#f8fafc;border-radius:6px;padding:8px;display:flex;align-items:center;justify-content:center;gap:6px;">
                <span style="color:#7aca6a;font-weight:700;font-size:12px;background:rgba(140,198,63,0.1);padding:2px 8px;border-radius:4px;">◉ Corps</span>
                <span style="color:#94a3b8;font-size:11px;">›</span>
                <span style="color:#64748b;font-size:12px;font-weight:500;">○ Organe</span>
                <span style="color:#94a3b8;font-size:11px;">›</span>
                <span style="color:#64748b;font-size:12px;font-weight:500;">○ Atome</span>
            </div>
        </div>'''
    
    # STENCIL-CARD - Fiche pouvoir enrichie
    elif visual_hint == "stencil-card":
        wireframe = '''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px solid #e2e8f0;border-radius:6px;padding:8px;box-shadow:0 1px 3px rgba(0,0,0,0.05),0 1px 2px rgba(0,0,0,0.03);position:relative;overflow:hidden;">
            <div style="position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,#7aca6a 0%,#9ad85a 100%);"></div>
            <div style="display:flex;align-items:flex-start;gap:5px;margin-bottom:12px;">
                <div style="width:28px;height:28px;background:linear-gradient(135deg,#fff8a0 0%,#f8e090 100%);border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:12px;box-shadow:0 2px 4px rgba(251,191,36,0.2);">💡</div>
                <div style="flex:1;">
                    <div style="font-size:12px;font-weight:700;color:#1e293b;letter-spacing:-0.3px;margin-bottom:4px;">Veille du Système</div>
                    <div style="font-size:13px;color:#64748b;line-height:1.5;">Voir l'état de santé du projet en un coup d'œil</div>
                </div>
            </div>
            <div style="display:flex;gap:5px;margin-top:16px;padding-top:12px;border-top:1px solid #f1f5f9;">
                <span style="flex:1;padding:5px 8px;background:linear-gradient(145deg,#7aca6a 0%,#6aba5a 100%);border-radius:6px;text-align:center;font-size:13px;color:white;font-weight:600;box-shadow:0 2px 4px rgba(140,198,63,0.3);text-shadow:0 1px 2px rgba(0,0,0,0.1);">🟢 Garder</span>
                <span style="flex:1;padding:5px 8px;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border:1px solid #cbd5e1;border-radius:6px;text-align:center;font-size:13px;color:#64748b;font-weight:500;">⚪ Réserve</span>
            </div>
        </div>'''
    
    # DETAIL-CARD - Fiche technique Figma-like
    elif visual_hint == "detail-card":
        wireframe = '''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px solid #e2e8f0;border-radius:6px;padding:8px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex;align-items:center;gap:5px;margin-bottom:12px;padding-bottom:12px;border-bottom:1px solid #f1f5f9;">
                <span style="font-size:12px;font-weight:700;color:#5a9ac6;background:rgba(59,130,246,0.1);padding:3px 8px;border-radius:4px;text-transform:uppercase;letter-spacing:0.5px;">GET</span>
                <span style="font-size:13px;font-weight:600;color:#1e293b;font-family:'SF Mono',monospace;letter-spacing:-0.3px;">/api/health</span>
            </div>
            <div style="background:#f8fafc;border-radius:6px;padding:8px;margin-bottom:12px;">
                <div style="font-size:12px;color:#64748b;margin-bottom:6px;font-weight:500;">Retour JSON</div>
                <div style="font-size:11px;color:#94a3b8;font-family:monospace;background:#1e293b;padding:8px;border-radius:6px;line-height:1.6;">
                    <span style="color:#7aca6a;">{</span><br>
                    &nbsp;&nbsp;<span style="color:#98c8f8;">"status"</span><span style="color:#e2e8f0;">:</span> <span style="color:#b8e8ff;">"ok"</span>,<br>
                    &nbsp;&nbsp;<span style="color:#98c8f8;">"uptime"</span><span style="color:#e2e8f0;">:</span> <span style="color:#f0e080;">3600</span><br>
                    <span style="color:#7aca6a;">}</span>
                </div>
            </div>
            <div style="display:flex;gap:5px;">
                <span style="flex:1;padding:8px;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border:1px solid #cbd5e1;border-radius:6px;text-align:center;font-size:12px;color:#475569;font-weight:600;">📋 Copier</span>
                <span style="flex:1;padding:8px;background:linear-gradient(145deg,#5a9ac6 0%,#4a83b6 100%);border-radius:6px;text-align:center;font-size:12px;color:white;font-weight:600;box-shadow:0 2px 4px rgba(59,130,246,0.3);">↗️ Tester</span>
            </div>
        </div>'''
    
    # COLOR-PALETTE - Style détecté enrichi
    elif visual_hint == "color-palette":
        wireframe = '''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px solid #e2e8f0;border-radius:6px;padding:8px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;">
                <span style="font-size:11px;font-weight:700;color:#1e293b;letter-spacing:-0.2px;">🎨 Style détecté</span>
                <span style="font-size:11px;color:#64748b;background:#f1f5f9;padding:2px 8px;border-radius:6px;">3.2s</span>
            </div>
            <div style="display:flex;gap:5px;margin-bottom:14px;">
                <div style="flex:1;aspect-ratio:1;background:linear-gradient(145deg,#5a9ac6 0%,#4a83b6 100%);border-radius:7px;box-shadow:0 2px 4px rgba(59,130,246,0.3),inset 0 1px 0 rgba(255,255,255,0.2);position:relative;overflow:hidden;">
                    <div style="position:absolute;bottom:0;left:0;right:0;height:40%;background:rgba(0,0,0,0.1);"></div>
                </div>
                <div style="flex:1;aspect-ratio:1;background:linear-gradient(145deg,#7aca6a 0%,#6aba5a 100%);border-radius:7px;box-shadow:0 2px 4px rgba(140,198,63,0.3),inset 0 1px 0 rgba(255,255,255,0.2);"></div>
                <div style="flex:1;aspect-ratio:1;background:linear-gradient(145deg,#e4bb5a 0%,#c69c4a 100%);border-radius:7px;box-shadow:0 2px 4px rgba(245,158,11,0.3),inset 0 1px 0 rgba(255,255,255,0.2);"></div>
                <div style="flex:1;aspect-ratio:1;background:linear-gradient(145deg,#1e293b 0%,#0f172a 100%);border-radius:7px;box-shadow:0 2px 4px rgba(30,41,59,0.3),inset 0 1px 0 rgba(255,255,255,0.1);"></div>
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:6px;">
                <span style="padding:4px 10px;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border:1px solid #cbd5e1;border-radius:20px;font-size:11px;color:#475569;font-weight:600;">Rounded: 8px</span>
                <span style="padding:4px 10px;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border:1px solid #cbd5e1;border-radius:20px;font-size:11px;color:#475569;font-weight:600;font-family:system-ui;">Inter</span>
                <span style="padding:4px 10px;background:linear-gradient(145deg,#fff8a0 0%,#f8e090 100%);border:1px solid #f0e080;border-radius:20px;font-size:11px;color:#92400e;font-weight:600;">Spacing: 16px</span>
            </div>
        </div>'''
    
    # CHOICE-CARD - Sélection style
    elif visual_hint == "choice-card":
        wireframe = '''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px solid #e2e8f0;border-radius:6px;padding:8px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="font-size:11px;font-weight:700;color:#1e293b;letter-spacing:-0.2px;margin-bottom:14px;">🎨 Choisissez votre style</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:16px;">
                <div style="border:1px solid #e2e8f0;border-radius:7px;padding:8px;text-align:center;background:linear-gradient(145deg,#ffffff 0%,#f8fafc 100%);transition:all 0.2s;cursor:pointer;">
                    <div style="width:16px;height:16px;margin:0 auto 8px;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;">○</div>
                    <span style="font-size:12px;color:#475569;font-weight:600;">Minimal</span>
                </div>
                <div style="border:1px solid #7aca6a;border-radius:7px;padding:8px;text-align:center;background:linear-gradient(145deg,#f5fff0 0%,#e0f8e0 100%);box-shadow:0 0 0 1px rgba(140,198,63,0.2),0 2px 4px rgba(140,198,63,0.1);">
                    <div style="width:16px;height:16px;margin:0 auto 8px;background:linear-gradient(145deg,#7aca6a 0%,#6aba5a 100%);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;color:white;box-shadow:0 2px 4px rgba(140,198,63,0.3);">●</div>
                    <span style="font-size:12px;color:#4a8b54;font-weight:700;">Brutaliste</span>
                </div>
                <div style="border:1px solid #e2e8f0;border-radius:7px;padding:8px;text-align:center;background:linear-gradient(145deg,#ffffff 0%,#f8fafc 100%);">
                    <div style="width:16px;height:16px;margin:0 auto 8px;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;">○</div>
                    <span style="font-size:12px;color:#475569;font-weight:600;">Moderne</span>
                </div>
                <div style="border:1px solid #e2e8f0;border-radius:7px;padding:8px;text-align:center;background:linear-gradient(145deg,#ffffff 0%,#f8fafc 100%);">
                    <div style="width:16px;height:16px;margin:0 auto 8px;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;">○</div>
                    <span style="font-size:12px;color:#475569;font-weight:600;">Corporate</span>
                </div>
            </div>
            <div style="display:flex;justify-content:flex-end;">
                <span style="padding:8px 16px;background:linear-gradient(145deg,#5a9ac6 0%,#4a83b6 100%);border-radius:6px;font-size:13px;color:white;font-weight:600;box-shadow:0 2px 4px rgba(59,130,246,0.3);">Continuer →</span>
            </div>
        </div>'''
    
    # LAUNCH-BUTTON - Fusée enrichie
    elif visual_hint == "launch-button":
        wireframe = '''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px solid #e2e8f0;border-radius:6px;padding:12px;box-shadow:0 1px 3px rgba(0,0,0,0.05);text-align:center;">
            <div style="width:32px;height:32px;margin:0 auto 14px;background:linear-gradient(145deg,#fff8a0 0%,#f8e090 100%);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:24px;box-shadow:0 4px 8px rgba(251,191,36,0.3),inset 0 1px 0 rgba(255,255,255,0.5);">🚀</div>
            <div style="font-size:12px;font-weight:700;color:#1e293b;margin-bottom:6px;letter-spacing:-0.2px;">Génération du code</div>
            <div style="font-size:12px;color:#64748b;margin-bottom:16px;">Prêt à distiller votre projet</div>
            <div style="padding:8px 24px;background:linear-gradient(145deg,#7aca6a 0%,#6aba5a 100%);border-radius:7px;font-size:11px;color:white;font-weight:700;box-shadow:0 4px 8px rgba(140,198,63,0.3),0 2px 4px rgba(140,198,63,0.2),inset 0 1px 0 rgba(255,255,255,0.2);text-shadow:0 1px 2px rgba(0,0,0,0.1);">🚀 Lancer la distillation</div>
        </div>'''
    
    # APPLY-CHANGES - Sauvegarder/Annuler
    elif visual_hint == "apply-changes":
        wireframe = '''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px solid #e2e8f0;border-radius:6px;padding:8px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex;align-items:center;gap:5px;margin-bottom:14px;padding-bottom:14px;border-bottom:1px solid #f1f5f9;">
                <div style="width:22px;height:22px;background:linear-gradient(145deg,#fff8a0 0%,#f8e090 100%);border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:12px;">💾</div>
                <div>
                    <div style="font-size:11px;font-weight:700;color:#1e293b;letter-spacing:-0.2px;">Sauvegarder les changements</div>
                    <div style="font-size:12px;color:#64748b;">3 modifications en attente</div>
                </div>
            </div>
            <div style="display:flex;gap:6px;">
                <span style="flex:1;padding:6px;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border:1px solid #cbd5e1;border-radius:6px;text-align:center;font-size:13px;color:#475569;font-weight:600;transition:all 0.2s;">↩️ Annuler</span>
                <span style="flex:1;padding:6px;background:linear-gradient(145deg,#7aca6a 0%,#6aba5a 100%);border-radius:6px;text-align:center;font-size:13px;color:white;font-weight:700;box-shadow:0 2px 4px rgba(140,198,63,0.3);text-shadow:0 1px 2px rgba(0,0,0,0.1);">💾 Appliquer</span>
            </div>
        </div>'''
    
    # TABLE - Tableau enrichi
    elif visual_hint == "table":
        wireframe = f'''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px solid #e2e8f0;border-radius:6px;padding:8px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:14px;padding-bottom:14px;border-bottom:1px solid #f1f5f9;">
                <div style="width:22px;height:22px;background:linear-gradient(145deg,{color} 0%,{color}dd 100%);border-radius:6px;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                    <span style="color:white;font-size:11px;font-weight:800;text-shadow:0 1px 2px rgba(0,0,0,0.2);">{method[:1]}</span>
                </div>
                <div style="flex:1;">
                    <div style="font-size:11px;font-weight:700;color:#1e293b;letter-spacing:-0.2px;">{nom_clair}</div>
                    <div style="font-size:12px;color:#64748b;font-family:monospace;">{endpoint}</div>
                </div>
                <span style="padding:3px 8px;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border-radius:4px;font-size:11px;color:#475569;font-weight:700;text-transform:uppercase;">{method}</span>
            </div>
            <div style="background:#f8fafc;border-radius:6px;padding:8px;">
                <div style="display:flex;gap:6px;margin-bottom:8px;">
                    <div style="flex:2;height:8px;background:linear-gradient(90deg,#e2e8f0 0%,#cbd5e1 100%);border-radius:2px;"></div>
                    <div style="flex:1;height:8px;background:linear-gradient(90deg,{color}22 0%,{color}44 100%);border-radius:2px;"></div>
                    <div style="width:32px;height:8px;background:{color};border-radius:2px;box-shadow:0 1px 2px rgba(0,0,0,0.1);"></div>
                </div>
                <div style="display:flex;gap:6px;margin-bottom:8px;">
                    <div style="flex:2;height:8px;background:#e2e8f0;border-radius:2px;"></div>
                    <div style="flex:1;height:8px;background:#e2e8f0;border-radius:2px;"></div>
                    <div style="width:32px;height:8px;background:#e2e8f0;border-radius:2px;"></div>
                </div>
                <div style="display:flex;gap:6px;">
                    <div style="flex:2;height:8px;background:#e2e8f0;border-radius:2px;"></div>
                    <div style="flex:1;height:8px;background:#e2e8f0;border-radius:2px;"></div>
                    <div style="width:32px;height:8px;background:#e2e8f0;border-radius:2px;"></div>
                </div>
            </div>
        </div>'''
    
    # CARD - Carte enrichie
    elif visual_hint == "card":
        wireframe = f'''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px solid #e2e8f0;border-radius:6px;padding:8px;box-shadow:0 1px 3px rgba(0,0,0,0.05);position:relative;overflow:hidden;">
            <div style="position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,{color} 0%,{color}88 100%);"></div>
            <div style="display:flex;align-items:center;gap:5px;margin-bottom:12px;">
                <div style="width:28px;height:28px;background:linear-gradient(145deg,{color} 0%,{color}dd 100%);border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:13px;box-shadow:0 2px 4px rgba(0,0,0,0.1);">◆</div>
                <div style="flex:1;">
                    <div style="font-size:12px;font-weight:700;color:#1e293b;letter-spacing:-0.3px;">{nom_clair}</div>
                    <div style="font-size:12px;color:#64748b;">{method} {endpoint}</div>
                </div>
            </div>
            <div style="height:6px;background:linear-gradient(90deg,#f1f5f9 0%,#e2e8f0 100%);border-radius:3px;position:relative;overflow:hidden;">
                <div style="position:absolute;top:0;left:0;width:60%;height:100%;background:linear-gradient(90deg,{color}44 0%,{color} 100%);border-radius:3px;"></div>
            </div>
        </div>'''
    
    # FORM - Formulaire enrichi
    elif visual_hint == "form":
        wireframe = '''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px solid #e2e8f0;border-radius:6px;padding:8px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex;align-items:center;gap:5px;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid #f1f5f9;">
                <span style="font-size:11px;font-weight:700;color:#1e293b;letter-spacing:-0.2px;">Formulaire</span>
                <span style="margin-left:auto;font-size:11px;color:#94a3b8;">2 champs requis</span>
            </div>
            <div style="margin-bottom:14px;">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
                    <span style="font-size:12px;font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:0.3px;">Nom du projet</span>
                    <span style="font-size:11px;color:#d56363;">*</span>
                </div>
                <div style="height:36px;border:1px solid #cbd5e1;border-radius:6px;background:linear-gradient(145deg,#ffffff 0%,#f8fafc 100%);box-shadow:inset 0 1px 2px rgba(0,0,0,0.05);"></div>
            </div>
            <div style="margin-bottom:16px;">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
                    <span style="font-size:12px;font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:0.3px;">Description</span>
                </div>
                <div style="height:36px;border:1px solid #cbd5e1;border-radius:6px;background:linear-gradient(145deg,#ffffff 0%,#f8fafc 100%);box-shadow:inset 0 1px 2px rgba(0,0,0,0.05);"></div>
            </div>
            <div style="display:flex;gap:6px;padding-top:12px;border-top:1px solid #f1f5f9;">
                <span style="flex:1;padding:6px;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border:1px solid #cbd5e1;border-radius:6px;text-align:center;font-size:13px;color:#475569;font-weight:600;">Annuler</span>
                <span style="flex:1;padding:6px;background:linear-gradient(145deg,#7aca6a 0%,#6aba5a 100%);border-radius:6px;text-align:center;font-size:13px;color:white;font-weight:700;box-shadow:0 2px 4px rgba(140,198,63,0.3);">Valider</span>
            </div>
        </div>'''
    
    # DASHBOARD - Dashboard enrichi
    elif visual_hint == "dashboard":
        wireframe = '''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px solid #e2e8f0;border-radius:6px;padding:8px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
                <span style="font-size:11px;font-weight:700;color:#1e293b;letter-spacing:-0.2px;">📊 Dashboard</span>
                <span style="font-size:11px;color:#64748b;background:#f1f5f9;padding:3px 8px;border-radius:6px;">Temps réel</span>
            </div>
            <div style="display:flex;gap:5px;margin-bottom:16px;">
                <div style="flex:1;text-align:center;padding:8px;background:linear-gradient(145deg,#f5fff0 0%,#e0f8e0 100%);border:1px solid #b8ecd0;border-radius:7px;">
                    <div style="font-size:22px;font-weight:800;color:#4a8b54;margin-bottom:2px;letter-spacing:-0.5px;">29</div>
                    <div style="font-size:11px;color:#6ac87a;font-weight:600;text-transform:uppercase;letter-spacing:0.3px;">Composants</div>
                </div>
                <div style="flex:1;text-align:center;padding:8px;background:linear-gradient(145deg,#e8f4ff 0%,#d0e6ff 100%);border:1px solid #b8d8f0;border-radius:7px;">
                    <div style="font-size:22px;font-weight:800;color:#4a7a9e;margin-bottom:2px;letter-spacing:-0.5px;">9</div>
                    <div style="font-size:11px;color:#5a9ac6;font-weight:600;text-transform:uppercase;letter-spacing:0.3px;">Phases</div>
                </div>
            </div>
            <div style="background:#f8fafc;border-radius:6px;padding:8px;">
                <div style="display:flex;align-items:flex-end;gap:4px;height:50px;padding:0 4px;">
                    <div style="flex:1;height:40%;background:linear-gradient(180deg,#7aca6a 0%,#6aba5a 100%);border-radius:3px 3px 0 0;box-shadow:0 -2px 4px rgba(140,198,63,0.2);"></div>
                    <div style="flex:1;height:65%;background:linear-gradient(180deg,#7aca6a 0%,#6aba5a 100%);border-radius:3px 3px 0 0;box-shadow:0 -2px 4px rgba(140,198,63,0.2);"></div>
                    <div style="flex:1;height:45%;background:linear-gradient(180deg,#5a9ac6 0%,#4a83b6 100%);border-radius:3px 3px 0 0;box-shadow:0 -2px 4px rgba(59,130,246,0.2);"></div>
                    <div style="flex:1;height:80%;background:linear-gradient(180deg,#7aca6a 0%,#6aba5a 100%);border-radius:3px 3px 0 0;box-shadow:0 -2px 4px rgba(140,198,63,0.2);"></div>
                    <div style="flex:1;height:55%;background:linear-gradient(180deg,#e4bb5a 0%,#c69c4a 100%);border-radius:3px 3px 0 0;box-shadow:0 -2px 4px rgba(245,158,11,0.2);"></div>
                </div>
            </div>
        </div>'''
    
    # CHAT/BUBBLE - Chat enrichi
    elif visual_hint == "chat/bubble":
        wireframe = '''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px solid #e2e8f0;border-radius:6px;padding:8px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex;gap:6px;margin-bottom:14px;">
                <div style="width:22px;height:22px;background:linear-gradient(145deg,#6a8aca 0%,#5a7aba 100%);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:white;box-shadow:0 2px 4px rgba(79,70,229,0.3);text-shadow:0 1px 2px rgba(0,0,0,0.2);">S</div>
                <div style="flex:1;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border-radius:6px 12px 12px 4px;padding:8px;box-shadow:0 1px 2px rgba(0,0,0,0.05);">
                    <div style="height:5px;background:#cbd5e1;border-radius:2px;margin-bottom:5px;width:85%;"></div>
                    <div style="height:5px;background:#cbd5e1;border-radius:2px;width:60%;"></div>
                </div>
            </div>
            <div style="display:flex;gap:6px;justify-content:flex-end;">
                <div style="flex:1;max-width:70%;background:linear-gradient(145deg,#6a8aca 0%,#5a7aba 100%);border-radius:6px 12px 4px 12px;padding:8px;box-shadow:0 2px 4px rgba(79,70,229,0.2);">
                    <div style="height:5px;background:rgba(255,255,255,0.4);border-radius:2px;margin-bottom:5px;width:80%;"></div>
                    <div style="height:5px;background:rgba(255,255,255,0.4);border-radius:2px;width:50%;"></div>
                </div>
            </div>
            <div style="margin-top:12px;padding-top:12px;border-top:1px solid #f1f5f9;display:flex;gap:5px;">
                <div style="flex:1;height:32px;background:#f1f5f9;border-radius:16px;"></div>
                <div style="width:22px;height:22px;background:linear-gradient(145deg,#6a8aca 0%,#5a7aba 100%);border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-size:11px;box-shadow:0 2px 4px rgba(79,70,229,0.3);">➤</div>
            </div>
        </div>'''
    
    # EDITOR - Éditeur enrichi
    elif visual_hint == "editor":
        wireframe = '''<div style="background:linear-gradient(145deg,#1e293b 0%,#0f172a 100%);border:1px solid #334155;border-radius:6px;padding:8px;box-shadow:0 4px 6px rgba(0,0,0,0.1),0 2px 4px rgba(0,0,0,0.1);">
            <div style="display:flex;gap:6px;margin-bottom:12px;padding-bottom:12px;border-bottom:1px solid #334155;">
                <div style="width:10px;height:10px;background:#d56363;border-radius:50%;box-shadow:0 0 0 1px rgba(239,68,68,0.3);"></div>
                <div style="width:10px;height:10px;background:#e4bb5a;border-radius:50%;box-shadow:0 0 0 1px rgba(245,158,11,0.3);"></div>
                <div style="width:10px;height:10px;background:#7aca6a;border-radius:50%;box-shadow:0 0 0 1px rgba(140,198,63,0.3);"></div>
                <div style="flex:1;text-align:center;font-size:11px;color:#64748b;font-family:monospace;">component.py</div>
            </div>
            <div style="font-family:'SF Mono',monospace;font-size:12px;line-height:1.7;">
                <div style="display:flex;gap:5px;"><span style="color:#64748b;width:16px;text-align:right;">1</span><span style="color:#a8d8f0;">def</span> <span style="color:#8acad8;">render</span><span style="color:#e2e8f0;">(</span><span style="color:#e0b0b0;">props</span><span style="color:#e2e8f0;">):</span></div>
                <div style="display:flex;gap:5px;"><span style="color:#64748b;width:16px;text-align:right;">2</span><span style="color:#e2e8f0;">&nbsp;&nbsp;&nbsp;&nbsp;</span><span style="color:#a8d8f0;">return</span> <span style="color:#b8e8ff;">"hello"</span></div>
                <div style="display:flex;gap:5px;"><span style="color:#64748b;width:16px;text-align:right;">3</span></div>
            </div>
        </div>'''
    
    # PREVIEW - Aperçu enrichi
    elif visual_hint == "preview":
        wireframe = '''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px solid #e2e8f0;border-radius:6px;padding:8px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
                <span style="font-size:11px;font-weight:700;color:#1e293b;letter-spacing:-0.2px;">👁️ Aperçu maquette</span>
                <span style="font-size:11px;color:#64748b;background:#f1f5f9;padding:2px 8px;border-radius:6px;">3 zones</span>
            </div>
            <div style="position:relative;background:linear-gradient(135deg,#f8fafc 0%,#e2e8f0 100%);border-radius:6px;height:100px;overflow:hidden;box-shadow:inset 0 2px 4px rgba(0,0,0,0.05);">
                <div style="position:absolute;top:15%;left:10%;width:35%;height:30%;background:linear-gradient(135deg,rgba(59,130,246,0.2) 0%,rgba(37,99,235,0.15) 100%);border:1px dashed #5a9ac6;border-radius:6px;box-shadow:0 0 0 4px rgba(59,130,246,0.1);"></div>
                <div style="position:absolute;top:45%;left:55%;width:30%;height:40%;background:linear-gradient(135deg,rgba(140,198,63,0.2) 0%,rgba(122,179,46,0.15) 100%);border:1px dashed #7aca6a;border-radius:6px;box-shadow:0 0 0 4px rgba(140,198,63,0.1);"></div>
                <div style="position:absolute;bottom:10%;left:5%;width:25%;height:25%;background:linear-gradient(135deg,rgba(236,72,153,0.15) 0%,rgba(219,39,119,0.1) 100%);border:1px dashed #ec4899;border-radius:6px;box-shadow:0 0 0 4px rgba(236,72,153,0.1);"></div>
            </div>
            <div style="display:flex;gap:5px;margin-top:12px;">
                <span style="padding:3px 8px;background:rgba(59,130,246,0.1);border-radius:4px;font-size:13px;color:#5a9ac6;font-weight:600;">Header</span>
                <span style="padding:3px 8px;background:rgba(140,198,63,0.1);border-radius:4px;font-size:13px;color:#7aca6a;font-weight:600;">Content</span>
                <span style="padding:3px 8px;background:rgba(236,72,153,0.1);border-radius:4px;font-size:13px;color:#ec4899;font-weight:600;">Sidebar</span>
            </div>
        </div>'''
    
    # UPLOAD - Zone upload enrichie
    elif visual_hint == "upload":
        wireframe = '''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px dashed #cbd5e1;border-radius:6px;padding:24px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,0.05);position:relative;overflow:hidden;">
            <div style="position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,#7aca6a 0%,#9ad85a 50%,#7aca6a 100%);"></div>
            <div style="width:36px;height:36px;margin:0 auto 16px;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:28px;box-shadow:0 2px 4px rgba(0,0,0,0.05),inset 0 1px 0 rgba(255,255,255,0.8);">📁</div>
            <div style="font-size:11px;font-weight:700;color:#1e293b;margin-bottom:6px;letter-spacing:-0.2px;">Déposez votre fichier ici</div>
            <div style="font-size:12px;color:#64748b;margin-bottom:12px;">ou cliquez pour parcourir</div>
            <div style="height:8px;background:#f1f5f9;border-radius:4px;overflow:hidden;margin:0 20px;">
                <div style="width:0%;height:100%;background:linear-gradient(90deg,#7aca6a 0%,#9ad85a 100%);"></div>
            </div>
            <div style="font-size:11px;color:#94a3b8;margin-top:10px;">PNG, JPG, Figma jusqu'à 20MB</div>
        </div>'''
    
    # GRID - Galerie enrichie
    elif visual_hint == "grid":
        wireframe = '''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px solid #e2e8f0;border-radius:6px;padding:8px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;">
                <span style="font-size:11px;font-weight:700;color:#1e293b;letter-spacing:-0.2px;">🎨 Galerie de styles</span>
                <span style="font-size:11px;color:#64748b;">6 layouts</span>
            </div>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px;">
                <div style="aspect-ratio:1;background:linear-gradient(145deg,#d0e6ff 0%,#b8d8f0 100%);border-radius:7px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;box-shadow:0 2px 4px rgba(59,130,246,0.15);border:1px solid #7aca6a;position:relative;">
                    <span style="font-family:Georgia,serif;font-size:13px;color:#4a7a9e;font-weight:600;">Aa</span>
                    <span style="font-size:13px;color:#5a9ac6;font-weight:600;">Serif</span>
                    <div style="position:absolute;top:4px;right:4px;width:10px;height:10px;background:#7aca6a;border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-size:13px;font-weight:700;">✓</div>
                </div>
                <div style="aspect-ratio:1;background:linear-gradient(145deg,#e0f8e0 0%,#b8ecd0 100%);border-radius:7px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                    <span style="font-family:system-ui,sans-serif;font-size:13px;color:#4a8b54;font-weight:600;">Aa</span>
                    <span style="font-size:13px;color:#6ac87a;">Sans</span>
                </div>
                <div style="aspect-ratio:1;background:linear-gradient(145deg,#fff8a0 0%,#f8e090 100%);border-radius:7px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                    <span style="font-family:monospace;font-size:13px;color:#92400e;font-weight:600;">Aa</span>
                    <span style="font-size:13px;color:#e4bb5a;">Mono</span>
                </div>
            </div>
        </div>'''
    
    # GENERIC - Fallback enrichi
    else:
        wireframe = f'''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px solid #e2e8f0;border-radius:6px;padding:8px;box-shadow:0 1px 3px rgba(0,0,0,0.05);position:relative;overflow:hidden;">
            <div style="position:absolute;top:0;left:0;width:2px;height:100%;background:linear-gradient(180deg,{color} 0%,{color}88 100%);"></div>
            <div style="display:flex;align-items:center;gap:5px;">
                <div style="width:36px;height:36px;background:linear-gradient(145deg,{color} 0%,{color}dd 100%);border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:13px;color:white;box-shadow:0 2px 4px rgba(0,0,0,0.1);">◆</div>
                <div style="flex:1;">
                    <div style="font-size:11px;font-weight:700;color:#1e293b;letter-spacing:-0.2px;">{nom_clair}</div>
                    <div style="font-size:12px;color:#64748b;font-family:monospace;">{endpoint}</div>
                </div>
                <span style="padding:3px 8px;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border-radius:4px;font-size:11px;color:#475569;font-weight:700;">{method}</span>
            </div>
            <div style="margin-top:12px;padding-top:12px;border-top:1px solid #f1f5f9;">
                <div style="display:flex;gap:6px;">
                    <div style="flex:1;height:6px;background:#e2e8f0;border-radius:3px;"></div>
                    <div style="width:40px;height:6px;background:{color};border-radius:3px;opacity:0.5;"></div>
                </div>
            </div>
        </div>'''
    
    # CARTE FINALE AVEC CHECKBOX
    html = f'''<div class="component-card" style="background:white;border:1px solid #e2e8f0;border-radius:14px;padding:0;cursor:pointer;transition:all 0.2s;position:relative;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.05);" onclick="toggleCheckbox('comp-{comp_id}')">
        <div style="position:absolute;bottom:12px;right:12px;z-index:10;background:rgba(255,255,255,0.9);padding:4px;border-radius:6px;box-shadow:0 1px 3px rgba(0,0,0,0.1);">
            <input type="checkbox" id="comp-{comp_id}" class="comp-checkbox" value="{comp_id}" style="width:18px;height:18px;cursor:pointer;accent-color:#6a9a4f;" onclick="event.stopPropagation();updateValidateButton()">
        </div>
        {wireframe}
        <div style="padding:6px 12px;border-top:1px solid #f1f5f9;background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);">
            <div style="font-size:12px;font-weight:700;color:#1e293b;margin-bottom:4px;letter-spacing:-0.2px;">{nom_clair}</div>
            {f'<div style="font-size:13px;color:#64748b;line-height:1.4;margin-bottom:6px;">{description}</div>' if description else ''}
            <div style="display:flex;align-items:center;gap:5px;">
                <span style="padding:2px 6px;background:{color}15;color:{color};border-radius:4px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;">{method}</span>
                <span style="font-size:12px;color:#94a3b8;font-family:monospace;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1;">{endpoint}</span>
            </div>
        </div>
    </div>'''
    
    return html


def generate_hierarchy_html(genome):
    """Generate 4-level hierarchy: Corps > Organes > Cellules > Atomes"""
    
    # Classification des composants par niveau
    corps_items = []      # Pages/Templates
    organes_items = []    # Zones sémantiques
    cellules_items = []   # Composants composites
    atomes_items = []     # Éléments primitifs
    
    for phase in genome.get('n0_phases', []):
        for section in phase.get('n1_sections', []):
            for feature in section.get('n2_features', []):
                for comp in feature.get('n3_components', []):
                    comp['_phase'] = phase.get('name', 'Unknown')
                    visual = comp.get('visual_hint', 'generic')
                    
                    # Classification par visual_hint
                    if visual in ['preview', 'table', 'dashboard', 'grid', 'editor', 'list', 'accordion']:
                        corps_items.append(comp)
                    elif visual in ['stepper', 'breadcrumb', 'status', 'zoom-controls', 'chat/bubble']:
                        organes_items.append(comp)
                    elif visual in ['upload', 'color-palette', 'stencil-card', 'detail-card', 
                                   'choice-card', 'card', 'form', 'chat-input', 'modal']:
                        cellules_items.append(comp)
                    else:  # button, launch-button, apply-changes, etc.
                        atomes_items.append(comp)
    
    # Ordre pédagogique user-teaching-friendly
    # Corps: ordre de découverte - preview d'abord (où tout commence)
    corps_order = ['preview', 'table', 'dashboard', 'grid', 'editor', 'list', 'accordion']
    corps_items.sort(key=lambda x: corps_order.index(x.get('visual_hint', '')) if x.get('visual_hint', '') in corps_order else 99)
    
    # Organes: ordre de navigation - stepper d'abord (où en suis-je)
    organes_order = ['stepper', 'breadcrumb', 'status', 'zoom-controls', 'chat/bubble']
    organes_items.sort(key=lambda x: organes_order.index(x.get('visual_hint', '')) if x.get('visual_hint', '') in organes_order else 99)
    
    # Cellules: ordre d'interaction - upload d'abord (la première action)
    cellules_order = ['upload', 'color-palette', 'stencil-card', 'detail-card', 'choice-card', 'card', 'form', 'chat-input', 'modal']
    cellules_items.sort(key=lambda x: cellules_order.index(x.get('visual_hint', '')) if x.get('visual_hint', '') in cellules_order else 99)
    
    # Atomes: ordre d'usage fréquent - boutons génériques d'abord
    atomes_order = ['button', 'launch-button', 'apply-changes']
    atomes_items.sort(key=lambda x: atomes_order.index(x.get('visual_hint', '')) if x.get('visual_hint', '') in atomes_order else 99)
    
    def render_items(items):
        html = '<div class="component-grid">'
        for comp in items:
            desc = comp.get('description_ui', '')
            html += generate_component_wireframe(comp, comp['_phase'], desc)
        html += '</div>'
        return html
    
    return f'''
    <div class="hierarchy-container">
        <!-- CORPS: Templates et Pages -->
        <div class="level-section">
            <div class="level-header" onclick="toggleLevel('corps')">
                <span class="level-arrow" id="arrow-corps">6</span>
                <span class="level-title">Corps</span>
                <span class="level-count">{len(corps_items)}</span>
                <span class="level-desc">Templates et pages conteneurs</span>
            </div>
            <div class="level-content open" id="content-corps">
                <p class="level-explanation">
                    Les Corps sont les pages et templates qui structurent l'espace ecran. 
                    Vous commencez par l'apercu maquette, puis explorez les rapports, dashboards et editeurs 
                    qui organisent votre travail en espaces coherents.
                </p>
                {render_items(corps_items)}
            </div>
        </div>
        
        <!-- ORGANES: Zones sémantiques -->
        <div class="level-section">
            <div class="level-header" onclick="toggleLevel('organes')">
                <span class="level-arrow" id="arrow-organes">6</span>
                <span class="level-title">Organes</span>
                <span class="level-count">{len(organes_items)}</span>
                <span class="level-desc">Zones sémantiques et navigation</span>
            </div>
            <div class="level-content open" id="content-organes">
                <p class="level-explanation">
                    Les Organes sont les zones fonctionnelles qui guident votre navigation. 
                    Le stepper vous situe dans le processus, le fil d'ariane vous oriente, 
                    les indicateurs d'etat vous informent sur la sante du systeme.
                </p>
                {render_items(organes_items)}
            </div>
        </div>
        
        <!-- CELLULES: Composants composites -->
        <div class="level-section">
            <div class="level-header" onclick="toggleLevel('cellules')">
                <span class="level-arrow" id="arrow-cellules">6</span>
                <span class="level-title">Cellules</span>
                <span class="level-count">{len(cellules_items)}</span>
                <span class="level-desc">Blocs fonctionnels composes</span>
            </div>
            <div class="level-content open" id="content-cellules">
                <p class="level-explanation">
                    Les Cellules sont les outils d'interaction : vous uploadez un design, 
                    recevez une palette de couleurs, choisissez des styles, consultez des details. 
                    Chaque Cellule realise une tache complete pour construire votre interface.
                </p>
                {render_items(cellules_items)}
            </div>
        </div>
        
        <!-- ATOMES: Elements primitifs -->
        <div class="level-section">
            <div class="level-header" onclick="toggleLevel('atomes')">
                <span class="level-arrow" id="arrow-atomes">6</span>
                <span class="level-title">Atomes</span>
                <span class="level-count">{len(atomes_items)}</span>
                <span class="level-desc">Elements d'interface indivisibles</span>
            </div>
            <div class="level-content open" id="content-atomes">
                <p class="level-explanation">
                    Les Atomes sont les briques de base de l'interface : les boutons que vous cliquez, 
                    les lancements d'actions, les validations. Invisibles seuls, ils donnent vie aux Cellules 
                    et rendent l'interface interactive.
                </p>
                {render_items(atomes_items)}
            </div>
        </div>
    </div>
    '''

def generate_html(genome):
    components = []
    for phase in genome.get('n0_phases', []):
        for section in phase.get('n1_sections', []):
            for feature in section.get('n2_features', []):
                for comp in feature.get('n3_components', []):
                    comp['_phase'] = phase.get('name', 'Unknown')
                    comp['_section'] = section.get('name', 'Unknown')
                    comp['_feature'] = feature.get('name', 'Unknown')
                    components.append(comp)
    
    hierarchy_html = generate_hierarchy_html(genome)
    
    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HoméOS - Genome Viewer (Port 9999)</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; overflow: hidden; background: #f8fafc; }}
        
        /* Tabs enrichis */
        .tabs {{ display: flex; height: 52px; background: #fff; border-bottom: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
        .tab {{ flex: 1; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 14px; color: #64748b; border-right: 1px solid #f1f5f9; transition: all 0.2s; font-weight: 500; letter-spacing: -0.2px; }}
        .tab:last-child {{ border-right: none; }}
        .tab:hover {{ background: linear-gradient(180deg, #fff 0%, #f8fafc 100%); color: #334155; }}
        .tab.active {{ background: transparent !important; color: #1e293b; font-size: 1.2em; font-weight: 900; box-shadow: none; border-bottom: 3px solid #7aca6a; padding-bottom: 10px; }}
        
        /* Main */
        .main {{ display: flex; height: calc(100vh - 52px); transition: opacity 0.3s ease-in-out; }}
        
        /* Vue Browser et Editor - Layout scrollable */
        #browser-view {{ }}
        #editor-view {{ display: none; background: #f8fafc; height: calc(100vh - 52px); }}
        
        /* Animations fluides Option A */
        .accordion-section {{ transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }}
        .accordion-content {{ transition: all 0.25s ease-out; }}
        .hierarchy-item {{ transition: background-color 0.15s ease, transform 0.1s ease; }}
        .hierarchy-item:hover {{ transform: translateX(4px); }}
        #editor-breadcrumb {{ transition: all 0.3s ease; }}
        .corps-thumb {{ transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); }}
        .corps-thumb:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}
        #editor-toolbar button {{ transition: all 0.15s ease; }}
        
        /* Sélection canvas */
        .canvas-container-active {{ box-shadow: inset 0 0 0 2px #7aca6a; }}
        
        /* Sidebar enrichie */
        .sidebar {{ width: 300px; background: linear-gradient(180deg, #fff 0%, #fafafa 100%); border-right: 1px solid #e2e8f0; overflow-y: auto; box-shadow: 2px 0 8px rgba(0,0,0,0.03); }}
        .sidebar-header {{ padding: 20px; border-bottom: 1px solid #e2e8f0; background: linear-gradient(180deg, #fff 0%, #f8fafc 100%); }}
        .sidebar-title {{ font-size: 22px; font-weight: 800; color: #7aca6a; letter-spacing: -0.5px; }}
        .sidebar-subtitle {{ font-size: 12px; color: #94a3b8; margin-top: 4px; font-weight: 500; }}
        .sidebar-section {{ padding: 18px; border-bottom: 1px solid #f1f5f9; }}
        .sidebar-label {{ font-size: 12px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 14px; }}
        
        /* Content */
        .content {{ flex: 1; overflow-y: auto; padding: 24px; background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%); }}
        .genome-container {{ max-width: 1400px; margin: 0 auto; }}
        
        /* Sticky Header enrichi */
        .sticky-header {{ position: sticky; top: 0; background: linear-gradient(180deg, rgba(248,250,252,0.98) 0%, rgba(241,245,249,0.98) 100%); padding: 16px 24px; border-bottom: 1px solid #e2e8f0; z-index: 100; display: flex; justify-content: space-between; align-items: center; backdrop-filter: blur(8px); border-radius: 0 0 12px 12px; margin: -24px -24px 20px -24px; }}
        
        /* Stats enrichis */
        .stats {{ display: flex; gap: 16px; margin-bottom: 24px; }}
        .stat {{ flex: 1; text-align: center; padding: 18px 12px; background: linear-gradient(145deg, #fff 0%, #fafafa 100%); border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); transition: all 0.2s; }}
        .stat:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}
        .stat-value {{ font-size: 28px; font-weight: 800; color: #7aca6a; letter-spacing: -1px; }}
        .stat-label {{ font-size: 12px; color: #64748b; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px; margin-top: 4px; }}
        
        /* Hierarchical Genome Structure */
        .hierarchy-container {{ padding: 0; }}
        
        .level-section {{ border-top: 1px solid #e2e8f0; }}
        .level-section:first-child {{ border-top: none; }}
        
        .level-header {{ 
            display: flex; align-items: center; gap: 12px; padding: 16px 24px; 
            cursor: pointer; background: #fff; user-select: none;
            transition: background 0.15s;
        }}
        .level-header:hover {{ background: #f8fafc; }}
        
        .level-arrow {{ 
            font-family: "Wingdings 2", sans-serif; font-size: 16px; color: #64748b;
            width: 20px; text-align: center;
        }}
        
        .level-title {{ 
            font-size: 15px; font-weight: 600; color: #1e293b; 
            text-transform: uppercase; letter-spacing: 0.5px;
        }}
        .level-count {{ 
            font-size: 13px; color: #94a3b8; font-weight: 500; 
            margin-left: 8px; background: #f1f5f9; padding: 2px 10px; border-radius: 10px;
        }}
        
        .level-desc {{ 
            font-size: 14px; color: #64748b; margin-left: auto; font-weight: 400;
        }}
        
        .level-content {{ 
            padding: 0 24px 24px 56px; background: #fafafa; display: none;
        }}
        .level-content.open {{ display: block; }}
        
        .level-explanation {{
            font-size: 14px; color: #64748b; margin-bottom: 20px; line-height: 1.6;
            padding: 16px; background: #fff; border-radius: 8px; border: 1px solid #e2e8f0; border-left: 3px solid #7aca6a;
        }}
        
        /* Component Grid */
        .component-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }}
        .component-card:hover {{ box-shadow: 0 8px 24px rgba(0,0,0,0.1); transform: translateY(-2px); }}
        .component-card.selected {{ border-color: #7aca6a; box-shadow: 0 0 0 3px rgba(140,198,63,0.15), 0 8px 24px rgba(140,198,63,0.1); }}
    </style>
</head>
<body>
    <div class="tabs">
        <div class="tab" onclick="switchTab(this, 'brs')">Brainstorm</div>
        <div class="tab" onclick="switchTab(this, 'bkd')">Backend</div>
        <div class="tab active" onclick="switchTab(this, 'frd')" id="tab-frd">Frontend</div>
        <div class="tab" onclick="switchTab(this, 'dpl')">Deploy</div>
    </div>

    <div id="browser-view" class="main" style="display:flex;">
        <aside class="sidebar">
            <div class="sidebar-header">
                <div class="sidebar-title">HoméOS</div>
                <div class="sidebar-subtitle">Architecture Genome</div>
            </div>
            <div class="sidebar-section">
                <div class="sidebar-label">Le Genome</div>
                <p style="font-size: 13px; color: #166534; line-height: 1.6; margin-bottom: 12px;">
                    <strong>Le Genome est l'ADN de votre application.</strong> Il capture la structure et les interactions.
                </p>
                <p style="font-size: 12px; color: #15803d; line-height: 1.5;">
                    <strong>Production:</strong> Inférence par confrontation de 4 sources.<br>
                    <strong>Organisation:</strong> Hiérarchie biologique Corps/Organes/Cellules/Atomes.
                </p>
            </div>
            <div class="sidebar-section">
                <div class="sidebar-label">Confiance globale</div>
                <div style="font-size: 42px; font-weight: 800; color: #7aca6a; letter-spacing: -2px; text-shadow: 0 2px 4px rgba(140,198,63,0.2);">{int(genome.get('metadata', {}).get('confidence_global', 0) * 100)}%</div>
            </div>
            <div class="sidebar-section">
                <div class="sidebar-label">Statistiques</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                    <div style="text-align: center; padding: 14px; background: linear-gradient(145deg, #fff 0%, #f8fafc 100%); border-radius: 10px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <div style="font-size: 24px; font-weight: 800; color: #7aca6a; letter-spacing: -1px;">{len(genome.get('n0_phases', []))}</div>
                        <div style="font-size: 11px; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px;">phases</div>
                    </div>
                    <div style="text-align: center; padding: 14px; background: linear-gradient(145deg, #fff 0%, #f8fafc 100%); border-radius: 10px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <div style="font-size: 24px; font-weight: 800; color: #5a9ac6; letter-spacing: -1px;">{len(components)}</div>
                        <div style="font-size: 11px; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px;">composants</div>
                    </div>
                </div>
            </div>
            <div class="sidebar-section">
                <div class="sidebar-label">Types de composants</div>
                <div style="font-size: 13px; color: #64748b; line-height: 1.8; font-weight: 500;">
                    <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;">
                        <span style="width:8px;height:8px;background:#7aca6a;border-radius:50%;"></span>
                        <span style="flex:1;">Indicateurs d'etat</span>
                    </div>
                    <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;">
                        <span style="width:8px;height:8px;background:#5a9ac6;border-radius:50%;"></span>
                        <span style="flex:1;">Contrôles de navigation</span>
                    </div>
                    <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;">
                        <span style="width:8px;height:8px;background:#e4bb5a;border-radius:50%;"></span>
                        <span style="flex:1;">Cartes de donnees</span>
                    </div>
                    <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;">
                        <span style="width:8px;height:8px;background:#8b5cf6;border-radius:50%;"></span>
                        <span style="flex:1;">Visualisation design</span>
                    </div>
                    <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;">
                        <span style="width:8px;height:8px;background:#ec4899;border-radius:50%;"></span>
                        <span style="flex:1;">Formulaires de choix</span>
                    </div>
                    <div style="display:flex;align-items:center;gap:6px;">
                        <span style="width:8px;height:8px;background:#64748b;border-radius:50%;"></span>
                        <span style="flex:1;">Actions principales</span>
                    </div>
                </div>
            </div>
        </aside>

        <div class="content">
            <div class="sticky-header">
                <div style="display: flex; gap: 14px; align-items: center;">
                    <input type="checkbox" id="select-all" style="width: 22px; height: 22px; accent-color: #7aca6a; cursor: pointer;" onclick="toggleAll(this)">
                    <label for="select-all" style="font-size: 15px; color: #334155; cursor: pointer; font-weight: 600; letter-spacing: -0.2px;">Tout sélectionner</label>
                </div>
                <button id="validate-btn" style="padding: 12px 24px; background: linear-gradient(145deg, #7aca6a 0%, #6aba5a 100%); color: white; border: none; border-radius: 10px; font-size: 14px; font-weight: 700; cursor: pointer; opacity: 0.5; box-shadow: 0 2px 8px rgba(140,198,63,0.3); text-shadow: 0 1px 2px rgba(0,0,0,0.1); transition: all 0.2s;" disabled onclick="openEditorFromSelection()">Valider (0)</button>
            </div>
            
            <div class="genome-container">
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">{len([c for c in components if c.get('method') == 'GET'])}</div>
                        <div class="stat-label">Lire (GET)</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" style="color: #5a9ac6;">{len([c for c in components if c.get('method') == 'POST'])}</div>
                        <div class="stat-label">Creer (POST)</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" style="color: #e4bb5a;">{len([c for c in components if c.get('method') == 'PUT'])}</div>
                        <div class="stat-label">Modifier (PUT)</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" style="color: #64748b;">{len([c for c in components if c.get('method') not in ['GET', 'POST', 'PUT']])}</div>
                        <div class="stat-label">Autres</div>
                    </div>
                </div>
                
                <h2 style="font-size: 18px; font-weight: 700; color: #1e293b; margin-bottom: 4px; letter-spacing: -0.3px;">Architecture Genome</h2>
                <p style="font-size: 14px; color: #64748b; margin-bottom: 20px;">{len(components)} composants classifies par niveau d'abstraction</p>
                
                {hierarchy_html}
            </div>
        </div>
    </div>
    
    <!-- VUE 2: FIGMA EDITOR (cachée par défaut) -->
    <div id="editor-view" style="position:relative;">
        <!-- Bouton Retour -->
        <button onclick="closeEditor()" style="position:absolute; top:16px; left:16px; z-index:1000; padding:10px 18px; background:linear-gradient(145deg, #fff 0%, #f8fafc 100%); border:1px solid #e2e8f0; border-radius:8px; cursor:pointer; display:flex; align-items:center; gap:8px; font-size:14px; font-weight:600; color:#475569; box-shadow:0 2px 8px rgba(0,0,0,0.1); transition:all 0.2s;" onmouseover="this.style.background='#f1f5f9';this.style.transform='translateY(-2px)';" onmouseout="this.style.background='linear-gradient(145deg, #fff 0%, #f8fafc 100%)';this.style.transform='translateY(0);'">
            <span style="font-size:16px;">↑</span> Retour au Genome
        </button>
        
        <div id="editor-container" style="width:100%; height:100%; position:relative;">
            <div id="row-corps" style="height:140px; background:linear-gradient(180deg,#fff 0%,#f8fafc 100%); border-bottom:1px solid #e2e8f0; display:flex; gap:16px; padding:16px 24px; overflow-x:auto; align-items:center;">
                <!-- Miniatures des Corps sélectionnés -->
            </div>
            <div id="editor-main" style="display:flex; height:calc(100% - 140px);">
                <div id="editor-sidebar" style="width:280px; background:linear-gradient(180deg,#fff 0%,#fafafa 100%); border-right:1px solid #e2e8f0; overflow-y:auto; padding:16px;">
                    <!-- Titre Sidebar -->
                    <div style="font-size:12px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:16px;">Hiérarchie</div>
                    <!-- Hiérarchie accordéon -->
                    <div id="sidebar-accordion"></div>
                </div>
                <div style="flex:1; display:flex; flex-direction:column;">
                    <!-- Breadcrumb -->
                    <div id="editor-breadcrumb" style="height:48px; background:#fff; border-bottom:1px solid #e2e8f0; display:flex; align-items:center; padding:0 20px; gap:8px; font-size:14px;">
                        <span style="color:#94a3b8;">Sélectionnez un élément</span>
                    </div>
                    <div id="canvas-container" style="flex:1; background:#f8fafc; position:relative;">
                        <canvas id="fabric-canvas"></canvas>
                    </div>
                </div>
            </div>
            
            <!-- Toolbar avec Zoom + Clear + Export -->
            <div id="editor-toolbar" style="height:56px; background:linear-gradient(180deg,#fff 0%,#fafafa 100%); border-top:1px solid #e2e8f0; display:flex; align-items:center; justify-content:space-between; padding:0 24px;">
                <div style="display:flex; align-items:center; gap:16px;">
                    <!-- Zoom Controls -->
                    <div style="display:flex; align-items:center; gap:4px; background:#f1f5f9; padding:4px; border-radius:8px;">
                        <button onclick="zoomOut()" style="width:32px; height:32px; background:#fff; border:none; border-radius:6px; cursor:pointer; font-size:16px; color:#475569; display:flex; align-items:center; justify-content:center; box-shadow:0 1px 2px rgba(0,0,0,0.05);" onmouseover="this.style.background='#f8fafc'" onmouseout="this.style.background='#fff'">−</button>
                        <span id="zoom-level" style="width:50px; text-align:center; font-size:13px; font-weight:600; color:#64748b;">100%</span>
                        <button onclick="zoomIn()" style="width:32px; height:32px; background:#fff; border:none; border-radius:6px; cursor:pointer; font-size:16px; color:#475569; display:flex; align-items:center; justify-content:center; box-shadow:0 1px 2px rgba(0,0,0,0.05);" onmouseover="this.style.background='#f8fafc'" onmouseout="this.style.background='#fff'">+</button>
                        <button onclick="resetZoom()" style="width:32px; height:32px; background:#fff; border:none; border-radius:6px; cursor:pointer; font-size:12px; color:#64748b; display:flex; align-items:center; justify-content:center; box-shadow:0 1px 2px rgba(0,0,0,0.05); margin-left:4px;" title="Reset zoom" onmouseover="this.style.background='#f8fafc'" onmouseout="this.style.background='#fff'">⟲</button>
                    </div>
                    
                    <!-- Object Count -->
                    <div style="font-size:13px; color:#64748b;">
                        <span id="canvas-objects-count">0 Corps</span>
                    </div>
                    
                    <!-- Delete Selected -->
                    <button onclick="window.deleteSelectedObject()" style="padding:8px 16px; background:#fef2f2; border:1px solid #fecaca; border-radius:6px; font-size:12px; color:#dc2626; cursor:pointer; display:flex; align-items:center; gap:6px;" title="Supprimer la sélection (Suppr)" onmouseover="this.style.background='#fee2e2'" onmouseout="this.style.background='#fef2f2'">
                        <span>🗑️</span> Suppr
                    </button>
                    
                    <!-- Clear All -->
                    <button onclick="clearCanvas()" style="padding:8px 16px; background:#f1f5f9; border:1px solid #e2e8f0; border-radius:6px; font-size:12px; color:#64748b; cursor:pointer; display:flex; align-items:center; gap:6px;" title="Vider tout le canvas" onmouseover="this.style.background='#e2e8f0'" onmouseout="this.style.background='#f1f5f9'">
                        <span>❌</span> Tout
                    </button>
                    
                    <!-- Restore Session -->
                    <button onclick="restoreSession()" style="padding:8px 16px; background:#f0fdf4; border:1px solid #bbf7d0; border-radius:6px; font-size:12px; color:#166534; cursor:pointer; display:flex; align-items:center; gap:6px;" title="Restaurer la session précédente" onmouseover="this.style.background='#dcfce7'" onmouseout="this.style.background='#f0fdf4'">
                        <span>↩️</span> Restaurer
                    </button>
                </div>
                
                <div style="display:flex; align-items:center; gap:12px;">
                    <!-- Delete hint -->
                    <span style="font-size:12px; color:#94a3b8;">Suppr pour effacer</span>
                    
                    <button onclick="exportToJSON()" style="padding:10px 20px; background:linear-gradient(145deg,#7aca6a 0%,#6aba5a 100%); color:#fff; border:none; border-radius:8px; font-size:13px; font-weight:600; cursor:pointer; display:flex; align-items:center; gap:8px; box-shadow:0 2px 8px rgba(122,202,106,0.3);">
                        <span>⬇️</span> Exporter JSON
                    </button>
                </div>
            </div>
        </div>
        
        <!-- Modal Brainstorm -->
        <div id="brainstorm-modal" style="display:none; position:fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.5); z-index:10000; align-items:center; justify-content:center;">
            <div style="background:#fff; border-radius:16px; padding:32px; width:90%; max-width:480px; box-shadow:0 25px 50px rgba(0,0,0,0.25);">
                <div style="display:flex; align-items:center; gap:12px; margin-bottom:24px;">
                    <span style="font-size:28px;">💡</span>
                    <div>
                        <div style="font-size:18px; font-weight:700; color:#1e293b;">Brainstorm Dimensions</div>
                        <div style="font-size:13px; color:#64748b;">Définissez les dimensions pour ce Corps</div>
                    </div>
                </div>
                
                <div id="brainstorm-corps-name" style="font-size:14px; font-weight:600; color:#5a9ac6; margin-bottom:20px; padding:12px 16px; background:#f1f5f9; border-radius:8px;">
                    Corps: <span id="brainstorm-target-name">Unknown</span>
                </div>
                
                <div style="margin-bottom:20px;">
                    <label style="display:block; font-size:12px; font-weight:600; color:#64748b; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:8px;">Largeur (px)</label>
                    <input type="number" id="brainstorm-width" value="1440" min="320" max="3840" style="width:100%; padding:12px 16px; border:2px solid #e2e8f0; border-radius:8px; font-size:15px; color:#1e293b; outline:none; transition:border-color 0.2s;" onfocus="this.style.borderColor='#7aca6a'" onblur="this.style.borderColor='#e2e8f0'">
                </div>
                
                <div style="margin-bottom:24px;">
                    <label style="display:block; font-size:12px; font-weight:600; color:#64748b; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:8px;">Hauteur (px)</label>
                    <input type="number" id="brainstorm-height" value="900" min="200" max="2160" style="width:100%; padding:12px 16px; border:2px solid #e2e8f0; border-radius:8px; font-size:15px; color:#1e293b; outline:none; transition:border-color 0.2s;" onfocus="this.style.borderColor='#7aca6a'" onblur="this.style.borderColor='#e2e8f0'">
                </div>
                
                <div style="display:flex; gap:12px;">
                    <button onclick="closeBrainstormModal()" style="flex:1; padding:12px 20px; background:#f1f5f9; border:none; border-radius:8px; font-size:14px; font-weight:600; color:#64748b; cursor:pointer; transition:all 0.2s;" onmouseover="this.style.background='#e2e8f0'" onmouseout="this.style.background='#f1f5f9'">Annuler</button>
                    <button onclick="validateBrainstorm()" style="flex:1; padding:12px 20px; background:linear-gradient(145deg,#7aca6a 0%,#6aba5a 100%); border:none; border-radius:8px; font-size:14px; font-weight:600; color:#fff; cursor:pointer; box-shadow:0 2px 8px rgba(122,202,106,0.3); transition:all 0.2s;" onmouseover="this.style.transform='translateY(-1px)';this.style.boxShadow='0 4px 12px rgba(122,202,106,0.4)';" onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 2px 8px rgba(122,202,106,0.3)';">Valider</button>
                </div>
            </div>
            </div>
        </div>
    </div>
    
    <script src="https://unpkg.com/fabric@5.3.0/dist/fabric.min.js"></script>
    <script>
        // ============================================================
        // DONNÉES GENOME (injectées depuis Python)
        // ============================================================
        
        const GENOME_DATA = {json.dumps(genome, ensure_ascii=False)};
        
        // Extraction des 9 Corps (N0) depuis le genome
        const N0_CORPS = (GENOME_DATA.n0_phases || []).map(phase => ({{
            id: phase.id,
            name: phase.name || phase.id,
            description: phase.description || '',
            order: phase.order || 0,
            visual_hint: phase.visual_hint || 'dashboard'
        }}));
        
        // Cache des wireframes générés (persistance UX)
        const WIREFRAME_CACHE_KEY = 'homeos_wireframe_cache';
        let WIREFRAME_CACHE = {{}};
        
        // Charger le cache depuis localStorage
        function loadWireframeCache() {{
            try {{
                const cached = localStorage.getItem(WIREFRAME_CACHE_KEY);
                if (cached) WIREFRAME_CACHE = JSON.parse(cached);
            }} catch(e) {{ console.warn('Cache non chargé'); }}
        }}
        
        // Sauvegarder le cache
        function saveWireframeCache() {{
            try {{
                localStorage.setItem(WIREFRAME_CACHE_KEY, JSON.stringify(WIREFRAME_CACHE));
            }} catch(e) {{ console.warn('Cache non sauvegardé'); }}
        }}
        
        // État de navigation FRD (cliquable, contextuel)
        let currentNavigation = {{
            corpsId: null,      // Corps actif (N0) - détermine le contexte
            organeId: null,     // Organe actif (N1) - filtré par corps
            celluleId: null,    // Cellule active (N2) - filtrée par organe
            level: 0
        }};
        
        // Charger le cache au démarrage
        loadWireframeCache();
        
        // ============================================================
        // PHASE 0: Génération des Blueprints (au chargement)
        // ============================================================
        
        const CORP_STRUCTURES = {{
            'preview': {{ layout: 'single', zones: [{{type:'preview-area',x:0,y:0,w:1440,h:900}}] }},
            'table': {{ layout: 'header-content', zones: [{{type:'header',x:0,y:0,w:1440,h:80}},{{type:'table',x:0,y:80,w:1440,h:820}}] }},
            'dashboard': {{ layout: 'header-grid-footer', zones: [{{type:'header',x:0,y:0,w:1440,h:80}},{{type:'stats',x:0,y:80,w:1440,h:200}},{{type:'content',x:0,y:280,w:1440,h:620}}] }},
            'grid': {{ layout: 'masonry', zones: [{{type:'grid',x:0,y:0,w:1440,h:900}}] }},
            'editor': {{ layout: 'sidebar-content', zones: [{{type:'sidebar',x:0,y:0,w:280,h:900}},{{type:'editor',x:280,y:0,w:1160,h:900}}] }},
            'default': {{ layout: 'flex', zones: [{{type:'content',x:0,y:0,w:1440,h:900}}] }}
        }};
        
        function generateBlueprint(corpsId, visualHint) {{
            const structure = CORP_STRUCTURES[visualHint] || CORP_STRUCTURES['default'];
            return {{
                id: corpsId,
                width: 1440,
                height: 900,
                viewport: 'desktop',
                structure: structure,
                organes: [],
                generated_at: new Date().toISOString(),
                status: 'ready'
            }};
        }}
        
        function saveToLocalStorage(key, data) {{
            try {{
                localStorage.setItem(key, JSON.stringify(data));
            }} catch(e) {{
                console.warn('localStorage non disponible');
            }}
        }}
        
        function loadFromLocalStorage(key) {{
            try {{
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : null;
            }} catch(e) {{
                return null;
            }}
        }}
        
        // Génération background au chargement
        document.addEventListener('DOMContentLoaded', function() {{
            // Détecter les Corps de la page
            const corpsElements = document.querySelectorAll('.level-section');
            const blueprintData = {{
                version: '1.0',
                generated_at: new Date().toISOString(),
                blueprints: {{}}
            }};
            
            // Simulation: générer pour quelques types connus
            const knownTypes = ['preview', 'table', 'dashboard', 'grid', 'editor'];
            knownTypes.forEach(type => {{
                const blueprint = generateBlueprint(type, type);
                blueprintData.blueprints[type] = blueprint;
                saveToLocalStorage(`blueprint_${{type}}`, blueprint);
            }});
            
            saveToLocalStorage('homeos_blueprints', blueprintData);
            console.log('Blueprints générés:', blueprintData);
        }});
        
        // ============================================================
        // PHASE 1: Switch Vue 1 → Vue 2 avec transition alpha
        // ============================================================
        
        function openEditor(selectedIds) {{
            console.log('Ouverture editeur avec selection:', selectedIds);
            
            // 1. Rendre les 9 Corps (N0) dans le Row
            renderRowCorps();
            
            // 2. Activer le premier Corps ou celui sélectionné
            const targetCorpsId = selectedIds.length > 0 ? selectedIds[0] : N0_CORPS[0]?.id;
            if (targetCorpsId) {{
                activateCorps(targetCorpsId);
            }}
            
            // 3. Afficher l'editeur et scroller vers lui
            const editorView = document.getElementById('editor-view');
            editorView.style.display = 'block';
            
            // Scroll smooth vers l'editeur
            setTimeout(() => {{
                editorView.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            }}, 100);
            
            // 4. Initialiser Fabric.js et le drill-down
            setTimeout(() => {{
                initFabricEditor([]);
                setupDrillDown();
            }}, 500);
        }}
        
        // Rend les 9 Corps (N0) dans le Row - Aperçus DISTINCTS par type
        function renderRowCorps() {{
            const row = document.getElementById('row-corps');
            
            // Mapping explicite phase → type visuel
            const phaseToType = {{
                'phase_1_ir': 'table',
                'phase_2_arbiter': 'card', 
                'phase_3_session': 'status',
                'phase_4_navigation': 'breadcrumb',
                'phase_5_layout': 'grid',
                'phase_6_upload': 'upload',
                'phase_7_chat': 'chat',
                'phase_8_validation': 'dashboard',
                'phase_9_zoom': 'preview'
            }};
            
            row.innerHTML = N0_CORPS.map((corps, index) => {{
                // FORCER le type visuel selon la phase
                const visualType = phaseToType[corps.id] || 'default';
                const wireframeSVG = generateWireframeByType(visualType);
                const isActive = currentNavigation.corpsId === corps.id;
                
                return `
                <div class="corps-thumb ${{isActive ? 'active' : ''}}" 
                     data-id="${{corps.id}}" 
                     onclick="activateCorps('${{corps.id}}')"
                     draggable="true"
                     style="width:140px;height:100px;background:${{isActive ? '#f0fdf4' : '#fff'}};border:2px solid ${{isActive ? '#7aca6a' : '#e2e8f0'}};border-radius:10px;padding:10px;cursor:pointer;flex-shrink:0;position:relative;transition:all 0.2s ease;box-shadow:${{isActive ? '0 4px 12px rgba(122,202,106,0.3)' : '0 1px 3px rgba(0,0,0,0.05)'}};">
                    <div style="position:absolute;top:6px;right:6px;width:20px;height:20px;background:${{isActive ? '#7aca6a' : '#f1f5f9'}};border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:10px;color:${{isActive ? '#fff' : '#94a3b8'}};font-weight:700;">${{index + 1}}</div>
                    <div style="width:100%;height:45px;background:linear-gradient(145deg,#f8fafc 0%,#f1f5f9 100%);border-radius:6px;margin-bottom:8px;display:flex;align-items:center;justify-content:center;overflow:hidden;border:1px solid #e2e8f0;">
                        ${{wireframeSVG}}
                    </div>
                    <div style="font-size:11px;font-weight:${{isActive ? '700' : '600'}};color:${{isActive ? '#166534' : '#1e293b'}};text-align:center;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${{corps.name}}</div>
                    <div style="font-size:9px;color:#94a3b8;text-align:center;margin-top:2px;">${{getOrganesCount(corps.id)}} organes</div>
                </div>
                `;
            }}).join('');
            
            // Activer drag & drop
            row.querySelectorAll('.corps-thumb').forEach(thumb => {{
                thumb.addEventListener('dragstart', (e) => {{
                    e.dataTransfer.setData('corps-id', thumb.dataset.id);
                    thumb.style.opacity = '0.5';
                }});
                thumb.addEventListener('dragend', () => {{
                    thumb.style.opacity = '1';
                }});
            }});
        }}
        
        // Récupère ou génère le wireframe d'un Corps
        function getOrGenerateWireframe(corps) {{
            if (WIREFRAME_CACHE[corps.id]) {{
                return WIREFRAME_CACHE[corps.id];
            }}
            
            // Générer un aperçu visuel simple selon le type
            const svg = generateWireframeSVG(corps);
            WIREFRAME_CACHE[corps.id] = svg;
            saveWireframeCache();
            return svg;
        }}
        
        // Génère un SVG wireframe par TYPE (aperçus DISTINCTS)
        function generateWireframeByType(type) {{
            const wireframes = {{
                'table': `
                    <svg viewBox="0 0 100 60" style="width:100%;height:100%;">
                        <rect x="5" y="5" width="90" height="12" rx="2" fill="#475569"/>
                        <rect x="5" y="22" width="90" height="8" rx="1" fill="#e2e8f0"/>
                        <rect x="5" y="32" width="90" height="8" rx="1" fill="#f1f5f9"/>
                        <rect x="5" y="42" width="90" height="8" rx="1" fill="#e2e8f0"/>
                        <line x1="35" y1="22" x2="35" y2="50" stroke="#cbd5e1" stroke-width="0.5"/>
                        <line x1="65" y1="22" x2="65" y2="50" stroke="#cbd5e1" stroke-width="0.5"/>
                    </svg>`,
                'card': `
                    <svg viewBox="0 0 100 60" style="width:100%;height:100%;">
                        <rect x="10" y="5" width="80" height="50" rx="8" fill="#fff" stroke="#e2e8f0" stroke-width="2"/>
                        <rect x="20" y="15" width="60" height="8" rx="2" fill="#1e293b"/>
                        <rect x="20" y="28" width="40" height="6" rx="1" fill="#64748b"/>
                        <circle cx="75" cy="42" r="10" fill="#22c55e"/>
                        <text x="75" y="45" text-anchor="middle" fill="#fff" font-size="8">✓</text>
                    </svg>`,
                'status': `
                    <svg viewBox="0 0 100 60" style="width:100%;height:100%;">
                        <rect x="5" y="5" width="90" height="50" rx="4" fill="#f8fafc"/>
                        <circle cx="20" cy="20" r="8" fill="#22c55e"/>
                        <rect x="35" y="15" width="55" height="10" rx="2" fill="#e2e8f0"/>
                        <circle cx="20" cy="42" r="8" fill="#3b82f6"/>
                        <rect x="35" y="37" width="40" height="10" rx="2" fill="#e2e8f0"/>
                    </svg>`,
                'breadcrumb': `
                    <svg viewBox="0 0 100 60" style="width:100%;height:100%;">
                        <rect x="5" y="20" width="25" height="15" rx="3" fill="#3b82f6"/>
                        <text x="17" y="30" text-anchor="middle" fill="#fff" font-size="7">1</text>
                        <rect x="32" y="20" width="25" height="15" rx="3" fill="#e2e8f0"/>
                        <text x="44" y="30" text-anchor="middle" fill="#64748b" font-size="7">2</text>
                        <rect x="59" y="20" width="25" height="15" rx="3" fill="#e2e8f0"/>
                        <text x="71" y="30" text-anchor="middle" fill="#64748b" font-size="7">3</text>
                        <path d="M 30 27 L 32 27" stroke="#94a3b8" stroke-width="1"/>
                        <path d="M 57 27 L 59 27" stroke="#94a3b8" stroke-width="1"/>
                    </svg>`,
                'grid': `
                    <svg viewBox="0 0 100 60" style="width:100%;height:100%;">
                        <rect x="5" y="5" width="27" height="22" rx="3" fill="#dbeafe" stroke="#3b82f6" stroke-width="0.5"/>
                        <rect x="36" y="5" width="27" height="22" rx="3" fill="#dcfce7" stroke="#22c55e" stroke-width="0.5"/>
                        <rect x="67" y="5" width="27" height="22" rx="3" fill="#fef3c7" stroke="#f59e0b" stroke-width="0.5"/>
                        <rect x="5" y="32" width="27" height="22" rx="3" fill="#f3e8ff" stroke="#a855f7" stroke-width="0.5"/>
                        <rect x="36" y="32" width="27" height="22" rx="3" fill="#ffe4e6" stroke="#f43f5e" stroke-width="0.5"/>
                    </svg>`,
                'upload': `
                    <svg viewBox="0 0 100 60" style="width:100%;height:100%;">
                        <rect x="5" y="5" width="90" height="50" rx="4" fill="#f0fdf4" stroke="#22c55e" stroke-width="1" stroke-dasharray="3,2"/>
                        <rect x="35" y="12" width="30" height="20" rx="2" fill="#dcfce7"/>
                        <path d="M 42 22 L 50 15 L 58 22" stroke="#22c55e" stroke-width="2" fill="none"/>
                        <line x1="50" y1="15" x2="50" y2="28" stroke="#22c55e" stroke-width="2"/>
                        <rect x="20" y="38" width="60" height="8" rx="2" fill="#bbf7d0"/>
                    </svg>`,
                'chat': `
                    <svg viewBox="0 0 100 60" style="width:100%;height:100%;">
                        <rect x="8" y="8" width="55" height="18" rx="9" fill="#dbeafe"/>
                        <rect x="37" y="30" width="55" height="18" rx="9" fill="#dcfce7"/>
                        <rect x="8" y="50" width="35" height="6" rx="3" fill="#e2e8f0"/>
                    </svg>`,
                'dashboard': `
                    <svg viewBox="0 0 100 60" style="width:100%;height:100%;">
                        <rect x="5" y="5" width="90" height="12" rx="2" fill="#475569"/>
                        <rect x="5" y="22" width="28" height="16" rx="2" fill="#22c55e" opacity="0.8"/>
                        <rect x="36" y="22" width="28" height="16" rx="2" fill="#3b82f6" opacity="0.8"/>
                        <rect x="67" y="22" width="28" height="16" rx="2" fill="#f59e0b" opacity="0.8"/>
                        <rect x="5" y="42" width="90" height="13" rx="2" fill="#e2e8f0"/>
                    </svg>`,
                'preview': `
                    <svg viewBox="0 0 100 60" style="width:100%;height:100%;">
                        <rect x="10" y="5" width="80" height="45" rx="4" fill="#f8fafc" stroke="#e2e8f0" stroke-width="2"/>
                        <rect x="20" y="15" width="60" height="25" rx="2" fill="#e2e8f0"/>
                        <circle cx="50" cy="47" r="3" fill="#cbd5e1"/>
                    </svg>`,
                'default': `
                    <svg viewBox="0 0 100 60" style="width:100%;height:100%;">
                        <rect x="15" y="10" width="70" height="40" rx="4" fill="#f1f5f9" stroke="#e2e8f0" stroke-width="2"/>
                        <rect x="25" y="20" width="50" height="8" rx="2" fill="#cbd5e1"/>
                        <rect x="25" y="32" width="30" height="6" rx="2" fill="#e2e8f0"/>
                    </svg>`
            }};
            
            return wireframes[type] || wireframes['default'];
        }}
        
        // Fonction legacy pour compatibilité
        function generateWireframeSVG(corps) {{
            const phaseToType = {{
                'phase_1_ir': 'table', 'phase_2_arbiter': 'card',
                'phase_3_session': 'status', 'phase_4_navigation': 'breadcrumb',
                'phase_5_layout': 'grid', 'phase_6_upload': 'upload',
                'phase_7_chat': 'chat', 'phase_8_validation': 'dashboard',
                'phase_9_zoom': 'preview'
            }};
            return generateWireframeByType(phaseToType[corps.id] || 'default');
        }}
        
        // Compte les organes d'un Corps
        function getOrganesCount(corpsId) {{
            const phase = (GENOME_DATA.n0_phases || []).find(p => p.id === corpsId);
            return phase ? (phase.n1_sections || []).length : 0;
        }}
        
        // Active un Corps (navigation FRD cliquable)
        function activateCorps(corpsId) {{
            console.log('Activation Corps:', corpsId);
            currentNavigation.corpsId = corpsId;
            currentNavigation.organeId = null;
            currentNavigation.celluleId = null;
            currentNavigation.level = 0;
            
            // Mettre à jour le Row (highlight)
            renderRowCorps();
            
            // Mettre à jour la sidebar (filtrer par ce corps)
            renderSidebarForCorps(corpsId);
            
            // Mettre à jour le breadcrumb
            updateBreadcrumb();
        }}
        
        function initFabricEditor(blueprints) {{
            // Initialisation Fabric.js
            const canvas = new fabric.Canvas('fabric-canvas', {{
                width: document.getElementById('canvas-container').clientWidth,
                height: document.getElementById('canvas-container').clientHeight,
                backgroundColor: '#f8fafc'
            }});
            
            // Drop zone
            const container = document.getElementById('canvas-container');
            container.addEventListener('dragover', (e) => {{
                e.preventDefault();
            }});
            
            container.addEventListener('drop', (e) => {{
                e.preventDefault();
                const corpsId = e.dataTransfer.getData('corps-id');
                if (corpsId) {{
                    // Vérifier si le blueprint a besoin de brainstorm
                    const blueprint = loadFromLocalStorage(`blueprint_${{corpsId}}`);
                    
                    if (blueprint && blueprint.status === 'missing') {{
                        showBrainstormModal(corpsId);
                        return;
                    }}
                    
                    // Créer le Corps en DIMENSIONS RÉELLES (1440x900 desktop)
                    renderCorpsOnCanvas(canvas, corpsId, e.offsetX, e.offsetY);
                }}
            }});
            
            // Sauvegarder après modification d'objet (move, resize, rotate)
            canvas.on('object:modified', () => {{
                saveCanvasState();
            }});
            
            window.fabricCanvas = canvas;
            console.log('Fabric.js initialisé');
            
            // NE PAS charger automatiquement - demander confirmation
            // setTimeout(loadCanvasState, 100);
        }}
        
        function getSelectedCorpsIds() {{
            const checkboxes = document.querySelectorAll('.comp-checkbox:checked');
            return Array.from(checkboxes).map(cb => cb.dataset.id || cb.id);
        }}
        
        // Connecter le bouton Valider
        document.addEventListener('DOMContentLoaded', function() {{
            const validateBtn = document.getElementById('validate-btn');
            if (validateBtn) {{
                validateBtn.addEventListener('click', () => {{
                    const selectedIds = getSelectedCorpsIds();
                    if (selectedIds.length > 0) {{
                        openEditor(selectedIds);
                    }} else {{
                        alert('Veuillez sélectionner au moins un Corps');
                    }}
                }});
            }}
        }});
        
        // ============================================================
        // Fonctions existantes
        // ============================================================
        
        function switchTab(element, tabName) {{
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            element.classList.add('active');
        }}
        
        function toggleLevel(level) {{
            const content = document.getElementById('content-' + level);
            const arrow = document.getElementById('arrow-' + level);
            if (content && arrow) {{
                content.classList.toggle('open');
                // Webdings: 6 = down (open), 5 = up (closed)
                if (content.classList.contains('open')) {{
                    arrow.textContent = '6';
                }} else {{
                    arrow.textContent = '5';
                }}
            }}
        }}
        
        function toggleAll(source) {{
            const checkboxes = document.querySelectorAll('.comp-checkbox');
            const isChecked = source.checked;
            console.log('ToggleAll - isChecked:', isChecked, 'checkboxes found:', checkboxes.length);
            checkboxes.forEach(cb => {{
                cb.checked = isChecked;
            }});
            updateValidateButton();
        }}
        
        function updateValidateButton() {{
            const count = document.querySelectorAll('.comp-checkbox:checked').length;
            const btn = document.getElementById('validate-btn');
            btn.innerHTML = 'Valider (' + count + ')';
            btn.disabled = count === 0;
            btn.style.opacity = count === 0 ? '0.5' : '1';
            console.log('updateValidateButton - count:', count);
        }}
        
        function toggleCheckbox(id) {{
            const cb = document.getElementById(id);
            if (cb) {{
                cb.checked = !cb.checked;
                updateValidateButton();
            }}
        }}
        
        // Helper pour récupérer les IDs sélectionnés depuis les checkboxes
        function openEditorFromSelection() {{
            const checkboxes = document.querySelectorAll('.comp-checkbox:checked');
            const selectedIds = Array.from(checkboxes).map(cb => cb.id.replace('comp-', ''));
            if (selectedIds.length > 0) {{
                openEditor(selectedIds);
            }} else {{
                alert('Veuillez sélectionner au moins un composant');
            }}
        }}
        
        // Fonction pour retourner à la Vue 1 (scroll up)
        function closeEditor() {{
            const editorView = document.getElementById('editor-view');
            const browserView = document.getElementById('browser-view');
            
            // Reset navigation state
            currentNavigation = {{ corpsId: null, organeId: null, celluleId: null, level: 0 }};
            
            // Scroller vers le haut (browser)
            browserView.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            
            // Cacher l'editeur apres le scroll
            setTimeout(() => {{
                editorView.style.display = 'none';
            }}, 500);
        }}
        
        // ============================================================
        // PHASE 3: Navigation hiérarchique (Sidebar + Breadcrumb + Drill-down)
        // ============================================================
        
        // Extrait la hiérarchie d'un Corps depuis GENOME_DATA (filtré par corpsId)
        function getCorpsHierarchy(corpsId) {{
            const hierarchy = {{ organes: [], cellules: [], atomes: [] }};
            
            // Trouver la phase (Corps) correspondante
            const phase = (GENOME_DATA.n0_phases || []).find(p => p.id === corpsId);
            if (!phase) return hierarchy;
            
            // Parcourir N1→N2→N3 UNIQUEMENT pour ce Corps
            for (const section of phase.n1_sections || []) {{
                // N1 = Organe
                const organe = {{
                    id: section.id || 'section_unknown',
                    name: section.name || section.id || 'Organe',
                    description: section.description || '',
                    cellules: []
                }};
                
                for (const feature of section.n2_features || []) {{
                    // N2 = Cellule
                    const cellule = {{
                        id: feature.id || 'feature_unknown',
                        name: feature.name || feature.id || 'Cellule',
                        description: feature.description || '',
                        atomes: []
                    }};
                    
                    for (const comp of feature.n3_components || []) {{
                        // N3 = Atome
                        cellule.atomes.push({{
                            id: comp.id || 'comp_unknown',
                            name: comp.name || comp.id || 'Atome',
                            visual_hint: comp.visual_hint || 'default',
                            method: comp.method || 'GET'
                        }});
                    }}
                    
                    organe.cellules.push(cellule);
                    hierarchy.cellules.push(cellule);
                }}
                
                hierarchy.organes.push(organe);
            }}
            
            return hierarchy;
        }}
        
        // Rend la sidebar pour un Corps spécifique (FRD cliquable)
        function renderSidebarForCorps(corpsId) {{
            const sidebar = document.getElementById('sidebar-accordion');
            const phase = (GENOME_DATA.n0_phases || []).find(p => p.id === corpsId);
            
            if (!phase) {{
                sidebar.innerHTML = '<div style="padding:20px;color:#94a3b8;text-align:center;">Sélectionnez un Corps</div>';
                return;
            }}
            
            // Header avec info du Corps
            let html = `
                <div style="padding:12px 16px;background:linear-gradient(145deg,#f0fdf4 0%,#dcfce7 100%);border-radius:10px;margin-bottom:16px;border:1px solid #bbf7d0;">
                    <div style="font-size:11px;color:#22c55e;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">Corps Actif</div>
                    <div style="font-size:14px;font-weight:700;color:#166534;">${{phase.name}}</div>
                    <div style="font-size:12px;color:#15803d;margin-top:4px;">${{phase.n1_sections?.length || 0}} organes</div>
                </div>
            `;
            
            // Liste des Organes (N1) de ce Corps uniquement
            const organes = (phase.n1_sections || []).map(section => ({{
                id: section.id,
                name: section.name || section.id,
                description: section.description || '',
                count: (section.n2_features || []).length
            }}));
            
            html += createAccordionSection('organes', `Organes (${{organes.length}})`, organes, 1, corpsId);
            
            sidebar.innerHTML = html;
            attachAccordionListeners(corpsId);
        }}
        
        // Rend la sidebar accordéon (sans le Corps racine) - alias pour compatibilité
        function renderSidebarAccordion(corpsId) {{
            renderSidebarForCorps(corpsId);
        }}
        
        // Crée une section accordéon
        function createAccordionSection(key, title, items, level, corpsId) {{
            const isOpen = level === 1 ? 'open' : ''; // Organes ouverts par défaut
            const arrow = level === 1 ? '▼' : '▶';
            
            let html = `
                <div class="accordion-section" data-section="${{key}}" style="margin-bottom:8px;">
                    <div class="accordion-header" style="display:flex;align-items:center;gap:8px;padding:10px 12px;background:#f8fafc;border-radius:8px;cursor:pointer;transition:background 0.2s;" onmouseover="this.style.background='#f1f5f9'" onmouseout="this.style.background='#f8fafc'">
                        <span class="accordion-arrow" style="font-size:10px;color:#64748b;transition:transform 0.2s;">${{arrow}}</span>
                        <span style="font-size:13px;font-weight:600;color:#334155;flex:1;">${{title}}</span>
                        <span style="font-size:11px;color:#94a3b8;background:#e2e8f0;padding:2px 8px;border-radius:10px;">${{items.length}}</span>
                    </div>
                    <div class="accordion-content ${{isOpen}}" style="padding-left:12px;margin-top:4px;${{isOpen ? '' : 'display:none;'}}">
                        ${{items.map(item => createHierarchyItem(item, level, corpsId)).join('')}}
                    </div>
                </div>
            `;
            return html;
        }}
        
        // Crée un item de hiérarchie cliquable
        function createHierarchyItem(item, level, corpsId) {{
            const indent = level * 12;
            const methodColors = {{
                'GET': '#7aca6a',
                'POST': '#5a9ac6',
                'PUT': '#e4bb5a',
                'DELETE': '#ef4444'
            }};
            const methodColor = methodColors[item.method] || '#64748b';
            
            return `
                <div class="hierarchy-item" 
                     data-id="${{item.id}}" 
                     data-level="${{level}}"
                     data-corps="${{corpsId}}"
                     style="display:flex;align-items:center;gap:8px;padding:8px 12px;margin-bottom:4px;border-radius:6px;cursor:pointer;transition:all 0.2s;margin-left:${{indent}}px;"
                     onmouseover="this.style.background='#f1f5f9'" 
                     onmouseout="this.style.background='transparent'"
                     onclick="handleHierarchyClick('${{item.id}}', ${{level}}, '${{corpsId}}')">
                    <span style="width:6px;height:6px;background:${{methodColor}};border-radius:50%;"></span>
                    <span style="font-size:12px;color:#475569;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${{item.name}}</span>
                    ${{item.method ? `<span style="font-size:10px;color:#94a3b8;text-transform:uppercase;">${{item.method}}</span>` : ''}}
                </div>
            `;
        }}
        
        // Attache les listeners pour l'accordéon
        function attachAccordionListeners(corpsId) {{
            document.querySelectorAll('.accordion-header').forEach(header => {{
                header.addEventListener('click', (e) => {{
                    e.stopPropagation();
                    const section = header.parentElement;
                    const content = section.querySelector('.accordion-content');
                    const arrow = header.querySelector('.accordion-arrow');
                    
                    const isOpen = content.style.display !== 'none';
                    content.style.display = isOpen ? 'none' : 'block';
                    arrow.textContent = isOpen ? '▶' : '▼';
                    arrow.style.transform = isOpen ? 'rotate(0deg)' : 'rotate(90deg)';
                }});
            }});
        }}
        
        // Gère le clic sur un item de hiérarchie
        function handleHierarchyClick(itemId, level, corpsId) {{
            console.log('Clic hiérarchie:', itemId, 'niveau:', level);
            
            // Mettre à jour la navigation
            if (level === 1) {{
                currentNavigation = {{ corpsId, organeId: itemId, celluleId: null, level: 1 }};
            }} else if (level === 2) {{
                currentNavigation = {{ corpsId, organeId: currentNavigation.organeId, celluleId: itemId, level: 2 }};
            }} else if (level === 3) {{
                currentNavigation.level = 3;
            }}
            
            // Mettre à jour le breadcrumb
            updateBreadcrumb();
            
            // Highlight sur le canvas (si l'objet existe)
            highlightOnCanvas(itemId);
        }}
        
        // Met à jour le breadcrumb avec les noms du contexte actif
        function updateBreadcrumb() {{
            const breadcrumb = document.getElementById('editor-breadcrumb');
            const {{ corpsId, organeId, celluleId, level }} = currentNavigation;
            
            if (!corpsId) {{
                breadcrumb.innerHTML = '<span style="color:#94a3b8;">Sélectionnez un Corps ci-dessus</span>';
                return;
            }}
            
            // Récupérer les noms depuis le contexte
            const corps = N0_CORPS.find(c => c.id === corpsId);
            const corpsName = corps ? corps.name : corpsId;
            
            let html = `<span style="color:#1e293b;font-weight:700;">${{corpsName}}</span>`;
            
            if (organeId) {{
                html += '<span style="color:#cbd5e1;margin:0 8px;">›</span>';
                html += `<span style="color:#5a9ac6;font-weight:600;">${{organeId}}</span>`;
            }}
            
            if (celluleId) {{
                html += '<span style="color:#cbd5e1;margin:0 8px;">›</span>';
                html += `<span style="color:#7aca6a;font-weight:600;">${{celluleId}}</span>`;
            }}
            
            // Indicateur de niveau
            const levelNames = ['Corps', 'Organe', 'Cellule', 'Atome'];
            html += `<span style="margin-left:auto;font-size:12px;color:#94a3b8;background:#f1f5f9;padding:4px 12px;border-radius:12px;">${{levelNames[level] || 'Niveau ' + level}}</span>`;
            
            breadcrumb.innerHTML = html;
        }}
        
        // Navigation via breadcrumb
        function navigateToLevel(targetLevel) {{
            currentNavigation.level = targetLevel;
            if (targetLevel === 0) {{
                currentNavigation.organeId = null;
                currentNavigation.celluleId = null;
            }} else if (targetLevel === 1) {{
                currentNavigation.celluleId = null;
            }}
            updateBreadcrumb();
        }}
        
        // Highlight un élément sur le canvas
        function highlightOnCanvas(itemId) {{
            if (!window.fabricCanvas) return;
            
            const objects = window.fabricCanvas.getObjects();
            objects.forEach(obj => {{
                if (obj.data && obj.data.id === itemId) {{
                    // Animation de highlight
                    obj.set({{ strokeWidth: 4, stroke: '#5a9ac6' }});
                    window.fabricCanvas.renderAll();
                    
                    setTimeout(() => {{
                        obj.set({{ strokeWidth: 2, stroke: '#7aca6a' }});
                        window.fabricCanvas.renderAll();
                    }}, 1000);
                }}
            }});
        }}
        
        // Double-clic drill-down sur le canvas
        function setupDrillDown() {{
            if (!window.fabricCanvas) return;
            
            window.fabricCanvas.on('mouse:dblclick', (e) => {{
                const obj = e.target;
                if (!obj || !obj.data) return;
                
                const {{ type, id }} = obj.data;
                
                if (type === 'corps') {{
                    // Zoom vers vue Organe
                    currentNavigation = {{ 
                        corpsId: id, 
                        organeId: null, 
                        celluleId: null, 
                        level: 1 
                    }};
                    renderSidebarAccordion(id);
                    updateBreadcrumb();
                    zoomIn();
                }} else if (type === 'organe') {{
                    // Zoom vers vue Cellule
                    currentNavigation.organeId = id;
                    currentNavigation.celluleId = null;
                    currentNavigation.level = 2;
                    updateBreadcrumb();
                    zoomIn();
                }} else if (type === 'cellule') {{
                    // Zoom vers vue Atome
                    currentNavigation.celluleId = id;
                    currentNavigation.level = 3;
                    updateBreadcrumb();
                    zoomIn();
                }}
            }});
        }}
        
        // ============================================================
        // RENDU CORPS EN DIMENSIONS RÉELLES (1440x900 Desktop)
        // ============================================================
        
        function renderCorpsOnCanvas(canvas, corpsId, dropX, dropY) {{
            const blueprint = loadFromLocalStorage(`blueprint_${{corpsId}}`) || generateBlueprint(corpsId, 'default');
            const corps = N0_CORPS.find(c => c.id === corpsId);
            const corpsName = corps ? corps.name : corpsId;
            
            // Dimensions réelles desktop
            const REAL_WIDTH = 1440;
            const REAL_HEIGHT = 900;
            
            // Échelle pour tenir dans la vue (25% de la taille réelle)
            const scale = 0.25;
            const displayWidth = REAL_WIDTH * scale;
            const displayHeight = REAL_HEIGHT * scale;
            
            // Position centrée sur le drop
            const left = (dropX || 200) - displayWidth / 2;
            const top = (dropY || 200) - displayHeight / 2;
            
            // Créer le groupe principal du Corps
            const corpsObjects = [];
            
            // 1. Cadre principal
            const frame = new fabric.Rect({{
                left: left,
                top: top,
                width: displayWidth,
                height: displayHeight,
                fill: '#ffffff',
                stroke: '#7aca6a',
                strokeWidth: 3,
                rx: 4,
                shadow: {{ color: 'rgba(0,0,0,0.15)', blur: 20, offsetX: 0, offsetY: 4 }}
            }});
            frame.data = {{ type: 'corps', id: corpsId, role: 'frame' }};
            corpsObjects.push(frame);
            
            // 2. Header (80px réel)
            const headerHeight = 80 * scale;
            const header = new fabric.Rect({{
                left: left,
                top: top,
                width: displayWidth,
                height: headerHeight,
                fill: '#f8fafc',
                stroke: '#e2e8f0',
                strokeWidth: 1
            }});
            header.data = {{ type: 'corps', id: corpsId, role: 'header' }};
            corpsObjects.push(header);
            
            // 3. Titre
            const titleText = new fabric.Text(corpsName, {{
                left: left + 15,
                top: top + headerHeight / 2,
                fontSize: 12,
                fontWeight: 'bold',
                fill: '#1e293b',
                originY: 'center'
            }});
            titleText.data = {{ type: 'corps', id: corpsId, role: 'title' }};
            corpsObjects.push(titleText);
            
            // 4. Badge dimensions
            const dimText = new fabric.Text(`${{REAL_WIDTH}}×${{REAL_HEIGHT}}`, {{
                left: left + displayWidth - 10,
                top: top + headerHeight / 2,
                fontSize: 9,
                fill: '#64748b',
                originX: 'right',
                originY: 'center'
            }});
            dimText.data = {{ type: 'corps', id: corpsId, role: 'dimensions' }};
            corpsObjects.push(dimText);
            
            // 5. Zones selon structure Sullivan
            const structure = blueprint.structure || CORP_STRUCTURES['default'];
            const zones = structure.zones || [];
            
            const zoneColors = {{
                'header': '#f1f5f9', 'sidebar': '#f8fafc', 'content': '#ffffff',
                'stats': '#f0fdf4', 'table': '#ffffff', 'grid': '#fafafa', 'preview-area': '#f8fafc'
            }};
            
            zones.forEach((zone, index) => {{
                if (zone.type === 'header') return; // Déjà rendu
                
                const zoneLeft = left + (zone.x * scale);
                const zoneTop = top + (zone.y * scale) + (zone.y > 0 ? headerHeight : 0);
                const zoneWidth = Math.max(zone.w * scale, 30);
                const zoneHeight = Math.max(zone.h * scale - (zone.y > 0 ? 0 : headerHeight), 20);
                
                const zoneRect = new fabric.Rect({{
                    left: zoneLeft,
                    top: zoneTop,
                    width: zoneWidth,
                    height: zoneHeight,
                    fill: zoneColors[zone.type] || '#f8fafc',
                    stroke: '#e2e8f0',
                    strokeWidth: 1,
                    strokeDashArray: [3, 3]
                }});
                zoneRect.data = {{ type: 'zone', id: `${{corpsId}}_${{zone.type}}_${{index}}`, corpsId, zoneType: zone.type }};
                corpsObjects.push(zoneRect);
                
                const zoneLabel = new fabric.Text(zone.type, {{
                    left: zoneLeft + 5,
                    top: zoneTop + 5,
                    fontSize: 8,
                    fill: '#94a3b8'
                }});
                zoneLabel.data = {{ type: 'zone-label', parentZone: `${{corpsId}}_${{zone.type}}_${{index}}` }};
                corpsObjects.push(zoneLabel);
            }});
            
            // Ajouter au canvas
            corpsObjects.forEach(obj => canvas.add(obj));
            
            // Groupe pour manipulation
            const group = new fabric.Group(corpsObjects, {{ canvas }});
            canvas.setActiveObject(group);
            canvas.renderAll();
            
            saveCanvasState();
            updateObjectCount();
            
            currentNavigation.corpsId = corpsId;
            currentNavigation.level = 0;
            renderSidebarAccordion(corpsId);
            updateBreadcrumb();
        }}
        
        // ============================================================
        // OPTION A: Polissage - Zoom Controls + Resize + Delete + Auto-save
        // ============================================================
        
        // Zoom Controls
        function zoomIn() {{
            if (!window.fabricCanvas) return;
            const currentZoom = window.fabricCanvas.getZoom();
            const newZoom = Math.min(3, currentZoom * 1.2);
            window.fabricCanvas.setZoom(newZoom);
            window.fabricCanvas.renderAll();
            updateZoomDisplay();
        }}
        
        function zoomOut() {{
            if (!window.fabricCanvas) return;
            const currentZoom = window.fabricCanvas.getZoom();
            const newZoom = Math.max(0.5, currentZoom / 1.2);
            window.fabricCanvas.setZoom(newZoom);
            window.fabricCanvas.renderAll();
            updateZoomDisplay();
        }}
        
        function resetZoom() {{
            if (!window.fabricCanvas) return;
            window.fabricCanvas.setZoom(1);
            window.fabricCanvas.renderAll();
            updateZoomDisplay();
        }}
        
        function updateZoomDisplay() {{
            if (!window.fabricCanvas) return;
            const zoom = Math.round(window.fabricCanvas.getZoom() * 100);
            const display = document.getElementById('zoom-level');
            if (display) display.textContent = zoom + '%';
        }}
        
        // Vider le canvas
        function clearCanvas() {{
            if (!window.fabricCanvas) return;
            if (confirm('Vider tous les éléments du canvas ?')) {{
                window.fabricCanvas.clear();
                window.fabricCanvas.renderAll();
                // Vider aussi la sauvegarde
                localStorage.removeItem('homeos_canvas_backup');
                updateObjectCount();
                console.log('Canvas vidé et sauvegarde effacée');
            }}
        }}
        
        // Restaurer la session précédente
        function restoreSession() {{
            if (!window.fabricCanvas) {{
                alert('Canvas non initialisé');
                return;
            }}
            const saved = localStorage.getItem('homeos_canvas_backup');
            if (!saved) {{
                alert('Aucune session précédente trouvée');
                return;
            }}
            if (confirm('Restaurer la session précédente ? Cela remplacera le contenu actuel.')) {{
                loadCanvasState();
            }}
        }}
        
        // Suppression objet (touche Delete/Suppr) - Fonction globale
        window.deleteSelectedObject = function() {{
            if (!window.fabricCanvas) return false;
            const activeObject = window.fabricCanvas.getActiveObject();
            if (activeObject) {{
                console.log('Suppression:', activeObject.type);
                // Si c'est un groupe (sélection multiple)
                if (activeObject.type === 'activeSelection') {{
                    const objects = activeObject.getObjects();
                    objects.forEach((obj) => {{
                        window.fabricCanvas.remove(obj);
                    }});
                }} else {{
                    window.fabricCanvas.remove(activeObject);
                }}
                window.fabricCanvas.discardActiveObject();
                window.fabricCanvas.renderAll();
                updateObjectCount();
                saveCanvasState();
                return true;
            }}
            return false;
        }};
        
        // Écouteur clavier global
        document.addEventListener('keydown', function(e) {{
            const key = e.key || e.code;
            if ((key === 'Delete' || key === 'Backspace' || key === 'Del') && !e.repeat) {{
                // Vérifier si on est dans un input
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable) {{
                    return;
                }}
                e.preventDefault();
                e.stopPropagation();
                window.deleteSelectedObject();
            }}
        }}, true);
        
        // Sauvegarde auto dans localStorage
        const CANVAS_STORAGE_KEY = 'homeos_canvas_backup';
        
        function saveCanvasState() {{
            if (!window.fabricCanvas) return;
            try {{
                const canvasData = window.fabricCanvas.toJSON(['data']);
                localStorage.setItem(CANVAS_STORAGE_KEY, JSON.stringify({{
                    timestamp: new Date().toISOString(),
                    canvas: canvasData,
                    navigation: currentNavigation
                }}));
            }} catch(e) {{
                console.warn('Sauvegarde impossible:', e);
            }}
        }}
        
        function loadCanvasState() {{
            try {{
                const saved = localStorage.getItem(CANVAS_STORAGE_KEY);
                if (saved && window.fabricCanvas) {{
                    const data = JSON.parse(saved);
                    window.fabricCanvas.loadFromJSON(data.canvas, () => {{
                        window.fabricCanvas.renderAll();
                        updateObjectCount();
                        console.log('Canvas restauré:', data.timestamp);
                    }});
                    if (data.navigation) {{
                        currentNavigation = data.navigation;
                        updateBreadcrumb();
                    }}
                }}
            }} catch(e) {{
                console.warn('Restauration impossible:', e);
            }}
        }}
        
        // Auto-save toutes les 10 secondes
        setInterval(saveCanvasState, 10000);
        
        // Save avant fermeture
        window.addEventListener('beforeunload', saveCanvasState);
        
        // Charger au démarrage de l'éditeur
        document.addEventListener('DOMContentLoaded', () => {{
            // La restauration se fait dans initFabricEditor après création du canvas
        }});
        
        // Zoom via molette (Ctrl+wheel)
        document.addEventListener('wheel', (e) => {{
            if (e.ctrlKey && window.fabricCanvas) {{
                e.preventDefault();
                if (e.deltaY < 0) zoomIn();
                else zoomOut();
            }}
        }}, {{ passive: false }});
        
        // ============================================================
        // PHASE 4: Brainstorm Modal & Export JSON
        // ============================================================
        
        let brainstormTargetId = null;
        
        // Affiche le modal Brainstorm
        function showBrainstormModal(corpsId) {{
            brainstormTargetId = corpsId;
            document.getElementById('brainstorm-target-name').textContent = corpsId;
            document.getElementById('brainstorm-modal').style.display = 'flex';
        }}
        
        // Ferme le modal Brainstorm
        function closeBrainstormModal() {{
            document.getElementById('brainstorm-modal').style.display = 'none';
            brainstormTargetId = null;
        }}
        
        // Valide le brainstorm et met à jour le blueprint
        function validateBrainstorm() {{
            if (!brainstormTargetId) return;
            
            const width = parseInt(document.getElementById('brainstorm-width').value) || 1440;
            const height = parseInt(document.getElementById('brainstorm-height').value) || 900;
            
            // Récupérer et mettre à jour le blueprint
            const blueprint = loadFromLocalStorage(`blueprint_${{brainstormTargetId}}`);
            if (blueprint) {{
                blueprint.width = width;
                blueprint.height = height;
                blueprint.status = 'ready';
                blueprint.updated_at = new Date().toISOString();
                saveToLocalStorage(`blueprint_${{brainstormTargetId}}`, blueprint);
                console.log('Blueprint mis à jour:', blueprint);
            }}
            
            closeBrainstormModal();
            
            // Mettre à jour le compteur d'objets
            updateObjectCount();
        }}
        
        // Exporte l'état du canvas en JSON
        function exportToJSON() {{
            if (!window.fabricCanvas) {{
                alert("Le canvas n'est pas initialisé");
                return;
            }}
            
            const objects = window.fabricCanvas.getObjects();
            const usedBlueprintIds = [...new Set(objects
                .filter(obj => obj.data && obj.data.id)
                .map(obj => obj.data.id))];
            
            const exportData = {{
                version: '1.0',
                exported_at: new Date().toISOString(),
                project: 'Homeos/Sullivan',
                canvas_state: window.fabricCanvas.toJSON(['data']),
                blueprints_used: usedBlueprintIds.map(id => {{
                    const bp = loadFromLocalStorage(`blueprint_${{id}}`);
                    return {{ id, ...bp }};
                }}),
                fabric_objects: objects.map(obj => ({{
                    type: obj.type,
                    position: {{ x: obj.left, y: obj.top }},
                    size: {{ width: obj.width, height: obj.height }},
                    data: obj.data || {{}},
                    fill: obj.fill,
                    stroke: obj.stroke
                }})),
                navigation_state: currentNavigation
            }};
            
            // Téléchargement
            const blob = new Blob([JSON.stringify(exportData, null, 2)], {{ type: 'application/json' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `homeos-export-${{Date.now()}}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            console.log('Export JSON:', exportData);
        }}
        
        // Met à jour le compteur d'objets
        function updateObjectCount() {{
            if (!window.fabricCanvas) return;
            const count = window.fabricCanvas.getObjects().length / 2; // Diviser par 2 car chaque Corps = rect + texte
            document.getElementById('canvas-objects-count').textContent = `${{Math.floor(count)}} Corps`;
        }}
        
        // Ferme le modal si clic en dehors
        document.getElementById('brainstorm-modal').addEventListener('click', (e) => {{
            if (e.target.id === 'brainstorm-modal') {{
                closeBrainstormModal();
            }}
        }});
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
    genome = load_genome()
    print(f"🚀 Serveur v2.1 démarré : http://localhost:{PORT}")
    print(f"   Layout : Enrichi (ombres, gradients, style Figma)")
    print(f"   Wireframes : 10 FRD V2 enrichis + classiques")
    
    with HTTPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()
