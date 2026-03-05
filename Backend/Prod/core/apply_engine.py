"""Unified Apply Engine for AetherFlow: handles surgical patches, overwrites, and validation."""
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger
from datetime import datetime

from .surgical_editor import SurgicalEditor, SurgicalInstructionParser
from .surgical_editor_js import SurgicalApplierJS, ASTParserJS
from .post_apply_validator import validate_after_apply
from ..claude_helper import _extract_code_blocks

class ApplyEngine:
    """
    Consolidates all apply logic (surgical, full-file, fallback).
    Integrates validation and auto-rollback.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize ApplyEngine."""
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        logger.info(f"ApplyEngine initialized with project root: {self.project_root}")

    def apply(
        self,
        step_id: str,
        output: str,
        target_files: List[str],
        step_type: str = "refactoring",
        surgical_mode: bool = False,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Apply generated code/patches to target files.
        
        Args:
            step_id: ID of the step that produced the output
            output: Raw LLM output
            target_files: List of file paths to modify
            step_type: 'refactoring' or 'code_generation'
            surgical_mode: Whether surgical mode was active for this step
            context: Step context (contains auto_apply, etc.)
            
        Returns:
            Review results dictionary
        """
        # 1. Check auto_apply flag
        context = context or {}
        auto_apply = context.get("auto_apply", True)
        
        results = {
            "step_id": step_id,
            "applied_files": [],
            "failed_files": [],
            "review_needed": [],
            "validation_results": {}
        }

        if not auto_apply:
            logger.info(f"Auto-apply disabled for step {step_id}. Saving for review.")
            for file_path_str in target_files:
                self._save_for_review(file_path_str, output, results)
            return results

        # 2. Iterate through target files
        for file_path_str in target_files:
            file_path = self._resolve_path(file_path_str)
            
            success = False
            method_used = "none"

            # Strategy Selection
            if surgical_mode and file_path.suffix in (".py", ".js") and step_type == "refactoring" and file_path.exists():
                # TRY SURGICAL
                success, method_used = self._apply_surgical(file_path, output)
            
            if not success:
                # TRY SMART OVERWRITE (as fallback or primary for non-surgical/non-python)
                success, method_used = self._apply_smart_overwrite(file_path, output, step_type)

            if success:
                # 3. Validation
                val_success, val_msg, test_out = self._validate(file_path)
                results["validation_results"][file_path_str] = {
                    "success": val_success,
                    "message": val_msg,
                    "test_output": test_out
                }
                
                if val_success:
                    results["applied_files"].append(f"{file_path_str} ({method_used})")
                    logger.info(f"✓ Successfully applied and validated {file_path_str} via {method_used}")
                else:
                    results["failed_files"].append(f"{file_path_str} (Validation failed: {val_msg})")
                    logger.error(f"✗ Applied {file_path_str} but validation FAILED: {val_msg}")
            else:
                # 4. Review Fallback
                self._save_for_review(file_path_str, output, results)
                logger.warning(f"⚠ Could not safely apply changes to {file_path_str}. Saved .generated file for review.")

        return results

    def _resolve_path(self, path_str: str) -> Path:
        """Resolve path relative to project root."""
        path = Path(path_str)
        if not path.is_absolute():
            path = self.project_root / path
        return path

    def _apply_surgical(self, file_path: Path, output: str) -> Tuple[bool, str]:
        """Attempt surgical patch."""
        if not SurgicalInstructionParser.is_surgical_output(output):
            return False, "no_surgical_json"

        try:
            if file_path.suffix == ".js":
                # Use JS Editor
                parser = ASTParserJS(file_path)
                if not parser.parse():
                    return False, "ast_parse_failed_js"
                applier = SurgicalApplierJS(file_path, parser)
                try:
                    operations, parse_err = SurgicalInstructionParser.parse_instructions(output)
                    if not operations:
                         return False, f"instruction_parse_failed: {parse_err}"
                    success, result_content = applier.apply_operations(operations)
                    if success:
                        self._create_backup(file_path)
                        file_path.write_text(result_content, encoding='utf-8')
                        return True, "surgical_js"
                    else:
                        logger.debug(f"Surgical JS apply failed for {file_path}: {result_content}")
                        return False, f"surgical_js_failed: {result_content}"
                except Exception as e:
                    logger.error(f"Error during surgical JS apply for {file_path}: {e}")
                    return False, "surgical_js_exception"
            else:
                # Use Python Editor
                editor = SurgicalEditor(file_path)
                if not editor.prepare():
                    return False, "ast_parse_failed"

                success, modified_code, error_msg = editor.apply_instructions(output)
                if success and modified_code:
                    # Backup before write
                    self._create_backup(file_path)
                    file_path.write_text(modified_code, encoding='utf-8')
                    return True, "surgical"
                else:
                    logger.debug(f"Surgical apply failed for {file_path}: {error_msg}")
                    return False, f"surgical_failed: {error_msg}"
        except Exception as e:
            logger.error(f"Error during surgical apply for {file_path}: {e}")
            return False, "surgical_exception"

    def _apply_smart_overwrite(self, file_path: Path, output: str, step_type: str) -> Tuple[bool, str]:
        """Extract code blocks and overwrite."""
        code_blocks = _extract_code_blocks(output)
        if not code_blocks:
            return False, "no_code_blocks"

        # Filter out surgical JSON blocks if possible
        selected_block = code_blocks[0]
        if len(code_blocks) > 1:
            for lang, content in code_blocks:
                # If it's a python file, look for python-looking blocks that aren't surgical JSON
                if file_path.suffix == ".py":
                    if (lang in ("python", "py") or "def " in content or "class " in content) and '"operations"' not in content:
                        selected_block = (lang, content)
                        break
        
        _, code_content = selected_block
        
        try:
            # For existing files, create backup
            if file_path.exists():
                self._create_backup(file_path)
            else:
                file_path.parent.mkdir(parents=True, exist_ok=True)

            file_path.write_text(code_content, encoding="utf-8")
            return True, "overwrite"
        except Exception as e:
            logger.error(f"Error during smart overwrite for {file_path}: {e}")
            return False, "overwrite_exception"

    def _save_for_review(self, file_path_str: str, output: str, results: Dict[str, Any]):
        """Save output to a .generated file for manual review."""
        file_path = self._resolve_path(file_path_str)
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            gen_path = file_path.with_suffix(f".generated{file_path.suffix}")
            
            # Try to extract code blocks first for a cleaner review file
            code_blocks = _extract_code_blocks(output)
            if code_blocks:
                content = "\n\n".join(b[1] for b in code_blocks)
            else:
                content = output

            gen_path.write_text(content, encoding="utf-8")
            results["review_needed"].append(str(gen_path))
        except Exception as e:
            logger.error(f"Failed to save review file for {file_path_str}: {e}")

    def _create_backup(self, file_path: Path):
        """Create a .bak file."""
        try:
            bak_path = file_path.with_suffix(f"{file_path.suffix}.bak")
            bak_path.write_text(file_path.read_text(encoding="utf-8"), encoding="utf-8")
        except Exception as e:
            logger.warning(f"Failed to create backup for {file_path}: {e}")

    def _validate(self, file_path: Path) -> Tuple[bool, str, Optional[str]]:
        """Run PostApplyValidator."""
        try:
            # We use auto_rollback=True to revert via git if it fails
            # Note: validate_after_apply uses git checkout -- file
            return validate_after_apply(
                file_path=file_path,
                run_tests=True,
                auto_rollback=True,
                project_root=self.project_root
            )
        except Exception as e:
            logger.error(f"Validation exception for {file_path}: {e}")
            return False, f"Validation exception: {e}", None
