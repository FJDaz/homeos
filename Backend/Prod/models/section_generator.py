"""Section-based incremental code generation.

Generates large files section by section instead of all at once.
Accumulates output progressively to handle files that would exceed token limits.
"""
import re
from typing import List, Dict, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from loguru import logger

try:
    from .plan_reader import Step
except ImportError:
    # Fallback if Step not available
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from .plan_reader import Step


class SectionType(Enum):
    """Types of code sections."""
    IMPORTS = "imports"
    CONSTANTS = "constants"
    TYPES = "types"              # Type definitions, enums
    UTILITIES = "utilities"      # Helper functions
    CLASSES = "classes"          # Class definitions
    FUNCTIONS = "functions"      # Standalone functions
    MAIN = "main"                # Main execution block
    EXPORTS = "exports"          # Module exports


@dataclass
class CodeSection:
    """A section of code to generate."""
    section_type: SectionType
    name: str
    description: str
    dependencies: List[SectionType] = field(default_factory=list)
    estimated_lines: int = 50
    generated_code: str = ""
    is_complete: bool = False


@dataclass
class GenerationPlan:
    """Plan for section-based generation."""
    sections: List[CodeSection]
    language: str
    file_path: Optional[str]
    total_estimated_lines: int
    requires_integration: bool


@dataclass
class SectionResult:
    """Result of generating a section."""
    section: CodeSection
    success: bool
    code: str
    tokens_used: int
    error: Optional[str] = None


class SectionGenerator:
    """
    Generates code incrementally by sections.
    
    Instead of generating an entire file at once (which can hit token limits),
    this generator:
    1. Analyzes the requirements and creates a section plan
    2. Generates each section independently with context from previous sections
    3. Accumulates the output progressively
    4. Optionally performs integration pass at the end
    
    Usage:
        generator = SectionGenerator()
        plan = generator.create_plan(step_description, language="python")
        
        accumulated_code = ""
        for section in plan.sections:
            result = await generator.generate_section(
                section, accumulated_code, client
            )
            if result.success:
                accumulated_code += result.code
    """
    
    # Section order for different file types
    SECTION_ORDERS = {
        "python": [
            SectionType.IMPORTS,
            SectionType.CONSTANTS,
            SectionType.TYPES,
            SectionType.UTILITIES,
            SectionType.CLASSES,
            SectionType.FUNCTIONS,
            SectionType.MAIN,
        ],
        "javascript": [
            SectionType.IMPORTS,
            SectionType.CONSTANTS,
            SectionType.TYPES,
            SectionType.UTILITIES,
            SectionType.CLASSES,
            SectionType.FUNCTIONS,
            SectionType.EXPORTS,
        ],
        "typescript": [
            SectionType.IMPORTS,
            SectionType.TYPES,
            SectionType.CONSTANTS,
            SectionType.UTILITIES,
            SectionType.CLASSES,
            SectionType.FUNCTIONS,
            SectionType.EXPORTS,
        ],
        "java": [
            SectionType.IMPORTS,
            SectionType.CONSTANTS,
            SectionType.TYPES,
            SectionType.CLASSES,
            SectionType.UTILITIES,
            SectionType.MAIN,
        ],
        "html": [
            SectionType.IMPORTS,      # Head, meta tags
            SectionType.TYPES,        # Component definitions
            SectionType.CLASSES,      # HTML structure
            SectionType.FUNCTIONS,    # Scripts
            SectionType.MAIN,         # Body content
        ],
    }
    
    # Section templates for prompts
    SECTION_TEMPLATES = {
        SectionType.IMPORTS: "Generate the imports and dependencies section.",
        SectionType.CONSTANTS: "Generate constants and configuration definitions.",
        SectionType.TYPES: "Generate type definitions, interfaces, and enums.",
        SectionType.UTILITIES: "Generate utility and helper functions.",
        SectionType.CLASSES: "Generate class definitions with methods.",
        SectionType.FUNCTIONS: "Generate standalone functions.",
        SectionType.MAIN: "Generate the main execution block or entry point.",
        SectionType.EXPORTS: "Generate module exports and public API.",
    }
    
    def __init__(self, max_section_lines: int = 100):
        """
        Initialize section generator.
        
        Args:
            max_section_lines: Maximum lines per section
        """
        self.max_section_lines = max_section_lines
    
    def create_plan(
        self,
        description: str,
        language: str = "python",
        file_path: Optional[str] = None,
        existing_code: Optional[str] = None
    ) -> GenerationPlan:
        """
        Create a generation plan from description.
        
        Args:
            description: Step description or requirements
            language: Programming language
            file_path: Target file path (optional)
            existing_code: Existing code to extend (optional)
            
        Returns:
            GenerationPlan with sections
        """
        language = language.lower()
        section_order = self.SECTION_ORDERS.get(language, self.SECTION_ORDERS["python"])
        
        # Analyze description to determine needed sections
        needed_sections = self._analyze_description(description, section_order)
        
        # Create sections with descriptions
        sections = []
        total_lines = 0
        
        for section_type in needed_sections:
            section_desc = self._create_section_description(
                section_type, description, language
            )
            estimated_lines = self._estimate_section_lines(
                section_type, description
            )
            
            # Find dependencies (sections that must come before)
            dependencies = self._get_section_dependencies(section_type, needed_sections)
            
            section = CodeSection(
                section_type=section_type,
                name=section_type.value,
                description=section_desc,
                dependencies=dependencies,
                estimated_lines=estimated_lines
            )
            sections.append(section)
            total_lines += estimated_lines
        
        return GenerationPlan(
            sections=sections,
            language=language,
            file_path=file_path,
            total_estimated_lines=total_lines,
            requires_integration=len(sections) > 2
        )
    
    async def generate_section(
        self,
        section: CodeSection,
        accumulated_code: str,
        generate_fn: Callable[[str], Any],
        context: Optional[str] = None
    ) -> SectionResult:
        """
        Generate a single section.
        
        Args:
            section: Section to generate
            accumulated_code: Code generated so far (for context)
            generate_fn: Async function that takes prompt and returns result
            context: Additional context
            
        Returns:
            SectionResult with generated code
        """
        # Build section-specific prompt
        prompt = self._build_section_prompt(section, accumulated_code, context)
        
        logger.info(
            f"Generating section: {section.section_type.value} "
            f"(~{section.estimated_lines} lines)"
        )
        
        try:
            # Generate section
            result = await generate_fn(prompt)
            
            # Extract code from result
            code = self._extract_code(result, section.section_type)
            
            # Validate section
            is_valid, error = self._validate_section(code, section)
            
            if is_valid:
                section.generated_code = code
                section.is_complete = True
                
                tokens_used = getattr(result, 'tokens_used', 0) or len(code) // 4
                
                return SectionResult(
                    section=section,
                    success=True,
                    code=code,
                    tokens_used=tokens_used
                )
            else:
                return SectionResult(
                    section=section,
                    success=False,
                    code="",
                    tokens_used=0,
                    error=error
                )
                
        except Exception as e:
            logger.error(f"Failed to generate section {section.section_type.value}: {e}")
            return SectionResult(
                section=section,
                success=False,
                code="",
                tokens_used=0,
                error=str(e)
            )
    
    async def generate_all_sections(
        self,
        plan: GenerationPlan,
        generate_fn: Callable[[str], Any],
        context: Optional[str] = None,
        on_progress: Optional[Callable[[int, int, str], None]] = None
    ) -> Tuple[str, List[SectionResult]]:
        """
        Generate all sections in plan.
        
        Args:
            plan: GenerationPlan with sections
            generate_fn: Async function to generate code
            context: Additional context
            on_progress: Callback(progress, total, current_section)
            
        Returns:
            Tuple of (final_code, section_results)
        """
        accumulated_code = ""
        results = []
        
        total_sections = len(plan.sections)
        
        for idx, section in enumerate(plan.sections):
            if on_progress:
                on_progress(idx + 1, total_sections, section.section_type.value)
            
            result = await self.generate_section(
                section, accumulated_code, generate_fn, context
            )
            results.append(result)
            
            if result.success:
                accumulated_code = self._merge_sections(
                    accumulated_code, result.code, section.section_type, plan.language
                )
            else:
                logger.warning(
                    f"Section {section.section_type.value} failed: {result.error}"
                )
        
        # Integration pass if needed
        if plan.requires_integration and len(results) > 1:
            accumulated_code = await self._integration_pass(
                accumulated_code, plan, generate_fn
            )
        
        return accumulated_code, results
    
    def _analyze_description(
        self,
        description: str,
        available_sections: List[SectionType]
    ) -> List[SectionType]:
        """Analyze description to determine which sections are needed."""
        needed = []
        desc_lower = description.lower()
        
        # Check for imports
        import_indicators = ["import", "require", "from", "module", "package"]
        if any(ind in desc_lower for ind in import_indicators):
            if SectionType.IMPORTS in available_sections:
                needed.append(SectionType.IMPORTS)
        
        # Check for constants
        const_indicators = ["constant", "config", "setting", "default value"]
        if any(ind in desc_lower for ind in const_indicators):
            if SectionType.CONSTANTS in available_sections:
                needed.append(SectionType.CONSTANTS)
        
        # Check for types
        type_indicators = ["type", "interface", "enum", "struct", "class definition"]
        if any(ind in desc_lower for ind in type_indicators):
            if SectionType.TYPES in available_sections:
                needed.append(SectionType.TYPES)
        
        # Check for utilities/helpers
        util_indicators = ["helper", "utility", "function", "tool"]
        if any(ind in desc_lower for ind in util_indicators):
            if SectionType.UTILITIES in available_sections:
                needed.append(SectionType.UTILITIES)
        
        # Check for classes
        class_indicators = ["class", "object", "component"]
        if any(ind in desc_lower for ind in class_indicators):
            if SectionType.CLASSES in available_sections:
                needed.append(SectionType.CLASSES)
        
        # Check for functions
        func_indicators = ["def ", "function", "method", "procedure"]
        if any(ind in desc_lower for ind in func_indicators):
            if SectionType.FUNCTIONS in available_sections:
                needed.append(SectionType.FUNCTIONS)
        
        # Check for main/entry
        main_indicators = ["main", "entry point", "execute", "run"]
        if any(ind in desc_lower for ind in main_indicators):
            if SectionType.MAIN in available_sections:
                needed.append(SectionType.MAIN)
        
        # Check for exports
        export_indicators = ["export", "module.exports", "public api"]
        if any(ind in desc_lower for ind in export_indicators):
            if SectionType.EXPORTS in available_sections:
                needed.append(SectionType.EXPORTS)
        
        # Ensure at least imports and main/default
        if not needed:
            needed = [SectionType.IMPORTS, SectionType.FUNCTIONS]
        elif SectionType.IMPORTS not in needed:
            needed.insert(0, SectionType.IMPORTS)
        
        return needed
    
    def _create_section_description(
        self,
        section_type: SectionType,
        full_description: str,
        language: str
    ) -> str:
        """Create description for a specific section."""
        base_template = self.SECTION_TEMPLATES.get(
            section_type,
            f"Generate the {section_type.value} section."
        )
        
        return f"{base_template}\n\nIn the context of: {full_description[:200]}..."
    
    def _estimate_section_lines(
        self,
        section_type: SectionType,
        description: str
    ) -> int:
        """Estimate lines needed for a section."""
        base_lines = {
            SectionType.IMPORTS: 10,
            SectionType.CONSTANTS: 15,
            SectionType.TYPES: 30,
            SectionType.UTILITIES: 40,
            SectionType.CLASSES: 80,
            SectionType.FUNCTIONS: 50,
            SectionType.MAIN: 20,
            SectionType.EXPORTS: 10,
        }
        
        # Adjust based on description complexity
        words = len(description.split())
        complexity_factor = min(2.0, 1.0 + (words / 100))
        
        return min(
            int(base_lines.get(section_type, 50) * complexity_factor),
            self.max_section_lines
        )
    
    def _get_section_dependencies(
        self,
        section_type: SectionType,
        all_sections: List[SectionType]
    ) -> List[SectionType]:
        """Get dependencies for a section."""
        dependencies = {
            SectionType.CONSTANTS: [SectionType.IMPORTS],
            SectionType.TYPES: [SectionType.IMPORTS, SectionType.CONSTANTS],
            SectionType.UTILITIES: [SectionType.IMPORTS, SectionType.TYPES],
            SectionType.CLASSES: [SectionType.IMPORTS, SectionType.TYPES, SectionType.UTILITIES],
            SectionType.FUNCTIONS: [SectionType.IMPORTS, SectionType.TYPES, SectionType.UTILITIES],
            SectionType.MAIN: [SectionType.IMPORTS, SectionType.CLASSES, SectionType.FUNCTIONS],
            SectionType.EXPORTS: [SectionType.CLASSES, SectionType.FUNCTIONS],
        }
        
        deps = dependencies.get(section_type, [])
        # Filter to only include dependencies that are in the plan
        return [d for d in deps if d in all_sections]
    
    def _build_section_prompt(
        self,
        section: CodeSection,
        accumulated_code: str,
        context: Optional[str] = None
    ) -> str:
        """Build prompt for generating a section."""
        parts = []
        
        # Base section instruction
        parts.append(f"Generate ONLY the {section.section_type.value.upper()} section.")
        parts.append(section.description)
        
        # Add accumulated code as context
        if accumulated_code:
            parts.append("\nPreviously generated code (for context, do not repeat):")
            parts.append("```")
            # Limit context to last 1000 chars to avoid token explosion
            context_code = accumulated_code[-1000:] if len(accumulated_code) > 1000 else accumulated_code
            parts.append(context_code)
            parts.append("```")
        
        # Add dependencies information
        if section.dependencies:
            dep_names = [d.value for d in section.dependencies]
            parts.append(f"\nThis section depends on: {', '.join(dep_names)}")
        
        # Add additional context
        if context:
            parts.append(f"\nAdditional context: {context}")
        
        # Add output constraint
        parts.append(f"\nGenerate approximately {section.estimated_lines} lines.")
        parts.append("Output ONLY the code for this section, no explanations.")
        parts.append("Do not include code from previous sections.")
        
        return "\n".join(parts)
    
    def _extract_code(
        self,
        result: Any,
        section_type: SectionType
    ) -> str:
        """Extract code from generation result."""
        # Handle different result types
        if isinstance(result, str):
            code = result
        elif hasattr(result, 'code'):
            code = result.code
        elif hasattr(result, 'output'):
            code = result.output
        else:
            code = str(result)
        
        # Clean up code
        code = code.strip()
        
        # Remove markdown code blocks if present
        if code.startswith("```"):
            lines = code.split("\n")
            # Remove first line (```language)
            if lines[0].startswith("```"):
                lines = lines[1:]
            # Remove last line (```)
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            code = "\n".join(lines)
        
        return code.strip()
    
    def _validate_section(
        self,
        code: str,
        section: CodeSection
    ) -> Tuple[bool, Optional[str]]:
        """Validate generated section."""
        if not code:
            return False, "Empty code generated"
        
        lines = code.split("\n")
        
        # Check for reasonable line count
        if len(lines) > section.estimated_lines * 3:
            return False, f"Section too long: {len(lines)} lines (expected ~{section.estimated_lines})"
        
        # Check for basic syntax based on section type
        if section.section_type == SectionType.IMPORTS:
            # Should contain import statements
            if not any(line.strip().startswith(("import", "from", "require")) for line in lines):
                return False, "No import statements found"
        
        elif section.section_type == SectionType.CLASSES:
            # Should contain class definition
            if "class " not in code:
                return False, "No class definition found"
        
        return True, None
    
    def _merge_sections(
        self,
        accumulated: str,
        new_section: str,
        section_type: SectionType,
        language: str
    ) -> str:
        """Merge a new section into accumulated code."""
        # Add separator for readability
        separator = "\n\n"
        
        if not accumulated:
            return new_section
        
        # For some languages, specific ordering matters
        if section_type == SectionType.IMPORTS:
            # Imports always go at the top
            return new_section + separator + accumulated
        
        # Default: append
        return accumulated + separator + new_section
    
    async def _integration_pass(
        self,
        code: str,
        plan: GenerationPlan,
        generate_fn: Callable[[str], Any]
    ) -> str:
        """Perform integration pass to clean up and optimize."""
        prompt = f"""Review and optimize the following {plan.language} code.
        
        Tasks:
        1. Remove any duplicate imports
        2. Ensure consistent formatting
        3. Check for missing dependencies between sections
        4. Optimize imports (remove unused, sort)
        
        Code:
        ```{plan.language}
        {code}
        ```
        
        Output the complete optimized code.
        """
        
        try:
            result = await generate_fn(prompt)
            optimized = self._extract_code(result, SectionType.UTILITIES)
            return optimized or code
        except Exception as e:
            logger.warning(f"Integration pass failed: {e}")
            return code


def should_use_section_generation(
    step: Step,
    estimated_tokens: int,
    threshold: int = 25000
) -> bool:
    """
    Determine if section-based generation should be used.
    
    Args:
        step: Step to evaluate
        estimated_tokens: Estimated token count
        threshold: Token threshold for using sections
        
    Returns:
        True if section generation should be used
    """
    if estimated_tokens < threshold:
        return False
    
    # Only use for code generation
    if step.type != "code_generation":
        return False
    
    # Check if it's a multi-component task
    if step.complexity > 0.7:
        return True
    
    # Check for multiple classes/functions
    desc_lower = step.description.lower()
    class_count = desc_lower.count("class ")
    func_count = desc_lower.count("def ") + desc_lower.count("function")
    
    if class_count > 1 or func_count > 3:
        return True
    
    return False
