"""Base interface for plan planners."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path


class BasePlanner(ABC):
    """Base interface for plan planners."""
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
