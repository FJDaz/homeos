"""Quick RAG integration test."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from Backend.Prod.orchestrator import Orchestrator
from loguru import logger

async def test():
    o = Orchestrator(rag_enabled=True)
    logger.info(f"RAG enabled: {o.rag_enabled}")
    logger.info(f"RAG available: {o.rag.enabled if o.rag else False}")
    
    if o.rag and o.rag.enabled:
        rag_results = await o.rag.retrieve('parallélisation étape 7', [], 3)
        logger.info(f"RAG test results: {len(rag_results)}")
        for r in rag_results[:3]:
            logger.info(f"  - {r['reference']}")
        return len(rag_results) > 0
    return False

if __name__ == "__main__":
    success = asyncio.run(test())
    exit(0 if success else 1)
