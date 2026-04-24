import asyncio
import nest_asyncio
from loguru import logger

def safe_run(coro):
    """
    Exécute une coroutine de manière sécurisée, même si une loop tourne déjà.
    Utile pour appeler du code asynchrone (RAG, Playwright) depuis un handler synchrone FastAPI.
    """
    try:
        # Tenter de récupérer la boucle d'événements en cours
        loop = asyncio.get_running_loop()
        
        # Si on arrive ici, une loop tourne déjà. On applique nest_asyncio pour permettre la réentrance.
        nest_asyncio.apply(loop)
        return loop.run_until_complete(coro)
        
    except RuntimeError:
        # Aucune loop ne tourne dans le thread courant. On peut utiliser asyncio.run() normalement.
        return asyncio.run(coro)
    except Exception as e:
        logger.error(f"Error in safe_run: {e}")
        raise
