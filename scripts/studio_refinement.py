#!/usr/bin/env python3
"""Run Studio workflow: genome → build → refinement (Homeos Studio)."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


async def main() -> int:
    from Backend.Prod.config.settings import settings
    from Backend.Prod.core.genome_generator import generate_genome
    from Backend.Prod.sullivan.refinement import run_refinement

    base = Path(settings.output_dir) / "studio"
    base.mkdir(parents=True, exist_ok=True)
    genome_path = base / "homeos_genome.json"
    html_path = base / "studio_index.html"

    print("1. Genome")
    if not genome_path.exists():
        generate_genome(output_path=genome_path)
        print(f"   Generated: {genome_path}")
    else:
        print(f"   Using: {genome_path}")

    print("2. Build + Refinement (build → screenshot → audit → revise until score > 85)")
    path, html, audit = await run_refinement(
        genome_path,
        output_path=html_path,
        base_url="http://localhost:8000",
        max_iterations=5,
        score_threshold=85,
    )
    print(f"   Wrote: {path}")
    if audit:
        print(f"   Final visual_score: {audit.visual_score}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
