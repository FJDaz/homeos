homeos/
├── ir/
│   ├── __init__.py
│   ├── pipeline.py
│   ├── models.py
│   ├── services.py
│   └── arbiter.py
└── tests/
    └── test_ir_pipeline.py

from typing import Dict, List, Tuple
from homeos.ir.models import ValidationResult

class SullivanArbiter:
    """Validator for genome dictionaries."""

    REQUIRED_KEYS = {'metadata', 'topology', 'endpoints'}
    OPTIONAL_KEYS = {'intents', 'features', 'compartments'}

    def validate(self, genome: Dict) -> ValidationResult:
        """
        Validate a genome dictionary.

        Args:
            genome: Dictionary to validate

        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult(valid=True)

        # Check required keys
        for key in self.REQUIRED_KEYS:
            if key not in genome:
                result.add_error(f"Missing required key: {key}")

        # Check optional keys are lists if present
        for key in self.OPTIONAL_KEYS:
            if key in genome and not isinstance(genome[key], list):
                result.add_error(f"Key '{key}' must be a list, got {type(genome[key])}")

        return result

import json
from pathlib import Path
from typing import Optional, Dict

from Backend.Prod.core.genome_generator import generate_genome

class IRPipeline:
    def run(self, backend_path: Optional[Path] = None, prd_path: Optional[Path] = None, output_path: Optional[Path] = None) -> Dict:
        """
        Run the IR pipeline to generate the genome_v1 dict.

        Args:
        - backend_path (Optional[Path]): The path to the backend (default: None)
        - prd_path (Optional[Path]): The path to the PRD (default: None)
        - output_path (Optional[Path]): The path to write the genome_v1 dict (default: None)

        Returns:
        - genome_v1 (Dict): The generated genome_v1 dict
        """

        # Call Backend.Prod.core.genome_generator.generate_genome to get base genome dict
        genome = generate_genome()

        # Ensure genome has top-level keys intents (list), features (list), compartments (list); add empty lists if missing
        genome.setdefault("intents", [])
        genome.setdefault("features", [])
        genome.setdefault("compartments", [])

        # Create the genome_v1 dict
        genome_v1 = genome

        # Write to output_path if provided (default output/studio/genome_v1.json)
        if output_path is None:
            output_path = Path("output/studio/genome_v1.json")
        with open(output_path, "w") as f:
            json.dump(genome_v1, f, indent=4)

        return genome_v1

import json
from pathlib import Path
from typing import Optional, Dict
import logging
from homeos.ir.arbiter import SullivanArbiter

class IRPipeline:
    def run(self, backend_path: Optional[Path] = None, prd_path: Optional[Path] = None, output_path: Optional[Path] = None, validate: bool = True) -> Optional[Dict]:
        """
        Run the IR pipeline to generate the genome_v1 dict.

        Args:
        - backend_path (Optional[Path]): The path to the backend (default: None)
        - prd_path (Optional[Path]): The path to the PRD (default: None)
        - output_path (Optional[Path]): The path to write the genome_v1 dict (default: None)
        - validate (bool): Whether to validate the genome_v1 dict (default: True)

        Returns:
        - genome_v1 (Optional[Dict]): The generated genome_v1 dict, or None if validation fails
        """

        # Call Backend.Prod.core.genome_generator.generate_genome to get base genome dict
        genome = generate_genome()

        # Ensure genome has top-level keys intents (list), features (list), compartments (list); add empty lists if missing
        genome.setdefault("intents", [])
        genome.setdefault("features", [])
        genome.setdefault("compartments", [])

        # Create the genome_v1 dict
        genome_v1 = genome

        # Validate the genome_v1 dict if required
        if validate:
            arbiter = SullivanArbiter()
            validation_result = arbiter.validate(genome_v1)
            if not validation_result['valid']:
                logging.error("Genome validation failed:")
                for error in validation_result['errors']:
                    logging.error(error)
                return None

        # Write to output_path if provided (default output/studio/genome_v1.json)
        if output_path is None:
            output_path = Path("output/studio/genome_v1.json")
        with open(output_path, "w") as f:
            json.dump(genome_v1, f, indent=4)

        return genome_v1

# Example usage
if __name__ == "__main__":
    # Create an instance of the IRPipeline class
    ir_pipeline = IRPipeline()

    # Run the

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