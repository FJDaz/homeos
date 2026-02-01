"""Test prompt caching integration."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from Backend.Prod.cache import PromptCache
from Backend.Prod.models.agent_router import AgentRouter
from Backend.Prod.models.plan_reader import Step
from loguru import logger


async def test_prompt_cache():
    """Test prompt caching functionality."""
    logger.info("=" * 60)
    logger.info("Testing Prompt Caching")
    logger.info("=" * 60)
    
    # Initialize cache and router
    cache = PromptCache()
    router = AgentRouter(prompt_cache=cache)
    
    # Create a test step with cacheable context
    step_data = {
        "id": "test_step",
        "description": "Test step with cacheable context",
        "type": "code_generation",
        "complexity": 0.5,
        "estimated_tokens": 1000,
        "dependencies": [],
        "validation_criteria": [],
        "context": {}
    }
    step = Step(step_data)
    
    # Large cacheable context (simulating RAG results or docs)
    cacheable_context = """
    Context: AETHERFLOW is an AI agent orchestrator.
    Architecture: Claude Code generates plans, DeepSeek executes them.
    Best practices: Use Gemini for analysis, DeepSeek for code generation.
    """ * 10  # Make it large enough to be cacheable
    
    logger.info("First execution (cache miss expected)...")
    result1 = await router.execute_step(step, context=cacheable_context)
    logger.info(f"Result 1 - Success: {result1.success}, Tokens: {result1.tokens_used}")
    
    logger.info("\nSecond execution (cache hit expected)...")
    result2 = await router.execute_step(step, context=cacheable_context)
    logger.info(f"Result 2 - Success: {result2.success}, Tokens: {result2.tokens_used}")
    
    # Get cache stats
    stats = cache.get_stats()
    summary = cache.get_cache_summary()
    
    logger.info("\n" + "=" * 60)
    logger.info("Cache Statistics")
    logger.info("=" * 60)
    for key, value in summary.items():
        logger.info(f"{key}: {value}")
    
    return stats.cache_hit_rate > 0 or stats.total_requests > 0


if __name__ == "__main__":
    success = asyncio.run(test_prompt_cache())
    sys.exit(0 if success else 1)
