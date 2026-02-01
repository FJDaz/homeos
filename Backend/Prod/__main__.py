"""CLI entry point for AetherFlow."""
import sys
import argparse
from pathlib import Path

# Import main functions
from .cli import main as plan_main
from .cli_generate import generate_code
import asyncio


def main() -> int:
    """Main entry point with subcommands."""
    parser = argparse.ArgumentParser(
        description="AETHERFLOW - Orchestrateur d'Agents IA",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Plan command (original CLI)
    plan_parser = subparsers.add_parser(
        "plan",
        help="Execute a plan JSON file (original workflow)"
    )
    plan_parser.add_argument("--plan", type=Path, required=True, help="Path to plan JSON file")
    plan_parser.add_argument("--output", type=Path, default=None, help="Output directory")
    plan_parser.add_argument("--context", type=str, default=None, help="Additional context")
    plan_parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    plan_parser.add_argument("--info", action="store_true", help="Show plan information and exit")
    
    # Generate command (new simplified CLI)
    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate code directly (Option B - Claude Code First)"
    )
    generate_parser.add_argument("--task", type=str, required=True, help="Task description")
    generate_parser.add_argument("--context", type=str, default=None, help="Additional context")
    generate_parser.add_argument("--context-file", type=Path, default=None, help="Path to context file")
    generate_parser.add_argument("--provider", type=str, default="auto", choices=["auto", "deepseek", "codestral", "gemini", "groq"], help="Provider to use")
    generate_parser.add_argument("--output", "-o", type=Path, default=None, help="Output file path (default: stdout)")
    generate_parser.add_argument("--max-tokens", type=int, default=None, help="Maximum tokens to generate")
    generate_parser.add_argument("--temperature", type=float, default=None, help="Sampling temperature")
    generate_parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == "plan":
        # Call original CLI with plan arguments
        # Reconstruct sys.argv for the original CLI
        original_argv = ["cli"]
        if args.plan:
            original_argv.extend(["--plan", str(args.plan)])
        if args.output:
            original_argv.extend(["--output", str(args.output)])
        if args.context:
            original_argv.extend(["--context", args.context])
        if args.verbose:
            original_argv.append("--verbose")
        if args.info:
            original_argv.append("--info")
        
        old_argv = sys.argv
        sys.argv = original_argv
        try:
            return plan_main()
        finally:
            sys.argv = old_argv
            
    elif args.command == "generate":
        # Call generate function directly
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
            print("\nInterrupted by user", file=sys.stderr)
            return 130
        except Exception as e:
            print(f"Fatal error: {e}", file=sys.stderr)
            if args.verbose:
                import traceback
                traceback.print_exc()
            return 1
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
