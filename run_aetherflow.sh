#!/bin/bash
# Wrapper script to run AETHERFLOW bypassing Cursor shell hooks
# Usage: ./run_aetherflow.sh -q --plan <plan.json>
#        ./run_aetherflow.sh -f --plan <plan.json> --output <dir>
#        ./run_aetherflow.sh --costs
#        ./run_aetherflow.sh --stats
# Uses venv or .venv if present, else python3.

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [ -x "$ROOT/venv/bin/python" ]; then
  PYTHON="$ROOT/venv/bin/python"
elif [ -x "$ROOT/.venv/bin/python" ]; then
  PYTHON="$ROOT/.venv/bin/python"
else
  PYTHON=python3
fi

# _ is $0 for the -c script; $PYTHON and args follow
exec /bin/bash -c '"$1" -m Backend.Prod.cli "${@:2}"' _ "$PYTHON" "$@"
