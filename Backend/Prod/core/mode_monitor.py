"""
Mode Monitor for AetherFlow - Tracking usage of AetherFlow modes by Kimi.

This module provides:
- Real-time tracking of mode usage (PROTO, PROD, FRONTEND, DESIGNER, SURGICAL)
- Cost tracking per mode
- Performance metrics per mode
- Usage reports for monitoring work patterns
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
from dataclasses import dataclass, asdict
from loguru import logger


@dataclass
class ModeExecution:
    """Single execution of an AetherFlow mode."""
    timestamp: str
    mode: str  # PROTO, PROD, FRONTEND, DESIGNER, SURGICAL
    action_type: str  # "code_generation", "analysis", "refinement", "chat", "review"
    files_modified: List[str]
    files_created: List[str]
    execution_time_ms: float
    cost_usd: float
    tokens_used: int
    success: bool
    plan_id: Optional[str] = None
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModeExecution':
        """Create from dictionary."""
        return cls(**data)


class ModeMonitor:
    """
    Singleton monitor for AetherFlow mode usage.
    
    Tracks all executions by mode and provides reporting capabilities.
    Data is stored in a JSON file for persistence across sessions.
    """
    
    _instance: Optional['ModeMonitor'] = None
    _storage_path: Path = Path.home() / ".aetherflow" / "mode_tracking.json"
    
    def __new__(cls) -> 'ModeMonitor':
        """Create or return the singleton instance."""
        if cls._instance is None:
            cls._instance = super(ModeMonitor, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """Initialize the monitor."""
        self.executions: List[ModeExecution] = []
        self._load_data()
        logger.info(f"ModeMonitor initialized with {len(self.executions)} executions")
    
    def _load_data(self) -> None:
        """Load existing tracking data from storage."""
        if self._storage_path.exists():
            try:
                with open(self._storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.executions = [
                    ModeExecution.from_dict(e) for e in data.get("executions", [])
                ]
                logger.debug(f"Loaded {len(self.executions)} mode executions")
            except Exception as e:
                logger.warning(f"Could not load mode tracking data: {e}. Starting fresh.")
                self.executions = []
        else:
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            self.executions = []
    
    def _save_data(self) -> None:
        """Save tracking data to storage."""
        try:
            data = {
                "executions": [e.to_dict() for e in self.executions],
                "last_updated": datetime.now().isoformat()
            }
            with open(self._storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Could not save mode tracking data: {e}")
    
    def record(
        self,
        mode: str,
        action_type: str,
        execution_time_ms: float,
        cost_usd: float = 0.0,
        tokens_used: int = 0,
        success: bool = True,
        files_modified: Optional[List[str]] = None,
        files_created: Optional[List[str]] = None,
        plan_id: Optional[str] = None,
        description: str = ""
    ) -> ModeExecution:
        """
        Record a mode execution.
        
        Args:
            mode: AetherFlow mode (PROTO, PROD, FRONTEND, DESIGNER, SURGICAL)
            action_type: Type of action performed
            execution_time_ms: Execution time in milliseconds
            cost_usd: Cost in USD
            tokens_used: Number of tokens used
            success: Whether execution was successful
            files_modified: List of files modified
            files_created: List of files created
            plan_id: Associated plan ID
            description: Description of the execution
            
        Returns:
            The recorded ModeExecution
        """
        execution = ModeExecution(
            timestamp=datetime.now().isoformat(),
            mode=mode.upper(),
            action_type=action_type,
            files_modified=files_modified or [],
            files_created=files_created or [],
            execution_time_ms=execution_time_ms,
            cost_usd=cost_usd,
            tokens_used=tokens_used,
            success=success,
            plan_id=plan_id,
            description=description
        )
        
        self.executions.append(execution)
        
        # Save periodically (every 5 executions)
        if len(self.executions) % 5 == 0:
            self._save_data()
        
        logger.debug(f"Recorded {mode} execution: {action_type} ({execution_time_ms:.0f}ms)")
        return execution
    
    def save(self) -> None:
        """Force save current data."""
        self._save_data()
    
    def get_executions_by_mode(self, mode: Optional[str] = None) -> Dict[str, List[ModeExecution]]:
        """Get executions grouped by mode."""
        if mode:
            return {mode.upper(): [e for e in self.executions if e.mode == mode.upper()]}
        
        result = defaultdict(list)
        for e in self.executions:
            result[e.mode].append(e)
        return dict(result)
    
    def get_stats_by_mode(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics grouped by mode."""
        stats = {}
        by_mode = self.get_executions_by_mode()
        
        for mode, executions in by_mode.items():
            successful = [e for e in executions if e.success]
            failed = [e for e in executions if not e.success]
            
            stats[mode] = {
                "total_executions": len(executions),
                "successful": len(successful),
                "failed": len(failed),
                "success_rate": len(successful) / len(executions) if executions else 0,
                "total_time_ms": sum(e.execution_time_ms for e in executions),
                "avg_time_ms": sum(e.execution_time_ms for e in executions) / len(executions) if executions else 0,
                "total_cost_usd": sum(e.cost_usd for e in executions),
                "total_tokens": sum(e.tokens_used for e in executions),
                "files_modified": sum(len(e.files_modified) for e in executions),
                "files_created": sum(len(e.files_created) for e in executions)
            }
        
        return stats
    
    def get_daily_stats(self, days: int = 30) -> Dict[str, Dict[str, Any]]:
        """Get daily statistics for the last N days."""
        cutoff = datetime.now() - timedelta(days=days)
        daily = defaultdict(lambda: defaultdict(lambda: {
            "count": 0, "time_ms": 0, "cost": 0, "tokens": 0
        }))
        
        for e in self.executions:
            try:
                entry_time = datetime.fromisoformat(e.timestamp)
                if entry_time >= cutoff:
                    day_key = entry_time.strftime("%Y-%m-%d")
                    daily[day_key][e.mode]["count"] += 1
                    daily[day_key][e.mode]["time_ms"] += e.execution_time_ms
                    daily[day_key][e.mode]["cost"] += e.cost_usd
                    daily[day_key][e.mode]["tokens"] += e.tokens_used
            except:
                pass
        
        return dict(sorted(daily.items()))
    
    def get_total_cost(self) -> float:
        """Get cumulative total cost."""
        return sum(e.cost_usd for e in self.executions)
    
    def get_total_executions(self) -> int:
        """Get total number of executions."""
        return len(self.executions)
    
    def get_current_session_stats(self) -> Dict[str, Any]:
        """Get stats for current session (last hour of activity)."""
        cutoff = datetime.now() - timedelta(hours=1)
        recent = [e for e in self.executions 
                  if datetime.fromisoformat(e.timestamp) >= cutoff]
        
        by_mode = defaultdict(int)
        for e in recent:
            by_mode[e.mode] += 1
        
        return {
            "executions_last_hour": len(recent),
            "by_mode": dict(by_mode),
            "total_cost_last_hour": sum(e.cost_usd for e in recent)
        }
    
    def generate_summary(self) -> str:
        """Generate a text summary of mode usage."""
        stats = self.get_stats_by_mode()
        total_executions = self.get_total_executions()
        total_cost = self.get_total_cost()
        
        lines = [
            "=" * 70,
            "           AETHERFLOW MODE MONITORING - RÉSUMÉ",
            "=" * 70,
            "",
            f"📊 Total exécutions: {total_executions}",
            f"💰 Coût total: ${total_cost:.4f}",
            ""
        ]
        
        if stats:
            lines.append("-" * 70)
            lines.append("📈 USAGE PAR MODE:")
            lines.append("-" * 70)
            lines.append(f"{'Mode':<12} {'Count':>8} {'Succès':>8} {'Temps avg':>12} {'Coût':>10}")
            lines.append("-" * 70)
            
            for mode, s in sorted(stats.items()):
                lines.append(
                    f"{mode:<12} {s['total_executions']:>8} "
                    f"{s['success_rate']*100:>7.0f}% "
                    f"{s['avg_time_ms']/1000:>10.1f}s "
                    f"${s['total_cost_usd']:>9.4f}"
                )
            lines.append("")
        
        # Current session
        session = self.get_current_session_stats()
        lines.append("-" * 70)
        lines.append("⏱️ SESSION ACTUELLE (dernière heure):")
        lines.append("-" * 70)
        lines.append(f"   Exécutions: {session['executions_last_hour']}")
        lines.append(f"   Coût: ${session['total_cost_last_hour']:.4f}")
        for mode, count in session['by_mode'].items():
            lines.append(f"   {mode}: {count} exécutions")
        lines.append("")
        
        lines.append("=" * 70)
        return "\n".join(lines)
    
    def print_summary(self) -> None:
        """Print summary to console."""
        print(self.generate_summary())
    
    def export_json(self, output_path: Path) -> None:
        """Export all executions to JSON."""
        data = {
            "executions": [e.to_dict() for e in self.executions],
            "stats": self.get_stats_by_mode(),
            "exported_at": datetime.now().isoformat()
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Mode tracking exported to: {output_path}")


# Global instance
_global_monitor: Optional[ModeMonitor] = None


def get_mode_monitor() -> ModeMonitor:
    """Get the global mode monitor instance."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = ModeMonitor()
    return _global_monitor


def record_mode_execution(
    mode: str,
    action_type: str,
    execution_time_ms: float,
    **kwargs
) -> ModeExecution:
    """Convenience function to record a mode execution."""
    monitor = get_mode_monitor()
    return monitor.record(
        mode=mode,
        action_type=action_type,
        execution_time_ms=execution_time_ms,
        **kwargs
    )


def print_mode_summary() -> None:
    """Print mode usage summary."""
    monitor = get_mode_monitor()
    monitor.print_summary()
