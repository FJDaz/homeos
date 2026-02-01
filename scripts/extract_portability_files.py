#!/usr/bin/env python3
"""Extract code blocks from AETHERFLOW portability step outputs."""
import re
from pathlib import Path

def extract_code_blocks(file_path, language=None):
    """Extract code blocks from markdown file"""
    content = Path(file_path).read_text()
    lang_pattern = language or r'\w+'
    pattern = rf'```{lang_pattern}\n(.*?)```'
    matches = re.finditer(pattern, content, re.DOTALL)
    blocks = []
    for match in matches:
        blocks.append(match.group(1).strip())
    return blocks

def main():
    base_dir = Path(__file__).parent.parent
    
    # Extract install.sh from step_6
    step6_path = base_dir / 'output/portabilite_aetherflow/step_outputs/step_6.txt'
    if step6_path.exists():
        blocks = extract_code_blocks(step6_path, 'bash')
        if blocks:
            install_script = blocks[0]
            output_file = base_dir / 'scripts/install.sh'
            output_file.write_text(install_script)
            output_file.chmod(0o755)
            print(f'✅ {output_file} créé')

    # Extract pyinstaller_mac.sh from step_4
    step4_path = base_dir / 'output/portabilite_aetherflow/step_outputs/step_4.txt'
    if step4_path.exists():
        blocks = extract_code_blocks(step4_path, 'bash')
        if blocks:
            mac_script = blocks[0]
            output_file = base_dir / 'scripts/packaging/pyinstaller_mac.sh'
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(mac_script)
            output_file.chmod(0o755)
            print(f'✅ {output_file} créé')

    # Extract pyinstaller scripts from step_5
    step5_path = base_dir / 'output/portabilite_aetherflow/step_outputs/step_5.txt'
    if step5_path.exists():
        blocks = extract_code_blocks(step5_path, 'bash')
        if len(blocks) >= 1:
            output_file = base_dir / 'scripts/packaging/pyinstaller_linux.sh'
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(blocks[0])
            output_file.chmod(0o755)
            print(f'✅ {output_file} créé')
        # Check for Windows batch file
        content = step5_path.read_text()
        bat_pattern = r'```(?:bat|batch|cmd)\n(.*?)```'
        bat_matches = re.finditer(bat_pattern, content, re.DOTALL)
        bat_blocks = [m.group(1).strip() for m in bat_matches]
        if bat_blocks:
            output_file = base_dir / 'scripts/packaging/pyinstaller_windows.bat'
            output_file.write_text(bat_blocks[0])
            print(f'✅ {output_file} créé')

    # Extract test_portability.sh from step_8
    step8_path = base_dir / 'output/portabilite_aetherflow/step_outputs/step_8.txt'
    if step8_path.exists():
        blocks = extract_code_blocks(step8_path, 'bash')
        if blocks:
            output_file = base_dir / 'scripts/test_portability.sh'
            output_file.write_text(blocks[0])
            output_file.chmod(0o755)
            print(f'✅ {output_file} créé')

    # Extract INSTALLATION.md from step_7
    step7_path = base_dir / 'output/portabilite_aetherflow/step_outputs/step_7.txt'
    if step7_path.exists():
        content = step7_path.read_text()
        # Find markdown content after separator
        parts = content.split('============================================================')
        if len(parts) > 1:
            md_content = parts[-1].strip()
            # Remove step metadata
            lines = md_content.split('\n')
            start_idx = 0
            for i, line in enumerate(lines):
                if line.startswith('#') and not line.startswith('###'):
                    start_idx = i
                    break
            md_content = '\n'.join(lines[start_idx:])
            output_file = base_dir / 'docs/INSTALLATION.md'
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(md_content)
            print(f'✅ {output_file} créé')

    print('\n✅ Extraction terminée!')

if __name__ == '__main__':
    main()
