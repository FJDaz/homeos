homeos/
├── __init__.py
├── config/
├── core/
│   ├── __init__.py
│   ├── mode_manager.py
│   └── models.py
├── construction/
│   └── __init__.py
└── project/
    └── __init__.py

import os
import json
import csv
from typing import Dict, List

# Define the Agent and Task classes
class Agent:
    def __init__(self, name: str):
        self.name = name

class Task:
    def __init__(self, complexity: float, size_in_tokens: int, type: str):
        self.complexity = complexity
        self.size_in_tokens = size_in_tokens
        self.type = type

# Define the AgentRouter class
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

        for scenario, config in decision_matrix.items():
            if all(condition for condition in config["conditions"]):
                return Agent(config["agent"])

        # Default agent
        return Agent("default_agent")

# Define the Metrics class
class Metrics:
    def __init__(self):
        self.metrics = {}

    def export_json(self, file_path: str):
        with open(file_path, "w") as f:
            json.dump(self.metrics, f)

    def export_csv(self, file_path: str):
        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Metric", "Value"])
            for metric, value in self.metrics.items():
                writer.writerow([metric, value])

    def print_summary(self):
        print("Metrics Summary:")
        for metric, value in self.metrics.items():
            print(f"{metric}: {value}")

    def update_metrics(self, task_id: str, metrics: Dict[str, float]):
        self.metrics[task_id] = metrics

# Define the Orchestrator class
class Orchestrator:
    def __init__(self):
        self.metrics = Metrics()

    def _save_step_outputs(self, output_dir: str, plan: str, results: List[Dict[str, float]]):
        metrics_json = os.path.join(output_dir, f"metrics_{plan}.json")
        metrics_csv = os.path.join(output_dir, f"metrics_{plan}.csv")
        self.metrics.export_json(metrics_json)
        self.metrics.export_csv(metrics_csv)

    def run(self, task: Task):
        agent = AgentRouter().select_agent(task)
        # Run the task using the selected agent
        # For demonstration purposes, assume the task is completed successfully
        results = [{"metric1": 0.8, "metric2": 0.9}]
        self.metrics.update_metrics("task1", results)
        self._save_step_outputs("output_dir", "plan1", results)