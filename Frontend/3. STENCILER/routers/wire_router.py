"""
Wire Router - Extracted from server_v3.py
Contains all wire-related routes for the Stenciler module.
"""

import os
import re
import json
import ast
import uuid
import asyncio
import logging
import urllib.request
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Query, Body, Request
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel, Field
from bs4 import BeautifulSoup

from wire_analyzer import WireAnalyzer

logger = logging.getLogger("WireRouter")

# --- Paths ---
CWD = Path(__file__).parent.parent.resolve()
ROOT_DIR = CWD.parent.parent
PROJECTS_DIR = ROOT_DIR / "projects"
ACTIVE_PROJECT_FILE = ROOT_DIR / "active_project.json"
STATIC_DIR_PATH = CWD / "static"


# --- Pydantic Models ---

class WireRequest(BaseModel):
    html: str

class SurgicalDiagRequest(BaseModel):
    selector: str
    html: str

class PreWireRequest(BaseModel):
    screen_html: str

class PreWireValidation(BaseModel):
    selector: str
    tag: str
    text: str
    inferred_intent: str
    confirmed: bool
    custom_intent: Optional[str] = None

class PreWireValidateRequest(BaseModel):
    validations: List[PreWireValidation]

# --- Helper Functions ---

def _build_wire_prompt(html_context: str) -> str:
    return (
        "Tu es Sullivan (IA HomeOS), expert en diagnostic et implémentation de code HTML/JS.\n"
        "Analyse le code source fourni.\n\n"
        "PARTIE 1 — DIAGNOSTIC : Identifie les problèmes existants :\n"
        "- Sélecteurs orphelins (getElementById/querySelector vers IDs absents)\n"
        "- Bindings manquants (addEventListener/onclick vers fonctions non définies)\n"
        "- Fetch vers endpoints non déclarés\n"
        "- Interactions décrites dans le HTML mais sans JS correspondant\n\n"
        "PARTIE 2 — PLAN D'IMPLÉMENTATION : Liste les actions JS à implémenter pour que l'UI soit fonctionnelle. "
        "Pour chaque action : indique l'élément cible, le comportement attendu, et l'endpoint API si applicable.\n\n"
        "FORMAT (Markdown) :\n"
        "# 🕸️ Diagnostic WIRE\n\n"
        "## 🔍 Problèmes détectés\n- [Liste ou 'Aucun']\n\n"
        "## 📋 Plan d'implémentation\n"
        "1. [Action] — [Élément] → [Comportement / Endpoint]\n"
        "2. ...\n\n"
        "SOIS FACTUEL ET CONCIS. Si le fichier est un shell sans JS, liste quand même tout ce qui devrait être branché."
        f"\n\nCODE SOURCE :\n{html_context}"
    )


def get_active_project_id() -> Optional[str]:
    """Retourne l'ID du projet actif depuis le fichier active_project.json."""
    if ACTIVE_PROJECT_FILE.exists():
        try:
            data = json.loads(ACTIVE_PROJECT_FILE.read_text(encoding='utf-8'))
            return data.get("active_id")
        except:
            return None
    return None


def get_manifest_context(project_id: str):
    """Mission 181: Protocole Sullivan : Manifeste-Driven Identity."""
    try:
        if project_id == "active":
            project_id = get_active_project_id()
        manifest_path = PROJECTS_DIR / project_id / "manifest.json"
        if not manifest_path.exists():
            return "ALERTE : manifeste absent. anatomie non déclarée. rejoignez le mode CADRAGE pour initialiser cet organe."

        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        return f"""
MANIFESTE DU PROJET (SOURCE DE VÉRITÉ) :
---
ARCHETYPE : {manifest.get('archetype', 'non défini')}
ANATOMIE : {', '.join(manifest.get('anatomy', []))}
DESIGN TOKENS : {json.dumps(manifest.get('design_tokens', {}))}
WIRES (CÂBLAGE) : {len(manifest.get('wires', []))} actifs
---
"""
    except Exception as e:
        logger.error(f"Failed to load manifest context: {e}")
        return "ALERTE : Échec du chargement du manifeste."


def ensure_ids(html: str) -> str:
    """Mission 187: Injecte ou renomme les IDs pour qu'ils soient exploitables."""
    soup = BeautifulSoup(html, 'html.parser')
    counters = {}

    TAG_PREFIXES = {
        'button': 'btn', 'a': 'lnk', 'input': 'inp', 'form': 'frm',
        'select': 'sel', 'summary': 'tog', 'textarea': 'inp',
        'header': 'hdr', 'footer': 'ftr', 'nav': 'nav', 'section': 'sec'
    }

    targets = soup.find_all(['button', 'a', 'input', 'form', 'select', 'summary', 'textarea', 'header', 'footer', 'nav', 'section', 'h1', 'h2', 'h3'])

    for el in targets:
        current_id = el.get('id', '')
        is_generic = not current_id or re.match(r'^(el|div|section|block|id|tmp|gen)-\d+$', current_id) or len(current_id) < 3

        if is_generic:
            prefix = TAG_PREFIXES.get(el.name, 'el')
            raw_text = el.get_text(strip=True)[:40] or el.get('placeholder', '') or el.get('aria-label', '') or el.get('name', '')

            if raw_text:
                slug = re.sub(r'[^\w\s-]', '', raw_text).strip().lower()
                slug = re.sub(r'[\s_]+', '-', slug)
                new_id = f"{prefix}-{slug}" if slug else f"{prefix}-{counters.get(prefix, 0)+1}"
            else:
                counters[prefix] = counters.get(prefix, 0) + 1
                new_id = f"{prefix}-{counters[prefix]}"

            base_id = new_id
            c = 1
            while soup.find(id=new_id):
                new_id = f"{base_id}-{c}"
                c += 1

            el['id'] = new_id

    return str(soup)


# --- Router ---

router = APIRouter()

_wire_preview_html: str = ""


@router.post("/api/frd/wire")
async def frd_wire(req: WireRequest):
    prompt = _build_wire_prompt(req.html)
    # Note: _ARBITRATOR must be injected or imported from sullivan_arbitrator
    from sullivan_arbitrator import SullivanArbitrator
    arbitrator = SullivanArbitrator()
    config = arbitrator.pick("wire")

    def _call():
        r = urllib.request.Request(
            config["base_url"],
            data=json.dumps({
                "model": config["model"],
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0
            }).encode('utf-8'),
            headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {config["api_key"]}'}
        )
        with urllib.request.urlopen(r, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data['choices'][0]['message']['content']

    try:
        diagnostic = await asyncio.to_thread(_call)
        return {"diagnostic": diagnostic, "provider": config["provider"], "model": config["model"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/frd/wire-audit")
async def wire_audit(request: Request, name: str = Query(...)):
    """Audit technique intent <-> endpoint pour le mode Wire v2."""
    ROOT_DIR = Path(__file__).parent.parent.parent
    analyzer = WireAnalyzer(ROOT_DIR)
    return analyzer.analyze_template(name, request.app.routes)


@router.get("/api/frd/wire-source")
async def get_wire_source(endpoint: str = Query(...)):
    """
    Parser AST Python pour extraire le handler correspondant à la route dans server_v3.py.
    """
    try:
        source_path = Path(__file__).parent / "server_v3.py"
        tree = ast.parse(source_path.read_text(encoding='utf-8'))

        handler_source = "# Handler non trouvé pour cet endpoint"
        lines_range = [0, 0]

        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef) or isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call) and \
                       isinstance(decorator.func, ast.Attribute) and \
                       decorator.func.attr in ("get", "post", "put", "delete", "patch") and \
                       len(decorator.args) > 0 and \
                       isinstance(decorator.args[0], ast.Constant) and \
                       decorator.args[0].value == endpoint:

                        handler_source = ast.get_source_segment(source_path.read_text(encoding='utf-8'), node)
                        lines_range = [node.lineno, node.end_lineno]
                        return {"source": handler_source, "endpoint": endpoint, "lines": lines_range}

        return {"source": handler_source, "endpoint": endpoint, "lines": lines_range}
    except Exception as e:
        logger.error(f"Error in wire-source: {e}")
        return {"source": f"# Erreur lors du parsing : {str(e)}", "endpoint": endpoint, "lines": [0,0]}


@router.get("/api/projects/{project_id}/wire-audit")
async def wire_audit_project(project_id: str):
    """Bilan de santé du maillage selon le Corpus CLEA."""
    if project_id == "active":
        project_id = get_active_project_id()
    project_path = PROJECTS_DIR / project_id
    manifest_path = project_path / "manifest.json"
    if not manifest_path.exists():
        manifest_path = ROOT_DIR / "exports" / "manifest.json"

    manifest = {}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        except:
            manifest = {}

    analyzer = WireAnalyzer(ROOT_DIR)

    registered_routes = []
    # Note: In router context, we can't access app.routes directly
    # This would need to be passed in or accessed via request.app
    registered_routes = []

    audit = []
    raw_components = manifest.get("components", [])
    if not raw_components:
        for screen in manifest.get("screens", []):
            for corps in screen.get("corps", []):
                for organe in corps.get("organes", []):
                    raw_components.append(organe)
    components = raw_components
    backend_map = analyzer._get_backend_mapping()

    for comp in components:
        name = comp.get("name") or comp.get("label") or comp.get("id")
        intent = comp.get("role") or comp.get("intent") or comp.get("label") or "action"
        endpoint = backend_map.get(name) or backend_map.get(intent)

        status = "todo"
        if endpoint:
            match = any(r.rstrip('/') == endpoint.rstrip('/') for r in registered_routes)
            status = "ok" if match else "error"

        audit.append({
            "organ": name,
            "intent": intent,
            "endpoint": endpoint or "non défini",
            "status": status
        })

    plan = "# Plan d'Action (Revue Bionique)\n\n"
    gaps = [a for a in audit if a["status"] != "ok"]
    if not gaps:
        plan += "Votre projet est sain. Tous les organes sont correctement maillés au corps de l'application."
    else:
        for item in gaps:
            action = f"Relier l'organe '{item['organ']}' à sa fonction '{item['intent']}'"
            plan += f"- [ ] **Action** : {action}\n"

    return {"audit": audit, "plan": plan}


@router.post("/api/projects/{project_id}/pre-wire")
async def pre_wire(project_id: str, req: PreWireRequest):
    """Mission 185 : Sullivan extrait les intentions du template (Infilling)."""
    if project_id == "active":
        project_id = get_active_project_id()

    processed_html = ensure_ids(req.screen_html)
    soup = BeautifulSoup(processed_html, 'html.parser')
    interactives = []

    tags = soup.find_all(['button', 'a', 'summary'])
    inputs = soup.find_all('input', type=['submit', 'button', 'reset'])
    onclicks = soup.find_all(lambda t: t.has_attr('onclick') and t.name not in ['button', 'a'])

    for i, el in enumerate(tags + inputs + onclicks):
        selector = f"#{el['id']}" if el.has_attr('id') else f"{el.name}:nth-of-type({i+1})"
        text = el.get_text(strip=True)[:50] or el.get('value', '') or el.get('placeholder', '') or "Sans label"

        interactives.append({
            "selector": selector,
            "tag": el.name,
            "text": text,
            "id": el.get('id', ''),
            "class": " ".join(el.get('class', [])),
            "data_wire": el.get('data-wire') # Capture existing intent
        })

    if not interactives:
        return {"elements": [], "bijection": "null", "manifest_exists": False}

    project_path = PROJECTS_DIR / project_id
    manifest_path = project_path / "manifest.json"
    manifest_exists = manifest_path.exists()
    manifest_data = {}
    if manifest_exists:
        try:
            manifest_data = json.loads(manifest_path.read_text(encoding='utf-8'))
        except:
            manifest_exists = False

    prompt = f"""Tu es Sullivan, l'Expert BRS HoméOS.
Voici des éléments d'interface. Pour chacun, devine son label (nom humain) et son intent (code_action).
RÉPONDS UNIQUEMENT EN JSON : [{{ "selector": "...", "label": "...", "intent": "..." }}, ...]

ÉLÉMENTS :
{json.dumps(interactives[:20], ensure_ascii=False)}
"""
    from sullivan_arbitrator import SullivanArbitrator
    arbitrator = SullivanArbitrator()
    config = arbitrator.pick("quick")
    res = await asyncio.to_thread(arbitrator.dispatch, config, [{"role":"user", "content": prompt}])
    inferred = []
    try:
        cleaned_json = res.get("text", "[]").strip()
        if "```json" in cleaned_json:
            cleaned_json = cleaned_json.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned_json:
            cleaned_json = cleaned_json.split("```")[1].split("```")[0].strip()
        inferred = json.loads(cleaned_json)
    except Exception as e:
        logger.error(f"Failed to parse Sullivan inference: {e}")

    existing_intents = []
    for s in manifest_data.get("screens", []):
        for c in s.get("corps", []):
            for o in c.get("organes", []):
                existing_intents.append(o.get("id") or o.get("role"))

    final_elements = []
    matches = 0
    for inf in inferred:
        orig = next((x for x in interactives if x['selector'] == inf.get('selector')), {})
        
        # PRE-SELECTION: matched if LLM guess matches manifest OR if it already had a data-wire
        matched = (inf.get("intent") in existing_intents) or (orig.get("data_wire") in existing_intents)
        if matched:
            matches += 1

        final_elements.append({
            "selector": inf.get("selector"),
            "id": orig.get("id", ""),
            "tag": orig.get("tag", "div"),
            "text": orig.get("text", "Sans texte"),
            "inferred_intent": inf.get("intent"),
            "endpoint": inf.get("endpoint", ""),
            "matched": matched
        })

    bijection = "total" if matches == len(final_elements) else "incomplete"
    if matches == 0:
        bijection = "null"

    return {
        "elements": final_elements,
        "bijection": bijection,
        "manifest_exists": manifest_exists,
        "enriched_html": str(soup)
    }


@router.post("/api/projects/{project_id}/pre-wire/validate")
async def pre_wire_validate(project_id: str, req: PreWireValidateRequest):
    """Mission 185 : Sullivan met à jour le manifeste après validation humaine."""
    if project_id == "active":
        project_id = get_active_project_id()

    project_path = PROJECTS_DIR / project_id
    manifest_path = project_path / "manifest.json"

    manifest = {"name": project_id, "screens": [{"id": "workspace", "corps": [{"id": "main", "organes": []}]}]}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        except:
            pass

    if "screens" not in manifest or not manifest["screens"]:
        manifest["screens"] = [{"id": "workspace", "corps": [{"id": "main", "organes": []}]}]

    organs = manifest["screens"][0]["corps"][0]["organes"]
    pending = manifest.get("pending_intents", [])

    count = 0
    for val in req.validations:
        if not val.confirmed:
            pending.append({
                "selector": val.selector,
                "text": val.text,
                "tag": val.tag,
                "note": val.custom_intent or "utilisateur à défini 'autre'"
            })
            continue

        intent = val.custom_intent or val.inferred_intent
        existing = next((o for o in organs if o.get("id") == intent or o.get("role") == intent), None)

        if existing:
            existing["name"] = val.text
            existing["selector"] = val.selector
        else:
            organs.append({
                "id": intent,
                "name": val.text,
                "role": intent,
                "selector": val.selector
            })
        count += 1

    manifest["pending_intents"] = pending
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
    logger.info(f"✅ [WiRE] Manifeste mis à jour ({count} organes validés, {len(pending)} en attente) pour {project_id}")

    return {"status": "success", "organs_count": count, "pending_count": len(pending)}


@router.post("/api/projects/{project_id}/wire-apply")
async def wire_apply_plan(project_id: str, req: Dict[str, Any]):
    """Mission 187 : Forge déterministe (Plus de LLM). Applique les validations confirmées."""
    if project_id == "active":
        project_id = get_active_project_id()
    screen_html = req.get("screen_html")
    validations = req.get("validations", [])
    if not screen_html:
        return {"status": "error", "message": "screen_html manquant"}

    try:
        soup = BeautifulSoup(screen_html, 'html.parser')
        modified_elements = []

        for v in validations:
            el_id = v.get('id')
            intent = v.get('intent') or v.get('inferred_intent')
            endpoint = v.get('endpoint')
            if not el_id or not intent:
                continue

            el = soup.find(id=el_id)
            if el:
                el['data-wire'] = intent
                if endpoint:
                    el['data-endpoint'] = endpoint
                modified_elements.append(f"#{el_id}")

        new_html = str(soup)

        template_name = req.get("template_name")
        if template_name and '/' not in template_name and '..' not in template_name:
            template_file = STATIC_DIR_PATH / "templates" / template_name
            if template_file.exists():
                shutil.copy2(template_file, template_file.with_suffix('.html.bak'))
                template_file.write_text(new_html, encoding='utf-8')
                logger.info(f"Forge saved to {template_file}")

        wire_runtime = """<script>
(function(){
    const WIRE_BASE = window.parent?.location?.origin || window.location.origin;
    function showToast(msg, ok){
        let t = document.getElementById('_wire_toast');
        if(!t){ t = document.createElement('div'); t.id='_wire_toast';
            t.style.cssText='position:fixed;bottom:24px;right:24px;z-index:99999;padding:12px 20px;border-radius:10px;font-size:13px;font-family:system-ui,sans-serif;max-width:320px;box-shadow:0 4px 16px rgba(0,0,0,.15);transition:opacity .3s;white-space:pre-wrap;line-height:1.4';
            document.body.appendChild(t); }
        t.style.background = ok ? '#f0fce8' : '#fff3cd';
        t.style.color = ok ? '#2d5a0e' : '#856404';
        t.style.border = ok ? '1px solid #8cc63f' : '1px solid #ffc107';
        t.textContent = msg; t.style.opacity='1';
        clearTimeout(t._hide); t._hide = setTimeout(()=>{ t.style.opacity='0'; }, 5000);
    }
    async function execute(wire, userInput, endpoint){
        showToast('⏳ ' + wire + '…', true);
        try {
            const base = window.parent?.location?.origin || 'http://localhost:9998';
            const res = await fetch(base + '/api/wire-execute', {
                method:'POST', headers:{'Content-Type':'application/json'},
                body: JSON.stringify({ wire, user_input: userInput, endpoint })
            });
            const data = await res.json();
            showToast(data.response || data.message || '✓ action exécutée', true);
        } catch(e) { showToast('❌ erreur wire : ' + e.message, false); }
    }
    document.addEventListener('DOMContentLoaded', ()=>{
        document.querySelectorAll('[data-wire]').forEach(el => {
            const wire = el.getAttribute('data-wire');
            const endpoint = el.getAttribute('data-endpoint') || '';
            el.addEventListener('click', e => {
                const container = el.closest('form') || el.parentElement;
                const input = container?.querySelector('textarea,input[type=text],input:not([type])');
                const userInput = input?.value || '';
                if(el.tagName === 'A') e.preventDefault();
                execute(wire, userInput, endpoint);
            });
        });
    });
})();
</script>"""
        if '</head>' in new_html:
            new_html = new_html.replace('</head>', wire_runtime + '\n</head>')
        else:
            new_html = wire_runtime + new_html

        return {"status": "success", "html": new_html, "modified_elements": modified_elements or []}
    except Exception as e:
        logger.error(f"❌ [WiRE] Échec de la Forge Déterministe : {e}")
        return {"status": "error", "message": str(e)}
    finally:
        # --- MISSION 189 : Auto-compile HOMEO_GENOME.md après forge ---
        try:
            import sys
            backend_prod = ROOT_DIR / "Backend/Prod"
            if str(backend_prod) not in sys.path:
                sys.path.insert(0, str(backend_prod))
            from sullivan.genome_compiler import GenomeCompiler
            compiler = GenomeCompiler(PROJECTS_DIR / project_id)
            compiler.compile()
            logger.info(f"[WiRE] HOMEO_GENOME.md auto-compiled after wire-apply for {project_id}")
        except Exception as e:
            logger.warning(f"[WiRE] Genome auto-compile failed (non-blocking): {e}")


@router.post("/wire-preview")
async def set_wire_preview(req: Dict[str, Any]):
    global _wire_preview_html
    _wire_preview_html = req.get("html", "")
    return {"status": "ok"}


@router.get("/wire-preview")
async def get_wire_preview():
    return HTMLResponse(content=_wire_preview_html or "<p>aucun preview</p>")


@router.post("/api/wire-execute")
async def wire_execute(request: Request, req: Dict[str, Any]):
    """Runtime Wire : intercepte une action et appelle Groq. Mission 137: BYOK."""
    from core.key_resolver import resolve_key
    wire = req.get("wire", "")
    user_input = req.get("user_input", "")
    endpoint = req.get("endpoint", "")
    user_id = getattr(request.state, 'user_id', None)

    api_key = resolve_key("groq", user_id)
    if not api_key:
        return {"response": f"[wire:{wire}] Clé Groq manquante — configurez-la via ⚙ Settings"}

    system = (
        f"Tu es un assistant IA branché sur l'interface HoméOS.\n"
        f"L'utilisateur a déclenché l'action : '{wire}'.\n"
        f"Réponds de manière courte et utile (1-3 phrases max)."
    )
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_input or f"action: {wire}"},
        ],
        "temperature": 0.7,
        "max_tokens": 200,
    }
    try:
        import urllib.request as urlreq
        r = urlreq.Request(url, data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}", "User-Agent": "AetherFlow/1.0"})
        with urlreq.urlopen(r, timeout=15) as resp:
            data = json.loads(resp.read())
        response = data["choices"][0]["message"]["content"].strip()
        return {"response": response}
    except Exception as e:
        logger.error(f"[wire-execute] erreur Groq : {e}")
        return {"response": f"erreur groq : {e}"}


@router.post("/api/projects/{project_id}/wire-catchup")
async def wire_catchup(project_id: str):
    """Mission 187 : Sullivan suggère des intentions/endpoints pour les 'autre' mis en attente."""
    if project_id == "active":
        project_id = get_active_project_id()

    project_path = PROJECTS_DIR / project_id
    manifest_path = project_path / "manifest.json"
    if not manifest_path.exists():
        return {"status": "error", "message": "Manifeste introuvable"}

    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    pending = manifest.get("pending_intents", [])
    if not pending:
        return {"status": "success", "suggestions": []}

    prompt = f"""Tu es Sullivan, l'Expert de Maillage AetherFlow (Corpus CLEA).
MISSION : Suggère des intentions (intent) et des endpoints (METHOD /path) pour ces éléments mis en attente.

ÉLÉMENTS EN ATTENTE :
{json.dumps(pending, ensure_ascii=False)}

RÈGLES DE NOMMAGE (CLEA) :
- intent : snake_case (ex: valider_commande, voir_profil)
- endpoint : METHODE /chemin (ex: POST /api/cart/validate, GET /api/user/profile)

Réponds UNIQUEMENT avec un JSON pur sous ce format :
[
  {{"id": "id-de-l-element", "intent": "suggestion_intent", "endpoint": "METHOD /suggestion/path"}},
  ...
]
"""
    try:
        from sullivan_arbitrator import SullivanArbitrator
        arbitrator = SullivanArbitrator()
        config = arbitrator.pick("construction")
        res = await asyncio.to_thread(arbitrator.dispatch, config, [{"role":"user", "content": prompt}])
        text = res.get("text", "[]")

        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        suggestions = json.loads(text)
        return {"status": "success", "suggestions": suggestions}
    except Exception as e:
        logger.error(f"Error in wire-catchup: {e}")
        return {"status": "error", "message": str(e)}


@router.post("/api/projects/{project_id}/surgical-diag")
async def surgical_diag(project_id: str, req: SurgicalDiagRequest):
    """Diagnostic chirurgical ciblé (CLEA UX)."""
    if project_id == "active":
        project_id = get_active_project_id()

    manifest_context = get_manifest_context(project_id)

    prompt = f"""Tu es Sullivan, l'Arbitre de Maillage HoméOS (Corpus CLEA).
{manifest_context}
CONTEXTE : L'utilisateur inspecte un organe spécifique qui semble présenter un défaut de câblage.
ORGANE (Sélecteur) : {req.selector}
EXTRAIT HTML : {req.html[:1000]}

MISSION : Produis un diagnostic "Bilan de Santé" court et sémantique (style CLEA).
- Utilise le "Fil d'Ariane émotionnel" : rassurer l'utilisateur.
- Utilise "L'erreur qui guide" : explique comment réparer le pont serveur.
- Jargon technique INTERDIT (pas de 'endpoint', '404', 'api'). Utilise 'Pont Serveur', 'Flux', 'Maillage', 'Organe'.

Réponds en 3-4 lignes maximum. Pas de prose, pas de markdown complexe.
"""
    from sullivan_arbitrator import SullivanArbitrator
    arbitrator = SullivanArbitrator()
    config = arbitrator.pick("quick")
    res = await asyncio.to_thread(arbitrator.dispatch, config, [{"role":"user", "content": prompt}])
    return {"explanation": res.get("text", "Diagnostic indisponible.")}
