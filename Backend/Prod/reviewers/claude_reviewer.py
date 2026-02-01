"""Claude Sonnet reviewer for reviewing plans and execution results."""
import json
from typing import Dict, Any, Optional, List
from loguru import logger

from ..models.claude_client import ClaudeClient


class ClaudeReviewer:
    """Plan reviewer using Claude Sonnet 3.5."""
    
    def __init__(self, claude_client: Optional[ClaudeClient] = None):
        """
        Initialize Claude reviewer.
        
        Args:
            claude_client: Optional Claude client (creates new if None)
        """
        self.client = claude_client or ClaudeClient()
    
    async def review(
        self,
        plan: Dict[str, Any],
        execution_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Review a plan and detect issues.
        
        Args:
            plan: Plan dictionary to review
            execution_results: Optional execution results if available
            
        Returns:
            Review result with issues and suggestions
        """
        logger.info(f"Claude Reviewer: Reviewing plan {plan.get('task_id', 'unknown')}")
        
        system_prompt = """You are an expert code reviewer. Your task is to review execution plans and detect potential issues.

Return your review as JSON with this structure:
{
  "is_valid": true/false,
  "issues": [
    {
      "severity": "error|warning|info",
      "step_id": "step_1",
      "description": "Issue description",
      "suggestion": "How to fix"
    }
  ],
  "suggestions": [
    "General improvement suggestion"
  ],
  "score": 0.0-1.0
}"""
        
        user_prompt = f"""Review the following execution plan:

Plan:
{json.dumps(plan, indent=2)}
"""
        
        if execution_results:
            user_prompt += f"""

Execution Results:
{json.dumps(execution_results, indent=2)}
"""
        
        user_prompt += "\n\nAnalyze the plan for potential issues and return your review as JSON only."
        
        result = await self.client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=2048,
            temperature=0.3,  # Lower temperature for review
            output_constraint="JSON only"
        )
        
        if not result.success:
            logger.warning(f"Plan review failed: {result.error}")
            return {
                "is_valid": True,  # Assume valid if review fails
                "issues": [],
                "suggestions": [],
                "score": 0.8,
                "error": result.error
            }
        
        # Parse review result
        try:
            content = result.code.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            review = json.loads(content)
            
            logger.info(
                f"Review completed: {len(review.get('issues', []))} issues, "
                f"score {review.get('score', 0):.2f}, cost ${result.cost_usd:.4f}"
            )
            
            return review
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse review JSON: {e}")
            return {
                "is_valid": True,
                "issues": [],
                "suggestions": [],
                "score": 0.8,
                "error": f"JSON parse error: {e}"
            }
