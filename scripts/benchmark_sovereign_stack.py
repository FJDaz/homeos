import asyncio
import time
from Backend.Prod.bridger.persona_orchestrator import PersonaOrchestrator
from loguru import logger

async def run_benchmark():
    orchestrator = PersonaOrchestrator()
    
    test_cases = [
        {
            "name": "Standard (3B Path)",
            "message": "Bonjour Spinoza, comment vas-tu ?",
            "context": {"persona": "Spinoza", "origin": "Persona"}
        },
        {
            "name": "Resistance (7B Elevation Path)",
            "message": "MAIS ALORS si tout est nécessaire, je n'ai aucune liberté, c'est absurde !",
            "context": {"persona": "Spinoza", "origin": "Persona"}
        }
    ]
    
    logger.info("Starting BERT+3+7 Benchmark...")
    
    for case in test_cases:
        logger.info(f"\n--- Testing: {case['name']} ---")
        start = time.time()
        
        try:
            result = await orchestrator.chat(case['message'], case['context'])
            elapsed = time.time() - start
            
            logger.success(f"Response received in {elapsed:.2f}s")
            logger.info(f"Model used: {result['model']}")
            logger.info(f"Intent detected: {result['intent_detected']}")
            logger.info(f"Content: {result['content'][:150]}...")
            
        except Exception as e:
            logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
