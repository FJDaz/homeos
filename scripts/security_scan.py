#!/usr/bin/env python3
"""
Security scanner for AetherFlow.

Scans for:
- Hardcoded secrets
- Insecure dependencies
- Security misconfigurations
- Potential injection points

Usage:
    python scripts/security_scan.py [--fix]
"""
import re
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class SecurityFinding:
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str
    file: str
    line: int
    message: str
    suggestion: str


class SecretScanner:
    """Scanner for hardcoded secrets."""
    
    PATTERNS = [
        # API Keys
        (r'[a-zA-Z_]*api_key\s*=\s*["\']([a-zA-Z0-9_-]{20,})["\']', "API Key", "CRITICAL"),
        (r'[a-zA-Z_]*apikey\s*=\s*["\']([a-zA-Z0-9_-]{20,})["\']', "API Key", "CRITICAL"),
        
        # Secrets
        (r'[a-zA-Z_]*secret\s*=\s*["\']([a-zA-Z0-9_-]{16,})["\']', "Secret", "CRITICAL"),
        (r'[a-zA-Z_]*password\s*=\s*["\']([^"\']{8,})["\']', "Password", "CRITICAL"),
        (r'[a-zA-Z_]*token\s*=\s*["\']([a-zA-Z0-9_-]{20,})["\']', "Token", "CRITICAL"),
        
        # AWS Keys
        (r'AKIA[0-9A-Z]{16}', "AWS Access Key", "CRITICAL"),
        (r'aws_secret_access_key\s*=\s*["\']([a-zA-Z0-9/+=]{40})["\']', "AWS Secret", "CRITICAL"),
        
        # Private Keys
        (r'-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----', "Private Key", "CRITICAL"),
        
        # GitHub Tokens
        (r'gh[pousr]_[A-Za-z0-9_]{36,}', "GitHub Token", "CRITICAL"),
        
        # Generic high-entropy strings that look like secrets
        (r'["\']([a-zA-Z0-9_-]{32,64})["\']', "High-entropy string (potential secret)", "MEDIUM"),
    ]
    
    EXCLUDED_PATTERNS = [
        r'your_', r'example', r'test_', r'fake_', r'dummy_',
        r'placeholder', r'xxxxxxxx', r'\*\*\*', r'changeme',
        r'__pycache__', r'\.pyc$',
    ]
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.findings: List[SecurityFinding] = []
    
    def scan(self) -> List[SecurityFinding]:
        """Scan all Python files for secrets."""
        backend_dir = self.project_root / "Backend" / "Prod"
        
        for py_file in backend_dir.rglob("*.py"):
            if self._is_excluded(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                self._scan_file(py_file, content)
            except Exception as e:
                print(f"Error reading {py_file}: {e}")
        
        return self.findings
    
    def _is_excluded(self, file_path: Path) -> bool:
        """Check if file should be excluded."""
        path_str = str(file_path)
        for pattern in self.EXCLUDED_PATTERNS:
            if re.search(pattern, path_str, re.IGNORECASE):
                return True
        return False
    
    def _scan_file(self, file_path: Path, content: str) -> None:
        """Scan a single file."""
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for pattern, secret_type, severity in self.PATTERNS:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    # Check if it's a false positive
                    if self._is_false_positive(match.group(), line):
                        continue
                    
                    finding = SecurityFinding(
                        severity=severity,
                        category="Hardcoded Secret",
                        file=str(file_path.relative_to(self.project_root)),
                        line=line_num,
                        message=f"Potential {secret_type} detected",
                        suggestion="Use environment variables or a secret manager"
                    )
                    self.findings.append(finding)
    
    def _is_false_positive(self, match: str, line: str) -> bool:
        """Check if match is a false positive."""
        # Check excluded patterns
        for pattern in self.EXCLUDED_PATTERNS:
            if re.search(pattern, match, re.IGNORECASE):
                return True
        
        # Check if it's a settings/env var default
        if 'settings' in line or 'environ' in line or 'getenv' in line:
            return True
        
        # Check if it's a type hint
        if '->' in line and ':' in line:
            return True
        
        return False


class SecurityConfigScanner:
    """Scanner for security misconfigurations."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.findings: List[SecurityFinding] = []
    
    def scan(self) -> List[SecurityFinding]:
        """Scan for security misconfigurations."""
        self._scan_dockerfile()
        self._scan_api_routes()
        self._scan_file_uploads()
        self._scan_sql_injection()
        return self.findings
    
    def _scan_dockerfile(self) -> None:
        """Check Dockerfile security."""
        dockerfile = self.project_root / "Backend" / "Dockerfile"
        if not dockerfile.exists():
            return
        
        content = dockerfile.read_text()
        
        # Check for root user
        if "USER root" in content:
            self.findings.append(SecurityFinding(
                severity="HIGH",
                category="Container Security",
                file="Backend/Dockerfile",
                line=0,
                message="Dockerfile uses root user",
                suggestion="Use non-root user (USER instruction)"
            ))
        
        # Check for latest tag
        if ":latest" in content:
            self.findings.append(SecurityFinding(
                severity="MEDIUM",
                category="Container Security",
                file="Backend/Dockerfile",
                line=0,
                message="Using 'latest' tag in FROM",
                suggestion="Pin to specific version (e.g., python:3.11-slim-bookworm)"
            ))
    
    def _scan_api_routes(self) -> None:
        """Check API routes for missing auth."""
        api_file = self.project_root / "Backend" / "Prod" / "api.py"
        if not api_file.exists():
            return
        
        content = api_file.read_text()
        
        # Check for auth decorators
        has_auth = any(x in content for x in ["Depends", "HTTPBearer", "OAuth2", "APIKey"])
        
        if not has_auth:
            self.findings.append(SecurityFinding(
                severity="HIGH",
                category="API Security",
                file="Backend/Prod/api.py",
                line=0,
                message="No authentication mechanism detected",
                suggestion="Implement API key or OAuth2 authentication"
            ))
    
    def _scan_file_uploads(self) -> None:
        """Check for insecure file uploads."""
        backend_dir = self.project_root / "Backend" / "Prod"
        
        for py_file in backend_dir.rglob("*.py"):
            try:
                content = py_file.read_text()
                
                # Check for upload endpoints without validation
                if "UploadFile" in content or "File(..." in content:
                    if ".suffix" not in content and "extension" not in content:
                        self.findings.append(SecurityFinding(
                            severity="MEDIUM",
                            category="File Upload",
                            file=str(py_file.relative_to(self.project_root)),
                            line=0,
                            message="File upload without extension validation",
                            suggestion="Validate file extensions and MIME types"
                        ))
            except:
                pass
    
    def _scan_sql_injection(self) -> None:
        """Check for potential SQL injection."""
        backend_dir = self.project_root / "Backend" / "Prod"
        
        sql_patterns = [
            r'execute\s*\(\s*["\'].*%s',
            r'execute\s*\(\s*["\'].*\{',
            r'execute\s*\(\s*f["\']',
        ]
        
        for py_file in backend_dir.rglob("*.py"):
            try:
                content = py_file.read_text()
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    for pattern in sql_patterns:
                        if re.search(pattern, line):
                            self.findings.append(SecurityFinding(
                                severity="HIGH",
                                category="SQL Injection",
                                file=str(py_file.relative_to(self.project_root)),
                                line=line_num,
                                message="Potential SQL injection (string formatting in query)",
                                suggestion="Use parameterized queries"
                            ))
            except:
                pass


class DependencyScanner:
    """Scanner for dependency vulnerabilities."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.findings: List[SecurityFinding] = []
    
    def scan(self) -> List[SecurityFinding]:
        """Scan requirements.txt for issues."""
        req_file = self.project_root / "requirements.txt"
        if not req_file.exists():
            return self.findings
        
        content = req_file.read_text()
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Check for unpinned versions
            if '==' not in line and '>=' not in line and '<' not in line:
                self.findings.append(SecurityFinding(
                    severity="MEDIUM",
                    category="Dependencies",
                    file="requirements.txt",
                    line=line_num,
                    message=f"Unpinned dependency: {line}",
                    suggestion="Pin to specific version (package==1.2.3)"
                ))
            
            # Check for http (not https)
            if line.startswith('http://'):
                self.findings.append(SecurityFinding(
                    severity="HIGH",
                    category="Dependencies",
                    file="requirements.txt",
                    line=line_num,
                    message="HTTP URL in dependency (not HTTPS)",
                    suggestion="Use HTTPS for all external dependencies"
                ))
        
        return self.findings


def print_findings(findings: List[SecurityFinding]) -> None:
    """Print findings in a readable format."""
    if not findings:
        print("\n✅ No security issues found!")
        return
    
    # Group by severity
    by_severity: Dict[str, List[SecurityFinding]] = {
        "CRITICAL": [],
        "HIGH": [],
        "MEDIUM": [],
        "LOW": []
    }
    
    for f in findings:
        by_severity[f.severity].append(f)
    
    print(f"\n{'=' * 70}")
    print("SECURITY SCAN RESULTS")
    print(f"{'=' * 70}")
    print(f"Total findings: {len(findings)}")
    print(f"  CRITICAL: {len(by_severity['CRITICAL'])}")
    print(f"  HIGH: {len(by_severity['HIGH'])}")
    print(f"  MEDIUM: {len(by_severity['MEDIUM'])}")
    print(f"  LOW: {len(by_severity['LOW'])}")
    print()
    
    # Print findings by severity
    icons = {
        "CRITICAL": "🔴",
        "HIGH": "🟠",
        "MEDIUM": "🟡",
        "LOW": "🔵"
    }
    
    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        severity_findings = by_severity[severity]
        if severity_findings:
            print(f"\n{icons[severity]} {severity} ({len(severity_findings)})")
            print("-" * 70)
            
            for finding in severity_findings:
                print(f"\n  [{finding.category}]")
                print(f"  File: {finding.file}:{finding.line}")
                print(f"  Issue: {finding.message}")
                print(f"  Fix: {finding.suggestion}")


def main():
    parser = argparse.ArgumentParser(description="Security scan for AetherFlow")
    parser.add_argument("--json", "-j", action="store_true", help="Output JSON format")
    parser.add_argument("--output", "-o", type=str, help="Output file")
    args = parser.parse_args()
    
    project_root = Path(__file__).parent.parent.resolve()
    
    all_findings: List[SecurityFinding] = []
    
    print("🔒 Running security scans...")
    print()
    
    # Run all scanners
    print("1. Scanning for hardcoded secrets...")
    secret_scanner = SecretScanner(project_root)
    all_findings.extend(secret_scanner.scan())
    
    print("2. Scanning for security misconfigurations...")
    config_scanner = SecurityConfigScanner(project_root)
    all_findings.extend(config_scanner.scan())
    
    print("3. Scanning dependencies...")
    dep_scanner = DependencyScanner(project_root)
    all_findings.extend(dep_scanner.scan())
    
    # Output results
    if args.json:
        output = {
            "findings": [
                {
                    "severity": f.severity,
                    "category": f.category,
                    "file": f.file,
                    "line": f.line,
                    "message": f.message,
                    "suggestion": f.suggestion
                }
                for f in all_findings
            ]
        }
        
        if args.output:
            Path(args.output).write_text(json.dumps(output, indent=2))
            print(f"\nReport saved to {args.output}")
        else:
            print(json.dumps(output, indent=2))
    else:
        print_findings(all_findings)
    
    # Exit with error code if critical findings
    critical_count = len([f for f in all_findings if f.severity == "CRITICAL"])
    high_count = len([f for f in all_findings if f.severity == "HIGH"])
    
    if critical_count > 0 or high_count > 0:
        print(f"\n❌ {critical_count + high_count} critical/high severity issues found!")
        sys.exit(1)
    else:
        print(f"\n✅ No critical or high severity issues found.")
        sys.exit(0)


if __name__ == "__main__":
    main()
