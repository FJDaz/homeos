#!/usr/bin/env python3
"""Debug toutes les clés API (env vs .env, ascii, placeholder)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from Backend.Prod.debug_keys import run_debug_keys

if __name__ == "__main__":
    run_debug_keys(verbose=True)
    sys.exit(0)
