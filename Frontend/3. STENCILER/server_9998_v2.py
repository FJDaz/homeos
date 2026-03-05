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
import threading
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

# Ajout du chemin pour importer les modules Backend
cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(cwd, "../.."))
sys.path.append(os.path.join(cwd, "../../Backend/Prod"))
sys.path.append(os.path.join(cwd, "../../Backend/_archive"))

from sullivan.context_pruner import prune_genome
from genome_preview import render_genome_preview
from exporters.genome_to_svg import generate_svg

PORT = 9998
GENOME_FILE = "../2. GENOME/genome_reference.json"
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

        # Route API pour le manifestation (Figma Bridge - Mission 25B)
        if self.path == '/api/manifest':
            manifest_path = Path(__file__).parent.parent.parent / 'exports' / 'manifest.json'
            if manifest_path.exists():
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    self.send_json(json.load(f))
            else:
                self.send_error_json(404, "Manifest not found. Run composer first.")
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

        # Route /template-viewer — XHR inline SVG injection + Drag/Resize (24C)
        if self.path == '/template-viewer':
            html = """<!DOCTYPE html><html><head><meta charset="utf-8">
<title>KIMI Template Viewer</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{height:100%;background:#1a1a1a}
body{display:flex;flex-direction:column}
#bar{width:100%;background:#111;color:#666;font:11px/28px monospace;padding:0 16px;display:flex;gap:16px;align-items:center;border-bottom:1px solid #2a2a2a;flex-shrink:0;height:28px}
#dot{width:7px;height:7px;border-radius:50%;background:#333;flex-shrink:0;transition:background .3s}
#dot.live{background:#4caf50}
#main{flex:1;display:flex;overflow:hidden}
#canvas{flex:1;min-width:0;background:#f0eeea;padding:32px;display:flex;justify-content:center;align-items:flex-start;overflow:auto}
#canvas svg{max-width:1440px;width:100%;height:auto;display:block;box-shadow:0 8px 40px rgba(0,0,0,.18)}
#empty{color:#555;font:13px monospace;margin:auto;text-align:center;line-height:2}
#chat{width:340px;flex-shrink:0;background:#111;border-left:1px solid #2a2a2a;display:flex;flex-direction:column;font:12px monospace;overflow:hidden}
#chat-title{padding:10px 14px;color:#666;border-bottom:1px solid #1e1e1e;font-size:11px;letter-spacing:.05em}
#messages{flex:1;overflow-y:auto;padding:10px 14px;display:flex;flex-direction:column;gap:6px}
.msg{color:#888;line-height:1.5;padding:4px 0;border-bottom:1px solid #1a1a1a}
.msg.sent{color:#aaa}
.msg.ok{color:#4caf50}
.msg.err{color:#e57373}
.msg.running{color:#ffb74d}
#chat-input{border-top:1px solid #1e1e1e;padding:10px 14px;display:flex;flex-direction:column;gap:8px}
#txt{background:#0d0d0d;border:1px solid #2a2a2a;color:#ccc;font:12px monospace;padding:8px;resize:none;height:72px;width:100%;outline:none;border-radius:2px}
#txt:focus{border-color:#444}
#btns{display:flex;gap:8px}
#btn-send,#btn-accept{flex:1;padding:7px 0;border:none;cursor:pointer;font:11px monospace;border-radius:2px;transition:opacity .2s}
#btn-send{background:#2a2a2a;color:#ccc}
#btn-send:hover{background:#333}
#btn-accept{background:#1b3a1b;color:#4caf50}
#btn-accept:hover{background:#1f4a1f}
#btn-send:disabled,#btn-accept:disabled{opacity:.4;cursor:default}

/* Interaction SVG (24D) */
svg .af-organ { cursor: grab; }
svg .af-organ:active { cursor: grabbing; }
svg .af-organ:hover > rect:first-child { stroke: #1258ca; stroke-dasharray: 4; }
svg .af-organ.selected > rect:first-child { stroke: #f05e23; stroke-width: 2; stroke-dasharray: none; }
svg .kimi-comp.selected > rect:first-child { stroke: #f05e23; stroke-width: 2; stroke-dasharray: none; }
svg .kimi-comp.selected .resize-handle { opacity: 1 !important; fill: #fff; }
svg .kimi-comp.hovered > rect:first-child { stroke: #1258ca; stroke-width: 2; stroke-dasharray: none; }
</style>
<script>
var lastTs=0,lastRunning=false;
// --- Pipeline & Chat Logic ---
function addMsg(text,cls){
  var d=document.getElementById('messages');
  var m=document.createElement('div');m.className='msg '+(cls||'');
  m.textContent=text;d.appendChild(m);
  d.scrollTop=d.scrollHeight;
}
function setButtons(on){
  document.getElementById('btn-send').disabled=!on;
  document.getElementById('btn-accept').disabled=!on;
}
function loadSVG(){
  var x=new XMLHttpRequest();
  x.open('GET','/api/template-svg?t='+Date.now(),true);
  x.onload=function(){
    try{
      var d=JSON.parse(x.responseText);
      if(d.svg&&d.svg.indexOf('<svg')!==-1){
        document.getElementById('canvas').innerHTML=d.svg;
        document.getElementById('ts').textContent='Rendu '+new Date().toLocaleTimeString();
        var dot=document.getElementById('dot');dot.className='live';
        setTimeout(function(){dot.className='';},2000);
        setTimeout(initInteraction,100); // Initialize interaction logic when SVG loads
      }
    }catch(e){}
  };
  x.send();
}
function pollTemplate(){
  var x=new XMLHttpRequest();
  x.open('GET','/api/template-ts?t='+Date.now(),true);
  x.onload=function(){
    try{var d=JSON.parse(x.responseText);if(d.ts&&d.ts!==lastTs){lastTs=d.ts;loadSVG();}}catch(e){}
  };
  x.send();
}
function pollStatus(){
  var x=new XMLHttpRequest();
  x.open('GET','/api/pipeline-status?t='+Date.now(),true);
  x.onload=function(){
    try{
      var d=JSON.parse(x.responseText);
      if(d.running&&!lastRunning){addMsg('⟳ Génération en cours...','running');setButtons(false);}
      if(!d.running&&lastRunning){addMsg('✓ Template mis à jour','ok');setButtons(true);loadSVG();}
      lastRunning=d.running;
    }catch(e){}
  };
  x.send();
}
function sendFeedback(){
  var txt=document.getElementById('txt').value.trim();
  if(!txt)return;
  var x=new XMLHttpRequest();
  x.open('POST','/api/feedback',true);
  x.setRequestHeader('Content-Type','application/json');
  x.onload=function(){try{var d=JSON.parse(x.responseText);if(d.status==='already_running')addMsg('⚠ Pipeline déjà en cours','err');}catch(e){}};
  x.send(JSON.stringify({feedback:txt}));
  addMsg('→ '+txt,'sent');
  document.getElementById('txt').value='';
}
function acceptTemplate(){
  var x=new XMLHttpRequest();
  x.open('POST','/api/accept',true);
  x.setRequestHeader('Content-Type','application/json');
  x.onload=function(){try{var d=JSON.parse(x.responseText);addMsg('✓ Sauvegardé : '+d.saved,'ok');}catch(e){}};
  x.send(JSON.stringify({}));
}
document.addEventListener('keydown',function(e){
  if((e.ctrlKey||e.metaKey)&&e.key==='Enter'){e.preventDefault();sendFeedback();}
});
window.onload=function(){
  pollTemplate();setInterval(pollTemplate,3000);
  pollStatus();setInterval(pollStatus,2000);
  document.getElementById('btn-send').onclick=sendFeedback;
  document.getElementById('btn-accept').onclick=acceptTemplate;
  addMsg('Viewer prêt. Tape un feedback et appuie sur Envoyer.');
};

// --- SVG Interaction Logic (24D) ---
var selectedOrgan = null;
var selectedComp = null;
var isDragging = false;
var isDraggingComp = false;
var isResizing = false;
var dragStart = {x:0, y:0};
var startTransform = {tx:0, ty:0, s:1};

function getTransformParams(el) {
    var transform = el.getAttribute('transform');
    if (!transform) return {tx:0, ty:0, s:1};
    var tMatch = transform.match(/translate\\(([^,]+),\\s*([^)]+)\\)/);
    var sMatch = transform.match(/scale\\(([^)]+)\\)/);
    var tx = tMatch ? parseFloat(tMatch[1]) : 0;
    var ty = tMatch ? parseFloat(tMatch[2]) : 0;
    var s = sMatch ? parseFloat(sMatch[1]) : 1;
    return {tx:tx, ty:ty, s:s};
}

function setTransformParams(el, p) {
    el.setAttribute('transform', 'translate('+p.tx+','+p.ty+') scale('+p.s+')');
}

function initInteraction() {
  var svg = document.querySelector('#canvas svg');
  if(!svg) return;
  var pt = svg.createSVGPoint();

  function getMousePosition(evt) {
    pt.x = evt.clientX;
    pt.y = evt.clientY;
    return pt.matrixTransform(svg.getScreenCTM().inverse());
  }

  svg.addEventListener('mousedown', function(evt) {
    var resizeHandle = evt.target.closest('.resize-handle');
    var gComp = evt.target.closest('.kimi-comp');
    var gOrgan = evt.target.closest('.af-organ');
    
    // Component scale/resize is still allowed (from 24C)
    if(resizeHandle && gComp) {
      isResizing = true;
      selectedComp = gComp;
      var mousePt = getMousePosition(evt);
      dragStart = {x: mousePt.x, y: mousePt.y};
      startTransform = getTransformParams(selectedComp);
      evt.preventDefault();
      evt.stopPropagation();
      return;
    }

    // Component Drag (Atom level)
    if (gComp) {
      if(selectedComp) selectedComp.classList.remove('selected');
      selectedComp = gComp;
      selectedComp.classList.add('selected');
      
      var mousePt = getMousePosition(evt);
      dragStart = {x: mousePt.x, y: mousePt.y};
      startTransform = getTransformParams(selectedComp);
      isDraggingComp = true;
      evt.preventDefault();
      evt.stopPropagation();
      return;
    }

    // Organ Drag
    if(gOrgan) {
      if(selectedOrgan) selectedOrgan.classList.remove('selected');
      selectedOrgan = gOrgan;
      selectedOrgan.classList.add('selected');
      
      var mousePt = getMousePosition(evt);
      dragStart = {x: mousePt.x, y: mousePt.y};
      startTransform = getTransformParams(selectedOrgan);
      isDragging = true;

      // Handle Component Selection (no drag)
      if(selectedComp) selectedComp.classList.remove('selected');
      selectedComp = gComp;
      if(selectedComp) selectedComp.classList.add('selected');
    } else {
      if(selectedOrgan) selectedOrgan.classList.remove('selected');
      selectedOrgan = null;
      if(selectedComp) selectedComp.classList.remove('selected');
      selectedComp = null;
    }
  });

  // --- PEDAGOGICAL DEVICE ---
  // Wait for fetch...
  var pedagogicalDict = {};
  fetch('/api/genome')
    .then(r => r.json())
    .then(data => {
      // Build a flat dictionary of N3 components
      if(data && data.n0_phases) {
        data.n0_phases.forEach(ph => {
          (ph.n1_sections||[]).forEach(org => {
            (org.n2_features||[]).forEach(feat => {
              (feat.n3_components||[]).forEach(comp => {
                // Map component ID to its parent feature (N2) for pedagogical context
                pedagogicalDict[comp.id] = {
                  atom: comp,
                  feature: feat,
                  organ: org
                };
              });
            });
          });
        });
      }
    }).catch(e => console.error(e));

  var lastHoveredComp = null;
  var pedoPanel = document.getElementById('pedagogical-panel');
  var pedoTitle = document.getElementById('pedo-title');
  var pedoRole = document.getElementById('pedo-role');
  var pedoIntent = document.getElementById('pedo-intent');
  
  document.getElementById('btn-quick-prompt').onclick = function() {
    if(lastHoveredComp) {
      document.getElementById('txt').value = "Examine l'atome N3 \\"" + lastHoveredComp.atom.name + "\\" (ID: " + lastHoveredComp.atom.id + "), appartenant à la Cellule N2 \\"" + lastHoveredComp.feature.name + "\\".\\nLe Genome spécifie pour cet atome :\\n- Rôle UX : " + (lastHoveredComp.atom.ui_role || "?") + "\\n- Intent-Code N3 : " + (lastHoveredComp.atom.intent_code || "?") + "\\n(Contexte N2 : " + (lastHoveredComp.feature.doc_sens_humain || "?") + ")\\n\\nPenses-tu que ce composant frontend y réponde efficacement ? Que proposerais-tu d'améliorer ?";
      document.getElementById('txt').focus();
    }
  };

  svg.addEventListener('mousemove', function(evt) {
    if(isResizing && selectedComp) {
      var mousePt = getMousePosition(evt);
      var dx = mousePt.x - dragStart.x;
      var scaleDelta = dx / 300; 
      var newS = Math.max(0.1, startTransform.s + scaleDelta);
      setTransformParams(selectedComp, {tx: startTransform.tx, ty: startTransform.ty, s: newS});
    } else if(isDraggingComp && selectedComp) {
      var mousePt = getMousePosition(evt);
      var dx = mousePt.x - dragStart.x;
      var dy = mousePt.y - dragStart.y;
      setTransformParams(selectedComp, {tx: startTransform.tx + dx, ty: startTransform.ty + dy, s: startTransform.s});
    } else if(isDragging && selectedOrgan) {
      var mousePt = getMousePosition(evt);
      var dx = mousePt.x - dragStart.x;
      var dy = mousePt.y - dragStart.y;
      setTransformParams(selectedOrgan, {tx: startTransform.tx + dx, ty: startTransform.ty + dy, s: startTransform.s});
    } else {
      // Hover detection for pedagogical device
      var gComp = evt.target.closest('.kimi-comp');
      if(gComp && !isDragging && !isResizing && !isDraggingComp) {
        var compId = gComp.getAttribute('id');
        var context = pedagogicalDict[compId];
        if(context) {
           lastHoveredComp = context;
           pedoTitle.innerText = "N2: " + context.feature.name + " / N3: " + context.atom.name;
           
           var atomRole = context.atom.ui_role || "Role inconnu";
           var atomIntent = context.atom.intent_code || "Intent inconnu";
           var featSens = context.feature.doc_sens_humain || "Non documenté";
           
           pedoRole.innerHTML = "<strong>Role N3 :</strong> " + atomRole;
           
           pedoIntent.innerHTML = 
             "<div style='margin-bottom:8px; border-bottom:1px solid #333; padding-bottom:6px;'><b>Intent N3 (Code) :</b> " + atomIntent + "</div>" +
             "<div><b>Contexte N2 (Feature UX) :</b> " + featSens + "</div>";
             
           pedoPanel.style.display = 'block';
           
           // Highlight current
           document.querySelectorAll('.kimi-comp').forEach(c => c.classList.remove('hovered'));
           gComp.classList.add('hovered');
        }
      } else {
         document.querySelectorAll('.kimi-comp').forEach(c => c.classList.remove('hovered'));
      }
    }
  });

  svg.addEventListener('mouseup', function(evt) {
    if(isDragging && selectedOrgan) {
      isDragging = false;
      var finalT = getTransformParams(selectedOrgan);
      if(finalT.tx !== startTransform.tx || finalT.ty !== startTransform.ty) {
        var xReq = new XMLHttpRequest();
        xReq.open('POST','/api/organ-move',true);
        xReq.setRequestHeader('Content-Type','application/json');
        xReq.send(JSON.stringify({id: selectedOrgan.id, x: Math.round(finalT.tx), y: Math.round(finalT.ty)}));
        addMsg('📌 Organe déplacé : '+selectedOrgan.id);
      }
    } else if(isDraggingComp && selectedComp) {
      isDraggingComp = false;
      var finalT = getTransformParams(selectedComp);
      if(finalT.tx !== startTransform.tx || finalT.ty !== startTransform.ty) {
        var xReq = new XMLHttpRequest();
        xReq.open('POST','/api/comp-move',true); // This endpoint accepts x, y, and s
        xReq.setRequestHeader('Content-Type','application/json');
        xReq.send(JSON.stringify({id: selectedComp.id, x: Math.round(finalT.tx), y: Math.round(finalT.ty), s: finalT.s}));
        addMsg('📌 Atome déplacé : ' + selectedComp.id);
      }
    } else if(isResizing && selectedComp) {
      isResizing = false;
      var finalT = getTransformParams(selectedComp);
      if(finalT.s !== startTransform.s) {
        var xReq = new XMLHttpRequest();
        xReq.open('POST','/api/comp-move',true); // Keeping scale as comp-move for now
        xReq.setRequestHeader('Content-Type','application/json');
        xReq.send(JSON.stringify({id: selectedComp.id, x: Math.round(finalT.tx), y: Math.round(finalT.ty), s: finalT.s}));
        addMsg('📌 Échelle atome persistée : '+selectedComp.id);
      }
    }
  });
}
</script></head><body>
<div id="bar">
  <div id="dot"></div>
  <span style="color:#aaa">KIMI Template Viewer</span>
  <span id="ts" style="color:#555">En attente...</span>
  <span style="margin-left:auto;color:#333">XHR · 3s</span>
</div>
<div id="main">
  <div id="canvas"><div id="empty">En attente du pipeline...</div></div>
  <div id="chat">
    <div id="chat-title">KIMI FEEDBACK</div>
    
    <!-- PEDAGOGICAL PANEL -->
    <div id="pedagogical-panel" style="display:none; padding:12px; background:#1e1e1e; border-bottom:1px solid #333; flex-shrink:0;">
      <div id="pedo-title" style="color:#fff; font-weight:700; margin-bottom:4px; font-size:12px;">Composant</div>
      <div id="pedo-role" style="color:#aaa; margin-bottom:8px; font-size:11px;">Rôle UI</div>
      <div id="pedo-intent" style="color:#d4b2bc; margin-bottom:10px; line-height:1.4; font-style:italic; font-size:12px;">Intention génome</div>
      <button id="btn-quick-prompt" style="background:#5c7aff; color:#fff; border:none; padding:6px 10px; border-radius:4px; cursor:pointer; font-family:'Inter', sans-serif; font-size:11px; width:100%; font-weight:600; text-align:left;">
        <span style="opacity:0.7">↳</span> Poser une question sur ce design
      </button>
    </div>
    
    <div id="messages"></div>
    <div id="chat-input">
      <textarea id="txt" placeholder="Décris ce que tu veux changer...&#10;Cmd+Enter pour envoyer"></textarea>
      <div id="btns">
        <button id="btn-send">Envoyer</button>
        <button id="btn-accept">✓ Accepter</button>
      </div>
    </div>
  </div>
</div>
</body></html>"""
            self._send_html(html)
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
            
            # Merge logic for Figma extra data or sync
            if 'figma_extra' in patch:
                manifest['figma_extra'] = patch['figma_extra']
            if 'components' in patch:
                for cid, data in patch['components'].items():
                    if cid in manifest['components']:
                        manifest['components'][cid].update(data)
            
            manifest['last_updated'] = datetime.now().isoformat()
            
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
            
            self.send_json({"ok": True})
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
    server = ThreadingHTTPServer(('0.0.0.0', PORT), Handler)
    print(f"🧬 Serveur Genome lancé sur http://localhost:{PORT}")
    print(f"   - Viewer:        http://localhost:{PORT}/")
    print(f"   - Stenciler:     http://localhost:{PORT}/stenciler")
    print(f"   - API Genome:    http://localhost:{PORT}/api/genome")
    print(f"   - InferLayout:   http://localhost:{PORT}/api/infer_layout  (POST)")
    print(f"   - Preview HTML:  http://localhost:{PORT}/preview")
    server.serve_forever()
