#!/usr/bin/env python3
"""
Benchmark script for Speculative Decoding.

Tests the performance of speculative decoding (draft + verify) vs normal execution.
Measures: accept rate, speedup factor, latency reduction.
"""
import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Any
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Backend.Prod.models.agent_router import AgentRouter
from Backend.Prod.models.plan_reader import Step
from Backend.Prod.cache import PromptCache
from Backend.Prod.models.execution_monitor import ExecutionMonitor
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn


async def benchmark_speculative_vs_normal():
    """Compare speculative decoding vs normal execution."""
    
    console = Console()
    
    # Show initialization progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Initializing routers and cache...", total=None)
        
        # Initialize router with speculative enabled
        # Disable semantic cache for benchmark (faster startup, not needed for this test)
        prompt_cache = PromptCache()
        router_speculative = AgentRouter(
            prompt_cache=prompt_cache, 
            enable_speculative=True,
            enable_semantic_cache=False  # Disable for faster startup
        )
        router_normal = AgentRouter(
            prompt_cache=prompt_cache, 
            enable_speculative=False,
            enable_semantic_cache=False  # Disable for faster startup
        )
        
        progress.update(task, description="✓ Routers initialized")
    
    # Test steps: long/complex code generation tasks
    test_steps = [
        Step({
            "id": "step_1",
            "description": "Generate a complete REST API with FastAPI including authentication, CRUD operations, and error handling",
            "type": "code_generation",
            "complexity": 0.8,
            "estimated_tokens": 2000,
            "dependencies": []
        }),
        Step({
            "id": "step_2",
            "description": "Create a comprehensive test suite with pytest covering unit tests, integration tests, and fixtures",
            "type": "code_generation",
            "complexity": 0.75,
            "estimated_tokens": 1500,
            "dependencies": []
        }),
        Step({
            "id": "step_3",
            "description": "Implement a data processing pipeline with pandas including data cleaning, transformation, and validation",
            "type": "code_generation",
            "complexity": 0.7,
            "estimated_tokens": 1200,
            "dependencies": []
        }),
    ]
    
    results = {
        "speculative": [],
        "normal": []
    }
    
    console.print(Panel.fit(
        "[bold cyan]Speculative Decoding Benchmark[/bold cyan]\n"
        f"Testing {len(test_steps)} steps\n"
        "Comparing speculative (draft+verify) vs normal execution",
        border_style="cyan"
    ))
    
    # Initialize monitoring for benchmark
    monitor = ExecutionMonitor("Speculative Decoding Benchmark", len(test_steps) * 2)  # 2 runs per step
    monitor.start_monitoring()  # Start live display
    
    # Print initial state
    console.print("\n[bold cyan]Starting benchmark with live monitoring...[/bold cyan]\n")
    
    for step_idx, step in enumerate(test_steps, 1):
        console.print(f"\n[bold yellow]{'='*60}[/bold yellow]")
        console.print(f"[bold]Step {step_idx}/{len(test_steps)}: {step.id}[/bold]")
        console.print(f"Description: {step.description[:60]}...")
        console.print(f"Complexity: {step.complexity}, Tokens: {step.estimated_tokens}")
        
        # Add step to monitor
        monitor.add_step(f"{step.id}_spec", f"{step.description[:40]}... (Speculative)", "code_generation", step.complexity)
        monitor.add_step(f"{step.id}_normal", f"{step.description[:40]}... (Normal)", "code_generation", step.complexity)
        
        # Test with speculative decoding
        console.print("\n[cyan]--- With Speculative Decoding ---[/cyan]")
        monitor.start_step(f"{step.id}_spec", "groq+deepseek")
        start_spec = time.time()
        try:
            result_spec = await router_speculative.execute_step(
                step=step,
                context=None,
                use_speculative=True
            )
            time_spec = (time.time() - start_spec) * 1000  # ms
            
            monitor.complete_step(
                f"{step.id}_spec",
                result_spec.success,
                time_spec,
                result_spec.tokens_used,
                result_spec.cost_usd,
                result_spec.error
            )
            
            results["speculative"].append({
                "step_id": step.id,
                "success": result_spec.success,
                "time_ms": time_spec,
                "tokens": result_spec.tokens_used,
                "cost": result_spec.cost_usd
            })
            
            console.print(f"[green]✓ Speculative:[/green] {time_spec:.0f}ms, {result_spec.tokens_used} tokens, ${result_spec.cost_usd:.4f}")
        except Exception as e:
            console.print(f"[red]✗ Speculative failed:[/red] {e}")
            monitor.complete_step(f"{step.id}_spec", False, 0, 0, 0.0, str(e))
            results["speculative"].append({
                "step_id": step.id,
                "success": False,
                "error": str(e)
            })
        
        # Test with normal execution
        console.print("\n[cyan]--- Normal Execution ---[/cyan]")
        monitor.start_step(f"{step.id}_normal", "deepseek")
        start_normal = time.time()
        try:
            result_normal = await router_normal.execute_step(
                step=step,
                context=None,
                use_speculative=False
            )
            time_normal = (time.time() - start_normal) * 1000  # ms
            
            monitor.complete_step(
                f"{step.id}_normal",
                result_normal.success,
                time_normal,
                result_normal.tokens_used,
                result_normal.cost_usd,
                result_normal.error
            )
            
            results["normal"].append({
                "step_id": step.id,
                "success": result_normal.success,
                "time_ms": time_normal,
                "tokens": result_normal.tokens_used,
                "cost": result_normal.cost_usd
            })
            
            console.print(f"[green]✓ Normal:[/green] {time_normal:.0f}ms, {result_normal.tokens_used} tokens, ${result_normal.cost_usd:.4f}")
        except Exception as e:
            console.print(f"[red]✗ Normal failed:[/red] {e}")
            monitor.complete_step(f"{step.id}_normal", False, 0, 0, 0.0, str(e))
            results["normal"].append({
                "step_id": step.id,
                "success": False,
                "error": str(e)
            })
        
        # Calculate speedup
        if results["speculative"][-1].get("success") and results["normal"][-1].get("success"):
            speedup = results["normal"][-1]["time_ms"] / results["speculative"][-1]["time_ms"]
            console.print(f"\n[bold green]📊 Speedup: {speedup:.2f}x[/bold green]")
    
    # Stop monitoring
    monitor.stop_monitoring()
    monitor.print_final_summary()
    
    # Generate summary report
    console.print(f"\n[bold yellow]{'='*60}[/bold yellow]")
    console.print("[bold cyan]BENCHMARK SUMMARY[/bold cyan]")
    console.print(f"[yellow]{'='*60}[/yellow]")
    
    total_spec = sum(r.get("time_ms", 0) for r in results["speculative"] if r.get("success"))
    total_normal = sum(r.get("time_ms", 0) for r in results["normal"] if r.get("success"))
    
    if total_normal > 0:
        overall_speedup = total_normal / total_spec if total_spec > 0 else 1.0
        console.print(f"\n[bold green]Overall Speedup: {overall_speedup:.2f}x[/bold green]")
        console.print(f"Total Time (Speculative): {total_spec:.0f}ms")
        console.print(f"Total Time (Normal): {total_normal:.0f}ms")
        time_saved = total_normal - total_spec
        time_saved_pct = ((time_saved / total_normal) * 100) if total_normal > 0 else 0
        console.print(f"[green]Time Saved: {time_saved:.0f}ms ({time_saved_pct:.1f}%)[/green]")
    
    # Save results to JSON
    output_file = Path(__file__).parent.parent / "output" / "benchmark_speculative.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump({
            "results": results,
            "summary": {
                "total_speculative_ms": total_spec,
                "total_normal_ms": total_normal,
                "overall_speedup": overall_speedup if total_normal > 0 else 1.0,
                "time_saved_ms": total_normal - total_spec,
                "time_saved_percent": ((total_normal - total_spec) / total_normal * 100) if total_normal > 0 else 0
            }
        }, f, indent=2)
    
    console.print(f"\n[green]✓ Results saved to: {output_file}[/green]")
    
    return results


if __name__ == "__main__":
    asyncio.run(benchmark_speculative_vs_normal())
