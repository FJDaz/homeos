"""Metrics panel widget for TUI."""
from textual.widgets import Static


class MetricsPanel(Static):
    """Panel displaying real-time metrics."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics = {
            "total_time": "0s",
            "total_cost": "$0.0000",
            "cache_hits": 0,
            "cache_misses": 0,
            "tokens_used": 0
        }
    
    def update_metrics(self, **kwargs):
        """Update metrics."""
        self.metrics.update(kwargs)
        self.update_display()
    
    def update_display(self):
        """Update metrics display."""
        content = "[bold cyan]📊 Métriques[/bold cyan]\n\n"
        content += f"Temps: {self.metrics['total_time']}\n"
        content += f"Coût: {self.metrics['total_cost']}\n"
        content += f"Cache Hits: {self.metrics['cache_hits']}\n"
        content += f"Cache Misses: {self.metrics['cache_misses']}\n"
        content += f"Tokens: {self.metrics['tokens_used']:,}\n"
        self.update(content)
