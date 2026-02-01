#!/usr/bin/env python3
"""Script de suite de benchmarks pour comparaisons avant/après optimisations."""
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import defaultdict
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.benchmark_comprehensive import benchmark_plan, generate_markdown_report

console = Console()


async def run_benchmark_suite(
    plans: List[Path],
    output_base_dir: Path,
    baseline_label: str = "baseline",
    optimized_label: str = "optimized"
) -> Dict[str, Any]:
    """
    Exécute une suite de benchmarks et compare les résultats.
    
    Args:
        plans: Liste des plans à exécuter
        output_base_dir: Répertoire de base pour les résultats
        baseline_label: Label pour les résultats baseline
        optimized_label: Label pour les résultats optimisés
        
    Returns:
        Dictionnaire avec comparaisons
    """
    console.print(Panel.fit(
        f"[bold cyan]Suite de Benchmarks AETHERFLOW[/]\n"
        f"[dim]{len(plans)} plans à exécuter[/]",
        border_style="cyan"
    ))
    
    all_results = []
    
    for plan_path in plans:
        if not plan_path.exists():
            console.print(f"[yellow]⚠ Plan non trouvé: {plan_path}, ignoré[/]")
            continue
        
        console.print(f"\n[cyan]📊 Exécution: {plan_path.name}[/]")
        
        # Exécuter benchmark
        output_dir = output_base_dir / plan_path.stem
        benchmark_data = await benchmark_plan(plan_path, output_dir)
        
        if benchmark_data.get("success"):
            all_results.append(benchmark_data)
            console.print(f"[green]✓ {plan_path.name} terminé[/]")
        else:
            console.print(f"[red]✗ {plan_path.name} échoué[/]")
    
    # Analyser les résultats
    comparison = analyze_results(all_results)
    
    # Générer rapport de comparaison
    comparison_report = output_base_dir / "comparison_report.md"
    generate_comparison_report(comparison, comparison_report, baseline_label, optimized_label)
    
    # Sauvegarder données JSON
    comparison_json = output_base_dir / "comparison_data.json"
    with open(comparison_json, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)
    
    console.print(f"\n[green]✓ Suite de benchmarks terminée[/]")
    console.print(f"  Rapport: {comparison_report}")
    console.print(f"  Données: {comparison_json}")
    
    return comparison


def analyze_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyse et compare les résultats de plusieurs benchmarks.
    
    Args:
        results: Liste des résultats de benchmarks
        
    Returns:
        Dictionnaire avec analyses et comparaisons
    """
    if not results:
        return {"error": "Aucun résultat à analyser"}
    
    # Agrégation globale
    total_steps = sum(r.get("total_steps", 0) for r in results)
    total_time = sum(r.get("total_time_ms", 0) for r in results)
    total_cost = sum(r.get("total_cost_usd", 0) for r in results)
    total_tokens = sum(r.get("total_tokens", 0) for r in results)
    successful_results = [r for r in results if r.get("success")]
    success_rate = len(successful_results) / len(results) if results else 0
    
    # Analyse par provider (agrégée)
    provider_stats = defaultdict(lambda: {
        "count": 0,
        "total_time_ms": 0.0,
        "total_tokens": 0,
        "total_cost": 0.0,
        "success_count": 0
    })
    
    for result in successful_results:
        provider_analysis = result.get("provider_analysis", {})
        for provider, stats in provider_analysis.items():
            provider_stats[provider]["count"] += stats["count"]
            provider_stats[provider]["total_time_ms"] += stats["total_time_ms"]
            provider_stats[provider]["total_tokens"] += stats["total_tokens"]
            provider_stats[provider]["total_cost"] += stats["total_cost"]
            provider_stats[provider]["success_count"] += int(stats["success_rate"] * stats["count"])
    
    # Calculer moyennes par provider
    provider_comparison = {}
    for provider, stats in provider_stats.items():
        count = stats["count"]
        provider_comparison[provider] = {
            "total_steps": count,
            "avg_time_ms": stats["total_time_ms"] / count if count > 0 else 0,
            "avg_tokens": stats["total_tokens"] / count if count > 0 else 0,
            "avg_cost": stats["total_cost"] / count if count > 0 else 0,
            "success_rate": stats["success_count"] / count if count > 0 else 0,
            "total_time_ms": stats["total_time_ms"],
            "total_tokens": stats["total_tokens"],
            "total_cost": stats["total_cost"]
        }
    
    # Analyse par type (agrégée)
    type_stats = defaultdict(lambda: {
        "count": 0,
        "total_time_ms": 0.0,
        "total_tokens": 0,
        "total_cost": 0.0,
        "success_count": 0
    })
    
    for result in successful_results:
        type_analysis = result.get("type_analysis", {})
        for step_type, stats in type_analysis.items():
            type_stats[step_type]["count"] += stats["count"]
            type_stats[step_type]["total_time_ms"] += stats["total_time_ms"]
            type_stats[step_type]["total_tokens"] += stats["total_tokens"]
            type_stats[step_type]["total_cost"] += stats["total_cost"]
            type_stats[step_type]["success_count"] += int(stats["success_rate"] * stats["count"])
    
    # Calculer moyennes par type
    type_comparison = {}
    for step_type, stats in type_stats.items():
        count = stats["count"]
        type_comparison[step_type] = {
            "total_steps": count,
            "avg_time_ms": stats["total_time_ms"] / count if count > 0 else 0,
            "avg_tokens": stats["total_tokens"] / count if count > 0 else 0,
            "avg_cost": stats["total_cost"] / count if count > 0 else 0,
            "success_rate": stats["success_count"] / count if count > 0 else 0
        }
    
    return {
        "execution_date": datetime.now().isoformat(),
        "total_plans": len(results),
        "successful_plans": len(successful_results),
        "success_rate": success_rate,
        
        # Métriques agrégées
        "aggregated_metrics": {
            "total_steps": total_steps,
            "total_time_ms": total_time,
            "total_time_seconds": total_time / 1000,
            "total_cost_usd": total_cost,
            "total_tokens": total_tokens,
            "avg_time_per_step_ms": total_time / total_steps if total_steps > 0 else 0,
            "avg_cost_per_step": total_cost / total_steps if total_steps > 0 else 0,
            "avg_tokens_per_step": total_tokens / total_steps if total_steps > 0 else 0
        },
        
        # Comparaison par provider
        "provider_comparison": provider_comparison,
        
        # Comparaison par type
        "type_comparison": type_comparison,
        
        # Résultats individuels
        "individual_results": [
            {
                "task_id": r.get("task_id"),
                "task_description": r.get("task_description"),
                "success": r.get("success"),
                "total_steps": r.get("total_steps", 0),
                "total_time_ms": r.get("total_time_ms", 0),
                "total_cost_usd": r.get("total_cost_usd", 0),
                "total_tokens": r.get("total_tokens", 0),
                "success_rate": r.get("success_rate", 0)
            }
            for r in results
        ]
    }


def generate_comparison_report(
    comparison: Dict[str, Any],
    output_file: Path,
    baseline_label: str,
    optimized_label: str
) -> None:
    """
    Génère un rapport de comparaison markdown.
    
    Args:
        comparison: Données de comparaison
        output_file: Fichier de sortie
        baseline_label: Label baseline
        optimized_label: Label optimisé
    """
    md_lines = []
    
    md_lines.append("# Rapport de Comparaison - Suite de Benchmarks AETHERFLOW\n")
    md_lines.append(f"**Date** : {comparison.get('execution_date', 'N/A')}\n")
    md_lines.append("")
    
    # Résumé global
    md_lines.append("## Résumé Global\n")
    md_lines.append("| Métrique | Valeur |")
    md_lines.append("|----------|--------|")
    md_lines.append(f"| Plans exécutés | {comparison.get('total_plans', 0)} |")
    md_lines.append(f"| Plans réussis | {comparison.get('successful_plans', 0)} |")
    md_lines.append(f"| Taux de succès | {comparison.get('success_rate', 0):.1%} |")
    md_lines.append("")
    
    # Métriques agrégées
    agg = comparison.get("aggregated_metrics", {})
    md_lines.append("## Métriques Agrégées\n")
    md_lines.append("| Métrique | Valeur |")
    md_lines.append("|----------|--------|")
    md_lines.append(f"| Total étapes | {agg.get('total_steps', 0)} |")
    md_lines.append(f"| Temps total | {agg.get('total_time_seconds', 0):.2f}s |")
    md_lines.append(f"| Coût total | ${agg.get('total_cost_usd', 0):.4f} |")
    md_lines.append(f"| Tokens total | {agg.get('total_tokens', 0):,} |")
    md_lines.append(f"| Temps moyen par étape | {agg.get('avg_time_per_step_ms', 0):.0f}ms |")
    md_lines.append(f"| Coût moyen par étape | ${agg.get('avg_cost_per_step', 0):.4f} |")
    md_lines.append(f"| Tokens moyen par étape | {agg.get('avg_tokens_per_step', 0):.0f} |")
    md_lines.append("")
    
    # Comparaison par provider
    provider_comp = comparison.get("provider_comparison", {})
    if provider_comp:
        md_lines.append("## Comparaison par Provider\n")
        md_lines.append("| Provider | Étapes | Temps Moyen | Tokens Moyen | Coût Moyen | Taux Succès |")
        md_lines.append("|----------|--------|-------------|--------------|------------|-------------|")
        for provider, stats in sorted(provider_comp.items()):
            md_lines.append(
                f"| {provider} | {stats['total_steps']} | {stats['avg_time_ms']:.0f}ms | "
                f"{stats['avg_tokens']:.0f} | ${stats['avg_cost']:.4f} | "
                f"{stats['success_rate']:.1%} |"
            )
        md_lines.append("")
    
    # Comparaison par type
    type_comp = comparison.get("type_comparison", {})
    if type_comp:
        md_lines.append("## Comparaison par Type de Tâche\n")
        md_lines.append("| Type | Étapes | Temps Moyen | Tokens Moyen | Coût Moyen | Taux Succès |")
        md_lines.append("|------|--------|-------------|--------------|------------|-------------|")
        for step_type, stats in sorted(type_comp.items()):
            md_lines.append(
                f"| {step_type} | {stats['total_steps']} | {stats['avg_time_ms']:.0f}ms | "
                f"{stats['avg_tokens']:.0f} | ${stats['avg_cost']:.4f} | "
                f"{stats['success_rate']:.1%} |"
            )
        md_lines.append("")
    
    # Résultats individuels
    md_lines.append("## Résultats Individuels\n")
    for result in comparison.get("individual_results", []):
        status = "✅" if result.get("success") else "❌"
        md_lines.append(f"### {status} {result.get('task_id', 'N/A')}\n")
        md_lines.append(f"- **Description** : {result.get('task_description', 'N/A')}")
        md_lines.append(f"- **Étapes** : {result.get('total_steps', 0)}")
        md_lines.append(f"- **Temps** : {result.get('total_time_ms', 0) / 1000:.2f}s")
        md_lines.append(f"- **Coût** : ${result.get('total_cost_usd', 0):.4f}")
        md_lines.append(f"- **Tokens** : {result.get('total_tokens', 0):,}")
        md_lines.append(f"- **Taux de succès** : {result.get('success_rate', 0):.1%}")
        md_lines.append("")
    
    # Écrire le fichier
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(md_lines), encoding="utf-8")
    console.print(f"[green]✓ Rapport de comparaison généré: {output_file}[/]")


async def main():
    """Point d'entrée principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Suite de Benchmarks AETHERFLOW")
    parser.add_argument(
        "--plans",
        type=Path,
        nargs="+",
        required=True,
        help="Chemins vers les plans JSON à exécuter"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output") / "benchmark_suite",
        help="Répertoire de sortie"
    )
    parser.add_argument(
        "--baseline-label",
        type=str,
        default="baseline",
        help="Label pour résultats baseline"
    )
    parser.add_argument(
        "--optimized-label",
        type=str,
        default="optimized",
        help="Label pour résultats optimisés"
    )
    
    args = parser.parse_args()
    
    # Exécuter la suite
    comparison = await run_benchmark_suite(
        plans=args.plans,
        output_base_dir=args.output,
        baseline_label=args.baseline_label,
        optimized_label=args.optimized_label
    )
    
    # Afficher tableau récapitulatif
    if comparison.get("success_rate") is not None:
        table = Table(title="Résumé de la Suite", box=box.ROUNDED)
        table.add_column("Métrique", style="cyan")
        table.add_column("Valeur", style="green")
        
        agg = comparison.get("aggregated_metrics", {})
        table.add_row("Plans réussis", f"{comparison.get('successful_plans', 0)}/{comparison.get('total_plans', 0)}")
        table.add_row("Temps total", f"{agg.get('total_time_seconds', 0):.2f}s")
        table.add_row("Coût total", f"${agg.get('total_cost_usd', 0):.4f}")
        table.add_row("Tokens total", f"{agg.get('total_tokens', 0):,}")
        
        console.print("\n")
        console.print(table)


if __name__ == "__main__":
    asyncio.run(main())
