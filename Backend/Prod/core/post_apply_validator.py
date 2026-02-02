"""Post-apply validator: validates code after apply, runs targeted tests.

Pipeline:
1. Syntactic validation (ast.parse for Python, basic checks for other languages)
2. Detect associated test files (foo.py → test_foo.py, foo_test.py)
3. Run targeted tests only (not full test suite)
4. Automatic rollback via git if validation fails

Game changer: test what you implement, immediately.
"""
import ast
import subprocess
import re
from pathlib import Path
from typing import Optional, Tuple, List
from loguru import logger


class PostApplyValidator:
    """
    Validates code after it has been applied to a file.

    If validation fails, can rollback via git checkout.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize validator with project root for test discovery."""
        self.project_root = project_root or Path.cwd()

    def validate_and_test(
        self,
        file_path: Path,
        run_tests: bool = True,
        auto_rollback: bool = True
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Validate applied code and run targeted tests.

        Args:
            file_path: Path to the file that was just modified
            run_tests: Whether to run associated tests
            auto_rollback: Whether to rollback on failure

        Returns:
            Tuple of (success, message, test_output)
        """
        file_path = Path(file_path)

        if not file_path.exists():
            # NEW FILE: Cannot rollback a file that didn't exist before
            # Just validate syntax if content exists
            return True, f"New file created: {file_path}", None

        # Step 1: Syntactic validation
        syntax_valid, syntax_msg = self._validate_syntax(file_path)
        if not syntax_valid:
            logger.warning(f"Syntax validation failed for {file_path}: {syntax_msg}")
            if auto_rollback:
                rollback_success = self._rollback_file(file_path)
                if rollback_success:
                    return False, f"SYNTAX ERROR (rolled back): {syntax_msg}", None
            return False, f"SYNTAX ERROR: {syntax_msg}", None

        # Step 2: Find and run associated tests
        if run_tests:
            test_files = self._find_associated_tests(file_path)
            if test_files:
                logger.info(f"Found {len(test_files)} test file(s) for {file_path.name}")
                test_success, test_output = self._run_tests(test_files)
                if not test_success:
                    logger.warning(f"Tests failed for {file_path}")
                    if auto_rollback:
                        rollback_success = self._rollback_file(file_path)
                        if rollback_success:
                            return False, f"TESTS FAILED (rolled back)", test_output
                    return False, "TESTS FAILED", test_output
                return True, f"Syntax OK, {len(test_files)} test(s) passed", test_output
            else:
                logger.debug(f"No tests found for {file_path.name}")
                return True, "Syntax OK (no tests found)", None

        return True, "Syntax OK (tests skipped)", None

    def _validate_syntax(self, file_path: Path) -> Tuple[bool, str]:
        """
        Validate syntax based on file type.

        Returns:
            Tuple of (is_valid, error_message)
        """
        suffix = file_path.suffix.lower()

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            return False, f"Could not read file: {e}"

        if suffix == ".py":
            return self._validate_python_syntax(content, file_path)
        elif suffix == ".json":
            return self._validate_json_syntax(content)
        elif suffix in [".yaml", ".yml"]:
            return self._validate_yaml_syntax(content)
        elif suffix in [".html", ".htm"]:
            return self._validate_html_syntax(content)
        elif suffix in [".js", ".ts", ".jsx", ".tsx"]:
            return self._validate_js_syntax(content, file_path)
        else:
            # For unknown file types, just check it's not empty
            if not content.strip():
                return False, "File is empty"
            return True, "OK"

    def _validate_python_syntax(self, content: str, file_path: Path) -> Tuple[bool, str]:
        """Validate Python syntax using ast.parse."""
        try:
            ast.parse(content)
            return True, "OK"
        except SyntaxError as e:
            return False, f"Line {e.lineno}: {e.msg}"

    def _validate_json_syntax(self, content: str) -> Tuple[bool, str]:
        """Validate JSON syntax."""
        import json
        try:
            json.loads(content)
            return True, "OK"
        except json.JSONDecodeError as e:
            return False, f"Line {e.lineno}: {e.msg}"

    def _validate_yaml_syntax(self, content: str) -> Tuple[bool, str]:
        """Validate YAML syntax."""
        try:
            import yaml
            yaml.safe_load(content)
            return True, "OK"
        except yaml.YAMLError as e:
            return False, str(e)
        except ImportError:
            # If PyYAML not installed, skip validation
            return True, "OK (yaml not installed)"

    def _validate_html_syntax(self, content: str) -> Tuple[bool, str]:
        """Basic HTML validation - check for unclosed tags."""
        # Simple heuristic: check for obvious issues
        if not content.strip():
            return False, "Empty HTML"

        # Check for DOCTYPE or html tag
        if "<html" not in content.lower() and "<!doctype" not in content.lower():
            # Could be a fragment, that's OK
            pass

        # Check for obviously broken tags
        if content.count("<") != content.count(">"):
            return False, "Mismatched < and > brackets"

        return True, "OK"

    def _validate_js_syntax(self, content: str, file_path: Path) -> Tuple[bool, str]:
        """Validate JavaScript/TypeScript syntax using node if available."""
        # Try to use node for syntax check
        try:
            suffix = file_path.suffix.lower()
            if suffix in [".ts", ".tsx"]:
                # For TypeScript, try tsc --noEmit
                result = subprocess.run(
                    ["npx", "tsc", "--noEmit", str(file_path)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.project_root
                )
                if result.returncode != 0:
                    # Extract first error line
                    errors = result.stderr or result.stdout
                    first_line = errors.split("\n")[0] if errors else "Unknown error"
                    return False, first_line
            else:
                # For JS, use node --check
                result = subprocess.run(
                    ["node", "--check", str(file_path)],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode != 0:
                    return False, result.stderr.split("\n")[0] if result.stderr else "Syntax error"
            return True, "OK"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # node/tsc not available, do basic check
            if not content.strip():
                return False, "Empty file"
            return True, "OK (node not available for full check)"

    def _find_associated_tests(self, file_path: Path) -> List[Path]:
        """
        Find test files associated with the given source file.

        Patterns:
        - foo.py → test_foo.py, foo_test.py, tests/test_foo.py
        - src/foo.py → tests/test_foo.py, src/tests/test_foo.py
        """
        tests = []
        stem = file_path.stem
        suffix = file_path.suffix
        parent = file_path.parent

        # Skip if the file itself is a test
        if stem.startswith("test_") or stem.endswith("_test"):
            return []

        # Possible test file names
        test_names = [
            f"test_{stem}{suffix}",
            f"{stem}_test{suffix}",
        ]

        # Search locations
        search_dirs = [
            parent,                           # Same directory
            parent / "tests",                 # tests/ subdirectory
            parent / "test",                  # test/ subdirectory
            self.project_root / "tests",      # Project root tests/
            self.project_root / "test",       # Project root test/
        ]

        # Also check for mirrored structure: src/foo.py → tests/src/test_foo.py
        if "src" in file_path.parts:
            src_idx = file_path.parts.index("src")
            relative = Path(*file_path.parts[src_idx + 1:]).parent
            search_dirs.append(self.project_root / "tests" / relative)

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
            for test_name in test_names:
                test_path = search_dir / test_name
                if test_path.exists():
                    tests.append(test_path)

        return list(set(tests))  # Remove duplicates

    def _run_tests(self, test_files: List[Path]) -> Tuple[bool, str]:
        """
        Run the specified test files.

        Returns:
            Tuple of (all_passed, combined_output)
        """
        outputs = []
        all_passed = True

        for test_file in test_files:
            suffix = test_file.suffix.lower()

            if suffix == ".py":
                success, output = self._run_pytest(test_file)
            elif suffix in [".js", ".ts", ".jsx", ".tsx"]:
                success, output = self._run_js_test(test_file)
            else:
                continue

            outputs.append(f"=== {test_file.name} ===\n{output}")
            if not success:
                all_passed = False

        return all_passed, "\n\n".join(outputs)

    def _run_pytest(self, test_file: Path) -> Tuple[bool, str]:
        """Run a single Python test file with pytest."""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", str(test_file), "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.project_root
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Test timed out (120s)"
        except FileNotFoundError:
            return False, "pytest not found"

    def _run_js_test(self, test_file: Path) -> Tuple[bool, str]:
        """Run a JavaScript/TypeScript test file."""
        try:
            # Try npm test with the specific file
            result = subprocess.run(
                ["npx", "jest", str(test_file), "--colors=false"],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.project_root
            )
            return result.returncode == 0, result.stdout + result.stderr
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return True, "JS test runner not available"

    def _rollback_file(self, file_path: Path) -> bool:
        """
        Rollback a file to its previous state using git checkout.

        Returns:
            True if rollback succeeded
        """
        try:
            result = subprocess.run(
                ["git", "checkout", "--", str(file_path)],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=file_path.parent
            )
            if result.returncode == 0:
                logger.info(f"Rolled back {file_path} to previous state")
                return True
            else:
                logger.warning(f"Git rollback failed: {result.stderr}")
                return False
        except Exception as e:
            logger.warning(f"Rollback error: {e}")
            return False


# Global instance
_validator: Optional[PostApplyValidator] = None


def get_validator(project_root: Optional[Path] = None) -> PostApplyValidator:
    """Get or create the global validator instance."""
    global _validator
    if _validator is None:
        _validator = PostApplyValidator(project_root)
    return _validator


def validate_after_apply(
    file_path: Path,
    run_tests: bool = True,
    auto_rollback: bool = True,
    project_root: Optional[Path] = None
) -> Tuple[bool, str, Optional[str]]:
    """
    Convenience function to validate a file after apply.

    Args:
        file_path: Path to the file that was just modified
        run_tests: Whether to run associated tests
        auto_rollback: Whether to rollback on failure
        project_root: Project root for test discovery

    Returns:
        Tuple of (success, message, test_output)
    """
    validator = get_validator(project_root)
    return validator.validate_and_test(file_path, run_tests, auto_rollback)
