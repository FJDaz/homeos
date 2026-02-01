#!/usr/bin/env python3
"""Benchmark méta : Tester AETHERFLOW 0.1 pour construire AETHERFLOW 0.2 (Codestral).

Ce script mesure les performances de l'association Claude Code + DeepSeek
pour implémenter CodestralClient (Phase 2.1).
"""
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Backend.Prod.orchestrator import Orchestrator, ExecutionError
from Backend.Prod.plan_reader import PlanReader, PlanValidationError

console = Console()


async def benchmark_codestral_implementation(plan_path: Path, output_dir: Path) -> Dict[str, Any]:
    """
    Exécute le plan d'implémentation de Codestral et collecte les métriques.
    
    Args:
        plan_path: Chemin vers le plan JSON
        output_dir: Répertoire de sortie
        
    Returns:
        Dictionnaire avec toutes les métriques
    """
    console.print(Panel.fit(
        "[bold cyan]AETHERFLOW 0.1 → AETHERFLOW 0.2[/]\n"
        "[dim]Benchmark méta : Claude Code + DeepSeek construisent Codestral[/]",
        border_style="cyan"
    ))
    
    console.print(f"\n[cyan]📊 Exécution du plan: {plan_path.name}[/]")
    
    orchestrator = Orchestrator()
    
    try:
        # Exécuter le plan
        start_time = datetime.now()
        result = await orchestrator.execute_plan(
            plan_path=plan_path,
            output_dir=output_dir
        )
        end_time = datetime.now()
        
        metrics = result["metrics"]
        plan = result["plan"]
        
        # Calculer le temps total (incluant overhead)
        total_wall_time = (end_time - start_time).total_seconds() * 1000
        
        # Collecter les métriques détaillées
        benchmark_data = {
            "benchmark_type": "meta_benchmark",
            "benchmark_description": "AETHERFLOW 0.1 (Claude Code + DeepSeek) construit AETHERFLOW 0.2 (Codestral)",
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
            "total_execution_time_ms": metrics.total_execution_time_ms,
            "total_wall_time_ms": total_wall_time,
            "overhead_ms": total_wall_time - metrics.total_execution_time_ms,
            "average_step_time_ms": metrics.average_step_time_ms,
            
            # Coûts
            "total_cost_usd": metrics.total_cost_usd,
            "cost_per_step": metrics.total_cost_usd / metrics.total_steps if metrics.total_steps > 0 else 0,
            
            # Tokens
            "total_tokens": metrics.total_tokens_used,
            "total_input_tokens": metrics.total_input_tokens,
            "total_output_tokens": metrics.total_output_tokens,
            "tokens_per_step": metrics.total_tokens_used / metrics.total_steps if metrics.total_steps > 0 else 0,
            
            # Détails par étape
            "step_details": [
                {
                    "step_id": step_m["step_id"],
                    "description": step_m["step_description"],
                    "type": step_m["step_type"],
                    "complexity": next(
                        (s.complexity for s in plan.steps if s.id == step_m["step_id"]),
                        0.0
                    ),
                    "success": step_m["success"],
                    "time_ms": step_m["execution_time_ms"],
                    "tokens": step_m["tokens_used"],
                    "cost": step_m["cost_usd"],
                    "error": step_m.get("error")
                }
                for step_m in metrics.step_metrics
            ],
            
            # Fichiers générés
            "generated_files": [
                str(output_dir / "step_outputs" / f"{step.id}.txt")
                for step in plan.steps
                if (output_dir / "step_outputs" / f"{step.id}.txt").exists()
            ],
            
            # Métriques spécifiques au benchmark méta
            "meta_metrics": {
                "self_hosting_success": result["success"],
                "code_quality": "to_be_evaluated",  # À évaluer manuellement
                "implementation_completeness": metrics.success_rate,
                "cost_efficiency": metrics.total_cost_usd,
                "time_efficiency_ms": metrics.total_execution_time_ms
            }
        }
        
        return benchmark_data
        
    except ExecutionError as e:
        console.print(f"[red]✗ Erreur d'exécution: {e}[/]")
        return {
            "benchmark_type": "meta_benchmark",
            "task_id": plan_path.stem,
            "success": False,
            "error": str(e),
            "execution_date": datetime.now().isoformat()
        }
    except Exception as e:
        console.print(f"[red]✗ Erreur inattendue: {e}[/]")
        return {
            "benchmark_type": "meta_benchmark",
            "task_id": plan_path.stem,
            "success": False,
            "error": str(e),
            "execution_date": datetime.now().isoformat()
        }
    finally:
        await orchestrator.close()


def generate_markdown_report(benchmark_data: Dict[str, Any], output_file: Path) -> None:
    """
    Génère un rapport markdown pour analyser le benchmark méta.
    
    Args:
        benchmark_data: Données de benchmark
        output_file: Fichier de sortie markdown
    """
    md_lines = []
    
    md_lines.append("# Rapport de Benchmark Méta - AETHERFLOW 0.1 → 0.2\n")
    md_lines.append(f"**Date** : {benchmark_data.get('execution_date', 'N/A')}\n")
    md_lines.append(f"**Type** : Benchmark méta (self-hosting)\n")
    md_lines.append(f"**Description** : {benchmark_data.get('benchmark_description', 'N/A')}\n")
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
    md_lines.append(f"| Temps d'exécution total | {benchmark_data.get('total_execution_time_ms', 0) / 1000:.2f}s |")
    md_lines.append(f"| Temps wall-clock total | {benchmark_data.get('total_wall_time_ms', 0) / 1000:.2f}s |")
    md_lines.append(f"| Overhead | {benchmark_data.get('overhead_ms', 0) / 1000:.2f}s |")
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
    
    # Détails par étape
    md_lines.append("## Détails par Étape\n")
    for step in benchmark_data.get("step_details", []):
        status = "✅" if step.get("success") else "❌"
        complexity = step.get("complexity", 0.0)
        md_lines.append(f"### {status} {step.get('step_id', 'N/A')} (complexity: {complexity:.2f})\n")
        md_lines.append(f"- **Description** : {step.get('description', 'N/A')}")
        md_lines.append(f"- **Type** : {step.get('type', 'N/A')}")
        md_lines.append(f"- **Temps** : {step.get('time_ms', 0):.0f}ms")
        md_lines.append(f"- **Tokens** : {step.get('tokens', 0):,}")
        md_lines.append(f"- **Coût** : ${step.get('cost', 0):.4f}")
        if step.get("error"):
            md_lines.append(f"- **Erreur** : {step['error']}")
        md_lines.append("")
    
    # Métriques méta
    meta_metrics = benchmark_data.get("meta_metrics", {})
    md_lines.append("## Métriques Méta (Self-Hosting)\n")
    md_lines.append("| Métrique | Valeur |")
    md_lines.append("|----------|--------|")
    md_lines.append(f"| Succès self-hosting | {'✅' if meta_metrics.get('self_hosting_success') else '❌'} |")
    md_lines.append(f"| Complétude implémentation | {meta_metrics.get('implementation_completeness', 0):.1%} |")
    md_lines.append(f"| Efficacité coût | ${meta_metrics.get('cost_efficiency', 0):.4f} |")
    md_lines.append(f"| Efficacité temps | {meta_metrics.get('time_efficiency_ms', 0) / 1000:.2f}s |")
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
    md_lines.append("Claude Code, analyse ce benchmark méta et réponds :\n")
    md_lines.append("1. **Self-Hosting** : AETHERFLOW a-t-il réussi à se construire lui-même ?")
    md_lines.append("2. **Qualité du code généré** : Le code de CodestralClient est-il de bonne qualité ?")
    md_lines.append("3. **Performance** : Les temps d'exécution sont-ils acceptables ?")
    md_lines.append("4. **Coûts** : Les coûts sont-ils raisonnables pour cette tâche complexe ?")
    md_lines.append("5. **Efficacité** : AETHERFLOW est-il efficace pour construire ses propres composants ?")
    md_lines.append("6. **Améliorations** : Quelles améliorations suggères-tu pour AETHERFLOW ?")
    md_lines.append("")
    
    # Écrire le fichier
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(md_lines), encoding="utf-8")
    console.print(f"[green]✓ Rapport généré: {output_file}[/]")


def print_summary_table(benchmark_data: Dict[str, Any]) -> None:
    """Affiche un tableau récapitulatif dans la console."""
    table = Table(title="Résumé du Benchmark Méta", box=box.ROUNDED)
    table.add_column("Métrique", style="cyan")
    table.add_column("Valeur", style="green")
    
    success = benchmark_data.get("success", False)
    table.add_row("Statut", "✅ Succès" if success else "❌ Échec")
    table.add_row("Étapes réussies", f"{benchmark_data.get('successful_steps', 0)}/{benchmark_data.get('total_steps', 0)}")
    table.add_row("Temps total", f"{benchmark_data.get('total_execution_time_ms', 0) / 1000:.2f}s")
    table.add_row("Coût total", f"${benchmark_data.get('total_cost_usd', 0):.4f}")
    table.add_row("Tokens total", f"{benchmark_data.get('total_tokens', 0):,}")
    
    console.print("\n")
    console.print(table)


async def main():
    """Point d'entrée principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Benchmark méta : AETHERFLOW 0.1 construit AETHERFLOW 0.2 (Codestral)"
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=Path("Backend/Notebooks/benchmark_tasks/task_10_phase2_codestral_implementation.json"),
        help="Chemin vers le plan JSON (défaut: task_10_phase2_codestral_implementation.json)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Répertoire de sortie (défaut: output/benchmark_meta_codestral)"
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Fichier de rapport markdown (défaut: output_dir/benchmark_report.md)"
    )
    
    args = parser.parse_args()
    
    # Déterminer les chemins
    plan_path = args.plan
    if not plan_path.exists():
        console.print(f"[red]Erreur: Plan non trouvé: {plan_path}[/]")
        sys.exit(1)
    
    output_dir = args.output or Path("output") / "benchmark_meta_codestral"
    report_file = args.report or output_dir / "benchmark_report.md"
    
    # Exécuter le benchmark
    benchmark_data = await benchmark_codestral_implementation(plan_path, output_dir)
    
    # Afficher le résumé
    if benchmark_data.get("success"):
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
