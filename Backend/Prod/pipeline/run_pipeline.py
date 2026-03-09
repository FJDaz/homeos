"""run_pipeline.py — Orchestrateur pipeline KIMI Design.

Usage:
  python run_pipeline.py                          # run complet (steps 1-7)
  python run_pipeline.py --from 5 --theme jackryan  # changer la référence WP
  python run_pipeline.py --from 6                 # re-composer (boucle acceptation)
  python run_pipeline.py --from 6 --feedback "les headers sont trop petits"
  python run_pipeline.py --from 7                 # re-composer seulement
"""
import argparse
import subprocess
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
pipeline_dir = Path(__file__).parent

STEPS = {
    1: ("01_zone_planner.py",      "Zone Planner       — genome → zone_map.json"),
    2: ("02_kimi_layout_director.py", "KIMI Layout Director — zone_map → layout_plan.json"),
    3: ("03_scaffold_generator.py","Scaffold Generator  — layout_plan → scaffold SVG (light placeholders)"),
    4: ("04_kimi_atom_factory.py", "KIMI Atom Factory   — 32 components → atoms/*.svg (4 workers)"),
    5: ("05_wp_reference.py",      "WP Reference        — theme tokens → wp_reference.json"),
    6: ("06_kimi_composer.py",     "KIMI Composer       — WP align → refined_plan.json"),
    7: ("07_composer.py",          "Composer            — atoms + plan → template_*.svg"),
}


def run_step(step_num: int, extra_args: list[str] = None) -> bool:
    script, label = STEPS[step_num]
    print(f"\n{'─'*60}")
    print(f"Step {step_num}/7 — {label}")
    print(f"{'─'*60}")

    cmd = [sys.executable, str(pipeline_dir / script)] + (extra_args or [])
    result = subprocess.run(cmd, cwd=str(project_root))
    if result.returncode != 0:
        print(f"❌ Step {step_num} failed (exit code {result.returncode})")
        return False
    return True


def open_preview(path: Path):
    """Open the SVG in Preview (macOS)."""
    if path.exists():
        os.system(f'open "{path}"')


def acceptance_loop(args):
    """Loop: run step 6+7, show result, ask FJD to accept or give feedback."""
    iteration = 0
    while True:
        iteration += 1
        print(f"\n{'='*60}")
        print(f"🔄 Iteration {iteration}")
        print(f"{'='*60}")

        feedback_args = ["--feedback", args.feedback] if args.feedback else []
        if not run_step(6, feedback_args):
            return False
        if not run_step(7):
            return False

        latest = project_root / "exports" / "template_latest.svg"
        open_preview(latest)

        print(f"\n{'='*60}")
        print(f"📋 Template ready: {latest}")
        print("Accept? [y = accept, n = retry, or type feedback then Enter]")
        print(f"{'='*60}")

        try:
            answer = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n⛔ Interrupted")
            return False

        if answer.lower() == "y":
            print("✅ Template accepted!")
            # Save as FINAL
            import shutil
            from datetime import datetime
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            final = project_root / "exports" / f"FINAL_template_{ts}.svg"
            shutil.copy(latest, final)
            print(f"💾 Saved: {final.name}")
            return True
        elif answer.lower() == "n":
            args.feedback = ""
            print("↩️  Retrying without feedback...")
        else:
            args.feedback = answer
            print(f"↩️  Retrying with feedback: {answer}")


def main():
    parser = argparse.ArgumentParser(description="AetherFlow KIMI Design Pipeline")
    parser.add_argument("--from", dest="from_step", type=int, default=1,
                        help="Start from step N (1-7, default=1)")
    parser.add_argument("--theme", default="most",
                        choices=["most", "osty", "nicex", "mokko", "jackryan", "siberia", "emilynolan"],
                        help="WP reference theme")
    parser.add_argument("--feedback", default="",
                        help="FJD feedback for step 6 (acceptance loop)")
    parser.add_argument("--no-loop", action="store_true",
                        help="Skip acceptance loop, just run steps once")
    parser.add_argument("--context", type=str, default="",
                        help="Path to a context document (e.g. MANIFEST_FRD.md) to inject into KIMI prompts")
    args = parser.parse_args()

    start = args.from_step
    print(f"\n{'='*60}")
    print(f"🚀 AetherFlow KIMI Design Pipeline")
    print(f"   Starting from step {start} — theme: {args.theme}")
    if args.feedback:
        print(f"   Feedback: {args.feedback}")
    if args.context:
        print(f"   Context Injection: {args.context}")
    print(f"{'='*60}")
    
    # Read Context File
    context_text = ""
    if args.context:
        context_path = Path(args.context)
        if not context_path.is_absolute():
            context_path = project_root / context_path
        if context_path.exists():
            context_text = context_path.read_text(encoding="utf-8")
        else:
            print(f"⚠️  Context file not found at {context_path}")

    # Steps 1-5 run once
    for step in range(start, min(6, 8)):
        extra = []
        if step == 2 and context_text:
            extra = ["--context_text", context_text]
        if step == 4 and context_text:
            extra = ["--context_text", context_text]
        if step == 5:
            extra = ["--theme", args.theme]
        if not run_step(step, extra):
            print(f"\n❌ Pipeline aborted at step {step}")
            sys.exit(1)
        
        # Post-Step 4 Validation
        if step == 4:
            print(f"\n{'─'*60}")
            print(f"Step 4.5 — Quality Control — validate_atoms.py")
            print(f"{'─'*60}")
            v_cmd = [sys.executable, str(pipeline_dir / "validate_atoms.py")]
            v_result = subprocess.run(v_cmd, cwd=str(project_root))
            if v_result.returncode != 0:
                print(f"⚠️  Quality Control failed. Launching surgical auto-patching...")
                p_cmd = [sys.executable, str(pipeline_dir / "surgical_patch_atoms.py")]
                p_result = subprocess.run(p_cmd, cwd=str(project_root))
                if p_result.returncode == 0:
                    print(f"✅ All atoms corrected surgically.")
                else:
                    print(f"❌ Surgical patching failed for some atoms. Manual review required.")

    # Step 6+7 = acceptance loop (unless --no-loop)
    if start <= 6:
        if args.no_loop:
            feedback_args = ["--feedback", args.feedback] if args.feedback else []
            if not run_step(6, feedback_args):
                sys.exit(1)
            if not run_step(7):
                sys.exit(1)
            print("\n✅ Pipeline complete (no acceptance loop)")
        else:
            if not acceptance_loop(args):
                sys.exit(1)
    elif start == 7:
        if not run_step(7):
            sys.exit(1)

    print("\n🎉 Pipeline complete!")
    print(f"   Template: exports/template_latest.svg")
    print(f"   Open with: open {project_root}/exports/template_latest.svg")


if __name__ == "__main__":
    main()
