"""Surgical Protocol - System prompt and protocol for surgical editing operations.

This module defines the surgical editing protocol including the system prompt
and validation rules for surgical operations.
"""

SURGICAL_SYSTEM_PROMPT = """# SURGICAL EDITING PROTOCOL - ABSOLUTE SILENCE REQUIRED

You are a surgical code editor. Your ONLY output must be a JSON object with an "operations" array.
NO explanations, NO markdown, NO code blocks, NO natural language. JUST JSON.

## OPERATION TYPES (6 supported types)

1. **add_method** - Add a method to an existing class
   - Required: `"type": "add_method"`, `"target": "ClassName"`, `"code": "def method_name(...): ..."`
   - Optional: `"position": "end"` (default) or `"after": "existing_method_name"`

2. **modify_method** - Replace an existing method
   - Required: `"type": "modify_method"`, `"target": "ClassName.method_name"` or `"method_name"`, `"code": "new implementation"`
   - Target MUST be fully qualified: "ClassName.method_name" for methods, "function_name" for module-level functions

3. **add_import** - Add an import statement
   - Required: `"type": "add_import"`, `"import": "import statement"`
   - Example: `"import": "from pathlib import Path"`

4. **replace_import** - Replace an existing import
   - Required: `"type": "replace_import"`, `"old": "old import", "new": "new import"`
   - Example: `"old": "import os", "new": "import os, sys"`

5. **add_class** - Add a new class to the module
   - Required: `"type": "add_class"`, `"code": "class NewClass: ..."`
   - Optional: `"position": "end"` or `"after": "ExistingClass"`

6. **add_function** - Add a module-level function
   - Required: `"type": "add_function"`, `"code": "def function_name(...): ..."`

## TARGET QUALIFICATION RULES

1. **Methods**: MUST use "ClassName.method_name" format
2. **Classes**: Use simple class name
3. **Functions**: Use simple function name
4. **Imports**: Use exact import statement text

## AST STRUCTURE VERIFICATION

Before specifying targets, verify against this AST summary:
{ast_summary}

Check that:
- Classes exist before adding methods to them
- Methods exist before modifying them
- Imports exist before replacing them
- Functions exist before modifying them

## OUTPUT FORMAT

{
  "operations": [
    {
      "type": "operation_type",
      "target": "qualified_target_name",  // For add_method, modify_method
      "code": "python code here",         // For add_method, modify_method, add_class, add_function
      "import": "import statement",       // For add_import
      "old": "old import",                // For replace_import
      "new": "new import",                // For replace_import
      "position": "end",                  // Optional: "end", "after"
      "after": "existing_element"         // Optional: insert after this element
    }
  ]
}

## VALIDATION RULES

1. Each operation MUST have a valid "type" from the 6 supported types
2. Required fields MUST be present for each operation type
3. Targets MUST be qualified according to AST structure
4. Code MUST be valid Python syntax
5. Position references MUST exist in the AST

## ERROR PREVENTION

- Verify target existence in AST before use
- Ensure code indentation matches context
- Check import statements are valid Python
- Validate method/function signatures

## REMINDER: ABSOLUTE SILENCE

NO TEXT BEFORE OR AFTER THE JSON.
NO MARKDOWN CODE BLOCKS.
NO EXPLANATIONS.
JUST THE JSON OBJECT.
"""


class SurgicalProtocol:
    """Surgical editing protocol validator and helper."""

    @staticmethod
    def validate_target_qualification(target: str, node_type: str, ast_summary: str) -> bool:
        """
        Validate that a target is properly qualified against AST structure.

        Args:
            target: Target name (e.g., "ClassName.method_name")
            node_type: Type of node ("method", "class", "function", "import")
            ast_summary: AST structure summary from SurgicalEditor

        Returns:
            True if target is properly qualified, False otherwise
        """
        if not target:
            return False

        if node_type == "method":
            # Methods must be qualified as "ClassName.method_name"
            if "." not in target:
                return False
            class_name, method_name = target.split(".", 1)
            # Check class exists in AST summary
            if f"Class {class_name}" not in ast_summary:
                return False
            # Check method exists in class (for modify operations)
            if f"Method {method_name}" not in ast_summary:
                # Might be adding a new method, which is OK
                pass

        elif node_type == "class":
            # Classes should be simple names
            if "." in target:
                return False
            # For modify operations, check class exists
            if f"Class {target}" not in ast_summary:
                # Might be adding a new class, which is OK
                pass

        elif node_type == "function":
            # Functions can be simple names
            if "." in target:
                # Might be nested function, check parent exists
                pass

        elif node_type == "import":
            # Imports should be exact statements
            if not (target.startswith("import ") or target.startswith("from ")):
                return False

        return True

    @staticmethod
    def generate_prompt(ast_summary: str, task_description: str = "") -> str:
        """
        Generate a complete surgical editing prompt.

        Args:
            ast_summary: AST structure summary from SurgicalEditor
            task_description: Optional task description to include

        Returns:
            Complete prompt string
        """
        prompt = SURGICAL_SYSTEM_PROMPT.format(ast_summary=ast_summary)

        if task_description:
            prompt += f"\n\n## TASK\n{task_description}\n\n"

        prompt += """## READY FOR SURGICAL OPERATIONS

Provide JSON with operations array only:"""

        return prompt

    @staticmethod
    def get_operation_requirements(op_type: str) -> dict:
        """
        Get required and optional fields for an operation type.

        Args:
            op_type: Operation type string

        Returns:
            Dictionary with 'required' and 'optional' field lists
        """
        requirements = {
            "add_method": {
                "required": ["type", "target", "code"],
                "optional": ["position", "after"]
            },
            "modify_method": {
                "required": ["type", "target", "code"],
                "optional": []
            },
            "add_import": {
                "required": ["type", "import"],
                "optional": []
            },
            "replace_import": {
                "required": ["type", "old", "new"],
                "optional": []
            },
            "add_class": {
                "required": ["type", "code"],
                "optional": ["position", "after"]
            },
            "add_function": {
                "required": ["type", "code"],
                "optional": []
            }
        }

        return requirements.get(op_type, {"required": [], "optional": []})

    @staticmethod
    def validate_operation_structure(operation: dict, ast_summary: str) -> tuple:
        """
        Validate an operation structure against protocol rules.

        Args:
            operation: Operation dictionary
            ast_summary: AST structure summary

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(operation, dict):
            return False, "Operation must be a dictionary"

        op_type = operation.get("type")
        if not op_type:
            return False, "Missing 'type' field"

        # Check if operation type is supported
        supported_types = {
            "add_method", "modify_method", "add_import",
            "replace_import", "add_class", "add_function"
        }

        if op_type not in supported_types:
            return False, f"Unsupported operation type: {op_type}"

        # Get requirements for this operation type
        reqs = SurgicalProtocol.get_operation_requirements(op_type)

        # Check required fields
        for field in reqs["required"]:
            if field not in operation:
                return False, f"Missing required field: {field}"

        # Validate target qualification
        if "target" in operation:
            node_type = "method" if op_type in ["add_method", "modify_method"] else "class"
            if not SurgicalProtocol.validate_target_qualification(
                operation["target"], node_type, ast_summary
            ):
                return False, f"Invalid target qualification: {operation['target']}"

        # Validate position references
        if "after" in operation:
            after_target = operation["after"]
            # Check that the referenced element exists in AST
            if after_target and f" {after_target} " not in ast_summary:
                return False, f"Referenced element not found: {after_target}"

        return True, "Valid"

    @staticmethod
    def create_surgical_instructions(operations: list) -> str:
        """
        Create surgical instructions JSON from operations list.

        Args:
            operations: List of operation dictionaries

        Returns:
            JSON string with operations array
        """
        import json

        instructions = {
            "operations": operations
        }

        return json.dumps(instructions, indent=2)

    @staticmethod
    def extract_ast_context_for_prompt(surgical_editor) -> str:
        """
        Extract AST context for prompt generation.

        Args:
            surgical_editor: SurgicalEditor instance

        Returns:
            Formatted AST context string
        """
        if hasattr(surgical_editor, 'get_ast_context'):
            return surgical_editor.get_ast_context()
        elif hasattr(surgical_editor, 'parser'):
            return surgical_editor.parser.get_structure_summary()
        else:
            return "AST structure not available"
