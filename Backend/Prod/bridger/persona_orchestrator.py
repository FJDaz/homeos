"""Orchestrateur Hybride Persona (Aetherflow V2).
Gère la séparation entre l'intelligence de surveillance (Cloud) 
et le cœur philosophique (Local 7B FT).
"""
import json
import time
from typing import Dict, Any, List
from loguru import logger

from ..models.gemini_client import GeminiClient
from ..models.ollama_client import OllamaClient

class PersonaOrchestrator:
    def __init__(self):
        # Niveau 1 : Surveillance & Vigilance (Cloud rapide)
        self.vigilance = GeminiClient(execution_mode="FAST")
        
        # Niveau 2 : Cœur Philosophique (Local 7B FT)
        self.philosophe_local = OllamaClient(model="spinoza-7b") 

    async def chat(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        philosopher = context.get("persona", "Spinoza").lower()
        
        # --- Étape 1 : Vigilance (Analyse d'intention via Cloud) ---
        intent_prompt = f"""Analyse cette réponse d'élève : "{message}"
Détecte l'état : confusion, résistance, accord ou neutre.
Réponds uniquement par un mot."""
        
        intent_result = await self.vigilance.generate(prompt=intent_prompt, max_tokens=10)
        intent = intent_result.code.strip().lower() if intent_result.success else "neutre"
        
        # --- Étape 2 : Inférence Philosophique (Hybride) ---
        # On prépare le prompt avec le persona pur
        system_prompt = self._get_persona_prompt(philosopher, intent)
        
        # On tente le local d'abord (Souveraineté)
        response = await self.philosophe_local.generate(
            prompt=message,
            context=system_prompt,
            max_tokens=250
        )
        
        model_used = "ollama_spinoza_7b"
        
        # --- Étape 3 : Fallback Stratégique (Résilience) ---
        if not response.success:
            logger.warning(f"Ollama local down (Spinoza 7B). Fallback sur Gemini.")
            response = await self.vigilance.generate(
                prompt=f"{system_prompt}\n\nÉlève: {message}\n{philosopher.capitalize()}:",
                max_tokens=250
            )
            model_used = "gemini_fallback"

        elapsed = (time.time() - start_time) * 1000
        
        return {
            "success": True,
            "content": response.code,
            "intent_detected": intent,
            "model": model_used,
            "metadata": {
                "time_ms": elapsed,
                "philosopher": philosopher,
                "hybrid_mode": True
            }
        }

    def _get_persona_prompt(self, philo: str, intent: str) -> str:
        # On pourrait charger ça d'un fichier YAML plus tard
        prompts = {
            "spinoza": "Tu ES Baruch Spinoza. Tutoie l'élève. Révèle la nécessité. Pas de code.",
            "bergson": "Tu ES Henri Bergson. Tutoie l'élève. Parle de la durée. Pas de code.",
            "kant": "Tu ES Emmanuel Kant. Tutoie l'élève. Examine les conditions. Pas de code."
        }
        base = prompts.get(philo, prompts["spinoza"])
        
        # Adaptation selon vigilance
        if intent == "resistance":
            base += " L'élève résiste : utilise 'MAIS ALORS' pour montrer une contradiction."
        elif intent == "confusion":
            base += " L'élève est perdu : donne une analogie concrète."
            
        return base
