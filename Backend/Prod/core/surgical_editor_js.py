"""Surgical Edit Mode JS - Precise code modifications via AST for JavaScript.

This module provides functionality to apply precise code modifications
to JavaScript files, wrapping a Node.js AST parser using Acorn.
"""
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from loguru import logger

from .surgical_editor import ASTNodeInfo, SurgicalOperation, SurgicalInstructionParser, SUPPORTED_OPERATIONS

class ASTParserJS:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.source_lines: List[str] = []
        self.source_text: str = ""
        self.nodes: List[ASTNodeInfo] = []
        
    def parse(self) -> bool:
        try:
            if not self.file_path.exists():
                logger.warning(f"File not found: {self.file_path}")
                return False
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                source = f.read()
                self.source_text = source
                self.source_lines = source.splitlines()
            
            # The node parser script path
            parser_script = Path(__file__).parent / "js_parser" / "ast_parser.js"
            if not parser_script.exists():
                logger.error(f"JS parser script not found at {parser_script}")
                return False
                
            result = subprocess.run(
                ["node", str(parser_script), str(self.file_path)],
                capture_output=True, text=True, check=False
            )
            
            if result.returncode != 0:
                logger.error(f"Node.js parser error: {result.stderr}\nCode: {result.returncode}\nOutput: {result.stdout}")
                return False
                
            try:
                data = json.loads(result.stdout)
                if "error" in data:
                    logger.error(f"JS Parser error: {data['error']}")
                    return False
                    
                self.nodes = []
                for n in data.get("nodes", []):
                    # We inject dynamically start_char/end_char into the NodeInfo object 
                    # since the original dataclass doesn't have it natively, we can subclass or just monkeypatch
                    node = ASTNodeInfo(
                        name=n['name'],
                        node_type=n['node_type'],
                        line_start=n['line_start'],
                        line_end=n['line_end'],
                        parent=n['parent']
                    )
                    setattr(node, "start_char", n['start_char'])
                    setattr(node, "end_char", n['end_char'])
                    self.nodes.append(node)
                
                logger.info(f"Parsed {len(self.nodes)} AST nodes from {self.file_path} via Node.js Acorn")
                return True
            except json.JSONDecodeError:
                logger.error(f"Failed to decode JS parser output: {result.stdout}")
                return False
                
        except Exception as e:
            logger.error(f"Error parsing {self.file_path}: {e}")
            return False

    def get_structure_summary(self) -> str:
        if not self.nodes:
            return "No structure found."
        
        lines = ["AST Structure:"]
        classes = [n for n in self.nodes if n.node_type == 'class']
        functions = [n for n in self.nodes if n.node_type == 'function']
        methods_by_class: Dict[str, List[ASTNodeInfo]] = {}
        imports = [n for n in self.nodes if n.node_type == 'import']
        
        for node in self.nodes:
            if node.node_type == 'method' and node.parent:
                if node.parent not in methods_by_class:
                    methods_by_class[node.parent] = []
                methods_by_class[node.parent].append(node)
        
        if imports:
            lines.append("- Imports (lines {}-{})".format(
                min(i.line_start for i in imports),
                max(i.line_end for i in imports)
            ))
        
        for cls in classes:
            methods = methods_by_class.get(cls.name, [])
            lines.append(f"- Class/Object {cls.name} (lines {cls.line_start}-{cls.line_end})")
            for method in methods:
                lines.append(f"  - Method {method.name} (lines {method.line_start}-{method.line_end})")
        
        for func in functions:
            lines.append(f"- Function {func.name} (lines {func.line_start}-{func.line_end})")
        
        return "\n".join(lines)
    
    def find_node(self, name: str, node_type: Optional[str] = None, parent: Optional[str] = None) -> Optional[ASTNodeInfo]:
        for node in self.nodes:
            if node.name == name:
                if node_type and node.node_type != node_type:
                    continue
                if parent and node.parent != parent:
                    continue
                return node
        return None

    def get_char_range(self, name: str, node_type: Optional[str] = None, parent: Optional[str] = None) -> Tuple[int, int]:
        if not self.source_text:
            raise ValueError("No source text. Call parse() first.")
        node_info = self.find_node(name, node_type, parent)
        if not node_info:
            raise ValueError(f"Node '{name}' not found (node_type={node_type!r}, parent={parent!r})")
        
        return getattr(node_info, 'start_char'), getattr(node_info, 'end_char')


class SurgicalApplierJS:
    """Apply surgical operations to JS AST and regenerate code."""
    
    def __init__(self, file_path: Path, parser: ASTParserJS):
        self.file_path = file_path
        self.parser = parser
        self.source_text = parser.source_text
        
    def _validate_operation(self, op: SurgicalOperation) -> Optional[str]:
        if not op or not getattr(op, "op_type", None):
            return "Operation missing type"
        # Support modify_function in case JS LLM decides to replace top level function
        valid_ops = SUPPORTED_OPERATIONS.union({"modify_function"})
        if op.op_type not in valid_ops:
            return f"Unsupported operation type: {op.op_type!r}."
        if op.op_type in ("add_method", "modify_method", "modify_function") and (not op.target or not op.code):
            return f"{op.op_type} requires 'target' and 'code'"
        if op.op_type == "add_import" and not (op.new_import or op.code or getattr(op, "import", None)):
            return "add_import requires 'import' or 'code'"
        if op.op_type == "replace_import" and (not op.old_import or not op.new_import):
            return "replace_import requires 'old' and 'new'"
        return None

    def apply_operations(self, operations: List[SurgicalOperation]) -> Tuple[bool, str]:
        if not operations:
            return False, "No operations to apply"

        for i, op in enumerate(operations):
            err = self._validate_operation(op)
            if err:
                return False, f"Operation {i + 1} invalid: {err}"

        # Try range-based replacement ONLY (since we have exact char ranges from acorn)
        if self.parser.source_text:
            try:
                success, result = self.apply_operations_ranged(operations)
                if success:
                    return True, result
                return False, result
            except Exception as e:
                logger.exception("Surgical apply failed range fallback")
                return False, f"Exception during range apply JS: {e}"
        
        return False, "No source text available."

    def apply_operations_ranged(self, operations) -> Tuple[bool, str]:
        source = self.parser.source_text
        if not source:
            return False, "No source_text in parser. Call parser.parse() first."

        replacements = []

        for i, op in enumerate(operations):
            try:
                if op.op_type in ('modify_method', 'modify_function'):
                    if op.target and '.' in op.target:
                        parent_cls, method_name = op.target.split('.', 1)
                        # Object literal parent could just be simple parent wrapper
                        start, end = self.parser.get_char_range(method_name, parent=parent_cls)
                    else:
                        node_info = self.parser.find_node(op.target) 
                        if not node_info:
                            raise ValueError(f"Target {op.target} not found")
                        start, end = getattr(node_info, 'start_char'), getattr(node_info, 'end_char')
                    
                    # Indent calculation
                    indent_str = ''
                    # Traverse backwards to find indent size
                    p = start - 1
                    while p >= 0 and source[p] != '\n':
                        if source[p] in (' ', '\t'):
                            indent_str = source[p] + indent_str
                        else:
                            indent_str = ''
                        p -= 1
                            
                    code_lines = op.code.splitlines()
                    if code_lines:
                        code_indent = len(code_lines[0]) - len(code_lines[0].lstrip())
                        reindented = '\n'.join(
                            indent_str + line[code_indent:] if line.strip() else line
                            for line in code_lines
                        )
                    else:
                        reindented = op.code
                        
                    # Fix object literal trailing comma support
                    # If this was an object method like `myMethod() { ... },` we don't want to overwrite the comma if there isn't one in the replacement
                    # It's safer to just let the replacement handle it, but for JS it's good to be aware.
                    replacements.append((start, end, reindented))

                elif op.op_type == 'add_method':
                    class_node = self.parser.find_node(op.target, 'class')
                    if not class_node:
                        return False, f"Class/Object '{op.target}' not found"
                    
                    # Insert right before the last closing brace of the class/object
                    insert_pos = getattr(class_node, 'end_char') - 1
                    
                    method_nodes = [n for n in self.parser.nodes if n.node_type == 'method' and n.parent == op.target]
                    if method_nodes:
                        m_line = source.splitlines()[method_nodes[0].line_start - 1]
                        indent_str = m_line[:len(m_line) - len(m_line.lstrip())]
                    else:
                        indent_str = '    '

                    code_lines = op.code.splitlines()
                    code_indent = len(code_lines[0]) - len(code_lines[0].lstrip()) if code_lines else 0
                    reindented = '\n'.join(
                        indent_str + line[code_indent:] if line.strip() else line
                        for line in code_lines
                    )
                    
                    prefix = '\n\n'
                    replacements.append((insert_pos, insert_pos, prefix + reindented.rstrip() + '\n'))

                elif op.op_type == 'add_import':
                    imports = [n for n in self.parser.nodes if n.node_type == 'import']
                    if imports:
                        last_import = max(imports, key=lambda i: getattr(i, 'end_char'))
                        insert_pos = getattr(last_import, 'end_char')
                        prefix = '\n'
                    else:
                        insert_pos = 0
                        prefix = ''
                        
                    new_import = prefix + (op.new_import or op.code or getattr(op, 'import', '')).rstrip() + '\n'
                    replacements.append((insert_pos, insert_pos, new_import))
                    
                else:
                    return False, f"Unsupported operation type for JS Ranged Apply: {op.op_type}"

            except ValueError as e:
                return False, f"Range error on op {op.op_type}/{op.target}: {e}"

        replacements.sort(key=lambda x: x[0], reverse=True)

        result = source
        for start, end, new_text in replacements:
            result = result[:start] + new_text + result[end:]

        return True, result
