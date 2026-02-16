"""Command-line interface for AetherFlow."""
import asyncio
import os
import sys
import time
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich import box
from rich.text import Text
from loguru import logger

from .orchestrator import Orchestrator, ExecutionError
from .models.plan_reader import PlanValidationError
from .config.settings import settings


console = Console()

# ═══════════════════════════════════════════════════════════════════════════════
# TYPEWRITER EFFECT FOR CLI
# ═══════════════════════════════════════════════════════════════════════════════

class TypewriterConfig:
    """Configuration pour l'effet machine à écrire."""
    # Lire depuis variable d'env (désactivé par défaut pour ne pas surprendre)
    ENABLED: bool = os.getenv("SULLIVAN_TYPEWRITER", "0") == "1"
    BASE_SPEED: float = 0.015     # 15ms par caractère (comme le frontend)
    MIN_SPEED: float = 0.005      # Minimum 5ms pour textes longs
    MAX_DURATION: float = 8.0     # Max 8 secondes total
    PAUSE_CHARS: str = ".!?;,"   # Caractères qui provoquent une pause
    PAUSE_DURATION: float = 0.08  # 80ms de pause
    SKIP_KEY: str = " "           # Espace pour skip
    
    @classmethod
    def enable(cls):
        """Active l'effet machine à écrire."""
        cls.ENABLED = True
    
    @classmethod
    def disable(cls):
        """Désactive l'effet machine à écrire."""
        cls.ENABLED = False


def typewriter_print(
    prefix: str,
    text: str,
    prefix_style: str = "bold cyan",
    text_style: Optional[str] = None,
    config: TypewriterConfig = TypewriterConfig,
) -> None:
    """
    Affiche du texte avec effet machine à écrire.
    
    Args:
        prefix: Texte avant (ex: "Sullivan:")
        text: Le contenu à afficher
        prefix_style: Style rich pour le prefix
        text_style: Style rich optionnel pour le texte
        config: Configuration typewriter
    """
    import select
    import termios
    import tty
    
    # Si désactivé, affichage instantané
    if not config.ENABLED:
        if text_style:
            console.print(f"[{prefix_style}]{prefix}[/][{text_style}]{text}[/]")
        else:
            console.print(f"[{prefix_style}]{prefix}[/]{text}")
        return
    
    # Afficher le prefix
    console.print(f"[{prefix_style}]{prefix}[/]", end="")
    
    # Calculer la vitesse adaptative (plus rapide pour textes longs)
    text_length = len(text)
    if text_length > 500:
        speed = config.MIN_SPEED
    elif text_length > 200:
        # Interpolation entre BASE et MIN
        ratio = (text_length - 200) / 300
        speed = config.BASE_SPEED - (config.BASE_SPEED - config.MIN_SPEED) * ratio
    else:
        speed = config.BASE_SPEED
    
    # S'assurer qu'on ne dépasse pas MAX_DURATION
    estimated_time = text_length * speed
    if estimated_time > config.MAX_DURATION:
        speed = config.MAX_DURATION / text_length
    
    # Configurer le terminal pour lecture non-bloquante
    old_settings = None
    skip_requested = threading.Event()
    
    def check_skip():
        """Thread qui vérifie si l'utilisateur veut skipper."""
        try:
            # Unix only - vérifie si touche pressée
            import sys
            import select
            while not skip_requested.is_set():
                if select.select([sys.stdin], [], [], 0.05)[0]:
                    key = sys.stdin.read(1)
                    if key in (config.SKIP_KEY, '\n', '\r', '\x03'):  # Espace, Entrée, Ctrl+C
                        skip_requested.set()
                        break
        except:
            pass
    
    # Démarrer le thread de détection
    try:
        # Mettre le terminal en mode raw pour capturer les touches
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setcbreak(fd)
        
        skip_thread = threading.Thread(target=check_skip, daemon=True)
        skip_thread.start()
    except (ImportError, AttributeError, termios.error):
        # Windows ou erreur terminal - on continue sans skip
        old_settings = None
    
    try:
        # Affichage caractère par caractère
        for i, char in enumerate(text):
            if skip_requested.is_set():
                # Afficher le reste instantanément
                console.print(text[i:], end="", style=text_style or "")
                break
            
            console.print(char, end="", style=text_style or "")
            
            # Pause sur ponctuation
            if char in config.PAUSE_CHARS:
                time.sleep(config.PAUSE_DURATION)
            else:
                time.sleep(speed)
    finally:
        skip_requested.set()
        if old_settings:
            try:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            except:
                pass
    
    console.print()  # Nouvelle ligne finale


# Pour Windows ou si termios non dispo
if sys.platform == "win32":
    def typewriter_print(
        prefix: str,
        text: str,
        prefix_style: str = "bold cyan",
        text_style: Optional[str] = None,
        config: TypewriterConfig = TypewriterConfig,
    ) -> None:
        """Version simplifiée pour Windows (sans skip interacif)."""
        if not config.ENABLED:
            if text_style:
                console.print(f"[{prefix_style}]{prefix}[/][{text_style}]{text}[/]")
            else:
                console.print(f"[{prefix_style}]{prefix}[/]{text}")
            return
        
        console.print(f"[{prefix_style}]{prefix}[/]", end="")
        
        # Calcul vitesse adaptative
        text_length = len(text)
        speed = max(config.MIN_SPEED, min(config.BASE_SPEED, 3.0 / text_length if text_length > 0 else 0.01))
        
        for char in text:
            console.print(char, end="", style=text_style or "")
            time.sleep(speed)
            if char in config.PAUSE_CHARS:
                time.sleep(config.PAUSE_DURATION)
        
        console.print()


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
    use_streaming: bool = False,
    sequential: bool = False
) -> int:
    """Execute plan asynchronously."""
    orchestrator = Orchestrator(execution_mode=execution_mode or "BUILD", sequential_mode=sequential)

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
    from .cache import SemanticCache
    
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
        "-b",
        "--build",
        action="store_true",
        dest="build",
        help="PROD workflow: Quality-first (FAST draft → BUILD refactor → DOUBLE-CHECK) [same as -f]"
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
        "-fq",
        "--frd-quick",
        action="store_true",
        dest="frd_quick",
        help="FRD Quick: Fast prototyping with KIMI (FRD-FAST only)"
    )
    workflow_group.add_argument(
        "-ff",
        "--frd-full",
        action="store_true",
        dest="frd_full",
        help="FRD Full: Complete workflow with KIMI → DeepSeek → Gemini (FRD-FAST → TEST → REVIEW)"
    )
    workflow_group.add_argument(
        "-fvfx",
        "--frd-vfx",
        action="store_true",
        dest="frd_vfx",
        help="FRD Verify-Fix: Full cycle with KIMI verification and fixes (FRD-FAST → TEST → VERIFY → FIX)"
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
    workflow_group.add_argument(
        "--hybrid",
        type=str,
        metavar="TASK",
        dest="hybrid_task",
        help="Hybrid FRD: KIMI code + DeepSeek tests + Review. Example: aetherflow --hybrid 'Create login component'"
    )
    
    parser.add_argument(
        "--workflow",
        type=str,
        choices=["quick", "full", "verify-fix", "PROTO", "PROD", "VerifyFix"],
        default=None,
        help="Workflow: quick (PROTO), full (PROD), verify-fix (validate then correct errors). Overrides -q/-f/--verify-fix if set."
    )
    
    parser.add_argument(
        "--plan",
        type=Path,
        default=None,
        help="Path to plan JSON file (required for -q/-f/--fast/--build/--workflow)"
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
        "--sequential",
        "-seq",
        action="store_true",
        help="Execute plan steps one at a time (sequential mode) to avoid rate limiting. Recommended for large plans."
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
    
    # report-correction: log a correction applied by Cursor/Claude (error survey)
    report_parser = subparsers.add_parser(
        "report-correction",
        help="Log a correction applied by Cursor or Claude (error survey directory)"
    )
    report_parser.add_argument(
        "--title", "-t",
        type=str,
        required=True,
        help="Short title of the problem/correction"
    )
    report_parser.add_argument(
        "--nature", "-n",
        type=str,
        default="correction_applied",
        help="Nature: correction_applied, apply_fix, validation_fix, etc. (default: correction_applied)"
    )
    report_parser.add_argument(
        "--solution", "-s",
        type=str,
        required=True,
        help="Proposed solution / description of the fix applied"
    )
    report_parser.add_argument(
        "--source",
        type=str,
        choices=["cursor", "claude"],
        default="cursor",
        help="Source: cursor or claude (default: cursor)"
    )
    report_parser.add_argument(
        "--file", "-f",
        type=str,
        default=None,
        help="File path concerned (optional)"
    )
    report_parser.add_argument(
        "--step",
        type=str,
        default=None,
        help="Step id concerned, e.g. step_1 (optional)"
    )
    report_parser.add_argument(
        "--error",
        type=str,
        default=None,
        help="Raw error message (optional)"
    )
    
    # survey list: read all system anomalies (errors, corrections, build, API, etc.)
    survey_list_parser = subparsers.add_parser(
        "survey",
        help="Survey: list all system anomalies (errors, corrections, build, API, etc.)"
    )
    survey_list_parser.add_argument(
        "action",
        nargs="?",
        default="list",
        choices=["list"],
        help="Action: list (default)"
    )
    survey_list_parser.add_argument(
        "--source",
        type=str,
        choices=["aetherflow", "cursor", "claude", "system"],
        default=None,
        help="Filter by source (aetherflow | cursor | claude | system)"
    )
    survey_list_parser.add_argument(
        "--nature",
        type=str,
        default=None,
        help="Filter by nature (e.g. step_failed, build_error, api_error, correction_applied)"
    )
    survey_list_parser.add_argument(
        "--limit", "-n",
        type=int,
        default=None,
        help="Max number of entries to show"
    )
    survey_list_parser.add_argument(
        "--format",
        type=str,
        choices=["table", "json"],
        default="table",
        help="Output format: table (default) or json"
    )
    
    # studio (build | ir-sync)
    studio_parser = subparsers.add_parser(
        "studio",
        help="Studio: build (genome → HTML) or ir-sync (IR Markdown → JSON)"
    )
    studio_subparsers = studio_parser.add_subparsers(
        dest="studio_command",
        required=False,
        help="Studio subcommands (default: build)"
    )
    build_parser = studio_subparsers.add_parser(
        "build",
        help="Build studio: genome → build → refinement (Homeos Studio)"
    )
    build_parser.add_argument(
        "--genome", "-g",
        type=Path,
        default=None,
        help="Path to existing genome (default: generate then output/studio/homeos_genome.json)"
    )
    build_parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output HTML path (default: output/studio/studio_index.html)"
    )
    build_parser.add_argument(
        "--base-url",
        type=str,
        default="http://localhost:8000",
        help="API base URL for Fetch (default: http://localhost:8000)"
    )
    build_parser.add_argument(
        "--max-iterations",
        type=int,
        default=5,
        help="Max refinement iterations (default: 5)"
    )
    build_parser.add_argument(
        "--no-refine",
        action="store_true",
        help="Skip refinement loop (build only)"
    )
    ir_sync_parser = studio_subparsers.add_parser(
        "ir-sync",
        help="Convert IR inventory Markdown to JSON (output/studio/ir_inventaire.json)"
    )
    ir_sync_parser.add_argument(
        "--md",
        type=Path,
        default=None,
        help="Path to IR inventory Markdown (default: output/studio/ir_inventaire.md)"
    )
    ir_sync_parser.add_argument(
        "--json",
        type=Path,
        default=None,
        help="Path to output JSON (default: output/studio/ir_inventaire.json)"
    )
    ir_sync_parser.add_argument(
        "--schema",
        type=Path,
        default=None,
        help="Path to JSON schema (default: docs/references/technique/ir_schema.json)"
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
    
    # Chat agent parser
    chat_parser = sullivan_subparsers.add_parser(
        "chat",
        help="Chat avec Sullivan Agent (conversation avec mémoire et outils)"
    )
    chat_parser.add_argument(
        "message",
        nargs="?",
        help="Message à envoyer à Sullivan (sinon mode interactif)"
    )
    chat_parser.add_argument(
        "--session", "-s",
        type=str,
        default=None,
        help="ID de session existante (pour continuer une conversation)"
    )
    chat_parser.add_argument(
        "--user", "-u",
        type=str,
        default="cli_user",
        help="ID utilisateur (défaut: cli_user)"
    )
    chat_parser.add_argument(
        "--step",
        type=int,
        default=4,
        help="Étape du parcours UX (1-9, défaut: 4)"
    )
    chat_parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Mode interactif (conversation continue)"
    )
    
    # CTO Mode parser
    cto_parser = sullivan_subparsers.add_parser(
        "cto",
        help="Mode CTO: Sullivan comme Chief Technology Officer (analyse → décision → exécution)"
    )
    cto_parser.add_argument(
        "request",
        nargs="?",
        help="Demande en langage naturel (ex: 'Crée une page de login', 'Analyse docs/mockup.png')"
    )
    cto_parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Mode interactif CTO (conversation avec exécution)"
    )
    
    # Plan Builder parser
    plan_parser = sullivan_subparsers.add_parser(
        "plan",
        help="Mode PlanBuilder: De l'idée au plan structuré (backend + frontend)"
    )
    plan_parser.add_argument(
        "brief",
        nargs="?",
        help="Brief en langage naturel (ex: 'Dashboard avec auth et graphiques')"
    )
    plan_parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        default=True,
        help="Mode interactif - dialogue pour affiner le plan (défaut: True)"
    )
    plan_parser.add_argument(
        "--execute", "-e",
        action="store_true",
        help="Exécuter le plan immédiatement après création"
    )
    plan_parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Chemin de sortie pour le plan JSON"
    )
    
    # FrontendMode (frd) parser
    frd_parser = sullivan_subparsers.add_parser(
        "frd",
        help="Mode FRONTEND: orchestration multi-modèles (Gemini/DeepSeek/Groq) pour workflows frontend"
    )
    frd_subparsers = frd_parser.add_subparsers(dest="frd_action", required=True, help="Actions FrontendMode")
    
    # frd analyze
    frd_analyze_parser = frd_subparsers.add_parser(
        "analyze",
        help="Analyser un design (image) avec Gemini vision"
    )
    frd_analyze_parser.add_argument(
        "--image", "-i",
        type=Path,
        required=True,
        help="Chemin vers l'image design (PNG, JPG, SVG)"
    )
    frd_analyze_parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Fichier JSON de sortie pour la structure de design (optionnel)"
    )
    
    # frd generate
    frd_generate_parser = frd_subparsers.add_parser(
        "generate",
        help="Générer composants HTML (Gemini si contexte > 50k, sinon DeepSeek)"
    )
    frd_generate_parser.add_argument(
        "--design-structure",
        type=Path,
        required=True,
        help="Fichier JSON avec structure de design"
    )
    frd_generate_parser.add_argument(
        "--genome",
        type=Path,
        default=None,
        help="Fichier JSON avec genome/frontend structure (optionnel)"
    )
    frd_generate_parser.add_argument(
        "--webography",
        type=Path,
        default=None,
        help="Fichier texte avec webographie (défaut: docs/02-sullivan/Références webdesign de Sullivan.md)"
    )
    frd_generate_parser.add_argument(
        "--output", "-o",
        type=Path,
        required=True,
        help="Fichier HTML de sortie"
    )
    frd_generate_parser.add_argument(
        "--context-size",
        type=int,
        default=None,
        help="Taille du contexte en tokens (calculé automatiquement si non fourni)"
    )
    
    # frd refine
    frd_refine_parser = frd_subparsers.add_parser(
        "refine",
        help="Raffiner le style d'un fragment HTML (Groq avec fallback Gemini)"
    )
    frd_refine_parser.add_argument(
        "--html",
        type=Path,
        required=True,
        help="Fichier HTML à raffiner"
    )
    frd_refine_parser.add_argument(
        "--instruction", "-i",
        type=str,
        required=True,
        help="Instruction de raffinement"
    )
    frd_refine_parser.add_argument(
        "--output", "-o",
        type=Path,
        required=True,
        help="Fichier HTML de sortie"
    )
    
    # frd dialogue
    frd_dialogue_parser = frd_subparsers.add_parser(
        "dialogue",
        help="Dialogue conversationnel (Groq avec fallback Gemini)"
    )
    frd_dialogue_parser.add_argument(
        "--message", "-m",
        type=str,
        required=True,
        help="Message utilisateur"
    )
    frd_dialogue_parser.add_argument(
        "--session-context",
        type=Path,
        default=None,
        help="Fichier JSON avec contexte de session (optionnel)"
    )
    frd_dialogue_parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Fichier texte de sortie pour la réponse (optionnel, affiche à l'écran si non fourni)"
    )
    
    # frd validate
    frd_validate_parser = frd_subparsers.add_parser(
        "validate",
        help="Valider homéostasie d'un payload JSON (Groq avec fallback Gemini)"
    )
    frd_validate_parser.add_argument(
        "--json", "-j",
        type=Path,
        required=True,
        help="Fichier JSON à valider"
    )
    frd_validate_parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Fichier JSON de sortie pour le résultat de validation (optionnel)"
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

    # Handle -h/--hybrid command (Hybrid FRD Mode: KIMI + DeepSeek + Sonnet)
    if args.hybrid_task:
        from .sullivan.modes.hybrid_frd_mode import HybridFRDMode

        async def run_hybrid_frd():
            console.print(f"\n[cyan]╔══════════════════════════════════════╗[/]")
            console.print(f"[cyan]║   Hybrid FRD Mode                    ║[/]")
            console.print(f"[cyan]╚══════════════════════════════════════╝[/]\n")
            console.print(f"[bold]Tâche :[/] {args.hybrid_task}\n")
            console.print("[dim]KIMI (code) → DeepSeek (tests) → Sonnet (review)[/]\n")

            hybrid = HybridFRDMode()

            try:
                result = await hybrid.execute_from_task(args.hybrid_task)

                if result["success"]:
                    console.print("\n[green]╔═══════════════════════════╗[/]")
                    console.print("[green]║   WORKFLOW COMPLETED      ║[/]")
                    console.print("[green]║   Verdict : ✅ GO         ║[/]")
                    console.print("[green]║   Ready for production    ║[/]")
                    console.print("[green]╚═══════════════════════════╝[/]\n")

                    # Afficher résumé
                    console.print("[bold]Résumé :[/]")
                    if 'kimi' in result:
                        console.print(f"  • KIMI : {len(result['kimi']['files_created'])} fichiers créés")
                    if 'deepseek' in result:
                        console.print(f"  • DeepSeek : {len(result['deepseek']['test_files_created'])} tests (Coverage: {result['deepseek']['coverage']}%)")
                    if 'review' in result:
                        console.print(f"  • Sonnet : Verdict {result['review']['verdict']}")

                    return 0
                else:
                    console.print("\n[red]╔═══════════════════════════╗[/]")
                    console.print("[red]║   WORKFLOW FAILED         ║[/]")
                    console.print("[red]║   Verdict : ❌ NO-GO      ║[/]")
                    console.print("[red]╚═══════════════════════════╝[/]\n")

                    # Afficher erreur et détails
                    if 'error' in result:
                        console.print(f"[bold red]Erreur :[/] {result['error']}")

                    if 'details' in result:
                        console.print(f"[dim]{result['details']}[/]")

                    # Afficher issues si disponibles
                    if 'review' in result and 'issues' in result['review'] and result['review']['issues']:
                        console.print("\n[bold red]Issues :[/]")
                        for issue in result['review']['issues']:
                            console.print(f"  • {issue}")

                    return 1

            except Exception as e:
                console.print(f"\n[red]✗ Erreur : {e}[/]")
                logger.exception("Hybrid FRD Mode failed")
                return 1

        return asyncio.run(run_hybrid_frd())

    # Handle genome command
    if args.command == "genome":
        from .core.genome_generator import run_genome_cli
        out = getattr(args, "output", None)
        return run_genome_cli(output_path=out)
    
    # Handle report-correction (error survey: Cursor/Claude corrections)
    if args.command == "report-correction":
        from .core.error_survey import log_correction
        path = log_correction(
            title=args.title,
            nature=getattr(args, "nature", "correction_applied"),
            proposed_solution=args.solution,
            source=getattr(args, "source", "cursor"),
            raw_error=getattr(args, "error", None),
            step_id=getattr(args, "step", None),
            file_path=getattr(args, "file", None),
        )
        console.print(f"[green]Correction enregistrée : {path}[/]")
        return 0
    
    # Handle survey list (read error/correction entries; independent of report-correction)
    if args.command == "survey":
        import json
        from .core.error_survey import list_entries
        entries = list_entries(
            source=getattr(args, "source", None),
            nature=getattr(args, "nature", None),
            limit=getattr(args, "limit", None),
        )
        out_fmt = getattr(args, "format", "table") or "table"
        if out_fmt == "json":
            # Strip paths for compact output; keep title, date, nature, source
            out = [{"title": e.get("title"), "date": e.get("date"), "nature": e.get("nature"), "source": e.get("source"), "md_path": e.get("md_path")} for e in entries]
            console.print(json.dumps(out, indent=2, ensure_ascii=False))
            return 0
        if not entries:
            console.print(f"[dim]Aucune entrée dans {settings.error_log_dir}[/]")
            return 0
        table = Table(title="Error survey", box=box.ROUNDED)
        table.add_column("Date", style="dim", width=20)
        table.add_column("Source", width=10)
        table.add_column("Nature", width=22)
        table.add_column("Title", style="cyan", no_wrap=False)
        for e in entries:
            table.add_row(
                (e.get("date") or "")[:19],
                e.get("source") or "",
                e.get("nature") or "",
                (e.get("title") or "")[:60],
            )
        console.print(table)
        console.print(f"[dim]{len(entries)} entrée(s) — répertoire : {settings.error_log_dir}[/]")
        return 0
    
    # Handle studio build command
    if args.command == "studio" and getattr(args, "studio_command", None) == "ir-sync":
        from .core.ir_md_to_json import ir_md_to_json
        base = Path(settings.output_dir) / "studio"
        default_md = base / "ir_inventaire.md"
        default_json = base / "ir_inventaire.json"
        default_schema = Path("docs/references/technique/ir_schema.json")
        md_path = getattr(args, "md", None) or default_md
        json_path = getattr(args, "json", None) or default_json
        schema_path = getattr(args, "schema", None) or default_schema
        try:
            success = ir_md_to_json(
                Path(md_path),
                Path(json_path),
                Path(schema_path),
            )
            if success:
                console.print(f"[green]✓ IR Markdown → JSON: {json_path}[/]")
                return 0
            console.print("[red]✗ Conversion failed[/]")
            return 1
        except Exception as e:
            console.print(f"[red]Error: {e}[/]")
            if getattr(args, "verbose", False):
                logger.exception("IR sync error")
            return 1

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
    
    # Handle sullivan frd (FrontendMode)
    if args.command == "sullivan" and getattr(args, "sullivan_command", None) == "frd":
        async def run_sullivan_frd():
            from .sullivan.modes.frontend_mode import FrontendMode
            
            frontend_mode = FrontendMode()
            action = getattr(args, "frd_action", None)
            
            if action == "analyze":
                image_path = Path(args.image)
                if not image_path.exists():
                    console.print(f"[red]✗ Image not found: {image_path}[/]")
                    return 1
                
                try:
                    result = await frontend_mode.analyze_design(image_path)
                    
                    if args.output:
                        import json
                        output_path = Path(args.output)
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
                        console.print(f"[green]✓ Design structure saved to: {output_path}[/]")
                    
                    console.print("[green]✓ Design analysis completed[/]")
                    ds = result
                    console.print(f"  Sections: {len(ds.get('sections', []))}")
                    console.print(f"  Components: {len(ds.get('components', []))}")
                    return 0
                except Exception as e:
                    console.print(f"[red]✗ Analysis failed: {e}[/]")
                    if args.verbose:
                        logger.exception("FrontendMode analyze failed")
                    return 1
            
            elif action == "generate":
                import json
                
                design_structure_path = Path(args.design_structure)
                if not design_structure_path.exists():
                    console.print(f"[red]✗ Design structure file not found: {design_structure_path}[/]")
                    return 1
                
                design_structure = json.loads(design_structure_path.read_text(encoding="utf-8"))
                
                genome = None
                if args.genome:
                    genome_path = Path(args.genome)
                    if genome_path.exists():
                        genome = json.loads(genome_path.read_text(encoding="utf-8"))
                
                webography_path = args.webography
                if webography_path is None:
                    # Default webography
                    root = Path(__file__).resolve().parents[3]
                    webography_path = root / "docs" / "02-sullivan" / "Références webdesign de Sullivan.md"
                
                if not Path(webography_path).exists():
                    console.print(f"[yellow]⚠ Webography file not found: {webography_path}, using empty string[/]")
                    webography_text = ""
                else:
                    webography_text = Path(webography_path).read_text(encoding="utf-8")
                
                try:
                    html = await frontend_mode.generate_components(
                        design_structure=design_structure,
                        genome=genome,
                        webography=webography_text,
                        context_size=getattr(args, "context_size", None)
                    )
                    
                    output_path = Path(args.output)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(html, encoding="utf-8")
                    
                    console.print(f"[green]✓ HTML generated: {output_path}[/]")
                    return 0
                except Exception as e:
                    console.print(f"[red]✗ Generation failed: {e}[/]")
                    if args.verbose:
                        logger.exception("FrontendMode generate failed")
                    return 1
            
            elif action == "refine":
                html_path = Path(args.html)
                if not html_path.exists():
                    console.print(f"[red]✗ HTML file not found: {html_path}[/]")
                    return 1
                
                html_fragment = html_path.read_text(encoding="utf-8")
                instruction = args.instruction
                
                try:
                    refined_html = await frontend_mode.refine_style(html_fragment, instruction)
                    
                    output_path = Path(args.output)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(refined_html, encoding="utf-8")
                    
                    console.print(f"[green]✓ HTML refined: {output_path}[/]")
                    return 0
                except Exception as e:
                    console.print(f"[red]✗ Refinement failed: {e}[/]")
                    if args.verbose:
                        logger.exception("FrontendMode refine failed")
                    return 1
            
            elif action == "dialogue":
                message = args.message
                session_context = None
                
                if args.session_context:
                    import json
                    session_context_path = Path(args.session_context)
                    if session_context_path.exists():
                        session_context = json.loads(session_context_path.read_text(encoding="utf-8"))
                
                try:
                    response = await frontend_mode.dialogue(message, session_context)
                    
                    if args.output:
                        output_path = Path(args.output)
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        output_path.write_text(response, encoding="utf-8")
                        console.print(f"[green]✓ Response saved to: {output_path}[/]")
                    else:
                        console.print("[green]✓ Response:[/]")
                        console.print(response)
                    
                    return 0
                except Exception as e:
                    console.print(f"[red]✗ Dialogue failed: {e}[/]")
                    if args.verbose:
                        logger.exception("FrontendMode dialogue failed")
                    return 1
            
            elif action == "validate":
                import json
                
                json_path = Path(args.json)
                if not json_path.exists():
                    console.print(f"[red]✗ JSON file not found: {json_path}[/]")
                    return 1
                
                json_payload = json.loads(json_path.read_text(encoding="utf-8"))
                
                try:
                    validation_result = await frontend_mode.validate_homeostasis(json_payload)
                    
                    if args.output:
                        output_path = Path(args.output)
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        output_path.write_text(
                            json.dumps(validation_result, indent=2, ensure_ascii=False),
                            encoding="utf-8"
                        )
                        console.print(f"[green]✓ Validation result saved to: {output_path}[/]")
                    
                    is_valid = validation_result.get("valid", False)
                    if is_valid:
                        console.print("[green]✓ Validation passed[/]")
                    else:
                        console.print("[yellow]⚠ Validation failed[/]")
                        issues = validation_result.get("issues", [])
                        if issues:
                            console.print("  Issues:")
                            for issue in issues:
                                console.print(f"    - {issue}")
                    
                    suggestions = validation_result.get("suggestions", [])
                    if suggestions:
                        console.print("  Suggestions:")
                        for suggestion in suggestions:
                            console.print(f"    - {suggestion}")
                    
                    return 0 if is_valid else 1
                except Exception as e:
                    console.print(f"[red]✗ Validation failed: {e}[/]")
                    if args.verbose:
                        logger.exception("FrontendMode validate failed")
                    return 1
            
            else:
                console.print(f"[red]✗ Unknown frd action: {action}[/]")
                return 1
        
        return asyncio.run(run_sullivan_frd())
    
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
    
    # Handle sullivan chat
    if args.command == "sullivan" and getattr(args, "sullivan_command", None) == "chat":
        async def run_sullivan_chat():
            from .sullivan.agent import create_agent
            from .sullivan.agent.tools import ToolResult
            import time
            
            session_id = getattr(args, "session", None)
            user_id = getattr(args, "user", "cli_user")
            step = getattr(args, "step", 4)
            message = getattr(args, "message", None)
            interactive = getattr(args, "interactive", False) or not message
            
            # Créer ou récupérer l'agent
            try:
                agent = await create_agent(
                    user_id=user_id,
                    session_id=session_id,
                    step=step,
                )
            except Exception as e:
                console.print(f"[red]❌ Erreur création agent: {e}[/]")
                return 1
            
            def display_tool_execution(tool_name: str, params: dict, result: ToolResult, elapsed_ms: float):
                """Affiche l'exécution d'un outil avec monitoring."""
                status = "✅" if result.success else "❌"
                status_color = "green" if result.success else "red"
                
                # Afficher l'action
                console.print(f"\n[{status_color}]{status} Action: {tool_name}[/{status_color}] [dim]({elapsed_ms:.0f}ms)[/]")
                
                # Paramètres (limités)
                if params:
                    params_str = ", ".join([f"{k}={str(v)[:30]}" for k, v in params.items()])
                    if len(params_str) > 60:
                        params_str = params_str[:60] + "..."
                    console.print(f"   [dim]→ {params_str}[/]")
                
                # Résultat
                if result.content:
                    content = result.content[:100] + "..." if len(result.content) > 100 else result.content
                    console.print(f"   [dim]← {content}[/]")
                
                if result.error:
                    console.print(f"   [red]Erreur: {result.error}[/]")
            
            def display_response_summary(response, total_time_ms: float):
                """Affiche un résumé de la réponse style AetherFlow."""
                from rich.table import Table
                
                table = Table(show_header=False, box=None, padding=(0, 2))
                table.add_column("Label", style="dim", width=12)
                table.add_column("Value")
                
                table.add_row("⏱️  Temps:", f"{total_time_ms:.0f}ms")
                table.add_row("💬 Réponse:", f"{len(response.content)} caractères")
                
                if response.tool_calls:
                    success_count = sum(1 for r in response.tool_results if r.success)
                    table.add_row("🔧 Outils:", f"{len(response.tool_calls)} appels, {success_count} ✅")
                
                if response.metadata.get("step"):
                    table.add_row("📍 Étape:", f"{response.metadata['step']}/9")
                
                console.print(table)
            
            # Si un message est fourni, mode one-shot avec monitoring
            if message:
                start_time = time.time()
                
                with console.status("[cyan]🧠 Sullivan réfléchit..."):
                    response = await agent.chat(message)
                
                total_time = (time.time() - start_time) * 1000
                
                # DEBUG: Afficher les tool_calls détectés
                if response.tool_calls:
                    console.print(f"\n[dim]DEBUG: {len(response.tool_calls)} tool_calls détectés:[/]")
                    for tc in response.tool_calls:
                        console.print(f"  - {tc.get('tool')}({tc.get('params', {})})")
                else:
                    console.print("\n[dim]DEBUG: Aucun tool_calls détecté[/]")
                
                # Afficher les actions exécutées
                if response.tool_calls and response.tool_results:
                    console.print("\n[bold cyan]🔧 Actions exécutées:[/]")
                    for call, result in zip(response.tool_calls, response.tool_results):
                        # Estimer le temps (on n'a pas le détail par outil)
                        display_tool_execution(call['tool'], call.get('params', {}), result, total_time / max(len(response.tool_calls), 1))
                
                # Afficher la réponse
                console.print("\n[bold cyan]💬 Sullivan:[/]")
                console.print(response.content)
                
                # Résumé
                console.print()
                display_response_summary(response, total_time)
                
                console.print(f"\n[dim]Session: {response.session_id}[/]")
                return 0
            
            # Mode interactif
            console.print("\n[bold cyan]🎭 Sullivan Agent[/] - Mode interactif")
            console.print("[dim]Tape 'quit', 'exit' ou Ctrl+C pour quitter[/]")
            console.print(f"[dim]Session: {agent.session_id} | Étape: {step} | Monitoring actif ✅[/]\n")
            
            import sys
            if not sys.stdin.isatty():
                console.print("[yellow]⚠️ stdin n'est pas un terminal interactif.[/]")
                console.print("[dim]Utilisez: ./aetherflow-chat 'votre message'[/]")
                return 1
            
            # Boucle interactive
            try:
                while True:
                    # Lire l'input
                    try:
                        console.print("[bold green]Vous:[/] ", end="")
                        sys.stdout.flush()
                        user_input = input()
                    except EOFError:
                        console.print("\n[dim]Au revoir ! 👋[/]")
                        break
                    
                    if user_input.lower() in ("quit", "exit", "q"):
                        console.print("\n[dim]Au revoir ! 👋[/]")
                        break
                    
                    if not user_input.strip():
                        continue
                    
                    # Envoyer le message avec monitoring AetherFlow
                    start_time = time.time()

                    with console.status("[cyan]🧠 Sullivan réfléchit..."):
                        response = await agent.chat(user_input)

                    total_time = (time.time() - start_time) * 1000

                    # MONITORING AETHERFLOW - Affichage détaillé des actions
                    if response.tool_calls and response.tool_results:
                        from rich.table import Table
                        from rich import box

                        # Table de monitoring
                        monitor_table = Table(
                            title="[bold cyan]⚡ SULLIVAN MONITORING[/]",
                            box=box.ROUNDED,
                            show_header=True,
                            header_style="bold white on blue"
                        )
                        monitor_table.add_column("🔧 Outil", style="cyan", width=20)
                        monitor_table.add_column("📥 Params", style="dim", width=35)
                        monitor_table.add_column("📤 Résultat", style="green", width=40)
                        monitor_table.add_column("⏱️", style="yellow", width=8)
                        monitor_table.add_column("✓", width=3)

                        per_tool_time = total_time / max(len(response.tool_calls), 1)

                        for call, result in zip(response.tool_calls, response.tool_results):
                            tool_name = call.get('tool', '?')
                            params = call.get('params', {})
                            params_str = ", ".join([f"{k}={str(v)[:20]}" for k, v in list(params.items())[:2]])
                            if len(params_str) > 35:
                                params_str = params_str[:32] + "..."

                            result_str = result.content[:40] if result.content else "-"
                            if len(result_str) > 40:
                                result_str = result_str[:37] + "..."

                            status = "[green]✓[/]" if result.success else "[red]✗[/]"
                            time_str = f"{per_tool_time:.0f}ms"

                            monitor_table.add_row(tool_name, params_str, result_str, time_str, status)

                        console.print()
                        console.print(monitor_table)

                        # Résumé
                        success_count = sum(1 for r in response.tool_results if r.success)
                        console.print(f"[dim]Total: {len(response.tool_calls)} actions | {success_count} ✅ | {total_time:.0f}ms[/]")

                    # Afficher la réponse
                    console.print(f"\n[bold cyan]💬 Sullivan:[/]")
                    console.print(response.content)
                    console.print()
                    
            except KeyboardInterrupt:
                console.print("\n\n[dim]Au revoir ! 👋[/]")
                return 0
            except Exception as e:
                console.print(f"\n[red]❌ Erreur: {e}[/]")
                return 1
            
            return 0
        
        return asyncio.run(run_sullivan_chat())
    
    # Handle sullivan cto command
    if args.command == "sullivan" and getattr(args, "sullivan_command", None) == "cto":
        async def run_sullivan_cto():
            from .sullivan.modes.cto_mode import CTOMode
            
            request = getattr(args, "request", None)
            interactive = getattr(args, "interactive", False) or not request
            
            cto = CTOMode()
            
            # Mode one-shot
            if request:
                console.print(f"\n[bold cyan]🎯 CTO Mode[/] - Analyse de la demande...")
                console.print(f"[dim]→ {request}[/]\n")
                
                with console.status("[cyan]Sullivan CTO réfléchit..."):
                    result = await cto.execute(request)
                
                # Afficher la décision
                console.print(f"[bold]📋 Décision:[/] [cyan]{result['reasoning']}[/]")
                console.print(f"[bold]🔧 Mode:[/] [green]{result['mode'].upper()}[/]")
                console.print(f"[bold]🎯 Intent:[/] {result['intent']}\n")
                
                # Afficher le résultat selon le mode
                if result['mode'] == 'direct':
                    console.print(f"[bold]💬 Réponse:[/]")
                    console.print(result['result'].get('response', 'Aucune réponse'))
                elif result['mode'] in ['frontend', 'designer']:
                    if result['result'].get('output_file'):
                        console.print(f"[bold]📄 Fichier généré:[/] [green]{result['result']['output_file']}[/]")
                    console.print(f"[dim]⏱️  Temps: {result['result'].get('time_ms', 0):.0f}ms[/]")
                    console.print(f"[dim]💰 Coût: ${result['result'].get('cost_usd', 0):.4f}[/]")
                elif result['mode'] in ['proto', 'prod']:
                    console.print(f"[bold]📄 Plan:[/] {result['result'].get('plan', 'N/A')}")
                    console.print(f"[dim]⏱️  Total: {result['result'].get('total_time_ms', 0)/1000:.1f}s[/]")
                    console.print(f"[dim]💰 Coût: ${result['result'].get('total_cost_usd', 0):.4f}[/]")
                
                console.print(f"\n[dim]✅ Exécution terminée en {result['total_time_ms']:.0f}ms[/]")
                return 0 if result['success'] else 1
            
            # Mode interactif CTO
            console.print("\n[bold cyan]🎯 Sullivan CTO[/] - Mode interactif")
            console.print("[dim]Parle-moi comme à un CTO. Je décide et j'exécute.[/]")
            console.print("[dim]Tape 'quit', 'exit' ou Ctrl+C pour quitter[/]\n")
            
            import sys
            if not sys.stdin.isatty():
                console.print("[yellow]⚠️ stdin non interactif[/]")
                return 1
            
            try:
                while True:
                    console.print("[bold green]Vous:[/] ", end="")
                    sys.stdout.flush()
                    user_input = input()
                    
                    if user_input.lower() in ("quit", "exit", "q"):
                        console.print("\n[dim]Au revoir ! 👋[/]")
                        break
                    
                    if not user_input.strip():
                        continue
                    
                    # Exécuter la demande
                    console.print(f"\n[dim]Analyse...[/]")
                    result = await cto.execute(user_input)
                    
                    # Résumé rapide
                    console.print(f"[cyan]→ {result['reasoning']}[/] ([green]{result['mode'].upper()}[/])")
                    
                    if result['mode'] == 'direct':
                        console.print(f"\n{result['result'].get('response', '')}")
                    else:
                        success = "✅" if result['success'] else "❌"
                        console.print(f"\n{success} Terminé en {result['total_time_ms']:.0f}ms")
                        if result['result'].get('output_file'):
                            console.print(f"   📄 {result['result']['output_file']}")
                    
                    console.print()
                    
            except KeyboardInterrupt:
                console.print("\n\n[dim]Au revoir ! 👋[/]")
                return 0
            except Exception as e:
                console.print(f"\n[red]❌ Erreur: {e}[/]")
                return 1
            
            return 0
        
        return asyncio.run(run_sullivan_cto())
    
    # Handle sullivan plan command (PlanBuilder)
    if args.command == "sullivan" and getattr(args, "sullivan_command", None) == "plan":
        async def run_sullivan_plan():
            from .sullivan.modes.plan_builder import PlanBuilder
            
            brief = getattr(args, "brief", None)
            interactive = getattr(args, "interactive", True)
            execute = getattr(args, "execute", False)
            output_path = getattr(args, "output", None)
            
            # Mode interactif si pas de brief
            if not brief:
                console.print("\n[bold cyan]📋 Sullivan PlanBuilder[/]")
                console.print("[dim]Décris ton projet, je vais générer un plan structuré.[/]\n")
                console.print("[bold green]Votre brief:[/] ", end="")
                import sys
                sys.stdout.flush()
                brief = input()
            
            if not brief.strip():
                console.print("[red]❌ Brief vide[/]")
                return 1
            
            # Créer le plan
            builder = PlanBuilder()
            
            try:
                plan = await builder.create_plan_from_brief(
                    brief=brief,
                    interactive=interactive
                )
                
                # Sauvegarder si output spécifié
                if output_path:
                    import shutil
                    plan_path = Path(plan.output_dir if hasattr(plan, 'output_dir') else settings.output_dir) / f"{plan.task_id}.json"
                    if plan_path.exists():
                        shutil.copy(plan_path, output_path)
                        console.print(f"[green]✓ Plan copié vers:[/] {output_path}")
                
                # Exécuter si demandé
                if execute:
                    console.print("\n[bold cyan]🚀 Exécution du plan[/]")
                    result = await builder.execute_plan_step_by_step(plan, interactive=True)
                    
                    if result['success']:
                        console.print("\n[bold green]✅ Plan exécuté avec succès![/]")
                    else:
                        console.print(f"\n[yellow]⚠️ Plan partiellement exécuté ({result['completed_steps']}/{result['total_steps']} étapes)[/]")
                else:
                    console.print("\n[dim]Pour exécuter ce plan:[/]")
                    console.print(f"  [cyan]./aetherflow-chat sullivan plan '{brief}' --execute[/]")
                    console.print(f"  [cyan]./aetherflow -q --plan output/plans/{plan.task_id}.json[/]")
                
                return 0
                
            except Exception as e:
                console.print(f"\n[red]❌ Erreur: {e}[/]")
                import traceback
                traceback.print_exc()
                return 1
        
        return asyncio.run(run_sullivan_plan())
    
    # sullivan sans sous-commande ni --design ni --build → aide
    if args.command == "sullivan" and not getattr(args, "design", None) and not getattr(args, "build", False) and not getattr(args, "sullivan_command", None):
        console.print("[dim]Usage:[/] [cyan]aetherflow sullivan -d image.png[/] (designer)  |  [cyan]sullivan -b[/] (build)  |  [cyan]sullivan plan-screens[/]  |  [cyan]sullivan dev --backend-path ...[/]  |  [cyan]sullivan build[/]  |  [cyan]sullivan read-genome[/]  |  [cyan]sullivan frd <action>[/] (frontend)  |  [cyan]sullivan chat[/] (agent)  |  [cyan]sullivan cto[/] (CTO)  |  [cyan]sullivan plan[/] (PlanBuilder)")
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
    elif args.quick or args.fast:
        workflow_type = "PROTO"
    elif args.full or args.build:
        workflow_type = "PROD"
    elif getattr(args, "verify_fix", False):
        workflow_type = "VerifyFix"
    elif getattr(args, "frd_quick", False):
        workflow_type = "frd-quick"
    elif getattr(args, "frd_full", False):
        workflow_type = "frd-full"
    elif getattr(args, "frd_vfx", False):
        workflow_type = "frd-vfx"

    # Debug API keys if requested (before any other action)
    if args.debug_keys:
        from .debug_keys import run_debug_keys
        run_debug_keys(verbose=True)
        print()
    
    # Require plan for workflow execution
    if workflow_type and not args.plan:
        console.print("[red]Error: --plan is required for -q / -f / -vfx workflows[/]")
        return 1
    
    # Check if plan file exists (if provided); resolve to absolute so workflows read the intended file
    if args.plan:
        if not args.plan.exists():
            console.print(f"[red]Error: Plan file not found: {args.plan}[/]")
            return 1
        args.plan = args.plan.resolve()
    
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

        # FRD-QUICK workflow (--frd-quick)
        elif workflow_type == "frd-quick":
            async def run_frd_quick():
                from .workflows.frd import FrdWorkflow
                workflow = FrdWorkflow(variant="quick")
                result = await workflow.execute(
                    plan_path=args.plan,
                    output_dir=output_dir,
                    context=args.context
                )

                summary_table = Table(title="FRD-QUICK Summary", box=box.ROUNDED)
                summary_table.add_column("Metric", style="cyan")
                summary_table.add_column("Value", style="green")
                summary_table.add_row("Workflow", "FRD-QUICK (KIMI fast)")
                summary_table.add_row("Files Applied", str(result["code_applied"]["files_applied"]))
                summary_table.add_row("Total Time", f"{result['total_time_ms']/1000:.2f}s")
                summary_table.add_row("Total Cost", f"${result['total_cost_usd']:.4f}")
                summary_table.add_row("Success", "✓" if result["success"] else "✗")
                console.print(summary_table)

                return 0 if result["success"] else 1

            return asyncio.run(run_frd_quick())

        # FRD-FULL workflow (--frd-full)
        elif workflow_type == "frd-full":
            async def run_frd_full():
                from .workflows.frd import FrdWorkflow
                workflow = FrdWorkflow(variant="full")
                result = await workflow.execute(
                    plan_path=args.plan,
                    output_dir=output_dir,
                    context=args.context
                )

                summary_table = Table(title="FRD-FULL Summary", box=box.ROUNDED)
                summary_table.add_column("Metric", style="cyan")
                summary_table.add_column("Value", style="green")
                summary_table.add_row("Workflow", "FRD-FULL (KIMI → DeepSeek → Gemini)")
                summary_table.add_row("Files Applied", str(result["code_applied"]["files_applied"]))
                summary_table.add_row("Total Time", f"{result['total_time_ms']/1000:.2f}s")
                summary_table.add_row("Total Cost", f"${result['total_cost_usd']:.4f}")
                summary_table.add_row("Success", "✓" if result["success"] else "✗")
                console.print(summary_table)

                return 0 if result["success"] else 1

            return asyncio.run(run_frd_full())

        # FRD-VFX workflow (--frd-vfx)
        elif workflow_type == "frd-vfx":
            async def run_frd_vfx():
                from .workflows.frd import FrdWorkflow
                workflow = FrdWorkflow(variant="vfx")
                result = await workflow.execute(
                    plan_path=args.plan,
                    output_dir=output_dir,
                    context=args.context
                )

                summary_table = Table(title="FRD-VFX Summary", box=box.ROUNDED)
                summary_table.add_column("Metric", style="cyan")
                summary_table.add_column("Value", style="green")
                summary_table.add_row("Workflow", "FRD-VFX (KIMI → TEST → VERIFY → FIX)")
                summary_table.add_row("Files Applied", str(result.get("code_applied", {}).get("files_applied", 0)))
                summary_table.add_row("Total Time", f"{result['total_time_ms']/1000:.2f}s")
                summary_table.add_row("Total Cost", f"${result['total_cost_usd']:.4f}")
                summary_table.add_row("Success", "✓" if result["success"] else "✗")
                console.print(summary_table)

                return 0 if result["success"] else 1

            return asyncio.run(run_frd_vfx())

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
                use_streaming=args.streaming,
                sequential=args.sequential
            ))
        else:
            console.print("[red]Error: --plan is required. Use -q / -f / -vfx or --workflow quick|full|verify-fix[/]")
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