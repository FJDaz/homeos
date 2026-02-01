"""Plan reader and validator for AetherFlow."""
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, AsyncIterator
import jsonschema
from loguru import logger

from ..config.settings import settings


class PlanValidationError(Exception):
    """Raised when plan validation fails."""
    pass


class Step:
    """Represents a single execution step."""
    
    def __init__(self, step_data: Dict[str, Any]):
        self.id: str = step_data["id"]
        self.description: str = step_data["description"]
        self.type: str = step_data["type"]
        self.complexity: float = step_data["complexity"]
        self.estimated_tokens: int = step_data["estimated_tokens"]
        self.dependencies: List[str] = step_data.get("dependencies", [])
        self.validation_criteria: List[str] = step_data.get("validation_criteria", [])
        self.context: Optional[Dict[str, Any]] = step_data.get("context")
    
    def __repr__(self) -> str:
        return f"Step(id={self.id}, type={self.type}, complexity={self.complexity})"


class Plan:
    """Represents a complete execution plan."""
    
    def __init__(self, plan_data: Dict[str, Any]):
        self.task_id: str = plan_data["task_id"]
        self.description: str = plan_data["description"]
        self.steps: List[Step] = [Step(step_data) for step_data in plan_data["steps"]]
        self.metadata: Dict[str, Any] = plan_data.get("metadata", {})
        
        # Build dependency graph for validation
        self._validate_dependencies()
    
    def _validate_dependencies(self) -> None:
        """Validate that all dependencies reference existing steps."""
        step_ids = {step.id for step in self.steps}
        for step in self.steps:
            for dep in step.dependencies:
                if dep not in step_ids:
                    raise PlanValidationError(
                        f"Step {step.id} has dependency on non-existent step: {dep}"
                    )
    
    def get_step(self, step_id: str) -> Optional[Step]:
        """Get a step by its ID."""
        for step in self.steps:
            if step.id == step_id:
                return step
        return None
    
    def get_execution_order(self) -> List[List[Step]]:
        """
        Get steps in execution order respecting dependencies.
        Returns a list of lists, where each inner list contains steps
        that can be executed in parallel.
        
        This method uses topological sorting to maximize parallelism by
        grouping all steps without dependencies at each level.
        """
        # Build dependency graph
        step_map = {step.id: step for step in self.steps}
        in_degree = {step.id: len(step.dependencies) for step in self.steps}
        
        execution_order = []
        remaining_steps = set(step.id for step in self.steps)
        
        while remaining_steps:
            # Find steps with no remaining dependencies
            ready_steps = [
                step_map[sid] for sid in remaining_steps
                if in_degree[sid] == 0
            ]
            
            if not ready_steps:
                # Circular dependency detected
                raise PlanValidationError(
                    f"Circular dependency detected. Remaining steps: {remaining_steps}"
                )
            
            # Sort ready steps by priority (complexity, then estimated_tokens)
            # Lower complexity/tokens = higher priority (execute simpler tasks first)
            ready_steps.sort(key=lambda s: (s.complexity, s.estimated_tokens))
            
            execution_order.append(ready_steps)
            
            # Update in-degrees
            for step in ready_steps:
                remaining_steps.remove(step.id)
                # Decrease in-degree for steps that depend on this one
                for other_step in self.steps:
                    if step.id in other_step.dependencies:
                        in_degree[other_step.id] -= 1
        
        return execution_order
    
    def get_execution_order_with_partial_deps(self) -> List[List[Step]]:
        """
        Get execution order with partial dependency detection.
        
        This is an enhanced version that could detect partial dependencies
        (e.g., step A depends on B only for file X, not Y), allowing more parallelism.
        
        Currently returns the same as get_execution_order(), but can be extended
        to analyze step.context for file-level dependencies.
        
        Returns:
            List of batches of steps that can execute in parallel
        """
        # For now, use standard execution order
        # Future enhancement: analyze step.context.get("files") to detect
        # file-level dependencies and allow more parallelism
        return self.get_execution_order()
    
    def __repr__(self) -> str:
        return f"Plan(task_id={self.task_id}, steps={len(self.steps)})"


class PlanReader:
    """Reads and validates plan JSON files."""
    
    def __init__(self, schema_path: Optional[Path] = None):
        """
        Initialize PlanReader.
        
        Args:
            schema_path: Path to JSON schema file. If None, uses default schema.
        """
        if schema_path is None:
            # Use default schema from docs/references
            project_root = Path(__file__).parent.parent.parent.parent
            schema_path = project_root / "docs" / "references" / "plan_schema.json"
        
        self.schema_path = schema_path
        self._load_schema()
    
    def _load_schema(self) -> None:
        """Load JSON schema from file."""
        try:
            with open(self.schema_path, "r", encoding="utf-8") as f:
                self.schema = json.load(f)
        except FileNotFoundError:
            logger.warning(f"Schema file not found at {self.schema_path}, skipping validation")
            self.schema = None
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON schema: {e}")
            self.schema = None
    
    def read(self, plan_path: Path) -> Plan:
        """
        Read and validate a plan JSON file.
        
        Args:
            plan_path: Path to the plan JSON file
            
        Returns:
            Plan object
            
        Raises:
            PlanValidationError: If plan is invalid
            FileNotFoundError: If plan file doesn't exist
        """
        if not plan_path.exists():
            raise FileNotFoundError(f"Plan file not found: {plan_path}")
        
        logger.info(f"Reading plan from {plan_path}")
        
        try:
            with open(plan_path, "r", encoding="utf-8") as f:
                plan_data = json.load(f)
        except json.JSONDecodeError as e:
            raise PlanValidationError(f"Invalid JSON in plan file: {e}")
        
        # Validate against schema if available
        if self.schema:
            try:
                jsonschema.validate(instance=plan_data, schema=self.schema)
                logger.debug("Plan validated against schema successfully")
            except jsonschema.ValidationError as e:
                raise PlanValidationError(f"Plan validation failed: {e.message}")
        
        # Create Plan object (which also validates dependencies)
        try:
            plan = Plan(plan_data)
            logger.info(f"Plan loaded successfully: {plan.task_id} with {len(plan.steps)} steps")
            return plan
        except Exception as e:
            raise PlanValidationError(f"Error creating plan: {e}")
    
    def read_from_string(self, plan_json: str) -> Plan:
        """
        Read and validate a plan from a JSON string.
        
        Args:
            plan_json: JSON string containing the plan
            
        Returns:
            Plan object
        """
        try:
            plan_data = json.loads(plan_json)
        except json.JSONDecodeError as e:
            raise PlanValidationError(f"Invalid JSON string: {e}")
        
        # Validate against schema if available
        if self.schema:
            try:
                jsonschema.validate(instance=plan_data, schema=self.schema)
            except jsonschema.ValidationError as e:
                raise PlanValidationError(f"Plan validation failed: {e.message}")
        
        try:
            plan = Plan(plan_data)
            return plan
        except Exception as e:
            raise PlanValidationError(f"Error creating plan: {e}")
    
    async def read_streaming(
        self,
        plan_path: Path,
        max_wait_seconds: float = 30.0,
        check_interval: float = 0.5
    ) -> AsyncIterator[Step]:
        """
        Read plan steps as they become available (streaming mode).
        
        This method watches the plan file and yields steps as soon as they are
        complete in the JSON. Useful when Claude Code is writing the plan progressively.
        
        Args:
            plan_path: Path to plan JSON file
            max_wait_seconds: Maximum time to wait for file to be complete
            check_interval: How often to check for file updates (seconds)
            
        Yields:
            Step objects as they become available
            
        Raises:
            PlanValidationError: If plan is invalid
            FileNotFoundError: If plan file doesn't exist
        """
        if not plan_path.exists():
            raise FileNotFoundError(f"Plan file not found: {plan_path}")
        
        logger.info(f"Reading plan in streaming mode from {plan_path}")
        
        seen_step_ids = set()
        start_time = asyncio.get_event_loop().time()
        last_size = 0
        
        while True:
            # Check if file exists and has grown
            if not plan_path.exists():
                await asyncio.sleep(check_interval)
                continue
            
            current_size = plan_path.stat().st_size
            
            # Try to parse the file
            try:
                with open(plan_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                # Try to parse as JSON
                try:
                    plan_data = json.loads(content)
                except json.JSONDecodeError:
                    # File is incomplete, wait and retry
                    if (asyncio.get_event_loop().time() - start_time) > max_wait_seconds:
                        # Fallback to normal read
                        logger.warning("Streaming timeout, falling back to normal read")
                        plan = self.read(plan_path)
                        for step in plan.steps:
                            if step.id not in seen_step_ids:
                                yield step
                        return
                    await asyncio.sleep(check_interval)
                    continue
                
                # File is valid JSON, extract steps
                steps_data = plan_data.get("steps", [])
                
                for step_data in steps_data:
                    step_id = step_data.get("id")
                    if step_id and step_id not in seen_step_ids:
                        try:
                            # Validate step against schema if available
                            if self.schema and "items" in self.schema.get("properties", {}).get("steps", {}):
                                step_schema = self.schema["properties"]["steps"]["items"]
                                jsonschema.validate(instance=step_data, schema=step_schema)
                            
                            step = Step(step_data)
                            seen_step_ids.add(step_id)
                            logger.debug(f"Streaming step: {step_id}")
                            yield step
                        except Exception as e:
                            logger.warning(f"Failed to parse step {step_id}: {e}")
                            continue
                
                # Check if we have all steps (file is complete)
                if "steps" in plan_data and len(plan_data["steps"]) > 0:
                    # Check if file size hasn't changed (likely complete)
                    if current_size == last_size:
                        # Wait a bit more to be sure
                        await asyncio.sleep(check_interval)
                        if plan_path.stat().st_size == current_size:
                            logger.info("Plan file appears complete, finishing streaming")
                            break
                
                last_size = current_size
                
            except Exception as e:
                logger.warning(f"Error reading plan file: {e}")
                if (asyncio.get_event_loop().time() - start_time) > max_wait_seconds:
                    # Fallback to normal read
                    logger.warning("Streaming error, falling back to normal read")
                    plan = self.read(plan_path)
                    for step in plan.steps:
                        if step.id not in seen_step_ids:
                            yield step
                    return
                await asyncio.sleep(check_interval)
                continue
            
            await asyncio.sleep(check_interval)
        
        logger.info(f"Streaming complete: {len(seen_step_ids)} steps extracted")