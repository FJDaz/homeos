# MANIFESTE_HOMEOS_V0

## INTENTION PRIMAIRE

"Construire une interface d'administration (Studio) pour Homeos qui soit :

1. Aussi autoconstructive qu'Aetherflow
2. Pédagogique (enseigne les bonnes pratiques)
3. Brutaliste mais lisible (Gumroad + iA.net)
4. Séparée clairement des interfaces générées pour les utilisateurs"

## CONTRAINTES HCI FORTES

- **Navigation** : 3 niveaux max (Brainstorm > Back > Front > Deploy)
- **Z-index stratifié** : Sullivan UI (10000) > Studio (1000) > Interface utilisateur (1)
- **Validation** : Obligatoire à chaque étape de construction
- **Fallback** : Design principles des 8 références si validation rapide

## RÉFÉRENCES

- PRD_HOMEOS.md
- docs/02-sullivan/DÉTAILS_CONSTRUCTION_INTERFACE.md


import os
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Task:
    complexity: float
    size_in_tokens: int
    type: str
    task_id: str

@dataclass
class Agent:
    name: str

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
            },
            # Add more decision matrix entries as needed
        }

        for task_type, task_config in decision_matrix.items():
            if all(condition for condition in task_config["conditions"]):
                return Agent(task_config["agent"])

        # Default agent if no conditions are met
        return Agent("default_agent")

class Metrics:
    def __init__(self):
        self.metrics = {}

    def export_json(self, metrics_json):
        import json
        with open(metrics_json, 'w') as f:
            json.dump(self.metrics, f)

    def export_csv(self, metrics_csv):
        import csv
        with open(metrics_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Metric", "Value"])
            for metric, value in self.metrics.items():
                writer.writerow([metric, value])

    def print_summary(self):
        for metric, value in self.metrics.items():
            print(f"{metric}: {value}")

    def update_metrics(self, task_id, metrics):
        self.metrics[task_id] = metrics

class Orchestrator:
    def __init__(self):
        self.metrics = Metrics()

    def _save_step_outputs(self, output_dir, plan, results):
        metrics_json = os.path.join(output_dir, f"metrics_{plan.task_id}.json")
        metrics_csv = os.path.join(output_dir, f"metrics_{plan.task_id}.csv")
        self.metrics.export_json(metrics_json)
        self.metrics.export_csv(metrics_csv)

    def run(self, task: Task):
        agent_router = AgentRouter()
        selected_agent = agent_router.select_agent(task)
        print(f"Selected agent: {selected_agent.name}")

        # Run the task with the selected agent
        # ...

        # Update metrics
        metrics = {"accuracy": 0.9, "f1_score": 0.8}  # Replace with actual metrics
        self.metrics.update_metrics(task.task_id, metrics)

        # Save step outputs
        output_dir = "output"
        plan = type('Plan', (), {'task_id': task.task_id})
        results = type('Results', (), {'metrics': metrics})
        self._save_step_outputs(output_dir, plan, results)

        # Print summary
        self.metrics.print_summary()

        # Return results
        plan_metrics = self.metrics.metrics
        return plan_metrics

# Example usage:
task = Task(complexity=0.8, size_in_tokens=600, type="module_creation", task_id="task_1")
orchestrator = Orchestrator()
results = orchestrator.run(task)
print(results)