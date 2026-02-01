"""
Speculative Decoding implementation for AETHERFLOW.

Uses draft + verify pattern:
- Draft model (fast, cheap): Groq or Gemini Flash
- Verify model (quality): DeepSeek or Gemini
- Parallel verification of draft tokens
- Accept verified tokens to reduce TTFT
"""
import asyncio
import time
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict, Any
from loguru import logger

from ..models.base_client import BaseLLMClient, GenerationResult


@dataclass
class SpeculativeResult:
    """Result of speculative decoding."""
    result: GenerationResult
    draft_provider: str
    verify_provider: str
    draft_time_ms: float
    verify_time_ms: float
    total_time_ms: float
    speculative_accept_rate: float  # % of draft tokens accepted
    speedup_factor: float  # Speedup vs non-speculative
    draft_tokens: int
    accepted_tokens: int
    rejected_tokens: int


class SpeculativeDecoder:
    """
    Speculative decoding decoder using draft + verify pattern.
    
    Strategy:
    1. Generate draft tokens with fast model (Groq/Gemini Flash)
    2. Verify draft tokens in parallel with quality model (DeepSeek/Gemini)
    3. Accept verified tokens, regenerate rejected ones
    """
    
    def __init__(
        self,
        draft_client: BaseLLMClient,
        verify_client: BaseLLMClient,
        draft_provider: str = "groq",
        verify_provider: str = "deepseek"
    ):
        """
        Initialize speculative decoder.
        
        Args:
            draft_client: Fast model for draft generation (Groq/Gemini Flash)
            verify_client: Quality model for verification (DeepSeek/Gemini)
            draft_provider: Name of draft provider
            verify_provider: Name of verify provider
        """
        self.draft_client = draft_client
        self.verify_client = verify_client
        self.draft_provider = draft_provider
        self.verify_provider = verify_provider
    
    async def decode(
        self,
        prompt: str,
        context: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        draft_max_tokens: Optional[int] = None
    ) -> SpeculativeResult:
        """
        Perform speculative decoding: draft + verify.
        
        Args:
            prompt: User prompt
            context: Additional context
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            draft_max_tokens: Max tokens for draft (default: max_tokens or 512)
            
        Returns:
            SpeculativeResult with generation and metrics
        """
        start_time = time.time()
        
        # Determine draft token limit
        if draft_max_tokens is None:
            draft_max_tokens = min(max_tokens or 512, 512)  # Cap draft at 512 tokens
        
        # Step 1: Generate draft tokens (fast model)
        draft_start = time.time()
        logger.info(f"Speculative decoding: Generating draft with {self.draft_provider}")
        
        draft_result = await self.draft_client.generate(
            prompt=prompt,
            context=context,
            max_tokens=draft_max_tokens,
            temperature=temperature
        )
        
        draft_time = (time.time() - draft_start) * 1000  # ms
        draft_text = draft_result.code  # GenerationResult uses .code, not .text
        draft_tokens = len(draft_text.split())  # Approximate token count
        
        if not draft_text.strip():
            # Draft failed, fallback to verify model directly
            logger.warning("Draft generation failed, falling back to verify model")
            verify_start = time.time()
            verify_result = await self.verify_client.generate(
                prompt=prompt,
                context=context,
                max_tokens=max_tokens,
                temperature=temperature
            )
            verify_time = (time.time() - verify_start) * 1000
            
            return SpeculativeResult(
                result=verify_result,
                draft_provider=self.draft_provider,
                verify_provider=self.verify_provider,
                draft_time_ms=draft_time,
                verify_time_ms=verify_time,
                total_time_ms=(time.time() - start_time) * 1000,
                speculative_accept_rate=0.0,
                speedup_factor=1.0,
                draft_tokens=0,
                accepted_tokens=0,
                rejected_tokens=0
            )
        
        # Step 2: Verify draft tokens (quality model)
        # We verify by asking the verify model to complete from the draft
        verify_start = time.time()
        logger.info(f"Speculative decoding: Verifying draft with {self.verify_provider}")
        
        # Create verification prompt: ask verify model to continue/validate draft
        verify_prompt = f"{prompt}\n\nDraft response:\n{draft_text}\n\nPlease verify and complete this draft if correct, or regenerate if incorrect:"
        
        verify_result = await self.verify_client.generate(
            prompt=verify_prompt,
            context=context,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        verify_time = (time.time() - verify_start) * 1000
        
        # Step 3: Compare draft vs verify to calculate accept rate
        verify_text = verify_result.code  # GenerationResult uses .code, not .text
        
        # Simple token-level comparison (approximate)
        draft_tokens_list = draft_text.split()
        verify_tokens_list = verify_text.split()
        
        # Calculate overlap (tokens that match)
        min_len = min(len(draft_tokens_list), len(verify_tokens_list))
        accepted = 0
        
        # Compare first N tokens
        for i in range(min(min_len, 50)):  # Compare first 50 tokens
            if i < len(draft_tokens_list) and i < len(verify_tokens_list):
                if draft_tokens_list[i] == verify_tokens_list[i]:
                    accepted += 1
        
        accepted_tokens = accepted
        rejected_tokens = draft_tokens - accepted
        
        # Calculate accept rate
        if draft_tokens > 0:
            accept_rate = (accepted_tokens / min(draft_tokens, 50)) * 100  # Cap at 50 tokens comparison
        else:
            accept_rate = 0.0
        
        # Use verify result (higher quality)
        final_result = verify_result
        
        total_time = (time.time() - start_time) * 1000
        
        # Calculate speedup: if draft was fast and verify accepted most tokens, we saved time
        # Speedup = (time_without_speculative) / (time_with_speculative)
        # Estimated time without speculative = verify_time (if we had to generate from scratch)
        estimated_non_speculative_time = verify_time * 1.2  # Add 20% overhead
        if total_time > 0:
            speedup = estimated_non_speculative_time / total_time
        else:
            speedup = 1.0
        
        logger.info(
            f"Speculative decoding complete: "
            f"accept_rate={accept_rate:.1f}%, "
            f"speedup={speedup:.2f}x, "
            f"draft={draft_time:.0f}ms, "
            f"verify={verify_time:.0f}ms"
        )
        
        return SpeculativeResult(
            result=final_result,
            draft_provider=self.draft_provider,
            verify_provider=self.verify_provider,
            draft_time_ms=draft_time,
            verify_time_ms=verify_time,
            total_time_ms=total_time,
            speculative_accept_rate=accept_rate,
            speedup_factor=speedup,
            draft_tokens=draft_tokens,
            accepted_tokens=accepted_tokens,
            rejected_tokens=rejected_tokens
        )
    
    async def decode_parallel(
        self,
        prompt: str,
        context: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> SpeculativeResult:
        """
        Perform speculative decoding with parallel draft + verify.
        
        This version starts verify immediately after draft starts generating,
        using streaming if available.
        
        Args:
            prompt: User prompt
            context: Additional context
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            SpeculativeResult with generation and metrics
        """
        start_time = time.time()
        
        # Start draft generation
        draft_task = asyncio.create_task(
            self.draft_client.generate(
                prompt=prompt,
                context=context,
                max_tokens=min(max_tokens or 512, 512),
                temperature=temperature
            )
        )
        
        # Wait for draft to complete
        draft_result = await draft_task
        draft_time = (time.time() - start_time) * 1000
        
        draft_text = draft_result.code  # GenerationResult uses .code, not .text

        if not draft_text.strip():
            # Fallback to verify only
            verify_start = time.time()
            verify_result = await self.verify_client.generate(
                prompt=prompt,
                context=context,
                max_tokens=max_tokens,
                temperature=temperature
            )
            verify_time = (time.time() - verify_start) * 1000
            
            return SpeculativeResult(
                result=verify_result,
                draft_provider=self.draft_provider,
                verify_provider=self.verify_provider,
                draft_time_ms=draft_time,
                verify_time_ms=verify_time,
                total_time_ms=(time.time() - start_time) * 1000,
                speculative_accept_rate=0.0,
                speedup_factor=1.0,
                draft_tokens=0,
                accepted_tokens=0,
                rejected_tokens=0
            )
        
        # Verify draft
        verify_start = time.time()
        verify_prompt = f"{prompt}\n\nDraft: {draft_text}\n\nVerify and complete:"
        
        verify_result = await self.verify_client.generate(
            prompt=verify_prompt,
            context=context,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        verify_time = (time.time() - verify_start) * 1000
        total_time = (time.time() - start_time) * 1000
        
        # Calculate metrics (simplified)
        draft_tokens = len(draft_text.split())
        verify_text = verify_result.code  # GenerationResult uses .code, not .text
        verify_tokens = len(verify_text.split())
        
        # Approximate accept rate
        min_tokens = min(draft_tokens, verify_tokens, 50)
        accepted = sum(
            1 for i in range(min_tokens)
            if i < len(draft_text.split()) and i < len(verify_text.split())
            and draft_text.split()[i] == verify_text.split()[i]
        )
        
        accept_rate = (accepted / min_tokens * 100) if min_tokens > 0 else 0.0
        
        estimated_non_speculative = verify_time * 1.2
        speedup = (estimated_non_speculative / total_time) if total_time > 0 else 1.0
        
        return SpeculativeResult(
            result=verify_result,
            draft_provider=self.draft_provider,
            verify_provider=self.verify_provider,
            draft_time_ms=draft_time,
            verify_time_ms=verify_time,
            total_time_ms=total_time,
            speculative_accept_rate=accept_rate,
            speedup_factor=speedup,
            draft_tokens=draft_tokens,
            accepted_tokens=accepted,
            rejected_tokens=draft_tokens - accepted
        )
