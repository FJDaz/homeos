"""Metrics collection and reporting for AetherFlow."""
import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from loguru import logger

from .deepseek_client import StepResult
from .plan_reader import Plan, Step


@dataclass
class StepMetrics:
    """Metrics for a single step."""
    step_id: str
    step_description: str
    step_type: str
    success: bool
    execution_time_ms: float
    tokens_used: int
    input_tokens: int
    output_tokens: int
    cost_usd: float
    error: Optional[str] = None
    # Latency metrics (will be None if not available yet)
    ttft_ms: Optional[float] = None  # Time to first token
    ttr_ms: Optional[float] = None  # Time to response (total)
    queue_latency_ms: Optional[float] = None  # Queue wait time
    network_overhead_ms: Optional[float] = None  # DNS + TCP + TLS (reduced by connection pooling)
    connection_reused: Optional[bool] = None  # Whether connection was reused (pool hit)
    provider: Optional[str] = None  # Provider used for this step
    # Cache metrics (will be None if not available yet)
    cache_hit: Optional[bool] = None  # Whether prompt cache was hit
    cache_read_cost_multiplier: Optional[float] = None  # Cost multiplier if cache hit
    # Speculative decoding metrics (will be None if not used)
    speculative_enabled: Optional[bool] = None  # Whether speculative decoding was used
    speculative_accept_rate: Optional[float] = None  # % of draft tokens accepted
    speculative_speedup_factor: Optional[float] = None  # Speedup vs non-speculative
    draft_provider: Optional[str] = None  # Provider used for draft
    verify_provider: Optional[str] = None  # Provider used for verification


@dataclass
class PlanMetrics:
    """Aggregated metrics for a complete plan execution."""
    task_id: str
    task_description: str
    total_steps: int
    successful_steps: int
    failed_steps: int
    total_execution_time_ms: float
    total_tokens_used: int
    total_input_tokens: int
    total_output_tokens: int
    total_cost_usd: float
    average_step_time_ms: float
    success_rate: float
    started_at: str
    completed_at: str
    step_metrics: List[Dict[str, Any]]


class MetricsCollector:
    """Collects and aggregates execution metrics."""
    
    def __init__(self, plan: Plan):
        """
        Initialize metrics collector.
        
        Args:
            plan: The plan being executed
        """
        self.plan = plan
        self.step_metrics: List[StepMetrics] = []
        self.started_at = datetime.now()
        self.completed_at: Optional[datetime] = None
    
    def record_step_result(
        self, 
        step: Step, 
        result: StepResult,
        provider: Optional[str] = None,
        ttft_ms: Optional[float] = None,
        ttr_ms: Optional[float] = None,
        queue_latency_ms: Optional[float] = None,
        speculative_accept_rate: Optional[float] = None,
        speculative_speedup: Optional[float] = None,
        draft_provider: Optional[str] = None,
        verify_provider: Optional[str] = None,
        network_overhead_ms: Optional[float] = None,
        cache_hit: Optional[bool] = None,
        cache_read_cost_multiplier: Optional[float] = None
    ) -> None:
        """
        Record metrics for a completed step.
        
        Args:
            step: The step that was executed
            result: The execution result
            provider: Provider used for this step
            ttft_ms: Time to first token in milliseconds
            ttr_ms: Time to response in milliseconds
            queue_latency_ms: Queue wait time in milliseconds
            network_overhead_ms: Network overhead (DNS + TCP + TLS) in milliseconds
            cache_hit: Whether prompt cache was hit
            cache_read_cost_multiplier: Cost multiplier if cache hit (e.g., 0.1 for cache reads)
            speculative_accept_rate: Speculative decoding accept rate (%)
            speculative_speedup: Speculative decoding speedup factor
            draft_provider: Provider used for draft generation
            verify_provider: Provider used for verification
        """
        metrics = StepMetrics(
            step_id=step.id,
            step_description=step.description,
            step_type=step.type,
            success=result.success,
            execution_time_ms=result.execution_time_ms,
            tokens_used=result.tokens_used,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            cost_usd=result.cost_usd,
            error=result.error,
            provider=provider,
            ttft_ms=ttft_ms,
            ttr_ms=ttr_ms or result.execution_time_ms,  # Default to execution_time if not provided
            queue_latency_ms=queue_latency_ms,
            network_overhead_ms=network_overhead_ms,
            cache_hit=cache_hit,
            cache_read_cost_multiplier=cache_read_cost_multiplier,
            speculative_enabled=speculative_accept_rate is not None,
            speculative_accept_rate=speculative_accept_rate,
            speculative_speedup_factor=speculative_speedup,
            draft_provider=draft_provider,
            verify_provider=verify_provider
        )
        self.step_metrics.append(metrics)
        logger.debug(f"Recorded metrics for step {step.id}")
    
    def finalize(self) -> None:
        """Mark execution as completed."""
        self.completed_at = datetime.now()
    
    def get_plan_metrics(self) -> PlanMetrics:
        """
        Get aggregated metrics for the entire plan.
        
        Returns:
            PlanMetrics with aggregated data
        """
        if not self.completed_at:
            self.finalize()
        
        total_time = (self.completed_at - self.started_at).total_seconds() * 1000
        
        successful = sum(1 for m in self.step_metrics if m.success)
        failed = len(self.step_metrics) - successful
        
        total_tokens = sum(m.tokens_used for m in self.step_metrics)
        total_input = sum(m.input_tokens for m in self.step_metrics)
        total_output = sum(m.output_tokens for m in self.step_metrics)
        total_cost = sum(m.cost_usd for m in self.step_metrics)
        
        avg_time = total_time / len(self.step_metrics) if self.step_metrics else 0
        success_rate = successful / len(self.step_metrics) if self.step_metrics else 0
        
        return PlanMetrics(
            task_id=self.plan.task_id,
            task_description=self.plan.description,
            total_steps=len(self.step_metrics),
            successful_steps=successful,
            failed_steps=failed,
            total_execution_time_ms=total_time,
            total_tokens_used=total_tokens,
            total_input_tokens=total_input,
            total_output_tokens=total_output,
            total_cost_usd=total_cost,
            average_step_time_ms=avg_time,
            success_rate=success_rate,
            started_at=self.started_at.isoformat(),
            completed_at=self.completed_at.isoformat(),
            step_metrics=[asdict(m) for m in self.step_metrics]
        )
    
    def export_json(self, output_path: Path) -> None:
        """
        Export metrics to JSON file.
        
        Args:
            output_path: Path to output JSON file
        """
        metrics = self.get_plan_metrics()
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(asdict(metrics), f, indent=2, ensure_ascii=False)
        
        logger.info(f"Metrics exported to JSON: {output_path}")
    
    def export_csv(self, output_path: Path) -> None:
        """
        Export metrics to CSV file.
        
        Args:
            output_path: Path to output CSV file
        """
        metrics = self.get_plan_metrics()
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                "Metric", "Value"
            ])
            
            # Write plan-level metrics
            writer.writerow(["Task ID", metrics.task_id])
            writer.writerow(["Task Description", metrics.task_description])
            writer.writerow(["Total Steps", metrics.total_steps])
            writer.writerow(["Successful Steps", metrics.successful_steps])
            writer.writerow(["Failed Steps", metrics.failed_steps])
            writer.writerow(["Total Execution Time (ms)", metrics.total_execution_time_ms])
            writer.writerow(["Average Step Time (ms)", metrics.average_step_time_ms])
            writer.writerow(["Total Tokens Used", metrics.total_tokens_used])
            writer.writerow(["Total Input Tokens", metrics.total_input_tokens])
            writer.writerow(["Total Output Tokens", metrics.total_output_tokens])
            writer.writerow(["Total Cost (USD)", metrics.total_cost_usd])
            writer.writerow(["Success Rate", metrics.success_rate])
            writer.writerow(["Started At", metrics.started_at])
            writer.writerow(["Completed At", metrics.completed_at])
            
            # Write step-level metrics
            writer.writerow([])  # Empty row
            writer.writerow([
                "Step ID", "Description", "Type", "Success", 
                "Time (ms)", "Tokens", "Input Tokens", "Output Tokens", 
                "Cost (USD)", "Error"
            ])
            
            for step_metric in metrics.step_metrics:
                writer.writerow([
                    step_metric["step_id"],
                    step_metric["step_description"],
                    step_metric["step_type"],
                    step_metric["success"],
                    step_metric["execution_time_ms"],
                    step_metric["tokens_used"],
                    step_metric["input_tokens"],
                    step_metric["output_tokens"],
                    step_metric["cost_usd"],
                    step_metric.get("error", "")
                ])
        
        logger.info(f"Metrics exported to CSV: {output_path}")
    
    def print_summary(self) -> None:
        """Print a summary of metrics to console."""
        metrics = self.get_plan_metrics()
        
        logger.info("=" * 60)
        logger.info("EXECUTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Task: {metrics.task_description}")
        logger.info(f"Task ID: {metrics.task_id}")
        logger.info(f"Total Steps: {metrics.total_steps}")
        logger.info(f"Successful: {metrics.successful_steps}")
        logger.info(f"Failed: {metrics.failed_steps}")
        logger.info(f"Success Rate: {metrics.success_rate:.1%}")
        logger.info(f"Total Time: {metrics.total_execution_time_ms:.0f}ms ({metrics.total_execution_time_ms/1000:.2f}s)")
        logger.info(f"Average Step Time: {metrics.average_step_time_ms:.0f}ms")
        logger.info(f"Total Tokens: {metrics.total_tokens_used:,}")
        logger.info(f"  Input: {metrics.total_input_tokens:,}")
        logger.info(f"  Output: {metrics.total_output_tokens:,}")
        logger.info(f"Total Cost: ${metrics.total_cost_usd:.4f}")
        logger.info("=" * 60)
