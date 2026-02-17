#!/usr/bin/env python3
"""
Serveur HTTP pour visualisation du Genome - Port 9998
Version 7.0 - Sullivan Architecture (Modular Templates)
"""

from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import json
import os
import re
import sys

# Ajout du chemin pour importer les modules Backend
cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(cwd, "../.."))
sys.path.append(os.path.join(cwd, "../../Backend/Prod"))

from sullivan.context_pruner import prune_genome

PORT = 9998
GENOME_FILE = "../2. GENOME/genome_reference.json"
FONTS_DIR = "../fonts"
STATIC_DIR = "static"
TEMPLATES_DIR = os.path.join(STATIC_DIR, "templates")

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


# =============================================================================
# SERVEUR HTTP ET DISTRIBUTION DES TEMPLATES
# =============================================================================

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Route pour les fonts Wingdings3
        if self.path.startswith('/fonts/'):
            self.serve_font(self.path[7:])
            return
        
        # Route principale (Genome Viewer)
        if self.path == '/' or self.path.startswith('/studio'):
            self.serve_template('viewer.html')
            return
        
        # Route Stenciler
        if self.path == '/stenciler':
            self.serve_template('stenciler.html')
            return
        
        # Route Stenciler V3 (Modular)
        if self.path == '/stenciler_v3':
            self.serve_template('stenciler_v3.html')
            return
        
        # Route pour le Service Worker (doit être à la racine pour le scope)
        if self.path == '/sw.js':
            self.serve_sw()
            return
        
        # Route API pour le genome
        if self.path == '/api/genome':
            self.send_json(load_genome())
            return
        
        # Route API pour le lexique de design
        if self.path == '/api/lexicon':
            lexicon_path = os.path.join(cwd, "../1. CONSTITUTION/LEXICON_DESIGN.json")
            if os.path.exists(lexicon_path):
                with open(lexicon_path, 'r') as f:
                    self.send_json(json.load(f))
            else:
                self.send_error_json(404, "Lexicon not found")
            return
        
        # Route API pour le genome contextuel (Pruning)
        if self.path.startswith('/api/genome/pruned/'):
            target_id = self.path[19:]
            genome = load_genome()
            pruned = prune_genome(genome, target_id)
            if pruned:
                self.send_json(pruned)
            else:
                self.send_error(404, f"ID {target_id} not found in genome")
            return
        
        # Route pour les fichiers statiques (CSS, JS)
        if self.path.startswith('/static/'):
            self.serve_static(self.path[8:])
            return

        # Route API pour le CSS (PropertyEnforcer)
        if self.path.endswith('/css') and '/api/genome/' in self.path:
            self.send_json({"css": "/* Genome Enforced Styles */\n:root { --accent-rose: #ff0080; }"})
            return
        
        self.send_error_json(404, f"Route {self.path} not found")

    def do_HEAD(self):
        """Support pour les requêtes HEAD (ping API)"""
        if self.path == '/api/genome' or self.path.startswith('/api/'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def send_error_json(self, code, message):
        """Envoie une erreur au format JSON pour satisfaire le Semantic Bridge"""
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message, "code": code}).encode('utf-8'))

    def serve_template(self, template_name):
        """Lit, remplit et sert un template HTML avec injection de scripts"""
        try:
            cwd = os.path.dirname(os.path.abspath(__file__))
            template_path = os.path.join(cwd, TEMPLATES_DIR, template_name)
            
            if not os.path.exists(template_path):
                self.send_error(404, f"Template {template_name} not found")
                return
            
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Injection minimaliste (Pristine Mode)
            placeholders = {
                "custom_injection": load_custom_injection()
            }
            
            for key, value in placeholders.items():
                content = content.replace(f"{{{{{key}}}}}", value)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except Exception as e:
            self.send_error(500, str(e))

    def serve_static(self, filename, content_type=None):
        """Sert un fichier statique (JS, CSS, etc.)"""
        try:
            cwd = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(cwd, STATIC_DIR, filename)
            
            if not os.path.exists(filepath):
                self.send_error(404, f"File {filename} not found")
                return
            
            if not content_type:
                if filename.endswith('.js'): content_type = 'application/javascript'
                elif filename.endswith('.css'): content_type = 'text/css'
                elif filename.endswith('.png'): content_type = 'image/png'
                elif filename.endswith('.svg'): content_type = 'image/svg+xml'
                else: content_type = 'text/plain'
            
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            
            with open(filepath, 'rb') as f:
                self.wfile.write(f.read())
        except Exception as e:
            self.send_error(500, str(e))

    def serve_sw(self):
        """Sert le Service Worker depuis la racine du serveur."""
        try:
            cwd = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(cwd, STATIC_DIR, 'js', 'sw.js') # Assurez-vous que le chemin est correct
            
            if not os.path.exists(filepath):
                self.send_error(404, "Service Worker file not found")
                return
            
            self.send_response(200)
            self.send_header('Content-type', 'application/javascript')
            self.end_headers()
            
            with open(filepath, 'rb') as f:
                self.wfile.write(f.read())
        except Exception as e:
            self.send_error(500, str(e))

    def serve_font(self, font_name):
        """Sert les fichiers de font"""
        font_path = os.path.join(FONTS_DIR, font_name)
        if not os.path.exists(font_path):
            cwd = os.path.dirname(os.path.abspath(__file__))
            font_path = os.path.join(cwd, FONTS_DIR, font_name)
        
        if os.path.exists(font_path):
            self.send_response(200)
            self.send_header('Content-type', 'font/woff2' if font_name.endswith('.woff2') else 'font/woff')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            with open(font_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()

    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def log_message(self, format, *args):
        pass

def load_custom_injection() -> str:
    """Charge un script d'injection personnalisé pour les tests Sullivan"""
    try:
        cwd = os.path.dirname(os.path.abspath(__file__))
        custom_path = os.path.join(cwd, STATIC_DIR, 'js', 'custom_injection.js')
        
        if os.path.exists(custom_path):
            with open(custom_path, 'r', encoding='utf-8') as f:
                return f'<script>\n{f.read()}\n</script>'
        return "<!-- No custom injection found -->"
    except Exception as e:
        return f"<!-- Error loading custom injection: {str(e)} -->"

def get_api_schema() -> dict:
    """Retourne le schéma de l'API pour le endpoint /api/schema"""
    return {
        "api_version": "1.0.0",
        "endpoints": {
            "/api/genome": {
                "method": "GET",
                "description": "Retourne le genome complet",
                "response_format": {
                    "n0_phases": "list",
                    "metadata": "dict"
                }
            },
            "/api/genome/pruned/{id}": {
                "method": "GET",
                "description": "Retourne un fragment du genome (Extreme Contextualization)",
                "response_format": "dict (subset of genome)"
            },
            "/api/schema": {
                "method": "GET",
                "description": "Retourne ce schéma d'API",
                "response_format": "dict"
            }
        },
        "templates": {
            "/": {
                "name": "Genome Viewer",
                "description": "Interface de visualisation du genome",
                "injected_scripts": ["engine", "semantic_bridge", "viewer"]
            },
            "/stenciler": {
                "name": "Stenciler",
                "description": "Interface de génération de code",
                "injected_scripts": ["stenciler"]
            }
        },
        "static_files": {
            "css": ["/static/css/viewer.css", "/static/css/stenciler.css"],
            "js": ["/static/js/semantic_bridge.js", "/static/js/viewer.js", "/static/js/stenciler.js"]
        },
        "metadata": {
            "server_version": "7.0 Sullivan",
            "port": PORT,
            "genome_file": GENOME_FILE,
            "templates_dir": TEMPLATES_DIR
        }
    }


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = ThreadingHTTPServer(('0.0.0.0', PORT), Handler)
    print(f"🧬 Genome Viewer v7.0 (Sullivan) running at http://localhost:{PORT}")
    print(f"🎨 Stenciler at http://localhost:{PORT}/stenciler")
    print(f"📁 Serving templates from: {TEMPLATES_DIR}")
    print("Press Ctrl+C to stop")
    server.serve_forever()