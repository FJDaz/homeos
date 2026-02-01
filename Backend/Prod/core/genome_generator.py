"""Genome generator: scan API, produce homeos_genome.json (ex-Contrat)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

# Lazy import to avoid circular deps / heavy init
def _get_openapi() -> Dict[str, Any]:
    from ..api import app
    return app.openapi()


def _path_to_ui_hint(path: str, method: str) -> str:
    """
    Déduit x_ui_hint depuis path + method avec heuristiques enrichies.
    
    Args:
        path: API path
        method: HTTP method
        
    Returns:
        x_ui_hint string (terminal, gauge, form, dashboard, status, list, detail, create, update, delete, ou generic)
    """
    p = path.lower()
    m = method.lower()
    
    # Patterns spécifiques d'abord (pour éviter faux positifs)
    
    # Patterns Auth (avant "log" pour éviter confusion avec /login)
    if any(auth in p for auth in ["/login", "/logout", "/auth", "/authenticate", "/register"]):
        return "form"
    
    # Patterns File (avant patterns génériques)
    if any(file_op in p for file_op in ["/upload", "/download", "/files", "/file"]):
        return "form"
    
    # Patterns Config
    if any(config in p for config in ["/settings", "/config", "/preferences", "/options"]):
        return "form"
    
    # Patterns Action
    if any(action in p for action in ["/execute", "/run", "/start", "/stop", "/cancel"]):
        return "form"
    
    # Patterns Query
    if any(query in p for query in ["/search", "/filter", "/query", "/find"]):
        return "dashboard"
    
    # Patterns Metrics
    if any(metric in p for metric in ["/metrics", "/stats", "/analytics", "/performance"]):
        return "gauge"
    
    # Heuristiques existantes (préservées)
    if p.endswith("/log") or "/log/" in p:  # Plus spécifique pour éviter /login
        return "terminal"
    if "score" in p:
        return "gauge"
    if path == "/execute" or (m == "post" and "execute" in p):
        return "form"
    if "component" in p or "search" in p:
        return "dashboard"
    if "health" in p or "status" in p:
        return "status"
    if "analyze" in p or "designer" in p or "dev" in p:
        return "form"
    
    # Patterns CRUD - List/Dashboard
    if m == "get" and ("{" not in path):  # GET sans paramètre = liste
        if any(segment in p for segment in ["/users", "/items", "/components", "/products", "/orders"]):
            return "dashboard"  # ou "list" si ajouté au builder
    
    # Patterns Detail - GET avec {id}
    if m == "get" and "{" in path:
        return "detail"  # ou "dashboard" si detail non supporté
    
    # Patterns Create - POST sur collection
    if m == "post" and ("{" not in path):
        if any(segment in p for segment in ["/users", "/items", "/create", "/add", "/new"]):
            return "form"
    
    # Patterns Update - PUT/PATCH avec {id}
    if m in ("put", "patch") and "{" in path:
        return "form"
    
    # Patterns Delete - DELETE avec {id}
    if m == "delete" and "{" in path:
        return "form"  # ou "delete" si ajouté au builder
    
    # Fallback
    return "generic"


def _path_to_ui_hint_enriched(path: str, method: str, summary: str = "") -> str:
    """
    Déduit x_ui_hint avec heuristiques + IntentTranslator/STAR pour enrichir l'inférence.
    
    Args:
        path: API path
        method: HTTP method
        summary: Endpoint summary/description (optionnel)
        
    Returns:
        x_ui_hint string
    """
    # Appeler d'abord _path_to_ui_hint() pour heuristiques basiques
    hint = _path_to_ui_hint(path, method)
    
    # Si résultat = "generic", utiliser IntentTranslator pour analyse sémantique
    if hint == "generic":
        try:
            # Lazy import d'IntentTranslator pour éviter dépendances circulaires
            from ..sullivan.intent_translator import IntentTranslator
            
            # Créer instance IntentTranslator (peut être coûteux, mais seulement si generic)
            intent_translator = IntentTranslator()
            
            # Construire query pour analyse sémantique
            query = f"{path} {method} {summary}".strip()
            
            # Rechercher situations similaires avec embeddings
            situations = intent_translator.search_situation(query, limit=3)
            
            if situations:
                # Propager STAR pour obtenir réalisations
                for situation in situations:
                    realisation = intent_translator.propagate_star(situation)
                    if realisation:
                        # Mapper patterns STAR vers x_ui_hint
                        pattern_name = situation.pattern_name.lower() if situation.pattern_name else ""
                        
                        # Patterns UI interactifs → form ou dashboard
                        if any(p in pattern_name for p in ["toggle", "accordion", "modal"]):
                            hint = "form"
                            logger.debug(f"STAR pattern '{pattern_name}' → hint 'form' for {path}")
                            break
                        
                        # Pattern Navigation → dashboard ou list
                        if "navigation" in pattern_name:
                            hint = "dashboard"
                            logger.debug(f"STAR pattern '{pattern_name}' → hint 'dashboard' for {path}")
                            break
                
                if hint != "generic":
                    logger.info(f"Enriched hint for {path}: generic → {hint} (via STAR)")
            
        except ImportError as e:
            logger.debug(f"IntentTranslator not available: {e}. Using basic heuristics.")
        except Exception as e:
            logger.warning(f"Error using IntentTranslator for {path}: {e}. Using basic heuristics.")
    
    return hint


def generate_genome(
    output_path: Path | None = None,
    intent: str = "PaaS_Studio",
    topology: List[str] | None = None,
) -> Path:
    """
    Génère le Genome (homeos_genome.json) à partir de l'API FastAPI.

    Args:
        output_path: Fichier de sortie. Si None, output/studio/homeos_genome.json.
        intent: metadata.intent (défaut PaaS_Studio).
        topology: metadata.topology (défaut Brainstorm, Back, Front, Deploy).

    Returns:
        Chemin du fichier écrit.
    """
    from ..config.settings import settings

    topology = topology or ["Brainstorm", "Back", "Front", "Deploy"]
    base = Path(settings.output_dir) / "studio"
    if output_path is None:
        output_path = base / "homeos_genome.json"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    openapi = _get_openapi()
    paths = openapi.get("paths") or {}
    components = openapi.get("components") or {}
    schemas = components.get("schemas") or {}

    endpoints: List[Dict[str, Any]] = []
    for path, spec in paths.items():
        if not isinstance(spec, dict):
            continue
        for method, op in spec.items():
            if method.lower() not in ("get", "post", "put", "patch", "delete"):
                continue
            if not isinstance(op, dict):
                continue
            summary = (op.get("summary") or op.get("description") or "").strip() or path
            # Utiliser _path_to_ui_hint_enriched() avec summary pour enrichir l'inférence
            hint = _path_to_ui_hint_enriched(path, method, summary)
            endpoints.append({
                "method": method.upper(),
                "path": path,
                "x_ui_hint": hint,
                "summary": summary[:200],
            })

    schema_definitions: Dict[str, Any] = {}
    for name, s in schemas.items():
        if not isinstance(s, dict):
            continue
        schema_definitions[name] = {
            "type": s.get("type", "object"),
            "properties": s.get("properties"),
            "required": s.get("required"),
        }

    genome = {
        "metadata": {
            "intent": intent,
            "version": "0.1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "topology": topology,
        "endpoints": endpoints,
        "schema_definitions": schema_definitions,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(genome, f, indent=2, ensure_ascii=False)

    # Compter les generic pour monitoring
    generic_count = sum(1 for ep in endpoints if ep.get("x_ui_hint") == "generic")
    generic_percentage = (generic_count / len(endpoints) * 100) if endpoints else 0
    
    logger.info(
        f"Genome generated: {len(endpoints)} endpoints, {len(schema_definitions)} schemas -> {output_path}"
    )
    logger.info(
        f"x_ui_hint distribution: {generic_count}/{len(endpoints)} generic ({generic_percentage:.1f}%)"
    )
    
    return output_path


def run_genome_cli(output_path: Path | str | None = None) -> int:
    """
    Point d'entrée CLI pour la génération du Genome.

    Returns:
        0 en succès, 1 en erreur.
    """
    try:
        out = Path(output_path) if output_path else None
        path = generate_genome(output_path=out)
        print(f"Genome written: {path}")
        return 0
    except Exception as e:
        logger.exception("Genome generation failed")
        print(f"Error: {e}")
        return 1


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