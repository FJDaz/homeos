"""Command-line interface for AetherFlow."""
import asyncio
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich import box
from loguru import logger

from .orchestrator import Orchestrator, ExecutionError
from .models.plan_reader import PlanValidationError
from .config.settings import settings


console = Console()


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    log_level = "DEBUG" if verbose else "INFO"
    
    # Remove default handler
    logger.remove()
    
    # Add console handler with colors
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=log_level,
        colorize=True
    )
    
    # Add file handler
    log_file = settings.logs_dir / "aetherflow.log"
    logger.add(
        log_file,
        rotation="10 MB",
        retention="7 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}"
    )


def print_header() -> None:
    """Print application header."""
    header = Panel.fit(
        "[bold cyan]AetherFlow[/] - Orchestrateur d'Agents IA\n"
        "[dim]Claude Code → DeepSeek API[/]",
        border_style="cyan"
    )
    console.print(header)


def display_pedagogical_feedback(validation_details: List[Dict[str, Any]]) -> None:
    """
    Display pedagogical feedback with Rich formatting.
    
    Args:
        validation_details: List of validation details with optional pedagogical_feedback
    """
    from .models.feedback_parser import PedagogicalFeedback
    
    for detail in validation_details:
        step_id = detail.get("step_id", "unknown")
        pedagogical = detail.get("pedagogical_feedback")
        
        if not pedagogical:
            continue
        
        # Create PedagogicalFeedback from dict
        try:
            feedback = PedagogicalFeedback(
                is_valid=pedagogical.get("is_valid", True),
                score=pedagogical.get("score", 1.0),
                passed_rules=pedagogical.get("passed_rules", []),
                violations=[],  # Will be populated below
                overall_feedback=pedagogical.get("overall_feedback", "")
            )
            
            # Convert violations
            from .models.feedback_parser import RuleViolation
            for v_data in pedagogical.get("violations", []):
                violation = RuleViolation(
                    rule=v_data.get("rule", ""),
                    location=v_data.get("location", ""),
                    issue=v_data.get("issue", ""),
                    explanation=v_data.get("explanation", ""),
                    suggestion=v_data.get("suggestion", ""),
                    code_reference=v_data.get("code_reference")
                )
                feedback.violations.append(violation)
        except Exception as e:
            logger.warning(f"Failed to parse pedagogical feedback for {step_id}: {e}")
            continue
        
        # Display feedback
        status = "✅ Validation Passed" if feedback.is_valid else "❌ Validation Failed"
        status_style = "green" if feedback.is_valid else "red"
        console.print(Panel(status, title=f"Step {step_id}", style=status_style))
        
        # Score
        console.print(f"\n[bold]Score:[/bold] {feedback.score:.1%}")
        
        # Passed rules
        if feedback.passed_rules:
            console.print("\n[bold green]✅ Rules Passed:[/bold green]")
            for rule in feedback.passed_rules:
                console.print(f"  • {rule}")
        
        # Violations
        if feedback.violations:
            console.print("\n[bold red]❌ Rule Violations:[/bold red]")
            violations_table = Table(box=box.ROUNDED)
            violations_table.add_column("Rule", style="yellow", width=15)
            violations_table.add_column("Location", style="cyan", width=20)
            violations_table.add_column("Issue", style="red", width=40)
            violations_table.add_column("Fix", style="green", width=40)
            
            for violation in feedback.violations:
                violations_table.add_row(
                    violation.rule,
                    violation.location[:20] + "..." if len(violation.location) > 20 else violation.location,
                    violation.issue[:40] + "..." if len(violation.issue) > 40 else violation.issue,
                    violation.suggestion[:40] + "..." if len(violation.suggestion) > 40 else violation.suggestion
                )
            
            console.print(violations_table)
            
            # Detailed violations with code references
            for violation in feedback.violations:
                console.print(f"\n[bold yellow]{violation.rule}[/bold yellow] - {violation.location}")
                console.print(f"  [red]Issue:[/red] {violation.issue}")
                console.print(f"  [yellow]Why:[/yellow] {violation.explanation}")
                console.print(f"  [green]Fix:[/green] {violation.suggestion}")
                if violation.code_reference:
                    console.print(f"  [dim]Code Reference:[/dim]\n```\n{violation.code_reference}\n```")


def print_plan_info(plan_path: Path) -> None:
    """Print information about the plan."""
    from .plan_reader import PlanReader
    
    try:
        reader = PlanReader()
        plan = reader.read(plan_path)
        
        table = Table(title="Plan Information", box=box.ROUNDED)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Task ID", plan.task_id)
        table.add_row("Description", plan.description)
        table.add_row("Total Steps", str(len(plan.steps)))
        table.add_row("Created At", plan.metadata.get("created_at", "N/A"))
        table.add_row("Planner Used", plan.metadata.get("planner_used", plan.metadata.get("planner", "claude_code")))
        
        console.print(table)
        
        # Show steps
        steps_table = Table(title="Steps", box=box.ROUNDED)
        steps_table.add_column("ID", style="cyan")
        steps_table.add_column("Type", style="yellow")
        steps_table.add_column("Complexity", style="magenta")
        steps_table.add_column("Description", style="white")
        
        for step in plan.steps:
            steps_table.add_row(
                step.id,
                step.type,
                f"{step.complexity:.2f}",
                step.description[:60] + "..." if len(step.description) > 60 else step.description
            )
        
        console.print(steps_table)
        
    except Exception as e:
        console.print(f"[red]Error reading plan: {e}[/]")


async def execute_plan_async(
    plan_path: Path,
    output_dir: Optional[Path],
    context: Optional[str],
    verbose: bool,
    execution_mode: Optional[str] = None,
    use_streaming: bool = False
) -> int:
    """Execute plan asynchronously."""
    orchestrator = Orchestrator(execution_mode=execution_mode or "BUILD")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Executing plan...", total=None)
            
            result = await orchestrator.execute_plan(
                plan_path=plan_path,
                output_dir=output_dir,
                context=context,
                use_streaming=use_streaming,
                execution_mode=execution_mode
            )
            
            progress.update(task, completed=True)
        
        # Print results summary
        metrics = result["metrics"]
        
        summary_table = Table(title="Execution Summary", box=box.ROUNDED)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")
        
        summary_table.add_row("Success Rate", f"{metrics.success_rate:.1%}")
        summary_table.add_row("Total Steps", str(metrics.total_steps))
        summary_table.add_row("Successful", str(metrics.successful_steps))
        summary_table.add_row("Failed", str(metrics.failed_steps))
        summary_table.add_row("Total Time", f"{metrics.total_execution_time_ms/1000:.2f}s")
        summary_table.add_row("Total Tokens", f"{metrics.total_tokens_used:,}")
        summary_table.add_row("Total Cost", f"${metrics.total_cost_usd:.4f}")
        
        # Show planner if available in plan
        try:
            from .plan_reader import PlanReader
            plan_reader = PlanReader()
            plan = plan_reader.read(plan_path)
            planner_used = plan.metadata.get("planner_used", plan.metadata.get("planner", "claude_code"))
            summary_table.add_row("Planner", planner_used)
        except Exception:
            pass  # Ignore if can't read plan
        
        console.print(summary_table)
        
        if output_dir:
            console.print(f"\n[green]✓ Results saved to: {output_dir}[/]")
        
        return 0 if result["success"] else 1
        
    except ExecutionError as e:
        console.print(f"[red]Execution failed: {e}[/]")
        return 1
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/]")
        if verbose:
            logger.exception("Unexpected error")
        return 1
    finally:
        await orchestrator.close()


def print_cache_stats() -> None:
    """Print cache statistics."""
    from ..cache import SemanticCache
    
    try:
        cache = SemanticCache()
        summary = cache.get_cache_summary()
        
        table = Table(title="Cache Statistics", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Entries", str(summary["total_entries"]))
        table.add_row("Cache Hit Rate", f"{summary['cache_hit_rate']:.1f}%")
        table.add_row("Total Requests", str(summary["total_requests"]))
        table.add_row("Cache Hits", str(summary["cache_hits"]))
        table.add_row("Cache Misses", str(summary["cache_misses"]))
        table.add_row("Avg Similarity", f"{summary['avg_similarity']:.3f}")
        table.add_row("Tokens Saved", f"{summary['tokens_saved']:,}")
        table.add_row("Cost Saved", f"${summary['cost_saved_usd']:.4f}")
        
        if summary.get("entries_by_namespace"):
            table.add_row("", "")
            table.add_row("[bold]Entries by Namespace[/bold]", "")
            for ns, count in summary["entries_by_namespace"].items():
                table.add_row(f"  {ns}", str(count))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error reading cache stats: {e}[/]")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AetherFlow - Orchestrateur d'Agents IA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --plan plan.json
  %(prog)s -q --plan plan.json              # Quick: prototype (FAST then validate)
  %(prog)s -f --plan plan.json              # Full: quality (FAST → BUILD → validate)
  %(prog)s -vfx --plan plan.json             # Verify & fix: run plan, validate, then correct errors
  %(prog)s --workflow quick --plan plan.json # Same as -q
  %(prog)s --workflow full --plan plan.json  # Same as -f
  %(prog)s --workflow verify-fix --plan plan.json  # Same as -vfx / --verify-fix
  %(prog)s -rfx --command "cd frontend-svelte && npm run build"  # Run-and-fix
  %(prog)s --stats                           # Cache statistics
  %(prog)s --status                          # Plan monitoring (current or last run)
        """
    )
    
    # Workflow flags (mutually exclusive)
    workflow_group = parser.add_mutually_exclusive_group()
    workflow_group.add_argument(
        "--fast",
        action="store_true",
        help="PROTO workflow: Fast prototyping (FAST → DOUBLE-CHECK) [DEPRECATED: use -q or --workflow quick]"
    )
    workflow_group.add_argument(
        "--build",
        action="store_true",
        help="PROD workflow: Quality-first (FAST draft → BUILD refactor → DOUBLE-CHECK) [DEPRECATED: use -f or --workflow full]"
    )
    workflow_group.add_argument(
        "-q",
        "--quick",
        action="store_true",
        dest="quick",
        help="Quick workflow: Fast prototyping (FAST → DOUBLE-CHECK) [alias for PROTO]"
    )
    workflow_group.add_argument(
        "-f",
        "--full",
        action="store_true",
        dest="full",
        help="Full workflow: Quality-first (FAST draft → BUILD refactor → validate)"
    )
    workflow_group.add_argument(
        "-vfx",
        "--verify-fix",
        action="store_true",
        dest="verify_fix",
        help="Verify & fix: Run plan, validate with Gemini, then correct reported errors and re-validate"
    )
    workflow_group.add_argument(
        "-rfx",
        "--run-and-fix-workflow",
        action="store_true",
        dest="run_and_fix_workflow",
        help="Run-and-fix: Run command (build/deploy), on failure fix from stderr and retry. Requires --command."
    )
    workflow_group.add_argument(
        "--stats",
        action="store_true",
        help="Show cache statistics and exit"
    )
    workflow_group.add_argument(
        "--costs",
        action="store_true",
        help="Show cumulative API costs and exit"
    )
    workflow_group.add_argument(
        "--usage",
        action="store_true",
        help="Show Claude Code / Cursor usage only (tokens, cost, sessions)"
    )
    workflow_group.add_argument(
        "--status",
        action="store_true",
        dest="plan_status",
        help="Show current or last plan execution status (monitoring)"
    )
    
    parser.add_argument(
        "--workflow",
        type=str,
        choices=["quick", "full", "verify-fix", "run-and-fix", "PROTO", "PROD", "VerifyFix", "RunAndFix"],
        default=None,
        help="Workflow: quick (PROTO), full (PROD), verify-fix, run-and-fix (build/deploy then fix from errors). Overrides -q/-f/--verify-fix if set."
    )
    
    parser.add_argument(
        "--plan",
        type=Path,
        default=None,
        help="Path to plan JSON file (required for -q/-f/-vfx; not used for run-and-fix)"
    )
    
    parser.add_argument(
        "--command",
        type=str,
        default=None,
        help="Command for run-and-fix (e.g. 'cd frontend-svelte && npm run build'). Required when --workflow run-and-fix."
    )
    
    parser.add_argument(
        "--run-and-fix-workdir",
        type=Path,
        default=None,
        help="Working directory for run-and-fix (default: project root)"
    )
    
    parser.add_argument(
        "--run-and-fix-max-rounds",
        type=int,
        default=5,
        help="Max fix rounds for run-and-fix (default: 5)"
    )
    
    parser.add_argument(
        "--run-and-fix",
        type=str,
        default=None,
        metavar="CMD",
        help="After -f (PROD), run this command and fix from errors until success (e.g. 'cd frontend-svelte && npm run build')"
    )
    
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output directory for results (default: settings.OUTPUT_DIR)"
    )
    
    parser.add_argument(
        "--context",
        type=str,
        default=None,
        help="Additional context for all steps"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show plan information and exit"
    )
    
    parser.add_argument(
        "--mode",
        type=str,
        choices=["FAST", "BUILD", "DOUBLE-CHECK"],
        default=None,
        help="Execution mode: FAST (ultra-fast), BUILD (balanced), DOUBLE-CHECK (with audit). Overridden by --fast/--build"
    )
    
    parser.add_argument(
        "--mentor",
        action="store_true",
        help="Enable pedagogical feedback mode - shows detailed rule violations with explanations"
    )
    
    parser.add_argument(
        "--tui",
        action="store_true",
        help="Launch Terminal User Interface (TUI) instead of CLI mode"
    )
    
    parser.add_argument(
        "--streaming",
        action="store_true",
        help="Use streaming mode to start execution as soon as steps are available"
    )
    
    parser.add_argument(
        "--planner",
        type=str,
        choices=["claude_code", "claude_api", "gemini", "deepseek", "auto"],
        default=None,
        help="Planner to use for plan generation: claude_code (Cursor), claude_api (Sonnet), gemini, deepseek, or auto (default: settings.DEFAULT_PLANNER)"
    )
    
    parser.add_argument(
        "--debug-keys",
        action="store_true",
        help="Print debug for all API keys (env vs .env, ascii, placeholder) before running"
    )
    
    # Subcommands (genome, sullivan)
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    genome_parser = subparsers.add_parser(
        "genome",
        help="Generate Genome (homeos_genome.json) from API"
    )
    genome_parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output path (default: output/studio/homeos_genome.json)"
    )
    
    # studio build (genome → build → refinement)
    studio_parser = subparsers.add_parser(
        "studio",
        help="Studio build: genome → build → refinement (Homeos Studio)"
    )
    studio_parser.add_argument(
        "build",
        nargs="?",
        default="build",
        help="Subcommand: build (default)"
    )
    studio_parser.add_argument(
        "--genome", "-g",
        type=Path,
        default=None,
        help="Path to existing genome (default: generate then output/studio/homeos_genome.json)"
    )
    studio_parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output HTML path (default: output/studio/studio_index.html)"
    )
    studio_parser.add_argument(
        "--base-url",
        type=str,
        default="http://localhost:8000",
        help="API base URL for Fetch (default: http://localhost:8000)"
    )
    studio_parser.add_argument(
        "--max-iterations",
        type=int,
        default=5,
        help="Max refinement iterations (default: 5)"
    )
    studio_parser.add_argument(
        "--no-refine",
        action="store_true",
        help="Skip refinement loop (build only)"
    )
    
    # sullivan (--design = designer en court : sullivan --design image.png)
    sullivan_dev_parser = subparsers.add_parser(
        "sullivan",
        help="Sullivan Kernel commands"
    )
    sullivan_dev_parser.add_argument(
        "--design", "-d",
        type=Path,
        default=None,
        help="Analyser image (template) avec Gemini — court pour designer (ex. sullivan -d docs/DA/Interface front.png)"
    )
    sullivan_dev_parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Sortie (frontend ou HTML selon la sous-commande)"
    )
    sullivan_dev_parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Sans confirmations interactives"
    )
    sullivan_dev_parser.add_argument(
        "--extract-principles",
        action="store_true",
        help="Extraire principes graphiques (couleurs, typo) → output/studio/design_principles.json"
    )
    sullivan_dev_parser.add_argument(
        "--principles-path",
        type=Path,
        default=None,
        help="Chemin sortie design_principles.json (défaut: output/studio/design_principles.json)"
    )
    sullivan_dev_parser.add_argument(
        "--build", "-b",
        action="store_true",
        help="Build interface (genome → studio_index.html). Court pour: sullivan build"
    )
    sullivan_dev_parser.add_argument(
        "--genome", "-g",
        type=Path,
        default=None,
        help="Genome JSON (pour --build, défaut: output/studio/homeos_genome.json)"
    )
    sullivan_dev_parser.add_argument(
        "--base-url",
        type=str,
        default=None,
        help="URL API pour --build (défaut: http://localhost:8000)"
    )
    sullivan_dev_parser.add_argument(
        "--no-refine",
        action="store_true",
        help="Build sans refinement (pour --build)"
    )
    sullivan_subparsers = sullivan_dev_parser.add_subparsers(dest="sullivan_command", required=False, help="Sous-commandes (dev, build, read-genome). Sans sous-commande: --design = designer, --build = build.")
    
    dev_parser = sullivan_subparsers.add_parser(
        "dev",
        help="Mode DEV: Analyze backend and generate frontend"
    )
    dev_parser.add_argument(
        "--backend-path",
        type=Path,
        required=True,
        help="Path to backend project to analyze (required)"
    )
    dev_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output directory for generated frontend (optional)"
    )
    dev_parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="Only analyze backend and display global function report (no frontend generation)"
    )
    dev_parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Disable interactive confirmations (run in non-interactive mode)"
    )
    
    read_genome_parser = sullivan_subparsers.add_parser(
        "read-genome",
        help="Sullivan reads Genome: load and print summary (metadata, topology, endpoints)"
    )
    read_genome_parser.add_argument(
        "--genome", "-g",
        type=Path,
        default=None,
        help="Genome path (default: output/studio/homeos_genome.json)"
    )
    
    designer_parser = sullivan_subparsers.add_parser(
        "designer",
        help="Mode DESIGNER: analyse image (template) avec Gemini puis génère frontend"
    )
    designer_parser.add_argument(
        "--design", "-d",
        type=Path,
        required=True,
        help="Chemin vers l'image design (PNG, JPG, SVG) — ex. docs/DA/Interface front.png"
    )
    designer_parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Répertoire de sortie pour le frontend généré (optionnel)"
    )
    designer_parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Sans confirmations interactives"
    )
    designer_parser.add_argument(
        "--extract-principles",
        action="store_true",
        help="Extraire principes graphiques → design_principles.json"
    )
    designer_parser.add_argument(
        "--principles-path",
        type=Path,
        default=None,
        help="Chemin sortie design_principles.json"
    )
    
    build_parser = sullivan_subparsers.add_parser(
        "build",
        help="Sullivan build: genome → studio_index.html (interface single-file)"
    )
    build_parser.add_argument(
        "--genome", "-g",
        type=Path,
        default=None,
        help="Genome JSON (défaut: output/studio/homeos_genome.json)"
    )
    build_parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Fichier HTML de sortie (défaut: output/studio/studio_index.html)"
    )
    build_parser.add_argument(
        "--base-url",
        type=str,
        default="http://localhost:8000",
        help="URL de base API pour Fetch (défaut: http://localhost:8000)"
    )
    build_parser.add_argument(
        "--no-refine",
        action="store_true",
        help="Build uniquement, sans boucle refinement (screenshot → audit → revise)"
    )
    
    plan_screens_parser = sullivan_subparsers.add_parser(
        "plan-screens",
        help="Sullivan plan-screens: genome → screen_plan.json (plan d'écrans)"
    )
    plan_screens_parser.add_argument(
        "--genome", "-g",
        type=Path,
        default=None,
        help="Genome JSON (défaut: output/studio/homeos_genome.json)"
    )
    plan_screens_parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Sortie screen_plan.json (défaut: output/studio/screen_plan.json)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(verbose=args.verbose)
    
    # Handle --tui command (launch TUI interface)
    if args.tui:
        from .tui import AetherFlowTUI
        app = AetherFlowTUI()
        if args.plan:
            app.set_plan_path(args.plan)
        if args.mentor:
            app.mentor_mode = True
            # Update mentor button after app is created
            # We'll do this in on_mount instead
        app.run()
        return 0
    
    # Print header
    print_header()
    
    # Handle --stats command
    if args.stats:
        print_cache_stats()
        return 0

    # Handle --status command (plan monitoring)
    if args.plan_status:
        from .core.plan_status import get_plan_status
        s = get_plan_status()
        if not s:
            console.print("[dim]Aucun plan en cours ou récent. Lancez -q ou -f avec --plan pour exécuter un plan.[/]")
            return 0
        t = Table(title="Plan en cours / Dernier plan", box=box.ROUNDED)
        t.add_column("Champ", style="cyan")
        t.add_column("Valeur", style="green")
        t.add_row("Plan", s.get("plan_path", "—") or "—")
        t.add_row("ID", s.get("plan_id", "—") or "—")
        t.add_row("Workflow", s.get("workflow_type", "—") or "—")
        t.add_row("Phase", s.get("phase", "—") or "—")
        status = s.get("status", "—")
        style = "green" if status == "completed" else "red" if status == "failed" else "yellow"
        t.add_row("Statut", f"[{style}]{status}[/]")
        if s.get("batch_index") is not None and s.get("total_batches"):
            t.add_row("Batch", f"{s['batch_index']} / {s['total_batches']}")
        if s.get("completed_steps") is not None:
            n = len(s["completed_steps"])
            total = s.get("total_steps") or n
            t.add_row("Steps terminés", f"{n} / {total}")
        if s.get("current_step_ids"):
            t.add_row("Steps en cours", ", ".join(s["current_step_ids"]))
        t.add_row("Démarré", s.get("started_at", "—") or "—")
        t.add_row("Mis à jour", s.get("updated_at", "—") or "—")
        if s.get("total_time_ms") is not None:
            t.add_row("Durée totale", f"{s['total_time_ms']/1000:.1f} s")
        if s.get("total_cost_usd") is not None:
            t.add_row("Coût total", f"${s['total_cost_usd']:.4f}")
        if s.get("error"):
            t.add_row("Erreur", f"[red]{s['error']}[/]")
        console.print(t)
        return 0

    def _print_usage_table(usage_data: Dict[str, Any], title: str) -> None:
        if not usage_data.get("has_data"):
            return
        t = Table(title=title, box=box.ROUNDED)
        t.add_column("Métrique", style="cyan")
        t.add_column("Valeur", style="green")
        t.add_row("Abonnement", "Claude Pro")
        t.add_row("Tokens total", f"{usage_data['total_tokens']:,}")
        t.add_row("Input", f"{usage_data['input_tokens']:,}")
        t.add_row("Output", f"{usage_data['output_tokens']:,}")
        if usage_data.get("cache_tokens"):
            t.add_row("Cache", f"{usage_data['cache_tokens']:,}")
        cost_label = "Coût (rapporté)" if usage_data.get("cost_source") == "reported" else "Coût (estimé)"
        t.add_row(cost_label, f"${usage_data['estimated_cost_usd']:.4f}")
        t.add_row("Sessions", str(usage_data["session_count"]))
        console.print(t)

    # Handle --costs command (AETHERFLOW + Cursor / Claude Pro split)
    if args.costs:
        from .core.cost_tracker import get_cost_report
        from .core.claude_usage_reader import get_claude_code_usage_split
        console.print(get_cost_report())
        split = get_claude_code_usage_split()
        cursor_pro = split["cursor_pro"]
        standalone = split["claude_pro_standalone"]
        any_data = cursor_pro["has_data"] or standalone["has_data"]
        if any_data:
            _print_usage_table(cursor_pro, "Claude Code in Cursor Pro (hors AetherFlow)")
            _print_usage_table(standalone, "Claude Code in Claude Pro (standalone)")
            if split.get("merged"):
                console.print("[dim]Source unique : si toute l'usage apparaît en « Claude Pro (standalone) », définir CLAUDE_CURSOR_CONFIG_DIR pour un répertoire Cursor distinct.[/]")
        else:
            console.print("[dim]Aucune donnée Claude Code trouvée (~/.config/claude ou CLAUDE_CONFIG_DIR)[/]")
        return 0

    # Handle --usage command (Cursor / Claude Pro split)
    if args.usage:
        from .core.claude_usage_reader import get_claude_code_usage_split
        split = get_claude_code_usage_split()
        cursor_pro = split["cursor_pro"]
        standalone = split["claude_pro_standalone"]
        any_data = cursor_pro["has_data"] or standalone["has_data"]
        if any_data:
            _print_usage_table(cursor_pro, "Claude Code in Cursor Pro (hors AetherFlow)")
            _print_usage_table(standalone, "Claude Code in Claude Pro (standalone)")
            if split.get("merged"):
                console.print("[dim]Source unique : si toute l'usage apparaît en « Claude Pro (standalone) », définir CLAUDE_CURSOR_CONFIG_DIR pour un répertoire Cursor distinct.[/]")
        else:
            console.print("[dim]Aucune donnée Claude Code trouvée (~/.config/claude ou CLAUDE_CONFIG_DIR)[/]")
        return 0
    
    # Handle genome command
    if args.command == "genome":
        from .core.genome_generator import run_genome_cli
        out = getattr(args, "output", None)
        return run_genome_cli(output_path=out)
    
    # Handle studio build command
    if args.command == "studio":
        async def run_studio():
            from .core.genome_generator import generate_genome
            from .sullivan.builder.sullivan_builder import build_from_genome, build_html
            from .sullivan.refinement import run_refinement
            
            genome_path = getattr(args, "genome", None)
            out_path = getattr(args, "output", None)
            base_url = getattr(args, "base_url", "http://localhost:8000") or "http://localhost:8000"
            max_iter = getattr(args, "max_iterations", 5) or 5
            no_refine = getattr(args, "no_refine", False) or False
            
            base = Path(settings.output_dir) / "studio"
            base.mkdir(parents=True, exist_ok=True)
            default_genome = base / "homeos_genome.json"
            default_html = base / "studio_index.html"
            
            if not genome_path or not Path(genome_path).exists():
                console.print("[dim]Generating genome...[/]")
                genome_path = generate_genome(output_path=default_genome)
            else:
                genome_path = Path(genome_path)
            
            out_path = Path(out_path) if out_path else default_html
            
            if no_refine:
                console.print("[dim]Building studio_index.html (no refinement)...[/]")
                build_from_genome(genome_path, output_path=out_path, base_url=base_url)
                console.print(f"[green]✓ Studio HTML written: {out_path}[/]")
                return 0
            
            console.print("[dim]Running refinement loop (build → screenshot → audit → revise)...[/]")
            path, html, audit = await run_refinement(
                genome_path,
                output_path=out_path,
                base_url=base_url,
                max_iterations=max_iter,
                score_threshold=85,
            )
            console.print(f"[green]✓ Studio HTML written: {path}[/]")
            if audit:
                console.print(f"[cyan]Final visual_score: {audit.visual_score}[/]")
                if audit.critiques:
                    console.print("[dim]Critiques:[/]")
                    for c in audit.critiques[:5]:
                        console.print(f"  - {c}")
            return 0
        
        return asyncio.run(run_studio())
    
    # Handle sullivan --design (court : sullivan -d image.png = designer)
    if args.command == "sullivan" and getattr(args, "design", None):
        async def run_sullivan_designer():
            from .sullivan.modes.designer_mode import DesignerMode
            designer_mode = DesignerMode(
                design_path=args.design,
                output_path=args.output,
                non_interactive=args.non_interactive,
                extract_principles=getattr(args, "extract_principles", False),
                principles_path=getattr(args, "principles_path", None),
            )
            result = await designer_mode.run()
            if result["success"]:
                console.print("[green]✓ Sullivan designer (analyse image) terminé[/]")
                if result.get("design_structure"):
                    ds = result["design_structure"]
                    console.print(f"  Sections: {len(ds.get('sections', []))}  Composants: {len(ds.get('components', []))}")
                if result.get("matched_patterns"):
                    console.print(f"  Patterns matchés: {len(result['matched_patterns'])}")
                if args.output:
                    console.print(f"  Sortie: {args.output}")
                return 0
            console.print(f"[red]✗ Échec: {result.get('message', 'Unknown error')}[/]")
            return 1
        return asyncio.run(run_sullivan_designer())
    
    # Handle sullivan --build (court : sullivan -b = build)
    if args.command == "sullivan" and getattr(args, "build", False):
        async def run_sullivan_build_short():
            from .core.genome_generator import generate_genome
            from .sullivan.builder.sullivan_builder import build_from_genome
            from .sullivan.refinement import run_refinement
            
            base = Path(settings.output_dir) / "studio"
            base.mkdir(parents=True, exist_ok=True)
            default_genome = base / "homeos_genome.json"
            default_html = base / "studio_index.html"
            
            genome_path = getattr(args, "genome", None) or default_genome
            out_path = getattr(args, "output", None) or default_html
            base_url = getattr(args, "base_url", None) or "http://localhost:8000"
            no_refine = getattr(args, "no_refine", False)
            
            if not Path(genome_path).exists():
                console.print("[dim]Genome absent, génération...[/]")
                genome_path = generate_genome(output_path=default_genome)
            else:
                genome_path = Path(genome_path)
            
            out_path = Path(out_path)
            
            if no_refine:
                console.print("[dim]Build Sullivan (sans refinement)...[/]")
                build_from_genome(genome_path, output_path=out_path, base_url=base_url)
                console.print(f"[green]✓ Sullivan HTML: {out_path}[/]")
                return 0
            
            console.print("[dim]Build Sullivan + refinement...[/]")
            path, html, audit = await run_refinement(
                genome_path, output_path=out_path, base_url=base_url,
                max_iterations=5, score_threshold=85,
            )
            console.print(f"[green]✓ Sullivan HTML: {path}[/]")
            if audit:
                console.print(f"[cyan]visual_score: {audit.visual_score}[/]")
            return 0
        
        return asyncio.run(run_sullivan_build_short())
    
    # Handle sullivan read-genome command
    if args.command == "sullivan" and getattr(args, "sullivan_command", None) == "read-genome":
        import json
        genome_path = getattr(args, "genome", None) or (Path(settings.output_dir) / "studio" / "homeos_genome.json")
        genome_path = Path(genome_path)
        if not genome_path.exists():
            console.print(f"[red]Genome not found: {genome_path}[/]")
            return 1
        try:
            g = json.loads(genome_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            console.print(f"[red]Invalid genome JSON: {e}[/]")
            return 1
        meta = g.get("metadata") or {}
        topo = g.get("topology") or []
        endpoints = g.get("endpoints") or []
        schemas = g.get("schema_definitions") or {}
        console.print(Panel.fit(
            f"[bold]intent[/] {meta.get('intent', '—')}  [bold]version[/] {meta.get('version', '—')}\n"
            f"[bold]generated_at[/] {meta.get('generated_at', '—')}",
            title="Genome · metadata",
            border_style="cyan"
        ))
        console.print(f"\n[bold cyan]topology[/] [dim]→[/] [green]{' → '.join(topo) or '—'}[/]")
        t = Table(title="endpoints")
        t.add_column("method", style="dim")
        t.add_column("path", style="cyan")
        t.add_column("x_ui_hint", style="yellow")
        t.add_column("summary", style="white")
        for ep in endpoints:
            t.add_row(
                str(ep.get("method", "—")),
                str(ep.get("path", "—")),
                str(ep.get("x_ui_hint", "—")),
                (ep.get("summary") or "—")[:48]
            )
        console.print(t)
        console.print(f"\n[dim]Schemas: {len(schemas)}  ·  Endpoints: {len(endpoints)}[/]")
        return 0
    
    # Handle sullivan dev command
    if args.command == "sullivan" and hasattr(args, 'sullivan_command') and args.sullivan_command == "dev":
        async def run_sullivan_dev():
            from .sullivan.modes.dev_mode import DevMode
            
            dev_mode = DevMode(
                backend_path=args.backend_path,
                output_path=args.output,
                analyze_only=args.analyze_only,
                non_interactive=args.non_interactive
            )
            
            result = await dev_mode.run()
            
            if result["success"]:
                console.print("[green]✓ Sullivan DevMode completed successfully[/]")
                if result.get("global_function"):
                    console.print(f"\n[cyan]Global Function:[/]")
                    gf = result["global_function"]
                    console.print(f"  Product Type: {gf.get('product_type')}")
                    console.print(f"  Actors: {', '.join(gf.get('actors', []))}")
                    console.print(f"  Business Flows: {', '.join(gf.get('business_flows', []))}")
                    console.print(f"  Use Cases: {', '.join(gf.get('use_cases', []))}")
                
                if args.output:
                    console.print(f"\n[green]Results saved to: {args.output}[/]")
                return 0
            else:
                console.print(f"[red]✗ Sullivan DevMode failed: {result.get('message', 'Unknown error')}[/]")
                return 1
        
        return asyncio.run(run_sullivan_dev())
    
    # Handle sullivan plan-screens
    if args.command == "sullivan" and getattr(args, "sullivan_command", None) == "plan-screens":
        from .sullivan.planner.screen_planner import plan_screens
        base = Path(settings.output_dir) / "studio"
        base.mkdir(parents=True, exist_ok=True)
        genome_path = getattr(args, "genome", None) or (base / "homeos_genome.json")
        out_path = getattr(args, "output", None) or (base / "screen_plan.json")
        genome_path = Path(genome_path)
        out_path = Path(out_path)
        if not genome_path.exists():
            console.print(f"[red]Genome not found: {genome_path}[/]")
            return 1
        try:
            plan = plan_screens(genome_path, out_path)
            console.print(f"[green]✓ Sullivan plan-screens: {len(plan)} corps → {out_path}[/]")
            return 0
        except Exception as e:
            console.print(f"[red]✗ plan-screens failed: {e}[/]")
            return 1
    
    # sullivan sans sous-commande ni --design ni --build → aide
    if args.command == "sullivan" and not getattr(args, "design", None) and not getattr(args, "build", False) and not getattr(args, "sullivan_command", None):
        console.print("[dim]Usage:[/] [cyan]aetherflow sullivan -d image.png[/] (designer)  |  [cyan]sullivan -b[/] (build)  |  [cyan]sullivan plan-screens[/]  |  [cyan]sullivan dev --backend-path ...[/]  |  [cyan]sullivan build[/]  |  [cyan]sullivan read-genome[/]")
        return 0
    
    # Handle sullivan build command
    if args.command == "sullivan" and hasattr(args, "sullivan_command") and args.sullivan_command == "build":
        async def run_sullivan_build():
            from .core.genome_generator import generate_genome
            from .sullivan.builder.sullivan_builder import build_from_genome
            from .sullivan.refinement import run_refinement
            
            base = Path(settings.output_dir) / "studio"
            base.mkdir(parents=True, exist_ok=True)
            default_genome = base / "homeos_genome.json"
            default_html = base / "studio_index.html"
            
            genome_path = getattr(args, "genome", None) or default_genome
            out_path = getattr(args, "output", None)
            base_url = getattr(args, "base_url", "http://localhost:8000") or "http://localhost:8000"
            no_refine = getattr(args, "no_refine", False) or False
            
            if not Path(genome_path).exists():
                console.print("[dim]Genome absent, génération...[/]")
                genome_path = generate_genome(output_path=default_genome)
            else:
                genome_path = Path(genome_path)
            
            out_path = Path(out_path) if out_path else default_html
            
            if no_refine:
                console.print("[dim]Build Sullivan (sans refinement)...[/]")
                build_from_genome(genome_path, output_path=out_path, base_url=base_url)
                console.print(f"[green]✓ Sullivan HTML: {out_path}[/]")
                return 0
            
            console.print("[dim]Build Sullivan + refinement (screenshot → audit → revise)...[/]")
            path, html, audit = await run_refinement(
                genome_path,
                output_path=out_path,
                base_url=base_url,
                max_iterations=5,
                score_threshold=85,
            )
            console.print(f"[green]✓ Sullivan HTML: {path}[/]")
            if audit:
                console.print(f"[cyan]visual_score: {audit.visual_score}[/]")
            return 0
        
        return asyncio.run(run_sullivan_build())
    
    # Determine workflow type (priority: --workflow > -q/-f > --fast/--build)
    workflow_type = None
    if args.workflow:
        # Normalize workflow names
        if args.workflow in ["quick", "PROTO"]:
            workflow_type = "PROTO"
        elif args.workflow in ["full", "PROD"]:
            workflow_type = "PROD"
        elif args.workflow in ["verify-fix", "VerifyFix"]:
            workflow_type = "VerifyFix"
        elif args.workflow in ["run-and-fix", "RunAndFix"]:
            workflow_type = "RunAndFix"
    elif args.quick or args.fast:
        workflow_type = "PROTO"
    elif args.full or args.build:
        workflow_type = "PROD"
    elif getattr(args, "verify_fix", False):
        workflow_type = "VerifyFix"
    elif getattr(args, "run_and_fix_workflow", False):
        workflow_type = "RunAndFix"
    
    # Debug API keys if requested (before any other action)
    if args.debug_keys:
        from .debug_keys import run_debug_keys
        run_debug_keys(verbose=True)
        print()
    
    # Require plan for workflow execution (except RunAndFix which requires --command)
    if workflow_type and workflow_type != "RunAndFix" and not args.plan:
        console.print("[red]Error: --plan is required for -q / -f / -vfx workflows[/]")
        return 1
    if workflow_type == "RunAndFix" and not getattr(args, "command", None):
        console.print("[red]Error: --command is required for --workflow run-and-fix[/]")
        return 1
    
    # Check if plan file exists (if provided)
    if args.plan and not args.plan.exists():
        console.print(f"[red]Error: Plan file not found: {args.plan}[/]")
        return 1
    
    # Show plan info if requested
    if args.info:
        if not args.plan:
            console.print("[red]Error: --plan is required for --info[/]")
            return 1
        print_plan_info(args.plan)
        return 0
    
    # Determine output directory
    output_dir = args.output or settings.output_dir
    
    # Execute workflows or plan
    try:
        # PROTO workflow (--workflow quick, -q, or --fast)
        if workflow_type == "PROTO":
            async def run_proto():
                from .workflows.proto import ProtoWorkflow
                workflow = ProtoWorkflow()
                result = await workflow.execute(
                    plan_path=args.plan,
                    output_dir=output_dir,
                    context=args.context
                )
                
                # Print summary
                summary_table = Table(title="PROTO Workflow Summary", box=box.ROUNDED)
                summary_table.add_column("Metric", style="cyan")
                summary_table.add_column("Value", style="green")
                
                summary_table.add_row("Total Time", f"{result['total_time_ms']/1000:.2f}s")
                summary_table.add_row("Total Cost", f"${result['total_cost_usd']:.4f}")
                summary_table.add_row("Success", "✓" if result["success"] else "✗")
                
                console.print(summary_table)
                
                # Display pedagogical feedback if --mentor is enabled
                if args.mentor and "validation" in result:
                    validation_details = result["validation"].get("validation_details", [])
                    if validation_details:
                        console.print("\n")
                        display_pedagogical_feedback(validation_details)
                
                return 0 if result["success"] else 1
            
            return asyncio.run(run_proto())
        
        # PROD workflow (--workflow full, -f, or --build)
        elif workflow_type == "PROD":
            async def run_prod():
                from .workflows.prod import ProdWorkflow
                workflow = ProdWorkflow()
                result = await workflow.execute(
                    plan_path=args.plan,
                    output_dir=output_dir,
                    context=args.context
                )
                
                # Print summary
                summary_table = Table(title="PROD Workflow Summary", box=box.ROUNDED)
                summary_table.add_column("Metric", style="cyan")
                summary_table.add_column("Value", style="green")
                
                summary_table.add_row("FAST Draft Time", f"{result['fast_draft']['metrics'].total_execution_time_ms/1000:.2f}s")
                summary_table.add_row("BUILD Refactor Time", f"{result['build_refactored']['metrics'].total_execution_time_ms/1000:.2f}s")
                summary_table.add_row("Total Time", f"{result['total_time_ms']/1000:.2f}s")
                summary_table.add_row("Total Cost", f"${result['total_cost_usd']:.4f}")
                summary_table.add_row("Success", "✓" if result["success"] else "✗")
                
                console.print(summary_table)
                
                # Display pedagogical feedback if --mentor is enabled
                if args.mentor and "validation" in result:
                    validation_details = result["validation"].get("validation_details", [])
                    if validation_details:
                        console.print("\n")
                        display_pedagogical_feedback(validation_details)
                
                # Optional: after PROD, run-and-fix (build/deploy then fix from errors)
                run_and_fix_cmd = getattr(args, "run_and_fix", None)
                if run_and_fix_cmd:
                    from .workflows.run_and_fix import RunAndFixWorkflow
                    console.print("\n[cyan]Run-and-Fix phase (build/deploy then fix from errors)[/]")
                    rnf = RunAndFixWorkflow()
                    rnf_result = await rnf.execute(
                        command=run_and_fix_cmd,
                        workdir=getattr(args, "run_and_fix_workdir", None),
                        max_rounds=getattr(args, "run_and_fix_max_rounds", 5),
                        output_dir=output_dir,
                    )
                    rnf_table = Table(title="Run-and-Fix Summary", box=box.ROUNDED)
                    rnf_table.add_column("Metric", style="cyan")
                    rnf_table.add_column("Value", style="green")
                    rnf_table.add_row("Rounds", str(rnf_result["rounds_done"]))
                    rnf_table.add_row("Success", "✓" if rnf_result["success"] else "✗")
                    rnf_table.add_row("Message", rnf_result.get("message", ""))
                    console.print(rnf_table)
                    return 0 if rnf_result["success"] else 1
                
                return 0 if result["success"] else 1
            
            return asyncio.run(run_prod())
        
        # VerifyFix workflow (--verify-fix or --workflow verify-fix)
        elif workflow_type == "VerifyFix":
            async def run_verify_fix():
                from .workflows.verify_fix import VerifyFixWorkflow
                workflow = VerifyFixWorkflow()
                result = await workflow.execute(
                    plan_path=args.plan,
                    output_dir=output_dir,
                    context=args.context,
                )
                summary_table = Table(title="VerifyFix Summary", box=box.ROUNDED)
                summary_table.add_column("Metric", style="cyan")
                summary_table.add_column("Value", style="green")
                summary_table.add_row("Total Time", f"{result['total_time_ms']/1000:.2f}s")
                summary_table.add_row("Total Cost", f"${result['total_cost_usd']:.4f}")
                summary_table.add_row("Corrections applied", str(result.get("fix_rounds_done", 0)))
                summary_table.add_row("Success", "✓" if result["success"] else "✗")
                summary_table.add_row("Message", result.get("message", ""))
                console.print(summary_table)
                if args.mentor and result.get("validation"):
                    validation_details = result["validation"].get("validation_details", [])
                    if validation_details:
                        console.print("\n")
                        display_pedagogical_feedback(validation_details)
                return 0 if result["success"] else 1
            return asyncio.run(run_verify_fix())
        
        # Run-and-Fix workflow (build/deploy then fix from errors)
        elif workflow_type == "RunAndFix":
            async def run_run_and_fix():
                from .workflows.run_and_fix import RunAndFixWorkflow
                workflow = RunAndFixWorkflow()
                result = await workflow.execute(
                    command=args.command,
                    workdir=getattr(args, "run_and_fix_workdir", None),
                    max_rounds=getattr(args, "run_and_fix_max_rounds", 5),
                    output_dir=output_dir,
                )
                summary_table = Table(title="Run-and-Fix Summary", box=box.ROUNDED)
                summary_table.add_column("Metric", style="cyan")
                summary_table.add_column("Value", style="green")
                summary_table.add_row("Rounds", str(result["rounds_done"]))
                summary_table.add_row("Total Time", f"{result['total_time_ms']/1000:.2f}s")
                summary_table.add_row("Total Cost", f"${result['total_cost_usd']:.4f}")
                summary_table.add_row("Success", "✓" if result["success"] else "✗")
                summary_table.add_row("Message", result.get("message", ""))
                console.print(summary_table)
                if result.get("last_stderr") and not result["success"]:
                    console.print("[dim]Last stderr:[/dim]")
                    console.print(result["last_stderr"][:2000] + ("..." if len(result["last_stderr"]) > 2000 else ""))
                return 0 if result["success"] else 1
            return asyncio.run(run_run_and_fix())
        
        # Standard plan execution (legacy mode)
        elif args.plan:
            return asyncio.run(execute_plan_async(
                plan_path=args.plan,
                output_dir=output_dir,
                context=args.context,
                verbose=args.verbose,
                execution_mode=args.mode,
                use_streaming=args.streaming
            ))
        else:
            console.print("[red]Error: --plan is required. Use -q / -f / -vfx or --workflow quick|full|verify-fix|run-and-fix[/]")
            parser.print_help()
            return 1
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/]")
        return 130
    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/]")
        if args.verbose:
            logger.exception("Fatal error")
        return 1


if __name__ == "__main__":
    sys.exit(main())