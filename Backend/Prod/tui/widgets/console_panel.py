"""Console panel widget for TUI."""
from textual.widgets import Static


class ConsolePanel(Static):
    """Panel displaying logs and outputs in real-time."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logs = []
        self.max_logs = 100
    
    def add_log(self, message: str, level: str = "info"):
        """Add a log message."""
        self.logs.append((level, message))
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)
        self.update_console()
    
    def update_console(self):
        """Update console display."""
        content = "[bold cyan]💻 Console[/bold cyan]\n\n"
        for level, msg in self.logs[-20:]:  # Show last 20 logs
            if level == "error":
                content += f"[red]✗ {msg}[/red]\n"
            elif level == "success":
                content += f"[green]✓ {msg}[/green]\n"
            else:
                content += f"{msg}\n"
        self.update(content)
