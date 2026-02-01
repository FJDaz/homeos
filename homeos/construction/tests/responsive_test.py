"""
Responsive design testing module for HomeOS components.
Tests Svelte/CSS components for responsive design compliance.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class TestResult:
    """Data class for test results."""
    passed: bool
    score: float
    issues: List[str]
    warnings: List[str]


class ContentAnalyzer(ABC):
    """Abstract base class for content analysis strategies."""
    
    @abstractmethod
    def analyze(self, content: str) -> Tuple[bool, float, List[str], List[str]]:
        """Analyze content and return test results."""
        pass


class ResponsiveCSSAnalyzer(ContentAnalyzer):
    """Analyzes CSS content for responsive design compliance."""
    
    def __init__(self):
        self.forbidden_units = {'px', 'pt', 'pc', 'in', 'cm', 'mm'}
        self.allowed_units = {'%', 'rem', 'em', 'vw', 'vh', 'ch', 'ex'}
        self.responsive_patterns = {
            'media_query': r'@media',
            'flex_display': r'display\s*:\s*flex',
            'grid_display': r'display\s*:\s*grid',
        }
    
    def _find_units(self, content: str) -> Tuple[Set[str], Set[str]]:
        """Find forbidden and allowed units in content."""
        found_forbidden = set()
        found_allowed = set()
        
        # Pattern to match CSS values with units
        unit_pattern = r'\d+(\.\d+)?\s*(px|pt|pc|in|cm|mm|%|rem|em|vw|vh|ch|ex)\b'
        
        for match in re.finditer(unit_pattern, content, re.IGNORECASE):
            unit = match.group(2).lower()
            if unit in self.forbidden_units:
                found_forbidden.add(unit)
            elif unit in self.allowed_units:
                found_allowed.add(unit)
        
        return found_forbidden, found_allowed
    
    def _check_responsive_patterns(self, content: str) -> Dict[str, bool]:
        """Check for responsive design patterns."""
        results = {}
        for pattern_name, pattern in self.responsive_patterns.items():
            results[pattern_name] = bool(re.search(pattern, content, re.IGNORECASE))
        return results
    
    def analyze(self, content: str) -> Tuple[bool, float, List[str], List[str]]:
        """
        Analyze CSS content for responsive design compliance.
        
        Args:
            content: CSS content to analyze
            
        Returns:
            Tuple containing:
            - passed: Whether the test passed
            - score: Responsiveness score (0-1)
            - issues: List of issues found
            - warnings: List of warnings found
        """
        issues = []
        warnings = []
        passed = True
        score = 1.0
        
        # Check for forbidden units
        found_forbidden, found_allowed = self._find_units(content)
        
        if found_forbidden:
            passed = False
            penalty = len(found_forbidden) * 0.2
            score = max(0, score - penalty)
            for unit in found_forbidden:
                issues.append(f"Forbidden unit '{unit}' found")
        
        # Reward allowed units
        if found_allowed:
            bonus = len(found_allowed) * 0.1
            score = min(1.0, score + bonus)
        
        # Check responsive patterns
        pattern_results = self._check_responsive_patterns(content)
        
        if pattern_results['media_query']:
            score = min(1.0, score + 0.1)
            warnings.append("@media queries found - good for responsiveness")
        
        if pattern_results['flex_display'] or pattern_results['grid_display']:
            score = min(1.0, score + 0.1)
            warnings.append("Flexbox or Grid layout found - good for responsiveness")
        
        # Add warning if no responsive patterns found
        if not any(pattern_results.values()):
            warnings.append("No responsive design patterns (@media, flex, grid) found")
        
        return passed, score, issues, warnings


class SvelteComponentAnalyzer:
    """Analyzes Svelte components for responsive design."""
    
    def __init__(self, css_analyzer: ContentAnalyzer):
        self.css_analyzer = css_analyzer
    
    def extract_css_content(self, svelte_content: str) -> str:
        """
        Extract CSS content from Svelte component.
        
        Args:
            svelte_content: Full Svelte component content
            
        Returns:
            Extracted CSS content
        """
        # Extract content from <style> tags
        style_pattern = r'<style[^>]*>(.*?)</style>'
        matches = re.findall(style_pattern, svelte_content, re.DOTALL | re.IGNORECASE)
        
        # Also look for inline styles
        inline_style_pattern = r'style\s*=\s*["\']([^"\']+)["\']'
        inline_matches = re.findall(inline_style_pattern, svelte_content)
        
        css_content = '\n'.join(matches + inline_matches)
        return css_content
    
    def analyze(self, svelte_content: str) -> Tuple[bool, float, List[str], List[str]]:
        """
        Analyze Svelte component for responsive design.
        
        Args:
            svelte_content: Svelte component content
            
        Returns:
            Tuple containing test results
        """
        css_content = self.extract_css_content(svelte_content)
        
        if not css_content:
            return False, 0.0, ["No CSS content found"], []
        
        return self.css_analyzer.analyze(css_content)


class ResponsiveDesignTest:
    """
    Main class for testing responsive design of components.
    
    Tests Svelte/CSS components for responsive design compliance by checking:
    - Forbidden units (px, pt, pc, in, cm, mm)
    - Allowed units (%, rem, em, vw, vh, ch, ex)
    - Presence of @media queries
    - Use of display:flex or display:grid
    """
    
    def __init__(self, css_analyzer: Optional[ContentAnalyzer] = None):
        """
        Initialize ResponsiveDesignTest.
        
        Args:
            css_analyzer: Optional custom CSS analyzer
        """
        self.css_analyzer = css_analyzer or ResponsiveCSSAnalyzer()
        self.svelte_analyzer = SvelteComponentAnalyzer(self.css_analyzer)
    
    def _read_file_content(self, component_path: Path) -> str:
        """
        Read file content with error handling.

        Args:
            component_path: Path to component file

        Returns:
            File content as string

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        return component_path.read_text(encoding="utf-8")

    def test_component(self, component_path: Path) -> Dict:
        """
        Test a Svelte/CSS component for responsive design compliance.

        Args:
            component_path: Path to component file (.svelte or .css)

        Returns:
            Dict with passed, score, issues, warnings
        """
        content = self._read_file_content(component_path)
        passed, score, issues, warnings = self.svelte_analyzer.analyze(content)
        return {
            "passed": passed,
            "score": score,
            "issues": issues,
            "warnings": warnings,
        }


def main() -> None:
    """CLI: run test_component on a path and print result."""
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m homeos.construction.tests.responsive_test <path>")
        sys.exit(1)
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)
    tester = ResponsiveDesignTest()
    result = tester.test_component(path)
    print("passed:", result["passed"])
    print("score:", result["score"])
    for i in result["issues"]:
        print("issue:", i)
    for w in result["warnings"]:
        print("warning:", w)
    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
