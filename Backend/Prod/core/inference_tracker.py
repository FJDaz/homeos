"""
Inference Tracker - Suivi détaillé des appels LLM pour AetherFlow.

Ce module complète ModeMonitor en traçant chaque inférence individuelle :
- Appels aux différents providers (Groq, Gemini, DeepSeek)
- Tokens IN/OUT par appel
- Coût par inférence
- Contexte (fichier, action, mode)
- Latence (temps de réponse)

Utilisation:
    from Backend.Prod.core.inference_tracker import InferenceTracker, record_inference
    
    # Après chaque appel LLM
    record_inference(
        provider="groq",
        model="llama-3.1-70b",
        tokens_in=1500,
        tokens_out=800,
        cost_usd=0.002,
        latency_ms=450,
        context="generate_component",
        file_path="Backend/Prod/sullivan/agent/tools.py",
        mode="PROD"
    )
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from loguru import logger


class Provider(str, Enum):
    """Providers LLM supportés."""
    GROQ = "groq"
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    CLAUDE = "claude"


@dataclass
class InferenceRecord:
    """
    Enregistrement d'une inférence LLM individuelle.
    
    Attributes:
        timestamp: Horodatage ISO de l'appel
        provider: Provider utilisé (groq, gemini, deepseek, claude)
        model: Nom du modèle (ex: llama-3.1-70b, gemini-pro)
        tokens_in: Nombre de tokens en entrée (prompt)
        tokens_out: Nombre de tokens en sortie (completion)
        cost_usd: Coût estimé en USD
        latency_ms: Temps de réponse en millisecondes
        context: Contexte de l'appel (ex: "code_generation", "analysis")
        file_path: Fichier concerné (optionnel)
        mode: Mode AetherFlow associé (PROTO, PROD, etc.)
        success: Succès ou échec de l'appel
        error: Message d'erreur si échec
    """
    timestamp: str
    provider: str
    model: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    latency_ms: float
    context: str
    file_path: Optional[str] = None
    mode: Optional[str] = None
    success: bool = True
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour JSON."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InferenceRecord':
        """Crée depuis un dictionnaire."""
        return cls(**data)


class InferenceTracker:
    """
    Singleton pour tracker les inférences LLM.
    
    Stockage persistant dans ~/.aetherflow/inference_tracking.json
    """
    
    _instance: Optional['InferenceTracker'] = None
    _storage_path: Path = Path.home() / ".aetherflow" / "inference_tracking.json"
    
    # Coûts par million de tokens (approximatifs, à jour fév 2026)
    PRICING = {
        "groq": {
            "llama-3.1-8b": {"input": 0.05, "output": 0.08},
            "llama-3.1-70b": {"input": 0.59, "output": 0.79},
            "mixtral-8x7b": {"input": 0.24, "output": 0.24},
        },
        "gemini": {
            "gemini-pro": {"input": 0.50, "output": 1.50},
            "gemini-flash": {"input": 0.35, "output": 0.70},
        },
        "deepseek": {
            "deepseek-chat": {"input": 0.14, "output": 0.28},
            "deepseek-coder": {"input": 0.14, "output": 0.28},
        },
        "claude": {
            "claude-3-opus": {"input": 15.00, "output": 75.00},
            "claude-3-sonnet": {"input": 3.00, "output": 15.00},
            "claude-3-haiku": {"input": 0.25, "output": 1.25},
        }
    }
    
    def __new__(cls) -> 'InferenceTracker':
        """Crée ou retourne l'instance singleton."""
        if cls._instance is None:
            cls._instance = super(InferenceTracker, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """Initialise le tracker."""
        self.records: List[InferenceRecord] = []
        self._session_start = datetime.now()
        self._load_data()
        logger.info(f"InferenceTracker initialized with {len(self.records)} records")
    
    def _load_data(self) -> None:
        """Charge les données existantes."""
        if self._storage_path.exists():
            try:
                with open(self._storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.records = [
                    InferenceRecord.from_dict(r) for r in data.get("records", [])
                ]
                logger.debug(f"Loaded {len(self.records)} inference records")
            except Exception as e:
                logger.warning(f"Could not load inference data: {e}. Starting fresh.")
                self.records = []
        else:
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            self.records = []
    
    def _save_data(self) -> None:
        """Sauvegarde les données."""
        try:
            data = {
                "records": [r.to_dict() for r in self.records],
                "last_updated": datetime.now().isoformat(),
                "session_stats": self.get_session_stats()
            }
            with open(self._storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Could not save inference data: {e}")
    
    def record(
        self,
        provider: str,
        model: str,
        tokens_in: int,
        tokens_out: int,
        cost_usd: Optional[float] = None,
        latency_ms: Optional[float] = None,
        context: str = "unknown",
        file_path: Optional[str] = None,
        mode: Optional[str] = None,
        success: bool = True,
        error: Optional[str] = None,
    ) -> InferenceRecord:
        """
        Enregistre une inférence.
        
        Si cost_usd n'est pas fourni, il est calculé automatiquement
        selon la grille de prix.
        """
        # Calculer le coût si non fourni
        if cost_usd is None:
            cost_usd = self._calculate_cost(provider, model, tokens_in, tokens_out)
        
        record = InferenceRecord(
            timestamp=datetime.now().isoformat(),
            provider=provider,
            model=model,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_usd=cost_usd,
            latency_ms=latency_ms or 0,
            context=context,
            file_path=file_path,
            mode=mode,
            success=success,
            error=error,
        )
        
        self.records.append(record)
        
        # Sauvegarder périodiquement (toutes les 10 inférences)
        if len(self.records) % 10 == 0:
            self._save_data()
        
        logger.debug(f"Recorded inference: {provider}/{model} ({tokens_in+tokens_out} tokens, ${cost_usd:.4f})")
        return record
    
    def _calculate_cost(self, provider: str, model: str, tokens_in: int, tokens_out: int) -> float:
        """Calcule le coût selon la grille tarifaire."""
        provider_pricing = self.PRICING.get(provider, {})
        model_pricing = provider_pricing.get(model, {"input": 0.0, "output": 0.0})
        
        input_cost = (tokens_in / 1_000_000) * model_pricing["input"]
        output_cost = (tokens_out / 1_000_000) * model_pricing["output"]
        
        return round(input_cost + output_cost, 6)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Statistiques de la session courante."""
        session_records = [
            r for r in self.records 
            if datetime.fromisoformat(r.timestamp) >= self._session_start
        ]
        
        return {
            "session_start": self._session_start.isoformat(),
            "inferences_count": len(session_records),
            "total_tokens": sum(r.tokens_in + r.tokens_out for r in session_records),
            "total_cost_usd": sum(r.cost_usd for r in session_records),
            "avg_latency_ms": sum(r.latency_ms for r in session_records) / len(session_records) if session_records else 0,
            "by_provider": self._group_by_provider(session_records),
        }
    
    def _group_by_provider(self, records: List[InferenceRecord]) -> Dict[str, Any]:
        """Groupe les stats par provider."""
        result = {}
        for provider in set(r.provider for r in records):
            provider_records = [r for r in records if r.provider == provider]
            result[provider] = {
                "count": len(provider_records),
                "tokens": sum(r.tokens_in + r.tokens_out for r in provider_records),
                "cost_usd": sum(r.cost_usd for r in provider_records),
            }
        return result
    
    def get_stats_by_mode(self) -> Dict[str, Any]:
        """Statistiques groupées par mode AetherFlow."""
        result = {}
        for mode in set(r.mode for r in self.records if r.mode):
            mode_records = [r for r in self.records if r.mode == mode]
            result[mode] = {
                "count": len(mode_records),
                "total_tokens": sum(r.tokens_in + r.tokens_out for r in mode_records),
                "total_cost_usd": sum(r.cost_usd for r in mode_records),
                "avg_latency_ms": sum(r.latency_ms for r in mode_records) / len(mode_records) if mode_records else 0,
            }
        return result
    
    def get_stats_by_context(self) -> Dict[str, Any]:
        """Statistiques groupées par contexte d'utilisation."""
        result = {}
        for context in set(r.context for r in self.records):
            context_records = [r for r in self.records if r.context == context]
            result[context] = {
                "count": len(context_records),
                "total_tokens": sum(r.tokens_in + r.tokens_out for r in context_records),
                "total_cost_usd": sum(r.cost_usd for r in context_records),
            }
        return result
    
    def generate_report(self, format: str = "text", period: str = "session") -> str:
        """Génère un rapport d'utilisation des inférences."""
        if period == "session":
            stats = self.get_session_stats()
            records = [r for r in self.records if datetime.fromisoformat(r.timestamp) >= self._session_start]
            title = "SESSION COURANTE"
        else:
            stats = {
                "inferences_count": len(self.records),
                "total_tokens": sum(r.tokens_in + r.tokens_out for r in self.records),
                "total_cost_usd": sum(r.cost_usd for r in self.records),
                "by_provider": self._group_by_provider(self.records),
            }
            records = self.records
            title = "HISTORIQUE COMPLET"
        
        if format == "json":
            return json.dumps({
                "period": period,
                "stats": stats,
                "records": [r.to_dict() for r in records[-20:]],  # 20 derniers
            }, indent=2, ensure_ascii=False)
        
        # Format texte
        lines = []
        lines.append("")
        lines.append("╔══════════════════════════════════════════════════════════════╗")
        lines.append(f"║    🤖 RAPPORT D'INFÉRENCES LLM - {title:^24}   ║")
        lines.append("╚══════════════════════════════════════════════════════════════╝")
        lines.append("")
        
        # Stats globales
        lines.append("┌──────────────────────────────────────────────────────────────┐")
        lines.append("│  STATISTIQUES GLOBALES                                       │")
        lines.append("├──────────────────────────────────────────────────────────────┤")
        lines.append(f"│  • Inférences totales : {stats['inferences_count']:>8}                           │")
        lines.append(f"│  • Tokens totaux      : {stats['total_tokens']:>8}                           │")
        lines.append(f"│  • Coût total         : ${stats['total_cost_usd']:>7.4f}                          │")
        if stats.get('avg_latency_ms'):
            lines.append(f"│  • Latence moyenne    : {stats['avg_latency_ms']:>7.0f}ms                          │")
        lines.append("└──────────────────────────────────────────────────────────────┘")
        lines.append("")
        
        # Par provider
        if stats.get("by_provider"):
            lines.append("┌──────────────────────────────────────────────────────────────┐")
            lines.append("│  PAR PROVIDER                                                │")
            lines.append("├────────────┬─────────┬────────────┬──────────────────────────┤")
            lines.append("│ Provider   │ Appels  │ Tokens     │ Coût ($)                 │")
            lines.append("├────────────┼─────────┼────────────┼──────────────────────────┤")
            
            for provider, pstats in sorted(stats["by_provider"].items()):
                lines.append(f"│ {provider:<10} │ {pstats['count']:>7} │ {pstats['tokens']:>10} │ ${pstats['cost_usd']:>8.4f}              │")
            
            lines.append("└────────────┴─────────┴────────────┴──────────────────────────┘")
            lines.append("")
        
        # Dernières inférences
        if records:
            lines.append("┌──────────────────────────────────────────────────────────────┐")
            lines.append("│  10 DERNIÈRES INFÉRENCES                                     │")
            lines.append("├──────────────┬──────────┬────────────┬───────────┬───────────┤")
            lines.append("│ Heure        │ Provider │ Contexte   │ Tokens    │ Coût      │")
            lines.append("├──────────────┼──────────┼────────────┼───────────┼───────────┤")
            
            for r in sorted(records, key=lambda x: x.timestamp, reverse=True)[:10]:
                ts = r.timestamp[11:19] if len(r.timestamp) > 11 else r.timestamp
                provider = r.provider[:8]
                context = r.context[:10]
                tokens = r.tokens_in + r.tokens_out
                lines.append(f"│ {ts:<12} │ {provider:<8} │ {context:<10} │ {tokens:>9} │ ${r.cost_usd:>7.4f} │")
            
            lines.append("└──────────────┴──────────┴────────────┴───────────┴───────────┘")
            lines.append("")
        
        return "\n".join(lines)
    
    def save(self) -> None:
        """Force la sauvegarde des données."""
        self._save_data()


# Fonction helper pour usage simple
def record_inference(
    provider: str,
    model: str,
    tokens_in: int,
    tokens_out: int,
    cost_usd: Optional[float] = None,
    latency_ms: Optional[float] = None,
    context: str = "unknown",
    file_path: Optional[str] = None,
    mode: Optional[str] = None,
    success: bool = True,
    error: Optional[str] = None,
) -> InferenceRecord:
    """
    Enregistre une inférence de manière simple.
    
    Usage:
        record_inference(
            provider="groq",
            model="llama-3.1-70b",
            tokens_in=1500,
            tokens_out=800,
            context="code_generation",
            mode="PROD"
        )
    """
    tracker = InferenceTracker()
    return tracker.record(
        provider=provider,
        model=model,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        cost_usd=cost_usd,
        latency_ms=latency_ms,
        context=context,
        file_path=file_path,
        mode=mode,
        success=success,
        error=error,
    )


def get_inference_report(format: str = "text", period: str = "session") -> str:
    """Génère un rapport d'inférences."""
    tracker = InferenceTracker()
    return tracker.generate_report(format=format, period=period)


# Instance globale pour import facile
inference_tracker = InferenceTracker()


__all__ = [
    "InferenceTracker",
    "InferenceRecord",
    "Provider",
    "record_inference",
    "get_inference_report",
    "inference_tracker",
]