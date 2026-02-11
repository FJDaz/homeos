"""Ollama (Local) API client for hybrid philosophical inference."""
import asyncio
import time
from typing import List, Optional, Dict, Any
import httpx
from loguru import logger

from .base_client import BaseLLMClient, GenerationResult

class OllamaClient(BaseLLMClient):
    """Client for local Ollama inference."""
    
    def __init__(
        self,
        api_url: str = "http://localhost:11434/api/generate",
        model: str = "spinoza-7b", # Modèle par défaut (ton FT)
        timeout: int = 120
    ):
        self.api_url = api_url
        self.model = model
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=self.timeout)

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def specialties(self) -> List[str]:
        return ["philosophy", "local", "unfiltered", "persona"]

    async def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = 0.7,
        cache_params: Optional[Dict[str, Any]] = None,
        output_constraint: Optional[str] = None,
        keep_alive: str = "5m" # Garde en RAM 5 min par défaut
    ) -> GenerationResult:
        """Appelle l'inférence locale Ollama."""
        start_time = time.time()
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "keep_alive": keep_alive,
                "options": {
                    "num_predict": max_tokens or 250,
                    "temperature": temperature
                }
            }
            
            if context:
                payload["system"] = context

            response = await self.client.post(self.api_url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            elapsed = (time.time() - start_time) * 1000
            
            return GenerationResult(
                success=True,
                code=data.get("response", ""),
                tokens_used=data.get("eval_count", 0),
                input_tokens=data.get("prompt_eval_count", 0),
                output_tokens=data.get("eval_count", 0),
                cost_usd=0.0,
                execution_time_ms=elapsed,
                provider=f"ollama_{self.model}"
            )
            
        except Exception as e:
            logger.error(f"Ollama Error: {e}")
            return GenerationResult(
                success=False,
                code="",
                tokens_used=0,
                input_tokens=0,
                output_tokens=0,
                cost_usd=0.0,
                execution_time_ms=0,
                error=str(e),
                provider="ollama_local"
            )

    async def unload_model(self) -> bool:
        """Décharge explicitement le modèle de la RAM (Mac Intel Optimization)."""
        try:
            # Pour décharger, on envoie keep_alive=0
            payload = {"model": self.model, "keep_alive": 0}
            resp = await self.client.post(self.api_url, json=payload)
            return resp.status_code == 200
        except Exception as e:
            logger.error(f"Failed to unload model {self.model}: {e}")
            return False

    async def switch_model(self, new_model: str):
        """Change de modèle et décharge l'ancien si nécessaire."""
        if self.model != new_model:
            await self.unload_model()
            self.model = new_model
            logger.info(f"Ollama switched to {new_model}")

    async def close(self) -> None:
        await self.client.aclose()


{
  "operations": [
    {
      "type": "add_method",
      "target": "OllamaClient",
      "position": "after",
      "after_method": "switch_model",
      "code": "async def memory_management(self, action: str = 'check', model: Optional[str] = None) -> Dict[str, Any]:\n        \"\"\"Gestion avancée de la RAM pour Ollama.\n        Actions possibles: 'check', 'unload', 'load'\n        \"\"\"\n        model = model or self.model\n        try:\n            if action == 'check':\n                # Vérifie l'état de la RAM pour le modèle\n                payload = {\n                    \"model\": model,\n                    \"keep_alive\": \"0s\"\n                }\n                resp = await self.client.post(self.api_url, json=payload)\n                return {\n                    \"loaded\": resp.status_code == 200,\n                    \"model\": model\n                }\n            elif action == 'unload':\n                return await self.unload_model()\n            elif action == 'load':\n                # Charge le modèle avec keep_alive par défaut\n                payload = {\n                    \"model\": model,\n                    \"prompt\": \"\",\n                    \"keep_alive\": \"5m\"\n                }\n                resp = await self.client.post(self.api_url, json=payload)\n                return {\n                    \"success\": resp.status_code == 200,\n                    \"model\": model\n                }\n        except Exception as e:\n            logger.error(f\"Memory management error for {model}: {e}\")\n            return {\n                \"error\": str(e),\n                \"model\": model\n            }"
    },
    {
      "type": "modify_method",
      "target": "OllamaClient.generate",
      "position": "before",
      "code": "        # Gestion mémoire: charge le modèle si nécessaire\n        mem_status = await self.memory_management('load')\n        if not mem_status.get('success', False):\n            logger.warning(f\"Model {self.model} not loaded, proceeding anyway\")\n"
    },
    {
      "type": "add_method",
      "target": "OllamaClient",
      "position": "after",
      "after_method": "memory_management",
      "code": "async def optimize_memory_usage(self, max_ram_mb: int = 4096) -> Dict[str, Any]:\n        \"\"\"Optimise l'utilisation de la RAM en fonction des contraintes.\n        max_ram_mb: limite en Mo (par défaut 4Go)\n        \"\"\"\n        try:\n            # Vérifie l'état actuel\n            status = await self.memory_management('check')\n            if not status.get('loaded', False):\n                return {\n                    \"status\": \"unloaded\",\n                    \"action\": \"none\"\n                }\n\n            # Implémenter ici une logique d'optimisation basée sur:\n            # - Taille du modèle\n            # - Utilisation actuelle de la RAM\n            # - Politique de conservation\n\n            # Pour l'instant, on décharge si la RAM est trop pleine\n            # (à remplacer par une implémentation plus sophistiquée)\n            if max_ram_mb < 2048:  # Exemple de seuil\n                unload_success = await self.memory_management('unload')\n                return {\n                    \"status\": \"optimized\",\n                    \"action\": \"unloaded\",\n                    \"success\": unload_success\n                }\n            return {\n                \"status\": \"ok\",\n                \"action\": \"none\"\n            }\n        except Exception as e:\n            logger.error(f\"Memory optimization error: {e}\")\n            return {\n                \"error\": str(e),\n                \"status\": \"error\"\n            }"
    }
  ]
}