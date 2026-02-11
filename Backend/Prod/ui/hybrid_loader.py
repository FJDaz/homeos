"""Hybrid loading UI for Aetherflow multi-phase workflow.

Displays real-time progress for FAST → BUILD → DOUBLE-CHECK phases.
"""
import sys
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class Phase(Enum):
    """Workflow phases."""
    FAST = "FAST"
    BUILD = "BUILD"
    DOUBLE_CHECK = "DOUBLE-CHECK"


class StepStatus(Enum):
    """Step execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# ANSI Colors
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    DIM = '\033[2m'


@dataclass
class PhaseProgress:
    """Progress tracker for a phase."""
    phase: Phase
    current_step: int
    total_steps: int
    provider: str
    tokens_used: int = 0
    cost_usd: float = 0.0
    elapsed_seconds: float = 0.0
    status: StepStatus = StepStatus.RUNNING


@dataclass
class StepInfo:
    """Information about a step."""
    step_id: str
    description: str
    status: StepStatus
    provider: str = "-"
    tokens: int = 0
    cost: float = 0.0
    time_ms: float = 0.0


class HybridLoader:
    """
    Interactive dashboard for hybrid workflow progress.

    Displays:
    - Current phase with progress bar
    - Step-by-step status
    - Live metrics (tokens, cost, time)
    - Provider routing decisions
    """

    def __init__(self, total_steps: int, enable_animations: bool = True):
        """
        Initialize hybrid loader.

        Args:
            total_steps: Total number of steps in the plan
            enable_animations: Enable spinner animations
        """
        self.total_steps = total_steps
        self.enable_animations = enable_animations

        # Phase tracking
        self.current_phase: Optional[Phase] = None
        self.phase_progress: Dict[Phase, PhaseProgress] = {}

        # Step tracking
        self.steps: Dict[str, StepInfo] = {}
        self.step_order: List[str] = []

        # Overall metrics
        self.total_tokens = 0
        self.total_cost = 0.0
        self.start_time = time.time()

        # Spinner for animations
        self.spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.spinner_index = 0

    def start_phase(self, phase: Phase, provider: str) -> None:
        """Start a new phase."""
        self.current_phase = phase
        self.phase_progress[phase] = PhaseProgress(
            phase=phase,
            current_step=0,
            total_steps=self.total_steps,
            provider=provider,
            status=StepStatus.RUNNING
        )
        self._render()

    def update_step(
        self,
        step_id: str,
        description: str,
        status: StepStatus,
        provider: str = "-",
        tokens: int = 0,
        cost: float = 0.0,
        time_ms: float = 0.0
    ) -> None:
        """Update step progress."""
        if step_id not in self.steps:
            self.step_order.append(step_id)

        self.steps[step_id] = StepInfo(
            step_id=step_id,
            description=description,
            status=status,
            provider=provider,
            tokens=tokens,
            cost=cost,
            time_ms=time_ms
        )

        # Update phase progress
        if self.current_phase and self.current_phase in self.phase_progress:
            progress = self.phase_progress[self.current_phase]
            if status == StepStatus.COMPLETED:
                progress.current_step += 1
            progress.tokens_used += tokens
            progress.cost_usd += cost
            progress.elapsed_seconds = time.time() - self.start_time

        # Update totals
        self.total_tokens += tokens
        self.total_cost += cost

        self._render()

    def complete_phase(self, phase: Phase) -> None:
        """Mark phase as completed."""
        if phase in self.phase_progress:
            self.phase_progress[phase].status = StepStatus.COMPLETED
        self._render()

    def _get_spinner(self) -> str:
        """Get next spinner character."""
        if not self.enable_animations:
            return "⟳"
        char = self.spinner_chars[self.spinner_index]
        self.spinner_index = (self.spinner_index + 1) % len(self.spinner_chars)
        return char

    def _draw_progress_bar(self, current: int, total: int, width: int = 30) -> str:
        """Draw a progress bar."""
        if total == 0:
            filled = 0
            percentage = 0
        else:
            filled = int(width * current / total)
            percentage = int(100 * current / total)

        bar = '█' * filled + '░' * (width - filled)

        if percentage == 100:
            color = Colors.OKGREEN
        elif percentage >= 50:
            color = Colors.OKCYAN
        else:
            color = Colors.WARNING

        return f"{color}[{bar}] {percentage}%{Colors.ENDC}"

    def _render_phase_indicator(self) -> str:
        """Render phase indicator line."""
        lines = []

        # Header
        lines.append(f"\n{Colors.HEADER}{Colors.BOLD}╔══════════════════════════════════════════════════════════════════╗{Colors.ENDC}")
        lines.append(f"{Colors.HEADER}{Colors.BOLD}║   AETHERFLOW - Hybrid Workflow Progress                         ║{Colors.ENDC}")
        lines.append(f"{Colors.HEADER}{Colors.BOLD}╚══════════════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        # Phases status
        phase_icons = {
            Phase.FAST: "🚀",
            Phase.BUILD: "🔧",
            Phase.DOUBLE_CHECK: "✅"
        }

        phase_line = "  "
        for phase in Phase:
            if phase in self.phase_progress:
                progress = self.phase_progress[phase]
                icon = phase_icons[phase]

                if progress.status == StepStatus.COMPLETED:
                    phase_line += f"{Colors.OKGREEN}{icon} {phase.value} ✓{Colors.ENDC}  →  "
                elif phase == self.current_phase:
                    spinner = self._get_spinner()
                    phase_line += f"{Colors.OKCYAN}{icon} {phase.value} {spinner}{Colors.ENDC}  →  "
                else:
                    phase_line += f"{Colors.DIM}{icon} {phase.value}{Colors.ENDC}  →  "
            else:
                icon = phase_icons[phase]
                phase_line += f"{Colors.DIM}{icon} {phase.value}{Colors.ENDC}  →  "

        phase_line = phase_line.rstrip("  →  ")
        lines.append(phase_line)
        lines.append("")

        return "\n".join(lines)

    def _render_current_phase(self) -> str:
        """Render current phase details."""
        if not self.current_phase or self.current_phase not in self.phase_progress:
            return ""

        progress = self.phase_progress[self.current_phase]
        lines = []

        # Phase header
        phase_name = self.current_phase.value
        lines.append(f"{Colors.BOLD}📊 Phase: {phase_name}{Colors.ENDC}")
        lines.append(f"{Colors.DIM}Provider: {progress.provider}{Colors.ENDC}")

        # Progress bar
        bar = self._draw_progress_bar(progress.current_step, progress.total_steps, width=40)
        lines.append(f"Progress: {bar} ({progress.current_step}/{progress.total_steps} steps)")

        # Metrics
        elapsed = progress.elapsed_seconds
        lines.append(
            f"{Colors.DIM}Tokens: {progress.tokens_used:,} | "
            f"Cost: ${progress.cost_usd:.4f} | "
            f"Time: {elapsed:.1f}s{Colors.ENDC}"
        )
        lines.append("")

        return "\n".join(lines)

    def _render_steps(self) -> str:
        """Render step status table."""
        lines = []

        lines.append(f"{Colors.BOLD}Steps:{Colors.ENDC}")
        lines.append(f"{Colors.DIM}{'─' * 70}{Colors.ENDC}")

        for step_id in self.step_order[-5:]:  # Show last 5 steps
            step = self.steps[step_id]

            # Status icon
            if step.status == StepStatus.COMPLETED:
                status_icon = f"{Colors.OKGREEN}✓{Colors.ENDC}"
            elif step.status == StepStatus.RUNNING:
                status_icon = f"{Colors.OKCYAN}{self._get_spinner()}{Colors.ENDC}"
            elif step.status == StepStatus.FAILED:
                status_icon = f"{Colors.FAIL}✗{Colors.ENDC}"
            else:
                status_icon = f"{Colors.DIM}○{Colors.ENDC}"

            # Step line
            desc = step.description[:40] + "..." if len(step.description) > 40 else step.description
            provider_str = f"{Colors.DIM}{step.provider:8s}{Colors.ENDC}"

            if step.status == StepStatus.COMPLETED:
                time_str = f"{step.time_ms/1000:.1f}s"
                cost_str = f"${step.cost:.4f}" if step.cost > 0 else "-"
                tokens_str = f"{step.tokens:,}" if step.tokens > 0 else "-"
                lines.append(
                    f"  {status_icon} {step_id:8s} {provider_str} {desc:43s} "
                    f"{Colors.DIM}{time_str:6s} {tokens_str:8s} {cost_str}{Colors.ENDC}"
                )
            else:
                lines.append(f"  {status_icon} {step_id:8s} {provider_str} {desc}")

        lines.append("")
        return "\n".join(lines)

    def _render_summary(self) -> str:
        """Render overall summary."""
        elapsed = time.time() - self.start_time

        completed = sum(1 for s in self.steps.values() if s.status == StepStatus.COMPLETED)
        total = len(self.steps)

        lines = []
        lines.append(f"{Colors.BOLD}Overall Progress:{Colors.ENDC}")
        lines.append(
            f"{Colors.DIM}Steps: {completed}/{total} | "
            f"Tokens: {self.total_tokens:,} | "
            f"Cost: ${self.total_cost:.4f} | "
            f"Time: {elapsed:.1f}s{Colors.ENDC}"
        )

        return "\n".join(lines)

    def _render(self) -> None:
        """Render full dashboard."""
        # Clear screen (move cursor up)
        if hasattr(self, '_last_render_lines'):
            sys.stdout.write(f"\033[{self._last_render_lines}A")
            sys.stdout.write("\033[J")  # Clear from cursor to end

        # Build output
        output = []
        output.append(self._render_phase_indicator())
        output.append(self._render_current_phase())
        output.append(self._render_steps())
        output.append(self._render_summary())

        full_output = "\n".join(output)

        # Print
        print(full_output, flush=True)

        # Track lines for next clear
        self._last_render_lines = full_output.count('\n') + 1

    def finish(self, success: bool = True) -> None:
        """Finish loading and show final summary."""
        # Final render
        self._render()

        # Success/failure banner
        if success:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ Workflow completed successfully!{Colors.ENDC}\n")
        else:
            print(f"\n{Colors.FAIL}{Colors.BOLD}❌ Workflow failed.{Colors.ENDC}\n")


# Example usage
if __name__ == "__main__":
    import random

    loader = HybridLoader(total_steps=6)

    # Simulate FAST phase
    loader.start_phase(Phase.FAST, "Groq")
    for i in range(1, 4):
        loader.update_step(
            f"step_{i}",
            f"Generate component {i}",
            StepStatus.RUNNING,
            provider="groq"
        )
        time.sleep(0.5)
        loader.update_step(
            f"step_{i}",
            f"Generate component {i}",
            StepStatus.COMPLETED,
            provider="groq",
            tokens=random.randint(1000, 5000),
            cost=random.uniform(0.001, 0.01),
            time_ms=random.uniform(500, 2000)
        )
    loader.complete_phase(Phase.FAST)

    # Simulate BUILD phase
    loader.start_phase(Phase.BUILD, "Gemini")
    for i in range(4, 6):
        loader.update_step(
            f"step_{i}",
            f"Build with surgical editor {i}",
            StepStatus.RUNNING,
            provider="gemini"
        )
        time.sleep(0.5)
        loader.update_step(
            f"step_{i}",
            f"Build with surgical editor {i}",
            StepStatus.COMPLETED,
            provider="gemini",
            tokens=random.randint(5000, 15000),
            cost=random.uniform(0.01, 0.05),
            time_ms=random.uniform(2000, 5000)
        )
    loader.complete_phase(Phase.BUILD)

    # Simulate DOUBLE-CHECK phase
    loader.start_phase(Phase.DOUBLE_CHECK, "DeepSeek")
    loader.update_step(
        "validation",
        "Validate all outputs",
        StepStatus.RUNNING,
        provider="deepseek"
    )
    time.sleep(1)
    loader.update_step(
        "validation",
        "Validate all outputs",
        StepStatus.COMPLETED,
        provider="deepseek",
        tokens=random.randint(10000, 20000),
        cost=random.uniform(0.001, 0.005),
        time_ms=random.uniform(3000, 8000)
    )
    loader.complete_phase(Phase.DOUBLE_CHECK)

    loader.finish(success=True)
