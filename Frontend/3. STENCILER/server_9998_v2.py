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
from pathlib import Path

# Ajout du chemin pour importer les modules Backend
cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(cwd, "../.."))
sys.path.append(os.path.join(cwd, "../../Backend/Prod"))

from sullivan.context_pruner import prune_genome
from genome_preview import render_genome_preview

PORT = 9998
GENOME_FILE = "../2. GENOME/genome_reference.json"
FONTS_DIR = "../fonts"
STATIC_DIR = "static"
TEMPLATES_DIR = os.path.join(STATIC_DIR, "templates")

# =============================================================================
# INFER LAYOUT — Heuristique + LLM 3-tier
# =============================================================================

_ROLE_KEYWORDS = {
    "navigation":      ["nav", "navigation", "menu", "breadcrumb"],
    "toolbar":         ["toolbar", "tools", "controls", "palette"],
    "sidebar_controls":["sidebar", "panel", "controls", "settings"],
    "editor":          ["editor", "code", "script", "json", "analyse"],
    "canvas":          ["canvas", "board", "drawing", "stencil"],
    "chat":            ["chat", "dialogue", "message", "input"],
    "preview":         ["preview", "render", "viewer", "output"],
    "dashboard":       ["dashboard", "session", "summary", "status", "report"],
    "deploy_pipeline": ["deploy", "pipeline", "export", "build", "publish"],
}

_ROLE_LAYOUT = {
    "navigation":       {"zone": "header",        "w": 1024, "h": 48,    "layout": "flex"},
    "toolbar":          {"zone": "header",        "w": 1024, "h": 40,    "layout": "flex"},
    "sidebar_controls": {"zone": "sidebar_right", "w": 240,  "h": "auto","layout": "stack"},
    "editor":           {"zone": "main",          "w": 640,  "h": "auto","layout": "stack"},
    "canvas":           {"zone": "canvas",        "w": 1024, "h": "full","layout": "free"},
    "chat":             {"zone": "sidebar_right", "w": 336,  "h": "auto","layout": "stack"},
    "preview":          {"zone": "preview_band",  "w": 1024, "h": 120,   "layout": "flex"},
    "dashboard":        {"zone": "main",          "w": 1024, "h": 320,   "layout": "grid"},
    "deploy_pipeline":  {"zone": "footer",        "w": 1024, "h": 48,    "layout": "flex"},
}

_LAYOUT_SYSTEM_PROMPT = """Tu es un expert UX/layout. Pour chaque organe N1 d'un genome JSON, tu inféres ses paramètres de layout SVG.
Règles : reference_width=1024px, grid_unit=8px (toutes les valeurs en multiples de 8).
Zones : header, sidebar_left, sidebar_right, main, canvas, preview_band, footer.
Layout types : flex, stack, grid, free. h = nombre|"auto"|"full", w = nombre|"full".
Réponds UNIQUEMENT avec un objet JSON valide, sans markdown, sans explication.
Format : { "organ_id": { "role": "...", "zone": "...", "w": ..., "h": ..., "layout": "..." }, ... }"""


def _load_env():
    """Charge le .env AetherFlow dans os.environ (setdefault)."""
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())


def infer_layout_heuristic(organs):
    """Tier 1 — heuristique offline, toujours disponible."""
    result = {}
    for o in organs:
        pool = f"{o.get('id','')} {o.get('name','')}".lower()
        role = next((r for r, kws in _ROLE_KEYWORDS.items() if any(k in pool for k in kws)), None)
        if role:
            result[o["id"]] = {"role": role, **_ROLE_LAYOUT[role]}
        else:
            w = min(320 + o.get("n2_count", 0) * 32, 800)
            result[o["id"]] = {"role": "unknown", "zone": "main", "w": round(w/8)*8, "h": "auto", "layout": "stack"}
    return result


def infer_layout_llm(organs, project_context="", model_name="gemini-2.0-flash"):
    """Tier 2/3 — LLM Gemini. project_context = tier 3."""
    try:
        import google.generativeai as genai
    except ImportError:
        return None, "google-generativeai not installed", None

    _load_env()
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return None, "GOOGLE_API_KEY not set", None

    genai.configure(api_key=api_key)
    system = _LAYOUT_SYSTEM_PROMPT
    if project_context:
        system += f"\n\nContexte projet : {project_context}"

    model = genai.GenerativeModel(model_name=model_name, system_instruction=system)
    organs_summary = [{"id": o["id"], "name": o.get("name",""), "n2_count": o.get("n2_count", 0)} for o in organs]
    user_msg = f"Genome organs N1 :\n{json.dumps(organs_summary, ensure_ascii=False, indent=2)}"

    try:
        response = model.generate_content(user_msg)
        raw = re.sub(r"^```json\s*|\s*```$", "", response.text.strip(), flags=re.MULTILINE).strip()
        return json.loads(raw), None, model_name
    except Exception as e:
        return None, str(e), model_name


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
        
        # Route Stenciler (V3 modulaire — référence active)
        if self.path == '/stenciler':
            self.serve_template('stenciler_v3.html')
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
        
        # Route preview HTML (Mission 18A — Flowbite HTML from genome)
        if self.path == '/preview':
            genome = load_genome()
            html = render_genome_preview(genome)
            self._send_html(html)
            return

        if self.path.startswith('/preview/'):
            phase_id = self.path[9:]
            genome = load_genome()
            html = render_genome_preview(genome, phase_id=phase_id)
            self._send_html(html)
            return

        self.send_error_json(404, f"Route {self.path} not found")

    def do_OPTIONS(self):
        """CORS preflight — nécessaire pour fetch() depuis le frontend."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_PATCH(self):
        """PATCH /api/genome/node/<id>  et  PATCH /api/genome/organ/<id>/reorder"""
        if re.match(r'^/api/genome/node/[^/]+$', self.path):
            self._handle_node_patch(self.path.split('/')[-1])
            return
        if re.match(r'^/api/genome/organ/[^/]+/reorder$', self.path):
            parts = self.path.split('/')
            self._handle_organ_reorder(parts[-2])
            return
        self.send_error_json(404, f"PATCH route {self.path} not found")

    def _handle_node_patch(self, node_id):
        """Met à jour un champ d'un composant N3 et sauvegarde le genome."""
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
        except Exception as e:
            self.send_error_json(400, f"Invalid JSON: {e}")
            return

        field = body.get('field')
        value = body.get('value')

        if field not in ('name', 'visual_hint'):
            self.send_error_json(400, f"Invalid field '{field}'. Allowed: name, visual_hint")
            return

        genome = load_genome()
        node = _find_n3_by_id(genome, node_id)
        if not node:
            self.send_error_json(404, f"Node {node_id} not found in genome")
            return

        node[field] = value
        save_genome(genome)
        self.send_json({"ok": True, "id": node_id, "field": field, "value": value})

    def _handle_organ_reorder(self, organ_id):
        """Réordonne les N3 dans le premier N2 d'un organe N1."""
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
        except Exception as e:
            self.send_error_json(400, f"Invalid JSON: {e}")
            return

        order = body.get('order', [])
        genome = load_genome()
        n2 = _find_n2_by_organ(genome, organ_id)
        if not n2:
            self.send_error_json(404, f"Organ {organ_id} not found in genome")
            return

        n3_map = {c['id']: c for c in n2.get('n3_components', [])}
        n2['n3_components'] = [n3_map[cid] for cid in order if cid in n3_map]
        save_genome(genome)
        self.send_json({"ok": True, "organ_id": organ_id, "order": order})

    def do_POST(self):
        if self.path == '/api/infer_layout':
            self._handle_infer_layout()
            return
        self.send_error_json(404, f"POST route {self.path} not found")

    def _handle_infer_layout(self):
        """Route POST /api/infer_layout
        Body : { organs: [...], mode: "heuristic"|"llm"|"llm_context", context: "", model: "" }
        Response : { result: {...}, tier: "...", model: "..." }
        """
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
        except Exception as e:
            self.send_error_json(400, f"Invalid JSON body: {e}")
            return

        organs = body.get('organs', [])
        mode   = body.get('mode', 'heuristic')
        context = body.get('context', '')
        model_name = body.get('model', 'gemini-2.0-flash')

        if mode == 'heuristic':
            self.send_json({"result": infer_layout_heuristic(organs), "tier": "heuristic"})

        elif mode in ('llm', 'llm_context'):
            ctx = context if mode == 'llm_context' else ''
            result, err, used_model = infer_layout_llm(organs, ctx, model_name)
            if err:
                # Fallback automatique → heuristique
                self.send_json({
                    "result": infer_layout_heuristic(organs),
                    "tier": "heuristic_fallback",
                    "error": err
                })
            else:
                self.send_json({"result": result, "tier": "llm", "model": used_model})

        else:
            self.send_error_json(400, f"Unknown mode: {mode}. Use heuristic|llm|llm_context")

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
            self.send_header('Cache-Control', 'no-store, must-revalidate')
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
                elif filename.endswith('.html'): content_type = 'text/html'
                else: content_type = 'text/plain'
            
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.send_header('Cache-Control', 'no-store, must-revalidate')
            self.end_headers()

            with open(filepath, 'rb') as f:
                self.wfile.write(f.read())
        except Exception as e:
            self.send_error(500, str(e))

    def serve_sw(self):
        """Sert le Service Worker depuis la racine du serveur."""
        try:
            cwd = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(cwd, STATIC_DIR, 'js', 'sw.js')
            
            if not os.path.exists(filepath):
                self.send_error(404, "Service Worker file not found")
                return
            
            self.send_response(200)
            self.send_header('Content-type', 'application/javascript')
            self.send_header('Cache-Control', 'no-store, must-revalidate')
            self.end_headers()

            with open(filepath, 'rb') as f:
                self.wfile.write(f.read())
        except Exception as e:
            self.send_error(500, str(e))

    def serve_font(self, filename):
        """Sert une police depuis le dossier fonts"""
        try:
            cwd = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(cwd, FONTS_DIR, filename)
            
            if not os.path.exists(filepath):
                self.send_error(404, f"Font {filename} not found")
                return
            
            self.send_response(200)
            self.send_header('Content-type', 'font/woff2')
            self.end_headers()

            with open(filepath, 'rb') as f:
                self.wfile.write(f.read())
        except Exception as e:
            self.send_error(500, str(e))

    def send_json(self, data):
        """Envoie une réponse JSON"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))

    def _send_html(self, html):
        """Envoie une page HTML complète"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-store, must-revalidate')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))


def save_genome(genome):
    """Sauvegarde le genome sur disque (miroir de load_genome)."""
    filepath = GENOME_FILE
    if not os.path.exists(os.path.dirname(os.path.abspath(filepath))):
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), GENOME_FILE)
    else:
        cwd_local = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(cwd_local, GENOME_FILE)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(genome, f, indent=2, ensure_ascii=False)


def _find_n3_by_id(genome, node_id):
    """Trouve un composant N3 par son id."""
    for phase in genome.get('n0_phases', []):
        for organ in phase.get('n1_sections', []):
            for feature in organ.get('n2_features', []):
                for comp in feature.get('n3_components', []):
                    if comp.get('id') == node_id:
                        return comp
    return None


def _find_n2_by_organ(genome, organ_id):
    """Retourne le premier N2 d'un organe N1 donné."""
    for phase in genome.get('n0_phases', []):
        for organ in phase.get('n1_sections', []):
            if organ.get('id') == organ_id:
                features = organ.get('n2_features', [])
                return features[0] if features else None
    return None


def load_custom_injection():
    """Charge le script d'injection personnalisé s'il existe"""
    try:
        cwd = os.path.dirname(os.path.abspath(__file__))
        injection_path = os.path.join(cwd, STATIC_DIR, 'js', 'custom_injection.js')
        if os.path.exists(injection_path):
            with open(injection_path, 'r') as f:
                return f"<script>{f.read()}</script>"
    except:
        pass
    return ""


if __name__ == '__main__':
    server = ThreadingHTTPServer(('0.0.0.0', PORT), Handler)
    print(f"🧬 Serveur Genome lancé sur http://localhost:{PORT}")
    print(f"   - Viewer:        http://localhost:{PORT}/")
    print(f"   - Stenciler:     http://localhost:{PORT}/stenciler")
    print(f"   - API Genome:    http://localhost:{PORT}/api/genome")
    print(f"   - InferLayout:   http://localhost:{PORT}/api/infer_layout  (POST)")
    print(f"   - Preview HTML:  http://localhost:{PORT}/preview")
    server.serve_forever()
