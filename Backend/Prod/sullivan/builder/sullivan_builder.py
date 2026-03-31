"""Sullivan Builder – Genome → studio_index.html (Brutalist, Fetch, single-file)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from loguru import logger

BRUTALIST_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
:root {
  --bg: #fff;
  --bg2: #f5f5f5;
  --text: #111;
  --text2: #444;
  --border: #ccc;
  --accent: #0066cc;
}
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 14px;
  line-height: 1.4;
  color: var(--text);
  background: var(--bg);
  min-height: 100vh;
  display: flex;
}
.sidebar {
  width: 200px;
  background: var(--bg2);
  border-right: 1px solid var(--border);
  padding: 1rem 0;
}
.sidebar h2 { font-size: 12px; text-transform: uppercase; padding: 0 1rem 0.5rem; color: var(--text2); }
.sidebar nav a {
  display: block;
  padding: 0.5rem 1rem;
  color: var(--text);
  text-decoration: none;
  border-left: 3px solid transparent;
}
.sidebar nav a:hover { background: var(--bg); border-left-color: var(--accent); }
.main {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
}
.main h1 { font-size: 1.25rem; margin-bottom: 1rem; }
.organe {
  background: var(--bg2);
  border: 1px solid var(--border);
  margin-bottom: 1rem;
  padding: 1rem;
}
.organe h3 { font-size: 13px; margin-bottom: 0.5rem; color: var(--text2); }
.organe pre, .organe .out { font-family: ui-monospace, monospace; font-size: 12px; white-space: pre-wrap; max-height: 200px; overflow-y: auto; }
.organe button, .organe input[type=submit] {
  font: inherit;
  padding: 0.4rem 0.8rem;
  background: var(--accent);
  color: #fff;
  border: none;
  cursor: pointer;
}
.organe button:hover { opacity: 0.9; }
.organe input, .organe textarea { font: inherit; padding: 0.4rem; border: 1px solid var(--border); width: 100%; max-width: 400px; }
.organe .err { color: #c00; }
.organe .ok { color: #080; }
"""


def _load_genome(source: Union[str, Path, Dict[str, Any]]) -> Dict[str, Any]:
    """Load genome from path or return dict as-is."""
    if isinstance(source, dict):
        return source
    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"Genome not found: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _organe_html(
    endpoint: Dict[str, Any],
    base_url: str,
    intent: str,
) -> str:
    """Render one organe (HTML fragment) from endpoint + x_ui_hint."""
    method = endpoint.get("method", "GET")
    path = endpoint.get("path", "")
    hint = endpoint.get("x_ui_hint", "generic")
    summary = endpoint.get("summary", path)
    lid = path.replace("/", "_").strip("_") or "root"
    bid = f"btn_{lid}"
    oid = f"out_{lid}"
    url = (base_url.rstrip("/") + path) if base_url else path

    if hint == "terminal":
        return f'''
<div class="organe" data-path="{path}" data-method="{method}" data-hint="terminal">
  <h3>{summary}</h3>
  <pre id="{oid}" class="out">—</pre>
  <button id="{bid}" type="button">Refresh</button>
</div>'''

    if hint == "gauge":
        return f'''
<div class="organe" data-path="{path}" data-method="{method}" data-hint="gauge">
  <h3>{summary}</h3>
  <div id="{oid}" class="out">—</div>
  <button id="{bid}" type="button">Refresh</button>
</div>'''

    if hint == "status":
        return f'''
<div class="organe" data-path="{path}" data-method="{method}" data-hint="status">
  <h3>{summary}</h3>
  <div id="{oid}" class="out">—</div>
  <button id="{bid}" type="button">Check</button>
</div>'''

    if hint == "form" and method.upper() == "POST":
        return f'''
<div class="organe" data-path="{path}" data-method="{method}" data-hint="form">
  <h3>{summary}</h3>
  <form id="form_{lid}"><button type="submit">Execute</button></form>
  <div id="{oid}" class="out"></div>
</div>'''

    if hint == "dashboard":
        return f'''
<div class="organe" data-path="{path}" data-method="{method}" data-hint="dashboard">
  <h3>{summary}</h3>
  <div id="{oid}" class="out">—</div>
  <button id="{bid}" type="button">Load</button>
</div>'''

    if hint == "detail":
        return f'''
<div class="organe" data-path="{path}" data-method="{method}" data-hint="detail">
  <h3>{summary}</h3>
  <div id="{oid}" class="out">—</div>
  <button id="{bid}" type="button">View</button>
</div>'''

    if hint == "list":
        return f'''
<div class="organe" data-path="{path}" data-method="{method}" data-hint="list">
  <h3>{summary}</h3>
  <div id="{oid}" class="out">—</div>
  <button id="{bid}" type="button">Load</button>
</div>'''

    return f'''
<div class="organe" data-path="{path}" data-method="{method}" data-hint="generic">
  <h3>{summary}</h3>
  <div id="{oid}" class="out">—</div>
  <button id="{bid}" type="button">Fetch</button>
</div>'''


def _fetch_js(base_url: str) -> str:
    """Inline JS: fetch buttons/forms → API, display in .out."""
    base = (base_url or "").rstrip("/")
    return f'''
<script>
(function() {{
  const BASE = {json.dumps(base)};
  function api(path, method, body) {{
    const url = BASE ? (BASE + (path.startsWith("/") ? path : "/" + path)) : path;
    const opt = {{ method: method || "GET", headers: {{ "Content-Type": "application/json" }} }};
    if (body && (method === "POST" || method === "PUT")) opt.body = JSON.stringify(body);
    return fetch(url, opt).then(r => r.json().catch(() => r.text()));
  }}
  function render(el, data) {{
    if (typeof data === "string") {{ el.textContent = data; return; }}
    el.textContent = JSON.stringify(data, null, 2);
  }}
  document.querySelectorAll(".organe").forEach(o => {{
    const path = o.dataset.path;
    const method = (o.dataset.method || "GET").toUpperCase();
    const out = o.querySelector(".out") || o.querySelector("[id^=out_]");
    if (!path || !out) return;
    const btn = o.querySelector("button[id^=btn_]") || o.querySelector("button:not([type=submit])");
    const form = o.querySelector("form");
    function run() {{
      out.classList.remove("err","ok");
      api(path, method).then(d => {{ out.classList.add("ok"); render(out, d); }})
        .catch(e => {{ out.classList.add("err"); out.textContent = "Error: " + e.message; }});
    }}
    if (btn) btn.addEventListener("click", run);
    if (form) form.addEventListener("submit", function(e) {{ e.preventDefault(); run(); }});
  }});
}})();
</script>'''


def build_html(
    genome: Union[str, Path, Dict[str, Any]],
    base_url: str = "http://localhost:8000",
) -> str:
    """
    Build single-file studio_index HTML from genome (dict or path).

    Layout: sidebar (topology) + main (organes per endpoint). Brutalist CSS, Fetch JS.
    """
    g = _load_genome(genome)
    metadata = g.get("metadata") or {}
    topology = g.get("topology") or ["Brainstorm", "Back", "Front", "Deploy"]
    endpoints = g.get("endpoints") or []
    intent = metadata.get("intent", "PaaS_Studio")

    nav = "".join(f'<a href="#{s}">{s}</a>' for s in topology)
    organes = "".join(_organe_html(ep, base_url, intent) for ep in endpoints)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Studio – {intent}</title>
  <style>{BRUTALIST_CSS}</style>
</head>
<body>
  <aside class="sidebar">
    <h2>Pipeline</h2>
    <nav>{nav}</nav>
  </aside>
  <main class="main">
    <h1>{intent}</h1>
    {organes}
  </main>
{_fetch_js(base_url)}
</body>
</html>"""
    return html


def build_from_genome(
    genome_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    base_url: str = "http://localhost:8000",
) -> Path:
    """
    Read genome from genome_path, write studio_index.html to output_path.

    If output_path is None, writes to same dir as genome, file studio_index.html.
    """
    genome_path = Path(genome_path)
    if output_path is None:
        output_path = genome_path.parent / "studio_index.html"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    html = build_html(genome_path, base_url=base_url)
    output_path.write_text(html, encoding="utf-8")
    logger.info(f"Builder wrote {output_path} from {genome_path}")
    return output_path


from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Dict
import logging
from importlib import import_module

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure templates
templates = Jinja2Templates(directory="templates")

def _path_to_ui_hint(path: str) -> Dict[str, str]:
    """
    Cette fonction renvoie un dictionnaire contenant des indices pour le type d'interface utilisateur 
    en fonction du chemin d'accès fourni.

    :param path: Le chemin d'accès
    :return: Un dictionnaire avec les indices pour le type d'interface utilisateur
    """
    ui_hint = {}

    # Patterns CRUD
    if path.endswith("/users") or path.endswith("/items"):
        # Liste ou tableau de bord
        ui_hint["type"] = "dashboard"
    elif path.endswith("/users/{id}") or path.endswith("/items/{id}"):
        # Détail
        ui_hint["type"] = "detail"

    # Patterns d'action
    elif path.endswith("/execute") or path.endswith("/run"):
        # Formulaire
        ui_hint["type"] = "form"

    # Patterns de requête
    elif path.endswith("/search") or path.endswith("/filter"):
        # Tableau de bord
        ui_hint["type"] = "dashboard"

    # Patterns de métriques
    elif path.endswith("/metrics") or path.endswith("/stats"):
        # Jauge
        ui_hint["type"] = "gauge"

    # Patterns de fichiers
    elif path.endswith("/upload") or path.endswith("/download"):
        # Formulaire
        ui_hint["type"] = "form"

    # Patterns d'authentification
    elif path.endswith("/login") or path.endswith("/logout"):
        # Formulaire
        ui_hint["type"] = "form"

    # Patterns de configuration
    elif path.endswith("/settings") or path.endswith("/config"):
        # Formulaire
        ui_hint["type"] = "form"

    # Heuristiques existantes
    elif path.endswith("/log"):
        # Terminal
        ui_hint["type"] = "terminal"
    elif path.endswith("/score"):
        # Jauge
        ui_hint["type"] = "gauge"
    elif path.endswith("/chart"):
        # Graphique
        ui_hint["type"] = "chart"
    elif path.endswith("/table"):
        # Tableau
        ui_hint["type"] = "table"

    return ui_hint

def _path_to_ui_hint_enriched(path: str, method: str, summary: str = '') -> Dict[str, str]:
    """
    Cette fonction combine les heuristiques avec IntentTranslator/STAR pour renvoyer un dictionnaire 
    contenant des indices pour le type d'interface utilisateur.

    :param path: Le chemin d'accès
    :param method: La méthode HTTP
    :param summary: Un résumé de la requête
    :return: Un dictionnaire avec les indices pour le type d'interface utilisateur
    """
    try:
        # Appeler d'abord _path_to_ui_hint() pour les heuristiques basiques
        ui_hint = _path_to_ui_hint(path)

        # Si le résultat est 'generic', utiliser IntentTranslator pour l'analyse sémantique
        if ui_hint.get("type") == "generic":
            # Importer IntentTranslator de manière paresseuse
            intent_translator = import_module('intent_translator')

            # Analyser la requête
            query = f"{path} {method} {summary}"
            parsed_query = intent_translator.parse_query(query)

            # Rechercher la situation
            situation = intent_translator.search_situation(parsed_query)

            # Propager les résultats STAR
            star_result = intent_translator.propagate_star(situation)

            # Mapper les patterns STAR vers x_ui_hint
            if star_result.get("pattern") == "Toggle Visibility":
                ui_hint["type"] = "form"
            elif star_result.get("pattern") == "Accordion":
                ui_hint["type"] = "dashboard"
            elif star_result.get("pattern") == "Modal":
                ui_hint["type"] = "form"
            elif star_result.get("pattern") == "Navigation":
                ui_hint["type"] = "dashboard"

        return ui_hint

    except ImportError as e:
        # Gérer les erreurs si IntentTranslator n'est pas disponible
        logger.error(f"Erreur lors de l'importation de IntentTranslator: {e}")
        return _path_to_ui_hint(path)

    except Exception as e:
        # Gérer les erreurs générales
        logger.error(f"Erreur lors de l'exécution de _path_to_ui_hint_enriched: {e}")
        return _path_to_ui_hint(path)

# Exemples d'utilisation
@app.get("/users")
def read_users(request: Request):
    """
    Cette fonction renvoie les utilisateurs et propose une interface utilisateur de type tableau de bord.
    """
    ui_hint = _path_to_ui_hint_enriched("/users", "GET")
    return templates.TemplateResponse("dashboard.html", {"request": request, "ui_hint": ui_hint})

@app.get("/users/{id}")
def read_user(request: Request, id: int):
    """
    Cette fonction renvoie un utilisateur et propose une interface utilisateur de type détail.
    """
    ui_hint = _path_to_ui_hint_enriched(f"/users/{id}", "GET")
    return templates.TemplateResponse("detail.html", {"request": request, "ui_hint": ui_hint})

@app.get("/execute")
def execute_action(request: Request):
    """
    Cette fonction exécute une action et propose une interface utilisateur de type formulaire.
    """
    ui_hint = _path_to_ui_hint_enriched("/execute", "GET")
    return templates.TemplateResponse("form.html", {"request": request, "ui_hint": ui_hint})

@app.get("/search")
def search_items(request: Request):
    """
    Cette fonction recherche des éléments et propose une interface utilisateur de type tableau de bord.
    """
    ui_hint = _path_to_ui_hint_enriched("/search", "GET")
    return templates.TemplateResponse("dashboard.html", {"request": request, "ui_hint": ui_hint})

@app.get("/metrics")
def read_metrics(request: Request):
    """
    Cette fonction renvoie des métriques et propose une interface utilisateur de type jauge.
    """
    ui_hint = _path_to_ui_hint_enriched("/metrics", "GET")
    return templates.TemplateResponse("gauge.html", {"request": request, "ui_hint": ui_hint})

@app.get("/upload")
def upload_file(request: Request):
    """
    Cette fonction télécharge un fichier et propose une interface utilisateur de type formulaire.
    """
    ui_hint = _path_to_ui_hint_enriched("/upload", "GET")
    return templates.TemplateResponse("form.html", {"request": request, "ui_hint": ui_hint})

@app.get("/login")
def login_user(request: Request):
    """
    Cette fonction connecte un utilisateur et propose une interface utilisateur de type formulaire.
    """
    ui_hint = _path_to_ui_hint_enriched("/login", "GET")
    return templates.TemplateResponse("form.html", {"request": request, "ui_hint": ui_hint})

@app.get("/settings")
def read_settings(request: Request):
    """
    Cette fonction renvoie les paramètres et propose une interface utilisateur de type formulaire.
    """
    ui_hint = _path_to_ui_hint_enriched("/settings", "GET")
    return templates.TemplateResponse("form.html", {"request": request, "ui_hint": ui_hint})

@app.get("/log")
def read_log(request: Request):
    """
    Cette fonction renvoie les journaux et propose une interface utilisateur de type terminal.
    """
    ui_hint = _path_to_ui_hint_enriched("/log", "GET")
    return templates.TemplateResponse("terminal.html", {"request": request, "ui_hint": ui_hint})

@app.get("/score")
def read_score(request: Request):
    """
    Cette fonction renvoie les scores et propose une interface utilisateur de type jauge.
    """
    ui_hint = _path_to_ui_hint_enriched("/score", "GET")
    return templates.TemplateResponse("gauge.html", {"request": request, "ui_hint": ui_hint})

@app.get("/chart")
def read_chart(request: Request):
    """
    Cette fonction renvoie les graphiques et propose une interface utilisateur de type graphique.
    """
    ui_hint = _path_to_ui_hint_enriched("/chart", "GET")
    return templates.TemplateResponse("chart.html", {"request": request, "ui_hint": ui_hint})

@app.get("/table")
def read_table(request: Request):
    """
    Cette fonction renvoie les tableaux et propose une interface utilisateur de type tableau.
    """
    ui_hint = _path_to_ui_hint_enriched("/table", "GET")
    return templates.TemplateResponse("table.html", {"request": request, "ui_hint": ui_hint})

# Nouveaux hints ajoutés
@app.get("/list")
def read_list(request: Request):
    """
    Cette fonction renvoie une liste et propose une interface utilisateur de type liste.
    """
    ui_hint = _path_to_ui_hint_enriched("/list", "GET")

from typing import List
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

class Component(BaseModel):
    id: str
    html: str
    css: str
    js: str

def generate_preview_html(component: Component, base_url: str) -> str:
    """
    Generate HTML for previewing a component with iframe.
    """
    html = f"""
    <html>
    <head>
        <title>Component Preview</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
            }}
            iframe {{
                width: 100%;
                height: 500px;
                border: none;
            }}
        </style>
    </head>
    <body>
        <h1>Component Preview</h1>
        <iframe src="{base_url}/preview/{component.id}" frameborder="0"></iframe>
    </body>
    </html>
    """
    return html

def generate_preview_page(components: List[Component], base_url: str) -> str:
    """
    Generate HTML for listing multiple components.
    """
    html = f"""
    <html>
    <head>
        <title>Components List</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
            }}
            ul {{
                list-style: none;
                padding: 0;
                margin: 0;
            }}
            li {{
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <h1>Components List</h1>
        <ul>
            {"".join(f"<li><a href='{base_url}/preview/{component.id}'>{component.id}</a></li>" for component in components)}
        </ul>
    </body>
    </html>
    """
    return html

# Template HTML with brutalist style
template_html = """
<html>
<head>
    <title>Brutalist Template</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f0f0f0;
        }
        .container {
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            background-color: #fff;
            border: 1px solid #ddd;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>
"""

# Support for displaying HTML/CSS/JS of a component in a secure iframe
@app.get("/preview/{component_id}")
async def preview_component(component_id: str):
    # Fetch the component from the database or a storage system
    component = Component(id=component_id, html="<p>Hello World!</p>", css="", js="")
    
    # Generate the HTML for the preview
    html = f"""
    <html>
    <head>
        <style>
            {component.css}
        </style>
    </head>
    <body>
        {component.html}
        <script>
            {component.js}
        </script>
    </body>
    </html>
    """
    
    # Return the HTML as a response
    return HTMLResponse(content=html, status_code=200)

# Create a simple HTTP server using FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class ScreenPlanner:
    def __init__(self):
        pass

    def plan_from_genome(self, genome: Dict) -> List[Dict]:
        """
        Create a plan from a genome dictionary.

        Args:
        - genome (Dict): A dictionary containing topology and endpoints.

        Returns:
        - plan (List[Dict]): A list of body dictionaries with corps_id, label, organes, and endpoints.
        """
        topology = genome["topology"]
        endpoints = genome["endpoints"]

        # Group endpoints by first segment of path or x_ui_hint
        endpoint_groups = {}
        for endpoint in endpoints:
            path = endpoint["path"]
            first_segment = path.split("/")[1]
            x_ui_hint = endpoint.get("x_ui_hint")
            if x_ui_hint:
                key = x_ui_hint
            else:
                key = first_segment
            if key not in endpoint_groups:
                endpoint_groups[key] = []
            endpoint_groups[key].append(endpoint)

        # Distribute endpoints across bodies
        bodies = []
        for i, topology_element in enumerate(topology):
            body = {
                "corps_id": str(i + 1),
                "label": topology_element,
                "organes": [],
                "endpoints": []
            }
            for key, group in endpoint_groups.items():
                if i < len(group):
                    endpoint = group[i]
                    body["organes"].append({
                        "endpoint_path": endpoint["path"],
                        "method": endpoint["method"],
                        "x_ui_hint": endpoint.get("x_ui_hint")
                    })
                    body["endpoints"].append(endpoint)
            bodies.append(body)

        return bodies

    def save_plan(self, plan: List[Dict], output_path: Path):
        """
        Save a plan to a JSON file.

        Args:
        - plan (List[Dict]): A list of body dictionaries.
        - output_path (Path): The path to the output JSON file.
        """
        with open(output_path, "w") as f:
            json.dump(plan, f, indent=4)

def load_genome(path: Path) -> Dict:
    """
    Load a genome from a JSON file.

    Args:
    - path (Path): The path to the genome JSON file.

    Returns:
    - genome (Dict): A dictionary containing topology and endpoints.
    """
    with open(path, "r") as f:
        return json.load(f)

def plan_screens(genome_path: Path, output_path: Optional[Path] = None) -> List[Dict]:
    """
    Plan screens from a genome file.

    Args:
    - genome_path (Path): The path to the genome JSON file.
    - output_path (Optional[Path]): The path to the output JSON file. Defaults to output/studio/screen_plan.json.

    Returns:
    - plan (List[Dict]): A list of body dictionaries.
    """
    genome = load_genome(genome_path)
    planner = ScreenPlanner()
    plan = planner.plan_from_genome(genome)
    if output_path is None:
        output_path = Path("output/studio/screen_plan.json")
    planner.save_plan(plan, output_path)
    return plan

if __name__ == "__main__":
    genome_path = Path("path/to/genome.json")
    output_path = Path("output/studio/screen_plan.json")
    plan = plan_screens(genome_path, output_path)
    logger.info("Plan generated successfully!")

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional

# Define the logger
logger = logging.getLogger(__name__)

# Define the brutalist CSS style
BRUTALIST_CSS = """
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
}

section {
    border: 1px solid #ccc;
    margin: 20px;
    padding: 20px;
}

h1 {
    font-size: 24px;
    margin: 0;
    padding: 0;
}

.header, .main, .footer {
    border: 1px solid #ccc;
    padding: 20px;
}

.placeholder {
    border: 1px solid #ccc;
    padding: 20px;
}
"""

def load_screen_plan(path: Path) -> List[Dict]:
    """
    Load the screen plan from a JSON file.

    Args:
        path: The path to the JSON file.

    Returns:
        A list of dictionaries representing the screen plan.
    """
    try:
        with open(path, 'r') as f:
            screen_plan = json.load(f)
            return screen_plan
    except json.JSONDecodeError as e:
        logger.error(f"Failed to load screen plan: {e}")
        return []

def load_design_principles(path: Optional[Path]) -> Dict:
    """
    Load the design principles from a JSON file.

    Args:
        path: The path to the JSON file.

    Returns:
        A dictionary representing the design principles.
    """
    if path is None:
        return {}
    try:
        with open(path, 'r') as f:
            design_principles = json.load(f)
            return design_principles
    except json.JSONDecodeError as e:
        logger.error(f"Failed to load design principles: {e}")
        return {}

def generate_corps_html(screen_plan: List[Dict], design_principles: Dict, base_url: str) -> str:
    """
    Generate the HTML for the corps.

    Args:
        screen_plan: The list of dictionaries representing the screen plan.
        design_principles: The dictionary representing the design principles.
        base_url: The base URL for the endpoints.

    Returns:
        The HTML for the corps.
    """
    html = ""
    for corps in screen_plan:
        corps_id = corps['corps_id']
        label = corps['label']
        organes = corps['organes']
        html += f"<section id='corps_{corps_id}'>"
        html += f"<h1>{label}</h1>"
        html += "<div class='header'>Header</div>"
        html += "<div class='main'>"
        for organe in organes:
            endpoint_path = organe['endpoint_path']
            method = organe['method']
            x_ui_hint = organe['x_ui_hint']
            html += f"<div class='placeholder' data-endpoint-path='{endpoint_path}' data-method='{method}' data-x-ui-hint='{x_ui_hint}'>Placeholder</div>"
        html += "</div>"
        html += "<div class='footer'>Footer</div>"
        html += "</section>"
    # Apply design principles
    if design_principles:
        colors = design_principles.get('colors', {})
        font_family = design_principles.get('font_family', '')
        html += f"<style>body {{ font-family: {font_family}; }}</style>"
        html += f"<style>.header {{ background-color: {colors.get('header', '#ccc')}; }}</style>"
        html += f"<style>.main {{ background-color: {colors.get('main', '#fff')}; }}</style>"
        html += f"<style>.footer {{ background-color: {colors.get('footer', '#ccc')}; }}</style>"
    return html

def build_corps(screen_plan_path: Path, output_path: Path, design_principles_path: Optional[Path], base_url: str) -> None:
    """
    Build the corps HTML.

    Args:
        screen_plan_path: The path to the screen plan JSON file.
        output_path: The path to the output HTML file.
        design_principles_path: The path to the design principles JSON file.
        base_url: The base URL for the endpoints.
    """
    screen_plan = load_screen_plan(screen_plan_path)
    design_principles = load_design_principles(design_principles_path)
    html = generate_corps_html(screen_plan, design_principles, base_url)
    with open(output_path, 'w') as f:
        f.write(html)
    logger.info(f"Corps HTML built successfully: {output_path}")

if __name__ == '__main__':
    screen_plan_path = Path("screen_plan.json")
    output_path = Path("corps.html")
    design_principles_path = Path("design_principles.json")
    base_url = "https://example.com"
    build_corps(screen_plan_path, output_path, design_principles_path, base_url)