"""Surgical Edit Mode - Precise code modifications via AST.

This module provides functionality to apply precise code modifications
instead of generating complete files, solving merge and integration issues.
"""
import ast
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from loguru import logger

try:
    import astunparse
except ImportError:
    astunparse = None
    logger.warning("astunparse not available. Surgical Edit mode will have limited functionality.")


@dataclass
class ASTNodeInfo:
    """Information about an AST node."""
    name: str
    node_type: str  # 'class', 'function', 'method', 'import', etc.
    line_start: int
    line_end: int
    parent: Optional[str] = None  # For methods: parent class name


# Supported surgical operation types (for validation)
SUPPORTED_OPERATIONS = frozenset({
    "add_method", "modify_method", "add_import", "replace_import",
    "add_class", "add_function"
})


@dataclass
class SurgicalOperation:
    """Represents a surgical operation to apply."""
    op_type: Optional[str] = None  # 'add_method', 'modify_method', 'add_import', etc.
    target: Optional[str] = None
    position: Optional[str] = None  # 'after', 'before', 'end'
    code: Optional[str] = None
    modifications: Optional[List[Dict[str, Any]]] = None
    after_method: Optional[str] = None
    after_class: Optional[str] = None
    after_function: Optional[str] = None
    old_import: Optional[str] = None
    new_import: Optional[str] = None


class ASTParser:
    """Parse Python file AST and extract structure information."""
    
    def __init__(self, file_path: Path):
        """
        Initialize AST parser.
        
        Args:
            file_path: Path to Python file to parse
        """
        self.file_path = file_path
        self.tree: Optional[ast.Module] = None
        self.source_lines: List[str] = []
        self.nodes: List[ASTNodeInfo] = []
        
    def parse(self) -> bool:
        """
        Parse the file and extract AST structure.
        
        Returns:
            True if parsing succeeded, False otherwise
        """
        try:
            if not self.file_path.exists():
                logger.warning(f"File not found: {self.file_path}")
                return False
            
            # Read source code
            with open(self.file_path, 'r', encoding='utf-8') as f:
                source = f.read()
                self.source_lines = source.splitlines()
            
            # Parse AST
            self.tree = ast.parse(source, filename=str(self.file_path))
            
            # Extract structure
            self.nodes = []
            self._extract_nodes(self.tree)
            
            logger.info(f"Parsed {len(self.nodes)} AST nodes from {self.file_path}")
            return True
            
        except SyntaxError as e:
            logger.error(f"Syntax error in {self.file_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error parsing {self.file_path}: {e}")
            return False
    
    def _extract_nodes(self, node: ast.AST, parent: Optional[str] = None) -> None:
        """Recursively extract node information."""
        if isinstance(node, ast.Module):
            # Process module-level nodes
            for child in node.body:
                self._extract_nodes(child, parent)
        
        elif isinstance(node, ast.ClassDef):
            # Extract class information
            line_start = node.lineno
            line_end = node.end_lineno if hasattr(node, 'end_lineno') else line_start
            
            self.nodes.append(ASTNodeInfo(
                name=node.name,
                node_type='class',
                line_start=line_start,
                line_end=line_end,
                parent=parent
            ))
            
            # Process class body (methods, nested classes, etc.)
            for child in node.body:
                self._extract_nodes(child, node.name)
        
        elif isinstance(node, ast.FunctionDef):
            # Extract function/method information
            line_start = node.lineno
            line_end = node.end_lineno if hasattr(node, 'end_lineno') else line_start
            
            node_type = 'method' if parent else 'function'
            
            self.nodes.append(ASTNodeInfo(
                name=node.name,
                node_type=node_type,
                line_start=line_start,
                line_end=line_end,
                parent=parent
            ))
        
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            # Extract import information
            line_start = node.lineno
            line_end = node.end_lineno if hasattr(node, 'end_lineno') else line_start
            
            if isinstance(node, ast.ImportFrom):
                module = node.module or ''
                names = ', '.join([alias.name for alias in node.names])
                name = f"from {module} import {names}"
            else:
                names = ', '.join([alias.name for alias in node.names])
                name = f"import {names}"
            
            self.nodes.append(ASTNodeInfo(
                name=name,
                node_type='import',
                line_start=line_start,
                line_end=line_end,
                parent=parent
            ))
    
    def get_structure_summary(self) -> str:
        """
        Generate a human-readable structure summary for prompts.
        
        Returns:
            Formatted string describing the AST structure
        """
        if not self.nodes:
            return "No structure found."
        
        lines = ["AST Structure:"]
        
        # Group by type
        classes = [n for n in self.nodes if n.node_type == 'class']
        functions = [n for n in self.nodes if n.node_type == 'function']
        methods_by_class: Dict[str, List[ASTNodeInfo]] = {}
        imports = [n for n in self.nodes if n.node_type == 'import']
        
        for node in self.nodes:
            if node.node_type == 'method' and node.parent:
                if node.parent not in methods_by_class:
                    methods_by_class[node.parent] = []
                methods_by_class[node.parent].append(node)
        
        # Format imports
        if imports:
            lines.append("- Imports (lines {}-{})".format(
                min(i.line_start for i in imports),
                max(i.line_end for i in imports)
            ))
        
        # Format classes with methods
        for cls in classes:
            methods = methods_by_class.get(cls.name, [])
            methods_str = ", ".join([m.name for m in methods]) if methods else "no methods"
            lines.append(f"- Class {cls.name} (lines {cls.line_start}-{cls.line_end})")
            for method in methods:
                lines.append(f"  - Method {method.name} (lines {method.line_start}-{method.line_end})")
        
        # Format module-level functions
        for func in functions:
            lines.append(f"- Function {func.name} (lines {func.line_start}-{func.line_end})")
        
        return "\n".join(lines)
    
    def find_node(self, name: str, node_type: Optional[str] = None, parent: Optional[str] = None) -> Optional[ASTNodeInfo]:
        """
        Find a node by name and optionally type/parent.
        
        Args:
            name: Node name to find
            node_type: Optional node type filter
            parent: Optional parent name filter
            
        Returns:
            ASTNodeInfo if found, None otherwise
        """
        for node in self.nodes:
            if node.name == name:
                if node_type and node.node_type != node_type:
                    continue
                if parent and node.parent != parent:
                    continue
                return node
        return None


class SurgicalInstructionParser:
    """Parse surgical instructions JSON from LLM output."""
    
    @staticmethod
    def parse_instructions(output: str) -> Tuple[Optional[List[SurgicalOperation]], Optional[str]]:
        """
        Parse surgical instructions from LLM output.
        
        Args:
            output: Raw LLM output (may contain JSON instructions)
            
        Returns:
            Tuple of (list of operations, error message if any)
        """
        # Try to extract JSON from output - look for JSON code blocks first
        json_match = None
        
        # Try markdown code block with json (capture the JSON content)
        # Match ```json ... ``` or ``` ... ``` with JSON inside
        code_block_match = re.search(r'```(?:json)?\s*(\{.*?"operations".*?\})\s*```', output, re.DOTALL)
        if code_block_match:
            # Use the captured group (the JSON content)
            json_str = code_block_match.group(1)
            try:
                # Validate it's valid JSON
                json.loads(json_str)
                # Create a match object-like structure
                class MatchObj:
                    def __init__(self, json_str):
                        self._json_str = json_str
                    def group(self, n):
                        return self._json_str if n == 0 or n == 1 else None
                json_match = MatchObj(json_str)
            except json.JSONDecodeError:
                pass
        
        if not json_match:
            # Try to find JSON object with operations key (more flexible)
            json_match = re.search(r'\{[^{}]*"operations"\s*:\s*\[.*?\]\s*\}', output, re.DOTALL)
        
        if not json_match:
            # Try to find any JSON block containing operations (nested braces)
            # Use a more sophisticated approach to handle nested JSON
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*"operations"[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', output, re.DOTALL)
        
        if not json_match:
            return None, "No JSON instructions found in output"
        
        try:
            # Handle both regex match objects and our MatchObj
            if hasattr(json_match, '_json_str'):
                json_str = json_match._json_str
            else:
                json_str = json_match.group(0)
            data = json.loads(json_str)
            
            if 'operations' not in data:
                return None, "Missing 'operations' key in JSON"
            
            operations = []
            for op_data in data['operations']:
                try:
                    op = SurgicalOperation(
                        op_type=op_data.get('type'),
                        target=op_data.get('target'),
                        position=op_data.get('position'),
                        code=op_data.get('code'),
                        modifications=op_data.get('modifications'),
                        after_method=op_data.get('after_method'),
                        after_class=op_data.get('after_class'),
                        after_function=op_data.get('after_function'),
                        old_import=op_data.get('old'),
                        new_import=op_data.get('new') or op_data.get('import')  # Support both 'new' and 'import' keys
                    )
                    operations.append(op)
                except Exception as e:
                    logger.warning(f"Error parsing operation: {e}")
                    continue
            
            if not operations:
                return None, "No valid operations found"
            
            return operations, None
            
        except json.JSONDecodeError as e:
            return None, f"Invalid JSON: {e}"
        except Exception as e:
            return None, f"Error parsing instructions: {e}"
    
    @staticmethod
    def is_surgical_output(output: str) -> bool:
        """
        Check if output contains surgical instructions.
        
        Uses multiple heuristics to avoid false positives from Python code
        containing strings like "operations": in dict literals.
        
        Args:
            output: Raw LLM output
            
        Returns:
            True if output appears to contain surgical instructions
        """
        if not output or not output.strip():
            return False
        
        # Strategy: Find potential JSON blocks and validate they are surgical instructions
        
        # Pattern 1: Markdown code block with JSON
        json_block_pattern = r'```(?:json)?\s*(\{[\s\S]*?"operations"\s*:[\s\S]*?\})\s*```'
        for match in re.finditer(json_block_pattern, output, re.IGNORECASE):
            json_content = match.group(1)
            if SurgicalInstructionParser._is_valid_surgical_json(json_content):
                return True
        
        # Pattern 2: Raw JSON object at start of line or after empty line
        # This avoids matching Python dicts which are typically after '=' or ':'
        raw_json_pattern = r'(?:^|\n\n)\s*(\{[\s\S]*?"operations"\s*:[\s\S]*?\})\s*(?:\n\n|$)'
        for match in re.finditer(raw_json_pattern, output):
            json_content = match.group(1)
            if SurgicalInstructionParser._is_valid_surgical_json(json_content):
                return True
        
        return False
    
    @staticmethod
    def _is_valid_surgical_json(json_str: str) -> bool:
        """
        Validate that a JSON string represents surgical instructions.
        
        Checks:
        1. Valid JSON
        2. Has "operations" key at root
        3. "operations" is an array
        4. Operations have surgical fields (type, code, target, etc.)
        
        Args:
            json_str: Potential JSON string
            
        Returns:
            True if valid surgical JSON
        """
        try:
            data = json.loads(json_str)
            
            # Must have 'operations' key
            if 'operations' not in data:
                return False
            
            operations = data['operations']
            
            # Must be a list
            if not isinstance(operations, list):
                return False
            
            # Empty operations array is valid but not useful
            if len(operations) == 0:
                return False
            
            # Check first operation has surgical fields
            # This distinguishes from random JSON with "operations" key
            first_op = operations[0]
            if not isinstance(first_op, dict):
                return False
            
            # Surgical operations typically have these fields
            surgical_fields = {'type', 'code', 'target', 'position', 'import', 'old', 'new'}
            op_keys = set(first_op.keys())
            
            # Must have at least one surgical field
            if not op_keys.intersection(surgical_fields):
                return False
            
            return True
            
        except json.JSONDecodeError:
            return False
        except Exception:
            return False


class SurgicalApplier:
    """Apply surgical operations to AST and regenerate code."""
    
    def __init__(self, file_path: Path, parser: ASTParser):
        """
        Initialize surgical applier.
        
        Args:
            file_path: Path to target file
            parser: ASTParser instance with parsed AST
        """
        self.file_path = file_path
        self.parser = parser
        self.tree = parser.tree
        self.source_lines = parser.source_lines
        
    def _validate_operation(self, op: SurgicalOperation) -> Optional[str]:
        """Validate operation has required fields and supported type. Returns error message or None."""
        if not op or not getattr(op, "op_type", None):
            return "Operation missing type"
        if op.op_type not in SUPPORTED_OPERATIONS:
            return f"Unsupported operation type: {op.op_type!r}. Supported: {sorted(SUPPORTED_OPERATIONS)}"
        if op.op_type == "add_method" and (not op.target or not op.code):
            return "add_method requires 'target' and 'code'"
        if op.op_type == "add_import" and not (op.new_import or op.code or getattr(op, "import", None)):
            return "add_import requires 'import' or 'code'"
        if op.op_type == "replace_import" and (not op.old_import or not op.new_import):
            return "replace_import requires 'old' and 'new'"
        if op.op_type == "add_class" and not op.code:
            return "add_class requires 'code'"
        if op.op_type == "add_function" and not op.code:
            return "add_function requires 'code'"
        if op.op_type == "modify_method" and (not op.target or not op.code):
            return "modify_method requires 'target' and 'code'"
        return None

    def apply_operations(self, operations: List[SurgicalOperation]) -> Tuple[bool, str]:
        """
        Apply surgical operations to the AST.
        
        Validates each operation, applies them, regenerates code, then validates
        Python syntax. On any failure returns (False, error_message) without
        modifying the file.
        
        Args:
            operations: List of operations to apply
            
        Returns:
            Tuple of (success, modified_code or error_message)
        """
        if not self.tree:
            return False, "AST not parsed"
        
        if astunparse is None:
            return False, "astunparse not available. Install it: pip install astunparse"
        
        if not operations:
            return False, "No operations to apply"
        
        try:
            # Validate all operations before applying any
            for i, op in enumerate(operations):
                err = self._validate_operation(op)
                if err:
                    return False, f"Operation {i + 1} invalid: {err}"
            
            # Apply each operation
            for i, op in enumerate(operations):
                success, error = self._apply_operation(op)
                if not success:
                    return False, f"Operation {i + 1} ({op.op_type}): {error}"
            
            # Regenerate code from modified AST
            try:
                modified_code = astunparse.unparse(self.tree)
            except Exception as e:
                return False, f"Failed to regenerate code: {e}"
            
            # Validate resulting Python syntax before returning
            try:
                ast.parse(modified_code)
            except SyntaxError as e:
                return False, f"Generated code has syntax error: {e}"
            
            return True, modified_code
                
        except Exception as e:
            logger.exception("Surgical apply failed")
            return False, f"Error applying operations: {e}"
    
    def _apply_operation(self, op: SurgicalOperation) -> Tuple[bool, Optional[str]]:
        """
        Apply a single surgical operation.
        
        Args:
            op: Operation to apply (assumed already validated)
            
        Returns:
            Tuple of (success, error_message if any)
        """
        if not op or not op.op_type:
            return False, "Missing operation type"
        if op.op_type == 'add_method':
            return self._add_method(op)
        elif op.op_type == 'add_import':
            return self._add_import(op)
        elif op.op_type == 'replace_import':
            return self._replace_import(op)
        elif op.op_type == 'add_class':
            return self._add_class(op)
        elif op.op_type == 'add_function':
            return self._add_function(op)
        elif op.op_type == 'modify_method':
            return self._modify_method(op)
        else:
            return False, f"Unsupported operation type: {op.op_type}"
    
    def _add_method(self, op: SurgicalOperation) -> Tuple[bool, Optional[str]]:
        """Add a method to a class."""
        if not op.target or not op.code:
            return False, "Missing target or code for add_method"
        
        # Find the target class
        class_node = None
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef) and node.name == op.target:
                class_node = node
                break
        
        if not class_node:
            return False, f"Class {op.target} not found"
        
        # Parse the new method code
        try:
            method_ast = ast.parse(op.code).body[0]
            if not isinstance(method_ast, ast.FunctionDef):
                return False, "Code is not a function definition"
        except SyntaxError as e:
            return False, f"Invalid method code: {e}"
        
        # Insert method at appropriate position
        if op.position == 'end':
            class_node.body.append(method_ast)
        elif op.position == 'after' and op.after_method:
            # Find the method to insert after
            insert_idx = len(class_node.body)
            for i, child in enumerate(class_node.body):
                if isinstance(child, ast.FunctionDef) and child.name == op.after_method:
                    insert_idx = i + 1
                    break
            class_node.body.insert(insert_idx, method_ast)
        else:
            # Default: append at end
            class_node.body.append(method_ast)
        
        return True, None
    
    def _add_import(self, op: SurgicalOperation) -> Tuple[bool, Optional[str]]:
        """Add an import statement."""
        # Support both 'import' and 'new_import' fields
        import_stmt = op.new_import or getattr(op, 'import', None) or op.code
        
        if not import_stmt:
            return False, "Missing import statement"
        
        try:
            import_ast = ast.parse(import_stmt).body[0]
            if not isinstance(import_ast, (ast.Import, ast.ImportFrom)):
                return False, "Code is not an import statement"
        except SyntaxError as e:
            return False, f"Invalid import code: {e}"
        
        # Insert at the beginning of the module (after existing imports)
        import_idx = 0
        for i, node in enumerate(self.tree.body):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                import_idx = i + 1
            else:
                break
        
        self.tree.body.insert(import_idx, import_ast)
        return True, None
    
    def _replace_import(self, op: SurgicalOperation) -> Tuple[bool, Optional[str]]:
        """Replace an import statement."""
        if not op.old_import or not op.new_import:
            return False, "Missing old or new import"
        
        # Find and replace the import
        for node in self.tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                try:
                    node_source = astunparse.unparse(node).strip()
                    # More precise matching: check if old_import matches the full import statement
                    # Normalize both for comparison (remove extra spaces)
                    normalized_old = ' '.join(op.old_import.split())
                    normalized_node = ' '.join(node_source.split())
                    
                    # Check exact match or if old_import is contained in node (but be careful)
                    if normalized_old == normalized_node or (
                        normalized_old in normalized_node and 
                        len(normalized_old) > 10  # Avoid false positives with short strings
                    ):
                        new_import_ast = ast.parse(op.new_import).body[0]
                        if not isinstance(new_import_ast, (ast.Import, ast.ImportFrom)):
                            return False, "New import is not a valid import statement"
                        # Replace the node
                        idx = self.tree.body.index(node)
                        self.tree.body[idx] = new_import_ast
                        return True, None
                except Exception as e:
                    logger.warning(f"Error processing import node: {e}")
                    continue
        
        return False, f"Import '{op.old_import}' not found"
    
    def _add_class(self, op: SurgicalOperation) -> Tuple[bool, Optional[str]]:
        """Add a class to the module."""
        if not op.code:
            return False, "Missing code for add_class"
        
        try:
            class_ast = ast.parse(op.code).body[0]
            if not isinstance(class_ast, ast.ClassDef):
                return False, "Code is not a class definition"
        except SyntaxError as e:
            return False, f"Invalid class code: {e}"
        
        # Insert at appropriate position
        if op.position == 'end':
            self.tree.body.append(class_ast)
        elif op.position == 'after' and op.after_class:
            # Find the class to insert after
            insert_idx = len(self.tree.body)
            for i, node in enumerate(self.tree.body):
                if isinstance(node, ast.ClassDef) and node.name == op.after_class:
                    insert_idx = i + 1
                    break
            self.tree.body.insert(insert_idx, class_ast)
        else:
            # Default: append at end
            self.tree.body.append(class_ast)
        
        return True, None
    
    def _add_function(self, op: SurgicalOperation) -> Tuple[bool, Optional[str]]:
        """Add a module-level function."""
        if not op.code:
            return False, "Missing code for add_function"
        
        try:
            func_ast = ast.parse(op.code).body[0]
            if not isinstance(func_ast, ast.FunctionDef):
                return False, "Code is not a function definition"
        except SyntaxError as e:
            return False, f"Invalid function code: {e}"
        
        # Insert at appropriate position (after imports, before classes typically)
        insert_idx = len(self.tree.body)
        for i, node in enumerate(self.tree.body):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            elif isinstance(node, ast.ClassDef):
                insert_idx = i
                break
        
        self.tree.body.insert(insert_idx, func_ast)
        return True, None
    
    def _modify_method(self, op: SurgicalOperation) -> Tuple[bool, Optional[str]]:
        """Modify an existing method by replacing it with new code."""
        if not op.target or not op.code:
            return False, "Missing target or code for modify_method"

        # Parse target: can be "ClassName.method_name" or just "method_name"
        if '.' in op.target:
            class_name, method_name = op.target.rsplit('.', 1)
        else:
            class_name = None
            method_name = op.target

        # Find and replace the method
        method_found = False

        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                if class_name and node.name != class_name:
                    continue

                # Search for method in class body
                for i, child in enumerate(node.body):
                    if isinstance(child, ast.FunctionDef) and child.name == method_name:
                        # Found the method, replace it
                        try:
                            new_method_ast = ast.parse(op.code).body[0]
                            if not isinstance(new_method_ast, ast.FunctionDef):
                                return False, "Replacement code is not a function definition"
                            node.body[i] = new_method_ast
                            method_found = True
                            break
                        except SyntaxError as e:
                            return False, f"Invalid method code: {e}"

                if method_found:
                    break

            elif isinstance(node, ast.Module) and class_name is None:
                # Module-level function
                for i, child in enumerate(node.body):
                    if isinstance(child, ast.FunctionDef) and child.name == method_name:
                        try:
                            new_func_ast = ast.parse(op.code).body[0]
                            if not isinstance(new_func_ast, ast.FunctionDef):
                                return False, "Replacement code is not a function definition"
                            node.body[i] = new_func_ast
                            method_found = True
                            break
                        except SyntaxError as e:
                            return False, f"Invalid function code: {e}"

        if not method_found:
            target_desc = f"{class_name}.{method_name}" if class_name else method_name
            return False, f"Method {target_desc} not found"

        return True, None


class SurgicalEditor:
    """Main interface for surgical editing."""
    
    def __init__(self, file_path: Path):
        """
        Initialize surgical editor.
        
        Args:
            file_path: Path to target file
        """
        self.file_path = file_path
        self.parser = ASTParser(file_path)
        self.applier: Optional[SurgicalApplier] = None
        
    def prepare(self) -> bool:
        """
        Parse the file and prepare for editing.
        
        Returns:
            True if preparation succeeded
        """
        if not self.file_path.exists():
            logger.warning(f"Cannot prepare SurgicalEditor: file does not exist: {self.file_path}")
            return False
        
        if not self.parser.parse():
            return False
        
        self.applier = SurgicalApplier(self.file_path, self.parser)
        return True
    
    @staticmethod
    def create_new_file(file_path: Path, llm_output: str) -> Tuple[bool, str]:
        """
        Create a new file from surgical instructions or raw code.
        
        This is a static method for creating new files (where surgical editing
        doesn't apply since there's no existing code to modify).
        
        Args:
            file_path: Path to the new file to create
            llm_output: Raw LLM output (surgical instructions or code)
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Check if output contains surgical instructions
            if SurgicalInstructionParser.is_surgical_output(llm_output):
                # Try to extract code from operations
                operations, error = SurgicalInstructionParser.parse_instructions(llm_output)
                if operations:
                    # Collect all code from operations
                    code_parts = []
                    for op in operations:
                        if op.code:
                            code_parts.append(op.code)
                    
                    if code_parts:
                        # Join with newlines, ensuring each part ends with a newline
                        code_content = "\n\n".join(
                            part if part.endswith("\n") else part + "\n"
                            for part in code_parts
                        )
                    else:
                        code_content = llm_output
                else:
                    code_content = llm_output
            else:
                # Use output directly
                code_content = llm_output
            
            # Clean up markdown code blocks if present
            if code_content.startswith('```'):
                lines = code_content.split('\n')
                if lines[0].strip().startswith('```'):
                    lines = lines[1:]
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                code_content = '\n'.join(lines).strip()
            
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Validate Python syntax before writing
            if file_path.suffix == '.py':
                try:
                    ast.parse(code_content)
                except SyntaxError as e:
                    return False, f"Syntax error in generated code: {e}"
            
            # Write the new file
            file_path.write_text(code_content, encoding='utf-8')
            return True, f"Created {file_path}"
            
        except Exception as e:
            logger.exception(f"Failed to create new file {file_path}")
            return False, f"Error creating file: {e}"
    
    def get_ast_context(self) -> str:
        """
        Get AST structure context for prompts.
        
        Returns:
            Formatted AST structure string
        """
        return self.parser.get_structure_summary()
    
    def apply_instructions(self, llm_output: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Apply surgical instructions from LLM output.
        
        On failure: returns (False, error_message, original_code). The caller
        should NOT overwrite the file; original_code is provided for optional
        restore. Fallback to normal (full-file) apply is recommended.
        
        Args:
            llm_output: Raw LLM output containing instructions
            
        Returns:
            Tuple of (success, modified_code or error_message, original_code)
        """
        if not self.applier:
            if not self.prepare():
                return False, "Failed to parse file", None
        
        # Save original code first (for restore on failure)
        original_code = self.file_path.read_text(encoding='utf-8') if self.file_path.exists() else ""
        
        # Parse instructions
        operations, error = SurgicalInstructionParser.parse_instructions(llm_output)
        if not operations:
            return False, error or "Failed to parse instructions", original_code or None
        
        # Apply operations (validation and syntax check done inside apply_operations)
        success, result = self.applier.apply_operations(operations)
        
        if success:
            return True, result, original_code or None
        return False, result, original_code or None

