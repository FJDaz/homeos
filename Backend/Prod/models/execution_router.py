"""Execution router for selecting provider stack based on execution mode."""
from typing import Dict, Optional
from loguru import logger

from .plan_reader import Step
from ..config.settings import settings


class ExecutionRouter:
    """
    Routes execution to appropriate provider stack based on execution mode.
    
    Modes:
    - FAST: Ultra-fast execution for simple tasks (Gemini Flash/Groq)
    - BUILD: Balanced execution for production code (DeepSeek-V3, Codestral for small tasks)
    - DOUBLE-CHECK: High-quality execution with audit (DeepSeek-V3 + Gemini Flash audit)
    """
    
    def __init__(self):
        """Initialize execution router."""
        self.available_providers = self._detect_available_providers()
    
    def _detect_available_providers(self) -> Dict[str, bool]:
        """Detect which providers are available."""
        providers = {
            "deepseek": bool(settings.deepseek_api_key),
            "codestral": bool(settings.mistral_api_key and 
                            settings.mistral_api_key.isascii() and 
                            not settings.mistral_api_key.startswith("your_") and
                            not settings.mistral_api_key.startswith("votre_")),
            "gemini": bool(settings.google_api_key and
                          settings.google_api_key.isascii() and
                          not settings.google_api_key.startswith("your_") and
                          not settings.google_api_key.startswith("votre_")),
            "groq": bool(settings.groq_api_key and
                        settings.groq_api_key.isascii() and
                        not settings.groq_api_key.startswith("your_") and
                        not settings.groq_api_key.startswith("votre_"))
        }
        return providers
    
    def get_stack(
        self,
        mode: str,
        step: Optional[Step] = None,
        task_size: Optional[int] = None
    ) -> Dict[str, str]:
        """
        Get provider stack for a given execution mode.
        
        Args:
            mode: Execution mode (FAST, BUILD, DOUBLE-CHECK)
            step: Optional step object for context-aware routing
            task_size: Optional task size estimate (in lines or tokens)
            
        Returns:
            Dictionary with provider assignments:
            {
                "plan": "provider_name",  # For plan generation (if applicable)
                "execution": "provider_name",  # For step execution
                "audit": "provider_name"  # For audit/validation (if applicable)
            }
        """
        mode = mode.upper()
        
        if mode == "FAST":
            return self._get_fast_stack(step, task_size)
        elif mode == "BUILD":
            return self._get_build_stack(step, task_size)
        elif mode == "DOUBLE-CHECK":
            return self._get_double_check_stack(step, task_size)
        else:
            logger.warning(f"Unknown execution mode: {mode}, defaulting to BUILD")
            return self._get_build_stack(step, task_size)
    
    def _get_fast_stack(self, step: Optional[Step], task_size: Optional[int]) -> Dict[str, str]:
        """
        Get FAST mode stack: Ultra-fast execution for simple tasks.
        
        Stack:
        - Plan: Gemini Flash (if available) or Groq
        - Execution: Groq/Llama 3.3 (if available) or Gemini Flash
        - Audit: None (no verification)
        """
        stack = {
            "plan": None,
            "execution": None,
            "audit": None
        }
        
        # Prefer Groq for execution (ultra-fast)
        if self.available_providers.get("groq"):
            stack["execution"] = "groq"
        elif self.available_providers.get("gemini"):
            stack["execution"] = "gemini"
        else:
            # Fallback to DeepSeek if neither available
            stack["execution"] = "deepseek"
        
        # For plan generation, prefer Gemini Flash
        if self.available_providers.get("gemini"):
            stack["plan"] = "gemini"
        elif self.available_providers.get("groq"):
            stack["plan"] = "groq"
        else:
            stack["plan"] = "deepseek"
        
        return stack
    
    def _get_build_stack(self, step: Optional[Step], task_size: Optional[int]) -> Dict[str, str]:
        """
        Get BUILD mode stack: Balanced execution for production code.
        
        Stack:
        - Plan: DeepSeek-V3 (or Claude 4.5 if available - not implemented yet)
        - Execution: DeepSeek-V3 for large/complex, Codestral for small (<30 lines)
        - Audit: None
        """
        stack = {
            "plan": "deepseek",  # Default to DeepSeek for plan
            "execution": None,
            "audit": None
        }
        
        # Use Codestral for small tasks (<30 lines or <500 tokens)
        if step:
            if (step.type == "refactoring" and step.complexity < 0.5) or \
               (step.type == "code_generation" and step.estimated_tokens < 500 and step.complexity < 0.5):
                if self.available_providers.get("codestral"):
                    stack["execution"] = "codestral"
                else:
                    stack["execution"] = "deepseek"
            else:
                stack["execution"] = "deepseek"
        elif task_size and task_size < 30:
            if self.available_providers.get("codestral"):
                stack["execution"] = "codestral"
            else:
                stack["execution"] = "deepseek"
        else:
            stack["execution"] = "deepseek"
        
        return stack
    
    def _get_double_check_stack(self, step: Optional[Step], task_size: Optional[int]) -> Dict[str, str]:
        """
        Get DOUBLE-CHECK mode stack: High-quality execution with audit.
        
        Stack:
        - Plan: DeepSeek-V3 (or Claude 4.5)
        - Execution: DeepSeek-V3
        - Audit: Gemini Flash (fast, free validation)
        """
        stack = {
            "plan": "deepseek",
            "execution": "deepseek",
            "audit": None
        }
        
        # Use Gemini Flash for audit if available
        if self.available_providers.get("gemini"):
            stack["audit"] = "gemini"
        elif self.available_providers.get("groq"):
            stack["audit"] = "groq"
        # If neither available, skip audit (still execute with DeepSeek)
        
        return stack
    
    def get_provider_for_step(
        self,
        step: Step,
        mode: str = "BUILD"
    ) -> str:
        """
        Get the appropriate provider for a step based on execution mode.
        
        This is a convenience method that combines mode-based routing with
        step-specific routing logic.
        
        Args:
            step: Step to execute
            mode: Execution mode (FAST, BUILD, DOUBLE-CHECK)
            
        Returns:
            Provider name to use
        """
        stack = self.get_stack(mode, step)
        return stack["execution"] or "deepseek"
    
    def should_use_audit(self, mode: str) -> bool:
        """Check if audit should be used for the given mode."""
        return mode.upper() == "DOUBLE-CHECK"
    
    def get_audit_provider(self, mode: str) -> Optional[str]:
        """Get the audit provider for the given mode."""
        if not self.should_use_audit(mode):
            return None
        
        stack = self.get_stack(mode)
        return stack.get("audit")
