"""Feedback exporter for pedagogical feedback."""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from .feedback_parser import PedagogicalFeedback


class FeedbackExporter:
    """Exporter for pedagogical feedback to different formats."""
    
    def __init__(self, feedback: PedagogicalFeedback):
        """
        Initialize exporter with feedback object.
        
        Args:
            feedback: PedagogicalFeedback object to export
        """
        self.feedback = feedback
    
    def export_json(self, filepath: Path, pretty: bool = True) -> None:
        """
        Export feedback to JSON file.
        
        Args:
            filepath: Path to output file
            pretty: If True, format JSON with indentation
        """
        data = self.feedback.to_dict()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f, ensure_ascii=False)
    
    def export_json_string(self, pretty: bool = True) -> str:
        """
        Export feedback as JSON string.
        
        Args:
            pretty: If True, format JSON with indentation
            
        Returns:
            JSON string representation
        """
        data = self.feedback.to_dict()
        
        if pretty:
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            return json.dumps(data, ensure_ascii=False)
    
    def export_markdown(self, filepath: Path) -> None:
        """
        Export feedback to Markdown file.
        
        Args:
            filepath: Path to output file
        """
        lines = []
        lines.append("# Validation Feedback\n")
        
        # Status
        status = "✅ Passed" if self.feedback.is_valid else "❌ Failed"
        lines.append(f"**Status**: {status}\n")
        lines.append(f"**Score**: {self.feedback.score:.1%}\n")
        
        # Passed rules
        if self.feedback.passed_rules:
            lines.append("\n## ✅ Passed Rules\n")
            for rule in self.feedback.passed_rules:
                lines.append(f"- {rule}\n")
        
        # Violations
        if self.feedback.violations:
            lines.append("\n## ❌ Rule Violations\n")
            for violation in self.feedback.violations:
                lines.append(f"\n### {violation.rule} - {violation.location}\n")
                lines.append(f"**Issue**: {violation.issue}\n")
                lines.append(f"**Why**: {violation.explanation}\n")
                lines.append(f"**Fix**: {violation.suggestion}\n")
                if violation.code_reference:
                    lines.append(f"**Code Reference**:\n```\n{violation.code_reference}\n```\n")
        
        # Overall feedback
        if self.feedback.overall_feedback:
            lines.append("\n## Overall Feedback\n")
            lines.append(f"{self.feedback.overall_feedback}\n")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    
    @staticmethod
    def validate_json_file(filepath: Path) -> bool:
        """
        Validate that a JSON file is correctly formatted.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            True if file is valid, False otherwise
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                json.load(f)
            return True
        except (json.JSONDecodeError, FileNotFoundError):
            return False
