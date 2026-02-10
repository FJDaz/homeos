#!/usr/bin/env python3
"""
Serveur HTTP pour visualisation du Genome - Port 9998
Version 6.0 - Collapses + Wingdings3 + Noms User-Friendly
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
        
        /* Style Previews */
        .style-preview {{
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 8px;
        }}
        .style-preview .sp-title {{
            font-size: 12px;
            font-weight: 700;
            margin-bottom: 2px;
        }}
        .style-preview .sp-sub {{
            font-size: 9px;
            font-weight: 500;
            opacity: 0.8;
        }}
        
        /* Minimal: Clean, light, airy */
        .minimal-preview {{
            background: #ffffff;
            color: #334155;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }}
        .minimal-preview .sp-title {{ font-weight: 300; letter-spacing: 0.5px; }}
        
        /* Corporate: Professional, structured */
        .corporate-preview {{
            background: #1e3a5f;
            color: #ffffff;
            font-family: Georgia, 'Times New Roman', serif;
        }}
        .corporate-preview .sp-title {{ font-weight: 600; text-transform: uppercase; letter-spacing: 1px; font-size: 11px; }}
        
        /* Creative: Bold, artistic */
        .creative-preview {{
            background: linear-gradient(135deg, #f97316 0%, #ec4899 100%);
            color: #ffffff;
            font-family: 'Courier New', monospace;
        }}
        .creative-preview .sp-title {{ font-weight: 800; font-style: italic; }}
        
        /* Tech: Modern, code-like */
        .tech-preview {{
            background: #0f172a;
            color: #22d3ee;
            font-family: 'SF Mono', Monaco, monospace;
        }}
        .tech-preview .sp-title {{ font-weight: 700; letter-spacing: 2px; font-size: 11px; }}
        
        /* Elegant: Refined, luxurious */
        .elegant-preview {{
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            color: #92400e;
            font-family: Georgia, serif;
        }}
        .elegant-preview .sp-title {{ font-weight: 400; letter-spacing: 1px; }}
        
        /* Playful: Friendly, rounded */
        .playful-preview {{
            background: #fce7f3;
            color: #be185d;
            font-family: 'Comic Sans MS', cursive, sans-serif;
            border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
        }}
        .playful-preview .sp-title {{ font-weight: 700; font-size: 13px; }}
        
        /* Dark: Night mode, sleek */
        .dark-preview {{
            background: #18181b;
            color: #e4e4e7;
            font-family: system-ui, sans-serif;
        }}
        .dark-preview .sp-title {{ font-weight: 500; letter-spacing: 0.5px; }}
        
        /* Colorful: Vibrant, gradient */
        .colorful-preview {{
            background: linear-gradient(45deg, #3b82f6, #8b5cf6, #ec4899, #f59e0b);
            background-size: 200% 200%;
            color: #ffffff;
            font-family: -apple-system, sans-serif;
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        }}
        .colorful-preview .sp-title {{ font-weight: 800; }} }} 
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
            
            // Gestion sélection de style
            document.querySelectorAll('.style-card').forEach(card => {{
                card.addEventListener('click', () => {{
                    // Désélectionner les autres
                    document.querySelectorAll('.style-card').forEach(c => c.classList.remove('selected'));
                    // Sélectionner celui-ci
                    card.classList.add('selected');
                    console.log('Style sélectionné:', card.dataset.style);
                }});
            }});
        }});
        
        function handleFileUpload(file) {{
            console.log('Fichier uploadé:', file.name);
            alert(`Maquette "${{file.name}}" uploadée !\\nAnalyse Gemini Vision à implémenter...`);
        }}
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
        else:
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


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f"🧬 Genome Viewer v6.0 running at http://localhost:{PORT}")
    print(f"📁 Serving genome from: {GENOME_FILE}")
    print(f"🔤 Wingdings3 fonts from: {FONTS_DIR}")
    print("Press Ctrl+C to stop")
    server.serve_forever()
