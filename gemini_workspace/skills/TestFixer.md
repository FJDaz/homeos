# Skill: Test Fixer

**Purpose**: Guides Gemini in resolving Python test failures (pytest).

**Workflow**:
1.  **Analyze Pytest Report**: Identify test collection errors or specific test failures.
2.  **Collection Errors**:
    *   **ModuleNotFoundError/ImportError**:
        *   Check for incorrect import paths (e.g., missing package prefixes).
        *   Verify `PYTHONPATH` or `pytest.ini` `pythonpath` settings.
        *   Correct test file imports surgically.
        *   If import is due to placeholder or unfixable source code issue, comment out the test or the problematic import within the test, adding a `TODO` comment.
    *   **SyntaxError**: Locate and fix syntax errors in test files.
3.  **Test Failures**:
    *   **Analyze Traceback**: Identify the root cause of the failure (assertion error, unhandled exception, etc.).
    *   **Locate Code**: Pinpoint the test code and the source code under test.
    *   **Reproduce (if possible)**: Mentally simulate the test execution.
    *   **Propose Fix**:
        *   If test logic is flawed, correct the test.
        *   If source code has a bug, identify the bug and suggest a fix (but note: only modify test files unless instructed otherwise).
    *   **Apply Fix**: Modify the test file.
4.  **Verify Fix**: Re-run affected tests or the entire test suite.
5.  **Document**: Update the audit report (if applicable) with the fix applied.

**Resources**:
*   `Backend/Prod/tests/` (test files)
*   `Backend/Prod/` (source code under test)
*   `pytest.ini` (pytest configuration)
*   `pytest-asyncio` (for async tests)

**Constraints**:
*   **DO NOT** delete test files.
*   **DO NOT** modify source code unless explicitly instructed (prioritize test modifications).
*   **Prioritize collection fixes** over individual test failures.
*   If a fix is complex or requires modifying source code, document it and await further instructions.
