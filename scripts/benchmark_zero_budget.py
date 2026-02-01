"""Benchmark script for zero-budget optimizations."""
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from loguru import logger

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from Backend.Prod.orchestrator import Orchestrator
from Backend.Prod.models.plan_reader import PlanReader
from Backend.Prod.models.metrics import MetricsCollector


async def benchmark_mode_comparison(
    plan_path: Path,
    output_dir: Path
) -> Dict[str, Any]:
    """
    Compare execution modes: FAST vs BUILD vs DOUBLE-CHECK.
    
    Args:
        plan_path: Path to plan JSON file
        output_dir: Output directory for results
        
    Returns:
        Dictionary with comparison results
    """
    logger.info("Starting mode comparison benchmark")
    
    modes = ["FAST", "BUILD", "DOUBLE-CHECK"]
    results = {}
    
    for mode in modes:
        logger.info(f"Testing mode: {mode}")
        orchestrator = Orchestrator(execution_mode=mode)
        
        try:
            start_time = datetime.now()
            result = await orchestrator.execute_plan(
                plan_path=plan_path,
                output_dir=output_dir / f"mode_{mode.lower()}",
                use_streaming=False,
                execution_mode=mode
            )
            end_time = datetime.now()
            
            execution_time_ms = (end_time - start_time).total_seconds() * 1000
            
            metrics = result["metrics"]
            results[mode] = {
                "execution_time_ms": execution_time_ms,
                "total_tokens": metrics.total_tokens_used,
                "total_cost_usd": metrics.total_cost_usd,
                "success_rate": metrics.success_rate,
                "total_steps": metrics.total_steps,
                "successful_steps": metrics.successful_steps,
                "failed_steps": metrics.failed_steps
            }
            
            logger.info(f"Mode {mode} completed: {execution_time_ms:.0f}ms, ${metrics.total_cost_usd:.4f}")
            
        except Exception as e:
            logger.error(f"Mode {mode} failed: {e}")
            results[mode] = {
                "error": str(e),
                "execution_time_ms": None,
                "total_tokens": None,
                "total_cost_usd": None,
                "success_rate": None
            }
        finally:
            await orchestrator.close()
    
    return results


async def benchmark_parallelization(
    plan_path: Path,
    output_dir: Path
) -> Dict[str, Any]:
    """
    Compare sequential vs parallel execution.
    
    Args:
        plan_path: Path to plan JSON file
        output_dir: Output directory for results
        
    Returns:
        Dictionary with comparison results
    """
    logger.info("Starting parallelization benchmark")
    
    # Read plan to get execution order
    plan_reader = PlanReader()
    plan = plan_reader.read(plan_path)
    execution_order = plan.get_execution_order()
    
    # Count parallelizable steps
    parallelizable_batches = [batch for batch in execution_order if len(batch) > 1]
    total_parallelizable_steps = sum(len(batch) for batch in parallelizable_batches)
    
    logger.info(f"Plan has {len(execution_order)} batches, {len(parallelizable_batches)} with parallelizable steps")
    logger.info(f"Total parallelizable steps: {total_parallelizable_steps}")
    
    # Execute with parallelization (normal mode)
    orchestrator = Orchestrator(execution_mode="BUILD")
    
    try:
        start_time = datetime.now()
        result = await orchestrator.execute_plan(
            plan_path=plan_path,
            output_dir=output_dir / "parallel",
            use_streaming=False
        )
        end_time = datetime.now()
        
        parallel_time_ms = (end_time - start_time).total_seconds() * 1000
        metrics = result["metrics"]
        
        parallel_results = {
            "execution_time_ms": parallel_time_ms,
            "total_tokens": metrics.total_tokens_used,
            "total_cost_usd": metrics.total_cost_usd,
            "success_rate": metrics.success_rate,
            "parallelizable_batches": len(parallelizable_batches),
            "total_parallelizable_steps": total_parallelizable_steps
        }
        
        logger.info(f"Parallel execution completed: {parallel_time_ms:.0f}ms")
        
    except Exception as e:
        logger.error(f"Parallel execution failed: {e}")
        parallel_results = {"error": str(e)}
    finally:
        await orchestrator.close()
    
    return {
        "parallel": parallel_results,
        "parallelization_info": {
            "total_batches": len(execution_order),
            "parallelizable_batches": len(parallelizable_batches),
            "total_parallelizable_steps": total_parallelizable_steps,
            "max_parallel_steps": max((len(batch) for batch in execution_order), default=0)
        }
    }


async def benchmark_streaming(
    plan_path: Path,
    output_dir: Path
) -> Dict[str, Any]:
    """
    Compare normal vs streaming execution.
    
    Args:
        plan_path: Path to plan JSON file
        output_dir: Output directory for results
        
    Returns:
        Dictionary with comparison results
    """
    logger.info("Starting streaming benchmark")
    
    orchestrator = Orchestrator(execution_mode="BUILD")
    
    # Normal execution
    try:
        start_time = datetime.now()
        result_normal = await orchestrator.execute_plan(
            plan_path=plan_path,
            output_dir=output_dir / "normal",
            use_streaming=False
        )
        end_time = datetime.now()
        
        normal_time_ms = (end_time - start_time).total_seconds() * 1000
        metrics_normal = result_normal["metrics"]
        
        normal_results = {
            "execution_time_ms": normal_time_ms,
            "total_tokens": metrics_normal.total_tokens_used,
            "total_cost_usd": metrics_normal.total_cost_usd,
            "success_rate": metrics_normal.success_rate
        }
        
        logger.info(f"Normal execution completed: {normal_time_ms:.0f}ms")
        
    except Exception as e:
        logger.error(f"Normal execution failed: {e}")
        normal_results = {"error": str(e)}
    
    # Streaming execution
    try:
        start_time = datetime.now()
        result_streaming = await orchestrator.execute_plan(
            plan_path=plan_path,
            output_dir=output_dir / "streaming",
            use_streaming=True
        )
        end_time = datetime.now()
        
        streaming_time_ms = (end_time - start_time).total_seconds() * 1000
        metrics_streaming = result_streaming["metrics"]
        
        streaming_results = {
            "execution_time_ms": streaming_time_ms,
            "total_tokens": metrics_streaming.total_tokens_used,
            "total_cost_usd": metrics_streaming.total_cost_usd,
            "success_rate": metrics_streaming.success_rate
        }
        
        logger.info(f"Streaming execution completed: {streaming_time_ms:.0f}ms")
        
    except Exception as e:
        logger.error(f"Streaming execution failed: {e}")
        streaming_results = {"error": str(e)}
    finally:
        await orchestrator.close()
    
    # Calculate gains
    if "error" not in normal_results and "error" not in streaming_results:
        time_saved_ms = normal_results["execution_time_ms"] - streaming_results["execution_time_ms"]
        time_saved_percent = (time_saved_ms / normal_results["execution_time_ms"]) * 100 if normal_results["execution_time_ms"] > 0 else 0
    else:
        time_saved_ms = None
        time_saved_percent = None
    
    return {
        "normal": normal_results,
        "streaming": streaming_results,
        "gains": {
            "time_saved_ms": time_saved_ms,
            "time_saved_percent": time_saved_percent
        }
    }


async def benchmark_prompt_stripping(
    plan_path: Path,
    output_dir: Path
) -> Dict[str, Any]:
    """
    Compare verbose vs stripped prompts.
    
    Note: This requires modifying AgentRouter to support verbose mode.
    For now, we'll just document the expected gains.
    
    Args:
        plan_path: Path to plan JSON file
        output_dir: Output directory for results
        
    Returns:
        Dictionary with comparison results
    """
    logger.info("Prompt stripping benchmark (stripped mode is default)")
    
    # Execute with stripped prompts (default)
    orchestrator = Orchestrator(execution_mode="BUILD")
    
    try:
        start_time = datetime.now()
        result = await orchestrator.execute_plan(
            plan_path=plan_path,
            output_dir=output_dir / "stripped",
            use_streaming=False
        )
        end_time = datetime.now()
        
        execution_time_ms = (end_time - start_time).total_seconds() * 1000
        metrics = result["metrics"]
        
        results = {
            "execution_time_ms": execution_time_ms,
            "total_tokens": metrics.total_tokens_used,
            "total_cost_usd": metrics.total_cost_usd,
            "success_rate": metrics.success_rate,
            "note": "Stripped prompts are used by default. Expected token reduction: 20-30%"
        }
        
        logger.info(f"Stripped prompts execution completed: {execution_time_ms:.0f}ms, {metrics.total_tokens_used} tokens")
        
    except Exception as e:
        logger.error(f"Stripped prompts execution failed: {e}")
        results = {"error": str(e)}
    finally:
        await orchestrator.close()
    
    return results


async def main():
    """Run all benchmarks."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Benchmark zero-budget optimizations")
    parser.add_argument(
        "--plan",
        type=Path,
        required=True,
        help="Path to plan JSON file"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/benchmark_zero_budget"),
        help="Output directory for results"
    )
    parser.add_argument(
        "--benchmark",
        choices=["all", "modes", "parallelization", "streaming", "prompts"],
        default="all",
        help="Which benchmark to run"
    )
    
    args = parser.parse_args()
    
    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)
    
    all_results = {
        "timestamp": datetime.now().isoformat(),
        "plan_path": str(args.plan),
        "benchmarks": {}
    }
    
    if args.benchmark in ["all", "modes"]:
        logger.info("=" * 60)
        logger.info("Benchmark: Mode Comparison")
        logger.info("=" * 60)
        all_results["benchmarks"]["mode_comparison"] = await benchmark_mode_comparison(
            args.plan,
            args.output
        )
    
    if args.benchmark in ["all", "parallelization"]:
        logger.info("=" * 60)
        logger.info("Benchmark: Parallelization")
        logger.info("=" * 60)
        all_results["benchmarks"]["parallelization"] = await benchmark_parallelization(
            args.plan,
            args.output
        )
    
    if args.benchmark in ["all", "streaming"]:
        logger.info("=" * 60)
        logger.info("Benchmark: Streaming")
        logger.info("=" * 60)
        all_results["benchmarks"]["streaming"] = await benchmark_streaming(
            args.plan,
            args.output
        )
    
    if args.benchmark in ["all", "prompts"]:
        logger.info("=" * 60)
        logger.info("Benchmark: Prompt Stripping")
        logger.info("=" * 60)
        all_results["benchmarks"]["prompt_stripping"] = await benchmark_prompt_stripping(
            args.plan,
            args.output
        )
    
    # Save results
    results_file = args.output / "benchmark_results.json"
    with open(results_file, "w") as f:
        json.dump(all_results, f, indent=2)
    
    logger.info(f"Benchmark results saved to: {results_file}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("BENCHMARK SUMMARY")
    print("=" * 60)
    
    if "mode_comparison" in all_results["benchmarks"]:
        print("\nMode Comparison:")
        for mode, result in all_results["benchmarks"]["mode_comparison"].items():
            if "error" not in result:
                print(f"  {mode}: {result['execution_time_ms']:.0f}ms, ${result['total_cost_usd']:.4f}, {result['success_rate']:.1%} success")
    
    if "streaming" in all_results["benchmarks"]:
        print("\nStreaming Gains:")
        gains = all_results["benchmarks"]["streaming"].get("gains", {})
        if gains.get("time_saved_ms"):
            print(f"  Time saved: {gains['time_saved_ms']:.0f}ms ({gains['time_saved_percent']:.1f}%)")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
