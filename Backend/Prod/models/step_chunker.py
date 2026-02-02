"""Automatic step chunking for large steps.

Splits heavy steps into smaller sub-steps that can be executed independently
and then merged back together.
"""
import re
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from loguru import logger

from .plan_reader import Step


class ChunkType(Enum):
    """Types of chunks for different splitting strategies."""
    FILE_BASED = "file_based"           # Split by target files
    SECTION_BASED = "section_based"     # Split by code sections (imports, classes, etc.)
    LOGIC_BASED = "logic_based"         # Split by logical components
    ITERATIVE = "iterative"             # Iterative refinement chunks


@dataclass
class StepChunk:
    """A chunk of a larger step."""
    id: str
    parent_step_id: str
    description: str
    chunk_index: int
    total_chunks: int
    chunk_type: ChunkType
    dependencies: List[str] = field(default_factory=list)
    context_files: List[str] = field(default_factory=list)
    generated_files: List[str] = field(default_factory=list)
    merge_instructions: Optional[str] = None
    estimated_tokens: int = 0
    
    def to_step_dict(self) -> Dict[str, Any]:
        """Convert chunk to step dictionary format."""
        return {
            "id": self.id,
            "description": self.description,
            "type": "code_generation",
            "complexity": 0.5,
            "estimated_tokens": self.estimated_tokens,
            "dependencies": self.dependencies,
            "validation_criteria": [],
            "context": {
                "files": self.context_files,
                "chunk_info": {
                    "parent_step": self.parent_step_id,
                    "index": self.chunk_index,
                    "total": self.total_chunks,
                    "type": self.chunk_type.value
                }
            }
        }


@dataclass
class ChunkingStrategy:
    """Strategy for chunking a specific step."""
    strategy_type: ChunkType
    chunks: List[StepChunk]
    merge_plan: str
    parallelizable: bool


class StepChunker:
    """
    Automatic step chunking for large or complex steps.
    
    Detects steps that need chunking based on:
    - Estimated token count > threshold
    - Number of files > threshold
    - Step type and complexity
    
    Provides multiple chunking strategies:
    - File-based: Split by target files
    - Section-based: Split by code sections
    - Logic-based: Split by logical components
    """
    
    # Thresholds for chunking
    DEFAULT_CHUNK_SIZE = 20000  # Target tokens per chunk
    MAX_CHUNK_SIZE = 30000      # Maximum tokens per chunk
    MIN_CHUNK_SIZE = 5000       # Minimum tokens per chunk
    
    def __init__(self, default_chunk_size: int = 20000):
        """
        Initialize step chunker.
        
        Args:
            default_chunk_size: Target tokens per chunk
        """
        self.default_chunk_size = default_chunk_size
    
    def analyze_step(self, step: Step, estimated_tokens: int) -> Tuple[bool, Optional[str]]:
        """
        Analyze if a step should be chunked.
        
        Args:
            step: Step to analyze
            estimated_tokens: Estimated token count
            
        Returns:
            Tuple of (should_chunk, reason)
        """
        reasons = []
        
        # Check token count
        if estimated_tokens > self.MAX_CHUNK_SIZE:
            reasons.append(f"estimated_tokens ({estimated_tokens}) > {self.MAX_CHUNK_SIZE}")
        
        # Check number of files
        if step.context and isinstance(step.context, dict):
            files = step.context.get("files", [])
            input_files = step.context.get("input_files", [])
            total_files = len(files) + len(input_files)
            if total_files > 3:
                reasons.append(f"total_files ({total_files}) > 3")
        
        # Check description length and complexity
        desc_words = len(step.description.split())
        if step.type == "code_generation":
            # Estimate output lines from description
            estimated_lines = desc_words // 5
            if estimated_lines > 200:
                reasons.append(f"estimated_output_lines ({estimated_lines}) > 200")
        
        # Check for multiple distinct tasks in description
        task_indicators = [
            "create", "add", "implement", "modify", "update",
            "delete", "remove", "refactor", "extract"
        ]
        task_count = sum(
            1 for indicator in task_indicators
            if indicator in step.description.lower()
        )
        if task_count > 3:
            reasons.append(f"multiple_tasks ({task_count})")
        
        if reasons:
            return True, "; ".join(reasons)
        
        return False, None
    
    def chunk_step(
        self,
        step: Step,
        estimated_tokens: int,
        strategy: Optional[ChunkType] = None
    ) -> ChunkingStrategy:
        """
        Chunk a step into smaller sub-steps.
        
        Args:
            step: Step to chunk
            estimated_tokens: Estimated token count
            strategy: Specific strategy to use (auto-detect if None)
            
        Returns:
            ChunkingStrategy with chunks and merge plan
        """
        # Auto-detect strategy if not specified
        if strategy is None:
            strategy = self._detect_best_strategy(step, estimated_tokens)
        
        logger.info(f"Chunking step {step.id} using {strategy.value} strategy")
        
        # Execute chunking based on strategy
        if strategy == ChunkType.FILE_BASED:
            return self._chunk_by_files(step, estimated_tokens)
        elif strategy == ChunkType.SECTION_BASED:
            return self._chunk_by_sections(step, estimated_tokens)
        elif strategy == ChunkType.LOGIC_BASED:
            return self._chunk_by_logic(step, estimated_tokens)
        else:
            return self._chunk_iterative(step, estimated_tokens)
    
    def _detect_best_strategy(
        self,
        step: Step,
        estimated_tokens: int
    ) -> ChunkType:
        """Detect the best chunking strategy for a step."""
        if step.context and isinstance(step.context, dict):
            files = step.context.get("files", [])
            
            # If multiple distinct files, use file-based
            if len(files) > 1:
                return ChunkType.FILE_BASED
            
            # If single large file with multiple sections
            if len(files) == 1:
                return ChunkType.SECTION_BASED
        
        # For complex code generation, use logic-based
        if step.type == "code_generation" and step.complexity > 0.6:
            return ChunkType.LOGIC_BASED
        
        # Default to iterative for unknown cases
        return ChunkType.ITERATIVE
    
    def _chunk_by_files(
        self,
        step: Step,
        estimated_tokens: int
    ) -> ChunkingStrategy:
        """Chunk step by target files."""
        files = []
        if step.context and isinstance(step.context, dict):
            files = step.context.get("files", [])
        
        if not files:
            # Fall back to logic-based if no files
            return self._chunk_by_logic(step, estimated_tokens)
        
        chunks = []
        num_chunks = len(files)
        
        for idx, file_path in enumerate(files):
            chunk_id = f"{step.id}_chunk_{idx + 1}"
            
            # Build description for this file
            description = self._extract_file_specific_description(
                step.description, file_path
            ) or f"{step.description} (File: {file_path})"
            
            chunk = StepChunk(
                id=chunk_id,
                parent_step_id=step.id,
                description=description,
                chunk_index=idx,
                total_chunks=num_chunks,
                chunk_type=ChunkType.FILE_BASED,
                dependencies=[f"{step.id}_chunk_{i}" for i in range(idx)] if idx > 0 else step.dependencies,
                context_files=[file_path],
                generated_files=[file_path],
                estimated_tokens=estimated_tokens // num_chunks,
                merge_instructions=f"File {file_path} generated in chunk {idx + 1}/{num_chunks}"
            )
            chunks.append(chunk)
        
        return ChunkingStrategy(
            strategy_type=ChunkType.FILE_BASED,
            chunks=chunks,
            merge_plan="Files are generated independently. No merging needed.",
            parallelizable=False  # Files may depend on each other
        )
    
    def _chunk_by_sections(
        self,
        step: Step,
        estimated_tokens: int
    ) -> ChunkingStrategy:
        """Chunk step by code sections."""
        # Parse description to find sections
        sections = self._parse_sections_from_description(step.description)
        
        if len(sections) < 2:
            # Fall back to logic-based if no clear sections
            return self._chunk_by_logic(step, estimated_tokens)
        
        chunks = []
        num_chunks = len(sections)
        
        for idx, section in enumerate(sections):
            chunk_id = f"{step.id}_chunk_{idx + 1}"
            
            chunk = StepChunk(
                id=chunk_id,
                parent_step_id=step.id,
                description=section["description"],
                chunk_index=idx,
                total_chunks=num_chunks,
                chunk_type=ChunkType.SECTION_BASED,
                dependencies=[f"{step.id}_chunk_{i}" for i in range(idx)] if idx > 0 else step.dependencies,
                context_files=step.context.get("files", []) if step.context else [],
                generated_files=[f"{step.context.get('files', ['output'])[0]}_section_{idx}"] if step.context else [],
                estimated_tokens=estimated_tokens // num_chunks,
                merge_instructions=section.get("merge_instruction", "")
            )
            chunks.append(chunk)
        
        return ChunkingStrategy(
            strategy_type=ChunkType.SECTION_BASED,
            chunks=chunks,
            merge_plan="Sections merged in order: " + ", ".join(s["name"] for s in sections),
            parallelizable=False  # Sections build on each other
        )
    
    def _chunk_by_logic(
        self,
        step: Step,
        estimated_tokens: int
    ) -> ChunkingStrategy:
        """Chunk step by logical components."""
        # Extract logical components from description
        components = self._extract_components(step.description)
        
        if len(components) < 2:
            # Fall back to iterative if no clear components
            return self._chunk_iterative(step, estimated_tokens)
        
        chunks = []
        num_chunks = len(components)
        
        for idx, component in enumerate(components):
            chunk_id = f"{step.id}_chunk_{idx + 1}"
            
            chunk = StepChunk(
                id=chunk_id,
                parent_step_id=step.id,
                description=component["description"],
                chunk_index=idx,
                total_chunks=num_chunks,
                chunk_type=ChunkType.LOGIC_BASED,
                dependencies=[f"{step.id}_chunk_{i}" for i in range(idx)] if idx > 0 else step.dependencies,
                context_files=step.context.get("files", []) if step.context else [],
                generated_files=component.get("outputs", []),
                estimated_tokens=estimated_tokens // num_chunks,
                merge_instructions=component.get("merge_instruction", "")
            )
            chunks.append(chunk)
        
        return ChunkingStrategy(
            strategy_type=ChunkType.LOGIC_BASED,
            chunks=chunks,
            merge_plan="Components merged: " + ", ".join(c["name"] for c in components),
            parallelizable=all(c.get("independent", False) for c in components)
        )
    
    def _chunk_iterative(
        self,
        step: Step,
        estimated_tokens: int
    ) -> ChunkingStrategy:
        """Create iterative chunks for refinement."""
        # Calculate number of chunks needed
        num_chunks = max(2, (estimated_tokens + self.default_chunk_size - 1) // self.default_chunk_size)
        
        chunks = []
        
        for idx in range(num_chunks):
            chunk_id = f"{step.id}_chunk_{idx + 1}"
            
            if idx == 0:
                # First chunk: generate skeleton
                description = f"{step.description}\n\nPART {idx + 1}/{num_chunks}: Generate the skeleton/structure and first part."
            elif idx == num_chunks - 1:
                # Last chunk: finalize
                description = f"{step.description}\n\nPART {idx + 1}/{num_chunks}: Generate the final part and ensure integration with previous parts."
            else:
                # Middle chunks: extend
                description = f"{step.description}\n\nPART {idx + 1}/{num_chunks}: Continue from previous part and extend implementation."
            
            chunk = StepChunk(
                id=chunk_id,
                parent_step_id=step.id,
                description=description,
                chunk_index=idx,
                total_chunks=num_chunks,
                chunk_type=ChunkType.ITERATIVE,
                dependencies=[f"{step.id}_chunk_{idx}"] if idx > 0 else step.dependencies,
                context_files=step.context.get("files", []) if step.context else [],
                estimated_tokens=self.default_chunk_size,
                merge_instructions=f"Part {idx + 1} of {num_chunks}"
            )
            chunks.append(chunk)
        
        return ChunkingStrategy(
            strategy_type=ChunkType.ITERATIVE,
            chunks=chunks,
            merge_plan="Iterative refinement: each part builds on previous",
            parallelizable=False
        )
    
    def merge_chunk_results(
        self,
        strategy: ChunkingStrategy,
        results: List[str]
    ) -> str:
        """
        Merge results from multiple chunks.
        
        Args:
            strategy: Chunking strategy used
            results: List of chunk results
            
        Returns:
            Merged result
        """
        if not results:
            return ""
        
        if len(results) == 1:
            return results[0]
        
        if strategy.strategy_type == ChunkType.FILE_BASED:
            # Files are independent, concatenate with headers
            merged = []
            for chunk, result in zip(strategy.chunks, results):
                merged.append(f"=== {chunk.generated_files[0] if chunk.generated_files else 'File'} ===\n{result}")
            return "\n\n".join(merged)
        
        elif strategy.strategy_type == ChunkType.SECTION_BASED:
            # Sections build on each other, concatenate
            return "\n\n".join(results)
        
        elif strategy.strategy_type == ChunkType.LOGIC_BASED:
            # Components may be independent or dependent
            if strategy.parallelizable:
                # Independent components, combine
                return "\n\n".join(results)
            else:
                # Dependent components, last result contains full implementation
                return results[-1]
        
        else:  # ITERATIVE
            # Iterative: last result should contain full implementation
            return results[-1]
    
    def _extract_file_specific_description(
        self,
        description: str,
        file_path: str
    ) -> Optional[str]:
        """Extract description specific to a file from general description."""
        file_name = file_path.split("/")[-1]
        
        # Look for file-specific instructions in description
        patterns = [
            rf"{re.escape(file_name)}[^.]*:([^.]*)\.?",
            rf"{re.escape(file_path)}[^.]*:([^.]*)\.?",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _parse_sections_from_description(
        self,
        description: str
    ) -> List[Dict[str, str]]:
        """Parse code sections from step description."""
        sections = []
        
        # Look for numbered or bulleted sections
        # Pattern: (1) Section name: description
        numbered_pattern = r'\(\d+\)\s*([^:]+):\s*([^.]+)\.?'
        numbered_matches = re.findall(numbered_pattern, description)
        
        for name, desc in numbered_matches:
            sections.append({
                "name": name.strip(),
                "description": f"Create {name.strip()}: {desc.strip()}",
                "merge_instruction": f"Add {name.strip()} section"
            })
        
        # If no numbered sections, look for bullet points
        if not sections:
            bullet_pattern = r'[-*]\s*([^:]+):\s*([^.]+)\.?'
            bullet_matches = re.findall(bullet_pattern, description)
            
            for name, desc in bullet_matches[:4]:  # Limit to 4 sections
                sections.append({
                    "name": name.strip(),
                    "description": f"Implement {name.strip()}: {desc.strip()}",
                    "merge_instruction": f"Add {name.strip()}"
                })
        
        return sections
    
    def _extract_components(self, description: str) -> List[Dict[str, Any]]:
        """Extract logical components from description."""
        components = []
        
        # Common component keywords in code generation
        component_keywords = [
            ("class", r'class\s+(\w+)'),
            ("function", r'(?:def|function)\s+(\w+)'),
            ("method", r'method\s+(\w+)'),
            ("route", r'route\s+(\S+)'),
            ("component", r'component\s+(\w+)'),
            ("module", r'module\s+(\w+)'),
        ]
        
        for comp_type, pattern in component_keywords:
            matches = re.findall(pattern, description, re.IGNORECASE)
            for match in matches[:3]:  # Limit per type
                components.append({
                    "name": match,
                    "type": comp_type,
                    "description": f"Create {comp_type} '{match}' as described in requirements.",
                    "outputs": [f"{match}.{comp_type}"],
                    "independent": comp_type in ["class", "function", "module"],
                    "merge_instruction": f"Integrate {comp_type} '{match}'"
                })
        
        return components
    
    def estimate_chunk_count(
        self,
        estimated_tokens: int,
        strategy: ChunkType = ChunkType.ITERATIVE
    ) -> int:
        """Estimate number of chunks needed."""
        if strategy == ChunkType.FILE_BASED:
            # Depends on number of files, assume 2-4
            return min(4, max(2, estimated_tokens // self.default_chunk_size))
        
        return max(2, (estimated_tokens + self.default_chunk_size - 1) // self.default_chunk_size)
