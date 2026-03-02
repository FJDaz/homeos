"""
BayesianInferenceEngine - Le Cerveau d'Orchestration d'AETHERFLOW V2.
Gère à la fois le Fallback Infrastructure et l'Alignement HCI.
"""
import time
from typing import Dict, Any, List, Optional
from loguru import logger

class BayesianInferenceEngine:
    """
    Moteur d'inférence probabiliste pour l'arbitrage de bouquet.
    Combine les signaux d'infrastructure (Health) et les signaux HCI (Vecteur de Style Dynamique).
    """
    
    def __init__(self):
        # État Interne : Vecteur de Style Dynamique (VSD)
        self.vsd = {
            "expertise": 0.5,   # 0: Débutant, 1: Expert
            "sensibilite": 0.5, # 0: Structure, 1: Ornement
            "patience": 1.0     # 1: Pleine attention, 0: Saturation/Braquage
        }
        
        # État Infrastructure : Probabilités de succès estimées
        self.infra_health = {
            "cloud": 0.95,
            "local_7b": 1.0,
            "local_3b": 1.0
        }

        # Frugalité Adaptative
        self.mode = "normal" # "normal" | "hostile" (ressources ultra-limitées)
        
        # Historique glissant pour l'apprentissage de session
        self.history = []

    def set_frugality_mode(self, mode: str):
        """Active/Désactive le mode Hostile (éco-frugalité)."""
        if mode in ["normal", "hostile"]:
            self.mode = mode
            logger.warning(f"Bayes Brain: Mode switched to {mode.upper()}")

    def update_vsd(self, signal: str, value: float):
        """Met à jour le VSD selon un signal utilisateur."""
        # Signal Pruning: En mode hostile, on ignore les signaux secondaires
        if self.mode == "hostile" and signal == "sensibilite":
            return

        if signal in self.vsd:
            alpha = 0.3 if self.mode == "normal" else 0.1 # Adaptation plus lente en mode éco
            self.vsd[signal] = (self.vsd[signal] * (1 - alpha)) + (value * alpha)
            logger.debug(f"Bayes VSD Update ({self.mode}): {signal} -> {self.vsd[signal]:.2f}")

    def update_infra(self, provider: str, success: bool, latency_ms: float):
        """Met à jour les probas de succès infra basées sur les retours d'AdminObserver."""
        target = "cloud" if provider != "ollama" else "local_7b"
        
        penalty = 0.0
        if not success:
            penalty = 0.2 if self.mode == "normal" else 0.4 # Plus punitif en mode hostile
        elif latency_ms > 2000:
            penalty = 0.05
            
        self.infra_health[target] = max(0.1, self.infra_health[target] - penalty)
        if success:
            self.infra_health[target] = min(0.99, self.infra_health[target] + 0.05)
            
        # Détection automatique du mode hostile sur latence critique
        if self.infra_health["cloud"] < 0.3 and self.mode == "normal":
            self.set_frugality_mode("hostile")

    def select_strategy(self, task_complexity: float, user_intent: str) -> Dict[str, Any]:
        """
        Calcule la stratégie optimale.
        """
        # 1. Arbitrage Infrastructure (Fallback)
        # En mode hostile, on force le local 3b ou le cloud ultra-léger
        use_local = self.infra_health["cloud"] < 0.7 or task_complexity < 0.3 or self.mode == "hostile"
        
        target_model = "cloud"
        if use_local:
            if self.mode == "hostile":
                target_model = "ollama_3b" # On ne tente même pas le 7B en mode hostile
            else:
                target_model = "ollama_7b" if task_complexity > 0.5 else "ollama_3b"
            
        # 2. Alignement HCI (Ajustement du ton via VSD)
        modifiers = []
        
        # Context Pruning suggestion (si patience nulle ou mode hostile)
        prune_context = self.vsd["patience"] < 0.2 or self.mode == "hostile"
        if prune_context:
            modifiers.append("ECO_MODE: Historique réduit au strict nécessaire.")

        if self.vsd["patience"] < 0.4:
            modifiers.append("CONCISE: Sois très bref.")
        if self.vsd["expertise"] > 0.7:
            modifiers.append("TECHNICAL: Utilise le jargon spécifique.")
        elif self.vsd["expertise"] < 0.3:
            modifiers.append("PEDAGOGIC: Explique les termes simplement.")
            
        if self.mode == "normal" and self.vsd["sensibilite"] > 0.7:
            modifiers.append("SENSORIAL: Mets l'accent sur le toucher.")

        return {
            "target_model": target_model,
            "prompt_modifiers": modifiers,
            "vsd_snapshot": self.vsd.copy(),
            "infra_confidence": self.infra_health["cloud"],
            "frugality_mode": self.mode,
            "pruning_required": prune_context
        }

    def get_status(self) -> Dict[str, Any]:
        """Retourne l'état actuel du cerveau pour le dashboard."""
        return {
            "vsd": self.vsd,
            "infra_health": self.infra_health,
            "mode": self.mode
        }

# Singleton
_engine: Optional[BayesianInferenceEngine] = None

def get_bayesian_engine() -> BayesianInferenceEngine:
    global _engine
    if _engine is None:
        _engine = BayesianInferenceEngine()
    return _engine