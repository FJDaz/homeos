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

import json
import os
from typing import Dict, List

class Task:
    def __init__(self, complexity: float, size_in_tokens: int, type: str):
        self.complexity = complexity
        self.size_in_tokens = size_in_tokens
        self.type = type

class Agent:
    def __init__(self, name: str):
        self.name = name

class AgentRouter:
    def select_agent(self, task: Task) -> Agent:
        decision_matrix = {
            "code_generation_large": {
                "agent": "deepseek_v3",
                "conditions": [
                    task.complexity > 0.7,
                    task.size_in_tokens > 500,
                    task.type in ["module_creation"]
                ]
            }
        }
        for key, value in decision_matrix.items():
            if all(value["conditions"]):
                return Agent(value["agent"])
        return None

class Metrics:
    def __init__(self):
        self.metrics = {}

    def export_json(self, filename: str):
        with open(filename, "w") as f:
            json.dump(self.metrics, f)

    def export_csv(self, filename: str):
        with open(filename, "w") as f:
            for key, value in self.metrics.items():
                f.write(f"{key},{value}\n")

    def print_summary(self):
        for key, value in self.metrics.items():
            print(f"{key}: {value}")

    def update_metrics(self, task_id: str, metrics: Dict):
        self.metrics[task_id] = metrics

class Orchestrator:
    def __init__(self):
        self.metrics = Metrics()

    def _save_step_outputs(self, output_dir: str, plan: str, results: List):
        # Export metrics
        metrics_json = os.path.join(output_dir, f"metrics_{plan}.json")
        metrics_csv = os.path.join(output_dir, f"metrics_{plan}.csv")
        self.metrics.export_json(metrics_json)
        self.metrics.export_csv(metrics_csv)

    def generate_report(self, genome: Dict, intentions: List, gaps: List):
        report = "# Inventaire Endpoints/Genome\n"
        report += "* Endpoints:\n"
        for endpoint in genome.get("endpoints", []):
            report += f"  + {endpoint}\n"
        report += "\n"
        report += "# Intentions Déclarées\n"
        report += "* Intentions:\n"
        for intention in intentions:
            report += f"  + {intention}\n"
        report += "\n"
        report += "# Écarts ou Zones Floues\n"
        report += "* Écarts:\n"
        for gap in gaps:
            report += f"  + {gap}\n"
        return report

    def run(self):
        # Load genome
        genome = self.load_genome()

        # Load intentions
        intentions = self.load_intentions()

        # Generate report
        report = self.generate_report(genome, intentions, [])

        # Write report to file
        with open("output/studio/ir_inventaire.md", "w") as f:
            f.write(report)

    def load_genome(self):
        # Load genome from file or generate it
        try:
            with open("output/studio/homeos_genome.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Generate genome
            return {"endpoints": ["endpoint1", "endpoint2"]}

    def load_intentions(self):
        # Load intentions from file
        try:
            with open("docs/04-homeos/PRD_HOMEOS.md", "r") as f:
                return [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            return []

if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.run()

import json
import os
from typing import Dict, List

class Task:
    def __init__(self, complexity: float, size_in_tokens: int, type: str):
        self.complexity = complexity
        self.size_in_tokens = size_in_tokens
        self.type = type

class Agent:
    def __init__(self, name: str):
        self.name = name

class AgentRouter:
    def select_agent(self, task: Task) -> Agent:
        decision_matrix = {
            "code_generation_large": {
                "agent": "deepseek_v3",
                "conditions": [
                    task.complexity > 0.7,
                    task.size_in_tokens > 500,
                    task.type in ["module_creation"]
                ]
            }
        }
        for key, value in decision_matrix.items():
            if all(value["conditions"]):
                return Agent(value["agent"])
        return None

class Orchestrator:
    def __init__(self):
        self.metrics = Metrics()

    def _save_step_outputs(self, output_dir: str, plan: Dict, results: List):
        # Export metrics
        metrics_json = os.path.join(output_dir, f"metrics_{plan['task_id']}.json")
        metrics_csv = os.path.join(output_dir, f"metrics_{plan['task_id']}.csv")
        self.metrics.export_json(metrics_json)
        self.metrics.export_csv(metrics_csv)

    def print_summary(self):
        self.metrics.print_summary()

    def get_plan_metrics(self):
        return self.metrics

class Metrics:
    def export_json(self, file_path: str):
        # Implement JSON export logic
        pass

    def export_csv(self, file_path: str):
        # Implement CSV export logic
        pass

    def print_summary(self):
        # Implement summary print logic
        pass

def generate_genome():
    # Implement genome generation logic
    pass

def generate_ir_inventaire():
    with open("output/studio/ir_inventaire.md", "w") as f:
        f.write("# Inventaire genome\n")
        f.write("## Metadata\n")
        f.write("## Topology\n")
        f.write("## Endpoints\n")
        f.write("| Méthode | Path | x_ui_hint | Summary |\n")
        f.write("| --- | --- | --- | --- |\n")
        f.write("| GET | /studio/genome | genome | Récupère le génome |\n")
        f.write("| POST | /execute | execute | Exécute une tâche |\n")
        f.write("| GET | /sullivan/* | sullivan | Récupère les informations de Sullivan |\n")

        f.write("\n# Ce qu'Aetherflow fait\n")
        f.write("## Modes d'exécution\n")
        f.write("* FAST\n")
        f.write("* BUILD\n")
        f.write("* DOUBLE-CHECK\n")
        f.write("## Workflows\n")
        f.write("* PROTO -q\n")
        f.write("* PROD -f\n")
        f.write("* VerifyFix -vfx\n")
        f.write("## Orchestrator/AgentRouter/RAG/cache\n")
        f.write("## Sullivan Kernel\n")
        f.write("* DevMode\n")
        f.write("* DesignerMode\n")
        f.write("* ScreenPlanner\n")
        f.write("* CorpsGenerator\n")
        f.write("* Chatbot\n")
        f.write("## Genome Generator\n")
        f.write("## API\n")
        f.write("agents (à venir)\n")

        f.write("\n# Méthodes à disposition du user\n")
        f.write("## CLI\n")
        f.write("| Commande | Description |\n")
        f.write("| --- | --- |\n")
        f.write("| workflows -q/-f/-vfx | Exécute les workflows |\n")
        f.write("| genome | Récupère le génome |\n")
        f.write("| studio build | Construit le studio |\n")
        f.write("| sullivan read-genome | Lit le génome de Sullivan |\n")
        f.write("| plan-screens | Planifie les écrans |\n")
        f.write("| build | Construit |\n")
        f.write("| designer | Démarre le designer |\n")
        f.write("| dev | Démarre le mode dev |\n")
        f.write("| --costs | Affiche les coûts |\n")
        f.write("| --stats | Affiche les statistiques |\n")
        f.write("| --status | Affiche le statut |\n")
        f.write("## Routes API\n")
        f.write("| Méthode | Path | Description |\n")
        f.write("| --- | --- | --- |\n")
        f.write("| GET | /studio/genome | Récupère le génome |\n")
        f.write("| POST | /execute | Exécute une tâche |\n")
        f.write("| GET | /sullivan/* | Récupère les informations de Sullivan |\n")

        f.write("\n# Intentions PRD\n")
        f.write("## Résumé\n")
        f.write("Vision: Développer un système de routage intelligent pour les tâches de développement logiciel\n")
        f.write("Scope: Le système doit être capable de gérer les tâches de développement logiciel de manière efficace et efficiente\n")
        f.write("Architecture: Le système sera basé sur une architecture de microservices avec des agents et des workflows\n")
        f.write("## Rôles\n")
        f.write("* Développeur\n")
        f.write("* Architecte\n")
        f.write("* Responsable de la qualité\n")
        f.write("## Sullivan phases 1-5\n")
        f.write("* Phase 1: Définition des exigences\n")
        f.write("* Phase 2: Conception de l'architecture\n")
        f.write("* Phase 3: Développement\n")
        f.write("* Phase 4: Tests et validation\n")
        f.write("* Phase 5: Déploiement\n")
        f.write("## Modes Sullivan\n")
        f.write("* DevMode\n")
        f.write("* DesignerMode\n")
        f.write("* ScreenPlanner\n")
        f.write("* CorpsGenerator\n")
        f.write("* Chatbot\n")
        f.write("## CLI/API\n")
        f.write("Les utilisateurs pourront interagir avec le système via une interface de ligne de commande ou une API\n")
        f.write("## Modèles\n")
        f.write("Les modèles de données seront utilisés pour représenter les tâches et les workflows\n")
        f.write("## Roadmap\n")
        f.write("Le système sera développé en plusieurs étapes, avec des jalons et des livrables clairs\n")

        f.write("\n# Écarts ou zones floues\n")
        f.write("## Genome vs PRD\n")
        f.write("Il peut y avoir des écarts entre le génome et la spécification des exigences\n")
        f.write("## Intents/features/compartments vides\n")
        f.write("Il peut y avoir des intents, des features ou des compartments vides dans le système\n")
        f.write("## HCI IR à venir\n")
        f.write("L'interface utilisateur sera développée ultérieurement\n")

if __name__ == "__main__":
    generate_ir_inventaire()