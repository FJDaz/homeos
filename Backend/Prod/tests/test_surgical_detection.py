"""Test surgical output detection to avoid false positives."""


def test_is_surgical_output_real_surgical():
    """Detect real surgical instructions."""
    from Backend.Prod.core.surgical_editor import SurgicalInstructionParser
    
    # Real surgical output in JSON block
    surgical_json = '''
```json
{
  "operations": [
    {
      "type": "add_method",
      "target": "MyClass",
      "code": "def new_method(self): pass"
    }
  ]
}
```
'''
    assert SurgicalInstructionParser.is_surgical_output(surgical_json) == True
    
    # Real surgical output without markdown block
    surgical_raw = '''
{
  "operations": [
    {"type": "add_import", "import": "import os"}
  ]
}
'''
    assert SurgicalInstructionParser.is_surgical_output(surgical_raw) == True
    print("✓ Real surgical instructions detected")


def test_is_surgical_output_python_code_false_positive():
    """Avoid false positives with Python code containing 'operations' key."""
    from Backend.Prod.core.surgical_editor import SurgicalInstructionParser
    
    # Python code with operations in a dict - should NOT be detected as surgical
    python_code = '''
def get_config():
    return {
        "operations": ["read", "write", "delete"],
        "timeout": 30,
        "retry": 3
    }

class Config:
    DEFAULTS = {
        "operations": ["op1", "op2"],
        "enabled": True
    }
'''
    result = SurgicalInstructionParser.is_surgical_output(python_code)
    assert result == False, f"Python code should not be detected as surgical, got: {result}"
    print("✓ Python dict with 'operations' key not detected as surgical")


def test_is_surgical_output_complex_python():
    """Avoid false positives with complex Python code."""
    from Backend.Prod.core.surgical_editor import SurgicalInstructionParser
    
    # Complex Python with operations in various contexts
    complex_python = '''
class WorkflowManager:
    """Manages workflow operations."""
    
    def __init__(self):
        self.config = {
            "operations": {
                "read": lambda x: x,
                "write": lambda x: x
            }
        }
    
    def execute(self, operation: str):
        if operation in self.config["operations"]:
            return self.config["operations"][operation]
        
        operations_list = ["a", "b", "c"]
        return {"operations": operations_list}

def main():
    data = {"operations": []}
    data["operations"].append("test")
    return data
'''
    result = SurgicalInstructionParser.is_surgical_output(complex_python)
    assert result == False, f"Complex Python code should not be detected as surgical"
    print("✓ Complex Python code not detected as surgical")


def test_is_surgical_output_edge_cases():
    """Test edge cases."""
    from Backend.Prod.core.surgical_editor import SurgicalInstructionParser
    
    # Empty string
    assert SurgicalInstructionParser.is_surgical_output("") == False
    
    # Just the word operations
    assert SurgicalInstructionParser.is_surgical_output("operations") == False
    
    # Operations in a string
    assert SurgicalInstructionParser.is_surgical_output('x = "operations":') == False
    
    # Operations in comment
    code_with_comment = '# Configures "operations": list of operations'
    assert SurgicalInstructionParser.is_surgical_output(code_with_comment) == False
    
    print("✓ Edge cases handled correctly")


def test_is_surgical_output_mixed_content():
    """Test mixed content (surgical + explanation)."""
    from Backend.Prod.core.surgical_editor import SurgicalInstructionParser
    
    mixed_content = '''
Here are the surgical instructions:

```json
{
  "operations": [
    {
      "type": "add_method",
      "target": "MyClass",
      "code": "def helper(self):\\n    return {\\"operations\\": []}"
    }
  ]
}
```

This will add a method that returns {"operations": []}.
'''
    # Should detect surgical instructions even with Python code inside
    result = SurgicalInstructionParser.is_surgical_output(mixed_content)
    assert result == True, "Should detect surgical instructions in mixed content"
    print("✓ Mixed content (surgical + Python) correctly detected")


if __name__ == "__main__":
    print("Testing surgical output detection...\n")
    
    test_is_surgical_output_real_surgical()
    print()
    
    test_is_surgical_output_python_code_false_positive()
    print()
    
    test_is_surgical_output_complex_python()
    print()
    
    test_is_surgical_output_edge_cases()
    print()
    
    test_is_surgical_output_mixed_content()
    print()
    
    print("=" * 50)
    print("All surgical detection tests passed! ✓")
