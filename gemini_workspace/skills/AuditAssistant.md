# Skill: Audit Assistant

**Purpose**: Guides Gemini in performing comprehensive codebase audits.

**Workflow**:
1.  **Analyze Request**: Understand the scope and specific focus of the audit (e.g., security, quality, architecture).
2.  **Tool Selection**: Identify and execute relevant static analysis tools (mypy, flake8, bandit, pip-audit, radon, vulture, safety).
3.  **Report Generation**: Compile raw tool outputs into structured reports (e.g., AUDIT_CODEBASE_COMPLET.md, domain-specific reports).
4.  **Issue Prioritization**: Analyze findings, categorize by severity, and prioritize based on impact and effort.
5.  **Action Plan Formulation**: Develop a prioritized, actionable plan for fixes, including estimated effort and target scores.
6.  **Verification**: After fixes are applied, re-run relevant tools/tests to verify improvements.

**Resources**:
*   `docs/support/audit/` (output directory for reports)
*   `Backend/Prod/` (target codebase)
*   `venv/bin/activate` (Python virtual environment)

**Key Metrics**:
*   Number of mypy errors
*   Number of passed/failed tests
*   Code coverage percentage
*   Number of security vulnerabilities (bandit, pip-audit)
*   Code complexity (radon)
*   Maintainability index (radon)
