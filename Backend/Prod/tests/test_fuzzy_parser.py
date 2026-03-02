import pytest
from Backend.Prod.core.surgical_editor import SurgicalInstructionParser

def test_parse_fuzzy_markdown():
    """Test that parser handles markdown blocks with extra text."""
    output = """
Here are the changes:
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
I hope this helps!
"""
    ops, error = SurgicalInstructionParser.parse_instructions(output)
    assert error is None
    assert len(ops) == 1
    assert ops[0].op_type == "add_method"
    assert ops[0].target == "MyClass"

def test_parse_fuzzy_missing_comma():
    """Test that parser handles missing commas between operations."""
    output = """
{
  "operations": [
    {
      "type": "add_method",
      "target": "A",
      "code": "..."
    }
    {
      "type": "add_method",
      "target": "B",
      "code": "..."
    }
  ]
}
"""
    ops, error = SurgicalInstructionParser.parse_instructions(output)
    assert error is None
    assert len(ops) == 2
    assert ops[0].target == "A"
    assert ops[1].target == "B"

def test_parse_fuzzy_trailing_comma():
    """Test that parser handles trailing commas (common LLM error)."""
    output = """
{
  "operations": [
    {
      "type": "add_method",
      "target": "A",
      "code": "...",
    },
  ],
}
"""
    ops, error = SurgicalInstructionParser.parse_instructions(output)
    # The current re.sub handles some trailing commas
    assert error is None
    assert len(ops) == 1

def test_is_surgical_output_fuzzy():
    """Test detection of surgical output in messy text."""
    output = "Refactoring... \n\n ```json\n{\"operations\": [{\"type\": \"add_method\"}]}\n```"
    assert SurgicalInstructionParser.is_surgical_output(output) is True
    
    output_no_ops = "Refactoring... \n\n ```json\n{\"not_ops\": []}\n```"
    assert SurgicalInstructionParser.is_surgical_output(output_no_ops) is False
