"""Mentor panel widget for TUI."""
from textual.widgets import Static


class MentorPanel(Static):
    """Panel displaying pedagogical feedback."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.feedback = None
    
    def set_feedback(self, feedback_data: dict):
        """Set and display feedback."""
        self.feedback = feedback_data
        self.update_display()
    
    def update_display(self):
        """Update feedback display."""
        if not self.feedback:
            self.update("[dim]No feedback available[/dim]")
            return
        
        content = "[bold cyan]🎓 Feedback Mentor[/bold cyan]\n\n"
        
        if self.feedback.get("is_valid"):
            content += "[green]✅ Validation Passed[/green]\n"
        else:
            content += "[red]❌ Validation Failed[/red]\n"
        
        content += f"Score: {self.feedback.get('score', 0):.1%}\n\n"
        
        passed_rules = self.feedback.get("passed_rules", [])
        if passed_rules:
            content += "[green]✅ Règles passées:[/green]\n"
            for rule in passed_rules:
                content += f"  • {rule}\n"
            content += "\n"
        
        violations = self.feedback.get("violations", [])
        if violations:
            content += f"[red]❌ Violations ({len(violations)}):[/red]\n"
            for v in violations[:5]:  # Show first 5
                content += f"  • {v.get('rule', 'Unknown')} ({v.get('location', 'N/A')})\n"
                if v.get('issue'):
                    content += f"    Issue: {v['issue'][:50]}...\n"
        
        self.update(content)
