# Skill: Python Type Fixer

**Purpose**: Guides Gemini in resolving mypy type-checking errors in Python code.

**Workflow**:
1.  **Analyze Mypy Report**: Identify the most critical or frequently occurring mypy errors (e.g., `[no-redef]`, `[union-attr]`, `[assignment]`, `PEP 484 implicit Optional`).
2.  **Locate Code**: Pinpoint the exact file and line number(s) where errors occur.
3.  **Understand Context**: Read the relevant code block to understand the types involved and the logic.
4.  **Propose Fix**: Based on the error type and context, propose a surgical fix:
    *   For `[no-redef]`: Remove duplicate imports, resolve circular dependencies, or use `if TYPE_CHECKING:`.
    *   For `[union-attr]`: Add `is not None` checks or narrow down types.
    *   For `[assignment]`/`[return-value]`: Adjust type hints to match actual types or correct code logic.
    *   For `PEP 484 implicit Optional`: Change `def func(arg: Type = None)` to `def func(arg: Optional[Type] = None)`.
    *   For `[var-annotated]`: Add explicit type annotations.
5.  **Apply Fix**: Use `replace` (for simple, isolated changes) or `read_file`/`write_file` (for complex, multi-line/context-dependent changes) to modify the file.
6.  **Verify Fix**: Re-run `mypy` on the affected file or the entire codebase to confirm the error is resolved.
7.  **Document**: Update the audit report (if applicable) with the fix applied.

**Constraints**:
*   **DO NOT** change runtime logic unless explicitly instructed or absolutely necessary to fix a type error. Prioritize type-hint adjustments and type-narrowing.
*   **Prefer explicit over implicit**: Use `Optional[Type]` over implicit `None` defaults.
*   **Surgical changes**: Aim for minimal, targeted modifications.
