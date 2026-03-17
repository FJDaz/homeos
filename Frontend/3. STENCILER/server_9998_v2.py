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
import uuid
import asyncio
import threading
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import urllib.request
import urllib.error

# Ajout des chemins pour importer les modules Backend et Frontend
cwd = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(cwd, "../.."))
backend_prod = os.path.abspath(os.path.join(cwd, "../../Backend/Prod"))
backend_archive = os.path.abspath(os.path.join(cwd, "../../Backend/_archive"))

for p in [root_dir, backend_prod, backend_archive]:
    if p not in sys.path:
        sys.path.insert(0, p)

from sullivan.context_pruner import prune_genome
from genome_preview import render_genome_preview
from exporters.genome_to_svg import generate_svg

# Mission 32/35 - Retro Genome (importés via Backend.Prod pour préserver les liens relatifs)
from Backend.Prod.retro_genome.analyzer import RetroGenomeAnalyzer
from Backend.Prod.retro_genome.intent_mapper import IntentMapper
from Backend.Prod.retro_genome.manifest_reader import ManifestReader
from Backend.Prod.retro_genome.html_generator import HtmlGenerator
from Backend.Prod.retro_genome.prd_generator import PRDGenerator

# Mission 43 — Phase Brainstorm (BRS)
from Backend.Prod.retro_genome import brainstorm_logic as brs_logic

RETRO_ANALYZE_DIR = Path(__file__).parent / "../../exports/retro_genome"
RETRO_ANALYZE_DIR.mkdir(parents=True, exist_ok=True)

PORT = 9998
GENOME_FILE = "../2. GENOME/genome_enriched.json"
LAYOUT_FILE = "../2. GENOME/layout.json"
FONTS_DIR = "../fonts"
STATIC_DIR = "static"
TEMPLATES_DIR = os.path.join(STATIC_DIR, "templates")

# =============================================================================
# PIPELINE STATE (Mission 24A)
# =============================================================================
_pipeline_running = False
_pipeline_iteration = 0
_pipeline_lock = threading.Lock()

# =============================================================================
# KIMI JOB QUEUE (Mission 54)
# =============================================================================
_kimi_jobs = {}          # { job_id: { status, label, html, error, ts } }
_kimi_jobs_lock = threading.Lock()

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


def _write_retro_status(step: str, message: str, **kwargs):
    """Écrit l'étape courante dans un fichier de statut pour le polling frontend."""
    try:
        status_path = Path(__file__).parent.parent.parent / "exports" / "retro_genome" / "upload_status.json"
        status_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"step": step, "message": message}
        data.update(kwargs)
        with open(status_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception:
        pass  # Non-bloquant


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


def enrich_genome_with_rag(genome):
    from pathlib import Path
    try:
        rag_file = Path(__file__).parent.parent.parent / "docs" / "06_Genome_Pedagogy" / "GENOME_RAG_INDEX.md"
        if not rag_file.exists(): return
        content = rag_file.read_text(encoding="utf-8")
        rag_dict = {}
        import re
        blocks = re.finditer(r'### \[([a-zA-Z0-9_]+)\](.*?)(?=### \[|\Z)', content, re.DOTALL)
        for b in blocks:
            feat_id = b.group(1)
            text = b.group(2)
            m_sens = re.search(r'\*\*(?:Sens Humain|Doc UX).*?\*\*.*?:(.*?)(?=\n- |\n\n|\Z)', text, re.DOTALL | re.IGNORECASE)
            m_intent = re.search(r'\*\*(?:Intent Code|Utilit|Intent).*?\*\*.*?:(.*?)(?=\n- |\n\n|\Z)', text, re.DOTALL | re.IGNORECASE)
            rag_dict[feat_id] = {
                "sens_humain": m_sens.group(1).strip() if m_sens else "",
                "intent_code": m_intent.group(1).strip() if m_intent else ""
            }
        
        for phase in genome.get('n0_phases', []):
            for section in phase.get('n1_sections', []):
                for feat in section.get('n2_features', []):
                    if feat['id'] in rag_dict:
                        feat['doc_sens_humain'] = rag_dict[feat['id']]['sens_humain']
                        feat['doc_intent_code'] = rag_dict[feat['id']]['intent_code']
    except Exception as e:
        print(f"WARN: Failed to enrich RAG {e}")

def _run_kimi_job(job_id, instruction, html_context):
    """Exécute l'appel KIMI en arrière-plan (Mission 54)."""
    try:
        # 1. Strip <script> blocks (Mission 52 optimization)
        html_stripped = re.sub(r'<script[\s\S]*?</script>', '', html_context, flags=re.IGNORECASE).strip()

        _load_env()
        api_key = os.environ.get('NVIDIA_NIM_API_KEY') or os.environ.get('NVIDIA_API_KEY')
        if not api_key:
            with _kimi_jobs_lock:
                _kimi_jobs[job_id] = { "status": "error", "error": "NVIDIA_API_KEY non configurée", "ts": datetime.now() }
            return

        url = "https://integrate.api.nvidia.com/v1/chat/completions"

        prompt = (
            "Tu es KIMI, expert en design UI/UX. Propose UNE refonte visuelle de l'interface HTML/Tailwind fournie.\n"
            "Réponds avec un label court (3-5 mots) puis le HTML complet modifié.\n"
            "Format strict :\nLABEL: [label]\n---HTML---\n[HTML complet]\n\n"
            f"Instruction : {instruction}\n"
            f"HTML actuel (scripts omis) :\n{html_stripped}"
        )

        payload = {
            "model": "moonshotai/kimi-k2.5",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 8192,
            "temperature": 0.7
        }

        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'),
                                     headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'})

        # Augmentation du timeout pour le thread d'arrière-plan (10 min)
        with urllib.request.urlopen(req, timeout=600) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            choices = res_data.get('choices') or []
            raw_text = (choices[0].get('message') or {}).get('content') if choices else None
            
            if not raw_text:
                finish = (choices[0].get('finish_reason') if choices else 'unknown')
                error_msg = f"KIMI content vide (finish_reason: {finish})"
                with _kimi_jobs_lock:
                    _kimi_jobs[job_id] = { "status": "error", "error": error_msg, "ts": datetime.now() }
                return

            print(f"[KIMI_DEBUG] {raw_text[:200]}...", flush=True)

            # Parse label + html
            label = "KIMI Design"
            html = raw_text.strip()
            if "LABEL:" in html:
                parts = html.split("---HTML---", 1)
                label = parts[0].replace("LABEL:", "").strip()
                html = parts[1].strip() if len(parts) > 1 else html
            elif "---HTML---" in html:
                html = html.split("---HTML---", 1)[1].strip()

            # Strip markdown code fences if present
            if html.startswith("```html"):
                html = html.split("```html", 1)[1].split("```")[0].strip()
            elif html.startswith("```"):
                html = html.split("```", 1)[1].split("```")[0].strip()

            with _kimi_jobs_lock:
                _kimi_jobs[job_id] = { "status": "done", "label": label, "html": html, "ts": datetime.now() }

    except Exception as e:
        print(f"[KIMI_ERROR] {str(e)}", flush=True)
        with _kimi_jobs_lock:
            _kimi_jobs[job_id] = { "status": "error", "error": str(e), "ts": datetime.now() }

def load_genome():
    """Charge le genome depuis le fichier JSON"""
    filepath = GENOME_FILE
    if not os.path.exists(filepath):
        cwd = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(cwd, GENOME_FILE)
    
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            genome = json.load(f)
            enrich_genome_with_rag(genome)
            return genome
    return {"n0_phases": [], "metadata": {"confidence_global": 0.85}}


# =============================================================================
# SERVEUR HTTP ET DISTRIBUTION DES TEMPLATES
# =============================================================================

class Handler(BaseHTTPRequestHandler):
    timeout = None  # Disable connection timeout for long Gemini API calls
    
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
        
        # Route /intent-viewer (Mission 32)
        if self.path == '/intent-viewer':
            self.serve_template('intent_viewer.html')
            return

        # Route /brainstorm (Mission 43)
        if self.path == '/brainstorm':
            self.serve_template('brainstorm_war_room.html')
            return

        # Mission 54 — KIMI Polling result
        if self.path.startswith('/api/frd/kimi/result/'):
            job_id = self.path.split('/')[-1]
            with _kimi_jobs_lock:
                job = _kimi_jobs.get(job_id, {"status": "not_found"})
                # On retire le timestamp datetime pour la sérialisation JSON
                res = job.copy()
                if "ts" in res: del res["ts"]
                self.send_json(res)
            return

        # Route /brainstorm-tw (Mission 48 — Tailwind Trial)
        if self.path == '/brainstorm-tw':
            self.serve_template('brainstorm_war_room_tw.html')
            return

        # Route /frd-editor (Mission 49 — FRD Editor)
        if self.path == '/frd-editor':
            self.serve_template('frd_editor.html')
            return

        # Route /frd-editor (Mission 49 — Monaco + Preview + Sullivan Chat)
        if self.path.startswith('/frd-editor'):
            self.serve_template('frd_editor.html')
            return

        # Route GET /api/frd/file?name=<filename> (Mission 45)
        if self.path.startswith('/api/frd/file'):
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            name = params.get('name', [''])[0]
            if not name or '/' in name or '..' in name:
                self.send_error_json(400, "Invalid filename")
                return
            cwd = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(cwd, TEMPLATES_DIR, name)
            if not os.path.exists(file_path):
                self.send_error_json(404, f"File not found: {name}")
                return
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.send_json({"name": name, "content": content})
            return

        # Route GET /api/frd/assets (Mission 51)
        if self.path.startswith('/api/frd/assets'):
            try:
                cwd = os.path.dirname(os.path.abspath(__file__))
                assets_dir = os.path.join(cwd, STATIC_DIR, "assets", "frd")
                assets = []
                if os.path.exists(assets_dir):
                    for f in os.listdir(assets_dir):
                        if os.path.isfile(os.path.join(assets_dir, f)) and not f.startswith('.'):
                            assets.append({"name": f, "url": f"/static/assets/frd/{f}"})
                self.send_json({"assets": assets})
            except Exception as e:
                self.send_error_json(500, f"Assets error: {str(e)}")
            return

        # Route pour le Service Worker (doit être à la racine pour le scope)
        if self.path == '/sw.js':
            self.serve_sw()
            return
        
        # Route API pour le genome
        if self.path == '/api/genome':
            self.send_json(load_genome())
            return
        
        # Route API pour le layout (Mission 19A)
        if self.path == '/api/layout':
            self.send_json(load_layout())
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
        
        # Route API pour les fichiers statiques (CSS, JS)
        if self.path.startswith('/static/'):
            self.serve_static(self.path[8:])
            return

        # Mission 43 — BRS API (GET)
        if self.path == '/api/brs/buffer-questions':
            self.send_json(brs_logic.get_buffer_questions())
            return

        if self.path.startswith('/api/brs/basket/'):
            session_id = self.path.split('/')[-1]
            self.send_json({"session_id": session_id, "basket": brs_logic.storage.get_basket(session_id)})
            return

        if self.path.startswith('/api/brs/stream/'):
            parts = self.path.split('/')
            if len(parts) >= 5:
                session_id = parts[-2]
                provider = parts[-1]
                self._handle_brs_stream(session_id, provider)
                return

        # Route API pour le manifestation (Figma Bridge - Mission 25B)
        if self.path == '/api/manifest':
            manifest_path = Path(__file__).parent.parent.parent / 'exports' / 'manifest.json'
            if manifest_path.exists():
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    self.send_json(json.load(f))
            else:
                self.send_error_json(404, "Genome Manifest not found.")
            return

        # NEW: Route API pour le manifestation du Retro-Genome (Mission 37)
        if self.path == '/api/retro-genome/manifest':
            retro_dir = Path(__file__).parent.parent.parent / 'exports' / 'retro_genome'
            manifest_path = retro_dir / 'manifest.json'
            if manifest_path.exists():
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    self.send_json(json.load(f))
            else:
                self.send_error_json(404, "Retro-Genome Manifest not found. Run export first.")
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

        if self.path == '/genome_canvas':
            p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'genome_canvas.html')
            with open(p, 'r', encoding='utf-8') as f:
                self._send_html(f.read())
            return

        # Route export SVG scaffold (Mission 21A — Genome Design Bridge)
        if self.path.startswith('/api/export/svg'):
            use_kimi = 'kimi=1' in self.path
            svg_bytes = generate_svg(load_genome(), use_kimi=use_kimi).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'image/svg+xml')
            self.send_header('Content-Disposition', 'attachment; filename="genome_scaffold.svg"')
            self.send_header('Content-Length', str(len(svg_bytes)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(svg_bytes)
            return

        # Route /template — serve template_latest.svg raw
        if self.path == '/template' or self.path.startswith('/template?'):
            svg_path = Path(__file__).parent.parent.parent / "exports" / "template_latest.svg"
            if svg_path.exists():
                svg_bytes = svg_path.read_bytes()
                self.send_response(200)
                self.send_header('Content-Type', 'image/svg+xml')
                self.send_header('Cache-Control', 'no-store, must-revalidate')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(svg_bytes)
            else:
                self.send_error(404, "No template yet — run pipeline first")
            return

        # Route /template-viewer — Dual Viewer (Mission 34A/34C)
        if self.path.startswith('/template-viewer'):
            templates_dir = Path(__file__).parent / "static" / "templates"
            retro_dir = Path(__file__).parent.parent.parent / "exports" / "retro_genome"
            
            # Mission 34C/35: Reality only if validated by user OR explicit reality mode
            if 'mode=reality' in self.path or (retro_dir / "validated_analysis.json").exists():
                template_path = templates_dir / "viewer_reality.html"
            else:
                template_path = templates_dir / "viewer_blueprint.html"
            
            if template_path.exists():
                self._send_html(template_path.read_text(encoding="utf-8"))
            else:
                self.send_error(404, f"Template not found at {template_path}")
            return
        if self.path == '/api/pedagogy/gaps':
            retro_dir = Path(__file__).parent.parent.parent / "exports" / "retro_genome"
            f = retro_dir / "validated_analysis.json"
            if f.exists():
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    # Mission 35: Structure is audit -> gaps
                    audit = data.get('audit', {})
                    gaps = audit.get('gaps', [])
                    # Fallback for old Mission 34 format
                    if not gaps:
                        gaps = audit.get('ergonomic_audit', {}).get('gaps', [])
                    
                    self.send_json({"gaps": gaps, "fidelity_score": audit.get('fidelity_score', 0)})
                except Exception as e:
                    self.send_json({"gaps": [], "error": str(e)})
            else:
                self.send_json({"gaps": []})
            return

        # Mission 35 - Serve the generated reality.html
        if self.path == '/api/retro-genome/reality':
            retro_dir = Path(__file__).parent.parent.parent / "exports" / "retro_genome"
            f = retro_dir / "reality.html"
            if f.exists():
                self._send_html(f.read_text(encoding='utf-8'))
            else:
                self._send_html("<div style='padding:50px; color:#666; text-align:center;'>Reality content not yet generated. Please validate analysis first.</div>")
            return

        if self.path.startswith('/api/pipeline-status'):
            with _pipeline_lock:
                self.send_json({'running': _pipeline_running, 'iteration': _pipeline_iteration})
            return

        # Route /api/template-ts — mtime du template_latest.svg pour auto-refresh
        if self.path.startswith('/api/template-ts'):
            svg_path = Path(__file__).parent.parent.parent / "exports" / "template_latest.svg"
            ts = int(svg_path.stat().st_mtime * 1000) if svg_path.exists() else 0
            self.send_json({"ts": ts, "exists": svg_path.exists()})
            return

        # Route /api/template-svg — SVG inline en JSON (bypass SW qui bloque /template)
        if self.path.startswith('/api/template-svg'):
            svg_path = Path(__file__).parent.parent.parent / "exports" / "template_latest.svg"
            if svg_path.exists():
                self.send_json({"svg": svg_path.read_text(encoding="utf-8")})
            else:
                self.send_json({"svg": None})
            return

        # Mission 34D - Progress Status Polling
        if self.path.startswith('/api/retro-genome/status'):
            status_path = Path(__file__).parent.parent.parent / "exports" / "retro_genome" / "upload_status.json"
            retro_dir = Path(__file__).parent.parent.parent / "exports" / "retro_genome"
            
            data = {"step": "idle", "message": ""}
            if status_path.exists():
                try:
                    data = json.loads(status_path.read_text(encoding='utf-8'))
                except Exception:
                    pass
            
            # Mission 37 restart fix: if idle/none but schema exists, we are 'done'
            if data.get("step") in ("idle", None):
                if (retro_dir / "validated_analysis.json").exists():
                    data["step"] = "done"
                    data["message"] = "Schema available for export."

            self.send_json(data)
            return

        self.send_error_json(404, f"Route {self.path} not found")

    def _get_overrides_file(self):
        return Path(__file__).parent.parent.parent / "exports" / "pipeline" / "template_overrides.json"

    def _load_overrides(self):
        f = self._get_overrides_file()
        if f.exists():
            try: return json.loads(f.read_text(encoding="utf-8"))
            except: return {}
        return {}

    def _save_overrides(self, data):
        f = self._get_overrides_file()
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(data, indent=2), encoding="utf-8")

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
        # Route /api/frd/chat (Mission 49)
        if self.path == '/api/frd/chat':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(content_length).decode('utf-8'))
                message = body.get('message', '')
                html_context = body.get('html', '')
                assets = body.get('assets', [])
                
                api_key = os.environ.get('GOOGLE_API_KEY')
                if not api_key:
                    self.send_error_json(500, "GOOGLE_API_KEY non configurée")
                    return

                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent?key={api_key}"
                
                # Inject assets into system prompt
                asset_context = ""
                if assets:
                    asset_context = "\nImages disponibles (utilise ces URLs relatives si pertinent) :\n" + "\n".join(assets)

                system_instruction = (
                    "Tu es Sullivan, assistant de modification d'interface HomeOS.\n"
                    "Tu modifies des fichiers HTML Tailwind CSS selon les instructions du développeur.\n"
                    "Tu réponds TOUJOURS dans ce format exact :\n"
                    "[explication courte en français, 1-2 phrases max]\n"
                    "---HTML---\n"
                    "[fichier HTML complet modifié, rien d'autre]\n"
                    "Règles : ne jamais modifier le <script> • préserver tous les IDs • Tailwind arbitrary values"
                    f"{asset_context}"
                )

                payload = {
                    "contents": [{
                        "parts": [{
                            "text": f"SYSTEM: {system_instruction}\n\nUSER MESSAGE: {message}\n\nCURRENT HTML:\n{html_context}"
                        }]
                    }]
                }
                
                req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
                with urllib.request.urlopen(req) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    raw_text = res_data['candidates'][0]['content']['parts'][0]['text']
                    
                    explanation = ""
                    new_html = ""
                    if "---HTML---" in raw_text:
                        parts = raw_text.split("---HTML---")
                        explanation = parts[0].strip()
                        new_html = parts[1].strip()
                    else:
                        explanation = raw_text
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"explanation": explanation, "html": new_html}).encode('utf-8'))
            except Exception as e:
                self.send_error_json(500, str(e))
            return

            return

        # Route /api/frd/kimi/start (Mission 54)
        if self.path == '/api/frd/kimi/start':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(content_length).decode('utf-8'))
                instruction = body.get('instruction', '')
                html_context = body.get('html', '')

                # Nettoyage optionnel des vieux jobs avant de commencer
                now = datetime.now()
                with _kimi_jobs_lock:
                    to_delete = [jid for jid, job in _kimi_jobs.items() 
                                 if (now - job.get('ts', now)).total_seconds() > 1800]
                    for jid in to_delete: del _kimi_jobs[jid]

                job_id = str(uuid.uuid4())[:8]
                with _kimi_jobs_lock:
                    _kimi_jobs[job_id] = { "status": "pending", "ts": now }
                
                threading.Thread(target=_run_kimi_job, args=(job_id, instruction, html_context), daemon=True).start()
                self.send_json({"job_id": job_id})
            except Exception as e:
                self.send_error_json(500, str(e))
            return

        # Route /api/frd/upload (Mission 51)
        if self.path == '/api/frd/upload':
            try:
                # Manual multipart parsing for Python 3.13+ (no cgi module)
                ctype = self.headers.get('Content-Type')
                if not ctype or 'multipart/form-data' not in ctype:
                    self.send_error_json(400, "Content-Type must be multipart/form-data")
                    return
                
                boundary = ctype.split("boundary=")[1].split(";")[0].strip().encode()
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                
                parts = body.split(b'--' + boundary)
                file_data = None
                filename = None
                
                for part in parts:
                    if b'filename="' in part:
                        # Extract filename
                        fn_match = re.search(b'filename="([^"]+)"', part)
                        if fn_match:
                            filename = fn_match.group(1).decode()
                            # Extract content (after \r\n\r\n)
                            header_end = part.find(b'\r\n\r\n')
                            if header_end != -1:
                                file_data = part[header_end+4:].rstrip(b'\r\n--')
                
                if not filename or not file_data:
                    self.send_error_json(400, "No file found in multipart data")
                    return
                
                # Sanitize filename
                filename = os.path.basename(filename)
                ext = os.path.splitext(filename)[1].lower()
                if ext not in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']:
                    self.send_error_json(400, "Invalid file type")
                    return
                
                assets_dir = os.path.join(cwd, STATIC_DIR, "assets", "frd")
                os.makedirs(assets_dir, exist_ok=True)
                
                dest_path = os.path.join(assets_dir, filename)
                with open(dest_path, 'wb') as f:
                    f.write(file_data)
                
                self.send_json({"url": f"/static/assets/frd/{filename}"})
            except Exception as e:
                self.send_error_json(500, f"Upload error: {str(e)}")
            return

        # Route /api/frd/save (Mission 49)
        if self.path == '/api/frd/save':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(content_length).decode('utf-8'))
                filename = body.get('filename', 'brainstorm_war_room_tw.html')
                html_content = body.get('html', '')
                
                if not filename.endswith('.html') or '/' in filename or '..' in filename:
                    self.send_error_json(400, "Nom de fichier invalide")
                    return

                _cwd = os.path.dirname(os.path.abspath(__file__))
                target_path = os.path.join(_cwd, 'static/templates', filename)
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok", "path": target_path}).encode('utf-8'))
            except Exception as e:
                self.send_error_json(500, str(e))
            return

        # Route POST /api/frd/file (Mission 45 — sauvegarde Monaco)
        if self.path == '/api/frd/file':
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length))
                name = data.get('name', '')
                content = data.get('content', '')
                if not name or '/' in name or '..' in name:
                    self.send_error_json(400, "Invalid filename")
                    return
                cwd = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(cwd, TEMPLATES_DIR, name)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.send_json({"status": "ok", "name": name})
            except Exception as e:
                self.send_error_json(500, str(e))
            return

        # Mission 34C: Validate Intent Mapping
        if self.path == '/api/retro-genome/validate':
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length))
                
                retro_dir = Path(__file__).parent.parent.parent / "exports" / "retro_genome"
                retro_dir.mkdir(parents=True, exist_ok=True)
                
                target = retro_dir / "validated_analysis.json"
                with open(target, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"[MISSION 34C] Validation success: {target}", flush=True)
                self.send_json({"status": "ok", "path": str(target)})
            except Exception as e:
                self.send_error_json(500, f"Validation failed: {str(e)}")
            return

        if self.path.startswith('/api/feedback'):
            global _pipeline_running, _pipeline_iteration
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length) or b'{}')
            feedback = body.get('feedback', '').strip()
            
            with _pipeline_lock:
                if _pipeline_running:
                    self.send_json({'status': 'already_running'})
                    return
                _pipeline_running = True
                _pipeline_iteration += 1
            
            project_root = str(Path(__file__).parent.parent.parent)
            pipeline_script = str(Path(__file__).parent.parent.parent / 'Backend' / 'Prod' / 'pipeline' / 'run_pipeline.py')
            
            def run():
                global _pipeline_running
                try:
                    cmd = [sys.executable, pipeline_script, '--from', '6', '--no-loop']
                    if feedback:
                        cmd += ['--feedback', feedback]
                    subprocess.run(cmd, cwd=project_root, capture_output=True)
                finally:
                    with _pipeline_lock:
                        _pipeline_running = False
            
            t = threading.Thread(target=run, daemon=True)
            t.start()
            self.send_json({'status': 'running'})
            return
        
        if self.path.startswith('/api/accept'):
            exports_dir = Path(__file__).parent.parent.parent / 'exports'
            src = exports_dir / 'template_latest.svg'
            if src.exists():
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                dst_name = f'FINAL_template_{ts}.svg'
                shutil.copy2(src, exports_dir / dst_name)
                self.send_json({'saved': dst_name})
            else:
                self.send_json({'error': 'No template to accept'})
            return

        if self.path == '/api/infer_layout':
            self._handle_infer_layout()
            return
        
        # Route API pour le layout (Mission 19A)
        if self.path == '/api/layout':
            self._handle_layout_post()
            return
        
        if self.path == '/api/organ-move':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            oid = body.get('id')
            if oid:
                ovr = self._load_overrides()
                if oid not in ovr: ovr[oid] = {}
                ovr[oid]['x'] = body.get('x')
                ovr[oid]['y'] = body.get('y')
                self._save_overrides(ovr)
                
                # Regenerate SVG to embed the changes physically
                project_root = str(Path(__file__).parent.parent.parent)
                subprocess.run([sys.executable, str(Path(__file__).parent.parent.parent / 'Backend' / 'Prod' / 'pipeline' / '07_composer.py')], cwd=project_root)
                
                self.send_json({'ok': True})
            else:
                self.send_error_json(400, "Missing organ id")
            return

        if self.path == '/api/comp-move':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            cid = body.get('id')
            if cid:
                ovr = self._load_overrides()
                if cid not in ovr: ovr[cid] = {}
                ovr[cid]['x'] = body.get('x')
                ovr[cid]['y'] = body.get('y')
                ovr[cid]['s'] = body.get('s', 1)
                self._save_overrides(ovr)
                
                # Regenerate SVG to embed the changes physically
                project_root = str(Path(__file__).parent.parent.parent)
                subprocess.run([sys.executable, str(Path(__file__).parent.parent.parent / 'Backend' / 'Prod' / 'pipeline' / '07_composer.py')], cwd=project_root)
                
                self.send_json({'ok': True})
            else:
                self.send_error_json(400, "Missing comp id")
            return

        if self.path == '/api/comp-resize':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            cid = body.get('id')
            if cid:
                ovr = self._load_overrides()
                if cid not in ovr: ovr[cid] = {}
                ovr[cid]['w'] = body.get('w')
                ovr[cid]['h'] = body.get('h')
                self._save_overrides(ovr)
                
                # Regenerate SVG to embed the changes physically
                project_root = str(Path(__file__).parent.parent.parent)
                subprocess.run([sys.executable, str(Path(__file__).parent.parent.parent / 'Backend' / 'Prod' / 'pipeline' / '07_composer.py')], cwd=project_root)
                
                self.send_json({'ok': True})
            else:
                self.send_error_json(400, "Missing comp id")
            return

        # Figma Manifest Patch (Mission 25B)
        if self.path == '/api/manifest/patch':
            manifest_path = Path(__file__).parent.parent.parent / 'exports' / 'manifest.json'
            if not manifest_path.exists():
                self.send_error_json(404, "Manifest not found")
                return
            
            length = int(self.headers.get('Content-Length', 0))
            patch = json.loads(self.rfile.read(length)) if length else {}
            
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            if 'elements' in patch:
                for patch_el in patch['elements']:
                    for el in manifest.get('elements', []):
                        if el.get('id') == patch_el.get('id'):
                            el.update(patch_el)
                            break
                            
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
                
            self.send_json({'ok': True})
            return

        if self.path == '/api/retro-genome/chat':
            self._handle_retro_chat()
            return

        # Mission 34D - Progress Status Polling
        if self.path.startswith('/api/retro-genome/status'):
            status_path = Path(__file__).parent.parent.parent / "exports" / "retro_genome" / "upload_status.json"
            retro_dir = Path(__file__).parent.parent.parent / "exports" / "retro_genome"
            
            data = {"step": "idle", "message": ""}
            if status_path.exists():
                try:
                    data = json.loads(status_path.read_text(encoding='utf-8'))
                except Exception:
                    pass
            
            # Mission 37 restart fix: if idle/none but schema exists, we are 'done'
            if data.get("step") in ("idle", None):
                if (retro_dir / "validated_analysis.json").exists():
                    data["step"] = "done"
                    data["message"] = "Schema available for export."

            self.send_json(data)
            return

        # Mission 32 - Retro Genome Upload
        elif self.path == '/api/retro-genome/approve':
            self._handle_retro_approve()
            return
        elif self.path == '/api/retro-genome/export-zip':
            self._handle_retro_export_zip()
            return
        elif self.path == '/api/retro-genome/export-manifest':
            self._handle_retro_export_manifest()
            return
        elif self.path == '/api/retro-genome/export-schema':
            self._handle_retro_export_schema()
            return
        elif self.path == '/api/retro-genome/generate-html':
            self._handle_retro_generate_html()
            return
        elif self.path == '/api/retro-genome/generate-prd':
            self._handle_retro_prd_gen()
            return
        elif self.path == '/api/retro-genome/upload':
            self._handle_retro_upload()
            return
        elif self.path == '/api/retro-genome/upload-svg':
            self._handle_retro_upload_svg()
            return
            
        # Mission 43 — BRS API (POST)
        elif self.path == '/api/brs/dispatch':
            self._handle_brs_dispatch()
            return

        elif self.path == '/api/brs/capture':
            self._handle_brs_capture()
            return

        elif self.path == '/api/brs/generate-prd':
            self._handle_brs_generate_prd()
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

    def _handle_layout_post(self):
        """Met à jour le layout.json (merge)."""
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
        except Exception as e:
            self.send_error_json(400, f"Invalid JSON body: {e}")
            return

        layout = load_layout()
        # Merge body into layout
        for organ_id, dims in body.items():
            layout[organ_id] = dims
        
        save_layout(layout)
        self.send_json({"ok": True, "count": len(body)})

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

    def _handle_retro_upload(self):
        """Handle multi-PNG upload and manifesto for Retro Genome analysis."""
        try:
            content_type = self.headers.get('Content-Type')
            if not content_type or 'multipart/form-data' not in content_type:
                self.send_error_json(400, "Content-Type must be multipart/form-data")
                return

            if 'boundary=' not in content_type:
                self.send_error_json(400, "Missing boundary in Content-Type")
                return
                
            boundary = content_type.split("boundary=")[1].split(";")[0].strip().encode()
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)

            # Basic multipart parsing
            parts = body.split(b'--' + boundary)
            images_data = []
            manifesto_text = ""

            for part in parts:
                if b'Content-Disposition: form-data; name="images"' in part:
                    subparts = part.split(b'\r\n\r\n')
                    if len(subparts) > 1:
                        img_data = subparts[1].split(b'\r\n--')[0].strip()
                        if img_data:
                            images_data.append(img_data)
                elif b'Content-Disposition: form-data; name="manifesto"' in part:
                    subparts = part.split(b'\r\n\r\n')
                    if len(subparts) > 1:
                        manifesto_text = subparts[1].split(b'\r\n--')[0].strip().decode('utf-8', errors='ignore')

            if not images_data:
                self.send_error_json(400, "No 'images' found in upload")
                return

            # Save PNGs
            retro_dir = Path(__file__).parent.parent.parent / "exports" / "retro_genome"
            retro_dir.mkdir(parents=True, exist_ok=True)
            
            saved_paths = []
            ts = datetime.now().strftime('%H%M%S')
            for i, data in enumerate(images_data):
                p = retro_dir / f"upload_{ts}_{i}.png"
                p.write_bytes(data)
                saved_paths.append(p)

            _write_retro_status("vision", f"Inférence sémantique sur {len(saved_paths)} mockups...")

            # Run analyzer (VisualDecomposer) - handles multiple PNGs
            analyzer = RetroGenomeAnalyzer()
            if len(saved_paths) > 1:
                analysis_result = asyncio.run(analyzer.analyze_multiple(saved_paths))
            else:
                analysis_result = asyncio.run(analyzer.analyze_png(saved_paths[0]))
            
            _write_retro_status("mapping", "Mise en tension : Manifeste ↔ Mockups...")

            # Run SemanticMatcher with the manifesto
            mapper = IntentMapper()
            audit_result = asyncio.run(mapper.map_intents(analysis_result, manifest=manifesto_text))
            
            _write_retro_status("saving", "Sauvegarde du diagnostic...")

            # Save result
            result_path = retro_dir / f"analysis_{ts}.json"
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump({"analysis": analysis_result, "audit": audit_result, "manifesto": manifesto_text}, f, indent=2, ensure_ascii=False)
            
            _write_retro_status("done", "Mission accomplie. Analyse disponible.")

            self.send_json({
                "status": "ok",
                "analysis": analysis_result,
                "audit": audit_result,
                "json_path": str(result_path)
            })

        except Exception as e:
            import traceback
            print(f"[RETRO_GENOME] ERROR: {e}\n{traceback.format_exc()}", flush=True)
            self.send_error_json(500, f"Retro Genome failed: {str(e)}")

    def _handle_retro_upload_svg(self):
        """POST /api/retro-genome/upload-svg — Ingress SVG Figma (Mission 41)."""
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
        except Exception as e:
            self.send_error_json(400, f"Invalid JSON: {e}")
            return

        svg_string = body.get('svg', '')
        frame_name = body.get('name', 'unnamed_frame')

        if not svg_string:
            self.send_error_json(400, "Missing 'svg' field")
            return

        # Sauvegarde SVG brut pour inspection
        from datetime import datetime
        retro_dir = Path(__file__).parent.parent.parent / "exports" / "retro_genome"
        retro_dir.mkdir(parents=True, exist_ok=True)
        safe_name = (frame_name or "frame").replace(" ", "_").replace("/", "_")[:40]
        svg_path = retro_dir / f"SVG_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.svg"
        svg_path.write_text(svg_string, encoding="utf-8")

        try:
            from Backend.Prod.retro_genome.svg_parser import parse_figma_svg
            from Backend.Prod.retro_genome.archetype_detector import ArchetypeDetector
            analysis = parse_figma_svg(svg_string)
            archetype = ArchetypeDetector().detect(analysis)
            self.send_json({
                "status": "ok",
                "visual_analysis": analysis,
                "archetype": archetype,
                "design_tokens": analysis.get("design_tokens", {}),
                "svg_saved": str(svg_path),
                "source": "figma_svg"
            })
        except Exception as e:
            self.send_error_json(500, f"SVG processing failed: {e}")

    def _handle_retro_generate_html(self):
        """Mission 35 — Génère le HTML/CSS de la Reality View depuis le JSON validé + PNG."""
        try:
            retro_dir = Path(__file__).parent.parent.parent / "exports" / "retro_genome"
            validated_path = retro_dir / "validated_analysis.json"

            if not validated_path.exists():
                self.send_error_json(400, "No validated_analysis.json found. Validate first.")
                return

            with open(validated_path, 'r', encoding='utf-8') as f:
                validated = json.load(f)

            # Find the most recent uploaded PNG
            pngs = sorted(retro_dir.glob("upload_*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
            if not pngs:
                self.send_error_json(400, "No source PNG found in retro_genome exports.")
                return

            png_path = pngs[0]
            
            generator = HtmlGenerator()
            
            # On simule la granularité ici car asyncio.run est bloquant pour le thread
            # Mais on peut mettre à jour le statut juste avant l'appel global ou 
            # modifier HtmlGenerator pour qu'il accepte un callback de status.
            
            # Option choisie : passer une fonction de callback à generator.generate
            def status_cb(msg, step="generating", **kwargs):
                _write_retro_status(step, msg, **kwargs)
                print(f"[{step.upper()}] {msg}", flush=True)

            html = asyncio.run(generator.generate(png_path=png_path, matched_analysis=validated, status_callback=status_cb))
            _write_retro_status("done", "Reality View prête.")

            self.send_json({
                "status": "ok",
                "html_path": str(retro_dir / "reality.html"),
                "html_length": len(html)
            })

        except Exception as e:
            import traceback
            print(f"[GENERATE_HTML] ERROR: {e}\n{traceback.format_exc()}", flush=True)
            self.send_error_json(500, f"HTML generation failed: {str(e)}")

    def _handle_retro_approve(self):
        """HCI: Approval by the Human Director."""
        try:
            # On passe simplement le statut à 'done'
            _write_retro_status("done", "Rendu validé par le Directeur. Prêt pour export.")
            self.send_json({"status": "ok", "message": "Approval recorded"})
        except Exception as e:
            self.send_error_json(500, f"Approval failed: {str(e)}")

    def _handle_retro_export_zip(self):
        """Packaging reality.html + css in a ZIP."""
        try:
            from Backend.Prod.retro_genome.exporter_vanilla import export_as_zip
            retro_dir = Path(__file__).parent.parent.parent / "exports" / "retro_genome"
            html_path = retro_dir / "reality.html"
            if not html_path.exists():
                self.send_error_json(400, "reality.html not found.")
                return
            
            html_content = html_path.read_text(encoding='utf-8')
            zip_path = export_as_zip("AetherFlow_Reality", html_content, retro_dir)
            
            self.send_json({"status": "ok", "zip_path": str(zip_path)})
        except Exception as e:
            self.send_error_json(500, f"ZIP export failed: {str(e)}")

    def _handle_retro_export_manifest(self):
        """Inferring manifest.json for Figma Bridge."""
        try:
            from Backend.Prod.retro_genome.manifest_inferer import ManifestInferer
            retro_dir = Path(__file__).parent.parent.parent / "exports" / "retro_genome"
            html_path = retro_dir / "reality.html"
            if not html_path.exists():
                self.send_error_json(400, "reality.html not found.")
                return
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            manifest = loop.run_until_complete(ManifestInferer.infer_from_html(html_path))
            
            output_path = retro_dir / "manifest.json"
            ManifestInferer.save_manifest(manifest, output_path)
            
            # Mission 37: Do NOT overwrite the main manifest anymore. 
            # Differentiate endpoints instead.
            
            self.send_json({"status": "ok", "manifest_path": str(output_path)})
        except Exception as e:
            self.send_error_json(500, f"Manifest inference failed: {str(e)}")

    def _handle_retro_export_schema(self):
        """Exporting the validated analysis JSON schema."""
        try:
            retro_dir = Path(__file__).parent.parent.parent / "exports" / "retro_genome"
            schema_path = retro_dir / "validated_analysis.json"
            if not schema_path.exists():
                self.send_error_json(400, "validated_analysis.json not found.")
                return
            
            # Optionally format it or just return the path
            self.send_json({"status": "ok", "schema_path": str(schema_path)})
        except Exception as e:
            self.send_error_json(500, f"Schema export failed: {str(e)}")

    def _handle_retro_prd_gen(self):
        """Invoke PRD and Roadmap generation from last analysis data."""
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length) or b'{}')
            analysis_data = body.get('data')
            project_name = body.get('project_name', 'Analyzed Mockup')

            if not analysis_data:
                retro_dir = Path(__file__).parent.parent.parent / "exports" / "retro_genome"
                validated_path = retro_dir / "validated_analysis.json"
                if validated_path.exists():
                    with open(validated_path, 'r', encoding='utf-8') as f:
                        analysis_data = json.load(f)
                else:
                    self.send_error_json(400, "Missing analysis data and no validated_analysis.json found")
                    return

            generator = PRDGenerator()
            result = asyncio.run(generator.generate(analysis_data, project_name))

            self.send_json({
                "status": "ok",
                "prd_path": result['prd_path'],
                "roadmap_path": result['roadmap_path'],
                "project_name": project_name
            })

        except Exception as e:
            self.send_error_json(500, f"PRD generation failed: {str(e)}")

    def _handle_retro_chat(self):
        """Invoke HTML Refinement via Sullivan Chat."""
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length) or b'{}')
            feedback = body.get('feedback', '').strip()
            current_html = body.get('current_html', '').strip()
            
            if not feedback or not current_html:
                self.send_error_json(400, "Missing feedback or current_html")
                return
                
            retro_dir = Path(__file__).parent.parent.parent / "exports" / "retro_genome"
            pngs = list(retro_dir.glob("*.png"))
            png_path = pngs[0] if pngs else None
            
            generator = HtmlGenerator()
            
            # Note: could be async, running it synchronously for now to keep the flow identical to PRD
            new_html = asyncio.run(generator.refine(
                current_html=current_html,
                feedback=feedback,
                png_path=png_path
            ))
            
            self.send_json({
                "status": "ok",
                "html_path": str(retro_dir / "reality.html"),
                "html_length": len(new_html)
            })
            
        except Exception as e:
            import traceback
            print(f"[RETRO_CHAT] ERROR: {e}\n{traceback.format_exc()}", flush=True)
            self.send_error_json(500, f"HTML refinement failed: {str(e)}")

    # --- Mission 43 BRS Handlers ---

    def _handle_brs_dispatch(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            session_id = data.get('session_id')
            prompt = data.get('prompt')
            if not session_id or not prompt:
                self.send_error_json(400, "Missing session_id or prompt")
                return
            buffer_answers = data.get('buffer_answers') or {}
            result = asyncio.run(brs_logic.dispatch_brainstorm(session_id, prompt, buffer_answers))
            self.send_json(result)
        except Exception as e:
            self.send_error_json(500, str(e))

    def _handle_brs_stream(self, session_id, provider):
        """SSE handler pour le brainstorm streaming."""
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.send_header('X-Accel-Buffering', 'no')
        self.end_headers()

        try:
            # On utilise asyncio pour le générateur
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            gen = brs_logic.sse_generator(session_id, provider)
            
            async def run_gen():
                async for chunk in gen:
                    self.wfile.write(chunk.encode('utf-8'))
                    self.wfile.flush()
            
            loop.run_until_complete(run_gen())
        except Exception as e:
            print(f"[BRS_STREAM] SSE Error: {e}", flush=True)
        finally:
            try:
                loop.close()
            except:
                pass

    def _handle_brs_capture(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            session_id = data.get('session_id')
            text = data.get('text')
            provider = data.get('provider')
            if not all([session_id, text, provider]):
                self.send_error_json(400, "Missing fields")
                return
            
            nugget = brs_logic.capture_nugget(session_id, text, provider)
            self.send_json({"status": "ok", "nugget_id": nugget["id"]})
        except Exception as e:
            self.send_error_json(500, str(e))

    def _handle_brs_generate_prd(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            session_id = data.get('session_id')
            project_name = data.get('project_name')
            if not session_id or not project_name:
                self.send_error_json(400, "Missing fields")
                return
            
            result = asyncio.run(brs_logic.generate_prd_from_basket(session_id, project_name))
            self.send_json(result)
        except Exception as e:
            self.send_error_json(500, str(e))

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


def load_layout():
    """Charge le layout canvas depuis le fichier JSON"""
    filepath = LAYOUT_FILE
    if not os.path.exists(filepath):
        cwd = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(cwd, LAYOUT_FILE)
    
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}


def save_layout(data):
    """Sauvegarde le layout sur disque."""
    filepath = LAYOUT_FILE
    if not os.path.exists(os.path.dirname(os.path.abspath(filepath))):
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), LAYOUT_FILE)
    else:
        cwd_local = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(cwd_local, LAYOUT_FILE)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


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
    _load_env()
    server = ThreadingHTTPServer(('0.0.0.0', PORT), Handler)
    print(f"🧬 Serveur Genome lancé sur http://localhost:{PORT}")
    print(f"   - Viewer:        http://localhost:{PORT}/")
    print(f"   - Stenciler:     http://localhost:{PORT}/stenciler")
    print(f"   - API Genome:    http://localhost:{PORT}/api/genome")
    print(f"   - InferLayout:   http://localhost:{PORT}/api/infer_layout  (POST)")
    print(f"   - Preview HTML:  http://localhost:{PORT}/preview")
    server.serve_forever()
