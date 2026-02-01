"""Main TUI application for AetherFlow."""
import asyncio
import re
from pathlib import Path
from typing import Optional
from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Button, Input, Select
from textual.binding import Binding
from loguru import logger

from ..workflows.proto import ProtoWorkflow
from ..workflows.prod import ProdWorkflow
from .widgets.plan_panel import PlanPanel
from .widgets.console_panel import ConsolePanel
from .widgets.metrics_panel import MetricsPanel
from .widgets.mentor_panel import MentorPanel


class AetherFlowTUI(App):
    """Main TUI application for AetherFlow."""
    
    CSS = """
    Screen {
        background: $surface;
    }

    #plan-panel {
        width: 30%;
        border: solid $primary;
        padding: 1;
    }

    #console-panel {
        width: 40%;
        border: solid $primary;
        padding: 1;
    }

    #metrics-panel {
        width: 30%;
        border: solid $primary;
        padding: 1;
    }

    #controls {
        height: 5;
        border: solid $primary;
        padding: 1;
    }

    #prompt-area {
        height: auto;
        border: solid $accent;
        padding: 1;
        margin-top: 1;
    }

    #prompt-area.hidden {
        display: none;
    }

    #prompt-input {
        width: 100%;
        margin-bottom: 1;
    }

    #prompt-mode-select {
        width: 20;
        margin-left: 1;
    }

    #mode-label {
        width: auto;
        padding-top: 1;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("f1", "help", "Help"),
        Binding("s", "start", "Start Workflow"),
    ]
    
    def __init__(self):
        super().__init__()
        self.plan_path: Optional[Path] = None
        self.workflow_type: str = "PROTO"
        self.mentor_mode: bool = False
        self._workflow_running: bool = False
        self.prompt_mode: bool = False
        self.prompt_execution_mode: str = "FAST"
        self.last_generated_code: Optional[str] = None
        self.last_generated_prompt: Optional[str] = None
    
    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header(show_clock=True)
        
        with Horizontal():
            yield PlanPanel(id="plan-panel")
            yield ConsolePanel(id="console-panel")
            yield MetricsPanel(id="metrics-panel")
        
        with Horizontal(id="controls"):
            yield Button("Select Plan", id="select-plan")
            yield Select(
                [("PROTO", "PROTO"), ("PROD", "PROD")],
                value="PROTO",
                id="workflow-select"
            )
            yield Button("Mentor Mode", id="mentor-toggle", variant="default")
            yield Button("Quick Generate", id="quick-gen-btn", variant="primary")
            yield Button("Save Code", id="save-code-btn", variant="warning", disabled=True)
            yield Button("Start", id="start-btn", variant="success")
            yield Button("Stop", id="stop-btn", variant="error", disabled=True)
        
        # Prompt input area (initially hidden)
        with Vertical(id="prompt-area", classes="hidden"):
            yield Static("[bold cyan]💬 Quick Generate - Enter your prompt:[/bold cyan]", id="prompt-label")
            yield Input(
                placeholder="e.g., Crée une fonction Python qui valide un email",
                id="prompt-input",
                classes="prompt-input"
            )
            with Horizontal():
                yield Static("Mode:", id="mode-label")
                yield Select(
                    [("FAST", "FAST"), ("BUILD", "BUILD"), ("DOUBLE-CHECK", "DOUBLE-CHECK")],
                    value="FAST",
                    id="prompt-mode-select"
                )
            with Horizontal():
                yield Button("Generate", id="generate-btn", variant="success")
                yield Button("Cancel", id="cancel-prompt-btn", variant="default")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when app is mounted."""
        self.title = "🚀 AetherFlow TUI"
        self.sub_title = "Terminal User Interface"
        
        # Update mentor button if mentor mode is enabled
        if self.mentor_mode:
            mentor_btn = self.query_one("#mentor-toggle", Button)
            mentor_btn.label = "Mentor: ON"
            mentor_btn.variant = "success"
        
        # Load plan if set before mount
        if self.plan_path:
            plan_panel = self.query_one("#plan-panel", PlanPanel)
            plan_panel.set_plan(self.plan_path)
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "select-plan":
            await self.action_select_plan()
        elif event.button.id == "start-btn":
            await self.action_start()
        elif event.button.id == "stop-btn":
            await self.action_stop()
        elif event.button.id == "mentor-toggle":
            self.mentor_mode = not self.mentor_mode
            event.button.label = "Mentor: ON" if self.mentor_mode else "Mentor Mode"
            event.button.variant = "success" if self.mentor_mode else "default"
        elif event.button.id == "quick-gen-btn":
            await self.action_show_prompt()
        elif event.button.id == "generate-btn":
            await self.action_generate_code()
        elif event.button.id == "cancel-prompt-btn":
            await self.action_hide_prompt()
        elif event.button.id == "save-code-btn":
            await self.action_save_code()
    
    async def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select changes."""
        if event.select.id == "workflow-select":
            self.workflow_type = event.value
        elif event.select.id == "prompt-mode-select":
            self.prompt_execution_mode = event.value
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission (Enter key)."""
        if event.input.id == "prompt-input":
            await self.action_generate_code()
    
    async def action_select_plan(self) -> None:
        """Select plan file."""
        # Simple file selection (can be improved with FilePicker)
        plan_panel = self.query_one("#plan-panel", PlanPanel)
        plan_panel.update("[yellow]Use --plan argument or set plan_path in code[/yellow]")
    
    async def action_start(self) -> None:
        """Start workflow execution."""
        if not self.plan_path:
            console_panel = self.query_one("#console-panel", ConsolePanel)
            console_panel.add_log("❌ No plan selected", "error")
            return
        
        if self._workflow_running:
            console_panel = self.query_one("#console-panel", ConsolePanel)
            console_panel.add_log("⚠️ Workflow already running", "error")
            return
        
        self._workflow_running = True
        start_btn = self.query_one("#start-btn", Button)
        stop_btn = self.query_one("#stop-btn", Button)
        start_btn.disabled = True
        stop_btn.disabled = False
        
        console_panel = self.query_one("#console-panel", ConsolePanel)
        console_panel.add_log(f"🚀 Starting {self.workflow_type} workflow...", "info")
        
        # Run workflow in background
        asyncio.create_task(self.run_workflow())
    
    async def action_stop(self) -> None:
        """Stop workflow execution."""
        self._workflow_running = False
        console_panel = self.query_one("#console-panel", ConsolePanel)
        console_panel.add_log("⏹️ Stopping workflow...", "info")
    
    async def action_show_prompt(self) -> None:
        """Show prompt input area."""
        prompt_area = self.query_one("#prompt-area", Vertical)
        prompt_area.remove_class("hidden")
        self.prompt_mode = True
        # Focus the input after a short delay to ensure rendering
        self.set_timer(0.1, self._focus_prompt_input)

    def _focus_prompt_input(self) -> None:
        """Focus the prompt input field."""
        try:
            prompt_input = self.query_one("#prompt-input", Input)
            prompt_input.focus()
        except Exception:
            pass
    
    async def action_hide_prompt(self) -> None:
        """Hide prompt input area."""
        prompt_area = self.query_one("#prompt-area", Vertical)
        prompt_area.add_class("hidden")
        prompt_input = self.query_one("#prompt-input", Input)
        prompt_input.value = ""
        self.prompt_mode = False
    
    def _detect_language(self, code: str) -> tuple[str, str]:
        """Detect programming language from code and return (language, extension)."""
        LANGUAGE_PATTERNS = {
            'python': re.compile(r'^\s*(def\s+|class\s+|import\s+|from\s+|print\s*\(|if\s+__name__\s*==)'),
            'javascript': re.compile(r'^\s*(function\s+|const\s+|let\s+|var\s+|console\.log|=>)'),
            'typescript': re.compile(r'^\s*(function\s+|const\s+|let\s+|var\s+|interface\s+|type\s+)'),
            'java': re.compile(r'^\s*(public\s+class|private\s+|protected\s+|System\.out\.print)'),
            'html': re.compile(r'^\s*(<!DOCTYPE|<html|<head|<body|<div\s+)'),
            'css': re.compile(r'^\s*(\.[\w-]+\s*{|#[\w-]+\s*{|@media)'),
            'sql': re.compile(r'^\s*(SELECT\s+|INSERT\s+|UPDATE\s+|CREATE\s+TABLE)'),
        }
        
        LANGUAGE_EXTENSIONS = {
            'python': 'py',
            'javascript': 'js',
            'typescript': 'ts',
            'java': 'java',
            'html': 'html',
            'css': 'css',
            'sql': 'sql',
            'rust': 'rs',
            'go': 'go',
            'bash': 'sh',
            'json': 'json',
            'yaml': 'yaml',
            'markdown': 'md',
        }
        
        lines = code.strip().split('\n')
        matches = {}
        for line in lines[:20]:
            for lang, pattern in LANGUAGE_PATTERNS.items():
                if pattern.search(line):
                    matches[lang] = matches.get(lang, 0) + 1
        
        if not matches:
            return ('python', 'py')
        
        best_language = max(matches.items(), key=lambda x: x[1])[0]
        extension = LANGUAGE_EXTENSIONS.get(best_language, 'txt')
        return (best_language, extension)
    
    def _sanitize_filename(self, filename: str, max_length: int = 50) -> str:
        """Sanitize a string to make it a valid filename."""
        sanitized = filename.strip().replace(' ', '_')
        sanitized = re.sub(r'[^\w\.\-_]', '_', sanitized)
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        return sanitized
    
    def _generate_default_filename(self, prompt: str, extension: str) -> str:
        """Generate a default filename based on prompt and extension."""
        sanitized_prompt = self._sanitize_filename(prompt)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{sanitized_prompt}_{timestamp}.{extension}"
        output_dir = Path("output/tui_quick_generate")
        output_dir.mkdir(parents=True, exist_ok=True)
        return str(output_dir / filename)
    
    async def action_save_code(self) -> None:
        """Save generated code to file."""
        if not self.last_generated_code:
            console_panel = self.query_one("#console-panel", ConsolePanel)
            console_panel.add_log("❌ No code to save", "error")
            return
        
        try:
            # Detect language and extension
            language, extension = self._detect_language(self.last_generated_code)
            
            # Generate default filename
            default_path = self._generate_default_filename(
                self.last_generated_prompt or "generated_code",
                extension
            )
            
            # Save code
            filepath = Path(default_path)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.last_generated_code)
            
            console_panel = self.query_one("#console-panel", ConsolePanel)
            console_panel.add_log(f"💾 Code saved to: {filepath}", "success")
            console_panel.add_log(f"📁 Language detected: {language} (.{extension})", "info")
            
            # Disable save button after successful save
            save_btn = self.query_one("#save-code-btn", Button)
            save_btn.disabled = True
            
        except Exception as e:
            console_panel = self.query_one("#console-panel", ConsolePanel)
            console_panel.add_log(f"❌ Error saving code: {e}", "error")
            logger.exception("Failed to save code")
    
    async def action_generate_code(self) -> None:
        """Generate code from prompt."""
        try:
            prompt_input = self.query_one("#prompt-input", Input)
            task = prompt_input.value.strip()
        except Exception:
            task = ""
        
        if not task:
            console_panel = self.query_one("#console-panel", ConsolePanel)
            console_panel.add_log("❌ Please enter a prompt", "error")
            return
        
        if self._workflow_running:
            console_panel = self.query_one("#console-panel", ConsolePanel)
            console_panel.add_log("⚠️ Another operation is running", "error")
            return
        
        self._workflow_running = True
        console_panel = self.query_one("#console-panel", ConsolePanel)
        metrics_panel = self.query_one("#metrics-panel", MetricsPanel)
        
        console_panel.add_log(f"🚀 Generating code for: {task[:50]}...", "info")
        
        # Hide prompt area
        await self.action_hide_prompt()
        
        # Run generation in background
        asyncio.create_task(self.run_generate_code(task))
    
    async def run_generate_code(self, task: str) -> None:
        """Run code generation from prompt."""
        try:
            console_panel = self.query_one("#console-panel", ConsolePanel)
            metrics_panel = self.query_one("#metrics-panel", MetricsPanel)
            
            # Import AgentRouter for direct generation
            from ..models.agent_router import AgentRouter
            
            # Initialize router with the selected execution mode
            router = AgentRouter(execution_mode=self.prompt_execution_mode)
            try:
                # Map execution mode to provider (for display)
                mode_to_provider = {
                    "FAST": "groq",  # Ultra-fast
                    "BUILD": "deepseek",  # Balanced quality/speed
                    "DOUBLE-CHECK": "gemini"  # Validation/audit
                }
                provider = mode_to_provider.get(self.prompt_execution_mode, "auto")
                
                console_panel.add_log(f"🤖 Generating code in {self.prompt_execution_mode} mode ({provider})...", "info")
                
                # Generate code directly (router will use execution_mode internally)
                result = await router.generate(
                    task=task,
                    context=None,
                    provider=provider,  # Explicit provider based on mode
                    max_tokens=None,
                    temperature=None
                )
                
                if result.success:
                    # Store generated code for saving
                    self.last_generated_code = result.code
                    self.last_generated_prompt = task
                    
                    console_panel.add_log("✅ Code generated successfully!", "success")
                    console_panel.add_log(f"📋 Provider: {result.provider}", "info")
                    console_panel.add_log(f"💰 Tokens: {result.tokens_used}, Cost: ${result.cost_usd:.4f}", "info")
                    console_panel.add_log("", "info")  # Empty line
                    console_panel.add_log("[bold cyan]Generated Code:[/bold cyan]", "info")
                    # Display code with proper formatting
                    code_lines = result.code.split('\n')
                    for line in code_lines[:50]:  # Show first 50 lines
                        console_panel.add_log(f"  {line}", "info")
                    if len(code_lines) > 50:
                        console_panel.add_log(f"  ... ({len(code_lines) - 50} more lines)", "info")
                    
                    # Enable Save Code button
                    save_btn = self.query_one("#save-code-btn", Button)
                    save_btn.disabled = False
                    
                    # Update metrics
                    metrics_panel.update_metrics(
                        total_cost=f"${result.cost_usd:.4f}",
                        tokens_used=result.tokens_used
                    )
                else:
                    console_panel.add_log(f"❌ Generation failed: {result.error}", "error")
            finally:
                await router.close()
            
        except Exception as e:
            console_panel = self.query_one("#console-panel", ConsolePanel)
            console_panel.add_log(f"❌ Error: {e}", "error")
            logger.exception("Code generation failed")
        finally:
            self._workflow_running = False
            start_btn = self.query_one("#start-btn", Button)
            stop_btn = self.query_one("#stop-btn", Button)
            start_btn.disabled = False
            stop_btn.disabled = True
    
    async def run_workflow(self) -> None:
        """Run the selected workflow."""
        try:
            plan_panel = self.query_one("#plan-panel", PlanPanel)
            console_panel = self.query_one("#console-panel", ConsolePanel)
            metrics_panel = self.query_one("#metrics-panel", MetricsPanel)
            mentor_panel = None
            
            # Load plan
            plan_panel.set_plan(self.plan_path)
            console_panel.add_log(f"📋 Plan loaded: {self.plan_path.name}", "info")
            
            # Execute workflow
            if self.workflow_type == "PROTO":
                workflow = ProtoWorkflow()
            else:
                workflow = ProdWorkflow()
            
            output_dir = Path("output/tui_execution")
            result = await workflow.execute(
                plan_path=self.plan_path,
                output_dir=output_dir,
                context=None
            )
            
            # Update metrics
            total_time = result.get("total_time_ms", 0) / 1000
            total_cost = result.get("total_cost_usd", 0.0)
            metrics_panel.update_metrics(
                total_time=f"{total_time:.2f}s",
                total_cost=f"${total_cost:.4f}"
            )
            
            # Display mentor feedback if enabled
            if self.mentor_mode and "validation" in result:
                validation_details = result["validation"].get("validation_details", [])
                if validation_details:
                    console_panel.add_log("🎓 Displaying mentor feedback...", "info")
                    # Extract first feedback
                    for detail in validation_details:
                        pf = detail.get("pedagogical_feedback")
                        if pf:
                            # Update metrics panel to show feedback summary
                            violations_count = len(pf.get("violations", []))
                            passed_count = len(pf.get("passed_rules", []))
                            console_panel.add_log(
                                f"📊 Feedback: {passed_count} rules passed, {violations_count} violations",
                                "info"
                            )
                            break
            
            console_panel.add_log("✅ Workflow completed successfully!", "success")
            
        except Exception as e:
            console_panel = self.query_one("#console-panel", ConsolePanel)
            console_panel.add_log(f"❌ Error: {e}", "error")
            logger.exception("Workflow execution failed")
        finally:
            self._workflow_running = False
            start_btn = self.query_one("#start-btn", Button)
            stop_btn = self.query_one("#stop-btn", Button)
            start_btn.disabled = False
            stop_btn.disabled = True
    
    def set_plan_path(self, plan_path: Path):
        """Set plan path from CLI argument."""
        self.plan_path = plan_path
        # Update plan panel if app is already mounted
        try:
            plan_panel = self.query_one("#plan-panel", PlanPanel)
            plan_panel.set_plan(plan_path)
        except Exception:
            # App not mounted yet, will be set in on_mount
            pass


def run_tui(plan_path: Optional[Path] = None, mentor: bool = False):
    """Run TUI application."""
    app = AetherFlowTUI()
    if plan_path:
        app.set_plan_path(plan_path)
    if mentor:
        app.mentor_mode = True
        # Button will be updated in on_mount()
    app.run()
