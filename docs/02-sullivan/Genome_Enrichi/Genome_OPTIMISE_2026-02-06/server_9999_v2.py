#!/usr/bin/env python3
"""
Serveur HTTP pour visualisation du Genome - Port 9999
Version 2.1 - Wireframes enrichis (ombres, gradients, style Figma)
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

PORT = 9999
GENOME_FILE = "genome_inferred_kimi_innocent_v2.json"

# Ordre d'identifiabilité pour le tri des composants
IDENTIFIABILITY_ORDER = [
    "upload", "color-palette", "preview", "chat/bubble", "download", "status",
    "grid", "choice-card", "stencil-card", "dashboard", "table", "form",
    "detail-card", "zoom-controls", "chat-input", "accordion", "editor", "launch-button",
    "apply-changes", "breadcrumb", "stepper", "modal", "list", "card", "button"
]

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
    
    # Mapping user-friendly
    USER_FRIENDLY_NAMES = {
        "Vue Rapport IR": "Tableau des organes détectés",
        "Détail Organe": "Fiche détaillée d'un organe",
        "Carte Stencil": "Carte de pouvoir à valider",
        "Status Session": "Indicateur de santé du projet",
        "Stepper 9 Étapes": "Navigation entre les 9 phases",
        "Galerie Layouts": "Choix de mise en page visuelle",
        "Zone Upload": "Import de fichier design (PNG)",
        "Palette Extraite": "Couleurs et style détectés",
        "Aperçu Zones": "Zones détectées dans votre maquette",
        "Bulles Conversation": "Dialogue avec Sullivan",
        "Input Message": "Zone de saisie de message",
        "Dashboard Validation": "Récapitulatif de vos choix",
        "Contrôles Zoom": "Navigation hiérarchique (Corps/Organes/Atomes)",
        "Zoom Out": "Remonter d'un niveau",
        "Fiche Détail Atome": "Détails techniques de l'endpoint",
        "Éditeur Code": "Éditeur de code avec coloration syntaxique",
        "Lancer Distillation": "Générer le code final",
        "Appliquer Changements": "Sauvegarder vos modifications",
        "Reset Session": "Réinitialiser la session",
        "Résumé Genome": "Vue d'ensemble du projet",
        "Liste Distillation": "Historique des générations",
        "Bouton Suivant": "Passer à l'étape suivante",
        "Fil d'Ariane": "Position actuelle dans le parcours",
        "Carte Layout": "Aperçu d'une mise en page",
        "Choix Style": "Sélection du style visuel (Minimal, Brutaliste...)",
        "Tableau Expert": "Vue technique des décisions",
        "Validation Arbiter": "Confirmation finale des choix",
        "Résumé Décisions": "Récapitulatif détaillé de vos décisions",
        "Modal Confirmation": "Fenêtre de confirmation"
    }
    nom_clair = USER_FRIENDLY_NAMES.get(nom_clair, nom_clair)
    
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
    
    # ZOOM-CONTROLS - Navigation compacte
    elif visual_hint == "zoom-controls":
        wireframe = '''<div style="background:#f8fafc;border-radius:4px;padding:6px;display:flex;gap:4px;align-items:center;justify-content:center;">
            <span style="padding:3px 6px;background:#e2e8f0;border-radius:3px;font-size:9px;color:#475569;">←</span>
            <span style="padding:3px 8px;background:#5a9ac6;border-radius:3px;font-size:9px;color:white;">Corps ▼</span>
            <span style="padding:3px 6px;background:#e2e8f0;border-radius:3px;font-size:9px;color:#475569;">→</span>
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
    
    # TABLE - Tableau compact
    elif visual_hint == "table":
        wireframe = '''<div style="background:#f8fafc;border-radius:4px;padding:6px;display:flex;flex-direction:column;gap:4px;justify-content:center;height:50px;">
            <div style="display:flex;gap:4px;"><div style="flex:2;height:6px;background:#e2e8f0;border-radius:1px;"></div><div style="flex:1;height:6px;background:#e2e8f0;border-radius:1px;"></div></div>
            <div style="display:flex;gap:4px;"><div style="flex:2;height:6px;background:#e2e8f0;border-radius:1px;"></div><div style="flex:1;height:6px;background:#e2e8f0;border-radius:1px;"></div></div>
            <div style="display:flex;gap:4px;"><div style="flex:2;height:6px;background:#e2e8f0;border-radius:1px;"></div><div style="flex:1;height:6px;background:#e2e8f0;border-radius:1px;"></div></div>
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
    
    # DASHBOARD - Dashboard compact
    elif visual_hint == "dashboard":
        wireframe = '''<div style="background:#f8fafc;border-radius:4px;padding:6px;display:flex;gap:4px;align-items:flex-end;justify-content:center;height:50px;">
            <div style="width:12%;height:40%;background:#7aca6a;border-radius:2px 2px 0 0;"></div>
            <div style="width:12%;height:65%;background:#7aca6a;border-radius:2px 2px 0 0;"></div>
            <div style="width:12%;height:45%;background:#5a9ac6;border-radius:2px 2px 0 0;"></div>
            <div style="width:12%;height:80%;background:#7aca6a;border-radius:2px 2px 0 0;"></div>
            <div style="width:12%;height:55%;background:#e4bb5a;border-radius:2px 2px 0 0;"></div>
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
    
    # PREVIEW - Aperçu compact
    elif visual_hint == "preview":
        wireframe = '''<div style="background:#f8fafc;border-radius:4px;padding:6px;display:flex;gap:4px;justify-content:center;align-items:center;height:50px;">
            <div style="width:25%;height:35px;background:rgba(59,130,246,0.2);border:1px dashed #5a9ac6;border-radius:3px;"></div>
            <div style="width:35%;height:35px;background:rgba(140,198,63,0.2);border:1px dashed #7aca6a;border-radius:3px;"></div>
            <div style="width:20%;height:35px;background:rgba(236,72,153,0.15);border:1px dashed #ec4899;border-radius:3px;"></div>
        </div>'''
    
    # UPLOAD - Zone upload compact
    elif visual_hint == "upload":
        wireframe = '''<div style="background:#f8fafc;border:1px dashed #cbd5e1;border-radius:4px;padding:8px;text-align:center;height:50px;display:flex;align-items:center;justify-content:center;gap:6px;">
            <span style="font-size:16px;">📁</span>
            <span style="font-size:9px;color:#64748b;">Déposer un fichier</span>
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
    html = f'''<div class="component-card" style="background:white;border:1px solid #e2e8f0;border-radius:10px;padding:0;cursor:pointer;transition:all 0.2s;position:relative;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.05);" onclick="toggleCheckbox('comp-{comp_id}')">
        <div style="position:absolute;bottom:4px;right:4px;z-index:10;background:rgba(255,255,255,0.95);padding:2px;border-radius:3px;box-shadow:0 1px 2px rgba(0,0,0,0.1);">
            <input type="checkbox" id="comp-{comp_id}" class="comp-checkbox" value="{comp_id}" style="width:12px;height:12px;cursor:pointer;accent-color:#6a9a4f;" onclick="event.stopPropagation();updateValidateButton()">
        </div>
        <div style="max-height:70px;overflow:hidden;background:#f8fafc;">
            {wireframe}
        </div>
        <div style="padding:5px 8px;border-top:1px solid #f1f5f9;background:linear-gradient(145deg,#ffffff 0%,#fafafa 100%);">
            <div style="font-size:11px;font-weight:700;color:#1e293b;margin-bottom:2px;letter-spacing:-0.2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{nom_clair}</div>
            {f'<div style="font-size:10px;color:#64748b;line-height:1.3;margin-bottom:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{description}</div>' if description else ''}
            <div style="display:flex;align-items:center;gap:3px;">
                <span style="padding:1px 4px;background:{color}15;color:{color};border-radius:3px;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.3px;">{method}</span>
                <span style="font-size:10px;color:#94a3b8;font-family:monospace;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1;">{endpoint}</span>
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
                    elif visual in ['upload', 'download', 'color-palette', 'stencil-card', 'detail-card',
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
    
    # Cellules: tri par identifiabilité
    cellules_items.sort(key=lambda x: IDENTIFIABILITY_ORDER.index(x.get('visual_hint', '')) if x.get('visual_hint', '') in IDENTIFIABILITY_ORDER else 999)
    
    # Atomes: tri par identifiabilité (upload/preview en premier, boutons génériques en dernier)
    atomes_items.sort(key=lambda x: IDENTIFIABILITY_ORDER.index(x.get('visual_hint', '')) if x.get('visual_hint', '') in IDENTIFIABILITY_ORDER else 999)
    
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
    # Extraire tous les composants pour les stats
    all_components = []
    for phase in genome.get('n0_phases', []):
        for section in phase.get('n1_sections', []):
            for feature in section.get('n2_features', []):
                all_components.extend(feature.get('n3_components', []))

    total_components = len(all_components)

    # Génération directe de la hiérarchie
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
        .main {{ display: flex; height: calc(100vh - 52px); }}
        
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
        .component-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; min-width: 0; }}
        .component-card {{ min-width: 0; }}
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

    <div class="main">
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
                        <div style="font-size: 24px; font-weight: 800; color: #5a9ac6; letter-spacing: -1px;">{total_components}</div>
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
                    <input type="checkbox" id="select-all" style="width: 22px; height: 22px; accent-color: #7aca6a; cursor: pointer;" onchange="toggleAll(this)">
                    <label for="select-all" style="font-size: 15px; color: #334155; cursor: pointer; font-weight: 600; letter-spacing: -0.2px;">Tout sélectionner</label>
                </div>
                <button id="validate-btn" style="padding: 12px 24px; background: linear-gradient(145deg, #7aca6a 0%, #6aba5a 100%); color: white; border: none; border-radius: 10px; font-size: 14px; font-weight: 700; cursor: pointer; opacity: 0.5; box-shadow: 0 2px 8px rgba(140,198,63,0.3); text-shadow: 0 1px 2px rgba(0,0,0,0.1); transition: all 0.2s;" disabled>Valider (0)</button>
            </div>
            
            <div class="genome-container">
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">{len([c for c in all_components if c.get('method') == 'GET'])}</div>
                        <div class="stat-label">Lire (GET)</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" style="color: #5a9ac6;">{len([c for c in all_components if c.get('method') == 'POST'])}</div>
                        <div class="stat-label">Creer (POST)</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" style="color: #e4bb5a;">{len([c for c in all_components if c.get('method') == 'PUT'])}</div>
                        <div class="stat-label">Modifier (PUT)</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" style="color: #64748b;">{len([c for c in all_components if c.get('method') not in ['GET', 'POST', 'PUT']])}</div>
                        <div class="stat-label">Autres</div>
                    </div>
                </div>
                
                <h2 style="font-size: 18px; font-weight: 700; color: #1e293b; margin-bottom: 4px; letter-spacing: -0.3px;">Architecture Genome</h2>
                <p style="font-size: 14px; color: #64748b; margin-bottom: 20px;">{total_components} composants classifies par niveau d'abstraction</p>
                
                {hierarchy_html}
            </div>
        </div>
    </div>
    
    <script>
        function switchTab(element, tabName) {{
            // Retirer active de tous les tabs
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            // Ajouter active au tab cliqué
            element.classList.add('active');
            // Masquer tous les contenus
            document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');
            // Afficher le contenu du tab sélectionné
            const content = document.getElementById('tab-content-' + tabName);
            if (content) content.style.display = 'block';
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
