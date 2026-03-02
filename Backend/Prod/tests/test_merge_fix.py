import pytest
from pathlib import Path
from Backend.Prod.claude_helper import merge_step_outputs_to_file, get_step_output

def test_merge_step_outputs_to_file(tmp_path):
    # Setup step outputs
    out_dir = tmp_path / "output"
    steps_dir = out_dir / "step_outputs"
    steps_dir.mkdir(parents=True)
    
    (steps_dir / "step_1_code.txt").write_text("code1")
    (steps_dir / "step_2_code.txt").write_text("code2")
    
    target_file = tmp_path / "merged.txt"
    
    # Test merge
    success = merge_step_outputs_to_file(["step_1", "step_2"], str(out_dir), target_file)
    
    assert success
    assert target_file.exists()
    assert target_file.read_text() == "code1\n\ncode2"

def test_merge_step_outputs_to_file_missing_step(tmp_path):
    out_dir = tmp_path / "output"
    steps_dir = out_dir / "step_outputs"
    steps_dir.mkdir(parents=True)
    
    (steps_dir / "step_1_code.txt").write_text("code1")
    
    target_file = tmp_path / "merged_partial.txt"
    
    # Test merge with one missing step
    success = merge_step_outputs_to_file(["step_1", "step_missing"], str(out_dir), target_file)
    
    assert success
    assert target_file.read_text() == "code1"
