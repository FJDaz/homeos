"""Test new file creation in surgical mode and code application."""
import tempfile
import shutil
from pathlib import Path


def test_surgical_editor_create_new_file():
    """Test SurgicalEditor.create_new_file for creating new files."""
    from Backend.Prod.core.surgical_editor import SurgicalEditor
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        new_file = Path(tmpdir) / "test_new_file.py"
        
        # Test 1: Create from raw code
        code = """
def hello():
    return "world"

class MyClass:
    pass
"""
        success, message = SurgicalEditor.create_new_file(new_file, code)
        
        assert success, f"Expected success but got: {message}"
        assert new_file.exists(), "File was not created"
        
        content = new_file.read_text()
        assert "def hello():" in content
        assert "class MyClass:" in content
        print("✓ Test 1: Create from raw code passed")
        
        # Test 2: Create from surgical instructions
        new_file2 = Path(tmpdir) / "test_new_file2.py"
        surgical_output = '''
```json
{
  "operations": [
    {
      "type": "add_class",
      "code": "class NewClass:\\n    def __init__(self):\\n        self.value = 42"
    },
    {
      "type": "add_function", 
      "code": "def helper():\\n    return 'helpful'"
    }
  ]
}
```
'''
        success, message = SurgicalEditor.create_new_file(new_file2, surgical_output)
        
        assert success, f"Expected success but got: {message}"
        assert new_file2.exists(), "File was not created from surgical instructions"
        
        content2 = new_file2.read_text()
        assert "class NewClass:" in content2
        assert "def helper():" in content2
        print("✓ Test 2: Create from surgical instructions passed")
        
        # Test 3: Syntax error should fail
        new_file3 = Path(tmpdir) / "test_new_file3.py"
        bad_code = "def broken(\n    pass  # syntax error"
        success, message = SurgicalEditor.create_new_file(new_file3, bad_code)
        
        assert not success, "Expected failure due to syntax error"
        assert "Syntax error" in message
        print("✓ Test 3: Syntax validation works")


def test_post_apply_validator_new_file():
    """Test PostApplyValidator handles new files correctly."""
    from Backend.Prod.core.post_apply_validator import PostApplyValidator
    
    with tempfile.TemporaryDirectory() as tmpdir:
        validator = PostApplyValidator(project_root=Path(tmpdir))
        
        # Test with non-existent file (should treat as new file)
        non_existent = Path(tmpdir) / "new_file.py"
        success, message, _ = validator.validate_and_test(non_existent)
        
        assert success, f"Expected success for new file but got: {message}"
        assert "New file created" in message
        print("✓ Test 4: PostApplyValidator handles new files")


def test_apply_generated_code_new_file():
    """Test apply_generated_code creates new files."""
    from Backend.Prod.claude_helper import apply_generated_code
    
    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir) / "subdir" / "new_module.py"
        
        step_output = """
```python
def new_function():
    return "I am new"

class NewClass:
    pass
```
"""
        step = {
            "id": "test_step",
            "type": "code_generation",
            "context": {"files": [str(target)]}
        }
        
        success = apply_generated_code(step_output, target, step)
        
        assert success, "apply_generated_code should succeed"
        assert target.exists(), "New file should be created"
        
        content = target.read_text()
        assert "def new_function():" in content
        print("✓ Test 5: apply_generated_code creates new files")


def test_apply_generated_code_refactoring_new_file():
    """Test refactoring type creates new files when they don't exist."""
    from Backend.Prod.claude_helper import apply_generated_code
    
    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir) / "refactored_module.py"
        
        step_output = """
```python
def refactored_function():
    return "refactored"
```
"""
        step = {
            "id": "test_step",
            "type": "refactoring",
            "context": {"files": [str(target)]}
        }
        
        success = apply_generated_code(step_output, target, step)
        
        assert success, "apply_generated_code should succeed for refactoring"
        assert target.exists(), "New file should be created even for refactoring type"
        print("✓ Test 6: refactoring type creates new files when not existing")


if __name__ == "__main__":
    print("Running new file creation tests...\n")
    
    test_surgical_editor_create_new_file()
    print()
    
    test_post_apply_validator_new_file()
    print()
    
    test_apply_generated_code_new_file()
    print()
    
    test_apply_generated_code_refactoring_new_file()
    print()
    
    print("=" * 50)
    print("All tests passed! ✓")
