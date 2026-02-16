I'll create a comprehensive test suite for race condition prevention in the orchestrator, following TDD principles and the refactoring guidelines. Let me structure this properly:

python
"""
Test suite for surgical mode execution in Orchestrator.
Tests that surgical mode is correctly enabled/disabled based on execution mode.
"""

import pytest
import asyncio
import tempfile
import shutil
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import sys

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from Backend.Prod.core.orchestrator import Orchestrator
from Backend.Prod.core.models import Plan, Step, StepResult
from Backend.Prod.core.agent_router import AgentRouter
from Backend.Prod.core.metrics import MetricsCollector


# ============================================================================
# MODELS
# ============================================================================

class TestPlanFactory:
    """Factory for creating test plans with different configurations."""
    
    @staticmethod
    def create_surgical_mode_test_plan(
        project_dir: Path,
        step_id: str = "step_1",
        step_type: str = "code_generation",
        surgical_mode_in_context: Optional[bool] = True,
        existing_files: Optional[List[str]] = None
    ) -> Plan:
        """
        Create a test plan for surgical mode testing.
        
        Args:
            project_dir: Project directory path
            step_id: Step identifier
            step_type: Type of step (code_generation, refactoring, etc.)
            surgical_mode_in_context: Whether to enable surgical mode in context
            existing_files: List of existing files to include in context
            
        Returns:
            Plan object configured for testing
        """
        if existing_files is None:
            existing_files = [
                str(project_dir / "test_module.py"),
                str(project_dir / "another_module.py")
            ]
        
        context = {"existing_files": existing_files}
        if surgical_mode_in_context is not None:
            context["surgical_mode"] = surgical_mode_in_context
        
        return Plan(
            task_id="test_surgical_mode",
            name="Surgical Mode Test",
            description="Test surgical mode activation based on execution mode",
            steps=[
                Step(
                    id=step_id,
                    name=f"Test {step_type} step",
                    description=f"Test {step_type} with surgical mode",
                    type=step_type,
                    context=context,
                    input_files={},
                    output_files=existing_files,
                    dependencies=[],
                    agent_preference=None
                )
            ]
        )
    
    @staticmethod
    def create_multi_step_plan(
        project_dir: Path,
        num_steps: int = 3,
        step_type: str = "code_generation",
        surgical_mode_in_context: Optional[bool] = True
    ) -> Plan:
        """
        Create a multi-step test plan.
        
        Args:
            project_dir: Project directory path
            num_steps: Number of steps to create
            step_type: Type of steps
            surgical_mode_in_context: Whether to enable surgical mode in context
            
        Returns:
            Plan with multiple steps
        """
        steps = []
        for i in range(num_steps):
            context = {
                "existing_files": [str(project_dir / f"test_module_{i}.py")],
                "surgical_mode": surgical_mode_in_context
            }
            
            steps.append(
                Step(
                    id=f"step_{i+1}",
                    name=f"Step {i+1}",
                    description=f"Test step {i+1}",
                    type=step_type,
                    context=context,
                    input_files={},
                    output_files=[str(project_dir / f"test_module_{i}.py")],
                    dependencies=[] if i == 0 else [f"step_{i}"],
                    agent_preference=None
                )
            )
        
        return Plan(
            task_id="multi_step_test",
            name="Multi-Step Test",
            description="Test multiple steps with surgical mode",
            steps=steps
        )


# ============================================================================
# SERVICES
# ============================================================================

class MockAgentRouterService:
    """Service for creating mock agent routers with different behaviors."""
    
    @staticmethod
    def create_successful_router() -> Mock:
        """
        Create a mock agent router that always succeeds.
        
        Returns:
            Mock AgentRouter configured for success
        """
        router = Mock(spec=AgentRouter)
        router.execute_step = AsyncMock(return_value=Mock(
            success=True,
            output=json.dumps({
                "operations": [{
                    "type": "add_method",
                    "target": "TestClass",
                    "position": "end",
                    "code": "def new_method(self):\n    return \"new method added\""
                }]
            }),
            execution_time=0.1,
            token_usage={"input": 100, "output": 50}
        ))
        return router
    
    @staticmethod
    def create_failing_router(step_id_to_fail: str = "step_2") -> Mock:
        """
        Create a mock agent router that fails for specific steps.
        
        Args:
            step_id_to_fail: Step ID that should fail
            
        Returns:
            Mock AgentRouter configured to fail for specific steps
        """
        router = Mock(spec=AgentRouter)
        
        async def execute_step(step, context, surgical_mode=False, loaded_files=None):
            if step.id == step_id_to_fail:
                return StepResult(
                    step_id=step.id,
                    success=False,
                    output="Simulated failure",
                    execution_time=0.1,
                    token_usage={"input": 100, "output": 0}
                )
            
            return StepResult(
                step_id=step.id,
                success=True,
                output=json.dumps({
                    "operations": [{
                        "type": "add_method",
                        "target": "TestClass",
                        "position": "end",
                        "code": f"def method_{step.id}(self):\n    return \"{step.id}\""
                    }]
                }),
                execution_time=0.1,
                token_usage={"input": 100, "output": 50}
            )
        
        router.execute_step = execute_step
        return router
    
    @staticmethod
    def create_tracking_router() -> Mock:
        """
        Create a mock agent router that tracks execution.
        
        Returns:
            Mock AgentRouter that tracks execution order and parameters
        """
        router = Mock(spec=AgentRouter)
        router.execution_order = []
        router.surgical_mode_calls = []
        
        async def execute_step(step, context, surgical_mode=False, loaded_files=None):
            router.execution_order.append(step.id)
            router.surgical_mode_calls.append(surgical_mode)
            
            await asyncio.sleep(0.01)  # Simulate processing
            
            return StepResult(
                step_id=step.id,
                success=True,
                output=json.dumps({
                    "operations": [{
                        "type": "add_method",
                        "target": "TestClass",
                        "position": "end",
                        "code": f"def method_{step.id}(self):\n    return \"{step.id}\""
                    }]
                }),
                execution_time=0.1,
                token_usage={"input": 100, "output": 50}
            )
        
        router.execute_step = execute_step
        return router


class MockSurgicalEditorService:
    """Service for mocking surgical editor components."""
    
    @staticmethod
    def create_mock_editor() -> Mock:
        """
        Create a mock SurgicalEditor.
        
        Returns:
            Mock SurgicalEditor
        """
        with patch('Backend.Prod.core.orchestrator.SurgicalEditor') as mock_editor_class:
            editor_instance = Mock()
            editor_instance.prepare.return_value = True
            editor_instance.get_ast_context.return_value = "AST context for test file"
            editor_instance.apply_instructions.return_value = (True, "modified code", "original code")
            
            mock_editor_class.return_value = editor_instance
            mock_editor_class.create_new_file.return_value = (True, "File created successfully")
            
            return mock_editor_class
    
    @staticmethod
    def create_mock_parser() -> Mock:
        """
        Create a mock SurgicalInstructionParser.
        
        Returns:
            Mock SurgicalInstructionParser
        """
        with patch('Backend.Prod.core.orchestrator.SurgicalInstructionParser') as mock_parser_class:
            mock_parser_class.is_surgical_output.return_value = True
            mock_parser_class.parse_instructions.return_value = (
                [Mock(code="def new_method(self):\n    return \"new method\"")],
                None
            )
            return mock_parser_class


class LogCaptureService:
    """Service for capturing and analyzing logs."""
    
    @staticmethod
    def capture_logs(caplog, level: int = logging.INFO) -> List[logging.LogRecord]:
        """
        Capture logs at specified level.
        
        Args:
            caplog: pytest caplog fixture
            level: Logging level
            
        Returns:
            List of log records
        """
        caplog.set_level(level)
        return caplog.records
    
    @staticmethod
    def filter_logs_by_message(records: List[logging.LogRecord], keyword: str) -> List[logging.LogRecord]:
        """
        Filter logs by message keyword.
        
        Args:
            records: List of log records
            keyword: Keyword to search for
            
        Returns:
            Filtered log records
        """
        return [record for record in records if keyword in record.message]
    
    @staticmethod
    def extract_surgical_mode_status(records: List[logging.LogRecord]) -> Dict[str, Any]:
        """
        Extract surgical mode status from logs.
        
        Args:
            records: List of log records
            
        Returns:
            Dictionary with surgical mode information
        """
        surgical_logs = LogCaptureService.filter_logs_by_message(records, "Surgical mode:")
        
        if not surgical_logs:
            return {"found": False, "status": None, "details": {}}
        
        # Parse the log message
        log_message = surgical_logs[0].message
        status = "True" in log_message
        
        # Extract details
        details = {}
        if "execution_mode=" in log_message:
            start = log_message.find("execution_mode=") + len("execution_mode=")
            end = log_message.find(",", start)
            details["execution_mode"] = log_message[start:end] if end != -1 else log_message[start:]
        
        if "step_type=" in log_message:
            start = log_message.find("step_type=") + len("step_type=")
            end = log_message.find(",", start)
            details["step_type"] = log_message[start:end] if end != -1 else log_message[start:]
        
        if "has_python_files=" in log_message:
            start = log_message.find("has_python_files=") + len("has_python_files=")
            end = log_message.find(")", start)
            details["has_python_files"] = log_message[start:end] if end != -1 else log_message[start:]
        
        return {
            "found": True,
            "status": status,
            "details": details,
            "raw_message": log_message
        }


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory with Python files."""
    temp_dir = tempfile.mkdtemp(prefix="aetherflow_test_")
    project_dir = Path(temp_dir) / "test_project"
    project_dir.mkdir(parents=True)
    
    # Create Python files for testing
    python_file = project_dir / "test_module.py"
    python_file.write_text("""
import os
from typing import Optional

class TestClass:
    def existing_method(self) -> str:
        return "existing"
        
def existing_function() -> int:
    return 42
""")
    
    another_file = project_dir / "another_module.py"
    another_file.write_text("""
from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_endpoint():
    return {"status": "ok"}
""")
    
    yield project_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_plan_factory():
    """Provide test plan factory."""
    return TestPlanFactory


@pytest.fixture
def mock_services():
    """Provide mock services."""
    return {
        "agent_router": MockAgentRouterService,
        "surgical_editor": MockSurgicalEditorService,
        "log_capture": LogCaptureService
    }


# ============================================================================
# TEST CLASSES
# ============================================================================

class TestSurgicalModeActivation:
    """Test surgical mode activation based on execution mode."""
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("execution_mode,expected_surgical_mode", [
        ("FAST", False),
        ("BUILD", True),
        ("DOUBLE-CHECK", True),
    ])
    async def test_surgical_mode_by_execution_mode(
        self,
        temp_project_dir,
        test_plan_factory,
        mock_services,
        execution_mode,
        expected_surgical_mode,
        caplog
    ):
        """
        Test that surgical mode is correctly enabled/disabled based on execution mode.
        
        Args:
            execution_mode: Execution mode to test
            expected_surgical_mode: Expected surgical mode status
        """
        # Setup
        plan = test_plan_factory.create_surgical_mode_test_plan(temp_project_dir)
        mock_router = mock_services["agent_router"].create_successful_router()
        
        with mock_services["surgical_editor"].create_mock_editor() as mock_editor, \
             mock_services["surgical_editor"].create_mock_parser() as mock_parser:
            
            orchestrator = Orchestrator(
                project_root=temp_project_dir,
                execution_mode=execution_mode,
                agent_router=mock_router
            )
            
            # Execute plan
            results = await orchestrator.execute_plan(plan)
            
            # Verify results
            assert results["step_1"].success
            
            # Analyze logs
            records = mock_services["log_capture"].capture_logs(caplog)
            surgical_info = mock_services["log_capture"].extract_surgical_mode_status(records)
            
            assert surgical_info["found"], "No surgical mode log found"
            assert surgical_info["status"] == expected_surgical_mode, \
                f"Surgical mode should be {expected_surgical_mode} in {execution_mode} mode"
            
            # Verify execution mode in logs
            assert surgical_info["details"].get("execution_mode") == execution_mode, \
                f"execution_mode={execution_mode} should be in logs"
            
            # Verify agent router call
            mock_router.execute_step.assert_called_once()
            call_kwargs = mock_router.execute_step.call_args[1]
            assert call_kwargs.get('surgical_mode') == expected_surgical_mode, \
                f"surgical_mode should be {expected_surgical_mode} when passed to agent_router"
            
            # Verify AST parsing based on surgical mode
            if expected_surgical_mode:
                mock_editor.return_value.prepare.assert_called()
                mock_editor.return_value.get_ast_context.assert_called()
            else:
                mock_editor.return_value.prepare.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_same_plan_different_modes_comparison(
        self,
        temp_project_dir,
        test_plan_factory,
        mock_services,
        caplog
    ):
        """Execute the same plan in FAST and BUILD modes and compare surgical mode status."""
        # Create plan
        plan = test_plan_factory.create_surgical_mode_test_plan(temp_project_dir)
        
        # Track results
        surgical_mode_results = {}
        
        # Test FAST mode
        mock_router_fast = mock_services["agent_router"].create_successful_router()
        
        with mock_services["surgical_editor"].create_mock_editor() as mock_editor_fast:
            orchestrator_fast = Orchestrator(
                project_root=temp_project_dir,
                execution_mode="FAST",
                agent_router=mock_router_fast
            )
            
            records = mock_services["log_capture"].capture_logs(caplog)
            await orchestrator_fast.execute_plan(plan)
            
            surgical_info_fast = mock_services["log_capture"].extract_surgical_mode_status(records)
            surgical_mode_results["FAST"] = surgical_info_fast.get("status", None)
        
        # Test BUILD mode
        mock_router_build = mock_services["agent_router"].create_successful_router()
        
        with mock_services["surgical_editor"].create_mock_editor() as mock_editor_build:
            orchestrator_build = Orchestrator(
                project_root=temp_project_dir,
                execution_mode="BUILD",
                agent_router=mock_router_build
            )
            
            records = mock_services["log_capture"].capture_logs(caplog)
            await orchestrator_build.execute_plan(plan)
            
            surgical_info_build = mock_services["log_capture"].extract_surgical_mode_status(records)
            surgical_mode_results["BUILD"] = surgical_info_build.get("status", None)
        
        # Verify the difference
        assert surgical_mode_results["FAST"] == False, "Surgical mode should be False in FAST mode"
        assert surgical_mode_results["BUILD"] == True, "Surgical mode should be True in BUILD mode"
        
        print(f"\nComparison test results:")
        print(f"  FAST mode: surgical_mode={surgical_mode_results['FAST']}")
        print(f"  BUILD mode: surgical_mode={surgical_mode_results['BUILD']}")


class TestSurgicalModeEdgeCases:
    """Test edge cases for surgical mode activation."""
    
    @pytest.mark.asyncio
    async def test_surgical_mode_with_new_files_only(
        self,
        temp_project_dir,
        test_plan_factory,
        mock_services,
        caplog
    ):
        """Test that surgical mode is disabled when only new files are involved."""
        # Create a plan with only new files
        new_file_path = temp_project_dir / "new_file.py"
        plan = test_plan_factory.create_surgical_mode_test_plan(
            temp_project_dir,
            existing_files=[str(new_file_path)]
        )
        
        mock_router = mock_services["agent_router"].create_successful