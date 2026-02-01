"""Fallback manager for planner selection."""
from typing import Optional, List
from loguru import logger

from ..config.settings import settings


class FallbackManager:
    """Manages fallback logic for planners."""
    
    # Order of fallback planners (from most expensive to cheapest)
    FALLBACK_CHAIN = [
        "claude_api",    # Most expensive but highest quality
        "gemini",        # Good balance
        "deepseek"       # Cheapest
    ]
    
    def __init__(self, enable_fallback: bool = True):
        """
        Initialize fallback manager.
        
        Args:
            enable_fallback: Whether to enable automatic fallback
        """
        self.enable_fallback = enable_fallback
    
    def check_api_keys_available(self) -> dict:
        """
        Check which API keys are available.
        
        Returns:
            Dictionary with availability status for each planner
        """
        availability = {
            "claude_api": bool(
                settings.anthropic_api_key and 
                settings.anthropic_api_key.isascii() and 
                not settings.anthropic_api_key.startswith("your_") and
                not settings.anthropic_api_key.startswith("votre_")
            ),
            "gemini": bool(
                settings.google_api_key and 
                settings.google_api_key.isascii() and 
                not settings.google_api_key.startswith("your_") and
                not settings.google_api_key.startswith("votre_")
            ),
            "deepseek": bool(
                settings.deepseek_api_key and 
                settings.deepseek_api_key.isascii() and 
                not settings.deepseek_api_key.startswith("your_") and
                not settings.deepseek_api_key.startswith("votre_")
            ),
            "claude_code": True  # Always available (Cursor)
        }
        
        return availability
    
    def select_fallback(
        self, 
        failed_planner: str, 
        has_claude_key: bool,
        available_planners: Optional[dict] = None
    ) -> Optional[str]:
        """
        Select the fallback planner.
        
        Rules:
        - If no Claude key: Gemini (economical) → DeepSeek
        - If has Claude key and failure: DeepSeek (super eco) → Gemini
        - Developer: can force manually
        
        Args:
            failed_planner: The planner that failed
            has_claude_key: Whether user has Claude API key
            available_planners: Optional dict of available planners (if None, checks automatically)
            
        Returns:
            Name of fallback planner, or None if no fallback available
        """
        if not self.enable_fallback:
            return None
        
        if available_planners is None:
            available_planners = self.check_api_keys_available()
        
        # Remove failed planner from consideration
        available_planners = {k: v for k, v in available_planners.items() if k != failed_planner}
        
        # If no Claude key, prefer Gemini then DeepSeek
        if not has_claude_key:
            if available_planners.get("gemini"):
                logger.info(f"Fallback: {failed_planner} → gemini (economical, no Claude key)")
                return "gemini"
            elif available_planners.get("deepseek"):
                logger.info(f"Fallback: {failed_planner} → deepseek (super economical)")
                return "deepseek"
        
        # If has Claude key, prefer DeepSeek then Gemini (cheaper alternatives)
        else:
            if available_planners.get("deepseek"):
                logger.info(f"Fallback: {failed_planner} → deepseek (super economical)")
                return "deepseek"
            elif available_planners.get("gemini"):
                logger.info(f"Fallback: {failed_planner} → gemini (economical)")
                return "gemini"
        
        # No fallback available
        logger.warning(f"No fallback available for {failed_planner}")
        return None
    
    def get_default_planner(self, has_claude_key: bool) -> str:
        """
        Get the default planner based on available keys.
        
        Args:
            has_claude_key: Whether user has Claude API key
            
        Returns:
            Name of default planner
        """
        available = self.check_api_keys_available()
        
        # If no Claude key, use Gemini (economical)
        if not has_claude_key:
            if available.get("gemini"):
                return "gemini"
            elif available.get("deepseek"):
                return "deepseek"
            else:
                return "claude_code"  # Fallback to Cursor
        
        # If has Claude key, use Claude API
        if available.get("claude_api"):
            return "claude_api"
        elif available.get("gemini"):
            return "gemini"
        elif available.get("deepseek"):
            return "deepseek"
        else:
            return "claude_code"  # Fallback to Cursor
    
    def get_fallback_chain(self, planner: str) -> List[str]:
        """
        Get the fallback chain for a given planner.
        
        Args:
            planner: Starting planner name
            
        Returns:
            List of fallback planners in order
        """
        available = self.check_api_keys_available()
        
        # Build chain based on availability
        chain = []
        
        if planner == "claude_api":
            if available.get("deepseek"):
                chain.append("deepseek")
            if available.get("gemini"):
                chain.append("gemini")
        elif planner == "gemini":
            if available.get("deepseek"):
                chain.append("deepseek")
        elif planner == "deepseek":
            # DeepSeek is cheapest, no fallback
            pass
        
        return chain
