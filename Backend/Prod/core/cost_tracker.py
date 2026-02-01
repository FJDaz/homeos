"""
Cost Tracker for AETHERFLOW - Persistent monitoring of API costs.

This module provides:
- Real-time cost tracking during execution
- Persistent storage of cumulative costs
- Cost reports by provider, workflow, and time period
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from collections import defaultdict
from dataclasses import dataclass, asdict
from loguru import logger


@dataclass
class CostEntry:
    """Single cost entry."""
    timestamp: str
    provider: str
    workflow_type: str
    step_id: str
    task_id: str
    cost_usd: float
    tokens_total: int
    tokens_input: int
    tokens_output: int
    execution_time_ms: float
    cached: bool = False


class CostTracker:
    """
    Persistent cost tracker for AETHERFLOW.

    Tracks all API costs and provides reporting capabilities.
    Data is stored in a JSON file for persistence across sessions.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize cost tracker.

        Args:
            storage_path: Path to store cost data. Defaults to ~/.aetherflow/costs.json
        """
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path.home() / ".aetherflow" / "costs.json"

        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._load_data()

    def _load_data(self):
        """Load existing cost data from storage."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                self.entries: List[Dict[str, Any]] = data.get("entries", [])
                self.cumulative_cost: float = data.get("cumulative_cost", 0.0)
                self.cumulative_tokens: int = data.get("cumulative_tokens", 0)
                logger.debug(f"Loaded {len(self.entries)} cost entries, total: ${self.cumulative_cost:.4f}")
            except Exception as e:
                logger.warning(f"Could not load cost data: {e}. Starting fresh.")
                self._init_empty()
        else:
            self._init_empty()

    def _init_empty(self):
        """Initialize empty data structures."""
        self.entries = []
        self.cumulative_cost = 0.0
        self.cumulative_tokens = 0

    def _save_data(self):
        """Save cost data to storage."""
        try:
            data = {
                "entries": self.entries,
                "cumulative_cost": self.cumulative_cost,
                "cumulative_tokens": self.cumulative_tokens,
                "last_updated": datetime.now().isoformat()
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save cost data: {e}")

    def record(
        self,
        provider: str,
        workflow_type: str,
        step_id: str,
        task_id: str,
        cost_usd: float,
        tokens_total: int,
        tokens_input: int = 0,
        tokens_output: int = 0,
        execution_time_ms: float = 0,
        cached: bool = False
    ):
        """
        Record a cost entry.

        Args:
            provider: LLM provider (deepseek, groq, gemini, etc.)
            workflow_type: Workflow type (FAST, BUILD, DOUBLE-CHECK)
            step_id: Step identifier
            task_id: Task identifier
            cost_usd: Cost in USD
            tokens_total: Total tokens used
            tokens_input: Input tokens
            tokens_output: Output tokens
            execution_time_ms: Execution time in milliseconds
            cached: Whether result was from cache
        """
        entry = CostEntry(
            timestamp=datetime.now().isoformat(),
            provider=provider,
            workflow_type=workflow_type,
            step_id=step_id,
            task_id=task_id,
            cost_usd=cost_usd,
            tokens_total=tokens_total,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            execution_time_ms=execution_time_ms,
            cached=cached
        )

        self.entries.append(asdict(entry))
        self.cumulative_cost += cost_usd
        self.cumulative_tokens += tokens_total

        # Save periodically (every 10 entries) or if cost is significant
        if len(self.entries) % 10 == 0 or cost_usd > 0.01:
            self._save_data()

    def save(self):
        """Force save current data."""
        self._save_data()

    def get_total_cost(self) -> float:
        """Get cumulative total cost."""
        return self.cumulative_cost

    def get_total_tokens(self) -> int:
        """Get cumulative total tokens."""
        return self.cumulative_tokens

    def get_cost_by_provider(self) -> Dict[str, float]:
        """Get costs grouped by provider."""
        costs = defaultdict(float)
        for entry in self.entries:
            costs[entry["provider"]] += entry["cost_usd"]
        return dict(costs)

    def get_cost_by_workflow(self) -> Dict[str, float]:
        """Get costs grouped by workflow type."""
        costs = defaultdict(float)
        for entry in self.entries:
            costs[entry["workflow_type"]] += entry["cost_usd"]
        return dict(costs)

    def get_cost_for_period(self, days: int = 30) -> float:
        """Get cost for the last N days."""
        cutoff = datetime.now() - timedelta(days=days)
        total = 0.0
        for entry in self.entries:
            try:
                entry_time = datetime.fromisoformat(entry["timestamp"])
                if entry_time >= cutoff:
                    total += entry["cost_usd"]
            except:
                pass
        return total

    def get_daily_costs(self, days: int = 30) -> Dict[str, float]:
        """Get daily costs for the last N days."""
        cutoff = datetime.now() - timedelta(days=days)
        daily = defaultdict(float)

        for entry in self.entries:
            try:
                entry_time = datetime.fromisoformat(entry["timestamp"])
                if entry_time >= cutoff:
                    day_key = entry_time.strftime("%Y-%m-%d")
                    daily[day_key] += entry["cost_usd"]
            except:
                pass

        return dict(sorted(daily.items()))

    def get_cache_savings(self) -> Dict[str, Any]:
        """Calculate savings from cache hits."""
        total_cached = 0
        total_uncached = 0
        cached_count = 0
        uncached_count = 0

        for entry in self.entries:
            if entry.get("cached"):
                cached_count += 1
                # Estimate what it would have cost without cache
                # Assume similar cost to uncached entries with similar token count
                total_cached += entry["tokens_total"]
            else:
                uncached_count += 1
                total_uncached += entry["cost_usd"]

        # Estimate cost per token from uncached entries
        if total_uncached > 0 and uncached_count > 0:
            avg_cost_per_entry = total_uncached / uncached_count
            estimated_savings = cached_count * avg_cost_per_entry
        else:
            estimated_savings = 0

        return {
            "cached_requests": cached_count,
            "uncached_requests": uncached_count,
            "cache_hit_rate": cached_count / (cached_count + uncached_count) if (cached_count + uncached_count) > 0 else 0,
            "estimated_savings_usd": estimated_savings
        }

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get detailed usage statistics."""
        provider_stats = defaultdict(lambda: {"calls": 0, "tokens": 0, "cost": 0.0})
        workflow_stats = defaultdict(lambda: {"calls": 0, "tokens": 0, "cost": 0.0})

        for entry in self.entries:
            provider = entry.get("provider", "unknown")
            workflow = entry.get("workflow_type", "unknown")

            provider_stats[provider]["calls"] += 1
            provider_stats[provider]["tokens"] += entry.get("tokens_total", 0)
            provider_stats[provider]["cost"] += entry.get("cost_usd", 0)

            workflow_stats[workflow]["calls"] += 1
            workflow_stats[workflow]["tokens"] += entry.get("tokens_total", 0)
            workflow_stats[workflow]["cost"] += entry.get("cost_usd", 0)

        return {
            "by_provider": dict(provider_stats),
            "by_workflow": dict(workflow_stats)
        }

    def generate_report(self) -> str:
        """Generate a formatted cost report with usage statistics."""
        usage = self.get_usage_stats()

        lines = [
            "=" * 70,
            "           AETHERFLOW - BILAN FINANCIER & USAGE",
            "=" * 70,
            "",
            f"📊 Total API calls: {len(self.entries)}",
            f"💰 Total cost: ${self.cumulative_cost:.4f} (~{self.cumulative_cost * 0.92:.2f} EUR)",
            f"📈 Total tokens: {self.cumulative_tokens:,}",
            ""
        ]

        # Cost by provider with calls
        lines.append("-" * 70)
        lines.append("📦 USAGE PAR PROVIDER:")
        lines.append("-" * 70)
        lines.append(f"{'Provider':<12} {'Appels':>8} {'Tokens':>12} {'Coût':>10} {'%':>6}")
        lines.append("-" * 70)

        for provider, stats in sorted(usage["by_provider"].items(), key=lambda x: -x[1]["cost"]):
            pct = (stats["cost"] / self.cumulative_cost * 100) if self.cumulative_cost > 0 else 0
            lines.append(
                f"{provider:<12} {stats['calls']:>8} {stats['tokens']:>12,} "
                f"${stats['cost']:>9.4f} {pct:>5.1f}%"
            )
        lines.append("")

        # Cost by workflow with calls
        lines.append("-" * 70)
        lines.append("🔄 USAGE PAR MODE:")
        lines.append("-" * 70)
        lines.append(f"{'Mode':<15} {'Appels':>8} {'Tokens':>12} {'Coût':>10} {'%':>6}")
        lines.append("-" * 70)

        for wf, stats in sorted(usage["by_workflow"].items(), key=lambda x: -x[1]["cost"]):
            pct = (stats["cost"] / self.cumulative_cost * 100) if self.cumulative_cost > 0 else 0
            lines.append(
                f"{wf:<15} {stats['calls']:>8} {stats['tokens']:>12,} "
                f"${stats['cost']:>9.4f} {pct:>5.1f}%"
            )
        lines.append("")

        # Cache savings
        cache_stats = self.get_cache_savings()
        if cache_stats["cached_requests"] > 0:
            lines.append("-" * 70)
            lines.append("💾 CACHE PERFORMANCE:")
            lines.append("-" * 70)
            lines.append(f"   Cache hits: {cache_stats['cached_requests']} requests")
            lines.append(f"   Cache hit rate: {cache_stats['cache_hit_rate']*100:.1f}%")
            lines.append(f"   Estimated savings: ${cache_stats['estimated_savings_usd']:.4f}")
            lines.append("")

        # Recent costs
        last_7_days = self.get_cost_for_period(7)
        last_30_days = self.get_cost_for_period(30)
        lines.append("-" * 70)
        lines.append("📅 PÉRIODE:")
        lines.append("-" * 70)
        lines.append(f"   Last 7 days:  ${last_7_days:.4f}")
        lines.append(f"   Last 30 days: ${last_30_days:.4f}")
        lines.append("")

        # Comparison with Claude/Cursor
        lines.append("-" * 70)
        lines.append("📊 COMPARAISON (si même travail avec Claude API direct):")
        lines.append("-" * 70)
        # Claude Sonnet pricing: $3/M input, $15/M output tokens
        # Estimate 70% input, 30% output
        estimated_input = int(self.cumulative_tokens * 0.7)
        estimated_output = int(self.cumulative_tokens * 0.3)
        claude_cost = (estimated_input * 3 / 1_000_000) + (estimated_output * 15 / 1_000_000)
        lines.append(f"   Claude API (Sonnet): ~${claude_cost:.2f}")
        lines.append(f"   AETHERFLOW actual:   ${self.cumulative_cost:.4f}")
        savings = claude_cost - self.cumulative_cost
        savings_pct = (savings / claude_cost * 100) if claude_cost > 0 else 0
        lines.append(f"   💰 Économies: ${savings:.2f} ({savings_pct:.0f}%)")
        lines.append("")

        lines.append("=" * 70)
        lines.append("Note: AETHERFLOW utilise Groq (gratuit), DeepSeek (~$0.14/M),")
        lines.append("      Gemini Flash (~gratuit) vs Claude Sonnet ($3-15/M)")
        lines.append("=" * 70)

        return "\n".join(lines)


# Global tracker instance
_global_tracker: Optional[CostTracker] = None


def get_cost_tracker() -> CostTracker:
    """Get the global cost tracker instance."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = CostTracker()
    return _global_tracker


def record_cost(
    provider: str,
    workflow_type: str,
    step_id: str,
    task_id: str,
    cost_usd: float,
    tokens_total: int,
    **kwargs
):
    """Convenience function to record a cost."""
    tracker = get_cost_tracker()
    tracker.record(
        provider=provider,
        workflow_type=workflow_type,
        step_id=step_id,
        task_id=task_id,
        cost_usd=cost_usd,
        tokens_total=tokens_total,
        **kwargs
    )


def get_cost_report() -> str:
    """Get the current cost report."""
    tracker = get_cost_tracker()
    return tracker.generate_report()
