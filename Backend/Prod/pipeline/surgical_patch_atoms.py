"""surgical_patch_atoms.py — Corrects failed atoms using KIMI.

Reads validation_report.json and sends targeted correction prompts for each failed SVG.
"""
import json
import os
import sys
import re
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

project_root = Path(__file__).parent.parent.parent.parent
load_dotenv(project_root / "Backend/.env")

pipeline_dir = project_root / "exports/pipeline"
atoms_dir = pipeline_dir / "atoms"
report_path = pipeline_dir / "validation_report.json"

CORRECTION_PROMPT = """You are a Lead UI Designer. The following SVG component has design violations that MUST be fixed.

VIOLATIONS FOUND:
{errors}

ORIGINAL SVG:
{svg_content}

TASK:
1. Fix the violations (remove serif fonts, cap radius at 10-12px, fix undefined strings).
2. Maintain the EXACT same visual structure and high-fidelity feel.
3. Output ONLY the corrected <svg>...</svg> block. No markdown, no commentary."""

def patch_atom(client, filename: str, errors: list[str]) -> bool:
    svg_path = atoms_dir / filename
    if not svg_path.exists():
        return False

    content = svg_path.read_text(encoding="utf-8")
    prompt = CORRECTION_PROMPT.format(
        errors="\n".join([f"- {e}" for e in errors]),
        svg_content=content
    )

    print(f"  🔧 Patching {filename}...")
    try:
        response = client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=[
                {"role": "system", "content": "You are a precise SVG editor. Fix the SVG as requested."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=8192,
            response_format={"type": "json_object"} if False else None # Gemini flash supports JSON but here we want raw SVG
        )
        new_content = response.choices[0].message.content or ""
        if "<svg" in new_content:
            start_idx = new_content.find("<svg")
            end_idx = new_content.rfind("</svg>")
            if end_idx != -1:
                svg = new_content[start_idx:end_idx + 6]
            else:
                # If closing tag is missing, the generation was truncated.
                print(f"    ⚠️ {filename}: Gemini output truncated (missing </svg>).")
                return False
            
            # Strict XML validation before saving
            import xml.etree.ElementTree as ET
            try:
                ET.fromstring(svg)
            except ET.ParseError as pe:
                print(f"    ⚠️ {filename}: Patched SVG is invalid XML ({pe}).")
                return False

            svg_path.write_text(svg, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def main():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not set")
        sys.exit(1)

    if not report_path.exists():
        print("✅ No validation report found. Nothing to patch.")
        sys.exit(0)

    with open(report_path, encoding="utf-8") as f:
        report = json.load(f)

    if not report:
        print("✅ Validation report is empty.")
        sys.exit(0)

    client = OpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=api_key
    )
    print(f"🩹 Starting surgical patching for {len(report)} atoms (8 concurrent workers)...")

    from concurrent.futures import ThreadPoolExecutor
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(patch_atom, client, filename, errors): filename for filename, errors in report.items()}
        
        success_count = 0
        for future in futures:
            filename = futures[future]
            try:
                if future.result():
                    success_count += 1
                    print(f"    ✅ {filename} corrected.")
                else:
                    print(f"    ❌ {filename} failed to patch.")
            except Exception as e:
                print(f"    ❌ {filename} error: {e}")

    print(f"\n🎉 Patching complete: {success_count}/{len(report)} atoms fixed.")
    if success_count == len(report):
        # Clear the report if everything is fixed
        if report_path.exists():
            report_path.unlink()
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
