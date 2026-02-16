"""Local Orchestrator - HOMEOS V2.
Gère l'alternance entre 3B (Vitesse/Syntaxe) et 7B (Logique/Philosophie).
Intègre les modificateurs de prompt du moteur Bayésien.
"""
from typing import Dict, Any, Optional, List
from loguru import logger
from ..models.ollama_client import OllamaClient

class LocalOrchestrator:
    """
    Orchestrateur local intelligent.
    Optimisé pour Mac Intel (RAM limitée).
    """
    
    def __init__(self, api_url: str = "http://localhost:11434/api/generate"):
        self.api_url = api_url
        self.client_3b = OllamaClient(api_url=api_url, model="llama3.2:3b")
        self.client_7b = OllamaClient(api_url=api_url, model="spinoza-7b")
        self.active_model = None

    async def execute(
        self, 
        prompt: str, 
        task_type: str = "logic", 
        context: Optional[str] = None,
        modifiers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Exécute une tâche sur le modèle local approprié avec modificateurs HCI.
        task_type: 'syntax' (3B) ou 'logic' (7B).
        modifiers: Liste de directives transmises par le moteur Bayésien.
        """
        try:
            target_model = "llama3.2:3b" if task_type == "syntax" else "spinoza-7b"
            client = self.client_3b if task_type == "syntax" else self.client_7b
            
            # Application des modificateurs Bayésiens (HCI Alignment)
            full_prompt = prompt
            if modifiers:
                mod_str = "\n".join(modifiers)
                full_prompt = f"--- INSTRUCTIONS DE STYLE ---\n{mod_str}\n\n--- REQUÊTE ---\n{prompt}"
                logger.info(f"Local Orchestrator: Applying {len(modifiers)} Bayesian modifiers.")

            # Gestion de la RAM : Si le modèle actif change, on décharge l'autre
            if self.active_model and self.active_model != target_model:
                logger.info(f"RAM Cleanup: Unloading {self.active_model}")
                old_client = self.client_7b if self.active_model == "spinoza-7b" else self.client_3b
                await old_client.unload_model()
            
            self.active_model = target_model
            
            # Exécution
            result = await client.generate(full_prompt, context=context)
            
            return {
                "success": result.success,
                "content": result.code,
                "model": f"ollama_{target_model}",
                "metrics": {
                    "time_ms": result.execution_time_ms,
                    "tokens": result.tokens_used
                }
            }
        except Exception as e:
            logger.error(f"Local Orchestrator Error: {e}")
            return {"success": False, "error": str(e)}

    async def cleanup(self):
        """Libère toute la RAM occupée par Ollama."""
        await self.client_3b.unload_model()
        await self.client_7b.unload_model()
        self.active_model = None
        logger.info("Local RAM fully cleared.")