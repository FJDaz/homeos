"""Feedback parser for pedagogical feedback from DOUBLE-CHECK validation."""
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class RuleViolation:
    """Represents a rule violation identified in feedback."""
    
    rule: str  # "TDD", "DRY", "SOLID", etc.
    location: str  # "Line 42", "function calculate_sum", etc.
    issue: str  # Description of the problem
    explanation: str  # Why this violates the rule
    suggestion: str  # How to fix it
    code_reference: Optional[str] = None  # Code snippet or line numbers
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule": self.rule,
            "location": self.location,
            "issue": self.issue,
            "explanation": self.explanation,
            "suggestion": self.suggestion,
            "code_reference": self.code_reference
        }


@dataclass
class PedagogicalFeedback:
    """Structured pedagogical feedback from validation."""
    
    is_valid: bool = True
    passed_rules: List[str] = field(default_factory=list)  # List of rules that passed
    violations: List[RuleViolation] = field(default_factory=list)  # List of violations
    overall_feedback: str = ""  # General feedback
    score: float = 1.0  # Score 0.0-1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "score": self.score,
            "passed_rules": self.passed_rules,
            "violations": [v.to_dict() for v in self.violations],
            "overall_feedback": self.overall_feedback
        }


class FeedbackParser:
    """Parser for pedagogical feedback text."""
    
    @staticmethod
    def parse_feedback(text: str) -> PedagogicalFeedback:
        """
        Parse feedback text into structured PedagogicalFeedback.
        
        Expected format:
        ## Validation Results
        
        ### ✅ Passed Checks
        - [Rule]: [Brief confirmation]
        
        ### ❌ Failed Checks
        - **[Rule Name]**: [Location]
          - **Issue**: [What's wrong]
          - **Why**: [Explanation]
          - **Fix**: [How to correct]
          - **Code Reference**: [Line numbers or snippet]
        
        Args:
            text: Feedback text to parse
            
        Returns:
            Parsed PedagogicalFeedback object
        """
        feedback = PedagogicalFeedback()
        
        if not text:
            return feedback
        
        # Normalize line endings
        text = text.replace('\r\n', '\n')
        
        # Extract passed rules
        passed_section = re.search(r'###\s*✅\s*Passed Checks?\s*\n(.*?)(?=###|$)', text, re.DOTALL | re.IGNORECASE)
        if passed_section:
            passed_text = passed_section.group(1)
            # Extract rules from lines starting with "-"
            passed_rules = re.findall(r'-\s*\*\*?([^*]+)\*\*?\s*:\s*(.+)', passed_text)
            for rule, _ in passed_rules:
                feedback.passed_rules.append(rule.strip())
        
        # Extract violations
        failed_section = re.search(r'###\s*❌\s*Failed Checks?\s*\n(.*?)(?=###|$)', text, re.DOTALL | re.IGNORECASE)
        if failed_section:
            failed_text = failed_section.group(1)
            
            # Pattern simplifié et robuste : split par violations
            # Chaque violation commence par "- **Rule**: Location" au début de ligne
            # On split le texte en sections, chaque section étant une violation
            # Format attendu:
            # - **Rule Name**: Location
            #   - **Issue**: ...
            #   - **Why**: ...
            #   - **Fix**: ...
            #   - **Code Reference**: ...
            
            # Split par les lignes qui commencent par "- **" (début de violation)
            # Mais on veut garder les lignes qui commencent par "  - **" (champs de la violation)
            violations_raw = re.split(r'\n(?=-\s*\*\*[^*\n]+\*\*?\s*:)', failed_text)
            
            for violation_block in violations_raw:
                if not violation_block.strip():
                    continue
                
                # Extraire la première ligne qui contient "Rule: Location"
                first_line_match = re.match(r'-\s*\*\*([^*\n]+?)\*\*?\s*:\s*([^\n]+)', violation_block)
                if not first_line_match:
                    continue
                
                rule = first_line_match.group(1).strip()
                location = first_line_match.group(2).strip()
                
                # Vérifier que ce n'est pas juste un champ isolé
                field_names = ['issue', 'why', 'fix', 'code reference', 'explanation', 'suggestion']
                if rule.lower().strip() in field_names:
                    continue
                
                # Le reste du bloc contient les champs (Issue, Why, Fix, Code Reference)
                violation_content = violation_block[first_line_match.end():].strip()
                
                # Extract issue, explanation, suggestion, code_reference
                # Pattern : cherche "**Field**: value" et capture jusqu'au prochain **Field ou fin de ligne suivie de **Field
                issue_match = re.search(r'\*\*Issue\*\*:\s*(.+?)(?=\n\s*-\s*\*\*[A-Z]|$)', violation_content, re.DOTALL | re.IGNORECASE)
                explanation_match = re.search(r'\*\*Why\*\*:\s*(.+?)(?=\n\s*-\s*\*\*[A-Z]|$)', violation_content, re.DOTALL | re.IGNORECASE)
                suggestion_match = re.search(r'\*\*Fix\*\*:\s*(.+?)(?=\n\s*-\s*\*\*[A-Z]|$)', violation_content, re.DOTALL | re.IGNORECASE)
                code_match = re.search(r'\*\*Code Reference\*\*:\s*(.+?)(?=\n\s*-\s*\*\*[A-Z]|$)', violation_content, re.DOTALL | re.IGNORECASE)
                
                # Nettoyer les extractions
                issue = issue_match.group(1).strip() if issue_match else ""
                explanation = explanation_match.group(1).strip() if explanation_match else ""
                suggestion = suggestion_match.group(1).strip() if suggestion_match else ""
                code_ref = code_match.group(1).strip() if code_match else None
                
                # Nettoyer les références de code (retirer les backticks)
                if code_ref:
                    code_ref = re.sub(r'^```[a-z]*\n?', '', code_ref, flags=re.IGNORECASE)
                    code_ref = re.sub(r'\n?```\s*$', '', code_ref)
                    code_ref = code_ref.strip()
                    if not code_ref:
                        code_ref = None
                
                violation = RuleViolation(
                    rule=rule,
                    location=location,
                    issue=issue,
                    explanation=explanation,
                    suggestion=suggestion,
                    code_reference=code_ref
                )
                
                feedback.violations.append(violation)
        
        # Determine validity and score
        feedback.is_valid = len(feedback.violations) == 0
        if feedback.violations:
            # Score decreases with violations
            feedback.score = max(0.0, 1.0 - (len(feedback.violations) * 0.2))
        
        # Extract overall feedback (text before sections)
        overall_match = re.match(r'(.+?)(?=###|$)', text, re.DOTALL)
        if overall_match:
            feedback.overall_feedback = overall_match.group(1).strip()
        
        return feedback
