"""
Speculative Decoding module for AETHERFLOW.

Implements draft + verify pipeline to reduce TTFT (Time To First Token) by:
1. Generating draft tokens with a fast model (Groq/Gemini Flash)
2. Verifying draft tokens in parallel with reference model (DeepSeek/Gemini)
3. Accepting verified tokens to skip generation time

Target: >70% speculative accept rate, >1.5x speedup factor.
"""
from .decoder import SpeculativeDecoder, SpeculativeResult

__all__ = ["SpeculativeDecoder", "SpeculativeResult"]
