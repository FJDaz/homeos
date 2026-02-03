#!/usr/bin/env python3
"""
Script d'audit pré-revue pour AetherFlow.

Exécute une série de vérifications automatisées pour évaluer
l'état du projet avant la revue senior.

Usage:
    python scripts/audit_pre_review.py [--output report.json]
"""
import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class AuditResult:
    """Result of a single audit check."""
    category: str
    check: str
    status: str  # "PASS", "WARN", "FAIL"
    message: str
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}


class AetherFlowAuditor:
    """Main auditor class."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.results: List[AuditResult] = []
        self.stats = {
            "total": 0,
            "pass": 0,
            "warn": 0,
            "fail": 0
        }
    
    def run_all_audits(self) -> None:
        """Run all audit checks."""
        print("🔍 Démarrage de l'audit AetherFlow...")
        print("=" * 60)
        
        # Security audits
        self.audit_secrets_exposure()
        self.audit_file_permissions()
        self.audit_docker_security()
        
        # Code quality
        self.audit_code_complexity()
        self.audit_test_coverage()
        self.audit_type_hints()
        
        # Configuration
        self.audit_env_files()
        self.audit_dependencies()
        
        # Documentation
        self.audit_documentation()
        
        print("=" * 60)
    
    def audit_secrets_exposure(self) -> None:
        """Check for potential secret exposure in code."""
        print("\n🔐 Audit: Exposition des secrets...")
        
        dangerous_patterns = [
            (r'api_key\s*=\s*["\'][^"\']+["\']', "API key en dur"),
            (r'password\s*=\s*["\'][^"\']+["\']', "Password en dur"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "Secret en dur"),
            (r'token\s*=\s*["\'][^"\']+["\']', "Token en dur"),
            (r'Authorization.*Bearer\s+[a-zA-Z0-9_-]+', "Bearer token en dur"),
            (r'private_key', "Clé privée potentielle"),
        ]
        
        backend_dir = self.project_root / "Backend" / "Prod"
        findings = []
        
        for py_file in backend_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
                
            try:
                content = py_file.read_text(encoding='utf-8')
                for pattern, desc in dangerous_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # Exclude env var defaults like "your_key_here"
                        if "your_" in match.group() or "example" in match.group():
                            continue
                        findings.append({
                            "file": str(py_file.relative_to(self.project_root)),
                            "line": content[:match.start()].count('\n') + 1,
                            "pattern": desc,
                            "snippet": match.group()[:50] + "..."
                        })
            except Exception as e:
                print(f"  ⚠️  Erreur lecture {py_file}: {e}")
        
        if findings:
            self.add_result("Security", "Secrets Exposure", "FAIL", 
                          f"{len(findings)} potentielles expositions trouvées", 
                          {"findings": findings[:10]})
        else:
            self.add_result("Security", "Secrets Exposure", "PASS", 
                          "Aucun secret exposé détecté")
    
    def audit_file_permissions(self) -> None:
        """Check sensitive file permissions."""
        print("\n📁 Audit: Permissions des fichiers...")
        
        sensitive_files = [
            ".env",
            "Backend/.env",
        ]
        
        issues = []
        for file_name in sensitive_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                stat = file_path.stat()
                # Check if readable by others (world-readable)
                if stat.st_mode & 0o044:
                    issues.append(f"{file_name} est lisible par tous (mode: {oct(stat.st_mode)})")
        
        # Check .gitignore
        gitignore = self.project_root / ".gitignore"
        if gitignore.exists():
            content = gitignore.read_text()
            if ".env" not in content:
                issues.append(".env n'est pas dans .gitignore")
        
        if issues:
            self.add_result("Security", "File Permissions", "WARN", 
                          f"{len(issues)} problèmes de permissions", 
                          {"issues": issues})
        else:
            self.add_result("Security", "File Permissions", "PASS", 
                          "Permissions OK")
    
    def audit_docker_security(self) -> None:
        """Check Dockerfile security best practices."""
        print("\n🐳 Audit: Sécurité Docker...")
        
        dockerfile = self.project_root / "Backend" / "Dockerfile"
        issues = []
        
        if not dockerfile.exists():
            self.add_result("Docker", "Dockerfile", "FAIL", "Dockerfile non trouvé")
            return
        
        content = dockerfile.read_text()
        
        # Check for non-root user
        if "USER" not in content:
            issues.append("Pas d'utilisateur non-root (USER)")
        
        # Check for multi-stage build
        if "FROM" in content and content.count("FROM") < 2:
            issues.append("Pas de multi-stage build (optimisation)")
        
        # Check for healthcheck
        if "HEALTHCHECK" not in content:
            issues.append("Pas de HEALTHCHECK")
        
        # Check for secrets in build args (avoid)
        if "ARG" in content and any(x in content for x in ["KEY", "SECRET", "PASSWORD"]):
            issues.append("Potentiels secrets dans ARG (utiliser secrets Docker)")
        
        if issues:
            self.add_result("Docker", "Dockerfile Security", "WARN", 
                          f"{len(issues)} améliorations possibles", 
                          {"issues": issues})
        else:
            self.add_result("Docker", "Dockerfile Security", "PASS", 
                          "Bonnes pratiques respectées")
    
    def audit_code_complexity(self) -> None:
        """Analyze code complexity."""
        print("\n📊 Audit: Complexité du code...")
        
        backend_dir = self.project_root / "Backend" / "Prod"
        
        total_lines = 0
        total_functions = 0
        total_classes = 0
        
        for py_file in backend_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                total_lines += len(content.splitlines())
                
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        total_functions += 1
                    elif isinstance(node, ast.ClassDef):
                        total_classes += 1
            except:
                pass
        
        self.add_result("Code Quality", "Code Complexity", "PASS", 
                      f"{total_lines} lignes, {total_functions} fonctions, {total_classes} classes",
                      {"lines": total_lines, "functions": total_functions, "classes": total_classes})
    
    def audit_test_coverage(self) -> None:
        """Check test coverage."""
        print("\n🧪 Audit: Tests...")
        
        test_dirs = [
            self.project_root / "Backend" / "Prod" / "tests",
            self.project_root / "tests",
        ]
        
        total_test_files = 0
        total_tests = 0
        
        for test_dir in test_dirs:
            if test_dir.exists():
                for test_file in test_dir.rglob("test_*.py"):
                    total_test_files += 1
                    try:
                        content = test_file.read_text()
                        # Count test functions
                        total_tests += len(re.findall(r'^\s*def test_', content, re.MULTILINE))
                    except:
                        pass
        
        if total_tests == 0:
            self.add_result("Code Quality", "Test Coverage", "FAIL", 
                          "Aucun test trouvé")
        elif total_tests < 50:
            self.add_result("Code Quality", "Test Coverage", "WARN", 
                          f"{total_tests} tests trouvés (objectif: 100+)",
                          {"test_files": total_test_files, "tests": total_tests})
        else:
            self.add_result("Code Quality", "Test Coverage", "PASS", 
                          f"{total_tests} tests dans {total_test_files} fichiers",
                          {"test_files": total_test_files, "tests": total_tests})
    
    def audit_type_hints(self) -> None:
        """Check type hints usage."""
        print("\n📝 Audit: Type Hints...")
        
        backend_dir = self.project_root / "Backend" / "Prod"
        
        files_with_typing = 0
        files_without_typing = 0
        
        for py_file in backend_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            
            try:
                content = py_file.read_text()
                if "from typing import" in content or "import typing" in content or "-> " in content:
                    files_with_typing += 1
                else:
                    files_without_typing += 1
            except:
                pass
        
        ratio = files_with_typing / (files_with_typing + files_without_typing + 0.001)
        
        if ratio < 0.5:
            status = "WARN"
        else:
            status = "PASS"
        
        self.add_result("Code Quality", "Type Hints", status, 
                      f"{int(ratio*100)}% des fichiers utilisent les type hints",
                      {"with_typing": files_with_typing, "without": files_without_typing})
    
    def audit_env_files(self) -> None:
        """Check environment configuration."""
        print("\n⚙️  Audit: Configuration...")
        
        issues = []
        
        # Check .env.example exists
        env_example = self.project_root / ".env.example"
        if not env_example.exists():
            issues.append(".env.example manquant")
        
        # Check settings.py uses pydantic
        settings_file = self.project_root / "Backend" / "Prod" / "config" / "settings.py"
        if settings_file.exists():
            content = settings_file.read_text()
            if "pydantic" not in content:
                issues.append("Pas de Pydantic Settings (validation recommandée)")
        
        if issues:
            self.add_result("Configuration", "Environment", "WARN", 
                          f"{len(issues)} problèmes", {"issues": issues})
        else:
            self.add_result("Configuration", "Environment", "PASS", 
                          "Configuration bien structurée")
    
    def audit_dependencies(self) -> None:
        """Check dependencies for security issues."""
        print("\n📦 Audit: Dépendances...")
        
        req_file = self.project_root / "requirements.txt"
        if not req_file.exists():
            self.add_result("Dependencies", "Requirements", "FAIL", "requirements.txt non trouvé")
            return
        
        content = req_file.read_text()
        
        # Check for pinned versions
        unpinned = []
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and '==' not in line and '>=' not in line:
                unpinned.append(line)
        
        if len(unpinned) > 5:
            self.add_result("Dependencies", "Pinned Versions", "WARN", 
                          f"{len(unpinned)} dépendances non épinglées",
                          {"unpinned": unpinned[:5]})
        else:
            self.add_result("Dependencies", "Pinned Versions", "PASS", 
                          "Dépendances bien épinglées")
    
    def audit_documentation(self) -> None:
        """Check documentation completeness."""
        print("\n📚 Audit: Documentation...")
        
        required_docs = [
            "README.md",
            "docs/",
        ]
        
        missing = []
        for doc in required_docs:
            path = self.project_root / doc
            if not path.exists():
                missing.append(doc)
        
        if missing:
            self.add_result("Documentation", "Required Docs", "WARN", 
                          f"{len(missing)} documents manquants", {"missing": missing})
        else:
            self.add_result("Documentation", "Required Docs", "PASS", 
                          "Documentation de base présente")
    
    def add_result(self, category: str, check: str, status: str, message: str, details: Dict = None) -> None:
        """Add an audit result."""
        result = AuditResult(category, check, status, message, details)
        self.results.append(result)
        
        self.stats["total"] += 1
        if status == "PASS":
            self.stats["pass"] += 1
            icon = "✅"
        elif status == "WARN":
            self.stats["warn"] += 1
            icon = "⚠️"
        else:
            self.stats["fail"] += 1
            icon = "❌"
        
        print(f"  {icon} [{status}] {check}: {message}")
    
    def generate_report(self, output_file: Path = None) -> None:
        """Generate audit report."""
        print("\n" + "=" * 60)
        print("📊 RAPPORT D'AUDIT")
        print("=" * 60)
        
        # Summary
        print(f"\nTotal: {self.stats['total']} checks")
        print(f"  ✅ PASS: {self.stats['pass']}")
        print(f"  ⚠️  WARN: {self.stats['warn']}")
        print(f"  ❌ FAIL: {self.stats['fail']}")
        
        score = (self.stats['pass'] * 100 + self.stats['warn'] * 50) / max(self.stats['total'], 1)
        print(f"\nScore: {score:.0f}/100")
        
        if score >= 80:
            print("🟢 ÉTAT: Bon - Prêt pour revue")
        elif score >= 60:
            print("🟡 ÉTAT: Moyen - Corrections recommandées avant revue")
        else:
            print("🔴 ÉTAT: Critique - Corrections requises avant revue")
        
        # Write JSON report if requested
        if output_file:
            report = {
                "timestamp": datetime.now().isoformat(),
                "score": score,
                "stats": self.stats,
                "results": [asdict(r) for r in self.results]
            }
            output_file.write_text(json.dumps(report, indent=2))
            print(f"\n📄 Rapport sauvegardé: {output_file}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Audit AetherFlow before senior review")
    parser.add_argument("--output", "-o", type=str, help="Output JSON file for report")
    args = parser.parse_args()
    
    # Find project root
    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent
    
    auditor = AetherFlowAuditor(project_root)
    auditor.run_all_audits()
    
    output_file = Path(args.output) if args.output else None
    auditor.generate_report(output_file)
    
    # Exit with error code if FAIL found
    if auditor.stats['fail'] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
