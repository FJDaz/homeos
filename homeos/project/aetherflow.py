homeos/project/
├── __init__.py
├── aetherflow.py
├── models.py
├── services.py
└── tests/
    ├── __init__.py
    ├── test_aetherflow.py
    └── test_models.py

homeos/
├── project/
│   ├── __init__.py
│   ├── aetherflow.py
│   └── tests/
│       └── test_aetherflow.py
├── models/
│   ├── __init__.py
│   ├── task.py
│   ├── agent.py
│   └── configuration.py
├── services/
│   ├── __init__.py
│   ├── agent_router.py
│   └── metrics_service.py
└── backend/
    └── prod/
        ├── __init__.py
        └── orchestrator.py

from typing import Dict, Optional
import os
import json
import csv

class Task:
    def __init__(self, complexity: float, size_in_tokens: int, task_type: str):
        self.complexity = complexity
        self.size_in_tokens = size_in_tokens
        self.type = task_type

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

        for task_type, task_config in decision_matrix.items():
            if all(condition for condition in task_config["conditions"]):
                return Agent(task_config["agent"])

        return Agent("default_agent")

class ModeConfiguration:
    def __init__(self, config: Dict):
        self.config = config

class Metrics:
    def __init__(self):
        self.metrics = {}

    def export_json(self, output_file: str):
        with open(output_file, "w") as f:
            json.dump(self.metrics, f)

    def export_csv(self, output_file: str):
        with open(output_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Metric", "Value"])
            for metric, value in self.metrics.items():
                writer.writerow([metric, value])

    def print_summary(self):
        for metric, value in self.metrics.items():
            print(f"{metric}: {value}")

    def update_metrics(self, metrics: Dict):
        self.metrics.update(metrics)

class Orchestrator:
    def __init__(self):
        self.metrics = Metrics()

    def _save_step_outputs(self, output_dir: str, plan: str, results: Dict):
        # Export metrics
        metrics_json = os.path.join(output_dir, f"metrics_{plan}.json")
        metrics_csv = os.path.join(output_dir, f"metrics_{plan}.csv")
        self.metrics.export_json(metrics_json)
        self.metrics.export_csv(metrics_csv)

    def execute_plan(self, plan_path: str, output_dir: Optional[str] = None, context: Optional[Dict] = None, **kwargs):
        # Read plan from file
        with open(plan_path, "r") as f:
            plan = json.load(f)

        # Initialize metrics
        self.metrics = Metrics()

        # Execute plan
        results = {}
        for step in plan["steps"]:
            # Execute step
            # For demonstration purposes, assume step execution returns a dictionary
            step_results = {"step": step["name"], "result": "success"}
            results[step["name"]] = step_results

            # Update metrics
            self.metrics.update_metrics(step_results)

        # Save step outputs
        if output_dir:
            self._save_step_outputs(output_dir, plan["task_id"], results)

        # Print summary
        self.metrics.print_summary()

        # Return results
        return results

class ProjectAetherflow:
    def __init__(self, config: ModeConfiguration):
        self.config = config
        self.orchestrator = Orchestrator()

    def execute_plan(self, plan_path: str, output_dir: Optional[str] = None, context: Optional[Dict] = None, **kwargs):
        return self.orchestrator.execute_plan(plan_path, output_dir, context, **kwargs)

# Example usage:
if __name__ == "__main__":
    # Create a task
    task = Task(0.8, 1000, "module_creation")

    # Create an agent router
    agent_router = AgentRouter()

    # Select an agent for the task
    agent = agent_router.select_agent(task)
    print(f"Selected agent: {agent.name}")

    # Create a project Aetherflow instance
    config = ModeConfiguration({"mode": "PROJECT"})
    project_aetherflow = ProjectAetherflow(config)

    # Execute a plan
    plan_path = "path_to_plan.json"
    output_dir = "path_to_output_dir"
    results = project_aetherflow.execute_plan(plan_path, output_dir)

    print("Execution results:")
    print(results)