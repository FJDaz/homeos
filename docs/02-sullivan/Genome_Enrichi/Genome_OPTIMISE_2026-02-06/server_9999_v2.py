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
        "GET": "#8aca7f",
        "POST": "#6a8aa6", 
        "PUT": "#d4ab7a",
        "DELETE": "#c58383"
    }
    color = method_colors.get(method, "#64748b")
    nom_clair = name.replace("Comp ", "").replace("Component ", "")
    
    # === WIREFRAMES ENRICHIS ===
    
    # STATUS - LEDs avec ombres et gradients
    if visual_hint == "status":
        wireframe = '''<div style="background:linear-gradient(145deg,#ffffff 0%,#f8fafc 100%);border:1px solid #e2e8f0;border-radius:12px;padding:12px;box-shadow:0 1px 3px rgba(0,0,0,0.05),0 1px 2px rgba(0,0,0,0.03);">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
                <div style="width:8px;height:8px;background:linear-gradient(135deg,#8aca7f 0%,#7aba6f 100%);border-radius:50%;box-shadow:0 0 0 2px rgba(140,198,63,0.2);"></div>
                <span style="font-size:11px;font-weight:600;color:#1e293b;letter-spacing:-0.2px;">🏥 Santé du projet</span>
            </div>
            <div style="display:flex;justify-content:center;gap:16px;margin:16px 0;">
                <div style="text-align:center;">
                    <div style="width:16px;height:16px;background:linear-gradient(135deg,#8aca7f 0%,#7aba6f 100%);border-radius:50%;margin:0 auto 6px;box-shadow:0 2px 4px rgba(140,198,63,0.3),inset 0 -2px 4px rgba(0,0,0,0.1);"></div>
                    <span style="font-size:9px;color:#64748b;font-weight:500;">OK</span>
                </div>
                <div style="text-align:center;">
                    <div style="width:16px;height:16px;background:linear-gradient(135deg,#8aca7f 0%,#7aba6f 100%);border-radius:50%;margin:0 auto 6px;box-shadow:0 2px 4px rgba(140,198,63,0.3),inset 0 -2px 4px rgba(0,0,0,0.1);"></div>
                    <span style="font-size:9px;color:#64748b;font-weight:500;">OK</span>
                </div>
                <div style="text-align:center;">
                    <div style="width:16px;height:16px;background:linear-gradient(135deg,#8aca7f 0%,#7aba6f 100%);border-radius:50%;margin:0 auto 6px;box-shadow:0 2px 4px rgba(140,198,63,0.3),inset 0 -2px 4px rgba(0,0,0,0.1);"></div>
                    <span style="font-size:9px;color:#64748b;font-weight:500;">OK</span>
                </div>
                <div style="text-align:center;">
                    <div style="width:16px;height:16px;background:linear-gradient(135deg,#94a3b8 0%,#64748b 100%);border-radius:50%;margin:0 auto 6px;box-shadow:inset 0 2px 4px rgba(0,0,0,0.1);"></div>
                    <span style="font-size:9px;color:#64748b;font-weight:500;">?</span>
                </div>
            </div>
            <div style="background:linear-gradient(90deg,rgba(140,198,63,0.1) 0%,rgba(140,198,63,0.05) 100%);border-radius:6px;padding:8px;text-align:center;">
                <span style="font-size:10px;color:#8aca7f;font-weight:600;">✅ Fonctions vitales présentes</span>
            </div>
        </div>'''
    
    # ZOOM-CONTROLS - Navigation riche
    elif visual_hint == "zoom-controls":
        wireframe = '''<div style="background:linear-gradient(145deg,#ffffff 0%,#f8fafc 100%);border:1px solid #e2e8f0;border-radius:12px;padding:12px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
                <span style="font-size:11px;font-weight:600;color:#1e293b;letter-spacing:-0.2px;">🔭 Navigation</span>
                <span style="margin-left:auto;font-size:9px;color:#94a3b8;background:#f1f5f9;padding:2px 6px;border-radius:4px;">N2</span>
            </div>
            <div style="display:flex;gap:8px;margin-bottom:12px;">
                <span style="flex:1;padding:10px;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border:1px solid #cbd5e1;border-radius:8px;text-align:center;font-size:10px;color:#475569;font-weight:500;box-shadow:0 1px 2px rgba(0,0,0,0.05);">← Out</span>
                <span style="flex:1;padding:10px;background:linear-gradient(145deg,#6a8aa6 0%,#5a7396 100%);border:1px solid #4d6280;border-radius:8px;text-align:center;font-size:10px;color:white;font-weight:600;box-shadow:0 2px 4px rgba(59,130,246,0.3);">🔍 Corps ▼</span>
                <span style="flex:1;padding:10px;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border:1px solid #cbd5e1;border-radius:8px;text-align:center;font-size:10px;color:#475569;font-weight:500;box-shadow:0 1px 2px rgba(0,0,0,0.05);">In →</span>
            </div>
            <div style="background:#f8fafc;border-radius:6px;padding:8px;display:flex;align-items:center;justify-content:center;gap:6px;">
                <span style="color:#8aca7f;font-weight:700;font-size:10px;background:rgba(140,198,63,0.1);padding:2px 8px;border-radius:4px;">◉ Corps</span>
                <span style="color:#94a3b8;font-size:9px;">›</span>
                <span style="color:#64748b;font-size:10px;font-weight:500;">○ Organe</span>
                <span style="color:#94a3b8;font-size:9px;">›</span>
                <span style="color:#64748b;font-size:10px;font-weight:500;">○ Atome</span>
            </div>
        </div>'''
    
    # STENCIL-CARD - Fiche pouvoir enrichie
    elif visual_hint == "stencil-card":
        wireframe = '''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px solid #e2e8f0;border-radius:12px;padding:12px;box-shadow:0 1px 3px rgba(0,0,0,0.05),0 1px 2px rgba(0,0,0,0.03);position:relative;overflow:hidden;">
            <div style="position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#8aca7f 0%,#aac87a 100%);"></div>
            <div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:12px;">
                <div style="width:40px;height:40px;background:linear-gradient(135deg,#f5f0d0 0%,#f0dcb8 100%);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px;box-shadow:0 2px 4px rgba(251,191,36,0.2);">💡</div>
                <div style="flex:1;">
                    <div style="font-size:13px;font-weight:700;color:#1e293b;letter-spacing:-0.3px;margin-bottom:4px;">Veille du Système</div>
                    <div style="font-size:11px;color:#64748b;line-height:1.5;">Voir l'état de santé du projet en un coup d'œil</div>
                </div>
            </div>
            <div style="display:flex;gap:8px;margin-top:16px;padding-top:12px;border-top:1px solid #f1f5f9;">
                <span style="flex:1;padding:8px 12px;background:linear-gradient(145deg,#8aca7f 0%,#7aba6f 100%);border-radius:8px;text-align:center;font-size:11px;color:white;font-weight:600;box-shadow:0 2px 4px rgba(140,198,63,0.3);text-shadow:0 1px 2px rgba(0,0,0,0.1);">🟢 Garder</span>
                <span style="flex:1;padding:8px 12px;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border:1px solid #cbd5e1;border-radius:8px;text-align:center;font-size:11px;color:#64748b;font-weight:500;">⚪ Réserve</span>
            </div>
        </div>'''
    
    # DETAIL-CARD - Fiche technique Figma-like
    elif visual_hint == "detail-card":
        wireframe = '''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px solid #e2e8f0;border-radius:12px;padding:12px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;padding-bottom:12px;border-bottom:1px solid #f1f5f9;">
                <span style="font-size:10px;font-weight:700;color:#6a8aa6;background:rgba(59,130,246,0.1);padding:3px 8px;border-radius:4px;text-transform:uppercase;letter-spacing:0.5px;">GET</span>
                <span style="font-size:11px;font-weight:600;color:#1e293b;font-family:'SF Mono',monospace;letter-spacing:-0.3px;">/api/health</span>
            </div>
            <div style="background:#f8fafc;border-radius:8px;padding:12px;margin-bottom:12px;">
                <div style="font-size:10px;color:#64748b;margin-bottom:6px;font-weight:500;">Retour JSON</div>
                <div style="font-size:9px;color:#94a3b8;font-family:monospace;background:#1e293b;padding:8px;border-radius:6px;line-height:1.6;">
                    <span style="color:#8aca7f;">{</span><br>
                    &nbsp;&nbsp;<span style="color:#a8b8d8;">"status"</span><span style="color:#e2e8f0;">:</span> <span style="color:#c8d8e8;">"ok"</span>,<br>
                    &nbsp;&nbsp;<span style="color:#a8b8d8;">"uptime"</span><span style="color:#e2e8f0;">:</span> <span style="color:#e8d8aa;">3600</span><br>
                    <span style="color:#8aca7f;">}</span>
                </div>
            </div>
            <div style="display:flex;gap:8px;">
                <span style="flex:1;padding:8px;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border:1px solid #cbd5e1;border-radius:8px;text-align:center;font-size:10px;color:#475569;font-weight:600;">📋 Copier</span>
                <span style="flex:1;padding:8px;background:linear-gradient(145deg,#6a8aa6 0%,#5a7396 100%);border-radius:8px;text-align:center;font-size:10px;color:white;font-weight:600;box-shadow:0 2px 4px rgba(59,130,246,0.3);">↗️ Tester</span>
            </div>
        </div>'''
    
    # COLOR-PALETTE - Style détecté enrichi
    elif visual_hint == "color-palette":
        wireframe = '''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px solid #e2e8f0;border-radius:12px;padding:12px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;">
                <span style="font-size:12px;font-weight:700;color:#1e293b;letter-spacing:-0.2px;">🎨 Style détecté</span>
                <span style="font-size:9px;color:#64748b;background:#f1f5f9;padding:2px 8px;border-radius:12px;">3.2s</span>
            </div>
            <div style="display:flex;gap:8px;margin-bottom:14px;">
                <div style="flex:1;aspect-ratio:1;background:linear-gradient(145deg,#6a8aa6 0%,#5a7396 100%);border-radius:10px;box-shadow:0 2px 4px rgba(59,130,246,0.3),inset 0 1px 0 rgba(255,255,255,0.2);position:relative;overflow:hidden;">
                    <div style="position:absolute;bottom:0;left:0;right:0;height:40%;background:rgba(0,0,0,0.1);"></div>
                </div>
                <div style="flex:1;aspect-ratio:1;background:linear-gradient(145deg,#8aca7f 0%,#7aba6f 100%);border-radius:10px;box-shadow:0 2px 4px rgba(140,198,63,0.3),inset 0 1px 0 rgba(255,255,255,0.2);"></div>
                <div style="flex:1;aspect-ratio:1;background:linear-gradient(145deg,#d4ab7a 0%,#b68c6a 100%);border-radius:10px;box-shadow:0 2px 4px rgba(245,158,11,0.3),inset 0 1px 0 rgba(255,255,255,0.2);"></div>
                <div style="flex:1;aspect-ratio:1;background:linear-gradient(145deg,#1e293b 0%,#0f172a 100%);border-radius:10px;box-shadow:0 2px 4px rgba(30,41,59,0.3),inset 0 1px 0 rgba(255,255,255,0.1);"></div>
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:6px;">
                <span style="padding:4px 10px;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border:1px solid #cbd5e1;border-radius:20px;font-size:9px;color:#475569;font-weight:600;">Rounded: 8px</span>
                <span style="padding:4px 10px;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border:1px solid #cbd5e1;border-radius:20px;font-size:9px;color:#475569;font-weight:600;font-family:system-ui;">Inter</span>
                <span style="padding:4px 10px;background:linear-gradient(145deg,#f5f0d0 0%,#f0dcb8 100%);border:1px solid #e8d8aa;border-radius:20px;font-size:9px;color:#92400e;font-weight:600;">Spacing: 16px</span>
            </div>
        </div>'''
    
    # CHOICE-CARD - Sélection style
    elif visual_hint == "choice-card":
        wireframe = '''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px solid #e2e8f0;border-radius:12px;padding:12px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="font-size:12px;font-weight:700;color:#1e293b;letter-spacing:-0.2px;margin-bottom:14px;">🎨 Choisissez votre style</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px;">
                <div style="border:1px solid #e2e8f0;border-radius:10px;padding:12px;text-align:center;background:linear-gradient(145deg,#ffffff 0%,#f8fafc 100%);transition:all 0.2s;cursor:pointer;">
                    <div style="width:24px;height:24px;margin:0 auto 8px;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;">○</div>
                    <span style="font-size:10px;color:#475569;font-weight:600;">Minimal</span>
                </div>
                <div style="border:1px solid #8aca7f;border-radius:10px;padding:12px;text-align:center;background:linear-gradient(145deg,#f5faf7 0%,#e8f0ec 100%);box-shadow:0 0 0 1px rgba(140,198,63,0.2),0 2px 4px rgba(140,198,63,0.1);">
                    <div style="width:24px;height:24px;margin:0 auto 8px;background:linear-gradient(145deg,#8aca7f 0%,#7aba6f 100%);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;color:white;box-shadow:0 2px 4px rgba(140,198,63,0.3);">●</div>
                    <span style="font-size:10px;color:#5a7b64;font-weight:700;">Brutaliste</span>
                </div>
                <div style="border:1px solid #e2e8f0;border-radius:10px;padding:12px;text-align:center;background:linear-gradient(145deg,#ffffff 0%,#f8fafc 100%);">
                    <div style="width:24px;height:24px;margin:0 auto 8px;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;">○</div>
                    <span style="font-size:10px;color:#475569;font-weight:600;">Moderne</span>
                </div>
                <div style="border:1px solid #e2e8f0;border-radius:10px;padding:12px;text-align:center;background:linear-gradient(145deg,#ffffff 0%,#f8fafc 100%);">
                    <div style="width:24px;height:24px;margin:0 auto 8px;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;">○</div>
                    <span style="font-size:10px;color:#475569;font-weight:600;">Corporate</span>
                </div>
            </div>
            <div style="display:flex;justify-content:flex-end;">
                <span style="padding:8px 16px;background:linear-gradient(145deg,#6a8aa6 0%,#5a7396 100%);border-radius:8px;font-size:11px;color:white;font-weight:600;box-shadow:0 2px 4px rgba(59,130,246,0.3);">Continuer →</span>
            </div>
        </div>'''
    
    # LAUNCH-BUTTON - Fusée enrichie
    elif visual_hint == "launch-button":
        wireframe = '''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px solid #e2e8f0;border-radius:12px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,0.05);text-align:center;">
            <div style="width:48px;height:48px;margin:0 auto 14px;background:linear-gradient(145deg,#f5f0d0 0%,#f0dcb8 100%);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:24px;box-shadow:0 4px 8px rgba(251,191,36,0.3),inset 0 1px 0 rgba(255,255,255,0.5);">🚀</div>
            <div style="font-size:13px;font-weight:700;color:#1e293b;margin-bottom:6px;letter-spacing:-0.2px;">Génération du code</div>
            <div style="font-size:10px;color:#64748b;margin-bottom:16px;">Prêt à distiller votre projet</div>
            <div style="padding:12px 24px;background:linear-gradient(145deg,#8aca7f 0%,#7aba6f 100%);border-radius:10px;font-size:12px;color:white;font-weight:700;box-shadow:0 4px 8px rgba(140,198,63,0.3),0 2px 4px rgba(140,198,63,0.2),inset 0 1px 0 rgba(255,255,255,0.2);text-shadow:0 1px 2px rgba(0,0,0,0.1);">🚀 Lancer la distillation</div>
        </div>'''
    
    # APPLY-CHANGES - Sauvegarder/Annuler
    elif visual_hint == "apply-changes":
        wireframe = '''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px solid #e2e8f0;border-radius:12px;padding:12px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:14px;padding-bottom:14px;border-bottom:1px solid #f1f5f9;">
                <div style="width:32px;height:32px;background:linear-gradient(145deg,#f5f0d0 0%,#f0dcb8 100%);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;">💾</div>
                <div>
                    <div style="font-size:12px;font-weight:700;color:#1e293b;letter-spacing:-0.2px;">Sauvegarder les changements</div>
                    <div style="font-size:10px;color:#64748b;">3 modifications en attente</div>
                </div>
            </div>
            <div style="display:flex;gap:10px;">
                <span style="flex:1;padding:10px;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border:1px solid #cbd5e1;border-radius:8px;text-align:center;font-size:11px;color:#475569;font-weight:600;transition:all 0.2s;">↩️ Annuler</span>
                <span style="flex:1;padding:10px;background:linear-gradient(145deg,#8aca7f 0%,#7aba6f 100%);border-radius:8px;text-align:center;font-size:11px;color:white;font-weight:700;box-shadow:0 2px 4px rgba(140,198,63,0.3);text-shadow:0 1px 2px rgba(0,0,0,0.1);">💾 Appliquer</span>
            </div>
        </div>'''
    
    # TABLE - Tableau enrichi
    elif visual_hint == "table":
        wireframe = f'''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px solid #e2e8f0;border-radius:12px;padding:12px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;padding-bottom:14px;border-bottom:1px solid #f1f5f9;">
                <div style="width:32px;height:32px;background:linear-gradient(145deg,{color} 0%,{color}dd 100%);border-radius:8px;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                    <span style="color:white;font-size:12px;font-weight:800;text-shadow:0 1px 2px rgba(0,0,0,0.2);">{method[:1]}</span>
                </div>
                <div style="flex:1;">
                    <div style="font-size:12px;font-weight:700;color:#1e293b;letter-spacing:-0.2px;">{nom_clair}</div>
                    <div style="font-size:10px;color:#64748b;font-family:monospace;">{endpoint}</div>
                </div>
                <span style="padding:3px 8px;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border-radius:4px;font-size:9px;color:#475569;font-weight:700;text-transform:uppercase;">{method}</span>
            </div>
            <div style="background:#f8fafc;border-radius:8px;padding:12px;">
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
        wireframe = f'''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px solid #e2e8f0;border-radius:12px;padding:12px;box-shadow:0 1px 3px rgba(0,0,0,0.05);position:relative;overflow:hidden;">
            <div style="position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,{color} 0%,{color}88 100%);"></div>
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
                <div style="width:40px;height:40px;background:linear-gradient(145deg,{color} 0%,{color}dd 100%);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;box-shadow:0 2px 4px rgba(0,0,0,0.1);">◆</div>
                <div style="flex:1;">
                    <div style="font-size:13px;font-weight:700;color:#1e293b;letter-spacing:-0.3px;">{nom_clair}</div>
                    <div style="font-size:10px;color:#64748b;">{method} {endpoint}</div>
                </div>
            </div>
            <div style="height:6px;background:linear-gradient(90deg,#f1f5f9 0%,#e2e8f0 100%);border-radius:3px;position:relative;overflow:hidden;">
                <div style="position:absolute;top:0;left:0;width:60%;height:100%;background:linear-gradient(90deg,{color}44 0%,{color} 100%);border-radius:3px;"></div>
            </div>
        </div>'''
    
    # FORM - Formulaire enrichi
    elif visual_hint == "form":
        wireframe = '''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px solid #e2e8f0;border-radius:12px;padding:12px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid #f1f5f9;">
                <span style="font-size:12px;font-weight:700;color:#1e293b;letter-spacing:-0.2px;">Formulaire</span>
                <span style="margin-left:auto;font-size:9px;color:#94a3b8;">2 champs requis</span>
            </div>
            <div style="margin-bottom:14px;">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
                    <span style="font-size:10px;font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:0.3px;">Nom du projet</span>
                    <span style="font-size:9px;color:#c58383;">*</span>
                </div>
                <div style="height:36px;border:1px solid #cbd5e1;border-radius:8px;background:linear-gradient(145deg,#ffffff 0%,#f8fafc 100%);box-shadow:inset 0 1px 2px rgba(0,0,0,0.05);"></div>
            </div>
            <div style="margin-bottom:16px;">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
                    <span style="font-size:10px;font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:0.3px;">Description</span>
                </div>
                <div style="height:36px;border:1px solid #cbd5e1;border-radius:8px;background:linear-gradient(145deg,#ffffff 0%,#f8fafc 100%);box-shadow:inset 0 1px 2px rgba(0,0,0,0.05);"></div>
            </div>
            <div style="display:flex;gap:10px;padding-top:12px;border-top:1px solid #f1f5f9;">
                <span style="flex:1;padding:10px;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border:1px solid #cbd5e1;border-radius:8px;text-align:center;font-size:11px;color:#475569;font-weight:600;">Annuler</span>
                <span style="flex:1;padding:10px;background:linear-gradient(145deg,#8aca7f 0%,#7aba6f 100%);border-radius:8px;text-align:center;font-size:11px;color:white;font-weight:700;box-shadow:0 2px 4px rgba(140,198,63,0.3);">Valider</span>
            </div>
        </div>'''
    
    # DASHBOARD - Dashboard enrichi
    elif visual_hint == "dashboard":
        wireframe = '''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px solid #e2e8f0;border-radius:12px;padding:12px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
                <span style="font-size:12px;font-weight:700;color:#1e293b;letter-spacing:-0.2px;">📊 Dashboard</span>
                <span style="font-size:9px;color:#64748b;background:#f1f5f9;padding:3px 8px;border-radius:12px;">Temps réel</span>
            </div>
            <div style="display:flex;gap:12px;margin-bottom:16px;">
                <div style="flex:1;text-align:center;padding:12px;background:linear-gradient(145deg,#f5faf7 0%,#e8f0ec 100%);border:1px solid #c8dcd5;border-radius:10px;">
                    <div style="font-size:22px;font-weight:800;color:#5a7b64;margin-bottom:2px;letter-spacing:-0.5px;">29</div>
                    <div style="font-size:9px;color:#7ab88a;font-weight:600;text-transform:uppercase;letter-spacing:0.3px;">Composants</div>
                </div>
                <div style="flex:1;text-align:center;padding:12px;background:linear-gradient(145deg,#f0f4f8 0%,#e0e6f0 100%);border:1px solid #c8d0e0;border-radius:10px;">
                    <div style="font-size:22px;font-weight:800;color:#5a6a7e;margin-bottom:2px;letter-spacing:-0.5px;">9</div>
                    <div style="font-size:9px;color:#6a8aa6;font-weight:600;text-transform:uppercase;letter-spacing:0.3px;">Phases</div>
                </div>
            </div>
            <div style="background:#f8fafc;border-radius:8px;padding:12px;">
                <div style="display:flex;align-items:flex-end;gap:4px;height:50px;padding:0 4px;">
                    <div style="flex:1;height:40%;background:linear-gradient(180deg,#8aca7f 0%,#7aba6f 100%);border-radius:3px 3px 0 0;box-shadow:0 -2px 4px rgba(140,198,63,0.2);"></div>
                    <div style="flex:1;height:65%;background:linear-gradient(180deg,#8aca7f 0%,#7aba6f 100%);border-radius:3px 3px 0 0;box-shadow:0 -2px 4px rgba(140,198,63,0.2);"></div>
                    <div style="flex:1;height:45%;background:linear-gradient(180deg,#6a8aa6 0%,#5a7396 100%);border-radius:3px 3px 0 0;box-shadow:0 -2px 4px rgba(59,130,246,0.2);"></div>
                    <div style="flex:1;height:80%;background:linear-gradient(180deg,#8aca7f 0%,#7aba6f 100%);border-radius:3px 3px 0 0;box-shadow:0 -2px 4px rgba(140,198,63,0.2);"></div>
                    <div style="flex:1;height:55%;background:linear-gradient(180deg,#d4ab7a 0%,#b68c6a 100%);border-radius:3px 3px 0 0;box-shadow:0 -2px 4px rgba(245,158,11,0.2);"></div>
                </div>
            </div>
        </div>'''
    
    # CHAT/BUBBLE - Chat enrichi
    elif visual_hint == "chat/bubble":
        wireframe = '''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px solid #e2e8f0;border-radius:12px;padding:12px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex;gap:10px;margin-bottom:14px;">
                <div style="width:32px;height:32px;background:linear-gradient(145deg,#7a7a9a 0%,#6a6a8a 100%);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;color:white;box-shadow:0 2px 4px rgba(79,70,229,0.3);text-shadow:0 1px 2px rgba(0,0,0,0.2);">S</div>
                <div style="flex:1;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border-radius:12px 12px 12px 4px;padding:12px;box-shadow:0 1px 2px rgba(0,0,0,0.05);">
                    <div style="height:5px;background:#cbd5e1;border-radius:2px;margin-bottom:5px;width:85%;"></div>
                    <div style="height:5px;background:#cbd5e1;border-radius:2px;width:60%;"></div>
                </div>
            </div>
            <div style="display:flex;gap:10px;justify-content:flex-end;">
                <div style="flex:1;max-width:70%;background:linear-gradient(145deg,#7a7a9a 0%,#6a6a8a 100%);border-radius:12px 12px 4px 12px;padding:12px;box-shadow:0 2px 4px rgba(79,70,229,0.2);">
                    <div style="height:5px;background:rgba(255,255,255,0.4);border-radius:2px;margin-bottom:5px;width:80%;"></div>
                    <div style="height:5px;background:rgba(255,255,255,0.4);border-radius:2px;width:50%;"></div>
                </div>
            </div>
            <div style="margin-top:12px;padding-top:12px;border-top:1px solid #f1f5f9;display:flex;gap:8px;">
                <div style="flex:1;height:32px;background:#f1f5f9;border-radius:16px;"></div>
                <div style="width:32px;height:32px;background:linear-gradient(145deg,#7a7a9a 0%,#6a6a8a 100%);border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-size:12px;box-shadow:0 2px 4px rgba(79,70,229,0.3);">➤</div>
            </div>
        </div>'''
    
    # EDITOR - Éditeur enrichi
    elif visual_hint == "editor":
        wireframe = '''<div style="background:linear-gradient(145deg,#1e293b 0%,#0f172a 100%);border:1px solid #334155;border-radius:12px;padding:12px;box-shadow:0 4px 6px rgba(0,0,0,0.1),0 2px 4px rgba(0,0,0,0.1);">
            <div style="display:flex;gap:6px;margin-bottom:12px;padding-bottom:12px;border-bottom:1px solid #334155;">
                <div style="width:10px;height:10px;background:#c58383;border-radius:50%;box-shadow:0 0 0 1px rgba(239,68,68,0.3);"></div>
                <div style="width:10px;height:10px;background:#d4ab7a;border-radius:50%;box-shadow:0 0 0 1px rgba(245,158,11,0.3);"></div>
                <div style="width:10px;height:10px;background:#8aca7f;border-radius:50%;box-shadow:0 0 0 1px rgba(140,198,63,0.3);"></div>
                <div style="flex:1;text-align:center;font-size:9px;color:#64748b;font-family:monospace;">component.py</div>
            </div>
            <div style="font-family:'SF Mono',monospace;font-size:10px;line-height:1.7;">
                <div style="display:flex;gap:8px;"><span style="color:#64748b;width:16px;text-align:right;">1</span><span style="color:#b8c8d0;">def</span> <span style="color:#9abac8;">render</span><span style="color:#e2e8f0;">(</span><span style="color:#d0c0c0;">props</span><span style="color:#e2e8f0;">):</span></div>
                <div style="display:flex;gap:8px;"><span style="color:#64748b;width:16px;text-align:right;">2</span><span style="color:#e2e8f0;">&nbsp;&nbsp;&nbsp;&nbsp;</span><span style="color:#b8c8d0;">return</span> <span style="color:#c8d8e8;">"hello"</span></div>
                <div style="display:flex;gap:8px;"><span style="color:#64748b;width:16px;text-align:right;">3</span></div>
            </div>
        </div>'''
    
    # PREVIEW - Aperçu enrichi
    elif visual_hint == "preview":
        wireframe = '''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px solid #e2e8f0;border-radius:12px;padding:12px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
                <span style="font-size:12px;font-weight:700;color:#1e293b;letter-spacing:-0.2px;">👁️ Aperçu maquette</span>
                <span style="font-size:9px;color:#64748b;background:#f1f5f9;padding:2px 8px;border-radius:12px;">3 zones</span>
            </div>
            <div style="position:relative;background:linear-gradient(135deg,#f8fafc 0%,#e2e8f0 100%);border-radius:8px;height:100px;overflow:hidden;box-shadow:inset 0 2px 4px rgba(0,0,0,0.05);">
                <div style="position:absolute;top:15%;left:10%;width:35%;height:30%;background:linear-gradient(135deg,rgba(59,130,246,0.2) 0%,rgba(37,99,235,0.15) 100%);border:1px dashed #6a8aa6;border-radius:6px;box-shadow:0 0 0 4px rgba(59,130,246,0.1);"></div>
                <div style="position:absolute;top:45%;left:55%;width:30%;height:40%;background:linear-gradient(135deg,rgba(140,198,63,0.2) 0%,rgba(122,179,46,0.15) 100%);border:1px dashed #8aca7f;border-radius:6px;box-shadow:0 0 0 4px rgba(140,198,63,0.1);"></div>
                <div style="position:absolute;bottom:10%;left:5%;width:25%;height:25%;background:linear-gradient(135deg,rgba(236,72,153,0.15) 0%,rgba(219,39,119,0.1) 100%);border:1px dashed #ec4899;border-radius:6px;box-shadow:0 0 0 4px rgba(236,72,153,0.1);"></div>
            </div>
            <div style="display:flex;gap:8px;margin-top:12px;">
                <span style="padding:3px 8px;background:rgba(59,130,246,0.1);border-radius:4px;font-size:8px;color:#6a8aa6;font-weight:600;">Header</span>
                <span style="padding:3px 8px;background:rgba(140,198,63,0.1);border-radius:4px;font-size:8px;color:#8aca7f;font-weight:600;">Content</span>
                <span style="padding:3px 8px;background:rgba(236,72,153,0.1);border-radius:4px;font-size:8px;color:#ec4899;font-weight:600;">Sidebar</span>
            </div>
        </div>'''
    
    # UPLOAD - Zone upload enrichie
    elif visual_hint == "upload":
        wireframe = '''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px dashed #cbd5e1;border-radius:12px;padding:24px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,0.05);position:relative;overflow:hidden;">
            <div style="position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#8aca7f 0%,#aac87a 50%,#8aca7f 100%);"></div>
            <div style="width:56px;height:56px;margin:0 auto 16px;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:28px;box-shadow:0 2px 4px rgba(0,0,0,0.05),inset 0 1px 0 rgba(255,255,255,0.8);">📁</div>
            <div style="font-size:12px;font-weight:700;color:#1e293b;margin-bottom:6px;letter-spacing:-0.2px;">Déposez votre fichier ici</div>
            <div style="font-size:10px;color:#64748b;margin-bottom:12px;">ou cliquez pour parcourir</div>
            <div style="height:8px;background:#f1f5f9;border-radius:4px;overflow:hidden;margin:0 20px;">
                <div style="width:0%;height:100%;background:linear-gradient(90deg,#8aca7f 0%,#aac87a 100%);"></div>
            </div>
            <div style="font-size:9px;color:#94a3b8;margin-top:10px;">PNG, JPG, Figma jusqu'à 20MB</div>
        </div>'''
    
    # GRID - Galerie enrichie
    elif visual_hint == "grid":
        wireframe = '''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px solid #e2e8f0;border-radius:12px;padding:12px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;">
                <span style="font-size:12px;font-weight:700;color:#1e293b;letter-spacing:-0.2px;">🎨 Galerie de styles</span>
                <span style="font-size:9px;color:#64748b;">6 layouts</span>
            </div>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;">
                <div style="aspect-ratio:1;background:linear-gradient(145deg,#e0e6f0 0%,#c8d0e0 100%);border-radius:10px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;box-shadow:0 2px 4px rgba(59,130,246,0.15);border:1px solid #8aca7f;position:relative;">
                    <span style="font-family:Georgia,serif;font-size:14px;color:#5a6a7e;font-weight:600;">Aa</span>
                    <span style="font-size:8px;color:#6a8aa6;font-weight:600;">Serif</span>
                    <div style="position:absolute;top:4px;right:4px;width:14px;height:14px;background:#8aca7f;border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-size:8px;font-weight:700;">✓</div>
                </div>
                <div style="aspect-ratio:1;background:linear-gradient(145deg,#e8f0ec 0%,#c8dcd5 100%);border-radius:10px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                    <span style="font-family:system-ui,sans-serif;font-size:14px;color:#5a7b64;font-weight:600;">Aa</span>
                    <span style="font-size:8px;color:#7ab88a;">Sans</span>
                </div>
                <div style="aspect-ratio:1;background:linear-gradient(145deg,#f5f0d0 0%,#f0dcb8 100%);border-radius:10px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                    <span style="font-family:monospace;font-size:14px;color:#92400e;font-weight:600;">Aa</span>
                    <span style="font-size:8px;color:#d4ab7a;">Mono</span>
                </div>
            </div>
        </div>'''
    
    # GENERIC - Fallback enrichi
    else:
        wireframe = f'''<div style="background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);border:1px solid #e2e8f0;border-radius:12px;padding:12px;box-shadow:0 1px 3px rgba(0,0,0,0.05);position:relative;overflow:hidden;">
            <div style="position:absolute;top:0;left:0;width:4px;height:100%;background:linear-gradient(180deg,{color} 0%,{color}88 100%);"></div>
            <div style="display:flex;align-items:center;gap:12px;">
                <div style="width:36px;height:36px;background:linear-gradient(145deg,{color} 0%,{color}dd 100%);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:14px;color:white;box-shadow:0 2px 4px rgba(0,0,0,0.1);">◆</div>
                <div style="flex:1;">
                    <div style="font-size:12px;font-weight:700;color:#1e293b;letter-spacing:-0.2px;">{nom_clair}</div>
                    <div style="font-size:10px;color:#64748b;font-family:monospace;">{endpoint}</div>
                </div>
                <span style="padding:3px 8px;background:linear-gradient(145deg,#f1f5f9 0%,#e2e8f0 100%);border-radius:4px;font-size:9px;color:#475569;font-weight:700;">{method}</span>
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
        <div style="padding:10px 12px;border-top:1px solid #f1f5f9;background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);">
            <div style="font-size:13px;font-weight:700;color:#1e293b;margin-bottom:4px;letter-spacing:-0.2px;">{nom_clair}</div>
            {f'<div style="font-size:11px;color:#64748b;line-height:1.4;margin-bottom:6px;">{description}</div>' if description else ''}
            <div style="display:flex;align-items:center;gap:8px;">
                <span style="padding:2px 6px;background:{color}15;color:{color};border-radius:4px;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;">{method}</span>
                <span style="font-size:10px;color:#94a3b8;font-family:monospace;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1;">{endpoint}</span>
            </div>
        </div>
    </div>'''
    
    return html


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
        
        /* Tabs enrichis */
        .tabs {{ display: flex; height: 52px; background: #fff; border-bottom: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
        .tab {{ flex: 1; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 14px; color: #64748b; border-right: 1px solid #f1f5f9; transition: all 0.2s; font-weight: 500; letter-spacing: -0.2px; }}
        .tab:last-child {{ border-right: none; }}
        .tab:hover {{ background: linear-gradient(180deg, #fff 0%, #f8fafc 100%); color: #334155; }}
        .tab.active {{ background: linear-gradient(180deg, #aac87a 0%, #8aca7f 100%); color: #1e293b; font-weight: 600; box-shadow: inset 0 -2px 4px rgba(0,0,0,0.05); }}
        
        /* Main */
        .main {{ display: flex; height: calc(100vh - 52px); }}
        
        /* Sidebar enrichie */
        .sidebar {{ width: 300px; background: linear-gradient(180deg, #fff 0%, #fafafa 100%); border-right: 1px solid #e2e8f0; overflow-y: auto; box-shadow: 2px 0 8px rgba(0,0,0,0.03); }}
        .sidebar-header {{ padding: 20px; border-bottom: 1px solid #e2e8f0; background: linear-gradient(180deg, #fff 0%, #f8fafc 100%); }}
        .sidebar-title {{ font-size: 22px; font-weight: 800; color: #8aca7f; letter-spacing: -0.5px; }}
        .sidebar-subtitle {{ font-size: 12px; color: #94a3b8; margin-top: 4px; font-weight: 500; }}
        .sidebar-section {{ padding: 18px; border-bottom: 1px solid #f1f5f9; }}
        .sidebar-label {{ font-size: 10px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 14px; }}
        
        /* Content */
        .content {{ flex: 1; overflow-y: auto; padding: 24px; background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%); }}
        .genome-container {{ max-width: 1400px; margin: 0 auto; }}
        
        /* Sticky Header enrichi */
        .sticky-header {{ position: sticky; top: 0; background: linear-gradient(180deg, rgba(248,250,252,0.98) 0%, rgba(241,245,249,0.98) 100%); padding: 16px 24px; border-bottom: 1px solid #e2e8f0; z-index: 100; display: flex; justify-content: space-between; align-items: center; backdrop-filter: blur(8px); border-radius: 0 0 12px 12px; margin: -24px -24px 20px -24px; }}
        
        /* Stats enrichis */
        .stats {{ display: flex; gap: 16px; margin-bottom: 24px; }}
        .stat {{ flex: 1; text-align: center; padding: 18px 12px; background: linear-gradient(145deg, #fff 0%, #fafafa 100%); border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); transition: all 0.2s; }}
        .stat:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}
        .stat-value {{ font-size: 28px; font-weight: 800; color: #8aca7f; letter-spacing: -1px; }}
        .stat-label {{ font-size: 10px; color: #64748b; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px; margin-top: 4px; }}
        
        /* Component Grid */
        .component-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 20px; }}
        .component-card:hover {{ box-shadow: 0 8px 24px rgba(0,0,0,0.1); transform: translateY(-2px); }}
        .component-card.selected {{ border-color: #8aca7f; box-shadow: 0 0 0 3px rgba(140,198,63,0.15), 0 8px 24px rgba(140,198,63,0.1); }}
    </style>
</head>
<body>
    <div class="tabs">
        <div class="tab">Brainstorm</div>
        <div class="tab">Backend</div>
        <div class="tab active">Frontend</div>
        <div class="tab">Deploy</div>
    </div>

    <div class="main">
        <aside class="sidebar">
            <div class="sidebar-header">
                <div class="sidebar-title">HoméOS</div>
                <div class="sidebar-subtitle">Genome Viewer v2.1</div>
            </div>
            <div class="sidebar-section">
                <div class="sidebar-label">Confiance globale</div>
                <div style="font-size: 42px; font-weight: 800; color: #8aca7f; letter-spacing: -2px; text-shadow: 0 2px 4px rgba(140,198,63,0.2);">{int(genome.get('metadata', {}).get('confidence_global', 0) * 100)}%</div>
            </div>
            <div class="sidebar-section">
                <div class="sidebar-label">Statistiques</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                    <div style="text-align: center; padding: 14px; background: linear-gradient(145deg, #fff 0%, #f8fafc 100%); border-radius: 10px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <div style="font-size: 24px; font-weight: 800; color: #8aca7f; letter-spacing: -1px;">{len(genome.get('n0_phases', []))}</div>
                        <div style="font-size: 10px; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px;">phases</div>
                    </div>
                    <div style="text-align: center; padding: 14px; background: linear-gradient(145deg, #fff 0%, #f8fafc 100%); border-radius: 10px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <div style="font-size: 24px; font-weight: 800; color: #6a8aa6; letter-spacing: -1px;">{len(components)}</div>
                        <div style="font-size: 10px; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px;">composants</div>
                    </div>
                </div>
            </div>
            <div class="sidebar-section">
                <div class="sidebar-label">Wireframes FRD V2</div>
                <div style="font-size: 12px; color: #64748b; line-height: 1.8; font-weight: 500;">
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;"><span style="color:#8aca7f;">●</span> status</div>
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;"><span style="color:#8aca7f;">●</span> zoom-controls</div>
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;"><span style="color:#8aca7f;">●</span> stencil-card</div>
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;"><span style="color:#8aca7f;">●</span> detail-card</div>
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;"><span style="color:#8aca7f;">●</span> color-palette</div>
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;"><span style="color:#8aca7f;">●</span> choice-card</div>
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;"><span style="color:#8aca7f;">●</span> launch-button</div>
                    <div style="display:flex;align-items:center;gap:8px;"><span style="color:#8aca7f;">●</span> apply-changes</div>
                </div>
            </div>
        </aside>

        <div class="content">
            <div class="sticky-header">
                <div style="display: flex; gap: 14px; align-items: center;">
                    <input type="checkbox" id="select-all" style="width: 22px; height: 22px; accent-color: #8aca7f; cursor: pointer;" onchange="toggleAll(this)">
                    <label for="select-all" style="font-size: 15px; color: #334155; cursor: pointer; font-weight: 600; letter-spacing: -0.2px;">Tout sélectionner</label>
                </div>
                <button id="validate-btn" style="padding: 12px 24px; background: linear-gradient(145deg, #8aca7f 0%, #7aba6f 100%); color: white; border: none; border-radius: 10px; font-size: 14px; font-weight: 700; cursor: pointer; opacity: 0.5; box-shadow: 0 2px 8px rgba(140,198,63,0.3); text-shadow: 0 1px 2px rgba(0,0,0,0.1); transition: all 0.2s;" disabled>Valider (0)</button>
            </div>
            
            <div class="genome-container">
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">{len([c for c in components if c.get('method') == 'GET'])}</div>
                        <div class="stat-label">📖 Voir</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" style="color: #6a8aa6;">{len([c for c in components if c.get('method') == 'POST'])}</div>
                        <div class="stat-label">➕ Ajouter</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" style="color: #d4ab7a;">{len([c for c in components if c.get('method') == 'PUT'])}</div>
                        <div class="stat-label">✏️ Modifier</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" style="color: #64748b;">{len([c for c in components if c.get('method') not in ['GET', 'POST', 'PUT']])}</div>
                        <div class="stat-label">Autres</div>
                    </div>
                </div>
                
                <h2 style="font-size: 20px; font-weight: 800; color: #1e293b; margin-bottom: 20px; letter-spacing: -0.5px;">🧬 le Génome — <span style="color: #8aca7f;">{len(components)}</span> composants</h2>
                
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
