"""Unit tests for Surgical Edit mode."""
import pytest
import tempfile
import json
from pathlib import Path
from typing import List

from Backend.Prod.core.surgical_editor import (
    ASTParser,
    SurgicalInstructionParser,
    SurgicalApplier,
    SurgicalEditor,
    SurgicalOperation,
    ASTNodeInfo
)


class TestASTParser:
    """Tests for ASTParser class."""
    
    def test_parse_simple_class(self):
        """Test parsing a simple class with methods."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""class TestClass:
    def method_one(self):
        pass
    
    def method_two(self, param):
        return param
""")
            file_path = Path(f.name)
        
        try:
            parser = ASTParser(file_path)
            assert parser.parse() is True
            assert len(parser.nodes) >= 3  # 1 class + 2 methods
            
            # Find the class
            class_node = parser.find_node("TestClass", "class")
            assert class_node is not None
            assert class_node.node_type == "class"
            
            # Find methods
            method1 = parser.find_node("method_one", "method", "TestClass")
            assert method1 is not None
            method2 = parser.find_node("method_two", "method", "TestClass")
            assert method2 is not None
            
        finally:
            file_path.unlink()
    
    def test_parse_imports(self):
        """Test parsing import statements."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""from typing import List, Dict
import os
from pathlib import Path
""")
            file_path = Path(f.name)
        
        try:
            parser = ASTParser(file_path)
            assert parser.parse() is True
            
            # Check imports are detected
            import_nodes = [n for n in parser.nodes if n.node_type == "import"]
            assert len(import_nodes) >= 2
            
        finally:
            file_path.unlink()
    
    def test_parse_functions(self):
        """Test parsing module-level functions."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""def module_function():
    return True

class MyClass:
    def class_method(self):
        pass
""")
            file_path = Path(f.name)
        
        try:
            parser = ASTParser(file_path)
            assert parser.parse() is True
            
            # Find module-level function
            func_node = parser.find_node("module_function", "function")
            assert func_node is not None
            assert func_node.parent is None
            
            # Find class method
            method_node = parser.find_node("class_method", "method", "MyClass")
            assert method_node is not None
            assert method_node.parent == "MyClass"
            
        finally:
            file_path.unlink()
    
    def test_get_structure_summary(self):
        """Test structure summary generation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""from typing import List

class Component:
    def process(self):
        pass
""")
            file_path = Path(f.name)
        
        try:
            parser = ASTParser(file_path)
            assert parser.parse() is True
            
            summary = parser.get_structure_summary()
            assert "AST Structure:" in summary
            assert "Component" in summary
            assert "process" in summary
            assert "Imports" in summary or "import" in summary.lower()
            
        finally:
            file_path.unlink()
    
    def test_parse_nonexistent_file(self):
        """Test parsing a non-existent file."""
        parser = ASTParser(Path("/nonexistent/file.py"))
        assert parser.parse() is False
    
    def test_parse_invalid_syntax(self):
        """Test parsing a file with invalid syntax."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("class InvalidSyntax: {")  # Invalid syntax
            file_path = Path(f.name)
        
        try:
            parser = ASTParser(file_path)
            assert parser.parse() is False
        finally:
            file_path.unlink()


class TestSurgicalInstructionParser:
    """Tests for SurgicalInstructionParser class."""
    
    def test_is_surgical_output_valid(self):
        """Test detection of surgical output."""
        output = '{"operations": [{"type": "add_method"}]}'
        assert SurgicalInstructionParser.is_surgical_output(output) is True
    
    def test_is_surgical_output_invalid(self):
        """Test detection of non-surgical output."""
        output = "def some_function(): pass"
        assert SurgicalInstructionParser.is_surgical_output(output) is False
    
    def test_parse_instructions_simple(self):
        """Test parsing simple instructions."""
        output = """{
  "operations": [
    {
      "type": "add_method",
      "target": "TestClass",
      "position": "after",
      "after_method": "existing_method",
      "code": "def new_method(self): pass"
    }
  ]
}"""
        operations, error = SurgicalInstructionParser.parse_instructions(output)
        assert operations is not None
        assert error is None
        assert len(operations) == 1
        assert operations[0].op_type == "add_method"
        assert operations[0].target == "TestClass"
        assert operations[0].after_method == "existing_method"
    
    def test_parse_instructions_multiple_ops(self):
        """Test parsing multiple operations."""
        output = """{
  "operations": [
    {
      "type": "add_import",
      "import": "from pathlib import Path"
    },
    {
      "type": "add_method",
      "target": "MyClass",
      "code": "def method(self): pass"
    }
  ]
}"""
        operations, error = SurgicalInstructionParser.parse_instructions(output)
        assert operations is not None
        assert len(operations) == 2
        assert operations[0].op_type == "add_import"
        assert operations[1].op_type == "add_method"
    
    def test_parse_instructions_markdown_block(self):
        """Test parsing instructions from markdown code block."""
        output = """Here is the JSON:
```json
{
  "operations": [
    {
      "type": "add_method",
      "target": "Test",
      "code": "def test(self): pass"
    }
  ]
}
```"""
        operations, error = SurgicalInstructionParser.parse_instructions(output)
        assert operations is not None
        assert error is None
        assert len(operations) == 1
    
    def test_parse_instructions_invalid_json(self):
        """Test parsing invalid JSON."""
        output = '{"operations": [invalid json}'
        operations, error = SurgicalInstructionParser.parse_instructions(output)
        assert operations is None
        assert error is not None
        assert "Invalid JSON" in error or "JSON" in error
    
    def test_parse_instructions_missing_operations(self):
        """Test parsing JSON without operations key."""
        output = '{"other_key": "value"}'
        operations, error = SurgicalInstructionParser.parse_instructions(output)
        assert operations is None
        assert error is not None
        # Error should mention operations or indicate no valid operations found
        assert "operations" in error.lower() or "no json" in error.lower() or "no valid" in error.lower()
    
    def test_parse_instructions_empty_operations(self):
        """Test parsing JSON with empty operations."""
        output = '{"operations": []}'
        operations, error = SurgicalInstructionParser.parse_instructions(output)
        assert operations is None
        assert error is not None
        assert "valid operations" in error.lower() or "no valid" in error.lower()


class TestSurgicalApplier:
    """Tests for SurgicalApplier class."""
    
    def test_add_method_to_class(self):
        """Test adding a method to an existing class."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""class TestClass:
    def existing_method(self):
        pass
""")
            file_path = Path(f.name)
        
        try:
            parser = ASTParser(file_path)
            assert parser.parse() is True
            
            applier = SurgicalApplier(file_path, parser)
            
            op = SurgicalOperation(
                op_type="add_method",
                target="TestClass",
                position="after",
                after_method="existing_method",
                code="def new_method(self):\n    return True"
            )
            
            success, result = applier.apply_operations([op])
            assert success is True
            assert "new_method" in result
            assert "existing_method" in result
            assert "TestClass" in result
            
        finally:
            file_path.unlink()
    
    def test_add_import(self):
        """Test adding an import statement."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""from typing import List

def some_function():
    pass
""")
            file_path = Path(f.name)
        
        try:
            parser = ASTParser(file_path)
            assert parser.parse() is True
            
            applier = SurgicalApplier(file_path, parser)
            
            op = SurgicalOperation(
                op_type="add_import",
                new_import="from pathlib import Path"
            )
            
            success, result = applier.apply_operations([op])
            assert success is True
            assert "from pathlib import Path" in result
            assert "from typing import List" in result
            
        finally:
            file_path.unlink()
    
    def test_replace_import(self):
        """Test replacing an import statement."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""from typing import List

def some_function():
    pass
""")
            file_path = Path(f.name)
        
        try:
            parser = ASTParser(file_path)
            assert parser.parse() is True
            
            applier = SurgicalApplier(file_path, parser)
            
            op = SurgicalOperation(
                op_type="replace_import",
                old_import="from typing import List",
                new_import="from typing import List, Dict"
            )
            
            success, result = applier.apply_operations([op])
            assert success is True
            assert "from typing import List, Dict" in result
            
        finally:
            file_path.unlink()
    
    def test_add_class(self):
        """Test adding a class to a module."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""class ExistingClass:
    pass
""")
            file_path = Path(f.name)
        
        try:
            parser = ASTParser(file_path)
            assert parser.parse() is True
            
            applier = SurgicalApplier(file_path, parser)
            
            op = SurgicalOperation(
                op_type="add_class",
                position="end",
                code="class NewClass:\n    def method(self):\n        pass"
            )
            
            success, result = applier.apply_operations([op])
            assert success is True
            assert "NewClass" in result
            assert "ExistingClass" in result
            
        finally:
            file_path.unlink()
    
    def test_add_function(self):
        """Test adding a module-level function."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""def existing_function():
    pass
""")
            file_path = Path(f.name)
        
        try:
            parser = ASTParser(file_path)
            assert parser.parse() is True
            
            applier = SurgicalApplier(file_path, parser)
            
            op = SurgicalOperation(
                op_type="add_function",
                position="after",
                after_function="existing_function",
                code="def new_function():\n    return True"
            )
            
            success, result = applier.apply_operations([op])
            assert success is True
            assert "new_function" in result
            assert "existing_function" in result
            
        finally:
            file_path.unlink()
    
    def test_add_method_nonexistent_class(self):
        """Test adding method to non-existent class."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def some_function(): pass")
            file_path = Path(f.name)
        
        try:
            parser = ASTParser(file_path)
            assert parser.parse() is True
            
            applier = SurgicalApplier(file_path, parser)
            
            op = SurgicalOperation(
                op_type="add_method",
                target="NonexistentClass",
                code="def method(self): pass"
            )
            
            success, result = applier.apply_operations([op])
            assert success is False
            assert "not found" in result.lower()
            
        finally:
            file_path.unlink()
    
    def test_modify_method(self):
        """Test modifying an existing method."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""class TestClass:
    def existing_method(self):
        return "old"
""")
            file_path = Path(f.name)

        try:
            parser = ASTParser(file_path)
            assert parser.parse() is True

            applier = SurgicalApplier(file_path, parser)

            op = SurgicalOperation(
                op_type="modify_method",
                target="TestClass.existing_method",
                code="def existing_method(self):\n    return 'new'"
            )

            success, result = applier.apply_operations([op])
            assert success is True
            assert "existing_method" in result
            assert "'new'" in result or '"new"' in result

        finally:
            file_path.unlink()

    def test_modify_method_not_found(self):
        """Test modifying a non-existent method."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("class Test:\n    pass")
            file_path = Path(f.name)

        try:
            parser = ASTParser(file_path)
            assert parser.parse() is True

            applier = SurgicalApplier(file_path, parser)

            op = SurgicalOperation(
                op_type="modify_method",
                target="Test.nonexistent",
                code="def nonexistent(self): pass"
            )

            success, result = applier.apply_operations([op])
            assert success is False
            assert "not found" in result.lower()

        finally:
            file_path.unlink()

    def test_invalid_operation_type(self):
        """Test handling invalid operation type."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("class Test: pass")
            file_path = Path(f.name)

        try:
            parser = ASTParser(file_path)
            assert parser.parse() is True

            applier = SurgicalApplier(file_path, parser)

            op = SurgicalOperation(
                op_type="invalid_operation",
                code="some code"
            )

            success, result = applier.apply_operations([op])
            assert success is False
            assert "unsupported" in result.lower() or "invalid" in result.lower()

        finally:
            file_path.unlink()


class TestSurgicalEditor:
    """Tests for SurgicalEditor main interface."""
    
    def test_prepare(self):
        """Test preparing the editor."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("class Test: pass")
            file_path = Path(f.name)
        
        try:
            editor = SurgicalEditor(file_path)
            assert editor.prepare() is True
            assert editor.parser.tree is not None
            assert editor.applier is not None
        finally:
            file_path.unlink()
    
    def test_get_ast_context(self):
        """Test getting AST context."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""from typing import List

class Component:
    def process(self):
        pass
""")
            file_path = Path(f.name)
        
        try:
            editor = SurgicalEditor(file_path)
            assert editor.prepare() is True
            
            context = editor.get_ast_context()
            assert "AST Structure:" in context
            assert "Component" in context
            assert "process" in context
            
        finally:
            file_path.unlink()
    
    def test_apply_instructions_success(self):
        """Test successfully applying instructions."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""class TestClass:
    def existing(self):
        pass
""")
            file_path = Path(f.name)
        
        try:
            editor = SurgicalEditor(file_path)
            assert editor.prepare() is True
            
            llm_output = """{
  "operations": [
    {
      "type": "add_method",
      "target": "TestClass",
      "position": "after",
      "after_method": "existing",
      "code": "def new_method(self): return True"
    }
  ]
}"""
            
            success, result, original = editor.apply_instructions(llm_output)
            assert success is True
            assert result is not None
            assert "new_method" in result
            assert original is not None
            
        finally:
            file_path.unlink()
    
    def test_apply_instructions_invalid_json(self):
        """Test applying invalid instructions."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("class Test: pass")
            file_path = Path(f.name)
        
        try:
            editor = SurgicalEditor(file_path)
            assert editor.prepare() is True
            
            llm_output = "Invalid JSON {"
            
            success, result, original = editor.apply_instructions(llm_output)
            assert success is False
            assert result is not None  # Error message
            assert "json" in result.lower() or "invalid" in result.lower()
            
        finally:
            file_path.unlink()
    
    def test_apply_instructions_nonexistent_file(self):
        """Test applying instructions to non-existent file."""
        editor = SurgicalEditor(Path("/nonexistent/file.py"))
        assert editor.prepare() is False


class TestIntegration:
    """Integration tests for complete workflow."""
    
    def test_full_workflow_add_method(self):
        """Test complete workflow: parse -> apply -> verify."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""from typing import List

class Component:
    def process(self):
        return True
""")
            file_path = Path(f.name)
        
        try:
            # Step 1: Prepare editor
            editor = SurgicalEditor(file_path)
            assert editor.prepare() is True
            
            # Step 2: Get AST context (simulating what orchestrator does)
            ast_context = editor.get_ast_context()
            assert "Component" in ast_context
            
            # Step 3: Simulate LLM output with surgical instructions
            llm_output = """{
  "operations": [
    {
      "type": "add_method",
      "target": "Component",
      "position": "after",
      "after_method": "process",
      "code": "def validate(self, data):\\n    return isinstance(data, dict)"
    }
  ]
}"""
            
            # Step 4: Apply instructions
            success, modified_code, original_code = editor.apply_instructions(llm_output)
            assert success is True
            
            # Step 5: Verify result
            assert "validate" in modified_code
            assert "process" in modified_code
            assert "Component" in modified_code
            assert "isinstance(data, dict)" in modified_code
            
            # Verify original is preserved
            assert "process" in original_code
            
        finally:
            file_path.unlink()
    
    def test_multiple_operations(self):
        """Test applying multiple operations in sequence."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""class Test:
    pass
""")
            file_path = Path(f.name)
        
        try:
            editor = SurgicalEditor(file_path)
            assert editor.prepare() is True
            
            llm_output = """{
  "operations": [
    {
      "type": "add_import",
      "import": "from pathlib import Path"
    },
    {
      "type": "add_method",
      "target": "Test",
      "code": "def method(self): return Path('.')"
    }
  ]
}"""
            
            success, result, _ = editor.apply_instructions(llm_output)
            assert success is True
            assert "from pathlib import Path" in result
            assert "def method(self)" in result
            
        finally:
            file_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
