"""Plan panel widget for TUI."""
from pathlib import Path
from textual.widgets import Static
from ...models.plan_reader import PlanReader


class PlanPanel(Static):
    """Panel displaying plan information and steps."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plan = None
        self.steps_status = {}
    
    def set_plan(self, plan_path: Path):
        """Load and display plan."""
        try:
            from ...models.plan_reader import PlanReader
            reader = PlanReader()
            self.plan = reader.read(plan_path)
            self.update_plan_display()
        except Exception as e:
            self.update(f"[red]Error loading plan: {e}[/]")
    
    def update_plan_display(self):
        """Update plan display."""
        if not self.plan:
            return
        
        content = f"[bold cyan]📋 Plan: {self.plan.task_id}[/bold cyan]\n\n"
        content += f"{self.plan.description}\n\n"
        content += f"[yellow]Steps: {len(self.plan.steps)}[/yellow]\n\n"
        
        for step in self.plan.steps:
            status = self.steps_status.get(step.id, "⏳")
            content += f"{status} {step.id}: {step.description[:50]}...\n"
        
        self.update(content)
    
    def update_step_status(self, step_id: str, status: str):
        """Update status of a step."""
        self.steps_status[step_id] = status
        self.update_plan_display()
