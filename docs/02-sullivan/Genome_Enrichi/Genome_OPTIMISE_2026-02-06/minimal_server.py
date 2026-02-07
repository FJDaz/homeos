#!/usr/bin/env python3
"""Serveur minimal pour tester le template IR + Genome"""
import json
import re
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

# Parser les données
def parse_ir_visuel():
    ir_path = Path("/Users/francois-jeandazin/AETHERFLOW/output/studio/ir_visuel_edite.md")
    endpoints = []
    if not ir_path.exists():
        return []
    content = ir_path.read_text(encoding="utf-8")
    lines = content.split('\n')
    for line in lines:
        match = re.match(
            r'\|\s*[^|]+\s+(GET|POST|PUT|DELETE|PATCH)\s*\|\s*`([^`]+)`\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*`([^`]+)`',
            line
        )
        if match:
            method, path, ui_hint, visual, component = match.groups()
            endpoints.append({
                "method": method.strip(),
                "path": path.strip(),
                "ui_hint": ui_hint.strip(),
                "visual_hint": visual.strip(),
                "visual_emoji": "",
                "component_ref": component.strip(),
                "wireframe": f"{visual.strip()} -> {component.strip()}"
            })
    return endpoints

def parse_genome_enrichi():
    genome_path = Path("/Users/francois-jeandazin/AETHERFLOW/output/studio/genome_enrichi.json")
    if not genome_path.exists():
        return []
    data = json.loads(genome_path.read_text(encoding="utf-8"))
    corps_list = []
    for corps in data.get("genome", {}).get("corps", []):
        organes_list = []
        for organe in corps.get("organes", []):
            atomes_list = []
            for atome in organe.get("atomes", []):
                atomes_list.append({
                    "id": atome.get("id"),
                    "name": atome.get("name"),
                    "endpoint": atome.get("endpoint"),
                    "method": atome.get("method"),
                    "component_ref": atome.get("component_ref"),
                    "visual_hint": atome.get("visual_hint"),
                })
            organes_list.append({
                "id": organe.get("id"),
                "name": organe.get("name"),
                "atomes": atomes_list
            })
        corps_list.append({
            "id": corps.get("id"),
            "name": corps.get("name"),
            "organes": organes_list
        })
    return corps_list

# Lire le template
template_path = Path("/Users/francois-jeandazin/AETHERFLOW/Backend/Prod/templates/studio/ir_genome_view.html")
template = template_path.read_text(encoding="utf-8")

# Récupérer les données
ir_endpoints = parse_ir_visuel()
genome_corps = parse_genome_enrichi()

# Remplacer les variables dans le template
html = template.replace("{{ ir_count }}", str(len(ir_endpoints)))
html = html.replace("{{ corps_count }}", str(len(genome_corps)))

# Pour les boucles, on fait simple - on remplace par du HTML généré
ir_html = ""
for ep in ir_endpoints[:20]:  # Limiter à 20 pour la démo
    ir_html += f'''
    <div class="card">
        <span class="badge {ep['method']}">{ep['method']}</span>
        <span class="endpoint-path">{ep['path']}</span>
        <div class="meta">{ep['visual_hint']}</div>
        <div class="wireframe">{ep['wireframe']}</div>
        <div class="component">-> {ep['component_ref']}</div>
    </div>
    '''

# Remplacer la boucle IR
import re
template_ir_pattern = r'{% for ep in ir_endpoints %}[\s\S]*?{% endfor %}'
html = re.sub(template_ir_pattern, ir_html, html)

# Générer le HTML du genome
genome_html = ""
for corps in genome_corps:
    organes_html = ""
    for organe in corps['organes']:
        atomes_html = ""
        for atome in organe['atomes']:
            atomes_html += f'''
            <div class="sub-sub-item">A: {atome['name']}</div>
            <div class="sub-sub-info">{atome['method']} {atome['endpoint']} -> {atome['component_ref']}</div>
            '''
        organes_html += f'''
        <div class="sub-item">
            <div>O: {organe['name']}</div>
            {atomes_html}
        </div>
        '''
    genome_html += f'''
    <div class="tree-item">
        <div class="tree-header">
            <span>C: {corps['name']}</span>
            <span class="stat">{len(corps['organes'])} organes</span>
        </div>
        {organes_html}
    </div>
    '''

# Remplacer la boucle genome
template_genome_pattern = r'{% for corps in genome_corps %}[\s\S]*?{% endfor %}'
html = re.sub(template_genome_pattern, genome_html, html)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ["/", "/studio/step/4", "/studio/ir-genome-view"]:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        elif self.path == "/health":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, format, *args):
        pass  # Silencieux

print(f"🚀 Serveur minimal démarré sur http://localhost:8000")
print(f"   - {len(ir_endpoints)} endpoints")
print(f"   - {len(genome_corps)} corps")
print(f"   URL: http://localhost:8000/studio/step/4")
HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
