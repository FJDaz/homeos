"""HomeOS CLI: mode display and switch (construction / project)."""

import argparse
import sys


def cmd_mode() -> int:
    """Print current mode from mode_manager.get_mode_info()."""
    from homeos.core.mode_manager import mode_manager

    try:
        info = mode_manager.get_mode_info()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    print(f"mode: {info.get('mode', 'unknown')}")
    print(f"config_path: {info.get('config_path', '')}")
    z = info.get('z_index_layers')
    print(f"z_index_layers: {z}")
    return 0


def cmd_switch(construction: bool, project: bool) -> int:
    """Switch to construction or project mode."""
    from homeos.core.mode_manager import mode_manager, HomeosMode

    if construction and project:
        print("Error: use either --construction or --project, not both.", file=sys.stderr)
        return 1
    if not construction and not project:
        print("Error: use --construction or --project.", file=sys.stderr)
        return 1
    try:
        target = HomeosMode.CONSTRUCTION if construction else HomeosMode.PROJECT
        mode_manager.switch_mode(target)
        print(f"Switched to {target.value}.")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(prog="homeos", description="HomeOS mode and switch.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("mode", help="Show current mode and config path")

    switch_parser = subparsers.add_parser("switch", help="Switch to construction or project mode")
    switch_parser.add_argument("--construction", action="store_true", help="Switch to construction mode")
    switch_parser.add_argument("--project", action="store_true", help="Switch to project mode")

    args = parser.parse_args()
    if args.command == "mode":
        return cmd_mode()
    if args.command == "switch":
        return cmd_switch(
            getattr(args, "construction", False),
            getattr(args, "project", False),
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())