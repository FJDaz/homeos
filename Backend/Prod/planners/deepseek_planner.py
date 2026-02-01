"""DeepSeek planner for generating execution plans."""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

from ..models.deepseek_client import DeepSeekClient
from ..models.plan_reader import PlanReader


class DeepSeekPlanner:
    """Plan planner using DeepSeek (super economical)."""
    
    def __init__(self, deepseek_client: Optional[DeepSeekClient] = None):
        """
        Initialize DeepSeek planner.
        
        Args:
            deepseek_client: Optional DeepSeek client (creates new if None)
        """
        self.client = deepseek_client or DeepSeekClient()
        self.plan_reader = PlanReader()
    
    def _build_planning_prompt(
        self,
        description: str,
        context: Optional[str] = None
    ) -> str:
        """Build the planning prompt for DeepSeek."""
        
        system_prompt = """You are an expert software architect. Your task is to generate a detailed execution plan in JSON format.

The plan must follow this exact schema:
{
  "task_id": "uuid-v4",
  "description": "Clear description of the main task",
  "steps": [
    {
      "id": "step_1",
      "description": "Detailed description of what this step should accomplish",
      "type": "code_generation|refactoring|analysis",
      "complexity": 0.0-1.0,
      "estimated_tokens": 100-8000,
      "dependencies": [],
      "validation_criteria": ["criterion 1", "criterion 2"],
      "context": {
        "language": "python|javascript|typescript|etc",
        "framework": "fastapi|react|express|etc",
        "files": ["path/to/file1.py", "path/to/file2.js"]
      }
    }
  ],
  "metadata": {
    "created_at": "2025-01-25T10:00:00Z",
    "planner": "deepseek"
  }
}

Guidelines:
- Break down the task into atomic, sequential steps
- Each step should have a single, clear responsibility
- Use dependencies to express step ordering
- Estimate complexity realistically (0.0 = simple, 1.0 = very complex)
- Estimate tokens based on step complexity
- Include validation criteria for each step
- Return ONLY valid JSON, no markdown, no explanations"""

        user_prompt = f"""Generate an execution plan for the following task:

Task Description:
{description}
"""
        
        if context:
            user_prompt += f"""

Additional Context:
{context}
"""
        
        user_prompt += """

Generate the plan.json following the schema above. Return ONLY the JSON, no markdown formatting."""
        
        return system_prompt, user_prompt
    
    async def generate_plan(
        self,
        description: str,
        context: Optional[str] = None,
        output_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Generate a plan.json from a description.
        
        Args:
            description: Task description
            context: Additional context (framework, language, etc.)
            output_path: Optional path to save the plan
            
        Returns:
            Plan dictionary conforming to plan_schema.json
        """
        logger.info(f"DeepSeek Planner: Generating plan for '{description[:50]}...'")
        
        # Build prompt
        system_prompt, user_prompt = self._build_planning_prompt(description, context)
        
        # Combine system and user prompt for DeepSeek
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        # Generate with DeepSeek
        result = await self.client.generate(
            prompt=full_prompt,
            context=None,
            max_tokens=4096,
            temperature=0.7,
            output_constraint="JSON only"
        )
        
        if not result.success:
            raise ValueError(f"Failed to generate plan: {result.error}")
        
        # Parse JSON from response
        try:
            # Extract JSON from response (may have markdown code blocks)
            content = result.code.strip()
            if content.startswith("```json"):
                content = content[7:]  # Remove ```json
            if content.startswith("```"):
                content = content[3:]  # Remove ```
            if content.endswith("```"):
                content = content[:-3]  # Remove closing ```
            content = content.strip()
            
            plan = json.loads(content)
            
            # Validate plan by reading it (PlanReader validates schema)
            try:
                # Convert dict to JSON string for validation
                plan_json = json.dumps(plan)
                self.plan_reader.read_from_string(plan_json)
            except Exception as e:
                logger.warning(f"Plan validation warning: {e}, attempting to fix...")
                # Try to fix common issues
                if "task_id" not in plan:
                    plan["task_id"] = str(uuid.uuid4())
                if "metadata" not in plan:
                    plan["metadata"] = {}
                plan["metadata"]["created_at"] = datetime.utcnow().isoformat() + "Z"
                plan["metadata"]["planner"] = "deepseek"
            
            # Save if output path provided
            if output_path:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(plan, f, indent=2, ensure_ascii=False)
                logger.info(f"Plan saved to {output_path}")
            
            logger.info(
                f"Plan generated successfully: {len(plan.get('steps', []))} steps, "
                f"cost ${result.cost_usd:.4f}"
            )
            
            return plan
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse plan JSON: {e}")
            logger.error(f"Response content: {result.code[:500]}")
            raise ValueError(f"Invalid JSON in plan response: {e}")
    
    async def review_plan(
        self,
        plan: Dict[str, Any],
        issues: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Review and improve a plan.
        
        Args:
            plan: Existing plan dictionary
            issues: List of issues detected
            
        Returns:
            Improved plan dictionary
        """
        logger.info(f"DeepSeek Planner: Reviewing plan {plan.get('task_id', 'unknown')}")
        
        system_prompt = """You are an expert software architect reviewing an execution plan. Your task is to improve the plan by fixing issues and optimizing it.

Return the improved plan in the same JSON format."""
        
        user_prompt = f"""Review and improve the following execution plan:

Current Plan:
{json.dumps(plan, indent=2)}
"""
        
        if issues:
            user_prompt += f"""

Detected Issues:
{json.dumps(issues, indent=2)}
"""
        
        user_prompt += "\n\nReturn the improved plan as valid JSON only, no markdown."
        
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        result = await self.client.generate(
            prompt=full_prompt,
            context=None,
            max_tokens=4096,
            temperature=0.3,  # Lower temperature for review
            output_constraint="JSON only"
        )
        
        if not result.success:
            logger.warning(f"Plan review failed: {result.error}, returning original plan")
            return plan
        
        # Parse improved plan
        try:
            content = result.code.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            improved_plan = json.loads(content)
            
            logger.info(f"Plan reviewed successfully, cost ${result.cost_usd:.4f}")
            
            return improved_plan
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse reviewed plan: {e}, returning original")
            return plan
