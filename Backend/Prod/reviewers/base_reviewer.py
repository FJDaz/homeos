"""Base interface for plan reviewers."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class BaseReviewer(ABC):
    """Base interface for plan reviewers."""
    
    @abstractmethod
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
        pass
