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


