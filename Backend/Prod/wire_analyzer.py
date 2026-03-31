import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any

class WireAnalyzer:
    """
    Moteur de bijection AetherFlow.
    Analyse les templates HTML pour extraire les intentions et les compare aux routes FastAPI.
    """

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.templates_dir = root_dir / "Frontend/3. STENCILER/static/templates"

    def analyze_template(self, template_name: str, app_routes: List[Any]) -> Dict[str, Any]:
        """
        Analyse un template spécifique.
        """
        html_path = self.templates_dir / template_name
        if not html_path.exists():
            return {"error": f"Template {template_name} not found"}

        content = html_path.read_text(encoding="utf-8")
        
        # 1. Extraction des intentions (data-af-intent, IDs evocateurs, etc.)
        intents = self._extract_intents(content)
        
        # 2. Extraction des appels API (fetch, manual calls)
        calls = self._extract_api_calls(content)
        
        # 3. Récupération des routes réelles
        registered_routes = self._parse_app_routes(app_routes)
        
        # 4. Bijection & Gap Analysis
        findings = self._compute_gaps(intents, calls, registered_routes)
        
        return {
            "template": template_name,
            "intents_found": len(intents),
            "intentions": [f["intent_id"] for f in findings],
            "statuts": [f["status"] for f in findings],
            "plan": [f.get("advice", {}).get("architect", "Endpoint opérationnel") if f["status"] == "error" else "Endpoint opérationnel" for f in findings],
            "findings": findings,
            "summary": {
                "ok": len([f for f in findings if f["status"] == "ok"]),
                "todo": len([f for f in findings if f["status"] == "todo"]),
                "error": len([f for f in findings if f["status"] == "error"])
            }
        }

    # Fonctions UI-only qui ne correspondent à aucun endpoint API
    UI_ONLY_FUNCTIONS = {
        'setMode', 'togglePanel', 'showTable', 'closeModal', 'openModal',
        'closePopover', 'toggleSidebar', 'removeFile', 'clearInput'
    }

    def _get_backend_mapping(self) -> Dict[str, str]:
        """Extrait le mapping intent -> route depuis backend.md."""
        mapping = {}
        b_path = self.root_dir / "backend.md"
        if not b_path.exists():
            return mapping
        
        try:
            content = b_path.read_text(encoding="utf-8")
            # Pattern: | Component[intent] | METHOD /api/... |
            for line in content.splitlines():
                # On capture le bloc "Component[intent]" et la route "/api/..."
                m = re.search(r'\|\s*([\w\-]+\[[\w\-]+\]|[\w\-]+)\s*\|\s*(\w+)\s+([^\s\|]+)', line)
                if m:
                    raw_id = m.group(1) # "Button[cta]" ou "login"
                    route = m.group(3)
                    # Si c'est du type Comp[intent], on indexe aussi par intent seul
                    if '[' in raw_id:
                        intent_only = raw_id.split('[')[1].split(']')[0]
                        mapping[intent_only] = route
                    mapping[raw_id] = route
        except Exception as e:
            print(f"[Wire] Error reading backend.md: {e}")
        return mapping

    def _extract_intents(self, html: str) -> List[Dict[str, str]]:
        """Extrait les intentions marquées via data-af-*, onclick et forms."""
        intents = []
        # Support data-af-intent="intent_id"
        for m in re.finditer(r'data-af-intent=["\'](.*?)["\']', html):
            intents.append({"id": m.group(1), "type": "data-af-intent"})

        # Support onclick dispatchers — nom brut pour INTENT_MAP + selector
        # Filtre : identifiant simple camelCase uniquement (pas document.xxx, this.xxx...)
        for m in re.finditer(r'onclick=["\']([a-zA-Z_]\w*)\s*\(', html):
            raw_func = m.group(1)
            if raw_func in self.UI_ONLY_FUNCTIONS:
                continue  # Exclure les fonctions UI-only sans endpoint API
            intents.append({"id": raw_func, "type": "onclick"})
        
        # Forms actions
        for m in re.finditer(r'action=["\'](.*?)["\']', html):
            intents.append({"id": m.group(1), "type": "form_action"})

        return intents

    def _extract_api_calls(self, html: str) -> List[str]:
        """Extrait les URLs d'API appelées via fetch() ou ajax."""
        calls = set()
        # fetch('/api/...')
        for m in re.finditer(r"fetch\(['\"](.*?)['\"]", html):
            calls.add(m.group(1))
        # API calls in static JS strings
        for m in re.finditer(r"['\"]/api/(.*?)['\"]", html):
            calls.add(f"/api/{m.group(1)}")
        return list(calls)

    def _parse_app_routes(self, routes: List[Any]) -> List[Dict[str, str]]:
        """Transforme les objets routes de FastAPI en liste simple pour comparaison."""
        parsed = []
        for route in routes:
            if hasattr(route, "path"):
                methods = list(route.methods) if hasattr(route, "methods") else ["GET"]
                parsed.append({"path": route.path, "methods": methods})
        return parsed

    def _compute_gaps(self, intents, calls, routes) -> List[Dict[str, Any]]:
        findings = []
        route_paths = [r["path"] for r in routes]
        
        # 0. Mapping intention -> endpoint probable (Source of Truth: backend.md)
        BACKEND_MAP = self._get_backend_mapping()
        
        # Mapping statique fallback
        STATIC_MAP = {
            "runWire": "/api/frd/wire",
            "sendChat": "/api/frd/chat",
            "saveTemplate": "/api/frd/save",
            "upload": "/api/retro-genome/upload",
            "validate": "/api/retro-genome/validate",
            "status": "/api/retro-genome/status"
        }

        # 1. Process explicit intents (onclick, data-af-intent)
        for intent in intents:
            intent_id = intent["id"]
            # Priorité 1: backend.md, Priorité 2: Mapping statique
            endpoint = BACKEND_MAP.get(intent_id) or STATIC_MAP.get(intent_id)
            selector = f"[onclick*='{intent_id}']" if intent["type"] == "onclick" else f"[data-af-intent='{intent_id}']"
            
            if not endpoint:
                # Pas de mapping connu → à implémenter (attente design)
                findings.append({
                    "target": "unknown",
                    "intent_id": intent_id,
                    "selector": selector,
                    "status": "todo",
                    "message": "À implémenter — aucun endpoint mappé",
                    "advice": {
                        "architect": f"L'intention '{intent_id}' n'est mappée à aucune route. Définir dans backend.md.",
                        "ouvrier": f"Créer la route correspondante et l'ajouter à backend.md."
                    }
                })
                continue

            match = any(r_path.rstrip('/') == endpoint.rstrip('/') for r_path in route_paths)
            status = "ok" if match else "error"
            message = "Endpoint opérationnel" if match else "Endpoint déclaré mais absent de FastAPI"

            findings.append({
                "target": endpoint,
                "intent_id": intent_id,
                "selector": selector,
                "status": status,
                "message": message,
                "advice": {
                    "architect": f"L'intention '{intent_id}' pointe vers {endpoint} — route manquante.",
                    "ouvrier": f"Implémenter la route {endpoint} dans server_v3.py."
                } if status == "error" else None
            })

        # 2. Process remaining API calls not tied to an intent
        processed_endpoints = [f["target"] for f in findings]
        for call in calls:
            if call in processed_endpoints: continue
            
            base_url = call.split('?')[0]
            match = False
            for r_path in route_paths:
                pattern = re.sub(r'\{.*?\}', '.*', r_path)
                if re.fullmatch(pattern.rstrip('/'), base_url.rstrip('/')):
                    match = True; break
            
            findings.append({
                "target": call,
                "intent_id": "direct_fetch",
                "selector": f"[href*='{call}'], [src*='{call}']",
                "status": "ok" if match else "error",
                "message": "Endpoint opérationnel" if match else "Endpoint manquant"
            })
        
        return findings

if __name__ == "__main__":
    # Test unitaire rapide
    analyzer = WireAnalyzer(Path("/Users/francois-jeandazin/AETHERFLOW"))
    print(json.dumps(analyzer.analyze_template("intent_viewer.html", []), indent=2))
