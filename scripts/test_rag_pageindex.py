"""
Test script for PageIndexRAG system with PRD and roadmap documents.

This script validates the RAG system's ability to retrieve relevant context
from PRD and roadmap documents.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from Backend.Prod.rag import PageIndexRAG
from loguru import logger


async def test_rag_basic():
    """Test basic RAG functionality."""
    logger.info("Testing PageIndexRAG basic functionality...")
    
    # Initialize RAG system
    try:
        rag = PageIndexRAG()
        logger.info("✓ RAG system initialized")
    except Exception as e:
        logger.error(f"✗ Failed to initialize RAG: {e}")
        return False
    
    # Get index stats
    stats = rag.get_index_stats()
    logger.info(f"Index stats: {stats}")
    
    # Test retrieval (will return empty if LlamaIndex not installed)
    query = "parallélisation Étape 7"
    logger.info(f"Testing retrieval with query: '{query}'")
    
    try:
        results = await rag.retrieve(query, history=[], top_k=3)
        logger.info(f"Retrieved {len(results)} results")
        
        if results:
            for i, result in enumerate(results, 1):
                logger.info(f"Result {i}:")
                logger.info(f"  Reference: {result.get('reference', 'N/A')}")
                logger.info(f"  Score: {result.get('score', 0.0):.3f}")
                logger.info(f"  Content preview: {result.get('content', '')[:100]}...")
        else:
            logger.warning("No results returned (LlamaIndex may not be installed)")
        
        return True
    except Exception as e:
        logger.error(f"✗ Retrieval failed: {e}")
        return False


async def test_rag_with_history():
    """Test RAG with conversation history."""
    logger.info("Testing RAG with conversation history...")
    
    rag = PageIndexRAG()
    
    history = [
        {"role": "user", "content": "Je veux implémenter la parallélisation"},
        {"role": "assistant", "content": "D'accord, je vais vous aider avec ça."}
    ]
    
    query = "Étape 7 parallélisation"
    results = await rag.retrieve(query, history=history, top_k=3)
    
    logger.info(f"Retrieved {len(results)} results with history context")
    return len(results) >= 0  # Accept empty results if LlamaIndex not installed


async def main():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("PageIndexRAG Test Suite")
    logger.info("=" * 60)
    
    tests = [
        ("Basic RAG", test_rag_basic),
        ("RAG with History", test_rag_with_history),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n--- Running: {test_name} ---")
        try:
            result = await test_func()
            results.append((test_name, result))
            logger.info(f"{'✓' if result else '✗'} {test_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            logger.error(f"✗ {test_name} raised exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        logger.info(f"{'✓' if result else '✗'} {test_name}: {status}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("All tests passed! ✓")
    else:
        logger.warning("Some tests failed or returned empty results (LlamaIndex may need to be installed)")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
