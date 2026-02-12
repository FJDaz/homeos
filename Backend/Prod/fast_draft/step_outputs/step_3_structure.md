I'll create a comprehensive test for race conditions in the orchestrator, focusing on sequential execution when multiple steps modify the same file.

python
import pytest
import asyncio
import tempfile
import shutil
import json
import logging
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import sys

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from Backend.Prod.orchestrator import Orchestrator
from Backend.Prod.core.plan import Plan, Step
from Backend.Prod.core.metrics import MetricsCollector


class TestSurgicalModeExecution:
    """Test surgical mode activation based on execution mode."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory with Python files."""
        temp_dir = tempfile.mkdtemp(prefix="aetherflow_test_")
        project_dir = Path(temp_dir) / "test_project"
        project_dir.mkdir(parents=True)
        
        # Create a simple Python file for testing
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
        
        # Create another Python file
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
    def test_plan(self, temp_project_dir):
        """Create a test plan that should trigger surgical mode."""
        plan = Plan(
            task_id="test_surgical_mode",
            description="Test surgical mode activation",
            steps=[
                Step(
                    id="step_1",
                    type="code_generation",
                    description="Add a new method to TestClass",
                    context={
                        "surgical_mode": True,  # Explicitly enable surgical mode
                        "existing_files": [
                            str(temp_project_dir / "test_module.py"),
                            str(temp_project_dir / "another_module.py")
                        ]
                    },
                    dependencies=[],
                    agent="test_agent"
                )
            ]
        )
        return plan
    
    @pytest.fixture
    def mock_agent_router(self):
        """Create a mock agent router."""
        router = Mock()
        router.execute_step = AsyncMock(return_value=Mock(
            success=True,
            output='''{
                "operations": [
                    {
                        "type": "add_method",
                        "target": "TestClass",
                        "position": "end",
                        "code": "def new_method(self):\\n    return \"new method added\""
                    }
                ]
            }'''
        ))
        return router
    
    @pytest.fixture
    def mock_surgical_editor(self):
        """Mock the SurgicalEditor to avoid actual file modifications."""
        with patch('Backend.Prod.orchestrator.SurgicalEditor') as mock_editor:
            # Mock the editor instance
            editor_instance = Mock()
            editor_instance.prepare.return_value = True
            editor_instance.get_ast_context.return_value = "AST context for test file"
            editor_instance.apply_instructions.return_value = (True, "modified code", "original code")
            
            # Mock the class methods
            mock_editor.return_value = editor_instance
            mock_editor.create_new_file.return_value = (True, "File created successfully")
            
            yield mock_editor
    
    @pytest.fixture
    def mock_surgical_parser(self):
        """Mock the SurgicalInstructionParser."""
        with patch('Backend.Prod.orchestrator.SurgicalInstructionParser') as mock_parser:
            mock_parser.is_surgical_output.return_value = True
            mock_parser.parse_instructions.return_value = ([Mock(code="def new_method(self):\n    return \"new method\"")], None)
            yield mock_parser
    
    def capture_logs(self, caplog, level=logging.INFO):
        """Helper to capture and filter logs."""
        caplog.set_level(level)
        return caplog
    
    @pytest.mark.asyncio
    async def test_surgical_mode_disabled_in_fast_mode(
        self, 
        temp_project_dir, 
        test_plan, 
        mock_agent_router,
        mock_surgical_editor,
        mock_surgical_parser,
        caplog
    ):
        """Test that surgical mode is DISABLED when execution_mode is FAST."""
        # Setup
        orchestrator = Orchestrator(
            project_root=temp_project_dir,
            execution_mode="FAST",
            agent_router=mock_agent_router
        )
        
        # Capture logs
        self.capture_logs(caplog)
        
        # Execute the plan
        results = await orchestrator.execute_plan(test_plan)
        
        # Verify surgical mode is disabled in logs
        surgical_mode_logs = [
            record for record in caplog.records 
            if "Surgical mode:" in record.message
        ]
        
        assert len(surgical_mode_logs) > 0, "No surgical mode logs found"
        
        # Check that surgical mode is False
        surgical_mode_enabled = any(
            "Surgical mode: False" in record.message 
            for record in surgical_mode_logs
        )
        
        assert surgical_mode_enabled, f"Surgical mode should be False in FAST mode. Logs: {[r.message for r in surgical_mode_logs]}"
        
        # Verify execution_mode is mentioned in logs
        fast_mode_log = next(
            (record for record in surgical_mode_logs if "execution_mode=FAST" in record.message),
            None
        )
        assert fast_mode_log is not None, "execution_mode=FAST should be in logs"
        
        # Verify that surgical edits were NOT applied
        # (agent_router.execute_step should have been called with surgical_mode=False)
        mock_agent_router.execute_step.assert_called_once()
        call_kwargs = mock_agent_router.execute_step.call_args[1]
        assert call_kwargs.get('surgical_mode') == False, "surgical_mode should be False when passed to agent_router"
        
        # Verify no AST parsing was attempted
        mock_surgical_editor.return_value.prepare.assert_not_called()
        
        print("✓ FAST mode: Surgical mode correctly disabled")
        print(f"  Log message: {surgical_mode_logs[0].message}")
    
    @pytest.mark.asyncio
    async def test_surgical_mode_enabled_in_build_mode(
        self, 
        temp_project_dir, 
        test_plan, 
        mock_agent_router,
        mock_surgical_editor,
        mock_surgical_parser,
        caplog
    ):
        """Test that surgical mode is ENABLED when execution_mode is BUILD."""
        # Setup
        orchestrator = Orchestrator(
            project_root=temp_project_dir,
            execution_mode="BUILD",
            agent_router=mock_agent_router
        )
        
        # Capture logs
        self.capture_logs(caplog)
        
        # Execute the plan
        results = await orchestrator.execute_plan(test_plan)
        
        # Verify surgical mode is enabled in logs
        surgical_mode_logs = [
            record for record in caplog.records 
            if "Surgical mode:" in record.message
        ]
        
        assert len(surgical_mode_logs) > 0, "No surgical mode logs found"
        
        # Check that surgical mode is True
        surgical_mode_enabled = any(
            "Surgical mode: True" in record.message 
            for record in surgical_mode_logs
        )
        
        assert surgical_mode_enabled, f"Surgical mode should be True in BUILD mode. Logs: {[r.message for r in surgical_mode_logs]}"
        
        # Verify execution_mode is mentioned in logs
        build_mode_log = next(
            (record for record in surgical_mode_logs if "execution_mode=BUILD" in record.message),
            None
        )
        assert build_mode_log is not None, "execution_mode=BUILD should be in logs"
        
        # Verify that surgical edits WERE attempted to be applied
        # (agent_router.execute_step should have been called with surgical_mode=True)
        mock_agent_router.execute_step.assert_called_once()
        call_kwargs = mock_agent_router.execute_step.call_args[1]
        assert call_kwargs.get('surgical_mode') == True, "surgical_mode should be True when passed to agent_router"
        
        # Verify AST parsing was attempted
        mock_surgical_editor.return_value.prepare.assert_called()
        mock_surgical_editor.return_value.get_ast_context.assert_called()
        
        print("✓ BUILD mode: Surgical mode correctly enabled")
        print(f"  Log message: {surgical_mode_logs[0].message}")
    
    @pytest.mark.asyncio
    async def test_surgical_mode_enabled_in_double_check_mode(
        self, 
        temp_project_dir, 
        test_plan, 
        mock_agent_router,
        mock_surgical_editor,
        mock_surgical_parser,
        caplog
    ):
        """Test that surgical mode is ENABLED when execution_mode is DOUBLE-CHECK."""
        # Setup
        orchestrator = Orchestrator(
            project_root=temp_project_dir,
            execution_mode="DOUBLE-CHECK",
            agent_router=mock_agent_router
        )
        
        # Capture logs
        self.capture_logs(caplog)
        
        # Execute the plan
        results = await orchestrator.execute_plan(test_plan)
        
        # Verify surgical mode is enabled in logs
        surgical_mode_logs = [
            record for record in caplog.records 
            if "Surgical mode:" in record.message
        ]
        
        assert len(surgical_mode_logs) > 0, "No surgical mode logs found"
        
        # Check that surgical mode is True
        surgical_mode_enabled = any(
            "Surgical mode: True" in record.message 
            for record in surgical_mode_logs
        )
        
        assert surgical_mode_enabled, f"Surgical mode should be True in DOUBLE-CHECK mode. Logs: {[r.message for r in surgical_mode_logs]}"
        
        # Verify execution_mode is mentioned in logs
        double_check_log = next(
            (record for record in surgical_mode_logs if "execution_mode=DOUBLE-CHECK" in record.message),
            None
        )
        assert double_check_log is not None, "execution_mode=DOUBLE-CHECK should be in logs"
        
        print("✓ DOUBLE-CHECK mode: Surgical mode correctly enabled")
        print(f"  Log message: {surgical_mode_logs[0].message}")
    
    @pytest.mark.asyncio
    async def test_same_plan_different_modes_comparison(
        self, 
        temp_project_dir, 
        test_plan, 
        mock_agent_router,
        mock_surgical_editor,
        mock_surgical_parser,
        caplog
    ):
        """Execute the same plan in FAST and BUILD modes and compare surgical mode status."""
        
        # Track surgical mode status for each execution
        surgical_mode_results = {}
        
        # Test FAST mode
        orchestrator_fast = Orchestrator(
            project_root=temp_project_dir,
            execution_mode="FAST",
            agent_router=mock_agent_router
        )
        
        self.capture_logs(caplog)
        await orchestrator_fast.execute_plan(test_plan)
        
        fast_logs = [
            record.message for record in caplog.records 
            if "Surgical mode:" in record.message
        ]
        surgical_mode_results["FAST"] = any("Surgical mode: True" in log for log in fast_logs)
        
        # Reset mocks
        mock_agent_router.reset_mock()
        mock_surgical_editor.reset_mock()
        
        # Test BUILD mode
        orchestrator_build = Orchestrator(
            project_root=temp_project_dir,
            execution_mode="BUILD",
            agent_router=mock_agent_router
        )
        
        self.capture_logs(caplog)
        await orchestrator_build.execute_plan(test_plan)
        
        build_logs = [
            record.message for record in caplog.records 
            if "Surgical mode:" in record.message
        ]
        surgical_mode_results["BUILD"] = any("Surgical mode: True" in log for log in build_logs)
        
        # Verify the difference
        assert surgical_mode_results["FAST"] == False, "Surgical mode should be False in FAST mode"
        assert surgical_mode_results["BUILD"] == True, "Surgical mode should be True in BUILD mode"
        
        print("✓ Comparison test passed:")
        print(f"  FAST mode: surgical_mode={surgical_mode_results['FAST']}")
        print(f"  BUILD mode: surgical_mode={surgical_mode_results['BUILD']}")
    
    @pytest.mark.asyncio
    async def test_surgical_mode_with_new_files_only(
        self, 
        temp_project_dir, 
        mock_agent_router,
        caplog
    ):
        """Test that surgical mode is disabled when only new files are involved."""
        # Create a plan with only new files (no existing content)
        new_file_path = temp_project_dir / "new_file.py"
        
        plan = Plan(
            task_id="test_new_files",
            description="Test with new files only",
            steps=[
                Step(
                    id="step_1",
                    type="code_generation",
                    description="Create a new file",
                    context={
                        "existing_files": [str(new_file_path)],  # File doesn't exist yet
                        "surgical_mode": True
                    },
                    dependencies=[],
                    agent="test_agent"
                )
            ]
        )
        
        # Test in BUILD mode (which normally enables surgical mode)
        orchestrator = Orchestrator(
            project_root=temp_project_dir,
            execution_mode="BUILD",
            agent_router=mock_agent_router
        )
        
        self.capture_logs(caplog)
        await orchestrator.execute_plan(plan)
        
        # Check logs for surgical mode status
        surgical_mode_logs = [
            record.message for record in caplog.records 
            if "Surgical mode:" in record.message
        ]
        
        # Surgical mode should be False because has_existing_code=False
        assert any("Surgical mode: False" in log for log in surgical_mode_logs), \
            f"Surgical mode should be False for new files. Logs: {surgical_mode_logs}"
        
        print("✓ New files test: Surgical mode correctly disabled for new files")
    
    @pytest.mark.asyncio
    async def test_surgical_mode_disabled_in_context(
        self, 
        temp_project_dir, 
        mock_agent_router,
        caplog
    ):
        """Test that surgical mode can be explicitly disabled in step context."""
        # Create a Python file
        python_file = temp_project_dir / "test_disable.py"
        python_file.write_text("class Test:\n    pass\n")
        
        # Create a plan with surgical_mode=False in context
        plan = Plan(
            task_id="test_disable_context",
            description="Test explicit surgical mode disable",
            steps=[
                Step(
                    id="step_1",
                    type="code_generation",
                    description="Test with surgical_mode=False",
                    context={
                        "existing_files": [str(python_file)],
                        "surgical_mode": False  # Explicitly disable
                    },
                    dependencies=[],
                    agent="test_agent"
                )
            ]
        )
        
        # Test in BUILD mode
        orchestrator = Orchestrator(
            project_root=temp_project_dir,
            execution_mode="BUILD",
            agent_router=mock_agent_router
        )
        
        self.capture_logs(caplog)
        await orchestrator.execute_plan(plan)
        
        # Check logs
        surgical_mode_logs = [
            record.message for record in caplog.records 
            if "Surgical mode:" in record.message
        ]
        
        # Should show context_surgical_mode=False
        context_disable_log = next(
            (log for log in surgical_mode_logs if "context_surgical_mode=False" in log),
            None
        )
        
        assert context_disable_log is not None, \
            f"Should show context_surgical_mode=False. Logs: {surgical_mode_logs}"
        
        # Surgical mode should be False
        assert any("Surgical mode: False" in log for log in surgical_mode_logs), \
            f"Surgical mode should be False when disabled in context. Logs: {surgical_mode_logs}"
        
        print("✓ Context disable test: Surgical mode correctly disabled via context")


def run_surgical_mode_tests():
    """Run the surgical mode tests and print results."""
    import sys
    import io
    
    # Capture output
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    try:
        # Create a test instance
        tester = TestSurgicalModeExecution()
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix="aetherflow_test_run_")
        project_dir = Path(temp_dir) / "test_project"
        project_dir.mkdir(parents=True)
        
        # Create test files
        python_file = project_dir / "test_file.py"
        python_file.write_text("class TestClass:\n    def method(self):\n        return 'test'")
        
        # Create test plan
        plan = Plan(
            task_id="manual_test",
            description="Manual surgical mode test",
            steps=[
                Step(
                    id="step_1",
                    type="code_generation",
                    description="Test step",
                    context={
                        "existing_files": [str(python_file)],
                        "surgical_mode": True
                    },
                    dependencies=[],
                    agent="test_agent"
                )
            ]
        )
        
        print("=" * 60)
        print("SURGICAL MODE TEST SUITE")
        print("=" * 60)
        
        # Test 1: FAST mode
        print("\n1. Testing FAST mode execution:")
        print("-" * 40)
        
        # Mock dependencies
        mock_router = Mock()
        mock_router.execute_step = AsyncMock(return_value=Mock(
            success