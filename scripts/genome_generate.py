#!/usr/bin/env python3
"""Génère le Genome (homeos_genome.json) depuis l'API Homeos."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from Backend.Prod.core.genome_generator import run_genome_cli

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else None
    sys.exit(run_genome_cli(output_path=out))
