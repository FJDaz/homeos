"""Real-time execution monitoring for AETHERFLOW."""
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from rich.console import Console, Group
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TaskID
from rich import box
from loguru import logger
import sys


class StepStatus(Enum):
    """Status of a step execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StepMonitor:
    """Monitor data for a single step."""
    step_id: str
    step_description: str
    step_type: str
    complexity: float
    status: StepStatus = StepStatus.PENDING
    provider: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    execution_time_ms: float = 0.0
    tokens_used: int = 0
    cost_usd: float = 0.0
    error: Optional[str] = None
    progress_message: str = ""


class ExecutionMonitor:
    """Real-time monitor for plan execution."""
    
    def __init__(self, plan_description: str, total_steps: int):
        """
        Initialize execution monitor.
        
        Args:
            plan_description: Description of the plan being executed
            total_steps: Total number of steps in the plan
        """
        self.plan_description = plan_description
        self.total_steps = total_steps
        # Force console to always render, even when piped
        self.console = Console(force_terminal=True, width=120)
        self.steps: Dict[str, StepMonitor] = {}
        self.current_step_id: Optional[str] = None
        self.completed_steps = 0
        self.failed_steps = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.start_time = datetime.now()
        self.live: Optional[Live] = None
        
    def add_step(self, step_id: str, description: str, step_type: str, complexity: float) -> None:
        """Add a step to monitor."""
        self.steps[step_id] = StepMonitor(
            step_id=step_id,
            step_description=description,
            step_type=step_type,
            complexity=complexity
        )
    
    def start_step(self, step_id: str, provider: str) -> None:
        """Mark a step as started."""
        if step_id in self.steps:
            self.steps[step_id].status = StepStatus.RUNNING
            self.steps[step_id].start_time = datetime.now()
            self.steps[step_id].provider = provider
            self.current_step_id = step_id
            self._update_display()
    
    def update_step_progress(self, step_id: str, message: str) -> None:
        """Update progress message for a step."""
        if step_id in self.steps:
            self.steps[step_id].progress_message = message
            self._update_display()
    
    def complete_step(
        self,
        step_id: str,
        success: bool,
        execution_time_ms: float,
        tokens_used: int,
        cost_usd: float,
        error: Optional[str] = None
    ) -> None:
        """Mark a step as completed."""
        if step_id in self.steps:
            step = self.steps[step_id]
            step.status = StepStatus.COMPLETED if success else StepStatus.FAILED
            step.end_time = datetime.now()
            step.execution_time_ms = execution_time_ms
            step.tokens_used = tokens_used
            step.cost_usd = cost_usd
            step.error = error
            
            if success:
                self.completed_steps += 1
            else:
                self.failed_steps += 1
            
            self.total_tokens += tokens_used
            self.total_cost += cost_usd
            self.current_step_id = None
            self._update_display()
    
    def _update_display(self) -> None:
        """Update the live display."""
        # ALWAYS print updates directly - force visibility!
        self.console.print("\n" + "-"*80)
        self.console.print(self._create_display())
        self.console.print("-"*80 + "\n")
    
    def _create_display(self) -> Panel:
        """Create the monitoring display."""
        # Calculate progress
        total_completed = self.completed_steps + self.failed_steps
        progress_percent = (total_completed / self.total_steps * 100) if self.total_steps > 0 else 0
        
        # Elapsed time
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        # Create main table
        table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
        table.add_column("Step", style="cyan", width=10)
        table.add_column("Type", style="yellow", width=12)
        table.add_column("Provider", style="magenta", width=12)
        table.add_column("Status", width=12)
        table.add_column("Time", style="green", width=10)
        table.add_column("Tokens", style="blue", width=10)
        table.add_column("Cost", style="yellow", width=10)
        table.add_column("Description", style="white", width=40)
        
        # Add step rows
        for step_id, step in self.steps.items():
            # Status indicator
            if step.status == StepStatus.COMPLETED:
                status = "[green]✓ Completed[/]"
            elif step.status == StepStatus.RUNNING:
                status = "[cyan]⟳ Running[/]"
            elif step.status == StepStatus.FAILED:
                status = "[red]✗ Failed[/]"
            else:
                status = "[dim]○ Pending[/]"
            
            # Time display
            if step.execution_time_ms > 0:
                time_str = f"{step.execution_time_ms/1000:.1f}s"
            elif step.status == StepStatus.RUNNING and step.start_time:
                running_time = (datetime.now() - step.start_time).total_seconds()
                time_str = f"[cyan]{running_time:.1f}s[/]"
            else:
                time_str = "-"
            
            # Provider display
            provider_str = step.provider or "-"
            
            # Tokens and cost
            tokens_str = f"{step.tokens_used:,}" if step.tokens_used > 0 else "-"
            cost_str = f"${step.cost_usd:.4f}" if step.cost_usd > 0 else "-"
            
            # Description (truncated)
            desc = step.step_description[:37] + "..." if len(step.step_description) > 40 else step.step_description
            
            table.add_row(
                step_id,
                step.step_type,
                provider_str,
                status,
                time_str,
                tokens_str,
                cost_str,
                desc
            )
        
        # Create summary panel
        summary_text = (
            f"[bold]Plan:[/] {self.plan_description[:60]}...\n"
            f"[bold]Progress:[/] {total_completed}/{self.total_steps} steps ({progress_percent:.1f}%)\n"
            f"[bold]Completed:[/] [green]{self.completed_steps}[/] | "
            f"[bold]Failed:[/] [red]{self.failed_steps}[/]\n"
            f"[bold]Elapsed Time:[/] {elapsed:.1f}s\n"
            f"[bold]Total Tokens:[/] {self.total_tokens:,}\n"
            f"[bold]Total Cost:[/] ${self.total_cost:.4f}"
        )
        
        summary_panel = Panel(summary_text, title="[bold cyan]Execution Summary[/]", border_style="cyan")
        
        # Combine as Rich renderables (not f-string, else Panel/Table become repr strings)
        content = Group(summary_panel, table)
        
        return Panel(content, title="[bold cyan]AETHERFLOW Execution Monitor[/]", border_style="cyan")
    
    def start_monitoring(self) -> None:
        """Start the live monitoring display."""
        # ALWAYS print initial display - force it!
        self.console.print("\n" + "="*80)
        self.console.print(self._create_display())
        self.console.print("="*80 + "\n")
        
        # Don't use Live - always print directly for maximum visibility
        self.live = None
    
    def stop_monitoring(self) -> None:
        """Stop the live monitoring display."""
        if self.live:
            try:
                self.live.stop()
            except Exception:
                pass
            self.live = None
        # ALWAYS print final state - force it!
        self.console.print("\n" + "="*80)
        self.console.print(self._create_display())
        self.console.print("="*80 + "\n")
    
    def print_final_summary(self) -> None:
        """Print final execution summary."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        summary_table = Table(title="[bold green]Execution Complete[/]", box=box.ROUNDED)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")
        
        summary_table.add_row("Total Steps", str(self.total_steps))
        summary_table.add_row("Completed", f"[green]{self.completed_steps}[/]")
        summary_table.add_row("Failed", f"[red]{self.failed_steps}[/]")
        summary_table.add_row("Success Rate", f"{(self.completed_steps/self.total_steps*100):.1f}%" if self.total_steps > 0 else "0%")
        summary_table.add_row("Total Time", f"{elapsed:.2f}s")
        summary_table.add_row("Total Tokens", f"{self.total_tokens:,}")
        summary_table.add_row("Total Cost", f"${self.total_cost:.4f}")
        
        self.console.print(summary_table)
