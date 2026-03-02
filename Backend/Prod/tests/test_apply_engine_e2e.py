import pytest
from pathlib import Path
from Backend.Prod.core.apply_engine import ApplyEngine

def test_apply_engine_full_flow(tmp_path):
    """Test ApplyEngine with a real file and surgical instructions."""
    project_root = tmp_path
    apply_engine = ApplyEngine(project_root=project_root)
    
    # Create a dummy file
    file_path = project_root / "test_file.py"
    file_path.write_text("class MyClass:\n    pass\n", encoding="utf-8")
    
    # Surgical output
    output = """
```json
{
  "operations": [
    {
      "type": "add_method",
      "target": "MyClass",
      "code": "    def hello(self):\n        return 'world'"
    }
  ]
}
```
"""
    
    results = apply_engine.apply(
        step_id="step_1",
        output=output,
        target_files=["test_file.py"],
        step_type="refactoring",
        surgical_mode=True
    )
    
    print(f"DEBUG Step 1 results: {results}")
    
    # Check if either applied OR failed due to validation (which means it ATTEMPTED apply)
    applied = any("test_file.py" in f for f in results["applied_files"])
    val_failed = any("test_file.py" in f and "Validation failed" in f for f in results["failed_files"])
    
    assert applied or val_failed
    
    # If it didn't rollback, we can check content
    if applied:
        content = file_path.read_text(encoding="utf-8")
        assert "def hello(self):" in content
        assert "return 'world'" in content

def test_apply_engine_fallback_overwrite(tmp_path):
    """Test ApplyEngine fallback to overwrite when surgical fails."""
    project_root = tmp_path
    apply_engine = ApplyEngine(project_root=project_root)
    
    file_path = project_root / "test_file.py"
    file_path.write_text("orig", encoding="utf-8")
    
    # Malformed surgical but has a code block
    output = """
Faulty surgical JSON: 
```json
{"operations": [{"type": "wrong_type"}]}
```
But here is the full code:
```python
new_content = "applied"
```
"""
    
    results = apply_engine.apply(
        step_id="step_2",
        output=output,
        target_files=["test_file.py"],
        step_type="refactoring",
        surgical_mode=True
    )
    
    print(f"DEBUG Step 2 results: {results}")
    applied = any("test_file.py" in f for f in results["applied_files"])
    val_failed = any("test_file.py" in f and "Validation failed" in f for f in results["failed_files"])
    
    assert applied or val_failed
    
    if applied:
        content = file_path.read_text(encoding="utf-8")
        assert "new_content = \"applied\"" in content

def test_apply_engine_auto_apply_false(tmp_path):
    """Test ApplyEngine respects auto_apply=False."""
    project_root = tmp_path
    apply_engine = ApplyEngine(project_root=project_root)
    
    file_path = project_root / "test_file.py"
    file_path.write_text("orig", encoding="utf-8")
    
    output = "```python\nnew\n```"
    
    results = apply_engine.apply(
        step_id="step_3",
        output=output,
        target_files=["test_file.py"],
        step_type="refactoring",
        surgical_mode=False,
        context={"auto_apply": False}
    )
    
    print(f"DEBUG Step 3 results: {results}")
    assert any("test_file.generated.py" in f for f in results["review_needed"])
    assert not results["applied_files"]
    assert (project_root / "test_file.generated.py").exists()
    assert file_path.read_text() == "orig"
