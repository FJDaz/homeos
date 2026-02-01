"""Planner manager for selecting and managing multiple planners."""
from typing import Dict, Any, Optional
from pathlib import Path
from loguru import logger

from .claude_planner import ClaudePlanner
from .gemini_planner import GeminiPlanner
from .deepseek_planner import DeepSeekPlanner
from .fallback_manager import FallbackManager
from ..config.settings import settings


class PlannerManager:
    """Manages multiple planners with fallback support."""
    
    def __init__(self, planner_mode: str = "auto"):
        """
        Initialize planner manager.
        
        Args:
            planner_mode: Planner mode:
                - "claude_code" : Use Claude Code (Cursor) - current
                - "claude_api" : Use Claude Sonnet API
                - "gemini" : Use Gemini
                - "deepseek" : Use DeepSeek (super eco)
                - "auto" : Automatic selection based on available API keys
        """
        self.planner_mode = planner_mode.lower()
        self.fallback_manager = FallbackManager(
            enable_fallback=settings.enable_planner_fallback
        )
        
        # Initialize planners (lazy loading)
        self._planners: Dict[str, Any] = {}
        self._initialize_planners()
    
    def _initialize_planners(self) -> None:
        """Initialize available planners."""
        available = self.fallback_manager.check_api_keys_available()
        
        # Claude API planner
        if available.get("claude_api"):
            try:
                self._planners["claude_api"] = ClaudePlanner()
                logger.info("Claude API planner initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Claude API planner: {e}")
        
        # Gemini planner
        if available.get("gemini"):
            try:
                self._planners["gemini"] = GeminiPlanner()
                logger.info("Gemini planner initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini planner: {e}")
        
        # DeepSeek planner
        if available.get("deepseek"):
            try:
                self._planners["deepseek"] = DeepSeekPlanner()
                logger.info("DeepSeek planner initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize DeepSeek planner: {e}")
        
        # Claude Code planner (always available, but handled separately)
        self._planners["claude_code"] = None  # Marker for Cursor-based planning
    
    def _select_planner(self, force_planner: Optional[str] = None) -> str:
        """
        Select the planner to use.
        
        Args:
            force_planner: Force a specific planner (from chat or BYOK/BYOC)
            
        Returns:
            Name of selected planner
        """
        # Force planner if specified (BYOK/BYOC or chat choice)
        if force_planner:
            force_planner = force_planner.lower()
            # Handle BYOK/BYOC aliases
            if force_planner in ["byok", "claude_key", "claude_api"]:
                force_planner = "claude_api"
            elif force_planner in ["byoc", "cursor", "claude_code"]:
                force_planner = "claude_code"
            
            if force_planner in self._planners or force_planner == "claude_code":
                logger.info(f"Using forced planner: {force_planner} (BYOK/BYOC or chat choice)")
                return force_planner
            else:
                logger.warning(f"Forced planner '{force_planner}' not available, using auto")
        
        # Auto mode: select based on availability
        if self.planner_mode == "auto":
            has_claude_key = self.fallback_manager.check_api_keys_available().get("claude_api", False)
            selected = self.fallback_manager.get_default_planner(has_claude_key)
            logger.info(f"Auto-selected planner: {selected}")
            return selected
        
        # Specific mode requested
        if self.planner_mode in self._planners or self.planner_mode == "claude_code":
            return self.planner_mode
        
        # Fallback if requested planner not available
        logger.warning(f"Requested planner '{self.planner_mode}' not available, using auto")
        has_claude_key = self.fallback_manager.check_api_keys_available().get("claude_api", False)
        return self.fallback_manager.get_default_planner(has_claude_key)
    
    async def generate_plan(
        self,
        description: str,
        context: Optional[str] = None,
        output_path: Optional[Path] = None,
        force_planner: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a plan with the selected planner.
        
        Args:
            description: Task description
            context: Additional context
            output_path: Optional path to save the plan
            force_planner: Force a specific planner (from chat)
            
        Returns:
            Plan dictionary
            
        Raises:
            ValueError: If planning fails and no fallback available
        """
        selected_planner = self._select_planner(force_planner)
        logger.info(f"Generating plan with planner: {selected_planner}")
        
        # Handle Claude Code separately (returns None, handled by caller)
        if selected_planner == "claude_code":
            logger.info("Using Claude Code (Cursor) - plan generation handled externally")
            return None  # Signal to use external Claude Code
        
        # Try selected planner with fallback
        last_error = None
        
        for attempt_planner in [selected_planner] + self.fallback_manager.get_fallback_chain(selected_planner):
            if attempt_planner not in self._planners:
                continue
            
            try:
                planner = self._planners[attempt_planner]
                plan = await planner.generate_plan(
                    description=description,
                    context=context,
                    output_path=output_path
                )
                
                # Add planner info to metadata
                if "metadata" not in plan:
                    plan["metadata"] = {}
                plan["metadata"]["planner_used"] = attempt_planner
                
                logger.info(f"Plan generated successfully with {attempt_planner}")
                return plan
                
            except Exception as e:
                last_error = e
                logger.warning(f"Planner {attempt_planner} failed: {e}")
                
                # Try fallback
                fallback = self.fallback_manager.select_fallback(
                    failed_planner=attempt_planner,
                    has_claude_key=self.fallback_manager.check_api_keys_available().get("claude_api", False)
                )
                
                if fallback and fallback != attempt_planner:
                    logger.info(f"Trying fallback planner: {fallback}")
                    continue
                else:
                    break
        
        # All planners failed
        raise ValueError(f"Failed to generate plan with any available planner. Last error: {last_error}")
    
    async def review_plan(
        self,
        plan: Dict[str, Any],
        issues: Optional[list] = None,
        planner_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Review a plan with the appropriate planner.
        
        Args:
            plan: Plan dictionary to review
            issues: Optional list of issues
            planner_name: Planner to use (if None, uses planner from plan metadata)
            
        Returns:
            Improved plan dictionary
        """
        # Determine which planner to use
        if planner_name:
            planner_to_use = planner_name
        else:
            planner_to_use = plan.get("metadata", {}).get("planner_used", "claude_api")
        
        if planner_to_use == "claude_code":
            logger.info("Claude Code review handled externally")
            return plan
        
        if planner_to_use not in self._planners:
            logger.warning(f"Planner {planner_to_use} not available for review, skipping")
            return plan
        
        try:
            planner = self._planners[planner_to_use]
            reviewed_plan = await planner.review_plan(plan, issues)
            return reviewed_plan
        except Exception as e:
            logger.warning(f"Plan review failed with {planner_to_use}: {e}, returning original")
            return plan
    
    def get_available_planners(self) -> list:
        """Get list of available planners."""
        available = []
        if "claude_code" in self._planners:
            available.append("claude_code")
        if "claude_api" in self._planners:
            available.append("claude_api")
        if "gemini" in self._planners:
            available.append("gemini")
        if "deepseek" in self._planners:
            available.append("deepseek")
        return available
