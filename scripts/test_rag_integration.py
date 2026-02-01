"""Test RAG integration in Orchestrator."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from Backend.Prod.orchestrator import Orchestrator
from loguru import logger


async def test_rag_integration():
    """Test RAG integration in orchestrator."""
    logger.info("=" * 60)
    logger.info("Testing RAG Integration in Orchestrator")
    logger.info("=" * 60)
    
    # Create orchestrator with RAG enabled
    orchestrator = Orchestrator(rag_enabled=True)
    
    logger.info(f"RAG enabled: {orchestrator.rag_enabled}")
    if orchestrator.rag:
        logger.info(f"RAG system available: {orchestrator.rag.enabled}")
        stats = orchestrator.rag.get_index_stats()
        logger.info(f"RAG stats: {stats}")
    
    # Test with a simple plan
    test_plan_path = Path("Backend/Notebooks/benchmark_tasks/task_rag_pageindex.json")
    
    if not test_plan_path.exists():
        logger.warning(f"Test plan not found: {test_plan_path}")
        logger.info("Creating minimal test...")
        
        # Test RAG retrieval directly
        if orchestrator.rag and orchestrator.rag.enabled:
            query = "parallélisation étape 7"
            logger.info(f"Testing RAG retrieval with query: '{query}'")
            results = await orchestrator.rag.retrieve(query, history=[], top_k=3)
            
            logger.info(f"Retrieved {len(results)} results:")
            for i, result in enumerate(results, 1):
                logger.info(f"  {i}. {result['reference']} (score: {result['score']:.3f})")
                logger.info(f"     Content: {result['content'][:100]}...")
            
            return len(results) > 0
        else:
            logger.error("RAG not available")
            return False
    else:
        logger.info(f"Executing plan: {test_plan_path}")
        try:
            result = await orchestrator.execute_plan(
                plan_path=test_plan_path,
                output_dir=Path("output/test_rag_integration"),
                context="Test RAG integration"
            )
            
            logger.info("Execution completed")
            logger.info(f"Success: {result['success']}")
            logger.info(f"RAG enabled: {result.get('rag_enabled', False)}")
            logger.info(f"RAG references: {result.get('rag_references', [])}")
            
            return result['success'] and len(result.get('rag_references', [])) > 0
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return False


if __name__ == "__main__":
    success = asyncio.run(test_rag_integration())
    sys.exit(0 if success else 1)
