#!/usr/bin/env python3
"""Script de benchmark complet pour AETHERFLOW avec métriques de latence."""
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from collections import defaultdict
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Backend.Prod.orchestrator import Orchestrator, ExecutionError
from Backend.Prod.models.plan_reader import PlanReader, PlanValidationError

console = Console()


async def benchmark_plan(plan_path: Path, output_dir: Path) -> Dict[str, Any]:
    """
    Exécute un plan et collecte les métriques complètes pour benchmark.
    
    Args:
        plan_path: Chemin vers le plan JSON
        output_dir: Répertoire de sortie
        
    Returns:
        Dictionnaire avec toutes les métriques
    """
    console.print(f"[cyan]📊 Benchmark Complet: {plan_path.name}[/]")
    
    orchestrator = Orchestrator()
    
    try:
        # Exécuter le plan
        result = await orchestrator.execute_plan(
            plan_path=plan_path,
            output_dir=output_dir
        )
        
        metrics = result["metrics"]
        plan = result["plan"]
        
        # Analyser les métriques par provider
        provider_stats = defaultdict(lambda: {
            "count": 0,
            "total_time_ms": 0.0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "success_count": 0,
            "ttft_ms": [],
            "ttr_ms": []
        })
        
        step_type_stats = defaultdict(lambda: {
            "count": 0,
            "total_time_ms": 0.0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "success_count": 0
        })
        
        for step_m in metrics.step_metrics:
            provider = step_m.get("provider", "unknown")
            step_type = step_m.get("step_type", "unknown")
            
            # Stats par provider
            provider_stats[provider]["count"] += 1
            provider_stats[provider]["total_time_ms"] += step_m.get("execution_time_ms", 0)
            provider_stats[provider]["total_tokens"] += step_m.get("tokens_used", 0)
            provider_stats[provider]["total_cost"] += step_m.get("cost_usd", 0)
            if step_m.get("success"):
                provider_stats[provider]["success_count"] += 1
            if step_m.get("ttft_ms"):
                provider_stats[provider]["ttft_ms"].append(step_m["ttft_ms"])
            if step_m.get("ttr_ms"):
                provider_stats[provider]["ttr_ms"].append(step_m["ttr_ms"])
            
            # Stats par type
            step_type_stats[step_type]["count"] += 1
            step_type_stats[step_type]["total_time_ms"] += step_m.get("execution_time_ms", 0)
            step_type_stats[step_type]["total_tokens"] += step_m.get("tokens_used", 0)
            step_type_stats[step_type]["total_cost"] += step_m.get("cost_usd", 0)
            if step_m.get("success"):
                step_type_stats[step_type]["success_count"] += 1
        
        # Calculer moyennes pour providers
        provider_analysis = {}
        for provider, stats in provider_stats.items():
            count = stats["count"]
            provider_analysis[provider] = {
                "count": count,
                "avg_time_ms": stats["total_time_ms"] / count if count > 0 else 0,
                "avg_tokens": stats["total_tokens"] / count if count > 0 else 0,
                "avg_cost": stats["total_cost"] / count if count > 0 else 0,
                "success_rate": stats["success_count"] / count if count > 0 else 0,
                "avg_ttft_ms": sum(stats["ttft_ms"]) / len(stats["ttft_ms"]) if stats["ttft_ms"] else None,
                "avg_ttr_ms": sum(stats["ttr_ms"]) / len(stats["ttr_ms"]) if stats["ttr_ms"] else None,
                "total_time_ms": stats["total_time_ms"],
                "total_tokens": stats["total_tokens"],
                "total_cost": stats["total_cost"]
            }
        
        # Calculer moyennes pour types
        type_analysis = {}
        for step_type, stats in step_type_stats.items():
            count = stats["count"]
            type_analysis[step_type] = {
                "count": count,
                "avg_time_ms": stats["total_time_ms"] / count if count > 0 else 0,
                "avg_tokens": stats["total_tokens"] / count if count > 0 else 0,
                "avg_cost": stats["total_cost"] / count if count > 0 else 0,
                "success_rate": stats["success_count"] / count if count > 0 else 0
            }
        
        # Collecter les métriques détaillées
        benchmark_data = {
            "task_id": plan.task_id,
            "task_description": plan.description,
            "execution_date": datetime.now().isoformat(),
            "plan_file": str(plan_path),
            "output_dir": str(output_dir),
            
            # Métriques globales
            "success": result["success"],
            "total_steps": metrics.total_steps,
            "successful_steps": metrics.successful_steps,
            "failed_steps": metrics.failed_steps,
            "success_rate": metrics.success_rate,
            
            # Performance
            "total_time_ms": metrics.total_execution_time_ms,
            "total_time_seconds": metrics.total_execution_time_ms / 1000,
            "average_step_time_ms": metrics.average_step_time_ms,
            
            # Coûts
            "total_cost_usd": metrics.total_cost_usd,
            "cost_per_step": metrics.total_cost_usd / metrics.total_steps if metrics.total_steps > 0 else 0,
            
            # Tokens
            "total_tokens": metrics.total_tokens_used,
            "total_input_tokens": metrics.total_input_tokens,
            "total_output_tokens": metrics.total_output_tokens,
            "tokens_per_step": metrics.total_tokens_used / metrics.total_steps if metrics.total_steps > 0 else 0,
            
            # Analyse par provider
            "provider_analysis": provider_analysis,
            
            # Analyse par type
            "type_analysis": type_analysis,
            
            # Détails par étape
            "step_details": [
                {
                    "step_id": step_m["step_id"],
                    "description": step_m["step_description"],
                    "type": step_m["step_type"],
                    "provider": step_m.get("provider"),
                    "success": step_m["success"],
                    "time_ms": step_m["execution_time_ms"],
                    "ttft_ms": step_m.get("ttft_ms"),
                    "ttr_ms": step_m.get("ttr_ms"),
                    "queue_latency_ms": step_m.get("queue_latency_ms"),
                    "network_overhead_ms": step_m.get("network_overhead_ms"),
                    "tokens": step_m["tokens_used"],
                    "cost": step_m["cost_usd"],
                    "cache_hit": step_m.get("cache_hit"),
                    "error": step_m.get("error")
                }
                for step_m in metrics.step_metrics
            ],
            
            # Fichiers générés
            "generated_files": [
                str(output_dir / "step_outputs" / f"{step.id}.txt")
                for step in plan.steps
                if (output_dir / "step_outputs" / f"{step.id}.txt").exists()
            ]
        }
        
        return benchmark_data
        
    except ExecutionError as e:
        console.print(f"[red]✗ Erreur d'exécution: {e}[/]")
        return {
            "task_id": plan_path.stem,
            "success": False,
            "error": str(e),
            "execution_date": datetime.now().isoformat()
        }
    except Exception as e:
        console.print(f"[red]✗ Erreur inattendue: {e}[/]")
        return {
            "task_id": plan_path.stem,
            "success": False,
            "error": str(e),
            "execution_date": datetime.now().isoformat()
        }
    finally:
        await orchestrator.close()


def generate_markdown_report(benchmark_data: Dict[str, Any], output_file: Path) -> None:
    """
    Génère un rapport markdown complet pour Claude Code analyser.
    
    Args:
        benchmark_data: Données de benchmark
        output_file: Fichier de sortie markdown
    """
    md_lines = []
    
    md_lines.append("# Rapport de Benchmark Complet AETHERFLOW\n")
    md_lines.append(f"**Date** : {benchmark_data.get('execution_date', 'N/A')}\n")
    md_lines.append(f"**Tâche** : {benchmark_data.get('task_description', 'N/A')}\n")
    md_lines.append(f"**Task ID** : `{benchmark_data.get('task_id', 'N/A')}`\n")
    md_lines.append("")
    
    # Statut
    success = benchmark_data.get("success", False)
    status_emoji = "✅" if success else "❌"
    md_lines.append(f"## Statut d'Exécution\n\n{status_emoji} **{'Succès' if success else 'Échec'}**\n")
    
    if not success:
        md_lines.append(f"**Erreur** : {benchmark_data.get('error', 'Unknown')}\n")
        md_lines.append("")
        output_file.write_text("\n".join(md_lines), encoding="utf-8")
        return
    
    # Métriques globales
    md_lines.append("## Métriques Globales\n")
    md_lines.append("| Métrique | Valeur |")
    md_lines.append("|----------|--------|")
    md_lines.append(f"| Total étapes | {benchmark_data.get('total_steps', 0)} |")
    md_lines.append(f"| Étapes réussies | {benchmark_data.get('successful_steps', 0)} |")
    md_lines.append(f"| Étapes échouées | {benchmark_data.get('failed_steps', 0)} |")
    md_lines.append(f"| Taux de réussite | {benchmark_data.get('success_rate', 0):.1%} |")
    md_lines.append("")
    
    # Performance
    md_lines.append("## Performance\n")
    md_lines.append("| Métrique | Valeur |")
    md_lines.append("|----------|--------|")
    md_lines.append(f"| Temps total | {benchmark_data.get('total_time_seconds', 0):.2f}s |")
    md_lines.append(f"| Temps moyen par étape | {benchmark_data.get('average_step_time_ms', 0):.0f}ms |")
    md_lines.append("")
    
    # Coûts
    md_lines.append("## Coûts\n")
    md_lines.append("| Métrique | Valeur |")
    md_lines.append("|----------|--------|")
    md_lines.append(f"| Coût total | ${benchmark_data.get('total_cost_usd', 0):.4f} |")
    md_lines.append(f"| Coût par étape | ${benchmark_data.get('cost_per_step', 0):.4f} |")
    md_lines.append("")
    
    # Tokens
    md_lines.append("## Utilisation de Tokens\n")
    md_lines.append("| Métrique | Valeur |")
    md_lines.append("|----------|--------|")
    md_lines.append(f"| Tokens total | {benchmark_data.get('total_tokens', 0):,} |")
    md_lines.append(f"| Tokens input | {benchmark_data.get('total_input_tokens', 0):,} |")
    md_lines.append(f"| Tokens output | {benchmark_data.get('total_output_tokens', 0):,} |")
    md_lines.append(f"| Tokens par étape | {benchmark_data.get('tokens_per_step', 0):.0f} |")
    md_lines.append("")
    
    # Analyse par Provider
    provider_analysis = benchmark_data.get("provider_analysis", {})
    if provider_analysis:
        md_lines.append("## Analyse par Provider\n")
        md_lines.append("| Provider | Étapes | Temps Moyen | Tokens Moyen | Coût Moyen | Taux Succès | TTFT Moyen |")
        md_lines.append("|----------|--------|-------------|--------------|------------|-------------|------------|")
        for provider, stats in provider_analysis.items():
            ttft_str = f"{stats['avg_ttft_ms']:.0f}ms" if stats.get('avg_ttft_ms') else "N/A"
            md_lines.append(
                f"| {provider} | {stats['count']} | {stats['avg_time_ms']:.0f}ms | "
                f"{stats['avg_tokens']:.0f} | ${stats['avg_cost']:.4f} | "
                f"{stats['success_rate']:.1%} | {ttft_str} |"
            )
        md_lines.append("")
    
    # Analyse par Type
    type_analysis = benchmark_data.get("type_analysis", {})
    if type_analysis:
        md_lines.append("## Analyse par Type de Tâche\n")
        md_lines.append("| Type | Étapes | Temps Moyen | Tokens Moyen | Coût Moyen | Taux Succès |")
        md_lines.append("|------|--------|-------------|--------------|------------|-------------|")
        for step_type, stats in type_analysis.items():
            md_lines.append(
                f"| {step_type} | {stats['count']} | {stats['avg_time_ms']:.0f}ms | "
                f"{stats['avg_tokens']:.0f} | ${stats['avg_cost']:.4f} | "
                f"{stats['success_rate']:.1%} |"
            )
        md_lines.append("")
    
    # Détails par étape
    md_lines.append("## Détails par Étape\n")
    for step in benchmark_data.get("step_details", []):
        status = "✅" if step.get("success") else "❌"
        provider = step.get("provider", "N/A")
        md_lines.append(f"### {status} {step.get('step_id', 'N/A')} ({provider})\n")
        md_lines.append(f"- **Description** : {step.get('description', 'N/A')}")
        md_lines.append(f"- **Type** : {step.get('type', 'N/A')}")
        md_lines.append(f"- **Temps** : {step.get('time_ms', 0):.0f}ms")
        if step.get("ttft_ms"):
            md_lines.append(f"- **TTFT** : {step['ttft_ms']:.0f}ms")
        if step.get("ttr_ms"):
            md_lines.append(f"- **TTR** : {step['ttr_ms']:.0f}ms")
        md_lines.append(f"- **Tokens** : {step.get('tokens', 0):,}")
        md_lines.append(f"- **Coût** : ${step.get('cost', 0):.4f}")
        if step.get("cache_hit") is not None:
            cache_status = "✅" if step["cache_hit"] else "❌"
            md_lines.append(f"- **Cache Hit** : {cache_status}")
        if step.get("error"):
            md_lines.append(f"- **Erreur** : {step['error']}")
        md_lines.append("")
    
    # Fichiers générés
    generated_files = benchmark_data.get("generated_files", [])
    if generated_files:
        md_lines.append("## Fichiers Générés\n")
        for file_path in generated_files:
            md_lines.append(f"- `{file_path}`")
        md_lines.append("")
    
    # Analyse pour Claude Code
    md_lines.append("## Analyse pour Claude Code\n")
    md_lines.append("Claude Code, analyse ce rapport et réponds :\n")
    md_lines.append("1. **Qualité** : Le code généré est-il de bonne qualité ?")
    md_lines.append("2. **Performance** : Les temps d'exécution sont-ils acceptables ?")
    md_lines.append("3. **Coûts** : Les coûts sont-ils dans les objectifs (< $0.50 par tâche) ?")
    md_lines.append("4. **Latence** : Les métriques TTFT/TTR sont-elles acceptables ?")
    md_lines.append("5. **Providers** : Y a-t-il des différences significatives entre providers ?")
    md_lines.append("6. **Améliorations** : Quelles améliorations suggères-tu ?")
    md_lines.append("")
    
    # Écrire le fichier
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(md_lines), encoding="utf-8")
    console.print(f"[green]✓ Rapport généré: {output_file}[/]")


def print_summary_table(benchmark_data: Dict[str, Any]) -> None:
    """Affiche un tableau récapitulatif dans le terminal."""
    if not benchmark_data.get("success"):
        return
    
    table = Table(title="Résumé du Benchmark", box=box.ROUNDED)
    table.add_column("Métrique", style="cyan")
    table.add_column("Valeur", style="green")
    
    table.add_row("Temps total", f"{benchmark_data.get('total_time_seconds', 0):.2f}s")
    table.add_row("Coût total", f"${benchmark_data.get('total_cost_usd', 0):.4f}")
    table.add_row("Tokens total", f"{benchmark_data.get('total_tokens', 0):,}")
    table.add_row("Taux de succès", f"{benchmark_data.get('success_rate', 0):.1%}")
    
    # Table par provider
    provider_analysis = benchmark_data.get("provider_analysis", {})
    if provider_analysis:
        provider_table = Table(title="Performance par Provider", box=box.ROUNDED)
        provider_table.add_column("Provider", style="cyan")
        provider_table.add_column("Étapes", style="yellow")
        provider_table.add_column("Temps Moyen", style="green")
        provider_table.add_column("Coût Moyen", style="magenta")
        provider_table.add_column("Succès", style="green")
        
        for provider, stats in provider_analysis.items():
            provider_table.add_row(
                provider,
                str(stats['count']),
                f"{stats['avg_time_ms']:.0f}ms",
                f"${stats['avg_cost']:.4f}",
                f"{stats['success_rate']:.1%}"
            )
        
        console.print("\n")
        console.print(table)
        console.print("\n")
        console.print(provider_table)
    else:
        console.print("\n")
        console.print(table)


async def main():
    """Point d'entrée principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Benchmark Complet AETHERFLOW")
    parser.add_argument("--plan", type=Path, required=True, help="Chemin vers le plan JSON")
    parser.add_argument("--output", type=Path, default=None, help="Répertoire de sortie")
    parser.add_argument("--report", type=Path, default=None, help="Fichier de rapport markdown")
    
    args = parser.parse_args()
    
    console.print(Panel.fit(
        "[bold cyan]AETHERFLOW Benchmark Complet[/]\n"
        "[dim]Métriques de latence et comparaisons providers[/]",
        border_style="cyan"
    ))
    
    # Déterminer les chemins
    plan_path = args.plan
    if not plan_path.exists():
        console.print(f"[red]Erreur: Plan non trouvé: {plan_path}[/]")
        sys.exit(1)
    
    output_dir = args.output or Path("output") / "benchmark" / plan_path.stem
    report_file = args.report or output_dir / "benchmark_report.md"
    
    # Exécuter le benchmark
    benchmark_data = await benchmark_plan(plan_path, output_dir)
    
    # Afficher résumé
    print_summary_table(benchmark_data)
    
    # Générer le rapport
    if benchmark_data.get("success"):
        generate_markdown_report(benchmark_data, report_file)
        
        # Sauvegarder aussi en JSON
        json_file = output_dir / "benchmark_data.json"
        json_file.parent.mkdir(parents=True, exist_ok=True)
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(benchmark_data, f, indent=2, ensure_ascii=False)
        
        console.print(f"\n[green]✓ Benchmark terminé[/]")
        console.print(f"  Rapport: {report_file}")
        console.print(f"  Données: {json_file}")
    else:
        console.print(f"\n[red]✗ Benchmark échoué[/]")
        console.print(f"  Erreur: {benchmark_data.get('error', 'Unknown')}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
