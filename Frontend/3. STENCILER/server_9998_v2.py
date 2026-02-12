#!/usr/bin/env python3
"""
Serveur HTTP pour visualisation du Genome - Port 9998
Version 6.0 - Collapses + Wingdings3 + Noms User-Friendly
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

PORT = 9998
GENOME_FILE = "../2. GENOME/genome_reference.json"
FONTS_DIR = "../fonts"

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


def get_method_color(method):
    """Retourne la couleur associée à une méthode HTTP"""
    colors = {"GET": "#7aca6a", "POST": "#5a9ac6", "PUT": "#e4bb5a", "DELETE": "#d56363"}
    return colors.get(method, "#64748b")


# =============================================================================
# WIREFRAMES AMÉLIORÉS PAR NIVEAU
# =============================================================================

def generate_wireframe_corps(visual_hint, color="#7aca6a"):
    """Wireframes explicites pour les Corps (niveau stratégique)"""
    
    if visual_hint == "brainstorm":
        # 💡 Démarrage - stepper créatif
        return '''<div style="background:linear-gradient(135deg,#fef3c7 0%,#fde68a 100%);padding:8px;border-radius:8px;height:70px;display:flex;flex-direction:column;gap:4px;justify-content:center;align-items:center;">
            <div style="display:flex;gap:6px;align-items:center;">
                <span style="font-size:20px;">💡</span>
                <div style="width:40px;height:3px;background:#fbbf24;border-radius:2px;"></div>
                <span style="font-size:16px;">📝</span>
                <div style="width:40px;height:3px;background:#cbd5e1;border-radius:2px;"></div>
                <span style="font-size:16px;opacity:0.5;">✓</span>
            </div>
            <div style="font-size:10px;color:#92400e;font-weight:600;">Phase créative</div>
        </div>'''
    
    elif visual_hint == "backend":
        # ⚙️ Moteur - dashboard technique
        return '''<div style="background:linear-gradient(135deg,#e0e7ff 0%,#c7d2fe 100%);padding:8px;border-radius:8px;height:70px;display:flex;flex-direction:column;gap:4px;">
            <div style="font-size:10px;color:#3730a3;font-weight:600;">⚙️ Moteur & Données</div>
            <div style="display:flex;gap:4px;align-items:flex-end;flex:1;padding:4px 0;">
                <div style="flex:1;height:40%;background:#6366f1;border-radius:2px 2px 0 0;"></div>
                <div style="flex:1;height:70%;background:#6366f1;border-radius:2px 2px 0 0;"></div>
                <div style="flex:1;height:55%;background:#818cf8;border-radius:2px 2px 0 0;"></div>
                <div style="flex:1;height:85%;background:#6366f1;border-radius:2px 2px 0 0;"></div>
            </div>
        </div>'''
    
    elif visual_hint == "frontend":
        # Design - preview colore
        return '''<div style="background:linear-gradient(135deg,#fce7f3 0%,#fbcfe8 100%);padding:8px;border-radius:8px;height:70px;display:flex;flex-direction:column;gap:4px;">
            <div style="font-size:10px;color:#9d174d;font-weight:600;">Design & Interface</div>
            <div style="display:flex;gap:4px;justify-content:center;align-items:center;flex:1;">
                <div style="width:30%;height:45px;background:rgba(59,130,246,0.3);border:1px dashed #3b82f6;border-radius:4px;"></div>
                <div style="width:35%;height:45px;background:rgba(16,185,129,0.3);border:1px dashed #10b981;border-radius:4px;"></div>
                <div style="width:25%;height:45px;background:rgba(236,72,153,0.3);border:1px dashed #ec4899;border-radius:4px;"></div>
            </div>
        </div>'''
    
    elif visual_hint == "deploy":
        # 🚀 Publication - bouton lancement
        return '''<div style="background:linear-gradient(135deg,#d1fae5 0%,#a7f3d0 100%);padding:8px;border-radius:8px;height:70px;display:flex;flex-direction:column;gap:4px;justify-content:center;align-items:center;">
            <div style="padding:8px 20px;background:linear-gradient(145deg,#10b981 0%,#059669 100%);border-radius:16px;color:white;font-size:11px;font-weight:700;display:flex;align-items:center;gap:6px;">
                <span>🚀</span> Publier
            </div>
            <div style="font-size:9px;color:#065f46;">Mise en ligne</div>
        </div>'''
    
    else:
        return generate_wireframe_general(visual_hint, color)


def generate_wireframe_organes(visual_hint, color="#7aca6a"):
    """Wireframes explicites pour les Organes (niveau fonctionnel)"""
    
    if visual_hint == "analyse":
        # 🔍 Analyse du Projet - tableau simple
        return '''<div style="background:#f8fafc;padding:6px;border-radius:6px;height:65px;display:flex;flex-direction:column;gap:3px;">
            <div style="display:flex;gap:3px;align-items:center;">
                <span style="font-size:12px;">🔍</span>
                <div style="flex:1;height:6px;background:#e2e8f0;border-radius:1px;"></div>
            </div>
            <div style="display:flex;gap:3px;"><div style="flex:2;height:5px;background:#cbd5e1;border-radius:1px;"></div><div style="flex:1;height:5px;background:#7aca6a;border-radius:1px;"></div></div>
            <div style="display:flex;gap:3px;"><div style="flex:2;height:5px;background:#cbd5e1;border-radius:1px;"></div><div style="flex:1;height:5px;background:#cbd5e1;border-radius:1px;"></div></div>
            <div style="display:flex;gap:3px;"><div style="flex:2;height:5px;background:#cbd5e1;border-radius:1px;"></div><div style="flex:1;height:5px;background:#fbbf24;border-radius:1px;"></div></div>
        </div>'''
    
    elif visual_hint == "choix":
        # ⚖️ Choix des Fonctions - cartes A/B
        return '''<div style="background:#f8fafc;padding:6px;border-radius:6px;height:65px;display:flex;gap:6px;justify-content:center;align-items:center;">
            <div style="width:40%;height:45px;background:white;border:2px solid #7aca6a;border-radius:6px;display:flex;align-items:center;justify-content:center;"><span style="color:#7aca6a;font-size:16px;font-weight:bold;">✓</span></div>
            <div style="width:40%;height:45px;background:#f1f5f9;border:1px solid #cbd5e1;border-radius:6px;display:flex;align-items:center;justify-content:center;"><span style="color:#94a3b8;font-size:16px;">○</span></div>
        </div>'''
    
    elif visual_hint == "sauvegarde":
        # 📁 Mon Travail - LEDs de statut
        return '''<div style="background:#f8fafc;padding:6px;border-radius:6px;height:65px;display:flex;flex-direction:column;gap:4px;justify-content:center;align-items:center;">
            <div style="display:flex;gap:8px;align-items:center;">
                <div style="width:14px;height:14px;background:#7aca6a;border-radius:50%;box-shadow:0 0 8px #7aca6a;"></div>
                <div style="width:14px;height:14px;background:#7aca6a;border-radius:50%;box-shadow:0 0 8px #7aca6a;"></div>
                <div style="width:14px;height:14px;background:#7aca6a;border-radius:50%;box-shadow:0 0 8px #7aca6a;"></div>
                <div style="width:14px;height:14px;background:#e2e8f0;border-radius:50%;"></div>
            </div>
            <div style="font-size:9px;color:#64748b;">3/4 sauvegardé</div>
        </div>'''
    
    elif visual_hint == "parcours":
        # 🧭 Parcours - breadcrumb
        return '''<div style="background:#f8fafc;padding:6px;border-radius:6px;height:65px;display:flex;flex-direction:column;gap:4px;justify-content:center;align-items:center;">
            <div style="display:flex;align-items:center;gap:4px;">
                <span style="color:#7aca6a;font-size:11px;font-weight:600;">1. Idée</span>
                <span style="color:#cbd5e1;">→</span>
                <span style="color:#7aca6a;font-size:11px;font-weight:600;">2. Choix</span>
                <span style="color:#cbd5e1;">→</span>
                <span style="color:#94a3b8;font-size:11px;">3. Design</span>
            </div>
            <div style="width:60%;height:4px;background:#e2e8f0;border-radius:2px;overflow:hidden;">
                <div style="width:66%;height:100%;background:#7aca6a;"></div>
            </div>
        </div>'''
    
    elif visual_hint == "style":
        # Style de Page - grille de choix
        return '''<div style="background:#f8fafc;padding:6px;border-radius:6px;height:65px;display:flex;flex-direction:column;gap:3px;">
            <div style="font-size:9px;color:#64748b;text-align:center;">Choisir le look</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;flex:1;">
                <div style="background:#fff;border:2px solid #7aca6a;border-radius:4px;"></div>
                <div style="background:#f1f5f9;border:1px solid #cbd5e1;border-radius:4px;"></div>
                <div style="background:#f1f5f9;border:1px solid #cbd5e1;border-radius:4px;"></div>
                <div style="background:#f1f5f9;border:1px solid #cbd5e1;border-radius:4px;"></div>
            </div>
        </div>'''
    
    elif visual_hint == "import":
        # Importer ma Maquette - upload
        return '''<div style="background:#f8fafc;padding:6px;border-radius:6px;height:65px;display:flex;flex-direction:column;gap:3px;justify-content:center;align-items:center;border:1px dashed #cbd5e1;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2" style="margin-bottom:8px;"><path d="M12 16V4m0 0l-4 4m4-4l4 4M4 17v2a2 2 0 002 2h12a2 2 0 002-2v-2"/></svg>
            <div style="font-size:9px;color:#64748b;">Glisser-déposer</div>
        </div>'''
    
    elif visual_hint == "decrypter":
        # 🔎 Décrypter l'Image - vision IA
        return '''<div style="background:#f8fafc;padding:6px;border-radius:6px;height:65px;display:flex;gap:4px;justify-content:center;align-items:center;position:relative;">
            <div style="width:40%;height:50px;background:linear-gradient(135deg,#ddd6fe 0%,#c4b5fd 100%);border-radius:4px;opacity:0.5;"></div>
            <div style="width:40%;height:50px;background:linear-gradient(135deg,#bae6fd 0%,#7dd3fc 100%);border-radius:4px;opacity:0.5;"></div>
            <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(255,255,255,0.9);padding:4px 8px;border-radius:12px;font-size:10px;font-weight:600;color:#7c3aed;">👁️ IA active</div>
        </div>'''
    
    elif visual_hint == "discussion":
        # 💬 Discussion avec l'Assistant - chat
        return '''<div style="background:#f8fafc;padding:6px;border-radius:6px;height:65px;display:flex;flex-direction:column;gap:4px;justify-content:center;">
            <div style="display:flex;gap:4px;align-items:flex-end;">
                <div style="width:18px;height:18px;background:#6366f1;border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-size:9px;font-weight:bold;">S</div>
                <div style="flex:1;height:14px;background:#e0e7ff;border-radius:8px 8px 8px 2px;"></div>
            </div>
            <div style="display:flex;gap:4px;align-items:flex-end;justify-content:flex-end;">
                <div style="width:50%;height:14px;background:#7aca6a;border-radius:8px 8px 2px 8px;"></div>
            </div>
        </div>'''
    
    elif visual_hint == "verifier":
        # ✅ Vérifier & Valider - dashboard validation
        return '''<div style="background:#f8fafc;padding:6px;border-radius:6px;height:65px;display:flex;flex-direction:column;gap:4px;justify-content:center;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:10px;color:#64748b;">✓ Validé</span>
                <div style="width:40px;height:6px;background:#7aca6a;border-radius:3px;"></div>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:10px;color:#64748b;">○ En attente</span>
                <div style="width:30px;height:6px;background:#e2e8f0;border-radius:3px;"></div>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:10px;color:#64748b;">✓ OK</span>
                <div style="width:50px;height:6px;background:#7aca6a;border-radius:3px;"></div>
            </div>
        </div>'''
    
    elif visual_hint == "details":
        # 🔧 Détails & Réglages - zoom + éditeur
        return '''<div style="background:#f8fafc;padding:6px;border-radius:6px;height:65px;display:flex;flex-direction:column;gap:4px;justify-content:center;align-items:center;">
            <div style="display:flex;gap:4px;align-items:center;">
                <span style="padding:3px 8px;background:#e2e8f0;border-radius:3px;font-size:10px;">🔍-</span>
                <span style="padding:3px 8px;background:#5a9ac6;border-radius:3px;font-size:10px;color:white;">Niv. 2</span>
                <span style="padding:3px 8px;background:#e2e8f0;border-radius:3px;font-size:10px;">🔍+</span>
            </div>
            <div style="width:80%;height:20px;background:#1e293b;border-radius:3px;display:flex;align-items:center;padding:0 6px;">
                <div style="width:40%;height:3px;background:#475569;border-radius:1px;"></div>
            </div>
        </div>'''
    
    elif visual_hint == "recuperer":
        # 📥 Récupérer mon Code - téléchargement
        return '''<div style="background:#f8fafc;padding:6px;border-radius:6px;height:65px;display:flex;flex-direction:column;gap:4px;justify-content:center;align-items:center;">
            <div style="display:flex;align-items:center;gap:6px;padding:6px 14px;background:#f1f5f9;border:1px solid #cbd5e1;border-radius:6px;">
                <span style="font-size:14px;">📥</span>
                <span style="font-size:10px;font-weight:600;color:#475569;">mon-projet.zip</span>
            </div>
            <div style="font-size:9px;color:#64748b;">Cliquer pour télécharger</div>
        </div>'''
    
    else:
        return generate_wireframe_general(visual_hint, color)


def generate_wireframe_cellules(visual_hint, color="#7aca6a"):
    """Wireframes explicites pour les Cellules (niveau feature)"""
    # Les cellules utilisent les mêmes visuels que les organes mais plus petits/détaillés
    return generate_wireframe_organes(visual_hint, color)


def generate_wireframe_general(visual_hint, color="#7aca6a"):
    """Wireframes pour les Atomes (niveau composant - inchangés, déjà bons)"""
    
    if visual_hint == "table":
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:3px;justify-content:center;">
            <div style="display:flex;gap:3px;"><div style="flex:2;height:5px;background:#e2e8f0;border-radius:1px;"></div><div style="flex:1;height:5px;background:#e2e8f0;border-radius:1px;"></div></div>
            <div style="display:flex;gap:3px;"><div style="flex:2;height:5px;background:#e2e8f0;border-radius:1px;"></div><div style="flex:1;height:5px;background:#7aca6a;border-radius:1px;"></div></div>
            <div style="display:flex;gap:3px;"><div style="flex:2;height:5px;background:#e2e8f0;border-radius:1px;"></div><div style="flex:1;height:5px;background:#e2e8f0;border-radius:1px;"></div></div>
        </div>'''
    
    elif visual_hint == "preview":
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;gap:3px;justify-content:center;align-items:center;">
            <div style="width:25%;height:40px;background:rgba(59,130,246,0.2);border:1px dashed #5a9ac6;border-radius:3px;"></div>
            <div style="width:35%;height:40px;background:rgba(140,198,63,0.2);border:1px dashed #7aca6a;border-radius:3px;"></div>
            <div style="width:20%;height:40px;background:rgba(236,72,153,0.15);border:1px dashed #ec4899;border-radius:3px;"></div>
        </div>'''
    
    elif visual_hint == "dashboard":
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;gap:3px;align-items:flex-end;justify-content:center;">
            <div style="width:12%;height:30%;background:#7aca6a;border-radius:2px 2px 0 0;"></div>
            <div style="width:12%;height:50%;background:#7aca6a;border-radius:2px 2px 0 0;"></div>
            <div style="width:12%;height:35%;background:#5a9ac6;border-radius:2px 2px 0 0;"></div>
            <div style="width:12%;height:60%;background:#7aca6a;border-radius:2px 2px 0 0;"></div>
        </div>'''
    
    elif visual_hint == "upload":
        return '''<div style="background:#f8fafc;border:1px dashed #cbd5e1;border-radius:4px;height:60px;display:flex;align-items:center;justify-content:center;">
            <span style="font-size:24px;color:#94a3b8;">+</span>
        </div>'''
    
    elif visual_hint == "color-palette":
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;gap:4px;justify-content:center;align-items:center;">
            <div style="width:18px;height:18px;background:#5a9ac6;border-radius:4px;"></div>
            <div style="width:18px;height:18px;background:#7aca6a;border-radius:4px;"></div>
            <div style="width:18px;height:18px;background:#e4bb5a;border-radius:4px;"></div>
            <div style="width:18px;height:18px;background:#1e293b;border-radius:4px;"></div>
        </div>'''
    
    elif visual_hint == "chat/bubble":
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:4px;justify-content:center;">
            <div style="display:flex;gap:4px;"><div style="width:16px;height:16px;background:#6a8aca;border-radius:50%;"></div><div style="flex:1;height:12px;background:#e2e8f0;border-radius:6px;"></div></div>
            <div style="display:flex;gap:4px;justify-content:flex-end;"><div style="width:50%;height:12px;background:#6a8aca;border-radius:6px;"></div></div>
        </div>'''
    
    elif visual_hint == "stepper":
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;gap:4px;justify-content:center;align-items:center;">
            <div style="width:16px;height:16px;background:#7aca6a;border-radius:50%;"></div>
            <div style="flex:1;height:2px;background:#7aca6a;"></div>
            <div style="width:16px;height:16px;background:#7aca6a;border-radius:50%;"></div>
            <div style="flex:1;height:2px;background:#e2e8f0;"></div>
            <div style="width:16px;height:16px;background:#e2e8f0;border-radius:50%;"></div>
        </div>'''
    
    elif visual_hint == "status":
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;gap:8px;justify-content:center;align-items:center;">
            <div style="width:12px;height:12px;background:#7aca6a;border-radius:50%;"></div>
            <div style="width:12px;height:12px;background:#7aca6a;border-radius:50%;"></div>
            <div style="width:12px;height:12px;background:#7aca6a;border-radius:50%;"></div>
            <div style="width:12px;height:12px;background:#e2e8f0;border-radius:50%;"></div>
        </div>'''
    
    elif visual_hint == "zoom-controls":
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;gap:4px;align-items:center;justify-content:center;">
            <span style="padding:4px 8px;background:#e2e8f0;border-radius:3px;font-size:10px;color:#64748b;">&lt;</span>
            <span style="padding:4px 8px;background:#5a9ac6;border-radius:3px;font-size:10px;color:white;font-weight:600;">N0</span>
            <span style="padding:4px 8px;background:#e2e8f0;border-radius:3px;font-size:10px;color:#64748b;">&gt;</span>
        </div>'''
    
    elif visual_hint == "stencil-card":
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:3px;justify-content:center;border-left:3px solid #e4bb5a;">
            <div style="height:6px;background:#e2e8f0;border-radius:1px;width:60%;"></div>
            <div style="display:flex;gap:3px;">
                <div style="flex:1;height:16px;background:#7aca6a;border-radius:2px;"></div>
                <div style="flex:1;height:16px;background:#e2e8f0;border-radius:2px;"></div>
            </div>
        </div>'''
    
    elif visual_hint == "launch-button":
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;align-items:center;justify-content:center;">
            <div style="padding:10px 24px;background:linear-gradient(145deg,#7aca6a 0%,#6aba5a 100%);border-radius:20px;color:white;font-size:11px;font-weight:700;">🚀 GO</div>
        </div>'''
    
    elif visual_hint == "download":
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;align-items:center;justify-content:center;">
            <span style="font-size:20px;color:#5a9ac6;">⬇</span>
        </div>'''
    
    elif visual_hint == "breadcrumb":
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;align-items:center;justify-content:center;gap:4px;">
            <span style="color:#7aca6a;font-size:11px;font-weight:600;">A</span>
            <span style="color:#94a3b8;">/</span>
            <span style="color:#64748b;font-size:11px;">B</span>
        </div>'''
    
    elif visual_hint == "detail-card":
        return f'''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:3px;justify-content:center;">
            <div style="height:6px;background:{color};border-radius:2px;width:30%;"></div>
            <div style="height:4px;background:#e2e8f0;border-radius:1px;"></div>
            <div style="height:4px;background:#e2e8f0;border-radius:1px;width:80%;"></div>
        </div>'''
    
    elif visual_hint == "choice-card":
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;gap:6px;justify-content:center;align-items:center;">
            <div style="width:32px;height:32px;background:white;border:2px solid #7aca6a;border-radius:6px;"></div>
            <div style="width:32px;height:32px;background:#f1f5f9;border:1px solid #e2e8f0;border-radius:6px;"></div>
        </div>'''
    
    elif visual_hint == "editor":
        return '''<div style="background:#1e293b;border-radius:4px;padding:6px;height:60px;display:flex;flex-direction:column;gap:3px;justify-content:center;">
            <div style="height:4px;background:#334155;border-radius:1px;width:60%;"></div>
            <div style="height:4px;background:#334155;border-radius:1px;width:40%;"></div>
        </div>'''
    
    elif visual_hint == "grid":
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:grid;grid-template-columns:repeat(3,1fr);gap:3px;">
            <div style="background:#d0e6ff;border-radius:3px;"></div>
            <div style="background:#e0f8e0;border-radius:3px;"></div>
            <div style="background:#fff8a0;border-radius:3px;"></div>
        </div>'''
    
    elif visual_hint == "button":
        return f'''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;align-items:center;justify-content:center;">
            <div style="padding:8px 20px;background:{color};border-radius:4px;color:white;font-size:11px;font-weight:600;">Action</div>
        </div>'''
    
    elif visual_hint == "form":
        return '''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;flex-direction:column;gap:4px;justify-content:center;">
            <div style="height:8px;background:#e2e8f0;border-radius:2px;width:40%;"></div>
            <div style="height:16px;background:white;border:1px solid #e2e8f0;border-radius:2px;"></div>
        </div>'''
    
    else:
        return f'''<div style="background:#f8fafc;padding:6px;border-radius:4px;height:60px;display:flex;align-items:center;justify-content:center;">
            <div style="width:36px;height:36px;background:{color}20;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;color:{color};">◆</div>
        </div>'''


# =============================================================================
# MAPPING DES NOMS USER-FRIENDLY
# =============================================================================

# Corps : noms inchangés mais wireframes améliorés
CORPS_MAPPING = {
    'n0_brainstorm': {'name': 'Brainstorm', 'hint': 'brainstorm', 'desc': 'Phase créative : comprendre vos besoins et structurer votre projet'},
    'n0_backend': {'name': 'Backend', 'hint': 'backend', 'desc': 'Moteur invisible : gestion des données et logique métier'},
    'n0_frontend': {'name': 'Frontend', 'hint': 'frontend', 'desc': 'Ce que vous voyez : interface, design et expérience utilisateur'},
    'n0_deploy': {'name': 'Deploy', 'hint': 'deploy', 'desc': 'Mise en ligne : publication et livraison de votre projet'}
}

# Organes : noms user-friendly (sans emojis)
ORGANES_MAPPING = {
    'n1_ir': {'name': 'Analyse du Projet', 'hint': 'analyse', 'desc': 'Inventaire complet de ce dont vous avez besoin'},
    'n1_arbitrage': {'name': 'Choix des Fonctions', 'hint': 'choix', 'desc': 'Décider quelles fonctionnalités garder ou mettre de côté'},
    'n1_session': {'name': 'Mon Travail', 'hint': 'sauvegarde', 'desc': 'Sauvegarde automatique et état de votre progression'},
    'n1_navigation': {'name': 'Parcours', 'hint': 'parcours', 'desc': 'Guide visuel : où vous êtes et où vous allez'},
    'n1_layout': {'name': 'Style de Page', 'hint': 'style', 'desc': 'Choisir l\'apparence visuelle de votre projet'},
    'n1_upload': {'name': 'Importer ma Maquette', 'hint': 'import', 'desc': 'Envoyer une image ou maquette existante'},
    'n1_analysis': {'name': 'Décrypter l\'Image', 'hint': 'decrypter', 'desc': 'L\'IA analyse votre design et extrait les éléments'},
    'n1_dialogue': {'name': 'Discussion avec l\'Assistant', 'hint': 'discussion', 'desc': 'Affiner votre projet en conversation avec Sullivan'},
    'n1_validation': {'name': 'Vérifier & Valider', 'hint': 'verifier', 'desc': 'Contrôle final avant génération du code'},
    'n1_adaptation': {'name': 'Détails & Réglages', 'hint': 'details', 'desc': 'Zoom sur les détails et ajustements fin'},
    'n1_export': {'name': 'Récupérer mon Code', 'hint': 'recuperer', 'desc': 'Télécharger le code final de votre projet'}
}

# Cellules : noms user-friendly (sous-éléments, sans emojis)
CELLULES_MAPPING = {
    'n2_ir_report': {'name': 'Résultat de l\'Analyse', 'hint': 'analyse'},
    'n2_stencils': {'name': 'Cartes de Fonctions', 'hint': 'choix'},
    'n2_session_mgmt': {'name': 'Sauvegarde Auto', 'hint': 'sauvegarde'},
    'n2_stepper': {'name': 'Où j\'en suis', 'hint': 'parcours'},
    'n2_layouts': {'name': 'Choix du Look', 'hint': 'style'},
    'n2_upload': {'name': 'Envoyer & Extraire', 'hint': 'import'},
    'n2_vision_analysis': {'name': 'Ce que l\'IA voit', 'hint': 'decrypter'},
    'n2_chat': {'name': 'Ma Conversation', 'hint': 'discussion'},
    'n2_validation': {'name': 'Mon Récap', 'hint': 'verifier'},
    'n2_zoom': {'name': 'Zoom Avant/Arrière', 'hint': 'details'},
    'n2_export': {'name': 'Mon Projet Final', 'hint': 'recuperer'}
}


def generate_component_card(comp, level='atomes'):
    """Génère une carte de composant avec son wireframe adapté au niveau"""
    comp_id = comp.get('id', 'unknown')
    name = comp.get('name', 'Sans nom')
    endpoint = comp.get('endpoint', 'N/A')
    method = comp.get('method', 'GET')
    visual_hint = comp.get('visual_hint', 'generic')
    description = comp.get('description', '')
    
    color = get_method_color(method)
    
    # Choisir le wireframe selon le niveau
    if level == 'corps':
        wireframe = generate_wireframe_corps(visual_hint, color)
    elif level == 'organes':
        wireframe = generate_wireframe_organes(visual_hint, color)
    elif level == 'cellules':
        wireframe = generate_wireframe_cellules(visual_hint, color)
    else:
        wireframe = generate_wireframe_general(visual_hint, color)
    
    # Afficher la description si elle existe (pour corps et organes)
    desc_html = ''
    if description and level in ['corps', 'organes']:
        desc_html = f'<div style="font-size:10px;color:#64748b;margin-top:4px;line-height:1.3;">{description}</div>'
    
    return f'''
    <div class="comp-card" onclick="toggleCheckbox('comp-{comp_id}')" data-corps="{comp.get('corps', 'all')}">
        {wireframe}
        <div class="comp-info">
            <div class="comp-name" title="{name}">{name}</div>
            {desc_html}
            <div class="comp-endpoint" title="{endpoint}">{endpoint}</div>
        </div>
        <div class="comp-footer">
            <span class="comp-method" style="background:{color}20;color:{color};">{method}</span>
            <input type="checkbox" id="comp-{comp_id}" class="comp-checkbox" value="{comp_id}" onclick="event.stopPropagation();updateValidateButton()">
        </div>
    </div>
    '''


def collect_components_by_level(genome):
    """Collecte tous les composants par niveau avec mapping user-friendly"""
    corps_list = []
    organes_list = []
    cellules_list = []
    atomes_list = []
    
    for phase in genome.get('n0_phases', []):
        phase_id = phase.get('id', 'unknown')
        corps_info = CORPS_MAPPING.get(phase_id, {'name': phase.get('name', 'Unknown'), 'hint': 'dashboard', 'desc': ''})
        
        # Créer le composant Corps
        corps_comp = {
            'id': phase_id,
            'name': corps_info['name'],
            'endpoint': f'/corps/{phase_id}',
            'method': 'GET',
            'visual_hint': corps_info['hint'],
            'corps': phase_id.replace('n0_', ''),
            'description': corps_info['desc']
        }
        corps_list.append(corps_comp)
        
        for section in phase.get('n1_sections', []):
            section_id = section.get('id', 'unknown')
            organe_info = ORGANES_MAPPING.get(section_id, {'name': section.get('name', 'Unknown'), 'hint': 'detail-card', 'desc': ''})
            
            # Créer le composant Organe
            organe_comp = {
                'id': section_id,
                'name': organe_info['name'],
                'endpoint': f'/organe/{section_id}',
                'method': 'GET',
                'visual_hint': organe_info['hint'],
                'corps': phase_id.replace('n0_', ''),
                'description': organe_info['desc']
            }
            if not any(o['id'] == section_id for o in organes_list):
                organes_list.append(organe_comp)
            
            for feature in section.get('n2_features', []):
                feature_id = feature.get('id', 'unknown')
                cellule_info = CELLULES_MAPPING.get(feature_id, {'name': feature.get('name', 'Unknown'), 'hint': 'detail-card'})
                
                # Créer le composant Cellule
                cellule_comp = {
                    'id': feature_id,
                    'name': cellule_info['name'],
                    'endpoint': f'/cellule/{feature_id}',
                    'method': 'GET',
                    'visual_hint': cellule_info['hint'],
                    'corps': phase_id.replace('n0_', ''),
                    'description': ''
                }
                if not any(c['id'] == feature_id for c in cellules_list):
                    cellules_list.append(cellule_comp)
                
                for comp in feature.get('n3_components', []):
                    comp['corps'] = phase_id.replace('n0_', '')
                    comp['organe_id'] = section_id
                    comp['cellule_id'] = feature_id
                    atomes_list.append(comp)
    
    return corps_list, organes_list, cellules_list, atomes_list


def generate_html(genome):
    """Génère la page HTML complète avec collapses Wingdings3"""
    
    corps_list, organes_list, cellules_list, atomes_list = collect_components_by_level(genome)
    
    total = len(atomes_list)
    confidence = int(genome.get('metadata', {}).get('confidence_global', 0.85) * 100)
    
    # Générer les cards par niveau
    corps_cards = ''.join(generate_component_card(c, 'corps') for c in corps_list)
    organes_cards = ''.join(generate_component_card(o, 'organes') for o in organes_list)
    cellules_cards = ''.join(generate_component_card(c, 'cellules') for c in cellules_list)
    atomes_cards = ''.join(generate_component_card(a, 'atomes') for a in atomes_list)
    
    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HoméOS - Genome Viewer (Port 9998)</title>
    <style>
        @font-face {{
            font-family: 'Wingdings3';
            src: url('/fonts/Wingdings3.woff2') format('woff2'),
                 url('/fonts/Wingdings3.woff') format('woff');
            font-weight: normal;
            font-style: normal;
            font-display: swap;
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; overflow: hidden; background: #f8fafc; }}
        
        /* Wingdings arrows */
        .wingding-arrow {{
            font-family: 'Wingdings3', sans-serif;
            font-size: 14px;
            display: inline-block;
            transition: transform 0.2s;
        }}
        .wingding-arrow.collapsed {{
            transform: rotate(-90deg);
        }}
        
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
        .K {{ color: #000; font-weight: 500; }}
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
        
        /* Collapsible Section */
        .section {{ 
            margin-bottom: 20px; 
            background: white;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            overflow: hidden;
        }}
        
        .section-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px 20px;
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            cursor: pointer;
            transition: all 0.2s;
            user-select: none;
        }}
        .section-header:hover {{
            background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        }}
        
        .section-title {{ 
            font-size: 14px; 
            font-weight: 700; 
            color: #1e293b;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .section-count {{
            font-size: 12px;
            color: #64748b;
            font-weight: 500;
            background: white;
            padding: 2px 10px;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
        }}
        .section-desc {{
            font-size: 12px;
            color: #64748b;
            margin-left: auto;
            font-style: italic;
        }}
        
        .section-content {{
            padding: 20px;
            transition: all 0.3s ease;
        }}
        .section-content.collapsed {{
            display: none;
        }}
        
        .row {{ 
            display: flex; 
            gap: 16px; 
            flex-wrap: wrap;
        }}
        
        .comp-card {{
            width: calc(20% - 13px);
            min-width: 180px;
            max-width: 240px;
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
        
        .comp-info {{ padding: 12px 14px; border-bottom: 1px solid #f1f5f9; min-height: 70px; }}
        .comp-name {{ 
            font-size: 13px; 
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
            padding: 10px 14px; 
            background: #fafafa;
        }}
        .comp-method {{ 
            font-size: 10px; 
            font-weight: 700; 
            text-transform: uppercase;
            padding: 3px 10px; 
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
        
        /* Style Choice Section */
        .style-option-card {{
            width: 450px;
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 16px;
            padding: 24px;
            transition: all 0.3s;
        }}
        .style-option-card:hover {{
            border-color: #7aca6a;
            box-shadow: 0 8px 24px rgba(122,202,106,0.15);
        }}
        .style-option-header {{
            font-size: 18px;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 20px;
            text-align: center;
        }}
        .upload-zone {{
            border: 2px dashed #cbd5e1;
            border-radius: 12px;
            padding: 40px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .upload-zone:hover {{
            border-color: #7aca6a;
            background: #f0fdf4;
        }}
        .styles-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
        }}
        .style-card {{
            height: 90px;
            background: #f8fafc;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s;
            overflow: hidden;
            padding: 0;
        }}
        .style-card:hover {{
            border-color: #7aca6a;
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        .style-card.selected {{
            border-color: #7aca6a;
            box-shadow: 0 0 0 3px rgba(122,202,106,0.3);
        }}
        
        /* Style Previews - Classy & Elegant */
        .style-preview {{
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 10px;
        }}
        .style-preview .sp-title {{
            font-size: 11px;
            font-weight: 600;
            margin-bottom: 3px;
            letter-spacing: 0.3px;
        }}
        .style-preview .sp-sub {{
            font-size: 8px;
            font-weight: 400;
            opacity: 0.7;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}
        
        /* Minimal: Refined simplicity */
        .minimal-preview {{
            background: #fafafa;
            color: #525252;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }}
        .minimal-preview .sp-title {{ 
            font-weight: 400; 
            letter-spacing: 1px;
            text-transform: uppercase;
            font-size: 10px;
        }}
        
        /* Corporate: Executive elegance */
        .corporate-preview {{
            background: #f8fafc;
            color: #1e3a5f;
            font-family: 'Times New Roman', Times, serif;
        }}
        .corporate-preview .sp-title {{ 
            font-weight: 600; 
            letter-spacing: 0.5px; 
            font-size: 12px;
        }}
        
        /* Creative: Artistic sophistication */
        .creative-preview {{
            background: #fef7ed;
            color: #9a3412;
            font-family: Georgia, 'Palatino', serif;
        }}
        .creative-preview .sp-title {{ 
            font-weight: 500; 
            font-style: italic;
            letter-spacing: 0.5px;
        }}
        
        /* Tech: Precision engineering */
        .tech-preview {{
            background: #f1f5f9;
            color: #334155;
            font-family: 'SF Mono', 'Monaco', monospace;
        }}
        .tech-preview .sp-title {{ 
            font-weight: 500; 
            letter-spacing: 1px;
            font-size: 10px;
        }}
        
        /* Elegant: Timeless luxury */
        .elegant-preview {{
            background: #fffbeb;
            color: #713f12;
            font-family: 'Times New Roman', serif;
        }}
        .elegant-preview .sp-title {{ 
            font-weight: 400; 
            letter-spacing: 1.5px;
            text-transform: uppercase;
            font-size: 10px;
        }}
        
        /* Playful: Approachable warmth */
        .playful-preview {{
            background: #fdf4ff;
            color: #7c3aed;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        .playful-preview .sp-title {{ 
            font-weight: 500; 
            letter-spacing: 0.5px;
        }}
        
        /* Dark: Understated sophistication */
        .dark-preview {{
            background: #27272a;
            color: #d4d4d8;
            font-family: -apple-system, sans-serif;
        }}
        .dark-preview .sp-title {{ 
            font-weight: 400; 
            letter-spacing: 1px;
            text-transform: uppercase;
            font-size: 10px;
        }}
        
        /* Colorful: Curated harmony */
        .colorful-preview {{
            background: linear-gradient(135deg, #ddd6fe 0%, #fce7f3 50%, #fed7aa 100%);
            color: #581c87;
            font-family: -apple-system, sans-serif;
        }}
        .colorful-preview .sp-title {{ 
            font-weight: 600;
            letter-spacing: 0.5px;
        }}
        
        /* Section header emoji removal */
        .section-title {{ font-size: 14px; font-weight: 700; }}
        .style-option-header {{ font-size: 18px; font-weight: 700; color: #1e293b; margin-bottom: 20px; text-align: center; }}
        .btn-secondary {{
            margin-top: 12px;
            padding: 8px 24px;
            background: #f1f5f9;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            color: #475569;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .btn-secondary:hover {{
            background: #e2e8f0;
        }}
        
        @media (max-width: 1400px) {{ 
            .comp-card {{ width: calc(25% - 12px); }} 
        }}
        @media (max-width: 1100px) {{ 
            .comp-card {{ width: calc(33.333% - 11px); }} 
        }}
        @media (max-width: 900px) {{ 
            .comp-card {{ width: calc(50% - 8px); }} 
        }}

        /* ========================================
           STENCILER SECTION (extension)
           ======================================== */
        
        #stenciler-section {{
            display: block;
            position: sticky;
            top: 0;
            z-index: 100;
            background: #fff;
            border-bottom: 1px solid #e2e8f0;
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
    </style>
</head>
<body>
    <div class="tabs">
        <div class="tab" onclick="switchTab(this, 'brs')">Brainstorm</div>
        <div class="tab" onclick="switchTab(this, 'bkd')">Backend</div>
        <div class="tab active current" onclick="switchTab(this, 'frd')">Frontend</div>
        <div class="tab" onclick="switchTab(this, 'dpl')">Deploy</div>
    </div>

    <div class="main">
        <aside class="sidebar">
            <div class="sidebar-header">
                <div class="sidebar-title">Homé<span class="K">OS</span></div>
                <div class="sidebar-subtitle">Architecture Genome v3.1</div>
            </div>
            <div class="sidebar-section">
                <div class="sidebar-label">Qu'est-ce que le Genome ?</div>
                <div style="font-size: 12px; color: #64748b; line-height: 1.6; margin-bottom: 12px;">
                    Le <strong>Genome</strong> est le plan complet de votre projet. 
                    Comme l'ADN d'un être vivant, il décrit chaque partie : 
                    les <em>grandes étapes</em> (Corps), les <em>fonctions</em> (Organes), 
                    les <em>actions</em> (Cellules) et les <em>éléments d'interface</em> (Atomes).
                </div>
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
                        <div class="stat-label">fonctions</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" style="color:#64748b;">{len(cellules_list)}</div>
                        <div class="stat-label">actions</div>
                    </div>
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
                    <button id="validate-btn" class="validate-btn" disabled onclick="scrollToStyleChoice()">Valider (0)</button>
                </div>
                
                <h1>Architecture Genome</h1>
                <p class="subtitle">Visualisation hiérarchique avec explications</p>
                
                <!-- ROW 1: Corps (Les 4 grandes étapes) -->
                <div class="section">
                    <div class="section-header" onclick="toggleSection(this)">
                        <span class="wingding-arrow"></span>
                        <span class="section-title">🎯 Les 4 Grandes Étapes (Corps)</span>
                        <span class="section-count">{len(corps_list)}</span>
                        <span class="section-desc">Vision stratégique de votre projet</span>
                    </div>
                    <div class="section-content" id="section-corps">
                        <div class="row">
                            {corps_cards}
                        </div>
                    </div>
                </div>
                
                <!-- ROW 2: Organes (Les fonctions principales) -->
                <div class="section">
                    <div class="section-header" onclick="toggleSection(this)">
                        <span class="wingding-arrow"></span>
                        <span class="section-title">🫀 Les Fonctions Principales (Organes)</span>
                        <span class="section-count">{len(organes_list)}</span>
                        <span class="section-desc">Ce que fait chaque partie du système</span>
                    </div>
                    <div class="section-content" id="section-organes">
                        <div class="row">
                            {organes_cards}
                        </div>
                    </div>
                </div>
                
                <!-- ROW 3: Cellules (Les actions concrètes) -->
                <div class="section">
                    <div class="section-header" onclick="toggleSection(this)">
                        <span class="wingding-arrow"></span>
                        <span class="section-title">🔬 Les Actions Concrètes (Cellules)</span>
                        <span class="section-count">{len(cellules_list)}</span>
                        <span class="section-desc">Tâches spécifiques à réaliser</span>
                    </div>
                    <div class="section-content" id="section-cellules">
                        <div class="row">
                            {cellules_cards}
                        </div>
                    </div>
                </div>
                
                <!-- ROW 4: Atomes (Les composants techniques) -->
                <div class="section">
                    <div class="section-header" onclick="toggleSection(this)">
                        <span class="wingding-arrow"></span>
                        <span class="section-title">⚛️ Les Composants Techniques (Atomes)</span>
                        <span class="section-count">{total}</span>
                        <span class="section-desc">Éléments finaux de l'interface</span>
                    </div>
                    <div class="section-content" id="section-atomes">
                        <div class="row">
                            {atomes_cards}
                        </div>
                    </div>
                </div>
                
                <!-- STEP 2: Style Choice (caché par défaut) -->
                <div class="section" id="section-style-choice" style="display: none; margin-top: 40px;">
                    <div class="section-header" style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);">
                        <span class="wingding-arrow"></span>
                        <span class="section-title">Etape 2 : Choisir le Style</span>
                        <span class="section-desc">Selectionnez une option pour continuer</span>
                    </div>
                    <div class="section-content">
                        <div class="row" style="justify-content: center; gap: 32px;">
                            
                            <!-- Option A: Upload -->
                            <div class="style-option-card">
                                <div class="style-option-header">Importer ma Maquette</div>
                                <div class="upload-zone" id="upload-zone">
                                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.5" style="margin-bottom: 12px;">
                                        <path d="M12 16V4m0 0l-4 4m4-4l4 4M4 17v2a2 2 0 002 2h12a2 2 0 002-2v-2"/>
                                    </svg>
                                    <p style="font-size: 14px; color: #64748b; margin-bottom: 8px;">
                                        Glisser-déposer ou cliquer
                                    </p>
                                    <input type="file" id="file-input" accept="image/*" style="display: none;">
                                    <button class="btn-secondary" onclick="document.getElementById('file-input').click()">
                                        Parcourir
                                    </button>
                                </div>
                            </div>
                            
                            <!-- Option B: Styles par défaut -->
                            <div class="style-option-card" style="width: 500px;">
                                <div class="style-option-header">Choisir un Style</div>
                                <div class="styles-grid">
                                    <div class="style-card" data-style="minimal">
                                        <div class="style-preview minimal-preview">
                                            <span class="sp-title">Minimal</span>
                                            <span class="sp-sub">Clean & Light</span>
                                        </div>
                                    </div>
                                    <div class="style-card" data-style="corporate">
                                        <div class="style-preview corporate-preview">
                                            <span class="sp-title">Corporate</span>
                                            <span class="sp-sub">Professional</span>
                                        </div>
                                    </div>
                                    <div class="style-card" data-style="creative">
                                        <div class="style-preview creative-preview">
                                            <span class="sp-title">Créatif</span>
                                            <span class="sp-sub">Bold & Art</span>
                                        </div>
                                    </div>
                                    <div class="style-card" data-style="tech">
                                        <div class="style-preview tech-preview">
                                            <span class="sp-title">Tech</span>
                                            <span class="sp-sub">Modern Code</span>
                                        </div>
                                    </div>
                                    <div class="style-card" data-style="elegant">
                                        <div class="style-preview elegant-preview">
                                            <span class="sp-title">Élégant</span>
                                            <span class="sp-sub">Refined</span>
                                        </div>
                                    </div>
                                    <div class="style-card" data-style="playful">
                                        <div class="style-preview playful-preview">
                                            <span class="sp-title">Ludique</span>
                                            <span class="sp-sub">Friendly</span>
                                        </div>
                                    </div>
                                    <div class="style-card" data-style="dark">
                                        <div class="style-preview dark-preview">
                                            <span class="sp-title">Dark</span>
                                            <span class="sp-sub">Night Mode</span>
                                        </div>
                                    </div>
                                    <div class="style-card" data-style="colorful">
                                        <div class="style-preview colorful-preview">
                                            <span class="sp-title">Coloré</span>
                                            <span class="sp-sub">Vibrant</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                        </div>
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
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            element.classList.add('active');
            
            const corpsFilter = tabMapping[tab];
            const cards = document.querySelectorAll('.comp-card');
            
            cards.forEach(card => {{
                if (corpsFilter === 'all' || card.dataset.corps === corpsFilter) {{
                    card.classList.remove('hidden');
                }} else {{
                    card.classList.add('hidden');
                }}
            }});
            
            updateValidateButton();
        }}
        
        function toggleSection(header) {{
            const arrow = header.querySelector('.wingding-arrow');
            const content = header.nextElementSibling;
            
            arrow.classList.toggle('collapsed');
            content.classList.toggle('collapsed');
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
        
        // Fonction de scroll vers le choix de style
        function scrollToStyleChoice() {{
            const styleSection = document.getElementById('section-style-choice');
            if (styleSection) {{
                // Afficher la section
                styleSection.style.display = 'block';
                
                // Scroll smooth vers la section
                setTimeout(() => {{
                    styleSection.scrollIntoView({{
                        behavior: 'smooth',
                        block: 'start'
                    }});
                }}, 100);
            }}
        }}
        
        // Gestion upload de fichier
        document.addEventListener('DOMContentLoaded', () => {{
            const uploadZone = document.getElementById('upload-zone');
            const fileInput = document.getElementById('file-input');
            
            if (uploadZone && fileInput) {{
                uploadZone.addEventListener('dragover', (e) => {{
                    e.preventDefault();
                    uploadZone.style.borderColor = '#7aca6a';
                    uploadZone.style.background = '#f0fdf4';
                }});
                
                uploadZone.addEventListener('dragleave', () => {{
                    uploadZone.style.borderColor = '#cbd5e1';
                    uploadZone.style.background = 'transparent';
                }});
                
                uploadZone.addEventListener('drop', (e) => {{
                    e.preventDefault();
                    const files = e.dataTransfer.files;
                    if (files.length > 0) {{
                        handleFileUpload(files[0]);
                    }}
                }});
                
                fileInput.addEventListener('change', (e) => {{
                    if (e.target.files.length > 0) {{
                        handleFileUpload(e.target.files[0]);
                    }}
                }});
            }}
            
            // Gestion sélection de style → Sauvegarde + Redirect vers /stenciler
            document.querySelectorAll('.style-card').forEach(card => {{
                card.addEventListener('click', () => {{
                    // Désélectionner les autres
                    document.querySelectorAll('.style-card').forEach(c => c.classList.remove('selected'));
                    // Sélectionner celui-ci
                    card.classList.add('selected');
                    
                    const selectedStyle = card.dataset.style;
                    console.log('Style sélectionné:', selectedStyle);
                    
                    // Sauvegarder dans localStorage pour /stenciler (le genome sera fetché via /api/genome)
                    localStorage.setItem('aetherflow_selected_style', selectedStyle);
                    localStorage.setItem('aetherflow_timestamp', Date.now().toString());
                    
                    console.log('💾 Données sauvegardées, redirection vers /stenciler...');
                    
                    // Redirection vers /stenciler
                    window.location.href = '/stenciler';
                }});
            }});
        }});
        
        function handleFileUpload(file) {{
            console.log('Fichier uploadé:', file.name);
            alert(`Maquette "${{file.name}}" uploadée !\\nAnalyse Gemini Vision à implémenter...`);
        }}

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
    </script>
</body>
</html>'''


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Route pour les fonts Wingdings3
        if self.path == '/fonts/Wingdings3.woff2':
            self.serve_font('Wingdings3.woff2')
            return
        elif self.path == '/fonts/Wingdings3.woff':
            self.serve_font('Wingdings3.woff')
            return
        
        # Route principale
        if self.path == '/' or self.path.startswith('/studio'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            genome = load_genome()
            html = generate_html(genome)
            self.wfile.write(html.encode('utf-8'))
            return
        
        # Route Stenciler (nouveau layout)
        if self.path == '/stenciler':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            stenciler_html = generate_stenciler_html()
            self.wfile.write(stenciler_html.encode('utf-8'))
            return
        
        # Route API pour le genome
        if self.path == '/api/genome':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            genome = load_genome()
            self.wfile.write(json.dumps(genome).encode('utf-8'))
            return
        
        # Route pour les fichiers statiques (CSS, JS)
        if self.path.startswith('/static/'):
            self.serve_static(self.path[8:])  # Enlever '/static/'
            return
        
        self.send_response(404)
        self.end_headers()
    
    def serve_font(self, font_name):
        """Sert les fichiers de font"""
        font_path = os.path.join(FONTS_DIR, font_name)
        if not os.path.exists(font_path):
            # Essayer depuis le répertoire courant
            cwd = os.path.dirname(os.path.abspath(__file__))
            font_path = os.path.join(cwd, FONTS_DIR, font_name)
        
        if os.path.exists(font_path):
            self.send_response(200)
            if font_name.endswith('.woff2'):
                self.send_header('Content-type', 'font/woff2')
            else:
                self.send_header('Content-type', 'font/woff')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            with open(font_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass
    
    def serve_static(self, filepath):
        """Sert les fichiers statiques (CSS, JS)"""
        try:
            cwd = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(cwd, 'static', filepath)
            print(f"📁 Serving static: {filepath} -> {full_path}")
            print(f"   Exists: {os.path.exists(full_path)}, Is file: {os.path.isfile(full_path) if os.path.exists(full_path) else 'N/A'}")

            if os.path.exists(full_path) and os.path.isfile(full_path):
                self.send_response(200)
                if filepath.endswith('.css'):
                    content_type = 'text/css'
                elif filepath.endswith('.js'):
                    content_type = 'application/javascript'
                elif filepath.endswith('.json'):
                    content_type = 'application/json'
                else:
                    content_type = 'text/plain'
                print(f"   Content-Type: {content_type}")
                self.send_header('Content-type', content_type)
                self.end_headers()
                with open(full_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                print(f"   ❌ File not found: {full_path}")
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.send_response(500)
            self.end_headers()


def generate_html(genome):
    """Génère la page HTML complète avec collapses Wingdings3"""
    
    corps_list, organes_list, cellules_list, atomes_list = collect_components_by_level(genome)
    
    total = len(atomes_list)
    confidence = int(genome.get('metadata', {}).get('confidence_global', 0.85) * 100)
    
    # Générer les cards par niveau
    corps_cards = ''.join(generate_component_card(c, 'corps') for c in corps_list)
    organes_cards = ''.join(generate_component_card(o, 'organes') for o in organes_list)
    cellules_cards = ''.join(generate_component_card(c, 'cellules') for c in cellules_list)
    atomes_cards = ''.join(generate_component_card(a, 'atomes') for a in atomes_list)
    
    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HoméOS - Genome Viewer (Port 9998)</title>
    <style>
        @font-face {{
            font-family: 'Wingdings3';
            src: url('/fonts/Wingdings3.woff2') format('woff2'),
                 url('/fonts/Wingdings3.woff') format('woff');
            font-weight: normal;
            font-style: normal;
            font-display: swap;
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; overflow: hidden; background: #f8fafc; }}
        
        /* Wingdings arrows */
        .wingding-arrow {{
            font-family: 'Wingdings3', sans-serif;
            font-size: 14px;
            display: inline-block;
            transition: transform 0.2s;
        }}
        .wingding-arrow.collapsed {{
            transform: rotate(-90deg);
        }}
        
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
        .K {{ color: #000; font-weight: 500; }}
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
        
        /* Collapsible Section */
        .section {{ 
            margin-bottom: 20px; 
            background: white;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            overflow: hidden;
        }}
        
        .section-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px 20px;
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            cursor: pointer;
            transition: all 0.2s;
            user-select: none;
        }}
        .section-header:hover {{
            background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        }}
        
        .section-title {{ 
            font-size: 14px; 
            font-weight: 700; 
            color: #1e293b;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .section-count {{
            font-size: 12px;
            color: #64748b;
            font-weight: 500;
            background: white;
            padding: 2px 10px;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
        }}
        .section-desc {{
            font-size: 12px;
            color: #64748b;
            margin-left: auto;
            font-style: italic;
        }}
        
        .section-content {{
            padding: 20px;
            transition: all 0.3s ease;
        }}
        .section-content.collapsed {{
            display: none;
        }}
        
        .row {{ 
            display: flex; 
            gap: 16px; 
            flex-wrap: wrap;
        }}
        
        .comp-card {{
            width: calc(20% - 13px);
            min-width: 180px;
            max-width: 240px;
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
        
        .comp-info {{ padding: 12px 14px; border-bottom: 1px solid #f1f5f9; min-height: 70px; }}
        .comp-name {{ 
            font-size: 13px; 
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
            padding: 10px 14px; 
            background: #fafafa;
        }}
        .comp-method {{ 
            font-size: 10px; 
            font-weight: 700; 
            text-transform: uppercase;
            padding: 3px 10px; 
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
        
        /* Style Choice Section */
        .style-option-card {{
            width: 450px;
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 16px;
            padding: 24px;
            transition: all 0.3s;
        }}
        .style-option-card:hover {{
            border-color: #7aca6a;
            box-shadow: 0 8px 24px rgba(122,202,106,0.15);
        }}
        .style-option-header {{
            font-size: 18px;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 20px;
            text-align: center;
        }}
        .upload-zone {{
            border: 2px dashed #cbd5e1;
            border-radius: 12px;
            padding: 40px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .upload-zone:hover {{
            border-color: #7aca6a;
            background: #f0fdf4;
        }}
        .styles-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
        }}
        .style-card {{
            height: 90px;
            background: #f8fafc;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s;
            overflow: hidden;
            padding: 0;
        }}
        .style-card:hover {{
            border-color: #7aca6a;
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        .style-card.selected {{
            border-color: #7aca6a;
            box-shadow: 0 0 0 3px rgba(122,202,106,0.3);
        }}
        
        /* Style Previews - Classy & Elegant */
        .style-preview {{
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 10px;
        }}
        .style-preview .sp-title {{
            font-size: 11px;
            font-weight: 600;
            margin-bottom: 3px;
            letter-spacing: 0.3px;
        }}
        .style-preview .sp-sub {{
            font-size: 8px;
            font-weight: 400;
            opacity: 0.7;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}
        
        /* Minimal: Refined simplicity */
        .minimal-preview {{
            background: #fafafa;
            color: #525252;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }}
        .minimal-preview .sp-title {{ 
            font-weight: 400; 
            letter-spacing: 1px;
            text-transform: uppercase;
            font-size: 10px;
        }}
        
        /* Corporate: Executive elegance */
        .corporate-preview {{
            background: #f8fafc;
            color: #1e3a5f;
            font-family: 'Times New Roman', Times, serif;
        }}
        .corporate-preview .sp-title {{ 
            font-weight: 600; 
            letter-spacing: 0.5px; 
            font-size: 12px;
        }}
        
        /* Creative: Artistic sophistication */
        .creative-preview {{
            background: #fef7ed;
            color: #9a3412;
            font-family: Georgia, 'Palatino', serif;
        }}
        .creative-preview .sp-title {{ 
            font-weight: 500; 
            font-style: italic;
            letter-spacing: 0.5px;
        }}
        
        /* Tech: Precision engineering */
        .tech-preview {{
            background: #f1f5f9;
            color: #334155;
            font-family: 'SF Mono', 'Monaco', monospace;
        }}
        .tech-preview .sp-title {{ 
            font-weight: 500; 
            letter-spacing: 1px;
            font-size: 10px;
        }}
        
        /* Elegant: Timeless luxury */
        .elegant-preview {{
            background: #fffbeb;
            color: #713f12;
            font-family: 'Times New Roman', serif;
        }}
        .elegant-preview .sp-title {{ 
            font-weight: 400; 
            letter-spacing: 1.5px;
            text-transform: uppercase;
            font-size: 10px;
        }}
        
        /* Playful: Approachable warmth */
        .playful-preview {{
            background: #fdf4ff;
            color: #7c3aed;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        .playful-preview .sp-title {{ 
            font-weight: 500; 
            letter-spacing: 0.5px;
        }}
        
        /* Dark: Understated sophistication */
        .dark-preview {{
            background: #27272a;
            color: #d4d4d8;
            font-family: -apple-system, sans-serif;
        }}
        .dark-preview .sp-title {{ 
            font-weight: 400; 
            letter-spacing: 1px;
            text-transform: uppercase;
            font-size: 10px;
        }}
        
        /* Colorful: Curated harmony */
        .colorful-preview {{
            background: linear-gradient(135deg, #ddd6fe 0%, #fce7f3 50%, #fed7aa 100%);
            color: #581c87;
            font-family: -apple-system, sans-serif;
        }}
        .colorful-preview .sp-title {{ 
            font-weight: 600;
            letter-spacing: 0.5px;
        }}
        
        /* Section header emoji removal */
        .section-title {{ font-size: 14px; font-weight: 700; }}
        .style-option-header {{ font-size: 18px; font-weight: 700; color: #1e293b; margin-bottom: 20px; text-align: center; }}
        .btn-secondary {{
            margin-top: 12px;
            padding: 8px 24px;
            background: #f1f5f9;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            color: #475569;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .btn-secondary:hover {{
            background: #e2e8f0;
        }}
        
        @media (max-width: 1400px) {{ 
            .comp-card {{ width: calc(25% - 12px); }} 
        }}
        @media (max-width: 1100px) {{ 
            .comp-card {{ width: calc(33.333% - 11px); }} 
        }}
        @media (max-width: 900px) {{ 
            .comp-card {{ width: calc(50% - 8px); }} 
        }}

        /* ========================================
           STENCILER SECTION (extension)
           ======================================== */
        
        #stenciler-section {{
            display: block;
            position: sticky;
            top: 0;
            z-index: 100;
            background: #fff;
            border-bottom: 1px solid #e2e8f0;
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
    </style>
</head>
<body>
    <div class="tabs">
        <div class="tab" onclick="switchTab(this, 'brs')">Brainstorm</div>
        <div class="tab" onclick="switchTab(this, 'bkd')">Backend</div>
        <div class="tab active current" onclick="switchTab(this, 'frd')">Frontend</div>
        <div class="tab" onclick="switchTab(this, 'dpl')">Deploy</div>
    </div>

    <div class="main">
        <aside class="sidebar">
            <div class="sidebar-header">
                <div class="sidebar-title">Homé<span class="K">OS</span></div>
                <div class="sidebar-subtitle">Architecture Genome v3.1</div>
            </div>
            <div class="sidebar-section">
                <div class="sidebar-label">Qu'est-ce que le Genome ?</div>
                <div style="font-size: 12px; color: #64748b; line-height: 1.6; margin-bottom: 12px;">
                    Le <strong>Genome</strong> est le plan complet de votre projet. 
                    Comme l'ADN d'un être vivant, il décrit chaque partie : 
                    les <em>grandes étapes</em> (Corps), les <em>fonctions</em> (Organes), 
                    les <em>actions</em> (Cellules) et les <em>éléments d'interface</em> (Atomes).
                </div>
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
                        <div class="stat-label">fonctions</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" style="color:#64748b;">{len(cellules_list)}</div>
                        <div class="stat-label">actions</div>
                    </div>
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
                    <button id="validate-btn" class="validate-btn" disabled onclick="scrollToStyleChoice()">Valider (0)</button>
                </div>
                
                <h1>Architecture Genome</h1>
                <p class="subtitle">Visualisation hiérarchique avec explications</p>
                
                <!-- ROW 1: Corps (Les 4 grandes étapes) -->
                <div class="section">
                    <div class="section-header" onclick="toggleSection(this)">
                        <span class="wingding-arrow"></span>
                        <span class="section-title">🎯 Les 4 Grandes Étapes (Corps)</span>
                        <span class="section-count">{len(corps_list)}</span>
                        <span class="section-desc">Vision stratégique de votre projet</span>
                    </div>
                    <div class="section-content" id="section-corps">
                        <div class="row">
                            {corps_cards}
                        </div>
                    </div>
                </div>
                
                <!-- ROW 2: Organes (Les fonctions principales) -->
                <div class="section">
                    <div class="section-header" onclick="toggleSection(this)">
                        <span class="wingding-arrow"></span>
                        <span class="section-title">🫀 Les Fonctions Principales (Organes)</span>
                        <span class="section-count">{len(organes_list)}</span>
                        <span class="section-desc">Ce que fait chaque partie du système</span>
                    </div>
                    <div class="section-content" id="section-organes">
                        <div class="row">
                            {organes_cards}
                        </div>
                    </div>
                </div>
                
                <!-- ROW 3: Cellules (Les actions concrètes) -->
                <div class="section">
                    <div class="section-header" onclick="toggleSection(this)">
                        <span class="wingding-arrow"></span>
                        <span class="section-title">🔬 Les Actions Concrètes (Cellules)</span>
                        <span class="section-count">{len(cellules_list)}</span>
                        <span class="section-desc">Tâches spécifiques à réaliser</span>
                    </div>
                    <div class="section-content" id="section-cellules">
                        <div class="row">
                            {cellules_cards}
                        </div>
                    </div>
                </div>
                
                <!-- ROW 4: Atomes (Les composants techniques) -->
                <div class="section">
                    <div class="section-header" onclick="toggleSection(this)">
                        <span class="wingding-arrow"></span>
                        <span class="section-title">⚛️ Les Composants Techniques (Atomes)</span>
                        <span class="section-count">{total}</span>
                        <span class="section-desc">Éléments finaux de l'interface</span>
                    </div>
                    <div class="section-content" id="section-atomes">
                        <div class="row">
                            {atomes_cards}
                        </div>
                    </div>
                </div>
                
                <!-- STEP 2: Style Choice (caché par défaut) -->
                <div class="section" id="section-style-choice" style="display: none; margin-top: 40px;">
                    <div class="section-header" style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);">
                        <span class="wingding-arrow"></span>
                        <span class="section-title">Etape 2 : Choisir le Style</span>
                        <span class="section-desc">Selectionnez une option pour continuer</span>
                    </div>
                    <div class="section-content">
                        <div class="row" style="justify-content: center; gap: 32px;">
                            
                            <!-- Option A: Upload -->
                            <div class="style-option-card">
                                <div class="style-option-header">Importer ma Maquette</div>
                                <div class="upload-zone" id="upload-zone">
                                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.5" style="margin-bottom: 12px;">
                                        <path d="M12 16V4m0 0l-4 4m4-4l4 4M4 17v2a2 2 0 002 2h12a2 2 0 002-2v-2"/>
                                    </svg>
                                    <p style="font-size: 14px; color: #64748b; margin-bottom: 8px;">
                                        Glisser-déposer ou cliquer
                                    </p>
                                    <input type="file" id="file-input" accept="image/*" style="display: none;">
                                    <button class="btn-secondary" onclick="document.getElementById('file-input').click()">
                                        Parcourir
                                    </button>
                                </div>
                            </div>
                            
                            <!-- Option B: Styles par défaut -->
                            <div class="style-option-card" style="width: 500px;">
                                <div class="style-option-header">Choisir un Style</div>
                                <div class="styles-grid">
                                    <div class="style-card" data-style="minimal">
                                        <div class="style-preview minimal-preview">
                                            <span class="sp-title">Minimal</span>
                                            <span class="sp-sub">Clean & Light</span>
                                        </div>
                                    </div>
                                    <div class="style-card" data-style="corporate">
                                        <div class="style-preview corporate-preview">
                                            <span class="sp-title">Corporate</span>
                                            <span class="sp-sub">Professional</span>
                                        </div>
                                    </div>
                                    <div class="style-card" data-style="creative">
                                        <div class="style-preview creative-preview">
                                            <span class="sp-title">Créatif</span>
                                            <span class="sp-sub">Bold & Art</span>
                                        </div>
                                    </div>
                                    <div class="style-card" data-style="tech">
                                        <div class="style-preview tech-preview">
                                            <span class="sp-title">Tech</span>
                                            <span class="sp-sub">Modern Code</span>
                                        </div>
                                    </div>
                                    <div class="style-card" data-style="elegant">
                                        <div class="style-preview elegant-preview">
                                            <span class="sp-title">Élégant</span>
                                            <span class="sp-sub">Refined</span>
                                        </div>
                                    </div>
                                    <div class="style-card" data-style="playful">
                                        <div class="style-preview playful-preview">
                                            <span class="sp-title">Ludique</span>
                                            <span class="sp-sub">Friendly</span>
                                        </div>
                                    </div>
                                    <div class="style-card" data-style="dark">
                                        <div class="style-preview dark-preview">
                                            <span class="sp-title">Dark</span>
                                            <span class="sp-sub">Night Mode</span>
                                        </div>
                                    </div>
                                    <div class="style-card" data-style="colorful">
                                        <div class="style-preview colorful-preview">
                                            <span class="sp-title">Coloré</span>
                                            <span class="sp-sub">Vibrant</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                        </div>
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
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            element.classList.add('active');
            
            const corpsFilter = tabMapping[tab];
            const cards = document.querySelectorAll('.comp-card');
            
            cards.forEach(card => {{
                if (corpsFilter === 'all' || card.dataset.corps === corpsFilter) {{
                    card.classList.remove('hidden');
                }} else {{
                    card.classList.add('hidden');
                }}
            }});
            
            updateValidateButton();
        }}
        
        function toggleSection(header) {{
            const arrow = header.querySelector('.wingding-arrow');
            const content = header.nextElementSibling;
            
            arrow.classList.toggle('collapsed');
            content.classList.toggle('collapsed');
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
        
        // Fonction de scroll vers le choix de style
        function scrollToStyleChoice() {{
            const styleSection = document.getElementById('section-style-choice');
            if (styleSection) {{
                // Afficher la section
                styleSection.style.display = 'block';
                
                // Scroll smooth vers la section
                setTimeout(() => {{
                    styleSection.scrollIntoView({{
                        behavior: 'smooth',
                        block: 'start'
                    }});
                }}, 100);
            }}
        }}
        
        // Gestion upload de fichier
        document.addEventListener('DOMContentLoaded', () => {{
            const uploadZone = document.getElementById('upload-zone');
            const fileInput = document.getElementById('file-input');
            
            if (uploadZone && fileInput) {{
                uploadZone.addEventListener('dragover', (e) => {{
                    e.preventDefault();
                    uploadZone.style.borderColor = '#7aca6a';
                    uploadZone.style.background = '#f0fdf4';
                }});
                
                uploadZone.addEventListener('dragleave', () => {{
                    uploadZone.style.borderColor = '#cbd5e1';
                    uploadZone.style.background = 'transparent';
                }});
                
                uploadZone.addEventListener('drop', (e) => {{
                    e.preventDefault();
                    const files = e.dataTransfer.files;
                    if (files.length > 0) {{
                        handleFileUpload(files[0]);
                    }}
                }});
                
                fileInput.addEventListener('change', (e) => {{
                    if (e.target.files.length > 0) {{
                        handleFileUpload(e.target.files[0]);
                    }}
                }});
            }}
            
            // Gestion sélection de style → Sauvegarde + Redirect vers /stenciler
            document.querySelectorAll('.style-card').forEach(card => {{
                card.addEventListener('click', () => {{
                    // Désélectionner les autres
                    document.querySelectorAll('.style-card').forEach(c => c.classList.remove('selected'));
                    // Sélectionner celui-ci
                    card.classList.add('selected');
                    
                    const selectedStyle = card.dataset.style;
                    console.log('Style sélectionné:', selectedStyle);
                    
                    // Sauvegarder dans localStorage pour /stenciler (le genome sera fetché via /api/genome)
                    localStorage.setItem('aetherflow_selected_style', selectedStyle);
                    localStorage.setItem('aetherflow_timestamp', Date.now().toString());
                    
                    console.log('💾 Données sauvegardées, redirection vers /stenciler...');
                    
                    // Redirection vers /stenciler
                    window.location.href = '/stenciler';
                }});
            }});
        }});
        
        function handleFileUpload(file) {{
            console.log('Fichier uploadé:', file.name);
            alert(`Maquette "${{file.name}}" uploadée !\\nAnalyse Gemini Vision à implémenter...`);
        }}

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
    </script>
</body>
</html>'''


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Route pour les fonts Wingdings3
        if self.path == '/fonts/Wingdings3.woff2':
            self.serve_font('Wingdings3.woff2')
            return
        elif self.path == '/fonts/Wingdings3.woff':
            self.serve_font('Wingdings3.woff')
            return
        
        # Route principale
        if self.path == '/' or self.path.startswith('/studio'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            genome = load_genome()
            html = generate_html(genome)
            self.wfile.write(html.encode('utf-8'))
            return
        
        # Route Stenciler (nouveau layout)
        if self.path == '/stenciler':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            stenciler_html = generate_stenciler_html()
            self.wfile.write(stenciler_html.encode('utf-8'))
            return
        
        # Route API pour le genome
        if self.path == '/api/genome':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            genome = load_genome()
            self.wfile.write(json.dumps(genome).encode('utf-8'))
            return
        
        # Route pour les fichiers statiques (CSS, JS)
        if self.path.startswith('/static/'):
            self.serve_static(self.path[8:])  # Enlever '/static/'
            return
        
        self.send_response(404)
        self.end_headers()
    
    def serve_font(self, font_name):
        """Sert les fichiers de font"""
        font_path = os.path.join(FONTS_DIR, font_name)
        if not os.path.exists(font_path):
            # Essayer depuis le répertoire courant
            cwd = os.path.dirname(os.path.abspath(__file__))
            font_path = os.path.join(cwd, FONTS_DIR, font_name)
        
        if os.path.exists(font_path):
            self.send_response(200)
            if font_name.endswith('.woff2'):
                self.send_header('Content-type', 'font/woff2')
            else:
                self.send_header('Content-type', 'font/woff')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            with open(font_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass
    
    def serve_static(self, filepath):
        """Sert les fichiers statiques (CSS, JS)"""
        try:
            cwd = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(cwd, 'static', filepath)
            print(f"📁 Serving static: {filepath} -> {full_path}")
            print(f"   Exists: {os.path.exists(full_path)}, Is file: {os.path.isfile(full_path) if os.path.exists(full_path) else 'N/A'}")

            if os.path.exists(full_path) and os.path.isfile(full_path):
                self.send_response(200)
                if filepath.endswith('.css'):
                    content_type = 'text/css'
                elif filepath.endswith('.js'):
                    content_type = 'application/javascript'
                elif filepath.endswith('.json'):
                    content_type = 'application/json'
                else:
                    content_type = 'text/plain'
                print(f"   Content-Type: {content_type}")
                self.send_header('Content-type', content_type)
                self.end_headers()
                with open(full_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                print(f"   ❌ File not found: {full_path}")
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.send_response(500)
            self.end_headers()


def generate_stenciler_html():
    """Génère le HTML du Stenciler (mi-chemin)"""
    return '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stenciler — Mi-chemin</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/geist@1.3.0/dist/geist/Geist.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/geist@1.3.0/dist/geist/GeistMono.css">
    <link rel="stylesheet" href="/static/stenciler.css">
    <style>
        /* 🌓 Variables Thème Jour/Nuit avec transitions fluides */
        :root {
            --bg-primary: #ffffff;
            --bg-secondary: #f8fafc;
            --bg-sidebar: linear-gradient(180deg, #fff 0%, #fafafa 100%);
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --text-muted: #94a3b8;
            --border-color: #e2e8f0;
            --border-light: #f1f5f9;
            --shadow-color: rgba(0,0,0,0.05);
            --canvas-bg: #fafafa;
            --input-bg: #ffffff;
            --hover-bg: #f1f5f9;
            --accent-glow: rgba(122,202,106,0.3);
            --transition-speed: 0.3s;
        }
        
        [data-theme="dark"] {
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-sidebar: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
            --text-primary: #f8fafc;
            --text-secondary: #cbd5e1;
            --text-muted: #64748b;
            --border-color: #334155;
            --border-light: #1e293b;
            --shadow-color: rgba(0,0,0,0.3);
            --canvas-bg: #0f172a;
            --input-bg: #1e293b;
            --hover-bg: #334155;
            --accent-glow: rgba(122,202,106,0.2);
        }
        
        /* 🎭 Transitions fluides sur toutes les propriétés de couleur */
        body, .stenciler-app, .sidebar, .stenciler-header, .right-zone,
        .preview-band-wrapper, .canvas-zone, .components-zone,
        h1, h2, h3, h4, p, span, div, button, input, label {
            transition: background-color var(--transition-speed) ease,
                        background-image var(--transition-speed) ease,
                        color var(--transition-speed) ease,
                        border-color var(--transition-speed) ease,
                        box-shadow var(--transition-speed) ease;
        }
        
        /* Application des variables */
        body {
            background-color: var(--bg-primary);
            color: var(--text-primary);
        }
        
        .stenciler-app {
            background-color: var(--bg-primary);
        }
        
        .stenciler-header {
            background: var(--bg-secondary);
            border-bottom-color: var(--border-color);
        }
        
        .sidebar {
            background: var(--bg-sidebar);
            border-right-color: var(--border-color);
        }
        
        .sidebar-section-title {
            color: var(--text-muted);
        }
        
        .sidebar-section {
            border-bottom-color: var(--border-light);
        }
        
        .preview-band-wrapper {
            background: var(--bg-secondary);
            border-bottom-color: var(--border-color);
        }
        
        .canvas-zone {
            background: var(--canvas-bg);
        }
        
        .components-zone {
            background: var(--bg-secondary);
            border-top-color: var(--border-color);
        }
        
        .component-card {
            background: var(--bg-primary);
            border-color: var(--border-color);
        }
        
        .component-card:hover {
            background: var(--hover-bg);
        }
        
        input[type="range"] {
            background: var(--input-bg);
        }
        
        .color-swatch {
            border-color: var(--border-color);
        }
        
        .preview-card {
            background: var(--bg-primary);
            border-color: var(--border-color);
        }
        
        .preview-card:hover {
            border-color: #7aca6a;
            box-shadow: 0 4px 12px var(--accent-glow);
        }
        
        /* 🌙 Mode nuit - ajustements spécifiques */
        [data-theme="dark"] .stenciler-header h1 {
            color: var(--text-primary);
        }
        
        [data-theme="dark"] .sidebar-brand {
            color: var(--text-primary);
        }
        
        [data-theme="dark"] .sidebar-tagline {
            color: var(--text-secondary);
        }
        
        [data-theme="dark"] .preview-card .name {
            color: var(--text-primary);
        }
        
        [data-theme="dark"] .preview-card .count {
            color: var(--text-secondary);
        }
        
        [data-theme="dark"] .component-card .name {
            color: var(--text-primary);
        }
        
        /* Bouton thème amélioré */
        #theme-toggle {
            background: linear-gradient(135deg, #7aca6a 0%, #5a9a4a 100%);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(122,202,106,0.3);
        }
        
        #theme-toggle:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(122,202,106,0.4);
        }
        
        [data-theme="dark"] #theme-toggle {
            background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
            box-shadow: 0 2px 8px rgba(99,102,241,0.3);
        }
        
        [data-theme="dark"] #theme-toggle:hover {
            box-shadow: 0 4px 12px rgba(99,102,241,0.4);
        }
        
        /* Canvas tarmac en mode nuit */
        [data-theme="dark"] #canvas-container {
            background: #1e293b;
            border-color: #334155;
        }
        
        [data-theme="dark"] .canvas-placeholder {
            color: var(--text-muted);
        }
    </style>
</head>
<body>
    <div id="stenciler-app" class="stenciler-app">
        <!-- Header -->
        <header class="stenciler-header">
            <h1>Stenciler</h1>
            <div class="header-actions">
                <div class="style-indicator minimal">
                    <span class="dot"></span>
                    <span>minimal</span>
                </div>
                <button id="theme-toggle" title="Basculer entre jour et nuit">
                    <span class="theme-icon">☀️</span>
                    <span class="theme-text">Mode nuit</span>
                </button>
            </div>
        </header>

        <!-- Workspace: Sidebar left, Main right -->
        <div class="stenciler-workspace">
            
            <!-- Sidebar (LEFT) -->
            <aside class="sidebar">
                <div class="sidebar-header">
                    <div class="sidebar-brand">Homé<span class="brand-k">OS</span></div>
                    <div class="sidebar-tagline">Stenciler</div>
                </div>

                <div class="sidebar-section">
                    <div class="sidebar-section-title">Navigation</div>
                    <div class="breadcrumb" id="breadcrumb">Brainstorm</div>
                    <button class="btn-back hidden" id="btn-back">← Retour</button>
                </div>

                <div class="sidebar-section">
                    <div class="sidebar-section-title">Actions</div>
                    <button class="btn-delete">
                        <span class="delete-icon">×</span>
                        Supprimer (Del)
                    </button>
                    <div class="kbd-hint">
                        <kbd>Del</kbd> ou <kbd>Backspace</kbd>
                    </div>
                </div>

                <div class="sidebar-section">
                    <div class="sidebar-section-title">Mode Couleur</div>
                    <div class="color-mode-toggle">
                        <button class="mode-btn active" data-mode="border" title="Couleur sur les bords">
                            <span class="mode-icon">▣</span>
                            <span class="mode-label">Bordure</span>
                        </button>
                        <button class="mode-btn" data-mode="fill" title="Couleur de fond">
                            <span class="mode-icon">◼</span>
                            <span class="mode-label">Fond</span>
                        </button>
                    </div>
                </div>

                <div class="sidebar-section">
                    <div class="sidebar-section-title">Couleur Personnalisée (TSL)</div>
                    <div class="tsl-picker">
                        <div class="tsl-preview" id="tsl-preview"></div>
                        <div class="tsl-sliders">
                            <div class="tsl-row">
                                <label>T</label>
                                <input type="range" class="tsl-slider hue" id="tsl-h" min="0" max="360" value="0">
                                <span class="tsl-value" id="tsl-h-val">0°</span>
                            </div>
                            <div class="tsl-row">
                                <label>S</label>
                                <input type="range" class="tsl-slider saturation" id="tsl-s" min="0" max="100" value="70">
                                <span class="tsl-value" id="tsl-s-val">70%</span>
                            </div>
                            <div class="tsl-row">
                                <label>L</label>
                                <input type="range" class="tsl-slider lightness" id="tsl-l" min="0" max="100" value="50">
                                <span class="tsl-value" id="tsl-l-val">50%</span>
                            </div>
                        </div>
                        <button class="btn-apply-color" id="btn-apply-tsl">Appliquer</button>
                    </div>
                </div>

                <div class="sidebar-section">
                    <div class="sidebar-section-title">Préréglages</div>
                    <div class="color-palette">
                        <div class="color-swatch selected" style="background: var(--accent-rose);" data-color="rose"></div>
                        <div class="color-swatch" style="background: var(--accent-bleu);" data-color="bleu"></div>
                        <div class="color-swatch" style="background: var(--accent-vert);" data-color="vert"></div>
                        <div class="color-swatch" style="background: var(--accent-orange);" data-color="orange"></div>
                        <div class="color-swatch" style="background: var(--accent-mauve);" data-color="mauve"></div>
                        <div class="color-swatch" style="background: var(--accent-rouge);" data-color="rouge"></div>
                    </div>
                </div>

                <div class="sidebar-section">
                    <div class="sidebar-section-title">Bordure</div>
                    <input type="range" class="border-slider" min="0" max="10" value="2">
                    <div class="border-value">2px</div>
                </div>

                <div class="sidebar-section">
                    <div class="sidebar-section-title">API Claude</div>
                    <div class="api-status" id="api-status">
                        <span class="status-dot offline"></span>
                        <span class="status-text">Hors ligne</span>
                    </div>
                    <button class="btn-api" id="btn-fetch-genome">Charger Genome</button>
                    <button class="btn-api" id="btn-fetch-styles">Charger Styles</button>
                </div>
            </aside>

            <!-- Right zone (Preview + Dropped + Canvas) -->
            <div class="right-zone">
                <!-- Sticky top zone: Preview + Dropped bar -->
                <div class="sticky-top-zone" id="sticky-top-zone">
                    <!-- Previews band (TOP) - Collapsible sticky -->
                    <div class="preview-band-wrapper" id="preview-band-wrapper">
                        <div class="preview-band" id="preview-band">
                            <div class="preview-card brainstorm" data-corps="brainstorm">
                                <div class="corps-wireframe wf-brainstorm">
                                    <div class="wf-step active"></div>
                                    <div class="wf-step-line"></div>
                                    <div class="wf-step"></div>
                                    <div class="wf-step-line dim"></div>
                                    <div class="wf-step dim"></div>
                                </div>
                                <span class="name">Brainstorm</span>
                                <span class="count">2 organes</span>
                            </div>
                            <div class="preview-card backend" data-corps="backend">
                                <div class="corps-wireframe wf-backend">
                                    <div class="wf-bar" style="height:40%"></div>
                                    <div class="wf-bar" style="height:70%"></div>
                                    <div class="wf-bar dim" style="height:55%"></div>
                                    <div class="wf-bar" style="height:85%"></div>
                                </div>
                                <span class="name">Backend</span>
                                <span class="count">1 organe</span>
                            </div>
                            <div class="preview-card frontend" data-corps="frontend">
                                <div class="corps-wireframe wf-frontend">
                                    <div class="wf-frame"></div>
                                    <div class="wf-frame accent"></div>
                                    <div class="wf-frame"></div>
                                </div>
                                <span class="name">Frontend</span>
                                <span class="count">7 organes</span>
                            </div>
                            <div class="preview-card deploy" data-corps="deploy">
                                <div class="corps-wireframe wf-deploy">
                                    <div class="wf-launch-btn"></div>
                                    <div class="wf-arrow"></div>
                                </div>
                                <span class="name">Deploy</span>
                                <span class="count">1 organe</span>
                            </div>
                        </div>
                    </div>
                    <button class="preview-band-toggle" id="preview-band-toggle" title="Collapse/Expand">▼</button>

                    <!-- Dropped corps bar -->
                    <div class="dropped-bar hidden" id="dropped-bar">
                        <button class="toggle-btn" id="toggle-corps">▼</button>
                        <span class="corps-title" id="dropped-title">Frontend</span>
                        <span class="corps-badge" id="dropped-badge">7 organes</span>
                    </div>
                </div>

                <!-- Main content: Canvas + Components -->
                <main class="main-content">
                    <!-- Canvas (CENTER) -->
                    <div class="canvas-zone" id="canvas-zone">
                    <canvas id="tarmac-canvas"></canvas>
                    <div class="canvas-placeholder" id="canvas-placeholder">
                        <div class="icon">+</div>
                        <p>Glissez un Corps depuis la bande du haut</p>
                    </div>
                    <!-- Zoom controls -->
                    <div class="zoom-controls">
                        <button id="zoom-out" title="Zoom arrière">−</button>
                        <span id="zoom-level">100%</span>
                        <button id="zoom-in" title="Zoom avant">+</button>
                        <button id="zoom-reset" title="Reset">⟲</button>
                    </div>
                </div>

                <!-- Components (BOTTOM) - Wireframes Genome-like minimalistes -->
                <div class="components-zone">
                    <div class="components-title">Composants</div>
                    <div class="components-grid">
                        <!-- Button Wireframe -->
                        <div class="component-card">
                            <div class="wireframe-button">
                                <div class="wf-btn-bar"></div>
                            </div>
                            <div class="name">Button</div>
                        </div>
                        <!-- Card Wireframe -->
                        <div class="component-card">
                            <div class="wireframe-card">
                                <div class="wf-card-header"></div>
                                <div class="wf-card-body">
                                    <div class="wf-line"></div>
                                    <div class="wf-line short"></div>
                                </div>
                            </div>
                            <div class="name">Card</div>
                        </div>
                        <!-- Input Wireframe -->
                        <div class="component-card">
                            <div class="wireframe-input">
                                <div class="wf-input-label"></div>
                                <div class="wf-input-field"></div>
                            </div>
                            <div class="name">Input</div>
                        </div>
                        <!-- Modal Wireframe -->
                        <div class="component-card">
                            <div class="wireframe-modal">
                                <div class="wf-modal-header"></div>
                                <div class="wf-modal-body">
                                    <div class="wf-line"></div>
                                </div>
                                <div class="wf-modal-footer">
                                    <div class="wf-btn-mini"></div>
                                </div>
                            </div>
                            <div class="name">Modal</div>
                        </div>
                        <!-- Table Wireframe -->
                        <div class="component-card">
                            <div class="wireframe-table">
                                <div class="wf-row header">
                                    <div class="wf-cell"></div>
                                    <div class="wf-cell"></div>
                                </div>
                                <div class="wf-row">
                                    <div class="wf-cell"></div>
                                    <div class="wf-cell"></div>
                                </div>
                            </div>
                            <div class="name">Table</div>
                        </div>
                        <!-- Tabs Wireframe -->
                        <div class="component-card">
                            <div class="wireframe-tabs">
                                <div class="wf-tab active"></div>
                                <div class="wf-tab"></div>
                                <div class="wf-tab-content"></div>
                            </div>
                            <div class="name">Tabs</div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.1/fabric.min.js"></script>
    <script src="/static/stenciler.js"></script>
    <script src="/static/property_enforcer.js"></script>
    <script>
        // 🌓 GESTION DU THÈME JOUR/NUIT avec transition fluide
        const ThemeManager = {
            init() {
                // Récupérer le thème sauvegardé ou défaut (jour)
                const savedTheme = localStorage.getItem('aetherflow_theme') || 'light';
                this.applyTheme(savedTheme);
                
                // Écouteur sur le bouton
                const toggleBtn = document.getElementById('theme-toggle');
                if (toggleBtn) {
                    toggleBtn.addEventListener('click', () => this.toggle());
                }
            },
            
            toggle() {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                this.applyTheme(newTheme);
                
                // Feedback visuel
                console.log(`🌓 Thème basculé: ${newTheme === 'dark' ? 'Mode nuit' : 'Mode jour'}`);
            },
            
            applyTheme(theme) {
                const html = document.documentElement;
                const toggleBtn = document.getElementById('theme-toggle');
                const iconSpan = toggleBtn?.querySelector('.theme-icon');
                const textSpan = toggleBtn?.querySelector('.theme-text');
                
                if (theme === 'dark') {
                    html.setAttribute('data-theme', 'dark');
                    if (iconSpan) iconSpan.textContent = '🌙';
                    if (textSpan) textSpan.textContent = 'Mode jour';
                } else {
                    html.removeAttribute('data-theme');
                    if (iconSpan) iconSpan.textContent = '☀️';
                    if (textSpan) textSpan.textContent = 'Mode nuit';
                }
                
                // Sauvegarder la préférence
                localStorage.setItem('aetherflow_theme', theme);
            }
        };
        
        // Initialiser le thème dès que le DOM est prêt
        document.addEventListener('DOMContentLoaded', () => {
            ThemeManager.init();
        });
        
        // 🔽 DRILL-DOWN MANAGER — Navigation hiérarchique N0→N1→N2→N3
        const DrillDownManager = {
            API_BASE_URL: 'http://localhost:8000',
            currentPath: null,
            currentLevel: 0,
            breadcrumb: [],
            breadcrumbPaths: [],
            
            // Initialiser avec le genome
            async init(genome) {
                console.log('🔽 DrillDownManager initialisé');
                this.genome = genome;
                this.currentPath = 'n0[0]'; // Commencer au premier Corps
                this.currentLevel = 0;
                this.breadcrumb = [genome.n0_phases[0]?.name || 'Brainstorm'];
                this.breadcrumbPaths = ['n0[0]'];
                
                // Afficher le breadcrumb initial
                this.renderBreadcrumb();
                
                // Configurer le bouton retour
                this.setupBackButton();
                
                console.log('✅ DrillDown prêt — Niveau 0 (Corps)');
            },
            
            // Double-clic sur un composant
            async handleDoubleClick(entityId, entityName) {
                console.log(`🔍 Double-clic sur: ${entityName} (${entityId})`);
                
                // Trouver le path à partir de l'ID
                const path = this.findPathFromId(entityId);
                if (!path) {
                    console.warn('❌ Path non trouvé pour:', entityId);
                    return;
                }
                
                console.log('📍 Path trouvé:', path);
                
                // Vérifier si on peut descendre
                if (this.currentLevel >= 3) {
                    console.log('⛔ Niveau maximum atteint (N3)');
                    return;
                }
                
                // Appeler l'API drill-down
                try {
                    const response = await fetch(`${this.API_BASE_URL}/api/drilldown/enter`, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({path: path, child_index: 0})
                    });
                    
                    if (!response.ok) {
                        const error = await response.json();
                        console.warn('⚠️ Pas d\'enfant:', error.detail);
                        return;
                    }
                    
                    const data = await response.json();
                    console.log('⬇️ Drill-down réussi:', data);
                    
                    // Mettre à jour l'état
                    this.currentPath = data.new_path || path;
                    this.currentLevel = data.current_level;
                    this.breadcrumb = data.breadcrumb;
                    this.breadcrumbPaths = data.breadcrumb_paths;
                    
                    // Rafraîchir l'affichage
                    this.renderBreadcrumb();
                    this.renderChildren(data.children);
                    this.updateBackButtonVisibility();
                    
                } catch (err) {
                    console.error('❌ Erreur drill-down:', err);
                }
            },
            
            // Remonter d'un niveau
            async goBack() {
                if (this.currentLevel <= 0) {
                    console.log('⛔ Déjà au niveau racine');
                    return;
                }
                
                console.log('⬆️ Remontée au niveau précédent');
                
                try {
                    const response = await fetch(`${this.API_BASE_URL}/api/drilldown/exit`, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({path: this.currentPath})
                    });
                    
                    if (!response.ok) {
                        console.error('❌ Erreur exit:', await response.text());
                        return;
                    }
                    
                    const data = await response.json();
                    console.log('⬆️ Drill-up réussi:', data);
                    
                    // Mettre à jour l'état
                    this.currentPath = data.parent_path;
                    this.currentLevel = data.current_level;
                    this.breadcrumb = data.breadcrumb;
                    this.breadcrumbPaths = data.breadcrumb_paths;
                    
                    // Rafraîchir l'affichage
                    this.renderBreadcrumb();
                    this.renderChildren(data.children);
                    this.updateBackButtonVisibility();
                    
                } catch (err) {
                    console.error('❌ Erreur drill-up:', err);
                }
            },
            
            // Trouver le path à partir d'un ID
            findPathFromId(entityId) {
                // Si on est au niveau 0 (Corps), chercher dans n0_phases
                if (this.currentLevel === 0) {
                    const index = this.genome.n0_phases.findIndex(c => c.id === entityId);
                    if (index !== -1) return `n0[${index}]`;
                }
                // Sinon utiliser le path stocké dans l'objet
                return this.currentPath;
            },
            
            // Afficher le breadcrumb
            renderBreadcrumb() {
                const container = document.getElementById('breadcrumb');
                if (!container) {
                    console.warn('⚠️ Conteneur breadcrumb non trouvé');
                    return;
                }
                
                container.innerHTML = this.breadcrumb.map((name, index) => {
                    const isLast = index === this.breadcrumb.length - 1;
                    return `<span class="breadcrumb-item ${isLast ? 'active' : ''}">${name}</span>`;
                }).join(' <span class="breadcrumb-separator">></span> ');
                
                console.log('🍞 Breadcrumb mis à jour:', this.breadcrumb.join(' > '));
            },
            
            // Configurer le bouton retour
            setupBackButton() {
                const btn = document.getElementById('btn-back');
                if (btn) {
                    btn.addEventListener('click', () => this.goBack());
                    // Afficher le bouton si on n'est pas au niveau 0
                    if (this.currentLevel > 0) {
                        btn.classList.remove('hidden');
                    }
                    console.log('⬅️ Bouton retour configuré');
                }
            },
            
            // Mettre à jour la visibilité du bouton retour
            updateBackButtonVisibility() {
                const btn = document.getElementById('btn-back');
                if (btn) {
                    if (this.currentLevel > 0) {
                        btn.classList.remove('hidden');
                    } else {
                        btn.classList.add('hidden');
                    }
                }
            },
            
            // Afficher les enfants dans le canvas
            renderChildren(children) {
                console.log('🎨 Rendu des enfants:', children);
                
                // Mettre à jour le preview band avec les nouveaux éléments
                const previewBand = document.getElementById('preview-band');
                if (!previewBand) return;
                
                // Vider et reconstruire avec les enfants
                previewBand.innerHTML = children.map((child, index) => {
                    const color = child.color || '#64748b';
                    return `
                        <div class="preview-card" data-id="${child.id}" style="border-color: ${color}">
                            <div class="corps-wireframe" style="background: ${color}20">
                                <div class="wf-step active" style="background: ${color}"></div>
                            </div>
                            <span class="name">${child.name}</span>
                            <span class="count">${child.n3_atomsets?.length || child.n2_features?.length || 0} items</span>
                        </div>
                    `;
                }).join('');
                
                // Ajouter les écouteurs de double-clic
                previewBand.querySelectorAll('.preview-card').forEach((card, index) => {
                    card.addEventListener('dblclick', () => {
                        const child = children[index];
                        this.handleDoubleClick(child.id, child.name);
                    });
                });
                
                console.log(`✅ ${children.length} enfants affichés avec double-clic activé`);
            }
        };
        
        // 🚀 Récupération des données depuis la page Genome
        document.addEventListener('DOMContentLoaded', async () => {
            const selectedStyle = localStorage.getItem('aetherflow_selected_style');
            const timestamp = localStorage.getItem('aetherflow_timestamp');
            
            if (selectedStyle) {
                console.log('🎨 Style récupéré:', selectedStyle);
                
                // Mettre à jour l'indicateur de style dans le header
                const styleIndicator = document.querySelector('.style-indicator');
                if (styleIndicator) {
                    styleIndicator.className = 'style-indicator ' + selectedStyle;
                    styleIndicator.querySelector('span:last-child').textContent = selectedStyle;
                }
                
                // 🧬 Fetch le genome depuis l'API Backend (localhost:8000)
                try {
                    const response = await fetch('http://localhost:8000/api/genome');
                    const data = await response.json();
                    const genome = data.genome || data;  // Supporte les deux formats
                    console.log('🧬 Genome chargé via API Backend:', genome.n0_phases?.length || 0, 'corps');
                    
                    // Stocker pour utilisation par stenciler.js
                    window.aetherflowState = {
                        genome: genome,
                        style: selectedStyle,
                        timestamp: parseInt(timestamp || '0')
                    };
                    
                    // 🔽 Initialiser le DrillDownManager
                    await DrillDownManager.init(genome);
                } catch (err) {
                    console.error('❌ Erreur chargement genome:', err);
                }
                
                // 🎭 Illusion : scroll vers le bas comme si on continuait la page
                setTimeout(() => {
                    window.scrollTo({
                        top: document.body.scrollHeight,
                        behavior: 'smooth'
                    });
                    console.log('🎭 Scroll automatique vers le bas (illusion de continuité)');
                }, 500);
                
            } else {
                console.log('ℹ️ Aucun style sélectionné — mode standalone');
            }
        });
    </script>
</body>
</html>'''


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f"🧬 Genome Viewer v6.0 running at http://localhost:{PORT}")
    print(f"🎨 Stenciler at http://localhost:{PORT}/stenciler")
    print(f"📁 Serving genome from: {GENOME_FILE}")
    print(f"🔤 Wingdings3 fonts from: {FONTS_DIR}")
    print("Press Ctrl+C to stop")
    server.serve_forever()
