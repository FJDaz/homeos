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
import csv
import uuid
import sqlite3
import asyncio
import threading
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import urllib.request
import urllib.error
import zipfile
import time

# Ajout des chemins pour importer les modules Backend et Frontend
cwd = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(cwd, "../.."))
backend_prod = os.path.abspath(os.path.join(cwd, "../../Backend/Prod"))
backend_archive = os.path.abspath(os.path.join(cwd, "../../Backend/_archive"))

for p in [root_dir, backend_prod, backend_archive]:
    if p not in sys.path:
        sys.path.insert(0, p)

from Backend.Prod.retro_genome.manifest_validator import validate_html, format_system_prompt_constraint

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

# Mission 83 — Sullivan Arbitrator
from sullivan_arbitrator import SullivanArbitrator, SullivanPulse

_ARBITRATOR = SullivanArbitrator()
_PULSE = SullivanPulse()
_PULSE.start()

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


def _load_manifest_frd():
    """Charge le MANIFEST_FRD pour contextualiser Sullivan sur le projet."""
    path = os.path.join(root_dir, "docs/02_Sullivan/Retro_Genome/MANIFEST_FRD.md")
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return ""
    return ""

_MANIFEST_FRD = _load_manifest_frd()

# --- Mission 81 : Sullivan BKD system_instruction ---
_SULLIVAN_BKD_SYSTEM = (
    "Tu es Sullivan BKD, architecte backend et DevOps du projet AetherFlow.\n"
    "Tu assistes le développeur dans la gestion du code backend Python, des API REST, des workflows AetherFlow, et du déploiement.\n\n"
    "CONTEXTE TECHNIQUE :\n"
    "- Stack : Python 3.11+, Flask/http.server, LlamaIndex, SQLite, Docker\n"
    "- Agents : Gemini (frontend), Groq (routing), Codestral (code gen), MiMo (wire/diag)\n"
    "- Pipeline AetherFlow : BRS → BKD → FRD → DPL\n"
    "- Éditeur : surgical_editor.py (AST Python), surgical_editor_js.py (acorn Range-Based)\n\n"
    "RÈGLES :\n"
    "1. Tu génères des patches précis (pas de rewrites complets si patch suffisant)\n"
    "2. Tu cites toujours le fichier + la fonction à modifier\n"
    "3. Pour les modifications multi-fichiers, tu listes les fichiers dans l'ordre d'application\n"
    "4. Tu n'inventes pas d'API — tu utilises uniquement les routes documentées\n"
    "5. Tu utilises query_knowledge_base() pour toute question sur l'archi AetherFlow\n\n"
    "FORMAT réponse code : ```python\n# fichier: <path>\n# fonction: <name>\n<code>\n```\n\n"
    "Tu ne génères JAMAIS de HTML/CSS/Tailwind. Si la tâche est frontend, tu le signales."
)

# --- Mission 77 : Sullivan Knowledge Base (RAG) ---
_SULLIVAN_DOCS = [
    '/Users/francois-jeandazin/AETHERFLOW/docs/02_Sullivan',
    '/Users/francois-jeandazin/AETHERFLOW/docs/02-sullivan',
    '/Users/francois-jeandazin/AETHERFLOW/docs/04_HomeOS',
    '/Users/francois-jeandazin/AETHERFLOW/docs/04-homeos',
    '/Users/francois-jeandazin/AETHERFLOW/docs/03_AetherFlow',
    '/Users/francois-jeandazin/AETHERFLOW/Frontend/4. COMMUNICATION/ROADMAP.md',
    '/Users/francois-jeandazin/AETHERFLOW/Frontend/4. COMMUNICATION/ROADMAP_ACHIEVED.md',
]

def _init_sullivan_rag():
    try:
        # Nettoyer temporairement sys.path pour éviter conflit import relatif llama_index
        _saved = sys.path.copy()
        sys.path = [p for p in sys.path if not p.endswith('Backend/Prod') and not p.endswith('Backend/_archive')]
        try:
            from Backend.Prod.rag.pageindex_store import PageIndexRetriever
        finally:
            sys.path = _saved
        docs = []
        for p in _SULLIVAN_DOCS:
            pp = Path(p)
            if pp.is_dir():
                docs += list(pp.rglob('*.md'))
            elif pp.exists():
                docs.append(pp)
        rag = PageIndexRetriever(document_paths=[str(d) for d in docs])
        if not getattr(rag, 'enabled', True):
            print('[RAG] LlamaIndex non disponible — RAG désactivé')
            return None
        print(f'[RAG] Index Sullivan : {len(docs)} documents ✅')
        return rag
    except Exception as e:
        print(f'[RAG] Désactivé : {e}')
        return None

_SULLIVAN_RAG = _init_sullivan_rag()

# --- Mission 79 : User DB BKD (project_id → project_path) ---
_BKD_DB_PATH = Path('/Users/francois-jeandazin/AETHERFLOW/db/projects.db')

def _init_bkd_db():
    _BKD_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(_BKD_DB_PATH))
    con.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            path TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            last_opened TEXT DEFAULT (datetime('now'))
        )
    """)
    con.commit()
    con.close()

_init_bkd_db()


def _bkd_db_con():
    """Retourne une connexion SQLite thread-safe (check_same_thread=False)."""
    return sqlite3.connect(str(_BKD_DB_PATH), check_same_thread=False)

_BKD_ALLOWED_EXTENSIONS = {'.py', '.js', '.ts', '.html', '.css', '.md', '.json', '.txt', '.yaml', '.yml', '.toml', '.sh', '.env.example'}
_BKD_EXCLUDE_DIRS = {'__pycache__', '.git', 'node_modules', '.venv', 'venv', 'dist', 'build', '.mypy_cache'}


def _resolve_bkd_project_root(project_id):
    """Résout le chemin racine d'un projet depuis la DB. Retourne Path ou None."""
    con = _bkd_db_con()
    row = con.execute('SELECT path FROM projects WHERE id=?', (project_id,)).fetchone()
    con.close()
    if not row:
        return None
    return Path(row[0])


def _bkd_safe_path(project_root, rel_path):
    """Vérifie que rel_path est bien sous project_root (anti path-traversal). Retourne Path ou None."""
    resolved = (project_root / rel_path).resolve()
    try:
        resolved.relative_to(project_root.resolve())
    except ValueError:
        return None
    if resolved.suffix not in _BKD_ALLOWED_EXTENSIONS:
        return None
    return resolved


def _bkd_build_tree(root, rel='', depth=2, current=0):
    """Construit récursivement l'arbre fichiers d'un projet."""
    result = []
    try:
        for entry in sorted(Path(root).iterdir(), key=lambda e: (e.is_file(), e.name)):
            if entry.name.startswith('.') and entry.name not in ('.env.example',):
                continue
            if entry.name in _BKD_EXCLUDE_DIRS:
                continue
            rel_entry = f"{rel}/{entry.name}" if rel else entry.name
            if entry.is_dir():
                node = {'name': entry.name, 'path': rel_entry, 'type': 'dir', 'children': []}
                if current < depth:
                    node['children'] = _bkd_build_tree(entry, rel_entry, depth, current + 1)
                result.append(node)
            elif entry.is_file() and entry.suffix in _BKD_ALLOWED_EXTENSIONS:
                result.append({'name': entry.name, 'path': rel_entry, 'type': 'file',
                                'size': entry.stat().st_size})
    except PermissionError:
        pass
    return result

REFERENCE_WHITELIST = {
    'manifest_frd': os.path.join(root_dir, "docs/02_Sullivan/Retro_Genome/MANIFEST_FRD.md"),
    'sullivan_interactions': os.path.join(root_dir, "Frontend/1. CONSTITUTION/SULLIVAN_INTERACTIONS.md"),
    'api_contract': os.path.join(root_dir, "Frontend/1. CONSTITUTION/API_CONTRACT.md"),
    'constitution': os.path.join(root_dir, "Frontend/1. CONSTITUTION/CONSTITUTION_AETHERFLOW_V3.md"),
    'lexicon_design': os.path.join(root_dir, "Frontend/1. CONSTITUTION/LEXICON_DESIGN.json"),
}

def _exec_read_reference(path_or_key):
    if path_or_key in REFERENCE_WHITELIST:
        abs_path = REFERENCE_WHITELIST[path_or_key]
    else:
        abs_path = os.path.join(root_dir, path_or_key)
    abs_path = os.path.abspath(abs_path)
    if not abs_path.startswith(root_dir):
        return f"Accès refusé pour '{path_or_key}' (hors racine du projet)."
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            return f.read(8000)
    except FileNotFoundError:
        return f"Fichier introuvable : '{path_or_key}'."
    except Exception as e:
        return f"Erreur lecture '{path_or_key}': {str(e)}"


def _exec_query_knowledge_base(query):
    if _SULLIVAN_RAG is None:
        return 'RAG non disponible.'
    try:
        import asyncio
        nodes = asyncio.run(_SULLIVAN_RAG.retrieve(query))
        if not nodes:
            return 'Aucun résultat trouvé dans la base de connaissance.'
        chunks = []
        for n in nodes[:4]:
            src = n.get('file_name', '?') if isinstance(n, dict) else getattr(getattr(n, 'node', n), 'metadata', {}).get('file_name', '?')
            content = n.get('content', '') if isinstance(n, dict) else n.node.get_content()
            chunks.append(f'[{src}]\n{content[:600]}')
        return '\n\n---\n\n'.join(chunks)
    except Exception as e:
        return f'Erreur RAG : {e}'


def _load_api_contract():
    """Charge le contrat d'API pour l'injecter dans les prompts Sullivan."""
    contract_path = os.path.join(root_dir, "Frontend/1. CONSTITUTION/API_CONTRACT.md")
    if os.path.exists(contract_path):
        try:
            with open(contract_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return "Contrat d'API non disponible."
    return "Contrat d'API non trouvé."


def _build_conseil_prompt(message, html_context):
    """
    Construit le prompt pour le mode CONSEIL (Audit UI/UX).
    Utilise ui-reasoning.csv pour enrichir l'intelligence de Sullivan.
    """
    csv_path = os.path.join(root_dir, ".agent/skills/ui-ux-pro-max/data/ui-reasoning.csv")
    reasoning_context = ""
    if os.path.exists(csv_path):
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                # On prend les 10 premières catégories pour ne pas exploser le contexte
                rows = list(reader)[:10]
                reasoning_context = "\nDESIGN PATTERNS REFERENCE :\n"
                for row in rows:
                    reasoning_context += f"- {row['UI_Category']}: {row['Recommended_Pattern']} | {row['Style_Priority']} | Colors: {row['Color_Mood']}\n"
        except Exception as e:
            print(f"Error reading csv: {e}")

    prompt = (
        "Tu es Sullivan, expert UI/UX de HomeOS. Ton rôle est d'AUDITER le code HTML/Tailwind fourni.\n"
        "Tu ne proposes PAS de code HTML dans ce mode. Tu ne réponds qu'avec du texte markdown.\n\n"
        "TON OBJECTIF :\n"
        "1. Analyser techniquement et visuellement le HTML actuel.\n"
        "2. Fournir un audit structuré avec les symboles suivants :\n"
        "   🔴 [Point critique bloquant ou erreur majeure]\n"
        "   🟡 [Amélioration recommandée ou warning UX]\n"
        "   🟢 [Point fort ou validation]\n\n"
        "FORMAT DE RÉPONSE :\n"
        "Commence par un titre '# Audit UX - [Nom du composant]'\n"
        "Puis liste tes points 🔴/🟡/🟢.\n"
        "Termine par un 'Score Global : X/10'.\n\n"
        "CONTRAINTES :\n"
        "• Sois sec et professionnel.\n"
        "• Utilise les patterns ci-dessous si pertinent :\n"
        f"{reasoning_context}\n\n"
        "ROUTES API DISPONIBLES (Ne jamais suggérer d'autres routes) :\n"
        f"{_load_api_contract()}\n\n"
        f"MESSAGE UTILISATEUR : {message}\n"
        f"HTML À AUDITER :\n{html_context}"
    )
    return prompt


def _build_wire_prompt(html_context):
    """
    Construit le prompt pour le mode WIRE (Diagnostic statique).
    Cible : Codestral (analyse de code).
    """
    return (
        "Tu es Sullivan (IA HomeOS), expert en diagnostic de code HTML/JS.\n"
        "Analyse le code source fourni pour identifier les problèmes de câblage.\n\n"
        "OBJECTIF : Détecter :\n"
        "1. **Sélecteurs orphelins** : Utilisation de getElementById() ou querySelector() pointant vers des IDs/classes absents du DOM.\n"
        "2. **Bindings manquants** : Appels addEventListener() ou attributs onclick vers des fonctions non définies.\n"
        "3. **Endpoints non déclarés** : Appels fetch() vers des URLs qui ne ressemblent pas à des routes valides (/api/...) ou non documentées.\n\n"
        "FORMAT DE RÉPONSE (Markdown) :\n"
        "# 🕸️ Diagnostic WIRE\n\n"
        "## 🔍 Sélecteurs Orphelins\n"
        "- [Liste ou 'Aucun']\n\n"
        "## 🔗 Bindings / Fonctions\n"
        "- [Liste ou 'Aucun']\n\n"
        "## 🔌 API Endpoints\n"
        "- [Liste ou 'Aucun']\n\n"
        "SOIS FACTUEL ET CONCIS. PAS DE PROSE INUTILE."
        f"\n\nCODE SOURCE À ANALYSER :\n{html_context}"
    )


def _route_request(message, html, js_controller, file_name, history=None):
    """
    Appelle Groq (Llama 3.3 70B) pour router la requête et générer spec/patch.
    Mission 64 - Mode Engineer Transparent.
    Mission 74 - History context pour détecter "procède" après un plan.
    """
    _load_env()
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return {"type": "html-only", "html_spec": message, "js_patch": None, "new_ids": []}

    url = "https://api.groq.com/openai/v1/chat/completions"

    # Load manifest for context
    from Backend.Prod.retro_genome.manifest_validator import load_manifest
    manifest = load_manifest(file_name) if file_name else {}
    manifest_str = json.dumps(manifest, indent=2, ensure_ascii=False) if manifest else "Aucun manifeste."

    # M74 : dernier tour Sullivan pour détecter "procède" après un plan
    last_model_turn = ""
    if history:
        last_model_turn = next((t.get('text', '') for t in reversed(history) if t.get('role') == 'model'), '')

    system = (
        "Tu es Tech Lead frontend. Tu analyses une requête utilisateur et décides de la route.\n"
        "Réponds UNIQUEMENT avec un JSON valide, sans markdown, sans explication :\n"
        '{"type":"text-only"|"html-only"|"js-only"|"both", "response":"...ou null", "html_spec":"...ou null", "js_patch":"...ou null", "new_ids":[]}\n\n'
        "ROUTING RULES — dans cet ordre de priorité :\n"
        '• "both" ou "html-only" : si le message est une confirmation d\'exécution courte '
        '("go", "procède", "génère", "fais-le", "proceed", "ok vas-y", "lance", "implémente") '
        'ET que le DERNIER TOUR SULLIVAN ci-dessous contient un plan technique ou du code → '
        'router vers "both" si le plan mentionne JS+HTML, sinon "html-only". '
        'Mettre la spec du plan dans "html_spec".\n'
        '• "text-only" : question, analyse, rapport, explication, lecture de document, conversation, "établis un plan". '
        'PAS de modification de code. Répondre dans "response" (texte markdown).\n'
        '• "html-only" : modification visuelle HTML/CSS/Tailwind uniquement.\n'
        '• "js-only" : modification logique JS uniquement, zéro changement HTML.\n\n'
        "RÈGLE : html_spec = spec précise pour l'exécuteur HTML. js_patch = code JS complet.\n"
        "RÈGLE : ne jamais modifier les IDs existants du manifeste.\n\n"
        f"MANIFESTE (IDs protégés) :\n{manifest_str}\n\n"
        f"CONTRÔLEUR JS ACTUEL (contexte) :\n{js_controller[:2000]}\n\n"
        f"DERNIER TOUR SULLIVAN :\n{last_model_turn[:1500]}"
    )

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Requête : {message}\n\nHTML actuel :\n{html[:1500]}"}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }

    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
            'User-Agent': 'AetherFlow-Agent/1.0'
        })
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            raw_content = res_data['choices'][0]['message']['content']
            return json.loads(raw_content)
    except Exception as e:
        print(f"[GROQ_ROUTER_ERROR] {e}")
        return {"type": "html-only", "html_spec": message, "js_patch": None, "new_ids": []}


# --- Mission 78 : Sullivan BKD Router ---


def _route_request_bkd(message, history=None):
    """Route BKD : Groq classifie en quick/code-simple/code-complex/wire/diagnostic."""
    _load_env()
    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
        return {'type': 'quick', 'model': 'gemini-2.5-flash'}

    last_model_turn = ''
    if history:
        last_model_turn = next((t.get('text', '') for t in reversed(history) if t.get('role') == 'model'), '')

    system = (
        'Tu es un routeur pour Sullivan BKD (assistant backend/devops AetherFlow).\n'
        'Réponds UNIQUEMENT avec un JSON : {"type": "...", "reason": "..."}\n\n'
        'Types disponibles :\n'
        '- quick         : question courte, explication archi, doc lookup, conversation\n'
        '- code-simple   : génération ou patch < 100 lignes, fichier unique\n'
        '- code-complex  : multi-fichiers, nouvelle feature, refactoring > 100L\n'
        '- wire          : analyse statique codebase, routes API, diagnostic dépendances\n'
        '- diagnostic    : débogage, stacktrace, investigation erreur\n\n'
        'RÈGLE : si le message est une confirmation d\'exécution ("go", "procède", "lance") '
        'ET que le dernier tour contient un plan technique → même type que le plan.\n\n'
        f'DERNIER TOUR SULLIVAN :\n{last_model_turn[:800]}'
    )

    url = 'https://api.groq.com/openai/v1/chat/completions'
    payload = {
        'model': 'llama-3.3-70b-versatile',
        'messages': [
            {'role': 'system', 'content': system},
            {'role': 'user', 'content': f'Message BKD : {message}'}
        ],
        'temperature': 0.1,
        'response_format': {'type': 'json_object'}
    }
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
            'User-Agent': 'AetherFlow-Agent/1.0'
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            route_type = json.loads(data['choices'][0]['message']['content']).get('type', 'quick')
            
            # Utilisation de l'arbitre dynamique pour choisir le modèle
            config = _ARBITRATOR.pick(route_type)
            model = config['model']
            provider = config['provider']
            
            print(f'[BKD] Route: {route_type} → {provider} ({model})')
            # On retourne aussi le provider pour que le dispatcher sache quel client utiliser
            return {'type': route_type, 'model': model, 'provider': provider}
    except Exception as e:
        print(f'[BKD_ROUTER_ERROR] {e}')
        # Fallback sécurisé par défaut
        return {'type': 'quick', 'model': 'gemini-2.5-flash', 'provider': 'gemini'}


def _update_manifest(file_name, new_ids):
    """Met à jour le manifeste DOM avec de nouveaux IDs (Mission 64)."""
    if not file_name or not new_ids:
        return

    from Backend.Prod.retro_genome.manifest_validator import get_manifest_path, load_manifest
    path = get_manifest_path(file_name)
    manifest = load_manifest(file_name)
    
    if not manifest:
        return

    updated = False
    existing_ids = {el['selector'].lstrip('#') for el in manifest.get('required_elements', [])}
    
    for nid in new_ids:
        clean_id = nid.lstrip('#')
        if clean_id not in existing_ids:
            manifest.get('required_elements', []).append({
                "selector": f"#{clean_id}",
                "description": f"Ajouté dynamiquement par Groq Engineer — {datetime.now().strftime('%Y-%m-%d')}"
            })
            existing_ids.add(clean_id)
            updated = True
            
    if updated:
        manifest['last_updated'] = datetime.now().strftime('%Y-%m-%d')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        print(f"[MANIFEST_UPDATE] {len(new_ids)} nouveaux IDs ajoutés à {path.name}")


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


def infer_layout_llm(organs, project_context="", model_name="gemini-2.5-flash"):
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
        api_key = os.environ.get('OPENROUTER_API_KEY')
        if not api_key or api_key == "votre_cle_ici":
            with _kimi_jobs_lock:
                _kimi_jobs[job_id] = { "status": "error", "error": "OPENROUTER_API_KEY non configurée", "ts": datetime.now() }
            return

        url = "https://openrouter.ai/api/v1/chat/completions"

        prompt = (
            "Tu es KIMI, expert en design UI/UX. Propose UNE refonte visuelle de l'interface HTML/Tailwind fournie.\n"
            "Réponds avec un label court (3-5 mots) puis le HTML complet modifié.\n"
            "Format strict :\nLABEL: [label]\n---HTML---\n[HTML complet]\n\n"
            f"Instruction : {instruction}\n"
            f"HTML actuel (scripts omis) :\n{html_stripped}"
        )

        payload = {
            "model": "google/gemma-2-9b-it:free",  # Modèle gratuit performant
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 8192,
            "temperature": 0.7
        }

        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'),
                                     headers={
                                         'Content-Type': 'application/json',
                                         'Authorization': f'Bearer {api_key}',
                                         'HTTP-Referer': 'https://aetherflow.ai', # Requis par OpenRouter
                                         'X-Title': 'AetherFlow'                 # Requis par OpenRouter
                                     })

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

        # Mission 83 — Sullivan Pulse (Reactivity Monitoring)
        if self.path == '/api/sullivan/pulse':
            self.send_json(_PULSE.get_status())
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

        # Route GET /api/frd/manifest/{name} (Mission 63)
        if self.path.startswith('/api/frd/manifest/'):
            try:
                parts = self.path.split('/')
                # /api/frd/manifest/NAME ou /api/frd/manifest/NAME/prompt
                name = parts[4]
                is_prompt = len(parts) > 5 and parts[5] == 'prompt'
                
                from Backend.Prod.retro_genome.manifest_validator import load_manifest, format_system_prompt_constraint
                
                if is_prompt:
                    prompt = format_system_prompt_constraint(name)
                    if not prompt:
                        self.send_error_json(404, f"Aucun manifeste pour '{name}'.")
                        return
                    self.send_json({"constraint_prompt": prompt})
                else:
                    manifest = load_manifest(name)
                    if manifest is None:
                        self.send_error_json(404, f"Aucun manifeste pour '{name}'.")
                        return
                    self.send_json(manifest)
                return
            except Exception as e:
                self.send_error_json(500, str(e))
                return

        # Route GET /api/frd/files — liste tous les templates HTML
        if self.path == '/api/frd/files':
            try:
                cwd = os.path.dirname(os.path.abspath(__file__))
                tdir = os.path.join(cwd, TEMPLATES_DIR)
                files = sorted([f for f in os.listdir(tdir) if f.endswith('.html')])
                self.send_json({"files": files})
            except Exception as e:
                self.send_error_json(500, str(e))
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

        if self.path.startswith('/api/brs/search'):
            from urllib.parse import urlparse, parse_qs
            q = parse_qs(urlparse(self.path).query).get('q', [''])[0]
            results = brs_logic.storage.search(q) if q else []
            self.send_json({"status": "ok", "query": q, "results": results})
            return

        # Mission 58 — BRS Arbitrate SSE (Sullivan synthesis)
        if self.path.startswith('/api/brs/arbitrate/'):
            session_id = self.path.split('/')[-1]
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.end_headers()
            loop = asyncio.new_event_loop()
            try:
                async def run_arb():
                    async for chunk in brs_logic.arbitrate_session(session_id):
                        self.wfile.write(chunk.encode('utf-8'))
                        self.wfile.flush()
                loop.run_until_complete(run_arb())
            except Exception as e:
                print(f"[BRS_ARB] SSE Error: {e}", flush=True)
            finally:
                loop.close()
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

        # --- Mission 79 : BKD Projects DB (GET) ---
        if self.path == '/api/bkd/projects':
            try:
                con = _bkd_db_con()
                rows = con.execute('SELECT id, name, path, created_at, last_opened FROM projects ORDER BY last_opened DESC').fetchall()
                con.close()
                projects = [{'id': r[0], 'name': r[1], 'path': r[2], 'created_at': r[3], 'last_opened': r[4]} for r in rows]
                self.send_json({'projects': projects})
            except Exception as e:
                self.send_error_json(500, str(e))
            return

        if self.path.startswith('/api/bkd/projects/'):
            try:
                project_id = self.path.split('/')[-1]
                con = _bkd_db_con()
                row = con.execute('SELECT id, name, path, created_at, last_opened FROM projects WHERE id=?', (project_id,)).fetchone()
                con.close()
                if not row:
                    self.send_error_json(404, f'Project {project_id} not found')
                    return
                self.send_json({'id': row[0], 'name': row[1], 'path': row[2], 'created_at': row[3], 'last_opened': row[4]})
            except Exception as e:
                self.send_error_json(500, str(e))
            return

        # --- Mission 80 : BKD File API (GET) ---
        if self.path.startswith('/api/bkd/file'):
            try:
                from urllib.parse import urlparse, parse_qs
                qs = parse_qs(urlparse(self.path).query)
                project_id = qs.get('project_id', [None])[0]
                rel_path = qs.get('path', [None])[0]
                if not project_id or not rel_path:
                    self.send_error_json(400, 'project_id and path required')
                    return
                root = _resolve_bkd_project_root(project_id)
                if root is None:
                    self.send_error_json(404, f'Project {project_id} not found')
                    return
                safe = _bkd_safe_path(root, rel_path)
                if safe is None:
                    self.send_error_json(403, 'Path not allowed')
                    return
                content = safe.read_text(encoding='utf-8')
                ext_map = {'.py':'python','.js':'javascript','.ts':'typescript','.html':'html','.css':'css','.md':'markdown','.json':'json','.yaml':'yaml','.yml':'yaml','.toml':'toml','.sh':'bash'}
                lang = ext_map.get(safe.suffix, 'text')
                self.send_json({'content': content, 'language': lang, 'path': rel_path, 'size': len(content)})
            except Exception as e:
                self.send_error_json(500, str(e))
            return

        if self.path.startswith('/api/bkd/tree'):
            try:
                from urllib.parse import urlparse, parse_qs
                qs = parse_qs(urlparse(self.path).query)
                project_id = qs.get('project_id', [None])[0]
                depth = int(qs.get('depth', ['2'])[0])
                if not project_id:
                    self.send_error_json(400, 'project_id required')
                    return
                root = _resolve_bkd_project_root(project_id)
                if root is None:
                    self.send_error_json(404, f'Project {project_id} not found')
                    return
                tree = _bkd_build_tree(root, depth=depth)
                self.send_json({'tree': tree, 'root': str(root)})
            except Exception as e:
                self.send_error_json(500, str(e))
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
                file_name = body.get('name', '')
                history = body.get('history', [])
                
                api_key = os.environ.get('GOOGLE_API_KEY')
                if not api_key:
                    self.send_error_json(500, "GOOGLE_API_KEY non configurée")
                    return

                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
                
                # Inject assets and API contract into system prompt
                asset_context = ""
                if assets:
                    asset_context = "\nImages disponibles (utilise ces URLs relatives si pertinent) :\n" + "\n".join(assets)

                api_contract = _load_api_contract()
                dom_constraint_block = format_system_prompt_constraint(file_name) if file_name else ""
                if dom_constraint_block:
                    dom_constraint_block = f"\n{dom_constraint_block}\n\n"

                manifest_block = f"\n\nCONTEXTE PROJET :\n{_MANIFEST_FRD}\n" if _MANIFEST_FRD else ""
                system_instruction = (
                    "Tu es Sullivan, expert frontend HomeOS. Tu crées ou modifies des fichiers HTML/Tailwind CSS.\n"
                    "RÈGLE CRITIQUE : Si la demande décrit une page DIFFÉRENTE de l'HTML actuel, IGNORE l'HTML actuel et crée une nouvelle page from scratch.\n"
                    "Tu réponds TOUJOURS dans ce format exact :\n"
                    "[explication courte en français, 1-2 phrases max]\n"
                    "---HTML---\n"
                    "[fichier HTML complet, rien d'autre]\n\n"
                    + dom_constraint_block
                    + manifest_block +
                    "\nROUTES API DISPONIBLES (Ne jamais inventer d'autres routes) :\n"
                    f"{api_contract}\n\n"
                    "RÈGLES ABSOLUES :\n"
                    "• Ne jamais modifier le <script> • Préserver tous les IDs • Pas de librairie externe\n\n"
                    "ANIMATIONS & TRANSITIONS :\n"
                    "• Toujours ajouter `transition-all duration-200 ease-in-out` sur l'élément animé\n"
                    "• Fade : `opacity-0 pointer-events-none` → `opacity-100` (+ class transition-opacity)\n"
                    "• Collapse/expand : JAMAIS height:auto animé. Utiliser max-height :\n"
                    "  <div class='overflow-hidden transition-[max-height] duration-300 ease-in-out' style='max-height:0'>\n"
                    "  JS : el.style.maxHeight = isOpen ? '0' : el.scrollHeight+'px'\n"
                    "• Slide drawer : `translate-x-full` ↔ `translate-x-0` avec transition-transform\n"
                    "• Spinner : `animate-spin border-2 border-current border-t-transparent rounded-full`\n"
                    "• Toggle button group actif : classList.remove('active') sur tous, classList.add('active') sur cliqué\n"
                    "• details/summary : acceptable si pas d'animation. Si animation requise → max-height pattern.\n"
                    f"{asset_context}"
                )

                mode = body.get('mode', 'construct')
                
                # Mode CONSEIL (Mission 56)
                if mode == 'conseil':
                    system_instruction = _build_conseil_prompt(message, html_context)
                    config = _ARBITRATOR.pick("quick")
                    res = _ARBITRATOR.dispatch(config, [], system=system_instruction)
                    if res.get("success"):
                        self.send_json({"explanation": res["text"], "html": "", "model": config["model"], "provider": config["provider"]})
                    else:
                        self.send_error_json(500, res.get("error", "Conseil error"))
                    return

                explanation = ""
                new_html = ""

                # --- Mission 64 : Groq Engineer Router (Transparent) ---
                route_info = {"type": "html-only", "html_spec": message}
                if mode == 'construct' and file_name:
                    # 1. Lire le contrôleur JS (via le manifeste)
                    js_code = ""
                    from Backend.Prod.retro_genome.manifest_validator import load_manifest
                    manifest = load_manifest(file_name)
                    if manifest and manifest.get('js_controller'):
                        js_rel_path = manifest['js_controller'].lstrip('/')
                        # /static/js/xxx -> static/js/xxx
                        js_abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), js_rel_path)
                        if os.path.exists(js_abs_path):
                            with open(js_abs_path, 'r', encoding='utf-8') as f:
                                js_code = f.read()

                    # 2. Router la requête via Groq
                    print(f"[MISSION 64] Routing request: {message[:50]}...")
                    last_model_turn = next((t.get('text', '') for t in reversed(history) if t.get('role') == 'model'), '')
                    route_info = _route_request(message, html_context, js_code, file_name, history=history)
                    print(f"[MISSION 64] Route: {route_info.get('type')}")

                    # text-only : Arbitre répond via Tier Quick
                    if route_info.get('type') == 'text-only':
                        txt_messages = []
                        for turn in history[-12:]:
                            txt_messages.append({"role": turn.get('role', 'user'), "content": turn.get('text', '')})
                        txt_messages.append({"role": "user", "content": message})
                        
                        config = _ARBITRATOR.pick("quick")
                        sys_txt = manifest_block + "\nTu es Sullivan. Réponds en texte markdown uniquement — pas de HTML, pas de code. Sois précis et concis."
                        
                        res = _ARBITRATOR.dispatch(config, txt_messages, system=sys_txt)
                        if res.get("success"):
                            self.send_json({"explanation": res["text"], "html": "", "model": config["model"], "provider": config["provider"]})
                        else:
                            self.send_error_json(500, res.get("error", "Text-only error"))
                        return

                    # 3. Patch JS si nécessaire
                    if route_info.get('type') in ('js-only', 'both') and route_info.get('js_patch'):
                        if manifest and manifest.get('js_controller'):
                            js_rel_path = manifest['js_controller'].lstrip('/')
                            js_abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), js_rel_path)
                            with open(js_abs_path, 'w', encoding='utf-8') as f:
                                f.write(route_info['js_patch'])
                            print(f"[MISSION 64] JS Patch appliqué : {js_rel_path}")

                    # 4. Update Manifest si nécessaire
                    if route_info.get('new_ids'):
                        _update_manifest(file_name, route_info['new_ids'])

                    # 5. Ajuster le message pour Gemini si HTML impliqué
                    if route_info.get('type') in ('html-only', 'both'):
                        groq_spec = route_info.get('html_spec') or message
                        # Si "proceed/go" → utiliser le dernier plan Sullivan comme spec (plus fidèle que la paraphrase Groq)
                        _exec_words = ('proceed', 'procède', 'go', 'génère', 'fais-le', 'lance', 'implémente', 'ok vas-y')
                        _is_exec = any(w in message.lower() for w in _exec_words)
                        if _is_exec and last_model_turn:
                            message = f"SPEC À IMPLÉMENTER (extrait du plan précédent) :\n{last_model_turn[:3000]}"
                        else:
                            message = groq_spec

                # Si c'était JS-ONLY, on peut s'arrêter là ou laisser Gemini 
                # confirmer visuellement. La roadmap suggère la transparence.
                # On continue vers Gemini si HTML est requis.
                
                # --- Mission 69 : Zones Invariantes ---
                import re
                locked_elements = re.findall(r'<(\w+)[^>]*data-frd-lock="true"[^>]*(?:id="([^"]*)")?', html_context)
                if locked_elements:
                    lock_desc = ', '.join([f'<{tag}{"#"+id_ if id_ else ""}>' for tag, id_ in locked_elements])
                    system_instruction += f"\n\nZONES INVARIANTES — NE PAS MODIFIER : {lock_desc}. Ces éléments et leur contenu sont intouchables."

                do_gemini = (route_info.get('type') in ('html-only', 'both')) or (mode == 'conseil')
                
                if do_gemini:
                    # Mode CONSEIL (Mission 56)
                    if mode == 'conseil':
                        system_instruction = _build_conseil_prompt(message, html_context)
                        payload = { "contents": [{ "parts": [{ "text": system_instruction }] }] }
                    else:
                        # Multi-turn : history + message courant
                        messages = []
                        for turn in history[-12:]:
                            messages.append({"role": turn.get('role', 'user'), "content": turn.get('text', '')})
                        messages.append({"role": "user", "content": f"{message}\n\nHTML ACTUEL:\n{html_context}"})
                        
                        config = _ARBITRATOR.pick("code-simple")
                        
                        tools = [{
                            "functionDeclarations": [
                                {
                                    "name": "read_reference",
                                    "description": "Lit un fichier de référence du projet.",
                                    "parameters": {"type": "OBJECT", "properties": {"path": {"type": "STRING"}}, "required": ["path"]}
                                },
                                {
                                    "name": "query_knowledge_base",
                                    "description": "Interroge la base de connaissance AetherFlow.",
                                    "parameters": {"type": "OBJECT", "properties": {"query": {"type": "STRING"}}, "required": ["query"]}
                                }
                            ]
                        }]

                    # Boucle tool calling (max 4 itérations)
                    res_data = None
                    for _ in range(4):
                        res = _ARBITRATOR.dispatch(config, messages, system=system_instruction, tools=tools)
                        if not res.get("success"):
                            raise Exception(res.get("error", "Construct dispatch error"))
                        
                        fc = res.get("function_call")
                        if fc and fc.get('name') == 'read_reference':
                            path_arg = fc['args'].get('path', '')
                            ref_content = _exec_read_reference(path_arg)
                            print(f"[TOOL USE] read_reference('{path_arg}') → {len(ref_content)} chars")
                            messages.append({"role": "assistant", "content": f"Appel outl read_reference: {path_arg}"})
                            messages.append({"role": "user", "content": f"RESULTAT: {ref_content}"})
                        elif fc and fc.get('name') == 'query_knowledge_base':
                            query_arg = fc['args'].get('query', '')
                            rag_content = _exec_query_knowledge_base(query_arg)
                            print(f"[RAG] query='{query_arg[:60]}' → {len(rag_content)} chars")
                            messages.append({"role": "assistant", "content": f"Appel outil query_knowledge_base: {query_arg}"})
                            messages.append({"role": "user", "content": f"RESULTAT: {rag_content}"})
                        else:
                            raw_text = res.get("text", "")
                            break

                    if mode == 'conseil':
                        self.send_json({"explanation": raw_text, "html": ""})
                        return

                    if "---HTML---" in raw_text:
                        parts = raw_text.split("---HTML---")
                        explanation = parts[0].strip()
                        new_html = parts[1].strip()
                    else:
                        explanation = raw_text
                else:
                    # JS-ONLY : Gemini n'est pas appelé
                    explanation = "Modifications logiques JS appliquées avec succès (Mode Engineer)."
                    new_html = html_context # On renvoie le HTML inchangé

                self.send_json({"explanation": explanation, "html": new_html, "model": config["model"], "provider": config["provider"]})
            except Exception as e:
                import traceback; traceback.print_exc()
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

        # Mission 68 — Endpoint /api/frd/unzip-preview
        if self.path == '/api/frd/unzip-preview':
            try:
                ctype = self.headers.get('Content-Type')
                if not ctype or 'multipart/form-data' not in ctype:
                    self.send_error_json(400, "Content-Type must be multipart/form-data")
                    return
                
                boundary = ctype.split("boundary=")[1].split(";")[0].strip().encode()
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                
                parts = body.split(b'--' + boundary)
                zip_data = None
                
                for part in parts:
                    if b'filename="' in part:
                        header_end = part.find(b'\r\n\r\n')
                        if header_end != -1:
                            zip_data = part[header_end+4:].rstrip(b'\r\n--')
                
                if not zip_data:
                    self.send_error_json(400, "No zip data found")
                    return
                
                # Isoler l'extraction dans un UUID
                uid = str(uuid.uuid4())
                temp_dir = os.path.join(cwd, STATIC_DIR, "temp_previews", uid)
                os.makedirs(temp_dir, exist_ok=True)
                
                zip_path = os.path.join(temp_dir, "dist.zip")
                with open(zip_path, 'wb') as f:
                    f.write(zip_data)
                
                # Extraire
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Chercher index.html (le plus superficiel possible)
                index_path = None
                min_depth = 999
                for root, dirs, files in os.walk(temp_dir):
                    if "index.html" in files:
                        # Count separators to find the shallowest file
                        depth = root.count(os.sep)
                        if depth < min_depth:
                            min_depth = depth
                            index_path = os.path.join(root, "index.html")
                
                if not index_path:
                    self.send_error_json(404, "Fichier index.html non trouvé dans l'archive.")
                    return

                # --- Mission 68 FIX: Injection de <base> pour corriger les chemins relatifs ---
                # On injecte <base href="/static/temp_previews/{uid}/...">
                # Cela permet à l'index.html de charger ses assets /static/temp_previews/UUID/assets/...
                rel_base_dir = os.path.relpath(os.path.dirname(index_path), os.path.join(cwd, STATIC_DIR))
                base_url = f"/static/{rel_base_dir}/"
                if not base_url.endswith('/'): base_url += '/'

                try:
                    with open(index_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    # 1. Réécrire les chemins absolus Vite (/assets/) → chemins serveur réels
                    # Vite génère src="/assets/xxx.js" — le <base> tag ne résout pas les URLs absolues
                    html_content = html_content.replace('="/assets/', f'="{base_url}assets/')
                    html_content = html_content.replace("='/assets/", f"='{base_url}assets/")
                    # 2. Injecter avant le bundle React :
                    #    - history.replaceState('/') → React Router voit '/' et matche la route par défaut
                    #    - <base> pour les URLs relatives résiduelles
                    router_fix = '<script>history.replaceState(null,"","/");</script>'
                    head_match = re.search(r'<head[^>]*>', html_content, re.IGNORECASE)
                    if head_match:
                        head_tag = head_match.group(0)
                        inject = f'{head_tag}\n    {router_fix}\n    <base href="{base_url}">'
                        html_content = html_content.replace(head_tag, inject, 1)
                    else:
                        html_content = f'{router_fix}\n<base href="{base_url}">\n' + html_content
                    
                    with open(index_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                except Exception as e:
                    print(f"Warning: could not inject <base> tag into {index_path}: {e}")


                rel_url_path = os.path.relpath(index_path, os.path.join(cwd, STATIC_DIR))
                self.send_json({"url": f"/static/{rel_url_path}"})
            except Exception as e:
                self.send_error_json(500, f"Unzip error: {str(e)}")
            return

        # Route POST /api/frd/wire (Mission 57)
        if self.path == '/api/frd/wire':
            try:
                length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(length))
                self._handle_frd_wire(body)
            except Exception as e:
                self.send_error_json(500, str(e))
            return

        # Route POST /api/frd/file (Mission 45 + 63 validation manifeste)
        if self.path == '/api/frd/file':
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length))
                name = data.get('name', '')
                content = data.get('content', '')
                if not name or '/' in name or '..' in name:
                    self.send_error_json(400, "Invalid filename")
                    return

                # Validation manifeste DOM (Mission 63)
                # force=true → avertissement seulement, save quand même
                force = data.get('force', False)
                is_valid, errors = validate_html(name, content)
                if not is_valid and not force:
                    self.send_response(422)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "error": "CONTRAT DOM VIOLÉ",
                        "violations": errors
                    }).encode('utf-8'))
                    return

                _cwd = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(_cwd, 'static/templates', name)
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

        # Mission 58 — BRS Rank (arbitrage classant)
        if self.path == '/api/brs/rank':
            self._handle_brs_rank()
            return

        # Mission 55 — BRS Multiplex Chat (POST)
        elif self.path.startswith('/api/brs/chat/'):
            try:
                provider = self.path.split('/')[-1]
                content_length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(content_length).decode('utf-8'))
                session_id = body.get('session_id')
                message = body.get('message')
                
                if not session_id or not message:
                    self.send_error_json(400, "Missing session_id or message")
                    return
                
                self.send_response(200)
                self.send_header('Content-Type', 'text/event-stream')
                self.send_header('Cache-Control', 'no-cache')
                self.send_header('Connection', 'keep-alive')
                self.end_headers()
                
                # Exécution du générateur sse_chat_generator de brainstorm_logic
                async def run_chat():
                    async for chunk in brs_logic.sse_chat_generator(session_id, provider, message):
                        self.wfile.write(chunk.encode('utf-8'))
                        self.wfile.flush()
                
                asyncio.run(run_chat())
            except Exception as e:
                logger.error(f"[BRS] server_brs_chat_error: {e}")
                self.send_error_json(500, str(e))
            return

        # --- Mission 79 : BKD Projects DB (POST/DELETE) ---
        if self.path == '/api/bkd/projects':
            try:
                length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(length).decode('utf-8'))
                name = body.get('name', '').strip()
                path = body.get('path', '').strip()
                if not name or not path:
                    self.send_error_json(400, 'name and path required')
                    return
                con = _bkd_db_con()
                existing = con.execute('SELECT id FROM projects WHERE path=?', (path,)).fetchone()
                if existing:
                    con.execute("UPDATE projects SET last_opened=datetime('now') WHERE id=?", (existing[0],))
                    con.commit()
                    con.close()
                    self.send_json({'id': existing[0], 'created': False})
                    return
                project_id = str(uuid.uuid4())
                con.execute('INSERT INTO projects (id, name, path) VALUES (?,?,?)', (project_id, name, path))
                con.commit()
                con.close()
                self.send_json({'id': project_id, 'created': True})
            except Exception as e:
                self.send_error_json(500, str(e))
            return

        if self.path.startswith('/api/bkd/projects/') and self.headers.get('X-HTTP-Method-Override','').upper() == 'DELETE':
            try:
                project_id = self.path.split('/')[-1]
                con = _bkd_db_con()
                con.execute('DELETE FROM projects WHERE id=?', (project_id,))
                con.commit()
                con.close()
                self.send_json({'ok': True, 'deleted': project_id})
            except Exception as e:
                self.send_error_json(500, str(e))
            return

        # --- Mission 80 : BKD File API (POST write) ---
        if self.path == '/api/bkd/file':
            try:
                length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(length).decode('utf-8'))
                project_id = body.get('project_id', '').strip()
                rel_path = body.get('path', '').strip()
                content = body.get('content', '')
                if not project_id or not rel_path:
                    self.send_error_json(400, 'project_id and path required')
                    return
                root = _resolve_bkd_project_root(project_id)
                if root is None:
                    self.send_error_json(404, f'Project {project_id} not found')
                    return
                safe = _bkd_safe_path(root, rel_path)
                if safe is None:
                    self.send_error_json(403, 'Path not allowed')
                    return
                safe.parent.mkdir(parents=True, exist_ok=True)
                safe.write_text(content, encoding='utf-8')
                self.send_json({'ok': True, 'path': rel_path, 'size': len(content)})
            except Exception as e:
                self.send_error_json(500, str(e))
            return

        # --- Mission 78 : Sullivan BKD Chat ---
        if self.path == '/api/bkd/chat':
            try:
                length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(length).decode('utf-8'))
                message = body.get('message', '')
                history = body.get('history', [])
                project_id = body.get('project_id', '')

                _load_env()
                api_key = os.environ.get('GOOGLE_API_KEY')
                if not api_key:
                    self.send_error_json(500, 'GOOGLE_API_KEY non configurée')
                    return

                route_info = _route_request_bkd(message, history)
                route_type = route_info.get('type', 'quick')
                config = _ARBITRATOR.pick(route_type)
                
                # Contexte projet si project_id fourni
                project_ctx = ''
                if project_id:
                    root = _resolve_bkd_project_root(project_id)
                    if root:
                        tree = _bkd_build_tree(root, depth=1)
                        tree_names = ', '.join(n['name'] for n in tree[:20])
                        project_ctx = f'\nPROJET ACTIF : {root}\nFICHIERS RACINE : {tree_names}\n'

                system_instruction = _SULLIVAN_BKD_SYSTEM + project_ctx + '\n\nMANIFEST PROJET :\n' + _MANIFEST_FRD

                messages = []
                for turn in history[-12:]:
                    messages.append({'role': turn.get('role', 'user'), 'content': turn.get('text', '')})
                messages.append({'role': 'user', 'content': message})

                tools = [{
                    'functionDeclarations': [
                        {
                            'name': 'query_knowledge_base',
                            'description': 'Interroge la base de connaissance AetherFlow (docs, PRDs, ROADMAP, Sullivan, HomeOS, Constitution).',
                            'parameters': {'type': 'OBJECT', 'properties': {'query': {'type': 'STRING'}}, 'required': ['query']}
                        },
                        {
                            'name': 'read_bkd_file',
                            'description': 'Lit le contenu d\'un fichier du projet backend.',
                            'parameters': {'type': 'OBJECT', 'properties': {'path': {'type': 'STRING'}}, 'required': ['path']}
                        }
                    ]
                }]

                final_text = ""
                for _ in range(4):
                    # Appel via l'arbitre (dispatch dynamique)
                    res = _ARBITRATOR.dispatch(config, messages, system=system_instruction, tools=tools)
                    if not res.get("success"):
                        raise Exception(res.get("error", "Unknown dispatch error"))
                    
                    fc = res.get("function_call")
                    if fc and fc.get('name') == 'query_knowledge_base':
                        q = fc['args'].get('query', '')
                        result = _exec_query_knowledge_base(q)
                        print(f'[BKD RAG] query={q[:50]} → {len(result)} chars')
                        # On met à jour l'historique interne pour le prochain tour de boucle
                        messages.append({'role': 'assistant', 'content': f'Appel outil knowledge base: {q}'})
                        messages.append({'role': 'user', 'content': f'RESULTAT: {result}'})
                    elif fc and fc.get('name') == 'read_bkd_file' and project_id:
                        rel = fc['args'].get('path', '')
                        root = _resolve_bkd_project_root(project_id)
                        file_content = ''
                        if root:
                            safe = _bkd_safe_path(root, rel)
                            if safe:
                                try:
                                    file_content = safe.read_text(encoding='utf-8')[:6000]
                                    print(f'[BKD FILE] read {rel} ({len(file_content)} chars)')
                                except Exception:
                                    file_content = f'Impossible de lire {rel}'
                            else:
                                file_content = f'Accès refusé : {rel}'
                        messages.append({'role': 'assistant', 'content': f'Appel outil read file: {rel}'})
                        messages.append({'role': 'user', 'content': f'CONTENU: {file_content}'})
                    else:
                        final_text = res.get("text", "")
                        break

                self.send_json({'explanation': final_text, 'model': config['model'], 'route': route_type, 'provider': config['provider']})
            except Exception as e:
                self.send_error_json(500, str(e))
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
        model_name = body.get('model', 'gemini-2.5-flash')

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

    def _handle_brs_rank(self):
        """Mission 58 — Arbitrage classant des 3 réponses COUNCIL."""
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            session_id = data.get('session_id')
            if not session_id:
                self.send_error_json(400, "Missing session_id")
                return
            result = asyncio.run(brs_logic.rank_council(session_id))
            self.send_json(result)
        except Exception as e:
            self.send_error_json(500, str(e))

    def _handle_frd_wire(self, body):
        """Diagnostic statique via Codestral (Mission 57)."""
        html_context = body.get('html', '')
        if not html_context:
            self.send_json({"error": "No HTML provided"}, 400)
            return

        mistral_key = os.environ.get("MISTRAL_API_KEY") or os.environ.get("MISTRAL_CHAT_KEY")
        if not mistral_key:
            self.send_json({"error": "MISTRAL_API_KEY missing"}, 500)
            return

        prompt = _build_wire_prompt(html_context)
        url = "https://api.mistral.ai/v1/chat/completions"
        payload = {
            "model": "codestral-latest",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0
        }

        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {mistral_key}'
            })
            with urllib.request.urlopen(req, timeout=30) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                diagnostic = res_data['choices'][0]['message']['content']
                self.send_json({"diagnostic": diagnostic})
        except Exception as e:
            self.send_json({"error": str(e)}, 500)

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

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
