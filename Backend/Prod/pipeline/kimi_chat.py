#!/usr/bin/env python3
"""KIMI Console Chat — boucle HCI interactive en mode terminal.

Affiche le template dans le browser (auto-refresh toutes les 3s).
Tu donnes ton feedback ici → KIMI re-compose → template se met à jour.

Usage:
  python Backend/Prod/pipeline/kimi_chat.py
  python Backend/Prod/pipeline/kimi_chat.py --feedback "plus de contraste"
"""
import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
pipeline_dir = Path(__file__).parent


def run_step(script: str, extra_args: list[str] | None = None) -> bool:
    cmd = [sys.executable, str(pipeline_dir / script)] + (extra_args or [])
    result = subprocess.run(cmd, cwd=str(project_root))
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--feedback", default="", help="Feedback initial pour step 6")
    args = parser.parse_args()

    print("\n🎨 KIMI Console — Design Loop")
    print("   Browser : http://localhost:9998/template-viewer")
    print("   Commandes : y=accepter | n=retry | texte=feedback | q=quitter")
    print("─" * 60)

    feedback = args.feedback
    iteration = 0

    while True:
        iteration += 1
        print(f"\n🔄 Iteration #{iteration}" + (f" — feedback: {feedback}" if feedback else ""))

        step6_args = ["--feedback", feedback] if feedback else []
        if not run_step("06_kimi_composer.py", step6_args):
            print("❌ Step 6 (KIMI Composer) failed")
            sys.exit(1)

        if not run_step("07_composer.py"):
            print("❌ Step 7 (Composer) failed")
            sys.exit(1)

        print("\n✅ Template régénéré — http://localhost:9998/template-viewer (auto-refresh)")
        print("Accept? [y = FINAL | n = retry | texte = feedback | q = quit]")

        try:
            answer = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n⛔ Interrupted")
            sys.exit(0)

        if answer.lower() == "y":
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            final = project_root / "exports" / f"FINAL_template_{ts}.svg"
            shutil.copy(project_root / "exports" / "template_latest.svg", final)
            print(f"💾 FINAL saved → exports/FINAL_template_{ts}.svg")
            sys.exit(0)
        elif answer.lower() in ("q", "quit", "exit"):
            print("👋 Bye")
            sys.exit(0)
        elif answer.lower() == "n":
            feedback = ""
            print("↩️  Retry sans feedback")
        else:
            feedback = answer
            print(f"↩️  Feedback : {feedback}")


if __name__ == "__main__":
    main()
