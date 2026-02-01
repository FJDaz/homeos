"""Simplified CLI for code generation (Option B - Claude Code First)."""
import asyncio
import sys
import argparse
from pathlib import Path
from typing import Optional
from loguru import logger

from .models.agent_router import AgentRouter
from .config.settings import settings


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    log_level = "DEBUG" if verbose else "WARNING"  # Quiet by default for CLI usage
    
    # Remove default handler
    logger.remove()
    
    # Add console handler only if verbose
    if verbose:
        logger.add(
            sys.stderr,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            level=log_level,
            colorize=True
        )


async def generate_code(
    task: str,
    context: Optional[str] = None,
    context_file: Optional[Path] = None,
    provider: Optional[str] = None,
    output: Optional[Path] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    verbose: bool = False
) -> int:
    """
    Generate code using AETHERFLOW.
    
    Args:
        task: Task description
        context: Additional context string
        context_file: Path to file containing context
        provider: Provider name or "auto" for automatic selection
        output: Output file path (if None, prints to stdout)
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        verbose: Enable verbose logging
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    router = AgentRouter()
    
    try:
        # Load context from file if provided
        if context_file:
            if not context_file.exists():
                logger.error(f"Context file not found: {context_file}")
                return 1
            with open(context_file, "r", encoding="utf-8") as f:
                file_context = f.read()
                context = f"{context}\n\n{file_context}" if context else file_context
        
        # Generate code
        result = await router.generate(
            task=task,
            context=context,
            provider=provider or "auto",
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        if not result.success:
            logger.error(f"Generation failed: {result.error}")
            if verbose:
                print(f"Error: {result.error}", file=sys.stderr)
            return 1
        
        # Output code
        if output:
            output.parent.mkdir(parents=True, exist_ok=True)
            with open(output, "w", encoding="utf-8") as f:
                f.write(result.code)
            if verbose:
                print(f"Code written to: {output}", file=sys.stderr)
                print(f"Provider: {result.provider}, Tokens: {result.tokens_used}, Cost: ${result.cost_usd:.4f}", file=sys.stderr)
        else:
            # Print to stdout (for Claude Code to capture)
            print(result.code)
            if verbose:
                print(f"\n# Provider: {result.provider}, Tokens: {result.tokens_used}, Cost: ${result.cost_usd:.4f}", file=sys.stderr)
        
        return 0
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if verbose:
            logger.exception("Unexpected error")
        return 1
    finally:
        await router.close()


def main() -> int:
    """Main entry point for generate command."""
    parser = argparse.ArgumentParser(
        description="AETHERFLOW Generate - Simple code generation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --task "Crée une fonction Python qui valide un email"
  %(prog)s --task "Crée un middleware JWT" --provider deepseek --output middleware.py
  %(prog)s --task "Refactorise cette fonction" --context-file src/utils.py --provider auto
        """
    )
    
    parser.add_argument(
        "--task",
        type=str,
        required=True,
        help="Task description (what code to generate)"
    )
    
    parser.add_argument(
        "--context",
        type=str,
        default=None,
        help="Additional context (framework, language, etc.)"
    )
    
    parser.add_argument(
        "--context-file",
        type=Path,
        default=None,
        help="Path to file containing context (e.g., existing code to refactor)"
    )
    
    parser.add_argument(
        "--provider",
        type=str,
        default="auto",
        choices=["auto", "deepseek", "codestral", "gemini", "groq"],
        help="Provider to use (default: auto)"
    )
    
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Output file path (default: stdout)"
    )
    
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=None,
        help="Maximum tokens to generate"
    )
    
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="Sampling temperature (0.0-1.0)"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(verbose=args.verbose)
    
    # Execute generation
    try:
        return asyncio.run(generate_code(
            task=args.task,
            context=args.context,
            context_file=args.context_file,
            provider=args.provider,
            output=args.output,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
            verbose=args.verbose
        ))
    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        if args.verbose:
            logger.exception("Fatal error")
        return 1


if __name__ == "__main__":
    sys.exit(main())
