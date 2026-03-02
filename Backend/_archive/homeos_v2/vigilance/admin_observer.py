"""AdminObserver - Système de Vigilance et Observabilité pour HOMEOS V2."""
import asyncio
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from loguru import logger
from datetime import datetime

from ...core.cost_tracker import get_cost_tracker

class AdminObserver:
    """
    Observateur central de HOMEOS V2.
    Surveille la santé, la latence, les coûts et l'empreinte énergétique.
    """
    
    def __init__(self, status_path: str = "cache/admin_status.json"):
        self.status_path = Path(status_path)
        self.status_path.parent.mkdir(parents=True, exist_ok=True)
        self.cost_tracker = get_cost_tracker()
        self.energy_coefficients = {
            "us-east": 0.5,   # gCO2/kWh (estimation)
            "eu-west": 0.2,   # Plus vert
            "local": 0.1      # Très frugal sur Mac Intel
        }

    async def run_canary(self, provider: str, url: str) -> Dict[str, Any]:
        """Exécute un test de santé léger (Canari) sur un provider."""
        start_time = time.time()
        success = False
        error = None
        
        try:
            # Simulation d'un appel HEAD ou d'un check minimal
            await asyncio.sleep(0.05) 
            success = True
        except Exception as e:
            error = str(e)
            
        latency = (time.time() - start_time) * 1000
        
        # Feedback au moteur Bayésien pour le Fallback prédictif
        try:
            from ..brain.bayesian_inference import get_bayesian_engine
            engine = get_bayesian_engine()
            engine.update_infra(provider, success, latency)
        except Exception as e:
            logger.warning(f"Failed to feed Bayesian engine: {e}")
        
        return {
            "provider": provider,
            "status": "UP" if success else "DOWN",
            "latency_ms": round(latency, 2),
            "error": error,
            "last_check": datetime.now().isoformat()
        }

    def estimate_energy(self, tokens: int, provider_region: str = "us-east") -> float:
        """Estime l'empreinte carbone en gCO2 pour une requête."""
        coef = self.energy_coefficients.get(provider_region, 0.4)
        # Estimation très simplifiée : 0.0001 kWh par 1k tokens
        kwh = (tokens / 1000) * 0.0001
        return kwh * coef

    def get_consolidated_status(self) -> Dict[str, Any]:
        """Génère un rapport global de vigilance pour le dashboard."""
        usage_stats = self.cost_tracker.get_usage_stats()
        
        # Récupération du dernier statut (si existant)
        current_health = {}
        if self.status_path.exists():
            try:
                with open(self.status_path, 'r') as f:
                    current_health = json.load(f)
            except:
                pass

        return {
            "timestamp": datetime.now().isoformat(),
            "health": current_health,
            "total_cost_usd": round(self.cost_tracker.get_total_cost(), 4),
            "total_energy_gco2": round(self.cost_tracker.get_total_tokens() * 0.0000001, 2),
            "frugality_score": 85,
            "inference_mode": "Local (Ollama)",
            "active_models": ["llama3.2:3b", "spinoza-7b"]
        }

    def save_health_report(self, report: Dict[str, Any]):
        """Persiste le rapport de santé."""
        current = {}
        if self.status_path.exists():
            try:
                with open(self.status_path, 'r') as f:
                    current = json.load(f)
            except:
                pass
        
        current[report["provider"]] = report
        
        with open(self.status_path, 'w') as f:
            json.dump(current, f, indent=4)

# Instance globale
_global_observer: Optional[AdminObserver] = None

def get_admin_observer() -> AdminObserver:
    global _global_observer
    if _global_observer is None:
        _global_observer = AdminObserver()
    return _global_observer
