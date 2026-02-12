"""
Test suite for race condition prevention in Orchestrator.
Tests that steps modifying the same file execute sequentially and maintain file integrity.
"""

import json
import asyncio
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import pytest
from unittest.mock import Mock, AsyncMock, patch

# Models
from ..core.models import Plan, Step, StepResult
from ..core.orchestrator import Orchestrator
from ..core.agent_router import AgentRouter
from ..core.metrics import MetricsCollector


# ============================================================================
# MODELS
# ============================================================================

class TestFile:
    """Represents a test file for race condition testing."""
    
    def __init__(self, content: str = "", suffix: str = ".py"):
        """Initialize a test file.
        
        Args:
            content: Initial file content
            suffix: File extension
        """
        self.content = content
        self.suffix = suffix
        self.path: Optional[Path] = None
        self._temp_file = None
    
    def __enter__(self) -> 'TestFile':
        """Context manager entry."""
        self._temp_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix=self.suffix, 
            delete=False,
            encoding='utf-8'
        )
        self._temp_file.write(self.content)
        self._temp_file.close()
        self.path = Path(self._temp_file.name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup."""
        if self.path and self.path.exists():
            self.path.unlink()
    
    def read(self) -> str:
        """Read file content."""
        if self.path:
            return self.path.read_text(encoding='utf-8')
        return ""
    
    def write(self, content: str):
        """Write content to file."""
        if self.path:
            self.path.write_text(content, encoding='utf-8')


class ExecutionTracker:
    """Tracks execution order and concurrency for testing."""
    
    def __init__(self):
        """Initialize execution tracker."""
        self.execution_order: List[str] = []
        self.active_steps: Set[str] = set()
        self.max_concurrent: int = 0
        self.execution_intervals: Dict[str, Tuple[float, float]] = {}
    
    def start_step(self, step_id: str) -> None:
        """Record step start.
        
        Args:
            step_id: Step identifier
        """
        self.execution_order.append(step_id)
        self.active_steps.add(step_id)
        self.max_concurrent = max(self.max_concurrent, len(self.active_steps))
        self.execution_intervals[step_id] = (time.time(), 0)
    
    def end_step(self, step_id: str) -> None:
        """Record step end.
        
        Args:
            step_id: Step identifier
        """
        self.active_steps.discard(step_id)
        start_time, _ = self.execution_intervals[step_id]
        self.execution_intervals[step_id] = (start_time, time.time())


# ============================================================================
# SERVICES
# ============================================================================

class MockAgentRouterService:
    """Service for mocking AgentRouter behavior in tests."""
    
    def __init__(self):
        """Initialize mock service."""
        self.execution_order: List[str] = []
        self.file_modifications: Dict[str, List[str]] = {}
        self.should_fail_steps: Set[str] = set()
        self.execution_delay: float = 0.1
    
    def create_mock_router(self, mocker) -> Mock:
        """Create a mock AgentRouter.
        
        Args:
            mocker: Pytest mocker fixture
            
        Returns:
            Mock AgentRouter instance
        """
        router = mocker.MagicMock(spec=AgentRouter)
        
        async def mock_execute_step(
            step: Step, 
            context: str, 
            surgical_mode: bool = False, 
            loaded_files: Optional[Dict] = None
        ) -> StepResult:
            """Mock step execution with tracking."""
            
            # Simulate processing delay
            await asyncio.sleep(self.execution_delay)
            
            # Track execution order
            self.execution_order.append(step.id)
            
            # Track file modifications
            if loaded_files:
                for file_path in loaded_files:
                    if file_path not in self.file_modifications:
                        self.file_modifications[file_path] = []
                    self.file_modifications[file_path].append(step.id)
            
            # Check if step should fail
            if step.id in self.should_fail_steps:
                return StepResult(
                    step_id=step.id,
                    success=False,
                    output="Simulated failure",
                    execution_time=self.execution_delay,
                    token_usage={"input": 100, "output": 0}
                )
            
            # Generate surgical instructions based on step
            output = self._generate_surgical_output(step)
            
            return StepResult(
                step_id=step.id,
                success=True,
                output=output,
                execution_time=self.execution_delay,
                token_usage={"input": 100, "output": 50}
            )
        
        router.execute_step = mock_execute_step
        return router
    
    def _generate_surgical_output(self, step: Step) -> str:
        """Generate surgical JSON output for a step.
        
        Args:
            step: Step to generate output for
            
        Returns:
            JSON string with surgical operations
        """
        if step.id.startswith("step_"):
            step_num = step.id.split("_")[1]
            return json.dumps({
                "operations": [{
                    "type": "add_method",
                    "target": "TestClass",
                    "position": "end",
                    "code": f"    def method_{step_num}(self):\n        return 'added by {step.id}'"
                }]
            })
        elif step.id.startswith("step"):
            # Handle stepA, stepB, stepC format
            step_letter = step.id.replace("step", "")
            return json.dumps({
                "operations": [{
                    "type": "add_method",
                    "target": "TestClass",
                    "position": "end",
                    "code": f"    def method_{step_letter.lower()}(self):\n        return 'added by {step.id}'"
                }]
            })
        return "{}"
    
    def reset(self) -> None:
        """Reset tracking data."""
        self.execution_order.clear()
        self.file_modifications.clear()
        self.should_fail_steps.clear()


class PlanGeneratorService:
    """Service for generating test plans."""
    
    @staticmethod
    def create_race_condition_plan(
        test_file_path: Path,
        num_steps: int = 3,
        step_prefix: str = "step_"
    ) -> Plan:
        """Create a plan with multiple steps modifying the same file.
        
        Args:
            test_file_path: Path to the file all steps will modify
            num_steps: Number of steps in the plan
            step_prefix: Prefix for step IDs
            
        Returns:
            Plan with steps targeting the same file
        """
        steps = []
        for i in range(1, num_steps + 1):
            step_id = f"{step_prefix}{i}"
            steps.append(
                Step(
                    id=step_id,
                    name=f"Add method {i}",
                    description=f"Add method_{i} to TestClass",
                    type="code_generation",
                    context={"surgical_mode": True},
                    input_files={},
                    output_files=[str(test_file_path)],
                    dependencies=[],  # No explicit dependencies
                    agent_preference=None
                )
            )
        
        return Plan(
            task_id="race_condition_test",
            name="Race Condition Test",
            description="Test sequential execution when multiple steps modify the same file",
            steps=steps
        )
    
    @staticmethod
    def create_dependent_steps_plan(
        test_file_path: Path,
        step_ids: List[str] = None
    ) -> Plan:
        """Create a plan with explicit step dependencies.
        
        Args:
            test_file_path: Path to the file all steps will modify
            step_ids: List of step IDs (default: ["step_a", "step_b", "step_c"])
            
        Returns:
            Plan with dependent steps
        """
        if step_ids is None:
            step_ids = ["step_a", "step_b", "step_c"]
        
        steps = []
        for i, step_id in enumerate(step_ids):
            dependencies = []
            if i > 0:
                dependencies.append(step_ids[i - 1])
            
            steps.append(
                Step(
                    id=step_id,
                    name=f"Step {step_id}",
                    description=f"Step {step_id} with dependencies {dependencies}",
                    type="code_generation",
                    context={"surgical_mode": True},
                    input_files={},
                    output_files=[str(test_file_path)],
                    dependencies=dependencies,
                    agent_preference=None
                )
            )
        
        return Plan(
            task_id="dependent_steps_test",
            name="Dependent Steps Test",
            description="Test execution with explicit dependencies",
            steps=steps
        )
    
    @staticmethod
    def plan_to_json(plan: Plan) -> Dict:
        """Convert plan to JSON-serializable dictionary.
        
        Args:
            plan: Plan to convert
            
        Returns:
            Dictionary representation of the plan
        """
        return {
            "task_id": plan.task_id,
            "name": plan.name,
            "description": plan.description,
            "steps": [
                {
                    "id": step.id,
                    "name": step.name,
                    "description": step.description,
                    "type": step.type,
                    "context": step.context,
                    "input_files": step.input_files,
                    "output_files": step.output_files,
                    "dependencies": step.dependencies,
                    "agent_preference": step.agent_preference
                }
                for step in plan.steps
            ]
        }


class FileIntegrityValidator:
    """Service for validating file integrity during tests."""
    
    @staticmethod
    def validate_file_content(
        file_path: Path,
        expected_methods: List[str],
        original_methods: List[str] = None
    ) -> Tuple[bool, List[str]]:
        """Validate file content after execution.
        
        Args:
            file_path: Path to the file to validate
            expected_methods: List of method names that should be present
            original_methods: List of original method names that should be preserved
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        if not file_path.exists():
            errors.append(f"File does not exist: {file_path}")
            return False, errors
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            errors.append(f"Failed to read file: {e}")
            return False, errors
        
        # Check expected methods
        for method in expected_methods:
            if f"def {method}(" not in content:
                errors.append(f"Expected method '{method}' not found in file")
        
        # Check original methods (if provided)
        if original_methods:
            for method in original_methods:
                if f"def {method}(" not in content:
                    errors.append(f"Original method '{method}' was lost")
        
        # Check for duplicates
        for method in expected_methods:
            count = content.count(f"def {method}(")
            if count > 1:
                errors.append(f"Method '{method}' appears {count} times (should be 1)")
        
        # Check Python syntax
        try:
            import ast
            ast.parse(content)
        except SyntaxError as e:
            errors.append(f"File contains invalid Python syntax: {e}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_no_overlapping_execution(
        execution_intervals: Dict[str, Tuple[float, float]]
    ) -> Tuple[bool, List[str]]:
        """Validate that execution intervals don't overlap.
        
        Args:
            execution_intervals: Dictionary mapping step_id to (start_time, end_time)
            
        Returns:
            Tuple of (no_overlap, error_messages)
        """
        errors = []
        intervals = list(execution_intervals.values())
        
        for i in range(len(intervals)):
            for j in range(i + 1, len(intervals)):
                start_i, end_i = intervals[i]
                start_j, end_j = intervals[j]
                
                # Check for overlap
                if not (end_i <= start_j or end_j <= start_i):
                    errors.append(
                        f"Overlap detected between intervals {i} and {j}: "
                        f"{start_i}-{end_i} overlaps with {start_j}-{end_j}"
                    )
        
        return len(errors) == 0, errors


# ============================================================================
# TEST CONTROLLERS
# ============================================================================

class RaceConditionTestController:
    """Controller for race condition tests."""
    
    def __init__(self):
        """Initialize test controller."""
        self.mock_service = MockAgentRouterService()
        self.plan_generator = PlanGeneratorService()
        self.validator = FileIntegrityValidator()
    
    async def run_sequential_execution_test(
        self,
        orchestrator: Orchestrator,
        test_file: TestFile,
        num_steps: int = 3
    ) -> Tuple[bool, Dict]:
        """Run sequential execution test.
        
        Args:
            orchestrator: Orchestrator instance
            test_file: Test file to modify
            num_steps: Number of steps to execute
            
        Returns:
            Tuple of (test_passed, results_dict)
        """
        # Create plan
        plan = self.plan_generator.create_race_condition_plan(
            test_file.path,
            num_steps=num_steps
        )
        
        # Execute plan
        results = await orchestrator.execute_plan(plan)
        
        # Verify results
        all_succeeded = all(result.success for result in results.values())
        
        # Verify execution order
        execution_order_correct = (
            self.mock_service.execution_order == [f"step_{i}" for i in range(1, num_steps + 1)]
        )
        
        # Verify file modifications
        file_was_modified = str(test_file.path) in self.mock_service.file_modifications
        if file_was_modified:
            modification_order = self.mock_service.file_modifications[str(test_file.path)]
            modification_order_correct = modification_order == [f"step_{i}" for i in range(1, num_steps + 1)]
        else:
            modification_order_correct = False
        
        # Verify file content
        expected_methods = [f"method_{i}" for i in range(1, num_steps + 1)]
        original_methods = ["get_value", "increment", "helper_function"]
        
        file_valid, file_errors = self.validator.validate_file_content(
            test_file.path,
            expected_methods,
            original_methods
        )
        
        test_passed = (
            all_succeeded and
            execution_order_correct and
            file_was_modified and
            modification_order_correct and
            file_valid
        )
        
        return test_passed, {
            "all_succeeded": all_succeeded,
            "execution_order": self.mock_service.execution_order.copy(),
            "execution_order_correct": execution_order_correct,
            "file_was_modified": file_was_modified,
            "modification_order": self.mock_service.file_modifications.get(str(test_file.path), []),
            "modification_order_correct": modification_order_correct,
            "file_valid": file_valid,
            "file_errors": file_errors,
            "results": {k: v.success for k, v in results.items()}
        }
    
    async def run_error_recovery_test(
        self,
        orchestrator: Orchestrator,
        test_file: TestFile,
        failing_step: str = "step_2"
    ) -> Tuple[bool, Dict]:
        """Run error recovery test.
        
        Args:
            orchestrator: Orchestrator instance
            test_file: Test file to modify
            failing_step: Step ID that should fail
            
        Returns:
            Tuple of (test_passed, results_dict)
        """
        # Configure mock to fail specific step
        self.mock_service.should_fail_steps.add(failing_step)
        
        # Create plan
        plan = self.plan_generator.create_race_condition_plan(
            test_file.path,
            num_steps=3
        )
        
        # Execute plan
        results = await orchestrator.execute_plan(plan)
        
        # Verify step_2 failed
        step_2_failed = not results["step_2"].success
        step_1_succeeded = results["step_1"].success
        
        # Verify file contains only successful modifications
        content = test_file.read()
        has_step_1_method = "def method_1(" in content
        has_step_2_method = "def method_2(" in content
        has_step_3_method = "def method_3(" in content
        
        # File should still be valid Python
        import ast
        try:
            ast.parse(content)
            syntax_valid = True
        except SyntaxError:
            syntax_valid = False
        
        test_passed = (
            step_2_failed and
            step_1_succeeded and
            has_step_1_method and
            not has_step_2_method and
            syntax_valid
        )
        
        return test_passed, {
            "step_2_failed": step_2_failed,
            "step_1_succeeded": step_1_succeeded,
            "has_step_1_method": has_step_1_method,
            "has_step_2_method": has_step_2_method,
            "has_step_3_method": has_step_3_method,
            "syntax_valid": syntax_valid,
            "results": {k: v.success for k, v in results.items()}
        }


# ============================================================================
# TEST SUITES
# ============================================================================

class TestRaceConditionPrevention:
    """Test suite for race condition prevention in Orchestrator."""
    
    @pytest.fixture
    def temp_test_file(self):
        """Create a temporary Python file for testing."""
        with TestFile("""# Test file for race condition testing
import time

class TestClass:
    def __init__(self):
        self.value = 0
    
    def get_value(self):
        return self.value
    
    def increment(self):
        self.value += 1
        return self.value

def helper_function():
    return

I'll create a comprehensive test suite for surgical mode execution based on the requirements. Let me refactor the draft code following TDD principles and SOLID design.