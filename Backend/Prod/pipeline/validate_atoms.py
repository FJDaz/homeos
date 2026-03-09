"""validate_atoms.py — Quality Control for KIMI generated SVGs.

Checks for:
1. No serif fonts (Times New Roman, Georgia, serif).
2. Border-radius (rx, ry) <= 12.
3. No array-syntax radius (rx="0 0 8 8").
4. No 'undefined' strings.
"""
import os
import re
import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
pipeline_dir = project_root / "exports/pipeline"
atoms_dir = pipeline_dir / "atoms"

# Regex patterns: exclude 'sans-serif' but catch 'serif', 'Times', 'Georgia'
SERIF_PATTERN = re.compile(r'font-family\s*=\s*["\'][^"\']*(?<!sans-)serif[^"\']*["\']|Times|Georgia', re.I)
RX_PATTERN = re.compile(r'rx\s*=\s*["\']([^"\']+)["\']')
RY_PATTERN = re.compile(r'ry\s*=\s*["\']([^"\']+)["\']')
UNDEFINED_PATTERN = re.compile(r'\b(?:undefined|NaN|null)\b', re.I)

import xml.etree.ElementTree as ET

def validate_svg(path: Path) -> list[str]:
    errors = []
    content = path.read_text(encoding="utf-8")

    # 0. XML check
    try:
        ET.fromstring(content)
    except ET.ParseError as pe:
        errors.append(f"Invalid XML syntax: {pe}")
        return errors # Stop checking if it's completely broken

    # 1. Font check
    if SERIF_PATTERN.search(content):
        errors.append("Serif font detected")

    # 2. Radius check
    for match in RX_PATTERN.finditer(content):
        val = match.group(1)
        if " " in val:
            errors.append(f"Array radius detected: rx='{val}'")
        else:
            try:
                if float(val) > 10:
                    errors.append(f"Radius too large: rx={val}")
            except ValueError:
                pass

    for match in RY_PATTERN.finditer(content):
        val = match.group(1)
        if " " in val:
            errors.append(f"Array radius detected: ry='{val}'")
        else:
            try:
                if float(val) > 10:
                    errors.append(f"Radius too large: ry={val}")
            except ValueError:
                pass

    # 3. Undefined check
    if UNDEFINED_PATTERN.search(content):
        errors.append("Undefined/NaN/Null string detected")

    return errors

def main():
    if not atoms_dir.exists():
        print(f"❌ Atoms directory not found: {atoms_dir}")
        sys.exit(1)

    svgs = list(atoms_dir.glob("*.svg"))
    print(f"🔍 Validating {len(svgs)} atoms...")

    all_errors = {}
    for svg_path in svgs:
        errors = validate_svg(svg_path)
        if errors:
            all_errors[svg_path.name] = errors
            print(f"  ❌ {svg_path.name}: {', '.join(errors)}")

    if not all_errors:
        print("✅ All atoms passed validation!")
        sys.exit(0)
    else:
        print(f"\n❌ {len(all_errors)} atoms failed validation.")
        # Save validation report
        report_path = pipeline_dir / "validation_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(all_errors, f, indent=2)
        print(f"📄 Validation report saved to {report_path}")
        sys.exit(1)

if __name__ == "__main__":
    main()
